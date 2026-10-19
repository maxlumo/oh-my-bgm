"""Ember Tango — passion held on a short leash: a bandoneon and a violin trading one theme over a piano and
double bass that drive the 3+3+2 marcato, a lyrical middle where the beat relaxes into four and the violin
sings, then everything back together and the classic two-hit tango ending (V on the last off-beat, i on one).
Feels: intense, elegant, a little dangerous. Scenes: a duel of glances, a night in a port city, a fashion or
dance film, a tense negotiation, a drama's turning point.
A minor, 118 BPM, 38 bars (~1:17).

A | Am | Am/G | F | E7 | Dm | G7 | Cmaj7 | E7b9 |
B | Dm9 | G7 | Cmaj7 | Fmaj7 | Bm7b5 | E7 | Am | A7 |
Form: intro 4 (piano + bass marcato, bandoneon stabs) · A bandoneon · A violin, bandoneon counter-line ·
B violin over "marcato in four" · A everyone · ending 2.
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/tango_nuevo.py   -> ./out/tango_nuevo/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402

from orch import GU_SF, Song, n, nearest  # noqa: E402
from score import P, finish, play, seq  # noqa: E402

BPM, B = 118, 4
V = {"Am": (9, "C4 E4 A4"), "Am/G": (7, "C4 E4 A4"), "F": (5, "C4 F4 A4"), "E7": (4, "D4 G#4 B4"),
     "Dm": (2, "D4 F4 A4"), "G7": (7, "D4 F4 B4"), "Cmaj7": (0, "E4 G4 B4"), "E7b9": (4, "D4 F4 G#4"),
     "Dm9": (2, "C4 F4 E5"), "Fmaj7": (5, "C4 E4 A4"), "Bm7b5": (11, "D4 F4 A4"), "A7": (9, "C#4 G4 E5")}
CA = ["Am", "Am/G", "F", "E7", "Dm", "G7", "Cmaj7", "E7b9"]
CB = ["Dm9", "G7", "Cmaj7", "Fmaj7", "Bm7b5", "E7", "Am", "A7"]
FORM = [("intro", ["Am", "Am", "F", "E7"]), ("A1", CA), ("A2", CA), ("B", CB), ("A3", CA), ("end", ["E7", "Am"])]
BARS = [(sec, c) for sec, chs in FORM for c in chs]
START = {}
for i, (sec, _) in enumerate(BARS):
    START.setdefault(sec, i)
song = Song(bpm=BPM, beats=len(BARS) * B, tail=3.5, seed=118)

THEME = ("A4/.75 C5/.25 E5/.5 A5/1 G#5/.5 A5/1 | B5/.75 A5/.25 G5/.5 E5/1 C5/.5 E5/1 | F5/1.5 E5/.5 D5/1 C5/1 | "
         "B4/.75 D5/.25 G#4/1 E4/2 | D5/.75 F5/.25 A5/.5 D6/1 C6/.5 A5/1 | B5/1.5 A5/.5 G5/1 F5/1 | "
         "E5/1.5 G5/.5 B5/1 A5/1 | G#5/1 F5/1 E5/1 D5/.5 B4/.5")
COUNTER_A = "E4/4 | E4/4 | F4/2 A4/2 | G#4/4 | F4/4 | F4/2 D4/2 | E4/4 | D4/2 F4/2"
SONG_B = "A5/3 G5/.5 F5/.5 | F5/2 E5/1 D5/1 | E5/3 D5/.5 E5/.5 | A5/2 G5/1 E5/1 | D6/2 C6/1 A5/1 | G#5/2 B5/1 D6/1 | C6/3 B5/.5 A5/.5 | G5/1 E5/1 C#5/2"
COUNTER_B = "F4/4 | D4/4 | E4/4 | C4/4 | D4/4 | D4/4 | C4/4 | C#4/4"

bando = P("bandoneon", 23, 17, expr_cc=2, pan=-.2, level=-18, send=-8, bus="lead", jitter_ms=3, legato=-.04,
          eq=[HighpassFilter(150), PeakFilter(1200, -1.5, 1), LowpassFilter(9000)])
violin = P("violin", 40, 17, expr_cc=2, pan=.25, level=-18, send=-6, bus="lead", jitter_ms=4, legato=.03,
           eq=[HighpassFilter(250), PeakFilter(2800, -2.5, 1.2), LowpassFilter(9500)])
piano = P("piano", 0, pan=-.05, width=1.2, level=-20, send=-9, bus="rhythm", jitter_ms=2,
          eq=[HighpassFilter(60), PeakFilter(300, -1.5, 1)])
bass = P("double_bass", 32, sf2=GU_SF, width=.2, level=-20.5, send=-18, bus="rhythm", jitter_ms=3, legato=-.08,
         eq=[HighpassFilter(38), PeakFilter(800, 2, 1)])

for bar, (sec, c) in enumerate(BARS):
    b0 = bar * B
    r, voi = V[c]
    vo = [n(q) for q in voi.split()]
    lo = nearest(r, n("A2"))
    if sec == "end":
        if bar == START["end"]:  # the tango ending: silence, then V on 4&, i on the next downbeat
            for q in vo + [lo, lo - 12]:
                piano.add(b0 + 3.5, .3, q, 112)
            bass.add(b0 + 3.5, .3, lo, 115)
            play(bando, seq("r/3.5 B4+E5+G#5/.4", b0), 110)
            play(violin, seq("r/3.5 B5/.4", b0), 108)
        else:
            for q in vo + [lo, lo - 12]:
                piano.add(b0, .5, q, 118)
            bass.add(b0, .6, lo - 12 if lo - 12 >= n("E1") else lo, 120)
            play(bando, seq("A4+C5+E5/.6", b0), 112)
            play(violin, seq("A5/.6", b0), 112)
        continue
    if sec == "B":  # marcato in four, softer: the beat relaxes under the song
        for k in range(4):
            bass.add(b0 + k, .8, lo if k % 2 == 0 else lo + 7, 80)
            for q in vo:
                piano.add(b0 + k, .6, q, 56 + (8 if k == 0 else 0))
        continue
    # 3+3+2 marcato: bass with a dragged pickup (arrastre) into beat one, piano chords on the accents
    bass.add(b0 - .25, .2, lo - 1, 70)
    for bb, q, v in ((0, lo, 104), (1.5, lo + 7, 92), (3, lo + 12, 96)):
        bass.add(b0 + bb, .6, q, v)
    for bb, v in ((0, 92), (1.5, 82), (3, 86)):
        for q in vo:
            piano.add(b0 + bb, .35, q, v)
        piano.add(b0 + bb, .35, lo - 12 if bb == 0 else lo, v)
    if sec == "intro":
        for bb in (1.5, 3):
            play(bando, [(b0 + bb, .3, q) for q in vo], 96)

play(bando, seq(THEME, START["A1"] * B), 96)
play(violin, seq(THEME, START["A2"] * B), 96)
play(bando, seq(COUNTER_A, START["A2"] * B), 78)
play(violin, seq(SONG_B, START["B"] * B), 98)
play(bando, seq(COUNTER_B, START["B"] * B), 76)
play(bando, seq(THEME, START["A3"] * B), 100)
play(violin, seq(THEME, START["A3"] * B, shift=12), 90)
for nt in list(violin.notes):   # violin slides into its long notes
    if nt.dur >= 1.5:
        violin.add(nt.beat - .12, .14, nt.pitch - 2, nt.vel - 20)

if __name__ == "__main__":
    S = START
    finish("tango_nuevo", [bando, violin, piano, bass], song,
           [("A1", S["A1"], S["A2"]), ("A2", S["A2"], S["B"]), ("B", S["B"], S["A3"]), ("A3", S["A3"], S["end"])],
           lead={"bandoneon", "violin"}, beats_per_bar=B,
           hall=dict(rt_low=1.6, rt_mid=1.4, rt_high=.8, predelay=.018, length=3.0))
