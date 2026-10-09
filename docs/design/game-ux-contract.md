---
title: The game UX contract
description: "Where the line runs between the Party and a game on a player's phone: phases, the briefing, rules access, unavailable actions, interaction floors, system cues and art, with each rule's status."
sources:
  - avrana-party:docs/design/GAME-UX-CONTRACT.md
  - avrana-party:docs/adr/0010-party-pregame.md
  - avrana-party:docs/adr/0011-party-console-model.md
  - avrana-party:avrana/party/core.py
  - avrana-party:web/party/app.js
  - avrana-party:web/party/lib/party-follow.js
  - avrana-party:web/party/lib/limited.js
  - avrana-party:web/src/party.css
  - avrana-party:contracts/games/arcade-gauntlet2.json
  - avrana-party-games:games/bluff/web/onboarding.json
verified: 2026-10-09
---

# The game UX contract

!!! abstract "What this document governs"
    GAME-UX-CONTRACT answers one question: **where the line runs between Avrana and a game on a
    player's phone, and which behaviours are the same in every game.** It covers the phases of
    a round, the pre-round briefing, rules access, how unavailable actions are explained, shared
    interaction floors, system sound and art slots. It was written for issue AVR-56 on
    2026-10-04 and updated with owner decisions of 2026-10-05. **No part of it has been
    validated on real phones**, and the first four-person BLUFF playtest it depends on (AVR-27)
    has not happened. It changes no machine contract. Many of its rules are still proposals.

## How to read the labels

The original labels every rule, and the labels matter because they are not interchangeable.
This page keeps them:

- **Implemented**: in source on `main` when the contract was written (2026-10-04), with a cited
  file. Equivalent to <span class="avr-badge source">In source</span>: not a claim of deployment
  or phone proof.
- **Accepted**: stated by a source with its own authority, such as an accepted ADR, the
  accessibility expectations, or a dated owner decision. It carries only the scope its source
  states; several owner decisions apply to EXPO only.
- **Proposed**: drafted by the contract itself. Direction for review, not contract, until the
  owner accepts it.

A single rule often mixes labels: an accepted sentence followed by a proposed reading of it.

The contract deliberately leaves neighbouring questions to other documents: the Party page's
visual system (UI-DESIGN-SYSTEM), the accessibility rules ([Accessibility](accessibility.md)),
the state machines ([Party lifecycle](party-lifecycle.md)), the wire between Party and Games
([the Party ↔ Games contract](../games/contracts-and-catalog.md#the-party-games-contract)),
chat (a proposed COMMUNICATION design) and Full versus Limited Mode
([Limited Mode](limited-mode.md)).

## The boundary: behaviour versus look

**Accepted (AVR-56).** The interaction layer should feel coherent across the Party and games
"without making every game look identical"; games keep intentional visual identity, and shared
feedback is not a requirement that every game share one art direction or sound design.

The contract's **proposed** reading is a memorable one: Avrana is recognizable by *behaviour*, a
game by *look and sound*. A game may have its own palette, typeface, motion and sound, unrelated
to the Party page.

**Accepted (ADR 0011).** Once play begins, platform chrome recedes and the game owns the
viewport. The ownership split, in brief:

| Concern | The platform owns | The game owns |
|---|---|---|
| Who is in the Party, who hosts, where the Party is | everything | nothing; a game keeps no host or membership |
| Name and avatar | the identity and its picture | where and how large it is drawn; an in-game persona if its rules need one |
| Briefing | the shell: layout, roster, Play/Watch, Start, rules sheet | the content: title, art, accent, premise, rules |
| Play | reconnect recovery, moving phones, a fallback End if the game draws none | the whole viewport, its controls, feedback and sound |
| Results | holding the Party there; the host's Play again and Party Home | how the result looks and what it celebrates |
| What is legal | nothing; there is no Avrana rules engine | all of it |
| Interaction floor | touch target, focus, confirmation, sheet and reduced-motion rules | meeting the floor in its own style |
| System cues | join, leave, ready, attention, connection | all game sound, music and haptics |

**Proposed.** A game must not restyle or imitate surfaces that carry trust: the Limited Mode
notice, the connection state, the host line, or the briefing's Ready and Start. It must not draw a
control labelled as a Party action unless it actually calls the Party's verb for it.

## Phases of a round

The location model is the console model's (see [Party lifecycle](party-lifecycle.md#the-partys-location)).
The contract reads it as four phases:

| Phase | Who draws it | Platform chrome | The host can | Everyone else can |
|---|---|---|---|---|
| Home | platform | all of it | pick a game | browse, edit their profile, chat where shown |
| Briefing | platform shell, game content | the shell is the screen | Start; pick another game | choose Play or Watch; read the rules |
| Play | game | none, except a reconnecting state | End for everyone (confirmed); game-defined host actions | play or watch; open the rules |
| Results | game | none | Play again; Party Home | look; wait for the host |

The rules for moving between them are mostly **accepted and implemented**:

- When the host picks a game, every phone moves into it. There is no per-game Join, admission or
  second membership step.
- While the Party is in a game, a non-host has no normal route back to Party Home or another game;
  the game's own global navigation is hidden in a Party, and a page in the wrong place is moved
  back.
- Only the host moves the Party: select, Start, End, Play again, Party Home. A follower's own
  actions never change the location. (**Proposed** generalization: a game's own forfeit or
  sit-out must not move the player's page either.)
- Reconnecting is recovery, not a choice. A phone that reloads, wakes or regains Wi-Fi lands where
  the Party is now, in its existing role, with no prompt or Rejoin button.
- A game that draws its own host controls uses the `window.AvranaParty` interface. A game that
  does not gets one host-only "End game for everyone" control from the platform. Whether a phone
  shows host controls is a drawing decision; the Party authorizes the action itself.
- Everyone who is not the host is always told **who they are waiting for, by name**, in the
  place the host's control sits ("Waiting for Dana to start"). Implemented in the briefing,
  BLUFF's results bar and the shared "Round over" panel; proposed as a rule.

**Proposed**, and limited by an accepted decision: during Play and Results the platform shows
only a connection-lost state while it is true, a system cue, and the rules overlay described
below. No Party prose, persistent bar or brand mark over the game. ADR 0011 says that during a
round the page shows no Party prose, so *any* platform overlay in play needs an amendment to that
ADR.

## The briefing

A game with a pregame opens with a **briefing**: the Party's own full-screen scene for that game,
modelled on the screen before a Mario Party minigame. It is a state of the selected game, not a
second joining ceremony. A game without a pregame has no briefing, and this is accepted; not
every title needs one.

**Accepted and implemented**, the briefing shows the game's title, art and premise, a "How to
play" sheet, the roster with each person's state (the word "Host", Playing, Watching, Choosing,
or "Away" with a greyed avatar), the two choices **Play this round** and **Watch this round**, and
either the host's Start or everyone else's waiting line. The library, chat and "This phone"
controls are hidden so it reads as the game's screen, not Party Home. Since a redesign decided on
2026-10-05, the list of people here and, on a Limited Mode phone, the Limited explanation can
open over the briefing without leaving it; chat cannot.

**Proposed**: a game's accent and art may tint more of the briefing than the cover, so two games'
briefings do not look like the same page with a different icon, while layout, positions and
wording stay fixed. Today only the cover takes the accent.

### Play, Watch and Start

**Accepted (ADR 0010) and implemented.** Every member who is here answers Play or Watch once per
round and may change their answer until the Start. Only the host starts. Party Core refuses until
everyone here has answered and the number of players fits the game, and shows why in a sentence
("At most 2 can play; 5 chose to play."). Away members do not block. There is no allocation rule
for too many players: someone has to change their answer. Roles change only at this boundary,
and a late arrival watches.

**Accepted (owner decision, 2026-10-05).** Watch is "a legitimate round-role choice". It may be
drawn as visually secondary to Play, but it must never be treated as an invalid or shame-path
fallback, and nobody may be forced into Play just so the Party can proceed. Today both choices
are equally large and Watch is always offered.

**Accepted, not built.** If a game declares that it has **no spectators**, the platform must not
invent a fake spectator view. A member who is not playing sees a clear state equivalent to "Game
in progress / You are not playing this round", keeps appropriate Party-level access, and rejoins
normal participation when the game ends. Where that state is drawn, and what the non-Play answer
is labelled in the briefing, are not designed. The one game that declares no spectators today is
the arcade, which has no briefing.

**Accepted for Limited Mode and implemented.** A phone that cannot play a game here sees Play
disabled with the reason beside it, and Watch stays available.

**Accepted (ADR 0010).** A game in a Party round must not run a second lobby. Its own ready, start
and settings actions are refused and the launch roster is seated at once.

### First play, simple games and heavy games

**Implemented.** A player who has not acknowledged a game's current briefing sees How to play
before their first answer, and "Got it, I'll play" counts as their Play. The acknowledgement is
remembered in that browser only; it is a convenience, not a record.

**Accepted (AVR-56).** For a **simple game**, the game provides content and Avrana provides the
familiar shell: the objective, the basic flow, the controls, and a clear Ready. A static or
lightly animated *fake-turn example* is preferred over a second interactive tutorial engine.
**Proposed**: no game must ship a playable tutorial; the example is one to four frames of the
game's own art with a caption each; and a simple briefing should be readable in about twenty
seconds (BLUFF's five short sections are the reference size). The example strip is not built.

**Accepted (AVR-56).** A **heavier game** provides a concise **Quick Start** that gets players to
their first meaningful turn, plus a structured **Rules Guide** with sections that can be linked,
searched and indexed by future tooling, and contextual help may link straight to a section.
**Proposed**: a game is "heavy" when its author ships a guide; search is a plain on-phone text
match with no network. None of this is built. EXPO, with 96 tasks and mission modifiers, is
named as the first consumer.

### Settings

**Accepted (AVR-56).** Host settings should not appear unless a game genuinely needs pre-start
configuration. The owner **deferred** host settings in the briefing as a platform question. For
EXPO only, and "for now", the owner decided that its mission and seating choices happen inside
EXPO before the first deal, with no change to the Party contract; the Party Host only confirms,
and game-specific choices stay with whoever the game's rules assign them to. A shape for
shell-drawn settings is **proposed** for whenever the question returns; it would need settings to
travel with the launch, which the session protocol does not carry.

## Rules content and rules during play

**Implemented.** A game may serve an `onboarding.json` file beside its page, in a small format
called `avrana.onboarding/v0`: a premise, an acknowledgement key and version, a few named facts,
and a list of rule sections with short points. Numbers such as a card cost are written once as
facts and filled into the text, so a test can pin them to the game's rule code. A game with no
file gets its catalogue summary as the entire How to play. The format is a convention and is not
declared in the Party ↔ Games contract.

**Proposed, not built.** A draft `avrana.onboarding/v1` would add stable section ids (for links,
search and tooling), a Quick Start, the Rules Guide, the example frames, a catalogue of
unavailable-action sentences and the deferred settings. It stays plain text, never executes
anything, and loads nothing from the internet.

**Accepted (AVR-56 and an owner decision of 2026-10-05), not built.** Rules must stay reachable
during play through a **platform-standard overlay or sheet** that opens without navigating away
from the running game. This requires amending ADR 0011's rule that the game owns the viewport,
which has not been done. Today BLUFF and EXPO each draw their own rules sheet in play.
**Proposed**: opening the rules never pauses, forfeits or desynchronizes the game, never hides a
pending prompt without saying so, and shows the same content as the briefing, from one source.
Neither game meets that last point today.

## Identity in a game

**Accepted and implemented.** Cross-game identity is the Party's: a game keeps no parallel
profile or token. Avatars are the 32 bundled Gaze avatars, also vendored into games. Names are
rendered as text, never markup, and system text never looks like a player said it. A game never
receives device identity and never decides who the host is.

**Proposed**: in a Party round a game must not ask for a name or offer its own avatar picker;
wherever it shows a person it shows the Party name and should show the Party avatar (framed in
its own style if it likes, with an in-game persona beside it); and "Party Host" is labelled
distinctly from any in-game leader role, as EXPO does with its Captain.

## Legal moves and unavailable actions

**Accepted (AVR-56).** Normal UI makes an illegal move difficult or impossible, and the game's
server validates every action regardless of what the client showed. There is no universal rules
engine.

**Accepted for EXPO only; proposed for every game.** Games are **referees, not oracles**: a legal
move that happens to be bad for the player is never warned about, marked, ranked or confirmed for
its consequences. A confirmation exists only to catch slips and irreversible actions ("Play 7 of
blue?" on a small card is fine; "Are you sure? This loses the mission" is not).

**Proposed.** When a player can reasonably expect a control that is unavailable right now, it is
shown disabled with **one plain sentence saying why**. The sentence is visible text, never only a
tooltip; it comes from the server along with the legality it explains; it speaks in the game's
own terms with no code, states or error names; it never reveals hidden information; it names the
person being waited for; and it may link to a rule section. A refusal after a tap uses the same
sentence. For EXPO, the owner decided the server's wording is the single source.

Today Party Core's Start blocker, the Limited Mode reasons and the library's "fits this phone"
line implement this on the Party side; EXPO implements it in its own code; BLUFF draws
unavailable actions disabled with no reason. There is no shared primitive.

## Controls, surfaces and confirmation

These are floors a game meets in its own visual language.

- **Touch targets** of at least 44 × 44 CSS pixels (**accepted**, with no exception). Proposed:
  that includes cards, seats and board cells; a dense board that cannot reach that size might use
  select-then-confirm, but only after the accessibility rules are amended to allow it.
- **Buttons** (proposed): one primary action per region; destructive actions never styled as
  primary or placed where the primary just was; pressed and busy states visible at once.
- **Sheets and dialogs** (proposed): anything that is not this turn opens as a sheet; sheets are
  properly modal for assistive technology, close with Escape or a visible Close, and return focus
  exactly where it was; only one is open at a time. EXPO and the Party's rules dialog implement
  this.
- **Phone-first layout** (proposed): designed from 360 pixels wide, portrait, one hand; play fits
  one viewport without scrolling; the primary action in the bottom third; nothing depends on
  hover or a keyboard.
- **Messages** (proposed): toasts are short, never steal focus, and never the only place a fact
  appears; connection loss is one calm line ("Reconnecting…"), not a takeover.

**Accepted (owner decision, 2026-10-05).** The Party Host may end a game unilaterally, after one
simple destructive confirmation equivalent to **Cancel / End Game**: no vote, no captain approval,
no second ceremony. BLUFF's dialog already has that form. The platform's fallback End and EXPO
use "tap again within four seconds", which offers no Cancel; bringing them into line is a recorded
follow-up.

## Accessibility, degraded states and preferences

The twelve rules in [Accessibility](accessibility.md) apply to the platform and every game
(**accepted**). The contract adds, as **proposals**: the platform shell is accessible by
construction so games inherit it; turn and prompt state ("your turn", "answer now") is announced
through a live region and is also a word on screen; timers show remaining time as text, and a game
should let the host relax a turn timer.

**Proposed** per-device preferences (reduced motion, higher contrast, system sound, haptics, later
text size and handedness) would be exposed to games as attributes on the page, and a game must
honour reduced motion, sound off and haptics off. Today only the old LAN Games code has such
flags, and the Party page honours only the phone's system settings.

For degraded situations, the **accepted** rule is that capabilities degrade individually and
visibly. The **proposed** message shape everywhere is: what is different on this phone, what
still works, and what, if anything, the player can do. A problem is said once, where the decision
is made, not repeated as a banner over play. Being offline from the internet is normal and never
mentioned; being unable to reach the Party says so, retries on its own and offers one Try again.

## System sound and motion

Nothing here is built: the Party page has no audio or vibration calls.

**Accepted (owner decision, 2026-10-05).** Restrained platform sounds are allowed for lifecycle
transitions, launch and entry, errors and important platform state changes. Games own their
gameplay soundscape, and the platform should not layer unnecessary sound over a game's audio.

**Proposed**: a closed, small cue set (join, leave, ready, attention, connection), each under 400
milliseconds, coalesced, never the only carrier of information, silent until a tap has unlocked
audio, and only *attention* and *connection* during play. Never music, voice or ambient sound
from the platform. Platform transitions are short fades, removed entirely under reduced motion,
with no branded interstitial before a game. The exact cue set and whether platform sound is on
by default are still to be designed.

## Results and the end of a round

**Accepted (ADR 0011).** A completed round's results are held until the host chooses Play again
or Party Home, with no automatic timer. An abandoned round has no results screen. Play again
returns to a fresh briefing with no choices carried over; a rematch that skips the briefing would
amend two ADRs.

**Proposed**: the results screen is the game's own and says first, in words, who won or what
happened, with the host's two choices and everyone else's waiting line in the same place on every
phone. No game ends a Party round or sends phones home by itself (**accepted** for BLUFF).

## Art

**Accepted (AVR-56).** No emoji is implicitly required as production game art. **Proposed**: no
platform slot assumes an emoji, because emoji render differently on every phone; a game may use
symbols where they are notation, such as card suits. Platform slots today are a square cover, an
accent colour and a summary line; example frames and wide hero art are proposed. Everything a page
needs comes from the appliance, never a remote address.

## What exists and what is only specified

**Built** (in source): the authoritative location and follow rule; host controls for a game's own
chrome with a fallback End; host authority checked at the action; the briefing shell with Play,
Watch, Start and the blocker sentence; the rules sheet and first-play acknowledgement; the v0
onboarding file; avatars and roster; capability and fit explanations; connection state; held
results with the "Round over" panel.

**Specified only**: the not-playing state for games without spectators; the platform rules
overlay in play; one Cancel / End Game confirmation everywhere; the accent beyond the cover; the
fake-turn example; shell-drawn settings; Quick Start, Rules Guide and onboarding v1; a shared
unavailable-action shape; shared announce, sheet and confirm helpers; Party-owned preferences;
system sound and haptic cues. The contract asks for no component library: a shared primitive is
built when a second game needs it.

## Pressure tests

The contract tests itself against four kinds of game:

- **BLUFF** fits well. Its strains: its in-play rules are a second, richer copy of the briefing's
  text, its disabled actions carry no reason, and its 20-second response timer has no host
  setting.
- **EXPO** fits on one-viewport play and server-owned reasons. It strains as a heavy game with
  no onboarding file (so its briefing shows only a summary) and settings that today exist only
  in its standalone lobby.
- **A simple two-player classic** in a party of six makes Watch the ordinary answer for most of
  the room, which is why Watch must never feel like a penalty, and makes the "too many players"
  blocker the main event.
- **A hypothetical real-time game** strains the most: sheets over live action cost the player,
  per-action sentences do not suit continuous input, and reduced motion cannot remove motion that
  is the game. The contract notes that no such native game exists, so this is reasoning, not
  evidence.

## Follow-ups and outstanding evidence

The owner's decisions of 2026-10-05 create work the contract does not do itself: amend ADR 0011
to admit the rules overlay; bring the host's End to one confirmation form; design the platform
sound cues; design the not-playing state; and design the rules overlay, including how it works
once games are on their own origin.

The contract also lists observations of current source against its rules (for example, BLUFF's
prompts are not announced to screen readers, and EXPO's top bar shows the platform's name above
the game's). It treats them as observations, not tasks.

Above all, the contract is unproven with real people. The four-person offline BLUFF playtest may
change the briefing's size limits, the first-play gate, the all-answer Start gate, how prominent
Watch is, the waiting line, and which platform sounds are worth having.
