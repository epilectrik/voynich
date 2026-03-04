# C1393: Compound MIDDLE Composition Grammar

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** GLOSS_PREDICTION_TESTS (Phase 504)
**Depends on:** C1065 (atom ordering grammar), C1200 (order encodes procedural state), C1209 (MIDDLE positional grammar), C1195 (atom gloss tiers)

## Statement

Compound MIDDLEs (2+ atoms) follow a **head-initial three-slot composition grammar** where atoms partition into four functional roles based on their positional behavior within compounds (chi²=30,868, p≈0, Cramér's V=0.593):

| Slot | Atoms | Mean Position | Function |
|------|-------|---------------|----------|
| **HEAD** | a (0.09), e (0.21), o (0.32) | 0.0–0.35 | Domain setter — determines WHAT kind of operation |
| **MODIFIER** | p (0.38), c (0.40), i (0.44), f (0.50), d (0.54), s (0.64) | 0.35–0.65 | Action transformer — shapes HOW it's done |
| **TERMINAL** | l (0.77), r (0.89), h (0.90), y (0.97), m (0.98), n (1.00) | 0.75–1.0 | State carrier — resulting CONDITION |
| **FREE** | k (0.48), t (0.52) | 0.45–0.55 | Role-dual process variables — position determines role |

The first atom predicts compound category at 74–76% (type-level) / 78–86% (token-weighted). This independently replicates C1209's INITIAL/MEDIAL/TERMINAL character classification using compound decomposition (15/19 atom match).

## Key Findings

### T1: Head-Initial Structure (Test 1)
- First atom matches compound category: 76.4% (PREFIX method), 74.2% (direct method)
- Last atom matches: 19.1% / 31.9%
- First-only exclusive: 63.1% / 60.2%
- Token-weighted first: 85.9% / 78.3%
- Monotonic position gradient (3+ atoms): FIRST 63.5% → MIDDLE 59.3% → LAST 37.6%

### T2: Four-Role Partition (Test 2)
- Chi²=30,868, p≈0, Cramér's V=0.593 (massive effect, one of strongest signals in project)
- Extremes: a is 86.4% FIRST (mean 0.087), n is 99.4% LAST (mean 0.998)
- k and t are the ONLY atoms without strong positional preference (43%/39% and 38%/42% FIRST/LAST)
- Replicates C1209 independently: 15/19 atoms match INITIAL/MEDIAL/TERMINAL classification

### T3: FREE Atom Role Duality (Test 3)
- k and t are NOT position-independent — they are the MOST position-sensitive atoms
- k-first compounds: 98.4% THERMAL (k as actor/operator)
- k-last compounds: 88.3% MONITORING (k as measurement target)
- k JSD(FIRST,LAST) = 0.717 — HIGHER than HEAD atom e (0.593)
- t shows same pattern: t-first 98.0% THERMAL, t-last 95.4% MONITORING
- "FREE" means positionally MOBILE with role duality, not behaviorally invariant
- Interpretation: k (heat) and t (transfer) are process variables — nouns that the system manipulates. In HEAD position they ACT, in TERMINAL position they are MEASURED.

### T4: Terminal Carry-Over (Test 4)
- Within-line: chi²=1144, p=2.47×10⁻¹¹⁸, V=0.077 (real but weak, ~1% variance)
- Across-line: chi²=208, p=0.209 (not significant — resets at line boundary, consistent with C1200/C1233)
- Strongest chain: r(respond)→a(yield) at 1.98× (processing output feeds back as input)
- h(watch)→p(pause) at 2.59×, e(cool)→r(respond) at 1.83×

### T5: Action vs Channel Distinction (Test 5)
- Head-only model predicts intrinsic FUNCTION (what MIDDLE does) but fails to predict PREFIX-derived CHANNEL (which subsystem deploys it)
- Example: edy = e(cool)+d(mark)+y(end) is functionally THERMAL, but deployed by ch/sh MONITORING channel
- Two independent readable layers: MIDDLE composition = action content, PREFIX = deployment channel
- Atom glosses describe WHAT the compound does; PREFIX assignment describes WHO deploys it

### T6: Channel-Specific Slot Grammar (Test 6)
- **Universal skeleton:** y, n, m, h are ALWAYS terminal regardless of channel. Head-initial structure holds at 93.5% globally.
- **Channel-specific slot assignment:** k and t completely reverse positional role by PREFIX channel:
  - qo (heat source): k 90.5% FIRST (actor — "heat something")
  - ch (monitor): k 2.0% FIRST, 68.9% LAST (target — "check the heat")
  - sh (passive monitor): k 3.7% FIRST, 70.0% LAST (target)
- i-atom exclusive to a-base channels (da/ka/sa/ta: 50%+; ch/sh: <1%)
- d-atom (checkpoint) enriched in monitoring channels (12–27%), depleted in iteration channels (<2%)
- Cross-channel consistency: 4/17 atoms UNIVERSAL, 8 MIXED, 5 CHANNEL-SPECIFIC
- PREFIX modulates atom slot interpretation within compounds, not just which compounds are selected

## Composition Reading Rule

To read a compound MIDDLE:
1. **Identify the channel** (PREFIX) — this is WHO is speaking
2. **Read the HEAD atom** (first position) — this is the operational DOMAIN
3. **Read MODIFIER atoms** (middle positions) — these shape HOW the operation is performed
4. **Read the TERMINAL atom** (last position) — this is the resulting STATE/CONDITION
5. **For k/t:** if in HEAD position = actor ("do this with heat/transfer"); if in TERMINAL = target ("measure/check heat/transfer")

Example: `qokey` = heat-source channel: heat(k, actor) → cool(e, modifier) → end(y, state) = "Fire the heat, let it cool, done."
Example: `cheky` = monitor channel: cool(e, domain) → heat(k, target) → end(y, state) = "Check if the heat has cooled, done."

## Relationship to C1379 (Two-Level Parallel Composition)

C1379 (Phase 494) independently discovered priority ordering within compound MIDDLEs: INITIAL atom anchors identity, MEDIAL specifies action, TERMINAL specifies exit condition. C1393 generalizes and extends this:

| C1379 finding | C1393 equivalent |
|---------------|------------------|
| INITIAL anchors instruction identity | HEAD atom determines category (76%) |
| MEDIAL = "action atoms practitioners know" | MODIFIER slot (p,c,i,f,d,s) |
| TERMINAL = exit condition | TERMINAL slot carries state forward |
| Order matters (reversed ratio 0.904) | Head-initial structure, order-sensitive categories |
| Macro-atoms (ke, ck, ch, in) fuse into units | Complementary: fused HEAD+TERMINAL pairs act as single operational units |
| Mode A/B channel separation (ke 2.68x A, in 0.54x) | Test 6 channel-specific slot grammar (qo vs ch/sh slot modulation) |

**No conflict.** C1379's macro-atom model is a finer-grained view of the same grammar. C1393 adds: (1) the four-role partition with statistical proof (V=0.593), (2) k/t role duality by channel, (3) the action-vs-channel distinction between MIDDLE composition and PREFIX assignment.

## Open Questions

- **l-anomaly:** l shifts from TERMINAL to INITIAL under po/so/to/da channels — may be semi-free like k/t
- **Modifier stacking order:** When multiple modifiers appear in one compound, is their internal sub-order fixed?
- **2-atom vs 3+ atom:** Does the grammar differ when no modifier slot exists?
- **Suffix boundary (resolved):** Suffix is a parallel compound domain using the same atom inventory, not an artifact of TERMINAL atoms. 77% of MIDDLEs take 3+ different suffixes (entropy 1.475 bits), confirming independence. Compound MIDDLEs narrow suffix choice slightly (1.42 bits vs 1.99 for single-atom). See `phases/SUFFIX_BOUNDARY_TEST/`.

## Falsification

Would be falsified if:
1. A controlled test shows atom positional preferences are section-dependent artifacts (not genuine grammar)
2. The head-initial structure fails for a specific well-defined compound class (>50 tokens)
3. k/t role duality is shown to be a PREFIX-selection effect rather than genuine positional semantics

## Provenance

- `phases/GLOSS_PREDICTION_TESTS/scripts/compound_head_test.py` — Test 1
- `phases/GLOSS_PREDICTION_TESTS/scripts/atom_position_preferences.py` — Test 2
- `phases/GLOSS_PREDICTION_TESTS/scripts/free_atom_position_test.py` — Test 3
- `phases/GLOSS_PREDICTION_TESTS/scripts/terminal_head_carryover.py` — Test 4
- `phases/GLOSS_PREDICTION_TESTS/scripts/composition_grammar_accuracy.py` — Test 5
- `phases/GLOSS_PREDICTION_TESTS/scripts/channel_slot_grammar.py` — Test 6
- `phases/GLOSS_PREDICTION_TESTS/results/phase_504_composition_grammar.json` — consolidated results
