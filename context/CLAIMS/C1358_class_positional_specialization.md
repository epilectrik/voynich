# C1358: Class Positional Specialization

**Tier:** 2
**Scope:** B, line, 49-class, position
**Phase:** LINE_MICRO_GRAMMAR (Phase 474)
**Depends on:** C121, C556, C816

## Statement

Half of the 49 instruction classes (24/48 tested, 1 excluded for low count) are positional specialists at the quintile level (chi2 p<0.001). The strongest specialists are line-final: FL_SAFE classes 38 and 40 peak at Q4 (entropy 1.38-1.81 vs max 2.32), along with AXM classes 15, 21, 22, 25. Line-initial specialists include classes 4, 5, 26 (peaking at Q0). The remaining 24 classes distribute uniformly across positions. This extends C556 (role-level enrichment) and C816 (3 CC classes) to full 49-class resolution.

## Evidence

| Metric | Value |
|--------|-------|
| Specialist classes (p<0.001) | 24/48 |
| Generalist classes | 24/48 |
| Strongest specialist | Class 40 (FL_SAFE), entropy=1.377, peak Q4 |
| Lines analyzed (>=5 classified) | 1,890 |
| Tokens analyzed | 14,437 |
| Max entropy (uniform) | 2.322 bits |

**Top specialists by entropy:**
| Class | State | Entropy | Peak | Chi2 | n |
|-------|-------|---------|------|------|---|
| 40 | FL_SAFE | 1.377 | Q4 | 159.3 | 62 |
| 22 | AXM | 1.595 | Q4 | 82.2 | 41 |
| 38 | FL_SAFE | 1.807 | Q4 | 54.2 | 42 |
| 15 | AXM | 1.837 | Q4 | 78.4 | 62 |
| 21 | AXM | 2.062 | Q4 | 74.2 | 97 |
| 4 | AXM | 2.090 | Q0 | 28.6 | 108 |
| 26 | AXM | 2.111 | Q0 | 34.0 | 138 |

## Structural Implication

The 49-class grammar has a positional skeleton: approximately half the classes are anchored to specific line positions. The line-final bias is striking — FL_SAFE, escape-related classes concentrate at line endings, consistent with C556's CLOSE zone and the SETUP→WORK→CHECK→CLOSE model. But the other half of the grammar distributes freely, consistent with C964's free-interior finding. The grammar is a hybrid: positional scaffold + free execution.

**Results:** `phases/LINE_MICRO_GRAMMAR/results/line_micro_grammar.json`
