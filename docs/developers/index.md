---
title: Developers
description: Where to begin if you want to work on Avrana Party.
sources:
  - avrana-party:CONTRIBUTING.md
  - avrana-party:AGENTS.md
  - avrana-party:docs/WORKFLOW.md
verified: 2026-10-09
---

# Developers

Avrana Party can be developed without a Raspberry Pi. The Party interface, Party Core, the
contracts and most of the operations tooling run and are tested on an ordinary laptop or in
CI. The test suites can simulate the appliance on `localhost`, with real nginx and real
browsers acting as phones. Only questions about real hardware need the appliance itself:
phones, Wi-Fi, the video encoder and power.

This section is in reading order:

1. **[Repository ecosystem](ecosystem.md)**: which repository holds what, and how they relate.
2. **[Local development](local-development.md)**: running the Party UI and the test suites
   on your machine.
3. **[Testing](testing.md)**: the test tiers, what each proves, and how evidence is graded.
4. **[Contributing](contributing.md)**: how work is chosen, branched, reviewed, merged and
   deployed, and where humans and coding agents fit in.

Building a game? The [Games](../games/index.md) section covers the integration model, and
[Building or porting a game today](starting-a-game.md) says what is realistic before an SDK
exists. To find your way around the engineering repositories' own documents, see
[Navigating the engineering docs](reading-the-specs.md).

!!! warning "The project is moving quickly"

    The engineering repositories change daily, and much of their documentation is written to
    direct coding agents. This site is a stable explanation, but for anything you are about to
    change, read the current canonical documents and code. The
    [About this documentation](../about/this-documentation.md) page says which revisions this
    site was checked against.
