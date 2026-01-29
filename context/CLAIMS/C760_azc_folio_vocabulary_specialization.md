# C760: AZC Folio Vocabulary Specialization

**Status:** VALIDATED | **Tier:** 2 | **Phase:** AZC_FOLIO_DIFFERENTIATION | **Scope:** AZC

## Finding

AZC folios are vocabulary-specialized: 70% of MIDDLEs appear in only one folio, while a small universal core (13 MIDDLEs) provides shared vocabulary.

### Evidence

| Category | MIDDLEs | Percentage |
|----------|---------|------------|
| Exclusive (1 folio only) | 424 | 70.1% |
| Shared (2+ folios) | 181 | 29.9% |
| Universal (75%+ folios) | 13 | 2.1% |

Total unique MIDDLEs in AZC: 605

### Family Comparison

| Metric | Zodiac (13 folios) | A/C (15 folios) |
|--------|-------------------|-----------------|
| Mean tokens/folio | 112.7 | 91.0 |
| Mean MIDDLEs/folio | 59.7 | 51.3 |
| Mean TTR | 0.545 | 0.640 |
| Mean exclusivity ratio | 0.264 | 0.263 |

Exclusivity t-test: p=0.98 (no family difference)

### Specialist vs Generalist

14 folios classified as specialists (exclusivity > median):
- Top specialist: f68r3 (45% exclusive MIDDLEs)
- Mix of Zodiac (7) and A/C (7)

14 folios classified as generalists:
- Top generalist: f69r (15% exclusive MIDDLEs)
- Also mixed between families

Chi-squared for family x specialization: p=1.0 (random distribution)

## Implication

1. **Each AZC folio contributes unique vocabulary.** The 424 exclusive MIDDLEs represent folio-specific constraint options.

2. **Universal core provides shared infrastructure.** The 13 universal MIDDLEs appear across nearly all folios - these are the shared operational vocabulary.

3. **Specialization is not family-determined.** Both Zodiac and A/C families contain specialists and generalists.

4. **Consistent with "folio-specific scaffolds."** C436 notes A/C has varied scaffolds; this shows vocabulary varies correspondingly.

## Provenance

- Phase: AZC_FOLIO_DIFFERENTIATION
- Script: t3_azc_specialization.py
- Related: C430 (Bifurcation), C436 (Dual Rigidity)
