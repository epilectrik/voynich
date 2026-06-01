# PHASE 741 — f75r↔III.19 joint ×4-AND-×9 anchor: registration-grade correction

**Status:** COMPLETE — annotation to C1889 + C2034 (no new constraint; positive correction, not falsification)
**Date:** 2026-06-01
**Type:** Registration-grade confirming run of the joint corpus-rarity, correcting the PHASE_739 design-D scope error (the registry-compression episode).

---

## Why this phase exists

PHASE_739 design-D tested the f75r ×4-run **alone** (C1889) as "the Voynich leg of the 1/16,500" and got p=0.097 → I (wrongly) reported the anchor "deflated ~8×." That was a **registry-compression error**: the C1889/C2034 rows had flattened the anchor's Voynich leg to "×4-run unique = 1/82," but the anchor's actual Voynich leg is the **JOINT ×4-AND-×9** (the conjunction the 8D matcher landed on, C1969). See `feedback_registry_compression_test_the_claim.md`.

## Result (registration-grade, locked: N=10000, seed=0)

Predicate validated — reproduces C1969's exact 3 ≥9-qok-window folios (f75r, f86v3, f108r) and the corpus ceiling of 9.

| statistic | p (selection-safe corpus-max, type-freq-preserving within-folio null) |
|---|---|
| ×4-run alone | **0.10** (look-elsewhere-borderline — the design-D "deflation") |
| ×9-window alone | **0.96** (worthless — almost always reachable) |
| **JOINT (≥4 run AND ≥9 window, same folio)** | **0.0108** ≈ the registry's 1/82 |

f75r is the **unique** folio of 82 with BOTH (the 3 window-folios are f75r/f86v3/f108r; only f75r also has a ≥4 run). The joint is the real Voynich leg: 1/16,500 ≈ joint(0.0108) × Catalan C2034(1/189) **holds**.

## Disposition
- **C1889** ANNOTATED: ×4-run raw uniqueness stands; its selection-safe corpus-rarity is p≈0.10 (NOT 1/82); the 1/82 is the JOINT rarity (p_joint=0.0108).
- **C2034** ANNOTATED: "1/82 per C1889" re-attributed to the JOINT conjunction; 1/16,500 holds via the joint.
- **Anchor SOUND.** The earlier "deflation" was an artifact of testing the compressed ×4-alone leg.
- f75r↔III.19 MATCH interpretation unchanged (Tier 3, C1896). Independence of C1889×C2034 in the product is asserted, not tested (lean-expert caveat, carried forward).

## Method note
Null = within-folio token-ORDER shuffle (preserves exact per-folio type-frequency multiset → reachability automatic), re-segment to original line lengths, corpus-max over 82 folios (selection-safe / look-elsewhere-corrected). Token-order shuffle is the correct null for a token-run/adjacency claim (char-5-gram is window-blind here, C2066). Script: `scripts/joint_x4x9_corpusmax.py`; result: `results/joint_x4x9_corpusmax.json`.
