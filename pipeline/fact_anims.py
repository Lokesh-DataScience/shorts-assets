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
    a = max(0.0, min(1.0, alpha)) * (1.0 if name == "leaders" else _ease(lt / 0.25))   # hook visuals: visible at frame 0
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
