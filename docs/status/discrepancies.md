---
title: Known discrepancies
description: Places where the engineering repositories' documents, code comments and implementation disagree, found while writing this site.
sources:
  - avrana-party:docs/SYSTEM.md
  - avrana-party:docs/GAME-PLATFORM-ARCHITECTURE.md
  - avrana-party:docs/adr/0003-ids-and-keys.md
  - avrana-party:docs/adr/0013-party-and-game-browser-origins.md
  - avrana-party:docs/adr/0014-native-games-isolated-lan-games-retired.md
  - avrana-party:docs/adr/0016-service-identities-and-local-trust-boundary.md
  - avrana-party:docs/design/BROWSER-ORIGINS.md
  - avrana-party:docs/design/LIMITED-MODE.md
  - avrana-party:docs/findings/2026-10-02-avr130-deploy.md
  - avrana-party:docs/runbooks/add-a-game.md
  - avrana-party:docs/runbooks/deploy.md
  - avrana-party:avrana/party/identity.py
  - avrana-party:avrana/party/service.py
  - avrana-party:avrana/party/core.py
  - avrana-party:web/party/lib/party-client.js
  - avrana-party:contracts/games/standin.json
  - avrana-party:avrana/contracts/game.py
  - avrana-party:avrana-party.nginx
  - avrana-party-games:ADDING_A_GAME.md
  - avrana-party-games:games/registry.py
verified: 2026-10-09
---

# Known discrepancies

Explaining a system closely turns up places where its sources disagree with each other. This
page records the disagreements known as of the
[revisions this site was checked against](../about/this-documentation.md#source-revisions)
(first recorded 2026-10-09).

It is a **report to the engineering repositories, not a correction of them.** Each item should
be resolved there, through the project's normal process. Once it is fixed upstream, the entry is
removed here. Where this site had to pick a side, it followed the code and said so on the
relevant page.

Items are ordered roughly by how much they could mislead a reader.

## 1. The device cookie and same-origin game servers

**Observed.** ADR 0003 says the device token never reaches a game server, because "its cookie
is scoped to the party path and nginx strips cookies on game locations". ADR 0013 repeats that
nginx strips it. In current source:

- Party Core now issues the device cookie as `__Host-avrana_device` with `Path=/`, as part of
  the browser-origin work (`avrana/party/identity.py`). That change was merged on 2026-10-03,
  after any revision recorded on the appliance.
- The committed nginx site contains no directive that removes the `Cookie` header on any
  location. The repository's available history shows no such directive ever having been
  committed. Until now, the protection came from the old cookie's `Path=/party/` scope.
- Game pages are still served from the same host as the Party, because no separate game origin
  is configured yet. Besides `/games/` and `/arcade/`, the HTTPS server's catch-all location
  forwards every other path to the games server.
- The module docstring of `identity.py` itself says `Path=/` "is safe because game servers do
  not share the Party's host name". That is the target state of ADR 0013, not the current
  configuration.

**Why it matters.** Taken together, these suggest that once this source is deployed, browsers
would send the device cookie with requests to same-origin game servers. The design document
[BROWSER-ORIGINS](https://github.com/rcnechamkin/avrana-party/blob/main/docs/design/BROWSER-ORIGINS.md)
calls `Path=/` "safe once game servers no longer share the host", which implies an ordering
that the current source does not enforce. The practical risk today is limited: every service
already runs as one Unix user, and the games are first-party code. But the stated invariant and
the code disagree. *This needs confirmation from the project's engineers. It is reported here,
not concluded.*

## 2. The system map predates most October work

[SYSTEM](https://github.com/rcnechamkin/avrana-party/blob/main/docs/SYSTEM.md) was reconciled
on 2026-10-01. It does not mention native-game provisioning, the generic game route, the
Unix-socket game link, origin navigation, Limited Mode steps 1–2, the service-user unit or the
`__Host-` cookie. That is correct for a document about *deployed* state, but the file is also
headed "machines, repositories, branches, runtime paths".

The deployed revisions are also inconsistent between sources:

- SYSTEM gives the latest verified production as Party `956b968` and Games `c6d7b52`
  (2026-09-29).
- The [AVR-130 deployment record](https://github.com/rcnechamkin/avrana-party/blob/main/docs/findings/2026-10-02-avr130-deploy.md)
  of 2026-10-02 includes a read-only inspection of the appliance. It found Party `a32b7b4` and
  Games `0b4e9d2`, and calls that Games revision "already deployed". It then staged a deployment
  of Party `bb7364c` that was waiting for the owner.
- The [deploy runbook](https://github.com/rcnechamkin/avrana-party/blob/main/docs/runbooks/deploy.md)
  mentions in passing that the appliance was at `bb7364c` on 2026-10-04.
- The Linear project reports the console model as deployed.

No dated finding records a deployment after 2026-09-29. The project's Linear workspace tracks
capturing the exact deployed revisions as an open task.

## 3. Status lines older than the code

- **ADR 0014** is headed "not implemented". The registry, generic routing, provisioning script
  and native-game unit template it calls for are in source.
- **ADR 0016** is headed "accepted · not implemented · not deployed". Its phase-one pieces are in
  source: the Party Core service user and hardening, the migration script, the boundary
  checker, the native-game unit template and credential loading.
- **GAME-PLATFORM-ARCHITECTURE**'s "Accepted direction" table, reconciled on 2026-10-02, lists
  generic routing and provisioning as "not built". It also says the result schema is "not yet
  designed", although ADR 0015 accepted it on 2026-10-03 and implemented it.

In each case "not deployed" remains true. Only "not implemented" is stale.

## 4. The native runtime type

ADR 0014's supersession section says `lan_games_module` becomes legacy and "`process` is the
native runtime type". The game-contract validator (`avrana/contracts/game.py`) accepts only
`lan_games_module`, `emulator_profile` and `external`. The native stand-in game declares
`external`.

## 5. Stale guidance for adding a game

- The Party's [add-a-game runbook](https://github.com/rcnechamkin/avrana-party/blob/main/docs/runbooks/add-a-game.md)
  points to `experiments/manifests/` and `ps1/profiles.py`, which are not on `main`. Game
  metadata now lives in `contracts/games/`, and the PlayStation profiles in
  `avrana/providers/ps1.py` and `ps1/titles/`. The runbook names the registry, manifest and
  provisioning as work tracked in Linear, but does not describe the provisioning script, the
  registry or the stand-in game that now exist.
- The Games repository's `ADDING_A_GAME.md` still describes adding a module to the standalone
  hub on port 8096, which is retired in source.

## 6. Stale code comments

- The `avrana/party/service.py` module docstring says the nginx `/party/api/` step "is NOT
  done", but the committed site and the deployment evidence show it is done. The same docstring
  describes an explicit Join, which the console model replaced with automatic presence.
- The `avrana/party/core.py` docstring lists profiles and results as out of scope. Members now
  carry avatars, and sessions carry results.
- A comment in `web/party/lib/party-client.js` describes the device cookie as `Path=/party/`.
  The "What is true today" section of
  [LIMITED-MODE](https://github.com/rcnechamkin/avrana-party/blob/main/docs/design/LIMITED-MODE.md)
  and BROWSER-ORIGINS give the same old description. In LIMITED-MODE it is tagged as evidence
  read from an earlier commit.

## 7. BLUFF's minimum player count

The Games registry entry for BLUFF allows one player in solo mode. BLUFF's Party game contract
says a minimum of two, and the compiled Party catalog uses two. In a Party, the contract governs.

## Clarifications rather than contradictions

These are not errors. They are places where a reader of the engineering documents could easily
draw the wrong conclusion:

- **Party Chat** is described as a Party feature, and the Party does own its interface. Its
  transport still runs on the LAN Games fork's chat service, using that fork's own
  browser-generated token.
- **The System Admin role** appears in the platform design. No code implements it yet.
- **The catalog snapshot** in the Party ↔ Games contract still lists about thirty LAN Games
  titles, although only BLUFF and EXPO are offered. This is intentional: the snapshot is the
  contract artefact, and it supplies those two games' display text.
