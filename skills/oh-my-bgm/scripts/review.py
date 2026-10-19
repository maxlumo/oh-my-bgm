"""Score review without ears: load a piece (its module-level code builds the Parts, __main__ is not run) and
list half-step clashes between sustained notes of different parts, plus range and density facts.

usage: <skill>/scripts/run.sh <skill>/scripts/review.py piece.py [--min-overlap 0.5] [--show 12]

A clash = two notes in different parts sounding together for >= min-overlap beats with the upper one a minor
2nd / minor 9th / two octaves + a minor 2nd above the lower one (C under Db). Major 7ths (C under B) are
counted separately as colour: usually fine (maj7, 13 over b7 spread out). Some clashes are wanted (b9 on a
dominant, Hijaz, a passing note over a pad); the rest are wrong notes or voicings that put a 9th next to a
3rd in another part. Drum parts (channel 9) are skipped. Read every clash it prints and decide.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from orch import Part  # noqa: E402

NAMES = "C C# D Eb E F F# G Ab A Bb B".split()


def name(p):
    return f"{NAMES[p % 12]}{p // 12 - 1}"


def clashes(parts, min_overlap=0.5):
    ev = sorted(((nt.beat, nt.beat + nt.dur, nt.pitch, p.name) for p in parts if p.channel != 9 for nt in p.notes))
    out = []
    for i, (s, e, p, a) in enumerate(ev):
        for s2, e2, p2, b in ev[i + 1:]:
            if s2 >= e:
                break
            if a == b:
                continue
            ov = min(e, e2) - max(s, s2)
            d = abs(p - p2)
            if ov >= min_overlap and d <= 25 and d % 12 in (1, 11):
                out.append((max(s, s2), ov, a, name(p), b, name(p2), "clash" if d % 12 == 1 else "maj7"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("piece")
    ap.add_argument("--min-overlap", type=float, default=0.5)
    ap.add_argument("--show", type=int, default=12)
    a = ap.parse_args()
    path = Path(a.piece).resolve()
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("piece", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    parts, seen = [], set()
    for v in vars(mod).values():  # module-level Parts, also inside lists / dicts
        for p in (v if isinstance(v, (list, tuple)) else v.values() if isinstance(v, dict) else [v]):
            if isinstance(p, Part) and id(p) not in seen:
                seen.add(id(p))
                parts.append(p)
    song = getattr(mod, "song", None)
    bpb = getattr(mod, "B", 4)
    print(f"{path.name}: {len(parts)} parts" + (f", {song.beats / bpb:.0f} bars of {bpb}, "
                                                 f"{song.t(song.beats):.1f} s" if song else ""))
    for p in parts:
        if p.notes and p.channel != 9:
            lo, hi = min(nt.pitch for nt in p.notes), max(nt.pitch for nt in p.notes)
            print(f"  {p.name:18s} {len(p.notes):4d} notes  {name(lo)}-{name(hi)}")
        elif p.notes:
            print(f"  {p.name:18s} {len(p.notes):4d} hits")
    allc = clashes(parts, a.min_overlap)
    cl = [c for c in allc if c[6] == "clash"]
    pairs = Counter(tuple(sorted((c[2], c[4]))) for c in cl)
    print(f"minor-2nd/9th clashes >= {a.min_overlap} beat: {len(cl)} (major-7th colours: {len(allc) - len(cl)})"
          + (f"  by pair: {dict(pairs.most_common(5))}" if cl else ""))
    for beat, ov, pa, na, pb, nb, _ in sorted(cl, key=lambda c: -c[1])[: a.show]:
        print(f"  bar {beat // bpb + 1:3.0f} beat {beat % bpb + 1:4.2f}  {pa} {na} vs {pb} {nb}  ({ov:.2f} beats)")


if __name__ == "__main__":
    main()
