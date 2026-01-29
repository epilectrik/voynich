# C611: UN Role Prediction

**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** CLOSED
**Source:** Phase UN_COMPOSITIONAL_MECHANICS
**Scope:** B_INTERNAL | UN | ICC

## Statement

PREFIX-based prediction assigns 99.2% of UN tokens to ICC roles with mean confidence 0.863. The predicted distribution is EN 37.1%, AX 34.6%, FQ 22.4%, FL 5.9%, CC 0.0%. Zero UN tokens predict to CC — the CORE_CONTROL role is fully resolved with no unclassified variants. Consensus prediction (PREFIX + MIDDLE + SUFFIX) assigns 99.9% (5/7,042 unresolvable). UN is the morphologically extended tail of EN, AX, and FQ.

## Evidence

### Prediction Methods

| Method | Coverage | Mean Confidence |
|--------|----------|-----------------|
| PREFIX only | 99.2% | 0.863 |
| PREFIX+SUFFIX joint | 67.6% | 0.978 |
| MIDDLE only | 54.3% | 0.749 |
| **Consensus** | **99.9%** | -- |

### Consensus Role Distribution

| Role | Predicted UN | % of UN | High-conf |
|------|-------------|---------|-----------|
| EN | 2,612 | 37.1% | 2,145 |
| AX | 2,439 | 34.6% | 687 |
| FQ | 1,574 | 22.4% | 190 |
| FL | 412 | 5.9% | 36 |
| CC | 0 | 0.0% | 0 |
| Unresolved | 5 | 0.1% | -- |

High-confidence (all 3 methods agree): 3,058 tokens (43.4%).

### Combined B Distribution (Classified + Predicted UN)

| Role | Classified | + Predicted UN | Combined % of B |
|------|-----------|----------------|-----------------|
| EN | 7,211 | +2,612 | 42.5% |
| AX | 4,140 | +2,439 | 28.5% |
| FQ | 2,890 | +1,574 | 19.3% |
| FL | 1,078 | +412 | 6.5% |
| CC | 735 | +0 | 3.2% |

### CC Full Resolution

CC consists of 3 ICC classes (10, 11, 12) with highly specific tokens (standalone `ol`, `daiin`, `chol`-variants). Every CC-type token is already classified. No morphological variants exist below the cosurvival threshold.

### Why PREFIX Works

PREFIX->role mapping in classified tokens is near-deterministic:
- qo → 100% EN
- ch → 97.5% EN
- sh → 96.3% EN
- ol → 100% AX
- ot → 82.6% FQ
- ok → 80.9% FQ
- da → 62.8% FL
- Extended prefixes → 100% AX (pch, yk, lk, lch, te, etc.)

## Related

- C121 (49 instruction classes)
- C566 (UN morphologically normal)
- C610 (UN morphological profile)
- C570 (AX prefix patterns)
- C588 (suffix role selectivity)
