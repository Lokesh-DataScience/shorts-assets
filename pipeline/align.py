"""Time each scene of a script to a user-recorded voiceover, without speech recognition.

Usage: python3 align.py script.json voice.wav out_dir
Finds pauses with ffmpeg silencedetect, then picks the N-1 pauses that make every
scene's speaking rate (syllables per second) as even as possible. Writes
out_dir/timings.json in the format render.py expects.
"""
import json, re, subprocess, sys, os
import numpy as np, soundfile as sf

script, audio, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
data = json.load(open(script))
lines = [s["say"] for s in data["scenes"]]

def syl(s):
    dev = len(re.findall(r"[क-हअ-औक़-य़]", s))
    lat = re.findall(r"[A-Za-z]+", s)
    lat_syl = sum(max(1, len(re.findall(r"[aeiouy]+", w.lower()))) for w in lat)
    dig = sum(len(d) * 1.5 for d in re.findall(r"\d+", s))
    return max(1.0, dev + lat_syl + dig)

w = np.array([syl(l) for l in lines])
x, sr = sf.read(audio)
x = x if x.ndim == 1 else x.mean(1)
total = len(x) / sr
nz = np.where(np.abs(x) > 0.01)[0]
t0, t1 = nz[0] / sr, nz[-1] / sr

err = subprocess.run(["ffmpeg", "-hide_banner", "-i", audio, "-af", "silencedetect=noise=-38dB:d=0.12",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
st = [float(v) for v in re.findall(r"silence_start: ([\d.]+)", err)]
en = [float(v) for v in re.findall(r"silence_end: ([\d.]+)", err)]
gaps = [(a, b) for a, b in zip(st, en) if t0 + 0.3 < a and b < t1 - 0.3]
N, G = len(lines), len(gaps)
if G < N - 1:
    sys.exit(f"only {G} pauses for {N} scenes: ask the user to pause ~0.5s between lines")

# --- repeated opener (e.g. "फैक्ट नंबर"): scenes whose first two words match get a sound-match bonus
n = int(0.025 * sr); hop = n // 2
def spec(a):
    if len(a) < n * 4: return None
    fr = np.lib.stride_tricks.sliding_window_view(a, n)[::hop] * np.hanning(n)
    S = np.log(np.abs(np.fft.rfft(fr, axis=1))[:, 3:120] + 1e-3)
    return S - S.mean(1, keepdims=True)
def sim(t, tmpl, L=0.75):
    best = -1.0
    for dt in np.arange(-0.08, 0.09, 0.02):
        s_ = spec(x[int((t + dt) * sr):int((t + dt + L) * sr)])
        if s_ is None: continue
        m = min(len(s_), len(tmpl))
        best = max(best, float(np.corrcoef(s_[:m].ravel(), tmpl[:m].ravel())[0, 1]))
    return best
opener = lambda l: " ".join(re.sub(r"[^\w\s]", " ", l).split()[:2])
ops = [opener(l) for l in lines]
shared = [i for i in range(len(lines)) if ops.count(ops[i]) >= 3]
BONUS = 12.0  # weight of the sound match; gsim is centred so weak matches are penalised

# expected duration per scene at the recording's average rate; small bonus for longer pauses
rate = w.sum() / (t1 - t0 - 0.35 * (N - 1))
exp = w / rate
W = 10.0
def dc(dur, e):
    # relative duration error: speakers speed up and slow down, so penalise ratios, not seconds
    return W * np.log(max(dur, 0.2) / e) ** 2 if dur > 0.3 else 1e9

def run_dp(gsim):
  INF = 1e18
  # dp[k][g] = best cost with scene k ending at gap g
  dp = np.full((N, G), INF); back = np.zeros((N, G), int)
  for g in range(G):
      dp[0][g] = dc(gaps[g][0] - t0, exp[0]) - 0.5 * (gaps[g][1] - gaps[g][0])
  for k in range(1, N - 1):
      for g in range(k, G):
          for p in range(k - 1, g):
              c = dp[k - 1][p] + dc(gaps[g][0] - gaps[p][1], exp[k]) - 0.5 * (gaps[g][1] - gaps[g][0]) - (BONUS * gsim[p] if k in shared else 0)
              if c < dp[k][g]:
                  dp[k][g], back[k][g] = c, p
  best, bg = INF, -1
  for g in range(N - 2, G):
      c = dp[N - 2][g] + dc(t1 - gaps[g][1], exp[N - 1]) - (BONUS * gsim[g] if (N - 1) in shared else 0)
      if c < best:
          best, bg = c, g
  chosen = [bg]
  for k in range(N - 2, 0, -1):
      chosen.append(back[k][chosen[-1]])
  chosen = chosen[::-1]
  return chosen

chosen = run_dp([0.0] * G)
if shared:
    first = min(shared)
    if first > 0:
        tmpl = spec(x[int(gaps[chosen[first - 1]][1] * sr):int((gaps[chosen[first - 1]][1] + 0.75) * sr)])
        gsim = [sim(b, tmpl) - 0.35 for _, b in gaps]
        chosen = run_dp(gsim)
starts = [t0] + [gaps[g][1] for g in chosen]
ends = [gaps[g][0] for g in chosen] + [t1]
scenes = []
for i, (a, e) in enumerate(zip(starts, ends)):
    nxt = starts[i + 1] if i + 1 < N else total
    scenes.append({"i": i, "start": 0.0 if i == 0 else round(a, 3), "end": round(nxt, 3), "speech": round(e - a, 3)})
json.dump({"total": round(total, 3), "scenes": scenes}, open(os.path.join(out, "timings.json"), "w"), indent=1)
for s, l, ww in zip(scenes, lines, w):
    print(f"{s['start']:6.2f}-{s['start']+s['speech']:6.2f}s  {ww/s['speech']:4.1f} syl/s  {l[:40]}")
