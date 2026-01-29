# C722: Within-Line Accessibility Arch

**Status:** VALIDATED | **Tier:** 2 | **Phase:** B_LEGALITY_GRADIENT | **Scope:** A-B

## Finding

B token accessibility under A-folio filtering follows a **nonlinear arch pattern** by within-line position (KW H=74.4, p=2.67e-15). Line-initial (Q0=0.279) and line-final (Q4=0.282) positions are LESS accessible than medial positions (Q1-Q3=0.301-0.306). Linear correlation is near-zero (Spearman rho=0.011, p=0.097) because the pattern is symmetric, not monotonic.

The arch mirrors C556's SETUP-WORK-CLOSE positional syntax. The mechanism is **morphological composition**: line-initial positions are populated by B-exclusive tokens (daiin at 1.8%, articulator-bearing AX_INIT), medial positions by shared PP-MIDDLE vocabulary (EN is 100% PP per C575), and line-final positions by B-exclusive FLOW tokens (FL at 8.5%). A does not "recognize" B's positional grammar — the correlation is indirect, mediated through morphological profiles that vary by position.

## Implication

B's positional grammar creates a natural accessibility landscape. A's vocabulary authorization preferentially reaches B's operational core (medial WORK positions) while leaving B's structural framing (SETUP/CLOSE boundaries) autonomously determined. This is consistent with C384 (no entry-level coupling) — the pattern is population-level, not addressable.

## Key Numbers

| Metric | Value |
|--------|-------|
| Q0 (initial) mean accessibility | 0.279 |
| Q1 mean accessibility | 0.305 |
| Q2 mean accessibility | 0.306 |
| Q3 mean accessibility | 0.302 |
| Q4 (final) mean accessibility | 0.282 |
| Spearman rho (linear) | 0.011 (p=0.097) |
| Kruskal-Wallis H | 74.4 (p=2.67e-15) |
| SETUP vs WORK (MW) | p=1.9e-8 |

## Provenance

- Script: `phases/B_LEGALITY_GRADIENT/scripts/legality_gradient.py` (T1, T4)
- Extends: C556 (SETUP-WORK-CLOSE), C502.a (morphological filtering)
- Consistent with: C384 (no entry-level coupling), C557 (daiin initial-biased)
