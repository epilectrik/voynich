# C641: PP Population Execution Profiles

**Tier:** 2 | **Status:** CLOSED | **Scope:** CROSS_SYSTEM | **Source:** A_TO_B_ROLE_PROJECTION

## Statement

AZC-Mediated and B-Native PP populations differ in B-side behavioral profiles across multiple dimensions: role composition (Fisher p=0.006 AX, p=0.001 EN), REGIME distribution (MW p=0.0004 REGIME_2, p<0.0001 REGIME_3), and suffix diversity (MW p<0.0001, confounded by frequency rho=0.795). EN sub-family membership is **partially predictable from A-record composition**: PREFIX-to-EN-score correlation is rho=0.510 (partially independent), QO-dominant A records are smaller (5.5 vs 7.4 tokens, p<0.0001), have fewer PP MIDDLEs (5.2 vs 6.9, p=0.0001), and are enriched for ANIMAL material class (19.7% vs 12.2%, Fisher p=0.0034).

## Evidence

### Role Profile (Fisher's Exact, Matched PP)

| Role | AZC-Med Rate | B-Native Rate | Fisher p |
|------|-------------|--------------|----------|
| AX | 53.1% (43/81) | 0.0% (0/8) | 0.0057 * |
| CC | 0.0% (0/81) | 0.0% (0/8) | 1.0 |
| EN | 40.7% (33/81) | 100.0% (8/8) | 0.0014 * |
| FL | 4.9% (4/81) | 0.0% (0/8) | 1.0 |
| FQ | 1.2% (1/81) | 0.0% (0/8) | 1.0 |

B-Native matched PP is 100% single-role vs AZC-Med 48.1% (Fisher p=0.0061).

### FL Hazard Participation

AZC-Med: 21.0% (17/81) participate in FL classes; B-Native: 0.0% (0/8). Fisher p=0.345 (NS, underpowered).

### REGIME Profile (All 404 PP MIDDLEs, B-Token Pass)

| REGIME | AZC-Med Mean | B-Native Mean | MW p |
|--------|-------------|--------------|------|
| REGIME_1 | 0.272 | 0.313 | 0.335 |
| REGIME_2 | 0.296 | 0.266 | 0.0004 * |
| REGIME_3 | 0.062 | 0.054 | <0.0001 * |
| REGIME_4 | 0.369 | 0.368 | 0.097 |

AZC-Med PP MIDDLEs are more concentrated in REGIME_2 and REGIME_3; B-Native lean toward REGIME_1.

### Suffix Pattern (All PP with B-side Data)

| Metric | AZC-Med | B-Native | MW p |
|--------|---------|----------|------|
| Suffix diversity (mean) | 4.49 | 1.83 | <0.0001 * |
| Bare rate (mean) | 0.231 | 0.123 | <0.0001 * |

Frequency-diversity correlation: rho=0.795 (p<0.0001). Frequency confounds suffix diversity — AZC-Med's higher frequency explains most of the diversity difference.

### EN Sub-Family Prediction from A Records

60 PP MIDDLEs have EN class membership: 39 CHSH, 18 QO, 3 MIXED. Classifying 1521 A records by mean QO score yields 1307 CHSH-dominant, 38 QO-dominant, 176 mixed.

| Comparison | QO Records | CHSH Records | MW p |
|-----------|-----------|-------------|------|
| Record size | 5.5 | 7.4 | <0.0001 * |
| PP count | 5.2 | 6.9 | 0.0001 * |
| RI count | 0.3 | 0.5 | 0.202 |

PREFIX-to-EN correlation: rho=0.510, p<0.0001 (n=1436). EN sub-family signal is **partially independent of PREFIX** — knowing a record's PREFIX composition captures about half the EN sub-family signal, but not all.

Material class: QO-dominant records have higher ANIMAL rate (19.7% vs 12.2%, Fisher p=0.0034).

## Interpretation

The two PP populations (AZC-Mediated and B-Native) behave differently in B-side execution: they favor different REGIMEs, show different suffix complexity (though confounded), and have sharply different role profiles. This supports a **functional bifurcation** in the A-to-B pipeline, where AZC-Mediated MIDDLEs serve diverse B roles while B-Native MIDDLEs serve narrow EN functions.

The EN sub-family prediction from A records demonstrates that **B's execution pathway (QO vs CHSH) is partially encoded in A record structure**: QO-dominant records are smaller, have fewer PP, and are materially enriched for ANIMAL. The PREFIX partially captures this signal (rho=0.510), but substantial residual signal exists — the EN sub-family choice is not merely a PREFIX artifact.

**Caveat:** B-Native has only 8 matched MIDDLEs (vs 81 AZC-Med). All Fisher and role tests for B-Native are severely underpowered. The REGIME and suffix comparisons use all 404 PP MIDDLEs via B-token pass and are more robust.

## Extends

- **C498**: Population bifurcation confirmed at behavioral level, not just membership
- **C640**: Role projection foundation; populations differ in role profile
- **C604**: REGIME mediates ch_preference — now shown to differ by PP population pathway

## Related

C498, C604, C637, C640

## Provenance

- **Phase:** A_TO_B_ROLE_PROJECTION
- **Date:** 2026-01-26
- **Script:** population_profiles.py
