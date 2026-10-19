"""Timing helpers: read a video cues.json and fit the music's tempo grid to its hit points.

    from cues import load_cues, fit_bpm
    c = load_cues("cues.json")                 # dict with "hits", "beats", "duration", ...
    bpm, offset, err = fit_bpm(c["hits"] + c["beats"], lo=80, hi=130, div=2)
    # beat b of the score sounds at  offset + b * 60 / bpm  seconds

cues.json is the video-production skill's format: {"duration", "bpm", "markers": [{"type": "hit"
| "beat" | "shot" | "vo" | "text", "t": seconds, "end"?: seconds}, ...]}.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def load_cues(path) -> dict:
    d = json.loads(Path(path).read_text())
    marks = d.get("markers", [])
    return {"duration": d.get("duration"), "bpm": d.get("bpm"), "master_clock": d.get("master_clock"),
            "hits": [m["t"] for m in marks if m.get("type") == "hit"],
            "beats": [m["t"] for m in marks if m.get("type") == "beat"],
            "vo": [(m["t"], m.get("end", m["t"])) for m in marks if m.get("type") == "vo"],
            "markers": marks}


def fit_bpm(times, lo=70.0, hi=140.0, div=2, step=0.1):
    """Tempo (and grid offset in s) whose 1/div-beat grid best fits the given times.
    Returns (bpm, offset_s, worst_error_s). Prefers the slowest tempo within 5 ms of the best."""
    times = np.asarray(sorted(times), float)
    if len(times) < 2:
        return float(lo), float(times[0]) if len(times) else 0.0, 0.0
    best = []
    for bpm in np.arange(lo, hi + 1e-9, step):
        g = 60.0 / bpm / div
        # offset that best aligns the first time; then measure the worst residual
        for anchor in times[:3]:
            r = ((times - anchor + g / 2) % g) - g / 2
            best.append((np.abs(r).max(), bpm, anchor % (60.0 / bpm)))
    best.sort()
    top = best[0][0]
    for err, bpm, off in sorted(best, key=lambda x: x[1]):
        if err <= top + 0.005:
            return round(float(bpm), 2), float(off), float(err)
    return float(best[0][1]), float(best[0][2]), float(top)


def seconds_to_beat(t, bpm, offset=0.0):
    return (t - offset) * bpm / 60.0
