# PHASE 743 — AZC forward probes: ring sequence-vs-set + label/ring-text novelty

**Status:** COMPLETE — DOCUMENTED (no new constraint; refines C305/C525). Forward investigation off the
PHASE_742 cleaned foundation.
**Date:** 2026-06-01

---

## Why this phase exists
PHASE_742 cleaned the AZC data layer (4 serialization-artifact retractions). This phase is the forward
investigation it enabled: probe AZC's nature using the ONE token order PHASE_742 validated as real (within
a ring locus = genuine angular order; block-order between rings is the artifact).

## Findings

### 1. Ring "sequence vs set" — INCONCLUSIVE (document-only)
Within-ring lag-1 feature agreement vs within-ring shuffle (57 ring loci, 1714 tokens):
- MIDDLE (identity): 0.034 vs 0.034, Z=+0.32 — but MIDDLE base-rate floors power (lean: can't detect a lift <~0.015).
- PREFIX pooled directional: obs 0.2016 vs null 0.1879, one-sided p=0.0435 — **fails multiple-comparison correction** (3 features looked at); 5/57 rings indiv-sig on mixed folios (only 2/5 on C759-active → not pure zone-leakage).
- drift Z=-0.91 (none).
**Verdict:** no clean set-vs-sequence call. No detectable MIDDLE sequence (underpowered); a faint, non-robust
PREFIX local-clustering hint. NOT registrable as "rings are sets" (overstated off the lowest-power feature).

### 2. Label vs ring-text A-reference / novelty — small residual, DOCUMENTED not registered
Labels (S, short @Lz loci) vs ring-text (R, long @Cc loci), zodiac; MIDDLE classified by A/B-inventory membership.
- **A_only (A-exclusive): ~1.5% both arms** — floored by the large shared A∩B pool (denominator artifact). The
  first-pass "component-blind" verdict came from testing THIS no-power cell — DROPPED.
- **`neither` (novel, in neither inventory): Labels 15.2% vs Ring-text 8.1%, raw gap +0.071, within-folio p=0.0002.**
- **Frequency-matched control (the decisive gate, both experts):** raw +0.071 → **+0.025** (95% CI [+0.008,+0.041],
  excludes 0); per-folio **11/12** folios S>R. **~65% of the raw gap was the frequency confound** (label tokens use
  rarer MIDDLEs; rare MIDDLEs mechanically less likely attested in A/B). All AZC novelty lives in the hapax/rare bins;
  MIDDLEs appearing ≥4× in AZC are 100% shared-pool.
**Verdict:** a small (+0.025) residual survives frequency-matching and is per-folio robust — but it is **C525-adjacent**
(frequency-matching controls rarity, not label-pool-membership; C525 already establishes label vocabulary stratification,
61% label-only). Documented as a refinement of C305/C525, **not** registered as an independent constraint (small effect,
echo-adjacent; user decision 2026-06-01).

## Disposition
- No new constraint. Refinement notes added to C305 and C525.
- Scripts: `ring_sequence_structure.py`, `label_vs_ringtext_Aref.py`, `corrected_tests.py`, `freq_matched_control.py`.
- Results: corresponding JSONs in `results/`.

## Methodology note (the value of this phase)
Three expert-consult rounds, each catching an unearned verdict — a clean illustration of the differential check +
framework-as-null discipline at maturity:
1. "Rings are SETS" — overstated off MIDDLE (lowest-power feature); lean caught floor-vs-discriminator.
2. "A-reference component-blind" — tested the floored A_only cell (~6 tokens); lean caught it, surfaced the resolvable
   `neither` contrast I'd missed.
3. "Labels more novel" (p=0.0002) — both experts converged: frequency confound; likely C525/C760/C914 re-measured.
   Frequency-matching shrank it 65% to a small C525-adjacent residual.
**The four AZC forward angles this session (labeling, ring-set, indexing, novelty) all resolved into the existing
characterization (C305/C441/C326/C525/C760) — AZC is a mature subsystem. The audit cleaned it; forward structural
probes now re-derive it.** Expert-advisor (interpretive) repeatedly leaned register (framework-fit); lean (rigor)
repeatedly caught the verdicts weren't earned. The divergence localized the echo every time.
