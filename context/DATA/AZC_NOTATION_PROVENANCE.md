# AZC Notation Provenance

**Layer:** DATA (data-integrity / how-to-read-the-source). **NOT a structural contract**
(it asserts no legality) and **NOT a constraint** (it records nothing testable about the
manuscript's content). It documents how the AZC diagram text is recorded across three
representations, where information is lost between them, and which physical-layout facts
are verified vs. unverified — so that AZC analyses stop inheriting the errors that the
collapsed `placement` codes invite.

**Created:** 2026-06-01, from manual inspection of the IVTFF primary source.
**Companion docs:** `TRANSCRIPT_ARCHITECTURE.md` (full transcript), `ROSETTES_DATA_ARCHITECTURE.md` (f85/f86 foldout).
**Scope note:** "AZC" = sections A/Z/C — the astronomical/zodiac/cosmological diagram pages
(`language=NA` in the parsed transcript; ~3,299 H-track tokens, per CLAUDE.md canonical counts).

---

## 1. Three representations, decreasing information

| Layer | File | Carries | Loses |
|-------|------|---------|-------|
| **Parsed TSV** | `data/transcriptions/interlinear_full_words.txt` | one row/token; `placement` ∈ {P,L,R,S,C,W,X,Y} | reading order, locus subtype, ink, transcriber prose |
| **IVTFF source** | `data/transcriptions/reference/ZL_official.txt` | `#` transcriber notes; locus subtypes (`@P0 @L0 @Ro @Ri @Cc @Pb @Ls …`); `<!HH:MM>` clock positions; `[a:b]` alternates | — (richest layer) |
| **Layout maps** | `data/folio_annotations/azc/*.md`,`.json` | per-folio hand-verified layer assignment + ASCII diagram | only as reliable as the verification date (see §4) |

**Rule of thumb:** drive AZC analysis off the IVTFF loci + per-folio note. The TSV
`placement` column is a *lossy projection* of the IVTFF, and (§2) the projection is not
letter-preserving.

---

## 2. The TSV `placement` letter does NOT track the IVTFF locus letter  — VERIFIED FACT

This is the single most error-prone fact about AZC data. The parse remaps IVTFF loci to
placement letters by **physical role, not by locus name**, and one IVTFF locus can map to
two different placements. Worked example, **f69r** (IVTFF lines 3283–3346; TSV H-track
counts confirmed 2026-06-01):

| IVTFF locus | transcriber description | tokens | → TSV `placement` |
|-------------|-------------------------|--------|-------------------|
| `@P0` | normal paragraph above diagram | 36 | **P** |
| `@L0` (block 1) | "Large circle divided into 16 segments" | 43 | **C** |
| `@Ro` | "Radiating lines on 'organ pipes'" (22 radii) | 68 | **R** |
| `@Cc` | "Small circle, using small gap as start point" | 11 | **S** |
| `@L0` (block 2) | "In the centre…" (6 single chars) | 6 | **W** |

Note the two traps: **(a)** the locus named `@Cc` ("circle, continuous") became placement
**S**, *not* C; **(b)** `@L0` is reused for both the outer segmented ring (→C) and the
centre characters (→W), disambiguated only by position/order in the file. Anyone equating
"placement C" with "the @Cc locus," or treating placement letters as stable across folios,
will mis-assign rings. **The placement letter is a parse artifact; the locus + prose is ground truth.**

---

## 3. Locus subtypes present in the AZC source — VERIFIED FACT (collapsed in the TSV)

Observed across f57v, f67r1, f67r2, f68r1, f69r, zodiac folios:

| IVTFF locus | meaning | typical TSV collapse |
|-------------|---------|----------------------|
| `@P0`,`+P0` | paragraph / continuation line | P |
| `@L0`,`&L0` | labels, scattered writing, ring **segments**, centre chars | L / C / W (by role) |
| `@Ro`,`@Ri` | radial text ("radii", "organ pipes"); `<!HH:MM>` gives angular position | R |
| `@Cc`,`+Cc` | continuous circle/ring text | C or S (by role) |
| `@Pb` | **blocked** sector paragraph (e.g. f67r2 12-sector headings) | P |
| `@Ls` | inner star-point words (e.g. f67r2 "8 words around an 8-point star") | S / L |

Granularity that exists in the source but is **absent from the TSV**: continuous-vs-segmented
ring, radius-vs-ring, blocked-heading-vs-body, star-word-vs-ring-word. Any claim that needs
these distinctions must read the IVTFF, not the `placement` column. (C759 — position↔vocabulary,
Tier 2 — was computed on the *collapsed* R/S/C buckets; it holds at that coarse granularity and
says nothing finer.)

---

## 4. Physical ring position — VERIFIED on f69r ONLY

| Folio | C | S | basis | confidence |
|-------|---|---|-------|-----------|
| **f69r** | **OUTER** (43 tok, 16-seg "large circle") | **INNER** (11 tok, continuous "small circle") | IVTFF lines 3294 ("Large circle…16 segments") + 3338 ("Small circle…") | **VERIFIED** (resolved 2026-06-01) |
| all others | — | — | not verified against images | **UNVERIFIED** |

The abstract functional model (`positions.json`: C = Entry/outer, S = Boundary/inner)
*happens to match* f69r physically. This is **not confirmed for any other folio** — do not
assume it generalizes.

> **Swap history (resolved):** `currier_AZC.md` (C=outer) and `azc/f69r.md` (S=outer)
> contradicted each other until 2026-06-01. The IVTFF primary source settles it for
> `currier_AZC.md` (large=outer ⇒ C=outer); `f69r.md` was corrected. `currier_AZC.md:323`
> still warns that other, un-reconciled `azc/` annotations "may have S/C swapped" — that
> warning stands for every folio except f69r.

---

## 5. Reading order is per-folio geometric, NOT line-number order — VERIFIED FACT

`line_number` in the TSV is file order, **not** the manuscript reading sequence. The IVTFF
records the actual order per folio, usually as a clock-position start + direction:

| Folio | reading-order note (IVTFF line) |
|-------|-------------------------------|
| f57v | outer word "possibly meaning 'start here'"; 8 inner labels numbered cf. Petersen (2515–2516) |
| f67r1 | "Radii … clockwise, starting from the North" (2833) |
| f67r2 | sectors "first = 09:00 to 10:00 and further clockwise", Petersen numbering (2855); "At NW … a line that marks the start of text (?)" (2862) |
| f68r1 | "Radiating from central Sun, clockwise, starting at 09:30" (3032) |
| f69r | radii carry `<!HH:MM>`; "start presumably at 02:00", direction CW-vs-CCW **uncertain** (3313–3314); small-circle start = "small gap" (3338); a "start indicator" segment near 02:30 (3324) |
| f70v2-ish | "Radiating text, clockwise, starting at 00:30" (3246) |

The `<!HH:MM>` comment on each `@Ro`/`@Ri`/label line is the angular position — that, plus the
per-folio start + direction, reconstructs reading order. **Never reorder AZC tokens by `line_number` alone.**

---

## 6. Ring numbering is per-folio inconsistent — DOCUMENTED CAVEAT

Transcribers numbered rings from wherever they began reading; the direction is **not** a convention:

- f67r1: "Rings numbered C1 to C3, **outer to inner**" (2829)
- a 4-ring folio: "circles of text (C1 to C4 **outer to inner**)" (3426)
- zodiac nymph folios: rings counted "**inner to outer** (cf. Petersen)" (3699, 3746, 3792)
- zodiac R-subscripts flip too (`currier_AZC.md:312`): f70v2 R3=outermost; f72r1/f71r/f73r R1=outermost

**Implication:** any analysis assuming a fixed R1/R2/R3 or C1/C2/C3 → physical-position mapping
across folios may have ordering errors. Per-folio verification required (C456 interleaved-spiral
topology, Tier 2, is the validated structural claim about AZC ring/spoke alternation; C455 simple-cycle
topology is FALSIFIED, Tier 1).

---

## 7. Cues lost entirely in the TSV — VERIFIED FACT

- **Red ink** marks distinct structural layers: f67r2 "outer circle in red ink, 12 pieces of
  scattered writing in red ink" (2853, 2866); a red single line elsewhere (2943). The TSV has no ink column.
- **Blocked sector headings** (`@Pb`): f67r2 sector paragraphs start with a blocked heading; the
  TSV flattens these to ordinary P tokens.
- **"Start here" / start markers** (physical): f57v word, f67r2 NW line, f69r gap + 02:30 segment.

---

## 8. Confidence ledger (read before citing anything above)

| Tier | Items |
|------|-------|
| **VERIFIED FACT** | §2 placement≠locus remap; §3 locus subtypes exist & are collapsed; §5 reading order is geometric; §7 red-ink/blocked/start cues exist; **f69r C=outer/S=inner** |
| **DOCUMENTED CAVEAT** | §4 position unverified off f69r; §6 numbering inconsistent; S/C-swap risk in un-reconciled `azc/` annotations |
| **TIER 3+ — deliberately EXCLUDED** | what the rings/sectors *represent*; celestial-object IDs; semantics of "start here"; physical grounding of the C=Entry/S=Boundary functional model beyond f69r (per `currier_AZC.md:286–290`) |

## 9. Known un-resolved annotation discrepancy (flagged, not fixed here)

f69r centre chars (`W`): `azc/f69r.md` lists `d,o,l,s,em,y`; the IVTFF gives, in Petersen order,
`y(1) d(2) o(3) l(4) s(5) e[d:g](6)` (3341–3346) — order differs and char 6 is `e[d:g]` (alternate
reading), not `em`. The "dolsemy" word-reading in f69r.md is therefore not supported by the source as
written. This is a *reading* discrepancy (not a position swap) and is left open.

---

## 10. Nested concentric rings serialize as depth-ordered blocks — VERIFIED FACT (codicology, NOT a grammar)

On zodiac folios the concentric `@Cc` circle-text rings are parsed to placements **R1/R2/R3 by depth**
(R1 = one ring, R2 = next, …) and recorded as **contiguous blocks** — the whole of one ring, then the
whole of the next. The depth *direction* of the numbering is per-folio: **10/12 zodiac folios ascend
(R1=outer→R3=inner), but f70v1/f70v2 descend** (R3=outermost — matches `currier_AZC.md:312`). This is a
**transcription/codicological fact** (rings are discrete nested strata recorded ring-by-ring), NOT a
manuscript grammar.

> **Consequence (PHASE_742):** because the rings are serialized as depth-sorted blocks, any statistic on
> R-subscript *order* is forced — consecutive-token "transitions" are ~97.5% same-ring (the block-count
> floor) and "forward-only" by construction. This **retracted C434** ("R-Series Strict Forward Ordering")
> and the **self-transition half of C436** ("≥98% rigidity"), and put **C432/C433** + C435's "S-at-line-edges"
> spatial claim on the audit queue. Do **not** compute order/transition/rigidity statistics on R/S/C
> placement sequences and treat them as manuscript properties — they measure the block serialization.
> (Order-INDEPENDENT statistics — e.g. cross-folio vocabulary overlap, C436's surviving 0.945/0.340 half —
> are unaffected.)

## Practical checklist for AZC work

1. Read the per-folio IVTFF block + `#` notes **first**; treat the TSV `placement` column as a hint, not ground truth.
2. Do **not** assume placement letter = locus letter (§2), or that letters mean the same thing across folios.
3. Do **not** order tokens by `line_number`; use the per-folio start + `<!HH:MM>` (§5).
4. Do **not** assume a fixed ring-position or subscript mapping across folios (§4, §6); f69r is the only verified anchor.
5. If a claim needs continuous-vs-segmented, radius-vs-ring, or red-ink distinctions, it cannot be made from the TSV alone (§3, §7).
6. Do **not** compute order / transition / self-transition / "rigidity" statistics on R/S/C placement *sequences* and read them as manuscript grammar — placements serialize as depth-sorted blocks, so those statistics are forced (§10; this retracted C434 and C436's self-transition half). Order-independent statistics (vocabulary overlap, etc.) are fine.
