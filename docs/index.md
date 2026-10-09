---
title: Avrana Party
description: A portable, local-first multiplayer appliance. Phones are the screens and the controllers; the Pi is the console.
hide:
  - navigation
sources:
  - avrana-party:README.md
  - avrana-party:docs/ROADMAP.md
  - avrana-party:docs/SYSTEM.md
verified: 2026-10-09
---

# Avrana Party

<p class="avr-hero">
Avrana Party turns a Raspberry Pi into a self-contained multiplayer game system. Players join
its Wi-Fi, open a browser on their phones and play together. Nobody installs an app, signs up
for an account or needs a television. The appliance does not need the internet.
</p>

The project's motto is **"The game may change; the party does not."** One Party (the people in
the room, who is hosting, and where everyone should be) lasts across many games. Games come and
go inside it. Most of the architecture follows from taking that sentence seriously.

This site explains the project to engineers who have never seen it. It covers what Avrana Party
is, how its parts fit together, how games plug in, how mature each piece really is and how to
start contributing. It is a guided tour, not the specification. Every page links to the
canonical documents and code in the engineering repositories, and those remain the authority.

!!! note "Active development"

    Avrana Party is a working prototype that one person is developing quickly, with help from
    coding agents. Some parts run on the physical appliance today. Some exist only as merged
    source that has not been deployed. Others are accepted designs that are not built yet. This
    documentation marks each claim with a [maturity label](about/this-documentation.md#maturity-labels)
    such as <span class="avr-badge deployed">Deployed</span>, <span class="avr-badge source">In source</span>
    or <span class="avr-badge accepted">Accepted direction</span>, and the
    [project status](status/index.md) page collects them in one place.

## A party night, in seven steps

The product is built around the flow below. Every step is implemented in source and exercised
by automated tests that simulate four phones in a browser. The last *verified* deployment
(29 September 2026) has an older version of steps 4 and 5. A newer deployment is
[owner-reported but not yet recorded](status/index.md#what-is-deployed). The project's next
evidence gate is running the whole loop on four real phones, offline.

1. Someone switches on the appliance.
2. Everyone joins the **Avrana Party** Wi-Fi network.
3. Everyone opens `https://party.avrana.net/party/`. That address only resolves on the Party's
   own network and is not a public website.
4. Each phone picks a display name and an avatar and is in the Party automatically. The first
   person in becomes the **host**.
5. The host picks a game. Every phone moves to the game's setup screen, where each person
   chooses to **play** or **watch**.
6. The round plays out across the phones. Each player sees only what they are allowed to see.
7. When the round ends, the results stay up until the host takes everyone back to Party Home
   or starts another round.

## Where to start

<div class="grid cards" markdown>

-   **New to the project?**

    ---

    Start with [What Avrana Party is](introduction/index.md), then
    [why it is built around phones](introduction/phone-first.md).

-   **Want the system design?**

    ---

    The [architecture overview](architecture/index.md) has the main diagram and links to
    each subsystem.

-   **Why is it built this way?**

    ---

    [Decision records in brief](decisions/index.md) summarizes every architectural
    decision, with its reasoning and real status.

-   **Thinking about games?**

    ---

    [How games integrate](games/index.md) explains the Party ↔ Games boundary and the
    execution models.

-   **Ready to contribute?**

    ---

    Read [Developers](developers/index.md) for the repository map, local setup and the
    contribution workflow.

-   **Need to know what actually works?**

    ---

    [Project status](status/index.md) separates what is demonstrated, in progress and
    planned.

-   **Looking for a term?**

    ---

    The [glossary](about/glossary.md) defines Party, Member, Host, Participant, ticket,
    Full Mode and the rest.

</div>

## What this site is not

This site does not grant permission to deploy, change a contract or act on a roadmap item. It
does not replace the [Architecture Decision Records](decisions/index.md),
the [Party ↔ Games contract](games/contracts-and-catalog.md#the-party-games-contract)
or [Linear](https://linear.app/avranakern), where live work is tracked. When this site and the
engineering repositories disagree, the repositories are right and this site has a bug.
[About this documentation](about/this-documentation.md) explains how the two are kept in step.
