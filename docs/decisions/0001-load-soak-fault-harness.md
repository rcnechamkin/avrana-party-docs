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
    Build a reusable harness that holds several simulated phones on the arcade stream, injects
    client faults and gives a pass or fail, without changing the streaming service itself.

## The problem

The arcade runs one emulator, encodes its picture once with the hardware H.264 encoder, and
sends it to each phone over WebRTC (the browser's real-time media protocol). It had been checked
only in one-off ways: browser tests, a real two-phone session and a script that polls the
arcade's statistics. There was no repeatable way to hold several clients for a long period (a
**soak**) and get a pass or fail, to inject faults and check recovery, or to catch regressions
and slow drifts such as rising audio latency.

Two reliability defects were already known: audio latency that ratcheted upward with every
session, and a fatal error that left the service running but broken. Fixing them meant changing
and restarting the streaming server as root, which was not possible in that session, and shipping
blind fixes would have risked the working stream. A harness that touches nothing on the service
was the safest useful step, and it would measure those fixes before and after.

## What was decided

Add a harness, run from a machine on the Avrana Party Wi-Fi, in three layers:

1. **Pure metrics logic**: percentiles, per-client and server summaries, threshold checks and a
   report. It does no input or output, so it is unit-tested on its own.
2. **A browser driver**: Playwright helpers that connect clients, read the arcade page's own
   metrics, sample the server's statistics, and fail fast if the test machine has dropped off
   the Wi-Fi.
3. **Two suites**: a **soak** that holds N clients for a set time and writes a JSON report, and a
   **fault** suite for abrupt drops, join-and-leave churn and more clients than controllers. Both
   are tagged `@heavy`, so the everyday test run leaves them out.

## Why this way

The key choice is **what counts as a failure**. The harness simulates phones with several
Chromium browsers on one laptop over sometimes-flaky Wi-Fi, which exaggerates client-side
jitter (the ADR records about 31 ms on real phones against 30 to 130 ms for co-located browsers).
So the hard gates are only the signals that stay meaningful: no server error, the expected
number of clients connected, zero median packet loss, and a frame rate that did not collapse
(median at least 45 frames per second, never below 20). Jitter and round-trip time are reported,
not gated. Real phones remain the authority on absolute latency.

## What it means in practice

By default the soak runs two clients for 90 seconds; environment variables change the count,
duration and sampling interval. The ADR names its limits: browsers on one laptop are not phones;
closing a browser is a clean disconnect, not a phone silently losing the network; the laptop's
own Wi-Fi drops can interrupt long runs; and at the time, a soak itself triggered the audio
ratchet until the service restarted.

## Where it stands today

<span class="avr-badge source">In source</span> The harness and both suites are in the Party
repository. The pure metrics tests run in the offline CI lane; the soak and fault suites need
the live appliance and are run by hand. The soak suite's notes say two clients is the load tried
on real phones, and that the arcade's four controller seats need a four-client run and a real
four-phone session.

The arcade source now contains changes aimed at both defects: it re-stamps audio to the running
clock so latency cannot ratchet, and it exits with an error on an unrecoverable failure so
systemd restarts it. This page does not establish when those changes were verified on hardware.

See [Testing](../developers/testing.md) for how this fits the project's test tiers.

## Related decisions

- [ADR 0004](0004-full-mode-contracts-and-providers.md) defines the evidence tiers; this harness
  is live-appliance testing, outside what CI can prove.
- [ADR 0009](0009-arcade-party-provider.md) later made the arcade a Party-launched provider.
