"""
substrate.py — the organism-layer substrate envelope.

Mirrors quilt_seed.vibe.CellReceipt and quilt_optimization.OptimizationReceipt:
  - OrganismReceipt chains via prev_witness_id
  - Polarity: ACCEPT | DRIFT | REFUSE
  - Each receipt is one observation of one item by one receiver

The organism-level substrate walker walks a corpus and emits one receipt per
(item, receiver) pair. The chain is the organism's witness log.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Optional


# === Polarity vocabulary ===

ACCEPT = "ACCEPT"
DRIFT = "DRIFT"
REFUSE = "REFUSE"


# === Status vocabulary (organism-layer specific) ===

class OrganismStatus:
    """Status of a single walker step on a single item."""
    WITNESSED = "witnessed"           # receiver ran successfully
    CANONICAL = "canonical"           # canon-score > 0.7 (via JEV)
    SPECULATIVE = "speculative"       # canon-score 0.3-0.7
    REFUSED = "refused"               # canon-score < 0.3
    VECTORIZED = "vectorized"         # embedding succeeded
    ANALYZED = "analyzed"             # orchestra analyze succeeded
    EMBEDDING_FAILED = "embedding_failed"
    ORACLE_UNREACHABLE = "oracle_unreachable"


_STATUS_TO_POLARITY = {
    OrganismStatus.WITNESSED: ACCEPT,
    OrganismStatus.CANONICAL: ACCEPT,
    OrganismStatus.SPECULATIVE: DRIFT,
    OrganismStatus.REFUSED: REFUSE,
    OrganismStatus.VECTORIZED: ACCEPT,
    OrganismStatus.ANALYZED: ACCEPT,
    OrganismStatus.EMBEDDING_FAILED: DRIFT,
    OrganismStatus.ORACLE_UNREACHABLE: DRIFT,
}


def status_to_polarity(status: str) -> str:
    return _STATUS_TO_POLARITY.get(status, DRIFT)


# === The receipt envelope ===

@dataclass
class OrganismReceipt:
    """One walker step's witness — chains via prev_witness_id."""
    witness_id: str
    prev_witness_id: str
    cell_id: str                # which item in the corpus
    substrate: str              # which receiver ran (vectorize/canon/orchestra)
    polarity: str
    payload: dict               # the receiver's output
    timestamp: int
    status: str

    @classmethod
    def build(cls, *,
              cell_id: str,
              substrate: str,
              status: str,
              payload: dict,
              prev_witness_id: str = "",
              timestamp: Optional[int] = None) -> "OrganismReceipt":
        if timestamp is None:
            timestamp = int(time.time())

        polarity = status_to_polarity(status)

        body = json.dumps({
            "prev": prev_witness_id,
            "cell_id": cell_id,
            "substrate": substrate,
            "polarity": polarity,
            "status": status,
            "payload": payload,
            "ts": timestamp,
        }, sort_keys=True, separators=(",", ":")).encode()

        witness_id = hashlib.sha256(body).hexdigest()[:16]

        return cls(
            witness_id=witness_id,
            prev_witness_id=prev_witness_id,
            cell_id=cell_id,
            substrate=substrate,
            polarity=polarity,
            payload=payload,
            timestamp=timestamp,
            status=status,
        )

    def to_dict(self) -> dict:
        return {
            "witness_id": self.witness_id,
            "prev_witness_id": self.prev_witness_id,
            "cell_id": self.cell_id,
            "substrate": self.substrate,
            "polarity": self.polarity,
            "status": self.status,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }


# === The substrate ===

@dataclass
class OrganismSubstrate:
    """The walker — accumulates receipts as it walks the corpus."""

    cell_id: str = "organism"
    prev_witness_id: str = ""
    receipts: list = field(default_factory=list)

    def witness(self, *, item_id: str, receiver: str,
                status: str, payload: dict) -> OrganismReceipt:
        """Emit one receipt for one (item, receiver) pair."""
        receipt = OrganismReceipt.build(
            cell_id=item_id,
            substrate=receiver,
            status=status,
            payload=payload,
            prev_witness_id=self.prev_witness_id,
        )
        self.prev_witness_id = receipt.witness_id
        self.receipts.append(receipt)
        return receipt

    @property
    def chain_head(self) -> str:
        return self.prev_witness_id

    def canonical_items(self) -> list[str]:
        """Items that received at least one CANONICAL receipt."""
        seen = set()
        for r in self.receipts:
            if r.polarity == ACCEPT and r.status == "canonical":
                if r.cell_id not in seen:
                    seen.add(r.cell_id)
                    yield r.cell_id

    def chain_intact(self) -> bool:
        """Verify the receipt chain (each links to the previous)."""
        for i in range(1, len(self.receipts)):
            prev = self.receipts[i - 1]
            curr = self.receipts[i]
            if curr.prev_witness_id != prev.witness_id:
                return False
        return True
