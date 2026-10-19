"""orch — score-in-code instrumental music on SoundFonts.

score (beats) -> per-player MIDI -> FluidSynth with MuseScore General / GeneralUser GS (each part
picks its own SoundFont) -> stems (float32, 48 kHz) -> mix (placement, EQ, hall convolution, bus
comp) -> master (oversampled peak limiter, LUFS normalisation) -> WAV / MP3 / stems / spectrogram.

Everything is deterministic (seeded humanisation).
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import zlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import mido
import numpy as np
import pyloudnorm
import soundfile as sf
from pedalboard import (Compressor, HighpassFilter, HighShelfFilter, LowpassFilter,
                        LowShelfFilter, PeakFilter, Pedalboard)
from scipy import ndimage, signal

SR = 48000
LIBS = Path(os.environ.get("SOUND_LIBS", Path.home() / "sound-libs"))
GM_SF = LIBS / "MuseScore_General.sf3"
LOCAL_LIB = Path(os.environ.get("FLUIDSYNTH_LIB", Path.home() / ".local/lib64"))
GU_SF = LIBS / "GeneralUser-GS.sf2"


def _bin(name: str) -> str:
    """A tool on PATH, else in ~/.local/bin (where setup.sh installs it)."""
    import shutil
    return shutil.which(name) or str(Path.home() / ".local/bin" / name)

# ---------------------------------------------------------------- music helpers
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def n(name: str) -> int:
    """'D4' -> 62, 'Bb2' -> 46, 'C#5' -> 73."""
    pc = NOTE[name[0]]
    i = 1
    while i < len(name) and name[i] in "#b":
        pc += 1 if name[i] == "#" else -1
        i += 1
    return 12 * (int(name[i:]) + 1) + pc


CHORDS = {  # root pitch class, quality
    "Dm": (2, "m"), "Bb": (10, "M"), "F": (5, "M"), "C": (0, "M"),
    "Gm": (7, "m"), "A": (9, "M"), "Am": (9, "m"), "Eb": (3, "M"),
}


def chord_tones(ch: str) -> tuple[int, int, int]:
    root, q = CHORDS[ch]
    return root, (root + (3 if q == "m" else 4)) % 12, (root + 7) % 12


def nearest(pc: int, target: int) -> int:
    """MIDI note with pitch class pc closest to target."""
    base = target - ((target - pc) % 12)
    return base if target - base <= 6 else base + 12


# ---------------------------------------------------------------- score model
@dataclass
class Note:
    beat: float
    dur: float
    pitch: int
    vel: int
    bend: list | None = None    # pitch curve of this note: [(beats after its start, semitones)], see score.pitch


@dataclass
class Part:
    name: str
    program: int                # GM program 0-127 (for drums on channel 9: the kit number)
    sf2: str = str(GM_SF)       # SoundFont file: GM_SF (MuseScore General) or GU_SF (GeneralUser GS)
    bank: int = 0               # e.g. 8 / 17 for MuseScore General variations and "Expr." presets
    channel: int = 0            # 9 = GM drum channel
    players: int = 1            # unison players, each slightly detuned / late / panned
    pan: float = 0.0            # -1 .. 1
    width: float = 1.0          # stereo width of the stem
    gain: float = 0.0           # dB
    send: float = -12.0         # dB into the hall
    eq: list = field(default_factory=list)  # pedalboard plugins
    notes: list[Note] = field(default_factory=list)
    auto: list[tuple[float, float]] = field(default_factory=list)  # (beat, dB) gain automation
    bus: str = "orch"
    level: float | None = None  # target integrated LUFS of the raw stem (before automation)
    jitter_ms: float = 7.0
    legato: float = 0.0         # beats to shorten (<0) / overlap (>0) each note
    note_map: dict = field(default_factory=dict)  # remap pitches (percussion keys)
    transpose: int = 0
    cents: float = 0.0          # fine tuning of the whole part (pitch wheel, bend range 2 st): microtonal / just intonation
    roll: float | None = None   # emulate a roll: repeat long notes every `roll` beats
    cc: dict = field(default_factory=dict)  # initial controller values, e.g. {21: 64}
    curves: dict = field(default_factory=dict)  # cc -> [(beat, value)], e.g. {2: ...} for Expr presets
    expr_cc: int | None = None  # derive a dynamics curve on this CC from the notes (e.g. 2 for
                                # MuseScore General "Expr." presets): level = velocity, long notes swell
    offset_ms: float | None = None  # trigger this much early; None = measure the attack
    bend_range: int = 2         # pitch-wheel range in semitones (score.pitch raises it for wide slides)
    sends: dict = field(default_factory=dict)  # extra sends {name: dB} into mix(halls={name: ...})
    spread: float = 0.0         # pan notes by pitch across +-spread (low left, high right), like the strings of a
                                # zither, harp or piano in a stereo recording; each string group gets its own channel

    def add(self, beat, dur, pitch, vel, bend=None):
        """bend: this note's pitch curve [(beats after its start, semitones)], linear between points."""
        if isinstance(pitch, str):
            pitch = n(pitch)
        self.notes.append(Note(beat, dur, int(pitch), int(np.clip(vel, 1, 127)), bend))
        return self


@dataclass
class Song:
    bpm: float
    beats: float                # length of the music in beats
    tail: float = 4.0           # seconds of reverb tail after the last beat
    seed: int = 7
    tempo: list = field(default_factory=list)  # optional tempo map [(beat, bpm)]: linear ramps between the
                                               # points (rit., accel.), held outside them; empty = `bpm` throughout

    @property
    def spb(self):
        return 60.0 / self.bpm

    def bpm_at(self, beat):
        if not self.tempo:
            return self.bpm
        pts = sorted(self.tempo, key=lambda p: p[0])  # stable: (b, 60), (b, 90) is a jump at b
        return float(np.interp(beat, [b for b, _ in pts], [v for _, v in pts]))

    def t(self, beat):
        """Seconds at a beat (exact for the piecewise-linear tempo map)."""
        if not self.tempo:
            return beat * self.spb
        pts = sorted(self.tempo, key=lambda p: p[0])
        if beat <= pts[0][0]:
            return beat * 60.0 / pts[0][1]
        total = pts[0][0] * 60.0 / pts[0][1]
        for (b0, v0), (b1, v1) in zip(pts, pts[1:] + [(math.inf, pts[-1][1])]):
            if b1 <= b0:
                continue
            e = min(beat, b1)
            ve = v0 if b1 == math.inf else v0 + (v1 - v0) * (e - b0) / (b1 - b0)
            total += 60.0 * (e - b0) / v0 if abs(ve - v0) < 1e-9 else 60.0 * (e - b0) * math.log(ve / v0) / (ve - v0)
            if beat <= b1:
                break
        return total

    @property
    def length(self):
        return self.t(self.beats) + self.tail


# ---------------------------------------------------------------- rendering
TPB = 960
TPB_FLAT, TPB_TEMPO = TPB, 9600  # ticks per beat: constant tempo / with a tempo map


PRE = 0.3  # s of pre-roll in every MIDI file, so notes can be triggered early


def _events(part: Part, notes: list[Note]) -> list[Note]:
    """Apply the kit's pitch mapping and roll emulation."""
    out = []
    for nt in notes:
        p = part.note_map.get(nt.pitch, nt.pitch) + part.transpose
        if part.roll and nt.dur > part.roll * 2:
            k, b = 0, nt.beat
            while b < nt.beat + nt.dur - 1e-6:
                ramp = 0.75 + 0.25 * min(1, (b - nt.beat) / max(nt.dur, 1e-6))
                out.append(Note(b, part.roll, p, int(nt.vel * ramp) - (6 if k % 2 else 0)))
                b += part.roll
                k += 1
        else:
            out.append(Note(nt.beat, nt.dur, p, nt.vel, nt.bend))
    return out


def expr_curve(notes: list[Note]) -> list[tuple[float, float]]:
    """A phrase-level dynamics curve: each note sets the level from its velocity; notes longer
    than a beat swell by ~12 % into their middle and ease off before the end."""
    pts = []
    for nt in sorted(notes, key=lambda q: q.beat):
        v = float(np.clip(nt.vel, 20, 127))
        pts.append((nt.beat, v * 0.92))
        if nt.dur > 1.0:
            pts.append((nt.beat + nt.dur * 0.5, min(127, v * 1.05)))
            pts.append((nt.beat + nt.dur * 0.95, v * 0.85))
    pts.sort()
    merged = []
    for b, v in pts:  # chords: keep the loudest value per time
        if merged and abs(merged[-1][0] - b) < 1e-6:
            merged[-1] = (b, max(merged[-1][1], v))
        else:
            merged.append((b, v))
    return merged


BEND_STEP = 1 / 96  # beats between pitch-wheel updates along a note's curve


def _write_midi(part: Part, song: Song, player: int, path: Path, notes=None, offset_s=0.0):
    """One MIDI file per part and player. The score is shifted by PRE s of pre-roll at the opening tempo; a tempo
    map becomes tempo events. Notes with a pitch curve (Note.bend) are dealt round-robin over 8 channels, so each
    note bends on its own channel and never drags a neighbour or its own release. With Part.spread every group of
    neighbouring pitches ("string") gets its own channel and pan, so a repeated note still stops its own ring."""
    rng = np.random.default_rng(zlib.crc32(f"{song.seed}/{part.name}/{player}".encode()))
    # FluidSynth's player restarts its clock on the nearest tick at every tempo change; finer ticks keep a long
    # rit. from drifting (measured: 128 changes at 960 ticks drift ~9 ms)
    TPB = TPB_TEMPO if song.tempo else TPB_FLAT
    mid = mido.MidiFile(ticks_per_beat=TPB)
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(song.bpm_at(0)), time=0))

    def tps(beat):  # ticks per second at a beat
        return TPB / (60.0 / song.bpm_at(beat))
    tick_s = tps(0)
    pre_t = PRE * tick_s
    ev = []
    if song.tempo:  # piecewise-constant tempo per 1/8 beat (midpoint), shifted by the pre-roll
        last = song.bpm_at(0)
        for b in np.arange(0, song.beats + song.tail * song.bpm_at(song.beats) / 60 + 1, 1 / 8):
            v = song.bpm_at(b + 1 / 16)
            if abs(v - last) > 1e-3:
                ev.append((int(round(b * TPB + pre_t)), 0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(v))))
                last = v
    src = _events(part, part.notes if notes is None else notes)
    bends = part.channel != 9 and any(nt.bend for nt in src)
    pitches = sorted({nt.pitch for nt in src})
    spread = part.spread if part.channel != 9 and pitches else 0.0
    if bends:
        chans = [c for c in range(16) if c != 9][:8]
    elif spread:
        chans = [c for c in range(16) if c != 9][:len(pitches)]
    else:
        chans = [part.channel]

    def pan_cc(p):  # low strings left, high strings right
        lo, hi = pitches[0], pitches[-1]
        x = spread * np.clip((p - (lo + hi) / 2) / max(6.0, (hi - lo) / 2), -1, 1)
        return int(round(64 + 63 * x))
    detune = part.cents + (float(np.linspace(-9, 9, part.players)[player]) if part.players > 1 else 0.0)
    span = part.bend_range * 100.0  # players spread +-9 cents; default bend range 2 st = 200 c

    def wheel(semis=0.0):
        return int(np.clip((semis * 100 + detune) / span * 8191, -8192, 8191))
    for ch in chans:
        if part.bank:
            ev.append((0, 0, mido.Message("control_change", control=0, value=part.bank, channel=ch)))
        ev.append((0, 0, mido.Message("program_change", program=int(part.program), channel=ch)))
        ev.append((0, 0, mido.Message("control_change", control=91, value=0, channel=ch)))  # no reverb
        ev.append((0, 0, mido.Message("control_change", control=93, value=0, channel=ch)))
        for c, v in part.cc.items():
            ev.append((0, 0, mido.Message("control_change", control=int(c), value=int(v), channel=ch)))
        if part.bend_range != 2 and ch != 9:  # RPN 0: pitch-bend range in semitones
            for c, v in ((101, 0), (100, 0), (6, int(part.bend_range)), (38, 0), (101, 127), (100, 127)):
                ev.append((0, 0, mido.Message("control_change", control=c, value=v, channel=ch)))
        if (part.players > 1 or part.cents or bends) and ch != 9:
            ev.append((0, 0, mido.Message("pitchwheel", pitch=wheel(), channel=ch)))
    late = (player * 11.0) / 1000.0  # each extra player a little behind
    pre = PRE - offset_s
    curves = dict(part.curves)
    if part.expr_cc is not None and part.expr_cc not in curves:
        curves[part.expr_cc] = expr_curve(part.notes if notes is None else notes)
    for c, pts in curves.items():  # controller curves, linear between breakpoints, 1/16 beat
        if not pts:
            continue
        bs = np.array([b for b, _ in pts], float)
        vs = np.array([v for _, v in pts], float)
        last = None
        for b in np.arange(bs[0], bs[-1] + 1e-9, 0.0625):
            val = int(round(np.interp(b, bs, vs)))
            if val != last:
                tick = max(0, int(round(b * TPB + pre_t)))
                for ch in chans:
                    ev.append((tick, 0, mido.Message("control_change", control=int(c), value=val, channel=ch)))
                last = val
    order = sorted(range(len(src)), key=lambda i: src[i].beat)
    chan_of = {i: chans[r % len(chans)] for r, i in enumerate(order)}
    if spread and not bends:  # one channel per group of neighbouring pitches, panned by its mean pitch
        rank = {q: k for k, q in enumerate(pitches)}
        group = {q: chans[rank[q] * len(chans) // len(pitches)] for q in pitches}
        chan_of = {i: group[nt.pitch] for i, nt in enumerate(src)}
        for ch in sorted(set(group.values())):
            qs = [q for q, c in group.items() if c == ch]
            ev.append((0, 0, mido.Message("control_change", control=10, value=pan_cc(sum(qs) / len(qs)), channel=ch)))
    for i, note in enumerate(src):
        ch = chan_of[i]
        j = rng.normal(0, part.jitter_ms / 1000.0) + late + pre
        shift = j * tick_s if not song.tempo else pre_t + (j - PRE) * tps(note.beat)
        on = max(0, int(round(note.beat * TPB + shift)))
        off = max(on + 10, int(round((note.beat + note.dur + part.legato) * TPB + shift)))
        v = int(np.clip(note.vel + rng.normal(0, 4), 1, 127))
        if bends and spread:
            ev.append((on, 1.5, mido.Message("control_change", control=10, value=pan_cc(note.pitch), channel=ch)))
        if bends:  # this note's curve on its own channel, set just before its note-on
            pts = note.bend or [(0.0, 0.0)]
            ob = np.array([q[0] for q in pts], float)
            ov = np.array([q[1] for q in pts], float)
            last = wheel(float(np.interp(0.0, ob, ov)))
            ev.append((on, 1.5, mido.Message("pitchwheel", pitch=last, channel=ch)))
            stop = min(ob[-1], note.dur + max(part.legato, 0.0) + 1.0)
            for o in np.arange(BEND_STEP, stop + 1e-9, BEND_STEP):
                val = wheel(float(np.interp(o, ob, ov)))
                if val != last:
                    ev.append((max(on, int(round((note.beat + o) * TPB + shift))), 1.5,
                               mido.Message("pitchwheel", pitch=val, channel=ch)))
                    last = val
        ev.append((on, 2, mido.Message("note_on", note=note.pitch, velocity=v, channel=ch)))
        ev.append((off, 1, mido.Message("note_off", note=note.pitch, velocity=0, channel=ch)))
    ev.sort(key=lambda e: (e[0], e[1]))
    now = 0
    for tick, _, msg in ev:
        tr.append(msg.copy(time=tick - now))
        now = tick
    if song.tempo:
        end = int(song.beats * TPB + pre_t + song.tail * tps(song.beats))
    else:
        end = int(song.beats * TPB + (song.tail + PRE) / song.spb * TPB)
    tr.append(mido.MetaMessage("end_of_track", time=max(0, end - now)))
    mid.save(path)


def _run_engine(part: Part, midi: Path, wav: Path):
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = f"{LOCAL_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    cmd = [_bin("fluidsynth"), "-q", "-n", "-i", "-r", str(SR), "-O", "float", "-T", "wav",
           "-o", "synth.reverb.active=0", "-o", "synth.chorus.active=0",
           "-o", "synth.polyphony=512", "-F", str(wav), str(part.sf2), str(midi)]
    subprocess.run(cmd, env=env, check=True, capture_output=True)


def _fit(x: np.ndarray, length: int) -> np.ndarray:
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    if len(x) < length:
        x = np.pad(x, ((0, length - len(x)), (0, 0)))
    return x[:length].astype(np.float32)


def measure_onset(part: Part, workdir: Path, song: Song) -> float:
    """Seconds from note-on to the audible start of a typical note of this part
    (10 ms RMS first reaching -10 dB of its maximum in the first second)."""
    ps = sorted(nt.pitch for nt in part.notes)
    vs = sorted(nt.vel for nt in part.notes)
    probe = Part(**{**part.__dict__, "name": part.name + ".probe", "players": 1, "jitter_ms": 0,
                    "roll": None, "notes": [Note(0, 1.0, ps[len(ps) // 2], vs[len(vs) // 2])]})
    probe.note_map, probe.transpose = {}, 0  # pitches are already mapped
    probe.notes[0].pitch = part.note_map.get(probe.notes[0].pitch, probe.notes[0].pitch) + part.transpose
    tmp = Song(bpm=song.bpm, beats=2, tail=1.0, seed=song.seed)
    mid, wav = workdir / f"{probe.name}.mid", workdir / f"{probe.name}.wav"
    _write_midi(probe, tmp, 0, mid)
    _run_engine(probe, mid, wav)
    x, _ = sf.read(wav, dtype="float32", always_2d=True)
    x = x[int(PRE * SR): int((PRE + 1.0) * SR)].mean(1)
    if not len(x) or np.abs(x).max() < 1e-6:
        return 0.0
    r = np.sqrt(np.maximum(ndimage.uniform_filter1d(x ** 2, int(0.01 * SR)), 0))
    i = int(np.argmax(r >= r.max() * db(-10)))
    return max(0.0, i / SR - 0.005)


def render_parts(parts: list[Part], song: Song, workdir: Path) -> dict[str, np.ndarray]:
    """Render every part (all its players) to a raw stereo stem, in parallel.

    Each part is triggered early by its measured attack time (or offset_ms), so the audible
    start lands on the beat."""
    workdir.mkdir(parents=True, exist_ok=True)
    total = int(song.length * SR)
    live = [p for p in parts if p.notes]
    with ThreadPoolExecutor(max_workers=min(32, os.cpu_count() or 4)) as ex:
        onsets = dict(zip([p.name for p in live], ex.map(
            lambda p: p.offset_ms / 1000 if p.offset_ms is not None
            else min(0.15, measure_onset(p, workdir, song)), live)))
    jobs = []
    for p in live:
        for k in range(p.players):
            mid = workdir / f"{p.name}.{k}.mid"
            wav = workdir / f"{p.name}.{k}.wav"
            _write_midi(p, song, k, mid, offset_s=onsets[p.name])
            jobs.append((p, k, mid, wav))
    with ThreadPoolExecutor(max_workers=min(40, os.cpu_count() or 4)) as ex:
        list(ex.map(lambda j: _run_engine(j[0], j[2], j[3]), jobs))
    stems = {}
    for p in live:
        acc = np.zeros((total, 2), np.float32)
        for (q, k, _, wav) in [j for j in jobs if j[0] is p]:
            x, sr = sf.read(wav, dtype="float32", always_2d=True)
            assert sr == SR, (p.name, sr)
            x = _fit(x[int(PRE * SR):], total)
            if p.players > 1:  # spread players across a small arc around the part's pan
                off = np.linspace(-0.25, 0.25, p.players)[k]
                x = place(x, off, 1.0)
            acc += x / math.sqrt(p.players)
        stems[p.name] = acc
    render_parts.onsets = {k: round(v * 1000, 1) for k, v in onsets.items()}
    return stems


# ---------------------------------------------------------------- DSP
def db(x):
    return 10 ** (x / 20)


def place(x: np.ndarray, pan: float, width: float) -> np.ndarray:
    """Mid/side width, then constant-power pan (mono-safe, no Haas)."""
    m = (x[:, 0] + x[:, 1]) * 0.5
    s = (x[:, 0] - x[:, 1]) * 0.5 * width
    l, r = m + s, m - s
    a = (np.clip(pan, -1, 1) + 1) * math.pi / 4
    gl, gr = math.cos(a) * math.sqrt(2), math.sin(a) * math.sqrt(2)
    # pan as balance so a centred stem keeps unity gain
    return np.stack([l * min(1, gl), r * min(1, gr)], 1).astype(np.float32)


def envelope(points, song: Song, length: int) -> np.ndarray:
    """(beat, dB) breakpoints -> per-sample linear gain (held outside the range)."""
    if not points:
        return np.ones(length, np.float32)
    ts = np.array([song.t(b) * SR for b, _ in points])
    ds = np.array([d for _, d in points])
    g = np.interp(np.arange(length), ts, ds)
    return db(g).astype(np.float32)


def fx(x: np.ndarray, plugins) -> np.ndarray:
    if not plugins:
        return x
    return Pedalboard(plugins)(x.T.copy(), SR).T.astype(np.float32)


def hall_ir(rt_low=3.0, rt_mid=2.5, rt_high=1.4, predelay=0.022, length=4.5, seed=3):
    """Synthetic stereo hall: sparse early reflections + band-dependent exponential decay."""
    rng = np.random.default_rng(seed)
    N = int(length * SR)
    t = np.arange(N) / SR
    out = np.zeros((N, 2))
    bands = [(None, 300, rt_low), (300, 3000, rt_mid), (3000, None, rt_high)]
    for ch in range(2):
        noise = rng.standard_normal(N)
        late = np.zeros(N)
        for lo, hi, rt in bands:
            if lo is None:
                sos = signal.butter(4, hi, "low", fs=SR, output="sos")
            elif hi is None:
                sos = signal.butter(4, lo, "high", fs=SR, output="sos")
            else:
                sos = signal.butter(4, [lo, hi], "band", fs=SR, output="sos")
            late += signal.sosfilt(sos, noise) * np.exp(-6.9 * t / rt)
        late *= np.clip((t - 0.012) / 0.06, 0, 1)  # diffuse tail builds up after the ERs
        er = np.zeros(N)
        for _ in range(18):
            d = rng.uniform(0.004, 0.085)
            er[int(d * SR)] += rng.uniform(0.3, 1.0) * (1 - d / 0.1) * rng.choice([-1, 1])
        er = signal.sosfilt(signal.butter(2, 6000, "low", fs=SR, output="sos"), er)
        out[:, ch] = er * 0.6 + late * 0.35
    out = np.pad(out, ((int(predelay * SR), 0), (0, 0)))
    out /= np.sqrt((out ** 2).sum(0).mean())
    return out.astype(np.float32)


def convolve(x: np.ndarray, ir: np.ndarray) -> np.ndarray:
    y = np.stack([signal.oaconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return y.astype(np.float32)


def echo_ir(time=0.5, repeats=4, feedback=0.45, spread=0.7, lp=4500, darken=0.7, smear=0.012, seed=5):
    """A ping-pong echo as an impulse response for mix(halls=...): `repeats` taps every `time` s, each `feedback`
    quieter and darker (low-pass `lp`, x `darken` per repeat), alternating right/left by `spread` (0 centre,
    1 hard), each smeared over ~`smear` s so it sounds like a reflection off a far wall, not a copy."""
    rng = np.random.default_rng(seed)
    out = np.zeros((int((repeats * time + 0.25) * SR), 2))
    L = max(1, int(smear * SR))
    for k in range(1, repeats + 1):
        burst = rng.standard_normal(4 * L) * np.exp(-np.arange(4 * L) / L) * 0.12
        burst[0] += 1.0
        sos = signal.butter(2, max(400.0, lp * darken ** (k - 1)), "low", fs=SR, output="sos")
        burst = signal.sosfilt(sos, burst) * feedback ** (k - 1)
        side = spread if k % 2 else -spread
        i = int(k * time * SR)
        out[i:i + len(burst), 0] += burst * min(1.0, 1.0 - side)
        out[i:i + len(burst), 1] += burst * min(1.0, 1.0 + side)
    return out.astype(np.float32)


def true_peak_limit(x: np.ndarray, ceiling_db=-1.2, look_ms=5.0, hold_ms=40.0) -> np.ndarray:
    """Lookahead limiter driven by a 4x oversampled peak estimate."""
    up = signal.resample_poly(x, 4, 1, axis=0)
    pk = np.abs(up).max(1)
    pk = pk[: (len(pk) // 4) * 4].reshape(-1, 4).max(1)
    pk = np.pad(pk, (0, len(x) - len(pk)), mode="edge")
    c = db(ceiling_db)
    g_raw = np.minimum(1.0, c / np.maximum(pk, 1e-9))
    g = g_raw
    L = int(look_ms / 1000 * SR)
    H = int(hold_ms / 1000 * SR)
    # every sample within +-L of a peak gets that peak's gain; averaging over L keeps the
    # bound (each averaged value already satisfies it) and gives a smooth attack
    g = ndimage.minimum_filter1d(g, size=2 * L + 1)
    g = ndimage.minimum_filter1d(g, size=H + 1, origin=-(H // 2))  # hold after the peak
    # exponential release (one pole, ~150 ms), never rising above the required gain
    a = math.exp(-1.0 / (0.15 * SR))
    out = np.empty_like(g)
    cur = 1.0
    for i, v in enumerate(g):  # ~1 s for a minute of audio
        cur = v if v < cur else v + (cur - v) * a
        out[i] = cur
    out = ndimage.uniform_filter1d(out, size=L)
    out = np.minimum(out, g_raw)  # safety: the bound holds sample by sample
    return (x * out[:, None]).astype(np.float32)


def measure(path: Path) -> dict:
    """ffmpeg EBU R128: integrated LUFS, LRA, true peak (BS.1770, 4x)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                        "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    out = {}
    for key, label in (("lufs", "I:"), ("lra", "LRA:"), ("tp", "Peak:")):
        i = tail.find(label)
        out[key] = float(tail[i + len(label):].split()[0])
    return out


# ---------------------------------------------------------------- mix + master
def mix(parts: list[Part], stems: dict, song: Song, extra: dict | None = None,
        lufs=-14.0, ceiling=-1.2, hall: dict | None = None, duck=None,
        duck_exempt=("fx",), tone=None, bus_fx=None, sidechain=None, loop=False, halls: dict | None = None):
    """extra: name -> (stereo array, Part-like settings dict) for synthesised layers.
    duck: (beat, dB) automation on every bus (hall return included) except duck_exempt,
    e.g. a true silence before a drop. tone: master EQ plugins after the bus compressor.
    bus_fx: bus name -> plugins. sidechain: (trigger buses, ducked buses, depth dB).
    halls: extra reverbs or echoes beside the main hall, fed by Part.sends={name: dB}, each returned on its own
    bus "hall_<name>": {name: dict(hall_ir args..., hp=180, lp=9000, to_hall=None)} or
    {name: dict(echo=dict(echo_ir args...), hp=..., lp=..., to_hall=dB)}; hp/lp filter the send, to_hall also
    feeds the return into the main hall (an echo that reverberates). Use them for depth: a far, darker space for
    distant voices, a long echo for a solo flute.
    loop: optional seamless loop (games, long playback): the result is exactly song.beats long, the reverb tail after
    the last beat is folded onto the start, no fades, and the master chain runs pre-rolled with the
    loop's own end so compressor and limiter are already settled at sample 0."""
    length = int(song.length * SR)
    ir = hall_ir(**(hall or {}))
    buses: dict[str, np.ndarray] = {}
    hall_send = np.zeros((length, 2), np.float32)
    sends = {k: np.zeros((length, 2), np.float32) for k in (halls or {})}
    placed = {}
    items = [(p, stems[p.name]) for p in parts if p.name in stems]
    for name, (x, cfg) in (extra or {}).items():
        items.append((Part(name=name, program=0, **cfg), _fit(x, length)))
    meter = pyloudnorm.Meter(SR)
    levels = {}
    for p, x in items:
        y = fx(x, p.eq)
        if p.level is not None:
            cur = meter.integrated_loudness(y)
            levels[p.name] = round(cur, 1)
            if np.isfinite(cur):
                y = y * db(p.level - cur)
        y = place(y, p.pan, p.width) * db(p.gain)
        y *= envelope(p.auto, song, length)[:, None]
        placed[p.name] = y
        hall_send += y * db(p.send)
        for k, d in p.sends.items():
            sends[k] += y * db(d)
        buses.setdefault(p.bus, np.zeros((length, 2), np.float32))
        buses[p.bus] += y
    for k, cfg in (halls or {}).items():
        cfg = dict(cfg)
        hp, lp, to_hall, echo = cfg.pop("hp", 180), cfg.pop("lp", 9000), cfg.pop("to_hall", None), cfg.pop("echo", None)
        w = convolve(fx(sends[k], [HighpassFilter(hp), LowpassFilter(lp)]), echo_ir(**echo) if echo else hall_ir(**cfg))
        if to_hall is not None:
            hall_send += w * db(to_hall)
        buses[f"hall_{k}"] = w
    wet = convolve(fx(hall_send, [HighpassFilter(180), LowpassFilter(9000)]), ir)
    buses["hall"] = wet
    for k, plugins in (bus_fx or {}).items():
        if k in buses:
            buses[k] = fx(buses[k], plugins)
    if sidechain:  # (trigger buses, ducked buses, depth dB): orchestra breathes with the hits
        trig_names, targets, depth = sidechain
        trig = sum(buses[k] for k in trig_names if k in buses)
        e = np.abs(signal.sosfilt(signal.butter(2, 150, "low", fs=SR, output="sos"),
                                  trig.mean(1)))
        e = ndimage.maximum_filter1d(e, size=int(0.01 * SR))
        a = math.exp(-1 / (0.12 * SR))
        e = signal.lfilter([1 - a], [1, -a], e)
        e = np.clip(e / (np.percentile(e, 99.5) + 1e-9), 0, 1)
        g = db(-depth * e)[:, None].astype(np.float32)
        for k in targets:
            if k in buses:
                buses[k] = buses[k] * g
    if duck:
        d = envelope(duck, song, length)[:, None]
        for k in buses:
            if k not in duck_exempt:
                buses[k] = buses[k] * d
    pre = 0
    if loop:
        lm = int(round(song.t(song.beats) * SR))
        for k, b in buses.items():
            w = b[:lm].copy()
            t = b[lm:lm + lm]
            w[: len(t)] += t
            buses[k] = w
    dry = sum(buses.values())
    if loop:
        pre = min(int(4 * SR), len(dry))
        dry = np.concatenate([dry[-pre:], dry])
    bus = fx(dry, [HighpassFilter(28), Compressor(threshold_db=-16, ratio=2.0, attack_ms=30,
                                                 release_ms=250)] + list(tone or []))
    # loudness normalise, then limit; repeat so the post-limit loudness is on target
    master = bus
    for _ in range(3):
        g = lufs - meter.integrated_loudness(master)
        master = true_peak_limit(master * db(g), ceiling)
    if loop:
        master = master[pre:]
        g = lufs - meter.integrated_loudness(master)  # pre-roll was part of the measurement
        master = true_peak_limit(master * db(g), ceiling)
        return master, placed, buses, levels
    fade = int(1.5 * SR)
    master[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
    master[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))[:, None]
    return master, placed, buses, levels


def export(master: np.ndarray, buses: dict, outdir: Path, name: str, meta: dict | None = None):
    outdir.mkdir(parents=True, exist_ok=True)
    wav = outdir / f"{name}.wav"
    sf.write(wav, master, SR, subtype="PCM_24")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-b:a", "320k",
                    str(outdir / f"{name}.mp3")], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-lavfi",
                    "showspectrumpic=s=1600x600:legend=1:scale=log:fscale=log",
                    str(outdir / f"{name}.spectrogram.png")], check=True)
    stem_dir = outdir / "stems"  # pre-master buses: they sum to the mix before the master chain
    stem_dir.mkdir(exist_ok=True)
    for bname, x in buses.items():
        sf.write(stem_dir / f"{name}.{bname}.wav", x, SR, subtype="FLOAT")
    m = measure(wav)
    corr = float(np.corrcoef(master[:, 0], master[:, 1])[0, 1])
    report = {"file": str(wav), "seconds": round(len(master) / SR, 3), **m,
              "stereo_corr": round(corr, 3), **(meta or {})}
    (outdir / f"{name}.report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report
