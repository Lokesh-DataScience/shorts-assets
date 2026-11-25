"""Clean white / green motion-graphics renderer (reference style, Nov 2026).

White canvas, vibrant green accent (#00C853), black bold Hindi text with green italic-serif highlight lines,
green corner brackets, hexagon number badge with a progress ring, soft-shadow illustration card with green
line-art animation, alternating green/outline pill tags, snappy spring motion, word-by-word headlines.

Usage: python3 render_clean.py scene.json build out.mp4      (needs build/timings.json from align.py)
scene.json is the usual format; each story scene can add "icon" + "icon_args"; "sfx" works as in render.py.
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
script, build, out = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.load(open(script))
tim = json.load(open(os.path.join(build, "timings.json")))
TOTAL = tim["total"] + 0.6
SCN = data["scenes"]; TS = tim["scenes"]
NSTORY = sum(1 for s in SCN if s["kind"] == "fact")

GREEN, GREEN_D, GREEN_L = (0, 200, 83), (0, 150, 62), (128, 232, 157)
INK, GRAY, LINE, BGC = (17, 17, 17), (110, 110, 110), (229, 229, 229), (250, 250, 250)
F = lambda n, s: ImageFont.truetype(os.path.join(HERE, "fonts", n), s)
F_HEAD = lambda s: F("Baloo2-ExtraBold.ttf", s)
F_BODY = lambda s: F("Mukta-Bold.ttf", s)
F_SERIF = lambda s: F("TiroHindi-italic.ttf", s)


# ---------------------------------------------------------------- easing
def clamp(x): return max(0.0, min(1.0, x))
def spring(x, k=8.0, z=0.45):
    """Damped spring 0 -> 1 with a small overshoot."""
    x = max(0.0, x)
    return 1 - math.exp(-z * k * x * 1.6) * math.cos(k * x * 1.15) if x < 3 else 1.0
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3


# ---------------------------------------------------------------- background (precomputed)
def make_bg():
    im = Image.new("RGB", (W, H), BGC)
    d = ImageDraw.Draw(im)
    for y in range(60, H, 48):
        for x in range(30, W, 48):
            d.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=(232, 232, 232))
    return im
BG = make_bg()
def blob(r, a):
    b = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
    ImageDraw.Draw(b).ellipse([r, r, 3 * r, 3 * r], fill=GREEN_L + (a,))
    return b.filter(ImageFilter.GaussianBlur(r * 0.45))
BLOB_A, BLOB_B = blob(260, 70), blob(200, 55)


def background(t):
    im = BG.copy().convert("RGBA")
    im.alpha_composite(BLOB_A, (int(-420 + 60 * math.sin(t * 0.4)), int(150 + 80 * math.cos(t * 0.3))))
    im.alpha_composite(BLOB_B, (int(560 + 70 * math.cos(t * 0.35)), int(1150 + 60 * math.sin(t * 0.5))))
    return im


def brackets(d, t):
    m, a, w = 42, 78, 7
    br = 4 * math.sin(t * 2)
    for (x, y, sx, sy) in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        x += sx * br * 0; y += 0
        d.line([(x, y + sy * (a + br)), (x, y), (x + sx * (a + br), y)], fill=GREEN, width=w, joint="curve")


# ---------------------------------------------------------------- text helpers
def text_layer(txt, font, fill, stroke=0, sfill=None):
    bb = font.getbbox(txt, stroke_width=stroke)
    L = Image.new("RGBA", (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(L).text((10 - bb[0], 10 - bb[1]), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return L


def fit_font(fn, txt, size, maxw):
    while size > 34 and fn(size).getlength(txt) > maxw:
        size -= 3
    return fn(size)


def word_layer(txt, font, fill):
    """Fixed-height layer (ascent+descent) so every word shares one baseline."""
    asc, desc = font.getmetrics()
    bb = font.getbbox(txt)
    L = Image.new("RGBA", (bb[2] - bb[0] + 20, asc + desc + 20), (0, 0, 0, 0))
    ImageDraw.Draw(L).text((10 - bb[0], 10), txt, font=font, fill=fill)
    return L


def paste(base, L, cx, top, alpha=1.0, scale=1.0, dx=0, dy=0):
    if scale != 1.0:
        L = L.resize((max(1, int(L.width * scale)), max(1, int(L.height * scale))), Image.LANCZOS)
    if alpha < 1:
        L = L.copy(); L.putalpha(L.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(L, (int(cx - L.width / 2 + dx), int(top + dy)))


def words_in(base, txt, font, fill, cx, top, lt, delay=0.0, stagger=0.07):
    """Word-by-word slide-up with spring; returns height used."""
    words = txt.split()
    layers = [word_layer(w, font, fill) for w in words]
    sp = font.getlength(" ")
    total = sum(l.width - 20 for l in layers) + sp * (len(words) - 1)
    x = cx - total / 2
    for i, (w, L) in enumerate(zip(words, layers)):
        p = spring((lt - delay - i * stagger) / 0.55)
        if p > 0.01:
            a = clamp(p * 1.4)
            base.alpha_composite(_alpha(L, a), (int(x - 10), int(top + 50 * (1 - p))))
        x += L.width - 20 + sp
    return layers[0].height if layers else 0


def _alpha(L, a):
    if a >= 1: return L
    L = L.copy(); L.putalpha(L.getchannel("A").point(lambda v: int(v * a))); return L


def shadow_card(base, x0, y0, x1, y1, r=34, alpha=1.0):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + 14, x1, y1 + 14], r, fill=(0, 0, 0, int(28 * alpha)))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([x0, y0, x1, y1], r, fill=(255, 255, 255, int(255 * alpha)), outline=LINE + (int(255 * alpha),), width=2)


def hexagon(d, cx, cy, r, fill, rot=0.0):
    pts = [(cx + r * math.cos(math.pi / 6 + k * math.pi / 3 + rot), cy + r * math.sin(math.pi / 6 + k * math.pi / 3 + rot)) for k in range(6)]
    d.polygon(pts, fill=fill)


# ---------------------------------------------------------------- line-art icons (inside card box)
def ic_closed(d, box, lt, a):
    x0, y0, x1, y1 = box; cx = (x0 + x1) / 2
    sx0, sx1, top = cx - 200, cx + 120, y0 + 60
    d.rectangle([sx0 - 20, top - 30, sx1 + 20, top], fill=INK)
    h = (y1 - 50 - top) * eo(lt / 1.0)
    d.rectangle([sx0, top, sx1, top + h], outline=GREEN, width=6)
    for k in range(int(h / 34)):
        d.line([(sx0 + 6, top + 24 + k * 34), (sx1 - 6, top + 24 + k * 34)], fill=GREEN, width=4)
    d.line([(sx0 - 40, y1 - 46), (sx1 + 40, y1 - 46)], fill=INK, width=5)
    sw = 0.15 * math.sin(lt * 3)
    hx, hy = (sx0 + sx1) / 2, top + 30
    if lt > 0.9:
        k = spring((lt - 0.9) / 0.5)
        L = Image.new("RGBA", (240, 160), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        ld.rounded_rectangle([10, 40, 230, 150], 16, fill=GREEN)
        ld.line([(60, 40), (120, 4), (180, 40)], fill=INK, width=4)
        t = d._label if hasattr(d, "_label") else "बंद"
        f = F_HEAD(70); ld.text((120 - f.getlength(t) / 2, 42), t, font=f, fill=(255, 255, 255))
        L = L.rotate(math.degrees(sw), resample=Image.BICUBIC, center=(120, 4))
        L = L.resize((max(1, int(240 * k)), max(1, int(160 * k))))
        d._im.alpha_composite(L, (int(hx - L.width / 2), int(hy + 20)))
    # diya
    dx, dy = cx + 250, y1 - 70
    d.chord([dx - 70, dy - 40, dx + 70, dy + 40], 0, 180, fill=GREEN)
    fl = 1 + 0.12 * math.sin(lt * 14)
    d.polygon([(dx - 14, dy - 4), (dx, dy - 4 - 60 * fl), (dx + 14, dy - 4)], fill=(255, 170, 0))
    d.polygon([(dx - 6, dy - 6), (dx, dy - 6 - 30 * fl), (dx + 6, dy - 6)], fill=(255, 235, 120))


def ic_aqi(d, box, lt, a):
    x0, y0, x1, y1 = box
    val, vmax = float(a.get("value", 242)), float(a.get("max", 500))
    gx, gy, r = x0 + 470, y1 - 70, 185
    r = 165
    d.arc([gx - r, gy - r, gx + r, gy + r], 180, 360, fill=LINE, width=34)
    p = eo(lt / 1.4) * val / vmax
    d.arc([gx - r, gy - r, gx + r, gy + r], 180, 180 + 180 * p, fill=GREEN, width=34)
    ang = math.pi + math.pi * p
    d.line([(gx, gy), (gx + (r - 50) * math.cos(ang), gy + (r - 50) * math.sin(ang))], fill=INK, width=8)
    d.ellipse([gx - 16, gy - 16, gx + 16, gy + 16], fill=INK)
    f = F_HEAD(64); t = "AQI " + str(int(val * eo(lt / 1.4)))
    d.text((gx - f.getlength(t) / 2, gy - r - 92), t, font=f, fill=INK)
    # car + badge
    cx, cy = x0 + 150, y1 - 120
    d.rounded_rectangle([cx - 110, cy - 30, cx + 110, cy + 35], 24, outline=INK, width=6)
    d.polygon([(cx - 60, cy - 30), (cx - 30, cy - 80), (cx + 50, cy - 80), (cx + 80, cy - 30)], outline=INK, width=6)
    for wx in (cx - 60, cx + 60):
        d.ellipse([wx - 28, cy + 12, wx + 28, cy + 68], fill=INK); d.ellipse([wx - 10, cy + 30, wx + 10, cy + 50], fill=(255, 255, 255))
    if lt > 0.6:
        k = spring((lt - 0.6) / 0.45); t = a.get("badge", "BS6"); fb = F_HEAD(int(52 * max(0.05, k)))
        w = fb.getlength(t) + 34
        d.rounded_rectangle([cx - w / 2, y0 + 40, cx + w / 2, y0 + 40 + 76 * k], 38, fill=GREEN)
        if k > 0.6: d.text((cx - fb.getlength(t) / 2, y0 + 42), t, font=fb, fill=(255, 255, 255))
    for k in range(3):                                       # smoke puffs from the exhaust
        ph = (lt * 0.8 + k / 3) % 1
        sx = cx - 130 - 80 * ph; sy = cy + 10 - 30 * ph; rr = 12 + 26 * ph
        d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], outline=(180, 180, 180, int(255 * (1 - ph))), width=4)


def _train(d, x, y, s, nose=False):
    if nose:
        d.polygon([(x - 260 * s, y - 50 * s), (x + 40 * s, y - 50 * s), (x + 200 * s, y + 20 * s), (x + 210 * s, y + 45 * s), (x - 260 * s, y + 45 * s)], outline=INK, fill=(255, 255, 255), width=6)
        d.line([(x - 240 * s, y + 5 * s), (x + 150 * s, y + 5 * s)], fill=GREEN, width=int(10 * s))
        d.polygon([(x + 40 * s, y - 42 * s), (x + 120 * s, y - 10 * s), (x + 40 * s, y - 10 * s)], fill=INK)
    else:
        for c in range(2):
            cx0 = x - 300 * s + c * 290 * s
            d.rounded_rectangle([cx0, y - 60 * s, cx0 + 270 * s, y + 40 * s], int(16 * s), outline=INK, fill=(255, 255, 255), width=6)
            for wv in range(3):
                d.rectangle([cx0 + 25 * s + wv * 80 * s, y - 40 * s, cx0 + 75 * s + wv * 80 * s, y - 5 * s], fill=GREEN)
            for wx in (cx0 + 50 * s, cx0 + 220 * s):
                d.ellipse([wx - 18 * s, y + 30 * s, wx + 18 * s, y + 66 * s], fill=INK)


def ic_train(d, box, lt, a):
    x0, y0, x1, y1 = box
    ty = y1 - 70
    d.line([(x0 + 30, ty + 70), (x1 - 30, ty + 70)], fill=INK, width=5)
    for k in range(18):
        x = x0 + 40 + k * 40
        d.line([(x, ty + 62), (x + 20, ty + 78)], fill=GRAY, width=3)
    # route with two stations
    ax, bx, ry = x0 + 90, x1 - 90, y0 + 70
    p = eo(lt / 1.4)
    for k in range(int((bx - ax) / 26 * p)):
        d.line([(ax + k * 26, ry), (ax + k * 26 + 14, ry)], fill=GREEN, width=6)
    fs = F_BODY(40)
    for x, lab, show in ((ax, a.get("a", "अयोध्या"), True), (bx, a.get("b", "जनकपुर"), p > 0.95)):
        if show:
            d.ellipse([x - 16, ry - 16, x + 16, ry + 16], fill=GREEN)
            d.text((x - fs.getlength(lab) / 2, ry + 22), lab, font=fs, fill=INK)
    x = x0 + 260 + (x1 - x0 - 520) * (0.5 + 0.5 * math.sin(lt * 0.9 - 1.57))
    _train(d, x, ty, 0.78)


def ic_bullet(d, box, lt, a):
    x0, y0, x1, y1 = box
    cy = (y0 + y1) / 2 + 30
    for k in range(9):
        ph = (lt * 2.2 + k / 9) % 1
        ly = y0 + 50 + k * 30
        xa = x1 - (x1 - x0) * ph
        d.line([(xa, ly), (xa - 140, ly)], fill=GREEN_L if k % 2 else LINE, width=5)
    p = spring(lt / 0.8)
    _train(d, x0 - 200 + (360 + 0) * p, cy, 0.95, nose=True)
    lab = a.get("label", "")
    if lab and lt > 0.9:
        fs = F_BODY(40); w = fs.getlength(lab) + 40
        d.rounded_rectangle([x1 - w - 20, y0 + 20, x1 - 20, y0 + 84], 32, fill=GREEN)
        d.text((x1 - w, y0 + 24), lab, font=fs, fill=(255, 255, 255))


def ic_tanker(d, box, lt, a):
    x0, y0, x1, y1 = box
    wy = y1 - 80
    for k in range(3):
        pts = [(x, wy + k * 22 + 8 * math.sin(x / 50 + lt * 3 + k)) for x in range(int(x0 + 20), int(x1 - 20), 12)]
        d.line(pts, fill=GREEN if k == 0 else GREEN_L, width=5)
    bob = 6 * math.sin(lt * 2.4)
    hx = x0 + 300
    d.polygon([(hx - 220, wy - 70 + bob), (hx + 200, wy - 70 + bob), (hx + 160, wy + bob), (hx - 200, wy + bob)], outline=INK, fill=(255, 255, 255), width=6)
    d.rectangle([hx + 90, wy - 150 + bob, hx + 170, wy - 70 + bob], outline=INK, width=6)
    for k in range(3):
        d.rounded_rectangle([hx - 190 + k * 90, wy - 110 + bob, hx - 120 + k * 90, wy - 70 + bob], 10, outline=INK, width=5)
    # warning + counter
    pulse = 1 + 0.08 * math.sin(lt * 8)
    wx, wy2, s = x1 - 150, y0 + 130, 80 * pulse
    d.polygon([(wx, wy2 - s), (wx + s, wy2 + s * 0.75), (wx - s, wy2 + s * 0.75)], fill=(255, 70, 70))
    f = F_HEAD(90); d.text((wx - f.getlength("!") / 2, wy2 - s * 0.75), "!", font=f, fill=(255, 255, 255))
    n = int(float(a.get("count", 25)) * eo(lt / 1.6))
    t = f"{n}"; fb = F_HEAD(84)
    d.text((wx - fb.getlength(t) / 2, wy2 + 70), t, font=fb, fill=INK)


def ic_number(d, box, lt, a):
    x0, y0, x1, y1 = box
    t = a.get("text", "?"); f = fit_font(F_HEAD, t, 220, x1 - x0 - 80)
    k = spring(lt / 0.6)
    d.text(((x0 + x1) / 2 - f.getlength(t) / 2, y0 + 40 + 40 * (1 - k)), t, font=f, fill=GREEN)



def _bottle(d, cx, base, s, fill, outline=INK, w=5):
    d.rounded_rectangle([cx - 14 * s, base - 150 * s, cx + 14 * s, base - 128 * s], int(4 * s), fill=outline)
    d.rounded_rectangle([cx - 36 * s, base - 130 * s, cx + 36 * s, base], int(18 * s), fill=fill, outline=outline, width=w)
    d.rectangle([cx - 36 * s + w, base - 85 * s, cx + 36 * s - w, base - 55 * s], fill=(255, 255, 255))


def ic_bottles(d, box, lt, a):
    """Row of bottles, one (the failing batch) highlighted with a green bracket + tag."""
    x0, y0, x1, y1 = box
    n = int(a.get("n", 6)); hi = int(a.get("hi", 3))
    base = y1 - 70
    for i in range(n):
        cx = x0 + 70 + i * (x1 - x0 - 140) / (n - 1)
        k = spring((lt - 0.06 * i) / 0.45)
        if k <= 0.02: continue
        sel = i == hi and lt > 0.9
        _bottle(d, cx, base + 40 * (1 - k), 1.05, (255, 230, 230) if sel else (220, 240, 255), outline=(230, 60, 60) if sel else INK)
    if lt > 0.9:
        cx = x0 + 70 + hi * (x1 - x0 - 140) / (n - 1)
        k = spring((lt - 0.9) / 0.4); m = 30; ax, ay = 62 * (2 - k), 100 * (2 - k)
        cy = base - 75
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            x, y = cx + sx * ax, cy + sy * ay
            d.line([(x, y - sy * m), (x, y), (x - sx * m, y)], fill=GREEN, width=7)
    tag = a.get("tag", "")
    if tag and lt > 1.2:
        fs = F_BODY(42); w = fs.getlength(tag) + 44
        d.rounded_rectangle([(x0 + x1) / 2 - w / 2, y0 + 6, (x0 + x1) / 2 + w / 2, y0 + 72], 33, fill=INK)
        d.text(((x0 + x1) / 2 - fs.getlength(tag) / 2, y0 + 10), tag, font=fs, fill=(255, 255, 255))


def ic_meter(d, box, lt, a):
    """Gauge with a limit mark; needle sweeps to the value (turns red past the limit)."""
    x0, y0, x1, y1 = box
    val, lim, vmax = float(a.get("value", 12)), float(a.get("limit", 10)), float(a.get("max", 16))
    gx, gy, r = (x0 + x1) / 2, y1 - 40, 230
    d.arc([gx - r, gy - r, gx + r, gy + r], 180, 360, fill=LINE, width=36)
    d.arc([gx - r, gy - r, gx + r, gy + r], 180, 180 + 180 * lim / vmax, fill=GREEN_L, width=36)
    d.arc([gx - r, gy - r, gx + r, gy + r], 180 + 180 * lim / vmax, 360, fill=(255, 205, 205), width=36)
    la = math.pi + math.pi * lim / vmax
    d.line([(gx + (r - 40) * math.cos(la), gy + (r - 40) * math.sin(la)), (gx + (r + 34) * math.cos(la), gy + (r + 34) * math.sin(la))], fill=INK, width=6)
    fs = F_BODY(36); lt_ = a.get("limit_label", f"लिमिट {int(lim)}")
    d.text((gx + (r + 40) * math.cos(la) - fs.getlength(lt_) / 2 + 30, gy + (r + 40) * math.sin(la) - 50), lt_, font=fs, fill=INK)
    p = eo(lt / 1.3); v = val * p
    ang = math.pi + math.pi * v / vmax
    col = (230, 50, 50) if v > lim else INK
    d.line([(gx, gy), (gx + (r - 55) * math.cos(ang), gy + (r - 55) * math.sin(ang))], fill=col, width=9)
    d.ellipse([gx - 18, gy - 18, gx + 18, gy + 18], fill=col)
    f = F_HEAD(96); t = f"{v:.0f}"
    d.text((x0 + 30, y0 - 4), t, font=f, fill=col)
    u = a.get("unit", ""); fu = F_BODY(34)
    if u: d.text((x0 + 40 + f.getlength(t), y0 + 50), u, font=fu, fill=GRAY)


def ic_shield(d, box, lt, a):
    """Shield pops in, tick draws, optional pill label."""
    x0, y0, x1, y1 = box; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 - 10
    k = spring(lt / 0.55); s = 150 * k
    if s > 4:
        d.polygon([(cx, cy - s), (cx + s * 0.85, cy - s * 0.6), (cx + s * 0.75, cy + s * 0.35), (cx, cy + s), (cx - s * 0.75, cy + s * 0.35), (cx - s * 0.85, cy - s * 0.6)], fill=GREEN)
    q = eo((lt - 0.4) / 0.5)
    if q > 0:
        pts = [(cx - 60, cy), (cx - 15, cy + 45), (cx + 70, cy - 50)]
        seg = [(pts[0], pts[1], 0.4), (pts[1], pts[2], 0.6)]; acc = 0; drawn = [pts[0]]
        for (pa, pb, frac) in seg:
            u = clamp((q - acc) / frac); acc += frac
            if u > 0: drawn.append((pa[0] + (pb[0] - pa[0]) * u, pa[1] + (pb[1] - pa[1]) * u))
        d.line(drawn, fill=(255, 255, 255), width=18, joint="curve")
    for k2 in range(8):                                   # sparkle ring
        ph = (lt * 0.7 + k2 / 8) % 1; ang = k2 * math.pi / 4; rr = 190 + 30 * ph
        x, y = cx + rr * math.cos(ang), cy + rr * math.sin(ang) * 0.8
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=GREEN_L + (int(255 * (1 - ph)),))


def ic_bottleq(d, box, lt, a):
    """Hook art: big bottle with a pulsing red question mark (visible at frame 0)."""
    x0, y0, x1, y1 = box; cx = (x0 + x1) / 2 - 80
    _bottle(d, cx, y1 - 20, 2.6, (220, 240, 255))
    for k in range(5):
        ph = (lt * 0.8 + k / 5) % 1
        bx = cx - 40 + k * 20; by = y1 - 60 - 220 * ph
        d.ellipse([bx - 9, by - 9, bx + 9, by + 9], outline=(120, 180, 240, int(255 * (1 - ph))), width=3)
    pulse = 1 + 0.1 * math.sin(lt * 7)
    f = F_HEAD(int(300 * pulse)); q = "?"
    d.text((cx + 200 - f.getlength(q) / 2, y0 + 10 - 30 * (pulse - 1) * 10), q, font=f, fill=(230, 50, 50))


def _diya(d, cx, cy, s, lt, k=0):
    d.chord([cx - 70 * s, cy - 40 * s, cx + 70 * s, cy + 40 * s], 0, 180, fill=GREEN)
    d.ellipse([cx - 70 * s, cy - 10 * s, cx + 70 * s, cy + 10 * s], fill=GREEN_D)
    fl = 1 + 0.12 * math.sin(lt * 13 + k * 1.7)
    d.polygon([(cx - 15 * s, cy - 6 * s), (cx, cy - 6 * s - 70 * s * fl), (cx + 15 * s, cy - 6 * s)], fill=(255, 170, 0))
    d.polygon([(cx - 7 * s, cy - 8 * s), (cx, cy - 8 * s - 36 * s * fl), (cx + 7 * s, cy - 8 * s)], fill=(255, 238, 140))


def ic_diyas(d, box, lt, a):
    """Hook art: soft glow + row of flickering diyas (visible at frame 0)."""
    x0, y0, x1, y1 = box; cy = y1 - 160
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([x0 - 40, cy - 260, x1 + 40, cy + 120], fill=(255, 210, 120, int(110 + 30 * math.sin(lt * 3))))
    d._im.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)))
    for i, (dx, sc_) in enumerate(((-260, 0.9), (0, 1.35), (260, 0.9))):
        _diya(d, (x0 + x1) / 2 + dx, cy + (0 if i == 1 else 40), sc_, lt, i)
    for k in range(10):
        ph = (lt * 0.5 + k / 10) % 1; x = x0 + 40 + (k * 67) % (x1 - x0 - 80); y = cy - 80 - 300 * ph
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 190, 60, int(255 * (1 - ph))))


def ic_pin(d, box, lt, a):
    """Map pin drops on a place, label + year pill."""
    x0, y0, x1, y1 = box; cx = (x0 + x1) / 2
    base = y1 - 70
    d.ellipse([cx - 200, base - 26, cx + 200, base + 26], fill=LINE)
    for k in range(2):
        ph = (lt * 0.8 + k / 2) % 1; rr = 40 + 150 * ph
        d.ellipse([cx - rr, base - rr * 0.18, cx + rr, base + rr * 0.18], outline=GREEN + (int(255 * (1 - ph)),), width=4)
    p = spring(lt / 0.6); py = base - 260 * (1 - p)
    d.ellipse([cx - 70, py - 210, cx + 70, py - 70], fill=GREEN)
    d.polygon([(cx - 62, py - 115), (cx, py), (cx + 62, py - 115)], fill=GREEN)
    d.ellipse([cx - 28, py - 168, cx + 28, py - 112], fill=(255, 255, 255))
    lab = a.get("label", ""); fs = F_BODY(46)
    if lab and lt > 0.6:
        w = fs.getlength(lab) + 44
        d.rounded_rectangle([cx + 110, y0 + 30, cx + 110 + w, y0 + 100], 35, fill=INK)
        d.text((cx + 132, y0 + 34), lab, font=fs, fill=(255, 255, 255))
    yr = a.get("year", "")
    if yr:
        fy = F_HEAD(90); d.text((x0 + 20, y0 + 10), yr, font=fy, fill=GREEN)


def ic_circles(d, box, lt, a):
    """N circles in two rows; the first one lights up green with a bracket."""
    x0, y0, x1, y1 = box; n = int(a.get("n", 10)); cols = (n + 1) // 2
    hi = int(a.get("hi", 0))
    for i in range(n):
        r_, c_ = divmod(i, cols)
        cx = x0 + 80 + c_ * (x1 - x0 - 160) / (cols - 1); cy = y0 + 110 + r_ * 160
        k = spring((lt - 0.05 * i) / 0.4)
        if k <= 0.02: continue
        on = i == hi and lt > 0.8
        rr = 52 * k
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=GREEN if on else (255, 255, 255), outline=GREEN if on else INK, width=4)
        f = F_HEAD(int(56 * k)); t = str(i + 1)
        d.text((cx - f.getlength(t) / 2, cy - 44 * k), t, font=f, fill=(255, 255, 255) if on else INK)
        if on:
            q = spring((lt - 0.8) / 0.4); m = 22; ax = 78 * (2 - q)
            for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                x, y = cx + sx * ax, cy + sy * ax
                d.line([(x, y - sy * m), (x, y), (x - sx * m, y)], fill=GREEN, width=6)


def ic_word(d, box, lt, a):
    """Big serif green word with a soft glow pulse."""
    x0, y0, x1, y1 = box; t = a.get("text", "")
    f = fit_font(F_SERIF, t, 170, x1 - x0 - 60)
    k = spring(lt / 0.6)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gcx, gcy = (x0 + x1) / 2, (y0 + y1) / 2
    rr = 230 * (1 + 0.05 * math.sin(lt * 3))
    ImageDraw.Draw(g).ellipse([gcx - rr, gcy - rr * 0.55, gcx + rr, gcy + rr * 0.55], fill=GREEN_L + (110,))
    d._im.alpha_composite(g.filter(ImageFilter.GaussianBlur(40)))
    L = text_layer(t, f, GREEN)
    L = L.resize((max(1, int(L.width * (0.7 + 0.3 * k))), max(1, int(L.height * (0.7 + 0.3 * k)))), Image.LANCZOS)
    d._im.alpha_composite(_alpha(L, clamp(k * 1.3)), (int(gcx - L.width / 2), int(gcy - L.height / 2)))


def ic_plates(d, box, lt, a):
    """Row of plates filling in one by one, people dots seated behind (langar)."""
    x0, y0, x1, y1 = box; n = 6; cy = y1 - 120
    d.rounded_rectangle([x0 + 20, cy + 40, x1 - 20, cy + 70], 14, fill=(235, 225, 205))
    for i in range(n):
        cx = x0 + 70 + i * (x1 - x0 - 140) / (n - 1)
        k = spring((lt - 0.12 * i) / 0.45)
        if k <= 0.02: continue
        d.ellipse([cx - 22 * k, cy - 160 * k, cx + 22 * k, cy - 116 * k], fill=INK)
        d.rounded_rectangle([cx - 30 * k, cy - 112 * k, cx + 30 * k, cy - 40 * k], int(14 * k), fill=INK)
        d.ellipse([cx - 52 * k, cy - 20 * k, cx + 52 * k, cy + 30 * k], fill=(255, 255, 255), outline=INK, width=4)
        if lt > 0.6 + 0.12 * i:
            q = spring((lt - 0.6 - 0.12 * i) / 0.4)
            d.ellipse([cx - 30 * q, cy - 8 * q, cx + 6 * q, cy + 18 * q], fill=(255, 190, 60))
            d.ellipse([cx + 2 * q, cy - 6 * q, cx + 32 * q, cy + 16 * q], fill=GREEN)


def ic_counter(d, box, lt, a):
    """Big number counting up with a green progress ring."""
    x0, y0, x1, y1 = box; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    val = int(a.get("value", 557)); p = eo(lt / 1.4)
    r = 160
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=LINE, width=18)
    d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * p, fill=GREEN, width=18)
    t = str(int(round(val * p))) + a.get("suffix", ""); f = fit_font(F_HEAD, t, 130, 2 * r - 90)
    d.text((cx - f.getlength(t) / 2, cy - 100), t, font=f, fill=INK)

SILVER, SILVER_D = (214, 218, 224), (150, 156, 166)
def ic_coin(d, box, lt, a):
    """Silver coin spinning in (squash on x), value on face, optional price tag sliding in."""
    x0, y0, x1, y1 = box; cx, cy = (x0 + x1) / 2 - (60 if a.get("price") else 0), (y0 + y1) / 2 + 10
    r = 165; k = spring(lt / 0.7)
    sq = abs(math.cos(max(0.0, 1.2 - lt) * 4.5)) if lt < 1.2 else 1.0
    sq = max(0.08, sq) * (0.75 + 0.25 * k)
    rx = r * sq
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([cx - r - 30, cy - r - 30, cx + r + 30, cy + r + 30], fill=(255, 255, 255, int(150 + 60 * math.sin(lt * 3))))
    d._im.alpha_composite(g.filter(ImageFilter.GaussianBlur(30)))
    d.ellipse([cx - rx + 10, cy - r + 14, cx + rx + 10, cy + r + 14], fill=SILVER_D)
    d.ellipse([cx - rx, cy - r, cx + rx, cy + r], fill=SILVER, outline=SILVER_D, width=8)
    ph = (lt * 0.7) % 1
    if sq > 0.55 and ph < 0.4:
        sx = cx - rx + 2 * rx * ph / 0.4
        d.line([(sx - 30, cy - r * 0.7), (sx + 30, cy + r * 0.7)], fill=(255, 255, 255), width=14)
    if sq > 0.55:
        d.ellipse([cx - rx * 0.82, cy - r * 0.82, cx + rx * 0.82, cy + r * 0.82], outline=(255, 255, 255), width=5)
        t = a.get("text", "₹75"); f = fit_font(F_HEAD, t, 120, rx * 1.5)
        d.text((cx - f.getlength(t) / 2, cy - 95), t, font=f, fill=INK)
    pr = a.get("price")
    if pr and lt > 0.9:
        q = spring((lt - 0.9) / 0.45); fs = F_HEAD(64); w = fs.getlength(pr) + 60
        tx = x1 - w - 10 + 300 * (1 - q); ty = y0 + 40
        d.rounded_rectangle([tx, ty, tx + w, ty + 100], 22, fill=GREEN)
        d.ellipse([tx + 14, ty + 40, tx + 34, ty + 60], fill=(255, 255, 255))
        d.text((tx + 42, ty + 6), pr, font=fs, fill=(255, 255, 255))


def ic_jail(d, box, lt, a):
    """Old building behind jail bars; bars slide apart to reveal it, label pill."""
    x0, y0, x1, y1 = box; cx = (x0 + x1) / 2; base = y1 - 60
    # building
    bw, bh = 520, 230
    d.rectangle([cx - bw / 2, base - bh, cx + bw / 2, base], fill=(255, 255, 255), outline=INK, width=6)
    d.polygon([(cx - bw / 2 - 30, base - bh), (cx, base - bh - 110), (cx + bw / 2 + 30, base - bh)], fill=GREEN)
    for i in range(5):
        wx = cx - bw / 2 + 40 + i * (bw - 80) / 4
        d.rectangle([wx - 26, base - bh + 50, wx + 26, base - bh + 130], fill=GREEN_L, outline=INK, width=4)
    d.rectangle([cx - 40, base - 90, cx + 40, base], fill=INK)
    d.line([(x0 + 20, base), (x1 - 20, base)], fill=INK, width=6)
    # bars
    op = eo((lt - 0.5) / 0.7)
    n = 9
    for i in range(n):
        bx = x0 + 40 + i * (x1 - x0 - 80) / (n - 1)
        side = -1 if bx < cx else 1
        bx += side * op * 420
        if x0 + 10 < bx < x1 - 10:
            d.rounded_rectangle([bx - 9, y0 + 20, bx + 9, y1 - 20], 9, fill=(90, 90, 90))
    if op < 0.99:
        for yy in (y0 + 60, y1 - 60):
            d.rectangle([x0 + 20 - op * 420, yy - 8, cx - op * 420, yy + 8], fill=(90, 90, 90))
            d.rectangle([cx + op * 420, yy - 8, x1 - 20 + op * 420, yy + 8], fill=(90, 90, 90))
    lab = a.get("label", "")
    if lab and lt > 1.1:
        fs = F_BODY(44); w = fs.getlength(lab) + 44
        d.rounded_rectangle([x0 + 20, y0 + 20, x0 + 20 + w, y0 + 88], 34, fill=INK)
        d.text((x0 + 42, y0 + 22), lab, font=fs, fill=(255, 255, 255))


def ic_growbars(d, box, lt, a):
    """Bars grow; the highlighted one (label) is tallest and green."""
    x0, y0, x1, y1 = box; base = y1 - 80
    vals = a.get("vals", [0.42, 0.55, 0.38, 1.0, 0.5, 0.33]); hi = int(a.get("hi", 3))
    n = len(vals); bw = (x1 - x0 - 100) / n
    d.line([(x0 + 30, base), (x1 - 30, base)], fill=INK, width=5)
    for i, v in enumerate(vals):
        k = eo((lt - 0.08 * i) / 0.7)
        bx = x0 + 50 + i * bw; h = (base - y0 - 110) * v * k
        d.rounded_rectangle([bx + 10, base - h, bx + bw - 10, base], 14, fill=GREEN if i == hi else LINE)
        if i == hi and k > 0.9:
            lab = a.get("label", ""); fs = F_BODY(40)
            w = fs.getlength(lab) + 36; lx = bx + bw / 2 - w / 2
            d.rounded_rectangle([lx, base - h - 80, lx + w, base - h - 18], 30, fill=INK)
            d.text((lx + 18, base - h - 80), lab, font=fs, fill=(255, 255, 255))
            # crown-ish star
            sx, sy = bx + bw / 2, base - h - 115; rr = 26 * spring((lt - 0.8) / 0.4)
            pts = [(sx + rr * math.cos(math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else 0.45), sy - rr * math.sin(math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else 0.45)) for j in range(10)]
            d.polygon(pts, fill=GREEN)

ICONS = {"diyas": ic_diyas, "pin": ic_pin, "circles": ic_circles, "word": ic_word, "plates": ic_plates, "counter": ic_counter, "bottles": ic_bottles, "meter": ic_meter, "shield": ic_shield, "bottleq": ic_bottleq, "closed": ic_closed, "aqi": ic_aqi, "train": ic_train, "bullet": ic_bullet, "tanker": ic_tanker, "number": ic_number, "coin": ic_coin, "jail": ic_jail, "growbars": ic_growbars}


# ---------------------------------------------------------------- captions
captions = []
for sc, tm in zip(SCN, TS):
    words = sc["say"].split(); chunks, cur = [], []
    for w_ in words:
        cur.append(w_)
        if len(cur) >= 3 or w_.endswith((".", "?", ",", "!")):
            chunks.append(" ".join(cur)); cur = []
    if cur: chunks.append(" ".join(cur))
    tot = sum(len(c) + 2 for c in chunks); t = tm["start"]
    for c in chunks:
        du = tm["speech"] * (len(c) + 2) / tot
        captions.append((t, t + du, c)); t += du
F_CAP = F_BODY(62)


# ---------------------------------------------------------------- scenes
def header(base, d, idx, t):
    f = F_BODY(40); t1 = data.get("pill", "ख़बर का हिसाब")
    w = f.getlength(t1) + 50
    d.rounded_rectangle([540 - w / 2, 100, 540 + w / 2, 160], 30, fill=INK)
    d.text((540 - f.getlength(t1) / 2, 104), t1, font=f, fill=(255, 255, 255))
    # 5 segment progress
    n = NSTORY; seg = 120; gap = 16; x = 540 - (n * seg + (n - 1) * gap) / 2
    cur = SCN[idx].get("n", 0) if SCN[idx]["kind"] == "fact" else (n if SCN[idx]["kind"] == "cta" else 0)
    for i in range(n):
        d.rounded_rectangle([x, 190, x + seg, 200], 5, fill=LINE)
        if i + 1 < cur or SCN[idx]["kind"] == "cta":
            d.rounded_rectangle([x, 190, x + seg, 200], 5, fill=GREEN)
        elif i + 1 == cur:
            tm = TS[idx]; p = clamp((t - tm["start"]) / max(0.5, tm["end"] - tm["start"]))
            d.rounded_rectangle([x, 190, x + max(10, seg * p), 200], 5, fill=GREEN)
        x += seg + gap


def scene_hook(base, sc, lt, t):
    d = ImageDraw.Draw(base)
    if sc.get("icon") in ICONS:
        d._im = base
        ICONS[sc["icon"]](d, (200, 300, 880, 920), lt, sc.get("icon_args", {}))
        return _hook_text(base, sc, lt)
    cx, cy, r = 540, 640, 300
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=GREEN, width=8)
    d.arc([cx - r, cy - r, cx + r, cy + r], 340, 560, fill=LINE, width=4)
    for k in range(60):
        a = k * math.pi / 30
        r0 = r - (34 if k % 5 == 0 else 18)
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + (r - 6) * math.cos(a), cy + (r - 6) * math.sin(a))],
               fill=INK if k % 5 == 0 else (190, 190, 190), width=4 if k % 5 == 0 else 2)
    # needle: snaps tick by tick (fast)
    ticks = int(lt * 6)
    frac = (lt * 6) % 1
    ang = -math.pi / 2 + (ticks + spring(frac / 0.4) - 1 + 1) * (2 * math.pi / 60) * 3
    tip = (cx + (r - 50) * math.cos(ang), cy + (r - 50) * math.sin(ang))
    tail = (cx - 60 * math.cos(ang), cy - 60 * math.sin(ang))
    nx, ny = -math.sin(ang) * 14, math.cos(ang) * 14
    d.polygon([tail, (cx + nx, cy + ny), tip, (cx - nx, cy - ny)], fill=INK)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=GREEN)
    _hook_text(base, sc, lt)


def _hook_text(base, sc, lt):
    # text: fully visible at frame 0 (punch-in only)
    punch = 1.0 + 0.08 * (1 - eo(lt / 0.35))
    big = sc["big"]
    if sc.get("big2"):
        l1, l2 = big, sc["big2"]
    else:
        parts = big.split(" ", 2)
        l1 = " ".join(parts[:2]) if len(parts) > 2 else big
        l2 = parts[2] if len(parts) > 2 else ""
    f1 = fit_font(F_HEAD, l1, 120, 900)
    paste(base, text_layer(l1, f1, INK), 540, 975, scale=punch)
    if l2:
        f2 = fit_font(F_SERIF, l2, 150, 960)
        g = blob(160, 90); base.alpha_composite(g, (540 - g.width // 2, 1235 - g.height // 2))
        paste(base, text_layer(l2, f2, GREEN), 540, 1150, scale=punch)
    if sc.get("sub"):
        fs = fit_font(F_BODY, sc["sub"], 54, 900)
        paste(base, text_layer(sc["sub"], fs, GRAY), 540, 1390)


def scene_story(base, sc, lt, t, dur):
    d = ImageDraw.Draw(base)
    # hexagon badge + progress ring
    k = spring(lt / 0.5)
    cx, cy = 540, 360
    if k > 0.02:
        d.arc([cx - 110, cy - 110, cx + 110, cy + 110], -90, -90 + 360 * clamp(lt / max(1, dur)), fill=GREEN_L, width=8)
        hexagon(d, cx, cy, 82 * k, GREEN, rot=(1 - k) * 0.8)
        if k > 0.5:
            f = F_HEAD(110); n = str(sc.get("n", ""))
            d.text((cx - f.getlength(n) / 2, cy - 82), n, font=f, fill=(255, 255, 255))
    # headline (word by word) + green italic line
    fh = fit_font(F_HEAD, sc["big"], 132, 960)
    words_in(base, sc["big"], fh, INK, 540, 480, lt, delay=0.1)
    if sc.get("unit"):
        fu = fit_font(F_SERIF, sc["unit"], 92, 960)
        p = spring((lt - 0.35) / 0.55)
        if p > 0.02:
            paste(base, text_layer(sc["unit"], fu, GREEN), 540, 650, alpha=clamp(p * 1.3), dx=-80 * (1 - p))
            # hand-drawn underline stroke
            w = fu.getlength(sc["unit"]); q = eo((lt - 0.6) / 0.5)
            if q > 0:
                x0 = 540 - w / 2
                pts = [(x0 + w * u * q, 772 + 6 * math.sin(u * 9)) for u in [i / 30 for i in range(31)]]
                d.line(pts, fill=GREEN, width=7, joint="curve")
    # illustration card
    box = (150, 830, 930, 1230)
    kc = spring((lt - 0.2) / 0.55)
    if kc > 0.02:
        card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shadow_card(card, *box)
        cd = ImageDraw.Draw(card); cd._im = card
        ic = ICONS.get(sc.get("icon", ""), None)
        if ic:
            ic(cd, (box[0] + 20, box[1] + 20, box[2] - 20, box[3] - 20), max(0, lt - 0.2), sc.get("icon_args", {}))
        sc_ = 0.9 + 0.1 * clamp(kc)
        card = card.resize((int(W * sc_), int(H * sc_)), Image.LANCZOS) if sc_ < 0.999 else card
        ox = (W - card.width) / 2; oy = (box[1] + box[3]) / 2 * (1 - sc_)
        base.alpha_composite(_alpha(card, clamp(kc * 1.2)), (int(ox), int(oy + 60 * (1 - kc))))
    # pills
    pills = [p.strip() for p in sc.get("sub", "").split("•") if p.strip()]
    y = 1270
    for i, p_ in enumerate(pills[:3]):
        kp = spring((lt - 0.7 - 0.18 * i) / 0.5)
        if kp <= 0.02: continue
        fp = fit_font(F_BODY, p_, 48, 900)
        w = fp.getlength(p_) + 64
        solid = i % 2 == 0
        side = -1 if i % 2 == 0 else 1
        x = 540 - w / 2 + side * 500 * (1 - kp)
        L = Image.new("RGBA", (int(w) + 8, 92), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        if solid:
            ld.rounded_rectangle([2, 2, w + 2, 84], 42, fill=GREEN)
            ld.text((34, 10), p_, font=fp, fill=(255, 255, 255))
        else:
            ld.rounded_rectangle([2, 2, w + 2, 84], 42, fill=(255, 255, 255), outline=INK, width=3)
            ld.text((34, 10), p_, font=fp, fill=INK)
        base.alpha_composite(_alpha(L, clamp(kp * 1.3)), (int(x), int(y)))
        y += 100


def scene_cta(base, sc, lt, t):
    d = ImageDraw.Draw(base)
    big = sc["big"]; f = fit_font(F_HEAD, big, 120, 760)
    words_in(base, big, f, INK, 540, 420, lt)
    w = f.getlength(big); q = eo((lt - 0.5) / 0.7)
    if q > 0:
        d.arc([540 - w / 2 - 95, 385, 540 + w / 2 + 95, 640], 200, 200 + 330 * q, fill=GREEN, width=8)
    if not sc.get("choices", 0):
        k = spring((lt - 0.2) / 0.5); cx, cy = 540, 860
        if k > 0.02:
            w2, h2 = 300 * k, 190 * k
            d.rounded_rectangle([cx - w2, cy - h2, cx + w2, cy + h2], int(60 * k), fill=GREEN)
            d.polygon([(cx - 120 * k, cy + h2 - 4), (cx - 190 * k, cy + h2 + 90 * k), (cx - 40 * k, cy + h2 - 4)], fill=GREEN)
            for i in range(3):
                b = 1 + 0.35 * max(0, math.sin(lt * 6 - i * 0.9))
                r = 26 * k * b
                d.ellipse([cx - 110 + i * 110 - r, cy - r, cx - 110 + i * 110 + r, cy + r], fill=(255, 255, 255))
        _cta_tail(base, d, sc, lt)
        return
    # number circles + snapping bracket
    xs = [140 + i * 200 for i in range(5)]; cy = 860
    for i, x in enumerate(xs):
        k = spring((lt - 0.2 - 0.1 * i) / 0.45)
        if k <= 0.02: continue
        r = 70 * k
        sel = int(lt / 0.8) % 5 == i
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=GREEN if sel else (255, 255, 255), outline=INK if not sel else GREEN, width=4)
        fn = F_HEAD(int(90 * k))
        d.text((x - fn.getlength(str(i + 1)) / 2, cy - 70 * k), str(i + 1), font=fn, fill=(255, 255, 255) if sel else INK)
    si = int(lt / 0.8) % 5; bx = xs[si]; a = 105; m = 30
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        x, y = bx + sx * a, cy + sy * a
        d.line([(x, y - sy * m), (x, y), (x - sx * m, y)], fill=GREEN, width=7)
    _cta_tail(base, d, sc, lt)


def _cta_tail(base, d, sc, lt):
    if sc.get("sub"):
        fs = fit_font(F_SERIF, sc["sub"], 80, 960)
        paste(base, text_layer(sc["sub"], fs, GREEN), 540, 1130, alpha=clamp((lt - 0.5) / 0.4))
    fb = F_BODY(46); t2 = "फॉलो करो • " + data.get("pill", "ख़बर का हिसाब")
    if lt > 1.0:
        w = fb.getlength(t2) + 60
        d.rounded_rectangle([540 - w / 2, 1290, 540 + w / 2, 1370], 40, fill=INK)
        d.text((540 - fb.getlength(t2) / 2, 1296), t2, font=fb, fill=(255, 255, 255))


# ---------------------------------------------------------------- frame
def frame(t):
    im = background(t)
    idx = 0
    for i, s in enumerate(TS):
        if t >= s["start"] - 0.05: idx = i
    sc, tm = SCN[idx], TS[idx]
    lt = t - tm["start"]; dur = tm["end"] - tm["start"]
    nxt = TS[idx + 1]["start"] if idx + 1 < len(TS) else TOTAL + 1
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if sc["kind"] == "hook": scene_hook(layer, sc, max(0, lt), t)
    elif sc["kind"] == "cta": scene_cta(layer, sc, max(0, lt), t)
    else: scene_story(layer, sc, max(0, lt), t, dur)
    out_p = clamp((nxt - t) / 0.18) if idx + 1 < len(TS) else 1.0     # quick slide-up exit before next scene
    if out_p < 1:
        layer = _alpha(layer, out_p)
        im.alpha_composite(layer, (0, int(-60 * (1 - out_p))))
    else:
        im.alpha_composite(layer)
    d = ImageDraw.Draw(im)
    brackets(d, t)
    header(im, d, idx, t)
    # caption
    for (c0, c1, c) in captions:
        if c0 <= t < c1:
            f = fit_font(F_BODY, c, 62, 920)
            w = f.getlength(c); y = 1580
            k = spring((t - c0) / 0.25)
            d.rounded_rectangle([540 - w / 2 - 28, y - 6, 540 + w / 2 + 28, y + 84], 20, fill=(255, 255, 255, 235), outline=LINE, width=2)
            d.text((540 - w / 2, y + 6 + 8 * (1 - k)), c, font=f, fill=INK)
            d.rectangle([540 - w / 2, y + 74, 540 - w / 2 + w * clamp((t - c0) / max(0.2, c1 - c0)), y + 80], fill=GREEN)
            break
    return im.convert("RGB")


# ---------------------------------------------------------------- encode (+ sfx under voice)
VOICE = os.path.join(os.path.dirname(os.path.abspath(script)), data.get("audio", "voice.wav"))
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", VOICE]
if any(s.get("sfx") for s in SCN):
    sys.path.insert(0, HERE)
    import sfx as SFX
    track = SFX.make_track(SCN, TS, tim["total"], os.path.join(build, "sfx_track.wav"))
    vol = data.get("fx_volume", 0.35)
    cmd += ["-i", track, "-filter_complex",
            "[1:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[v];"
            f"[2:a]volume={vol}[s];[v][s]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,apad[a]",
            "-map", "0:v", "-map", "[a]", "-shortest"]
else:
    cmd += ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11,apad", "-shortest"]
cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-ar", "48000", "-movflags", "+faststart", out]

if os.environ.get("PREVIEW"):
    ts = [float(x) for x in os.environ["PREVIEW"].split(",")]
    tiles = [frame(x).resize((270, 480)) for x in ts]
    sh = Image.new("RGB", (270 * min(6, len(tiles)), 480 * ((len(tiles) + 5) // 6)), (0, 0, 0))
    for i, tl in enumerate(tiles): sh.paste(tl, ((i % 6) * 270, (i // 6) * 480))
    sh.save(os.path.join(build, "preview_clean.png")); print("preview"); sys.exit(0)

p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
n = int(TOTAL * FPS)
for i in range(n):
    p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); rc = p.wait()
print(f"wrote {out} frames={n} dur={n / FPS:.1f}s rc={rc}")
