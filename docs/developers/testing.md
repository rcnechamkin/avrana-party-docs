---
title: Testing
description: The project's evidence tiers, what each group of test suites proves, how CI runs them, and what is never claimed without real phones.
sources:
  - avrana-party:docs/TESTING.md
  - avrana-party:.github/workflows/offline-checks.yml
  - avrana-party:.github/workflows/cross-repo.yml
  - avrana-party:.github/workflows/service-trust-proof.yml
  - avrana-party:.github/workflows/reconcile.yml
  - avrana-party:.github/workflows/graphify.yml
  - avrana-party:docs/CROSS-REPO.md
verified: 2026-10-09
---

# Testing

Avrana Party is tested in layers, and the project is strict about one thing above all: **a test
only proves what it actually exercised.** A browser test at phone size is not a phone; a check
that the server answered is not a person playing. This page explains how evidence is graded,
what the main groups of tests prove, how CI runs them and what still needs real hardware.

For the commands to run the everyday checks yourself, see
[Local development](local-development.md#run-the-checks).

## Evidence tiers

The engineering testing guide defines three tiers:

| Tier | What it means | Where it runs |
|---|---|---|
| **1: pure** | No appliance, no network, no real browser. Unit tests, module tests, sometimes a virtual machine with fake browser globals. | Laptop, cloud, CI |
| **2: simulated Party** | Only `localhost`: a real nginx with the committed site configuration and stand-in services behind it, or real Chromium against the development server on `127.0.0.1` (a secure context, like the real origin). | Laptop, cloud, CI |
| **3: hardware** | The Raspberry Pi, real phones, the access point, the video encoder, power. The live-appliance suites and the manual runbooks. | Only on the Party Wi-Fi |

Alongside the tiers sits a separate category: **deployed, server-side verification**. That is
evidence that a specific release is installed on the appliance and its services answer
correctly, recorded with exact revisions in dated findings and summarized in
[Deployed system and history](../project/system-map.md).

### Why they are kept apart

The guide insists on three kinds of evidence that must never be blurred: automated source
verification (tiers 1 and 2), deployed server-side verification, and real-phone or human
acceptance (tier 3). The reasons follow from what each one cannot see:

- Chromium at an iPhone's screen size does not behave like iPhone Safari. It does not sleep, lose
  Wi-Fi, apply Safari's WebRTC rules or meet a real captive-portal check. The project does not
  even use Playwright's WebKit offline, because WebKit on Linux is not iPhone Safari.
- A `curl` against the deployed appliance shows that the service is up and its routes behave.
  It says nothing about whether a person on a phone can follow the host into a game.
- A systemd proof on a disposable CI machine shows that systemd behaves as the design assumes.
  It is not evidence about the appliance, which has not been migrated.

So results are always reported at the tier where they were collected, and the project's status
documents say "server-side verified" or "not checked on a phone" explicitly. See
[Navigating the engineering docs](reading-the-specs.md#evidence-tiers) for how those labels appear in
the engineering documents.

## What the test suites prove

The engineering guide lists every suite in detail, with dated results. The summary below groups
them by what they protect. Unless noted, these are tier 1 or tier 2 and run in CI.

### The Party and the session protocol

The largest group exercises Party Core, the Party's server-side authority (see
[The Party](../architecture/party.md)):

- **Party Core itself**: joining and resuming, the server-issued device cookie, presence,
  the host's grace period and succession, versioned host actions, and the one-session lifecycle
  from launching to ended. Randomized "fuzz" runs (150 seeds) drive long sequences of actions and
  check that the rules always hold. HTTP guards (host name, origin, JSON, size) and the absence
  of tokens from responses and logs are tested too.
- **Navigation** ([ADR 0008](../decisions/0008-party-navigation.md)): only committed transitions
  move people; only the host can switch or end; a switch stops the old game before launching the
  next, so there is never more than one activity; stale and concurrent host actions leave exactly
  one result.
- **Pregame setup** ([ADR 0010](../decisions/0010-party-pregame.md)): Play-or-Watch choices,
  host-only Start with each refusal reason, roles fixed once a round starts, late arrivals watch.
- **The console model** ([ADR 0011](../decisions/0011-party-console-model.md)): one location for
  the whole Party, moved only by the host, and the same on every phone; how each page decides
  where a phone should be.
- **The session protocol** ([ADR 0006](../decisions/0006-party-session-protocol.md)): shared test
  vectors for tickets (audience, session, expiry, tampering, replay), then end-to-end runs over
  HTTP with a reference game, in which forged, stale and replayed reports are refused. See
  [Game sessions](../architecture/game-sessions.md).

### The arcade

The arcade's service is tested with its media libraries stubbed out, so no emulator or encoder is
needed. The tests cover the Party starting and stopping the emulator under one lock, refusal of
forged or replayed control messages, recovery from slow or failed starts, and, in source since
early October, ticket admission, stable controller slots, reconnecting in any order within a
60-second hold, and refusal of spectators. A cross-component test runs a real Party Core with the
reference BLUFF and the managed arcade and checks that the two never run at the same time across
switches.

### Contracts, catalog and providers

Tier 1 tests check the shared vocabulary, Game Contract v0, the appliance's grants, per-seat
capability evaluation (including the rule that "unknown" is not the same as "no") and the
freshness of the compiled catalog. The Party ↔ Games **contract checker** proves each repository's
declaration against its own code and compares the two; mutation tests make sure it names the
component that drifted. See
[Repository ecosystem](ecosystem.md#how-the-two-are-kept-compatible).

### The Party shell in a browser

- **Module tests** in Node cover browser-side logic such as capability probing, seat evaluation,
  keep-awake and the service worker.
- **Offline browser tests** (tier 2) run real Chromium at phone sizes against the development
  server: the Party pages, diagnostics, the arcade page's states and the offline copy.
- **Multi-client Party tests** (tier 2) open three browser contexts as "phones" against a real
  Party Core: host and followers, starting and ending for everyone, switching, reloading without
  losing identity or seat, stale and unauthorized actions, setup and the host leaving.
- **Accessibility tests** check contrast, names, reading order, target sizes and keyboard focus on
  every shell page and Party state, also with high contrast and reduced motion requested. They
  have no screen reader, no Safari and no phone settings.
- **Generated files** (built CSS, icons, catalog) are checked to be up to date.

### Infrastructure and operations

- **nginx**: static checks on the committed site, plus a run of a **real nginx** with that site
  on high ports (tier 2): the captive probe unchanged on HTTP, `/party/` HTTPS-only, and Party
  Core behind `/party/api/` with internal paths never reaching it.
- **Log bounds**: the telemetry rotation rule and journald limits, with a real `logrotate` run.
- **Deployment tooling**: the [deployment manifest, status document and smoke
  checks](../project/deployment.md) with fake probes; the deployment script itself against
  throwaway checkouts with a recording stand-in for `systemctl`, including rollback and a failed
  smoke run (Linux only).
- **Service boundary checker** ([ADR 0016](../decisions/0016-service-identities-and-local-trust-boundary.md)):
  evaluates recorded facts from a host, including the facts recorded from the appliance on
  2026-10-03.
- **Rebuild procedure**: rehearsed on a simulated host. The commands a real run would execute are
  recorded, never run, so this is evidence about the procedure, not about a device.

### Proofs on disposable machines

Two jobs need root and systemd, so they run only on throwaway CI machines and **never on the
Pi**. One proves that the systemd features the service-identity design relies on (dynamic users,
credential loading, state directories, socket permissions) behave as the ADR assumes. The other
provisions the stand-in native game, has a real Party Core launch and end a full session with it
over socket activation, and checks that rotating or removing the game is refused mid-session.
Both are tier 2 evidence about systemd, not about the appliance or a product game.

### Across the two repositories

The **provider browser suite** runs the real Party shell and Party service against the real games
server from a checkout of the Games repository, on localhost: protocol join and resume, launch,
tickets and End with real BLUFF; reloads and lost ticket requests keeping a player's identity and
hand; forged or stale tickets never taking another seat or seeing private state; and the
full-screen setup with players' private hands versus the spectator view. The Games repository's
own cross-repository tests drive its server from a real Party service. These are still Chromium
at phone sizes, not real phones.

### Experimental branches

PlayStation title profiles, Personal Viewport geometry and the Party lifecycle model have their
own suites on experiment branches. Their recorded results are historical evidence for research,
not verification of anything on `main`.

## How CI runs them

The Party repository runs these GitHub Actions workflows:

| Workflow | When | What |
|---|---|---|
| **Offline checks** | Every pull request, every push to `main`, on demand | Repository integrity and generated-file freshness; on pull requests, a gate that fails if historical documents are edited without a label; the Party side of the contract check; the two committed nginx site files being identical; all Python unit tests with a real nginx and logrotate; Node module tests; offline browser tests; multi-client Party browser tests |
| **Cross-repo contract** | Every pull request, every push to `main`, on demand | Checks out the Games repository at the branch with the same issue number (otherwise `main`), then runs the contract checker on both, the Games cross-repository tests against the real Party service (not allowed to skip) and the provider browser suite |
| **Service trust proof** | Pull requests that touch the service code, contracts, deployment files or experiments; on demand | The two disposable-machine proofs described above |
| **Drift reconciliation** | Weekly and on demand | Compares Linear, GitHub and both repositories and publishes a report. It never fails the build and never writes anywhere. The appliance is reachable only on the Party network, so deployed-version checks run from a laptop instead |

A further scheduled workflow regenerates derived code-context files for agents; it tests nothing
about the product. The Games repository runs its own CI independently, including its own
cross-repository job. Nothing in any workflow deploys.

## The live-appliance suites

A separate set of Playwright tests targets the **real appliance**: the captive probe, the games
hub, the arcade page, video streaming, stream statistics and two-player play. Heavier soak and
fault-injection runs put real load on the Pi.

These need a laptop joined to the Party Wi-Fi with local name resolution set up for the appliance,
and the soak and fault runs also need the owner's explicit go-ahead. They **cannot run in the
cloud or in CI**: outside the Party network the appliance's name does not resolve, so they fail
before reaching any product code. A failure there is an environment problem, not a product
regression. The guide also warns never to run heavy suites on the Pi during a power measurement,
because every remote session is a burst of CPU load.

!!! danger "Live suites need authorization"

    `npm test`, `test:all`, `soak` and `fault` act on the live appliance. Running them is not a
    routine development step. Use the offline suites for everyday work.

A few read-only tools also run on the Pi itself, such as a topology check and a radio-capacity
sampler. The capacity test, measuring how many phones the access point really serves, has not
been run.

## What is never claimed from a lower tier

No automated test covers the following. They are checked manually, with the runbooks, on real
hardware, and the guide asks for release revisions, the network path and the actual devices to be
recorded before any acceptance is claimed:

- real iPhone Safari and Android Chrome behaviour, including offline captive probes,
  `party.local`, sleeping and waking, and WebRTC on iOS;
- real Wi-Fi with several phones, and the access point's client ceiling;
- H.264 encoding on the Pi's hardware encoder;
- input-to-screen latency;
- power under load.

Even the live-appliance browser tests do not establish human interaction on real phones. As of
the guide's last reconciliation, real-phone acceptance of the console model, the arcade's
controller reservations and four-player arcade play is still pending; see
[Project status](../status/index.md#known-limitations).
