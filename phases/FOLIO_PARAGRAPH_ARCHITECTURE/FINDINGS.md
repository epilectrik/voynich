# FOLIO_PARAGRAPH_ARCHITECTURE Findings

## Executive Summary

**Central Question:** Are folios organized as Template model (Par 1 sets profile) or Parallel Programs model (independent mini-programs)?

**Answer:** HYBRID - Role template with vocabulary independence.

Paragraphs share a **role profile** (EN/FL/FQ/CC ratios consistent) but have **independent vocabulary** (only 11.4% reuse from Par 1). This is neither pure template nor pure parallel, but a role-constrained independence pattern.

---

## Key Findings

### 1. Primary Cohesion Source (Script 01)

| Source | Score | Rank |
|--------|-------|------|
| Role similarity | 0.831 | 1st |
| Prefix overlap | 0.300 | 2nd |
| Vocabulary | 0.061 | 3rd |
| HT overlap | 0.024 | 4th |

**Conclusion:** Paragraphs cohere through ROLE PROFILES, not shared vocabulary.

---

### 2. Vocabulary Distribution (Script 02)

- Par 1 contains only **27.4%** of folio-unique vocabulary
- Gini coefficient: **0.279** (distributed)
- Cumulative by ordinal: 27% → 50% → 67% → ...

**Conclusion:** Folio-unique vocabulary is DISTRIBUTED across paragraphs, not concentrated in Par 1.

---

### 3. First Paragraph Role (Script 03)

| Metric | Par 1 | Later | Verdict |
|--------|-------|-------|---------|
| HT rate | 34.6% | 36.8% | No elevation |
| Vocab size | 47.2 | 30.1 | Larger but not special |
| Predictivity | - | 11.8% | Par 1 doesn't predict later |
| Role delta | EN +0.5%, FL +0.5% | - | Negligible difference |

**Conclusion:** Par 1 is NOT structurally distinct. Just the first in a sequence of equals.

---

### 4. Paragraph Count and Complexity (Script 04)

| Correlation | rho |
|-------------|-----|
| Par count vs vocabulary | 0.836 |
| Par count vs tokens | 0.802 |
| Par count vs role diversity | 0.826 |

Section F-ratio: **10.85** (significant)

**Conclusion:** Paragraph count REFLECTS folio complexity. More paragraphs = richer vocabulary and more diverse roles.

---

### 5. Paragraph Convergence (Script 05)

| Pattern | Finding |
|---------|---------|
| Vocabulary similarity | FLAT (0.055 → 0.045) |
| Role distance | INCREASING (0.259 → 0.329) - divergent |
| Cumulative overlap | INCREASING (14.2% → 38.6%) - convergent |
| Last paragraph | NOT distinct |

**Conclusion:** Paragraphs CONVERGE in vocabulary (more reuse over sequence) but DIVERGE in role execution (more variation).

---

### 6. Section Patterns (Script 06)

| Section | Pars/Folio | Cohesion | Pattern |
|---------|------------|----------|---------|
| HERBAL_B | 2.2 | 0.070 | Few, cohesive |
| BIO | 7.5 | 0.071 | Medium, cohesive |
| RECIPE_B | 10.2 | 0.053 | Many, moderate |
| PHARMA | 14.0 | 0.056 | Many, moderate |

**Conclusion:** Sections organize paragraphs differently. HERBAL_B uses few large paragraphs; RECIPE_B/PHARMA use many smaller ones.

---

### 7. LINK and Hazard Distribution (Script 07)

| Metric | Header | Body |
|--------|--------|------|
| LINK | 20.6% | 79.4% |
| Hazard FL | 19.1% | 80.9% |

LINK and hazard rates are **evenly distributed** across paragraph ordinals (CV 0.16-0.21).

**Conclusion:** LINK and hazard are distributed within paragraph bodies, not concentrated in specific paragraph positions.

---

### 8. Template Test (Script 08)

| Component | Score | Interpretation |
|-----------|-------|----------------|
| Vocabulary reuse | 0.114 | LOW - independent |
| Role correlation | 0.858 | HIGH - template |
| Role stability | 0.897 | HIGH - template |
| **Combined** | **0.623** | TEMPLATE (borderline) |

**Conclusion:** Template model wins but for role stability, NOT vocabulary. Paragraphs execute the same role profile independently.

---

## Integrated Model

```
FOLIO (Program Unit)
├── Role Profile: FIXED template (EN/FL/FQ/CC ratios)
├── Vocabulary Pool: SHARED but not prescribed
└── Paragraphs: INDEPENDENT mini-programs
    ├── Same role proportions as folio
    ├── Different vocabulary selections
    └── Vocabulary converges over sequence
```

### Key Insight

The folio defines **what proportions** of operations to use (role profile), but each paragraph independently decides **which specific operations** (vocabulary). This is constraint satisfaction, not instruction following.

---

## Constraints Produced

| # | Name | Statement |
|---|------|-----------|
| C855 | Folio Role Template | Paragraphs share role profile (0.831 cohesion) not vocabulary (0.061) |
| C856 | Vocabulary Distribution | Folio-unique vocab distributed (Gini 0.279), Par 1 has 27.4% |
| C857 | First Paragraph Ordinariness | Par 1 not structurally distinct, predicts only 11.8% of later vocab |
| C858 | Paragraph Count Complexity | Par count reflects complexity: rho 0.836 vocab, 0.826 diversity |
| C859 | Vocabulary Convergence | Cumulative overlap increases: 14.2% → 38.6% over sequence |
| C860 | Section Paragraph Organization | Sections differ: HERBAL_B 2.2 pars vs PHARMA 14.0 |
| C861 | LINK/Hazard Paragraph Neutrality | LINK/hazard evenly distributed across ordinals (CV < 0.21) |
| C862 | Role Template Verdict | Template score 0.623: role stability (0.897) not vocab (0.114) |

---

## Cross-References

| Finding | Related Constraints |
|---------|-------------------|
| Role cohesion | C552 (section role profiles) |
| Vocab distribution | C531 (folio unique vocab), C620 (folio network) |
| Section patterns | C552 (section role profiles) |
| LINK distribution | C821-C823 (regime-line syntax) |

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Folios analyzed | 82 |
| Paragraphs | 585 |
| Mean pars/folio | 7.1 |
| Intra-folio Jaccard | 0.061 |
| Role cohesion score | 0.831 |
| Template score | 0.623 |
