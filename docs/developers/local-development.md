---
title: Local development
description: Running the Party interface, a simulated Party and the offline test suites on your own machine, and what each kind of test does and does not prove.
sources:
  - avrana-party:README.md
  - avrana-party:CONTRIBUTING.md
  - avrana-party:docs/TESTING.md
  - avrana-party:package.json
  - avrana-party:avrana/web/devserver.py
  - avrana-party-games:CONTRIBUTING.md
  - avrana-party:docs/GENERATED.md
verified: 2026-10-09
---

# Local development

You do not need a Raspberry Pi to work on Avrana Party. This page condenses the setup from the
Party repository's README, contribution guide and testing guide. Those files are authoritative,
list platform-specific details, and are linked at the foot of this page. [Testing](testing.md)
explains the test suites in more depth.

## Prerequisites

- **Node.js 22** (CI pins a specific 22.x release) and npm
- **Python 3.12 or newer**
- Git
- For the browser suites: Playwright's Chromium (`npx playwright install chromium`)
- On Linux, to run every test that CI runs: `nginx` and `logrotate`

## Run the Party interface

```sh
git clone https://github.com/rcnechamkin/avrana-party.git
cd avrana-party
npm ci
npm run dev
```

Open <http://127.0.0.1:8180/party/>. The development server serves Party Home with the same
security headers as the appliance, a stub games hub and a simulated arcade status. In this
default form it does **not** start Party Core, real games or an emulator.

The development server has a few useful options:

| Command | What you get |
|---|---|
| `python3 -m avrana.web.devserver --port 8180` | The default: the shell, stubs and simulated arcade status (what `npm run dev` runs) |
| `… --party` | A real, in-memory **Party Core** behind `/party/api/`, with stub game pages. This is the local way to try the Party flow by hand: open several browser windows as different "phones" |
| `… --test-controls` | Test switches for the fake arcade, a Party reset, and a way to advance the Party's clock |
| `… --game-origin` | Serves game pages from a second origin, to exercise the separate-origin design |

Where only `python` is installed rather than `python3`, as on some Windows setups, run the
module directly with `python -m …`.

## Run the checks

The everyday offline lane:

```sh
npm run check:repo          # repository structure, documentation links, generated files
npm run test:unit           # Python unit tests
npm run test:modules        # Node tests for browser-side modules
npx playwright install chromium
npm run test:offline-browser  # Chromium at phone sizes against the dev server
npm run test:party-browser    # several browser "phones" against a real Party Core
```

`npm run test:offline` runs the last four together. CI also runs real nginx against the
committed site file, the Party ↔ Games contract checker and the cross-repository suites.

!!! danger "`npm test` is not the offline suite"

    `npm test`, `test:all`, `soak` and `fault` target the **live appliance** over its Wi-Fi.
    They need the hardware and explicit authorization. Use the offline commands above for
    normal development.

## Testing with the real games server

Full browser-game sessions, with real BLUFF and real Party Core, need a checkout of the Games
repository next to the Party repository:

```sh
# In avrana-party-games: set up its virtual environment
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt

# In avrana-party:
AVRANA_GAMES_REPO=../avrana-party-games \
AVRANA_PROVIDER_PYTHON=../avrana-party-games/.venv/bin/python \
npx playwright test -c playwright.provider.config.ts

# And the contract check:
python3 tools/contract_check.py --games ../avrana-party-games
```

## What a passing test proves

The project uses three **evidence tiers**, and it is strict about not mixing them up:

| Tier | What it is | Where it runs |
|---|---|---|
| **1: pure** | No appliance, no network, no real browser | Laptop, cloud, CI |
| **2: simulated Party** | Real nginx with the committed site, real Chromium against the dev server on `localhost` | Laptop, cloud, CI |
| **3: hardware** | The Pi, real phones, the access point, the video encoder, power | On the Party Wi-Fi only |

Tier 2 browser tests at phone sizes are useful, but **they are not evidence that something
works on a real iPhone or Android phone**. Results are never reported at a higher tier than the
one they were collected at. Deployed server-side checks are a separate category again: they show
the services work, not that the experience works in someone's hand.

## Generated files

Some committed files are generated: the built CSS, icons, avatars, artwork and the compiled
catalog. Change their sources and regenerate them with the npm scripts; never edit the
generated files by hand. `npm run check:repo` fails if they are out of date. The complete list,
with the command that regenerates each file, is `docs/GENERATED.md` in the Party repository.

## Working on the Games repository

The Games repository has its own Python test suite, static checks and CI. The everyday commands,
from its root:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
python ops/export_avrana_catalog.py --check provider/catalog.json
bash ops/check_static.sh
```

With a sibling Party checkout, it also runs the cross-repository tests, which its CI requires.
Every Markdown file in that repository needs an entry in its own documentation manifest, as in
the Party repository. See [Testing](testing.md) for what each kind of test proves.
