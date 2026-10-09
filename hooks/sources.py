"""MkDocs hook: make each page's traceability visible to readers.

* Appends a collapsed "Canonical sources" block to every page that declares `sources` in its
  front matter, linking each REPO:PATH to the engineering repository and stating the revision
  and date the page was verified against (from sources.yml).
* Replaces the marker <!-- source-revisions --> with a table generated from sources.yml, so the
  recorded revisions are written down in exactly one place.
"""
from __future__ import annotations

from pathlib import Path

import yaml

_REPOS: dict = {}
MARKER = "<!-- source-revisions -->"


def on_config(config, **kwargs):
    path = Path(config["config_file_path"]).parent / "sources.yml"
    _REPOS.clear()
    _REPOS.update(yaml.safe_load(path.read_text(encoding="utf-8"))["repositories"])
    return config


def _link(repo: str, path: str) -> str:
    entry = _REPOS.get(repo)
    if entry is None:
        return f"`{repo}:{path}`"
    kind = "tree" if path.endswith("/") or "." not in path.rsplit("/", 1)[-1] else "blob"
    url = f"{entry['url'].rstrip('/')}/{kind}/{entry.get('branch', 'main')}/{path.rstrip('/')}"
    return f"[`{repo}/{path}`]({url})"


def _revisions_table() -> str:
    rows = ["| Repository | Revision | Reconciled on |", "|---|---|---|"]
    for name, entry in _REPOS.items():
        url = entry["url"].rstrip("/")
        sha = str(entry["verified_revision"])
        rows.append(f"| [`{name}`]({url}) | [`{sha[:7]}`]({url}/commit/{sha}) "
                    f"| {entry.get('verified_on', '')} |")
    return "\n".join(rows)


def on_page_markdown(markdown, page, **kwargs):
    if MARKER in markdown:
        markdown = markdown.replace(MARKER, _revisions_table())
    sources = page.meta.get("sources") or []
    if not sources:
        return markdown
    repos_used = []
    lines = []
    for item in sources:
        repo, _, path = str(item).partition(":")
        lines.append(f"    - {_link(repo, path)}")
        if repo not in repos_used:
            repos_used.append(repo)
    revisions = ", ".join(
        f"`{r}` at `{str(_REPOS[r]['verified_revision'])[:7]}`" for r in repos_used if r in _REPOS)
    verified = page.meta.get("verified", "unknown")
    block = [
        "",
        "",
        '??? quote "Canonical sources for this page"',
        "",
        f"    This page explains the engineering sources below, which remain authoritative. "
        f"Last checked on {verified} against {revisions}. Links point to the current `main`, "
        f"which may have moved on since.",
        "",
        *lines,
        "",
    ]
    return markdown.rstrip() + "\n".join(block)
