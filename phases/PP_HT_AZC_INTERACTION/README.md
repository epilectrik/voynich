# PP_HT_AZC_INTERACTION Phase

## Objective

Investigate the three-way interaction between PP (Pipeline-Participating) vocabulary, HT (Human Track) density, and AZC (diagram system) mediation. Determine whether HT patterns are modulated by AZC involvement.

## Key Findings

### HT Dual Control Architecture (C798)

HT density is controlled by **two orthogonal factors**:

1. **AZC mediation** (negative effect):
   - Correlation: rho = -0.352, p = 0.0012
   - High AZC-mediation -> less HT
   - Interpretation: AZC vocabulary "displaces" HT

2. **Escape activity** (positive effect):
   - Correlation: rho = 0.377, p = 0.0005
   - High FL rate -> more HT
   - Interpretation: HT tracks operational intensity

These factors are **independent** (AZC-FL correlation = -0.023, NS) and **additive**:

| AZC Level | FL Level | Mean HT% |
|-----------|----------|----------|
| Low | Low | 31.4% |
| Low | High | 37.0% |
| High | Low | 25.2% |
| High | High | 30.2% |

### Line-1 AZC Independence (C799)

The line-1 header structure (C794-C795) is **NOT modulated by AZC**:

- Line-1 PP fraction: 66.7% (low AZC) vs 74.1% (high AZC), p=0.27 NS
- A-context prediction accuracy: 15.4% (low AZC) vs 12.5% (high AZC), p=1.0 NS
- Line-1 HT elevation (~24-25pp) is constant regardless of regime

The A-context declaration mechanism operates uniformly.

### Body HT Architecture (C800-C803)

Body HT (lines 2+) drives the escape correlation, with line-1 HT independent:

- Body HT vs FL: rho = 0.367, p = 0.0007
- Line-1 HT vs FL: rho = 0.107, p = 0.35 (NS)

Body HT uses **primitive PP vocabulary**:
- 80.1% PP (vs 68.3% in line-1)
- Top MIDDLEs: 'e', 'ed', 'd', 'l', 'k', 'o' (C085 primitives)
- Jaccard overlap with line-1: 0.122 (very low)

Body HT clusters at **line boundaries** and **LINK tokens**:
- First token HT: 45.8%
- Last token HT: 42.9%
- Middle tokens HT: 25.7%
- Distance to LINK: HT = 2.53, non-HT = 3.08 (p < 0.0001)
- Distance to FL: HT = 4.04, non-HT = 3.82 (p = 0.056, NS)

**Key insight:** Body HT correlates with escape at folio level but clusters near LINK tokens (not FL) at token level. HT marks monitoring/waiting zones, not escape points.

## Scripts

| Script | Tests | Key Findings |
|--------|-------|--------------|
| t1_azc_ht_baseline.py | AZC% vs HT% correlation | rho=-0.352, confounded by vocab size |
| t2_line1_azc_modulation.py | Line-1 by AZC tertile | No significant differences |
| t3_regime_ht_patterns.py | Kernel/Escape vs HT | Escape rho=0.377, Kernel rho=-0.241 |
| t4_escape_ht_mechanism.py | Path analysis | AZC and FL are orthogonal predictors |
| t5_body_ht_escape.py | Body vs Line-1 escape correlation | Body drives correlation (rho=0.367) |
| t6_body_ht_middles.py | Body HT MIDDLE patterns | 80.1% PP, primitives dominate |
| t7_body_ht_positions.py | Body HT positional patterns | Boundaries, LINK proximity |

## Constraints Produced

| # | Name | Finding |
|---|------|---------|
| C796 | HT-Escape Correlation | rho=0.377, p=0.0005 |
| C797 | AZC-HT Inverse | rho=-0.352, p=0.0012 |
| C798 | HT Dual Control | Orthogonal, additive effects |
| C799 | Line-1 AZC Independence | Header is fixed structure |
| C800 | Body HT Escape Driver | Body HT drives escape correlation, line-1 independent |
| C801 | Body HT Primitive Vocabulary | 80.1% PP, C085 primitives dominate |
| C802 | Body HT LINK Proximity | Clusters near LINK, not FL |
| C803 | Body HT Boundary Enrichment | 45.8%/42.9% at line boundaries |

## Interpretation

HT is not random padding. It encodes **two independent pieces of information**:

1. **Vocabulary provenance** (AZC axis):
   - High AZC-mediation means vocabulary is pre-filtered for legality
   - Less HT needed because context is implicit in vocabulary source

2. **Operational intensity** (FL axis):
   - High escape rate means complex execution with many recovery events
   - More HT needed to signal escape-heavy operational context

**Body HT Architecture:**
- Line-1 HT is a **fixed header structure** for A-context declaration
- Body HT marks **monitoring checkpoints** (control block boundaries, LINK proximity)
- Uses primitive PP vocabulary for minimal morphological complexity
- Reconciles C341 (HT-LINK association) with C796 (escape correlation)

## Dependencies

- C085 (10 single-character primitives)
- C341-C342 (HT-LINK decoupling)
- C360 (Line = control block)
- C746 (HT Folio Compensatory Distribution)
- C765 (AZC Kernel Access Bottleneck)
- C794-C795 (Line-1 Composite Header)

## Data Sources

- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`
- `scripts/voynich.py` (Transcript, Morphology)
