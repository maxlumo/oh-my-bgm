"""Song of Shifting Sands — solo cello over a harp ostinato and a low drone in D Hijaz
(D Eb F# G A Bb C, the augmented 2nd Eb-F#), sitar ornaments, frame-drum maqsum, an English horn answering,
then a high solo violin with choir for the climax. Suits: desert journeys, Silk Road / Middle East
documentaries, pilgrimage and solitude. 76 BPM, 32 bars (~1:41); with --loop a seamless loop.

Roots: drone D D Eb D · A D Eb D Cm Gm Eb D D (x2) · B Gm Eb Cm D Gm Eb Cm D · drone D D Eb D
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/hijaz_desert.py [--loop]   -> ./out/hijaz_desert/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv  # optional seamless game loop; default: a whole piece with an ending

import numpy as np  # noqa: E402
from pedalboard import HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402
from scipy import signal  # noqa: E402

import hybrid as hy  # noqa: E402
from orch import GU_SF, SR, Song, n, nearest  # noqa: E402
from score import P, finish, kit, play, seq  # noqa: E402

BPM, B = 76, 4
song = Song(bpm=BPM, beats=32 * B, tail=5.0, seed=76)
D, Eb, C, G = 2, 3, 0, 7
QUAL = {D: 4, Eb: 4, C: 3, G: 3}
A_ROOTS = [D, Eb, D, C, G, Eb, D, D]
ROOTS = [D, D, Eb, D] + A_ROOTS * 2 + [G, Eb, C, D, G, Eb, C, D] + [D, D, Eb, D]
SEC = ["drone"] * 4 + ["A1"] * 8 + ["A2"] * 8 + ["B"] * 8 + ["return"] * 4

CELLO_A = ("D4/1.5 Eb4/.5 F#4/2 | G4/1 F#4/.5 Eb4/.5 D4/2 | A4/2 Bb4/1 A4/1 | G4/1.5 F#4/.5 G4/1 Eb4/1 | "
           "D4/1 G4/1 Bb4/1.5 A4/.5 | G4/2 F#4/1 Eb4/1 | F#4/1 G4/.5 F#4/.5 Eb4/1 D4/1 | D4/4")
VIOLIN_B = ("D5/1 G5/1 Bb5/2 | G5/1.5 Bb5/.5 G5/1 Eb5/1 | Eb5/1 G5/1 C6/2 | Bb5/1 A5/1 F#5/1 Eb5/1 | "
            "D5/1 G5/1 Bb5/1.5 C6/.5 | D6/2 C6/1 Bb5/1 | A5/1 Bb5/.5 A5/.5 G5/1 F#5/1 | F#5/1 Eb5/1 D5/2")
CELLO_B = "G3/4 | Bb3/4 | C4/4 | A3/4 | Bb3/4 | G3/4 | Eb3/4 | D3/4"
EH_ANSWERS = "r/4 | r/4 | r/4 | r/2 A4/.5 Bb4/.5 A4/1 | r/4 | r/4 | r/4 | r/1 F#4/.5 G4/.5 F#4/.5 Eb4/.5 D4/1"
SITAR_TURN = [(0, "D5"), (.25, "Eb5"), (.5, "D5"), (.75, "C5"), (1, "D5")]

cello = P("cello", 42, 17, expr_cc=2, pan=-.05, level=-17, send=-5, bus="lead", jitter_ms=5, legato=.1,
          eq=[HighpassFilter(70), PeakFilter(300, -1.5, 1), LowpassFilter(7500)])
violin = P("violin", 40, 17, expr_cc=2, pan=-.2, level=-17.5, send=-4, bus="lead", jitter_ms=5, legato=.08,
           eq=[HighpassFilter(280), PeakFilter(2800, -2.5, 1.2), LowpassFilter(9000)])
ehorn = P("english_horn", 69, 17, expr_cc=2, pan=.25, level=-20, send=-5, bus="lead", jitter_ms=5,
          eq=[HighpassFilter(200)])
sitar = P("sitar", 104, sf2=GU_SF, pan=.4, level=-25, send=-6, bus="pluck", jitter_ms=3, eq=[HighpassFilter(250)])
harp = P("harp", 46, pan=.3, width=1.3, level=-22, send=-6, bus="pluck", jitter_ms=3, eq=[HighpassFilter(150)])
celli = P("drone_celli", 49, 41, expr_cc=2, players=2, pan=-.25, width=1.3, level=-24, send=-5, bus="strings",
          legato=.3, eq=[HighpassFilter(55), PeakFilter(300, -2, 1)])
basses = P("drone_basses", 49, 51, expr_cc=2, pan=.2, level=-26, send=-7, bus="strings", legato=.3,
           eq=[HighpassFilter(35), LowpassFilter(2500)])
choir = P("choir", 53, 17, expr_cc=2, players=2, pan=0, width=1.6, level=-25, send=-3, bus="choir", legato=.4,
          eq=[HighpassFilter(200), PeakFilter(2500, -2, 1)])
drum = kit("frame_drum", 0, pan=.1, width=1.2, level=-25, send=-8, bus="perc", jitter_ms=5,
           eq=[HighpassFilter(60), LowpassFilter(7000)])
DUM, TEK, OPEN, TAMB = 64, 62, 63, 54

for bar, (sec, r) in enumerate(zip(SEC, ROOTS)):
    b0 = bar * B
    third = QUAL[r]
    r4 = nearest(r, n("D4"))
    if r == D:
        arp = [r4, r4 + 7, r4 + 12, r4 + 7, r4 + 16, r4 + 7, r4 + 13, r4 + 7]   # D A D A F# A Eb A: one b2 per bar
    else:
        arp = [r4, r4 + 7, r4 + 12, r4 + 7, r4 + 12 + third, r4 + 7, r4 + 12, r4 + 7]
    for i, q in enumerate(arp):
        harp.add(b0 + i * .5, min(1.2, B - i * .5), q, (72 if i == 0 else 56 + (6 if i == 4 else 0)) - (8 if sec == "drone" else 0))
    lo = nearest(r, n("D2"))
    sv = {"drone": 62, "A1": 70, "A2": 78, "B": 92, "return": 62}[sec]
    if bar == 0 or ROOTS[bar - 1] != r or bar % 4 == 0:
        dur = 1
        while bar + dur < len(ROOTS) and ROOTS[bar + dur] == r and (bar + dur) % 4:
            dur += 1
        celli.add(b0, dur * B, lo + 12, sv)
        celli.add(b0, dur * B, lo + 19, sv - 8)
        basses.add(b0, dur * B, lo, sv - 6)
        if sec == "B":
            for q in (nearest(r, n("D4")), nearest((r + third) % 12, n("F#4")), nearest((r + 7) % 12, n("A4"))):
                choir.add(b0, dur * B, q, 74)
    # frame drum: maqsum (D T . T D . T .) in 8ths, ghost 16ths in the climax
    if sec in ("A2", "B"):
        for pos, (q, v) in {0: (DUM, 96), 1: (TEK, 64), 3: (TEK, 70), 4: (DUM, 88), 6: (OPEN, 72)}.items():
            drum.add(b0 + pos * .5, .3, q, v - (10 if sec == "A2" else 0))
        if sec == "B":
            for pos in (2.25, 3.75):
                drum.add(b0 + pos, .2, TEK, 44)
            for pos in (.5, 1.5, 2.5, 3.5):
                drum.add(b0 + pos, .2, TAMB, 46)
    if bar in (7, 15, 23) or (sec == "A2" and bar % 2 == 1):  # sitar turns in the gaps of the tune
        at = 2 if bar in (7, 15, 23) else 3
        for off, q in SITAR_TURN:
            sitar.add(b0 + at + off, .3 if off < 1 else 1.0, q, 78)

play(cello, seq(CELLO_A, 4 * B), 88)
play(cello, seq(CELLO_A, 12 * B), 92)
play(ehorn, seq(EH_ANSWERS, 12 * B), 86)
play(violin, seq(VIOLIN_B, 20 * B), 96)
play(cello, seq(CELLO_B, 20 * B), 80)
play(cello, seq("D4/1.5 Eb4/.5 F#4/2 | G4/1 F#4/.5 Eb4/.5 D4/2 | r/4 | r/4", 28 * B), 76)

N = int(song.length * SR)
rng = np.random.default_rng(9)
noise = signal.sosfilt(signal.butter(2, [200, 1800], "band", fs=SR, output="sos"), rng.standard_normal((N, 2)), axis=0)
k = int(SR * 6)
pts = rng.uniform(.15, 1, N // k + 2)
env = np.interp(np.arange(N), np.arange(len(pts)) * k, pts)
fx = hy.Layer(song.length)
fx.at(song.t(20 * B), hy.ensemble_hit(.6, seed=20), gain=.5)
extra = {"wind": ((noise * env[:, None] ** 2).astype(np.float32),
                  dict(level=-38, send=-20, width=1.4, bus="fx", eq=[HighpassFilter(150)])),
         "drum_hit": (fx.buf, dict(level=-30, send=-6, width=1.2, bus="perc",
                                   eq=[HighpassFilter(70), HighpassFilter(70), LowpassFilter(5000)]))}

if __name__ == "__main__":
    finish("hijaz_desert", [cello, violin, ehorn, sitar, harp, celli, basses, choir, drum], song,
           [("drone", 0, 4), ("A1", 4, 12), ("A2", 12, 20), ("B", 20, 28), ("return", 28, 32)],
           lead={"cello", "violin", "english_horn"}, beats_per_bar=B, loop=LOOP, extra=extra,
           hall=dict(rt_low=3.0, rt_mid=2.6, rt_high=1.4, predelay=.03, length=5.0))
