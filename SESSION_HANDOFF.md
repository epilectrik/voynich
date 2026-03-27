# Session Handoff: Crib Decode & Cross-Folio Analysis

**Date:** 2026-03-26/27
**Last commit:** `903f7a7` (Phase 629 complete, C1891-C1896)
**Current branch:** master
**Status:** Exploratory work in progress (NOT committed — all scripts are `_prefixed` throwaway)

---

## What We've Been Doing (Phases 626-629 + Exploratory)

### The Big Picture

We've been matching individual chapters from the **Pseudo-Lull Testamentum** (a medieval alchemical text, 209 chapters) to individual **Voynich manuscript folios** (83 in Currier B), using an 8-dimensional residual feature matching system. Then we've been doing **crib decodes** — using the known recipe content as a key to read the Voynich tokens.

### Phase 626-629 Summary

| Phase | What | Verdict | Constraints |
|-------|------|---------|-------------|
| 626 | A-to-B Bridge Decomposition | BRIDGE_FEATURE_COHERENT_NOT_HOLISTIC | C1859-C1870 |
| 627 | Per-Domain Bridge Calibration | CHANNEL_DISCRIMINATIVE_NOT_STRUCTURALLY_CALIBRATED | C1871-C1881 |
| 628 | Individual Recipe-to-Folio Correspondence | INDIVIDUAL_MATCHING_VALIDATED | C1882-C1890 |
| 629 | Crib Decode Validation | CONTENT_VALIDATED | C1891-C1896 |

**Key result from Phase 628:** The permutation test passed (p<0.05) — individual chapter-to-folio matching is statistically real, not just regime-level gradient noise. 9/16 distillation chapters matched confidently to R1 folios.

**Key result from Phase 629:** Content validation of the two strongest matches (Ch19→f75r, Ch18→f76r) produced 6 independent structural confirmations per folio. Verdict: CONTENT_VALIDATED.

### Post-Phase 629: The Exploratory Sprint (THIS SESSION)

After the formal phases, we went deep on exploratory analysis. None of this is committed yet. Here's what happened:

---

## The 5 Recipe-Folio Matches

| Folio | PL Chapter | Recipe | Ratio | CV% | Status | Folio Notes |
|-------|-----------|--------|-------|-----|--------|-------------|
| **f75r** | Ch19 | Aqua vitae (9x reflux, balneum mariae) | 1.317 | 69.6% | **CONFIRMED** (Phase 629) | [f75r.md](context/FOLIOS/f75r.md) |
| **f76r** | Ch18 | Element separation (silver-plate purity test) | 1.707 | 78.6% | **CONFIRMED** (Phase 629) | [f76r.md](context/FOLIOS/f76r.md) |
| **f77v** | Ch27 | Furnace specification (3 fire regimes) | 2.805 | 83.4% | Supported match | [f77v.md](context/FOLIOS/f77v.md) |
| **f84r** | Ch14 | Gold dissolution (balneum mariae + putrefaction) | 2.097 | 84.0% | Supported, approaching confirmed | [f84r.md](context/FOLIOS/f84r.md) |
| **f108r** | Ch16 | Two-phase element separation | 1.348 | 76.6% | Statistical match, blind test FAILED | [f108r.md](context/FOLIOS/f108r.md) |

**Local clustering discovery:** f75r, f76r, f77v are **three consecutive folios** matching nearby PL chapters (Ch19, Ch18, Ch27 — all in the same PL part). This isn't just individual matches — there's a neighborhood correspondence.

---

## Cross-Folio Crib Analysis: Candidate Decoded Words

This is the most exciting result of the session. By looking for tokens that behave consistently across MULTIPLE independently-matched folios, we found:

### `chekar` (ch + ek + ar) — "active quality check → result"

- Present on ALL 3 balneum mariae folios: **f75r** (L43), **f84r** (L29), **f108r**
- Only appears on **7/83 folios** total (12.95x enriched on balneum folios)
- The other 4 folios with chekar (f33r, f34r, f94r, f95r1) are **untested predictions** — they should describe water-bath procedures
- Context is identical across folios: always preceded by thermal/dar tokens, always followed by monitoring tokens
- Probability of appearing on all 3 balneum folios by chance: **p ≈ 0.0004**
- ABSENT from f76r (correct negative — Ch18 uses silver-plate test, NOT balneum)
- Script: `_balneum_crib_analysis.py`, `_balneum_crib_deep.py`, `_balneum_crib_final.py`

### `dar` — "material addition (thermal context)"

- f84r is #1 in entire corpus (13 occurrences), f75r is #2 (10 occurrences)
- Canonical context: THERMAL → dar → MONITOR (add material while hot, then watch)
- `dal` = material addition in PASSIVE/cold context (monitoring-dominant surroundings)
- f75r's **double-dar** (L35-36) is unique in all Currier B — maps to Ch19's two materials (honey + wax)
- Script: `_analyze_dar_dal.py`

### `qokal` (qo + k + al) — "heat source → heat → terminal/endpoint"

- 18 occurrences on f77v alone (structural backbone of the furnace specification folio)
- Enriched 2.69x on matched folios overall, 18x on f77v specifically
- Reading: fire/heat endpoint — "the fire reaches completion"
- Script: `_cross_folio_crib_analysis.py`

### The `ek`-MIDDLE Family — "quality assay/check"

| Token | Decomposition | Reading | Where |
|-------|--------------|---------|-------|
| chekar | ch + ek + ar | Active quality check → result | f75r, f84r, f108r (balneum folios) |
| chekain | ch + ek + ain | Active quality check → intake/input | f76r (silver-plate test zone) |
| chekear | ch + ek + e + ar | Active extended quality check → result | f76r only (folio-unique) |
| shekar | sh + ek + ar | Passive quality check → result | Various |
| shekedy | sh + ek + edy | Passive quality check → batch/cycle | Various |

The ek-MIDDLE consistently encodes quality assurance operations. The PREFIX determines active (ch) vs passive (sh) mode.

### The `qok-` Suffix Rotation System

Same prefix+middle, different suffixes encoding different operations:

| Token | Suffix | Meaning |
|-------|--------|---------|
| qokedy | -edy | Thermal cycle-close (one heat cycle done) |
| qokain | -ain | Thermal intake (apply heat input) |
| qokal | -al | Thermal endpoint (fire reaches completion) |
| qokar | -ar | Thermal output/result |
| qokaiin | -aiin | Thermal binding (sustained settling) |
| qokey | -ey | Thermal check/verify (is heat correct?) |

This suffix rotation appears across the matched folios — the same PREFIX+MIDDLE core takes different suffixes to encode different phases of the same operation.

---

## The Atom-Level Full Decode (Final Discovery)

The last thing we did was realize we were being stupid treating MIDDLEs as opaque blobs. The constraint system (C1195, C1394) says MIDDLEs decompose into **HEAD + MOD* + TERM** with all 18 atoms glossed:

- **HEAD:** k(heat), e(cool), a(yield), o(arrange), t(transfer)
- **MOD:** p(pause), f(flag), i(iterate), c(adjust), d(mark), s(sequence)
- **TERM:** l(state), r(respond), h(watch), y(end), m(final), n(halt)

Combined with the PREFIX domain selectors and SUFFIX context markers, this gives **100% glossing coverage** of every token. The auto-composition system in `data/token_dictionary.json` and `data/middle_dictionary.json` already handles 95.6% of tokens.

We ran a full atom-level decode of f76r (`_full_decode_f76r_v2.py`):
- 91.9% from middle dictionary, 6.4% auto-composed, 1.6% raw atom fallback
- Zero unknowns
- Paragraph-level PREFIX distributions match recipe phases exactly
- P3 verification spike (ok/ot → 23%) matches the washing step
- Readable operational sequences trace the same procedure Ch18 describes

### What the Decode CAN Do
- Read every token as an operational instruction (domain + action + modifier + exit state)
- Trace procedure sequences that match the PL recipes
- Show paragraph-level functional shifts (thermal → monitoring → correction → convergence)

### What the Decode CANNOT Do
- Name specific materials, vessels, or temperatures (semantic ceiling, C171)
- Translate tokens into natural language sentences
- Identify substances (chekar = "quality check," not "balneum mariae" — the external reference provides that)

---

## Key Exploratory Scripts (All Uncommitted, All `_prefixed`)

All in `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/`:

| Script | What It Does |
|--------|-------------|
| `_decode_f77v_comprehensive.py` | Paragraph-level analysis of f77v (furnace spec) |
| `_blind_test_f108r.py` | Blind prediction test for Ch16→f108r (FAILED) |
| `_blind_test_f84r.py` | Blind prediction test for Ch14→f84r (MIXED) |
| `_decode_f84r_posthoc.py` | Post-hoc structural analysis of f84r |
| `_decode_f84r_deep.py` | Deep header+body zone analysis of f84r |
| `_decode_f108r_ch16_content.py` | Operational content comparison Ch16 vs f108r |
| `_balneum_crib_analysis.py` | Cross-folio balneum token analysis |
| `_balneum_crib_deep.py` | Deep balneum token distribution |
| `_balneum_crib_final.py` | Final balneum synthesis |
| `_analyze_dar_dal.py` | dar/dal material addition analysis across corpus |
| `_cross_folio_crib_analysis.py` | qokal, shared vocabulary, enrichment analysis |
| `_analyze_f84r_headers.py` | f84r header morphological analysis |
| `_analyze_f84r_headers_v2.py` | f84r header 3×4 grouping analysis |
| `_crib_decode_f75r_ch19.py` | Side-by-side f75r vs Ch19 |
| `_decode_f76r_ch18_sidebyside.py` | Side-by-side f76r vs Ch18 |
| `_crib_f84r_ch14.py` | Side-by-side f84r vs Ch14 |
| `_full_decode_f76r.py` | First decode attempt (WRONG — treated MIDDLEs as opaque) |
| `_full_decode_f76r_v2.py` | Correct atom-level decode (100% coverage) |

---

## Folio Notes Updated This Session

| Folio | Status | File |
|-------|--------|------|
| f76r | Updated with full crib decode findings (2026-03-26) | `context/FOLIOS/f76r.md` |
| f77v | **Created** | `context/FOLIOS/f77v.md` |
| f84r | **Created** | `context/FOLIOS/f84r.md` |
| f108r | **Created** | `context/FOLIOS/f108r.md` |
| INDEX | Updated with f77v, f84r, f108r entries | `context/FOLIOS/INDEX.md` |

---

## Where We Left Off / What To Do Next

### The User's Final Question
> "So what's stopping you from doing a token for token full decode now that we have hard external references?"

### The Answer We Arrived At
The atom system gives 100% operational coverage. The PL recipes provide content context. Together they produce readable operational procedures. But the atoms alone encode FUNCTION (heat, cool, check, transfer), not CONTENT (silver, mercury, honeycomb). The external references are what supply content — the Voynich tokens encode the control program for EXECUTING a recipe, not describing it.

### Concrete Next Steps (Pick Any)

1. **Test the chekar prediction** — the 4 other folios with `chekar` (f33r, f34r, f94r, f95r1) should describe water-bath procedures. This is a real falsifiable prediction.

2. **Full atom decode of f75r** — we did f76r; now do f75r with the same atom-level approach and compare side-by-side with Ch19. The double-dar, 4x qokedy run, and paragraph progression should all be readable.

3. **Formalize as Phase 630** — the cross-folio vocabulary analysis (chekar, dar, qokal, suffix rotation) is strong enough for a formal phase with constraints. Could include the chekar prediction as P1.

4. **Decode more confidently-matched folios** — there are 9 confident distillation→R1 matches. We've deeply analyzed 5. The remaining 4 could have cross-folio patterns we're missing.

5. **Section H herbal illustration matches** — f31r (rose/rosewater), f46v (thistle/salt), f55r (poppy/oil) are illustration-structure-product matches that haven't been integrated with the PL recipe matching.

---

## Critical Context Files

| File | What It Is |
|------|-----------|
| `context/FOLIOS/` | All folio notes (11 documented folios) |
| `context/GLOSSING.md` | Full glossing system documentation |
| `context/CLAIMS/C1394_instruction_encoding_architecture.md` | MIDDLE = HEAD + MOD* + TERM |
| `context/CLAIMS/C1195_atom_gloss_confidence_tiers.md` | All 18 atom glosses |
| `data/token_dictionary.json` | Token-level glosses (8,150 tokens) |
| `data/middle_dictionary.json` | MIDDLE-level glosses (75+ MIDDLEs) |
| `phases/RECIPE_FOLIO_CORRESPONDENCE/` | All Phase 628 scripts and results |
| `sources/pseudo_lull_testamentum/testamentum_complete_english.txt` | PL English translation |
| `context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml` | Currier B grammar contract |

---

## Git Status Note

There are a LOT of untracked files in the working tree (exploratory scripts, temp files, artifacts from previous sessions). The `_prefixed` scripts in `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/` are all throwaway exploratory — they don't need to be committed. The folio notes in `context/FOLIOS/` DO contain valuable findings and should eventually be committed.

The `.gitignore` has a staged modification. `context/ARCHITECTURE/currier_AZC.md` and `scripts/voynich.py` have unstaged modifications from earlier work.
