---
title: Project status
description: What Avrana Party has demonstrated, what is in progress, its known limitations and its planned development, as of October 2026.
sources:
  - avrana-party:docs/SYSTEM.md
  - avrana-party:docs/ROADMAP.md
  - avrana-party:docs/findings/2026-09-29-avr129-deploy.md
  - avrana-party:docs/findings/2026-10-02-avr130-deploy.md
  - avrana-party:docs/findings/2026-10-06-ux-redesign-slice-1-acceptance.md
  - avrana-party:docs/findings/2026-09-24-no-usb-power-baseline.md
  - avrana-party:docs/findings/2026-09-24-ps1-latency.md
  - avrana-party:docs/runbooks/party-https.md
  - avrana-party:docs/runbooks/deploy.md
  - avrana-party:arcade/README.md
  - avrana-party:docs/runbooks/provision-game.md
  - avrana-party:docs/TESTING.md
verified: 2026-10-09
---

# Project status

!!! abstract "Snapshot: 9 October 2026"

    This page is a dated summary. It goes out of date quickly. The live sources are
    [Linear](https://linear.app/avranakern) for work in progress, the
    [roadmap](https://github.com/rcnechamkin/avrana-party/blob/main/docs/ROADMAP.md) for
    direction, the [system map](https://github.com/rcnechamkin/avrana-party/blob/main/docs/SYSTEM.md)
    for verified deployment, and `/party/api/status` on the appliance for what is running.

## The short version

Avrana Party is a **working prototype on one appliance**. The core Party loop and two kinds of
game (a native card game and a streamed arcade game) have been deployed and checked on the
appliance from the server side. The source code has moved well beyond the deployed build, with a
console-style Party model, a redesigned shell, and the groundwork for isolated native games,
separate browser origins, Limited Mode and separate service identities. The project's most
important missing evidence is **real people on real phones**. The next gate the owner has set is
four people on four phones finishing a round of BLUFF offline, including a reconnect.

## What is deployed

The most recent deployment that the system map records as **verified** is from 2026-09-29:
Party `956b968`, Games `c6d7b52`, checked from the server side. Later evidence is partial and
does not fully agree. On 2026-10-02 a read-only inspection recorded Party `a32b7b4` and Games
`0b4e9d2`; that Games revision includes the Games side of the console model. A deployment of
Party `bb7364c` was then staged for the owner to run. The deploy runbook mentions the appliance
at `bb7364c` on 2026-10-04, and the owner reports the console model as deployed. No dated
finding records the result, and capturing the exact deployed revisions is an open task in
Linear. Until it is done, treat anything after 2026-09-29 as **owner-reported, not verified**.
The [known discrepancies](discrepancies.md#2-the-system-map-predates-most-october-work) page
sets out the conflicting records.

None of the October 2026 platform work (native-game machinery, origin separation, Limited Mode,
service users, the new deployment script) has been recorded as deployed. The new deployment
script itself has not yet been run in production.

## Demonstrated capabilities

Each entry notes the strongest evidence behind it.

| Capability | Evidence | Strength |
|---|---|---|
| Trusted HTTPS on the Party Wi-Fi with no internet | The owner's phone loaded the Party with no warning (2026-09-25) | Real phone, one device |
| Arcade streaming with phones as gamepads | Two iPhones played *Gauntlet II* together for a few minutes (2026-09-20) | Real phones, short session |
| Party Core, host navigation, Party-managed arcade, BLUFF Play or Watch | Deployed and checked on the appliance (2026-09-29) | Server-side only |
| Stable power without the USB Wi-Fi adapter | 3 h 26 min baseline with no under-voltage under CPU and radio load (2026-09-24) | Measured, limited workloads |
| Full Party journey with real BLUFF, four simulated phones | Automated test: home, library, briefing, Play or Watch, a round, held results, Play again, home (2026-10-06) | Simulated, Chromium at phone size |
| Party ↔ Games compatibility | The contract checker and cross-repository tests in both CIs | Automated |
| Native-game path (systemd units, dynamic users, socket activation, a full session) | Proof job on a disposable CI runner with the stand-in game | Automated, not the appliance |

## Work in progress

From Linear, as of the snapshot date:

- **Checkers as the first native game process**, launched and ended by Party Core
  (AVR-238, in review). A companion task prepares an appliance for native games with one
  owner-run step (AVR-304, in review).
- **Real-phone verification** of the deployed console model (AVR-212) and of the repaired
  *Gauntlet II* launch (AVR-92).
- **Appliance reliability**: a Wi-Fi qualification harness and pre-event network gate
  (AVR-296), reproducible fresh install and rebuild (AVR-32), and service restart and crash
  recovery (AVR-33).
- **Hardening**: failure boundaries from a hostile audit (AVR-216), and tolerance of
  wall-clock jumps on an appliance with no real-time clock (AVR-221).
- **Platform messaging architecture** and ownership (AVR-53).
- **BLUFF presentation polish** (AVR-313).
- **EXPO**, the adaptation of a cooperative trick-taking game, as its own Linear project.

## Known limitations

These are stated in the engineering documents themselves:

- **No real-phone acceptance** yet for the console model, the redesigned shell, arcade
  reservations or four arcade players.
- **Certificate renewal is manual.** The automatic renewal timer is staged but not enabled.
  The current certificate is valid until 2026-12-25.
- **All appliance services run as one Unix user.** The accepted separation into service
  identities is not deployed. See [Trust boundaries](../architecture/trust-boundaries.md).
- **Game pages share the Party's browser origin.** The accepted separation is not configured.
- **Losing trusted HTTPS still means losing Party Home.** Limited Mode is not deployed.
- **Party state lives in memory.** A restart starts a fresh Party. There are no durable
  profiles, results or history.
- **Party Chat still runs on the legacy LAN Games chat service.**
- **Unmeasured hardware limits**: how many phones the access point can really serve, arcade
  input-to-screen latency, battery runtime, cold boot and long sessions.
- **PlayStation streaming is research only**, CPU-bound and with latency stalls on a real phone.
- **No license file** in the Party repository. Its package metadata and the absence of a
  license file disagree, and that awaits an owner decision.

## Planned development

The roadmap sets an **order of outcomes** for the platform boundary, each depending on the ones
before it. Their state as of the snapshot:

| # | Outcome | State |
|---|---|---|
| 1 | Decision records and design documents agree with the October decisions | Done in documents |
| 2 | Single-use session tickets | <span class="avr-badge source">In source</span> |
| 3 | Party/game browser origin boundary | <span class="avr-badge source">In source</span>, not configured |
| 4 | Service and process isolation | <span class="avr-badge source">In source</span>, migration not recorded |
| 5 | One canonical per-game manifest | <span class="avr-badge source">In source</span> (game contracts) |
| 6 | Generic registry, routing and provisioning | <span class="avr-badge source">In source</span> |
| 7 | Versioned results from games | <span class="avr-badge source">In source</span>; durable history undecided |
| 8 | Retire the LAN Games operational dependency | Standalone mode retired in source; BLUFF, EXPO and chat still depend on it |
| 9 | Checkers platform proof | In review |
| 10 | Spades pressure test | Readiness work only |
| 11 | Then freeze and build the SDK, package format and provider abstractions | <span class="avr-badge planned">Planned</span> |
| 12 | Community, package signing, productization | <span class="avr-badge planned">Planned</span> |

Alongside that sequence, the roadmap keeps three other tracks:

- **The party-night milestone**: a coherent evening on real phones, including sleeping,
  reloading and reopening phones and truly offline play. This must not regress while the
  platform work proceeds.
- **Emulation and Personal Viewports research**: prove readability and preference against a
  full shared frame on real phones before any automation.
- **Appliance readiness**: boot-to-joinable time, power-loss recovery, battery runtime,
  cooling, phone battery drain, the access point's real client ceiling, noisy-venue usability,
  maintainable certificate renewal and release rollback.

Longer term, the roadmap describes profiles and local history, social features built on Party
Chat, progression with honest provenance, more native games that use each phone as a private
surface, open installation with appliance-owned grants, and optional TV or companion surfaces.
None of these is scheduled.

## What is explicitly not planned

The roadmap rules these out: a universal gameplay engine, cloud accounts, a proprietary game
store, a multi-party appliance, simultaneous activities in the standard mode, and any commitment
to spreading one display across several phones.
