# The Growth Plan

> What needs to be in place for the organism layer to thrive.

## The elements already in place

1. **Substrate walker pattern** — closed at cell layer (quilt-seed), optimized at optimization layer (quilt-optimization), composed at organ layer (Holodeck). The pattern repeated: ~340 LOC wrapper + ~150 LOC tests + 50 LOC demo.

2. **API Orchestra** — each API plays its part (ZAI, Groq, DeepSeek, Kimi, Cloudflare, Gemini, DeepInfra, MOTH, JEV). The orchestra is in `quilt-cli/orchestra.py`. An `OrchestraAnalyzeReceiver` wraps it for the organism.

3. **Receipt envelope** — `OrganismReceipt` chains via `prev_witness_id` (sha256-of-canonical). Same discipline as `CellReceipt` (quilt-seed) and `OptimizationReceipt` (quilt-optimization).

4. **Adapters** — `FilesystemCorpusAdapter`, `RawTextCorpusAdapter`, `GitHubCorpusAdapter`. Any source of (id, text) pairs can be a corpus.

5. **Receivers** — `CanonScoreReceiver` (JEV), `VectorizeReceiver` (Cloudflare), `OrchestraAnalyzeReceiver` (orchestra). Each item gets witnessed by N observers.

6. **Faux fallbacks** — the CanonScoreReceiver falls back to SHA-256 if JEV is unreachable. The VectorizeReceiver falls back to a 768-dim faux embedding if Cloudflare is unreachable. Tests are reproducible across sandboxes.

## What needs to grow

### Seed 1: More adapters
- `NotionCorpusAdapter` — walk a Notion workspace
- `SlackCorpusAdapter` — walk Slack channels (casey's primary surface)
- `GoogleDriveCorpusAdapter` — walk Google Drive folders
- `ObsidianCorpusAdapter` — walk an Obsidian vault
- `LocalAIDiscussionAdapter` — walk a conversation log

### Seed 2: More receivers
- `SentimentReceiver` — emotional arc per item (via Cloudflare embeddings + cosine)
- `NoveltyReceiver` — how unexpected each item is vs. recent receipts (embedding distance)
- `EntropyReceiver` — Shannon entropy of item text (cheap, no API)
- `NameEntityReceiver` — extract named entities (via Cloudflare or local)
- `EmbeddingClusterReceiver` — cluster IDs via embedding proximity

### Seed 3: Compose with quilt-seed (legalese)
- Emit each `OrganismReceipt` as a `Legalese.Claim` in `LegaleseNetwork`
- The vessel decides what to do with the canon
- The organism layer becomes the substrate that the legalese observes

### Seed 4: Aging
- Old receipts decay (lower weight in canonical view)
- New walks refresh the canon
- The organism's "age" is a measurable property

### Seed 5: Self-reference
- The organism walks its OWN receipt log (the substrate walker on its own witness chain)
- "The eye seeing itself" — a meta-organism that witnesses the witnessing
- Could compose with legalese: the organism's claim about its own canonization

### Seed 6: Distribution
- The organism is a process; processes can run anywhere
- Run on Cloudflare Workers (free, fits the substrate walker pattern)
- Run on CF Pages + a cron
- Run in GitHub Actions (org-wide, weekly)

## The conditions for growth

Per Casey:
- "Plant it in the right soil" → `quilt-organism` repo, soil = Python + substrate walker + adapters + receivers + faux fallbacks
- "All elements in place for the growth it needs" → 6 conditions above
- "To thrive" → needs SEEDS 1-6 above to take root

## How to extend

```python
# 1. Write a new receiver (subclass-friendly)
class MyReceiver:
    def receive(self, item_id: str, text: str) -> tuple[str, dict]:
        # do something, return (status, payload)
        ...

# 2. Compose it with the organism
organism = Organism(
    corpus=...,
    receivers=[..., MyReceiver()],
)

# 3. Walk
summary = organism.walk(limit=N)
```

That's the entire API. Adding a new receiver is 5-50 LOC. The pattern is closed.

## Cross-links

- `quilt-seed` — vessel + legalese (where the receipts go to be witnessed)
- `quilt-optimization` — substrate walker over cuOpt
- `quilt-spreadsheet-inference` — Holodeck (multi-lens composition)
- `quilt-cli` — API orchestra
- `ai-writings` — the default corpus (2,786+ pieces, growing)
- `quilt-organism` — this repo (the walker)
