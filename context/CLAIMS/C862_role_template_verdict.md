# C862: Role Template Verdict

**Status:** Validated
**Tier:** 2
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

Folios organize paragraphs via **ROLE TEMPLATE** (combined score 0.623), but this derives from **role stability** (0.897), NOT vocabulary reuse (0.114). Paragraphs share what proportions of operations to execute, not which specific operations.

## Evidence

```
Template test components:
  Vocabulary reuse:    0.114  (LOW - independent)
  Role correlation:    0.858  (HIGH - template)
  Role stability:      0.897  (HIGH - template)
  Combined score:      0.623  (TEMPLATE - borderline)
```

## Model

```
FOLIO TEMPLATE MODEL:
├── Role profile: SHARED (template component)
│   └── EN/FL/FQ/CC proportions consistent
├── Vocabulary: INDEPENDENT (parallel component)
│   └── Each paragraph selects different tokens
└── Pattern: Constraint satisfaction, not instruction copying
```

## Reconciliation with Probe

Probe found:
- 63-85% NEW vocabulary per paragraph → vocabulary independence ✓
- Role composition FLAT across sequence → role stability ✓
- Intra-folio similarity 1.51x inter-folio → weak template ✓

All consistent with HYBRID model: role template + vocabulary independence.

## Verdict

**HYBRID MODEL** - Neither pure template nor pure parallel.
- Folio defines WHAT PROPORTIONS of roles to execute
- Paragraphs independently choose WHICH TOKENS satisfy these proportions

## Related

- C855 (role template)
- C856 (vocab distribution)
- C857 (Par 1 ordinariness)
