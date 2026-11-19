# Hindi Trending-Facts Shorts pipeline

Free, offline pipeline for the Jack-of-all-trades channel.

1. `bash setup.sh` — builds Hindi+Latin fonts (Baloo 2, Mukta) into `fonts/`.
2. Write the scene file (`examples/gta6_hindi.json` shows the format) next to the user's recording `voice.wav`.
3. `python3 align.py scene.json voice.wav build/` — times scenes to the recording (pauses + speaking rate + repeated "फैक्ट नंबर" sound match).
4. `python3 render.py scene.json build/ build/short.mp4` — 1080x1920, 30 fps, Devanagari captions, -14 LUFS.
5. `bash host_video.sh build/short.mp4 <slug>` — pushes to this repo, prints the raw URL for vidIQ import.
6. vidIQ: `vidiq_video_upload(url)` → `vidiq_social_post_draft_create` (YouTube, public, title/description/tags from `meta/<slug>.json`) → show the user → publish only after "post it".

`tts.py` (Kokoro, free) is the fallback when there is no recording.
Published Shorts are logged in `meta/`.
