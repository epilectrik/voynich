# A→AZC→B Pipeline Implementation Report

**Date:** 2026-01-17
**Purpose:** Expert review of implementation logic
**Status:** Request for validation

---

## Overview

This report traces the exact logic flow of the Constraint Flow Visualizer's A→AZC→B pipeline implementation. Each step includes the relevant code location and constraint references.

---

## STEP 1: Token Decomposition (morphology.py)

**Input:** Raw EVA token string (e.g., "chedy")
**Output:** MorphologyResult with PREFIX, MIDDLE, SUFFIX

### Logic:

```
1. Check if token is infrastructure minimal form (ol, ar, al, etc.)
   → If yes: Return as infrastructure token (no MIDDLE)

2. Extract PREFIX (2-3 chars from start)
   → Must be in MARKER_FAMILIES: {ch, sh, ok, ot, da, qo, ol, ct}
   → Extended prefixes (kch, sch, etc.) map to base family
   → If no valid prefix: Return invalid

3. Extract SUFFIX (longest match from end)
   → Check against A_UNIVERSAL_SUFFIXES: {ol, or, y, aiin, ar, chy, ...}

4. Extract MIDDLE (everything between PREFIX and SUFFIX)
   → This is the PRIMARY DISCRIMINATOR for AZC legality (C472)
```

**Example:**
```
"chedy" → PREFIX=ch, MIDDLE=ed, SUFFIX=y
"qokaiin" → PREFIX=qo, MIDDLE=k, SUFFIX=aiin
"ol" → Infrastructure (no MIDDLE)
```

**Constraint compliance:** C240 (8 marker families), C267 (morphological composition), C269 (universal suffixes)

---

## STEP 2: Bundle Computation (constraint_bundle.py)

**Input:** ARecord with multiple tokens
**Output:** ConstraintBundle with aggregated MIDDLEs

### Logic:

```
1. For each token in record:
   → Decompose via morphology.py
   → Extract MIDDLE (if present)

2. Aggregate into record-level bundle:
   → bundle.middles = UNION of all token MIDDLEs
   → bundle.prefix_families = UNION of all PREFIX families

3. The MIDDLE SET is what gets projected through AZC
```

**Example:**
```
Record "f1r.12" with tokens: [oksho, kshoy, otairin, ...]
→ Individual MIDDLEs: [sho, cho, air, ...]
→ Bundle.middles = {sho, cho, air, e, i, od, ...}
```

**Constraint compliance:** C233 (LINE_ATOMIC), C473 (A entry = constraint bundle), C481 (survivor-set uniqueness)

---

## STEP 3: AZC Folio Compatibility Check (reachability_engine.py:385-417)

**Input:** ConstraintBundle with MIDDLEs
**Output:** List of compatible AZC folios

### Logic:

```python
# Step 3a: Classify bundle MIDDLEs
restricted_bundle_middles = {
    m for m in bundle_middles
    if 1 <= data_store.middle_folio_spread.get(m, 0) <= 3
}

# Classification:
#   spread = 0: UNKNOWN (not in AZC vocab) → cannot forbid
#   spread 1-3: RESTRICTED → CAN forbid compatibility
#   spread 4+: UNIVERSAL → cannot forbid compatibility

# Step 3b: Check each AZC folio
for folio_id, projection in projection_summary.results.items():
    folio_vocab = data_store.azc_folio_middles.get(folio_id, set())

    # Compatibility FAILS only if a RESTRICTED MIDDLE is absent
    missing_restricted = restricted_bundle_middles - folio_vocab
    if not missing_restricted:
        compatible_folios.append((folio_id, projection))
```

**Key insight:** Universal MIDDLEs (4+ folios) and Unknown MIDDLEs (0 folios) CANNOT forbid compatibility. Only Restricted MIDDLEs (1-3 folios) can disqualify a folio.

**Constraint compliance:** C442 (compatibility filter), C470 (restricted vs universal), C472 (77% in 1 folio)

---

## STEP 4: Vocabulary Union (reachability_engine.py:442-453)

**Input:** List of compatible AZC folios
**Output:** effective_middles (UNION of all folio vocabularies)

### Logic (CORRECTED 2026-01-17):

```python
# Per expert correction: Use UNION, not intersection
# AZC folios are ALTERNATIVE legality postures, not conjunctive constraints.
# Intersection artificially over-restricts (C437: Jaccard ≈ 0.056).
effective_middles = set()
for folio_id, projection in compatible_folios:
    folio_vocab = data_store.azc_folio_middles.get(folio_id, set())
    effective_middles |= folio_vocab  # UNION of vocabularies
```

**Key insight:** AZC folios are ALTERNATIVE legality postures, not combined constraints. The effective vocabulary is the UNION of all compatible folio vocabularies. Zone legality then subtracts from this union (preserving subtractive semantics).

**Why INTERSECTION was wrong:**
- C437 says folios have 5.6% Jaccard overlap (maximally orthogonal by design)
- Intersecting orthogonal vocabularies produces near-empty sets
- This created artificial over-restriction

**Constraint compliance:** C437 (orthogonal folios), C440 (uniform B sourcing), C442 (exception-based filter)

---

## STEP 5: Zone Legality Application (reachability_engine.py:459-484)

**Input:** effective_middles, zone (C, P, R1, R2, R3, S)
**Output:** zone_legal_middles for each zone

### Logic:

```python
for zone in ZONES:  # ['C', 'P', 'R1', 'R2', 'R3', 'S']
    legality_zone = _get_consolidated_zone(zone)  # R1/R2/R3 → 'R'

    zone_legal_middles = set()
    for middle in effective_middles:
        # Default: ALL_ZONES (legal everywhere) if no explicit restriction
        legal_zones = data_store.middle_zone_legality.get(middle, ALL_ZONES)
        if legality_zone in legal_zones:
            zone_legal_middles.add(middle)
```

**Key insight:**
- MIDDLEs with explicit zone restrictions become illegal in certain zones
- MIDDLEs WITHOUT zone data default to ALL_ZONES (legal everywhere)
- Later zones (R, S) have fewer legal MIDDLEs (monotonic restriction)

**Constraint compliance:** C313 (position constrains legality), C443 (positional escape gradient)

---

## STEP 6: Class Reachability Computation (azc_projection.py:226-270)

**Input:** zone_legal_middles for a specific zone
**Output:** Set of reachable instruction classes (subset of 1-49)

### Logic:

```python
reachable = set(range(1, 50))  # Start with all 49 classes

for class_id in list(reachable):
    class_obj = data_store.classes.get(class_id)

    # CATEGORY 1: Kernel classes - NEVER pruned
    if class_id in data_store.kernel_classes:
        continue  # Always reachable (31 classes in all B folios)

    class_middles = class_obj.middles
    if not class_middles:
        # CATEGORY 2: Atomic class (no MIDDLEs) - always reachable
        continue

    # Filter out empty string MIDDLEs
    effective_class_middles = {m for m in class_middles if m}

    if not effective_class_middles:
        continue  # No specific MIDDLE requirement

    # CATEGORY 3: Decomposable class - pruned if NO MIDDLEs available
    if not (effective_class_middles & available_middles):
        reachable.discard(class_id)
```

**Three categories:**
| Category | Description | Prunable? |
|----------|-------------|-----------|
| Kernel (31 classes) | In ALL B folios | NEVER |
| Atomic (e.g., 7, 9, 23) | No MIDDLE components | NEVER |
| Decomposable (e.g., 8, 11, 30, 31, 33, 41) | Has MIDDLEs | YES, if all MIDDLEs unavailable |

**Constraint compliance:** C085 (kernel operators), C089 (load-bearing), hazard class taxonomy (v2.56)

---

## STEP 7: B Folio Classification (reachability_engine.py:302-357)

**Input:** grammar_by_zone (reachable classes per zone), B folio
**Output:** FolioReachability (REACHABLE / CONDITIONAL / UNREACHABLE)

### Logic:

```python
# Get classes required by this B folio (from corpus)
required = data_store.b_folio_class_footprints.get(folio, set())

# Check which zones have ALL required classes
reachable_zones = []
for zone in ZONES:
    gs = grammar_by_zone.get(zone)
    if gs and required <= gs.reachable_classes:
        reachable_zones.append(zone)

# Classification
if len(reachable_zones) == len(ZONES):
    status = REACHABLE      # All zones OK
elif len(reachable_zones) > 0:
    status = CONDITIONAL    # Some zones OK
else:
    status = UNREACHABLE    # No zones OK
```

**Key insight:** A B folio is REACHABLE if ALL its required classes are reachable in ALL zones. CONDITIONAL means it's only reachable in early zones (before classes get pruned).

**Constraint compliance:** C468-C470 (causal transfer), B folio class footprints (from corpus)

---

## DATA FLOW SUMMARY

```
User selects A record (e.g., "f1r.12")
    ↓
STEP 1: Decompose each token → Extract MIDDLEs
    ↓
STEP 2: Aggregate → bundle.middles = {sho, e, i, od, air}
    ↓
STEP 3: Classify MIDDLEs:
    - restricted (spread 1-3): {sho}
    - universal (spread 4+): {e, i, od, air}
    - unknown (spread 0): {}
    ↓
STEP 4: Find compatible AZC folios
    - Check: restricted_middles ⊆ folio_vocab?
    - Result: [f72v3] (1 compatible folio)
    ↓
STEP 5: Compute effective_middles = ⋃ folio_vocabs (UNION, not intersection)
    ↓
STEP 6: For each zone, apply zone legality:
    - Zone C: 48 MIDDLEs legal → 48 classes reachable
    - Zone P: 45 MIDDLEs legal → 45 classes reachable
    - Zone R: 40 MIDDLEs legal → 42 classes reachable
    - Zone S: 35 MIDDLEs legal → 39 classes reachable
    ↓
STEP 7: Classify each B folio:
    - Check: required_classes ⊆ reachable_classes?
    - f103r: REACHABLE (all zones OK)
    - f104v: CONDITIONAL (only C, P zones OK)
    - f105r: UNREACHABLE (requires pruned classes)
```

---

## CURRENT STATUS (Updated 2026-01-17)

### Fixed: Step 4 Vocabulary Aggregation

**Problem:** Intersection of folio vocabularies artificially over-restricted.
**Fix:** Changed to UNION. AZC folios are alternative postures.

### Explained: Type-Token Frequency Inversion

**Observation:** 62.8% of A records have NO restricted MIDDLEs
- 68.3% of MIDDLE occurrences are universal (spread ≥4)
- 16.7% are unknown (spread=0, not in AZC vocab)
- Only 15% are restricted (spread 1-3)

**Resolution (per expert):** This is EXPECTED behavior.
- C472 measures MIDDLE TYPES (77% restricted) ✓
- A records USE mostly universal MIDDLEs (hub MIDDLEs like 'a', 'o', 'e')
- This is type-token frequency inversion, not a bug

### AZC Compatibility Distribution (Unchanged)

| Category | Count | Percentage |
|----------|-------|------------|
| 0 compatible folios | 117 | 7.6% |
| 1 compatible folio | 188 | 12.3% |
| 2 compatible folios | 186 | 12.1% |
| 3+ compatible folios | 1042 | 68% |

**Note:** Expert clarified that "60-70% with 1 compatible" applies conditionally to A entries with restricted MIDDLEs, not globally.

### B Reachability After Fix

| Status | Records | Percentage |
|--------|---------|------------|
| Has REACHABLE B folios | 1225 | 79.9% |
| Only CONDITIONAL B folios | 80 | 5.2% |
| All UNREACHABLE B folios | 228 | 14.9% |

---

## QUESTIONS FOR EXPERT (Updated 2026-01-17)

### Answered by Expert

1. **MIDDLE extraction consistency:** ✅ YES - A and AZC must use identical logic (mandatory).

2. **Unknown MIDDLEs (spread=0):** ✅ YES - Non-restrictive is correct. They represent A-exclusive discriminators.

3. **Universal threshold:** ✅ YES - spread≥4 is correct. Do NOT tune this (avoids semantic leakage).

4. **Vocabulary intersection:** ✅ ANSWERED - INTERSECTION was WRONG. Changed to UNION. AZC folios are alternative postures, not conjunctive constraints.

5. **Zone legality default:** ✅ YES - ALL_ZONES is correct and required.

### Remaining Questions

1. **B reachability distribution:** After UNION fix, 79.9% of A records have at least one REACHABLE B folio. Is this expected?

2. **Per-folio vs aggregated view:** Would Option A (per-folio evaluation) show better differentiation than Option B (union)?

---

## FILES REFERENCED

| File | Purpose |
|------|---------|
| `core/morphology.py` | Token decomposition (PREFIX/MIDDLE/SUFFIX) |
| `core/constraint_bundle.py` | Bundle computation from A records |
| `core/azc_projection.py` | Zone reachability, class computation |
| `core/reachability_engine.py` | Compatibility check, B folio classification |
| `core/data_loader.py` | Data loading, MIDDLE folio spread computation |

---

## CONSTRAINT REFERENCES

| Constraint | Role in Pipeline |
|------------|------------------|
| C240 | 8 marker families for PREFIX extraction |
| C267 | Morphological composition rules |
| C313 | Position constrains legality |
| C437 | 5.6% AZC folio overlap |
| C441-C442 | Vocabulary-activated constraints |
| C443 | Positional escape gradient |
| C468-C470 | Causal transfer A→AZC→B |
| C472 | 77% MIDDLEs in 1 folio |
| C473 | A entry = constraint bundle |
| C481 | Survivor-set uniqueness |

