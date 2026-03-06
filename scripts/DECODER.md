# B Folio Decoder (`show_b_folio.py`)

Command-line tool for rendering Currier B folios with structural annotations derived from the constraint system.

> **Work in progress.** The decoder is under active development. Gloss labels, rendering modes, and annotation layers evolve as new constraints are validated. Outputs are structural projections, not translations — treat labels as display tokens subject to revision. Check back for updates.

## Quick Start

```bash
python scripts/show_b_folio.py f75r          # Default table view
python scripts/show_b_folio.py f75r -p       # Paragraph view
python scripts/show_b_folio.py f75r --flow   # Control-flow view
python scripts/show_b_folio.py f75r --ir     # Control IR (typed blocks)
python scripts/show_b_folio.py f75r --profile          # Program card (Tier 2)
python scripts/show_b_folio.py f75r --profile --interp  # Card + Tier 3-4
python scripts/show_b_folio.py f75r -s       # Raw morpheme structural view
```

---

## Rendering Modes

The decoder has **6 rendering modes**, each showing the same tokens at a different level of abstraction.

### 1. Default Table (no flags)

Token-per-row table with three columns: TOKEN, CALCULATED gloss, MANUAL gloss.

```
TOKEN          | CALCULATED                          | MANUAL GLOSS
kchedy         | precision-heat cool-mark-end[e]     | -
qokar          | heat[k] , [close]                   | -
shedy          | monitor cool-mark-end[e]            | -
```

- **TOKEN**: Raw Voynich word
- **CALCULATED**: Auto-composed gloss from PREFIX + MIDDLE + SUFFIX mappings
- **MANUAL**: Hand-assigned gloss from `data/token_dictionary.json` (currently all empty — glosses lost in encoding crash, replaced by auto-composition)

**Gloss composition** (CALCULATED column):
- PREFIX is looked up in `_PREFIX_GLOSS` (e.g., `qo` = "heat-src", `sh` = "monitor")
- MIDDLE is expanded character by character using atom glosses (C1195): `k`=heat, `e`=cool, `h`=watch, etc.
- SUFFIX is shown as a bracketed hint (e.g., `[close]`, `[thorough]`, `[check]`)
- Kernel markers `[k]`/`[e]`/`[h]` indicate which kernel operator dominates the MIDDLE
- `(FL)` marks tokens in the FL census (C582)

**Special token types:**
- `[ident: X.Y.Z]` — Dark Pipeline (DP) tokens (C1137). MIDDLE characters expanded with atom glosses.
- `[hold-light]` — Human Track (HT) tokens. Frozen posture grammar, not operationally glossed.

**Flags:**
- `--no-token` — Hide token column
- `--no-calc` — Hide calculated gloss column
- `--no-manual` — Hide manual gloss column
- `--tokens-only` — Show only tokens (shortcut for `--no-calc --no-manual`)
- `--line N` — Show only line N
- `--detail N` — Detail level (1-4, default 2). Level 4 shows full metadata per token: macro state, hub role, affordance bin/family, prefix zone, terminal group, compound depth/atoms, DP flag, suffix continuation, prefix decomposition, HEAD+MOD*+TERM decomposition (hmt:), frame, opacity tier, frame hazard, safe pathway flag, i-modifier count, quenching modifier flag. Also shows HT structural internals (prefix/middle/suffix/kernel).

### 2. Structural Mode (`-s` / `--structural-mode`)

Same table layout as default, but the CALCULATED column shows raw morpheme notation instead of English glosses. Useful for cross-folio comparison without gloss interpretation.

```
kchedy         | precision-heat edy[e]              | -
qokar          | k[k] (ar)                          | -
shedy          | monitor edy[e]                     | -
```

MIDDLE is shown as raw characters, not expanded to English. PREFIX still uses its label. Suffix shown raw.

### 3. Paragraph View (`-p` / `--paragraph`)

Groups tokens by line, showing three layers per line plus a prefix chain.

```
L1: ___ ___ ___ ___ ___ ___ ___ ___
    precision-heat cool-mark-end[e] heat-yield input-end vessel-temp cool-cool-end[e] ...
    [kchedy kary okeey qokar shy kchedy qotar shedy]
    pfx: kch > ka > ok > qo > sh > kch > qo > sh
```

- **Line 1**: Manual glosses (or `___` if none)
- **Line 2**: Calculated glosses (auto-composed)
- **Line 3**: Raw tokens in brackets
- **Line 4**: Prefix chain — sequence of PREFIX morphemes for the line, showing control flow

The header shows paragraph structure: `STRUCTURE: P1(L1-L5), P2(L6-L6), ...`

Use `--no-calc` to hide the calculated gloss line.

### 4. Flow View (`--flow` / `-f`)

Control-flow rendering showing operation semantics, FL stages, and macro states.

```
L1 [HEADER]: precision-heat cool-mark-end -> heat-yield input-end -> vessel-temp cool-cool-end <e> | [QO] heat <k> [CLOSE] | monitor end -> ...
    macro: AXM --- FQ AXM AXM AXM AXM AXM
    [kchedy kary okeey qokar shy kchedy qotar shedy]
```

- **Operations** are joined by `->` (cross-phase), `|` (work-to-work), or `=` (suffix continuation/batch repetition)
- **`(FL:STAGE)`** markers appear inline on FL-role tokens with their stage (INITIAL, EARLY, MEDIAL, LATE, TERMINAL)
- **`[FLOW_LABEL]`** shows control-flow labels like `[CLOSE]`, `[CHECKPOINT]`, `[VERIFY]`, `[THOROUGH]`
- **Kernel markers**: `<k>` = heat, `<e>` = cool, `<h>` = watch
- **`macro:` line** shows macro state sigils per token: AXM (active), FL (flow-layer), CC (control-change), `---` (no macro)
- **`!!`** (red): High frame hazard token (C1448)
- **`~~`** (green): Safe pathway token (e→y, C1457)
- **Zone tag**: `[HEADER]`, `[BODY]`, or `[TAIL]` per C747/C963

### 5. Control IR (`--ir`)

The most detailed mode. Renders each line as a typed control block with tokens grouped by role.

```
L1 [B] [HEADER] kern(e:4 k:1) cat:OP:37%/TR:25%/TH:25%  EN:CHSH:2 EN:QO:2 AX:2
  | final:OPEN
  HT_UN { 2:kary[HT/UN|pred:AX] }
  WORK {                                    # unordered (C961)
    EN:CHSH: 5:shy[EN:CHSH|c31] 8:shedy[EN:CHSH|c8]
    EN:QO:   4:qokar[EN:QO|c32] 7:qotar[EN:QO|c36]
    AX:      1:kchedy[AX:INIT|c26] 6:kchedy[AX:INIT|c26]
  }
  CHECK { 3:okeey[FQ:PREFIXED|c13] }
  # T3 {unordered}
  #   1: kchedy = [AX] (precision-heat) cool.mark.end [OP]
  > kchedy kary okeey qokar shy kchedy qotar shedy
```

**Line header fields:**
- **Mode marker**: `[A]` = specification (suffix-heavy) or `[B]` = continuation (bare-heavy), per C1229-C1231
- **Zone**: `[HEADER]`, `[BODY]`, `[TAIL]`
- **`kern()`**: Kernel distribution as multiset (k=heat, h=watch, e=cool counts)
- **`cat:`**: Top-3 operational categories with percentages (C1250)
- **Role counts**: EN:CHSH, EN:QO, AX token counts in WORK zone

**Detail line** (`|`):
- **`loop:`**: Control loop markers (C1234) — `setup(word)` for line-initial iteration, `check(word)` for penultimate check
- **`final:`**: Line-final type (C1235/C1237) — FINALIZE, LOOP_CHECK, TERMINAL, CLOSE, ROUTE, or OPEN

**Zones** (C556 prefix-phase routing):
- **SETUP**: CC census tokens (C581) and SETUP-phase tokens
- **HT_UN**: Human Track (C740) and Dark Pipeline (C1137) tokens — excluded from operational grammar
- **WORK**: Core operational tokens, grouped by role then lane:
  - `EN:CHSH` — Engine tokens, monitor lane (ch/sh prefixes)
  - `EN:QO` — Engine tokens, energy lane (qo prefix)
  - `AX` — Axial/scaffold tokens (positional sub-labels: INIT/MED/FINAL per C563)
- **CHECK**: FQ census tokens (C583) and AX_LATE role tokens
- **FL**: FL census tokens (C582) with stage annotations
- **CLOSE**: CLOSE-phase tokens

**Token notation**: `position:word[ROLE:SUB|cN]`
- `cN` = 49-class grammar number (C121)
- `|zb:` = zone basis audit trail (shown only for non-census routing): `ph=prefix_phase`, `r=prefix_role`
- `pred:X` on HT/UN tokens = C611 PREFIX morphology prediction (99.2% accuracy) — affinity, not classification
- `*word*` = Dark Pipeline token
- `FQ:CONN/PREFIXED/CLOSER` = FQ sub-grouping (C593)

**T3 annotations** (Tier 3, commented):
- Character-level kernel expansion of MIDDLE using C1195 atom glosses
- Category-hazard indicator: `[TH.]` = thermal/low-hazard, `[FL!]` = flow/high-hazard, `[OP]` = operation/neutral
- Frame annotation: `{e->y}` = HEAD→TERM frame (C1393, C1448)
- Hazard refinement: `!!HAZ` = high frame hazard, `~IMMUNE` = k-HEAD neutralization, `~SAFE` = e→y safe pathway
- Modifier annotation: `[Q]` = quenching mod (c,d,f,p,s), `[i]`/`[ii]` = iteration count, `[i+Q]` = both (C1450-C1456)

**Paragraph header** (above each paragraph's lines):
```
-- P1 (K-gallows, 5L/46T) k43/h8/e47 EN:34% key:[TH|TR|FL] modes=[BBBA](33%) tail=PROCESS_HEAVY term:- ----
```
- Gallows type, line/token count, kernel percentages, EN percentage
- `key:` = category key (C1308) — top categories
- `modes=` = suffix mode sequence with interleave rate (C1229-C1232)
- `tail=` = tail product signature
- `term:` = paragraph termination type (C1237), `AM(word)` or `-`

### 6. Profile Mode (`--profile`)

Folio-level program card — a statistical summary without per-token output.

```
PROGRAM CARD: f75r                                              [Tier 2]
  Section: B - "Bathing/Biology" | BIO
  Kernel: k=43.3% [+12pp z=1.3]  h=4.7% [-12pp* z=2.1]  e=52.0% [~avg]
  Roles: EN ~avg | AX ~avg | CC 2.7x z=1.2
  REGIME: REGIME_1 (100%) (C494)
  Archetype: 6 - HAZARD_TOLERANT (C1016)
```

**Fields:**
- **Kernel**: k/h/e percentages with deviation from corpus average (pp = percentage points, z = z-score, `*` = significant)
- **Roles**: EN/AX/CC distribution relative to average
- **REGIME**: Regime assignment and probability (C494)
- **Archetype**: Folio archetype (C1016)

**STRUCTURAL PROFILE**: QO-lane %, sister ch %, ol-morph %, forgiveness, hazard density

**VOCABULARY**: Bridge/dark ratios, unique MIDDLE count, compound %, AXM vocab size and residual

**PARAGRAPH SUMMARY**: Table of all paragraphs with gallows type, kernel distribution, role, size, suffix type %, mode sequence, and tail signature.

**`--interp` flag**: Adds Tier 3-4 interpretive blocks (material hypothesis, output hypothesis, operational gloss). Only works with `--profile`.

Profile mode is composable: `--profile -p` shows the card then paragraph view; `--profile --ir` shows the card then Control IR.

---

## Filtering Options

| Flag | Effect |
|------|--------|
| `--line N` | Show only line N |
| `--para N` | Show only paragraph N (works with `-p`, `--flow`, `--ir`) |
| `--no-color` | Disable ANSI color output |
| `--debug-ht` | Show HT atom details in default mode |

---

## Color Scheme

When `colorama` is installed, tokens are colored by functional role:

| Color | Role | Meaning |
|-------|------|---------|
| Red | QO | Energy/heat lane |
| Cyan | CH/SH | Monitor/test lane |
| Yellow | CC | Control-change |
| Light blue | FL | Flow-layer state |
| Green | AX | Scaffold/axial |
| Light green | PREP | Preparation tier |
| Magenta | DP | Dark pipeline (C1137) |
| Dim white | HT | Human track (C740) |
| White | BARE | Bare/unclassified |

**Category colors** (C1250, shown in IR mode headers):
TH=red, FL=blue, CN=yellow, ST=green, OP=white, TR=magenta, MK=cyan, MN=light blue

**Mode colors**: `[A]`=warm yellow (specification), `[B]`=cool cyan (continuation)

Use `--no-color` for piping output or terminals without ANSI support.

---

## Gloss Sources

The decoder composes glosses from multiple data sources:

| Source | File | What it provides |
|--------|------|-----------------|
| PREFIX glosses | `_PREFIX_GLOSS` in show_b_folio.py | Prefix → operational label (e.g., `qo`→"heat-src") |
| Atom glosses | `_CHAR_GLOSS` / C1195 | Single character → kernel meaning (e.g., `k`→"heat") |
| Suffix glosses | `_SUFFIX_GLOSS` | Whole suffix → control label (e.g., `ar`→"close") |
| Decoder maps | `data/decoder_maps.json` | Canonical prefix/suffix/category mappings |
| MIDDLE dictionary | `data/middle_dictionary.json` | 91 learned MIDDLE glosses (IR mode T3 only) |
| Token dictionary | `data/token_dictionary.json` | Whole-token manual glosses (currently empty — structural metadata only) |

**Gloss pipeline** (CALCULATED column): Compound MIDDLE decomposition → character-level atom expansion (C1195). PREFIX and SUFFIX labels are composed around the MIDDLE gloss. MiddleDictionary and F-BRU tier labels are bypassed in favor of transparent atom expansion.

**DP tokens** use character-level expansion of MIDDLE with dot-separated atom glosses: `[ident: frame.adjust.watch]`.

**HT tokens** show `[hold-light]` (frozen posture grammar) — never operationally glossed.

---

## Key Constraints Referenced

| Constraint | What it governs |
|------------|----------------|
| C121 | 49 grammar classes |
| C556 | Prefix phase (SETUP/PREP/WORK/CLOSE) |
| C563-C572 | AX positional stratification |
| C573, C581-C583 | BCSC role census (CC/EN/AX/FQ/FL) |
| C574 | EN-internal lanes (QO/CHSH) |
| C582 | FL census classes (7, 30, 38, 40) |
| C593 | FQ sub-groups (CONN/PREFIXED/CLOSER) |
| C611 | PREFIX→role prediction (99.2%) |
| C740 | HT/UN exclusion from 479-type grammar |
| C747, C963 | Paragraph zone (HEADER/BODY/TAIL) |
| C855 | Paragraphs as independent parallel programs |
| C961 | WORK zones are unordered sets |
| C1004 | Suffix hint is not FL state |
| C1016 | Folio archetypes and forgiveness |
| C1137 | Dark pipeline subset |
| C1195 | Character-level atom glosses |
| C1229-C1232 | Suffix mode cycling (A/B) |
| C1234 | Control loop iteration markers |
| C1235, C1237 | Line-final / paragraph termination |
| C1250 | 8-category operational classification |
| C1280 | Category-hazard association |
| C1393-C1394 | HEAD+MOD*+TERM positional grammar |
| C1440 | Three-tier terminal opacity gradient |
| C1446 | k-HEAD complete hazard immunity |
| C1448 | HEAD x TERM frame hazard map |
| C1450 | Modifier quenching (c,d,f,p,s → 0% hazard) |
| C1452-C1456 | i-modifier hazard (Simpson's paradox) |
| C1457-C1462 | e→y safe pathway / stability anchor |

---

## Examples

```bash
# Browse a folio quickly
python scripts/show_b_folio.py f75r -p --no-color

# Deep-dive a single paragraph
python scripts/show_b_folio.py f75r --ir --para 4 --no-color

# Get folio statistics then detailed view
python scripts/show_b_folio.py f75r --profile -p

# Compare raw morphemes across folios
python scripts/show_b_folio.py f75r -s --no-color > f75r_struct.txt
python scripts/show_b_folio.py f82r -s --no-color > f82r_struct.txt

# Full metadata dump for a specific line
python scripts/show_b_folio.py f75r --detail 4 --line 3

# Pipe-friendly (no colors, just tokens)
python scripts/show_b_folio.py f75r --tokens-only --no-color
```
