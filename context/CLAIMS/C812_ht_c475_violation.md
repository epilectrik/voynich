# C812: HT Novel MIDDLE Combinations

## Constraint

HT uses MIDDLE pair combinations at 11.19% rate that **never occur in classified-classified adjacencies**, despite both MIDDLEs existing in classified vocabulary. This is NOT a C475 forbidden pair violation (C742 shows 0.44% forbidden pair compliance), but demonstrates HT occupies a **distinct combinatorial space**.

Key findings:
- 11.19% of HT-HT transitions use "novel" pairs (both MIDDLEs in classified, pair not seen)
- Only 14.4% of HT-HT pairs are also seen in classified tokens
- 90.7% of HT MIDDLEs are exclusive to HT (not in classified vocabulary)

## Evidence

HT-HT transition analysis:
| Metric | Value |
|--------|-------|
| Total HT-HT MIDDLE transitions | 2,028 |
| Unique HT-HT pairs | 1,913 |
| Pairs also seen in classified | 293 (14.4%) |
| Novel pairs (potential) | 1,735 (85.6%) |
| Novel pairs with both MIDDLEs in classified | 227 (11.19%) |

HT MIDDLE vocabulary:
| Category | Count | Percentage |
|----------|-------|------------|
| Total MIDDLEs in HT-HT | 908 | 100% |
| HT-exclusive MIDDLEs | 824 | 90.7% |
| Shared with classified | 84 | 9.3% |

## Clarification: Not C475 Violation

**C742 shows HT obeys C475 forbidden pairs at 0.44%** (below 2% threshold). The 11.19% here measures something different:
- C475 forbidden pairs: Specific pairs that are structurally prohibited
- C812 novel pairs: Pairs that COULD occur but happen not to in classified

HT doesn't violate C475's forbidden rules - it simply uses different combinations than classified tokens, reflecting its distinct vocabulary and structural role.

## Interpretation

HT operates in a **separate combinatorial space** from classified tokens:
1. 90.7% of HT MIDDLEs don't appear in classified vocabulary at all
2. When HT uses shared MIDDLEs, it combines them differently (11.19% novel combinations)
3. But HT doesn't violate the actual forbidden pair rules (C742: 0.44%)

This supports HT as a structurally distinct layer that shares morphological building blocks but combines them independently.

## Provenance

- Phase: CONTROL_LOOP_SYNTHESIS
- Script: t3_ht_c475_compliance.py
- Related: C742 (HT C475 compliance), C475 (MIDDLE incompatibility)
- Note: Originally mis-titled as "C475 violation" - corrected to "novel combinations"

## Tier

2 (Validated Finding)
