# Phase 516: Cross-Slot Interaction Grammar

**Date:** 2026-03-05
**Status:** COMPLETE
**Constraints produced:** C1411-C1415

---

## Motivation

Phases 504-515 independently decomposed each morphological slot:
- **PREFIX** = modifier + base (C1218-C1219)
- **MIDDLE** = HEAD + MOD* + TERM (C1393-C1394)
- **SUFFIX** = HEAD + TERM with 16-atom subset (C1408-C1410)

This phase tests how these three slots constrain each other WITHIN tokens. Are the slots independent channels, or does knowing one slot sharply constrain the others?

---

## Key Results

### T1: PREFIX -> MIDDLE Selectivity

PREFIX strongly selects MIDDLE HEAD atom (V=0.414, MI=1.089 bits, N=16,537). This is the strongest cross-slot coupling found. PREFIX -> MIDDLE TERM is weaker but still significant (V=0.314, MI=0.384 bits, N=7,428).

**Sister pairs select nearly identical MIDDLE atoms.** ch vs sh show JSD=0.010 for HEAD and JSD=0.010 for TERM. ok vs ot show JSD=0.010 for HEAD and JSD=0.012 for TERM. This means sister pairs differ in how carefully they do something, NOT in what they do. The operational domain (which MIDDLE atoms are legal) is identical within a sister pair; only manner/mode differs. This quantifies C1305 at atom resolution.

**Key selectivities:**
- qo: 94.2% of HEADs are k/t/e/s (energy-operational atoms)
- ch/sh: 74% e-initial (stability domain)
- ok/ot: 88% a/e-initial (iteration/stability domain)
- da: 92.1% i/r/d/l-initial (infrastructure atoms)

### T2: PREFIX -> SUFFIX Selectivity

PREFIX strongly determines whether a suffix EXISTS (V=0.489, N=19,232):
- qo: 90.4% suffixed (near-mandatory)
- ok/ot: ~28% suffixed (rare)
- da: 19.9% suffixed (rare)
- ch: 53.0% suffixed
- sh: 40.7% suffixed

PREFIX -> suffix MODE is weaker (V=0.169, MI=0.021 bits). PREFIX constrains suffix presence more than suffix type.

### T3: MIDDLE -> SUFFIX Selectivity (Strongest Single Coupling)

Full MIDDLE -> suffix mode: V=0.678, MI=0.422 bits.
MIDDLE TERM -> suffix mode: V=0.503, MI=0.187 bits.
MIDDLE HEAD -> suffix mode: V=0.323, MI=0.091 bits.

MIDDLE HEAD -> suffix presence: V=0.568 (very strong).

**MIDDLE is the dominant suffix determinant.** MIDDLE TERM alone outpredicts PREFIX (V=0.503 vs 0.169) for suffix mode. This extends C1338 to the atom level: the MIDDLE's terminal atom is the primary gatekeeper for what suffix can follow.

**Per-HEAD mode polarization:**
- d-initial: 3.1% Mode A (near-pure Mode B)
- r-initial: 0.8% Mode A (near-pure Mode B)
- i-initial: 3.2% Mode A (near-pure Mode B)
- h-initial: 68.1% Mode A (strong Mode A)
- e-initial: 56.2% Mode A (moderate Mode A)
- k-initial: 54.9% Mode A (moderate Mode A)

### T4: Three-Way Interaction

Suffix mode: I(PREFIX) = 0.021, I(MIDDLE) = 0.384, I(PREFIX+MIDDLE jointly) = 0.452 bits. Synergy = +0.047 bits (mild positive). Joint explains 45.4% of suffix mode entropy.

Suffix identity: synergy = +0.009 bits (negligible). Suffix identity is determined almost entirely by MIDDLE with minimal PREFIX contribution.

**Verdict:** Pairwise interactions dominate (confirming C1003 at the atom level). No three-way synergy detected.

### T5: Slot Independence Hierarchy

| Pair | MI (bits) | NMI | z-score |
|------|-----------|-----|---------|
| MIDDLE <-> SUFFIX | 1.767 | 0.451 | 239.1 |
| PREFIX <-> MIDDLE | 1.514 | 0.481 | 148.5 |
| PREFIX <-> SUFFIX | 0.283 | 0.090 | 79.1 |

**PREFIX and SUFFIX are the most independent pair** (NMI=0.090). Their coupling is almost entirely mediated through MIDDLE. This validates the architecture: PREFIX selects MIDDLE, MIDDLE determines SUFFIX. PREFIX-to-SUFFIX is a chain, not a direct link.

### T6: Cross-Slot Atom Co-occurrence

Same atom appearing in both MIDDLE and SUFFIX of one token:

| Atom | O/E ratio | Direction | p-value |
|------|-----------|-----------|---------|
| d | 0.203 | STRONG REPEL | 7.1e-81 |
| a | 0.465 | REPEL | 1.9e-29 |
| h | 0.509 | REPEL | 6.6e-9 |
| o | 0.634 | REPEL | 1.0e-7 |
| e | 1.310 | ATTRACT | 3.8e-50 |
| m | 10.156 | STRONG ATTRACT | 6.8e-9 |

**d strongly avoids appearing in both MIDDLE and SUFFIX** (only 20% of expected). This is striking because d is common in both MIDDLE (12.4% of tokens) and suffix (26.7%). This is a genuine cross-slot exclusion rule: tokens encoding d-operations in their MIDDLE avoid d-marked suffixes. Interpretation: d encodes "seal/close" in both positions; if the MIDDLE already specifies sealing, the suffix provides a different parameter.

**e attracts across slots** (131% of expected). Tokens with e in the MIDDLE are MORE likely to also have e in the suffix. This is consistent with e as stability depth marker -- stability compounds accumulate e across both MIDDLE and SUFFIX positions.

### T7: PREFIX Base vs Modifier -> MIDDLE

BASE predicts MIDDLE HEAD better than modifier (V=0.494 vs 0.295). This confirms and quantifies C1219 at the atom level: the last character of PREFIX (the base) determines what operational domain the MIDDLE comes from.

For suffix prediction, base and modifier are equally weak (V ~ 0.125). The PREFIX's suffix-selection power comes from overall PREFIX identity, not from the base-modifier distinction.

### T8: Conditional Entropy Chain

| Conditioning | Suffix Entropy Remaining | Reduction |
|-------------|-------------------------|-----------|
| None | 3.915 bits | -- |
| PREFIX | 3.632 bits | 0.283 bits (7.2%) |
| MIDDLE | 2.148 bits | 1.767 bits (45.1%) |
| PREFIX + MIDDLE | 1.853 bits | 2.062 bits (52.7%) |

**MIDDLE reduces suffix entropy 6.2x more than PREFIX does.** Combined, they explain 52.7% of suffix entropy — the remaining 47.3% is genuine token-level variation (consistent with C1153's ~40% design freedom).

Within MIDDLE atoms: TERM reduces suffix by 0.910 bits vs HEAD's 0.366 bits. **The exit atom of the MIDDLE is the primary suffix selector.**

### T9: Forbidden Combinations

**83 PREFIX x MIDDLE HEAD depleted pairs** (observed/expected < 0.10, chi2 p < 0.001).

Key patterns:
- **qo avoids e/a/o/y HEAD** (ratio 0.037-0.070). qo strongly selects k/t heads.
- **ok/ot categorically forbid k/t HEAD** (0 occurrences, expected 79-269). The ok/ot prefix never combines with k/t-initial MIDDLEs.
- **da forbids e HEAD** (0 observed, 214 expected). Infrastructure prefix da categorically avoids stability-domain MIDDLEs.
- **ch/sh forbid i/m/h HEAD** (0 observed in all cases). Monitoring prefixes never combine with iteration/containment/monitoring-initial MIDDLEs.

**2 forbidden MIDDLE TERM x SUFFIX HEAD pairs:**
- l (terminal) + e (suffix head) = 0 occurrences (37 expected)
- r (terminal) + e (suffix head) = 0 occurrences (46 expected)

This means: **when MIDDLE ends in l or r, suffix NEVER starts with e.** These are absolute prohibitions. Since l=state and r=response (C1385, C1387), this means state/response MIDDLEs never take e-headed (stability) suffixes — they use different suffix vocabulary.

**2 forbidden PREFIX x SUFFIX pairs** (low N, less confident): yk x al, te x y.

---

## Constraint Summary

| ID | Statement | Tier | Key Numbers |
|----|-----------|------|-------------|
| C1411 | PREFIX->MIDDLE selectivity hierarchy with sister pair atom identity | 2 | V=0.414 HEAD, JSD=0.010 sisters |
| C1412 | MIDDLE dominates suffix determination via terminal atom | 2 | V=0.678, TERM V=0.503 |
| C1413 | PREFIX-SUFFIX coupling is MIDDLE-mediated | 2 | NMI=0.090 direct, vs MIDDLE-SUFFIX NMI=0.451 |
| C1414 | Cross-slot atom co-occurrence exclusion rules | 2 | d O/E=0.203, e O/E=1.310, l/r-TERM x e-SUF=0 |
| C1415 | 83 forbidden PREFIX x MIDDLE HEAD combinations at atom level | 2 | 83 depleted, qo x e ratio=0.061, ok x k obs=0 |

---

## Structural Implications

1. **The instruction encoding chain is PREFIX -> MIDDLE -> SUFFIX**, not a three-way interaction. PREFIX selects MIDDLE domain (C1411), MIDDLE determines suffix (C1412), PREFIX->SUFFIX is almost entirely mediated (C1413). This validates C1003 (pairwise compositionality) at atom resolution.

2. **Sister pairs select identical MIDDLE content** (JSD=0.010). The ch/sh and ok/ot sister pairs differ only in manner, not material. This quantifies what C1305 stated qualitatively: sisters achieve category divergence through MIDDLE frequency modulation within an identical atom pool, not by accessing different atoms.

3. **MIDDLE TERM is the suffix gatekeeper.** The terminal atom of MIDDLE determines what suffix can follow — this is the most operationally significant cross-slot junction. l-terminal and r-terminal MIDDLEs absolutely forbid e-headed suffixes (C1414).

4. **Cross-slot atom co-occurrence reveals semantic exclusion.** d-atoms strongly repel across MIDDLE and SUFFIX, while e-atoms attract. This suggests a complementary-information principle: atoms encoding "seal" operations avoid suffix-domain sealing markers, while atoms encoding "stability" accumulate across both domains.

5. **qo is the most constrained PREFIX** — near-mandatory suffix (90.4%), near-forbidden from e/a/o MIDDLE HEAD atoms, strongly channeled into k/t-initial MIDDLEs. The THERMAL channel operates under tighter construction constraints than other prefixes.

---

## Files

- **Script:** `phases/CROSS_SLOT_INTERACTION/scripts/cross_slot_interaction.py`
- **Results:** `phases/CROSS_SLOT_INTERACTION/results/cross_slot_interaction.json`
- **Constraints:** C1411-C1415 in `context/CLAIMS/`
