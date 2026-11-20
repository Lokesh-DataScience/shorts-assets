"""1080x1920 high-CTR Shorts thumbnail.

Usage: python3 thumb_short.py out.png --top "छोटी लाइन" --hook "बड़ा हुक" --badge "4 सैटेलाइट" [--tag ISRO]
       [--badge-color red|green|gold] [--arrow down|up] [--font fonts/Baloo2-ExtraBold.ttf]
Design rules baked in: one huge hook (2-3 words) in gold, one short setup line in white,
one contrasting number badge, thick black outlines, everything inside the centre safe area
(channel grids crop ~ the middle 1080x1350), high-contrast dark background with a hot glow.
"""
import argparse, math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("--top", default=""); ap.add_argument("--hook", required=True)
ap.add_argument("--badge", default=""); ap.add_argument("--tag", default="")
ap.add_argument("--badge-color", default="red"); ap.add_argument("--arrow", default="")
ap.add_argument("--font", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts/Baloo2-ExtraBold.ttf"))
a = ap.parse_args()

W, H = 1080, 1920
COL = {"red": (235, 40, 50), "green": (20, 170, 90), "gold": (255, 190, 0)}
im = Image.new("RGB", (W, H))
d = ImageDraw.Draw(im)
for y in range(H):
    f = y / H
    d.line([(0, y), (W, y)], fill=(int(10 + 30 * f), int(8 + 10 * f), int(30 + 25 * f)))
glow = Image.new("RGB", (W, H)); g = ImageDraw.Draw(glow)
g.ellipse([-200, 450, 1280, 1500], fill=(190, 120, 0))
im = Image.blend(im, glow.filter(ImageFilter.GaussianBlur(220)), 0.55)
d = ImageDraw.Draw(im, "RGBA")
BG = im  # background image; foreground goes on fg and is centred at the end
# radial burst lines for energy
cx, cy = W / 2, 900
for k in range(24):
    ang = k * math.pi / 12
    d.polygon([(cx, cy), (cx + 1400 * math.cos(ang - 0.05), cy + 1400 * math.sin(ang - 0.05)),
               (cx + 1400 * math.cos(ang + 0.05), cy + 1400 * math.sin(ang + 0.05))], fill=(255, 210, 90, 18))

def font_fit(txt, maxw, start, minsize=60):
    s = start
    while s > minsize:
        f = ImageFont.truetype(a.font, s)
        if f.getlength(txt) <= maxw: return f
        s -= 6
    return ImageFont.truetype(a.font, minsize)

def centred(txt, f, y, fill, stroke=14, scol=(0, 0, 0)):
    w = d.textlength(txt, font=f)
    d.text(((W - w) / 2, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=scol)
    bb = f.getbbox(txt); return y + (bb[3] - bb[1]) + stroke

fg = Image.new("RGBA", (W, H), (0, 0, 0, 0)); im = fg; d = ImageDraw.Draw(fg, "RGBA")
y = 330
if a.tag:
    ft = ImageFont.truetype(a.font, 64); tw = d.textlength(a.tag, font=ft)
    d.rounded_rectangle([(W - tw) / 2 - 40, y, (W + tw) / 2 + 40, y + 110], 55, fill=(255, 196, 0, 255))
    d.text(((W - tw) / 2, y + 12), a.tag, font=ft, fill=(20, 15, 30))
    y += 170
if a.top:
    y = centred(a.top, font_fit(a.top, 960, 150), y, (255, 255, 255)) + 40
# hook: split into at most two lines, each as big as fits
words = a.hook.split()
lines = [a.hook] if len(words) <= 2 else [" ".join(words[: (len(words) + 1) // 2]), " ".join(words[(len(words) + 1) // 2:])]
for ln in lines:
    y = centred(ln, font_fit(ln, 1000, 260), y, (255, 205, 0), stroke=18) + 30
if a.badge:
    fb = font_fit(a.badge, 820, 130); bw = d.textlength(a.badge, font=fb); bb = fb.getbbox(a.badge)
    bh = bb[3] - bb[1]; y += 40
    box = [(W - bw) / 2 - 50, y, (W + bw) / 2 + 50, y + bh + 90]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([box[0] + 12, box[1] + 16, box[2] + 12, box[3] + 16], 40, fill=(0, 0, 0, 160))
    im.paste(sh.filter(ImageFilter.GaussianBlur(10)), (0, 0), sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle(box, 40, fill=COL.get(a.badge_color, COL["red"]) + (255,), outline=(255, 255, 255, 255), width=8)
    d.text(((W - bw) / 2, y + 45 - bb[1]), a.badge, font=fb, fill=(255, 255, 255))
    y = box[3]
if a.arrow in ("down", "up"):
    col = (255, 60, 60) if a.arrow == "down" else (40, 220, 120)
    ax, ay0, ay1 = W - 150, 380, 760
    if a.arrow == "up": ay0, ay1 = ay1, ay0
    d.line([(ax, ay0), (ax, ay1)], fill=col + (255,), width=44)
    s = 1 if a.arrow == "down" else -1
    d.polygon([(ax - 80, ay1 - 20 * s), (ax + 80, ay1 - 20 * s), (ax, ay1 + 100 * s)], fill=col + (255,))
bbox = fg.getbbox()
if bbox:
    content = fg.crop((0, bbox[1], W, bbox[3]))
    top = int(H * 0.47 - content.height / 2)
    BG.paste(content, (0, max(120, top)), content)
BG.convert("RGB").save(a.out)
print("wrote", a.out)
