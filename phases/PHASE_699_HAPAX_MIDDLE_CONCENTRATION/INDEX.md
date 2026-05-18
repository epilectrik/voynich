# PHASE 699: Hapax MIDDLE Concentration — Methodology Correction + Composition Shadow Falsification

**Status:** COMPLETE
**Date:** 2026-05-17 / 2026-05-18
**Constraints registered:** C2037, C2038, C2039 (all Tier 2)
**Posture:** Long arc with two interpretive overshoots reversed by expert pushback + user methodological challenge

---

## Origin and trigger

Phase deferred from PHASE_698 as crazy-expert proposal: per-folio hapax MIDDLE concentration vs frequency-matched non-hapax controls. Discriminating test between "operational productive tail" and "lexical content tail (specific materials/parameters/names as one-off MIDDLE forms)" — C914's 3.7× label enrichment as precedent threshold.

Initial framing: if hapaxes cluster ≥3× more than frequency-matched controls on specific folios, lexical-content interpretation wins.

---

## Test arc (four iterations)

### v1: P-placement-only filter (initial pre-registered design)

Pre-registered criteria:
- H1: max hapax enrichment ≥ 3.0 → **PASS** (3.94× on f57r)
- H2: hapax Gini > 0.25 → **PASS** (0.325)
- H3: hapax > n_2_3 paired sign test on top-decile → **FAIL** (6/8, p=0.14)
- H4: TTR confound check → **CONFOUND** (3/8 overlap, expected 0.78)

**v1 verdict:** PARTIAL clustering, lexical-content-tail NOT supported. Frequency-matched n_2_3 controls cluster nearly as much as hapaxes.

### v1 follow-up: Hapax × Dark Pipeline overlap

78 of 820 P-only hapax MIDDLEs (9.5%) catalogued in dark pipeline (per C1137/C1140 four-way partition). 31% of catalogued dark pipeline lives at P-only hapax frequency. Tentative finding: small lexical-content subset within hapax cohort. Several dictionary-confirmed identifiers (fsh=lute compound, alod=aludel, olyd=gold solution, cs=gold) appeared as P-only hapaxes.

### User methodological challenge

User: *"alod = aludel? oddly specific. is it hapax? i'd expect if it names a vessel we'd see it in other folios."*

This was the critical pushback. The intuition: if a MIDDLE names a vessel-class (whether by operational properties or by lexical assignment), it should appear on every folio that uses that vessel class.

### Audit: full-placement check

Of 78 P-only "hapax × dark pipeline" MIDDLEs:
- **Truly hapax corpus-wide (all placements): 2**
- Multi-occurrence on same folio: 0
- **Multi-FOLIO under broader placement filter: 76**

Specific dictionary identifiers under all placements:
- alod: 2 folios (f108r, f44v) — NOT hapax
- fsh: 2 folios (f76r R-placement, f83r P) — NOT hapax
- olyd: 2 folios (f81v P, f88v t-placement) — NOT hapax
- cs: 2 folios — NOT hapax
- rol: 4 folios
- ea: **20 folios** — clearly multi-folio class identifier
- loch: NOT FOUND under any placement (catalog inconsistency)

**The "P-only hapax" framing was artifact of placement filtering. 97% of supposed hapax-dark identifiers are multi-folio under broader filter.**

### v2: All-placement filter (corrected from user pushback)

Re-ran with all placements (H-track + non-uncertain only, no P restriction):
- H1: max hapax enrichment = 3.37× → **PASS**
- H2: hapax Gini = 0.316 → **PASS**
- **H3: 7/8, p=0.035 → PASS** (changed from v1 FAIL)
- H4: TTR confound 3/8 vs expected 0.78 → **CONFOUND remains**

v2 verdict shifted: **LEXICAL-CONTENT-TAIL POSSIBLE but TTR-CONFOUNDED**. H1+H2+H3 PASS with H4 caveat.

### v3: Expert consultation revealed remaining confounds

Both expert-advisor and crazy-expert independently flagged convergent issues:

1. **Placement-stratified H3 test**: which placements drive the v1→v2 flip?
2. **TTR-controlled partial correlation**: does signal survive vocabulary diversity control?
3. **70-MIDDLE distribution**: where do hapax×dark MIDDLEs actually live (corpus-uniform / Section S confound / diagram-heavy artifact)?

v3 controls ran:

**Control A (placement-stratified H3):**
```
P-only:           H3 FAIL (6/8, p=0.14)
P+L (with labels): H3 FAIL (6/8, p=0.14)  ← identical to P-only!
All placements:    H3 PASS (7/8, p=0.035)
```
Adding LABELS did NOT change the result. The v2 PASS depends specifically on **AZC diagram tokens (R rings, S stars, C circles, X, Y, N, T)**. Crazy-expert contamination concern confirmed but at finer granularity than labels.

**Control B (TTR-controlled partial correlation):**
- Raw r(hapax×dark rate, hapax enrichment) = 0.557
- TTR-controlled partial r = 0.395
- Signal nominally survives TTR control (threshold ≥0.15)

**Control C (70-MIDDLE distribution):**
- Section H: 5.1% hapax×dark fraction (vs corpus 2.5%) — chi-square 8.60 (df=3), critical 7.81 → marginal Section H over-representation
- **96% of 70 hapax×dark MIDDLEs on P-placement** (paragraph text, NOT diagram annotations)
- The 96% P-placement finding STRUCTURALLY DISCONFIRMS the plant-label reading (plant labels live in L-placement per C914)

### v4: Within-folio shuffle null (mandatory control per methodology memory)

Both experts converged on a single load-bearing requirement: per `feedback_within_folio_shuffle_null_first.md`, aggregate rho in +0.15 to +0.65 range with no within-folio null is the documented signature of folio-composition shadow. The partial r=0.40 sits squarely in this range.

Ran shuffle null: permute MIDDLE-folio assignments preserving per-folio token counts and global MIDDLE frequency distribution (n=200 permutations).

**Within-folio shuffle null result:**
```
Observed partial r (TTR-controlled): 0.3943
Null distribution: mean=0.2859, SD=0.1187
z-score: 0.914
p-value: 0.18

VERDICT: COMPOSITION SHADOW (z=0.91 < 2.0 threshold)
```

The TTR-controlled partial r does NOT survive within-folio shuffle null. Null mean is 0.286 already substantial under random permutation. Observed 0.394 is only ~1 SD above null.

Notable secondary: raw r=0.56 gives z=2.30 (just-significant raw), but the **TTR-controlled partial r collapses to z=0.91**. The TTR control absorbed most of the raw signal; within-folio shuffle absorbed the rest.

**This matches `feedback_within_folio_shuffle_null_first.md` prediction exactly** — third documented case of aggregate-rho-in-+0.4-range claim dying at within-folio shuffle null (after k-e-depth thermal regimes and triple-i ↔ iter-terminal, both 2026-05-11).

---

## Constraints registered

### C2037 — AZC-diagram-token contamination correction (Tier 2 methodology)

Pre-registered H3 test (hapax > n_2_3 paired sign test on top-decile folios) verdict depends on placement filter choice. P-only and P+L identically FAIL (6/8, p=0.14). All-placement (P + L + R + S + C + X + Y + N + T) PASSES (7/8, p=0.035). The flip is driven specifically by AZC diagram tokens (R rings, S stars, C circles, etc.), NOT by label tokens. Adding labels alone (P+L) gives identical result to P-only. For MIDDLE inventory analyses requiring paragraph-text frequency claims, the defensible standard is P+L; all-placement filter contaminates with AZC diagram singletons that have categorically different distributional properties (per AZC architecture C300-series). The previous PHASE_699 v2 H3 PASS verdict (7/8, p=0.035) was AZC-token-contamination artifact.

### C2038 — Low-frequency hapax-band corpus census (Tier 2 distributional fact)

Currier B has 866 corpus-wide hapax MIDDLEs (all-placement filter). The C1135-catalogued unmatched-PP set ("dark pipeline," 300 MIDDLEs, mean 5.7 tokens) has a heavily-skewed frequency distribution: median=3, 60% at n≤3, 28% at n=1 (hapax frequency band). 70 corpus-wide hapax MIDDLEs (sample of 866) overlap with C1135's catalog under exact MIDDLE-string match. 96% (67/70) of these overlap MIDDLEs occur on P-placement (paragraph text); 0/70 occur on R (ring) placement; <5% on combined C/X/T placements. Distributional census only — does NOT constitute association evidence beyond what C1135's own frequency profile already implies (see C2039 for the within-folio null on the association claim).

### C2039 — Hapax×dark rate vs hapax enrichment correlation is composition shadow (Tier 2 negative)

Per-folio analysis: hapax×dark-pipeline MIDDLE rate (count of hapax-MIDDLE occurrences on folio normalized by folio token count, restricted to MIDDLEs in C1135 catalog) correlates with per-folio hapax enrichment (folio hapax token rate / corpus hapax token rate) at raw r=0.56, partial r=0.40 (TTR-controlled). Within-folio shuffle null (200 permutations preserving per-folio token counts and global MIDDLE frequency distribution): observed partial r vs null mean 0.286 (SD 0.119) gives **z=0.91, p=0.18**. Signal does NOT survive within-folio shuffle null. Folio-composition shadow, not hapax-specific association. **Third documented within-folio-null falsification in +0.4-aggregate-rho pattern** following k-e-depth thermal regimes and triple-i ↔ iter-terminal (both 2026-05-11). The TTR control absorbed half the raw signal (z_raw=2.30 → z_partial=0.91 after combined TTR + within-folio control). Specific lexical-content-tail interpretations for hapax MIDDLEs (PHASE_698 crazy-expert proposal) are NOT supported by per-folio rate analysis at this scale.

---

## Methodology memory updates

### NEW: `feedback_placement_filter_azc_contamination.md`

P-only and P+L are equivalent for paragraph-text MIDDLE analyses (identical H3 verdict in v3 Control A). All-placement filter contaminates with AZC diagram tokens (R, S, C, X, Y, N, T) that have categorically different distributional behavior. For MIDDLE inventory or per-folio frequency analyses where the question is about paragraph-text content, use P+L (or P-only) — NOT all-placement. The error mode is: AZC diagram singletons (MIDDLEs appearing exactly once on a ring/star/circle position) artificially inflate the "hapax" cohort by ~5% and the inflation is concentrated on diagram-heavy folios, flipping per-folio enrichment tests.

### Reinforces existing: `feedback_within_folio_shuffle_null_first.md`

Third documented within-folio-null falsification in +0.4-aggregate-rho pattern. Add PHASE_699 hapax×dark rate to the registry alongside k-e-depth thermal regimes and triple-i. The discipline now has three independent data points for the same trap pattern.

---

## What survives, what dies

### Surviving (registered)

- AZC contamination as documented failure mode (C2037)
- 70 hapax × C1135 distributional overlap as census fact (C2038)
- Within-folio shuffle null falsification of hapax×dark rate correlation (C2039)
- Reinforced confidence in within-folio-shuffle-null-first discipline

### Dying (registered as negative or rejected)

- PHASE_699 v2 H3 PASS verdict (artifact-sensitive per Control A)
- TTR-controlled partial r=0.40 as positive signal (composition shadow)
- Strong "lexical content tail SUPPORTED" interpretation (Self-falsified before registration)
- Section H over-representation interpretation (marginal + 96% P-placement disconfirms plant-label reading)
- Specific dictionary identifications at hapax frequency (alod=aludel etc. remain Tier 3-4 dictionary entries)

### Not registered (drop)

- Section H 5.1% vs 2.5% hapax×dark fraction (chi-square 8.60, marginal, contradicts plant-label reading already)

---

## Methodology lessons

1. **Three interpretive overshoots reversed in one phase**, all caught by expert pushback or user methodological challenge:
   - v1 → tentative lexical-content subset framing (corrected after user "alod=aludel oddly specific")
   - v2 → "lexical content tail SUPPORTED" framing (corrected after expert convergent pushback on placement contamination)
   - v3 partial r → "TTR-controlled signal survives" framing (corrected after within-folio shuffle null collapsed it)

2. **The user's intuition was the load-bearing pushback**. *"If it names a vessel we'd see it in other folios"* directly motivated the full-placement audit that revealed 76/78 supposed hapaxes were multi-folio. Without that pushback, the v1 framing would have been registered.

3. **Within-folio shuffle null is mandatory for any +0.15 to +0.65 aggregate correlation**, per documented methodology. PHASE_699 confirms this for the third time in the project's history. Future correlation registrations should run this control as control #1, NOT control #4.

4. **AZC placement contamination is a real measurement-layer issue** affecting MIDDLE inventory analyses. The all-placement filter (commonly used as "no filter") admits AZC diagram singletons that don't belong in paragraph-text frequency analyses.

5. **"Specific dictionary identifications at hapax frequency are speculative" was the right call** (PHASE_698 alod=aludel concern). The user's pushback hardened that into evidence: hapax-frequency dictionary identifications mostly disappear under broader placement filtering (76/78 turn out to be multi-folio), and the 2 that survive lack discriminating support.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `_hapax_concentration.py` | v1 P-only test (initial pre-registered) |
| `_hapax_dark_pipeline_overlap.py` | First follow-up: 78 hapax×dark overlap under P-only filter |
| `_phonetic_resemblance_check.py` | alod=aludel phonetic check; revealed 2-char shared prefix only |
| `_dark_hapax_full_placement_check.py` | Full-placement audit: 76/78 multi-folio; ALOD=aludel disconfirmed |
| `_hapax_concentration_v2_all_placement.py` | v2 with all-placement filter |
| `_v3_three_controls.py` | Expert-required Controls A/B/C |
| `_within_folio_shuffle_null.py` | Final mandatory control; collapsed v2 PASS |

---

## Origin

Initial: PHASE_698 deferred test, crazy-expert proposal.
Critical user pushback: "alod = aludel? oddly specific. is it hapax? i'd expect if it names a vessel we'd see it in other folios."
Two expert consultation rounds (expert-advisor + crazy-expert) demanded three controls before any registration.
Final expert sign-off after within-folio shuffle null confirmed composition shadow.

PHASE_699 is the cleanest documented example in the project of methodology discipline catching three interpretive overshoots in sequence before registration, including one driven entirely by user methodological intuition (the alod=aludel pushback).
