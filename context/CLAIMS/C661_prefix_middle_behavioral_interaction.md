# C661: PREFIX x MIDDLE Behavioral Interaction

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

PREFIX fundamentally transforms MIDDLE behavioral profiles. Within-MIDDLE between-PREFIX JSD = 0.425, which is 97.5% of the computed between-MIDDLE JSD (0.436). Changing the PREFIX on the same MIDDLE produces behavioral divergence nearly as large as changing the MIDDLE entirely. Effect ratio = 0.792 against C657 reference (0.537). 42 MIDDLEs are testable (>=2 PREFIX variants each with >=10 bigrams).

Top interaction MIDDLEs: ckh (JSD=0.710), eeo (0.660), ok (0.649), eed (0.612), i (0.601). These MIDDLEs have completely different successor class profiles depending on which PREFIX they carry.

## Evidence

- 42 testable MIDDLEs with >=2 PREFIX variants (each >=10 bigrams)
- Within-MIDDLE between-PREFIX JSD: mean=0.425, median=0.407, max=0.710
- Between-MIDDLE JSD (computed, n=4278 pairs): 0.436
- C657 reference between-MIDDLE JSD: 0.537
- Effect ratio (within/between, vs C657): 0.792
- Effect ratio (within/between, vs computed): 0.975
- Top interaction MIDDLEs:
  - ckh: NONE/ch/sh variants, JSD=0.710, max=0.919
  - eeo: ch/lk/ok/ot variants, JSD=0.660
  - ok: ch/sh variants, JSD=0.649
  - eed: ch/ot/sh variants, JSD=0.612
  - i: da/sa/ta variants, JSD=0.601

## Interpretation

PREFIX is not a modifier — it is a behavioral transformer. The same MIDDLE deployed with different PREFIXes produces successor class profiles as divergent as those between entirely different MIDDLEs. This resolves the PP continuity puzzle (C656, C657): PP MIDDLEs don't cluster by MIDDLE identity because their behavior depends on PREFIX context. The combination (PREFIX, MIDDLE) — not MIDDLE alone — is the functional unit.

This is consistent with C570 (PREFIX as role selector: 87.1% accuracy) but extends it quantitatively: PREFIX doesn't just predict which role category (AX vs EN) but produces fundamentally different transition dynamics within each role. The continuous MIDDLE landscape (C656) becomes structured when PREFIX is included.

## Cross-References

- C657: PP behavioral profile continuity (mean JSD=0.537) — C661 shows PREFIX accounts for most of this variance
- C656: PP co-occurrence continuity (sil=0.016) — MIDDLE alone is continuous; PREFIX+MIDDLE may be structured
- C570: PREFIX predicts AX vs EN (87.1%) — C661 extends to behavioral profiles, not just role categories
- C506.b: Different MIDDLEs within class have different profiles (73% JSD>0.4) — PREFIX is the mechanism
- C660: Most MIDDLEs are PREFIX-promiscuous — they NEED to be, because PREFIX transforms their behavior

## Provenance

PREFIX_MIDDLE_SELECTIVITY, Script 2 (prefix_middle_interaction.py), Test 5
