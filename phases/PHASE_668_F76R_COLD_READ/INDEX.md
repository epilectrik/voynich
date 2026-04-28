# Phase 668: Folio Cold Reads Against Matched Recipes

**Status:** COMPLETE (expert-reviewed)
**Started:** 2026-04-27
**Goal:** Read decoded folios sequentially against their matched Pseudo-Lull Testamentum recipes, judging coherence at the control-grammar level.

## Approach

For each matched folio:
1. Pull the SISMEL Catalan recipe text (primary source)
2. Produce full atom-level decode (prefix, atoms, glosses, e-depth)
3. Identify paragraph structure (gallows-delimited)
4. Read token sequence against recipe operations
5. Check observation MIDDLEs, dar distribution, e-depth profile, and thermal signature

## Methodology Validation

**Generic agent cold reads** (initial pass) produced narrative assessments but lacked discriminative power: 2/4 wrong-recipe controls came back COHERENT. **Expert-advisor agents** (constraint-system-grounded, prediction-first methodology) achieved clean discrimination: 4/4 wrong recipes INCOHERENT, 8/13 right recipes COHERENT.

**Key methodological finding:** Derive quantitative structural predictions from the recipe BEFORE reading the folio (dar count, e-depth arc, counting anchors, material markers fch/cs, apparatus tokens). Post-hoc narrative assessment cannot discriminate same-domain recipes.

### Negative Controls (wrong recipe → folio)

| Folio | Wrong Recipe | Generic Verdict | Expert Verdict |
|-------|-------------|-----------------|----------------|
| f75r | III.21.0 (vessel spec) | INCOHERENT | INCOHERENT (0/7) |
| f84r | III.12.0 (mercury sublim.) | COHERENT | INCOHERENT (0/10) |
| f82r | II.16.0 (sevenfold distill.) | COHERENT | INCOHERENT (0/6) |
| f112v | III.19.3 (short maceration) | PARTIALLY COHERENT | INCOHERENT (0/9) |

## Folios Read (Expert-Reviewed Verdicts)

| Folio | Recipe (SISMEL) | Tier | Tokens | Paras | Expert Verdict | Notes |
|-------|----------------|------|--------|-------|----------------|-------|
| f75r | III.19.0 aqua vitae (x4/x9 reflux) | CONFIRMED | 412 | 9 | **Coherent** 8/8 | Template cold read |
| f84r | II.12.0 gold dissolution (balneum + putrefaction) | CONFIRMED | 361 | 3 | **Coherent** 7/9 | Part II cipher |
| f76r | II.16.0 element separation (silver-plate test) | CONFIRMED | 546 | 4 | **Coherent** 5/8 | Part II cipher; P1=357 tokens |
| f79r | III.12.0 mercury sublimation -> elixir | Strong-supported | 389 | 10 | **Coherent** 5/7 | fch mercury markers in P5 |
| f76v | III.15.0 ferment conversion (liquefaction) | Strong-supported | 400 | 6 | **Coherent** 5/7 | chekar at fusibility test |
| f81v | III.18.0 potable gold / water of life | Supported | 258 | 2 | **Coherent** | fch at L15 rectification |
| f112v | III.1.0 lunaria -> quicksilver pipeline | Supported | 415 | 15 | **Coherent** 6/8 | fch in P1; 3-regime thermal |
| f82r | III.19.1-5 waters 2-6 (multi-recipe) | Strong-supported | 275 | 9 | **Coherent** 4/8 | Upgraded from single-recipe PARTIAL via C1937 |
| f103r | III.16.0 ferment multiplication | Strong-supported | 522 | 12 | **Partial** 5/7 | Ash regime absent; sa-prefix mislocated |
| f116r | III.4.0 fixation / fusibility test | Supported | 537 | 8 | **Partial** 4/7 | Zero fch mercury markers (C1939) |
| f112r | III.11.0 red mercury tincture (cohobation) | Supported | 394 | 14 | **Partial** | P14 e-depth contradicts calcination |
| f107r | (no SISMEL match, sim=0.0) | Supported | 488 | 18 | Token-analysis only | |
| f80r | (no SISMEL match, multi-chapter 21-25) | Supported | 441 | 7 | Token-analysis only | |

### Rejected Matches (removed from this phase)

| Folio | Wrong Recipe | Reason |
|-------|-------------|--------|
| f77v | III.20.0 furnace specification | Procedural folio (dar=32) vs specification chapter |
| f82v | III.21.0 vessel specification | Procedural folio (dar=13) vs specification chapter |

Both need new recipe assignments. All f77v/f82v files deleted from this phase.

## Directory Structure

```
results/
  cold_reads/           ← 13 narrative cold reads (one .md per folio)
  data/                 ← raw .txt decodes and .json paragraph summaries
  validation/           ← expert controls, positive tests, and reviews
  _cold_read_reference.md   ← shared atom/prefix/observation reference
  COLD_READ_FINDINGS.md     ← cross-folio patterns (pre-expert-review, preliminary)
```

### cold_reads/ (the cold reads)

| File | Verdict |
|------|---------|
| f75r_cold_read.md | Coherent |
| f76r_cold_read.md | Coherent |
| f76v_cold_read.md | Coherent |
| f79r_cold_read.md | Coherent |
| f81v_cold_read.md | Coherent |
| f82r_cold_read.md | Coherent (multi-recipe: III.19.1-5) |
| f84r_cold_read.md | Coherent |
| f112v_cold_read.md | Coherent |
| f103r_cold_read.md | Partially Coherent |
| f112r_cold_read.md | Partially Coherent |
| f116r_cold_read.md | Partially Coherent |
| f107r_cold_read.md | Token-analysis only |
| f80r_cold_read.md | Token-analysis only |

### validation/ (expert testing layer)

| File type | Count | Purpose |
|-----------|-------|---------|
| *_CONTROL.md | 4 | Negative controls (wrong recipe, expert-advisor) |
| *_POSITIVE.md | 11 | Positive controls (right recipe, prediction-first) |
| *_REVIEW.md | 10 | Expert error-check of cold reads |

### data/ (raw decode output)

| File type | Count | Purpose |
|-----------|-------|---------|
| *_cold_read.txt | 13 | Line-by-line token decode with prefix, atoms, glosses |
| *_decode_summary.json | 13 | Per-paragraph quantitative stats |

## Auxiliary Analyses

| Script | Finding |
|--------|---------|
| middle_on_observers.py | 266 observer-exclusive MIDDLEs corpus-wide, but 211 are hapax. Real observation vocabulary is ~15 common MIDDLEs |
| observer_middle_frequency.py | 92.6% of observer tokens use shared MIDDLEs. Top exclusive: ecth (50 tokens, 21 folios) |
| atom_bigrams_by_prefix.py | Polyalphabetic cipher hypothesis REJECTED: soft atoms d=0.994, o=0.924, r=0.939 cosine similarity across prefix classes |
| cth_across_matches.py | Transfer-watch MIDDLEs present on 11-15 of 15 matched folios with positional correlation to recipe transfer steps |
| h_stacking.py | h (watch) stacks to depth 2 in 1.5% of runs, depth 3 once. 49 hh tokens across 31 folios. Encodes sustained observation |

## Outstanding Work

- **f77v and f82v need new recipe assignments** -- both are procedural folios incorrectly matched to specification chapters
- **COLD_READ_FINDINGS.md** contains pre-review verdicts and should be treated as preliminary
