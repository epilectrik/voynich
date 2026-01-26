# ACTION_SEQUENCE_TEST Results

**Phase:** ACTION_SEQUENCE_TEST
**Date:** 2026-01-25
**Status:** CLOSED

---

## Hypothesis

Brunschwig's procedural action sequence (GATHER → CHOP → DISTILL) maps to B grammar class transition patterns.

---

## Findings

### Primary Result: WEAK SUPPORT

B grammar shows **phase structure** but **not linear procedural flow**.

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Forward/Backward ratio | 1.42x | Too weak for strict sequencing (need >2x) |
| M→M transitions | 72.5% | System stays in working phase |
| EARLY ENERGY_OPERATOR | 79.4% | Line-start dominated by energy setup |
| LATE "OTHER" | 100% | Line-end has distinct morphology |

**Conclusion:** B encodes **iterative control loops**, not linear recipes.

---

### Secondary Result: LATE Prefix Class (C539)

Discovered a distinct morphological class at line-end positions:

| Prefix | Position | Suffix-Less | Pattern |
|--------|----------|-------------|---------|
| al | 0.692 | 43.9% | V+L |
| ar | 0.744 | 68.4% | V+L |
| or | 0.664 | 70.5% | V+L |

**Key properties:**
- 3.78x enrichment at absolute line end
- V+L morphology (vowel + liquid) distinct from consonantal ENERGY prefixes
- 85.4% B-exclusive tokens, but 76.2% PP MIDDLEs
- B-internal grammatical operation applied to pipeline vocabulary

**Documented as:** C539 (Tier 2)

---

### Tertiary Result: REGIME Operational Intensity

| REGIME | ENERGY_OPERATOR % |
|--------|-------------------|
| REGIME_3 | 55.2% |
| REGIME_1 | 50.3% |
| REGIME_4 | 39.5% |
| REGIME_2 | 37.7% |

Different REGIMEs have different operational intensity profiles.

---

## Interpretation

The line-level structure supports **control-loop semantics**:

```
LINE = CONTROL CYCLE:
  [EARLY]  Initialize energy state (ENERGY prefixes)
  [MIDDLE] Monitor → Intervene → Monitor... (all roles, high M→M)
  [LATE]   Record output (V+L prefixes)
  [RESET]  New cycle or line termination
```

This is consistent with the Tier 0 frozen conclusion: B encodes closed-loop control programs.

---

## Constraints Produced

| Constraint | Tier | Description |
|------------|------|-------------|
| C539 | 2 | LATE Prefix Morphological Class |

---

## Scripts

- `action_sequence_mapping.py` - Phase transition analysis
- `prefix_semantic_analysis.py` - CCM role mapping by position
- `late_prefix_analysis.py` - LATE prefix deep dive
- `late_provenance_check.py` - B-exclusive vs PP provenance

---

## Next Steps

Recommended follow-up: **LINE_BOUNDARY_OPERATORS** phase
- Test if L-compounds (line-initial) and LATE prefixes (line-final) form symmetric brackets
- Characterize the full line-level control cycle structure
