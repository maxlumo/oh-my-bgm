#!/usr/bin/env bash
# Install what the oh-my-bgm skill needs, into the user's home. Idempotent: each step
# checks first and skips what is already there. About 100 MB.
#
#   FluidSynth 2.4.4 (built from source into ~/.local) + MuseScore General SF3 + GeneralUser GS
#   2.0.3 (into ~/sound-libs, override with SOUND_LIBS) + the Python environment (uv).
#
# Linux x86_64; needs uv, git, a C++ compiler, curl and ffmpeg. FluidSynth's build dependencies
# (glib2, libsndfile headers) are installed with sudo dnf/apt when available.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIBS="${SOUND_LIBS:-$HOME/sound-libs}"; SRC="${SRC_DIR:-$HOME/src}"
PREFIX="$HOME/.local"; export PATH="$PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$PREFIX/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
[ $# -eq 0 ] || { echo "setup.sh takes no options"; exit 2; }
say() { printf '\n== %s\n' "$*"; }
need() { command -v "$1" >/dev/null || { echo "missing: $1 — $2"; exit 1; }; }
need uv "https://docs.astral.sh/uv/"; need git "package manager"; need g++ "gcc-c++ / g++"
need ffmpeg "ffmpeg (static build in ~/.local/bin is fine)"; need curl "curl"
mkdir -p "$LIBS" "$SRC" "$PREFIX/bin"

syspkgs() {  # $@: dnf names ; apt names after a literal --
  local dnf=() apt=() side=dnf
  for p in "$@"; do if [ "$p" = -- ]; then side=apt; elif [ $side = dnf ]; then dnf+=("$p"); else apt+=("$p"); fi; done
  if command -v dnf >/dev/null && sudo -n true 2>/dev/null; then sudo dnf -y -q install "${dnf[@]}"
  elif command -v apt-get >/dev/null && sudo -n true 2>/dev/null; then sudo apt-get -y -qq install "${apt[@]}"
  else echo "install these system packages yourself: ${dnf[*]} (dnf) / ${apt[*]} (apt)"; fi
}

say "cmake"
command -v cmake >/dev/null || uv tool install -q cmake

say "FluidSynth 2.4.4"
if fluidsynth --version >/dev/null 2>&1; then echo "present: $(fluidsynth --version | head -1)"; else
  syspkgs glib2-devel libsndfile-devel -- libglib2.0-dev libsndfile1-dev
  [ -d "$SRC/fluidsynth" ] || git clone -q --depth 1 --branch v2.4.4 https://github.com/FluidSynth/fluidsynth.git "$SRC/fluidsynth"
  cmake -S "$SRC/fluidsynth" -B "$SRC/fluidsynth/build" -DCMAKE_INSTALL_PREFIX="$PREFIX" -DCMAKE_BUILD_TYPE=Release \
    -Denable-libinstpatch=off -Denable-pulseaudio=off -Denable-alsa=off -Denable-jack=off -Denable-sdl2=off \
    -Denable-pipewire=off -Denable-readline=off >/dev/null
  cmake --build "$SRC/fluidsynth/build" -j "$(nproc)" >/dev/null && cmake --install "$SRC/fluidsynth/build" >/dev/null
  fluidsynth --version | head -1
fi

say "SoundFonts"
[ -s "$LIBS/MuseScore_General.sf3" ] || curl -sSfL -o "$LIBS/MuseScore_General.sf3" \
  https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General.sf3
[ -s "$LIBS/GeneralUser-GS.sf2" ] || curl -sSfL -o "$LIBS/GeneralUser-GS.sf2" \
  https://github.com/mrbumpy409/GeneralUser-GS/raw/main/GeneralUser-GS.sf2
ls -la "$LIBS"/*.sf[23]

say "Python environment"
"$HERE/run.sh" -c "import orch, cues; print('python env ok')"

say "smoke test: one piano note through each SoundFont"
"$HERE/run.sh" - <<'PY'
import tempfile, mido, subprocess, soundfile as sf, numpy as np
from orch import GM_SF, GU_SF, _bin
d = tempfile.mkdtemp(); m = mido.MidiFile(); t = mido.MidiTrack(); m.tracks.append(t)
t += [mido.Message("note_on", note=60, velocity=100), mido.Message("note_off", note=60, time=480)]
m.save(f"{d}/t.mid")
for sf2 in (GM_SF, GU_SF):
    subprocess.run([_bin("fluidsynth"), "-q", "-n", "-i", "-F", f"{d}/t.wav", "-r", "48000", str(sf2), f"{d}/t.mid"], check=True)
    x, _ = sf.read(f"{d}/t.wav"); assert np.abs(x).max() > 1e-3, f"silent render: {sf2}"
    print("ok:", sf2.name, "peak", round(float(np.abs(x).max()), 3))
PY
