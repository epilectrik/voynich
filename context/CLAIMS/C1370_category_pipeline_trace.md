# C1370 — Category Pipeline Trace (A→AZC→B)

**Tier:** 2
**Scope:** A, AZC, B, cross-system, category, bridge, dark pipeline
**Phase:** 483 (CATEGORY_PIPELINE_TRACE)
**Depends on:** C1250, C1347, C1272, C1139, C1136, C1134, C1282

## Constraint

The 8-category pipeline is **WEAKLY_RESHAPED** (A↔B JS=0.026). Bridge MIDDLEs carry the same category identity across all systems, but B execution selectively amplifies THERMAL (+72%) and OPERATION (+58%) while attenuating STAGING (-47%) and MONITORING (-73%). AZC occupies an intermediate position closer to A (JS A↔AZC=0.015 < JS AZC↔B=0.016). Dark pipeline shows 3x less redistribution than bridge (JS 0.009 vs 0.026), confirming dark carries category identity more stably. Section-specific transfer functions exist: BIO has the strongest THERMAL amplification (2.03x), HERBAL is THERMAL-neutral (0.98x).

## T1: System-Level Category Profiles

| Category | A | AZC | B | A→B Ratio |
|----------|---|-----|---|-----------|
| THERMAL | 0.138 | 0.144 | **0.237** | **1.72** ↑ |
| FLOW | 0.173 | 0.190 | 0.201 | 1.16 |
| CONTAINMENT | 0.053 | 0.046 | 0.054 | 1.01 |
| STAGING | **0.250** | 0.161 | 0.134 | **0.54** ↓ |
| OPERATION | 0.097 | 0.126 | **0.153** | **1.58** ↑ |
| TRANSITION | 0.196 | **0.287** | 0.170 | 0.87 |
| MARKING | 0.041 | 0.024 | 0.037 | 0.91 |
| MONITORING | 0.053 | 0.022 | **0.014** | **0.27** ↓ |

Token counts: A=9,168, AZC=2,356, B=19,771 (bridge MIDDLEs only).

JS divergences: A↔B=0.026, A↔AZC=0.015, AZC↔B=0.016.

**Pipeline character:** Same vocabulary pool (C1136 uniform A supply confirmed), but execution grammar (B) selectively amplifies categories associated with active processing (THERMAL, OPERATION) and attenuates categories associated with specification/observation (STAGING, MONITORING).

**AZC is intermediate and closer to A.** AZC draws from the A pool (C758, C900) but already shows some B-direction shifts: TRANSITION peaks in AZC (0.287 vs 0.196 A, 0.170 B), consistent with AZC serving as the activation/transition boundary.

## T2: Pipeline Amplification Interpretation

The amplification pattern forms two coherent groups:

**Amplified in B (execution categories):**
- THERMAL +72%: Active heating/processing
- OPERATION +58%: Procedural actions
- FLOW +16%: Fluid dynamics (modest)

**Attenuated in B (specification categories):**
- STAGING -47%: Preparation/setup
- MONITORING -73%: Observation/measurement
- TRANSITION -13%: State changes (slight, compensated by AZC peak)
- MARKING -9%: Identification (nearly stable)

**CONTAINMENT is invariant** (ratio 1.01) — vessel/container references appear at equal rates across all systems.

## T3: AZC Zone Category Structure

| Zone | n | Top Category | TRANSITION fraction |
|------|---|--------------|-------------------|
| R (ring) | 1003 | TRANSITION 0.267 | 0.267 |
| C (center) | 482 | TRANSITION 0.268 | 0.268 |
| P (perimeter) | 313 | TRANSITION 0.307 | 0.307 |
| S (boundary) | 306 | **TRANSITION 0.333** | **0.333** |

TRANSITION dominates all AZC zones (consistent with AZC being the activation boundary). Zone S has the highest TRANSITION concentration (0.333 vs 0.267 for R), confirming P4 prediction. Zone S also has the lowest MONITORING (0.003) and STAGING (0.101).

Zone S is the most "execution-like" AZC zone; Zone R is the most "specification-like."

## T4: Section-Conditioned Transfer Functions

| Section | n | THERMAL ratio | JS from A | Character |
|---------|---|--------------|-----------|-----------|
| BIO | 6162 | **2.03** | 0.032 | **THERMAL-dominated execution** |
| STARS | 8938 | 1.84 | 0.033 | Strong THERMAL + FLOW |
| COSMO | 1243 | 1.19 | 0.024 | FLOW-oriented |
| HERBAL | 2226 | **0.98** | 0.025 | **THERMAL-neutral** |
| T_OTHER | 524 | 1.11 | 0.012 | Closest to A baseline |

**BIO = maximum THERMAL amplification** (2.03x). Consistent with balneum mariae = sustained gentle heating requiring intense thermal focus. BIO also amplifies OPERATION by 1.76x.

**HERBAL = THERMAL-neutral** (0.98x). Herbal programs do NOT preferentially select THERMAL bridge MIDDLEs. Instead, HERBAL amplifies CONTAINMENT (1.94x) and OPERATION (1.72x) — vessel-focused procedures, not heat-focused.

**Universal attenuations:** All sections attenuate STAGING (0.45-0.69x) and MONITORING (0.20-0.54x). The specification→execution shift is section-universal; only the amplification pattern varies.

## T5: Per-MIDDLE Rank Stability

82/85 bridge MIDDLEs appear in both A and B contexts. Rank correlation: **rho=0.644** (p<0.000001). Moderate disruption — the frequency hierarchy is recognizable but substantially rearranged.

**Per-category mean rank change (negative = gained rank in B):**
| Category | Mean Rank Change | Interpretation |
|----------|-----------------|----------------|
| OPERATION | -8.0 | Strongest gainers |
| THERMAL | -6.1 | Strong gainers |
| FLOW | -5.3 | Moderate gainers |
| CONTAINMENT | -2.6 | Stable |
| TRANSITION | +1.5 | Stable |
| STAGING | +4.3 | Moderate losers |
| MARKING | +5.9 | Losers |
| MONITORING | +13.3 | **Strongest losers** |

**Top gainer:** "edy" (OPERATION) — 7 tokens in A → 1,938 in B (rank change -71). This MIDDLE is the quintessential B execution token.

**Top loser:** "hy" (MONITORING) — 104 tokens in A → 8 in B (rank change +53). A common monitoring term in the specification that B rarely uses.

## T6: Dark Pipeline Control

| | Bridge JS(A↔B) | Dark JS(A↔B) | Ratio |
|--|----------------|--------------|-------|
| | 0.026 | **0.009** | **2.9x** |

Dark pipeline shows 2.9x less category redistribution than bridge. Dark MIDDLEs carry their category identity more stably across systems, consistent with their identification role (C1254) rather than active dynamics. Dark is MARKING-dominated (40% in A, 33% in B) across all systems — the identification vocabulary is categorically stable.

## Pre-Registered Prediction Scorecard

| # | Prediction | Result | Actual |
|---|-----------|--------|--------|
| P1 | A↔B JS > 0.05 (significant) | **FALSIFIED** | JS=0.026 (weak, not significant) |
| P2 | AZC intermediate, closer to A | **CONFIRMED** | JS A↔AZC=0.015, AZC↔B=0.016 |
| P3 | THERMAL amp, MARKING+STAGING att | **FALSIFIED** | THERMAL+STAGING correct, MARKING barely misses (0.91) |
| P4 | Zone S TRANSITION > Zone R | **CONFIRMED** | S=0.333 > R=0.267 |
| P5 | BIO highest THERMAL, HERBAL closest to A | **FALSIFIED** | BIO highest confirmed, but T_OTHER closest to A |
| P6 | Rank rho 0.5-0.7 | **CONFIRMED** | rho=0.644 |
| P7 | Dark less redistributed than bridge | **CONFIRMED** | JS 0.009 < 0.026 |

**Score: 4/7 confirmed.** The pipeline is weaker than predicted (P1 falsified) but internally coherent. Section predictions were half-right (P5: BIO correct, HERBAL wrong).

## Synthesis

The 8-category system reveals a **frequency-modulated pipeline** from specification (A) through activation (AZC) to execution (B):

1. **A provides a uniform specification pool** (C1136 confirmed) with balanced category representation. STAGING (25%) is the largest A category — programs start by specifying what to prepare.

2. **AZC serves as the transition boundary** — TRANSITION peaks here (28.7%), exceeding both A (19.6%) and B (17.0%). AZC is where specification becomes activation.

3. **B selectively amplifies execution categories** (THERMAL +72%, OPERATION +58%) and attenuates specification categories (STAGING -47%, MONITORING -73%). The shift is section-universal for attenuation but section-specific for amplification (BIO=THERMAL, HERBAL=CONTAINMENT).

4. **Dark pipeline is categorically stable** (3x less redistribution) — it carries identification labels, not dynamic content.

This is the first end-to-end trace of the 8-category system through the A→AZC→B pipeline, validating C1250's "spanning organizational principle" with quantitative transfer functions.

## Provenance

Script: `phases/CATEGORY_PIPELINE_TRACE/scripts/category_pipeline_trace.py`
Results: `phases/CATEGORY_PIPELINE_TRACE/results/category_pipeline_trace.json`
