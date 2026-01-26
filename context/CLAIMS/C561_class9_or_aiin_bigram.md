# C561: Class 9 or->aiin Directional Bigram

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Class 9 "self-chaining" (from C559) is actually a directional or->aiin bigram: 87.5% of chains (42/48) follow or->aiin pattern. Zero aiin->aiin sequences exist. The bigram functions as a grammatical unit, appearing after AUXILIARY tokens (51%) and before AUXILIARY tokens (45%). HERBAL shows highest bigram rate (21.7%), BIO lowest (8.8%).

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/class9_chaining_analysis.py`

### Class 9 Membership

| Token | Count | % of Class |
|-------|-------|------------|
| aiin | 351 | 55.7% |
| or | 250 | 39.7% |
| o | 29 | 4.6% |

### Chain Pair Analysis

| Pair | Count | % of Chains |
|------|-------|-------------|
| **or->aiin** | **42** | **87.5%** |
| aiin->or | 4 | 8.3% |
| or->or | 4 | 8.3% |
| aiin->o | 2 | 4.2% |
| o->aiin | 2 | 4.2% |

**Zero aiin->aiin chains exist.** This is a structural constraint, not a statistical tendency - aiin never immediately follows aiin despite being the most common Class 9 token (55.7%).

### Chain Direction

| Position | Token | Count |
|----------|-------|-------|
| Chain start | or | 41 (85%) |
| Chain start | aiin | 5 (10%) |
| Chain end | aiin | 43 (90%) |
| Chain end | or | 3 (6%) |

Pattern: `or` initiates, `aiin` terminates.

### Chain Length Distribution

| Length | Count |
|--------|-------|
| 2 | 42 (87.5%) |
| 3 | 6 (12.5%) |

Chains are predominantly bigrams.

### Context Analysis

**Preceding chains:**
| Role | % |
|------|---|
| AX | 51.1% |
| UN | 27.7% |
| EN | 14.9% |

**Following chains:**
| Role | % |
|------|---|
| AX | 44.7% |
| EN | 21.3% |
| UN | 21.3% |

Bigram embeds in AUXILIARY-rich context.

### Section Distribution

| Section | Chain Rate |
|---------|------------|
| HERBAL | 21.7% |
| RECIPE | 16.6% |
| BIO | 8.8% |

HERBAL enriched, BIO depleted (inverse of ENERGY pattern).

### Sample Contexts

```
f103r.17: sar shey qokey keedy qokeey chckhy qokal oty [or] [aiin]
f104v.38: okechey chedy chchy qotain qokain chey [or] [aiin] cheo [or] [aiin] chedain okam
f106r.17: yochor lshedy qockhey qokedain [or] [aiin] chodar
```

Pattern appears at line-end or mid-line, often in pairs.

---

## Interpretation

### Bigram as Grammatical Unit

The or->aiin sequence functions as a compound marker:
- **or:** Initiator/connector (MIDDLE=or)
- **aiin:** Terminator/anchor (MIDDLE=aiin)
- Together: Boundary or continuation signal

### Not Random Adjacency

If Class 9 tokens appeared randomly adjacent, we'd expect:
- aiin-aiin: (0.557)² = 31% of pairs
- or-aiin: 0.397 × 0.557 = 22% of pairs

Observed: or->aiin = 87.5%, aiin->aiin = 0%

The directionality (or->aiin not aiin->or) indicates grammatical structure.

### HERBAL Context

HERBAL's elevated bigram rate (21.7% vs 8.8% BIO) parallels its FREQUENT enrichment from C559. The bigram may mark procedural transitions in non-thermal (HERBAL) contexts.

---

## Revision to C559

C559 stated "Class 9 self-chains at 16.2%". This is accurate for class-level chaining but masks the internal structure:
- NOT same-token repetition
- IS directional or->aiin bigram
- Functions as grammatical unit

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C389 | Consistent - bigram-dominant determinism (H=0.41); or->aiin is structural bigram |
| C332 | Parallel - kernel bigram ordering (h→k suppressed); or→aiin similarly ordered |
| C559 | Refined - "self-chaining" is or->aiin bigram, not same-token repeat |
| C550 | Extended - FQ self-chaining (2.38x) is driven by Class 9 bigram |
| C552 | Contextualized - HERBAL +FQ profile includes or->aiin bigram usage |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** class9_chaining_analysis.py

---

## Navigation

<- [C560_class17_ol_derivation.md](C560_class17_ol_derivation.md) | [INDEX.md](INDEX.md) ->
