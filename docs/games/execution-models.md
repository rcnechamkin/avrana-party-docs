---
title: Execution models
description: The kinds of game Avrana Party can run (LAN Games modules, isolated native processes, streamed emulation, Personal Viewports) and the maturity of each.
sources:
  - avrana-party:docs/adr/0005-lan-games-provider-launch.md
  - avrana-party:docs/adr/0009-arcade-party-provider.md
  - avrana-party:docs/adr/0014-native-games-isolated-lan-games-retired.md
  - avrana-party:docs/design/PERSONAL-VIEWPORTS.md
  - avrana-party:docs/GAME-PLATFORM-ARCHITECTURE.md
  - avrana-party:avrana/contracts/game.py
  - avrana-party:contracts/appliances/avrana-pi4.json
  - avrana-party:arcade/README.md
  - avrana-party:ps1/README.md
  - avrana-party:avrana/games/standin
  - avrana-party-games:README.md
  - avrana-party-games:games/registry.py
verified: 2026-10-09
---

# Execution models

"A game" can mean very different things on this appliance. Some games are rules on a server
with a web page on each phone. Others are 1990s console games running in an emulator, with
video streamed to everyone. The platform treats these as different **execution models** behind
the same Party contract, so that the Party flow is identical whatever runs underneath.

| Model | Example | Status |
|---|---|---|
| Browser game inside the LAN Games fork | BLUFF, EXPO | <span class="avr-badge deployed">Deployed</span> · <span class="avr-badge retiring">Retiring</span> |
| Isolated native game process | Stand-in test game; Checkers next | <span class="avr-badge source">In source</span>, no product game yet |
| Streamed emulation (shared picture) | *Gauntlet II* | <span class="avr-badge deployed">Deployed</span> |
| Emulation profiles for PlayStation titles | *Bomberman*, *Worms* | <span class="avr-badge experimental">Experimental</span> |
| Personal Viewports | Per-player crops of a split-screen game | <span class="avr-badge experimental">Experimental</span> |
| App-native or TV-rendered games | — | <span class="avr-badge planned">Planned</span> as concepts only |

## The LAN Games fork

<span class="avr-badge deployed">Deployed</span> · <span class="avr-badge retiring">Retiring</span>

The project's first game runtime is a fork of **LAN Games**, an MIT-licensed, self-hosted
browser game hub by BEACNpool whose upstream was retired in September 2026. It is a single
Python web server with a shared game-session framework, about thirty games, bots, chat and
avatars. It was adopted as a deliberately cheap starting point, and it worked. It is where
**BLUFF** was built, and where **EXPO** lives: an Avrana adaptation of a cooperative
trick-taking game, which has its own Linear project.

The fork is bridged to the Party by the session protocol. When the Party launches BLUFF, the
fork receives the signed launch, admits phones only with Party tickets and reports the end and
the result back to Party Core.

In October 2026 the project decided
([ADR 0014](../decisions/0014-native-games-isolated-lan-games-retired.md))
that this runtime must not become the platform by default. One process held every game and
every game's keys. Its standalone mode trusted a token any browser could forge. Game-specific
logic had crept into its shared core. So the fork is now **legacy and donor code**:

- In source, standalone LAN Games play and the hub page are retired. nginx routes only BLUFF
  and EXPO to the fork.
- New native games must not be built as LAN Games modules.
- The other titles remain as reference material for possible future "Classics" adaptations
  onto the native boundary.
- BLUFF still runs inside the fork, and will until it moves.

## Isolated native game processes

<span class="avr-badge source">In source</span> · not deployed · no product game yet

This is the target model for every Avrana-native game. Each game is **its own process**, run
from a shared systemd unit template (`avrana-game@<slug>`) with its own dynamically allocated
Unix user. It receives its own signing key from systemd and has its own state directory. It
serves HTTP and WebSockets on its own Unix socket. A generic nginx rule routes
`/games/<slug>/` to that socket. Party Core finds the game through a registry directory that it
reloads without restarting. A single provisioning command creates the key, the registry entry
and the unit configuration from the appliance's grant for that game.

The machinery is in the Party repository and has been exercised end to end on a CI runner with
real systemd, using a **test-only stand-in game**. The stand-in's own description says it must
never be installed on a product appliance. No product game uses this path yet, and the
provisioning runbook is labelled as a proposed procedure that has not been run on the
appliance. **Checkers** is being built as the first real game on this boundary, and is in
review as of October 2026. The [native games page](native-games.md) explains the plan in detail.

## Streamed emulation: the arcade

<span class="avr-badge deployed">Deployed</span>

Some games cannot run in a phone's browser: anything that needs an emulator, for a start. For
these, the appliance runs the game itself and streams it:

1. **RetroArch** runs the game inside a virtual X display.
2. The display and a private audio sink are captured. The video is encoded **once** in the Pi's
   hardware H.264 encoder (640×480 at 60 fps, with a 2.5 Mbit/s target bitrate), and the audio
   as Opus.
3. That single encoded stream is sent to each phone over its own **WebRTC** connection. No STUN
   or TURN server is needed on a local network.
4. Each phone's controller page sends its gamepad state over a WebSocket 20 times a second.
   The appliance feeds it into a virtual Linux gamepad. Held buttons are released automatically
   if a phone stops sending.

Encoding once and fanning the stream out keeps the cost per viewer low on a Raspberry Pi. The
trade-off is that every phone sees the same picture.

*Gauntlet II* is the working example. Two iPhones played it together in September 2026. Since
[ADR 0009](../decisions/0009-arcade-party-provider.md)
the emulator and encoder run only while the Party has an arcade session. In that deployment,
any phone on the arcade page can take a free controller. Admitting phones with Party tickets,
four controller seats, seat reservations that survive a short disconnect and a redesigned
controller page are
<span class="avr-badge source">In source</span>. Four real phones have not been run together
yet, and input-to-screen latency has never been measured.

The arcade's emulator core is licensed for non-commercial use only. The engineering notes
record it as a choice for the private prototype.

## PlayStation profiles and Personal Viewports

<span class="avr-badge experimental">Experimental</span>

The roadmap names **emulated multiplayer** as one of the three things the platform should
eventually demonstrate. PlayStation party games such as *Bomberman* and *Worms* are the test
cases, with game files supplied legally by the owner.

On `main`, this exists only as **data and checks**: title profiles, a provider module that
generates configuration and input mappings, and catalog entries marked experimental. The
README says that nothing there launches an emulator. A working streamer exists on a parked
research branch. A bounded experiment in September 2026 measured it on the Pi. It ran a
four-slot *Bomberman* to simulated phones, but CPU was the limit: about 21–44 emulated frames
per second with the arcade running beside it. On a real iPhone it had latency stalls, with a
99th-percentile input round trip of 1.4 seconds.

**Personal Viewports** are the more ambitious idea. In a split-screen game, each phone would
show only its own player's quarter of the screen, enlarged, instead of the whole frame. The
design treats a viewport as a method with several possible implementations: cropping one
shared stream on the phone, separate encoded streams, or a renderer in the browser. Only the
crop approach has been tried, and it missed its frame-rate target. The design's own rule is
that a manual proof on real phones must come before any automatic detection or per-title
result adapters.

## App-native and TV-rendered games

<span class="avr-badge planned">Planned</span>, as concepts only

The game contract can already *describe* an `app_native` presentation, and the architecture
documents discuss a future companion app and an optional HDMI "TV mode". Neither exists. The
roadmap is explicit that an app or a TV must never become a requirement for the platform as a
whole.

## How the platform chooses

Each game declares, in its contract, an **ordered list of presentations**, each with the device
and appliance capabilities it needs. For each seat, the Party evaluates what that phone can
actually do and picks the first presentation that fits. If none fits, it picks the game's
fallback, such as watching instead of playing. Capabilities are reported as `yes`, `no`,
`partial` or `unknown`, and **`unknown` is never treated as `no`**. A weak phone changes only its
own seat. The Party never drops to the lowest common denominator. The report is advisory, for
the interface, and never used to authorize anything.
