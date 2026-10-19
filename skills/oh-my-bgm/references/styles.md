# From a scene to music: styles, rules and examples

Users often give only a scene, a mood or a reference: "music for a science explainer", "a warm brand film", "a sad ending", "like the exploration music in some open-world game". Do not quiz them about style. Make the decisions in section 1, write a finished piece, and say in one or two sentences what you chose and why. Ask only when the use is unclear (voice-over or not, cue points, length, loop) and the answer would change the result.

**Naming and describing.** Give every piece an original title (e.g. "Wheatfield Town"). Never use the name of a game, film, song or brand, or words taken from them, and never write "in the style of X". When the user mentions a work, take only its musical traits (instruments, tempo, mode, texture). Describe a piece by **what it feels like and where it fits**, e.g. "tense, patient, deliberate: a mind weighing its next move; for strategy scenes, heist plans, historical drama". Do not label it with a genre tag or with the user's keyword ("Chinese strategy music", "anime battle"): one word in the brief is a hint, not a description.

## 1. Five decisions

| Decision | How |
|---|---|
| **Use and mood → tempo, density** | See the table below |
| **Mode** | Elegant melancholy: harmonic minor. Sad but hopeful: minor, ending on the major tonic (Picardy third). Mysterious, focused: aeolian or dorian, with a Lydian #4 for ambiguity. Warm and pastoral: major with Lydian #4 (II/I over the tonic) and a borrowed minor iv. Bright and curious: major with maj7, add9, Lydian. Urban and stylish: dorian with 9/11/13 chords. East Asian: pentatonic modes (yu, shang). Middle East / desert: Hijaz (D Eb F# G A Bb C). Balkan: "Gypsy" minor (D E F G# A Bb C#) |
| **Instrumentation** | Pick **one tradition** of ensemble, not a mixture: jazz combo, bossa trio, tango quintet, string quartet, chamber orchestra, full orchestra, Celtic band, brass band, East Asian ensemble, lo-fi beat. Every part has one role: melody, counter-line, harmony, bass, groove. 6-10 parts are plenty |
| **Theme** | 8 or 16 bars, question and answer, mostly stepwise with a few leaps, with long notes and rests. Every repeat changes the orchestration (another instrument takes the tune, a counter-line enters, drums come or go); never replay it unchanged |
| **Form and length** | Default: a complete piece with an ending: intro → theme → variation → middle (new tonal centre or new lead) → full theme → ending on the tonic. For video, follow the video length; otherwise 80-150 s. Make a `--loop` version only for games or long playback (section 4) |

| Use | Tempo and density | Dynamics | Examples |
|---|---|---|---|
| Promo, brand film, launch, opener | 110-125 BPM; build in layers: piano pulse → spiccato strings → drums → tutti, one hit to finish | Wide: 8-12 LU from intro to peak; a held breath before the peak | Toward the Light |
| Explainer, tutorial (voice-over) | 95-110 BPM; an ostinato and a sparse "question" melody, leave the voice band free | Small; the tune never fights the voice | Curiosity, Deep Pool, Gambit |
| Everyday listening, study, streams | 75-90 BPM; one loopable groove, warm and low-passed | Small | Steam & Static |
| Lifestyle, food, travel, joy | 120-135 BPM; syncopated groove, acoustic instruments | Medium | Afternoon, Oak & Ale, Wheatfield Town, Copper Wedding |
| Passion, drama, dance | 110-125 BPM; driving accents (3+3+2), a lyrical middle | Medium to wide | Ember Tango, Stratagems |
| Sad, memorial, farewell, charity | 60-80 BPM; piano and solo strings, voices added one by one | Medium: peak at two thirds, then let go | After the Rain, Candlelit Ruins, When the Stars Fall |
| Art, culture, interviews, poetry | 65-75 BPM; very few notes, a repeating piano figure, string quartet | Small | Sketch, Open Field |
| Landscape, documentary | 70-80 BPM or free time; long notes, drones, a solo instrument | Medium | Open Field, Song of Shifting Sands |
| City, fashion, tech product | 100-115 BPM; 16th-note groove, extended chords | Small to medium | Neon Alley, Smoke Rings |
| Animation and comics | Daily life 120-128 with a 16th push; emotional 76-84, piano + strings, last chorus up a step; action 160-175, string ostinato + rock kit + brass | Small for daily life, wide for emotion and action | After School, When the Stars Fall, Gale |
| Games | Thinking 80-112, exploring 60-80, towns 100-132, combat 140+ (skeleton: `examples/trailer_ascent.py`); optional loop | Small, made for long listening | any |

## 2. The first goal: it sounds good and serves the listener

Before every decision ask: will the listener find this beautiful, comfortable, moving? Code's freedom is for getting details right: phrase dynamics, voice leading, choosing what to leave out, space, the mix. It is not for stunts no player could perform. A human rejected a set of "limits of hearing" experiments (Shepard tones stacked over seven octaves, a canon in seven simultaneous tempos, harmonic-series just intonation) as "too much, meaningless stacking, unpleasant to listen to". So:
- Never add parts, octaves or tempos just because code can. Every layer must make the music sound better in a way you can name.
- Do not sell auditory illusions, microtones or extreme speeds as the point; at most as a small touch.
- Fewer lines, clearer: usually no more than three lines are clearly audible at once (melody, bass, one counter-line or groove).

## 3. Sophisticated vs childish

A human rejected a light pop cue ("Sunny Whistle") as "very juvenile and childish". Its problems are the left column. Unless the user asks for something cute or poppy, write the right column.

| Sounds childish | Sounds sophisticated |
|---|---|
| A bouncy 8th-note major-pentatonic tune in C5-C6, doubled an octave up on glockenspiel, whistle or kalimba | A lead in the middle register: cello, clarinet, viola, alto sax, vibes, flute low; mostly stepwise, with long notes and rests |
| I-V-vi-IV on repeat | Modal colour and extended chords: maj7, 9, 11, 13, slash chords (G/F, A/C#), borrowed chords (Bbm in F, Dbm6 in Ab), b9 on dominants, the Neapolitan |
| Something on every beat, claps on 2 and 4, every part equally bright | Space; a foreground and a background; groove detail: swing, bossa syncopation, 3+3+2, 7/8, 9/8, ghost notes |
| Melody and accompaniment only | Counterpoint: a contrary bass line, call and response; when the theme moves to another instrument, the old one takes a counter-line |
| A hard key change on the last chorus as the climax | A prepared key change (the bar before stops on the new key's dominant), used once, at the end |

## 4. Rules per use

- **Voice-over videos**: a sparse melody in the middle register with gaps between phrases; do not fill 2-5 kHz with the lead. Deliver music at -16 LUFS and duck it ~10 LU under the voice in the video mix. Voice rules are in SKILL.md.
- **Promos**: the arc is the point. Use `duck` to drop 2 beats to 2 bars before the peak; after the final hit let the reverb ring out. Deliver -14 LUFS.
- **Sad and art films**: slow, few notes, long notes. Longer reverb (rt_mid 2.1-2.8 s); piano from MuseScore General 8-0 (Mellow Grand); for art films a low-pass around 4 kHz makes it closer and softer.
- **Games**: small dynamics (LRA 3-6 LU), no section more than 4 LU louder than the others; melody 0-3 LU above the rest.
- **Optional seamless loop** (only for games or long playback): `mix(..., loop=True)` makes the file exactly the score length, folds the reverb tail onto the start and does not fade; write the ending so it leads back to the start (stop on the dominant or the intro chord); check with `qc.py --loop`. The examples switch with `--loop`: without it you get the full piece with its ending.

## 5. A palette of genres

The two SoundFonts cover far more than orchestras. Starting points that render well:

| Genre | Tempo, feel | Instruments here | Signature devices |
|---|---|---|---|
| Lo-fi hip hop | 75-90, swung 16ths (0.56-0.6) | Rhodes (4) with slow chorus, nylon guitar or vibes, finger bass, kit 0 with the snare ~30 ms late, vinyl and rain noise | 4-bar loop of 9th chords; whole mix low-passed ~11 kHz; sidechain keys to the kick |
| Bossa nova | 125-140, felt in 2 | Nylon guitar, upright bass, cross-stick + shaker, flute, Rhodes | Two-bar syncopated comp; ii-V with b9; borrowed iv6 |
| Tango nuevo | 110-125 | Bandoneon Expr. (17-23), violin Expr., piano, double bass | 3+3+2 marcato; bass drag into beat one; "marcato in four" for the lyrical part; two-hit ending (V on the last off-beat, i on one) |
| Balkan brass | 8th = 280-320 in 9/8 (2+2+2+3) or 7/8 | Trumpet, clarinet, trombones, tuba (all Expr.), accordion, big drum + stick, tambourine | "Gypsy" minor; tuba on every group, off-beat chords; harmony a chord-tone 3rd or 6th below |
| Jazz (lounge, noir) | 90-130 swing | Vibes, muted trumpet, Rhodes, upright, brushes | Charleston comp; walking bass in the bridge; guide-tone pads |
| Acid jazz, funk | 100-115 | Alto sax, flute, Rhodes, muted guitar, string and brass stabs, finger bass | 16th bass with octave pops; #9 chords; a break with only the rhythm section |
| City pop / anime daily life | 118-128, light 16th push | Bright piano, Rhodes, flute, strings, muted guitar, finger bass | Marunouchi progression IVmaj7-III7-vi7-v7 I7; royal-road IVmaj7-V7-iii7-vi7 |
| Emotional piano-and-strings ballad | 72-84 | Piano, violins, cello, pad, acoustic guitar, soft kit | Descending bass verse; royal-road chorus; quiet first chorus, full second; prepared step-up key change |
| Orchestral rock (action) | 160-175 | Horns, brass, 16th string ostinato, choir, piano octaves, overdrive guitar kept low, rock kit, timpani | i-VI-VII-V; 3+3+2 accents in the ostinato; three-hit ending |
| Cinematic build | 110-125 | Piano pulse, spiccato strings, horns, trombones, choir, orchestral kit, synth booms and risers | Descending bass (I-V/3-vi-IV); layer per section; a held breath before the peak |
| Neo-classical | 65-75 | Mellow piano low-passed, string quartet | One repeating broken-chord figure; voices join one at a time |
| Minimalism | any, odd meters | Marimba, celesta, harp, cello | Two loops of different lengths drifting against each other; one long-note melody |
| Celtic folk | 6/8 at dotted-quarter 70-80 | Fiddle, flute, accordion, nylon guitar, hammered dulcimer, frame drum | Dorian; diatonic 3rds; boom-chick-chick |
| East Asian pentatonic | 80-95 | Koto (MSG 107) for guzheng, GU shamisen (106) with tremolo for pipa, violin Expr. with `score.pitch` slides for erhu, flute Expr. darkened for xiao/dizi, GU dulcimer for yangqin, temple blocks, taiko (choices measured in `soundfonts.md` section 5) | Pentatonic mode; 3+3+2 drums; a lament bass; zither sweeps over all strings (`spread`), press-bends and vibrato; heterophony in the tutti. These libraries have no genuine Chinese instruments; say so when delivering |
| Middle-Eastern / desert | 70-90 | Cello, violin, English horn, sitar (GU 104), harp ostinato, drone, congas as frame drum | Hijaz; the b2 over the drone; maqsum rhythm |

Weak in these libraries, avoid as the main colour: distorted rock guitar up front, modern EDM leads and supersaws, realistic solo voice. Use them, if at all, low in the mix.

## 6. Example catalogue (`examples/styles/`)

Each runs as is: `<skill>/scripts/run.sh <skill>/examples/styles/<file>.py [--loop]`, output in `./out/<file name>/`. For a new piece copy the closest one as a skeleton and **rewrite the theme, harmony and orchestration**.

| Title | File | Feels like | Fits | Musical core |
|---|---|---|---|---|
| Toward the Light | `uplifting_launch.py` | Rising hope, resolve, a door opening | Launches, brand films, milestones, sports highlights | D major 118; piano pulse → strings → drums → tutti; descending bass; held breath; one hit |
| Curiosity | `curious_explainer.py` | Bright, inquisitive, light-footed but adult | Science and tech explainers, tutorials, walkthroughs | D major 104; piano ostinato in maj7/#11; clarinet asks short questions with rests |
| Steam & Static | `lofi_study.py` | Calm, cosy, unhurried, a little nostalgic | Study and work, rainy afternoons, streams, reading | F major 82; lo-fi beat, Rhodes 9th chords, nylon tune, rain and vinyl |
| Afternoon | `bossa_afternoon.py` | Sunny, relaxed, gently happy | Food and lifestyle vlogs, cafés, travel, weekends | F major 128; bossa trio + flute; Bbm6 |
| Ember Tango | `tango_nuevo.py` | Intense, elegant, a little dangerous | A duel of glances, a port city at night, dance and fashion films, tense negotiations | A minor 118; bandoneon and violin; 3+3+2 marcato; tango ending |
| Copper Wedding | `balkan_brass.py` | Exuberant, sweaty, irresistible | Weddings and festivals, chases through a market, comic chaos, celebrations | D "Gypsy" minor, 9/8; brass band |
| After the Rain | `after_rain_piano.py` | Grief that slowly lets light in | Memorials, farewells, emotional stories, charity films | D minor 72; piano, cello, violin; Neapolitan Eb; ends in D major |
| When the Stars Fall | `acg_emotional_ballad.py` | Tender, aching, uplifting at the end | Emotional scenes in animation and games, reunions, graduations, year-in-review | Eb → F major 80; royal-road chorus; prepared step-up |
| Candlelit Ruins | `melancholy_waltz.py` | Elegant sorrow, memories in an empty place | Quiet sad stories, ruins, flashbacks | C minor 3/4; piano, solo strings, choir, music box |
| Sketch | `sketch_neoclassical.py` | Intimate, thoughtful, bittersweet | Art and culture films, interviews, poetry, craft | Ab major 70; felt piano figure, string quartet; Dbm6 |
| Open Field | `sparse_piano_field.py` | Wide open, solitary, peaceful | Landscapes, nature, exploration, monologues | D major + G#, 72; sparse piano with long silences |
| Song of Shifting Sands | `hijaz_desert.py` | Vast, ancient, lonely, enduring | Deserts, Silk Road and Middle-East documentaries, pilgrimage | D Hijaz 76; solo cello over a harp ostinato and drone |
| Wheatfield Town | `pastoral_orchestra.py` | Warm, bustling, wholesome | Countryside, travel, warm brand films, game towns | F → G major 3/4; double-wind orchestra; Lydian G/F |
| Stratagems | `guofeng_pentatonic.py` | Tense, patient, deliberate: a mind weighing its next move | Strategy and history scenes, heist plans, a calm before a confrontation | D yu pentatonic 90; koto ostinato, pipa-style tremolo, erhu-style slides, taiko 3+3+2 |
| Gambit | `chamber_tactics.py` | Clever, poised, quietly competitive | Strategy maps, business analysis, history explainers, puzzles with a plan | A minor 100; harpsichord and pizz, woodwind counterpoint |
| Deep Pool | `minimal_seven_eight.py` | Absorbed, mysterious, steady | Focus and study, puzzles, tech explainers under a voice | E minor 7/8; marimba and celesta loops drifting against each other |
| Neon Alley | `acid_jazz_funk.py` | Stylish, cool, confident | City life, fashion and product showcases, urban vlogs | F dorian 112; acid-jazz funk |
| Smoke Rings | `lounge_jazz.py` | Late-night, sly, a little woozy | Night scenes, bars, noir, card tables | D minor 96 swing; vibes, muted trumpet, detuned organ |
| Oak & Ale | `celtic_tavern.py` | Cosy, merry, communal | Taverns and fantasy, food and autumn videos | E dorian 6/8; Celtic band |
| After School | `acg_daily_citypop.py` | Breezy, bright, everyday happiness | Daily life in animation and comics, campus and city vlogs | F major 124; Marunouchi verse, royal-road chorus |
| Gale | `acg_battle_rush.py` | Fierce, urgent, heroic | Battles in animation and games, boss fights, sports highlights, action trailers | D minor 168; orchestral rock; three-hit ending |

Not covered yet, starting points: horror (low drones, clusters, long unmetered stretches, a single high piano note now and then); sci-fi (MuseScore General bank 17 Expr. synth pads 89-99 for sustains, with strings and piano); racing and sport (130-150 BPM, four-on-the-floor kick, 16th synth bass).

## 7. Writing details

- **Write melodies with `score.seq`**: `"C5/1 F5/1 G5/1 | A5/1.5 B5/.5 A5/1"`. `|` is only a bar mark and is not checked; make every bar add up.
- **List chords per bar** with explicit voicings. Do not put a 9th in one part next to a 3rd in another (D4 against Eb4), and keep 7ths away from roots inside pads; `review.py` finds these.
- **Slash chords** (A/C#, D/F#): take fifths and arpeggios from the chord root, not the bass, or a G# appears over C#.
- **Stop broken chords at the chord change**, like a pianist changing pedal.
- **Pentatonic snapping must let the bar's own root through**: Bb is not in D yu, and snapping turns it into an A on top of a Bb bass.
- **Fixed loops step aside from non-chord half-steps** (the celesta in `minimal_seven_eight.py`).
- **Harmony lines**: a chord tone a 3rd or 6th below the tune (`harmony_below` in `balkan_brass.py`), not a blind diatonic 3rd.
- **Common progressions** worth knowing: royal road IVmaj7-V7-iii7-vi7; Marunouchi IVmaj7-III7-vi7-v7 I7; vi-IV-V-I; descending bass I-V/3-vi-iii/5-IV-I/3-ii-V; i-VI-VII-V for action; ii-V-I with b9. Sophistication comes from voicings, counterpoint and preparing key changes, not from cute timbres; celesta and music box are accents only.

## 8. Checking without ears

1. `run.sh review.py piece.py`: each part's range, and minor 2nds / 9ths between parts sounding together. Go through every one: a b9 on a dominant, the Hijaz b2 or a short passing note may stay; the rest are wrong notes or voicings.
2. `score.finish()` or `score.balance()`: melody vs the rest per section.
3. `qc.py` (`--loop` for loops): loudness, true peak, seam.
4. Look at the spectrogram and band levels: 20-60 Hz far above other pieces usually means taiko or synth hits without a low cut (`HighpassFilter` is only 6 dB/oct; stack two or three).
5. Always have a human listen.
