# C727: B Vocabulary Autonomy Rate

**Status:** VALIDATED | **Tier:** 2 | **Phase:** B_LEGALITY_GRADIENT | **Scope:** A-B

## Finding

69.3% of B token types have low-or-zero accessibility under A-folio filtering (C502.a):

| Accessibility Band | Count | Percent | Character |
|-------------------|-------|---------|-----------|
| Zero (completely B-exclusive) | 1684 | 34.4% | No A folio makes them legal |
| Low (0-10%) | 1706 | 34.9% | Accessible by very few A folios |
| Medium (10-50%) | 1147 | 23.5% | Moderately shared |
| High (50-99%) | 352 | 7.2% | Broadly shared |
| Full (100%) | 0 | 0.0% | No token is universally legal |

Mean accessibility across all B types: 0.122. Median: 0.026. No B token is legal under ALL 114 A folios.

Zero-access tokens by role: CC 0% (0/11), EN 0.6% (1/173), FQ 0% (0/33), AX 3.0% (7/232), FL 26.3% (5/19), UN 37.8% (1671/4421). The vast majority of B-exclusive vocabulary is unclassified (UN), consistent with C618 (unique MIDDLEs are 100% UN, 99.7% hapax).

## Implication

B's vocabulary is fundamentally its own. A specifies the ~30% of B types that carry operational content (EN MIDDLEs via C575, FQ shared vocabulary). B autonomously provides the ~70% that is grammatical infrastructure: L-compound operators (C501: 49 types), boundary closers, singleton variants, FL termination tokens, and CC triggers. This is consistent with the four-layer responsibility model: A constrains operational content while B provides its own structural scaffold.

Best-A-folio legality rate: mean 69.9%, range [55.2%, 81.6%]. Even under the most favorable A folio, ~30% of a B folio's tokens remain A-unauthorized — these are B's autonomous structural elements.

## Key Numbers

| Metric | Value |
|--------|-------|
| Mean B type accessibility | 0.122 |
| Median B type accessibility | 0.026 |
| Zero-access types | 1684 (34.4%) |
| Low-or-zero types | 3390 (69.3%) |
| High-access types (>50%) | 352 (7.2%) |
| Full-access types (100%) | 0 (0.0%) |
| Best-A-folio mean legality | 69.9% |

## Provenance

- Script: `phases/B_LEGALITY_GRADIENT/scripts/legality_gradient.py` (accessibility distribution, per-B-folio analysis)
- Confirms: C502.a (filtering cascade reduces to 0.8% legal), C501 (B-exclusive MIDDLE structure)
- Consistent with: C618 (unique MIDDLEs are UN hapax), C575 (EN 100% PP)
