# C1131: Ring Text Register Classification — BRIDGE_VOCABULARY_INDEX

**Tier:** 2
**Status:** Active
**Scope:** Rosettes foldout — ring text
**Phase:** 404 (RING_TEXT_REGISTER_CHARACTERIZATION)

## Finding

Ring text on the Rosettes foldout constitutes a **bridge vocabulary index register** — a text type that specifically samples B-grammar bridge vocabulary under B's hard constraints, functioning as a cross-system vocabulary reference rather than executable program or AZC-style label.

### Evidence

**Instruction class structure (not flat, not random):**
- 150/286 ring tokens (52.4%) map to the 479 B-grammar types
- 33 of 49 instruction classes used
- JS(ring, uniform) = 0.291 — structured, not random enumeration
- JS(ring, B body) = 0.271 — different from B body distribution
- AUXILIARY role: 42.7% (B: 25.4%) — structural vocabulary enriched
- ENERGY_OPERATOR: 11.3% (B: 45.8%) — execution vocabulary depleted

**Bridge enrichment:**
- 32.1% of ring MIDDLEs are bridge (vs non-ring 25.5%, B bootstrap p95 = 11.0%)
- 100th percentile of B vocabulary bootstrap (N=5000)
- 100% of classified (B-grammar) ring MIDDLEs are bridge
- Ring text is MORE bridge-enriched than non-ring rosettes entities

**Not a program (from C1130):**
- 0/277 forbidden transition violations (hard constraints respected)
- Transition entropy 7.92 bits (vs B's ~0.41) — soft constraints ignored
- No positional gradient: kernel 34%→40% (first→second half), PREFIX cosine 0.97
- Self-transition rate 2.89% — no sequential structure

**Not an AZC label:**
- Kernel density 37.06% (AZC per C757: 0% kernel role tokens)
- LINK density 4.20% (AZC per C757: 0%)
- Grammar coverage 52.4% (labels: 21-26%)

### Verdict Discrimination

| Candidate | Status | Reason |
|-----------|--------|--------|
| CONSTRAINED_ENUMERATION | Rejected | JS(uniform) = 0.291 >> 0.1 threshold |
| AZC_LABEL_REGISTER | Rejected | Kernel 37%, LINK 4.2% (vs AZC: 0%, 0%) |
| DEGRADED_PROGRAM | Rejected | Entropy 7.92 bits (vs B ~0.41), no positional structure |
| BRIDGE_VOCABULARY_INDEX | **Accepted** | Structured classes + elevated bridge + 100% classified bridge |

## Implication

Ring text is a distinct register that catalogues B-grammar bridge vocabulary — the vocabulary that mediates between Currier A and B systems. It lists these terms under B's hard grammatical constraints (forbidden transitions respected) but without B's sequential execution logic (random transition order). This is consistent with the metalayer interpretation (C1126): the Rosettes foldout serves as a reference map for cross-system vocabulary.

## Provenance

- Source: Phase 404, Tests A1-A4, B1-B4, C1-C4 (12-test battery)
- Related: C1130 (forbidden compliance), C1126 (metalayer), C1127 (AZC-like grammar), C1124 (bridge enrichment)
