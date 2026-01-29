# RECOVERY_ARCHITECTURE_DECOMPOSITION

**Phase status:** COMPLETE | **Constraints:** C634-C636 | **Date:** 2026-01-26

## Objective

Determine whether recovery architecture is unconditionally free (per-folio choice), class-mediated (explained by class composition), or regime-stratified (REGIMEs impose distinct strategies beyond composition). Tests kernel absorption, recovery path lengths, post-kernel routing, escape sub-group composition, and folio-level feature batteries with partial correlation controlling for class composition.

## Key Findings

1. **Recovery pathways NOT regime-stratified** (C634). 0/13 KW tests significant for kernel absorption rates, recovery path lengths, and post-kernel destination routing across 4 REGIMEs. Kernel exit rate ~98-100% everywhere.

2. **Escape strategies NOT regime-stratified** (C635). 0/9 per-folio KW tests significant for EN/CC sub-group composition in recovery zones and first-EN-after-hazard routing. Aggregate chi-squared on first-EN is significant (p=0.0003) but reflects pooled counts, not per-folio consistency. REGIME fingerprint JSD 0.031-0.082 (near-identical).

3. **Recovery UNCONDITIONALLY FREE with SUPPRESSOR effect** (C636). 10/12 composite features are FREE (no REGIME dependence at any level). 2/12 features (e_rate, h_rate) show SUPPRESSOR pattern: not significant raw (p>0.5) but highly significant after controlling for class composition (partial p=0.0005, eta_sq=0.188 for e_rate; partial p<0.0001, eta_sq=0.293 for h_rate). Class composition masks a latent REGIME effect on kernel routing (e vs h absorption).

## Verdict

Recovery architecture is **UNCONDITIONALLY FREE**: each folio independently determines its recovery strategy. The e/h kernel routing suppressor effect is a secondary finding -- REGIMEs may encode a latent preference for HOME_POSITION (e) vs h absorption, but this is invisible without controlling for composition and does not affect the dominant characterization.

## Scripts

| Script | Sections | Output |
|--------|----------|--------|
| `recovery_pathway_profiling.py` | Kernel absorption rates, recovery path lengths, post-kernel destinations, summary | `results/recovery_pathway_profiling.json` |
| `escape_strategy_decomposition.py` | EN recovery zones, first-EN-after-hazard, CC triggers, fingerprints | `results/escape_strategy_decomposition.json` |
| `recovery_regime_interaction.py` | Feature battery, raw KW, partial correlation, overall verdict | `results/recovery_regime_interaction.json` |

## Data Dependencies

- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`
- `phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json`
- `scripts/voynich.py`
