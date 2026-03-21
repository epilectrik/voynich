# Phase 618: PREFIX Composition Determinants

**Status:** COMPLETE
**Verdict:** FOLIO_DESIGN_FREEDOM (paragraph-level PREFIX freedom)
**Constraints:** C1808-C1812
**Date:** 2026-03-20

---

## Research Question

C1801 established PREFIX JSD as the strongest single apparatus manifold predictor (r=0.476). C1799 showed vocabulary is entirely absorbed by PREFIX. C1405/C1431 show PREFIX explains 73.6% of paragraph AXM variance and nothing else adds beyond it. But nothing explains what determines PREFIX proportions themselves. Is PREFIX a downstream expression of section+REGIME, or an independent design parameter?

## Design

- 82 B-folios, 23,096 tokens (14 major PREFIXes, 85.9% coverage)
- Five blocks: section effect (KW), REGIME effect (within-section KW + continuous correlations), hierarchical variance decomposition (LOO R2), residual PREFIX→manifold (6 partial Mantel tests), within-folio paragraph PREFIX diversity (ICC)
- Controls: section, REGIME, kernel (k/h/e ratios), headless_frac

## Results

### Block A: Section Effect (KW tests)

| Metric | Value |
|--------|-------|
| Significant PREFIXes | 13/14 |
| Mean eta-squared | 0.21 |
| Top: qo | eta2=0.60 (Bio=0.239, Herbal=0.099) |
| Top: lch | eta2=0.38 |

Section profiles match C1404 expectations (Bio=qo-dominant, Herbal=ch-dominant, Cosmo=BARE-dominant).

### Block B: REGIME Effect

| Context | Significant | Notes |
|---------|-------------|-------|
| Overall | 11/14 | Confounded with section |
| Within-Herbal (n=32) | **1/14** | REGIME barely differentiates PREFIX |
| Within-Stars (n=23) | **3/14** | Modest effect |

BARE_vs_headless_frac rho=+1.000 (definitional overlap — see caveat below).

### Block C: Hierarchical Variance Decomposition (LOO R2)

| Model | Mean LOO R2 | Mean LOO R2 (excl. BARE) |
|-------|-------------|--------------------------|
| Section only | 0.135 | ~0.14 |
| Section + REGIME | 0.132 | ~0.13 |
| Section + REGIME + kernel + headless | 0.176 | **~0.11** |

Note: BARE LOO R2=1.000 when headless_frac is included (tautology). The honest mean excluding BARE is ~0.11. qo is the only substantially section-determined PREFIX (LOO R2=0.58).

### Block D: Residual PREFIX → Manifold (Partial Mantel, n=76)

| Test | r | p | Retention |
|------|---|---|-----------|
| D1: PREFIX → manifold (raw) | 0.453 | 0.0001 | — |
| D2: PREFIX \| section | 0.413 | 0.0001 | 91.2% |
| D3: PREFIX \| REGIME | 0.399 | 0.0001 | 88.2% |
| D4: PREFIX \| section+REGIME | 0.377 | 0.0001 | 83.3% |
| D5: PREFIX \| kernel+headless | 0.427 | 0.0001 | 94.5% |
| D6: PREFIX \| sec+reg+kernel+headless | 0.368 | 0.0001 | **81.4%** |

PREFIX carries manifold information overwhelmingly its own — 81.4% retention after all controls.

### Block E: Within-Folio Paragraph PREFIX Diversity

| Metric | Value |
|--------|-------|
| Qualifying paragraphs | 412 |
| Mean ICC | 0.185 (C1182 sister=0.317) |
| sh ICC (highest) | 0.382 |
| or/pch/ar ICC | <0.05 |
| Within-folio JSD mean | 0.328 |
| Between-folio JSD mean | 0.240 |
| JSD ratio | 1.37 |

PREFIX composition is paragraph-level, not folio-level. Only 18.5% of PREFIX variance is between-folio.

## Scripts

| Script | Runtime | Output |
|--------|---------|--------|
| `scripts/prefix_composition_determinants.py` | ~14s | `results/prefix_composition_determinants.json` |

## Key Findings

### 1. PREFIX Is Not a Proxy (C1810)
PREFIX retains 81.4% of its manifold correlation after controlling for section, REGIME, kernel, and headless rate. Kernel+headless control alone retains 94.5%, confirming PREFIX is not kernel-mediated despite C1715 showing both load on PC1. PREFIX carries apparatus information through channels beyond kernel routing.

### 2. Section+REGIME Explain ~11% of PREFIX Variance (C1808, C1809)
Section significantly affects 13/14 PREFIXes (mean eta2=0.21) but LOO R2 is only 0.14. REGIME adds near-zero within sections (Herbal 1/14 sig, Stars 3/14 sig). After adding kernel+headless, LOO R2=0.11 (excluding BARE tautology). ~89% of PREFIX composition is unexplained by structural variables.

### 3. PREFIX Operates at Paragraph Level (C1811)
ICC=0.185 means 81.5% of PREFIX variance is within-folio (paragraph-to-paragraph). Within-folio paragraph JSD (0.328) exceeds between-folio JSD (0.240). Each paragraph independently selects its PREFIX profile. sh is the most folio-consistent PREFIX (ICC=0.382); or/pch/ar are near-zero.

### 4. Architectural Closure (C1812)
PREFIX composition is an independent paragraph-level design parameter, not downstream of section, REGIME, or kernel ecology. The manuscript's design hierarchy is: section → shared templates (C1569); paragraph → independent PREFIX selection (C1811); PREFIX → dynamics (C1405) → apparatus manifold (C1801). Folio identity = statistical ensemble of paragraph-level PREFIX choices (C1573 + C1812). REGIME is an emergent property of PREFIX composition, not a cause of it.

### 5. qo as Section-Determined Anchor
qo is the only PREFIX substantially section-determined (LOO R2=0.58). Bio has the highest qo (0.239), consistent with C1300 (qo=near-pure THERMAL channel) and Bio's thermal intensity. qo sets a thermal baseline that the section imposes; everything else is paragraph-level free choice around that anchor.

## Caveats

1. **BARE ≡ headless_frac** (rho=1.000): Definitional overlap. BARE tokens (no PREFIX) are essentially headless tokens. Including headless_frac trivially predicts BARE fraction (LOO R2=1.0). Mean R2 reported both with and without BARE.
2. **Within > between JSD** (ratio 1.37): The between-folio JSD uses folio aggregates while within-folio JSD uses paragraph-level vectors. Higher sampling variance at paragraph level may inflate the ratio. ICC is the more reliable measure.
3. **PREFIX coverage**: 85.9% of tokens covered by 14 major PREFIXes. The remaining ~14% includes rare extended PREFIXes (ke, te, ka, po, etc.) not individually tracked.

## Verdict Rationale

FOLIO_DESIGN_FREEDOM: Mean LOO R2 = 0.11 (excluding BARE) < 0.30, and D6 residual Mantel r=0.368 (p=0.0001) is significant. PREFIX is not mediated by kernel (D5 retention=94.5%). The finding is actually stronger than folio-level freedom — ICC=0.185 shows PREFIX is a paragraph-level free parameter.

## Dependencies

- C1801 (PREFIX as strongest manifold predictor, r=0.476)
- C1799 (vocabulary absorbed by PREFIX)
- C1405-C1407 (PREFIX drives paragraph AXM, universal across sections)
- C1431-C1433 (non-PREFIX features add zero)
- C1715 (PC1 loads on PREFIX/kernel axis)
- C1712 (REGIME gradient nature)
- C1569 (section-level parameterization, no folio-level within-domain)
- C1573 (distributional shape recovers folio specificity)
- C1182 (sister concentration ICC=0.317)
