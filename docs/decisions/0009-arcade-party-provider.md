---
title: "ADR 0009: The arcade as a Party game"
description: Why the arcade's emulator now runs only while the Party is playing Gauntlet II, how Party Core starts and stops it without new privileges, and what the first version left out.
sources:
  - avrana-party:docs/adr/0009-arcade-party-provider.md
  - avrana-party:arcade/stream.py
  - avrana-party:arcade/README.md
  - avrana-party:avrana/party/managed.py
  - avrana-party:contracts/games/arcade-gauntlet2.json
  - avrana-party:docs/runbooks/arcade-party-provider.md
verified: 2026-10-09
---

# ADR 0009: The arcade is a Party-launched game

!!! abstract "At a glance"
    **Decided:** 2026-09-29 · **Status:** <span class="avr-badge deployed">Deployed</span> (server-side verified); ticket-checked seats and four seats <span class="avr-badge source">In source</span>
    Party Core starts the arcade's emulator and video encoder when the host starts Gauntlet II,
    and stops them when the round ends. The arcade's page and controllers stay up throughout.

## The problem

[ADR 0008](0008-party-navigation.md) made Party Core run one activity at a time, stopping the old
game before starting the next. That works for games that speak the
[session protocol](0006-party-session-protocol.md), like BLUFF. The arcade did not.

The arcade was an always-on service: from boot it ran the RetroArch emulator, a 60 fps screen
capture, hardware video encoding and audio, whether or not anyone played. Gauntlet II could hold
the CPU, the encoder and power while the Party played BLUFF, and on the Raspberry Pi it already
starved the PlayStation experiment.

## What was decided

**Party Core controls the arcade's heavy work, not the service.** Given a Party session key, the
arcade starts idle. The page, the virtual controllers, the statistics page, the virtual display and
the audio sink stay up; they are light. Party Core's signed `launch` starts the emulator, capture
and encoding; its signed `end` stops them. This is the existing session protocol, so no new
privileges, service changes or web-server changes were needed.

**Control messages arrive on a private, loopback-only port** that the public web server never
forwards. A separate port was needed because, on the arcade's ordinary port, a phone's request
proxied by the web server would look local. The port also refuses forwarded requests, large
bodies, and unsigned, expired, replayed or misaddressed messages. Loopback keeps browsers out; it
does not tell local services apart, since they all ran as one Unix user
([ADR 0016](0016-service-identities-and-local-trust-boundary.md)).

**One lock keeps start and stop in order.** Launch, end and abandon never overlap. A start that
fails or takes over 15 seconds is stopped again and reported. An `end` for an old session while a
newer one runs is refused, so a late message never stops the current game; an `end` while idle is
answered "ok", so the host can carry on after an arcade restart. A stop that fails is not
confirmed, so a switch does not start the next game.

**Party Core rolls back failed launches** for every game: it sends an `end` before recording the
failure, while the session is still "launching" so nothing else can start. The arcade's time limit
is 25 seconds, its own 15-second start limit plus time to stop.

**Recovery.** A fatal arcade failure mid-session (watchdog, emulator death) reports the session
as abandoned, then exits; the Party leaves the game and the system restarts the arcade idle.

**Always-on stays the default and the rollback.** Party-managed mode is switched on only by one
configuration drop-in plus the key.

**Gauntlet II becomes a Party game.** The host gets "Start for everyone" and "Switch everyone";
the arcade page follows the Party; a phone that opens the arcade while idle is told the host
starts it.

## Why this way

The obvious alternative, letting Party Core stop and start the whole arcade service, was rejected
for three reasons: it needs new privileges for a deliberately unprivileged, sandboxed service; it
takes the arcade's page, statistics and controllers down with the emulator; and it turns every
host switch into an operating-system service operation. Reusing the session protocol avoided all
three.

## What it means in practice

The emulator now uses CPU, encoder and power only while the Party plays Gauntlet II, and never
beside BLUFF. Limits accepted for the first version:

- **The arcade did not check tickets.** While Gauntlet II was the Party's game, any phone on the
  arcade page could take a free controller. Seating by the Party roster was left for later.
- **The standalone arcade address works only while the Party runs Gauntlet II.** Always-on mode is
  the way back.
- **A rare late start.** If the arcade finishes starting after Party Core stopped waiting, the
  queued rollback `end` stops it about a second later.
- **Not measured:** idle versus running power and CPU on the Pi.

## Later changes

- **Ticket-checked seats (AVR-130).** <span class="avr-badge source">In source</span>. This lifts
  the first limit. In Party-managed mode the arcade page fetches a Party ticket for Gauntlet II on
  every connection and presents it when opening its controller connection; without a valid one
  the connection is refused. Only players get a seat, not spectators. A seat is tied to the
  player's ticket identity, so a phone that drops keeps its seat and player number for
  60 seconds without renumbering anyone. Releasing the controller frees the seat at once, and
  ending, switching or relaunching clears all seats. Always-on mode still hands out the first free
  slot. The ADR has no amendment for this; it is recorded in the arcade's README and runbook.
- **2026-10-07, four seats (AVR-311).** <span class="avr-badge source">In source</span>. Gauntlet
  II takes four phones; two had only been the most anyone had tried. The contract, the arcade and
  the emulator configuration all say four, and tests keep them equal. Four phones at once have not
  been tried on the Pi. When this is deployed, the owner must remove any hand-typed limit of two
  from the appliance's Party configuration, or Party Core refuses to start
  ([ADR 0010](0010-party-pregame.md)).

## Where it stands today

<span class="avr-badge deployed">Deployed</span> on 2026-09-29 and verified on the server side:
the Party starts and stops the emulator, and Gauntlet II is a Party game.

The deployed arcade **does not check tickets**: any phone on the page can take a free controller
while Gauntlet II is on, with at most two controllers. Ticket admission, the 60-second seat hold
and four seats are <span class="avr-badge source">In source</span> only, with no dated record of
deployment or of real-phone testing.

Still open on the Pi and real phones: the repeated emulator and encoder restart cycle, controllers
surviving across runs, and a four-phone night.

## Related decisions

- [ADR 0006: the session protocol](0006-party-session-protocol.md), which the arcade now speaks.
- [ADR 0008: Party navigation](0008-party-navigation.md), whose one-activity rule this completes.
- [ADR 0016: service identities](0016-service-identities-and-local-trust-boundary.md), on what
  loopback does and does not protect.
- [Game sessions](../architecture/game-sessions.md#the-arcade-uses-the-same-protocol).
