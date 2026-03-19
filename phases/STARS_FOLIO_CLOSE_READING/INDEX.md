# Phase 610: STARS_FOLIO_CLOSE_READING

**Status:** COMPLETE
**Verdict:** MONITORING_PHILOSOPHY_CONFIRMED
**Constraints:** C1768-C1771
**Scripts:** `scripts/extract_folio_data.py`, `scripts/make_blind_version.py` (data extraction only; analysis is qualitative)

## Motivation

After 609 phases of aggregate statistical analysis, the project shifted to qualitative close reading. The question: does the constraint system (1766 constraints, atom glosses, kernel structure, category taxonomy) actually produce coherent readings when applied to individual folios? Stars was chosen because it is the only section where h_ratio varies freely per folio (C1154), making it the best testbed for whether the monitoring axis reads coherently at the token level.

## Method

No statistical tests. Expert-advisor agent (all constraints embedded) read raw token-level data for three Stars folios:

1. **Blind test (f104r):** Expert read token dump without knowing h_resid. Predicted monitoring level from text alone.
2. **Extreme pair (f108v vs f107v):** Expert compared the most h-depleted and most h-enriched Stars folios with full context.

## Results Summary

### Blind Test (f104r)
Expert predicted **HIGH-MONITORING** with high confidence. Actual: h_resid = +0.069 (rank 21/23). **Correct.** Evidence cited: h-kernel in compounds across all paragraphs, e-dominance over k, MONITORING-category tokens on 6-8 lines, triple/quadruple kernel tokens.

### Extreme Pair Comparison

| Dimension | f108v (h_resid = -0.101) | f107v (h_resid = +0.075) |
|-----------|--------------------------|--------------------------|
| Paragraphs | 9 large (one = 40% of folio) | 20 small (8 single-line) |
| Kernel | e-dominant (67.6%) | Balanced (k≈48%, e≈42%) |
| Monitoring | Passive/absent | Active checkpoints |
| h position | Buried medially | TERMINAL (endpoint) |
| Sister pairs | Balanced ch/sh | ch-dominant |
| Philosophy | "Trust the process" | "Watch constantly" |

Five dimensions diverge simultaneously. The monitoring axis encodes complete operational philosophies, not a monitoring knob.

## Findings

### F1: Token-level predictive power confirmed
The constraint system enables correct monitoring-level prediction from raw token reading alone (blind test). The expert identified monitoring density, e-dominance, and h-distribution patterns without any aggregate statistics.

### F2: Monitoring axis = operational philosophy
High-h and low-h Stars folios differ across 5 dimensions simultaneously (paragraph architecture, kernel balance, monitoring mode, token morphology, sister pair selection). This is a complete program-structure difference, not a parametric adjustment.

### F3: Bridge vocabulary is invariant to monitoring level
Bridge rate: 88.1% (low-h) vs 88.6% (high-h). The monitoring difference operates through deployment (how tokens are composed and sequenced), not vocabulary (which tokens are available).

### F4: h morphological position tracks monitoring philosophy
In high-monitoring folios, h-kernel appears in TERMINAL compound position (architecturally significant endpoint). In low-monitoring folios, h is buried medially (structurally passive). Monitoring character, not just amount, varies with h_resid.

## Constraints

### C1768: Blind Token-Level Monitoring Prediction Succeeds in Stars
**Tier 2 | Scope: B_Stars**

Expert-advisor reading raw f104r token data (atom glosses, morphology, categories) without aggregate statistics correctly predicted HIGH-MONITORING. Actual h_resid = +0.069 (rank 21/23 in Stars). Evidence: h-kernel distributed across all paragraphs in compound forms, e-dominance over k, MONITORING-category tokens on 6-8 lines, triple/quadruple kernel tokens. The constraint system (C1195 atom glosses, C1250 categories, C1393 positional decomposition) has genuine token-level predictive power for within-Stars monitoring variation.

### C1769: Stars Monitoring Axis Encodes Operational Philosophy
**Tier 2 | Scope: B_Stars**

Extreme-pair comparison (f108v h_resid=-0.101 vs f107v h_resid=+0.075, both R1) reveals the monitoring axis is a complete operational philosophy difference, not a parametric adjustment. Five dimensions diverge simultaneously: paragraph architecture (9 large vs 20 small), kernel balance (e-dominant vs balanced), monitoring mode (passive vs active checkpoints), h morphological position (medial vs TERMINAL), and sister pair selection (balanced ch/sh vs ch-dominant). Low-h programs trust the process to run autonomously ("confidence"); high-h programs insist on constant checking ("vigilance").

### C1770: Bridge Rate Invariant to Monitoring Level Within Stars
**Tier 2 | Scope: B_Stars**

Bridge rate (shared vocabulary fraction) is 88.1% for f108v (lowest h_resid in Stars) and 88.6% for f107v (highest h_resid), a negligible difference. The monitoring axis operates through token deployment (composition, sequencing, positional emphasis) rather than vocabulary sourcing. Consistent with the shared grammar model: all Stars folios draw from the same lexicon but deploy it under different operational strategies.

### C1771: h Morphological Position Tracks Monitoring Philosophy
**Tier 2 | Scope: B_Stars**

In high-monitoring Stars folios (f107v, f104r), h-kernel appears in TERMINAL compound position — the architecturally significant endpoint of HEAD + MOD* + TERM decomposition (C1393/C1394). In the lowest-monitoring folio (f108v), h is buried medially in compounds (structurally passive). This means monitoring character, not just monitoring amount, varies with h_resid. Supports C1394 (TERMINAL atoms encode program endpoints) applied specifically to monitoring: when h is TERMINAL, the instruction "ends with" monitoring; when h is medial, monitoring is incidental to other operations.

## Output Files

| File | Description |
|------|-------------|
| `f104r_blind_analysis.md` | Blind test protocol, prediction, reveal, observations |
| `f108v_vs_f107v_comparison.md` | Extreme pair analysis, five dimensions, surprises |
| `comparison_notes.md` | Phase synthesis |
| `data/f104r_dump.txt` | Full annotated token dump (438 tokens) |
| `data/f104r_blind.txt` | Blind version (aggregate stats stripped) |
| `data/f108v_dump.txt` | Full annotated token dump (570 tokens) |
| `data/f107v_dump.txt` | Full annotated token dump (455 tokens) |
