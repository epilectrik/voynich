# Phase 668: Folio Cold Reads Against Matched Recipes

**Status:** COMPLETE  
**Started:** 2026-04-27  
**Goal:** Read decoded folios sequentially against their matched Pseudo-Lull Testamentum recipes, judging coherence at the control-grammar level.

## Approach

For each matched folio:
1. Pull the SISMEL Catalan recipe text (primary source)
2. Produce full atom-level decode (prefix, atoms, glosses, e-depth)
3. Identify paragraph structure (gallows-delimited)
4. Read token sequence against recipe operations
5. Check observation MIDDLEs, dar distribution, e-depth profile, and thermal signature

## Folios Read

| Folio | Recipe | Tier | Tokens | Paras | Verdict |
|-------|--------|------|--------|-------|---------|
| f76r | II.16.0 element separation (silver-plate test) | CONFIRMED | 546 | 4 | Coherent |
| f84r | II.12.0 gold dissolution (balneum + putrefaction) | CONFIRMED | 361 | 3 | Coherent |
| f79r | III.12.0 mercury sublimation → elixir | Strong-supported | 389 | 10 | Coherent |
| f103r | III.16.0 ferment multiplication (multi-chamber) | Strong-supported | 522 | 12 | Coherent |
| f82r | III.22.0 fire governance / congelation | Strong-supported | 275 | 9 | Coherent |
| f76v | III.15.0 ferment conversion (liquefaction→multiplication) | Strong-supported | 400 | 6 | Coherent |
| f75r | III.19.0 aqua vitae (×4/×9 reflux distillation) | CONFIRMED | 412 | 9 | Coherent |
| f77v | III.27.0 furnace specification | Supported | 331 | 7 | Plausible |
| f81v | III.18.0 potable gold / water of life | Supported | 258 | 2 | Plausible |
| f82v | III.28.0 vessel specification | Supported | 298 | 8 | Plausible |
| f112r | III.11.0 red mercury tincture (cohobation) | Supported | 394 | 14 | Coherent |
| f112v | III.1.0 lunaria → quicksilver (pipeline origin) | Supported | 415 | 15 | Coherent |
| f116r | III.4.0 fixation / fusibility test | Supported | 537 | 8 | Coherent |
| f107r | III.44.0 quicksilver coagulation | Supported | 488 | 18 | Coherent |
| f80r | III.21.0 animal ash chain (calcination) | Supported | 441 | 7 | Coherent |

## Auxiliary Analyses

| Script | Finding |
|--------|---------|
| middle_on_observers.py | 266 observer-exclusive MIDDLEs corpus-wide, but 211 are hapax. Real observation vocabulary is ~15 common MIDDLEs |
| observer_middle_frequency.py | 92.6% of observer tokens use shared MIDDLEs. Top exclusive: ecth (50 tokens, 21 folios) |
| atom_bigrams_by_prefix.py | Polyalphabetic cipher hypothesis REJECTED: soft atoms d=0.994, o=0.924, r=0.939 cosine similarity across prefix classes |
| cth_across_matches.py | Transfer-watch MIDDLEs present on 11-15 of 15 matched folios with positional correlation to recipe transfer steps |
| h_stacking.py | h (watch) stacks to depth 2 in 1.5% of runs, depth 3 once. 49 hh tokens across 31 folios. Encodes sustained observation |

## Scripts

| Script | Purpose |
|--------|---------|
| decode_f76r.py | Full atom decode of f76r |
| decode_f84r.py | Full atom decode of f84r |
| decode_f79r.py | Full atom decode of f79r |
| decode_f103r.py | Full atom decode of f103r |
| decode_f82r.py | Full atom decode of f82r |
| get_recipe_correct.py | Pull II.16.0 Catalan text |
| get_recipe_f84r.py | Pull II.12.0 Catalan/Latin text |
| get_recipe_f79r.py | Pull III.12.0 Catalan/Latin text |
| get_recipe_f103r.py | Pull III.16.0 Catalan/Latin text |
| get_recipe_f82r.py | Pull III.22.0 Catalan/Latin text |
| middle_on_observers.py | MIDDLE diversity on ch/sh vs qo/ok/ot/ol tokens |
| observer_middle_frequency.py | Frequency distribution of observer-exclusive MIDDLEs |
| atom_bigrams_by_prefix.py | Bigram cosine similarity test (polyalphabetic hypothesis) |
| cth_across_matches.py | Transfer-watch MIDDLEs across all 15 matched folios |
| h_stacking.py | Stacking depth distribution for e, i, h atoms |
| decode_generic.py | Reusable folio decoder (folio + SISMEL prefix args) |

## Results

| File | Contents |
|------|----------|
| f76r_decode_summary.json | Per-paragraph stats for f76r |
| f84r_decode_summary.json | Per-paragraph stats for f84r |
| f79r_decode_summary.json | Per-paragraph stats for f79r |
| f103r_decode_summary.json | Per-paragraph stats for f103r |
| f82r_decode_summary.json | Per-paragraph stats for f82r |
| f76v_decode_summary.json | Per-paragraph stats for f76v |
| f75r_decode_summary.json | Per-paragraph stats for f75r |
| f77v_decode_summary.json | Per-paragraph stats for f77v |
| f81v_decode_summary.json | Per-paragraph stats for f81v |
| f82v_decode_summary.json | Per-paragraph stats for f82v |
| f112r_decode_summary.json | Per-paragraph stats for f112r |
| f112v_decode_summary.json | Per-paragraph stats for f112v |
| f116r_decode_summary.json | Per-paragraph stats for f116r |
| f107r_decode_summary.json | Per-paragraph stats for f107r |
| f80r_decode_summary.json | Per-paragraph stats for f80r |
