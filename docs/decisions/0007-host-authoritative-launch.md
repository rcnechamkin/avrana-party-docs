---
title: "ADR 0007: The host starts the game"
description: Why only the Party Host starts a party game, and how Party Home learned to follow Party Core instead of letting every phone pick its own game.
sources:
  - avrana-party:docs/adr/0007-host-authoritative-launch.md
  - avrana-party:docs/adr/0011-party-console-model.md
  - avrana-party:avrana/party/core.py
  - avrana-party:web/party/lib/party-mode.js
  - avrana-party:web/party/lib/party-client.js
verified: 2026-10-09
---

# ADR 0007: The host starts the game, and Party Home follows

!!! abstract "At a glance"
    **Decided:** 2026-09-28 · **Status:** <span class="avr-badge deployed">Deployed</span>; its reconnect rule and manual Join were replaced by [ADR 0011](0011-party-console-model.md)
    Only the Party Host can start a party game. Every other phone learns about the start from
    Party Core and moves into the game on its own.

## The problem

Party Core already knew who was in the Party, who was hosting and which game session was
running, and it refused a launch from anyone but the host
([ADR 0006](0006-party-session-protocol.md)). But Party Home, the page phones open first, ignored
it: each phone picked a game tile and opened the game by itself. Nobody's choice was
authoritative, two phones could end up in two different games, and being host changed nothing.

## What was decided

- **Party mode switches on only when there is a Party.** Party Home asks Party Core for the
  Party's state at start-up. Only a well-formed answer turns Party mode on; anything else leaves
  the ordinary catalog page unchanged. Nothing is guessed from the browser type.
- **Party Core says which games are party games; the catalog says where they open.** No game id
  is hard-coded into Party Home.
- **Only the host starts a party game.** The host's tile reads "Start for everyone"; others see a
  disabled "The host starts it". Party Core re-checks and refuses anyone else. If the Party had
  merely moved on a moment earlier (someone joined, a phone woke), Party Home retries once.
- **Sync uses the existing long poll.** Each Party Home keeps one request open that Party Core
  answers as soon as anything changes, or after about 20 seconds. It doubles as the phone's
  "still here" heartbeat.
- **Followers move only on a committed start.** When a phone sees that the game is actually
  running, it announces "The host started BLUFF. Joining…" and opens it a moment later.
- **Host succession never ends the game.** A player in the running game counts as present, so a
  host who leaves mid-game hands over at once to the earliest-joined present member. The game
  and its players are untouched.

The original also had a **reconnect rule**: a reloaded or reopened page went into the game unless
that tab remembered leaving on purpose, in which case it only offered "Rejoin". Joining and
leaving the Party were explicit buttons. These no longer hold (see [Later changes](#later-changes)).

## Why this way

**No WebSocket or server-sent events.** Party Core's state carries a version number that rises
with each change, so the long poll already gives ordered, repeatable, resumable updates. It
already worked through the web server and the service worker's never-cache rule. A new channel
would have added something to deploy and nothing the poll lacked.

**Wait for the committed start.** A host start passes through "launching" and then "active" once
the game accepts. Followers move only on the second, so nobody rushes into a game that failed
to start.

**Count players as present.** The earlier succession rule skipped players, which left the host
role empty mid-game until someone opened Party Home.

## What it means in practice

The host taps a game and every phone on Party Home follows. While a party game is on, the other
party games are closed to everyone ("Party is playing BLUFF") and Party Core refuses a second
launch as busy. Standalone titles were left alone. A page already *inside* a game still did not
follow the host to a different game; [ADR 0008](0008-party-navigation.md) closed that gap the
next day.

## Later changes

- **2026-09-29, [ADR 0008](0008-party-navigation.md):** game pages follow Party Core too, and
  the host can switch games in one step.
- **[ADR 0011](0011-party-console-model.md), the console model:** replaced the reconnect rule and
  the Join and Leave buttons. Every member page now goes wherever the Party is, on load and on
  every change, and presence is automatic once a phone has a profile.

**Still in force from this ADR:** host-only start; Party Core decides and the catalog says where
a game opens; the versioned long poll; moving only on committed changes; and succession that
never ends a game. In current source the successor also prefers a member on the trusted HTTPS
connection ([ADR 0012](0012-limited-mode-party-survives-https-loss.md)).

## Where it stands today

<span class="avr-badge deployed">Deployed</span> with Party Core v0 and part of the last verified
deployment (2026-09-29). When the ADR was written, production had no Party service; that
deployment added it.

The reconnect rule is gone from current source: the "Rejoin", "Join the party" and "Leave the
party" buttons and the tab memory behind them have been removed from Party Home. Their
replacement, the console model, is <span class="avr-badge source">In source</span> and
<span class="avr-badge reported">Owner-reported</span> as deployed.

Not yet checked on real phones: the automatic follow on iPhone Safari and Android Chrome, phones
that slept, and the long poll through the appliance's real web server.

## Related decisions

- [ADR 0006: the session protocol](0006-party-session-protocol.md), which this amends.
- [ADR 0008: Party navigation](0008-party-navigation.md), which extends it to game pages.
- [ADR 0011: the console model](0011-party-console-model.md), which replaces its reconnect rule.
- [The Party](../architecture/party.md), for hosting and presence today.
