#!/usr/bin/env python3
"""Check that every page is traceable to the engineering repositories.

For each page under docs/ this checks that:

  * the front matter has `sources` and `verified`;
  * each source names a repository listed in sources.yml;
  * each source file or directory exists at that repository's recorded `verified_revision`;
  * each link into an engineering repository (github.com/rcnechamkin/<repo>/blob|tree/<ref>/<path>)
    points at a path that exists.

It also warns when a source no longer exists on the repository's current branch (the page
explains something that has since moved or been deleted, and needs reconciling), and when a
status snapshot page has not been re-verified for more than 30 days.

Usage (checkouts are local clones with history covering the recorded revisions):

    python tools/check_sources.py \
        --repo avrana-party=../avrana-party \
        --repo avrana-party-games=../avrana-party-games \
        --repo avrana-game=../avrana-game

A repository without a checkout is skipped with a warning, so the structural checks still run
on a laptop with no clones. CI passes every checkout and `--require-checkouts`.
Exit status: 0 when there are no errors, 1 otherwise.
"""
from __future__ import annotations

import argparse
import datetime
import sys

from docsources import load_pages, load_repos, links, parse_checkouts

SNAPSHOT_DIRS = ("status/",)
SNAPSHOT_MAX_AGE = 30  # days


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--repo", action="append", default=[], metavar="NAME=PATH",
                        help="local checkout of an engineering repository")
    parser.add_argument("--require-checkouts", action="store_true",
                        help="fail instead of skipping when a repository has no checkout")
    parser.add_argument("--strict-head", action="store_true",
                        help="treat a source missing on the current branch as an error")
    args = parser.parse_args(argv)

    repos = load_repos(parse_checkouts(args.repo))
    errors: list[str] = []
    warnings: list[str] = []

    for repo in repos.values():
        if repo.checkout is None:
            message = f"{repo.name}: no checkout given; its paths are not checked"
            (errors if args.require_checkouts else warnings).append(message)
        elif not repo.has_revision(repo.verified_revision):
            errors.append(f"{repo.name}: recorded revision {repo.verified_revision} is not in "
                          f"{repo.checkout} (fetch more history)")
            repo.checkout = None

    def check(page_rel: str, repo_name: str, path: str, ref: str | None, what: str) -> None:
        repo = repos.get(repo_name)
        if repo is None:
            errors.append(f"{page_rel}: {what} names unknown repository {repo_name!r}")
            return
        if repo.checkout is None:
            return
        head = repo.tip()
        # A link to the tracked branch (or a source) is checked at the recorded revision, which is
        # what the page was written against. A link pinned to another ref is checked at that ref.
        rev = repo.verified_revision
        if ref is not None and ref != repo.branch:
            rev = repo.resolve(ref)
            if rev is None:
                errors.append(f"{page_rel}: {what} {repo_name} uses unknown ref {ref!r}")
                return
        if not repo.exists(path, rev):
            errors.append(f"{page_rel}: {what} {repo_name}:{path} does not exist at {rev[:12]}")
        elif not repo.exists(path, head):
            message = (f"{page_rel}: {what} {repo_name}:{path} no longer exists on "
                       f"{head}; reconcile this page")
            (errors if args.strict_head else warnings).append(message)

    pages = load_pages()
    today = datetime.date.today()
    for page in pages:
        if not page.meta.get("sources"):
            errors.append(f"{page.rel}: no `sources` in front matter")
        verified = page.meta.get("verified")
        if not verified:
            errors.append(f"{page.rel}: no `verified` date in front matter")
        elif not isinstance(verified, datetime.date):
            errors.append(f"{page.rel}: `verified` must be a YYYY-MM-DD date")
        elif page.rel.startswith(SNAPSHOT_DIRS) and (today - verified).days > SNAPSHOT_MAX_AGE:
            # Status snapshots draw on Linear, which no tool can check: flag them by age instead.
            warnings.append(f"{page.rel}: snapshot verified {verified}, more than "
                            f"{SNAPSHOT_MAX_AGE} days ago; refresh it")
        for repo_name, path in page.sources:
            if not repo_name:
                errors.append(f"{page.rel}: source {path!r} must be written REPO:PATH")
                continue
            check(page.rel, repo_name, path, None, "source")
        for repo_name, ref, path in links(page):
            check(page.rel, repo_name, path, ref, "link to")

    for line in warnings:
        print(f"warning: {line}")
    for line in errors:
        print(f"error: {line}")
    print(f"{len(pages)} pages checked: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
