# C1248: Apparatus-Marker Co-occurrence Architecture

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** APPARATUS_VOCABULARY_CLASSIFICATION (Phase 445)
**Extends:** C179 (4 stable REGIMEs), C537 (token-level material differentiation)
**Relates to:** C1247 (aii R3 specificity), C1249 (section apparatus diversity), C1226 (ke/ek conditioning)

---

## Statement

Apparatus-relevant MIDDLEs co-occur in specific combinations at the folio level, forming operational cycle signatures. Two co-occurrence pairs are highly significant; the strongest inter-profile axis (DISTILLATION vs PRECISION) shows rho=-0.666.

### Significant co-occurrence pairs

| Pair | MIDDLEs | Both | A only | B only | Neither | OR | p |
|------|---------|------|--------|--------|---------|-----|---|
| drive+sustain | t + eol | 61 | 10 | 3 | 8 | 16.27 | 0.0001 |
| heat+overnight | ke + eeol | 23 | 38 | 0 | 21 | inf | 0.0003 |

**t + eol (drive off + sustain output):** 61/82 folios have both. If a program drives off volatiles, it sustains output during the process. This is the distillation cycle signature.

**ke + eeol (sustained heat + overnight standing):** Every folio with eeol also has ke — no exceptions (0 folios have eeol without ke). The sustained heat cycle always includes overnight standing as a phase.

### Non-significant pairs

seal+unseal (ok + aii) shows OR=0.94 (p=0.65): sealing and unsealing do NOT significantly co-occur. This means sealing (ok) and unsealing (aii) serve different programs or different phases, not a single seal→unseal cycle within the same folio.

### Inter-profile correlation

The DISTILLATION and PRECISION apparatus profiles are strongly anti-correlated at the folio level (Spearman rho=-0.666, p<0.0001). A folio that scores high on distillation vocabulary (t, od, te, eol) scores low on precision vocabulary (ek, s, m, ep), and vice versa. No other profile pair shows a correlation this strong.

DISTILLATION vs SEALED_VESSEL: rho=-0.254 (p=0.02) — moderate separation.

---

## REGIME alignment

REGIME predicts the dominant apparatus vocabulary profile with high accuracy for R1 and R3, but not for R2 and R4:

| REGIME | Dominant profile | % | Second profile | % |
|--------|-----------------|---|----------------|---|
| REGIME_1 | DISTILLATION | 97% (31/32) | SEALED_VESSEL | 3% (1/32) |
| REGIME_2 | SEALED_VESSEL | 60% (9/15) | DISTILLATION | 40% (6/15) |
| REGIME_3 | DISTILLATION | 95% (19/20) | SEALED_VESSEL | 5% (1/20) |
| REGIME_4 | DISTILLATION | 60% (9/15) | SEALED/SUSTAINED | 20%/20% |

R1 and R3 are single-apparatus REGIMEs. R2 and R4 mix apparatus types within the same fire degree — consistent with Brunschwig's description of applying the same temperature via different apparatus.

---

## R3 vs R1 vocabulary differentiation

The two distillation-dominant REGIMEs use systematically different vocabularies:

**R3-enriched (batch/open-cycle):** aii 41x, eo "cool-open" 7.6x, od "collect" 6.9x, eeo "monitored-cool" 4.8x, tch "pound" 5.1x

**R1-enriched (continuous/sustained):** ke "sustained heat" 3.2x, ck "direct heat" 2.7x, lk "L-compound energy" 4.3x, eck "extended-direct-heat" 3.8x

R3 programs include unsealing, collecting, and cooling-with-opening operations. R1 programs emphasize sustained energy management without interruption.

---

## Apparatus profile definitions

Five profiles scored per folio based on marker MIDDLE presence rates:

| Profile | Key markers (MIDDLEs) | Overall rate |
|---------|----------------------|-------------|
| DISTILLATION | t, od, te, eol + qo PREFIX | 20.1% |
| SEALED_VESSEL | aii, ok, ee, eey, eeol + ok PREFIX | 10.5% |
| SUSTAINED_HEAT | ke, eeo, eeol, ee + da PREFIX | 8.3% |
| PRECISION | ek, s, m, ep + kch/ct PREFIX | 3.4% |
| DIRECT_FIRE | ck, kc, te | 1.4% |

---

## Method

- 82 Currier B folios (H-track, ≥50 tokens)
- 5 apparatus profiles defined from Brunschwig-grounded MIDDLE glosses
- Per-folio scoring: (marker token count) / (total tokens)
- Co-occurrence: Fisher exact test (one-sided, greater)
- Profile correlations: Spearman across all 82 folios

**Script:** `phases/APPARATUS_VOCABULARY_CLASSIFICATION/scripts/apparatus_profiles.py`
**Results:** `phases/APPARATUS_VOCABULARY_CLASSIFICATION/results/apparatus_profiles.json`
