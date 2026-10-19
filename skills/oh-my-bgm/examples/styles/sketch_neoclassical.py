"""Sketch — modern neo-classical for art-house and humanities films: a soft, close-miked piano repeating
a broken-chord figure, a string quartet that joins one voice at a time, a borrowed minor iv (Dbm6) for the
bittersweet turn. Very few notes; the space is the style.
Suits: art / culture / humanities videos, interviews, poetry, slow travel, brand films about craft.
Ab major, 70 BPM, 34 bars (~1:56); with --loop a seamless loop (drops the ending).

| Ab | Fm7 | Dbmaj9 | Ebsus4 Eb | Ab/C | Fm7 | Dbm6 | Eb7sus4 |
Form: piano 4 · + cello 8 · + violin tune, viola 8 · everyone 8 (violin + viola in sixths, cello bass line) ·
piano and violin 4 · ending 2 (Ab add9).
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/sketch_neoclassical.py [--loop]   -> ./out/sketch_neoclassical/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402

from orch import Song, n, nearest  # noqa: E402
from score import P, finish, play, seq  # noqa: E402

BPM, B = 70, 4
song = Song(bpm=BPM, beats=(32 if LOOP else 34) * B, tail=6.0, seed=70)
# chord -> (bass pc, piano figure pcs low -> high)
CH = {"Ab": (8, [0, 3, 8, 10]), "Fm7": (5, [0, 3, 5, 8]), "Dbmaj9": (1, [5, 8, 0, 3]), "Ebsus4": (3, [8, 10, 3, 5]),
      "Eb": (3, [7, 10, 3, 5]), "Ab/C": (0, [3, 8, 0, 10]), "Dbm6": (1, [4, 8, 10, 1]), "Eb7sus4": (3, [8, 10, 1, 5])}
PROG = [["Ab"], ["Fm7"], ["Dbmaj9"], ["Ebsus4", "Eb"], ["Ab/C"], ["Fm7"], ["Dbm6"], ["Eb7sus4"]]
FORM = [("piano", PROG[:4]), ("cello", PROG), ("violin", PROG), ("all", PROG), ("thin", PROG[:4])] + \
       ([] if LOOP else [("end", [["Ab"], ["Ab"]])])
BARS = [(sec, chs) for sec, bars in FORM for chs in bars]

TUNE = "C5/3 Eb5/1 | Ab5/2 G5/1 F5/1 | F5/4 | Bb4/2 G4/2 | C5/2 Eb5/2 | F5/2 Ab5/1 G5/1 | E5/2 Db5/2 | Db5/2 Bb4/2"
SIXTHS = "Eb4/3 G4/1 | C5/2 Bb4/1 Ab4/1 | Ab4/4 | Eb4/2 Eb4/2 | Eb4/2 G4/2 | Ab4/2 C5/1 Bb4/1 | Ab4/2 E4/2 | F4/2 Eb4/2"
CELLO_LONG = "Ab3/4 | C4/4 | Db4/4 | Bb3/4 | Eb3/4 | Ab3/4 | E3/4 | Db3/2 Bb2/2"
CELLO_BASS = "Ab2/4 | F2/4 | Db2/4 | Eb2/4 | C3/4 | F2/4 | Db2/4 | Eb2/4"

piano = P("felt_piano", 0, 8, pan=0, width=1.1, level=-18, send=-5, bus="piano", jitter_ms=8,
          eq=[HighpassFilter(70), PeakFilter(300, -1, 1), LowpassFilter(4200), PeakFilter(1800, 1.5, 1)])
violin = P("violin", 40, 17, expr_cc=2, pan=-.3, level=-17.5, send=-4, bus="strings", jitter_ms=6, legato=.12,
           eq=[HighpassFilter(280), PeakFilter(2800, -3, 1.2), LowpassFilter(8500)])
viola = P("viola", 41, 17, expr_cc=2, pan=.15, level=-22, send=-4, bus="strings", jitter_ms=6, legato=.12,
          eq=[HighpassFilter(180), PeakFilter(2500, -2, 1)])
cello = P("cello", 42, 17, expr_cc=2, pan=.35, level=-20, send=-4, bus="strings", jitter_ms=6, legato=.12,
          eq=[HighpassFilter(60), PeakFilter(300, -1.5, 1), LowpassFilter(7000)])

for bar, (sec, chs) in enumerate(BARS):
    span = B / len(chs)
    for ci, c in enumerate(chs):
        b0 = bar * B + ci * span
        bpc, pcs = CH[c]
        lo = nearest(bpc, n("Ab2"))
        fig, prev = [], n("C4") - 1
        for p in pcs:  # stack the figure upwards from middle C
            prev = prev + 1 + (p - prev - 1) % 12
            fig.append(prev)
        if sec == "end":
            if bar == len(BARS) - 2:
                for k, q in enumerate([lo, lo + 7] + fig):
                    piano.add(b0 + k * .3, 2 * B - k * .3, q, 50 - k * 2)
                play(violin, [(b0, 2 * B, n("C5"))], 66)
                play(cello, [(b0, 2 * B, n("Ab2"))], 66)
            continue
        piano.add(b0, span, lo, 48)
        order = [0, 2, 1, 3, 2, 1, 3, 2]
        for k in range(int(span * 2)):
            piano.add(b0 + k * .5, min(1.2, span - k * .5), fig[order[k]], 44 + (6 if k % 4 == 0 else 0))

play(cello, seq(CELLO_LONG, 4 * B), 76)
play(violin, seq(TUNE, 12 * B), 84)
play(viola, seq(CELLO_LONG, 12 * B), 66)
play(violin, seq(TUNE, 20 * B, shift=12), 90)
play(viola, seq(SIXTHS, 20 * B, shift=12), 76)
play(cello, seq(CELLO_BASS, 20 * B), 80)
play(violin, seq(TUNE, 28 * B)[:7], 74)

if __name__ == "__main__":
    finish("sketch_neoclassical", [piano, violin, viola, cello], song,
           [("piano", 0, 4), ("cello", 4, 12), ("violin", 12, 20), ("all", 20, 28), ("thin", 28, 32)],
           lead={"violin"}, beats_per_bar=B, loop=LOOP,
           hall=dict(rt_low=2.4, rt_mid=2.1, rt_high=1.1, predelay=.025, length=4.0))
