# C1098: Rosettes Structural Index Confirmed

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** GLOBAL
**Phase:** ROSETTES_STRUCTURAL_VALIDATION (Phase 389)
**Strengthens:** C1095 (metalayer status)
**Supported by:** C1096 (bridge enrichment), C1097 (affordance profile)

---

## Statement

Phase 389 confirms that the Rosettes metalayer (C1095) operates as a structural index, not just a vocabulary-level anomaly. Four independent tests yield a mean index score of 0.92/1.0:

| Test | Verdict | Score | Key Finding |
|------|---------|-------|-------------|
| V1: C475 Compatibility | ELEVATED_COMPATIBILITY | 0.8 | Within-region 74-83% vs B corpus 54% |
| V2: Bridge Enrichment | ENRICHED | 1.0 | 3.46x enrichment, p=6.9e-16 |
| V3: Affordance Bins | BRIDGE_CONCENTRATED | 1.0 | Bridge bins = 69.2%, all 4 enriched |
| V4: PREFIX Distribution | INDEX_PROFILE | 0.9 | Evenness 0.791 > all baselines |

The Rosettes preferentially uses cross-system connective vocabulary (bridges), concentrates in connective functional bins, shows elevated mutual compatibility (consequence of bridge density), and distributes PREFIXes more evenly than any individual system.

---

## Evidence

### V1: Elevated Compatibility
- Rosettes within-region legal pair rate: LABEL 74.3%, DESC 83.5%
- Rosettes cross-region legal pair rate: 63.9%
- B corpus within-line reference: 54.4%
- Random baseline: 7.2%
- Rosettes vocabulary is 37-53% more mutually compatible than B corpus vocabulary

### V2: Bridge Enrichment (C1096)
- 75/308 unique Rosettes MIDDLEs are bridges (24.4% vs 7.0% B baseline)
- Fisher's exact: p = 6.9e-16, OR = 4.25
- All 7 folios show 6-9x enrichment
- LABEL regions: 6.38x, DESCRIPTION regions: 9.27x

### V3: Affordance Profile (C1097)
- Bridge bins (0,6,8,9): 69.2% of mapped MIDDLEs
- HUB_UNIVERSAL: 2.20x enriched (all 23/23 present)
- ENERGY_SPECIALIZED: 0.13x (near-absent)
- LABEL regions: 79.4% bridge bins
- DESCRIPTION regions: 86.5% bridge bins

### V4: PREFIX Distribution
- Rosettes PREFIX evenness: 0.791
- B corpus: 0.738, A corpus: 0.745, AZC: 0.710
- Rosettes has highest PREFIX evenness of any system
- JSD to B = 0.0253 (closest), to A = 0.0677, to AZC = 0.0732
- f85v2 prefix ratio = 6.538 (AZC-like), other folios 0.3-0.7 (B-like)

---

## Structural Interpretation

The four tests form a coherent picture:
1. **Bridge enrichment** (V2) is the primary mechanism — Rosettes uses the vocabulary that connects A's discrimination manifold to B's execution grammar
2. **Affordance concentration** (V3) is the functional consequence — bridge MIDDLEs cluster in connective bins, so the Rosettes does too
3. **Elevated compatibility** (V1) is the emergent property — bridge MIDDLEs are by definition the most general, most compatible vocabulary
4. **PREFIX evenness** (V4) is the scope signature — the index samples across all operational lanes more evenly than any production text

**C384 note:** This index function operates through vocabulary-mediated correlation (consistent with C384.a: "CONDITIONAL RECORD-LEVEL CORRESPONDENCE PERMITTED"), not through direct A-to-B addressing.

---

## Provenance

- Phase: 389 (ROSETTES_STRUCTURAL_VALIDATION)
- Script: `phases/ROSETTES_STRUCTURAL_VALIDATION/scripts/rosettes_structural_validation.py`
- Results: `phases/ROSETTES_STRUCTURAL_VALIDATION/results/rosettes_structural_validation.json`
- Related: C1095, C1096, C1097, C1013, C1014, C995, C384
