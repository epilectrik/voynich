# C1523: Currier A Headless Rate 1.43x Higher Than B/AZC

**Tier:** 2
**Scope:** GLOBAL, cross-system, headless, A, B, AZC, HEAD, rate, enrichment, C1488, C1507, C1519
**Phase:** HEADLESS_CROSS_SYSTEM (Phase 542)

## Claim

Currier A has a significantly higher headless compound rate (39.0%) than Currier B (27.2%) or AZC (27.9%). A vs B ratio = 1.43x (chi2=487.73, p=4.44e-108). B and AZC are statistically indistinguishable (chi2=0.63, p=0.428). A's excess headless tokens concentrate in pseudo-HEAD atoms i (21.3%, A's top-1) and y (16.4%, A's #2) rather than B's l/d-dominant profile (20.4%/18.2%). A's declarative register (C1395, C1507) preferentially uses headless compounds — specifically i-initial (TRANSITION) and y-initial (OPERATION) — over the headed executable domains. AZC tracks B's headless rate, not A's, despite AZC's otherwise A-proximate vocabulary profile (C1522).

## Evidence

- N=11,174 (A), 23,096 (B), 3,227 (AZC) tokens with valid MIDDLEs
- A headless: 4,353/11,174 = 39.0%
- B headless: 6,277/23,096 = 27.2%
- AZC headless: 899/3,227 = 27.9%
- Omnibus chi2=504.49, p=2.82e-110, dof=2
- A vs B: chi2=487.73, p=4.44e-108, ratio=1.433
- A vs AZC: chi2=132.62, p=1.09e-30, ratio=1.398
- B vs AZC: chi2=0.63, p=0.428, ratio=0.976 (NOT significant)
- A pseudo-HEAD profile: i=21.3%, y=16.4%, c=11.1%, l=10.5%, h=10.0%
- B pseudo-HEAD profile: l=20.4%, d=18.2%, i=16.8%, r=13.9%, c=9.8%

## Relationship to Prior Constraints

- **Extends C1488**: Headless as coherent domain now quantified cross-system; A has 1.43x more
- **Connects C1507**: A selects o-HEAD/headless (declarative). A's headless enrichment is the headless side of the same A-vs-B HEAD redistribution documented for headed compounds
- **Connects C1519**: A/C AZC family has 31.1% headless (closer to A=39%) vs Zodiac 25.4% (closer to B=27.2%), consistent with A/C being A-proximate
- **Connects C1395**: A as situation description language uses more headless infrastructure — headless = non-executable support vocabulary
- **Refines C1489**: A's pseudo-HEAD profile (i-dominant) differs from B's (l/d-dominant), suggesting system-specific pseudo-HEAD functional emphasis

## Source

`phases/HEADLESS_CROSS_SYSTEM/results/headless_cross_system.json` (T1, T2)
