"""Gambit — a chamber orchestra thinking two moves ahead. Suits: turn-based strategy maps, puzzles
with a plan, business-strategy and history explainers. A minor, 100 BPM, 40 bars (~1:40) + a final Am;
with --loop a seamless loop (outro = intro).

A  | Am | F | Dm | E | Am | C | Dm E | Am |
B  | F | G | Em | Am | Dm | G | C | E |
Form: intro 4 (harpsichord, pizz) · A clarinet · A oboe + bassoon counterline · B violins, horns, snare ·
A tutti · outro 4.
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/chamber_tactics.py [--loop]   -> ./out/chamber_tactics/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv  # optional seamless game loop; default: a whole piece with an ending

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter

from orch import GM_SF, GU_SF, SR, Song, n, nearest  # noqa: E402,F401
from score import P, finish, kit, play, seq, swing  # noqa: E402,F401

BPM, B = 100, 4
song = Song(bpm=BPM, beats=(40 if LOOP else 41) * B, tail=4.0, seed=100)
Q = {"Am": (9, 3), "F": (5, 4), "Dm": (2, 3), "E": (4, 4), "C": (0, 4), "G": (7, 4), "Em": (4, 3)}
CA = [["Am"], ["F"], ["Dm"], ["E"], ["Am"], ["C"], ["Dm", "E"], ["Am"]]
CB = [["F"], ["G"], ["Em"], ["Am"], ["Dm"], ["G"], ["C"], ["E"]]
INTRO = [["Am"], ["F"], ["Dm"], ["E"]]
FORM = [("intro", INTRO), ("A1", CA), ("A2", CA), ("B", CB), ("A3", CA), ("outro", INTRO)]
BARS = [(sec, chs) for sec, bars in FORM for chs in bars]

MEL_A = ("A4/.75 B4/.25 C5/1 E5/1.5 D5/.5 | C5/1 A4/1 F5/1.5 E5/.5 | D5/.75 E5/.25 F5/1 A5/1 G5/.5 F5/.5 | "
         "E5/1 G#4/1 B4/2 | A4/.75 B4/.25 C5/1 E5/1.5 D5/.5 | E5/1 G5/1 C6/1.5 B5/.5 | "
         "A5/.5 G5/.5 F5/.5 E5/.5 D5/1 B4/1 | C5/.5 B4/.5 A4/3")
COUNTER = ("A3/1 E3/1 A3/1 C4/1 | F3/1 C4/1 A3/1 F3/1 | D3/1 F3/1 A3/1 D4/1 | E3/1 B3/1 G#3/1 E3/1 | "
           "A3/1 C4/1 E4/1 C4/1 | C4/1 G3/1 E3/1 G3/1 | F3/1 D3/1 E3/1 G#3/1 | A3/2 E3/1 A2/1")
MEL_B = ("F5/1.5 E5/.5 C5/2 | D5/1.5 E5/.5 G5/2 | B5/1.5 A5/.5 G5/1 E5/1 | A5/2 C6/1 B5/1 | "
         "A5/1.5 G5/.5 F5/1 D5/1 | G5/1.5 F5/.5 D5/1 B4/1 | C5/1 E5/1 G5/1 C6/1 | B5/2 G#5/2")

clar = P("clarinet", 71, 17, expr_cc=2, pan=-.2, level=-19.5, send=-8, bus="winds", jitter_ms=4, legato=-.04,
         eq=[HighpassFilter(180), LowpassFilter(9000)])
oboe = P("oboe", 68, 17, expr_cc=2, pan=.15, level=-17.5, send=-8, bus="winds", jitter_ms=4, legato=-.04,
         eq=[HighpassFilter(250), PeakFilter(1500, -1.5, 1)])
bsn = P("bassoon", 70, 17, expr_cc=2, pan=.3, level=-22, send=-8, bus="winds", jitter_ms=4, legato=-.12,
        eq=[HighpassFilter(60), PeakFilter(400, -1, 1)])
vln = P("violins", 49, 21, expr_cc=2, players=2, pan=-.35, width=1.3, level=-19.5, send=-6, bus="strings",
        legato=.06, eq=[HighpassFilter(250), PeakFilter(3000, -2, 1)])
vln_pad = P("violins_pad", 49, 26, expr_cc=2, players=2, pan=-.2, width=1.4, level=-26, send=-5, bus="strings",
            legato=.15, eq=[HighpassFilter(250), PeakFilter(3000, -2, 1)])
horns = P("horns", 60, 17, expr_cc=2, players=2, pan=.25, width=1.2, level=-24, send=-5, bus="brass", legato=.1,
          eq=[HighpassFilter(90), LowpassFilter(5000)])
hpsi = P("harpsichord", 6, pan=.2, width=1.3, level=-24, send=-9, bus="keys", jitter_ms=3,
         eq=[HighpassFilter(200), PeakFilter(2500, -2, 1), LowpassFilter(9000)])
pizz = P("pizz_low", 45, players=2, pan=-.1, width=1.2, level=-21, send=-8, bus="strings", jitter_ms=4,
         eq=[HighpassFilter(45), PeakFilter(250, -1, 1)])
timp = P("timpani", 47, pan=0, level=-26, send=-7, bus="perc", jitter_ms=3, roll=.125, eq=[HighpassFilter(40)])
snare = kit("snare", 48, sf2=GM_SF, pan=.1, level=-30, send=-8, bus="perc", jitter_ms=3, eq=[HighpassFilter(150)])

voice_top = n("E5")
for bar, (sec, chs) in enumerate(BARS):
    b0 = bar * B
    half = B / len(chs)
    for ci, c in enumerate(chs):
        cb = b0 + ci * half
        r, third = Q[c]
        ts = [r, (r + third) % 12, (r + 7) % 12]
        lo = nearest(r, n("A2"))
        # pizz: root, fifth, octave, fifth (quarters)
        for k in range(int(half)):
            q = [lo, lo + 7, lo + 12, lo + 7][k] if half == 4 else [lo, lo + 7][k]
            pizz.add(cb + k, .5, q, 86 if k == 0 else 72)
        # harpsichord: broken chord in 8ths (thins out under the B tune)
        if sec != "B":
            pat = [nearest(ts[0], n("A3")), nearest(ts[2], n("E4")), nearest(ts[1], n("C5")), nearest(ts[2], n("E4"))]
            for k in range(int(half * 2)):
                hpsi.add(cb + k * .5, .45, pat[k % 4] + (12 if k % 8 == 4 else 0), 74 if k % 2 == 0 else 62)
        if sec in ("B", "A3"):
            for q in (nearest(ts[0], n("F3")), nearest(ts[1], n("A3")), nearest(ts[2], n("C4"))):
                horns.add(cb, half, q, 74 if sec == "B" else 66)
        if sec == "A3":
            voice_top = min((nearest(t, voice_top) for t in ts[1:]), key=lambda q: abs(q - voice_top))
            vln_pad.add(cb, half, voice_top, 78)
            vln_pad.add(cb, half, nearest(ts[0], voice_top - 4), 70)
    if sec in ("B", "A3"):
        if bar % 2 == 0:
            timp.add(b0, .9, nearest(Q[chs[0]][0], n("A2")), 82)
        for bb, v in [(0, 70), (1.5, 50), (1.75, 54), (2, 62), (3.5, 50), (3.75, 56)]:
            snare.add(b0 + bb, .2, 38, v - (8 if sec == "A3" else 0))
    if bar in (19, 35):  # timpani roll into B and the outro
        timp.add(b0 + 2, 2, n("E2"), 76)

play(clar, seq(MEL_A, 4 * B), 90)
play(oboe, seq(MEL_A, 12 * B), 90)
play(bsn, seq(COUNTER, 12 * B), 84)
play(vln, seq(MEL_B, 20 * B), 92)
play(clar, seq(MEL_B, 20 * B, shift=-12), 60)        # clarinet doubles the violins softly, 8vb
play(oboe, seq(MEL_A, 28 * B), 92)
play(clar, seq(MEL_A, 28 * B, shift=-12), 80)
play(bsn, seq(COUNTER, 28 * B), 86)
play(clar, seq("A4/.75 B4/.25 C5/1 E5/1.5 D5/.5 | C5/1 A4/1 F5/2 | r/4 | E5/2 G#4/2", 36 * B), 72)
if not LOOP:  # ending: the outro's E resolves to A minor
    e = 40 * B
    play(clar, seq("A4/4", e), 74)
    play(horns, seq("A3+C4+E4/4", e), 70)
    play(bsn, seq("A2/4", e), 80)
    play(pizz, seq("A2/1", e), 90)
    for k, q in enumerate(("A3", "E4", "A4", "C5")):
        hpsi.add(e + k * .08, 2, q, 76)
    timp.add(e, 1, n("A2"), 80)

if __name__ == "__main__":
    finish("chamber_tactics", [clar, oboe, bsn, vln, vln_pad, horns, hpsi, pizz, timp, snare], song,
           [("intro", 0, 4), ("A1", 4, 12), ("A2", 12, 20), ("B", 20, 28), ("A3", 28, 36)],
           lead={"clarinet", "oboe", "violins"}, beats_per_bar=B, loop=LOOP,
           hall=dict(rt_low=1.9, rt_mid=1.7, rt_high=1.0, predelay=.02, length=3.5))
