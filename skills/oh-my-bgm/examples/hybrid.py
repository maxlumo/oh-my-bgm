"""Synthesised trailer layers that a chamber sample library does not have:
ensemble "taiko" drums, sub booms, risers, reverse swells. All return stereo float32 at SR."""
from __future__ import annotations

import numpy as np
from scipy import signal

from orch import SR

_rng = np.random.default_rng(11)


def _st(m, width=0.0, seed=0):
    """mono -> stereo with an M/S side made from a decorrelated (all-pass) copy."""
    if width <= 0:
        return np.stack([m, m], 1).astype(np.float32)
    rng = np.random.default_rng(seed)
    side = m.copy()
    for _ in range(4):  # random first-order all-passes: phase-only, keeps mono sum = m
        c = rng.uniform(-0.7, 0.7)
        side = signal.lfilter([c, 1], [1, c], side)
    side = side * width
    return np.stack([m + side, m - side], 1).astype(np.float32)


def _noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def taiko(vel=1.0, pitch=58.0, seed=0, dur=1.6):
    """Big low drum: pitched membrane (falling pitch) + skin noise + room-ish body."""
    N = int(dur * SR)
    t = np.arange(N) / SR
    f = pitch * (1 + 1.6 * np.exp(-t / 0.012))           # strike pitch drop
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.42)
    body += 0.35 * np.sin(1.59 * ph + 0.3) * np.exp(-t / 0.18)  # membrane mode (non-harmonic)
    body += 0.18 * np.sin(2.14 * ph + 1.1) * np.exp(-t / 0.09)
    skin = signal.sosfilt(signal.butter(2, [180, 2400], "band", fs=SR, output="sos"),
                          _noise(N, seed)) * np.exp(-t / 0.035) * 0.9
    x = body + skin
    x = np.tanh(1.8 * x) / np.tanh(1.8)
    return _st(x * vel * 0.9, 0.25, seed)


def ensemble_hit(vel=1.0, seed=0, players=4):
    """Several taikos struck nearly together (flam), slightly different tunings."""
    rng = np.random.default_rng(seed)
    out = None
    for k in range(players):
        d = int(abs(rng.normal(0, 0.006)) * SR)
        x = taiko(vel * rng.uniform(0.8, 1.0), pitch=rng.uniform(52, 66), seed=seed * 10 + k)
        x = np.pad(x, ((d, 0), (0, 0)))
        out = x if out is None else _sum(out, x)
    return out / np.sqrt(players)


def boom(vel=1.0, seed=0, dur=4.0):
    """Sub boom: sine drop 70 -> 32 Hz + soft click, long decay."""
    N = int(dur * SR)
    t = np.arange(N) / SR
    f = 32 + 38 * np.exp(-t / 0.08)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 1.1)
    click = signal.sosfilt(signal.butter(2, 1500, "low", fs=SR, output="sos"),
                           _noise(N, seed)) * np.exp(-t / 0.01) * 0.4
    x = np.tanh(1.5 * (x + click)) / np.tanh(1.5)
    return _st(x * vel, 0.0)


def riser(dur=4.0, seed=0, f0=300, f1=7000):
    """Filtered noise + rising tone, ends at its last sample (align the END to the hit)."""
    N = int(dur * SR)
    t = np.arange(N) / SR
    p = t / dur
    nz = _noise(N, seed)
    # time-varying band-pass via block processing
    out = np.zeros(N)
    blk = 1024
    zi = None
    for i in range(0, N, blk):
        fc = f0 * (f1 / f0) ** (p[i] ** 1.6)
        sos = signal.butter(2, [fc / 1.6, min(fc * 1.6, SR / 2 - 100)], "band", fs=SR,
                            output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[i:i + blk], zi = signal.sosfilt(sos, nz[i:i + blk], zi=zi)
    tone_f = 110 * 2 ** (p ** 1.4 * 3)
    tone = np.sin(2 * np.pi * np.cumsum(tone_f) / SR) * 0.12
    x = (out * 1.6 + tone) * (p ** 2.2)
    return _st(x, 0.8, seed)


def reverse_swell(dur=2.5, seed=0):
    """Reverse cymbal-like swell: HP noise with exponential rise, ends at the hit."""
    N = int(dur * SR)
    t = np.arange(N) / SR
    x = signal.sosfilt(signal.butter(2, 3500, "high", fs=SR, output="sos"), _noise(N, seed))
    x *= np.exp(-(dur - t) / 0.55)
    return _st(x * 0.9, 0.9, seed)


def braam(dur=3.5, notes=(38, 45, 50), seed=0, drive=2.5):
    """Low brass-like "braam": detuned saw stacks, filter opening then closing, saturated."""
    N = int(dur * SR)
    t = np.arange(N) / SR
    rng = np.random.default_rng(seed)
    x = np.zeros(N)
    for note in notes:
        f = 440 * 2 ** ((note - 69) / 12)
        for _ in range(6):
            fd = f * 2 ** (rng.normal(0, 9) / 1200)
            ph = (fd * t + rng.uniform()) % 1.0
            x += 2 * ph - 1
    x /= np.sqrt(len(notes) * 6)
    cut = 180 + 2600 * np.exp(-((t - 0.25) / 0.35) ** 2) + 600 * np.exp(-t / 1.2)
    out = np.zeros(N)
    blk = 512
    zi = None
    for i in range(0, N, blk):
        sos = signal.butter(2, min(cut[i], SR / 2 - 100), "low", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[i:i + blk], zi = signal.sosfilt(sos, x[i:i + blk], zi=zi)
    env = np.minimum(1, t / 0.04) * np.exp(-t / 1.6)
    out = np.tanh(drive * out * env) / np.tanh(drive)
    return _st(out, 0.5, seed)


def _sum(a, b):
    n = max(len(a), len(b))
    a = np.pad(a, ((0, n - len(a)), (0, 0)))
    b = np.pad(b, ((0, n - len(b)), (0, 0)))
    return a + b


class Layer:
    """Accumulates one-shots on the timeline (sync = start, or end for risers/swells)."""

    def __init__(self, seconds):
        self.buf = np.zeros((int(seconds * SR), 2), np.float32)

    def at(self, t, x, gain=1.0, end=False):
        i = int(round((t * SR) - (len(x) if end else 0)))
        if i < 0:
            x, i = x[-i:], 0
        j = min(len(self.buf), i + len(x))
        self.buf[i:j] += x[: j - i] * gain
        return self
