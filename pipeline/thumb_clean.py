"""Single-topic Shorts thumbnail in the clean white/green style (1080x1920).

Usage: python3 thumb_clean.py cfg.json out.png
cfg: {"tag": "FSSAI vs बिसलेरी", "line1": "बिसलेरी का", "line2": "पानी फ़ेल?", "badge": "सिर्फ़ 1 बैच • पूरा सच",
      "art": "frame.png"  (optional: a PNG cut from a video frame to place in the middle)}
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
GREEN, GREEN_L, INK, WHITE, RED = (0, 200, 83), (128, 232, 157), (17, 17, 17), (255, 255, 255), (230, 50, 50)
FH = lambda s: ImageFont.truetype(os.path.join(HERE, "fonts", "Baloo2-ExtraBold.ttf"), s)
FB = lambda s: ImageFont.truetype(os.path.join(HERE, "fonts", "Mukta-Bold.ttf"), s)
FS = lambda s: ImageFont.truetype(os.path.join(HERE, "fonts", "TiroHindi-italic.ttf"), s)


def fit(fn, t, size, maxw):
    while size > 40 and fn(size).getlength(t) > maxw:
        size -= 4
    return fn(size)


def main(cfg, out, base_dir):
    im = Image.new("RGBA", (W, H), (250, 250, 250, 255)); d = ImageDraw.Draw(im)
    for y in range(60, H, 48):
        for x in range(30, W, 48):
            d.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=(230, 230, 230))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse([-300, 500, 500, 1300], fill=GREEN_L + (120,)); gd.ellipse([650, 1200, 1450, 2000], fill=GREEN_L + (100,))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(120))); d = ImageDraw.Draw(im)
    m, a = 40, 100
    for (x, y, sx, sy) in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        d.line([(x, y + sy * a), (x, y), (x + sx * a, y)], fill=GREEN, width=10)
    tag = cfg.get("tag", "")
    if tag:
        f = FB(56); w = f.getlength(tag) + 80
        d.rounded_rectangle([540 - w / 2, 120, 540 + w / 2, 210], 45, fill=INK)
        d.text((540 - f.getlength(tag) / 2, 126), tag, font=f, fill=WHITE)
    l1, l2 = cfg.get("line1", ""), cfg.get("line2", "")
    f1 = fit(FH, l1, 190, 960); f2 = fit(FS, l2, 230, 1000)
    d.text((540 - f1.getlength(l1) / 2, 250), l1, font=f1, fill=INK)
    d.text((540 - f2.getlength(l2) / 2, 520), l2, font=f2, fill=GREEN)
    w2 = f2.getlength(l2)
    d.line([(540 - w2 / 2 + 10 + k * (w2 - 20) / 30, 815 + 9 * math.sin(k * 0.9)) for k in range(31)], fill=GREEN, width=11)
    art = cfg.get("art")
    if art:
        A = Image.open(os.path.join(base_dir, art)).convert("RGBA")
        A.thumbnail((900, 760))
        im.alpha_composite(A, (int(540 - A.width / 2), int(860 + (740 - A.height) / 2)))
    badge = cfg.get("badge", "")
    if badge:
        d = ImageDraw.Draw(im)
        f = fit(FB, badge, 72, 900); w = f.getlength(badge) + 90
        d.rounded_rectangle([540 - w / 2, 1620, 540 + w / 2, 1745], 62, fill=RED if cfg.get("badge_red") else GREEN)
        d.text((540 - f.getlength(badge) / 2, 1633), badge, font=f, fill=WHITE)
    im.convert("RGB").save(out); print("wrote", out)


if __name__ == "__main__":
    src = sys.argv[1]
    main(json.load(open(src)), sys.argv[2], os.path.dirname(os.path.abspath(src)))
