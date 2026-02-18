# C1100: Rosettes-T Jaccard Correlation Is Bridge-Mediated

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** GLOBAL
**Phase:** BRIDGE_BACKBONE_MANUSCRIPT_SURVEY (Phase 390)
**Qualifies:** C1090 (Rosettes-T correlation)
**Strengthens:** C1098 (structural index), C1096 (bridge enrichment)

---

## Statement

The C1090 finding that all Rosettes regions correlate most with Section T by Jaccard is fully mediated by bridge vocabulary. When MIDDLEs are split into bridge and non-bridge subsets:

| Jaccard Type | Winner | Runner-up | T Rank |
|-------------|--------|-----------|--------|
| ALL MIDDLEs | T (0.241) | B (0.226) | 1 |
| BRIDGE only | S (0.893) | H (0.882) | 7 |
| NON-BRIDGE only | B (0.128) | T (0.128) | 2 (tied) |

T wins the overall Jaccard but drops to tied-2nd when bridge MIDDLEs are removed. The mechanism is **Jaccard size sensitivity**: T has the fewest unique MIDDLEs (290) of any section, producing the smallest union denominator and inflating the overlap ratio. Since bridge MIDDLEs are shared at very high rates across all sections (bridge Jaccards 0.77-0.89), the section with the smallest vocabulary wins the overall metric by arithmetic, not by meaningful content similarity.

---

## Evidence

### Mediation Test (3-way Jaccard decomposition)

**ALL-MIDDLE Jaccard ranking:**
1. T = 0.241
2. B = 0.226
3. A = 0.218
4. C = 0.215
5. P = 0.205
6. Z = 0.194
7. S = 0.194
8. H = 0.173

**NON-BRIDGE Jaccard ranking:**
1. B = 0.128
2. T = 0.128 (tied)
3. S = 0.128 (tied)
4. H = 0.111
5. A = 0.109
6. P = 0.104
7. C = 0.103
8. Z = 0.100

**BRIDGE Jaccard ranking:**
1. S = 0.893
2. H = 0.882
3. P = 0.877
4. B = 0.817
5. A = 0.785
6. T = 0.783
7. C = 0.744
8. Z = 0.772

### Mediation Verdict

T wins ALL but loses NON-BRIDGE → **FULL_MEDIATION**. Bridge vocabulary fully explains the Rosettes-T correlation. The non-bridge Jaccard shows B, T, and S essentially tied at 0.128 — the Rosettes has no preferential non-bridge vocabulary overlap with any single section.

### Size Sensitivity

Section T has 290 unique MIDDLEs — the smallest vocabulary of any section. The Jaccard denominator |Rosettes ∪ Section| is smallest for T, inflating the ratio. This is not an error in C1090 but an artifact of the metric choice. The correlation is real but its interpretation changes: T doesn't share special content with Rosettes — it has the smallest vocabulary, making any shared items produce a larger ratio.

---

## Implication

C1090 should be read as: "Rosettes vocabulary overlaps with all sections at similar rates, but the overlap ratio is inflated for small-vocabulary sections (T) by Jaccard's size sensitivity." The Rosettes is not specifically a Section T index — it is a universal bridge vocabulary index (C1098) whose non-bridge tail vocabulary is evenly spread across B, T, and S sections.

This strengthens the structural index interpretation (C1098): the Rosettes indexes the bridge backbone of the entire grammar, not any particular section's content.

---

## Provenance

- Phase: 390 (BRIDGE_BACKBONE_MANUSCRIPT_SURVEY), Test P5
- Script: `phases/BRIDGE_BACKBONE_MANUSCRIPT_SURVEY/scripts/bridge_backbone_survey.py`
- Results: `phases/BRIDGE_BACKBONE_MANUSCRIPT_SURVEY/results/bridge_backbone_survey.json`
- Related: C1090, C1096, C1098, C1013
