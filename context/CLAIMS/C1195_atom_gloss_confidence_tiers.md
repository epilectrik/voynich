# C1195: Atom Gloss Confidence Tiers

**Tier:** 2
**Scope:** B
**Phase:** ATOM_GLOSS_AUDIT (Phase 424)
**Depends on:** C1190 (MIDDLE additive composition), C777 (FL state index)

## Constraint

The 18 MIDDLE atom glosses fall into four confidence tiers based on compound evidence validation:

| Tier | Atoms | Count | Criterion |
|------|-------|-------|-----------|
| **LOCKED** | k(heat), e(cool), h(watch), y(end), i(iterate), n(halt), a(yield), m(final) | 8 | Strong compound evidence, internally consistent across multiple glossed compounds |
| **SOLID** | d(mark), t(transfer), l(state), o(arrange), c(adjust), p(pause) | 6 | Good evidence from compounds, correct but label might be refined |
| **PLAUSIBLE** | f(flag), s(sequence), g(complete), x(diagram), r(respond) | 5 | Thin evidence, nothing contradicts; too few compounds to fully validate |
| **WEAK** | *(none)* | 0 | All atoms now at PLAUSIBLE or above |

## Evidence

Spot-check analysis of all 18 atoms against 91 manually glossed compounds (GLOSSING.md + dictionary):

- **LOCKED atoms**: Each validated against 4+ glossed compounds where atom decomposition explains the compound gloss. Example: k=heat validated through ke=sustained heat, ck=direct heat, ek=precision, kc=intense heat-seal (order-sensitive). The i+n family (in=link, iin=iterate, ain=intake, aiin=settle) is the most internally consistent family in the system.
- **SOLID atoms**: d=mark validated through ed=discharge, od=collect, ked=release, keed=vent, eod=stand — all output/product operations. Could be refined to "product". t=transfer fits ct=control, te=rapid gather, et=path, ot=route.
- **SOLID atom l=state**: Upgraded from WEAK ("frame") to SOLID ("state") by Phase 496 (C1385). 15-round investigation established l as state/condition marker: 68.9% post-state-change rate (vs 47.2% baseline), 77% kernel-before-l ordering, kernel contact avoidance (rho=-0.197), Mode B locking. German candidate: Lage. Compound readings: ol=arrange-state (LINK operator, C874), el=cool-state, kl=heat-state.
- **PLAUSIBLE atom r=respond**: Upgraded from WEAK ("input") to PLAUSIBLE ("respond") by Phase 497 (C1387). 10-round investigation established r as a responder atom: 72.6% post-state-change rate, ar monopolizes FL_HAZ (248:0 vs or, 4.910x enrichment), anti-cycling (rho=-0.334, p=0.003), iteration-axis chaining (r→a 2.142x). PLAUSIBLE ceiling due to a/o initial confound — only 2 MIDDLE forms (ar, or) exist.
- **SOLID atom o=arrange**: Upgraded from WEAK ("work") to SOLID ("arrange") by Phase 498 (C1388). 23-test investigation across three batteries: vessel hypothesis (3/12), ordnen hypothesis (4/8), tiebreakers (1/3). The CONTAINMENT prediction (vessel/Ofen) was falsified, but the ordnen (arrange) hypothesis confirmed through convergent evidence: (1) C874 convergence — ol independently established as LINK operator from structural analysis, compositional decomposition independently yields o(arrange)+l(state) = 100% STAGING at 7.68x; (2) 100% compound determinism — ol=STAGING, ok=CONTAINMENT, or=FLOW, ot=MONITORING; al=FLOW vs ol=STAGING proves first atom carries independent semantic content; (3) anti-THERMAL 0.105x (most extreme depletion of any atom), anti-AXM #1 of 20, kernel interleaver #1. Temporal ordering falsified (48.6%, chance) — o is a domain marker, not a sequential verb. German candidate: ordnen (to arrange). Tier counts now 8/4/7/0.

- **SOLID atom c=adjust**: Upgraded from PLAUSIBLE to SOLID by Phase 499 (C1389). 19-test investigation across three batteries: initial cross-token battery (4/12), compound decomposition (2/4), tiebreakers (2/3) = 8/19 total. Initial battery confirmed category identity (MONITORING 12.237x #1, MARKING 2.916x, anti-THERMAL 0.055x) and 100% compound determinism, but cross-token structural tests failed because c operates as an intra-compound modifier. Compound decomposition battery revealed the decisive evidence: 6/6 compositional convergence — every independently glossed c-compound matches its CategoryClassifier output when decomposed through c(adjust)+X (ck→"direct heat"=OPERATION, ckh→"firm"=CONTAINMENT, ct→"control"=MONITORING, cth→"hazard"=MARKING, cph→"measure"=MONITORING, kc→"intense heat-seal"=CONTAINMENT). Additional evidence: MON+MARK injection +43.2pp (5/5 bases), order sensitivity with 100% category flips (ck=OPERATION vs kc=CONTAINMENT), h-suffix category transformation (p<0.000001), folio coverage exceeding all controls. AXM 93.5% (most confined atom), ACTOR timing 31.6%, CHSH+c MONITORING 23.09x. German candidate: justieren. Tier counts now 8/5/6/0.

- **SOLID atom p=pause**: Upgraded from PLAUSIBLE to SOLID by Phase 500 (C1390). 12-test investigation scored 10/12 (Cycle 1: 4/4, Cycle 2: 3/4, Cycle 3: 3/4). p is the #1 MARKING atom in the system (12.033x enrichment, 93.63% of all p-initial tokens classify as MARKING) and the #1 carryover atom (8.126x consecutive pair enrichment, ZERO cross-line pairs). Compositional convergence: 3/4 gloss-to-category matches (op=TRANSITION, cph=MONITORING, cp=MARKING; ep=MARKING miss expected THERMAL). MARKING injection +68.3pp across 4/4 testable bases (universal, strongest single-category injection of any atom). Gateway compound op: 95.5% INITIAL position (210/220), 100% TRANSITION, 63 folios. CHSH+p MON+MARK 87.4% (higher than CHSH+c). AXM 88.7% (enriched main-loop, less confined than c's 93.5%). ACTOR timing 26.7% (proactive). Two failures minor: cp/pc both MARKING (p too dominant for order sensitivity), section gradient best tracker is FLOW (+0.714) not MARKING (+0.657). German candidate: pausieren. Tier counts now 8/6/5/0.

- **PLAUSIBLE atom s=sequence**: Investigated in Phase 501 (C1391, standard battery 6/12) and Phase 503 (modifier battery 5/8), combined 11/20. s is the #1 STAGING atom (87.50%, 6.721x enrichment) with perfect compound determinism (6/6 at 100% purity). Phase 503 modifier battery proved s is a PREDICTABLE base-dependent modifier: SM-8 showed cosine 0.966 stability across independent corpus halves (all 5 compounds >= 0.925). s systematically shifts partner category (4/5 Xs compounds, SM-2), amplifies PREFIX selectivity (SM-3), changes suffix distributions (SM-4), and routes differently from ch (SM-7, chi2=211.2). h-junction not universal — tsh=FLOW, psh=MARKING override (SM-1). s remains PLAUSIBLE — strong modifier characterization but 11/20 combined score below SOLID threshold. German candidate: sequenzieren. Tier counts unchanged 8/6/5/0.

- **PLAUSIBLE atom f=flag**: Investigated in Phase 502 (C1392). 12-test investigation scored 6/12 (6 PASS, 4 FAIL, 1 INCONCLUSIVE, 1 N/A). f is the #2 MARKING atom (12.009x enrichment, behind only p at 12.033x) with the strongest compound uniformity of any atom — 90.9% of all f-compounds are MARKING. KEY STRUCTURAL FINDING: f-initial vocabulary is 100% HT/UN and NEVER enters the 49-class execution grammar, making f the purest identification/annotation atom in the system. f->c junction 10.28x (fch compound unit), CHSH+f 82.8% MARKING, 5/5 compositional convergence, H1 "flag" wins 4/4 discriminants. Failures are data-driven (215 tokens, sparse compounds, no testable reversed forms) not structural. f remains PLAUSIBLE due to data sparsity ceiling. German candidate: Flagge/Fahne. Tier counts unchanged 8/6/5/0.

- **Phase 504 (C1393): Composition Grammar.** All 18 atoms classified into four functional roles within compound MIDDLEs (V=0.593): HEAD (a, e, o — always first, set domain), MODIFIER (p, c, i, f, d, s — always middle, shape action), TERMINAL (l, r, h, y, m, n — always last, carry state), FREE (k, t — positionally mobile, role-dual). HEAD atom predicts compound category at 74–76%. k and t reverse role by PREFIX channel: actor under qo, target under ch/sh. Independently replicates C1209 (15/19 match). This establishes a composition reading rule: [HEAD=domain] + [MODIFIER=how] + [TERMINAL=resulting state], with PREFIX as channel context.

Dictionary synchronized: 5 atom glosses corrected from FL-stage markers (C777) to GLOSSING.md expert-validated values: i(early→iterate), l(late→frame), o(near→work), r(mid→input), s(break→sequence). Both readings coexist — FL positional data is structural observation, operational gloss is interpretive.

## Falsification

Would be falsified if new compound glosses systematically contradict LOCKED atom glosses (e.g., if k-compounds consistently mean something unrelated to heat).

## Provenance

- `phases/ATOM_GLOSS_AUDIT/scripts/spotcheck_report.py` — atom-by-atom compound analysis
- `phases/ATOM_GLOSS_AUDIT/scripts/generate_autogloss.py` — confidence tier assignments
- `phases/ATOM_GLOSS_AUDIT/results/spotcheck_report.txt` — full spot-check report
- `phases/ATOM_GLOSS_AUDIT/results/autogloss_summary.json` — tier distribution
