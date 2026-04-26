# Phase 657 — Pre-Registration

**Locked:** 2026-04-26 (commit hash to be recorded post-commit)
**Type:** Confirmatory hypothesis test
**Reason for pre-registration:** Stage B of Catalan utilization. Methodology locked before extraction or test execution to prevent post-hoc parameter selection.

---

## Hypothesis

**H:** SISMEL Catalan REPETITION connectives with explicit numerical counts (`per quatre vegades`, `per .iii. vegades`, etc.) correspond to homogeneous token-class clusters of the same size on their matched Voynich folio at higher rate than random folio assignment.

**H₀ (null):** Numerical cycle-count correspondence is independent of the recipe-folio match (random chance).

**Falsifiable:** If matched-pair correspondence proportion does not exceed the 95th percentile of the null distribution, the alignment claim is rejected.

---

## Locked decisions (binding)

### 1. Catalan numerical-count extraction (locked)

Source: `phases/PHASE_656_CATALAN_CONNECTIVE_CORPUS/results/CONNECTIVE_CORPUS.json` (procedural corpus only — Theorica excluded per C1748/C1932).

For each REPETITION-category instance, search the **last 30 characters of `context_left`** for an adjacent numerical modifier:

| Pattern | Example | Action |
|---|---|---|
| Roman numeral `\b\.?\s*([ivxlcdm]+)\.?\s*$` | `.iii.` | Convert to integer (i=1, v=5, x=10, l=50, etc.) |
| Catalan number word `\b(una\|dos\|dues\|tres\|quatre\|cinch\|cinc\|sis\|set\|huit\|nou\|deu\|onze\|dotze)\s*$` | `quatre` | Map to integer (1-12) |
| Arabic digits `\b(\d+)\s*$` | `7` | Convert to integer |

Number-word map (locked):
```
una/un=1, dos/dues=2, tres=3, quatre=4, cinch/cinc=5, sis=6,
set=7, huit/vuit=8, nou=9, deu=10, onze=11, dotze=12
```

**Inclusion bar:** N >= 3. Counts of 1 ("una vegada") and 2 are excluded (too small to form a structurally distinguishable cluster).

**Pre-survey result (informational, NOT binding):** 10 REPETITION instances carry adjacent numerical counts; of those, 7 have N >= 3:

| Subrecipe | Count | Match status |
|---|---:|---|
| III.19.0 | 4 | matched -> f75r (CONFIRMED) |
| III.19.0 | 9 | matched -> f75r (CONFIRMED) |
| III.11.0 | 3 | matched -> f112r (Supported) |
| II.17.0 | 7 | unmatched (negative control) |
| II.20.0 | 3 | unmatched (negative control) |
| III.17.0 | 5 | unmatched (negative control; "v o vi" — recorded as 5) |
| III.17.0 | 6 | unmatched (negative control; recorded as 6) |

Two distinct counts on III.19.0 (4 and 9) are recorded as two separate
test items.

### 2. VMS cycle-cluster enumeration (locked)

For every Currier B folio (all 83), enumerate **homogeneous prefix-class clusters**:

**Definition:** A cluster of size N is a maximal consecutive run of N tokens within a single line OR spanning at most one line break, where every token shares the same prefix-class.

**Prefix-class set (locked, exhaustive):**
- `qo` (THERMAL)
- `ot` (TRANSFER-INTO)
- `ok` (VESSEL)
- `ol` (CONTINUE)
- `or` (FLOW)
- `ch` (TEST)
- `sh` (MONITOR)
- `da` (SETUP)
- `qok` (compound — counted both as `qo` and as a separate `qok` class for matching)
- `qot` (compound — counted both as `qo` and `qot`)

**Why include compound classes:** The f75r ×4 anchor is `qokedy qokedy qokedy qokedy` (all share `qok` prefix). At the bare `qo` resolution, this is part of a longer run of qo-tokens but might not form a tight cluster. At `qok` resolution it is exact.

**Implementation:** For each folio, for each prefix in {qo, ot, ok, ol, or, ch, sh, da, qok, qot}, scan the linear token sequence (per line, allowing 1-line-break span) and emit every maximal run of length >= 3.

**Output: VMS_CYCLE_CLUSTERS.json** with schema:
```json
{
  "f75r": {
    "qok": [{"size": 4, "line_start": 13, "line_end": 13, "tokens": [...]},
            {"size": 9, "line_start": 37, "line_end": 38, "tokens": [...]}],
    "qo":  [...],
    ...
  }
}
```

This file is the locked VMS-side input. **It is computed once, before any matched-pair scoring runs.** Any subsequent extraction with revised parameters requires a documented bug fix and a commit-hash diff.

### 3. Matched-pair table (locked)

The matched pairs used for scoring are the 15 from Phase 636 plan (in
project memory), reproduced here for binding:

| Folio | Catalan chapter | Tier |
|---|---|---|
| f75r | III.19 | CONFIRMED |
| f76r | II.18 | CONFIRMED |
| f84r | II.14 | CONFIRMED |
| f79r | III.12 | strong |
| f82r | III.22 (or III.19.3 per remap) | strong |
| f103r | III.16 | strong |
| f76v | III.15 | strong |
| f77v | III.27 | supported |
| f81v | III.18 | supported |
| f82v | III.28 | supported |
| f112r | III.11 | supported |
| f112v | III.1 | supported |
| f116r | III.4 | supported |
| f107r | III.44 | supported |
| f80r | III.21-25 (multi-chapter) | supported |

Catalan chapter mapping uses the SISMEL canonical numbering (per
project_chapter_numbering_remap memory note).

### 4. Test statistic (locked)

Define a "match" between a Catalan numerical anchor (subrecipe S, count N)
and its assigned folio F as:

> **The folio F contains at least one cycle-cluster of size N for any
> prefix-class p in the locked prefix-class set.**

Tolerance: exact size match. No fuzzy matching ("cluster size 4 vs target 5"
does not count). The pre-registration explicitly forbids fuzzy size
matching.

**Observed statistic:** Number of matches across all in-set test items.

**Test item set:**
- Primary set (matched): 3 items — III.19.0/×4 -> f75r, III.19.0/×9 -> f75r,
  III.11.0/×3 -> f112r.
- Negative-control set (unmatched): 4 items — II.17.0/×7, II.20.0/×3,
  III.17.0/×5, III.17.0/×6.

For negative-control items, the assigned "folio" is **the corresponding
matched chapter's folio if such mapping is later established, OR the
all-folios-search result** (does any Currier B folio contain a cluster of
size N?). Negative controls are NOT folio-specific — they only test
whether the cluster size exists somewhere in the Currier B corpus.

### 5. Null distribution (locked)

For the matched primary set:
1. Take the 3 matched test items (III.19.0/×4, III.19.0/×9, III.11.0/×3).
2. For each, randomly reassign the matching to one of the other 82 Currier B folios
   (uniform random, without replacement when multiple items in the same
   recipe go together).
3. For III.19.0's two anchors, the random reassignment treats them as a
   pair (both ×4 and ×9 land on the same randomly-chosen folio, since
   they're in the same Catalan subrecipe). This preserves the within-recipe
   anchor pairing.
4. Recompute number of matches.
5. Repeat 10,000 times.

**p-value (one-sided):** Fraction of null trials with matches >= observed.

### 6. Verdicts (locked)

| Verdict | Criterion |
|---|---|
| **SUPPORTED** | Observed matches >= 2/3 AND null p <= 0.05 |
| **DIRECTIONAL** | Observed matches >= 1/3 AND null p <= 0.20 |
| **INCONCLUSIVE** | Observed matches >= 1/3 AND null p > 0.20 |
| **FALSIFIED** | Observed matches = 0/3 |

### 7. Negative-control interpretation (locked)

For each unmatched numerical-anchor item (II.17.0/×7, II.20.0/×3,
III.17.0/×5, III.17.0/×6), report:
- Which Currier B folios (if any) contain a cycle-cluster of that size
- The total count across all 83 folios

**Interpretation rules (locked):**
- A negative-control count N **must** appear on at least 1 folio for the
  test to be informative (else the cluster size is corpus-impossible and
  the matched test is trivially non-specific).
- If a negative-control N matches >50% of folios, the cluster size is
  trivial and the matched test is degraded to FALSIFIED-by-triviality
  for that count.
- These rules apply per-count.

### 8. Single-folio over-determination check (locked)

After the cross-folio test, perform a separate confirmation for f75r alone:

**Q:** Is f75r the only Currier B folio with BOTH a `qok`-cluster of size
exactly 4 AND a `qok`-cluster of size exactly 9?

If YES, the f75r ↔ III.19.0 dual-anchor specificity is exact. Combined
with the pre-existing 5 independent confirmations (8D distance, ×4, ×9,
P9 alternation, atom predictions), this becomes the 6th independent
structural confirmation.

If NO (other folios also have both clusters), the dual-anchor specificity
is degraded; the f75r match retains its prior 5 confirmations but the
Stage B contribution is reduced.

### 9. What this phase does NOT do

- No tweaking the prefix-class set after seeing results.
- No relaxing the exact-size-match rule to fuzzy matching.
- No expanding the matched-pair table to find additional alignments.
- No re-running with revised regexes unless a documented bug is fixed
  (commit-hash diff required).
- No claims about Catalan-side ordering, position, or paragraph structure.
  These are deferred to future phases.

### 10. Methodology guardrails carried over from Phase 656 expert consultation

1. No post-hoc atom-glossing (Phase 653 lesson). The cluster-size match
   is purely structural; no semantic claim.
2. No substring-vs-morphological resolution drift (Phase 654 lesson). The
   cluster definition uses canonical prefix extraction via `voynich.Morphology`,
   not substring matching.
3. Theorica filter applied: the Catalan numerical-anchor inventory is
   sourced from CONNECTIVE_CORPUS.json (procedural only), not the
   negative-control corpus.
4. Editor-introduced features avoided: cluster boundaries are defined by
   manuscript line breaks (transcription artifacts of the Voynich, not
   Pereira), and Catalan numerical extraction works on the diplomatic
   Catalan transcription.

---

## Stopping rules

- **No test set expansion** after running. If we want additional anchor
  extractions (e.g., temporal durations like "per .iii. dies"), they go
  in a follow-up pre-registration.
- **No threshold relaxation.** If observed matches < 1/3 the test is
  null; we do not loosen the cluster definition or include fuzzy matches.
- **One commit per stage.** s1 (Catalan extraction), s2 (VMS clusters),
  s3 (specificity test) each commit independently with their JSON output,
  before moving to the next.

---

## Honest expectation

The primary set is small (3 items). Even a perfect 3/3 match has a
ceiling p-value bounded by the null distribution shape — if random
folios commonly contain clusters of these sizes, the p-value will be
high regardless of observed matches.

The pre-registered negative-control checks (section 7) discipline the
interpretation: if cluster sizes 3, 4, and 9 are common across the
Currier B corpus, the matched-pair test loses specificity and the
verdict drops to DIRECTIONAL or INCONCLUSIVE.

The over-determination check (section 8) is the strongest possible
single-folio confirmation: f75r being unique in containing both ×4 and
×9 qok-clusters would be a categorical, not statistical, finding.

If the test returns null, that is informative: it means the dual-anchor
match on f75r is a structural coincidence at the cluster-size level,
and the existing 5 confirmations carry the f75r ↔ III.19 claim alone.
