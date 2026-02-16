### C1082 — HT Oscillation Is Section-Driven, Not Intrinsic

- **Tier:** 2 (ESTABLISHED)
- **Scope:** B (HT density temporal autocorrelation × section structure)
- **Phase:** HT_INTERACTION_ARCHITECTURE (2026-02-15)

**Finding:** HT density across 82 B folios shows significant autocorrelation at raw lags 1,2,4,6,20 (threshold=0.216). Peak ACF at lag 1 (r=0.378). After removing section means (7 section boundaries, 8 quire boundaries), only lag 7 survives above threshold. No signal in the target lag 8-12 range. The reported "~10-folio HT oscillation" is primarily explained by section structure, not by an intrinsic HT rhythm.

**Interpretation:** The open question "Why does HT cluster in ~10-folio oscillations?" is now answered: the oscillation is an artifact of section boundaries. Different sections (H, B, S, C, T) have different mean HT densities (C451: A=0.170, AZC=0.162, B=0.149). When folios from different sections are arranged in physical order, the transitions between sections create apparent periodicity. The residual lag-7 signal may reflect within-section structure (possibly quire-related given C156's 4.3x quire alignment) but does not match the reported ~10-folio period.

**Resolves:** "Why does HT cluster in ~10-folio oscillations?" (INTERPRETATION_SUMMARY.md open question)
**Extends:** C451 (HT system stratification), C156 (section-quire alignment 4.3x)
**Consistent with:** C450 (HT quire clustering), C459 (anticipatory compensation)

**Quantitative:**
- B folios: 82
- Mean HT density: 0.310, std: 0.076
- Raw ACF significant lags: 1, 2, 4, 6, 20 (threshold=0.216)
- Peak: lag 1, r=0.378
- Section-residualized significant lags: 7 only
- Target range (lag 8-12): no significant signal
- Section boundaries: 7, quire boundaries: 8
