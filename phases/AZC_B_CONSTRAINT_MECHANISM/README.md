# AZC_B_CONSTRAINT_MECHANISM Phase

## Objective

Pin down the CONCRETE MECHANISM by which AZC constrains Currier B. Move from "something is going on" to "here's exactly what's happening."

## The Problem

We say "AZC constrains B" but this is hand-wavy. What does it actually mean?

Current understanding:
- A->AZC->B is "constraint propagation, not content routing" (C753)
- AZC has zero KERNEL/LINK - it's outside the execution layer (C757)
- 70% of AZC MIDDLEs are folio-exclusive (C760)
- Both AZC families provide redundant B coverage (C761)

But we haven't answered:
- What specific property of B does AZC constrain?
- How does the constraint operate at token/vocabulary level?
- Is it predictive? Can we predict B behavior from AZC overlap?

## Testable Hypotheses

### H1: Vocabulary Restriction Hypothesis
AZC constrains B by restricting which MIDDLEs are available. Since 70% of AZC MIDDLEs are folio-exclusive, a B folio's vocabulary is determined by which AZC folios it overlaps with.

**Test:** Measure B folio vocabulary as function of AZC overlap. Do B folios with narrow AZC overlap have narrower vocabulary?

### H2: Behavioral Prediction Hypothesis
If AZC genuinely constrains B execution, then AZC overlap patterns should predict B behavioral properties (escape rate, hazard exposure, REGIME).

**Test:** Correlate AZC overlap metrics with B behavioral metrics per folio.

### H3: Bottleneck Hypothesis
The constraint operates as a bottleneck - B folios must use vocabulary that passed through AZC, and the AZC folio(s) determine what's available.

**Test:** Quantify what fraction of each B folio's vocabulary is AZC-mediated vs B-native. Does this fraction predict anything?

### H4: No Real Constraint (Null Hypothesis)
AZC and B vocabulary overlap is incidental - they share common Voynichese words but there's no causal constraint relationship.

**Test:** Compare actual AZC-B overlap to random expectation. Is the overlap structured or just baseline similarity?

## Tests

| Test | Question | Method |
|------|----------|--------|
| T1 | What fraction of B vocabulary is AZC-mediated? | Per-B-folio AZC overlap quantification |
| T2 | Does AZC overlap predict B vocabulary size? | Correlation: AZC overlap breadth vs B vocab size |
| T3 | Does AZC overlap predict B escape rate? | Correlation: AZC metrics vs escape rate per folio |
| T4 | Does AZC overlap predict B REGIME? | REGIME classification vs AZC overlap profile |
| T5 | Is AZC-B overlap structured or random? | Compare to null model (shuffled folios) |
| T6 | Which specific MIDDLEs carry the constraint? | Identify MIDDLEs that appear in AZC AND predict B behavior |

## Key Data Sources

- `scripts/voynich.py` (Transcript, Morphology)
- AZC vocabulary from AZC_FOLIO_DIFFERENTIATION results
- B folio behavioral metrics from BCSC / existing constraints
- REGIME classifications from existing constraints

## Results

| Test | Finding | Verdict |
|------|---------|---------|
| T1 | Mean 75.5% AZC-mediated; r=-0.800 with vocab size | VOCABULARY_BOTTLENECK |
| T2 | AZC % predicts escape (r=-0.311) but mediated by vocab size | VOCAB_SIZE_MEDIATES |
| T3 | AZC tokens: 31.3% escape, 51.3% kernel; B-native: 21.5% escape, 77.8% kernel | KERNEL_ACCESS_DIFFERENCE |
| T4 | High AZC % → fewer B-native → less kernel depth → less escape needed | KERNEL_ACCESS_BOTTLENECK |

## Key Finding: C765 - AZC Kernel Access Bottleneck

**AZC constrains B by limiting kernel access, not by limiting escape directly.**

| Vocabulary Source | Escape Rate | Kernel Contact |
|-------------------|-------------|----------------|
| AZC-mediated | 31.3% (high) | 51.3% (low) |
| B-native | 21.5% (low) | 77.8% (high) |

The mechanism:
1. AZC vocabulary is escape-prone but kernel-shallow
2. B-native vocabulary is escape-resistant but kernel-deep
3. High AZC-mediation → less B-native → less kernel access
4. Less kernel access → simpler execution → less escape needed

This explains C757 (AZC has zero KERNEL/LINK) - AZC provides vocabulary that interacts with the kernel from the OUTSIDE, not from within.

## Provenance

Follow-up to AZC_FOLIO_DIFFERENTIATION, based on expert-advisor recommendation to test constraint propagation mechanism.
