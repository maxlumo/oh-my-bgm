# The two SoundFonts: which to use and how

## 1. Overview

| | MuseScore General (`orch.GM_SF`) | GeneralUser GS 2.0.3 (`orch.GU_SF`) |
|---|---|---|
| File | `~/sound-libs/MuseScore_General.sf3`, 40 MB (SF3 is compressed) | `~/sound-libs/GeneralUser-GS.sf2`, 32 MB |
| Presets | 308 | 286 |
| Drum kits (bank 128) | 37: Standard 0-7, Room 8-15, Power 16-19, Electronic 24, TR-808 25, Jazz 32-36, Brush 40-42, Orchestra 48, Marching 56-59, 95-96 | 13: Standard 0-2, Room 8, Power 16, Electronic 24, 808/909 25, Dance 26, Jazz 32, Brush 40, Orchestral 48, SFX 56, CM-64 127 |
| Strengths | Bank 8 variations (e.g. 8-0 Mellow Grand Piano, 8-48 Orchestral Pad); "Expr." presets (banks 17/18, 21, 26, 31, 41, 51) whose volume follows CC2, so a single long note can swell; sectional strings (banks 20-51, same samples as bank 0) | Many GS variations (banks 1-13), e.g. 11-11 Vibraphone without tremolo |
| Licence | MIT | Free for any music, including commercial; the author notes a few sample sources cannot be verified 100 % |

Full lists are in `presets-*.txt` as `bank-program name`. Usage: `Part(name, program, sf2=str(GM_SF), bank=bank)`; drums: `Part(name, kit_number, sf2=..., channel=9)`.

## 2. Measured timbre differences

Method: one mid-range note, velocity 100, FluidSynth's own reverb and chorus off. Brightness = spectral centroid (Hz); stereo width = side RMS / mid RMS. Single notes only; other registers differ, ears decide.

| Instrument (GM program) | Brightness MSG / GU | Width MSG / GU | Verdict |
|---|---|---|---|
| Piano (0) | 908 / 1416 | 0.39 / 0.03 | MSG warmer and stereo; GU brighter, nearly mono |
| Strings (48) | 1845 / 2038 | 0.68 / 0.27 | MSG wider; GU faster attack (60 ms vs 91 ms) |
| Choir (52) | 1921 / 2072 | 0.75 / 0.34 | MSG wider |
| Bass (33) | 971 / 417 | 0 / 0 | GU much deeper, MSG has a clearer attack |
| Horns (60) | 810 / 976 | 0 / 0.20 | GU slightly brighter |
| Trumpet (56) / Flute (73) | 3064 / 2754, 2444 / 1896 | 0 / 0 | MSG brighter |
| Snare (kit 38) | 2834 / 3303 | 0 / 0 | GU crisper and louder |

**Starting split per part**: piano, strings, choir and pads, which need width and swells inside long notes, from MSG (Expr. presets for strings and choir); drums and bass, which need punch and low end, from GU. The libraries have different room sounds; the shared hall in `mix()` glues them together.

## 3. GM drum map (channel 10, `channel=9`)

35/36 kick · 37 side stick · 38/40 snare · 39 clap · 41/43/45/47/48/50 toms (low → high) · 42 closed hat · 44 pedal hat · 46 open hat · 49/57 crash · 51/59 ride · 52 china · 53 ride bell · 54 tambourine · 55 splash · 56 cowbell · 62/63/64 congas (mute high, open high, low) · 69 cabasa · 70 maracas · 75 claves · 76/77 wood blocks · 81 open triangle

## 4. Common sounds

| Use | MuseScore General | GeneralUser GS |
|---|---|---|
| Piano | 0-0 Grand Piano, 8-0 Mellow Grand Piano (softer) | 0-0, 0-1 Bright |
| Electric piano | 0-4 Tine Electric Piano (Rhodes) | 0-4 |
| Long strings | 0-48 Strings Fast, 0-49 Strings Slow; swells with 17-48 / 17-49 (Expr., CC2); solo 17-40 violin, 17-41 viola, 17-42 cello | 0-48, 0-49 |
| Short, plucked, tremolo strings | short notes on 0-48; 0-45 Pizzicato; 0-44 Tremolo (17-44 Expr.) | 0-45, 0-44 |
| Brass | 0-60 horns, 0-57 trombone, 0-58 tuba, 0-56 trumpet; Expr. 17-60 / 17-57 / 17-58 / 17-56, muted trumpet 17-59, section 17-61 | same numbers |
| Choir | 0-52 Choir Aahs, 0-53 Voice Oohs; Expr. 17-52 / 17-53 | same |
| Woodwinds | 0-73 flute, 0-72 piccolo, 0-68 oboe, 0-69 English horn, 0-71 clarinet, 0-70 bassoon; Expr. in bank 17; 17-65 alto sax | same |
| Squeezeboxes | 17-21 Accordion Expr., 17-23 Bandoneon Expr. | 0-21 |
| Timpani | 0-47 (no roll sample, use `roll=0.125`) | 0-47 |
| Bass | 0-33 finger, 0-32 acoustic, 0-38 synth | 0-33 (deeper), 0-32 upright, 0-34 picked |
| Guitar | 0-25 steel, 0-24 nylon; strumming in `examples/ballad_backing.py` | 0-24, 0-28 muted, 0-30 overdrive |
| Mallets, bells | 0-11 vibes, 0-12 marimba, 0-8 celesta, 0-14 tubular bells, 0-10 music box, 0-9 glockenspiel | 11-11 vibes no tremolo |
| World | 0-107 koto, 0-106 shamisen, 0-77 shakuhachi (17-77 Expr.), 0-15 dulcimer, 0-116 taiko, 1-115 Temple Blocks (5 blocks x 4 velocity layers) | 0-104 sitar, 0-105 banjo, 0-106 shamisen (10 velocity layers), 0-15 dulcimer (long ring) |
| Pads, atmosphere | 0-89 Warm Pad, 8-48 Orchestral Pad, 17-92 Bowed Glass Expr. | 0-89 |
| Kits | 37 kits in bank 128, see section 1 | 13 kits |

The `ROLES` table in `examples/trailer_ascent.py` is a complete orchestral part map you can copy.

## 5. East Asian ensemble: what measured best

Same phrase per candidate, same hall, -18 LUFS, scored with Audiobox Aesthetics (a weak proxy: only differences of 0.3 or more were acted on; ears decide).

| Role | Use | Instead of | Why |
|---|---|---|---|
| Guzheng (ostinato and solo) | MSG 0-107 Koto | MSG 8-107 Taisho Koto (koto + steel guitar), GU 0-107 | Taisho's steel layer smears fast figures (16ths CE 6.37 vs 6.95); GU's koto has 2 samples pitched far up |
| Pipa | GU 0-106 Shamisen | MSG 0-106 | Velocity layers, short decay that suits tremolo (PQ 8.04 vs 7.92) |
| Xiao, dizi | MSG 17-73 Flute Expr., darkened for xiao: HPF 220, +1.5 dB at 700 Hz, -2.5 dB at 2.5 kHz, LPF 5.2 kHz | 17-77 Shakuhachi Expr. | Both libraries' shakuhachi is a single looped sample (root C5) stretched over the range (PQ 7.06 vs 7.44; an octave down 6.27) |
| Erhu | MSG 17-40 Violin Expr. with `score.pitch` slides, EQ: HPF 300, +1.5 dB at 1.1 kHz, -3 dB at 2.9 kHz, LPF 8 kHz | GU 0-40, 0-110 | 14 samples; MSG viola Expr. scores the same |
| Yangqin | GU 0-15 Dulcimer | MSG 0-15 | Higher CE, long natural ring; keep tremolo out of dense tutti |
| Drums | GU 0-116 taiko about 10 semitones down (key 50), MSG kit 48 keys 86/87 (short and long taiko hits), MSG 8-116 Concert Bass Drum (7 velocity layers) | the taiko 22 semitones down | A sample slowed to a quarter of its speed sounds like a synth boom |

Pitfalls: the China cymbal is key 52 of the **standard kit** (MuseScore General bank 128 program 0); in the **Orchestra kit** (48) keys 41-53 are timpani, so key 52 there plays a timpani note. Violin samples carry about ±17 c of vibrato at 5-6 Hz, shakuhachi and flute about ±9 c: add pitch-wheel vibrato to winds and plucked strings, little or none to violins.
