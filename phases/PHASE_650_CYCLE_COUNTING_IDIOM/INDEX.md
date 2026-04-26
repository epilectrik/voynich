# Phase 650: Cycle-Counting Idiom

**Status:** COMPLETE
**Date:** 2026-04-26
**Constraints registered:** C1965 (Tier 3, scope-restricted to f75r)
**Refinement note:** C1394 MOD-atom subtypes

---

## Question

Phase 649 closed with C1963 (qo as paragraph operational opener, 77.9% mean precedence) and C1964 (within-line interleaving dominance). The user observed that f75r's L37-L38 region encodes the recipe's ×9 redistillation count as a corpus-singular qok-cycle run, with operational logic: "1 initial distillation + 9 redistillations = 10 fire-events." Phase 650 tests whether this **cycle-counting idiom** generalizes across the matched-recipe corpus.

---

## Method

### Test rounds (incremental refinement)

**Round 1 (s1):** Per-line qok-class clusters matching recipe iteration counts. Permutation null at 83.9% — falsified at this granularity.

**Round 2 (s2):** Sequential qok-runs with gap tolerance. Identified f75r corpus-singular run of 8 (with max_gap=1) at L37-L38 (p=0.04). Other matched recipes flat.

**Round 3 (s3):** User correction — the proper unit is the **closed cycle** (qok+...+`-dy`), not qok-class. Tokens like `qokey` lack `-dy` closure (transitional sub-state, not complete cycle). Tested at paragraph level — too coarse: f75r P0 has 17 closed cycles total, hiding the L36-L38 sub-block.

**Round 4 (s4):** Line-window closed-cycle count. Correct granularity: small (1-5 line) operational blocks. Tests both `n` and `n+1` interpretations (`n+1` accounts for "1 initial + N redistillations").

### Closed-cycle filter

A closed cycle = token matching `qok.*dy`:
- **Includes:** qokedy, qokeedy, qokchdy, qokechdy (closed-with-`-dy`)
- **Excludes:** qokey, qokar, qokain, qoky (no `-dy` closure → transitional/sub-state)

Per F-B-007 / C1735, the `-dy` suffix is closure/end. A token matching qok+...+dy represents a **complete fire-bounded operational pass**.

---

## Findings

### Finding 1: f75r encodes both recipe phases at line-localized resolution

The recipe specifies two phases: *"per **quatre vegades** aliter broicé e triblé; e aprés **ix vegades**"* (×4 first, then ×9).

| Phase | Recipe | Voynich encoding | Corpus rarity |
|---|---|---|---|
| ×4 | "× 4 vegades" | **L13: 4 closed cycles in 1 line** (4-qokedy identical-token run, per memory note) | ~7 other 1-line windows in corpus with 4 cycles |
| ×9 (n+1) | "× 9 vegades" + initial | **L36-L38: 10 closed cycles in 3-line window** | **Corpus-singular (1 such window in all of Currier B)** |
| ×9 (n alone) | "× 9 vegades" | L37-L38: 9 closed cycles in 2-line window | **Corpus-singular** |

The ×9 anchor is **corpus-singular at both n and n+1 interpretations**. Random distributions of qok-class tokens in the corpus produce 9-or-10 cycle 2-3 line windows essentially nowhere else.

### Finding 2: Per-cycle MOD-atom annotation marks test cycles at phase boundary

The 10-cycle L36-L38 cluster is composed of:

| Cycle | Token | MOD atoms | Reading |
|---|---|---|---|
| 1 | qokeedy | k + e + e | initial pass at degree-2 (gentle/balneum) |
| 2 | qokedy | k + e | degree-1 routine |
| 3 | qokedy | k + e | degree-1 routine |
| **4** | **qokchdy** | **k + ch** | **raw heat (no e) + TEST (ch)** |
| **5** | **qokechdy** | **k + e + ch** | **degree-1 + TEST (ch)** |
| 6 | qokeedy | k + e + e | degree-2 routine |
| 7 | qokeedy | k + e + e | degree-2 routine |
| 8 | qokedy | k + e | degree-1 routine |
| 9 | qokedy | k + e | degree-1 routine |
| 10 | qokeedy | k + e + e | degree-2 routine |

The two `ch`-marked cycles (4 and 5) sit **exactly at the recipe's phase boundary**: cycle 4 transitions from the first phase (×4) to the second phase (×9). Operationally coherent: hot-test (cycle 4: raw heat + ch), then cool-and-test (cycle 5: degree-1 + ch), then resume routine.

This generalizes the C929 ch=active-test gloss to a per-cycle annotation: `ch` inside a cycle token marks "this cycle includes a test."

### Finding 3: Refinement of C1394 MOD-atom semantics

The HEAD+MOD*+TERM atom architecture (C1394) does NOT distinguish between MOD atom subtypes. Phase 650 evidence requires distinguishing:

- **Continuous/extensible MOD atoms:** `e` modulates thermal intensity (k → ke → kee → keee, per F-B-007 / C1735). Multiple `e`s do NOT mean "multiple discrete cool actions" — they're a single thermal-regime spec.
- **Discrete/event MOD atoms:** `ch` marks an event (active test, per C929). Different operational character: presence vs absence is the binary, not depth.

This refinement matters for atom-gloss interpretation: previous loose readings of qokeedy as "fire+heat+cool+cool+end" were wrong; correct reading is "fire+heat-at-degree-2+end."

### Finding 4: Idiom does NOT generalize to small-count recipes

| Folio | Recipe | Best window match | Corpus rarity |
|---|---|---|---|
| f82v | ×4 vessel spec | 5 cycles in 4-line window | 30 other corpus windows |
| f82v | ×4 (n alone) | 4 cycles in 3-line window | 64 other corpus windows |
| f112r | ×3 cohobation | No 1-5 line window with 3 or 4 cycles | n/a |

Small iteration counts (×3, ×4) are **structurally indistinguishable from corpus noise** at line-window resolution — too many windows have those counts by chance. The cycle-counting idiom is **detectable only when the iteration count is large enough to be corpus-rare** (×9 or larger).

This is an **epistemic limit**, not just a sample-size issue: you cannot detect "encoded ×3" in a corpus where dozens of windows have 3 closed cycles by chance.

### Finding 5: `lol` as transition checkpoint (sub-finding, not registered)

Scratch analysis: `lol` is rare (38 instances across 24 folios in Currier B), 1.41× enriched near qok-class neighbors but not dramatically. Section B (bath/balneum) at 0.32% vs Section H at 0.03% — section-localized to where vessel-state work happens.

In the f75r 10-cycle cluster, `lol` (idx 15) sits between cycle 5 (qokechdy = cool-test) and cycle 6 (qokeedy = back to routine) — at the test-completion / routine-resumption boundary. Operational reading: vessel-state checkpoint after the test pair, before continuing.

Effect size too small for independent constraint registration. Documented here.

---

## Methodology lesson

This phase repeated the pattern from project memory `feedback_read_first_scripts_verify`: **direct folio reading found a real pattern that scripts missed**. Three test rounds produced null/marginal results until the user corrected my filter (qok-class → qok+...+dy closed cycles) AND my granularity (paragraph → line-window). Both corrections came from looking at the actual f75r tokens, not from running more scripts.

The lesson: when a structural pattern is reported from direct reading, code the test to match what was *observed*, not what's *easy to compute*. Filter and granularity choices have to come from the data, not from defaults.

---

## Constraint registered

### C1965 (Tier 3): f75r cycle-counting + per-cycle annotation idiom

[Full text in `context/CLAIMS/C1965_f75r_cycle_counting_idiom.md`]

**Statement:** On f75r, the recipe's two-phase reflux specification (×4 first, ×9 after) is encoded as line-localized closed-cycle clusters. The ×9 phase encodes as a corpus-singular 3-line window (L36-L38) of 10 closed cycles (1 initial + 9 redistillations). The two test cycles (qokchdy at cycle 4, qokechdy at cycle 5) carry `ch` MOD atoms (per C929 active-test gloss) at the recipe's phase boundary. Idiom does NOT generalize to small-count recipes (f82v ×4 and f112r ×3 show no distinguishing encoding above corpus noise).

**Tier:** 3 (anchor on single confirmed-match folio; mechanism plausible but not statistically generalized)

### Refinement note on C1394

MOD-atom class includes two distinguishable subtypes:
- **Continuous-extensible:** `e` (thermal intensity, per F-B-007/C1735), `i` (duration per existing notes)
- **Discrete-event:** `ch` (active test per C929), `d` (mark), `n` (halt/bind)

Earlier loose readings conflating these (e.g., "qokeedy = heat + cool + cool + end" treating each `e` as discrete) are corrected.

---

## Pending future work

1. **Test the closed-cycle idiom on unmatched Currier B folios.** Find folios with corpus-rare closed-cycle line-window counts (≥7 in 1-3 line window) and predict their iteration count. If the prediction matches independent recipe-content evidence, the idiom generalizes to the rarity-detectable scope.

2. **Per-cycle ch annotation across other cycle clusters.** Do other multi-cycle qok-runs in the corpus also have ch-insertions at structurally meaningful positions (phase transitions, etc.)?

3. **`lol` in conjunction with other ol-self-loop tokens.** A full STAGING-marker family analysis (`ol`, `oldy`, `lol`, `olor` etc.) might reveal whether the transition-checkpoint reading generalizes.

---

## Files

- `scripts/`
  - `s1_qok_count_vs_recipe_cycles.py` — Round 1 (line-bounded qok-class)
  - `s2_qok_runs_with_gaps.py` — Round 2 (sequential gap-tolerant runs)
  - `s3_closed_cycle_filter.py` — Round 3 (paragraph-bounded closed cycles, too coarse)
  - `s4_line_window_closed_cycles.py` — Round 4 (line-window closed cycles, correct)
- `results/`
  - `cycle_count_test.json`
  - `qok_runs_with_gaps.json`
  - `closed_cycle_filter.json`
  - `line_window_closed_cycles.json`
