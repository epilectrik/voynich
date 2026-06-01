# PHASE 742 — C759 audit: AZC position→vocabulary under a within-folio null

**Status:** COMPLETE — REGISTERED (v7.00). C759 sharpened + glosses struck; no new constraint.
**Date:** 2026-06-01
**Type:** Constraint audit (within-folio null + geometry correction), triggered by the AZC notation-provenance discovery (`context/DATA/AZC_NOTATION_PROVENANCE.md`). Expert-reconciled design (expert-advisor + lean-expert differential).

---

## Why this phase exists

C759 (Tier 2): *"AZC position (R/S/C) determines vocabulary selection"* — chi²=112.59, df=12, p<0.001,
Cramér's V=0.208, **pooled across all AZC folios, NO within-folio control**. Two flags:
1. **Confound:** position and folio are confounded (C760: ~70% of AZC MIDDLEs folio-exclusive). A pooled
   chi² can be pure folio-composition shadow. Pre-PHASE_700 chi² in cross-layer space = high audit suspicion.
2. **Scrambled geometry:** C759 glosses **S=spoke/nymph, C=center, R=ring** and reads "S favors ok+ot =
   monitoring, C favors ch = control." Those glosses contradict the now-verified f69r geometry
   (R=radii, C=a ring, S=a ring, **W**=center) and the placement≠locus fact (PHASE_741-adjacent provenance work).

## Design (expert-reconciled)

- **Null:** within each folio, permute the position-label vector (no replacement) among that folio's tokens,
  PREFIX fixed. Preserves folio vocab + per-folio position counts exactly; destroys only the within-folio
  position↔prefix link. **One-sided:** survive iff V_obs > 95th pct; exact permutation p, B=10000, seed=0.
  (lean-expert fix: single one-sided critical percentile, not a two-sided band; permute, don't resample.)
- **Diagnostic:** each folio tested against ITS OWN within-folio null (B=2000) — removes the small-N
  Cramér's-V inflation that makes a raw per-folio V distribution uninterpretable.
- Two binnings: FULL (no-prefix as a category) and PREFIXED-ONLY (drop no-prefix, ≈ C759's 0.208 tabulation).
- Script: `scripts/c759_within_folio_audit.py` → `results/c759_within_folio_audit.json`.

## Result

**Pooled within-folio permutation — SURVIVES (both binnings):**

| binning | V_obs | within-folio null mean | null 95th | one-sided p | verdict |
|---|---|---|---|---|---|
| FULL (no-prefix incl.) | 0.152 | 0.110 | 0.123 | **0.0001** | SURVIVE |
| PREFIXED-ONLY (≈C759) | 0.181 | 0.122 | 0.135 | **0.0001** | SURVIVE |

The association is **NOT** folio-composition shadow. (Differential check resolved: expert-advisor's
"folio-shadow → demote" prior was interpretation-carried; lean-expert's "slightly toward survival" on the
numbers was right. We did not pre-commit — we ran it.)

**Per-folio (each vs own null): heterogeneous, radial-scaffold-concentrated.** 8/17 multi-position folios
show position structure at p<0.05:

- **Significant (8):** f73r, f72r3, f72r2, f72v1, f70v1, f72v2, f70v2 (all **Zodiac**) + f68r3 (**A**, the
  radial Sun diagram). → 7 Zodiac + 1 radial astronomical.
- **Not significant:** cosmological f69r (p=0.39), f67v2 (0.70) — **0/2 C**; astronomical 1/3; several
  Zodiac folios borderline-to-null (f71r 0.053, f72v3 0.17, f73v 0.28, f72r1 0.43, f71v 0.97).

Pooled V (0.152) is **lower** than the significant per-folio Vs (0.26–0.36): folios carry *different*
position→prefix directions, so pooling dilutes. There is no single universal profile.

## Disposition (recommended)

1. **C759 statistical core: KEEP (annotate, sharpened).** Position carries vocabulary information beyond
   folio composition (within-folio p=0.0001). NOT demoted.
2. **Scope narrowed:** the effect is concentrated in the **regular radial-medallion scaffold** (Zodiac folios
   + the radial Sun diagram f68r3); it is **absent in cosmological folios** (f69r, f67v2) and weak in
   astronomical. "Position determines vocabulary" holds where there is a regular radial grammar (cf. C433/C434
   zodiac block grammar / forward ordering), **not** as a universal AZC property.
3. **Strike the geometry glosses + functional reading.** S=spoke/nymph, C=center, R=ring are false vs verified
   f69r geometry; the pooled "S=monitoring, C=control" reading is a dilution artifact built on those glosses
   (named flaw + new evidence → down-weight, per anti-dismissal-symmetric gate). Re-derive on corrected
   geometry only if motivated. Link `AZC_NOTATION_PROVENANCE.md`.

**Gate:** survival is a null-driven measurement (self-clearing); the scope-narrowing is descriptive (reading
which folios); the gloss-strike is primary-source-grounded. No echo-class verdict — no external-test requirement.

## Exposed-class sweep (RUN 2026-06-01)

Tested the constraints the experts flagged as attaching a physical gloss to a cross-folio placement
letter, same within-folio machinery. Script: `scripts/sweep_c457_c904_within_folio.py`; result:
`results/sweep_c457_c904.json`. **C312 does not exist** (expert mis-cite, verified — dropped).

| Constraint | Claim | Within-folio null verdict | Note |
|---|---|---|---|
| **C457** (HT S>R) | HT prefers S over R, zodiac | **SURVIVES** V_obs=0.121 vs 95th=0.055, p=0.0001; 8/12 folios S>R | **Filter bug found:** orig N=2952 was ALL-TRANSCRIBER; correct H-only N=1329. Effect reproduces + survives. CONFIRMED at corrected N. |
| **C904** (-ry S-zone) | -ry enriched in S, 3.18× | **SURVIVES** obs 0.60 vs 95th 0.40, p=0.0008 | N=20 (orig 39, likely same inflation). FRAGILE — suggestive not robust. |
| **C496** (o-prefix 75% nymph-S) | — | **NOT RUN** | No reproducible script/data in repo (title-only, ⊂ azc_system). Needs reconstruction before audit. |
| **C434** (R strict forward order) | — | **NOT RUN** | Provenance check (clock geometry vs `line_number`), not a null test. Code-archaeology follow-up. |

**Meta-result — the folio-shadow hypothesis is REJECTED for the statistical cores.** C759, C457, C904
all SURVIVE the within-folio null: AZC within-folio position structure is **real and pervasive**, not a
pooling artifact. What is actually wrong in this class is narrower and case-specific:
1. **Scrambled geometry GLOSSES** — case-by-case, not uniform. C759's "C=center" was flatly wrong (struck);
   C457's "R=radial/S=sector" is defensible for zodiac (kept, with S unverified-off-f69r caveat).
2. **Pre-2026-02 transcriber-filter inflation** (C457 all-transcriber N; C904 likely) — cosmetic, rates/effects stable.
The associations themselves are robust. This *strengthens* the AZC-position-grammar picture (cf. C433/C434/C456).

## Dispositions (sweep)
- **C457** — CONFIRMED, annotated: corrected H-only N + added within-folio null (p=0.0001). Gloss kept (zodiac-defensible).
- **C904** — CONFIRMED-but-fragile, annotated: H-only N=20, survives but small.
- No demotions, no new constraints.

## C434 order-provenance check (RUN 2026-06-01) → RETRACTED + cascade

Script: `scripts/c434_order_provenance.py`; result: `results/c434_order_provenance.json`. Expert-validated
(expert-advisor + lean-expert differential; both → RETRACT).

**Finding:** the parsed R1/R2/R3 are concentric `@Cc` circle-text rings recorded by depth as **contiguous
blocks**. All 12 zodiac folios serialize monotonically — **10 ascending (R1→R2→R3), 2 descending**
(f70v1/f70v2: R3→R2→R1, the per-folio numbering flip, `currier_AZC.md:312`). 927/951 transitions are
same-ring; ring-changes occur only at the 24 block boundaries. "0 backward FORBIDDEN" is forced by the
depth-sort (orient ascending → 0 by construction; actual = 3 once descending folios count). The shuffle-null
"expected 349" only tests "is the file sorted by ring depth?". 97.5% self-transition = the block-count floor
(1 − 24/951), zero excess. **A grammar cannot reverse direction between folios → C434 was never a manuscript
property.**

**Differential check:** both experts agree on the RETRACTIONS (numbers); they diverged on the RETENTIONS —
expert-advisor confidently kept C436-cross-folio + C435-spatial; lean said verify order-independence first.
Resolved: C436-cross-folio is a set-overlap statistic (mathematically order-invariant) → retained; C435's
"S-at-line-edges" is *not* obviously order-independent → flagged, not retained.

### Dispositions (registered, v7.01)
| Constraint | Action |
|---|---|
| **C434** | **RETRACTED → Tier 1** (struck in INDEX, azc_system.md, currier_AZC.md) |
| **C436** | **SPLIT** — ≥98% self-transition half retracted (block floor); cross-folio 0.945-vs-0.340 half RETAINED Tier 2 (order-independent, corroborated C319/C431/C1519) |
| **C435** | "ordered stages" sub-claim STRUCK; S-edge/R-interior spatial split retained but FLAGGED for audit |
| **C1520** | reworded — its no-HEAD-gradient now *corroborates* the artifact; parent ref flipped |
| SPECULATIVE R-series-grammar leg | discarded (INTERPRETATION_SUMMARY §H6+H7 chain leg 1) |
| `AZC_NOTATION_PROVENANCE.md` §10 | nested-ring layout fact added (codicology, not a constraint) |

## C433 + C432 checks (RUN 2026-06-01)

Script: `scripts/c433_c432_checks.py`; result: `results/c433_c432_checks.json`.

- **C433** (Zodiac Block Grammar, ≥98% self-transition) → **RETRACTED (Tier 1).** Every placement code sits
  AT its block-serialization floor (1 − n_blocks/n_tokens): C 0.986/floor 0.985, R1 0.973/0.973, S2 0.918/0.918
  (exact), … overall 0.970 vs 1−128/3299=0.961. Same artifact as C434 — each code recorded as ~1 contiguous
  block per folio (~26 tok/block). "Stricter than Currier B" invalid (block-order vs reading-order). N also
  all-transcriber inflated (R1 1022/1023 → H-only 470/483). Validated 2058→2057; retracted 10→11.
- **C432** (Ordered Subscript Exclusivity) → **CORRECTED, kept Tier 2.** NOT a serialization artifact
  (order-independent presence/absence). But "exclusively Zodiac / binary diagnostic" is **falsified**: f57v
  (cosmological multi-ring) carries R1=51/R2=69/R3=31. Subscripts are **near-exclusive** to Zodiac (1298/1330)
  and track **multi-ring diagram geometry**, not zodiac-family membership. Sharpened, not retracted (factual
  counterexample, not a floor effect).

## C435 spatial check (RUN 2026-06-01) → RETRACTED

Script: `scripts/c435_spatial_check.py`; result: `results/c435_spatial_check.json`. **C435 RETRACTED (Tier 1).**
The "S 95%+ at line edges / R interior" spatial claim is a **locus-length identity**: `line_initial`/`line_final`
are position indices within a single-placement locus, so a code's line-edge rate = 1/(mean locus length) with
zero degrees of freedom. Confirmed at the digit for every code (S0 100%/len1.0, S1 80.4%/0.804, S2 80.8%/0.808,
R1 2.8%/0.028, R2 3.5%/0.035, R3 6.2%/0.062). S = short label loci (`@Lz`), R = long ring loci (`@Cc`). With
"ordered stages" already struck (C434 cascade), both sub-claims fall → full retraction. Resolves the C434-cascade
differential divergence in lean's direction (expert-advisor had tentatively retained C435-spatial; the test shows
it is not structure-independent). C457's HT-rate finding is independent and STANDS (reframe its "boundary" reading).
Validated 2057→2056; retracted 11→12.

## Follow-up audit queue (remaining — NOT serialization-class)
- **C496** — reconstruct the original o-prefix/nymph-S computation, then audit (no script exists).
- **W-census** — C759 excluded W (center) entirely; W may be a distinct register.
- **Inv 2 (angular reading order):** gate first — needs ≥12 items/folio × ≥10–15 folios for Stouffer power; likely under-powered. Defer.

## Serialization-artifact class — CLOSED
| Survived / sharpened (order-INDEPENDENT) | Retracted (sequence / position forced by transcriber chunking) |
|---|---|
| C759 ✓ · C457 ✓ · C904 ✓(fragile) · C436 cross-folio ✓ · C432 (corrected, near-exclusive) | **C434** (forward order) · **C433** (block grammar) · **C435** (S/R edge tautology) · C436 self-transition half |
The artifact had **two mechanisms**, both = "a statistic forced by how the transcriber chunked tokens into loci":
(a) depth-sorted blocks → forced forward-order + ~98% self-transition (C434/C433/C436-self-trans);
(b) single-placement loci → line-edge rate = 1/locus-length (C435). Every claim that depended on the chunking
fell; every claim independent of it (within-folio associations, cross-folio overlap, presence/absence) survived.
**4 retractions total** (C434, C433, C435, + C436-half). Discriminator: does the statistic depend on the
transcriber's locus chunking (order or length)?
