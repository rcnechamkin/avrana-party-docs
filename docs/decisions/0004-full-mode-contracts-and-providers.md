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
  - avrana-party:.github/workflows/offline-checks.yml
  - avrana-party:docs/SYSTEM.md
verified: 2026-10-09
---

# ADR 0004: The Full Mode origin, platform contracts and provider boundaries

!!! abstract "At a glance"
    **Decided:** 2026-09-26 · **Status:** D1 accepted; D2–D6 proposed, then merged · Full Mode shell <span class="avr-badge deployed">Deployed</span> · HTTPS-only recovery stance superseded by ADR 0012
    The Party lives at `https://party.avrana.net/party/`, with no HSTS so an expired certificate
    stays escapable. The ADR also sets how phone capabilities are judged, what a game contract
    says, the three kinds of provider behind a game, what the offline copy may do, and three tiers
    of test evidence.

## The problem

Trusted HTTPS at `party.avrana.net` went live on 2026-09-25. That raised several questions at
once: where the Party's pages live, how to judge what each phone can do, what a game declares
versus what the appliance grants, how the arcade's parts are separated, and what counts as
evidence. The ADR answers them as decisions D1 to D6.

## What was decided

**D1. The canonical origin is `https://party.avrana.net`.** (An *origin* is the scheme, host and
port a browser uses to separate cookies and storage.) Avrana's pages live under `/party/` on the
HTTPS server only. The plain-HTTP server is unchanged: captive-portal probes get their expected
answer and there is no global redirect. There is **never HSTS**, which would make browsers refuse
anything but valid HTTPS and trap phones if the certificate expired. The TLS key never leaves the
appliance, and no private certificate authority goes on phones. Because HTTP and HTTPS are
different origins, Party identity is scoped to HTTPS and its cookie is `Secure`.

**D2. Capabilities are judged per seat, by observation.** The engine keeps apart what the device
can do (observed in the browser), the seat's role, what the appliance's runtime offers and what
the game requires, and produces a presentation strategy per seat. Each capability is `yes`, `no`,
`partial` or `unknown`, and **unknown is never treated as no**. Probes never trigger permission
prompts and never use the user-agent string. A weak phone changes only its own seat, getting a
fallback or a plain explanation; the party never drops to the weakest phone. The report is
advice for the interface, never an input to authorization. The logic exists in Python and in
browser JavaScript, kept in agreement by shared test vectors.

**D3. Game Contract v0.** Each game is described by a JSON contract that lists its possible
**presentations** in order of preference (a native browser game, a shared stream, a personal
viewport, controller-only or a native app), each with the capabilities and roles it needs, plus a
per-seat fallback and the permissions and resources it requests. The guiding rule is **the
package describes and requests; the appliance decides.** A separate appliance file holds the
grants (entry path, trust tier, granted permissions); the validator rejects grant-side keys in a
contract, and a grant cannot give a permission the contract did not request.

**D4. Three provider boundaries, with policy kept in Avrana.** A *provider* is the code that runs
a game's program, handles its input or delivers its picture. The ADR defines three small
interfaces, with the arcade as the first implementation of each:

| Boundary | Role | Arcade implementation |
|---|---|---|
| Runtime | start, check and stop the program running the game | RetroArch, with its network command port kept off |
| Input and virtual controller | apply full input snapshots to a controller | a Linux virtual gamepad |
| Presentation | deliver the picture | the arcade's single shared video encode |

Policy stays with Avrana whatever the provider: seat-to-slot mapping, tickets, stale-input
release, rate limits, the encoder budget, and never exposing an emulator's control port.

**D5. The offline copy is a convenience, not a recovery mechanism.** A service worker (a script
the browser keeps to serve pages offline) is scoped to `/party/` and is network-first, so phones
on the Party Wi-Fi always run the current build. Its cache answers only when the appliance is
unreachable, and the page says so. It never caches the hub, the arcade, the Party API, party state
or identity. Three kill switches exist, from a flag in the version file to a self-destructing
worker build and a manual removal button on the diagnostics page.

**D6. Three test tiers.** Tier 1 is pure tests; Tier 2 is a simulated Party on one machine with
real nginx and a real browser; Tier 3 is the real appliance, phones, Wi-Fi and encoder. CI runs
Tiers 1 and 2. Tier 3 stays manual, and a lower tier's results are never reported as hardware
validation.

## Why this way

The common thread is keeping the appliance escapable and its claims honest: an expired
certificate must not trap a phone, one weak phone must not degrade everyone's game, a game must
not award itself permissions, and a simulated pass must not be taken for proof on hardware. The
ADR is also frank about the offline copy's limits: with an expired certificate it may show a
cached page while every live call fails, and Safari evicts its storage after about a week.

## What it means in practice

Deploying the shell needed a one-time, owner-approved nginx change plus an install script with
rollback and kill-switch options. Follow-ups named at the time included Party Home adopting the
shell's libraries, a ticket version bound to the seat, and making the arcade exit on a fatal error
so systemd restarts it.

## Later changes

**2026-10-02.** The text is unchanged; two later decisions change parts of D1:

- [ADR 0012](0012-limited-mode-party-survives-https-loss.md) supersedes "HTTP is not a recovery
  path for the Party page". At the time, the shell sent guests to the plain-HTTP LAN Games hub if
  HTTPS failed. The target is now **Limited Mode**, in which the Party itself stays usable without
  trusted HTTPS. The origin, no HSTS, keys on the appliance and the `Secure` cookie all stand, and
  production stays HTTPS-only until a verified deployment says otherwise.
- [ADR 0013](0013-party-and-game-browser-origins.md) keeps the Party origin but moves game pages
  to a separate one; "one origin for everything" is no longer the target.

## Where it stands today

- <span class="avr-badge deployed">Deployed</span> The Full Mode shell under `/party/`, with its
  service worker and browser-side capability evaluation (first installed 2026-09-27, verified at
  the 2026-09-29 deployment), and the arcade's provider-based server. The ADR's header, "nothing in
  this ADR is deployed", was true when written.
- <span class="avr-badge source">In source</span> Game contracts for the current games, the
  appliance grant file, both evaluators and the provider interfaces. The presentation provider's
  attach and detach operations are documented, not built.
- The offline CI lane runs Tiers 1 and 2; Tier 3 remains manual. The arcade source now exits on
  a fatal error so systemd restarts it.

See [The appliance and its network](../architecture/appliance-and-network.md),
[Contracts, catalog and grants](../games/contracts-and-catalog.md),
[Execution models](../games/execution-models.md#playstation-profiles-and-personal-viewports) for
personal viewports, and [Testing](../developers/testing.md).

## Related decisions

- [ADR 0001](0001-load-soak-fault-harness.md): the arcade soak harness (Tier 3 testing).
- [ADR 0005](0005-lan-games-provider-launch.md): the LAN Games fork as a provider.
- [ADR 0009](0009-arcade-party-provider.md): the arcade as a Party-launched provider.
- [ADR 0012](0012-limited-mode-party-survives-https-loss.md): Limited Mode.
- [ADR 0013](0013-party-and-game-browser-origins.md): separate browser origins.
