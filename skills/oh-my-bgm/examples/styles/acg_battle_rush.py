"""Gale — ACG battle BGM: orchestral rock at full tilt. 16th-note string ostinato, horn tune over
i - VI - VII - V, palm-muted power chords low in the mix, rock kit, piano octaves, then choir and brass for the
chorus and a three-hit ending. Suits: anime / game battles and boss fights, sports highlights, action trailers.
D minor, 168 BPM, 48 bars (~1:11); with --loop a seamless loop (drops the ending hits).

A | Dm | Bb | C | A | Dm | Bb | Gm | A |
C | Bb | C | Dm | Dm | Bb | C | A | A |
Form: intro 4 (strings ostinato, toms) · A horns · B strings tune an octave up, guitar · A horns + violins ·
C choir + brass · C again, highest · ending 4 (Bb C Dm hits).
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/acg_battle_rush.py [--loop]   -> ./out/acg_battle_rush/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv

from pedalboard import Distortion, HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402

import hybrid as hy  # noqa: E402
from orch import GU_SF, Song, n, nearest  # noqa: E402
from score import P, finish, kit, play, seq  # noqa: E402

BPM, B = 168, 4
Q = {"Dm": (2, 3), "Bb": (10, 4), "C": (0, 4), "A": (9, 4), "Gm": (7, 3)}
CA = ["Dm", "Bb", "C", "A", "Dm", "Bb", "Gm", "A"]
CC = ["Bb", "C", "Dm", "Dm", "Bb", "C", "A", "A"]
FORM = [("intro", ["Dm", "Dm", "Bb", "A"]), ("A1", CA), ("B", CA), ("A2", CA), ("C1", CC), ("C2", CC)] + \
       ([] if LOOP else [("end", ["Dm"] * 4)])
BARS = [(sec, c) for sec, chs in FORM for c in chs]
START = {}
for i, (sec, _) in enumerate(BARS):
    START.setdefault(sec, i)
song = Song(bpm=BPM, beats=len(BARS) * B, tail=3.0, seed=168)

TUNE_A = ("D5/1.5 A4/.5 D5/1 E5/1 | F5/2 D5/1 Bb4/1 | E5/1.5 C5/.5 G5/2 | E5/2 C#5/2 | "
          "D5/1.5 A4/.5 D5/1 F5/1 | G5/2 F5/1 D5/1 | Bb5/2 G5/1 D5/1 | E5/1 C#5/1 A4/2")
TUNE_C = "D5/1 F5/1 Bb5/2 | C6/1.5 Bb5/.5 G5/2 | A5/3 F5/1 | E5/1 F5/1 A5/2 | Bb5/1.5 A5/.5 F5/2 | G5/1.5 A5/.5 C6/2 | C#6/3 A5/1 | A5/4"

horns = P("horns", 60, 17, expr_cc=2, players=2, pan=-.25, width=1.2, level=-15, send=-6, bus="brass", legato=-.03,
          eq=[HighpassFilter(100), LowpassFilter(6500)])
brass = P("brass", 61, 17, expr_cc=2, players=2, pan=.25, width=1.3, level=-20, send=-6, bus="brass", legato=-.03,
          eq=[HighpassFilter(120), PeakFilter(2500, -2, 1)])
violins = P("violins", 48, 21, expr_cc=2, players=2, pan=-.4, width=1.3, level=-17, send=-5, bus="strings",
            legato=-.02, eq=[HighpassFilter(250), PeakFilter(3000, -2.5, 1)])
ostinato = P("ostinato", 48, players=3, pan=.2, width=1.5, level=-22.5, send=-7, bus="strings", jitter_ms=3,
             legato=-.06, eq=[HighpassFilter(90), PeakFilter(300, -2, 1), PeakFilter(2800, -2, 1)])
choir = P("choir", 52, 17, expr_cc=2, players=2, pan=0, width=1.6, level=-22, send=-3, bus="choir", legato=.1,
          eq=[HighpassFilter(200), PeakFilter(2500, -2, 1)])
piano = P("piano", 0, pan=.1, width=1.2, level=-23, send=-9, bus="keys", jitter_ms=2, eq=[HighpassFilter(80)])
guitar = P("guitar", 30, sf2=GU_SF, players=2, pan=0, width=1.6, level=-27, send=-16, bus="guitar", jitter_ms=3,
           eq=[HighpassFilter(110), PeakFilter(400, -3, 1), LowpassFilter(5500)])
bass = P("bass", 34, sf2=GU_SF, width=.2, level=-21, send=-30, bus="bass", jitter_ms=2, legato=-.05,
         eq=[HighpassFilter(40), Distortion(drive_db=4), LowpassFilter(3500)])
drums = kit("drums", 16, width=1.3, level=-19, send=-12, bus="drums", jitter_ms=2,
            eq=[HighpassFilter(40), HighpassFilter(40)])
timp = P("timpani", 47, pan=-.1, level=-24, send=-7, bus="drums", roll=.125, eq=[HighpassFilter(40)])
KICK, SNARE, HHC, CRASH, RIDE, TOMS = 36, 38, 42, 49, 51, (41, 45, 48)
ENERGY = {"intro": 0, "A1": 1, "B": 2, "A2": 2, "C1": 3, "C2": 4, "end": 4}

for bar, (sec, c) in enumerate(BARS):
    b0 = bar * B
    r, third = Q[c]
    lo = nearest(r, n("D3"))
    E = ENERGY[sec]
    if sec == "end":
        continue
    # 16th ostinato: root root octave root fifth root third root (accents on the 3+3+2 grouping)
    shape = [0, 0, 12, 0, 7, 0, third, 0]
    for k in range(16):
        ostinato.add(b0 + k * .25, .2, lo + shape[k % 8] - (12 if E < 2 else 0), 70 + (22 if k % 8 in (0, 3, 6) else 0))
    bass.add(b0, .45, lo - 12, 100)
    for k in range(1, 8):
        bass.add(b0 + k * .5, .4, lo - 12 + (12 if k == 3 and E >= 2 else 0), 86)
    if E >= 2:  # palm-muted power chords in 8ths
        for k in range(8):
            for q in (lo - 12, lo - 5, lo):
                guitar.add(b0 + k * .5, .3 if k % 4 else .45, q, 84 if k % 4 == 0 else 70)
    if E >= 3:
        for q in (nearest(r, n("D4")), nearest((r + third) % 12, n("F4")), nearest((r + 7) % 12, n("A4"))):
            choir.add(b0, B, q, 70 + E * 6)
            brass.add(b0, .9, q, 90)
            brass.add(b0 + 2.5, 1.4, q, 96)
    if sec == "intro" or E >= 3:
        piano.add(b0, 1, lo - 12, 96)
        piano.add(b0, 1, lo, 90)
        piano.add(b0 + 1.5, .5, lo, 80)
    # drums
    if sec == "intro":
        for k, v in [(0, 100), (1.5, 86), (2, 92), (3, 96), (3.5, 100)]:
            drums.add(b0 + k, .3, TOMS[0], v)
    else:
        for k in ((0, 1.5, 2.5) if E < 3 else (0, .5, 1.5, 2, 2.5)):
            drums.add(b0 + k, .2, KICK, 110)
        for k in (1, 3):
            drums.add(b0 + k, .2, SNARE, 112)
        for k in range(8):
            drums.add(b0 + k * .5, .1, RIDE if E >= 3 else HHC, 76 if k % 2 == 0 else 58)
        if (bar - START[sec]) % 8 == 7:  # fill
            for j in range(8):
                drums.add(b0 + 2 + j * .25, .2, TOMS[2 - j // 3] if j < 6 else SNARE, 90 + j * 3)
    if bar == START[sec]:
        drums.add(b0, 2, CRASH, 110)
        timp.add(b0, .9, nearest(r, n("D2")), 100)

play(horns, seq(TUNE_A, START["A1"] * B), 96)
play(violins, seq(TUNE_A, START["B"] * B, shift=12), 98)
play(horns, seq(TUNE_A, START["A2"] * B), 104)
play(violins, seq(TUNE_A, START["A2"] * B, shift=12), 88)
play(horns, seq(TUNE_C, START["C1"] * B), 108)
play(violins, seq(TUNE_C, START["C1"] * B), 92)
play(horns, seq(TUNE_C, START["C2"] * B), 112)
play(violins, seq(TUNE_C, START["C2"] * B, shift=12), 100)

fx = hy.Layer(song.length)
for sec in ("C1", "C2"):
    fx.at(song.t(START[sec] * B), hy.riser(2.5, seed=START[sec]), end=True, gain=.5)
if not LOOP:  # ending: Bb on 1, C on 2&, Dm on 4 ... and one last Dm
    e = START["end"] * B
    for at, c, length in ((0, "Bb", .8), (1.5, "C", .8), (3, "Dm", .8), (4, "Dm", 6)):
        r, third = Q[c]
        lo = nearest(r, n("D3"))
        for q in (lo, lo + third, lo + 7, lo + 12):
            brass.add(e + at, length, q, 112)
            horns.add(e + at, length, q + 12 if q < n("F4") else q, 108)
            violins.add(e + at, length, q + 12, 106)
        for q in (lo - 12, lo - 5, lo):
            guitar.add(e + at, length, q, 100)
        bass.add(e + at, length, lo - 12, 112)
        piano.add(e + at, length, lo - 12, 110)
        drums.add(e + at, .3, KICK, 120)
        drums.add(e + at, 2 if at == 4 else .5, CRASH, 116)
        timp.add(e + at, .6, nearest(r, n("D2")), 110)
        fx.at(song.t(e + at), hy.ensemble_hit(.9, seed=int(at * 10)), gain=.7)
    choir.add(e + 4, 6, n("D4"), 100)
    choir.add(e + 4, 6, n("A4"), 100)
extra = {"fx": (fx.buf, dict(level=-25, send=-8, width=1.3, bus="fx", eq=[HighpassFilter(60), HighpassFilter(60)]))}

if __name__ == "__main__":
    S = START
    finish("acg_battle_rush", [horns, brass, violins, ostinato, choir, piano, guitar, bass, drums, timp], song,
           [("intro", 0, 4), ("A1", S["A1"], S["B"]), ("B", S["B"], S["A2"]), ("A2", S["A2"], S["C1"]),
            ("C1", S["C1"], S["C2"]), ("C2", S["C2"], S["C2"] + 8)],
           lead={"horns", "violins"}, beats_per_bar=B, loop=LOOP, lufs=-14.0, extra=extra,
           hall=dict(rt_low=2.0, rt_mid=1.8, rt_high=1.0, predelay=.02, length=3.5),
           sidechain=(("drums",), ("strings", "guitar", "choir"), 1.5),
           bus_fx={"guitar": [PeakFilter(2500, -2, 1)]})
