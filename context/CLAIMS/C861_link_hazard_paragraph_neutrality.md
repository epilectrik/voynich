# C861: LINK/Hazard Paragraph Neutrality

**Status:** Validated
**Tier:** 2
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

LINK (class 29) and hazard FL (classes 7, 30) are **evenly distributed** across paragraph ordinals. No paragraph position specializes in monitoring or hazard navigation.

## Evidence

```
LINK rate by ordinal (CV = 0.16):
  Par 1: 2.5%
  Par 2: 3.5%
  Par 3: 3.5%
  Par 4: 3.5%
  Par 5: 2.8%
  Par 6: 2.5%
  Par 7: 2.6%
  Par 8: 3.3%

Hazard rate by ordinal (CV = 0.21):
  Par 1: 3.9%
  Par 2: 3.9%
  Par 3: 3.5%
  Par 4: 3.9%
  Par 5: 1.8%  (anomalous dip)
  Par 6: 3.2%
  Par 7: 3.5%
  Par 8: 3.3%
```

## Position Within Paragraph

```
         Header (Line 1)    Body
LINK     20.6%             79.4%
Hazard   19.1%             80.9%
```

Both concentrate in body, not header. ~80% body allocation.

## Interpretation

Monitoring (LINK) and hazard navigation are paragraph-internal operations, not paragraph-level specializations. Each paragraph independently manages its own control requirements.

## Related

- C821-C823 (regime-line syntax)
- C855 (role template)
