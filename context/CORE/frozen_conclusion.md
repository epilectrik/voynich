# Frozen Conclusion (Tier 0)

**Status:** FROZEN (restated 2026-09-28 by human sign-off) | **Tier:** 0 | **Scope:** Currier B only

---

## The Core Finding (Tier 0, measurement)

> **Currier B is written in a single, compact token grammar: 49 classes covering 69.5% of its tokens, organised by line
> with positional zones and word-boundary glyph coupling, and applied in folio units that share the grammar while
> carrying their own vocabulary. This structure is not reproduced by copy-and-modify generation or by the Naibbe cipher
> as published.**

Basis: C121, C124 (grammar and its coverage, as corrected); C956, C357 (positional zones and line regularity); C1212, C1563 with
PHASE_761 (boundary coupling, robust to spacing uncertainty and replicated on the ZL transcription); C531, C1790 (folio
units: shared grammar, unique vocabulary); C2077, C2080 (generators excluded).

## Working interpretation (Tier 3 — support withdrawn, not falsified)

> *The grammar is read as a family of closed-loop, kernel-centric control programs.*

This was the Tier-0 sentence until 2026-09-28. It was restated because its supports were found flawed or withdrawn,
not because a discriminating test refuted it:
- **"Kernel-centric"** (C089 k, h, e; C085 primitives; C103–C105 roles): the only documented evidence — an adversarial-audit
  surrogate test — is uninformative. Its pass criterion does not depend on the data (the real corpus fails it too: k ranks
  7th), its first-order Markov null reproduces the bigram counts its "centrality" is computed from (centrality ≈
  frequency), and it counts EVA letters, where "h" is half the bench glyph (PHASE_754). A glyph-level re-test is PHASE_763.
- **"Closed-loop"** (C171): all four remaining legs are withdrawn — monitoring (the 38% LINK figure does not reproduce;
  LINK is a morphological artifact, C609, C1174), intervention by kernel operators (above), hazard avoidance (C783, C2060,
  C2063, C2081) and convergence (no sequential convergence at any scale; MONOSTATE is the most common mode; the completion
  gradient is a section confound — C1401–C1403). Three live results cut against a cycling reading: no cyclic eigenmode
  (C2067), no sequential convergence (C1402), complete paragraph resets (C1834, C1785).
- **What remains of the kernel idea as measurement:** qo-prefixed tokens are rich in the gallows k and ok-prefixed tokens in
  e, and qo tokens alternate with ch/sh tokens beyond line composition (C1313, C549, C2056) — a family preference, not a
  control core.

### History
- Until 2026-09-27: "…encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within
  a narrow viability regime, governed by a single shared grammar."
- 2026-09-28 (morning): "designed to maintain a system within a narrow viability regime" struck (forbidden transitions and
  hazard classes withdrawn).
- 2026-09-28: restated as above after the pillar re-check (expert-advisor and lean-expert reviews agreed; human sign-off).

---

## Key Metrics

| Metric | Value | Note |
|--------|-------|------|
| Instruction classes | 49 | 9.8x compression from 479 token types |
| Grammar coverage | 69.5% of B tokens | 100% of the grammar's own 479/480-type vocabulary; the remaining tokens (HT/UN) are defined by exclusion (C124, C566, C740) |
| Folios | 83 | Each folio uses the shared grammar with its own vocabulary |
| Boundary glyph coupling | 0.228 bits (H), 0.243 (ZL); 0.215 at definite spaces | C1212, C1563; PHASE_761 |
| Positional zone dependence | 0.172 bits beyond shuffle | C956; PHASE_757 |
| Forbidden transitions | none beyond known effects | C783, C2060, C2063, C2081 |
| LINK density | 13.2% | `ol` morphology; a morphological artifact, not a functional layer (C609, C1174) |

---

## Scope Limitation

**This conclusion applies to Currier B only.**

- Currier B = 61.9% of tokens, 83 folios
- Currier A (30.5%) is a different system (categorical registry)
- AZC (7.7%) is a hybrid (diagram annotation)

See [model_boundary.md](model_boundary.md) for complete scope.

---

## What It Rests On

1. **Grammar closure** (Phase 20): 479 token types reduce to 49 classes with 0 loss (C121).
2. **Coverage** (Phase 21): the 49 classes cover the grammar's own vocabulary; that vocabulary is 69.5% of Currier B
   tokens (C124, C566).
3. **Line organisation:** positional zones (C956) and boundary glyph coupling (C1212/C1563; PHASE_761).
4. **Folio units:** every folio uses the same classes with its own vocabulary (C531, C1790).
5. **External generators excluded:** copy-and-modify (C2077); the Naibbe cipher as published (C2080).
Withdrawn from this list on 2026-09-28: forbidden topology (C783, C2081), kernel dominance (C089, flawed test),
convergence as dynamics (C1401–C1403 — the 57.8% STATE-C figure stays as a measurement, C074 at Tier 2).

---

## What This Is NOT

- **NOT a translation** — no token has a demonstrated equivalent in any language (C171 semantic ceiling framing retained
  as a statement about recoverability).
- **NOT natural language written one token per word** (C132, C2015, C2022; the old "0.19% reference rate" is tainted and not
  relied on).
- **NOT a cipher of the classes tested** (token ≈ word codes; atom-level polyalphabetic C1976; three published decipherments
  C2017; the Naibbe verbose homophonic cipher as published, C2080). Other sub-lexical designs remain untested. Excluding a
  rival is not evidence for the working interpretation.
- **NOT illustration-dependent at the grammar level** — swap invariance p = 1.0 (C138/C140, grammar scope).

See [falsifications.md](falsifications.md) for the rejection list.

---

## Purpose Class (Tier 3)

"Continuous closed-loop process control" was the best-supported purpose class among those tested (C171). Only 2 of its 12
eliminations were discriminating tests (NEGATIVE_AUDIT), and its four structural legs are now withdrawn (above). It
remains a working interpretation, not a finding.

---

## Navigation

↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md) | [model_boundary.md](model_boundary.md) →
