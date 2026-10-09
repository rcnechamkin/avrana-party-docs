---
title: "ADR 0008: Party navigation"
description: How Party Core became the one place that says where the Party is, how the host switches games safely, and how pages inside games follow.
sources:
  - avrana-party:docs/adr/0008-party-navigation.md
  - avrana-party:docs/adr/0011-party-console-model.md
  - avrana-party:docs/design/PARTY-LIFECYCLE.md
  - avrana-party:avrana/party/core.py
  - avrana-party:avrana/party/service.py
  - avrana-party:web/party/lib/party-follow.js
  - avrana-party:web/party/lib/party-mode.js
verified: 2026-10-09
---

# ADR 0008: One activity, a host switch, and game pages that follow

!!! abstract "At a glance"
    **Decided:** 2026-09-29 · **Status:** <span class="avr-badge deployed">Deployed</span>; its "follow only what you watched" rule and in-game Party line are replaced in source by [ADR 0011](0011-party-console-model.md)
    The Party runs one game at a time. The host can move everyone to another game in one step,
    and pages already inside a game follow the host's moves.

## The problem

[ADR 0007](0007-host-authoritative-launch.md) made the host's start authoritative, but only Party
Home listened. A phone already inside a game never heard about the host's next move. So the host
could not switch games without ending and restarting; players left in a finished game had to
find their own way back; and "one game at a time" was enforced only by refusing a second launch,
so nothing stopped the next game starting while the old one was still shutting down. Real-phone
testing on 2026-09-29 confirmed the gap. The rules to fix it were already written in the Party
lifecycle design.

## What was decided

**Party Core says where the Party is.** Every state it sends carries a small navigation record:
"go to this game" or "go home", with a counter that rises on each move. It rises only on
**committed** changes: a session that actually became active, the host's End, or a failed start
that replaced a running game. Intentions (a launch in progress, a switch still waiting) never
move it.

**One Party activity, enforced by the server.** At most one session is live at a time. Only the
current host may start, switch or end, and only against the current state version. A game page
asking for a ticket while the Party plays a different game is refused, so a stale or hand-typed
address can neither join nor start a party game.

**A switch is "end, then launch".**

```mermaid
sequenceDiagram
  participant H as Host's phone
  participant C as Party Core
  participant A as Old game server
  participant B as Next game server
  H->>C: switch to the next game
  C->>C: old session "ending"; its tickets stop working
  C->>A: end
  A-->>C: confirmed (or timeout)
  C->>C: one locked step: close old, open next
  C->>B: launch
```

If the old game does not confirm that it stopped, the switch stops there, everyone goes home and
the Party shows why. Nothing is started on top of a game that may still be running.

**Pages inside games follow Party Core.** A small follower script, loaded by integrated game
pages and the arcade page, keeps the same long poll as Party Home. On a start it goes to that
game; on an End it goes home if it was that game. The arcade and standalone titles follow a
start but never an end, so End did not send an arcade page home. In this first version a page moved only on
moves it had watched; a reloaded page showed "Your party is playing X · Join them" instead.

**The host's controls are where the host is.** Party Home offered "Switch everyone to this". A
game page offered "End for everyone", needing two taps so a stray tap never moves the Party. Back
to Party stayed a personal link.

## Why this way

Moving only on committed changes means no phone chases a start that then fails. A strictly
sequential switch means two heavy runtimes never compete, and a game that did not stop cleanly is
never covered up by a new one. Requiring the current version for every host action means two host
tabs, or a stale one, cannot both act.

## What it means in practice

The host can say "let's play something else" and everyone moves together, and the host's End
brings stragglers home. Either side could be deployed first: without the follower or without
navigation, pages behaved as before.

The arcade was the exception. Its emulator ran all the time as its own service, so Gauntlet II
could keep running beside BLUFF. Letting Party Core start and stop it was left to a separate,
owner-approved decision: [ADR 0009](0009-arcade-party-provider.md).

## Later changes

- **[ADR 0009](0009-arcade-party-provider.md)** made the arcade a Party-launched game.
- **[ADR 0011](0011-party-console-model.md), the console model**, replaced two parts. Pages no
  longer follow only moves they watched: every member page goes wherever the Party is, on load
  and on every change. The in-game Party status line is gone, and host controls live in the
  game's own interface.
- **2026-10-02, an amendment to ADR 0011.** An abandoned round now sends the Party home at once
  (this ADR had left navigation alone when a game ended by its own rules), and a switch moves
  everyone to the next game's setup as soon as the new session exists.

**Still in force from this ADR:** the navigation record and when it moves; one live session at a
time; host-only start, switch and end against the current version; tickets refused for a game
the Party is not playing; and the "end, then launch" switch that stops if the old game does not
confirm.

## Where it stands today

<span class="avr-badge deployed">Deployed</span> on 2026-09-29, verified on the server side. The
navigation record, the switch and the follower script are in current source, now driven by the
console model's location rule, which is <span class="avr-badge source">In source</span> and
<span class="avr-badge reported">Owner-reported</span> as deployed.

Not yet checked on real phones: the in-game follow on iPhone Safari and Android Chrome, sleeping
phones, and the host's End from inside a game.

## Related decisions

- [ADR 0007: the host starts the game](0007-host-authoritative-launch.md), which this extends.
- [ADR 0009: the arcade as a Party game](0009-arcade-party-provider.md).
- [ADR 0010: the Party's pregame](0010-party-pregame.md).
- [ADR 0011: the console model](0011-party-console-model.md), which replaces part of this.
- [The Party](../architecture/party.md) and [game sessions](../architecture/game-sessions.md).
