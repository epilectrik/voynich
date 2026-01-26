# C598: Cross-Boundary Sub-Group Structure

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Internal sub-group structure is visible across role boundaries. 8/10 cross-role pairs show significant sub-group routing (raw p<0.05), 5/10 survive Bonferroni correction. The strongest signal: FQ_CONN (Class 9) feeds EN_CHSH at 1.41x enrichment but avoids EN_QO at 0.16x — near-total avoidance that holds across all 4 REGIMEs. Sub-groups are not internal curiosities; they participate in cross-role grammar.

---

## Evidence

**Test:** `phases/SUB_ROLE_INTERACTION/scripts/sub_role_transitions.py`

### Cross-Role Pair Significance

| Pair | chi2 | p | Bonferroni | Total Pairs |
|------|------|---|------------|-------------|
| CC->EN | 104.1 | 1.4e-21 | Yes | 347 |
| AX->FQ | 43.9 | 6.7e-9 | Yes | 446 |
| EN->FQ | 25.5 | 4.0e-5 | Yes | 812 |
| FQ->EN | 78.1 | 1.5e-15 | Yes | 770 |
| AX->EN | 23.0 | 1.3e-4 | Yes | 1099 |
| CC->FQ | 16.1 | 2.9e-3 | No | 128 |
| FQ->AX | 11.8 | 1.9e-2 | No | 409 |
| FQ->FL | 7.6 | 2.2e-2 | No | 167 |
| EN->AX | 6.3 | 1.8e-1 | No | 1096 |
| FL->FQ | 0.8 | 6.7e-1 | No | 143 |

### Top Enrichments (n>=5)

| Source | Target | Enrichment | Count |
|--------|--------|------------|-------|
| EN_MINOR | FQ_CONN | 3.82x | 5 |
| CC_OL_D | EN_QO | 2.73x | 54 |
| FQ_CONN | FL_SAFE | 2.09x | 9 |
| CC_OL | FQ_CONN | 1.78x | 17 |
| FQ_CLOSER | AX_INIT | 1.62x | 23 |
| AX_INIT | FQ_CONN | 1.57x | 52 |
| FQ_CONN | EN_CHSH | 1.41x | 125 |

### Top Depletions (n>=5)

| Source | Target | Enrichment | Count |
|--------|--------|------------|-------|
| FQ_CONN | EN_QO | 0.16x | 7 |
| CC_OL | EN_QO | 0.34x | 10 |
| CC_DAIIN | EN_QO | 0.37x | 9 |
| CC_OL_D | EN_CHSH | 0.53x | 38 |

### FQ_CONN->EN Gateway

The or/aiin bigram (C561) almost exclusively connects to ch/sh-prefixed EN tokens:
- FQ_CONN -> EN_CHSH: 125 pairs, 1.41x enrichment
- FQ_CONN -> EN_QO: 7 pairs, 0.16x enrichment (near-zero)
- This holds across all REGIMEs: QO avoidance is 0.00-0.31x in every REGIME

---

## Interpretation

Sub-group structure extends across role boundaries. The grammar is not just "EN follows FQ" — it's "CHSH follows CONNECTOR, not QO." This means the morphological gating (PREFIX selects MIDDLE subvocabulary) has cross-role consequences: different prefix families receive input from different upstream sub-groups.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C550 | Extended - role-level transitions now decomposed to sub-group level |
| C593 | Instantiated - FQ 3-group structure has cross-role consequences |
| C576 | Extended - EN QO/CHSH bifurcation visible in upstream routing |
| C561 | Contextualized - or->aiin bigram feeds CHSH specifically |
| C599 | Related - AX scaffolding also routes by sub-group |
| C600 | Related - CC triggers also route by sub-group |

---

## Provenance

- **Phase:** SUB_ROLE_INTERACTION
- **Date:** 2026-01-26
- **Script:** sub_role_transitions.py

---

## Navigation

<- [C597_fq_class23_boundary_dominance.md](C597_fq_class23_boundary_dominance.md) | [INDEX.md](INDEX.md) ->
