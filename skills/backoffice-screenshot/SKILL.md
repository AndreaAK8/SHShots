---
name: backoffice-screenshot
description: Use when a KB article, review doc, Jira ticket, or guide needs a clean PNG of StoreHub BackOffice (including pre-GA / flag-gated screens), or when Playwright/headless capture hits the Google login wall on storehubhq.com. Captures the writer's own logged-in Chrome on macOS with built-in tools only — no CleanShot, no paid apps.
---

# BackOffice Screenshot (macOS, no paid tools)

## Overview

Capture the **writer's real, logged-in Chrome window** using macOS-native
`screencapture` + AppleScript, then annotate in the locked StoreHub style
with `scripts/annotate.py`. This is the only route that shows pre-GA /
flag-gated BackOffice screens: a separate browser context (Playwright,
incognito, headless) has no session and dies at Google OAuth — and feature
flags are tied to the writer's account anyway.

**Flow:** find the Chrome window BY URL → wait for load → locate elements →
warn the writer (hands-off window) → capture full screen → crop to window →
strip browser chrome → VERIFY by reading the PNG → annotate → deliver.

**Never** ask for, type, or store a login. The writer logs in themselves;
this skill only drives an already-authenticated window.

## When NOT to use

- Public pages where any session works → Playwright is fine.
- The shot needs to land in a Lark Doc → capture with this skill first, then
  `lark-cli docs +media-insert --selection-with-ellipsis "<placeholder text>"`
  to insert it right after a `[SCREENSHOT: …]` placeholder paragraph.

## One-time permissions (fresh Mac)

1. **Automation → Google Chrome** — probe:
   `osascript -e 'tell application "Google Chrome" to get title of active tab of front window'`
   A title back = ready. Error -1743 = approve the prompt, retry.
2. **Screen Recording** for the terminal app — FAILS SILENTLY as a pure-black
   or wallpaper-only PNG. Grant in System Settings → Privacy & Security →
   Screen & System Audio Recording, then RESTART the terminal app.
   **macOS 26 silently re-revokes this periodically** — if captures suddenly
   go black mid-session, have the writer open that Settings panel; just
   visiting it usually refreshes the grant WITHOUT a restart.
3. **Chrome: Allow JavaScript from Apple Events** — needed for load checks
   and element targeting. The View → Developer menu toggle sometimes doesn't
   stick; the reliable route is:
   `defaults write com.google.Chrome AllowJavascriptAppleEvents -bool true`
   then fully quit + reopen Chrome.

## The procedure

```bash
# 1. Find the window BY URL — never trust "front window" (the writer is
#    usually browsing something else in front). Get a STABLE window id:
osascript -e '
tell application "Google Chrome"
  repeat with w in windows
    repeat with j from 1 to count of tabs of w
      if URL of tab j of w contains "<url-fragment>" then return (id of w) & "," & j
    end repeat
  end repeat
end tell'
# -> "WID,TIX". Use "window id WID" + "tab TIX" from here on. Window INDEX
#    numbers reshuffle every time the writer clicks — ids do not.

# 2. Probe the page through that exact tab (readiness + geometry):
osascript -e 'tell application "Google Chrome" to execute tab TIX of window id WID javascript "JSON.stringify({ready:document.readyState,w:innerWidth,h:innerHeight,dpr:devicePixelRatio})"'
#    innerWidth vs the window's point-width gives the writer's zoom level —
#    e.g. 1920 CSS px in a 1440-pt window = 75% zoom. ALL coordinate math
#    depends on this; re-probe if the writer may have changed zoom.

# 3. Locate elements to annotate — getBoundingClientRect through the same
#    channel. Find by text, not by brittle selectors:
#    Array.from(document.querySelectorAll('button')).find(b=>/apply/i.test(b.textContent))
#    If the DOM query can't reach it (iframe / odd layer): capture first,
#    crop the region, READ the image, and locate it by eye instead.

# 4. TELL THE WRITER before touching the screen: "I need ~25s, hands off."
#    Then raise the window (by id), scroll, settle, capture FULL SCREEN:
osascript -e 'tell application "Google Chrome"
  set active tab index of window id WID to TIX
  set index of window id WID to 1
  activate
end tell'
sleep 1
screencapture -x /tmp/full.png
#    Re-raise before EVERY shot in a batch — the writer may have clicked.

# 5. Crop to the window in Python (PIL), then strip browser chrome:
#    window bounds in points (x1,y1,x2,y2) -> img px = points * dpr
#    crop_browser_chrome() in scripts/annotate.py strips the 87-pt bar
#    (auto-detects Retina by comparing PNG width to window point-width).

# 6. VERIFY — Read the PNG. Confirm it shows the right page (not Lark, not
#    another Chrome window, not a spinner, not black). Re-shoot if not.
#    This catches the writer photobombing mid-batch — normal, just redo.

# 7. Restore: switch the window's active tab back to whatever the writer
#    had, and re-activate the app that was frontmost before you started
#    (read it first via System Events "first process whose frontmost is true").
```

### Why full-screen + crop, not `screencapture -R`

`-R` region capture starts failing with "could not create image from rect"
for ANY rect once a second display joins (especially arranged at negative
coordinates). Full-screen + PIL crop is display-safe and gives identical
output. Don't fight `-R`.

### Coordinate math (memorize this)

```
factor = png_width / innerWidth          # CSS px  -> image px (1.5 at 75% zoom on Retina)
img_x  = css_x * factor
img_y  = (css_y - scrollY) * factor      # rects are viewport-relative after scroll
points * dpr = image px                  # window geometry -> image px
```

### Full-page shots (page taller than viewport)

Capture at scroll 0 and at max scroll, then stitch. Cut the top slice ABOVE
its horizontal scrollbar and any fixed/floating button (support launcher),
and start the bottom slice at the matching CSS offset — otherwise the seam
shows a scrollbar band and the floating button appears twice.

### Clicking things (dropdowns, filters)

React UIs ignore bare `el.click()`. Dispatch the full sequence:
`pointerdown, mousedown, pointerup, mouseup, click` (bubbling MouseEvents).
Re-measure rects AFTER opening — hidden controls report 0×0 until visible.

## Annotation (locked style — never freestyle)

`scripts/annotate.py` — all marks #EA3329 red, antialiased:

| Flag | Draws |
|---|---|
| `--box X,Y,W,H` | rounded-corner rectangle (8px radius, 4px stroke) |
| `--arrow TIPX,TIPY[,left\|right]` | tapered arrow — thin tail, solid head, tip lands at that pixel |
| `--blur X,Y,W,H` | gaussian smudge for sensitive data (emails, phones, names) |
| `--crop-chrome POINTS` | strip browser bar (pass window width in points) |
| `--round RADIUS` | rounded screenshot corners, transparent (24 at 1x / 48 Retina) |
| `--scale N` | 2 on Retina (default) so strokes match the 1x look |

Coordinates are IMAGE pixels. Blur the operator's name in the top bar when
the account label shows a real person. Always blur real staff/customer data.

## Quick reference

| Need | Do |
|---|---|
| Writer must click something first | They navigate + say "go"; you run capture only |
| Several shots, one page | ONE hands-off batch: scroll → capture → scroll → capture; re-raise window each time |
| `[SCREENSHOT: …]` placeholders in a Lark draft | Capture each per its instruction, then `lark-cli docs +media-insert` after each placeholder; count `<img` tags before/after to prove no duplicates |
| Element in unreachable DOM | Visual fallback: crop region → Read → locate by eye |
| Window-ID capture (`-l`) | Don't — Chrome's AppleScript id ≠ CGWindowID |

## Common mistakes

- **Trusting window indexes** — they reshuffle whenever the writer clicks. Resolve by URL → window **id** once, use the id throughout.
- **Capturing without warning the writer** — they switch to Lark mid-shot and you photograph Lark. Announce the hands-off window; verify every frame.
- **Capturing before the SPA settles** — `readyState complete` ≠ charts rendered. Settle ~1s after scroll/raise AND visually verify.
- **Assuming requested window bounds** — Chrome clamps `set bounds`; always read back the ACTUAL bounds for crop math.
- **Forgetting zoom** — coordinate math breaks silently if the writer changes Chrome zoom between probe and capture. Re-probe `innerWidth`.
- **Trying Playwright on storehubhq.com** — separate context → OAuth wall. Don't burn time on it.
- **Annotating with raw PIL polygons elsewhere** — they alias (jaggy edges). Use `annotate.py`; it supersamples 4x.
