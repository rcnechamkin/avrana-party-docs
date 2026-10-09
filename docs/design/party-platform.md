---
title: Party platform design
description: "The platform's thesis and principles, its identity layers, admin versus host, the social and progression layers, and its proportionate security model, with what is built separated from what is proposed."
sources:
  - avrana-party:docs/design/PARTY-PLATFORM.md
  - avrana-party:avrana/party/core.py
  - avrana-party:avrana/party/identity.py
  - avrana-party:avrana/party/result.py
  - avrana-party:docs/adr/0002-party-platform.md
  - avrana-party:docs/adr/0003-ids-and-keys.md
  - avrana-party:docs/adr/0011-party-console-model.md
  - avrana-party:docs/adr/0015-game-result-envelope.md
verified: 2026-10-09
---

# Party platform design

!!! abstract "In short"
    The hub design for Avrana Party: what the product is, the principles every design must
    respect, the decisions the owner has locked, the concepts behind "a player", the split
    between the appliance's administrator and a party's host, and a security model sized to a
    party among friends. The engineering document (PARTY-PLATFORM) is **canonical design
    direction**.

    **Where it stands:** only part of it is built. Party Core, Party Home, game sessions and
    synchronized navigation exist, while profiles, teams, votes, progression, moderation and
    third-party installation are still proposals. Its status line was last reconciled on
    2026-10-01 and 2026-10-02, so it is older than some of the October code. This page follows
    the code where they differ.

## Built and proposed at a glance

| Area | State |
|---|---|
| One Party per appliance, members, presence, host and succession | <span class="avr-badge deployed">Deployed</span> (Party Core v0) |
| Automatic presence with no Join button (the console model) | <span class="avr-badge source">In source</span> · <span class="avr-badge reported">Owner-reported</span> as deployed |
| One authoritative Party location that every phone follows | <span class="avr-badge deployed">Deployed</span> (navigation); console presentation <span class="avr-badge reported">Owner-reported</span> |
| Play or Watch setup with host-only Start | <span class="avr-badge deployed">Deployed</span> |
| Display-name rule (normalization, reserved words, one alphabet) | <span class="avr-badge source">In source</span> in Party Core |
| Structured game results checked by the Party | <span class="avr-badge source">In source</span> (ADR 0015), held in memory only |
| Full Mode and Limited Mode; separate Party and game origins; isolated native games | <span class="avr-badge accepted">Accepted direction</span>, with parts <span class="avr-badge source">In source</span> |
| Saved profiles, PINs, trusted devices, the System Admin role | <span class="avr-badge planned">Planned</span>, design only |
| Teams, queue and voting, achievements, history, moderation presets | <span class="avr-badge planned">Planned</span>, design only |

## The thesis

The document opens with one sentence: **the game may change; the party does not.** Avrana Party
is described as a portable local multiplayer platform whose games plug into a shared Party. It is
deliberately *not* a ROM box, a LAN Games front end or a phone game launcher.

Technically, the sentence means that the Party is a long-lived object that outlives every game
session. A phone with a name and avatar is in the Party without pressing Join. A game is a
session the Party starts and ends. When a round finishes, its results stay on screen until the
host picks Play again or Party Home, and the next round begins with a fresh Play-or-Watch choice
rather than a re-join. (Whether the Party survives an appliance reboot is still open; see
[the lifecycle page](party-lifecycle.md#still-open).)

Avrana claims ownership of everything social around a game: presence, seats, roles, the host,
navigation, reconnect, spectators, chat, and in time profiles, teams, voting and stats. It is
also meant to be the **only writer of the durable record**: results, history and attribution to
a person. Games decide what happened in a round and report it; they are consumers of platform
services, not co-owners of platform state.

The document is equally clear about what the platform is not: a universal gameplay framework
(rules, state, rendering and turn logic stay with each game), a social network or cloud account
system, a store, or something that depends on a captive portal or an app. The first real version
is for the owner, to answer one question: can the whole experience actually work and be fun? A
later commercial path is acknowledged only as a reason to avoid obvious dead ends.

## Product principles

The document lists 21 durable principles; breaking one needs a recorded reason. Grouped by
theme, they say:

- **The Party is the constant**: one appliance, one party, one activity at a time, with
  navigation synchronized across everyone.
- **No friction**: browser-first, guest-first, no app, no TV required, never an account step.
- **Identity belongs to Avrana** and games consume it; no game reinvents profiles, chat,
  reconnect, teams, spectators or session lifecycle. **Device identity is not human identity.**
- **Authority is separated**: admin is not host, and game code is not Party code.
- **Honesty and resilience**: never claim what cannot be observed; work offline; prefer trusted
  HTTPS but never require it.
- **The phone is not just a controller**: it is each player's private screen (see
  [Designing for phones](../games/designing-for-phones.md)).

## Locked product decisions

On 2026-09-24 the owner locked a set of product answers: one active party per appliance; no
mandatory TV (games may still declare that they need one); host migration when the host
disappears; late joiners watch by default unless a game opts into more; no modelling of physical
seating; no proprietary store; no required native app or captive portal; and phones forming one
big display only as an experiment.

A second set was added on 2026-10-02, each recorded in an ADR and labelled
<span class="avr-badge accepted">Accepted direction</span>:

- the Party must survive the loss of trusted HTTPS ([ADR 0012](../decisions/0012-limited-mode-party-survives-https-loss.md), explained in [Limited Mode](limited-mode.md));
- the Party shell and games live on separate browser origins ([ADR 0013](../decisions/0013-party-and-game-browser-origins.md), explained in [Browser origins](browser-origins.md));
- LAN Games is not the native-game runtime; native games run as independent, isolated processes
  ([ADR 0014](../decisions/0014-native-games-isolated-lan-games-retired.md));
- the Party owns results and history, and games only report;
- a person is only ever represented by an explicit, optional, server-side Profile, never by a
  browser-stored name;
- tickets are single-use and signed with a secret key that both sides share (HMAC); public-key signatures are kept
  for package provenance;
- native games are validated in order: BLUFF, then Checkers, then Spades, and no SDK or package
  format is frozen before that.

## The browser is the product

A player joins the Avrana Wi-Fi, opens the party address, and from then on the browser is their
whole interface. Two consequences drive much of the design.

**Identity lives in exactly one browser origin.** Browsers keep separate cookies and storage per
host name, so one phone reaching the appliance by two names looks like two devices, with two
presences and two votes. The design therefore never spreads Party identity across origins or
tries to recover it across them. The trusted Party origin is
`https://party.avrana.net` <span class="avr-badge deployed">Deployed</span>, resolved locally by
the appliance's DNS (see [the appliance and its network](../architecture/appliance-and-network.md)).

**Games get their own origin, eventually.** The target is a separate game origin that holds only
session-scoped tickets, so game JavaScript cannot act as the member. Today games and the arcade
are still served from the Party origin; the mechanisms are in source but not configured.

**Full and Limited Mode.** When trusted HTTPS is unavailable, the Party should keep working in a
visibly degraded Limited Mode with its own credential, rather than weakening the secure cookie.
The captive portal is only a convenience: nothing is chosen, trusted or played inside it.

## Identity in layers

The document's central instruction is: **do not collapse "player" into one object.** It keeps
these concepts apart, each with its own random, opaque identifier:

| Concept | Meaning | State |
|---|---|---|
| Party | The persistent unit people join. Exactly one per appliance. | <span class="avr-badge deployed">Deployed</span>, memory only |
| Device | A recognized browser, via a server-issued random cookie whose hash is stored | <span class="avr-badge deployed">Deployed</span> |
| Presence (member) | A device's participation in the Party | <span class="avr-badge deployed">Deployed</span> |
| Seat | A temporary binding of a presence to a slot in one game session | Game-owned; arcade seats <span class="avr-badge source">In source</span> |
| Game session | One launch of one game | <span class="avr-badge deployed">Deployed</span> |
| Role | Host, player, spectator; Admin for the appliance | Host, player, spectator <span class="avr-badge deployed">Deployed</span>; Admin <span class="avr-badge planned">Planned</span> |
| Profile | The optional, durable, server-side person record | <span class="avr-badge planned">Planned</span> |
| Guest, persona, team, device trust | A person without a profile; a nickname for tonight or one game; a named group; a device allowed to pick a profile without its PIN | <span class="avr-badge planned">Planned</span> |

The identifiers map to one another but are never the same value, and none of them authorizes
anything on its own: only a credential checked by the server does, and names never do. A game
sees only a secret key scoped to one session and one participant, plus a name to display.

The document separates **live identity** (device, presence, seat: who is here tonight) from
**durable identity** (a profile: who someone is across nights). The name and avatar a phone
uses today are stored in that phone's browser and are display values, not a profile. Until a
real Profile exists, nothing persistent is stored about a person.

A proposed state-model review (2026-09-26) adds a principle worth knowing: **store facts, derive
roles.** "Player" and "spectator" are derived from whether a presence holds a seat; a unique
role like host is a pointer on the Party; appliance roles bind to admin sessions, never to a
presence. It also proposes treating a TV as a *public surface with no presence*, so it can never
become host, hold a seat or vote. None of this is built beyond the host pointer.

## Guests and saved profiles

<span class="avr-badge planned">Planned</span> Everything in this section is design. Its
prerequisite, a server-side Profile, does not exist.

Joining never needs a profile. Guests get default names (Player 1, Player 2) and can rename
immediately. Later, a guest could be offered "Save Player" (never "Create Account"), carrying
their history with it. A recognized phone would greet people with a short picker ("Welcome back:
Cody, Audrey, someone else, guest"). A **player PIN is optional**; without one, picking a
profile runs on the honour system and the interface says so. The **System Admin PIN is
required**. Device recognition uses only the random server-issued token, never MAC addresses or
fingerprinting. The proposal also sketches a profile lifecycle, from guest promotion to
deletion, merging and QR pairing, and the categories of per-player settings.

## Admin and host are separate

The document keeps two kinds of authority entirely apart, and a host can never escalate to admin:

| | System Admin | Party Host |
|---|---|---|
| What it is | A persistent, privileged identity for the appliance | A temporary, disposable role inside one party |
| Credential | A required PIN; in v0, an SSH command-line tool | None |
| Powers | Network, updates, storage, installing and trusting games, profile management, moderation defaults | Choosing and starting games, ending rounds, managing spectators and seats, moderating party chat, kicking from the current party |
| Cannot | — | Touch profiles, devices, PINs, installation or admin settings; see other players' hidden state |
| State | <span class="avr-badge planned">Planned</span>; no Admin role exists in code | The role, game selection, Start, End and hand-over <span class="avr-badge deployed">Deployed</span>; seat management, chat moderation, votes and kicks are design |

**The host is disposable.** If the host goes quiet, the role passes to someone else after a
grace period, and a returning former host does not get it back; there is no "claim host"
action. Party Core implements this, picking the earliest-joined member who is still present (in
source, preferring a Full Mode member). See [the lifecycle page](party-lifecycle.md#the-host).

**Moderation presets.** <span class="avr-badge planned">Planned</span> Moderation is meant to be
configurable by the admin rather than hard-coded, with an optional preset pair instead of an
enterprise role system:

- **Friends / Private party** (the default). The Wi-Fi password is the only gate. In this mode
  being able to reach the Party on the appliance's network is, deliberately, the practical root
  of admission. This also holds in Limited Mode.
- **Public / Demo party** (a future, distinct mode). New arrivals would wait for host admission,
  optionally with a short party code in the QR link, and the admin would choose the first host.
  It would not bring back a Join ceremony for normal parties.

A **kick is not a ban**. It removes a presence from this party and says so publicly, but a
private browser tab is a new device, so only the Wi-Fi password or Public-mode admission keeps
someone out.

## Party Home and synchronized navigation

<span class="avr-badge source">In source</span> · <span class="avr-badge reported">Owner-reported</span>
for the console model described here. What the last verified deployment (2026-09-29) has is
host-moved navigation and a Play-or-Watch setup shown on the game's own page.

Party Core exposes a single authoritative **location** (home, setup, game or results) that only
the host moves, and every Party page, game page and the arcade page moves itself there on load,
on reconnect and on every change, with no detour prompts or Rejoin offers. Party Home at
`/party/` holds the roster, catalogue, Party Chat, the library and the full-screen setup scene.
The location is singular by design: one appliance, one party, one activity. The details are on
[The Party](../architecture/party.md) and in the [lifecycle design](party-lifecycle.md).

## Seats, spectators and teams

These are design requirements, not a claim of a complete platform seat layer. BLUFF keeps its own
session identity; the arcade's controller reservations (stable slots, neutral input on
disconnect, a 60-second grace, explicit release) are
<span class="avr-badge source">In source</span>.

- **Seats** survive a disconnect: input goes neutral, the slot stays reserved, and the owner
  reclaims it on return. A disconnected seat is never "free"; only a released seat can be
  refilled, and a refill gets a new id and key.
- **Spectators** are a first-class role, not a failed player. The server rejects their input.
- **Teams** <span class="avr-badge planned">Planned</span> would live above any single game, so
  a party score could span several games. The rule is: never fake a team result in a game that
  has no teams.

## The social layer

<span class="avr-badge planned">Planned</span>, apart from today's Party Chat (which still runs on
the retiring LAN Games chat service).

- **Chat channels**: party, team, whispers, game-defined channels, and server-only **system
  events** ("SYSTEM: Audrey is now Host"). System events are a separate message type in their own
  element, and the name rule means no player can be named to look like one.
- **Private player panels**: hidden roles, cards and prompts on each phone. Private data is
  filtered on the server, never hidden with CSS.
- **Queue and voting**: anyone nominates, the party votes, **the host decides**. Votes belong to
  a presence, so a refresh or a second tab never adds one.

## Stats, achievements and history

<span class="avr-badge planned">Planned</span>, except where marked.

Every stat would carry its **provenance**: reported by the game, observed by the platform, or
entered by a person. Emulated games produce no results unless a per-title adapter can observe
them honestly, and **participation is never a win**. Achievements would only come from stats
whose provenance supports them, with no monetization.

The Party is to be the only writer of persistent results. The document's own status says the
result format "is not yet designed". That is out of date:
[ADR 0015](../decisions/0015-game-result-envelope.md) defined it on 2026-10-03, and Party Core
now checks a completed game's structured result and keeps it on the session
<span class="avr-badge source">In source</span>. Nothing is persisted yet: there is no history or
stats store.

## Games and the platform

A game meets the platform through three separate things: **capabilities** (what the game is),
a **runtime request** (how its code runs) and a **grant** (what the appliance allows). It joins
a party through optional pieces such as a ticket handshake, a result report and the shared
navigation follower. The full picture is on [How games integrate](../games/index.md).

The target is that each native game is an isolated process with its own service identity and
secrets, reached through generic routing from a game registry and served from the game origin,
with no game-specific logic in Party Core. Today BLUFF and EXPO still run inside the LAN Games
fork's single process on the Party origin. The platform aims to prove three kinds of game: native
party games with no TV, native action games, and emulated multiplayer with
[Personal Viewports](../games/execution-models.md#playstation-profiles-and-personal-viewports).

## A proportionate security model

The threats considered are mischievous guests on the same Wi-Fi (impersonation, spoiled stats,
double voting, grabbing the host role), cookie sniffing on a shared-password network, other web
pages on a phone that also has mobile data, and, once open installation exists, a malicious or
buggy game. Anyone with SSH or SD-card access is an admin by design. The wider picture is on
[Trust boundaries](../architecture/trust-boundaries.md).

The model's main commitments:

- **Transport.** The canonical Party is TLS-protected. Plain HTTP remains an accepted legacy
  risk that must not be extended to HTTPS credentials or hidden game state. The Wi-Fi must not be
  open.
- **Device token.** Random, server-issued, `HttpOnly`, stored only as a hash, revocable by
  deletion. It never grants admin.
- **Requests.** Host names are allowlisted (which also defeats DNS rebinding, a trick that makes a malicious name point at the appliance), `Origin` is checked
  on every state-changing request, a GET never changes anything, and authorization comes only from
  identifiers the server resolved.
- **Names** are display values only, normalized, limited to 1–16 characters and one alphabet, and
  never a reserved word such as SYSTEM, Admin or Host
  <span class="avr-badge source">In source</span>.
- **Admin, later.** v0 has no web admin at all, so there is nothing for a guest to brute-force. A
  later web admin would run on its own origin with a required PIN of at least six digits and a
  short backoff capped so a guest cannot lock the owner out all night.

The document is candid about **honest limits**. Device tokens are free, so a kick is not a ban
and one person can stuff a vote; votes therefore stay advisory and the host decides. Built-in
games are not isolated from each other today because the LAN Games fork is one process, and every
service on the appliance shares one Unix user, so file modes do not separate them;
[ADR 0016](../decisions/0016-service-identities-and-local-trust-boundary.md) defines the boundary
that will.

One statement in this section is older than the code. The device cookie is described as scoped
to `/party/` with nginx stripping cookies from game locations; in source the cookie is now
`__Host-avrana_device` with `Path=/`, and no such nginx directive exists (see
[Known discrepancies](../status/discrepancies.md#1-the-device-cookie-and-same-origin-game-servers)).

Untrusted community games would later get a stronger, sandboxed tier on top of the origin
split. The document also lists what it deliberately does *not* do, including private certificate
authorities on phones, JWTs (signed web login tokens), encrypted databases, device fingerprinting and CAPTCHAs.

## Open questions

The document keeps a list of questions that are still open. The main ones are:

- whether a party survives an appliance reboot;
- what `/` should become and what the QR code carries (Limited Mode's doorway answers part of
  this);
- the trust model for third-party games beyond the origin split and process isolation;
- the `.avrgame` package format, deliberately unfrozen until Checkers and Spades prove the
  boundary;
- how chat and avatars leave the LAN Games code they still depend on;
- the onboarding path across iOS and Android, which needs real-phone tests;
- smaller policy points such as spectator voting, whether a kick ever reaches beyond the current
  party, a TV "screen" presence, and host-less kiosk parties.

Several further ideas are explicitly experimental and outside the product plan: phones forming
one distributed display, a companion app (only ever for onboarding or hardware conveniences),
Bluetooth discovery, optional upstream internet (the party must never depend on it), automatic
Personal Viewport detection, and per-title result adapters for emulated games.
