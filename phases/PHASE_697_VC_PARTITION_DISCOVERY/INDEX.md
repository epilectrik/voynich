# PHASE 697: V/C-Partition Discovery — Projection Flexibility as Substrate Signature

**Status:** COMPLETE
**Date:** 2026-05-16 / 2026-05-17
**Main constraint registered:** C2033

---

## Origin and Trigger

Started 2026-05-16 evening as analysis of Layfield & Davis (2026) DHQ paper applying LSA to Voynich. Evolved through several phases:

1. L&D paper replication and methodology validation
2. Programming-language comparison (Voynich vs constructed-grammar territory)
3. EVA-vowel critique → V/C-partition hill-climb search
4. Bootstrap stability discovery
5. Three discriminating tests (A-prime confirmation)
6. NL-operational sanity null
7. Three pre-bookkeeping controls
8. Option B partition characterization (revealed combinatorial nature)
9. NL→NL hill-climb ceiling control (revealed projection flexibility, not closeness)

The phase produced one Tier 2 measurement (C2033) at narrow scope after three substantive narrowings of initial framings, each caught by pre-registered controls.

---

## Main Finding (C2033)

**Voynich Currier B's V/C-partition optimization shows uniquely large hill-climb improvement compared to natural-language Latin baselines.** Improvement from EVA-vowel baseline (0.544) to optimal partition (0.257) = +0.286 bits Jensen-Shannon divergence. This is 2.4× the maximum NL Latin improvement (Brunschwig +0.120) and ~14× the mean NL improvement (+0.020) across 8 Latin corpora.

The partition {a, g, h, n, o, r, y} is bootstrap-stable (5/5 identical resamples). Position-dependent (within-folio shuffle destroys recovery). NOT a frequency artifact (top-7-by-frequency overlaps only 4/7 with core). The partition partially intersects but does NOT fully recover the project's slot-grammar atom roles (5/7 atom correspondence; 9 positionally-locked atoms excluded).

**This is FLEXIBILITY, NOT CLOSENESS.** Multiple NL operational Latin corpora reach lower JS to Italian than Voynich's optimal (SISMEL 0.229 baseline, Codicillus 0.270 baseline). Voynich is uniquely tunable; it is NOT uniquely close to Italian.

---

## Three narrowings caught by pre-registered controls

This phase is methodologically valuable as a documented case of substrate-axis findings narrowing under discipline:

**Narrowing 1: Atom-system rediscovery framing → partial correspondence only.**
Initial framing: "V/C optimization rediscovers Voynich's slot grammar." Caught by Control 3 atom-role uniqueness check: 9 other positionally-locked atoms (e, i, q, m, k, t, d, f, s) are excluded from the partition. Partition is a SUBSET of slot-grammar atoms, target-language-fitted.

**Narrowing 2: Closeness to Italian framing → no unique closeness.**
Mid-phase framing: "Voynich at 0.256 below cross-NL ceiling 0.319 → uniquely Italian-close." Caught by NL→NL hill-climb ceiling control: SISMEL Testamentum Latin baseline JS=0.229 is BELOW Voynich's hill-climbed optimum. Codicillus baseline 0.270 is roughly equal. Voynich is NOT uniquely close to Italian.

**Narrowing 3: Designer prosodic-bias framing → killed.**
Crazy-expert wild reading: "Voynich was designed by someone with Italian ear." Required Voynich to project closer to Italian than NL Latin does. Falsified by Narrowing 2 result. No salvage.

**Surviving framing:** FLEXIBILITY of projection space. Voynich's hill-climb improvement is unique (2.4× max NL). The improvement metric is robust to all three narrowings.

---

## Methodology summary

**V/C-partition hill-climb optimization:**
- 20K-token-capped source corpora
- Hill-climbing search over 2^20 possible vowel/consonant partitions
- 15-30 random restarts per target
- Target distribution: CV-pattern distribution of comparison NL corpus
- Objective: minimize Jensen-Shannon divergence between source CV-pattern dist and target

**Bootstrap stability test:**
- Resample Voynich tokens with replacement, repeat hill-climb
- 5 iterations gave identical optimal partition {a, g, h, n, o, r, y}
- JS spread 0.0027

**Discriminating tests (A-prime vs B-prime):**
- Positional clustering: mean max-position-bucket 84% across 7 core chars (NOT NL-vowel-like)
- Within-token scrambling: 0/5 trials recover core (positional, not identity)
- Currier A vs B convergence: 6/7 shared core

**Pre-bookkeeping controls:**
- Within-folio character shuffle null: shuffled-Voynich does NOT recover core (PASS)
- Frequency confound check: top-7-by-freq overlap only 4/7 with core (PASS)
- Atom-role uniqueness: 9 positionally-locked atoms NOT in core — caught the morning's overclaim

**NL-operational sanity null:**
- 5 NL Latin corpora recover NL-vowel-like sets at 66% mean overlap
- Voynich at 43% NL-vowel overlap, below NL range
- Methodology distinguishes NL from Voynich

**NL→NL hill-climb ceiling:**
- 8 NL Latin corpora (operational + classical + Renaissance)
- Voynich improvement +0.286 vs NL max +0.120 (Brunschwig)
- Most NL improvements ≤0.01 (known vowels already near-optimal)
- Voynich uniquely flexible; NOT uniquely close

---

## Confound caveats explicitly disclaimed in C2033

Per crazy-expert's pre-registration paranoia check:

**(a) Character inventory size.** Voynich has 20 unique chars; some NL Latin corpora have 22-26. Smaller char inventory may give the optimizer mechanical headroom. Has NOT been controlled.

**(b) Baseline JS asymmetry.** Voynich EVA baseline JS=0.544 is substantially higher than NL Latin baselines (0.235-0.460). Larger improvement room is partially mechanical. Normalized improvement (improvement/baseline) gives Voynich 52% vs Brunschwig 26% — still 2× max NL but less dramatic than absolute.

**(c) N=1 in engineered-grammar column.** No other constructed/engineered scripts tested. "Engineered grammars are tunable" claim requires synthetic-corpus control or cross-script transfer test (queued for next phase).

---

## Pre-registered binary criteria evaluation

| Test | Pre-registered criterion | Result | Verdict |
|------|--------------------------|--------|---------|
| Bootstrap stability | 5/5 identical resamples | 5/5 identical {a,g,h,n,o,r,y} | PASS |
| Positional clustering | mean max-bucket ≥60% | 84.0% | PASS |
| Within-token scrambling | 0-1/5 recoveries | 0/5 | PASS |
| Currier A vs B | shared core ≥5/7 | 6/7 shared | PASS |
| Within-folio shuffle null | shuffled doesn't recover | 0/3 trials recover | PASS |
| Frequency confound | top-7-freq != core | 4/7 overlap (not match) | PASS |
| Atom-role uniqueness | core uniquely positionally-locked | 9 other chars positionally-locked | **FAIL** → narrowing 1 |
| NL sanity null | NL corpora recover NL-vowels | 66% mean NL-overlap (4/5 ≥60%) | PASS |
| NL→NL ceiling (closeness) | Voynich below all NL Latin | SISMEL 0.229 below Voynich 0.257 | **FAIL** → narrowing 2 |
| NL→NL ceiling (improvement) | Voynich improvement > NL max | Voynich +0.286, NL max +0.120 | PASS |

**8 of 10 pre-registered criteria PASS. 2 caught the morning's overclaims, narrowed the registered scope.**

---

## Scripts (in scripts/)

- `_lsa_replication.py` — L&D paper replication with H-track filtering
- `_lsa_replication_unfiltered.py` — L&D replication across 4 filter conditions
- `_lsa_logentropy_match.py` — Log-Entropy weighting attempt
- `_comparison_text_lsa.py` / `_v2.py` — Multi-corpus LSA landscape
- `_three_tier_controls.py` — token-count-matched + leave-one-out + window-size controls
- `_programming_language_lsa.py` — Voynich vs Python/C/Lisp/LaTeX
- `_four_controls.py` — Mesue stability + programming with comments + per-folio + within-Voynich shuffle
- `_phonotactics_test.py` / `_extended.py` / `_vc_search.py` — phonotactic analysis with V/C hill-climb
- `_vc_ceiling_and_bootstrap.py` — bootstrap stability + initial ceiling control
- `_aprime_bprime_discriminator.py` — three discriminating tests
- `_nl_operational_sanity_null.py` — methodology validation
- `_three_prebookkeeping_controls.py` — within-folio shuffle, frequency, atom-role checks
- `_option_b_partition_analysis.py` — combinatorial selection logic characterization
- `_nl_to_nl_hillclimb_ceiling.py` — final ceiling control (revealed flexibility framing)
- `_cardinality_search.py` — ×4/×9 anchor search in non-Voynich corpora (auxiliary)

## Key Results JSON files (in results/)

- `lsa_replication.json`, `lsa_replication_unfiltered.json`, `lsa_logentropy_match.json`
- `comparison_text_lsa.json`, `comparison_text_lsa_v2.json`
- `three_tier_controls.json`, `programming_language_lsa.json`
- `phonotactics_*.json` (3 files)
- `vc_ceiling_and_bootstrap.json` — initial discovery
- `aprime_bprime_discriminator.json` — A-prime confirmation
- `nl_operational_sanity_null.json` — methodology validation
- `three_prebookkeeping_controls.json` — Control 3 narrowing
- `option_b_partition_analysis.json` — combinatorial selection
- `nl_to_nl_hillclimb_ceiling.json` — final narrowing, flexibility framing

---

## What's next

Queued for next phase:

1. **Synthetic-corpus control.** Generate text from M2.1 / C1365 generative model. Hill-climb its V/C partition against Italian. If synthetic engineered grammar also shows ~50% normalized improvement → C2033 reframes to "engineered grammars are tunable" class property. If synthetic doesn't show flexibility → C2033 strengthens to "Voynich has unique flexibility even among engineered grammars."

2. **Cross-script transfer test.** Apply V/C optimizer to Sloane MS 3851 alchemical sigils, Datini merchant marks, Trithemius cipher. If Voynich's flexibility is shared with other constructed scripts → substrate-class evidence. If unique → Voynich-specific signature.

3. **Atom-partition alignment test (crazy-expert Q4.2).** Does the V/C-hill-climb optimal partition correlate with the HEAD/MOD/TERM partition (C1394)? Direct structural-axis grounding test.

4. **Non-romance target test.** Hill-climb toward Greek, Hebrew, Arabic, Old English. Is Voynich's flexibility romance-specific or universal?

After these: external corpus work (Antidotarium Nicolai full transcription, Mesue Grabadin 1602 cleanup) per `project_section_s_source_genre_gap.md`.

---

## Methodology lessons (registered as memory notes)

1. **Pre-registered numerical thresholds need empirical calibration before locking.** Pre-bookkeeping ceiling threshold ≤0.10 turned out wrong (actual cross-NL ceiling 0.32). When metric is new, calibrate against control distributions BEFORE locking binary criteria.

2. **Substrate-axis findings can be re-cast as operational by interpretation creep.** This phase had three narrowings, each killing an operational interpretation while a substrate-level measurement survived. The discipline that killed the closeness framing is the same discipline that makes the flexibility framing trustworthy.

3. **Improvement-vs-final-JS framing matters.** Today's measurement-class fact ("Voynich uniquely tunable") survives where the operational-class fact ("Voynich uniquely Italian-close") died. Frame measurements as improvement-from-baseline when possible.

See `feedback_calibrate_thresholds_against_controls.md` for the methodology note.

---

## Phase verdict: COMPLETE — one Tier 2 measurement registered, three operational overclaims caught and retracted by pre-registered controls, methodology notes filed
