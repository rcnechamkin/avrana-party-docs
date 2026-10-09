---
title: Decision records
description: Every Architecture Decision Record in plain language, with its real implementation status and how they amend each other.
sources:
  - avrana-party:docs/adr/0001-load-soak-fault-harness.md
  - avrana-party:docs/adr/0002-party-platform.md
  - avrana-party:docs/adr/0003-ids-and-keys.md
  - avrana-party:docs/adr/0004-full-mode-contracts-and-providers.md
  - avrana-party:docs/adr/0005-lan-games-provider-launch.md
  - avrana-party:docs/adr/0006-party-session-protocol.md
  - avrana-party:docs/adr/0007-host-authoritative-launch.md
  - avrana-party:docs/adr/0008-party-navigation.md
  - avrana-party:docs/adr/0009-arcade-party-provider.md
  - avrana-party:docs/adr/0010-party-pregame.md
  - avrana-party:docs/adr/0011-party-console-model.md
  - avrana-party:docs/adr/0012-limited-mode-party-survives-https-loss.md
  - avrana-party:docs/adr/0013-party-and-game-browser-origins.md
  - avrana-party:docs/adr/0014-native-games-isolated-lan-games-retired.md
  - avrana-party:docs/adr/0015-game-result-envelope.md
  - avrana-party:docs/adr/0016-service-identities-and-local-trust-boundary.md
verified: 2026-10-09
---

# Decision records

The project records significant architectural decisions as **Architecture Decision Records**
(ADRs) in `docs/adr/` of the Party repository. Those originals are authoritative and are written
for coding agents. This section has a plain-language edition of each one, linked from the table
below. Each edition ends with a link to its original.

## How to read the ADRs

Three conventions in the project's ADRs differ from what readers may expect:

- **Status is mixed and specific.** Many ADRs give a separate status for their direction and for
  their mechanisms, for example "accepted (direction) · proposed (mechanisms) · not
  implemented". A status of *accepted* does not mean *built*.
- **Old text is not rewritten.** When a later decision changes an earlier one, the earlier ADR
  keeps its text and gains a dated **amendment** section or a "superseded in part" banner. To
  understand a topic, read the newest ADR that touches it and follow its links back.
- **History stays useful.** A partly superseded ADR still describes the deployed system
  accurately where the replacement has not been deployed and verified yet.

## The records

The **Built today** column summarizes implementation as of this site's
[verified revision](../about/this-documentation.md#source-revisions). When an ADR's own status
line is older than the code, the column says so.

| ADR | Decision in one sentence | Built today |
|---|---|---|
| [0001](0001-load-soak-fault-harness.md) | Build a repeatable load, soak, fault and regression harness for the arcade stream. It runs from a machine on the Party Wi-Fi against the live appliance. | <span class="avr-badge source">In source</span> |
| [0002](0002-party-platform.md) | Avrana Party is a **party platform**: one persistent Party that games consume, with layered identity, the host separate from the admin, and a small, optional integration contract. | Partly realized: Party Core, host and navigation <span class="avr-badge deployed">Deployed</span> (ADRs 0006–0010), the console model <span class="avr-badge reported">Owner-reported</span>; profiles, admin and durable history <span class="avr-badge planned">Planned</span> |
| [0003](0003-ids-and-keys.md) | Identifiers, credentials and display values are never mixed: ids grant nothing, secrets never leave their lane, and games get a session key and a name, never a device identity. | Invariants <span class="avr-badge deployed">Deployed</span> on the server side; game pages can still act as the player in the browser, the gap ADR 0013 addresses; profiles and PINs <span class="avr-badge planned">Planned</span> |
| [0004](0004-full-mode-contracts-and-providers.md) | `https://party.avrana.net` is the canonical origin with no HSTS; per-seat capability evaluation; Game Contract v0; three provider interfaces; three evidence tiers. | <span class="avr-badge deployed">Deployed</span>; the HTTPS-only consequence was later superseded by ADR 0012 |
| [0005](0005-lan-games-provider-launch.md) | The LAN Games fork becomes a **provider** behind the Party's catalog, with Party-initiated launches. | <span class="avr-badge deployed">Deployed</span>; long-term role superseded by ADR 0014 |
| [0006](0006-party-session-protocol.md) | Party Core v0 and the signed **session protocol**: launch, tickets, end and ended. | <span class="avr-badge deployed">Deployed</span>; single-use tickets <span class="avr-badge source">In source</span> |
| [0007](0007-host-authoritative-launch.md) | Only the host launches games; Party Home follows Party Core. | <span class="avr-badge deployed">Deployed</span>; reconnect rule superseded by ADR 0011 |
| [0008](0008-party-navigation.md) | One activity at a time; the host switches games; pages inside games follow the Party. | <span class="avr-badge deployed">Deployed</span>; partly superseded by ADR 0011 |
| [0009](0009-arcade-party-provider.md) | The arcade is a **Party-launched provider**: the emulator runs only for a Party session. | <span class="avr-badge deployed">Deployed</span> (server-side verified) |
| [0010](0010-party-pregame.md) | The pregame belongs to the Party: each person chooses **Play or Watch**, and only the host starts. | <span class="avr-badge deployed">Deployed</span>; setup moved to Party Home by ADR 0011 |
| [0011](0011-party-console-model.md) | The **console model**: automatic presence, one authoritative location that only the host moves, the setup as the Party's own scene, held results. | <span class="avr-badge reported">Owner-reported</span>; real-phone check open |
| [0012](0012-limited-mode-party-survives-https-loss.md) | Losing trusted HTTPS must not disable the Party: **Full Mode and Limited Mode**. | <span class="avr-badge accepted">Accepted direction</span>; first steps <span class="avr-badge source">In source</span> |
| [0013](0013-party-and-game-browser-origins.md) | The Party shell and game pages get **separate browser origins**; the browser origin is part of the trust boundary. | <span class="avr-badge accepted">Accepted direction</span>; mechanisms <span class="avr-badge source">In source</span>, not configured |
| [0014](0014-native-games-isolated-lan-games-retired.md) | Native games are **isolated platform consumers**; LAN Games is retired as a runtime; the SDK and `.avrgame` stay unfrozen until Checkers and Spades. | <span class="avr-badge accepted">Accepted direction</span>; machinery <span class="avr-badge source">In source</span>, which is newer than the ADR's "not implemented" status line |
| [0015](0015-game-result-envelope.md) | Games report results in a small, separately versioned **result envelope** carried inside `ended`. | <span class="avr-badge source">In source</span>; history and stats not decided |
| [0016](0016-service-identities-and-local-trust-boundary.md) | **Separate service identities**, per-game secrets and Unix-socket IPC, with an explicit list of what is not protected. | <span class="avr-badge accepted">Accepted direction</span>; phase-one pieces <span class="avr-badge source">In source</span>, which is newer than the ADR's status line; migration not recorded |

## The decisions that matter most to a newcomer

If you read only four ADRs, read these:

1. **[0002, the party platform](0002-party-platform.md).**
   It explains why the Party exists separately from any game. Its "alternatives considered"
   section explains why the project rejected an iframe shell, a single-page app that absorbs
   every game, and cloud accounts.
2. **[0003, identifiers and keys](0003-ids-and-keys.md).**
   Its tables of which value authorizes what are the clearest statement of the identity model.
3. **[0011, the console model](0011-party-console-model.md).**
   It explains, from a real-device test, why "one location that the host moves" replaced softer
   designs.
4. **[0014, isolated native games](0014-native-games-isolated-lan-games-retired.md).**
   It sets the direction the platform is moving in now, and the order in which it will be
   proven.

## How decisions are made

Decisions start as product discussions with the project owner. They become a Linear issue and,
for architecture, an ADR. The owner accepts them, sometimes with recorded decisions labelled D1,
D2 and so on inside the ADR. Agents implement accepted decisions. They do not make new product
decisions, and when an issue contains an unresolved product question they are expected to stop
and ask. See [Contributing](../developers/contributing.md) for the full loop.
