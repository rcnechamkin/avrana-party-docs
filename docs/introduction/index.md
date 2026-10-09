---
title: What Avrana Party is
description: The product, the problem it solves and the main pieces, in plain terms.
sources:
  - avrana-party:README.md
  - avrana-party:docs/ROADMAP.md
  - avrana-party:docs/adr/0002-party-platform.md
  - avrana-party:docs/design/PARTY-PLATFORM.md
verified: 2026-10-09
---

# What Avrana Party is

Avrana Party is a **local multiplayer game appliance**. It is a small computer, today a
Raspberry Pi 4, that broadcasts its own Wi-Fi network and serves games to the phones that
join it. Each phone is both that person's controller and their own private screen. The
appliance coordinates everyone: it knows who is in the room, who is hosting, which game is
running and which screen each phone should be showing.

The intended experience takes about a minute to start. You switch the box on, your friends join
the Wi-Fi, everyone opens a web address in the browser they already have, and you play.

## The problem it addresses

Most group games for phones fall into one of a few patterns, and each comes with friction:

- **Shared-screen party games** need a television or a laptop that everyone can see, plus an
  internet connection to reach the game's servers. Everyone also has to type a room code.
- **App-based games** need everyone to install the same app, often create an account, and
  have working mobile data or venue Wi-Fi.
- **Self-hosted LAN game servers** avoid the cloud, but someone has to bring a laptop, set it
  up on the local network and explain to everyone how to reach it.

Avrana Party bets that the most reliable party is one that depends on nothing outside the box.
The appliance is the network, the server and the game library. That makes it usable where the
other approaches struggle: a cabin with no signal, a crowded venue with useless Wi-Fi, a
classroom, a long trip.

## The central idea: one party, many games

The early prototype ran several independent systems side by side: a fork of an open-source LAN
game hub, an arcade emulator stream and an experimental PlayStation stream. Each had its own
idea of who a player was and where they should be. The project then made a deliberate decision
([ADR 0002](../decisions/0002-party-platform.md)):
**Avrana Party is a party platform, and games are consumers of it.**

In practice the appliance owns the things that should persist from one game to the next:

- **Who is here.** The phones in the Party, their display names and avatars, and whether
  each one is present right now.
- **Who decides.** The **host** picks games and moves the group. If the host's phone goes away,
  the role passes to someone else automatically.
- **Where everyone is.** The Party has exactly one location (Party Home, a game's setup, a game
  in progress or a game's results), and every phone follows it.
- **Navigation, the catalog and the social layer.** These are platform surfaces, not something
  each game reinvents.

Games own their rules, their screens and their private state. A game never learns a phone's
long-term identity. It receives short-lived, single-purpose credentials for one session and an
anonymous participant id for each person. The [architecture section](../architecture/index.md)
explains how that boundary works and why it is drawn where it is.

## The main pieces

| Piece | What it is | Where it lives |
|---|---|---|
| **The appliance** | A Raspberry Pi 4 running its own Wi-Fi access point, local DNS, nginx and the services below | Configuration in `avrana-party` (`deploy/`, `ops/`) |
| **Party Home** | The web app every phone opens: the game library, profile, Party view and setup screens | `avrana-party` (`web/party/`) |
| **Party Core** | A small Python service that holds membership, the host role, the Party's location and the session with the current game | `avrana-party` (`avrana/party/`) |
| **Games** | Browser games whose server runs on the appliance. **BLUFF**, a hidden-role card game, is the first Avrana-native title. **EXPO**, an adaptation of a cooperative trick-taking game, is the second Party-integrated game | `avrana-party-games` |
| **Arcade** | An emulator on the appliance whose video is streamed to phones, which act as gamepads. *Gauntlet II* is the working example | `avrana-party` (`arcade/`) |
| **Contracts** | Machine-checked declarations of what Party offers games and what games require | `avrana-party` (`contracts/`) and `avrana-party-games` (`provider/`) |

The [repository ecosystem](../developers/ecosystem.md) page describes each repository in more
detail.

## What it is not

Some boundaries matter as much as the features. The roadmap states them explicitly:

- **Not a cloud service.** There are no accounts, and nothing needs the internet for core play.
- **Not a store.** Installing games is meant to stay open, with no marketplace, payments or DRM.
- **Not a universal game engine.** Rules, rendering and netcode belong to each game. Shared
  platform code grows only when a second game needs it.
- **Not a multi-room server.** One appliance hosts one Party, which does one activity at a time.
- **Not dependent on a TV or an app.** Either may exist later as an optional convenience. The
  phone-only party is the baseline.

## Who it is for, today

The roadmap is candid about this. Version 1.0 is meant for the project's owner: to prove that a
whole party night works and is fun. Commercialization, a crowdfunded appliance or a community
game ecosystem come later, and only if that proof holds. The current Linear project describes
1.0 as **"friend-ready"**. Its next evidence gate is four people on four real phones finishing a
round of BLUFF offline, including a reconnect.

Next: [why the project insists on phones, and only phones](phone-first.md).
