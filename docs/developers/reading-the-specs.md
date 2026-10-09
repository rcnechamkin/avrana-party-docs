---
title: Reading the specifications
description: How the engineering documentation is organized, which source answers which question, how to read document status, and how evidence is graded.
sources:
  - avrana-party:AGENTS.md
  - avrana-party:docs/README.md
  - avrana-party:docs/manifest.json
  - avrana-party:docs/WORKFLOW.md
  - avrana-party:docs/TESTING.md
  - avrana-party:docs/design/README.md
  - avrana-party:docs/GRAPHIFY.md
verified: 2026-10-09
---

# Reading the specifications

The Party repository's `docs/` directory holds a large body of written engineering knowledge:
ADRs, design documents, runbooks, dated findings and several long direction documents. It is written mainly for coding agents and the engineer
directing them. It is precise and dense, and its most important feature is easy to miss on a
first read: **every document has a scoped authority.** This page explains how to navigate it.

## Which source answers which question

The project is explicit that "newest" does not mean "most authoritative". Each question has
its own source:

| Question | Source of truth |
|---|---|
| What does the code do? | The code and tests on `main` of each repository |
| What is the system meant to be? | Canonical documents and accepted ADRs |
| What should change next, and how will we know it is done? | The Linear issue |
| What is running on the appliance? | `/party/api/status` and the deployment manifest; the [system map](../project/system-map.md) summarizes verified state |
| How do the Party and the Games server talk? | The [Party ↔ Games contract](../games/contracts-and-catalog.md#the-party-games-contract) and its JSON declarations |
| What does a test prove? | The testing guide (plain-language edition: [Testing](testing.md)) |
| Where is the project going? | The [roadmap](../project/roadmap.md), which is never a task queue |

Most apparent contradictions turn out to be answers to different questions. The commonest case:
the source on `main` has moved ahead of what is deployed. Both are correct, about different
things.

## Kinds of document

| Kind | Where in the Party repository | How to treat it | Plain-language edition here |
|---|---|---|---|
| **ADRs** | `docs/adr/` | Decisions. Read each one's status line *and* its dated amendments | [Decision records](../decisions/index.md) |
| **Design documents** | `docs/design/` | Contracts and detailed designs. Many mix implemented, accepted and proposed parts, and label each | [Design](../design/party-platform.md) section, plus the [game platform](../games/index.md) pages |
| **Direction documents** | `docs/GAME-PLATFORM-ARCHITECTURE.md`, `docs/OFFLINE-TRUST-AND-RECOVERY.md`, `docs/PERSONAL-VIEWPORT-AND-EMULATION.md`, `docs/AVRANA-EXPERIENCE.md` | Broad product and architecture direction. Mostly conceptual, and they say so | [Today versus the vision](../introduction/today-and-vision.md), [execution models](../games/execution-models.md), [Limited Mode](../design/limited-mode.md) |
| **Runbooks** | `docs/runbooks/` | Procedures. Some are labelled "proposed, never run". **A command in a runbook is not permission to run it** | [Deployment](../project/deployment.md), [starting a game](starting-a-game.md) |
| **Findings** | `docs/findings/YYYY-MM-DD-*.md` | Dated observations and measurements: evidence of what was true on that day, never instructions | [System map](../project/system-map.md#deployment-history) |
| **Research** | `docs/research/` | Candidate technologies and reference implementations. Context only | Not covered |
| **Archive** | `docs/archive/` | Old handoffs and drafts. History | Not covered |

A machine-readable manifest, `docs/manifest.json` in the Party repository, classifies every
Markdown file there by class (`canonical`, `decision`, `design`, `strategy`, `runbook`,
`evidence`, `research`, `historical` or `archived`), status and the domain it is canonical for.
CI fails if a document is missing from it. If you are unsure how much weight an engineering
document carries, look it up there.

## Plain-language editions on this site

Every engineering document this site relies on has a plain-language edition here, either a page
of its own or a section of a broader page. The editions keep the substance and drop the
agent-oriented detail: issue chains, file-by-file change lists and exhaustive tables. Each page
ends with a collapsed **Canonical sources** block that links to the original documents and code,
which remain authoritative. Use the edition to understand a topic. Use the original when you are
about to change something.

## Status labels inside documents

Within design documents, look for these markers:

- **Implemented / in source**: present on `main`, usually with a file cited.
- **Accepted**: decided by the owner, not necessarily built.
- **Proposed**: drafted for review; direction, not contract.
- **Not deployed / not validated on phones**: exactly what it says. The documents use these
  phrases carefully.
- `[E]`, `[I]`, `[R]` tags in some documents: **E**vidence read in source, **I**nference and
  **R**ecommendation.

Statuses are dated. An ADR whose status line says "not implemented" may have been overtaken by
code merged since. The [known discrepancies](../status/discrepancies.md) page lists the cases
this site found.

## Evidence tiers

The project grades evidence in three tiers, and it never lets a lower tier stand in for a
higher one:

- **Tier 1, pure.** Unit and module tests with no appliance, network or real browser.
- **Tier 2, simulated Party.** Real nginx and real Chromium on `localhost`, often with several
  browser contexts acting as phones.
- **Tier 3, hardware.** Real phones on the Party Wi-Fi, with the real access point, encoder and
  power.

**Deployed, server-side** evidence is kept as a separate category. It shows the change is on
the appliance and its services answer correctly. It does not show that the experience works
in someone's hand.

A few phrases from the project's guidance are worth remembering: *a merged PR is not a
deployment; a curl is not a phone test; a simulation is not a measurement; chat history is not
a source.*

## Navigating efficiently

- In the Party repository, start from the documentation map, `docs/README.md`. It is a table of
  every document category with its purpose, its limits and where to look instead.
- For a specific behaviour, read the code and its tests first, then the documents the code
  cites. This is the order the project asks its own agents to follow.
- The repositories include **Graphify**, a generated knowledge graph used by agents for broad
  navigation. It is explicitly derived context, never a source of truth. Verify anything it
  suggests against the code and canonical documents.
