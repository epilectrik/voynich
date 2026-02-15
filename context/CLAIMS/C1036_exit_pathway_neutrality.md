# C1036: AXM Exit Pathway Allocation Is Frequency-Neutral — C458 Does Not Manifest at Macro-State Boundary

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** EXIT_PATHWAY_PROFILING (Phase 358)
**Extends:** C1035 (57% residual irreducible), C1016 T3 (C458 reversal at raw transition level)
**Strengthens:** C458 (localizes where asymmetry does NOT live), C1023 (PREFIX routing is load-bearing)
**Relates to:** C1007 (AXM exit skyline), C1015 (6x6 transition matrix), C599 (AX scaffolding routing), C600 (CC trigger selectivity), C980 (free variation envelope)

---

## Statement

C458's hazard-clamped/recovery-free design asymmetry does not manifest at the AXM macro-state boundary. Exit allocation (which pathway is taken when leaving AXM), ingress allocation (which pathway is taken when entering AXM), and dwell duration (how long the system stays in AXM before exiting) all show the same pattern: CV is inversely proportional to pathway frequency. The most common pathway (FQ, ~57%) has the lowest CV; the rarest (AXm, ~9%) has the highest. This is the sampling theory prediction, not a structural signal.

The structurally important finding is in the correlation structure: exit pathways do not trade off within a simple multinomial constraint. FL and CC are uncorrelated (rho = -0.003 vs compositional null -0.333), and FL and AXm are positively correlated (rho = +0.038). Exit pathways are independently modulated — consistent with PREFIX-conditioned routing (C1023) rather than competitive allocation.

C458's asymmetry must live upstream of the boundary: within-AXM micro-dynamics, PREFIX routing distributions, hazard adjacency structure, or pre-exit gating — not in exit destination selection.

---

## Evidence

### S2-S3: Egress Analysis (Primary)

Exit-conditional framing: "Given that AXM IS exited, what fraction of exits go to each target?"

| Pathway | Mean Frac | CV | Weighted CV | Min | Max |
|---------|-----------|-----|-------------|-----|-----|
| FQ | 0.560 | 0.259 | 0.221 | 0.167 | 0.917 |
| FL | 0.203 | 0.557 | 0.485 | 0.000 | 0.583 |
| CC | 0.143 | 0.650 | 0.653 | 0.000 | 0.364 |
| AXm | 0.094 | 0.671 | 0.654 | 0.000 | 0.278 |

CV ranking: FQ < FL < CC < AXm — perfectly correlated with frequency.

C458 predicted FL lowest CV (hazard clamped) and FQ highest (recovery free). The opposite holds: FQ has the lowest CV and FL is intermediate. P1-P3 all FAIL.

### S6: Correlation Structure (Most Informative)

| Pair | rho | p | Delta from null (-0.333) |
|------|-----|---|--------------------------|
| FQ vs FL | -0.662 | <0.000001 | -0.329 (near null) |
| FQ vs CC | -0.536 | 0.000001 | -0.202 (exceeds) |
| FL vs CC | -0.003 | 0.981 | +0.331 (exceeds) |
| FL vs AXm | +0.038 | 0.752 | +0.371 (exceeds) |
| CC vs AXm | -0.344 | 0.003 | -0.011 (near null) |

FL and CC are completely uncorrelated — hazard and initiator pathways are independently allocated. FL and AXm are positively correlated — both are "escape from the main loop" exits that co-vary. This matches PREFIX-conditioned routing (C1023, C599, C600) rather than competitive probabilistic allocation.

### S9: Ingress Analysis (Mirror)

| Pathway | Ingress CV | Egress CV | Delta |
|---------|-----------|-----------|-------|
| FQ | 0.217 | 0.259 | -0.042 |
| FL | 0.531 | 0.557 | -0.026 |
| CC | 0.620 | 0.650 | -0.030 |
| AXm | 0.742 | 0.671 | +0.071 |

Ingress CV ranking identical to egress: FQ < FL < CC < AXm. Ingress-egress correlations strong (rho = 0.55-0.74, all p < 0.000001). The frequency-driven pattern is perfectly symmetric.

### S10: Dwell Duration Analysis

| Pathway | N episodes | Mean dwell | Cross-folio CV of mean |
|---------|-----------|------------|------------------------|
| FQ | 1560 | 2.252 | 0.227 |
| FL | 539 | 2.497 | 0.338 |
| CC | 385 | 2.208 | 0.411 |
| AXm | 259 | 2.247 | 0.443 |

Dwell CV ranking: FQ < FL < CC < AXm — same frequency-driven pattern. FL dwell is NOT more consistent than FQ dwell. C458 timing signal absent.

### S5: Variance Decomposition

| Pathway | eta2(REGIME) | eta2(Section) | eta2(R+S) | Residual |
|---------|-------------|---------------|-----------|----------|
| FQ | 0.022 | 0.154 | 0.249 | 0.751 |
| FL | 0.018 | 0.038 | 0.198 | 0.802 |
| CC | 0.134 | 0.396 | 0.461 | 0.539 |
| AXm | 0.090 | 0.186 | 0.308 | 0.692 |

FL exit allocation has the LOWEST eta-squared from REGIME+section (0.198) — its variance is predominantly program-specific, not explained by macro-organizational categories. CC has the highest section dependence (0.396), consistent with section-specific initiator patterns.

### Controls

- No pathway confounded with folio length (max |rho| = 0.103, P5 PASS)
- Corpus-level exit fractions match C1007 within 0.003 (validation)
- 72/82 B folios pass threshold (consistent with C1016)

---

## Interpretation

This is a localization result with three structural implications:

**1. C458 does not operate at the exit boundary.** The design asymmetry (hazard clamped, recovery free) does not manifest as differential exit allocation variability. All boundary-level measures (egress, ingress, dwell) show the same frequency-proportional CV pattern. The exit door is not where the asymmetry lives.

**2. Exit pathways are independently routed, not competitively allocated.** The correlation structure (S6) deviates systematically from the compositional null. FL/CC independence and FL/AXm positive correlation indicate that PREFIX-conditioned routing (C1023) governs exit selection, not a single probabilistic switch. Gatekeepers mark exits but do not bias destinations.

**3. The design freedom space is narrowed.** Combined with C1035 (aggregate folio statistics fail), this eliminates exit allocation proportions from the irreducible 57% residual. The program-specific variation must live in: within-AXM micro-dynamics, PREFIX routing distributions, hazard adjacency depth, or dwell path composition — not exit endpoints.

---

## Pre-registered prediction outcomes

| # | Prediction | Result | Pass |
|---|-----------|--------|------|
| P1 | FL exit has LOWEST CV (C458 hazard clamped) | Lowest = FQ (CV=0.259) | FAIL |
| P2 | FQ exit has HIGHEST CV (C458 recovery free) | Highest = AXm (CV=0.671) | FAIL |
| P3 | FQ CV > FL CV (C458 asymmetry) | FQ CV=0.259 < FL CV=0.557 | FAIL |
| P4 | CV ranking stable odd/even split | Lowest agrees, highest does not | FAIL |
| P5 | No pathway confounded with length (|rho| < 0.3) | Max |rho| = 0.103 | PASS |
| P6 | FL eta2(REGIME+section) < 0.50 | eta2 = 0.198 | PASS |
| P7 | CV(FQ) - CV(FL) >= 0.10 | -0.298 (wrong sign) | FAIL |

2/7 passed -> EXIT_PATHWAY_ASYMMETRY_NOT_FOUND

---

## Method

- 72 B folios with >= 50 state transitions (C1010 6-state partition, canonical: class 45 in AXm)
- Exit-conditional framing: normalize AXM row excluding self-loop
- 4 pathways: FQ, FL (FL_HAZ + FL_SAFE merged — FL_SAFE ~1.4 exits/folio), CC, AXm
- Cross-folio CV with N_exits-weighted sensitivity check
- Compositional correction: K=4 null rho = -1/3
- Odd/even line split for within-folio stability
- Ingress mirror: same analysis on AXM column
- Dwell episodes: maximal consecutive AXM runs within lines, grouped by exit target
- Variance decomposition: eta-squared by REGIME, section, archetype per pathway

**Script:** `phases/EXIT_PATHWAY_PROFILING/scripts/exit_pathway_profiling.py`
**Results:** `phases/EXIT_PATHWAY_PROFILING/results/exit_pathway_profiling.json`

---

## Verdict

**EXIT_PATHWAY_ASYMMETRY_NOT_FOUND**: C458's hazard-clamped/recovery-free design asymmetry does not manifest at the AXM macro-state boundary. Exit allocation, ingress allocation, and dwell duration all show frequency-proportional CV (FQ < FL < CC < AXm). The structurally informative finding is that exit pathways are independently routed (FL/CC uncorrelated, rho=-0.003), consistent with PREFIX-conditioned routing (C1023) rather than competitive allocation. This localizes C458 to within-AXM dynamics, not boundary crossing, and eliminates exit proportions from the 57% irreducible design freedom space (C1035).
