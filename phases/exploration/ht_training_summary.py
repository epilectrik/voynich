#!/usr/bin/env python3
"""
HT Training Hypothesis - Complete Summary

HYPOTHESIS: Currier A is where scribes were trained, explaining higher HT rates.

This script produces a complete summary of all findings.
"""

print("""
================================================================================
HT TRAINING HYPOTHESIS - COMPLETE ANALYSIS SUMMARY
================================================================================

HYPOTHESIS:
  Currier A is where scribes were trained, explaining higher HT rates
  (A: 6.46% HT vs B: 4.26% HT)

--------------------------------------------------------------------------------
PREDICTIONS TESTED:
--------------------------------------------------------------------------------

1. COMPLEXITY GRADIENT
   Prediction: Early A should have higher HT than late A (learning improvement)
   Result: NO GRADIENT DETECTED
   - Spearman rho = -0.004, p = 0.97 (essentially zero)
   - Early A: 7.62%, Middle A: 5.71%, Late A: 6.92%
   - No systematic decrease through A folios
   VERDICT: NOT SUPPORTED

2. SIMPLICITY CORRELATION
   Prediction: High-HT lines should be simpler (practice on easier material)
   Result: NO PATTERN
   - HT rate vs line length: rho = 0.044, p = 0.08 (not significant)
   - HT rate vs token length: rho = -0.095, p = 0.0002 (weak negative)
   VERDICT: NOT SUPPORTED

3. SCRIBE VARIATION
   Prediction: Different sections = different skill levels
   Result: SECTIONS DIFFER (but not as expected)
   - Chi-square p < 0.0001
   - But this reflects section FUNCTION, not skill level
   VERDICT: PARTIAL (not diagnostic)

4. REPETITION PATTERN
   Prediction: HT higher in repeated entries (practicing)
   Result: OPPOSITE PATTERN
   - HT is LOWER in high-repetition lines
   - rho = -0.078, p = 0.002
   - This suggests mastery, not practice
   VERDICT: CONTRADICTED

5. B GRADIENT COMPARISON
   Prediction: B should NOT show same gradient (production context)
   Result: B SHOWS STRONGER GRADIENT
   - B gradient: rho = -0.478, p < 0.0001
   - A gradient: rho = -0.004, p = 0.97
   - B's gradient is section-driven (early B = section H, late B = section S)
   VERDICT: CONTRADICTED

6. TOKEN DIVERSITY
   Prediction: HT-heavy text should have lower diversity
   Result: NO PATTERN
   - HT rate vs TTR: rho = 0.117, p = 0.22 (not significant)
   VERDICT: NOT SUPPORTED

--------------------------------------------------------------------------------
CRITICAL FINDING: SECTION COMPOSITION EFFECT
--------------------------------------------------------------------------------

The A>B HT difference is ENTIRELY explained by section composition:

Section Distribution:
- Currier A: 72% section H, 21% section P, 7% section T
- Currier B: 40% section S, 37% section B, 15% section H, 5% section C, 2% section T

Section HT Rates (in B):
- Section C: 9.82%
- Section H: 8.12%
- Section T: 7.76%
- Section S: 3.28%
- Section B: 2.76%

Within-Section Comparison (shared sections H and T):
- Section H: A = 6.87%, B = 8.12% -- B is HIGHER (p < 0.0001)
- Section T: A = 7.02%, B = 7.76% -- No significant difference

Decomposition:
- Actual A-B difference: +2.20%
- Due to section composition: +3.39%
- Intrinsic (within-section): -1.19%

>>> A has MORE HT than B only because A is dominated by section H
>>> Within the SAME sections, B actually has HIGHER HT than A

--------------------------------------------------------------------------------
FINAL VERDICT
--------------------------------------------------------------------------------

TRAINING HYPOTHESIS: **NOT SUPPORTED**

Evidence Against:
1. No learning gradient in A (prediction 1 failed)
2. B shows stronger gradient than A (prediction 5 failed)
3. Repetition correlates with LOWER HT, not higher (prediction 4 failed)
4. Within same sections, B has HIGHER HT than A (reverses premise)
5. A>B difference is entirely compositional

Evidence For:
- (None significant)

--------------------------------------------------------------------------------
ALTERNATIVE EXPLANATION
--------------------------------------------------------------------------------

The A>B HT difference reflects:

1. SECTION COMPOSITION
   - A is 72% section H (herbal), which has high HT in both systems
   - B has diverse sections including S and B (low HT)
   - The difference is an artifact of manuscript organization

2. FUNCTIONAL ARCHITECTURE
   - A = non-sequential categorical registry
   - B = sequential executable programs
   - HT (non-operational layer) may serve different roles in each

3. ESTABLISHED CONSTRAINTS (Context System):
   - C341: HT density varies by PROGRAM TYPE (not learning stage)
   - C342: HT is independent of LINK density (not "doodling during pauses")
   - C348: HT tracks procedural phase (systematic, not random)
   - C404-406: HT is non-operational (removing it doesn't affect grammar)

CONCLUSION:
The "training context" interpretation does not fit the data.
The A>B HT difference is a compositional artifact of section distribution,
not evidence of different scribe skill levels or learning contexts.

================================================================================
""")
