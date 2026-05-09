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
- **691.3** ✅ — Test pre-registered predictions: **7/10 PASS** (P1, P2, P4, P6, P7, P9, P10); P7 confirmed via 691.5 token-level reformulation
- **691.4** ✅ — Anomaly detection vs 18-transcriber: 1.55x enrichment unstratified
- **691.4b** ✅ — Stratified anomaly: **3.40x aggregate enrichment**, 6.21x at length-8
- **691.5** ✅ — Token-level P7 reformulation: **PASSES**, forbidden pairs penalized 25x more than legal (p=0.0011, confirms C109/C997)
- **691.5b** ✅ — A-only vs B-only LMs: cross-system perplexity asymmetric (B-LM 2.8x more native-fit), Procrustes alignment ratio 0.30 (substantial but imperfect alignment), B-LM penalizes forbidden pairs 30% more than A-LM. Refines C2005 framing: A and B share substrate + ~70% structure but B layers contextual tightening.
- **691.5d** ✅ — Scaffolding folio confirmation: **f57v (z=+7.26 rank 1/224)**, f66r (z=+1.61), f49v (z=+1.41) all flagged as anomaly-rich; rosettes foldout (f86v3-v6) NOT flagged (operational, not instructional). 3/4 testable candidates confirmed.
- **691.6** OPEN — Three-LM comparison (Voynich vs Latin vs procedural). De-prioritized after 691.5b directly addressed the leverage gap. Still valuable for compression-curve / what-is-Voynich question.
- **691.7** OPEN — Bilingual encoder. Per expert-advisor: PREMATURE (n=15 confirmed pairs too small for paired training).

## Aggregate findings (Phases 691.1-691.5d)

External char-LM corroborates 7 of 10 structural-claim categories from independent training. Plus refines structural model via cross-section comparison and confirms scaffolding-page hypothesis.

**Real findings (not just confirmations):**
- **P8 → 691.5b refinement:** A and B share atom substrate AND ~70% of grammatical structure (Procrustes residual 0.30 vs 1.0 random). B layers ~30% additional contextual tightening on top — confirmed by 2.8x asymmetric native-fit. Refutes "two different systems" reading; supports "two operating modes of one system."
- **691.5d scaffolding confirmation:** f57v ranks #1 most-surprising of 224 folios at z=+7.26. f66r and f49v in top 13. Rosettes NOT flagged. The "manuscript contains explicit scaffolding pages" hypothesis (Phase 684) is corroborated by independent LM-derived measure.

**Newly proposed constraints (per expert-advisor framing):**
- C2002 — LM-corroborated MIDDLE compositionality (P1+P2+P9). Tier 2.
- C2003 — LM recovers A/B system distinction (reframed from "geometric integration" per expert-advisor). Tier 2.
- C2004 — Frequency-structure geometric independence (P6, confirms C1011). Tier 2.
- C2005 — Same-MIDDLE A-context vs B-context embedding divergence; extends C522 (NOT a falsification of C1499/C1509). Tier 2. Refined per 691.5b: ~70% Procrustes-aligned, ~30% B-tightening.
- C2006 — Stratified-by-length LM surprise correlates 3.40x with 18-transcriber disagreement. Tier 2.
- C2007 — LM flags Phase-684 character-key folio f66r as outlier-rich. **Tier 3** (single-folio replication per expert-advisor).
- C2008 — Token-level forbidden-pair penalty (25x stronger than legal substitution, B-LM 30% stronger than A-LM, confirms C109/C997). Tier 2.
- C2009 — Length-8 H-track tokens with high LM surprise have 41% transcriber-disagreement rate (6.21x baseline). Strong candidate-error pool. Tier 2.
- C2010 — LM-derived folio-mean surprise corroborates "scaffolding page" hypothesis: f57v (z=+7.26, rank 1/224), f66r (rank 12), f49v (rank 13). Tier 2.

## Methodology notes (Tier 3)
- P3 char-level distributional embeddings cannot test C1218 positional grammar without architectural modification (positional masking required).
- P7 char-level synthetic sequences are the wrong test for MIDDLE-class forbidden pairs; token-level substitution required (691.5).

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
