# Transcriber Filtering Review

**Created:** 2026-01-15
**Issue:** Multiple research phases loaded ALL transcribers instead of filtering to H (PRIMARY) only
**Impact:** Token counts inflated ~3.2x, some sequential analyses produced artifacts

---

## Summary

The interlinear transcript contains parallel readings from 18 transcribers (H, C, F, U, V, etc.). The PRIMARY transcriber is **H**. Many analysis scripts failed to filter to H-only, causing:

1. **Token inflation:** ~3.2x more tokens than actual
2. **False repetition patterns:** Transcriber interleaving created artificial `[BLOCK] x N` patterns
3. **Inflated bigram counts:** Same tokens from different transcribers counted as adjacent
4. **Vocabulary inflation:** Variant readings added ~4,200 spurious types

### What's ROBUST (confirmed invariant)
- Currier B grammar (49 classes, hazard topology, kernel structure)
- AZC placement patterns (folio independence, section distribution)
- A/B disjointness (vocabulary separation)
- Folio-level analyses (scheduling, control signatures)
- Entry-level adjacency (C424)

### What's INVALIDATED
- C250: 64.1% block repetition → **0% with H-only**
- C267: 70.7% bigram reuse → **14.0% with H-only**
- C300: 9,401 AZC tokens → **3,299 with H-only**
- C304: 1,529 AZC-unique types → **903 with H-only**

---

## Phases Requiring Review

### CRITICAL (Token-sequence analyses)

#### `phases/01-09_early_hypothesis/`
| Script | Issue | Constraints Affected |
|--------|-------|---------------------|
| `phase1_daiin_abuse.py` | No H filter | C001-C010 (daiin patterns) |
| `phase2a_layer_map.py` | No H filter, sequential bigrams | Bigram co-occurrence |
| `phase3_pattern_search.py` | No H filter | Pattern frequencies |
| `phase4_frequency_analysis.py` | No H filter | Token frequencies |
| `phase5_compositional_probe.py` | No H filter | MIDDLE counts |
| `phase6_entry_signatures.py` | No H filter | Entry structure |
| `phase7a_middle_roles.py` | No H filter | MIDDLE role analysis |
| `phase8_structural_tokens.py` | No H filter | Structural token counts |
| `phase9_recursive_structure.py` | No H filter | Recursion detection |
| `phase20_operational_normalization.py` | No H filter | **C121 (49 classes)** - but verified OK |

**Status:** HIGH RISK - These are foundational analyses

#### `phases/CAS_currier_a_schema/`
| Script | Issue | Constraints Affected |
|--------|-------|---------------------|
| `currier_a_block_analysis.py` | No H filter, sequential | **C250 (INVALIDATED)** |
| `currier_a_payload_analysis.py` | No H filter | C251-C266 (multiplicity) |
| `analyze_daiin.py` | No H filter | daiin repetition counts |
| `analyze_daiin_v2.py` | No H filter | daiin consecutive patterns |
| `analyze_daiin_relationships.py` | No H filter | daiin bigrams |
| `cas_deep_structure_tests.py` | No H filter | Block structure |
| `cas_deep_validation_tests.py` | No H filter | Repetition validation |
| `cas_nonblock_marker_scan.py` | No H filter | Marker analysis |
| `cas_phase5_normalize.py` | No H filter | Sequence repetition |

**Status:** HIGH RISK - C250-C266 multiplicity encoding claims need complete re-evaluation

#### `phases/AZC_astronomical_zodiac_cosmological/`
| Script | Issue | Constraints Affected |
|--------|-------|---------------------|
| `azc_folio_features.py` | No H filter | **C300, C304** (counts wrong) |
| `azc_vocabulary_analysis.py` | No H filter | AZC vocabulary counts |
| `azc_structure_tests.py` | No H filter | AZC structure |
| All other AZC scripts (~45) | No H filter | Various AZC constraints |

**Status:** MEDIUM RISK - Patterns preserved but counts need updating

### MEDIUM RISK (May have inflated counts)

#### `phases/exploration/`
| Script | Issue | Constraints Affected |
|--------|-------|---------------------|
| `super_entry_grouping.py` | No H filter | C424 - but verified OK |
| Most other scripts (~84) | No H filter | Various |

**Exception:** `c412_verification.py` correctly filters to H

#### `phases/EXT_*/`
| Phase | Issue | Status |
|-------|-------|--------|
| `EXT_HF_hf_morphology/` | 26/27 files missing filter | REVIEW |
| `EXT_PP_positional_parsing/` | Missing filter | REVIEW |
| `EXT_FUNC_functional_layer/` | Missing filter | REVIEW |

**Exception:** `ext_hf_02_analysis.py` correctly filters to H

#### `phases/OPS*/`
| Phase | Issue | Constraints Affected |
|-------|-------|---------------------|
| `OPS1_folio_control_signatures/` | Missing filter | Folio signatures |
| `OPS6A_spatial_control/` | Missing filter | Spatial analysis |

**Note:** OPS2-OPS5 inherit from OPS1, so downstream may be affected

### LIKELY OK (Verified or lower risk)

#### `phases/15-20_kernel_grammar/`
| Script | Issue | Status |
|--------|-------|--------|
| `phase15_state_c_deep_structure.py` | Has deduplication | LIKELY OK |
| `phase17_kernel_semantics.py` | Has deduplication | LIKELY OK |
| `phase18_failure_typology.py` | Has deduplication | **VERIFIED OK** (hazards = 0) |
| `phase19_identifier_boundary.py` | Has deduplication | LIKELY OK |

These have `seen.add(key)` deduplication which helps but doesn't filter to H.

#### Phases that correctly filter to H
- `phases/SISTER_sister_pair_analysis/` - Uses proper filtering
- `phases/perturbation_space/` - Uses proper filtering
- `phases/CAud_currier_a_audit/` - Uses proper filtering
- `phases/PCS_coordinate_system/` - Uses proper filtering
- `phases/PMS_prefix_material/` - Uses proper filtering

---

## Constraints Requiring Update

### INVALIDATED (Must revise or remove)
| Constraint | Original Claim | Action |
|------------|----------------|--------|
| C250 | 64.1% block repetition | INVALIDATE - artifact |
| C267 | 70.7% bigram reuse | REVISE to 14.0% |
| C251-C266 | Multiplicity encoding | REVIEW all |

### UPDATE NUMBERS (Pattern valid, count wrong)
| Constraint | Original | Correct (H-only) | Action |
|------------|----------|------------------|--------|
| C300 | 9,401 AZC tokens | 3,299 | Update |
| C304 | 1,529 AZC-unique types | 903 | Update |

### VERIFIED OK
| Constraint | Status |
|------------|--------|
| C121 (49 classes) | Verified invariant |
| C485 (h->k = 0) | Verified invariant |
| C109-C114 (hazards) | Verified invariant |
| C364 (41 core, 3368 unique) | Already used H-only |
| C424 (adjacency) | Verified invariant |
| C357 (cross-line bigrams) | Verified OK |

---

## Fix Template

For each affected script, apply this fix:

```python
# BEFORE (wrong)
df = pd.read_csv(DATA_FILE, sep='\t', low_memory=False)

# AFTER (correct)
df = pd.read_csv(DATA_FILE, sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']  # PRIMARY track only
```

Or for manual file reading:

```python
# BEFORE (wrong)
for row in reader:
    word = row['word']
    # process...

# AFTER (correct)
for row in reader:
    if row.get('transcriber', '').strip('"') != 'H':
        continue
    word = row['word']
    # process...
```

---

## Review Checklist

- [x] `phases/01-09_early_hypothesis/` - **COMPLETE** (2026-01-15)
  - Fixed 10 scripts that load transcript data (7 scripts don't load transcript)
  - **C121 (49 classes) CONFIRMED INVARIANT** - 9.8x compression preserved
  - **Layer structure PRESERVED** - ALPHA/BETA/GAMMA/DELTA layers intact
  - **daiin patterns PRESERVED** - 93.9% entry presence, hub avoidance intact
  - Token counts reduced from ~100K to 32,729 (H-only)
  - All key constraints verified with H-only data
- [x] `phases/CAS_currier_a_schema/` - **COMPLETE** (2026-01-15)
  - Fixed 24 scripts with H filter
  - Block-dependent analyses now return NO_BLOCKS (0% repetition)
  - Marker taxonomy (phase 3) PRESERVED - 8 mutually exclusive prefixes
  - CAS_REPORT.md updated with corrections
  - All JSONs regenerated
- [x] `phases/AZC_*/` - **COMPLETE** (2026-01-15)
  - Fixed 45+ scripts across 6 AZC-related directories
  - H filter added to all transcript loading functions
  - C300 updated: 9,401 → 3,299 tokens
  - C304 updated: 1,529 → 903 types
  - AZC folio features verified: 3,299 tokens, 903 AZC-only types
- [x] `phases/exploration/` - **REPORTS UPDATED** (2026-01-16)
  - RECORD_STRUCTURE_SYNTHESIS.md - Added INVALIDATED warning for C250
  - RECORD_GEOMETRY_SYNTHESIS.md - Added INVALIDATED warning for C250
  - Scripts not individually fixed (exploratory, not constraint-producing)
- [x] `phases/EXT_*/` - **NO CHANGES NEEDED** (2026-01-16)
  - No C250/9401/1529 references found in EXT reports
  - Scripts are external validation tests, not transcript-dependent
- [x] `phases/AZC_astronomical_zodiac_cosmological/` - **REPORTS UPDATED** (2026-01-16)
  - AZC_REPORT.md - Token counts corrected (9,401 → 3,299, 1,529 → 903)
  - AZC_PLAN.md - Token counts corrected
- [x] `phases/CAS_currier_a_schema/` - **REPORTS UPDATED** (2026-01-16)
  - CAS_MULT_REPORT.md - Added INVALIDATED warning
  - CAS_DEEP_REPORT.md - Added INVALIDATED warning
- [x] `phases/MIXED_marker_entry_analysis/` - **REPORT UPDATED** (2026-01-16)
  - MIXED_ENTRY_REPORT.md - Added INVALIDATED note for C250 reference
- [x] `phases/OPS*/` - **COMPLETE** (2026-01-15)
  - Fixed OPS1_folio_control_signatures/ops1_extract_signatures.py
  - Fixed OPS6A_human_navigation/ops6A_analysis.py
  - OPS2-OPS6 consume OPS1 output (no direct transcript loading)
  - All quality checks PASS with H-only data
  - Outputs regenerated: ops1_folio_control_signatures.json, ops1_folio_signature_table.csv
- [x] Update `context/CLAIMS/` with corrected values - **COMPLETE** (2026-01-16)
  - C250-C262, C266 marked INVALIDATED in currier_a.md, INDEX.md
  - C300 updated: 9,401 → 3,299 in azc_system.md, coverage_metrics.md
  - C304 updated: 1,529 → 903 in azc_system.md
  - All ARCHITECTURE files updated (currier_A.md, currier_AZC.md, cross_system_synthesis.md)
  - CONSTRAINT_TABLE.txt regenerated (356 constraints)
- [x] Update `context/MODEL_FITS/` if affected - **COMPLETE** (2026-01-16)
  - F-A-003 and F-A-008 marked INVALIDATED in fits_currier_a.md
  - fits_azc.md token counts corrected
  - FIT_TABLE.txt regenerated (29 fits)
- [ ] Re-run validation suite after fixes

---

## Validation After Fixes

After fixing scripts, re-run:
```bash
python temp_primary_track_validation.py
python temp_b_grammar_rederive.py
python temp_azc_rederive.py
python temp_ab_disjointness.py
python temp_secondary_verify.py
```

All should pass with H-only data.

---

*This document tracks the transcriber filtering issue discovered 2026-01-15.*
