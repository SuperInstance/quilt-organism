"""
quilt-organism — the organism layer of Quilt.

Per Casey (2026-09-24):
  "we have moved from a bunch of stem cells to tissues and organs
   and the organizm is still a concept from within we can think about
   for the shell beyond the current pottery-limits but its a different
   puzzle to break the mold than it is to fit the mold."

The organism layer is a substrate walker over a corpus:
  - It walks (reads N essays / files / fragments)
  - It witnesses each one via the API orchestra
  - It composes the receipts into a canon chain
  - The chain IS the organism's understanding of itself

Layers:
  Layer 1: Substrate (a corpus — ai-writings, papers, conversations)
  Layer 2: Walker (walks one item at a time)
  Layer 3: Receivers (vectorize via Cloudflare, canon-score via JEV, analyze via orchestra)
  Layer 4: Chain (the witness receipts, linked)
  Layer 5: View (the federation of cathedrals — the corpus as concept)

Maps to:
  - Cells (single item) → substrate walker pattern
  - Tissues (cluster of similar items) → top-N similar pairs
  - Organs (collection of clusters) → the whole corpus map
  - Organism (the running walker) → the substrate that walks itself

This is the seed for an organism: not a static object, but a process that
walks, witnesses, and grows. The "elements in place for growth":
  1. Substrate walker pattern (closed)
  2. API orchestra (each instrument plays its part)
  3. Receipt envelope (substrate walker compatible)
  4. Adapters for any corpus (GitHub, filesystem, raw)
  5. Composable with quilt-seed's legalese (the vessel decides)
"""

from .substrate import (
    OrganismReceipt, OrganismStatus, OrganismSubstrate,
    ACCEPT, DRIFT, REFUSE,
    status_to_polarity,
)
from .walkers import (
    GitHubCorpusAdapter, FilesystemCorpusAdapter, RawTextCorpusAdapter,
)
from .receivers import (
    VectorizeReceiver, CanonScoreReceiver, OrchestraAnalyzeReceiver,
)
from .organism import Organism

__all__ = [
    # Substrate (the walker envelope)
    "OrganismReceipt", "OrganismStatus", "OrganismSubstrate",
    "ACCEPT", "DRIFT", "REFUSE", "status_to_polarity",
    # Adapters (where the corpus lives)
    "GitHubCorpusAdapter", "FilesystemCorpusAdapter", "RawTextCorpusAdapter",
    # Receivers (what the walker does with each item)
    "VectorizeReceiver", "CanonScoreReceiver", "OrchestraAnalyzeReceiver",
    # The whole organism
    "Organism",
]

__version__ = "0.1.0"
