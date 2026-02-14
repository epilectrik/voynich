# C1027 — Hazard Violation Archaeology: Forbidden Pair Violations Are Spatially Uniform but Structurally Conditioned

**Tier:** 2 (Structural Inference)
**Scope:** B
**Phase:** HAZARD_VIOLATION_ARCHAEOLOGY (Phase 350)
**Depends on:** C109, C789, C554, C624, C1026

---

## Statement

The 84 class-level forbidden pairs (expanded from 17 MIDDLE-level forbidden pairs) are violated at 26.5% (717/2707 eligible transitions). Violations are **spatially uniform** — no significant clustering by folio (chi2 p=0.69), line position (KS p=0.22), paragraph position (chi2 p=0.32), REGIME (chi2 p=0.22), or permutation test (folio p=0.28, regime p=0.27). However, violations are **structurally conditioned**: violation-hosting lines are significantly longer (+1.20 tokens, p<0.0001), have lower kernel density (-0.064, p<0.0001), and lower ENERGY density (-0.081, p<0.0001). PREFIX partially gates violation rate (chi2 p=0.051, borderline): qo-source at 1.89x enrichment, lsh-source at 0.21x. Per-pair variation is high (Gini=0.49, CV=0.93), with AX→FQ the most common violation category (171/717). Section specificity is borderline (p=0.028): BIO=0.217 vs RECIPE_B=0.292.

**Interpretation:** Forbidden pair violations are a **uniform grammar property**, not a context-dependent exception mechanism. The ~26.5% leakage rate is a constant of the grammar, not modulated by manuscript position, paragraph structure, or REGIME. However, violations preferentially occur in longer, less kernel-dense lines — suggesting that line structural complexity (more tokens, less core grammar) creates more opportunities for forbidden pairs to surface. The borderline PREFIX effect suggests PREFIX may partially gate which transitions are tolerable.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Class-level forbidden pairs | 84 (from 17 MIDDLE pairs) |
| Eligible transitions | 2,707 |
| Violations | 717 |
| Violation rate | 26.5% |
| MIDDLE-level violations | 13 (0.71%, near zero) |

### Spatial Uniformity Tests (all NON-significant)

| Test | Statistic | p-value | Verdict |
|------|-----------|---------|---------|
| Folio clustering (chi2) | 74.28 | 0.688 | UNIFORM |
| Line position (KS) | 0.045 | 0.221 | UNIFORM |
| Paragraph position (chi2) | 0.99 | 0.320 | UNIFORM |
| REGIME specificity (chi2) | 4.37 | 0.224 | UNIFORM |
| Section specificity (chi2) | 10.85 | 0.028 | BORDERLINE |
| PREFIX context (chi2) | 33.87 | 0.051 | BORDERLINE |
| Folio permutation | — | 0.283 | UNIFORM |
| Regime permutation | — | 0.272 | UNIFORM |

### Structural Conditioning (Test 7 — significant)

| Line Property | Violation Lines | Clean Lines | Diff | p-value |
|---------------|----------------|-------------|------|---------|
| Length | 7.55 | 6.35 | +1.20 | <0.0001 |
| Kernel density | 0.148 | 0.212 | -0.064 | <0.0001 |
| EN density | 0.393 | 0.474 | -0.081 | <0.0001 |
| CC density | 0.052 | 0.067 | -0.015 | 0.003 |
| FL density | 0.058 | 0.069 | -0.011 | 0.031 |
| Class diversity | 0.861 | 0.855 | +0.007 | 0.291 |
| Unique MIDDLE rate | 0.847 | 0.844 | +0.004 | 0.577 |

### Pair Variation

| Metric | Value |
|--------|-------|
| Gini coefficient | 0.49 |
| Rate CV | 0.93 |
| Rate range | 0.00 – 0.20 |
| Top category | AX→FQ (171 violations) |
| Second | EN→FQ (125 violations) |
| Third | AX→EN (113 violations) |

---

## Implications

1. **Violations are not "exception handling"** — they don't concentrate in specific REGIMEs, folios, or paragraph positions. No evidence for deliberate override mechanism.

2. **Violations are not scribal errors** — they're too evenly distributed and too frequent (26.5%) for random copying mistakes. They are a grammar-level property.

3. **The ~26.5% rate is a grammar constant** — it represents the degree to which class-level forbidden pairs are "soft" constraints rather than hard prohibitions. Confirms and refines C789.

4. **Structural conditioning** — violations preferentially occur in longer, less core-grammar-intensive lines. This suggests forbidden pairs surface when the grammar has more "room" for variant transitions.

5. **PREFIX gating (borderline)** — the p=0.051 PREFIX effect suggests that some prefixes may selectively tolerate forbidden transitions, consistent with PREFIX as the primary routing mechanism (C1015, C1024).

---

## Evidence

Results file: `phases/HAZARD_VIOLATION_ARCHAEOLOGY/results/hazard_violation_archaeology.json`
Script: `phases/HAZARD_VIOLATION_ARCHAEOLOGY/scripts/hazard_violation_archaeology.py`
