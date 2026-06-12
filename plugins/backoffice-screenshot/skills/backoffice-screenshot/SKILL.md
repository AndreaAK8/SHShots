---
name: backoffice-screenshot
description: Use when a KB article, review doc, or guide needs a clean PNG of StoreHub BackOffice (including pre-GA / flag-gated screens), or when Playwright/headless capture hits the Google login wall on storehubhq.com. Captures the writer's own logged-in Chrome on macOS with built-in tools only — no CleanShot, no paid apps.
---

# BackOffice Screenshot (macOS, no paid tools)

## Overview

Capture the **writer's real, logged-in Chrome window** using macOS-native
`screencapture` + AppleScript. This is the only route that shows pre-GA /
flag-gated BackOffice screens: a separate browser context (Playwright,
incognito, headless) has no session and dies at Google OAuth — and feature
flags are tied to the writer's account anyway.

**Flow:** drive Chrome to the page (or let the writer navigate) → wait for
load → capture just the window → verify the PNG.

## When NOT to use

- Public pages where any session works → Playwright is fine.
- The shot needs to land in a Lark Doc and you have that pipeline → capture
  with this skill first, then upload (`lark-cli docs +media-insert`).

## The procedure

```bash
# 0. One-time permission probe. TWO permissions are involved on a fresh Mac:
#    (a) Automation → Google Chrome:
osascript -e 'tell application "Google Chrome" to get title of active tab of front window'
#    A title back = ready. Error -1743 = approve the Automation prompt, retry.
#    (b) Screen Recording (for screencapture): FAILS SILENTLY — you get a PNG
#    of the wallpaper with no window in it. If that happens: grant the
#    terminal app Screen Recording in System Settings, then RESTART the
#    terminal app (the grant does not take effect until restart), redo 4-6.
#    Also confirm with the writer that the FRONT Chrome window is her
#    logged-in work profile — AppleScript drives "front window" blindly.

# 1. Normalize window size (consistent KB dimensions)
osascript -e 'tell application "Google Chrome"
  activate
  set bounds of front window to {100, 60, 1540, 960}
end tell'

# 2. Navigate the live session (no password handling — it's their login).
#    ASK FIRST. If the writer is mid-work in the active tab, use a NEW tab:
#    osascript -e 'tell application "Google Chrome" to make new tab at end of tabs of front window with properties {URL:"https://<store>.storehubhq.com/<path>"}'
#    Otherwise drive the active tab:
osascript -e 'tell application "Google Chrome" to set URL of active tab of front window to "https://<store>.storehubhq.com/<path>"'

# 3. Wait for load — poll Chrome itself, then settle (SPA fetches data
#    AFTER document-ready; the spinner is the #1 ruined-shot cause)
for i in {1..30}; do
  [ "$(osascript -e 'tell application "Google Chrome" to get loading of active tab of front window')" = "false" ] && break
  sleep 1
done
sleep 2

# 4+5 MUST run as ONE shell invocation (the $x1.. variables don't survive
#    across separate calls). Pick an explicit absolute output path.
osascript -e 'tell application "Google Chrome" to activate'; sleep 0.5
IFS=', ' read -r x1 y1 x2 y2 <<< "$(osascript -e 'tell application "Google Chrome" to get bounds of front window')"
out="$HOME/Desktop/bo-shot-$(date +%H%M%S).png"
screencapture -x -R "${x1},${y1},$((x2-x1)),$((y2-y1))" -t png "$out"

# 6. VERIFY — open/Read the PNG. Confirm the real content rendered
#    (not a spinner, not a login page, no notification banner). Re-shoot if not.
```

## Quick reference

| Need | Do |
|---|---|
| Writer must click something first | They navigate + say "go"; you run steps 4–6 only |
| Crop off tab bar/omnibox | Read pixel size first: `sips -g pixelWidth -g pixelHeight "$out"`, substitute the numbers in: `sips --cropOffset 174 0 --cropToHeightWidth $((PIXEL_H-174)) $PIXEL_W "$out" --out "${out%.png}-crop.png"`. Browser chrome is 87 pts → 174 px on Retina, 87 px on a non-Retina external display (pixel width == window width ⇒ non-Retina, use 87) |
| Multiple shots, same session | Repeat 2–6; window stays normalized |
| Window-ID capture (`-l`) | Don't — Chrome's AppleScript id ≠ CGWindowID; `-R` is the reliable route |

## Common mistakes

- **Capturing before the SPA settles** — `loading=false` ≠ table rendered. Keep the 2s buffer AND the visual verify.
- **Hijacking the writer's active tab** — ask, or `make new tab`.
- **Trying Playwright on storehubhq.com** — separate context → OAuth wall. Don't burn time on it.
- **CleanShot clipboard route** — times out even where installed (PNG never lands on the clipboard). This skill exists to not need it.
- **Forgetting Retina** — the PNG is 2× the point size; crop math doubles too.
