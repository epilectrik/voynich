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

## Follow-ons still open (not run)
- **C496** — reconstruct the original o-prefix/nymph-S computation, then audit (no script exists).
- **C434** — order-provenance check: was "strict forward ordering" computed on clock geometry or `line_number`? (Discovery C bites only if file-order.)
- **W-census** — C759 excluded W (center) entirely; W may be a distinct register.
- **Inv 2 (angular reading order):** gate first — needs ≥12 items/folio × ≥10–15 folios for Stouffer power (lean); likely under-powered. Defer.
