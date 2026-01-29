# C848: A Paragraph RI Position Variance

**Tier:** 2
**Scope:** Currier-A
**Phase:** PARAGRAPH_INTERNAL_PROFILING

## Constraint

RI rate varies significantly by folio position. Middle paragraphs have the highest RI concentration (14.3%) despite being the shortest. RI is concentrated 3.84x higher in line 1 than body across all paragraphs.

## Evidence

**By folio position:**

| Position | n | RI Rate | Lines |
|----------|---|---------|-------|
| first | 86 | 9.3% | 5.35 |
| middle | 142 | **14.3%** | 2.75 |
| last | 86 | 11.8% | 5.36 |
| only | 28 | 7.1% | 11.79 |

Kruskal-Wallis H = 13.55, p = 0.001

**Line-1 concentration:**
- Mean RI concentration in line 1: **3.84x** (vs expected 1.85x from C833)
- This is much stronger than previously documented

## Interpretation

Middle paragraphs are short but RI-dense, suggesting they serve as metadata or header records. The inverse relationship between size and RI rate indicates structural specialization:
- Short paragraphs: RI-heavy (identification/registration)
- Long paragraphs: PP-heavy (operational content)

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C831 | CONFIRMS - RI three-tier structure |
| C833 | EXTENDS - Line-1 concentration stronger at paragraph level (3.84x vs 1.85x) |

## Provenance

- Script: `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/02_a_ri_profile.py`
- Data: `phases/PARAGRAPH_INTERNAL_PROFILING/results/a_ri_profile.json`

## Status

CONFIRMED
