"""Dark paper-cutout Short: Samvidhan Diwas (continuous story, 7 beats).
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
         "Aaj 26 November hai... Samvidhan Diwas! 1949 mein aaj hi ke din, humne apna samvidhan apnaya tha.",
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




def art_page(lines=("WE, THE PEOPLE OF INDIA,", "having solemnly resolved", "to constitute India into a", "SOVEREIGN SOCIALIST", "SECULAR DEMOCRATIC", "REPUBLIC..."), w=640, h=820):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h], fill=PARCH)
    d.rectangle([22, 22, w - 22, h - 22], outline=PARCH_D, width=6)
    d.rectangle([36, 36, w - 36, h - 36], outline=(170, 120, 60), width=2)
    f = FT(50)
    for i, l in enumerate(lines):
        d.text((w / 2 - f.getlength(l) / 2, 110 + i * 100), l, font=f, fill=INKB)
    rng = np.random.default_rng(5); a = np.array(im)
    a[..., :3] = np.clip(a[..., :3].astype(int) + rng.normal(0, 6, a.shape[:2] + (1,)).astype(int), 0, 255)
    return Image.fromarray(a)


def art_pen():
    im = Image.new("RGBA", (120, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([30, 0, 90, 380], 26, fill=(40, 40, 60))
    d.rectangle([30, 300, 90, 330], fill=(212, 175, 55))
    d.polygon([(30, 380), (90, 380), (60, 520)], fill=(212, 175, 55))
    d.line([(60, 400), (60, 510)], fill=(90, 70, 20), width=4)
    return im


def art_calendar(top, big, sub):
    im = Image.new("RGBA", (460, 480), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 30, 460, 480], 36, fill=WHITE)
    d.rounded_rectangle([0, 30, 460, 150], 36, fill=RED); d.rectangle([0, 110, 460, 150], fill=RED)
    for x in (110, 350): d.rounded_rectangle([x - 16, 0, x + 16, 70], 14, fill=(70, 72, 82))
    f = FH(70); d.text((230 - f.getlength(top) / 2, 45), top, font=f, fill=WHITE)
    f = FH(190); d.text((230 - f.getlength(big) / 2, 140), big, font=f, fill=INK)
    f = FH(72); d.text((230 - f.getlength(sub) / 2, 370), sub, font=f, fill=(120, 120, 130))
    return im


def art_scroll(h=1000):
    w = 560
    im = Image.new("RGBA", (w, h + 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([40, 60, w - 40, h + 60], fill=PARCH)
    for i in range(int(h / 46)):
        y = 110 + i * 46; ln = (w - 140) * (0.6 + 0.4 * ((i * 37) % 10) / 10)
        d.line([(70, y), (70 + ln, y)], fill=(170, 140, 95), width=6)
    for y in (0, h + 60):
        d.rounded_rectangle([0, y, w, y + 60], 30, fill=PARCH_D, outline=(150, 110, 60), width=5)
    return im


def art_namecard():
    w, h = 820, 430
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], 40, fill=WHITE)
    d.rounded_rectangle([0, 0, w, 110], 40, fill=NAVY); d.rectangle([0, 70, w, 110], fill=NAVY)
    f = FB(48); t = "DRAFTING COMMITTEE CHAIRMAN"; d.text((w / 2 - f.getlength(t) / 2, 24), t, font=f, fill=WHITE)
    t = "Dr. B.R. Ambedkar"; sz = 110
    while FH(sz).getlength(t) > w - 70: sz -= 4
    f = FH(sz); d.text((w / 2 - f.getlength(t) / 2, 150), t, font=f, fill=INK)
    for i, c in enumerate((SAFF, WHITE, IGREEN)):
        d.rectangle([60 + i * 233, 340, 60 + (i + 1) * 233, 370], fill=c if c != WHITE else (225, 225, 225))
    return im


def art_tricolor(text):
    w, h = 900, 330
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, c in enumerate((SAFF, WHITE, IGREEN)): d.rectangle([0, i * 110, w, (i + 1) * 110], fill=c)
    sz = 120
    while FH(sz).getlength(text) > w - 70: sz -= 4
    f = FH(sz); d.text((w / 2 - f.getlength(text) / 2, 165 - sz * 0.72), text, font=f, fill=NAVY)
    return im


def art_comment():
    im = art_text_card(["Comment karo:", "Jai Samvidhan!"], w=640, fill=YEL, size=66, font=FH(66))
    out = Image.new("RGBA", (im.width, im.height + 50), (0, 0, 0, 0)); out.alpha_composite(im)
    ImageDraw.Draw(out).polygon([(110, im.height - 5), (100, im.height + 50), (190, im.height - 5)], fill=YEL)
    return out


def writing(base, x0, y0, wd, t, at, dur, seed=1):
    """Ink line being written, with the pen following its tip. Returns pen pos."""
    k = clamp((t - at) / dur)
    if k <= 0: return None
    d = ImageDraw.Draw(base); pts = []
    n = int(60 * k) + 1
    for i in range(n):
        u = i / 60; x = x0 + wd * u; y = y0 + 14 * math.sin(u * 40 + seed) + 8 * math.sin(u * 97)
        pts.append((x, y))
    if len(pts) > 1: d.line(pts, fill=INKB, width=7, joint="curve")
    return pts[-1]


# ---------------------------------------------------------------- scenes
def s0(t, d):
    base = BG.copy().convert("RGBA")
    pg = C("page", art_page, border=10)
    for i in range(3):
        k = spring((t - 0.12 * i) / 0.5)
        place(base, pg, W / 2 + (i - 1) * 40 + jit(t, i, 2), 920 + 900 * (1 - k), 0.95, (i - 1) * 7 + jit(t, 5 + i))
    if t > 1.4:
        tip = writing(base, W / 2 - 230, 1250, 460, t, 1.4, 1.8)
        if tip: place(base, C("pen", art_pen, border=6), tip[0] + 40, tip[1] - 230, 0.9, -25)
    k = spring((t - 0.25) / 0.5)
    place(base, S("s0", lambda: art_strip("HAATH SE LIKHA!", size=96, seed=6)), W / 2, 300, 1.0, -2 - 16 * (1 - k), alpha=clamp(k * 2))
    return base


def s1(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.45)
    place(base, C("cal", lambda: art_calendar("NOVEMBER", "26", "1949"), border=10), W / 2 + jit(t, 1, 2), 900 - 700 * (1 - k), 1.15, -4 + jit(t, 2))
    if t > 1.0:
        kk = spring((t - 1.0) / 0.45)
        place(base, S("sd", lambda: art_tricolor("SAMVIDHAN DIWAS")), W / 2 + 900 * (1 - kk), 360, 0.95, -3 + jit(t, 3))
    if t > 3.2:
        place(base, C("ap", lambda: art_tag("APNAYA GAYA", col=WHITE, size=64), border=6), W / 2, 1420, spring((t - 3.2) / 0.4), 3)
    return base


def s2(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.45)
    place(base, S("s2", lambda: art_strip("BANANE MEIN LAGE", bg=WHITE, size=86, seed=8)), W / 2 - 700 * (1 - k), 300, 1.0, -3)
    items = [("2", "SAAL", 2.0), ("11", "MAHINE", 3.6), ("18", "DIN", 5.2)]
    for i, (n, u, at) in enumerate(items):
        if t < at: continue
        kk = spring((t - at) / 0.45); prog = clamp((t - at) / 0.6)
        v = int(round(int(n) * eo(prog)))
        card = art_text_card([f"{v} {u}"], w=600, fill=(YEL, WHITE, (105, 240, 140))[i], size=110, font=FH(110))
        place(base, card, W / 2 + (i - 1) * 30, 640 + i * 300 - 300 * (1 - kk), max(0.01, kk), (i - 1) * 4 + jit(t, 10 + i))
    return base


def s3(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.5)
    place(base, C("page", art_page, border=10), W / 2 + jit(t, 1, 2), 950 + 900 * (1 - k), 1.05, -2 + jit(t, 2))
    if t > 0.8:
        kk = spring((t - 0.8) / 0.45)
        place(base, C("raiz", lambda: art_tag("Prem Behari Narain Raizada", col=YEL, size=54), border=6), W / 2, 330, max(0.01, kk), -3)
    for j in range(2):
        tip = writing(base, W / 2 - 250, 1290 + j * 70, 500, t, 1.5 + j * 1.4, 1.3, seed=j + 2)
        if tip and t < 1.5 + j * 1.4 + 1.35: place(base, C("pen", art_pen, border=6), tip[0] + 40, tip[1] - 230, 0.9, -25)
    if t > 3.3:
        kk = spring((t - 3.3) / 0.4)
        place(base, C("cal2", lambda: art_tag("CALLIGRAPHY", col=WHITE, size=54), border=6), W / 2 + 240, 1520, max(0.01, kk), 5)
    sh = stamp_in(base, "nt", "NO TYPING!", (255, 82, 82), W / 2, 760, t, 4.6, -10, 0.9)
    return shake_im(base, sh)


def s4(t, d):
    base = BG.copy().convert("RGBA")
    k = eo(t / 1.2)
    sc = cutout(art_scroll(int(60 + 1100 * k)), seed=4, border=8) if k < 1 else C("scroll", lambda: art_scroll(1160), border=8)
    place(base, sc, W / 2 + jit(t, 1, 2), 380 + sc.height / 2 * 0.95, 0.95, jit(t, 2))
    sh = stamp_in(base, "sl", "SABSE LAMBA!", (255, 82, 82), W / 2, 1050, t, 1.4, -8, 0.95)
    if t > 1.9: place(base, C("dm", lambda: art_tag("DUNIYA MEIN", col=YEL, size=64), border=6), W / 2, 1300, spring((t - 1.9) / 0.4), 4)
    return shake_im(base, sh)


def s5(t, d):
    base = BG.copy().convert("RGBA")
    k = spring((t - 0.2) / 0.5)
    place(base, C("book", lambda: art_page(("CONSTITUTION", "OF", "INDIA")), border=10), W / 2 + jit(t, 1, 2), 700 - 600 * (1 - k), 0.7, -5 + jit(t, 2))
    if t > 2.2:
        kk = spring((t - 2.2) / 0.5)
        place(base, C("nc", art_namecard, border=10), W / 2 + jit(t, 3, 2), 1300 + 700 * (1 - kk), 1.0, 2 + jit(t, 4))
    return base


def s6(t, d):
    base = BG.copy().convert("RGBA")
    k = spring(t / 0.45)
    place(base, C("cm", art_comment, border=8), W / 2, 560 - 400 * (1 - k), max(0.01, k), -3 + jit(t, 1))
    if t > 0.9:
        kk = spring((t - 0.9) / 0.45)
        place(base, S("js", lambda: art_tricolor("JAI SAMVIDHAN")), W / 2, 1100, max(0.01, kk), 2 + jit(t, 2))
        place(base, C("fol", lambda: art_tag("FOLLOW • Khabar Ka Hisab", col=WHITE, size=54), border=6), W / 2, 1450, max(0.01, spring((t - 1.2) / 0.4)), -2)
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
for i in range(1, 7): add(wh, B[i] - 0.05, 0.45)
plan = [(0.0, "page", 0.8), (0.15, "page", 0.6), (1.4, "pen", 0.7),
        (B[1] + 0.0, "page", 0.7), (B[1] + 1.0, "boom", 0.4), (B[1] + 3.2, "ding", 0.4),
        (B[2] + 2.0, "stamp", 0.5), (B[2] + 3.6, "stamp", 0.5), (B[2] + 5.2, "stamp", 0.6),
        (B[3] + 1.5, "pen", 0.6), (B[3] + 2.9, "pen", 0.5), (B[3] + 4.6, "stamp", 0.9),
        (B[4] + 0.0, "scroll", 0.8), (B[4] + 1.4, "stamp", 0.9),
        (B[5] + 2.2, "boom", 0.45), (B[6] + 0.0, "ding", 0.5), (B[6] + 0.9, "boom", 0.4)]
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
