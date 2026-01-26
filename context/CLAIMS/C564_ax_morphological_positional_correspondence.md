# C564: AUXILIARY Morphological-Positional Correspondence

**Tier:** 2 (Structural Inference)
**Scope:** B
**Phase:** AUXILIARY_STRATIFICATION
**Status:** VALIDATED (re-verified 2026-01-26 with 19 AX classes)

## Claim

AX positional sub-groups have distinct morphological signatures. Prefix family, suffix density, and articulator usage systematically differentiate INIT, MED, and FINAL sub-roles.

## Evidence

### Morphological Profiles

| Feature | AX_INIT | AX_MED | AX_FINAL |
|---------|---------|--------|----------|
| Prefix rate | 72.6% | 86.4% | 60.2% |
| Suffix rate | 28.5% | 33.9% | 44.9% |
| Articulator rate | 14.1% | 6.9% | **0.0%** |
| Dominant prefix | diverse (yk, ch, pch) | ok/ot | bare (NONE) |
| Tokens | 1195 | 2056 | 601 |

### Key Distinctions

1. **Articulators are INIT-concentrated within AX**: 14.1% in INIT, 6.9% in MED, 0.0% in FINAL
   - Classes 4, 5, 6, 26 have >30% articulator rate
   - AX_FINAL has zero articulators
   - This matches ICC finding that articulators are AX-specific (C267)

2. **Prefix density decreases with position**: INIT (72.6%) < MED (86.4%) -- but then drops to FINAL (60.2%)
   - AX_MED is most morphologically "standard" (ok/ot prefix)
   - AX_FINAL is morphologically minimal ("bare" tokens like ly, ry, sy)

3. **Suffix density is FINAL-elevated**: 44.9% vs 28-34% for INIT/MED
   - Frame closers carry more suffix material

### Prefix Family Mapping

| Prefix Family | Sub-Group | Purity |
|---------------|-----------|--------|
| OK/OT (6 classes) | AX_MED | 100% (6/6; Class 14 removed to FQ, C583) |
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
