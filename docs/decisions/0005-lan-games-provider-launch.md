---
title: "ADR 0005: LAN Games as a provider"
description: How the LAN Games fork became a provider behind the Party's catalog, with Party-initiated launches, and why that boundary is now being retired.
sources:
  - avrana-party:docs/adr/0005-lan-games-provider-launch.md
  - avrana-party:docs/design/LAN-GAMES-PROVIDER.md
  - avrana-party:avrana/contracts/lan_catalog.py
  - avrana-party:contracts/appliances/avrana-pi4.json
  - avrana-party:docs/findings/2026-09-27-production-deploy.md
  - avrana-party:docs/SYSTEM.md
  - avrana-party-games:provider/catalog.json
  - avrana-party-games:web/avrana-integration.js
  - avrana-party-games:server.py
verified: 2026-10-09
---

# ADR 0005: The LAN Games fork becomes a provider behind the Party

!!! abstract "At a glance"
    **Decided:** 2026-09-26 · **Status:** Implemented and <span class="avr-badge deployed">Deployed</span> (2026-09-27) · long-term role superseded by ADR 0014 <span class="avr-badge retiring">Retiring</span>
    Avrana owns identity, navigation, discovery, the library and Party Chat. The LAN Games fork
    owns the individual games, which the Party launches through a versioned, credential-free
    link. The fork's own hub becomes a compatibility surface, not part of the product.

## The problem

The games server was a fork of LAN Games, a collection of browser party games with its own hub
page, profiles and avatars, library of favourites, global chat and service worker. Once Avrana
had its own Party shell ([ADR 0004](0004-full-mode-contracts-and-providers.md)), there were two
global front doors. The project had to decide which parts belonged to whom, and how the Party
would launch a game without dropping players into the old hub.

## What was decided

**Avrana owns** identity and profile, global navigation, discovery, the library and Party Chat.
**LAN Games owns** the game implementations and, for now, some transport internals.

- **A public catalog.** The games server exports a deterministic description of its titles
  (`avrana.lan-catalog/v1`) from its registry, with a recorded revision and digest and tests in
  both repositories that catch drift. Ids are `lan-<slug>`, except `bluff`. Installation remains
  an appliance grant, checked against the known route.
- **A launch marker.** The games server advertises `avrana.lan-launch/v1`, and the Party launches
  a game with a plain URL marker (`?avrana=1`): no credentials, no arbitrary return address. An
  out-of-date games server is reported visibly instead of falling back to the old hub.
- **No competing global chrome.** Inside integrated games, the old hub's global profile and
  navigation controls are hidden, and the room leaves space for one explicit way back to
  `/party/`. Game-specific interface stays; no iframe shell is introduced.
- **Compatible browser storage.** The old identity and library keys remain, with canonical
  library entries written as `avrana:<id>`. "History" means a game was opened, not that it ran.
  Unknown data is preserved.
- **One chat.** The existing single conversation stays; games do not create competing chats, and
  chat connection counts are not treated as the Party's roster.
- **Separate service workers.** Integrated pages do not register the games server's site-wide
  worker, and that worker leaves Avrana's pages and caches alone.

## Why this way

The catalog only *describes* titles, so the appliance, not the game, decides what is installed.
The launch marker carries no credentials. An out-of-date games server fails visibly, as a
deployment dependency to fix. And, following [ADR 0002](0002-party-platform.md), games keep owning
their pages rather than being wrapped in an iframe.

## What it means in practice

The change took two coordinated pull requests, a version gate for deployment and hardware checks
after review; browsers with the old worker installed needed update testing. The ADR lists the debt
left behind: storage on older HTTP origins cannot be recovered, authorization by the old browser
token remained, and there was no authoritative session state yet.

## Later changes

- **ADRs 0006 to 0011** added Party session and roster authority, and replaced the fixed "back to
  Party" bar during rounds with following the Party's location and host-owned controls
  ([ADR 0006](0006-party-session-protocol.md), [ADR 0011](0011-party-console-model.md)).
- **2026-10-02:** [ADR 0014](0014-native-games-isolated-lan-games-retired.md) supersedes this
  ADR's long-term architecture: LAN Games is retiring as an Avrana runtime, standalone LAN Games
  is not a product mode, and admission by the old browser token is retiring. ADR 0005 remains the
  record of the boundary still deployed until the retirement is carried out and verified.

## Where it stands today

- <span class="avr-badge deployed">Deployed</span> Provider launches and the switch to the fork,
  since 2026-09-27. At the verified 2026-09-29 deployment the games server is still this fork.
- <span class="avr-badge retiring">Retiring</span> The boundary as a whole. In current source the
  Party's appliance grants offer only BLUFF and EXPO. The games server still has its hub page; it
  can be configured so that a connection without a Party ticket may only watch, but by default
  standalone play is still admitted.
- Party Chat's interface belongs to the Party, but its transport still runs on the fork's chat
  service with the fork's browser token (see [Known discrepancies](../status/discrepancies.md)).

See [Games](../games/index.md) and
[Contracts, catalog and grants](../games/contracts-and-catalog.md#the-party-games-contract).

## Related decisions

- [ADR 0002](0002-party-platform.md): the party platform.
- [ADR 0004](0004-full-mode-contracts-and-providers.md): the origin and contracts this builds on.
- [ADR 0006](0006-party-session-protocol.md): Party Core and the session protocol.
- [ADR 0014](0014-native-games-isolated-lan-games-retired.md): isolated native games; LAN Games
  retired.
