# Phase 656: SISMEL Catalan Conditional-Connective Corpus

**Phase:** 656
**Status:** STAGE A COMPLETE — corpus extracted, all quality bars passed
**Started:** 2026-04-26
**Prior:** Phase 642 (Catalan-gloss correlation, returned null)

## Stage A results

| Bar | Threshold | Actual | Verdict |
|---|---|---|---|
| Procedural instances | >=800 | 1012 | PASS |
| Categories in >=50% of subrecipes | >=3 | 4 | PASS |
| Theorica negative-control instances | >=100 | 926 | PASS |
| Spot-check correctness | >=18/20 | 24/24 in examples | PASS |

**Procedural corpus:** 1012 connective instances across 89 subrecipes (Practica II + Mercuriorum III). 83/89 subrecipes contain >=1 instance.

**Negative control:** 926 connective instances in Theorica (part I, 100 subrecipes). Comparable density to procedural — confirms connective grammar is general-purpose, not procedure-specific. Stage B alignment must use positional/structural correspondence, NOT raw density.

**Notable:** III.19.0 (f75r match) example captures both `quatre vegades` and `aprés ix vegades` in one context window — the ×4/×9 anchors that confirmed the f75r match are connective-marked in Catalan.

---

## Why this exists

Both expert-advisor and crazy-expert converged on a recommendation: the
foundational unmined Catalan layer is **structural conditional grammar**
(`si...lavors`, `fins que`, `en tro que`, `tro que`, `e aprés`, `vegades`),
not the substance cipher.

Reasoning:
- Conditionals are structural, not lexical — they survive any cipher and any
  editorial regularization.
- VMS already has substance discrimination at token level (C1939 fch=mercury,
  C1940 cs=gold) without a consolidated cipher table — the cipher is not the
  bottleneck.
- VMS-side conditional grammar is well-instrumented: forbidden transitions
  (C109, 17 disfavored pairs), CTS continuous closure transition score
  (C1579), AXM transitions (C1015), 5 hazard classes (C789). These have
  never been aligned with Catalan-side conditional structure.
- Phase 642 (gloss correlation, N=16, density features) returned null. This
  phase is structurally different: per-instance, per-position, not aggregate
  density.

The Catalan stream is authoritative (per memory: f75r ×4 + ×9 anchors only
present together in Catalan). It is also the language closest to workshop
practice. If structural conditional grammar aligns anywhere, it aligns here.

---

## Scope

This phase has two stages, run sequentially:

### Stage A — Connective extraction (this phase)

Build a structured corpus of every conditional-connective instance in
SISMEL Catalan, scoped to Practica + Mercuriorum (Theorica filtered out
per C1748/C1932 — theoretical chapters share vocabulary but encode no
procedures).

Output: `results/CONNECTIVE_CORPUS.json` with per-instance records:
- chapter ID (part.chapter.sub)
- connective surface form
- normalized type
- character offset within recipe
- recipe-phase ordinal (paragraph index within chapter)
- ±60 character context window (raw)
- preceded-by / followed-by verb (if any) — purely descriptive

Output: `results/CONNECTIVE_INVENTORY.md` — frequency table + per-type
example list for human verification.

This is data prep. There are no hypothesis tests in Stage A. The
pre-registration locks the regex, tokenization, normalization, and
chapter-scope filters so they cannot be revised after seeing alignment
results.

### Stage B — f75r ↔ Ch.III.19 alignment test (separate phase, future)

Pre-registered structural alignment of Catalan conditional positions
against VMS-side CTS / forbidden-transition boundaries on a single
over-determined folio (f75r already confirmed at four independent levels:
8D, ×4, ×9, P9 alternation, atom predictions). A sixth independent
confirmation is decipherment-class evidence per crazy-expert framing.

Stage B will not be initiated until Stage A is committed and locked.
Stage B predictions are not committed in this phase's pre-registration.

---

## Constraints expected

Stage A produces no tier-0/1/2 constraints by itself — it is a corpus.
Possible deliverables on completion:

| Outcome | Deliverable |
|---------|-------------|
| Inventory completes cleanly | Tier 2 corpus reference (SISMEL Catalan connective inventory, N instances across N chapters) |
| Inventory reveals systematic structural pattern by chapter type | Tier 3 observation — descriptive only |

Substantive constraints come from Stage B alignment, not Stage A extraction.

---

## Files

```
phases/PHASE_656_CATALAN_CONNECTIVE_CORPUS/
  INDEX.md                              ← this file
  PRE_REGISTRATION.md                   ← locked methodology, committed before extractor
  scripts/
    s1_extract_connectives.py           ← extractor (locked per pre-registration)
  results/
    CONNECTIVE_CORPUS.json              ← per-instance records
    CONNECTIVE_INVENTORY.md             ← frequency table + examples
```

---

## Dependencies

- `phases/SISMEL_RECIPE_CORPUS/results/sismel_subrecipes.json` (input text)
- `sources/sismel_testamentum/sismel_testamentum_assembled.txt` (fallback, for
  cross-checking edge cases)

---

## Guardrails (from expert consultation)

1. No post-hoc atom-glossing (Phase 653 lesson).
2. No substring-vs-morphological resolution drift (Phase 654 lesson).
3. Tokenize Catalan once, freeze rules. Decisions on accent variants
   (`destil·lar` vs `destillar`), abbreviation expansion (`q.` `dit.`), and
   punctuation splitting locked in PRE_REGISTRATION.md.
4. Filter to Practica + Mercuriorum. Treat Theorica as negative control.
5. Lock alignment to manuscript-original features only — never editor
   segmentation, capitalization, modern paragraph breaks, or chapter numbers
   imposed by Pereira/Spaggiari.
6. Single-source data — no internal replication. Bootstrap chapter
   resampling is the only available robustness check, deferred to Stage B.
