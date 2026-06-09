# C957: Token-Level Bigram Constraints

**Tier:** 2 | **Scope:** B | **Phase:** LINE_CONTROL_BLOCK_GRAMMAR

> **STRENGTHENED (2026-06-08, SELF_CITATION_HEAD_TO_HEAD P4a verification):** directionality
> independently confirmed at strict word-adjacency -- all 9 forbidden bigrams at 0 observed vs
> ~37.5 joint within-line-shuffle expectation (P ~ 5e-17), while ALL reverse directions are
> at-or-above expectation (e.g. qokain->ol 12 obs vs 7.4 exp). With C783's class-level
> projection demoted, **this token-bigram layer is the surviving directional prohibition
> structure of the hazard topology.** Note the within-line analytic expectations here (2.0-7.3
> per pair) are smaller than this file's corpus-wide expectations; the joint zero is what
> carries the significance.

## Statement

26 mandatory bigrams (obs/exp > 5.0) and 9 forbidden bigrams (obs = 0, exp >= 5.0) exist at the token level, beyond the known or->aiin (C561). Two forbidden bigrams are genuinely token-specific (same ENERGY class), not explained by role separation.

## Evidence

- 334 common tokens, 10,061 bigrams analyzed
- Mandatory: 26 total (25 new beyond or->aiin). Top: r->ain (32.8x), sar->ain (23.7x), s->aiin (22.5x)
- or->aiin validated at 11.2x (C561 confirmed)
- Forbidden: 9 total. 7 role-expected (different roles), 2 token-specific:
  - chey -> chedy (exp = 6.37, both ENERGY_OPERATOR, classes 31 vs 8)
  - chey -> shedy (exp = 5.31, both ENERGY_OPERATOR, classes 31 vs 8)
- Shuffle: 0.6 +/- 0.8 forbidden (p = 0.000)
- Negative control: effect is STRUCTURAL (survives token-identity destruction)

## Interpretation

Most bigram constraints are role-driven, but the two within-ENERGY forbidden bigrams (chey cannot precede chedy or shedy) represent genuine token-level syntax — a rare instance where specific token identity matters beyond role.

## Provenance

- `phases/LINE_CONTROL_BLOCK_GRAMMAR/scripts/02_mandatory_forbidden_bigrams.py`
- Related: C561, C389, C109
