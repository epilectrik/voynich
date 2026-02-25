# C1308: Within-Paragraph Category Coherence

**Tier:** 2
**Scope:** B
**Phase:** CROSS_MODE_CATEGORY_COUPLING (460)
**Date:** 2026-02-25

## Finding

Both Mode A and Mode B lines within a paragraph share a common category "key." Within-paragraph A-B category divergence (JSD=0.141) is significantly less than cross-paragraph A-B divergence (JSD=0.170), with p=7.4e-6 (Mann-Whitney). The paragraph sets the operational domain; both modes operate within it.

## Evidence

- 258 paragraphs with both modes present
- Within-paragraph mean JSD: 0.141 (std=0.104)
- Cross-paragraph mean JSD: 0.170 (std=0.102)
- Mann-Whitney U=25947, p=7.42e-6

## Interpretation

Paragraphs function as operationally coherent units where both suffix mode tracks work in the same category domain. A THERMAL-heavy paragraph has THERMAL content in both its Mode A and Mode B lines. This is consistent with the paragraph independence model (C858) — each paragraph is a self-contained program addressing a specific operational concern, and both voices contribute to that concern.

## Note

This is a **refinement** of C1288 (folio-level paragraph coherence, within JSD=0.109 vs null=0.122, z=-4.92), not an independent finding. The shared category "key" is the paragraph's category profile inherited from the folio theme. The effect nests: folio imposes a theme → paragraphs inherit it → both modes within a paragraph share it at the finest grain.

## Extends

- C858 (paragraph independence) — adds category-level evidence for paragraph coherence
- C1258 (parallel mode tracks) — the parallel tracks share a paragraph-level "key"
- C1288 (within-folio paragraph coherence) — refines folio-level coherence to within-paragraph A-B level

## Falsifiability

Would be falsified if within-paragraph JSD >= cross-paragraph JSD (modes are category-independent within paragraphs).

## Evidence Files

- `phases/CROSS_MODE_CATEGORY_COUPLING/results/cross_mode_category_coupling.json` (T8)
