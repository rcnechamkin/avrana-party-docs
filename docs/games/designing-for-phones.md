---
title: Designing for phones
description: "What makes a good Avrana-native game: private player surfaces, the designer checklist, where shared code belongs, and BLUFF as a worked example."
sources:
  - avrana-party:docs/design/NATIVE-GAMES.md
  - avrana-party:docs/design/GAME-UX-CONTRACT.md
  - avrana-party:docs/design/ACCESSIBILITY.md
  - avrana-party:docs/ROADMAP.md
  - avrana-party-games:games/bluff/game.py
verified: 2026-10-09
---

# Designing for phones

This page is for people thinking about *what* to build. It is the plain-language edition of the
project's native-games design document. Its guidance is principles and recommendations, not a
built framework.

## The phone is a private, dynamic surface

The smartphone in each player's hand can be a controller. It can also be a private screen, a
secret hand of cards, a hidden role, a personal objective, an inventory, a drawing canvas, a
buzzer, a ballot, an auction paddle or a team back-channel. It can also be adjusted for one
person's accessibility needs without affecting anyone else. A game that only puts a D-pad on
the phone uses the least interesting part of the platform.

Because the TV is optional, a native game must be **fully playable on phones alone**. If a TV is
present, it is just one more public viewer.

## The designer checklist

The design document asks every native game to answer these questions before it is built. They
are worth reproducing almost verbatim, because together they describe what the platform
values:

1. What does each player know that the others don't? If nothing, why phones?
2. What does my phone show when it is **not** my turn? Idle phones sleep, and people drift.
3. Does every public moment work on phones alone, tested with **no TV connected**?
4. Which inputs need a private touchscreen: text, drawing, a secret choice, a wager?
5. Is every private field filtered per viewer **on the server**, and covered by a leak test?
6. Is every timed moment set by a server deadline, and safe after a phone sleeps and wakes?
7. Is speed scored? If so, is Wi-Fi lag compensated, or should speed not count?
8. Does every control have an accessible alternative that sends **the same value**?
9. What is anonymous, and to whom: other players, the host, the logs?
10. What official results and statistics does the game report, and with what provenance?

## BLUFF as a worked example

<span class="avr-badge deployed">Deployed</span>

BLUFF is a hidden-role bluffing card game for two to six players, inspired by *Coup* but with
original working names and assets. It is the first Avrana-native game and the platform's main
testbed. The game itself is deployed; two of the points below are newer. It shows how the
checklist turns into code:

- **Hidden information stays on the server.** The game state is filtered separately for each
  viewer. Your phone receives your two cards and nobody else's. The deck is never sent to any
  phone. Spectators get their own separate view.
- **The server is authoritative.** Phones send intentions such as claim, challenge or block,
  and the server decides what happens. Every prompt carries a step number, so a late answer to
  an earlier question is rejected instead of being applied to the current one.
- **Phones sleep, so the game keeps going.** Timers run on the server. Bots can fill seats, and
  an autopilot can act for a player who has dropped out. A reconnecting phone receives the full
  current state.
- <span class="avr-badge source">In source</span> **It reports a result.** When a round
  completes, BLUFF reports each participant's standing through the result envelope.
- <span class="avr-badge reported">Owner-reported</span> **The Party owns the setup.** The game
  ships its premise and rules as data. The Party's full-screen briefing presents them, and the
  Party handles Play, Watch and Start. In the last verified deployment, Play, Watch and the
  host-only Start already belonged to the Party, but the setup panel sat above the game's own
  page.

The roadmap is clear about what BLUFF has not yet proven. A real group playing on real phones
should shape its mechanics, theme, prompts, event history and balance across player counts.
Testing that hidden state can never reach the wrong browser "remains essential".

## Where shared code belongs

The design document names **four homes** for code, and it is strict about not promoting
anything to shared code too early:

| Home | Holds | Status |
|---|---|---|
| **Party service** | Identity, presence, seats, host, navigation, chat, statistics and events, accessibility preferences | Exists (Party Core), partly |
| **Game SDK** | Shared server code running inside each game's own process | **Does not exist** |
| **Client UI kit** | Optional phone widgets a game may use | Does not exist |
| **Game logic** | Rules, scoring, turn order, real-time loops | Each game |

Its advice is to *standardize the frame around a player moment, and leave the moment itself to
the game*. The frame covers who may act, until when, who sees what, how it is revealed and
what is recorded. The document lists candidate primitives in the order it thinks they are worth
standardizing: presence and eligibility, a response window for collecting answers, an
authoritative clock, private per-viewer views with an automatic leak test, and others. A
primitive becomes shared code only when a **second independent game** needs it.

The LAN Games fork is mined for patterns, not imported wholesale. The design document
classifies each part of the fork as an extraction candidate, a pattern donor or legacy code to
leave behind. Code that handles identity, admission, lobbies, navigation or chat is always
legacy, because the Party now owns that authority.

## Platform UX that every game shares

A separate contract, the [shared game UX contract](../design/game-ux-contract.md), defines where the line runs on a player's phone between Avrana and the game. It covers the
briefing, Ready, Watch and Start, access to the rules during play, how an unavailable action is
explained, minimum touch-target and interaction standards, system cues such as sound, and art
slots. Every rule in it is labelled as implemented, accepted or proposed. None has been
validated on phones yet. A game designer should read it before designing screens, together
with the project's
[accessibility expectations](../design/accessibility.md).
