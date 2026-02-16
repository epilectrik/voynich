### C1081 — LINK Adjacency Does Not Modulate HT Prefix Phase

- **Tier:** 2 (ESTABLISHED)
- **Scope:** B (LINK operator × HT prefix phase distribution)
- **Phase:** HT_INTERACTION_ARCHITECTURE (2026-02-15)

**Finding:** LINK-adjacent HT tokens show no difference in EARLY/LATE prefix ratio compared to non-adjacent HT: chi2=0.89, p=0.35, V=0.022. Adjacent EARLY/LATE = 306/92 (76.9% EARLY), non-adjacent = 1208/317 (79.2% EARLY). Position-controlled analysis gives identical results. The HTSC cross-guarantee prediction (C806 × C348) yields no interaction.

**Interpretation:** LINK co-occurrence with HT (C806: OR=1.50) is a positional co-occurrence, not a phase-conditioning relationship. LINK does not induce HT tokens to prefer EARLY or LATE phase prefixes. This is consistent with C804 (LINK predecessor bias NS, p=0.41; successor bias weak, ~1.1x) — LINK is phase-neutral in its neighborhood effects. The HT-LINK association (C806) reflects shared positional preferences (both occur in early-to-medial line positions), not functional coupling.

**Extends:** C806 (LINK-HT positive association, OR=1.50), C348 (phase synchrony EARLY/LATE)
**Confirms:** C804 (LINK transition grammar: predecessor NS, successor weak)

**Quantitative:**
- LINK-adjacent HT with EARLY/LATE prefix: 398 (EARLY=306, LATE=92)
- Non-adjacent HT with EARLY/LATE prefix: 1,525 (EARLY=1208, LATE=317)
- Uncontrolled: chi2=0.89, p=0.346, V=0.022, OR=0.873
- Position-controlled: chi2=0.89, p=0.346, V=0.022 (identical — no positional confound)
