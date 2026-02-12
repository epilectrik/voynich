# Phase: CONSTRAINT_ENERGY_FUNCTIONAL

## Purpose

Scalarize the ~100D MIDDLE discrimination space (C981-C989) into a per-line compatibility energy metric. Test whether B execution lines are low-energy paths through A's constraint manifold — not just respecting boundaries (T12: 37× enrichment), but actively minimizing constraint tension.

## Architectural Position

This phase does NOT discover new grammar. It operationalizes:
- The residual cosine geometry (C987: continuous manifold)
- The hub-residual decomposition (C986: frequency vs constraint)
- The B embedding concordance (C989: 80.2% token-level compatibility)

Into a single scalar that can be tested against known structural features.

## Energy Functional Definition

```
E(line) = (1/N_pairs) × Σ_{i<j} cos(r_i, r_j)
```

Where:
- r_i, r_j are residual-space embeddings (eigenvectors 2-100, hub removed) of MIDDLEs on the line
- N_pairs = number of MIDDLE pairs where both MIDDLEs exist in A-space (972)
- Lines with <2 A-space MIDDLEs are excluded

Higher E = more internally compatible line (MIDDLEs face same residual direction).
Lower E = more constraint tension (MIDDLEs face opposing directions).

## Tests

### T1: Energy Functional Definition and Line-Level Distribution
**Goal:** Establish E(line) as a well-behaved scalar.
- Compute E for all B lines with ≥2 A-space MIDDLEs
- Distribution shape, quartiles, mean, variance
- Correlation with line length (expect weak — energy is normalized)
- Null comparison: random MIDDLE subsets of matching size (1000 shuffles)
- Coverage: what fraction of B lines have ≥2 A-space MIDDLEs?
- Compare A-line energy to B-line energy distributions

**Verdict:** WELL_DEFINED if distribution is non-degenerate and significantly different from random null.

### T2: Hazard Association
**Goal:** Test whether constraint tension increases near hazard events.
- E vs distance-to-nearest-hazard-class token (C669: rho=-0.104)
- E on lines containing hazard tokens vs lines without
- Lane-specific: QO lines vs CHSH lines (C669: QO tightens, CHSH static)
- REGIME stratification (C979: R2/R3 strongest tightening)
- Pre-hazard energy drop: E on line N-1 vs line N where N contains hazard

**Prediction:** E drops (more tension) as hazard proximity increases. Effect strongest in QO lane and REGIME 2/3.

### T3: Escape and Zone Association
**Goal:** Test whether escape events correlate with constraint energy and whether AZC source zone modulates energy.
- E on lines containing escape events vs lines without (C667)
- E by AZC source zone of constituent MIDDLEs (C443: escape rate C > R1 > R2 > R3 = S)
- Mean E for MIDDLEs sourced from each AZC zone
- Radial depth in embedding vs escape rate (the expert's "geometric closure" test)

**Prediction:** Higher-escape-rate vocabulary comes from higher-energy (more compatible) regions. Escape = having residual-space slack.

### T4: REGIME and Program Structure
**Goal:** Test whether REGIME modulates energy variance (not mean) and whether energy trajectories track convergence.
- E by REGIME (C979: topology invariant, weights differ)
- E variance by REGIME (expect R4 tightest, R1 loosest)
- E across folio line position (program progression)
- E trajectory toward terminal state (C074: 57.8% STATE-C)
- Late-folio E vs early-folio E (convergence tightening)

**Prediction:** REGIME modulates E variance, not mean. Energy tightens monotonically toward convergence.

### T5: Kernel Composition Shift
**Goal:** Test whether the h/e kernel shift (C965) corresponds to energy landscape movement.
- E vs h-kernel fraction on the line (C965: h increases through body)
- E vs e-kernel fraction (C965: e decreases)
- Safe-pool E vs hazard-pool E (C965: shift localized to safe pool)
- Compound MIDDLE energy vs simple MIDDLE energy
- Line-1 (HT specification) E vs body-line E

**Prediction:** h-kernel enrichment correlates with higher E (monitoring vocabulary is more compatible). Safe-pool drives the energy trajectory; hazard-pool energy is invariant.

## Resources

| Resource | Path | Use |
|----------|------|-----|
| Compatibility matrix | phases/DISCRIMINATION_SPACE_DERIVATION/results/t1_compat_matrix.npy | Embedding source |
| Eigenvalues | phases/DISCRIMINATION_SPACE_DERIVATION/results/t1_eigenvalues.npy | Hub removal |
| T11 results | phases/DISCRIMINATION_SPACE_DERIVATION/results/t11_hub_residual_structure.json | Residual structure |
| T12 results | phases/DISCRIMINATION_SPACE_DERIVATION/results/t12_b_side_validation.json | B concordance baseline |
| voynich.py | scripts/voynich.py | Transcript, Morphology, RecordAnalyzer |
| BCSC contract | context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml | Line structure, hazard, convergence |

## Key Constraints Under Test

| Constraint | What E(line) Tests |
|-----------|-------------------|
| C669 | Hazard proximity → energy gradient |
| C667 | Escape density → energy association |
| C979 | REGIME → energy variance modulation |
| C434/C443 | Zone progression → energy by source zone |
| C965 | Kernel shift → energy landscape movement |
| C074 | Convergence → energy trajectory tightening |

## Stop Condition

This phase is CONSOLIDATION, not exploration. Five tests, tight scope. Do not:
- Discover new grammar features
- Reopen interpretive questions
- Expand beyond the energy functional framework
- Add tests beyond T1-T5

## Expected Outcomes

**If E is well-defined and predictive:**
- B lines are low-energy paths through A's constraint manifold
- Confirms geometric optimality of execution (beyond mere legality)
- Energy functional becomes a diagnostic tool for future analysis

**If E is non-predictive:**
- Constraint geometry is real but not energetically ordered
- B respects boundaries but doesn't minimize tension
- Still valuable: rules out energy minimization hypothesis
