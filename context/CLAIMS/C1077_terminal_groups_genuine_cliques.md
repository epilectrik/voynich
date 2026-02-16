### C1077 — Terminal Compatibility Groups Form Genuine Cliques

- **Tier:** 2 (ESTABLISHED)
- **Scope:** B (MIDDLE terminal character x C475 compatibility transitivity)
- **Phase:** TERMINAL_COMPATIBILITY_GEOGRAPHY (2026-02-15)

**Finding:** 3 of 5 pre-registered terminal groups (from C1072) show within-group compatibility significantly above frequency-band-matched null: 'n' (clique fraction 0.330 vs null 0.081, ratio 4.07x, p=0.000), 'y' (0.156 vs 0.046, 3.40x, p=0.001), 'l' (0.049 vs 0.020, 2.52x, p=0.014). Two groups narrowly miss: 'r' (2.58x, p=0.052) and 'm' (3.24x, p=0.085, only 8 MIDDLEs / 28 pairs). Global compatibility rate is 2.17%. Global clustering coefficient is 0.873 (C983), confirming the compatibility graph is inherently transitive — but terminal groups exceed even this high baseline.

**Interpretation:** Terminal-character groups are not just sparsely enriched for compatible pairs — they form genuine cliques where compatibility is transitive within the group at rates well above what frequency-matched random groups achieve. This establishes that terminal character identity captures a real structural neighborhood in the compatibility graph, not just a statistical artifact. The 'n' group is the strongest clique (33% of all pairs compatible, 4x null), suggesting MIDDLEs ending in 'n' share deep functional similarity. The 'm' group's high ratio (3.24x) but marginal p-value reflects its small size (8 MIDDLEs).

**Extends:** C1072 (terminal compatibility signal — 5 elevated groups), C475 (MIDDLE incompatibility), C983 (global clustering 0.873)
**Consistent with:** C986 (frequency control in null), C995 (affordance neighborhoods)

**Quantitative:**
- 5 pre-registered groups tested (from C1072):
  - 'n': 14 MIDDLEs, 91 pairs, 30 compatible, fraction=0.330, null=0.081, ratio=4.07x, p=0.000
  - 'y': 22 MIDDLEs, 231 pairs, 36 compatible, fraction=0.156, null=0.046, ratio=3.40x, p=0.001
  - 'l': 51 MIDDLEs, 1275 pairs, 63 compatible, fraction=0.049, null=0.020, ratio=2.52x, p=0.014
  - 'r': 32 MIDDLEs, 496 pairs, 25 compatible, fraction=0.050, null=0.020, ratio=2.58x, p=0.052
  - 'm': 8 MIDDLEs, 28 pairs, 5 compatible, fraction=0.179, null=0.055, ratio=3.24x, p=0.085
- Elevated (>2x null, p<0.05): 3/5
- Global compatibility rate: 2.17%
- C983 global clustering: 0.873 (z=+136.9)
