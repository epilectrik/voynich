# Phase 544: PREFIX Atom Taxonomy

**Date:** 2026-03-06
**Status:** COMPLETE
**Constraints produced:** C1534-C1539

---

## Purpose

Decompose PREFIX morphology at the individual atom (character) level, paralleling the MIDDLE atom decomposition (Phases 523-540) and suffix atom decomposition (Phase 540). This completes the atom-level characterization of all three morphological slots (PREFIX, MIDDLE, SUFFIX).

## Background

C1218 established that PREFIX characters have an internal base-modifier positional grammar. C1219 proved that the base (final) character determines MIDDLE content selection. C1220 showed modifier consistency varies by character. C1393-C1394 established the MIDDLE instruction encoding as HEAD+MOD*+TERM with 18 atoms in 4 slot roles. C1499 proved the atom ontology is a manuscript-wide shared substrate.

The question now: does PREFIX decompose into the SAME atoms as MIDDLE, and if so, do they occupy the same functional slots?

## Research Questions (7)

1. Does PREFIX decompose into atoms with positional preferences?
2. What is the base inventory with functional domains?
3. Are PREFIX modifiers analogous to MIDDLE modifiers?
4. Sister pair comparison at atom resolution?
5. Cross-system distribution?
6. PREFIX-to-hazard mapping at atom level?
7. Articulator interaction?

---

## Method

Analysis script: `phases/PREFIX_ATOM_TAXONOMY/scripts/prefix_atom_taxonomy.py`

13-step analysis on 30,938 prefixed tokens (A=9,257, B=19,232, AZC=2,449):

1. Character inventory and frequency
2. Positional classification (MODIFIER/BASE/DUAL)
3. Base-to-HEAD selection profiles
4. Modifier analysis and overlap with MIDDLE MODs
5. Sister pair atom-level decomposition
6. Cross-system character distribution
7. Base-to-category routing
8. Headless rates by PREFIX type
9. Base x terminal interaction
10. Cross-slot inventory comparison (PREFIX vs MIDDLE vs SUFFIX)
11. Articulator rates by PREFIX
12. Modifier effects on HEAD selection within each base
13. Line position analysis (not reported separately, extends C1218)

---

## Results

### Finding 1: PREFIX uses exactly 15 characters, identical across all 3 systems

PREFIX inventory: {a, c, d, e, f, h, k, l, o, p, q, r, s, t, y}

Cross-system Jaccard similarity:
- A-B: 1.000
- A-AZC: 1.000
- B-AZC: 1.000

All 15 characters appear in all three systems. This extends C1499 (shared substrate) to confirm PREFIX is part of the same universal alphabet.

**Frequency ordering:** o (12,787) > h (11,748) > c (8,462) > q (5,227) > s (4,779) > k (4,618) > t (4,297) > a (3,939) > d (3,062) > l (2,259) > e (844) > y (648) > p (501) > r (489) > f (85)

**Length distribution:** 94% two-character, 6% three-character. NO singleton PREFIXes exist in the corpus.

### Finding 2: Three-tier positional classification (MODIFIER / BASE / DUAL)

PREFIX characters partition into three strict positional tiers:

| Tier | Characters | Positional Rule | Count |
|------|-----------|----------------|-------|
| **MODIFIER** | c, d, f, p, q, s, y | Always/mostly position-0 (96-100%) | 7 |
| **BASE** | e, h | Always position-final (100%) | 2 |
| **DUAL** | a, k, l, o, r, t | Both positions (11-89% initial) | 6 |

Key observations:
- MODIFIER atoms {d, f, p, q, y} are 100% position-0 (categorical)
- {c} is 79.3% position-0 (medial 20.7% in 3-char PREFIXes like kch, lch, tch)
- {s} is 97.5% position-0 (medial 2.5%)
- BASE atoms {e, h} are 100% position-final (categorical)
- DUAL atoms span a gradient: a (88.8% final) through o (51.4% final)

This REFINES C1218 which classified 7 modifiers (q,d,f,p,y,s + "c") and 2 bases (h,e) with "dual-role" (o,k,l,t,c,a,r). Our data confirms the exact same classification with quantitative precision.

### Finding 3: 'i' is categorically ABSENT from PREFIX

The 6 MIDDLE MOD atoms are {p, i, c, f, d, s} (C1394). Of these, 5 appear in PREFIX: {p, c, f, d, s}. The atom 'i' is the ONLY MIDDLE MOD atom categorically excluded from PREFIX position.

Similarly, MIDDLE has 5 characters not present in PREFIX: {i, m, n, g, x}.

Cross-slot inventory comparison:
- PREFIX: 15 chars
- MIDDLE: 20 chars (all 15 PREFIX chars + i, m, n, g, x)
- SUFFIX: 13 chars (subset of MIDDLE, missing k, t, p, f, c per C1511)

PREFIX is a SUBSET of MIDDLE's alphabet (Jaccard PREFIX/MIDDLE = 0.75). SUFFIX is a different subset (Jaccard PREFIX/SUFFIX = 0.474). No character is PREFIX-exclusive.

The i-exclusion is structurally significant because:
- 'i' is the iteration/extensibility atom in MIDDLE (C1197, C1204, C1205)
- 'i' is the ONLY atom that can repeat consecutively (with 'e') at structural levels
- PREFIX explicitly excludes the iteration mechanism from its compositional grammar

### Finding 4: Base-to-HEAD selection is structured (V=0.478)

Chi-squared = 21,946.2, p < 0.001, Cramer's V = 0.478. Each base character selects a distinct HEAD domain profile:

| Base | Dominant HEAD | Rate | Second HEAD | Rate | Headless | N |
|------|-------------|------|------------|------|----------|---|
| **o** | k (THERMAL) | 57.1% | t (FLOW) | 18.0% | 19.3% | 4,683 |
| **h** | e (STABILITY) | 65.7% | o (ARRANGE) | 11.9% | 10.3% | 6,993 |
| **a** | headless | 95.8% | -- | -- | 95.8% | 1,887 |
| **k** | e (STABILITY) | 49.0% | a (CONTAIN) | 39.1% | 7.6% | 2,228 |
| **t** | e (STABILITY) | 43.4% | a (CONTAIN) | 37.3% | 11.6% | 1,508 |
| **l** | k (THERMAL) | 37.8% | e (STABILITY) | 17.6% | 19.8% | 1,048 |
| **e** | e (STABILITY) | 52.4% | headless | 30.7% | 30.7% | 576 |
| **r** | a (CONTAIN) | 49.5% | o (ARRANGE) | 26.2% | 14.9% | 309 |

**Domain specializations:**
- **o-base = THERMAL channel** (qo: 64% k-HEAD + 20% t-HEAD = 84% thermal/flow)
- **h-base = STABILITY channel** (ch/sh: 66% e-HEAD)
- **a-base = HEADLESS domain** (da/sa/ka/ta: 94-96% headless)
- **k-base and t-base = STABILITY/CONTAINMENT** (k: 49% e + 39% a; t: 43% e + 37% a)
- **l-base = mixed THERMAL/STABILITY** (38% k + 18% e)
- **r-base = CONTAINMENT/ARRANGEMENT** (50% a + 26% o)
- **e-base = STABILITY** (52% e + 31% headless)

### Finding 5: Sister pairs have structurally DIFFERENT architectures

| Sister Pair | Modifier | Base | Structure | HEAD JSD |
|------------|----------|------|-----------|----------|
| ch / sh | c / s | h | SAME_BASE | 0.0089 |
| ok / ot | o | k / t | SAME_MOD | 0.0034 |
| da / sa | d / s | a | SAME_BASE | 0.0028 |

All three pairs have extremely low HEAD JSD (< 0.01), confirming they select the SAME operational domain. But their non-content properties diverge:

**ch vs sh (SAME_BASE h):**
- Suffix rate: ch 53.0% vs sh 40.7% (ch more suffixed)
- Articulator rate: ch 3.9% vs sh 13.2% (sh 3.4x more articulators)
- Headless rate: ch 10.4% vs sh 6.6%

**ok vs ot (SAME_MOD o):**
- Suffix rate: ok 28.5% vs ot 27.1% (nearly identical)
- Articulator rate: ok 0.8% vs ot 0.8% (identical)
- Headless rate: ok 7.7% vs ot 8.6% (nearly identical)

**da vs sa (SAME_BASE a):**
- Suffix rate: da 19.9% vs sa 20.7% (nearly identical)
- Articulator rate: da 3.4% vs sa 2.7% (similar)
- Headless rate: da 95.9% vs sa 96.0% (nearly identical)

ok/ot is structurally DIFFERENT from ch/sh and da/sa: ok/ot shares the modifier (o) but differs in base (k vs t), while ch/sh and da/sa share the base but differ in modifier. Yet ok/ot shows the SMALLEST HEAD JSD (0.0034) because k and t are terminal mirrors (C1478) that produce similar HEAD selection when used as bases.

### Finding 6: Modifier effects on HEAD selection are base-dependent

Within base 'h' (stability channel), different modifiers produce different headless rates and HEAD emphasis:

| Modifier + h | e-HEAD | headless | N |
|-------------|--------|----------|---|
| ch | 60.3% | 10.4% | 3,492 |
| sh | 72.0% | 6.6% | 2,329 |
| lch | 77.5% | 14.0% | 315 |
| lsh | 86.2% | 6.0% | 116 |
| dch | 74.0% | 12.5% | 104 |
| kch | 57.7% | 32.0% | 97 |
| pch | 62.4% | 16.3% | 245 |
| tch | 56.4% | 24.4% | 172 |
| fch | 61.4% | 21.1% | 57 |

Key patterns:
- l-modifier MAXIMIZES e-HEAD selection (lch 77.5%, lsh 86.2%)
- k-modifier and t-modifier INCREASE headless rate (kch 32.0%, tch 24.4%)
- sh consistently has HIGHER e-HEAD than ch across all modifier combinations

Within base 'a' (headless channel), modifiers have MINIMAL effect:

| Modifier + a | headless | N |
|-------------|----------|---|
| da | 95.9% | 1,083 |
| sa | 96.0% | 329 |
| ka | 94.5% | 238 |
| ta | 95.8% | 237 |

All modifiers produce 94-96% headless. The a-base LOCKS headless status regardless of modifier.

Within base 'o' (thermal channel), q-modifier is the THERMAL selector:

| Modifier + o | k-HEAD | headless | N |
|-------------|--------|----------|---|
| qo | 64.0% | 11.1% | 4,069 |
| so | 18.5% | 73.0% | 189 |
| po | 8.1% | 65.4% | 136 |
| do | 4.8% | 86.5% | 126 |
| to | 15.7% | 67.0% | 115 |
| ko | 6.2% | 79.2% | 48 |

q-modifier is the ONLY modifier that strongly selects k-HEAD (64%) when paired with o-base. All other modifiers with o-base produce MOSTLY HEADLESS tokens (65-87%). This means qo is genuinely compositional: q specifically activates the thermal channel on the o-base.

### Finding 7: Articulator rates vary dramatically by PREFIX

te (45.7%), ta (42.2%), tch (22.1%), fch (22.8%), pch (19.6%), ar (18.4%) have the highest articulator rates. qo (0.1%), po (0.7%), lk (0.7%), ok/ot (0.8%) have the lowest.

t-initial PREFIXes consistently show elevated articulator rates. BARE and qo PREFIXes almost never take articulators. This extends C1418 (ARTICULATOR PREFIX-locked with BARE/qo exclusion).

### Finding 8: Cross-system distribution is nearly identical

Base character JSD:
- A-B: 0.011 (extremely similar)
- A-AZC: 0.040 (very similar)
- B-AZC: 0.046 (very similar)

Modifier character JSD:
- A-B: 0.037
- A-AZC: 0.058
- B-AZC: 0.073

PREFIX atoms are deployed with near-identical frequency distributions across all three systems. This parallels C1504 (modifier grammar universal, MOD JSD < 0.007) but at a coarser level. The base distribution is MORE stable than modifier distribution (JSD 0.011-0.046 vs 0.037-0.073), consistent with bases being the primary domain selectors.

---

## Constraint Summary

### C1534: PREFIX uses 15 characters in three-tier positional classification identical across all systems

PREFIX decomposes into 15 characters organized in three positional tiers: 7 MODIFIER atoms {c,d,f,p,q,s,y} at position-0, 2 BASE atoms {e,h} at position-final, and 6 DUAL atoms {a,k,l,o,r,t} at both positions. Character inventory is identical across all three systems (Jaccard=1.000 for all pairs). No PREFIX-exclusive characters exist. Extends C1218 with quantitative precision and cross-system confirmation. Extends C1499 (shared substrate) to PREFIX slot.

**Tier 2.** Scope: GLOBAL, PREFIX, atom, positional, inventory, MODIFIER, BASE, DUAL, cross-system.

### C1535: i-atom categorically excluded from PREFIX — iteration mechanism absent from channel selection

The atom 'i' (iteration/extensibility, C1197/C1204/C1205) is categorically absent from PREFIX position despite being present in MIDDLE MOD slot. Of the 6 MIDDLE MOD atoms {p,i,c,f,d,s}, only 'i' is excluded. PREFIX uses 15 of MIDDLE's 20 characters, missing {i,m,n,g,x}. The 5 excluded characters are: i (iteration MOD), m (TRANSITION TERM), n (CONTAINMENT TERM), g (rare), x (rare/coordinate). PREFIX cannot encode iteration depth — that information is exclusively carried in the MIDDLE slot via i/ii extensibility.

**Tier 2.** Scope: GLOBAL, PREFIX, MIDDLE, atom, i-atom, exclusion, iteration, extensibility.

### C1536: Base-to-HEAD selection V=0.478 — each base selects a distinct operational domain

Chi-squared=21,946.2, V=0.478. Base characters define operational domain channels: o-base=THERMAL (57% k-HEAD), h-base=STABILITY (66% e-HEAD), a-base=HEADLESS (96%), k/t-base=STABILITY+CONTAINMENT (49/43% e + 39/37% a), l-base=mixed THERMAL/STABILITY, r-base=CONTAINMENT/ARRANGEMENT, e-base=STABILITY+headless. V=0.478 is 89% of MIDDLE HEAD category specificity (V=0.511 per C1475). PREFIX base is a DOMAIN SELECTOR that is nearly as strong as MIDDLE HEAD for determining operational category.

**Tier 2.** Scope: GLOBAL, PREFIX, atom, base, HEAD, domain, selection, category, V=0.478.

### C1537: a-base is the universal headless gateway (94-96% headless regardless of modifier)

All a-base PREFIXes (da, sa, ka, ta) produce 94-96% headless MIDDLEs. Modifier identity has NO effect on headless rate for a-base PREFIXes (range 94.5-96.0%). This is the most deterministic base-to-HEAD mapping in the system. Connects C1491 (da-PREFIX near-exclusivity) to the broader a-base family: da is NOT special — ALL a-base PREFIXes are headless selectors. Extends C1524 (headless PREFIX exclusivity universal) with the atom-level mechanism.

**Tier 2.** Scope: GLOBAL, PREFIX, atom, base, a-base, headless, gateway, modifier-independent, da, sa, ka, ta.

### C1538: q-modifier uniquely activates THERMAL channel on o-base (64% k-HEAD vs 5-19% for other modifiers)

Within o-base PREFIXes, the q-modifier uniquely selects k-HEAD at 64.0% (+ 20.3% t-HEAD = 84.3% thermal/flow). All other modifiers paired with o-base produce 65-87% headless tokens with only 5-19% k-HEAD. q is the ONLY modifier that activates the thermal channel; other modifiers on o-base default to headless. qo is genuinely COMPOSITIONAL: q = thermal activation, o = domain base. This resolves qo's special status: it is not a lexicalized unit but a transparent modifier+base combination where q carries the thermal signal.

**Tier 2.** Scope: B, PREFIX, atom, modifier, q, o-base, THERMAL, k-HEAD, compositional, qo.

### C1539: Sister pair atom architecture — ok/ot is SAME_MOD while ch/sh and da/sa are SAME_BASE

Three known sister pairs decompose into two structural types at atom level: ch/sh and da/sa share BASE but differ in MODIFIER (SAME_BASE), while ok/ot shares MODIFIER (o) but differs in BASE (k vs t) (SAME_MOD). Despite structural asymmetry, all three pairs have HEAD JSD < 0.01 (content-equivalent). ok/ot has the SMALLEST JSD (0.0034) because k and t are terminal mirrors (C1478). Non-content differentiation: ch/sh diverge on suffix rate (53% vs 41%) and articulator rate (3.9% vs 13.2%); ok/ot and da/sa are near-identical on all non-content dimensions. SAME_BASE pairs differentiate on non-content axes; SAME_MOD pairs do not.

**Tier 2.** Scope: GLOBAL, PREFIX, atom, sister-pair, ch, sh, ok, ot, da, sa, SAME_BASE, SAME_MOD, HEAD, JSD, C408, C1478.

---

## Relationship to Existing Constraints

| Existing | Relationship | Detail |
|----------|-------------|--------|
| C1218 | **REFINED** | Three-tier classification confirmed with exact quantitative boundaries |
| C1219 | **CONFIRMED** | Base-to-HEAD selection V=0.478 confirms base determines MIDDLE content |
| C1220 | **EXTENDED** | Modifier effects now quantified per base: a-base modifier-insensitive, h-base modifier-sensitive |
| C1394 | **CONNECTED** | PREFIX slot uses 15/20 MIDDLE atoms, missing {i,m,n,g,x} |
| C1475 | **PARALLELED** | PREFIX base V=0.478 parallels MIDDLE HEAD V=0.511 at 89% strength |
| C1478 | **CONFIRMED** | k/t as terminal mirrors explains ok/ot minimal JSD |
| C1491 | **GENERALIZED** | da exclusivity is part of broader a-base headless gateway |
| C1499 | **EXTENDED** | Shared substrate now confirmed at PREFIX atom level (15/20 chars, Jaccard=0.75) |
| C1504 | **EXTENDED** | Cross-system modifier universality confirmed in PREFIX (JSD 0.037-0.073) |
| C1524 | **MECHANIZED** | Universal headless PREFIX exclusivity explained by a-base gateway |

## Expert Predictions Assessment

The expert-advisor predicted PREFIX is NOT HEAD/MOD/TERM like MIDDLE but rather an instruction header field (channel selector + register framing + domain family latch). This is **CONFIRMED**: PREFIX has a MODIFIER+BASE structure, not HEAD+MOD+TERM. The base is a domain selector (channel), and modifiers frame variant selection within that domain. The i-exclusion confirms PREFIX cannot encode iteration depth (which is a MIDDLE-internal concern, not a channel-selection concern).

## Summary

PREFIX has a distinct two-tier compositional grammar (MODIFIER+BASE) using 15 of the 20 manuscript atoms. The base character is a domain selector (V=0.478) nearly as powerful as MIDDLE HEAD (V=0.511). The a-base is a categorical headless gateway. The q-modifier uniquely activates thermal operation when paired with o-base. Sister pairs decompose into SAME_BASE (ch/sh, da/sa) and SAME_MOD (ok/ot) structural types, both content-equivalent but differentially sensitive to non-content axes. The system is cross-system universal (Jaccard=1.000). The 5 excluded atoms {i,m,n,g,x} reveal that PREFIX cannot encode iteration depth, transition closure, containment binding, or the rare coordinate/structural atoms — these are MIDDLE-internal concerns that the channel selector does not touch.
