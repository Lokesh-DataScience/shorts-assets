"""Synthesized sound effects for Shorts (numpy only, no third-party audio).

Each scene in scene.json can list effects: "sfx": ["whoosh", "crash"] or [["cheer", 1.2]] (name, offset s).
make_track(scenes, timings, total, path) writes a stereo 48 kHz WAV that render.py mixes under the voice.
"""
import wave
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
RNG = np.random.default_rng(7)


def _t(d): return np.arange(int(SR * d)) / SR
def _lp(x, f, o=4): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def _hp(x, f, o=4): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def _bp(x, a, b, o=3): return sosfilt(butter(o, [a, b], "band", fs=SR, output="sos"), x)
def _env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    return np.clip(t / a, 0, 1) * np.exp(-np.maximum(0, t - a) / r)
def _norm(x, peak=0.9): return x / (np.abs(x).max() + 1e-9) * peak


def whoosh(d=0.45):
    t = _t(d); n = len(t)
    noise = RNG.standard_normal(n)
    out = np.zeros(n)
    # sweep a band-pass up across the noise in chunks
    for k in range(12):
        a, b = int(n * k / 12), int(n * (k + 1) / 12)
        f = 400 + 3200 * (k / 11)
        out[a:b] = _bp(noise, f * 0.7, min(f * 1.4, 20000))[a:b]
    shape = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return _norm(out * shape, 0.7)


def sting(d=1.4):
    """News-intro sting: low hit + rising bright chord + shimmer."""
    t = _t(d)
    hit = np.sin(2 * np.pi * 55 * t) * _env(len(t), 0.003, 0.25)
    chord = sum(np.sin(2 * np.pi * f * t) for f in (392, 494, 587, 784)) / 4
    chord *= np.clip((t - 0.05) / 0.08, 0, 1) * np.exp(-np.maximum(0, t - 0.15) / 0.6)
    sh = _hp(RNG.standard_normal(len(t)), 6000) * _env(len(t), 0.02, 0.4) * 0.3
    return _norm(1.0 * hit + 0.6 * chord + sh)


def ding(f=1320, d=0.7):
    t = _t(d)
    x = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t)) * _env(len(t), 0.002, 0.22)
    return _norm(x, 0.6)


def pop(d=0.12):
    t = _t(d)
    x = np.sin(2 * np.pi * (900 - 5000 * t) * t) * _env(len(t), 0.001, 0.03)
    return _norm(x, 0.7)


def crash(d=1.3):
    """Market crash: falling tone + heavy thud."""
    t = _t(d)
    f = 900 * np.exp(-t * 2.2) + 80
    fall = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.clip(1 - t / d, 0, 1) * 0.6
    th_t = t - 0.7
    thud = np.where(th_t > 0, np.sin(2 * np.pi * 50 * th_t) * np.exp(-np.maximum(th_t, 0) / 0.18), 0)
    rumble = _lp(RNG.standard_normal(len(t)), 200) * np.where(th_t > 0, np.exp(-np.maximum(th_t, 0) / 0.25), 0)
    return _norm(fall + 1.2 * thud + 0.8 * _norm(rumble))


def buzzer(d=0.55):
    """Wrong-answer buzzer (two short square-ish blasts)."""
    t = _t(d)
    sq = np.sign(np.sin(2 * np.pi * 140 * t)) * 0.6 + np.sin(2 * np.pi * 280 * t) * 0.4
    gate = ((t < 0.22) | ((t > 0.28) & (t < 0.5))).astype(float)
    return _norm(_lp(sq, 2500) * gate * 0.8, 0.7)


def bubbles(d=0.9):
    out = np.zeros(int(SR * d))
    for k in range(7):
        s = int(SR * RNG.uniform(0, d - 0.1)); n = int(SR * 0.06)
        tt = np.arange(n) / SR
        f0 = RNG.uniform(500, 1100)
        out[s:s + n] += np.sin(2 * np.pi * (f0 + 2500 * tt) * tt) * np.exp(-tt / 0.02)
    return _norm(out, 0.5)


def gavel(d=0.9, hits=(0.0, 0.32)):
    out = np.zeros(int(SR * d))
    for h in hits:
        s = int(SR * h); n = int(SR * 0.25); tt = np.arange(n) / SR
        knock = np.sin(2 * np.pi * 180 * tt) * np.exp(-tt / 0.04) + 0.5 * np.sin(2 * np.pi * 420 * tt) * np.exp(-tt / 0.02)
        click = _hp(RNG.standard_normal(n), 2000) * np.exp(-tt / 0.006) * 0.6
        out[s:s + n] += knock + click
    return _norm(out)


def bat(d=0.25):
    t = _t(d)
    x = _bp(RNG.standard_normal(len(t)), 1500, 6000) * np.exp(-t / 0.01) + np.sin(2 * np.pi * 900 * t) * np.exp(-t / 0.03) * 0.6
    return _norm(x)


def cheer(d=2.0):
    t = _t(d); n = len(t)
    crowd = _bp(RNG.standard_normal(n), 300, 3000)
    mod = 1 + 0.3 * np.sin(2 * np.pi * 3 * t + RNG.uniform(0, 6))
    shape = np.clip(t / 0.3, 0, 1) * np.clip((d - t) / 0.6, 0, 1)
    return _norm(crowd * mod * shape, 0.55)


def digital(d=0.9):
    """Rising data blips (tech / AI)."""
    out = np.zeros(int(SR * d))
    for k in range(9):
        s = int(SR * k * 0.09); n = int(SR * 0.06); tt = np.arange(n) / SR
        f = 600 * (1.12 ** k)
        out[s:s + n] += np.sign(np.sin(2 * np.pi * f * tt)) * np.exp(-tt / 0.03) * 0.5
    return _norm(_lp(out, 6000), 0.55)


def cash(d=0.8):
    """Cash-register 'cha-ching'."""
    t = _t(d)
    bell = (np.sin(2 * np.pi * 2093 * t) + np.sin(2 * np.pi * 2637 * t)) * np.where(t > 0.12, np.exp(-(t - 0.12) / 0.25), 0)
    clunk = _lp(RNG.standard_normal(len(t)), 900) * np.exp(-t / 0.03)
    return _norm(0.8 * clunk + bell)


def tick(d=0.08):
    t = _t(d)
    return _norm(_hp(RNG.standard_normal(len(t)), 3000) * np.exp(-t / 0.004), 0.5)


FX = {"whoosh": whoosh, "sting": sting, "ding": ding, "pop": pop, "crash": crash, "buzzer": buzzer, "bubbles": bubbles,
      "gavel": gavel, "bat": bat, "cheer": cheer, "digital": digital, "cash": cash, "tick": tick}
LEVEL = {"whoosh": 0.55, "sting": 0.8, "ding": 0.6, "pop": 0.6, "crash": 0.85, "buzzer": 0.6, "bubbles": 0.5,
         "gavel": 0.8, "bat": 0.8, "cheer": 0.45, "digital": 0.55, "cash": 0.7, "tick": 0.4}


def make_track(scenes, timings, total, path):
    out = np.zeros(int(SR * (total + 2)))
    for sc, tm in zip(scenes, timings):
        for ev in sc.get("sfx", []):
            name, off = (ev, 0.0) if isinstance(ev, str) else (ev[0], float(ev[1]))
            if name not in FX:
                continue
            clip = FX[name]() * LEVEL[name]
            s = int(SR * max(0.0, tm["start"] + off))
            e = min(len(out), s + len(clip))
            out[s:e] += clip[:e - s]
    out = np.clip(out, -0.98, 0.98)
    st = np.stack([out, np.roll(out, 120)], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    return path
