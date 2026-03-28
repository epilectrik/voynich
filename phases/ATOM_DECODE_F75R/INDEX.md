# Phase 630: Atom-Level Decode & HT Positional Grammar

**Status:** COMPLETE
**Verdict:** ATOM_DECODE_VALIDATED
**Constraints:** C1897-C1900

---

## Research Question

Can the atom-level glossing system (C1394 HEAD+MOD*+TERM) produce operationally coherent readings when applied to f75r, and does the corrected e-depth data strengthen the Ch19 recipe alignment (C1896)? Separately, do HT token articulators exhibit structured positional behavior across the corpus?

## Background

Phase 629 (C1891-C1896) established content validation for Ch19→f75r and Ch18→f76r matches. During exploratory atom-level decoding of f75r, a suffix parsing bug was discovered: the -edy suffix greedily absorbs terminal 'e' from compound MIDDLEs, suppressing e-depth information (kee→ke). This motivated the creation of `Morphology.atomize()`, which bypasses the MIDDLE/SUFFIX boundary entirely and reads post-prefix characters as a flat atom sequence.

The corrected e-depth data revealed balneum mariae gentle-heat signatures previously invisible. Additionally, analysis of HT (Human Track) tokens on f75r revealed that articulators encode positional information — prompting a corpus-wide test.

## Novel Contribution

1. The -edy suffix e-depth suppression observation and atomize() resolution
2. HT articulator two-group positional split (OPENERS vs EMBEDDED), validated corpus-wide
3. f75r atom decode with corrected e-depth confirming kee/ke thermal trajectory
4. Fermentation fingerprint falsification (confirms C171)

---

## Scripts

| Script | Runtime | Output |
|--------|---------|--------|
| `_full_decode_f75r_v2.py` | ~5s | Console (full atom decode) |
| `_ht_corpus_positional_test.py` | ~30s | Console (HT positional test) |
| `_fermentation_signature.py` | ~15s | Console (fermentation test) |
| `_align_f75r_ch19.py` | ~5s | Console (recipe alignment) |
| `_semantic_ceiling_test.py` | ~10s | Console (HT/hapax/dar analysis) |

All scripts in `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/` (shared with Phase 628-629 exploratory work).

---

## Constraints

### C1897: Suffix -edy suppresses e-depth in compound MIDDLEs (Tier 2)

The suffix -edy in the standard morphological parser absorbs the terminal 'e' from compound MIDDLEs, parsing kee+dy as ke+edy. This suppresses e-depth (C1225) information: tokens with e-depth=2 (gentle/stabilized heat) appear as e-depth=1 (steady heat). Morphology.atomize() bypasses the MIDDLE/SUFFIX boundary for atom-level analysis, reading post-prefix characters as a flat HEAD+MOD*+TERM atom sequence (C1394). 100% coverage on 23,096 Currier B tokens.

- Scope: B, GLOBAL, morphology, parser, C1225, C1394
- Metrics: affected_suffix=edy. corrected_tokens=all_ke+edy→kee+dy. coverage=100%. corpus=23096.

### C1898: HT articulators exhibit two-group positional split (Tier 2, refines C1417)

HT token articulators divide into two positional groups across all Currier B: OPENER articulators (p, t, f, d) are 66.7% line-initial (N=240), EMBEDDED articulators (l, r) are 4.3% line-initial (N=187). Chi-squared=171.4 (df=1, p<0.001). Consistent across 92% of testable folios (23/25 with 3+ tokens in each group). The y-articulator (N=522, 51.2% of all HT) splits by prefix: sh/ch-prefixed y is 77-87% initial, te/ta-prefixed y is 15-24% initial. k-articulator is embedded (19.4%, N=36); s-articulator is mixed (47.1%, N=34). Refines C1417 (articulator line-initial concentration) with non-uniform articulator-character distribution.

- Scope: HT, B, articulator, position, C1417
- Metrics: opener_init=66.7%. embedded_init=4.3%. chi2=171.4. p<0.001. folio_consistency=23of25. N_opener=240. N_embedded=187. N_y=522. N_total=1019.

### C1899: f75r atom decode confirms Ch19 alignment with corrected e-depth (Tier 3, extends C1896)

Full atom-level decode of f75r (412 tokens, 9 paragraphs) using atomize() confirms 8 structural predictions from PL Ch19 recipe alignment and reveals e-depth thermal trajectory previously hidden by -edy suffix suppression. Corrected e-depth shows: P4 (enumerated repetition) 6% gentle heat = active distillation; P9 L38 alternating kee/ke (gentle/steady); L41 100% gentle heat immediately preceding material addition (L42 dar) and quality check (L43 chekar). E-depth trajectory within P9 matches recipe internal structure: gentle warming → material addition → quality check → sharp distillation finish.

- Scope: B, f75r, PL, Ch19, C1896, C1225, C1394
- Metrics: tokens=412. paragraphs=9. predictions_confirmed=8of8. P4_gentle=6%. P9_gentle=26%. L41_gentle=100%.

### C1900: Fermentation structural fingerprint falsified (Tier 1)

Hypothesis: fermentation operations produce a unique structural signature distinguishable from other passive-monitoring operations. Criteria: sh>20%, ch<10%, qo<15%, e-HEAD>25%, k-HEAD<15%. Result: 1/555 paragraphs passes (f113r P14, not a balneum folio). f75r P5 (predicted fermentation paragraph) fails criteria (ch=13.5%, qo=21.2%). The text encodes operational behavior shifts (monitor-heavy, heat-light) but not process-specific labels. Confirms C171 semantic ceiling.

- Scope: B, paragraph, fermentation, C171
- Metrics: pass=1of555. f75r_P5_ch=13.5%. f75r_P5_qo=21.2%. criteria=sh>20+ch<10+qo<15+e>25+k<15.
