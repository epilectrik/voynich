# C1246: Mode-Differentiated Cross-Lane Pairing

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** EN_CROSS_LANE_PAIRING (Phase 444)
**Extends:** C1242 (cross-lane content prediction), C1229 (alternating suffix modes), C1230 (mode MIDDLE differentiation)
**Relates to:** C1231 (universal suffix modes), C1245 (selectivity gradient)

---

## Statement

Mode A (specification/terminal-heavy) and Mode B (execution/bare-heavy) lines use genuinely different cross-lane QO-CHSH pairings (Jensen-Shannon divergence z=4.60, 1000 permutations). Mode A has tighter heat-measure coupling (MI=1.425 bits vs Mode B MI=0.978 bits).

**Mode A enriched pairs** (specification = setting parameters):
- k-ck (5.08x), ke-ey (3.69x), ke-e (1.98x), k-eck (1.56x)
- Energy MIDDLEs paired with specific measurement MIDDLEs

**Mode B enriched pairs** (execution = running the process):
- k-eol (6.50x), l-edy (3.32x), edy-edy (3.13x), l-e (2.53x)
- Sustained/equilibrium MIDDLEs paired with passive monitoring

The pattern: specification lines lock energy operations to targeted checks; execution lines pair routine operations with generic monitoring. This extends C1230's MIDDLE-family differentiation (k-family enriched in A, e-family in B) to the cross-lane pairing level — not just which MIDDLEs appear in each mode, but which heat-measure combinations they form.

---

## Method

- 47 paragraphs assessed for mode assignment (k-means on suffix profiles, silhouette > 0.3, 8+ body lines)
- 557 lines with mode labels (Mode A and Mode B)
- 546 Mode A pairs, 756 Mode B pairs
- JSD with 1000 permutations (shuffle mode labels across lines)
- Enrichment computed as Mode A fraction / Mode B fraction (threshold: ratio > 1.3x, count >= 5)

**Script:** `phases/EN_CROSS_LANE_PAIRING/scripts/cross_lane_pairing.py` (T6)
**Results:** `phases/EN_CROSS_LANE_PAIRING/results/cross_lane_pairing.json`
