# C1390: p-Atom Marking Pause Profile

**Tier:** 2
**Scope:** B
**Phase:** P_ATOM_SEMANTIC_DEEP_DIVE (Phase 500)
**Depends on:** C1195 (atom gloss tiers), C1207 ({o,p} structural cluster), C1208 (p positive carryover), C1209 (p early-medial slot position), C1251 (p H-kernel affinity), C1216 (p->c junction), C1190 (MIDDLE additive composition), C1305 (MIDDLE determines category)

## Constraint

Atom p = "pause" (German: pausieren) is an AXM-enriched main-loop MARKING atom. It is the single most MARKING-dominant atom in the system (12.033x, 93.63% of all p-initial tokens), with the strongest carryover of any atom (8.126x). Evidence from 12 prediction tests (10 pass, 2 fail). SOLID upgrade justified by compositional convergence (3/4), universal MARKING injection (4/4 bases at +68.3pp mean), gateway compound op (95.5% INITIAL, 100% TRANSITION), and CHSH+p signal (MON+MARK 87.4%). p creates a MARKING pause that resets at line boundaries (cross-line 0.000x) and operates proactively within the main execution loop.

### Core behavioral profile
1. **Category signature**: MARKING 12.033x (#1 enriched atom in the entire system), MONITORING 1.508x. Depleted: THERMAL 0.041x (near-zero, comparable to c's 0.055x), CONTAINMENT 0.289x, STAGING 0.000x, TRANSITION 0.000x (outside op compound).
2. **AXM enrichment**: 88.7% AXM (1.311x enriched), 0% FL_HAZ, 0% FQ, 0% CC. Enriched in main execution loop but NOT over-confined (< 90%, less than c's 93.5%).
3. **ACTOR timing**: 26.7% post-state-change rate (vs baseline), proactive not reactive. Post-hazard enrichment 0.56x (depleted -- p is NOT triggered by hazards).
4. **Carryover**: 8.126x consecutive pair enrichment (#1 of all 17 atoms). C1208 delta = +0.138 (largest absolute delta of any atom, z=+4.27). ZERO cross-line carryover (0.000x) -- p resets at line boundaries.

### Compound mechanics
5. **MARKING dominance**: p dominates category in ALL p-containing compounds: cp=MARKING, pc=MARKING, ep=MARKING. This is unique -- p's 93.63% MARKING rate is so strong that the second atom cannot override it, which is why order sensitivity fails (cp=pc=MARKING, JSD=0.000).
6. **op gateway compound**: o(arrange)+p(pause) = TRANSITION. 95.5% INITIAL position in compound MIDDLEs (210/220), 100% TRANSITION category, 63 folios (76.8% corpus coverage). Functions as a process restart/transition point.
7. **CHSH+p extreme signal**: MON+MARK 87.4%, MARKING 11.86x, MONITORING 3.77x. Checkpoint prefix + p-containing MIDDLE = intensified marking/pause operations. Higher MON+MARK than CHSH+c.
8. **p->c junction is intra-token**: The p->c enrichment (11.02x, 306 tokens) operates WITHIN compounds (recreating pch PREFIX inside MIDDLEs), NOT across tokens. Cross-token p->c is depleted (0.78x). Same intra-compound pattern as c->h (Phase 499).
9. **MARKING injection (+68.3pp)**: p as first atom increases MARKING by +68.3 percentage points on average across all 4 testable bases (4/4 universal). This is the strongest single-category injection of any atom tested.

### Compositional convergence (decisive evidence)
10. **3/4 gloss-to-category matches**: op = o(arrange)+p(pause) = "start" -> TRANSITION (match), cph = c(adjust)+p(pause)+h(watch) = "measure" -> MONITORING (match), cp = c(adjust)+p(pause) -> MARKING (match). ep = e(cool)+p(pause) = "precision cool" -> expected THERMAL but actual MARKING (miss -- p dominates e).
11. **ep anomaly explained**: ep is 100% MARKING, not THERMAL. p's MARKING dominance (93.63%) overwhelms e's THERMAL signal. The compound gloss "precision cool" may need revision -- the actual operation is MARKING (a pause during cooling), not a thermal operation.

### What was falsified
- **Order sensitivity**: cp and pc produce identical categories (100% MARKING, JSD=0.000). Unlike c-atom where ck/kc show 100% category flips, p's MARKING dominance prevents position from affecting outcome.
- **Section gradient as MARKING tracker**: While MARKING rho=+0.657 passes the +0.40 threshold, the best section gradient tracker is FLOW (rho=+0.714). p tracks FLOW slightly better than MARKING across sections.
- **NEUTRAL timing**: p shows ACTOR timing (26.7%), not NEUTRAL (35-55%) as predicted for "pause". This suggests p is proactively applied, not a passive wait.

## Gloss

p = "pause" (pausieren, German: to pause). SOLID. AXM-enriched main-loop MARKING atom. Creates a marking pause within the operational cycle, resetting at line boundaries (cross-line 0.000x). The #1 MARKING atom (12.033x, 93.63%) and #1 carryover atom (8.126x) in the system. Gateway compound op = "start" (TRANSITION, 95.5% INITIAL). ACTOR timing (proactive). German etymology consistent: K=Kochen, E=Erkalten, C=Corrigieren/Justieren, D=Dichten, T=Treiben, O=Ordnen, P=Pausieren.

Compound readings (3/4 verified by compositional convergence): op = arrange+pause -> "start" (TRANSITION), cph = adjust+pause+watch -> "measure" (MONITORING), cp = adjust+pause -> MARKING, ep = cool+pause -> "precision cool" glossed but actual MARKING (p dominates). pc = pause+adjust -> MARKING (no order sensitivity).

## Falsification

Would be falsified if: (1) p-initial tokens appear with significant FL_HAZ presence (currently 0%), or (2) op loses its INITIAL position dominance (currently 95.5%), or (3) new compounds show p NOT dominating MARKING category (currently universal across all p-compounds except op).

## Provenance

- `phases/P_ATOM_SEMANTIC_DEEP_DIVE/scripts/p_p01_*.py` through `p_p12_*.py` -- 12 prediction scripts
- `phases/P_ATOM_SEMANTIC_DEEP_DIVE/results/p_atom_prediction_results.json` -- structured results
