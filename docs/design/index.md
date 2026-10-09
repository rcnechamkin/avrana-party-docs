---
title: Design documents
description: The detailed designs behind the Architecture pages, and which one to open for which question.
sources:
  - avrana-party:docs/design/README.md
  - avrana-party:docs/design/PARTY-PLATFORM.md
  - avrana-party:docs/design/PARTY-LIFECYCLE.md
  - avrana-party:docs/design/LIMITED-MODE.md
  - avrana-party:docs/design/BROWSER-ORIGINS.md
  - avrana-party:docs/design/GAME-UX-CONTRACT.md
  - avrana-party:docs/design/ACCESSIBILITY.md
verified: 2026-10-09
---

# Design documents

The [Architecture](../architecture/index.md) and [Games](../games/index.md) sections give the
short version. The pages here are the long version: plain-language editions of the design
documents in the engineering repository, with the rules, the edge cases and the open questions.
Read them when the short version leaves you asking "but what exactly happens when…".

Each design mixes what is built with what is only proposed, so every page opens with a summary
of which parts are real, marked with the [maturity labels](../about/this-documentation.md#maturity-labels).

| If you have read… | …and want the detail, open | It covers |
|---|---|---|
| [The Party](../architecture/party.md) | [Party lifecycle](party-lifecycle.md) | Presence, the host role, succession, seats, and the timers Party Core uses |
| [What Avrana Party is](../introduction/index.md) and [The Party](../architecture/party.md) | [Party platform design](party-platform.md) | The platform's principles, identity layers, admin versus host, and the proposed social and progression features |
| [Full Mode and Limited Mode](../architecture/appliance-and-network.md#full-mode-and-limited-mode) | [Limited Mode](limited-mode.md) | How the Party keeps working when trusted HTTPS fails |
| [Trust boundaries](../architecture/trust-boundaries.md#2-the-party-versus-game-code-in-the-browser), boundary 2 | [Browser origins](browser-origins.md) | Moving game pages to their own origin, the bridge frame and the rollout steps |
| [Designing for phones](../games/designing-for-phones.md) | [Shared game UX contract](game-ux-contract.md) | Where the Party ends and a game begins on a player's screen |
| [Designing for phones](../games/designing-for-phones.md) | [Accessibility](accessibility.md) | The rules every player-facing page must meet, and how they are tested |

The reasoning for *why* each design exists usually lives in a
[decision record](../decisions/index.md); the design pages link to the relevant one.
