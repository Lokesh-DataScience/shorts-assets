#!/usr/bin/env bash
# One-time setup per session: Hindi+Latin fonts (from npm/fontsource) and Python deps.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
pip install -q --break-system-packages fonttools brotli soundfile numpy pillow 2>/dev/null || true
mkdir -p "$HERE/fonts"
if [ ! -f "$HERE/fonts/Baloo2-ExtraBold.ttf" ] || [ ! -f "$HERE/fonts/Mukta-Bold.ttf" ]; then
  T="$(mktemp -d)"; cd "$T"
  npm pack @fontsource/baloo-2 @fontsource/mukta >/dev/null 2>&1
  for f in *.tgz; do tar xzf "$f" --wildcards '*-latin-*-normal.woff2' '*-devanagari-*-normal.woff2'; done
  python3 - "$HERE/fonts" <<'EOF'
import sys
from fontTools.ttLib import TTFont
from fontTools.merge import Merger
out = sys.argv[1]
for fam, wt, name in [("baloo-2", "800", "Baloo2-ExtraBold"), ("mukta", "700", "Mukta-Bold")]:
    paths = []
    for sub in ("devanagari", "latin"):
        f = TTFont(f"package/files/{fam}-{sub}-{wt}-normal.woff2"); f.flavor = None
        p = f"{fam}-{sub}.ttf"; f.save(p); paths.append(p)
    Merger().merge(paths).save(f"{out}/{name}.ttf"); print("font", name)
EOF
fi
which ffmpeg >/dev/null && echo "ffmpeg ok"
