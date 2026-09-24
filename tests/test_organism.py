"""Tests for the high-level Organism walker."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quilt_organism import (
    Organism, RawTextCorpusAdapter, VectorizeReceiver, CanonScoreReceiver,
)


def test_organism_with_raw_text():
    corpus = RawTextCorpusAdapter([
        ("essay-1", "The cell is a cathedral of thought."),
        ("essay-2", "Sometimes the substrate makes secrets legible."),
        ("essay-3", ""),  # empty — should be skipped
    ])

    # Use faux-fallback receivers (no env keys needed)
    org = Organism(
        corpus=corpus,
        receivers=[
            CanonScoreReceiver(),
            # Skip VectorizeReceiver since Cloudflare requires setup
        ],
        cell_id="test-organism",
    )

    summary = org.walk(limit=10)

    assert summary["items_walked"] == 2  # empty skipped
    assert summary["receipts_emitted"] == 2  # 2 items × 1 receiver
    assert summary["chain_intact"] is True
    assert "CanonScoreReceiver" in summary["by_receiver"]


def test_organism_chains_receipts():
    corpus = RawTextCorpusAdapter([
        ("a", "X" * 100),
        ("b", "Y" * 100),
        ("c", "Z" * 100),
    ])
    org = Organism(
        corpus=corpus,
        receivers=[CanonScoreReceiver()],
        cell_id="chain-test",
    )
    org.walk(limit=10)
    assert len(org.receipts) == 3
    # Each receipt's prev_witness_id matches the previous receipt's witness_id
    for i in range(1, len(org.receipts)):
        assert org.receipts[i].prev_witness_id == org.receipts[i-1].witness_id


def test_organism_with_multiple_receivers():
    corpus = RawTextCorpusAdapter([("x", "test text")])
    org = Organism(
        corpus=corpus,
        receivers=[CanonScoreReceiver()],
        cell_id="multi-test",
    )
    org.walk(limit=10)
    # Only one receiver → one receipt
    assert len(org.receipts) == 1


def test_organism_handles_empty_corpus():
    corpus = RawTextCorpusAdapter([])
    org = Organism(corpus=corpus, receivers=[CanonScoreReceiver()])
    summary = org.walk(limit=10)
    assert summary["items_walked"] == 0
    assert summary["receipts_emitted"] == 0
    assert summary["chain_intact"] is True


def test_organism_summary_fields():
    corpus = RawTextCorpusAdapter([
        ("a", "canon piece"),
        ("b", "speculative"),
    ])
    org = Organism(corpus=corpus, receivers=[CanonScoreReceiver()])
    summary = org.walk(limit=10)

    assert "items_walked" in summary
    assert "receipts_emitted" in summary
    assert "by_receiver" in summary
    assert "by_polarity" in summary
    assert "chain_head" in summary
    assert "chain_intact" in summary
    assert "canonical_items" in summary
