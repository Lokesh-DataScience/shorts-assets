"""Render a 16:9 long-form explainer from a project JSON and one recording per part.

Usage: python3 render_long.py project.json out_dir
  project.json: {"title", "font_main", "font_sub", "brand", "parts": [{"chapter", "audio", "scenes": [...]}]}
  Each scene has "say" (the line as recorded) and a "type":
    title    {big, sub}                        chapter cards / hook
    stat     {big, unit, sub}                  one hero number
    compare  {items:[{label, value, show}], sub}   horizontal bars
    line     {points:[{label, value, show}], sub}  animated line chart
    list     {head, items:[...]}               bullet reveal
    text     {head, sub}                       a statement
Steps per part: align.py-style pause matching -> timings; parts are joined with a short gap.
Writes out_dir/long.mp4, out_dir/chapters.txt (YouTube timestamps), out_dir/timings.json.
"""
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import long_visuals as LV

W, H, FPS = 1920, 1080, 30
proj_path, out = sys.argv[1], sys.argv[2]
BASE = os.path.dirname(os.path.abspath(proj_path))
HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(proj_path))
os.makedirs(out, exist_ok=True)
GAP = 0.6  # silence between parts

# ---------- timing: run align.py on each part ----------
def align_part(i, part):
    sj = os.path.join(out, f"part{i}_scene.json")
    json.dump({"scenes": part["scenes"]}, open(sj, "w"), ensure_ascii=False)
    od = os.path.join(out, f"part{i}")
    r = subprocess.run([sys.executable, os.path.join(HERE, "align.py"), sj, os.path.join(BASE, part["audio"]), od],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"part {i}: {r.stdout}{r.stderr}")
    print(f"--- part {i} ({part['chapter']})\n{r.stdout.rstrip()}")
    return json.load(open(os.path.join(od, "timings.json")))

scenes, chapters, audio, offset, SR = [], [], [], 0.0, 48000
for i, part in enumerate(P["parts"]):
    tm = align_part(i, part)
    x, sr = sf.read(os.path.join(BASE, part["audio"]))
    x = x if x.ndim == 1 else x.mean(1)
    if sr != SR:  # resample with ffmpeg for simplicity
        tmp = os.path.join(out, f"part{i}_48k.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(BASE, part["audio"]), "-ac", "1", "-ar", str(SR), tmp], check=True)
        x, _ = sf.read(tmp)
    for sc, t in zip(part["scenes"], tm["scenes"]):
        s = dict(sc); s.update(start=offset + t["start"], end=offset + t["end"], speech=t["speech"], part=i,
                               chapter=sc.get("chapter_name", part["chapter"]))
        if not chapters or chapters[-1][1] != s["chapter"]:
            chapters.append((0.0 if not scenes else s["start"], s["chapter"]))
        scenes.append(s)
    audio += [x.astype(np.float32), np.zeros(int(GAP * SR), np.float32)]
    offset += len(x) / SR + GAP
TOTAL = offset
for k in range(len(scenes) - 1):
    scenes[k]["end"] = scenes[k + 1]["start"]
scenes[-1]["end"] = TOTAL
sf.write(os.path.join(out, "voice_all.wav"), np.concatenate(audio), SR)
json.dump([{k: v for k, v in s.items() if k in ("start", "end", "type", "say")} for s in scenes],
          open(os.path.join(out, "timings.json"), "w"), ensure_ascii=False, indent=1)
with open(os.path.join(out, "chapters.txt"), "w") as f:
    for t, name in chapters:
        f.write(f"{int(t // 60)}:{int(t % 60):02d} {name}\n")

# ---------- drawing helpers ----------
def F(path, size): return ImageFont.truetype(os.path.join(BASE, path), size)
FM, FS = P["font_main"], P["font_sub"]
f_hero, f_big, f_mid, f_unit = F(FM, 230), F(FM, 120), F(FM, 84), F(FM, 70)
f_sub, f_small, f_cap, f_tag = F(FS, 46), F(FS, 36), F(FM, 58), F(FS, 34)
BG1, BG2 = (12, 10, 24), (46, 26, 8)
GOLD, GOLD2, WHITE, MUTED, RED, GREEN = (255, 196, 0), (255, 140, 0), (255, 255, 255), (200, 196, 215), (255, 90, 90), (90, 220, 140)
ACC = tuple(P.get("accent", GOLD))

bg = Image.new("RGB", (W + 200, H + 120))
d = ImageDraw.Draw(bg)
for y in range(bg.height):
    f = y / bg.height
    d.line([(0, y), (bg.width, y)], fill=tuple(int(BG1[c] + (BG2[c] - BG1[c]) * f) for c in range(3)))
glow = Image.new("RGB", bg.size, (0, 0, 0)); g = ImageDraw.Draw(glow)
g.ellipse([1200, -300, 2300, 700], fill=(120, 80, 10)); g.ellipse([-400, 500, 700, 1500], fill=(60, 20, 90))
bg = Image.blend(bg, glow.filter(ImageFilter.GaussianBlur(260)), 0.45)
rng = np.random.default_rng(3)
parts_xy = rng.uniform([0, 0, 1.5, 6], [W, H, 3.5, 22], size=(60, 4))

def eo(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def eb(x):
    x = max(0.0, min(1.0, x)); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def layer_text(txt, font, fill, alpha=1.0, stroke=0):
    bb = font.getbbox(txt); w, h = bb[2] - bb[0] + 40, bb[3] - bb[1] + 40
    L = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0))
    ImageDraw.Draw(L).text((20 - bb[0], 20 - bb[1]), txt, font=font, fill=fill + (int(255 * alpha),),
                           stroke_width=stroke, stroke_fill=(0, 0, 0, int(255 * alpha)))
    return L

def put(im, L, x, y, scale=1.0, anchor="c"):
    if scale != 1.0:
        L = L.resize((max(1, int(L.width * scale)), max(1, int(L.height * scale))), Image.LANCZOS)
    if anchor == "c": x -= L.width / 2
    im.paste(L, (int(x), int(y - L.height / 2)), L)

def fit(font, txt, maxw):
    return min(1.0, maxw / max(1, font.getlength(txt)))

def wrap(txt, font, maxw):
    out_, cur = [], ""
    for w_ in txt.split():
        t = (cur + " " + w_).strip()
        if font.getlength(t) <= maxw: cur = t
        else: out_.append(cur); cur = w_
    if cur: out_.append(cur)
    return out_

# caption chunks (3 words, by character weight inside each scene's speech)
caps = []
for s in scenes:
    words, chunks, cur = s["say"].split(), [], []
    for w_ in words:
        cur.append(w_)
        if len(cur) >= 4 or w_.endswith((".", "?", ",", "!", "।")):
            chunks.append(" ".join(cur)); cur = []
    if cur: chunks.append(" ".join(cur))
    tot = sum(len(c) + 2 for c in chunks); t = s["start"]
    for c in chunks:
        dur = s["speech"] * (len(c) + 2) / tot
        caps.append((t, t + dur, c)); t += dur

# ---------- scene renderers (lt = seconds into scene, a = fade-out alpha) ----------
CX, CY = W / 2, 470
MAXW = 1600

def r_title(im, dr, s, lt, a):
    if s.get("chapter_no"):
        put(im, layer_text(f"चैप्टर {s['chapter_no']}", f_sub, ACC, eo(lt / 0.3) * a), CX, CY - 190)
    sc = (0.6 + 0.4 * eb(lt / 0.5)) * fit(f_big, s["big"], MAXW)
    put(im, layer_text(s["big"], f_big, WHITE, min(1, lt / 0.2) * a), CX, CY - 40, sc)
    if s.get("sub"):
        put(im, layer_text(s["sub"], f_mid, ACC, eo((lt - 0.35) / 0.35) * a), CX, CY + 110 + 20 * (1 - eo((lt - 0.35) / 0.35)), fit(f_mid, s["sub"], MAXW))

def r_stat(im, dr, s, lt, a):
    sc = (0.5 + 0.5 * eb(lt / 0.45)) * fit(f_hero, s["big"], MAXW)
    put(im, layer_text(s["big"], f_hero, WHITE, min(1, lt / 0.2) * a), CX, CY - 60, sc)
    put(im, layer_text(s.get("unit", ""), f_unit, ACC, eo((lt - 0.25) / 0.3) * a), CX, CY + 95)
    bw = 520 * eo((lt - 0.45) / 0.5)
    dr.rounded_rectangle([CX - bw / 2, CY + 150, CX + bw / 2, CY + 162], 6, fill=GOLD2 + (int(255 * a),))
    if s.get("sub"):
        put(im, layer_text(s["sub"], f_sub, MUTED, eo((lt - 0.5) / 0.35) * a), CX, CY + 215, fit(f_sub, s["sub"], MAXW))

def r_compare(im, dr, s, lt, a):
    items = s["items"]; vmax = max(i["value"] for i in items)
    x0, x1, y0, rowh = 560, 1620, CY - (len(items) - 1) * 75, 150
    for k, it in enumerate(items):
        y = y0 + k * rowh; p = eo((lt - 0.15 * k) / 0.8)
        lab = layer_text(it["label"], f_mid if len(items) <= 3 else f_sub, WHITE, eo((lt - 0.15 * k) / 0.3) * a)
        im.paste(lab, (int(x0 - 30 - lab.width), int(y - lab.height / 2)), lab)
        bw = (x1 - x0) * it["value"] / vmax * p
        col = tuple(it.get("color", ACC if k == 0 else GOLD2))
        dr.rounded_rectangle([x0, y - 34, x0 + max(8, bw), y + 34], 14, fill=col + (int(235 * a),))
        va = eo((lt - 0.6 - 0.15 * k) / 0.3) * a
        val = layer_text(it.get("show", str(it["value"])), f_sub, WHITE, va)
        if x0 + bw + 20 + val.width <= W - 60:      # room to the right of the bar
            im.paste(val, (int(x0 + bw + 20), int(y - val.height / 2)), val)
        else:                                       # long bar: label inside, dark text
            val = layer_text(it.get("show", str(it["value"])), f_sub, (20, 15, 30), va)
            im.paste(val, (int(x0 + bw - 20 - val.width), int(y - val.height / 2)), val)
    if s.get("sub"):
        put(im, layer_text(s["sub"], f_small, MUTED, eo((lt - 0.8) / 0.4) * a), CX, y0 + len(items) * rowh + 10, fit(f_small, s["sub"], 1600))

def r_line(im, dr, s, lt, a):
    pts = s["points"]; vals = [p["value"] for p in pts]
    lo, hi = min(vals), max(vals); pad = (hi - lo) * 0.25 or 1
    lo, hi = lo - pad, hi + pad
    gx0, gx1, gy0, gy1 = 300, 1620, 230, 720
    for k in range(4):
        yy = gy0 + (gy1 - gy0) * k / 3
        dr.line([(gx0, yy), (gx1, yy)], fill=(255, 255, 255, int(35 * a)), width=2)
    xy = [(gx0 + (gx1 - gx0) * k / (len(pts) - 1), gy1 - (gy1 - gy0) * (p["value"] - lo) / (hi - lo)) for k, p in enumerate(pts)]
    prog = eo(lt / 1.6) * (len(pts) - 1)
    for k in range(len(pts) - 1):
        seg = max(0.0, min(1.0, prog - k))
        if seg <= 0: break
        (ax, ay), (bx, by) = xy[k], xy[k + 1]
        down = pts[k + 1]["value"] < pts[k]["value"]
        dr.line([(ax, ay), (ax + (bx - ax) * seg, ay + (by - ay) * seg)], fill=(RED if down else GREEN) + (int(255 * a),), width=10)
    for k, ((x, y), p) in enumerate(zip(xy, pts)):
        al = eo((prog - k + 0.3) / 0.3) * a
        if al <= 0: continue
        dr.ellipse([x - 14, y - 14, x + 14, y + 14], fill=ACC + (int(255 * al),))
        v = layer_text(p.get("show", str(p["value"])), f_sub, WHITE, al)
        put(im, v, x, y - 55)
        lb = layer_text(p["label"], f_small, MUTED, al)
        put(im, lb, x, gy1 + 55)
    if s.get("sub"):
        put(im, layer_text(s["sub"], f_sub, ACC, eo((lt - 1.4) / 0.4) * a), CX, gy1 + 125, fit(f_sub, s["sub"], 1600))

def r_list(im, dr, s, lt, a):
    put(im, layer_text(s["head"], f_mid, ACC, eo(lt / 0.3) * a), CX, CY - 200, fit(f_mid, s["head"], 1600))
    n = len(s["items"]); per = max(0.4, min(1.2, s["speech"] / (n + 1)))
    for k, it in enumerate(s["items"]):
        al = eo((lt - 0.4 - per * k) / 0.3) * a
        y = CY - 70 + k * 105
        dr.ellipse([420, y - 14, 448, y + 14], fill=GOLD2 + (int(255 * al),))
        L = layer_text(it, f_sub, WHITE, al)
        im.paste(L, (int(480 + 30 * (1 - al)), int(y - L.height / 2)), L)

def r_text(im, dr, s, lt, a):
    lines = wrap(s["head"], f_big, MAXW)
    y = CY - (len(lines) - 1) * 70 - 30
    for k, ln in enumerate(lines):
        put(im, layer_text(ln, f_big, WHITE, eo((lt - 0.12 * k) / 0.35) * a), CX, y, 0.85 + 0.15 * eb((lt - 0.12 * k) / 0.4))
        y += 140
    if s.get("sub"):
        put(im, layer_text(s["sub"], f_sub, ACC, eo((lt - 0.4) / 0.35) * a), CX, y + 10, fit(f_sub, s["sub"], MAXW))

CTX = dict(text=layer_text, put=put, fit=fit, f_mid=f_mid, f_sub=f_sub, f_small=f_small, base=BASE,
           pdir=P.get("people_dir", "people"), people=P.get("people", {}),
           fonts={"mid": f_big, "sub": f_sub, "small": f_small})
R = dict(title=r_title, stat=r_stat, compare=r_compare, line=r_line, list=r_list, text=r_text,
         leaders=lambda im, dr, s, lt, a: LV.r_leaders(im, dr, s, lt, a, CTX),
         warheads=lambda im, dr, s, lt, a: LV.r_warheads(im, dr, s, lt, a, CTX),
         hormuz=lambda im, dr, s, lt, a: LV.r_hormuz(im, dr, s, lt, a, CTX))

def draw_scene(im, dr, s, lt, a):
    global CX, MAXW
    if s.get("anim") and s["type"] in ("title", "stat", "text"):
        CX, MAXW = 780, 1150                   # content on the left, animation on the right
        R[s["type"]](im, dr, s, lt, a)
        LV.side_anim(im, s["anim"], lt, a * LV.eo(lt / 0.3), 1530, 480, CTX)
        CX, MAXW = W / 2, 1600
    else:
        R[s["type"]](im, dr, s, lt, a)

def frame(t):
    z = 1.0 + 0.04 * ((t % 20) / 20)  # slow push-in
    ox, oy = int(100 - 100 * (z - 1) * 10), int(60 - 60 * (z - 1) * 10)
    im = bg.crop((ox, oy, ox + W, oy + H)).copy()
    dr = ImageDraw.Draw(im, "RGBA")
    for x, y, r, sp in parts_xy:
        yy = (y - t * sp) % H
        dr.ellipse([x - r, yy - r, x + r, yy + r], fill=(255, 230, 160, 45))
    k = 0
    while k + 1 < len(scenes) and t >= scenes[k + 1]["start"]: k += 1
    s = scenes[k]; lt = t - s["start"]
    a = 1.0 - eo((t - (s["end"] - 0.18)) / 0.18) if t > s["end"] - 0.18 and k < len(scenes) - 1 else 1.0
    # header: brand + chapter + progress
    dr.rounded_rectangle([60, 44, 60 + f_tag.getlength(P.get("brand", "")) + 48, 100], 28, fill=GOLD + (235,))
    dr.text((84, 52), P.get("brand", ""), font=f_tag, fill=(20, 15, 30))
    ch = s["chapter"]
    dr.text((W - 60 - f_tag.getlength(ch), 54), ch, font=f_tag, fill=MUTED)
    dr.rectangle([0, H - 8, W * t / TOTAL, H], fill=GOLD + (220,))
    draw_scene(im, dr, s, lt, a)
    for (c0, c1, c) in caps:
        if c0 <= t < c1:
            pop = 0.9 + 0.1 * eb((t - c0) / 0.15)
            L = layer_text(c, f_cap, WHITE, 1.0, stroke=7)
            sc = pop * fit(f_cap, c, 1500)
            put(im, L, CX, H - 140, sc)
            break
    return im

# ---------- preview ----------
if os.environ.get("PREVIEW"):
    lt_p = float(os.environ.get("PREVIEW_T", "1.8"))
    tiles = []
    for s in scenes:
        im = bg.crop((100, 60, 100 + W, 60 + H)).copy(); dr = ImageDraw.Draw(im, "RGBA")
        draw_scene(im, dr, s, lt_p, 1.0)
        dr.text((20, H - 60), s.get("id", ""), font=f_tag, fill=GOLD)
        if os.environ.get("PREVIEW_IDS") and s.get("id") in os.environ["PREVIEW_IDS"].split(","):
            im.save(os.path.join(out, f"full_{s['id']}.png"))
        tiles.append(im.resize((480, 270)))
    cols = 6; rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 480, rows * 270))
    for k, t_ in enumerate(tiles): sheet.paste(t_, ((k % cols) * 480, (k // cols) * 270))
    sheet.save(os.path.join(out, "preview.png")); print("preview", len(tiles)); sys.exit(0)

# ---------- encode ----------
outmp4 = os.path.join(out, "long.mp4")
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-i", os.path.join(out, "voice_all.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,apad", "-shortest",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", outmp4]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
n = int((TOTAL + 0.5) * FPS)
only = os.environ.get("ONLY_SECONDS")  # quick preview: render just the first N seconds
if only: n = min(n, int(float(only) * FPS))
for i in range(n):
    p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait()
print(f"wrote {outmp4} {n/FPS:.1f}s rc={p.returncode}")
print(open(os.path.join(out, "chapters.txt")).read())
