---
title: "ADR 0015: Game result envelope"
description: The small, versioned result format a game sends when a session ends, the limits the Party enforces on it, and what the Party does and does not yet do with results.
sources:
  - avrana-party:docs/adr/0015-game-result-envelope.md
  - avrana-party:avrana/party/result.py
  - avrana-party:avrana/party/core.py
  - avrana-party:contracts/vectors/game-result.v1.json
  - avrana-party-games:core/party_session.py
  - avrana-party-games:games/bluff/game.py
verified: 2026-10-09
---

# ADR 0015: Game result envelope v1

!!! abstract "At a glance"
    **Decided:** 2026-10-03 · **Status:** <span class="avr-badge accepted">Accepted</span>; <span class="avr-badge source">In source</span> in both repositories, not deployed
    When a session ends, a game may attach a small, structured, separately versioned **result**:
    who won, lost or drew, plus a little game-specific data. The Party checks it strictly and
    keeps it in memory. History, stats and privacy are left to a later decision.

## The problem

The session protocol ([ADR 0006](0006-party-session-protocol.md)) lets a game report that a
session ended, `completed` or `abandoned`, and nothing more. BLUFF knows who won and EXPO knows
whether the mission succeeded, but the Party does not. With several games, each would keep its
own idea of results and the Party could never hold an authoritative record, although
[ADR 0014](0014-native-games-isolated-lan-games-retired.md) made the Party the owner of durable
results.

Two things are kept. The `ended` message is signed with the game's key, bound to one session,
protected against replay, and accepted only locally. And games name people only by
**participant ids**, random per-session ids issued by the Party, never member or device ids.

## What was decided

**The result rides inside `ended`.** `ended` gains one optional `result` field with its own
format name and version, `avrana.game-result/v1`; the session protocol stays at v0, and a
receiver that does not know the field ignores it. With no separate message, a result always
arrives with the end it describes, never for a running session. Authentication and replay
protection come from `ended`.

**The envelope**, in short:

```json
{
  "schema": "avrana.game-result/v1",
  "game": {"id": "bluff", "build": "sha256:3f9c0a…"},
  "mode": "competitive",
  "standings": [
    {"participant": "participant-…", "standing": "won"},
    {"participant": "participant-…", "standing": "lost"}
  ],
  "data_schema": "bluff.result/v1",
  "data": {"steps": 41}
}
```

The platform reads which game and **build** produced it (optionally a ruleset or content pack),
whether it is `competitive` or `cooperative`, and one standing per player (`won`, `lost` or
`draw`, optionally ranked). `data` belongs to the game, named by `data_schema`; the Party stores
it but never interprets it. There is deliberately **no score, team, round or achievement field**.
Scores go in `data`, and any cross-game scoring model is for later, designed from real results.

**The limits.** An authenticated result is still untrusted input. The Party refuses unknown
fields; participants who are not players of this session, or a player missing or listed twice;
ranks given for only some players; anything but one shared `won` or `lost` in cooperative mode;
`data` without `data_schema` (or the reverse), nested over 4 levels, with strings over 200
characters, integers beyond ±2^53, or non-player participant ids; and a result over 2048 bytes or
`data` over 1024 bytes as canonical JSON. These sizes keep the signed message within the
protocol's 8192-byte limits.

**The end and the result are judged separately.** A bad *message* (signature, issuer, session,
replay, not local) is refused whole, as before. A valid message ends the session regardless; the
result is then accepted or refused on its own, and the reply says which. A result sent with
`abandoned`, or after the host's End began, is refused as `not_completed`.

**One result per session.** A second `ended` is a replay or stale, and the stored result never
changes. Only the game server can produce one: it needs the game's key and a local route nginx
does not forward. Nothing a browser sends can reach it.

## Why this way

- **Fail closed for the record, not the lifecycle.** A faulty result must not leave the Party
  stuck on a finished game. Honouring the end while refusing the result keeps both safe.
- **Separate versioning** lets results evolve to a `v2` without touching the session protocol,
  and keeps old games and old Parties compatible.
- **`game.build` identifies the implementation, not just the rules.** In the LAN Games fork it is
  a SHA-256 digest of the shared runtime plus the game's server-side files, excluding browser
  assets. A Git commit would be natural, but a deployed copy has no trustworthy Git metadata. The
  digest is computed from the files actually loaded and can be recomputed at any commit. A game
  with its own releases may use its release version.

## What it means in practice

The format's reference code is one self-contained file that games copy. Its `build` function
applies the Party's own check, so a game cannot send what would be refused. A game without
results reports exactly as before. The ADR's examples: **BLUFF** (competitive) reports the last
player standing as `won` and the rest `lost`, with only public facts in `data`, never a card. An
**EXPO-shaped** cooperative result, where everyone shares `won` or `lost`, is proven by test
vectors and a stand-in game; EXPO itself was not changed.

**What the Party does with a result.** One function in Party Core is the only place a result
becomes the Party's. Once per session, after it closes, it keeps an in-memory record: the
checked result, session id and outcome, and for each standing the **member** behind the
participant, which only the Party knows.

**What it does not do yet.** Nothing is written to disk, nothing outlives the session object, and
phones are not shown the record. A separate decision (AVR-71) owns storage and retention,
cross-session history, stats and leaderboards, attribution to profiles, privacy and deletion,
and whether phones see results. Also deferred: a manifest field for supported result formats,
reporting it in the status endpoint, an `invalid` outcome and teams. Holding member-linked
results, even in memory, is new for the Party, which is why privacy must be decided before
anything is persisted.

## Later changes

[ADR 0016](0016-service-identities-and-local-trust-boundary.md) changes only where a native
game's result arrives: on Party Core's internal Unix socket rather than loopback TCP. The fork
and the arcade keep the loopback transport. The envelope is unchanged.

## Where it stands today

<span class="avr-badge source">In source</span>, not deployed. The reference code, test vectors
and Party Core's acceptance step are in the Party repository. The Games repository carries
byte-identical copies, compared in both repositories' CI, and BLUFF produces a result there. The
contract stays `avrana.party-games/v0` because the change is additive. No durable history or
profile store exists.

## Related decisions

- [ADR 0006: the session protocol](0006-party-session-protocol.md), which carries the result
- [ADR 0003: identifiers and keys](0003-ids-and-keys.md), why games see only participant ids
- [ADR 0014: native games](0014-native-games-isolated-lan-games-retired.md), which made the Party the owner of durable results
- [ADR 0016: service identities](0016-service-identities-and-local-trust-boundary.md)
- [Game sessions](../architecture/game-sessions.md) and [the Party–Games contract](../games/contracts-and-catalog.md#the-party-games-contract)
