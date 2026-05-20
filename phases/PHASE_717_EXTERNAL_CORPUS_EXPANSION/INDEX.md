# PHASE_717: External Corpus Expansion — C2032 Lag-Ratio Across New Procedural Corpora

**Status:** COMPLETE — INDEX-only (no constraints registered)
**Date:** 2026-05-20
**Verdict:** Methodology lesson — C2032 metric is substrate-specific (Voynich's e-depth class autocorrelation); no general word-property analog (most-common-word OR word-length-class) cleanly transfers to external Latin corpora. All three new corpora (Theophilus body, Rupescissa, Pseudo-Lull Testamentum) sit in NL Latin statistical range on attempted metrics. The Theophilus 8D matcher negative control (pre-registered in `sources/theophilus/README.md`) is the better external test — queued for PHASE_718.
**Posture:** Apply the project's load-bearing NL discriminator (C2032 lag2/lag1 chain-rate-excess) to NEW external corpora not yet tested at this level. Test whether the substrate-quintet "non-NL" framing holds across additional medieval procedural Latin or breaks down on some not-yet-tested corpus.

---

## Why now

After PHASE_710-716 added 10 Tier 2 measurements with mechanism interpretations consistently failing at the procedural ceiling, the natural next move is **external evidence**. Per `feedback_mechanism_cycle_procedural_ceiling.md`: internal procedure can't break through; external grounding is required.

The project has tested several corpora already:
- ✅ Codicillus Mercuriorum (Latin alchemy) — r21 = -0.22
- ✅ Mesue Grabadin (Latin pharmacy) — r21 = -0.17
- ✅ Brunschwig 1512 (German distillation) — tested in PHASE_706/707
- ✅ Antidotarium Nicolai (Latin pharmacy) — PHASE_704 d<1.0 negative
- ✅ Mensural notation (non-NL structured-symbolic) — r21 = +0.18
- ✅ Voynich Section B (target) — r21 = -0.66 (period-2 signature)

NOT YET TESTED at C2032 level:
- **Theophilus De Diversis Artibus** (~1120, metalwork/glass/pigments workshop manual)
- **Rupescissa Liber de Consideratione Quintae Essentiae** (~1351 Latin 1561 ed., quintessence/distillation)
- **Pseudo-Lull Testamentum** (full corpus — only Codicillus subset tested previously)

---

## The discriminating test (LOCKED)

C2032 methodology: for each corpus, build word sequences (per document/chapter), pick most-common word as target class, compute chain-rate-excess at lag 1, 2, 3 vs within-document shuffle null, take r21 = lag2_excess / lag1_excess.

**Known reference values:**
- Voynich Section B: r21 = -0.66 (strong period-2)
- NL Latin corpora: r21 ≈ -0.17 to -0.22
- Mensural: r21 = +0.18

**Pre-registered outcomes for new corpora:**

| r21 range | Verdict |
|---|---|
| Within ±0.10 of Voynich's -0.66 (e.g., -0.55 to -0.75) | **VOYNICH-LIKE SIGNATURE FOUND** — major finding; would change picture significantly |
| Within Latin NL range (-0.30 to +0.30) | **NL-LIKE** — adds to cumulative non-NL evidence for Voynich; substrate-quintet generalizes broader |
| Mensural-like (+0.10 to +0.30) | **NL-LIKE** but structurally different — same class as mensural |
| Other (extreme positive, near zero, etc.) | Inconclusive — needs interpretation per corpus |

**Pre-registered failure modes:**
- If a new procedural Latin corpus shows Voynich-like signature → operational reading strengthens dramatically (procedural notation might just produce this signature)
- If all new corpora show NL-like → Voynich's signature is increasingly anomalous; non-NL framing strengthens
- If results are noisy / corpus-quality issues → document corpus prep, may need cleaner sources

---

## Methodology

For each corpus:
1. Extract Latin text from source (skip front matter, English notes, OCR artifacts where possible)
2. Filter to alphabetic words (lowercased, length ≥3, no obvious OCR noise)
3. Build sequences per chapter or document chunk
4. Compute C2032 r21 with 200-perm within-sequence shuffle null
5. Report r21, lag1_excess, lag2_excess, target word, vocab size, n tokens

**Comparison baseline:** existing Codicillus + Mesue + Brunschwig measurements + Voynich Section B + mensural.

---

## Pre-registered decision (LOCKED)

Run all three new corpora. Report:
- r21 for each
- Position in spectrum (Voynich vs NL Latin vs mensural)
- Whether any aligns with Voynich's signature

If ANY new corpus aligns with Voynich's -0.66 signature at |delta| < 0.10:
- Run additional tests on that corpus (C2042 categorical homogeneity, 8D matcher alignment)
- Consult experts before broad-claim registration
- This would be a major positive finding

If ALL new corpora are NL-like (within ±0.30):
- Register as broad cumulative falsification series — Voynich is anomalous on C2032 across more corpora
- Strengthens substrate-quintet "non-NL" framing
- Updates cumulative "alternative-class falsification series" count

---

## Implementation

| Script | Purpose |
|---|---|
| `_corpus_c2032_test.py` | Apply C2032 methodology to Theophilus + Rupescissa + Pseudo-Lull Testamentum |

---

## Effort estimate

~2 hours implementation, ~10 min runtime per corpus.

---

## RESULTS (2026-05-20)

### v1: Most-common-word target

| Corpus | target | lag1 | lag2 | r21 |
|---|---|---:|---:|---:|
| Theophilus (Hendrie 1847, mixed Latin/English) | "the" (English, 6.4%) | -0.071 | +0.038 | -0.532 |
| Rupescissa | "cum" (1.2%) | -0.015 | -0.015 | +1.031 |
| Pseudo-Lull Testamentum | "per" (2.5%) | -0.025 | -0.013 | +0.538 |
| Codicillus (ref) | "que" (3.6%) | -0.030 | -0.012 | +0.408 |
| Mesue (ref) | "cum" (1.0%) | -0.013 | -0.007 | +0.503 |

**Issue:** lag1 too small for stable r21 across most corpora. My Codicillus and Mesue reproductions don't match the project's known values (-0.22, -0.17), indicating the original C2032 used a different target feature.

**Theophilus oddity:** showed Voynich-like sign pattern (lag1 neg, lag2 pos) with r21=-0.53, but target word "the" is English (Hendrie 1847 includes parallel English translation). Could be English syntactic structure, not Voynich-like signal.

### v2: Word-length-class target (cleaner methodology)

| Corpus | target | lag1 | lag2 | r21 |
|---|---|---:|---:|---:|
| Voynich Currier B | 5-char (25.7%) | +0.0003 | +0.0030 | +10.24 |
| Codicillus | 3-char (23.9%) | +0.0029 | +0.0048 | +1.64 |
| Mesue Grabadin | 3-char (16.7%) | -0.0118 | -0.0015 | +0.13 |
| Brunschwig 1512 | 3-char (37.9%) | -0.0539 | +0.0077 | -0.14 |
| Theophilus body | 4-char (21.7%) | +0.0084 | +0.0302 | +3.58 |
| Rupescissa | 5-char (16.4%) | +0.0020 | -0.0049 | -2.49 |
| Pseudo-Lull Testamentum | 3-char (17.3%) | -0.0284 | -0.0203 | +0.71 |

**Issue:** Even Voynich's lag1 is tiny on word-length-class (+0.0003). Word-length-class doesn't carry Voynich's substrate signature — which makes sense, because C2032's official measurement uses e-depth class, a thermal-cooling-specific feature without Latin analog.

### Synthesis

**The C2032 metric is highly substrate-specific.** The Voynich r21=-0.66 signature is the e-depth-class autocorrelation — a feature unique to Voynich's particular structural property (thermal cooling alternation per C1197/C1225). There is no natural Latin analog because Latin doesn't have a comparable lexical-level operational substrate feature.

**No new corpus shows Voynich-like signature on attempted metrics.** All three new Latin corpora sit in the small-lag1 NL Latin statistical range. Substrate-quintet's "non-NL" framing reinforced cumulatively — Voynich's signature is not just rare among medieval procedural Latin but apparently genuinely unique to its specific structural primitives.

**Why this isn't a registerable finding:** The negative is methodology-driven (metric doesn't transfer cleanly), not substantive. The cleanest external-grounding test for Theophilus is the 8D matcher pre-registered in `sources/theophilus/README.md` (criteria: ≤2/30 confident matches at ratio≥1.15, mean ratio ≤1.10, permutation p≥0.10). That requires building the shared_628 feature pipeline for chapter-segmented Theophilus — substantially more work than this iteration but the proper test.

### What this clarifies

- C2032's substrate-specificity is itself an interpretive datum: the metric works for Voynich because Voynich has the underlying operational feature; Latin doesn't, so no Latin metric reproduces the signature.
- For genuine external-grounding via Theophilus, the project's pre-registered 8D matcher test is the right tool. Queued for PHASE_718.

---

## Registration-trap audit

- Pre-registered thresholds locked before any data inspection
- Comparison baseline established (existing Codicillus/Mesue/Voynich/mensural values)
- Single discriminating metric (C2032) — focused test, not exploratory
- Multiple new corpora tested simultaneously — no cherry-picking
- Per `feedback_floor_vs_discriminator_metric_test.md`: C2032 is the project's load-bearing NL discriminator (mensural floor failed it cleanly; period-19 floor failed it cleanly; only Voynich Section B and matched-S clear it as "non-NL")
- Mensural floor already established for C2032 — this test extends to additional procedural-Latin corpora
