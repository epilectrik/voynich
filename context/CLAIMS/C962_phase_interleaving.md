# C962: Phase Interleaving Pattern

**Tier:** 2 | **Scope:** B | **Phase:** LINE_CONTROL_BLOCK_GRAMMAR

## Statement

KERNEL, LINK, and FL phases within lines show weak clustering (alternation rate significantly below random, p<0.001) but NOT sequential blocking. Phases are tendencies, not strict positional sequences.

## Evidence

- 1,191 multi-phase lines (2+ distinct phases among KERNEL/LINK/FL)
- Alternation rate: 0.566 (shuffle mean 0.596, z=-6.34, p<0.001)
- Sequential compliance (LINK->KERNEL->FL): 32.7% (shuffle 21.7%, +11.0pp)
- Pair ordering: LINK->KERNEL 0.517 (neutral), KERNEL->FL 0.623 (ordered), LINK->FL 0.659 (ordered)
- Phase distribution: KERNEL 31.2%, FL 4.7%, LINK 3.5%, OTHER 60.6%

## Interpretation

The canonical phase ordering (C813: LINK->KERNEL->FL) manifests as a weak positional preference with some clustering. KERNEL->FL and LINK->FL are moderately ordered, but LINK and KERNEL freely intermix. This confirms C815's finding (eta^2 = 0.015): phase position is real but explains only 1.5% of variance.

## Provenance

- `phases/LINE_CONTROL_BLOCK_GRAMMAR/scripts/07_phase_interleaving.py`
- Related: C813, C815, C816
