# Contributing to the Avrana Party documentation

This repository explains Avrana Party to people. It does not define it. Read
[About this documentation](docs/about/this-documentation.md) first. It explains the relationship
to the engineering repositories that every change here has to respect.

## Ground rules

1. **The engineering repositories are authoritative.** Never state a contract, a security
   property, a requirement or a decision that is not in them. If you believe the engineering
   repositories are wrong or inconsistent, record it in
   [`docs/status/discrepancies.md`](docs/status/discrepancies.md) and raise it upstream. Do not
   "fix" it here.
2. **Label maturity honestly.** Use the [maturity labels](docs/about/this-documentation.md#maturity-labels).
   Deployed means dated deployment evidence. Merged means *in source*. Accepted means decided,
   not built. When evidence is missing, say so in words.
3. **No tutorials for functionality that does not exist.** Explain the plan, link to it and say
   it is a plan.
4. **Explain, then link.** Do not copy volatile detail such as message tables, schemas or exact
   configuration. Explain what it is for, and link to the canonical file.
5. **Every page is traceable.** Front matter lists `sources` (`REPO:PATH`, with repositories as
   named in `sources.yml`) and a `verified` date.

## Writing style

- Write for a technically competent reader who has never seen the project. Introduce a concept
  before its implementation.
- Prefer connected prose to bullet fragments. Use lists for genuinely list-shaped content:
  options, steps, inventories.
- Explain *why* a decision was made whenever the sources record it. Rejected alternatives are
  often the most useful part.
- Avoid marketing language and superlatives. Say "the appliance broadcasts its own Wi-Fi", not
  "a revolutionary seamless experience".
- Use the project's own terms (Party, Member, Host, Participant, ticket, Full Mode) and define
  them in the [glossary](docs/about/glossary.md).
- Diagrams use Mermaid fenced blocks (` ```mermaid `). Add one only when it explains a
  relationship, sequence or state machine better than prose.
- **Link to this site, not to the engineering repositories.** When a page refers to an engineering
  document, link to its plain-language edition here: a decision under `docs/decisions/`, a design
  under `docs/design/`, or the page or section that explains it. If no edition exists yet, write
  one rather than linking to the original. Put the original in the page's `sources`. The build
  renders those as the **Canonical sources** block, which is how readers reach the authoritative
  text. `tools/check_sources.py` fails on body links to files in the engineering repositories.
  Links to a repository's root page are fine.
- Inside this site, use relative links to `.md` files. `mkdocs build --strict` checks them.
- Dates are ISO 8601 (`2026-10-09`). Status snapshots say "as of" with a date.

## Pull requests

Before opening one:

```sh
mkdocs build --strict
python tools/check_sources.py --require-checkouts --repo avrana-party=… --repo avrana-party-games=… --repo avrana-game=…
```

Fill in the pull request template. Say which engineering revisions you read, which pages changed,
and whether any claim's maturity label changed. A person reviews and merges every change.
Merging does not publish. Publishing is a separate, manual step.

## Reconciling with the engineering repositories

The engineering repositories change daily. This site should change much less often, but it must
not silently drift. The procedure:

1. **Get the report.** Run `tools/reconcile.py` locally, or download the artifact from the latest
   *Reconciliation report* workflow run. It lists:
   - pages whose declared sources changed since the revision in `sources.yml`;
   - sources that were deleted or renamed;
   - new ADRs, design documents, runbooks or contracts that no page lists.
2. **Read the upstream changes**, not just the file names. Use the compare links in the report.
   Also check the upstream dated findings and the system map for deployment evidence.
3. **For each affected page, decide** whether the human explanation changes:
   - **No:** nothing to edit for that page.
   - **Yes:** edit the prose, update maturity labels, add or remove `sources`, and update
     `verified`.
   - **Upstream inconsistency:** record it in `docs/status/discrepancies.md`. Remove entries that
     have since been fixed upstream.
4. **Cover new material** if it matters to a newcomer, such as a new ADR. Otherwise leave it.
   Not every runbook needs a page.
5. **Bump `verified_revision` and `verified_on`** in `sources.yml` for each repository you
   reconciled, in the same pull request.
6. **Validate**: a strict build, and the source check with `--require-checkouts`.
7. **Open a pull request** describing what changed upstream and what changed here.

### Prompt for an AI agent

An agent can carry out the procedure above. It proposes changes and never publishes. A suitable
prompt:

> You maintain the human-facing Avrana Party documentation in this repository. Read
> CONTRIBUTING.md and docs/about/this-documentation.md. Clone the engineering repositories named
> in sources.yml with full history, run `tools/reconcile.py` against them, and read every upstream
> change the report lists, including relevant ADRs, findings and the system map. Update only the
> pages whose human explanation is now wrong or incomplete, keeping the existing style and
> maturity labels and never stating anything the engineering repositories do not support. Record
> upstream inconsistencies in docs/status/discrepancies.md rather than resolving them. Bump
> `verified_revision` for each repository you reconciled. Run `mkdocs build --strict` and
> `tools/check_sources.py --require-checkouts`. Then open a pull request that summarizes the
> upstream changes, the page changes, any maturity changes and anything you were unsure about.
> Do not merge, publish or modify the engineering repositories.

## What not to do

- Do not edit the engineering repositories from work in this repository.
- Do not add an automatic publishing trigger.
- Do not paste credentials, internal hostnames, private addresses beyond those already public in
  the engineering repositories, or any personal data.
- Do not present a dated snapshot as current without its date.
