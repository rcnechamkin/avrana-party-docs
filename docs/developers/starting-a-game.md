---
title: Starting a game
description: What you can realistically do today if you want to develop or port a game for Avrana Party, and what to wait for.
sources:
  - avrana-party:docs/runbooks/add-a-game.md
  - avrana-party:docs/adr/0014-native-games-isolated-lan-games-retired.md
  - avrana-party:docs/design/NATIVE-GAMES.md
  - avrana-party:avrana/games/standin
  - avrana-party:contracts/games/standin.json
  - avrana-party:docs/runbooks/provision-game.md
  - avrana-party-games:ADDING_A_GAME.md
  - avrana-party-games:games/bluff/game.py
verified: 2026-10-09
---

# Starting a game

The honest answer first: **there is not yet a supported path for an outside developer to build
and install a new Avrana game.** No SDK exists, and no package format, installer or developer
guide for native games either. These are deliberately waiting until Checkers and Spades have
proven the native-game boundary
([ADR 0014](../decisions/0014-native-games-isolated-lan-games-retired.md)).
The Party repository's own add-a-game runbook says the same: for a new native game there is "no
procedure to follow here". This page is the plain-language edition of that runbook.

This site will not invent a tutorial for a path that does not exist. What follows is what you
*can* usefully do now, ordered by how close it is to the project's direction.

## 1. Design against the platform principles

The design guidance is stable even though the tooling is not. Before writing code:

- work through the [designer checklist](../games/designing-for-phones.md#the-designer-checklist),
  especially private information, idle phones, server deadlines and the "no TV" test;
- read [How games integrate](../games/index.md) for what the platform owns. Do not build
  login, profiles, chat, reconnect, teams or spectating yourself;
- read the [shared game UX contract](../design/game-ux-contract.md)
  and the [accessibility expectations](../design/accessibility.md).

A game designed this way will port to the eventual SDK with the least friction, whatever that
SDK turns out to be.

## 2. Study the reference implementations

Two existing implementations show the shapes involved.
[The reference games, explained](reference-games.md) walks through both:

- **BLUFF**, in the Games repository at `games/bluff/`, is the reference for a
  hidden-information game. It has server-side masking per viewer, a separate spectator view,
  step-numbered prompts, bots and autopilot, Party ticket admission and result reporting. It runs
  inside the retiring LAN Games framework, so read it for its *patterns*, not its plumbing.
- **The stand-in game**, in the Party repository at `avrana/games/standin/`, is a minimal Python
  process. It implements the native-game side of the session protocol end to end. It is
  test-only and is never installed on a product appliance, but it is the clearest small example
  of what a native game process must do. Its game contract, `contracts/games/standin.json`, is the
  smallest complete example of the format.

The session protocol and the result envelope each have a single reference implementation in
the Party repository (`avrana/party/protocol.py` and `avrana/party/result.py`), with shared test
vectors. A game in Python vendors those files unchanged, as the Games repository does. A game
in another language would need to reproduce them against the vectors. The vectors make that
possible, but nobody has done it yet.

## 3. Experiment locally

You can run a Party with Party Core on your own machine
(`python3 -m avrana.web.devserver --party`, see [Local development](local-development.md)). You
can also run the native-game unit tests and the stand-in end to end. The full native path,
with systemd units, dynamic users and socket activation, needs Linux with systemd and root. The
project runs it only on disposable CI machines, **never on the appliance**.

## 4. Porting an existing game

The routes depend on what you are porting:

- **A browser party game with an authoritative server** is the natural fit. It would become a
  native game process once that path is open. Until then, the useful work is separating its
  rules from its networking and identity code, and making private state server-filtered.
- **An emulated game** goes through the arcade's emulation path. The PlayStation title profiles
  show the experimental direction. Game files are never committed to any repository, and
  running emulators on the appliance is supervised and needs the owner's approval.
- **A LAN Games title** already lives in the Games repository. The project intends to adapt
  selected titles onto the native boundary one at a time, as "Classics", and never in bulk.

!!! warning "Do not start a new LAN Games module"

    The Games repository's `ADDING_A_GAME.md` still describes how to add a module to the
    standalone LAN Games hub. That route is legacy. The project's rule is not to start a new
    native game as a LAN Games module unless a Linear issue says so explicitly. In current
    source, nginx routes no new LAN titles anyway.

## 5. Talk to the project

Because the native path is being designed right now through Checkers and Spades, the most
valuable contribution from a prospective game developer may be **evidence and feedback**: what
your game needs from the platform that the current contracts do not offer. Raise it as an issue
on the [Party repository](https://github.com/rcnechamkin/avrana-party), so it can inform the SDK
before it is frozen. [How to get involved](contributing.md#how-to-get-involved) covers the
current, limited contributor guidance.
