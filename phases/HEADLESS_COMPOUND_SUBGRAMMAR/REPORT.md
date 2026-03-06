# Phase 536: HEADLESS_COMPOUND_SUBGRAMMAR

**Date:** 2026-03-06
**Status:** COMPLETE
**Constraints produced:** C1488-C1493 (6 new)

---

## Summary

Phase 536 characterizes the ~20.5% of Currier B compound MIDDLE tokens whose initial atom is NOT a HEAD atom {a,e,o,k,t}. These "headless" compounds (3,312 tokens, 469 types) form a structurally coherent functional domain with properties systematically distinct from headed compounds across all six dimensions tested: population structure, category profiles, terminal distributions, PREFIX selectivity, suffix behavior, and internal composition.

The verdict is **HEADLESS_IS_COHERENT_DOMAIN** (3 coherent vs 1 grab-bag evidence points).

---

## Analyses Performed

### a. Census (C1488)

Population structure of headless compounds:
- **3,312 tokens** (20.5% of 16,153 compound tokens), **469 types**
- Initial atom class: MODIFIER 77.5% (2,568 tokens), TERMINAL 19.3% (638), OTHER 3.2% (106)
- Top pseudo-HEAD atoms by token count: i=918, d=805, c=612, l=428, p=157, r=122

### b. Terminal Profile (C1490)

Headless compounds show a systematic terminal atom shift vs headed compounds:
- **Enriched:** h 2.98x (16.2% vs 5.4%), n 2.45x (25.0% vs 10.2%)
- **Depleted:** l 0.076x (1.0% vs 13.1%), r 0.153x (1.4% vs 9.1%), m 0.21x (0.3% vs 1.6%)
- **Neutral:** e 0.98x, y 0.86x
- **LOCKED tier total:** headless 1.7% vs headed 10.7% (6.2x depletion)

This represents structural hazard avoidance -- r-terminal is the primary hazard vector (C1447, 92.58% of forbidden violations). The shift concentrates headless terminals in the DIFFUSE (h) and CHANNELED (n) tiers, away from the hazard-carrying LOCKED tier.

### c. C1484 Compliance (C1490)

Terminal-modifier exclusivity rules hold in headless:
- n compliance: 100% (828/828 have i as only modifier)
- h compliance: 99.6% (535/537, 2 violations)
- y compliance: 99.6% (772/775, 3 violations)

### d. Modifier Distribution

Headless modifier composition is dominated by i (27.7%) and d (24.3%), consistent with the functional domain split where d=CONTAINMENT and i=STAGING are the dominant operations.

### e. Category Profiles (C1489)

The initial atom acts as a PSEUDO-HEAD with strong category selectivity (Cramer's V=0.511, chi2=5872, p=0.0):

| Pseudo-HEAD | Dominant Category | Concentration | N |
|-------------|------------------|---------------|---|
| d | CONTAINMENT | 84.0% | 805 |
| i | STAGING | 66.9% | 918 |
| p | MARKING | 91.7% | 157 |
| f | MARKING | 90.9% | 44 |
| r | FLOW | 60.7% | 122 |
| c | OPERATION | 32.2% | 612 |

Headless aggregate vs headed enrichment: CONTAINMENT 10.6x, MARKING 5.4x, MONITORING 4.0x, STAGING 2.9x. Depleted: THERMAL 0.11x, FLOW 0.24x, TRANSITION 0.22x.

The headless aggregate is categorically distinct from ALL 5 HEAD domains. Nearest HEAD: o (JSD=0.302), reflecting shared emphasis on STAGING/arrangement. Farthest: a (JSD=0.665).

### f. Hazard Profile

Headless compounds show structural hazard avoidance:
- r-terminal fraction: headless 1.39% vs headed 9.09% (0.153x)
- d-initial shows highest high-frame match rate at 84.1% (d→y frame), but these are CONTAINMENT operations with low actual hazard
- Quenched fraction (modifier-bearing): headless 21.0% vs headed 35.2%

### g. Position Profile

Line position shows no dramatic headless-specific pattern:
- Headless mean position: 0.491 vs headed 0.494
- Headless shows slightly higher line-initial rate (11.2% vs 9.6%) and lower line-final rate (8.5% vs 10.4%)

### h. PREFIX Selectivity (C1491)

Extreme PREFIX selectivity:
- **da:** 2284x enriched in headless (17.8% vs ~0.008% in headed)
- **sa:** 197 tokens, 100% headless (exclusive)
- **ta:** 107 tokens, 100% headless (exclusive)
- **ok:** 0.5% of headless vs 7.5% headed (depleted)
- **ot:** 0.8% of headless vs 7.2% headed (depleted)
- **BARE:** 18.0% of headless vs 30.1% headed (depleted)

The da-enrichment is specifically i-initial (C1394 noted da+iin/in pattern). sa and ta PREFIXes appear EXCLUSIVELY with headless MIDDLEs.

### i. Suffix Bifurcation (C1492)

Headless compounds bifurcate into two suffix populations:

**BARE (binary ops):** d-initial 14.9% suffix, i-initial 9.3% -- self-contained binary operations (seal/iterate) that don't need parametric specification.

**SUFFIXED (parametric ops):** c-initial 96.2%, p-initial 96.8%, f-initial 93.2% -- operations that require suffix to specify scope/mode.

Aggregate headless suffix rate: 47.5% (vs headed 35.7%). Modifier ordering grammar (C1472) compliance: headless 61.9% vs headed 70.1% (same grammar).

### j. Headless-Headed JSD

JSD distances from headless aggregate to each HEAD domain:
- o = 0.302 (nearest -- shared STAGING emphasis)
- k = 0.327
- e = 0.373
- t = 0.618
- a = 0.665 (farthest -- headless avoids FLOW/TRANSITION)

### k. Internal Structure (C1493)

Headless compounds have distinctive internal patterns:
- Dominant: MT (modifier+terminal) 46.7%
- T-only: 19.3%
- MMT: 16.3%
- MMMT+: 5.1%
- 35.7% contain HEAD atoms {a,e,o,k,t} in non-initial positions -- "displaced HEAD" compounds where a modifier or terminal atom takes grammatical priority

### l. Length Distribution

- Headless mean atom count: 2.64 (std 0.85)
- Headed mean atom count: 2.75 (std 0.87)
- KS test: p=1.17e-8 (statistically different but practically similar)
- Modal: 2-atom compounds dominate both populations

---

## Key Findings

1. **Headless is a coherent domain, not a grab-bag.** V=0.511 pseudo-HEAD differentiation, systematic category profile distinct from all 5 HEAD domains, consistent internal structure.

2. **Functional domain split maps to operational roles.** d=CONTAINMENT (seal/close), i=STAGING (cycle control), p/f=MARKING (parametric tagging), c=OPERATION (interior adjustment), r=FLOW (routing).

3. **Structural hazard avoidance is built-in.** LOCKED tier (r+m terminals) depleted 6.2x in headless. r-terminal, the primary hazard vector, drops from 9.1% to 1.4%.

4. **PREFIX channel separation is near-absolute.** da, sa, ta are headless-exclusive or near-exclusive. ok/ot are near-absent. Headless compounds occupy a distinct PREFIX channel.

5. **Suffix bifurcation reveals binary vs parametric operations.** d/i bare (binary presence/absence) vs c/p/f suffixed (parametric specification). Same modifier ordering grammar applies.

6. **The da-enrichment from C1394 is i-initial-specific.** The generic "headless" enrichment is actually concentrated in the da+i-initial channel (iin/in patterns).

---

## Constraints Produced

| # | Name | Tier | Key Finding |
|---|------|------|-------------|
| C1488 | Headless compound population structure | 2 | 3,312 tokens (20.5%), 469 types, MOD-initial 77.5% |
| C1489 | Headless pseudo-HEAD category differentiation | 2 | V=0.511, d=CONTAINMENT 84%, i=STAGING 67%, p=MARKING 92% |
| C1490 | Headless terminal profile shift | 2 | h 2.98x, n 2.45x enriched; r 0.153x, l 0.076x depleted; LOCKED 6.2x depletion |
| C1491 | Headless da-PREFIX near-exclusivity | 2 | da 2284x enriched; sa/ta 100% exclusive; ok/ot near-absent |
| C1492 | Headless suffix bifurcation | 2 | d/i bare (<15%) vs c/p/f suffixed (>93%); same ordering grammar |
| C1493 | Headless internal structure | 2 | MT dominant 46.7%; 35.7% displaced HEAD atoms; nearest HEAD domain o (JSD=0.302) |

---

## Relationship to Prior Work

- **C1397** (headless compound functional grammar): Phase 536 fully quantifies and extends the initial finding. V=0.503 from C1397 refined to V=0.511 with full atom decomposition.
- **C1394** (instruction encoding architecture): The da-enrichment noted in C1394 is confirmed as i-initial-specific, not generic headless.
- **C1475-C1479** (HEAD domain taxonomy): Headless pseudo-HEAD analysis parallels the HEAD taxonomy -- same method, complementary population.
- **C1440-C1445** (terminal opacity): Terminal rules apply in headless with minor deviations (3/6 opacity tiers fully compliant).
- **C1484** (terminal-modifier exclusivity): Confirmed in headless at 99.6-100% compliance.
- **C1472** (modifier co-occurrence avoidance): Same grammar applies in headless (61.9% vs 70.1% compliance).

---

## Files

| File | Purpose |
|------|---------|
| `scripts/headless_compound_subgrammar.py` | Phase analysis script (12 analyses + synthesis) |
| `results/headless_compound_subgrammar.json` | Complete results (2,870 lines) |
