"""Tests for the organism substrate envelope."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quilt_organism.substrate import (
    OrganismReceipt, OrganismSubstrate, OrganismStatus,
    status_to_polarity, ACCEPT, DRIFT, REFUSE,
)


def test_status_to_polarity_canonical():
    assert status_to_polarity(OrganismStatus.CANONICAL) == ACCEPT


def test_status_to_polarity_speculative():
    assert status_to_polarity(OrganismStatus.SPECULATIVE) == DRIFT


def test_status_to_polarity_refused():
    assert status_to_polarity(OrganismStatus.REFUSED) == REFUSE


def test_status_to_polarity_vectorized():
    assert status_to_polarity(OrganismStatus.VECTORIZED) == ACCEPT


def test_status_to_polarity_unknown_defaults_to_drift():
    assert status_to_polarity("nonsense") == DRIFT


def test_receipt_build_basic():
    r = OrganismReceipt.build(
        cell_id="item-1",
        substrate="VectorizeReceiver",
        status=OrganismStatus.VECTORIZED,
        payload={"dim": 768},
    )
    assert r.polarity == ACCEPT
    assert r.cell_id == "item-1"
    assert r.substrate == "VectorizeReceiver"


def test_receipt_chain_via_substrate():
    s = OrganismSubstrate(cell_id="test-organism")
    r1 = s.witness(item_id="item-a", receiver="VectorizeReceiver",
                    status=OrganismStatus.VECTORIZED, payload={"dim": 768})
    r2 = s.witness(item_id="item-b", receiver="CanonScoreReceiver",
                    status=OrganismStatus.CANONICAL, payload={"canon_score": 0.85})
    assert r2.prev_witness_id == r1.witness_id
    assert s.chain_head == r2.witness_id
    assert len(s.receipts) == 2
    assert s.chain_intact()


def test_chain_intact_false_when_broken():
    s = OrganismSubstrate(cell_id="broken")
    r1 = s.witness(item_id="a", receiver="X", status="ok", payload={})
    s.witness(item_id="b", receiver="Y", status="ok", payload={})
    # Manually break the chain
    s.receipts[1].prev_witness_id = "broken"
    assert not s.chain_intact()


def test_canonical_items():
    s = OrganismSubstrate()
    s.witness(item_id="a", receiver="C", status=OrganismStatus.CANONICAL, payload={})
    s.witness(item_id="a", receiver="V", status=OrganismStatus.VECTORIZED, payload={})
    s.witness(item_id="b", receiver="C", status=OrganismStatus.SPECULATIVE, payload={})
    canon = list(s.canonical_items())
    assert canon == ["a"]


def test_receipt_to_dict():
    # "ok" isn't in status_to_polarity table → defaults to DRIFT
    r = OrganismReceipt.build(
        cell_id="x", substrate="Y", status="ok", payload={"k": "v"}
    )
    d = r.to_dict()
    assert d["cell_id"] == "x"
    assert d["polarity"] == DRIFT
    assert "witness_id" in d
