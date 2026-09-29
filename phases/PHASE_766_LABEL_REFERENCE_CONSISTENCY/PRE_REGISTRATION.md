# PHASE_766 — Do pharmaceutical fragment labels go with the herbal page of the same plant? (pre-registration)

**Status:** LOCKED (v2, 2026-09-28). The draft v1 went to a lean-expert design audit, verdict "LOCK WITH CHANGES"; its
edits E1–E8 are incorporated below. Nothing in this file may change after lock without a new phase number.

**Origin:** RESEARCH_AGENDA Tier C #8 (pictures and text). This is an association test that surface statistics of
the text alone cannot fake:
- if the labels and the herbal text name or index their plants, a fragment's label should recur on the herbal page of
  the same plant;
- a practised pseudo-script has no reason to do that.

Prior registry work compared jar labels only with the pharmaceutical section's own text (C523: Jaccard 0.000). It never
compared fragment labels with the herbal page of the same plant.

**Question:** a plant fragment drawn in the pharmaceutical section may have been visually matched to a whole plant on
a herbal page. When it has, does the fragment's label resemble that page's text more than the text of the other
matched pages?

**Asymmetry (E7):**
- **ABOVE NULL** is evidence that label strings go with the depicted plant across sections (as a name, code or index
  key), conditional on the matches being text-blind. It does not show linguistic content.
- **NO SIGNAL** is weak: labels may be codes, quantities or contents, and herbal text need not name its plant. It is
  robust to text-informed matching, and it is not evidence of meaninglessness.

## Matches (external, fixed before any statistic)

### Source
- **Where:** voynich.nu page descriptions (R. Zandbergen, drawing on Th. Petersen and M. Knowles). The pharmaceutical
  side is quires 15 and 19; the herbal side is the herbal page descriptions in quires 2, 3, 5, 6, 7, 15 and 17.
- **Archived** 2026-09-28 in git-ignored `external/voynich_nu/` (kept local; not redistributed). SHA-256:

  | File | SHA-256 |
  |---|---|
  | q15 | 25a8bb0083a2c6c09913910c52d03a699091c100294f8fe3c604e3846253f3a7 |
  | q19 | 119fe32a005723833ec07a313fd87e1cd044a1f685ddd4fdd199e573c1dff1fb |
  | q02 | 62dacc593854f9de724820c427ee5285492084b08839684fe59143ff2e95c89a |
  | q03 | c43ff6e75e0d6db22a6c7e887101f3d1045f8a72878717e733c10ec93ce65ab3 |
  | q05 | 48d3ee83bde2ffffa8a95770f5ca54ae996f340d81080e4024f9f94581d7f3ed |
  | q06 | bd377ccecf0c472e4b7965f9885b130943be6c98097b33fa5486c592cf133beb |
  | q07 | 69af3fe68a574e4ac12e1af5eddf46c642d0ffa52b36b0fa577d3676294c2b1f |
  | q17 | 5b5f1743df54e5e0b5f3e1e60e994870b237a3722122b8c6ce7be9121d6a24dd |

- **Scope:** 30 matches are listed. The test uses the **13** whose item number carries an explicit ZL tag (`<!NN>`)
  linking it to its label line.

### The 13 pairs, with verbatim wording
| Item | Pharma folio | Label (ZL) | Herbal page | Pharmaceutical-side wording | Herbal-side wording |
|---|---|---|---|---|---|
| 61 | f89v2 | daseky | f48r | "Fragment 61 appears to be the same plant as on f48r." | "This appears to be the same plant as shown in fragment 61 on f89v2." |
| 80 | f99r | oaro (jar: oparal) | f51r | "Fragment 80 shows some similarity with the plant on f51r." | "This plant shows some similarity with plant fragment #80 on f99r." |
| 94 | f99r | tolsasy (jar: yteoldy) | f96v | "Fragment 94 shows some similarity with the plant on f96v." | "This plant shows some similarity with plant fragment #94 on f99r and with plant fragment #116 on f100r." |
| 95 | f99v | otoldy (jar: okaramy) | f44r | "Fragment 95 shows some similarity with the plant on f44r." | "This plant shows some similarity with plant fragment #95 on f99v." |
| 110 | f99v | otal / chor.olekor | f34v | "Fragment 110 shows some similarity with the plant on f34v." | "This plant shows some similarity with plant fragment #110 on f99v." |
| 116 | f100r | sochorcfhy | f96v | "Fragment 116 shows some similarity with the plant on f96v." | (see item 94) |
| 133 | f100v | opchor | f13v | "Fragment 133 shows some similarity with the plant on f13v." | "This plant shows some similarity with plant fragment #133 on f100v." |
| 136 | f100v | ykchochdy | f90v2 | "Fragment 136 shows some similarity with the plant on f90v2." | "This plant shows some similarity with plant fragment #136 on f100v." |
| 203 | f102r1 | ddardsh (coded as a container) | f37v | "Fragment 203 appears to be the same plant as on f37v;" | "This appears to be the same plant as shown in fragment 203 on f102r1." |
| 212 | f102r2 | koldarod | f18v | "Fragment 212 appears to be the same plant as on f18v;" | "This appears to be the same plant as shown in fragment 212 on f102r2." |
| 213 | f102r2 | odalydary | f23r | "Fragment 213 appears to be the same plant as on f23r;" | "This appears to be the same plant as shown in fragment 213 on f102r2." |
| 225 | f102v2 | sarol | f36r | "Fragment 225 shows some similarity with the plant on f36r." | "This plant shows some similarity with plant fragment #225 on f102v2." |
| 240 | f102v1 | loralody | f19r | "Fragment 240 appears to be the same plant as on f19r." | "This appears to be the same plant as shown in fragment 240 on f102v1." |

"appears to be the same plant" = **same** (5 pairs); "shows some similarity" = **sim** (8 pairs).

### Independence from the text (E4)
- **What the sources show:** they present the matches as visual. None documents a text-blind procedure, and the
  matchers worked with the text (Petersen made his own transcription and concordance). Text-informed matching cannot
  be excluded.
- **Direction of the bias:** text-informed matching can only inflate T.
- **Exclusion check:** any pair whose source cites a word, label or text resemblance is excluded. Both sides of all 13
  pairs were read. **Result: none found.** The only extra remark is codicological and kept: "The two plants on the
  same side of this bifolio (f18v and f23r), also appear next to each other as plant fragments on f102r2."

### Item-to-label rule and selection (E5)
- **An item's label** is every ZL label string carrying its `<!NN>` tag beside the fragment. If there is none, its
  container label is used (item 203 only; its one label is coded `Lc`).
- **Tag presence by page:**

  | Group | Pages (tagged labels / all labels) |
  |---|---|
  | Tagged in full or nearly so | f99r 34/34, f99v 25/25, f100r 15/17, f100v 13/13, f102r1 4/4, f102v1 10/10, f102v2 22/22 |
  | Partly tagged | f89v2 5/15: only the bottom row, items 58–61 (the page note records a May 2025 correction to item 59 in that row; why the row is tagged cannot be verified) |
  | Partly tagged | f102r2 2/7: its two fragment labels; the other five are container labels |
  | Untagged | f88r, f88v, f89r1, f89r2, f89v1, f101v |

  Selection is therefore page-blocked, with the f89v2 row as the one exception whose cause is unknown.
- **The 13 pairs were selected on tag presence alone.**
- **Counting-rule check:** item counts were compared with tags only (the rule agrees at 119 of 130 tags).
- **Timing:** both steps were done before any label–page similarity was computed and without consulting herbal text.
  Only page token counts and Currier languages were read, to define R and the surrogate pools below.
- **Excluded matches (reason recorded in `results/item_map.json`):**
  - Items 11, 22, 25, 28, 31, 35, 50, 54 and 56: untagged, and the counting rule is off by 2 before the first tag.
  - Items 150, 155, 168, 188 and 204–209: in unlabelled stretches, where the count and the tags disagree by up to 39.

## Text and statistic (E1)

### Text
- **Herbal page:** ZL 3b `P` text, labels excluded.
  - Uncertain spaces (`,`) merged; tokens containing `?` or `*` dropped; first reading of ZL alternates.
- **Labels:** the same rules.
  - Words split at `.`.
  - Separate label strings of one item are separate words (item 110: otal | chor | olekor).
  - Label words containing `?`/`*` are dropped (none among the 13).
- **Units:** glyph units (`c[tkpf]h|[cs]h|i+[nrlm]|.`).

### Reference set R
All herbal (`$I=H`) pages of ZL 3b with ≥ 40 readable P-text tokens: **128 pages**. Only f65r (0 tokens) is left out.
- R includes the 12 matched pages and f65v (no Currier language assigned).
- Frozen list:

f1v f2r f2v f3r f3v f4r f4v f5r f5v f6r f6v f7r f7v f8r f8v f9r f9v f10r f10v f11r f11v f13r f13v f14r f14v f15r f15v
f16r f16v f17r f17v f18r f18v f19r f19v f20r f20v f21r f21v f22r f22v f23r f23v f24r f24v f25r f25v f26r f26v f27r
f27v f28r f28v f29r f29v f30r f30v f31r f31v f32r f32v f33r f33v f34r f34v f35r f35v f36r f36v f37r f37v f38r f38v
f39r f39v f40r f40v f41r f41v f42r f42v f43r f43v f44r f44v f45r f45v f46r f46v f47r f47v f48r f48v f49r f49v f50r
f50v f51r f51v f52r f52v f53r f53v f54r f54v f55r f55v f56r f56v f57r f65v f66v f87r f87v f90r1 f90r2 f90v2 f90v1
f93r f93v f94r f94v f95r1 f95r2 f95v2 f95v1 f96r f96v

### Statistic
- **Distance:** d(w, p) is the minimum glyph-unit edit distance (unit costs) from label word w to any token of page p.
- **Calibration:** F_w(d) = (1 + #{r ∈ R : d(w, r) ≤ d}) / (1 + |R|).
- **Pair score:** h(i, p) = max over the words w of label i of −log2 F_w(d(w, p)), where a word counts only if
  d(w, p) ≤ 2 (otherwise it contributes 0).
- **Primary statistic:** T = Σ over the 13 pairs of h(label_i, matched page_i).

This scores surprisal of the closest match, so common word shapes score about 0 everywhere and near matches of rare
forms score high.

## Null and test
- **Null:** permute the 13 page slots among the labels. f96v fills two slots (items 94 and 116).
- **What the null holds constant:** every additive label effect (length, shape, number of words) and every additive
  page effect (length, Currier language, scribe) cancels. Only label × page interactions remain.
- **p-value:** p = (1 + #{T_perm ≥ T_obs}) / (1 + 100,000), from 100,000 permutations with seed 766.

## Power (E2; computed before any real-pairing statistic, uses no real pairing)
- **Surrogate pages:** each draw assigns the 13 labels to surrogate pages from R minus the 12 matched pages.
  - 12 distinct pages, one used twice, with the same Currier-language mix as the matched set: 10 A (one used twice,
    for items 94 and 116, as f96v is) and 2 B.
  - Token counts lie within the matched range, 54–111. The pools hold 70 A pages and 22 B pages.
- **Plants:** in k randomly chosen pairs, the label's longest word (glyph units; first on ties) replaces a random
  token of its surrogate page, in two forms:
  - (a) unchanged;
  - (b) with one glyph-unit substitution: a random position, replaced by a different unit drawn from R's glyph-unit
    frequencies.
- **Calibration:** F_w is recomputed with the modified surrogate pages in R, since in the real test the matched page
  is a member of R.
- **Scale:** primary test with 10,000 permutations; 200 draws per k, k = 0..13 (k = 0 estimates size); seed 766.
- **MDE80(a), MDE80(b):** the smallest k with power ≥ 0.80.
- **Per label:** the h an exact plant earns, and its percentile among the label's h over all R pages. Low percentiles
  flag rows that cannot move T.

## Decision rule (E6)
| Verdict | Condition | Reported as |
|---|---|---|
| **ABOVE NULL** | p ≤ 0.05 | |
| **NO SIGNAL (bounded)** | p > 0.05 and MDE80(a) ≤ 4 | "no label–page similarity above the pairing null; ≥ MDE80(a) exact (MDE80(b) one-glyph) matched pairs of 13 would be detected with 80% power" |
| **UNINFORMATIVE** | p > 0.05 and MDE80(a) > 4 | 4 leaves a margin below the five same-plant pairs |

## Variants (reported; the primary verdict stands)
F_w is recomputed on each variant's own text unit.

| Variant | Change |
|---|---|
| V1 | "same plant" pairs only (5; exact enumeration, 120 permutations; descriptive, since the smallest possible p is 0.008) |
| V2 | jar labels added to the label words (items 80, 94, 95) |
| V3 | item 203 excluded (container-coded label; 12 pairs) |
| V4 | first P-text line of each herbal page, for both page text and R |
| V5 | H-track text (P placement, uncertain tokens dropped) for both page text and R |
| V6 | EVA characters in place of glyph units |
| V7 | the draft statistic: max over label words and page tokens of 1 − ED/max(len), in glyph units |
| V8 | restricted permutation (E3): pages permuted only within pharma-folio groups {80, 94, 95, 110} (f99), {116, 133, 136} (f100), {203, 212, 213, 225, 240} (f102); item 61 fixed; exact enumeration (17,280); controls folio-level hand/register × page interactions (C902) |

## Descriptive (E3)
- **Leave-one-pair-out p** (13 values). If removing one pair flips the verdict, report "single-pair-driven"; the
  verdict itself is unchanged.
- **Leave-f96v-out p:** items 94 and 116 removed, 11 pairs.
- **Labels 94 and 116 (both matched to f96v):** the glyph-unit edit distance between their words, ranked among all 78
  label pairs. This check does not use the herbal text.
- **Per pair:** the best-matching token, its d, and the number of R pages reaching that d.

## Registry consequences (E8)
| Verdict | Consequence |
|---|---|
| **ABOVE NULL** | A Tier-2 measurement row, with the human's sign-off: "label–page glyph similarity of the 13 published pharma–herbal visual matches with ZL-tagged labels exceeds the pairing-permutation null (p = …; V8 p = …); matches not verified text-blind." |
| **NO SIGNAL (bounded)** | A Tier-2 negative-knowledge row with MDE80(a)/(b) (precedent C2071), plus a STATUS_BRIEF §4 note. |
| **UNINFORMATIVE** | Phase record only. |

Any reading of an ABOVE NULL result (naming, reference, meaning) is echo-class. Before it enters STATUS_BRIEF it needs
the human's sign-off and a text-blind re-match: a rater shown only the drawings, with all text masked, reproduces the
pairings.

## Caveats
- **Visual matches can be wrong,** and they were not made text-blind (see above).
- **13 pairs is small.** Only a strong effect is detectable, and the power run states how strong.
- **Labels may not be plant names.** In the pharmaceutical layout they could name parts, preparations or quantities.
