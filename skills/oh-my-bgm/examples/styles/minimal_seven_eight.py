"""Deep Pool — minimalism for concentration: a marimba ostinato in 7/8 (2+2+3), a 5-note celesta loop
that drifts against it (5 against 7 realigns every 5 bars), solo cello in long notes. Suits: puzzles and
dungeons, focus / study, science and tech explainers under a voice.
E minor / C Lydian, 8th = 252 (bar = 7 eighths), 48 bars (~1:25) + a final Em; with --loop a seamless loop.

Harmony (2 bars each): Em | C | Am | B(sus)
Layers: 0 marimba, bass · 8 + celesta, glass pad · 16 + cello, light percussion · 32 harp and choir instead of
the cello · 40 back to marimba + celesta.
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/minimal_seven_eight.py [--loop]   -> ./out/minimal_seven_eight/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv  # optional seamless game loop; default: a whole piece with an ending

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter

from orch import GM_SF, GU_SF, SR, Song, n, nearest  # noqa: E402,F401
from score import P, finish, kit, play, seq, swing  # noqa: E402,F401

BPM, B = 252, 7
song = Song(bpm=BPM, beats=(48 if LOOP else 49) * B, tail=5.0, seed=7)
CH = [(4, 3, 6), (4, 3, 6), (0, 4, 2), (0, 4, 2), (9, 3, 11), (9, 3, 11), (11, 5, 9), (11, 4, 6)]  # root, 3rd/4th, colour pc

CELLO = ("B3/4 E4/3 | F#4/4 G4/3 | E4/7 | D4/4 E4/3 | C4/4 B3/3 | A3/7 | F#3/4 A3/3 | B3/7 | "
         "G4/4 F#4/3 | E4/4 B4/3 | B4/7 | A4/4 G4/3 | E4/4 F#4/3 | G4/4 E4/3 | D#4/4 F#4/3 | B3/7")
CELESTA = [n(q) for q in ("B5", "F#5", "E5", "G5", "D5")]

marimba = P("marimba", 12, pan=-.2, width=1.2, level=-20, send=-9, bus="mallets", jitter_ms=3,
            eq=[HighpassFilter(150), PeakFilter(600, -1.5, 1)])
celesta = P("celesta", 8, pan=.3, width=1.2, level=-23, send=-7, bus="mallets", jitter_ms=3,
            eq=[HighpassFilter(400)])
cello = P("cello", 42, 17, expr_cc=2, pan=-.05, level=-18, send=-6, bus="lead", jitter_ms=5, legato=.1,
          eq=[HighpassFilter(70), PeakFilter(300, -1.5, 1), LowpassFilter(7000)])
glass = P("glass_pad", 92, 17, expr_cc=2, pan=0, width=1.6, level=-30, send=-5, bus="pad", legato=.5,
          eq=[HighpassFilter(250), LowpassFilter(6000)])
choir = P("choir", 53, 17, expr_cc=2, players=2, pan=.1, width=1.5, level=-26, send=-4, bus="pad", legato=.4,
          eq=[HighpassFilter(200), PeakFilter(2500, -2, 1)])
harp = P("harp", 46, pan=-.35, width=1.3, level=-21, send=-6, bus="mallets", jitter_ms=3, eq=[HighpassFilter(150)])
bass = P("basses", 49, 51, expr_cc=2, pan=.1, level=-23, send=-10, bus="bass", legato=.3,
         eq=[HighpassFilter(35), LowpassFilter(2500)])
perc = kit("perc", 0, sf2=GU_SF, pan=.25, width=1.3, level=-31, send=-10, bus="perc", jitter_ms=3,
           eq=[HighpassFilter(300)])
CABASA, STICK = 69, 37

for bar in range(48):
    b0 = bar * B
    r, x, col = CH[bar % 8]
    root = nearest(r, n("E4"))
    third = nearest((r + x) % 12, root + 4)
    fifth, ninth = root + 7, nearest(col, root + 14)
    pat = [root, fifth, third, fifth, ninth, fifth, root + 12]
    thin = 32 <= bar < 40
    for k, q in enumerate(pat):
        if thin and k % 2:
            continue
        marimba.add(b0 + k, .9, q, 84 if k in (0, 2, 4) else 66)
    if bar >= 8:  # celesta: a 5-step loop over the 7-step bar, quarter of the time an octave up
        for k in range(7):
            step = bar * 7 + k
            if step % 2 == 0:
                q = CELESTA[(step // 2) % 5] + (12 if (step // 10) % 4 == 3 else 0)
                chord = {r, (r + x) % 12, (r + 7) % 12, col}
                if any((q - c) % 12 in (1, 11) for c in chord) and q % 12 not in chord:  # avoid note: step to a chord tone
                    q = min((q + d for d in (-2, -1, 1, 2) if (q + d) % 12 in chord), key=lambda v: abs(v - q))
                celesta.add(b0 + k, 1.6, q, 70 if bar < 40 else 62)
    if bar % 2 == 0:
        lo = nearest(r, n("E2"))
        bass.add(b0, 2 * B, lo, 70 if bar < 16 else 80)
        if 8 <= bar < 40:
            g0 = nearest(r, n("E3"))
            for q in (g0, g0 + 7, g0 + 12):  # open: the colour note is left to the mallets
                glass.add(b0, 2 * B, q, 64)
        if 32 <= bar < 40:
            for q in (nearest(r, n("E4")), nearest((r + 7) % 12, n("B4"))):  # open fifth, above the pad
                choir.add(b0, 2 * B, q, 72)
            for k, q in enumerate((lo + 12, lo + 19, lo + 24, third, ninth, root + 19)):
                harp.add(b0 + 7 + k * .5, 4, q, 66 + k * 2)
    if 16 <= bar < 40:
        for k in range(7):
            perc.add(b0 + k, .2, CABASA, 50 + (14 if k in (0, 2, 4) else 0))
        perc.add(b0 + 4, .2, STICK, 52)

play(cello, seq(CELLO, 16 * B), 86)
if not LOOP:  # ending: the cycle's B resolves to E minor, marimba and celesta let it ring
    e = 48 * B
    play(marimba, seq("E3+B3+E4+G4/7", e), 74)
    play(celesta, seq("B5/7", e), 62)
    play(bass, seq("E2/7", e), 74)
    play(glass, seq("E3+B3+E4/7", e), 60)

if __name__ == "__main__":
    finish("minimal_seven_eight", [marimba, celesta, cello, glass, choir, harp, bass, perc], song,
           [("0-8", 0, 8), ("8-16", 8, 16), ("16-32", 16, 32), ("32-40", 32, 40), ("40-48", 40, 48)],
           lead={"cello", "celesta", "harp"}, beats_per_bar=B, loop=LOOP,
           hall=dict(rt_low=2.6, rt_mid=2.3, rt_high=1.3, predelay=.025, length=4.5))
