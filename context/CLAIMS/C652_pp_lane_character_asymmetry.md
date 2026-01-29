# C652: PP Lane Character Asymmetry

**Tier:** 2 | **Status:** CLOSED | **Scope:** GLOBAL

## Finding

PP vocabulary is strongly CHSH-biased by initial character: among 235 lane-predicting PP MIDDLEs, only 25.5% are QO-predicting (k/t/p-initial) vs 74.5% CHSH-predicting (e/o-initial) at type level (binomial p < 3e-14). At token level (B-frequency weighted), 31.3% QO (p < 1e-300). Material class does not modulate this bias (chi2=2.4, p=0.49). The PP vocabulary landscape is inherently CHSH-favoring.

## Evidence

- 404 PP MIDDLEs classified by C649 initial character rule
- Type-level: 60 QO-predicting, 175 CHSH-predicting, 169 neutral
- QO fraction of lane-predicting: 0.255 (type), 0.313 (token)
- Binomial test vs 0.5: p < 3.1e-14 (type), p < 1e-300 (token)
- By material class (type-level, lane-predicting only):
  - ANIMAL: 9 QO / 23 CHSH (28.1%)
  - HERB: 22 QO / 48 CHSH (31.4%)
  - MIXED: 7 QO / 27 CHSH (20.6%)
  - NEUTRAL: 22 QO / 77 CHSH (22.2%)
  - Material x Lane: chi2=2.40, p=0.49, V=0.101 (NS)
- Token-level tokens: 3962 QO, 8681 CHSH, 8999 neutral

## Interpretation

The PP vocabulary, which defines the shared type system between A and B (C498), carries an intrinsic CHSH bias at the character level. Since C649 shows initial character determines lane (k/t/p -> QO, e/o -> CHSH), the vocabulary available to B programs contains nearly 3x more CHSH-predicting types than QO-predicting types. Despite this, B programs achieve ~40.7% QO in EN lane balance (see C654), indicating that grammar-level selection compensates for vocabulary-level bias.

## Cross-References

- C649: EN-exclusive MIDDLE deterministic lane partition (initial character rule)
- C498: PP/RI bifurcation (404 PP MIDDLEs shared between A and B)
- C576: EN MIDDLE vocabulary bifurcation (QO=25, CHSH=43 MIDDLEs)
- C654: Non-EN PP does not predict lane balance

## Provenance

PP_LANE_PIPELINE, Script 1 (pp_lane_vocabulary_architecture.py), Test 1
