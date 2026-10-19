"""Candlelit Ruins — a melancholy chamber waltz. Piano broken chords with a sad 9th, solo violin,
cello taking the tune over, a descending cello line under the major-key middle, far-away choir, a music-box
memory at the end. Suits: ruins and underground towns, memorial / farewell videos, quiet sad stories.
C minor, 3/4 at 80 BPM, 40 bars (~1:30) + 2 bars of C minor; with --loop a seamless loop.

A  | Cm | Ab | Fm | G | Cm | Eb/Bb | Ab | G |
B  | Eb | Bb/D | Cm | G/B | Ab | Fm | Dm7b5 | G |      (cello: Eb D C B Ab F D G)
Form: intro 4 (piano) · A violin · A cello melody + violin countermelody, harp · B violin + viola, choir ·
A violin + cello counter, everyone · outro 4 (piano, music box).
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/melancholy_waltz.py [--loop]   -> ./out/melancholy_waltz/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv  # optional seamless game loop; default: a whole piece with an ending

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402

from orch import Song, n, nearest  # noqa: E402
from score import P, finish, play, seq  # noqa: E402

BPM, B = 80, 3
song = Song(bpm=BPM, beats=(40 if LOOP else 42) * B, tail=5.0, seed=80)
# chord -> (root, third, tension above the root in semitones, bass pc)
C = {"Cm": (0, 3, 14, 0), "Ab": (8, 4, 14, 8), "Fm": (5, 3, 14, 5), "G": (7, 4, 12, 7), "Eb/Bb": (3, 4, 14, 10),
     "Eb": (3, 4, 14, 3), "Bb/D": (10, 4, 14, 2), "G/B": (7, 4, 12, 11), "Dm7b5": (2, 3, 10, 2)}
CA = ["Cm", "Ab", "Fm", "G", "Cm", "Eb/Bb", "Ab", "G"]
CB = ["Eb", "Bb/D", "Cm", "G/B", "Ab", "Fm", "Dm7b5", "G"]
FORM = [("intro", CA[:4]), ("A1", CA), ("A2", CA), ("B", CB), ("A3", CA), ("outro", CA[:4])]
BARS = [(sec, c) for sec, chs in FORM for c in chs]

MEL_A = "G4/2 C5/1 | Eb5/2 D5/.5 C5/.5 | C5/1.5 Bb4/.5 Ab4/1 | B4/3 | G4/2 C5/1 | G5/2 F5/.5 Eb5/.5 | Eb5/1 D5/1 C5/1 | D5/1.5 C5/.5 B4/1"
COUNTER = "Eb5/2 G5/1 | Ab5/2 G5/1 | F5/2 Eb5/1 | D5/3 | Eb5/2 G5/1 | Bb5/2 Ab5/1 | G5/1 F5/1 Eb5/1 | D5/3"
MEL_B = "Bb4/1 Eb5/1 G5/1 | F5/2 D5/1 | Eb5/1 G5/1 C6/1 | B5/2 G5/1 | C6/1.5 Bb5/.5 Ab5/1 | Ab5/1 G5/1 F5/1 | F5/1.5 Eb5/.5 D5/1 | D5/2 B4/1"
VIOLA_B = "G4/3 | F4/3 | G4/3 | D4/3 | Eb4/3 | C4/3 | Ab3/3 | B3/3"
CELLO_B = "Eb3/3 | D3/3 | C3/3 | B2/3 | Ab2/3 | F2/3 | D2/3 | G2/3"
CELLO_A3 = "C3/3 | Ab2/1.5 C3/1.5 | F3/3 | G2/1.5 D3/1.5 | Eb3/3 | Bb2/3 | Ab2/1.5 C3/1.5 | G2/3"

piano = P("piano", 0, pan=0, width=1.2, level=-19, send=-7, bus="piano", jitter_ms=6,
          eq=[HighpassFilter(55), PeakFilter(300, -1.5, 1)])
violin = P("violin", 40, 17, expr_cc=2, pan=-.25, level=-17.5, send=-6, bus="strings", jitter_ms=5, legato=.08,
           eq=[HighpassFilter(250), PeakFilter(2800, -2.5, 1.2), LowpassFilter(9000)])
viola = P("viola", 41, 17, expr_cc=2, pan=.2, level=-22, send=-6, bus="strings", jitter_ms=5, legato=.1,
          eq=[HighpassFilter(180), PeakFilter(2500, -2, 1)])
cello = P("cello", 42, 17, expr_cc=2, pan=.3, level=-19, send=-6, bus="strings", jitter_ms=5, legato=.1,
          eq=[HighpassFilter(60), PeakFilter(300, -1, 1), LowpassFilter(7000)])
choir = P("choir", 53, 17, expr_cc=2, players=2, pan=0, width=1.6, level=-27, send=-3, bus="choir", legato=.4,
          eq=[HighpassFilter(200), PeakFilter(2500, -2, 1), LowpassFilter(7000)])
harp = P("harp", 46, pan=-.4, width=1.3, level=-25, send=-6, bus="piano", jitter_ms=4, eq=[HighpassFilter(150)])
musicbox = P("music_box", 10, pan=.3, level=-18, send=-4, bus="piano", jitter_ms=4, eq=[HighpassFilter(500)])
timp = P("timpani", 47, pan=-.1, level=-28, send=-6, bus="perc", roll=.125, eq=[HighpassFilter(40)])

for bar, (sec, c) in enumerate(BARS):
    b0 = bar * B
    r, third, tens, bass_pc = C[c]
    lo = nearest(bass_pc, n("C3") if sec != "outro" else n("C3"))
    root = nearest(r, n("C3"))
    fifth = root + (6 if c == "Dm7b5" else 7)
    arp = [lo - 12 if sec in ("B", "A3") else lo, fifth, root + 12 + third, root + tens + 12 * (tens < 12),
           root + 12 + third, fifth]
    soft = sec in ("B",)
    for k, q in enumerate(arp):
        dur = B - k * .5 if k == 0 else min(1.4, B - k * .5)  # pedal change at the bar line
        piano.add(b0 + k * .5, dur, q, (62 if k == 0 else 50 + (4 if k == 3 else 0)) - (6 if soft else 0))
    if sec in ("B", "A3"):
        c4 = nearest(r, n("C4"))  # open: root, fifth, octave (the piano's 9th sits right under a third)
        for q in (c4, c4 + fifth - root, c4 + 12):
            choir.add(b0, B, q, 64 if sec == "B" else 74)
    if sec == "A2" and bar % 4 == 3:
        for k, q in enumerate((root + 12, fifth + 12, root + 24 + third, root + 31)):
            harp.add(b0 + 1 + k / 3, 2 - k / 3 - .05, q, 64 + k * 3)
    if bar in (20, 28):
        timp.add(b0, 2.5, nearest(bass_pc, n("C2")), 70)

play(violin, seq(MEL_A, 4 * B), 86)
play(cello, seq(MEL_A, 12 * B, shift=-12), 90)
play(violin, seq(COUNTER, 12 * B), 70)
play(violin, seq(MEL_B, 20 * B), 92)
play(viola, seq(VIOLA_B, 20 * B), 74)
play(cello, seq(CELLO_B, 20 * B), 80)
play(violin, seq(MEL_A, 28 * B), 96)
play(cello, seq(CELLO_A3, 28 * B), 84)
play(musicbox, seq("G5/2 C6/1 | Eb6/2 D6/.5 C6/.5 | C6/1.5 Bb5/.5 Ab5/1 | B5/3", 36 * B), 74, extend=.5)
if not LOOP:  # ending: the outro's G resolves to a held C minor (two bars)
    e = 40 * B
    for k, q in enumerate(("C2", "G2", "Eb3", "G3", "C4", "Eb4")):
        piano.add(e + k * .15, 2 * B - k * .15, q, 58 - k * 2)
    play(musicbox, seq("C6/6", e), 70)
    play(cello, seq("C3/6", e), 70)

if __name__ == "__main__":
    finish("melancholy_waltz", [piano, violin, viola, cello, choir, harp, musicbox, timp], song,
           [("intro", 0, 4), ("A1", 4, 12), ("A2", 12, 20), ("B", 20, 28), ("A3", 28, 36), ("outro", 36, 40)],
           lead={"violin", "cello", "music_box"}, beats_per_bar=B, loop=LOOP,
           hall=dict(rt_low=2.8, rt_mid=2.4, rt_high=1.3, predelay=.03, length=4.5))
