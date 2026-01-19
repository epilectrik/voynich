# CAR Phase Observations - Currier A Human-Factors Refinement

**Tier:** 3 (Speculative observations - CAR-O1 validated)
**Phase:** CAR (Currier A Re-examination)
**Date:** 2026-01-16
**Status:** CAR-O1 VALIDATED | Others pending cross-section replication

---

## Summary

Phase CAR re-examined Currier A with clean H-only data following the transcriber filtering bug fix. The phase revealed structure at the **interface level** (how a human scans and navigates entries) rather than the **architecture level** (how systems relate).

**These are human-factors refinement observations, not architectural claims.**

---

## Key Observations

### CAR-O1: A-B Population Frequency Correlation - VALIDATED

**Raw observation:** rho = 0.491, p < 0.0001

**Controlled validation results (2026-01-16):**

| Test | Finding |
|------|---------|
| CAR-FC1 (Within-band) | Correlation persists in high-frequency band (rho=0.52) |
| CAR-FC2 (Rank-shuffled) | Overall correlation fully explained by frequency structure |
| CAR-FC3 (Section-stratified) | Consistent across A and C sections (CV=0.04) |

**Verdict: INFRASTRUCTURE EFFECT (FREQUENCY-DOMINATED)**

The correlation reflects shared high-frequency vocabulary:
- Tokens common in A are common in B (core apparatus terms)
- Within high-frequency tokens, there's additional correlation
- Effect is consistent across manuscript sections

**What this does NOT mean:**
- Does NOT violate C384 (no entry-level A<->B coupling)
- Does NOT contradict C451 (HT stratification - different topic)
- Does NOT imply per-token procedural meaning

**Why this is expected:**
- Both systems describe the same apparatus space
- Consistent with C281/C282/C285 (161 balanced tokens, shared vocabulary)
- Consistent with C343 (A-tokens persist across AZC placements)
- Registry and procedures naturally share operational terminology

**Architectural status:** CONFIRMED CONSISTENT - No constraint changes required

---

### CAR-O2: Entry Terminators (Closure States)

**Observation:** Tokens enriched at line-final position (>3x expected)
- dan (4.7x), dam (3.8x), sal (3.4x), d (3.4x), dy (2.9x)

**Deep analysis findings (2026-01-16):**
- DA-family tokens enriched 1.92x at last position (18.1% vs 9.4% baseline)
- Morphological signature: -y ending 36.5%, -n ending 15.2%, -m ending 12.2%
- Boundary enrichment is LINE_BOUNDARY_PRIMARY (5-7x stronger at line position than DA position)
- 91% of lines have NEITHER starter NOR terminator (not delimiters)

**Interpretation (validated by expert review):**
- **Closure states**, not delimiters - return vocabulary space to neutral, maximally compatible state
- DA-family closure reduces cognitive load before starting new discrimination bundle
- The -y/-n/-m endings are "cognitively safe landing points"
- Function: signal that current entry has emitted all its discriminating vocabulary
- Consistent with C233 (LINE_ATOMIC), C422 (DA articulation), C475 (DA-boundary suppression)

**Required validation:** Cross-section replication (mechanism validated)

---

### CAR-O3: Entry Starters (Openers)

**Observation:** Tokens enriched at line-initial position (>2.5x expected)
- tol (3.8x), dchor (3.5x), sor (2.7x), qotol (2.5x)

**Deep analysis findings (2026-01-16):**
- 57.5% of first tokens have NO standard PREFIX (non-prefix openers)
- DA-family depleted 0.66x at first position (6.2% vs 9.4% baseline)
- Entry grammar pattern: [non-prefix opener] + [prefixed content] + [DA-family closer]

**Interpretation:**
- Openers emerge FROM closure - entry starts after closure state emits
- Not delimiters or headers - absence of regular prefix structure
- Cognitive bracketing affordances (visual entry recognition)
- NOT semantic content markers

**Required validation:** Cross-section replication

---

### CAR-O4: Folio Marker Specialization

**Observation:** Entropy 1.35 vs baseline 1.46
- Most specialized: f100v (89% ch), f16v (83% ch)

**Interpretation:**
- Folios organize around dominant marker types
- Thematic clustering at folio level
- Consistent with C424 (clustered adjacency)

**Required validation:** Section-stratified null comparison

---

### CAR-O5: Block Position Vocabulary

**Observation:** Chi-square 77.3, p < 0.0001
- qo, sh prefer FIRST block position
- ct prefers LAST block position

**Interpretation:**
- DA-segmented blocks have positional structure
- Consistent with C422 (DA as internal punctuation)
- May indicate processing sequence cues

**Required validation:** Post-CAS block framing review
- Note: "block" framing is sensitive after CAS collapse of C250

---

### CAR-O6: Entry Grammar (Closure State Architecture)

**Observation:** Systematic morphological structure at entry boundaries

**Evidence synthesis:**
| Position | Pattern | Enrichment |
|----------|---------|------------|
| FIRST | No standard prefix | 57.5% of openers |
| FIRST | DA-family depleted | 0.66x |
| LAST | DA-family enriched | 1.92x |
| LAST | -y/-n/-m endings | 63.9% cumulative |

**Entry structure formula:**
```
[non-prefix opener] + [prefixed content] + [DA-family closer]
```

**Interpretation (validated by expert review):**

This is NOT a delimiter system. It's a **closure state architecture**:

1. **Closure, not boundary:** The DA-family tokens at line-final position are not punctuation marking "end". They are **closure states** - vocabulary-neutral tokens that return the system to a maximally compatible state.

2. **Cognitive reset:** After a closure state, ANY next entry can begin. Closure reduces cognitive load by signaling "current entry has emitted all discriminating vocabulary."

3. **Openers emerge from closure:** Entry-initial tokens don't "mark start" - they're simply the first non-closure vocabulary after a closure state. Their non-prefix nature means they don't immediately commit to a discrimination path.

4. **Why this matters:** A registry without punctuation still needs human usability. Closure states make it cognitively scannable without semantic interpretation. The reader can visually bracket entries by recognizing closure morphology.

**Relationship to existing constraints:**
- Cements C233 (LINE_ATOMIC) - now we understand the mechanism
- Cements C236, C240 (line independence) - closure enables independence
- Cements C422 (DA articulation) - DA-family has dual role (internal punctuation AND entry closure)
- Cements C475 (DA-boundary suppression) - same mechanism, different context

**Does NOT:**
- Reopen LINE = RECORD (confirmed, now explained)
- Create new architectural constraints (this is human-factors interface)
- Imply semantic meaning in boundary tokens

**Status:** Validated mechanism - awaiting cross-section replication of specific ratios

---

### CAR-O7: LINE_BOUNDARY_PRIMARY

**Observation:** Boundary marker enrichment is 5-7x stronger at LINE position than DA position

**Evidence:**
| Token | Line-initial | DA-initial | Ratio |
|-------|--------------|------------|-------|
| tol | 3.8x | 0.6x | 6.3x stronger |
| dchor | 3.5x | 0.5x | 7.0x stronger |
| sor | 2.7x | 0.6x | 4.5x stronger |

**Interpretation:**
- Boundary markers mark LINE boundaries, not DA-block boundaries
- This is consistent with LINE = RECORD (not DA-block = sub-record)
- DA articulation is internal punctuation; LINE boundaries are entry boundaries

**Required validation:** None (mechanism confirmed)

---

## Adjacency Structure Confirmed

The following are NOT new observations but **confirmations of existing constraints** with clean data:

| Existing Constraint | CAR Finding |
|---------------------|-------------|
| C346 (sequential coherence 1.31x) | Clean value: 1.20x - SURVIVES |
| C424 (clustered adjacency 31%) | Clean value: 41.5% - STRENGTHENED |
| C422 (DA articulation) | CONFIRMED |
| C389 (adjacency structure exists) | CONFIRMED with 9.1% bigram reuse |

These confirm that adjacency structure is real, just less inflated than previously measured.

---

## What This Phase Contributes

**Domain:** Human-factors interface design, not architecture

**Questions answered:**
1. How would a human navigate and scan Currier A entries?
2. What mechanism makes LINE = RECORD cognitively usable?
3. Why do boundary-enriched tokens exist in a system without punctuation?

**Major finding: Closure State Architecture**

Currier A entries use **closure states** (not delimiters) for human usability:
- DA-family tokens at entry-final position return vocabulary to neutral state
- Non-prefix openers don't commit to discrimination path immediately
- Morphological cues (-y/-n/-m endings) signal safe cognitive landing points
- This makes a non-semantic registry scannable and navigable

**Evidence for:**
- Boundary markers exist (starters/terminators)
- Boundary markers are CLOSURE STATES (validated mechanism)
- Folios specialize by marker type
- Block position affects vocabulary
- Shared vocabulary pool with B (not shared meaning)
- Entry grammar: [non-prefix opener] + [prefixed content] + [DA-family closer]

**Evidence against:**
- Sister pairs do NOT cluster (ch-sh, ok-ot - NULL finding)
- DA blocks do NOT segment semantically coherent units (NULL finding)
- DA count does NOT correlate with entry complexity (NULL finding)
- Multi-line records do NOT exist (91% of lines have neither marker)

---

## Integration Path

If observations survive frequency-controlled validation:

1. **Add to Currier A usage model** - Document how entries are scanned
2. **Do NOT add to architecture** - These are interface details
3. **Consider for CASC extension** - Potential navigation affordances section
4. **Do NOT propose as Tier 2 constraints** - Remain Tier 3 until replicated

---

## Validation Schedule

| Observation | Required Test | Status |
|-------------|---------------|--------|
| CAR-O1 | Partial correlation, rank-shuffled null | **COMPLETE** - Infrastructure effect confirmed |
| CAR-O2 | Cross-section replication (specific ratios) | Mechanism VALIDATED, ratios pending |
| CAR-O3 | Cross-section replication | Mechanism VALIDATED, ratios pending |
| CAR-O4 | Section-stratified null | Pending |
| CAR-O5 | Post-CAS block review | Pending |
| CAR-O6 | Closure state cross-validation | **COMPLETE** - Mechanism validated |
| CAR-O7 | LINE_BOUNDARY_PRIMARY | **COMPLETE** - 5-7x ratio confirmed |

---

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C384 | NOT violated by CAR-O1 |
| C451 | Different topic (HT stratification) |
| C281/C282/C285 | Predicts CAR-O1 (shared vocabulary) |
| C343 | Predicts A-token persistence |
| C233 | **CEMENTED** by CAR-O6 (LINE_ATOMIC - now with mechanism) |
| C236/C240 | **CEMENTED** by CAR-O6 (line independence via closure) |
| C422 | **CEMENTED** by CAR-O6 (DA dual role: internal punctuation + closure) |
| C424 | CAR-O4 extends (clustered adjacency) |
| C475 | **CEMENTED** by CAR-O6 (DA-boundary suppression via closure) |

---

## Source Files

Full analysis: `phases/CAR_currier_a_reexamination/`
- `CAR_REPORT.md` - Complete findings
- `car_track*.py` - Track test implementations
- `car_frequency_controlled.py` - A-B correlation validation
- `car_da_boundary_analysis.py` - LINE vs DA boundary analysis
- `car_multiline_detection.py` - LINE = RECORD confirmation
- `car_boundary_semantics.py` - PREFIX-boundary association
- `car_prefix_boundary_deep.py` - Closure state mechanism discovery
- `car_track*_results.json` - Raw results

---

*Tier 3: Speculative observations pending validation*
*Do not cite as fact*
*Do not extend without controlled replication*
