#!/bin/bash
# Capture the frontmost Chrome window -> chrome-stripped content PNG.
# Usage: capture_win.sh OUT.png [X1 Y1 X2 Y2 WIDTH_POINTS DPR]
#   X1..Y2 = the window's ACTUAL bounds in points (read them back from
#   AppleScript — Chrome clamps requested bounds).
#   DPR    = display pixel ratio (2 = Retina default, 1 = most externals).
# Defaults match a full-width window at (0,30,1440,806) on a 2x display.
set -e
OUT="$1"
X1=${2:-0}; Y1=${3:-30}; X2=${4:-1440}; Y2=${5:-806}; WPTS=${6:-1440}; DPR=${7:-2}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TMP=$(mktemp /tmp/cap-XXXX.png)
screencapture -x "$TMP"
SCRIPT_DIR="$SCRIPT_DIR" python3 - "$TMP" "$OUT" "$X1" "$Y1" "$X2" "$Y2" "$WPTS" "$DPR" <<'EOF'
import os, sys
sys.path.insert(0, os.environ['SCRIPT_DIR'])
from PIL import Image
from annotate import crop_browser_chrome
full = Image.open(sys.argv[1])
x1, y1, x2, y2, wpts, dpr = map(int, sys.argv[3:9])
win = full.crop((x1 * dpr, y1 * dpr, x2 * dpr, y2 * dpr))
win = crop_browser_chrome(win, wpts)
win.save(sys.argv[2])
print(sys.argv[2], win.size)
EOF
rm -f "$TMP"
