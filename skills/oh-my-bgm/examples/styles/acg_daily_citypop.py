"""After School — ACG slice-of-life BGM in a city-pop cut: the Marunouchi progression
(IVmaj7 - III7 - vi7 - v7 I7) in the verse, the royal-road progression (IVmaj7 - V7 - iii7 - vi7) in the chorus,
bright piano tune, Rhodes, finger bass with 16th push, muted guitar, strings, flute + violins for the chorus.
Suits: anime / manga daily-life scenes, campus and city vlogs, light character intros, cafés.
F major, 124 BPM, 50 bars (~1:40); with --loop a seamless loop (drops the ending).

intro | Bbmaj7 | A7 | Dm7 | Cm7 F7 |
verse | Bbmaj7 | A7 | Dm7 | Cm7 F7 | Bbmaj7 | A7 | Dm7 G7 | Gm7 C7 |
pre   | Gm7 | Am7 | Bbmaj7 | C7sus C7 |
chorus| Bbmaj7 | C7 | Am7 | Dm7 | Gm7 | C7 | F | F7 |
Form: intro 4 · verse (piano) · pre (strings) · chorus (flute + violins) · interlude 4 · verse (piano + flute
answers) · pre · chorus (everyone) · ending 2 (Fmaj9).
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/acg_daily_citypop.py [--loop]   -> ./out/acg_daily_citypop/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402

from orch import GU_SF, Song, n, nearest  # noqa: E402
from score import P, finish, kit, play, seq, swing  # noqa: E402

BPM, B = 124, 4
V = {"Bbmaj7": (10, "D4 F4 A4"), "A7": (9, "C#4 E4 G4"), "Dm7": (2, "C4 F4 A4"), "Cm7": (0, "Bb3 Eb4 G4"),
     "F7": (5, "A3 Eb4 G4"), "G7": (7, "B3 D4 F4"), "Gm7": (7, "Bb3 D4 F4"), "C7": (0, "Bb3 E4 G4"),
     "Am7": (9, "C4 E4 G4"), "C7sus": (0, "Bb3 F4 G4"), "F": (5, "A3 C4 F4"), "Fmaj9": (5, "A3 E4 G4")}
INTRO = [["Bbmaj7"], ["A7"], ["Dm7"], ["Cm7", "F7"]]
VERSE = INTRO + [["Bbmaj7"], ["A7"], ["Dm7", "G7"], ["Gm7", "C7"]]
PRE = [["Gm7"], ["Am7"], ["Bbmaj7"], ["C7sus", "C7"]]
CHORUS = [["Bbmaj7"], ["C7"], ["Am7"], ["Dm7"], ["Gm7"], ["C7"], ["F"], ["F7"]]
FORM = [("intro", INTRO), ("verse1", VERSE), ("pre1", PRE), ("chorus1", CHORUS), ("inter", INTRO),
        ("verse2", VERSE), ("pre2", PRE), ("chorus2", CHORUS)] + ([] if LOOP else [("end", [["Fmaj9"], ["Fmaj9"]])])
BARS = [(sec, chs) for sec, bars in FORM for chs in bars]
START = {}
for i, (sec, _) in enumerate(BARS):
    START.setdefault(sec, i)
song = Song(bpm=BPM, beats=len(BARS) * B, tail=3.0, seed=124)

VERSE_MEL = ("r/.5 F4/.5 A4/.5 C5/.5 D5/1 C5/.5 A4/.5 | C#5/1.5 E5/.5 G5/1 E5/1 | F5/1.5 E5/.5 D5/1 C5/1 | "
             "Bb4/1 C5/.5 D5/.5 Eb5/1 C5/1 | r/.5 F4/.5 A4/.5 C5/.5 D5/1 F5/.5 E5/.5 | E5/1 G5/.5 Bb5/.5 A5/2 | "
             "F5/1 E5/1 D5/1 B4/1 | D5/1.5 C5/.5 Bb4/1 E4/1")
PRE_MEL = "Bb4/2 D5/1 F5/1 | C5/2 E5/1 G5/1 | D5/2 F5/1 A5/1 | G5/1.5 F5/.5 E5/1 G5/1"
CHORUS_MEL = ("D5/.5 F5/.5 A5/1.5 G5/.5 F5/1 | E5/1 G5/.5 C6/1.5 Bb5/1 | A5/1.5 G5/.5 E5/1 C5/1 | "
              "D5/1 F5/.5 A5/.5 C6/2 | Bb5/1.5 A5/.5 G5/1 F5/1 | E5/1 F5/.5 G5/.5 Bb5/1 A5/1 | A5/2 C6/1 A5/1 | "
              "G5/2 F5/1 Eb5/1")
ANSWERS = "r/4 | r/2 E6/.5 C#6/.5 A5/1 | r/4 | r/2 G5/.5 F5/.5 Eb5/1 | r/4 | r/4 | r/4 | r/2 G5/.5 E5/.5 C5/1"

piano = P("piano", 1, pan=-.1, width=1.2, level=-18, send=-10, bus="keys", jitter_ms=3,
          eq=[HighpassFilter(150), PeakFilter(400, -2, 1)])
rhodes = P("rhodes", 4, pan=.25, width=1.3, level=-23, send=-11, bus="keys", jitter_ms=3,
           eq=[HighpassFilter(140), PeakFilter(450, -2, 1)])
flute = P("flute", 73, 17, expr_cc=2, pan=.15, level=-17.5, send=-8, bus="lead", jitter_ms=3, legato=-.04,
          eq=[HighpassFilter(300)])
violins = P("violins", 48, 21, expr_cc=2, players=2, pan=-.35, width=1.3, level=-20, send=-6, bus="strings",
            legato=.04, eq=[HighpassFilter(250), PeakFilter(3000, -2, 1)])
strings = P("strings_pad", 49, 17, expr_cc=2, players=2, pan=0, width=1.6, level=-25, send=-5, bus="strings",
            legato=.15, eq=[HighpassFilter(200)])
guitar = P("muted_guitar", 28, sf2=GU_SF, pan=.45, level=-28, send=-14, bus="keys", jitter_ms=3,
           eq=[HighpassFilter(300), PeakFilter(1500, 2, 1)])
bass = P("bass", 33, sf2=GU_SF, width=.2, level=-20.5, send=-30, bus="bass", jitter_ms=3, legato=-.05,
         eq=[HighpassFilter(38), PeakFilter(900, 2, 1), LowpassFilter(5000)])
drums = kit("drums", 0, width=1.2, level=-22, send=-15, bus="drums", jitter_ms=3, eq=[HighpassFilter(35)])
KICK, SNARE, XSTICK, HHC, HHO, CRASH = 36, 38, 37, 42, 46, 49

flat = [(bar, sec, ci, len(chs), c) for bar, (sec, chs) in enumerate(BARS) for ci, c in enumerate(chs)]
for k, (bar, sec, ci, nch, c) in enumerate(flat):
    span = B / nch
    b0 = bar * B + ci * span
    r, voi = V[c]
    vo = [n(q) for q in voi.split()]
    lo = nearest(r, n("F2"))
    if sec == "end":
        if bar == START["end"]:
            for j, q in enumerate([lo - 12, lo] + vo + [n("C5"), n("E5")]):
                rhodes.add(b0 + j * .04, 2 * B, q, 66)
            bass.add(b0, 2 * B, lo - 12 if lo - 12 >= n("E1") else lo, 90)
            drums.add(b0, 3, CRASH, 80)
        continue
    nxt = nearest(V[flat[(k + 1) % len(flat)][4]][0], lo)
    line = [(0, .9, lo, 100), (1.5, .4, lo, 80), (2.5, .4, lo + 12, 84), (3, .4, lo + 7, 82), (3.5, .4, nxt - 1, 78)]
    if nch == 2:
        line = [(0, .9, lo, 98), (1.5, .4, nxt - 1 if ci == 1 else lo + 12, 80)]
    for bb, d, q, v in line:
        bass.add(b0 + bb, d, q, v)
    # Rhodes: off-beat 16th comp; strings pad in pre and chorus
    cells = [(0, .4), (.75, .2), (1.5, .4), (2.5, .4), (3.25, .2)] if nch == 1 else [(0, .4), (.75, .2), (1.5, .4)]
    for bb, d in cells:
        for j, q in enumerate(vo):
            rhodes.add(b0 + bb + j * .01, d, q, 62 + (6 if bb == 0 else 0))
    if sec.startswith(("pre", "chorus")):
        for q in vo:
            strings.add(b0, span, q, 64 if sec.startswith("pre") else 70)
    if sec in ("chorus1", "verse2", "chorus2"):
        for i in range(int(span * 4)):
            if i % 4 in (1, 3):
                guitar.add(b0 + i * .25, .12, vo[-1] + 12, 62)
# drums
for bar, (sec, _) in enumerate(BARS):
    b0 = bar * B
    if sec == "end":
        continue
    big = sec.startswith("chorus")
    for bb in ((0, 1.5, 2.5) if big else (0, 2.5)):
        drums.add(b0 + bb, .2, KICK, 96 if big else 84)
    for bb in (1, 3):
        drums.add(b0 + bb, .2, SNARE if (big or sec.startswith("pre")) else XSTICK, 92 if big else 74)
    step = .25 if big else .5
    for i in range(int(B / step)):
        t = b0 + i * step
        if big and i == 14:
            drums.add(t, .3, HHO, 70)
        else:
            drums.add(t, .1, HHC, (70 if i % 2 == 0 else 50) if big else 62)
    if bar in (START["chorus1"], START["chorus2"], START["inter"]):
        drums.add(b0, 2, CRASH, 92)

for v in ("verse1", "verse2"):
    play(piano, seq(VERSE_MEL, START[v] * B), 88)
play(flute, seq(ANSWERS, START["verse2"] * B), 80)
for p_ in ("pre1", "pre2"):
    play(violins, seq(PRE_MEL, START[p_] * B), 86)
play(flute, seq(CHORUS_MEL, START["chorus1"] * B), 94)
play(violins, seq(CHORUS_MEL, START["chorus1"] * B, shift=-12), 72)
play(flute, seq(CHORUS_MEL, START["chorus2"] * B), 98)
play(violins, seq(CHORUS_MEL, START["chorus2"] * B), 84)
play(piano, seq(CHORUS_MEL, START["chorus2"] * B, shift=-12), 70)
if not LOOP:
    play(flute, seq("A5/1 G5/1 A5/2 | C6/4", START["end"] * B), 86)
for p in (piano, rhodes, guitar, bass, drums, flute):
    swing(p, .54, unit=.25)

if __name__ == "__main__":
    S = START
    finish("acg_daily_citypop", [piano, rhodes, flute, violins, strings, guitar, bass, drums], song,
           [("verse1", S["verse1"], S["pre1"]), ("pre1", S["pre1"], S["chorus1"]), ("chorus1", S["chorus1"], S["inter"]),
            ("verse2", S["verse2"], S["pre2"]), ("chorus2", S["chorus2"], S["chorus2"] + 8)],
           lead={"piano", "flute", "violins"}, beats_per_bar=B, loop=LOOP,
           hall=dict(rt_low=1.4, rt_mid=1.2, rt_high=.8, predelay=.02, length=2.8),
           sidechain=(("drums",), ("keys", "strings"), 1.0))
