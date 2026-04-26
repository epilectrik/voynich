# Phase 648: Vessel-State 4-Axis Recipe Validation

**Status:** COMPLETE
**Date:** 2026-04-25
**Constraints registered:** C1961 (Tier 2), C1962 (Tier 3); refinement notes on C1958, C1388

---

## Question

Do the four o-prefixes (ok, ot, ol, or) form a 4-axis vessel-state monitoring grammar that can be promoted from category-level glosses (per C1316/C1388) to specific physical-channel readings (analogous to C1958's promotion of `ot` to "transfer/drip rate")?

And does the folio-level structure decompose into a fire-side / vessel-side architecture (user hypothesis), distinct from the registered token-level QO-lane / CHSH-lane partition (C1217/C1242/C1306)?

---

## Method

### Phase setup
- 16 SISMEL-matched folio↔recipe pairs (3 CONFIRMED, 4 strong-supported, 8 supported, 1 added Phase 644)
- 8D feature-space matching infrastructure (`shared_628.py`)
- Atom decomposition via `voynich.Morphology.atomize()`

### Scripts (executed in order)
1. `s1_profile_o_prefixes.py` — Per-folio rate of each o-prefix; pairwise correlation matrix
2. `s2_cross_reference_matched_recipes.py` — Label-based predictions (baseline)
3. `s3_recipe_text_by_prefix_group.py` — Group folios by dominant prefix; dump SISMEL Catalan recipe text for each group
4. `s4_retest_refined_definitions.py` — Re-test predictions under text-grounded definitions
5. `s5_chsh_qo_lane_test.py` — Test fire-side vs vessel-side hypothesis at folio level
6. `s6_position_resolve_and_permute.py` — Position-resolution + permutation null + paragraph-level replication
7. `s7_section_regime_controls.py` — Within-section + within-regime controls

---

## Findings summary

### Finding 1: 4-axis runtime channels (C1962, Tier 3)

Reading SISMEL Catalan recipe text for each matched folio yielded refined channel definitions:

| Prefix | Refined gloss | Recipe signature |
|---|---|---|
| **ol** | Vessel-content state monitoring (which vessel holds what, batch identity, vessel role) | f75r batch-keeping, f80r vessel-naming, f84r apparatus arrangement, f83r sealed-state |
| **ot** | Material transfer / addition / iteration cycles | f112r cohobation, f103r chamber combination, f76v addition, f116r repeated cycles |
| **ok** | Thermal regime / fire-degree state on contents | f82r theoretical fire-regime, f76r calcination-driven preparation |
| **or** | Outcome / completion state (per C539 LATE positional class) | No matched recipes or-dominant; enriches on herbal-B + recipes-section short folios |

Within-sample top-1 fit: 16/16 (100%). Top-2 strict: 7/16 (43.8% vs 17% random). Position-uniform within paragraphs (early/base ratio 0.75–1.13× across all four).

**Note:** The within-sample fit caveat — definitions were derived from these same texts. Out-of-sample validation pending.

### Finding 2: Fire-side / vessel-side paragraph-level architecture (C1961, Tier 2)

| Block | Members | Within-block r̄ | Cross-block r̄ | Differential |
|---|---|---|---|---|
| Fire-side | qo, ch, sh | +0.063 | — | — |
| Vessel-side | ok, ot, ol, or | +0.097 | — | — |
| **Cross** | — | — | **−0.232** | **+0.295** (folio-level) |
| **Cross** | — | — | — | **+0.131** (paragraph-level, p=0.024) |

Strongest cells:
- qo↔ok = −0.42 (problematic for "QO lane" reading at folio scale)
- ch↔ol = −0.45 (operator active-test vs vessel-state, anti-correlated)
- qo↔ol = +0.29 (the bridge — heat application meets vessel-state change)
- ok↔or = +0.34 (vessel-side internal coherence)

### Finding 3: Position-resolution discriminates runtime vs. setup-phase reading

All four o-prefixes are positionally uniform within paragraphs, falsifying the alternative reading where ol could have been a setup-phase declaration:

| Prefix | Early/Base | Late/Base | Verdict |
|---|---|---|---|
| ok | 0.91× | 1.10× | UNIFORM |
| ot | 0.97× | 0.95× | UNIFORM |
| ol | 0.87× | 1.10× | UNIFORM |
| or | 0.75× | 1.14× | mixed (small N) |
| ch | 0.79× | 1.18× | LATE-enriched |
| sh | 1.13× | 0.92× | EARLY-enriched |

The ch-late / sh-early sub-distinction within the fire-side block is consistent with crazy-expert's event-monitor (ch) vs continuous-monitor (sh) reading. Documented as commentary in C1961; effect sizes below 1.5× threshold so not registered as separate constraint.

---

## Controls (per expert-advisor recommendation)

### Permutation null on folio differential
- Real: +0.2949
- Null mean (1000 shuffles of 7→3+4 splits): +0.0041
- 95th percentile of null: +0.2949
- p-value: 0.058 (borderline; constrained by discrete C(7,3)=35 split space)

### Paragraph-level replication (per C1811-C1812)
- Differential: +0.131 (n=466 paragraphs)
- p-value: 0.024
- Architecture survives at the load-bearing PREFIX scale

### Within-section controls (per C1404)

| Section | n | Differential | p | Verdict |
|---|---|---|---|---|
| B (Bath) | 84 | +0.4111 | 0.015 | SURVIVES |
| H (Herbal) | 68 | +0.3205 | 0.027 | SURVIVES |
| S (Stars/Recipes) | 278 | +0.0885 | 0.018 | SURVIVES |
| C (Cosmo) | 22 | +0.1458 | 0.120 | directional |

3/4 significant, 4/4 directional. Not section-confounded.

### Within-regime controls (per C1300/C1547)

| Regime | Profile | n | Differential | p | Verdict |
|---|---|---|---|---|---|
| REGIME_1 | qo-heavy | 201 | +0.1196 | 0.112 | directional |
| REGIME_2 | iteration/k-heavy, low link | 32 | **−0.0814** | 0.704 | **FAILS** |
| REGIME_3 | h-ratio/thermo-kch | 190 | +0.1386 | 0.011 | SURVIVES |
| REGIME_4 | link-heavy, low qo | 43 | +0.2897 | 0.025 | SURVIVES |

3/4 directional, 2/4 significant. **REGIME_2 fails directionally.** Documented as scope-restriction in C1961.

---

## Pending future work (flagged by crazy-expert)

Three discriminating tests not run in Phase 648 — would either further support or weaken the architecture:

1. **Paragraph-shuffle null within REGIME_2** to determine whether the −0.081 differential is below noise (would demote REGIME_2 from "directional failure" to "underpowered") or genuinely structural (would promote LINK-as-separator hypothesis).
2. **Variance decomposition** of the differential at paragraph vs folio level to confirm the architecture operates at PREFIX-load-bearing scale rather than appearing paragraph-level only because most folios are dominated by one paragraph type.
3. **MIDDLE-pool comparison** across o-prefixes at fixed paragraph position — distinguishes "4 distinct channels" from "4 allomorphs of same channel."

If all three pass, the 7-channel multivariable control architecture reading would have stronger structural support. The historical claim ("undocumented 15th-century process control") remains Tier 3 regardless.

---

## Constraint verdicts

| Constraint | Tier | Status |
|---|---|---|
| C1961 — Fire/vessel paragraph-level partition | 2 | Registered |
| C1962 — 4-axis o-prefix runtime channels | 3 | Registered |
| C1958 — broadened from "drip rate" to "transfer/iteration cycles" | 2 | Refinement note |
| C1388 — ol gloss sharpened to "vessel-content state monitoring" | 2 | Refinement note |
| ch/sh position sub-distinction | — | Commentary in C1961 |

---

## Script runtimes

All scripts complete in <60s on a standard workstation. Total phase wall-time ~30 min.

---

## Files

- `scripts/` — 7 Python scripts (s1–s7)
- `results/`
  - `o_prefix_folio_profile.json`
  - `cross_reference.json`
  - `grouped_text.txt` (SISMEL Catalan text grouped by dominant o-prefix)
  - `refined_test.json`
  - `chsh_qo_lane_test.json`
  - `position_and_permutation.json`
  - `section_regime_controls.json`
