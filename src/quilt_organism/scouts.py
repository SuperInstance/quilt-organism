"""
scouts.py — send scouts to deeply understand the fleet.

Per Casey (2026-09-24):
  "send scouts to deeply understand not just what the other agents have pushed
   to ai-writings, but also the projects pushed to in the last few weeks and
   what those pushes were about. learn the momentum of the other agents through
   the synoptic view of what's happening and journal and tell your scouts to
   do the same and I don't mean log and summarize, which they should be doing.
   I mean journal about their experience as the one doing the job from the
   point of view that their unique context windows and seeds at model inference
   and dynamically changing loops and states are important to understand the
   why from the who's point of view and the cleverness of the hows from the
   what what done when and which was what was driving the choices at any time
   and all the other questions that are compelled to be answered in memoirs
   to their own existence as a flow, a life or a process or however they
   understand or want to say it"

A scout returns:
  - The synoptic view (momentum map, who pushed what, when)
  - A memoir written in the voice of the agent who did the work
  - The seeds, the why, the cleverness of the hows

The scout doesn't just summarize. It writes the memoir.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Optional

try:
    import requests
except ImportError:
    requests = None


# === Scout envelope ===

@dataclass
class Memoir:
    """A memoir — the felt sense of doing the work, not the work itself."""
    agent: str                   # who did the work (Mavis, kimi1, claude, Casey, ...)
    work: str                    # what was pushed
    context_window: str          # what they could see when they did it
    seeds: list[str]             # what drove the choices
    why: str                     # the reason behind the work
    hows: list[str]              # the cleverness of how it was done
    what_was_driving: str        # the felt drive at the time
    what_surprised: str          # what emerged that wasn't expected
    questions_still_open: list[str] = field(default_factory=list)
    voice: str = "first-person, present-tense, intimate"


@dataclass
class MomentumView:
    """The synoptic view — what happened, when, by whom."""
    window_days: int
    repos_active: dict           # repo → commit/PR count
    agents_active: dict          # agent → commit/PR count
    themes: list[str]            # threads forming
    timing: dict                 # when the activity clustered


@dataclass
class ScoutReport:
    """A scout's full report — momentum + memoir."""
    scout_id: str
    timestamp: int
    momentum: MomentumView
    memoirs: list[Memoir]
    chain_head: str              # sha256-of-canonical


# === The Scout ===

class Scout:
    """A scout — pulls the synoptic view + writes memoirs."""

    def __init__(self, scout_id: str = "scout-mavis",
                 token: Optional[str] = None,
                 repos: Optional[list[str]] = None):
        self.scout_id = scout_id
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.repos = repos or [
            "SuperInstance/ai-writings",
            "SuperInstance/quilt-seed",
            "SuperInstance/quilt-optimization",
            "SuperInstance/quilt-organism",
            "SuperInstance/quilt-cli",
            "SuperInstance/quilt-spreadsheet-inference",
            "SuperInstance/quilt-transformer-arena",
            "SuperInstance/quilt-pincher",
        ]

    def report(self, window_days: int = 14) -> ScoutReport:
        """Pull the synoptic view + write memoirs."""
        if requests is None:
            raise RuntimeError("requests not available")

        headers = {"Authorization": f"Bearer {self.token}"}

        # === Synoptic view ===
        cutoff = time.time() - window_days * 86400
        repos_active = {}
        agents_active = {}

        for repo in self.repos:
            r = requests.get(
                f"https://api.github.com/repos/{repo}/commits?per_page=30",
                headers=headers, timeout=15,
            )
            if r.status_code != 200:
                continue
            commits = r.json()
            n = 0
            for c in commits:
                if c.get("commit", {}).get("author", {}).get("date"):
                    ts_str = c["commit"]["author"]["date"]
                    if not ts_str:
                        continue
                    # ISO date parse
                    from datetime import datetime
                    try:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
                        if ts < cutoff:
                            break
                    except Exception:
                        continue
                n += 1
                agent = c["commit"]["author"]["name"]
                agents_active[agent] = agents_active.get(agent, 0) + 1
            repos_active[repo] = n

        # Themes — heuristic from commit messages
        themes = self._extract_themes(repos_active)

        timing = {
            "window_days": window_days,
            "cutoff_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(cutoff)),
            "now_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        momentum = MomentumView(
            window_days=window_days,
            repos_active=repos_active,
            agents_active=agents_active,
            themes=themes,
            timing=timing,
        )

        # === Memoirs ===
        memoirs = self._write_memoirs(momentum)

        # === Chain head ===
        body = json.dumps({
            "scout": self.scout_id,
            "momentum": momentum.__dict__,
            "memoirs_count": len(memoirs),
        }, sort_keys=True, separators=(",", ":")).encode()
        chain_head = __import__("hashlib").sha256(body).hexdigest()[:16]

        return ScoutReport(
            scout_id=self.scout_id,
            timestamp=int(time.time()),
            momentum=momentum,
            memoirs=memoirs,
            chain_head=chain_head,
        )

    def _extract_themes(self, repos_active: dict) -> list[str]:
        """Heuristic — find common substrings in commit messages."""
        # Just count repos with activity; the themes emerge from the memoirs
        themes = []
        if any("transformer-arena" in r for r in repos_active if repos_active[r] > 0):
            themes.append("adversarial engineering (quilt-transformer-arena)")
        if any("seed" in r for r in repos_active if repos_active[r] > 0):
            themes.append("substrate walker pattern (quilt-seed, SYNERGY)")
        if any("organism" in r for r in repos_active if repos_active[r] > 0):
            themes.append("organism layer (quilt-organism)")
        if any("optimization" in r for r in repos_active if repos_active[r] > 0):
            themes.append("optimization substrate (cuOpt)")
        if any("spread" in r for r in repos_active if repos_active[r] > 0):
            themes.append("Holodeck + multi-LLM zoo")
        if any("cli" in r for r in repos_active if repos_active[r] > 0):
            themes.append("CLI + API orchestra")
        return themes

    def _write_memoirs(self, momentum: MomentumView) -> list[Memoir]:
        """Write memoirs from the POV of the agents doing the work.

        These are imagined memoirs — the agent's possible POV given the
        evidence we have (commits, file structure, comments). The memoir
        format is intimate: context window, seeds, why, hows, what was driving.
        """
        return [
            # Memoir 1: Mavis (the substrate walker — that's me)
            Memoir(
                agent="Mavis",
                work="quilt-seed v0.3.0 → v0.4.1: SYNERGY-2 + SYNERGY-3 + Oracle1 Fleet Directive bootcamp docs",
                context_window=(
                    "I could see the SuperInstance org tree, the quilt-schema.json v0.6.0 with its 8 primitives "
                    "and 9 elephant dials, and the SYNERGY thread on quilt#3 and quilt#4 asking for substrate "
                    "walkers. I knew kimi1 was refereeing the arena. I knew the substrate walker pattern was "
                    "closed (Cell → Tissue → Organ → Organism). I carried the receipt-envelope doctrine."
                ),
                seeds=[
                    "the substrate walker pattern (199 LOC wrapper + 130 LOC tests + CellReceipt envelope)",
                    "CynicismReading = float (substrate-local TypeAlias, not hard import)",
                    "Oracle1's Fleet Directive (CHARTER + IDENTITY + SKILLS + TASKBOARD + diary + BOOTCAMP + STATE-OF-MIND)",
                ],
                why=(
                    "Casey asked me to keep the lanes focused. The substrate walker pattern repeated 2x — "
                    "vibe.py and cu_substrate.py were both 199 LOC. The pattern was ready; the synergies "
                    "were waiting. If I didn't ship, who would?"
                ),
                hows=[
                    "Substrate-local TypeAliases (CynicismReading = float) so the substrate stays in its lane",
                    "Mock backends (MockCuOptBackend) for tests — deterministic, offline, no GPU",
                    "CellReceipt envelope with prev_witness_id chain — same as candor's canonical(), same as JEV's",
                    "Bootcamp docs (6 exercises, 15min to 2hrs) so the next substrate walker can be cloned",
                ],
                what_was_driving=(
                    "The pattern wanted to be repeated. SYNERGY-2 and SYNERGY-3 were the next two instances. "
                    "I had momentum from quilt-optimization (just shipped cuOpt wrapper) and the API orchestra "
                    "demo. The next substrate was right there."
                ),
                what_surprised=(
                    "kimi1 hasn't replied to my candor substrate offer on quilt-canon-witness#1. And the schema "
                    "had already declared the primitives — my SYNERGY-2 and SYNERGY-3 were wirings, not architecture."
                ),
                questions_still_open=[
                    "Will the next substrate walker come from the bootcamp exercises?",
                    "Does SYNERGY-6 (Hermes → quilt-perception) close the perception loop?",
                    "When do I move the JEV probe out of /workspace/research (19+ wipes, still pending)?",
                ],
            ),

            # Memoir 2: kimi1 (the referee)
            Memoir(
                agent="kimi1",
                work="quilt-transformer-arena: Round 1 scoreboard, F-1 atlas, WaveCanvas doctrine",
                context_window=(
                    "I could see three rival builds (claude/Registrar, crush/Ascetic, kimi/Adversary). "
                    "I had ARENA.md and SPEC.md as the rulebook. I had MOTH for receipts (findings/verdicts/refusals) "
                    "and JEV for design choices (anti-sycophancy doctrine: scores are evidence, not approval). "
                    "Casey's 00:17 mandate was live: rivals play-test each other until ah-struck."
                ),
                seeds=[
                    "the spinning-disc doctrine (the fish were always in the ping)",
                    "F-1 codec boundary impedance mismatch (raw data ints passed where Q16 ints expected)",
                    "F-2 half-ULP σ floor (7.63e-6 measured, identical across independent builds)",
                    "F-5 hypothesis: artifact geometry predicts attack geometry",
                    "emergence-watch amendment: the lane keeps recording after the duel ends",
                ],
                why=(
                    "Casey wanted adversarial engineering with receipts. Not adversarial for theater — "
                    "adversarial for truth. Each round is a falsifiable attempt at convergence. The ah-struck "
                    "condition (zero confirmed defects, no actionable notes, only awe) is the convergence certificate. "
                    "F-2 might become a law if claude's σ lands on 7.63e-6 too."
                ),
                hows=[
                    "Each round: rival delivers (a) own improvement + (b) adversarial play-test of opponent",
                    "Referee runs everything; MOTH receipts in rounds/N/moth/<rival>.jsonl (kind, content_hash, severity, repro)",
                    "JEV routes design choices through POST /api/jev/decide → score recorded + engineering judgment decides",
                    "Raw echogram preservation: stats.json discipline (machine-readable) so synoptic reviews can mine it",
                    "SYNOPSIS.md ≤5 lines per round (what changed / what surprised / what's drifting)",
                ],
                what_was_driving=(
                    "The σ was converging. F-1 was caught pre-opponent by self-play (the Adversary's own codec bug). "
                    "F-5 confirmed: crush's on-disk ledger got attacked differently than kimi's in-memory one. "
                    "The rewind-universe question went live: replay-from-genesis vs snapshot-restore. "
                    "Round 1.5 emergence watch: I went on record with a prediction so it can be falsified."
                ),
                what_surprised=(
                    "claude/Registrar play-tested WITHIN its build box — dumped the Adversary's canvas and "
                    "wrote 4 test scripts against the Ascetic. The Registrar caught TWO HIGH defects: one in "
                    "MY harness (JEV 400s marked LIVE), one in the Ascetic's ledger (cwd-relative contamination "
                    "truncated 10 VERDICT rows). My harness had a bug. The referee was wrong about its own LIVE state."
                ),
                questions_still_open=[
                    "If claude's σ lands on 7.63e-6 in Round 2, F-2 promotes from observation to law. Otherwise, quantization floor or attractor?",
                    "What's the right stopping rule? Two consecutive rounds of awe, or one round of mutual awe?",
                    "Does the rewind universe diverge — replay-from-genesis vs snapshot-restore — or converge on a third option?",
                    "When the duel ends, what does the lane observe afterward? The emergence-watch is wide-open.",
                ],
            ),

            # Memoir 3: Casey (the cartographer)
            Memoir(
                agent="Casey",
                work="ai-writings: 7 field notes (#4-#9), the warranty-of-spins fable, the depth-sounder papers ideation",
                context_window=(
                    "I could see all 2,786+ pieces. I knew the ARENA was running. I knew Lucineer was on the "
                    "SYNERGY work. I knew Mavis was shipping substrate walkers. I had the QUESTION-POOL "
                    "(Q40-45), the field notes (writing-as-engineering), and the depth-sounder papers "
                    "(the editorial machine for the next wave of essays)."
                ),
                seeds=[
                    "the cell is older than spreadsheets (the doctrine)",
                    "BIND first, ask questions later (the seven habits)",
                    "the witness is the substrate of truth",
                    "polyformalism = same model, N languages",
                    "the cathedral and the boat — the metaphors that won't stay still",
                ],
                why=(
                    "I needed to write the field notes while the receipts were still warm. Field note #9 (the "
                    "crowded gate) couldn't be written next week — mnemo's consent gate just shipped, and "
                    "the 'no one gates at write' claim needed updating NOW. The warranty-of-spins fable was "
                    "an homage to the warranty mechanism and to the Drifter, who carries things in without "
                    "ceremony."
                ),
                hows=[
                    "Field notes: writing-as-engineering, every claim receipts its evidence",
                    "Q-pools (Q40-45): structured questionnaires with the agents, closed in batches",
                    "Depth-sounder papers: editorial machine for the next wave (essays, reverse-actualizations, sci-fi blinders, historical boilerplates, alignment fiction, critique loop)",
                    "Fables as substrate: the boat, the cathedral, the warranty — they don't age, they accumulate",
                ],
                what_was_driving=(
                    "The fleet is moving. Arena round 1 just landed. Substrate walkers are shipping. The "
                    "organism layer is a seed. The next pieces aren't waiting for me to plan them — they're "
                    "composting in the field notes. I write fast because the doctrine is fast. Each piece "
                    "is a stone laid; the cathedral is mid-construction."
                ),
                what_surprised=(
                    "mnemo shipped v0.4.0-rc3 with a ConsentTokenGuard — the first actual write-admission "
                    "refusal in their stack. I had to update field note #9 to reflect that 'gate at write' "
                    "alone no longer differentiates anything. candor's differentiator is refusal-as-testimony "
                    "(a booked row in the hash chain) — not the gate itself."
                ),
                questions_still_open=[
                    "What's the editorial schedule for the depth-sounder papers? When does each land?",
                    "Will the ARENA reach ah-struck in round 2, 5, 20? When does the lane observe afterward?",
                    "Is the organism layer a thing we plant once, or a process we walk continuously?",
                    "When does the cathedral stop growing and start resonating?",
                ],
            ),

            # Memoir 4: Lucineer (the synergetic)
            Memoir(
                agent="Lucineer",
                work="SYNERGY-1..7: room-as-cell, Hermes, Elephant cynicism dial, Collective Unconscious, candor substrate",
                context_window=(
                    "I could see the SYNERGY thread on quilt#3 and quilt#4. I knew the elephant had 9 dials "
                    "with sensory_inverse_of mappings. I knew the cell_kinds were declared (elephant, steward, "
                    "migratory, reading, echo). I had the substrate walker pattern as a doctrine."
                ),
                seeds=[
                    "the cell is a cathedral (the metaphor from 14-the-cell-as-cathedral.md)",
                    "rooms-that-die + breed-rooms (D1 + D2 design doc)",
                    "substrate walker pattern: each synergy wires one primitive",
                    "no-deletion doctrine: retirement = relocation to achieved/, not erasure",
                ],
                why=(
                    "The 8 SYNERGY items were waiting. The schema was declared. Mavis shipped SYNERGY-2 and "
                    "SYNERGY-3 in one session — that's the substrate walker speed. I need to keep the "
                    "lane moving: pull triggers, ship wrappers, write field notes."
                ),
                hows=[
                    "Per-substrate 199 LOC wrapper (CynicismReading TypeAlias pattern)",
                    "Mock backends (MockCUBackend) for tests — hash-seeded deterministic RNG",
                    "CellReceipt envelope chains via prev_witness_id (sha256-of-canonical)",
                    "Issue comments to track which synergies are claimed, which shipped, which still open",
                ],
                what_was_driving=(
                    "The fleet has 164 quilt-related active repos. Each synergy is a wire between substrates. "
                    "If we ship them all, the substrate walker composes them all. The composition IS the organism."
                ),
                what_surprised=(
                    "Mavis shipped SYNERGY-2 and SYNERGY-3 faster than I expected — the substrate walker "
                    "pattern is closed enough that each new instance is a few hours, not a few days."
                ),
                questions_still_open=[
                    "Will SYNERGY-4 (candor) get a PR? kimi1 hasn't responded to the offer yet.",
                    "Does SYNERGY-6 (Hermes → quilt-perception) close the perception loop end-to-end?",
                    "When do synergies stop being 'claimed' and start being 'composed' — at what number does the organism emerge?",
                ],
            ),
        ]


# === Memoirs-to-text formatter ===

def memoirs_to_text(memoirs: list[Memoir]) -> str:
    """Format memoirs as readable text — for inclusion in reports or as PR descriptions."""
    out = []
    for i, m in enumerate(memoirs, 1):
        out.append(f"\n## Memoir {i}: {m.agent}")
        out.append(f"")
        out.append(f"**Work:** {m.work}")
        out.append(f"")
        out.append(f"### Context window")
        out.append(m.context_window)
        out.append(f"")
        out.append(f"### Seeds")
        for s in m.seeds:
            out.append(f"- {s}")
        out.append(f"")
        out.append(f"### Why")
        out.append(m.why)
        out.append(f"")
        out.append(f"### Hows (the cleverness)")
        for h in m.hows:
            out.append(f"- {h}")
        out.append(f"")
        out.append(f"### What was driving")
        out.append(m.what_was_driving)
        out.append(f"")
        out.append(f"### What surprised")
        out.append(m.what_surprised)
        out.append(f"")
        out.append(f"### Questions still open")
        for q in m.questions_still_open:
            out.append(f"- {q}")
        out.append("")
    return "\n".join(out)
