# BackOffice Screenshot

**This repo IS the plugin** — one independent Claude Code plugin, nothing else.

For StoreHub KB writers: capture clean, **annotated** PNGs of BackOffice — **including pre-GA / flag-gated screens** — straight from your own logged-in Chrome on macOS. Built-in tools only. No CleanShot, no paid apps, no Playwright login wall. Use the shots anywhere: KB articles, Jira tickets, Lark docs, training decks.

📖 **New here? Read the [User Guide](docs/SHShots-user-guide.html)** (download the file and open it in a browser — install, one-time permissions, daily use, troubleshooting, FAQ).

**What's included:**
- Window capture targeted by URL (never grabs the wrong window or your bookmarks)
- Full-page capture with seamless stitching for pages taller than the screen
- Locked annotation style: #EA3329 red rounded boxes + tapered arrows (antialiased)
- Blur option for sensitive data (staff emails, phones, names)
- Rounded screenshot corners, browser chrome stripped automatically
- Self-verifying: every capture is checked before delivery
- Lark Doc insertion at `[SCREENSHOT: …]` placeholders (needs `lark-cli`)

## Install

In Claude Code — first time only, point Claude Code at this repo:

```
/plugin marketplace add AndreaAK8/SHShots
```

Then install (and later update) with one command:

```
/plugin install backoffice-screenshot@shshots
```

## First run (one-time, macOS)

Two permission prompts will appear — the skill walks you through both:

1. **Automation → Google Chrome** — approve when prompted.
2. **Screen Recording** for your terminal app — grant in System Settings, then **restart the terminal** (the grant doesn't take effect until restart).

## Use

Just ask Claude for a BackOffice screenshot, e.g.:

> "Capture the Promotions list page in BackOffice"

Claude drives your already-logged-in Chrome window, waits for the page to fully load, captures just the browser window, and verifies the shot. Your login is never touched — no passwords stored or typed.
