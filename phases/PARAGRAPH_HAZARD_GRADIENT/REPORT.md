# Phase 529: Paragraph-Level Hazard Gradient

**Date:** 2026-03-05
**Status:** COMPLETE
**Constraints Produced:** C1467-C1469

---

## Research Question

Phase 528 (C1463) proved that lines have a monotonic hazard gradient: ZERO-hazard frames concentrate at SPECIFICATION (Q0, 1.236x), IMMUNE (k-HEAD) at THERMAL_WORK (Q1-Q3, 1.165x), and HIGH-hazard frames at CLOSURE (Q4, 1.134x). Does this safety architecture repeat at paragraph scale -- creating a nested safety design with the same topology at two levels?

## Method

23,090 Currier B tokens (H-track, labels excluded, uncertain excluded) were assigned to paragraphs using gallows-initial detection (C864). 590 paragraphs were identified. Each token received:
- **Paragraph zone:** HEADER (first line of paragraph), BODY (middle lines), TAIL (last line)
- **Frame hazard class:** HIGH (7 frames), ZERO (3 frames), IMMUNE (k-HEAD), LOW (default) from decoder_maps.json
- **Line position:** quintile and zone (SPECIFICATION/THERMAL_WORK/CLOSURE per C1463)

Eight tests plus two supplementary tests were run.

## Token Distribution

| Category | N | % |
|----------|---|---|
| HEADER | 5,982 | 25.9% |
| BODY | 13,317 | 57.7% |
| TAIL | 3,791 | 16.4% |

| Hazard Class | N | % |
|-------------|---|---|
| LOW | 10,552 | 45.7% |
| HIGH | 4,782 | 20.7% |
| ZERO | 4,656 | 20.2% |
| IMMUNE | 3,100 | 13.4% |

Paragraph length distribution: median=3 lines, mean=4.2, range 1-33. 257 paragraphs (43.6%) have 4+ lines. 90 single-line paragraphs were included (HEADER = TAIL for these).

## Results Summary

### T1-T2: Paragraph Zone x Hazard Contingency (C1467)

The core interaction is overwhelming: chi2=233.9, dof=6, p=1.15e-47, V=0.071.

| Zone | HIGH | LOW | ZERO | IMMUNE |
|------|------|-----|------|--------|
| HEADER | 1.057x | **1.130x** | **0.784x** | **0.793x** |
| BODY | 0.936x | 0.959x | **1.077x** | **1.121x** |
| TAIL | **1.134x** | 0.939x | 1.069x | 0.900x |

**Critical finding:** The paragraph-level pattern is TOPOLOGICALLY DIFFERENT from the line-level pattern (C1463):

| Feature | Line Level (C1463) | Paragraph Level |
|---------|-------------------|-----------------|
| V | 0.085 | 0.071 |
| Safe/ZERO enrichment | SPECIFICATION (1.236x) | BODY (1.077x) |
| IMMUNE enrichment | THERMAL_WORK (1.165x) | BODY (1.121x) |
| HIGH enrichment | CLOSURE (1.134x) | TAIL (1.134x) |
| Opening zone profile | SAFE-first | INFRASTRUCTURE-first |

The magnitudes are comparable (ratio 0.84), but the topology differs: line-level SPECIFICATION concentrates ZERO (safe), while paragraph-level HEADER concentrates LOW (infrastructure). This is NOT a fractal repetition.

### T3-T4: e->y and k-IMMUNE Body Concentration (C1468)

The two categorically safe vocabulary types both concentrate in paragraph BODY, not HEADER:

| Frame | HEADER | BODY | TAIL |
|-------|--------|------|------|
| e->y (ZERO) | **0.796x** | 1.077x | 1.052x |
| k-HEAD (IMMUNE) | **0.793x** | **1.121x** | 0.900x |

e->y mean paragraph position: 0.492 (slightly later than corpus mean 0.467). The primary safe pathway is a BODY phenomenon at paragraph scale, not a header phenomenon.

### T5: No Monotonic Paragraph-Position Gradient

The quintile-by-quintile HIGH hazard rate across normalized paragraph position shows NO significant monotonic trend:

| PQ | N | HIGH% |
|----|---|-------|
| PQ0 | 3,881 | 19.0% |
| PQ1 | 3,394 | 20.1% |
| PQ2 | 2,417 | 17.3% |
| PQ3 | 3,263 | 20.2% |
| PQ4 | 3,466 | 20.2% |

Spearman rho=0.600, p=0.285 (NS with 5 data points). First-line vs last-line HIGH rate ratio: 1.073 -- modest and not statistically significant as a continuous gradient. The paragraph hazard effect is concentrated at zone boundaries (HEADER and TAIL), not distributed as a smooth gradient.

### T6: Fractal Comparison

| Scale | V | Verdict |
|-------|---|---------|
| Line (C1463) | 0.085 | -- |
| Paragraph | 0.071 | COMPARABLE magnitude |
| Ratio | 0.84 | DIFFERENT topology |

The paragraph-level effect is 84% of the line-level effect size. Both are statistically overwhelming (p < 10^-47). But they have different organizing principles (safe-first at line level, infrastructure-first at paragraph level).

### T7: Paragraph Length Interaction

| Length | N | V | TAIL HIGH |
|--------|---|---|-----------|
| Short (2-3) | 5,895 | 0.057 | 1.014x |
| Medium (4-5) | 5,917 | 0.061 | 1.019x |
| Long (6+) | 10,504 | 0.060 | **1.274x** |

Long paragraphs show the strongest TAIL hazard concentration (1.274x), consistent with longer operational sequences accumulating more hazardous closures. Short paragraphs show essentially no TAIL HIGH enrichment. The HEADER pattern is stable across lengths.

### T8: Header Infrastructure Composition

Headers have a distinctively LOW-heavy profile:
- LOW: 51.6% (vs 43.8% body, 42.9% tail)
- ZERO: 15.8% (vs 21.7% body, 21.6% tail)
- IMMUNE: 10.6% (vs 15.1% body, 12.1% tail)

The 51.6% LOW rate at headers means that over half of all header tokens use MIDDLEs whose HEAD x TERM frame is not one of the 7 HIGH, 3 ZERO, or k-HEAD IMMUNE categories. These are the MARKING/STAGING specification tokens (C1287).

### T-Extra: Line Gradient Persists Within Paragraph Zones (C1469)

The line-level hazard gradient (C1463) operates INDEPENDENTLY within every paragraph zone:

| Paragraph Zone | N | Line V | Line-Q0 HIGH% | Line-Q4 HIGH% | Q4/Q0 |
|---------------|---|--------|---------------|---------------|-------|
| HEADER | 5,982 | 0.079 | 20.6% | 23.9% | 1.16 |
| BODY | 13,317 | **0.094** | 15.5% | 22.0% | 1.42 |
| TAIL | 3,791 | 0.091 | 18.4% | 27.8% | 1.51 |

All three within-zone V values are highly significant (p < 10^-11). The BODY zone shows the STRONGEST within-zone line gradient (V=0.094, exceeding the corpus-wide V=0.085). TAIL shows the steepest Q4/Q0 ratio (1.51). This confirms that line-level safety architecture operates independently of paragraph position.

### T-Extra: Section Universality

The TAIL > HEADER HIGH rate pattern is present in 4/5 sections (B, H, S, T). Section C (Cosmo) shows slightly higher BODY HIGH rate than TAIL, consistent with its uniformly high-hazard profile. Per-section V ranges from 0.039 (Section B, low baseline hazard) to 0.119 (Section T, small N=660).

## Constraints Produced

| ID | Title | Key Finding |
|----|-------|-------------|
| C1467 | Paragraph zone x hazard interaction (non-fractal) | V=0.071 comparable to line V=0.085 but DIFFERENT topology: LOW-first not SAFE-first |
| C1468 | Header infrastructure-first composition | HEADER LOW 1.130x, ZERO 0.784x; headers use infrastructure not safe vocabulary |
| C1469 | Line hazard gradient paragraph-independent | Within-zone line V=0.079-0.094; line gradient persists independently in all paragraph zones |

## Interpretive Significance

This phase resolves the fractal safety hypothesis: the answer is NO -- the paragraph and line levels do NOT repeat the same topology. Instead, they implement COMPLEMENTARY architectures:

1. **Line level (C1463):** SAFE-first design. Lines open with categorically safe e->y vocabulary and close with hazardous a/d-HEAD operations. This is a TOKEN-LEVEL safety mechanism.

2. **Paragraph level (C1467):** SPECIFICATION-first design. Paragraphs open with infrastructure/specification vocabulary (MARKING, STAGING per C1287) and accumulate hazardous operations at TAIL. This is a STRUCTURAL safety mechanism.

3. **The two levels are independent (C1469):** The line gradient operates unchanged within every paragraph zone. Even within hazardous TAIL lines, the line's own internal structure puts safe tokens first.

The combined architecture means: no matter where you are in a paragraph, each line independently applies its own safety gradient. Safety is enforced at the LINE level, while the paragraph level handles operational specification and sequencing.

This connects to:
- C1399/C1400 (paragraphs independently composed, no ordering)
- C1398 (paragraph operational gradient -- continuous variation)
- C1425-C1430 (three-zone line model)
- C1457-C1462 (e->y as pre-emptive safety anchor -- confirmed as LINE-level mechanism)

## Files

- **Script:** `phases/PARAGRAPH_HAZARD_GRADIENT/scripts/paragraph_hazard_gradient.py`
- **Results:** `phases/PARAGRAPH_HAZARD_GRADIENT/results/paragraph_hazard_gradient.json`
