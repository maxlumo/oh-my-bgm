"""Ascent — hybrid orchestral trailer cue on General MIDI SoundFonts, D minor, 92 BPM, 66 s.

Form (bars of 4/4, 0-based):
  0-3   intro   low-string ostinato, choir pp, piano, timpani roll into bar 4
  4-11  build   + violas/violins 16ths, horns theme, taiko, crescendo; one beat of silence at the end
  12-19 climax  tutti theme (horns + violins, celli an octave down), brass chords, choir ff
  20-22 final   tutti Dm hit, gong, boom, long decay, piano echo of the theme

Orchestra: General MIDI programs on one SoundFont (the default, MuseScore General with plain GM
programs, is the version the human picked). --expr switches the long strings, brass and choir to
MuseScore General's "Expr." presets, whose dynamics follow CC2 curves derived from the notes.
Hybrid layers (taiko ensemble, booms, braams, riser, swells) are synthesised in hybrid.py.

usage: <skill>/scripts/run.sh examples/trailer_ascent.py [musescore|generaluser] [--expr] [--no-hybrid]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pedalboard import (Distortion, Gain, HighpassFilter, HighShelfFilter,  # noqa: E402
                        LowpassFilter, PeakFilter)

import hybrid as hy  # noqa: E402
from orch import GM_SF, GU_SF, Part, Song, chord_tones, export, mix, n, nearest, render_parts  # noqa: E402

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")] if __name__ == "__main__" else []
SF = ARGS[0] if ARGS else "musescore"
SF2 = str(GM_SF if SF == "musescore" else GU_SF)
NO_HYBRID = __name__ == "__main__" and "--no-hybrid" in sys.argv
EXPR = SF == "musescore" and "--expr" in sys.argv  # GeneralUser GS has no "Expr." presets

# role -> (program, bank, extra Part settings); drums on channel 9 use GM drum keys
_E = dict(expr_cc=2) if EXPR else {}
_B = 17 if EXPR else 0
_L = 49 if EXPR else 48  # Expr: "Strings Slow Expr." (17-49); plain GM: Strings (0-48)
ROLES = {
    "celli_spic": (48, 0, {}), "basses_spic": (43, 0, {}), "violas_spic": (48, 0, {}),
    "violins_spic": (48, 0, {}),
    "violins_long": (_L, _B, _E), "celli_long": (_L, _B, _E), "violas_long": (_L, _B, _E),
    "basses_long": (43, _B, _E),
    "horns": (60, _B, _E), "trombones": (57, _B, _E), "tuba": (58, _B, _E), "trumpets_stac": (56, 0, {}),
    "choir": (52, _B, _E), "piano": (0, 0, {}), "tubular_bells": (14, 0, {}),
    "timpani": (47, 0, {}), "timpani_roll": (47, 0, dict(roll=.125)),
    "perc_drum": (0, 0, dict(channel=9, note_map={36: 35, 41: 38})),   # concert bass drum, snare
    "perc_cym": (0, 0, dict(channel=9, note_map={46: 52})),            # crash; "gong" -> china
    "oboe": (68, 0, {}), "flutes": (73, 0, {}), "piccolo": (72, 0, {}),
}


def P(name, **mix_settings):
    program, bank, extra = ROLES[name]
    return Part(name, program, sf2=SF2, bank=bank, **extra, **mix_settings)


song = Song(bpm=92, beats=23 * 4, tail=6.0)
B = 4  # beats per bar
INTRO, BUILD, CLIMAX, FINAL = 0, 4, 12, 20
prog = {}
for b, ch in enumerate(["Dm", "Bb", "F", "C"]):
    prog[INTRO + b] = ch
for b, ch in enumerate(["Dm", "Bb", "F", "C"] * 2):
    prog[BUILD + b] = ch
for b, ch in enumerate(["Dm", "Bb", "F", "C", "Dm", "Bb", "Gm", "A"]):
    prog[CLIMAX + b] = ch
prog[FINAL] = prog[FINAL + 1] = prog[FINAL + 2] = "Dm"

GAP = (BUILD + 7) * B + 3  # beat where everything stops before the drop


def theme(climax: bool):
    """8-bar horn theme: list of (bar offset, beat, dur, note)."""
    t = [(0, 0, 2, "A3"), (0, 2, 1, "D4"), (0, 3, 1, "E4"),
         (1, 0, 3, "F4"), (1, 3, .5, "E4"), (1, 3.5, .5, "D4"),
         (2, 0, 2, "C4"), (2, 2, 1, "F4"), (2, 3, 1, "G4"),
         (3, 0, 2, "G4"), (3, 2, 2, "E4"),
         (4, 0, 2, "A4"), (4, 2, 1, "F4"), (4, 3, 1, "D4"),
         (5, 0, 2, "Bb4"), (5, 2, 1, "A4"), (5, 3, 1, "G4")]
    if climax:
        t += [(6, 0, 2, "G4"), (6, 2, 1, "Bb4"), (6, 3, 1, "A4"),
              (7, 0, 2, "A4"), (7, 2, 1, "C#5"), (7, 3, 1, "E5")]
    else:
        t += [(6, 0, 2, "F4"), (6, 2, 1, "E4"), (6, 3, 1, "F4"),
              (7, 0, 3, "E4")]  # stops at beat 3: the gap
    return [(bar, beat, dur, n(p)) for bar, beat, dur, p in t]


ACC = [1, 0, 0, 1, 0, 0, 1, 0]  # 3+3+2 accents on 8ths

# ---------------------------------------------------------------- strings
cello_sp = P("celli_spic", players=2, pan=.4, level=-22, send=-10,
                eq=[HighpassFilter(45)], bus="strings", legato=-.1)
bass_sp = P("basses_spic", pan=.55, level=-25, send=-12,
               eq=[HighpassFilter(30)], bus="strings", legato=-.1)
viola_sp = P("violas_spic", players=2, pan=.15, level=-27, send=-9,
                eq=[HighpassFilter(120)], bus="strings", legato=-.05)
vln_sp = P("violins_spic", players=2, pan=-.5, level=-28, send=-9,
              eq=[HighpassFilter(160)], bus="strings", legato=-.05)
vln_long = P("violins_long", pan=-.45, level=-20, send=-8,
                eq=[HighpassFilter(160), PeakFilter(3200, -3.0, 1.2), LowpassFilter(12000)], bus="strings",
                legato=.08)
cello_long = P("celli_long", pan=.4, level=-22, send=-9,
                  eq=[HighpassFilter(50)], bus="strings", legato=.08)
viola_long = P("violas_long", pan=.15, level=-25, send=-9,
                  eq=[HighpassFilter(110)], bus="strings", legato=.08)
bass_long = P("basses_long", pan=.55, level=-26, send=-12,
                 eq=[HighpassFilter(30)], bus="strings", legato=.08)

for bar in range(INTRO, FINAL):
    r, _, f = chord_tones(prog[bar])
    root = nearest(r, n("D3"))
    for i in range(8):
        beat = bar * B + i * .5
        if beat >= GAP and bar < CLIMAX:
            break
        sec = 0 if bar < BUILD else 1 if bar < CLIMAX else 2
        # unaccented 8ths in the soft layer (<63), accents in the loud one: two timbres
        v = ([96, 104, 118][sec] if ACC[i] else [50, 58, 74][sec]) + (bar - BUILD) * 1.2 * (sec == 1)
        cello_sp.add(beat, .5, root, v)
        if ACC[i] or sec == 2:
            bass_sp.add(beat, .5, root - 12, v - 4)
    if bar >= BUILD:  # violas: 16th arpeggio r-5-8-5
        low = nearest(r, n("A3"))
        cyc = [low, low + ((f - r) % 12), low + 12, low + ((f - r) % 12)]
        for i in range(16):
            beat = bar * B + i * .25
            if beat >= GAP and bar < CLIMAX:
                break
            viola_sp.add(beat, .25, cyc[i % 4], (100 if i % 4 == 0 else 56) + (14 if bar >= CLIMAX else 0))
    if bar >= BUILD + 4:  # violins: 16ths 8-5-3-5 an octave higher
        r_, t_, f_ = chord_tones(prog[bar])
        top = nearest(r_, n("D5"))
        cyc = [top, nearest(f_, top - 4), nearest(t_, top - 7), nearest(f_, top - 4)]
        for i in range(16):
            beat = bar * B + i * .25
            if beat >= GAP and bar < CLIMAX:
                break
            vln_sp.add(beat, .25, cyc[i % 4], (98 if i % 4 == 0 else 54) + (12 if bar >= CLIMAX else 0))

for bar, beat, dur, p in theme(True):  # climax: violins +12, celli -12
    b0 = (CLIMAX + bar) * B + beat
    vln_long.add(b0, dur, p + 12, 112)
    cello_long.add(b0, dur, p - 12, 108)

# ---------------------------------------------------------------- brass
horns = P("horns", players=3, pan=-.3, level=-19, send=-4,
             eq=[HighpassFilter(90)], bus="brass", legato=.06)
bones = P("trombones", players=2, pan=.35, level=-23, send=-5,
             eq=[HighpassFilter(70)], bus="brass", legato=.05)
tuba = P("tuba", pan=.5, level=-26, send=-9,
            eq=[HighpassFilter(28), LowpassFilter(3000)], bus="brass", legato=.05)
tpt_st = P("trumpets_stac", players=2, pan=.2, level=-26, send=-7,
              eq=[HighpassFilter(200)], bus="brass", legato=-.05)

for bar, beat, dur, p in theme(False):
    horns.add((BUILD + bar) * B + beat, dur, p, 72 + bar * 3)
for bar, beat, dur, p in theme(True):
    horns.add((CLIMAX + bar) * B + beat, dur, p, 118)

for bar in range(CLIMAX, FINAL):
    r, t, f = chord_tones(prog[bar])
    lo = nearest(r, n("D3"))
    for q in (nearest(r, n("D3")), nearest(f, n("A3")), nearest(t, n("F3"))):
        bones.add(bar * B, 4, q, 108)
    tuba.add(bar * B, 4, nearest(r, n("D2")), 104)
    for i, a in enumerate(ACC):  # trumpet stabs on the 3+3+2 accents
        if a:
            for q in (nearest(t, n("F4")), nearest(f, n("A4"))):
                tpt_st.add(bar * B + i * .5, .4, q, 112)
del lo

# ---------------------------------------------------------------- choir, piano, bells
choir = P("choir", players=2, pan=0, width=1.6, level=-22, send=-3,
             eq=[HighpassFilter(150), PeakFilter(350, -2.5, 1.0)], bus="choir", legato=.1)
for bar in range(INTRO, FINAL):
    r, t, f = chord_tones(prog[bar])
    v = 52 if bar < BUILD else 78 if bar < CLIMAX else 112
    end = 4 if not (BUILD <= bar < CLIMAX and bar * B + 4 > GAP) else GAP - bar * B
    for q in (nearest(r, n("D3")), nearest(f, n("A3")), nearest(t, n("F4")), nearest(r, n("D4"))):
        choir.add(bar * B, end, q, v)

piano = P("piano", pan=-.1, level=-25, send=-4,
             eq=[HighpassFilter(120), LowpassFilter(9000)], bus="keys", jitter_ms=3)
for bar, beat, p, v in [(0, 0, "D5", 58), (0, 2, "A4", 50), (1, 0, "F5", 56), (1, 2, "D5", 48),
                        (2, 0, "C5", 54), (2, 2, "A4", 48), (3, 0, "E5", 56), (3, 2, "G4", 50)]:
    piano.add(bar * B + beat, 2, p, v)
for beat, p in [(0, "A4"), (1, "D5"), (2, "E5"), (3, "F5")]:  # echo of the theme after the hit
    piano.add((FINAL + 2) * B + beat, 1.5 if p != "F5" else 8, p, 50)

bells = P("tubular_bells", pan=-.2, level=-27, send=-5,
             eq=[HighpassFilter(200)], bus="perc")
for bar in (CLIMAX, CLIMAX + 4, FINAL):
    bells.add(bar * B, 4, "D5", 110)

# ---------------------------------------------------------------- percussion
timp = P("timpani", pan=-.1, level=-21, send=-6,
            eq=[HighpassFilter(38)], bus="perc", jitter_ms=4)
timp_roll = P("timpani_roll", pan=-.1, level=-24, send=-8,
                 eq=[HighpassFilter(38)], bus="perc",
                 auto=[(INTRO * B + 12, -18), (BUILD * B, 0), (BUILD * B + .5, 0),
                       ((BUILD + 7) * B, -16), (GAP, 0), (GAP + .5, 0),
                       (FINAL * B + 1, -2), ((FINAL + 2) * B + 2, -22)])
perc = P("perc_drum", pan=0, width=1.2, level=-25, send=-6,
         eq=[HighpassFilter(30)], bus="perc", jitter_ms=3)
cym = P("perc_cym", pan=0, width=1.4, level=-26, send=-5,
        eq=[HighpassFilter(120)], bus="perc", jitter_ms=3)

timp_roll.add(INTRO * B + 12, 4, "D2", 110)  # into the build
timp_roll.add((BUILD + 7) * B, 3, "A2", 115)  # into the gap
timp_roll.add(FINAL * B + 1, 9, "D2", 120)
for bar in range(BUILD, FINAL):
    r, _, f = chord_tones(prog[bar])
    lo = nearest(r, n("D2") if r in (2, 0, 10) else n("G2"))
    if bar < CLIMAX:
        if bar * B < GAP:
            timp.add(bar * B, 1, lo, 80 + (bar - BUILD) * 4)
    else:
        for beat, v in [(0, 125), (1.5, 100), (2, 112), (3, 108), (3.5, 96), (3.75, 104)]:
            timp.add(bar * B + beat, .5, lo if beat != 3.5 else nearest(f, lo + 4), v)
timp.add(FINAL * B, 2, "D2", 127)

cym.add(CLIMAX * B, 4, 49, 120)  # crash
cym.add((CLIMAX + 4) * B, 4, 49, 115)
cym.add(FINAL * B, 4, 49, 127)
cym.add(FINAL * B, 8, 46, 127)  # gong
for bar in range(CLIMAX, FINAL + 1):
    perc.add(bar * B, 1, 36, 120)  # concert bass drum
perc.add((FINAL - 1) * B, 4, 41, 100)  # snare roll into the final hit

# ---------------------------------------------------------------- hybrid layers
t = song.t
L = song.length
taiko = hy.Layer(L)
for bar in range(BUILD, FINAL):
    pat = [0, 2.5, 3] if bar < CLIMAX else [0, .75, 1.5, 2, 2.5, 3, 3.5, 3.75]
    for k, beat in enumerate(pat):
        b0 = bar * B + beat
        if bar < CLIMAX and b0 >= GAP:
            continue
        v = (.55 + .03 * (bar - BUILD)) if bar < CLIMAX else (1.0 if beat in (0, 2) else .75)
        taiko.at(t(b0), hy.ensemble_hit(v, seed=bar * 16 + k))
taiko.at(t(FINAL * B), hy.ensemble_hit(1.0, seed=999, players=6))

booms = hy.Layer(L)
for bar in (INTRO, CLIMAX, FINAL):
    booms.at(t(bar * B), hy.boom(1.0 if bar else .7, seed=bar))

fx_layer = hy.Layer(L)
fx_layer.at(t(BUILD * B), hy.reverse_swell(2.0, 1), end=True, gain=.7)
fx_layer.at(t(GAP), hy.riser(t(B * 4) - t(1), 2), end=True)  # cuts with the gap
fx_layer.at(t(CLIMAX * B), hy.reverse_swell(2.5, 3), end=True)  # fills the gap into the drop
fx_layer.at(t(FINAL * B), hy.reverse_swell(3.0, 4), end=True)

braams = hy.Layer(L)
for bar, notes in [(CLIMAX, (38, 45, 50)), (CLIMAX + 4, (38, 45, 50)), (FINAL, (26, 38, 45, 50))]:
    braams.at(t(bar * B), hy.braam(4.5 if bar == FINAL else 3.0, notes, seed=bar))

extra = {
    "taiko": (taiko.buf, dict(pan=0, width=1.0, level=-20, send=-12,
                              eq=[HighpassFilter(35)], bus="hybrid")),
    "booms": (booms.buf, dict(pan=0, width=1.0, level=-25, send=-40, bus="hybrid")),
    "braams": (braams.buf, dict(pan=0, width=1.2, level=-23, send=-6,
                                eq=[HighpassFilter(35), LowpassFilter(6000)], bus="hybrid")),
    "fx": (fx_layer.buf, dict(pan=0, width=1.0, level=-27, send=-12,
                              eq=[HighpassFilter(150)], bus="fx")),
}

# ---------------------------------------------------------------- woodwinds
oboe = P("oboe", pan=.05, level=-24, send=-4,
            eq=[HighpassFilter(200)], bus="winds", legato=.05, jitter_ms=4)
for bar, beat, dur, p in [(2, 0, 1, "A4"), (2, 1, 1, "D5"), (2, 2, 1, "E5"), (2, 3, 1, "F5"),
                          (3, 0, 3.5, "E5")]:  # the theme's head, foreshadowed in the intro
    oboe.add(bar * B + beat, dur, p, 70)
flute = P("flutes", players=2, pan=-.15, level=-27, send=-4,
             eq=[HighpassFilter(250)], bus="winds", legato=.06)
picc = P("piccolo", pan=-.2, level=-30, send=-4,
            eq=[HighpassFilter(400), LowpassFilter(11000)], bus="winds", legato=.06)
for bar, beat, dur, p in theme(True):
    if bar >= 4:  # second half of the climax gets the top octave
        flute.add((CLIMAX + bar) * B + beat, dur, p, 110)
        picc.add((CLIMAX + bar) * B + beat, dur, p + 12, 100)

# ---------------------------------------------------------------- final tutti hit (Dm)
HIT, HOLD = FINAL * B, 8
for part, notes, v in [
    (vln_long, ["D5", "A5"], 120), (viola_long, ["F4", "A4"], 115), (cello_long, ["D3", "A3"], 118),
    (bass_long, ["D2"], 118), (horns, ["D4", "F4", "A4"], 124), (bones, ["D3", "A3", "F3"], 120),
    (tuba, ["D2"], 118), (choir, ["D3", "A3", "F4", "D4"], 120),
]:
    for p in notes:
        part.add(HIT, HOLD, p, v)
for p in ("D5", "F5", "A4"):
    tpt_st.add(HIT, .6, p, 124)
for part in (vln_long, viola_long, cello_long, bass_long, horns, bones, tuba, choir):
    part.auto = [(HIT + 1, 0), (HIT + HOLD + 2, -12)]  # tutti dies away under the piano echo

PARTS = [cello_sp, bass_sp, viola_sp, vln_sp, vln_long, cello_long, viola_long, bass_long,
         horns, bones, tuba, tpt_st, choir, piano, bells, timp, timp_roll, perc, cym,
         oboe, flute, picc]

# intro sits lower, the build ramps up, and one beat of real silence (reverb cut too) before
# the drop; only the "fx" bus (reverse swell) plays through the gap
DUCK = [(0, -7), (BUILD * B - .01, -7), (BUILD * B, -3.5), ((BUILD + 7) * B, 0),
        (GAP - .02, 0), (GAP + .2, -60), (CLIMAX * B - .03, -60), (CLIMAX * B, 0)]
TONE = [PeakFilter(700, -2.5, 0.7), PeakFilter(3500, 1.5, 0.8),
        HighShelfFilter(cutoff_frequency_hz=10000, gain_db=2.5)]
BUS_FX = {
    "strings": [PeakFilter(250, -2.0, 1.0)],
    "brass": [PeakFilter(250, -1.5, 1.0)],
    "hybrid": [Distortion(drive_db=5), Gain(-3)],
    "perc": [Distortion(drive_db=3), Gain(-2)],
}
SIDECHAIN = (("hybrid",), ("strings", "brass", "choir", "winds"), 2.5)
HALL = dict(rt_low=3.6, rt_mid=3.0, rt_high=1.6, predelay=0.03, length=6.0)

if __name__ == "__main__":
    import time
    name = f"ascent-{SF}" + ("-expr" if EXPR else "") + ("-no-hybrid" if NO_HYBRID else "")
    out = Path.cwd() / "out" / name
    t0 = time.time()
    stems = render_parts(PARTS, song, out / "_render")
    t1 = time.time()
    master, placed, buses, levels = mix(PARTS, stems, song, extra=None if NO_HYBRID else extra,
                                        lufs=-14.0, hall=HALL, duck=DUCK, tone=TONE, bus_fx=BUS_FX,
                                        sidechain=None if NO_HYBRID else SIDECHAIN)
    rep = export(master, buses, out, name,
                 meta={"render_s": round(t1 - t0, 1), "mix_s": round(time.time() - t1, 1),
                       "soundfont": SF2,
                       "onset_ms": render_parts.onsets, "stem_lufs_raw": levels})
    print(rep)
