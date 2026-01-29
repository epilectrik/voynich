# C845: B Paragraph Self-Containment

**Tier:** 2
**Scope:** B
**Phase:** B_PARAGRAPH_STRUCTURE

## Constraint

B paragraphs do not exhibit inter-paragraph linking. Unlike A's RI linkers (C835-C838), HT tokens in B paragraph headers do not create cross-reference networks between paragraphs. Each B paragraph is a self-contained mini-program.

## Evidence

Testing whether B's HT tokens link paragraphs like A's RI tokens:

| Metric | A (RI) | B (HT) | Interpretation |
|--------|--------|--------|----------------|
| Both-position rate | 0.6% | 7.1% | B = general vocabulary, not deliberate linking |
| ct-prefix signature | 75% | 0% | No morphological marker |
| h-MIDDLE signature | 75% | 0% | No morphological marker |
| Topology | Strictly convergent | 66% symmetric | B = random distribution |

**B positional structure:**
- INITIAL-only: 67.8%
- FINAL-only: 25.2%
- Both positions: 7.1%

The 7.1% "both-position" rate is 12x higher than A's 0.6%, indicating less positional specialization rather than deliberate linking. A's linkers are rare and morphologically marked; B's overlap is common and unmarked.

**Topology comparison:**
- A linkers: 4 tokens create 12 directed links across 12 folios (convergent network)
- B tokens in both positions: 187 types with mixed topology (24 convergent, 39 divergent, 124 symmetric)

## Structural Interpretation

The asymmetry reflects functional differences:

| System | Role | Linking Behavior |
|--------|------|------------------|
| A (registry) | Cross-reference entries | ct-ho linkers create explicit links |
| B (execution) | Run self-contained programs | No inter-paragraph references |

A→B provides **vocabulary constraints**, not **execution flow**. B paragraphs operate independently within A-defined constraints.

## Why This Matters

Confirms the A/B functional separation:
- A = registry with relational structure (RI linkers)
- B = execution with isolated units (self-contained paragraphs)

B's paragraph structure (C840-C844) provides **identification and context**, not **cross-referencing**.

## Provenance

- Script: `phases/B_PARAGRAPH_STRUCTURE/scripts/b_ht_linker_test.py`
- Data: `phases/B_PARAGRAPH_STRUCTURE/results/b_ht_linker_test.json`
- Depends: C835 (RI linker mechanism), C840 (B paragraph structure)

## Status

CONFIRMED - Negative result validates B paragraph independence.
