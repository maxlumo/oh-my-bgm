"""Oak & Ale — a Celtic folk band in a warm tavern, 6/8, E dorian. Suits: fantasy taverns and
card games, travel and food videos, cosy autumn vlogs.
Dotted quarter = 72 (written as 8ths at 216 BPM, 6 per bar), 48 bars (~1:20); with --loop a seamless loop.

A  | Em | D | Em | Bm | Em | D | G A | Em |
B  | G | D | A | Em | G | D | A | B7 |
Form: intro 4 (guitar, dulcimer, harp) · A fiddle · A flute, fiddle harmony · B flute, accordion ·
B fiddle, flute harmony · A tutti · outro 4.
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/celtic_tavern.py [--loop]   -> ./out/celtic_tavern/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv  # optional seamless game loop; default: a whole piece with an ending

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter

from orch import GM_SF, GU_SF, SR, Song, n, nearest  # noqa: E402,F401
from score import P, finish, kit, play, seq, swing  # noqa: E402,F401

BPM, B = 216, 6
song = Song(bpm=BPM, beats=48 * B, tail=4.0, seed=72)
Q = {"Em": (4, "m"), "D": (2, "M"), "Bm": (11, "m"), "G": (7, "M"), "A": (9, "M"), "B7": (11, "7")}
CA = [["Em"], ["D"], ["Em"], ["Bm"], ["Em"], ["D"], ["G", "A"], ["Em"]]
CB = [["G"], ["D"], ["A"], ["Em"], ["G"], ["D"], ["A"], ["B7"]]
FORM = [("intro", [["Em"], ["D"], ["Em"], ["B7"]]), ("A1", CA), ("A2", CA), ("B1", CB), ("B2", CB), ("A3", CA),
        ("outro", [["Em"], ["D"], ["G", "A"], ["Em"]])]
BARS = [(sec, chs) for sec, bars in FORM for chs in bars]
DORIAN = [4, 6, 7, 9, 11, 1, 2]

MEL_A = ("E5/2 B4/1 E5/1 F#5/1 G5/1 | F#5/2 D5/1 A4/2 D5/1 | E5/1 F#5/1 G5/1 A5/2 G5/1 | F#5/2 E5/1 D5/2 B4/1 | "
         "E5/2 B4/1 E5/1 F#5/1 G5/1 | A5/2 F#5/1 D5/2 F#5/1 | G5/1 F#5/1 E5/1 C#5/1 D5/1 E5/1 | E5/5 r/1")
MEL_B = ("D5/2 G5/1 B5/2 A5/1 | A5/2 F#5/1 D5/3 | E5/2 A5/1 C#6/2 B5/1 | B5/3 G5/2 E5/1 | "
         "D5/2 G5/1 B5/2 D6/1 | C#6/2 A5/1 F#5/2 A5/1 | G5/1 F#5/1 E5/1 C#5/2 E5/1 | F#5/2 D#5/1 B4/3")


def third_below(p):
    """Diatonic third below in E dorian (chromatic notes drop a minor third)."""
    if p % 12 not in DORIAN:
        return p - 3
    i = DORIAN.index(p % 12)
    q = DORIAN[(i - 2) % 7]
    return p - ((p - q) % 12)


def tones(c):
    r, q = Q[c]
    return [r, (r + (3 if q == "m" else 4)) % 12, (r + 7) % 12] + ([(r + 10) % 12] if q == "7" else [])


fiddle = P("fiddle", 110, 17, expr_cc=2, pan=-.15, level=-17.5, send=-8, bus="lead", jitter_ms=5, legato=-.05,
           eq=[HighpassFilter(250), PeakFilter(2800, -2.5, 1.2), LowpassFilter(9000)])
flute = P("flute", 73, 17, expr_cc=2, pan=.2, level=-18, send=-8, bus="lead", jitter_ms=5, legato=-.05,
          eq=[HighpassFilter(300), LowpassFilter(10000)])
harm = P("fiddle_harmony", 110, 17, expr_cc=2, pan=-.35, level=-24, send=-7, bus="lead", jitter_ms=6, legato=-.05,
         eq=[HighpassFilter(250), PeakFilter(2800, -3, 1.2), LowpassFilter(8000)])
fl_harm = P("flute_harmony", 73, 17, expr_cc=2, pan=.35, level=-24, send=-7, bus="lead", jitter_ms=6,
            eq=[HighpassFilter(300)])
guitar = P("guitar", 24, sf2=GU_SF, pan=-.3, width=1.2, level=-21, send=-12, bus="band", jitter_ms=4,
           eq=[HighpassFilter(90), PeakFilter(250, -2, 1)])
dulcimer = P("dulcimer", 15, pan=.35, width=1.2, level=-24, send=-9, bus="band", jitter_ms=4,
             eq=[HighpassFilter(250)])
accordion = P("accordion", 21, 17, expr_cc=2, pan=.1, width=1.2, level=-25, send=-8, bus="band", legato=-.1,
              eq=[HighpassFilter(200), PeakFilter(1200, -2, 1), LowpassFilter(7000)])
harp = P("harp", 46, pan=.25, width=1.3, level=-23, send=-8, bus="band", jitter_ms=4, eq=[HighpassFilter(120)])
bass = P("bass", 32, sf2=GU_SF, width=.2, level=-22, send=-26, bus="bass", jitter_ms=5, legato=-.3,
         eq=[HighpassFilter(40), PeakFilter(700, 2, 1)])
bodhran = kit("bodhran", 0, width=1.0, level=-26, send=-12, bus="drums", jitter_ms=5,
              eq=[HighpassFilter(45), LowpassFilter(5000)])
tamb = kit("tambourine", 0, pan=.4, level=-31, send=-10, bus="drums", jitter_ms=5, eq=[HighpassFilter(800)])
DUM, TEK, TEK2, TAMB = 41, 45, 47, 54

for bar, (sec, chs) in enumerate(BARS):
    b0 = bar * B
    half = B // len(chs)
    for ci, c in enumerate(chs):
        cb = b0 + ci * half
        ts = tones(c)
        lo = nearest(ts[0], n("E2"))
        shape = sorted({nearest(ts[1], n("G3")), nearest(ts[2], n("B3")), nearest(ts[0], n("E4"))})
        # guitar boom-chick-chick (strings spread)
        for k in range(half):
            if k % 3 == 0:
                guitar.add(cb + k, 1.2, lo if k == 0 else nearest(ts[2], lo + 7), 82)
            else:
                for j, q in enumerate(shape):
                    guitar.add(cb + k + j * .06, .8, q, 62 - j * 2 + (4 if k % 3 == 1 else 0))
        if sec not in ("intro", "outro"):
            bass.add(cb, 2.6, lo, 92)
            if half == 6:
                bass.add(cb + 3, 2.6, nearest(ts[2], lo + 7), 80)
        # dulcimer arpeggio
        if sec in ("intro", "A1", "B1", "outro"):
            arp = [ts[0], ts[2], ts[0], ts[1], ts[0], ts[2]]
            for k in range(half):
                q = nearest(arp[k], n("E5") if k in (2, 3) else n("B4"))
                dulcimer.add(cb + k, 1.0, q, 70 + (8 if k % 3 == 0 else 0))
        if sec in ("B1", "B2", "A3"):
            for q in shape:
                accordion.add(cb, half, q + 12, 72 if sec != "A3" else 70)
        if sec in ("intro", "outro", "A3"):
            for k, q in enumerate([ts[0], ts[2], ts[1], ts[0]]):
                harp.add(cb + k * .5, 2.5, nearest(q, n("E3") + k * 5), 70)
    # bodhran: dum on 1 and 4, ghost tek on the rest
    if sec not in ("intro", "outro"):
        for k, (note, v) in enumerate([(DUM, 92), (TEK, 48), (TEK2, 56), (DUM, 78), (TEK, 48), (TEK2, 64)]):
            bodhran.add(b0 + k, .3, note, v)
        if sec in ("B2", "A3"):
            for k in (1, 2, 4, 5):
                tamb.add(b0 + k, .3, TAMB, 54 + (10 if k in (2, 5) else 0))

play(fiddle, seq(MEL_A, 4 * B), 92)
play(flute, seq(MEL_A, 12 * B), 90)
play(harm, [(b, d, third_below(p)) for b, d, p in seq(MEL_A, 12 * B)], 78)
play(flute, seq(MEL_B, 20 * B), 92)
play(fiddle, seq(MEL_B, 28 * B), 94)
play(fl_harm, [(b, d, p + 12) for b, d, p in seq(MEL_B, 28 * B) if b % 3 == 0], 72)  # sparse flute 8va
play(fiddle, seq(MEL_A, 36 * B), 88)
play(flute, seq(MEL_A, 36 * B, shift=12), 64)
play(flute, seq("E5/2 B4/1 E5/1 F#5/1 G5/1 | F#5/2 D5/1 A4/3 | r/6 | E5/6", 44 * B), 76)

if __name__ == "__main__":
    finish("celtic_tavern", [fiddle, flute, harm, fl_harm, guitar, dulcimer, accordion, harp, bass, bodhran, tamb], song,
           [("intro", 0, 4), ("A1", 4, 12), ("A2", 12, 20), ("B1", 20, 28), ("B2", 28, 36), ("A3", 36, 44)],
           lead={"fiddle", "flute", "fiddle_harmony", "flute_harmony"}, beats_per_bar=B, loop=LOOP,
           hall=dict(rt_low=1.3, rt_mid=1.1, rt_high=.7, predelay=.012, length=2.8))
