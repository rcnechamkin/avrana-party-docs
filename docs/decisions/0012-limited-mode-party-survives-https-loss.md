---
title: "ADR 0012: Limited Mode"
description: Why the Party must keep working when trusted HTTPS fails, and how Limited Mode, a plain-HTTP form of the same Party, provides that.
sources:
  - avrana-party:docs/adr/0012-limited-mode-party-survives-https-loss.md
  - avrana-party:docs/design/LIMITED-MODE.md
  - avrana-party:avrana/party/identity.py
  - avrana-party:avrana/party/service.py
  - avrana-party:avrana/party/core.py
  - avrana-party:web/party/doorway/index.html
  - avrana-party:avrana-party.nginx
  - avrana-party:deploy/party-core/party-core.example.json
verified: 2026-10-09
---

# ADR 0012: The Party survives the loss of trusted HTTPS

!!! abstract "At a glance"
    **Decided:** 2026-10-02, mechanisms 2026-10-03 · **Status:** <span class="avr-badge accepted">Accepted direction</span>; rollout steps 1–2 <span class="avr-badge source">In source</span>; not deployed or switched on
    If a phone cannot reach the Party over trusted HTTPS, it still gets the Party over plain HTTP,
    in a clearly labelled **Limited Mode**. Only features that truly need a secure connection are
    lost, and only for that phone.

## The problem

[ADR 0004](0004-full-mode-contracts-and-providers.md) made `https://party.avrana.net` the
canonical address and served the Party page over HTTPS only. The device cookie is marked
`Secure`, so a phone's Party identity exists only there. If HTTPS failed, the only fallback was a
link to the old LAN Games hub.

But the appliance is meant to run offline for weeks, and its public certificate needs an internet
connection to renew. HTTPS also fails when a phone's private DNS overrides the local name, or a
browser rejects the chain. A 2026-10-02 architecture review concluded that making trusted HTTPS
a hard requirement contradicts the product's principles: offline-first, no app, no internet.

Some features genuinely need a *secure context*, meaning a page the browser treats as
trustworthy: screen wake lock, the service worker and offline copy, `crypto.subtle`, camera and
microphone, warning-free WebRTC, and the `Secure` cookie itself.

## What was decided

- **Two modes, one Party.** *Full Mode* is the Party over trusted HTTPS, the default. *Limited
  Mode* is the same Party when trusted HTTPS is unavailable. These are names for a capability
  state, not separate code or separate parties.
- **Losing HTTPS must not disable the Party.** As far as browsers allow, membership, presence,
  the host and succession, synchronized navigation, and choosing, launching and playing
  compatible games keep working, on phones alone.
- **Features degrade per feature and per phone.** Wake lock, the offline copy, secure-context APIs
  and games that require a secure context are explained or unavailable *for that phone*. One weak
  phone never downgrades the Party.
- **Limited Mode is honest.** It says the connection is not secure, what is missing and how Full
  Mode returns. It never hides the browser's warning.
- **Identity needs its own model**, because the `Secure` cookie is not sent over HTTP. The
  existing cookie is never weakened, Limited Mode gets a distinct server-issued credential,
  continuity across modes is a goal rather than a guarantee, and Limited Mode never grants
  elevated authority.

## Why this way

Rejected alternatives:

- **Dropping `Secure` from the device cookie** would expose the long-lived credential to anyone
  on the Wi-Fi and merge two origins into one cookie jar by accident.
- **A private certificate authority on phones** was already rejected by ADR 0004 and the
  no-setup principle.
- **An HTTP-only Party** would throw away Full Mode's real value.
- **An app as the recovery route** may add convenience but cannot be the baseline.

## What it means in practice

This replaces one consequence of ADR 0004: that HTTP is no recovery path and the LAN Games hub
is the fallback. The rest stands: the Party lives at `https://party.avrana.net/party/`, the TLS
key stays on the appliance, and there is no HSTS (the header that forces browsers onto HTTPS).
No HSTS now matters more, because it is what lets a phone escape an expired certificate into
Limited Mode. The offline copy remains a convenience; Limited Mode is the recovery mechanism.

## Later changes

On 2026-10-03 the owner accepted six mechanisms from the
[Limited Mode design](../design/limited-mode.md):

| | Decision |
|---|---|
| D1 | `http://10.42.0.1`, the appliance's own address, is the canonical Limited Mode address: the only name that survives private DNS, a VPN or Private Relay. |
| D2 | Party Core knows a request is Limited because it arrived on a second local listener, not from a header. |
| D3 | A phone that changes mode joins again **as a new device**, with a separate `avrana_limited` credential: not `Secure`, 12 hours, kept only in Party Core's memory so a restart forgets it, accepted only on the Limited listener. A host-approved "That's me" reclaim may come later. |
| D4 | Mixed parties are allowed and each member's mode is visible. In host succession a present Full Mode member is preferred; a present host is never displaced. |
| D5 | In Limited Mode, first-party games use the Party's own origin; there is no game origin or community tier there. |
| D6 | `/` on port 80 becomes a **doorway** that opens Full Mode if the secure address answers on that phone, and Limited Mode if not. |

A Limited member has ordinary Party rights, including the host role, but there is no PIN entry
or profile claiming. The amendment states the costs openly. On a shared-password Wi-Fi another
guest can read a Limited credential off the air and act as that member, which is why it is
short-lived and the banner says the connection is not private. The 12 hours are not renewed by
use, so a phone still present afterwards rejoins as a new member. Browsers label where a request came from with two headers, `Origin` and `Sec-Fetch-Site`. Over
plain HTTP they do not send `Sec-Fetch-Site`, so there Party Core stops requests from other sites
with its `Origin` allow-list alone. And game pages follow the Party only in a secure context, so in Limited Mode a
game page does not yet follow the Party.

## Where it stands today

<span class="avr-badge source">In source</span> (rollout steps 1–2), not deployed. Party Core
has the separate Limited credential store, an optional second listener, a mode on every member
and view, and D4 succession. The shell has the Limited banner, each member's mode in the roster,
per-phone limits in a round's setup, and the doorway page.

Deploying this code would change little visibly: views gain `"mode": "full"`, and with everyone
in Full Mode succession behaves as before. Nothing switches Limited Mode on. The configuration
has no `limited` object, so no second listener runs. The repository's port-80 nginx server has
no Limited locations, and its `/` is a plain link to the Party, not yet the doorway.

Owner-only steps remain: the nginx locations and deployed configuration (step 3), then real-phone
tests with an expired certificate, a wrong clock, Android Private DNS and iCloud Private Relay
(step 4). **Until step 4 passes, Limited Mode is not a recovery path to rely on.** Still open:
what the QR code carries, and host-approved reclaim.

## Related decisions

- [ADR 0004: Full Mode, contracts and providers](0004-full-mode-contracts-and-providers.md), whose HTTPS-only consequence this replaces
- [ADR 0006: the session protocol](0006-party-session-protocol.md), which defined the device cookie
- [ADR 0013: separate browser origins](0013-party-and-game-browser-origins.md)
- [ADR 0014: native games, LAN Games retired](0014-native-games-isolated-lan-games-retired.md)
- [Limited Mode design](../design/limited-mode.md) and [the appliance and network](../architecture/appliance-and-network.md)
