# Phase 639: A-System Functional Types

**Status:** COMPLETE
**Verdict:** FUNCTIONAL_BIFURCATION_CONFIRMED
**Constraints:** C1949-C1951

---

## Research Question

Does the Currier A system contain functionally distinct folio types, and does the dark pipeline's role in A vary by illustration status?

## Background

Both Currier A folios and Currier B Section H folios have plant illustrations. The text-illustration complementarity model (Section H analysis) says B herbal folios lack dark pipeline identifiers because the illustration carries material identity. The question: does the A system show an analogous pattern? And what is f58r/f58v's "master catalog" status (C1942) relative to typical herbal A folios?

## Method

1. Measured raw dark MIDDLE density across all 114 A folios by section → negligible gradient (H=0.006, P=0.008, T=0.009). **Failed** — A system uses RI derivatives, not bare dark MIDDLEs (per C1903).

2. Measured RI-embedded dark substrate: for each A folio, counted tokens whose MIDDLEs contain dark pipeline MIDDLEs as substrings (capturing RI derivatives like `ofch`, `olch`, `octh`). Measured both density and TYPE BREADTH (how many distinct dark bases appear per folio).

3. Classified dark MIDDLEs on herbal outlier folios against C1941 three-class taxonomy.

## Results

### RI-Embedded Dark Substrate by Section

| Section | Folios | Embed fraction | Mean breadth | Total bases |
|---------|--------|---------------|-------------|-------------|
| H (illustrated plants) | 95 | 0.015 | 1.1 | 15 |
| P | 16 | 0.018 | 2.4 | 11 |
| T (catalog) | 3 | 0.040 | 7.0 | 14 |

Section T is 2.7x Section H in embed density. Mean breadth: T=7.0, P=2.4, H=1.1.

### f58r/f58v Master Catalog Profile

| Folio | Tokens | RI-embedded dark | Breadth | Dark bases |
|-------|--------|-----------------|---------|-----------|
| f58r | 366 | 21 (5.7%) | **11** | cs, cth, eet, eke, ep, fch, ir, lch, lk, ro, tsh |
| f58v | 365 | 14 (3.8%) | **8** | eckh, eke, ir, lch, lk, lsh, rai, ro |

f58r catalogs 11 of 16 tested dark base types — near-complete coverage. No other folio exceeds breadth=4.

### Herbal Folio Concentration

Typical herbal A folios have breadth 0-1. They concentrate in 1-2 dark bases relevant to their specific plant's processing requirements:
- Most common: cth (state-transition monitoring), ro (fermentation)
- Material-specific: fch (mercury-process plants), eckh (volatile liquid plants)

### Herbal Outlier Classification (C1941 taxonomy)

ALL high-dark herbal A folios are PROCESS-class, not material or equipment:

| Folio | Dark tokens | Classification |
|-------|------------|---------------|
| f90r2 | ro×2 | PROCESS (fermentation) |
| f10v | cth×2 | PROCESS (state-transition) |
| f96v | ro, eckh | PROCESS + MATERIAL |
| f24r | cth×2, ro | PROCESS |
| f35v | ro, cth | PROCESS |

These are plants requiring specific operational TECHNIQUES (fermentation, state-monitoring), not plants associated with specific minerals.

---

## Constraints

### C1949: A-system RI-embedded dark breadth distinguishes catalog from specification folios (Tier 2)

RI-embedded dark base BREADTH (count of distinct dark pipeline MIDDLEs appearing as substrings in folio's RI MIDDLEs) sharply distinguishes A folio functional types:
- **Master catalog folios** (f58r): breadth=11/16 (near-complete dark vocabulary coverage)
- **Section P folios**: mean breadth=2.4
- **Herbal specification folios**: mean breadth=1.1 (concentrated in 0-2 process-relevant bases)

Raw dark MIDDLE density shows negligible section gradient (0.006-0.009) due to A-system coverage optimization (C755/C756). The signal emerges at the RI derivative level (C1903: 78% of dark MIDDLEs spawn RI derivatives in A).

- Scope: A, dark pipeline, RI, C1903, C1942, C755
- Metrics: T_embed_frac=0.040. H_embed_frac=0.015. T_mean_breadth=7.0. H_mean_breadth=1.1. f58r_breadth=11/16.
- Tier 2 because: measurable structural difference independent of recipe interpretation.

### C1950: Herbal A folio dark tokens are PROCESS-class, not material-class (Tier 2)

High-dark herbal A folios (f90r2, f10v, f96v, f24r, f35v) carry exclusively PROCESS-class dark MIDDLEs (cth=state-transition, ro=fermentation, eke=precision testing) per the C1941 taxonomy. Zero EQUIPMENT-class tokens (lch, lk, eed). Material-class tokens (fch, eckh) appear only where the plant requires that material in its processing (e.g., mercury-process herbs).

This means herbal A folios with elevated dark density are specifying plants that require COMPLEX TECHNIQUES, not plants associated with specific minerals. The dark tokens encode what the plant NEEDS operationally.

- Scope: A, H, dark pipeline, C1941
- Metrics: outlier_folios=5. process_class=100%. equipment_class=0%.
- Tier 2 because: classification against C1941 taxonomy is objective.

### C1951: Dark pipeline serves as text-based channel substitute for illustrations (Tier 3)

The dark pipeline's material identification function (fch=mercury, cs=gold per C1939/C1940) operates as a TEXT-BASED SUBSTITUTE for visual material identification (plant illustrations) in contexts where illustrations cannot carry material identity:
- **Herbal folios** (A and B): Plant illustration identifies the material. Dark density low, concentrated in process-relevant bases.
- **Mineral/chemical B folios** (Section B/S): No illustration for mercury, gold, sulfur. Dark material identifiers (fch, cs, eckh) carry material identity in text.
- **Master catalog A folios** (f58r/f58v): Catalog the full dark vocabulary with near-complete base coverage (breadth 8-11).

This is a CHANNEL SUBSTITUTION model: the same function (material identification) is carried by different channels (visual vs. textual) depending on whether the material can be illustrated. The A system expresses this through RI derivative breadth, not raw dark MIDDLE density.

- Scope: A, B, dark pipeline, illustration, C1939, C1940, C1941, C1942
- Metrics: See C1949 for quantitative support.
- Tier 3 because: the "channel substitution" interpretation is a functional model, not directly measurable. The structural measurements (C1949, C1950) are Tier 2; the interpretation is Tier 3.

---

## Key Methodological Finding

Raw dark MIDDLE density FAILED to distinguish A folio types (H=0.006, P=0.008, T=0.009). The signal only emerged at the RI derivative level (C1903). This confirms that the A system's coverage optimization (C755/C756) operates on the PP/raw MIDDLE layer, suppressing differentiation. The RI layer — where instance-level specification occurs — is where functional bifurcation is measurable.

This has implications for future A-system analysis: always check the RI derivative layer, not just raw MIDDLE distributions.
