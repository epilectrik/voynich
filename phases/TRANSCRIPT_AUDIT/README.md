# TRANSCRIPT-ARCHITECTURE-AUDIT

**Phase ID:** TRANSCRIPT-ARCHITECTURE-AUDIT
**Status:** COMPLETE
**Date:** 2026-01-16

---

## Purpose

Comprehensive analysis of the transcript file structure to document ALL columns, ALL placement types, and establish proper filtering conventions.

---

## Key Finding

The `placement` column (index 10) distinguishes TOKEN TYPES, not just positions:

| Category | Codes | H-only A | H-only B |
|----------|-------|----------|----------|
| TEXT | P, P1-P4 | 11,081 (97.1%) | 21,649 (93.1%) |
| LABEL | L, L1-L4 | 183 (1.6%) | 99 (0.4%) |
| RING | R, R1-R4 | 19 | 844 |
| CIRCLE | C, C1-C2 | 4 | 191 |
| STAR | S, S0-S3 | - | - |
| OTHER | Various | 128 | 460 |

**Labels have 38% vocabulary overlap with text** - they use some common words but also have 100 unique types.

---

## Filtering Convention

```python
# TEXT ONLY (standard analysis)
df_text = df[df['placement'].str.startswith('P')]

# EXCLUDE LABELS
df_no_labels = df[~df['placement'].str.startswith('L')]
```

---

## Files

| File | Description |
|------|-------------|
| `transcript_audit.py` | Analysis script |
| `impact_assessment.md` | Impact on prior analyses |
| `results/transcript_audit.json` | Full data |

---

## Impact on Prior Work

- **MIDDLE-AB analysis:** Minimal impact (1.6% label contamination)
- **Single-token records:** 16/23 were labels, not text
- **Vocabulary counts:** ~100 label-only types (3% of apparent A vocabulary)

---

## Documentation Updated

- `context/DATA/TRANSCRIPT_ARCHITECTURE.md` - Added complete placement taxonomy

---

*This phase resolves the transcript structure ambiguity discovered during pharma label investigation.*
