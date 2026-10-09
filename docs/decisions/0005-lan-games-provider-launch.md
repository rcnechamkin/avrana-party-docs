---
title: "ADR 0005: LAN Games as a provider"
description: How the LAN Games fork became a provider behind the Party's catalog, with Party-initiated launches, and why that boundary is now being retired.
sources:
  - avrana-party:docs/adr/0005-lan-games-provider-launch.md
  - avrana-party:docs/design/LAN-GAMES-PROVIDER.md
  - avrana-party:avrana/contracts/lan_catalog.py
  - avrana-party:docs/findings/2026-09-27-production-deploy.md
  - avrana-party:docs/SYSTEM.md
  - avrana-party-games:provider/catalog.json
  - avrana-party-games:web/avrana-integration.js
  - avrana-party-games:server.py
  - avrana-party:contracts/appliances/avrana-pi4.json
verified: 2026-10-09
---

# ADR 0005: The LAN Games fork becomes a provider behind the Party

!!! abstract "At a glance"
    **Decided:** 2026-09-26 · **Status:** Implemented and <span class="avr-badge deployed">Deployed</span> (2026-09-27) · long-term role superseded by ADR 0014 <span class="avr-badge retiring">Retiring</span>
    Avrana owns identity, navigation, discovery, the library and Party Chat. The LAN Games fork
    owns the individual games and is launched by the Party through a versioned, credential-free
    link. Its standalone hub becomes a compatibility surface, not part of the product.

## The problem

The project's games server was a fork of LAN Games, an existing collection of browser party
games with its own hub page, its own profile and avatar handling, its own library of favourites
and recent games, its own global chat and its own service worker. Once Avrana had a Party shell
of its own ([ADR 0004](0004-full-mode-contracts-and-providers.md)), two global "front doors"
existed. The project needed to decide which parts belonged to Avrana and which to the games
server, and how the Party would launch a game without dropping the player into the old hub.

## What was decided

The dividing line: **Avrana owns** identity and profile, global navigation, discovery, the
library and Party Chat. **LAN Games owns** the individual game implementations and, for now,
some transport internals. The standalone hub stays only for compatibility and development.

- **A public catalog.** The games server exports a deterministic description of its titles
  (`avrana.lan-catalog/v1`) from its authoritative registry, with a recorded revision and digest
  and tests in both repositories that catch drift. Ids take the form `lan-<slug>`, except BLUFF,
  which keeps `bluff`. Routes stay out of the game contracts: installation is still an appliance
  grant, checked against the known route.
- **A launch marker.** The games server advertises support for `avrana.lan-launch/v1`. The Party
  launches a game with a plain marker in the URL (`?avrana=1`), carrying no credentials and no
  arbitrary return address. If the games server is too old to support it, the Party says so
  visibly instead of falling back to the old hub.
- **No competing global chrome.** A shared bootstrap script and declared page markers hide the
  old hub's global profile and navigation controls inside integrated games. A contained game
  room leaves space for one explicit way back to `/party/`. Game-specific interface stays, and no
  iframe shell is introduced.
- **Shared browser storage stays compatible.** The old identity keys remain for compatibility,
  and the existing library lists remain the one library store, with canonical entries written as
  `avrana:<id>` and old aliases collapsed lazily. "History" means a game was opened, not that it
  ran successfully. Unknown data is preserved.
- **One chat.** The existing single chat conversation stays; games do not create competing global
  chats. Chat connection counts are not treated as the Party's roster, and no Party service was
  promoted at this point.
- **Separate service workers.** Integrated pages do not register the games server's site-wide
  worker, and that worker was updated to leave Avrana's pages and caches alone. The `/party/`
  worker scope, HTTPS, the captive-portal HTTP behaviour and diagnostics are unchanged.

## Why this way

The design notes behind this ADR come from an audit of what the games server actually owned. The
choices follow a few principles:

- **The appliance, not the game, decides installation.** The catalog only *describes* titles; it
  cannot grant itself routes or capabilities.
- **No credentials in URLs.** The launch marker identifies the integration version and nothing
  else.
- **Fail visibly.** An out-of-date games server is a deployment dependency to fix, not a reason
  to silently drop the player into the old hub.
- **No iframe shell.** In line with [ADR 0002](0002-party-platform.md), games keep owning the page.

## What it means in practice

The change needed two coordinated pull requests, one in each repository, an explicit version gate
for deployment and hardware checks after review. Browsers that already had the old site-wide
worker installed needed update testing. The ADR lists known debt that remained: storage on older
HTTP origins cannot be recovered, legacy authorization through the old browser token remained,
there was no authoritative session state, and deeper extraction of the transport was left for
later.

## Later changes

- **ADRs 0006 to 0011** added Party session and roster authority, and replaced the fixed "back to
  Party" chrome during Party rounds with authoritative following of the Party's location and
  host-owned controls ([ADR 0006](0006-party-session-protocol.md) to
  [ADR 0011](0011-party-console-model.md)).
- **2026-10-02:** [ADR 0014](0014-native-games-isolated-lan-games-retired.md) supersedes this
  ADR's long-term architecture. LAN Games is retiring as an Avrana runtime, standalone LAN Games
  is no longer a product mode, and admission by the old browser token is retiring. ADR 0005 is
  kept as the accurate record of the boundary that is still deployed, until the retirement is
  carried out and verified.

## Where it stands today

- <span class="avr-badge deployed">Deployed</span> The provider launches and the switch to the
  fork, since 2026-09-27. In the verified 2026-09-29 deployment, the games server is still the
  LAN Games fork, launched this way.
- <span class="avr-badge retiring">Retiring</span> The boundary as a whole, under ADR 0014. In
  current source the Party's appliance grants offer only BLUFF and EXPO. The games server still
  has its hub page; it can be configured so that a connection without a Party ticket may only
  watch, but by default standalone play is still admitted.
- Party Chat's interface belongs to the Party, but its transport still runs on the fork's chat
  service, using the fork's browser-generated token (see
  [Known discrepancies](../status/discrepancies.md)).

The catalog and launch flow are covered in [Games](../games/index.md) and
[Contracts, catalog and grants](../games/contracts-and-catalog.md#the-party-games-contract).

## Related decisions

- [ADR 0002](0002-party-platform.md): the party platform.
- [ADR 0004](0004-full-mode-contracts-and-providers.md): the origin, game contracts and providers
  this ADR builds on.
- [ADR 0006](0006-party-session-protocol.md): Party Core and the session protocol.
- [ADR 0014](0014-native-games-isolated-lan-games-retired.md): isolated native games; LAN Games
  retired.
