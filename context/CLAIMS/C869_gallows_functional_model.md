# C869: Gallows Functional Model

**Status:** Validated
**Tier:** 3
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

Gallows characters at paragraph start function as procedure-type markers with distinct roles:
- **f**: Folio opener/header (HT-rich, PHARMA-specific)
- **k**: Special e-pathway opener (front-biased, unique morphology)
- **p**: Primary processing mode (self-continuing, stable)
- **t**: Transitional mode (returns to p, temporary excursion)

## Evidence Summary

| Gallows | Position | Morphology | Content | Transition |
|---------|----------|------------|---------|------------|
| f | 0.30 (front) | Often bare | 54% HT, 23% EN | - |
| k | 0.35 (front) | Uses 'e' POST | Normal | 18% self |
| p | 0.52 (middle) | ch/o complete | Normal | 54% self |
| t | 0.49 (middle) | sh/e complete | Normal | 31% self, 50% -> p |

## Model

```
FOLIO STRUCTURE:

[f/k opener]  ->  [p continuation]  ->  [t excursion]  ->  [p return]
    |                   |                    |                  |
  Setup            Main process         Adjustment         Resume main
```

### Content Signatures

| Gallows | HT Rate | EN Rate | Section |
|---------|---------|---------|---------|
| f | 54% | 23% | PHARMA (25%) |
| k | 34% | 33% | BIO elevated |
| p | 33% | 31% | BIO dominant (4.1x vs t) |
| t | 35% | 33% | PHARMA equal to p |

## Distillation Interpretation

| Gallows | Role | Analog |
|---------|------|--------|
| f | Material identification | "Here's what we're working with" |
| k | Initial setup | "Prepare apparatus using e-pathway" |
| p | Main processing | "Standard distillation procedure" |
| t | Adjustment phase | "Temporary modification, then resume" |

## Tier Justification

Tier 3 (Speculative) because:
- Structural patterns (Tier 2) are established
- Functional interpretation requires domain semantics
- "Opener" and "mode" labels are plausible but not proven

## Provenance

Scripts: 10-15 in FOLIO_PARAGRAPH_ARCHITECTURE

## Related

- C864-C868 (structural gallows findings)
- C863 (paragraph-ordinal EN gradient)
- C840-C845 (paragraph structure)
