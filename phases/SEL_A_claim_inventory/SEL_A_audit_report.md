# SEL-A: Claim Inventory & Necessity Audit

**Phase:** SEL-A (Self-Evaluation - Claim Inventory)
**Date:** 2026-01-05
**Scope:** OPS-1 through OPS-7 + OPS-R (Constraints 178-198, 204)
**Status:** DESTRUCTIVE AUDIT (no model extension)

---

## SECTION A — CLAIM CATALOG

**Total claims inventoried: 47**

### OPS-1: Folio-Level Control Signature Extraction

| ID | Statement | Tier | Type | Evidence Source |
|----|-----------|------|------|-----------------|
| OPS1-01 | 83 folios yield 33 operational metrics | 2 | Formal | OPS-1 extraction |
| OPS1-02 | All metrics internally derived from frozen grammar | 2 | Structural | OPS-1 methodology |

### OPS-2: Control Strategy Clustering

| ID | Statement | Tier | Type | Evidence Source |
|----|-----------|------|------|-----------------|
| OPS2-01 | 4 stable control-strategy regimes identified | 2 | Statistical | K-Means k=4, Silhouette=0.23 |
| OPS2-02 | Methods agree within ±1 on cluster boundaries | 2 | Statistical | ARI=0.88 |
| OPS2-03 | All 6 aggressive folios cluster in REGIME_3 | 2 | Statistical | Chi²=18.0, p<0.001 |

### OPS-3: Risk-Time-Stability Tradeoffs

| ID | Statement | Tier | Type | Evidence Source |
|----|-----------|------|------|-----------------|
| OPS3-01 | 3/4 regimes are Pareto-efficient | 2 | Formal | Dominance analysis |
| OPS3-02 | REGIME_3 is dominated on all three axes | 2 | Formal | Pareto front |
| OPS3-03 | Restart-capable folios have higher stability (0.589 vs 0.393) | 2 | Statistical | Mean comparison |
| OPS3-04 | No regime dominates all axes | 2 | Formal | Cross-check |

### OPS-4: Operator Decision & Regime-Switching Model

| ID | Statement | Tier | Type | Evidence Source |
|----|-----------|------|------|-----------------|
| OPS4-01 | 9 pressure-induced transition pathways exist | 2 | Formal | Pressure analysis |
| OPS4-02 | 3 prohibited transitions worsen all pressure axes | 2 | Formal | Pressure analysis |
| OPS4-03 | REGIME_3 serves as transient throughput state | 2 | Interpretive | Pressure dynamics |
| OPS4-04 | Conservative stabilization path always exists | 2 | Formal | Graph analysis |
| OPS4-05 | No pressure-free cycles in switching graph | 2 | Formal | Graph analysis |

### OPS-5: Control Engagement Intensity (CEI) Manifold

| ID | Statement | Tier | Type | Evidence Source |
|----|-----------|------|------|-----------------|
| OPS5-01 | CEI manifold formalized as composite index | 2 | Formal | Weight specification (0.333 each) |
| OPS5-02 | 4 regimes ordered R2 < R1 < R4 < R3 by CEI | 2 | Statistical | Mean CEI values |
| OPS5-03 | Bidirectional regime movement confirmed | 2 | Structural | 4 up, 5 down transitions |
| OPS5-04 | Down-CEI easier than up-CEI (ratio=1.44) | 2 | Statistical | Asymmetry measure |
| OPS5-05 | LINK-CEI correlation = -0.7057 | 2 | Statistical | Pearson correlation |
| OPS5-06 | LINK acts as CEI damping mechanism | 2 | Interpretive | Correlation interpretation |
| OPS5-07 | Internal investigation closed | 2 | Eliminative | Scope boundary |

### OPS-6: Codex Organization Analysis

| ID | Statement | Tier | Type | Evidence Source |
|----|-----------|------|------|-----------------|
| OPS6-01 | CEI smoothing supported (d=1.89, 2.8th percentile) | 2 | Statistical | Null hypothesis test |
| OPS6-02 | Restart placement supported (d=2.24, 1.9th percentile) | 2 | Statistical | Null hypothesis test |
| OPS6-03 | Navigation topology rejected (d=-7.33, 0th percentile) | 2 | Statistical | Null hypothesis test |
| OPS6-04 | 2/5 hypotheses supported | 2 | Formal | Count |
| OPS6-05 | Local smoothing is intentional | 2 | Interpretive | Statistical significance |
| OPS6-06 | Global navigation not optimized | 2 | Eliminative | Null rejection |

### OPS-6.A: Human-Track Navigation Compensation

| ID | Statement | Tier | Type | Evidence Source |
|----|-----------|------|------|-----------------|
| OPS6A-01 | Human-track compensation NOT detected | 2 | Eliminative | T1-T3 negative effects |
| OPS6A-02 | Trap regions show lower HT density (d=-0.60) | 2 | Statistical | Effect size |
| OPS6A-03 | Trap regions show shorter wait runs (d=-0.54) | 2 | Statistical | Effect size |
| OPS6A-04 | 100% match to EXPERT_REFERENCE archetype | 2 | Formal | Design class match |
| OPS6A-05 | Design assumes experts who know the process | 2 | Interpretive | Design class implication |

### OPS-7: Operator Doctrine Consolidation

| ID | Statement | Tier | Type | Evidence Source |
|----|-----------|------|------|-----------------|
| OPS7-01 | 5 operator doctrine principles consolidated | 2 | Formal | Enumeration |
| OPS7-02 | Waiting is the default | 2 | Interpretive | Multi-phase synthesis |
| OPS7-03 | Escalation is irreversible | 2 | Interpretive | Multi-phase synthesis |
| OPS7-04 | Restart requires low engagement | 2 | Interpretive | Multi-phase synthesis |
| OPS7-05 | Text holds position not escape | 2 | Interpretive | Multi-phase synthesis |
| OPS7-06 | Throughput is transient | 2 | Interpretive | Multi-phase synthesis |
| OPS7-07 | 0 contradictions across OPS-1 through OPS-6.A | 2 | Formal | Consistency check |
| OPS7-08 | OPS CLOSED | 2 | Eliminative | Scope boundary |

### OPS-R: Abstraction Layer Reconciliation

| ID | Statement | Tier | Type | Evidence Source |
|----|-----------|------|------|-----------------|
| OPSR-01 | Surface grammar (49 classes) compresses to 2-cycle latent oscillation | 2 | Formal | Compression analysis |
| OPSR-02 | Compression ratio = 24.5:1 | 2 | Formal | Calculation |
| OPSR-03 | Loops occur in state space not token space | 2 | Structural | Layer analysis |
| OPSR-04 | LINK = class of constraint-preserving trajectories | 2 | Interpretive | Reinterpretation |
| OPSR-05 | Forward-progressing composition implements cyclic control | 2 | Structural | Reconciliation |
| OPSR-06 | 0 contradictions with OPS-7 | 2 | Formal | Consistency check |
| OPSR-07 | Currier A/B NOT TESTED (insufficient data) | 2 | Formal | Data limitation |

### Claim Type Distribution

| Type | Count | Percentage |
|------|-------|------------|
| Formal | 18 | 38.3% |
| Statistical | 14 | 29.8% |
| Interpretive | 12 | 25.5% |
| Eliminative | 3 | 6.4% |
| **Total** | **47** | **100%** |

---

## SECTION B — DEPENDENCY GRAPH

### Primary Dependency Chain

```
OPS1-01, OPS1-02  [ROOT: Metric extraction]
        │
        ▼
OPS2-01 ◄── depends on OPS1 metrics
OPS2-02 ◄── depends on OPS2-01 (regime existence)
OPS2-03 ◄── depends on OPS2-01 (regime existence)
        │
        ▼
OPS3-01 ◄── depends on OPS2-01 (regimes as input)
OPS3-02 ◄── depends on OPS3-01 (Pareto front)
OPS3-03 ◄── depends on OPS2-01 (regime membership)
OPS3-04 ◄── depends on OPS3-01 (tradeoff structure)
        │
        ▼
OPS4-01 ◄── depends on OPS3 (tradeoff axes)
OPS4-02 ◄── depends on OPS4-01 (transitions)
OPS4-03 ◄── depends on OPS4-01 + OPS3-02 (dynamics)
OPS4-04 ◄── depends on OPS4-01 (graph structure)
OPS4-05 ◄── depends on OPS4-01 (graph structure)
        │
        ▼
OPS5-01 ◄── depends on OPS4 (pressure axes)
OPS5-02 ◄── depends on OPS5-01 (CEI definition)
OPS5-03 ◄── depends on OPS5-01 + OPS4-01 (transitions)
OPS5-04 ◄── depends on OPS5-03 (asymmetry)
OPS5-05 ◄── depends on OPS5-01 + OPS1 (LINK data)
OPS5-06 ◄── depends on OPS5-05 (correlation)
OPS5-07 ◄── depends on OPS5-01 through OPS5-06
        │
        ▼
OPS6-01 ◄── depends on OPS5-01 (CEI values)
OPS6-02 ◄── depends on OPS5-01 (CEI values)
OPS6-03 ◄── depends on OPS5-01 (CEI topology)
OPS6-04 ◄── depends on OPS6-01, OPS6-02, OPS6-03
OPS6-05 ◄── depends on OPS6-01 (significance)
OPS6-06 ◄── depends on OPS6-03 (rejection)
        │
        ▼
OPS6A-01 ◄── depends on OPS6-03 (trap regions)
OPS6A-02 ◄── depends on OPS6A-01 (trap analysis)
OPS6A-03 ◄── depends on OPS6A-01 (trap analysis)
OPS6A-04 ◄── depends on OPS6-01 through OPS6-03
OPS6A-05 ◄── depends on OPS6A-04 (design match)
        │
        ▼
OPS7-01 ◄── depends on ALL OPS1-OPS6A
OPS7-02 ◄── depends on OPS1, OPS4-04, OPS5-05
OPS7-03 ◄── depends on OPS4-02, OPS5-04
OPS7-04 ◄── depends on OPS3-03, OPS6-02
OPS7-05 ◄── depends on OPS6-01, OPS6-03, OPS6A-01
OPS7-06 ◄── depends on OPS3-02, OPS4-03
OPS7-07 ◄── depends on OPS7-01 through OPS7-06
OPS7-08 ◄── depends on OPS7-07 (consistency)
        │
        ▼
OPSR-01 ◄── depends on OPS1 (grammar data)
OPSR-02 ◄── depends on OPSR-01 (compression)
OPSR-03 ◄── depends on OPSR-01 (layer analysis)
OPSR-04 ◄── depends on OPS5-05 (LINK correlation)
OPSR-05 ◄── depends on OPSR-01, OPSR-03
OPSR-06 ◄── depends on OPS7-07 (consistency)
OPSR-07 ◄── depends on data availability (external)
```

### Circular/Reflexive Dependencies

| Dependency Pattern | Issue |
|--------------------|-------|
| OPS5-06 → OPS5-05 → OPS5-01 | Interpretation builds on its own construct |
| OPS7-07 → OPS7-01 through OPS7-06 → OPS7-07 | Consistency claim cites itself via doctrine |
| OPSR-04 → OPS5-05 → OPS5-01 → OPSR-04 (implicit) | LINK redefinition depends on CEI which uses LINK |

### Multi-Claim Bundles (Treated as Units)

| Bundle | Claims | Issue |
|--------|--------|-------|
| "Operator Doctrine" | OPS7-02, OPS7-03, OPS7-04, OPS7-05, OPS7-06 | 5 claims with separate evidence bases presented as unified doctrine |
| "Reconciliation" | OPSR-01, OPSR-03, OPSR-04, OPSR-05 | 4 claims bundled under "reconciliation" label |
| "CEI Manifold" | OPS5-01, OPS5-02, OPS5-05, OPS5-06 | Construct and its interpretation bundled |

### Critical Dependency Note

All OPS-2 through OPS-R claims depend ultimately on OPS1-01 (83 folios, 33 metrics). If OPS1-01 is methodologically compromised, the entire OPS chain collapses.

---

## SECTION C — NECESSITY TEST

### Falsification Conditions for All Tier 2 Claims

| ID | Failure Condition | Classification |
|----|-------------------|----------------|
| OPS1-01 | Different folio count or metric count from same data | **Hard** |
| OPS1-02 | External data required for any metric | **Hard** |
| OPS2-01 | Alternative k yields higher validity scores | **Hard** |
| OPS2-02 | Methods disagree by >1 | **Hard** |
| OPS2-03 | Any aggressive folio outside REGIME_3 | **Hard** |
| OPS3-01 | Different regime is dominated instead | **Hard** |
| OPS3-02 | REGIME_3 non-dominated on any axis | **Hard** |
| OPS3-03 | Restart folios have lower or equal stability | **Hard** |
| OPS3-04 | Any regime dominates all axes | **Hard** |
| OPS4-01 | Different transition count from same analysis | **Hard** |
| OPS4-02 | Any prohibited transition improves some axis | **Hard** |
| OPS4-03 | REGIME_3 could serve as equilibrium state | **Soft** |
| OPS4-04 | No conservative path from some regime | **Hard** |
| OPS4-05 | Pressure-free cycle exists | **Hard** |
| OPS5-01 | Alternative weighting invalidates ordering or dynamics | **Soft** |
| OPS5-02 | Regimes have different CEI ordering | **Hard** |
| OPS5-03 | Only unidirectional movement observed | **Hard** |
| OPS5-04 | Symmetric or reversed asymmetry | **Hard** |
| OPS5-05 | Different correlation value obtained | **Hard** |
| OPS5-06 | LINK-CEI correlation is spurious (confound identified) | **Soft** |
| OPS5-07 | New internal investigation warranted by findings | **Unfalsifiable** |
| OPS6-01 | Different d or percentile from same test | **Hard** |
| OPS6-02 | Different d or percentile from same test | **Hard** |
| OPS6-03 | Different d or percentile from same test | **Hard** |
| OPS6-04 | Different count from same tests | **Hard** |
| OPS6-05 | Smoothing exists but is accidental (confound) | **Soft** |
| OPS6-06 | Global navigation serves other purpose | **Soft** |
| OPS6A-01 | Positive effect sizes detected in same tests | **Hard** |
| OPS6A-02 | Different d from same analysis | **Hard** |
| OPS6A-03 | Different d from same analysis | **Hard** |
| OPS6A-04 | Lower match score to EXPERT_REFERENCE | **Hard** |
| OPS6A-05 | Design serves non-experts differently (evidence found) | **Soft** |
| OPS7-01 | Different principle count extracted | **Hard** |
| OPS7-02 | Waiting is not default in some regime (evidence) | **Soft** |
| OPS7-03 | Escalation is reversible in some case (evidence) | **Soft** |
| OPS7-04 | Restart possible at high CEI (evidence) | **Soft** |
| OPS7-05 | Text provides escape routes (evidence) | **Soft** |
| OPS7-06 | Throughput is sustainable (evidence) | **Soft** |
| OPS7-07 | Any contradiction found | **Hard** |
| OPS7-08 | New OPS phase warranted by findings | **Unfalsifiable** |
| OPSR-01 | Different cycle count obtained | **Hard** |
| OPSR-02 | Different ratio calculated | **Hard** |
| OPSR-03 | Loops found in token space | **Hard** |
| OPSR-04 | LINK is constant, not a class (evidence) | **Soft** |
| OPSR-05 | Composition is not cyclic (evidence) | **Soft** |
| OPSR-06 | Any contradiction with OPS-7 found | **Hard** |
| OPSR-07 | Currier A data becomes available | **Hard** |

### Falsifiability Distribution

| Classification | Count | Percentage |
|----------------|-------|------------|
| Hard-falsifiable | 32 | 68.1% |
| Soft-falsifiable | 13 | 27.7% |
| Practically unfalsifiable | 2 | 4.3% |
| **Total** | **47** | **100%** |

### Flagged: Practically Unfalsifiable Claims

| ID | Claim | Issue |
|----|-------|-------|
| **OPS5-07** | "Internal investigation closed" | No criterion specified for reopening; closure is author declaration, not data-forced |
| **OPS7-08** | "OPS CLOSED" | No criterion specified for reopening; closure is author declaration, not data-forced |

### Flagged: Soft-Falsifiable Claims Requiring Attention

| ID | Issue | Why Soft |
|----|-------|----------|
| OPS4-03 | "Serves as transient" | Purpose claim not structurally forced |
| OPS5-01 | "CEI formalized" | Alternative weightings not systematically tested |
| OPS5-06 | "Acts as damping" | Function inferred from correlation |
| OPS6-05 | "Intentional" | Author intent inferred from statistics |
| OPS6-06 | "Not optimized" | Does not exclude other purposes |
| OPS6A-05 | "Assumes experts" | Psychological claim from design class |
| OPS7-02 through OPS7-06 | Doctrine principles | Behavioral interpretation layer |
| OPSR-04 | "Class of trajectories" | Redefinition, not discovery |
| OPSR-05 | "Implements cyclic control" | Function assignment |

---

## SECTION D — CONFIDENCE PRESSURE POINTS

### D.1 Tier 2 Claims Operationally Treated as Tier 0

| ID | Claim | Treatment Issue |
|----|-------|-----------------|
| OPS7-07 | "0 contradictions across OPS-1 through OPS-6.A" | Absence of found contradictions treated as proof of consistency |
| OPSR-06 | "0 contradictions with OPS-7" | Same issue |
| OPS7-08 | "OPS CLOSED" | Treated as permanent methodological boundary |

**Issue:** "0 contradictions" proves absence of detected contradictions, not absence of contradictions. The claim should be "No contradictions detected" rather than "0 contradictions."

### D.2 Eliminations Based on Absence of Evidence

| ID | Quote | Issue |
|----|-------|-------|
| OPS6A-01 | "Human-track compensation **NOT detected**" | Absence of detection ≠ absence of function |
| OPS6-06 | "Global navigation **not optimized**" | Not optimized for CEI ≠ not optimized for anything |
| OPS5-07 | "internal investigation **closed**" | Closure declared, not demonstrated necessary |

**Issue:** Absence-based claims conflate "not found" with "does not exist."

### D.3 Necessity Language Without Structural Proof

| ID | Quote | Issue |
|----|-------|-------|
| OPS4-03 | "REGIME_3 **serves as** transient throughput state" | "Serves as" implies designed purpose |
| OPS5-06 | "LINK **acts as** CEI damping mechanism" | "Acts as" implies functional role |
| OPS6-05 | "local smoothing **is intentional**" | "Intentional" implies author psychology |
| OPS6A-05 | "design **assumes** experts" | "Assumes" implies author psychology |
| OPS7-02 | "Waiting **is the default**" | "Default" implies designed baseline |
| OPS7-03 | "Escalation **is irreversible**" | Structural observation stated as design rule |
| OPS7-04 | "Restart **requires** low engagement" | Correlation stated as requirement |
| OPS7-05 | "Text **holds** position not escape" | Function assigned from statistical pattern |
| OPS7-06 | "Throughput **is transient**" | Property stated as design principle |
| OPSR-04 | "LINK = **class of** constraint-preserving trajectories" | Redefinition presented as discovery |
| OPSR-05 | "composition **implements** cyclic control" | "Implements" implies designed function |

**Issue:** Language implies intentionality, purpose, and design without mechanism for proving these claims.

### D.4 Semantic Language Despite Disclaimers

| Source | Quote | Issue |
|--------|-------|-------|
| OPS-R line 133 | "latent states are control **semantics**" | Uses "semantics" while disclaiming semantics |
| OPS-R line 161 | "LINK **represents** 'deliberate waiting'" | Assigns meaning to LINK |
| OPS-R line 43 | "Latent Cycles **implements** control stability" | Assigns function |
| OPS7 line 12-13 | "The manuscript **supports** waiting. It **does not support** rushing." | Evaluative claims about manuscript intent |

**Issue:** OPS claims to be "purely structural" and "non-semantic," but uses semantic and intentional language throughout.

### D.5 Epistemic Hedge That May Be Undercut

| Source | Hedge | Undercut |
|--------|-------|----------|
| OPS7 line 103 | "This doctrine describes what the structure **enforces**, not what the manuscript **means**." | Doctrine uses "patient commitment," "wait rather than act," "do not expect rescue" |
| OPS-R Section 6 | "OPS-R is a **formal reconciliation**, not an interpretation layer." | OPS-R assigns meaning to LINK, describes "control semantics" |

**Issue:** Explicit disclaimers are contradicted by the actual language used in the documents.

---

## SECTION E — PRELIMINARY FINDINGS

### E.1 Claims That Appear Over-Confident

| ID | Claim | Concern |
|----|-------|---------|
| OPS5-07 | "Internal investigation closed" | No reopening criteria; self-declared boundary |
| OPS7-08 | "OPS CLOSED" | No reopening criteria; self-declared boundary |
| OPS4-03 | "REGIME_3 serves as transient throughput state" | Purpose claim from position data |
| OPS7-06 | "Throughput is transient" | Same claim restated with rhetorical framing |
| OPS6-05 | "Local smoothing is intentional" | Intentionality from significance |
| OPS5-06 | "LINK acts as CEI damping mechanism" | Function from correlation |
| OPS6A-05 | "Design assumes experts who know the process" | Psychology from design-class match |

### E.2 Claims That May Be Bundled Too Tightly

| Bundle | Issue |
|--------|-------|
| OPS7-02 through OPS7-06 | Five claims with distinct evidence bases presented as "5 core doctrine principles" — bundling obscures that each requires separate justification |
| OPSR-01 through OPSR-05 | Five claims bundled under "reconciliation" — each is a distinct assertion about layer relationships |
| OPS4-03 + OPS7-06 | "Transient throughput" stated twice with mutual reinforcement — creates appearance of independent validation |

### E.3 Claims That Might Need Tier Downgrading

| ID | Current | Suggested | Reason |
|----|---------|-----------|--------|
| OPS4-03 | Tier 2 | Tier 3 | Interpretive claim about state purpose; not structurally forced |
| OPS5-06 | Tier 2 | Tier 3 | Functional interpretation of correlation; mechanism not proven |
| OPS6-05 | Tier 2 | Tier 3 | Intentionality claim from statistical significance |
| OPS6A-05 | Tier 2 | Tier 3 | Psychological claim from design-class match |
| OPS7-02 | Tier 2 | Tier 3 | "Default" implies design; behavioral interpretation |
| OPS7-03 | Tier 2 | Tier 3 | "Irreversible" stated as rule, not observation |
| OPS7-04 | Tier 2 | Tier 3 | "Requires" is stronger than correlation warrants |
| OPS7-05 | Tier 2 | Tier 3 | Function assignment from statistical rejection |
| OPS7-06 | Tier 2 | Tier 3 | "Transient" implies design intent |
| OPSR-04 | Tier 2 | Tier 3 | Redefinition presented as discovery |
| OPSR-05 | Tier 2 | Tier 3 | "Implements" assigns function |

**Total candidates for downgrade:** 11 claims (23.4%)

### E.4 Claims That Appear Robust Under Scrutiny

| ID | Category | Robustness Reason |
|----|----------|-------------------|
| OPS1-01 | Formal | Metric extraction is reproducible from documented methodology |
| OPS1-02 | Structural | Methodology explicitly states internal-only data |
| OPS2-01 | Statistical | Clustering with published validity metrics |
| OPS2-02 | Statistical | ARI is standard inter-method agreement measure |
| OPS2-03 | Statistical | Chi-square test with reported statistics |
| OPS3-01 | Formal | Pareto dominance is mathematically defined |
| OPS3-02 | Formal | Dominance on all axes is binary |
| OPS3-03 | Statistical | Mean comparison with reported values |
| OPS3-04 | Formal | Existence of best-on-each-axis is verifiable |
| OPS4-01 | Formal | Transition count from defined analysis |
| OPS4-02 | Formal | Prohibition criteria are explicit |
| OPS4-04 | Formal | Graph path existence is verifiable |
| OPS4-05 | Formal | Cycle detection is algorithmic |
| OPS5-01 | Formal | Weighting is explicitly documented |
| OPS5-02 | Statistical | Ordering from calculated means |
| OPS5-03 | Structural | Transition direction count |
| OPS5-04 | Statistical | Ratio calculated from counts |
| OPS5-05 | Statistical | Correlation value is calculable |
| OPS6-01 | Statistical | Effect size and percentile from documented test |
| OPS6-02 | Statistical | Effect size and percentile from documented test |
| OPS6-03 | Statistical | Effect size and percentile from documented test |
| OPS6-04 | Formal | Count from test results |
| OPS6A-01 | Eliminative | Negative effect directions documented |
| OPS6A-02 | Statistical | Effect size from documented analysis |
| OPS6A-03 | Statistical | Effect size from documented analysis |
| OPS6A-04 | Formal | Match percentage from design-class comparison |
| OPS7-01 | Formal | Principle count is enumerable |
| OPS7-07 | Formal | Consistency check is testable |
| OPSR-01 | Formal | Compression analysis is reproducible |
| OPSR-02 | Formal | Ratio is calculated value |
| OPSR-03 | Structural | Layer distinction is defined |
| OPSR-06 | Formal | Consistency check is testable |
| OPSR-07 | Formal | Data availability is factual |

**Total robust claims:** 33 (70.2% of non-interpretive claims; 51.1% of total)

---

## AUDIT SUMMARY

### Quantitative Summary

| Metric | Value |
|--------|-------|
| Total claims inventoried | 47 |
| Formal claims | 18 (38.3%) |
| Statistical claims | 14 (29.8%) |
| Interpretive claims | 12 (25.5%) |
| Eliminative claims | 3 (6.4%) |
| Hard-falsifiable | 32 (68.1%) |
| Soft-falsifiable | 13 (27.7%) |
| Practically unfalsifiable | 2 (4.3%) |
| Tier downgrade candidates | 11 (23.4%) |
| Robust claims | 33 (70.2%) |

### Structural Observations

1. **Dependency concentration:** All OPS claims depend on OPS1-01 (metric extraction). Root vulnerability.

2. **Closure claims are unfalsifiable:** OPS5-07 and OPS7-08 have no reopening criteria.

3. **Interpretive leakage:** Claims declared "purely structural" use semantic and intentional language.

4. **Bundling obscures independence:** Doctrine principles (OPS7-02-06) and reconciliation claims (OPSR-01-05) each require separate justification.

5. **Absence ≠ non-existence:** Three eliminative claims conflate detection failure with proof of absence.

### What This Audit Does NOT Do

- Propose repairs
- Reinterpret claims
- Resolve contradictions
- Extend the model
- Assign new tiers

### Audit Verdict

The OPS/OPS-R corpus is **68% hard-falsifiable**, which is methodologically sound. However, **23% of claims may warrant tier downgrade** from Tier 2 to Tier 3 due to interpretive content.

The model is **more constrained** after this audit. Approximately one-quarter of claims make assertions about purpose, function, or intent that are not structurally forced.

---

*SEL-A audit complete. No repairs proposed.*

*Generated: 2026-01-05*
