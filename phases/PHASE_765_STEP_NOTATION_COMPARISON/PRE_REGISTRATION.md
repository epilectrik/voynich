# PHASE_765 — Is Currier B nearer to discrete-operation step notations than to prose, gibberish and constrained non-notation? (pre-registration)

**Status:** LOCKED v2 (2026-09-28), before any statistic was computed on any corpus. The lean-expert design audit of v1
returned LOCK WITH CHANGES; edits E1–E8 are incorporated, and deviations are listed at the end.

**Origin:** the human's working model (2026-09-28): Currier B is a set of discrete workshop operations ("start heat,
prepare vessel A, watch for reaction"). On that view it is finer-grained than recipe prose, which is why
sentence-level recipe matching failed (`SPECULATIVE/rupescissa_comparative.md`; PHASE_762, C2052).
- **Prompt from PHASE_764 (descriptive):** B has more adjacent repetition and near-repetition than both improvised
  gibberish and meaningful text.

**Question:** is B's low-level rule-boundedness profile nearer to step notations than to prose (English and Latin,
general and procedural) and gibberish? Is it also nearer to them than to constrained text that is not operation
notation (the floor control)?

**Scope:** a low-level profile at 197-pair scale.
- Line-position dependence is excluded by design: re-wrapping removes it from every corpus, B included, so no verdict
  here bears on it (E1).
- This phase does not test what B notates.

**Change control:** after lock nothing below may change without a new phase number.

## Corpora (raw files in git-ignored `external/`, or tracked `sources/`)
| Unit | Corpora |
|---|---|
| **SN-KNIT** (step notation) | 11 knitting/crochet notation corpora: needlework paragraphs whose words are ≥ 30% pattern abbreviations or counts (lexicon `sn765.ABBREV` + numerals), ≥ 1,500 words per book; Project Gutenberg |
| **SN-CHESS** | 6 chess collections (Morphy, Capablanca, Tal, Fischer, Karpov, Carlsen; pgnmentor). SAN movetext with case kept |
| **SN-AGC** | Apollo Guidance Computer assembly: Comanche055 and Luminary099 merged into one corpus, with source files identical across the two counted once. Comments removed |
| **PP** (procedural prose, English) | the needlework books' prose paragraphs (≥ 1,500 words per book) |
| **PP-L** (procedural prose, Latin) | Antidotarium Nicolai (`antidotarium_nicolai_latin_plain.txt`); Mesue Grabadin; Rupescissa 1561 (first 200 lines skipped); SISMEL Testamentum Latin pages (as in PHASE_763). Codicillus and Theophilus are excluded because their texts mix in English (C2054; PHASE_763 D2) |
| **M** (meaningful) | Gaskell & Bowern's 71 texts |
| **G** (gibberish) | the 23 Gaskell & Bowern samples with ≥ 197 pairs |
| **CN** (constrained non-notation, floor control) | Naibbe GV1/P-REC/STREAM/SR0/V0, 5 runs (seeds 765001–765005); Timm–Schinner, 5 runs (seeds 765101–765105), both on B's skeleton via the PHASE_757 harness in glyph units; Roget's Thesaurus (Gutenberg 10681), a word-list genre |
| **B** | ZL 3b Currier B, `P` placement, uncertain spaces merged, glyph units |

**Text normalisation:** non-B, non-generator corpora are NFD alphanumeric and lower-cased, except chess. Units are
characters, digits included.

**Line structure (E3):** every corpus, B included, is joined into running text and re-cut into lines whose lengths are
drawn from B's segment lengths (ZL, merged spaces). A token dropped by normalisation still splits the stream: there is
no bridging.
- Join units: paragraph (Gutenberg, M, PP, PP-L), game (chess), source file (AGC), sample (G), folio (B and CN
  generators).
- B on its authorial lines is variant V5.

## Statistics per chunk
Each chunk has exactly 197 within-line pairs. Each statistic is compared with 200 within-line shuffles.

| Name | Definition | In primary profile |
|---|---|---|
| P1 | (I(L1(t); F1(t+1)) − shuffle mean) / H(F1) | yes |
| P2 | log((O+0.5)/(E+0.5)) for identical adjacent words; E is the analytic within-line expectation (PHASE_757 D3) | yes |
| P3 | log((O+0.5)/(E+0.5)) for adjacent words at edit distance ≤ 1 but not identical; E is the shuffle mean | yes |
| P4 | type-token ratio (E4) | variant V2 only |

- The raw O and E for P2 and P3 are reported per corpus.
- **Chunks:** 100 per corpus from random starts; 400 for B; 1 per G sample.

## Distance (E5)
- **Scale:** each statistic is divided by the class-balanced pooled within-class SD of chunk-level values. The classes
  are SN, PP, PP-L, M, G and CN, weighted equally; the three SN subgroups are weighted equally within SN.
- **Chunk distance:** the Euclidean distance between a chunk's scaled P1–P3 and B's profile, the median of B's 400
  chunks.
- **Corpus distance:** d(c) is the mean chunk distance over corpus c's chunks.
- **Floor:** the mean distance of B's own chunks from B's profile. The B-halves split (100 splits) is also reported.

## Decision (E6)
- **Units:** the SN subgroups (KNIT, CHESS, AGC) and the comparison classes M, PP, PP-L, G and CN. A unit's value is the
  median d over its corpora.
- **Stability:** 1,000 bootstrap resamples, resampling corpora within each unit; for single-corpus units (AGC),
  chunks within the corpus. "g < k" holds if it is true in ≥ 90% of resamples. This 90% is a stability rule, not a
  significance level.
- **A subgroup WINS** if g < k holds for every k in {M, PP, PP-L, G}.
- **Outcome:**
  - **SUPPORT:** all three subgroups win, **and** g < CN holds for each subgroup, **and** the paired test does not
    contradict.
  - **NOT SUPPORTED:** no subgroup wins.
  - **PARTIAL:** anything else. The winning subgroups and the classes they fail against are named. A subgroup that
    beats M, PP, PP-L and G but not CN is recorded as "rule-bound, not notation-specific".
- **Paired test (knitting books that yield both a notation and a prose corpus):** count the books where d(notation) <
  d(prose). It is reported if there are ≥ 6 pairs, and it contradicts SUPPORT if notation is nearer in fewer than two
  thirds of pairs.
- **Mann–Whitney** (corpora as units, and subgroups as units): descriptive only.

## Variants (E7)
A variant that moves the verdict between SUPPORT and NOT SUPPORTED makes it PARTIAL; the variant is named.

| Variant | Change |
|---|---|
| V1 | B and the CN generators in EVA characters |
| V2 | profile with P4 added |
| V3 | chess lower-cased |
| V4 | needlework threshold 0.25 and 0.35 |
| V5 | B and the CN generators on their authorial lines |
| V6 | in every non-B corpus, each digit run replaced by one placeholder symbol |
| V7 | Mahalanobis distance, using the class-balanced pooled within-class covariance |
| V8a–c | P1, P2 or P3 dropped in turn (the carrying statistic is named) |

## Registry consequences (E8)
- **SUPPORT:** Tier-2 measurement row, naming the corpora: "B's P1–P3 profile at 197-pair scale is nearer to
  knitting/crochet pattern notation, chess SAN and AGC assembly than to English and Latin procedural prose, meaningful
  text, improvised gibberish and constrained non-notation controls." It **requires human sign-off**, because it relates
  a structural feature to an external class of referents. Any reading of what B notates stays Tier 3.
- **NOT SUPPORTED:** Tier-2 negative-knowledge row: on this profile, B is not nearer to step notations than to prose or
  gibberish. The "discrete operations" model loses this line of support, not the model itself.
- **PARTIAL:** phase record only. "Rule-bound, not notation-specific" is stated if it applies.

## Caveats
- **Modern notations:** chess and assembly are generality subgroups, not workshop procedure. Knitting and crochet are
  the only craft-operation notation here.
- **Units differ:** glyph units for B and CN generators, characters elsewhere.
- **OCR:** Mesue and Rupescissa are noisy OCR (long-s printed as f), which weakens PP-L as a comparison.

## Deviations from the audit
- **D1:** Theophilus is excluded from PP-L. The Hendrie text interleaves English, the same reason as Codicillus
  (C2054; PHASE_763 D2). SISMEL Latin replaces it.
- **D2:** B and the CN generators are joined within folio, not paragraph, because the ZL loader does not keep
  paragraph markers.
- **D3:** the list genre in CN is Roget's Thesaurus (Gutenberg 10681).

## Outputs
`results/step_compare.json`, `results/run_log.txt`. Scripts: `scripts/step_compare.py` and `scripts/sn765.py`; shared
statistics come from PHASE_764's `g764.py`.
