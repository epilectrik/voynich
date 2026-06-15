# C2078: A/B Within-Token Construction-Determinism Difference is Localized to Multi-Character Suffix Construction

> **RETRACTED 2026-06-15 (same day as registration). STATUS:RETRACTED.**
> The entire effect is a **marginal-frequency shadow**, not conditional-arrangement determinism.
> Two decisive controls — flagged by lean-expert in the original review but run AFTER registration —
> killed it:
> - **`-dy` census (suffix leg):** removing the `-dy/-edy/-eedy` family collapses the len-2 closure
>   gap from +0.297 to **−0.010 [−0.032,+0.009]** (exact null). B's low suffix entropy is the ~63%
>   `-dy` marginal concentration (already owned by C283 `-edy` 191× enriched, C919, C1514), NOT
>   distributed arrangement determinism.
> - **Prefix/core marginal decomposition (the reversal):** ΔH_cond(prefix) −0.050 decomposes into
>   ΔH_marg −0.237 (B's flatter prefix marginal = more prefix *variety*, known) + arrangement-info
>   ΔI −0.187 in the OPPOSITE direction (B prefix arrangement is if anything *tighter*). So "B looser
>   in prefix" is a marginal artifact, not arrangement. Same for core.
> **No conditional-arrangement A/B construction difference survives marginal control.** Every leg
> reduces to known marginal-frequency facts (B `-dy`-heavy suffix; B prefix-variety). Panel: lean
> RETRACT; advisor SPLIT collapsed to RETRACT once the reversal failed its own control.
> **Failure modes:** marginal-frequency-shadow + sufficient-vs-necessary-control (5 necessary
> controls passed, none targeted the mechanism) + premature-registration (registered before
> discharging the marginal-shuffle control lean flagged in review). Kept as negative knowledge: the
> construction-entropy lens, marginal-controlled, shows A and B build shared roots IDENTICALLY in
> arrangement; the apparent gaps are marginal concentration (C283/C1514). Not counted as validated.
> *Open, NOT claimed:* the ΔI arrangement-info (B prefix more context-determined) needs its own
> marginal controls before any registration.

**Tier:** ~~2~~ RETRACTED → negative knowledge
**Scope:** A, B, construction, suffix, closure, within-token
**Date:** 2026-06-15 (registered AND retracted same day)
**Class:** ~~structural measurement~~ marginal-frequency-shadow (the construction-entropy gap was the marginal, not arrangement)
**Validation:** expert-advisor + lean-expert + crazy-expert(hurter) — the differential check + the lean-flagged controls retracted it; see below.

---

## Statement

Measuring within-token **construction determinism** — conditional entropy H(next char | previous 2 chars) — on the **395 MIDDLEs shared by Currier A and B**, root-frequency-matched (each shared MIDDLE contributes equal token counts from A and B), the A/B difference is **NOT a uniform "B tighter."** It reverses by morphological region and **localizes to multi-character suffix construction** (ΔH = H(A) − H(B); positive = B more deterministic):

| region | ΔH(A−B) | 95% CI | reading |
|---|---|---|---|
| PREFIX | −0.049 | [−0.064, −0.032] | B slightly **looser** |
| CORE (MIDDLE) | −0.025 | [−0.033, −0.016] | B slightly **looser** |
| SUFFIX, length-1 | +0.019 | [−0.019, +0.059] | **NULL** — identical |
| SUFFIX, length-2 | **+0.295** | **[+0.268, +0.324]** | B **much tighter** |

Single-character closures are also identical in *content* (A: y 78% / s 13% / r 6%; B: y 81% / r 8% / s 8% — both `-y`-dominated). So **A and B build the same roots, make the same single-character endings with the same determinism, but B constructs multi-character suffixes as near-deterministic closure operators while A attaches multi-character endings to the same roots freely.** The within-token construction difference between the two systems is localized to **multi-character suffix/closure arrangement.**

The **prefix/core reversal** (B *looser*, not tighter) is load-bearing: it is the part NOT predicted by a naive "B is more constrained overall" reading, and is what distinguishes this from a restatement of the frozen B=executable/A=registry conclusion.

---

## Controls (all passed; the control history is the evidence)

| control | result |
|---|---|
| N-matched corpus sizes | applied throughout |
| shared-MIDDLE only (vocabulary) | C1514: A/B suffix atom *inventory* near-identical (JSD 0.050) → a measured entropy *difference* is informative, not an inventory artifact |
| prefix-stripped (qo-dominance C1538) | effect survived (post-prefix +0.138) |
| **root-frequency-matched** | removed ~¾ of a naive aggregate estimate (+0.165 → +0.041 overall) — most of the apparent "B tighter overall" was B reusing fewer shared roots (frequency-shadow / usage-concentration confound) |
| terminal `$` excluded | effect *grew* (+0.125 → +0.228) → NOT a token-length / terminal-predictability artifact |
| **length-stratified** | effect survives at fixed length-2 (+0.295), null at length-1 → genuine arrangement determinism, not the (real) A/B suffix-length difference (A mean 0.86 vs B 1.18) |

Estimator: plug-in conditional entropy, 300-resample bootstrap CIs. **Miller–Madow bias works AGAINST the reported direction** (A samples a wider suffix-atom set per C1514 → larger per-context K → more downward bias on H(A)), so +0.295 is a conservative lower bound. Correct instrument (char-arrangement, not token-adjacency; C2066 window-blindness N/A).

---

## Relationship to existing constraints

- **EXTENDS C522** (construction–execution layer independence): the within-token *construction* layer is now shown to carry an A/B distinction, localized to multi-char closure. (C522 measures construction↔execution *coupling within B*, r=−0.21 p=0.07; this is a different quantity — A-vs-B construction entropy — so no conflict and no reopening of the independence finding.)
- **SHARPENS C2009** (A/B same-MIDDLE contextual divergence, Procrustes residual 0.30, whole-token / region-agnostic): region-decomposes that divergence and localizes it to multi-char suffix, with prefix/core *reversed* (B looser).
- **DISTINGUISHED FROM C1514** (cross-system suffix atom identity, JSD 0.050; A enriches o/h/l/s, B enriches d/e/i): C1514 measures suffix atom *inventory/enrichment*; C2078 measures *arrangement determinism*. A's wider atom set (C1514) is mechanistically **consistent** with A's higher multi-char closure entropy — corroborating, not redundant.
- **CROSS-REF C1487** (six-terminal taxonomy), **C919** (d-extension END-class), **C1735** (suffix=closure): B's grammaticalized multi-char closure operators.

---

## What this does NOT claim (discipline)

- **C171-safe:** a determinism MEASUREMENT, no semantic/referent content.
- **Does NOT register the operational interpretation** "because B is executable it constrains closure / A is a registry so closes freely." That reading is a Tier-3/4 framework-fit gloss — per framework-as-null, a clean fit to the frozen conclusion is a prior toward NULL, not confirmation. It belongs in SPECULATIVE, NOT in this constraint. The registrable content is the **ΔH-by-region localization** and the **prefix/core reversal**.

## Validation (differential check)

- **expert-advisor (novelty):** PARTIALLY NEW — register as a Tier-2 extension of C522 / sharpening of C2009, distinguished from C1514; lead with the prefix/core reversal.
- **lean-expert (rigor):** confirmed the quantity is new (no prior-art collision); caught the **suffix-length confound** as un-controlled.
- **The experts DIVERGED** on the aggregate closure number (advisor: registrable; lean: length-confounded). Per methodology, divergence flagged that interpretation was carrying the aggregate. Running lean's demanded controls (`$`-exclusion + length-stratification) **resolved it**: the effect survives at fixed length-2 and is localized to multi-char construction. The clean result came from the disagreement, not either expert alone.

## Provenance

Off-books char-construction analysis, 2026-06 (Phase 691 LM exploration tail). Scripts inline: `scripts.voynich` Transcript + Morphology → plug-in conditional entropy → morphological-region decomposition → root-frequency-match → `$`-exclusion → length-stratification → bootstrap.
