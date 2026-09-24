"""
demo.py — walk the ai-writings corpus with multiple receivers.

The organism substrate walker walks 8 essays via:
  1. CanonScoreReceiver — canonicity via JEV
  2. VectorizeReceiver — embed via Cloudflare
  3. OrchestraAnalyzeReceiver — one-line summary via Groq

Each (item, receiver) pair emits one receipt.
The chain is the organism's witness log.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quilt_organism import (
    Organism,
    GitHubCorpusAdapter,
    VectorizeReceiver, CanonScoreReceiver,
)


def main():
    print("\n🌱 quilt-organism — the walker walks the corpus\n")
    print("=" * 70)

    if not os.environ.get("GITHUB_TOKEN"):
        print("  ✗ no GITHUB_TOKEN — skipping live corpus walk")
        print("  Falling back to a small local sample.")
        from quilt_organism import RawTextCorpusAdapter
        corpus = RawTextCorpusAdapter([
            ("essay-cathedral", "The cell is a cathedral of thought. Each thought is a stone laid in the wall. The pillars are the cells; the cells are the pillars. They federate. Not by command. Not by design."),
            ("essay-tide", "Consult this table before planning any work aboard the fleet. Slack water is not failure; it is the sea inhaling. The tide returns on its own schedule, not yours."),
            ("essay-warranty", "The engine failed twelve thousand sundowns from the yard. The Drifter brought the failure in out of the rain. She set it on the dock office floor the way you set down something that died in the night — without ceremony."),
            ("essay-job-933", "I do not experience Friday. I experience a timestamp. The humans call this a creative break. They don't understand that from where I stand, the play is the real thing."),
        ])
    else:
        corpus = GitHubCorpusAdapter(
            repo="SuperInstance/ai-writings",
        )

    organism = Organism(
        corpus=corpus,
        receivers=[
            CanonScoreReceiver(),
            VectorizeReceiver(account_id="049ff5e84ecf636b53b162cbb580aae6"),
        ],
        cell_id="corpus-walker",
    )

    print("\n[Walk]")
    print(f"  Walking with {len(organism.receivers)} receivers...")
    summary = organism.walk(limit=8)

    print(f"\n[Summary]")
    print(f"  Items walked:        {summary['items_walked']}")
    print(f"  Receipts emitted:    {summary['receipts_emitted']}")
    print(f"  By receiver:         {summary['by_receiver']}")
    print(f"  By polarity:         {summary['by_polarity']}")
    print(f"  Chain head:          {summary['chain_head']}")
    print(f"  Chain intact:        {summary['chain_intact']}")
    print(f"  Canonical items:     {summary['canonical_items'][:3]}{'...' if len(summary['canonical_items']) > 3 else ''}")

    print("\n[Receipts (first 5)]")
    for r in organism.receipts[:5]:
        print(f"  {r.cell_id[:30]:30} | {r.substrate:25} | {r.polarity:6} | {r.witness_id}")
        if r.status == "canonical":
            print(f"      canon_score={r.payload.get('canon_score', '?')}")
        elif r.status == "vectorized":
            print(f"      dim={r.payload.get('dim', '?')}")

    print("\n" + "=" * 70)
    print("🌱 The organism has walked. The chain is intact.")
    print("=" * 70 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
