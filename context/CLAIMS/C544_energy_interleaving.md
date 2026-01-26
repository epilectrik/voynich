# C544: ENERGY_OPERATOR Interleaving Pattern

**Tier:** 2 | **Status:** CLOSED | **Scope:** CO-OCCURRENCE

---

## Statement

> ENERGY_OPERATOR classes exhibit systematic interleaving: qo-family (Classes 32-33) and ch/sh-family (Classes 8, 31, 34) alternate in sustained chains, with 2.5x enrichment for qo->ch/sh transitions.

---

## Interleaving Evidence

**Enriched Adjacent Pairs:**
| Transition | Enrichment | Occurrences | Classes |
|------------|------------|-------------|---------|
| 32 -> 8 | 2.56x | 104 | qokal -> chedy |
| 8 -> 33 | 2.24x | 210 | chedy -> qokeey |
| 8 -> 32 | 2.44x | 99 | chedy -> qokal |
| 36 -> 8 | 2.33x | 30 | qotar -> chedy |

**Common Trigram Motifs:**
| Pattern | Count | Classes |
|---------|-------|---------|
| (33, 33, 33) | 45 | qokeey self-chain |
| (32, 8, 33) | 33 | qo -> ch -> qo interleave |
| (8, 33, 33) | 32 | ch -> qo -> qo buildup |
| (33, 34, 33) | 30 | qo -> ch-extended -> qo |

---

## Self-Repetition Pattern

| Class | Role | Self-Repeat Rate | Tokens |
|-------|------|------------------|--------|
| 33 | ENERGY | **14.6%** | qokeey, qokeedy |
| 8 | ENERGY | 5.2% | chedy, shedy |
| 34 | ENERGY | 5.0% | cheey, cheol |

Class 33 (qokeey family) shows highest self-repetition, creating sustained qo-chains that intersperse with ch/sh operations.

---

## Interpretation

The interleaving pattern suggests alternating operational modes:
- **qo-family** = One type of energy operation (possibly "escape route" per C397)
- **ch/sh-family** = Complementary energy operation (possibly "precision mode" per C412)

The 2.5x enrichment for qo->ch transitions indicates grammatical preference for alternation over same-family sequences.

---

## Evidence

**Test:** `phases/INSTRUCTION_CLASS_CHARACTERIZATION/scripts/class_cooccurrence_analysis.py`

- Analyzed 2,396 lines for class bigram patterns
- Calculated enrichment vs independence baseline
- Identified trigram motifs appearing 5+ times

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C412 | Extended - transition-level evidence of sister-escape anticorrelation |
| C397 | Consistent - qo-prefix escape route pattern |
| C408 | Consistent - ch-sh/ok-ot equivalence classes |

---

## Provenance

- **Phase:** INSTRUCTION_CLASS_CHARACTERIZATION
- **Date:** 2026-01-25
- **Script:** class_cooccurrence_analysis.py

---

## Navigation

<- [C543_role_positional_grammar.md](C543_role_positional_grammar.md) | [C545_regime_class_profiles.md](C545_regime_class_profiles.md) ->
