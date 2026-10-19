"""Toward the Light — an inspiring build for brand films and launches: a piano 8th-note pulse, then
spiccato strings, then toms and big drums, horns and choir; a held breath before the last chorus, one hit at the end.
Suits: promotional / brand films, product launches, company milestones, sports highlights, openers.
D major, 118 BPM, 42 bars (~1:28); the arc is the point, so there is no loop version.

Progression (8 bars): | D(add9) | A/C# | Bm7 | G(add9) | Em7 | G | D/F# | Asus4 A |   (bass D C# B G E G F# A)
Form: intro 4 (piano) · A 8 piano + low strings, a soft kick · B 8 + spiccato strings, horn tune, toms ·
C 8 full: drums, brass, choir, violins an octave up · breath 2 (piano alone) · D 8 everything, highest ·
hit 4 (D chord, boom, ring out).
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/uplifting_launch.py   -> ./out/uplifting_launch/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]

from pedalboard import HighpassFilter, HighShelfFilter, LowpassFilter, PeakFilter  # noqa: E402

import hybrid as hy  # noqa: E402
from orch import GM_SF, GU_SF, Song, n, nearest  # noqa: E402
from score import P, finish, kit, play, seq  # noqa: E402

BPM, B = 118, 4
song = Song(bpm=BPM, beats=42 * B, tail=4.0, seed=118)
CH = {"D": (2, [2, 6, 9, 4]), "A/C#": (1, [9, 1, 4]), "Bm7": (11, [11, 2, 6, 9]), "G": (7, [7, 11, 2, 9]),
      "Em7": (4, [4, 7, 11, 2]), "D/F#": (6, [2, 6, 9]), "Asus4": (9, [9, 2, 4]), "A": (9, [9, 1, 4])}
PROG = [["D"], ["A/C#"], ["Bm7"], ["G"], ["Em7"], ["G"], ["D/F#"], ["Asus4", "A"]]
FORM = ([("intro", PROG[:4]), ("A", PROG), ("B", PROG), ("C", PROG), ("breath", [["G"], ["Asus4", "A"]]),
         ("D", PROG), ("hit", [["D"], ["D"], ["D"], ["D"]])])
BARS = [(sec, chs) for sec, bars in FORM for chs in bars]
START = {}
for i, (sec, _) in enumerate(BARS):
    START.setdefault(sec, i)

TUNE = "F#5/2 E5/1 D5/1 | E5/3 A4/1 | D5/2 C#5/1 B4/1 | D5/4 | B4/1 D5/1 G5/2 | F#5/2 E5/1 D5/1 | A5/3 F#5/1 | E5/2 C#5/2"

piano = P("piano", 0, pan=-.1, width=1.3, level=-19, send=-8, bus="keys", jitter_ms=3,
          eq=[HighpassFilter(80), PeakFilter(300, -2, 1), PeakFilter(3500, 1.5, 1)])
spicc = P("spiccato", 48, players=3, pan=.25, width=1.5, level=-23, send=-7, bus="strings", jitter_ms=4, legato=-.08,
          eq=[HighpassFilter(150), PeakFilter(2800, -2, 1)])
lows = P("low_strings", 49, 41, expr_cc=2, players=2, pan=.3, width=1.3, level=-22, send=-6, bus="strings", legato=.1,
         eq=[HighpassFilter(45), PeakFilter(300, -2, 1)])
violins = P("violins", 49, 21, expr_cc=2, players=2, pan=-.4, width=1.4, level=-17, send=-5, bus="strings", legato=.08,
            eq=[HighpassFilter(250), PeakFilter(3000, -2, 1)])
horns = P("horns", 60, 17, expr_cc=2, players=2, pan=-.25, width=1.2, level=-15.5, send=-5, bus="brass", legato=.06,
          eq=[HighpassFilter(90), LowpassFilter(6000)])
brass = P("brass_chords", 57, 17, expr_cc=2, players=2, pan=.3, width=1.3, level=-25, send=-5, bus="brass", legato=.1,
          eq=[HighpassFilter(90), PeakFilter(1200, -1.5, 1), LowpassFilter(6000)])
choir = P("choir", 52, 17, expr_cc=2, players=2, pan=0, width=1.6, level=-25, send=-3, bus="choir", legato=.3,
          eq=[HighpassFilter(200), PeakFilter(2500, -2, 1)])
drums = kit("drums", 48, sf2=GM_SF, width=1.3, level=-21, send=-8, bus="drums", jitter_ms=3,
            eq=[HighpassFilter(45), HighpassFilter(45)])
pulse = kit("pulse", 0, sf2=GU_SF, width=1.0, level=-26, send=-14, bus="drums", jitter_ms=2,
            eq=[HighpassFilter(45), HighpassFilter(45), LowpassFilter(4000)])
KICK, SNARE, CRASH, TOMS = 36, 38, 49, (41, 43, 45, 47)
ORDER = ["intro", "A", "B", "C", "breath", "D", "hit"]

flat = [(bar, sec, ci, len(chs), c) for bar, (sec, chs) in enumerate(BARS) for ci, c in enumerate(chs)]
for bar, sec, ci, nch, c in flat:
    span = B / nch
    b0 = bar * B + ci * span
    bpc, pcs = CH[c]
    lo = nearest(bpc, n("D2"))
    up = sorted(nearest(p, n("A4")) for p in pcs)
    lvl = ORDER.index(sec)
    if sec == "hit":
        if bar == START["hit"]:
            for k, q in enumerate([lo - 12, lo, lo + 7] + up + [q + 12 for q in up]):
                piano.add(b0 + k * .03, 4 * B, q, 92 - k)
            play(lows, [(b0, 3 * B, lo), (b0, 3 * B, lo + 12)], 110)
            play(brass, [(b0, 3 * B, q - 12) for q in up], 110)
            play(horns, [(b0, 3 * B, q) for q in up], 106)
            play(choir, [(b0, 3 * B, q) for q in up], 100)
            play(violins, [(b0, 3 * B, q + 12) for q in up], 104)
            drums.add(b0, 4, CRASH, 112)
            drums.add(b0, .5, TOMS[0], 120)
        continue
    # piano 8ths: root-fifth-octave-ninth shape, louder as the piece grows
    t = sorted(nearest(p, n("E4")) for p in pcs)  # chord tones, not fifths above a slash bass
    pat = [lo + 12, t[0], t[1], t[-1], t[1], t[0], t[2], t[0]]
    for k in range(int(span * 2)):
        piano.add(b0 + k * .5, min(.9, span - k * .5), pat[k], 58 + lvl * 4 + (8 if k % 4 == 0 else 0))
    if sec == "breath":
        continue
    if sec != "intro":
        lows.add(b0, span, lo, 70 + lvl * 6)
        lows.add(b0, span, lo + 12, 64 + lvl * 6)
    if sec in ("B", "C", "D"):  # spiccato 16ths on root and fifth, accents on the dotted pattern 3+3+2
        for k in range(int(span * 4)):
            q = up[0] if k % 2 == 0 else up[min(2, len(up) - 1)]
            spicc.add(b0 + k * .25, .2, q - 12, 66 + (20 if k % 8 in (0, 3, 6) else 0) + lvl * 3)
    if sec in ("C", "D"):
        for q in up:
            brass.add(b0, span, q - 12, 70 + lvl * 4)
            choir.add(b0, span, q, 64 + lvl * 4)
# drums per bar
for bar, (sec, _) in enumerate(BARS):
    b0 = bar * B
    if sec == "A":
        pulse.add(b0, .2, KICK, 76)
        pulse.add(b0 + 2, .2, KICK, 66)
    elif sec == "B":
        for k, v in [(0, 96), (1.5, 74), (2, 84), (3.5, 70)]:
            drums.add(b0 + k, .3, TOMS[1], v)
        pulse.add(b0, .2, KICK, 84)
        pulse.add(b0 + 2, .2, KICK, 76)
    elif sec in ("C", "D"):
        for k in (0, 1, 2, 3):
            pulse.add(b0 + k, .2, KICK, 96)
        drums.add(b0 + 2, .3, SNARE, 104)
        for k, v in [(0, 108), (.75, 80), (1.5, 96), (2.5, 84), (3, 100), (3.5, 88)]:
            drums.add(b0 + k, .3, TOMS[0] if k in (0, 1.5, 3) else TOMS[2], v)
        if (bar - START[sec]) % 4 == 0:
            drums.add(b0, 3, CRASH, 100)
    if sec in ("B", "C") and bar == START[sec] + 7:  # fill into the next section
        for j in range(8):
            drums.add(b0 + 2 + j * .25, .2, TOMS[3 - j // 2], 80 + j * 5)

play(horns, seq(TUNE, START["B"] * B), 96)
play(horns, seq(TUNE, START["C"] * B), 98)
play(violins, seq(TUNE, START["C"] * B, shift=12), 90)
play(violins, seq(TUNE, START["D"] * B, shift=12), 100)
play(horns, seq(TUNE, START["D"] * B), 104)
play(piano, seq(TUNE, START["A"] * B, shift=12), 64)   # the tune first appears quietly, high on the piano

fx = hy.Layer(song.length)
for sec in ("C", "D"):
    fx.at(song.t(START[sec] * B), hy.riser(3.0, seed=START[sec]), end=True, gain=.6)
    fx.at(song.t(START[sec] * B), hy.boom(.8, seed=START[sec]), gain=.7)
fx.at(song.t(START["hit"] * B), hy.boom(1.0, seed=99), gain=.9)
fx.at(song.t(START["hit"] * B), hy.ensemble_hit(1.0, seed=99), gain=.6)
extra = {"fx": (fx.buf, dict(level=-24, send=-8, width=1.3, bus="fx", eq=[HighpassFilter(35)]))}
DUCK = [(0, 0), (START["breath"] * B - .01, 0), (START["breath"] * B, -3), (START["D"] * B - .01, -3),
        (START["D"] * B, 0)]

if __name__ == "__main__":
    finish("uplifting_launch", [piano, spicc, lows, violins, horns, brass, choir, drums, pulse], song,
           [("intro", 0, 4), ("A", 4, 12), ("B", 12, 20), ("C", 20, 28), ("breath", 28, 30), ("D", 30, 38)],
           lead={"horns", "violins"}, beats_per_bar=B, lufs=-14.0, extra=extra, duck=DUCK,
           hall=dict(rt_low=2.6, rt_mid=2.2, rt_high=1.2, predelay=.025, length=4.5),
           sidechain=(("drums",), ("strings", "brass", "choir"), 1.5),
           tone=[PeakFilter(500, -1.5, .8), HighShelfFilter(cutoff_frequency_hz=8000, gain_db=1.5)])
