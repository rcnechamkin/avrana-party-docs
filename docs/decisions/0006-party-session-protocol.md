---
title: "ADR 0006: Party Core and the session protocol"
description: The decision that created Party Core v0 and the signed protocol through which the Party launches a game, admits exactly the right people and learns that the game has ended.
sources:
  - avrana-party:docs/adr/0006-party-session-protocol.md
  - avrana-party:avrana/party/protocol.py
  - avrana-party:avrana/party/core.py
  - avrana-party:avrana/party/sessions.py
  - avrana-party:avrana/party/service.py
  - avrana-party:avrana/party/identity.py
  - avrana-party:contracts/vectors/party-session.v0.json
  - avrana-party:docs/findings/2026-09-29-party-core-deploy.md
  - avrana-party:docs/SYSTEM.md
verified: 2026-10-09
---

# ADR 0006: Party Core v0 and the Party–game session protocol

!!! abstract "At a glance"
    **Decided:** 2026-09-27 · **Status:** Accepted · <span class="avr-badge deployed">Deployed</span> (server-side verified 2026-09-29) · later additions <span class="avr-badge source">In source</span> · no real-phone proof yet
    A small Party service, Party Core, decides who is in the party and who may enter each game.
    It talks to game servers through a small signed protocol, `avrana.party-session/v0`: launch
    a session, admit each person with a short-lived ticket, end the session, and hear from the
    game itself when it is over.

## The problem

In late September 2026 nothing authoritative ran in production. "Players" were connections to
the LAN Games fork, each holding a token the browser had generated for itself. That one token was
the device, the person, the seat key and the reconnect credential at once
([ADR 0003](0003-ids-and-keys.md)).

The first real party the project aimed for was simple to describe: four phones, offline, go from
Party Home into BLUFF and back. It needed three things that did not exist:

- one party that decides who is in;
- a way to admit exactly those people into a game;
- a way to learn, from the game server itself, that the game is over.

An earlier experiment had proved most of the pieces, but it tied a person's presence to Party
Home's open connection, so opening a game looked like leaving the party.

## What was decided

### Who owns what

| The Party owns | The game owns |
|---|---|
| device identity, membership, party-level names, presence | rules, turns, timers, teams, scores and results |
| the host, succession and host actions | seats and seat layout |
| choosing and launching a game, and **who may enter** | bots and autopilot |
| the session id and each member's participant id | what happens when a player disconnects mid-game |
| finishing, ending for everyone, and returning | private views and what each viewer sees |

Game concepts do not move into Party Core just because BLUFF happens to use them.

### Presence is liveness, and playing is not leaving

- **Membership** is not removed by silence or by navigating into a game. Only an explicit
  leave operation removes it.
- **Presence** is *here* while any authenticated request has arrived from the member in the last
  45 seconds (Party Home's polling, a heartbeat from a game page, or a ticket request), and
  *away* otherwise.
- A member holding a place in the running game is **playing**. A host who is playing keeps the
  role. The Party never runs its own copy of the game's disconnect timers.
- **Host succession:** after a 30-second grace period beyond the liveness window, the role passes
  to the earliest-joined member who is here, or stays vacant if nobody is. A returning former host
  does not take it back.

### Device identity

The Party issues a random 256-bit token in an `HttpOnly`, `Secure` cookie and stores only its
hash. Merely loading a page does not create membership, and a forged or unknown value is never
adopted. In the original design the cookie was scoped to the `/party/` path, so a game page's own
requests never carried it.

### One game session at a time

A session moves through *launching*, *active*, *ending* and *ended*, and finishes with one of four
outcomes: completed, abandoned, ended by the host, or failed to launch. At launch the Party fixes
the roster from members who are here: players up to the game's maximum, then spectators. Late
arrivals join as spectators. Each member gets a random **participant id** that exists only in
that session and survives their reconnects. Games never see device ids or member ids.

### The protocol

`avrana.party-session/v0` is a wire contract between Party Core and one game server.

**Signed envelopes.** Every message and ticket is a small JSON payload followed by an
HMAC-SHA256 signature, written as `aps0.<payload>.<signature>`. Each payload names its version,
its type, who signed it, who may accept it, the session, and when it was issued and expires. A
token of one type is never accepted as another.

**One key per game.** The appliance provisions a random 32-byte key for each game, in a file only
its owner can read. There is no public-key infrastructure: one appliance, local services.

**Four kinds of message.**

- **Launch** (Party to game): start a session with this roster of participants, each with a
  display name and a role. It expires after 30 seconds and carries a nonce, so a replay is
  refused.
- **Ticket** (Party to browser to game): "this connection is participant P, with role R, in
  session S". It lives for 120 seconds, is addressed to one game, and must match the session
  that game is running. A phone fetches it from Party Core with its cookie and sends it **only**
  as the first WebSocket message, never in a URL.
- **End** (Party to game): stop this session. The game returns to a non-running state and every
  ticket for that session stops working.
- **Ended** (game to Party): this session finished, as completed or abandoned. Version 0 carried
  no results.

**Stable identity across reconnects.** A fresh ticket for the same member and session carries
the same participant id. From its key, the session and that id, the game derives a stable secret
**game token** it can use wherever LAN Games used the browser's own token. The game never needs
the device identity.

**Completion cannot be forged.** Party Core accepts an *ended* report only from the local
machine, with no proxy headers, properly signed, and only for the current session. A stale,
replayed or unknown report is refused, so an old report can never end, or revive, a newer
session. A browser has neither the key nor a route to send one.

**One file to vendor.** The reference implementation is a single standard-library Python file
with no Avrana imports, so a game repository can copy it. Its game-side class is the whole seam a
game needs. Shared test vectors pin the format across both repositories.

### What is not the protocol

Party Core's internal Python API may change freely. LAN Games' session class is one game-side
implementation, not the protocol. A future native-game SDK would *wrap* this protocol; none of
that SDK exists, and this ADR does not design it.

## Why this way

The design follows from its **threat assumptions**. The appliance, its local services and
whoever holds administrator access are trusted. Every browser is not, including a phone's own
page, and guests share the Party Wi-Fi. So everything a browser presents is a short-lived,
signed capability, and the messages that change a session's state travel only between local
services.

Symmetric keys were chosen because both ends sit on one appliance. The ADR states the trade-off
openly: a game server can mint tickets for its own sessions and declare its own session ended,
but cannot touch another game's sessions. Built-in LAN Games modules shared one process, so
their keys were effectively per process; that was accepted only for trusted built-in code.

## What it means in practice

The ADR recorded residual risks rather than hiding them:

- **Stolen tickets.** A ticket copied off a phone within its 120 seconds could take that
  participant's place. Version 0 neither bound tickets to a connection nor made them single-use.
- **The party is memory-only.** A restart starts a new party; device identities survive. Whether
  a party should survive a reboot stayed open.
- **Real phones still needed testing**, including iOS sleep and wake timing.

The original plan was for BLUFF to implement the game side first: the launch and end routes,
ticket admission at the first message with the browser-token path switched off for Party
sessions, an *ended* report at completion and abandonment, and an optional heartbeat. Deployment
needed an owner-approved nginx route for the public Party API (never the internal route), a
systemd unit and the key files.

Deliberately deferred: results, scores and an event sink; single-use or connection-bound
tickets; party persistence; votes, kicks and profiles; late-join policies other than spectating;
automatic navigation; the PlayStation and service runtimes; and the SDK.

## Later changes

- **2026-09-28:** [ADR 0007](0007-host-authoritative-launch.md) made Party Home follow the host's
  committed start into the game. Further navigation followed in
  [ADR 0008](0008-party-navigation.md).
- **2026-09-29:** [ADR 0009](0009-arcade-party-provider.md) brought the arcade under the same
  protocol, and [ADR 0010](0010-party-pregame.md) let each person choose to play or watch before
  the host starts, replacing the "players up to the maximum" roster rule.
- **2026-09-29:** [ADR 0011](0011-party-console-model.md), the console model, made presence automatic (no manual
  Join), gave the Party one authoritative location, moved setup into the Party and held results
  on screen.
- **2026-10-02, forward direction.** The v0 protocol stays as implemented and deployed, and:
    - **Tickets are single-use.** Each game keeps a record of spent tickets until they expire; a
      second presentation is refused as a replay. Reconnecting fetches a fresh ticket. This closed
      a gap against [ADR 0003](0003-ids-and-keys.md), which always required single use.
    - Each ticket gained a random `jti` field, so that two tickets minted in the same second are
      distinct strings. It identifies and authorizes nothing.
    - A ticket issued too far in the future (more than 5 seconds) is now refused for "clock"
      rather than "expired", so clock problems can be diagnosed.
    - Tickets stay symmetric HMAC capabilities.
    - Results will cross the boundary in a versioned envelope, and the Party alone keeps the
      durable record ([ADR 0014](0014-native-games-isolated-lan-games-retired.md)).
    - Game pages calling the Party API directly is removed by
      [ADR 0013](0013-party-and-game-browser-origins.md).
- **2026-10-03:** [ADR 0015](0015-game-result-envelope.md) added an optional `result` field to
  *ended*, carrying a separately versioned result envelope. The protocol version stays v0, and a
  receiver that does not know the field ignores it.
- **2026-10-03:** [ADR 0016](0016-service-identities-and-local-trust-boundary.md) narrows the key
  and transport statements. Each key file belongs to Party Core's own service identity, and a game
  receives only its own key. A native game reports on Party Core's internal Unix socket instead of
  over the local network address. Until separate service users are deployed, every service can
  read every key, so "one key per game" is nominal.
- **2026-10-04, accepted by the owner: the host claim.** A game that lets the Party Host act
  inside it (EXPO, for example: begin a mission, retry, go on) had no trustworthy way to know who
  the host was. Two additions answer that. Each ticket now carries `host`, true or false at the
  moment it was minted. Because a claim can be up to 120 seconds stale, a game must also ask Party
  Core, server to server, whether that participant is the host *now*, and act only on a yes. No
  answer, a refusal or a mismatched answer all mean no. A host who has lost the role therefore has
  nothing left to spend, however many tickets they collected. Games keep no host of their own. A
  ticket without the field reads as "unknown", a transitional allowance so the two repositories
  can deploy in either order.

## Where it stands today

- <span class="avr-badge deployed">Deployed</span> Party Core v0 and the protocol for BLUFF,
  verified on the server side at the 2026-09-29 deployment, together with Party-launched arcade
  start and end. Real-phone proof is separate and still open.
- <span class="avr-badge source">In source</span> Single-use tickets, the `jti` field, the
  "clock" refusal, the result field, the host claim and host question, and the internal Unix
  socket. The ADR's 2026-10-04 section describes the host claim as "not merged", but it is on the
  main branch. None of these is recorded as deployed. A game that vendors the protocol file gets
  them only when it takes the new copy.
- In current source the device cookie is renamed `__Host-avrana_device` and scoped to the whole
  host, not `/party/`. See [Known discrepancies](../status/discrepancies.md) for why that matters
  while game pages still share the Party's host.
- Party state is still in memory; only hashed device tokens persist.

For how a round runs end to end today, see [Running a game session](../architecture/game-sessions.md);
for the Party's side, [The Party](../architecture/party.md); and for the cross-repository
contract, [Contracts, catalog and grants](../games/contracts-and-catalog.md#the-party-games-contract).

## Related decisions

- [ADR 0002](0002-party-platform.md): the party platform.
- [ADR 0003](0003-ids-and-keys.md): identifiers and credentials.
- [ADR 0005](0005-lan-games-provider-launch.md): the LAN Games provider launch this builds on.
- [ADR 0007](0007-host-authoritative-launch.md) and [ADR 0008](0008-party-navigation.md): host
  launch and navigation.
- [ADR 0009](0009-arcade-party-provider.md): the arcade as a Party provider.
- [ADR 0010](0010-party-pregame.md) and [ADR 0011](0011-party-console-model.md): pregame and the
  console model.
- [ADR 0013](0013-party-and-game-browser-origins.md): separate browser origins.
- [ADR 0015](0015-game-result-envelope.md): the result envelope.
- [ADR 0016](0016-service-identities-and-local-trust-boundary.md): service identities and the
  internal socket.
