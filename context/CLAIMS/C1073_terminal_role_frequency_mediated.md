### C1073 — Terminal-Role Association Is Frequency-Mediated

- **Tier:** 2 (ESTABLISHED)
- **Scope:** B (MIDDLE terminal character x C591 role)
- **Phase:** TERMINAL_COMPATIBILITY_GEOGRAPHY (2026-02-15)

**Finding:** Terminal-character groups show highly distinctive C591 role profiles (V=0.4069, chi2=10634.7, p~0), but permutation null (shuffling terminal labels preserving per-MIDDLE token counts) produces equivalent or higher V (null mean=0.414, perm_p=0.582). The association is entirely mediated by token frequency: terminal characters create frequency neighborhoods, and frequency already determines role membership.

**Interpretation:** Terminal characters are NOT an independent pathway to role identity. The apparent role discrimination (e.g., 'n' terminal: 43% FQ, 16% CC; 'k' terminal: 91% EN) is a consequence of terminal groups having characteristic frequency distributions. Consistent with C986 (frequency as primary discrimination axis) and C985 (character-level features have limited power). Note: 'k'/'h'/'e' terminals showing 0% FL is tautological from C770 (FL Kernel Exclusion) — flagged as C908 consistency check, not novelty. 'y' terminal FL=1.7% quantifies C777's known FL terminal bias.

**Extends:** C1072 (terminal compatibility signal), C986 (frequency-based discrimination), C985 (character-level limits)
**Consistent with:** C777 (FL terminal bias), C770 (FL kernel exclusion), C908 (kernel correlation)

**Quantitative:**
- Contingency: 17 terminal groups x 5 roles, 16,054 classified tokens
- Observed V=0.4069, chi2=10,634.7, p~0
- Permutation null (1000x): mean V=0.414, perm_p=0.582
- Key profiles: 'n' FQ=43%/CC=16%; 'k' EN=91%; 'l' all 5 roles represented; 'm' FQ=47%/FL=28%
