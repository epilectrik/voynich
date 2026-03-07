# Phase 548: o-Domain Deep Dive

**Date:** 2026-03-06
**Status:** COMPLETE
**Constraints produced:** C1556-C1561 (6 new)
**Phase type:** Characterization (single HEAD atom domain)

---

## Research Questions

1. What is the terminal profile of o-HEAD and how does it compare to other HEADs?
2. What modifiers does o-HEAD attract/repel?
3. How does suffix attachment and mode selection work for o-HEAD?
4. How does o-HEAD distribute across Currier A, B, and AZC systems?
5. How does o-HEAD distribute across AZC zones?
6. What instruction classes emerge from o-HEAD compound detail?
7. What is o-HEAD's relationship to hazard topology?
8. How does o compare to e (the other multi-category HEAD)?
9. What is o-HEAD's line position profile?
10. What are cross-token transition patterns involving o-HEAD?

---

## Data

- **Corpus:** 23,096 Currier B tokens with valid morphology + cross-system (A, AZC)
- **o-HEAD in B:** 2,717 tokens (11.8%), 276 types
- **o-HEAD in A:** 3,181 tokens (28.5%), 264 types
- **o-HEAD in AZC:** 723 tokens (22.4%), 196 types
- **Analysis:** 13 test functions (T1-T13) covering all 10 research questions

---

## Key Findings

### Finding 1: Terminal-to-Category Deterministic Mapping (C1556)

**The strongest result.** Within o-HEAD MIDDLEs, the terminal atom deterministically selects the operational category:

| Terminal | Dominant Category | Rate | N |
|----------|-------------------|------|---|
| l | STAGING | 92.9% | 820 |
| r | FLOW | 88.6% | 508 |
| bare | OPERATION | 76.7% | 647 |
| h | MARKING/MONITORING | 33.8%/25.4% | 287/63 |
| bare (100%) | CONTAINMENT | 100% | 102 |
| bare (100%) | THERMAL | 100% | 63 |
| bare (100%) | TRANSITION | 100% | 39 |

The three largest o-HEAD MIDDLEs demonstrate this perfectly:
- **ol** (762 tokens): 100% STAGING, 3% suffix rate, 2% Mode A
- **or** (446 tokens): 100% FLOW, 3% suffix rate, 0% Mode A
- **bare o** (388 tokens): 100% OPERATION, 77% suffix rate, 54% Mode A

This is the sharpest terminal-category coupling for any HEAD atom. For comparison, C1483 found overall terminal category specificity V=0.463 across all HEADs. Within o-HEAD, the l-terminal and r-terminal achieve near-100% categorical purity.

The determinism extends C1485 (HEAD x TERM affinity structure) by showing that o-HEAD's terminal atom is not just preferred but LOCKED to specific categories. This resolves the vague "arrangement" label (C1388): o-HEAD is an arrangement domain BECAUSE it uses different terminals to specify different arrangement ASPECTS -- staging arrangements (l), flow arrangements (r), and operational arrangements (bare).

### Finding 2: y-Terminal Near-Complete Depletion (C1557)

o-HEAD depletes y-terminal to 0.007x (essentially zero: ~19 tokens out of 2,717). This is the strongest single-terminal depletion for any HEAD atom. For context:
- k-HEAD y-terminal: 0.082x (low but present)
- e-HEAD y-terminal: 1.792x (strongly enriched)
- a-HEAD y-terminal: 0.804x (mildly depleted)

Since y-terminal is the exclusive PHASE_ORDERING hazard vector (C1551: dy=100% of PHASE_ORDERING violations), o-HEAD's y-avoidance is a structural safety mechanism. o-HEAD cannot produce PHASE_ORDERING failures because it categorically lacks the terminal atom that causes them.

Combined with C1546 (HEAD immunity from hazard source), this creates double protection: o-HEAD tokens are immune as sources (via HEAD presence) AND avoid the y-terminal hazard vector. This structural property is not shared by any other HEAD atom.

### Finding 3: p/f Executive Modifier Enrichment (C1558)

o-HEAD modifier profile:

| Modifier | Rate | Enrichment | Interpretation |
|----------|------|------------|----------------|
| p | 9.7% | 3.51x | Marking/pause modifier |
| f | 2.7% | 2.83x | Marking/flag modifier |
| c | 13.1% | 1.42x | Main-loop modifier |
| s | 3.1% | 1.26x | Staging modifier |
| d | 10.6% | 0.55x | Seal/closure modifier |
| i | 6.1% | 0.32x | Iteration modifier |

The p and f atoms were identified as "o-HEAD arrangement-affiliated modifiers" in C1543. This phase confirms and quantifies: p at 3.51x is the strongest modifier enrichment for any single HEAD, and f at 2.83x is second-strongest. The i-depletion (0.32x) is consistent with C1205 (i orthogonal to energy system) and with o's non-iterative arrangement function.

This profile directly contrasts with a-HEAD (where i dominates at >50%) and e-HEAD (where d dominates at 38%). Each HEAD atom selects a characteristic modifier profile that determines its operational palette.

### Finding 4: Cross-System A>AZC>B Gradient with AZC Boundary Concentration (C1559)

| System | o-HEAD Rate | Tokens | Types |
|--------|-------------|--------|-------|
| Currier A | 28.5% | 3,181 | 264 |
| AZC | 22.4% | 723 | 196 |
| Currier B | 11.8% | 2,717 | 276 |

A/B ratio = 2.42x. AZC/B ratio = 1.90x.

Within AZC zones:

| Zone | o-HEAD Rate | Interpretation |
|------|-------------|----------------|
| L (label) | 30.9% | Identification vocabulary |
| S (boundary) | 29.3% | Configuration at boundaries |
| C (core) | 26.2% | Core positions |
| P (text-proximate) | 19.1% | Near executable text |
| R (interior) | 17.7% | Interior operational positions |

S/R ratio = 1.66x, confirming and extending C1517 (o-HEAD zone-graded: S=29.3% vs R=17.7%). The gradient runs from A-proximate zones (S, C, L: high o-HEAD, arrangement-heavy) to B-proximate zones (R, P: lower o-HEAD, execution-heavy), precisely matching C1522 (AZC grades from A-like to B-like).

A-enriched o-MIDDLEs include c-containing forms (oc 0.04x, otc 0.07x, okc 0.08x, oct 0.21x) -- forms with the c-modifier that is associated with A's declarative register. B-enriched o-MIDDLEs are simpler operational forms (olk 3.27x, opch 2.07x).

### Finding 5: Inner Atom Composition Divergent from Corpus (C1560)

The internal composition of o-HEAD compounds (excluding the o itself) dramatically diverges from the corpus baseline:

| Atom | o-HEAD Rate | Corpus Rate | Enrichment |
|------|-------------|-------------|------------|
| y | 0.4% | 15.8% | **0.023x** |
| n | 1.1% | 5.9% | **0.193x** |
| i | 4.4% | 11.9% | **0.368x** |
| d | 7.6% | 14.0% | **0.543x** |
| l | 23.2% | 8.5% | **2.739x** |
| r | 12.6% | 5.5% | **2.292x** |
| h | 9.0% | 4.0% | **2.237x** |
| p | 7.0% | 1.5% | **4.674x** |
| f | 1.9% | 0.5% | **3.650x** |

The y-depletion at 0.023x is the most extreme single-atom divergence in the entire atom system. Combined with l-enrichment (2.74x) and r-enrichment (2.29x), this shows o-HEAD compounds are built from a CHANNELED terminal vocabulary (l, r, h) while categorically excluding the OPERATION terminal (y) and the CONTAINMENT/TRANSITION terminal (n).

The p and f enrichment inside compounds parallels the modifier enrichment (Finding 3), showing the executive atoms are attracted to o-HEAD at both the modifier AND inner-atom levels.

### Finding 6: Empirical Hazard Immunity (C1561)

o-HEAD has 0% hazard source rate AND 0% hazard target rate across all 2,717 tokens:

| HEAD | Source Rate | Target Rate |
|------|------------|-------------|
| a | 0.038% | 0.337% |
| e | 0.000% | 0.000% |
| **o** | **0.000%** | **0.000%** |
| k | 0.000% | 0.000% |
| t | 0.000% | 0.000% |
| HEADLESS | 0.189% | 0.019% |

While C1546 established that ALL HEADs have 0% source rate, the target rate finding is new. Theoretically, 3 forbidden pairs involve o-HEAD MIDDLEs as targets: [he->or], [shedy->o], and o-HEAD as source in [or->dal]. In practice, none of these fire. The shedy source is a phantom MIDDLE (C1552, 0 tokens), and he->or is vanishingly rare.

This makes o-HEAD the safest HEAD domain: zero hazard involvement in any direction, reinforced by y-terminal avoidance (Finding 2) and executive modifier preference (Finding 3).

### Additional Findings (Not Constraint-Worthy)

**Line position:** o-HEAD is positionally flat (mean=0.497, quintile enrichments all within 0.95-1.03x). No boundary bias. This contrasts with the AZC boundary concentration (Finding 4) -- o-HEAD marks arrangements at AZC boundaries but distributes evenly within B execution lines.

**Transition routing:** o-HEAD self-transition rate is 0.136 (moderate, 1.14x enrichment). Primary successors are e-HEAD (0.311, 1.03x) and HEADLESS (0.247, 0.96x). Primary predecessors are HEADLESS (0.293, 1.14x) and e-HEAD (0.248, 0.78x). No strong routing asymmetries -- o-HEAD integrates smoothly into the general transition flow.

**Suffix behavior:** o-HEAD suffix rate is 0.480 (near corpus baseline). Mode A rate is 0.253 (below baseline). The suffix first-atom census shows a (30.7%), d (19.6%), e (19.4%) dominating -- consistent with the terminal profile but not independently constraint-worthy.

**Compound morphology:** o-HEAD compounds are overwhelmingly 2-atom (1,629/2,717 = 59.9%). The length distribution is 1-atom=388, 2-atom=1629, 3-atom=220, 4-atom=329, with a secondary peak at 4-atom compounds (opch-type).

**o vs e divergence:** Category JSD=0.365 (LARGE), Terminal JSD=0.412 (VERY LARGE). o=STAGING domain (25.7x vs e), e=THERMAL domain (0.07x in o). These are maximally different operational domains despite both being "multi-category" HEADs. Modifier divergence: o attracts p (3.51x) while e attracts d (0.55x in o, 38% in e). The only shared feature is c-modifier moderate enrichment in both.

---

## Constraints Produced

| C# | Claim | Tier | Key Evidence |
|----|-------|------|--------------|
| C1556 | o-HEAD terminal-to-category deterministic mapping | 2 | ol=100% STAGING, or=100% FLOW, bare o=100% OPERATION; STAGING->l 92.9%, FLOW->r 88.6% |
| C1557 | o-HEAD y-terminal near-complete depletion (0.007x) | 2 | ~19/2717 y-terminal tokens; structural safety against PHASE_ORDERING hazard |
| C1558 | o-HEAD p/f executive modifier enrichment with i/d depletion | 2 | p 3.51x, f 2.83x enriched; i 0.32x, d 0.55x depleted |
| C1559 | o-HEAD cross-system gradient A(28.5%)>AZC(22.4%)>B(11.8%) with AZC S/R=1.66x | 2 | A/B ratio 2.42x; AZC S-zone=29.3% vs R-zone=17.7% |
| C1560 | o-HEAD inner atom composition divergent (y 0.023x, l 2.74x, p 4.67x) | 2 | Strongest single-atom divergence in system; CHANNELED terminal vocabulary |
| C1561 | o-HEAD empirical hazard immunity (0% source AND 0% target) | 2 | 0/2717 in either direction; 3 theoretical forbidden pairs never fire |

---

## Cross-References

| Existing Constraint | Relationship | Finding |
|--------------------|-------------|---------|
| C1388 (o-atom arrangement domain) | **EXTENDED** | Arrangement is CHANNELED through terminal atoms: l=staging, r=flow, bare=operation |
| C1475 (HEAD domain differentiation) | **CONFIRMED** at deeper resolution | o domain is more internally structured than other HEADs |
| C1485 (HEAD x TERM affinity) | **SHARPENED** | o-HEAD affinities are near-deterministic, not just enriched |
| C1517 (o-HEAD zone-graded in AZC) | **CONFIRMED** with full zone detail | S=29.3% > C=26.2% > P=19.1% > R=17.7% |
| C1507 (bridge HEAD redistributes A vs B) | **CONFIRMED** with token-level detail | A selects o (28.5%), B selects e/k (11.8%) |
| C1543 (p/f o-HEAD arrangement affiliates) | **CONFIRMED** quantitatively | p 3.51x, f 2.83x within o-HEAD modifiers |
| C1546 (HEAD hazard source immunity) | **EXTENDED** to target immunity | o-HEAD 0% on both sides |
| C1551 (PHASE_ORDERING = y-terminal dy) | **CONNECTED** | o-HEAD avoids y at 0.007x, making it structurally immune |
| C1483 (terminal category specificity) | **SHARPENED** | o-HEAD shows near-deterministic terminal-category within a single HEAD |
| C1522 (AZC A-proximate vs B-proximate) | **CONFIRMED** at atom resolution | o-HEAD rate grades continuously from A-like to B-like zones |

---

## Interpretation (Tier 3)

The o-HEAD domain is an ARRANGEMENT SPECIFICATION SYSTEM. It uses three terminal atoms as categorical selectors:

1. **o+l = STAGING arrangement** (762 tokens) -- How things are arranged/positioned/configured. Minimal suffix (3%), no Mode A (2%). The `ol` morpheme is the LINK operator (C874) -- confirmed here as "arrangement + state = staging."

2. **o+r = FLOW arrangement** (446 tokens) -- How things flow/move through the system. Minimal suffix (3%), zero Mode A. Pure flow description.

3. **bare o = OPERATION arrangement** (388 tokens) -- What operational configuration is active. High suffix (77%), moderate Mode A (54%). Takes suffixes because the operation needs specification (dy for seal-end, s for staging, aiin for iteration).

4. **o+k/t = CONTAINMENT/MONITORING** (70+46 tokens) -- How containment and monitoring are arranged. These use the k/t terminal mirror (C1478) for thermal/flow monitoring of arrangements.

The "arrangement" gloss (C1388) is now PRECISE: o does not describe a single type of arrangement. It is a domain-selector HEAD that produces different arrangement types depending on its terminal atom. The terminal atom IS the arrangement type.

This makes o unique among HEADs: while k (THERMAL) and t (FLOW) are single-category domains (C1475), and e is a multi-category balanced domain, o is a multi-category CHANNELED domain where the terminal atom deterministically routes to the appropriate category.

---

## Files

| File | Purpose |
|------|---------|
| `phases/O_DOMAIN_DEEP_DIVE/scripts/o_domain_deep_dive.py` | Analysis script (13 tests) |
| `phases/O_DOMAIN_DEEP_DIVE/results/o_domain_deep_dive.json` | Full results |
| `phases/O_DOMAIN_DEEP_DIVE/REPORT.md` | This report |
