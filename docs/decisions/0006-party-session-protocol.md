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
    It talks to game servers through a signed protocol, `avrana.party-session/v0`: launch a
    session, admit each person with a short-lived ticket, end the session, and hear from the game
    itself when it is over.

## The problem

In late September 2026 nothing authoritative ran in production. "Players" were connections to
the LAN Games fork, each holding a token the browser had made for itself, which was device,
person, seat key and reconnect credential at once ([ADR 0003](0003-ids-and-keys.md)). The first
real party the project aimed for (four phones, offline, from Party Home into BLUFF and back)
needed one party that decides who is in, a way to admit exactly those people into a game, and a
way to learn from the game server itself that the game is over. An earlier experiment had proved
most pieces, but opening a game there looked like leaving the party.

## What was decided

**Ownership.** The Party owns device identity, membership, names and presence; the host and
succession; choosing and launching a game and **who may enter**; session and participant ids; and
ending and returning. The game owns its rules, turns, timers, teams, scores and results; seats
and their layout; bots; what happens when a player disconnects mid-game; and private views. Game
concepts do not move into Party Core because BLUFF happens to use them.

**Presence is liveness, and playing is not leaving.** Membership is not removed by silence or by
going into a game. A member is *here* if any authenticated request arrived in the last 45 seconds
(Party Home polling, a game page's heartbeat, or a ticket request), otherwise *away*. A member in
the running game is *playing*, and a playing host keeps the role. After 30 seconds' grace beyond
the liveness window, an absent host is succeeded by the earliest-joined member who is here; a
returning former host does not take the role back.

**Device identity.** A random 256-bit token in an `HttpOnly`, `Secure` cookie, stored only as a
hash. Forged or unknown values are never adopted, and merely loading a page creates no
membership. The cookie was originally scoped to `/party/`, so game pages' own requests never
carried it. A game page could still *call* `/party/api/` itself, and that request did carry the
cookie: the gap [ADR 0013](0013-party-and-game-browser-origins.md) later closes.

**One game session at a time.** A session goes from *launching* to *active*, *ending* and *ended*,
with one of four outcomes: completed, abandoned, ended by the host, or failed to launch. At launch
the Party fixes the roster from members who are here (players up to the game's maximum, then
spectators; late arrivals spectate). Each member gets a random **participant id** that exists
only in that session and survives reconnects. Games never see device or member ids.

### The protocol

Every message and ticket is a small JSON payload with an HMAC-SHA256 signature, written as
`aps0.<payload>.<signature>`. Each names its type, signer, intended recipient, session, and issue
and expiry times, and a token of one type is never accepted as another. Each game has its own
random 32-byte key, provisioned by the appliance; there is no public-key infrastructure.

There are four kinds of message:

- **Launch** (Party to game): start a session with this roster of participants, names and roles.
- **Ticket** (Party to browser to game): "this connection is participant P, with role R, in
  session S". It lives 120 seconds, is addressed to one game and must match its running session.
  A phone fetches it with its cookie and sends it **only** as the first WebSocket message, never
  in a URL.
- **End** (Party to game): stop the session; its tickets stop working.
- **Ended** (game to Party): the session finished, completed or abandoned. Version 0 carried no
  results.

Server-to-server messages expire after 30 seconds and carry a nonce (a random value used
once), so a recorded message replayed later is refused.
Reconnecting means fetching a fresh ticket, which carries the same participant id; from it the
game derives a stable secret **game token** to use where LAN Games used the browser's token.

**Completion cannot be forged.** Party Core accepts *ended* only from the local machine, without
the headers nginx adds to forwarded requests (so it cannot have come from a phone), properly signed and for the current session, so an old report can never end or
revive a newer session. A browser has neither the key nor a route.

The reference implementation is one standard-library Python file that a game repository can copy,
and shared test vectors pin the format across both repositories. Party Core's internal API and
LAN Games' session class are explicitly *not* the protocol, and a future native-game SDK would
wrap it; none of that SDK exists.

## Why this way

The design follows from its **threat assumptions**. The appliance, its local services and its
administrators are trusted; every browser is not, including a phone's own page, and guests share
the Wi-Fi. So browsers only ever present short-lived signed capabilities, and messages that change
a session travel only between local services.

Symmetric keys suit one appliance. The trade-off is stated openly: a game server can mint tickets
for its own sessions and end its own session, but cannot touch another game's. Built-in LAN Games
modules shared one process and so effectively one key, accepted only for trusted built-in code.

## What it means in practice

The ADR recorded residual risks. A ticket copied off a phone within 120 seconds could take that
participant's place, because version 0 neither made tickets single-use nor bound them to a
connection. The party is memory-only, so a restart starts a new one while device identities
survive. Real phones, including iOS sleep and wake, still needed testing.

BLUFF was to implement the game side first, with its browser-token path switched off for Party
sessions. Deliberately deferred: results and an event sink, single-use tickets, party
persistence, votes, kicks and profiles, other late-join policies, automatic navigation, the
PlayStation runtime and the SDK.

## Later changes

- **2026-09-28 and 2026-09-29:** [ADR 0007](0007-host-authoritative-launch.md) and
  [ADR 0008](0008-party-navigation.md) made the Party follow the host into and between games;
  [ADR 0009](0009-arcade-party-provider.md) brought the arcade under this protocol;
  [ADR 0010](0010-party-pregame.md) let each person choose Play or Watch before the host starts;
  and [ADR 0011](0011-party-console-model.md) made presence automatic and gave the Party one
  authoritative location.
- **2026-10-02:** v0 stays as deployed, and tickets become **single-use**: each game records spent
  tickets until they expire and refuses a second presentation. This closed a gap against
  ADR 0003, which always required it. Tickets gained a random identifier (`jti`) so two minted in the
  same second differ, and a ticket dated more than 5 seconds in the future is refused as a clock
  problem rather than as expired. Results are to cross the boundary in a versioned envelope, with
  the Party alone keeping the durable record
  ([ADR 0014](0014-native-games-isolated-lan-games-retired.md)), and game pages stop calling the
  Party API directly ([ADR 0013](0013-party-and-game-browser-origins.md)).
- **2026-10-03:** [ADR 0015](0015-game-result-envelope.md) adds an optional, separately versioned
  `result` field to *ended*; the protocol stays v0.
  [ADR 0016](0016-service-identities-and-local-trust-boundary.md) gives each game only its own
  key and has native games report over Party Core's internal Unix socket. Until separate service
  users are deployed, every service can read every key, so "one key per game" is nominal.
- **2026-10-04, accepted by the owner:** the **host claim**. A game that lets the host act inside
  it (EXPO's "begin mission", for example) had no trustworthy way to know who the host was. Each
  ticket now says whether its participant was host when minted, and because that may be stale,
  the game must also ask Party Core, server to server, whether the participant is host *now*, and
  act only on a yes. A host who lost the role has nothing left to spend, and games keep no host of
  their own. During the transition, a ticket from an older Party carries no claim; a game then
  keeps its earlier behaviour and must say so, and that allowance is to be removed later.

## Where it stands today

- <span class="avr-badge deployed">Deployed</span> Party Core v0 and the protocol for BLUFF, plus
  Party-launched arcade start and end, verified on the server side on 2026-09-29. Real-phone proof
  is still open.
- <span class="avr-badge source">In source</span> Single-use tickets, `jti`, the clock refusal,
  the result field, the host claim and question, and the internal Unix socket. The ADR's
  2026-10-04 section calls the host claim "not merged", but it is on the main branch. None of
  these is recorded as deployed.
- In current source the device cookie is `__Host-avrana_device`, scoped to the whole host rather
  than `/party/`; see [Known discrepancies](../status/discrepancies.md). Party state is still in
  memory, and only hashed device tokens persist.

For a round end to end, see [Game sessions](../architecture/game-sessions.md); see also
[The Party](../architecture/party.md) and
[Contracts, catalog and grants](../games/contracts-and-catalog.md#the-party-games-contract).

## Related decisions

- [ADR 0002](0002-party-platform.md) and [ADR 0003](0003-ids-and-keys.md): the platform and its
  identity rules.
- [ADR 0005](0005-lan-games-provider-launch.md): the provider launch this builds on.
- [ADR 0007](0007-host-authoritative-launch.md), [ADR 0008](0008-party-navigation.md),
  [ADR 0009](0009-arcade-party-provider.md), [ADR 0010](0010-party-pregame.md) and
  [ADR 0011](0011-party-console-model.md): the Party features built on this protocol.
- [ADR 0013](0013-party-and-game-browser-origins.md), [ADR 0015](0015-game-result-envelope.md)
  and [ADR 0016](0016-service-identities-and-local-trust-boundary.md): later amendments.
