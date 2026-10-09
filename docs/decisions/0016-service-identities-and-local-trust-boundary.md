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
  - avrana-party-games:deploy/avrana-party-session.conf
verified: 2026-10-09
---

# ADR 0016: Service identities and the local trust boundary

!!! abstract "At a glance"
    **Decided:** 2026-10-03 · **Status:** <span class="avr-badge accepted">Accepted direction</span>; phase-one pieces and the native-game unit <span class="avr-badge source">In source</span>; nothing deployed or migrated
    Every service on the appliance, and every native game, should run as its own system
    identity, hold only its own secrets, and reach other services through Unix sockets whose
    permissions say who may connect. The ADR is just as explicit about what this does **not**
    protect against.

## The problem

[ADR 0014](0014-native-games-isolated-lan-games-retired.md) decided that each native game is its
own process with its own identity, secrets and state, and that local communication should prefer
Unix sockets. It left the service-manager details open. This ADR fills them in.

What it found on the appliance (recorded read-only on 2026-10-03, nothing changed):

- **One Unix user for everything.** Party Core, the LAN Games fork and the arcade all ran as the
  owner's login account, from code checkouts that account owns.
- **Every key was every service's key.** Each game has its own signing key, but all three
  processes could read all the keys, Party Core's device store, the fork's Wi-Fi password file and
  avatar store, and could rewrite the code the others run. A "per-game key" was therefore only
  nominal: the Unix user was the only boundary, and it was shared.
- **Loopback was the only local gate.** Requests between the Party and games were accepted if
  they came from `127.0.0.1` and then checked by signature. But "loopback" means "any process on
  this machine". With shared keys, nothing identified the caller.

The signatures themselves are sound: typed, bound to an audience and session, expiring and
protected against replay. What they lacked was a key that only two parties can read. That was
fine for a prototype, but not a boundary to hand to a field tester or to build the second native
game on.

## What was decided

### What is promised for the first field-test appliance

The unit of trust is **the systemd service identity**. For an appliance that leaves the owner's
hands:

1. A bug in, or compromise of, one native game cannot read another game's key or state, Party
   Core's device store, any other service's secrets, the TLS private key or the Wi-Fi
   credentials. It cannot change any code or service definition on the appliance, cannot connect
   to another game's socket, and cannot pass itself off to Party Core as a different game.
2. No local caller is trusted because of its address. A local peer is admitted by file
   permissions on a Unix socket, and identified as a specific game by a key only that game and
   Party Core can read.
3. The operator's login account runs no service and owns no secret a service uses.

### What is not promised

The ADR lists these so that nobody assumes them:

- anything against `root`, whoever holds `sudo`, or someone with physical access (the storage is
  not encrypted);
- containment of **deliberately hostile** game code: kernel attack surface, resource exhaustion
  and a stronger sandbox are a later decision (AVR-69). Field-test games are first-party code that
  may be *buggy*, not *adversarial*;
- isolation between games inside the legacy LAN Games process, which is one trust unit;
- protection from a compromised Party Core, which holds every game key by design, or a
  compromised nginx;
- what a game can do with its own authority: mint tickets for its own session, end its own
  session, or misreport its own result (the Party validates the result's shape,
  [ADR 0015](0015-game-result-envelope.md));
- anything in the browser, which is [ADR 0013](0013-party-and-game-browser-origins.md)'s boundary.

### Service identities

| Service | Identity | Why this kind |
|---|---|---|
| Party Core | A fixed system user, `avrana-party` | It owns long-lived files, notably the master store of game keys, and needs a stable group membership. |
| Arcade | A fixed system user, `avrana-arcade`, with the input and video device groups | Device access is granted by group, and it is the only service that needs those groups. |
| LAN Games fork (retiring) | A fixed system user, `avrana-lan-games`, while it exists | One trust unit for everything inside it; deleted with the runtime. |
| Each native game | A systemd **dynamic user**: one template unit, with a distinct temporary uid per running game | Games come and go, and need no files outside their own directories. Nothing to clean up on removal. |
| nginx | Unchanged: `root` master, `www-data` workers | The front door. |
| Certificate renewal, deployment, provisioning | `root`, run once per task | They create identities and write secrets. |
| Operator | The owner's login account, with `sudo` | Runs no service. |

Because the dynamic-user template *is* the identity, provisioning a game never creates a Unix
user. Two groups express the only two local permissions that exist: one for "may connect to a
game's socket" (nginx and Party Core) and one for "may connect to Party Core's internal socket"
(every native game, and nothing else). Across every row: no service runs as a login account, no
service can write code, unit files, the registry, grants or contracts (all owned by `root`), and
services run only `root`-owned code outside any home directory.

### Secrets and state

- **Party Core owns the key store** and reads it directly. That lets a registry reload pick up a
  new game without a restart. The file permissions would let Party Core's identity rewrite a key.
  Nothing in Party Core does, and it is already the trust root for every key.
- **Every other key holder gets exactly its own key** through systemd's `LoadCredential=`:
  systemd reads the key as `root` when the unit starts and gives that unit alone a private,
  memory-backed copy. A game never has access to the key directory.
- **Each native game gets a private state directory** and a private `/tmp` that is discarded when
  it stops.
- **Keys are never in Git, an image, a backup, a log or a unit file.** On a rebuild they are
  regenerated: they protect only live sessions, and the Party is memory-only.

Rejected for delivering keys: a second on-disk copy per game, because two files drift on
rotation; a shared group on the key file, because a group is not "exactly two readers" and the
key loader rightly refuses it; and environment variables, which are visible in unit files and
`/proc`.

One code change was a prerequisite. systemd grants access to a credential file through an
access-control list, so the file's mode looks group-readable, and the Party's key loader refused
it in the proof run. The loader had to accept exactly that case while still refusing keys with
real group or other access. That was approved as a paired change to both repositories (AVR-253),
with no change to any message format.

### Local communication

Native games use Unix sockets and have **no network access at all**: a game's unit allows only
Unix sockets. It has no TCP port, cannot reach the remaining loopback listeners, and cannot open
a port on the Party Wi-Fi. nginx and Party Core reach a game through its socket. A game reports
its end and result to Party Core through Party Core's internal socket.

Loopback TCP stays, for now, for the public Party API behind nginx (a local caller gains nothing
a phone lacks), for the arcade (it needs IP for WebRTC), and for the retiring LAN Games fork.
Each depends on a key that is no longer shared.

Two layers divide the work:

- **Socket permissions answer "which kind of peer may speak here at all".** Only the front door
  and the Party reach a game; only games reach the Party's internal socket. The kernel enforces
  this.
- **The signature answers "which game is this".** Dynamic uids are not stable, so the Party does
  not map a uid to a game. The per-game key, now private to that game, does that job.

## Why this way

The ADR weighed the options against a Raspberry Pi appliance:

- **A fixed user per platform service: adopted.** There are three such services, and they own
  files or device groups that outlive a run.
- **A fixed user per game: rejected.** Provisioning would create and delete Unix users, and
  removal would leave orphaned uids and files.
- **A dynamic user per game: adopted.** It is an identity with no provisioning state, comes with
  hardening built in, and leaves nothing to reconcile on removal.
- **Dynamic users for Party Core or the arcade: rejected.** Party Core owns the key store, and the
  arcade needs fixed device groups.
- **Encrypted credentials: deferred.** The Pi 4 has no TPM, and the threat they address (reading
  the disk offline) is physical access, which is not promised.
- **A private network namespace, system-call filters, stricter resource ceilings: deferred**,
  until hostile code is in scope or real games have been measured.
- **Containers: rejected for now.** They answer no requirement the above does not.

The owner also made five decisions on 2026-10-03. They carried this reconciled design forward.
They accepted that, for the field test, Party Core tells native games apart **by signature
alone**. They approved the key-loader change ahead of everything else. They required Party Core,
the LAN Games fork and the arcade to **leave the owner's login account before the field test**,
without waiting for LAN Games to retire. And they kept Party Core's public API on loopback TCP.

The accepted cost of signature-only identification: every native game can connect to the Party's
internal socket, so **a game whose key leaked could be impersonated to the Party by any other
local game**. With first-party games that each hold only their own key, a key disclosure has to
happen first. Rejected alternatives were checking the peer's Unix credentials (it needs stable
uids, and gains nothing over a private key), a second Party-only control socket per game (it
doubles every game's listeners; to revisit with untrusted games), and games creating their own
sockets (they would then need the group that reaches every other game).

**Party Core gets no authority over systemd**: no `sudo`, no policy rule. A game starts on its
first connection (socket activation) and stops itself when idle. Enabling and removing games is
provisioning's job, as `root`.

## What it means in practice

The migration is planned in three phases. Each is an owner-approved deployment with a reverse
procedure, and each leaves a working appliance:

1. Before the field test, the three existing services leave the operator's account and get their
   own users and groups. Keys move to the new ownership and `LoadCredential=` delivery.
2. Native games arrive with the template units, sockets, generic nginx route and
   `provision-game`, with Checkers first.
3. The legacy LAN Games identity is deleted with its runtime.

The protocol on the wire does not change. Messages, tickets, replay rules and the result envelope
are exactly as [ADR 0006](0006-party-session-protocol.md) and ADR 0015 state. Only the address a
native game's messages go to changes. Earlier statements such as "`ended` is only accepted from
loopback" remain true for the arcade and the fork. For native games, the equivalent is "only on
Party Core's internal socket". ADR 0006's "the appliance and its local services are trusted" is
narrowed: local services are distinct identities, each trusted only with its own key.

## Where it stands today

The ADR's status line says "not implemented · not deployed". The first half is older than the
code. **In source**, not deployed:

- Party Core's unit running as `avrana-party`, with hardening and its internal Unix socket for
  games;
- the arcade and LAN Games unit drop-ins that receive their own keys by `LoadCredential=`, and
  the key loader that accepts such a credential;
- an owner-run **migration script** for phase 1, with a dry-run mode and a reverse;
- the native-game **unit template** (dynamic user, private state, Unix sockets only, key by
  credential) and `provision-game`;
- the boundary written down as data (`contracts/service-boundary.v1.json`), and a read-only
  **boundary checker** that judges a host against it rule by rule.

Evidence so far: a proof script on a disposable CI runner (Ubuntu, systemd 255) passed 9 of 9
checks. A dynamic user could read only its own key and state; socket groups admitted the intended
peers and refused others; and a game with only Unix sockets still reached the Party. Run against
the facts recorded from the appliance on 2026-10-03, the checker found **6 of 25** phase-one
rules met: every service ran as one user, the keys belonged to that user, and the games server
listened on all interfaces rather than loopback.

**Not proven, and needing the appliance itself:** the same checks on its Debian/arm64 system,
where service code will live, nginx workers joining the socket group, the arcade under a new
user, and socket activation of a real game. No migration has been recorded as done.

Deliberately deferred: community-game sandboxing and resource policy (AVR-69), encrypted
credentials and storage, moving the public API, arcade or fork to Unix sockets, a per-game
Party-only channel, a web admin's identity, and the SDK and `.avrgame`.

## Related decisions

- [ADR 0014: native games, LAN Games retired](0014-native-games-isolated-lan-games-retired.md), whose open service details this settles
- [ADR 0006: the session protocol](0006-party-session-protocol.md), whose key and transport statements this narrows
- [ADR 0003: identifiers and keys](0003-ids-and-keys.md) and [ADR 0009: the arcade provider](0009-arcade-party-provider.md)
- [ADR 0013: separate browser origins](0013-party-and-game-browser-origins.md), the browser-side boundary
- [ADR 0015: the game result envelope](0015-game-result-envelope.md)
- [Trust boundaries](../architecture/trust-boundaries.md) and [native games](../games/native-games.md)
