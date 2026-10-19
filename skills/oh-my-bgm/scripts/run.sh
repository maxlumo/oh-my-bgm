#!/usr/bin/env bash
# Run a Python file with this skill's environment (kept outside the skill folder).
#   <skill>/scripts/run.sh piece.py [args...]
#   <skill>/scripts/run.sh <skill>/scripts/qc.py out/mix.wav --lufs -14
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$HOME/.cache/oh-my-bgm/venv}"
export MUSIC_SKILL_DIR="${MUSIC_SKILL_DIR:-$(dirname "$HERE")}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$HERE${PYTHONPATH:+:$PYTHONPATH}"
export LD_LIBRARY_PATH="${FLUIDSYNTH_LIB:-$HOME/.local/lib64}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec uv run --quiet --frozen --project "$HERE" python "$@"
