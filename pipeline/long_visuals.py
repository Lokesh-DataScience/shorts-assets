"""Extra visuals for render_long.py (16:9): flags, leader photo cards, warhead rows, Hormuz route map,
and small side animations. Everything is drawn in code; leader photos are only the files the user supplies
(people/<key>.png cutouts made with cutout.py)."""
import math, os
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080
GOLD, WHITE, MUTED, RED, GREEN = (255, 196, 0), (255, 255, 255), (200, 196, 215), (255, 80, 80), (90, 220, 140)


def eo(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def eb(x):
    x = max(0.0, min(1.0, x)); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


# ------------------------------------------------------------------ flags
def _star(d, cx, cy, r, fill, rot=-math.pi / 2):
    pts = []
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.4
        a = rot + k * math.pi / 5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def flag(code, w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if code == "us":
        for k in range(13):
            d.rectangle([0, k * h / 13, w, (k + 1) * h / 13], fill=(178, 34, 52) if k % 2 == 0 else (255, 255, 255))
        cw, ch = w * 0.4, h * 7 / 13
        d.rectangle([0, 0, cw, ch], fill=(60, 59, 110))
        for r in range(5):
            for c in range(6):
                d.ellipse([cw * (c + 0.5) / 6 - 3, ch * (r + 0.5) / 5 - 3, cw * (c + 0.5) / 6 + 3, ch * (r + 0.5) / 5 + 3], fill=WHITE)
    elif code == "cn":
        d.rectangle([0, 0, w, h], fill=(222, 41, 16))
        u = h / 20
        _star(d, 5 * u, 5 * u, 3 * u, (255, 222, 0))
        for (x, y) in ((10, 2), (12, 4), (12, 7), (10, 9)):
            _star(d, x * u, y * u, u, (255, 222, 0), rot=math.atan2(5 - y, 5 - x))
    elif code == "ru":
        for k, c in enumerate(((255, 255, 255), (0, 57, 166), (213, 43, 30))):
            d.rectangle([0, k * h / 3, w, (k + 1) * h / 3], fill=c)
    elif code == "in":
        for k, c in enumerate(((255, 153, 51), (255, 255, 255), (19, 136, 8))):
            d.rectangle([0, k * h / 3, w, (k + 1) * h / 3], fill=c)
        r = h / 6 - 2
        d.ellipse([w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r], outline=(0, 0, 128), width=max(2, int(h / 60)))
        for k in range(24):
            a = k * math.pi / 12
            d.line([w / 2, h / 2, w / 2 + r * math.cos(a), h / 2 + r * math.sin(a)], fill=(0, 0, 128), width=1)
    else:
        d.rectangle([0, 0, w, h], fill=(90, 90, 110))
    return im


FLAG_COL = {"us": (60, 59, 110), "cn": (222, 41, 16), "ru": (0, 57, 166), "in": (255, 153, 51)}

# ------------------------------------------------------------------ leader cards
_photo_cache = {}


def photo(base, pdir, key):
    if key not in _photo_cache:
        p = os.path.join(base, pdir, f"{key}.png")
        _photo_cache[key] = Image.open(p).convert("RGBA") if os.path.exists(p) else None
    return _photo_cache[key]


def leader_card(im, cx, cy, r, key, info, photo_im, t, alpha, focus, fonts, line=None):
    """Flag disc with the cutout over it (head may pop out above the disc), then a name plate."""
    if alpha <= 0:
        return
    r = int(r)
    S = int(r * 2 + 40)
    L = Image.new("RGBA", (S, int(S * 1.45)), (0, 0, 0, 0))
    ox, oy = S // 2, int(S * 1.45) - S // 2 - 20          # disc centre in layer
    d = ImageDraw.Draw(L)
    # glow + flag disc
    g = Image.new("RGBA", L.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([ox - r - 18, oy - r - 18, ox + r + 18, oy + r + 18], fill=FLAG_COL.get(key, GOLD) + (150,))
    L.alpha_composite(g.filter(ImageFilter.GaussianBlur(18)))
    fl = flag(key, int(2 * r * 1.6), int(2 * r))
    fl = fl.crop((int(fl.width / 2 - r), 0, int(fl.width / 2 + r), int(2 * r)))
    m = Image.new("L", fl.size, 0); ImageDraw.Draw(m).ellipse([0, 0, fl.width - 1, fl.height - 1], fill=255)
    fl.putalpha(m.point(lambda v: int(v * 0.85)))
    L.alpha_composite(fl, (ox - r, oy - r))
    if photo_im is not None:
        z = 1.0 + 0.03 * math.sin(t * 0.6)                  # slow breathing zoom
        ph = photo_im
        th = int(r * 2.35 * z)
        tw = int(ph.width * th / ph.height)
        if tw > 2.2 * r:
            tw = int(2.2 * r); th = int(ph.height * tw / ph.width)
        ph = ph.resize((tw, th), Image.LANCZOS)
        pl = Image.new("RGBA", L.size, (0, 0, 0, 0))
        pl.alpha_composite(ph, (ox - tw // 2, oy + r - th))
        # keep inside the disc below its centre line, free above it (cut-out pop)
        mk = Image.new("L", L.size, 0); md = ImageDraw.Draw(mk)
        md.ellipse([ox - r, oy - r, ox + r, oy + r], fill=255)
        md.rectangle([0, 0, L.width, oy], fill=255)
        pl.putalpha(Image.composite(pl.getchannel("A"), Image.new("L", L.size, 0), mk))
        L.alpha_composite(pl)
    else:
        # no photo yet: name initial on the flag
        f = fonts["mid"]
        ini = info["name"].split()[0][:1] if info.get("name") else key.upper()
        d.text((ox - d.textlength(ini, font=f) / 2, oy - 70), ini, font=f, fill=WHITE, stroke_width=6, stroke_fill=(0, 0, 0))
    ring = GOLD if focus else (255, 255, 255)
    ImageDraw.Draw(L).ellipse([ox - r, oy - r, ox + r, oy + r], outline=ring + (255,), width=8 if focus else 5)
    if alpha < 1:
        L.putalpha(L.getchannel("A").point(lambda v: int(v * alpha)))
    im.paste(L, (int(cx - ox), int(cy - oy)), L)
    # name plate
    dr = ImageDraw.Draw(im, "RGBA")
    nm = info.get("name", key)
    fn, fr = fonts["sub"], fonts["small"]
    nw = dr.textlength(nm, font=fn) + 60
    py = cy + r + 28
    dr.rounded_rectangle([cx - nw / 2, py, cx + nw / 2, py + 66], 33, fill=(GOLD if focus else (255, 255, 255)) + (int(240 * alpha),))
    dr.text((cx - dr.textlength(nm, font=fn) / 2, py + 4), nm, font=fn, fill=(20, 15, 30, int(255 * alpha)))
    sub = line or info.get("role", "")
    if sub:
        col = GOLD if line else MUTED
        dr.text((cx - dr.textlength(sub, font=fr) / 2, py + 76), sub, font=fr, fill=col + (int(255 * alpha),))


def r_leaders(im, dr, s, lt, a, ctx):
    who = s["who"]; n = len(who)
    r = {1: 185, 2: 195, 3: 175}.get(n, 160)
    gap = {1: 0, 2: 620, 3: 560}.get(n, 480)
    head = s.get("head")
    if head:
        L = ctx["text"](head, ctx["f_mid"], GOLD, eo(lt / 0.3) * a)
        ctx["put"](im, L, W / 2, 150, ctx["fit"](ctx["f_mid"], head, 1600))
    if s.get("sub"):
        L = ctx["text"](s["sub"], ctx["f_sub"], WHITE, eo((lt - 0.3) / 0.3) * a)
        ctx["put"](im, L, W / 2, 225, ctx["fit"](ctx["f_sub"], s["sub"], 1600))
    cy = 545 if (head or s.get("sub")) else 500
    if n == 1:
        cy = 590
    lines = s.get("lines") or [None] * n
    for k, key in enumerate(who):
        cx = W / 2 + (k - (n - 1) / 2) * gap
        p = eb((lt - 0.12 * k) / 0.55)
        al = eo((lt - 0.12 * k) / 0.3) * a
        focus = s.get("focus") == key or n == 1
        info = ctx["people"].get(key, {})
        leader_card(im, cx, cy + 80 * (1 - p), r * (1.08 if s.get("focus") == key else 1.0), key, info,
                    photo(ctx["base"], ctx["pdir"], key), lt, al, focus, ctx["fonts"],
                    line=lines[k] if lines[k] and lt > 0.5 + 0.9 * k else None)


# ------------------------------------------------------------------ warheads
def _missile(d, x, y, s, col):
    d.rounded_rectangle([x - 5 * s, y - 22 * s, x + 5 * s, y + 14 * s], 4 * s, fill=col)
    d.polygon([(x - 5 * s, y - 20 * s), (x, y - 32 * s), (x + 5 * s, y - 20 * s)], fill=col)
    d.polygon([(x - 5 * s, y + 6 * s), (x - 11 * s, y + 16 * s), (x - 5 * s, y + 14 * s)], fill=col)
    d.polygon([(x + 5 * s, y + 6 * s), (x + 11 * s, y + 16 * s), (x + 5 * s, y + 14 * s)], fill=col)


def r_warheads(im, dr, s, lt, a, ctx):
    items = s["items"]; per = 250                        # one icon = 250 warheads
    y0 = 470 - (len(items) - 1) * 100
    for k, it in enumerate(items):
        y = y0 + k * 200
        al = eo((lt - 0.2 * k) / 0.3) * a
        fl = flag(it["flag"], 150, 100)
        fl.putalpha(fl.getchannel("A").point(lambda v: int(v * al)))
        im.paste(fl, (180, int(y - 50)), fl)
        lab = ctx["text"](it["label"], ctx["f_sub"], WHITE, al)
        ctx["put"](im, lab, 255, y + 85)
        n_full = it["value"] / per
        shown = n_full * eo((lt - 0.3 - 0.2 * k) / 1.4)
        col = (255, 120, 90) if it["flag"] != "cn" else (255, 196, 0)
        for j in range(int(math.ceil(n_full))):
            frac = max(0.0, min(1.0, shown - j))
            if frac <= 0:
                break
            x = 420 + j * 58
            pop = eb(frac)
            _missile(dr, x, y + 10, 1.9 * pop, col + (int(255 * al),))
        vx = 420 + int(math.ceil(n_full)) * 58 + 40
        v = ctx["text"](it["show"], ctx["f_mid"], WHITE, eo((lt - 1.2 - 0.2 * k) / 0.4) * a)
        im.paste(v, (int(vx), int(y - v.height / 2)), v)
    if s.get("sub"):
        ctx["put"](im, ctx["text"](s["sub"] + "  (1 आइकन = 250)", ctx["f_small"], MUTED, eo((lt - 0.8) / 0.4) * a),
                   W / 2, y0 + len(items) * 200 - 45)


# ------------------------------------------------------------------ Hormuz route map
IRAN = [(0, 0), (1400, 0), (1400, 270), (1000, 290), (820, 310), (720, 330), (640, 300), (460, 240), (240, 175), (0, 140)]
ARAB = [(0, 560), (0, 330), (130, 300), (260, 320), (300, 290), (330, 300), (330, 360), (420, 385), (560, 400), (640, 380),
        (690, 372), (712, 395), (735, 460), (880, 520), (1000, 560)]
ROUTE = [(120, 250), (430, 300), (600, 335), (705, 350), (800, 400), (1000, 455), (1230, 455), (1380, 430)]


def _along(pts, f):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum(seg); d = f * tot
    for i, sl in enumerate(seg):
        if d <= sl:
            u = d / sl
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u), \
                   math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])
        d -= sl
    return pts[-1], 0.0


def r_hormuz(im, dr, s, lt, a, ctx):
    ox, oy = 260, 250
    T = lambda p: (ox + p[0], oy + p[1])
    al = eo(lt / 0.4) * a
    dr.rounded_rectangle([ox - 10, oy - 10, ox + 1410, oy + 570], 30, fill=(20, 60, 110, int(200 * al)))
    for poly, col in ((IRAN, (120, 100, 70)), (ARAB, (150, 125, 85))):
        dr.polygon([T(p) for p in poly], fill=col + (int(255 * al),))
    f = ctx["f_small"]
    for txt, p, c in (("ईरान", (560, 110), WHITE), ("अरब देश", (230, 470), WHITE), ("अरब सागर", (1120, 380), (170, 210, 255)),
                      ("खाड़ी", (500, 330), (170, 210, 255))):
        dr.text((ox + p[0] - dr.textlength(txt, font=f) / 2, oy + p[1]), txt, font=f, fill=c + (int(255 * al),))
    # strait marker
    sx, sy = T((705, 352))
    pulse = 1 + 0.25 * math.sin(lt * 5)
    blocked = s.get("blocked", True)
    mc = RED if blocked else GREEN
    dr.ellipse([sx - 38 * pulse, sy - 38 * pulse, sx + 38 * pulse, sy + 38 * pulse], outline=mc + (int(255 * al),), width=5)
    lab = "होर्मुज़ स्ट्रेट"
    dr.text((sx - dr.textlength(lab, font=f) / 2, sy - 105), lab, font=f, fill=mc + (int(255 * al),), stroke_width=4, stroke_fill=(0, 0, 0))
    # route
    rp = [T(p) for p in ROUTE]
    n = len(rp)
    prog = eo((lt - 0.3) / 1.2)
    for i in range(n - 1):
        u = max(0.0, min(1.0, prog * (n - 1) - i))
        if u <= 0: break
        (x0, y0), (x1, y1) = rp[i], rp[i + 1]
        steps = int(math.dist(rp[i], rp[i + 1]) / 24)
        for k in range(steps):
            if k / steps > u: break
            if k % 2 == 0:
                xa, ya = x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps
                xb, yb = x0 + (x1 - x0) * (k + 1) / steps, y0 + (y1 - y0) * (k + 1) / steps
                dr.line([(xa, ya), (xb, yb)], fill=(255, 255, 255, int(170 * al)), width=5)
    # India marker at the route end
    ex, ey = rp[-1]
    dr.polygon([(ex + 10, ey - 22), (ex + 40, ey), (ex + 10, ey + 22)], fill=(255, 153, 51, int(255 * al)))
    fl = flag("in", 90, 60); fl.putalpha(fl.getchannel("A").point(lambda v: int(v * al)))
    im.paste(fl, (int(ex - 20), int(ey + 34)), fl)
    # tankers
    stop = 0.40                                         # fraction of route where the strait is
    for j in range(4):
        base = ((lt * 0.07 + j * 0.25) % 1.0)
        fr = min(base, stop - 0.03 - j * 0.035) if blocked else base
        if fr < 0: continue
        (x, y), ang = _along(rp, fr)
        tl = Image.new("RGBA", (90, 44), (0, 0, 0, 0)); td = ImageDraw.Draw(tl)
        td.polygon([(0, 14), (74, 14), (88, 22), (74, 30), (0, 30)], fill=(40, 40, 50))
        td.rectangle([6, 8, 30, 14], fill=(230, 230, 235)); td.rectangle([40, 10, 70, 14], fill=(200, 60, 50))
        tl = tl.rotate(-math.degrees(ang), expand=True, resample=Image.BICUBIC)
        tl.putalpha(tl.getchannel("A").point(lambda v: int(v * al)))
        im.paste(tl, (int(x - tl.width / 2), int(y - tl.height / 2)), tl)
    if blocked:
        k = eb((lt - 1.0) / 0.4)
        if k > 0:
            L = 34 * k
            dr.line([(sx - L, sy - L), (sx + L, sy + L)], fill=RED + (int(255 * a),), width=12)
            dr.line([(sx - L, sy + L), (sx + L, sy - L)], fill=RED + (int(255 * a),), width=12)
    if s.get("head"):
        ctx["put"](im, ctx["text"](s["head"], ctx["f_mid"], GOLD, eo(lt / 0.3) * a), W / 2, 150, ctx["fit"](ctx["f_mid"], s["head"], 1600))
    if s.get("sub"):
        ctx["put"](im, ctx["text"](s["sub"], ctx["f_small"], WHITE, eo((lt - 0.4) / 0.4) * a), W / 2, 862,
                   ctx["fit"](ctx["f_small"], s["sub"], 1600))


# ------------------------------------------------------------------ side animations (box centred at cx, cy, size ~360)
def side_anim(im, name, lt, a, cx, cy, ctx):
    L = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(L, "RGBA")
    c = 210
    s = eb(lt / 0.5)
    if name == "pin":
        d.ellipse([c - 150, c + 90, c + 150, c + 150], fill=(255, 255, 255, 40))
        for k in range(3):
            ph = (lt * 0.8 + k / 3) % 1
            rr = 30 + 120 * ph
            d.ellipse([c - rr, c + 120 - rr * 0.25, c + rr, c + 120 + rr * 0.25], outline=(255, 196, 0, int(200 * (1 - ph))), width=4)
        py = c + 120 - 240 * (1 - eb(lt / 0.6))
        d.ellipse([c - 60, py - 190, c + 60, py - 70], fill=(230, 50, 70))
        d.polygon([(c - 52, py - 110), (c, py), (c + 52, py - 110)], fill=(230, 50, 70))
        d.ellipse([c - 24, py - 154, c + 24, py - 106], fill=(255, 255, 255))
    elif name == "globe":
        r = 150 * s
        d.ellipse([c - r, c - r, c + r, c + r], fill=(30, 110, 200))
        for k in range(5):
            ph = ((lt * 0.25 + k / 5) % 1) * math.pi
            ew = abs(math.cos(ph)) * r
            d.ellipse([c - ew, c - r, c + ew, c + r], outline=(160, 220, 255, 150), width=3)
        for yy in (-0.5, 0, 0.5):
            hw = r * math.sqrt(1 - yy * yy)
            d.line([(c - hw, c + yy * r), (c + hw, c + yy * r)], fill=(160, 220, 255, 150), width=3)
        for (bx, by, br) in ((-0.3, -0.2, 0.35), (0.35, 0.25, 0.3)):
            x = c + (bx + 0.2 * math.sin(lt * 0.5)) * r
            d.ellipse([x - br * r, c + by * r - br * r * 0.7, x + br * r, c + by * r + br * r * 0.7], fill=(90, 190, 110, 220))
        d.ellipse([c - r, c - r, c + r, c + r], outline=WHITE, width=4)
    elif name == "atom":
        d.ellipse([c - 30 * s, c - 30 * s, c + 30 * s, c + 30 * s], fill=(255, 196, 0))
        for k in range(3):
            rot = k * math.pi / 3
            pts = []
            for j in range(61):
                u = j / 60 * 2 * math.pi
                x, y = 160 * s * math.cos(u), 55 * s * math.sin(u)
                pts.append((c + x * math.cos(rot) - y * math.sin(rot), c + x * math.sin(rot) + y * math.cos(rot)))
            d.line(pts, fill=(120, 220, 255, 200), width=4)
            u = lt * 3 + k * 2
            x, y = 160 * s * math.cos(u), 55 * s * math.sin(u)
            ex, ey = c + x * math.cos(rot) - y * math.sin(rot), c + x * math.sin(rot) + y * math.cos(rot)
            d.ellipse([ex - 14, ey - 14, ex + 14, ey + 14], fill=(255, 90, 140))
    elif name in ("oil", "lpg"):
        if name == "oil":
            bw, bh = 170 * s, 230 * s
            d.rounded_rectangle([c - bw / 2, c - bh / 2 + 40, c + bw / 2, c + bh / 2 + 40], 22, fill=(30, 30, 40))
            for yy in (-0.25, 0.25):
                d.rectangle([c - bw / 2, c + 40 + yy * bh - 6, c + bw / 2, c + 40 + yy * bh + 6], fill=(255, 196, 0))
            ph = (lt * 0.9) % 1
            dy = c - 200 + 150 * ph
            d.ellipse([c - 22, dy, c + 22, dy + 50], fill=(20, 20, 25))
            d.polygon([(c - 20, dy + 18), (c, dy - 22), (c + 20, dy + 18)], fill=(20, 20, 25))
        else:
            d.rounded_rectangle([c - 85 * s, c - 90 * s + 40, c + 85 * s, c + 150 * s + 40], 60, fill=(210, 40, 40))
            d.rectangle([c - 35, c - 140 + 40, c + 35, c - 90 + 40], fill=(120, 120, 130))
            fh = 60 + 15 * math.sin(lt * 12)
            d.polygon([(c - 22, c - 140 + 40), (c, c - 140 + 40 - fh), (c + 22, c - 140 + 40)], fill=(80, 170, 255))
            d.text((c - 40, c + 20), "LPG", font=ctx["f_small"], fill=WHITE)
    elif name == "gavel":
        d.rectangle([c - 120, c + 110, c + 120, c + 150], fill=(140, 95, 55))
        sw = math.sin(min(1, (lt % 1.3) / 0.35) * math.pi) if (lt % 1.3) < 0.35 else 0
        ang = -0.9 + 0.9 * (1 - sw) if lt > 0.4 else -0.9
        ang = -0.9 + (0.9 if (lt % 1.3) < 0.18 else 0.0)
        hx, hy = c + 120, c + 60
        tx, ty = hx - 220 * math.cos(ang), hy + 220 * math.sin(ang) - 40
        d.line([(hx, hy), (tx, ty)], fill=(160, 110, 60), width=18)
        d.rounded_rectangle([tx - 60, ty - 35, tx + 60, ty + 35], 12, fill=(120, 80, 45))
        if (lt % 1.3) < 0.18:
            for k in range(6):
                u = k * math.pi / 5
                d.line([(c - 60 + 50 * math.cos(u), c + 100 - 30 * math.sin(u)), (c - 60 + 90 * math.cos(u), c + 100 - 60 * math.sin(u))], fill=GOLD, width=5)
    elif name == "treaty":
        d.rounded_rectangle([c - 120 * s, c - 150 * s, c + 120 * s, c + 150 * s], 14, fill=(245, 238, 220))
        for k in range(6):
            yy = c - 100 * s + k * 34 * s
            d.line([(c - 85 * s, yy), (c + 85 * s, yy)], fill=(150, 140, 120), width=5)
        d.ellipse([c + 40, c + 70, c + 110, c + 140], fill=(200, 40, 50))
        k = eb((lt - 0.9) / 0.4)
        if k > 0:
            Lx = 140 * k
            d.line([(c - Lx, c - Lx), (c + Lx, c + Lx)], fill=RED, width=22)
            d.line([(c - Lx, c + Lx), (c + Lx, c - Lx)], fill=RED, width=22)
    elif name == "cross":
        d.rounded_rectangle([c - 120 * s, c - 150 * s, c + 120 * s, c + 150 * s], 14, fill=(245, 238, 220))
        for k in range(6):
            yy = c - 100 * s + k * 34 * s
            d.line([(c - 85 * s, yy), (c + 85 * s, yy)], fill=(150, 140, 120), width=5)
        k = eb((lt - 0.5) / 0.35)
        if k > 0:
            d.ellipse([c - 110 * k, c - 110 * k, c + 110 * k, c + 110 * k], outline=RED, width=16)
            d.line([(c - 78 * k, c + 78 * k), (c + 78 * k, c - 78 * k)], fill=RED, width=16)
    elif name == "flag_in":
        fw, fh = 300, 200
        d.rectangle([60, 40, 72, 400], fill=(200, 200, 215))
        strips = 40
        cols = ((255, 153, 51), (255, 255, 255), (19, 136, 8))
        for i in range(strips):
            u = i / strips
            off = 14 * u * math.sin(u * 7 - lt * 6)
            x = 72 + i * fw / strips
            for j, col in enumerate(cols):
                d.rectangle([x, 60 + off + j * fh / 3, x + fw / strips + 1, 60 + off + (j + 1) * fh / 3], fill=col)
        off = 7 * math.sin(3.5 - lt * 6)
        d.ellipse([72 + fw / 2 - 28, 60 + off + fh / 2 - 28, 72 + fw / 2 + 28, 60 + off + fh / 2 + 28], outline=(0, 0, 128), width=4)
    elif name == "pump":
        d.rounded_rectangle([c - 100 * s, c - 150 * s, c + 70 * s, c + 170 * s], 20, fill=(40, 160, 90))
        d.rounded_rectangle([c - 75, c - 120, c + 45, c - 40], 10, fill=(20, 30, 25))
        val = "₹ " + ("".join(str((int(lt * 7) + k) % 10) for k in range(2)) if lt < 1.2 else "₹ फ्रीज़")
        d.text((c - 65, c - 112), val, font=ctx["f_small"], fill=(120, 255, 160))
        d.line([(c + 70, c - 40), (c + 130, c - 10), (c + 130, c + 110)], fill=(40, 40, 50), width=14)
    else:
        return
    if a < 1:
        L.putalpha(L.getchannel("A").point(lambda v: int(v * a)))
    im.paste(L, (int(cx - 210), int(cy - 210)), L)
