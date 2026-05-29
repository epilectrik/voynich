# C109: 17 Forbidden Transitions (existence)

**Tier:** 2 | **Status:** ACTIVE | **Phase:** Phase 18 (revised PHASE_732, 2026-05-28)

---

## Claim

**17 forbidden directional transitions exist in the Currier B grammar** — token-pairs that never occur adjacently (~0% realized rate; ~65% class-level compliance per C789). The forbidden set is fixed across all 83 folios.

This is the genuinely-frozen, independently-grounded core (C627 token-specific lookup, C783 all-17-directional, C2023 zero real adjacent occurrences in both directions, C1118 bidirectional dominance, C1071 above-component-rules). It does NOT depend on any classification of the 17 into groups.

---

## REVISION NOTICE (PHASE_732, 2026-05-28)

**The original "5 hazard failure classes" claim has been struck.** It was registered with the evidence line *"Cluster analysis reveals 5 natural groupings"* — which is **false about its method**. No clustering was ever run. Forensic trace (triple-confirmed):

- `phase18_failure_typology.py` lines 61-87 **hardcode** a dictionary of 5 distillation failure-mode names + keyword lists, written before any analysis.
- Lines 392-411 sort the 17 transitions into these 5 classes by **keyword substring-matching**.
- The only clustering anywhere in the phase 15-20 chain produced **1 cluster** (phase15a `internal_clusters=1`), not 5. Phase 16 had a different 12-mode scheme.

Empirical clustering of the 17 transitions by atom territory (run in PHASE_732):
- **5 is not data-preferred** (silhouette-optimal k=8; k=3 ≥ k=5; natural-vs-imposed ARI=0.42).
- Only **PHASE_ORDERING (n=7)** is a tight, gloss-coherent cluster — corresponding to C1529's headless/y-terminal → a-HEAD sequencing failure ("sealed/completed → iteration/restart forbidden").
- **ENERGY_OVERSHOOT is contradicted** by the project's own hazard-frame map (C1448): its sole member `he→t` contains no k-HEAD heat atom (`he` = watch.cool). RATE_MISMATCH and COMPOSITION_JUMP labels have no supporting atoms.

See **C2060** for the full provenance correction + clustering result. The atom-territory structure that IS real is independently and more rigorously held by **C1528-C1533** (atom-grounded re-derivation), which supersede the distillation-failure-mode labels.

---

## What survives, by status

| Item | Status |
|------|--------|
| 17 forbidden directional transitions exist | **Tier 2 (this constraint)** |
| Atom-territory structure of the transitions | **Tier 2 (C1528-C1533)** |
| PHASE_ORDERING as a sequencing failure (sealed→iteration) | **Tier 2/3 (C1529)** |
| The 5-class distillation taxonomy (the partition) | **Tier 3 — imposed, not discovered (C2060)** |
| The physical-failure-mode labels (vapor lock, scorching, etc.) | **Tier 3-4 interpretive; ENERGY_OVERSHOOT gloss-contradicted** |
| Three-level safety architecture | **survives — independent of taxonomy (C1440-C1448, C1463-C1471)** |

---

## Related Constraints

- C2060 - provenance correction (imposed taxonomy, k=5 not data-preferred)
- C1528-C1533 - atom-grounded hazard structure (the rigorous replacement)
- C1529 - PHASE_ORDERING = headless-y → a-HEAD sequencing failure
- C627, C783, C2023, C1118, C1071 - independent grounding of forbidden-transition existence
- C789 - class-level compliance (~65%)
- C110, C111, C112 - measurements over the 17 (C110 = PHASE_ORDERING dominance; C111/C112 taxonomy-independent)
- C216 - hybrid hazard model (DEMOTED Tier 3 — leans on imposed partition)

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
