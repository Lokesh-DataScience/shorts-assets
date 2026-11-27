"""Dark paper-cutout Short: Tariff: phone dawa kapda mehenga (continuous story, 7 beats).
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

LINES = ["Hamare samvidhan ki original copy... haath se likhi gayi thi!",
         "Aaj 26 November hai... Tariff: phone dawa kapda mehenga! 1949 mein aaj hi ke din, humne apna samvidhan apnaya tha.",
         "Ise banane mein lage... 2 saal, 11 mahine aur 18 din!",
         "Prem Behari Narain Raizada ne ise apne haath se, sundar calligraphy mein likha... koi typing nahi!",
         "Ye duniya ka sabse lamba likhit samvidhan hai...",
         "Aur iski Drafting Committee ke chairman the... Dr. B.R. Ambedkar.",
         "Comment mein likho... Jai Samvidhan!"]
SAFF, IGREEN, NAVY, PARCH, PARCH_D, INKB = (255, 153, 51), (19, 136, 8), (0, 0, 128), (243, 228, 190), (196, 170, 120), (60, 40, 25)
FT = lambda s: ImageFont.truetype(os.path.join(HERE, "fonts", "TiroHindi-italic.ttf"), s)
from PIL import ImageFont


# ---------------------------------------------------------------- art
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




LINES = ["Amrika ne India pe... 25% tariff thok diya!",
         "America ka kehna hai... India ke trade tareeke, US business ko nuksaan pahuncha rahe hain.",
         "Asar padega... textiles, gems aur engineering saamaan pe. Yaani lakhon kaarigaron ki roji-roti pe.",
         "Aur dekho... Japan, Korea aur Europe pe sirf 15%... lekin India pe 25%!",
         "India ne saaf kaha... humne koi galat kaam nahi kiya, aur hum trade deal ke liye taiyaar hain.",
         "Agar deal ho gayi... to ye tariff ghat kar 17% ho sakta hai.",
         "Tumhe kya lagta hai... deal hogi ya nahi? Comment karo!"]
USRED, USBLUE = (178, 34, 52), (60, 59, 110)


def art_flag_us(w=520, h=320):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(13): d.rectangle([0, i * h / 13, w, (i + 1) * h / 13], fill=USRED if i % 2 == 0 else WHITE)
    d.rectangle([0, 0, w * 0.42, h * 7 / 13], fill=USBLUE)
    for r in range(5):
        for c in range(6):
            x = 18 + c * (w * 0.42 - 30) / 5; y = 16 + r * (h * 7 / 13 - 30) / 4
            d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=WHITE)
    return im


def art_flag_in(w=520, h=340):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, c in enumerate((SAFF, WHITE, IGREEN)): d.rectangle([0, i * h / 3, w, (i + 1) * h / 3], fill=c)
    cx, cy, r = w / 2, h / 2, h / 6 - 8
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=5)
    for k in range(24):
        a = k * math.pi / 12; d.line([(cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a))], fill=NAVY, width=2)
    return im


def art_big(text, col=(255, 82, 82), size=300):
    f = FH(size); bb = f.getbbox(text)
    im = Image.new("RGBA", (bb[2] - bb[0] + 60, bb[3] - bb[1] + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(14, 0, -2): d.text((30 - bb[0] + k, 30 - bb[1] + k), text, font=f, fill=tuple(int(c * 0.55) for c in col))
    d.text((30 - bb[0], 30 - bb[1]), text, font=f, fill=col)
    return im


def art_ship():
    im = Image.new("RGBA", (700, 380), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(0, 220), (700, 220), (620, 380), (60, 380)], fill=(40, 60, 100))
    d.rectangle([0, 210, 700, 230], fill=(200, 60, 60))
    cols = [(255, 140, 0), (0, 150, 136), (230, 60, 60), (255, 200, 0), (90, 120, 200)]
    for r in range(2):
        for c in range(6):
            d.rectangle([60 + c * 90, 130 - r * 75, 140 + c * 90, 200 - r * 75], fill=cols[(r * 3 + c) % 5], outline=(30, 30, 40), width=4)
    d.rectangle([580, 40, 660, 210], fill=WHITE, outline=(120, 120, 130), width=4)
    for y in (70, 120, 170): d.rectangle([595, y, 645, y + 25], fill=(150, 200, 235))
    return im


def art_barrier():
    im = Image.new("RGBA", (820, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([40, 40, 780, 150], fill=WHITE)
    for i in range(9): d.polygon([(40 + i * 90, 40), (90 + i * 90, 40), (40 + i * 90 + 30, 150), (40 + i * 90 - 20, 150)], fill=(230, 40, 45))
    for x in (90, 730): d.rectangle([x - 18, 150, x + 18, 230], fill=(90, 90, 100))
    f = FH(84); t = "TARIFF"; w = f.getlength(t) + 60
    d.rounded_rectangle([410 - w / 2, 48, 410 + w / 2, 142], 20, fill=INK); d.text((410 - w / 2 + 30, 50), t, font=f, fill=YEL)
    return im


def art_fabric():
    im = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 40, 290, 260], 30, fill=(200, 30, 90))
    for i in range(6): d.line([(10, 70 + i * 34), (290, 70 + i * 34)], fill=(255, 190, 60), width=8)
    d.ellipse([0, 20, 70, 280], fill=(170, 20, 70))
    return im


def art_gem():
    im = Image.new("RGBA", (300, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(60, 20), (240, 20), (290, 90), (150, 250), (10, 90)], fill=(80, 200, 255))
    d.polygon([(60, 20), (110, 90), (10, 90)], fill=(150, 230, 255)); d.polygon([(240, 20), (190, 90), (290, 90)], fill=(40, 150, 220))
    d.line([(10, 90), (290, 90)], fill=WHITE, width=5); d.polygon([(110, 90), (190, 90), (150, 250)], fill=(120, 220, 255))
    return im


def art_gear():
    im = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx = cy = 150
    for k in range(10):
        a = k * math.pi / 5
        d.polygon([(cx + 95 * math.cos(a - 0.17), cy + 95 * math.sin(a - 0.17)), (cx + 140 * math.cos(a - 0.12), cy + 140 * math.sin(a - 0.12)),
                   (cx + 140 * math.cos(a + 0.12), cy + 140 * math.sin(a + 0.12)), (cx + 95 * math.cos(a + 0.17), cy + 95 * math.sin(a + 0.17))], fill=(190, 195, 205))
    d.ellipse([45, 45, 255, 255], fill=(190, 195, 205)); d.ellipse([110, 110, 190, 190], fill=(24, 27, 38))
    return im


def art_doc():
    im = Image.new("RGBA", (560, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 560, 640], fill=(250, 248, 240)); d.rectangle([0, 0, 560, 110], fill=NAVY)
    f = FB(40); t = "COMMERCE MINISTRY"; d.text((280 - f.getlength(t) / 2, 28), t, font=f, fill=WHITE)
    for i, l in enumerate(["No structural", "excess capacity", "in any sector."]):
        f = FH(58); d.text((280 - f.getlength(l) / 2, 170 + i * 85), l, font=f, fill=INK)
    for y in (470, 520, 570): d.line([(60, y), (500, y)], fill=(200, 196, 185), width=6)
    return im


def bars(base, t, at, vals, labels, hi, x0=150, x1=930, base_y=1480, top=860):
    n = len(vals); bw = (x1 - x0) / n; d = ImageDraw.Draw(base); vmax = max(vals)
    d.line([(x0 - 20, base_y), (x1 + 20, base_y)], fill=WHITE, width=5)
    for i, (v, l) in enumerate(zip(vals, labels)):
        k = eo((t - at - 0.12 * i) / 0.6)
        if k <= 0: continue
        h = (base_y - top) * v / vmax * k; bx = x0 + i * bw
        col = (255, 82, 82) if i == hi else (200, 205, 215)
        d.rounded_rectangle([bx + 18, base_y - h, bx + bw - 18, base_y], 16, fill=col)
        f = FH(64); tv = f"{int(round(v * k))}%"; d.text((bx + bw / 2 - f.getlength(tv) / 2, base_y - h - 85), tv, font=f, fill=col)
        f = FB(44); d.text((bx + bw / 2 - f.getlength(l) / 2, base_y + 14), l, font=f, fill=WHITE)


def art_btn(text, col):
    return art_text_card([text], w=int(FH(80).getlength(text)) + 90, fill=col, fg=WHITE, size=80, font=FH(80), radius=50)


LINES = ["Phone, dawa, kapda... sab mehenga ho sakta hai! Lekin kiske liye?",
         "America ne Indian saamaan pe 25% tariff ka plan banaya hai... yaani India ka maal, America mein mehenga.",
         "Dawa, electronics, gehne, kapde... traders ke mutabik 48 billion dollar ka export khatre mein... aur lagbhag 5 lakh naukriyan!",
         "Ab traders ki maang hai... India bhi US saamaan pe 25% tariff lagaye.",
         "Agar aisa hua... to America se aane wali dal, khana-peena... yahan India mein mehenga ho sakta hai!",
         "Tumhe kya lagta hai... India ko jawab dena chahiye? Comment karo!"]
PPL = os.path.join(WD, "people")
def photo(name, h):
    im = Image.open(os.path.join(PPL, name)).convert("RGBA")
    if name.startswith("portrait"):
        im = im.crop((0, 0, im.width, int(im.height * 0.58)))
        a = np.array(im.getchannel("A"), float); hh = a.shape[0]
        fade = np.clip((hh - np.arange(hh)) / (hh * 0.12), 0, 1)[:, None]
        im.putalpha(Image.fromarray((a * fade).astype(np.uint8)))
    im = im.crop(im.getbbox()); s = h / im.height
    return im.resize((int(im.width * s), h), Image.LANCZOS)


def polaroid(name, w=860):
    im = Image.open(os.path.join(PPL, name)).convert("RGBA"); s = w / im.width
    im = im.resize((w, int(im.height * s)), Image.LANCZOS)
    out = Image.new("RGBA", (w + 40, im.height + 40), (255, 255, 255, 255)); out.alpha_composite(im, (20, 20))
    return out


def art_ball(r=110):
    n = 2 * r + 20
    yy, xx = np.mgrid[0:n, 0:n].astype(float); cx = cy = n / 2
    dist = np.hypot(xx - cx, yy - cy); m = dist <= r
    lx, ly = cx - r * 0.35, cy - r * 0.4
    sh = 1 - np.clip(np.hypot(xx - lx, yy - ly) / (r * 1.9), 0, 1)
    rgb = np.zeros((n, n, 4))
    rgb[..., 0] = 120 + 120 * sh; rgb[..., 1] = 10 + 40 * sh; rgb[..., 2] = 20 + 40 * sh; rgb[..., 3] = m * 255
    im = Image.fromarray(rgb.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    for off in (-14, 14):
        d.arc([cx - r * 1.6 + off, cy - r * 1.2, cx + r * 0.4 + off, cy + r * 1.2], -60, 60, fill=(245, 235, 225), width=5)
    for k in range(-5, 6):
        a = math.radians(k * 10); x = cx - r * 0.6 + r * math.cos(a); y = cy + r * math.sin(a)
        d.line([(x - 22, y - 4), (x + 22, y + 4)], fill=(245, 235, 225), width=3)
    d.ellipse([lx - r * 0.25, ly - r * 0.18, lx + r * 0.1, ly + r * 0.1], fill=(255, 170, 170, 160))
    return im


def art_flame():
    im = Image.new("RGBA", (220, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(110, 0), (170, 90), (210, 180), (180, 270), (110, 300), (40, 270), (10, 180), (60, 120), (80, 160)], fill=(255, 120, 0))
    d.polygon([(115, 110), (160, 190), (150, 260), (110, 285), (70, 260), (65, 200), (95, 170)], fill=(255, 210, 0))
    return im


BALL = None
def flying_balls(base, t, at, n=6, seed=1):
    global BALL
    if BALL is None: BALL = art_ball()
    for i in range(n):
        tt = t - at - i * 0.18
        if tt <= 0 or tt > 1.2: continue
        r = random.Random(seed * 31 + i); a = r.uniform(-2.4, -0.7)
        x = W / 2 + r.uniform(-150, 150) + math.cos(a) * 1300 * tt; y = 900 + math.sin(a) * 1500 * tt + 700 * tt * tt
        place(base, BALL, x, y, 0.45 * (1 - 0.4 * tt), tt * 720)


def counter_big(base, t, at, dur, target, x, y, size=300, col=YEL, suffix=""):
    p = clamp((t - at) / dur); v = int(round(target * eo(p)))
    if t >= at: place(base, art_big(f"{v}{suffix}", col=col, size=size), x, y, 1.0 + (0.05 * math.sin(t * 18) if p >= 1 else 0), jit(t, 9, 1.5))



def item(key, name, h, border=10):
    return C(key, lambda: photo(name, h), border=border)


def s0(t, d):
    base = BG.copy().convert("RGBA")
    its = [("ph", "phone_cut.png", 520, W / 2 - 290, 760, -8, 0.2), ("pl", "pills_cut.png", 470, W / 2 + 230, 700, 6, 1.0), ("cl", "cloth_cut.png", 440, W / 2, 1180, -3, 1.7)]
    shake = 3 * math.sin(t * 50) if 3.0 < t < 3.4 else 0
    for key, nm, h, x, y, r, at in its:
        if t < at: continue
        k = spring((t - at) / 0.4)
        place(base, item(key, nm, h), x + shake + jit(t, ord(key[1]), 2), y - 700 * (1 - k), 1.0, r + jit(t, ord(key[0]), 2))
    sh = stamp_in(base, "meh", "SAB MEHENGA?", (255, 82, 82), W / 2, 330, t, 3.0, -5, 1.0)
    if t > 4.6:
        k = clamp((t - 4.6) / 0.15)
        dim = Image.new("RGBA", (W, H), (10, 11, 16, int(170 * k))); base.alpha_composite(dim)
        place(base, art_big("KISKE LIYE?", col=YEL, size=150), W / 2, 960, 1.5 - 0.5 * eo(k), -3, alpha=k)
        if t < 4.9: sh = max(sh, 18)
    return shake_im(base, sh)


def s1(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.5)
    place(base, item("tm", "trumpmodi_cut.png", 520, 12), W / 2, 520 - 500 * (1 - k), 1.0, -2 + jit(t, 1, 1.5))
    if t > 1.9:
        kk = clamp((t - 1.9) / 0.12)
        place(base, art_big("25% TARIFF", col=(255, 82, 82), size=150), W / 2, 930, 1.6 - 0.6 * eo(kk), -4, alpha=kk)
    if t > 3.6:
        xs = W / 2 + 500 * (1 - eo((t - 3.6) / 1.0))
        place(base, item("ship", "ship_cut.png", 330), xs + jit(t, 3, 2), 1270 + 6 * math.sin(t * 3), 1.0, jit(t, 4, 1))
        place(base, C("route", lambda: art_tag("INDIA SE USA", col=WHITE, size=52), border=6), W / 2, 1050, spring((t - 3.9) / 0.4), 2)
    sh = stamp_in(base, "usm", "AMERICA MEIN MEHENGA", (255, 200, 0), W / 2, 1500, t, 5.6, -4, 0.62)
    return shake_im(base, sh)


def s2(t, d):
    base = BG.copy().convert("RGBA")
    its = [("pl2", "pills_cut.png", 300, "DAWA", W / 2 - 250, 560, 0.0), ("ph2", "phone_cut.png", 320, "ELECTRONICS", W / 2 + 250, 560, 0.5),
           ("rg", "ring_cut.png", 290, "GEHNE", W / 2 - 250, 980, 1.0), ("cl2", "cloth_cut.png", 280, "KAPDE", W / 2 + 250, 980, 1.5)]
    for key, nm, h, lab, x, y, at in its:
        if t < at: continue
        k = spring((t - at) / 0.4)
        place(base, item(key, nm, h, 8), x + jit(t, ord(key[0]), 2), y - 500 * (1 - k), max(0.01, k), jit(t, ord(key[1]), 3))
        place(base, C("lb" + key, lambda lab=lab: art_tag(lab, col=WHITE, size=40), border=5), x, y + 190, max(0.01, k), -3)
    p = clamp((t - 2.6) / 1.4); v = int(round(48 * eo(p)))
    if t > 2.6:
        place(base, art_big(f"${v} BILLION", col=YEL, size=130), W / 2, 1360, 1.0 + (0.04 * math.sin(t * 16) if p >= 1 else 0), -2)
    if t > 4.8:
        kk = spring((t - 4.8) / 0.45)
        place(base, S("jobs", lambda: art_strip("5 LAKH NAUKRIYAN KHATRE MEIN", bg=(255, 82, 82), fg=WHITE, size=60, seed=9)), W / 2, 1560, max(0.01, kk), 3)
    return base


def s3(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.4)
    place(base, S("mg", lambda: art_strip("TRADERS KI MAANG", bg=WHITE, size=88, seed=11)), W / 2 - 700 * (1 - k), 330, 1.0, -3)
    place(base, C("in", art_flag_in), W / 2 - 220, 800, 0.75, -6 + jit(t, 1))
    place(base, C("us", art_flag_us), W / 2 + 220, 800 + 0, 0.75, 6 + jit(t, 2))
    # arrow India -> US
    if t > 0.5:
        a = eo((t - 0.5) / 0.4); dd = ImageDraw.Draw(base)
        x0, x1, y = W / 2 - 140, W / 2 - 140 + 280 * a, 1080
        dd.line([(x0, y), (x1, y)], fill=YEL, width=18)
        if a > 0.9: dd.polygon([(x1 + 30, y), (x1 - 10, y - 30), (x1 - 10, y + 30)], fill=YEL)
    sh = stamp_in(base, "ret", "25% WAPAS?", (255, 82, 82), W / 2, 1330, t, 1.3, -6, 1.0)
    return shake_im(base, sh)


def s4(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.45)
    place(base, C("agar", lambda: art_strip("AGAR AISA HUA...", bg=WHITE, size=90, seed=12)) if False else S("agar", lambda: art_strip("AGAR AISA HUA...", bg=WHITE, size=90, seed=12)), W / 2, 320, 1.0, -3 - 14 * (1 - k), alpha=clamp(k * 2))
    if t > 1.2:
        kd = spring((t - 1.2) / 0.45)
        place(base, item("dal", "dal_cut.png", 560), W / 2 - 120, 920 + 700 * (1 - kd), 1.0, jit(t, 3, 2))
        place(base, C("usd", lambda: art_tag("US SE AANE WALI", col=WHITE, size=48), border=5), W / 2 - 120, 600, max(0.01, kd), -3)
        place(base, C("usf", lambda: art_flag_us(200, 125)), W / 2 + 300, 600, max(0.01, kd), 8)
    if t > 2.8:
        kk = spring((t - 2.8) / 0.4); dd = ImageDraw.Draw(base)
        place(base, C("up", lambda: art_tag("MEHENGA", col=(255, 82, 82), fg=WHITE, size=64), border=6), W / 2 + 250, 1150, max(0.01, kk), -8)
    sh = stamp_in(base, "indm", "INDIA MEIN!", (255, 200, 0), W / 2, 1460, t, 3.9, -5, 0.95)
    return shake_im(base, sh)


def s5(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.5)
    place(base, item("tm2", "trumpmodi_cut.png", 460, 12), W / 2, 560 - 500 * (1 - k), 1.0, jit(t, 1, 1.5))
    if t > 0.7:
        place(base, art_big("JAWAB DO?", col=YEL, size=150), W / 2, 960, spring((t - 0.7) / 0.4), -3)
    if t > 1.3:
        place(base, C("haan", lambda: art_btn("HAAN", (37, 180, 90)), border=8), W / 2 - 220, 1250, spring((t - 1.3) / 0.4), -4)
        place(base, C("na", lambda: art_btn("NA", (230, 60, 60)), border=8), W / 2 + 220, 1250, spring((t - 1.45) / 0.4), 4)
    if t > 2.0: place(base, C("fol", lambda: art_tag("COMMENT KARO • FOLLOW", col=WHITE, size=54), border=6), W / 2, 1500, spring((t - 2.0) / 0.4), -2)
    return base


SCENES = [s0, s1, s2, s3, s4, s5]

def caption(base, i, t, dur):
    words = LINES[i].split(); n = max(1, math.ceil(len(words) / 5)); per = math.ceil(len(words) / n)
    j = min(n - 1, int(t / max(0.01, dur) * n)); txt = " ".join(words[j * per:(j + 1) * per])
    f = FB(56); w = f.getlength(txt) + 60; dd = ImageDraw.Draw(base); y = 1700
    dd.rounded_rectangle([W / 2 - w / 2, y, W / 2 + w / 2, y + 100], 24, fill=WHITE)
    dd.text((W / 2 - w / 2 + 30, y + 8), txt, font=f, fill=INK)


def render_scene(i, t):
    dur = B[i + 1] - B[i]; im = SCENES[i](t, dur); caption(im, i, t, dur); return im


def frame(T):
    i = max(j for j in range(len(SCENES)) if B[j] <= T); t = T - B[i]
    im = render_scene(i, t)
    if i > 0 and t < 0.18:
        im = whip(im, render_scene(i - 1, B[i] - B[i - 1] - 0.001), t / 0.18)
    return im.convert("RGB")


if os.environ.get("PREVIEW"):
    ts = [float(x) for x in os.environ["PREVIEW"].split(",")]
    ims = [frame(t).resize((360, 640)) for t in ts]
    sheet = Image.new("RGB", (360 * len(ims), 640)); [sheet.paste(im, (360 * i, 0)) for i, im in enumerate(ims)]
    sheet.save(os.path.join(WD, "preview.png")); sys.exit()

# ---------------------------------------------------------------- audio (voice untouched: no trim, no speed, no loudness change)
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
for i in range(1, 6): add(wh, B[i] - 0.05, 0.45)
for i in range(8): add(sfx.FX['tick'](), B[2] + 2.6 + 0.17 * i, 0.4)
plan = [(0.2, "boom", 0.4), (0.2, "stamp", 0.5), (1.0, "stamp", 0.5), (1.7, "stamp", 0.5), (3.0, "stamp", 1.0), (4.6, "boom", 0.6),
        (B[1] + 1.9, "stamp", 1.0), (B[1] + 3.6, "horn", 0.3), (B[1] + 5.6, "stamp", 0.9),
        (B[2] + 0.0, "ding", 0.3), (B[2] + 0.5, "ding", 0.3), (B[2] + 1.0, "ding", 0.3), (B[2] + 1.5, "ding", 0.3), (B[2] + 2.6, "cash", 0.5), (B[2] + 4.8, "gate", 0.6),
        (B[3] + 1.3, "stamp", 1.0),
        (B[4] + 1.2, "coins", 0.5), (B[4] + 2.8, "cash", 0.5), (B[4] + 3.9, "stamp", 1.0),
        (B[5] + 0.7, "boom", 0.4), (B[5] + 1.3, "ding", 0.5)]
for at, nm, lv in plan: add(E(nm), at, lv)
tr = np.clip(tr[:int(SR * (TOTAL + 0.5))], -0.98, 0.98) * 0.5
fxp = os.path.join(WD, "fxmix.wav")
with wave.open(fxp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((tr * 32767).astype(np.int16).tobytes())
p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-i", os.path.join(WD, "voice.wav"), "-i", fxp, "-filter_complex",
                      "[1:a]aresample=48000,aformat=channel_layouts=stereo[v];[2:a]aresample=48000,aformat=channel_layouts=stereo[f];[v][f]amix=inputs=2:normalize=0[a]",
                      "-map", "0:v", "-map", "[a]", "-t", f"{TOTAL:.2f}",
                      "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", OUT], stdin=subprocess.PIPE)
for k in range(int(TOTAL * FPS)): p.stdin.write(frame(k / FPS).tobytes())
p.stdin.close(); p.wait(); print("wrote", OUT, TOTAL)
