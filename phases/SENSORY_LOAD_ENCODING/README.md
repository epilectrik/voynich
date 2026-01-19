# SENSORY_LOAD_ENCODING Phase

## Goal

Test the hypothesis that **sensory requirements are encoded as constraint pressure** (brittleness, recovery slack, timing) rather than as tokens or keywords in the Voynich Manuscript.

## Background

BRUNSCHWIG_FULL_MAPPING phase found 4 semantic anchors but NULL result for direct sensory anchoring:
- Only 7% real sensory content in Brunschwig procedures
- 4.5% overlap between LINK class and sensory keywords

External expert insight:
> "The Voynich Manuscript does not encode sensory cues. It encodes the *cost of ignoring them*."

## The Theory

Sensory requirements manifest as:
- **Recoverability constraints** - how forgiving is the process?
- **Timing sensitivity** - how narrow is the intervention window?
- **Brittleness** - what's the cost of misjudging?
- **Commitment irreversibility** - can you recover from mistakes?

| Sensory Modality | Voynich Signature |
|------------------|-------------------|
| SMELL | Short P-zones, high PHASE_ORDERING, early S-lock |
| SIGHT | High LINK ratio, low k-density, extended LINK→LINK runs |
| SOUND | h-boundaries that become absorbing, sudden prohibition |
| TOUCH | k modulation (already handled by energy encoding) |

## Phase Structure

| Phase | Script | Goal |
|-------|--------|------|
| 1 | `negative_anchor_test.py` | Confirm no direct sensory token encoding |
| 2 | `sensory_load_index.py` | Compute SLI, correlate with HT density |
| 3 | `brittleness_gradient.py` | Test P-zone compression in sensory-critical programs |
| 4 | `modality_signatures.py` | Test smell/sight/sound structural predictions |
| 5 | Report | Document findings |

## Key Metric: Sensory Load Index (SLI)

```
SLI = (PHASE_ORDERING + COMPOSITION_JUMP + CONTAINMENT_TIMING) / (escape_density + LINK_ratio)
```

- High SLI → sensory-critical operation
- Low SLI → robust, forgiving process

## Constraints

| Constraint | Requirement |
|------------|-------------|
| C171 | Zero material encoding |
| C469 | Categorical Resolution |
| C458 | Execution Design Clamp |
| C477 | HT Tail Correlation |
| C443 | Positional Escape Gradient |

## Success Criteria

- Negative anchor test: overlap < 5%
- SLI correlates with HT density (p < 0.05)
- P-zone negatively correlates with SLI (p < 0.05)
- At least 2/3 modality signatures validated
