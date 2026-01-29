# AZC_FOLIO_DIFFERENTIATION Phase

## Objective

Investigate whether AZC folios are internally differentiated or interchangeable. Determine if different AZC folios serve different roles in the A->AZC->B constraint pipeline.

## Background

Post AZC_REASSESSMENT, we know:
- A->AZC->B is constraint propagation, not content routing (C753)
- A folios are coverage-optimized, not discriminative (C756)
- AZC has two families: Zodiac (13 folios) and A/C (17 folios) (C430)
- P-text on AZC folios is linguistically Currier A, not AZC diagram text

But we haven't asked:
- Do separate AZC folios cover different token roles?
- Do certain A folios preferentially route through certain AZC folios?
- Are some AZC folios generalists (cover everything) vs specialists?
- Does diagram position (R, S, C) determine vocabulary?
- How does P-text relate to adjacent diagram text on the same folio?
- Which AZC folios most strongly constrain which B folios?

## Tests

| Test | Question | Method |
|------|----------|--------|
| T1 | Do AZC folios differ in role coverage? | Role profile per folio (KERNEL, LINK, PP, etc.) |
| T2 | Do A folios cluster with specific AZC folios? | A-AZC vocabulary overlap matrix |
| T3 | Are any AZC folios specialists vs generalists? | Vocabulary breadth and exclusivity |
| T4 | Does diagram position determine vocabulary? | PREFIX/MIDDLE profile by placement code |
| T5 | What is P-text relationship to diagram text? | Same-folio P vs diagram vocabulary overlap |
| T6 | Which AZC folios most constrain B? | AZC-B vocabulary compatibility matrix |
| T7 | Do Zodiac vs A/C families serve different B folios? | Family-stratified B coverage |
| T8 | Manual token-level inspection | Review of AZC tokens, single-char sequences |
| T9 | Cross-system single-char analysis | Compare f49v/f76r/f57v single-char sequences |

## Results Summary

| Test | Finding | Verdict |
|------|---------|---------|
| T1 | Zero KERNEL/LINK tokens; ~50% OPERATIONAL, ~50% UN | FAMILY_UNIFORM |
| T2 | All AZC folios overlap all A folios; Zodiac slightly higher | FAMILY_DIFFERENTIATED |
| T3 | 70% MIDDLEs exclusive to single folio | NO_CLEAR_SPECIALIZATION |
| T4 | Position affects PREFIX (p<0.001, V=0.21) | POSITION_DETERMINES_VOCABULARY |
| T5 | P-text cosine 0.97 to A, 0.74 to diagram | PTEXT_IS_CURRIER_A |
| T6 | All AZC cover all B; top 5 only 22.5% | DISTRIBUTED_COVERAGE |
| T7 | Zodiac-A/C B coverage correlation r=0.90 | FAMILIES_REDUNDANT |
| T8 | f57v R2 has repeating single-char sequence | ANOMALOUS_SEQUENCE |
| T9 | All 4 cross-system shared chars (d,k,o,r) are primitives | PRIMITIVE_OVERLAP |

## Key Findings

1. **AZC has NO kernel control operators.** Zero KERNEL and LINK tokens. AZC vocabulary is ~50% in the 49-class grammar (OPERATIONAL) and ~50% outside (UN). This structurally distinguishes AZC from B.

2. **P-text is linguistically Currier A.** PREFIX profile has 0.97 cosine similarity to Currier A, only 0.74 to diagram text. Mean 19.5% MIDDLE overlap with same-folio diagram text.

3. **Position determines vocabulary within AZC.** Significant effect (p<0.001):
   - S-positions (spoke/nymph): 56% ok+ot prefixes
   - C-positions (center): 28% ch enrichment
   - R1/R2/R3 are nearly identical (cosine >0.985)

4. **AZC folios are vocabulary-specialized.** 70% of MIDDLEs (424/605) appear in only ONE folio. Only 13 MIDDLEs are universal (75%+ of folios).

5. **Both AZC families provide redundant B coverage.** Zodiac and A/C family B coverage correlates at r=0.90. 81/82 B folios are balanced between families.

6. **Universal shared vocabulary.** All A folios overlap all AZC folios, and all AZC folios overlap all B folios. The coverage is distributed, not hub-dominated.

## Single-Character Sequence Discovery (T8-T9)

Manual inspection of f57v revealed an anomalous single-character sequence in R2 position:
```
o l d r * x k k f * t r * * y c * (repeating pattern with asterisks)
```

Cross-referencing with existing notes (C497), we identified two other folios with single-character sequences:
- **f49v** (Currier A): 26 single-char L-placement labels
- **f76r** (Currier B): 9 single-char L-placement labels

Analysis found the 4 characters appearing in ALL THREE sequences (`d`, `k`, `o`, `r`) are **all grammar primitives** per C085. This is documented in C762.

| Folio | System | Placement | Primitive Rate | Function |
|-------|--------|-----------|----------------|----------|
| f49v | A | L (Label) | 67% (6/9) | Instructional (meta-structural) |
| f76r | B | L (Label) | 86% (6/7) | Control sentinels (grammatical) |
| f57v | AZC | R2 (Ring) | 54% (7/13) | Unknown |

The shared primitives span full token morphology: PREFIX (o, k) + MIDDLE (k) + SUFFIX (d, r).

**f57v R2 Ring Anomaly (C763):** Detailed analysis of f57v revealed that ring R2 is 100% single characters while other rings (R1, R3) have normal Voynichese (26-28% single chars). The R2 sequence shows a repeating ~27-character pattern with systematic p/f substitution and unique `m n` terminators. This is structurally non-Voynichese and diagram-integrated, unlike the margin labels in f49v/f76r.

## Implications for AZC Understanding

1. **AZC is not part of the execution layer.** Zero KERNEL/LINK means AZC cannot execute B-style control. It provides constraints, not instructions.

2. **P-text is A-registry material.** Not diagram annotation but Currier A entries placed above diagrams. Treat as separate from AZC diagram text.

3. **Position within diagrams encodes information.** The R/S/C distinction is not arbitrary - it correlates with vocabulary selection. This supports the "context-locking scaffold" interpretation.

4. **Folios specialize via exclusive vocabulary.** Each folio contributes unique MIDDLEs, but shares core universal vocabulary. This is consistent with "folio-specific constraint sets."

5. **Two families are functionally redundant.** Zodiac and A/C don't serve different B folios - they provide the same vocabulary coverage. The difference is structural (uniform vs varied scaffolds), not functional.

## Scripts

- `t1_azc_role_coverage.py` - Role distribution by AZC folio
- `t2_a_azc_affinity.py` - A-AZC vocabulary clustering
- `t3_azc_specialization.py` - Generalist vs specialist classification
- `t4_position_vocabulary.py` - Vocabulary by placement code
- `t5_ptext_diagram_relation.py` - P-text to diagram relationship
- `t6_azc_b_compatibility.py` - AZC-B vocabulary compatibility
- `t7_family_b_coverage.py` - Zodiac vs A/C family B coverage
- `t8_manual_token_extraction.py` - AZC token extraction for manual review
- `single_char_investigation.py` - Cross-system single-char sequence analysis
- `f57v_ring_analysis.py` - Detailed f57v R2 ring pattern analysis (scratchpad)

## Key Data Sources

- `scripts/voynich.py` (Transcript, Morphology)
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` (49 classes)
- Transcript filtering: placement != 'P' for diagram text, placement == 'P' for P-text

## Notes

- P-text confirmed as Currier A in AZC_INTERFACE_VALIDATION phase
- Two AZC families: Zodiac (13: 12 Z + f57v), A/C (17: 8 A + 6 C + 2 H + 1 S)
- Zodiac uses subscripted codes (R1-R3, S1-S2), A/C uses generic codes (R, S, C, P)

## Provenance

Phase designed based on post-AZC_REASSESSMENT gap analysis: we characterized AZC grammar but not internal differentiation.
