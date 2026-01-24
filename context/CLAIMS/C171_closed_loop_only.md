# C171: Only Continuous Closed-Loop Process Control Survives

**Tier:** 2 | **Status:** CLOSED | **Phase:** PCI

---

## Claim

Of all purpose classes tested, only continuous closed-loop process control is structurally compatible with the Currier B grammar. All other hypotheses have been eliminated.

## Eliminated Purpose Classes

| Purpose Class | Reason for Elimination |
|---------------|------------------------|
| Cipher/hoax | Phase G: transforms DECREASE MI |
| Encoded language | Phase X.5: 0.19% reference rate |
| Recipe/pharmacology | No batch boundaries |
| Herbarium/taxonomy | No identifier tokens |
| Medical procedure | No patient-response branching |
| Astronomical calculation | No computational primitives |
| Ritual/symbolic | No conditional structure |
| Educational text | No definitions or examples |
| Discrete batch operations | No end markers |
| Fermentation | No time-dependent markers |
| Glassmaking/metallurgy | Wrong hazard topology |
| Dyeing/mordanting | Wrong phase structure |

## What Remains

**Continuous closed-loop process control** characterized by:
- Ongoing monitoring (38% LINK)
- Intervention when needed (kernel operators)
- Hazard avoidance (17 forbidden transitions)
- State maintenance (convergence to STATE-C)

### Tokens as State-Triggered Interventions (Clarification)

B tokens are **interventions selected by a control loop based on assessed system state**, not sequential recipe steps. The program structure is:

```
MONITOR state
    ↓
ASSESS: does state require intervention?
    ↓
SELECT intervention (from legal set)
    ↓
EXECUTE intervention
    ↓
RETURN to MONITOR
```

**Recipe model (WRONG):**
- Step 1: Chop
- Step 2: Grind
- Step 3: Heat
- Fixed sequence

**Control model (CORRECT):**
- IF material too coarse → apply chop intervention
- IF material needs fine texture → apply grind intervention
- IF temp low → apply heat intervention
- Condition-triggered responses

This explains observed patterns:
- **High line-to-line class change (94.2%)** - state varies between assessments
- **Positional preferences** - monitor/assess phases vs intervention phases
- **Low within-line repetition (5.2%)** - one intervention per assessment cycle
- **LINK operator function (C366)** - boundary between monitoring and intervention phases
- **Partial token differentiation** - related interventions triggered by related conditions

The grammar encodes **which interventions are legal given current state constraints**, not which intervention comes "next" in a sequence. Different tokens within the same class represent related but distinct interventions (like "chop" vs "grind") that may be triggered by different assessed conditions.

**Supporting evidence (2026-01-23):**
- Predecessor profiles differ for different-MIDDLE tokens (p=0.04)
- Successor profiles differ more strongly (p=0.0003)
- Pred/succ divergence ratio = 0.51 (partial differentiation)
- Mean co-occurrence rate = 5.2% (mostly mutually exclusive)

> **DISALLOWED INTERPRETATIONS**
>
> Any interpretation that introduces discrete steps, batch semantics, or narrative sequence is invalid. This includes:
> - "B encodes step X, then step Y" (batch processing)
> - "B encodes material preparation" (discrete steps)
> - "B encodes ingredient lists" (taxonomic, not control)
> - "B encodes recipes" (narrative sequence)
>
> **Valid framing:** B encodes control envelopes. External analysts may observe that these envelopes are *compatible with* certain materials or processes, but compatibility is discovered externally, not encoded internally.
>
> *Added 2026-01-22 following framing correction review. See `phases/INTEGRATED_PROCESS_TEST/FRAMING_CORRECTION.md`*

## Viable Process Classes (Tier 2)

1. Circulatory reflux distillation
2. Volatile aromatic extraction
3. Circulatory thermal conditioning

## Related Constraints

- C157 - Circulatory reflux uniquely compatible
- C175 - 3 process classes survive
- C177 - Both extraction/conditioning survive

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
