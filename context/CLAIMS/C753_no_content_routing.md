# C753: No Content-Specific A-B Routing

**Status:** VALIDATED | **Tier:** 2 | **Phase:** AZC_REASSESSMENT | **Scope:** A<>B

## Finding

A folio content does not predict which B folios it serves. After controlling for pool size, A-B Jaccard similarity has near-zero correlation with coverage (partial r = -0.038). The "routing" detected in C734-C739 is entirely driven by pool size effects, not content specificity.

### Evidence

| Test | Result | Interpretation |
|------|--------|----------------|
| T1: Size-controlled specificity | partial r = -0.038 | No content signal |
| T2: Rare vocabulary fidelity | rho = +0.69 | Common MIDDLEs spread to both A and B |
| T3: Material class alignment | Cramer's V = 0.12 | Weak section alignment |
| T5: Operating unit discovery | max disc = 1.12 | No granularity achieves discrimination |

At every granularity tested (single line to full folio), assignment remains degenerate. The top 3 units serve 72-100% of all B folios regardless of unit size.

## Implication

A folios do not "route" content to specific B programs. The vocabulary overlap between A and B reflects shared vocabulary source, not functional targeting. C384 (no token-level A-B lookup) is strongly confirmed.

**Reframe:** A→AZC→B is a **constraint propagation pipeline**, not a **content routing pipeline**. A provides vocabulary availability; AZC provides constraint gradients; B executes within those constraints.

## Constraints Affected

- C734-C739: Remain valid as descriptions of coverage architecture, but "routing" language should be interpreted as "constraint propagation"
- C384: Strongly confirmed — no addressable A→B mapping exists
- C502: Remains valid — filtering is real, but operates via vocabulary restriction, not content targeting

## Provenance

- Phase: AZC_REASSESSMENT
- Scripts: t1_size_controlled_specificity.py, t2_rare_vocabulary_fidelity.py, t3_material_class_alignment.py, t5_operating_unit_discovery.py
