# Phase 656 Stage A — Pre-Registration

**Locked:** 2026-04-26 (commit hash to be recorded post-commit)
**Scope:** Stage A only (corpus extraction). Stage B alignment predictions are NOT in this document.

---

## Empirical pre-survey (NOT a result, just a sanity check)

A regex sweep across all 189 SISMEL subrecipes confirms the connective inventory is non-empty and well-distributed:

| Surface form | Hits | Category |
|---|---:|---|
| `per ço` | 401 | CAUSAL |
| `quant` | 392 | CONDITIONAL_TEMPORAL |
| `aprés` (any spelling) | 232 | TEMPORAL_AFTER |
| `donchs` | 111 | CONSEQUENT |
| `e aprés` | 60 | TEMPORAL_AFTER (sequence-marked) |
| `vegades` | 56 | REPETITION |
| `tro que` | 48 | BOUNDED_DURATION |
| `en tro que` | 47 | BOUNDED_DURATION |
| `donques` | 33 | CONSEQUENT |
| `segons que` | 30 | MANNER |
| `totes vegades` | 27 | REPETITION |
| `altra vegada` | 13 | REPETITION |
| `si donchs/donques` | 10 | CONDITIONAL |
| `lavors` | 8 | CONSEQUENT |
| `adonques` | 8 | CONSEQUENT |
| `fins que` | 8 | BOUNDED_DURATION |
| `en tro tant que` | 4 | BOUNDED_DURATION |
| `en tro a tant que` | 3 | BOUNDED_DURATION |

This sweep is for sample-size confidence only. The survey produces no claim.

---

## Locked decisions (binding)

### 1. Source corpus

- **Input file:** `phases/SISMEL_RECIPE_CORPUS/results/sismel_subrecipes.json`
- **Field:** `catalan` (the Catalan transcription field per subrecipe record)
- **No alternative source.** If the file is incomplete or corrupted, this phase pauses; we do not switch to OCR fallback without a separate methodology amendment.

### 2. Theorica filter (per C1748 / C1932)

- **Include:** part ∈ {`II` (Practica), `III` (Mercuriorum)}
- **Exclude:** part = `I` (Theorica)
- **Rationale:** C1932 — theoretical chapters yield zero atom-validated matches. Per crazy-expert and expert-advisor: Theorica acts as a negative control — connectives there are vocabulary, not procedure.

We DO extract from Theorica into a separate `theorica_negative_control` corpus to enable Stage B comparison, but Theorica instances are tagged with `theorica_control: true` and are not part of the procedural corpus for alignment.

### 3. Text normalization (frozen)

Applied to each `catalan` field before regex matching:

1. **Unicode:** NFC normalize, then strip the spread-marker tokens like `f. 63vb` (regex `f\.\s*\d+[rv][a-z]?`).
2. **OCR garbage strip:** remove sequences of `*` (used as scribal placeholder for damaged chars).
3. **Note marker strip:** remove footnote superscripts `\d+\b` only when adjacent to a recognized footnote-context lexeme — actually NO, we leave them in and rely on regex word boundaries. Decision: do NOT strip footnote marks; they are extraneous to connective matching.
4. **Apostrophe handling:** keep `·` as itself; treat `'`, `'`, `'` as equivalent.
5. **Lowercase:** for matching only (preserve original case in stored context window).
6. **No other normalization.** No spelling regularization. No abbreviation expansion. No accent stripping.

**Rationale:** Pereira-Spaggiari is a critical edition with diplomatic choices already made. Further normalization risks introducing editorial-of-editorial drift.

### 4. Connective taxonomy (frozen — 7 categories)

| Category | Surface forms (regex, IGNORECASE) | Semantic role |
|---|---|---|
| TEMPORAL_AFTER | `\baprés\b`, `\baprès\b`, `\bapres\b`, `\be aprés\b`, `\be après\b`, `\be apres\b`, `\bpuys?\b`, `\bpuis\b` | sequence step boundary |
| BOUNDED_DURATION | `\bfins que\b`, `\btro que\b`, `\ben tro que\b`, `\ben tro tant que\b`, `\ben tro a tant que\b` | until-condition holds |
| CONDITIONAL_TEMPORAL | `\bquant\b`, `\bquan\b` | when/whenever |
| CONDITIONAL_HYPOTHETICAL | `\bsi donchs\b`, `\bsi donques\b`, `\bsi\b(?=\s+\w)` (lookahead, only when followed by word) | if-clause |
| CONSEQUENT | `\blavors\b`, `\badonques\b`, `\bdonchs\b`, `\bdonques\b` | then/therefore |
| CAUSAL | `\bper ço\b`, `\bper co\b`, `\bper ço que\b` | because |
| REPETITION | `\bvegades?\b`, `\baltra vegada\b`, `\baltres vegades\b`, `\btotes vegades\b`, `\btots vegades\b`, `\bnovament\b` | cycle / repeat |
| MANNER | `\bsegons que\b` | according-as |

**Decisions baked in:**

- Standalone `\bsi\b` is included (with word-lookahead) but flagged `weak_si=true` because it is also a conjunction without conditional force ("either ... or"). Stage B alignment must filter on `weak_si=false` for primary tests.
- `puis` and `puys` are TEMPORAL_AFTER (sequence step), distinct from `aprés` only as a separate surface form (logged in the same category).
- `donchs` and `donques` are merged into CONSEQUENT regardless of whether preceded by `si`. The `si donchs` compound is recorded as CONDITIONAL_HYPOTHETICAL only when `si` immediately precedes; standalone `donchs` is CONSEQUENT.

### 5. Per-instance record fields (frozen schema)

Each connective instance produces one record:

```json
{
  "subrecipe_id": "III.19.0",
  "part": "III",
  "chapter_num": 19,
  "sub_idx": 0,
  "label_canonical": "primary",
  "char_offset": 142,
  "phase_ordinal": 1,
  "surface_form": "Aprés",
  "category": "TEMPORAL_AFTER",
  "weak_si": false,
  "context_left": "(60 chars before, original case)",
  "context_right": "(60 chars after, original case)",
  "next_verb_candidate": "metr"
}
```

- **`phase_ordinal`:** sentence index within the subrecipe (count of sentence-terminators `.`, `!`, `?`, `;` preceding `char_offset`). This is the recipe-internal step ordinal.
- **`next_verb_candidate`:** first 4-character infinitive-ending stem (regex `\b\w{3,}(?:ar|er|ir|re)\b`) within 30 chars after the connective. Heuristic only, exposed as descriptive metadata, NOT used in any alignment claim. Future verb-inventory phase will produce the authoritative verb extraction.
- **No editor-introduced features:** `phase_ordinal` is computed from punctuation actually present in the catalan text (transcribed by Pereira). We do not use her chapter-internal numbering, paragraph breaks, or section headings.

### 6. Output products (locked)

| File | Contents |
|---|---|
| `results/CONNECTIVE_CORPUS.json` | List of all instance records + summary block |
| `results/CONNECTIVE_CORPUS_THEORICA.json` | Negative-control records (part=I) |
| `results/CONNECTIVE_INVENTORY.md` | Frequency table by category × part, plus 3 random examples per category for human verification |

### 7. What this phase does NOT do

- **No hypothesis test.** No correlation, no rho, no p-value.
- **No claim of significance** anywhere in Stage A outputs.
- **No constraint registration** (the data is the deliverable).
- **No re-running with revised regexes** unless a documented bug is fixed (commit hash before/after).
- **No comparison to VMS-side data.** That is Stage B.

### 8. Falsifiable corpus-quality bar

Stage A is acceptable iff:
- Total instance count across all categories ≥ 800
- ≥ 3 categories present in ≥ 50% of subrecipes
- Theorica negative-control corpus ≥ 100 instances
- Manual spot-check of 20 random extracted records confirms ≥ 18 are correctly categorized (90%)

If these fail, the regexes need fixing (with diff commit) before proceeding to Stage B.

---

## Open questions deferred to Stage B

These are NOT decided here; they will be locked in a separate Stage B pre-registration before any alignment scoring runs:

- Which Voynich-side structural feature to align with (CTS / forbidden-transition / hazard-class / paragraph break)
- Which folio-recipe pair is primary (f75r ↔ III.19 is the leading candidate, but f76r/f84r are also CONFIRMED)
- Window size for "alignment" (1 line? 1 paragraph? exact char-offset proportional position?)
- Null-distribution construction (random-shuffle which: connective positions or VMS-side boundaries)
- What threshold on aligned positions counts as decipherment-class

---

## Why pre-register Stage A at all

Stage A is corpus extraction, not a hypothesis test. Pre-registration here is methodological hygiene:

- Locks the regex set so Stage B cannot fish for the alignment-friendly subset.
- Locks the Theorica filter so we cannot drop it post-hoc when negative-control noise hurts a desired alignment.
- Locks the recipe-phase ordinal definition so we can't redefine it after seeing where alignments cluster.
- Forces the verb-extraction heuristic to be descriptive metadata, not a load-bearing alignment feature.

Per crazy-expert: lock alignment to features Pereira *transcribed*, not features she *organized*. This pre-registration enforces that constraint at the data-construction layer.
