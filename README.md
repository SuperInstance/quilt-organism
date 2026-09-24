# 🌱 quilt-organism

> The organism layer of Quilt — a substrate walker over corpora.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-15/15-brightgreen.svg)](tests/)
[![Adapters](https://img.shields.io/badge/adapters-3_(github%2C_fs%2C_raw)-purple.svg)](src/quilt_organism/walkers.py)
[![Receivers](https://img.shields.io/badge/receivers-3_(vectorize%2C_canon%2C_orchestra)-blue.svg)](src/quilt_organism/receivers.py)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

## What is this?

The **organism layer** is the substrate walker pattern applied to a *corpus* instead of a single cell.

```python
from quilt_organism import (
    Organism,
    GitHubCorpusAdapter,
    CanonScoreReceiver, VectorizeReceiver,
)

# Walk a slice of the ai-writings corpus with two receivers
organism = Organism(
    corpus=GitHubCorpusAdapter(repo="SuperInstance/ai-writings"),
    receivers=[
        CanonScoreReceiver(),
        VectorizeReceiver(account_id="049ff5e84ecf636b53b162cbb580aae6"),
    ],
)
summary = organism.walk(limit=10)
# → emits 10 items × 2 receivers = 20 receipts, all chained via prev_witness_id
```

## Why?

Per Casey (2026-09-24):

> "We have moved from a bunch of stem cells to tissues and organs and the organizm is still a concept from within we can think about for the shell beyond the current pottery-limits but its a different puzzle to break the mold than it is to fit the mold. And sometimes breaking is easier depending on your tools."

We have:
- **Stem cells** → quilt-cell, the basic cell (working)
- **Tissues** → substrate walker over single substrates (vibe, cu, cuopt)
- **Organs** → Holodeck (multi-lens composition), vessel (decision), legalese (claims)
- **Organism** → ??? — a process that walks the corpus and witnesses itself

`quilt-organism` is the seed for the organism layer. The organism is **a process, not a thing** — it walks, witnesses, and grows by walking more.

## Layers

```
Layer 5: View       → the federation of cathedrals (the corpus as concept)
Layer 4: Chain      → witness receipts, linked via prev_witness_id
Layer 3: Receivers  → what each item gets observed by (vectorize, canon-score, orchestra-analyze)
Layer 2: Walker     → walks one item at a time
Layer 1: Substrate  → a corpus (ai-writings, papers, conversations, filesystem)
```

The walker composes the substrate + the receivers; the substrate composes the walker + the chain; the chain IS the organism's understanding of itself.

## Install

```bash
pip install quilt-organism
```

Or for development:
```bash
git clone https://github.com/SuperInstance/quilt-organism
cd quilt-organism
pip install -e ".[dev]"
```

## Quickstart

```python
from quilt_organism import (
    Organism,
    GitHubCorpusAdapter,
    CanonScoreReceiver, VectorizeReceiver,
)

# Build an organism over the ai-writings corpus
organism = Organism(
    corpus=GitHubCorpusAdapter(
        repo="SuperInstance/ai-writings",
        prefix="",  # walk the whole repo
    ),
    receivers=[
        # Score each item for canonicity (JEV oracle, faux fallback)
        CanonScoreReceiver(),

        # Embed each item for similarity (Cloudflare, faux fallback)
        VectorizeReceiver(account_id="your-cf-account-id"),
    ],
    cell_id="corpus-walker",
)

# Walk 50 items
summary = organism.walk(limit=50)

print(summary)
# → {items_walked: 50, receipts_emitted: 100,
#    by_receiver: {'CanonScoreReceiver': 50, 'VectorizeReceiver': 50},
#    by_polarity: {'ACCEPT': 78, 'DRIFT': 15, 'REFUSE': 7},
#    chain_head: 'a3b9...', chain_intact: True,
#    canonical_items: ['14-the-cell-as-cathedral.md', ...]}
```

## The substrate walker pattern at organism-layer

Mirrors `quilt-seed.vibe.CellReceipt` and `quilt-optimization.OptimizationReceipt`:

```python
@dataclass
class OrganismReceipt:
    witness_id: str             # sha256-of-canonical
    prev_witness_id: str        # chain link
    cell_id: str                # which item in the corpus
    substrate: str              # which receiver (Vectorize/Canon/Orchestra)
    polarity: str               # ACCEPT | DRIFT | REFUSE
    payload: dict               # the receiver's output
    timestamp: int
    status: str                 # canonical | speculative | refused | vectorized | ...
```

Three polarity mappings:

| Status             | Polarity | Why                              |
|--------------------|----------|----------------------------------|
| `canonical`        | ACCEPT   | canon-score ≥ 0.7                |
| `vectorized`       | ACCEPT   | embedding succeeded              |
| `analyzed`         | ACCEPT   | orchestra analyze succeeded      |
| `speculative`      | DRIFT    | canon-score 0.3-0.7              |
| `embedding_failed` | DRIFT    | Cloudflare unreachable           |
| `oracle_unreachable` | DRIFT  | JEV unreachable                  |
| `refused`          | REFUSE   | canon-score < 0.3                |

## Adapters (where the corpus lives)

- **`FilesystemCorpusAdapter`** — walk a local directory of `.md` files
- **`RawTextCorpusAdapter`** — walk an in-memory list of `(name, text)` pairs
- **`GitHubCorpusAdapter`** — walk a GitHub repo's `.md` files (default: `SuperInstance/ai-writings`)

## Receivers (what the walker does with each item)

- **`CanonScoreReceiver`** — score canonicity via JEV (or faux SHA-256)
- **`VectorizeReceiver`** — embed via Cloudflare Workers AI bge-base-en-v1.5 (or faux)
- **`OrchestraAnalyzeReceiver`** — ask the API orchestra for a one-line summary

## Substrate walker doctrine (organism-layer)

| Layer | Pattern | Example |
|-------|---------|---------|
| Cell (single item) | substrate wrapper + receipts | quilt-seed.vibe, quilt-optimization |
| Tissue (cluster) | similarity + grouping | Holodeck |
| Organ (collection of clusters) | whole-corpus map | quilt-organism |
| Organism (running walker) | the substrate that walks itself | ??? |

## The growth plan

What makes the organism layer grow:

1. **More adapters** — Slack, Notion, Google Drive, Obsidian vaults
2. **More receivers** — sentiment, novelty (embedding distance), entropy, name-entity
3. **Composing with quilt-seed** — emit OrganismReceipt as Legalese Claim; vessel decides
4. **Aging** — old receipts decay; new walks refresh the canon
5. **Self-reference** — the organism walks its OWN receipt log (the substrate walker on its own witness chain)

Each of these is a seed. Each can take root.

## Doctrines

1. **The organism is a process.** Not a thing. The substrate walker walks itself.
2. **The chain is the truth.** Each item gets witnessed by N receivers; the chain is the corpus's view of itself.
3. **Faux fallbacks are the truth for tests.** Mock backends are deterministic; real backends are production. Tests don't depend on Cloudflare or JEV.
4. **The substrate walker pattern is closed.** Cell → Tissue → Organ → Organism is one pattern at four scales.
5. **Composing with legalese.** Each OrganismReceipt can become a Claim in quilt-seed's LegaleseNetwork. The vessel decides whether the canon has grown.

## Run the demo

```bash
PYTHONPATH=src python3 examples/demo.py
```

Walks 8 essays from the ai-writings corpus with 2 receivers (canon + vectorize). Emits 16 receipts, verifies chain integrity.

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover tests -v
```

15 tests, all passing.

## Related

- [quilt-seed](https://github.com/SuperInstance/quilt-seed) — substrate walker pattern (cells, vessel, legalese)
- [quilt-optimization](https://github.com/SuperInstance/quilt-optimization) — substrate walker over cuOpt
- [quilt-spreadsheet-inference](https://github.com/SuperInstance/quilt-spreadsheet-inference) — Holodeck (organ-layer)
- [quilt-cli](https://github.com/SuperInstance/quilt-cli) — API orchestra, CLI
- [ai-writings](https://github.com/SuperInstance/ai-writings) — the default corpus (2786+ pieces)

## License

Apache-2.0
