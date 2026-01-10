# C457: HT Boundary Preference in Zodiac AZC

**Tier:** 2 | **Status:** CLOSED | **Scope:** HT / AZC

---

## Statement

In Zodiac AZC, HT tokens show **significant preference for sector (S) positions over radial (R) positions**:

| Family | Total Tokens | HT Tokens | HT Rate |
|--------|-------------|-----------|---------|
| R (radial/interior) | 1,840 | 542 | 29.5% |
| S (sector/boundary) | 1,112 | 442 | 39.7% |

**Difference:** 10.3 percentage points (S > R)

This supports the interpretation that HT marks **attention at phase boundaries** - operators write HT more during boundary/transition states than during stable interior states.

---

## Evidence

### Statistical Test

| Metric | Value |
|--------|-------|
| Chi-squared | 32.57 |
| P-value | < 0.0001 |
| Cramér's V | 0.105 |
| Sample size | 2,952 tokens |

**Effect size is MEANINGFUL** (V > 0.1).

### Detailed Breakdown

| Placement | Tokens | HT | HT Rate |
|-----------|--------|-----|---------|
| R1 | 777 | 238 | 30.6% |
| R2 | 676 | 192 | 28.4% |
| R3 | 375 | 106 | 28.3% |
| S1 | 593 | 254 | **42.8%** |
| S2 | 469 | 169 | 36.0% |
| S3 | 17 | 13 | **76.5%** |

The S1 and S3 positions show notably elevated HT rates.

---

## What This Constraint Claims

- HT density is NOT uniform across AZC placements
- HT preferentially occurs at sector (boundary) positions
- This is consistent with "attention at phase boundaries" interpretation
- The effect is statistically significant and practically meaningful

---

## What This Constraint Does NOT Claim

- HT is exclusively at boundaries (R positions still have 29.5% HT)
- The mechanism for this preference (could be attention, could be timing)
- Extension to non-Zodiac AZC (only tested on 12 Zodiac folios)

---

## Architectural Interpretation

This finding connects:
- **C456** (interleaved R-S spiral) - the topological structure
- **C457** (HT boundary preference) - how HT anchors to that structure

The R-S alternation represents:
- **R (Radial):** Interior/stable states - lower HT (29.5%)
- **S (Sector):** Boundary/transition states - higher HT (39.7%)

**Interpretation:** Operators write more practice text (HT) during phase transitions, possibly because:
1. Transition phases require waiting/watching
2. Boundary positions are cognitively more salient
3. Attention naturally peaks at state changes

This reinforces the "cognitive scaffold" interpretation of AZC - the spiral topology isn't just structural, it correlates with human attentional patterns.

---

## Relationship to Other Constraints

| Constraint | Relationship |
|------------|--------------|
| **C456** | C457 extends: spiral topology has HT correlates |
| **C450** | C457 refines: within-quire clustering has positional substructure |
| **C209** | C457 supports: HT as attentional pacing mechanism |
| **C454** | C457 is independent: HT-AZC coupling exists, AZC-B coupling doesn't |

---

## Phase Documentation

Research conducted: 2026-01-10 (HT-AZC placement affinity test)

Scripts:
- `phases/exploration/ht_azc_placement_test.py`

Results:
- `results/ht_azc_placement_affinity.json`

---

## Test Completion Note

Per the approved plan, this was the SINGLE focused test for HT-AZC exploration.

**Outcome:** Significant finding documented.
**Status:** Investigation CLOSED.

---

## Navigation

<- [INDEX.md](INDEX.md) | ^ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
