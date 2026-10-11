---
title: Native games and SDK status
description: The isolated native-game boundary, how a native game is provisioned, the validation sequence (BLUFF, Checkers, Spades), and the honest status of the SDK and the .avrgame package format.
sources:
  - avrana-party:docs/adr/0014-native-games-isolated-lan-games-retired.md
  - avrana-party:docs/adr/0016-service-identities-and-local-trust-boundary.md
  - avrana-party:docs/design/GAME-INSTALLATION.md
  - avrana-party:docs/design/NATIVE-GAMES.md
  - avrana-party:docs/runbooks/provision-game.md
  - avrana-party:docs/runbooks/add-a-game.md
  - avrana-party:avrana/ops/provision_game.py
  - avrana-party:avrana/party/registry.py
  - avrana-party:deploy/games/avrana-game@.service
  - avrana-party:deploy/games/avrana-game@.socket
  - avrana-party:avrana/games/standin
  - avrana-party:docs/ROADMAP.md
verified: 2026-10-11
---

# Native games and SDK status

An **Avrana-native game** is one written for this platform: browser clients on each phone, an
authoritative server on the appliance, and Party integration from the start. BLUFF is the first
in product terms. This page explains the isolated **native game process** boundary that such
games are moving to, how far it has got, and why the SDK and the package format have deliberately been left unfrozen.

## The boundary

<span class="avr-badge accepted">Accepted direction</span>
([ADR 0014](../decisions/0014-native-games-isolated-lan-games-retired.md))

Each native game process is an **independent platform consumer**:

- **Its own process**, with its own service identity, secrets and state directory. A game reads
  no other game's state or keys. "Built-in" describes how much the game is trusted. It is not
  permission to share a process.
- **Local IPC over Unix sockets.** nginx and Party Core reach the game through its socket.
  Nothing the game serves is reachable except through the front door.
- **Generic routing from a registry.** Adding a game adds a registry entry and a grant. It
  never means editing nginx.
- **One provisioning path** creates the game's identity, grants, keys and registration. It is
  the same for every game.
- **No game-specific logic in Party Core.** The Party speaks the session protocol and the result
  envelope. It knows roles, the roster, the location and outcomes, never a game's rules or
  screens.
- **One active activity.** The appliance runs one Party doing one thing at a time. Idle games
  should cost nothing, so "runs only while active" is the expectation on a Raspberry Pi.

## What is built

<span class="avr-badge source">In source</span> · not deployed

```mermaid
flowchart LR
  subgraph prov["Provisioning (root, owner-run)"]
    PG["ops/provision-game &lt;slug&gt;"]
  end
  PG -- "writes key" --> KEY[("/etc/avrana-party/<br/>game-keys/&lt;slug&gt;.key")]
  PG -- "writes entry" --> REG[("games.d/&lt;slug&gt;.json<br/>registry")]
  PG -- "enables" --> UNIT["avrana-game@&lt;slug&gt;<br/>socket + service<br/>(dynamic user)"]
  PG -- "reloads" --> CORE["Party Core"]
  REG --> CORE
  NGINX["nginx<br/>/games/&lt;slug&gt;/"] -- "unix socket" --> UNIT
  CORE -- "signed launch / end<br/>(unix socket)" --> UNIT
  UNIT -- "signed ended + result" --> CORE
```

All of these pieces are merged in the Party repository:

- a systemd **unit template** for native games, using socket activation, a dynamic user, a
  key passed in by systemd, a private state directory and Unix-socket networking only;
- a **registry directory** that Party Core reloads without restarting, and Unix-socket
  transport for the session protocol;
- a **generic nginx rule** that maps `/games/<slug>/` to that game's socket and refuses
  outside access to its control endpoints;
- **`ops/provision-game`**, which creates or rotates a game's key, writes its registry entry and
  unit configuration from the appliance grant, enables its socket and reloads Party Core. It
  can also remove a game;
- support for sending phones to a game's **own browser origin** when one is configured, with the
  repository's nginx server block, DNS record and certificate steps for that origin written down
  as an owner-run procedure that has not been run;
- **`ops/prepare-native-games`**, a single owner-run command that readies an appliance for the
  path (it replaces a list of hand edits), tested on a CI runner;
- a **test-only stand-in game**, **Checkers** (Party's side: contract, appliance-profile grant and
  tests) and proof scripts that exercise the whole path on a CI runner with real systemd.

What is not done: no game is provisioned on the appliance, the appliance has not been prepared
for it, and the provisioning runbooks are labelled as proposed procedures that have never run
there. Idle self-stop and resource ceilings are still deferred.

## The validation sequence

The project is deliberately proving the boundary with real games before generalizing it. The
roadmap sets the order:

1. **BLUFF**: the first Avrana-native vertical slice. It proved the Party, tickets, host
   navigation and the console model, while running inside the LAN Games fork.
2. **Checkers**: deliberately simple. It is the first game to live entirely outside the LAN
   Games runtime, launched and ended by Party Core as its own process. Party's side of the
   integration is merged and has a real-systemd proof on a CI runner; this site has not re-read
   the Games repository's side. Playing it on real phones on the appliance is a separate,
   later step.
3. **Spades**: the pressure test, covering teams, private hands, reconnect, scoring and richer
   results. A readiness packet and rule characterization tests exist. A Spades module already lives in the
   LAN Games donor library, and Checkers does too. The native versions that run outside it do not
   exist yet.
4. **Only then** freeze and build the SDK, the package format and the provider abstractions.

The reasoning is a common one: an SDK designed from one example encodes that example's
accidents. The project already had a near miss here. An earlier design document suggested that
the LAN Games session framework already *was* the SDK. ADR 0014 explicitly reversed that and
called the framework "a donor of patterns, not the SDK".

## The SDK

<span class="avr-badge planned">Planned</span>. **No SDK exists.** The Party's protocol source
file says so in its own header. The unit template describes itself as "a field-test runtime
convention, not an SDK".

The intended role of an SDK is clear from the design documents. It would wrap the session
protocol (launch, ticket admission, end, results), the browser-side Party bridge and the
conventions for private per-player views. Then a game author would write rules and screens
instead of plumbing. Its surface will be designed after Checkers and Spades have shown what
actually repeats.

## The `.avrgame` package concept

<span class="avr-badge experimental">Experimental</span> · <span class="avr-badge source">In source</span>
· not deployed. **The format is not frozen and is not a specification.** The Party repository
now has an experimental package format, `avrana.avrgame/experimental.1`: one archive holding a
game's server code and its browser client, a validator and packer, and a minimal installer
(`ops/install-game`) that stages a package on the appliance and registers it through the same
provisioning path first-party native games use. A package is treated as untrusted even when it
validates: it can request, never grant, and the appliance decides what it gets. The installer
has been run only on CI runners and scratch directories, never on the appliance, and upgrades,
rollback, signing and a package repository do not exist. The format cannot be called stable
until the Checkers integration, a review of the four-human BLUFF playtest evidence and the Spades
validation have happened and the owner accepts it.

The concept, from the project's open game installation design, is an installable package for
an Avrana game. Some principles around it are already
accepted:

- **No store.** The intended feel is *"Sure, install that weird GitHub project."* Install a
  package, add a trusted repository or a Git repository, sideload local content. No commercial
  marketplace, payments, reviews or DRM.
- **The package requests; the appliance grants.** A package describes what it needs. The
  appliance decides what it gets, through the same grant mechanism used today.
- **Signatures prove provenance, not safety.** Public-key signatures will say who published a
  package and that it has not changed. A signed package still runs inside the same process,
  identity and browser-origin boundaries as an unsigned one.
- **Trust tiers.** Built-in, trusted and community games are distinguished. Community code is
  expected to need a stronger sandbox tier, which has not been designed yet.

Signing, a community repository, dependency handling, upgrade and rollback and the developer
workflow remain deferred. The design for delivering a package's phone client (portable
HTML, JavaScript and optionally WebAssembly, with an app viewport only as an option) is
described in [Execution models](execution-models.md#portable-web-clients).

## If you want to build a game today

[Building or porting a game today](../developers/starting-a-game.md) gives practical guidance on what you can do
now, and what to wait for.
