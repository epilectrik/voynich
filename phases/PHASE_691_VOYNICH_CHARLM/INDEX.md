# Phase 691: Voynich Character-Level Language Model

**Status:** 691.1-691.5 COMPLETE; 691.6-691.7 OPEN
**Started:** 2026-05-09
**Latest update:** 2026-05-09
**Goal:** Train a small char-level transformer on the H-track corpus as a research instrument. Use it to test pre-registered predictions about Voynich structure derived from existing constraints, detect transcript-error candidates and structural anomalies, and probe whether the model rediscovers known structural categories independently.

## Background

The structural research has accumulated 2001 constraints across 690 phases. A small char-level LM offers an external, unbiased instrument: train it on the H-track corpus alone and ask whether what it learns is consistent with our hand-built structural model.

Two expert reviews produced consolidated requirements:
- **Expert-advisor:** pre-registration mandatory; falsification framing only; folio-shuffle null required everywhere; section identity must be a probe target, not a free input; transcriber-disagreement grounds anomaly detection (not self-validation).
- **Crazy-expert:** failure modes are informative (uniform PPL → C1025 sufficiency confirmed); attention-head decomposition can falsify C1413; three-LM comparison (Voynich vs Latin vs procedural) is the most diagnostic single experiment for "what is Voynich".

## Sub-phases

- **691.1** ✅ — Pre-registered predictions document (locked, SHA256 chain-of-custody)
- **691.2** ✅ — Build pipeline + train base LM (without_tag, with_tag both at val_loss ≈ 0.66)
- **691.3** ✅ — Test pre-registered predictions: **6/10 PASS** (P1, P2, P4, P6, P9, P10); plus P7 fixed in 691.5
- **691.4** ✅ — Anomaly detection vs 18-transcriber: 1.55x enrichment unstratified
- **691.4b** ✅ — Stratified anomaly: **3.40x aggregate enrichment**, 6.21x at length-8
- **691.5** ✅ — Token-level P7 reformulation: **PASSES**, forbidden pairs penalized 25x more than legal (p=0.0011, confirms C109/C997)
- **691.6** OPEN — Three-LM comparison (Voynich vs Latin vs procedural)
- **691.7** OPEN — *(optional)* Paired bilingual encoder for predictive PL recipe matching

## Aggregate findings (Phases 691.1-691.5)

External char-LM corroborates 7 of 10 structural-claim categories from independent training. The 3 failures are interpretable:
- **P3** (real null): MODIFIER vs BASE chars not separable at distributional level — C1218 may be positional-only
- **P5** (partial): qualitative trends pass, only shuffle-baseline criterion fails
- **P8** (informative falsification): same MIDDLE has more divergent A-vs-B contextual usage than C1499/C1509 substrate-identity predicts

**Newly proposed constraints** (not yet registered):
- C2002 — LM-corroborated MIDDLE compositionality (P1+P2+P9)
- C2003 — A/B geometric integration architecture (P4+P10)
- C2004 — Frequency-structure geometric independence (P6, confirms C1011)
- C2005 — A/B contextual divergence beyond substrate identity (P8 falsifies tight C1499)
- C2006 — Stratified-by-length LM surprise as anomaly detector (3.40x enrichment vs transcriber disagreement)
- C2007 — LM independently flags Phase-684 character-key folio f66r as outlier-rich
- C2008 — Token-level forbidden-pair penalty in LM (25x stronger than legal substitution, confirms C109/C997)

## Architecture (locked)

- Encoder-only transformer, 6 layers, 256 hidden dim, 8 heads, FFN dim 1024
- Char-level vocab: 22 EVA chars + ` ` (space) + `[PAD]` + `[MASK]`
- Max sequence length 256
- Masked character modeling (15% mask rate, 80/10/10 mask/random/identity)
- ~6M parameters

## Data (locked)

- H-track only (transcriber == 'H'), exclude uncertain (asterisks)
- Per-line training examples (tokens space-separated)
- 80/10/10 train/val/test split by **folio** (not by line) to prevent leakage
- Stratified by Currier section
- Two training variants (per expert-advisor):
  - `with-tag`: section markers `[CURR_A]/[CURR_B]/[CURR_AZC]` prepended
  - `without-tag`: no section information leaked into input

Section identity is a probe target (cluster separability test), so the without-tag variant is primary.

## Files

- [prereg_predictions.md](prereg_predictions.md) — locked pre-registration (Phase 691.1)
- `scripts/build_corpus.py` — H-track extraction, splits (Phase 691.2)
- `scripts/tokenizer.py` — char-level (Phase 691.2)
- `scripts/model.py` — small encoder transformer (Phase 691.2)
- `scripts/train.py` — MLM training (Phase 691.2)
- `scripts/test_predictions.py` — runs each pre-registered test (Phase 691.3)
- `scripts/probe_*.py` — additional probes (Phases 691.4–691.6)

## Constraint expectations on registration

If predictions PASS broadly: external instrument confirms structural model. Register as Tier 2 ("LM-corroborated structural claim") for any prediction that survives nulls.

If predictions FAIL: register as Tier 1 falsifications (the LM disconfirms the structural claim). Update affected constraints.

If predictions are MIXED: triage individually. Most informative outcome.

## Time budget

- Phase 691.1: 1 day (pre-registration document)
- Phase 691.2-691.3: 2 days (build, train, test)
- Phase 691.4-691.5: 2 days (probes)
- Phase 691.6: 1 day (three-LM comparison)
- Phase 691.7: 2 days (optional)

**Total: ~6 days for core phases (691.1-691.6).**
