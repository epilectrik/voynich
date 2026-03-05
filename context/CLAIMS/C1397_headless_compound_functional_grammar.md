# C1397: Headless Compound Functional Grammar

**Tier:** 2 (ESTABLISHED)
**Scope:** B, MIDDLE, headless, grammar, composition
**Phase:** HEADLESS_COMPOUND_GRAMMAR (Phase 509)
**Extends:** C1394 (instruction encoding architecture, T8-T11 headless findings), C1395 (cross-system, T2 HEAD recovery rejected)
**Relates to:** C1250 (operational categories), C1393 (composition grammar)

---

## Statement

Headless compounds (20.6% of compound tokens, 3,288 tokens, 467 types) are NOT a homogeneous infrastructure class. The initial atom of a headless compound acts as a **pseudo-HEAD**, creating atom-specific functional domains with distinct category profiles (V=0.503), PREFIX channel preferences (V=0.459), positional specialization, and suffix behavior. The headless subgrammar follows the same modifier ordering as headed compounds (61.9% vs 70.1% compliance) but with a stark suffix bifurcation: d/i-initial are bare-dominant (85-93%) while c/p/f-initial are suffix-dominant (93-97%).

### Token Counts

| Initial Atom | Role (C1394) | Tokens | Types |
|-------------|-------------|--------|-------|
| i | MODIFIER | 976 | 38 |
| d | MODIFIER | 915 | 103 |
| c | MODIFIER | 395 | 118 |
| p | MODIFIER | 157 | 45 |
| l | TERMINAL | 371 | 83 |
| r | TERMINAL | 122 | 54 |
| f | MODIFIER | 44 | 11 |
| y | TERMINAL | 71 | 44 |
| s | MODIFIER | 32 | 16 |
| h | TERMINAL | 46 | 27 |
| m | TERMINAL | 29 | 24 |
| q | (non-grammar) | 104 | 48 |

q-initial (104 tokens) is a separate non-grammar population: 98% BARE prefix, 100% unclassifiable. Excluded from functional analysis.

---

## Key Findings

### T1: Initial Atom Census

All 6 MODIFIER atoms lead headless compounds (i, d, c, p, f, s). 5/6 TERMINAL atoms also lead (l, r, y, h, m; only n absent). MODIFIER-initial dominates at 77.4% of headless tokens; TERMINAL-initial at 19.4%.

Top headless MIDDLEs: dy (675), iin (560), in (264), ck (197), ckh (127), ct (95), pch (79), lch (74), lk (58).

### T2: Functional Profiles — DIFFERENTIATED (V=0.503)

Chi2=5,601.4, V=0.503 — headless initial atoms predict operational category with high discriminative power.

| Initial | Dominant Category | Purity | Role |
|---------|------------------|--------|------|
| d | CONTAINMENT | 83.9% | Sealing/closing |
| p | MARKING | 91.7% | Hold/pause |
| f | MARKING | 90.9% | Flag/checkpoint |
| i | STAGING | 66.0% | Cycle control |
| r | FLOW | 60.7% | Response/routing |
| c | OPERATION | 32.2% | Process adjustment (most diverse) |
| l | STAGING | 27.8% | State annotation (most versatile — 6 categories above 6%) |

d, p, f are near-mono-categorical (84-92% purity). c is the most diversely distributed. l is the most versatile. This mirrors the headed pattern where some atoms lock category and others are versatile.

### T3: Positional Specialization — DIFFERENTIATED (23/45 KS pairs significant)

| Initial | Mean Pos | Line-Initial | Line-Final | Para-Initial | Role |
|---------|----------|-------------|-----------|-------------|------|
| i | 0.419 | 29.3% | 8.8% | 1.3% | Early-line |
| r | 0.670 | 22.1% | 44.3% | 11.5% | Extreme line-final |
| c | 0.523 | 2.9% | 8.2% | 0.5% | Interior-locked |
| s | 0.415 | 40.6% | 34.4% | 25.0% | Extreme boundary |
| l | 0.473 | 27.3% | 19.4% | 12.6% | Both boundaries |
| Headed | 0.492 | 9.3% | 9.2% | 2.1% | Balanced |

### T4: PREFIX Channel Distribution — DIFFERENTIATED (V=0.459)

Chi2=6,198.5. Each initial atom has distinct PREFIX preferences:

| Initial | Primary PREFIX | Rate | Secondary |
|---------|---------------|------|-----------|
| i | da | 54% | sa (19%) |
| d | ch | 20% | BARE (19%) |
| c | ch | 53% | sh (19%) |
| p | qo | 71% | BARE (11%) |
| f | qo | 61% | BARE (18%) |
| r | BARE | 39% | da (25%) |

**Critical finding:** The da enrichment reported in C1394 T8 ("da 2213x") is driven almost entirely by i-initial (iin, in). d-initial and c-initial prefer ch/sh channels. p/f-initial prefer qo. da-PREFIX is NOT a generic headless channel.

### T5: Suffix Bifurcation — DIFFERENTIATED (V=0.352)

Chi2=3,645.2. Headless compounds are more suffix-rich than headed overall (52.9% bare vs 65.0%).

| Initial | Bare Rate | Interpretation |
|---------|-----------|---------------|
| i | 93.2% | Self-contained iteration |
| d | 85.1% | Self-terminating containment |
| c | 3.8% | Almost always suffixed |
| p | 3.2% | Almost always suffixed |
| f | 6.8% | Almost always suffixed |
| l | 22.7% | Mostly suffixed |
| r | 37.0% | Mixed |

d/i are bare because they're self-contained (you seal or you don't). c/p/f need suffix specification (what *kind* of adjustment, *what* pause).

### T6: Compound Length

Headless mean 2.65 chars vs headed 2.76. Slightly shorter, consistent with infrastructure role. p-initial longest (3.43), d-initial shortest (2.18, driven by dy).

### T7: REGIME Distribution — MODERATE (within-headless V=0.157)

Notable REGIME preferences:
- l-initial: 65.4% R1 (sustained gentle-heating)
- p-initial: 50.3% R3 (open-cycle batch)
- s-initial: 34.4% R4 (precision)

### T8: Modifier Ordering Compliance — SAME GRAMMAR

Headless 61.9% vs headed 70.1%. Same grammar, slightly relaxed. The c atom is the primary ordering violator (appears earlier than expected in 4 of top 5 violations), consistent with its interior-locked positional behavior.

### T9: HT/INFRA Association — q-INITIAL ONLY

Headless HT rate 3.2% vs headed 1.7% (1.83x), but driven entirely by q-initial (100% HT). All other initial atoms are 0.0-0.1% HT. q-initial is a separate non-grammar population.

### T10: Sequential Context

Headless compounds embed within normal headed sequences (54.3% preceded by headed, 52.9% followed by headed). Not boundary-isolated. 16.9% headless→headless self-sequencing rate.

---

## Interpretation

Headless compounds constitute the **operational housekeeping layer** of the grammar. Where headed compounds specify what to do to the process (heat, cool, arrange, yield, transfer), headless compounds manage the infrastructure:

- **Containment** (d-initial): seal, close, physical management
- **Cycle control** (i-initial): iteration setup, loop management
- **Process tuning** (c-initial): mid-line parameter adjustment
- **Pause/hold** (p-initial): marking pause points in the thermal channel
- **Flagging** (f-initial): checkpoint marking in the thermal channel
- **Flow routing** (r-initial): response/output routing at line endings
- **State annotation** (l-initial): boundary state recording

The initial atom acts as a pseudo-HEAD, and the suffix bifurcation (d/i bare vs c/p/f suffixed) reflects whether the operation is binary (do/don't) or parametric (how much/what kind).

---

## Falsification Criteria

1. If initial atom category purity drops below V=0.30 under section control, findings are section-driven
2. If suffix bifurcation disappears under REGIME control, it's REGIME-driven
3. If da enrichment persists for non-i-initial headless at >10x, da-channel finding is wrong

---

## Method

- 15,929 compound Currier B tokens (H-track, labels excluded, uncertain excluded)
- 3,288 headless (first character not in {a, e, o, k, t}) across 467 types
- 10 tests: census, category profiles, position, PREFIX, suffix, length, REGIME, modifier ordering, HT association, sequential context
- Chi-squared + Cramer's V for categorical, KS for continuous
- Random seed 42

**Script:** `phases/HEADLESS_COMPOUND_GRAMMAR/scripts/headless_compound_grammar.py`
**Results:** `phases/HEADLESS_COMPOUND_GRAMMAR/results/headless_compound_grammar.json`
