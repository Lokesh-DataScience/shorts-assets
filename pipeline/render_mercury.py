"""Dark paper-cutout Short: mercury in fairness cream (continuous story, 7 beats).
Usage: python3 render_mercury.py workdir out.mp4   (workdir: voice.wav, bounds.json, fx/*.wav from earshot)
"""
import json, math, os, random, subprocess, sys, wave
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
WD, OUT = sys.argv[1], sys.argv[2]
src = open(os.path.join(HERE, "demo_cutout.py")).read()
src = src[:src.rindex('if os.environ.get("PREVIEW")')]
ns = {"__file__": os.path.join(HERE, "demo_cutout.py")}
sys.argv = ["x", OUT]
exec(src, ns); g = globals()
for k, v in ns.items():
    if not k.startswith("__"): g[k] = v
import sfx

B = json.load(open(os.path.join(WD, "bounds.json")))
TOTAL = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(WD, "voice.wav")]))
B[-1] = TOTAL
WHITE = (255, 255, 255); PINK = (255, 120, 170); KID = (214, 60, 70); KID_D = (150, 30, 40); GREEN_W = (37, 211, 102)

LINES = ["Gora hone ki cream... aur kidney kharab!",
         "Kerala mein ek 17 saal ki ladki ne online cream mangwayi... aur kuch hi time mein, use kidney ki bimari ho gayi.",
         "Jaanch hui to pata chala... cream mein mercury tha. 12,500 ppm! Jabki limit hai sirf 1 ppm.",
         "Yaani... 12,500 guna zyada zeher!",
         "Aur ye akeli nahi hai... ek hi hospital mein aise 13 case mil chuke hain.",
         "Isliye bina label wali, sasti online cream... bilkul mat kharido!",
         "Ye video apne ghar walon ko zaroor bhejo."]


# ---------------------------------------------------------------- art
def art_jar(label="FAIRNESS", sub="CREAM", unlabeled=False):
    im = Image.new("RGBA", (440, 400), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([30, 0, 410, 110], 30, fill=PINK, outline=(200, 80, 130), width=6)
    for x in range(60, 400, 30): d.line([(x, 14), (x, 96)], fill=(235, 100, 150), width=6)
    d.rounded_rectangle([10, 100, 430, 400], 50, fill=(250, 248, 252), outline=(210, 205, 220), width=6)
    if unlabeled:
        d.text((220 - FH(170).getlength("?") / 2, 110), "?", font=FH(170), fill=(180, 175, 190))
    else:
        d.rounded_rectangle([50, 170, 390, 340], 24, fill=(255, 230, 240))
        f = FH(66); d.text((220 - f.getlength(label) / 2, 175), label, font=f, fill=(200, 60, 120))
        f2 = FB(52); d.text((220 - f2.getlength(sub) / 2, 262), sub, font=f2, fill=(120, 60, 90))
    d.rounded_rectangle([40, 130, 70, 360], 14, fill=(255, 255, 255))
    return im


def art_kidney(col=KID, cold=KID_D):
    im = Image.new("RGBA", (420, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([20, 10, 400, 500], fill=col, outline=cold, width=10)
    d.ellipse([250, 180, 470, 340], fill=(0, 0, 0, 0))
    m = im.getchannel("A"); md = ImageDraw.Draw(m); md.ellipse([270, 190, 470, 330], fill=0); im.putalpha(m)
    d.arc([255, 175, 285, 345], 270, 90, fill=cold, width=10)
    d.ellipse([90, 90, 170, 200], fill=(240, 120, 130))
    return im


def crack_overlay(base, cx, cy, s, k, seed=3):
    """Jagged cracks growing from the centre (k: 0..1)."""
    if k <= 0: return
    rng = random.Random(seed); d = ImageDraw.Draw(base)
    for b in range(5):
        a = rng.uniform(0, 2 * math.pi); x, y = cx, cy
        L = int(7 * k)
        for i in range(L):
            a += rng.uniform(-0.6, 0.6); nx, ny = x + 30 * s * math.cos(a), y + 30 * s * math.sin(a)
            d.line([(x, y), (nx, ny)], fill=(25, 12, 14), width=max(3, int(9 * s * (1 - i / 8))))
            x, y = nx, ny


def art_phone():
    w, h = 470, 820
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 60, fill=(30, 32, 40))
    d.rounded_rectangle([22, 60, w - 22, h - 40], 34, fill=WHITE)
    d.rounded_rectangle([w / 2 - 60, 22, w / 2 + 60, 40], 9, fill=(70, 72, 82))
    jar = art_jar().resize((300, 273)); im.alpha_composite(jar, (int(w / 2 - 150), 110))
    f = FB(42); d.text((50, 420), "Glow Fairness Cream", font=f, fill=INK)
    d.text((50, 480), "₹99", font=FH(70), fill=(200, 40, 60))
    d.text((190, 498), "₹499", font=FB(38), fill=(150, 150, 150)); d.line([(188, 525), (290, 525)], fill=(150, 150, 150), width=4)
    d.rounded_rectangle([50, 600, w - 50, 700], 26, fill=(255, 160, 0))
    f2 = FH(56); d.text((w / 2 - f2.getlength("BUY NOW") / 2, 608), "BUY NOW", font=f2, fill=WHITE)
    return im


def art_report():
    w, h = 780, 760
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h], fill=(250, 248, 240)); d.rectangle([0, 0, w, 120], fill=(30, 60, 110))
    d.text((40, 18), "LAB TEST REPORT", font=FH(62), fill=WHITE)
    rows = [("Sample", "Fairness cream"), ("Mercury", "12,500 ppm"), ("Limit", "1 ppm"), ("Result", "DANGER")]
    for i, (a, b) in enumerate(rows):
        y = 170 + i * 140
        d.line([(40, y + 115), (w - 40, y + 115)], fill=(200, 196, 185), width=3)
        d.text((50, y + 30), a, font=FB(46), fill=(90, 90, 90))
        d.text((330, y + 22), b, font=FH(58), fill=RED if b in ("DANGER", "12,500 ppm") else INK)
    return im


def art_hospital():
    im = Image.new("RGBA", (640, 470), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([60, 90, 580, 470], fill=(236, 240, 246), outline=(180, 186, 200), width=6)
    d.rectangle([220, 0, 420, 130], fill=(236, 240, 246), outline=(180, 186, 200), width=6)
    d.rectangle([300, 20, 340, 110], fill=RED); d.rectangle([275, 45, 365, 85], fill=RED)
    for r in range(3):
        for c in range(5):
            if c == 2 and r == 2: continue
            x = 100 + c * 95; y = 170 + r * 95
            d.rectangle([x, y, x + 60, y + 55], fill=(150, 200, 235), outline=(120, 140, 170), width=4)
    d.rectangle([280, 360, 360, 470], fill=(90, 110, 140))
    f = FH(52); d.text((320 - f.getlength("HOSPITAL") / 2, 128), "HOSPITAL", font=f, fill=(60, 70, 90))
    return im


def art_patient():
    im = Image.new("RGBA", (120, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 120, 150], 18, fill=WHITE, outline=(200, 205, 215), width=4)
    d.ellipse([38, 16, 82, 60], fill=(255, 140, 140)); d.rounded_rectangle([22, 66, 98, 132], 30, fill=(255, 140, 140))
    return im


def art_share():
    im = art_text_card(["Ghar walon ko", "zaroor bhejo!"], w=700, fill=GREEN_W, fg=WHITE, size=72, font=FH(72))
    out = Image.new("RGBA", (im.width, im.height + 50), (0, 0, 0, 0)); out.alpha_composite(im)
    ImageDraw.Draw(out).polygon([(110, im.height - 5), (100, im.height + 50), (190, im.height - 5)], fill=GREEN_W)
    return out


def art_text_card(lines, w=640, fill=WHITE, fg=INK, size=50, pad=34, radius=30, font=None):
    font = font or FB(size); lh = int(size * 1.25); h = pad * 2 + lh * len(lines)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=fill)
    for i, l in enumerate(lines): d.text((pad, pad + i * lh - size * 0.12), l, font=font, fill=fg)
    return im


def art_tag(text, col=YEL, fg=INK, size=70):
    f = FH(size); w = int(f.getlength(text)) + 110; h = int(size * 1.5)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(0, h / 2), (50, 0), (w, 0), (w, h), (50, h)], fill=col)
    d.ellipse([28, h / 2 - 12, 52, h / 2 + 12], fill=(24, 27, 38)); d.text((70, h * 0.04), text, font=f, fill=fg)
    return im


A = {}
def C(key, fn, **kw):
    if key not in A: A[key] = cutout(fn(), seed=sum(map(ord, key)) % 97, **kw)
    return A[key]
def S(key, fn):
    if key not in A: A[key] = fn()
    return A[key]


def shake_im(base, amt):
    if amt <= 0: return base
    return base.transform(base.size, Image.AFFINE, (1, 0, random.uniform(-amt, amt), 0, 1, random.uniform(-amt, amt)), fillcolor=PAPER + (255,))


def stamp_in(base, key, text, col, x, y, t, at, rot=-8, scale=1.0):
    if t < at: return 0
    k = clamp((t - at) / 0.12)
    place(base, S(key, lambda: art_stamp(text, col=col)), x, y, (1.8 - 0.8 * eo(k)) * scale, rot, alpha=k)
    return 20 * (1 - (t - at) / 0.3) if t - at < 0.3 else 0


# ---------------------------------------------------------------- scenes
def s0(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.45)
    place(base, C("jar", art_jar), W / 2 - 170 + jit(t, 1, 2), 760 - 600 * (1 - k), 1.0, -8 + jit(t, 2))
    sh = 0
    if t > 1.35:
        kk = spring((t - 1.35) / 0.4)
        dim = clamp((t - 1.9) / 0.6)
        place(base, C("kid", art_kidney), W / 2 + 190, 1080 + 500 * (1 - kk), 0.85, 10 + jit(t, 3))
        crack_overlay(base, W / 2 + 160, 1080, 0.9, clamp((t - 1.9) / 0.5))
        if 1.9 < t < 2.2: sh = 16
    sh = max(sh, stamp_in(base, "x1", "KIDNEY KHARAB!", (255, 82, 82), W / 2, 1460, t, 2.3, -4, 0.75))
    if t > 0.3:
        ks = spring((t - 0.3) / 0.5)
        place(base, S("strip0", lambda: art_strip("GORA HONE KI CREAM?", size=86, seed=6)), W / 2, 300, 1.0, -2 - 16 * (1 - ks), alpha=clamp(ks * 2))
    return shake_im(base, sh)


def s1(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.5)
    place(base, C("pin", lambda: art_tag("KERALA", col=WHITE, size=64), border=6), W / 2 - 210, 330 - 300 * (1 - k), max(0.01, k), -5)
    place(base, C("age", lambda: art_tag("17 SAAL", col=YEL, size=64), border=6), W / 2 + 220, 330 - 300 * (1 - spring((t - 0.25) / 0.5)), max(0.01, spring((t - 0.25) / 0.5)), 5)
    kp = spring((t - 0.5) / 0.5)
    tap = 1.4 < t < 1.6
    place(base, C("phone", art_phone, border=10), W / 2 - (120 if t > 3.4 else 0) * eo((t - 3.4) / 0.5) + jit(t, 4, 1.5), 1010 + 900 * (1 - kp), 0.9 * (0.97 if tap else 1), -3 + jit(t, 5))
    if 1.3 < t < 1.9:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rr = 30 + 150 * (t - 1.3)
        ImageDraw.Draw(ov).ellipse([W / 2 - rr, 1300 - rr, W / 2 + rr, 1300 + rr], outline=(255, 255, 255, int(255 * (1 - (t - 1.3) / 0.6))), width=10)
        base.alpha_composite(ov)
    if t > 2.0:
        place(base, C("ordered", lambda: art_tag("ORDER PLACED", col=GREEN_W, fg=WHITE, size=54), border=6), W / 2, 1530, spring((t - 2.0) / 0.4), -3)
    if t > 3.6:
        kk = spring((t - 3.6) / 0.5)
        col = tuple(int(c * (1 - 0.35 * clamp((t - 4.6) / 1.2))) for c in KID)
        place(base, C("kid", art_kidney), W / 2 + 270 + 500 * (1 - kk), 1000, 0.6, 12 + jit(t, 6))
        crack_overlay(base, W / 2 + 250, 1000, 0.65, clamp((t - 4.8) / 0.8), seed=7)
        if t > 5.2:
            dimv = clamp((t - 5.2) / 1.0)
            ov = Image.new("RGBA", (W, H), (10, 11, 16, int(110 * dimv))); base.alpha_composite(ov)
            place(base, S("bim", lambda: art_strip("KIDNEY KI BIMARI", bg=(255, 82, 82), fg=WHITE, size=80, seed=9)), W / 2, 1530 - 0 * dimv, 1.0, -3, alpha=dimv)
    return base


def s2(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.45)
    place(base, S("jaanch", lambda: art_strip("JAANCH HUI...", bg=WHITE, size=84, seed=8)), W / 2 + 700 * (1 - k), 290, 1.0, -3 + jit(t, 3))
    kr = spring((t - 0.6) / 0.5)
    rep = C("rep", art_report, border=10)
    place(base, rep, W / 2 + jit(t, 4, 2), 980 + 900 * (1 - kr), 1.0, 1.5 + jit(t, 5))
    cx = W / 2; top = 980 - 380
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    if t > 2.3:   # highlight mercury row
        hk = eo((t - 2.3) / 0.4); ry = top + 170 + 140 + 22
        od.rectangle([cx - 350, ry, cx - 350 + 700 * hk, ry + 85], fill=(255, 230, 0, 110))
        if t > 3.0:
            ck = eo((t - 3.0) / 0.4)
            od.arc([cx - 90, ry - 30, cx + 300, ry + 115], -90, -90 + 360 * ck, fill=RED, width=12)
    if t > 4.6:   # limit row highlight green
        hk = eo((t - 4.6) / 0.4); ry = top + 170 + 2 * 140 + 22
        od.rectangle([cx - 350, ry, cx - 350 + 700 * hk, ry + 85], fill=(105, 240, 140, 100))
    base.alpha_composite(ov)
    return base


def s3(t, d):
    base = BG.copy().convert("RGBA")
    p = clamp((t - 0.3) / 1.6); v = int(round(12500 * eo(p)))
    txt = f"{v:,}×"
    f = FH(230); w = f.getlength(txt)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for kk in range(14, 0, -2): od.text((W / 2 - w / 2 + kk, 640 + kk), txt, font=f, fill=(150, 30, 30))
    od.text((W / 2 - w / 2, 640), txt, font=f, fill=(255, 82, 82))
    sc = 1 + 0.04 * math.sin(t * 20) if p >= 1 else 1
    base.alpha_composite(ov)
    place(base, S("zy", lambda: art_strip("ZYADA ZEHER!", size=96, seed=11)), W / 2, 520, spring(t / 0.45), -3)
    # danger meter
    mk = eo(p); cx, cy, r = W / 2, 1330, 300
    md = ImageDraw.Draw(base)
    for i in range(30):
        a0 = 180 + i * 6; colr = (int(60 + 195 * i / 29), int(200 - 170 * i / 29), 70)
        md.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 5, fill=colr, width=46)
    ang = math.radians(180 + 180 * min(0.97, mk) + (3 * math.sin(t * 40) if p >= 1 else 0))
    md.line([(cx, cy), (cx + (r - 30) * math.cos(ang), cy + (r - 30) * math.sin(ang))], fill=WHITE, width=14)
    md.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=WHITE)
    sh = stamp_in(base, "zeher", "ZEHER!", (255, 82, 82), W / 2 + 200, 1480, t, 2.3, -10, 0.85)
    return shake_im(base, sh)


def s4(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.45)
    place(base, S("akeli", lambda: art_strip("AKELI NAHI!", bg=WHITE, size=90, seed=12)), W / 2 - 700 * (1 - k), 280, 1.0, -3)
    kh = spring((t - 0.3) / 0.5)
    place(base, C("hosp", art_hospital, border=10), W / 2 + jit(t, 6, 1.5), 700 + 800 * (1 - kh), 0.95, jit(t, 7))
    pat = C("pat", art_patient, border=5)
    for i in range(13):
        at = 1.4 + i * 0.12
        if t < at: continue
        kk = spring((t - at) / 0.35); r, c = divmod(i, 5)
        x = W / 2 - 360 + c * 180 + (90 if r == 2 else 0); y = 1150 + r * 190
        place(base, pat, x, y - 400 * (1 - kk), 0.95, jit(t, 20 + i, 3))
    if t > 3.2:
        kk = spring((t - 3.2) / 0.4)
        place(base, C("13", lambda: art_tag("13 CASE", col=(255, 82, 82), fg=WHITE, size=70), border=6), W / 2 + 250, 460, max(0.01, kk), 8)
    return base


def s5(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.45)
    place(base, C("jarq", lambda: art_jar(unlabeled=True)), W / 2 + jit(t, 1, 2), 950 + 700 * (1 - k), 1.1, -4 + jit(t, 2))
    if t > 0.4: place(base, C("nolab", lambda: art_tag("NO LABEL", col=WHITE, size=60), border=6), W / 2 - 230, 640, spring((t - 0.4) / 0.4), -8)
    if t > 1.0: place(base, C("cheap", lambda: art_tag("SASTI ONLINE", col=YEL, size=60), border=6), W / 2 + 220, 1260, spring((t - 1.0) / 0.4), 6)
    sh = stamp_in(base, "mat", "MAT KHARIDO!", (255, 82, 82), W / 2, 1000, t, 2.2, -10, 0.9)
    return shake_im(base, sh)


def s6(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.45)
    place(base, C("share", art_share, border=8), W / 2, 760 - 400 * (1 - k), max(0.01, k), -3 + jit(t, 1))
    if t > 0.5:
        kk = spring((t - 0.5) / 0.4)
        place(base, C("fol", lambda: art_tag("FOLLOW • Khabar Ka Hisab", col=WHITE, size=54), border=6), W / 2, 1180, max(0.01, kk), 2)
        place(base, C("jar2", art_jar), W / 2 - 280, 1420, 0.45 * kk, -12)
        place(base, C("kid2", art_kidney), W / 2 + 280, 1420, 0.4 * kk, 12)
    return base


SCENES = [s0, s1, s2, s3, s4, s5, s6]


def caption(base, i, t, dur):
    words = LINES[i].split(); n = max(1, math.ceil(len(words) / 5)); per = math.ceil(len(words) / n)
    j = min(n - 1, int(t / max(0.01, dur) * n)); txt = " ".join(words[j * per:(j + 1) * per])
    f = FB(56); w = f.getlength(txt) + 60; dd = ImageDraw.Draw(base); y = 1700
    dd.rounded_rectangle([W / 2 - w / 2, y, W / 2 + w / 2, y + 100], 24, fill=WHITE)
    dd.text((W / 2 - w / 2 + 30, y + 8), txt, font=f, fill=INK)


def render_scene(i, t):
    dur = B[i + 1] - B[i]; im = SCENES[i](t, dur); caption(im, i, t, dur); return im


def frame(T):
    i = max(j for j in range(7) if B[j] <= T); t = T - B[i]
    im = render_scene(i, t)
    if i > 0 and t < 0.18:
        im = whip(im, render_scene(i - 1, B[i] - B[i - 1] - 0.001), t / 0.18)
    return im.convert("RGB")


if os.environ.get("PREVIEW"):
    ts = [float(x) for x in os.environ["PREVIEW"].split(",")]
    ims = [frame(t).resize((360, 640)) for t in ts]
    sheet = Image.new("RGB", (360 * len(ims), 640)); [sheet.paste(im, (360 * i, 0)) for i, im in enumerate(ims)]
    sheet.save(os.path.join(WD, "preview.png")); sys.exit()

# ---------------------------------------------------------------- audio
SR = sfx.SR; tr = np.zeros(int(SR * (TOTAL + 5)))
def add(clip, at, lvl):
    s = int(SR * at); e = min(len(tr), s + len(clip)); tr[s:e] += clip[:e - s] * lvl
def E(name):
    x, sr = sf.read(os.path.join(WD, "fx", name + ".wav"))
    if x.ndim > 1: x = x.mean(1)
    if sr != SR:
        import soxr; x = soxr.resample(x, sr, SR)
    return x
wh = sfx.FX["whoosh"]()
for i in range(1, 7): add(wh, B[i] - 0.05, 0.5)
plan = [(0.0, "boom", 0.5), (0.05, "stamp", 0.6), (1.35, "tap", 0.6), (1.9, "crack", 0.9), (2.3, "stamp", 0.9),
        (B[1] + 1.4, "tap", 0.9), (B[1] + 2.0, "ding", 0.6), (B[1] + 3.6, "heart", 0.7), (B[1] + 4.8, "crack", 0.7),
        (B[2] + 0.6, "stamp", 0.4), (B[2] + 3.0, "ding", 0.4),
        (B[3] + 2.3, "stamp", 0.9), (B[3] + 2.3, "boom", 0.6),
        (B[5] + 2.2, "stamp", 1.0), (B[6] + 0.1, "ding", 0.6)]
for at, nm, lv in plan: add(E(nm), at, lv)
for i in range(13): add(sfx.FX["pop"](), B[4] + 1.4 + i * 0.12, 0.35)
for i in range(10): add(sfx.FX["tick"](), B[3] + 0.3 + i * 0.16, 0.4)
tr = np.clip(tr[:int(SR * (TOTAL + 0.5))], -0.98, 0.98)
fxp = os.path.join(WD, "fxmix.wav")
with wave.open(fxp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((tr * 32767).astype(np.int16).tobytes())
p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-i", os.path.join(WD, "voice.wav"), "-i", fxp, "-filter_complex",
                      "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-16:TP=-2[v];[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.3[f];[v][f]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                      "-map", "0:v", "-map", "[a]", "-t", f"{TOTAL:.2f}", "-ar", "48000",
                      "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", OUT], stdin=subprocess.PIPE)
for k in range(int(TOTAL * FPS)): p.stdin.write(frame(k / FPS).tobytes())
p.stdin.close(); p.wait(); print("wrote", OUT, TOTAL)
