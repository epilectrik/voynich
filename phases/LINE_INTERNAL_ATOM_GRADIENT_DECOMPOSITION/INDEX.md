# Phase 581: Line-Internal Atom Gradient Decomposition

**Status:** COMPLETE
**Phase type:** Corpus analysis
**Simulation budget:** 0 traces

## Goal

Decompose the validated line three-zone architecture (C1425-C1430) at individual atom resolution. Determine which specific HEAD, TERMINAL, and MODIFIER atoms drive each zone transition, with focus on the Q3->Q4 closure step (C1566). Test hazard x atom x position interaction and section-conditioned gradients.

## Target Constraints

| ID | Track | Verdict | Runtime |
|----|-------|---------|---------|
| C1671 | Atom positional gradient structure | GRADIENT_HETEROGENEOUS | <1s |
| C1672 | Q3->Q4 atom decomposition | CLOSURE_DISTRIBUTED | <1s |
| C1673 | Hazard x atom x position | HAZARD_POSITION_COUPLED | <1s |
| C1674 | Section-conditioned atom gradients | SECTION_MODULATES_GRADIENT | <1s |

## Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| t0_data_assembly.py | Load B tokens with position, atom, hazard, category, section | PASS |
| t1_atom_positional_gradients.py | HEAD/TERM/MOD x quintile profiles, chi-squared, 6 predictions | PASS |
| t2_q3q4_decomposition.py | Per-atom JSD contribution to Q3->Q4 step | PASS |
| t3_hazard_atom_position.py | Hazard x HEAD x zone interaction | PASS |
| t4_section_conditioned_gradients.py | Section-specific atom gradients | PASS |
| t5_synthesis.py | Write C1671-C1674, generate REPORT_581.md | PASS |

## Data Sources

| File | Fields |
|------|--------|
| scripts/voynich.py | Transcript, Morphology, decompose_middle_hmt, CategoryClassifier |
| data/decoder_maps.json | frame_hazard map |

## Key Results

- 23,074 tokens across 2,406 lines analyzed
- HEAD atoms gradient heterogeneously (chi2=659, min cosine=0.929): e/headless most position-sensitive, o nearly flat
- Q3->Q4 closure driven primarily by m-terminal (77% of TERM JSD), HEAD closure is distributed (e-collapse + headless/a-surge)
- Hazard x position strongly coupled (chi2=337, 16 zone-specific pairs); work-zone safety is k-LED
- Sections preserve scaffold but modulate amplitudes (C section HEAD corr=0.76, Q3Q4 JSD ratio=2.2x)
- 5/6 predictions passed (P5 failed: r-terminal not depleted at Q0)
- Position-sensitive atoms are predominantly POSITIVE carryover (50% of top-6)

## Key Prior Constraints

- C1425-C1430: Three-zone line model (SPEC/WORK/CLOSURE)
- C1463-C1466: Zone-hazard routing
- C1475-C1479: HEAD atom domain taxonomy
- C1487: Terminal functional taxonomy (LOCKED/CHANNELED/DIFFUSE)
- C1566: Q3->Q4 step discontinuity (26x HEAD JSD, 20x TERM JSD)
- C1208: Atom carryover classification (POSITIVE/NEGATIVE/NEUTRAL)
