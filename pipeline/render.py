"""Render a 1080x1920 motion-graphics Short from script.json + build/timings.json + build/voice.wav.

Usage: python3 render.py script.json build out.mp4
Free: PIL frames piped into ffmpeg. No network.
"""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
script, build, out = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.load(open(script))
tim = json.load(open(os.path.join(build, "timings.json")))
TOTAL = tim["total"] + 0.6

FD = "/usr/share/fonts/opentype/inter/"
LANG = data.get("lang", "en")
FONT_MAIN = os.environ.get("FONT_MAIN") or data.get("font_main")
FONT_SUB = os.environ.get("FONT_SUB") or data.get("font_sub")
def font(w, s):
    if FONT_MAIN:
        sub = FONT_SUB if (w == "Bold" and FONT_SUB) else FONT_MAIN
        return ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(script)), sub), s)
    for name in (f"Inter-{w}.otf", "Inter-ExtraBold.otf", "Inter-Bold.otf"):
        p = FD + name
        if os.path.exists(p):
            return ImageFont.truetype(p, s)
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)

BG1, BG2 = (10, 12, 30), (40, 14, 70)
ACC, ACC2, WHITE, MUTED = (255, 196, 0), (255, 70, 140), (255, 255, 255), (190, 190, 215)

def ease_out(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def ease_back(x):
    x = max(0.0, min(1.0, x)); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# static background with gradient + soft glows
bg = Image.new("RGB", (W, H))
d = ImageDraw.Draw(bg)
for y in range(H):
    f = y / H
    d.line([(0, y), (W, y)], fill=tuple(int(BG1[i] + (BG2[i] - BG1[i]) * f) for i in range(3)))
glow = Image.new("RGB", (W, H), (0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([-300, 300, 700, 1300], fill=(90, 30, 140))
gd.ellipse([500, 900, 1400, 1800], fill=(140, 20, 80))
bg = Image.blend(bg, glow.filter(ImageFilter.GaussianBlur(220)), 0.35)

random.seed(7)
particles = [(random.uniform(0, W), random.uniform(0, H), random.uniform(1.5, 4), random.uniform(10, 40)) for _ in range(70)]

def text_center(dr, txt, f, y, fill, stroke=0, sfill=(0, 0, 0)):
    w = dr.textlength(txt, font=f)
    dr.text(((W - w) / 2, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill)

def scaled_text(txt, f, fill, scale, alpha):
    """Render text to its own layer so it can scale/fade."""
    bbox = f.getbbox(txt)
    tw, th = bbox[2] - bbox[0] + 40, bbox[3] - bbox[1] + 40
    layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((20 - bbox[0], 20 - bbox[1]), txt, font=f, fill=fill + (int(255 * alpha),))
    if scale != 1:
        layer = layer.resize((max(1, int(tw * scale)), max(1, int(th * scale))), Image.LANCZOS)
    return layer

def wrap(dr, txt, f, maxw):
    words, lines, cur = txt.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if dr.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

# caption chunks: words spread across each scene's speech time by character weight
captions = []
for sc, tm in zip(data["scenes"], tim["scenes"]):
    words = sc["say"].split()
    chunks, cur = [], []
    for w_ in words:
        cur.append(w_)
        if len(cur) >= 3 or w_.endswith((".", "?", ",")):
            chunks.append(" ".join(cur)); cur = []
    if cur: chunks.append(" ".join(cur))
    total_chars = sum(len(c) + 2 for c in chunks)
    t = tm["start"]
    for c in chunks:
        dur = tm["speech"] * (len(c) + 2) / total_chars
        captions.append((t, t + dur, c.upper() if LANG == "en" else c))
        t += dur

F_BIG, F_UNIT, F_SUB = font("Black", 330), font("Black", 110), font("Bold", 58)
F_PILL, F_CAP, F_HOOK = font("Bold", 40), font("Black", 74), font("Black", 230)
nfacts = sum(1 for s in data["scenes"] if s["kind"] == "fact")

INTRO = data.get("intro")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import intro_rocket, fact_anims
ANIM_FONTS = {"small": font("Black", 44), "mid": font("Black", 120)}

COVER = None
if data.get("cover"):
    COVER = Image.open(os.path.join(os.path.dirname(os.path.abspath(script)), data["cover"])).convert("RGB").resize((W, H))

def frame(t):
    im = bg.copy()
    dr = ImageDraw.Draw(im, "RGBA")
    # drifting particles
    for (x, y, r, sp) in particles:
        yy = (y - t * sp) % H
        dr.ellipse([x - r, yy - r, x + r, yy + r], fill=(255, 255, 255, 50))
    if INTRO == "rocket":
        im = intro_rocket.draw(im, t)
        dr = ImageDraw.Draw(im, "RGBA")
    # which scene
    idx = 0
    for s in tim["scenes"]:
        if t >= s["start"]: idx = s["i"]
    sc, tm = data["scenes"][idx], tim["scenes"][idx]
    lt = t - tm["start"]
    if sc.get("anim"):
        sdur = tm["end"] - tm["start"]
        fade = 1.0 if idx == len(tim["scenes"]) - 1 else max(0.0, min(1.0, (tm["end"] - t) / 0.2))
        im = fact_anims.draw(im, sc["anim"], lt, sdur, fade, ANIM_FONTS, sc.get("anim_args"), intro_rocket.SPRITE)
        dr = ImageDraw.Draw(im, "RGBA")
    # top pill
    pill = data.get("pill", "TRENDING FACTS")
    pw = dr.textlength(pill, font=F_PILL) + 60
    dr.rounded_rectangle([(W - pw) / 2, 150, (W + pw) / 2, 222], 36, fill=(255, 196, 0, 235))
    text_center(dr, pill, F_PILL, 163, (20, 15, 30))
    # fact progress dots
    if nfacts:
        cur = sc.get("n", 0 if sc["kind"] == "hook" else nfacts + 1)
        gap, r = 70, 14
        x0 = W / 2 - gap * (nfacts - 1) / 2
        for k in range(nfacts):
            on = k + 1 <= cur
            dr.ellipse([x0 + k * gap - r, 270 - r, x0 + k * gap + r, 270 + r],
                       fill=ACC + (255,) if on else (255, 255, 255, 70))
    # scene-out fade for last 0.15s
    out_a = 1.0 - ease_out((t - (tm["end"] - 0.15)) / 0.15) if t > tm["end"] - 0.15 and idx < len(tim["scenes"]) - 1 else 1.0
    if sc["kind"] == "fact":
        tag = data.get("fact_tag", "FACT #{n}").format(n=sc["n"])
        a = ease_out(lt / 0.3) * out_a
        layer = scaled_text(tag, F_SUB, ACC2, 1, a)
        im.paste(layer, (int((W - layer.width) / 2), 430), layer)
        s = 0.4 + 0.6 * ease_back(lt / 0.45)
        big = sc["big"]
        if big.isdigit() and int(big) > 1:
            big = str(int(round(int(big) * ease_out(lt / 0.7))))
        fit = min(1.0, 900 / max(1, dr.textlength(sc["big"], font=F_BIG)))  # keep wide numbers inside the frame
        layer = scaled_text(big, F_BIG, WHITE, s * fit, min(1, lt / 0.2) * out_a)
        im.paste(layer, (int((W - layer.width) / 2), int(760 - layer.height / 2)), layer)
        layer = scaled_text(sc["unit"], F_UNIT, ACC, 1, ease_out((lt - 0.25) / 0.3) * out_a)
        im.paste(layer, (int((W - layer.width) / 2), 960 + int(30 * (1 - ease_out((lt - 0.25) / 0.3)))), layer)
        # underline bar
        bw = 420 * ease_out((lt - 0.45) / 0.5)
        dr.rounded_rectangle([W / 2 - bw / 2, 1110, W / 2 + bw / 2, 1124], 7, fill=ACC2 + (int(255 * out_a),))
        y = 1160
        for line in wrap(dr, sc["sub"], F_SUB, 900):
            layer = scaled_text(line, F_SUB, MUTED, 1, ease_out((lt - 0.5) / 0.35) * out_a)
            im.paste(layer, (int((W - layer.width) / 2), y), layer); y += 76
    elif sc["kind"] == "hook" and COVER is not None:
        z = 1.0 + 0.10 * (1 - ease_out(lt / 0.35))          # punch-in: starts 10% zoomed, settles in 0.35 s
        cw, ch = int(W * z), int(H * z)
        big = COVER.resize((cw, ch), Image.LANCZOS)
        im.paste(big.crop(((cw - W) // 2, (ch - H) // 2, (cw - W) // 2 + W, (ch - H) // 2 + H)), (0, 0))
        if out_a < 1:                                       # fade to the background only at the very end
            im = Image.blend(bg, im, out_a)
        dr = ImageDraw.Draw(im, "RGBA")
    else:
        if sc["kind"] == "hook":
            # hook: fully visible from frame 0 (no fade-in from a blank screen), big, with a quick punch-in
            punch = 1.0 + 0.12 * (1 - ease_out(lt / 0.35))
            fit_big = min(1.0, 860 / max(1, dr.textlength(sc["big"], font=F_HOOK)))  # leaves room for the punch-in
            layer = scaled_text(sc["big"], F_HOOK, ACC, fit_big * punch, out_a)
            im.paste(layer, (int((W - layer.width) / 2), int(720 - layer.height / 2)), layer)
            fit_sub = min(1.0, 860 / max(1, dr.textlength(sc["sub"], font=F_UNIT)))
            layer = scaled_text(sc["sub"], F_UNIT, WHITE, fit_sub * punch, out_a)
            im.paste(layer, (int((W - layer.width) / 2), 930), layer)
        else:
            f1 = F_HOOK if len(sc["big"]) <= 7 else F_UNIT
            s = 0.5 + 0.5 * ease_back(lt / 0.5)
            layer = scaled_text(sc["big"], f1, WHITE, s, min(1, lt / 0.2) * out_a)
            im.paste(layer, (int((W - layer.width) / 2), int(720 - layer.height / 2)), layer)
            layer = scaled_text(sc["sub"], F_UNIT, ACC, 0.8, ease_out((lt - 0.3) / 0.35) * out_a)
            im.paste(layer, (int((W - layer.width) / 2), 900), layer)
    # captions (safe zone: above bottom UI, away from right-side buttons)
    for (a0, a1, c) in captions:
        if a0 <= t < a1:
            pop = 0.85 + 0.15 * ease_back((t - a0) / 0.15)
            lines = wrap(dr, c, F_CAP, 820)
            if sc["kind"] == "hook" and COVER is not None:
                break  # the cover already shows the hook in big text; captions would sit on its badge
            y = 1360
            for line in lines:
                layer = Image.new("RGBA", (W, 110), (0, 0, 0, 0))
                ld = ImageDraw.Draw(layer)
                tw = ld.textlength(line, font=F_CAP)
                ld.text(((W - tw) / 2, 10), line, font=F_CAP, fill=WHITE, stroke_width=8, stroke_fill=(0, 0, 0))
                if pop != 1:
                    layer = layer.resize((int(W * pop), int(110 * pop)), Image.LANCZOS)
                im.paste(layer, (int((W - layer.width) / 2), y), layer)
                y += 100
            break
    return im

VOICE = data.get("audio") and os.path.join(os.path.dirname(os.path.abspath(script)), data["audio"]) or os.path.join(build, "voice.wav")
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", VOICE]
if INTRO == "rocket":
    # launch sound under the voice: voice normalised first, SFX at a fixed level below it, then a limiter
    sfx = intro_rocket.make_sfx(os.path.join(build, "rocket_sfx.wav"))
    vol = data.get("sfx_volume", 0.32)
    cmd += ["-i", sfx, "-filter_complex",
            f"[1:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[v];"
            f"[2:a]volume={vol}[s];[v][s]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,apad[a]",
            "-map", "0:v", "-map", "[a]", "-shortest"]
else:
    cmd += ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11,apad", "-shortest"]
cmd += [
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
n = int(TOTAL * FPS)
for i in range(n):
    p.stdin.write(frame(i / FPS).tobytes())
# optional cover frame: the thumbnail held for the last 0.5 s, so it can be picked as the Shorts cover
cover = data.get("cover")
if cover:
    cimg = Image.open(os.path.join(os.path.dirname(os.path.abspath(script)), cover)).convert("RGB").resize((W, H))
    for _ in range(int(0.5 * FPS)):
        p.stdin.write(cimg.tobytes())
p.stdin.close(); p.wait()
print(f"wrote {out} frames={n} dur={n/FPS:.1f}s rc={p.returncode}")
