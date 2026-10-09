---
title: "ADR 0002: Avrana Party is a party platform"
description: The founding decision that one persistent Party owns identity, session and navigation, while games consume those services through a small optional contract.
sources:
  - avrana-party:docs/adr/0002-party-platform.md
  - avrana-party:avrana/party/core.py
  - avrana-party:avrana/party/identity.py
  - avrana-party:avrana/contracts/game.py
  - avrana-party:docs/SYSTEM.md
verified: 2026-10-09
---

# ADR 0002: Avrana Party is a party platform, and games consume its services

!!! abstract "At a glance"
    **Decided:** 2026-09-24 · **Status:** <span class="avr-badge accepted">Accepted direction</span> · mechanisms proposed at the time and later built through ADRs 0006–0011 · amended 2026-09-24 and 2026-10-02
    Avrana Party is one Party that moves between games: "the game may change; the party does
    not". The Party owns identity, session, social features and navigation; games consume them.

## The problem

By September 2026 the appliance ran several separate game runtimes, each with its own idea of a
player. LAN Games, a collection of 28 browser games, identified players by a token the browser
generated for itself, kept names and avatars only in the browser, let any player start a game or
clear the chat, and sent each phone into each game on its own. BLUFF was building presence,
reconnect and spectators inside the game. The PlayStation stream minted its own slot tokens, and
the arcade had no identity at all.

The owner's direction was a single party that moves between games, with Avrana owning identity,
session, social features, progression, navigation and player management. Keeping per-game
identity would multiply exactly the systems the product meant to unify.

## What was decided

1. **A persistent Party** (members, host, seats, current game, queue, teams, chat) outlives any
   single game, and navigation is synchronized across it.
2. **Identity is layered.** Device (a recognized browser), Profile (an optional persistent
   person), Presence (being in this party), Seat (a place in this game), Role (host, player or
   spectator) and Persona (how someone is displayed) are separate. Games receive a game key and a
   persona, never a device token or profile secret ([ADR 0003](0003-ids-and-keys.md)).
3. **Guest-first, browser-first, offline-first.** Profiles are optional, the captive portal is a
   convenience, and nothing needs the internet.
4. **Admin is not Host.** The System Admin is a PIN-protected appliance role. The Party Host is a
   temporary, transferable party role with no system powers.
5. **A small, optional integration contract, not a framework**: a capability manifest, a ticket
   handshake as the first WebSocket message, an event sink that records provenance, and a small
   script that follows Party navigation. A game using none of them keeps working.
6. **Every statistic records its provenance**, game-reported or platform-observed. Emulated games
   produce no results without a per-game adapter, and taking part never counts as a win.
7. **Not a gameplay framework.** Rules, state, rendering and networking stay with each game;
   platform contracts grow only when two consumers need them.

The proposed mechanisms were a separate small party service on the same web origin as
everything else, a server-issued device cookie, full-page navigation driven by a small script,
and a thin bridge in the LAN Games fork.

## Why this way

The ADR records the alternatives it rejected:

- **Per-game identity**: every game re-implements lobby, reconnect and identity, and cross-game
  features such as teams, history and voting become impossible.
- **The party inside the LAN Games server**: simpler, but the party would die with that process
  and the other runtimes would depend on it. Kept as a fallback.
- **An iframe shell around every game**: games assume they own the page (safe areas, fullscreen,
  audio unlocking, iOS gestures, service workers). It may return for overlays such as chat.
- **A single-page app that absorbs every game**: a rewrite of every game.
- **Cloud accounts**: contrary to offline-first and setup-free.

## What it means in practice

New games should not build their own login, profile store, chat, reconnect, team or spectator
systems; they wait for or contribute to the platform's. The ADR also noted that the LAN Games
token would have to be replaced without breaking the live service, and that a new party process
had to stay small on a Raspberry Pi then suffering power problems.

## Later changes

**2026-09-24, same day.** The owner locked several product decisions, refining rather than
reversing the above: one appliance runs one party; a TV is optional and each game declares
whether it needs one; the host is disposable (grace period, simple succession, voluntary
transfer, and a returning former host does not reclaim the role); late joiners spectate by
default; physical seating is not a platform concept; installation is open, with no store; no
app or captive portal is required; native games should use each player's private screen; and
version 1.0 is for the owner, to prove the experience before any commercialization.

**2026-10-02.** Where this amendment differs from the original, it governs:

- One Party runs **one active activity at a time** ([ADR 0011](0011-party-console-model.md),
  [ADR 0014](0014-native-games-isolated-lan-games-retired.md)).
- **LAN Games is retiring as a runtime** (ADR 0014); its browser token is retired, not migrated.
- **Only the Party writes durable records** of people, results, history and stats. Games decide
  outcomes and report them, and receive only session-scoped authority
  ([ADR 0006](0006-party-session-protocol.md)).
- **Separate browser origins** replace the one-origin assumption
  ([ADR 0013](0013-party-and-game-browser-origins.md)).
- **Trusted HTTPS is preferred, not required**
  ([ADR 0012](0012-limited-mode-party-survives-https-loss.md)).

## Where it stands today

- <span class="avr-badge deployed">Deployed</span> Party Core as a separate small service, with
  a server-issued device cookie, host succession and Party-synchronized navigation (ADRs
  0006–0010, server-side verified 2026-09-29).
- <span class="avr-badge source">In source</span> The game contract that serves as the capability
  manifest ([ADR 0004](0004-full-mode-contracts-and-providers.md)) and a result envelope for
  reporting outcomes ([ADR 0015](0015-game-result-envelope.md)).
- <span class="avr-badge planned">Planned</span> Profiles, durable history and statistics, the
  provenance-tagged event sink and the System Admin role; none exists in code. Party state is in
  memory, and only hashed device tokens persist.

See [The Party](../architecture/party.md) and the fuller design in
[Party platform](../design/party-platform.md).

## Related decisions

- [ADR 0003](0003-ids-and-keys.md): identifiers and credentials.
- [ADR 0006](0006-party-session-protocol.md): Party Core and the session protocol.
- [ADR 0011](0011-party-console-model.md): the console model.
- [ADR 0012](0012-limited-mode-party-survives-https-loss.md), [ADR 0013](0013-party-and-game-browser-origins.md)
  and [ADR 0014](0014-native-games-isolated-lan-games-retired.md): the 2026-10-02 decisions.
