# PHASE_766 — Do pharmaceutical fragment labels go with the herbal page of the same plant?

**Status:** COMPLETE. Locked verdict: **NO SIGNAL (bounded)**, stable in all variants. Registered as C2084 (Tier 2,
negative knowledge).
**Pre-registration:** `PRE_REGISTRATION.md`, locked at commit 0b24813 after a lean-expert audit (edits E1–E8).
**Scripts:**
- `scripts/item_map.py`: maps item numbers to ZL label lines; the counting rule agrees with 119 of 130 tags.
- `scripts/lab766.py`: text rules, label words, edit distance.
- `scripts/label_test.py`: power, test, variants and descriptives (39 s).

**Results:** `results/label_test.json`, `results/run_log.txt`, `results/item_map.json`.
**Sources:** voynich.nu quire pages (Zandbergen, after Petersen and Knowles), archived with SHA-256 hashes in
git-ignored `external/voynich_nu/`.

## Question
Some plant fragments drawn in the pharmaceutical section have been matched by eye to a whole plant on a herbal page.
Does such a fragment's label resemble the text of that herbal page more than the text of the other matched pages? If
labels and herbal text name or index their plants, the label should recur on the right page.

## Design (as locked)
- **Pairs:** 13 published visual matches whose labels carry ZL item tags (5 "same plant", 8 "shows some
  similarity").
- **Statistic:** surprisal of the closest label-word match on the page, in glyph-unit edit distance, counted up to
  distance 2.
  - Calibration: the fraction of the 128 herbal pages that reach that distance.
  - Effect: common word shapes score about 0 and near matches of rare forms score high.
- **Null:** permute the 13 page slots, 100,000 permutations. This cancels every label effect and page effect and
  leaves only the pairing.
- **Power** was estimated on surrogate herbal pages (same Currier-language mix and length range) with planted label
  words, before any real-pairing statistic.

## Result
| Quantity | Value |
|---|---|
| T observed | 0.78 |
| T under the null (mean) | 5.12 |
| p (one-sided, above null) | 0.974 |
| Size (k = 0) | 0.045 |
| Power, exact label word planted in k pairs | k = 1: 0.46; k = 2: 0.93; k = 3: 1.00 → **MDE80(a) = 2** |
| Power, one-glyph variant planted | k = 1: 0.37; k = 2: 0.82; k = 3: 0.97 → **MDE80(b) = 2** |

**Variants:** all NO SIGNAL.

| Variant | p |
|---|---|
| V1 same-plant pairs only | T = 0, p = 1.0 (exact, 120 permutations) |
| V2 jar labels added | 0.84 |
| V3 item 203 excluded | 0.97 |
| V4 first line only | 0.94 |
| V5 H-track | 0.93 |
| V6 EVA characters | 0.96 |
| V7 draft similarity statistic | 0.74 |
| V8 permutation within pharma-folio groups | 0.96 (exact, 17,280) |

**Descriptive:**
- **Pairs:** 10 of the 13 labels have no word within two edits of any token on their matched page. The three
  exceptions are common shapes found on most herbal pages:
  - oaro → or/oaiin (distance 2; reached on 114 of 128 pages);
  - otal → otain/otam/otar/ytal (distance 1; 93 pages);
  - opchor → kchor/otchol (distance 2; 115 pages).
- **Label vocabulary:**
  - 10 of the 15 label words occur nowhere in the herbal text.
  - tolsasy, sochorcfhy and koldarod have no neighbour within two edits on any herbal page.
- **Robustness:**
  - Leave-one-pair-out p ranges from 0.93 to 0.99, so no single pair drives the result.
  - Leave-f96v-out p = 0.97.
- **The two labels matched to the same plant** (items 94 and 116, both f96v; both "similarity" matches) are 5 edits
  apart. That is the median distance between label pairs (mid-rank 31 of 78), so they are no more alike than a
  typical pair.
- **Lower tail (not registered, not interpreted):** P(T_perm ≤ T_obs) = 0.06.

## Reading
- **What is excluded:** no fragment label reuses a word of its plant's herbal page, exactly or within one glyph. The
  test would have detected that in as few as 2 of the 13 pairs with 80% power.
- **Consistency with prior work:** this fits C523 (jar labels share nothing with pharmaceutical text) and C914 (label
  vocabulary is enriched in rare forms). Labels form a vocabulary largely absent from the running text.
- **What is not excluded:**
  - labels as codes, quantities, preparations or contents;
  - plant names that take a different form in the two sections;
  - herbal text that never names its own plant.

  The result is not evidence of meaninglessness.
- **Match quality:** the matches were not made text-blind. That bias could only have raised T, so it does not weaken
  the null. The null does rest on the matches being right, and 8 of the 13 are only "some similarity".
- **Next step for the pictures-and-text question** (RESEARCH_AGENDA #8): a design that does not assume a label is a
  word of the herbal text. For example, test whether labels of the same plant within the pharmaceutical section agree
  with each other, which needs a larger set of text-blind plant identifications.

## Deviations
None. The power run used the matched-page token range 54–111. The audit text quoted 51–117 as a placeholder; the
locked pre-registration states 54–111.
