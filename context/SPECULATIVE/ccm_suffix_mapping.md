# Component-to-Class Mapping: Suffix Analysis (CCM-2)

**Tier:** 3 | **Status:** IN PROGRESS | **Date:** 2026-01-10

> **Goal:** Map the 7 universal suffixes to decision archetype clusters using A/B enrichment patterns.

---

## Data Sources

| Source | What It Provides |
|--------|------------------|
| C277 | Suffixes are UNIVERSAL (appear across all prefixes) |
| C283 | Suffix enrichment ratios (A vs B) |
| ECR-3 | 12 decision archetypes by layer |
| canonical_grammar.json | Token → role with suffix patterns |

---

## Step 1: Suffix Enrichment Patterns

From C283:

| Suffix | Enrichment | Interpretation |
|--------|------------|----------------|
| **-edy** | 191x B-enriched | Extreme B specialization |
| **-dy** | 4.6x B-enriched | Strong B preference |
| **-ar** | 3.2x B-enriched | Moderate B preference |
| **-ol** | ~1x balanced | Cross-system |
| **-aiin** | ~1x balanced | Cross-system |
| **-or** | 0.67x A-enriched | Moderate A preference |
| **-chy** | 0.61x A-enriched | Moderate A preference |
| **-chor** | 0.18x A-enriched | Strong A preference |

---

## Step 2: Layer → Decision Archetype Recap

From ECR-3:

| Layer | Archetypes | Function |
|-------|------------|----------|
| **B** | D1, D3-D8, D12 | Execution decisions |
| **A** | D2, D9 | Discrimination decisions |
| **HT** | D10 | Attention decisions |
| **AZC** | D11 | Orientation decisions |

---

## Step 3: Suffix → Decision Archetype Mapping

### B-Enriched Suffixes: Execution Archetypes

| Suffix | B-Enrichment | Tokens (from grammar) | Role | Archetype Mapping |
|--------|--------------|----------------------|------|-------------------|
| **-edy** | 191x | chedy, tedy | ENERGY_OPERATOR, AUXILIARY | D5 (Energy Level) |
| **-dy** | 4.6x | dy | FREQUENT_OPERATOR | D6 (Wait vs Act) |
| **-ar** | 3.2x | dar | AUXILIARY | D7 (Recovery Path) |

**Interpretation:**
- -edy marks energy-related execution decisions (extreme B-specialization)
- -dy marks frequent/routine execution decisions
- -ar marks recovery/support decisions

### A-Enriched Suffixes: Discrimination Archetypes

| Suffix | A-Enrichment | Interpretation | Archetype Mapping |
|--------|--------------|----------------|-------------------|
| **-chor** | 5.6x (= 0.18x B) | Strong registry specialization | D9 (Case Comparison) |
| **-chy** | 1.6x (= 0.61x B) | Moderate registry preference | D2 (Fraction Identity) |
| **-or** | 1.5x (= 0.67x B) | Moderate registry preference | D2 (Fraction Identity) |

**Interpretation:**
- -chor marks case-comparison decisions (registry lookup)
- -chy, -or mark fraction/identity discrimination decisions

### Balanced Suffixes: Cross-Archetype

| Suffix | Balance | Interpretation | Archetype Mapping |
|--------|---------|----------------|-------------------|
| **-ol** | ~1x | Cross-system utility | D6 (Wait vs Act) OR D8 (Restart Viability) |
| **-aiin** | ~1x | Cross-system utility | D1 (Phase Position) OR D4 (Flow Balance) |

**Interpretation:**
- -ol and -aiin appear in both execution and discrimination contexts
- They encode decisions that apply across layers

---

## CCM-2 Synthesis: Suffix → Archetype Mapping

| Suffix | Primary Layer | Primary Archetype | Confidence |
|--------|---------------|-------------------|------------|
| **-edy** | B (execution) | D5 (Energy Level) | HIGH |
| **-dy** | B (execution) | D6 (Wait vs Act) | MEDIUM |
| **-ar** | B (execution) | D7 (Recovery Path) | MEDIUM |
| **-ol** | Cross-layer | D6/D8 (Wait/Restart) | LOW |
| **-aiin** | Cross-layer | D1/D4 (Phase/Flow) | LOW |
| **-or** | A (discrimination) | D2 (Fraction Identity) | MEDIUM |
| **-chy** | A (discrimination) | D2 (Fraction Identity) | MEDIUM |
| **-chor** | A (discrimination) | D9 (Case Comparison) | HIGH |

---

## Hazard Alignment Check

Cross-reference with hazard classes:

| Archetype | Hazard Class | Suffix Pattern |
|-----------|--------------|----------------|
| D1 (Phase Position) | PHASE_ORDERING (41%) | -aiin (balanced) |
| D2 (Fraction Identity) | COMPOSITION_JUMP (24%) | -or, -chy (A-enriched) |
| D5 (Energy Level) | ENERGY_OVERSHOOT (6%) | -edy (191x B!) |

**Key finding:** The extreme -edy B-enrichment matches the apparatus-focused hazards (29%) that require immediate response (no LINK nearby). Energy decisions are the most time-critical, hence most B-specialized.

---

## The Suffix Function

Suffixes are **universal** across prefixes (C277) — they cross all material class boundaries.

This means:
- **Suffixes encode decision TYPE, not material identity**
- The same decision archetype can apply to any material class
- Suffix choice is orthogonal to prefix choice

### Compositional Meaning

```
TOKEN = PREFIX (material-class operation) + MIDDLE (variant) + SUFFIX (decision type)
```

Example interpretation:
- **ch-edy** = Energy operation (ch-) + [variant] + energy-level decision (-edy)
- **ch-or** = Energy operation (ch-) + [variant] + fraction-identity decision (-or)
- **ct-or** = Registry reference (ct-) + [variant] + fraction-identity decision (-or)

The suffix tells you **what kind of decision** is being marked, regardless of what material class the prefix operates on.

---

## Constraints Satisfied

| Constraint | How Satisfied |
|------------|---------------|
| C277 | Universal suffixes → universal decision types |
| C283 | Enrichment patterns map to layer-specific archetypes |
| C284 | CT in B uses -edy, -dy → registry items can enter execution context |

---

## Remaining Uncertainty

| Question | Status |
|----------|--------|
| Exact -ol archetype mapping | LOW confidence |
| Exact -aiin archetype mapping | LOW confidence |
| Whether suffixes encode single or multiple archetypes | Unclear |

---

## Next Steps

- CCM-3: Test sister-pair choice (ch vs sh, ok vs ot)
- CCM-4: Classify MIDDLEs by prefix/suffix class

---

## Navigation

← [ccm_prefix_mapping.md](ccm_prefix_mapping.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
