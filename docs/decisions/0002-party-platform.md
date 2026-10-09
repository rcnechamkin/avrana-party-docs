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
    **Decided:** 2026-09-24 · **Status:** <span class="avr-badge accepted">Accepted direction</span> · mechanisms proposed at the time, later built through ADRs 0006–0011 · amended 2026-09-24 and 2026-10-02
    Avrana Party is one Party that moves between games: "the game may change; the party does
    not". The Party owns who people are, the session, social features and navigation. Games
    consume those services instead of building their own.

## The problem

By September 2026 the appliance ran several separate game runtimes, and each had its own idea
of what a player was:

- **LAN Games**, a collection of 28 browser games, identified each player by a token the browser
  generated for itself (`wc-token`). Names and avatars lived only in the browser. Any ready
  player could start a game, anyone could change settings or clear the chat, and each phone
  navigated into each game on its own.
- **BLUFF**, the first native game, was adding presence, reconnect grace, autopilot and
  spectators, all inside the game.
- **The PlayStation stream** minted its own slot tokens with a 30-second grace period.
- **The arcade** had no identity at all: first free controller slot, freed on disconnect.
- The PlayStation stream was also served from a different web address from everything else.

The owner's product direction was a single party that moves between games, with Avrana owning
identity, session, social features, progression, navigation and player management. Keeping
per-game identity would multiply exactly the systems the product was meant to unify.

## What was decided

1. **A persistent Party.** The Party has members, a host, seats, a current game, a queue, teams
   and chat, and it outlives any single game. Navigation is synchronized across the Party.
2. **Identity is layered, not one "player" object.** A *device* (a recognized browser), a
   *profile* (an optional, persistent person), a *presence* (being in this party), a *seat* (a
   place in this game), a *role* (host, player or spectator) and a *persona* (how someone is
   displayed) are separate concepts. Games receive a game key and a persona, never a device
   token or profile secret. [ADR 0003](0003-ids-and-keys.md) works this out in detail.
3. **Guest-first, browser-first, offline-first.** Profiles are optional, the captive portal is a
   convenience rather than a dependency, and nothing needs the internet.
4. **The administrator is not the host.** The System Admin is a PIN-protected role for the
   appliance itself. The Party Host is a temporary, transferable party role with no system
   powers.
5. **Games integrate through a small, optional contract, not a framework.** The pieces named
   were a capability manifest, a ticket handshake as the first WebSocket message, an event sink
   that records where each event came from, and a small script that follows Party navigation. A
   game that uses none of these keeps working.
6. **Every statistic records its provenance**: whether it came from the game itself or was only
   observed by the platform. Emulated games produce no results without a per-game adapter, and
   taking part never counts as a win.
7. **Not a universal gameplay framework.** Rules, state, rendering and networking stay with each
   game. Platform contracts grow only when two consumers need the same thing.

The ADR also sketched mechanisms, marked as proposals: a separate small party service on the
same web origin as everything else, a server-issued device cookie, full-page navigation driven
by a small script, a thin bridge in the LAN Games fork, and game manifests derived from the
LAN Games registry.

## Why this way

The ADR records the alternatives and why each was set aside:

- **Keep per-game identity.** Rejected. Every new game would re-implement lobby, reconnect and
  identity, and features that span games (teams, history, voting) would be impossible.
- **Build the party layer inside the LAN Games server.** Simpler, because no tickets would cross
  processes. But the party would die with that process, and the arcade and PlayStation stream
  would depend on it. Kept only as a fallback.
- **An iframe shell that hosts every game.** Rejected for now. Games assume they own the page:
  safe areas, fullscreen, audio unlocking, iOS gestures and service workers. An iframe might
  return for overlays such as chat.
- **A single-page app that absorbs every game.** Rejected, because it means rewriting every
  game.
- **Cloud accounts.** Rejected: the product is offline-first and should need no setup.

## What it means in practice

New games should not build their own login, profile store, chat, reconnect, team or spectator
systems. They wait for, or contribute to, the platform versions. The ADR also noted costs: the
LAN Games browser-generated token would have to be replaced without breaking the live service,
and a new party process had to stay small on a Raspberry Pi that then had power problems.

## Later changes

**Same day (2026-09-24): locked product decisions.** The owner closed several open questions.
They refine the decision rather than reverse it:

- one appliance runs one party, not a multi-tenant server;
- a TV is optional, and a game declares whether it needs one;
- the host is disposable: a reconnect grace period, then simple succession, voluntary transfer,
  and a returning former host does not take the role back;
- late joiners spectate by default, and games can opt into more;
- physical seating is not a platform concept;
- open installation with no store, payments, reviews or DRM;
- no app and no captive portal is required;
- the phone is more than a controller: native games should use each player's private screen;
- version 1.0 is for the owner, to prove the experience before any commercialization.

**2026-10-02: Standard Mode, origins and the retirement of LAN Games.** Where this amendment
differs from the original, it governs:

- One appliance runs one Party with **one active activity at a time**. Several simultaneous games
  are outside Standard Mode ([ADR 0011](0011-party-console-model.md),
  [ADR 0014](0014-native-games-isolated-lan-games-retired.md)).
- **LAN Games is retiring as a runtime** ([ADR 0014](0014-native-games-isolated-lan-games-retired.md)).
  Its browser-generated token is resolved by retiring it, not by migrating it.
- **The Party alone writes durable records** of people, profiles, results, history and stats.
  Games decide outcomes and report them; they do not keep the platform's record.
- Games receive only session-scoped authority: tickets, a derived game token and a persona
  ([ADR 0006](0006-party-session-protocol.md)).
- **Separate browser origins replace the single-origin assumption.** The Party keeps its own
  origin and game pages move to a separate one ([ADR 0013](0013-party-and-game-browser-origins.md)).
- **Trusted HTTPS is preferred, not required** ([ADR 0012](0012-limited-mode-party-survives-https-loss.md)).

## Where it stands today

The direction has largely been realized through later decisions:

- <span class="avr-badge deployed">Deployed</span> Party Core, a separate small party service,
  with a server-issued device cookie, host and succession rules, and Party-synchronized
  navigation (ADRs 0006–0010, verified on the server side on 2026-09-29).
- <span class="avr-badge source">In source</span> The game contract that plays the role of the
  capability manifest ([ADR 0004](0004-full-mode-contracts-and-providers.md)), and a result
  envelope through which games report outcomes ([ADR 0015](0015-game-result-envelope.md)).
- <span class="avr-badge planned">Planned</span> Profiles, durable history and statistics, the
  provenance-tagged event sink, and the System Admin role. None of these exists in code. Party
  state is held in memory; only hashed device tokens persist.

See [The Party](../architecture/party.md) for how these pieces fit together today, and
[Party platform](../design/party-platform.md) for the fuller design.

## Related decisions

- [ADR 0003](0003-ids-and-keys.md): identifiers, credentials and what each authorizes.
- [ADR 0006](0006-party-session-protocol.md): Party Core v0 and the session protocol.
- [ADR 0011](0011-party-console-model.md): the console model.
- [ADR 0012](0012-limited-mode-party-survives-https-loss.md): Limited Mode.
- [ADR 0013](0013-party-and-game-browser-origins.md): separate browser origins.
- [ADR 0014](0014-native-games-isolated-lan-games-retired.md): isolated native games and the
  retirement of LAN Games.
