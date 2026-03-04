# C1379: Two-Level Parallel Composition with Priority Ordering

**Tier:** 2
**Scope:** B
**Phase:** PARALLEL_MONITORING_TRACKS (Phase 494)
**Date:** 2026-03-01

## Statement

MIDDLE atoms compose through a two-level architecture: high-affinity atom pairs from C1210 fuse into macro-atoms that then combine with remaining individual atoms. Macro-atom decomposition significantly improves behavioral prediction over individual atoms (r=0.797 vs 0.760, z=5.98, p<0.001, 1000 permutations). All atom positions contribute to token behavior (removal ratio 1.375, below 1.5 threshold) but INITIAL position dominates (Kruskal p=0.004). Atom order matters nearly as much as atom identity (reversed/different-set JSD ratio 0.904). Cross-token coupling flows through TERMINAL→INITIAL (MI=0.079 bits), not the full atom set (0.025 bits). The model is parallel composition with priority ordering: multiple monitoring parameters encoded simultaneously, but ordered, not interchangeable.

## Hypothesis Tested

MIDDLE atoms encode parallel monitoring parameters (e.g., simultaneous heat, vessel state, completion checks). High-affinity atom pairs from C1210 (ke 7.94x, in 6.78x, ct 6.58x, ck 5.81x, ch 4.98x, am 4.38x, an 3.18x, dy 3.18x, ph 7.24x) are fused operational units. Compound MIDDLEs compose these units in parallel.

**Four-test battery (pre-registered):**
- T1: Macro-atom decomposition improves C1190 composition r — **PASS**
- T2: Reversed pairs (same atoms, different order) behave alike — **FAIL**
- T3: SET carry MI >= TERMINAL→INITIAL MI — **MIXED**
- T4: Removing any atom position produces equal change — **PASS threshold, qualified**

## Evidence

### T1: Macro-Atom Composition (KEY TEST) — PASS
- Individual atoms (compounds >= 2): r=0.758 (replicates C1190)
- Individual atoms (compounds >= 3): r=0.760
- Macro-atom decomposition (compounds >= 3): r=0.797
- Improvement: +0.037
- Permutation test (1000 random pairings): mean=0.761, std=0.006
- z=5.98, p<0.001, **highly significant**
- 9 macro-atoms tested: ke, in, ck, ch, dy, an, am, ct, ph

### T2: Order Magnitude Effect — FAIL
- 7 reversed pairs found (ck/kc, ct/tc, eek/kee, ek/ke, et/te, ko/ok, lo/ol)
- Reversed-pair mean JSD: 0.488
- Different-set mean JSD: 0.540
- Ratio: 0.904 (prediction was < 0.5)
- Mann-Whitney U p=0.146 (not significant)
- **Interpretation:** Atom order matters almost as much as atom identity. This REJECTS pure parallelism but is consistent with priority-ordered composition where position encodes rank.

### T3: Cross-Token Coupling — MIXED
- TERMINAL(N)→INITIAL(N+1): V=0.079, MI=0.079 bits (strongest)
- INITIAL(N)→INITIAL(N+1): V=0.068, MI=0.060 bits (75% of T→I)
- TERMINAL(N)→TERMINAL(N+1): V=0.064, MI=0.051 bits
- SET carry (sum per-atom): MI=0.025 bits
- SET/T→I ratio: 0.32x; I→I/T→I ratio: 0.75x
- **Interpretation:** Cross-token grammar flows through exit state (TERMINAL→INITIAL), not the full monitoring set. But INITIAL→INITIAL coupling at 75% shows the entry state also persists, consistent with priority ordering.

### T4: Atom Removal Symmetry — PASS (qualified)
- 38 testable 3-char MIDDLEs, 114 removal comparisons
- Mean JSD by position: initial=0.374, medial=0.272, terminal=0.299
- Max/min ratio: 1.375 (below 1.5 parallel threshold)
- Kruskal-Wallis: H=10.90, p=0.004 (positions ARE statistically different)
- Effect ordering: initial > terminal > medial
- **Interpretation:** All positions contribute (ratio < 1.5), but initial atom has priority. Medial drops first — consistent with C1209 MEDIAL slot containing action atoms that expert practitioners already know.

### T5: Suffix Mode Channel Separation — PASS

Macro-atoms have functional channel assignments aligned with suffix mode tracks (C1229, C1258):

**PREFIX channel by mode:**
- THERMAL_SOURCE (qo): Mode A 24.5% vs Mode B 12.9% — **1.91x enrichment** (p=0.0000, 10K perms)
- Thermal aggregate (qo+ok+ot+ol): Mode A 39.3% vs Mode B 30.5% — **1.29x** (p=0.0000)
- Assessment (ch+sh): Mode A 30.6% vs Mode B 30.0% — 1.02x (p=0.82, no separation)
- Chi-squared V=0.165 across all channels
- BARE PREFIX: Mode B 18.9% vs Mode A 13.5% — Mode B is the continuation channel

**Macro-atom mode assignment:**

| Mode A enriched | Ratio | Mode B enriched | Ratio |
|-----------------|-------|-----------------|-------|
| ct | 2.87x | in | 0.54x |
| ke | 2.68x | am | 0.82x |
| ch | 2.34x | an | 0.00x |
| ph | 2.02x | | |
| ck | 1.91x | | |

dy is neutral (0.92x).

**Kernel by mode:**
- k/e ratio: Mode A = 0.673, Mode B = 0.431 (Mode A has 56% more heating relative to cooling)
- k enrichment in A: 1.78x; h enrichment in A: 2.14x

**Interpretation:** The fused macro-atoms split into two functional classes — specification atoms (ke, ct, ck, ch, ph) that concentrate in Mode A lines where thermal parameters are set, and continuation atoms (in, am, an) that concentrate in Mode B lines where process state evolves. This is not an artifact of suffix classification: the macro-atom channel assignments are independent evidence that the two suffix modes encode functionally distinct instruction streams operating on different subsystems.

## Interpretation

The two-level model reconciles two tensions in the data:

1. **ke/kee/keee tension (C1225):** Some atom pairs behave as integrated units where only one component (e) can extend. The fused-pair macro-atom model handles this: ke is a single operational unit, and e-depth is an internal parameter of that unit.

2. **Additive vs ordered:** C1190 shows additive composition (mean of component profiles predicts compound). But T2 shows order matters. Resolution: atoms compose additively (T1 confirms) but with priority weighting by position — INITIAL atom anchors instruction identity, MEDIAL specifies action, TERMINAL specifies exit condition.

3. **Two-channel architecture (T5):** Macro-atoms are not channel-neutral. The specification atoms (ke, ct, ck, ch, ph) concentrate in Mode A — the thermal/parameter-setting voice. The continuation atoms (in, am, an) concentrate in Mode B — the process/state-evolution voice. The line-level suffix mode alternation (C1229) is a two-channel clock where different macro-atoms serve different channels.

The practical reading: a compound MIDDLE like "ked" in a Mode A line encodes "set [ke-parameter] with [d-exit-condition]" — a thermal specification. The same MIDDLE in a Mode B line (rare for ke, 2.68x A-enriched) would encode something closer to "maintain [ke-parameter]." The instruction's channel context determines whether it specifies or continues.

## Qualifies

- C1190 (additive composition r=0.754) — confirmed and improved: macro-atom r=0.797
- C1209 (3-slot grammar) — qualified: slots have functional roles (priority, action, exit)
- C1210 (forbidden combinations + affinities) — extended: high-affinity pairs are fused macro-atoms with channel assignments
- C1211 (negative 3-way synergy) — consistent: mutual exclusions between incompatible monitoring targets
- C1225 (e-depth parametricity) — integrated: e-depth is internal parameter of ke macro-atom
- C1229 (alternating suffix modes) — extended: modes carry different macro-atom populations
- C1258 (parallel mode tracks) — strengthened: macro-atoms provide independent evidence for two-channel architecture
- C1309 (mode category specialization) — converges: category-level thermal enrichment in A matches macro-atom ke/ct/ck enrichment

## Method

- 23,096 Currier B tokens with MIDDLEs, 210 MIDDLEs with profiles (>= 5 tokens)
- 22 behavioral features per MIDDLE (matching C1190)
- 9 macro-atoms from C1210 high-affinity pairs (enrichment > 3x)
- Greedy decomposition: longest macro-atom match first
- Permutation null: 1000 random atom pairings, same number of pairs (T1); 10K mode-shuffle permutations (T5)
- Pre-registered thresholds: p < 0.05, ratio < 0.5 (T2), ratio < 1.5 (T4)
- Suffix mode classification: C1231 centroid distance (4-dimensional suffix category vector)
- 2,406 lines classified (1,035 Mode A, 1,371 Mode B), 23,074 tokens with mode assignment

## Provenance

- Script: `phases/PARALLEL_MONITORING_TRACKS/scripts/parallel_monitoring_test.py`
- Script: `phases/PARALLEL_MONITORING_TRACKS/scripts/suffix_mode_channel_test.py`
- Results: `phases/PARALLEL_MONITORING_TRACKS/results/parallel_monitoring_test.json`
- Results: `phases/PARALLEL_MONITORING_TRACKS/results/suffix_mode_channel_test.json`
- Pre-registration: `phases/PARALLEL_MONITORING_TRACKS/results/pre_registration.json`
- Depends: C1190, C1209, C1210, C1211, C1225, C1229, C1231, C1258, C1309

## Status

CONFIRMED — Two-level macro-atom composition confirmed (T1 z=5.98). Pure parallelism rejected (T2 ratio 0.904). Macro-atoms have functional channel assignments (T5: ke/ct/ck 1.9-2.9x Mode A; in 0.54x Mode B; thermal p=0.0000). Refined model: two-channel parallel composition with priority ordering and channel-specific macro-atom populations.
