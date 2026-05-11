# Phase 693: MIDDLE-Layer Sequential Null and Class-Layer Sequential Structure (T1/T2/T3)

**Status:** COMPLETE
**Started:** 2026-05-11
**Completed:** 2026-05-11
**Goal:** Resolve a longstanding terminological ambiguity in BCSC: when the constraint system says "17 forbidden transitions" (C109, C783), at which abstraction layer does "transition" apply? Within-line shuffle null at MIDDLE-string vs 49-class layers.

## Origin

A clean Opus agent did a cold read of the H-track transcript (no project framing) and proposed a discriminator: `H(coda | stem)` vs `H(coda | prev_coda)` vs `H(coda | line_pos)` to separate natural-language-like signature from state-machine signature.

Initial run at the SUFFIX (coda) layer showed stem strongly dominates (~1.0 bits MI vs ~0.07 for prev_coda) — the cold agent's literal discriminator scored as "natural-language-like." Re-run at the MIDDLE layer showed apparent `prev_middle` dominance (1.55-2.70 bits) but a within-line shuffle null erased it: real I ≈ null I across all subsets (z = −0.39 B, −2.48 H-track, −5.09 A).

Expert-advisor (first pass) flagged this as a confirmation of C1118 / C1212 / C1024 / C1034 already in the corpus, not a reframing. Recommended three follow-up tests before any registration: T1 section stratification, T2 directional forbidden-pair analysis, T3 (KILLER) class-layer shuffle null.

## Sub-tests

### T1 — Per-section shuffle null (MIDDLE layer, Currier B)

Stratify by data-file section code (B/C/H/S/T). Run within-line shuffle null on I(middle; prev_middle) per section.

**Result:** Only Bio (data section B; f74-f84 area) has positive excess (z = +1.49). Herbal (z = −2.70), Stars (z = −1.33), Cosmo C-foldouts (z = −1.17), and Top/intro (z = −0.91) all at-or-below null. Whole-of-B z = −0.39 is the average. Bio is the marginal-residual carrier.

| section | n tok | H(mid) | real_I | null_I | excess | z |
|---|---|---|---|---|---|---|
| **B (Bio)** | 4,216 | 4.721 | 1.137 | 1.104 | **+0.034** | **+1.49** |
| C (Cosmo foldouts) | 703 | 5.699 | 2.824 | 2.879 | −0.054 | −1.17 |
| H (Herbal_B) | 1,911 | 6.081 | 2.612 | 2.708 | −0.097 | −2.70 |
| S (Stars/Recipe_B) | 6,971 | 6.019 | 1.861 | 1.886 | −0.025 | −1.33 |
| T (Top/intro B-tokens) | 205 | 5.440 | 3.634 | 3.688 | −0.054 | −0.91 |

Confirms expert prediction (per C1048). Registered as **C2024**.

### T2 — Forward vs backward count on the 17 forbidden pairs

For each forbidden pair `(A, B)`, count adjacent occurrences in real order (fwd = `M_t=A AND M_{t+1}=B`; bwd = reverse). Compare to within-line shuffle null. Also report same-line co-occurrence.

**Result:** All 17 pairs have **0 real adjacent occurrences in both directions**. 16/17 have zero same-line co-occurrence (the MIDDLE values never appear in the same line at all — consistent with C1552 phantom-source pattern: 5/9 hazard-source MIDDLEs are absent from the corpus). The 1 pair with same-line co-occurrence (`he → t`, 4 line-overlaps) shows 0 real adjacencies in EITHER direction against null expectations of fwd=0.53 / bwd=0.63. **Both directions symmetrically suppressed.**

Confirms expert prediction (per C1118 / C1034). The forbidden-pair mechanism is bag-of-line co-occurrence prohibition, not directional transition. Folded into **C2023** as the directional-symmetry evidence.

### T3 — Class-layer shuffle null (KILLER TEST)

Replace each token's MIDDLE with its 49-class id (via `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`, 480 token→class mappings, 42 of 49 classes represented). Recompute real I(class; prev_class) and 30-shuffle within-line null.

**Result:** CLEAN SEPARATION confirmed.

| subset | class coverage | H(class) | real_I | null_I | excess | z |
|---|---|---|---|---|---|---|
| H-track FULL | 58.0% | 4.508 | 0.284 | 0.255 | +0.028 | +2.74 |
| **Currier B only** | 62.5% | 4.311 | 0.264 | 0.215 | **+0.049** | **+3.91** |
| Currier A only | 47.5% | 4.639 | 0.707 | 0.698 | +0.009 | +0.37 |

- **Currier B at MIDDLE layer: z = −0.39 (at-null).** Same data at 49-class layer: **z = +3.91 (significantly above null, genuinely sequential).** Two layers, two results. The macro-state automaton at the class projection (C976, C1010, C1015) is genuinely Markov. The MIDDLE-token layer below it is co-occurrence-only.
- **Currier A at class layer: z = +0.37 (at-null).** A has neither class-Markov nor MIDDLE-Markov structure. C346's "sequential coherence" must live at a different organizational level — record-level / positional / compositional, not class-Markov adjacency.

Registered as **C2023** (B two-layer result) and **C2025** (A class-layer null confirming C225 via shuffle-null methodology).

## Aggregate findings

Three Tier 2 constraints registered:

- **C2023** — MIDDLE-Layer Sequential Null vs Class-Layer Sequential Structure (B). Shuffle-null operationalization of C1118/C1212/C1024/C1034 layer distinction. References: C109, C627, C783, C886, C391, C976, C996, C1010, C1011, C1019, C1024, C1025, C1031, C1032, C1034, C1071, C1118, C1212, C1552.
- **C2024** — Bio Section Residual MIDDLE-Layer Sequential Structure (per-section heterogeneity within B). Confirms C1048. References: C1047, C1048, C1055, C1085, C1086, C1116, C1404.
- **C2025** — Currier A Class-Layer Shuffle Null Confirms C225 via Independent Methodology. References: C225, C230, C231, C233, C240, C346, C422, C475, C729, C964.

## Methodological precedent

**Within-line shuffle null** is a clean test for distinguishing co-occurrence from sequence within line units. Procedure: for each transcript line, randomize token order while preserving line membership and length; recompute the conditional MI of interest; average over N≥20 shuffles to get a null mean and SD; report (real − null) excess and z-score. Useful for any constraint that claims sequential structure within a line; distinguishes such claims from bag-of-line composition. Recommended for future tests where the layer-of-application is ambiguous.

## BCSC amendment applied

`context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml` HAZARD_TOPOLOGY_FIXED rewording:

> 17 forbidden class-level transitions are directional (C783); the underlying MIDDLE-level forbidden pairs are predominantly bidirectional co-occurrence prohibitions (C1118, C2023). At the 49-class projection, hazard structure is transitional; at the MIDDLE-token layer, it is co-occurrence-forbidden.

## Files

- `scripts/entropy_shuffle_null_v1.py` — Layer 1 (suffix) and Layer 2 (MIDDLE) shuffle-null
- `scripts/entropy_shuffle_null_v2.py` — T1 (per-section), T2 (directional forbidden-pair), T3 (class-layer) follow-up tests
- `scripts/list_forbidden_pairs.py` — utility to enumerate the 17 forbidden pairs from `phases/15-20_kernel_grammar/phase18a_forbidden_inventory.json`
- `results/v1_layer1_layer2_output.txt` — raw output of v1 script
- `results/v2_t1_t2_t3_output.txt` — raw output of v2 script

## Scripts

Run from project root with the canonical venv:

```bash
python phases/PHASE_693_MIDDLE_LAYER_SHUFFLE_NULL/scripts/entropy_shuffle_null_v1.py
python phases/PHASE_693_MIDDLE_LAYER_SHUFFLE_NULL/scripts/entropy_shuffle_null_v2.py
```

Both scripts are deterministic given fixed random seeds (default seed=0 for v1, seed=42 in T2 of v2). N_SHUFFLES = 30 for v2. Total runtime ~20 seconds on local CPU.
