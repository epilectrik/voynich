# C1086: Bio Section Apparatus-Hazard Depletion

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** BIO_DOMAIN_DISTINCTIVENESS (Phase 385)
**Extends:** C109 (5 failure classes), C216 (hybrid hazard model: 71% batch, 29% apparatus)
**Strengthens:** C554 (hazard class clustering), C458 (design asymmetry)
**Relates to:** C601 (QO never participates in hazard events), C1085 (Bio kernel balance)

---

## Statement

Bio section has fewer apparatus-specific hazards (CONTAINMENT_TIMING + RATE_MISMATCH): 24.4% vs non-Bio 32.2% (Fisher exact OR=0.680, p<0.0001). This is compensated by elevated COMPOSITION_JUMP (36.3% vs 27.0%). Bio's hazard profile is shifted toward material-state failures and away from apparatus failures.

---

## Evidence

### Hazard Class Distribution

| Class | Bio | Bio% | Non-Bio | NB% |
|-------|-----|------|---------|-----|
| PHASE_ORDERING | 550 | 39.3% | 770 | 40.8% |
| COMPOSITION_JUMP | 508 | 36.3% | 510 | 27.0% |
| CONTAINMENT_TIMING | 276 | 19.7% | 422 | 22.4% |
| RATE_MISMATCH | 65 | 4.6% | 185 | 9.8% |
| ENERGY_OVERSHOOT | 0 | 0.0% | 0 | 0.0% |

Chi-square: 53.5, dof=3, p<0.0001.

### Apparatus-Specific Hazard Depletion

Apparatus hazards (CONTAINMENT_TIMING + RATE_MISMATCH):
- Bio: 341/1399 = 24.4%
- Non-Bio: 607/1887 = 32.2%
- Fisher exact: OR=0.680, p<0.0001

Bio shifts the hazard profile from C216's corpus-wide ratio (71% batch / 29% apparatus) to approximately 76% batch / 24% apparatus.

### Connection to QO Dominance

C601 establishes that QO never participates in hazard events. Bio's elevated QO CC trigger routing (44.8% vs 13.0%, T4) means Bio preferentially routes through the safe (QO) lane, mechanistically explaining the reduced apparatus hazard rate.

---

## Interpretation

Bio programs operate with less apparatus complexity — fewer containment and rate-mismatch failures suggest simpler equipment or more forgiving process conditions. At Tier 3, this is consistent with balneum mariae, where the water bath provides thermal inertia that prevents apparatus-specific failure modes (containment breaches, rate mismatches) while material-state transitions (composition jumps) remain relevant.

---

## Method

- Hazard-source tokens identified from forbidden transition pairs (C109)
- 5 hazard classes from C109 taxonomy
- Bio (n=20 folios) vs non-Bio (n=62 folios) comparison
- Chi-square for overall distribution, Fisher exact for apparatus-specific subset
- Pre-registered test with falsification criteria

**Script:** `phases/BIO_DOMAIN_DISTINCTIVENESS/scripts/bio_domain_tests.py`
**Results:** `phases/BIO_DOMAIN_DISTINCTIVENESS/results/bio_domain_results.json`

---

## Verdict

**BIO_APPARATUS_DEPLETED**: Bio section hazard profile is shifted toward material-state failures (COMPOSITION_JUMP elevated) and away from apparatus failures (CONTAINMENT_TIMING + RATE_MISMATCH depleted, OR=0.680), consistent with operationally simpler or more forgiving equipment.
