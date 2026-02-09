# C846: A-B Paragraph Pool Relationship

**Tier:** 2
**Scope:** A-B
**Phase:** A_B_PARAGRAPH_CORRESPONDENCE

## Constraint

A paragraphs provide vocabulary pools without specific pairing to B paragraphs. The A→B relationship is POOL-BASED, not ADDRESS-BASED. Best-match relationships are dominated by pool size, not specific correspondence.

> **Aggregation Note (2026-01-30):** This constraint analyzes at paragraph level (306 units).
> C885 establishes that A FOLIO (114 units) achieves 81% vocabulary coverage for B paragraphs,
> compared to 58% at paragraph level. Folio-level aggregation is the operational unit.

## Evidence

Testing paragraph-to-paragraph correspondence:

| Metric | Value |
|--------|-------|
| A paragraphs | 306 |
| B paragraphs | 585 |
| Best-match coverage | 66.2% |
| Random baseline | 26.6% |
| Raw lift | 2.49x |
| Pool-size-controlled lift | **1.20x** |

**Hub concentration reveals pool-based mechanism:**

Only 39 unique A paragraphs serve as "best match" for 568 B paragraphs:

| A Paragraph | B Matches | % | PP Pool Size |
|-------------|-----------|---|--------------|
| f101v2_p0 | 166 | 29.2% | 58 MIDDLEs |
| f101r1_p0 | 150 | 26.4% | 54 MIDDLEs |
| f99v_p0 | 39 | 6.9% | 50 MIDDLEs |
| f100r_p0 | 39 | 6.9% | 52 MIDDLEs |
| f1r_p0 | 37 | 6.5% | 51 MIDDLEs |

Top 10 A paragraphs capture 85.9% of all best matches.

**Pool size correlation:** Spearman rho = 0.694 (p < 0.001) between A paragraph PP pool size and coverage achieved.

**Many tied matches:** Mean 24.5 A paragraphs within 1% of best coverage. Only 47.7% of B paragraphs have a unique best match.

## Interpretation

The 2.49x raw lift is a **selection artifact**, not evidence of specific correspondence:

1. A few large A paragraphs have massive PP pools (50-58 MIDDLEs)
2. These hubs cover most of the PP vocabulary union
3. Best-match selection always finds these hubs
4. Random baseline cannot exploit selection effect

When controlling for pool size, lift drops to 1.20x - the remaining effect is vocabulary clustering within A paragraphs, not specific A→B pairing.

## Structural Model

```
A PARAGRAPH → PP VOCABULARY POOL → B DRAWS FROM POOL
     ↓              ↓                    ↓
  (source)    (available words)    (no specific pairing)
```

B paragraphs operate independently, drawing from whatever vocabulary is available. "Best match" means "largest overlapping pool," not "designated source."

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C384 | CONFIRMS - No A-B token coupling extends to paragraph level |
| C502 | CONFIRMS - Morphological filtering is pool-based, not address-based |
| C735 | CONFIRMS - Pool size dominance at paragraph level (rho=0.694 vs folio rho=0.85) |
| C827 | EXTENDS - Paragraphs aggregate vocabulary pools |
| C845 | ALIGNS - B paragraphs are self-contained, no specific A sources |

## Provenance

- Script: `phases/A_B_PARAGRAPH_CORRESPONDENCE/scripts/paragraph_correspondence.py`
- Data: `phases/A_B_PARAGRAPH_CORRESPONDENCE/results/paragraph_correspondence.json`
- Depends: C384, C502, C735, C827

## Status

CONFIRMED - Pool-based model validated at paragraph granularity.
