# C643: Lane Hysteresis Oscillation Pattern

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> EN tokens alternate between QO and CHSH lanes at 56.3%, significantly above the 49.4% permutation null (p < 0.0001, 10,000 within-line permutations). Run lengths are short (QO mean 1.46, CHSH mean 1.61), and QO exits faster (QO->CHSH = 60.0% vs CHSH->QO = 53.3%). Section variation confirms content-driven oscillation rate.

---

## Evidence

**Test:** `phases/LANE_CHANGE_HOLD_ANALYSIS/scripts/change_hold_validation.py` Section 6

### Alternation Rate

| Metric | Value |
|--------|-------|
| Lines tested (>= 4 EN tokens) | 869 |
| EN pairs analyzed | 3,465 |
| Observed alternation rate | 0.563 |
| Null mean (permutation) | 0.494 |
| Null std | 0.007 |
| Empirical p | < 0.0001 |

### Transition Matrix

| From \ To | QO | CHSH |
|-----------|-----|------|
| QO | 627 (40.0%) | 941 (60.0%) |
| CHSH | 1011 (53.3%) | 886 (46.7%) |

QO exits to CHSH at 60.0%; CHSH exits to QO at 53.3%. The asymmetry means QO tokens are shorter-lived in sequence.

### Run Length Distribution

| Lane | Mean | Median | Max |
|------|------|--------|-----|
| QO | 1.46 | 1.0 | 7 |
| CHSH | 1.61 | 1.0 | 8 |

Median 1.0 for both = the most common "run" is a single token before switching.

### Section Variation

| Section | Alternation Rate | N pairs |
|---------|-----------------|---------|
| BIO (B) | 0.606 | 1,550 |
| STARS (S) | 0.551 | 1,453 |
| COSMO (C) | 0.506 | 156 |
| RECIPE (T) | 0.491 | 53 |
| HERBAL_B (H) | 0.427 | 253 |

BIO shows highest oscillation; HERBAL_B lowest.

---

## Relationship to C549

C549 established interleaving significance at 56.3% vs 50.6% null (z=10.27) using cross-line shuffles. C643 confirms at within-line level using 10,000 permutations and adds:
- Transition matrix (QO exits faster)
- Run length distributions (both median 1.0)
- Section-stratified alternation rates

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C549 | Confirmed and extended with within-line permutation |
| C577 | Section variation confirms content-driven interleaving |
| C608 | Short runs confirm no lane coherence at line level |
| C579 | QO exit asymmetry consistent with CHSH-first ordering |

---

## Provenance

- **Phase:** LANE_CHANGE_HOLD_ANALYSIS
- **Date:** 2026-01-26
- **Script:** change_hold_validation.py (Section 6)

---

## Navigation

<- [C642_a_record_role_material_architecture.md](C642_a_record_role_material_architecture.md) | [INDEX.md](INDEX.md) ->
