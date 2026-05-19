# PHASE 701: Lullian Wheels Combinatorial Test (Brief)

**Status:** COMPLETE — INDEX entry only (no constraint registration per expert consultation)
**Date:** 2026-05-18
**Posture:** Methodology shift attempt that produced self-generated-alternative falsification — documented but not constraint-tier per crazy-expert recommendation

---

## What was tested

Tested whether the Voynich 9-rosette foldout (f85v + f86r, transcribed as f86v3 etc.) implements Ramon Llull's Ars Magna combinatorial wheel structure.

**Hypothesis:** If the rosettes are Lullian wheels, they should:
- Have 9 distinct vocabularies (one per Lullian principle B-K)
- Show all-to-all (36-edge) combinatorial topology
- Have higher vocabulary overlap on connected pairs (combinatorial pairings)

**Pre-registered criteria:**
- H1: vocabulary distinctness mean Jaccard > 0.7
- H2: ≥70% of testable rosettes have ≥3 unique MIDDLEs
- H4: topology matches Lullian all-to-all (36 edges) not hub-and-spoke / spoke-and-ring

---

## Result

**LULLIAN WHEELS FALSIFIED.**

| Test | Result |
|------|--------|
| H1 (vocabulary distinctness) | **FAIL** (mean Jaccard = 0.6974, below 0.7 threshold) |
| H2 (9-fold partition) | PASS (5/6 testable rosettes have ≥3 unique MIDDLEs) |
| H4 (topology Lullian) | **FAIL** (12-edge spoke-and-ring, not 36-edge all-to-all) |

**Decisive finding:** Topology has 12 edges (4 CENTER↔cardinal + 8 cardinal↔corner). Lullian wheel requires 36 edges (all-to-all). Even maximal hidden connectivity from the 3 non-transcribed rosettes (NE, EAST, SE) cannot produce required topology.

**Vocabulary check:** Connected pairs mean Jaccard 0.687, unconnected pairs mean 0.706 — essentially identical. The connection structure is geometric/topological, not vocabulary-driven (which Lullian combinatorial pairings would require).

---

## Why this is INDEX-only, not a registered constraint

Per crazy-expert consultation (2026-05-18):

> "Llull-specific falsification is a special case, not a new architectural finding. C1128 (generic indexing) + C1130 (random transition) + C1989 (path/node differentiation) + `SPECULATIVE/rosettes_workshop_diagram.md` Tier 4 (workshop topology) already foreclose flowchart-class hypotheses generically. The Llull hypothesis was self-generated based on visual + tradition reasoning, not responding to external scholarly advocacy. Registering as new constraint adds to negative-space framework-echo trap — 'Voynich-NOT-mensural, NOT-computus, NOT-Lullian, NOT-X...' becomes its own framework that dilutes load-bearing distinctness measurements."

Both experts converged that the alternative-class internal-methodology approach is saturated. PHASE_701 produced a useful methodology experiment but the result is already implicit in existing constraints.

**The 12-edge spoke-and-ring topology is genuinely new data**, but it's a refinement of existing rosettes findings, not a separate architectural fact warranting its own constraint number.

---

## Cross-references

This finding refines / is implied by:
- **C1124** — rosettes use bridge MIDDLE vocabulary (3.05x enrichment) — generic operational backbone
- **C1126-C1127** — AZC-like metalayer (diagram-with-labels syntactic mode)
- **C1128** — generic indexing across all 82 B folios (rosettes serve all recipes, not specific ones)
- **C1130** — forbidden-bigram compliant, random transition structure (topology, not directed flowchart)
- **C1989** — path tokens have 9.4x da-prefix enrichment (material markers); node tokens have 4.3x ok-prefix enrichment (apparatus markers)
- **C2032 / C2040** — alternative-class falsification series (mensural, 6 medieval periodic notations)
- **`SPECULATIVE/rosettes_workshop_diagram.md`** — Tier 4 interpretation: rosettes = alchemical workshop topology, central multi-alembic apparatus

---

## Scripts

| Script | Purpose |
|--------|---------|
| `_inspect_rosettes_data.py` | Initial transcript inspection of f85/f86 folios |
| `_inspect_rosettes_annotated.py` | Inspect `data/rosettes_annotated.json` and `data/rosettes_unified.json` |
| `_inspect_rosette_grid.py` | Examine per-rosette topology and metadata |
| `_inspect_rosette_profiles.py` | Inspect combined_profile data per rosette |
| `_lullian_wheels_test.py` | Main test: H1 vocabulary distinctness + H2 partition + H4 topology |

---

## Data limitations (transparency)

Only 6 of 9 rosettes have sufficient transcribed tokens for vocabulary testing:
- **Tested:** NW (41 tokens), NORTH (39), WEST (31), CENTER (60), SW (34), SOUTH (40)
- **Excluded:** NE (2 tokens), EAST (0), SE (4)

Topology test does NOT depend on token data and is decisive at 12 edges < 36 required.

---

## What this means for the project

**Internal alternative-class adversarial methodology is saturated.** Cumulative falsification series now stands at:
- Mensural notation (C2032, period-2)
- 6 medieval periodic notations (C2040: weekly, zodiac, indiction, computus Metonic, solar dominical, lunaria)
- Lullian wheels combinatorial (PHASE_701, this brief)

Both experts converged that PHASE_701 should be the **last alternative-class test using internal methodology**. Future work needs:
1. External corpus acquisition (Antidotarium Nicolai, Mesue's Grabadin for Section S source-matching gap)
2. Physical reconstruction grounded in C2031/C2032/C2040 substrate signatures
3. Synthesis writeup consolidating accumulated findings

---

## Origin

Phase suggested in PHASE_700 strategic context as combinatorial methodology shift to break the procedural ceiling crazy-expert flagged. User opted to run it. Result: clean negative, but doesn't break the ceiling — different angle on the same wall.

Honest meta-finding: the Lullian wheels hypothesis was self-generated (visual + Pseudo-Lull-tradition reasoning) rather than responding to external Voynich-scholar advocacy. This is the framework-echo-against-self-constructed-alternative pattern. Both experts flagged this; recommendation was to document but not constraint-register.

PHASE_701 stands as a documented test of a specific named alternative-class hypothesis, with clean negative result. It is NOT registered as a constraint because it does not establish substrate-level structural fact beyond existing C1128/C1130/C1989/rosettes_workshop_diagram.md findings.
