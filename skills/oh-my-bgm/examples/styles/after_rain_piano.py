"""After the Rain — sad but not hopeless: piano with a flowing left hand, the tune passing to the cello,
a high violin over a descending cello line, and a last chord that turns to D major (a Picardy third: the light
coming back). Suits: memorial and farewell videos, emotional stories, charity films, quiet endings.
D minor, 72 BPM, 36 bars (~2:00); with --loop a seamless loop (stays minor, drops the ending).

A  | Dm | Bbmaj7 | F/A | C | Gm7 | Dm/F | Ebmaj7 | A7sus4 A7 |     (Eb = the Neapolitan, the ache)
B  | Bb | F/A | Gm7 | Dm | Bb | C | Asus4 | A |
Form: intro 2 (left hand) · A piano · A cello, piano answers high · B violin + cello line, strings ·
A piano + strings, cello counter · ending 2 (D major).
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/after_rain_piano.py [--loop]   -> ./out/after_rain_piano/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402

from orch import Song, n, nearest  # noqa: E402
from score import P, finish, play, seq  # noqa: E402

BPM, B = 72, 4
song = Song(bpm=BPM, beats=(34 if LOOP else 36) * B, tail=6.0, seed=72)
# chord -> (bass pc, root pc, third, fifth interval)
CH = {"Dm": (2, 2, 3, 7), "Bbmaj7": (10, 10, 4, 7), "F/A": (9, 5, 4, 7), "C": (0, 0, 4, 7), "Gm7": (7, 7, 3, 7),
      "Dm/F": (5, 2, 3, 7), "Ebmaj7": (3, 3, 4, 7), "A7sus4": (9, 9, 5, 7), "A7": (9, 9, 4, 7), "Bb": (10, 10, 4, 7),
      "Asus4": (9, 9, 5, 7), "A": (9, 9, 4, 7), "D": (2, 2, 4, 7)}
CA = [["Dm"], ["Bbmaj7"], ["F/A"], ["C"], ["Gm7"], ["Dm/F"], ["Ebmaj7"], ["A7sus4", "A7"]]
CB = [["Bb"], ["F/A"], ["Gm7"], ["Dm"], ["Bb"], ["C"], ["Asus4"], ["A"]]
FORM = [("intro", [["Dm"], ["Dm"]]), ("A1", CA), ("A2", CA), ("B", CB), ("A3", CA)] + ([] if LOOP else [("end", [["D"], ["D"]])])
BARS = [(sec, chs) for sec, bars in FORM for chs in bars]

MEL_A = ("A4/1.5 D5/.5 E5/1 F5/1 | F5/1.5 D5/.5 A4/2 | C5/1.5 F5/.5 G5/1 A5/1 | G5/3 E5/1 | "
         "F5/1.5 D5/.5 Bb4/1 D5/1 | A4/2 F5/1 E5/1 | D5/1.5 Eb5/.5 G5/2 | D5/2 C#5/2")
ANSWERS = "r/4 | r/2 A5/1 D6/1 | r/4 | r/2 C6/1 E6/1 | r/4 | r/2 F5/1 A5/1 | r/4 | r/2 E6/2"
VIOLIN_B = ("D6/2 C6/1 Bb5/1 | A5/2 C6/2 | Bb5/1.5 A5/.5 G5/1 F5/1 | A5/4 | D6/1.5 C6/.5 Bb5/1 D6/1 | "
            "G5/1 C6/1 E6/2 | D6/3 E6/1 | C#6/4")
CELLO_B = "D3/2 F3/2 | C3/2 A2/2 | Bb2/2 D3/2 | A2/2 F3/2 | D3/2 F3/2 | E3/2 G3/2 | D3/4 | C#3/4"
CELLO_A3 = "D3/4 | D3/2 F3/2 | C3/4 | E3/2 G3/2 | Bb2/2 D3/2 | A2/2 C3/2 | G2/2 Bb2/2 | A2/2 G2/2"

piano = P("piano", 0, pan=0, width=1.3, level=-18, send=-6, bus="piano", jitter_ms=6,
          eq=[HighpassFilter(55), PeakFilter(300, -1.5, 1)])
cello = P("cello", 42, 17, expr_cc=2, pan=.25, level=-18, send=-5, bus="strings", jitter_ms=5, legato=.1,
          eq=[HighpassFilter(60), PeakFilter(300, -1.5, 1), LowpassFilter(7000)])
violin = P("violin", 40, 17, expr_cc=2, pan=-.25, level=-18.5, send=-4, bus="strings", jitter_ms=5, legato=.08,
           eq=[HighpassFilter(280), PeakFilter(2800, -3, 1.2), LowpassFilter(9000)])
pad = P("strings", 49, 17, expr_cc=2, players=2, pan=0, width=1.6, level=-25, send=-4, bus="strings", legato=.3,
        eq=[HighpassFilter(180), PeakFilter(2500, -2, 1)])

for bar, (sec, chs) in enumerate(BARS):
    span = B / len(chs)
    for ci, c in enumerate(chs):
        b0 = bar * B + ci * span
        bpc, r, th, fi = CH[c]
        lo = nearest(bpc, n("D2"))
        root = nearest(r, n("D3"))
        if sec == "end":
            if bar == len(BARS) - 2:
                for k, q in enumerate((lo, lo + 7, root + 12, root + 16, root + 19, root + 24)):
                    piano.add(b0 + k * .25, 2 * B - k * .25, q, 56 - k * 2)
                play(pad, [(b0, 2 * B, q) for q in (n("D4"), n("F#4"), n("A4"))], 66)
                play(cello, [(b0, 2 * B, n("D3"))], 72)
                play(violin, [(b0 + 1, 2 * B - 1, n("F#5"))], 70)
            continue
        # left hand: 8ths low root, fifth, tenth, fifth ... and the bar's pedal change
        lh = [lo, root + fi, root + 12 + th, root + fi + 12, root + 12 + th, root + fi]
        if sec == "intro" or span == 4:
            lh = lh + [root + 12, root + fi]
        for k, q in enumerate(lh[: int(span * 2)]):
            piano.add(b0 + k * .5, min(1.6 if k == 0 else 1.0, span - k * .5), q, (58 if k == 0 else 46) - (4 if sec == "B" else 0))
        if sec in ("B", "A3"):
            for q in (nearest(r, n("D4")), nearest((r + th) % 12, n("F4")), nearest((r + fi) % 12, n("A4"))):
                pad.add(b0, span, q, 62 if sec == "B" else 68)

play(piano, seq(MEL_A, 2 * B), 70, extend=.3)
play(cello, seq(MEL_A, 10 * B, shift=-12), 90)
play(piano, seq(ANSWERS, 10 * B), 54, extend=.6)
play(violin, seq(VIOLIN_B, 18 * B), 92)
play(cello, seq(CELLO_B, 18 * B), 80)
play(piano, seq(MEL_A, 26 * B), 76, extend=.3)
play(cello, seq(CELLO_A3, 26 * B), 76)

if __name__ == "__main__":
    finish("after_rain_piano", [piano, cello, violin, pad], song,
           [("intro", 0, 2), ("A1", 2, 10), ("A2", 10, 18), ("B", 18, 26), ("A3", 26, 34)],
           lead={"cello", "violin"}, beats_per_bar=B, loop=LOOP,
           hall=dict(rt_low=2.8, rt_mid=2.4, rt_high=1.3, predelay=.03, length=4.5))
