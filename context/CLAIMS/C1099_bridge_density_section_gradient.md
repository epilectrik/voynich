# C1099: Bridge Density Section Gradient

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** GLOBAL
**Phase:** BRIDGE_BACKBONE_MANUSCRIPT_SURVEY (Phase 390)
**Extends:** C1013 (bridge MIDDLEs), C909 (section-specific vocabulary)
**Tension with:** C299 (Section T generic vocabulary)

---

## Statement

Bridge MIDDLE density (fraction of unique folio MIDDLEs that are bridges) varies massively by manuscript section (Kruskal-Wallis H=129.0, p≈0). The ranking is:

| Rank | Section | Mean Density | N Folios |
|------|---------|-------------|----------|
| 1 | H (Herbal) | 0.697 | 129 |
| 2 | B (Bio) | 0.603 | 20 |
| 3 | P (Pharma) | 0.564 | 16 |
| 4 | C (Cosmo) | 0.536 | 7 |
| 5 | Z (Zodiac) | 0.506 | 12 |
| 6 | A (Astro) | 0.480 | 8 |
| 7 | S (Stars) | 0.480 | 23 |
| 8 | T (Text) | 0.453 | 4 |

Section T has the **lowest** bridge density — the opposite of the prediction from C299 (67.7% of T MIDDLEs appear in B baseline). Section H (Herbal) has the highest, meaning the viability backbone runs through Herbal, not Text.

---

## Evidence

### Kruskal-Wallis Test
- H statistic: 129.0
- p-value: ≈0 (reported as 0.0 at machine precision)
- 8 sections, 219 folios total

### Section T Details
- 4 folios, mean bridge density 0.453
- 290 unique MIDDLEs, 73 bridges (25.2%)
- Mann-Whitney U (T vs non-T): U=79.5, p=0.9974 (T is NOT higher than average)
- Rank 8 of 8 — dead last

### C299 Paradox Resolution
C299 reports that 67.7% of Section T MIDDLEs appear in B (vs 42.4% baseline). This was interpreted as T being "generic." But generic-within-B does not mean bridge-enriched. Bridge MIDDLEs are specific: the 85 items that cross from A's discrimination manifold into B's grammar. T's vocabulary is generic B vocabulary, not cross-system bridge vocabulary.

---

## Implication

The viability backbone (C1013-C1014: 85 bridges carrying 91% of viability signal) is concentrated in the Herbal section, not the Text section. This is consistent with C1085 (Bio distinctive operational mode) and the Herbal section's role as the manuscript's dominant content section (129 folios). Herbal programs use the most broadly connective vocabulary — they are the bridge-dense core of the grammar.

---

## Provenance

- Phase: 390 (BRIDGE_BACKBONE_MANUSCRIPT_SURVEY), Test P1/P2
- Script: `phases/BRIDGE_BACKBONE_MANUSCRIPT_SURVEY/scripts/bridge_backbone_survey.py`
- Results: `phases/BRIDGE_BACKBONE_MANUSCRIPT_SURVEY/results/bridge_backbone_survey.json`
- Related: C1013, C1014, C299, C909, C1085
