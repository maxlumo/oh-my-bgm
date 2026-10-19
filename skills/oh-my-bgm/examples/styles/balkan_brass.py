"""Copper Wedding — a Balkan brass band at full joy in 9/8 (2+2+2+3): trumpet and clarinet trading a
twisting tune in the "Gypsy" minor (D E F G# A Bb C#), tuba on every group, trombone and accordion on the
off-beats, a big drum with a stick, and a last chorus where everyone plays.
Feels: exuberant, sweaty, irresistible, slightly wild. Scenes: a wedding or festival, a chase through a market,
travel montages, comic chaos, a celebration at the end of a story.
D minor (Gypsy scale), 8th = 300 (bar = 9 eighths, 1.8 s), 44 bars (~1:22).

A | Dm | Dm | A7 | Dm | Gm | Dm | A7 | Dm |
B | F | C7 | F | Bb | Gm | Dm | E7 | A7 |
Form: intro 2 (drum, tuba, off-beats) · A trumpet · A trumpet + clarinet in thirds · B clarinet · B trumpet ·
A everyone, accordion · ending 2 (unison run and a hit).
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/balkan_brass.py   -> ./out/balkan_brass/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402

from orch import Song, n, nearest  # noqa: E402
from score import P, finish, kit, play, seq  # noqa: E402

BPM, B = 300, 9                        # one beat = one 8th; groups 2+2+2+3
GROUPS = (0, 2, 4, 6)
Q = {"Dm": (2, 3), "A7": (9, 4), "Gm": (7, 3), "F": (5, 4), "C7": (0, 4), "Bb": (10, 4), "E7": (4, 4)}
CA = ["Dm", "Dm", "A7", "Dm", "Gm", "Dm", "A7", "Dm"]
CB = ["F", "C7", "F", "Bb", "Gm", "Dm", "E7", "A7"]
FORM = [("intro", ["Dm", "Dm"]), ("A1", CA), ("A2", CA), ("B1", CB), ("B2", CB), ("A3", CA), ("end", ["A7", "Dm"])]
BARS = [(sec, c) for sec, chs in FORM for c in chs]
START = {}
for i, (sec, _) in enumerate(BARS):
    START.setdefault(sec, i)
song = Song(bpm=BPM, beats=len(BARS) * B, tail=3.0, seed=300)

TUNE_A = ("D5/2 F5/1 E5/1 D5/1 C#5/1 D5/3 | A5/2 G#5/1 A5/1 Bb5/2 A5/3 | G5/1 F5/1 E5/1 F5/1 G5/2 C#5/3 | "
          "F5/1 E5/1 D5/4 A4/3 | G5/2 Bb5/1 A5/1 G5/1 F5/1 G5/3 | F5/2 A5/1 G#5/1 F5/1 E5/1 D5/3 | "
          "E5/1 F5/1 G5/1 A5/1 Bb5/2 A5/1 C#5/2 | D5/6 r/3")
TUNE_B = ("C5/2 F5/2 A5/2 G5/3 | Bb5/2 A5/1 G5/1 E5/2 C5/3 | A5/2 C6/2 A5/2 F5/3 | D6/2 C6/1 Bb5/1 A5/2 F5/3 | "
          "G5/2 Bb5/1 A5/1 G5/2 D5/3 | F5/2 E5/1 D5/1 C#5/2 D5/3 | G#5/2 B5/1 A5/1 G#5/2 E5/3 | C#5/2 E5/1 G5/1 Bb5/2 A5/3")


def harmony_below(beat, p):
    """The highest tone of the bar's chord 3-9 semitones under the tune (a third or a sixth, never a second)."""
    r, third = Q[BARS[int(beat // B)][1]]
    tones = {r, (r + third) % 12, (r + 7) % 12}
    for d in range(3, 10):
        if (p - d) % 12 in tones:
            return p - d
    return p - 12


tpt = P("trumpet", 56, 17, expr_cc=2, pan=-.2, level=-17, send=-8, bus="lead", jitter_ms=4, legato=-.06,
        eq=[HighpassFilter(220), PeakFilter(2500, -2, 1), LowpassFilter(9000)])
clar = P("clarinet", 71, 17, expr_cc=2, pan=.2, level=-18, send=-8, bus="lead", jitter_ms=4, legato=-.05,
         eq=[HighpassFilter(200)])
bone = P("trombones", 57, 17, expr_cc=2, players=2, pan=.3, width=1.3, level=-23, send=-8, bus="band", legato=-.1,
         eq=[HighpassFilter(100), PeakFilter(800, -1.5, 1)])
tuba = P("tuba", 58, 17, expr_cc=2, pan=0, width=.3, level=-20, send=-14, bus="band", legato=-.15,
         eq=[HighpassFilter(35), LowpassFilter(3000)])
accordion = P("accordion", 21, 17, expr_cc=2, pan=-.35, width=1.2, level=-25, send=-8, bus="band", legato=-.1,
              eq=[HighpassFilter(200), PeakFilter(1200, -2, 1)])
drum = kit("tapan", 0, width=1.1, level=-21, send=-10, bus="drums", jitter_ms=3, eq=[HighpassFilter(40)])
tamb = kit("tambourine", 0, pan=.35, level=-29, send=-8, bus="drums", jitter_ms=3, eq=[HighpassFilter(800)])
BIG, STICK, TAMB = 36, 37, 54

for bar, (sec, c) in enumerate(BARS):
    b0 = bar * B
    r, third = Q[c]
    lo = nearest(r, n("D2"))
    chord = [nearest(r, n("D4")), nearest((r + third) % 12, n("F4")), nearest((r + 7) % 12, n("A4"))]
    if sec == "end":
        if bar == START["end"]:  # unison run up the A7 into the last bar
            run = [n(q) for q in ("A4", "C#5", "E5", "G5", "A5", "Bb5", "A5", "G#5", "A5")]
            for i, m in enumerate(run):
                for p_, sh in ((tpt, 0), (clar, 0), (bone, -12)):
                    p_.add(b0 + i, .8, m + sh, 104)
            for g in GROUPS:
                drum.add(b0 + g, .3, BIG, 110)
        else:
            for p_, ms in ((tpt, (n("D5"), n("A5"))), (clar, (n("F5"),)), (bone, (n("D4"), n("A3"), n("F4"))),
                           (accordion, chord), (tuba, (n("D2"),))):
                for m in ms:
                    p_.add(b0, 3, m, 118)
            drum.add(b0, .5, BIG, 124)
            tamb.add(b0, .5, TAMB, 100)
        continue
    for gi, g in enumerate(GROUPS):  # tuba on each group: root, fifth alternating
        tuba.add(b0 + g, 1.4 if g < 6 else 2.4, lo if gi % 2 == 0 else lo + 7, 100 if g in (0, 6) else 86)
    for off in (1, 3, 5, 7, 8):  # off-beats
        for q in chord:
            bone.add(b0 + off, .6, q - 12 if q > n("A4") else q, 78 if off != 8 else 70)
            if sec in ("A3", "B2"):
                accordion.add(b0 + off, .6, q, 70)
    for e in range(9):
        if e in GROUPS:
            drum.add(b0 + e, .3, BIG, 108 if e in (0, 6) else 92)
        else:
            drum.add(b0 + e, .2, STICK, 62 + (12 if e == 8 else 0))
        if sec != "intro" and e not in GROUPS:
            tamb.add(b0 + e, .2, TAMB, 58)

play(tpt, seq(TUNE_A, START["A1"] * B), 96)
play(tpt, seq(TUNE_A, START["A2"] * B), 98)
play(clar, [(b, d, harmony_below(b, p)) for b, d, p in seq(TUNE_A, START["A2"] * B)], 86)
play(clar, seq(TUNE_B, START["B1"] * B), 96)
play(tpt, seq(TUNE_B, START["B2"] * B), 100)
play(clar, seq(TUNE_B, START["B2"] * B, shift=-12), 80)
play(tpt, seq(TUNE_A, START["A3"] * B), 104)
play(clar, seq(TUNE_A, START["A3"] * B, shift=12), 88)

if __name__ == "__main__":
    S = START
    finish("balkan_brass", [tpt, clar, bone, tuba, accordion, drum, tamb], song,
           [("A1", S["A1"], S["A2"]), ("A2", S["A2"], S["B1"]), ("B1", S["B1"], S["B2"]), ("B2", S["B2"], S["A3"]),
            ("A3", S["A3"], S["end"])],
           lead={"trumpet", "clarinet"}, beats_per_bar=B, lufs=-14.0,
           hall=dict(rt_low=1.4, rt_mid=1.2, rt_high=.7, predelay=.015, length=2.6))
