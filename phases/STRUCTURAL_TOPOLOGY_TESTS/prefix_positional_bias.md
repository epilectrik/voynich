# Test 6: PREFIX Positional Bias

**Question:** Do control-flow participation roles (PREFIX) show positional bias within B programs?

**Verdict:** PARTIALLY_CONFIRMED - Line-level positional grammar exists; program-level gradient requires further testing

---

## Critical Framing (Expert Requirement)

**DO NOT** frame as "materials changing" or "M-A early, M-D late."

**CORRECT framing:**
> Do control-flow roles show positional constraints within closed-loop trajectories?

The question is about GRAMMAR constraints on where certain control-flow roles appear, not about material transformation through a process.

---

## Existing Evidence

### 1. Line-Level Positional Grammar in B (C371, C375)

**C371: PREFIX Positional Grammar (Tier 2, CLOSED)**

| PREFIX | Line-Initial Enrichment | Line-Final Enrichment |
|--------|------------------------|----------------------|
| so | **6.3x** | - |
| ych | **7.0x** | - |
| pch | **5.2x** | - |
| lo | - | **3.7x** |
| al | - | **2.7x** |

**C375: SUFFIX Positional Grammar (Tier 2, CLOSED)**

| SUFFIX | Line-Final Enrichment | Notes |
|--------|----------------------|-------|
| -am | **7.7x** | 80-90% line-final |
| -om | **8.7x** | 80-90% line-final |
| -oly | **4.6x** | Strong line-final |

**Interpretation:** B-grammar has STRONG positional constraints at the LINE level. Some prefixes are line-openers, others are line-closers.

### 2. Currier A Is Position-Free (C234)

**C234: A = POSITION_FREE (Tier 2, CLOSED)**

- Zero JS divergence between positions
- No positional grammar in A
- **Source:** CAS

**Interpretation:** Unlike B, Currier A has no positional constraints. This is consistent with A being a registry (non-sequential) rather than a program (sequential control flow).

### 3. Inference: Control-Flow Roles Have Grammatical Positions

The strong line-level positional grammar in B suggests:

1. **Control-flow roles are not freely orderable** - Grammar constrains where they appear
2. **Line-initial prefixes (so, ych, pch)** may be "entry" roles
3. **Line-final prefixes (lo, al)** may be "exit" roles

This is CONTROL-FLOW grammar, not material transformation.

---

## Program-Level Gradient: Requires Further Testing

### The Expert's Question

The expert asked about positional bias **within programs** (early/mid/late thirds), not just at line boundaries.

**Untested Hypothesis:**
> Do certain control-flow roles concentrate in early, middle, or late portions of B programs?

### What We Know

| Evidence | Finding |
|----------|---------|
| C371 | PREFIX has line-level positional grammar |
| C382 | Morphology encodes control phase |
| AZC | C→P→R→S progression narrows options |

**C382 suggests:** Morphology (which includes PREFIX) encodes control phase information. This would predict some program-level positional bias.

### What We Don't Yet Know

1. Do certain PREFIXes concentrate in early vs late program phases?
2. Is there a PREFIX × program-position gradient?
3. Does M-A/B/C/D distribution vary by program position?

---

## Structural Model (Current Understanding)

```
B PROGRAM STRUCTURE
├── Line 1 (early program)
│   ├── so/ych/pch- (line-initial)
│   ├── ... (mid-line)
│   └── lo/al- + -am/-om (line-final)
├── Line 2
│   └── [same line-level grammar]
├── ...
└── Line N (late program)
    └── [same line-level grammar]

QUESTION: Does PREFIX distribution also vary
          across Lines 1 vs Lines N?
```

---

## Conclusion

**Test 6 Verdict: PARTIALLY_CONFIRMED**

**What's confirmed (Tier 2):**
1. PREFIX has strong LINE-LEVEL positional grammar (C371)
2. Control-flow roles are grammatically constrained
3. Currier A has NO positional grammar (C234)

**What's unconfirmed:**
1. Program-level PREFIX gradient (early/mid/late)
2. M-A/B/C/D × program-position interaction

### Recommended Follow-Up Analysis

To fully answer the expert's question:

```python
# Proposed Test
1. For each B program (folio):
   - Segment into thirds (early/mid/late)
   - Count PREFIX occurrences per third
2. Test for positional independence:
   - Chi-square: PREFIX × program-position
3. If significant, characterize gradient:
   - Which PREFIXes skew early?
   - Which skew late?
4. Frame result as CONTROL-FLOW positions, NOT material flow
```

---

## Epistemic Note

This test is PARTIALLY COMPLETE. Existing constraints confirm line-level positional grammar but do not directly address program-level gradients.

The absence of program-level evidence is **not evidence of absence** - this specific test hasn't been run.

---

## Related Constraints

- C371: PREFIX Positional Grammar (line-level, confirmed)
- C375: SUFFIX Positional Grammar (line-level, confirmed)
- C234: A = POSITION_FREE
- C382: Morphology Encodes Control Phase

---

## Data Sources

- `context/CLAIMS/morphology.md` - C371, C375
- `context/CLAIMS/currier_a.md` - C234
