<p align="center">
  <img src="assets/logo.svg" width="128" alt="Oh My BGM">
</p>

<h1 align="center">Oh My BGM</h1>

<p align="center"><b>Background music, written as code.</b><br>
An agent skill that composes, plays, mixes and checks instrumental music in Python.</p>

---

Your agent can't hear a thing. It writes music anyway.

Tell it a scene, like "rain on a study window", "a heist being planned" or "a launch that should feel like sunrise".
It picks a style, writes every note as a line of Python, lets FluidSynth play each part on two free SoundFonts, mixes
and masters in code, and then measures what it made: loudness, true peak, clipping, phase, clashing notes. A human
gets the last word. Out come a WAV, an MP3, stems and a QC report.

No DAW, no VSTs, no sample packs to buy. The same code always renders the same track.

## Listen

Seven of the pieces in `skills/oh-my-bgm/examples/styles/`; each renders in about a minute:

| Piece | Sounds like | Built from |
|---|---|---|
| After the Rain (`after_rain_piano.py`) | grief that slowly lets light in | piano, cello, violin |
| Steam & Static (`lofi_study.py`) | calm, cosy, a little nostalgic | lo-fi beat, Rhodes, nylon guitar, rain and vinyl |
| Toward the Light (`uplifting_launch.py`) | rising hope, a door opening | piano pulse, then strings, drums, everyone |
| Wheatfield Town (`pastoral_orchestra.py`) | warm, bustling, wholesome | a small orchestra in 3/4 |
| Ember Tango (`tango_nuevo.py`) | intense, elegant, a little dangerous | bandoneon and violin, 3+3+2 |
| Stratagems (`guofeng_pentatonic.py`) | a mind weighing its next move | pentatonic ostinato, tremolo, slides, taiko |
| Copper Wedding (`balkan_brass.py`) | exuberant, sweaty, irresistible | a brass band in 9/8 |

## Install

**Claude Code**

```
/plugin marketplace add maxlumo/oh-my-bgm
/plugin install oh-my-bgm@maxlumo
```

On Claude Code 2.1.275 or later, `/plugin install oh-my-bgm --marketplace maxlumo/oh-my-bgm` does both in one step.

**Codex**

```bash
codex plugin marketplace add maxlumo/oh-my-bgm
codex plugin add oh-my-bgm@maxlumo
```

**Any other agent**: copy `skills/oh-my-bgm` into the folder where the agent looks for skills.

Then ask for music. The first time, the agent runs the skill's `scripts/setup.sh`, which installs FluidSynth, both
SoundFonts and a Python environment (about 100 MB; Linux x86_64 with `uv`, `git`, a C++ compiler, `curl` and `ffmpeg`).
[`SKILL.md`](skills/oh-my-bgm/SKILL.md) is the agent's manual; `references/` next to it holds the style guide, mixing
notes and the SoundFont maps.

Without an agent:

```bash
git clone https://github.com/maxlumo/oh-my-bgm && cd oh-my-bgm/skills/oh-my-bgm
scripts/setup.sh
scripts/run.sh examples/styles/lofi_study.py      # -> ./out/lofi_study/
```

## How it works

```
score in Python ─▶ one MIDI file per part (mido) ─▶ FluidSynth plays it on MuseScore General / GeneralUser GS ─▶ stems
      ─▶ mix: levels, EQ and compression (pedalboard), halls (convolution in NumPy / SciPy)
      ─▶ master: loudness (pyloudnorm), true-peak limiter ─▶ WAV · MP3 (ffmpeg) · stems ─▶ qc.py
```

FluidSynth is the only thing that makes sound: it plays the notes with the SoundFont samples. pedalboard (Spotify's
audio effects library) only shapes those recordings afterwards.

## License

MIT for the code (see [LICENSE](LICENSE)). `setup.sh` downloads the SoundFonts; they are not in this repository:
MuseScore General (MIT) and GeneralUser GS 2.0.3 (free for any music, including commercial).
