---
title: "ADR 0016: Service identities"
description: How each service and each native game on the appliance gets its own identity, its own key and its own state, what that protects against, and what it explicitly does not.
sources:
  - avrana-party:docs/adr/0016-service-identities-and-local-trust-boundary.md
  - avrana-party:contracts/service-boundary.v1.json
  - avrana-party:avrana/ops/boundary.py
  - avrana-party:avrana/ops/provision_game.py
  - avrana-party:avrana/party/protocol.py
  - avrana-party:deploy/games/avrana-game@.service
  - avrana-party:deploy/games/avrana-game@.socket
  - avrana-party:deploy/party-core/avrana-party-core.service
  - avrana-party:deploy/party-core/avrana-party-core.socket
  - avrana-party:deploy/arcade/avrana-party-session.conf
  - avrana-party:ops/migrate-service-users.sh
  - avrana-party:experiments/service-trust/proof.sh
  - avrana-party-games:deploy/avranaparty-games.service
verified: 2026-10-09
---

# ADR 0016: Service identities and the local trust boundary

!!! abstract "At a glance"
    **Decided:** 2026-10-03 · **Status:** <span class="avr-badge accepted">Accepted direction</span>; phase-one pieces and the native-game unit <span class="avr-badge source">In source</span>; nothing deployed or migrated
    Every service on the appliance, and every native game, should run as its own system
    identity, hold only its own secrets, and reach other services through Unix sockets whose
    permissions say who may connect. The ADR is equally explicit about what this does **not**
    protect against.

## The problem

[ADR 0014](0014-native-games-isolated-lan-games-retired.md) decided that each native game has its
own process, identity, secrets and state, but left the service-manager details open. This ADR
supplies them, starting from what was recorded read-only on the appliance on 2026-10-03:

- **One Unix user for everything.** Party Core, the LAN Games fork and the arcade all ran as the
  owner's login account, from code that account owns.
- **Every key was every service's key.** Each game has its own signing key, but every service
  could read all of them, plus Party Core's device store and the fork's Wi-Fi password file, and
  could rewrite the others' code. Per-game keys were nominal.
- **Loopback was the only local gate.** "From `127.0.0.1`" means "from any process on this
  machine", so with shared keys nothing identified the caller.

The signatures are sound: typed, session-bound, expiring and replay-protected. What was missing
was a key only two parties can read. That was fine for a prototype, but not for a field tester's
appliance or for building the second native game.

## What was decided

### What is promised

The unit of trust is **the systemd service identity**. For the first appliance to leave the
owner's hands:

1. A bug in, or compromise of, one native game cannot read another game's key or state, Party
   Core's device store, other services' secrets, the TLS key or Wi-Fi credentials; cannot change
   code or service definitions; cannot connect to another game's socket; and cannot pass itself
   off to Party Core as another game.
2. No local caller is trusted for its address. Socket file permissions admit a peer, and a key
   only that game and Party Core can read identifies it.
3. The operator's login account runs no service and owns no service secret.

### What is not promised

Stated so that nobody assumes it:

- anything against `root`, `sudo` holders or physical access (storage is unencrypted);
- containment of **deliberately hostile** game code (kernel attack surface, resource exhaustion,
  a stronger sandbox), which is a later decision (AVR-69). Field-test games are first-party code
  that may be *buggy*, not *adversarial*;
- isolation between games inside the legacy LAN Games process, which is one trust unit;
- protection from a compromised Party Core, which holds every game key by design, or nginx;
- what a game can do with its own authority: mint tickets for or end its own session, or
  misreport its own result ([ADR 0015](0015-game-result-envelope.md) checks only its shape);
- anything in the browser, which is [ADR 0013](0013-party-and-game-browser-origins.md)'s boundary.

### Service identities

| Service | Identity | Why |
|---|---|---|
| Party Core | Fixed system user `avrana-party` | Owns the master key store and needs a stable group membership |
| Arcade | Fixed system user `avrana-arcade`, plus the input and video device groups | Device access is by group; no other service gets those groups |
| LAN Games fork (retiring) | Fixed system user `avrana-lan-games`, while it exists | One trust unit; deleted with the runtime |
| Each native game | A systemd **dynamic user** from one template unit: a distinct, temporary uid per running game | Games come and go; nothing to create or clean up |
| nginx | Unchanged (`root` master, `www-data` workers) | The front door |
| Renewal, deployment, provisioning | `root`, one-off tasks | They create identities and write secrets |
| Operator | The owner's login account, with `sudo` | Runs no service |

Provisioning therefore never creates a Unix user for a game. Two groups express the only two
local permissions: "may connect to a game's socket" (nginx and Party Core) and "may connect to
Party Core's internal socket" (native games only). No service can write code, unit files, the
registry, grants or contracts, all of which are owned by `root`.

### Secrets and state

Party Core owns the key store and reads it directly, so a registry reload can pick up a new game.
Every other key holder receives **exactly its own key** through systemd's `LoadCredential=`:
systemd reads it as `root` at start and gives that unit alone a private in-memory copy. Each
native game also gets a private state directory and a private `/tmp`. Keys are never in Git, an
image, a backup, a log or a unit file, and are regenerated on a rebuild.

Rejected for key delivery: a second on-disk copy per game (copies drift on rotation), a shared
group on the key file (not "exactly two readers"), and environment variables (visible in unit
files and `/proc`). One prerequisite code change was approved: the key loader had to accept
systemd's credential file, whose access-control list makes it look group-readable, while still
refusing real group access.

### Local communication

Native games use **Unix sockets only and have no IP networking at all**: no TCP port, no route to
the remaining loopback listeners, no way to open a port on the Party Wi-Fi. nginx and Party Core
reach a game through its socket; a game reports its end and result on Party Core's internal
socket. Loopback TCP stays for the public Party API behind nginx, the arcade (it needs IP for
WebRTC) and the retiring fork, each now protected by a key that is no longer shared.

Two layers share the work. **Socket permissions** decide which *kind* of peer may connect, enforced
by the kernel. **The signature** decides *which game* it is, because dynamic uids are not stable
enough to map to games.

## Why this way

Options weighed against a Raspberry Pi appliance:

- **Fixed users for the three platform services: adopted.** They own files or device groups that
  outlive a run.
- **A fixed user per game: rejected.** Provisioning would create and delete users, leaving
  orphaned uids and files.
- **A dynamic user per game: adopted.** No provisioning state, hardening built in.
- **Dynamic users for Party Core or the arcade: rejected**, because of the key store and device
  groups.
- **Encrypted credentials: deferred.** The Pi 4 has no TPM, and offline disk reads are physical
  access, which is not promised.
- **Network namespaces, system-call filters, stricter resource ceilings: deferred** until hostile
  code is in scope or real games are measured. **Containers: rejected for now.**

The owner's decisions of 2026-10-03 carried this design forward: native games are told apart
**by signature alone** for the field test; the key-loader change goes first; Party Core, the fork
and the arcade **leave the owner's login account before the field test**, without waiting for LAN
Games to retire; and the public API stays on loopback TCP.

The accepted cost: any native game can reach the Party's internal socket, so **a game whose key
leaked could be impersonated by another local game**. With first-party games holding only their
own keys, that first requires a key disclosure. Also rejected: checking peer Unix credentials
(needs stable uids), a second Party-only control socket per game (doubles listeners; revisit for
untrusted games), and games creating their own sockets (they would need the group that reaches
every game). **Party Core gets no authority over systemd**: games start on first connection
and stop when idle, and only `root` provisioning enables or removes them.

## What it means in practice

Migration happens in three owner-approved phases, each with a reverse and each leaving a working
appliance: (1) before the field test, the three existing services move to their own users and
`LoadCredential=` delivery; (2) native games arrive with the template, sockets, generic nginx
route and `provision-game`, Checkers first; (3) the legacy LAN Games identity is deleted with its
runtime.

The wire protocol does not change. Only the address a native game's messages go to changes.
"`ended` only from loopback" stays true for the arcade and fork; for native games it becomes
"only on Party Core's internal socket". [ADR 0006](0006-party-session-protocol.md)'s "local
services are trusted" is narrowed: each is trusted only with its own key.

## Where it stands today

The status line "not implemented · not deployed" is older than the code. **In source**, not
deployed: Party Core's hardened unit as `avrana-party` with its internal socket; arcade and LAN
Games units receiving their own keys by `LoadCredential=`, and the key loader that accepts them;
an owner-run **phase-one migration script** with a dry run and a reverse; the native-game **unit
template** and `provision-game`; and the boundary written as data, with a read-only **boundary
checker** that judges a host rule by rule.

Evidence: a proof script on a disposable CI runner passed 9 of 9 checks (a dynamic user read only
its own key and state; socket groups admitted only the intended peers; a game without IP still
reached the Party). Against the appliance facts of 2026-10-03, the checker found **6 of 25**
phase-one rules met. **Not yet proven on the appliance itself:** the same checks on its
Debian/arm64 system, where service code will live, nginx joining the socket group, the arcade
under a new user, and socket activation of a real game. No migration has been recorded as done.

Deferred: community-game sandboxing (AVR-69), encrypted credentials and storage, moving the
public API, arcade or fork to Unix sockets, a per-game Party-only channel, a web admin's
identity, the SDK and `.avrgame`.

## Related decisions

- [ADR 0014: native games, LAN Games retired](0014-native-games-isolated-lan-games-retired.md), whose open details this settles
- [ADR 0006: the session protocol](0006-party-session-protocol.md), whose key and transport statements this narrows
- [ADR 0003: identifiers and keys](0003-ids-and-keys.md) and [ADR 0009: the arcade provider](0009-arcade-party-provider.md)
- [ADR 0013: separate browser origins](0013-party-and-game-browser-origins.md) and [ADR 0015: the result envelope](0015-game-result-envelope.md)
- [Trust boundaries](../architecture/trust-boundaries.md) and [native games](../games/native-games.md)
