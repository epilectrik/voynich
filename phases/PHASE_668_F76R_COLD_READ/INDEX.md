# Phase 668: Validated Recipe-Folio Correspondence

**Status:** IN PROGRESS
**Started:** 2026-04-27
**Goal:** Validate folio-recipe matches through prediction-first structural assessment, negative controls, expert review, and complete token-level documentation with workshop readings.

## What This Phase Produced

1. **Discrimination methodology** — proved that prediction-first quantitative assessment (not narrative) can distinguish correct from incorrect recipe-folio pairings (4/4 negative controls INCOHERENT, 8/13 positive controls COHERENT)
2. **Two rejected matches** — f77v (furnace spec) and f82v (vessel spec) identified as wrong assignments; both are procedural folios matched to specification chapters
3. **Multi-recipe confirmation** — f82r encodes III.19.1-5 (waters 2-6), not just III.19.3 alone, per C1937
4. **B Dictionary v3** — 52/100 entries revised through two independent expert audits; `e` defaults to "steady" not "cool"; workshop readings tested for sequential coherence
5. **Complete token documentation** — every token on every line shown with workshop reading and source; 96-99% workshop-readable, 1-4% truly unrecognized
6. **Validated folio readings** — recipe text + structural predictions + per-line token tables + cross-paragraph patterns + verdict, for 13 folios

## Approach

For each matched folio:
1. Derive structural predictions from the recipe BEFORE reading the folio
2. Pull SISMEL Catalan recipe text (primary source) with cipher resolved
3. Produce full atom-level decode (prefix, atoms, v3 workshop readings)
4. Assess every token on every line — nothing omitted
5. Check structural features: e-depth arc, dar distribution, prefix shifts, observation MIDDLEs, material markers (fch/cs), counting anchors
6. Compare prediction scorecard against negative control baseline

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
  readings/             ← 13 validated folio readings (one .md per folio)
  data/                 ← raw .txt decodes, .json summaries, workshop tables
  validation/           ← expert controls, positive tests, reviews, v3 audits
  headers/              ← per-folio header templates (recipe, predictions, overview)
  footers/              ← per-folio footer templates (cross-paragraph, verdict)
  _cold_read_reference.md   ← shared atom/prefix/observation reference
  COLD_READ_FINDINGS.md     ← cross-folio patterns (preliminary, pre-expert-review)
```

### readings/ (the validated folio readings)

**Rebuilt with v3 workshop readings (every token, every line):**

| File | Verdict | Status |
|------|---------|--------|
| f75r_cold_read.md | Coherent (8/8) | **v3 rebuilt** |
| f84r_cold_read.md | Coherent (7/9) | **v3 rebuilt** |

**Awaiting v3 rebuild (structural verdicts confirmed, old token format):**

| File | Verdict | Status |
|------|---------|--------|
| f76r_cold_read.md | Coherent (5/8) | v3 tables generated |
| f76v_cold_read.md | Coherent (5/7) | v3 tables generated |
| f79r_cold_read.md | Coherent (5/7) | v3 tables generated |
| f81v_cold_read.md | Coherent | v3 tables generated |
| f112v_cold_read.md | Coherent (6/8) | v3 tables generated |
| f82r_cold_read.md | Coherent (multi-recipe: III.19.1-5) | v3 tables generated |
| f103r_cold_read.md | Partially Coherent (5/7) | v3 tables generated |
| f112r_cold_read.md | Partially Coherent | v3 tables generated |
| f116r_cold_read.md | Partially Coherent (4/7) | v3 tables generated |
| f107r_cold_read.md | Token-analysis only | no recipe |
| f80r_cold_read.md | Token-analysis only | no recipe |

### validation/ (expert testing layer)

| File type | Count | Purpose |
|-----------|-------|---------|
| *_CONTROL.md | 4 | Negative controls (wrong recipe, expert-advisor) |
| *_POSITIVE.md | 11 | Positive controls (right recipe, prediction-first) |
| *_REVIEW.md | 10 | Expert error-check of original readings |
| v3_expert_validation.md | 1 | Expert v3 workshop reading validation (4 folios) |
| v3_crazy_validation.md | 1 | Outsider v3 readability test (4 folios) |

### data/ (raw decode output + workshop tables)

| File type | Count | Purpose |
|-----------|-------|---------|
| *_cold_read.txt | 13 | Line-by-line token decode with prefix, atoms, glosses |
| *_decode_summary.json | 13 | Per-paragraph quantitative stats |
| *_workshop_tables.md | 10 | v3 workshop reading tables (generated) |

### B Dictionary (in `phases/B_OPERATIONAL_DICTIONARY/results/`)

| File | Purpose |
|------|---------|
| b_dictionary_top100.md | Original (D0/D1 seeded, D2+ auto-generated) |
| b_dictionary_top100_v2.md | v2: D2/D3 composed to workshop readings |
| b_dictionary_top100_v3.md | **v3: "steady" not "cool", consistent labels, expert-audited** |
| b_dictionary_audit.md | Expert-advisor audit (34 revisions) |
| b_dictionary_crazy_audit.md | Crazy-expert audit (principles + 10 rewrites) |

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
