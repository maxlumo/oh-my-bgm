"""Wheatfield Town — a pastoral orchestral waltz with a Lydian lift (G/F: the raised 4th B natural
over the tonic), a borrowed minor iv (Bbm/Db), a woodwind dialogue in the relative minor, and a last verse a
whole step up. Suits: open-world towns, travel and countryside videos, warm brand films.
F major -> G major, 3/4 at 132 BPM (one-in-a-bar lilt), 80 bars (~1:50). Ends in G; with --loop the outro
turns back to F for a seamless loop.

A (16) | F | G/F | C/E | Dm7 | Bb | F/A | Gm7 | C7sus C7 | F | G/F | Am7 | Dm7 | Bb | Bbm/Db | F/C C7 | F |
B (16) | Dm | A7/C# | Dm | F/C | Bb | F/A | Gm | C | Bb | C | Am | Dm | Gm | Bb/C | Dsus | D7 |  (D7 -> G)
outro  | G | Cmaj7/G | G | Gm7 | Gm7 | C7sus | C7sus | C7 |  (G -> Gm7 = ii of F -> back to the intro)

Orchestration: intro harp, pizz, pad, flute bird-calls · A1 flute, clarinet counterline · A2 violins + flute,
horn countermelody, moving cellos · B oboe and clarinet answer each other over pizz oom-pah-pah, bassoon bass ·
A3 (G) tutti: violins + flute + oboe, horns, celesta, timpani, triangle · outro back to F.
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/pastoral_orchestra.py [--loop]   -> ./out/pastoral_orchestra/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv  # optional seamless game loop; default: a whole piece with an ending

from pedalboard import HighpassFilter, HighShelfFilter, LowpassFilter, PeakFilter  # noqa: E402

import hybrid as hy  # noqa: E402
from orch import GM_SF, Song, n, nearest  # noqa: E402
from score import P, finish, kit, play, seq  # noqa: E402

BPM, B = 132, 3
song = Song(bpm=BPM, beats=80 * B, tail=5.0, seed=132)

CH = {"F": (5, [5, 9, 0]), "G/F": (5, [7, 11, 2]), "C/E": (4, [0, 4, 7]), "Dm7": (2, [2, 5, 9, 0]),
      "Bb": (10, [10, 2, 5]), "F/A": (9, [5, 9, 0]), "Gm7": (7, [7, 10, 2, 5]), "C7sus": (0, [0, 5, 7, 10]),
      "C7": (0, [0, 4, 7, 10]), "Am7": (9, [9, 0, 4, 7]), "Bbm/Db": (1, [10, 1, 5]), "F/C": (0, [5, 9, 0]),
      "Dm": (2, [2, 5, 9]), "A7/C#": (1, [9, 1, 4, 7]), "Gm": (7, [7, 10, 2]), "C": (0, [0, 4, 7]),
      "Am": (9, [9, 0, 4]), "Bb/C": (0, [10, 2, 5]), "Dsus": (2, [2, 7, 9]), "D7": (2, [2, 6, 9, 0]),
      "G": (7, [7, 11, 2]), "Cmaj7/G": (7, [0, 4, 7, 11])}
A_CH = [["F"], ["G/F"], ["C/E"], ["Dm7"], ["Bb"], ["F/A"], ["Gm7"], ["C7sus", "C7"],
        ["F"], ["G/F"], ["Am7"], ["Dm7"], ["Bb"], ["Bbm/Db"], ["F/C", "C7"], ["F"]]
B_CH = [["Dm"], ["A7/C#"], ["Dm"], ["F/C"], ["Bb"], ["F/A"], ["Gm"], ["C"],
        ["Bb"], ["C"], ["Am"], ["Dm"], ["Gm"], ["Bb/C"], ["Dsus"], ["D7"]]
OUTRO = ([["G"], ["Cmaj7/G"], ["G"], ["Gm7"], ["Gm7"], ["C7sus"], ["C7sus"], ["C7"]] if LOOP  # back to F
         else [["G"], ["Cmaj7/G"], ["G"], ["Cmaj7/G"], ["C"], ["Dsus"], ["D7"], ["G"]])  # cadence in G
FORM = [("intro", A_CH[:8], 0), ("A1", A_CH, 0), ("A2", A_CH, 0), ("B", B_CH, 0), ("A3", A_CH, 2), ("outro", OUTRO, 0)]
BARS = [(sec, chs, sh) for sec, bars, sh in FORM for chs in bars]

MEL_A = ("C5/1 F5/1 G5/1 | A5/1.5 B5/.5 A5/1 | G5/2 E5/1 | F5/1.5 E5/.5 D5/1 | D5/1 F5/1 Bb5/1 | A5/2 G5/.5 F5/.5 | "
         "Bb5/1.5 A5/.5 G5/1 | F5/1.5 E5/1.5 | C5/1 F5/1 G5/1 | A5/1.5 B5/.5 D6/1 | C6/2 B5/.5 A5/.5 | "
         "A5/1.5 G5/.5 F5/1 | D5/1 F5/1 A5/1 | Ab5/2 F5/1 | A5/1 C6/.5 G5/1 E5/.5 | F5/3")
MEL_B = ("A4/1 D5/1 E5/1 | F5/1.5 E5/.5 C#5/1 | D5/1 F5/1 A5/1 | G5/1.5 F5/.5 C5/1 | D5/2 F5/1 | C5/2 A4/1 | "
         "Bb4/1 D5/1 G5/1 | E5/3 | F5/1 D5/1 Bb4/1 | E5/1 G5/1 C6/1 | C6/1.5 B5/.5 A5/1 | A5/1 F5/1 D5/1 | "
         "Bb5/2 A5/.5 G5/.5 | F5/2 G5/1 | G5/1 A5/1 C6/1 | A5/1.5 F#5/.5 D5/1")
HORN = ("A4/3 | B4/3 | C5/2 G4/1 | F4/3 | F4/2 D4/1 | C4/3 | D4/3 | F4/1.5 E4/1.5 | A4/3 | B4/3 | C5/3 | A4/3 | "
        "F4/3 | F4/3 | F4/1.5 E4/1.5 | F4/3")
CLAR_A = "r/3 | r/3 | r/3 | r/3 | r/3 | r/3 | r/3 | r/3 | F4/3 | D4/3 | E4/3 | F4/3 | D4/3 | Db4/3 | C4/1.5 Bb3/1.5 | A3/3"
BIRDS = "r/3 | r/3 | C6/.5 G5/.5 E5/2 | r/3 | r/3 | r/3 | D6/.5 Bb5/.5 G5/1 A5/1 | r/3"
OUTRO_FL = ("B5/1.5 A5/.5 G5/1 | E5/3 | D5/3 | r/3 | Bb5/1.5 A5/.5 G5/1 | F5/3 | G5/1.5 F5/1.5 | E5/3" if LOOP else
            "B5/1.5 A5/.5 G5/1 | E5/3 | D5/3 | r/3 | E5/1.5 D5/.5 C5/1 | G5/3 | F#5/1.5 E5/.5 D5/1 | B4+G5/3")
SCALE_F = [5, 7, 9, 10, 0, 2, 4]


def third_below(p):
    if p % 12 not in SCALE_F:
        return p - 4
    i = SCALE_F.index(p % 12)
    return p - ((p - SCALE_F[(i - 2) % 7]) % 12)


flute = P("flute", 73, 17, expr_cc=2, pan=-.1, level=-18, send=-6, bus="winds", jitter_ms=4, legato=-.03,
          eq=[HighpassFilter(300), LowpassFilter(11000)])
oboe = P("oboe", 68, 17, expr_cc=2, pan=.05, level=-19, send=-6, bus="winds", jitter_ms=4, legato=-.03,
         eq=[HighpassFilter(250), PeakFilter(1500, -1.5, 1)])
clar = P("clarinet", 71, 17, expr_cc=2, pan=.2, level=-20.5, send=-6, bus="winds", jitter_ms=4, legato=-.03,
         eq=[HighpassFilter(150)])
bsn = P("bassoon", 70, 17, expr_cc=2, pan=.25, level=-22, send=-7, bus="winds", jitter_ms=4, legato=-.1,
        eq=[HighpassFilter(55)])
vln = P("violins", 48, 21, expr_cc=2, players=2, pan=-.4, width=1.3, level=-18.5, send=-5, bus="strings",
        jitter_ms=4, legato=.04, eq=[HighpassFilter(250), PeakFilter(3000, -2, 1)])
violas = P("violas_pad", 49, 31, expr_cc=2, players=2, pan=.15, width=1.4, level=-26, send=-5, bus="strings",
           legato=.2, eq=[HighpassFilter(180), PeakFilter(350, -2, 1)])
celli = P("celli", 49, 41, expr_cc=2, players=2, pan=.35, width=1.2, level=-22, send=-6, bus="strings",
          legato=.05, eq=[HighpassFilter(60), PeakFilter(300, -2, 1)])
basses = P("basses", 49, 51, expr_cc=2, pan=.5, level=-25, send=-8, bus="strings", legato=.05,
           eq=[HighpassFilter(35), LowpassFilter(3000)])
pizz = P("pizz", 45, players=2, pan=-.1, width=1.4, level=-23, send=-7, bus="strings", jitter_ms=4,
         eq=[HighpassFilter(80)])
horns = P("horns", 60, 17, expr_cc=2, players=2, pan=-.3, width=1.2, level=-21.5, send=-5, bus="brass", legato=.08,
          eq=[HighpassFilter(90), LowpassFilter(5000)])
harp = P("harp", 46, pan=.35, width=1.3, level=-22, send=-6, bus="harp", jitter_ms=3, eq=[HighpassFilter(120)])
celesta = P("celesta", 8, pan=.4, level=-27, send=-5, bus="harp", jitter_ms=3, eq=[HighpassFilter(500)])
timp = P("timpani", 47, pan=-.1, level=-25, send=-6, bus="perc", roll=.125, eq=[HighpassFilter(40)])
perc = kit("triangle", 48, sf2=GM_SF, pan=.3, level=-31, send=-5, bus="perc", eq=[HighpassFilter(2000)])
TRIANGLE = 81

flat = [(bar, sec, ci, len(chs), c, sh) for bar, (sec, chs, sh) in enumerate(BARS) for ci, c in enumerate(chs)]
for k, (bar, sec, ci, nch, c, sh) in enumerate(flat):
    span = B / nch
    b0 = bar * B + ci * span
    bpc, pcs = CH[c]
    bpc, pcs = (bpc + sh) % 12, [(p + sh) % 12 for p in pcs]
    nb, nsh = CH[flat[(k + 1) % len(flat)][4]][0], flat[(k + 1) % len(flat)][5]
    lo = nearest(bpc, n("F2"))
    nxt = nearest((nb + nsh) % 12, lo)
    up = sorted(nearest(p, n("A3")) for p in pcs)
    arp = [lo + 12] + up + [q + 12 for q in up]
    # harp: rising-and-falling 8ths (lighter in B, where the pizz carries the time)
    if sec != "B":
        idx = [0, 1, 2, 3, 4, 3] if nch == 1 else [0, 2, 4]
        for j, i in enumerate(idx):
            harp.add(b0 + j * .5, min(1.2, span - j * .5), arp[min(i, len(arp) - 1)], (70 if j == 0 else 58) - (6 if sec == "A2" else 0))
    # bass voice: pizz basses in intro / A1, bowed cellos + basses in A2 / A3 with a passing note, bassoon in B
    if sec in ("intro", "A1", "outro"):
        pizz.add(b0, 1, lo, 84)
        violas.add(b0, span, up[1] + 12 if len(up) > 1 else up[0], 62 if sec != "A1" else 66)
        violas.add(b0, span, up[0], 58)
    elif sec in ("A2", "A3"):
        if nch == 1:
            celli.add(b0, 2, lo, 86)
            tones = [lo + (p - lo) % 12 for p in pcs if (p - lo) % 12 not in (0, 1, 11)]
            celli.add(b0 + 2, 1, min(tones, key=lambda q: abs(q - lo - 7)), 74)  # a chord tone over the held bass
        else:
            celli.add(b0, span, lo, 84)
        basses.add(b0, span, lo - 12 if lo - 12 >= n("E1") else lo, 80)
        violas.add(b0, span, up[1] + 12 if len(up) > 1 else up[0], 70)
    elif sec == "B":
        bsn.add(b0, 1, lo, 86)
        pizz.add(b0, 1, lo, 82)
        if nch == 1:
            for bb in (1, 2):
                for q in up[:3]:
                    pizz.add(b0 + bb, .5, q + 12, 66)
    if sec == "A3":
        if bar % 4 == 0:
            timp.add(b0, .9, nearest(bpc, n("A2")), 86)
        if bar % 2 == 0:
            perc.add(b0, .5, TRIANGLE, 70)
timp.add(54 * B, 6, n("A2"), 70)  # roll into the key change

play(flute, seq(BIRDS, 0), 78)
play(flute, seq(MEL_A, 8 * B), 90)
play(clar, seq(CLAR_A, 8 * B), 76)
play(vln, seq(MEL_A, 24 * B), 92)
play(flute, seq(MEL_A, 24 * B), 76)
play(horns, seq(HORN, 24 * B), 80)
B_NOTES = seq(MEL_B, 40 * B)
for first, part, vel in [(40, oboe, 90), (44, clar, 86), (48, oboe, 90)]:  # oboe and clarinet answer each other
    play(part, [x for x in B_NOTES if first * B <= x[0] < (first + 4) * B], vel)
last = [x for x in B_NOTES if x[0] >= 52 * B]  # last 4 bars together, clarinet a third below
play(oboe, last, 92)
play(clar, [(b, d, third_below(p)) for b, d, p in last if b < 55 * B] + seq("F#5/1.5 D5/.5 A4/1", 55 * B), 78)  # D7 bar: thirds in D
play(vln, seq(MEL_A, 56 * B, shift=2), 92)
play(flute, seq(MEL_A, 56 * B, shift=2), 74)
play(oboe, seq(MEL_A, 56 * B, shift=-10), 68)
play(horns, seq(HORN, 56 * B, shift=2), 88)
play(celesta, seq(MEL_A, 56 * B, shift=14), 66)
play(flute, seq(OUTRO_FL, 72 * B), 76)

fx = hy.Layer(song.length)
fx.at(song.t(56 * B), hy.reverse_swell(2.0, 56), end=True, gain=.6)
extra = {"swell": (fx.buf, dict(level=-30, send=-8, width=1.2, bus="fx", eq=[HighpassFilter(400)]))}

if __name__ == "__main__":
    finish("pastoral_orchestra",
           [flute, oboe, clar, bsn, vln, violas, celli, basses, pizz, horns, harp, celesta, timp, perc], song,
           [("intro", 0, 8), ("A1", 8, 24), ("A2", 24, 40), ("B", 40, 56), ("A3 (G)", 56, 72), ("outro", 72, 80)],
           lead={"flute", "violins", "oboe"}, beats_per_bar=B, loop=LOOP, extra=extra,
           hall=dict(rt_low=2.4, rt_mid=2.1, rt_high=1.2, predelay=.025, length=4.0),
           tone=[PeakFilter(400, -1.0, .8), HighShelfFilter(cutoff_frequency_hz=8000, gain_db=1.5)])
