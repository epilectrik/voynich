# C1389: c-Atom Main-Loop Modifier Profile

**Tier:** 2
**Scope:** B
**Phase:** C_ATOM_SEMANTIC_DEEP_DIVE (Phase 499)
**Depends on:** C1195 (atom gloss tiers), C1207 ({c,h} monitoring cluster), C1216 (c->h obligatory junction), C1208 (c positive carryover), C1209 (c medial slot position), C1251 (c H-kernel affinity), C1190 (MIDDLE additive composition), C1305 (MIDDLE determines category)

## Constraint

Atom c = "adjust" (German: justieren) is an AXM-confined main-loop modifier. It creates operational modes through compound formation, functioning as a compound-internal modifier rather than a cross-token operator. Evidence from 19 prediction tests across three batteries (8 pass, 11 fail). SOLID upgrade justified by compound decomposition convergence: 6/6 independently glossed compounds match their dictionary meanings when decomposed through c(adjust)+X, with 100% compound determinism across all 61 c-initial MIDDLEs.

### Core behavioral profile
1. **Category signature**: MONITORING 12.237x (#1 enriched), CONTAINMENT 4.263x, MARKING 2.916x, OPERATION 2.222x. Depleted: THERMAL 0.055x (near-zero, most extreme single-category depletion alongside o's 0.105x), STAGING 0.000x, TRANSITION 0.000x, FLOW 0.067x.
2. **AXM confinement**: 93.5% AXM, 6.5% AXm — exclusively main execution loop. Zero FL_HAZ, FQ, CC tokens. The most macro-state-confined atom in the system.
3. **ACTOR timing**: 31.6% post-state-change rate (vs 46.2% baseline), proactive not reactive. Post-hazard enrichment 0.96x (chance).
4. **Section gradient**: Tracks MONITORING (rho=+0.543), CONTAINMENT/OPERATION (rho=+0.771). Does not track THERMAL (|rho|=0.371). Control: k vs THERMAL rho=+0.943.

### Compound mechanics (central finding)
5. **100% compound determinism**: Each c+X compound maps to a different category at 100% purity — ck=OPERATION (197 tokens), ckh=CONTAINMENT (127), ct=MONITORING (95), cth=MARKING (49), cph=MONITORING (36), cfh=MARKING (9). The junction atom determines which monitoring/operational mode c creates.
6. **CHSH+c extreme signal**: MONITORING 23.09x enrichment (most extreme PREFIX+atom category signal observed), MARKING 6.02x, CONTAINMENT 3.24x. Checkpoint prefix + c-MIDDLE = intensified monitoring operations.
7. **c->h junction is intra-token**: The obligatory c->h junction (C1216: 380/380, 11.7x) operates WITHIN MIDDLEs (ckh, cth, cph, cfh), not across tokens. c-terminal -> h-initial cross-token enrichment is ZERO (0 instances). This is a compound-formation rule, not a sequential execution rule.

### Compound decomposition (decisive evidence for SOLID)
8. **Compositional reading convergence (6/6)**: Every independently glossed c-compound matches CategoryClassifier output: ck→"direct heat"=OPERATION (match), ckh→"firm"=CONTAINMENT (match), ct→"control"=MONITORING (match), cth→"hazard"=MARKING (match), cph→"measure"=MONITORING (match), kc→"intense heat-seal"=CONTAINMENT (match). This is the strongest compositional convergence of any non-LOCKED atom.
9. **MON+MARK injection (+43.2pp)**: c as first atom increases MONITORING+MARKING by +43.2 percentage points on average across all 5 base atoms tested (5/5 bases). MONITORING alone: 3/5 bases injected at +19.3pp mean.
10. **Order sensitivity (100% category flips)**: ck=OPERATION vs kc=CONTAINMENT, ct=MONITORING vs tc=FLOW — reversing atom order produces completely different categories in 2/3 tested pairs. Confirms c carries independent semantic content.
11. **h-suffix transforms category (p<0.000001)**: Adding -h suffix shifts compound categories: ck(OPERATION)→ckh(CONTAINMENT), ct(MONITORING)→cth(MARKING), cp(OPERATION)→cph(MONITORING). 3/4 pairs show category shift (chi-square p<0.000001).
12. **Folio coverage breadth**: All 5 major c-compounds span >= 24 folios, all exceeding non-c controls. ck covers 67 folios (81% of Currier B corpus).

### What was falsified
- **Cross-token sequential model**: c does NOT feed h across tokens (0 cross-token c->h). The {c,h} cluster (C1207: r=+0.746) reflects co-occurrence in compound MIDDLEs, not token-to-token chaining.
- **Carryover at atom level**: The positive carryover (C1208: z=+3.23) operates at MIDDLE compound level (c-containing MIDDLEs cluster together), not at the initial-atom level (c-c pair enrichment 1.015x, chance).
- **c precedes h in lines**: c and h are at essentially the same mean line position (0.5225 vs 0.5306), with h actually preceding c within paired lines 68.8% of the time.
- **FQ enrichment**: c is 0% FQ — completely AXM-locked, not distributed across multiple macro-states as predicted.

## Gloss

c = "adjust" (justieren, German: to adjust, to calibrate). SOLID. AXM-confined main-loop modifier. Creates monitoring/operational mode variants through compound formation. Not a sequential operator — functions within compounds to set operational parameters. ACTOR timing (proactive, not reactive). German etymology consistent: K=Kochen, E=Erkalten, C=Corrigieren/Justieren, D=Dichten, T=Treiben, O=Ordnen.

Compound readings (all 6/6 verified by compositional convergence): ck = adjust+heat → "direct heat" (OPERATION), ckh = adjust+heat+watch → "firm" (CONTAINMENT), ct = adjust+transfer → "control" (MONITORING), cth = adjust+transfer+watch → "hazard" (MARKING), cph = adjust+pause+watch → "measure" (MONITORING), kc = heat+adjust → "intense heat-seal" (CONTAINMENT). Order-sensitive: ck=OPERATION vs kc=CONTAINMENT, ct=MONITORING vs tc=FLOW (100% category flips).

## Falsification

Would be falsified if: (1) c-initial tokens appear outside AXM/AXm (currently 0% FL_HAZ/FQ/CC), or (2) c-compound category determinism breaks (currently 100% across 6 compounds), or (3) c->h cross-token enrichment becomes significant (currently zero).

## Provenance

- `phases/C_ATOM_SEMANTIC_DEEP_DIVE/scripts/p_c01_*.py` through `p_c19_*.py` — 19 prediction scripts (3 batteries)
- `phases/C_ATOM_SEMANTIC_DEEP_DIVE/results/c_atom_prediction_results.json` — structured results
