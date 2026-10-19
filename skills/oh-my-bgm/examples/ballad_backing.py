"""Night Train: a Mandarin pop ballad backing track, G major, 80 BPM, 66 s + tail.

Everything here is General MIDI on a SoundFont through FluidSynth (MuseScore General by default),
using its extra banks: bank 8 Mellow Grand Piano, bank 17 "Expr." strings whose dynamics follow
CC2 curves, a GM drum kit, steel guitar strums, fingered bass, warm pad, music box.

Form (bars, 0-based):  0-3 intro | 4-11 verse | 12-19 chorus | 20-21 outro
This file renders the instrumental and per-bus stems.

usage: <skill>/scripts/run.sh examples/ballad_backing.py [musescore|generaluser]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from pedalboard import HighpassFilter, HighShelfFilter, LowpassFilter, PeakFilter  # noqa: E402

from orch import LIBS, Part, Song, chord_tones, export, mix, n, nearest, render_parts  # noqa: E402

SOUNDFONTS = {"musescore": str(LIBS / "MuseScore_General.sf3"),
              "generaluser": str(LIBS / "GeneralUser-GS.sf2")}
SF = sys.argv[1] if len(sys.argv) > 1 and __name__ == "__main__" else "musescore"
SF2 = SOUNDFONTS[SF]
EXPR = SF == "musescore"  # GeneralUser has no CC2 "Expr." banks

song = Song(bpm=80, beats=22 * 4, tail=5.0, seed=11)
B = 4
INTRO, VERSE, CHORUS, OUTRO = 0, 4, 12, 20
CH = {}
for i, c in enumerate(["G", "D", "Em", "C"]):
    CH[INTRO + i] = c
for i, c in enumerate(["G", "D", "Em", "C", "G", "D", "C", "D"]):
    CH[VERSE + i] = c
for i, c in enumerate(["C", "D", "G", "Em", "C", "D", "G", "G"]):
    CH[CHORUS + i] = c
CH[OUTRO], CH[OUTRO + 1] = "C", "G"
TONES = {"G": (7, 11, 2), "D": (2, 6, 9), "Em": (4, 7, 11), "C": (0, 4, 7), "Bm": (11, 2, 6)}


def tones(c):
    return TONES[c]


def S(name, program, bank=0, **kw):
    return Part(name, program, sf2=SF2, bank=bank, **kw)


piano = S("piano", 0, bank=8 if SF == "musescore" else 0, pan=-.15, level=-20, send=-12,
          eq=[HighpassFilter(70), PeakFilter(300, -2, 1)], bus="keys", jitter_ms=4)
bass = S("bass", 33, pan=0, width=.3, level=-22, send=-30, eq=[HighpassFilter(35), LowpassFilter(5000)],
         bus="rhythm", jitter_ms=4)
strings = S("strings", 49, bank=17 if EXPR else 0, players=2, pan=.1, width=1.4, level=-24, send=-8,
            eq=[HighpassFilter(150), PeakFilter(2500, -2, 1)], bus="strings", legato=.1)
guitar = S("guitar", 25, pan=.45, level=-25, send=-14, eq=[HighpassFilter(140), PeakFilter(400, -3, 1)],
           bus="rhythm", jitter_ms=3)
pad = S("pad", 89, pan=0, width=1.6, level=-30, send=-10, eq=[HighpassFilter(200), LowpassFilter(6000)],
        bus="keys", legato=.2)
musicbox = S("music_box", 10, pan=-.4, level=-29, send=-6, eq=[HighpassFilter(500)], bus="keys")
drums = S("drums", 0, channel=9, pan=0, width=1.0, level=-21, send=-16, eq=[HighpassFilter(30)],
          bus="drums", jitter_ms=3)

# ---------------------------------------------------------------- piano
for bar in range(INTRO, OUTRO + 2):
    r, t, f = tones(CH[bar])
    root = nearest(r, n("G3"))
    if bar < CHORUS or bar >= OUTRO:  # flowing 8th arpeggio: 1-5-8-10-8-5-...
        pat = [nearest(r, n("G2")), nearest(f, n("D3")), root, nearest(t, n("B3")),
               nearest(r, n("G4")), nearest(t, n("B3")), root, nearest(f, n("D3"))]
        vel = 48 if bar < VERSE else 58
        if bar == OUTRO + 1:
            for p in pat[:4]:
                piano.add(bar * B, 6, p, 54)
            continue
        for i, p in enumerate(pat):
            piano.add(bar * B + i * .5, .9, p, vel + (8 if i == 0 else 0) - (i % 2) * 4)
    else:  # chorus: half-note chords + top line in 8ths
        for beat in (0, 2):
            for p in (nearest(r, n("G2")), nearest(r, n("G3")), nearest(t, n("B3")), nearest(f, n("D4"))):
                piano.add(bar * B + beat, 1.9, p, 66 if beat == 0 else 58)
        for i in range(8):
            if i % 2:
                piano.add(bar * B + i * .5, .45, nearest(t if i % 4 == 1 else f, n("D5")), 50)

# ---------------------------------------------------------------- bass
for bar in range(VERSE, OUTRO + 2):
    r, t, f = tones(CH[bar])
    lo = nearest(r, n("G1") if r in (7, 9, 11) else n("D2"))
    if bar >= OUTRO:
        bass.add(bar * B, 4 if bar == OUTRO else 6, lo, 80)
    elif bar < CHORUS:
        for beat, d, v in [(0, 1.4, 86), (1.5, .5, 64), (2, 1.9, 80)]:
            bass.add(bar * B + beat, d, lo, v)
    else:
        for beat, d, p, v in [(0, .9, lo, 92), (1, .45, lo, 70), (1.5, .45, lo + 12, 66),
                              (2, .9, lo, 86), (3, .45, nearest(f, lo + 5), 74), (3.5, .45, lo, 70)]:
            bass.add(bar * B + beat, d, p, v)

# ---------------------------------------------------------------- strings (Expr: CC2 swells)
curve = []
for bar in range(VERSE, OUTRO + 2):
    r, t, f = tones(CH[bar])
    v = 70 if bar < CHORUS else 92
    voicing = (nearest(r, n("G3")), nearest(t, n("B3")), nearest(f, n("D4"))) if bar < CHORUS else \
        (nearest(r, n("G3")), nearest(f, n("D4")), nearest(t, n("B4")), nearest(r, n("G5")))
    for p in voicing:
        strings.add(bar * B, 4 if bar < OUTRO + 1 else 7, p, v)
    lo, hi = (38, 70) if bar < CHORUS else (72, 108)
    if bar == OUTRO + 1:
        curve += [(bar * B, 80), (bar * B + 7, 10)]
    else:  # swell inside every bar, a little louder towards the chorus
        lift = (bar - VERSE) * 3 if bar < CHORUS else 0
        curve += [(bar * B, lo + lift), (bar * B + 2.5, hi + lift), (bar * B + 3.9, lo + 10 + lift)]
if EXPR:
    strings.curves = {2: [(b, min(127, max(0, v))) for b, v in curve]}

# ---------------------------------------------------------------- guitar strums (chorus)
for bar in range(CHORUS, OUTRO):
    r, t, f = tones(CH[bar])
    shape = sorted({nearest(r, n("G2")), nearest(f, n("D3")), nearest(r, n("G3")), nearest(t, n("B3")),
                    nearest(f, n("D4")), nearest(r, n("G4"))})
    for k, (beat, down, v) in enumerate([(0, 1, 84), (1, 1, 62), (1.5, 0, 56), (2.5, 0, 58), (3, 1, 70),
                                         (3.5, 0, 54)]):
        strum = shape if down else shape[::-1][:4]
        for j, p in enumerate(strum):  # ~12 ms between strings
            guitar.add(bar * B + beat + j * .016, .45, p, v - j * 2)

# ---------------------------------------------------------------- pad + music box
for bar in range(INTRO, OUTRO + 2):
    r, t, f = tones(CH[bar])
    for p in (nearest(r, n("G3")), nearest(t, n("B3")), nearest(f, n("D4"))):
        pad.add(bar * B, 4, p, 40 if bar < CHORUS else 52)
for bar in (CHORUS, CHORUS + 2, CHORUS + 4, CHORUS + 6):
    r, t, f = tones(CH[bar])
    for i, p in enumerate((nearest(r, n("G5")), nearest(f, n("D6")), nearest(t, n("B5")))):
        musicbox.add(bar * B + 2 + i * .5, 1, p, 64)

# ---------------------------------------------------------------- drums (GM kit)
KICK, RIM, SNARE, HHC, HHO, CRASH, RIDE, TOM_H, TOM_M, TOM_L, SHAKER = 36, 37, 38, 42, 46, 49, 51, 50, 47, 45, 70
for bar in range(VERSE, OUTRO):
    b0 = bar * B
    if bar < CHORUS:
        for beat in (0, 2.5):
            drums.add(b0 + beat, .25, KICK, 84)
        for beat in (1, 3):
            drums.add(b0 + beat, .25, RIM, 70)
        for i in range(8):
            drums.add(b0 + i * .5, .2, SHAKER, 44 + (10 if i % 2 == 0 else 0))
    else:
        for beat in (0, 1.5, 2, 3.5):
            drums.add(b0 + beat, .25, KICK, 100 if beat in (0, 2) else 80)
        for beat in (1, 3):
            drums.add(b0 + beat, .25, SNARE, 98)
        for i in range(8):
            drums.add(b0 + i * .5, .2, HHC, 60 + (14 if i % 2 == 0 else 0))
        if bar in (CHORUS, CHORUS + 4):
            drums.add(b0, 2, CRASH, 96)
for i, (beat, p) in enumerate([(3, TOM_H), (3.25, TOM_H), (3.5, TOM_M), (3.75, TOM_L)]):  # fill
    drums.add((CHORUS - 1) * B + beat, .25, p, 84 + i * 4)
drums.add(OUTRO * B, 3, CRASH, 84)
drums.add(OUTRO * B, .5, KICK, 90)

PARTS = [piano, bass, strings, guitar, pad, musicbox, drums]
HALL = dict(rt_low=1.8, rt_mid=1.6, rt_high=0.9, predelay=0.025, length=3.5)
TONE = [PeakFilter(250, -1.5, 0.8), HighShelfFilter(cutoff_frequency_hz=10000, gain_db=1.5)]


def render(out_dir: Path, name: str, lufs=-16.0):
    stems = render_parts(PARTS, song, out_dir / "_render")
    master, placed, buses, levels = mix(PARTS, stems, song, lufs=lufs, hall=HALL, tone=TONE)
    return export(master, buses, out_dir, name, meta={"soundfont": SF2, "stem_lufs_raw": levels}), buses


if __name__ == "__main__":
    out = Path.cwd() / "out" / "song01" / SF
    rep, _ = render(out, f"song01-backing-{SF}")
    print({k: rep[k] for k in ("file", "seconds", "lufs", "tp", "lra")})
