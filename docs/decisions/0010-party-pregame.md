---
title: "ADR 0010: The Party's pregame"
description: Why the Party, not each game, runs the moment before a round, where everyone chooses Play or Watch and only the host starts.
sources:
  - avrana-party:docs/adr/0010-party-pregame.md
  - avrana-party:docs/adr/0011-party-console-model.md
  - avrana-party:avrana/party/core.py
  - avrana-party:avrana/contracts/party_config.py
  - avrana-party:contracts/games/bluff.json
  - avrana-party:web/party/lib/party-mode.js
  - avrana-party-games:core/session.py
verified: 2026-10-09
---

# ADR 0010: The pregame belongs to the Party (Play or Watch, host starts)

!!! abstract "At a glance"
    **Decided:** 2026-09-29 · **Status:** <span class="avr-badge deployed">Deployed</span> for BLUFF; the setup screen itself was moved to Party Home by [ADR 0011](0011-party-console-model.md)
    Before a round starts, everyone in the Party chooses **Play this round** or **Watch this
    round**, and only the host can start. The game then skips its own lobby.

## The problem

On real phones on 2026-09-29, BLUFF could begin as soon as enough players pressed Ready, and
**any** ready player could press Start. Launching BLUFF from Party Home opened BLUFF's own
ready-and-countdown lobby: a second lobby after the Party's, where the host had no role. Nobody
could choose to watch a round instead of playing it. BLUFF's only watching view was the TV view,
which hides every hand.

Two open issues framed the answer. One asked what a game's lobby should do once the Party has
formed, without building a general lobby framework. The other asked for a shared
briefing-and-ready pattern that games fill in.

## What was decided

**1. The Party owns the pregame.** A game configured for a pregame does not launch straight away.
The host's start opens the session in a new **setup** state. Nothing runs at the game yet, and
every phone is moved to the setup. Each member who is present chooses Play or Watch and can change
their mind until the start. Only the host can start the round, and Party Core refuses until:

- every member who is present has chosen, and
- the number choosing Play is within the game's minimum and maximum.

Members who are away do not block the start; someone who joins during setup must choose too.
The choices become the roles in the ordinary launch message, players first, then spectators.
During setup the host can also end or switch; nothing has reached the game, so there is nothing to
stop there.

**2. Roles change only between rounds.** During a round, changing your choice is refused ("Roles
change between rounds"). Late arrivals and people coming back from away join as spectators. The
next time the host picks the game, a fresh setup starts with no choices carried over. Seats in a
live round never move.

**3. Game pages wait instead of joining alone.** While the round is being set up, a game page
asking for a ticket is told "setup". The page opens no connection to the game, shows that it is
waiting, and asks again every two seconds. The host's start arrives as a ticket, and the page
joins with its role.

**4. The Party draws the setup; the game supplies its rules.** The Party drew the setup panel:
who plays, who watches, who is still choosing, the Play and Watch buttons, and Start for the host
only, disabled with the reason written out. A game could step in just before a member's Play;
BLUFF used that to show its first-play briefing, so nobody plays without having seen it.

**5. A Party round skips the game's own lobby.** In the shared games code, a Party round seats the
launch roster's players at once and refuses the game's own Ready, Start and settings actions ("The
Party Host starts rounds from the Party"). The round begins after a 3-2-1 countdown once every
seated phone has arrived, or after 15 seconds; missing players start as away, so BLUFF's grace
period and autopilot cover them. Playing BLUFF without a Party keeps its own lobby.

**6. Spectators see what the game allows; BLUFF allows everything.** BLUFF's spectator view is
deliberately all-seeing: every hand, and the exchange draw while one is open. Only a Party
spectator's connection gets it. Players see only their own cards; anonymous watchers, including a
TV the players can see, get the public view. When the Party session ends, spectator connections
become ordinary watchers, so the all-seeing view never leaks into a later game.

## Why this way

The ADR draws a firm line between what is reusable and what is BLUFF's own:

| Shared by any Party game with a pregame | Specific to BLUFF |
|---|---|
| The setup state, choices, host-only start, player limits and the between-rounds rule | The briefing content and its gate |
| The Party's setup interface | The look of its setup screen |
| Seating from the roster, refusing lobby actions, the arrival countdown, a spectator view hook | The all-seeing spectator view |

The record is explicit that this is **not a lobby framework**. Party Core decides who plays.
Games keep their own rules, seating and drawing.

## What it means in practice

Only the host can begin a round, and the Party is where people decide whether to play. Two
limits were accepted. Party identity is per device, so a player whose second phone joined as
another member could watch as a spectator and see every hand; social norms cover that. And a
spectator cannot become a player in the middle of a round, by design.

Deployment order mattered. Party Core had to go first and the game pages before the pregame was
switched on, otherwise old game pages would have misread "setup" as "no Party" and joined a
standalone room.

## Later changes

- **[ADR 0011](0011-party-console-model.md), the console model.** The setup is no longer a panel
  above the game page. It is a full-screen scene on Party Home, in the Party's own design, with the
  game supplying its premise and rules as data. A Party round's results are now held until the host
  moves on. The Play and Watch rules, host-only start, the role boundary and spectator privacy
  are unchanged.
- **2026-10-03 amendment (AVR-229).** <span class="avr-badge source">In source</span>. Whether a
  game has a pregame, and its player limits and late-join rule, are no longer typed into the
  appliance's Party configuration. Party Core reads them from each game's contract when it starts.
  A configuration that still carries its own copy must agree with the contract, or Party Core
  refuses to start. Turning on a pregame is now a contract change, so the games side must be
  deployed first.

## Where it stands today

<span class="avr-badge deployed">Deployed</span> on 2026-09-29 with BLUFF's pregame switched on,
verified on the server side. BLUFF's contract asks for a pregame with two to six players. The
full-screen setup scene from ADR 0011 is <span class="avr-badge source">In source</span> and
<span class="avr-badge reported">Owner-reported</span> as deployed.

Not yet checked on real phones: setup and start, the briefing gate on a first-time phone, a phone
that sleeps during setup, a four-person round with a spectator, and whether the 15-second arrival
wait and the two-second setup poll are well tuned.

## Related decisions

- [ADR 0006: the session protocol](0006-party-session-protocol.md), whose launch message carries
  the roles.
- [ADR 0008: Party navigation](0008-party-navigation.md), which moves everyone to the setup.
- [ADR 0011: the console model](0011-party-console-model.md), which moved the setup to Party Home.
- [The Party](../architecture/party.md#setup-play-or-watch), for setup as it works today.
