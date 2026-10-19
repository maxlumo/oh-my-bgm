"""Open Field — sparse piano fragments with a lot of air between them, a faint string bed, a flute
answer, harp glints and wind. Suits: open-world exploration, landscape and nature footage, reflective essays.
D major with Lydian G#, 72 BPM, 30 bars (~1:45), no drums; with --loop a seamless loop.

Left hand (open fifths): D · G · D E · Bm G · G A · D G · D G · D
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/sparse_piano_field.py [--loop]   -> ./out/sparse_piano_field/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv  # optional seamless game loop; default: a whole piece with an ending

import numpy as np
from pedalboard import HighpassFilter, LowpassFilter, PeakFilter
from scipy import signal

from orch import GM_SF, GU_SF, SR, Song, n, nearest  # noqa: E402,F401
from score import P, finish, kit, play, seq, swing  # noqa: E402,F401

BPM, B = 72, 4
song = Song(bpm=BPM, beats=30 * B, tail=5.0, seed=72)

LH = [(0, "D2+A2", 4), (4, "G2+D3", 4), (8, "D2+A2", 2), (10, "E2+B2", 2), (12, "B1+F#2", 2), (14, "G2+D3", 2),
      (16, "G2+D3", 2), (18, "A2+E3", 2), (20, "D2+A2", 2), (22, "G2+D3", 2), (24, "D2+A2", 2), (26, "G2+D3", 2),
      (28, "D2+A2", 2)]
PAD = {"D2+A2": "D3 A3 E4", "G2+D3": "G3 D4 F#4", "E2+B2": "E3 B3 F#4", "B1+F#2": "B2 F#3 D4", "A2+E3": "A3 E4 F#4"}
RH = [(1, "A4/.5 D5/.5 E5/1 F#5/2 | r/2 E5/.5 A5/1.5"),
      (5, "B4/.5 D5/.5 F#5/1 A5/1 F#5/1 | E5/3"),
      (8, "D6/.5 A5/.5 F#5/.5 E5/.5 F#5/1 G#5/1 | A5/2"),
      (10, "r/1 B4/.5 E5/.5 F#5/2 | E5/1 B4/3"),
      (12, "B4/1 D5/.5 F#5/.5 A5/2 | G5/1 F#5/1 D5/2"),
      (20, "A5/.5 E6/.5 D6/1 A5/2 | F#5/.5 E5/.5 D5/3"),
      (22, "r/1 B5/1 A5/1 F#5/1 | E5/4"),
      (24, "A4/.5 D5/.5 E5/1 F#5/2 | r/2 G#5/.5 A5/1.5"),
      (26, "r/2 D6/.5 B5/.5 | A5/4"),
      (28, "F#5/.5 E5/.5 D5/3")]
FLUTE = "F#5/2 E5/1 D5/1 | A5/3 G5/.5 F#5/.5 | E5/4 | r/4"

piano = P("piano", 0, 8, pan=0, width=1.2, level=-18, send=-8, bus="piano", jitter_ms=8,
          eq=[HighpassFilter(60), PeakFilter(250, -1.5, 1), PeakFilter(3500, 1, 1)])
pad = P("strings", 49, 17, expr_cc=2, players=2, pan=0, width=1.6, level=-29, send=-6, bus="pad", legato=.5,
        eq=[HighpassFilter(150), LowpassFilter(5000), PeakFilter(2500, -3, 1)])
flute = P("flute", 73, 17, expr_cc=2, pan=.2, level=-21, send=-4, bus="lead", jitter_ms=6,
          eq=[HighpassFilter(300), LowpassFilter(9000)])
harp = P("harp", 46, pan=-.3, width=1.3, level=-26, send=-4, bus="lead", jitter_ms=5, eq=[HighpassFilter(200)])

for bar, notes, dur in LH:
    for k, q in enumerate(notes.split("+")):
        piano.add(bar * B + k * .08, dur * B, q, 50 - k * 4)
    for q in PAD[notes].split():
        pad.add(bar * B, dur * B, q, 54 if 14 <= bar < 22 else 44)
for bar, s in RH:
    play(piano, seq(s, bar * B), 62, extend=.8, accent=lambda b: 6 if b % 1 == 0 else -2)
for bar in (16, 18):  # soft chords under the flute
    for q in ("D4", "F#4", "A4") if bar == 16 else ("C#4", "E4", "A4"):
        piano.add(bar * B + 1, 6, q, 44)
play(flute, seq(FLUTE, 16 * B), 82)
GLINT = {10: ("E4", "B4", "E5", "F#5", "B5", "E6"), 18: ("A3", "E4", "A4", "C#5", "E5", "A5"),
         26: ("G3", "D4", "A4", "B4", "D5", "F#5")}  # follow the left hand's chord
for bar, notes in GLINT.items():  # harp glints: a slow rising arpeggio
    for k, q in enumerate(notes):
        harp.add(bar * B + 2 + k / 3, 3, q, 56 + k * 3)

# wind: two bands of decorrelated noise with slow random swells
N = int(song.length * SR)


def gust(lo, hi, rate, seed):
    r = np.random.default_rng(seed)
    x = signal.sosfilt(signal.butter(2, [lo, hi], "band", fs=SR, output="sos"), r.standard_normal((N, 2)), axis=0)
    k = int(SR / rate)
    pts = r.uniform(.1, 1, N // k + 2)
    env = np.interp(np.arange(N), np.arange(len(pts)) * k, pts)
    env = signal.sosfiltfilt(signal.butter(1, rate, fs=SR, output="sos"), env)
    return x * np.clip(env, 0, None)[:, None] ** 2


wind = (gust(150, 700, .12, 1) + .5 * gust(900, 3500, .2, 2)).astype(np.float32)
extra = {"wind": (wind, dict(level=-37, send=-20, width=1.4, bus="fx", eq=[HighpassFilter(120)]))}

if __name__ == "__main__":
    finish("sparse_piano_field", [piano, pad, flute, harp], song,
           [("0-8", 0, 8), ("8-16", 8, 16), ("16-20", 16, 20), ("20-30", 20, 30)],
           lead={"piano", "flute"}, beats_per_bar=B, loop=LOOP, extra=extra,
           hall=dict(rt_low=3.2, rt_mid=2.8, rt_high=1.6, predelay=.03, length=5.0))
