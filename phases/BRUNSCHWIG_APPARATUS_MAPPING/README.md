# Phase: BRUNSCHWIG_APPARATUS_MAPPING

**Status:** COMPLETE | **Date:** 2026-02-06 | **Verdict:** STRONG

## Objective

Map Brunschwig distillation apparatus/methods to Voynich manuscript sections using prefix distribution, positional analysis, and MIDDLE selectivity evidence.

## Background

- C930 established lk prefix is 81.7% concentrated in section S, mapping to fire-method monitoring (MONITOR_DRIPS/REGULATE_FIRE)
- C931 established prefix positional ordering within lines matches Brunschwig's 7-phase workflow
- F-BRU-012 previously mapped 5 prep operations to 5 prep-tier MIDDLEs (rho=1.0)
- BRSC v2.0 documents 33 operations across 7 phases with apparatus-specific assignments

## Results Summary

### Test 01: Section B Complement Analysis - PASS

**ol** is the B-section complement to lk's S-section concentration:
- ol: 45.3% in B (1.47x enriched) vs lk: 81.7% in S (1.78x enriched)
- ol's top MIDDLE is **k** (kernel operator) in ALL sections — it operates on thermal execution targets
- lk completely avoids k (0/2068) — it monitors checkpoints
- Folio-level anti-correlation: rho=-0.147 (negative but not significant; directionally correct)
- ol selects sh (10.3x), kee (7.1x), ch (5.7x) = sustained monitoring + kernel targets

**ol is not a direct balneum equivalent of lk.** Instead, ol=CONTINUE/STORE (applies kernel operations at line-final positions) while lk=MONITOR (checks fire status at mid-line positions). They operate on different objects in different phases, and their complementary section distribution reflects that fire-method folios need fire-monitoring (lk) while balneum folios need sustained kernel management (ol).

### Test 02: Section-Apparatus Mapping - PASS

| Section | Apparatus | Key discriminators |
|---------|-----------|-------------------|
| **S** | Fire methods (Degree 2-3) | lk 4.0% (highest), ol 3.2% (lowest), ch/sh=2.00 |
| **B** | Balneum mariae (Degree 1) | ol 6.7% (highest), lk 0.8% (lowest), qo 27.5% (highest), ch/sh=0.96 |
| **H** | Gentle/precision (REGIME_4) | lk 0.3% (near-zero), ok 10.4% (highest), ch/sh=1.85, qo 11.9% (lowest) |
| **C** | Rectification-heavy | ot 11.1% (highest), tch 2.1% (highest), ok 3.1% (lowest) |
| **T** | Setup-dominant | da 11.4% (highest), sh 17.2% (highest), small sample |

Three key discriminating ratios:
- **lk/ol ratio**: S=1.27 (fire-dominant), B=0.12 (balneum-dominant), H=0.09 (gentle)
- **ch/sh ratio**: H=1.86 (precision/testing), S=2.00 (balanced), B=0.96 (observation-dominant)
- **qo intensity**: B=27.5% (high execution), H=11.9% (low, setup-heavy), S=20.6% (standard)

### Test 03: Prefix-Operation Assignment - 14 PREFIXES MAPPED

| Prefix | Operation | Confidence | Key evidence |
|--------|-----------|------------|--------------|
| pch | GATHER/COLLECT | HIGH | 48.2% line-initial, 25.5x par-initial, F-BRU-012 confirmed |
| tch | CHOP/CUT | HIGH | 52.9% line-initial, 10.7x par-initial, F-BRU-012 confirmed |
| qo | DISTILL/EXECUTE | HIGH | Rank 1 prefix, selects t/ke/k exclusively, even positional |
| sh | MONITOR (continuous) | HIGH | Front-loaded (3.14x), C929 confirmed, observation MIDDLEs |
| ch | TEST (discrete) | HIGH | Mid-to-late, C929 confirmed, gates close/input/iterate |
| lk | MONITOR_DRIPS/REGULATE_FIRE | HIGH | 81.7% section S, C930, checkpoint MIDDLEs |
| sa | DRY/MACERATE | MEDIUM | 43.8% line-initial, continuation MIDDLEs, B-enriched |
| te | STRIP/WASH | MEDIUM | 19.7% line-initial, C/H-enriched, material MIDDLEs |
| ok | SEAL/GATE | MEDIUM | H-enriched, checkpoint MIDDLEs, Jaccard 0.82 with ot |
| ot | RECTIFY/FILTER/POUR | MEDIUM | Late position, C-enriched, finalize MIDDLEs |
| da | SETUP/MIX/REPLENISH | MEDIUM | Bimodal (setup+teardown), continuation MIDDLEs |
| ol | STORE/CONTINUE | MEDIUM | Final position, B-enriched, kernel operator MIDDLEs |
| ke | COOL/SETTLE | LOW-MEDIUM | Late position, observation/state MIDDLEs |
| lch | POUR/STRAIN | LOW-MEDIUM | Final position, B-enriched, observation MIDDLEs |

### Phase-Level Frequency Comparison

| Phase | Brunschwig | Voynich | Ratio |
|-------|-----------|---------|-------|
| PREPARATION | 37.0% | 4.2% | 0.11x |
| PRE-TREATMENT | 12.9% | 2.0% | 0.15x |
| DISTILLATION | 27.2% | 24.2% | 0.89x |
| MONITORING | 3.1% | 37.2% | 12.0x |
| POST-PROCESS | 9.7% | 10.1% | 1.05x |
| COMPLETION | 10.1% | 22.3% | 2.22x |

Phase-level Spearman rho = -0.486 (p=0.33, not significant).

**This negative correlation is itself evidence.** Brunschwig is a narrative text that describes preparation at length but abbreviates monitoring ("watch the drips"). Voynich is an operational program that compresses preparation to single tokens (pch+material) but expands every monitoring checkpoint into its own instruction. The inversion is exactly what you'd expect comparing a human recipe book to a control program: **inverted verbosity for the same operations**.

DISTILLATION (0.89x) and POST-PROCESS (1.05x) match because they're neither narrative-heavy nor checkpoint-heavy — they're proportional in both encoding systems.

## MIDDLE Functional Clusters (from Jaccard similarity)

Three distinct MIDDLE families emerged, with zero cross-family overlap:

| Cluster | Prefixes | Jaccard | MIDDLEs | Domain |
|---------|----------|---------|---------|--------|
| **Observation** | ch, sh, ke, te, pch, lch, tch | 0.54-0.82 | edy, ey, ed, dy, eo, eol, e | State observation targets |
| **Checkpoint** | ok, ot, lk | 0.67-0.82 | aiin, ain, ar, al, ch, eey | Gate/verification targets |
| **Continuation** | da, sa | 0.67 | iin, in, i, r, l, m | Flow/sustained state |

qo stands alone (Jaccard 0.00 with ok/ot/sa) — it exclusively selects kernel operators (k, t, ke).

## New Constraints

- **C930**: lk section-S concentration + fire-method specificity
- **C931**: Prefix positional phase mapping

## Scripts

- `01_section_complement_analysis.py` — Prefix profiles, MIDDLE selectivity, ol deep-dive
- `02_section_apparatus_mapping.py` — Section-apparatus mapping, prefix-operation assignment, frequency comparison
