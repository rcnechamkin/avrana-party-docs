"""Shared helpers for the documentation source-tracing tools.

Every page under docs/ declares, in its YAML front matter, the engineering files it explains:

    sources:
      - avrana-party:docs/adr/0011-party-console-model.md
    verified: 2026-10-09

sources.yml records, for each engineering repository, the revision this site was last
reconciled against. These helpers load both and talk to local Git checkouts of the source
repositories. They never fetch, write or push anything.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SOURCES_FILE = ROOT / "sources.yml"

# A link into one of the engineering repositories, e.g.
# https://github.com/rcnechamkin/avrana-party/blob/main/docs/adr/0011-x.md#anchor
# Limitation: the ref must not contain "/" (link to `main` or a commit, not to `feat/x`).
GITHUB_LINK = re.compile(
    r"https://github\.com/rcnechamkin/(?P<repo>[A-Za-z0-9_.-]+)/(?P<kind>blob|tree)/"
    r"(?P<ref>[A-Za-z0-9_.-]+)/(?P<path>[^)\s#\"'>]+)"
)


@dataclass
class Repo:
    name: str
    url: str
    branch: str
    verified_revision: str
    checkout: Path | None = None

    def git(self, *args: str) -> subprocess.CompletedProcess:
        if self.checkout is None:
            raise RuntimeError(f"no checkout for {self.name}")
        return subprocess.run(
            ["git", "-C", str(self.checkout), *args],
            capture_output=True, text=True, check=False,
        )

    def exists(self, path: str, rev: str) -> bool:
        """True when `path` (a file or a directory) exists at `rev`."""
        path = path.rstrip("/")
        return self.git("cat-file", "-e", f"{rev}:{path}").returncode == 0

    def has_revision(self, rev: str) -> bool:
        return self.git("cat-file", "-e", f"{rev}^{{commit}}").returncode == 0

    def resolve(self, rev: str) -> str | None:
        result = self.git("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
        return result.stdout.strip() or None

    def tip(self) -> str:
        """The ref the repository's current state is read from: origin/<branch>, else HEAD."""
        return f"origin/{self.branch}" if self.resolve(f"origin/{self.branch}") else "HEAD"

    def commit_date(self, rev: str) -> str:
        return self.git("show", "-s", "--format=%cs", rev).stdout.strip()


@dataclass
class Page:
    path: Path
    meta: dict
    body: str
    sources: list[tuple[str, str]] = field(default_factory=list)

    @property
    def rel(self) -> str:
        return self.path.relative_to(DOCS).as_posix()


def load_repos(checkouts: dict[str, str] | None = None) -> dict[str, Repo]:
    data = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8"))
    repos = {}
    for name, entry in data["repositories"].items():
        checkout = (checkouts or {}).get(name)
        repos[name] = Repo(
            name=name,
            url=entry["url"].rstrip("/"),
            branch=entry.get("branch", "main"),
            verified_revision=str(entry["verified_revision"]),
            checkout=Path(checkout).resolve() if checkout else None,
        )
    return repos


def parse_pairs(values: list[str], option: str = "--repo", what: str = "PATH") -> dict[str, str]:
    """Turn ["avrana-party=../avrana-party", ...] into a dict."""
    result = {}
    for value in values or []:
        name, sep, rest = value.partition("=")
        if not sep or not name or not rest:
            raise SystemExit(f"{option} expects NAME={what}, got {value!r}")
        result[name] = rest
    return result


def parse_checkouts(values: list[str]) -> dict[str, str]:
    return parse_pairs(values, "--repo", "PATH")


def split_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    meta = yaml.safe_load(text[4:end]) or {}
    return meta, text[end + 5:]


def load_pages() -> list[Page]:
    pages = []
    for path in sorted(DOCS.rglob("*.md")):
        meta, body = split_front_matter(path.read_text(encoding="utf-8"))
        page = Page(path=path, meta=meta, body=body)
        for item in meta.get("sources") or []:
            repo, sep, src = str(item).partition(":")
            page.sources.append((repo, src) if sep else ("", str(item)))
        pages.append(page)
    return pages


def links(page: Page):
    """Yield (repo, ref, path) for each link from the page into an engineering repository."""
    for match in GITHUB_LINK.finditer(page.body):
        yield match["repo"], match["ref"], match["path"]


def all_sources(page: Page, repos: dict[str, Repo]) -> set[tuple[str, str]]:
    """Declared sources plus files the page links to on a repository's tracked branch."""
    found = {(r, s) for r, s in page.sources if r}
    for repo_name, ref, path in links(page):
        repo = repos.get(repo_name)
        if repo is not None and ref == repo.branch:
            found.add((repo_name, path))
    return found
