# C1042: Section-Conditional Positional Exclusivity Reduction

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** SECTION_PARAMETERIZED_LINE_GRAMMAR (Phase 365)
**Qualifies:** C956 (positional token exclusivity, 192/334 at 2.72x shuffle)
**Relates to:** C941 (section is primary vocabulary organizer), C1029 (section-parameterized grammar)

---

## Statement

C956's zone-exclusive tokens (192/334 at 2.72x shuffle enrichment) retain only 30-55% exclusivity within individual sections:

| Section | Tested | Retained | Rate |
|---------|--------|----------|------|
| B (BIO) | 22 | 12 | 54.5% |
| C (COSMO) | 8 | 3 | 37.5% |
| H (HERBAL) | 24 | 13 | 54.2% |
| S (STARS_RECIPE) | 33 | 10 | 30.3% |

Global positional exclusivity is partially a **section composition effect**: tokens appear zone-locked globally because they concentrate in sections that deploy them in specific zones. The structural origin (confirmed by C956's negative control at 2.72x) remains valid; the section-mediation mechanism is additive, not a replacement.

---

## Evidence

- 36 globally exclusive tokens had sufficient per-section data (>= 2 occurrences)
- Per-section retention tested by verifying each token maintains single-zone exclusivity
- All 4 sections fall well below the 80% invariance threshold
- STARS_RECIPE shows weakest retention (30.3%), consistent with its largest vocabulary and greatest combinatorial freedom

---

## Interpretation

C956 is NOT falsified — the 2.72x enrichment over shuffle is real and structurally grounded. But the exclusivity is partially mediated by section composition. A token that appears only in INITIAL zone globally may do so because it primarily occurs in sections that happen to place it there. Within any single section, the same token may appear in multiple zones. Both facts are true simultaneously: the global pattern is real but compositionally constructed.

---

## Method

- 192 globally exclusive tokens from C956 mapped to their exclusive zone
- Per-section zone counts computed for each exclusive token
- Retention = fraction of tokens maintaining single-zone exclusivity within section
- Required >= 2 occurrences per token per section for inclusion
- H10 null hypothesis (>= 80% retention in all sections): FAIL

**Script:** `phases/SECTION_PARAMETERIZED_LINE_GRAMMAR/scripts/section_line_grammar.py`
**Results:** `phases/SECTION_PARAMETERIZED_LINE_GRAMMAR/results/section_line_grammar.json`
