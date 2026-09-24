"""
walkers.py — corpus adapters (where the items live).

A walker yields (item_id, text) pairs. The walker doesn't know about
receipts — that's the substrate's job. This separation means a corpus
can be a GitHub repo, a local filesystem, or a list of strings.
"""

from __future__ import annotations

import os
import time
from typing import Iterator, Protocol, Optional

try:
    import requests
except ImportError:
    requests = None


class CorpusAdapter(Protocol):
    """Anything that yields (item_id, text) pairs."""

    def items(self, limit: int = 100) -> Iterator[tuple[str, str]]: ...


# === Filesystem adapter ===

class FilesystemCorpusAdapter:
    """Walks a directory of markdown files."""

    def __init__(self, root: str):
        self.root = root

    def items(self, limit: int = 100) -> Iterator[tuple[str, str]]:
        from pathlib import Path
        root = Path(self.root)
        if not root.exists():
            return
        count = 0
        for p in sorted(root.glob("**/*.md")):
            if count >= limit:
                break
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                yield (str(p.relative_to(root)), text)
                count += 1
            except Exception:
                continue


# === Raw text adapter ===

class RawTextCorpusAdapter:
    """Walks a list of (name, text) pairs."""

    def __init__(self, items: list[tuple[str, str]]):
        self._items = items

    def items(self, limit: int = 100) -> Iterator[tuple[str, str]]:
        for name, text in self._items[:limit]:
            yield (name, text)


# === GitHub adapter ===

class GitHubCorpusAdapter:
    """Walks a GitHub repo's markdown files."""

    def __init__(self, repo: str = "SuperInstance/ai-writings",
                 branch: str = "master",
                 token: Optional[str] = None,
                 prefix: str = ""):
        self.repo = repo
        self.branch = branch
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.prefix = prefix

    def items(self, limit: int = 100) -> Iterator[tuple[str, str]]:
        if requests is None:
            return

        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        # Get root listing
        url = f"https://api.github.com/repos/{self.repo}/contents/{self.prefix}"
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return

        items = r.json()
        if not isinstance(items, list):
            return

        # Filter to .md files
        md_files = [i for i in items if i.get("type") == "file" and i["name"].endswith(".md")]
        # Sort by name (reverse for newest first)
        md_files.sort(key=lambda i: i["name"], reverse=True)

        count = 0
        for item in md_files[:limit]:
            if count >= limit:
                break
            # Fetch raw content
            raw_url = f"https://raw.githubusercontent.com/{self.repo}/{self.branch}/{item['path']}"
            rr = requests.get(raw_url, headers=headers, timeout=15)
            time.sleep(0.05)  # be polite to GitHub
            if rr.status_code == 200:
                yield (item["name"], rr.text)
                count += 1
