---
title: Avrana Party
description: A portable, local-first multiplayer appliance. Phones are the screens and the controllers; the Pi is the console.
hide:
  - navigation
  - toc
sources:
  - avrana-party:README.md
  - avrana-party:docs/ROADMAP.md
  - avrana-party:docs/SYSTEM.md
  - avrana-party:docs/adr/0011-party-console-model.md
verified: 2026-10-09
---

# Avrana Party

<p class="avr-hero">
Avrana Party turns a Raspberry Pi into a self-contained multiplayer game system. Players join
its Wi-Fi, open a browser on their phones and play together. Nobody installs an app, signs up
for an account or needs a television, and the box does not need the internet.
</p>

<p class="avr-motto">"The game may change; the party does not."</p>

That motto is the design. One **Party** (the people in the room, who is hosting and where
everyone should be) lasts all evening. Games come and go inside it, and every phone follows the
Party from one to the next.

## A party night

```mermaid
flowchart TB
  A["Switch on the box"] --> B["Phones join the<br/>Avrana Party Wi-Fi"]
  B --> C["Open party.avrana.net<br/>in the browser"]
  C --> D["Pick a name and avatar:<br/>you're in the Party"]
  D --> E["The host picks a game"]
  E --> F["Each phone chooses<br/>Play or Watch"]
  F --> G["The round plays out,<br/>each phone showing only<br/>what its player may see"]
  G --> H["Results stay up until<br/>the host moves on"]
  H -- "Play again" --> F
  H -- "Party Home" --> E
```

The first phone in becomes the **host**. If the host's phone goes away, the role passes on
automatically. Every step is implemented in source and tested with four simulated phones. The
deployed build has an older version of joining, setup and results.
[What Avrana Party is](introduction/index.md#a-party-night-step-by-step) walks through each
step.

## What works today

Avrana Party is a working prototype on one appliance, developed quickly by its owner with coding
agents. This site labels every capability by how far it has really got:

- <span class="avr-badge deployed">Deployed</span> The Party itself, BLUFF (a hidden-role card
  game) with Play or Watch, and an arcade game streamed to phones, all on the appliance and
  checked from the server side.
- <span class="avr-badge source">In source</span> A console-style Party model, a redesigned
  interface and the groundwork for isolated native games. These are merged and tested, but not
  verified as deployed.
- <span class="avr-badge accepted">Accepted direction</span> A degraded mode for when trusted
  HTTPS fails, separate browser origins for games, and separate service identities.

The next milestone is evidence rather than features: four people on four real phones finishing
a round offline. [What works today](status/index.md) has the full picture.

## Choose your path

<div class="grid cards" markdown>

-   :material-compass-outline: **New to Avrana Party**

    ---

    What it is, why it insists on phones alone, and what is real today.

    [What Avrana Party is](introduction/index.md) ·
    [Why phones, and only phones](introduction/phone-first.md)

-   :material-sitemap-outline: **Understanding the system**

    ---

    The components, their boundaries and the reasoning behind them.

    [Architecture overview](architecture/index.md) ·
    [The Party](architecture/party.md)

-   :material-gamepad-variant-outline: **Thinking about a game**

    ---

    How games plug in, the working examples, and what having no SDK yet means for you.

    [How games integrate](games/index.md) ·
    [Building or porting a game today](developers/starting-a-game.md)

</div>

Going further: [Developers](developers/index.md) covers setup and contributing,
[Reference](reference/index.md) holds every decision record and design document, and
[Project](project/roadmap.md) has the roadmap and deployment history.

!!! info "This site explains; the engineering repositories decide"

    This is a guided tour, not the specification. Every page ends with links to the canonical
    documents it explains. When this site and the engineering repositories disagree, the
    repositories are right. Nothing here grants permission to deploy or change a contract.
    [About this documentation](about/this-documentation.md) explains how the two stay in step.
