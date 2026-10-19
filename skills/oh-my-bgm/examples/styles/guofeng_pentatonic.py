"""Stratagems — tense, patient, deliberate: a mind weighing its next move. A koto ostinato in the role of a
guzheng, pipa-style tremolo on shamisen, xiao-style shakuhachi, erhu-style violin with slides, taiko in 3+3+2,
a lament bass under it all. Scenes: strategy and history, a heist being planned, the calm before a
confrontation, a chess-like duel. D yu pentatonic (D F G A C), 90 BPM, 40 bars (~1:50); with --loop a
seamless loop.

Bass, A: D D C C Bb Bb A A (a slow lament descent) · B: F F G G Bb C D D (rising)
Form: intro 4 (koto, drone) · A shakuhachi · A' pipa tremolo + taiko · B erhu, strings · A'' erhu + shakuhachi,
full percussion · outro 4 (koto, drone).
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/guofeng_pentatonic.py [--loop]   -> ./out/guofeng_pentatonic/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv  # optional seamless game loop; default: a whole piece with an ending

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter

from orch import GM_SF, GU_SF, SR, Song, n, nearest  # noqa: E402,F401
from score import P, finish, kit, play, seq, swing  # noqa: E402,F401
import hybrid as hy  # noqa: E402

BPM, B = 90, 4
song = Song(bpm=BPM, beats=40 * B, tail=4.5, seed=90)
PENT = {2, 5, 7, 9, 0}
D, F, G, A, C, Bb = 2, 5, 7, 9, 0, 10
SEC = ["intro"] * 4 + ["A"] * 8 + ["A2"] * 8 + ["B"] * 8 + ["A3"] * 8 + ["outro"] * 4
ROOTS_A = [D, D, C, C, Bb, Bb, A, A]
ROOTS_B = [F, F, G, G, Bb, C, D, D]
ROOT = [D, D, C, D] + ROOTS_A * 2 + ROOTS_B + ROOTS_A + [D, D, C, D]


def snap(p, root=None):
    """Nearest pentatonic pitch; the bar's own root (e.g. Bb) is allowed too."""
    ok = PENT | ({root} if root is not None else set())
    for k in range(7):
        for q in (p - k, p + k):
            if q % 12 in ok:
                return q
    return p


MEL_A = ("A4/2 C5/1 D5/1 | F5/1.5 D5/.5 C5/2 | D5/1 C5/.5 A4/.5 G4/2 | A4/.5 G4/.5 F4/1 G4/2 | "
         "D5/2 F5/1 G5/1 | A5/1.5 G5/.5 F5/1 D5/1 | C5/1 D5/.5 C5/.5 A4/2 | G4/.5 A4/3.5")
MEL_B = ("C5/1 F5/1 A5/2 | G5/1 F5/.5 D5/.5 F5/2 | D5/1.5 F5/.5 G5/2 | A5/1 C6/1 A5/.5 G5/.5 F5/1 | "
         "F5/2 D5/1 F5/1 | G5/1.5 A5/.5 C6/2 | D6/3 C6/1 | A5/1 G5/.5 F5/.5 D5/2")
# shakuhachi answers inside A'' (call and response with the erhu)
ANSWER = "r/4 | r/4 | r/4 | r/2 C6/.5 A5/.5 G5/1 | r/4 | r/4 | r/4 | r/2 D6/.5 C6/.5 A5/1"

koto = P("koto", 107, pan=-.25, width=1.2, level=-21, send=-10, bus="pluck", jitter_ms=4,
         eq=[HighpassFilter(150), PeakFilter(500, -1.5, 1)])
pipa = P("pipa", 106, pan=.25, level=-19, send=-10, bus="lead", jitter_ms=3,
         eq=[HighpassFilter(220), PeakFilter(1500, -1, 1)])
xiao = P("xiao", 77, 17, expr_cc=2, pan=-.1, level=-18, send=-7, bus="lead", jitter_ms=4, legato=.05,
         eq=[HighpassFilter(250), LowpassFilter(9000)])
erhu = P("erhu", 40, 18, expr_cc=2, pan=.1, level=-16.5, send=-7, bus="lead", jitter_ms=4, legato=.08,
         eq=[HighpassFilter(280), PeakFilter(2800, -2.5, 1.2), PeakFilter(1000, 1.5, 1), LowpassFilter(8500)])
celli = P("celli", 49, 41, expr_cc=2, players=2, pan=-.2, width=1.3, level=-23, send=-6, bus="strings", legato=.2,
          eq=[HighpassFilter(55), PeakFilter(300, -1.5, 1)])
basses = P("basses", 49, 51, expr_cc=2, pan=.15, level=-25, send=-8, bus="strings", legato=.2,
           eq=[HighpassFilter(40), LowpassFilter(3000)])
violas = P("violas_pad", 49, 31, expr_cc=2, players=2, pan=.3, width=1.4, level=-27, send=-5, bus="strings",
           legato=.2, eq=[HighpassFilter(200), PeakFilter(2500, -2, 1)])
taiko = P("taiko", 116, sf2=GU_SF, pan=0, width=1.2, level=-22, send=-9, bus="drums", jitter_ms=4,
          eq=[HighpassFilter(70), HighpassFilter(70), HighpassFilter(50), LowpassFilter(6000)])
perc = kit("perc", 48, sf2=GM_SF, pan=.3, width=1.4, level=-28, send=-8, bus="drums", jitter_ms=5,
           eq=[HighpassFilter(200)])
WOOD_HI, WOOD_LO, CHINA = 76, 77, 52

KOTO_SHAPE = [0, 7, 12, 7, 15, 12, 7, 5]
for bar, sec in enumerate(SEC):
    b0, r = bar * B, ROOT[bar]
    base = nearest(r, n("E3"))
    # koto: 8ths on a pentatonic shape over the bass, a 16th run into every 4th bar
    shape = KOTO_SHAPE if bar % 2 == 0 else [12, 7, 15, 12, 17, 15, 12, 7]
    vel = 74 if sec in ("intro", "outro", "A") else 66
    for i, iv in enumerate(shape):
        koto.add(b0 + i * .5, .9, snap(base + iv, r), vel + (8 if i % 4 == 0 else 0))
    if bar % 4 == 3 and sec != "outro":
        top = snap(base + 24)
        for k in range(6):
            q = snap(top - [0, 2, 5, 7, 9, 12][k])
            koto.add(b0 + 3.0 + k / 6, .3, q, 70 - k * 3)  # descending gliss into the next bar
    # drone strings
    lo = nearest(r, n("D2"))
    sv = {"intro": 62, "A": 70, "A2": 76, "B": 86, "A3": 90, "outro": 60}[sec]
    if bar % 2 == 0 or ROOT[bar] != ROOT[bar - 1]:
        dur = B * (2 if bar + 1 < len(ROOT) and ROOT[bar + 1] == r else 1)
        celli.add(b0, dur, lo + 12, sv)
        celli.add(b0, dur, snap(lo + 19, r), sv - 10)
        if sec not in ("intro", "outro"):
            basses.add(b0, dur, lo, sv - 4)
        if sec in ("B", "A3"):
            for q in (snap(lo + 24, r), snap(lo + 28, r)):
                violas.add(b0, dur, q, sv - 6)
    # taiko 3+3+2, softer in A, with pickup flams before section starts
    if sec in ("A2", "B", "A3"):
        t_lo = n("D2")
        for bb, v in [(0, 96), (1.5, 76), (3, 84)]:
            taiko.add(b0 + bb, .5, t_lo, v - (10 if sec == "A2" else 0))
        if sec == "A3":
            taiko.add(b0 + 3.5, .3, t_lo + 7, 70)
        for bb in (.5, 2, 2.5):
            if sec != "A2":
                perc.add(b0 + bb, .2, WOOD_HI if bb != 2 else WOOD_LO, 62)
    if sec == "A" and bar % 2 == 1:
        taiko.add(b0 + 3, .5, n("D2"), 70)
    if bar in (12, 20, 28):
        perc.add(b0, 2, CHINA, 70)

play(xiao, seq(MEL_A, 4 * B), 88)
play(pipa, seq(MEL_A, 12 * B), 92)
play(pipa, seq(MEL_A, 12 * B, shift=-12), 66)       # pipa's lower string doubling
play(erhu, seq(MEL_B, 20 * B), 94)
play(erhu, seq(MEL_A, 28 * B), 92)
play(xiao, seq(ANSWER, 28 * B), 90)
play(pipa, seq(MEL_A, 28 * B, shift=-12), 70)       # pipa heterophony under the erhu
play(xiao, seq("A4/2 C5/1 D5/1 | F5/1.5 D5/.5 C5/2 | r/4 | r/2 D5/2", 36 * B), 74)
# pipa: tremolo (lunzhi) on notes of a beat or longer, single plucks otherwise
long_ = [nt for nt in pipa.notes if nt.dur >= 1]
pipa.notes = [nt for nt in pipa.notes if nt.dur < 1]
for nt in long_:
    k = 0
    while k * .125 < nt.dur - .06:
        pipa.add(nt.beat + k * .125, .125, nt.pitch, nt.vel * (.8 + .2 * min(1, k / 6)) - (5 if k % 2 else 0))
        k += 1
# erhu slides: a short grace note a step below each long note
for nt in list(erhu.notes):
    if nt.dur >= 1.5:
        erhu.add(nt.beat - .12, .14, snap(nt.pitch - 2), nt.vel - 18)

fx = hy.Layer(song.length)
for bar in (12, 20, 28):  # deep drum at section starts
    fx.at(song.t(bar * B), hy.ensemble_hit(.7, seed=bar), gain=.6)
extra = {"big_drum": (fx.buf, dict(level=-27, send=-8, width=1.2, bus="drums", eq=[HighpassFilter(70), HighpassFilter(70), HighpassFilter(50), LowpassFilter(5000)]))}

if __name__ == "__main__":
    finish("guofeng_pentatonic", [koto, pipa, xiao, erhu, celli, basses, violas, taiko, perc], song,
           [("intro", 0, 4), ("A", 4, 12), ("A'", 12, 20), ("B", 20, 28), ("A''", 28, 36)],
           lead={"pipa", "xiao", "erhu"}, beats_per_bar=B, loop=LOOP, extra=extra,
           hall=dict(rt_low=2.2, rt_mid=1.9, rt_high=1.0, predelay=.025, length=4.0))
