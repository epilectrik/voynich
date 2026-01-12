# Fit to Constraint Mapping

**Purpose:** Cross-reference which fits support or refine which constraints

**Warning:** Fits explain patterns. They do NOT create or modify constraints.

---

## How to Use

Look up a fit ID to see which constraints it supports.
Look up a constraint number to see which fits explain its mechanism.

---

## Fit → Constraint (by Fit ID)

| Fit ID | Name | Tier | Supports | Result |
|--------|------|------|----------|--------|
| F-A-001 | Compositional Token Generator | F2 | C267-C282 | PARTIAL |
| F-A-002 | Sister-Pair Classifier | F1 | C407-C410 | NULL |
| F-A-003 | Repetition Distribution | F2 | C250-C258 | PARTIAL |
| F-A-004 | Entry Clustering HMM | F2 | C424 | SUCCESS |
| F-A-005 | Scarcity-Weighted Registry Effort | F1 | C293 (partial) | NULL |
| F-A-007 | Forbidden-Zone Attraction | F1 | C281 (unexpectedly) | NULL (opposite) |
| F-A-008 | Repetition as Relational Stabilizer | F1 | C287-C290 (weakly) | NULL |
| F-A-009 | Comparability Window | F2 | C424 (refines) | SUCCESS |
| F-ECR-001 | Material-Class Identification | F3 | C109-C114, C232 | SUCCESS |
| F-ECR-002 | Apparatus-Role Identification | F3 | C085-C108, C171, C216 | SUCCESS |
| F-ECR-003 | Decision-State Semantics | F3 | C384, C404-C405, C459-C460 | SUCCESS |
| F-AZC-015 | Windowed AZC Activation Trace | F2 | C440, C441-C444 | SUCCESS |
| F-AZC-016 | AZC->B Constraint Fit Validation | F2 | C468, C469, C470 | SUCCESS |

---

## Constraint → Fit (by Constraint Range)

### Currier A Morphology (C267-C282)

| Constraint | Fit ID | What Fit Explains |
|------------|--------|-------------------|
| C267-C282 | F-A-001 | 98% of token frequency explained by factored model |

### Currier A Multiplicity (C250-C266)

| Constraint | Fit ID | What Fit Explains |
|------------|--------|-------------------|
| C250-C258 | F-A-003 | Shifted Poisson approximately fits repetition counts |

### Sister-Pair Architecture (C407-C411)

| Constraint | Fit ID | What Fit Explains |
|------------|--------|-------------------|
| C407-C410 | F-A-002 | NULL: contextual features fail to predict ch/sh |

**Interpretation:** F-A-002 failure supports C411 (sister selection is human/external).

### Entry Clustering (C424+)

| Constraint | Fit ID | What Fit Explains |
|------------|--------|-------------------|
| C424 | F-A-004 | 2-state Markov fully explains clustering autocorrelation |
| C424 | F-A-009 | Clustering correlates with universality band (layout scaffolding) |

**Interpretation:** F-A-004 showed clustering follows Markovian dynamics. F-A-009 refines this: clustering is not just random local stickiness - entries with similar universality band cluster 34% more than expected. This suggests layout provides weak scaffolding for relational comparison.

### MIDDLE Discriminator (C293)

| Constraint | Fit ID | What Fit Explains |
|------------|--------|-------------------|
| C293 | F-A-005 | NULL: scarcity-effort compensation is section-specific (H only) |

**Interpretation:** F-A-005 shows partial support for C293 in H section, but effect does not generalize across sections. Registry effort adaptation is not universal.

### PREFIX-BOUND MIDDLE (C276) and Component Sharing (C281)

| Constraint | Fit ID | What Fit Explains |
|------------|--------|-------------------|
| C276/C281 | F-A-007 | NULL (opposite): A prefers universal MIDDLEs, avoids exclusives |

**Interpretation:** F-A-007 found the **opposite** of boundary attraction. Currier A systematically selects vocabulary that works across prefix families (48% universal MIDDLEs vs 8% in random). This unexpectedly supports C281 (components SHARED) and suggests registry is designed for cross-reference, not frontier recording.

### Literal Enumeration (C287-C290)

| Constraint | Fit ID | What Fit Explains |
|------------|--------|-------------------|
| C287-C290 | F-A-008 | NULL: repetition is uniform across universality classes |

**Interpretation:** F-A-008 tested whether universal vocabulary receives more repetition (salience reinforcement). It does not. Relationality is enforced through selection (F-A-007), not reinforcement. Repetition serves literal enumeration uniformly.

---

### Entity-Class Reconstruction - ECR (Global)

| Constraint | Fit ID | What Fit Explains |
|------------|--------|-------------------|
| C109-C114 | F-ECR-001 | 4 material classes inferred from hazard topology |
| C232 | F-ECR-001 | Section conditioning explained by class instantiation |
| C085-C108 | F-ECR-002 | Kernel operators map to apparatus roles |
| C171 | F-ECR-002 | Circulatory requirement implies circulation path role |
| C216 | F-ECR-002 | Hybrid hazard model explains 71/29 batch/apparatus split |
| C384 | F-ECR-003 | A↔B decoupling explained by layer decision archetypes |
| C404-C405 | F-ECR-003 | HT non-operational explained by attention archetype |
| C459-C460 | F-ECR-003 | AZC orientation role explained by context archetype |

**Interpretation:** ECR fits demonstrate that frozen constraints can be explained by a coherent apparatus-centric model. Material classes, apparatus roles, and decision archetypes are mutually consistent and satisfy all referenced constraints.

---

### AZC Pipeline Resolution (C440-C444, C468-C470)

| Constraint | Fit ID | What Fit Explains |
|------------|--------|-------------------|
| C440-C444 | F-AZC-011, F-AZC-012 | Uniform B-to-AZC sourcing, vocabulary-activated constraints |
| C466-C467 | F-A-014b | PREFIX encodes control-flow participation, qo- is kernel-adjacent |
| C468 | F-AZC-016 | 28x escape rate transfer from AZC to B |
| C469 | F-AZC-015, F-AZC-016 | Categorical resolution via vocabulary legality |
| C470 | F-AZC-016 | 12.7x MIDDLE restriction inheritance |

**Interpretation:** F-AZC-015 established AZC is an ambient legality field (70% of folios active per window). F-AZC-016 validated causal constraint transfer: escape rates and MIDDLE restrictions propagate from AZC to B. The pipeline A -> AZC -> B is structurally and behaviorally validated.

---

## Failed Fits (F1 Registry)

Failed fits provide negative knowledge by exclusion.

| Fit ID | What Failed | Supports by Exclusion |
|--------|-------------|----------------------|
| F-A-002 | Contextual ch/sh prediction | Sister choice is external to text features |
| F-A-005 | Universal scarcity-effort compensation | Effect is section-specific (H only), not registry-wide |
| F-A-007 | Boundary/frontier attraction | Registry prefers INTERIOR (universal), not boundary (exclusive) |
| F-A-008 | Repetition as salience reinforcement | Repetition is uniform; relationality enforced through selection only |

---

## Fits Pending Constraint Mapping

| Fit ID | Status | Notes |
|--------|--------|-------|
| (none currently) | - | - |

---

## Fits That MAY Suggest New Constraints

**WARNING:** New constraints require human authorization.

| Fit ID | Potential Finding | Current Status |
|--------|-------------------|----------------|
| F-A-004 | Clustering autocorrelation exactly matches 2-state Markov | Logged as fit only |

---

## Navigation

← [phase_to_claim.md](phase_to_claim.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
