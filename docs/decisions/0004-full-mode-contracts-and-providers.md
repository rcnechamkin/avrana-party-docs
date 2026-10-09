---
title: "ADR 0004: Full Mode origin, contracts and providers"
description: The canonical HTTPS origin, per-seat capability evaluation, Game Contract v0, three provider interfaces, the offline copy and the three test tiers.
sources:
  - avrana-party:docs/adr/0004-full-mode-contracts-and-providers.md
  - avrana-party:contracts/capabilities.v0.json
  - avrana-party:avrana/contracts/evaluate.py
  - avrana-party:web/party/lib/evaluate.js
  - avrana-party:avrana/contracts/game.py
  - avrana-party:contracts/appliances/avrana-pi4.json
  - avrana-party:avrana/providers/base.py
  - avrana-party:web/party/sw.js
  - avrana-party:web/party/version.json
  - avrana-party:.github/workflows/offline-checks.yml
  - avrana-party:docs/SYSTEM.md
verified: 2026-10-09
---

# ADR 0004: The Full Mode origin, platform contracts and provider boundaries

!!! abstract "At a glance"
    **Decided:** 2026-09-26 · **Status:** D1 accepted; D2–D6 proposed, then merged · Full Mode shell <span class="avr-badge deployed">Deployed</span> · the HTTPS-only recovery stance superseded by ADR 0012
    The Party's home is `https://party.avrana.net/party/`, with no HSTS so an expired
    certificate stays escapable. The ADR also sets how phone capabilities are judged (per seat,
    by observation), what a game contract says, the three kinds of provider behind a game, what
    the offline copy may do, and three tiers of test evidence.

## The problem

By late September 2026 the appliance had a working trusted HTTPS address, `party.avrana.net`,
live since 2026-09-25. Several things needed settling around it at once: where the Party's own
pages live and how they coexist with the existing captive-portal and LAN Games traffic; how to
decide what a given phone can do; what a game declares about itself versus what the appliance
grants it; how the emulator, input and video pieces of the arcade are separated; and what
counts as evidence that something works. This ADR records those six decisions, labelled D1 to D6.

## What was decided

### D1. The canonical origin is `https://party.avrana.net`

An *origin* is the scheme, host and port a browser uses to separate cookies and storage.

- Avrana's own pages live under `/party/`, on the HTTPS server only.
- The plain-HTTP server is unchanged. Apple's captive-portal probes still get their expected
  answer, other paths still reach LAN Games, and there is no global redirect.
- **No HSTS, ever.** HSTS would tell browsers to refuse anything but valid HTTPS for the domain,
  which would trap phones if the certificate ever expired.
- The TLS private key never leaves the appliance, and no private certificate authority is
  installed on phones.

Because HTTP and HTTPS are separate origins, a phone that switches between them looks like two
devices. So Party identity is scoped to the HTTPS origin, and its cookie is `Secure`. Still open
at the time: an HTTP "doorway" page that probes HTTPS and hands off, a redirect for the plain-HTTP
Party host name, and whether the site root becomes Party Home.

### D2. Capability Engine v0: per seat, observed, never guessed from the user agent

The engine keeps five things apart: what the **device** can do (observed in the browser), the
**seat** (a role in this game), what the appliance's **runtime** offers, what the **game**
requires, and the result, a **presentation strategy** for each seat.

- Each capability is `yes`, `no`, `partial` or `unknown`, and **unknown is never treated as no**.
- Probes never trigger a permission prompt.
- A weak phone changes only its own seat: it gets a fallback (such as watching, or TV controls)
  or a plain explanation. The party never drops to the lowest common denominator. Only runtime
  limits can affect every seat.
- The capability report is advice for the interface, never an input to authorization.

The evaluation exists twice, in Python on the server and in JavaScript in the browser, kept in
agreement by shared test vectors.

### D3. Game Contract v0

Each game is described by a JSON contract, which grew out of an earlier experimental manifest
(old manifests can be converted). It adds:

- an ordered list of **presentations**: a native browser game, a shared stream, a personal
  viewport, controller-only, or a native app, each with the device and runtime capabilities and
  roles it needs;
- a per-seat **fallback**;
- the runtime permissions and resources the game requests;
- an optional package block and namespaced extensions.

A *personal viewport* is a method with a defined kind (a crop, a dedicated stream, a
browser-side renderer or a private panel), not a synonym for cropping.

The key principle is **the package describes and requests; the appliance decides.** A separate
appliance file holds the grants: entry path, health path, trust tier and granted permissions.
The contract validator rejects grant-side keys by name, and a grant cannot give a permission the
contract did not request.

### D4. Three provider boundaries, with policy kept in Avrana

A *provider* is the code that actually runs a game's emulator, handles its input or delivers its
picture. The ADR defines three small interfaces (Python protocols, with no framework or registry):

| Boundary | What it does | First implementation (the arcade) |
|---|---|---|
| **Runtime provider** | starts, checks and stops the program that runs the game | RetroArch as a child process, with its network command port kept off |
| **Input provider** and **virtual controller** | opens a controller and applies full input snapshots | a Linux virtual gamepad |
| **Presentation provider** | delivers the picture, for example requesting a fresh keyframe | the arcade's single shared video encode |

Later candidates were named for each, such as the PlayStation launcher, per-player key banks and
dedicated streams. Each provider declares what it offers, and the appliance profile lists them as
live, experimental or planned.

Some things stay with Avrana whatever the provider: mapping seats to controller slots, tickets,
releasing stale or backgrounded input, rate limits, personal-viewport policy, the encoder budget,
lifecycle screens, and the rule never to expose an emulator's control port.

### D5. The offline copy is a convenience, not a recovery mechanism

A service worker (a script the browser keeps to serve pages offline) is scoped to `/party/`. It is
network-first for everything, so a phone on the Party Wi-Fi always runs the current build. Its
cache answers only when the appliance cannot be reached, and the page then says so. It never
caches the games hub, the arcade, the Party API, party state or identity.

There are three kill switches, from mildest to most drastic: a flag in the published version
file, a self-destructing worker build, and a manual "Remove offline copy" button on the
diagnostics page. The worker has limits: with an expired certificate it may still show the cached
page while every live call fails, and Safari evicts its storage after about a week unused.

### D6. Three test tiers

- **Tier 1:** pure tests, no appliance.
- **Tier 2:** a simulated Party on one machine, with real nginx, stand-in services and a real
  Chromium browser.
- **Tier 3:** the real appliance, phones, Wi-Fi, HDMI and encoder.

CI runs Tiers 1 and 2. Tier 3 stays manual, and results from a lower tier are never reported as
hardware validation.

## Why this way

Most reasons are given inline above. The thread running through them is that the appliance
must stay escapable and honest. No HSTS and no private certificate authority keep a phone from
being trapped by an expired certificate. Per-seat, observed capabilities keep one weak phone from
degrading everyone's game. Keeping grants out of the game contract means a game can never award
itself permissions. Separating test tiers keeps a simulated pass from being mistaken for proof on
real hardware.

## What it means in practice

Deploying the shell was a one-time, owner-approved nginx change to the HTTPS server plus an
install script with rollback and kill-switch options. The arcade's server now imports the shared
Avrana code from the repository, and its statistics gained a providers section. Follow-ups noted
at the time included Party Home adopting the shell's capability and keep-awake libraries, a
second ticket version bound to the seat, and making the arcade exit on a fatal error so systemd
restarts it.

## Later changes

**2026-10-02.** The original text is left as written; two later decisions change parts of D1:

- [ADR 0012](0012-limited-mode-party-survives-https-loss.md) supersedes "HTTP is not a recovery
  path for the Party page". At the time, the shell sent guests to the plain-HTTP LAN Games hub when
  HTTPS failed. The accepted target is now a **Limited Mode** in which the Party itself stays
  usable without trusted HTTPS. The canonical origin, no HSTS, keys on the appliance, unchanged
  captive probes and the `Secure` Party cookie all stand. Production remains HTTPS-only until a
  verified deployment says otherwise.
- [ADR 0013](0013-party-and-game-browser-origins.md) keeps `https://party.avrana.net` as the
  trusted Party origin but moves game pages to a separate origin. "One origin for everything" is
  no longer the target.
- D5's closing remark about recovery routes now reads with ADR 0012: the recovery route is
  Limited Mode, not the LAN Games hub.

## Where it stands today

- <span class="avr-badge deployed">Deployed</span> The Full Mode shell under `/party/`, including
  its service worker and browser-side capability evaluation, served by nginx on the HTTPS server
  (shell first installed 2026-09-27; verified at the 2026-09-29 deployment), and the arcade's
  provider-based server. The ADR's own header, "nothing in this ADR is deployed", was true when
  written and predates those deployments.
- <span class="avr-badge source">In source</span> Game contracts for the current games, the
  appliance grant file, both capability evaluators with their shared vectors, and the three
  provider interfaces. The presentation provider's attach, set-view and detach operations are
  documented, not built.
- The CI lane runs Tier 1 and the simulated Tier 2. Tier 3 remains manual.
- The arcade source now exits on a fatal error so systemd restarts it, one of the follow-ups
  listed above.

For the network and origin picture today, see
[The appliance and its network](../architecture/appliance-and-network.md). Game contracts and
grants are covered in [Contracts, catalog and grants](../games/contracts-and-catalog.md), and
personal viewports in
[Execution models](../games/execution-models.md#playstation-profiles-and-personal-viewports).
Testing practice is in [Testing](../developers/testing.md).

## Related decisions

- [ADR 0001](0001-load-soak-fault-harness.md): the arcade load and soak harness (Tier 3 testing).
- [ADR 0005](0005-lan-games-provider-launch.md): the LAN Games fork as a provider, built on this ADR.
- [ADR 0009](0009-arcade-party-provider.md): the arcade as a Party-launched provider.
- [ADR 0012](0012-limited-mode-party-survives-https-loss.md): Limited Mode.
- [ADR 0013](0013-party-and-game-browser-origins.md): separate browser origins.
