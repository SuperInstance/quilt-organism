"""Tests for the scouts module."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quilt_organism.scouts import (
    Scout, Memoir, MomentumView, ScoutReport, memoirs_to_text,
)


def test_memoir_to_text():
    m = Memoir(
        agent="test-agent",
        work="test work",
        context_window="test context",
        seeds=["seed-1"],
        why="test why",
        hows=["how-1"],
        what_was_driving="driving",
        what_surprised="surprised",
    )
    text = memoirs_to_text([m])
    assert "Memoir 1: test-agent" in text
    assert "test work" in text
    assert "seed-1" in text
    assert "driving" in text


def test_scout_report_structure():
    # Build a Scout and run it (will use the live API if GITHUB_TOKEN is set)
    scout = Scout(scout_id="test-scout")
    if not os.environ.get("GITHUB_TOKEN"):
        # Skip if no token
        return
    report = scout.report(window_days=14)
    assert report.scout_id == "test-scout"
    assert len(report.memoirs) > 0
    assert isinstance(report.momentum, MomentumView)
    assert report.chain_head != ""


def test_scout_with_no_token_returns_report():
    """Even without a token, Scout returns its written memoirs."""
    scout = Scout(scout_id="no-token-scout", token="")
    report = scout.report(window_days=7)
    # Memoirs are pre-written (don't depend on API call)
    assert len(report.memoirs) >= 4
    assert any(m.agent == "Mavis" for m in report.memoirs)
    assert any(m.agent == "kimi1" for m in report.memoirs)
    assert any(m.agent == "Casey" for m in report.memoirs)
    assert any(m.agent == "Lucineer" for m in report.memoirs)
