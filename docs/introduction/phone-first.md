---
title: Why phones, and only phones
description: How Avrana Party works without a television, without the internet and without an app, and what each of those choices costs.
sources:
  - avrana-party:docs/adr/0002-party-platform.md
  - avrana-party:docs/adr/0004-full-mode-contracts-and-providers.md
  - avrana-party:docs/adr/0012-limited-mode-party-survives-https-loss.md
  - avrana-party:docs/design/NATIVE-GAMES.md
  - avrana-party:docs/runbooks/party-https.md
  - avrana-party:docs/runbooks/network.md
  - avrana-party:avrana-captive.conf
verified: 2026-10-09
---

# Why phones, and only phones

Avrana Party starts from one observation. Everyone at a gathering already carries a capable
computer with a touchscreen, a speaker, a vibration motor and a modern web browser. If the game
can use those phones well, nothing else is needed. This page explains the three things the
project chooses to do without, how each works in practice and what each costs.

## No television required

A shared TV makes some games better and most party setups harder. Someone has to find the
input, borrow a cable and arrange the room around the screen, and a TV is useless on a camping
trip anyway. So the product baseline is **phones alone**, and a TV is at most an extra public
viewer.

This changes what a game can be. The project's design guidance for native games
(see [Designing for phones](../games/designing-for-phones.md))
puts it this way: *the phone is not just a controller.* Each phone is a private, dynamic
surface. It can hold a secret hand of cards, a hidden role, a private objective, a drawing
canvas, a ballot or a map only you can see. The question every Avrana-native game is supposed
to start from is:

> What can this player's private touchscreen do that a normal shared-screen game cannot?

BLUFF, the first native game, is the example. Each player's two hidden cards exist only on
their own phone. The server sends every phone a view filtered for that viewer, so another
player's hand never reaches your browser at all.

Every game declares how it relates to a screen: `no_tv_needed`, `tv_optional` or
`tv_required`. Today BLUFF and EXPO are `no_tv_needed`. The *Gauntlet II* arcade is
`tv_optional`, because its shared video can be streamed to every phone.

## No internet required

The appliance runs its own Wi-Fi access point, hands out addresses and answers DNS for the
phones that join. Every game server runs on the box. Once a phone is on the Party network,
nothing it needs is anywhere else.

The interesting problem is **HTTPS**. Modern browsers reserve many features for secure
contexts: screen wake lock, service workers, some cryptography APIs, warning-free WebRTC and
`Secure` cookies. An offline box normally cannot give phones a certificate they trust without
installing a private certificate authority on every phone, and that would mean an app or a
configuration profile.

Avrana Party solves this with a real domain and a real certificate. On the Party network, the
appliance's own DNS answers `party.avrana.net` with the box's address, and the box holds a
normal publicly trusted certificate for that name. Phones validate it offline, with no warning,
no app and no configuration.
[Trusted HTTPS with no internet](../architecture/appliance-and-network.md#trusted-https-with-no-internet)
explains how this works.

The catch is renewal: the certificate lasts 90 days, renewing it needs a brief internet
connection, and renewal is manual today. The project accepted that losing the certificate must
not end the Party: see
[Full Mode and Limited Mode](../architecture/appliance-and-network.md#full-mode-and-limited-mode).

## No app required

Everything a player touches is a web page. There is no app to install and no store review,
nothing to keep updated on each phone, and no difference between the iPhone and the Android
in someone's pocket beyond what their browsers support.

The project is equally deliberate about **captive portals**, the sign-in pages that pop up
when you join hotel Wi-Fi. They sound convenient, but the mini-browser they open has limited
storage and odd behaviour, and it closes as soon as the user taps away. So the appliance
answers Apple's connectivity probe with the "Success" page Apple expects, and iPhones join
quietly. Players then open the Party address in their real browser. The onboarding design
treats QR codes, NFC tags or a small e-ink display showing the Wi-Fi details and address as
possible conveniences around that, never replacements for it.

A native companion app is listed among long-term possibilities, mainly as a recovery and
convenience path. The roadmap is explicit that an app must never become the baseline.

## What the phone-first choice costs

These choices have real costs, and the engineering documents spend a lot of effort on them:

- **Browsers differ, and phones sleep.** A locked phone drops its connection, and Safari
  evicts storage after about a week of non-use. Much of Party Core's design (presence windows,
  host grace periods, reconnect tickets, the single authoritative location) exists so that a
  phone waking up from a pocket lands in the right place.
- **Capabilities vary per phone.** The platform evaluates what each phone can do (WebRTC,
  wake lock, video decoding) for that player alone. A weak phone gets a fallback, such as
  watching instead of playing, or a plain explanation. It never drags the whole Party down to
  the weakest device.
- **The appliance is small.** A Raspberry Pi 4 has to run the network, the web front door,
  Party Core, the game servers and sometimes an emulator with a video encoder. Its power
  budget and CPU shape the architecture.
- **Testing is hard.** A browser emulating a phone on a laptop proves much less than a real
  iPhone on the Party Wi-Fi. The project treats real-phone evidence as a separate, higher
  [tier of evidence](../developers/reading-the-specs.md#evidence-tiers) and does not claim it
  from simulations.

Next: [what exists, and what is planned](today-and-vision.md).
