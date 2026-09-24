"""
receivers.py — what the walker does with each corpus item.

Each receiver takes (item_id, text) and returns (status, payload).
The substrate wraps that into an OrganismReceipt.

Three first-class receivers:
  - VectorizeReceiver: embed via Cloudflare bge-base-en-v1.5
  - CanonScoreReceiver: canonicity via JEV (or faux SHA-256 fallback)
  - OrchestraAnalyzeReceiver: ask the API orchestra for a one-line analysis
"""

from __future__ import annotations

import hashlib
import os
import time
from typing import Protocol

try:
    import requests
except ImportError:
    requests = None

from .substrate import OrganismStatus


class Receiver(Protocol):
    """Anything that takes (item_id, text) and returns (status, payload)."""

    def receive(self, item_id: str, text: str) -> tuple[str, dict]: ...


# === Vectorize via Cloudflare Workers AI ===

class VectorizeReceiver:
    """Embed text via Cloudflare's bge-base-en-v1.5 (768 dims, free, fast).

    Falls back to a SHA-256 faux embedding if Cloudflare is unreachable.
    """

    def __init__(self, account_id: str = "",
                 model: str = "@cf/baai/bge-base-en-v1.5"):
        self.account_id = account_id or os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
        self.model = model

    def receive(self, item_id: str, text: str) -> tuple[str, dict]:
        if requests is None or not self.account_id or not os.environ.get("CLOUDFLARE_TOKEN"):
            # Faux embedding: SHA-256 → 768-bit vector (padded with zeros)
            h = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
            # 32 bytes → 768 dims by tiling + sign bit
            faux = []
            for i in range(768):
                byte = h[i % 32]
                bit = (byte >> (i % 8)) & 1
                faux.append(float(bit * 2 - 1))
            return OrganismStatus.WITNESSED, {
                "model": "faux-sha256",
                "dim": 768,
                "head5": faux[:5],
            }

        try:
            url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/@cf/baai/bge-base-en-v1.5"
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {os.environ['CLOUDFLARE_TOKEN']}",
                         "Content-Type": "application/json"},
                json={"text": [text[:1500]]},
                timeout=20,
            )
            if r.status_code == 200:
                data = r.json().get("result", {}).get("data", [])
                if data:
                    emb = data[0]
                    return OrganismStatus.VECTORIZED, {
                        "model": self.model,
                        "dim": len(emb),
                        "head5": emb[:5],
                    }
            return OrganismStatus.EMBEDDING_FAILED, {"http_status": r.status_code}
        except Exception as e:
            return OrganismStatus.EMBEDDING_FAILED, {"error": str(e)[:200]}


# === Canon score via JEV ===

class CanonScoreReceiver:
    """Score canonicity of an item via JEV oracle.

    JEV API is at api.typesafe.ai/v1/evaluate.
    Falls back to faux SHA-256 score if unreachable.
    """

    def __init__(self, threshold_canonical: float = 0.7,
                 threshold_speculative: float = 0.3):
        self.threshold_canonical = threshold_canonical
        self.threshold_speculative = threshold_speculative

    def receive(self, item_id: str, text: str) -> tuple[str, dict]:
        score = self._call_jev(text[:800])
        if score >= self.threshold_canonical:
            status = OrganismStatus.CANONICAL
        elif score >= self.threshold_speculative:
            status = OrganismStatus.SPECULATIVE
        else:
            status = OrganismStatus.REFUSED
        return status, {
            "canon_score": round(score, 4),
            "threshold_canonical": self.threshold_canonical,
            "threshold_speculative": self.threshold_speculative,
        }

    def _call_jev(self, text: str) -> float:
        if requests is None:
            return self._faux_score(text)
        api_key = os.environ.get("TYPESAFEAI_KEY")
        if not api_key:
            return self._faux_score(text)
        try:
            r = requests.post(
                "https://api.typesafe.ai/v1/evaluate",
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json"},
                json={
                    "question": "Is this a canon piece?",
                    "text": text,
                    "criteria": {
                        "true": "the piece is canon — well-established, true to the project's culture, or part of the official canon",
                        "false": "the piece is speculative, a draft, an experiment, or not canon",
                    },
                },
                timeout=15,
            )
            if r.status_code == 200:
                d = r.json()
                return d.get("probability", d.get("score", 0.5))
        except Exception:
            pass
        return self._faux_score(text)

    def _faux_score(self, text: str) -> float:
        """Deterministic 0..1 from SHA-256 (used when JEV is unreachable)."""
        h = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
        return int.from_bytes(h[:4], "big") / 0xFFFFFFFF


# === Orchestra analysis ===

class OrchestraAnalyzeReceiver:
    """Ask the API orchestra to analyze an item in one line.

    Routes to the right API per task type (default: 'bootstrap' for terse summary).
    """

    def __init__(self, task: str = "bootstrap", **orchestra_kwargs):
        self.task = task
        self.orchestra_kwargs = orchestra_kwargs
        self._orchestra = None

    def _get_orchestra(self):
        if self._orchestra is None:
            from quilt_cli.orchestra import Orchestra
            self._orchestra = Orchestra(**self.orchestra_kwargs)
        return self._orchestra

    def receive(self, item_id: str, text: str) -> tuple[str, dict]:
        try:
            orch = self._get_orchestra()
            receipt = orch.call(
                self.task,
                f"In one sentence, what is this piece about?\n\n{text[:600]}",
                max_tokens=80,
            )
            return OrganismStatus.ANALYZED, {
                "task": self.task,
                "api": receipt.api,
                "model": receipt.model,
                "latency_ms": receipt.latency_ms,
                "summary": receipt.response[:200],
                "polarity": receipt.polarity,
            }
        except Exception as e:
            return OrganismStatus.ORACLE_UNREACHABLE, {"error": str(e)[:200]}
