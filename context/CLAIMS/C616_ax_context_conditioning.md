# C616: AX Section/REGIME Conditioning

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** AX_BEHAVIORAL_UNPACKING

## Statement

Section affects AX transitions (V=0.081, p<0.001) and AX MIDDLE selection (V=0.227, p<0.001). REGIME affects AX transitions (V=0.082, p<0.001), with AX->EN varying from 24.5% (REGIME_2) to 39.1% (REGIME_1) per folio (Kruskal-Wallis p=0.0006). AX->FQ is also REGIME-dependent (p=0.003), refining C602's REGIME-independence claim for this transition.

## Evidence

### Section-Stratified AX Transitions (Section 1)

| Section | N | CC | EN | FL | FQ | AX | UN |
|---------|---|----|----|----|----|----|----|
| B | 964 | 4.6% | 39.6% | 4.6% | 11.1% | 17.7% | 22.4% |
| C | 271 | 3.3% | 21.8% | 9.6% | 14.4% | 18.8% | 32.1% |
| H | 549 | 3.8% | 26.4% | 5.3% | 16.9% | 20.8% | 26.8% |
| S | 1533 | 2.0% | 32.0% | 4.4% | 13.0% | 18.1% | 30.5% |
| T | 85 | 3.5% | 27.1% | 5.9% | 8.2% | 20.0% | 35.3% |

Chi-squared: chi2=89.18, p<0.000001, dof=20, V=0.081

Section B has the highest AX->EN rate (39.6%) and lowest UN successor rate (22.4%). Section C has highest FL routing (9.6%).

Pairwise: B vs S chi2=38.85, p<0.0001; H vs S chi2=17.92, p=0.003.

### Section-Specific MIDDLE Selection (Section 2)

Chi-squared: chi2=739.65, p<0.000001, dof=108, V=0.227

The MIDDLE effect (V=0.227) is substantially stronger than the transition effect (V=0.081). Sections have characteristic AX MIDDLE profiles:

| MIDDLE | Section-enriched (>= 2x expected) |
|--------|-----------------------------------|
| dy | H (2.1x) |
| ch | T (3.4x) |
| aiin | C (2.8x) |
| o | C (2.0x), H (2.4x) |
| od | C (2.4x) |
| ar | C (2.1x) |
| k | C (3.2x) |

### AX-REGIME Interaction (Section 3)

Chi-squared (REGIME x next-role): chi2=68.43, p<0.000001, dof=15, V=0.082

AX->EN proportion per folio by REGIME (Kruskal-Wallis H=17.43, p=0.0006):

| REGIME | Mean AX->EN | Median | Folios |
|--------|-------------|--------|--------|
| REGIME_1 | 39.1% | 38.5% | 23 |
| REGIME_2 | 24.5% | 25.0% | 24 |
| REGIME_3 | 26.9% | 23.5% | 8 |
| REGIME_4 | 31.1% | 33.8% | 27 |

AX->FQ: Kruskal-Wallis H=14.13, p=0.0027 (REGIME-dependent).

### C602 Refinement

C602 established AX->FQ as REGIME-independent at the folio level. The current test (H=14.13, p=0.003) finds a significant REGIME effect using a per-folio proportion approach. This may reflect different methodologies or a genuine refinement: the scaffold's routing to FQ is partially REGIME-conditioned when measured at individual AX token granularity.

## Extends

- **C551**: Confirms section-level MIDDLE specialization extends to AX (not just EN/FQ)
- **C602**: Refines AX->FQ REGIME independence — effect exists at token level (p=0.003)

## Related

C551, C563, C572, C599, C602, C614

## Method

Chi-squared for section/REGIME x transition contingency tables. Kruskal-Wallis for per-folio AX->EN/FQ proportions by REGIME. Section-enrichment defined as >= 2x expected proportion.
