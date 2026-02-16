### C1068 — Cross-Layer Partial Coupling (C475 x C911)

- **Tier:** 2 (ESTABLISHED)
- **Scope:** B (MIDDLE compatibility x PREFIX restriction)
- **Phase:** MULTI_LAYER_COMPATIBILITY_ARCHITECTURE (2026-02-15)

**Finding:** Three morphological constraint layers show mixed independence. C475 (MIDDLE compatibility) and C911 (PREFIX x MIDDLE forbidden pairs) exhibit moderate coupling (NMI=0.185), partially frequency-mediated (permutation null mean=0.070, p=0.13). C475 x C1063 (PREFIX x SUFFIX) and C911 x C1063 are independent (NMI=0.005 and 0.002 respectively).

**Interpretation:** MIDDLEs with higher C475 compatibility degree tend to face more C911 prefix restrictions, but this coupling is largely driven by frequency — common MIDDLEs naturally appear in more testing pools. The PREFIX x SUFFIX forbidden layer (C1063) operates on a fully independent axis. Two of three constraint layers are orthogonal; the MIDDLE-centric layers (C475, C911) share a frequency-mediated coupling.

**Extends:** C1003 (pairwise sufficiency — no three-way synergy), C660 (PREFIX x MIDDLE selectivity)

**Quantitative:**
- C475 x C911: chi²=1367.0, p=3.4e-292, V=0.177, NMI=0.185, perm_null_p=0.13
- C475 x C1063: chi²=36.4, p=2.3e-6, V=0.029, NMI=0.005
- C911 x C1063: chi²=45.5, p=3.1e-9, V=0.032, NMI=0.002
- n=21,711 tokens with valid MIDDLE in 972-matrix
