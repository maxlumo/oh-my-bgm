---
name: oh-my-bgm
description: "Oh My BGM: compose instrumental music as code. Write the score in Python, render each part with FluidSynth on two free SoundFonts (MuseScore General, MIT; GeneralUser GS, free for any music incl. commercial), then mix and master in code. Covers any genre and any place people hear music: everyday listening and playlists, film and TV scoring, games (optional seamless loops), anime, promo and brand films, explainers, vlogs, sad or joyful moments, art films, documentaries, trailers, pop backing tracks. Can hit a video's cue points. Delivers WAV, MP3, stems and a QC report. No vocals. Use it to write background music or a score, and also when the user only describes a scene, a mood or a reference work (e.g. 'music for a rainy study session', 'something tense for a negotiation scene', 'an upbeat track for a product launch'): then choose the style yourself and deliver a finished piece."
---

# Oh My BGM: score in code → two SoundFonts → mix in code

Use only two sound libraries: **MuseScore General** (MIT) and **GeneralUser GS 2.0.3** (free for any music, including commercial). Both are safe for ads and promotional films. Do not bring in other sample sources.

A score is a Python file: each part is a `Part`, notes are written in beats. Every part renders to its own track, so each part can use a different library. The same code always renders the same audio. A minute of music with 20+ parts renders in about 20 s and mixes in about 30 s.

## First run

```bash
<skill dir>/scripts/setup.sh
```

Installs FluidSynth 2.4.4, both SoundFonts and a Python environment (~100 MB), skipping anything already present, then renders one piano note per library as a smoke test. Afterwards run every Python file with `<skill dir>/scripts/run.sh file.py`: it sets up the virtualenv, `PYTHONPATH` and the libfluidsynth path.

## Workflow

1. **Pin down the brief**: length, use (decides loudness), mood, style and instrumentation, key and tempo, cue points. For a video, read its `cues.json` (video-production skill format) and fit the tempo to the hits with `cues.fit_bpm()`.
   - **If the user only gives a scene, a mood or a reference work**: read `references/styles.md` and decide tempo, mode, instrumentation, theme and form yourself; do not quiz the user about style. The first goal is music that sounds good and serves the listener, never stacking for its own sake. Write in the "sophisticated" manner (sections 2-3 of that file). Deliver a complete piece with an ending; make a loop only when asked.
   - Start from the closest piece in `examples/styles/`. Rewrite the theme, harmony and orchestration; changing the instruments does not make a new piece.
   - Give each piece an original title. Never use the name of a game, film, song or brand, and describe it by **feeling and scene**, not by echoing a genre keyword or a reference title (start of `styles.md`).
2. **Write the score**: copy `templates/piece.py` into the work folder and edit its SCORE section. The ~30 s template shows the two libraries per part (piano, Expr. strings and pads from MuseScore General; drums and bass from GeneralUser GS), fitting the tempo to cues, ending exactly at the video length, and running QC.

   Fuller examples in `examples/`:
   - `styles/*.py`: 21 complete pieces of 70-135 s across genres, moods and uses (catalogue in `references/styles.md` section 5). They write melodies with `score.seq` and call `score.finish()` to render, mix, export, print the melody balance and run QC in one go; `--loop` gives a seamless-loop version where supported.
   - `trailer_ascent.py`: a 66 s hybrid orchestral trailer with 20+ parts (synth percussion layers in `hybrid.py`).
   - `ballad_backing.py`: a 71 s pop ballad backing: Expr. strings with swells, strummed acoustic guitar, GM kit.
3. **Choose sounds**: `Part(name, program, sf2=GM_SF or GU_SF, bank=..., channel=...)`. Program numbers are in `references/presets-*.txt`; which library suits which part is in `references/soundfonts.md`.
4. **Render**: `render_parts(PARTS, song, workdir)`. Each part's sample attack is measured and triggered early so the sound lands on the beat; do not nudge notes by hand.
5. **Mix and master**: `mix(...)`. Each track is first set to its `level=` (target LUFS), then EQ, pan, reverb and bus processing, then the master at `lufs=`. Starting values in `references/mixing.md`, including depth (extra `halls=`: a far space, a valley echo) and the stereo stage (`Part.spread` for plucked instruments). Make lines sound played, not sequenced: `score.pitch()` for slides and vibrato, a tempo map (`Song(tempo=...)`) for breaths and the final ritardando.
6. **Export and check**: `export(...)` writes a 24-bit WAV, an MP3, a spectrogram, `stems/` and `report.json`. First run `run.sh <skill dir>/scripts/review.py piece.py` to find wrong notes (minor 2nds / 9ths between parts sounding together) and judge each one. Then:
   ```bash
   <skill dir>/scripts/run.sh <skill dir>/scripts/qc.py out/cue.wav --lufs -14 [--duration 24] [--cues cues.json] [--loop]
   ```
   Exit code 1 means a hard check failed: loudness ±1 LU, true peak, non-finite samples, duration ±20 ms, L/R correlation > 0; with `--loop` also no click or drop at the seam; with `--voice` the voice must not be compressed (below). Hit jumps, loudness every 2 s and band levels are reported, not judged.
7. **Have a human listen**: the agent cannot hear. Serve the files with a background task:
   ```bash
   nohup <skill dir>/scripts/run.sh <skill dir>/scripts/serve.py out 8766 > serve.log 2>&1 &
   ```
   The server is read-only, supports seeking (also on iPhone Safari) and has no directory listing, so share links to specific files.

## Pitfalls

- **"Expr." presets are nearly silent without CC2**: they exist only in MuseScore General (banks 17/18/21/26/31/41/51). Add `expr_cc=2` to the `Part` to derive phrase swells from the velocities, or draw `curves={2: [(beat, value), ...]}`.
- **Drums are on channel 10**: `channel=9`; `program` is the kit (0 Standard, 8 Room, 16 Power, 25 808, 32 Jazz, 40 Brush, 48 Orchestra); notes follow the GM drum map in `references/soundfonts.md`.
- **Sectional strings are not more realistic**: MuseScore General banks 20/30/40/50 use the same samples as bank 0 (correlation 1.0).
- **Set loudness with `level=`, not `gain`**: the two libraries differ by 2-4 dB raw; `level` aligns every track first.
- **Video deliveries must match the video length exactly**: `Song.tail` is the ring-out after the last beat: `tail = duration - bars × seconds per bar`. The template does this.
- **Never compress a voice-over or vocal in the mix.** A real failure: another program set the voice track to -4 LUFS, raising it 16 dB into a limiter, and the master was limited to -3 dBTP; voice peaks lost 2-6 dB and sounded hard and distorted. Instead:
  - Treat the voice (TTS or recorded) as finished material: gain only. No compression, limiting, saturation, "warmth" or "air", and no level/normalise feature that pushes it into a limiter.
  - Making room is the music's job: duck the music about 10 LU below the voice while it speaks, and bring it back between lines.
  - Check the headroom first: the voice's PLR (true peak minus loudness) caps the mix at `true-peak ceiling - PLR`. TTS PLR is often 15-17 dB, so at -1 dBTP the mix lands at -16 to -18 LUFS. Forcing -14 means squashing the voice. Deliver -16 (platforms normalise anyway).
  - With a different sample rate (TTS is often 22.05 or 24 kHz) resample once, with `scipy.signal.resample_poly`.
  - Before delivery: `qc.py mix.wav --lufs <target> --voice voice.wav --voice-offset <s>`. If the voice's PLR in the mix is more than 1 dB below the original, it was compressed and the check fails (two earlier mixes measured 2.5 and 2.1 dB; a gain-only mix measures ~0).
- **Loops need `mix(..., loop=True)`**: a normal `mix()` fades the last 1.5 s, which breaks a loop. With `loop=True` the file is exactly `song.beats` long, the reverb tail is folded onto the start, and compressor and limiter are pre-rolled with the loop's own ending.
- **Stop broken chords at the chord change**: cut piano and harp arpeggio notes at the bar line (like a pedal change), or `review.py` will show minor 9ths across every bar line.
- **LLM listening is not a quality gate**: in A/B tests Gemini always preferred whichever track played second and misheard keys and tempos. The gate is `qc.py` plus human ears.
- **Render in the foreground**: it takes seconds. Use a background task only for the review server or batch renders longer than a few minutes; never sleep-wait.

## References

| File | Contents | Read when |
|---|---|---|
| `references/styles.md` | Five decisions from a scene or mood; tempo and dynamics per use; "serve the listener first"; sophisticated vs childish writing; naming and describing pieces; a palette of modern genres; optional loops; the `examples/styles/` catalogue; writing details; checks without ears | First, whenever the user asks for music by scene, mood or use |
| `references/soundfonts.md` | Both libraries: presets, banks, kits, measured timbre differences, which part from which library, GM drum map | Choosing sounds |
| `references/mixing.md` | Starting levels, pans, reverb sends and EQ per role; bus processing, sidechain, mastering; making parts sound played | Mixing and shaping expression |
| `references/api.md` | `orch` / `score` / `cues` / `qc` / `review` / `serve` interfaces | Writing a score |
| `references/presets-musescore-general.txt`, `presets-generaluser-gs.txt` | Every preset's bank-program number and name | Looking up a sound |
