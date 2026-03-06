# Phase 545: Executive Atom Instability -- p/f/c Cross-System Analysis

**Date:** 2026-03-06
**Status:** COMPLETE
**Constraints produced:** C1540-C1545

---

## Background

C1509 identifies three atoms {p, f, c} as the most UNSTABLE atoms in the system -- their behavioral profiles shift most between Currier A's declarative register and Currier B's execution grammar. The other modifier atoms {i, d, s} are classified as STABLE (i) or MODERATE (d, s). This phase investigates WHY p/f/c are unstable and WHAT structural mechanism drives the cross-system behavioral shift.

All three unstable atoms are from the MOD slot class (C1394). All three are also categorically excluded from suffix position (C1511: {k,t,p,f,c} absent from suffix). This exclusion pattern groups them with ACTION HEAD atoms {k,t} rather than with their fellow modifiers {i,d,s}.

## Key Findings

### FINDING 1: p/f/c Are NOT More Behaviorally Divergent (C1540)

**MAJOR SURPRISE.** The mean cross-system JSD(A,B) for UNSTABLE atoms {p,f,c} is 0.0110, which is LOWER than STABLE_MOD atoms {i,d,s} at 0.0319 -- a ratio of only 0.35x. Unstable atoms are actually LESS divergent than stable modifiers on aggregate behavioral measures.

The C1509 "instability" label does NOT reflect overall behavioral divergence. Instead, it reflects a very specific kind of shift: p/f/c change their FUNCTIONAL ROLE across systems while maintaining similar behavioral PROFILES within each system. This is consistent with C1509's internal/external JSD ratio metric (0.41) -- p/f/c are unstable in the sense that the CONTEXT around them shifts, not that their intrinsic behavior shifts.

The most divergent modifier atom is actually d (mean JSD = 0.0567), which C1509 classifies as MODERATE, not unstable. d's divergence is driven by massive headless rate shift (A: 55.1% -> B: 29.0%, delta = 26.1pp) and terminal profile changes (JSD = 0.0919).

### FINDING 2: Suffix Exclusion Defines the Unstable Set (C1541)

C1511's suffix exclusion set {k,t,p,f,c} = ACTION HEADs {k,t} + UNSTABLE MODs {p,f,c}. This is not a coincidence. The 5 suffix-excluded atoms share a structural property: they are NEVER used to encode outcomes or conditions (suffix function per C1510-C1511). Instead, they appear ONLY in instruction-encoding positions (HEAD and MOD slots in MIDDLE, plus PREFIX).

Validation: all 5 atoms have exactly 0 occurrences in suffix across all three systems (A=0, B=0, AZC=0). The other MOD atoms {i,d,s} all appear in suffix: i=4,209, d=3,806, s=986. The suffix exclusion is the sharpest partition between unstable and stable modifiers.

### FINDING 3: c Is a Slot-Switching Atom (C1542)

c has a dramatically different HEAD co-occurrence profile depending on whether it appears in PREFIX or MIDDLE position in B:

| Position | n | e-HEAD | headless | o-HEAD | k-HEAD | t-HEAD | a-HEAD |
|----------|---|--------|----------|--------|--------|--------|--------|
| PREFIX | 4,608 | 61.0% | 21.2% | 12.0% | 1.8% | 0.8% | 3.2% |
| MIDDLE | 2,096 | 17.9% | 46.4% | 16.8% | 11.8% | 5.8% | 1.3% |

When c is in PREFIX (as ch/sh modifier), it overwhelmingly selects e-HEAD MIDDLEs (61.0%). When c is in MIDDLE itself, it preferentially appears in headless compounds (46.4%) and distributes more broadly across HEAD domains.

This slot-switching behavior is unique to c among MOD atoms. c is the bridge atom between PREFIX parameterization (selecting e-family operations) and MIDDLE execution (operating in headless compounds). This explains C1496 (c-modifier at 87.1% is primary displacement context for k/t in headless compounds) and C1389 (c-atom main-loop modifier profile).

### FINDING 4: p/f Are o-HEAD Affiliated Across Systems (C1543)

Both p and f show strong o-HEAD affiliation that is STABLE across systems:

| Atom | A o-HEAD% | B o-HEAD% | Shift | A headless% | B headless% |
|------|-----------|-----------|-------|-------------|-------------|
| p | 36.6% | 41.2% | +4.6pp | 55.9% | 47.6% |
| f | 34.8% | 33.0% | -1.8pp | 57.4% | 46.0% |

Both atoms concentrate in o-HEAD (arrangement) and headless domains. Their top MIDDLEs confirm this:
- p: opch (107), pch (79), op (36), cph (36) -- overwhelmingly o-initial or headless
- f: fch (23), ofch (17), of (15), cfh (9) -- same pattern

Contrast with i (the stable MOD): i is 53.2% a-HEAD in B, completely different domain. p and f are ARRANGEMENT atoms (o-HEAD partnership) while i is an ITERATION atom (a-HEAD partnership).

### FINDING 5: Mode A Suffix Enrichment Gradient (C1544)

All three unstable atoms show strong Mode A suffix enrichment in B:

| Atom | B Mode A% | B Mode B% | B bare% | A->B Mode A shift |
|------|-----------|-----------|---------|-------------------|
| c | 83.4% | 10.3% | 4.9% | +25.3pp |
| f | 54.4% | 33.0% | 9.8% | +22.3pp |
| p | 56.9% | 32.0% | 6.7% | +15.5pp |

The stable MOD atoms are completely different: d=3.5% Mode A (bare-dominant at 68.6%), i=3.9% Mode A (bare-dominant at 74.3%). Only s among stable mods shows high Mode A (52.9%).

The A->B shift direction is consistent: all three unstable atoms INCREASE their Mode A rate when moving from A to B. Mode A = THERMAL/MONITORING specification (C1515). This means p/f/c become MORE specification-oriented in B's execution grammar than in A's declarative register.

### FINDING 6: f Has Anomalous Bridge/Dark Ratio (C1545)

f has the lowest bridge rate of any MOD atom at 49.3% (shared MIDDLEs between A and B), meaning 50.7% of f-containing tokens in B use B-only MIDDLEs. Compare:

| Atom | Bridge (shared)% | B-only% | n |
|------|------------------|---------|---|
| c | 78.6% | 21.4% | 2,096 |
| d | 89.4% | 10.6% | 4,401 |
| f | **49.3%** | **50.7%** | 215 |
| i | 92.8% | 7.2% | 2,875 |
| p | 65.7% | 34.3% | 638 |
| s | 59.1% | 40.9% | 560 |

f is unique: half its MIDDLE vocabulary is B-exclusive. This means f participates disproportionately in B's autonomous grammar (the dark pipeline / identification vocabulary layer). Combined with f's low total frequency (215 tokens in B, far below any other MOD atom), f is the rarest and most B-specialized of all modifiers.

p also shows elevated B-only rate (34.3%), consistent with p/f sharing a structural role distinct from d/i which are heavily bridge-affiliated.

## Synthesis

### The Instability Mechanism

p/f/c are "unstable" NOT because their behavioral profiles diverge maximally across systems, but because they occupy a unique FUNCTIONAL NICHE:

1. **Suffix exclusion** (shared with k,t): They encode instructions, never outcomes/conditions
2. **Slot switching** (especially c): They change functional role between PREFIX and MIDDLE positions
3. **Arrangement affiliation** (p,f): They partner with o-HEAD, the arrangement domain marker
4. **Mode A enrichment**: They become more specification-oriented in B's execution grammar
5. **B-exclusive vocabulary** (especially f): They participate disproportionately in B's autonomous identification vocabulary

The expert hypothesis that p/f/c are "register-sensitive operator-facing atoms that help convert shared ontology into executable formatting" is PARTIALLY CONFIRMED. c is indeed a parameterization atom (slot-switching between PREFIX and MIDDLE). p and f are arrangement-affiliated atoms that concentrate in B-exclusive vocabulary. But the instability is not about behavioral divergence -- it is about FUNCTIONAL NICHE SPECIALIZATION. These atoms occupy the boundary between the shared substrate and system-specific deployment.

### Relationship to C1509

C1509's internal/external JSD ratio of 0.41 makes sense now: the MIDDLE containing p/f/c is stable (same atom composition), but the CONTEXT around it (PREFIX choice, suffix attachment, system affiliation) shifts dramatically. The atoms don't change; their deployment context does. This is exactly what you'd expect for atoms that serve as the "conversion machinery" between registers.

### What This Tells Us About the Grammar

The 18 atoms partition into THREE functional tiers by suffix access:

| Tier | Atoms | Suffix access | Function |
|------|-------|--------------|----------|
| OUTCOME | {a,e,o,d,i,s,y,l,r,h,m,n} | YES (in suffix) | Can encode results/conditions |
| INSTRUCTION-ONLY | {k,t,p,f,c} | NO (excluded) | Encode actions/parameters only |

Within INSTRUCTION-ONLY:
- {k,t} are ACTION HEADs -- domain selectors (THERMAL/FLOW)
- {p,f,c} are EXECUTIVE MODs -- parameterizers/formatters

This partition was already noted in C1511 but not connected to the instability finding. Phase 545 establishes the connection: suffix exclusion = instruction-only function = register sensitivity = "instability" in C1509's metric.

## Constraints Produced

- **C1540**: p/f/c NOT more behaviorally divergent than stable MODs; mean JSD 0.0110 vs 0.0319 (0.35x); instability is functional niche not behavioral divergence
- **C1541**: Suffix exclusion set {k,t,p,f,c} partitions atoms into OUTCOME-accessible vs INSTRUCTION-ONLY tiers; connects C1511 exclusion to C1509 instability
- **C1542**: c is slot-switching atom: PREFIX position selects e-HEAD 61%, MIDDLE position selects headless 46%; unique bridge between PREFIX parameterization and MIDDLE execution
- **C1543**: p/f are o-HEAD arrangement-affiliated atoms stable across systems (o-HEAD 33-41%); contrast with i (a-HEAD 53%); arrangement vs iteration partition
- **C1544**: All three unstable atoms increase Mode A suffix rate A->B (+15 to +25pp); specification-oriented in execution grammar
- **C1545**: f has anomalous 49.3% bridge rate (50.7% B-exclusive vocabulary); rarest MOD atom (215 B tokens); most B-specialized modifier

## Expert Predictions Assessment

| Prediction | Result |
|-----------|--------|
| c is parameterization atom | **CONFIRMED** -- slot-switching between PREFIX and MIDDLE (C1542) |
| p/f are register-sensitive | **PARTIALLY CONFIRMED** -- arrangement-affiliated, Mode A enriched, but not maximally divergent |
| Instability = behavioral divergence | **INVERTED** -- p/f/c are LESS divergent than i/d/s (0.35x ratio) |
| Suffix exclusion connects to instability | **CONFIRMED** -- {k,t,p,f,c} suffix exclusion = instruction-only tier (C1541) |
