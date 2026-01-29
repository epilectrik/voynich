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
| F-B-001 | LINK Operator as Sustained Monitoring Interval | F2 | C366, C609, C190 | SUCCESS |
| F-B-002 | QO Lane as Safe Energy Pathway | F3 | C601, C574, C600 | SUCCESS |
| F-B-003 | Pre-Operational Configuration via A→AZC→B Pipeline | F2 | C473, C506, C468 | SUCCESS |
| F-B-004 | Lane Hysteresis Control Model | F2 | C643, C549, C577, C608 | SUCCESS |
| F-B-005 | PP-Lane MIDDLE Discrimination | F2 | C646, C576, C642 | SUCCESS |
| F-B-006 | Energy/Stabilization Lane Assignment | F3 | C647, C645, C601, C521 | PARTIAL |
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

### Currier B Operational Controls (C190, C366, C468, C473, C506, C574, C600, C601, C609)

| Constraint | Fit ID | What Fit Explains |
|------------|--------|-------------------|
| C366 | F-B-001 | LINK phase boundary maps to monitoring-to-intervention transition |
| C609 | F-B-001 | 13.2% LINK density maps to sustained monitoring duty cycle |
| C190 | F-B-001 | LINK-CEI anticorrelation (r=-0.7057) maps to stable-process monitoring pattern |
| C601 | F-B-002 | QO's 0/19 hazard exclusion maps to non-fire/safe thermal pathway |
| C574 | F-B-002 | QO-CHSH grammatical identity maps to same operations at different risk levels |
| C600 | F-B-002 | CC sub-group trigger selectivity maps to distinct entry points for different methods |
| C473 | F-B-003 | A-record as constraint bundle maps to pre-operational configuration (fuel, vessel, method) |
| C506 | F-B-003 | PP→survival correlation (r=0.715) maps to better configuration → more operational options |
| C468 | F-B-003 | B blind execution maps to operator executing within pre-set apparatus constraints |

**Interpretation:** F-B-001 through F-B-003 demonstrate alignment between Brunschwig's verified distillation control practices and Currier B's structural architecture. All mappings verified against original German text (sources/brunschwig_1500_text.txt, Part 1, lines 1-2800).

---

### Lane Architecture (C549, C576, C577, C601, C608, C642-C647)

| Constraint | Fit ID | What Fit Explains |
|------------|--------|-------------------|
| C643 | F-B-004 | Lane oscillation (0.563 vs 0.494 null) accounts for hysteresis control pattern |
| C549 | F-B-004 | Interleaving significance re-confirmed at within-line level with run lengths |
| C577 | F-B-004 | Content-driven oscillation rates (BIO=0.606, HERBAL_B=0.427) |
| C608 | F-B-004 | Short runs (median 1.0) confirm no lane coherence |
| C646 | F-B-005 | 20/99 PP MIDDLEs predict lane preference (z=24.26) |
| C576 | F-B-005 | Vocabulary bifurcation has k/t vs o character-content basis |
| C642 | F-B-005 | A-record architecture transmits lane-relevant information |
| C647 | F-B-006 | QO k=70.7%, CHSH e=68.7% accounts for energy/stabilization assignment |
| C645 | F-B-006 | CHSH 75.2% post-hazard accounts for stabilization function |
| C601 | F-B-006 | QO zero hazard accounts for safe (non-hazardous) energy application |
| C521 | F-B-006 | Kernel directionality (e absorbing) consistent with CHSH stabilization role |

**Interpretation:** F-B-004 through F-B-006 establish that the two execution lanes (QO/CHSH) exhibit hysteresis-like oscillation, are predicted by A-side PP MIDDLE vocabulary, and carry distinct kernel-character morphological signatures (QO=k-energy, CHSH=e-stability). The "Change/Hold" interpretation (QO=hold, CHSH=change) is falsified in its literal form; the reversed mapping (QO=energy addition, CHSH=stabilization) is consistent with all Tier 0-2 constraints. F-B-002 annotation confirms "safe energy pathway" = controlled energy application.

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
