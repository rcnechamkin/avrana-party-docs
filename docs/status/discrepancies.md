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
  - avrana-party:docs/adr/0004-full-mode-contracts-and-providers.md
  - avrana-party:docs/adr/0006-party-session-protocol.md
  - avrana-party:docs/adr/0007-host-authoritative-launch.md
  - avrana-party:docs/adr/0008-party-navigation.md
  - avrana-party:docs/adr/0009-arcade-party-provider.md
  - avrana-party:docs/adr/0011-party-console-model.md
  - avrana-party:docs/adr/0012-limited-mode-party-survives-https-loss.md
  - avrana-party:docs/design/PARTY-PLATFORM.md
  - avrana-party:docs/design/GAME-UX-CONTRACT.md
  - avrana-party:docs/design/ACCESSIBILITY.md
  - avrana-party:docs/design/STATUS-ENDPOINT.md
  - avrana-party:docs/TESTING.md
  - avrana-party:docs/findings/2026-09-20-audio-ratchet-and-recovery.md
  - avrana-party:arcade/index.html
  - avrana-party:arcade/README.md
  - avrana-party:deploy/party-core/party-core.example.json
  - avrana-party:.github/workflows/cross-repo.yml
  - avrana-party-games:server.py
  - avrana-party-games:deploy/avrana-party-session.conf
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
`docs/design/BROWSER-ORIGINS.md` (plain-language edition: [Browser origins](../design/browser-origins.md))
calls `Path=/` "safe once game servers no longer share the host", which implies an ordering
that the current source does not enforce. The practical risk today is limited: every service
already runs as one Unix user, and the games are first-party code. But the stated invariant and
the code disagree. *This needs confirmation from the project's engineers. It is reported here,
not concluded.*

## 2. The system map predates most October work

The engineering system map, `docs/SYSTEM.md` (plain-language edition: [Deployed system and history](../project/system-map.md)),
was reconciled on 2026-10-01. It does not mention native-game provisioning, the generic game route, the
Unix-socket game link, origin navigation, Limited Mode steps 1–2, the service-user unit or the
`__Host-` cookie. That is correct for a document about *deployed* state, but the file is also
headed "machines, repositories, branches, runtime paths".

The deployed revisions are also inconsistent between sources:

- SYSTEM gives the latest verified production as Party `956b968` and Games `c6d7b52`
  (2026-09-29).
- The AVR-130 deployment record, `docs/findings/2026-10-02-avr130-deploy.md`,
  of 2026-10-02 includes a read-only inspection of the appliance. It found Party `a32b7b4` and
  Games `0b4e9d2`, and calls that Games revision "already deployed". It then staged a deployment
  of Party `bb7364c` that was waiting for the owner.
- The deploy runbook, `docs/runbooks/deploy.md`, mentions in passing that the appliance was at `bb7364c` on 2026-10-04.
- The Linear project reports the console model as deployed.

No dated finding records a deployment after 2026-09-29. The project's Linear workspace tracks
capturing the exact deployed revisions as an open task.

## 3. Status lines and amendments older than the code

The ADRs are amended by adding dated notes rather than rewriting them. Several notes have not
kept up with the code.

**Status lines that say "not implemented" for things now in source.** In each case "not
deployed" remains true; only "not implemented" is stale.

- **ADR 0014** is headed "not implemented", but the registry, generic routing, provisioning
  script and native-game unit template it calls for are in source. It also still lists "the
  registry file format and where it lives" as open, although source has chosen one: a JSON file
  per game under `/etc/avrana-party/games.d/`.
- **ADR 0016** is headed "accepted · not implemented · not deployed". Its phase-one pieces are in
  source: the Party Core service user and hardening, the migration script, the boundary
  checker, the native-game unit template and credential loading.
- **GAME-PLATFORM-ARCHITECTURE**'s "Accepted direction" table, reconciled on 2026-10-02, lists
  generic routing and provisioning as "not built", and the result schema as "not yet designed".
  **PARTY-PLATFORM** says the same about the result schema and calls Limited Mode "not
  implemented". ADR 0015 accepted and implemented the schema on 2026-10-03, and Limited Mode
  steps 1–2 are in source.

**Amendments and notes that the code has overtaken:**

- **ADR 0004**'s header says "Nothing in this ADR is deployed". The Full Mode shell has been
  deployed since 2026-09-27.
- **ADR 0006**'s host-claim amendment of 2026-10-04 says "not merged". The host claim on tickets
  and the host question route are on `main`.
- **ADR 0007** still says production has "no Party service yet". Party Core was deployed on
  2026-09-29.
- **ADR 0008** still describes the "Join them" banner, and a rule that a game ending by itself
  leaves navigation alone. The console model removed the first. Since a 2026-10-02 amendment to
  ADR 0011, an *abandoned* round sends the Party home. Neither change is marked in ADR 0008.
- **ADR 0009** was never amended for ticket admission. Its "accepted limits in v0" still say the
  arcade does not check tickets. Ticket admission and seat holds are in source, and only the
  arcade's README and runbook describe them.
- **ADR 0011**'s status line and the arcade README's header still say its deployment is pending.
  The owner reports it as deployed, and no dated finding records that.
- **ADR 0012**, decision D5, says first-party games stay on the Party's origin in Limited Mode.
  The port-80 nginx rules in source serve no native game over plain HTTP; only BLUFF and EXPO
  are routed. The ADR does not mention that narrowing.
- **ADR 0013**'s amendment still lists "the paired Games change (vendor the shim); the arcade
  page" as to-do. Its status line says those steps are in source, and the vendored shim exists
  in the Games repository.

**Design documents with stale details:**

- **LIMITED-MODE** calls folding the Limited Mode notice an open question in one section and
  describes it as folding in another. The shell implements the fold.
- **BROWSER-ORIGINS**' real-phone checklist expects a switch to another game to pass through
  Party Home. Since 2026-10-02 the Party goes straight to the next game's setup.
- **GAME-UX-CONTRACT** still records the away and host markers as opacity and an icon. Its own
  later rule and the shell now use the visible words "Host" and "Away". It also says the touch
  target test checks height only, but the test checks both directions.
- **ACCESSIBILITY** points to the old `experiments/` locations for Party Home and the
  accessibility block, audits the LAN Games hub that source no longer serves, and says a smoke
  test runs in WebKit when the current configuration is Chromium only.
- **TESTING**'s list of offline CI steps omits several that the workflow runs: the multi-client
  Party browser tests, the historical-edit gate and the Graphify checks.
- **The 2026-09-20 arcade finding** says the fixes for its two reliability defects were not
  started. Fixes for both now exist in `arcade/stream.py`, with no record of hardware
  verification.
- **The arcade page** still tells a phone that cannot get a ticket to "Join the party from Party
  Home", although there has been no Join button since the console model.
- **The example Party Core configuration** points its status checkout paths at the operator's
  home directory. The Party Core unit in source now runs code from `/opt/avrana-party/current`.

## 4. The native runtime type

ADR 0014's supersession section says `lan_games_module` becomes legacy and "`process` is the
native runtime type". The game-contract validator (`avrana/contracts/game.py`) accepts only
`lan_games_module`, `emulator_profile` and `external`. The native stand-in game declares
`external`.

## 5. Stale guidance for adding a game

- The Party's [add-a-game runbook](../developers/starting-a-game.md)
  points to `experiments/manifests/` and `ps1/profiles.py`, which are not on `main`. Game
  metadata now lives in `contracts/games/`, and the PlayStation profiles in
  `avrana/providers/ps1.py` and `ps1/titles/`. The runbook names the registry, manifest and
  provisioning as work tracked in Linear, but does not describe the provisioning script, the
  registry or the stand-in game that now exist.
- The Games repository's `ADDING_A_GAME.md` still describes adding a module to the standalone
  hub on port 8096. That guide is legacy: in the Party repository's source, nginx no longer
  routes to the hub or to any title other than BLUFF and EXPO. The Games server itself keeps
  the hub, and standalone admission stays on until the owner sets
  `AVRANA_STANDALONE_ADMISSION=0`.

## 6. Stale code comments

- The `avrana/party/service.py` module docstring says the nginx `/party/api/` step "is NOT
  done", but the committed site and the deployment evidence show it is done. The same docstring
  describes an explicit Join, which the console model replaced with automatic presence.
- The `avrana/party/core.py` docstring lists profiles and results as out of scope. Members now
  carry avatars, and sessions carry results.
- A comment in `web/party/lib/party-client.js` describes the device cookie as `Path=/party/`.
  The "What is true today" section of `docs/design/LIMITED-MODE.md`, and `BROWSER-ORIGINS.md`,
  give the same old description. In LIMITED-MODE it is tagged as evidence
  read from an earlier commit.

## 7. BLUFF's minimum player count

The Games registry entry for BLUFF allows one player in solo mode. BLUFF's Party game contract
says a minimum of two, and the compiled Party catalog uses two. In a Party, the contract governs.

## 8. The "live authority" is probably not live

AGENTS, SYSTEM and the status-endpoint design all name `/party/api/status` on the appliance as
the answer to "what is running". The endpoint was merged on 2026-10-02. Every build recorded or
reported on the appliance (`956b968`, `a32b7b4`, `bb7364c`) predates it, and the deployment
script that would install it has never been run there. So the appliance most likely does not
serve it yet. This site's [Deployment](../project/deployment.md#the-status-endpoint) page says
so.

## 9. An unrecorded deployment around 2026-09-30

The inspection in the 2026-10-02 AVR-130 deployment record found the appliance's Party checkout
at `a32b7b4`, with a web release built on 2026-09-30. No finding records that deployment. The
system map still names `956b968` as both the checkout and the current web release.

## 10. Is the Games repository private?

SYSTEM and TESTING describe `avrana-party-games` as private. The cross-repository CI workflow
says "Both repositories are public, so no token is needed", and checks the Games repository out
without credentials. GitHub currently lists it as public.

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
