"""Cut a person out of a photo (background removed) and crop to the subject.

Usage: python3 cutout.py photo.jpg out.png
Uses rembg with the u2net_human_seg model (download once into ~/.u2net from the rembg GitHub release).
Only use photos the user supplied (official portraits are the safest for copyright).
"""
import sys
from PIL import Image
from rembg import remove, new_session

src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
if max(im.size) > 1600:
    im.thumbnail((1600, 1600), Image.LANCZOS)
out = remove(im, session=new_session("u2net_human_seg"), alpha_matting=True,
             alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=15)
bbox = out.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
if bbox:
    out = out.crop(bbox)
out.save(dst)
print(dst, out.size)
