#!/usr/bin/env bash
# Push a rendered Short to a public GitHub repo and print a raw URL vidIQ can import.
# Usage: host_video.sh <video.mp4> <slug> [owner/repo]
set -euo pipefail
VIDEO="$(realpath "$1")"; SLUG="$2"; REPO="${3:-Lokesh-DataScience/shorts-assets}"
DIR="${SHORTS_ASSETS_DIR:-/home/claude/shorts-assets}"
if [ ! -d "$DIR/.git" ]; then
  git clone -q --depth 1 "https://github.com/$REPO.git" "$DIR"
fi
cd "$DIR"
git pull -q --rebase || true
NAME="videos/$(date -u +%Y%m%d-%H%M)-$SLUG.mp4"
mkdir -p videos
cp "$VIDEO" "$NAME"
git add "$NAME"
git -c user.name="shorts-bot" -c user.email="shorts-bot@users.noreply.github.com" commit -qm "add $NAME"
git -c push.negotiate=true push -q
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
URL="https://raw.githubusercontent.com/$REPO/$BRANCH/$NAME"
# wait until the raw URL serves the file (CDN can lag a few seconds)
for i in $(seq 1 20); do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -I "$URL") && [ "$CODE" = "200" ] && break
  sleep 3
done
curl -sI "$URL" | grep -iE "^(HTTP|content-type|content-length)" >&2
echo "$URL"
