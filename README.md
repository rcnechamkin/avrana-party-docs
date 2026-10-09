# Avrana Party documentation

Human-readable documentation for [Avrana Party](https://github.com/rcnechamkin/avrana-party):
a portable, local-first multiplayer appliance where phones are the screens and the controllers.

The engineering repositories are written for coding agents and the engineers directing them.
This repository explains the same system to people: what it is, how it fits together, how games
plug in, how mature each part is, and how to contribute. It is a **presentation layer, not an
authority**. Every technical contract, security guarantee and architectural decision is owned by
the engineering repositories, and every page here links back to them.

## Layout

```
mkdocs.yml            site configuration and navigation
requirements.txt      pinned build dependencies
sources.yml           engineering repositories and the revisions this site was reconciled against
docs/                 the site's pages (Markdown)
  index.md            landing page
  introduction/       what Avrana Party is, why phones only, today versus the vision
  architecture/       system overview, appliance and network, the Party, sessions, trust, ADRs
  games/              how games integrate, execution models, contracts, native games, design
  developers/         ecosystem, local development, contributing, reading the specs, games
  status/             project status snapshot and known upstream discrepancies
  about/              glossary, how this documentation works
  assets/             stylesheet and icon
includes/             snippets appended to every page (abbreviations)
tools/                source-tracing checks and the reconciliation report
.github/workflows/    CI (build and checks), scheduled reconciliation report, manual publishing
```

## Preview locally

Requires Python 3.10 or newer.

```sh
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
mkdocs serve                    # http://127.0.0.1:8000, reloads on save
```

## Build and validate

```sh
mkdocs build --strict           # fails on broken internal links, anchors or nav entries
```

To check that every page's declared sources and every link into the engineering repositories
still resolve, clone the engineering repositories (with enough history to contain the revisions
in `sources.yml`) and run:

```sh
git clone https://github.com/rcnechamkin/avrana-party .sources/avrana-party
git clone https://github.com/rcnechamkin/avrana-party-games .sources/avrana-party-games
git clone https://github.com/rcnechamkin/avrana-game .sources/avrana-game

python tools/check_sources.py --require-checkouts \
  --repo avrana-party=.sources/avrana-party \
  --repo avrana-party-games=.sources/avrana-party-games \
  --repo avrana-game=.sources/avrana-game
```

CI runs both on every pull request (`.github/workflows/docs.yml`).

## Keeping the site in step with the engineering repositories

```sh
python tools/reconcile.py \
  --repo avrana-party=.sources/avrana-party \
  --repo avrana-party-games=.sources/avrana-party-games \
  --repo avrana-game=.sources/avrana-game
```

This prints a report of the pages whose sources changed since the recorded revisions, sources
that were deleted or renamed, and new ADRs or design documents that no page covers. It changes
nothing. A weekly workflow produces the same report as a downloadable artifact. The procedure for
acting on it, including a prompt for an AI agent, is in [CONTRIBUTING](CONTRIBUTING.md).

## Publishing

The site is published with GitHub Pages at
<https://rcnechamkin.github.io/avrana-party-docs/>. Nothing publishes automatically: merging to
`main` changes the repository, not the live site.

To publish the current `main`, run the **Publish** workflow manually from the Actions tab
(`.github/workflows/publish.yml`). It refuses to run without `site_url` or from a branch other
than `main`, builds with `--strict`, and deploys.

How it is set up, for reference:

- Settings → Pages → Build and deployment → Source is **GitHub Actions**. On a personal account,
  a Pages site is public even when the repository is private.
- `site_url` in `mkdocs.yml` is the published address.
- Recommended: Settings → Environments → `github-pages` allows deployments only from `main`,
  optionally with required reviewers.
- To move to a custom domain such as `docs.avrana.net`, add a DNS-only `CNAME` to
  `rcnechamkin.github.io`, set the domain in Settings → Pages, enforce HTTPS, and update
  `site_url`. Do not enable HSTS on the `avrana.net` zone: the appliance's `party.avrana.net`
  must never receive HSTS (Party ADR 0004 and ADR 0012).

Any static host works instead. `mkdocs build` writes a self-contained site to `site/`.

## Licensing

No license has been chosen for this documentation yet. The Avrana Party repository itself has no
license file, and that is an open decision for its owner. The documentation's license should be
decided alongside it.
