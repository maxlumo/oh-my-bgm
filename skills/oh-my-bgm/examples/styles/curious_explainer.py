"""Curiosity — light, bright and grown-up, made to sit under a narrator: a bouncing piano ostinato on
major-7th and Lydian colours, pizzicato off-beats, a clarinet that asks short questions with rests between them.
Suits: science / tech explainers, knowledge videos, product walkthroughs, tutorials.
D major, 104 BPM, 38 bars (~1:28); with --loop a seamless loop (drop the 2-bar ending).

A  | Dmaj7 | Bm9 | Gmaj7#11 | Asus4 A | D/F# | Gmaj9 | Em9 | A7sus4 |
B  | Bm9 | Gmaj7 | D/F# | Em9 | Bm9 | Gmaj7 | Em9 | Asus4 A |
Form: intro 4 (piano) · A clarinet questions, pizz, shaker · A vibes takes the questions, clarinet long notes ·
B vibes tune over a string pad · A clarinet + vibes, everyone · ending 2 (Dmaj9).
Under a voice: render as is and duck it in the video mix; the tune is sparse on purpose.
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/curious_explainer.py [--loop]   -> ./out/curious_explainer/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv  # optional seamless loop; default: a whole piece with an ending

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402

from orch import GU_SF, Song, n, nearest  # noqa: E402
from score import P, finish, kit, play, seq  # noqa: E402

BPM, B = 104, 4
NBARS = 36 if LOOP else 38
song = Song(bpm=BPM, beats=NBARS * B, tail=3.5, seed=104)
# chord -> (bass pc, upper chord tones as pcs)
CH = {"Dmaj7": (2, [6, 9, 1, 4]), "Bm9": (11, [2, 6, 9, 1]), "Gmaj7#11": (7, [11, 2, 6, 1]), "Asus4": (9, [2, 4, 9, 7]),
      "A": (9, [1, 4, 9, 7]), "D/F#": (6, [9, 2, 6, 4]), "Gmaj9": (7, [11, 2, 6, 9]), "Em9": (4, [7, 11, 2, 6]),
      "A7sus4": (9, [2, 4, 7, 11]), "Gmaj7": (7, [11, 2, 6, 7]), "Dmaj9": (2, [6, 9, 1, 4])}
PADV = {"Dmaj7": "F#3 A3 D4", "Bm9": "D4 F#4 B4", "Gmaj7#11": "B3 D4 G4", "Asus4": "A3 D4 E4", "A": "A3 C#4 E4",
        "D/F#": "A3 D4 F#4", "Gmaj9": "B3 D4 G4", "Em9": "G3 B3 E4", "A7sus4": "A3 D4 E4", "Gmaj7": "B3 D4 G4"}  # triads
CA = [["Dmaj7"], ["Bm9"], ["Gmaj7#11"], ["Asus4", "A"], ["D/F#"], ["Gmaj9"], ["Em9"], ["A7sus4"]]
CB = [["Bm9"], ["Gmaj7"], ["D/F#"], ["Em9"], ["Bm9"], ["Gmaj7"], ["Em9"], ["Asus4", "A"]]
FORM = [("intro", CA[:4]), ("A1", CA), ("A2", CA), ("B", CB), ("A3", CA)] + ([] if LOOP else [("end", [["Dmaj9"], ["Dmaj9"]])])
BARS = [(sec, chs) for sec, bars in FORM for chs in bars]

QUESTIONS = ("r/1 A4/.5 B4/.5 D5/1 r/1 | r/2 C#5/.5 D5/.5 F#5/1 | r/1 B4/.5 C#5/.5 D5/1.5 F#5/.5 | E5/2 r/1 C#5/1 | "
             "r/1 A4/.5 B4/.5 D5/1 r/1 | r/2 F#5/.5 A5/.5 B5/1 | G5/1 F#5/.5 E5/.5 D5/1 B4/1 | D5/2 r/2")
LONG = "F#4/4 | D4/4 | B3/4 | E4/4 | F#4/4 | D4/4 | B3/4 | E4/4"
VIBES_B = ("F#5/1.5 E5/.5 D5/1 C#5/1 | B4/2 F#5/2 | A5/1.5 G5/.5 F#5/2 | E5/1 G5/1 B5/2 | "
           "D6/1.5 C#6/.5 B5/1 F#5/1 | A5/2 F#5/1 D5/1 | E5/1.5 F#5/.5 G5/1 B5/1 | A5/2 C#5/2")

piano = P("piano", 0, 8, pan=-.1, width=1.2, level=-19, send=-10, bus="keys", jitter_ms=4,
          eq=[HighpassFilter(90), PeakFilter(350, -2, 1), PeakFilter(3000, 1, 1)])
clar = P("clarinet", 71, 17, expr_cc=2, pan=-.25, level=-19, send=-8, bus="lead", jitter_ms=4, legato=-.05,
         eq=[HighpassFilter(180)])
vibes = P("vibes", 11, pan=.25, level=-19, send=-8, bus="lead", jitter_ms=3, eq=[HighpassFilter(250)])
pizz = P("pizz", 45, players=2, pan=.35, width=1.3, level=-25, send=-8, bus="strings", jitter_ms=4,
         eq=[HighpassFilter(120)])
pad = P("strings", 49, 17, expr_cc=2, players=2, pan=0, width=1.6, level=-26, send=-5, bus="strings", legato=.2,
        eq=[HighpassFilter(200), PeakFilter(2800, -2, 1)])
bass = P("bass", 32, sf2=GU_SF, width=.2, level=-23, send=-24, bus="bass", jitter_ms=4, legato=-.1,
         eq=[HighpassFilter(40), PeakFilter(700, 2, 1)])
perc = kit("perc", 0, width=1.3, level=-27, send=-14, bus="drums", jitter_ms=4, eq=[HighpassFilter(40)])
KICK, RIM, SHAKER = 36, 37, 70

for bar, (sec, chs) in enumerate(BARS):
    span = B / len(chs)
    for ci, c in enumerate(chs):
        b0 = bar * B + ci * span
        bpc, pcs = CH[c]
        tones = sorted(nearest(p, n("C5")) for p in pcs)
        lo = nearest(bpc, n("D2"))
        if sec == "end":  # a rolled Dmaj9 held for both bars
            if bar == len(BARS) - 2:
                for k, q in enumerate([lo, lo + 12] + tones):
                    piano.add(b0 + k * .12, 2 * B - k * .12, q, 60 - k * 2)
                bass.add(b0, 2 * B, lo, 84)
                play(pad, [(b0, 2 * B, q) for q in (n("F#4"), n("A4"), n("E5"))], 70)
            continue
        pat = [0, 1, 2, 1, 0, 3, 2, 1]
        for k in range(int(span * 2)):
            piano.add(b0 + k * .5, min(.9, span - k * .5), tones[pat[k]], (60 if k % 2 == 0 else 50) + (6 if k == 0 else 0))
        piano.add(b0, span, lo + 12, 56)
        if sec != "intro":
            bass.add(b0, 1.4, lo, 90)
            if span == 4:
                bass.add(b0 + 2.5, 1.2, lo + 12, 74)  # octave: a fifth above a slash bass would be wrong
            for k in (1.5, 3.5) if span == 4 else (1.5,):
                for q in tones[:2]:
                    pizz.add(b0 + k, .3, q - 12, 70)
        if sec in ("B", "A3"):
            for q in PADV[c].split():
                pad.add(b0, span, q, 66 if sec == "B" else 60)
    if sec in ("A1", "A2", "B", "A3"):
        b0 = bar * B
        for k in range(16):
            perc.add(b0 + k * .25, .1, SHAKER, 44 + (16 if k % 4 == 2 else 0))
        perc.add(b0, .2, KICK, 70)
        perc.add(b0 + 2.5, .2, KICK, 58)
        if sec != "A1":
            perc.add(b0 + 3, .2, RIM, 60)

play(clar, seq(QUESTIONS, 4 * B), 88)
play(vibes, seq(QUESTIONS, 12 * B), 92)
play(clar, seq(LONG, 12 * B), 70)
play(vibes, seq(VIBES_B, 20 * B), 108)
play(clar, seq(QUESTIONS, 28 * B), 90)
play(vibes, seq(QUESTIONS, 28 * B, shift=12), 70)
if not LOOP:
    play(clar, seq("r/1 A4/.5 B4/.5 E5/2 | F#5/4", 36 * B), 82)
    play(vibes, seq("r/4 | r/1 F#6/3", 36 * B), 66)

if __name__ == "__main__":
    finish("curious_explainer", [piano, clar, vibes, pizz, pad, bass, perc], song,
           [("intro", 0, 4), ("A1", 4, 12), ("A2", 12, 20), ("B", 20, 28), ("A3", 28, 36)],
           lead={"clarinet", "vibes"}, beats_per_bar=B, loop=LOOP,
           hall=dict(rt_low=1.5, rt_mid=1.3, rt_high=.8, predelay=.02, length=3.0))
