"""Afternoon — happy without being childish: a bossa nova trio with flute. Nylon guitar in the
syncopated bossa comp, upright bass on root and fifth, cross-stick clave and shaker, Rhodes pads, flute tune,
vibes for the middle. Suits: lifestyle and food vlogs, cafés, travel, light product videos, weekend moods.
F major, 128 BPM (felt in 2), 40 bars (~1:15); with --loop a seamless loop (drops the ending).

A  | Fmaj7 | Bb9 | Am7 | D7b9 | Gm9 | C13 | Fmaj7 | Gm7 C7 |
B  | Bbmaj7 | Bbm6 | Am7 | D7b9 | Gm7 | C7sus | Fmaj7 | Gm7 C7 |
Form: intro 4 (guitar, percussion) · A flute · A flute, Rhodes · B vibes · A flute + vibes · ending 4.
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/bossa_afternoon.py [--loop]   -> ./out/bossa_afternoon/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402

from orch import GU_SF, Song, n, nearest  # noqa: E402
from score import P, finish, kit, play, seq  # noqa: E402

BPM, B = 128, 4
NB = 36 if LOOP else 40
song = Song(bpm=BPM, beats=NB * B, tail=3.5, seed=128)
# chord -> (root pc, guitar voicing)
V = {"Fmaj7": (5, "F3 A3 C4 E4"), "Bb9": (10, "Ab3 C4 D4 F4"), "Am7": (9, "G3 C4 E4"), "D7b9": (2, "F#3 C4 Eb4"),
     "Gm9": (7, "F3 Bb3 D4 A4"), "C13": (0, "E3 Bb3 D4 A4"), "Gm7": (7, "F3 Bb3 D4"), "C7": (0, "E3 Bb3 G3"),
     "Bbmaj7": (10, "F3 A3 D4"), "Bbm6": (10, "F3 G3 Db4"), "C7sus": (0, "F3 Bb3 G3"), "Fmaj9": (5, "E3 A3 C4 G4")}
CA = [["Fmaj7"], ["Bb9"], ["Am7"], ["D7b9"], ["Gm9"], ["C13"], ["Fmaj7"], ["Gm7", "C7"]]
CB = [["Bbmaj7"], ["Bbm6"], ["Am7"], ["D7b9"], ["Gm7"], ["C7sus"], ["Fmaj7"], ["Gm7", "C7"]]
FORM = [("intro", CA[:4]), ("A1", CA), ("A2", CA), ("B", CB), ("A3", CA)] + \
       ([] if LOOP else [("end", [["Fmaj7"], ["Bb9"], ["Fmaj9"], ["Fmaj9"]])])
BARS = [(sec, chs) for sec, bars in FORM for chs in bars]

FLUTE_A = ("r/.5 C5/.5 E5/.5 A5/1.5 G5/1 | F5/2.5 D5/.5 C5/1 | E5/1.5 G5/.5 C6/1.5 B5/.5 | A5/2 Eb5/1 F#5/1 | "
           "A5/1.5 Bb5/.5 A5/1 F5/1 | E5/2 r/.5 D5/.5 A5/1 | G5/3 F5/1 | D5/1 F5/1 E5/2")
VIBES_B = ("D5/1.5 F5/.5 A5/2 | Db5/1.5 F5/.5 G5/2 | C5/1 E5/1 G5/2 | F#5/1.5 Eb5/.5 C5/2 | "
           "Bb4/1 D5/1 F5/1.5 A5/.5 | G5/2 F5/2 | E5/4 | r/1 D5/1 C5/1 Bb4/1")

flute = P("flute", 73, 17, expr_cc=2, pan=.15, level=-17.5, send=-8, bus="lead", jitter_ms=5, legato=-.04,
          eq=[HighpassFilter(300), LowpassFilter(10000)])
vibes = P("vibes", 11, 11, sf2=GU_SF, pan=-.2, level=-19.5, send=-8, bus="lead", jitter_ms=4, eq=[HighpassFilter(250)])
guitar = P("nylon_guitar", 24, sf2=GU_SF, pan=-.25, width=1.2, level=-20, send=-11, bus="band", jitter_ms=5,
           eq=[HighpassFilter(90), PeakFilter(250, -2, 1)])
rhodes = P("rhodes", 4, pan=.3, width=1.3, level=-27, send=-10, bus="band", legato=.1,
           eq=[HighpassFilter(150), PeakFilter(450, -2, 1)])
bass = P("upright", 32, sf2=GU_SF, width=.2, level=-22, send=-24, bus="bass", jitter_ms=5, legato=-.1,
         eq=[HighpassFilter(40), PeakFilter(700, 2, 1)])
perc = kit("perc", 0, width=1.3, level=-26, send=-12, bus="perc", jitter_ms=5, eq=[HighpassFilter(45)])
KICK, XSTICK, SHAKER = 36, 37, 70
COMP = ([(0, .45), (1.5, .45), (3, .7)], [(1, .45), (2.5, 1.2)])   # two-bar bossa comp
CLAVE = ([0, 1.5, 3], [1, 2.5])

for bar, (sec, chs) in enumerate(BARS):
    span = B / len(chs)
    for ci, c in enumerate(chs):
        b0 = bar * B + ci * span
        r, voi = V[c]
        vo = [n(q) for q in voi.split()]
        lo = nearest(r, n("F2"))
        if sec == "end" and bar >= len(BARS) - 2:
            if bar == len(BARS) - 2:
                for k, q in enumerate([lo] + vo):
                    guitar.add(b0 + k * .05, 2 * B, q, 72 - k * 2)
                bass.add(b0, 2 * B, lo, 80)
                play(rhodes, [(b0, 2 * B, q) for q in vo[:3]], 64)
            continue
        # guitar: thumb on 1 and 3 (root, fifth), fingers on the bossa syncopation
        for bb, q in ((0, lo), (2, lo + 7)):
            if bb < span:
                guitar.add(b0 + bb, 1.5, q, 78)
        cells = COMP[bar % 2] if span == 4 else [(.5, .4), (1.5, .45)]
        for bb, d in cells:
            for j, q in enumerate(vo):
                guitar.add(b0 + bb + j * .015, d, q, 62)
        if sec != "intro":
            for bb, d, q, v in ((0, 1.4, lo, 88), (1.5, .45, lo + 7, 70), (2, 1.4, lo + 7, 80), (3.5, .45, lo, 70)):
                if bb < span:
                    bass.add(b0 + bb, min(d, span - bb), q, v)
        if sec in ("A2", "B", "A3"):
            for q in vo[:3]:
                rhodes.add(b0, span, q, 58)  # under the tune: no 9th-against-3rd seconds
    b0 = bar * B
    if sec != "end" or bar < len(BARS) - 2:
        for bb in CLAVE[bar % 2]:
            perc.add(b0 + bb, .2, XSTICK, 70)
        for k in range(8):
            perc.add(b0 + k * .5, .2, SHAKER, 46 + (16 if k % 2 else 0))
        if sec != "intro":
            for bb, v in ((0, 66), (1.5, 50), (2, 62), (3.5, 50)):
                perc.add(b0 + bb, .2, KICK, v)

play(flute, seq(FLUTE_A, 4 * B), 86)
play(flute, seq(FLUTE_A, 12 * B), 90)
play(vibes, seq(VIBES_B, 20 * B), 92)
play(flute, seq(FLUTE_A, 28 * B), 92)
play(vibes, seq(FLUTE_A, 28 * B, shift=-12), 62)
if not LOOP:
    play(flute, seq("r/.5 C5/.5 E5/.5 A5/1.5 G5/1 | F5/2.5 D5/.5 C5/1 | A5/8", 36 * B), 84)

if __name__ == "__main__":
    finish("bossa_afternoon", [flute, vibes, guitar, rhodes, bass, perc], song,
           [("intro", 0, 4), ("A1", 4, 12), ("A2", 12, 20), ("B", 20, 28), ("A3", 28, 36)],
           lead={"flute", "vibes"}, beats_per_bar=B, loop=LOOP,
           hall=dict(rt_low=1.3, rt_mid=1.1, rt_high=.7, predelay=.015, length=2.6))
