# Glossing System

**Status:** ACTIVE | **Tier:** 3-4 | **Date:** 2026-02-06

---

## Purpose

This document defines the rules, architecture, and conventions for assigning interpretive glosses to Currier B tokens. Glossing is Tier 3-4 speculative work — consistent with structural evidence but not proven by it.

**Read this document before writing ANY glossing code or modifying gloss data.**

---

## Architecture

### Atom-Level Decomposition: `atomize()` (PREFERRED for glossing)

**New scripts should use `morph.atomize()` instead of dictionary-based glossing.**

The atom system (C1394, C1195) decomposes every token into PREFIX + flat atom sequence, where each character maps to one of 18 glossed atoms with positional roles:

```python
morph = Morphology()
a = morph.atomize('qokeedy')
# a.prefix = 'qo'
# a.atoms = [('k','HEAD','heat'), ('e','MOD','cool'), ('e','MOD','cool'),
#            ('d','MOD','mark'), ('y','TERM','end')]
# a.e_depth = 2 (gentle heat / balneum mariae signature)
# a.gloss = 'qo:heat.cool.cool.mark.end'
```

**Why atomize() instead of extract() + dictionaries:**

The traditional MIDDLE/SUFFIX split (via `extract()`) can draw the morphological boundary in the wrong place. The suffix `-edy` greedily absorbs the terminal `e` from compound MIDDLEs, hiding e-depth information (e.g., `kee` becomes `ke` + suffix `edy`). The `atomize()` method bypasses this boundary entirely — the atoms self-organize by their positional preferences (C1209).

**When to use each:**

| Method | Use for | Returns |
|---|---|---|
| `morph.atomize(token)` | Glossing, decoding, recipe alignment | `AtomAnalysis` — flat atom sequence with roles |
| `morph.extract(token)` | Structural constraint analysis, backward-compatible code | `MorphAnalysis` — PREFIX + MIDDLE + SUFFIX split |

**Positional roles:**

| Role | Meaning | Atoms |
|---|---|---|
| HEAD | Domain selector (first atom, C1475) | a, e, o, k, t |
| PSEUDO_HEAD | Headless compound (C1489) | Any non-HEAD atom in first position |
| SOLE | Single-atom instruction (complete in one atom) | Any atom as sole remainder |
| MOD | Modifier/parametrization (interior) | p, f, i, c, d, s (plus HEAD/TERM atoms in interior) |
| TERM | Closure/exit state (last atom) | y, n, m, h, l, r, k, t |

**Terminal opacity (C1440):**

| Opacity | Terminals | Meaning |
|---|---|---|
| OPAQUE | y, n, m | Instruction complete — no continuation |
| SEMI_TRANSPARENT | l, r | Optional continuation atoms |
| TRANSPARENT | h | Instruction incomplete — continuation expected |

**Extension depths (C1197, C1225):**
- `e_depth`: consecutive e's encode stabilization intensity (1=standard, 2=deep/gentle, 3=very deep)
- `i_depth`: consecutive i's encode iteration depth (1=open loop, 2=bounded/safe per C1482)

**Headless compounds (C1488-C1498):**
When the first post-prefix atom is NOT in HEAD_ATOMS {a,e,o,k,t}, the token is headless. The first atom gets role `PSEUDO_HEAD`. Common pseudo-head domains (C1489):
- d → OPERATION (close/mark operations)
- i → TRANSITION (iteration-initial)
- l → STAGING (state/level operations)
- c → parametric operations (C1492: c/p/f-initial = parametric, suffixed)
- s → sequence operations

Example: `dy` → PSEUDO_HEAD:d(mark) + TERM:y(end) = "close, end." Headless tokens typically appear at boundaries (paragraph-initial 2.16x, line-initial 1.8x — C1394 T8).

**Caveats and known limitations:**

1. **k and t are FREE atoms** (C1209) — they have no positional preference. When first, they get HEAD; when last, TERM; when interior, MOD. In a two-atom sequence like `kt`, k=HEAD and t=TERM. This is a convention, not a structural certainty — k and t are genuinely role-dual.

2. **ATOM_GLOSSES confidence varies widely.** 8 atoms are LOCKED (heat, cool, watch, end, iterate, bind, into, final), 6 are SOLID (mark, transfer, state, arrange, adjust, pause), 5 are PLAUSIBLE (flag, sequence, respond, ?, diagram). Do not treat PLAUSIBLE glosses as established. See C1195 for the full tiering.

3. **Secondary prefix (prefix2) not stripped.** `extract()` detects embedded ch/sh after the primary prefix (e.g., `qolchedy` has prefix=qo, prefix2=lch). `atomize()` does NOT strip prefix2 — those characters appear in the atom sequence as MOD atoms. This is intentional: in the unified atom model, the "secondary prefix" is just more instruction atoms.

4. **The MIDDLE/SUFFIX boundary is real structurally** (C1394 T1: 77.1% of MIDDLEs appear with 3+ different suffixes, entropy 1.475 bits; C1440: opacity gradient). `atomize()` bypasses it for glossing but does not invalidate it. The boundary marks where combinatorial freedom shifts (C1440 terminal opacity). Use `extract()` when suffix independence or opacity classification matters for structural constraint work.

5. **Atoms g, q, x are rare/untiered.** g(?) appears in line-final position on ~1 folio each. q appears in post-prefix position only in 3 hapax tokens on f75r — likely transcription edge cases. x = diagram marker (C764). These do not affect normal glossing.

### Two Dictionaries (LEGACY)

| Dictionary | Path | Scope | Entries |
|---|---|---|---|
| **Token Dictionary** | `data/token_dictionary.json` | Individual token glosses | ~8,150 tokens |
| **Middle Dictionary** | `data/middle_dictionary.json` | MIDDLE-level operation glosses | ~1,339 middles |

The middle dictionary is the **semantic core**. Token glosses should reference it, not duplicate it.

### Three Rendering Paths (in `BTokenAnalysis.interpretive()`)

The decoder tries these in order:

1. **Manual token gloss** — If a token has a `gloss` field in the token dictionary, use it directly. If the gloss contains `*middle` references (e.g., `"check *edy."`), expand them from the middle dictionary.

2. **Auto-composition** — If no manual gloss exists but the token's MIDDLE has a gloss in the middle dictionary, compose automatically: `[PREFIX_ACTION] + MIDDLE_MEANING + {FL} + [SUFFIX_GLOSS]`

3. **Structural fallback** — If neither exists, show raw structural notation: `[LANE] middle:kernel [-suffix]`

### The `*middle` Reference Pattern (CRITICAL)

When writing manual token glosses, **always use `*middle` to reference the middle dictionary** instead of hardcoding the middle's meaning:

```
GOOD:  "check *edy."           → expands to "check batch."
GOOD:  "apply *k, set."        → expands to "apply heat, set."
BAD:   "check batch."          → hardcoded, won't update if edy's gloss changes
BAD:   "apply heat, set."      → hardcoded, won't update if k's gloss changes
```

**Why:** When you improve a middle's gloss (e.g., change `k` from "heat" to "fire"), the `*` reference propagates to all tokens automatically. Hardcoded text requires a regex script to update hundreds of tokens.

**Current debt:** As of 2026-02-06, 3,896 glossed token types (22,080/23,096 = 95.6% token coverage). Auto-composition handles most tokens; only 923 are manually curated (5 use `*` references, rest hardcoded). Remaining 4.4% gap = tokens with unglossed middles (all hapax, 2 tokens each).

### PREFIX as Domain Selector (C570, C571, C936)

PREFIX functions as a **domain selector** — it determines WHAT you're acting on, while MIDDLE provides the actual action (C570: 89.6% accuracy; C571: PREFIX selects role, MIDDLE carries material; C661: effect ratio 0.975).

**Domain selector model (Tier 3 semantic labels):**

| PREFIX | Domain Target | Evidence |
|---|---|---|
| ch/sh | the PROCESS (testing, monitoring) | C929: ch=active testing, sh=passive monitoring |
| qo | the HEAT SOURCE (fire/furnace management) | C911: k-family only. Phase 461 T1: k=0.510 |
| ok | the VESSEL TEMPERATURE (coarse thermal verification) | C936, Phase 461 T1: e=0.282, T8 |
| ot | the OPERATIONAL STATE (fine process verification) | C408: ok/ot sister pair. Phase 461 T8, post-phase |
| ol | CONTINUATION (maintaining during active process) | C609, Phase 461 T8 |
| da | the SETUP (infrastructure, apparatus prep) | C911: infrastructure only. Phase 461 T4 |
| sa | the SCAFFOLD (supporting infrastructure) | Phase 461 T1 neg: thermally neutral |

**Same-MIDDLE differentiation examples:**

| ok token | Other token | Shared MIDDLE | Reading |
|---|---|---|---|
| okaiin (vessel: check) | chaiin (test: check) | aiin (check) | Same action, different target |
| okeey (vessel: deep cool) | cheey (test: deep cool) | eey (deep cool) | Cool the vessel vs test cooling |
| okedy (vessel: batch) | chedy (test: batch) | edy (batch) | Batch vessel ops vs test batch |

**Glossing approach:** ok tokens use auto-composition with MIDDLE glosses. The token dictionary does NOT need direct composite glosses — the auto-composition `[PREFIX_DOMAIN] + MIDDLE_ACTION` produces correct readings. Middle dictionary `prefix_composites.ok` fields document the domain relationship.

### When to Use Each Path

| Situation | Action |
|---|---|
| Token is compositional (prefix + middle + suffix) | Let auto-composition handle it via middle dictionary |
| Token needs a special reading | Add manual gloss with `*middle` references |
| Token is an HT-ID (unresolvable compound) | Add manual gloss: `"[HT-ID]."` |
| Token is a bare functional (ar, or, ol, s, y) | Add manual gloss directly (no middle to reference) |

---

## Current Vocabulary (Expert-Validated)

All glosses below have been validated by the expert-advisor agent against the constraint system. Constraint citations indicate the structural evidence supporting each assignment.

### Prefixes (Operation Domain Selectors)

| Prefix | Gloss | Domain | Evidence |
|---|---|---|---|
| ch | test | Active state testing (discrete checkpoint) | C929: pos 0.515, checkpoint suffix 1.87x, followed by close/input/iterate. Brunschwig: finger test, taste test, thumbnail viscosity |
| sh | monitor | Passive process monitoring (continuous observation) | C929: pos 0.396, front-loaded 33% in first 20% of line, followed by heat 18.3%. Brunschwig: drip watching, fire monitoring, color watching |
| qo | heat source | **Heat source control.** k-enriched (0.510), THERMAL 59%. Part of two-channel thermal architecture: qo manages heat input while ok/ot verify vessel response. sh->qo = 1.98x (monitoring triggers heat action). | C644, C911: k-family only. C1313: k-frac=0.510. C1314: overshoot-correct cycling |
| ol | continue / LINK | Morphological component, role-stratified (not unified function) | C609: density, C1174: morphological artifact |
| da | setup | Infrastructure, apparatus prep | C911: infrastructure selector. Phase 461 T4 |
| sa | scaffold | Supporting infrastructure (thermally neutral) | Phase 461 T1 neg: neutral control. Not "dry" (stale). |
| ok | vessel temperature | **Vessel thermal verification (coarse).** ok selects the vessel/apparatus as action target; MIDDLE provides the action. e-enriched (0.282), THERMAL 24.7%. First stage of post-heat-action verification: checks whether vessel temperature has stabilized. ok->ot = 1.18x (coarse precedes fine). Top MIDDLE: aiin (settling). | C936 (revised), C911: e-family + infra. C1313: e-frac=0.282. C1316: ok->ot asymmetry 1.14 |
| ot | operational verification | **Vessel operational verification (fine).** e-enriched (0.258), OPERATION 17.3%. Second stage of post-heat-action verification: checks whether the operation/output is running correctly. Top MIDDLE: edy (batching). Enriched in od (collect), or (portion). Follows ok in preferred sequence qo->ok->ot. | C911: h-family selector. C1316: ot +4.9% OPERATION vs ok. C408: ok/ot sister pair |
| ct | control | Control, hazard management | |

### Extended Prefixes

| Prefix | Gloss | Notes |
|---|---|---|
| pch | stage-test | C1396: paragraph-opener (41.2% par-initial), suffix-heavy (50.6% bare), REGIME_3. p=pause/marking + ch=test. Atom-grounded. |
| tch | transfer-test | C1396: initial-biased (52.9%), REGIME_3 (43.6%), highest Section C. t=transfer + ch=test. Atom-grounded. |
| dch | mark-test | C1396: most line-initial (71.2%). d=mark + ch=test. Atom-grounded. |
| fch | flag-test | f=flag + ch=test. No C1396 profiling (low frequency). Atom-inferred. |
| kch | precision-heat | Retained specific label: k+ch compound. Test 18 |
| lch | hold-test | C1396: sustainer (81.3% bare, REGIME_1 70.5%, 0% par-initial, Section B 40%). l=state + ch=test. Atom-grounded. |
| lk, lsh | hold-heat, hold-monitor | L-compound prefixes. C298: NOT LINK (C609), L-modifier. lk peaks R2 (1.8x). Test 18 |
| ke, te, se, de, pe | heat-burst, transfer-cool, scaffold, divide, start | Compound prefixes. ke updated per C1226. te = "transfer-cool" (C1396: body position, distributed REGIMEs). |
| so, po, do, ko | scaffold, pre-work, mark, heat-work | Compound [C]+o prefixes. so peaks R1 (1.9x, pos 0.190), po peaks R2 (pos 0.107 = line-initial). Test 18 |
| ta, ka | transfer-yield, heat-yield | Compound [C]+a prefixes. ta peaks R2 (1.8x), ka peaks R2 (1.3x, pos 0.570 = late). Test 18 |
| rch, sch | respond-test, sequence-test | Compound [C]+ch prefixes. Atom-inferred from C1394; no C1396 profiling (low frequency). |

### Middles (Operation Types) — Top Frequency

| Middle | Gloss | Kernel | Count | Evidence |
|---|---|---|---|---|
| k | heat | K | 2081 | K-family core, 82% qo-prefix |
| edy | batch | — | 1763 | Universal default middle. Not a misparse of ed+y or e+dy (prep prefix test: pchedy/tchedy). No kernel. Functions as generic object reference ("the work"). Test 24 |
| l | frame | K | 853 | Structural frame |
| e | cool | E | 845 | STABILITY_ANCHOR C105: 54.7% recovery |
| eey | extended cool | E | 615 | Double-e = longer cooling duration. Test 12 |
| ol | continue | K | 759 | Continuation marker |
| r | input | K | 749 | Input/parameter |
| dy | close | K | 594 | Close/seal operation |
| t | transfer | — | 574 | Transfer between stages |
| ke | sustained heat | K | 421 | Peaks R1 (1.6x), NOT R2. F-BRU-017. Test 12 |
| ed | discharge | E | 377 | Kept neutral (expert rejected "drain") |
| o | work | — | 376 | General processing step, C475 universal |
| eo | cool-open | E | 340 | Peaks R2 (1.4x). Extended cooling. Test 12 |
| od | collect | — | 173 | Collect distillate/product |
| ck | direct heat | K | 196 | Peaks R3 (direct fire). Test 12 |
| ek | precision | K | 166 | Peaks R4 (1.5x). Test 12 |
| ee | extended cool | E | 146 | Peaks R2 (1.5x). Double-e = duration. Test 12 |
| eeo | extended cool, work | E | 130 | Peaks R2 (1.7x). Monitored cooling. Test 12 |
| ok | seal | K | 70 | Peaks R2. Sealed vessel (water bath). Test 12 |
| ep | precision cool | E | 16 | Peaks R4 (1.7x). Controlled cooling. Test 12 |
| eol | sustain output | — | 281 | Peaks R3 (3.1x). Sustain output during active distillation. Test 16 |
| s | precise sequence | — | 142 | Peaks R4 (4.1x). Sequential steps, tight tolerance. Test 16 |
| te | rapid gather | — | 87 | Peaks R3 (8.5x). Rapid collection, direct fire. Test 16 |
| eeol | overnight standing | E | 46 | Peaks R2 (8.1x). Brunschwig: "let stand overnight to cool." Test 16 |
| aii | unseal | — | 32 | Peaks R2 (6.1x). Complement of ok(seal). Open vessel after cooling. Test 16 |
| kc | intense heat-seal | K | 33 | Peaks R3 (3.0x). Direct fire closure. F-BRU-020 OIL_MARKER. Test 16 |

### Suffixes (Context Markers)

| Suffix | Gloss | Position | Evidence |
|---|---|---|---|
| -y | done / terminal | Late (0.583) | Step complete marker |
| -dy | close / seal | Balanced (0.528) | Closing operation |
| -hy | verify / maintain | Center (0.504) | Ongoing checking |
| -ey | set / established | **Early (0.435)** | Condition established, proceed. GLOSS_RESEARCH Test 02 |
| -ly | settled / cooled | Late (0.695) | Strong late bias |
| -am | finalize | **Line-final (0.930)** | Almost exclusively last token |
| -aiin / -ain | settle / intake | Early-mid (0.465/0.477) | C561 bigram, C1244 wind-down, F-B-007 iteration. aiin=sustained cycling (a+ii+n), ain=final pass (a+i+n). "Check" applies to or→aiin bigram (C561), not suffix semantics — monitoring is CHSH's job (C929, C1243) |
| -al | complete / transfer | Mid (0.494) | |
| -ar | close | Mid (0.480) | |
| -or | portion | Mid (0.473) | Kept neutral (expert rejected "measure", C469) |
| -s | next / boundary | Early (0.458) | Sequence boundary |
| -edy | (thorough) | — | Compound: most common suffix pattern |
| -eey | extended | Early (0.416) | Double-e = duration + -y = done. R1 peak (1.24x). Test 23 |
| -ry | output | Late (0.748) | C839 OUTPUT marker. S-zone 3.18x enrichment. Test 23 |
| -eol | sustain | Early (0.380) | e-cool + ol-continue. R2 peak (1.51x). Balneum marie sustain. Test 23 |
| -om | work-final | Line-final (0.926) | o-work + m-final. R3 peak (1.49x). Test 23 |
| -im | iterate-final | Line-final (0.876) | i-iterate + m-final. R2 peak (2.60x). Balneum marie iteration. Test 23 |

### Rejected Glosses (Expert Validation)

| Morpheme | Rejected Gloss | Reason | Kept As |
|---|---|---|---|
| ed | "drain" | Too liquid-specific | "discharge" |
| or | "measure" | Implies parametric quantification, C469 | "portion" |
| -ey | "release" | No evidence for release semantics | "set" (Test 02) |
| -ey | "open" | "Opening what?" — too vague | "set" |
| ke | "gentle heat" | Peaks R1 not R2; F-BRU-017 says sustained cycle | "sustained heat" (Test 12) |
| ck | "hard heat" | "Hard" is vague; peaks R3 = direct fire | "direct heat" (Test 12) |
| ee | "deep cool" | "Deep" unclear; double-e encodes duration | "extended cool" (Test 12) |
| ok | "lock" | Not a verb — domain selector (Test 26) | "vessel" (domain selector, C936 revised) |
| ok | "seal/cover/plug" | Composite verb glosses produce word salad at line level (Test 26) | "vessel" (domain selector) |

### Control Flow Loop (Phase 461, Tier 3-4)

Within-line bigram analysis reveals a preferred PREFIX sequencing pattern consistent with a closed-loop control cycle:

```
sh (watch) -> qo (stoke fire) -> ok (check vessel temp) -> ot (check output) -> sh (watch)
   1.98x          1.08x              1.18x                    (return to monitoring)
```

**Key transition ratios (vs chance):**

| Transition | Ratio | Interpretation |
|---|---|---|
| sh -> qo | 1.98x | Passive monitoring triggers heat action (strongest link) |
| qo -> ok | 1.08x | Heat action triggers vessel thermal check |
| qo -> ot | 1.08x | Heat action triggers operations check |
| ok -> ot | 1.18x | Vessel check leads to operations check (coarse then fine) |
| ok -> qo | 0.84x | Vessel check does NOT lead back to heat directly |
| ot -> qo | 0.88x | Operations check does NOT lead back to heat directly |

**Two-stage verification:** After heat action (qo), the operator performs two sequential checks:
1. **ok (coarse):** Is the vessel temperature correct? (THERMAL 24.7%, top MIDDLE: aiin = settling)
2. **ot (fine):** Is the operation running properly? (OPERATION 17.3%, top MIDDLE: edy = batching)

The operator would not fine-tune flow rate if vessel temperature was not stable yet. Neither verification step leads directly back to heat action — passive monitoring (sh) is the gatekeeper for the next heat cycle.

**What sh watches before triggering heat:** 36.7% of sh tokens precede qo. The sh-before-qo position is enriched in OPERATION (+4.4%, especially edy=batch at 1.32x) and depleted in FLOW (ar 0.29x) and STAGING (ol 0.58x). The monitor watches **the ongoing batch operation** and triggers heat when it needs more energy. It does NOT trigger heat after flow endpoints or staging transitions.

| sh->qo enriched | Ratio | Category | Reading |
|---|---|---|---|
| edy (batch) | 1.32x | OPERATION | "batch needs more heat" |
| eck (containment check) | 1.36x | CONTAINMENT | "seal integrity check triggers heat" |
| ect (monitoring) | 1.44x | MONITORING | "monitoring result triggers heat" |

| sh->qo depleted | Ratio | Category | Reading |
|---|---|---|---|
| ar (close/release) | 0.29x | FLOW | flow endpoints do NOT trigger heat |
| ol (continue) | 0.58x | STAGING | staging transitions do NOT trigger heat |
| y (end) | 0.63x | TRANSITION | completion does NOT trigger heat |

**Loop scope: cross-line, not intra-line.** The full sh->qo->ok->ot sequence completes within a single line only 3.3% of the time (48 lines of 2,417). Contiguous 4-token chains (sh-qo-ok-ot adjacent): only 4 lines in the corpus. With mean line length of 8 tokens and 5.2 unique prefixes per line, each line executes one or two steps of the loop, not a complete cycle. The loop is a statistical tendency that emerges across lines. Forward/reverse directionality is 6.0x (strongly directional despite being cross-line).

**Evidence:** C1313 (atom separation), C1314 (overshoot cycling), C1316 (ok->ot ordering). Phase 461 T1, T2, T8, post-phase analysis.

---

## Semantic Ceiling (C171)

> No token-level meaning or translation is recoverable from internal analysis alone.

Glosses indicate **role-level function** (what the token does in the control system), not specific physical actions. We say "heat" not "light the coals under the alembic."

**Permitted:** Verbs, states, transitions, operational modes, method distinctions (direct vs sustained heat)
**Forbidden:** Specific materials, temperatures, quantities, equipment names

**Brunschwig extension (Test 12):** Cross-referencing with Brunschwig fire degree -> REGIME mappings permits finer distinctions within operation families (e.g., "direct heat" vs "sustained heat" vs "precision heat") without violating C171. These are structural method distinctions, not semantic translations.

---

## Expert Validation Workflow

1. **Draft glosses** for a folio (analyze → write gloss script → apply)
2. **Request expert validation** — expert-advisor checks against constraint system
3. **Apply revisions** — fix flagged issues
4. **Document** — rejected glosses go in "Rejected" section above; learned rules go below

### Learned Rules (from expert corrections)

| Rule | Source | Constraint |
|---|---|---|
| k, h, e are bound morphemes — never standalone MIDDLEs | f43v expert review | C540 |
| lk/lch/lsh = L-compound (modified energy), NOT LINK | f43v expert review | C298 |
| LINK = ol substring only | f43v expert review | C609 |
| qe- prefix does not exist — reparse as q+e middle | f43v expert review | C903 |
| -ry suffix = OUTPUT marker | f40v expert review | C839 |
| Compound MIDDLEs are atomic units, not decomposable inline | f26r expert review | — |
| ch+t violates C911 — reparse as ch+te+y | f46r expert review | C911 |
| ch = active state testing, sh = passive process monitoring | GLOSS_RESEARCH Test 20 | C929 |
| "m" MIDDLE = precision marker, not "mass" | f46r expert review | C912 |
| eed = extended stability (C901), not "deep discharge" | f46v expert review | C901 |
| ok is a DOMAIN SELECTOR (vessel), not a verb — MIDDLE provides the action | Test 26: 15 hypotheses, 378 same-MIDDLE pairs | C936 (revised), C570, C571 |
| PREFIX glosses should be domain labels, not action verbs | Test 26: verb glosses = word salad | C936 |
| ok tokens use auto-composition (not direct composite glosses) | Test 26: domain+action = correct reading | C936 |

---

## GLOSS_RESEARCH Phase

**Location:** `phases/GLOSS_RESEARCH/`
**Status:** OPEN (perpetual)

Empirical tests to validate, refine, or reject gloss assignments. Tests and results live in:
- `phases/GLOSS_RESEARCH/scripts/` — test scripts
- `phases/GLOSS_RESEARCH/results/` — JSON output

### Completed Tests

| # | Script | Finding |
|---|---|---|
| 01 | suffix_minimal_pairs.py | Suffixes have distinct positional profiles. -am is line-final (0.930), -ey is early (0.435). 295 stems with minimal pairs. |
| 02 | ey_suffix_context.py | -ey precedes energy operations, -dy follows them. -ey = "set/established." 17 minimal pairs confirm -ey earlier than -dy on same stems. |
| 03 | middle_inventory.py | 75/1339 middles glossed. K-family splits: qo+k-variants = doing heat, ch/sh+k-variants = checking heat. |
| 04 | gloss_format_audit.py | Only 5/923 glossed tokens use *middle references. 918 hardcoded. |
| 05 | middle_sync_check.py | Found 229 misaligned token/middle glosses and 18 stale vocabulary entries. |
| 06 | fix_middle_vocab.py | Applied vocabulary shift to middle dictionary (19 updates). |
| 07 | fix_stale_token_glosses.py | Fixed 40 stale token glosses (release->set, settling->cool, etc). |
| 08 | middle_simplification_preview.py | Preview of collapse: 4 groups (close, check, transfer, deep cool). All accepted as genuine synonyms. |
| 09 | simplify_middles.py | Stripped prefix-verbs from 34 middles. Middles now prefix-independent bare operations. |
| 10 | auto_compose_middles.py | Auto-composed 253 compound middles from glossed atoms. Coverage: 85.3% -> 95.0%. |
| 11 | brunschwig_balneum_marie_test.py | Validated k=heat (R2 lowest), e=cool (R2 highest), ch=check (R2 highest), od=collect (R2 highest). ke peaked R1 not R2 -> "sustained heat" not "gentle heat". |
| 12 | brunschwig_compound_differentiation.py | **K-family 4-way REGIME split:** R1=standard, R2=water bath, R3=direct fire, R4=precision. **E-family R2/R3 split:** double/triple-e = extended cooling (R2), single-e = rapid cooling (R3). 23 gloss refinements. |
| 13 | apply_brunschwig_refinements.py | Applied 23 Brunschwig-derived refinements (ke->sustained heat, ck->direct heat, ee->extended cool, ok->seal, etc). |
| 14 | fix_brunschwig_stale_glosses.py | Fixed 76 token glosses using pre-Brunschwig vocabulary (gentle heat->sustained heat, deep cool->extended cool, lock->seal, cool,open->cool-open). |
| 15 | fix_redundant_glosses.py | Fixed 4 redundant glosses from vocabulary collision (sustain sustained heat->sustained heat, apply seal->seal). |
| 16 | apparatus_discrimination_test.py | **Apparatus signatures by REGIME.** 5/10 PASS, 8/10 partial. R2 = balneum marie cycle (seal->heat->pause->cool overnight->unseal->collect). R3 = per ignem (rapid gather 8.5x, direct heat). R4 = precision (m 4.7x, s 4.1x). Key discovery: aii(unseal) 6.1x R2 = complement of ok(seal). |
| 17 | apparatus_gloss_refinements.py | Applied 12 apparatus-derived refinements (eeol->overnight standing, aii->unseal, te->rapid gather, kc->intense heat-seal, etc). |
| 18 | prefix_regime_discrimination.py | **Prefix REGIME test.** Prefixes less regime-specific than middles (max 2.0x vs 8.5x). Key findings: prep prefixes (fch/tch/pch) cluster R2 (balneum marie), precision prefixes (kch/ct/sch) cluster R4. 12 unglossed compound prefixes identified and glossed (so, ta, ka, po, do, ko, dch, rch, sch). Positional analysis: po=0.107 (line-initial), ar=0.744 (line-final). |
| 19 | suffix_regime_discrimination.py | **Suffix REGIME test. NEGATIVE RESULT.** Suffixes are NOT apparatus-specific (1/9 PASS). Only -am (finalize) peaks R2 correctly. However, suffix POSITIONS shift by regime: -ly shifts 0.241 (late in R3, mid in R4), -ain shifts 0.128 (early in R2, late in R4). Conclusion: suffixes are universal grammar markers. Apparatus info is in middles (high) and prefixes (moderate), not suffixes. |
| 20 | ch_sh_sensory_modality.py | **ch/sh sensory modality discrimination. C929.** ch=active state testing (pos 0.515), sh=passive process monitoring (pos 0.396), delta +0.120. ch gets checkpoint suffixes 1.87x; sh followed by heat 18.3% (monitoring fire), ch followed by input 1.98x and iterate 2.01x (testing then acting). Maps to Brunschwig: sh=drip watching/fire monitoring (continuous), ch=finger test/taste test/thumbnail (discrete sampling). Folio-unique middles amplify delta to +0.156. |
| 21 | fix_ch_sh_glosses.py | Applied C929 vocabulary to 159 token glosses: ch "check"->"test" (106), sh "observe"->"monitor" (45). Compound prefixes initially overcorrected (pch/tch/fch lost prep verbs). |
| 22 | restore_prep_verbs.py | Restored F-BRU-012 prep verbs overcorrected by Test 21: pch="chop" (2), tch="pound" (3), fch="prepare" (3). **SUPERSEDED by C1396:** atom-grounded glosses (pch=stage-test, tch=transfer-test, dch=mark-test, lch=hold-test) replace both Brunschwig verbs and generic "process". **Definitively closed 2026-04-01:** recipe-folio comparison across 10 matched folios shows pch does NOT concentrate on grinding-recipe folios (f83r/Ch9P pch=4 vs f103r/Ch16M pch=7, no grinding). lch dominates uniformly across all recipe types. Compound prefixes are paragraph-opening structural markers (6.5x par-initial enrichment), not preparation operation referents. |
| 23 | full_gloss_refresh.py | **Full refresh.** 5 new suffix glosses (-eey=extended, -ry=output, -eol=sustain, -om=work-final, -im=iterate-final). Auto-composed 2,973 tokens. Token coverage: **67.8% -> 95.6%**. Zero stale prefix fixes needed (Tests 21-22 already caught them). |
| 24 | edy_batch_regloss.py | **Cracked the "standard" problem.** Middle `edy` (1,763 tokens, 5% of B) reglossed from "standard" to "batch." Proved edy is genuine middle, NOT misparse of ed+y or e+dy (prep prefix test: pchedy/tchedy make no sense as "chop cool" or "chop discharge"). Folio-level correlation with e/ed near zero (r~0.13). edy sits in heat-check-heat cycles (26.9% followed by heat). 49 token glosses updated. |
| 25 | ok_three_operations.py + apply_ok_glosses.py | **SUPERSEDED by Test 26.** Originally found three Brunschwig sealing operations (LUTE_JOINTS/PLUG/COVER). Distributional evidence valid but verb-based glosses produce incoherent line readings. |
| 26 | ok_hypothesis_test.py + ok_hypothesis_round2.py + ok_vessel_recipe.py | **ok = VESSEL domain selector.** Tested 15 glossing hypotheses against 10 lines and 5 full folios. Only "vessel" (ok = apparatus target, MIDDLE = action) produces coherent procedures. 378 same-MIDDLE pairs confirm domain differentiation. All verb hypotheses (seal, close, cap, cover, shut, stopper, secure, lute, tend, contain) fail at line level. Revised C936, BCSC v3.2. |

---

## Data Files

### token_dictionary.json

```json
{
  "meta": { "version": "6.0", "glossed": 923 },
  "tokens": {
    "chedy": {
      "gloss": "check *edy.",           // *edy expands from middle dictionary
      "morphology": { "prefix": "ch", "middle": "edy", "suffix": null },
      "notes": "...",
      "fl_state": "...", "fl_meaning": "...", "is_fl_role": false
    }
  }
}
```

### middle_dictionary.json

```json
{
  "meta": { "version": "1.3", "glossed": 75 },
  "middles": {
    "k": {
      "kernel": "K",
      "gloss": "apply heat",
      "token_count": 2081,
      "folio_count": 81
    }
  }
}
```

---

## Encoding Safety (Windows)

**CRITICAL:** Always use `encoding='utf-8'` when reading/writing JSON files on Windows.

```python
# CORRECT
td = json.load(open(td_path, encoding='utf-8'))
with open(td_path, 'w', encoding='utf-8') as f:
    json.dump(td, f, indent=2, ensure_ascii=False)

# WRONG — will crash on Unicode characters and TRUNCATE the file
td = json.load(open(td_path))  # defaults to cp1252 on Windows
```

The `open('w')` mode truncates the file BEFORE writing. If the write fails (encoding error), the file is destroyed. This has happened once already (2026-02-06, token_dictionary.json lost all 8,150 entries).

---

## Recovery

If token_dictionary.json is corrupted, the full gloss state can be rebuilt from scratchpad scripts:

1. Start from a base token dictionary (git or backup)
2. Run `scripts/add_gloss_field.py` (schema upgrade)
3. Run `scripts/add_fl_fields.py` (FL fields)
4. Run all `gloss_*.py` scripts in order (chronological)
5. Run all `revise_*.py` scripts
6. Run vocabulary shift script

The recovery script is at: `scratchpad/recover_all.py` (lists all scripts in order).

---

## Navigation

← [CLAUDE_INDEX.md](CLAUDE_INDEX.md) | [SPECULATIVE/INTERPRETATION_SUMMARY.md](SPECULATIVE/INTERPRETATION_SUMMARY.md) →
