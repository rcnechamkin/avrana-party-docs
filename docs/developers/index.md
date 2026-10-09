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
3. **[Contributing](contributing.md)**: how work is chosen, branched, reviewed, merged and
   deployed, and where humans and coding agents fit in.
4. **[Reading the specifications](reading-the-specs.md)**: how the engineering documentation
   is organized, which document answers which question, and how to read evidence.
5. **[Starting a game](starting-a-game.md)**: what you can realistically do today if you want
   to build or port a game.

!!! warning "The project is moving quickly"

    The engineering repositories change daily, and much of their documentation is written to
    direct coding agents. This site is a stable explanation, but for anything you are about to
    change, read the current canonical documents and code. The
    [About this documentation](../about/this-documentation.md) page says which revisions this
    site was checked against.
