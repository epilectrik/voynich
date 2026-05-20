# PHASE_718: Theophilus 8D Matcher Negative-Control Test

**Status:** COMPLETE
**Date:** 2026-05-20
**Verdict:** **NEGATIVE CONTROL FAILED** — matcher is generic, not alchemy-specific.

**Headline result:** Pre-registered test from 2026-05-14, never previously run, executed today. Script's own verdict: "OVERALL VERDICT: FAIL — matcher is generic; demote C1882-C1956 to structural-similarity." Both experts consulted and converged.

**Posture:** The project's pre-registered negative-control test per `sources/theophilus/README.md`. Apply the same 8D matcher methodology used in C1971 (Codicillus chapters → Voynich folios) to Theophilus chapters → Voynich folios. If Theophilus produces confident matches at rates indistinguishable from Codicillus (the positive corpus), the "operational correspondence" reading weakens to "structural attraction to medieval procedural text generally."

---

## Pre-registered failure criteria (from README, dated 2026-05-14)

> Per expert-advisor + crazy-expert convergence:
> - ≤2/30 confident matches (ratio ≥ 1.15) expected
> - Mean ratio ≤ 1.10
> - Permutation p ≥ 0.10
> - Matches should NOT concentrate on the Section B alchemy folios already matched to PL

If any of these criteria fail, demote C1882-C1956 from "operational correspondence" to "structural attraction to medieval procedural text."

---

## Methodology

1. **Segment Theophilus** into chapter-units using English CHAPTER markers from Books I, II, III (~167 chapters total per README)

2. **Extract 4-channel features** per chapter using the same keyword-based featurization as Codicillus (`sources/codicillus/_featurize_codicillus.py`):
   - k_channel: heat_rate, mean_heat_intensity, heat_transition_rate
   - h_channel: monitoring_rate, color_frac, consistency_frac, volatility_frac
   - t_channel: termination_rate, threshold_frac
   - e_channel: correction_rate, recoverable_frac, process_drift_frac

3. **Apply 8D matcher** using the locked TUNED_DIMS from `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/shared_628.py`

4. **Match against Voynich Currier B folios** with ratio-based confidence scoring

5. **Compare to pre-registered criteria**

---

## Why Theophilus is the right negative control

Theophilus *De Diversis Artibus* (~1120 CE):
- Same era and language family as Voynich (Latin, medieval)
- Same document type (technical procedural manual)
- DIFFERENT domain (metalwork/glass/pigments vs alchemy/distillation)

Both share operational vocabulary (heat, vessel, transfer, monitor, iterate) but Theophilus is NOT alchemy. If the 8D matcher is specifically detecting alchemy/distillation correspondence (positive interpretation), Theophilus should NOT match Voynich confidently. If the matcher is detecting any medieval procedural text (null interpretation), Theophilus should match similarly to Codicillus.

---

## Outcome interpretation (pre-registered)

| Outcome | Verdict for C1971/C1882-C1956 |
|---|---|
| All 4 failure criteria met | **NEGATIVE CONTROL PASSED** — matcher specifically detects alchemy/distillation; C1971 operational reading stands |
| 1-2 criteria fail | **PARTIAL** — matcher has alchemy-bias but isn't fully specific |
| 3-4 criteria fail | **NEGATIVE CONTROL FAILED** — matcher is detecting "any medieval procedural text"; demote C1971's operational reading to "structural attraction" |

---

## Implementation plan

| Script | Purpose |
|---|---|
| `_featurize_theophilus.py` | Segment Theophilus, extract 4-channel features per chapter (mirrors Codicillus featurization) |
| `_theophilus_8d_matcher.py` | Apply 8D matcher with Theophilus features → Voynich folios; report ratio statistics + pre-registered criteria check |

---

## Effort estimate

- Featurization: ~2 hours (segment 167 chapters + apply keyword extraction)
- Matcher: ~1 hour (reuse shared_628 infrastructure)
- Total: ~3 hours implementation, ~5 min runtime

---

## Registration-trap audit

- Pre-registered failure criteria locked since 2026-05-14 (README documented)
- Negative control by design — matcher should NOT match Theophilus
- If matcher DOES match Theophilus, that's the load-bearing failure mode
- Methodology mirrors C1971's Codicillus matcher exactly (apples-to-apples)

---

## RESULTS (2026-05-20)

### Pre-registered criteria

| Criterion | Threshold | Observed | Verdict |
|---|---|---:|---|
| C1: confident matches ≤2/30 | PASS ≤7%, FAIL ≥17% | 4/30 (13.3%) | AMBIGUOUS |
| C2: mean ratio ≤ 1.10 | failure if ≥1.20 | 0.878 | PASS |
| C3: permutation p ≥ 0.10 | failure if p<0.10 | **0.0000** | **FAIL** |
| C4: Section B concentration <40% | failure if ≥40% | **53.3%** | **FAIL** |

Script's overall verdict: "FAIL — matcher is generic; demote C1882-C1956 to structural-similarity"

### Theophilus chapters matching Voynich folios (T1 results)

30 Theophilus chapters → 32 REGIME_1 folios. Mean distance 2.72, mean ratio 0.878.

**Confident matches (ratio≥1.15):** 4/30
- B2.23 → f112r (ratio 1.71)
- B3.95 → f84r (ratio 1.33, ON original PL match list)
- B3.61 → f77v (ratio 1.21, ON PL match list)
- B3.33 → f84v (ratio 1.15, ON PL match list)

**Section B concentration:** 16/30 Theophilus chapters (53.3%) land on Voynich folios that are also on the original Pseudo-Lull match list — including f84r, f77v, f75r, f76v, f76r, f81v, f75v, f77r, f81r, f80v, f83r, f82r, f78r. **The matcher attracts both Theophilus AND Codicillus to the same Voynich folios.**

### Permutation test (T2)

- Real mean ratio: 0.878
- Random mean ratio: 0.612
- **p(ratio): 0.0000** — Theophilus matches Voynich significantly above random
- p(confident): 0.0000
- p(distance): 0.0000

The matcher is NOT producing null behavior on Theophilus. It's producing real structural attraction — just not alchemy-specific.

### Expert consultation

**Expert-advisor:** "This is a clean, pre-registered falsification. Acting on this is methodologically correct." Recommended NOT blanket-demote 75 constraints; apply triage criterion: **content-correspondence claims demote, structural-measurement claims survive**.

**Crazy-expert:** "This is the cleanest blow the operational reading has taken. Same folios, two completely different source corpora, same matcher — that's not specificity; that's a generic-medieval-procedural attractor pattern." Tier 0 survives. The operational reading survives at genre level (medieval craft procedure), dies at domain-specific level (alchemy).

### Both experts converge

1. **Tier 0 survives** — "closed-loop control programs" framing isn't tied to alchemy. Theophilus is also a closed-loop craft control text.
2. **C2042 atom-monocategorical signature survives** — atoms remain operationally-glossable.
3. **C2032 substrate quintet survives** — non-NL signature unaffected.
4. **C1971 family triage required** — NOT blanket demotion. Per-constraint reasoning needed.
5. **Triage criterion:** does the constraint claim CONTENT (e.g., "Ch19 = aqua vitae", specific PL→folio correspondence) or STRUCTURE (e.g., "d<1.0 alignment", "8D distance")? Content claims demote to Tier 3; structural claims survive at Tier 2.

### What this means

**The 8D matcher detects medieval procedural Latin structural attraction generally, not alchemy-specific operational correspondence.** Voynich folios attract Codicillus chapters AND Theophilus chapters at similar rates and to the same Section B folios. The substrate's "operational shape" is real at the genre level (medieval craft procedure manual) but the domain interpretation (alchemy/distillation specifically) is NOT supported by the matcher.

### Registered constraint

**C2052 (Tier 2 negative measurement):** PHASE_718 Theophilus 8D matcher negative control FAILS pre-registered criteria. Matcher is generic — detects medieval procedural Latin structural attraction, not alchemy-specifically. Implication: scope-refine C1971 + C1882-C1956 family from "alchemy-specific operational correspondence" to "structural attraction to medieval procedural text generally." Per-constraint audit queued as future phase.

### What does NOT change
- Tier 0 ("closed-loop control programs")
- C2042 (atom-monocategorical signature)
- C2032 (substrate quintet)
- Structural-measurement-level constraints in C1882-C1956 family

### What needs per-constraint audit (FUTURE PHASE)

C1971 + C1882-C1956 constraints that explicitly claim:
- Specific PL chapter → Voynich folio content correspondence (likely demote)
- Specific recipe content interpretation (likely demote)
- Mercuriorum book-level mapping (likely demote)
vs. constraints that claim:
- Structural alignment / 8D distance measurement (likely survive)
- 8D feature space geometry findings (likely survive)
- Cross-family replication of signature (likely survive — Theophilus actually CONFIRMS broader signature)

### Pattern this confirms

Four failed mechanism interpretations in this session (PHASE_711 parametric, PHASE_716 line-spanning, mode coherence, now alchemy-specificity) + cumulative audit pattern = **the "operational-specificity death zone" is real**. Mechanism interpretations at the "encodes X domain" level reliably die under discriminating tests. Structural measurements survive.

The operational reading at GENRE level (medieval craft procedure) survives. The DOMAIN-specific reading (alchemy/distillation) does NOT. C171's semantic ceiling re-confirmed at the matcher level.
