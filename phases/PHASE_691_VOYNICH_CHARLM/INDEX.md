# Phase 691: Voynich Character-Level Language Model

**Status:** IN PROGRESS — 691.1 (pre-registration)
**Started:** 2026-05-09
**Goal:** Train a small char-level transformer on the H-track corpus as a research instrument. Use it to test pre-registered predictions about Voynich structure derived from existing constraints, detect transcript-error candidates and structural anomalies, and probe whether the model rediscovers known structural categories independently.

## Background

The structural research has accumulated 2001 constraints across 690 phases. A small char-level LM offers an external, unbiased instrument: train it on the H-track corpus alone and ask whether what it learns is consistent with our hand-built structural model.

Two expert reviews produced consolidated requirements:
- **Expert-advisor:** pre-registration mandatory; falsification framing only; folio-shuffle null required everywhere; section identity must be a probe target, not a free input; transcriber-disagreement grounds anomaly detection (not self-validation).
- **Crazy-expert:** failure modes are informative (uniform PPL → C1025 sufficiency confirmed); attention-head decomposition can falsify C1413; three-LM comparison (Voynich vs Latin vs procedural) is the most diagnostic single experiment for "what is Voynich".

## Sub-phases

- **691.1** — Pre-registered predictions document (this phase, locked before training)
- **691.2** — Build pipeline + train base LM
- **691.3** — Test pre-registered predictions (PASS/FAIL each)
- **691.4** — Anomaly detection vs 18-transcriber ground truth
- **691.5** — Macro-state / atom / forbidden-bigram probes
- **691.6** — Three-LM comparison (Voynich vs Latin vs Forme of Cury)
- **691.7** — *(optional)* Paired bilingual encoder for predictive PL recipe matching

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
