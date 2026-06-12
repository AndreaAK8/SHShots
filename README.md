# BackOffice Screenshot

Claude Code plugin for StoreHub KB writers: capture clean PNGs of BackOffice — **including pre-GA / flag-gated screens** — straight from your own logged-in Chrome on macOS. Built-in tools only. No CleanShot, no paid apps, no Playwright login wall.

## Install

In Claude Code:

```
/plugin marketplace add AndreaAK8/SHShots
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
