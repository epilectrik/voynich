# FL_PRIMITIVE_ARCHITECTURE

**Phase Status:** COMPLETE
**Constraints:** C770-C781
**Prior Phase:** COMPOUND_MIDDLE_ARCHITECTURE (C766-C769)

## Objective

Investigate why FL (Flow Operator) role shows 0% compound rate and 0 kernel characters. Determine if FL represents a primitive substrate layer in the grammar.

## Background

From COMPOUND_MIDDLE_ARCHITECTURE, we discovered:
- FL has 0% compound MIDDLEs (vs FQ 46.7%)
- FL uses 0 kernel characters (k, h, e)
- This motivated a deep dive into FL's architecture

## Key Findings

### T1: FL Inventory (C770, C771)

FL is constrained to a minimal character set:

**Characters Used (9):** a, d, i, l, m, n, o, r, y

**Characters Excluded (6):**
- Kernel: k, h, e
- Helper: c, s, t

**MIDDLE Inventory (17 types):**
```
al, am, ar, dy, i, ii, im, in, l, ly, m, n, o, ol, r, ry, y
```

**Morphological Profile:**
- Mean MIDDLE length: 1.58 chars (short)
- 93.8% suffix-free
- 40.3% prefix-free

### T2: FL Behavior (C773)

FL shows distinct hazard/safe positional profiles:

| Category | Classes | Tokens | % of FL | Mean Position |
|----------|---------|--------|---------|---------------|
| Hazard   | 7, 30   | 956    | 88.7%   | 0.546 (medial) |
| Safe     | 38, 40  | 122    | 11.3%   | 0.811 (final) |

**Positional Difference:** Safe FL is 0.265 (26.5% of line) later than hazard FL.

**Transitions:**
- FL -> UN: 28.8%
- FL -> EN: 25.1%
- FL -> FQ: 16.0%
- FL -> FL: 9.9% (self-chaining)

### T3: FL Primitive Substrate (C772)

FL provides the base layer for the grammar's character architecture:

```
LAYER 0: FL SUBSTRATE
  Characters: {a, d, i, l, m, n, o, r, y}
  Kernel chars: 0
  Function: Pure material flow

LAYER 1: KERNEL-MODULATED
  Characters: FL + {k, h, e}
  Function: Energy/phase/stability modulation
  Primary role: EN (60.7% kernel-containing)

LAYER 2: FULL GRAMMAR
  Characters: FL + kernel + {c, s, t}
  Function: Complete vocabulary with helper modulation
  All roles except FL
```

**Kernel Distribution by Role:**
| Role | Kernel Rate | Description |
|------|-------------|-------------|
| FL   | 0.0%        | Pure substrate |
| FQ   | 29.0%       | Partial modulation |
| EN   | 60.7%       | Heavy modulation |
| CC   | 100.0%      | Full kernel |

### T4: FL Hazard Relationship (C774-C776)

FL is outside the hazard topology and drives escape transitions:

**Forbidden Pair Absence:**
- FL classes (7, 30, 38, 40) not in ANY of the 17 forbidden pairs
- FL operates below the hazard layer

**Hazard FL -> FQ Escape:**
| FL Class | Category | FL->FQ Count | % of FL->FQ |
|----------|----------|--------------|-------------|
| 7        | HAZARD   | 71           | 49.7%       |
| 30       | HAZARD   | 69           | 48.3%       |
| 38       | SAFE     | 3            | 2.1%        |
| 40       | SAFE     | 0            | 0.0%        |

Hazard FL drives 98% of FL->FQ transitions. FL->FQ rate is 22.5%.

**Post-FL Kernel Enrichment:**
- 59.4% of post-FL tokens have kernel characters (k, h, e)
- Confirms FL -> kernel-modulated flow pattern

### T5: FL State Index (C777)

FL MIDDLEs function as state indices marking material progression:

**FL MIDDLE Positional Gradient:**
| MIDDLE | Position | Stage |
|--------|----------|-------|
| 'i'    | 0.35     | INITIAL |
| 'in'   | 0.42     | EARLY |
| 'r'    | 0.51     | MEDIAL |
| 'ar'   | 0.55     | MEDIAL |
| 'al'   | 0.61     | LATE |
| 'l'    | 0.62     | LATE |
| 'ly'   | 0.79     | FINAL |
| 'm'    | 0.86     | TERMINAL |
| 'y'    | 0.94     | TERMINAL |

**Key Metrics:**
- Position range: 0.64 (64% of line span)
- Self-transition rate: 23% (state changes 77% of the time)
- Character split: 'i' = early, 'y' = late

### T6: EN Kernel Profile (C778, C779)

EN is the phase/stability operator that guides material through FL states:

**EN Kernel Signature:**
| Signature | % |
|-----------|---|
| h+e       | 35.8% |
| k         | 14.6% |
| k+e       | 14.3% |
| h         | 13.9% |

**Kernel Character Rates:**
- h (phase): 59.4%
- e (stability): 58.3%
- k (energy): 38.6%

**EN-FL State Coupling:**
| FL State | EN 'h' rate |
|----------|-------------|
| EARLY    | 95.1%       |
| MEDIAL   | 89.3%       |
| LATE     | 76.9%       |

Early FL states require heavy phase management (h=95%); late states need less (h=77%).

### T7: Role Kernel Taxonomy (C780, C781)

Complete kernel profile for all 5 roles:

| Role | Kernel% | k | h | e | Dominant | Forbidden Pairs |
|------|---------|---|---|---|----------|-----------------|
| FL   | 0%      | 0% | 0% | 0% | none | 0 |
| CC   | 25%     | 17% | 8% | 19% | none | 20 |
| EN   | 92%     | 39% | 59% | 58% | h+e | 4 |
| FQ   | 46%     | 33% | **0%** | 26% | k+e | 10 |
| AX   | 57%     | 30% | 26% | 38% | balanced | 0 |

**Critical Finding:** FQ has exactly 0% 'h' (phase). Escape routes bypass phase management entirely.

## Constraints Established

| # | Name | Summary |
|---|------|---------|
| C770 | FL Kernel Exclusion | FL uses 0 kernel chars; only role with complete exclusion |
| C771 | FL Character Restriction | FL uses exactly 9 chars; excludes c,e,h,k,s,t |
| C772 | FL Primitive Substrate | FL is base layer; kernel is additive modulation |
| C773 | FL Hazard-Safe Position Split | Hazard FL medial (0.546), safe FL final (0.811) |
| C774 | FL Outside Forbidden Topology | FL classes not in any of 17 forbidden pairs |
| C775 | Hazard FL Escape Driver | Hazard FL drives 98% of FL->FQ (escape) transitions |
| C776 | Post-FL Kernel Enrichment | 59.4% of post-FL tokens have kernel chars |
| C777 | FL State Index | FL MIDDLEs index material state; 'i'=start, 'y'=end; 0.64 position range |
| C778 | EN Kernel Profile | EN is h+e dominant (35.8%); phase/stability operator |
| C779 | EN-FL State Coupling | EN 'h' rate drops 95%->77% as FL advances early->late |
| C780 | Role Kernel Taxonomy | Roles partition kernel: FL=0%, EN=92% h+e, FQ=46% k+e, CC=25%, AX=57% |
| C781 | FQ Phase Bypass | FQ has 0% 'h'; escape routes bypass phase management |

## Architectural Implications

1. **Three-Layer Model:** Grammar has a layered character architecture
   - FL provides primitive substrate
   - Kernel (k,h,e) provides control modulation
   - Helpers (c,s,t) provide additional modulation

2. **Role Specialization:** Each role occupies a specific layer position
   - FL: Layer 0 only
   - FQ: Layers 0-1
   - EN/AX: Layers 0-2
   - CC: Requires kernel (Layer 1+)

3. **Positional Function:** FL hazard/safe split correlates with line position
   - Hazard FL drives mid-line flow
   - Safe FL terminates flow at line boundaries

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| t1_fl_inventory.py | FL character/MIDDLE census | t1_fl_inventory.json |
| t2_fl_behavior.py | FL transitions and positions | t2_fl_behavior.json |
| t3_fl_primitive_substrate.py | Cross-role character comparison | t3_fl_primitive_substrate.json |
| t4_fl_hazard_relationship.py | FL in hazard topology | t4_fl_hazard_relationship.json |
| t5_fl_index_test.py | FL as state index test | t5_fl_index_test.json |
| t6_en_kernel_profile.py | EN kernel profile analysis | t6_en_kernel_profile.json |
| t7_role_kernel_taxonomy.py | Complete role kernel profiles | t7_role_kernel_taxonomy.json |

## Dependencies

- CLASS_COSURVIVAL_TEST/results/class_token_map.json (49 classes)
- scripts/voynich.py (Transcript, Morphology)

## Next Steps

Potential follow-on investigations:
1. CC's low kernel but high forbidden-pair involvement
2. FQ escape mechanics (class 9 as primary target)
3. State transition grammar (allowed/forbidden FL state sequences)
