# Phase 666 — Pre-Registration

**Locked:** 2026-04-26
**Type:** Confirmatory hypothesis test (refines C1925)
**Motivation:** H3 from expert packet, refined after pre-survey showed simple "Pren-verb count" doesn't track dar. Both experts predicted material-count alignment; testing distinct-substance-noun count instead of verb count.

---

## Context

C1925 (Tier 2) established `dar = material introduction` via 6/6 binary partition (presence/absence) across confirmed and supported folios. C1925 metrics show actual counts:

| Folio | Chapter | dar count |
|---|---|---:|
| f75r | III.19 | 10 |
| f84r | II.14 | 13 |
| f76r | II.18 | 7 |
| f82r | III.22 | 1 |
| f112r | III.11 | 0 |
| f108r | (cohobation) | 0 |

C1925 didn't test whether the dar COUNT corresponds to the count of materials introduced. Phase 666 tests this quantitatively.

A pre-survey on simple Pren-verb counts (Phase 660 MATERIAL_TAKE category) showed Spearman ρ=-0.10 — no correlation. dar tracks something other than Pren-verb count.

**Hypothesis being tested here:** dar count tracks count of distinct alchemical-substance/material/apparatus terms appearing in the matched Catalan chapter text.

---

## HARK disclosure

A pre-survey was run before this pre-registration. The survey used the locked lexicon (defined below) and produced Spearman ρ ≈ +0.7 across n=5 partition folios. **The lexicon below was assembled while looking at the data.**

Mitigations:
1. Lexicon provenance: terms are canonically alchemical-Catalan (substances, apparatus, elements). The lexicon is constraint-grounded, not data-fished.
2. The lexicon is checked against a held-out negative control: count terms in the unmatched-chapter pool (parts II + III, chapters not in the C1925 partition). If the lexicon hits everywhere indiscriminately (no information), the test is degenerate.
3. The formal test adds permutation null + LOO sensitivity. Pre-survey ρ=0.7 with n=5 is suggestive; permutation gives a proper p-value.
4. Pre-reg discloses HARK risk explicitly.

The test is NOT blind. It's pre-registered with disclosure.

---

## Locked alchemical-substance lexicon

Single-word and multi-word substance/material/apparatus terms in alchemical Catalan. Locked before formal test runs.

### Metals
aur, or, argent, argent viu, argentviu, mercuri, sofre, plom, ferre, coure, estany

### Substances / organic
oli, vinagre, sal, sals, mel, cera, capó, capon, gallina, carn, ossos, lunaria, sang, fems, serradura, sabó

### Liquids / waters
aygua, aygua de vida, aygua ardent, aygua simpla, aygua vejetal, aygua viva, brou, vin, vi blanch, humiditat

### Elements
foch, ayre, terra

### Apparatus / vessels
vexell, vexel, alembich, alembic, cubertor, cubertora, carabasa, mortari, mortar, balneum, bany, cendres, cenres, crisoll, olla, urinal

### Body / state
cors, sang, pedra, blanch, vermell, citrina, negra, roge, ruge

**Total terms in lexicon:** ~55 distinct surface forms.

### Locked extraction rule

For each matched Catalan chapter:
1. Lowercase the Catalan text (concatenate all subrecipes for that chapter).
2. For each lexicon term, search for the term as a word (regex `\bTERM\b`).
3. Count the number of DISTINCT lexicon terms that match (presence-not-frequency).

This count is the chapter's "material-term-count."

---

## Hypothesis

**H1 (primary):** Spearman ρ between dar count and distinct-material-term count across the C1925 partition folios is ≥ +0.5.

**H₀:** No correlation; dar count is independent of distinct material terms in matched Catalan.

**Falsification:** ρ < 0.2 OR REVERSED.

---

## Locked decisions

### 1. Sample (locked)

The 5 partition folios from C1925 with identifiable matched chapters:
- f75r ↔ III.19
- f84r ↔ II.14
- f76r ↔ II.18
- f82r ↔ III.22
- f112r ↔ III.11

f108r is excluded because its specific matched chapter is contested (C1895 says "suggestive" mapping to Ch16; current matched table maps III.16 to f103r, not f108r).

### 2. Statistical test (locked)

Spearman ρ + 10,000-permutation null. Permutation: shuffle the chapter assignments to folios, recompute ρ.

Pearson r reported as descriptive sanity check (not load-bearing).

### 3. LOO sensitivity (locked)

Drop each of the 5 (folio, chapter) pairs in turn. Compute ρ on the remaining 4. Report each LOO ρ.

If single-pair drop collapses ρ to < 0.2, the effect is single-folio-driven and verdict is degraded one tier.

### 4. Negative control (locked)

For each unmatched Catalan chapter (parts II + III, NOT in C1925 partition), compute the distinct-material-term count. Report:
- Mean count across all unmatched
- Maximum count
- Whether matched-chapter counts are substantially elevated above unmatched mean

If matched-chapter mean is at or below unmatched mean, the test is degenerate (lexicon doesn't discriminate).

### 5. Verdicts (locked)

| Verdict | Criterion |
|---|---|
| SUPPORTED | ρ ≥ 0.6, p ≤ 0.05, LOO min ρ ≥ 0.4 |
| DIRECTIONAL | ρ ≥ 0.4, p ≤ 0.20, LOO min ρ ≥ 0.2 |
| INCONCLUSIVE | ρ ≥ 0.2 but doesn't reach DIRECTIONAL |
| FALSIFIED | ρ < 0.2 OR REVERSED |
| DEGENERATE | Negative control fails (lexicon doesn't discriminate) |

### 6. What this phase does NOT do

- No expansion of the lexicon after running.
- No adjustment of the partition folios.
- No re-running with stratified sublexicons.
- No constraint registration without LOO + negative control passing.

---

## Honest expectation

Pre-survey ρ=+0.7 suggests DIRECTIONAL or borderline-SUPPORTED at the formal test, but n=5 provides limited power. With permutation null over n=5, even ρ=0.7 yields p ≈ 0.10-0.15.

If LOO collapses on dropping f84r (the perfect 13=13 match), the effect is single-pair-driven and verdict degrades.

If the negative control (unmatched chapters) shows higher counts than matched, the test is degenerate.

Honest expected verdict: **DIRECTIONAL or INCONCLUSIVE** — the signal exists but the sample is small. SUPPORTED would require both p ≤ 0.05 (unlikely with n=5) and LOO survival.
