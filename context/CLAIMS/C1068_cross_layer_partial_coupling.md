### C1068 — Cross-Layer Coupling Marginal at Proper Null [DEMOTED Tier 2→3, REFRAMED 2026-05-19]

- **Tier:** 3 (was Tier 2) | **Status:** DEMOTED via audit
- **Scope:** B (MIDDLE compatibility x PREFIX restriction)
- **Phase:** MULTI_LAYER_COMPATIBILITY_ARCHITECTURE (2026-02-15); audit clearance from `phases/C475_AUDIT/` (2026-05-19, C475 demotion follow-up)

**REVISED CLAIM (Tier 3):** C475_degree × C911_restriction shows **marginal cross-layer coupling that does not cleanly clear permutation null** (NMI=0.185 vs null mean 0.070, **perm_null_p = 0.13**, not significant at α=0.05). Coupling is plausibly real but cannot be distinguished from frequency mediation. Coexists with **clean independence findings** for the C1063 (PREFIX × SUFFIX) layer.

**Why demoted from Tier 2:**

The chi² p-value (3.4e-292) looks devastating but tests against the **wrong null** (assumes independent marginals; both C475_degree and C911_restriction are frequency-correlated because both inherit token-frequency distribution). The methodologically appropriate null is the **permutation null preserving marginal distributions**, which gives **NMI null mean 0.070, p = 0.13**.

Modern discipline (post-PHASE_700) requires permutation null significance for cross-layer coupling claims at Tier 2. C1068 fails this threshold by a meaningful margin (p=0.13 vs target <0.05). The original constraint text was self-aware ("partially frequency-mediated") and explicitly cited perm_null_p=0.13, but the Tier 2 status was too generous. Demotion preserves the substantive observation while honest about its statistical strength.

**Quantitative (unchanged from original):**
- C475_degree × C911_restriction: chi²=1367.0, p=3.4e-292, V=0.177, **NMI=0.185, perm_null_p=0.13** ← demoted: marginal
- C475_degree × C1063_restriction: chi²=36.4, p=2.3e-6, V=0.029, **NMI=0.005** ← clean: independent
- C911_restriction × C1063_restriction: chi²=45.5, p=3.1e-9, V=0.032, **NMI=0.002, perm_null_p=0.91** ← clean: independent
- n=21,711 tokens with valid MIDDLE in 972-matrix

**What survives (preserved within this demotion):**

The companion findings for the C1063 layer are methodologically robust at any reasonable threshold:
- C475_degree × C1063: NMI=0.005 (near-zero, clearly independent)
- C911_restriction × C1063: NMI=0.002, perm_p=0.91 (clearly independent)

These establish the PREFIX × SUFFIX layer (C1063) is genuinely orthogonal to both compatibility-degree and PREFIX-restriction. Per expert consultation, these are preserved within the C1068 narrative rather than split into a separate Tier 2 constraint (surgical overkill).

**C475-wholesale-graph concern audit (cleared):**

C1068 was flagged AUDIT_PENDING in the C475 demotion commit (`phases/C475_AUDIT/`) because of concern that C475 graph's sparsity-driven edges might inflate the cross-layer NMI. **Audit cleared this concern:** C1068's methodology uses `c475_degree[mid] = compat_matrix[i].sum()` — per-MIDDLE OBSERVED co-occurrence count. This is the methodologically-clean attested-pair side of C475 (equivalent to C729's framing), NOT the sparsity-driven "95.7% illegal pairs" framing that got demoted. C1068's marginality has its own origin (frequency-correlated marginals in chi² test) unrelated to C475's sparsity issue.

**Methodology lesson:** [feedback_chi2_vs_permutation_null_mismatch.md](memory) — Chi² tests against independence null assume marginals are independent; when both factors correlate with token frequency, chi² will reject independence trivially while marginal-preserving permutation null gives the correct (marginal) p-value. Required control for cross-layer NMI/coupling claims is permutation null preserving marginal distributions.

**Extends:** C1003 (pairwise sufficiency — no three-way synergy), C660 (PREFIX × MIDDLE selectivity)

**Provenance:** Original test `phases/MULTI_LAYER_COMPATIBILITY_ARCHITECTURE/scripts/multi_layer_compatibility.py` T1; audit narrative added 2026-05-19 as follow-up to C475 demotion.
