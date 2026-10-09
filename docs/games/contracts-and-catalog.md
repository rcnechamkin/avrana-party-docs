---
title: Contracts, catalog and grants
description: How a game is described (the game contract), how the appliance decides what is installed (grants), how the catalog is built, and how the Party and Games repositories stay compatible.
sources:
  - avrana-party:docs/adr/0004-full-mode-contracts-and-providers.md
  - avrana-party:docs/design/PARTY-GAMES-CONTRACT.md
  - avrana-party:contracts/games/bluff.json
  - avrana-party:contracts/appliances/avrana-pi4.json
  - avrana-party:contracts/capabilities.v0.json
  - avrana-party:contracts/party-games.v0.json
  - avrana-party:avrana/contracts/game.py
  - avrana-party:avrana/contracts/catalog.py
  - avrana-party:avrana/contracts/appliance.py
  - avrana-party:docs/GENERATED.md
  - avrana-party:tools/contract_check.py
  - avrana-party-games:provider/avrana-contract.json
verified: 2026-10-09
---

# Contracts, catalog and grants

Avrana Party relies on a few small machine-readable documents rather than conventions or
documentation. They answer three different questions:

1. **What is this game, and what does it need?** The *game contract*, written from the game's
   side.
2. **Is it installed here, and what is it allowed to do?** The *appliance grant*, written from
   the appliance's side.
3. **Do the Party and the Games server agree on how to talk?** The *Party ↔ Games contract*,
   checked in CI on both sides.

## The game contract

<span class="avr-badge source">In source</span>, schema `avrana.game/v0`

Each game has one JSON contract in the Party repository under `contracts/games/`. An excerpt of
BLUFF's, with some fields omitted (the
[full file](https://github.com/rcnechamkin/avrana-party/blob/main/contracts/games/bluff.json) is
authoritative):

```json
{
  "contract": "avrana.game/v0",
  "id": "bluff",
  "name": "BLUFF",
  "summary": "Hidden roles, bold claims. Your cards stay on your phone.",
  "kind": "native",
  "players": {"min": 2, "max": 6},
  "screen": "no_tv_needed",
  "late_join": "spectator_only",
  "spectators": "watch",
  "runtime": {"type": "lan_games_module", "permissions": ["party_roster"]},
  "presentations": [
    {
      "id": "phone_table",
      "method": "browser_native",
      "requires": {"device": ["websocket"], "runtime": ["runtime.lan_games"]}
    }
  ]
}
```

`screen` is one of `no_tv_needed`, `tv_optional` or `tv_required`. `late_join: spectator_only`
means latecomers watch until the next round. `permissions` lists what the game asks the
appliance for, and `presentations` are tried in order for each phone.

A few design choices are visible here:

- **Presentations are ordered and evaluated per phone.** A game can offer several ways to take
  part, for example a native browser table, a shared video stream or a controller-only mode,
  each with the device and appliance capabilities it needs. Each phone gets the first one it can
  support, or the game's declared fallback.
- **A Personal Viewport is a method, not a synonym for cropping.** The schema allows a
  viewport to be a crop, a dedicated stream, a browser renderer or a private panel.
- **Capability names come from one vocabulary.** `contracts/capabilities.v0.json` names device
  capabilities (WebSocket, WebRTC, H.264 decoding, wake lock and others) and appliance
  capabilities (the LAN Games runtime, RetroArch, a virtual gamepad, a shared stream, Personal
  Viewport variants). The browser and the server evaluate them with two implementations pinned
  to the same test vectors.
- **The contract describes and requests. It never grants.** The validator rejects fields that
  only the appliance may set, such as an entry point, a trust tier or granted permissions, if a
  game tries to declare them.

The project intends this contract to grow into the **one canonical per-game manifest** from
which everything else is derived or checked. It would carry player counts, Party behaviour,
runtime and presentation requirements, permissions, resources, lifecycle bounds and supported
protocol versions. That avoids competing metadata layers.

## The appliance grant

An appliance profile (`contracts/appliances/avrana-pi4.json` for the current Pi) lists:

- the **providers** installed on that appliance, each marked `live`, `experiment` or `planned`,
  for example the LAN Games runtime, RetroArch, the virtual gamepad and the shared WebRTC
  stream;
- the **installed games**, each with its entry path, trust tier (`builtin`, `trusted` or
  `community`), granted permissions and, for native games, how to run it.

The current Pi profile grants BLUFF, EXPO and *Gauntlet II*. The experimental PlayStation titles
appear in the catalog as experimental, with no entry point.

The grant is checked when the catalog is built: an appliance cannot grant a permission the game
did not request (ADR 0004). In current source, granted permissions are read only by those
build-time checks. Nothing reads them while a game runs. The real limits on what a game can do
are meant to come from the process and identity boundaries described in
[Trust boundaries](../architecture/trust-boundaries.md).

## The catalog

A build step (`npm run catalog`) compiles the game contracts and the appliance profile into the
static catalog that Party Home reads. The compiled catalog is committed. CI fails if it is stale
or if a contract is invalid. The project's
[GENERATED](https://github.com/rcnechamkin/avrana-party/blob/main/docs/GENERATED.md) document
lists which files are generated in this way and must not be edited by hand.

## The Party ↔ Games contract

<span class="avr-badge source">In source</span>, `avrana.party-games/v0`

The Party and the Games server live in different repositories, with different CI and release
cadences. To stop them drifting apart silently, each side declares the boundary in a file:

| Repository | File | Declares |
|---|---|---|
| Party | `contracts/party-games.v0.json` | what Party **implements** |
| Games | `provider/avrana-contract.json` | what Games **requires** |

Both name the same components: the session protocol version, plus the SHA-256 of its reference
file and test vectors; the result envelope schema and its reference file; the browser bridge
script; the ticket, launch, end and `ended` routes; the launch integration; the environment
variable names; and a snapshot of the games catalog. The Games repository **vendors** byte-for-byte
copies of the Party's reference files for the protocol, the result envelope and the bridge
script, so hashes are enough to prove that both sides run the same code.

A dependency-free checker (`tools/contract_check.py`) proves each declaration against its own
repository's code, then compares the two. It runs in CI on both sides. Each side runs it against
the other repository's branch with the same issue id, so paired changes are tested together.
Each failure names the drifted component and the file to change. The rules for changing the
contract are deliberately conservative. Additive, backward-compatible changes keep `v0`. The
version is bumped only when a Games build made for the old contract would stop working with the
new Party.

!!! note "This contract describes today's boundary"

    `v0` describes the Party and the LAN Games fork as they actually run: one browser origin
    and the fork's launch integration. It is not the target architecture. When the separate game
    origin and isolated native games land, the declarations will change with them, through the
    same paired-change procedure.

Player identity, the chat transport and service-worker scopes are deliberately left out of this
contract. They are platform ownership rules, enforced by tests on each side, rather than a
versioned interface.
