"""Synthesize all original music loops and SFX for the storybook theme.

Music: Thai pentatonic phrases voiced with synthesized khlui (bamboo flute),
ranad (wooden bars), phin (plucked string), klong (drum) and ching (small cymbals).
Everything here is generated from scratch so the project ships no borrowed audio.

Music loops are seamless: the reverb tail is wrapped back onto the loop start.

Usage:  python scripts/build_audio.py
Requires: numpy, scipy, and ffmpeg on PATH (for OGG encoding).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
ROOT = Path(__file__).resolve().parent.parent
MUSIC_DIR = ROOT / "Assets" / "Generated" / "Sound" / "Music"
FX_DIR = ROOT / "Assets" / "Generated" / "Sound" / "FX"

# Pentatonic degrees in semitones from the root.
MAJOR_PENT = [0, 2, 4, 7, 9]
MINOR_PENT = [0, 3, 5, 7, 10]


# --------------------------------------------------------------------------- #
# Core helpers
# --------------------------------------------------------------------------- #


def n_samples(seconds: float) -> int:
    return max(1, int(round(seconds * SR)))


def time_axis(seconds: float) -> np.ndarray:
    return np.arange(n_samples(seconds), dtype=np.float64) / SR


def midi_to_hz(midi: float) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def degree_to_midi(root: int, scale: list[int], degree: int) -> float:
    """Degree may run past the scale length; it wraps into higher octaves."""
    octave, index = divmod(degree, len(scale))
    return root + 12 * octave + scale[index]


def adsr(dur: float, a: float, d: float, s: float, r: float) -> np.ndarray:
    """Attack/decay/sustain-level/release envelope covering exactly dur seconds."""
    total = n_samples(dur)
    na, nd, nr = n_samples(a), n_samples(d), n_samples(r)
    ns = max(0, total - na - nd - nr)
    if na + nd + nr > total:
        scale = total / float(na + nd + nr)
        na, nd, nr = int(na * scale), int(nd * scale), int(nr * scale)
        ns = max(0, total - na - nd - nr)
    env = np.concatenate(
        [
            np.linspace(0.0, 1.0, na, endpoint=False) ** 0.7,
            np.linspace(1.0, s, nd, endpoint=False),
            np.full(ns, s),
            np.linspace(s, 0.0, nr) ** 1.4,
        ]
    )
    if env.size < total:
        env = np.pad(env, (0, total - env.size))
    return env[:total]


def expo_decay(dur: float, tau: float) -> np.ndarray:
    return np.exp(-time_axis(dur) / max(1e-4, tau))


def noise(dur: float, seed: int | None = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(-1.0, 1.0, n_samples(dur))


def lowpass(x: np.ndarray, cutoff: float, order: int = 4) -> np.ndarray:
    cutoff = float(np.clip(cutoff, 20.0, SR / 2 - 100))
    sos = signal.butter(order, cutoff, btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def highpass(x: np.ndarray, cutoff: float, order: int = 4) -> np.ndarray:
    cutoff = float(np.clip(cutoff, 20.0, SR / 2 - 100))
    sos = signal.butter(order, cutoff, btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def bandpass(x: np.ndarray, lo: float, hi: float, order: int = 2) -> np.ndarray:
    lo = float(np.clip(lo, 20.0, SR / 2 - 200))
    hi = float(np.clip(hi, lo + 50.0, SR / 2 - 100))
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def sweep_bandpass(x: np.ndarray, f_start: float, f_end: float, bw: float = 0.6) -> np.ndarray:
    """Cheap moving bandpass: blend a few static bands along the sweep."""
    steps = 8
    out = np.zeros_like(x)
    win = np.array_split(np.arange(x.size), steps)
    for i, idx in enumerate(win):
        frac = i / max(1, steps - 1)
        centre = f_start * (f_end / f_start) ** frac
        seg = np.zeros_like(x)
        seg[idx] = x[idx]
        out += bandpass(seg, centre * (1 - bw / 2), centre * (1 + bw / 2))
    return out


def reverb(x: np.ndarray, tail: float = 1.2, mix: float = 0.25, damp: float = 3500.0) -> np.ndarray:
    """Convolution reverb with an exponentially decaying noise impulse response."""
    ir = noise(tail, seed=777) * expo_decay(tail, tail / 3.5)
    ir = lowpass(ir, damp)
    ir[: n_samples(0.004)] = 0.0
    ir /= np.max(np.abs(ir)) + 1e-9
    if x.ndim == 1:
        wet = signal.fftconvolve(x, ir)[: x.size]
    else:
        wet = np.stack([signal.fftconvolve(x[:, c], ir)[: x.shape[0]] for c in range(x.shape[1])], axis=1)
    return (1.0 - mix) * x + mix * wet


def normalize(x: np.ndarray, peak: float = 0.9) -> np.ndarray:
    m = float(np.max(np.abs(x)))
    if m < 1e-9:
        return x
    return x * (peak / m)


def write_wav(path: Path, x: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.clip(x, -1.0, 1.0)
    wavfile.write(str(path), SR, (data * 32767.0).astype(np.int16))
    print(f"  {path.name}  {path.stat().st_size / 1024:.0f} KB")


def encode_ogg(wav_path: Path, ogg_path: Path, quality: int = 4) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        print("  ffmpeg not found; keeping WAV")
        return
    ogg_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-i", str(wav_path), "-c:a", "libvorbis", "-q:a", str(quality), str(ogg_path)],
        check=True,
    )
    wav_path.unlink(missing_ok=True)
    print(f"  {ogg_path.name}  {ogg_path.stat().st_size / 1024:.0f} KB")


# --------------------------------------------------------------------------- #
# Instruments
# --------------------------------------------------------------------------- #


def khlui(freq: float, dur: float, gain: float = 0.5) -> np.ndarray:
    """Bamboo flute: soft sine core, weak octave, breath noise, gentle vibrato."""
    t = time_axis(dur)
    vib = 1.0 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.clip(t / 0.25, 0, 1)
    phase = 2 * np.pi * freq * np.cumsum(vib) / SR
    tone = np.sin(phase) + 0.22 * np.sin(2 * phase) + 0.06 * np.sin(3 * phase)
    breath = highpass(noise(dur, seed=int(freq) % 9991), 2200.0) * 0.05
    env = adsr(dur, 0.055, 0.09, 0.82, min(0.22, dur * 0.4))
    return gain * (tone * 0.55 + breath) * env


def ranad(freq: float, dur: float, gain: float = 0.5) -> np.ndarray:
    """Struck wooden bar: inharmonic partials with a quick woody transient."""
    t = time_axis(dur)
    partials = [(1.0, 1.0, 0.34), (2.76, 0.34, 0.16), (5.40, 0.13, 0.09), (8.93, 0.05, 0.05)]
    out = np.zeros_like(t)
    for ratio, amp, tau in partials:
        out += amp * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t / tau)
    click = lowpass(noise(dur, seed=int(freq) % 7717), 5200.0) * expo_decay(dur, 0.006) * 0.5
    return gain * (out / 1.5 + click) * adsr(dur, 0.002, 0.02, 0.55, min(0.12, dur * 0.5))


def pluck(freq: float, dur: float, gain: float = 0.45, damp: float = 0.5) -> np.ndarray:
    """Karplus-Strong string for phin / krajappi colour."""
    total = n_samples(dur)
    delay = max(2, int(SR / max(20.0, freq)))
    rng = np.random.default_rng(int(freq) % 5333)
    buf = rng.uniform(-1.0, 1.0, delay)
    buf = lowpass(buf, 4200.0)
    out = np.zeros(total)
    idx = 0
    decay = 0.996 - 0.004 * damp
    for i in range(total):
        cur = buf[idx]
        nxt = buf[(idx + 1) % delay]
        out[i] = cur
        buf[idx] = decay * 0.5 * (cur + nxt)
        idx = (idx + 1) % delay
    return gain * out * adsr(dur, 0.001, 0.03, 0.7, min(0.15, dur * 0.4))


def klong(dur: float = 0.4, base: float = 96.0, gain: float = 0.7) -> np.ndarray:
    """Hand drum: pitched thump plus a filtered skin slap."""
    t = time_axis(dur)
    pitch = base * (1.0 + 0.8 * np.exp(-t / 0.02))
    body = np.sin(2 * np.pi * np.cumsum(pitch) / SR) * expo_decay(dur, 0.10)
    skin = lowpass(noise(dur, seed=4242), 1800.0) * expo_decay(dur, 0.035)
    return gain * (body * 0.85 + skin * 0.4)


def ching(dur: float = 0.5, gain: float = 0.25, closed: bool = True) -> np.ndarray:
    """Small hand cymbals: 'ching' is damped, 'chap' rings on."""
    tau = 0.05 if closed else 0.30
    metal = np.zeros(n_samples(dur))
    t = time_axis(dur)
    for f in (2870.0, 4310.0, 5720.0, 7480.0, 9260.0):
        metal += np.sin(2 * np.pi * f * t) * np.exp(-t / (tau * (2870.0 / f)))
    hiss = highpass(noise(dur, seed=91), 4000.0) * expo_decay(dur, tau * 0.8)
    return gain * (metal / 5.0 + hiss * 0.6)


def pad(freq: float, dur: float, gain: float = 0.18) -> np.ndarray:
    """Slow detuned drone for night scenes."""
    t = time_axis(dur)
    out = np.zeros_like(t)
    for det in (-0.06, 0.0, 0.07):
        out += np.sin(2 * np.pi * (freq + det) * t + np.sin(2 * np.pi * 0.13 * t))
    out += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
    fade = min(1.2, dur * 0.3)
    return gain * lowpass(out / 3.3, 1600.0) * adsr(dur, fade, 0.2, 0.85, fade)


# --------------------------------------------------------------------------- #
# Music arrangement
# --------------------------------------------------------------------------- #


class Track:
    """Stereo buffer with wrap-around mixing so loops stay seamless."""

    def __init__(self, seconds: float):
        self.length = n_samples(seconds)
        self.buf = np.zeros((self.length, 2))

    def add(self, at: float, mono: np.ndarray, pan: float = 0.0, gain: float = 1.0) -> None:
        start = int(round(at * SR))
        left = gain * mono * np.sqrt(0.5 * (1.0 - pan))
        right = gain * mono * np.sqrt(0.5 * (1.0 + pan))
        for chan, sig in ((0, left), (1, right)):
            i = start % self.length
            remaining = sig
            while remaining.size:
                room = self.length - i
                take = min(room, remaining.size)
                self.buf[i : i + take, chan] += remaining[:take]
                remaining = remaining[take:]
                i = 0

    def finish(self, rev_tail: float, rev_mix: float, rms: float = 0.14) -> np.ndarray:
        """Reverb, then match a target RMS and only limit the few peaks that stick out.

        Gain staging matters here: saturating before normalising turns a dense mix
        into a square wave, so the level is set first and the limiter barely engages.
        """
        out = reverb(self.buf, tail=rev_tail, mix=rev_mix)
        cur = float(np.sqrt(np.mean(out**2)))
        if cur > 1e-9:
            out = out * (rms / cur)
        ceiling = 0.92
        loud = np.max(np.abs(out))
        if loud > ceiling:
            out = np.tanh(out / ceiling) * ceiling
        return out


def build_menu_theme() -> np.ndarray:
    """Calm khlui over a rocking pluck figure. No drums: this is the book cover."""
    bpm, bars = 66.0, 16
    beat = 60.0 / bpm
    track = Track(bars * 4 * beat)
    root = 60  # C4

    arp = [0, 2, 4, 2, 3, 2, 1, 2]
    for bar in range(bars):
        for step, deg in enumerate(arp):
            at = (bar * 4 + step * 0.5) * beat
            hz = midi_to_hz(degree_to_midi(root - 12, MAJOR_PENT, deg))
            track.add(at, pluck(hz, beat * 0.9, gain=0.30), pan=-0.25)
        bass = midi_to_hz(degree_to_midi(root - 24, MAJOR_PENT, [0, 0, 4, 2][bar % 4]))
        track.add(bar * 4 * beat, pluck(bass, beat * 2.4, gain=0.34, damp=0.9), pan=0.05)

    melody = [
        (0.0, 4, 1.5), (1.5, 3, 0.5), (2.0, 2, 2.0),
        (4.0, 3, 1.0), (5.0, 4, 1.0), (6.0, 5, 2.0),
        (8.0, 4, 1.5), (9.5, 2, 0.5), (10.0, 1, 2.0),
        (12.0, 2, 1.0), (13.0, 1, 1.0), (14.0, 0, 2.0),
    ]
    for cycle in range(2):
        offset = cycle * 16 * beat
        shift = 0 if cycle == 0 else 2
        for at, deg, length in melody:
            hz = midi_to_hz(degree_to_midi(root, MAJOR_PENT, deg + (shift if at > 7 else 0)))
            track.add(offset + at * beat, khlui(hz, length * beat * 0.95, gain=0.42), pan=0.22)

    for bar in range(bars):
        track.add((bar * 4 + 2) * beat, ching(0.4, gain=0.10), pan=0.35)
    return track.finish(rev_tail=1.9, rev_mix=0.32)


def build_day_walk() -> np.ndarray:
    """Levels 1-2: bright ranad walking tune with light percussion."""
    bpm, bars = 102.0, 16
    beat = 60.0 / bpm
    track = Track(bars * 4 * beat)
    root = 64  # E4

    phrase = [
        (0.0, 0, 0.5), (0.5, 2, 0.5), (1.0, 4, 0.5), (1.5, 2, 0.5),
        (2.0, 3, 1.0), (3.0, 2, 0.5), (3.5, 1, 0.5),
        (4.0, 2, 0.5), (4.5, 4, 0.5), (5.0, 5, 1.0),
        (6.0, 4, 0.5), (6.5, 3, 0.5), (7.0, 2, 1.0),
    ]
    for bar_pair in range(bars // 2):
        offset = bar_pair * 8 * beat
        lift = [0, 0, 1, 0, 2, 0, 1, 3][bar_pair % 8]
        for at, deg, length in phrase:
            hz = midi_to_hz(degree_to_midi(root, MAJOR_PENT, deg + lift))
            track.add(offset + at * beat, ranad(hz, length * beat * 1.4, gain=0.40), pan=-0.18)

    for bar in range(bars):
        base = bar * 4 * beat
        low = [0, 4, 2, 3][bar % 4]
        track.add(base, pluck(midi_to_hz(degree_to_midi(root - 24, MAJOR_PENT, low)), beat * 1.8, gain=0.40, damp=0.8), pan=0.1)
        track.add(base + 2 * beat, pluck(midi_to_hz(degree_to_midi(root - 17, MAJOR_PENT, low)), beat * 1.4, gain=0.26, damp=0.8), pan=0.28)
        track.add(base, klong(0.34, base=92.0, gain=0.42), pan=0.0)
        track.add(base + 2.5 * beat, klong(0.26, base=118.0, gain=0.28), pan=-0.08)
        for off in (1, 3):
            track.add(base + off * beat, ching(0.22, gain=0.11), pan=0.4)
    return track.finish(rev_tail=1.1, rev_mix=0.20)


def build_noon_trail() -> np.ndarray:
    """Levels 3-4: dry, sparse, hotter. Minor pentatonic with a driving drum."""
    bpm, bars = 90.0, 16
    beat = 60.0 / bpm
    track = Track(bars * 4 * beat)
    root = 57  # A3

    calls = [
        (0.0, 4, 1.0), (1.0, 3, 0.5), (1.5, 4, 1.5), (3.5, 2, 0.5),
        (4.0, 0, 1.5), (6.0, 2, 1.0), (7.0, 1, 1.0),
    ]
    for block in range(bars // 4):
        offset = block * 16 * beat
        for rep in range(2):
            lift = 0 if rep == 0 else [0, 2, 1, 2][block % 4]
            for at, deg, length in calls:
                hz = midi_to_hz(degree_to_midi(root + 12, MINOR_PENT, deg + lift))
                voice = ranad if rep == 0 else khlui
                gain = 0.36 if rep == 0 else 0.34
                track.add(offset + (rep * 8 + at) * beat, voice(hz, length * beat, gain=gain), pan=0.2 * (1 if rep else -1))

    for bar in range(bars):
        base = bar * 4 * beat
        track.add(base, pad(midi_to_hz(root - 12), 4 * beat, gain=0.10), pan=0.0)
        track.add(base, klong(0.3, base=84.0, gain=0.5), pan=-0.05)
        track.add(base + 1.5 * beat, klong(0.22, base=124.0, gain=0.3), pan=0.12)
        track.add(base + 2 * beat, klong(0.28, base=96.0, gain=0.36), pan=0.0)
        if bar % 2 == 1:
            track.add(base + 3.5 * beat, ching(0.3, gain=0.13, closed=False), pan=0.42)
    return track.finish(rev_tail=0.9, rev_mix=0.16)


def build_night_canal() -> np.ndarray:
    """Levels 5-6: low drone, distant flute, water-drop plucks, wide reverb."""
    bpm, bars = 70.0, 16
    beat = 60.0 / bpm
    track = Track(bars * 4 * beat)
    root = 55  # G3

    for bar in range(0, bars, 2):
        deg = [0, 3, 2, 4, 0, 1, 3, 2][(bar // 2) % 8]
        track.add(bar * 4 * beat, pad(midi_to_hz(degree_to_midi(root - 12, MINOR_PENT, deg)), 8 * beat, gain=0.16), pan=0.0)

    long_line = [
        (0.0, 4, 3.0), (3.5, 3, 1.5), (6.0, 2, 2.0),
        (9.0, 1, 2.0), (12.0, 2, 1.5), (13.5, 0, 2.5),
    ]
    for cycle in range(2):
        offset = cycle * 16 * beat
        for at, deg, length in long_line:
            hz = midi_to_hz(degree_to_midi(root + 12, MINOR_PENT, deg + (0 if cycle == 0 else 1)))
            track.add(offset + at * beat, khlui(hz, length * beat, gain=0.34), pan=-0.2 + 0.4 * cycle)

    rng = np.random.default_rng(20260903)
    for bar in range(bars):
        for _ in range(2):
            at = (bar * 4 + rng.uniform(0.0, 3.5)) * beat
            deg = int(rng.integers(2, 8))
            hz = midi_to_hz(degree_to_midi(root, MINOR_PENT, deg))
            track.add(at, pluck(hz, beat * 1.6, gain=0.16, damp=0.3), pan=float(rng.uniform(-0.5, 0.5)))
        if bar % 4 == 0:
            track.add(bar * 4 * beat, ching(0.7, gain=0.10, closed=False), pan=0.3)
    return track.finish(rev_tail=2.6, rev_mix=0.40)


MUSIC = {
    "menu_theme": build_menu_theme,
    "day_walk": build_day_walk,
    "noon_trail": build_noon_trail,
    "night_canal": build_night_canal,
}


# --------------------------------------------------------------------------- #
# Sound effects
# --------------------------------------------------------------------------- #


def sfx_page_turn() -> np.ndarray:
    dur = 0.42
    body = sweep_bandpass(noise(dur, seed=11), 700.0, 3600.0, bw=0.9)
    crinkle = noise(dur, seed=12) * (np.abs(noise(dur, seed=13)) ** 3)
    crinkle = highpass(crinkle, 2500.0) * 0.5
    env = np.sin(np.pi * np.linspace(0, 1, n_samples(dur))) ** 1.3
    return normalize((body + crinkle) * env, 0.55)


def sfx_ui_click() -> np.ndarray:
    dur = 0.09
    t = time_axis(dur)
    woody = np.sin(2 * np.pi * 760 * t) * np.exp(-t / 0.014)
    tap = lowpass(noise(dur, seed=21), 4000.0) * np.exp(-t / 0.008)
    return normalize(woody * 0.7 + tap * 0.6, 0.5)


def sfx_ui_back() -> np.ndarray:
    dur = 0.12
    t = time_axis(dur)
    woody = np.sin(2 * np.pi * 420 * t) * np.exp(-t / 0.02)
    tap = lowpass(noise(dur, seed=22), 2600.0) * np.exp(-t / 0.01)
    return normalize(woody * 0.7 + tap * 0.5, 0.5)


def sfx_jump() -> np.ndarray:
    dur = 0.22
    t = time_axis(dur)
    f = 300.0 * (2.2 ** (t / dur))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)
    air = highpass(noise(dur, seed=31), 1800.0) * np.exp(-t / 0.05) * 0.25
    return normalize(tone * 0.8 + air, 0.62)


def sfx_land() -> np.ndarray:
    dur = 0.26
    t = time_axis(dur)
    thud = np.sin(2 * np.pi * 130 * np.exp(-t * 6) * t * 6) * np.exp(-t / 0.055)
    dust = lowpass(noise(dur, seed=32), 1500.0) * np.exp(-t / 0.045) * 0.45
    return normalize(thud * 0.7 + dust, 0.55)


def sfx_throw_stone() -> np.ndarray:
    dur = 0.24
    whoosh = sweep_bandpass(noise(dur, seed=41), 2600.0, 700.0, bw=0.7)
    env = np.exp(-time_axis(dur) / 0.075)
    return normalize(whoosh * env, 0.5)


def sfx_stone_hit() -> np.ndarray:
    dur = 0.18
    t = time_axis(dur)
    clack = (np.sin(2 * np.pi * 980 * t) + 0.5 * np.sin(2 * np.pi * 1640 * t)) * np.exp(-t / 0.02)
    grit = bandpass(noise(dur, seed=42), 1200.0, 6000.0) * np.exp(-t / 0.015)
    return normalize(clack * 0.6 + grit * 0.7, 0.6)


def sfx_enemy_hit() -> np.ndarray:
    dur = 0.16
    t = time_axis(dur)
    slap = lowpass(noise(dur, seed=51), 2400.0) * np.exp(-t / 0.022)
    tone = np.sin(2 * np.pi * 240 * t) * np.exp(-t / 0.03)
    return normalize(slap * 0.8 + tone * 0.5, 0.58)


def sfx_enemy_death() -> np.ndarray:
    dur = 0.5
    t = time_axis(dur)
    splat = lowpass(noise(dur, seed=52), 3000.0) * np.exp(-t / 0.09)
    f = 340.0 * np.exp(-t * 5.0) + 70.0
    fall = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)
    return normalize(splat * 0.6 + fall * 0.7, 0.6)


def sfx_hurt() -> np.ndarray:
    dur = 0.3
    t = time_axis(dur)
    f = 430.0 * np.exp(-t * 4.5) + 150.0
    cry = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.1)
    crumple = highpass(noise(dur, seed=61), 1600.0) * np.exp(-t / 0.05) * 0.35
    return normalize(cry * 0.75 + crumple, 0.6)


def sfx_death() -> np.ndarray:
    dur = 1.1
    t = time_axis(dur)
    f = 380.0 * np.exp(-t * 2.2) + 60.0
    fall = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
    rumble = lowpass(noise(dur, seed=62), 300.0) * np.exp(-t / 0.3) * 0.5
    smear = highpass(noise(dur, seed=63), 900.0) * np.exp(-t / 0.12) * 0.2
    return normalize(reverb(fall * 0.7 + rumble + smear, tail=1.0, mix=0.3), 0.65)


def sfx_respawn() -> np.ndarray:
    dur = 0.75
    out = np.zeros(n_samples(dur))
    for i, deg in enumerate([0, 2, 4]):
        seg = pluck(midi_to_hz(degree_to_midi(60, MAJOR_PENT, deg)), 0.45, gain=0.5, damp=0.4)
        start = n_samples(i * 0.11)
        out[start : start + seg.size] += seg[: max(0, out.size - start)]
    return normalize(reverb(out, tail=0.8, mix=0.25), 0.55)


def _chime(degrees: list[int], root: int, step: float, note: float, voice=ranad, gain: float = 0.5) -> np.ndarray:
    dur = step * (len(degrees) - 1) + note + 0.2
    out = np.zeros(n_samples(dur))
    for i, deg in enumerate(degrees):
        seg = voice(midi_to_hz(degree_to_midi(root, MAJOR_PENT, deg)), note, gain=gain)
        start = n_samples(i * step)
        room = out.size - start
        out[start : start + min(seg.size, room)] += seg[: min(seg.size, room)]
    return out


def sfx_pickup_kratib() -> np.ndarray:
    return normalize(reverb(_chime([2, 4], 72, 0.075, 0.3), tail=0.6, mix=0.2), 0.5)


def sfx_pickup_heart() -> np.ndarray:
    return normalize(reverb(_chime([0, 2, 4, 5], 72, 0.07, 0.36), tail=0.9, mix=0.28), 0.55)


def sfx_pickup_stone() -> np.ndarray:
    dur = 0.24
    t = time_axis(dur)
    knock = lowpass(noise(dur, seed=71), 2200.0) * np.exp(-t / 0.018)
    tone = ranad(midi_to_hz(degree_to_midi(60, MAJOR_PENT, 1)), dur, gain=0.5)
    return normalize(knock * 0.5 + tone, 0.52)


def sfx_checkpoint_bell() -> np.ndarray:
    dur = 2.1
    t = time_axis(dur)
    out = np.zeros_like(t)
    for ratio, amp, tau in [(1.0, 1.0, 1.5), (2.0, 0.6, 0.9), (2.97, 0.35, 0.6), (4.1, 0.2, 0.4), (5.43, 0.12, 0.3)]:
        out += amp * np.sin(2 * np.pi * 528.0 * ratio * t) * np.exp(-t / tau)
    strike = highpass(noise(dur, seed=81), 3000.0) * expo_decay(dur, 0.01) * 0.4
    return normalize(reverb(out / 2.3 + strike, tail=2.2, mix=0.35), 0.6)


def sfx_gate_open() -> np.ndarray:
    dur = 0.9
    t = time_axis(dur)
    creak = signal.sawtooth(2 * np.pi * np.cumsum(120.0 + 55.0 * np.sin(2 * np.pi * 3.1 * t)) / SR)
    creak = bandpass(creak, 260.0, 1500.0) * np.sin(np.pi * np.linspace(0, 1, t.size)) ** 0.8
    grind = bandpass(noise(dur, seed=91), 400.0, 2600.0) * np.exp(-t / 0.4) * 0.3
    thud = np.sin(2 * np.pi * 90 * t) * np.exp(-((t - 0.78) ** 2) / 0.002) * 0.6
    return normalize(creak * 0.45 + grind + thud, 0.6)


def sfx_patience_low() -> np.ndarray:
    dur = 0.85
    out = np.zeros(n_samples(dur))
    for i in range(2):
        t = time_axis(0.42)
        strike = np.zeros_like(t)
        for ratio, amp, tau in [(1.0, 1.0, 0.3), (2.4, 0.4, 0.18), (3.7, 0.2, 0.1)]:
            strike += amp * np.sin(2 * np.pi * 196.0 * ratio * t) * np.exp(-t / tau)
        start = n_samples(i * 0.33)
        room = out.size - start
        out[start : start + min(strike.size, room)] += strike[: min(strike.size, room)] / 1.6
    return normalize(reverb(out, tail=1.0, mix=0.25), 0.5)


def sfx_level_complete() -> np.ndarray:
    dur = 1.7
    out = np.zeros(n_samples(dur))
    for i, deg in enumerate([0, 2, 4, 5]):
        seg = ranad(midi_to_hz(degree_to_midi(67, MAJOR_PENT, deg)), 0.6, gain=0.5)
        flute = khlui(midi_to_hz(degree_to_midi(67, MAJOR_PENT, deg)), 0.55, gain=0.22)
        start = n_samples(i * 0.16)
        for seg_x in (seg, flute):
            room = out.size - start
            out[start : start + min(seg_x.size, room)] += seg_x[: min(seg_x.size, room)]
    out[: n_samples(0.34)] += ching(0.34, gain=0.14)
    return normalize(reverb(out, tail=1.4, mix=0.3), 0.7)


def sfx_win() -> np.ndarray:
    dur = 3.0
    out = np.zeros(n_samples(dur))
    melody = [(0.0, 0, 0.35), (0.3, 2, 0.35), (0.6, 4, 0.5), (1.05, 5, 0.5), (1.5, 4, 0.4), (1.85, 7, 1.1)]
    for at, deg, length in melody:
        start = n_samples(at)
        for seg in (
            ranad(midi_to_hz(degree_to_midi(67, MAJOR_PENT, deg)), length, gain=0.45),
            khlui(midi_to_hz(degree_to_midi(67, MAJOR_PENT, deg)), length * 0.95, gain=0.26),
        ):
            room = out.size - start
            out[start : start + min(seg.size, room)] += seg[: min(seg.size, room)]
    for at in (0.0, 0.6, 1.5, 1.85):
        start = n_samples(at)
        drum = klong(0.3, base=92.0, gain=0.34)
        room = out.size - start
        out[start : start + min(drum.size, room)] += drum[: min(drum.size, room)]
    for at in (0.3, 1.05, 2.3):
        start = n_samples(at)
        c = ching(0.3, gain=0.13)
        room = out.size - start
        out[start : start + min(c.size, room)] += c[: min(c.size, room)]
    return normalize(reverb(out, tail=1.8, mix=0.32), 0.75)


def sfx_game_over() -> np.ndarray:
    dur = 3.0
    out = np.zeros(n_samples(dur))
    melody = [(0.0, 4, 0.8), (0.75, 3, 0.7), (1.4, 1, 0.9), (2.2, 0, 1.4)]
    for at, deg, length in melody:
        hz = midi_to_hz(degree_to_midi(57, MINOR_PENT, deg))
        start = n_samples(at)
        for seg in (khlui(hz, length, gain=0.34), pluck(hz / 2, length, gain=0.2, damp=0.9)):
            room = out.size - start
            out[start : start + min(seg.size, room)] += seg[: min(seg.size, room)]
    for at in (0.0, 1.4):
        start = n_samples(at)
        drum = klong(0.5, base=70.0, gain=0.4)
        room = out.size - start
        out[start : start + min(drum.size, room)] += drum[: min(drum.size, room)]
    return normalize(reverb(out, tail=2.4, mix=0.38), 0.7)


SFX = {
    "page_turn": sfx_page_turn,
    "ui_click": sfx_ui_click,
    "ui_back": sfx_ui_back,
    "jump": sfx_jump,
    "land": sfx_land,
    "throw_stone": sfx_throw_stone,
    "stone_hit": sfx_stone_hit,
    "enemy_hit": sfx_enemy_hit,
    "enemy_death": sfx_enemy_death,
    "hurt": sfx_hurt,
    "death": sfx_death,
    "respawn": sfx_respawn,
    "pickup_kratib": sfx_pickup_kratib,
    "pickup_heart": sfx_pickup_heart,
    "pickup_stone": sfx_pickup_stone,
    "checkpoint_bell": sfx_checkpoint_bell,
    "gate_open": sfx_gate_open,
    "patience_low": sfx_patience_low,
    "level_complete": sfx_level_complete,
    "win": sfx_win,
    "game_over": sfx_game_over,
}


def main() -> None:
    only = sys.argv[1] if len(sys.argv) > 1 else "all"

    if only in ("all", "sfx"):
        print("Sound effects:")
        FX_DIR.mkdir(parents=True, exist_ok=True)
        for name, fn in SFX.items():
            write_wav(FX_DIR / f"{name}.wav", fn())

    if only in ("all", "music"):
        print("Music loops:")
        MUSIC_DIR.mkdir(parents=True, exist_ok=True)
        for name, fn in MUSIC.items():
            tmp = MUSIC_DIR / f"{name}.wav"
            write_wav(tmp, fn())
            encode_ogg(tmp, MUSIC_DIR / f"{name}.ogg")

    print("done")


if __name__ == "__main__":
    main()
