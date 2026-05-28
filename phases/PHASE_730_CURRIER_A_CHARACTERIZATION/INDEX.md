# Phase 730 — Currier A Characterization (Linker / Plant / Section / Within-A)

**Status:** COMPLETE
**Date:** 2026-05-28
**Scope:** Multi-test Currier A pivot. Four discriminating tests run after expert consultation; three Tier 2/3 registrations + one framework-as-null trap caught before registration.

---

## Motivation

The project has tested Currier B (recipes/execution) extensively. Currier A remains less characterized. The session pivoted to A to ask: what kind of text is it, structurally? User hypothesis: "operational lab notes."

Expert-advisor + crazy-expert recommended four discriminating tests, three of which produced registerable findings and one of which was killed by proper controls — exactly the discrimination ratio the procedural-ceiling memory predicts.

---

## Tests Run

### Test 1 — Linker topology vs content (registers as C2057)

**Script:** `scripts/_currier_a_linker_test.py` + `scripts/_a_linker_atom_test.py`

C835 established 4 RI linkers (12 edges). Test asked: is linker non-randomness structural-only or content-bearing?

| Hypothesis | Result |
|---|---|
| H1 (topology non-random vs degree-preserving null) | **PASS** |
| H5 (cluster structure) | **PASS** |
| H2/H3/H4 (content-discrimination) | **FAIL** |
| Atom-specificity test (5 atom-level subtests) | **0/5 PASS** |

**Verdict:** Linkers are structural-only. Topology marks connections without carrying atom-level semantic content.

### Test 2 — o-HEAD rate vs plant morphological complexity (registers as C2058)

**Script:** `scripts/_a_ohead_plant_v2.py`

Pre-registered (locked before running): if A's o-HEAD "arrange" vocabulary encodes botanical spatial structure, folios with more-complex plant illustrations should have higher o-HEAD rate.

- N=29 Currier A herbal folios with PIAA blind morphological "Key Features" descriptions
- Complexity proxy: count of distinct plant-structure terms
- Spearman ρ(complexity, o-rate) = **+0.031, p = 0.87**
- Token-count confound: ρ(tokens, o-rate) = +0.41, p = 0.027
- **Partial correlation controlling for token count: ρ = −0.057, p = 0.77**

**Verdict:** Falsified. o-HEAD arrangement vocabulary does NOT track plant visual structural complexity (via this proxy). Scope of falsification: spatial-complexity-via-tag-count proxy. Does NOT falsify botanical-category-coded or use-coded interpretations.

(Note: an earlier attempt `_a_oheadplant_test.py` used PPC's morphology classification which turned out to be Currier B folios — wrong system. PIAA covered the actual Currier A herbal folios. The error was caught and corrected before locking the result.)

### Test 3 — Section H/P HEAD-domain profile (registers as C2059)

**Script:** `scripts/_a_arrange_semantics.py` + `scripts/_read_currier_a.py`

Currier A HEAD distribution by section (H = herbal, P = pharma, T = text):

| Section | o-HEAD | e-HEAD | k-HEAD | a-HEAD | Character |
|---|---|---|---|---|---|
| H (herbal) | **26.2%** | 10.9% | 4.6% | 5.8% | Arrangement-dominant |
| P (pharma) | 21.1% | **28.0%** | 8.1% | 6.4% | Thermal-recovery — B-like |
| T (text) | 20.6% | 13.4% | 8.8% | 21.7% | Yield+arrange co-dominant |

Currier B comparison: e-HEAD 40.4%, o-HEAD 16.1% (thermal-dominant).

Section P recovers a thermal HEAD-profile (e-dominant) inside Currier A. Per-section breakdown not articulated by C1266 (which used atom-cluster framing). Refines C1266 at HEAD-domain resolution.

**Verdict:** Real section-internal architectural fact. Tier 3 refinement (interpretation pending — operational reading "P is the pharma execution context" is framework-echo-suspect).

### Test 4 — Within-A action-form test (NO REGISTRATION — framework-as-null catch)

**Scripts:** `scripts/_a_state_action_test.py`, `scripts/_within_a_action_test.py`, `scripts/_b_side_mirror.py`

The original "Finding 1" framing: A=95% state-form, B=21% action-form via dy-terminal asymmetry. Per-MIDDLE: `ke` 0% dy in A, 67% dy in B. Aggregate passed within-folio shuffle null at p=0.000.

**Crazy-expert framework-echo flag:** if A's grammar architecturally excludes dy-suffix (C234 + C239 + C1395), the "0% dy in A" is tautological — restating grammar architecture, not finding a deployment choice.

**Within-A action-form discriminating test (pre-registered):**

- H1 PASS at 38.9% — A IS grammatically capable of dy (21 of 54 dy-eligible MIDDLEs appear in dy-form somewhere in A). Architectural-tautology hypothesis falsified.
- H2 FAIL at p=0.51 — line-position-within-paragraph does NOT predict dy-rate.
- Pre-registered verdict: AMBIGUOUS.

**Post-hoc observation** in the data: dy-permissive A MIDDLEs all contained `o`; dy-suppressed ones didn't. User glossed: "A=setup, B=execute via arrangement-selective completion."

**Expert audit of proposed pre-registered test on o-content** flagged six flaws:
1. Post-hoc fig leaf (test designed after seeing pattern)
2. Frequency confound + structural-domain confound
3. B-side mirror missing (load-bearing)
4. C1557 cross-check unaddressed
5. HEAD vs ANY predicate ambiguity
6. Framework-echo (no new mechanism beyond C1395+C1502+C1556+C1559)

**B-side mirror + terminal-atom-matched permutation null:**

| Test | Result |
|---|---|
| B dy-rate on o-MIDDLEs vs non-o (Mann-Whitney one-sided) | **p=0.62** (B symmetric — A asymmetry IS A-specific) |
| A o vs non-o (raw, Mann-Whitney) | p=0.013 |
| **Terminal-atom-matched permutation null** | **p=0.71 (effect collapses)** |
| o-HEAD MIDDLEs A dy-rate | 0.026 (suppressed) |
| o-non-HEAD MIDDLEs A dy-rate | 0.420 (permitted) |
| no-o MIDDLEs A dy-rate | 0.040 |

The o-content effect is purely terminal-atom artifact. MIDDLEs ending in `o` or `l` are dy-permitted in A; MIDDLEs ending in `e` or `h` are suppressed — regardless of o-content elsewhere. This is terminal-atom selection (C1485 HEAD×TERM affinity extended), not arrangement-selection.

**Verdict:** No registration. The o-selectivity / setup-execute mechanism story FAILED expert audit + B-mirror + terminal-atom null. Residual observation (A gates dy by terminal-atom; B does not) is post-hoc; needs fresh pre-registration on held-out scope before any future Tier 2 consideration.

---

## Registered Constraints

| Constraint | Tier | Scope | Verdict |
|---|---|---|---|
| C2057 | 2 | A:RI:linkers | Linker topology structural-only — 0/5 atom-specificity tests pass, 4-of-5 topology tests pass |
| C2058 | 2 (falsification) | A:H:o-HEAD | o-HEAD rate does NOT track plant-spatial-complexity (PIAA proxy, N=29, partial ρ=−0.06) |
| C2059 | 3 | A:section:HEAD-domain | Section P recovers thermal e-HEAD profile (28%) inside A; sections diverge at HEAD level |

## Findings NOT Registered (framework-as-null catches)

- **State/action o-selectivity mechanism** — F1 reframed away from registration after experts caught framework-echo. Pre-registered H1/H2 verdict: AMBIGUOUS. Post-hoc o-pattern killed by terminal-atom-matched permutation (p=0.71).
- **Terminal-atom gating of A's dy (residual observation)** — real but post-hoc; tabled for fresh pre-registration tomorrow.

---

## Methodology Notes

This phase produced **3 registrations + 1 clean framework-echo catch + 1 corrected execution error** (PPC-vs-PIAA system mismatch). All four expert-audit-flagged failure modes for the o-selectivity claim materialized in the actual data — confirming the audit's value.

Framework-as-null discipline working as designed:
- F4 (botanical) — null protects against future drift toward "o-HEAD = botanical depiction"
- F3 (linker) — clean asymmetric topology-passes-content-fails result
- F1 — would have registered an over-clean operational gloss if not for expert intervention

The within-A action-form trap is **trap pattern #5 in 2026-05**, following k-e-depth thermal regimes, triple-i iteration encoding, hh intense-monitoring, and f66r-glossary. All built clean operational stories with surface evidence; all failed expert-validated controls. Pattern is now an established procedural signature.

---

## Scripts

| Script | Purpose |
|---|---|
| `scripts/_a_arrange_semantics.py` | Per-folio o-HEAD distribution, section breakdown |
| `scripts/_read_currier_a.py` | A characterization summary (state/action %, HEAD profile) |
| `scripts/_b_head_dist.py` | B HEAD distribution baseline for comparison |
| `scripts/_currier_a_linker_test.py` | Linker topology H1-H5 |
| `scripts/_a_linker_atom_test.py` | Linker atom-specificity (5 subtests) |
| `scripts/_a_state_action_test.py` | Original state/action S1-S5 test |
| `scripts/_a_ohead_plant_v2.py` | o-HEAD vs plant complexity (PIAA, N=29) |
| `scripts/_a_oheadplant_test.py` | Earlier (incorrect-system) PPC version |
| `scripts/_within_a_action_test.py` | Within-A dy-eligibility H1+H2 |
| `scripts/_b_side_mirror.py` | B-side mirror + terminal-atom-matched null |

---

## Cross-Reference

- C1266 (Section atom-cluster differentiation) — refined by C2059 at HEAD-domain
- C835 (RI linker mechanism) — refined by C2057 with content-emptiness
- C138/C140 (illustrations epiphenomenal) — extended by C2058
- C1394 (HEAD+MOD+TERM atom decomposition) — used throughout
- C1395 (state/action terminal split) — tested but NOT extended (F1 reframed away)
- C1485, C1487, C1440-C1445 (terminal-atom mechanics) — implicated in killed o-selectivity story
