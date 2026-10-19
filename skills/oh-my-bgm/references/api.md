# Interfaces (modules in `scripts/`)

Make the modules importable first: `sys.path.insert(0, f"{MUSIC_SKILL_DIR}/scripts")`. `run.sh` already does this.

## orch: score, render, mix, export

```python
from orch import Part, Song, n, nearest, chord_tones, render_parts, mix, export, GM_SF, GU_SF, SR
```

- `SR = 48000`; `GM_SF` / `GU_SF` are the two SoundFont paths; `LIBS` defaults to `~/sound-libs` (env `SOUND_LIBS`).
- `n("F#4") -> 66`: note name to MIDI number, middle C = C4 = 60.
- `nearest(pc, target)`: the MIDI number of pitch class `pc` closest to `target`, for voice leading.
- `chord_tones("Dm") -> (root, third, fifth)` pitch classes. Built in: Dm Bb F C Gm A Am Eb only; write your own table for other chords (see `TONES` in `templates/piece.py`).

### `Song(bpm, beats, tail=4.0, seed=7, tempo=[])`
`beats` is the music's length in beats, `tail` the ring-out after the last beat (s). Duration = `song.t(beats) + tail`. `song.t(beat)` converts beats to seconds, `song.bpm_at(beat)` gives the tempo there, `song.spb` is seconds per beat at `bpm`. For odd meters pick the unit yourself: 8ths at 300 BPM with 9 per bar.

`tempo=[(beat, bpm), ...]` is an optional tempo map: linear ramps between the points, held outside them; two points on the same beat make a jump. Use it for a free prelude (`(0, 60)`: a beat is a second), an accelerando into tempo, a small breath before a section (`(b - 2, 90), (b, 87), (b, 90)`), a ritardando into the last chord. Every part, automation and `song.t()` follow it.

### `Part(name, program, sf2=GM_SF, bank=0, channel=0, **kw)` and `part.add(beat, dur, pitch, vel, bend=None)`
`pitch` is a MIDI number or note name; `beat` and `dur` are in beats. `bend=[(beats after the note's start, semitones), ...]` gives that note its own pitch curve (a zither press-bend `[(0, 0), (.3, 0), (.5, 2)]`, a fall, a scoop); `score.pitch()` writes these curves for a whole line. Bent notes are dealt over 8 MIDI channels, so a curve never bends a neighbour.

| Field | Purpose |
|---|---|
| `program`, `sf2`, `bank`, `channel` | GM program; SoundFont (`str(GM_SF)` or `str(GU_SF)`); bank; MIDI channel. Drums: `channel=9`, then `program` is the kit |
| `level`, `pan`, `width`, `gain`, `send`, `eq`, `bus` | Mix: target LUFS, pan -1..1, M/S width, extra gain dB, hall send dB, pedalboard plugins, bus name (stems are exported per bus) |
| `auto=[(beat, dB), ...]` | Gain automation for this track |
| `players` | Unison players, each slightly detuned, late and panned |
| `jitter_ms`, `legato` | Random timing; lengthen (+) or shorten (-) every note, in beats |
| `expr_cc`, `curves`, `cc` | Derive a dynamics curve from the notes on this CC (2 for Expr. presets); hand-drawn CC curves `{cc: [(beat, value)]}`; initial CC values |
| `note_map`, `transpose`, `cents`, `roll`, `offset_ms` | Remap keys (percussion); transpose; fine-tune the whole track in cents (±200); emulate rolls (e.g. 0.125 beats); manual attack compensation |
| `bend_range` | Pitch-wheel range in semitones (default 2; `score.pitch` raises it for wide slides) |
| `sends={name: dB}` | Extra sends into the reverbs and echoes named in `mix(halls=...)` |
| `spread` | Pan the notes by pitch across ±spread, low strings left and high right, as in a stereo recording of a zither, harp, dulcimer or piano (0.3-1.0). Each group of neighbouring pitches gets its own channel, so a repeated note still stops its own ring |

### `render_parts(parts, song, workdir) -> {name: stereo array}`
One MIDI file per part and player, rendered in parallel. Measured attack offsets are in `render_parts.onsets` (ms).

### `mix(parts, stems, song, extra=None, lufs=-14, ceiling=-1.2, hall=None, duck=None, duck_exempt=("fx",), tone=None, bus_fx=None, sidechain=None, loop=False, halls=None)`
Returns `(master, placed, buses, levels)`:
- `master`: the mastered stereo array.
- `placed`: each part after processing (dry).
- `buses`: each bus plus the `hall` return, pre-master; they sum to the pre-master mix.
- `levels`: each track's raw LUFS.

`loop=True` (optional) makes a seamless loop, e.g. for games or long playback: the result is exactly `song.beats` long, the tail after the last beat is folded onto the start, no fades; bus compressor and limiter are pre-rolled with the last 4 s so the start continues the end. Keep `Song.tail` long enough for the reverb; it is folded back.

`halls={name: dict(...)}` adds reverbs or echoes beside the main `hall`, fed by `Part.sends` and returned on their own buses `hall_<name>`: `dict(rt_low=..., rt_mid=..., rt_high=..., predelay=..., length=..., hp=180, lp=9000)` is another `hall_ir` (e.g. a far, darker space), `dict(echo=dict(time=1.0, repeats=3, feedback=.42, spread=.6, lp=3500), hp=350, lp=6500, to_hall=-6)` is a ping-pong echo (`echo_ir`) whose return also feeds the main hall by `to_hall` dB. Values that work are in `mixing.md`.

`extra={name: (array, dict(level=..., pan=..., bus=...))}` mixes in non-MIDI audio layers, e.g. the synthesised percussion of `examples/hybrid.py`, rain or vinyl noise. Argument usage is in `mixing.md`.

### `export(master, buses, outdir, name, meta=None) -> report`
Writes `name.wav` (24-bit), `name.mp3` (320k), `name.spectrogram.png`, `stems/name.<bus>.wav` (32-bit float) and `name.report.json` with LUFS, true peak, LRA, L/R correlation and `meta`.

Other helpers: `hall_ir(...)`, `echo_ir(...)`, `convolve(x, ir)`, `true_peak_limit(x, ceiling_db)`, `measure(path)` (ffmpeg EBU R128), `place(x, pan, width)`, `fx(x, plugins)`, `db(dB)`.

## score: score-writing helpers

```python
from score import P, kit, seq, play, swing, pitch, balance, finish
```

- `P(name, program, bank=0, sf2=GM_SF, **kw)`: `Part` shorthand; `kit(name, kit_number, sf2=GU_SF, **kw)`: a drum part on channel 10.
- `seq("A4/.5 r/1 C5+E5/1.5 | ...", start=beat, shift=semitones)`: each token is `pitch/beats`; `r` is a rest, `+` stacks a chord, `|` is only a bar mark (not checked). Returns `[(beat, dur, midi)]`, which you can filter or transpose before `play`.
- `play(part, notes, vel=90, extend=0, accent=None)`: add notes; `extend` lengthens each (pedal, let ring), `accent(beat) -> velocity offset`.
- `swing(part, ratio=0.62, unit=0.5)`: call after all notes are added. `unit=0.5` swings 8ths (0.67 triplet feel, 0.6-0.64 a light lounge swing); `unit=0.25` swings 16ths (0.54-0.58 a funk / lo-fi push).
- `pitch(part, song, vib=None, slide=None, scoop=None, fall=None, max_slide=5, when=None, seed=0)`: a player's pitch for a melodic line, call after its notes are added. `vib=(cents, hz, delay_s)` vibrato on long notes, fading in; `slide=seconds` portamento into a note that follows without a gap (at most `max_slide` semitones); `scoop=(semitones, seconds)` notes after a rest rise into pitch; `fall=(semitones, seconds)` notes before a rest drop away; `when(prev, note) -> bool` picks the slides (e.g. `lambda a, b: b.dur >= .9`: only into long notes). Starting values: erhu-style violin `slide=.13, scoop=(1, .1)` and no extra vibrato (the samples have ±17 c); flute or xiao `vib=(22, 4.8, .35), scoop=(1, .14), fall=(1, .3)`; zither left hand `vib=(28, 5.4, .5)`.
- `balance(placed, song, sections, lead, beats_per_bar)`: LUFS of the melody vs everything else per section. `sections=[(label, first_bar, end_bar)]`, `lead` is a set of melody part names.
- `finish(name, parts, song, sections, lead, beats_per_bar=4, outdir=None, lufs=-16, loop=False, **mix_args)`: render, mix, export to `./out/<name>/`, print the balance, run `qc.py` (with `--loop` for loops). Every piece in `examples/styles/` uses it.

## cues: timing to a video

`load_cues(path)` returns `{"duration", "bpm", "hits", "beats", "vo", "markers"}`. `fit_bpm(times, lo, hi, div=2)` returns `(bpm, offset_s, worst_err_s)`, taking the slowest tempo within 5 ms of the best fit. `seconds_to_beat(t, bpm, offset)` converts seconds to beats. Beat 0 of the score is at 0 s; if `offset` is not 0, pad that much silence in front or shift every note.

## Command-line tools

| Command | Purpose |
|---|---|
| `run.sh qc.py mix.wav [--lufs -14] [--tp -1] [--duration s] [--cues f] [--voice vo.wav --voice-offset s] [--loop]` | Delivery checks, exit 1 on failure; `--voice` checks that a voice-over was not compressed in the mix; `--loop` checks the loop seam (click, or a drop of more than 6 dB back into the start) |
| `run.sh review.py piece.py [--min-overlap 0.5] [--show 12]` | Reads the score without rendering: notes and range per part, minor 2nds / 9ths of ≥ 0.5 beat between different parts (wrong notes or voicings); major 7ths are only counted. The piece must build its `Part`s at module level (lists and dicts are scanned too) and render under `if __name__ == "__main__":` |
| `run.sh serve.py DIR [port]` | Read-only listening server with Range requests and no directory listing |
