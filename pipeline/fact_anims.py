"""Per-scene illustrations for Shorts, drawn in code (no third-party art).

Each animation lives in a band under the scene text (y ~ 1490-1770), which is clear of the captions above it
and mostly above the YouTube title overlay. Set "anim": "<name>" on a scene in scene.json.

  clock     analogue clock spinning to a time + calendar page dropping in   (args: time "18:25", day "21", month "NOV")
  bicycle   bicycle carrying a rocket nose cone, bullock cart with the body behind it
  church    church facade with lit windows and a radio dish sending waves
  altitude  small rocket climbing across the band, then an orange cloud blooming
  flag      waving Indian tricolour on a pole
  planets   Moon and Mars, each with an orbiting spacecraft
"""
import math
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
BY0, BY1 = 1490, 1770
CY = (BY0 + BY1) // 2


def _ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def _back(x):
    x = max(0.0, min(1.0, x)); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def _nose(d, x, y, w, h, fill, point="up"):
    pts = []
    for k in range(21):
        a = k / 20
        dy = a * h
        hw = w / 2 * math.sqrt(a)
        pts.append((x + hw, y + dy) if point == "up" else (x + dy, y + hw))
    for k in range(20, -1, -1):
        a = k / 20
        dy = a * h
        hw = w / 2 * math.sqrt(a)
        pts.append((x - hw, y + dy) if point == "up" else (x + dy, y - hw))
    d.polygon(pts, fill=fill)


def _wheel(d, cx, cy, r, ang, col=(235, 235, 245), spokes=8, width=6):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=width)
    for k in range(spokes):
        a = ang + k * math.pi / spokes * 2
        d.line([cx, cy, cx + r * math.cos(a), cy + r * math.sin(a)], fill=col + (170,) if len(col) == 3 else col, width=2)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=col)


# ---------------------------------------------------------------- clock + calendar
def clock(L, lt, dur, fonts, args):
    d = ImageDraw.Draw(L, "RGBA")
    hh, mm = (int(v) for v in args.get("time", "18:25").split(":"))
    s = _back(lt / 0.5)
    # clock
    cx, cy, r = 360, CY, 110 * s
    if r > 2:
        d.ellipse([cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10], fill=(255, 196, 0))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 248, 240))
        for k in range(12):
            a = k * math.pi / 6
            d.line([cx + 0.8 * r * math.sin(a), cy - 0.8 * r * math.cos(a), cx + 0.92 * r * math.sin(a), cy - 0.92 * r * math.cos(a)],
                   fill=(40, 40, 60), width=5)
        # hands spin forward and settle on the time
        p = _ease((lt - 0.2) / 1.6)
        tot_min = (hh % 12) * 60 + mm
        cur = tot_min - (1 - p) * 720          # spins through 12 hours, then lands
        am = (cur % 60) / 60 * 2 * math.pi
        ah = (cur / 720) * 2 * math.pi
        d.line([cx, cy, cx + 0.5 * r * math.sin(ah), cy - 0.5 * r * math.cos(ah)], fill=(30, 30, 50), width=12)
        d.line([cx, cy, cx + 0.78 * r * math.sin(am), cy - 0.78 * r * math.cos(am)], fill=(230, 50, 70), width=7)
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(30, 30, 50))
    # calendar page drops in with a bounce
    dy = -260 * (1 - _back((lt - 0.35) / 0.55))
    if lt > 0.35:
        x0, y0 = 600, CY - 120 + dy
        d.rounded_rectangle([x0, y0, x0 + 220, y0 + 240], 18, fill=(250, 248, 240))
        d.rounded_rectangle([x0, y0, x0 + 220, y0 + 70], 18, fill=(230, 50, 70))
        d.rectangle([x0, y0 + 50, x0 + 220, y0 + 70], fill=(230, 50, 70))
        for rx in (x0 + 55, x0 + 165):
            d.ellipse([rx - 9, y0 - 14, rx + 9, y0 + 4], fill=(60, 60, 80))
        f_m, f_d = fonts["small"], fonts["mid"]
        m = args.get("month", "NOV")
        d.text((x0 + 110 - d.textlength(m, font=f_m) / 2, y0 + 4), m, font=f_m, fill=(255, 255, 255))
        day = args.get("day", "21")
        d.text((x0 + 110 - d.textlength(day, font=f_d) / 2, y0 + 60), day, font=f_d, fill=(30, 30, 50))


# ---------------------------------------------------------------- bicycle + bullock cart
def _bicycle(d, x, y, ang, t):
    col = (235, 235, 245)
    r = 50
    bx, fx = x - 85, x + 85
    _wheel(d, bx, y, r, ang); _wheel(d, fx, y, r, ang)
    # frame
    seat = (x - 25, y - 85); crank = (x, y); head = (x + 60, y - 90)
    d.line([(bx, y), crank, seat, (bx, y)], fill=(255, 196, 0), width=7)
    d.line([crank, head, seat], fill=(255, 196, 0), width=7)
    d.line([head, (fx, y)], fill=(255, 196, 0), width=7)
    d.line([head, (head[0] + 10, head[1] - 25), (head[0] + 35, head[1] - 25)], fill=col, width=6)
    # pedals
    pa = ang * 0.6
    for sgn in (1, -1):
        d.line([crank, (crank[0] + sgn * 22 * math.cos(pa), crank[1] + sgn * 22 * math.sin(pa))], fill=col, width=5)
    # rider (simple stick figure, pushing pedals)
    hip = (seat[0], seat[1] - 10)
    sh = (x + 15, y - 175)
    d.line([hip, sh], fill=col, width=10)
    d.line([sh, (head[0] + 30, head[1] - 22)], fill=col, width=8)
    d.ellipse([sh[0] - 4, sh[1] - 62, sh[0] + 46, sh[1] - 12], fill=col)
    foot = (crank[0] + 22 * math.cos(pa), crank[1] + 22 * math.sin(pa))
    knee = ((hip[0] + foot[0]) / 2 + 25, (hip[1] + foot[1]) / 2 - 20)
    d.line([hip, knee, foot], fill=col, width=9)
    # rocket nose cone strapped on the rear carrier, pointing back
    d.rectangle([bx - 10, y - 75, x - 30, y - 68], fill=col)
    _nose(d, bx - 110, y - 100, 64, 150, (230, 50, 70), point="side")
    d.line([(bx - 25, y - 100), (bx - 25, y - 70)], fill=(60, 60, 80), width=5)


def _cart(d, x, y, ang, t):
    col = (235, 235, 245)
    # bullock (flat, stylised) walking on the right
    ox = x + 170
    bob = 4 * math.sin(t * 8)
    d.rounded_rectangle([ox - 70, y - 120 + bob, ox + 70, y - 55 + bob], 30, fill=(205, 205, 215))
    d.ellipse([ox + 50, y - 150 + bob, ox + 105, y - 95 + bob], fill=(205, 205, 215))
    d.line([(ox + 60, y - 145 + bob), (ox + 50, y - 175 + bob)], fill=col, width=6)
    d.line([(ox + 95, y - 145 + bob), (ox + 108, y - 175 + bob)], fill=col, width=6)
    d.ellipse([ox + 82, y - 132 + bob, ox + 90, y - 124 + bob], fill=(30, 30, 50))
    for k, lx in enumerate((ox - 50, ox - 25, ox + 30, ox + 55)):
        sw = 14 * math.sin(t * 8 + k * math.pi / 2)
        d.line([(lx, y - 60 + bob), (lx + sw, y + 15)], fill=(205, 205, 215), width=11)
    # yoke
    d.line([(x + 40, y - 70), (ox - 60, y - 90 + bob)], fill=(150, 110, 70), width=8)
    # cart with a big wooden wheel carrying the rocket body
    d.rectangle([x - 110, y - 75, x + 60, y - 55], fill=(150, 110, 70))
    _wheel(d, x - 25, y - 15, 62, ang * 0.8, col=(170, 125, 80), spokes=6, width=10)
    d.rounded_rectangle([x - 140, y - 135, x + 50, y - 78], 10, fill=(244, 244, 250))
    d.rectangle([x - 60, y - 135, x - 40, y - 78], fill=(255, 153, 51))
    d.rectangle([x - 40, y - 135, x - 20, y - 78], fill=(19, 136, 8))


def bicycle(L, lt, dur, fonts, args):
    d = ImageDraw.Draw(L, "RGBA")
    y = BY1 - 70
    d.line([(0, y + 52), (W, y + 52)], fill=(255, 255, 255, 60), width=4)
    for k in range(12):                                     # road dashes sliding left
        rx = (k * 120 - lt * 260) % (W + 120) - 60
        d.line([(rx, y + 70), (rx + 50, y + 70)], fill=(255, 255, 255, 45), width=4)
    speed = (W + 900) / max(dur, 3.5)
    x = -260 + speed * lt
    _bicycle(d, x, y, lt * 9, lt)
    _cart(d, x - 520, y, lt * 7, lt)


# ---------------------------------------------------------------- church = control room
def church(L, lt, dur, fonts, args):
    """Drawn on a full-size layer, then scaled to 0.64 around the base so the cross stays below the captions."""
    T = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    _church(T, lt)
    k = 0.64
    T = T.resize((int(W * k), int(H * k)), Image.LANCZOS)
    ax, ay = 540, BY1 + 5                                   # anchor: base centre of the scene
    L.alpha_composite(T, (int(ax - 540 * k), int(ay - BY1 * k)))


def _church(L, lt):
    d = ImageDraw.Draw(L, "RGBA")
    rise = 300 * (1 - _ease(lt / 0.6))
    base = BY1 - 20 + rise
    cx = 440
    wall = (236, 232, 222)
    d.rectangle([cx - 210, base - 170, cx + 210, base], fill=wall)
    d.polygon([(cx - 230, base - 170), (cx, base - 255), (cx + 230, base - 170)], fill=(200, 70, 60))
    # tower + cross
    d.rectangle([cx - 45, base - 330, cx + 45, base - 170], fill=wall)
    d.polygon([(cx - 55, base - 330), (cx, base - 385), (cx + 55, base - 330)], fill=(200, 70, 60))
    d.rectangle([cx - 4, base - 430, cx + 4, base - 380], fill=(255, 196, 0))
    d.rectangle([cx - 18, base - 418, cx + 18, base - 410], fill=(255, 196, 0))
    # door + windows (lit, blinking like control desks)
    d.rounded_rectangle([cx - 35, base - 100, cx + 35, base], 30, fill=(90, 60, 40))
    for i, wx in enumerate((cx - 150, cx - 90, cx + 90, cx + 150)):
        on = math.sin(lt * 7 + i * 1.7) > -0.3
        d.rounded_rectangle([wx - 20, base - 140, wx + 20, base - 80], 18, fill=(255, 210, 80) if on else (120, 110, 90))
    # radio dish on the right, sending waves
    dx, dy = cx + 330, base - 60
    d.line([(dx, base), (dx, dy)], fill=(200, 200, 215), width=10)
    d.pieslice([dx - 80, dy - 110, dx + 80, dy + 50], 200, 340, fill=(220, 222, 235))
    d.line([(dx, dy - 30), (dx + 30, dy - 90)], fill=(200, 200, 215), width=5)
    for k in range(3):
        ph = ((lt * 0.9 + k / 3) % 1.0)
        rr = 40 + 160 * ph
        a = int(220 * (1 - ph))
        d.arc([dx + 30 - rr, dy - 90 - rr, dx + 30 + rr, dy - 90 + rr], 250, 330, fill=(120, 220, 255, a), width=6)


# ---------------------------------------------------------------- altitude + orange cloud
def altitude(L, lt, dur, fonts, args, sprite=None):
    d = ImageDraw.Draw(L, "RGBA")
    p = _ease(lt / 1.8)
    # orange sodium-vapour cloud blooming after the climb
    if lt > 1.3:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        q = _ease((lt - 1.3) / 1.6)
        for (ox, oy, rr) in ((800, CY - 40, 120), (720, CY - 10, 90), (880, CY + 10, 85), (790, CY + 30, 100)):
            r = rr * (0.3 + 0.9 * q) * (1 + 0.04 * math.sin(lt * 2 + ox))
            gd.ellipse([ox - r * 1.3, oy - r, ox + r * 1.3, oy + r], fill=(255, 140, 30, int(170 * q)))
        L.alpha_composite(g.filter(ImageFilter.GaussianBlur(28)))
        d = ImageDraw.Draw(L, "RGBA")
    # climb path: lower-left to upper-right of the band
    x0, y0, x1, y1 = 140, BY1 - 10, 780, BY0 + 40
    pts = [(x0 + (x1 - x0) * k / 40, y0 - (y0 - y1) * (k / 40) ** 0.6) for k in range(41)]
    n = int(40 * p)
    if n > 1:
        d.line(pts[:n + 1], fill=(255, 255, 255, 110), width=6)
    x, y = pts[min(40, n)]
    if sprite is not None and lt < 2.2:
        k2 = min(40, n + 1); nx, ny = pts[k2]
        ang = math.degrees(math.atan2(-(ny - y), nx - x)) - 90 if (nx, ny) != (x, y) else 45 - 90
        sp = sprite.resize((sprite.width // 3, sprite.height // 3), Image.LANCZOS).rotate(ang, expand=True, resample=Image.BICUBIC)
        L.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))
    # altitude scale on the left
    d.line([(70, BY0), (70, BY1)], fill=(255, 255, 255, 90), width=4)
    for k in range(5):
        yy = BY1 - k * (BY1 - BY0) / 4
        d.line([(60, yy), (80, yy)], fill=(255, 255, 255, 120), width=3)
    yy = BY1 - (BY1 - BY0) * p
    d.polygon([(85, yy), (105, yy - 12), (105, yy + 12)], fill=(255, 196, 0))


# ---------------------------------------------------------------- waving tricolour
def flag(L, lt, dur, fonts, args):
    d = ImageDraw.Draw(L, "RGBA")
    px, top = 330, BY0 + 10
    rise = _ease(lt / 0.8)
    fw, fh = 390, 250
    ftop = BY1 - fh - 20 - (BY1 - fh - 20 - top) * rise
    d.rectangle([px - 8, top - 10, px + 8, BY1 + 10], fill=(200, 200, 215))
    d.ellipse([px - 14, top - 26, px + 14, top + 2], fill=(255, 196, 0))
    cols = ((255, 153, 51), (255, 255, 255), (19, 136, 8))
    strips = 48
    sw = fw / strips
    for i in range(strips):
        u = i / strips
        off = 16 * u * math.sin(u * 7 - lt * 6)
        shade = 0.88 + 0.12 * math.cos(u * 7 - lt * 6)
        x = px + 8 + i * sw
        for j, c in enumerate(cols):
            c2 = tuple(int(v * shade) for v in c)
            d.rectangle([x, ftop + off + j * fh / 3, x + sw + 1, ftop + off + (j + 1) * fh / 3], fill=c2)
    # Ashoka chakra (navy wheel) riding the wave
    u = 0.5
    off = 16 * u * math.sin(u * 7 - lt * 6)
    ccx, ccy, r = px + 8 + fw / 2, ftop + off + fh / 2, fh / 6 - 4
    d.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], outline=(0, 0, 128), width=4)
    for k in range(24):
        a = k * math.pi / 12
        d.line([ccx, ccy, ccx + r * math.cos(a), ccy + r * math.sin(a)], fill=(0, 0, 128), width=1)
    # sparkles
    for k in range(10):
        ph = (lt * 0.7 + k * 0.137) % 1.0
        sx = 780 + 220 * math.sin(k * 2.3) * 0.6
        sy = BY1 - 40 - ph * 240
        a = int(255 * math.sin(ph * math.pi))
        rr = 5 + 4 * math.sin(ph * math.pi)
        d.polygon([(sx, sy - rr * 2), (sx + rr * 0.6, sy), (sx, sy + rr * 2), (sx - rr * 0.6, sy)], fill=(255, 220, 90, a))
        d.polygon([(sx - rr * 2, sy), (sx, sy + rr * 0.6), (sx + rr * 2, sy), (sx, sy - rr * 0.6)], fill=(255, 220, 90, a))


# ---------------------------------------------------------------- Moon vs Mars
def planets(L, lt, dur, fonts, args):
    d = ImageDraw.Draw(L, "RGBA")
    s = _back(lt / 0.6)
    for (cx, base, craters, label) in ((300, (200, 200, 210), (95, 95, 110), "moon"), (780, (215, 95, 50), (160, 60, 35), "mars")):
        cy = CY + 8 * math.sin(lt * 2 + cx)
        r = 105 * s
        if r < 3:
            continue
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([cx - r - 25, cy - r - 25, cx + r + 25, cy + r + 25], fill=base + (90,))
        L.alpha_composite(glow.filter(ImageFilter.GaussianBlur(20)))
        d = ImageDraw.Draw(L, "RGBA")
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=base)
        for (fx, fy, fr) in ((-0.35, -0.3, 0.22), (0.3, 0.1, 0.16), (-0.1, 0.45, 0.13), (0.45, -0.4, 0.1)):
            d.ellipse([cx + fx * r - fr * r, cy + fy * r - fr * r, cx + fx * r + fr * r, cy + fy * r + fr * r], fill=craters)
        # orbiting spacecraft
        a = lt * 1.8 + (0 if label == "moon" else math.pi)
        ox, oy = cx + 1.45 * r * math.cos(a), cy + 0.45 * r * math.sin(a)
        d.arc([cx - 1.45 * r, cy - 0.45 * r, cx + 1.45 * r, cy + 0.45 * r], 0, 360, fill=(255, 255, 255, 70), width=2)
        if True:
            d.rectangle([ox - 9, oy - 7, ox + 9, oy + 7], fill=(255, 196, 0))
            d.rectangle([ox - 26, oy - 4, ox - 11, oy + 4], fill=(80, 160, 255))
            d.rectangle([ox + 11, oy - 4, ox + 26, oy + 4], fill=(80, 160, 255))
    # "VS" pulse in the middle
    f = fonts["mid"]
    sc = 1 + 0.08 * math.sin(lt * 6)
    txt = args.get("vs", "VS")
    tl = Image.new("RGBA", (220, 160), (0, 0, 0, 0))
    td = ImageDraw.Draw(tl)
    td.text((110 - td.textlength(txt, font=f) / 2, 10), txt, font=f, fill=(255, 70, 140), stroke_width=6, stroke_fill=(20, 10, 30))
    tl = tl.resize((int(220 * sc * s), int(160 * sc * s)), Image.LANCZOS) if s > 0.05 else tl
    L.alpha_composite(tl, (int(540 - tl.width / 2), int(CY - tl.height / 2)))


ANIMS = {"clock": clock, "bicycle": bicycle, "church": church, "altitude": altitude, "flag": flag, "planets": planets}


def draw(im, name, lt, dur, alpha, fonts, args=None, sprite=None):
    """Composite animation `name` onto RGB image im at scene-local time lt; returns a new RGB image."""
    fn = ANIMS.get(name)
    if fn is None or alpha <= 0:
        return im
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if name == "altitude":
        fn(L, lt, dur, fonts, args or {}, sprite=sprite)
    else:
        fn(L, lt, dur, fonts, args or {})
    a = max(0.0, min(1.0, alpha)) * (1.0 if (name in ("leaders", "office", "candlecrash") or (args or {}).get("instant")) else _ease(lt / 0.25))   # hook visuals: visible at frame 0
    if a < 1:
        L.putalpha(L.getchannel("A").point(lambda v: int(v * a)))
    out = im.convert("RGBA")
    out.alpha_composite(L)
    return out.convert("RGB")


# ================================================================ geopolitics set (reuses long_visuals drawings)
def _lv():
    import long_visuals as LV
    return LV


def _ctx(size=44):
    from PIL import ImageFont
    import os as _os
    f = ImageFont.truetype(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "fonts", "Mukta-Bold.ttf"), size)
    LV = _lv()
    def text(t, font, fill, alpha=1.0, stroke=0):
        bb = font.getbbox(t); L = Image.new("RGBA", (bb[2] - bb[0] + 40, bb[3] - bb[1] + 40), (0, 0, 0, 0))
        ImageDraw.Draw(L).text((20 - bb[0], 20 - bb[1]), t, font=font, fill=fill + (int(255 * alpha),))
        return L
    return {"f_small": f, "f_sub": f, "f_mid": f, "text": text, "put": lambda *a, **k: None, "fit": lambda *a: 1.0}


def _boxed(L, name, lt, size=340, cy=CY + 5):
    LV = _lv()
    T = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
    LV.side_anim(T, name, lt, 1.0, 210, 210, _ctx())
    T = T.resize((size, size), Image.LANCZOS)
    L.alpha_composite(T, (int(540 - size / 2), int(cy - size / 2)))


def pin(L, lt, dur, fonts, args): _boxed(L, "pin", lt)
def treaty(L, lt, dur, fonts, args): _boxed(L, "treaty", lt)
def stamp(L, lt, dur, fonts, args): _boxed(L, "cross", lt)


def missiles(L, lt, dur, fonts, args):
    LV = _lv(); d = ImageDraw.Draw(L, "RGBA")
    rows = args.get("rows", [("us", 5000), ("ru", 5000), ("cn", 620)])
    for k, (code, val) in enumerate(rows):
        y = BY0 + 45 + k * 92
        fl = LV.flag(code, 84, 56); L.alpha_composite(fl, (70, int(y - 28)))
        n = val / 250; shown = n * _ease((lt - 0.2 - 0.25 * k) / 1.3)
        col = (255, 120, 90) if code != "cn" else (255, 196, 0)
        for j in range(int(math.ceil(n))):
            fr = max(0.0, min(1.0, shown - j))
            if fr <= 0: break
            LV._missile(d, 190 + j * 40, y + 6, 1.25 * _back(fr), col)


def hormuz(L, lt, dur, fonts, args):
    LV = _lv()
    C = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)); dc = ImageDraw.Draw(C, "RGBA")
    LV.r_hormuz(C, dc, {"blocked": args.get("blocked", True)}, lt, 1.0, _ctx(58))
    C = C.crop((250, 240, 1670, 820))
    h = 290; w = int(C.width * h / C.height)
    C = C.resize((w, h), Image.LANCZOS)
    L.alpha_composite(C, (int(540 - w / 2), BY0 - 10))


def leaders(L, lt, dur, fonts, args):
    """Hook: three flag discs with the user's cutout photos, fully visible from frame 0 (quick pop-in only)."""
    import os as _os
    LV = _lv()
    who = args.get("who", ["us", "cn", "ru"]); base = args.get("_base", ".")
    r, cy = 150, 1160
    for k, key in enumerate(who):
        cx = 540 + (k - (len(who) - 1) / 2) * 330
        p = _os.path.join(base, args.get("dir", "people"), f"{key}.png")
        ph = Image.open(p).convert("RGBA") if _os.path.exists(p) else None
        pop = 0.9 + 0.1 * _back(lt / 0.35)
        rr = int(r * pop * (1.08 if k == 1 else 1.0))
        T = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        LV.leader_card(T, cx, cy, rr, key, {}, ph, lt, 1.0, k == 1, {"mid": None, "sub": _ctx(40)["f_small"], "small": _ctx(30)["f_small"]})
        # leader_card draws an empty name plate when no name is given: cut everything below the disc
        T = T.crop((0, 0, 1080, cy + rr + 12))
        L.alpha_composite(T)


def longthumb(L, lt, dur, fonts, args):
    import os as _os
    p = _os.path.join(args.get("_base", "."), args["img"])
    if not _os.path.exists(p): return
    th = Image.open(p).convert("RGBA")
    s = 0.6 + 0.4 * _back(lt / 0.5)
    w = int(520 * s * (1 + 0.03 * math.sin(lt * 5))); h = int(w * 9 / 16)
    th = th.resize((w, h), Image.LANCZOS)
    d = ImageDraw.Draw(L, "RGBA")
    x0, y0 = 540 - w // 2, CY - h // 2 - 10
    d.rounded_rectangle([x0 - 8, y0 - 8, x0 + w + 8, y0 + h + 8], 18, fill=(255, 255, 255))
    L.alpha_composite(th, (x0, y0))
    pr = 46 * s
    d.ellipse([540 - pr, CY - 10 - pr, 540 + pr, CY - 10 + pr], fill=(230, 30, 40, 235))
    d.polygon([(540 - pr * 0.35, CY - 10 - pr * 0.5), (540 - pr * 0.35, CY - 10 + pr * 0.5), (540 + pr * 0.55, CY - 10)], fill=(255, 255, 255))


ANIMS.update({"pin": pin, "treaty": treaty, "stamp": stamp, "missiles": missiles, "hormuz": hormuz,
              "leaders": leaders, "longthumb": longthumb})


# ================================================================ cricket set
def scoreboard(L, lt, dur, fonts, args):
    """Dark scoreboard whose runs tick up to the target, wickets and 'DECLARED' stamp."""
    d = ImageDraw.Draw(L, "RGBA")
    runs, wk = int(args.get("runs", 720)), int(args.get("wkts", 9))
    x0, y0, x1, y1 = 240, BY0 + 10, 840, BY1 - 20
    d.rounded_rectangle([x0 - 10, y0 - 10, x1 + 10, y1 + 10], 22, fill=(255, 196, 0))
    d.rounded_rectangle([x0, y0, x1, y1], 16, fill=(18, 40, 28))
    p = 1.0 if args.get("instant") else _ease(lt / 1.6)
    cur = int(runs * p)
    f = fonts["mid"]
    t = f"{cur}/{min(wk, int(wk * p + 0.5))}"
    d.text((540 - d.textlength(t, font=f) / 2, y0 + 30), t, font=f, fill=(255, 235, 120))
    lab = args.get("label", "INDIA")
    fs = fonts["small"]
    if lt <= 1.7 or not args.get("stamp", "DECLARED"):
        d.text((540 - d.textlength(lab, font=fs) / 2, y0 + 175), lab, font=fs, fill=(200, 230, 210))
    if lt > 1.7 and args.get("stamp", "DECLARED"):
        k = _back((lt - 1.7) / 0.35)
        st = Image.new("RGBA", (420, 110), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([4, 4, 416, 106], 14, outline=(230, 40, 50), width=8)
        tt = args.get("stamp", "DECLARED")
        sd.text((210 - sd.textlength(tt, font=fs) / 2, 26), tt, font=fs, fill=(230, 40, 50))
        st = st.resize((max(1, int(320 * k)), max(1, int(84 * k))), Image.LANCZOS).rotate(-4, expand=True, resample=Image.BICUBIC)
        L.alpha_composite(st, (int(540 - st.width / 2), int(y0 + 212 - st.height / 2)))


def _bat(d, x, y, ang, s=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    def P(px, py): return (x + px * ca - py * sa, y + px * sa + py * ca)
    d.polygon([P(-7 * s, 0), P(7 * s, 0), P(7 * s, 60 * s), P(-7 * s, 60 * s)], fill=(30, 30, 40))      # handle
    d.polygon([P(-22 * s, 60 * s), P(22 * s, 60 * s), P(20 * s, 220 * s), P(0, 232 * s), P(-20 * s, 220 * s)], fill=(235, 205, 150))
    d.line([P(0, 75 * s), P(0, 215 * s)], fill=(210, 175, 120), width=3)


def _ball(d, x, y, r=18):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 30, 40))
    d.arc([x - r * 0.6, y - r, x + r * 0.6, y + r], 70, 290, fill=(255, 235, 235), width=2)


def six(L, lt, dur, fonts, args):
    """Bat swings, ball arcs over a boundary rope; a SIX counter ticks up to n."""
    d = ImageDraw.Draw(L, "RGBA")
    n = int(args.get("n", 6))
    period = max(0.6, min(1.1, (dur - 0.5) / max(1, n)))
    k = min(n, int(lt / period) + 1)
    ph = (lt % period) / period
    # boundary rope (arc) + grass
    d.arc([520, BY0 + 60, 1240, BY1 + 380], 185, 265, fill=(255, 255, 255, 180), width=8)
    d.rectangle([60, BY1 - 18, 1020, BY1 - 8], fill=(60, 150, 70, 160))
    bx, by = 230, BY1 - 40
    swing = -1.9 + 2.6 * _ease(min(1, ph / 0.25))
    _bat(d, bx, by - 180, swing, 0.85)
    if ph > 0.2:
        u = (ph - 0.2) / 0.8
        x = bx + 60 + 720 * u
        y = by - 120 - 300 * math.sin(math.pi * min(1, u * 0.9))
        for j in range(1, 6):
            uu = max(0, u - j * 0.03)
            tx = bx + 60 + 720 * uu; ty = by - 120 - 300 * math.sin(math.pi * min(1, uu * 0.9))
            d.ellipse([tx - 10 + j, ty - 10 + j, tx + 10 - j, ty + 10 - j], fill=(255, 200, 60, 140 - j * 22))
        _ball(d, x, y)
    f = fonts["small"]
    t = f"6 x {k}"
    d.rounded_rectangle([780, BY0 - 5, 1010, BY0 + 75], 20, fill=(255, 196, 0))
    d.text((895 - d.textlength(t, font=f) / 2, BY0 + 4), t, font=f, fill=(20, 15, 30))


def stumps(L, lt, dur, fonts, args):
    """Ball zips in, stumps and bails fly. Repeats twice (both innings)."""
    d = ImageDraw.Draw(L, "RGBA")
    reps = int(args.get("reps", 2))
    period = max(1.4, (dur - 0.3) / reps)
    ph = (lt % period) / period
    base = BY1 - 15
    hit = 0.35
    for i, sx in enumerate((500, 540, 580)):
        if ph < hit:
            ang, ox, oy = 0, 0, 0
        else:
            u = (ph - hit) / (1 - hit)
            ang = (0.5 + 0.35 * (i - 1)) * _ease(u * 1.5) * (1 if i else -0.4)
            ox, oy = 30 * (i - 1) * u, 0
        ca, sa = math.cos(ang), math.sin(ang)
        h = 230
        top = (sx + ox + h * sa, base - h * ca)
        d.line([(sx + ox, base), top], fill=(245, 230, 200), width=16)
    # bails
    if ph < hit:
        d.rectangle([494, base - 238, 586, base - 228], fill=(230, 200, 140))
    else:
        u = (ph - hit) / (1 - hit)
        for j, dx in enumerate((-1, 1)):
            x = 540 + dx * (40 + 260 * u); y = base - 235 - 300 * u + 520 * u * u
            ang = u * 9 * dx
            ln = 46
            d.line([(x - ln / 2 * math.cos(ang), y - ln / 2 * math.sin(ang)), (x + ln / 2 * math.cos(ang), y + ln / 2 * math.sin(ang))],
                   fill=(230, 200, 140), width=10)
        for k in range(10):
            a = k * math.pi / 5
            r = 60 + 140 * u
            d.line([(540 + r * 0.6 * math.cos(a), base - 140 + r * 0.6 * math.sin(a)), (540 + r * math.cos(a), base - 140 + r * math.sin(a))],
                   fill=(255, 196, 0, int(255 * (1 - u))), width=6)
    if ph < hit:
        u = ph / hit
        _ball(d, 120 + 420 * u, base - 60 - 180 * (1 - u) * u * 4 * 0.25, 20)
    f = fonts["small"]
    t = args.get("label", "0  &  0")
    d.text((820 - d.textlength(t, font=f) / 2, BY0 + 30), t, font=f, fill=(255, 90, 90))


def batcount(L, lt, dur, fonts, args):
    """Bat with runs counter ticking up (e.g. 78 off 79)."""
    d = ImageDraw.Draw(L, "RGBA")
    ang = -0.5 + 0.25 * math.sin(lt * 4)
    _bat(d, 330, BY0 + 10, ang, 1.05)
    f = fonts["mid"]; fs = fonts["small"]
    runs = int(args.get("runs", 78)); balls = int(args.get("balls", 79))
    p = _ease(lt / 1.4)
    t = str(int(runs * p))
    d.text((720 - d.textlength(t, font=f) / 2, BY0 + 10), t, font=f, fill=(255, 196, 0))
    s = f"({int(balls * p)} गेंद)"
    d.text((720 - d.textlength(s, font=fs) / 2, BY0 + 170), s, font=fs, fill=(255, 255, 255))


def trophy(L, lt, dur, fonts, args):
    """Trophy rising with a 1 vs ? series board and calendar for the next Test."""
    d = ImageDraw.Draw(L, "RGBA")
    k = _back(lt / 0.6)
    cx, base = 380, BY1 - 10
    s = k
    d.rectangle([cx - 70 * s, base - 30 * s, cx + 70 * s, base], fill=(140, 95, 55))
    d.rectangle([cx - 18 * s, base - 90 * s, cx + 18 * s, base - 30 * s], fill=(255, 196, 0))
    d.pieslice([cx - 95 * s, base - 260 * s, cx + 95 * s, base - 70 * s], 0, 180, fill=(255, 196, 0))
    d.rectangle([cx - 95 * s, base - 170 * s, cx + 95 * s, base - 165 * s], fill=(255, 196, 0))
    for sgn in (-1, 1):
        d.arc([cx + sgn * 95 * s - 40 * s, base - 230 * s, cx + sgn * 95 * s + 40 * s, base - 150 * s],
              90 if sgn > 0 else 270, 270 if sgn > 0 else 90, fill=(255, 196, 0), width=int(10 * s) + 1)
    for j in range(6):
        ph = (lt * 0.8 + j / 6) % 1
        a = j * 1.1
        r = 130 + 60 * ph
        d.ellipse([cx + r * math.cos(a) - 5, base - 170 + r * math.sin(a) * 0.6 - 5, cx + r * math.cos(a) + 5, base - 170 + r * math.sin(a) * 0.6 + 5],
                  fill=(255, 240, 150, int(255 * (1 - ph))))
    if lt > 0.4:
        dy = -200 * (1 - _back((lt - 0.4) / 0.5))
        x0, y0 = 640, BY0 + 20 + dy
        d.rounded_rectangle([x0, y0, x0 + 220, y0 + 240], 18, fill=(250, 248, 240))
        d.rounded_rectangle([x0, y0, x0 + 220, y0 + 70], 18, fill=(230, 50, 70))
        d.rectangle([x0, y0 + 50, x0 + 220, y0 + 70], fill=(230, 50, 70))
        fm, fd = fonts["small"], fonts["mid"]
        m = args.get("month", "NOV"); day = args.get("day", "27")
        d.text((x0 + 110 - d.textlength(m, font=fm) / 2, y0 + 4), m, font=fm, fill=(255, 255, 255))
        d.text((x0 + 110 - d.textlength(day, font=fd) / 2, y0 + 60), day, font=fd, fill=(30, 30, 50))


def poll(L, lt, dur, fonts, args):
    """Two buttons (HAAN / NA) with bars filling and a tapping finger on HAAN."""
    d = ImageDraw.Draw(L, "RGBA")
    f = fonts["small"]
    for i, (lab, col, pct) in enumerate(((args.get("a", "हाँ"), (60, 190, 110), 0.7), (args.get("b", "ना"), (220, 70, 70), 0.3))):
        y = BY0 + 30 + i * 125
        d.rounded_rectangle([200, y, 880, y + 95], 47, fill=(255, 255, 255, 40))
        w = 680 * pct * _ease((lt - 0.2 * i) / 1.2)
        if w > 95:
            d.rounded_rectangle([200, y, 200 + w, y + 95], 47, fill=col + (230,))
        d.text((240, y + 14), lab, font=f, fill=(255, 255, 255))
    tp = (lt % 1.2) / 1.2
    fx, fy = 760, BY0 + 105 + (10 if tp < 0.2 else 0)
    d.ellipse([fx - 26, fy - 26, fx + 26, fy + 26], fill=(255, 220, 180))
    d.rounded_rectangle([fx - 22, fy, fx + 22, fy + 90], 18, fill=(255, 220, 180))
    if tp < 0.3:
        r = 40 + 80 * tp / 0.3
        d.ellipse([fx - r, fy - 26 - r * 0.2, fx + r, fy - 26 + r * 0.2 * 2], outline=(255, 255, 255, int(200 * (1 - tp / 0.3))), width=4)


ANIMS.update({"scoreboard": scoreboard, "six": six, "stumps": stumps, "batcount": batcount, "trophy": trophy, "poll": poll})


# ================================================================ politics / social-media set
def _person(d, x, y, s, col, sign=None, t=0.0, k=0):
    bob = 6 * math.sin(t * 7 + k)
    d.ellipse([x - 16 * s, y - 120 * s + bob, x + 16 * s, y - 88 * s + bob], fill=col)
    d.rounded_rectangle([x - 20 * s, y - 86 * s + bob, x + 20 * s, y - 20 * s + bob], 10, fill=col)
    d.line([(x - 10 * s, y - 20 * s + bob), (x - 12 * s, y)], fill=col, width=int(9 * s))
    d.line([(x + 10 * s, y - 20 * s + bob), (x + 12 * s, y)], fill=col, width=int(9 * s))
    if sign:
        up = 10 * math.sin(t * 8 + k * 1.3)
        d.line([(x + 18 * s, y - 70 * s + bob), (x + 30 * s, y - 150 * s + up)], fill=(150, 110, 70), width=5)
        d.rectangle([x - 5 * s, y - 200 * s + up, x + 70 * s, y - 145 * s + up], fill=sign)


def office(L, lt, dur, fonts, args):
    """Glass office building with a crowd waving placards in front (visible from frame 0)."""
    d = ImageDraw.Draw(L, "RGBA")
    bx0, bx1, top, base = 340, 740, BY0 - 40, BY1 - 10
    d.rectangle([bx0, top, bx1, base], fill=(60, 90, 130))
    for r in range(6):
        for c in range(6):
            on = (r * 3 + c + int(lt * 3)) % 7 != 0
            x = bx0 + 22 + c * 63; y = top + 18 + r * 42
            d.rectangle([x, y, x + 44, y + 28], fill=(150, 200, 240) if on else (90, 120, 160))
    d.rectangle([bx0 + 160, base - 60, bx1 - 160, base], fill=(30, 40, 60))
    for k in range(9):
        x = 150 + k * 100
        if bx0 + 30 < x < bx1 - 30 and k % 2 == 0:
            continue
        _person(d, x, base + 5, 0.9, (235, 235, 245), sign=((255, 255, 255) if k % 3 else (230, 50, 60)), t=lt, k=k)


def citypins(L, lt, dur, fonts, args):
    """Three city pins dropping one after another, labels under each, badge at the end."""
    d = ImageDraw.Draw(L, "RGBA")
    cities = args.get("cities", ["हैदराबाद", "मुंबई", "गुरुग्राम"])
    f = fonts["small"]
    for i, name in enumerate(cities):
        x = 230 + i * 310
        p = _back((lt - 0.35 * i) / 0.5)
        if p <= 0:
            continue
        y = BY0 + 150 - 220 * (1 - p)
        d.ellipse([x - 45, y - 140, x + 45, y - 50], fill=(230, 50, 70))
        d.polygon([(x - 40, y - 80), (x, y), (x + 40, y - 80)], fill=(230, 50, 70))
        d.ellipse([x - 18, y - 113, x + 18, y - 77], fill=(255, 255, 255))
        d.text((x - d.textlength(name, font=f) / 2, BY0 + 165), name, font=f, fill=(255, 255, 255))
    if lt > 1.3 and args.get("badge"):
        k = _back((lt - 1.3) / 0.4)
        t = args["badge"]
        w = d.textlength(t, font=f) + 50
        d.rounded_rectangle([540 - w / 2 * k, BY1 - 55, 540 + w / 2 * k, BY1 + 15], 30, fill=(255, 196, 0))
        if k > 0.9:
            d.text((540 - d.textlength(t, font=f) / 2, BY1 - 52), t, font=f, fill=(20, 15, 30))


def phoneflip(L, lt, dur, fonts, args):
    """Generic phone (no brand): profile with 'removed' banner, then flips to 'restored'."""
    d = ImageDraw.Draw(L, "RGBA")
    f = fonts["small"]
    flip = max(1.4, dur * 0.55)
    for j, x in enumerate((370, 710)):
        restored = lt > flip + 0.15 * j
        sq = abs(math.cos(min(1, max(0, (lt - flip - 0.15 * j) / 0.4)) * math.pi)) if lt > flip + 0.15 * j - 0.2 and lt < flip + 0.15 * j + 0.4 else 1
        w = max(14, 120 * sq)
        d.rounded_rectangle([x - w, BY0 - 10, x + w, BY1 + 10], 26, fill=(25, 25, 35))
        d.rounded_rectangle([x - w + 10, BY0 + 5, x + w - 10, BY1 - 5], 18, fill=(245, 245, 250))
        if sq > 0.5:
            d.ellipse([x - 40, BY0 + 30, x + 40, BY0 + 110], fill=(200, 200, 215))
            d.ellipse([x - 16, BY0 + 42, x + 16, BY0 + 74], fill=(150, 150, 170))
            d.rounded_rectangle([x - 30, BY0 + 76, x + 30, BY0 + 106], 14, fill=(150, 150, 170))
            col = (60, 180, 110) if restored else (220, 50, 60)
            lab = args.get("ok", "वापस आया") if restored else args.get("bad", "हटाया गया")
            d.rounded_rectangle([x - 100, BY0 + 140, x + 100, BY0 + 200], 14, fill=col)
            d.text((x - d.textlength(lab, font=f) / 2, BY0 + 142), lab, font=f, fill=(255, 255, 255))
            for r in range(2):
                d.rectangle([x - 90, BY0 + 220 + r * 18, x + 60 - r * 40, BY0 + 230 + r * 18], fill=(210, 210, 220))


def lockwall(L, lt, dur, fonts, args):
    """Grid of profile icons, padlocks snapping on one by one."""
    d = ImageDraw.Draw(L, "RGBA")
    cols, rows = 9, 3
    n = cols * rows
    shown = n * _ease(lt / 1.8)
    for i in range(n):
        r, c = divmod(i, cols)
        x = 140 + c * 100; y = BY0 + 40 + r * 90
        d.ellipse([x - 32, y - 32, x + 32, y + 32], fill=(90, 90, 120))
        d.ellipse([x - 11, y - 20, x + 11, y + 2], fill=(170, 170, 200))
        d.pieslice([x - 20, y + 2, x + 20, y + 40], 180, 360, fill=(170, 170, 200))
        if i < shown:
            k = _back(min(1, shown - i))
            lx, ly = x + 18, y + 14
            d.arc([lx - 11 * k, ly - 22 * k, lx + 11 * k, ly], 180, 360, fill=(255, 196, 0), width=5)
            d.rounded_rectangle([lx - 15 * k, ly - 9 * k, lx + 15 * k, ly + 13 * k], 4, fill=(255, 196, 0))


def splitsides(L, lt, dur, fonts, args):
    """Two panels sliding in from left and right with labels and a VS badge."""
    d = ImageDraw.Draw(L, "RGBA")
    f = fonts["small"]
    p = _ease(lt / 0.5)
    A, B = args.get("a", "आरोप"), args.get("b", "जवाब")
    ca, cb = tuple(args.get("ca", (40, 120, 220))), tuple(args.get("cb", (255, 140, 40)))
    w = 430
    xa = -w + (90 + w) * p; xb = W - (90 + w) * p
    d.rounded_rectangle([xa, BY0 + 20, xa + w, BY1 - 20], 26, fill=ca + (230,))
    d.rounded_rectangle([xb, BY0 + 20, xb + w, BY1 - 20], 26, fill=cb + (230,))
    d.text((xa + w / 2 - d.textlength(A, font=f) / 2, BY0 + 50), A, font=f, fill=(255, 255, 255))
    d.text((xb + w / 2 - d.textlength(B, font=f) / 2, BY0 + 50), B, font=f, fill=(255, 255, 255))
    # megaphone / shield icons
    mx, my = xa + w / 2, BY0 + 170
    d.polygon([(mx - 60, my - 22), (mx + 20, my - 60), (mx + 20, my + 60), (mx - 60, my + 22)], fill=(255, 255, 255))
    for k in range(3):
        ph = (lt * 1.2 + k / 3) % 1
        d.arc([mx + 10 - 30 * ph - 20, my - 40 - 40 * ph, mx + 50 + 40 * ph, my + 40 + 40 * ph], 300, 60, fill=(255, 255, 255, int(255 * (1 - ph))), width=5)
    sx, sy = xb + w / 2, BY0 + 170
    d.polygon([(sx - 55, sy - 60), (sx + 55, sy - 60), (sx + 55, sy), (sx, sy + 65), (sx - 55, sy)], fill=(255, 255, 255))
    d.text((sx - d.textlength("§", font=f) / 2, sy - 45), "§", font=f, fill=cb)
    if p > 0.95:
        r = 52 * (1 + 0.08 * math.sin(lt * 6))
        d.ellipse([540 - r, CY - r, 540 + r, CY + r], fill=(20, 15, 30), outline=(255, 196, 0), width=5)
        d.text((540 - d.textlength("VS", font=f) / 2, CY - 30), "VS", font=f, fill=(255, 196, 0))


def growbars(L, lt, dur, fonts, args):
    """Two bars: tiny 'before' bar, then a huge 'after' bar shooting up with a counter."""
    d = ImageDraw.Draw(L, "RGBA")
    f = fonts["small"]
    items = args.get("items", [["2025", 0.013, "~70 हज़ार"], ["2026 (6 महीने)", 1.0, "54 लाख+"]])
    hmax = BY1 - BY0 - 70
    for i, (lab, frac, val) in enumerate(items):
        x = 330 + i * 400
        p = _ease((lt - 0.2 - 0.6 * i) / 1.2)
        h = max(6, hmax * frac * p)
        col = (120, 130, 170) if i == 0 else (230, 50, 60)
        d.rounded_rectangle([x - 70, BY1 - 40 - h, x + 70, BY1 - 40], 10, fill=col)
        d.text((x - d.textlength(lab, font=f) / 2, BY1 - 35), lab, font=f, fill=(200, 196, 215))
        if p > 0.3:
            vy = BY1 - 40 - h - 55
            d.text((x - d.textlength(val, font=f) / 2, vy), val, font=f, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))


ANIMS.update({"office": office, "citypins": citypins, "phoneflip": phoneflip, "lockwall": lockwall,
              "splitsides": splitsides, "growbars": growbars})


# ================================================================ markets set
RED_C, GRN_C = (235, 60, 70), (60, 200, 120)


def _arrow_down(d, x, y, s, col):
    d.rectangle([x - 12 * s, y - 50 * s, x + 12 * s, y + 5 * s], fill=col)
    d.polygon([(x - 32 * s, y), (x + 32 * s, y), (x, y + 40 * s)], fill=col)


def candlecrash(L, lt, dur, fonts, args):
    """Candlestick chart: a few green candles then a run of red ones crashing; visible at frame 0."""
    d = ImageDraw.Draw(L, "RGBA")
    d.line([(90, BY1), (990, BY1)], fill=(255, 255, 255, 70), width=3)
    seq = [(0.55, 0.62), (0.62, 0.70), (0.70, 0.78), (0.78, 0.74), (0.74, 0.60), (0.60, 0.45), (0.45, 0.30), (0.30, 0.12)]
    n = 3 + int(min(5, (lt / 0.25)))
    for i, (o, c) in enumerate(seq[:n]):
        x = 150 + i * 105
        y = lambda v: BY1 - 10 - v * (BY1 - BY0 - 30)
        col = GRN_C if c > o else RED_C
        hi, lo = max(o, c) + 0.05, min(o, c) - 0.05
        d.line([(x, y(hi)), (x, y(lo))], fill=col, width=4)
        top, bot = y(max(o, c)), y(min(o, c))
        d.rectangle([x - 28, top, x + 28, max(bot, top + 6)], fill=col)
    if n >= 8:
        p = (lt % 0.8) / 0.8
        _arrow_down(d, 960, BY0 + 80 + 30 * p, 1.4, RED_C)


def ticker(L, lt, dur, fonts, args):
    """Index board counting down from a start value to the close, with a red change pill."""
    d = ImageDraw.Draw(L, "RGBA")
    a, b = float(args.get("from", 83919.71)), float(args.get("to", 82435.99))
    p = _ease(lt / 1.8)
    v = a + (b - a) * p
    x0, x1, y0, y1 = 170, 910, BY0 + 10, BY1 - 20
    d.rounded_rectangle([x0, y0, x1, y1], 24, fill=(20, 22, 34), outline=(255, 255, 255, 60), width=3)
    f, fs = fonts["mid"], fonts["small"]
    lab = args.get("label", "SENSEX")
    d.text((x0 + 40, y0 + 22), lab, font=fs, fill=(200, 196, 215))
    t = f"{v:,.0f}"
    d.text((x0 + 40, y0 + 80), t, font=f, fill=RED_C if p > 0.05 else (255, 255, 255))
    ch = args.get("change", "−1,484  (−1.77%)")
    if p > 0.6:
        w = d.textlength(ch, font=fs) + 40
        d.rounded_rectangle([x1 - w - 30, y0 + 20, x1 - 30, y0 + 80], 30, fill=RED_C)
        d.text((x1 - w - 10, y0 + 22), ch, font=fs, fill=(255, 255, 255))
    _arrow_down(d, x1 - 90, y1 - 90 + 10 * math.sin(lt * 6), 1.2, RED_C)


def linecrash(L, lt, dur, fonts, args):
    """Intraday line: rises to the day's high (marked), then plunges; dashed open line for reference."""
    d = ImageDraw.Draw(L, "RGBA")
    pts_v = [0.45, 0.55, 0.72, 0.85, 0.80, 0.70, 0.55, 0.40, 0.28, 0.18, 0.12]
    X = lambda i: 120 + i * 84
    Y = lambda v: BY1 - 10 - v * (BY1 - BY0 - 40)
    for k in range(0, 900, 30):
        d.line([(120 + k, Y(0.45)), (135 + k, Y(0.45))], fill=(255, 255, 255, 80), width=3)
    prog = _ease(lt / 2.2) * (len(pts_v) - 1)
    pts = []
    for i in range(len(pts_v)):
        if i <= prog:
            pts.append((X(i), Y(pts_v[i])))
        else:
            fr = prog - (i - 1)
            if fr > 0:
                pts.append((X(i - 1) + (X(i) - X(i - 1)) * fr, Y(pts_v[i - 1] + (pts_v[i] - pts_v[i - 1]) * fr)))
            break
    for i in range(len(pts) - 1):
        col = GRN_C if pts[i + 1][1] <= pts[i][1] else RED_C
        d.line([pts[i], pts[i + 1]], fill=col, width=9)
    if len(pts) > 0:
        x, y = pts[-1]; d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(255, 255, 255))
    if prog >= 3:
        hx, hy = X(3), Y(0.85)
        f = fonts["small"]
        t = args.get("high", "HIGH 84,663")
        d.rounded_rectangle([hx - 10, hy - 75, hx + d.textlength(t, font=f) + 20, hy - 15], 14, fill=(60, 200, 120, 230))
        d.text((hx + 5, hy - 73), t, font=f, fill=(255, 255, 255))


def moneybag(L, lt, dur, fonts, args):
    """Money bag with notes flying out and the bag shrinking; label below."""
    d = ImageDraw.Draw(L, "RGBA")
    s = 1.0 - 0.35 * _ease(lt / 2.5)
    cx, cy = 420, CY + 10
    d.ellipse([cx - 120 * s, cy - 90 * s, cx + 120 * s, cy + 130 * s], fill=(200, 150, 60))
    d.polygon([(cx - 40 * s, cy - 85 * s), (cx + 40 * s, cy - 85 * s), (cx + 60 * s, cy - 140 * s), (cx - 60 * s, cy - 140 * s)], fill=(200, 150, 60))
    d.rectangle([cx - 45 * s, cy - 95 * s, cx + 45 * s, cy - 80 * s], fill=(120, 80, 30))
    f = fonts["mid"]
    d.text((cx - d.textlength("₹", font=f) / 2, cy - 60 * s), "₹", font=f, fill=(255, 240, 180))
    for k in range(7):
        ph = (lt * 0.9 + k / 7) % 1
        x = cx + 80 + 420 * ph; y = cy - 100 - 120 * math.sin(ph * math.pi) + 60 * ph
        ang = ph * 6 + k
        w, h = 70, 36
        pts = [(x + w / 2 * math.cos(ang) * sx - h / 2 * math.sin(ang) * sy, y + w / 2 * math.sin(ang) * sx + h / 2 * math.cos(ang) * sy)
               for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        d.polygon(pts, fill=(110, 190, 110, int(255 * (1 - ph))))
    t = args.get("label", "₹3 लाख करोड़+")
    fs = fonts["small"]
    d.rounded_rectangle([640, BY1 - 75, 640 + d.textlength(t, font=fs) + 40, BY1 - 15], 28, fill=RED_C)
    d.text((660, BY1 - 73), t, font=fs, fill=(255, 255, 255))


def sectordown(L, lt, dur, fonts, args):
    """Bank building and a steel I-beam, each with a red down arrow and % label."""
    d = ImageDraw.Draw(L, "RGBA")
    f = fonts["small"]
    p = _back(lt / 0.5)
    # bank
    bx, base = 330, BY1 - 20
    d.polygon([(bx - 150 * p, base - 190 * p), (bx, base - 260 * p), (bx + 150 * p, base - 190 * p)], fill=(230, 230, 240))
    for k in range(5):
        x = bx - 120 * p + k * 60 * p
        d.rectangle([x - 12 * p, base - 180 * p, x + 12 * p, base - 30 * p], fill=(230, 230, 240))
    d.rectangle([bx - 160 * p, base - 30 * p, bx + 160 * p, base], fill=(230, 230, 240))
    # steel beam
    sx = 760
    d.rectangle([sx - 140 * p, base - 200 * p, sx + 140 * p, base - 175 * p], fill=(160, 170, 185))
    d.rectangle([sx - 18 * p, base - 175 * p, sx + 18 * p, base - 55 * p], fill=(160, 170, 185))
    d.rectangle([sx - 140 * p, base - 55 * p, sx + 140 * p, base - 30 * p], fill=(160, 170, 185))
    for x in (bx, sx):
        y = BY0 + 20 + 14 * math.sin(lt * 5)
        if lt > 0.5:
            _arrow_down(d, x + 150, y + 60, 1.0, RED_C)
    for x, t in ((bx, args.get("a", "बैंक")), (sx, args.get("b", "मेटल"))):
        d.text((x - d.textlength(t, font=f) / 2, base - 5), t, font=f, fill=(255, 255, 255))


def causes(L, lt, dur, fonts, args):
    """Three cause cards popping in sequence: profit booking, US rates, rupee."""
    d = ImageDraw.Draw(L, "RGBA")
    f = fonts["small"]
    labels = args.get("labels", ["मुनाफ़ावसूली", "US ब्याज़ दर", "₹93/$"])
    per = max(0.8, (dur - 0.5) / 3)
    for i, t in enumerate(labels):
        k = _back((lt - per * i * 0.85) / 0.4)
        if k <= 0:
            continue
        cx = 210 + i * 330
        w, h = 140 * k, 120 * k
        d.rounded_rectangle([cx - w, CY - h, cx + w, CY + h], 22, fill=(35, 30, 55), outline=(255, 196, 0), width=4)
        iy = CY - 40 * k
        if i == 0:      # hand taking coins: up arrow then coins
            for j in range(3):
                d.ellipse([cx - 40 + j * 28 - 18 * k, iy - 18 * k + j * 6, cx - 40 + j * 28 + 18 * k, iy + 18 * k + j * 6], fill=(255, 196, 0))
        elif i == 1:    # percent with up arrow
            d.text((cx - 50 * k, iy - 55 * k), "%", font=fonts["mid"], fill=(255, 120, 120)) if k > 0.6 else None
            d.polygon([(cx + 40, iy - 40), (cx + 70, iy), (cx + 10, iy)], fill=RED_C)
        else:           # rupee falling
            d.text((cx - 25, iy - 60), "₹", font=fonts["mid"], fill=(255, 255, 255)) if k > 0.6 else None
            _arrow_down(d, cx + 60, iy - 10, 0.7, RED_C)
        if k > 0.8:
            d.text((cx - d.textlength(t, font=f) / 2, CY + 50), t, font=f, fill=(255, 255, 255))


ANIMS.update({"candlecrash": candlecrash, "ticker": ticker, "linecrash": linecrash, "moneybag": moneybag,
              "sectordown": sectordown, "causes": causes})


# ================================================================ news-bulletin set
def bottle(L, lt, dur, fonts, args):
    """Generic water bottle (no brand), lab test FAIL stamp, then company's response tag."""
    d = ImageDraw.Draw(L, "RGBA")
    f = fonts["small"]
    cx, base = 330, BY1 - 10
    d.rounded_rectangle([cx - 28, base - 290, cx + 28, base - 250], 8, fill=(40, 110, 220))
    d.rounded_rectangle([cx - 70, base - 255, cx + 70, base], 34, fill=(190, 230, 255, 200))
    lvl = base - 210 + 6 * math.sin(lt * 4)
    d.rounded_rectangle([cx - 62, lvl, cx + 62, base - 8], 28, fill=(90, 170, 240, 200))
    d.rectangle([cx - 70, base - 170, cx + 70, base - 110], fill=(255, 255, 255, 230))
    for k in range(5):
        ph = (lt * 0.7 + k / 5) % 1
        bx = cx - 40 + k * 20; by = base - 20 - 180 * ph
        d.ellipse([bx - 6, by - 6, bx + 6, by + 6], outline=(255, 255, 255, int(220 * (1 - ph))), width=2)
    # test tube
    tx = 560
    d.rounded_rectangle([tx - 24, BY0 + 10, tx + 24, base - 30], 24, outline=(230, 230, 240), width=5)
    d.rounded_rectangle([tx - 19, BY0 + 120, tx + 19, base - 35], 19, fill=(255, 196, 0, 200))
    if lt > 0.8:
        k = _back((lt - 0.8) / 0.35)
        st = Image.new("RGBA", (300, 110), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([4, 4, 296, 106], 14, outline=(230, 40, 50), width=9)
        t = args.get("stamp", "FAIL")
        sd.text((150 - sd.textlength(t, font=fonts["mid"]) / 2 * 0.6, 8), "", font=f)
        sd.text((150 - sd.textlength(t, font=f) / 2, 22), t, font=f, fill=(230, 40, 50))
        st = st.resize((max(1, int(300 * k)), max(1, int(110 * k))), Image.LANCZOS).rotate(-10, expand=True, resample=Image.BICUBIC)
        L.alpha_composite(st, (int(820 - st.width / 2), int(BY0 + 70 - st.height / 2)))
    if lt > max(2.2, dur * 0.55):
        t = args.get("reply", "कंपनी: पानी सुरक्षित")
        k = _ease((lt - max(2.2, dur * 0.55)) / 0.4)
        w = d.textlength(t, font=f) + 40
        x0 = 810 - w / 2
        d.rounded_rectangle([x0, BY1 - 105, x0 + w, BY1 - 45], 28, fill=(60, 160, 230, int(240 * k)))
        d.text((x0 + 20, BY1 - 103), t, font=f, fill=(255, 255, 255, int(255 * k)))


def courtlist(L, lt, dur, fonts, args):
    """Gavel striking + voter list where struck-out names get restored (ticks)."""
    d = ImageDraw.Draw(L, "RGBA")
    f = fonts["small"]
    # list sheet
    x0, y0, x1, y1 = 520, BY0 - 10, 900, BY1 - 10
    d.rounded_rectangle([x0, y0, x1, y1], 16, fill=(245, 240, 228))
    d.text((x0 + 20, y0 + 6), args.get("title", "वोटर लिस्ट"), font=f, fill=(40, 40, 60))
    rows = 4
    for r in range(rows):
        y = y0 + 80 + r * 50
        d.ellipse([x0 + 22, y, x0 + 52, y + 30], fill=(150, 150, 170))
        d.rectangle([x0 + 70, y + 8, x1 - 80, y + 22], fill=(170, 165, 150))
        restored = lt > 0.9 + r * 0.45
        if not restored:
            d.line([(x0 + 60, y + 15), (x1 - 70, y + 15)], fill=(220, 40, 50), width=6)
        else:
            k = _back(min(1, (lt - 0.9 - r * 0.45) / 0.3))
            d.line([(x1 - 60, y + 15), (x1 - 48, y + 15 + 12 * k), (x1 - 25, y + 15 - 16 * k)], fill=(40, 170, 90), width=7)
    # gavel (strikes at start and every ~1.6 s)
    ph = (lt % 1.6)
    down = ph < 0.15
    ang = -0.15 if down else -0.85
    hx, hy = 330, BY1 - 70
    tx, ty = hx - 200 * math.cos(ang), hy + 200 * math.sin(ang) - 10
    d.rectangle([150, BY1 - 40, 420, BY1 - 10], fill=(140, 95, 55))
    d.line([(hx, hy), (tx, ty)], fill=(160, 110, 60), width=16)
    d.rounded_rectangle([tx - 55, ty - 32, tx + 55, ty + 32], 10, fill=(120, 80, 45))
    if down:
        for k in range(6):
            a = math.pi + k * math.pi / 5
            d.line([(260 + 40 * math.cos(a), BY1 - 45 + 25 * math.sin(a)), (260 + 80 * math.cos(a), BY1 - 45 + 50 * math.sin(a))], fill=(255, 196, 0), width=5)


def aichip(L, lt, dur, fonts, args):
    """Glowing chip with circuit traces pulsing, plus a bar shooting up with a value tag."""
    d = ImageDraw.Draw(L, "RGBA")
    f = fonts["small"]
    cx, cy, s = 330, CY, 110
    for k in range(6):
        for side in (-1, 1):
            y = cy - s + 20 + k * 36
            d.line([(cx + side * s, y), (cx + side * (s + 55), y)], fill=(255, 196, 0), width=6)
            x = cx - s + 20 + k * 36
            d.line([(x, cy + side * s), (x, cy + side * (s + 55))], fill=(255, 196, 0), width=6)
    g = 0.5 + 0.5 * math.sin(lt * 4)
    d.rounded_rectangle([cx - s, cy - s, cx + s, cy + s], 20, fill=(30, 40, 70), outline=(120, 200, 255, int(150 + 100 * g)), width=6)
    d.text((cx - d.textlength("AI", font=fonts["mid"]) / 2, cy - 80), "AI", font=fonts["mid"], fill=(120, 200, 255))
    for k in range(4):
        ph = (lt * 0.8 + k / 4) % 1
        x = cx + s + 55 + 0 * ph
        d.ellipse([cx + s + 55 - 6 + 0, cy - s + 20 + k * 36 * 1.0 - 6, cx + s + 55 + 6, cy - s + 20 + k * 36 + 6], fill=(255, 240, 150, int(255 * (1 - ph))))
    # bars
    for i, (frac, lab, col) in enumerate(((0.5, args.get("a", "2025"), (120, 130, 170)), (0.98, args.get("b", "2026"), (60, 200, 120)))):
        x = 690 + i * 170
        p = _ease((lt - 0.3 - 0.4 * i) / 1.0)
        h = (BY1 - BY0 - 60) * frac * p
        d.rounded_rectangle([x - 55, BY1 - 40 - h, x + 55, BY1 - 40], 10, fill=col)
        d.text((x - d.textlength(lab, font=f) / 2, BY1 - 35), lab, font=f, fill=(220, 220, 235))
    if lt > 1.3:
        t = args.get("tag", "+96%")
        d.rounded_rectangle([760, BY0 - 20, 760 + d.textlength(t, font=f) + 40, BY0 + 40], 28, fill=(60, 200, 120))
        d.text((780, BY0 - 18), t, font=f, fill=(255, 255, 255))


def numpick(L, lt, dur, fonts, args):
    """Five numbered buttons popping in, one pulsing (comment the number)."""
    d = ImageDraw.Draw(L, "RGBA")
    f = fonts["mid"]
    for i in range(5):
        k = _back((lt - 0.12 * i) / 0.35)
        if k <= 0:
            continue
        cx = 160 + i * 190
        pulse = 1 + (0.12 * math.sin(lt * 7) if int(lt / 0.7) % 5 == i else 0)
        r = 72 * k * pulse
        d.ellipse([cx - r, CY - r, cx + r, CY + r], fill=(255, 196, 0) if int(lt / 0.7) % 5 == i else (60, 50, 90),
                  outline=(255, 255, 255), width=4)
        t = str(i + 1)
        if k > 0.7:
            d.text((cx - d.textlength(t, font=f) / 2, CY - 82), t, font=f, fill=(20, 15, 30) if int(lt / 0.7) % 5 == i else (255, 255, 255))


ANIMS.update({"bottle": bottle, "courtlist": courtlist, "aichip": aichip, "numpick": numpick})
