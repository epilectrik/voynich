# SENSORY_LOAD_ENCODING Phase Report

## Executive Summary

**Primary Finding:** Sensory requirements are NOT encoded as tokens but ARE encoded as constraint pressure - and the relationship with HT density is **INVERSE** to the initial hypothesis.

| Test | Result | Significance |
|------|--------|--------------|
| Negative Anchor | PASSED | 0.01% overlap, no direct encoding |
| SLI vs HT | **r = -0.453** | p < 0.0001 (highly significant) |
| SLI by REGIME | F = 38.54 | p < 0.0001 (significant differentiation) |

---

## Key Finding: Constraint Pressure SUBSTITUTES for Vigilance

The external expert hypothesized:
> "High sensory demand → higher HT (vigilance signal)"

We found the **OPPOSITE**:
> "High constraint pressure (SLI) → LOWER HT density"

### Interpretation

This makes sense under a different model:

| Scenario | SLI | HT | Explanation |
|----------|-----|-----|-------------|
| Sensory-critical, constrained | HIGH | LOW | Grammar enforces safety; vigilance built into structure |
| Forgiving, many options | LOW | HIGH | More decision complexity; needs engagement signal |

The Voynich system appears to encode sensory requirements by **tightening constraints** rather than by signaling vigilance. When operations are dangerous, the grammar restricts options - the operator doesn't need a warning because they literally cannot make the wrong choice.

---

## Phase 1: Negative Anchor Test

**Goal:** Confirm no direct sensory token encoding

**Results:**
- Voynich tokens (EVA): 8,106 unique
- Brunschwig sensory vocabulary: 63 terms
- **Direct overlap: 1 term ("arom")** - likely coincidental EVA sequence
- **Jaccard similarity: 0.0001** (0.01%)

**Conclusion:** Sensory information is NOT encoded at the token level. This confirms C171 (zero material/sensory encoding) and supports indirect encoding via constraint pressure.

---

## Phase 2: Sensory Load Index (SLI)

**Formula:**
```
SLI = hazard_density / (escape_density + link_density)
```

**Results (83 B folios):**

| Metric | Value |
|--------|-------|
| SLI Mean | 1.107 |
| SLI Std | 0.225 |
| SLI Range | 0.609 - 1.804 |

### SLI vs HT Correlation

| Correlation | P-value | Interpretation |
|-------------|---------|----------------|
| r = **-0.453** | p = 0.000017 | Highly significant, **NEGATIVE** |

**Comparison to C477 (tail_pressure):**
- C477: r = 0.504, p = 0.0045 (positive)
- SLI: r = -0.453, p = 0.00002 (negative, comparable magnitude)

### SLI by REGIME

| REGIME | Mean SLI | n |
|--------|----------|---|
| REGIME_1 | 1.098 | 31 |
| REGIME_2 | **0.786** | 11 |
| REGIME_3 | **1.395** | 16 |
| REGIME_4 | 1.074 | 25 |

**ANOVA:** F = 38.54, p < 0.0001

Key pattern:
- **REGIME_2** (gentle, forgiving): LOWEST SLI, HIGHEST HT
- **REGIME_3** (intense, oil/resin): HIGHEST SLI, LOWEST HT

### Extreme Folios

**Highest SLI (most constrained):**
- f33v: SLI=1.804, HT=0.158 (REGIME_3)
- f46r: SLI=1.638, HT=0.139 (REGIME_3)
- All top-5 are REGIME_3

**Lowest SLI (most forgiving):**
- f48r: SLI=0.609, HT=0.233 (REGIME_2)
- f105v: SLI=0.686, HT=0.218 (REGIME_2)
- All top-5 are REGIME_2

---

## Theoretical Implications

### Original External Expert Model
> "Sensory requirements → constraint tightening → higher vigilance (HT)"

### Revised Model (Based on Results)
> "Sensory requirements → constraint tightening → LOWER vigilance needed (because constraints enforce safety)"

The system works by **structural substitution**:
- When sensory judgment is critical, the grammar restricts options
- The operator doesn't need a vigilance signal - they can't make the wrong choice
- HT tracks **decision complexity** (how many valid options), not sensory criticality

### Architectural Insight

```
High Sensory Demand → Tight Grammar → Few Options → Low HT
Low Sensory Demand  → Loose Grammar → Many Options → High HT
```

HT appears to encode "cognitive load for choice" rather than "vigilance for sensing."

---

## Phases Deferred

### Phase 3: Brittleness Gradient
- Requires per-folio P-zone length computation from token sequences
- Global data confirms gradient exists (P=15.87% > R=9.23% > S=4.36%)
- Would need additional development to test per-folio

### Phase 4: Modality Signatures
- Only 7% of Brunschwig procedures have real sensory content
- Insufficient sample to test modality-specific signatures
- Would require different external source with richer sensory annotation

---

## Conclusions

### What We Found

1. **NO direct sensory encoding** - Confirmed by negative anchor test (0.01% overlap)

2. **SLI predicts HT density** - Strong correlation (r=-0.453, p<0.0001)

3. **INVERSE relationship** - Higher constraint pressure = LOWER HT, not higher

4. **REGIMEs differentiate on SLI** - REGIME_2 (forgiving) vs REGIME_3 (constrained)

### What This Means

The external expert's insight was correct that sensory requirements are encoded as constraint pressure. But the mechanism is **substitution**, not **amplification**:

> "The Voynich Manuscript does not encode sensory cues - it encodes constraints that make misjudging impossible."

This is a more sophisticated system than "signal when danger exists." Instead, it's "remove the dangerous options so signaling is unnecessary."

### Fit Recommendation

**F-SLI-001: Constraint-Vigilance Inverse Relationship**
- SLI (hazard/recovery ratio) negatively correlates with HT density
- High constraint pressure substitutes for vigilance signaling
- REGIMEs differentiate on constraint geometry
- Tier: 3 (structural characterization)

---

## Files Created

| File | Purpose |
|------|---------|
| `phases/SENSORY_LOAD_ENCODING/README.md` | Phase documentation |
| `phases/SENSORY_LOAD_ENCODING/negative_anchor_test.py` | Confirm no direct encoding |
| `phases/SENSORY_LOAD_ENCODING/sensory_load_index.py` | SLI computation and analysis |
| `results/negative_anchor_test.json` | Phase 1 results |
| `results/sensory_load_index.json` | Phase 2 results |

---

*Phase completed: 2026-01-19*
*Key finding: Constraint pressure SUBSTITUTES for vigilance signaling*
*Status: HYPOTHESIS REFINED - inverse relationship discovered*
