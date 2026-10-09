---
title: "ADR 0003: Identifiers and credentials"
description: The rules that keep identifiers, credentials and display values apart, and what each credential may authorize.
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
    Every value is one of three kinds: an identifier that grants nothing, a secret credential
    that grants exactly what is written down, or a display value that never grants anything.
    Games receive a session key and a display name, nothing that identifies a device or person
    durably.

## The problem

Before the Party, each runtime used one string for everything. In LAN Games, a token the browser
generated itself was the device, the person, the player's key in each game and the reconnect
credential, and it also keyed avatars and chat. The PlayStation stream minted its own slot
tokens, and the arcade had no identifier at all.

[ADR 0002](0002-party-platform.md) separated device, profile, presence, seat, role and persona as
concepts. That only works if their *keys* are separate too, and if it is written down which key
may authorize what. Mistakes here are expensive later, because every record and statistic would
carry the wrong key. This ADR fixes the rules and deliberately leaves formats and storage open.

## What was decided

### Three kinds of value

| Kind | Examples | Secret? | Authorizes? |
|---|---|---|---|
| **Identifier**: stable, opaque, server-issued | party, device, profile, presence, seat, game session and team ids | No | **Nothing.** Knowing an id grants nothing. |
| **Credential**: a bearer secret or something a person knows | device token, seat ticket, game key, pairing code, admin session, PINs | **Yes** | Only what the table below lists |
| **Display value** | name, persona, avatar, "Player 3", controller number, team colour | No | **Never** |

### The rules

- **Distinct values.** Device token, device id, profile id, presence id, seat id and controller
  slot may be mapped to each other, but are never the same value or derived from each other.
- **Random, opaque identifiers**, never built from names, MAC or IP addresses, timestamps,
  fingerprints or other ids.
- **Only credentials checked on the server authorize.** A client may *mention* an id ("I vote for
  seat X"), but the server decides who the client *is* only from a credential.
- **Secrets stay in their lane.** No credentials in URL paths or query strings, logs, exports,
  other players' data, TV views, or game servers that don't need them. (A short-lived pairing code
  may go in the URL *fragment*, which browsers do not send.) The device token never reaches a game
  server. Long-lived secrets are stored only as hashes, PINs as slow hashes.
- **Games get a game key and a persona, nothing more.** The game key is a secret for one
  participant in one session, sent only to that participant. Party-launched games must accept a
  ticket, never an arbitrary client-supplied token. Each game binds seats in its own way and
  reports them back by seat id.
- **Games key anything they store by the opaque ids they are given**, never by names or by
  tokens of their own, so records survive renames and profile changes.
- **One active party per appliance**: no party selector and no multi-tenant routing.
- **Records point at identifiers, never display values**, and every statistic records its
  provenance (game-reported, platform-observed or entered by hand).
- **A guest is a presence without a profile.** Saving a profile later *links* earlier records to
  it rather than rewriting them; merging profiles never moves credentials.

**Host is not a credential.** It is a role flag on a presence, checked on the server for every
host action. A spectator is simply someone without a seat.

### What each credential authorizes

| Credential | Lifetime | Authorizes | May appear |
|---|---|---|---|
| **Device token** | about 400 days, revocable | "this is device X": offer its profiles, resume its presence | in a cookie only, never sent to game servers |
| **Seat ticket** | seconds to minutes, single use | "this connection is presence P in game G" | in the first WebSocket message only |
| **Game key** | one game session | the game's own per-player key | that participant's client and the game server |
| **Pairing code** | about 3 minutes, single use | link a new browser to a profile | URL fragment or typed; never logged |
| **Profile PIN** (optional) | until changed | claim a profile on an untrusted device | never stored in clear |
| **Admin session** | idle about 15 min, at most about 2 h | admin actions only | a cookie on the admin path |
| **Admin PIN** | until changed | open an admin session | never stored in clear |

How they relate: a device can be trusted by many profiles and vice versa; within the active
party a profile has at most one presence; a presence holds at most one seat per game session and
belongs to at most one team; each seat maps to at most one controller slot. Hot-seat games, where
several people share a slot, cannot attribute results to individuals.

The old tokens were to be mapped onto this model: the LAN Games browser token replaced by a
per-session game key, the PlayStation slot token by a ticket, the arcade's first-free-slot by a
ticket mapped to a controller, and the LAN Games player name by a platform persona.

## Why this way

If identity values are mixed now, every record inherits the confusion. Two consequences recorded
in the ADR are worth knowing. **Per-game keys**: tickets name the game they are for, and each game
verifies them with its own key, never one key shared by all, which would let any game mint
tickets for any other. **Device identity cannot stop one person holding several places**, since a
private browser tab is a new device; so kicks are not bans, votes are advisory, and admission
control belongs to a future public or demo preset.

Left open on purpose: id encoding, storage, migration from the LAN Games token, surviving a
reboot, the exact host-succession policy and hot-seat attribution.

## Later changes

**2026-10-02.** The rules stand, with these clarifications:

- **Tickets are single-use**, as always specified. [ADR 0006](0006-party-session-protocol.md)'s
  first version allowed replay within 120 seconds as a temporary gap, since closed in source.
  Reconnecting fetches a fresh ticket with the same participant id.
- **A Profile is an optional, durable, server-side person record**, and must exist before Avrana
  stores anything persistent about a person. The name and avatar a phone keeps under the console
  model ([ADR 0011](0011-party-console-model.md)) are display values, not identity.
- **Symmetric HMAC keys remain right for session tickets.** Public-key signatures are reserved for
  proving where a game package or update came from.
- [ADR 0014](0014-native-games-isolated-lan-games-retired.md) retires standalone LAN Games play
  and its browser token. Each native game runs as its own process with its own key, so per-game
  keys become a real boundary for built-in games too.

**2026-10-03.** A per-game key separates only processes that cannot read each other's files. On
the deployed appliance every service runs as one Unix user, so each should be treated as holding
every game's key until [ADR 0016](0016-service-identities-and-local-trust-boundary.md)'s separate
identities are in place.

## Where it stands today

- <span class="avr-badge deployed">Deployed</span> The server-side core. Party Core issues a random
  256-bit device token, stores only its SHA-256 hash and never adopts a value a browser invents.
  Ids are random 128-bit values. Games receive a per-session participant id, from which the game
  derives its own per-player token; they never see device or member ids.
- In code the names differ: a *presence* is a **member**, the per-session identity is a
  **participant**, the seat ticket is a **ticket** and the game key is the **game token**.
- <span class="avr-badge source">In source</span> Single-use tickets, and a device cookie renamed
  `__Host-avrana_device` and scoped to the whole host rather than the Party path. While game pages
  still share the Party's host, that sits uneasily with "never reaches a game server"; see
  [Known discrepancies](../status/discrepancies.md).
- <span class="avr-badge planned">Planned</span> Profiles, PINs, pairing codes and the admin
  session; none exists in code. The party lives in memory, so a restart starts a new one; device
  identities survive because their hashes are stored.

See [The Party](../architecture/party.md) and [Trust boundaries](../architecture/trust-boundaries.md).

## Related decisions

- [ADR 0002](0002-party-platform.md): the party platform and layered identity.
- [ADR 0006](0006-party-session-protocol.md): tickets and the session protocol.
- [ADR 0011](0011-party-console-model.md): automatic presence and phone-stored names.
- [ADR 0013](0013-party-and-game-browser-origins.md): separate browser origins.
- [ADR 0014](0014-native-games-isolated-lan-games-retired.md): native games as separate processes.
- [ADR 0016](0016-service-identities-and-local-trust-boundary.md): service identities and
  per-game keys.
