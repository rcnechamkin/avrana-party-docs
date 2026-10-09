---
title: Accessibility
description: "The accessibility rules every page a player uses must meet, the game contract's accessibility block, proposed per-player preferences, the BLUFF audit, and how accessibility is tested."
sources:
  - avrana-party:docs/design/ACCESSIBILITY.md
  - avrana-party:docs/design/GAME-UX-CONTRACT.md
  - avrana-party:avrana/contracts/game.py
  - avrana-party:contracts/games/bluff.json
  - avrana-party:tests/offline/a11y.spec.ts
  - avrana-party:tests/party/a11y.spec.ts
  - avrana-party:tests/offline/party.spec.ts
  - avrana-party:web/party/app.js
verified: 2026-10-09
---

# Accessibility

!!! abstract "What this document governs"
    ACCESSIBILITY sets the expectations that the platform and every game must meet on any page a
    player uses: twelve MUST rules, a few SHOULDs, an honest accessibility block in each game's
    contract, a proposal for per-player preferences, and how to test. Its status line, dated
    2026-09-24, says **expectations, partly implemented**. The Party's own pages have automated
    accessibility checks <span class="avr-badge source">In source</span>; the audited fixes for
    BLUFF and the old LAN Games hub were proposed but **not applied**; per-player preferences are
    <span class="avr-badge planned">Planned</span>. Some file locations in the original's status
    line predate the move of Party Home into the main source tree.

## Why it matters here

The document treats accessibility as **product infrastructure, not polish**. Avrana has an
advantage most party games lack: every player holds their own screen. Larger text, higher
contrast, less motion or haptic cues can change **for one person** without changing anyone
else's game.

## The twelve rules

These apply to every page a player uses, on the platform and in every game. The
[game UX contract](game-ux-contract.md) applies them to the line between platform and game and
does not restate them.

1. **Real controls.** Use `<button>`, links and form elements. A clickable `<div>` needs a role,
   keyboard focus, Enter and Space handling and a name, so prefer a real button.
2. **Every control has a name.** Inputs have labels; icon-only buttons have an accessible label;
   icons inside buttons are hidden from assistive technology.
3. **Touch targets are at least 44 × 44 CSS pixels.**
4. **Text scales.** Never disable zoom. Size text in `rem`, and let the layout scroll rather than
   clip at 200 % text size.
5. **Never colour alone.** Whose turn it is, who is out, what can be targeted, who hosts and who
   is disconnected also get a word, icon or shape, such as badges reading "Host", "Away" or
   "OUT".
6. **Prompts are announced.** Use a polite live region for status, and an assertive one only for
   "your turn" or "answer now". Toasts and connection banners are status regions.
7. **Updates keep focus.** When new state arrives and the page re-renders, the focused control
   keeps or regains focus.
8. **Respect reduced motion and higher contrast** system settings: no confetti, no pulsing.
9. **Contrast** of at least 4.5:1 for text (3:1 for large text and control outlines), and a
   visible focus outline.
10. **No audio-only information.** A sound may accompany a cue, never be the cue.
11. **Names are text.** Player names are inserted as text, never HTML, and system messages use a
    separate element so no player name can pass for one. This rule serves security as well as
    accessibility.
12. **Language and width.** The page declares its language and has no sideways scroll at 375
    pixels.

The **SHOULDs**: a haptic buzz (where the player allows it) when a prompt appears; timers that
show remaining time as text as well as a bar; and a way to extend or pause timers for a player who
needs it. That last one is a game-design decision, recorded honestly in the game's
`timing_pressure` value.

## The accessibility block in a game's contract

Every game describes itself in a game contract (see
[Contracts, catalog and grants](../games/contracts-and-catalog.md)). Its accessibility block has
five keys, each `true`, `false` or `"unknown"`. "Unknown" is always allowed, so no author is forced
to guess.

| Key | `true` means |
|---|---|
| `color_independent` | nothing needed to play is conveyed by colour alone |
| `audio_required` | a player who cannot hear misses information needed to play |
| `text_scalable` | the game's text follows the player's text size |
| `reduced_motion_respected` | the game honours the reduced-motion setting |
| `timing_pressure` | there are deadlines or real-time play a slower player can miss |

In current source the contract validator knows these five keys, and the game contracts carry the
block (BLUFF, for example, declares timing pressure, no required audio, and colour independence
as unknown). The values are **display-only**: nothing filters or blocks a game on them yet. The
original document still points at an older experimental manifest location for this block.

Emulated games such as the arcade are honestly `text_scalable: false` and
`reduced_motion_respected: false`, because the platform cannot reflow or slow a video frame.

## Per-player preferences

<span class="avr-badge planned">Planned</span> The proposal: text size, high contrast, reduced
motion, haptics on or off, and handedness (which side the main buttons sit). They would be stored
per device now and per saved profile later, applied by the platform's shared stylesheet, and
exposed to games as CSS custom properties and attributes on the page. The game UX contract adds
that a game must honour reduced motion, sound off and haptics off.

Today the old LAN Games code has per-browser contrast, motion, sound and haptics flags, which are
meant to be the seed. The Party page honours only the phone's own system settings.

## The September audit

On 2026-09-24 the document audited, read-only, the LAN Games hub and BLUFF. These findings are a
snapshot of that date. The proposed fixes were **not applied** at the time, and the game UX
contract's later review (2026-10-04) still found the main BLUFF gaps.

**The hub was mostly good**: dialogs trapped and returned focus, icon buttons were labelled,
targets met 44 pixels, focus was visible, and there was a contrast toggle and a motion setting.
Its gaps were selection shown by colour only on filter chips and avatar cells, faint text at
about 3.4:1, several 9-pixel labels, and toasts and the reconnect banner not being live regions.
The hub page is no longer served in source.

**BLUFF**, ranked by impact:

1. Prompts are never announced. "Your call: challenge or pass?" is visual only, with 20 seconds
   to answer. Proposed fix: a deduplicated live region and an optional haptic buzz.
2. Every state update rebuilds the action bar and drops focus to the page body. Proposed fix:
   restore focus by a stable key after each render.
3. Choosing a seat to target, a card to lose or exchange picks uses clickable `<div>`s with no
   role, keyboard access or name; cards read their emoji twice; face-down cards say nothing.
4. Eliminated, targetable and current-turn seats are shown only by opacity, a red pulse and a gold
   ring. Proposed fix: an "OUT" chip, a target badge with a dashed outline, and a "current" marker
   for assistive technology.
5. The drawer's close button and the stepper buttons are unlabelled, and the drawer does not take
   or return focus.

At lower priority, BLUFF's fixed-height layout clips at large text; the document asks for that to
be checked on a phone during the playtest. BLUFF uses no sound, so it has no audio-only cues.

**Platform defaults to extract.** When a second game needs them, the document proposes lifting
a few helpers into shared code: an announce function with a deduplicated live region, a helper
that turns an element into a proper labelled button, focus restore across renders, a
screen-reader-only class and a default focus ring, status roles on toasts and the connection
banner, pressed states on chips, faint text raised to at least 4.5:1, and one shared reduced-motion
rule. None is built yet.

## How accessibility is tested

- **Automated, per page.** The original describes a smoke-test pattern (controls named,
  targets of at least 44 pixels, language set, no sideways scroll) and says to copy it for new
  pages. <span class="avr-badge source">In source</span> the Party page's offline browser test
  now checks, on each of its four places, that the language is set, that every control is at
  least 44 pixels in both directions and that there is no sideways scroll, in Chromium at phone
  sizes.
- **Automated, the Party shell.** <span class="avr-badge source">In source</span> Since the UX/UI
  redesign, shared accessibility helpers run over every shell page and Party state: contrast,
  control edges, names and reading order, each screen also drawn with more contrast and less
  motion requested, plus a Tab walk that checks for a visible focus ring at every stop. These run
  in Chromium only and replace none of the manual pass.
- **Manual, per release (about ten minutes).** VoiceOver on an iPhone or TalkBack on Android
  through one full round; the largest system text size; reduced motion on; one pass with a
  colour-blindness simulator.

The [testing guide](../developers/testing.md) explains how these tiers fit the project's wider
test strategy.

## Where the Party stands today

One concrete improvement since the audit: the Party's own roster and briefing now mark the host
with the visible word "Host" and an away member with the word "Away" and a greyed avatar, rather
than an icon or reduced opacity alone, which is what rule 5 asks for
<span class="avr-badge source">In source</span>. Like the rest of the October shell work, it is
not recorded as deployed or checked on a phone.
