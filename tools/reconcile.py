#!/usr/bin/env python3
"""Report which documentation pages may need updating after the engineering repositories change.

For each repository in sources.yml this compares the recorded `verified_revision` with a target
revision (default: origin/<branch> in the local checkout, else HEAD) and writes a Markdown report
of:

  * pages whose sources changed, with the changed files and a compare link. A page's sources are
    its front-matter `sources` plus every file it links to on the tracked branch;
  * sources that were deleted or renamed;
  * new canonical material (ADRs, design documents, dated findings, runbooks, game contracts,
    games) that no page covers;
  * repositories with no changes, naming the target revision so a stale checkout is visible.

It is report-only. It never fetches, edits pages, updates sources.yml, commits or publishes. A
person or an agent reads the report, updates the pages in a pull request and, once the pages are
reconciled, bumps `verified_revision` in that same pull request.

Usage:

    python tools/reconcile.py \
        --repo avrana-party=../avrana-party \
        --repo avrana-party-games=../avrana-party-games \
        --repo avrana-game=../avrana-game \
        --output reconcile-report.md

Exit status is 0 unless --fail-on-drift is given and something needs attention (including a
repository that could not be compared).
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict

from docsources import all_sources, load_pages, load_repos, parse_checkouts, parse_pairs

# New files under these paths are material a page may need to explain. Dated findings carry
# deployment and real-phone evidence, which is how maturity labels change.
WATCHED = {
    "avrana-party": ("docs/adr/", "docs/design/", "docs/findings/", "docs/runbooks/",
                     "contracts/games/", "contracts/appliances/", "avrana/games/"),
    "avrana-party-games": ("docs/", "provider/", "games/"),
    "avrana-game": ("docs/",),
}


def covers(source: str, changed: str) -> bool:
    """A source covers a changed path when it is that file or a directory containing it."""
    source = source.rstrip("/")
    return changed == source or changed.startswith(source + "/")


def changed_files(repo, base: str, target: str) -> list[tuple[str, str, str | None]]:
    """[(status, path, new_path_or_None)] between two revisions, with renames detected."""
    result = repo.git("diff", "--name-status", "-M", f"{base}..{target}")
    if result.returncode != 0:
        raise SystemExit(f"{repo.name}: git diff failed: {result.stderr.strip()}")
    rows = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        status = parts[0][0]
        if status in ("R", "C") and len(parts) == 3:
            rows.append((status, parts[1], parts[2]))
        elif len(parts) >= 2:
            rows.append((status, parts[1], None))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--repo", action="append", default=[], metavar="NAME=PATH")
    parser.add_argument("--to", action="append", default=[], metavar="NAME=REV",
                        help="target revision for a repository (default: origin/<branch>, else HEAD)")
    parser.add_argument("--output", help="write the report here instead of stdout")
    parser.add_argument("--fail-on-drift", action="store_true")
    args = parser.parse_args(argv)

    repos = load_repos(parse_checkouts(args.repo))
    targets = parse_pairs(args.to, "--to", "REV")
    pages = load_pages()

    by_source: dict[tuple[str, str], set[str]] = defaultdict(set)
    for page in pages:
        for key in all_sources(page, repos):
            by_source[key].add(page.rel)

    out: list[str] = ["# Documentation reconciliation report", ""]
    attention = False

    for repo in repos.values():
        out += [f"## {repo.name}", ""]
        if repo.checkout is None:
            out += ["No checkout given; not compared.", ""]
            attention = True
            continue
        base = repo.verified_revision
        wanted = targets.get(repo.name) or repo.tip()
        target = repo.resolve(wanted)
        if target is None or not repo.has_revision(base):
            out += [f"Cannot compare: `{base[:12]}` or `{wanted}` is not in the checkout "
                    "(fetch more history).", ""]
            attention = True
            continue
        target_line = f"`{wanted}` = `{target[:12]}` ({repo.commit_date(target)})"
        if target == repo.resolve(base):
            out += [f"No changes: the recorded revision is the target, {target_line}.", ""]
            continue

        rows = changed_files(repo, base, target)
        out += [f"`{base[:12]}` → {target_line}: {len(rows)} files changed. "
                f"[Compare on GitHub]({repo.url}/compare/{base}...{target})", ""]

        sources = {src: pages_ for (name, src), pages_ in by_source.items() if name == repo.name}
        affected: dict[str, set[str]] = defaultdict(set)
        for status, path, new_path in rows:
            for src, page_set in sources.items():
                if covers(src, path):
                    note = path if status == "M" else \
                        f"{path} ({status}{' → ' + new_path if new_path else ''})"
                    for page in page_set:
                        affected[page].add(note)

        # A source is gone when it (file or directory) no longer exists at the target.
        gone = []
        for src, page_set in sorted(sources.items()):
            if repo.exists(src, base) and not repo.exists(src, target):
                renamed = [n for s, p, n in rows if s == "R" and p == src.rstrip("/")]
                what = f"renamed to `{renamed[0]}`" if renamed else "no longer exists"
                gone.append(f"`{src}` {what}; used by {', '.join(sorted(page_set))}")

        if affected:
            attention = True
            out += ["### Pages to review", ""]
            for page in sorted(affected):
                out.append(f"- **{page}** ({len(affected[page])} changed sources)")
                out += [f"    - `{note}`" for note in sorted(affected[page])]
            out.append("")
        if gone:
            attention = True
            out += ["### Sources deleted or renamed", ""] + [f"- {line}" for line in gone] + [""]

        new_material = [path for status, path, _ in rows
                        if status == "A" and path.startswith(WATCHED.get(repo.name, ()))
                        and not any(covers(src, path) for src in sources)]
        if new_material:
            attention = True
            out += ["### New material no page covers", ""]
            out += [f"- `{path}`" for path in sorted(new_material)] + [""]
        if not affected and not gone and not new_material:
            out += ["Changes touch no documented source.", ""]

    out += [
        "---",
        "",
        "Next step: for each page above, read the upstream change and decide whether the human "
        "explanation changes. Update pages, record any upstream discrepancy in "
        "`docs/status/discrepancies.md`, then bump `verified_revision` in `sources.yml` in the "
        "same pull request. See CONTRIBUTING.md, \"Reconciling with the engineering repositories\".",
        "",
    ]
    report = "\n".join(out)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(report)
    else:
        sys.stdout.write(report)
    return 1 if (args.fail_on_drift and attention) else 0


if __name__ == "__main__":
    sys.exit(main())
