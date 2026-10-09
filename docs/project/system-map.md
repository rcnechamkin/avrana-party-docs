---
title: System map
description: What runs on the Avrana appliance, how the deployed build relates to the source code, who the services run as, and a dated history of deployments.
sources:
  - avrana-party:docs/SYSTEM.md
  - avrana-party:docs/findings/2026-09-27-production-deploy.md
  - avrana-party:docs/findings/2026-09-29-party-core-deploy.md
  - avrana-party:docs/findings/2026-09-29-avr128-134-deploy.md
  - avrana-party:docs/findings/2026-09-29-avr129-deploy.md
  - avrana-party:docs/findings/2026-10-02-avr130-deploy.md
  - avrana-party:avrana-party.nginx
  - avrana-party:avrana/ops/status.py
  - avrana-party:avrana/ops/boundary.py
verified: 2026-10-09
---

# System map

This page describes the appliance as it was last **verified**: which services run on it, which
ports they use, how the deployed build relates to the code in the repositories, and how it got
there.

!!! warning "A dated summary, not the live answer"

    The engineering system map was last reconciled on 2026-10-01 and describes the latest
    *verified* production evidence, from 2026-09-29. It is not updated by itself. Once a build
    that includes it is deployed, the authority on what is running is the appliance itself:
    `GET /party/api/status`, which reports the exact deployed revisions and the health of each
    service (see [Deployment](deployment.md#the-status-endpoint)). The builds recorded on this
    page predate that endpoint, so whether the appliance serves it depends on a later
    deployment that has not been recorded. For what is in progress, see
    [Project status](../status/index.md).

## The machines involved

Only one machine is the product: the **appliance**, a Raspberry Pi 4 running Debian 13 (see
[The appliance and its network](../architecture/appliance-and-network.md)). It holds the
production services and a separate development and test area.

Code is never edited on the appliance. Development happens on the owner's laptop and in Claude
Code cloud sessions, on branches. GitHub holds the canonical history of both repositories. A
separate home-infrastructure machine hosts an older documentation mirror and a telemetry hub; it
is not part of this project's code.

The direction of travel is always **development branch → GitHub → appliance**. If work ever
turns up uncommitted on the appliance, it is copied to a development checkout and committed
there on a branch, and nothing on the appliance is reset until the owner agrees.

## What runs on the appliance

<span class="avr-badge deployed">Deployed</span> As verified on 2026-09-29, these are the
long-running pieces:

- **nginx**, the front door. On plain HTTP it answers the phones' captive-portal probes so they
  join the Wi-Fi quietly. On HTTPS, as `party.avrana.net` with a Let's Encrypt certificate, it
  serves the Party shell at `/party/` (static files only), forwards `/party/api/` to Party Core,
  and forwards games and the arcade to their services.
- **Party Core** (`avrana-party-core`), the Party's authority: membership, the Party Host,
  navigation and game sessions. See [The Party](../architecture/party.md). Its state is in
  memory; a restart starts a fresh, empty Party. Only hashed device tokens persist.
- **The games server** (`avranaparty-games`), the Avrana Party Games fork of LAN Games, which
  serves BLUFF and the other browser games. It is <span class="avr-badge retiring">Retiring</span>
  as a runtime under [ADR 0014](../decisions/0014-native-games-isolated-lan-games-retired.md),
  but it is what runs today. The original upstream LAN Games checkout is kept on the appliance,
  untouched, as a rollback copy.
- **The arcade** (`avranaparty-arcade`), which runs RetroArch on a virtual display and streams it
  over WebRTC, with phones as gamepads. Since 2026-09-29 the Party starts and stops the emulator
  through a signed, loopback-only control link
  ([ADR 0009](../decisions/0009-arcade-party-provider.md)). When no Party session is using it, the
  emulator does not run at all.
- **Network services**: NetworkManager's `dnsmasq` hands out addresses and answers DNS on the
  Party Wi-Fi; avahi advertises `party.local`.
- **Operations**: an SSH server for the owner, an `iperf3` server for network measurements and a
  telemetry agent that reports power and health to the home telemetry hub.

### Ports

"Loopback" means the service listens only on `127.0.0.1`, so phones and the network cannot reach
it directly; only processes on the appliance can.

| Port | What | Listens on |
|---|---|---|
| 80 | nginx, HTTP: captive probes, plus games and the arcade over plain HTTP | Network |
| 443 | nginx, HTTPS: `party.avrana.net` — Party shell, `/party/api/`, games, arcade | Network |
| 8096 | Games server (LAN Games fork) | All interfaces (see below) |
| 8191 | Party Core, behind nginx's `/party/api/` | Loopback only |
| 8097 | Arcade web and stream service | Loopback only |
| 8098 | Arcade control: the Party's signed launch and end; never proxied by nginx | Loopback only |
| 53, 67 | DNS and DHCP for the Party Wi-Fi (`dnsmasq`) | The access point's address |
| 5353 | avahi, `party.local` | Network |
| 5201 | `iperf3` measurements | Network |
| 45876 | Telemetry agent | Network |
| 22 | SSH, for the owner | Network |

The deployment checks of 2026-09-29 confirmed that 8191, 8097 and 8098 listen on loopback only.
The games server does not: on 2026-10-03 it was observed listening on all interfaces, because a
loopback-only default merged in the Games repository has not been deployed.

Three more ports appear only while someone is experimenting on the development side of the
appliance: a BLUFF development server (8196), a PlayStation stream (8198) and an experimental
Party front door (8190). None of them is part of production.

## Source versus the deployed build

The repositories and the appliance are deliberately decoupled. **Merging a change is not
deploying it, and deploying it is not verifying it on phones.**

The appliance keeps a production checkout of each repository in the owner's home directory. A
deployment selects an exact, reviewed commit and moves the checkout to it; simply synchronizing
with GitHub is not a release. Two other artefacts are built from those checkouts:

- **The Party shell** is installed as a numbered, root-owned **web release**, built from a clean
  checkout. A `current` link points at the live one, and the newest five are kept, so rolling the
  shell back is a matter of moving the link.
- **The Games checkout** has been updated from a bundle copied over from the laptop and left at a
  detached commit.

On 2026-10-01 the source was well ahead of the verified build. Party `main` was at `bb7364c` and
Games `main` at `0b4e9d2`, including the [console model](../decisions/0011-party-console-model.md)
and the arcade's controller reservations. Most of the October platform work (native-game
provisioning, generic routing, origin separation, Limited Mode, service users, the `__Host-`
device cookie) came later still. The engineering map warns against ever substituting a newer
`main` revision for a deployed one.

The new deployment script changes this picture: it moves each checkout to a detached, named
commit and also builds root-owned code releases under `/opt`. That script has not yet been run in
production. See [Deployment](deployment.md).

## Who the services run as

A read-only inspection on 2026-10-03 found that **Party Core, the games server and the arcade all
run as one Unix user: the owner's login account**. That account can use `sudo` and owns both
source checkouts. The per-game signing keys are readable only by that account, but because every
service is that account, every service can read every key. Only Party Core's systemd unit has
any hardening.

The engineering map spells out the consequences so that nothing is mistaken for isolation. Every
service can read every game's key and every other service's state, can rewrite the code the
others run, and can reach every loopback port. A private key file and a loopback-only port
protect against phones and the network, **not against another service on the same machine**.

The intended boundary is [ADR 0016](../decisions/0016-service-identities-and-local-trust-boundary.md):
a dedicated user per service and a temporary user per native game. Its first-phase pieces are
<span class="avr-badge source">In source</span>. A read-only checker reports how far a machine is
from that target; on 2026-10-03 the appliance met **6 of 25** first-phase rules. The migration
is an owner step that has not been recorded. See
[Trust boundaries](../architecture/trust-boundaries.md#3-services-versus-each-other-on-the-appliance).

## What never goes into Git

Some things exist only on the appliance and are deliberately kept out of the repositories:
power telemetry, playtest logs, ROM and BIOS files, Wi-Fi profiles with their passwords, DHCP
leases (the phones' addresses), device-token hashes and the live web releases. The engineering
map lists their locations. Summaries of measurements belong in dated findings; the raw data does
not.

## Deployment history

Each entry is a dated record from the engineering repository. Every verified deployment was
checked **from the server side**: services running, ports, routes through the real HTTPS front
door, and scripted Party flows using throwaway browser sessions. **None of them was checked on a
real phone.** The three deployments of 2026-09-29 were carried out the same way: the agent
prepared the checkouts, which needs no administrator rights, and the owner ran a single
administrator script.

### 2026-09-27: the games fork and the Party shell go live

The games service switched from upstream LAN Games to the Avrana Party Games fork, which added
BLUFF to the catalog. The Party checkout and shell moved to `7581baa`, and a restart activated a
diagnostics-only fix in the arcade's access-point detection. Party Core was present in source but
not running, so nothing used the session protocol yet. Rollback paths for both the games service
and the shell were kept.

### 2026-09-28: BLUFF in Party Home

Party `15f6322` and Games `c6199be` listed BLUFF in Party Home. This step is recorded in the
system map's history but has no finding of its own.

### 2026-09-29, morning: Party Core v0

<span class="avr-badge deployed">Deployed</span> Party Core was installed and started on loopback,
nginx gained its `/party/api/` route, and the games server was configured to take part in Party
sessions (Party `6bd5af4`, Games `eeedb19`). The same deployment added an arcade watchdog that
restarts the stream if video stalls, and bounded log and telemetry retention. Two test sessions
confirmed that the first to join became Party Host, that a non-host could not start a game, and
that a signed launch and end reached BLUFF. No tokens appeared in any log.

The owner then rehearsed recovery: a clean restart (which, by design, starts an empty Party), a
forced crash (systemd restarted Party Core by itself), a full rollback in runbook order, and a
roll forward to `b345b6d`. Every check passed.

### 2026-09-29, afternoon: host navigation and the Party-managed arcade

<span class="avr-badge deployed">Deployed</span> Party `0e97c2e` and Games `03df5ae` gave Party
Core authority over navigation, with one Party activity at a time
([ADR 0008](../decisions/0008-party-navigation.md)), and made *Gauntlet II* a Party game whose
emulator runs only while the Party runs it. A scripted flow started the arcade, switched to BLUFF
(the emulator stopped before BLUFF launched), switched back and ended. With nobody playing, the
system went from a load average above 2 to 99.5% idle, and the processor ran about 9 °C cooler.
Those were single snapshots, not power measurements. The arcade still did not check Party
tickets: any phone could take a free controller.

### 2026-09-29, evening: BLUFF's Play-or-Watch setup — the latest verified build

<span class="avr-badge deployed">Deployed</span> **Party `956b968`, Games `c6d7b52`.** BLUFF
rounds now begin with the Party's setup
([ADR 0010](../decisions/0010-party-pregame.md)): everyone present chooses Play or Watch, and
only the host can start, once everyone has chosen and two to six will play. A three-session check
confirmed each refusal reason, the roles carried by tickets and the end of the round. It stopped
at the game's launch roster and did not open the game's live connections; actual play was
covered by laptop browser tests.

This is the **latest deployment the engineering records verify**.

### 2026-10-02: an inspection, and a staged deployment

A read-only inspection before the AVR-130 deployment found the appliance at a later state than
any finding records: the Party checkout at `a32b7b4` with a web release built on 2026-09-30, and
Games at `0b4e9d2`, which includes the Games side of the console model. A deployment of Party
`bb7364c` (arcade ticket admission and 60-second controller reservations) was then staged for the
owner, with automatic rollback if a service failed to start. The record ends with the deployment
**awaiting the owner**; no after-state was captured.

### After 2026-10-02: owner-reported only

<span class="avr-badge reported">Owner-reported</span> The deployment runbook mentions in passing
that the appliance was at `bb7364c` on 2026-10-04, and the owner reports the console model as
deployed. No dated finding records either, and capturing the exact deployed revisions is an open
task. Nothing from the October platform work is recorded as deployed. The conflicting records are
set out in
[Known discrepancies](../status/discrepancies.md#2-the-system-map-predates-most-october-work).

### What every record leaves open

The same items recur as unverified across these deployments: Party Home, setup and BLUFF on real
iPhones and Android phones; sleeping and waking phones; *Gauntlet II*'s picture and controls after
a Party start; the arcade watchdog on a real encoder stall; and power use with the Party-managed
arcade.
