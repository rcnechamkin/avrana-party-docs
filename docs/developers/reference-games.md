---
title: The reference games, explained
description: A guided walk through the two pieces of code that show what an Avrana game does, BLUFF and the test-only stand-in native game, without reading the source first.
sources:
  - avrana-party:avrana/games/standin/game.py
  - avrana-party:contracts/games/standin.json
  - avrana-party:deploy/games/avrana-game@.service
  - avrana-party:avrana/party/protocol.py
  - avrana-party-games:games/bluff/game.py
  - avrana-party-games:core/session.py
  - avrana-party-games:core/party_session.py
verified: 2026-10-09
---

# The reference games, explained

Two pieces of code show, better than any specification, what a game has to do to take part in a
Party. **BLUFF** is a real game, with real rules, hidden information and bots. The
**stand-in** is the smallest possible native game: it exists only to prove the native-game path
and has almost no rules at all. This page walks through both, so you know what to look for when
you open the code.

Both are referenced by file path in plain text. The **Canonical sources** block at the foot of
this page links to each file.

## The stand-in: the smallest native game

<span class="avr-badge source">In source</span>, test only. The stand-in lives in the Party
repository at `avrana/games/standin/`. It is a single Python module of about 300 lines that uses
only the standard library and the Party's own protocol code. Its game contract,
`contracts/games/standin.json`, says plainly that it must never be installed on a product
appliance. Only a CI test fixture grants it.

### What it is handed

A native game does not open network ports or read configuration files of its own. systemd starts
it from the shared `avrana-game@<slug>` unit template and hands it exactly four things:

- **A listening Unix socket**, already open, as file descriptor 3. nginx connects to it to serve
  the game's pages, and Party Core connects to it to launch and end sessions. The unit forbids IP
  networking entirely, so the process could not open an IP socket even if it tried.
- **Its own signing key**, in a credentials directory that only this running instance can read.
- **The address of Party Core's internal socket**, where it reports the end of a session.
- **The Party's browser origin**, so its pages can find the Party's bridge when game pages are
  served from their own origin.

### What it does

The stand-in answers five kinds of request, all under `/games/standin/`:

```mermaid
sequenceDiagram
  autonumber
  participant Core as Party Core
  participant Game as Stand-in
  actor Phone
  Core->>Game: launch (signed; roster of participants)
  Phone->>Game: GET the page
  Phone->>Game: redeem a Party ticket
  Game-->>Phone: a private game token + only this player's own view
  Phone->>Game: finish (with that token)
  Game->>Core: ended (signed) + result: this player won, the others lost
  Core-->>Game: result accepted
```

1. **Launch and end** arrive from Party Core as signed messages. The game checks two things: the
   request did not come through nginx (Party Core never sends proxy headers and nginx always adds
   them), and the signature is valid. It then starts or stops its session. A forged or replayed
   message is refused.
2. **Redeem** takes a single-use Party ticket from a phone and verifies it. It answers with a
   private token for that participant and *that participant's own view only*: their name and how
   many people are playing, and nothing about anyone else.
3. **Finish** declares the caller the winner. It builds a result envelope (the caller won,
   everyone else lost), stops admitting anyone new, and sends the signed `ended` message to Party
   Core. Party Core answers whether it accepted the result.

That covers the whole native-game contract in miniature: no IP networking, signed control
messages, ticket admission, per-viewer privacy and a reported result. The session logic itself is
the Party's reference `GameSide` class, used unmodified. The code is heavily commented with the
reasoning behind each choice. One example is why the session stops admitting players *before* it
reports the result.

What it deliberately does not do: stop itself when idle, or enforce resource limits. Both are
deferred to the Checkers work.

## BLUFF: a real game

<span class="avr-badge deployed">Deployed</span>. BLUFF lives in the Games repository at
`games/bluff/`. It is a module of the LAN Games framework, which is
[retiring](../games/execution-models.md#the-lan-games-fork), so read it for its **patterns**, not
its plumbing.

| File | What it holds |
|---|---|
| `game.py` (about 900 lines) | The rules, as a `BluffSession` class: turns, claims, challenges, blocks, timers, bots, forfeits and the result |
| `web/client.js`, `web/index.html`, `web/table.css` | The phone client |
| `web/onboarding.json` | The premise and rules that the Party's briefing screen shows |
| `README.md`, `PLAYTEST-BRIEFING.md` | Notes for humans and playtesters |

The patterns worth studying:

- **The server decides everything.** A phone sends an *intention*, such as "claim this role" or
  "challenge that claim". `game_action` checks that a game is running, that the sender holds a
  seat, and that the message answers the current prompt. Only then does `_apply` validate the
  move itself. A bad message gets an explanation back and changes nothing.
- **Every viewer gets their own state.** `game_state(viewer)` builds the view for one player: your
  own two cards, everyone's coin counts and revealed cards, but never another player's hidden
  hand and never the deck. Party spectators get a separate view through `game_state_spectator`,
  which in BLUFF shows every hand. That is deliberate, because spectators are not playing. Only a
  spectator connection admitted with a spectator ticket ever receives it. The Games repository has
  dedicated security and isolation tests for this.
- **Prompts are numbered.** Each decision point carries a step number, and an answer for an old
  step is rejected. A slow phone can't apply its answer to the wrong question.
- **Time is the server's.** `game_tick` handles every deadline: a turn that takes too long, a
  challenge window that closes, a player who never picks which card to lose. A sleeping phone
  can't stall the table, and bots and an autopilot can act for absent players.
- **The result is honest and public.** `game_result` reports one winner and everyone else as lost,
  plus a few public facts (how long the game ran, how many seats were bots, who forfeited). It
  includes no card or hand.

Party integration happens around the game rather than inside it. The Games repository's
`core/party_session.py` loads the key, accepts the Party's signed launch and end, admits phones
by ticket and sends `ended` back with the result. A new native game would do the same things
itself, the way the stand-in does.

## Where to go next

- [Starting a game](starting-a-game.md): what you can realistically build today.
- [Running a game session](../architecture/game-sessions.md): the protocol both games speak.
- [Designing for phones](../games/designing-for-phones.md): the design checklist BLUFF follows.
