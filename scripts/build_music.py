#!/usr/bin/env python3
"""Synthesise the explainer video's backing track: an original, light-hearted loop.

No samples and no third-party music, so there is nothing to license and it can be
used on every platform. Writes public/video/setsoflove-explainer-music.m4a (30.5 s).

Needs: numpy, scipy and ffmpeg.
Run: python3 scripts/build_music.py
"""
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "video" / "setsoflove-explainer-music.m4a"
SR = 44100
BPM = 124
BEAT = 60 / BPM
EIGHTH = BEAT / 2
BAR = BEAT * 4
TOTAL = 30.5
rng = np.random.default_rng(7)

NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}


def hz(name):
    """'C4' -> frequency."""
    pitch, octave = name[:-1], int(name[-1])
    return 440 * 2 ** ((NOTE[pitch] + 12 * (octave + 1) - 69) / 12)


buf = np.zeros(int((TOTAL + 2) * SR))


def put(t, sig, gain=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    end = min(len(buf), i + len(sig))
    buf[i:end] += sig[: end - i] * gain


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def pluck(f, dur=0.5, bright=1.0):
    """Ukulele-ish pluck: a few harmonics with a quick decay."""
    t = tt(dur)
    sig = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (7 + 5 * k) / bright)
              for k, a in enumerate([1.0, 0.5, 0.25, 0.12], start=1))
    sig *= np.minimum(t / 0.004, 1)
    return sig


def bass(f, dur=0.45):
    t = tt(dur)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 4.5) * np.minimum(t / 0.006, 1)


def bell(f, dur=0.35):
    t = tt(dur)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 3 * f * t)) * np.exp(-t * 9) * np.minimum(t / 0.003, 1)


def kick(dur=0.3):
    t = tt(dur)
    f = 55 + 90 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)


def hat(dur=0.05):
    t = tt(dur)
    n = rng.standard_normal(len(t))
    sos = butter(2, 7000, "highpass", fs=SR, output="sos")
    return sosfilt(sos, n) * np.exp(-t * 70)


def clap(dur=0.12):
    t = tt(dur)
    n = rng.standard_normal(len(t))
    sos = butter(2, [1200, 5000], "bandpass", fs=SR, output="sos")
    return sosfilt(sos, n) * np.exp(-t * 32)


# C - G - Am - F, one bar each.
CHORDS = [("C", ["C4", "E4", "G4"], "C2"), ("G", ["B3", "D4", "G4"], "G2"),
          ("A", ["C4", "E4", "A4"], "A2"), ("F", ["C4", "F4", "A4"], "F2")]
# Melody per bar on eighth-note steps (None = rest). Pentatonic and bouncy.
A_PART = [
    ["E5", None, "G5", "E5", None, "C5", "E5", "G5"],
    ["D5", None, "G5", "D5", None, "B4", "D5", "G5"],
    ["C5", None, "E5", "C5", None, "A4", "C5", "E5"],
    ["A4", "C5", "F5", None, "E5", "C5", "A4", None],
]
B_PART = [
    ["G5", "E5", "G5", "A5", "G5", None, "E5", None],
    ["B5", "G5", "D5", "G5", "B5", None, "A5", None],
    ["A5", "E5", "C5", "E5", "A5", "G5", "E5", None],
    ["F5", "A5", "C6", "A5", "G5", "E5", "D5", None],
]

BARS = 14
for bar in range(BARS):
    t0 = bar * BAR
    name, notes, root = CHORDS[bar % 4]
    melody = (A_PART if bar < 4 or 8 <= bar < 12 else B_PART)[bar % 4] if bar >= 2 else None
    for beat in range(4):
        t = t0 + beat * BEAT
        if bar >= 1:
            put(t, kick(), 0.55)
        if beat in (1, 3) and bar >= 2:
            put(t, clap(), 0.16)
        # bouncy bass: root on 1, fifth-ish on the and of 2
        if beat == 0:
            put(t, bass(hz(root)), 0.5)
        if beat == 2:
            put(t, bass(hz(root) * 1.5), 0.32)
    for step in range(8):
        t = t0 + step * EIGHTH
        if bar >= 1:
            put(t, hat(), 0.07 if step % 2 == 0 else 0.11)
        if step % 2 == 1:                       # off-beat strum
            for n_i, n in enumerate(notes):
                put(t + n_i * 0.008, pluck(hz(n), 0.35), 0.13)
        if melody and melody[step]:
            put(t, bell(hz(melody[step])), 0.2)

# Closing sparkle on a bright C chord with a little bass.
end = BARS * BAR
for n_i, n in enumerate(["C4", "E4", "G4", "C5"]):
    put(end + n_i * 0.03, pluck(hz(n), 1.4, 0.45), 0.2)
put(end, bass(hz("C2"), 1.2), 0.5)
put(end + 0.12, bell(hz("E6"), 0.9), 0.14)
put(end + 0.24, bell(hz("G6"), 0.9), 0.12)

buf = buf[: int(TOTAL * SR)]
# Gentle fade in and out.
n_in, n_out = int(0.25 * SR), int(1.6 * SR)
buf[:n_in] *= np.linspace(0, 1, n_in)
buf[-n_out:] *= np.linspace(1, 0, n_out)
# Light stereo width: tiny delay on one side.
delay = int(0.012 * SR)
left = buf
right = np.concatenate([np.zeros(delay), buf[:-delay]]) * 0.97
stereo = np.stack([left, right], axis=1)
stereo *= 0.89 / np.max(np.abs(stereo))       # peak about -1 dB, then bring down for platform loudness

with tempfile.TemporaryDirectory() as tmp:
    wav = Path(tmp) / "m.wav"
    wavfile.write(wav, SR, (stereo * 32767).astype(np.int16))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", "loudnorm=I=-16:TP=-1.5:LRA=7", "-ar", "44100", "-c:a", "aac", "-b:a", "192k", str(OUT)], check=True)
print(f"{OUT.relative_to(ROOT)}: {TOTAL:.1f} s, {OUT.stat().st_size / 1e3:.0f} KB")
