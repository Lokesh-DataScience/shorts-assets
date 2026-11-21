"""Rocket-launch intro for Shorts: a tricolour rocket lifts off behind the hook text, plus a synthesized launch sound.

Used by render.py when scene.json has "intro": "rocket". Everything is drawn in code and the sound is
synthesized with numpy, so there is no third-party art or audio.
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
CX = W // 2
GROUND = 1830          # rocket base y while on the pad
IGNITE = 0.40          # seconds of ignition before lift-off
ACCEL = 950            # px/s^2


def base_y(t):
    if t < IGNITE:
        return GROUND
    d = t - IGNITE
    return GROUND - ACCEL * d * d


def _sprite():
    """Rocket drawn at 2x and scaled down for clean edges. Base (nozzle exit) is the bottom centre."""
    s = 2
    w, h = 200 * s, 520 * s
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = w // 2
    bw = 52 * s                          # body half-width
    top, bot = 150 * s, 470 * s          # body
    # fins
    for sgn in (-1, 1):
        d.polygon([(cx + sgn * bw, bot - 120 * s), (cx + sgn * (bw + 48 * s), bot + 10 * s),
                   (cx + sgn * (bw + 48 * s), bot + 30 * s), (cx + sgn * bw, bot)], fill=(214, 40, 50))
    # body
    d.rounded_rectangle([cx - bw, top, cx + bw, bot], 10 * s, fill=(244, 244, 250))
    # shading strip
    d.rectangle([cx + bw * 0.45, top + 8, cx + bw - 4, bot - 8], fill=(214, 216, 230))
    # tricolour bands
    d.rectangle([cx - bw, bot - 110 * s, cx + bw, bot - 82 * s], fill=(255, 153, 51))
    d.rectangle([cx - bw, bot - 82 * s, cx + bw, bot - 54 * s], fill=(255, 255, 255))
    d.rectangle([cx - bw, bot - 54 * s, cx + bw, bot - 26 * s], fill=(19, 136, 8))
    d.ellipse([cx - 9 * s, bot - 77 * s, cx + 9 * s, bot - 59 * s], outline=(0, 0, 128), width=3 * s)
    # nose cone (ogive)
    pts = []
    for k in range(41):
        a = k / 40
        pts.append((cx - bw * math.sin(a * math.pi / 2), top - (1 - a) * 0 - (1 - math.sin(a * math.pi / 2)) * 0))
    nose = [(cx, 20 * s)]
    for k in range(1, 41):
        a = k / 40
        nose.append((cx + bw * math.sqrt(a), 20 * s + a * (top - 20 * s)))
    for k in range(40, 0, -1):
        a = k / 40
        nose.append((cx - bw * math.sqrt(a), 20 * s + a * (top - 20 * s)))
    d.polygon(nose, fill=(230, 45, 55))
    # window
    d.ellipse([cx - 28 * s, top + 60 * s, cx + 28 * s, top + 116 * s], fill=(60, 70, 90))
    d.ellipse([cx - 21 * s, top + 67 * s, cx + 21 * s, top + 109 * s], fill=(80, 190, 255))
    d.ellipse([cx - 12 * s, top + 74 * s, cx - 2 * s, top + 86 * s], fill=(225, 245, 255))
    # nozzle
    d.polygon([(cx - 30 * s, bot), (cx + 30 * s, bot), (cx + 40 * s, h - 20 * s), (cx - 40 * s, h - 20 * s)], fill=(70, 72, 88))
    im = im.resize((w // s, h // s), Image.LANCZOS)
    return im


SPRITE = _sprite()
SW, SH = SPRITE.size
NOZZLE = SH - 10       # sprite y of the nozzle exit

random.seed(11)
# smoke puffs: (emit time, x jitter, drift vx, max radius, life)
PUFFS = []
for i in range(260):
    te = random.uniform(0, 2.4)
    PUFFS.append((te, random.uniform(-30, 30), random.uniform(-160, 160), random.uniform(50, 120), random.uniform(1.0, 1.8)))
GROUND_PUFFS = [(random.uniform(0, 1.3), random.choice((-1, 1)) * random.uniform(40, 520), random.uniform(80, 190),
                 random.uniform(1.6, 2.8)) for _ in range(70)]


def draw(im, t):
    """Draw the launch onto im (RGB). Returns the image. Call before the hook text so text stays on top."""
    if t > 3.4:
        return im
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    shake = 6 * max(0.0, 1 - t / 1.2)
    sx = random.uniform(-shake, shake) if shake else 0
    # ground glow at ignition
    if t < 1.6:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        a = int(190 * min(1, t / 0.15) * max(0, 1 - t / 1.6))
        gd.ellipse([CX - 480, GROUND - 140, CX + 480, GROUND + 200], fill=(255, 150, 40, a))
        layer = Image.alpha_composite(layer, g.filter(ImageFilter.GaussianBlur(70)))
        d = ImageDraw.Draw(layer, "RGBA")
    # ground smoke cloud spreading sideways
    for (te, dx, r, life) in GROUND_PUFFS:
        age = t - te
        if 0 <= age < life:
            k = age / life
            x = CX + dx * (0.3 + 1.2 * (1 - (1 - k) ** 2))
            y = GROUND + 40 - 60 * k
            rr = r * (0.4 + 0.9 * k)
            a = int(185 * (1 - k) ** 1.3)
            c = 170 + int(50 * (1 - k))
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(c, c, c + 8, a))
    # trail smoke: emitted from the nozzle position at emission time
    for (te, dx, vx, r, life) in PUFFS:
        if te < IGNITE or te > t:
            continue
        age = t - te
        if age >= life:
            continue
        k = age / life
        y0 = base_y(te) + 10
        if y0 < -100 or y0 > H + 100:
            continue
        x = CX + dx + vx * age
        rr = r * (0.3 + 0.9 * k)
        a = int(105 * (1 - k) ** 1.5)       # thin, so hook text stays readable over it
        c = 200 + int(40 * (1 - k))
        d.ellipse([x - rr, y0 - rr + 40 * age, x + rr, y0 + rr + 40 * age], fill=(c, c, c, a))
    layer = layer.filter(ImageFilter.GaussianBlur(9))    # soft, cloud-like smoke instead of hard circles
    by = base_y(t)
    if by > -SH - 300:
        # flame
        fl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fd = ImageDraw.Draw(fl)
        grow = min(1, t / IGNITE) if t < IGNITE else 1.0
        L = (150 + 110 * min(1, max(0, t - IGNITE) / 0.6) + random.uniform(-25, 25)) * grow
        ny = by + 0
        for (wd, ln, col) in ((44, 1.0, (255, 90, 20, 230)), (30, 0.72, (255, 190, 40, 245)), (15, 0.42, (255, 250, 220, 255))):
            fd.polygon([(CX + sx - wd, ny), (CX + sx + wd, ny), (CX + sx + random.uniform(-6, 6), ny + L * ln)], fill=col)
            fd.ellipse([CX + sx - wd, ny - wd * 0.5, CX + sx + wd, ny + wd * 0.9], fill=col)
        glow = fl.filter(ImageFilter.GaussianBlur(22))
        layer = Image.alpha_composite(layer, glow)
        layer = Image.alpha_composite(layer, fl)
        layer.paste(SPRITE, (int(CX + sx - SW / 2), int(by - NOZZLE)), SPRITE)
    im = im.convert("RGBA")
    im = Image.alpha_composite(im, layer)
    return im.convert("RGB")


def make_sfx(path, sr=48000, dur=3.6, seed=3):
    """Synthesized launch: ignition thump + crackle, deep rumble, roar that fades and dulls as the rocket climbs."""
    from scipy.signal import butter, sosfilt
    import wave
    rng = np.random.default_rng(seed)
    n = int(sr * dur)
    t = np.arange(n) / sr

    def lp(x, f, o=4): return sosfilt(butter(o, f, "low", fs=sr, output="sos"), x)
    def bp(x, a, b, o=3): return sosfilt(butter(o, [a, b], "band", fs=sr, output="sos"), x)
    def env(a, peak, rel):
        e = np.clip(t / a, 0, 1) ** 0.7
        e *= np.where(t < peak, 1.0, np.exp(-(t - peak) / rel))
        return e

    white = rng.standard_normal(n)
    # ignition thump
    thump = np.sin(2 * np.pi * (55 - 20 * t) * t) * np.exp(-t / 0.18)
    burst = bp(white, 800, 6000) * np.exp(-t / 0.06) * 0.8
    # rumble
    rumble = lp(np.cumsum(white) / 300, 140)
    rumble = rumble / (np.abs(rumble).max() + 1e-9) * env(0.25, 1.4, 0.9)
    # roar: bright early, darker later (rocket moving away)
    bright = bp(white, 250, 4500)
    dark = bp(white, 120, 900)
    mixk = np.clip((t - 0.6) / 1.6, 0, 1)
    roar = (bright * (1 - mixk) + dark * mixk * 1.6)
    roar = roar / (np.abs(roar).max() + 1e-9) * env(0.35, 1.0, 0.8)
    # crackle: sparse sharp pops riding the roar
    pops = (rng.random(n) < 0.0016).astype(float) * rng.uniform(-1, 1, n)
    crackle = bp(pops, 1500, 9000) * env(0.4, 1.0, 0.6) * 6
    x = 1.0 * thump + 0.5 * burst + 0.9 * rumble + 0.75 * roar + 0.35 * crackle
    x[-int(0.2 * sr):] *= np.linspace(1, 0, int(0.2 * sr))
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    st = np.stack([x, np.roll(x, 240)], 1)            # tiny stereo width
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    return path


if __name__ == "__main__":
    import sys
    make_sfx(sys.argv[1] if len(sys.argv) > 1 else "rocket.wav")
