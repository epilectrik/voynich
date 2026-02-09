# QO_CHSH_DIFFERENTIATION Phase Summary

**Status:** COMPLETED
**Date:** 2026-02-05
**Verdict:** STRONG DIFFERENTIATION FOUND

## Research Question

What do the QO-family (qo, ok, ot, o-prefixed) and CHSH-family (ch, sh-prefixed) EN tokens specifically monitor or operate on?

## Key Findings

### Test 1: Kernel Profile (NEW)

| Family | k (energy) | h (hazard) | e (escape) |
|--------|------------|------------|------------|
| QO     | **43.5%**  | 13.5%      | 43.0%      |
| CHSH   | 17.4%      | 6.4%       | **76.2%**  |

**Chi-square: 1373.07, p < 10^-298** (HIGHLY SIGNIFICANT)

- QO is k/e balanced (energy + settling)
- CHSH is e-dominant (settling/escape operations)

### Test 2: Brunschwig Tier Mapping (NEW)

| Family | PREP | THERMO | EXTENDED |
|--------|------|--------|----------|
| QO-exclusive MIDDLEs | 4 | 0 | **9** |
| CHSH-exclusive MIDDLEs | 0 | **5** | 4 |

- QO MIDDLEs concentrate in **EXTENDED tier** (equilibration cycles)
- CHSH MIDDLEs concentrate in **THERMO tier** (monitoring)

### Test 3: Section Ratio (NEW)

| Section | QO% | CHSH% | Dominant |
|---------|-----|-------|----------|
| B (Bio) | **56.9%** | 43.1% | QO |
| H (Herbal) | 47.0% | **53.0%** | CHSH |
| S (Stars) | **55.3%** | 44.7% | QO |
| T (Misc) | 47.6% | **52.4%** | CHSH |
| C (Zodiac) | **56.4%** | 43.6% | QO |

**Chi-square: 57.92, p < 10^-11** (SIGNIFICANT)

- Herbal: CHSH-dominant (needs more monitoring?)
- Bio/Stars: QO-dominant (more energy application?)

### Prior Constraints (Confirmed)

- **C601**: QO = 0/19 hazard participation; CHSH = 58% of hazard targets
- **C644**: QO in stable contexts (stability=0.318 vs 0.278)
- **C645**: CHSH dominates post-hazard (75.2%)
- **C649**: k/t/p-initial MIDDLEs → QO; e/o-initial → CHSH (deterministic)

## Semantic Differentiation

Based on all evidence:

### QO-family: "Active Energy Application"
- **Kernel profile**: Balanced k (43%) + e (43%) = apply heat, let settle
- **Brunschwig tier**: EXTENDED (equilibration cycles) + PREP (preparation)
- **Operational mode**: Routine, predictable, hazard-avoidant
- **Gloss**: "heat/equilibrate" or "energy cycle"

### CHSH-family: "Passive Monitoring & Recovery"
- **Kernel profile**: Heavy e (76%) = waiting, settling, observing
- **Brunschwig tier**: THERMO (monitoring process state)
- **Operational mode**: Responsive, post-hazard recovery, variable conditions
- **Gloss**: "monitor/stabilize" or "watch process"

## Proposed Decoder Glosses

```python
# QO-family prefixes
'qo': 'heat-cycle',      # Active energy application
'ok': 'energy-check',    # Energy with kernel monitoring
'ot': 'energy-transfer', # Energy transfer operation
'o': 'output-check',     # Output monitoring

# CHSH-family prefixes
'ch': 'watch-process',   # Process state monitoring
'sh': 'check-stability', # Stability verification
```

## Constraints Extended

This phase extends:
- **C576**: MIDDLE bifurcation now explained by kernel content
- **C577**: Section interleaving now explained by QO:CHSH ratio differences
- **C644/C645**: Functional split now has semantic grounding

## Files

- `scripts/01_kernel_profile.py` - Kernel k/h/e distribution by family
- `scripts/02_brunschwig_tier_mapping.py` - F-BRU-011 tier mapping
- `scripts/03_section_ratio.py` - Section QO:CHSH ratios
- `results/` - JSON output files
