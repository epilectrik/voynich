# Phase 546: Hazard x PREFIX Integration

**Date:** 2026-03-06
**Status:** COMPLETE
**Constraints produced:** C1546-C1552 (7 new Tier 2 constraints)

## Purpose

Join the hazard-class atlas (C1528-C1533, Phase 543) with the PREFIX atom taxonomy (C1534-C1539, Phase 544) to determine whether PREFIX bases and modifiers actively route hazard exposure through the instruction grammar.

## Research Questions

1. Do different PREFIX bases feed into different hazard classes?
2. Do PREFIX modifiers shift hazard exposure within the same base?
3. Do sister pairs (ch/sh, ok/ot, da/sa/ta) differ in hazard-class exposure?
4. Is a-base the primary hazard feeder via headless -> PHASE_ORDERING pathway?
5. Does qo's k-HEAD routing create systematic safety via hazard immunity?
6. Why is PHASE_ORDERING CHSH-specific? (mechanism question)
7. Do safe tokens cluster under specific PREFIX types?

## Key Findings

### 1. Universal HEAD Atom Hazard Source Immunity (C1546)

**The strongest finding.** ALL five HEAD atoms {a, e, o, k, t} have exactly 0% hazard source rate across 16,819 headed tokens (chi2=4411.9, V=0.219). All 1,537 hazard source tokens come exclusively from HEADLESS MIDDLEs (24.49% of 6,277 headless tokens). This extends C1446 (k-HEAD immunity) from k alone to the entire HEAD class. HEAD presence vs absence is the PRIMARY binary safety gate.

The three-way base x HEAD x hazard decomposition confirmed this is HEAD-INTRINSIC: within EVERY PREFIX base, headed tokens have 0% source rate while headless tokens carry all hazard. The immunity is not mediated by base selection.

### 2. TERMINAL Atom Determines Hazard Class Type (C1547)

TERMINAL atom discriminates hazard class type MORE strongly than HEAD (V=0.306 vs V=0.219, ratio 1.40x). The mapping is categorical:
- y-terminal -> PHASE_ORDERING (675/675 = 100%)
- l-terminal -> CONTAINMENT_TIMING (855/855 = 100%)
- bare-terminal -> RATE_MISMATCH (5/5 = 100%)
- h-terminal -> ENERGY_OVERSHOOT (2/2 = 100%)

HEAD gates WHETHER hazard occurs (binary). TERMINAL selects WHAT TYPE of hazard results (categorical). Two complementary information channels.

### 3. PREFIX Base Hazard Differentiation (C1548)

PREFIX bases show a significant hazard gradient (chi2=2038.0, V=0.133):
- e-base: 3.37x enriched (22.4% source rate)
- a-base: 2.00x enriched (13.3%)
- o-base: 1.20x (7.99%)
- h-base: 0.71x depleted (4.75%)
- k-base: 0.30x depleted (2.02%)

The gradient is partly HEAD-mediated (bases selecting more HEAD atoms have lower aggregate hazard) and partly independent (headless hazard rates differ across bases).

### 4. q-Modifier Hazard Protection (C1549)

Within o-base, the q-modifier produces 4.15% hazard source rate (0.52x vs base mean) while ALL other o-modifiers produce 27-52% (3.4-6.5x). The mechanism is k-HEAD activation: q uniquely routes 64% of o-base tokens to k-HEAD (C1538), and k-HEAD is categorically immune (C1546). This makes qo the STRONGEST single-PREFIX hazard protection mechanism.

Contrast with h-base: kch (k-modifier on h-base) has 21.65% hazard — k as a modifier does NOT provide HEAD immunity because k occupies the modifier slot, not the HEAD slot. Slot position determines function.

### 5. Sister Pair Hazard Asymmetry (C1550)

Sister pairs show consistent asymmetry:
- ch/sh: 1.80x (ch more hazardous — active testing involves more diverse configurations)
- ok/ot: 0.66x INVERTED (ot more hazardous — base-driven, t-base has less k-HEAD protection)
- da/sa: 1.54x (da more hazardous — d-modifier routes to higher-hazard headless configurations)

Same-base pairs differ by modifier effect. Same-modifier pairs differ by base effect. The asymmetry direction is predictable from the atom-level HEAD routing profiles.

### 6. Hazard Class Atom Signatures (C1551)

PHASE_ORDERING is exclusively headless y-terminal 'dy' (675 tokens, spread across 10+ PREFIXes). CONTAINMENT_TIMING is exclusively l-terminal 'l' (855 tokens, spread across 12+ PREFIXes). Both source MIDDLEs appear under all major PREFIX channels — hazard is MIDDLE-intrinsic, not PREFIX-induced. PREFIX modulates the RATE of exposure but not the EXISTENCE of hazard-capable MIDDLEs.

### 7. Phantom Source MIDDLEs (C1552)

5 of 9 hazard source MIDDLEs are phantom types with 0 corpus tokens: chey, shey, chedy, shedy, chol. All are ch/sh-initial (dead naming pattern, C1178). The forbidden topology was designed conservatively — it prohibits transitions that the vocabulary system subsequently made impossible. Defense-in-depth architecture.

## Answers to Research Questions

1. **Yes** — PREFIX bases feed into different hazard exposure levels (V=0.133) via HEAD proportion and headless MIDDLE vocabulary.
2. **Yes** — modifiers dramatically shift hazard within the same base; q on o-base provides ~7x protection vs other modifiers.
3. **Yes** — sister pairs show 0.66-1.80x asymmetry, direction determined by whether difference is modifier-driven or base-driven.
4. **Partially** — a-base is second-highest hazard (2.00x) but e-base is highest (3.37x). a-base's headless proportion (94-96%) makes it a large hazard contributor by volume.
5. **Yes** — qo's k-HEAD routing (C1538) creates systematic safety because k-HEAD (and all HEAD atoms) are categorically hazard-immune.
6. **Resolved** — PHASE_ORDERING is not inherently CHSH-specific at PREFIX level; 'dy' appears under ch (305), sh (111), BARE (95), qo (66), and others. C1533's finding of CHSH specificity reflects the higher density of hazard-vulnerable headless MIDDLEs in the CHSH lane.
7. **Yes** — k-HEAD immune tokens concentrate in o-base (2,566 tokens), l-base (394), and h-base (118). Safe tokens cluster under bases that select HEAD atoms frequently.

## Architectural Significance

This phase completes the hazard x atom architecture by connecting three previously separate findings:
- **Phase 534** (C1475-C1482): HEAD domains differentiate hazard exposure
- **Phase 543** (C1528-C1533): Hazard classes map to atom territories
- **Phase 544** (C1534-C1539): PREFIX bases select HEAD domains

The chain is now: **PREFIX base -> HEAD selection -> hazard immunity (binary) -> TERMINAL atom -> hazard class type (categorical)**. This is the COMPLETE hazard routing architecture from PREFIX input to hazard output.

## Method

Analysis script: `phases/HAZARD_PREFIX_INTEGRATION/scripts/hazard_prefix_integration.py`
Results: `phases/HAZARD_PREFIX_INTEGRATION/results/hazard_prefix_integration.json`

11-step analysis pipeline:
1. PREFIX hazard profiles (source/target rates for 30+ PREFIXes)
2. Base-level aggregation with HEAD distribution
3. HEAD hazard contingency table
4. TERMINAL hazard contingency table
5. Sister pair hazard comparison
6. Headless hazard pathway verification
7. k-HEAD/qo immunity analysis
8. CHSH mechanism decomposition
9. Modifier effects within bases
10. Safe token clustering by base
11. Three-way base x HEAD x hazard decomposition
