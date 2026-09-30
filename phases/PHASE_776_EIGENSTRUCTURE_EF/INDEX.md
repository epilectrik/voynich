# PHASE_776 — Does the class-transition eigenstructure (C2061/C2067) survive the edge-fixing null?

**Status:** DESIGN. Draft pre-registration written; certification on fresh seeds next, then a lean-expert audit, lock
and one run on B. **Nothing has been computed on B's token order.**

## Question
C2061/C2067 found that B's 49-class transition operator has slow eigenstructure (λ2, λ3) beyond a character 5-gram
model: the last registered leg of "sequence structure" behind the procedural reading. Does it survive a null that keeps
every word-boundary junction and the folio composition (the header-aware exact edge-frame permutation, EF)?

## Design so far (controls only)
- **Edge-only chains** fitted to B (next token by previous ending and zone) give λ2 excess ≈ 0 under EF (12 runs,
  −0.016 to +0.015, no p ≤ 0.05).
- **Class chains** fitted to B (habit, M1) give +0.013 to +0.048 (11 of 12 with p ≤ 0.003).
- Under EF the class chains' null λ2 is 0.12–0.18, against a within-line shuffle floor of 0.07–0.09: edges carry most
  of a class chain's λ2.
- **Thresholds:** SURVIVES EDGES if p ≤ 0.005 and D ≥ 0.0139; EDGE-REDUCIBLE if p > 0.05.
