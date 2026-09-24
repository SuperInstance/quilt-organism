"""
organism.py — the high-level walker.

Composes a corpus adapter + multiple receivers + the substrate envelope.
Walking emits one receipt per (item, receiver) pair.

The organism grows by:
  1. Walking more items
  2. Adding more receivers
  3. Composing with other substrates via LegaleseNetwork (quilt-seed)
  4. Vectorizing for similarity search
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .substrate import OrganismSubstrate, OrganismStatus
from .walkers import CorpusAdapter
from .receivers import Receiver


@dataclass
class Organism:
    """The walker — composes corpus + receivers + substrate envelope."""

    corpus: CorpusAdapter
    receivers: List[Receiver]
    cell_id: str = "organism"
    substrate: OrganismSubstrate = field(default_factory=OrganismSubstrate)

    def __post_init__(self):
        # Sync the cell_id
        if self.substrate.cell_id != self.cell_id:
            self.substrate.cell_id = self.cell_id

    def walk(self, limit: int = 10) -> dict:
        """Walk the corpus with each receiver; emit receipts.

        Returns a summary: {items_walked, receipts_emitted, by_receiver, by_polarity, canonical_items}
        """
        items = list(self.corpus.items(limit=limit))
        items_walked = 0
        by_receiver = {}
        by_polarity = {"ACCEPT": 0, "DRIFT": 0, "REFUSE": 0}

        for item_id, text in items:
            if not text or not text.strip():
                continue
            items_walked += 1
            for receiver in self.receivers:
                status, payload = receiver.receive(item_id, text)
                receipt = self.substrate.witness(
                    item_id=item_id,
                    receiver=type(receiver).__name__,
                    status=status,
                    payload=payload,
                )
                by_receiver.setdefault(type(receiver).__name__, 0)
                by_receiver[type(receiver).__name__] += 1
                by_polarity[receipt.polarity] += 1

        return {
            "items_walked": items_walked,
            "receipts_emitted": len(self.substrate.receipts),
            "by_receiver": by_receiver,
            "by_polarity": by_polarity,
            "chain_head": self.substrate.chain_head,
            "chain_intact": self.substrate.chain_intact(),
            "canonical_items": list(self.substrate.canonical_items()),
        }

    @property
    def chain_head(self) -> str:
        return self.substrate.chain_head

    @property
    def receipts(self) -> list:
        return self.substrate.receipts
