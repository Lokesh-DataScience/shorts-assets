"""Generate per-scene voiceover with Kokoro (free, offline) and write timings.

Usage: python3 tts.py script.json out_dir [voice] [speed]
Hindi Kokoro voices (hm_omega, hm_psi, hf_alpha, hf_beta) read English
phonemes with an Indian accent.
"""
import json, sys, os
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
script, out = sys.argv[1], sys.argv[2]
voice = sys.argv[3] if len(sys.argv) > 3 else "hm_omega:0.55+am_onyx:0.3+am_fenrir:0.15"
speed = float(sys.argv[4]) if len(sys.argv) > 4 else 1.1
os.makedirs(out, exist_ok=True)

k = Kokoro(os.path.join(HERE, "models/kokoro-v1.0.onnx"), os.path.join(HERE, "models/voices-v1.0.bin"))

def style(spec):
    """'hm_omega' or a blend like 'hm_omega:0.6+am_onyx:0.4' -> voice for Kokoro."""
    if ":" not in spec and "+" not in spec:
        return spec
    parts = [p.split(":") for p in spec.split("+")]
    tot = sum(float(w) for _, w in parts)
    return sum(k.get_voice_style(n) * (float(w) / tot) for n, w in parts).astype(np.float32)
vstyle = style(voice)
data = json.load(open(script))
gap = 0.25
chunks, timings, t = [], [], 0.0
sr = 24000
for i, sc in enumerate(data["scenes"]):
    samples, sr = k.create(sc["say"], voice=vstyle, speed=speed, lang="en-us")
    samples = np.asarray(samples, dtype=np.float32)
    dur = len(samples) / sr
    timings.append({"i": i, "start": round(t, 3), "end": round(t + dur + gap, 3), "speech": round(dur, 3)})
    chunks += [samples, np.zeros(int(gap * sr), dtype=np.float32)]
    t += dur + gap
raw = os.path.join(out, "voice_raw.wav")
sf.write(raw, np.concatenate(chunks), sr)
# deepen + clean: pitch down ~2 semitones (tempo kept), chest boost, tame harsh "s", even out loudness
PITCH = float(os.environ.get("VOICE_PITCH", "0.89"))
chain = (f"rubberband=pitch={PITCH}:formant=preserved,"
         "equalizer=f=140:t=q:w=1:g=4,equalizer=f=3000:t=q:w=1.5:g=2,"
         "deesser=i=0.6:m=0.6:f=0.5,"
         "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3")
import subprocess
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", chain, "-ar", "48000",
                os.path.join(out, "voice.wav")], check=True)
json.dump({"voice": voice, "total": round(t, 3), "scenes": timings}, open(os.path.join(out, "timings.json"), "w"), indent=1)
print(f"voice={voice} total={t:.2f}s scenes={len(timings)}")
