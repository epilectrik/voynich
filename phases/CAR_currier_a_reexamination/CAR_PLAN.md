# Plan: Phase CAR - Currier A Re-examination with Clean Data

## Status: IN PROGRESS

---

## Phase Metadata

| Field | Value |
|-------|-------|
| **Phase ID** | CAR (Currier A Re-examination) |
| **Tier** | 2 (Structural inference) |
| **Trigger** | Transcriber bug fix invalidated C250-C266; clean data available |
| **Scope** | Currier A internal structure + A→AZC→B pipeline gaps |
| **Dependencies** | H-only filtering mandatory for all scripts |

---

## Executive Summary

The transcriber filtering bug (loading ALL transcribers instead of H-only) created ~3.2x token inflation and false patterns. C250-C266 (block repetition) were entirely artifacts. Now with clean data, we can:

1. **Recover** patterns that were lost in noise
2. **Re-test** analyses that returned null results
3. **Fill gaps** in the A→AZC→B pipeline understanding

This phase systematically tests what structure actually exists in Currier A and how it connects to downstream systems.

---

## Research Questions

### RQ-1: What adjacency structure exists in clean A data?
C346 found 1.31x sequential overlap, but counts were inflated. Does structure persist?

### RQ-2: What's inside DA-segmented sub-records?
C422 established DA as punctuation (75.1% separation). Do sub-records have internal coherence?

### RQ-3: How does A organize entries for lookup?
We know lines are atomic and markers classify - but what's the indexing system?

### RQ-4: Why is A/C 45% denser in MIDDLE incompatibility?
F-AZC-019 found this difference vs Zodiac. What does it achieve downstream?

### RQ-5: Do failed tests yield results with clean data?
A-B correlation (C451) and HT-phase reset in A/C returned null. Retry?

---

## Track Structure

### Track 1: Adjacency Pattern Recovery (HIGH PRIORITY)

#### Test CAR-1.1: Bigram Distribution (Clean)
**Question:** What is the actual bigram reuse rate with H-only data?

#### Test CAR-1.2: MIDDLE Adjacency Coherence
**Question:** Do adjacent entries share MIDDLEs more than expected?

#### Test CAR-1.3: Transition Matrix (Clean)
**Question:** Are there forbidden or enriched adjacency patterns?

---

### Track 2: DA Block Mechanics (HIGH PRIORITY)

#### Test CAR-2.1: Sub-Record Vocabulary Coherence
**Question:** Do DA-segmented blocks have higher internal vocabulary overlap than random?

#### Test CAR-2.2: Block Position Effects
**Question:** Does block position (first vs middle vs last) predict vocabulary?

#### Test CAR-2.3: DA Count vs Entry Complexity
**Question:** Does more DA articulation correlate with entry complexity?

---

### Track 3: Entry Organization & Lookup (MEDIUM PRIORITY)

#### Test CAR-3.1: Marker Run Analysis
**Question:** Do same-marker entries cluster spatially?

#### Test CAR-3.2: Folio-Level Marker Concentration
**Question:** Do folios specialize in certain markers?

#### Test CAR-3.3: Sister Pair Proximity
**Question:** Do sister pairs (ch-sh, ok-ot) appear near each other?

#### Test CAR-3.4: Index Token Detection
**Question:** Are there tokens that mark entry beginnings or endings?

---

### Track 4: A/C Discrimination Analysis (HIGHEST SCIENTIFIC INTEREST)

#### Test CAR-4.1: Incompatibility Density vs B Escape Rate
**Question:** Does A/C's higher density correlate with downstream B behavior?

#### Test CAR-4.2: A/C Specificity Mechanism
**Question:** Does A/C achieve specificity through density or through vocabulary?

#### Test CAR-4.3: Constraint Propagation Path
**Question:** Do A/C constraints propagate to B through MIDDLE incompatibility?

---

### Track 5: Failed Test Retries (MEDIUM PRIORITY)

#### Test CAR-5.1: A-B Correlation (Retry)
**Question:** Is there ANY correlation between A vocabulary and B usage?

#### Test CAR-5.2: HT-Phase Reset in A/C (Retry)
**Question:** Does HT show different reset patterns in A/C vs Zodiac?

---

## Stop Conditions

### Hard Stops

| Condition | Action |
|-----------|--------|
| All Track 1 tests return null | STOP - adjacency structure doesn't exist |
| Track 4 shows no A/C-Zodiac difference | STOP - F-AZC-019 was artifact |
| 3+ tests show transcriber-variant results | STOP - need transcriber audit first |

### Constraint Proposal Threshold

New constraint requires:
- p < 0.001 for statistical tests
- Effect size > 0.1 for correlations
- Cross-validation with shuffled baseline
- NOT explainable by existing constraints

---

## Files

| File | Purpose |
|------|---------|
| `CAR_PLAN.md` | This document |
| `car_data_loader.py` | Common data utilities |
| `car_track1_adjacency.py` | Track 1 tests |
| `car_track2_da_blocks.py` | Track 2 tests |
| `car_track3_organization.py` | Track 3 tests |
| `car_track4_ac_discrimination.py` | Track 4 tests |
| `car_track5_retries.py` | Track 5 tests |
| `car_results.json` | All test results |
| `CAR_REPORT.md` | Final synthesis |

---

*Phase CAR initiated.*
