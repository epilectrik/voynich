# C1201: PREFIX-Mediated Energy State Routing

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** ENERGY_MODE_TRANSITION (Phase 426)
**Extends:** C929 (ch/sh sensory modality), C1200 (k/e state carryover)
**Relates to:** C1154 (h-kernel domain dependence), C931 (prefix positional phase mapping)

---

## Statement

PREFIX ch/sh actively routes energy state transitions between k-dominant and e-dominant modes. At k->e mode switches, the predecessor's ch:sh ratio is 1.76:1 (Fisher p=0.008), versus 1:1 at k->k continuations. The target token's PREFIX is strongly non-random at mode switches (chi2=104.2): sh (2.06x) and lsh (3.17x) are enriched at switches; qo (0.69x) and ol (0.57x) are enriched at continuations.

| Measure | Value |
|---------|-------|
| Predecessor ch:sh at k->e transition | 130:74 (1.76:1) |
| Predecessor ch:sh at k->k continuation | 62:63 (0.98:1) |
| Fisher exact p (ch vs sh, transition vs continuation) | 0.008 |
| Target PREFIX chi-squared (switch vs continue) | 104.2 |
| sh enrichment at mode switches | 2.06x |
| lsh enrichment at mode switches | 3.17x |
| ch enrichment at mode switches | 1.54x |
| qo enrichment at continuations | 0.69x |
| ol enrichment at continuations | 0.57x |
| Total mode switches (k->e or e->k) | 1,310 |
| Total mode continuations (k->k or e->e) | 904 |

---

## Interpretation

C929 established that ch = active state testing and sh = passive process monitoring. C1201 shows these sensory modalities don't just *describe* operations -- they **route** the energy state machine. When a ch-prefixed token (active test) precedes a mode switch, it functions as a conditional gate: "test the state, then switch energy mode." The enrichment of sh/lsh at the TARGET of switches means the system preferentially transitions into monitoring mode after switching states.

This connects the PREFIX sensory system (C929) to the MIDDLE energy state system (C1200) mechanistically. The PREFIX layer serves as the control interface for state transitions that the MIDDLE layer encodes.

PREFIX routing is asymmetric:
- **Switch-routing prefixes**: sh, lsh, ch (sensory/monitoring family)
- **Continuation-routing prefixes**: qo, ol, lch (operational family)

---

## Method

- 23,096 Currier B tokens across 2,420 lines
- For each adjacent pair A-B: classify by A's terminal character and B's initial character (k or e)
- T2: Record A's ch/sh prefix at transitions (k->e) vs continuations (k->k). Fisher exact test on 2x2 table.
- T3: Record B's PREFIX at mode switches (k->e or e->k) vs continuations (k->k or e->e). Compute enrichment ratios and chi-squared.

**Script:** `phases/ENERGY_MODE_TRANSITION/scripts/h_kernel_transition_test.py`
**Results:** `phases/ENERGY_MODE_TRANSITION/results/h_kernel_transition_results.json`
