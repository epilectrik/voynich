# C662: PREFIX Role Reclassification

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

PREFIX massively narrows instruction class membership. Mean class reduction ratio = 0.253 (median 0.182): a PP MIDDLE appearing in N instruction classes retains only ~25% of those classes when combined with a specific PREFIX. 50.4% of (PREFIX, MIDDLE) pairs reduce class membership to <20% of the MIDDLE's full range.

EN PREFIXes (ch/sh/qo) channel MIDDLEs into EN classes at 94.1% rate (81 pairs). AX PREFIXes (ok/ot/ct) channel into AX/FQ classes at 70.8% (44 pairs). INFRA PREFIXes (da/do/sa/so) do NOT channel into CC classes (2.8%, 18 pairs) — they channel into other non-CC roles.

## Evidence

- 264 (PREFIX, MIDDLE) pairs analyzed (>=5 B tokens, MIDDLE in >=2 classes)
- Class reduction ratio: mean=0.253, median=0.182
- Distribution:
  - 0.0-0.2: 133 pairs (50.4%)
  - 0.2-0.4: 78 pairs (29.5%)
  - 0.4-0.6: 39 pairs (14.8%)
  - 0.6-0.8: 6 pairs (2.3%)
  - 0.8-1.0: 8 pairs (3.0%)
- EN PREFIX (ch/sh/qo) -> EN class: 94.1% (81 pairs)
- AX PREFIX (ok/ot/ct) -> AX/FQ class: 70.8% (44 pairs)
- INFRA PREFIX (da/do/sa/so) -> CC class: 2.8% (18 pairs)
- Top narrowing: MIDDLE 'o' (15 classes) -> 1 class with ke/ok/ar/te PREFIXes

## Interpretation

PREFIX is the primary determinant of which instruction class a token belongs to. A MIDDLE like 'o' appears in 15 different instruction classes, but with PREFIX 'ke' it appears in exactly 1 class. PREFIX reduces the 49-class instruction space to a narrow channel.

The 94.1% EN-PREFIX -> EN-class rate confirms C570 at the PP MIDDLE level: ch/sh/qo PREFIXes reliably produce EN-role tokens. The 70.8% AX-PREFIX rate is lower because ok/ot PREFIXes also produce FQ-class tokens (especially Class 14, consistent with C570's FQ violation note).

The INFRA finding is notable: da/do/sa/so PREFIXes produce tokens that are NOT in CC classes. These PREFIXes channel MIDDLEs into specific operational roles outside the core control system.

## Cross-References

- C570: PREFIX predicts AX vs EN (87.1%) — C662 extends to class-level with 94.1% EN accuracy
- C509.b: PREFIX -> class with 100% necessity — C662 quantifies the narrowing ratio (75% reduction)
- C121: 479 tokens -> 49 classes — C662 shows PREFIX is the compression mechanism
- C661: PREFIX transforms behavior (JSD ratio 0.79) — C662 shows the structural basis: class reassignment

## Provenance

PREFIX_MIDDLE_SELECTIVITY, Script 2 (prefix_middle_interaction.py), Test 6
