# C564: AUXILIARY Morphological-Positional Correspondence

**Tier:** 2 (Structural Inference)
**Scope:** B
**Phase:** AUXILIARY_STRATIFICATION
**Status:** VALIDATED

## Claim

AX positional sub-groups have distinct morphological signatures. Prefix family, suffix density, and articulator usage systematically differentiate INIT, MED, and FINAL sub-roles.

## Evidence

### Morphological Profiles

| Feature | AX_INIT | AX_MED | AX_FINAL |
|---------|---------|--------|----------|
| Prefix rate | 74.8% | 88.8% | 60.9% |
| Suffix rate | 28.6% | 26.4% | 48.6% |
| Articulator rate | 17.5% | 6.4% | **0.0%** |
| Dominant prefix | diverse (yk, ch, pch) | ok/ot | bare (NONE) |
| Token types | 78 | 119 | 52 |

### Key Distinctions

1. **Articulators are INIT-exclusive within AX**: 17.5% in INIT, 6.4% in MED, 0.0% in FINAL
   - Classes 4, 5, 6, 26 have >30% articulator rate
   - AX_FINAL has zero articulators across all 52 token types
   - This matches ICC finding that articulators are AX-specific (C267)

2. **Prefix density decreases with position**: INIT (74.8%) < MED (88.8%) -- but then drops to FINAL (60.9%)
   - AX_MED is most morphologically "standard" (ok/ot prefix)
   - AX_FINAL is morphologically minimal ("bare" tokens like ly, ry, sy)

3. **Suffix density is FINAL-elevated**: 48.6% vs 26-29% for INIT/MED
   - Frame closers carry more suffix material

### Prefix Family Mapping

| Prefix Family | Sub-Group | Purity |
|---------------|-----------|--------|
| OK/OT (7 classes) | AX_MED | 86% (6/7, exception: class 14) |
| ARTICULATED (4 classes) | AX_INIT | 100% (4/4) |
| OL (1 class) | AX_FINAL | 100% (1/1) |
| CT (1 class) | AX_FINAL | 100% (1/1) |
| BARE/NONE (7 classes) | Mixed | split across all 3 sub-groups |

## Interpretation

Morphological composition is partially predictive of positional behavior:
- Articulated tokens -> always initial
- ok/ot prefixed tokens -> always medial
- Bare/ct/ol tokens -> tend toward final

This means the morphological type system encodes positional information for AX classes, consistent with the global finding that PREFIX carries functional properties (C267, C293).

## Cross-References

- C267: PREFIX encodes structural properties
- C293: TOKEN = [ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX]
- C563: AX positional stratification (this finding's structural basis)
