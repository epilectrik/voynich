# Phase 585: ATOM_COMPOSITIONAL_GENERATOR

**Status:** COMPLETE
**Date:** 2026-03-14
**Version:** 5.58
**Constraints:** C1689-C1695

## Purpose

Retest F-BRU-003 ("Property-Based Generator Rejection", v2.44, 2026-01-15) with the atom architecture discovered after F-BRU-003 was run. F-BRU-003 tested a naive property generator (8 random bins, featureless MIDDLEs) before the HEAD+MOD+TERM atom composition was known (C1190, C1250, C1393-C1498). This phase retests with atom-aware compositional generators and a diagnostic isolating whether the clustering gap is in composition or deployment.

## Philosophy

Refine existing constraints rather than expand the system. Strengthen or downgrade older tests against current understanding.

## Scripts

| Script | Runtime | Purpose |
|--------|---------|---------|
| `scripts/atom_compositional_generator.py` | ~3 min | Main 6-step retest: baseline, logistic model, 5 generators, ablation, scale sensitivity |
| `scripts/diagnostic_real_middles.py` | ~3 min | Diagnostic: logistic model applied to real MIDDLEs to isolate gap source |

## Results

### Main Script Results

| Model | Clustering | vs Real (0.873) |
|-------|-----------|-----------------|
| Naive (F-BRU-003 repro) | 0.021 | 2.4% |
| Independent Features K=100 | 0.475 | 54.4% |
| Structured-Random (uniform params) | 0.501 | 57.4% |
| Empirical (real params) | 0.599 | 68.6% |
| Param-Independent (no cross-slot deps) | 0.623 | 71.4% |
| **Real Voynich** | **0.873** | **100%** |

- Logistic compatibility model AUC: 0.7452
- Ablation: no single layer dominant (all 0.56-0.62)
- Scale sensitivity: stable across N=500/972/1500

### Diagnostic Results (logistic model on REAL MIDDLEs)

| Metric | Value |
|--------|-------|
| Density-matched threshold | 0.7335 |
| Predicted clustering (real MIDDLEs) | 0.412 |
| Real clustering | 0.873 |
| Edge Jaccard overlap | 0.064 |
| Precision | 0.119 |
| Recall | 0.122 |

**Diagnosis: COMPATIBILITY MODEL is the bottleneck.** Atom features do not predict which MIDDLEs co-occur on lines. The discrimination manifold's clustering arises from the deployment grammar, not morphological composition.

## Constraint Verdicts

| C# | Verdict | Description |
|----|---------|-------------|
| C1689 | ATOM_COMPATIBILITY_PARTIAL | Logistic AUC 0.745 but edge Jaccard 6.4% on real MIDDLEs |
| C1690 | COMPOSITION_BREAKS_CEILING | Empirical 0.599 > independent feature ceiling 0.49 |
| C1691 | SLOT_ARCHITECTURE_SUFFICIENT | Structured-Random 0.501 = 83.6% of Empirical 0.599 |
| C1692 | CROSS_SLOT_DEPENDENCIES_NEUTRAL | Param-Independent 0.623 >= Empirical 0.599 |
| C1693 | NAIVE_PROPERTY_CONFIRMED_DEAD | Naive model clustering 0.021 (H-filtered clean baseline) |
| C1694 | NO_DOMINANT_COMPOSITIONAL_LAYER | Ablation range 0.56-0.62, no single layer dominant |
| C1695 | DEPLOYMENT_NOT_COMPOSITIONAL | Real MIDDLEs predicted clustering 0.412, edge Jaccard 0.064 |

## F-BRU-003 Status Update

F-BRU-003 **NARROWED** (not killed, not strengthened):
- Its naive model correctly fails (C1693 confirms)
- But its conclusion "permanently kills property/low-rank interpretations" is too broad
- Atom composition breaks the 0.49 ceiling (C1690), which F-BRU-003 never tested
- However, even atom composition fails to predict real deployment (C1695)
- Net: F-BRU-003 kills naive property models; atom-compositional models get further but still fail at the deployment layer

## Key Finding

The discrimination manifold (0.873 clustering) is a property of the **deployment grammar** (B execution: kernel structure, hazard avoidance, program logic), NOT of **morphological composition** (atom architecture: HEAD+MOD+TERM). Atoms build MIDDLEs; the grammar decides which MIDDLEs co-occur.
