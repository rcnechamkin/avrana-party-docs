---
title: "ADR 0001: Load, soak and fault harness"
description: Why the project built a repeatable load, soak, fault and regression harness for the arcade stream, and which signals it treats as pass or fail.
sources:
  - avrana-party:docs/adr/0001-load-soak-fault-harness.md
  - avrana-party:tests/lib/soak-metrics.ts
  - avrana-party:tests/lib/soak-driver.ts
  - avrana-party:tests/soak.spec.ts
  - avrana-party:tests/fault.spec.ts
  - avrana-party:package.json
  - avrana-party:.github/workflows/offline-checks.yml
  - avrana-party:docs/findings/2026-09-20-audio-ratchet-and-recovery.md
  - avrana-party:arcade/stream.py
verified: 2026-10-09
---

# ADR 0001: A repeatable load, soak and fault harness for the arcade stream

!!! abstract "At a glance"
    **Decided:** 2026-09-20 · **Status:** Accepted · <span class="avr-badge source">In source</span> (test tooling, run by hand against the appliance)
    Build a reusable test harness that holds several simulated phones on the arcade stream for a
    sustained period, injects client faults, and gives a pass or fail, without changing the
    streaming service itself.

## The problem

The arcade runs one emulator on the appliance, encodes its picture once with the hardware H.264
encoder, and sends that video to each phone over WebRTC (the browser's real-time media
protocol). In September 2026 it had been checked in useful but one-off ways: browser end-to-end
tests, a real two-phone session, and a read-only script that polls the arcade's statistics
endpoint.

What it lacked was a *repeatable* way to:

- keep several clients connected for a long period (a **soak**) and get a clear pass or fail;
- inject client faults, such as an abrupt disconnect, rapid join-and-leave churn or more clients
  than there are controllers, and check that the service recovers;
- catch regressions in the streaming path automatically;
- measure behaviour over time, for example a drift in audio latency.

Two reliability defects were already known: audio latency that ratcheted upward with every
streaming session, and a fatal error that left the service running but broken instead of
restarting it. Fixing them meant changing the streaming server and restarting it as root, which
was not possible in the session that wrote this ADR. Shipping those fixes without a way to
verify them would have put the working stream at risk. A harness that touches nothing on the
service was the safest useful step, and it would become the before-and-after measuring tool for
those fixes.

## What was decided

Add a harness that runs from a machine joined to the Avrana Party Wi-Fi, built in three layers:

1. **Pure metrics logic.** Functions that compute medians and percentiles, summarize each
   client and the server, compare the results with thresholds and format a report. They do no
   input or output, so they can be unit-tested on their own.
2. **A browser driver.** Playwright helpers that connect a client (or attempt to, tolerating a
   rejection), read the arcade page's own metrics panel, sample the server's statistics, and fail
   quickly with a clear message when the test machine has dropped off the Wi-Fi.
3. **Two test suites.** A soak suite holds N clients for a set duration, samples them, applies
   the thresholds and writes a JSON report. A fault suite covers abrupt drops, churn and
   over-subscription, then checks recovery. Both are tagged `@heavy`, so the everyday test run
   stays fast and leaves them out.

## Why this way

The most important choice is **what counts as a failure**. The harness simulates phones with
several Chromium browsers on one laptop, over a Wi-Fi link that is sometimes unreliable. That is
a pessimistic model of the client side: the ADR records about 31 ms of jitter on real phones,
against 30 to 130 ms for co-located Chromium clients depending on contention.

So the hard gates are only the signals that stay meaningful under that model:

- the server reported no error;
- the expected number of clients connected;
- median packet loss per sampling interval was zero;
- the frame rate did not collapse (median at least 45 frames per second, never below 20).

Jitter-buffer delay and round-trip time are **reported but not gated**. Real phones remain the
authority on absolute latency and jitter.

Keeping the harness entirely outside the streaming service meant it could be built and verified
without root access and without touching the live WebRTC path.

## What it means in practice

The soak runs two clients for 90 seconds by default. The client count, duration and sampling
interval are set with environment variables, for example four clients for ten minutes. A
separate command runs the fault suite. Each run leaves a JSON report among the test results.

The ADR is candid about the limits:

- **Co-located browsers are not phones.** Client-side jitter is exaggerated, which is why it is
  not gated.
- **Closing a browser is a clean disconnect.** It is not the same as a phone silently losing
  the network. Simulating that needs packet-level tooling and the WebSocket heartbeat.
- **The test laptop's Wi-Fi drops intermittently.** That can interrupt long runs. The driver
  fails fast when it happens; a steadier Wi-Fi client is the real fix.
- **A soak has a side effect.** At the time, connecting real peers triggered the audio ratchet,
  which only cleared on a service restart.

## Where it stands today

<span class="avr-badge source">In source</span> The three layers and both suites are in the Party
repository, with `npm run soak` and `npm run fault` commands. The pure metrics tests run in the
project's offline CI lane. The soak and fault suites themselves need the live appliance, so they
are run by hand and are not part of CI.

The soak suite's own notes say two clients is the load that has been tried on real phones.
Exercising the arcade's four controller seats needs a four-client run and a real four-phone
session.

The arcade source now contains changes aimed at both defects that motivated the harness. It
re-stamps audio buffers to the running clock so the latency cannot ratchet, and it exits with
an error on an unrecoverable failure (including a stalled video capture) so that systemd
restarts it. This page does not establish when those changes were verified on hardware or
deployed.

For how this harness fits the project's test tiers, see [Testing](../developers/testing.md).

## Related decisions

- [ADR 0004](0004-full-mode-contracts-and-providers.md) defines the three evidence tiers. This
  harness is live-appliance testing, which that ADR keeps separate from what CI can prove.
- [ADR 0009](0009-arcade-party-provider.md) later made the arcade a Party-launched provider.
