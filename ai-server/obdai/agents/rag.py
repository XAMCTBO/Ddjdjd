"""RAG agent - retrieves grounding text for the other agents.

Corpus = every markdown article in knowledge/articles (plus any extra directory
listed in OBDAI_KB_DIRS, e.g. your own service bulletins or forum notes) and
one document per DTC catalog entry. Articles are chunked by paragraph/list
block, then ranked with BM25 (pure Python, no external services). Article
`tags:` lines and DTC codes get extra weight so a code lookup reliably
surfaces the right guide.

The ranking backend is isolated in `_score` so it can be swapped for a vector
database later without touching the agents that call `search()`.
"""
from __future__ import annotations

import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from ..knowledge import dtc_catalog

ARTICLES_DIR = Path(__file__).resolve().parent.parent / "knowledge" / "articles"
TOKEN = re.compile(r"[a-z0-9]+(?:\.[0-9]+)?")
CODE = re.compile(r"\b[PCBU][0-9][0-9A-F]{3}\b", re.I)
STOP = set("a an the and or of to in on for is are be it this that with as at by from if then not no "
           "can do does my your you i me we our its into than so when what why how which".split())


def tokenize(text: str) -> list[str]:
    toks = []
    for t in TOKEN.findall(text.lower()):
        if t in STOP:
            continue
        # crude stemming: plural/verb endings so "misfires"/"misfiring" match "misfire"
        for suf in ("ing", "es", "s"):
            if len(t) > 4 and t.endswith(suf) and not CODE.fullmatch(t):
                t = t[: -len(suf)]
                break
        toks.append(t)
    return toks


@dataclass
class Chunk:
    id: str
    title: str
    source: str
    text: str
    tags: list[str] = field(default_factory=list)
    tf: Counter = field(default_factory=Counter)
    length: int = 0


class RAGAgent:
    name = "rag"
    k1, b = 1.4, 0.75

    def __init__(self, extra_dirs: list[str] | None = None):
        dirs = [ARTICLES_DIR]
        env = os.environ.get("OBDAI_KB_DIRS", "")
        dirs += [Path(d) for d in (extra_dirs or []) + [d for d in env.split(os.pathsep) if d]]
        self.chunks: list[Chunk] = []
        for d in dirs:
            if d.is_dir():
                for path in sorted(d.glob("*.md")):
                    self._add_article(path)
        self._add_catalog()
        self._index()

    # ----------------------------------------------------------------- corpus
    def _add_article(self, path: Path):
        text = path.read_text(encoding="utf-8")
        title_m = re.search(r"^#\s+(.+)$", text, re.M)
        title = title_m.group(1).strip() if title_m else path.stem
        tags_m = re.search(r"^tags:\s*(.+)$", text, re.M)
        tags = [t.strip() for t in tags_m.group(1).split(",")] if tags_m else []
        body = re.sub(r"^(#.*|tags:.*)$", "", text, flags=re.M).strip()
        blocks = [b.strip() for b in re.split(r"\n\s*\n", body) if b.strip()]
        # merge very short blocks with the next one so chunks carry context
        merged, buf = [], ""
        for blk in blocks:
            buf = f"{buf}\n{blk}".strip()
            if len(buf) > 280:
                merged.append(buf)
                buf = ""
        if buf:
            merged.append(buf)
        for i, chunk in enumerate(merged):
            self.chunks.append(Chunk(id=f"{path.stem}#{i}", title=title, source=f"article:{path.stem}",
                                     text=chunk, tags=tags))

    def _add_catalog(self):
        for code, (desc, system, sev, causes, checks, cost) in dtc_catalog.CATALOG.items():
            text = (f"{code}: {desc}. System: {dtc_catalog.SYSTEM_LABEL[system]}. Severity: {sev}. "
                    f"Likely causes: {'; '.join(causes)}. First checks: {'; '.join(checks)}.")
            self.chunks.append(Chunk(id=f"dtc:{code}", title=f"{code} {desc}", source="dtc-catalog",
                                     text=text, tags=[code]))
        for i, (codes, text) in enumerate(dtc_catalog.PATTERNS):
            self.chunks.append(Chunk(id=f"pattern:{i}", title="Code combination: " + " + ".join(sorted(codes)),
                                     source="dtc-patterns", text=text, tags=sorted(codes)))

    def _index(self):
        df: Counter = Counter()
        for c in self.chunks:
            toks = tokenize(c.title) * 2 + tokenize(" ".join(c.tags)) * 3 + tokenize(c.text)
            c.tf = Counter(toks)
            c.length = len(toks)
            df.update(set(toks))
        n = len(self.chunks)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.avg_len = sum(c.length for c in self.chunks) / max(n, 1)

    # ----------------------------------------------------------------- search
    def _score(self, q: list[str], c: Chunk) -> float:
        s = 0.0
        for t in q:
            f = c.tf.get(t)
            if not f:
                continue
            s += self.idf.get(t, 0) * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * c.length / self.avg_len))
        return s

    def search(self, query: str, k: int = 5, sources: tuple[str, ...] | None = None) -> list[dict]:
        q = tokenize(query)
        if not q:
            return []
        codes = {m.upper() for m in CODE.findall(query)}
        scored = []
        for c in self.chunks:
            if sources and not c.source.startswith(sources):
                continue
            s = self._score(q, c)
            if codes:
                tagged = codes & {t.upper() for t in c.tags}
                if c.id.startswith("dtc:") and c.id[4:] in codes:
                    s *= 3.0          # the code's own catalog entry first
                elif tagged and c.source.startswith("article"):
                    s *= 2.0          # then the guide written for it
                elif tagged:
                    s *= 1.3
            if s > 0:
                scored.append((s, c))
        scored.sort(key=lambda x: -x[0])
        return [{"id": c.id, "title": c.title, "source": c.source, "text": c.text, "score": round(s, 3)}
                for s, c in scored[:k]]

    def context(self, query: str, k: int = 5, max_chars: int = 6000) -> str:
        """Formatted, citeable context block to inject into an LLM prompt."""
        out, used = [], 0
        for hit in self.search(query, k):
            block = f'<doc id="{hit["id"]}" title="{hit["title"]}">\n{hit["text"]}\n</doc>'
            if used + len(block) > max_chars:
                break
            out.append(block)
            used += len(block)
        return "\n".join(out) or "<doc>No matching reference material.</doc>"
