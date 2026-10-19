"""Delivery checks for a mixed music file. Exit 1 if a hard check fails.

usage: <skill>/scripts/run.sh <skill>/scripts/qc.py mix.wav [--lufs -14] [--tp -1.0]
            [--duration 30.0] [--cues cues.json] [--voice vo.wav --voice-offset 0] [--loop]
Hard checks: integrated loudness within ±1 LU of target, true peak <= limit, no non-finite
samples, duration (if given) within 20 ms, mono compatibility (L/R correlation > 0), with --loop
(an optional seamless loop made with mix(loop=True)): no click where the end joins the start and no drop of more
than 6 dB across the seam (0.5 s either side), and with
--voice: while speaking, the mix's peak-to-loudness ratio may be at most 1 dB below the voice's own
(more means the voice was compressed / limited / saturated in the mix, heard as a hard, rough voice).
Reported, not failed: loudness every 2 s, band balance, onset jump at every cues.json hit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pyloudnorm
import soundfile as sf
from scipy import ndimage, signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from orch import measure  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    ap.add_argument("--duration", type=float)
    ap.add_argument("--cues")
    ap.add_argument("--voice", help="the original voiceover, to check it was not squashed")
    ap.add_argument("--voice-offset", type=float, default=0.0, help="where the voiceover starts (s)")
    ap.add_argument("--loop", action="store_true", help="the file is a seamless loop: check the seam")
    a = ap.parse_args()
    x, sr = sf.read(a.wav, dtype="float64", always_2d=True)
    m = measure(Path(a.wav))
    rep = {"file": a.wav, "seconds": round(len(x) / sr, 3), **m}
    fails = []
    if abs(m["lufs"] - a.lufs) > 1.0:
        fails.append(f"loudness {m['lufs']} LUFS, target {a.lufs} ±1")
    if m["tp"] > a.tp:
        fails.append(f"true peak {m['tp']} dBTP > {a.tp}")
    if not np.isfinite(x).all():
        fails.append("non-finite samples")
    if a.duration and abs(len(x) / sr - a.duration) > 0.02:
        fails.append(f"duration {len(x) / sr:.3f} s, expected {a.duration}")
    corr = float(np.corrcoef(x[:, 0], x[:, -1])[0, 1]) if x.shape[1] > 1 else 1.0
    rep["stereo_corr"] = round(corr, 3)
    if corr <= 0:
        fails.append(f"L/R correlation {corr:.2f} (mono playback will cancel)")
    if a.loop:
        jump = float(np.abs(x[0] - x[-1]).max())
        step = float(np.percentile(np.abs(np.diff(x, axis=0)), 99.9))
        h = int(0.5 * sr)
        rms = lambda y: 10 * np.log10((y ** 2).mean() + 1e-20)  # noqa: E731
        lv = rms(x[:h]) - rms(x[-h:])
        rep["loop_seam"] = {"jump": round(jump, 4), "p99.9_step": round(step, 4), "start_minus_end_db": round(lv, 1)}
        if jump > max(0.02, 3 * step):
            fails.append(f"loop seam clicks: end-to-start jump {jump:.3f} (normal steps up to {step:.3f})")
        if lv < -6:  # louder after the seam is just a new entry; quieter means the loop drops out
            fails.append(f"loop seam drops {lv:+.1f} dB (0.5 s after vs before the seam)")
    meter = pyloudnorm.Meter(sr, block_size=3.0)
    rep["short_term_lufs"] = {f"{t:.0f}": round(meter.integrated_loudness(x[int(t * sr): int((t + 3) * sr)]), 1)
                              for t in np.arange(0, max(0, len(x) / sr - 3), 2)}
    bands = [(20, 60), (60, 150), (150, 400), (400, 1500), (1500, 5000), (5000, 16000)]
    rep["band_db"] = {}
    for lo, hi in bands:
        y = signal.sosfilt(signal.butter(4, [lo, hi], "band", fs=sr, output="sos"), x.mean(1))
        rep["band_db"][f"{lo}-{hi}"] = round(10 * np.log10((y ** 2).mean() + 1e-20), 1)
    if a.cues:
        from cues import load_cues
        mono = x.mean(1)

        def lvl(t0, t1):
            seg = mono[max(0, int(t0 * sr)): int(t1 * sr)]
            return 10 * np.log10((seg ** 2).mean() + 1e-12) if len(seg) else -120.0
        rep["hits"] = {f"{t:.3f}": round(lvl(t, t + 0.05) - lvl(t - 0.15, t - 0.01), 1)
                       for t in load_cues(a.cues)["hits"]}
    if a.voice:  # was the voice compressed in the mix? peak-to-loudness ratio, alone vs in the mix
        v, vsr = sf.read(a.voice, dtype="float64", always_2d=True)
        v = v.mean(1)
        if vsr != sr:
            g = np.gcd(sr, vsr)
            v = signal.resample_poly(v, sr // g, vsr // g)
        v = np.pad(v, (int(a.voice_offset * sr), 0))[: len(x)]
        e = np.sqrt(np.maximum(ndimage.uniform_filter1d(v ** 2, int(0.05 * sr)), 0))
        sp = 20 * np.log10(e + 1e-12) > 20 * np.log10(e.max() + 1e-12) - 35  # speaking
        sp = ndimage.binary_closing(sp, structure=np.ones(int(0.25 * sr)))
        if sp.any():
            mt = pyloudnorm.Meter(sr)
            tp = lambda y: 20 * np.log10(np.abs(signal.resample_poly(y, 4, 1, axis=0)).max() + 1e-12)  # noqa: E731
            vs = np.stack([v, v], 1)[sp]
            xm = x[: len(v)][sp]
            plr_v = tp(vs) - mt.integrated_loudness(vs)
            plr_m = tp(xm) - mt.integrated_loudness(xm)
            rep["voice_plr_db"] = {"voice_alone": round(plr_v, 1), "in_mix": round(plr_m, 1),
                                   "drop": round(plr_v - plr_m, 1)}
            if plr_v - plr_m > 1.0:
                fails.append(f"voice compressed in the mix: its peak-to-loudness ratio dropped "
                             f"{plr_v - plr_m:.1f} dB (allowed 1.0). Mix it with gain only, see SKILL.md")
    rep["fails"] = fails
    print(json.dumps(rep, indent=1, ensure_ascii=False, default=float))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
