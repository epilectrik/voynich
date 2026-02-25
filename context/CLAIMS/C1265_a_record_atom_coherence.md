# C1265: A Record Atom-Profile Coherence (Independent of Category)

**Tier:** 2
**Scope:** A
**Phase:** A_CATEGORY_SCATTERSHOT (Phase 452)
**Date:** 2026-02-24

## Statement

A records show within-record atom-profile coherence beyond what the 8-category system explains. Mean pairwise cosine similarity of MIDDLE AXIS vectors within records: 0.272 vs null 0.238 (d=11.6, p<0.001). Residual check: same-category MIDDLE pairs within records have cosine 0.529 vs null 0.238 -- atom coherence persists after controlling for category. The AXIS cluster system (C1207) and operational category system (C1250) carry complementary organizational information.

## Architecture

- **Atoms organize records independently of categories.** Two MIDDLEs can be in the same category but have very different atom profiles (e.g., both THERMAL but one is k-heavy, another e-heavy). Records prefer MIDDLEs with similar atom profiles even within the same category.
- **Dual organizational axes.** A records are organized by both: (1) operational category (C1261, d=9.7) and (2) atom-level composition (C1265, d=11.6, with independent residual). These are complementary, not redundant.
- **AXIS clusters (C1207) apply to A.** Originally discovered in B-internal atom profiling, the AXIS cluster system (ITERATION, MONITORING, ENERGY, CLOSURE, STRUCTURAL, STABILITY, FREE, OTHER) structures A's registry as well.

## Key Findings

| Metric | Value |
|--------|-------|
| Observed mean cosine | 0.272 |
| Null mean cosine | 0.238 +/- 0.003 |
| Cohen d | 11.6 |
| p-value | <0.001 |
| Records tested | 1,539 |
| Same-cat pair cosine | 0.529 |
| Residual vs null | +0.291 |

## Provenance

- Builds on C1207 (AXIS clusters), C1251 (atom-level structure)
- Extends C1261 (record category coherence) with independent residual test
- AXIS cluster definitions from atom_profiles.py (C1207)
