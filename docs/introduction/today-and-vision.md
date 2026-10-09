---
title: Today versus the vision
description: What Avrana Party can do now, what it is designed to do, and how to tell the two apart.
sources:
  - avrana-party:docs/ROADMAP.md
  - avrana-party:docs/SYSTEM.md
  - avrana-party:docs/GAME-PLATFORM-ARCHITECTURE.md
  - avrana-party:docs/AVRANA-EXPERIENCE.md
  - avrana-party:docs/adr/0014-native-games-isolated-lan-games-retired.md
verified: 2026-10-09
---

# Today versus the vision

The engineering repositories hold two kinds of writing side by side. Some documents describe
what the code does. Others describe what the project intends to become, sometimes in detail.
Both are valuable, but a newcomer can easily mistake a well-written design for a shipped
feature. This page draws the line for the product as a whole. The
[project status](../status/index.md) page goes into more detail.

## How maturity is labelled on this site

--8<-- "includes/maturity-labels.md"

An ADR is an *Architecture Decision Record*: the project's written record of a decision. See
[Decision records in brief](../architecture/decisions.md).

## What exists today

These are the headline capabilities as of October 2026. The last *verified* deployment dates
from 29 September 2026. Source has moved well ahead of it since then. The
[project status](../status/index.md) page has the full, dated picture and the evidence behind
each item.

- <span class="avr-badge deployed">Deployed</span> **Broadcast its own Wi-Fi** and serve the
  Party over trusted HTTPS at `party.avrana.net` with no internet connection.
- <span class="avr-badge deployed">Deployed</span> **Run Party Core**, which tracks membership,
  the host role with automatic succession, and the session with the current game.
- <span class="avr-badge deployed">Deployed</span> **Launch BLUFF from Party Home** with a
  Play-or-Watch setup and a host-only Start. BLUFF is a server-authoritative hidden-role card
  game for 2–6 players, with bots, timers and reconnect.
- <span class="avr-badge deployed">Deployed</span> **Stream an arcade game.** *Gauntlet II*
  runs in an emulator on the appliance, its video is streamed to phones over WebRTC, and the
  phones act as gamepads. The Party starts and stops the emulator.
- <span class="avr-badge reported">Owner-reported</span> **The console model.** Phones join the
  Party automatically, the Party has one authoritative location that the host moves, and
  results stay on screen until the host moves on. It is in source and the owner reports it as
  deployed, but there is no dated deployment record and no real-phone verification yet.
- <span class="avr-badge source">In source</span> **A redesigned Party shell**, four arcade
  controller seats, and **the machinery for isolated native games**. That machinery has been
  proven with a test-only stand-in game on a CI runner. No product game uses it yet.

## What it is designed to become

These are commitments or strong directions in the engineering documents. They are not built,
or not yet complete:

- <span class="avr-badge accepted">Accepted direction</span> **Limited Mode.** If the
  certificate expires or a phone cannot use trusted HTTPS, the Party keeps working over plain
  HTTP with clearly explained limitations. Part of it is in source; none of it is deployed.
- <span class="avr-badge accepted">Accepted direction</span> **Separate browser origins** for
  the Party and for games, so that game code can never act as the player inside the Party.
- <span class="avr-badge accepted">Accepted direction</span> **Isolated native games and
  separate service identities.** Each game becomes its own process with its own system user,
  keys and state. The LAN Games fork <span class="avr-badge retiring">Retiring</span> stops
  being the runtime.
- <span class="avr-badge accepted">Accepted direction</span> **Party-owned results and
  history.** Games already report results in a versioned envelope. Storing a durable history,
  with profiles to attach it to, is still to be designed.
- <span class="avr-badge planned">Planned</span> **A game SDK and the `.avrgame` package
  format.** These are deliberately left open until two more games (Checkers, then Spades)
  have proven the native boundary.
- <span class="avr-badge experimental">Experimental</span> **Emulated multiplayer with Personal
  Viewports**, where each phone shows its own player's part of a split-screen game.
- <span class="avr-badge planned">Planned</span> **Open game installation and a community
  ecosystem**, with appliance-controlled grants and trust tiers. No store.
- <span class="avr-badge planned">Planned</span> **Appliance readiness**: measured boot time,
  battery runtime, cooling, power-loss recovery and the real number of phones the access
  point can serve.

## Why the line is drawn so carefully

The engineering repositories are maintained largely by coding agents directed by the project
owner. A process like that produces documentation quickly, and it can also produce confident
prose about things that do not exist yet. The project guards against this with explicit
rules: a merged pull request is not a deployment; a request made with `curl` is not a phone
test; a simulation is not a measurement. This site follows the same rules. If it calls
something deployed, there is dated evidence behind that. If the evidence is missing, the site
says so.

Next: the [architecture overview](../architecture/index.md).
