# Folio Annotations

Human-verified observations about specific folios that may not be captured in automated analysis.

## Structure

```
folio_annotations/
├── azc/           # AZC (Astronomical/Zodiac/Cosmological) folios
│   └── f69v_f70r1_f70r2_foldout.json/.md
└── README.md
```

## Format

Each folio (or folio group) has:
- **JSON file**: Structured data for programmatic use
- **MD file**: Human-readable documentation

## Purpose

These annotations capture:
1. Visual oddities not evident from transcript alone
2. Physical relationships (foldouts, connected pages)
3. Mismatches between transcript classification and visual content
4. User observations during manual inspection

## Related

- `phases/PHARMA_LABEL_DECODING/` - Similar per-folio documentation for pharma section
