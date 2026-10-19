"""Smoke Rings — late-night lounge jazz with a slightly seasick, detuned organ underneath.
Suits: card tables, roguelike deck-builders, noir / night-city videos, cocktail-bar scenes.
D minor, 96 BPM swing, 40 bars (~1:40) + a final Dm9; with --loop a seamless loop (outro = intro).

A  | Dm9 | Dm9 | Bbmaj7 | A7b9 | Gm9 | C13 | Fmaj7 | Em7b5 A7b9 |
B  | Gm9 | C13 | Fmaj7 | Bbmaj7 | Em7b5 | A7b9 | Dm9 | A7b9 |
Form: intro 4 (Rhodes, bass, brushes) · A vibes · A' vibes · B muted trumpet · A vibes + trumpet 8vb · outro 4.
"""
# usage: <skill>/scripts/run.sh <skill>/examples/styles/lounge_jazz.py [--loop]   -> ./out/lounge_jazz/
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(SKILL / "scripts"), str(SKILL / "examples")]
LOOP = "--loop" in sys.argv  # optional seamless game loop; default: a whole piece with an ending

from pedalboard import Chorus, HighpassFilter, LowpassFilter, PeakFilter

from orch import GM_SF, GU_SF, SR, Song, n, nearest  # noqa: E402,F401
from score import P, finish, kit, play, seq, swing  # noqa: E402,F401
import numpy as np

BPM, B = 96, 4
song = Song(bpm=BPM, beats=(40 if LOOP else 41) * B, tail=4.0, seed=96)

VOICE = {"Dm9": (2, "m", "F3 A3 C4 E4"), "Bbmaj7": (10, "M", "F3 A3 Bb3 D4"), "A7b9": (9, "M", "G3 Bb3 C#4 E4"),
         "Gm9": (7, "m", "F3 A3 Bb3 D4"), "C13": (0, "M", "E3 A3 Bb3 D4"), "Fmaj7": (5, "M", "E3 G3 A3 C4"),
         "Em7b5": (4, "d", "G3 Bb3 D4")}
GUIDE = {"Dm9": "F3 C4", "Bbmaj7": "A3 D4", "A7b9": "G3 C#4", "Gm9": "F3 Bb3", "C13": "E3",
         "Fmaj7": "E3 A3", "Em7b5": "G3 D4"}
A = [["Dm9"], ["Dm9"], ["Bbmaj7"], ["A7b9"], ["Gm9"], ["C13"], ["Fmaj7"], ["Em7b5", "A7b9"]]
BS = [["Gm9"], ["C13"], ["Fmaj7"], ["Bbmaj7"], ["Em7b5"], ["A7b9"], ["Dm9"], ["A7b9"]]
FORM = [("intro", A[:4])] + [("A", A), ("A", A), ("B", BS), ("A", A), ("outro", A[:4])]
BARS = []  # (section, [(beat, dur, chord)])
for sec, bars in FORM:
    for chords in bars:
        d = B / len(chords)
        BARS.append((sec, [(i * d, d, c) for i, c in enumerate(chords)]))

MEL_A = ("r/1 E5/.5 F5/.5 A5/1.5 G5/.5 | F5/1 E5/.5 D5/.5 E5/2 | r/.5 D5/.5 F5/.5 A5/1 G5/.5 F5/1 | "
         "E5/1 C#5/.5 Bb4/.5 A4/2 | r/1 A4/.5 Bb4/.5 D5/1.5 F5/.5 | E5/1 D5/.5 C5/.5 A4/2 | "
         "r/.5 C5/.5 E5/.5 G5/.5 A5/1.5 E5/.5 | G5/.5 F5/.5 E5/1 C#5/2")
MEL_A2 = ("r/1 E5/.5 F5/.5 A5/1.5 G5/.5 | F5/1 E5/.5 D5/.5 E5/2 | r/.5 D5/.5 F5/.5 A5/1 G5/.5 F5/1 | "
          "E5/1 C#5/.5 Bb4/.5 A4/2 | Bb5/1.5 A5/.5 G5/1 F5/1 | E5/.5 F5/.5 G5/.5 A5/.5 Bb5/1 A5/1 | "
          "A5/3 r/1 | G5/.5 E5/.5 Bb4/1 C#5/1 E5/1")
MEL_B = ("D5/1.5 C5/.5 Bb4/1 A4/1 | G4/.5 A4/.5 Bb4/.5 D5/.5 E5/2 | r/1 E5/.5 F5/.5 E5/.5 C5/.5 A4/1 | "
         "D5/1.5 C5/.5 A4/2 | r/.5 Bb4/.5 D5/.5 E5/.5 G5/1.5 F5/.5 | E5/1 C#5/1 Bb4/1 G4/1 | "
         "F4/.5 A4/.5 C5/.5 E5/.5 D5/2 | E5/.5 C#5/.5 A4/1 r/2")
B_FILL = "r/2 A5/.5 G5/.5 E5/.5 C#5/.5"  # vibes answer in the last bar of B

vibes = P("vibes", 11, pan=.2, level=-18, send=-10, bus="lead", jitter_ms=4,
          eq=[HighpassFilter(250), PeakFilter(900, -1.5, 1)])
tpt = P("muted_trumpet", 59, 17, expr_cc=2, pan=-.15, level=-18.5, send=-9, bus="lead", jitter_ms=5, legato=-.05,
        eq=[HighpassFilter(250), PeakFilter(1400, -2, 1), LowpassFilter(8000)])
rhodes = P("rhodes", 4, pan=-.25, width=1.3, level=-22, send=-12, bus="keys", jitter_ms=6,
           eq=[HighpassFilter(140), PeakFilter(450, -2, 1),
               Chorus(rate_hz=0.6, depth=0.25, centre_delay_ms=7, feedback=0.0, mix=0.4)])
organ = P("organ", 16, 18, expr_cc=2, pan=.1, width=1.6, level=-31, send=-10, bus="keys", legato=.15,
          eq=[HighpassFilter(150), LowpassFilter(3500),
              Chorus(rate_hz=0.25, depth=0.5, centre_delay_ms=9, feedback=0.1, mix=0.6)])
bass = P("upright", 32, sf2=GU_SF, width=.2, level=-21, send=-24, bus="bass", jitter_ms=6, legato=-.08,
         eq=[HighpassFilter(38), PeakFilter(700, 2, 1), LowpassFilter(4500)])
drums = kit("brushes", 40, sf2=GM_SF, width=1.3, level=-25, send=-14, bus="drums", jitter_ms=6,
            eq=[HighpassFilter(40)])

KICK, RIM, SNARE, HHF, RIDE = 36, 37, 38, 44, 51


def root_of(c):
    return VOICE[c][0]


def tones(c):
    r, q, _ = VOICE[c]
    return r, (r + (3 if q in "md" else 4)) % 12, (r + (6 if q == "d" else 7)) % 12


flat = [(i, sec, b, d, c) for i, (sec, chs) in enumerate(BARS) for b, d, c in chs]
for k, (bar, sec, b, d, c) in enumerate(flat):
    b0 = bar * B + b
    nxt = flat[(k + 1) % len(flat)][4]
    r, th, f = tones(c)
    lo = nearest(r, n("E2"))
    tgt = nearest(root_of(nxt), lo)
    appr = tgt - 1 if bar % 2 else tgt + 1
    # bass: two-feel in A, walking in B and the last A
    if sec == "B" or (sec == "A" and bar >= 28):
        line = [lo, nearest(th, lo + 3), nearest(f, lo + 7), appr] if d == 4 else [lo, appr]
        for i, q in enumerate(line):
            bass.add(b0 + i, .95, q, 92 if i == 0 else 80)
    elif d == 4:
        for bb, dd, q, v in [(0, 1.9, lo, 96), (2, 1.3, nearest(f, lo + 7), 82), (3.5, .45, appr, 72)]:
            bass.add(b0 + bb, dd, q, v)
    else:
        bass.add(b0, 1.4, lo, 92)
        bass.add(b0 + 1.5, .45, appr, 72)
    # Rhodes comp (Charleston and its displacement), organ shells
    voicing = [n(q) for q in VOICE[c][2].split()]
    hits = ([(0, 1.2), (1.5, .4)] if bar % 2 == 0 else [(.5, .4), (2.5, 1.2)]) if d == 4 else [(0, 1.0)]
    if sec == "outro" and bar == 39:
        hits = [(0, 4)]
    for hb, hd in hits:
        for j, q in enumerate(voicing):
            rhodes.add(b0 + hb + j * .02, hd, q, 62 + (6 if hb == 0 else 0))
    if sec != "intro":
        for q in GUIDE[c].split():  # 3rd and 7th under the tune (C13: the 3rd only, its b7 rubs the 13th)
            organ.add(b0, d, q, 70 if sec != "B" else 80)

# drums: ride swing pattern, hi-hat foot on 2 and 4, brush swish, feathered kick
for bar, (sec, _) in enumerate(BARS):
    b0 = bar * B
    for bb, v in [(0, 70), (1, 78), (1.5, 56), (2, 70), (3, 78), (3.5, 56)]:
        drums.add(b0 + bb, .3, RIDE, v)
    for bb in (1, 3):
        drums.add(b0 + bb, .2, HHF, 62)
    if sec != "intro":
        for i in range(8):
            drums.add(b0 + i * .5, .3, SNARE, 30 + (12 if i in (2, 6) else 0))
        drums.add(b0, .2, KICK, 46)
        if bar % 4 == 3:
            drums.add(b0 + 3.5, .2, RIM, 58)
    if sec == "B":
        drums.add(b0 + 2.5, .2, KICK, 40)

# melodies
play(vibes, seq(MEL_A, 4 * B), 88, extend=.25)
play(vibes, seq(MEL_A2, 12 * B), 90, extend=.25)
play(vibes, seq(B_FILL, 27 * B), 80, extend=.25)
play(tpt, seq(MEL_B, 20 * B), 92)
play(vibes, seq(MEL_A, 28 * B), 92, extend=.25)
play(tpt, seq(MEL_A, 28 * B, shift=-12), 84)
play(vibes, seq("r/1 E5/.5 F5/.5 A5/1.5 G5/.5 | F5/1 E5/.5 D5/.5 E5/2 | r/4 | r/2 A5/2", 36 * B), 74, extend=.4)
if not LOOP:  # ending: the outro's A7b9 resolves to a held Dm9
    e = 40 * B
    for j, q in enumerate(VOICE["Dm9"][2].split()):
        rhodes.add(e + j * .03, 4, q, 66)
    for q in GUIDE["Dm9"].split():
        organ.add(e, 4, q, 64)
    bass.add(e, 4, "D2", 92)
    play(vibes, seq("A4+D5/4", e), 72)
    drums.add(e, .3, RIDE, 70)
    drums.add(e, .2, KICK, 50)
for p in (vibes, tpt, rhodes, organ, bass, drums):
    swing(p, .64)

# vinyl crackle: sparse clicks, a faint hiss
rng = np.random.default_rng(3)
N = int(song.length * SR)
crk = np.zeros(N)
idx = rng.integers(0, N, int(song.length * 9))
crk[idx] = rng.standard_normal(len(idx)) * rng.uniform(.2, 1, len(idx))
crk += rng.standard_normal(N) * .004
crk = np.stack([crk, np.roll(crk, 37)], 1).astype(np.float32)
extra = {"vinyl": (crk, dict(level=-44, send=-40, width=1.0, bus="fx",
                              eq=[HighpassFilter(1200), LowpassFilter(7000)]))}

if __name__ == "__main__":
    finish("lounge_jazz", [vibes, tpt, rhodes, organ, bass, drums], song,
           [("intro", 0, 4), ("A", 4, 12), ("A'", 12, 20), ("B", 20, 28), ("A''", 28, 36)],
           lead={"vibes", "muted_trumpet"}, beats_per_bar=B, loop=LOOP, extra=extra,
           hall=dict(rt_low=1.4, rt_mid=1.2, rt_high=.7, predelay=.015, length=3.0),
           tone=[PeakFilter(350, -1.0, .8), PeakFilter(3500, 1.0, .8)])
