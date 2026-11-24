"""Daily-bulletin thumbnail (1080x1920): header + all 5 stories as colored cards in one frame.

Usage: python3 thumb_bulletin.py items.json out.png
items.json: {"date": "23 नवंबर", "title": "आज की 5 बड़ी ख़बरें",
             "items": [{"text": "सेंसेक्स −1,484", "sub": "बाज़ार धड़ाम", "icon": "down", "color": "red"}, ...]}
icons: down, up, bottle, gavel, cricket, chip, rupee, globe, alert, flag, plane, rocket
colors: red, blue, green, orange, purple, teal, pink, gold
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FM = lambda s: ImageFont.truetype(os.path.join(HERE, "fonts", "Baloo2-ExtraBold.ttf"), s)
FS = lambda s: ImageFont.truetype(os.path.join(HERE, "fonts", "Mukta-Bold.ttf"), s)
COL = {"red": ((235, 45, 60), (150, 15, 40)), "blue": ((40, 120, 240), (20, 50, 150)), "green": ((30, 185, 110), (10, 100, 60)),
       "orange": ((255, 140, 20), (190, 70, 0)), "purple": ((150, 70, 235), (80, 25, 150)), "teal": ((20, 185, 190), (5, 100, 120)),
       "pink": ((240, 60, 150), (150, 20, 90)), "gold": ((255, 190, 0), (190, 120, 0))}
GOLD, WHITE, INK = (255, 200, 0), (255, 255, 255), (20, 15, 30)


def grad(w, h, c1, c2):
    g = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(g)
    for x in range(w):
        f = x / max(1, w - 1)
        d.line([(x, 0), (x, h)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * f) for i in range(3)))
    return g


def icon(d, name, cx, cy, s, w=WHITE):
    if name in ("down", "up"):
        sgn = 1 if name == "down" else -1
        pts = [(cx - 0.9 * s, cy - 0.5 * s * sgn), (cx - 0.3 * s, cy + 0.1 * sgn * s), (cx + 0.1 * s, cy - 0.2 * sgn * s), (cx + 0.7 * s, cy + 0.5 * sgn * s)]
        d.line(pts, fill=w, width=int(s * 0.18), joint="curve")
        tip = pts[-1]
        d.polygon([(tip[0] + 0.2 * s, tip[1] + 0.2 * s * sgn), (tip[0] - 0.35 * s, tip[1] + 0.05 * s * sgn), (tip[0] + 0.05 * s, tip[1] - 0.35 * s * sgn)], fill=w)
    elif name == "bottle":
        d.rounded_rectangle([cx - 0.18 * s, cy - 0.95 * s, cx + 0.18 * s, cy - 0.7 * s], 6, fill=w)
        d.rounded_rectangle([cx - 0.42 * s, cy - 0.72 * s, cx + 0.42 * s, cy + 0.9 * s], int(0.25 * s), fill=w)
        d.line([(cx - 0.5 * s, cy - 0.3 * s), (cx + 0.5 * s, cy + 0.5 * s)], fill=(230, 40, 50), width=int(0.16 * s))
    elif name == "gavel":
        d.line([(cx + 0.7 * s, cy + 0.7 * s), (cx - 0.1 * s, cy - 0.1 * s)], fill=w, width=int(0.2 * s))
        g = [(cx - 0.75 * s, cy - 0.3 * s), (cx - 0.3 * s, cy - 0.75 * s), (cx + 0.1 * s, cy - 0.35 * s), (cx - 0.35 * s, cy + 0.1 * s)]
        d.polygon(g, fill=w)
        d.rectangle([cx - 0.9 * s, cy + 0.75 * s, cx + 0.3 * s, cy + 0.92 * s], fill=w)
    elif name == "cricket":
        d.line([(cx - 0.75 * s, cy + 0.75 * s), (cx + 0.35 * s, cy - 0.35 * s)], fill=w, width=int(0.32 * s))
        d.line([(cx + 0.35 * s, cy - 0.35 * s), (cx + 0.7 * s, cy - 0.7 * s)], fill=w, width=int(0.12 * s))
        d.ellipse([cx + 0.25 * s, cy + 0.2 * s, cx + 0.7 * s, cy + 0.65 * s], fill=(255, 220, 220))
    elif name == "chip":
        d.rounded_rectangle([cx - 0.55 * s, cy - 0.55 * s, cx + 0.55 * s, cy + 0.55 * s], int(0.12 * s), fill=w)
        for k in range(3):
            o = (k - 1) * 0.3 * s
            for a, b, c, e in ((cx - 0.55 * s, cy + o, cx - 0.85 * s, cy + o), (cx + 0.55 * s, cy + o, cx + 0.85 * s, cy + o),
                               (cx + o, cy - 0.55 * s, cx + o, cy - 0.85 * s), (cx + o, cy + 0.55 * s, cx + o, cy + 0.85 * s)):
                d.line([(a, b), (c, e)], fill=w, width=int(0.1 * s))
        f = FM(int(0.6 * s))
        d.text((cx - d.textlength("AI", font=f) / 2, cy - 0.5 * s), "AI", font=f, fill=INK)
    elif name == "rupee":
        f = FM(int(1.6 * s)); d.text((cx - d.textlength("₹", font=f) / 2, cy - 1.0 * s), "₹", font=f, fill=w)
    elif name == "alert":
        d.polygon([(cx, cy - 0.9 * s), (cx + 0.9 * s, cy + 0.75 * s), (cx - 0.9 * s, cy + 0.75 * s)], fill=w)
        f = FM(int(1.0 * s)); d.text((cx - d.textlength("!", font=f) / 2, cy - 0.65 * s), "!", font=f, fill=INK)
    elif name == "globe":
        d.ellipse([cx - 0.85 * s, cy - 0.85 * s, cx + 0.85 * s, cy + 0.85 * s], outline=w, width=int(0.12 * s))
        d.ellipse([cx - 0.4 * s, cy - 0.85 * s, cx + 0.4 * s, cy + 0.85 * s], outline=w, width=int(0.08 * s))
        d.line([(cx - 0.85 * s, cy), (cx + 0.85 * s, cy)], fill=w, width=int(0.08 * s))
    elif name == "rocket":
        d.polygon([(cx, cy - 0.95 * s), (cx + 0.35 * s, cy - 0.3 * s), (cx + 0.35 * s, cy + 0.5 * s), (cx - 0.35 * s, cy + 0.5 * s), (cx - 0.35 * s, cy - 0.3 * s)], fill=w)
        d.polygon([(cx - 0.2 * s, cy + 0.5 * s), (cx + 0.2 * s, cy + 0.5 * s), (cx, cy + 0.95 * s)], fill=(255, 160, 40))
    elif name == "plane":
        d.polygon([(cx - 0.9 * s, cy), (cx + 0.9 * s, cy - 0.1 * s), (cx + 0.9 * s, cy + 0.1 * s)], fill=w)
        d.polygon([(cx - 0.1 * s, cy), (cx + 0.3 * s, cy - 0.75 * s), (cx + 0.45 * s, cy)], fill=w)
        d.polygon([(cx - 0.1 * s, cy), (cx + 0.3 * s, cy + 0.75 * s), (cx + 0.45 * s, cy)], fill=w)
    else:
        f = FM(int(1.2 * s)); d.text((cx - d.textlength("•", font=f) / 2, cy - 0.8 * s), "•", font=f, fill=w)


def fit(d, text, font_fn, size, maxw):
    while size > 30 and d.textlength(text, font=font_fn(size)) > maxw:
        size -= 2
    return font_fn(size)


def main(src, out):
    cfg = json.load(open(src))
    if cfg.get("theme") == "clean":
        return main_clean(cfg, out)
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        f = y / H
        d.line([(0, y), (W, y)], fill=(int(18 + 20 * f), int(10 + 8 * f), int(40 + 25 * f)))
    # light rays behind the header
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(rays)
    for k in range(18):
        a = k * math.pi / 9
        rd.polygon([(540, 260), (540 + 1500 * math.cos(a - 0.06), 260 + 1500 * math.sin(a - 0.06)),
                    (540 + 1500 * math.cos(a + 0.06), 260 + 1500 * math.sin(a + 0.06))], fill=(255, 200, 0, 22))
    im = Image.alpha_composite(im.convert("RGBA"), rays.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    # header
    date = cfg.get("date", "")
    if date:
        f = FS(54); w = d.textlength(date, font=f) + 70
        d.rounded_rectangle([540 - w / 2, 60, 540 + w / 2, 140], 40, fill=GOLD)
        d.text((540 - d.textlength(date, font=f) / 2, 64), date, font=f, fill=INK)
    t1, t2 = cfg.get("title1", "आज की 5"), cfg.get("title2", "बड़ी ख़बरें!")
    f1 = fit(d, t1, FM, 150, 980); f2 = fit(d, t2, FM, 190, 1000)
    d.text((540 - d.textlength(t1, font=f1) / 2, 150), t1, font=f1, fill=WHITE, stroke_width=10, stroke_fill=INK)
    d.text((540 - d.textlength(t2, font=f2) / 2, 300), t2, font=f2, fill=GOLD, stroke_width=12, stroke_fill=INK)
    # cards
    items = cfg["items"][:5]
    top, gap, ch = 545, 20, 232
    for i, it in enumerate(items):
        y = top + i * (ch + gap)
        c1, c2 = COL.get(it.get("color", "blue"), COL["blue"])
        x0, x1 = 50, W - 50
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([x0 + 8, y + 12, x1 + 8, y + ch + 12], 36, fill=(0, 0, 0, 140))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
        card = grad(x1 - x0, ch, c1, c2)
        m = Image.new("L", card.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, card.width - 1, ch - 1], 36, fill=255)
        im.paste(card, (x0, y), m)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([x0, y, x1, y + ch], 36, outline=(255, 255, 255, 90), width=3)
        # number badge
        bx, by = x0 + 85, y + ch / 2
        d.ellipse([bx - 62, by - 62, bx + 62, by + 62], fill=WHITE)
        fn = FM(96); n = str(i + 1)
        d.text((bx - d.textlength(n, font=fn) / 2, by - 78), n, font=fn, fill=c2)
        # icon
        icon(d, it.get("icon", ""), x1 - 115, by, 70)
        # text
        maxw = (x1 - 215) - (bx + 85)
        ft = fit(d, it["text"], FM, 92, maxw)
        d.text((bx + 85, y + 22), it["text"], font=ft, fill=WHITE, stroke_width=5, stroke_fill=(0, 0, 0))
        if it.get("sub"):
            fs = fit(d, it["sub"], FS, 52, maxw)
            d.text((bx + 87, y + 143), it["sub"], font=fs, fill=(255, 245, 210))
    # footer
    ft = cfg.get("footer", "ख़बर का हिसाब")
    f = FS(48); w = d.textlength(ft, font=f) + 60
    d.rounded_rectangle([540 - w / 2, H - 95, 540 + w / 2, H - 28], 35, fill=(255, 255, 255, 230))
    d.text((540 - d.textlength(ft, font=f) / 2, H - 93), ft, font=f, fill=INK)
    im.convert("RGB").save(out)
    print("wrote", out)


def main_clean(cfg, out):
    GREEN, INKc, GRAYc, LINEc = (0, 200, 83), (17, 17, 17), (110, 110, 110), (229, 229, 229)
    im = Image.new("RGBA", (W, H), (250, 250, 250, 255)); d = ImageDraw.Draw(im)
    for y in range(60, H, 48):
        for x in range(30, W, 48):
            d.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=(230, 230, 230))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse([-300, 80, 500, 800], fill=(128, 232, 157, 110)); gd.ellipse([620, 1250, 1400, 2050], fill=(128, 232, 157, 90))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(120))); d = ImageDraw.Draw(im)
    m, a = 40, 90
    for (x, y, sx, sy) in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        d.line([(x, y + sy * a), (x, y), (x + sx * a, y)], fill=GREEN, width=9)
    SER = lambda s_: ImageFont.truetype(os.path.join(HERE, "fonts", "TiroHindi-italic.ttf"), s_)
    date = cfg.get("date", "")
    if date:
        f = FS(50); w = d.textlength(date, font=f) + 70
        d.rounded_rectangle([540 - w / 2, 80, 540 + w / 2, 156], 38, fill=INKc)
        d.text((540 - d.textlength(date, font=f) / 2, 84), date, font=f, fill=WHITE)
    t1, t2 = cfg.get("title1", "आज की"), cfg.get("title2", "5 बड़ी ख़बरें")
    f1 = fit(d, t1, FM, 150, 980); f2 = fit(d, t2, SER, 175, 1000)
    d.text((540 - d.textlength(t1, font=f1) / 2, 160), t1, font=f1, fill=INKc)
    d.text((540 - d.textlength(t2, font=f2) / 2, 385), t2, font=f2, fill=GREEN)
    w2 = d.textlength(t2, font=f2)
    d.line([(540 - w2 / 2 + 10 + k * (w2 - 20) / 30, 598 + 7 * math.sin(k * 0.9)) for k in range(31)], fill=GREEN, width=8)
    top, gap, ch = 640, 18, 218
    for i, it in enumerate(cfg["items"][:5]):
        y = top + i * (ch + gap); x0, x1 = 50, W - 50
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([x0, y + 14, x1, y + ch + 14], 34, fill=(0, 0, 0, 40))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(im)
        d.rounded_rectangle([x0, y, x1, y + ch], 34, fill=WHITE, outline=LINEc, width=2)
        bx, by = x0 + 95, y + ch / 2
        pts = [(bx + 70 * math.cos(math.pi / 6 + k * math.pi / 3), by + 70 * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)]
        d.polygon(pts, fill=GREEN)
        fn = FM(92); n = str(i + 1); d.text((bx - d.textlength(n, font=fn) / 2, by - 72), n, font=fn, fill=WHITE)
        icon(d, it.get("icon", ""), x1 - 105, by, 62, w=GREEN)
        maxw = (x1 - 190) - (bx + 95)
        ft = fit(d, it["text"], FM, 90, maxw)
        d.text((bx + 95, y + 22), it["text"], font=ft, fill=INKc)
        if it.get("sub"):
            fs_ = fit(d, it["sub"], FS, 50, maxw)
            d.text((bx + 97, y + 134), it["sub"], font=fs_, fill=GRAYc)
    ft = cfg.get("footer", "ख़बर का हिसाब"); f = FS(46); w = d.textlength(ft, font=f) + 60
    d.rounded_rectangle([540 - w / 2, H - 100, 540 + w / 2, H - 34], 33, fill=GREEN)
    d.text((540 - d.textlength(ft, font=f) / 2, H - 98), ft, font=f, fill=WHITE)
    im.convert("RGB").save(out); print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
