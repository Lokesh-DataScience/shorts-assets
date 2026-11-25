"""Dark paper-cutout Short: Ambani vs Bisleri (7 scenes). Reuses demo_cutout.py helpers.
Usage: python3 render_cutout.py workdir out.mp4      (workdir has voice.wav, cut.json bounds, people/ambani.png)
PREVIEW=t1,t2 for a contact sheet.
"""
import json, math, os, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
WD, OUT = sys.argv[1], sys.argv[2]
src = open(os.path.join(HERE, "demo_cutout.py")).read()
src = src[:src.index('if os.environ.get("PREVIEW")')]
ns = {"__file__": os.path.join(HERE, "demo_cutout.py")}
sys.argv = ["x", OUT, os.path.join(WD, "people", "ambani.png")]
exec(src, ns); g = globals()
for k, v in ns.items():
    if not k.startswith("__"): g[k] = v
import sfx

B = json.load(open(os.path.join(WD, "cut.json")))["bounds"]
TOTAL = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(WD, "voice.wav")]))
B[-1] = TOTAL
GREEN_W = (37, 211, 102); WHITE = (255, 255, 255); CAMPA = (230, 40, 45); CAMPA_D = (160, 20, 25)

LINES = ["Kya Ambani ne Bisleri ko ban karwaya?",
         "Number ek! Internet pe theory viral hai... Reliance ne Bisleri ko phansaaya!",
         "Number do! Sach? Bisleri ka sirf ek batch fail hua... Goa plant, bromate 12, limit 10!",
         "Number teen! Reliance ka Campa Sure... sirf 15 rupaye litre, Bisleri se 30% sasta!",
         "Number chaar! Theory ka aadhaar? Bas timing... dono same time pe!",
         "Number paanch! Lekin Bisleri ban nahi hai... aur Reliance ke khilaaf koi saboot nahi!",
         "Tum kiska paani piyoge... Bisleri ya Campa? Comment karo!"]


# ---------------------------------------------------------------- extra art
def art_text_card(lines, w=640, fill=WHITE, fg=INK, size=50, pad=34, radius=30, font=None):
    font = font or FB(size); lh = int(size * 1.25)
    h = pad * 2 + lh * len(lines)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=fill)
    for i, l in enumerate(lines):
        d.text((pad, pad + i * lh - size * 0.12), l, font=font, fill=fg)
    return im


def art_bubble(text, col=(220, 248, 198)):
    im = art_text_card([text], w=int(FB(48).getlength(text)) + 70, fill=col, size=48)
    out = Image.new("RGBA", (im.width + 30, im.height + 10), (0, 0, 0, 0)); out.alpha_composite(im, (30, 0))
    ImageDraw.Draw(out).polygon([(30, im.height - 50), (0, im.height + 6), (70, im.height - 20)], fill=col)
    return out


def art_number(n):
    f = FH(520); t = str(n); bb = f.getbbox(t)
    im = Image.new("RGBA", (bb[2] - bb[0] + 80, bb[3] - bb[1] + 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(16, 0, -2): d.text((40 - bb[0] + k, 40 - bb[1] + k), t, font=f, fill=(180, 150, 0))
    d.text((40 - bb[0], 40 - bb[1]), t, font=f, fill=YEL)
    return im


def art_reliance_block():
    f = FH(110); t = "RELIANCE"; w = int(f.getlength(t)) + 80
    im = Image.new("RGBA", (w, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, 190], fill=CAMPA); d.text((40, 10), t, font=f, fill=WHITE)
    return im


def art_report():
    w, h = 760, 820
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h], fill=(250, 248, 240))
    d.rectangle([0, 0, w, 120], fill=(30, 60, 110))
    f = FH(60); d.text((40, 18), "FSSAI TEST REPORT", font=f, fill=WHITE)
    fb = FB(44)
    rows = [("Sample", "1 BATCH"), ("Plant", "GOA"), ("Bromate", "12 µg/L"), ("Limit", "10 µg/L"), ("Result", "FAIL")]
    for i, (a, b) in enumerate(rows):
        y = 170 + i * 115
        d.line([(40, y + 95), (w - 40, y + 95)], fill=(200, 196, 185), width=3)
        d.text((50, y + 20), a, font=fb, fill=(90, 90, 90))
        d.text((400, y + 20), b, font=FH(52), fill=RED if b == "FAIL" else INK)
    for yy in range(160, h - 20, 40):
        pass
    return im


def art_tag(text, col=YEL, fg=INK, size=78):
    f = FH(size); w = int(f.getlength(text)) + 110; h = int(size * 1.5)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(0, h / 2), (50, 0), (w, 0), (w, h), (50, h)], fill=col)
    d.ellipse([28, h / 2 - 12, 52, h / 2 + 12], fill=(24, 27, 38))
    d.text((70, h * 0.04), text, font=f, fill=fg)
    return im


def art_clock():
    r = 300; im = Image.new("RGBA", (2 * r + 20, 2 * r + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = r + 10
    d.ellipse([10, 10, 2 * r + 10, 2 * r + 10], fill=(245, 245, 240), outline=(200, 200, 205), width=18)
    for i in range(12):
        a = i * math.pi / 6; r1 = r - 50 if i % 3 else r - 75
        d.line([(c + r1 * math.sin(a), c - r1 * math.cos(a)), (c + (r - 25) * math.sin(a), c - (r - 25) * math.cos(a))], fill=INK, width=12 if i % 3 == 0 else 6)
    return im


def art_comment():
    im = art_text_card(["Comment karo:", "Bisleri ya Campa?"], w=720, fill=YEL, size=62, font=FH(62))
    out = Image.new("RGBA", (im.width, im.height + 50), (0, 0, 0, 0)); out.alpha_composite(im)
    ImageDraw.Draw(out).polygon([(110, im.height - 5), (100, im.height + 50), (190, im.height - 5)], fill=YEL)
    return out


A = {}
def C(key, fn, **kw):
    if key not in A: A[key] = cutout(fn(), seed=hash(key) % 97, **kw)
    return A[key]
BOT_B = lambda: C("botB", lambda: art_bottle())
BOT_C = lambda: C("botC", lambda: art_bottle("CAMPA", CAMPA, CAMPA_D))
CLOCK = cutout(art_clock(), seed=21); NUMS = {n: cutout(art_number(n), border=10, seed=30 + n) for n in range(1, 6)}


def number_pop(base, n, t):
    """Big yellow number punches in then fades/shrinks away by 0.65s."""
    if t > 0.7: return
    k = spring(t / 0.3); a = 1.0 if t < 0.45 else clamp(1 - (t - 0.45) / 0.25)
    place(base, NUMS[n], W / 2, 900, (0.4 + 0.7 * k) * (1 + 0.3 * max(0, t - 0.45)), jit(t, n, 3), alpha=a)


def shake_im(base, amt):
    if amt <= 0: return base
    return base.transform(base.size, Image.AFFINE, (1, 0, random.uniform(-amt, amt), 0, 1, random.uniform(-amt, amt)), fillcolor=PAPER + (255,))


# ---------------------------------------------------------------- scenes
def s1(t, d):
    return scene1(t / 0.72)


def s2(t, d):
    base = BG.copy().convert("RGBA"); number_pop(base, 1, t)
    t2 = t - 0.55
    if t2 > 0:
        k = spring(t2 / 0.5)
        place(base, C("rel", art_reliance_block), W / 2 + jit(t, 1, 2), 520 - 300 * (1 - k), 1.15, -6 + jit(t, 2))
        place(base, BOT_B(), W / 2 + 160, 1180, 0.62 * max(0, k), 14 + 6 * math.sin(t * 9))
    bubbles = [("Reliance ne Bisleri ko phansaya!", 0.25, 760, 1), ("Bisleri BAN ho gaya!", 0.6, 960, -1), ("Forward karo!!", 0.95, 1360, 1)]
    for i, (txt, at, y, side) in enumerate(bubbles):
        if t2 > at:
            k = spring((t2 - at) / 0.4)
            place(base, C("bub" + str(i), lambda txt=txt: art_bubble(txt), border=8), W / 2 - 120 * side + 600 * side * (1 - k), y, 0.95, side * 3 + jit(t, 10 + i))
    sh = 0
    if t2 > 1.9:
        ks = clamp((t2 - 1.9) / 0.12)
        place(base, C("vt", lambda: art_stamp("VIRAL THEORY", col=(255, 82, 82)), border=0) if False else A.setdefault("vt", art_stamp("VIRAL THEORY", col=(255, 82, 82))),
              W / 2, 1060, 1.8 - 0.75 * eo(ks), -12, alpha=ks)
        if t2 < 2.2: sh = 18 * (1 - (t2 - 1.9) / 0.3)
    return shake_im(base, sh)


def s3(t, d):
    base = BG.copy().convert("RGBA"); number_pop(base, 2, t)
    t2 = t - 0.55
    if t2 > 0:
        k = spring(t2 / 0.45)
        place(base, A.setdefault("bt", art_strip("BEHIND THE TRUTH", bg=WHITE, size=84, seed=8)), W / 2 + 700 * (1 - k), 330, 1.0, -3 + jit(t, 3))
    if t2 > 0.35:
        k = spring((t2 - 0.35) / 0.5)
        rep = C("rep", art_report, border=10)
        place(base, rep, W / 2 + jit(t, 4, 2), 1010 + 900 * (1 - k), 1.0, 2 + jit(t, 5))
        cx, cy = W / 2, 1010
        top = cy - rep.height / 2 + 64   # approx report origin (border pad)
        # highlighter on bromate row, red circle on 12, stamp-ish FAIL emphasis
        if t2 > 1.4:
            hk = eo((t2 - 1.4) / 0.4)
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            ry = top + 170 + 2 * 115 + 10
            od.rectangle([cx - 340, ry, cx - 340 + 680 * hk, ry + 80], fill=(255, 230, 0, 110))
            if t2 > 2.0:
                ck = eo((t2 - 2.0) / 0.35)
                od.arc([cx - 20, ry - 25, cx + 165, ry + 105], -90, -90 + 360 * ck, fill=RED, width=12)
            base.alpha_composite(ov)
        if t2 > 0.9:
            sk = spring((t2 - 0.9) / 0.4)
            place(base, C("vial", lambda: art_tag("1 BATCH", col=(255, 82, 82), fg=WHITE, size=64), border=8), W / 2 + 270, 520 + 30 * (1 - sk), sk, 8)
    return base


def s4(t, d):
    base = BG.copy().convert("RGBA"); number_pop(base, 3, t)
    t2 = t - 0.55
    if t2 > 0:
        k = spring(t2 / 0.45)
        place(base, BOT_C(), W / 2 - 220, 1000 + 700 * (1 - k), 1.0, -5 + jit(t, 6))
    if t2 > 0.5:
        k = spring((t2 - 0.5) / 0.6)
        sw = 10 * math.sin(t2 * 6) * math.exp(-(t2 - 0.5) * 1.5)
        place(base, C("tag15", lambda: art_tag("₹15 / LITRE"), border=8), W / 2 - 160, 520, max(0.01, k), -8 + sw)
    if t2 > 1.4:
        k = spring((t2 - 1.4) / 0.45)
        place(base, BOT_B(), W / 2 + 270, 1080 + 700 * (1 - k), 0.85, 6 + jit(t, 7))
        p = clamp((t2 - 1.7) / 1.0); v = int(round(30 * eo(p)))
        card = art_text_card([f"{v}% SASTA"], w=430, fill=GREEN_W, fg=WHITE, size=78, font=FH(78))
        place(base, card, W / 2 + 0, 1520, max(0.01, k), -3)
    return base


def s5(t, d):
    base = BG.copy().convert("RGBA"); number_pop(base, 4, t)
    t2 = t - 0.5
    if t2 > 0:
        k = spring(t2 / 0.45)
        place(base, CLOCK, W / 2, 820, 1.0 * max(0, k), jit(t, 8, 1))
        cx, cy = W / 2, 820
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        if k > 0.6:
            sec = int(t2 * 2) / 2 * 6 * 2
            a = math.radians(sec * 6); r = 250
            od.line([(cx, cy), (cx + 170 * math.sin(math.radians(40)), cy - 170 * math.cos(math.radians(40)))], fill=INK, width=18)
            od.line([(cx, cy), (cx + r * math.sin(a), cy - r * math.cos(a))], fill=RED, width=8)
            od.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=RED)
        base.alpha_composite(ov)
    if t2 > 0.9:
        for i, (txt, x) in enumerate([("Goa sample", W / 2 - 230), ("Campa launch", W / 2 + 230)]):
            k = spring((t2 - 0.9 - 0.25 * i) / 0.4)
            place(base, C("pin" + str(i), lambda txt=txt: art_tag(txt, col=WHITE, size=52), border=6), x, 1270 - 200 * (1 - k), max(0.01, k), (-6, 6)[i])
    if t2 > 1.6:
        k = spring((t2 - 1.6) / 0.4)
        place(base, A.setdefault("st", art_strip("SIRF TIMING. SABOOT NAHI.", size=70, seed=12)), W / 2 + 700 * (1 - k), 1460, 1.0, -2)
    return base


def s6(t, d):
    base = BG.copy().convert("RGBA")
    if t < 0.55:
        number_pop(base, 5, t); return base
    im = scene6((t - 0.55) * 1.05)
    if t > 2.2:
        k = spring((t - 2.2) / 0.4)
        place(im, A.setdefault("ns", art_strip("Reliance ke khilaaf koi saboot nahi", size=56, bg=WHITE, seed=14)), W / 2 + 900 * (1 - k), 1460, 1.0, -2)
    return im


def s7(t, d):
    base = BG.copy().convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.rectangle([0, 0, W / 2, H], fill=(0, 191, 165, 40)); od.rectangle([W / 2, 0, W, H], fill=(230, 40, 45, 40))
    base.alpha_composite(ov)
    k1 = spring(t / 0.45); k2 = spring((t - 0.15) / 0.45)
    place(base, BOT_B(), W / 4 - 600 * (1 - k1), 900, 0.95, -6 + jit(t, 1))
    place(base, BOT_C(), 3 * W / 4 + 600 * (1 - k2), 900, 0.95, 6 + jit(t, 2))
    if t > 0.25:
        place(base, C("t20", lambda: art_tag("₹20", col=WHITE, size=64), border=6), W / 4, 1340, spring((t - 0.25) / 0.4), -4)
        place(base, C("t15", lambda: art_tag("₹15", col=YEL, size=64), border=6), 3 * W / 4, 1340, spring((t - 0.35) / 0.4), 4)
    sh = 0
    if t > 0.45:
        kv = clamp((t - 0.45) / 0.12)
        place(base, A.setdefault("vs", art_stamp("VS", col=YEL)), W / 2, 900, 2.0 - 0.9 * eo(kv), -8, alpha=kv)
        if t < 0.75: sh = 18 * (1 - (t - 0.45) / 0.3)
    if t > 1.0:
        k = spring((t - 1.0) / 0.45)
        place(base, C("cm", art_comment, border=8), W / 2, 380 - 300 * (1 - k), max(0.01, k), -3 + jit(t, 3))
    return shake_im(base, sh)


SCENES = [s1, s2, s3, s4, s5, s6, s7]
SFXS = [[], [("whoosh", 0.0), ("pop", 0.6), ("pop", 0.85), ("pop", 1.2), ("pop", 1.55), ("crash", 2.45)],
        [("whoosh", 0.0), ("whoosh", 0.55), ("whoosh", 0.9), ("bubbles", 1.5), ("tick", 2.55), ("buzzer", 2.6)],
        [("whoosh", 0.0), ("whoosh", 0.55), ("cash", 1.05), ("whoosh", 1.95), ("digital", 2.25)],
        [("whoosh", 0.0)] + [("tick", 0.6 + 0.5 * i) for i in range(5)],
        [("whoosh", 0.0)],
        [("whoosh", 0.0), ("crash", 0.5), ("pop", 1.1), ("ding", 1.4)]]


def caption(base, i, t, d):
    words = LINES[i].split(); n = max(1, math.ceil(len(words) / 5)); per = math.ceil(len(words) / n)
    j = min(n - 1, int(t / max(0.01, d) * n)); txt = " ".join(words[j * per:(j + 1) * per])
    f = FB(56); w = f.getlength(txt) + 60; dd = ImageDraw.Draw(base); y = 1660
    dd.rounded_rectangle([W / 2 - w / 2, y, W / 2 + w / 2, y + 100], 24, fill=WHITE)
    dd.text((W / 2 - w / 2 + 30, y + 8), txt, font=f, fill=INK)


def render_scene(i, t):
    d = B[i + 1] - B[i]
    im = SCENES[i](t, d); caption(im, i, t, d); return im


def frame(T):
    i = max(j for j in range(7) if B[j] <= T)
    t = T - B[i]
    im = render_scene(i, t)
    if i > 0 and t < 0.18:
        prev = render_scene(i - 1, B[i] - B[i - 1] - 0.001)
        im = whip(im, prev, t / 0.18)
    return im.convert("RGB")


if os.environ.get("PREVIEW"):
    ts = [float(x) for x in os.environ["PREVIEW"].split(",")]
    ims = [frame(t).resize((360, 640)) for t in ts]
    sheet = Image.new("RGB", (360 * len(ims), 640)); [sheet.paste(im, (360 * i, 0)) for i, im in enumerate(ims)]
    sheet.save(os.path.join(WD, "preview.png")); sys.exit()

def rattle_clip():
    out = np.zeros(int(sfx.SR * 1.2))
    for k in range(14):
        c = sfx.tick(0.06) * (0.6 + 0.4 * random.random()); s = int(sfx.SR * (k * 0.08 + random.uniform(0, 0.02)))
        out[s:s + len(c)] += c[:len(out) - s]
    return out * 0.8

# audio: scene-1 sfx from demo + per-scene list + chain rattle/blast in scene 6
SR = sfx.SR; tr = np.zeros(int(SR * (TOTAL + 2)))
def add(clip, at, lvl):
    s = int(SR * at); e = min(len(tr), s + len(clip)); tr[s:e] += clip[:e - s] * lvl
for nm, at, lv in [("gavel", 0.08, 0.7), ("whoosh", 0.3, 0.5), ("whoosh", 0.5, 0.55), ("pop", 0.7, 0.6), ("crash", 0.95, 0.8)]:
    add(sfx.FX[nm](), at, lv)
for i, lst in enumerate(SFXS):
    for nm, off in lst:
        add(sfx.FX[nm](), B[i] + off, sfx.LEVEL[nm])
s6t = B[5] + 0.55
add(rattle_clip(), s6t + 0.1, 0.7); add(sfx.crash(), s6t + 1.3 / 1.05, 1.0); add(sfx.gavel(), s6t + 1.3 / 1.05, 0.8); add(sfx.gavel(), s6t + 1.67 / 1.05, 0.7)
tr = np.clip(tr, -0.98, 0.98)
fxp = os.path.join(WD, "fx.wav")
with wave.open(fxp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((tr * 32767).astype(np.int16).tobytes())

voice = os.path.join(WD, "voice.wav")
p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-i", voice, "-i", fxp, "-filter_complex",
                      "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-16:TP=-2[v];[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.32[f];[v][f]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                      "-map", "0:v", "-map", "[a]", "-t", f"{TOTAL:.2f}", "-ar", "48000",
                      "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", OUT], stdin=subprocess.PIPE)
for k in range(int(TOTAL * FPS)):
    p.stdin.write(frame(k / FPS).tobytes())
p.stdin.close(); p.wait(); print("wrote", OUT, TOTAL)
