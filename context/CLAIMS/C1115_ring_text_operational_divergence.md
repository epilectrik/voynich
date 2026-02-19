# C1115: Rosettes Ring Text Operational Divergence

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** ROSETTES
**Phase:** ROSETTES_RING_TEXT_GRAMMAR (Phase 397)
**Extends:** C1114 (construction compliance), C1092 (SOUTH TARGET-dominant)
**Relates to:** C551 (ENERGY-FLOW anticorrelation), C878 (section program variation)

---

## Statement

Despite passing all B construction rules (C1114), ring texts have a radically different operational profile from standard B programs: AXM depressed (32.1% vs B 66.7%), FQ elevated (39.6% vs B 19.2%), EN collapsed (7.5% vs B 31.2%), CC elevated (13.2% vs B 4.4%). PREFIX usage is ok-dominant (37.1% vs B 7.9%) with qo collapsed (3.4% vs B 22.3%). Affordance bins show HUB_UNIVERSAL at 79.6% (B 63.1%) with ENERGY_SPECIALIZED, PRECISION_SPECIALIZED, and ROUTINE_SPECIALIZED all at 0%. Ring texts are B-grammatical but operate in a **different functional register** — frequency/monitoring-dominant rather than energy-dominant, using only universal connector vocabulary.

---

## Evidence

### Macro-State Distribution (Test 5)

| State | Ring | B stationary | Delta |
|-------|------|-------------|-------|
| AXM | 32.1% | 66.7% | **-34.6%** |
| FQ | 39.6% | 19.2% | **+20.4%** |
| FL_HAZ | 13.2% | 6.0% | +7.2% |
| CC | 12.3% | 4.3% | +8.0% |
| AXm | 1.9% | 2.9% | -1.0% |
| FL_SAFE | 0.9% | 0.8% | +0.1% |

JSD(ring, B_stationary) = 0.0961, 77.5th percentile of B paragraph bootstrap (n=200). Within B noise for short sequences, but directionally consistent across all 5 rings.

### Role Distribution (Test 6)

| Role | Ring | B ref | AZC |
|------|------|-------|-----|
| FQ | 39.6% | 12.5% | 28.3% |
| AX | 25.5% | 16.6% | 29.6% |
| FO | 14.2% | 4.7% | 15.8% |
| CC | 13.2% | 4.4% | 4.1% |
| EN | 7.5% | 31.2% | 22.2% |

Ring text role profile is FQ-dominant, EN-collapsed. Closer to AZC than standard B for FQ/AX/FO, but with elevated CC unique to ring texts.

### PREFIX Distribution (Test 8)

| PREFIX | Ring | B baseline |
|--------|------|-----------|
| ok | 37.1% | 7.9% |
| ot | 20.2% | 6.9% |
| ol | 9.0% | 4.0% |
| ch | 6.7% | 17.8% |
| qo | 3.4% | 22.3% |

ok+ot+ol = 66.3% of ring text prefixes (B: 18.8%). These select e-family + infrastructure + h-family MIDDLEs — apparatus management and monitoring. qo (energy/k-family selector) is near-absent.

PREFIX evenness: ring 0.746, B 0.734, AZC 0.710 — similar evenness but completely different distribution.

### Affordance Bins (Test 7)

| Bin | Ring | B | Ratio |
|-----|------|---|-------|
| HUB_UNIVERSAL | 79.6% | 63.1% | 1.26x |
| STABILITY_CRITICAL | 8.8% | 17.6% | 0.50x |
| FLOW_TERMINAL | 6.1% | 9.1% | 0.67x |
| ENERGY_SPECIALIZED | 0.0% | 0.7% | 0.00x |
| PRECISION_SPECIALIZED | 0.0% | 0.2% | 0.00x |
| ROUTINE_SPECIALIZED | 0.0% | 0.7% | 0.00x |

Three specialist bins at exactly 0% — ring texts use ONLY universal vocabulary.

### Suffix Distribution (Test 3)
- Ring text: 62.6% bare (B: 51.5%, AZC: 47.8%)
- More bare tokens = simpler morphology, fewer suffixed forms

---

## Interpretation

Ring texts follow B's construction grammar but are tuned for a different operational mode. The ok-dominance and FQ-enrichment suggest apparatus-state monitoring and checking rather than energy-intensive procedural execution. The exclusive use of HUB_UNIVERSAL vocabulary (with zero specialist bins) is consistent with generic procedure skeletons that describe the structure of operations without domain-specific content.

This divergence is structural, not random: the same pattern appears across all 5 ring texts despite being at different physical positions (2 corners, 3 cardinals). The macro-state JSD falls within B paragraph noise (77.5th percentile), suggesting the divergence is a shift in parameter emphasis, not a fundamentally different grammar.

---

## Provenance

- Phase: 397 (ROSETTES_RING_TEXT_GRAMMAR)
- Script: `phases/ROSETTES_RING_TEXT_GRAMMAR/scripts/ring_text_grammar_test.py`
- Results: `phases/ROSETTES_RING_TEXT_GRAMMAR/results/ring_text_grammar_results.json`
- Related: C1114, C551, C878, C1029, C995, C976
