---
title: "ADR 0003: Identifiers and credentials"
description: The rules that keep identifiers, credentials and display values apart, and the table of what each value may authorize.
sources:
  - avrana-party:docs/adr/0003-ids-and-keys.md
  - avrana-party:avrana/party/identity.py
  - avrana-party:avrana/party/core.py
  - avrana-party:avrana/party/protocol.py
  - avrana-party:docs/SYSTEM.md
verified: 2026-10-09
---

# ADR 0003: Identifiers, credentials and what each one authorizes

!!! abstract "At a glance"
    **Decided:** 2026-09-24 · **Status:** Invariants accepted · formats and storage left open · server-side invariants <span class="avr-badge deployed">Deployed</span> · amended 2026-10-02, noted 2026-10-03
    Every value in the system is one of three kinds: an identifier that grants nothing, a secret
    credential that grants exactly what is written down, or a display value that never grants
    anything. Games receive a session key and a display name, never anything that identifies a
    device or a person durably.

## The problem

Before the Party existed, each runtime used one string for everything. In LAN Games, a token
the browser generated itself was simultaneously the device, the person, the player's key in each
game and the reconnect credential; it also keyed avatar photos and chat. The PlayStation stream
minted its own slot tokens, and the arcade had no identifier at all.

[ADR 0002](0002-party-platform.md) separated device, profile, presence, seat, role and persona
as concepts. That only works if their *keys* are separate too, and if it is written down which
key may authorize what. Getting this wrong is expensive later, because every record, statistic
and game session would carry the wrong key. This ADR fixes the rules (the *invariants*) and
deliberately leaves formats and storage open.

## What was decided

### Three kinds of value

| Kind | Examples | Secret? | Can it authorize anything? |
|---|---|---|---|
| **Identifier**: stable, opaque, issued by the server | party, device, profile, presence, seat, game session and team ids | No | **No.** Knowing an id grants nothing. |
| **Credential**: a bearer secret or something a person knows | device token, seat ticket, game key, pairing code, admin session, PINs | **Yes** | Yes, but only what it is listed for below |
| **Display value** | name, persona, avatar, "Player 3", controller number, team colour | No | **Never** |

### The rules

1. **Each identity value is distinct.** The device token, device id, profile id, presence id,
   seat id and controller slot number may be mapped to one another, but they are never the same
   value and never derived from one another.
2. **Identifiers are random and opaque.** They are never built from names, MAC or IP addresses,
   timestamps, device fingerprints or other ids.
3. **Only credentials checked on the server authorize.** A client may *mention* an id ("I vote
   for seat X"), but the server decides who the client *is* only from a credential.
4. **Secrets stay in their lane.** Credentials never appear in a URL path or query string, in
   logs, exports, other players' data, TV views, or game servers that don't need them. (A
   short-lived pairing code may go in the URL *fragment*, which browsers do not send to the
   server.) The device token never reaches a game server. The server stores only a hash of
   long-lived secrets, and a slow hash of PINs.
5. **Games receive a game key and a persona, nothing more.** The game key is a secret for one
   participant in one game session, sent only to that participant's own client. For
   Party-launched sessions a game must accept a ticket, not an arbitrary token the client
   supplies.
6. **One active party per appliance.** Parties still have ids, for history and recaps, but there
   is no party selector and no multi-tenant routing.
7. **Records point at identifiers, never at display values**, and every statistic or event
   records its provenance: reported by the game, observed by the platform, or entered by hand.
8. **A guest is a presence without a profile.** If a guest later saves a profile, their earlier
   records are *linked* to it, not rewritten.
9. **Merging profiles never moves credentials.** The merged-away profile keeps its id with a
   pointer to the survivor; its devices, trust links and PIN are dropped.

**Host is not a credential.** It is a role flag on a presence, checked on the server for every
host action. A spectator is simply someone without a seat.

### The credentials and what they authorize

Identifiers (party, device, profile, presence, game session and seat ids) authorize nothing, so
the table lists only the credentials.

| Credential | Lifetime | Authorizes | Where it may appear |
|---|---|---|---|
| **Device token** | long (about 400 days), revocable | "this is device X": offer its trusted profiles and resume its presence | a cookie only, never sent to game servers |
| **Seat ticket** | seconds to minutes, single use | "this connection is presence P in game G" | the first WebSocket message only |
| **Game key** | one game session | the game's own per-player key | that participant's client and the game server |
| **Pairing code** | about 3 minutes, single use | link a new browser to a profile | URL fragment or typed in; never logged |
| **Profile PIN** (optional) | until changed | claim a profile on an untrusted device | never stored in clear |
| **Admin session** | short (idle about 15 min, at most about 2 h) | admin actions only | a cookie on the admin path only |
| **Admin PIN** | until changed | open an admin session | never stored in clear |

A controller slot number belongs to the game and is only a mapping target: it authorizes nothing
and may appear anywhere.

### How the pieces relate

A device can be trusted by many profiles and a profile by many devices. Within the active party,
a profile has at most one presence; a guest presence has no profile. A presence belongs to
exactly one party, holds at most one seat per game session (no seat means spectating) and belongs
to at most one team. Each seat belongs to one game session and maps to at most one controller
slot. Hot-seat games, where several people share one slot, cannot attribute results to
individuals.

### Replacing the old tokens

- The **LAN Games browser token** was to be replaced, for Party-launched sessions, by a game key
  per participant per session; the device role moves to the platform's device token.
- The **PlayStation slot token** becomes a ticket and game-key pair: the stream validates a
  ticket instead of minting.
- The **arcade** accepts a ticket as its first message and maps the seat to a controller slot.
- The **LAN Games player name** becomes a persona set through the platform, still a display
  value.

## Why this way

The ADR's reasoning is mostly about cost later: if identity values are mixed now, every record
and statistic inherits the confusion. Two consequences it spells out are worth knowing:

- **Per-game keys.** Tickets name the game they are for. Sandboxed third-party games must verify
  them with their own key, never one key shared by every game, which would let any game mint
  tickets for any other. Built-in LAN Games modules shared one process, so per-game keys added
  nothing there; that was acceptable only because built-in code is trusted.
- **Device identity cannot stop one person holding several places.** Device tokens are free (a
  private browser tab is a new device). So kicks are not bans, votes are advisory, and admission
  control belongs to a future public or demo preset.

Games that store anything about players must key it by the opaque seat or presence ids they are
given, not by names or their own tokens. That keeps statistics attributable through renames,
persona changes, guest promotion and merges.

**Left open on purpose:** the exact id encoding, storage, how to migrate from the LAN Games
token, whether the party survives a reboot, the exact host-succession policy, and hot-seat
attribution.

## Later changes

**2026-10-02 amendment.** The invariants stand; these points clarify them:

- **Tickets are single-use.** [ADR 0006](0006-party-session-protocol.md)'s first implementation
  allowed a ticket to be replayed within its 120-second life, recorded as a temporary gap. That
  gap has been closed in source; it was always the rule, not a new decision.
- **Reconnecting means fetching a fresh ticket**, which carries the same participant id.
- **A Profile is an optional, durable, server-side person record.** Before Avrana stores anything
  persistent about a person, that record must exist. Live identity (device and presence) stays
  separate from it.
- **Names and avatars are never identity.** The name and avatar a phone stores locally under the
  console model ([ADR 0011](0011-party-console-model.md)) are display values. Nothing persistent
  may be keyed by them.
- **Symmetric keys (HMAC) remain right for session tickets** on a single appliance.
  Public-key signatures are reserved for proving where a game package or update came from.
- The LAN Games cutover happened on 2026-09-27, and
  [ADR 0014](0014-native-games-isolated-lan-games-retired.md) retires standalone LAN Games play
  and its browser token instead of preserving them. Under ADR 0014 each native game runs as its
  own process with its own key, so per-game keys become a real boundary for built-in games too.

**2026-10-03 note.** A per-game key is only a boundary between processes that cannot read each
other's files. On the appliance as deployed, Party Core, LAN Games and the arcade all run as one
Unix user, so every local service should be treated as holding every game's key.
[ADR 0016](0016-service-identities-and-local-trust-boundary.md) defines the separate identities
that would make per-game keys real.

## Where it stands today

- <span class="avr-badge deployed">Deployed</span> The server-side core of the model. Party Core
  issues a random 256-bit device token, stores only its SHA-256 hash, and never adopts a value a
  browser invents. Ids are random 128-bit values, never derived from anything. Games receive a
  per-session participant id, from which the game derives its own per-player token with its
  key; they never see the device or member id.
- In code the names differ slightly from the ADR's: a *presence* is called a **member**, the
  per-session identity is a **participant**, the seat ticket is simply a **ticket**, and the game
  key is the derived **game token**.
- <span class="avr-badge source">In source</span> Single-use tickets, and a device cookie renamed
  `__Host-avrana_device` and scoped to the whole host rather than the Party path. That second
  change sits uneasily with this ADR's statement that the cookie never reaches a game server,
  while game pages still share the Party's host; see
  [Known discrepancies](../status/discrepancies.md).
- <span class="avr-badge planned">Planned</span> Profiles, profile PINs, pairing codes, the admin
  session and admin PIN. None exists in code. The party itself lives in memory, so a restart
  starts a new party; device identities survive because their hashes are stored.

[The Party](../architecture/party.md) explains how identity works today, and
[Trust boundaries](../architecture/trust-boundaries.md) puts these rules in the wider security
picture.

## Related decisions

- [ADR 0002](0002-party-platform.md): the party platform and layered identity.
- [ADR 0006](0006-party-session-protocol.md): tickets and the session protocol.
- [ADR 0011](0011-party-console-model.md): automatic presence and phone-stored names.
- [ADR 0013](0013-party-and-game-browser-origins.md): separate browser origins.
- [ADR 0014](0014-native-games-isolated-lan-games-retired.md): native games as separate processes.
- [ADR 0016](0016-service-identities-and-local-trust-boundary.md): service identities and
  per-game keys.
