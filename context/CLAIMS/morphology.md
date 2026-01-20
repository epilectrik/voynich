# Morphology Constraints (C349-C382, C386-C402, C407-C412, C466-C467, C495)

**Scope:** Morphological structure, transitions, functional grammar
**Status:** CLOSED

---

## Morphology Closure (C349-C352)

### C349 - Extended Cluster Prefixes
**Tier:** 2 | **Status:** CLOSED
Added prefixes: pch, tch, kch, dch, fch, rch, sch. All follow C+C+h pattern.
**Source:** MORPH-CLOSE

**Negative Result (N349):** `ck` is NOT an independent prefix family. Analysis shows 95.9% of apparent `ck-` tokens are actually `ckh-` forms that map 1:1 onto `ch-` family tokens (ckhy↔chy, ckhol↔chol, etc.). Treat `ckh-` as ch-family variants, not a new category. Do not add `ck`, `kc`, `dc`, `fc`, etc. without constraint validation.

### C350 - HT+B Hybrids Explained
**Tier:** 2 | **Status:** CLOSED
HT prefix + B suffix = 12.47% of corpus. Cross-layer morphological reuse.
**Source:** MORPH-CLOSE

### C351 - Final Classification
**Tier:** 2 | **Status:** CLOSED
92.66% explained, 3.90% ambiguous, 2.82% noise, 0.62% TRUE ORPHAN.
**Source:** MORPH-CLOSE

### C352 - TRUE ORPHAN Residue
**Tier:** 2 | **Status:** CLOSED
0.62% = consonant ligatures, vowel-initial fragments, scribal artifacts. No unaccounted system.
**Source:** MORPH-CLOSE

---

## B-Folio Vocabulary (C361-C364)

### C361 - Adjacent Folio Sharing
**Tier:** 2 | **Status:** CLOSED
Adjacent B folios share 1.30x more vocabulary (p<0.000001, d=0.76).
**Source:** BVP

### C362 - Regime Vocabulary Fingerprints
**Tier:** 2 | **Status:** CLOSED
Within-regime 1.29x more similar than between-regime (p=0.002).
**Source:** BVP

### C363 - Vocabulary Independent of Profiles
**Tier:** 2 | **Status:** CLOSED
Independent of stability and LINK profiles (ratio ~1.05).
**Source:** BVP

### C364 - Hub-Peripheral Structure
**Tier:** 2 | **Status:** CLOSED
41 core tokens (≥50% folios), 3,368 unique (68%, single folio).
**Source:** BVP

---

## B-Prefix Functional Grammar (C371-C374)

### C371 - Positional Grammar
**Tier:** 2 | **Status:** CLOSED
Line-initial: so (6.3x), ych (7.0x), pch (5.2x). Line-final: lo (3.7x), al (2.7x).
**Source:** BPF

### C372 - Kernel Contact Dichotomy
**Tier:** 2 | **Status:** CLOSED
KERNEL-HEAVY (ch, sh, ok, lk, lch, yk, ke) = 100% kernel. KERNEL-LIGHT (da 4.9%, sa 3.4%).
**Source:** BPF

### C373 - LINK Affinity Patterns
**Tier:** 2 | **Status:** CLOSED
LINK-ATTRACTED: al (2.48x), ol (1.82x), da (1.66x). LINK-AVOIDING: qo (0.65x).
**Source:** BPF

### C374 - Section Preferences
**Tier:** 2 | **Status:** CLOSED
Chi2=2369 (p=0). lk is 81% Section S. yk is 36% Section H.
**Source:** BPF

---

## B-Suffix Functional Grammar (C375-C378)

### C375 - Suffix Positional Grammar
**Tier:** 2 | **Status:** CLOSED
Line-final: -am (7.7x), -om (8.7x), -oly (4.6x). -am/-om are 80-90% line-final.
**Source:** BSF

### C376 - Suffix Kernel Dichotomy
**Tier:** 2 | **Status:** CLOSED
KERNEL-HEAVY: -edy (91%), -ey (95%), -dy (83%). KERNEL-LIGHT: -in (6%), -l (12%).
**Source:** BSF

### C377 - KERNEL-LIGHT Suffixes LINK-Attracted
**Tier:** 2 | **Status:** CLOSED
-l (2.78x), -in (2.30x), -r (2.16x) near LINK. -edy avoids (0.59x).
**Source:** BSF

### C378 - Prefix-Suffix Constrained
**Tier:** 2 | **Status:** CLOSED
Chi2=7053 (p=0). da+-aiin=30%, sh+-edy=28%.
**Source:** BSF

### C495 - SUFFIX–REGIME Compatibility Breadth Association
**Tier:** 2 | **Status:** CLOSED
SUFFIX morphology in Currier A tokens is associated with downstream REGIME compatibility breadth in Currier B. Tokens with the **-r suffix** are significantly enriched in **universal REGIME compatibility** (11.5% vs 4.2% baseline), while **-ar and -or suffixes** are significantly enriched in **single-REGIME restriction** (χ² = 28.36, p = 0.0004, Cramér's V = 0.159). PREFIX morphology shows **no significant association** with REGIME compatibility breadth (V = 0.068, p = 0.82). This constraint is **associative, not causal**: SUFFIX does not encode REGIME selection, but correlates with the breadth of execution contexts under which a discriminator remains admissible.
**Source:** A_REGIME_STRATIFICATION

**Note:** The naive finding that "39% of A tokens are REGIME-specific" was shown to be heavily confounded by frequency (Cramér's V = 0.38). Among frequent tokens (>20 occurrences), only 4.7% are genuinely single-REGIME. The SUFFIX effect survived this frequency control and represents the robust finding.

---

## Morphological Stability (C379-C382)

### C379 - Vocabulary Varies by Context
**Tier:** 2 | **Status:** CLOSED
Prefix CV=0.50, suffix CV=0.62. Section chi2=876.
**Source:** MSTAB

### C380 - Function is INVARIANT
**Tier:** 2 | **Status:** CLOSED
ch/sh 100% kernel-heavy in ALL folios. Role is constant.
**Source:** MSTAB

### C381 - Instruction Concentration
**Tier:** 2 | **Status:** CLOSED
28 combinations cover 50%, 87 cover 80% (from 394 total).
**Source:** MSTAB

### C382 - Morphology Encodes Control Phase
→ See [C382_morphology_control_phase.md](C382_morphology_control_phase.md)

---

## Transition Enrichment (C386-C390)

### C386 - Transition Suppression
**Tier:** 2 | **Status:** CLOSED
8 transitions significantly suppressed (<0.5x). All involve KERNEL-HEAVY tokens.
**Source:** TRANS

### C387 - QO as Phase-Transition Hub
**Tier:** 2 | **Status:** CLOSED
sh→qo enriched (2.04x). da/sa/al→qo suppressed (0.23-0.43x).
**Source:** TRANS

### C388 - Self-Transition Enrichment
**Tier:** 2 | **Status:** CLOSED
3.76x average. qokeedy→qokeedy (4.7x), qokedy→qokedy (4.4x).
**Source:** TRANS

### C389 - Bigram-Dominant Determinism
**Tier:** 2 | **Status:** CLOSED
H(X|prev 2)=0.41 bits (95.9% reduction). Next token nearly predetermined by prior 2.
**Source:** HOS

### C390 - No Recurring N-Grams
**Tier:** 2 | **Status:** CLOSED
99.6% trigrams hapax. 100% 5-grams+ unique. Local generation, not templates.
**Source:** HOS

---

## Grammar Architecture (C391-C393)

### C391 - Time-Reversal Symmetry
**Tier:** 2 | **Status:** CLOSED
H(X|past k) = H(X|future k). Bidirectional adjacency constraints.
**Source:** SYM

### C392 - Role-Level Capacity
**Tier:** 2 | **Status:** CLOSED
35/36 transitions observed (97.2%). Only HIGH_IMPACT→HIGH_IMPACT absent.
**Source:** CAP

### C393 - Flat Role-Level Topology
**Tier:** 2 | **Status:** CLOSED
Diameter 1, transitivity 1.0, zero articulation points.
**Source:** TOPO

---

## Regime-Role (C394-C396)

### C394 - Intensity-Role Differentiation
**Tier:** 2 | **Status:** CLOSED
Aggressive 1.34x ENERGY_OPERATOR. Conservative 2.0x HIGH_IMPACT.
**Source:** RRD

### C395 - Dual Control Strategy
**Tier:** 2 | **Status:** CLOSED
Aggressive = rapid small. Conservative = big + wait.
**Source:** RRD

### C396 - AUXILIARY Invariance
**Tier:** 2 | **Status:** CLOSED
8.5-9.0% across all regimes (p=0.99). Infrastructure constant.
**Source:** RRD

#### C396.a - Operational Refinement (BCI, 2026-01-18)

AUXILIARY Invariance reflects execution-critical infrastructure roles that:
- are required for grammar connectivity across nearly all Currier B programs,
- mediate access to kernel control operators (k, h, e),
- exhibit near-universal presence with limited REGIME and zone sensitivity,
- are grammatically redundant (collapsible per C411) but structurally non-removable,
- must remain outside AZC vocabulary-based constraint scope.

This refinement does not introduce a new mechanism or constraint. It clarifies the execution-level role of AUXILIARY classes previously identified as statistically invariant under C396.

*See [../TIER3/b_execution_infrastructure_characterization.md](../TIER3/b_execution_infrastructure_characterization.md) for quantitative characterization of AUXILIARY execution-infrastructure behavior.*

---

## Hazard Avoidance (C397-C402)

### C397 - QO-Prefix Escape Route
**Tier:** 2 | **Status:** CLOSED
qo- tokens are universal escape from hazard sources (25-47%).
**Source:** HAV

### C398 - Escape Role Stratification
**Tier:** 2 | **Status:** CLOSED
ENERGY_OPERATOR primary escape (40-67%). CORE_CONTROL secondary (22-32%).
**Source:** HAV

### C399 - Safe Precedence Pattern
**Tier:** 2 | **Status:** CLOSED
ENERGY_OPERATOR and CORE_CONTROL safely precede hazard targets (33-67%).
**Source:** HAV

### C400 - Boundary Hazard Depletion
**Tier:** 2 | **Status:** CLOSED
5-7x depleted at line-initial. Zero at folio-initial (0/82).
**Source:** BSA

### C401 - Self-Transition Dominance
**Tier:** 2 | **Status:** CLOSED
ENERGY_OPERATOR 45.6% self-transition. Role persistence dominant.
**Source:** LRM

### C402 - HIGH_IMPACT Clustering
**Tier:** 2 | **Status:** CLOSED
Only enriched role bigram (1.73x). Big interventions cluster.
**Source:** LRM

---

## Sister Pair Analysis (C407-C412)

### C407 - DA is Infrastructure
**Tier:** 2 | **Status:** CLOSED
Extreme suffix bias (-in 34.4%), line-boundary enrichment (20.9% line-initial).
**Source:** SISTER

### C408 - Sister Pair Equivalence
→ See [C408_sister_pairs.md](C408_sister_pairs.md)

### C409 - Mutual Exclusion
**Tier:** 2 | **Status:** CLOSED
ch-sh bigrams 0.62-0.65x. ok-ot 0.53-0.64x. Same slot, alternative choices.
**Source:** SISTER

### C410 - Section Conditioning
**Tier:** 2 | **Status:** CLOSED
H prefers ch (78-92%). B balanced (42-57%). Quire-level conditioning.
**Source:** SISTER

### C411 - Deliberate Over-Specification
→ See [C411_over_specification.md](C411_over_specification.md)

### C412 - Sister-Escape Anticorrelation
→ See [C412_sister_escape_anticorrelation.md](C412_sister_escape_anticorrelation.md)

---

## PREFIX Control-Flow Role (C466-C467)

### C466 - PREFIX Encodes Control-Flow Participation
**Tier:** 2 | **Status:** CLOSED
PREFIX classes differ in kernel adjacency, positional bias, and intervention association, but show weak correlation with AZC compatibility (V=0.17); PREFIX governs how tokens participate in control-flow rather than which compatibility class they belong to.
**Source:** F-A-014b, F-AZC-014

### C467 - qo-Prefix is Kernel-Adjacent
**Tier:** 2 | **Status:** CLOSED
The qo- prefix is enriched near kernel nodes (1.31x) and virtually never line-initial (0.01%), indicating preferential participation at high-constraint decision points rather than avoidance of core execution states. Escape/intervention happens AT complexity, not away from it.
**Source:** F-A-014b

---

## Imported Constraints

### C365 - LINK tokens are SPATIALLY UNIFORM within folios and lines: no positional clustering (p=0.005), run lengths match random (z=0.14), line-position uniform (p=0.80); LINK has no positional marking function (LDF, Tier 2)
**Tier:** 2 | **Status:** CLOSED
LINK tokens are SPATIALLY UNIFORM within folios and lines: no positional clustering (p=0.005), run lengths match random (z=0.14), line-position uniform (p=0.80); LINK has no positional marking function (LDF, Tier 2)
**Source:** v1.8-import

### C366 - LINK marks GRAMMAR STATE TRANSITIONS: preceded by AUXILIARY (1.50x), FLOW_OPERATOR (1.30x); followed by HIGH_IMPACT (2.70x), ENERGY_OPERATOR (1.15x); p<10^-18; LINK is boundary between monitoring and intervention phases (LDF, Tier 2)
**Tier:** 2 | **Status:** CLOSED
LINK marks GRAMMAR STATE TRANSITIONS: preceded by AUXILIARY (1.50x), FLOW_OPERATOR (1.30x); followed by HIGH_IMPACT (2.70x), ENERGY_OPERATOR (1.15x); p<10^-18; LINK is boundary between monitoring and intervention phases (LDF, Tier 2)
**Source:** v1.8-import

### C383 - GLOBAL MORPHOLOGICAL TYPE SYSTEM: Prefixes encode functional type (INTERVENTION vs MONITORING) globally across A, B, and AZC; ch/sh/ok=100% kernel contact in ALL systems, da/sa<5% in ALL systems; LINK affinity patterns identical (da/al attracted, qo/ok avoiding); type system is grammar-independent (A has no sequential grammar but same types); B instantiates types in sequential programs, A instantiates types in non-sequential registry; explains vocabulary sharing without semantic transfer (A-ARCH, Tier 2)
**Tier:** 2 | **Status:** CLOSED
GLOBAL MORPHOLOGICAL TYPE SYSTEM: Prefixes encode functional type (INTERVENTION vs MONITORING) globally across A, B, and AZC; ch/sh/ok=100% kernel contact in ALL systems, da/sa<5% in ALL systems; LINK affinity patterns identical (da/al attracted, qo/ok avoiding); type system is grammar-independent (A has no sequential grammar but same types); B instantiates types in sequential programs, A instantiates types in non-sequential registry; explains vocabulary sharing without semantic transfer (A-ARCH, Tier 2)
**Source:** v1.8-import

### C384 - NO ENTRY-LEVEL A-B COUPLING: Although A and B share global vocabulary and type system, there is NO entry-level or folio-level cross-reference; all B programs draw from identical A-derived vocabulary pool (Jaccard 0.998 between all B folios); 215 one-to-one tokens scatter across 207 unique A-B pairs (no repeated pairings beyond noise); rare tokens are rare globally, not relationally; A does NOT function as lookup catalog for B programs; coupling occurs ONLY at global type-system level (A-ARCH, Tier 2)
**Tier:** 2 | **Status:** CLOSED
NO ENTRY-LEVEL A-B COUPLING: Although A and B share global vocabulary and type system, there is NO entry-level or folio-level cross-reference; all B programs draw from identical A-derived vocabulary pool (Jaccard 0.998 between all B folios); 215 one-to-one tokens scatter across 207 unique A-B pairs (no repeated pairings beyond noise); rare tokens are rare globally, not relationally; A does NOT function as lookup catalog for B programs; coupling occurs ONLY at global type-system level (A-ARCH, Tier 2)
**Source:** v1.8-import

### C385 - STRUCTURAL GRADIENT IN CURRIER A: Currier A exhibits measurable internal ordering; higher-frequency tokens appear earlier in sequence (rho=-0.44); later folios contain longer tokens with fewer recognizable morphological components (length rho=+0.35, components rho=-0.29); section-level diversity increases H (0.311) -> P (0.440) -> T (0.623); gradient reflects systematic structural change within registry, independent of execution grammar or semantic interpretation (A-ARCH, Tier 2)
**Tier:** 2 | **Status:** CLOSED
STRUCTURAL GRADIENT IN CURRIER A: Currier A exhibits measurable internal ordering; higher-frequency tokens appear earlier in sequence (rho=-0.44); later folios contain longer tokens with fewer recognizable morphological components (length rho=+0.35, components rho=-0.29); section-level diversity increases H (0.311) -> P (0.440) -> T (0.623); gradient reflects systematic structural change within registry, independent of execution grammar or semantic interpretation (A-ARCH, Tier 2)
**Source:** v1.8-import


## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
