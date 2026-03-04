# C1394: Instruction Encoding Architecture

**Tier:** 2 (ESTABLISHED)
**Scope:** B, grammar, composition
**Phase:** INSTRUCTION_ENCODING_MAP (Phases 505–506)
**Depends on:** C1393 (composition grammar), C1195 (atom glosses), C1065 (atom ordering), C1200 (state forward), C1197 (e/i extensibility)

## Statement

Compound MIDDLEs encode instructions as **HEAD + MOD\* + TERM** — fixed endpoints with a variable-length, internally ordered modifier stack. The frame (HEAD+TERM) predicts 64% of instruction category; modifiers account for the remaining 36% through consistent category-shifting effects. This extends C1393's three-slot model by establishing: (1) the modifier slot is a variable-length ordered array, not a single position; (2) modifiers follow a fixed stacking order (p→f→i→c→d→s); (3) each modifier has a measurable, consistent effect on instruction category; (4) most "macro-atoms" are just adjacent slots, not fused units.

Phase 506 resolved all four open questions: headless compounds are a specialized subgrammar for infrastructure operations (V=0.568); h-terminal is transparent, not chaotic (HEAD+MODS reach V=0.988); modifier ordering is morphological convention with first-modifier dominance (66.5% decisive); all five HEADs are genuine domains with e showing a depth-dependent cooling→thermal saturation gradient (ee=84% THERMAL, eee=100%).

## Key Findings

### T1: Suffix Boundary Confirmation

Suffixes decompose into the same atom inventory as compound MIDDLEs (94.7% follow C1393 slot grammar), but the suffix is a **genuine independent layer**: 77.1% of MIDDLEs appear with 3+ different suffixes (entropy 1.475 bits). Compound MIDDLEs narrow suffix choice slightly (1.42 bits vs 1.99 for single-atom). The morphological boundary MIDDLE|SUFFIX is real, not an artifact of terminal atoms being stripped.

### T2: Fusion Gradient

Candidate "macro-atoms" fall on a gradient, not a binary fused/separate distinction:

| Category | Pairs | Evidence |
|----------|-------|----------|
| **Hard-fused** | dy | Never separated (0.15%), 97.7% LAST, O/E 5.75x |
| **Soft-fused** | ed, ol, op, ck, ch, in | Rarely separated, high O/E (2.8–8.6x), but components substitute independently |
| **Adjacent slots** | ke, ee, od, ey | Separate freely; ke separates 25%, od has O/E=1.08 (chance), ey separates MORE than it's adjacent (1.67x) |

HEAD atoms show non-uniform modifier preferences (chi² massive): a→i (51.5%), e→d (33.2%), o→l (40.3%). This HEAD-modifier affinity creates the appearance of fusion without requiring it.

### T3: Pair-Locked Atoms

9/18 atoms are pair-locked (standalone MIDDLE rate <10%):

| Atom | Role | Standalone % |
|------|------|-------------|
| c | MODIFIER | 0.2% |
| n | TERMINAL | 0.3% |
| a | HEAD | 1.8% |
| h | TERMINAL | 2.9% |
| i | MODIFIER | 4.8% |
| p | MODIFIER | 7.4% |
| d | MODIFIER | 7.7% |
| f | MODIFIER | 7.9% |
| o | HEAD | 9.0% |

All 5 MODIFIER atoms are pair-locked. Both non-e HEAD atoms (a, o) are pair-locked. FREE atoms k (47%) and t (39%) are the most independent, confirming C1393. Only e and i can repeat (C1197 extensibility).

### T4: Modifier Stack Ordering

Modifiers follow a fixed internal ordering within compounds (p→f→i→c→d→s):

| Modifier | Gloss | Mean stack position | Asymmetry examples |
|----------|-------|--------------------|--------------------|
| p | pause | 0.225 | p before s: 8.7:1 |
| f | flag | 0.395 | |
| i | iterate | 0.519 | |
| c | adjust | 0.532 | c before h: 8.2:1 |
| d | mark | 0.696 | |
| s | sequence | 0.713 | |

Modifier co-occurrence avoidance: c/i (0.40x), c/s (0.48x), i/s (0.52x), d/f (0.50x). These pairs actively avoid each other in compounds.

### T5: HEAD × TERM Frame Matrix

Dominant frames by token count:

| Frame | Tokens | Dominant category | Purity |
|-------|--------|------------------|--------|
| e→y | 3,475 | OPERATION | 55.8% |
| a→n | 1,272 | TRANSITION | 65.6% |
| k→(open) | 779 | THERMAL | 69.1% |
| o→l | 777 | STAGING | 98.1% |
| a→r | 687 | FLOW | 99.4% |
| o→r | 455 | FLOW | ~99% |

HEAD-level category dominance: k=71% THERMAL, t=65% FLOW, a=55% FLOW, e=37% OPERATION (most versatile), o=35% STAGING.

TERM-level: r=99% FLOW (nearly deterministic), m=87% TRANSITION, n=64% TRANSITION, y=56% OPERATION, l=47% STAGING, h=transparent (category determined by HEAD+MODS, V=0.988).

### T6: Modifier Category-Shifting Effects

Each modifier has a consistent, statistically significant (p≈0) effect on instruction category:

| Modifier | Gloss | V | Strongest shift |
|----------|-------|---|-----------------|
| d | mark | 0.657 | +55.6% OPERATION (strongest modifier) |
| c | adjust | 0.505 | +30.1% MARKING |
| i | iterate | 0.418 | +44.7% TRANSITION; kills OPERATION/THERMAL |
| p | pause | 0.368 | +45.6% MARKING |
| f | flag | 0.351 | +76.4% MARKING (most concentrated) |
| s | sequence | 0.245 | boosts MONITORING/STAGING (weakest) |

Modifier hierarchy by effect size: d > c > i > p > f > s. The `d` modifier is the single most powerful category determiner; `f` is the most concentrated (80.2% MARKING).

### T7: Compound Size Distribution

By token frequency: 0 modifiers=24.1%, 1 modifier=47.0%, 2+ modifiers=28.9%. The modal instruction has exactly one modifier (HEAD+MOD+TERM). Longer compounds are type-rich but token-rare (4+ atoms = 35% of types but only 15% of tokens).

### T8: Headless Compounds — Specialized Subgrammar (Phase 506)

467 headless compound types (20.6% of compound tokens) lack a valid HEAD atom. These are NOT abbreviations — most are their own primary forms (mean headless fraction 0.706).

- **Category divergence** (V=0.568): enriched in CONTAINMENT (10.4x), MARKING (5.3x), MONITORING (3.9x), STAGING (2.7x). Depleted in THERMAL (0.12x), TRANSITION (0.21x), FLOW (0.24x).
- **PREFIX context** (V=0.565): massively concentrated under a-base PREFIXes (da 2213x, sa, ka, ta). The yield/transition channel is the primary consumer.
- **Positional enrichment**: paragraph-initial 2.16x, line-initial 1.8x, line-final 1.5x. Headless compounds favor boundary positions.
- **Interpretation**: HEAD-free instruction class for infrastructure/support operations at boundary positions. HEAD domain is either implicit (supplied by PREFIX channel) or genuinely absent.

### T9: h-Terminal Transparency (Phase 506)

h-terminal's apparent chaos (27% purity) is resolved: h is **transparent**, not random.

- **HEAD+MODS reach V=0.988** for h-terminal compounds — near-perfect category prediction when you include the modifier stack. The "chaos" exists only if you ignore modifiers.
- **HEAD alone**: V=0.541 (k+h=83% THERMAL, t+h=84% OPERATION, o+h=43% OPERATION, e+h=43% MARKING).
- **PREFIX compensates**: V(PREFIX,category) = 0.389 for h-terminal vs 0.223 for non-h (Δ=+0.166). When TERM doesn't lock category, PREFIX picks up the slack.
- **ch substructure**: 70.7% of h-terminal tokens end in ...ch. Within ch-ending compounds, HEAD is highly predictive (k→96% THERMAL, t→98% OPERATION). Non-ch h-terminals are the genuinely diverse minority.
- **Open monitor hypothesis SUPPORTED**: V(HEAD→category|TERM=h) / V(TERM→category|non-h) = 0.916. h lets HEAD's signal pass through — consistent with h="watch" (keep monitoring whatever HEAD specifies).

### T10: Modifier Ordering Semantics (Phase 506)

The p→f→i→c→d→s ordering is **morphological convention with weak semantic coupling**, not a procedural pipeline.

- **Order violations preserve category** (71%): reversing modifier order rarely changes the instruction's category. Only c↔p shows a genuine semantic reversal (OPERATION vs MARKING, chi²=26.0).
- **No position-effect gradient** (Spearman rho=0.086, p=0.87): effect magnitude is independent of stack position. d has the highest V=0.657 at position 0.70; s has the lowest V=0.245 at position 0.71.
- **First modifier dominates** (66.5% decisive): the modifier closest to HEAD carries the most category weight, consistent with head-initial architecture.
- **Multi-stage stacking collapses to MARKING** (V=0.516): compounds spanning GATE+LOOP+TUNE+SEAL converge 97–100% on MARKING. Pipeline model FALSIFIED for multi-stage; these are identification vocabulary.
- **Suffix mode coupling** (V=0.260): early modifiers (p,f) → Mode A (specification), late modifiers (d,s) → Mode B (continuation). Extends C1382 to the modifier layer.

### T11: e-Atom Domain Specificity (Phase 506)

e is a **genuine domain-specific HEAD**, not a transparent default. Score: 4/5 domain-specific.

- **o is the real versatility champion** (entropy 2.396 vs e's 2.191). e's apparent diversity was partly a sample-size effect.
- **e has the LOWEST modifier dominance** (V=0.672 vs a=0.866, o=0.873, k=0.829, t=0.812) — the opposite of a transparent default where modifiers would dominate.
- **Stripping initial e changes category 91%** of the time — e contributes genuine domain signal.
- **e-depth saturation**: single-e = diverse (entropy 2.250), ee = 84.3% THERMAL (entropy 0.789), eee = 100% THERMAL (entropy 0.0). Doubling e overwrites modifier influence and forces thermal identity.
- **e in modifier position** is more focused: 64.2% THERMAL (entropy 1.618 vs 2.263 as HEAD). As modifier, e is a specific thermal-shifter; as HEAD, it controls a broader domain.
- **e and k share thermal domain** from opposite directions (cool vs heat), confirmed by bare-atom classification: both = THERMAL.

## Instruction Encoding Model

```
TOKEN = PREFIX + MIDDLE + SUFFIX

MIDDLE = HEAD + MOD* + TERM

Where:
  HEAD ∈ {a, e, o, k*, t*}     — operational domain
  MOD  ∈ {p, f, i, c, d, s}*   — ordered parametrization stack
  TERM ∈ {l, r, h, y, m, n, k*, t*} — exit state/condition

  * k, t are role-dual: HEAD when first, TERM when last

Modifier stacking order: p → f → i → c → d → s
Frame predicts 64% of category; modifiers shift remaining 36%.
```

Reading rule:
1. **PREFIX** = who is speaking (deployment channel)
2. **HEAD** = operational domain (k=thermal, e=cooling, o=staging, a=yielding, t=transfer). May be absent in headless compounds (infrastructure ops, implicit from PREFIX).
3. **MOD stack** = parametrization (conventional order p→f→i→c→d→s; first modifier dominates at 66.5%). Multi-stage stacking = identification vocabulary, not procedural pipeline.
4. **TERM** = exit condition. Opaque terminals (r=respond/FLOW, m=final/TRANSITION, n=halt/TRANSITION, y=end/OPERATION, l=state/STAGING) impose category. Transparent terminal (h=watch) lets HEAD+MODS determine category.
5. **SUFFIX** = independent context/role marker (same atom grammar, separate domain)
6. **e-depth** = intensity gradient. Single e = diverse cooling domain. ee/eee = thermal saturation (84–100% THERMAL).

## Example Readings

| Compound | Decomposition | Category | Gloss |
|----------|--------------|----------|-------|
| aiin | a + ii + n | TRANSITION | yield + iterate(×2) + halt |
| edy | e + d + y | OPERATION | cool + mark + end |
| ol | o + l | STAGING | arrange + state |
| opch | o + pc + h | OPERATION | arrange + pause,adjust + watch |
| kch | k + c + h | THERMAL | heat + adjust + watch |
| ar | a + r | FLOW | yield + respond |
| ke | k + e | THERMAL | heat + cool |

## Relationship to C1393

C1393 (Phase 504) established the three-slot partition (HEAD/MOD/TERM/FREE) with V=0.593. C1394 extends this by:

| C1393 finding | C1394 extension |
|---------------|-----------------|
| Three slots: HEAD, MODIFIER, TERMINAL | Modifier slot is variable-length ordered array (0..N) |
| Four-role partition (V=0.593) | Frame (HEAD+TERM) predicts 64%, modifiers shift 36% |
| Head-initial structure | Fixed modifier ordering: p→f→i→c→d→s |
| "Macro-atoms" as fused units | Gradient of fusion; most are adjacent slots, only dy is hard-fused |
| k/t as FREE atoms | k/t confirmed as role-dual (T3: pair-lock data) |

**No conflict.** C1394 generalizes C1393's static slot partition into a dynamic instruction encoding architecture.

## Open Questions (Phase 505)

All four original open questions were **resolved in Phase 506** (T8–T11):
- ~~Modifier ordering semantics~~ → Morphological convention, first-modifier dominance, not procedural pipeline (T10)
- ~~h-terminal chaos~~ → h is transparent, not chaotic; HEAD+MODS reach V=0.988 (T9)
- ~~Headless compounds~~ → Specialized subgrammar for infrastructure ops at boundaries (T8)
- ~~e versatility~~ → Genuine domain (cooling); o is the real versatility champion (T11)

## Remaining Open Questions (Phase 506)

- **Headless compound HEAD recovery:** Can the missing HEAD be reliably inferred from PREFIX channel? (da→a-domain? ka→k-domain?)
- **Multi-stage MARKING collapse:** Why do compounds spanning 3+ pipeline stages converge to MARKING? Is this identification vocabulary (HT/dark pipeline) or a genuine operational pattern?
- **e/k thermal polarity:** e and k both map to THERMAL from opposite directions (cool vs heat). How does the system distinguish cooling operations from heating operations at the execution level?
- **o versatility mechanism:** o is the most category-diverse HEAD (entropy 2.396). What makes the "arrange" domain span more operational categories than any single physical process?

## Falsification

Would be falsified if:
1. Modifier ordering is shown to be a frequency artifact (randomized modifier sequences produce equal category prediction)
2. Frame (HEAD+TERM) category prediction drops below chance (12.5% for 8 categories) in a controlled subset
3. Modifier category-shifting effects are shown to be confounded by HEAD identity (same modifier has opposite effects under different HEADs)

## Provenance

### Phase 505
- `phases/SUFFIX_BOUNDARY_TEST/scripts/suffix_boundary_test.py` — T1 (suffix independence)
- `phases/SUFFIX_BOUNDARY_TEST/scripts/fusion_vs_adjacency.py` — T2 (fusion gradient)
- `phases/SUFFIX_BOUNDARY_TEST/scripts/pair_locked_atoms.py` — T3 (pair-locked atoms)
- `phases/SUFFIX_BOUNDARY_TEST/scripts/modifier_stack_test.py` — T4, T7 (modifier ordering, size distribution)
- `phases/INSTRUCTION_ENCODING_MAP/scripts/instruction_map.py` — T5, T6 (frame matrix, modifier effects)
- `phases/INSTRUCTION_ENCODING_MAP/results/compound_table.txt` — full decomposition table (190 compounds)
- `phases/INSTRUCTION_ENCODING_MAP/results/instruction_map.json` — consolidated results

### Phase 506
- `phases/INSTRUCTION_ENCODING_MAP/scripts/headless_compounds.py` — T8 (headless subgrammar)
- `phases/INSTRUCTION_ENCODING_MAP/scripts/h_terminal_analysis.py` — T9 (h-terminal transparency)
- `phases/INSTRUCTION_ENCODING_MAP/scripts/modifier_order_semantics.py` — T10 (modifier ordering semantics)
- `phases/INSTRUCTION_ENCODING_MAP/scripts/e_versatility_test.py` — T11 (e-atom domain specificity)
- `phases/INSTRUCTION_ENCODING_MAP/results/headless_compounds.json` — T8 results
- `phases/INSTRUCTION_ENCODING_MAP/results/h_terminal_analysis.json` — T9 results
- `phases/INSTRUCTION_ENCODING_MAP/results/modifier_order_semantics.json` — T10 results
- `phases/INSTRUCTION_ENCODING_MAP/results/e_versatility_test.json` — T11 results
