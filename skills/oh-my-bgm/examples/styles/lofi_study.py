"""Steam & Static — a lo-fi hip-hop beat for staying in: a warm, slightly seasick Rhodes on a
4-bar loop of 9th chords, a lazy swung boom-bap kit with the snare a hair late, finger bass, a nylon guitar
that hums a short tune, vibes that answer later, rain on the window and vinyl dust, everything gently
low-passed and ducking under the kick.
Feels: calm, cosy, unhurried, a little nostalgic. Scenes: studying or working, a rainy afternoon, background
for streams and vlogs, late-night reading, a café playlist.
F major, 82 BPM, 16ths swung 0.58, 42 bars (~2:03); with --loop a seamless loop (drops the ending).

| Bbmaj9 | Am7 D7b9 | Gm9 | C13 |   (x10, plus an intro and an ending)
Form: intro 2 (filtered Rhodes, rain) · A 8 beat + chords · B 8 + guitar tune · C 8 + vibes answers ·
break 4 (drums out) · A 8 everyone · ending 4 (filter closes, last chord).
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/lofi_study.py [--loop]   -> ./out/lofi_study/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv

import numpy as np  # noqa: E402
from pedalboard import Chorus, HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402
from scipy import signal  # noqa: E402

from orch import GU_SF, SR, Song, n, nearest  # noqa: E402
from score import P, finish, kit, play, seq, swing  # noqa: E402

BPM, B = 82, 4
V = {"Bbmaj9": (10, "A3 C4 D4 F4"), "Am7": (9, "G3 C4 E4"), "D7b9": (2, "F#3 C4 Eb4"), "Gm9": (7, "F3 Bb3 D4 A4"),
     "C13": (0, "E3 Bb3 D4 A4")}
LOOPC = [["Bbmaj9"], ["Am7", "D7b9"], ["Gm9"], ["C13"]]
FORM = [("intro", LOOPC[2:]), ("A", LOOPC * 2), ("B", LOOPC * 2), ("C", LOOPC * 2), ("break", LOOPC),
        ("A2", LOOPC * 2)] + ([] if LOOP else [("end", LOOPC[:2] + [["Bbmaj9"], ["Bbmaj9"]])])
BARS = [(sec, chs) for sec, bars in FORM for chs in bars]
START = {}
for i, (sec, _) in enumerate(BARS):
    START.setdefault(sec, i)
song = Song(bpm=BPM, beats=len(BARS) * B, tail=3.5, seed=82)

TUNE = ("r/.5 F4/.5 A4/.5 C5/.5 D5/1.5 C5/.5 | E5/1 C5/1 F#5/1 Eb5/1 | D5/1.5 A4/.5 Bb4/1 r/1 | r/1 E5/.5 G5/.5 A5/1.5 G5/.5 | "
        "r/.5 F5/.5 E5/.5 D5/.5 C5/2 | r/1 A4/.5 C5/.5 F#5/1 Eb5/1 | D5/3 r/1 | E5/1 G5/1 A5/2")
ANSWER = "A5/4 | G5/2 F#5/2 | F5/4 | E5/4 | A5/2 C6/2 | G5/2 F#5/2 | F5/3 D5/1 | E5/4"

rhodes = P("rhodes", 4, pan=-.1, width=1.4, level=-19, send=-12, bus="keys", jitter_ms=8,
           eq=[HighpassFilter(120), PeakFilter(450, -2, 1), LowpassFilter(5500),
               Chorus(rate_hz=.35, depth=.3, centre_delay_ms=8, feedback=0, mix=.5)])
guitar = P("nylon", 24, sf2=GU_SF, pan=.3, level=-16.5, send=-11, bus="lead", jitter_ms=8,
           eq=[HighpassFilter(200), LowpassFilter(6000)])
vibes = P("vibes", 11, 11, sf2=GU_SF, pan=-.35, level=-20, send=-9, bus="lead", jitter_ms=6,
          eq=[HighpassFilter(300), LowpassFilter(7000)])
bass = P("bass", 33, sf2=GU_SF, width=.2, level=-20, send=-30, bus="bass", jitter_ms=6, legato=-.05,
         eq=[HighpassFilter(38), LowpassFilter(2500)])
drums = kit("drums", 0, width=1.1, level=-20, send=-16, bus="drums", jitter_ms=6,
            eq=[HighpassFilter(40), LowpassFilter(8000), PeakFilter(4000, -3, 1)])
KICK, SNARE, RIM, HHC, HHO = 36, 38, 37, 42, 46
LATE = .035  # snare a hair behind the beat (beats)

flat = [(bar, sec, ci, len(chs), c) for bar, (sec, chs) in enumerate(BARS) for ci, c in enumerate(chs)]
for k, (bar, sec, ci, nch, c) in enumerate(flat):
    span = B / nch
    b0 = bar * B + ci * span
    r, voi = V[c]
    vo = [n(q) for q in voi.split()]
    lo = nearest(r, n("F2"))
    last = sec == "end" and bar >= START["end"] + 2
    if last:
        if bar == START["end"] + 2:
            for j, q in enumerate(vo + [n("C5"), n("E5")]):
                rhodes.add(b0 + j * .1, 2 * B - j * .1, q, 64)
            bass.add(b0, 2 * B, lo, 80)
            play(guitar, seq("r/1 F5/.5 D5/.5 C5/2 | A4/4", b0), 72)
        continue
    # Rhodes: a lazy push before the bar and a held chord
    for j, q in enumerate(vo):
        rhodes.add(b0 + j * .02, span - .1, q, 58 + (6 if ci == 0 else 0))
    if sec not in ("intro", "break"):
        nxt = nearest(V[flat[(k + 1) % len(flat)][4]][0], lo)
        line = [(0, 1.2, lo, 96), (1.75, .4, lo, 70), (2.5, .9, lo + 7, 84), (3.5, .4, nxt + 1, 72)] if nch == 1 \
            else [(0, 1.2, lo, 94), (1.5, .4, nxt - 1 if ci else lo + 12, 72)]
        for bb, d, q, v in line:
            bass.add(b0 + bb, d, q, v)
# drums: boom-bap, ghost snares, hats with random velocity
rng = np.random.default_rng(4)
for bar, (sec, _) in enumerate(BARS):
    b0 = bar * B
    if sec in ("intro", "break") or (sec == "end" and bar >= START["end"] + 2):
        continue
    for bb, v in ((0, 104), (1.75, 72), (2.5, 96)) if bar % 2 == 0 else ((0, 104), (2.25, 80), (2.75, 70)):
        drums.add(b0 + bb, .2, KICK, v)
    for bb in (1, 3):
        drums.add(b0 + bb + LATE, .2, SNARE, 92)
    drums.add(b0 + 3.75, .1, SNARE, 34)
    for i in range(8):
        drums.add(b0 + i * .5, .1, HHO if (i == 7 and bar % 4 == 3) else HHC, int(48 + rng.integers(0, 22)))

play(guitar, seq(TUNE, START["B"] * B), 88)
play(guitar, seq(TUNE, START["A2"] * B), 90)
play(vibes, seq(ANSWER, START["C"] * B), 84)
play(vibes, seq(ANSWER, START["A2"] * B, shift=-12), 66)
for p in (rhodes, guitar, vibes, bass, drums):
    swing(p, .58, unit=.25)

# rain on the window + vinyl dust
N = int(song.length * SR)
rr = np.random.default_rng(8)
rain = signal.sosfilt(signal.butter(2, [400, 6000], "band", fs=SR, output="sos"), rr.standard_normal((N, 2)), axis=0)
drops = np.zeros((N, 2))
for i in rr.integers(0, N, int(song.length * 25)):
    drops[i, rr.integers(0, 2)] = rr.uniform(.3, 1)
drops = signal.sosfilt(signal.butter(2, [1500, 7000], "band", fs=SR, output="sos"), drops, axis=0)
dust = np.zeros((N, 2))
idx = rr.integers(0, N, int(song.length * 8))
dust[idx, 0] = dust[idx, 1] = rr.uniform(-1, 1, len(idx))
amb = (rain * .25 + drops * 3 + dust).astype(np.float32)
extra = {"rain_vinyl": (amb, dict(level=-36, send=-20, width=1.3, bus="fx", eq=[HighpassFilter(300)]))}
DUCK = [(0, -2), (START["A"] * B - .01, -2), (START["A"] * B, 0)]
if not LOOP:
    DUCK += [(START["end"] * B, 0), (len(BARS) * B, -6)]

if __name__ == "__main__":
    S = START
    finish("lofi_study", [rhodes, guitar, vibes, bass, drums], song,
           [("A", S["A"], S["B"]), ("B", S["B"], S["C"]), ("C", S["C"], S["break"]), ("A2", S["A2"], S["A2"] + 8)],
           lead={"nylon", "vibes"}, beats_per_bar=B, loop=LOOP, extra=extra, duck=DUCK,
           hall=dict(rt_low=1.2, rt_mid=1.0, rt_high=.6, predelay=.015, length=2.4),
           bus_fx={"drums": [LowpassFilter(7500)]}, sidechain=(("drums",), ("keys", "bass"), 2.0),
           tone=[LowpassFilter(11000), PeakFilter(250, 1.0, .8)])
