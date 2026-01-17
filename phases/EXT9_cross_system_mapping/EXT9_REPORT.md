# EXT-9: Cross-System Mapping

**Phase ID:** EXT-9
**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** COMPLETE
**Date:** 2026-01-06
**Updated:** 2026-01-16 (H-only transcriber filter applied)

---

## MIDDLE Count Correction (2026-01-16)

> **The "~725 Middles (8 A-exclusive)" claim in this report is INVALIDATED.**
>
> Re-analysis (phase MIDDLE-AB) with consistent parsing reveals:
> - **Global MIDDLE universe (A ∪ B): 1,186**
> - **Currier A unique MIDDLEs: 617** (not 725)
> - **Currier B unique MIDDLEs: 837**
> - **Shared (A ∩ B): 268**
> - **A-exclusive: 349** (not 8-9)
> - **B-exclusive: 569**
> - **Jaccard similarity: 0.226**
>
> The original 725 figure was a parsing artifact. References to "only 9 A-exclusive" are incorrect.
> See `phases/MIDDLE_AB/MIDDLE_AB_REPORT.md` for full analysis.

---

## Executive Summary

> **Currier A and B use SHARED COMPONENTS with CONTEXT-DEPENDENT MODE PREFERENCES. The relationship is CO-DESIGNED, COMPLEMENTARY, OVERLAPPING, and MODE-PREFERRING — not mode-exclusive. Suffixes like -or/-chy favor registry (A) while -dy/-edy favor operations (B), with CT being a special "catalog-only" category that rarely appears in procedures.**

---

## Test Results

### Test 1: -or/-dy Modal Split

| Metric | Value |
|--------|-------|
| Bases with -or form | 375 |
| Bases with -dy form | 997 |
| Bases with BOTH | 177 (14.8% overlap) |
| Modal split rate | **57.9%** (11/19 testable) |

**Result:** HYPOTHESIS SUPPORTED (stronger with clean data)

Examples of modal split bases:
- `ch-`: chor (A=182, B=32) vs chdy (A=9, B=132)
- `sh-`: shor (A=69, B=26) vs shdy (A=2, B=42)
- `cth-`: cthor (A=42, B=3) — rarely has -dy form

**Interpretation:** About half of bases with both forms show the expected A-or/B-dy pattern. The relationship is real but not universal.

---

### Test 2: CT's Rare B Appearances

| Metric | Value |
|--------|-------|
| CT in A | 449 |
| CT in B | 59 (0.13x ratio) |
| B folios with CT | 39 |
| Top folio | f113v (4 CT tokens) |

**CT token distribution in B:**

| Token | In B | In A | Ratio |
|-------|------|------|-------|
| cthedy | 9 | 1 | 9.0x (exceptional!) |
| cthey | 9 | 38 | 0.24x |
| cthdy | 8 | 0 | B-only |
| cthy | 6 | 101 | 0.06x |
| cthor | 3 | 42 | 0.07x |

**Key finding:** When CT appears in B, it often uses B-enriched suffixes (-edy, -dy) that it rarely uses in A. This suggests CT references in procedures take "operational form" even though CT itself is primarily a registry category.

**Interpretation:** CT may represent:
1. Reference standards or control materials
2. Catalog-only materials rarely processed
3. Special materials used in specific procedures

---

### Test 3: Balanced Tokens

| Metric | Value |
|--------|-------|
| Balanced tokens (0.5x-2.0x, both >=10) | 66 |
| DA-family tokens in balanced set | Dominant |

**Top balanced tokens:**

| Token | In A | In B | Ratio |
|-------|------|------|-------|
| daiin | 511 | 315 | 0.62x |
| dar | 95 | 188 | 1.98x |
| dy | 124 | 110 | 0.89x |
| dal | 85 | 133 | 1.56x |
| dain | 93 | 114 | 1.23x |

**Interpretation:** Balanced tokens are dominated by:
1. Structural primitives (daiin)
2. DA-family tokens (dal, dain, dam, dair)
3. Simple suffix forms

These may serve as **cross-reference vocabulary** — the shared terminology used in both contexts.

---

### Test 4: Suffix Context Distribution

| Category | Count | Examples |
|----------|-------|----------|
| **A-ENRICHED** | 4 | -chor (0.21x), -chol (0.22x), -eor (0.64x), -chy (0.68x) |
| **B-ENRICHED** | 12 | -edy (175.39x!), -edaiin (103.0x), -kaiin (5.75x), -dy (4.46x), -eey (3.28x) |
| **BALANCED** | 11 | -or (0.75x), -odaiin (0.88x), -ol (0.88x), -ody (0.91x), -aiin (0.99x) |

**Extreme cases:**
- `-edy` is **175x more common in B** — almost exclusively operational
- `-chor` is **4.8x more common in A** — almost exclusively registry

**Interpretation:** Suffixes carry **context preference**, not exclusivity. The -edy suffix is the strongest operational marker; -chor/-chol are the strongest registry markers.

---

### Test 5: PREFIX × SUFFIX Modal Grid

```
Suffix       CH    QO    SH    DA    OK    OT    CT    OL
----------------------------------------------------------
-edy          B     B     B     B     B     B     B     B   (CONSISTENTLY B)
-dy           B     B     B     B     B     B     B     B   (CONSISTENTLY B)
-ar           B     B     B     B     B     B     A     B   (CT is exception)
-al           B     B     B     B     B     B     A     B   (CT is exception)
-ol           A     B     A     B     A     =     A     B   (VARIABLE)
-or           A     =     A     =     A     =     A     B   (A-LEANING)
-chy          A     A     =     =     =     A     A     B   (VARIABLE)
```

**Key finding:** CT behaves differently from other prefixes — many suffixes that are B-enriched for other prefixes are A-enriched for CT.

**Consistently B-enriched suffixes:** -edy, -ey, -ar, -eey, -al, -dy, -kaiin
**Variable suffixes:** -ol, -aiin, -hy, -or, -ky, -y, -eol, -chy

---

## Cross-System Model

### The Relationship

```
A and B share:
  - Same 8 prefixes
  - Same 27 suffixes
  - 268 shared MIDDLEs (349 A-exclusive, 569 B-exclusive)

A and B differ in:
  - Structural grammar (compositional vs sequential)
  - Physical location (0 shared folios)
  - Usage frequency of components
```

### Mode Preference Model

```
                     REGISTRY (A)          OPERATIONAL (B)
                     ────────────          ───────────────
Suffix preference:   -or, -chy, -chol      -edy, -dy, -ar, -al
Prefix behavior:     CT strongly A         OL strongly B
Balanced forms:      -ol, -aiin, -hy       (same as left)
```

### Architectural Summary

| Property | Status |
|----------|--------|
| CO-DESIGNED | Shared components confirm intentional design |
| COMPLEMENTARY | Different grammars for different purposes |
| OVERLAPPING | 66 balanced tokens, shared suffix inventory |
| MODE-PREFERRING | Consistent preferences but not exclusive |

---

## New Constraints

### Constraint 283: Suffix Context Preference
Suffixes show CONTEXT PREFERENCE, not exclusivity. A-enriched: -or (0.67x), -chy (0.61x), -chor (0.18x). B-enriched: -edy (191x), -dy (4.6x), -ar (3.2x). BALANCED: -ol (0.89x), -aiin (1.08x).

### Constraint 284: CT Folio Concentration
CT in B is CONCENTRATED in specific folios (48 folios, not uniform). When CT appears in B, it often uses B-enriched suffixes (-edy, -dy), suggesting operational reference form.

### Constraint 285: Balanced Vocabulary
66 tokens appear with BALANCED frequency (0.5x-2.0x) in both A and B. DA-family dominates. These serve as SHARED VOCABULARY between registry and operational contexts.

### Constraint 286: Prefix-Suffix Interaction
Modal preference is PREFIX × SUFFIX dependent. CT is consistently A-enriched across most suffixes. OL is consistently B-enriched. Other prefixes show variable patterns.

---

## The Complete Picture

```
VOYNICH MANUSCRIPT CROSS-SYSTEM ARCHITECTURE

┌─────────────────────────────────────────────────────────────────┐
│                    SHARED INFRASTRUCTURE                        │
│  ─────────────────────────────────────────────────────────────  │
│  8 Prefixes (ch, qo, sh, da, ok, ot, ct, ol)                   │
│  27 Suffixes (-ol, -or, -dy, -edy, -aiin, etc.)                │
│  1,186 MIDDLEs (617 A, 837 B, 268 shared)                      │
│  66 Balanced tokens (cross-reference vocabulary)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   CURRIER A (Registry)            CURRIER B (Operational)       │
│   ════════════════════            ═══════════════════════       │
│                                                                 │
│   MODE: Storage/Catalog           MODE: Active/Procedural       │
│   ─────────────────────           ─────────────────────         │
│   Suffix preference:              Suffix preference:            │
│   -or, -chy, -chor, -chol         -edy, -dy, -ar, -al           │
│                                                                 │
│   PREFIX affinity:                PREFIX affinity:              │
│   CT (7x enriched)                OL (5x enriched)              │
│                                   QO (4x enriched)              │
│                                                                 │
│   STRUCTURE:                      STRUCTURE:                    │
│   Compositional codes             Sequential grammar            │
│   897 identity combinations       49 instruction classes        │
│                                                                 │
│   FUNCTION:                       FUNCTION:                     │
│   Classify materials              Control operations            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    CROSS-REFERENCE POINTS                       │
│  ─────────────────────────────────────────────────────────────  │
│  daiin: boundary marker (A=1762, B=1140)                        │
│  DA-family: dal, dain, dam, dair                                │
│  Balanced suffixes: -ol, -aiin, -hy                             │
│                                                                 │
│  CT in B: rare (214), concentrated, uses -edy/-dy form          │
│  → Registry materials referenced in operational form            │
└─────────────────────────────────────────────────────────────────┘
```

---

## EXT-9B: Ratio Hypothesis — FALSIFIED

### Observations (Valid)

**Statistical patterns detected:**
- 27 compositions appear with variable repetition counts (2x, 3x, 4x)
- 3x dominance: 55% of repetitions
- 56.7% of folios have uniform repetition count
- H section: 25 folios uniformly 3x

**Repetition Distribution:**
| Count | Entries | % |
|-------|---------|---|
| 2x | 120 | 20% |
| 3x | 333 | 55% |
| 4x | 139 | 23% |
| 5x-6x | 9 | 2% |

### Interpretation (RETRACTED)

The initial interpretation that repetition encodes "ratios" or "proportions" was **structurally invalid**.

### Why Ratio Interpretation Fails

1. **Ratios are MORE demanding than counts** — require cross-entry comparison, reference frames, arithmetic semantics. None exist.

2. **No comparison mechanism** — "3x here" is NOT comparable to "3x there" because vocabularies are section-isolated. Ratios require comparability.

3. **3x dominance = human counting bias** — frequency distributions peak at small integers due to cognitive ergonomics, not proportional encoding.

4. **Folio uniformity = enumeration depth preference** — scribal convention, category density, registry norms. NOT "batch scale."

5. **Prior constraints violated** — Currier A has no abstract numerical system, no cross-record aggregation, no arithmetic. Ratio encoding would require all of these.

### Correct Interpretation

> **Repetition encodes LITERAL MULTIPLICITY of discrete identity instances, bounded for human usability, without abstraction, arithmetic, or proportional meaning.**

- Uniform folio = "this folio enumerates at fixed depth"
- Mixed folio = "this line has more instances than that line"
- Variable counts for same composition = "different instance counts, not different ratios"

### Verdict

**RATIO_HYPOTHESIS FALSIFIED**

The observations are real; the interpretation was semantic overreach. This strengthens the model by confirming:

> **Currier A intentionally refuses to encode quantity, even where humans expect it.**

### Constraints (287-290) — RETRACTED and REPLACED

| # | Constraint |
|---|------------|
| 287 | Repetition does NOT encode abstract quantity, proportion, or scale |
| 288 | 3x dominance reflects human counting bias, NOT proportional tiers |
| 289 | Folio uniformity = enumeration depth preference, NOT batch scale |
| 290 | Same composition with different counts = instance multiplicity, NOT magnitude |

---

## Files Generated

- `ext9_cross_system_analysis.py` — Cross-system mapping analysis
- `ext9_multiplicity_deeper.py` — Multiplicity deep dive
- `ext9_ratio_hypothesis.py` — Ratio hypothesis tests
- `ext9_folio_uniformity.py` — Folio-level pattern analysis
- `ext9_ratio_synthesis.md` — Ratio hypothesis synthesis
- `ext9_results.json` — Results data
- `EXT9_REPORT.md` — This report

---

## Phase Tag

```
Phase: EXT-9 + EXT-9B
Tier: 2 (STRUCTURAL INFERENCE) + Tier 1 (FALSIFICATION)
Subject: Cross-System Mapping + Ratio Hypothesis
Type: A-B relationship analysis + Semantic overreach correction
Status: COMPLETE
Verdict: CO-DESIGNED_COMPLEMENTARY_MODE-PREFERRING + RATIO_HYPOTHESIS_FALSIFIED
Constraints: 283-290 (287-290 are NEGATIVE constraints)
```
