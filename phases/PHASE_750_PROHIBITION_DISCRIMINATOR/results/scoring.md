# PHASE 750 — Scoring (external failure-mode ontologies vs the Voynich prohibition signature)

Scored from verbatim period-source quotes (in-repo), BLIND to the Voynich match, against the locked rubric.
Discriminator score = **F2 (sequence-dominant) + F3 (categorically-safe op) + F5 (process-not-recipe hazard)**, max 3.
Y=1, partial=0.5, N=0. Floor/gate features F1, F4 not scored into the verdict.

---

## P1 — Open / pot distillation  (Brunschwig 1500 + Geber Summa, English)
- **F2 sequence-dominant = N (0)** — dominant catastrophic hazards are CONTAINMENT and RATE, not sequence:
  - "luting for when a glass **cracks** on you in the fire"; "seal any glass with luting so that it can well **endure the fire**" (containment)
  - "the lead pans cannot well endure the sand, for they **melt**, or they must be heated with **very little fire**" (rate)
  - Geber's "First/Second/Third **Order**" = a medicine-classification scheme, NOT a sequence-hazard. [prior-vulnerable: Geber's "First dissolve... afterward distill... then coagulate" is real sequencing → a generous reading gives partial(0.5)]
- **F3 safe-op = N (0)** — no operation named as safe-in-all-contexts.
- **F5 process-not-recipe = partial (0.5)** — containment is a process hazard, but distillation hazard is heavily apparatus- and material-dependent.
- **Discriminator score = 0.5** (1.0 under generous F2)

## P2 — Sealed-circulatory digestion (pelican / circulatio)  (pseudo-Lull Testamentum + Rupescissa, English)  — *framework-favored, C157; gets MORE scrutiny*
- **F2 sequence-dominant = partial (0.5)** — order + sealing-timing emphasized, but allegorical (scored conservatively):
  - "the first consideration is to duly **proceed in the order** of intellectual doctrine"
  - Rupescissa: "it WILL NOT CORRUPT in perpetuity **if kept sealed**"; "**Seal the opening very firmly** with wax" (corruption follows from breaking closure)
- **F3 safe-op = partial (0.5)** — "**Extract gently** what floats"; non-addition framed as the safe path. Not a single crisp always-safe op.
- **F5 process-not-recipe = Y (1.0)** — the strongest, best-quoted match to VS5:
  - "you **must not add** to it another powder, or another water, nor any extraneous thing, but **only that which is born in it**, of its own proper radical nature"
  - i.e. the system is CLOSED/self-contained; **adding ingredients is itself the failure** — the inverse of a recipe/mixture hazard. Maps directly to VS5 (hazard is process-closure, not ingredient-compatibility).
- **Discriminator score = 2.0**

## P3 — Metalwork / smithing  (Theophilus, Hendrie 1847)  — OUT-OF-CLASS (the C2052 genericity foil)
- **F2 = N (0)** — dominant hazards are temperature/fire and irreversibility, not sequence:
  - "cook carefully, so that it may not **boil up** ... guard against the **flame**, because it is very **dangerous**"
  - "the **explosive** nature of the gas produced rendering the process highly **dangerous**" (oil/varnish)
- **F3 = N (0)** — no categorically-safe operation.
- **F5 = partial (0.5)** — process hazards exist but alloy/material composition is central (recipe-like).
- **Discriminator score = 0.5**

## P4 — Sealed fermentation / brewing  (external; SHARP control — sealed but biological)
- **F2 = partial (0.5)** — cool-then-pitch + seal/vent-timing matter, but dominant hazard = contamination + temperature.
- **F3 = N (0)** — no categorically-safe op.
- **F5 = N (0)** — contamination / ingredient ratios central (recipe-hazard).
- **Discriminator score = 0.5**
- *Key result: P4 is SEALED yet scores 0.5 — so "sealed" alone does NOT drive P2's score; P2 rests on closure/self-containment (F5), which P4 lacks. No tie.*

## P5 — Bread-baking / open cooking  (external; FLOOR control — must fail)
- **F2 = N (0)**, **F3 = N (0)**, **F5 = N (0)** — dominant hazards temperature/timing/ingredient ratios.
- **Discriminator score = 0.0**  ✓ floor control fails as required → rubric is NOT a pure floor.

---

## Result table

| Process | Class | F2 | F3 | F5 | **Disc. score** |
|---------|-------|----|----|----|-----------------|
| P2 sealed-circulatory digestion | in-domain (framework-favored) | 0.5 | 0.5 | **1.0** | **2.0** |
| P1 open distillation | in-domain | 0 | 0 | 0.5 | 0.5–1.0 |
| P3 metalwork | **out-of-class** | 0 | 0 | 0.5 | 0.5 |
| P4 sealed fermentation | **out-of-class** | 0.5 | 0 | 0 | 0.5 |
| P5 baking/cooking | **out-of-class (floor)** | 0 | 0 | 0 | 0.0 |

## Verdict vs pre-registered kill-conditions
- **KC2 (floor check): PASS** — P5=0, rubric is a discriminator not a floor.
- **KC1 (tie→closed): no tie** — P2 (2.0) clearly leads; P4-sealed=0.5 shows "sealed" alone doesn't tie it.
- **KC3 (unique selection, one candidate 3/3 + controls ≤1): NOT MET** — P2=2.0, not 3.0. Below the clean-recovery bar.
- **KC4 (framework-as-null guard): reasonably clean** — P2's lead rests on the well-quoted F5; the prior-vulnerable scores (P1-F2, P2-F2) do not flip the leader even under generous re-scoring.

## Honest verdict
- **COARSE level — POSITIVE / discriminating:** the engineered prohibition-layer signature **excludes the out-of-class crafts** (metalwork 0.5, fermentation 0.5, cooking 0.0). This is a discrimination the genericity-prone behavior-matcher could NOT achieve — C2052's 8D matcher hit Theophilus metalwork; the *prohibition-layer* channel does not. New result: testing the engineered layer (not emergent dynamics) defeats the genericity failure for out-of-class exclusion.
- **FINE level — SUGGESTIVE, BELOW BAR:** within the thermal-vessel domain it favors sealed-circulatory digestion (2.0) over open distillation (0.5–1.0), consistent with C157 — but does NOT reach the pre-registered 3/3 unique-selection bar. The edge rests mainly on the closure/self-containment hazard (VS5↔F5: "must not add extraneous thing").
- **Net:** process-class narrowed to **"sealed/closed, sequence-committed, self-contained thermal-chemical process"** — CLOSED-BY-TEST at the fine level (cannot cleanly separate distillation from sealed digestion via this channel), POSITIVE at the coarse level (out-of-class crafts excluded). NOT a clean single-process recovery; NOT material substance (C171 holds).

## Caveats (the part that keeps this honest)
1. **Coder non-independence:** I authored the rubric AND scored it, holding the framework prior. The scores are quote-backed (auditable) and the out-of-class controls *failed* (the direction my bias would have *resisted*), but the fine-level digestion edge specifically is the prior-vulnerable result and should not be promoted on my scoring alone.
2. **P4/P5 scored from general knowledge** (no in-repo period source) — their role is control, and the robust direction (they fail) is bias-resistant, but they are weaker-grounded than P1/P2/P3.
3. **Echo-class:** the fine-level "favors digestion" is a structural-feature↔referent claim → requires human sign-off; cannot be self-cleared.
