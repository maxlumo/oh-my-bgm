"""Score-writing helpers on top of orch: a compact melody notation, swing, and the melody-balance check.

    from score import P, kit, seq, play, swing, pitch, balance
"""
from __future__ import annotations

import zlib

import numpy as np

from orch import GM_SF, GU_SF, SR, Part, n


def P(name, program, bank=0, sf2=GM_SF, **kw) -> Part:
    """Part with the SoundFont given as a path (GM_SF or GU_SF)."""
    return Part(name, program, sf2=str(sf2), bank=bank, **kw)


def kit(name, number, sf2=GU_SF, **kw) -> Part:
    """Drum part on channel 10; `number` is the kit (0 Standard, 32 Jazz, 40 Brush, 48 Orchestra)."""
    return Part(name, number, sf2=str(sf2), channel=9, **kw)


def seq(s: str, start=0.0, shift=0) -> list[tuple[float, float, int]]:
    """'A4/.5 r/1 C5+E5/1.5 | ...' -> [(beat, dur, midi)]. Each token is pitch/duration in beats;
    'r' is a rest, '+' stacks a chord, '|' is a bar mark (ignored, but keep bars summing right)."""
    out, b = [], float(start)
    for tok in s.replace("|", " ").split():
        p, d = tok.split("/")
        d = float(d)
        if p != "r":
            for q in p.split("+"):
                out.append((b, d, n(q) + shift))
        b += d
    return out


def play(part: Part, notes, vel=90, extend=0.0, accent=None) -> Part:
    """Add (beat, dur, pitch) notes. `extend` lengthens each note (pedal / let ring),
    `accent(beat) -> velocity offset`."""
    for b, d, p in notes:
        part.add(b, d + extend, p, vel + (accent(b) if accent else 0))
    return part


def swing(part: Part, ratio=0.62, unit=0.5) -> Part:
    """Swing a part in place: the off-beat of each pair of `unit` notes (0.5 = 8ths, 0.25 = 16ths)
    moves from half-way to `ratio` of the pair (0.67 = triplet swing, 0.6-0.64 = a lighter lounge
    swing, 16ths at 0.54-0.58 = a funk/neo-soul push). Call after all notes are added."""
    g = 2 * unit

    def warp(x):
        w = np.floor(x / g + 1e-9) * g
        f = (x - w) / g
        return w + g * (f / .5 * ratio if f <= .5 else ratio + (f - .5) / .5 * (1 - ratio))
    for nt in part.notes:
        s, e = warp(nt.beat), warp(nt.beat + nt.dur)
        nt.beat, nt.dur = s, max(.05, e - s)
    return part


def pitch(part: Part, song, vib=None, slide=None, scoop=None, fall=None, max_slide=5, when=None, seed=0) -> Part:
    """A player's pitch for a melodic line, as per-note pitch-wheel curves (orch plays every bent note on its own
    MIDI channel, so a curve never drags a neighbour). Times in seconds at the local tempo. Call after all notes
    of the part are added; adds to curves already given with part.add(..., bend=[(beats, semitones)]).
      vib=(cents, hz, delay_s): vibrato on notes longer than delay + 0.25 s, fading in over 0.35 s, depth and rate
          drifting a little per note. Many string samples already carry vibrato (MuseScore General violins about
          +-17 c): add little or none there; winds and plucked strings take it well.
      slide=seconds: a note that follows the previous one without a gap, at most max_slide semitones away, starts
          at the previous pitch and glides into its own (portamento: erhu, violin, voice).
      scoop=(semitones, seconds): a note after a rest starts below its pitch and rises into it.
      fall=(semitones, seconds): a note before a rest drops away at its end.
      when(prev, note) -> bool chooses which connected pairs slide (default: all)."""
    rng = np.random.default_rng(seed + zlib.crc32(part.name.encode()))
    notes = sorted(part.notes, key=lambda q: q.beat)
    need = part.bend_range
    for i, nt in enumerate(notes):
        spb = 60.0 / song.bpm_at(nt.beat)
        dur_s = nt.dur * spb
        prev = notes[i - 1] if i else None
        nxt = notes[i + 1] if i + 1 < len(notes) else None
        joined = prev is not None and prev.beat < nt.beat and nt.beat - (prev.beat + prev.dur) <= 0.05
        rest_after = nxt is None or nxt.beat - (nt.beat + nt.dur) > 0.2
        offs = np.arange(0, nt.dur + 0.5 + 1e-9, 1 / 96)
        ts = offs * spb
        y = np.zeros_like(offs)
        if nt.bend:
            y += np.interp(offs, [q[0] for q in nt.bend], [q[1] for q in nt.bend])
        ease = lambda x: 0.5 * (1 + np.cos(np.pi * np.clip(x, 0, 1)))  # noqa: E731  1 -> 0, smooth at both ends
        if slide and joined and 0 < abs(prev.pitch - nt.pitch) <= max_slide and (when is None or when(prev, nt)):
            y += (prev.pitch - nt.pitch) * ease(ts / slide)
        elif scoop and not joined and dur_s > 2 * scoop[1]:
            y -= scoop[0] * ease(ts / scoop[1])
        if fall and rest_after and dur_s > 2 * fall[1]:
            y -= fall[0] * (1 - ease((ts - (dur_s - fall[1])) / fall[1]))
        if vib and dur_s > vib[2] + 0.25:
            c, hz, dl = vib
            depth, rate = c / 100 * rng.uniform(0.85, 1.15), hz * rng.uniform(0.94, 1.06)
            y += depth * np.clip((ts - dl) / 0.35, 0, 1) * np.sin(2 * np.pi * rate * np.maximum(ts - dl, 0))
        if np.abs(y).max() > 1e-4:
            nt.bend = list(zip(offs.tolist(), y.tolist()))
            need = max(need, int(np.ceil(np.abs(y).max() + 0.05)))
    part.bend_range = min(24, need)
    return part


def balance(placed: dict, song, sections, lead, beats_per_bar=4) -> dict:
    """Melody vs everything else, per section, from mix()'s `placed` (dry, before the hall).
    sections: [(label, first_bar, end_bar)], lead: names of the melody parts.
    Background music: melody about 0-3 LU above the rest; an accompaniment under a voice: below."""
    import pyloudnorm
    meter = pyloudnorm.Meter(SR)
    out = {}
    for label, a, b in sections:
        s0, s1 = int(song.t(a * beats_per_bar) * SR), int(song.t(b * beats_per_bar) * SR)
        mel = [v[s0:s1] for k, v in placed.items() if k in lead]
        rest = [v[s0:s1] for k, v in placed.items() if k not in lead]
        ml = meter.integrated_loudness(sum(mel)) if mel else float("-inf")
        rl = meter.integrated_loudness(sum(rest)) if rest else float("-inf")
        out[label] = (round(ml, 1), round(rl, 1))
        print(f"  {label:10s} melody {ml:6.1f} LUFS, rest {rl:6.1f}, diff {ml - rl:+5.1f}")
    return out


def finish(name, parts, song, sections, lead, beats_per_bar=4, outdir=None, lufs=-16.0, loop=False, **mix_kw):
    """Render, mix, export to <outdir or ./out>/<name>/<name>.wav, print the melody balance, run qc.py.
    loop=True makes an optional seamless loop (see orch.mix). Returns the export report."""
    import subprocess
    import sys
    from pathlib import Path

    from orch import export, mix, render_parts
    out = Path(outdir or Path.cwd() / "out") / name
    stems = render_parts(parts, song, out / "_render")
    master, placed, buses, levels = mix(parts, stems, song, lufs=lufs, loop=loop, **mix_kw)
    rep = export(master, buses, out, name, meta={"loop": loop, "stem_lufs_raw": levels})
    print({k: rep[k] for k in ("file", "seconds", "lufs", "tp", "lra", "stereo_corr")})
    balance(placed, song, sections, lead, beats_per_bar)
    qc = [sys.executable, str(Path(__file__).with_name("qc.py")), rep["file"], "--lufs", str(lufs)]
    r = subprocess.run(qc + (["--loop"] if loop else []), capture_output=True, text=True)
    print("qc:", "pass" if r.returncode == 0 else r.stdout[-600:])
    return rep
