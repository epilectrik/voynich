# C1217: Lane vs Non-Lane Atom Content Separation

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** ATOM_PROFILE_SYNTHESIS (Phase 433)
**Extends:** C605 (two-lane processing architecture), C1207 (atom correlation clusters)
**Relates to:** C908 (kernel family correlation), C911 (PREFIX-MIDDLE compatibility), C1001 (PREFIX dual encoding)

---

## Statement

QO/CHSH lane tokens and non-lane tokens carry fundamentally different MIDDLE atom content, constituting two interleaved information streams within lines. Lane tokens (QO + CHSH) carry ENERGY, STABILITY, and MONITORING atoms; non-lane tokens (VESSEL, INFRA, BARE) carry ITERATION atoms. The separation is categorical (p<0.002 by within-folio PREFIX shuffle, 0/500 exceeded).

### Axis-Level Separation

| Axis | Atoms | LANE fraction | NON-LANE fraction | Ratio | Assignment |
|------|-------|--------------|-------------------|-------|------------|
| ENERGY | k, l | 21.7% | 10.5% | 2.08 | LANE |
| STABILITY | e | 26.4% | 14.7% | 1.79 | LANE |
| MONITORING | c, h | 10.6% | 5.2% | 2.05 | LANE |
| FREE | t | 6.0% | 0.8% | 7.71 | LANE |
| ITERATION | a, i, n, r | 4.3% | 37.9% | 0.11 | NON-LANE |
| CLOSURE | d, y | 20.3% | 17.1% | 1.19 | neutral |
| STRUCTURAL | o, p | 9.2% | 10.6% | 0.87 | neutral |

### Strongest Individual Separations

| Atom | LANE% | NON-LANE% | Ratio | Notes |
|------|-------|-----------|-------|-------|
| t | 6.0% | 0.8% | 7.71 | Strongest LANE enrichment |
| k | 17.5% | 2.6% | 6.70 | Energy kernel |
| c | 6.5% | 2.5% | 2.56 | Monitoring operation |
| e | 26.4% | 14.7% | 1.79 | Stability/cooling |
| n | 0.3% | 7.0% | 0.04 | Strongest NON-LANE enrichment |
| i | 1.0% | 14.1% | 0.07 | Iteration counter |
| r | 1.0% | 6.5% | 0.16 | Iteration output |
| a | 2.1% | 10.4% | 0.20 | Iteration input |

### QO vs CHSH Internal Split

| Atom | QO fraction | CHSH fraction | Interpretation |
|------|------------|---------------|----------------|
| k | 38.0% | 7.3% | QO = heating operations |
| e | 15.2% | 32.0% | CHSH = cooling/stabilization |
| t | 12.1% | 3.1% | QO = volatilization |
| d | 3.6% | 13.1% | CHSH = sealing/closure |
| y | 1.0% | 15.0% | CHSH = closure outcomes |

### Population

| Class | PREFIX set | Tokens | MIDDLE chars |
|-------|-----------|--------|-------------|
| LANE | qo, ch, sh | 9,890 | 20,874 |
| NON-LANE | ok, ot, da, sa, bare, other | 13,206 | 30,093 |
| QO | qo | 4,069 | 6,923 |
| CHSH | ch, sh | 5,821 | 13,951 |

---

## Interpretation

Lines contain two interleaved information streams:

1. **Energy control stream** (QO/CHSH lane tokens): Encodes what energy mode is active -- heating (QO + k), cooling/monitoring (CHSH + e), volatilization (QO + t), sealing (CHSH + d/y). This is the operational control loop.

2. **Parametric metadata stream** (non-lane tokens): Encodes iteration parameters (a, i, n = begin/count/end), vessel references (o), stirring (r), measurement (m), and structural framing. These specify how many times, on what vessel, and when to release.

The two streams interleave within lines, with QO-CHSH tokens alternating between heat application and cooling/monitoring phases (visible at the individual token level), while non-lane tokens provide the iteration and structural metadata that parameterizes each phase.

CLOSURE (d, y) and STRUCTURAL (o, p) axes are approximately neutral between streams, appearing in both lane and non-lane contexts.

---

## Method

- 23,096 Currier B tokens with non-empty MIDDLEs
- Lane classification by PREFIX: QO = {qo}, CHSH = {ch, sh}, VESSEL = {ok, ot}, INFRA = {da, sa}, BARE = no prefix
- Character-level atom counting within MIDDLE strings
- Within-folio PREFIX shuffle permutation test: 500 iterations, shuffling PREFIX assignments across tokens within each folio
- Both ITERATION delta and k enrichment ratio exceeded in 0/500 shuffles (p<0.002)

**Script:** `phases/ATOM_PROFILE_SYNTHESIS/scripts/atom_profiles.py` (T1)
**Results:** `phases/ATOM_PROFILE_SYNTHESIS/results/atom_profiles.json`
