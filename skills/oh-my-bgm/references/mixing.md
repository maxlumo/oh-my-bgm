# Mixing and expression

## 1. Starting values (from the examples; adjust by ear)

`level` is a track's own target LUFS (measured only where it sounds); the master then brings the whole piece to `lufs=`, so only the relative values matter.

| Role | level | pan | send (dB to hall) | EQ |
|---|---|---|---|---|
| Melody (horn, long violin, piano theme, sax, flute) | -16 ~ -20 | by seating | -4 ~ -8 | HPF 70-250 Hz; if harsh, -2 ~ -3 dB near 3 kHz |
| Sustained harmony (strings, choir, pad) | -22 ~ -30 | 0, `width` 1.3-1.6 | -3 ~ -10 | HPF 120-200 Hz; -2 ~ -2.5 dB at 300-350 Hz against mud |
| Short notes, arpeggios (spiccato, broken piano chords, comping) | -20 ~ -28 | spread left/right | -9 ~ -12 | HPF by register |
| Bass, low cello | -20 ~ -26 | 0 ~ +0.5, `width` 0.2-0.3 | -12 ~ -30 | HPF 30-45 Hz, LPF 3-5 kHz |
| Drum kit, timpani | -19 ~ -25 | 0 | -6 ~ -16 | HPF 30-45 Hz |
| Cymbals, bells, music box | -26 ~ -30 | slightly off centre | -5 ~ -6 | HPF 200-500 Hz |

Orchestra seating (audience view): violins -0.45, violas +0.15, celli +0.4, basses +0.55; horns -0.3, trumpets +0.2, trombones +0.35, tuba +0.5; timpani -0.1. `players=2-3` splits a part into several players, each slightly detuned, late and panned: thicker sections, and fast repeated notes sound less like a machine gun.

## 2. Space: `hall=`

`hall_ir()` synthesises a stereo hall with separate low / mid / high decay times and early reflections.

| Style | rt_low / rt_mid / rt_high (s) | predelay | length |
|---|---|---|---|
| Trailer, epic orchestra | 3.6 / 3.0 / 1.6 | 0.03 | 6.0 |
| Ballad, sad piano, neo-classical, landscape | 2.4-3.2 / 2.1-2.8 / 1.1-1.6 | 0.025-0.03 | 4.0-5.0 |
| Pop, explainer, chamber | 1.5-1.9 / 1.3-1.7 / 0.8-1.0 | 0.02 | 3.0-3.5 |
| Jazz, bossa, lo-fi, folk, brass band | 1.2-1.6 / 1.0-1.4 / 0.6-0.8 | 0.012-0.018 | 2.4-3.0 |

**Depth, echo and the stereo stage** (`mix(halls=...)`, `Part.sends`, `Part.spread`). One hall puts everything in one place. For depth, give the piece three planes:
- Front (solo voices): moderately dry into a main hall with a long predelay (0.03 s) so the attack stays clear; a little valley echo for winds (`sends={"echo": -15 to -19}`).
- Middle (zither, pipa, strings): the main hall only.
- Back (drums, horns, drones, a voice "far away"): extra send into a far, darker space, e.g. `halls={"far": dict(rt_low=4.0, rt_mid=3.5, rt_high=1.5, predelay=.012, length=7.5, hp=140, lp=6000)}`, plus a low-pass on the part itself (4-5.5 kHz). Moving one voice from far (prelude) to near (theme) is itself a spatial event.
- Echo: `"echo": dict(echo=dict(time=1.0, repeats=3, feedback=.42, spread=.6, lp=3500), hp=350, lp=6500, to_hall=-6)`. The first repeat comes from the right: pan the voice that calls left of centre and the echo answers across the field.
- Left and right: pan by role (zither left, pipa and dulcimer right, horns left-back, celli right) and spread every plucked instrument across its strings with `spread` (zither 0.9, dulcimer 1.0, a swept glissando 0.85: it travels from left to right). Soloists stay narrow point sources. Measured on a finished mix: the bus correlation fell from 0.95 to 0.84 for the zither and to 0.67 for the dulcimer; the whole mix stayed at 0.44, mono-safe.

## 3. Buses and master: `mix()` arguments

- `bus_fx={"strings": [PeakFilter(250, -2, 1)], "drums": [Distortion(drive_db=3), Gain(-2)]}`: plugins per bus; the hall return is not affected.
- `sidechain=(("drums",), ("strings", "brass", "choir"), 2.5)`: when the drums hit, the other buses dip 2.5 dB so the drums punch. Lo-fi: duck keys and bass ~2 dB under the kick.
- `duck=[(beat, dB), ...]`: a gain curve on every bus except `duck_exempt` (hall return included): pull an intro down, build, or leave a real silence before a drop.
- `tone=[...]`: master EQ after the bus compressor, e.g. `PeakFilter(700, -2.5, .7)` against mid build-up, `PeakFilter(3500, 1.5, .8)` for presence, a +1.5-2 dB high shelf; lo-fi: `LowpassFilter(11000)`.
- `lufs=`: -14 for web and social platforms and for promos; -16 for background music, beds under a voice, and game music.
- `loop=True`: optional seamless loop (see SKILL.md).

**For voice-over videos**: the music should sit ~10 LU below the voice while it speaks. Never compress the voice; rules and the check are in SKILL.md.

## 4. Making parts sound played

| Technique | In code |
|---|---|
| Attack compensation (slow sample attacks sound late) | `render_parts` measures and triggers early. MuseScore General: choir ~92 ms, long strings 50-90 ms, short strings 60-90 ms, brass 10-35 ms, piano and drums ~0. Override with `offset_ms=` |
| Dynamics follow the phrase | velocity for short notes; Expr. presets + `expr_cc=2` for long notes, or `curves={2: [...]}`; do not give every voice of a chord the same curve |
| No two repeats alike | accents vs weak beats (e.g. 96 vs 50); `jitter_ms` (default 7 ms); `players` |
| Legato and separation | `legato=+0.05~0.1` for connected lines, `-0.05~-0.1` to let short notes breathe |
| Breath and stamina | leave gaps between wind phrases; no loud long note longer than a player could hold |
| Rolls | `roll=0.125` repeats long notes as 32nds with a rising ramp |
| Feel | `score.swing(part, ratio, unit)`: 8th or 16th swing; a late snare (~30 ms) for lo-fi; a dragged pickup into beat one for tango |
| Slides, vibrato, bends | `score.pitch(part, song, ...)`: portamento into long notes, scoops after rests, falls before rests, delayed vibrato; per-note `bend=` curves for zither press-bends. Slide into long notes only (`when=lambda a, b: b.dur >= .9`): sliding through every step sounds drunk |
| Timing that breathes | white `jitter_ms` sounds sequenced. Add a slow drift to the soloists and to ostinatos (two slow sine waves, ±7-14 ms), let accents sit ~6 ms late, vary each plucked note's ring, put a 4-bar swell on repeated figures, and an ornament now and then (a three-string brush into an accent). Tempo map: 3 % slower over the two beats into a new section |
| Tremolo | vary the rate (it settles in over the first strokes and wanders ±5 %), not just the velocity |
| Orchestration before EQ | parts crowding one register: change registers and voicings first; a big EQ cut means the arrangement needs another look. Measured: a sustained dulcimer tremolo plus a zither in 16ths under a tutti climax lowered the Audiobox scores (CE 7.36 → 7.62, PQ 7.63 → 7.87 with that bus 8 dB down); taking the tremolo out of the climax fixed it |

## 5. What to look at in the QC report

All hard `qc.py` checks must pass. Also:
- **Loudness every 2 s**: sections should breathe. A trailer moves ~10 LU from intro to peak; under 4 LU over a whole cinematic piece sounds flat (games and lo-fi are meant to be flatter).
- **Band levels**: 400-1500 Hz more than 10 dB above 1500-5000 Hz usually means a muddy, dull mix.
- **Hit jumps**: under 3 dB means the cue did not land.

The spectrogram (`*.spectrogram.png`) shows structure, silences and clicks; it is under 2000 px, so you can look at it directly.
