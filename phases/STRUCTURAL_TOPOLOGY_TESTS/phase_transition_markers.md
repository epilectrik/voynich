# Test 3: Phase Transition Markers

**Question:** What grammatical features signal phase transitions at AZC position boundaries?

**Verdict:** STRONG_MARKERS_IDENTIFIED - Multiple grammatical markers signal phase transitions

---

## Background

### Historical Parallel

Brunschwig: "Mark well the signs of change, for what is done too soon or too late cannot be corrected."

**Test Question:** Does the Voynich grammar encode "signs" at phase transitions?

### Known AZC Transition Points

| Transition | Escape Rate Change | Interpretation |
|------------|-------------------|----------------|
| → P | Entry to active phase | 15.87% escape (high) |
| P → R | **Commitment point** | 9.23% → 5.3% → 0% |
| R → S | Late-stage decision | 4.36% escape (low) |

---

## Findings

### 1. HT Step Change at AZC Entry: The "Orientation Reset" Marker

**Source:** azc_entry_orientation_trace.json (C460)

| Metric | Value |
|--------|-------|
| Pre-AZC mean HT | +0.200 (elevated) |
| AZC entry HT | +0.005 (near-zero) |
| Post-AZC mean HT | -0.185 (suppressed) |
| **Step change** | **-0.385** |
| t-statistic | 7.13 |
| p-value | **< 1.2e-6** |

**Interpretation:** AZC entry is marked by a dramatic HT polarity reversal. This functions as an **orientation reset signal** - the system "resets" tracking behavior at phase boundaries.

### 2. R-Series Progressive Commitment: The Escape Gradient

**Source:** azc_escape_by_position.json (F-AZC-007, C443)

| Position | Escape Rate | Interpretation |
|----------|-------------|----------------|
| R1 | 5.30% | Early commitment |
| R2 | 1.84% | Deep commitment |
| R3 | **0.00%** | Complete prohibition |
| R4 | **0.00%** | Terminal |

**Pattern:** Escape rate decreases monotonically through R-series. Each R-position is a "commitment checkpoint" with progressively restricted options.

**This matches heads→hearts→tails:**
- Heads (P): 15.87% - can still adjust
- Hearts (R-series): 5.3% → 0% - committed
- Tails (S): 4.36% - decision point

### 3. LINK Distribution: Monitoring/Intervention Boundary Marker

**Source:** link_metrics.md, sensory_affordance_analysis.json (C366)

| Context | LINK Behavior |
|---------|---------------|
| **Preceding LINK** | AUXILIARY roles enriched 1.50x |
| **Following LINK** | HIGH_IMPACT roles enriched 2.70x |
| **Near escalation (k/h)** | LINK suppressed 0.605x |

**Interpretation:** LINK marks the boundary between:
- **Before LINK:** Monitoring/observation (AUXILIARY enriched)
- **After LINK:** Intervention/action (HIGH_IMPACT enriched)

This is a grammatical "sign" indicating transition from passive monitoring to active intervention.

### 4. Boundary Asymmetry: C vs S Position Signatures

**Source:** azc_boundary_asymmetry.json (F-AZC-008)

| Metric | C (Intake) | S (Release) | Difference |
|--------|------------|-------------|------------|
| Token count | 1,131 | 275 | 4.1:1 ratio |
| Unique types | 344 | 129 | Broader → narrower |
| Jaccard similarity | | | **0.073** (highly distinct) |
| Universal MIDDLE rate | 4.42% | 10.18% | S uses more tail vocabulary |

**Chi-square tests (all p < 0.001):**
| Morpheme | Chi² | Cramér's V |
|----------|------|------------|
| PREFIX | 59.0 | 0.205 |
| MIDDLE | 550.8 | **0.737** |
| SUFFIX | 119.8 | 0.294 |

**Interpretation:** C and S have **distinct morphological signatures** - the grammar marks intake vs release positions differently.

### 5. Commitment Point Grammar: No Backward Motion

**Source:** azc_activation.act.yaml (C434)

**R-Series Transition Rules:**

| Transition | Count | Status |
|------------|-------|--------|
| R1→R2 (forward) | 2 | Legal (rare) |
| R2→R3 (forward) | Observed | Legal (rare) |
| R2→R1 (backward) | **0** | FORBIDDEN |
| R3→R2 (backward) | **0** | FORBIDDEN |
| R1→R3 (skip) | **0** | FORBIDDEN |

**No backward motion allowed.** This grammatically encodes the "commitment point" - once you enter R-series, you cannot return to earlier positions.

---

## Summary of Phase Transition Markers

| Marker | Location | Signal | p-value |
|--------|----------|--------|---------|
| **HT step change** | AZC entry | -0.385 polarity reversal | < 1.2e-6 |
| **Escape gradient** | R-series | 5.3% → 0% progressive | < 0.0001 |
| **LINK distribution** | Throughout | Monitoring→intervention boundary | Documented |
| **Morphological signature** | C vs S | Distinct PREFIX/MIDDLE profiles | < 0.001 |
| **Forbidden transitions** | R-series | No backward motion | 0/0 observed |

---

## Connection to Historical Parallel

### Heads/Hearts/Tails as Decision Grammar

| Distillation Phase | AZC Position | Escape Rate | Intervention Permission |
|--------------------|--------------|-------------|------------------------|
| **Heads (foreshots)** | P | 15.87% | CAN adjust |
| **Hearts** | R-series | 5.3%→0% | COMMITTED |
| **Tails (feints)** | S | 4.36% | Decision point |

The grammatical markers encode the historical concept:
- **"Signs of change"** = HT polarity reversal at boundaries
- **Commitment point** = R-series no-backward-motion rule
- **Phase-gated intervention** = LINK as monitoring/action boundary

---

## Conclusion

**Test 3 Verdict: STRONG_MARKERS_IDENTIFIED**

Multiple grammatical features signal phase transitions:

1. **HT step change (-0.385)** at AZC entry - orientation reset
2. **Escape gradient (5.3%→0%)** through R-series - progressive commitment
3. **LINK distribution** - marks monitoring/intervention boundary
4. **Morphological asymmetry** - distinct C vs S signatures
5. **Forbidden backward transitions** - grammatical commitment encoding

These markers validate the historical parallel: the grammar encodes "signs of change" that signal when phase transitions occur and when intervention options close.

---

## Related Constraints

- C460: AZC Entry Orientation (HT step change)
- C443: Position-Conditioned Escape Suppression
- C434: R-Series Strict Forward Ordering
- C366: LINK Marks Monitoring/Intervention Boundary
- F-AZC-008: C/S Boundary Asymmetry

---

## Data Sources

- `results/azc_entry_orientation_trace.json` - HT trajectory analysis
- `results/azc_escape_by_position.json` - Escape rates by position
- `results/azc_boundary_asymmetry.json` - C vs S analysis
- `context/METRICS/link_metrics.md` - LINK distribution
- `context/STRUCTURAL_CONTRACTS/azc_activation.act.yaml` - Positional rules
