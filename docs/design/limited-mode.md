---
title: Limited Mode
description: "How the Party is meant to keep working when trusted HTTPS fails: the failure cases, the doorway page, the separate Limited Mode credential, what is built, and the wider offline-trust direction."
sources:
  - avrana-party:docs/design/LIMITED-MODE.md
  - avrana-party:docs/OFFLINE-TRUST-AND-RECOVERY.md
  - avrana-party:docs/adr/0012-limited-mode-party-survives-https-loss.md
  - avrana-party:avrana/party/identity.py
  - avrana-party:avrana/party/service.py
  - avrana-party:avrana/party/core.py
  - avrana-party:web/party/doorway/index.html
  - avrana-party:web/party/lib/doorway.js
  - avrana-party:web/party/lib/limited.js
  - avrana-party:web/party/app.js
verified: 2026-10-09
---

# Limited Mode

!!! abstract "In short"
    How the Party is meant to keep working when a phone cannot reach it over trusted HTTPS: the
    mechanism behind [ADR 0012](../decisions/0012-limited-mode-party-survives-https-loss.md).

    **Where it stands:** the owner accepted the design (decisions D1 to D6 of the engineering
    document LIMITED-MODE) on 2026-10-03. Of its four rollout steps, the first two (Party Core
    and the shell) are <span class="avr-badge source">In source</span>; the nginx change and
    real-phone tests have not happened, so **nothing is deployed**. This page also draws on
    OFFLINE-TRUST-AND-RECOVERY, a broader and older design-direction document about
    certificates, offline operation and recovery, most of which is unbuilt.

## Why a Party needs a fallback

Avrana Party serves its pages over trusted HTTPS at `https://party.avrana.net`, using a real
public certificate while the traffic stays on the local network (see
[the appliance and its network](../architecture/appliance-and-network.md#full-mode-and-limited-mode)).
HTTPS matters for two separate reasons. It protects traffic, and it gives the page a **secure
context**, which browsers require before they offer features such as service workers, the
offline copy, Screen Wake Lock and many device APIs.

But trusted HTTPS can fail in ordinary ways, and today a phone that hits one of them simply has
no Party. ADR 0012 decided that losing trusted HTTPS must degrade individual features visibly and
must not disable the Party. Full Mode remains the default and the preferred experience; Limited
Mode is the recovery path, not a reason to let the certificate lapse. Certificate renewal stays
required regardless.

## How a phone ends up without trusted HTTPS

The design document lists four causes and what each does to three possible addresses:

| Cause | `https://party.avrana.net` | `http://party.avrana.net` | `http://10.42.0.1` |
|---|---|---|---|
| Certificate expired or not yet valid (the Pi has no battery-backed clock) | browser warning page | works | works |
| Phone uses Private DNS, a VPN or iCloud Private Relay | name does not resolve to the box | does not resolve | works |
| Guest typed the name without `https://` | never tried | works | works |
| Old browser cannot build the certificate chain | warning page | works | works |

Two conclusions follow. A browser's warning page is not Avrana's, so a phone can never be
*redirected* out of broken HTTPS: it has to *start* somewhere that works. And only the appliance's
IP address survives every row, because overriding DNS breaks every name.

## The doorway

The answer is a small page served over plain HTTP that every phone starts from, the **doorway**.
It does one thing. It tries to fetch a tiny file from the HTTPS Party. That request succeeds only
when DNS, the certificate and the phone's clock are all fine. On success the doorway sends the
phone to Full Mode; on failure, or after a short timeout, it sends it to Limited Mode. The QR code
on the box and the captive-portal landing page would both point at the doorway.

<span class="avr-badge source">In source</span> The doorway page exists. Its two destinations
are fixed in the page itself (`https://party.avrana.net/party/` and `http://10.42.0.1/party/`)
and it takes nothing from its own address. The test request carries no credentials and gives up
after 3.5 seconds. It is not yet served: that needs the nginx change, which also has to give the
doorway its own content-security policy so its one cross-origin request is allowed. The Limited
Mode notice links back to it as "Check for the full version". In source, port 80's `/` is an
interim link page; the deployed appliance still serves the LAN Games hub there.

## One canonical Limited Mode origin

Every distinct host name is a separate origin with its own cookies, so three plain-HTTP names
would make one phone look like three devices. The design picks one Limited Mode origin and
redirects the others to it. The choice was between the IP address, which is ugly but survives
every failure, and `http://party.avrana.net`, which reads well but fails exactly when DNS is
overridden. **Decision D1** chose the IP address, `http://10.42.0.1`.

## A separate credential

The Full Mode device cookie is `Secure`, so the browser never sends it over plain HTTP. The
design refuses to weaken it. Instead Limited Mode issues a **second, separate cookie**:

| | Full Mode | Limited Mode |
|---|---|---|
| Cookie | `__Host-avrana_device` (in source) | `avrana_limited` |
| Sent over | HTTPS only | plain HTTP |
| Lifetime | about 400 days | 12 hours, and it dies with a Party Core restart |
| Stored | hashed, on disk | hashed, in memory only |
| Accepted on | the HTTPS listener only | the Limited listener only |

Keeping the Limited credential short-lived and in memory is deliberate. Anything sent over plain
HTTP on a shared-password Wi-Fi can be read by another guest, so the credential should be
worthless the next day. Each store resolves only its own cookie, so neither can be passed off as
the other. The Limited cookie is scoped to `/party/`, so it reaches the Party API and not a game
server on the same address.

## How Party Core knows the mode

Party Core could read the scheme from a proxy header, but its internal routes deliberately
distrust proxy headers. **Decision D2** chose a **second loopback listener** instead: the Full
Mode listener and a Limited Mode listener share one Party, and the mode is a property of the
socket a request arrived on, so it cannot be forged by a header.

<span class="avr-badge source">In source</span> The second listener starts only when Party
Core's configuration has a `limited` section, which production does not set. A Limited origin
that is not plain HTTP, or one shared with Full Mode, is refused at start. The Limited listener
serves no game-to-Party route and no bridge origin. Every view says whether the phone is in
`full` or `limited` mode.

## Identity across a mode switch

The server cannot prove that a plain-HTTP visitor is the same phone as an HTTPS member, because
the `Secure` cookie never travels over HTTP. The document weighs four models:

- **New device.** A Limited visitor joins as a new member and the interface says so. The old
  member drifts to away after 45 seconds.
- **Twin cookie.** Also set the Limited cookie while in Full Mode, mapped to the same device.
  Rejected: it would routinely expose a credential in clear and only works if both modes share a
  host name.
- **Host-approved reclaim.** A Limited member taps "That's me" on an away member and the host
  confirms on their phone, a human check the server cannot fake.
- **Pairing code.** A Full Mode phone shows a code to type. Rejected as useless in the common
  case: when the certificate expires, no phone is in Full Mode.

**Decision D3**: ship "new device" now, add host-approved reclaim later if real parties show
people care, and never use a twin cookie. "New device" is less harsh than it sounds. A
certificate expiry hits every phone at once, and the Party is memory-only anyway, so the
realistic event is everyone rejoining by name in a few seconds.

## Authority and mixed parties

Host actions work in Limited Mode; ADR 0012 requires it. There must be no admin surface, PIN entry
or profile claiming over plain HTTP. None exists yet, so this is a rule for future work. The
document accepts that a guest on the Wi-Fi could read a Limited cookie off the air and act as
that member, including the host, as the platform design already accepts for plain HTTP among
friends.

A party can mix phones in both modes. **Decision D4**: show the mode beside each member, and when
the host role passes by succession, prefer a Full Mode member who is here. A Limited host who is
here is never displaced. <span class="avr-badge source">In source</span> in Party Core.

## What degrades, per phone

The design degrades capabilities one phone at a time, never the whole party.

| Capability | In Limited Mode |
|---|---|
| Joining, presence, host, navigation, setup, launch | work |
| BLUFF and other browser games over plain WebSockets | work |
| Arcade stream | should work, since receiving video needs no secure context; unverified on phones |
| Screen Wake Lock | unavailable; the phone is told to keep its screen on |
| Service worker and the offline copy | unavailable |
| A game whose contract requires a secure context | that phone watches, and is told why |

<span class="avr-badge source">In source</span> The shell's capability checks already treat a
plain-HTTP origin as having no secure context, wake lock or service worker. A notice lists what
is missing on this phone and which installed games it cannot play. In a round's setup, Play is
disabled with the reason beside it, and Watch is always available, so a Limited phone can never
hold up a round. The notice can be folded away for the rest of a visit; a "Limited" mark in the
top bar stays and reopens the same explanation.

Not built yet: in Limited Mode a game page does not follow the Party, because game pages and the
arcade page load the follower only in a secure context. That needs a paired change with the
Games repository.

**Decision D5** covers game origins. Over plain HTTP on an IP address there are no subdomains, so
first-party games stay on the same origin in Limited Mode, and any future untrusted-game tier is
unavailable there (see [Browser origins](browser-origins.md)). **Decision D6**: `/` becomes the
doorway as part of the Limited Mode rollout.

## What the player sees

One notice, in plain words: the connection is not private, what is missing on this phone, and
that the owner restores it by renewing the certificate. It never imitates a padlock and never
hides a browser warning. On Home it appears in full; elsewhere, and once folded, the "Limited"
mark opens a sheet with the same facts.

## Rollout

| Step | What | State |
|---|---|---|
| 1 | Party Core: the Limited store, cookie and listener, behind configuration production does not set | <span class="avr-badge source">In source</span>, tested |
| 2 | Shell: mode in the view, the notice, per-phone degradation, the doorway page | <span class="avr-badge source">In source</span>, tested in a browser with a simulated non-secure origin |
| 3 | nginx: `/party/` and `/party/api/` on port 80, plus the doorway | Not done; an owner-approved live change |
| 4 | Real phones: expired certificate, wrong clock, Private DNS on Android, iCloud Private Relay | Not done |

Step 1 is inert when deployed without the configuration: there is no second listener and no
Limited cookie, and views simply gain `mode: "full"`.

The document explicitly does **not** propose dropping `Secure` from the device cookie, a private
certificate authority, an app as the recovery route, persisting Limited credentials, or any change
to the session protocol. Tickets and game keys do not depend on the browser's scheme.

## The wider offline-trust direction

OFFLINE-TRUST-AND-RECOVERY is an earlier, broader design-direction document, written mainly for
AI agents, and **most of it is not implemented**. Its terminology was reconciled with ADR 0012
on 2026-10-02. Its main ideas:

**Offline is not an error.** The appliance is expected to work without internet. Internet may be
used for certificate renewal and optional updates, but ordinary local play must not depend on it,
and nothing should show an "offline" warning merely because the internet is absent.

**Limited Mode is one specific thing.** It means the Party running without trusted HTTPS. Other
degraded conditions, such as a corrupt game package, a failed update, low storage, a crashing
game or thermal limits, are separate recovery or reduced-capability states, reported per
capability, game or phone. Internally the system should reason about capabilities of the
appliance, of each phone and of each game, never a single global "limited" flag. One weak phone
should not drag the whole party down to its level.

**Certificate identity is not device identity.** The public certificate exists so browsers trust
the page, and it expires. The document proposes a separate, long-lived **device identity** (a
keypair) for the physical appliance, so that an expired certificate never means the box has lost
its identity. A commercial fleet should not ship one shared private key on every unit, since one
leak would compromise them all. Exact provisioning is open.

**Renew early, automatically.** Rather than "healthy until expiry", the document proposes tracking
an **offline runway**: how long trusted Full Mode would last if the internet vanished now. It
suggests renewing whenever the runway falls below a reserve of perhaps 10–14 days, to be checked
against certificate authority policy. Restoring security should be automatic, while
product-changing updates ask first. Ordinary users should never be asked to renew a certificate.

**An app as a courier.** <span class="avr-badge planned">Planned</span> A future native app could
download updates while online and carry them to an isolated appliance later. It could carry a
fresh certificate obtained earlier, but it cannot create a publicly trusted certificate offline.
An app is never the baseline: browser-only players stay in Limited Mode until a valid certificate
is obtained, and per ADR 0012 they still have a usable Party.

The document closes with a list of things still to prove, of which only the last is the subject
of LIMITED-MODE: that the Party itself survives an expired certificate, with an explicit Limited
Mode identity model.
