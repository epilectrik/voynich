# C1352: Dark Folio Span Matches Frequency Expectation

**Tier:** 2
**Scope:** B
**Phase:** DARK_PIPELINE_STRUCTURE (472)

## Constraint

Dark pipeline MIDDLEs span folios at rates consistent with their token frequency under a random-assignment null model. 78.3% have spans within ±2 standard deviations of null expectation; 21.7% are more concentrated than expected; 0% are more dispersed. There is no bimodal "staples vs specialists" split — the span distribution is unimodal with median 8 folios and mean 10.8 folios across 92 reliable dark MIDDLEs (≥5 tokens). The concentrated minority (z<-2) includes MIDDLEs like eed (37 folios observed vs 49 expected) and rc (3 vs 5), indicating some genuine folio specificity beyond frequency effects.

## Evidence

From dark_pipeline_structure.py test T3 (92 reliable dark MIDDLEs, frequency-controlled null):

| Category | Count | Fraction |
|----------|-------|----------|
| Concentrated (z<-2) | 20 | 21.7% |
| Expected (-2<z<2) | 72 | 78.3% |
| Dispersed (z>2) | 0 | 0.0% |

| Metric | Value |
|--------|-------|
| Mean span | 10.8 folios |
| Median span | 8 folios |
| Span=1 (single-folio) | 0 |
| Span≥5 | 89/92 (96.7%) |

**Span distribution shape:** Unimodal, right-skewed. Peak at 5-7 folios (39/92), gradual tail to 38 folios. No bimodality.

**Null model:** For each dark MIDDLE with n tokens, distribute n tokens across folios proportional to folio size (multinomial), count unique folios. 1000 permutations.

## Interpretation

The absence of a staples-vs-specialists split argues against a simple material vocabulary. In a material vocabulary, you'd expect a few "universal" materials (water, salt) appearing in most folios and many specialized materials in 1-2 folios, producing a bimodal span distribution. Instead, dark MIDDLEs span folios at roughly the rate their frequency predicts — their folio distribution is a consequence of their overall abundance, not of a material-referent role.

The 22% concentrated minority (more folio-specific than frequency predicts) could represent genuinely specialized context parameters — dark MIDDLEs that are not just rare but preferentially deployed in specific folios. This asymmetry (concentrated minority, no dispersed MIDDLEs) is consistent with folio-level parameterization: some parameters are folio-specific configurations, but none are artificially spread across more folios than their frequency warrants.

## Provenance

- dark_pipeline_structure.json: test T3
- Extends: C1135 (dark aggregate stats — mean 5.7 tokens, now shown to produce median 8-folio span)
- Extends: C1148 (section concentration — T3 shows concentration is primarily frequency-driven, not an independent property)

## Status

CONFIRMED — dark folio span is frequency-matched (78.3% within ±2σ of null), with a concentrated minority (21.7%) but no dispersed outliers and no bimodal split.
