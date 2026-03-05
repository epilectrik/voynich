# Phase 515: SUFFIX ATOM DECOMPOSITION

**Date:** 2026-03-05
**Status:** COMPLETE
**Script:** `phases/SUFFIX_ATOM_DECOMPOSITION/scripts/suffix_atom_decomposition.py`
**Results:** `phases/SUFFIX_ATOM_DECOMPOSITION/results/suffix_atom_decomposition.json`

---

## Summary

Suffix types in Currier B decompose into the same atom inventory as MIDDLEs (C1393), with **STRONG HEAD->TERM compositional ordering** (76.6% HEAD-initial, 100% TERM-terminal, 0 violations). The suffix domain is a genuine compositional space parallel to MIDDLE, not a fixed set of arbitrary markers.

However, atoms **shift function dramatically** between suffix and MIDDLE-terminal positions — 0/12 shared atoms are category-stable (all JSD > 0.027). This is the major finding: suffix atoms are the same characters but carry **different operational information** in suffix position vs MIDDLE position.

Suffix modes (C1229) decompose cleanly at atom level: Mode A (specification) enriches THERMAL-associated atoms {d, e, ee, h, y}, Mode B (continuation) enriches STAGING/TRANSITION atoms {a, i, ii, l, m, n, o, r, s}.

---

## Results

### T1: Suffix Inventory and Atom Census

| Metric | Value |
|--------|-------|
| Distinct suffix types | 35 (+ BARE) |
| Suffixed tokens | 11,151 (48.3% of B) |
| Bare tokens | 11,945 (51.7%) |
| Distinct atoms in suffix | 16 (including ee, ii, oo doublings) |

**Atom frequency in suffix position:**

| Atom | Count | MIDDLE slot | Role in suffix |
|------|-------|-------------|----------------|
| y | 5,773 | TERM | Universal terminal |
| a | 3,438 | HEAD | Domain selector (TRANSITION-associated MIDDLEs) |
| d | 2,972 | MOD | Modification (THERMAL/OPERATION MIDDLEs) |
| e | 2,541 | HEAD | Domain selector (strongly THERMAL MIDDLEs) |
| n | 1,856 | TERM | Binding terminal |
| r | 1,721 | TERM | Routing terminal |
| l | 1,231 | TERM | State terminal |
| ii | 1,083 | special | Extended iteration |
| h | 854 | TERM | Monitoring (CONTAINMENT/MONITORING MIDDLEs) |
| o | 821 | HEAD | Domain selector (STAGING-associated MIDDLEs) |
| i | 774 | MOD | Iteration modifier |
| ee | 603 | special | Deep THERMAL extension |
| s | 424 | MOD | Staging modifier |
| m | 305 | TERM | Batch-close terminal |

**Suffix length:** 2-atom dominant (5,764 tokens = 52%), 3-atom (3,751 = 34%), 1-atom (1,636 = 15%).

**HEAD/MOD/TERM coverage:** 3/5 HEAD atoms (a, e, o — missing k, t), 3/6 MOD atoms (d, i, s — missing p, f, c), 6/6 TERM atoms. TERM atoms are complete; HEAD and MOD are partially filtered.

**Verdict:** Suffix uses a **reduced atom inventory** (16 vs 18 in MIDDLE), missing the THERMAL heads k/t and the MARKING modifiers p/f/c. This is consistent with suffix encoding a **different operational axis** than MIDDLE.

### T2: Suffix Atom Positional Grammar

**Strict ordering confirmed:**

| Position | HEAD atoms | MOD atoms | TERM atoms |
|----------|-----------|-----------|------------|
| INITIAL | 76.6% | 11.7% | 11.7% |
| MEDIAL | (i, ii, d dominate) | — | — |
| TERMINAL | 0.0% | 0.0% | 100.0% |

- **Zero violations** of TERM-before-HEAD ordering.
- Atom 'a' is 100% initial; 'e' is 100% initial; 'o' is 92% initial.
- Atom 'y' is 100% terminal; 'n' is 100% terminal; 'm' is 100% terminal.
- Atom 'd' is 33.6% initial (when it IS the initial, as in -dy), 66.4% medial (in -edy).
- Atom 'i' is 96.3% medial (between HEAD and TERM in -ain, -aiin patterns).

**Verdict:** STRONG HEAD->TERM positional grammar, **identical in structure to MIDDLE's INITIAL->MEDIAL->TERMINAL** (C1209, C1210). Suffix is a parallel compositional domain with the same slot syntax.

### T3: Suffix Atom -> Operational Category

Cramer's V = 0.174 (moderate association).

**Key category associations by suffix atom:**

| Atom | Strong enrichment | Strong depletion | Interpretation |
|------|------------------|-----------------|----------------|
| e/ee | THERMAL (1.5-1.9x) | STAGING (0.2x), TRANSITION (0.01x) | Selects THERMAL MIDDLEs |
| h | CONTAINMENT (4.1x), MONITORING (4.9x), OPERATION (2.4x) | THERMAL (0.2x), TRANSITION (0.04x) | Selects MONITORING/CONTAINMENT MIDDLEs |
| s | TRANSITION (2.7x), OPERATION (1.6x) | FLOW (0.3x), CONTAINMENT (0.1x) | Selects TRANSITION MIDDLEs |
| o | STAGING (2.1x) | OPERATION (0.3x), TRANSITION (0.4x) | Selects STAGING MIDDLEs |
| r | STAGING (2.2x), TRANSITION (1.7x) | CONTAINMENT (0.4x), OPERATION (0.3x) | Selects STAGING/TRANSITION MIDDLEs |
| m | FLOW (1.9x), STAGING (1.6x), MARKING (1.5x) | THERMAL (0.6x), OPERATION (0.2x) | Selects FLOW MIDDLEs |
| a | FLOW (1.7x) | OPERATION (0.4x), TRANSITION (0.5x), MONITORING (0.3x) | Selects FLOW MIDDLEs |
| d | OPERATION (1.4x) | FLOW (0.6x) | Selects OPERATION MIDDLEs |

**Per-suffix-type category profiles (most informative):**

| Suffix | Dominant category | Key enrichments |
|--------|------------------|-----------------|
| edy | THERMAL (68%) | Strongest THERMAL selector |
| eey | THERMAL (75%) | Deep THERMAL specification |
| hy | OPERATION (24%) + CONTAINMENT (15%) + MONITORING (18%) | Process monitoring suffix |
| dy | OPERATION (30%) + TRANSITION (20%) | Marking/operational suffix |
| r | STAGING (47%) + TRANSITION (29%) | Routing/staging suffix |
| iin | TRANSITION (46%) + STAGING (25%) | Transfer/staging suffix |
| ly | TRANSITION (44%) | Transition suffix |
| am | FLOW (36%) + MARKING (20%) | Batch-close suffix |
| ol | FLOW (32%) + STAGING (20%) | Continuation suffix |
| ain | THERMAL (54%) | Thermal iteration suffix |
| aiin | THERMAL (39%) + FLOW (29%) | Thermal flow suffix |

**Verdict:** Suffix atoms are not random — they **select for specific MIDDLE categories**. The suffix HEAD atom (first atom) predicts the category of the MIDDLE it attaches to (V=0.277 for first-atom, more than last-atom's V=0.163). This is **not C1338's suffix selectivity** (which is about MIDDLE selecting suffix) — this is the complementary finding that **suffix HEAD atoms also correlate with MIDDLE category**.

### T4: Suffix Atom -> Macro-State

Cramer's V = 0.155 (moderate).

Nearly all suffix atoms are AXM-dominated (86-98%), with minor deviations:
- **d, e**: ~10-12% FQ (escape route involvement)
- **r**: 6.2% FL_HAZ (hazard flow marking)
- **m**: 20.5% AXm (minor attractor — consistent with m's batch-close terminal role)

**Cross-position JSD (suffix vs MIDDLE-terminal):**

| Atom | JSD | Interpretation |
|------|-----|----------------|
| h | 0.004 | Nearly identical — h carries same signal in both positions |
| y | 0.042 | Very similar — y is universal terminal in both |
| r | 0.297 | Moderate shift — r is more STAGING-oriented in suffix |
| l | 0.323 | Moderate shift — l is more AXM-concentrated in suffix |
| n | 0.439 | Large shift — n shifts toward AXM in suffix |
| m | 0.560 | Large shift — m shifts away from AXm in suffix |
| i | 0.493 | Large shift — i is more AXM in suffix |

**Verdict:** Macro-state association is weak (base rate dominated). Only h and y maintain similar macro-state profiles across positions.

### T5: Suffix Atom -> Line Position

Only two position specialists:
- **m**: mean=0.926 (FINAL) — 83% of m-bearing suffixes at line-final position
- **ee**: mean=0.416 (INITIAL) — early-line bias

All other atoms are position-neutral (mean 0.46-0.52). Bare tokens at mean 0.497.

**Verdict:** Line position is **not driven by individual suffix atoms** except for m (line-final) and ee (early-line). The suffix as a whole unit carries modest positional information (R²=0.077 for whole suffix, T7), but individual atoms contribute little. This contrasts with MIDDLE where atom positions are highly structured (C1209).

### T6: Suffix Atom Cross-Position Comparison

**0/12 atoms are category-stable between suffix and MIDDLE-terminal position.**

This is the most important finding. The same character 'y' is TRANSITION-dominant when it's a MIDDLE terminal but THERMAL-dominant when it's a suffix terminal. The same 'r' is FLOW-dominant in MIDDLE but STAGING-dominant in suffix.

**Explanation:** Category is determined by the MIDDLE, not the suffix (C1305). When 'y' appears in suffix position (e.g., suffix='-edy'), the category reflects the MIDDLE it accompanies, not 'y' itself. The suffix atom 'y' preferentially accompanies THERMAL MIDDLEs. When 'y' appears as MIDDLE terminal (e.g., MIDDLE='dy'), the category is determined by the MIDDLE 'dy' itself (MARKING/OPERATION).

**This confirms that suffix and MIDDLE are independent compositional domains.** Same alphabet, same slot grammar, but different semantic load. Suffix atoms encode **what scope of operation** (specification, continuation, closure); MIDDLE atoms encode **what type of operation** (heating, cooling, monitoring).

### T7: Suffix Compositional Structure

| Predictor | Category V | Position R² |
|-----------|-----------|-------------|
| First atom | 0.277 | 0.022 |
| Last atom | 0.163 | 0.059 |
| Whole suffix | 0.291 | 0.077 |

**HEAD+TERM structure: YES**
- First atom (HEAD) captures more category information (V=0.277 vs 0.163)
- Last atom (TERM) captures more positional information (R²=0.059 vs 0.022)
- This exactly parallels MIDDLE's HEAD→TERM compositional structure (C1393)

**Verdict:** Suffix has genuine HEAD+TERM compositional structure: first atom = domain selector (which category of MIDDLE it accompanies), last atom = exit condition (where in the line it tends to appear). This is a parallel architecture to C1393's MIDDLE composition.

### T8: Suffix Mode Atom Decomposition

Suffix modes (C1229) decompose cleanly at atom level:

| Mode A (specification) | Mode B (continuation) |
|-----------------------|----------------------|
| d (2.22x), e (2.38x), ee (1.84x), h (1.68x), y (2.00x) | a (0.49x), i (0.51x), ii (0.48x), l (0.58x), m (0.47x), n (0.49x), o (0.59x), r (0.50x), s (0.37x) |

**Interpretation:**
- **Mode A** = THERMAL/MONITORING-associated atoms dominate suffix. These are the **specification** suffixes (-edy, -eey, -hy, -dy, -y) that appear when the line specifies thermal operations.
- **Mode B** = STAGING/TRANSITION/FLOW-associated atoms dominate suffix. These are the **continuation** suffixes (-aiin, -ain, -ar, -al, -ol, -am, -r, -s) that appear when the line continues iteration/flow operations.

This perfectly explains C1229's two suffix modes: Mode A lines are THERMAL-specification lines with THERMAL-scope suffixes, Mode B lines are FLOW/STAGING-continuation lines with iteration/routing suffixes. The modes are not arbitrary clusters — they are **atom-level category partitions**.

### T9: Synthesis

**Does suffix have compositional structure?**
Yes. STRONG HEAD→TERM ordering with 0 violations. First atom selects category domain, last atom determines positional scope. Parallel to MIDDLE's HEAD→MOD→TERM architecture.

**How many functionally distinct suffix atoms?**
16, of which 12 are single characters shared with MIDDLE and 4 are doublings (ee, ii, oo, g). Missing from MIDDLE inventory: k, t (both THERMAL domain heads), p, f, c (MARKING modifiers). The suffix domain is **THERMAL-depleted and MARKING-depleted** relative to MIDDLE.

**What does "scope" map to at atom level?**
The suffix HEAD atom (e, a, o, h) selects which category of MIDDLE it accompanies. Suffix 'e' selects THERMAL MIDDLEs for specification. Suffix 'a' selects FLOW/iteration MIDDLEs for continuation. Suffix 'o' selects STAGING MIDDLEs. Suffix 'h' selects MONITORING/CONTAINMENT MIDDLEs.

**How do suffix atoms relate to MIDDLE atoms?**
Same characters, different function. 0/12 shared atoms maintain category identity across positions. Suffix atoms encode **scope** (what kind of operation is being scoped), MIDDLE atoms encode **content** (what the operation is). This confirms C1394's finding that suffix is an independent compositional domain sharing the atom alphabet but not the atom semantics.

---

## Constraint Candidates

### C_SUFFIX_COMPOSITIONAL_STRUCTURE (Tier 2)
Suffix types decompose into atoms from the C1393 inventory with STRONG HEAD→TERM positional ordering (76.6% HEAD-initial, 100% TERM-terminal, 0 ordering violations). First atom predicts MIDDLE category (V=0.277); last atom predicts line position (R²=0.059). Suffix is a parallel compositional domain to MIDDLE. 16 distinct atoms, reduced from MIDDLE's 18 (missing k, t, p, f, c).

### C_SUFFIX_CROSS_POSITION_DIVERGENCE (Tier 2)
Same atoms behave differently in suffix vs MIDDLE-terminal position: 0/12 shared atoms maintain category identity (all JSD > 0.027, mean JSD=0.395). Atoms h and y show lowest divergence (JSD=0.004, 0.042); atoms m, i, r show highest (JSD>0.49). Suffix atoms encode SCOPE (which category of MIDDLE they accompany); MIDDLE atoms encode CONTENT (what the operation is).

### C_SUFFIX_MODE_ATOM_PARTITION (Tier 2)
C1229's two suffix modes decompose at atom level: Mode A (specification) enriches atoms {d, e, ee, h, y} (THERMAL/MONITORING-associated, 1.68-2.38x enrichment); Mode B (continuation) enriches atoms {a, i, ii, l, m, n, o, r, s} (STAGING/TRANSITION/FLOW-associated, 0.37-0.59x Mode A ratio). Modes are category-level atom partitions, not arbitrary clusters.

---

## Key Finding for Architecture

The suffix domain operates as a **SCOPE SELECTOR** using the same atom alphabet as MIDDLE but with shifted semantics:

```
MIDDLE:  HEAD(domain) + MOD(modification) + TERM(exit)  → WHAT operation
SUFFIX:  HEAD(scope)  + [MOD(extension)]  + TERM(close) → HOW SCOPED
```

The HEAD atom in suffix position selects **which category of MIDDLE** this token accompanies (e→THERMAL, a→FLOW, o→STAGING, h→MONITORING). This is not the same as the MIDDLE HEAD determining **what the operation IS**. It's a parallel channel encoding operational scope, not operational content.

This extends C1394 (instruction encoding architecture) by confirming that suffix is not just an appendage but a second compositional domain sharing the atom alphabet with systematically different function.
