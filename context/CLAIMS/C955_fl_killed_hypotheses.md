# C955: FL Killed Hypotheses Registry

**Tier:** 1 | **Scope:** B | **Phase:** FL_RESOLUTION_TEST + precursor investigation

## Statement

Twelve FL hypotheses were tested and falsified using 1,000-iteration shuffle controls within 11 strong-forward Currier B folios. Per-prefix retests were conducted after discovering the 2D structure (C950).

## Falsified Hypotheses

| # | Hypothesis | Test | Result |
|---|-----------|------|--------|
| 1 | Active control / overshoot-correct | 5 shuffle tests, per-prefix retests | 0/9 prefixes significant, all p > 0.37 |
| 2 | Loop / periodic patterns | Bigram, period-2, period-1, per-prefix | 0/9 prefixes significant, all p > 0.20 |
| 3 | Dampening (variance reduction) | First-half vs second-half variance | ch 4/4 (suggestive, tiny N); others flat |
| 4 | Clean 0->5 ramp per line | Line-by-line stage dump | Only 5.1% span full range; 48% span=0 |
| 5 | PREFIX routing to nearby operations | FL prefix matches nearby OP prefix | p = 0.806 |
| 6 | Cross-line state / progression | Per-prefix Spearman vs line index | 0/9 prefixes significant |
| 7 | Folio-level arc | Per-prefix folio tracking | 2/33 pairs = chance level |
| 8 | Testing criteria (stage = what to test) | FL stage vs nearby role type | Chi2 p = 0.73, V = 0.049 |
| 9 | Preceding role determines FL stage | Kruskal-Wallis | p = 0.30 |
| 10 | Batch processing | FL vs OP prefix distributions | Distributions diverge |
| 11 | Alternation per prefix | Reversal rate vs shuffle | ch p = 0.069 borderline; all others ns |
| 12 | Assessment output for variant selection | NMI at token level, 99.9th threshold | 97.1th (weak pass, fails threshold) |

## What Survived

- FL gradient is real (p < 0.0001)
- FL is two-dimensional (C950)
- FL has weak EN variant coupling (97.1th percentile)
- ch-FL has significant suffix coupling (p = 0.004, C953)
- FL resets per line, within-line order meaningless

## Provenance

- FL_RESOLUTION_TEST phase (scripts 01-06)
- Precursor investigation (scratchpad scripts: test_fl_overshoot.py, test_fl_repetition.py, test_fl_prefix_routing.py, test_fl_prefix_across_lines.py, test_fl_as_test_criteria.py, test_fl_prefix_retest.py)
