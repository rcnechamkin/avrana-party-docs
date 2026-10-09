---
title: Roadmap
description: Where Avrana Party is going, in what order the platform work is meant to happen, and what the project has ruled out.
sources:
  - avrana-party:docs/ROADMAP.md
  - avrana-party:docs/SYSTEM.md
  - avrana-party:docs/adr/0012-limited-mode-party-survives-https-loss.md
  - avrana-party:docs/adr/0013-party-and-game-browser-origins.md
  - avrana-party:docs/adr/0014-native-games-isolated-lan-games-retired.md
  - avrana-party:docs/findings/2026-09-24-ps1-bomberman-party-slice.md
  - avrana-party:arcade/stream.py
verified: 2026-10-09
---

# Roadmap

The roadmap describes **product direction and the outcomes the project is working towards**. It
is deliberately not a task list.

!!! note "Linear owns live work"

    Priorities, sequencing, blockers, acceptance criteria and the next task all live in the
    project's Linear workspace. Nothing here assigns work or approves a deployment. For a dated
    view of work in progress, see [Project status](../status/index.md); for what is deployed, the
    [system map](system-map.md).

## Product direction

The guiding line is **"The game may change. The party does not."** One appliance hosts one
Party, which carries on across many games. The Party owns what crosses games: who is here, who is
hosting, where everyone is, the catalog and the social surfaces. Each game owns its rules,
rendering and private state (see [The Party](../architecture/party.md)). The defaults are
browser-first, guest-first and offline-first; a TV, a captive-portal page and an app are optional.

Version 1.0 is for the owner: prove that a whole party night works and is fun. A later
demonstrator or crowdfunded appliance must not distort that goal. The useful demonstrations are
native social games that need no TV, native action games designed around phones, and emulated
multiplayer through
[Personal Viewports](../games/execution-models.md#playstation-profiles-and-personal-viewports).
BLUFF is the first Avrana-native game and the testbed. The standard mode is one appliance, one
Party and one activity at a time.

## Where the foundation stands

An earlier build-order list mixed experiments, contracts and production work; it has been
retired as a queue. Its useful results now exist as foundations: device identity and session
tickets, one trusted HTTPS origin, Party Core's host authority and single-session rule, game
contracts with a catalog and per-seat capability checks, and signed session reports. What
remains around them is mostly persistence and richer identity: reboot-proof Party state, rich
profiles and pairing, moderation, and a wider stats and achievements record.

<span class="avr-badge deployed">Deployed</span> Party Home, host navigation, the Party-managed
arcade and BLUFF's Play-or-Watch setup were verified server-side on 2026-09-29. Server checks are
not phone acceptance.
<span class="avr-badge source">In source</span> The
[console model](../decisions/0011-party-console-model.md) and the arcade's controller
reservations are merged. The owner reports the console model as deployed
(<span class="avr-badge reported">Owner-reported</span>), but no dated record confirms it and
real-phone verification is open.

## The platform-boundary milestone

On 2026-10-02 the project accepted
[Limited Mode](../decisions/0012-limited-mode-party-survives-https-loss.md), a
[separate browser origin for games](../decisions/0013-party-and-game-browser-origins.md) and
[isolated native games with LAN Games retired as a runtime](../decisions/0014-native-games-isolated-lan-games-retired.md).
Those decisions set an **order of outcomes**, each depending on the ones before it. The SDK
comes deliberately late: it is frozen only after isolation, a canonical manifest, a result
protocol and two real games (Checkers, then Spades) have come first.

The engineering roadmap says none of the sequence is deployed. The state column repeats the
[status page's snapshot](../status/index.md#planned-development).

| # | Outcome | State |
|---|---|---|
| 1 | Decision records and design documents agree with the October decisions | Done in documents |
| 2 | Single-use session tickets; a reconnect fetches a fresh one | <span class="avr-badge source">In source</span> |
| 3 | Game pages leave the trusted Party origin | <span class="avr-badge source">In source</span>, not configured |
| 4 | Service and process isolation: own process, identity, secrets and state per game | <span class="avr-badge source">In source</span>, migration not recorded |
| 5 | One canonical per-game manifest for catalog and runtime metadata | <span class="avr-badge source">In source</span> (game contracts) |
| 6 | Generic registry, routing and provisioning, with no per-title front-door setup | <span class="avr-badge source">In source</span> |
| 7 | Versioned results from games; the Party owns the durable record | <span class="avr-badge source">In source</span>; durable history undecided |
| 8 | Retire the LAN Games operational dependency, keeping its code as reference | In source, nginx no longer routes the hub or other titles; the Games server can switch off standalone admission but still allows it by default; BLUFF, EXPO and chat still depend on it |
| 9 | Checkers platform proof: a simple game outside the LAN Games runtime | In review |
| 10 | Spades pressure test: teams, private hands, reconnect, scoring | Readiness work only |
| 11 | Only then freeze and build the SDK, package format and provider abstractions | <span class="avr-badge planned">Planned</span> |
| 12 | Community, package signing and productization | <span class="avr-badge planned">Planned</span> |

[Limited Mode](../design/limited-mode.md) is accepted direction that runs alongside the sequence
rather than as a numbered step; where it fits is a Linear decision.

## The party-night milestone

This runs in parallel, and the platform work must not regress it. The outcome is a coherent
evening: open the Party address, set a local name and avatar, follow the host through setup, play
or watch, finish a round and move on together. Sleeping, reloading or reopening a phone should
bring it back to the right place and the same game identity. It has to be shown on real iPhone
Safari and Android Chrome, including fully offline play (see
[Testing](../developers/testing.md)).

BLUFF already has server-authoritative rules, private views, bots, timers, reconnection and Party
integration; a real group should now shape its mechanics, prompts and balance. Tests that keep
one player's hidden state out of another's browser stay essential, and gameplay building blocks
are not generalized until a second game needs them. *Gauntlet II* remains the shared-stream
arcade path, with four controller slots in source since 2026-10-07; the earlier two-iPhone
session proves only that dated prototype.

## Emulation and Personal Viewports research

<span class="avr-badge experimental">Experimental</span> PlayStation title profiles, an
experimental Party service and viewport simulations live on experiment branches as research, not
as production contracts or branches to merge wholesale. A 2026-09-24 *Bomberman* slice proved
bounded shared-stream play with independent controllers, but found latency stalls and contention
with the arcade.

Personal Viewports, where each phone shows its own player's part of the picture, must first prove
on real phones that people can read it and prefer it to the full shared picture; then latency and
stability are measured; only after that come auto-detection and per-title result adapters. A win
in an emulated game is not observable without a trustworthy result adapter. All emulator runs are
bounded and supervised; long soaks, more than five viewers or stopping the production arcade need
the owner's approval.

## Appliance readiness

The roadmap lists what to measure on the box itself: time from power-on to joinable, power-loss
recovery, battery runtime, cooling, phone battery drain, the access point's real ceiling of awake
phones, usability in a noisy room and offline recovery. Certificate renewal and release rollback
must be maintainable. Removing the USB Wi-Fi adapter fixed under-voltage for the workloads
measured on 2026-09-24, which does not cover cold boots, long sessions, many phones, emulation
or battery power. See [The appliance and its network](../architecture/appliance-and-network.md).

## Longer-term direction

<span class="avr-badge planned">Planned</span> None of this is scheduled.

- **Profiles and local history**: guest-to-profile promotion, recent players, device trust and
  revocation, optional PINs, pairing, export and import.
- **Social play** on the existing Party Chat, adding queues, voting or team chat only where a real
  night shows the need. The host stays the final authority; votes are advisory.
- **Progression** as a Party-owned record, needing an optional server-side profile before anything
  persistent is stored about a person. Launching a game is never counted as having played it.
- **New native games** that use each phone as a private surface, each an isolated platform consumer.
- **Open installation** with appliance-owned grants, trust tiers and sandboxed community code. The
  [`.avrgame` package](../games/native-games.md#the-avrgame-package-concept) and package signing
  come after the platform-boundary milestone.
- **Optional TV and companion surfaces**, which never show private hands, never become required and
  never make an app the baseline.

## What is explicitly not planned

The roadmap rules out a universal gameplay engine, required cloud accounts, a proprietary game
store, one appliance hosting several Parties, simultaneous activities in the standard mode, and
any commitment to spreading one display across several phones. Standalone LAN Games is kept only
while the fork is the deployed runtime and retires with it. Classic map-based *Diplomacy* was
abandoned on 2026-09-23 and is never to be continued.

Throughout, development happens on reviewed branches; deployment, live configuration and
restarts are separate owner-approved steps (see [Deployment](deployment.md)); and credentials,
ROMs, BIOS files, runtime data and raw telemetry stay out of Git.
