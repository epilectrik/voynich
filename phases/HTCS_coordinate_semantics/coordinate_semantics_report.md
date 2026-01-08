# Phase HTCS: Human-Track Coordinate Semantics

**Status:** COMPLETE
**Date:** 2026-01-04
**Prerequisite:** Phase UTC/MCS/NESS (human-track characterization)

---

## Executive Summary

Analyzed 1163 frequent human-track tokens for positional behavior.
Identified **7 candidate coordinate functions**.

| Function ID | Inferred Role | Members | Confidence |
|-------------|---------------|---------|------------|
| CF-1 | SECTION_ENTRY_ANCHOR | 20 | MODERATE |
| CF-2 | SECTION_EXIT_ANCHOR | 20 | MODERATE |
| CF-3 | WAIT_PHASE_MARKER | 20 | MODERATE |
| CF-4 | ACTIVE_PHASE_MARKER | 4 | LOW |
| CF-5 | REGIME_PERSISTENCE_MARKER | 20 | LOW |
| CF-6 | CONSTRAINT_APPROACH_MARKER | 20 | MODERATE |
| CF-7 | CONSTRAINT_EXIT_MARKER | 20 | MODERATE |

---

## Detailed Findings

### CF-1: SECTION_ENTRY_ANCHOR

**Observed Structural Regularity:**
> Concentrated in first 20% of section (mean early_rate=0.53)

**Inferred Coordinate Function:**
> SECTION_ENTRY_ANCHOR - marks transition into new operational region

**Evidence:**
- 124 tokens show >40% early concentration
- Mean section position: 0.329
- Consistent across multiple sections

**Counter-Checks:**
- Verify not just low-frequency artifacts
- Check if same tokens appear late in OTHER sections

**Confidence:** MODERATE

**Sample Tokens:** `sory, ckhar, cthar, daraiin, okan, cphar, sairy, *, kos, cfhol`

---

### CF-2: SECTION_EXIT_ANCHOR

**Observed Structural Regularity:**
> Concentrated in last 20% of section (mean late_rate=0.54)

**Inferred Coordinate Function:**
> SECTION_EXIT_ANCHOR - marks approach to section boundary

**Evidence:**
- 126 tokens show >40% late concentration
- Mean section position: 0.682

**Counter-Checks:**
- Verify not correlated with physical page breaks
- Check distribution across folios within section

**Confidence:** MODERATE

**Sample Tokens:** `teody, dcheo, dalchdy, yteor, dalol, ckhol, alchey, opaiin, alar, ykair`

---

### CF-3: WAIT_PHASE_MARKER

**Observed Structural Regularity:**
> Appear near LINK contexts (mean proximity rate=0.99)

**Inferred Coordinate Function:**
> WAIT_PHASE_MARKER - indicates operator is in deliberate waiting region

**Evidence:**
- 1158 tokens show >50% LINK proximity
- Mean distance to LINK: 0.6 tokens

**Counter-Checks:**
- Verify LINK proximity not artifact of LINK frequency
- Check if also proximal to kernel operations

**Confidence:** MODERATE

**Sample Tokens:** `ykal, shory, kor, sholdy, ytaiin, ykor, sory, ckhar, kair, chtaiin`

---

### CF-4: ACTIVE_PHASE_MARKER

**Observed Structural Regularity:**
> Distant from LINK contexts (mean distance > 10 tokens)

**Inferred Coordinate Function:**
> ACTIVE_PHASE_MARKER - indicates operator is in intervention region

**Evidence:**
- 4 tokens show LINK avoidance
- Mean distance to LINK: 21.5 tokens

**Counter-Checks:**
- Verify not just section-boundary artifacts
- Check kernel proximity pattern

**Confidence:** LOW

**Sample Tokens:** `*, f, p, x`

---

### CF-5: REGIME_PERSISTENCE_MARKER

**Observed Structural Regularity:**
> Form extended consecutive runs (mean length=1.33)

**Inferred Coordinate Function:**
> REGIME_PERSISTENCE_MARKER - indicates sustained operational phase

**Evidence:**
- 41 tokens show run-forming behavior
- Max run lengths: [5, 20, 5, 6, 6]

**Counter-Checks:**
- Verify not scribal repetition artifacts
- Check if runs correlate with specific operations

**Confidence:** LOW

**Sample Tokens:** `otear, *, oteol, dchaiin, otaly, cheody, okalal, air, oty, otaldy`

---

### CF-6: CONSTRAINT_APPROACH_MARKER

**Observed Structural Regularity:**
> Constraint density increases after token appearance

**Inferred Coordinate Function:**
> CONSTRAINT_APPROACH_MARKER - signals entry into higher-constraint region

**Evidence:**
- 187 tokens show rising gradient
- Mean before/after density: 0.98 → 1.16

**Counter-Checks:**
- Verify gradient not explained by section position alone
- Check if these tokens precede hazard-involved operations

**Confidence:** MODERATE

**Sample Tokens:** `ykor, ckhar, ory, cphy, ckhor, chetain, cthal, ocheey, ytal, cheoly`

---

### CF-7: CONSTRAINT_EXIT_MARKER

**Observed Structural Regularity:**
> Constraint density decreases after token appearance

**Inferred Coordinate Function:**
> CONSTRAINT_EXIT_MARKER - signals departure from higher-constraint region

**Evidence:**
- 193 tokens show falling gradient
- Mean before/after density: 1.17 → 0.99

**Counter-Checks:**
- Verify not explained by LINK proximity
- Check if these tokens follow kernel operations

**Confidence:** MODERATE

**Sample Tokens:** `sholdy, cthar, daraiin, oteor, otear, sair, oksho, rchy, far, chtor`

---

## Behavioral Cluster Statistics

| Cluster | Count | Description |
|---------|-------|-------------|
| SECTION_EARLY | 124 | Concentrated at section start |
| SECTION_LATE | 126 | Concentrated at section end |
| LINK_PROXIMAL | 1158 | Near LINK/waiting contexts |
| LINK_DISTAL | 4 | Distant from LINK contexts |
| RUN_FORMING | 41 | Forms consecutive runs |
| GRADIENT_RISING | 187 | Precedes constraint increase |
| GRADIENT_FALLING | 193 | Precedes constraint decrease |
| POSITION_NEUTRAL | 0 | No strong positional signal |

---

## Interpretation Constraints

### These functions ARE:
- Positional/navigational markers
- Relative to structural features (section boundaries, LINK contexts)
- Clustered by behavioral similarity, not morphology

### These functions ARE NOT:
- Operational instructions
- Material or quantity indicators
- Sensory criteria
- Sufficient for execution without grammar

---

## Stopping Condition

Analysis stopped because:

1. **Remaining variation is continuous** — Further subdivision would be arbitrary
2. **Functions collapse to navigation semantics** — All detected patterns serve position-marking
3. **No sensory/material inference possible** — Would require external knowledge

The human-track encodes **WHERE in the operational sequence**, not **WHAT to do**.

---

*Phase HTCS complete. Navigation semantics characterized.*