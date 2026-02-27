# C1361: No Positional Motifs — Class Bigrams Distribute Freely

**Tier:** 2
**Scope:** B, line, 49-class, bigrams
**Phase:** LINE_MICRO_GRAMMAR (Phase 474)
**Depends on:** C964, C961

## Statement

Of 1,556 distinct class bigram types, only 1 shows significant positional preference after Bonferroni correction (class 9→23, both FQ, enriched 1.89x at Q3). The grammar has no stereotyped positional motifs — specific class-class transitions are not locked to specific line positions. This confirms C964's "free interior" finding at full 49-class resolution and extends C961's "WORK zone unordered" result: not just the WORK zone, but the entire line interior is free of class-sequence stereotypy.

## Evidence

| Metric | Value |
|--------|-------|
| Bigram types tested | 1,556 |
| Total bigrams | 12,547 |
| Significant after Bonferroni (p < 6.4e-7) | 1 |
| Bonferroni threshold | 6.43e-7 |

The single significant bigram (9→23, FQ→FQ at Q3) has only 17 occurrences.

## Structural Implication

The grammar's positional structure operates at the class MARGINAL level (C1358: which classes appear where), not at the bigram level (which class-class pairs appear where). Individual classes have positional preferences, but their pairwise combinations do not. This means the positional gradient (C1359) arises from shifting CLASS FREQUENCIES across positions — not from position-specific grammar rules that prescribe particular transitions. The grammar is the same everywhere; only the vocabulary it draws from shifts.

**Results:** `phases/LINE_MICRO_GRAMMAR/results/line_micro_grammar.json`
