# C1030: M2 Gap Decomposition — Two Independent Mechanisms

**Tier:** 2 | **Scope:** B | **Phase:** SECTION_GRAMMAR_VARIATION

## Statement

The M2 20% gap (12/15 tests in C1025) decomposes into TWO independent mechanisms, not three. B4 (role rank order) is misspecified: M2 trivially reproduces real self-loop rates (FQ=0.0952, FL=0.0493, EN=0.0695 — identical to real data because M2 copies the transition matrix diagonal). The corrected M2 pass rate is 13/15 = 86.7%.

The two remaining failures are independent:
- **B5 (forward-backward asymmetry):** M2 overestimates JSD by 3.85x (0.178 vs 0.046). Requires PREFIX symmetric routing mechanism (C1024).
- **C2 (CC suffix-free rate):** CC tokens are 100% suffix-free. Requires role-specific morphological constraints outside M2's scope.

B5 and C2 are independent: C2 is constant at 1.0 across all sections (zero variance), while B5 varies by section (0.086–0.245). No shared latent mechanism.

## B4 Correction

Phase 348 (C1025) defined B4 as: "Does FQ > FL > EN self-transition ordering hold?"

**Problem:** This tests whether an ordering property holds, not whether M2 matches real data. The real data does NOT have FQ > FL > EN — it has FQ > EN > FL globally. Both real and M2 "fail" B4, meaning M2 correctly matches real structure.

**Root cause:** The ordering is section-dependent (see C1029). BIO has EN > FQ > FL (thermal dominance); COSMO and STARS_RECIPE have FQ > FL > EN. No universal ordering exists.

**Correction:** B4 should count as PASS (M2 matches real). Corrected M2 pass rate: 13/15 = 86.7%.

## B5 Analysis

| Property | Value |
|----------|-------|
| Real forward-backward JSD | 0.046 |
| M2 forward-backward JSD | 0.178 |
| Ratio (M2/real) | 3.85x |

### Per-Role Asymmetry

| Role | JSD |
|------|-----|
| FQ | 0.030 |
| EN | 0.040 |
| FL | 0.062 |
| CC | 0.062 |
| AX | 0.062 |

FQ has the most symmetric transitions; FL/CC/AX are most asymmetric.

### Per-Section Asymmetry

| Section | JSD |
|---------|-----|
| BIO | 0.086 |
| STARS_RECIPE | 0.086 |
| HERBAL | 0.168 |
| COSMO | 0.245 |

Asymmetry varies 2.8x across sections. Smaller sections (COSMO) show more asymmetry, possibly a sample size effect.

### Diagnosis

M2 generates from a single directional Markov chain, producing more asymmetry than the real text's bidirectional constraint structure. The real text's symmetry likely comes from PREFIX's symmetric routing (C1024: MI asymmetry 0.018 bits for PREFIX vs 0.070 for MIDDLE, 4x ratio). A model incorporating PREFIX routing would reduce generated asymmetry.

## C2 Analysis

| Role | Suffix-Free Rate | Total Tokens |
|------|-----------------|-------------|
| CC (CORE_CONTROL) | **1.000** | 735 |
| FQ (FREQUENT) | 0.934 | 2890 |
| FL (FLOW) | 0.938 | 1078 |
| AX (AUXILIARY) | 0.693 | 4140 |
| EN (ENERGY) | 0.390 | 7211 |

Suffix attachment is strongly role-dependent. CC tokens are FULLY suffix-free (100%). EN tokens are the most suffix-bearing (61%). This is a morphological constraint that M2 cannot enforce because it generates class-level sequences without role-specific token selection rules.

### Independence Verification

C2 (CC suffix-free) = 1.0 in ALL sections (BIO, HERBAL, COSMO, STARS_RECIPE). Zero variance across sections. C2 is a universal morphological constraint, not section-parameterized.

## Provenance

C1024, C1025, C1029

**Script:** `phases/SECTION_GRAMMAR_VARIATION/scripts/section_grammar_variation.py`
**Results:** `phases/SECTION_GRAMMAR_VARIATION/results/section_grammar_variation.json`
