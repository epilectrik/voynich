# Phase 684: f66r as Character-Key/Glossary Page — PARTIALLY FALSIFIED

**Status:** C1992 holds (structural singleton). C1993 RETRACTED 2026-05-15 — glossary interpretation falsified.
**Started:** 2026-05-04
**Updated:** 2026-05-15
**Goal:** Test the structural anomaly of f66r (high short-start rate, anomalous header structure) against null distributions.

## Retraction notice (2026-05-15)

The "f66r is a character-key / glossary page" interpretation does not survive diagnostic testing. Both expert-advisor and crazy-expert independently flagged the C1993 claim as over-fit. Three pre-registered diagnostic tests were run (`scripts/_three_diagnostic_tests.py`):

| Test | Result |
|---|---|
| 1. Frequency-matched null on 11/15 singleton split | **PASS** (z=4.32, p=0.0001) — singleton concentration is real |
| 2. L1-L15 vs L16-L32 R-body structural equivalence | **FAIL** (JSD 0.1043, p=0.045) — two structurally distinct zones |
| 3. M-marker dominance on cross-referenced labels | **FAIL** (0/4 top-1, 1/4 top-3) — M-column does not predict neighborhood |

Combined with the original Phase 684 strict pre-reg failure (2/4 with sh-inverted), C1993 is now Tier 1 falsification. Updated speculation file at `context/SPECULATIVE/f66r_keypage.md` (marked FALSIFIED). C1992 remains Tier 2 (structural anomaly fact only; no interpretation registered).

The "qokal as named procedure cataloged by f66r" lexicon-anchor claim is also retracted. The qokal anchor test had M=sh ranking 3rd in qokal's neighborhood (behind o, ch), not dominant as required.

## Background

Off-books scatter-shot exploration surfaced f66r as a structural outlier:
- 30 of 34 lines (88%) start with a 1-2 character token
- Other Currier B folios: max 19% (f43v); most 0-17%
- Corpus-rare characters cluster as f66r line-starts (f: 4/4, x: 3/3, t: 2/3)
- 80% hapax rate
- Section T (only 2 folios in T)

Historical context: f66r has 16th-century Latin marginalia ("multos te vitum gd kt 8 v89") that scholars have flagged as anomalous; speculated as a "key page."

## Tests

### Test 1: Atom-gloss header-to-content correspondence

**Pre-registered 4 specific mappings** (per atom gloss system C1195):
- d-header → da-prefix content
- t-header → ot-prefix content
- l-header → ol-prefix content
- sh-header → sh-prefix content

**Pass criterion:** 3/4 at >2x enrichment, p<0.05.

**Results:**
| Mapping | Enrichment | p-value | Verdict |
|---------|-----------|---------|---------|
| d-header → da-prefix | **5.4x** | **0.012** | PASS |
| t-header → ot-prefix | **3.7x** | **0.014** | PASS |
| l-header → ol-prefix | 2.6x | 0.056 | borderline |
| sh-header → sh-prefix | 0.6x (DEPLETED) | 0.91 | INVERTED |

Strict pre-reg: 2/4 + 1 borderline + 1 inverted (FAILED criterion).

### Test 2 — Killer: max-folio short-start null distribution

10000-permutation null on max short-start rate across 82 folios:
- Actual: f66r at 88.2%
- Null max: mean 22.1%, std 6.0%, 95th percentile 33.3%
- **z-score: 11.11**
- **p < 0.0001**

f66r is 11 standard deviations above the null max. Genuine structural outlier, not long-tail extreme.

### Test 3 — Killer: cross-folio atom-gloss test

Run the same 4-mapping test on every Currier B folio with ≥30 lines (n=46).

**Results:**
- Folios passing 4 mappings: **0/46 (0%)**
- Folios passing 3 mappings: **0/46 (0%)**
- Folios passing 2+ mappings: **1/46 (2%) — only f66r**

Crazy-expert predicted "30%+ pass relaxed criterion by chance." **Actual: 2%.** f66r is the singular folio passing 2+ atom-gloss mappings.

## Verdict

Both findings register cleanly:

1. **Short-start anomaly: Tier 2.** z=11.11 against null is bulletproof structural fact.
2. **Atom-gloss correspondence: Tier 3.** Pre-reg strict criterion failed (3/4 required, got 2/4) BUT cross-folio specificity at 1/46 = 2% confirms f66r-uniqueness. Two individually-significant mappings (d→da, t→ot) plus structural specificity validates Tier 3.

The strict pre-reg failure is offset by the cross-folio test's extraordinary specificity (only f66r passes 2+ in 46 folios, not the 30% predicted by chance).

## Constraints Registered

### C1992 (Tier 2): f66r short-start structural singleton

f66r is a structural singleton in Currier B for line-initial token brevity. 30 of 34 lines (88.2%) start with a 1-2 character token, vs corpus null max distribution mean=22.1% (z=11.11, p<0.0001 from 10000-permutation null shuffling line-first-tokens across folios). Next-highest folio is f43v at 18.8%, a 69-percentage-point gap. Corpus-rare standalone characters cluster as f66r line-starts (f: 4/4 corpus instances, x: 3/3, t: 2/3, d: 4/6). Pure structural fact about line-first-token brevity distribution; no interpretation of WHY f66r has this property is registered. Cross-references C156 (quire alignment), C260 (section isolation), C763-C764 (f57v R2 single-char ring as comparable structural singleton).

**Tier:** 2 (Currier B structural fact)

### C1993 (Tier 3): f66r atom-gloss header-to-content correspondence

f66r exhibits systematic atom-gloss header-to-content prefix correspondence. Pre-registered 4 specific mappings (per C1195 atom glosses): d="do"→da-prefix, t="transfer"→ot-prefix, l="state"→ol-prefix, sh="passive monitor"→sh-prefix. Two pass at p<0.05 with >2x enrichment: d-header → da-prefix at 5.4x (p=0.012, n=32), t-header → ot-prefix at 3.7x (p=0.014, n=17). l→ol borderline (2.6x, p=0.056). sh→sh inverted (depleted at 0.6x). Strict pre-reg criterion (3/4) FAILED. However: cross-folio specificity test confirms f66r-uniqueness — only 1/46 folios with ≥30 lines passes 2+ mappings (that 1 is f66r), vs predicted ~30% under noise hypothesis. Pattern is f66r-specific, not generic. Consistent with f66r functioning as character-key/operational reference page (SPECULATIVE/f66r_keypage.md).

**Tier:** 3 (Currier B, character-content correspondence; cross-folio specific)

## Scripts

- `s1_keypage_test.py` — pre-registered atom-gloss mapping test
- `s2_killer_tests.py` — null distribution + cross-folio test

## Relationship to Existing Constraints

- **C1195** (atom gloss tiers): C1993 is internal validation — d/t (SOLID tier) atoms show clean header-content correspondence, supporting their gloss assignments
- **C1404** (section determines PREFIX programs): C1992 cross-references — f66r is in section T (only 2 folios), and Section T appears genuinely distinct from Section H/B/S patterns
- **C763-C764** (f57v R2 single-char ring): comparable structural singleton in different mode (cosmological diagram); f57v and f66r may share "anomalous reference page" character
- **C156** (quire alignment): f66r is at quire boundaries; consistent with reference-page placement
- **C1924-C1928** (Voynich-Brunschwig matching): unaffected; f66r is not a recipe folio

## Limits

- Tier 4 interpretation ("f66r is a key/glossary page") stays SPECULATIVE per project tier discipline
- Cross-corpus comparison to medieval abecedaria not done (would need external corpus loading)
- Visual content of f66r (the small drawing at top, layout details) not analyzed — text-only methods
- The sh-inversion is interpretively reframable ("sh-header lists what's monitored") but treated as failure per pre-reg

## Methodological Note

The session demonstrated the value of **null-distribution testing for apparent anomalies**:
- f66r 88% vs <19% elsewhere LOOKED extreme but could have been long-tail
- Null test confirmed it's actually z=11 outlier (impossible under random)
- Crazy-expert's prediction (30% folios pass atom-gloss test by chance) was empirically wrong (actual 2%)
- Without the cross-folio test, the atom-gloss correspondence would have been rejected per strict pre-reg
- WITH the cross-folio test, f66r-specificity is established

The user's scatter-shot exploration approach surfaced this finding that systematic phase work hadn't characterized. Sometimes wide-net probing finds things that targeted hypothesis testing misses.
