# C1241 - Header-Body Length Independence

**Tier:** 2 | **Scope:** B | **Phase:** PARAGRAPH_TERMINATION_MECHANICS (Phase 442)

## Statement

Header complexity does not predict body length (r=-0.039 for token count, -0.072 for unique MIDDLEs). Paragraph length is externally determined, not programmed by header specification. Short and long paragraphs are structurally identical (same kernel balance, mode ratio, interleave rate).

## Evidence

### Header-body correlations (n=75 paragraph pairs)

| Header metric | Correlation with body length |
|---------------|------------------------------|
| Token count | -0.039 |
| Unique MIDDLEs | -0.072 |
| HT token count | -0.009 |
| Kernel diversity | 0.213 |

All correlations near zero. The weak positive for kernel diversity (0.213) does not survive multiple comparison correction.

### Short vs long paragraph structure

| Length class | Count | % of total |
|-------------|-------|------------|
| Short (2-4 body lines) | 331 | 56.7% |
| Medium (5-7 body lines) | 102 | 17.5% |
| Long (8+ body lines) | 58 | 9.9% |

Structural comparison across length classes: kernel balance, suffix mode ratio, and interleave rate are all similar. The difference between short and long paragraphs is a section composition effect (SHORT=60% Stars, LONG=60% BIO), not an internal structural difference.

### Key finding

If headers "programmed" body length (as a specification-execution model might predict), we would expect complex headers to predict long bodies. They do not. Body length is determined by external factors (section, REGIME, folio-specific material being processed), not by the header's internal complexity.

## Interpretation

The header specifies WHAT is processed (compound MIDDLEs identifying the material), while body length reflects HOW LONG the process runs. These are independent. A complex specification (many unique MIDDLEs) does not require more execution lines. Length is parameterized by the type of process (section) and the operational context (REGIME), confirming C1239.

## Related constraints

- C1239: Paragraph body length parameterization (section and REGIME effects)
- C932: Spec -> exec gradient (header specification, body execution)
- C935: 71.6% header MIDDLE hit rate in body (vocabulary overlap)
- C963: Body homogeneous after length control
- C858: Paragraph count ~ complexity (rho=0.836) — this is count per FOLIO, not body length per paragraph

## Provenance

- `phases/PARAGRAPH_TERMINATION_MECHANICS/scripts/termination_analysis.py`
- `phases/PARAGRAPH_TERMINATION_MECHANICS/results/termination_analysis.json`
