"""5-second paper-cutout style demo: Scene 1 hook (photo -> bottle -> red ?) + Scene 6 chain break.
Usage: python3 demo_cutout.py out.mp4 [photo.png]
"""
import math, os, subprocess, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import sfx

W, H, FPS, DUR = 1080, 1920, 30, 5.0
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]; PHOTO = sys.argv[2] if len(sys.argv) > 2 else None
FH = lambda s: ImageFont.truetype(os.path.join(HERE, "fonts", "Baloo2-ExtraBold.ttf"), s)
FB = lambda s: ImageFont.truetype(os.path.join(HERE, "fonts", "Mukta-Bold.ttf"), s)
TEAL, TEAL_D, RED, INK, YEL, PAPER = (0, 191, 165), (0, 137, 123), (255, 82, 82), (25, 25, 25), (255, 221, 0), (24, 27, 38)


def clamp(x): return max(0.0, min(1.0, x))
def spring(x, k=9.0, z=0.42):
    x = max(0.0, x)
    return 1 - math.exp(-z * k * x * 1.6) * math.cos(k * x * 1.15) if x < 3 else 1.0
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def jit(t, seed, amt=1.6):
    """Stop-motion wobble: changes 12 times a second."""
    r = random.Random(int(t * 12) * 97 + seed); return r.uniform(-amt, amt)


# ---------------------------------------------------------------- paper background
def make_bg():
    rng = np.random.default_rng(3)
    n = rng.normal(0, 6, (H, W, 1))
    base = np.array(PAPER, float)[None, None, :] + n
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    fib = Image.new("L", (W, H), 0); d = ImageDraw.Draw(fib)
    for _ in range(900):
        x, y = rng.uniform(0, W), rng.uniform(0, H); a = rng.uniform(0, math.pi); l = rng.uniform(8, 30)
        d.line([(x, y), (x + l * math.cos(a), y + l * math.sin(a))], fill=int(rng.uniform(10, 30)), width=1)
    im = Image.composite(Image.new("RGB", (W, H), (44, 48, 64)), im, fib)
    d = ImageDraw.Draw(im)
    for y in range(0, H, 34):
        for x in range(0, W, 34):
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(38, 42, 56))
    v = Image.new("L", (W, H), 0); ImageDraw.Draw(v).ellipse([-300, -200, W + 300, H + 200], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(220))
    return Image.composite(im, Image.new("RGB", (W, H), (10, 11, 16)), v)
BG = make_bg()


# ---------------------------------------------------------------- cutout helpers
def torn_mask(mask, seed=1, amp=7):
    """Roughen the alpha edge like torn paper."""
    rng = np.random.default_rng(seed)
    a = np.array(mask.filter(ImageFilter.GaussianBlur(2)), float)
    noise = rng.normal(0, 1, (mask.height // 6 + 1, mask.width // 6 + 1))
    noise = np.array(Image.fromarray(((noise * 40) + 128).clip(0, 255).astype(np.uint8)).resize(mask.size, Image.BICUBIC), float) - 128
    return Image.fromarray(((a + noise * amp / 10) > 128).astype(np.uint8) * 255)


def cutout(art, border=14, seed=1):
    """Art (RGBA) -> white-bordered torn paper sticker with drop shadow. Returns RGBA."""
    pad = border + 40
    big = Image.new("RGBA", (art.width + 2 * pad, art.height + 2 * pad), (0, 0, 0, 0))
    big.alpha_composite(art, (pad, pad))
    a = big.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    outer = torn_mask(a.filter(ImageFilter.MaxFilter(border * 2 + 1)), seed)
    sh = Image.new("RGBA", big.size, (0, 0, 0, 0)); sh.putalpha(outer.point(lambda v: v * 0.7))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    res = Image.new("RGBA", big.size, (0, 0, 0, 0))
    res.alpha_composite(sh, (10, 16))
    wl = Image.new("RGBA", big.size, (255, 253, 248, 0)); wl.putalpha(outer)
    res.alpha_composite(wl); res.alpha_composite(big)
    return res


def place(base, im, cx, cy, s=1.0, rot=0.0, alpha=1.0):
    if s <= 0.02 or alpha <= 0.01: return
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


# ---------------------------------------------------------------- art
def art_person():
    if PHOTO and os.path.exists(PHOTO):
        p = Image.open(PHOTO).convert("RGBA"); p = p.crop(p.getbbox()); sc = 720 / p.width; return p.resize((720, int(p.height * sc)), Image.LANCZOS)
    im = Image.new("RGBA", (600, 720), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([190, 60, 410, 300], fill=(205, 210, 222))
    d.rounded_rectangle([60, 330, 540, 720], 200, fill=(205, 210, 222))
    d.polygon([(300, 330), (250, 500), (300, 560), (350, 500)], fill=(255, 255, 255))
    d.polygon([(300, 345), (275, 470), (300, 520), (325, 470)], fill=(255, 82, 82))
    f = FB(46); t = "AMBANI PHOTO"
    d.rounded_rectangle([110, 600, 490, 680], 20, fill=INK)
    d.text((300 - f.getlength(t) / 2, 604), t, font=f, fill=(255, 255, 255))
    return im


def art_bottle(label="BISLERI", col=TEAL, cold=TEAL_D):
    im = Image.new("RGBA", (300, 760), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([110, 0, 190, 60], 10, fill=cold)
    d.polygon([(115, 60), (185, 60), (250, 170), (50, 170)], fill=(200, 235, 240))
    d.rounded_rectangle([40, 150, 260, 750], 60, fill=(205, 238, 242), outline=(150, 200, 210), width=6)
    for y in (230, 640):
        d.line([(50, y), (250, y)], fill=(170, 215, 222), width=6)
    d.rounded_rectangle([75, 200, 105, 700], 14, fill=(255, 255, 255, 150))
    d.rectangle([40, 330, 260, 540], fill=col)
    f = FH(58); d.text((150 - f.getlength(label) / 2, 380), label, font=f, fill=(255, 255, 255))
    return im


def art_qmark():
    f = FH(620); t = "?"
    bb = f.getbbox(t); im = Image.new("RGBA", (bb[2] - bb[0] + 80, bb[3] - bb[1] + 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(18, 0, -2):
        d.text((40 - bb[0] + k, 40 - bb[1] + k), t, font=f, fill=(140, 20, 20))
    d.text((40 - bb[0], 40 - bb[1]), t, font=f, fill=RED)
    return im


def art_strip(text, fg=INK, bg=YEL, size=96, seed=5):
    f = FH(size); w = int(f.getlength(text)) + 90; h = int(size * 1.35)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h], fill=bg)
    d.text((45, h * 0.02), text, font=f, fill=fg)
    m = torn_mask(Image.new("L", (w, h), 255).crop((0, 0, w, h)).resize((w, h)), seed, amp=14)
    m = Image.fromarray(np.array(m) * 0 + 255)
    im2 = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); im2.alpha_composite(im, (20, 20))
    a = Image.new("L", im2.size, 0); ImageDraw.Draw(a).rectangle([20, 20, w + 20, h + 20], fill=255)
    a = torn_mask(a, seed, amp=18); im2.putalpha(ImageChops.multiply(im2.getchannel("A"), a))
    return im2


def art_stamp(text, col=RED):
    f = FH(120); w = int(f.getlength(text)) + 80; h = 190
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, w - 6, h - 6], 24, outline=col, width=12)
    d.text((40, 10), text, font=f, fill=col)
    rng = np.random.default_rng(4)
    a = np.array(im.getchannel("A"), float) * (rng.uniform(0.55, 1, (h, w)) > 0.18)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im


def link_img(horiz):
    im = Image.new("RGBA", (120, 70) if horiz else (70, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    box = [6, 6, 114, 64] if horiz else [6, 6, 64, 114]
    d.ellipse(box, outline=(40, 44, 58), width=22)
    d.ellipse([box[0] + 3, box[1] + 3, box[2] - 3, box[3] - 3], outline=(225, 228, 236), width=14)
    d.ellipse([b + (3 if i < 2 else -3) for i, b in enumerate(box)], outline=(255, 255, 255), width=5)
    return im


def art_lock():
    im = Image.new("RGBA", (200, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.arc([40, 0, 160, 130], 180, 360, fill=(220, 224, 232), width=26)
    d.line([(53, 65), (53, 100)], fill=(220, 224, 232), width=26); d.line([(147, 65), (147, 100)], fill=(220, 224, 232), width=26)
    d.rounded_rectangle([10, 90, 190, 230], 26, fill=(200, 160, 40), outline=(130, 100, 20), width=8)
    d.ellipse([85, 130, 115, 160], fill=INK); d.rectangle([94, 150, 106, 195], fill=INK)
    return im


PERSON = cutout(art_person(), seed=2)
BOTTLE = cutout(art_bottle(), seed=3)
QMARK = cutout(art_qmark(), border=12, seed=4)
STRIP = art_strip("AMBANI vs BISLERI?", seed=6)
STAMP = art_stamp("BAN NAHI!", col=(105, 240, 140))
LOCK = cutout(art_lock(), border=8, seed=7)
LINKS = [link_img(True), link_img(False)]
BOTTLE6 = cutout(art_bottle(), seed=9)


# ---------------------------------------------------------------- scenes
def scene1(t):
    base = BG.copy().convert("RGBA")
    shake = 0
    # person
    k = spring(t / 0.45)
    place(base, PERSON, W / 2 - 90 + jit(t, 1, 3), 830 - 500 * (1 - min(1, k)) + jit(t, 2, 3), 0.95 * max(0, k) ** 0.3, -3 + jit(t, 3))
    if t > 0.7:
        kb = spring((t - 0.7) / 0.4)
        place(base, BOTTLE, W / 2 + 250 + 500 * (1 - kb), 1050, 0.95, 8 + jit(t, 4) - 20 * (1 - kb))
    if t > 1.3:
        kq = clamp((t - 1.3) / 0.12)
        s = 1.6 - 0.6 * eo(kq)
        place(base, QMARK, W / 2 + 250, 980, s * 0.95, -10 + jit(t, 5), alpha=kq)
        if t < 1.6: shake = 22 * (1 - (t - 1.3) / 0.3)
    if t > 0.35:
        ks = spring((t - 0.35) / 0.5)
        place(base, STRIP, W / 2 + jit(t, 6, 2), 300, 1.0, -2 - 18 * (1 - ks) + jit(t, 7), alpha=clamp(ks * 2))
    if shake:
        base = base.transform(base.size, Image.AFFINE, (1, 0, random.uniform(-shake, shake), 0, 1, random.uniform(-shake, shake)), fillcolor=PAPER + (255,))
    return base


SHARDS = [(random.Random(i).uniform(0, 2 * math.pi), random.Random(i + 50).uniform(500, 1500), random.Random(i + 9).uniform(-720, 720), 0) for i in range(36)]


BANDS = [(-28, 860), (28, 1000), (-28, 1150)]
NL = 12
def chain_pos(i, n=None):
    """Three diagonal chain bands wrapped across the bottle."""
    b, j = divmod(i, NL); ang, cy = BANDS[b % 3]
    u = (j - (NL - 1) / 2) * 52
    a = math.radians(ang)
    return W / 2 + u * math.cos(a), cy - u * math.sin(a), ang + (90 if j % 2 else 0)


def scene6(t):
    base = BG.copy().convert("RGBA")
    br = 1.3  # chain break time
    rattle = 6 * math.sin(t * 60) if t < br else 0
    place(base, BOTTLE6, W / 2 + rattle * 0.6 + jit(t, 11, 2), 1000, 1.1, jit(t, 12, 1.5))
    n = NL * 3
    if t < br:
        k = spring(t / 0.4)
        for i in range(n):
            x, y, r = chain_pos(i, n)
            place(base, LINKS[0], x + rattle * (1 if i % 2 else -1), y - 400 * (1 - k), 1.0, r)
        place(base, LOCK, W / 2 + rattle, 1000 + 400 * (1 - k), 0.9, jit(t, 13, 4))
    else:
        u = t - br
        for i, (a, sp, rs, hz) in enumerate(SHARDS):
            x0, y0, r0 = chain_pos(i)
            x = x0 + math.cos(a) * sp * u; y = y0 + math.sin(a) * sp * u + 900 * u * u
            place(base, LINKS[hz], x, y, 1.0, r0 + rs * u, alpha=clamp(1.4 - u * 1.2))
        lx = W / 2 + 200 * u; ly = 1000 - 600 * u + 1500 * u * u
        place(base, LOCK, lx, ly, 0.9, 300 * u, alpha=clamp(1.3 - u))
        if u < 0.25:
            fl = Image.new("RGBA", (W, H), (255, 250, 220, int(230 * (1 - u / 0.25)))); base.alpha_composite(fl)
            g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            rr = 200 + 1600 * u
            ImageDraw.Draw(g).ellipse([W / 2 - rr, 1000 - rr, W / 2 + rr, 1000 + rr], outline=(255, 200, 60, 200), width=40)
            base.alpha_composite(g.filter(ImageFilter.GaussianBlur(12)))
        if u > 0.35:
            ks = clamp((u - 0.35) / 0.12)
            place(base, STAMP, W / 2, 400, 1.7 - 0.7 * eo(ks), -8, alpha=ks)
    sh = 24 * (1 - (t - br) / 0.35) if br <= t < br + 0.35 else 0
    if sh:
        base = base.transform(base.size, Image.AFFINE, (1, 0, random.uniform(-sh, sh), 0, 1, random.uniform(-sh, sh)), fillcolor=PAPER + (255,))
    return base


CAP1, CAP6 = "Kya Ambani ne Bisleri ko ban karwaya?", "Bisleri ban nahi hai!"
def caption(base, txt, t):
    f = FB(54); w = f.getlength(txt) + 60; d = ImageDraw.Draw(base)
    y = 1640
    d.rounded_rectangle([W / 2 - w / 2, y, W / 2 + w / 2, y + 96], 22, fill=(255, 255, 255))
    d.text((W / 2 - w / 2 + 30, y + 8), txt, font=f, fill=INK)


def whip(base, prev, u):
    """Whip-pan transition: both frames slide up with blur."""
    off = int(H * eo(u))
    out = Image.new("RGBA", (W, H))
    out.alpha_composite(prev.filter(ImageFilter.BoxBlur(18)), (0, -off))
    out.alpha_composite(base.filter(ImageFilter.BoxBlur(18 * (1 - u))), (0, H - off))
    return out


SPLIT = 2.5
def frame(t):
    if t < SPLIT:
        im = scene1(t); caption(im, CAP1, t)
    else:
        im = scene6(t - SPLIT); caption(im, CAP6, t)
        if t - SPLIT < 0.18:
            prev = scene1(SPLIT); caption(prev, CAP1, SPLIT)
            im = whip(im, prev, (t - SPLIT) / 0.18)
    return im.convert("RGB")


if os.environ.get("PREVIEW"):
    ts = [float(x) for x in os.environ["PREVIEW"].split(",")]
    ims = [frame(t).resize((360, 640)) for t in ts]
    sheet = Image.new("RGB", (360 * len(ims), 640)); [sheet.paste(im, (360 * i, 0)) for i, im in enumerate(ims)]
    sheet.save("preview_cutout.png"); sys.exit()

# ---------------------------------------------------------------- audio
def rattle_clip():
    out = np.zeros(int(sfx.SR * 1.2))
    for k in range(14):
        c = sfx.tick(0.06) * (0.6 + 0.4 * random.random()); s = int(sfx.SR * (k * 0.08 + random.uniform(0, 0.02)))
        out[s:s + len(c)] += c[:len(out) - s]
    return out * 0.8
SR = sfx.SR; track = np.zeros(int(SR * (DUR + 1)))
def add(clip, at, lvl):
    s = int(SR * at); e = min(len(track), s + len(clip)); track[s:e] += clip[:e - s] * lvl
add(sfx.gavel(), 0.12, 0.7); add(sfx.whoosh(), 0.35, 0.5); add(sfx.whoosh(), 0.7, 0.55); add(sfx.pop(), 0.95, 0.6)
add(sfx.crash(), 1.3, 0.8); add(sfx.whoosh(), SPLIT - 0.05, 0.6); add(rattle_clip(), SPLIT + 0.1, 0.7)
add(sfx.crash(), SPLIT + 1.3, 1.0); add(sfx.gavel(), SPLIT + 1.3, 0.8); add(sfx.gavel(), SPLIT + 1.67, 0.7); add(sfx.ding(), SPLIT + 1.75, 0.5)
track = np.clip(track, -0.98, 0.98)
import wave
with wave.open("/tmp/demo_sfx.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((track * 32767).astype(np.int16).tobytes())

p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-i", "/tmp/demo_sfx.wav", "-af", "loudnorm=I=-14:TP=-1.5", "-ar", "48000", "-t", str(DUR),
                      "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", OUT], stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait(); print("wrote", OUT)
