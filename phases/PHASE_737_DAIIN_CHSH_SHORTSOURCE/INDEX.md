# PHASE_737: daiin→CHSH Short-Source Discriminating Test

**Status:** COMPLETE — **VERDICT: CHAR-SIGNATURE ARTIFACT** (0/6 witnesses survive)
**Pre-registered in:** PHASE_735 INDEX (line 33), C2064 mechanism-ambiguity flag.

## Question

C2064 established that daiin→ch/sh survives the 5-gram null (z=4.05) but is **measurement-only, mechanism-ambiguous**: is the survival (A) genuine lane-routing/attraction toward CHSH, or (B) a char-signature artifact — the char-5-gram cannot recover the source token's routing-relevant identity at the token boundary, so it mispredicts the successor and ANY such source shows spurious positive excess regardless of routing?

## Mechanistic frame

At a token boundary the order-5 char context is the last 4 chars of `"<source> "`. For a **short** source (len ≤ 3) the *full token* sits inside that context (`"ol "` fits) → the char model HAS the source identity and should reproduce its routing → DEMOTE. For a **long** source (`daiin` → context `"iin "`) the identity is lost → spurious excess. `ol` (canonical short CHSH-router, C817 lane-conditional 93.2%) already DEMOTED (z=0.60) → prior leans artifact.

## Design (locked before null results)

- **Metric:** per-synth-own-shuffle excess (identical to PHASE_733/735). real_excess vs distribution of synth_excess (each synth referenced to its OWN within-line shuffle). p_emp = fraction synth_excess ≥ real_excess.
- **Null:** 5-gram char Markov, N_synth=200, N_shuffle_per=12, order=5 (identical machinery to PHASE_735 `_cascade_batch.py`).
- **Witness selection (mechanical):** source with ≥30 non-line-final occurrences, SHORT (len ≤ 3), HIGH-CHSH (real →ch/sh rate ≥ 1.5 × corpus base rate). Test ALL qualifying.
- **References (calibration, not counted):** daiin (long, expect SURVIVE), ol (short, expect DEMOTE).
- **Correction:** Bonferroni α = 0.05 / n_witness. Uncorrected also reported.

## Pre-registered decision rule

| Witnesses surviving | Verdict |
|---|---|
| ≥2 | **LANE-ATTRACTION REAL** — general short-source routing above char-Markov; C600/C817 routing mechanism partially rehabilitated as a real (if measurement-level) structure |
| <2 | **CHAR-SIGNATURE ARTIFACT** — daiin survival is the trivial boundary-identity-loss effect; C2064 stays measurement-only, mechanism = artifact, no rehabilitation of C600/C817 |

## Witness set (selected)

base P(next ch/sh) = 0.2535; HIGH threshold = 0.3803. Witnesses (6): `sol, qol, sor, dol, y, ol`. Reference: `daiin`.

## Results

**VERDICT: CHAR-SIGNATURE ARTIFACT.** 0 of 6 short witnesses survive (Bonferroni α=0.0083 AND uncorrected p<0.05). For every short source the 5-gram synth reproduces essentially the entire within-shuffle excess.

| source | len | N | role | real_exc | synth_exc | z | p_emp | verdict |
|---|---|---|---|---|---|---|---|---|
| sol | 3 | 47 | witness | +0.2879 | +0.2559 | 0.55 | 0.295 | demote |
| qol | 3 | 136 | witness | +0.2267 | +0.2211 | 0.13 | 0.445 | demote |
| sor | 3 | 32 | witness | +0.1880 | +0.1858 | 0.03 | 0.530 | demote |
| dol | 3 | 50 | witness | +0.1967 | +0.1260 | 1.03 | 0.160 | demote |
| y | 1 | 56 | witness | +0.1499 | +0.1791 | −0.51 | 0.710 | demote |
| ol | 2 | 381 | witness | +0.1508 | +0.1484 | 0.11 | 0.390 | demote |
| **daiin** | 5 | 290 | **ref** | +0.2145 | +0.1299 | **3.65** | **0.000** | **survive** |

**Calibration perfect:** daiin (long, expect survive) p=0.000, z=3.65 (reproduces C2064 z=4.05); ol (short, expect demote) p=0.39 (reproduces PHASE_735 z=0.60). The mechanistic prediction held exactly: short sources (full identity in boundary context) are char-Markov-reproducible → demote; only the long source whose identity is lost at the boundary shows spurious excess.

## Interpretation (post-expert adjudication)

The test confirms a generalizable artifact category — **the null cannot condition on the claimed antecedent**: a char-5-gram only sees the last 4 chars before the boundary, so when a source token's routing-relevant feature (its prefix) is DISTAL (long token, suffix-boundary-context), the null is structurally blind to it and "survival" is uninformative about routing. Short sources (full identity in-window) are reproduced → demote; the long source (daiin) "survives" because the null can't represent it. This is the **9th failure-mode pattern**, generalizing beyond daiin.

**daiin (precise framing, per crazy-expert's caveat):** the survival is **window-blindness-eligible** — it is NOT positive evidence for lane-routing, and C600/C817 are NOT rehabilitated. But the short-CC witnesses (ol, y, sol…) might be a *different mechanism* than daiin (short CC tokens may genuinely not route), so their demotion does not strictly PROVE daiin's routing is fake. **C2064 stays mechanism-AMBIGUOUS** (not "artifact confirmed"); routing is neither confirmed nor refuted. The clean, within-mechanism implication runs through **qol → C549**, not through daiin's CC short-witnesses.

**C2064 disposition:** stays Tier 2 measurement (daiin→ch/sh IS above-5-gram, z=4.05). Annotate: survival is window-blindness-eligible (char-5-gram cannot condition on long-token prefix identity); provides no positive evidence for routing; mechanism remains ambiguous. C600/C817 not rehabilitated.

## Cascade flag → PHASE_738 (both experts converged)

The window-blindness mechanism applies to **qo-PREFIXED source tokens** (qokeedy etc., long, successor-context = suffix `eedy `, qo-prefix identity lost at boundary). This is exactly C549 (qo→ch/sh, z=5.79) and the C2056 correction-lane family — which the PHASE_729–736 consolidation banner elevated as the surviving "local control bigrams" (Layer 1). **Smoking datum:** `qol` (qo-prefixed, short) was a witness here and DEMOTED (p=0.445) — qo-prefix→CHSH is char-reproducible when qo is in-window, raising the prior that the long-qo ledger survival is the same artifact.

**Expert-converged actions:**
- **C562 (ary line-final) is IMMUNE** — suffix/terminal/categorical-exclusion claim, not prefix-routing. Stays confirmed in Layer 1.
- **C549 / C2056 → PROVISIONAL** in the consolidation banner pending PHASE_738. Do NOT demote yet (C549's *original* class-level interleaving claim, C574/C577 lineage, was never char-5-gram-tested and may survive the appropriate null; the 5-gram-LEDGER entry is what's exposed).
- **PHASE_738 discriminating tests (cheapest → most rigorous):** (1) re-run THIS null on short qo-source tokens only (qok, qot, qoy; qol already demoted) — if all demote, within-mechanism witnesses fall like daiin; (2) **window-controlled / sentinel-injection null** — prepend a source-prefix-family symbol into the char context so the null CAN condition on qo regardless of length; residual collapses → artifact, survives → real; (3) **class-order-shuffle null** on qo-ENERGY→chsh-ENERGY interleaving — the RIGHT instrument for C549's class-level claim (char-5-gram is the wrong instrument; C2062 scalar-vs-eigenstructure lesson).

