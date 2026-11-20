"""1280x720 YouTube thumbnail: big two-line hook, a falling/rising trend graphic, brand tag.

Usage: python3 thumb.py out.png "LINE ONE" "LINE TWO" [down|up] [font_main.ttf]
Keep each line to ~3 short words so it reads at phone size.
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

out, l1, l2 = sys.argv[1], sys.argv[2], sys.argv[3]
trend = sys.argv[4] if len(sys.argv) > 4 else "down"
FONT = sys.argv[5] if len(sys.argv) > 5 else "fonts/Baloo2-ExtraBold.ttf"
W, H = 1280, 720
im = Image.new("RGB", (W, H))
d = ImageDraw.Draw(im)
for y in range(H):
    f = y / H
    d.line([(0, y), (W, y)], fill=(int(14 + 40 * f), int(10 + 18 * f), int(28 - 10 * f)))
glow = Image.new("RGB", (W, H)); g = ImageDraw.Draw(glow)
g.ellipse([760, -120, 1400, 520], fill=(200, 140, 0))
im = Image.blend(im, glow.filter(ImageFilter.GaussianBlur(160)), 0.55)
d = ImageDraw.Draw(im, "RGBA")

# trend line on the right
pts = [(780, 170), (900, 260), (980, 230), (1070, 380), (1150, 500)] if trend == "down" else \
      [(780, 560), (900, 470), (980, 500), (1070, 330), (1150, 210)]
col = (255, 70, 70) if trend == "down" else (70, 220, 120)
d.line(pts, fill=col + (255,), width=26, joint="curve")
ax, ay = pts[-1]; bx, by = pts[-2]
import math
ang = math.atan2(ay - by, ax - bx)
tip = (ax + 40 * math.cos(ang), ay + 40 * math.sin(ang))
left = (ax + 60 * math.cos(ang + 2.5), ay + 60 * math.sin(ang + 2.5))
right = (ax + 60 * math.cos(ang - 2.5), ay + 60 * math.sin(ang - 2.5))
d.polygon([tip, left, right], fill=col + (255,))

def fit_font(txt, maxw, start):
    s = start
    while s > 40:
        f = ImageFont.truetype(FONT, s)
        if f.getlength(txt) <= maxw: return f
        s -= 6
    return ImageFont.truetype(FONT, 40)

f1 = fit_font(l1, 760, 170); f2 = fit_font(l2, 760, 150)
top = (H - (f1.size + 20 + f2.size)) / 2 - 30          # centre the two lines vertically
d.text((50, top), l1, font=f1, fill=(255, 255, 255), stroke_width=10, stroke_fill=(0, 0, 0))
d.text((50, top + f1.size + 20), l2, font=f2, fill=(255, 200, 0), stroke_width=10, stroke_fill=(0, 0, 0))
im.save(out, quality=92)
print("wrote", out)
