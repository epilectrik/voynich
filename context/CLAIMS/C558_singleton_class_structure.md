# C558: Singleton Class Structure

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Only 3 instruction classes are singletons (single-token membership): Class 10 (daiin), Class 11 (ol), Class 12 (k). Two of three CORE_CONTROL classes (67%) are singletons with complementary positional biases: daiin is initial-biased (27.7% vs 7.6%), ol is final-biased (9.5% vs 5.2%). Singleton structure indicates these tokens are irreducible control primitives.

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/singleton_class_analysis.py`

### Singleton Classes

| Class | Token | Role | Occurrences | Initial% | Final% |
|-------|-------|------|-------------|----------|--------|
| 10 | daiin | CC | 314 | 27.7% | 7.6% |
| 11 | ol | CC | 421 | 5.2% | 9.5% |
| 12 | k | AX | 0 | N/A | N/A |

### Class Size Distribution

| Size | Count | Example Classes |
|------|-------|-----------------|
| 1 | 3 | 10, 11, 12 |
| 2 | 1 | 7 (al, ar) |
| 3 | 2 | 8 (chedy, chol, shedy), 9 (aiin, o, or) |
| 5+ | 43 | All other classes |

### CORE_CONTROL Composition

| Class | Tokens | Singleton |
|-------|--------|-----------|
| 10 | daiin | YES |
| 11 | ol | YES |
| 17 | 9 tokens | NO |

2/3 CORE_CONTROL classes = singletons (67%)

### Singleton Role Distribution

| Role | Singleton Classes | % of All Singletons |
|------|-------------------|---------------------|
| CC | 2 (Class 10, 11) | 67% |
| AX | 1 (Class 12) | 33% |
| EN, FL, FQ | 0 | 0% |

---

## Interpretation

### Complementary Control Operators

daiin and ol form a positional control pair:

| Operator | Bias | Function |
|----------|------|----------|
| daiin | Initial (27.7%) | Line-opening control signal |
| ol | Final (9.5%) | Line-closing control signal |

Neither is exclusive to its position, but each shows statistically significant preference opposite the other.

### k (Class 12) Absence

Class 12 (k) has zero occurrences in Currier B despite being classified. Possible explanations:
1. Latent operator not used in extant manuscript
2. Classification artifact from co-survival analysis
3. Reserved but unused control symbol

### Singleton as Primitive

Singleton status indicates irreducibility:
- daiin, ol, k cannot be decomposed into other class members
- They are the atomic units of their respective instruction classes
- Multi-token classes (like Class 17) contain variant forms

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C085 | Consistent - ol contains 'o','l' primitives; k is primitive |
| C089 | Aligned - k in core-within-core (k, h, e); Class 12 singleton |
| C407 | Consistent - daiin DA-family infrastructural function |
| C557 | Extended - daiin singleton has ENERGY-triggering function |
| C550 | Contextualized - CC role transitions involve singleton operators |
| C540 | Related - k is bound morpheme, never standalone |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** singleton_class_analysis.py

---

## Navigation

<- [C557_daiin_line_opener.md](C557_daiin_line_opener.md) | [INDEX.md](INDEX.md) ->
