# Animal Identification via Multi-Dimensional PP Convergence

## Summary

Using multi-dimensional triangulation (REGIME + PREFIX profile + PP convergence), we identified 4 A records containing animal RI tokens that connect to chicken-like B folios.

**Key Finding**: The RI token `eoschso` (in record f90r1:6) matches the chicken instruction profile (ESCAPE + AUX), suggesting **eoschso = ennen (chicken)**.

---

## Method

1. **B folio selection**: Used 4D conjunction (REGIME_4 + high qo + high aux + low da) to find chicken-like B folios: f40v, f41v, f85r1, f94v, f95v1

2. **A record convergence**: Found A records where multiple PP tokens converge to 3+ chicken folios

3. **Animal RI extraction**: Identified records containing known animal RI tokens

4. **PREFIX profile mapping**: Checked which unique PP tokens map to chicken-specific operations

---

## Results

### Animal Records Found

| Record | Animal RI | Converges to | Unique PP |
|--------|-----------|--------------|-----------|
| f100r:3 | teold | ALL 5 folios | t |
| f89r2:1 | eyd | ALL 5 folios | d,ckh,eod |
| f23r:4 | chald | 3 folios | fch |
| f90r1:6 | eoschso | 4 folios | ch,l |

### PREFIX Profile Analysis

Chicken pattern: `[e_ESCAPE, AUX, UNKNOWN, e_ESCAPE]`
- Requires BOTH escape (qo) AND auxiliary (ok/ot) operations
- No FLOW (da) operations

| Animal RI | ESCAPE PP? | AUX PP? | Chicken match? |
|-----------|------------|---------|----------------|
| teold | YES (t=88% qo) | NO | Partial |
| chald | YES (fch=74% qo) | NO | Partial |
| eoschso | YES (ke,keo) | YES (ch=48% aux) | **FULL** |
| eyd | weak | weak | No |

### Brunschwig Instruction Patterns

| Animal | Sequence | Signature |
|--------|----------|-----------|
| ennen (chicken) | [e_ESCAPE, AUX, UNKNOWN, e_ESCAPE] | ESCAPE + AUX |
| scharlach/charlach/milch | [e_ESCAPE, FLOW, UNKNOWN, UNKNOWN] | ESCAPE + FLOW |
| blut/ltzinblut | [AUX, UNKNOWN] | AUX only |
| frosch | [UNKNOWN, LINK] | LINK |

---

## Identification Hypothesis

Based on PP profile matching:

| RI Token | Candidate Animal | Evidence |
|----------|------------------|----------|
| **eoschso** | **ennen (chicken)** | Only record with both ESCAPE and AUX PP |
| teold | scharlach/charlach/milch? | High ESCAPE, no AUX |
| chald | scharlach/charlach/milch? | High ESCAPE, no AUX |
| eyd | blut/ltzinblut? | Weak pattern |

---

## Confidence Assessment

**High confidence**:
- 4 animal RI tokens identified in records converging to chicken-profile B folios
- eoschso uniquely matches chicken's ESCAPE+AUX instruction pattern

**Limitations**:
- Cannot distinguish between animals with same instruction pattern (e.g., scharlach vs charlach vs milch)
- Some animals (harnkrut, nig) have empty instruction sequences - may not be identifiable
- PP convergence is necessary but may not be sufficient for definitive identification

---

## Constraint Implications

This analysis suggests C384 (no entry-level A-B coupling) has nuance:
- Single PP tokens don't discriminate
- Multi-dimensional PP conjunction CAN discriminate at record level
- Instruction pattern matching via PREFIX profile adds discriminative power

Proposed refinement to C384: "Single PP tokens do not establish entry-level coupling, but multi-dimensional PP convergence combined with PREFIX profile matching can identify specific A records."

---

## Files

- `scripts/f95v1_trace.py` - Trace from chicken B folio to A records
- `scripts/animal_pp_detail.py` - PP token detail per animal record
- `scripts/animal_prefix_profile.py` - PREFIX profile scoring
- `scripts/animal_sequences.py` - Brunschwig instruction sequences
