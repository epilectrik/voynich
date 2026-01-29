# C649: EN-Exclusive MIDDLE Deterministic Lane Partition

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

EN-exclusive MIDDLEs partition deterministically by lane: 22/30 testable MIDDLEs show 100% lane assignment (13 QO-only, 9 CHSH-only, FDR < 0.05). k/t/p-initial MIDDLEs are exclusively QO; e/o-initial MIDDLEs are exclusively CHSH. This is absolute, not probabilistic.

## Evidence

- 30 EN-exclusive MIDDLEs (C578), 22 testable (n >= 10)
- Base QO rate: 44.7% (3,192/7,140 EN tokens)
- All 22 significant MIDDLEs show 100% concentration (zero crossover):
  - **QO-only (13):** ka, kai, kc, kch, ke, kec, keed, keeo, keo, pch, tc, tch, te
  - **CHSH-only (9):** ct, eck, ect, eek, ek, eod, et, ok, ot
- Morphological rule: initial character predicts lane (k/t/p -> QO, e/o -> CHSH)
- Aggregate: 784 QO vs 411 CHSH exclusive-MIDDLE tokens (65.6% QO, p < 1e-6)
- Benjamini-Hochberg FDR < 0.05 for all 22

## Interpretation

The QO/CHSH bifurcation within EN (C574, C576) is not a soft probabilistic tendency but a hard lexical boundary for the exclusive vocabulary. The morphological basis (initial character predicts lane) indicates this partition is built into the token construction layer (C522), where character-level composition rules deterministically assign MIDDLEs to one lane or the other.

## Cross-References

- C576: EN vocabulary bifurcation (Jaccard=0.133) -- C649 confirms deterministic extreme
- C578: 30 EN-exclusive MIDDLEs -- tested here
- C647: Morphological lane signature (V=0.654) -- C649 confirms absolute for exclusive vocabulary
- C574: EN distributional convergence (QO/CHSH grammatically identical but lexically partitioned)
- C522: Construction-execution independence

## Provenance

LANE_FUNCTIONAL_PROFILING, Script 1 (lane_monitoring_correlates.py), Bonus test
