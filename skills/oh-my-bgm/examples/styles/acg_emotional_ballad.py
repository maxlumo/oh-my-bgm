"""When the Stars Fall — the ACG emotional piano-and-strings ballad: a descending-bass verse
(Eb D C Bb Ab G F), a royal-road chorus (IVmaj7 - V7 - iii7 - vi7), a quiet first chorus and a full second one,
then the last chorus a whole step up (prepared by its own dominant) and a piano-alone ending.
Suits: anime / game emotional scenes, farewells and reunions, graduation and year-in-review videos.
Eb major -> F major, 80 BPM, 43 bars (~2:13); the arc is the point, so there is no loop version.

verse  | Eb | Bb/D | Cm7 | Gm/Bb | Abmaj7 | Eb/G | Fm7 | Bbsus4 Bb |
chorus | Abmaj7 | Bb7 | Gm7 | Cm7 | Fm7 | Bb7 | Eb | Eb7 |
Form: intro 4 (piano) · verse (piano tune, cello pad) · chorus (violins, soft drums) · interlude 2 ·
chorus (everyone, guitar arpeggios) · pivot 1 (C7sus C7) · chorus in F (highest) · outro 4 (piano).
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/acg_emotional_ballad.py   -> ./out/acg_emotional_ballad/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402

from orch import GU_SF, Song, n, nearest  # noqa: E402
from score import P, finish, kit, play, seq  # noqa: E402

BPM, B = 80, 4
# chord -> (bass pc, chord pcs)
CH = {"Eb": (3, [3, 7, 10]), "Bb/D": (2, [10, 2, 5]), "Cm7": (0, [0, 3, 7, 10]), "Gm/Bb": (10, [7, 10, 2]),
      "Abmaj7": (8, [8, 0, 3, 7]), "Eb/G": (7, [3, 7, 10]), "Fm7": (5, [5, 8, 0, 3]), "Bbsus4": (10, [10, 3, 5]),
      "Bb": (10, [10, 2, 5]), "Bb7": (10, [10, 2, 5, 8]), "Gm7": (7, [7, 10, 2, 5]), "Eb7": (3, [3, 7, 10, 1]),
      "C7sus": (0, [0, 5, 7, 10]), "C7": (0, [0, 4, 7, 10]), "F": (5, [5, 9, 0])}
VERSE = [["Eb"], ["Bb/D"], ["Cm7"], ["Gm/Bb"], ["Abmaj7"], ["Eb/G"], ["Fm7"], ["Bbsus4", "Bb"]]
CHORUS = [["Abmaj7"], ["Bb7"], ["Gm7"], ["Cm7"], ["Fm7"], ["Bb7"], ["Eb"], ["Eb7"]]
FINAL = CHORUS[:6] + [["Eb"], ["Eb"]]
FORM = [("intro", CHORUS[:4], 0), ("verse", VERSE, 0), ("chorus1", CHORUS, 0), ("inter", CHORUS[:2], 0),
        ("chorus2", CHORUS[:7] + [["Bbsus4", "Bb"]], 0), ("pivot", [["C7sus", "C7"]], 0), ("final", FINAL, 2),
        ("outro", [["Abmaj7"], ["Bb"], ["Eb"], ["Eb"]], 2)]
BARS = [(sec, chs, sh) for sec, bars, sh in FORM for chs in bars]
START = {}
for i, (sec, _, _) in enumerate(BARS):
    START.setdefault(sec, i)
song = Song(bpm=BPM, beats=len(BARS) * B, tail=6.0, seed=80)

VERSE_MEL = ("G4/1 Bb4/1 Eb5/1.5 D5/.5 | D5/2 C5/1 Bb4/1 | C5/1 Eb5/1 G5/1.5 F5/.5 | F5/2 D5/1 Bb4/1 | "
             "C5/1 Eb5/1 Ab5/1.5 G5/.5 | G5/2 F5/1 Eb5/1 | Ab5/1 G5/.5 F5/.5 Eb5/1 C5/1 | Eb5/2 D5/2")
CHORUS_MEL = ("Eb5/.5 F5/.5 G5/1.5 Ab5/.5 G5/1 | F5/1 D5/.5 F5/.5 Bb5/2 | D6/1 C6/.5 Bb5/.5 G5/2 | "
              "Eb5/.5 G5/.5 Bb5/1 C6/2 | Ab5/1.5 G5/.5 F5/1 Eb5/1 | D5/1 F5/1 Ab5/1 G5/1 | G5/3 F5/.5 Eb5/.5")
CH1_END = "Bb4/1 Db5/1 Eb5/2"    # over Eb7 (back to the verse colour)
CH2_END = "Eb5/2 D5/2"           # over Bbsus4 Bb
FINAL_END = "Eb5/4 | r/4"        # (+2 -> F5) and a bar of breath
PIVOT_MEL = "F5/2 E5/2"          # over C7sus C7: the new key's dominant

piano = P("piano", 0, pan=0, width=1.3, level=-18, send=-6, bus="piano", jitter_ms=5,
          eq=[HighpassFilter(55), PeakFilter(300, -1.5, 1)])
violins = P("violins", 49, 21, expr_cc=2, players=2, pan=-.35, width=1.4, level=-18, send=-4, bus="strings",
            legato=.08, eq=[HighpassFilter(250), PeakFilter(3000, -2.5, 1)])
cello = P("cello", 42, 17, expr_cc=2, pan=.3, level=-21, send=-5, bus="strings", legato=.1,
          eq=[HighpassFilter(60), PeakFilter(300, -1.5, 1)])
pad = P("strings_pad", 49, 17, expr_cc=2, players=2, pan=.1, width=1.6, level=-24, send=-4, bus="strings", legato=.3,
        eq=[HighpassFilter(180), PeakFilter(2500, -2, 1)])
guitar = P("guitar", 25, sf2=GU_SF, pan=.4, width=1.2, level=-25, send=-8, bus="band", jitter_ms=4,
           eq=[HighpassFilter(150), PeakFilter(250, -2, 1)])
bass = P("bass", 33, sf2=GU_SF, width=.2, level=-23, send=-24, bus="band", jitter_ms=4, legato=-.05,
         eq=[HighpassFilter(40), LowpassFilter(4000)])
drums = kit("drums", 0, width=1.2, level=-24, send=-10, bus="drums", jitter_ms=4, eq=[HighpassFilter(40)])
KICK, SNARE, XSTICK, HHC, CRASH, RIDE = 36, 38, 37, 42, 49, 51
LOUD = {"intro": 0, "verse": 1, "chorus1": 2, "inter": 1, "chorus2": 3, "pivot": 3, "final": 4, "outro": 0}

for bar, (sec, chs, sh) in enumerate(BARS):
    span = B / len(chs)
    L = LOUD[sec]
    for ci, c in enumerate(chs):
        b0 = bar * B + ci * span
        bpc, pcs = CH[c]
        bpc, pcs = (bpc + sh) % 12, [(p + sh) % 12 for p in pcs]
        lo = nearest(bpc, n("Eb2"))
        t = sorted(nearest(p, n("Bb3")) for p in pcs[:3])  # triad: the 7ths live in the tune, not next to a root
        if sec == "outro" and bar >= START["outro"] + 2:
            if bar == START["outro"] + 2:
                for j, q in enumerate([lo, lo + 7] + t + [t[-1] + 5]):
                    piano.add(b0 + j * .2, 2 * B - j * .2, q, 56 - j * 2)
            continue
        # piano left hand: low bass + 8th broken chord (pedal change on the chord)
        arp = [lo, t[0], t[1], t[-1], t[1] + 12, t[-1], t[1], t[0]]
        for j in range(int(span * 2)):
            piano.add(b0 + j * .5, min(1.5, span - j * .5), arp[j], (60 if j == 0 else 48) + L * 3)
        if sec in ("verse",):
            for q in t[:3]:
                pad.add(b0, span, q, 58)
            cello.add(b0, span, lo + 12, 70)
        if L >= 2:
            for q in t:
                pad.add(b0, span, q + 12, 58 + L * 5)
            cello.add(b0, span, lo + 12, 66 + L * 5)
            bass.add(b0, span * .9, lo, 76 + L * 4)
        if L >= 3:
            for j in range(int(span * 2)):  # guitar 8th arpeggios
                guitar.add(b0 + j * .5, .9, [lo + 12, t[0] + 12, t[1] + 12, t[-1] + 12][j % 4], 64)
    b0 = bar * B
    if sec in ("chorus1", "chorus2", "pivot", "final"):
        drums.add(b0, .2, KICK, 70 + L * 6)
        drums.add(b0 + 2.5, .2, KICK, 60 + L * 6)
        for bb in (1, 3):
            drums.add(b0 + bb, .2, XSTICK if sec == "chorus1" else SNARE, 66 + L * 7)
        for i in range(8):
            drums.add(b0 + i * .5, .1, RIDE if L >= 4 else HHC, 54 + (10 if i % 2 == 0 else 0))
    if bar in (START["chorus2"], START["final"]):
        drums.add(b0, 3, CRASH, 90)

for sec, end in (("chorus1", CH1_END), ("chorus2", CH2_END), ("final", FINAL_END)):
    sh = 2 if sec == "final" else 0
    vel = {"chorus1": 84, "chorus2": 96, "final": 104}[sec]
    play(violins, seq(CHORUS_MEL + " | " + end, START[sec] * B, shift=sh), vel)
    if sec != "chorus1":
        play(piano, seq(CHORUS_MEL + " | " + end, START[sec] * B, shift=sh), 72)
play(piano, seq(VERSE_MEL, START["verse"] * B), 78, extend=.3)
play(violins, seq(PIVOT_MEL, START["pivot"] * B, shift=12), 96)
play(piano, seq("Eb5/1.5 F5/.5 G5/2 | F5/1.5 D5/.5 Bb4/2", START["inter"] * B), 70)
play(piano, seq("D5/2 C5/2 | E5/2 G5/2 | A5/8", START["outro"] * B), 66, extend=.5)

if __name__ == "__main__":
    S = START
    finish("acg_emotional_ballad", [piano, violins, cello, pad, guitar, bass, drums], song,
           [("verse", S["verse"], S["chorus1"]), ("chorus1", S["chorus1"], S["inter"]),
            ("chorus2", S["chorus2"], S["pivot"]), ("final", S["final"], S["outro"])],
           lead={"violins", "piano"}, beats_per_bar=B,
           hall=dict(rt_low=2.6, rt_mid=2.2, rt_high=1.2, predelay=.03, length=4.5))
