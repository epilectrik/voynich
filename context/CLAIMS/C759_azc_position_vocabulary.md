# C759: AZC Position-Vocabulary Correlation

**Status:** VALIDATED (statistical core) — SHARPENED + glosses STRUCK | **Tier:** 2 | **Phase:** AZC_FOLIO_DIFFERENTIATION | **Scope:** AZC

> **[PHASE_742 AUDIT — 2026-06-01]** Re-tested under a **within-folio** position-label
> permutation null (the original chi² had NO within-folio control; position×folio confounded,
> C760). **Statistical core SURVIVES:** V_obs=0.152 (full) / 0.181 (prefixed-only) vs within-folio
> null 95th=0.123/0.135, **one-sided p=0.0001, B=10000** → position carries vocabulary information
> beyond folio composition; NOT folio-shadow. **BUT scope is narrower than stated:** per-folio (each
> vs its own null) only **8/17** folios show the effect — **7 Zodiac + f68r3 (radial Sun); cosmological
> folios f69r/f67v2 are NULL (0/2).** The effect tracks the **regular radial-medallion scaffold**
> (cf C433/C434), NOT AZC universally. Pooled V (0.152) is *below* the per-folio Vs (0.26–0.36):
> folios carry different position→vocab directions, so there is **no single universal profile.**
> **GLOSSES STRUCK (Tier 3→4):** the physical labels "S=spoke/nymph, C=center, R=ring" CONTRADICT the
> verified f69r geometry (R=radii, **C=outer ring, S=inner ring, W=center** — see
> `context/DATA/AZC_NOTATION_PROVENANCE.md`); placement letters are per-folio parse artifacts, not
> stable physical roles. The pooled **"S=ok+ot=monitoring / C=ch=control"** functional reading
> (Implication #1 below) is a dilution artifact built on those scrambled glosses — **withdrawn.**
> Phase: `phases/PHASE_742_AZC_C759_AUDIT/`. *The PREFIX-profile table below is the original pooled
> tabulation; read it as a diluted cross-folio average, and ignore the spoke/center/ring physical glosses.*

## Finding

Position within AZC diagrams (R, S, C placements) significantly determines vocabulary selection
**within the regular radial scaffold (Zodiac + radial diagrams); not in cosmological folios.**

### Evidence

Chi-squared test: chi2=112.59, df=12, **p<0.001**
Cramer's V: 0.208 (medium effect)

### PREFIX Profile by Position

| PREFIX | R-series (n=1326) | S-series (n=501) | C-series (n=629) |
|--------|-------------------|------------------|------------------|
| ch | 20.5% | 10.9% | **28.3%** |
| sh | 9.2% | 4.1% | 6.4% |
| ok | 14.0% | **29.2%** | 11.9% |
| ot | 24.3% | **27.2%** | 16.8% |

Key patterns:
- **S-positions (spoke/nymph):** 56% ok+ot - interior/boundary markers
- **C-positions (center):** 28% ch - convergence markers
- **R-positions (ring):** Mixed profile, ch+ot dominant

### Position Similarity

| Comparison | Cosine Similarity |
|------------|-------------------|
| R-S | 0.890 |
| R-C | 0.949 |
| S-C | 0.771 |

S-positions are most distinct from C-positions.

### R-Subscript Uniformity

| Comparison | Cosine Similarity |
|------------|-------------------|
| R1-R2 | 0.985 |
| R1-R3 | 0.989 |
| R2-R3 | 0.990 |

R1/R2/R3 are functionally identical - subscripts encode position, not vocabulary.

## Implication

1. **Position encodes semantic function within diagrams.** S-positions favor ok+ot (monitoring), C-positions favor ch (control).

2. **Supports "context-locking scaffold" interpretation.** Different diagram zones have different vocabulary constraints.

3. **R-subscripts are geometric, not semantic.** R1/R2/R3 differ only in physical location, not content.

## Provenance

- Phase: AZC_FOLIO_DIFFERENTIATION
- Script: t4_position_vocabulary.py
- Related: C433 (Block Grammar), C435 (S/R Division)
