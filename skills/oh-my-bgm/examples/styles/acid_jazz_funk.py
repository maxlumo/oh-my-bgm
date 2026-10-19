"""Neon Alley — stylish acid-jazz funk. Suits: city life, fashion / product showcases, urban
vlogs, menus and hideouts in games. F minor (dorian), 112 BPM, 16ths pushed slightly (swing 0.55),
44 bars (~1:34) + a final Fm9 hit; with --loop a seamless loop.

A  | Fm9 | Bb13 | Fm9 | Bb13 | Dbmaj9 | Eb13 | C7#9 | C7#9 |
B  | Dbmaj9 | C7#9 | Fm9 | Ebm9 Ab13 | Dbmaj9 | Bb13 | Gm7b5 | C7#9 |
Form: intro 4 (drums, bass, Rhodes) · A alto sax · A sax + flute 8va, string stabs, scratch guitar ·
B flute over strings · break 4 (bass, drums, guitar, sax calls) · A tutti with brass · outro 4 (= intro).
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/acid_jazz_funk.py [--loop]   -> ./out/acid_jazz_funk/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv  # optional seamless game loop; default: a whole piece with an ending

from pedalboard import HighpassFilter, LowpassFilter, PeakFilter  # noqa: E402

from orch import GM_SF, GU_SF, Song, n, nearest  # noqa: E402
from score import P, finish, kit, play, seq, swing  # noqa: E402

BPM, B = 112, 4
song = Song(bpm=BPM, beats=(44 if LOOP else 45) * B, tail=3.0, seed=112)

# chord -> (bass pitch class, Rhodes voicing)
V = {"Fm9": (5, "Ab3 C4 Eb4 G4"), "Bb13": (10, "Ab3 C4 D4 G4"), "Dbmaj9": (1, "F3 Ab3 C4 Eb4"),
     "Eb13": (3, "G3 C4 Db4 F4"), "C7#9": (0, "E3 Bb3 Eb4 Ab4"), "Ebm9": (3, "Gb3 Bb3 Db4 F4"),
     "Ab13": (8, "Gb3 Bb3 C4 F4"), "Gm7b5": (7, "F3 Bb3 Db4")}
VAMP = [["Fm9"], ["Bb13"], ["Fm9"], ["Bb13"]]
CA = VAMP + [["Dbmaj9"], ["Eb13"], ["C7#9"], ["C7#9"]]
CB = [["Dbmaj9"], ["C7#9"], ["Fm9"], ["Ebm9", "Ab13"], ["Dbmaj9"], ["Bb13"], ["Gm7b5"], ["C7#9"]]
FORM = [("intro", VAMP), ("A1", CA), ("A2", CA), ("B", CB), ("break", VAMP), ("A3", CA), ("outro", VAMP)]
BARS = [(sec, chs) for sec, bars in FORM for chs in bars]

SAX_A = ("r/.5 C5/.25 Eb5/.25 F5/.5 Ab5/.5 G5/.75 F5/.25 Eb5/.5 C5/.5 | D5/1 r/.5 F5/.25 G5/.25 Ab5/1 G5/.5 F5/.5 | "
         "r/.5 C5/.25 Eb5/.25 F5/.5 Ab5/.5 Bb5/.75 Ab5/.25 G5/.5 F5/.5 | G5/1.5 F5/.5 D5/1 r/1 | "
         "r/.5 Ab4/.5 C5/.5 Eb5/.5 F5/1 Eb5/.5 C5/.5 | Db5/.75 C5/.25 Bb4/.5 G4/.5 Bb4/1 C5/1 | "
         "E5/.5 Eb5/.5 C5/.5 Bb4/.5 Ab4/1 G4/1 | E4/.5 G4/.5 Bb4/.5 Db5/.5 E5/2")
FLUTE_B = ("F5/1.5 Eb5/.5 C5/1 Ab4/1 | Bb4/.5 C5/.5 Eb5/.5 E5/.5 G5/2 | Ab5/1.5 G5/.5 F5/.5 Eb5/.5 C5/1 | "
           "Db5/.5 Eb5/.5 F5/.5 Gb5/.5 F5/1 Eb5/1 | F5/1 Ab5/1 C6/2 | Ab5/1 G5/.5 F5/.5 D5/2 | "
           "Db5/1 F5/1 Bb5/1.5 Ab5/.5 | G5/.5 E5/.5 Eb5/.5 C5/.5 Bb4/1 r/1")
SAX_CALLS = "r/2 F5/.25 Ab5/.25 F5/.5 Eb5/.5 C5/.5 | r/4 | r/2 Ab5/.25 Bb5/.25 Ab5/.5 F5/.5 Eb5/.5 | r/1 C5/.5 F5/2.5"

sax = P("alto_sax", 65, 17, expr_cc=2, pan=-.1, level=-16.5, send=-10, bus="lead", jitter_ms=4, legato=-.04,
        eq=[HighpassFilter(220), PeakFilter(1800, -2, 1), LowpassFilter(9000)])
flute = P("flute", 73, 17, expr_cc=2, pan=.2, level=-17, send=-9, bus="lead", jitter_ms=4, legato=-.03,
          eq=[HighpassFilter(350)])
rhodes = P("rhodes", 4, pan=-.3, width=1.3, level=-21, send=-13, bus="keys", jitter_ms=4,
           eq=[HighpassFilter(140), PeakFilter(450, -2, 1)])
guitar = P("scratch_guitar", 28, sf2=GU_SF, pan=.45, level=-27, send=-16, bus="keys", jitter_ms=3,
           eq=[HighpassFilter(300), PeakFilter(1500, 2, 1)])
stabs = P("string_stabs", 48, players=2, pan=.3, width=1.5, level=-24, send=-8, bus="strings", jitter_ms=4,
          legato=-.05, eq=[HighpassFilter(250), PeakFilter(3000, -2, 1)])
pad = P("strings_pad", 49, 17, expr_cc=2, players=2, pan=-.1, width=1.6, level=-27, send=-6, bus="strings",
        legato=.15, eq=[HighpassFilter(220)])
brass = P("brass", 61, 17, expr_cc=2, pan=.1, width=1.3, level=-24, send=-8, bus="brass", jitter_ms=3, legato=-.05,
          eq=[HighpassFilter(180), PeakFilter(2500, -2, 1)])
bass = P("bass", 33, sf2=GU_SF, width=.2, level=-19.5, send=-30, bus="bass", jitter_ms=3, legato=-.04,
         eq=[HighpassFilter(38), PeakFilter(900, 2.5, 1), LowpassFilter(5000)])
drums = kit("drums", 0, width=1.2, level=-20, send=-17, bus="drums", jitter_ms=3, eq=[HighpassFilter(35)])
KICK, SNARE, HHC, HHO, CRASH, RIDE_BELL, TOM_H, TOM_L = 36, 38, 42, 46, 49, 53, 48, 45

flat = [(bar, sec, ci, len(chs), c) for bar, (sec, chs) in enumerate(BARS) for ci, c in enumerate(chs)]
for k, (bar, sec, ci, nch, c) in enumerate(flat):
    span = B / nch
    b0 = bar * B + ci * span
    root, voicing = V[c]
    lo = nearest(root, n("F2"))
    nxt = nearest(V[flat[(k + 1) % len(flat)][4]][0], lo)
    # bass: syncopated 16ths with octave pops and a chromatic approach
    line = [(0, .45, lo, 110), (.75, .2, lo + 12, 82), (1.5, .45, lo + 7, 96), (2, .2, lo + 10, 88),
            (2.5, .45, lo, 102), (3.25, .2, lo + 12, 86), (3.5, .45, nxt + (1 if bar % 2 else -1), 92)]
    if nch == 2:
        line = [(0, .45, lo, 108), (.75, .2, lo + 12, 82), (1.5, .45, nxt - 1, 90)]
    if sec == "break" and bar % 2 == 1:
        line = line[:4] + [(3, .2, lo + 12, 90), (3.25, .2, lo + 10, 86), (3.5, .45, lo + 7, 92)]
    for bb, d, q, v in line:
        bass.add(b0 + bb, d, q, v)
    vo = [n(q) for q in voicing.split()]
    # Rhodes: two alternating syncopated comp cells (rests out in the break)
    if sec != "break":
        cell = [(.75, .25), (1.5, .5), (2.75, .25), (3.5, .4)] if bar % 2 == 0 else [(0, .5), (1.75, .25), (2.5, .9)]
        if nch == 2:
            cell = [(0, .5), (1.5, .4)]
        for hb, hd in cell:
            for j, q in enumerate(vo):
                rhodes.add(b0 + hb + j * .012, hd, q, 64 + (8 if hb in (0, 1.5, 3.5) else 0))
    # scratch guitar: muted 16ths on the top two notes
    if sec in ("A2", "B", "break", "A3"):
        for i in range(int(span * 4)):
            if i % 4 in (1, 3) or i % 8 == 6:
                for q in vo[-2:]:
                    guitar.add(b0 + i * .25, .12, q + 12, 58 + (18 if i % 8 == 6 else 0))
    # string (and brass) stabs, every other bar: an anticipation on 4& and a hit on 2&
    if sec in ("A2", "A3") and bar % 2 == 0 and nch == 1:
        for q in vo:
            stabs.add(b0 + 1.5, .3, q + 12, 92)
            stabs.add(b0 + 3.5, .45, q + 12, 100)
            if sec == "A3":
                brass.add(b0 + 1.5, .3, q + 12, 96)
                brass.add(b0 + 3.5, .45, q + 12, 104)
    if sec == "B":
        for q in vo[:3]:
            pad.add(b0, span, q + 12, 72)

# drums: kick and snare backbeat with ghost notes, 16th hats, open hat on 4&, fills every 4 bars
for bar, (sec, _) in enumerate(BARS):
    b0 = bar * B
    for bb, v in [(0, 108), (1.75, 82), (2.5, 98)] + ([(3.75, 76)] if bar % 2 else []):
        drums.add(b0 + bb, .2, KICK, v)
    for bb in (1, 3):
        drums.add(b0 + bb, .2, SNARE, 100)
    if sec != "intro" or bar >= 2:
        for bb in (.75, 2.25, 3.25):
            drums.add(b0 + bb, .15, SNARE, 34)
    for i in range(16):
        if i == 14:
            drums.add(b0 + i * .25, .3, HHO, 76)
        elif i != 15:
            drums.add(b0 + i * .25, .1, HHC, 74 if i % 2 == 0 else 50)
    if bar % 4 == 3 and sec not in ("outro",):
        for j, (q, v) in enumerate([(SNARE, 70), (SNARE, 78), (TOM_H, 86), (TOM_L, 92)]):
            drums.add(b0 + 3 + j * .25, .2, q, v)
    if bar in (4, 12, 20, 32):
        drums.add(b0, 2, CRASH, 96)

play(sax, seq(SAX_A, 4 * B), 92)
play(sax, seq(SAX_A, 12 * B), 94)
play(flute, seq(SAX_A, 12 * B, shift=12), 74)
play(flute, seq(FLUTE_B, 20 * B), 108)
play(sax, seq(SAX_CALLS, 28 * B), 92)
play(sax, seq(SAX_A, 32 * B), 98)
play(flute, seq(SAX_A, 32 * B, shift=12), 72)
if not LOOP:  # ending: one Fm9 hit on the downbeat, let it ring
    e = 44 * B
    for q in V["Fm9"][1].split():
        rhodes.add(e, 3, q, 76)
        stabs.add(e, .6, n(q) + 12, 100)
        brass.add(e, .6, n(q) + 12, 104)
    bass.add(e, 2, "F1", 110)
    play(sax, seq("F5/2", e), 96)
    for q, v in ((KICK, 112), (CRASH, 104)):
        drums.add(e, 2, q, v)
for p in (sax, flute, rhodes, guitar, stabs, brass, bass, drums):
    swing(p, .55, unit=.25)

if __name__ == "__main__":
    finish("acid_jazz_funk", [sax, flute, rhodes, guitar, stabs, pad, brass, bass, drums], song,
           [("intro", 0, 4), ("A1", 4, 12), ("A2", 12, 20), ("B", 20, 28), ("break", 28, 32), ("A3", 32, 40)],
           lead={"alto_sax", "flute"}, beats_per_bar=B, loop=LOOP,
           hall=dict(rt_low=1.2, rt_mid=1.1, rt_high=.7, predelay=.015, length=2.6),
           bus_fx={"keys": [PeakFilter(700, -1.5, 1)]},
           sidechain=(("drums",), ("keys", "strings"), 1.0))
