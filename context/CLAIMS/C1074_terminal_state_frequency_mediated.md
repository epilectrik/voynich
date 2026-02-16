### C1074 — Terminal-State Association Is Frequency-Mediated

- **Tier:** 2 (ESTABLISHED)
- **Scope:** B (MIDDLE terminal character x C976 6-state automaton)
- **Phase:** TERMINAL_COMPATIBILITY_GEOGRAPHY (2026-02-15)

**Finding:** Terminal-character groups show distinctive C976 macro-state profiles even after excluding the dominant AXM state (non-AXM V=0.4165, chi2=3602.4, p~0), but permutation null (frequency-matched random groupings, 1000x) produces even higher V (null mean=0.5287, perm_p=0.992). The terminal-state association is entirely frequency-mediated. FL_SAFE has only 0.8% mass (C1015); minimum expected cell count=0.02 confirms sparsity.

**Interpretation:** Like C1073 for roles, terminal characters do not provide independent access to macro-state identity. The frequency gradient that defines terminal neighborhoods is sufficient to explain all observed state-profile variation. T1 and T2 are orthogonal (T1 discriminates EN vs AX merged in T2; T2 discriminates FL_HAZ vs FL_SAFE merged in T1), so the frequency-mediation conclusion holds on both axes independently.

**Extends:** C1072 (terminal compatibility signal), C976 (6-state minimal automaton), C986 (frequency-based discrimination)
**Consistent with:** C1015 (FL_SAFE 0.8% mass), C977 (macro-state convergence)

**Quantitative:**
- Full contingency: 17 terminals x 6 states, V=0.3198
- Non-AXM: 5,191 tokens, V=0.4165, chi2=3602.4
- FL-collapsed (FL_HAZ + FL_SAFE): V=0.3479
- Permutation null: mean V=0.5287, perm_p=0.992
- FL_SAFE minimum expected cell count: 0.02
