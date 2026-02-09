# Glossing System

**Status:** ACTIVE | **Tier:** 3-4 | **Date:** 2026-02-06

---

## Purpose

This document defines the rules, architecture, and conventions for assigning interpretive glosses to Currier B tokens. Glossing is Tier 3-4 speculative work — consistent with structural evidence but not proven by it.

**Read this document before writing ANY glossing code or modifying gloss data.**

---

## Architecture

### Two Dictionaries

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
| qo | the HEAT SOURCE (energy management) | C911: k-family only |
| ok | the VESSEL (apparatus management) | C936: 378 same-MIDDLE pairs, late position |
| da/sa | the SETUP (infrastructure) | C911: infrastructure only |
| ot/ol | the ADJUSTMENT (correction, continuation) | C408: ot=ok sister pair |

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
| qo | energy | Energy domain | C644: energy operations |
| ol | continue / LINK | Continuation, monitoring boundary | C609: LINK operator |
| da | setup | Infrastructure, anchoring | C911: infrastructure selector |
| ok | vessel | **DOMAIN SELECTOR.** ok selects the vessel/apparatus as action target; MIDDLE provides the action. ok+aiin = "check vessel," ok+ar = "close vessel," ok+e = "cool vessel," ok+ai = "open vessel." 378 same-MIDDLE pairs confirm domain differentiation. Late in line (0.538). Sister pair with ot (proactive vs corrective). | C936 (revised), C911: e-family + infra. C570/C571: PREFIX = role selector |
| ot | (scaffold) | Often silent/structural | C911: h-family selector |
| ct | control | Control, hazard management | |

### Extended Prefixes

| Prefix | Gloss | Notes |
|---|---|---|
| pch, tch, kch, fch | chop, pound, precision-heat, prepare | F-BRU-012 prep operations. pch/tch/fch peak R2 (1.4-2.0x). C929: ch=active interaction; chop/pound/prepare ARE active material work. Test 18 |
| lk, lch, lsh | L-compound: modified energy | C298: NOT LINK (C609), L-modifier. lk peaks R2 (1.8x). Test 18 |
| ke, te, se, de, pe | sustain, gather, scaffold, divide, start | Compound prefixes |
| so, po, do, ko | scaffold-work, pre-work, mark-work, heat-work | Compound [C]+o prefixes. so peaks R1 (1.9x, pos 0.190), po peaks R2 (pos 0.107 = line-initial). Test 18 |
| ta, ka | transfer-input, heat-anchor | Compound [C]+a prefixes. ta peaks R2 (1.8x), ka peaks R2 (1.3x, pos 0.570 = late). Test 18 |
| dch, rch, sch | divide-test, input-test, scaffold-test | Compound [C]+ch prefixes. C929: ch=active testing. dch peaks R3 (pos 0.168 = early), rch peaks R2 (1.7x). Test 18 |

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
| -aiin / -ain | check | Early-mid (0.465/0.477) | Verification moment, C561 |
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
| 22 | restore_prep_verbs.py | Restored F-BRU-012 prep verbs overcorrected by Test 21: pch="chop" (2), tch="pound" (3), fch="prepare" (3). These are Brunschwig-grounded active interactions, compatible with C929 (ch=active). |
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
