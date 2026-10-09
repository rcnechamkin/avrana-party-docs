---
title: "ADR 0014: Isolated native games"
description: Why each Avrana game becomes its own isolated process, why the LAN Games runtime is being retired, and the order in which the new boundary is proven.
sources:
  - avrana-party:docs/adr/0014-native-games-isolated-lan-games-retired.md
  - avrana-party:avrana/party/registry.py
  - avrana-party:avrana/ops/provision_game.py
  - avrana-party:deploy/games/avrana-game@.service
  - avrana-party:deploy/games/avrana-game@.socket
  - avrana-party:deploy/games/nginx-native-games.location
  - avrana-party:deploy/README.md
  - avrana-party:avrana-party.nginx
  - avrana-party:contracts/games/standin.json
  - avrana-party:avrana/contracts/game.py
verified: 2026-10-09
---

# ADR 0014: Native games are isolated platform consumers; LAN Games is retired

!!! abstract "At a glance"
    **Decided:** 2026-10-02 · **Status:** <span class="avr-badge accepted">Accepted direction</span>; registry, routing and provisioning <span class="avr-badge source">In source</span>, not deployed
    Each Avrana game should run as its own isolated process that talks to the Party only through
    the platform's protocols. The LAN Games fork, which hosts BLUFF today, was a cheap starting
    point and will not be the long-term runtime.

## The problem

LAN Games, an MIT-licensed project retired upstream, was adopted in September 2026 as a cheap
foundation: about 28 working browser party games, a hub, chat and avatars. It became a provider
behind the Party's catalog ([ADR 0005](0005-lan-games-provider-launch.md)) and was bridged to Party
sessions ([ADR 0006](0006-party-session-protocol.md)), so BLUFF could be played as a Party round.
That proved Party Core, tickets, host navigation and the console model.

It also cemented known debt: one process for every game and for chat; a browser-generated
`wc-token` serving as device, person, seat and reconnect credential at once; one shared key, so
any module could read any game's session; game-specific rules threaded through the shared core;
and a hand-written nginx block per title. The 2026-10-02 review concluded that building more
games this way would make the temporary foundation permanent by default.

## What was decided

**Retirement.** The standalone LAN Games player flow, browser-minted `wc-token` admission and the
monolith (the single LAN Games server process that hosts every game) as the native-game runtime are retired from normal operation. LAN Games is kept only as
donor and reference source, material for future *Classics* adaptations (individual LAN Games titles re-built, one at a time, as native games), and possibly a test
reference for TV-required games. Attribution is kept.

**The native-game boundary.**

- **Each game is an independent platform consumer**, with its own process, service identity,
  secrets and state. No game reads another's state or keys.
- **Local communication prefers Unix sockets**; nothing a game serves is reachable except through
  the front door (nginx, the only service phones talk to).
- **Routing is generic**, from a **game registry**. Adding a game adds a registry entry and a
  grant, not nginx edits.
- **One provisioning path** creates every game's identity, grants, keys and registration.
- **One canonical manifest per game** feeds the catalog, grant checks and registration. Game
  Contract v0 is its seed.
- **No game-specific logic in Party Core.** It knows roles, roster, location and outcomes, never
  rules or screens.
- **The Party owns durable results.** Games report structured, versioned outcomes
  ([ADR 0015](0015-game-result-envelope.md)); only the Party writes history and stats.

**Product shape.** One active activity at a time in Standard Mode ([ADR 0011](0011-party-console-model.md));
a future *Developer Mode* may experiment beyond that without complicating it. The validation
order: BLUFF stays the first vertical slice; **Checkers** is the first deliberately simple proof
of a game living entirely outside LAN Games; **Spades** then stress-tests teams, private hands,
reconnect, scoring and richer results. The SDK, `.avrgame` format and provider abstraction stay
**unfrozen** until both have proven the boundary. LAN Games' session framework is "a donor of
patterns, not the SDK".

## Why this way

The shortcut's cost grows with every game built on it. A shared process lets one game's bug
affect all games. A shared key makes per-game keys meaningless. Browser-minted identity cannot
carry the Party's identity model. And an SDK frozen around one example encodes that example's
accidents, so the boundary is proven with two very different games first. Exact systemd
settings, CLI syntax and container technology were left to implementation.

## What it means in practice

- Until retirement, **BLUFF still runs inside LAN Games infrastructure**; documents describing
  that path are current context, not contradictions.
- Chat, avatars and shared library keys need Party-owned replacements, or decisions to drop them,
  before the monolith can stop.
- Per-game processes cost memory and CPU on a Raspberry Pi 4, so idle games must be cheap to
  stop; games are expected to run only while active.
- ADR 0005 remains the record of the deployed provider boundary; its long-term architecture is
  superseded. Standalone-play clauses in ADRs 0007, 0008, 0010 and 0011 stop being requirements
  once standalone LAN play is retired. ADR 0009's standalone arcade rollback path is unaffected.
- Nothing here deletes code. Removing the fork from production is a separate, owner-approved
  deployment with a rollback plan.

## Later changes

[ADR 0016](0016-service-identities-and-local-trust-boundary.md) (2026-10-03) settled the service
identities, secrets, state and local communication left open here. It narrowed "loopback TCP
remains acceptable" to: acceptable as transport for legacy services, never as evidence of which
service is calling. Also open in this ADR's text: the registry format and location (since given
a form in source, below), whether Classics share a small runtime, re-homing chat and avatars,
`.avrgame`, and a community workflow.

## Where it stands today

The ADR's status line says "not implemented", which is older than the code. **In source**, not
deployed: a game **registry** that Party Core reloads without ending the party, reaching each
native game over its own Unix socket; one systemd **unit template** for all native games; a
**generic nginx rule** routing `/games/<slug>/` to that game's socket and refusing outside access
to control paths; **`provision-game`**, which creates, rotates or removes a game's key,
registry entry and unit configuration; and a test-only **stand-in game**. The repository's nginx
file no longer serves the LAN Games hub, and routes BLUFF and EXPO by name to the retiring
runtime.

Not done: the template is not installed on the appliance and no product game has a runtime grant.
The deployed appliance still runs BLUFF inside the LAN Games fork. Native Checkers was in review
in October 2026. A native Spades, the SDK and `.avrgame` do not exist. Checkers and Spades exist only as LAN Games modules in the donor library. One mismatch: the ADR names
`process` as the native runtime type, but the contract validator accepts only `lan_games_module`,
`emulator_profile` and `external`, and the stand-in declares `external` (see
[known discrepancies](../status/discrepancies.md#4-the-native-runtime-type)).

## Related decisions

- [ADR 0005: LAN Games as a provider](0005-lan-games-provider-launch.md), whose long-term architecture this supersedes
- [ADR 0006: the session protocol](0006-party-session-protocol.md) and [ADR 0011: the console model](0011-party-console-model.md)
- [ADR 0013: separate browser origins](0013-party-and-game-browser-origins.md)
- [ADR 0015: the game result envelope](0015-game-result-envelope.md)
- [ADR 0016: service identities](0016-service-identities-and-local-trust-boundary.md)
- [Native games](../games/native-games.md) and [execution models](../games/execution-models.md)
