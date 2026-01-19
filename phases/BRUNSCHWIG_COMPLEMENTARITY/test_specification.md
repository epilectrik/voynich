# Brunschwig Complementarity Test Specification

## Status: PROPOSED

---

## Question

> Do Brunschwig recipes show complementary handling-role composition at rates that match Voynich jar triplet enrichment?

---

## What This Tests

**Structural parallel:** Does period-authentic distillation practice organize materials by complementary operational roles, matching the Voynich jar pattern?

**Not tested:**
- Material identity
- Jar-to-product mapping
- PREFIX-to-material correlation

---

## Voynich Baseline (Already Established)

From JAR_WORKING_SET_INTERFACE phase:

| Metric | Value |
|--------|-------|
| Triplet enrichment (M-A + M-B + M-D) | 1.77x vs random |
| p-value | 0.022 |
| Cross-class pair enrichment | 1.59x - 1.84x |
| Homogeneity | 0.73x (LESS than random) |

**Pattern:** Jars deliberately combine different handling classes. Homogeneous groupings are underrepresented.

---

## Brunschwig Test Design

### Step 1: Recipe Extraction

Source: Brunschwig's "Liber de arte distillandi" (Book of the Art of Distillation)

Extract recipes that list multiple ingredients for a single preparation.

**Data needed per recipe:**
- Recipe ID
- Number of ingredients
- Processing instructions per ingredient (from Brunschwig's text)

### Step 2: Handling Role Coding (Content-Free)

Code each ingredient by Brunschwig's PROCESSING DESCRIPTION, not by material name.

**Coding scheme (derived from Brunschwig's own terminology):**

| Role | Brunschwig Indicators | Parallel |
|------|----------------------|----------|
| H-SENSITIVE | "gentle heat", "careful fire", "watch closely", "may spoil", "volatile" | M-A |
| H-ROUTINE | "standard fire", "common method", "usual time", "no special care" | M-B |
| H-STABLE | "strong heat", "long extraction", "robust", "will not spoil" | M-D |

**Key constraint:** Code by what Brunschwig says about PROCESS, not by what the ingredient IS.

### Step 3: Composition Analysis

For each recipe with 3+ ingredients:
- Count role distribution (H-SENSITIVE, H-ROUTINE, H-STABLE)
- Mark as TRIPLET if all three roles present
- Mark as HOMOGENEOUS if single role dominates (>80%)

### Step 4: Enrichment Calculation

Compare to random baseline:
- Shuffle role assignments across all ingredients
- Recalculate triplet frequency
- Compute enrichment ratio and p-value

---

## Predictions

**If Voynich pattern is period-authentic:**
- Brunschwig triplet enrichment > 1.0
- Brunschwig homogeneity < 1.0
- Ratios should be in similar range to Voynich (1.5x - 2.0x)

**If Voynich pattern is novel/anomalous:**
- Brunschwig shows no enrichment OR opposite pattern
- Would suggest Voynich is doing something different from standard practice

**If Brunschwig is uncategorizable:**
- His text doesn't provide enough processing-role information
- Test inconclusive (not falsification, just insufficient data)

---

## Constraints Respected

| Constraint | How Respected |
|------------|---------------|
| C171 (no material encoding) | Code by process, not identity |
| C138 (illustrations don't constrain) | No visual data used |
| C383 (global type system) | Role categories are structural |
| C493/C494 (Brunschwig embedding) | Tests composition, not mapping |
| X.19 (jars are interface-layer) | Compares patterns, not jar semantics |

---

## Data Requirements

1. **Brunschwig text access** - Need digital/searchable version of recipes
2. **Recipe count** - Minimum ~20-30 multi-ingredient recipes for statistical power
3. **Processing terminology list** - Brunschwig's vocabulary for handling instructions

---

## Validation Criteria

**Test PASSES if:**
- Brunschwig triplet enrichment ratio > 1.3 (above noise)
- Direction matches Voynich (complementary > homogeneous)
- p-value < 0.1 for enrichment

**Test FAILS if:**
- Brunschwig shows homogeneous preference
- OR no detectable pattern (random)
- Would NOT falsify Voynich model, just show non-parallel

**Test INCONCLUSIVE if:**
- Insufficient recipe data
- Processing descriptions too ambiguous to code

---

## Output

```
results/brunschwig_complementarity.json
```

Should contain:
- Recipe count analyzed
- Role distribution totals
- Triplet count (observed vs expected)
- Enrichment ratio
- p-value
- Comparison to Voynich baseline

---

## Next Steps

1. Obtain searchable Brunschwig text
2. Extract multi-ingredient recipes
3. Code handling roles from processing descriptions
4. Run enrichment analysis
5. Compare to Voynich jar baseline
