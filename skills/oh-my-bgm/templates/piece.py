"""Template cue: copy this file into your production folder and edit the SCORE section.

  <skill>/scripts/run.sh piece.py [cues.json]

Shows the whole pipeline in ~30 s of music: a General MIDI score in code, two SoundFonts mixed
per part (MuseScore General for piano / Expr. strings / pad, GeneralUser GS for drums and bass),
optional tempo fitting to a video's cues.json, mixing, mastering to -14 LUFS, and QC.
"""
import os
import subprocess
import sys
from pathlib import Path

SKILL = Path(os.environ.get("MUSIC_SKILL_DIR", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(SKILL / "scripts"))

from pedalboard import HighpassFilter, HighShelfFilter, LowpassFilter, PeakFilter  # noqa: E402

from cues import fit_bpm, load_cues  # noqa: E402
from orch import GM_SF, GU_SF, Part, Song, export, mix, n, nearest, render_parts  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
NAME = "cue"

# ---------------------------------------------------------------- timing
BARS, DURATION = 10, None
bpm, hits = 96.0, []
if len(sys.argv) > 1:  # follow a video: fit the tempo so its hits land on the 8th-note grid
    c = load_cues(sys.argv[1])
    hits = c["hits"] + c["beats"]
    if len(hits) >= 2:
        bpm, _, err = fit_bpm(hits, lo=84, hi=120, div=2)
        print(f"fitted {bpm} BPM, worst hit error {err * 1000:.0f} ms")
    DURATION = c["duration"]
    if DURATION:  # whole bars that leave >= 1.5 s for the last chord to ring, ending exactly on time
        BARS = max(2, int((DURATION - 1.5) / (240 / bpm)))
tail = DURATION - BARS * 240 / bpm if DURATION else 3.0
song = Song(bpm=bpm, beats=BARS * 4, tail=tail, seed=1)
B = 4

# ---------------------------------------------------------------- SCORE (edit here)
PROG = ["D", "A", "Bm", "G"]  # one chord per bar, looped
TONES = {"D": (2, 6, 9), "A": (9, 1, 4), "Bm": (11, 2, 6), "G": (7, 11, 2)}


def P(name, program, sf2, bank=0, **mix_settings):
    """A General MIDI part on a chosen SoundFont."""
    return Part(name, program, sf2=str(sf2), bank=bank, **mix_settings)


piano = P("piano", 0, GM_SF, bank=8, pan=-.15, level=-20, send=-12, bus="keys",
          eq=[HighpassFilter(70), PeakFilter(300, -2, 1)])
strings = P("strings", 49, GM_SF, bank=17, expr_cc=2, players=2, pan=.1, width=1.4, level=-24,
            send=-8, bus="strings", legato=.1, eq=[HighpassFilter(150)])
pad = P("pad", 89, GM_SF, pan=0, width=1.6, level=-30, send=-10, bus="keys", legato=.2,
        eq=[HighpassFilter(200), LowpassFilter(6000)])
bass = P("bass", 33, GU_SF, width=.3, level=-22, send=-30, bus="rhythm",
         eq=[HighpassFilter(35), LowpassFilter(5000)])
drums = P("drums", 0, GU_SF, channel=9, level=-21, send=-16, bus="drums", jitter_ms=3,
          eq=[HighpassFilter(30)])
half = BARS // 2
for bar in range(BARS):
    r, t, f = TONES[PROG[bar % len(PROG)]]
    last = bar == BARS - 1
    for i in range(8):  # piano 8th arpeggio
        p = [nearest(r, n("D3")), nearest(f, n("A3")), nearest(r, n("D4")), nearest(t, n("F#4"))][i % 4]
        piano.add(bar * B + i * .5, 4 if last else .9, p, 60 - (i % 2) * 6)
        if last:
            break
    for p in (nearest(r, n("D3")), nearest(t, n("F#3")), nearest(f, n("A3"))):
        pad.add(bar * B, 4, p, 45)
    if bar >= half:
        for p in (nearest(r, n("D4")), nearest(f, n("A4")), nearest(t, n("F#5"))):
            strings.add(bar * B, 4, p, 70 + 4 * (bar - half))  # expr_cc turns this into CC2 swells
        bass.add(bar * B, 1.5, nearest(r, n("D2")), 88)
        bass.add(bar * B + 2, 1.5, nearest(r, n("D2")), 80)
        if not last:
            for beat in (0, 2.5):
                drums.add(bar * B + beat, .25, 36, 96)  # kick
            for beat in (1, 3):
                drums.add(bar * B + beat, .25, 38, 90)  # snare
            for i in range(8):
                drums.add(bar * B + i * .5, .2, 42, 56 + (12 if i % 2 == 0 else 0))  # closed hat
drums.add((BARS - 1) * B, 3, 49, 100)  # crash on the last bar
for t_hit in hits:  # every video hit gets a kick + crash on the fitted grid
    b = round(t_hit / song.spb * 2) / 2
    drums.add(b, .25, 36, 110)
    drums.add(b, 2, 49, 92)

PARTS = [piano, strings, pad, bass, drums]

# ---------------------------------------------------------------- render, mix, master, QC
if __name__ == "__main__":
    stems = render_parts(PARTS, song, OUT / "_render")
    master, _, buses, levels = mix(
        PARTS, stems, song, lufs=-14.0,
        hall=dict(rt_low=1.8, rt_mid=1.6, rt_high=0.9, predelay=0.025, length=3.5),
        tone=[PeakFilter(250, -1.5, 0.8), HighShelfFilter(cutoff_frequency_hz=10000, gain_db=1.5)])
    rep = export(master, buses, OUT, NAME, meta={"bpm": bpm, "stem_lufs_raw": levels,
                                                  "onset_ms": render_parts.onsets})
    print({k: rep[k] for k in ("file", "seconds", "lufs", "tp", "lra")})
    qc = [sys.executable, str(SKILL / "scripts" / "qc.py"), rep["file"], "--lufs", "-14"]
    if len(sys.argv) > 1:
        qc += ["--cues", sys.argv[1]] + (["--duration", str(DURATION)] if DURATION else [])
    sys.exit(subprocess.run(qc, stdout=subprocess.DEVNULL).returncode)
