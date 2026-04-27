# Phase 660 — Pre-Registration

**Locked:** 2026-04-26
**Type:** Corpus extraction (no hypothesis test)
**Pattern:** Same as Phase 656 (connective corpus). Locked methodology before extractor runs. No claim of significance produced in Stage A.

---

## Why this exists

Phase 656 built the SISMEL Catalan **connective** corpus (1012 instances of conditional/temporal/causal grammar). The complementary infrastructure piece — the **operator-verb** corpus — is still missing.

The operator-verb inventory is foundational for the next round of cross-folio specific-operation discovery. C1925 (`dar`=material introduction, 6/6 partition) and C1926 (`chekar`=quality check) were both produced by aligning specific Catalan operations to specific VMS token signatures. To replicate this systematically across more matched-pair operations, we need a structured per-instance verb corpus.

Crazy-expert flagged operator-verb inventory as the foundational step before substance-cipher work; expert-advisor noted it as PARTIAL (count statistics in C1056/C1746 exist but per-chapter SISMEL Catalan inventory does not).

---

## What this phase produces

A per-instance JSON corpus of operator-verb occurrences in SISMEL Catalan procedural chapters (parts II + III), with category labels, surface forms, char offsets, and ±60 character context windows. Plus a parallel Theorica negative-control corpus.

**No hypothesis tests.** No correlations, p-values, or claims of significance. The corpus is the deliverable. Future phases (661+) will use it for partition tests.

---

## Locked decisions (binding)

### 1. Source corpus

- **Input:** `phases/SISMEL_RECIPE_CORPUS/results/sismel_subrecipes.json`, field `catalan`
- **Procedural set:** part ∈ {II (Practica), III (Mercuriorum)}
- **Negative control:** part = I (Theorica) — extracted to separate file, tagged

### 2. Verb taxonomy (frozen — 18 categories)

Empirical pre-survey across 89 procedural subrecipes found these verb stems with hit counts; the locked taxonomy below is informed by this survey but does not change with future re-runs.

| Category | Regex pattern | Surface examples | Operational role |
|---|---|---|---|
| MATERIAL_TAKE | `\bpren\w*`, `\bpendr\w*` | pren, pendre, pendràs | take/select material |
| MATERIAL_PLACE | `\bmet\w*\|met-\b`, `\bmit-\b`, `\bmetr\w*` | met, met-la, mit-li, metràs | put/place material |
| MIXTURE | `\bmescl\w*\|mesc\w*\b`, `\bconjun\w*`, `\bajunt\w*`, `\bcompon\w*\|composi\w*\|compóndr\w*` | mescla, mesclat, conjuncció, ajunta, composició | mix/combine |
| ADDITION | `\bajust\w*` | ajusta, ajuste | add to mixture |
| HEAT_APPLY | `\bescalf\w*`, `\bcrem\w*`, `\bcalcin\w*`, `\bbull\w*`, `\bcoc\w*\|cuit\w*\|cou\w*\|coú\b\|coga\w*` | escalfa, crema, calcinar, bullir, coú, cuit | apply heat (cook/calcine/burn) |
| DISTILLATION | `\bdistil\w*\|destil\w*\|destil·l\w*` | distil·la, destil·lar, distillaràs | distill |
| SUBLIMATION | `\bsublim\w*` | sublima, sublimat, sublimaràs | sublime |
| DISSOLUTION | `\bdissol\w*`, `\bdesli\w*\|deslliur\w*` | dissol, dissolvre, deslliurar | dissolve |
| PHASE_FUSE | `\bfond\w*\|fonr\w*`, `\bliquef\w*\|liquefer\w*\|liquefiar\w*`, `\bfos\b\|fus\w*` | fond, liquefactió, liquefer, fos | melt/fuse/liquefy |
| PHASE_FIX | `\bcongel\w*`, `\bcoagul\w*`, `\bfix\w*\|fixar\w*` | congelar, coagular, fixar | coagulate/fix/freeze |
| SEPARATION | `\bsepar\w*`, `\bfiltr\w*`, `\bparteix\w*\|parti\w*` | separar, filtrar, partir, parteix | separate |
| PUTREFACTION | `\bputref\w*\|putrif\w*\|pudr\w*`, `\bmacer\w*`, `\bdigest\w*\|digeri\w*\|digerir\w*` | putrefer, putrifició, macerar, digerir, digestió | putrefy/macerate/digest |
| REFINEMENT | `\brectif\w*`, `\bmundif\w*\|purif\w*\|depur\w*`, `\blimp\w*\|net\w*` | rectifica, mundificar, purificar, depura, netejar | refine/purify |
| MULTIPLICATION | `\bmultipl\w*`, `\baugme\w*`, `\bcrei[xs]\w*` | multiplica, multipla, augmenta, creixer | multiply/augment |
| IMBIBITION | `\benbeu\w*\|enbev\w*\|imbib\w*`, `\buntar\w*\|untu\w*`, `\blav\w*\|banya\w*` | enbeure, enbevent, imbibició, untar, lava, banyar | imbibe/oint/wash |
| CONTAINMENT | `\btap\w*\|cobr\w*\|cubr\w*`, `\bsegell\w*`, `\bsoter\w*\|enterr\w*` | tapa, cobreix, segella, soterrar | seal/cover/bury |
| OBSERVATION | `\bguard\w*`, `\bveur\w*\|mira\w*\|veg\w*`, `\bsent\w*` | guarda, veuràs, mira, sentir | watch/observe/note |
| QUALITY_TEST | `\bprov\w*`, `\bexamin\w*`, `\bgust\w*` | prova, examina, gusta | taste/test/verify |

**Decisions:**

- `fix\w*` is included in PHASE_FIX even though it could match `fixació` (state) and `fixa-la` (action). The pre-survey shows 83 hits; manual spot-check is required to confirm operational interpretation.
- `met` (and variants) is heavily polysemous in Catalan — also "between" / "amid". The leading regex `\bmet\w*` will produce false positives. Mitigation: spot-check during inventory MD generation.
- `pren` similarly polysemous (could be 3rd-person reflexive). Mitigation: same as `met`.
- `guarda` is OBSERVATION here, but in some contexts means "keep/store" (containment). The category is the dominant operational reading; edge cases flagged in spot-check.
- `cou` / `coú` (cook) — included with `\bcoc\w*\|cuit\w*\|cou\w*\|coú\b\|coga\w*` to catch Catalan cooking conjugations. The regex is broad on purpose.
- ITERATION verbs (reiterar, repetir, tornar) are NOT included as a separate category. Repetition is captured by Phase 656's REPETITION connective category. Including verbs of iteration here would double-count.

### 3. Text normalization

Identical to Phase 656 (NFC unicode, strip folio markers, strip OCR `*` placeholders, normalize smart apostrophes). No spelling regularization. No abbreviation expansion. Lowercase for matching only; preserve original case in stored context.

### 4. Per-instance record schema

```json
{
  "subrecipe_id": "III.19.0",
  "part": "III",
  "chapter_num": 19,
  "sub_idx": 0,
  "label_canonical": "primary",
  "char_offset": 142,
  "phase_ordinal": 1,
  "surface_form": "Pren",
  "category": "MATERIAL_TAKE",
  "context_left": "(60 chars before, original case)",
  "context_right": "(60 chars after, original case)"
}
```

`phase_ordinal` is identical to Phase 656's definition: count of sentence-terminators (`.`, `!`, `?`, `;`) preceding `char_offset`. Recipe-internal step ordinal.

### 5. Output products

| File | Contents |
|---|---|
| `results/VERB_CORPUS.json` | All instances (parts II + III) + summary block |
| `results/VERB_CORPUS_THEORICA.json` | Negative-control records (part I) |
| `results/VERB_INVENTORY.md` | Frequency table + 3 random examples per category for human spot-check |

### 6. Pre-registered corpus-quality bar

Stage A is acceptable iff:
- Total instance count across all categories ≥ 2,000
- ≥ 5 categories present in ≥ 50% of subrecipes
- Theorica negative-control corpus ≥ 200 instances
- Manual 30-record spot-check (selected randomly across categories): ≥ 27/30 categorized correctly (90%)

If the bar fails, regex must be fixed (with documented bug fix and commit-hash diff) before phase completes.

### 7. Non-overlap matching strategy

Same as Phase 656: longer/more-specific patterns matched first; matched character spans are masked so subsequent patterns cannot re-match. Order in the taxonomy table is the matching order.

### 8. What this phase does NOT do

- No alignment with VMS-side data.
- No correlation tests, no rho, no p-values.
- No claim that any verb category corresponds to any specific VMS token or atom.
- No constraint registration.
- No mapping to Latin (Catalan-only).
- No expansion to non-procedural verbs (auxiliary, copular, etc.).
- No re-running with revised regex unless documented bug is fixed.

### 9. Stopping rules

- One commit for pre-registration (this document).
- One commit for extractor + outputs.
- Stage A complete when corpus-quality bar passes; no further iteration.

---

## Honest expectation

The empirical pre-survey suggests ~2,500-3,500 procedural verb instances. ~5-7 categories should easily clear 50% subrecipe coverage (MATERIAL_TAKE, MATERIAL_PLACE, MIXTURE, HEAT_APPLY, DISTILLATION are likely all >50%).

False positives from polysemous stems (`met`, `pren`, `fix`) will reduce real count by some fraction. The spot-check is the methodology's quality gate — if more than 10% of randomly-selected records are mis-categorized, the regex needs fixing.

The corpus is data infrastructure for Phase 661+. By itself it produces no findings.

---

## What follows (NOT committed in this phase)

- **Phase 661 candidate:** Cross-folio partition test for one or more high-frequency operator-verb categories. Hypothesis: a Catalan recipe carrying a specific operator-verb category corresponds to a specific VMS token signature on its matched folio (replicating C1925's methodology). Requires its own pre-registration.

- **Phase 662 candidate:** Verb-category co-occurrence analysis — which categories cluster together in recipes? May identify operational signatures (e.g., "putrefaction recipes always pair with sealing" or "distillation recipes always pair with material take").

These are notes, not commitments.
