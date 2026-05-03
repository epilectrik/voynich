# Phase 675: Manuscript-Wide Layout-Ordering Test (Internal Proxy)

**Status:** COMPLETE (Tier 1 falsification)
**Started:** 2026-05-03
**Goal:** Test whether paragraph layout-position correlates with internal e-depth gradient across all Currier B folios with ≥4 paragraphs. Resolves an open question between C1399 (paragraph independence universal) and the prior empirical finding that paragraph layout-order tracks recipe-phase order at rho=+0.81 on 5 matched folios.

## Pre-Registration (Locked Before Running)

**Hypothesis:** Paragraph layout-position correlates with within-paragraph e-depth-mean (length-residualized) at Spearman |rho| > 0.4, with ≥60% same direction and p<0.001 majority.

**Procedural verdict:** |mean_rho| > 0.4 AND ≥60% same direction → procedural manuscript-wide. Tier 2 candidate.
**Null verdict:** |mean_rho| < 0.1 → matched-folio artifact. Tier 1 falsification candidate.
**Mixed verdict:** between extremes.

**Primary proxy:** e-depth-mean per paragraph (length-residualized via linear regression on paragraph token count).

## Phase 1 Results (Baseline)

| Stratum | N | Mean rho | % negative | Verdict |
|---------|---|----------|------------|---------|
| All | 46 | -0.174 | 70% | |rho|=0.367 < 0.4 — pre-reg threshold MISSED |
| H (Herbal) | 5 | -0.48 | 100% | clears 0.4 within section |
| B (Biological) | 13 | -0.27 | 77% | moderate |
| S (Stars/Pharm) | 23 | -0.04 | 52% | null |
| Cluster (Phase 642) | 8 | -0.29 | 87% | apparent thermal arc |
| Matched alchemical | 9 | -0.18 | 22% | weak |

**Pre-registered procedural threshold MISSED.** Mean |rho|=0.367 < 0.4. Verdict: MIXED.

**Sanity check FAILED:** Prior memory note "Test B 2026-04-25 mean rho=+0.81 across 5 matched folios" did not replicate (got -0.18 on 9 matched folios). Reason: prior Test B used external recipe-phase ordinal; Phase 675 uses internal e-depth gradient. Different proxies, different tests. Phase 675 is NOT a Test B replication — it is a parallel internal-proxy test.

## Expert Review

Both experts (expert-advisor and crazy-expert) flagged required falsifiers:

1. **Paragraph-1 ablation** (crazy-expert: "the trap"): C1287 establishes paragraph-headers are MARKING-enriched. Higher specification vocabulary → spuriously higher e-depth in paragraph 1, pulling all rho negative. Drop paragraph 1, recompute.
2. **H-section drop on cluster** (both): Cluster signal could be C939 leakage from H-section cluster folios.
3. **Section-mean residualization**: Could the gradient be the static "low-heat herbal" property?

Both experts also flagged **goalpost-shifting**: |rho|=0.367 < 0.4 IS a failed pre-reg, not a near-miss. Don't lean on the binomial directional consistency (70% same direction, p≈0.004) as a substitute success criterion.

## Phase 2 Results (Falsifiers)

### F1. Paragraph-1 Ablation (THE KILLER)

| Stratum | Baseline | After P1 drop | Effect |
|---------|----------|---------------|--------|
| All | -0.174 | **-0.100** | Mostly P1-driven |
| **H (Herbal)** | **-0.48** | **-0.10** | **COLLAPSED** |
| B (Biological) | -0.27 | -0.18 | Weakened, persists |
| S (Stars/Pharm) | -0.04 | -0.02 | Null (unchanged) |
| **Cluster** | **-0.29** | **-0.04** | **COLLAPSED** |
| Cluster non-H | -0.25 | -0.14 | Weakened |
| Matched | -0.18 | -0.17 | Persists |

**The "Herbal procedural arc" and "cluster procedural-not-reference" findings BOTH collapsed under P1 ablation.** C1287 prediction confirmed: paragraph-header MARKING-enrichment (specification vocabulary) inflated P1 e-depth, creating the apparent monotonic gradient.

### F2. Cluster Non-H Subset

Cluster non-H (n=6, after dropping f33r-f55v Herbal cluster folios): mean rho -0.25 baseline → -0.14 after P1 drop. Combined with P1 ablation, near-null. Cluster signal does NOT survive both falsifiers.

### F3. Section-Mean Residualization

No effect (the gradient was within-folio, not driven by static section means).

## Verdict

**Tier 1 falsification of the pre-registered hypothesis:**

- Pre-registered procedural threshold failed at baseline (|rho|=0.367 < 0.4)
- Section-conditional refinement collapsed under paragraph-1 ablation
- C1287 paragraph-header MARKING-enrichment is the dominant confound
- Cluster "procedural arc" finding is a paragraph-1 artifact, not a structural property

**What survives:**
- Biological-section weak negative gradient (mean rho -0.18 after P1 drop, n=13) — possibly real but small-sample
- Pharmaceutical/Stars no-gradient null (mean rho -0.02) — confirmed
- C1399 (paragraph independence universal) survives this test

**What does NOT survive:**
- "Herbal procedural thermal arc" hypothesis
- "Cluster is procedural, not reference" interpretation (Phase 674 question stays open at scope-limit)
- Manuscript-wide procedural arc via internal e-depth gradient

## Constraint Updates

### C1986 (Tier 1, falsification): Manuscript-wide procedural arc via internal e-depth gradient REJECTED

Pre-registered Phase 675 test: paragraph layout-position vs length-residualized e-depth-mean across 46 Currier B folios with ≥4 paragraphs. Pre-registered procedural threshold |mean_rho|>0.4 + ≥60% same direction failed (|rho|=0.367 mean, 70% same direction).

Section-conditional pattern (Herbal -0.48, Cluster -0.29) initially appeared promising but collapsed under paragraph-1 ablation (Herbal: -0.48 → -0.10; Cluster: -0.29 → -0.04). C1287 (paragraph-header MARKING-enrichment) explains the apparent gradient as paragraph-1 specification-vocabulary artifact, not a procedural thermal arc.

Surviving signals (after P1 ablation): only Biological section weak negative gradient (mean rho -0.18, n=13). Pharmaceutical/Stars and Cluster show no gradient. C1399 (paragraph independence universal) survives this test.

This rejects the strong-form hypothesis "Voynich paragraphs are sequential thermal-procedure steps with monotonic e-depth decay." Phase 668-669's paragraph-recipe ordering rho=+0.81 (external recipe-phase ordinal) is a different test — it measures ordinal correspondence between paragraph layout and recipe step, not internal thermal gradient.

**Tier:** 1 (Currier B, falsification of pre-registered hypothesis)

## Methodological Notes

1. **Pre-registration discipline saved this phase from registering an artifact.** The headline -0.48 Herbal effect would have looked like a clean Tier 2 finding without the P1 ablation falsifier.
2. **Crazy-expert called the P1 trap correctly.** "Paragraph-1 trap. Yes, this is the trap. Header/setup paragraphs (PSC: header enrichment, MARKING-heavy) plausibly carry higher e-depth via specification vocabulary, not thermal content. Mandatory test: drop paragraph 1, recompute mean rho. If it drops to |rho|<0.1, finding is a header artifact." It did exactly that.
3. **Failed sanity check is informative.** The -0.18 matched alchemical mean DID NOT reproduce the prior +0.81 because prior Test B used a different proxy (external recipe-phase ordinal vs internal e-depth gradient). The two findings are not in conflict; they measure different things.
4. **Phase 674 cluster question remains open.** This phase did not validate "cluster is procedural" — that interpretation collapsed. C1985 (Phase 674 scope-limit) still applies.

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| s1_layout_ordering_test.py | Baseline test on all 46 folios with ≥4 paragraphs | ~30s |
| s2_falsifiers.py | Three falsifiers (P1 ablation, H-drop, section-demean) | ~5s |

## Relationship to Existing Constraints

- **C1399** (paragraph independence universal): SURVIVES. Phase 675 cannot reject paragraph independence; the apparent within-folio gradient was a paragraph-1 artifact.
- **C1287** (paragraph-header MARKING-enrichment): VALIDATED as confound source. P1 ablation collapsed the apparent thermal-arc signal in 2 of 3 strata that initially showed it.
- **C1985** (Phase 642 cluster scope-limit): UNCHANGED. Phase 675 did not refine the cluster operational signature claim.
- **C939** (low-heat herbal section): NEUTRAL. F3 section-mean residualization had no effect, so the gradient was within-folio, not section-mean-driven.
- **C1325** (folio REGIME homogeneity): UNAFFECTED.

## Suggested Follow-Up

- **External recipe-phase ordinal replication** (true Test B): Replicate the prior +0.81 finding with full transparency on n, methodology, and proxy choice. The 5-folio sample may have been overstated. With 11 matched folios available, redo the test with explicit external recipe-step alignment.
- **Biological-section drill-down:** The B-section gradient (-0.18 after P1) is the only surviving signal. Test whether it's a real procedural thermal arc within Bio folios specifically, or another confound.
- **Different proxies:** e-depth was the primary proxy. Other internal proxies (kernel-fraction, monitoring-MIDDLE density, terminator-vs-bare ratio) might have different gradients. None are mandatory follow-ups; Phase 675 already showed that internal-proxy thermal gradients are not the right axis for procedural signal.
