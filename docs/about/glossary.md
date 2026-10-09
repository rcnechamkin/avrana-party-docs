---
title: Glossary
description: Avrana Party terms in plain language.
sources:
  - avrana-party:docs/adr/0002-party-platform.md
  - avrana-party:docs/adr/0003-ids-and-keys.md
  - avrana-party:docs/adr/0006-party-session-protocol.md
  - avrana-party:docs/adr/0011-party-console-model.md
  - avrana-party:docs/adr/0012-limited-mode-party-survives-https-loss.md
  - avrana-party:docs/design/PARTY-PLATFORM.md
verified: 2026-10-09
---

# Glossary

Abandoned
:   A session outcome meaning the game, or its managed runtime, gave up. Unlike *completed*,
    there are no held results: the Party goes straight home.

ADR (Architecture Decision Record)
:   A dated record of an architectural decision, in the Party repository's `docs/adr/`. See
    [Decision records in brief](../decisions/index.md).

Admin (System Admin)
:   A planned, PIN-protected role that would administer the appliance itself. It is deliberately
    distinct from *Host*. Design only.

Appliance
:   The physical Avrana Party box: today a Raspberry Pi 4 with its own Wi-Fi network.

Appliance grant
:   The appliance's decision about an installed game: its entry point, trust tier and granted
    permissions. A game requests; the appliance grants.

AVR-N
:   An issue identifier in the project's Linear workspace (team `AVR`), for example AVR-238.
    Branches and pull requests that implement an issue carry it in their names.

Arcade
:   The service that runs an emulator on the appliance and streams its video to phones, which
    act as gamepads.

BLUFF
:   The first Avrana-native game: a server-authoritative, hidden-role bluffing card game for
    two to six players.

Bridge
:   The planned Party-owned frame and `postMessage` protocol (`avrana.party-bridge/v1`) through
    which a game page on its own origin can ask the Party for a ticket or perform host actions.
    In source; not configured.

Checkers
:   The first game being built entirely outside the LAN Games runtime, as an isolated native game
    process, to prove the boundary.

Classics
:   The project's name for possible future adaptations of individual LAN Games titles onto the
    native-game boundary, chosen one at a time.

Console model
:   The design ([ADR 0011](../decisions/0011-party-console-model.md))
    in which presence is automatic, the Party has one authoritative location, and only the host
    moves it.

Device
:   A recognized browser, identified by a server-issued cookie. Not a person.

Doorway
:   In the Limited Mode design, a small plain-HTTP start page. It checks whether trusted HTTPS
    works and sends the phone to Full Mode or Limited Mode accordingly. In source; not deployed.

EXPO
:   An Avrana adaptation of a cooperative trick-taking game, in the Games repository, with its
    own Linear project.

Full Mode
:   The Party reached over trusted HTTPS at `https://party.avrana.net`. The default and preferred
    experience.

Game contract
:   A game's JSON description (`avrana.game/v0`): what it is, its player counts, how it is
    presented and what it needs. Intended to become the one canonical per-game manifest.

Game token
:   A per-session, per-participant secret derived by the platform. A game uses it internally as
    a player's key. It is stable across reconnects within one session.

Gaze avatar
:   One of the bundled, illustrated avatars a player picks in Party Home. It is a display value,
    not an identity.

Host
:   The member who picks games and moves the Party. A role checked by the server, not a
    credential. It passes automatically to someone else if the host goes away.

LAN Games
:   An MIT-licensed, self-hosted browser game hub by BEACNpool, retired upstream in September
    2026. Avrana's fork of it is the current game runtime and is itself retiring as a runtime.

Limited Mode
:   The same Party reached over plain HTTP when trusted HTTPS is unavailable, with
    secure-context features explained or unavailable. Accepted direction; partly in source;
    not deployed.

Location
:   Where the Party is: `home`, `setup`, `game` or `results`, plus which game and session. There
    is exactly one, and every phone follows it.

Member
:   A device's membership in the current Party, with a display name and avatar. The engineering
    documents also call this a *presence*.

Native game
:   A game written for Avrana: browser clients on each phone, an authoritative server on the
    appliance, Party integration from the start.

Participant
:   A person's identity inside one game session: a random id issued for that session only. It is
    the only name a game has for a person.

Party
:   The people present, the host, and where everyone should be. It outlasts any single game.
    "The game may change; the party does not."

Party Core
:   The Python service on the appliance that holds membership, the host role, the location and
    the current game session.

Party Home
:   The web app every phone opens at `/party/`.

Personal Viewport
:   A planned way of showing each phone its own player's part of a shared or split-screen game.
    Experimental.

Presentation
:   One way a game can be shown to a seat, such as a native browser table, a shared stream, a
    personal viewport or controller-only. Games list them in order of preference.

Profile
:   A planned, optional, durable person record that history could attach to. It does not exist
    yet. A name and avatar stored in the browser are not a Profile.

Provider
:   A component that supplies a runtime, input or presentation capability, such as RetroArch, a
    virtual gamepad or a shared video stream.

Result envelope
:   The small, versioned structure (`avrana.game-result/v1`) in which a game reports how a
    session finished.

Secure context
:   A browser's term for a page loaded over trusted HTTPS (or from `localhost`). Features such
    as screen wake lock, service workers and `Secure` cookies are available only there.

Seat
:   A place in a specific game, such as a controller slot. Spectators have no seat.

Session
:   One launch of one game inside the Party.

Session protocol
:   `avrana.party-session/v0`: the signed messages between Party Core and a game (launch, end,
    ended) and the tickets that admit players.

Stand-in game
:   A test-only native game used to prove the native-game path in CI. Never installed on a
    product appliance.

Standard Mode
:   The consumer configuration: one appliance, one Party, one active activity at a time.

Ticket
:   A short-lived (at most 120 s), single-use, signed capability saying that this connection is
    participant P, with role R, in session S of game G. Presented as the first WebSocket
    message.

Tier 1 / Tier 2 / Tier 3
:   Evidence grades: pure tests, a simulated Party on localhost, and real hardware with real
    phones. See [Reading the specifications](../developers/reading-the-specs.md#evidence-tiers).
