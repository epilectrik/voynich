# C1285: TRANSITION Anti-Escape via Role Redirection

**Tier:** 2
**Scope:** B
**Phase:** CATEGORY_MECHANISM_DECOMPOSITION (Phase 455)
**Date:** 2026-02-24

## Statement

TRANSITION-category source MIDDLEs redirect successors away from ENERGY_OPERATOR (escape-capable) toward AUXILIARY (1.24x enriched) and FREQUENT_OPERATOR (1.13x enriched). ENERGY_OPERATOR successor rate is 0.403 for TRANSITION sources vs 0.476 baseline (0.85x). EN->EN self-loop rate is also suppressed: 0.474 for TRANSITION EN sources vs 0.517 baseline. Chi2=47.7, V=0.057, p<0.001. N=2,001 TRANSITION-sourced bigrams, 12,765 other-sourced.

## Architecture

- **Rejects EN self-loop hypothesis.** The expert predicted TRANSITION would create EN->EN self-loops to prevent escape. The opposite occurs: TRANSITION sources have *lower* EN successor rates and *lower* EN->EN self-loop rates.
- **Role redirection mechanism.** TRANSITION vocabulary forces successors into AUX/FQ roles, which lack escape capacity (qo-prefix tokens concentrate in EN per C397/C398). This is a vocabulary-level routing mechanism, not a sequential pattern.
- **Per-token, not sequential.** C1281 showed TRANSITION anti-escape is PREFIX-independent. T2 (FAIL) confirms no sequential clustering. Each TRANSITION token independently redirects its successor.
- **Asymmetric escape architecture confirmed.** C1277: THERMAL escapes via PREFIX routing (qo). C1285: TRANSITION prevents escape via role redirection. Same category system, opposite mechanisms.

## Provenance

- Solves C1281 (TRANSITION anti-escape mechanism unknown)
- Connects C397/C398 (escape role stratification) with C1250 (category system)
- Complements C1277 (THERMAL escape via PREFIX mediation)
