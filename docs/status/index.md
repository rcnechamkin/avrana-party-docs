---
title: What works today
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

# What works today

!!! abstract "Snapshot: 9 October 2026"

    This page is a dated summary. It goes out of date quickly. The live sources are
    [Linear](https://linear.app/avranakern) for work in progress, the
    [roadmap](../project/roadmap.md) for
    direction, and [Deployed system and history](../project/system-map.md)
    for verified deployment. Once a build that includes it is deployed, `/party/api/status` on
    the appliance will report what is running. Every recorded build predates that endpoint (see
    [Deployment](../project/deployment.md#the-status-endpoint)).

## The short version

Avrana Party is a **working prototype on one appliance**. The core Party loop and two kinds of
game (an Avrana-native card game and a streamed arcade game) have been deployed and checked on the
appliance from the server side. The source code has moved well beyond the deployed build, with a
console-style Party model, a redesigned shell, and the groundwork for isolated native games,
separate browser origins, Limited Mode and separate service identities. The project's most
important missing evidence is **real people on real phones**. The next gate the owner has set is
four people on four phones finishing a round of BLUFF offline, including a reconnect.

## What is deployed

| Date | Status | Party | Games | Evidence |
|---|---|---|---|---|
| 2026-09-29 | <span class="avr-badge deployed">Deployed</span>, verified | `956b968` | `c6d7b52` | Deployment finding, checked from the server side |
| 2026-10-02 | Observed, not a recorded deployment | `a32b7b4` | `0b4e9d2` | Read-only inspection; the Games revision includes the Games side of the console model. It also found a web release from about 2026-09-30, an unrecorded deployment, and its "already deployed" Games revision disagrees with the system map |
| By 2026-10-04 | <span class="avr-badge reported">Owner-reported</span> | `bb7364c` | `0b4e9d2` (unchanged by the staged script) | Staged for the owner to run; mentioned in the deploy runbook; owner reports the console model as deployed |

The latest **verified** deployment is the one from 2026-09-29. No dated finding records the
later result, and capturing the exact deployed revisions is an open task in Linear. Until it is
done, treat anything after 2026-09-29 as owner-reported, not verified. The
[known discrepancies](discrepancies.md#2-the-system-map-predates-most-october-work) page sets out
the conflicting records.

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

The roadmap sets an order of twelve outcomes for the platform boundary, from single-use tickets
through isolation, a Checkers proof and a Spades pressure test, and only then an SDK. Much of it is
in source, and none of it is deployed. Alongside it run the party-night milestone, emulation research and
appliance readiness (boot time, power-loss recovery, battery, cooling, the access point's real
client ceiling). The [roadmap](../project/roadmap.md) has the full sequence with each step's
state, the parallel tracks, and what is explicitly not planned.

Next: the [architecture overview](../architecture/index.md).
