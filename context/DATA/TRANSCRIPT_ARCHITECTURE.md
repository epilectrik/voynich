# Voynich Transcript Architecture

**CRITICAL: Read this before writing ANY data-loading code.**

---

## Source File

```
data/transcriptions/interlinear_full_words.txt
```

- **Total rows:** 122,235
- **Tab-separated values (TSV)**
- **Encoding:** UTF-8
- **Header row:** Yes

---

## THE PRIMARY TRACK RULE

> **ALWAYS filter to `transcriber == 'H'` unless you have a specific reason not to.**

The transcript contains **parallel readings from 18 transcribers**. The **H track is the PRIMARY/CANONICAL transcription**. Other transcribers represent alternative readings, variant interpretations, or secondary sources.

| Track | Rows | % of Total | Status |
|-------|------|------------|--------|
| **H** | 37,957 | 31.1% | **PRIMARY - USE THIS** |
| F | 33,368 | 27.3% | Secondary |
| C | 18,122 | 14.8% | Secondary |
| U | 11,307 | 9.3% | Secondary |
| V | 9,664 | 7.9% | Secondary |
| Others | 4,817 | 3.9% | Rare |

### What Happens If You Don't Filter

1. **Token inflation:** ~3.2x more tokens than actual
2. **Artificial patterns:** Transcriber interleaving creates false repetition patterns
3. **Vocabulary pollution:** ~4,200 spurious variant types
4. **Conflicting data:** 47% of positions have transcriber disagreement

### The Filter Pattern

```python
# Pandas
df = pd.read_csv(DATA_FILE, sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']  # PRIMARY track only

# Manual CSV
for row in reader:
    if row.get('transcriber', '').strip('"') != 'H':
        continue
    # ... process row
```

---

## Column Reference

| Index | Column | Description | Values |
|-------|--------|-------------|--------|
| 0 | `word` | Token (lowercase) | 12,362 unique |
| 1 | `complex_word` | Token with special chars | See notes |
| 2 | `folio` | Folio identifier | 227 unique (225 in H) |
| 3 | `section` | Section code | H, S, B, P, C, T, Z, A |
| 4 | `quire` | Quire identifier | A-T |
| 5 | `panel` | Panel identifier | A-X |
| 6 | `language` | Currier language | A, B, or NA |
| 7 | `hand` | Scribe hand | 1-5, X, Y, or NA |
| 8 | `misc` | Miscellaneous flag | NA or U (uncertain) |
| 9 | `d.hand` | Derived hand | 1-5, "2, 3" |
| 10 | `placement` | Text placement | P, R, C, etc. |
| 11 | `line_number` | Line number | 1-103, may have suffixes |
| 12 | `transcriber` | Transcriber ID | **H = PRIMARY** |
| 13 | `line_initial` | Position from start | 1-69 |
| 14 | `line_final` | Position from end | 1-69 |
| 15 | `par_initial` | Paragraph position | NA or numeric |
| 16 | `par_final` | Paragraph position | NA or numeric |

---

## Section Codes

| Code | Name | H-only Tokens | Description |
|------|------|---------------|-------------|
| H | Herbal | 11,392 | Plant illustrations |
| S | Stars/Recipes | 10,680 | Recipe-like text, "Stars" section |
| B | Biological/Balneological | 6,955 | Human figures, bathing scenes |
| P | Pharmaceutical | 2,568 | Jars, containers |
| C | Cosmological | 2,560 | Cosmological diagrams |
| T | Text | 1,626 | Text-only pages |
| Z | Zodiac | 1,330 | Zodiac diagrams |
| A | Astronomical | 846 | Astronomical diagrams |

---

## Language Values

| Value | Meaning | H-only Count |
|-------|---------|--------------|
| `A` | Currier A | 11,415 |
| `B` | Currier B | 23,243 |
| `NA` | No assignment (AZC sections) | 3,299 |

**Important:** `language=NA` does NOT mean "missing data." These are tokens in sections A, Z, C (astronomical/zodiac/cosmological diagrams) which exist outside the Currier A/B classification system.

H-only language=NA breakdown:
- C (Cosmological): 1,075
- Z (Zodiac): 1,330
- A (Astronomical): 846
- H (Herbal): 48 (minor spillover)

---

## Edge Cases and Warnings

### 1. Asterisks (*) in Words

Asterisks indicate **illegible or uncertain characters**.

- Total in H track: **172 tokens**
- Examples: `cth*ar`, `*doin`, `**chol`, `k**chy`

**Action:** Filter out or handle separately:
```python
if '*' in word:
    # Handle uncertain token
```

### 2. Empty Words

- Total in H track: **17 tokens**
- All in section B

**Action:** Skip empty words:
```python
if not word.strip():
    continue
```

### 3. Uncertain Tokens (misc='U')

- Total in H track: **75 tokens**
- Marked as uncertain readings

**Action:** Consider filtering:
```python
if row['misc'].strip('"') == 'U':
    # Uncertain reading
```

### 4. Missing Folios in H Track

Two folios have NO H readings:
- `f85v2` - Only U and V transcribers (409 rows)
- `f116v` - Only U transcriber (2 rows)

**Action:** Be aware these folios won't appear in H-only analysis.

### 5. Non-Numeric Line Numbers

Some line numbers have suffixes: `9a`, `1b`, `11c`, etc.

- Total: 1,198 rows
- Pattern: Base number + letter suffix for sub-positions

**Action:** Handle in line parsing:
```python
# Extract numeric part
line_num = ''.join(c for c in line_number if c.isdigit())
```

### 6. word vs complex_word

197 rows have differences between `word` and `complex_word`:
- `ooiin` vs `o'oiin` (apostrophe notation)
- `*` vs `�` (encoding issues)
- `ckeor` vs `cKeor` (capitalization)

**Action:** Use `word` column for analysis. `complex_word` preserves original notation.

---

## H Track Statistics (Canonical Numbers)

These are the CORRECT numbers to use in constraints and documentation:

| Metric | Value |
|--------|-------|
| Total H tokens | 37,957 |
| Currier A tokens | 11,415 |
| Currier B tokens | 23,243 |
| AZC tokens (language=NA) | 3,299 |
| Unique folios | 225 |
| Uncertain (*) tokens | 172 |
| Empty tokens | 17 |
| Uncertain (misc=U) tokens | 75 |

---

## Transcriber Agreement

**Critical finding:** Transcribers disagree on **47.2% of positions**.

| Metric | Value |
|--------|-------|
| Positions with multiple readings | 36,152 |
| Positions with full agreement | 19,085 (52.8%) |
| Positions with disagreement | 17,067 (47.2%) |

This high disagreement rate means:
1. Non-H data introduces conflicting information, not just duplicates
2. Using all transcribers pollutes analysis with variant readings
3. H track represents a consistent, primary reading

---

## Placement Codes (for AZC sections)

| Code | Meaning | H-only AZC |
|------|---------|------------|
| P | Paragraph (main text) | 1,359 |
| C | Circular text | 728 |
| R1-R4 | Ring positions (inner to outer) | 1,339 |
| S, S1, S2 | Sector text | 484 |
| X, Y | Special positions | 188 |
| L | Label | 65 |
| Q | Quadrant | 60 |
| O | Other | 49 |

---

## Quick Reference: Safe Loading Pattern

```python
import pandas as pd
from pathlib import Path

DATA_FILE = Path('data/transcriptions/interlinear_full_words.txt')

def load_h_only():
    """Load only the PRIMARY (H) transcriber track."""
    df = pd.read_csv(DATA_FILE, sep='\t', low_memory=False)

    # Filter to PRIMARY track
    df = df[df['transcriber'] == 'H']

    # Clean string columns
    for col in ['word', 'folio', 'section', 'language']:
        df[col] = df[col].str.strip('"')

    # Optional: Remove uncertain tokens
    df = df[~df['word'].str.contains(r'\*', na=False)]
    df = df[df['word'].str.len() > 0]

    return df

def load_currier_a():
    """Load Currier A tokens (H track only)."""
    df = load_h_only()
    return df[df['language'] == 'A']

def load_currier_b():
    """Load Currier B tokens (H track only)."""
    df = load_h_only()
    return df[df['language'] == 'B']

def load_azc():
    """Load AZC tokens (language=NA in H track)."""
    df = load_h_only()
    return df[df['language'] == 'NA']
```

---

## Historical Bugs (Learn from Past Mistakes)

### Bug: Missing H Filter (discovered 2026-01-15)

**Impact:** Multiple phases loaded ALL transcribers, causing:
- C250 (64.1% block repetition) was completely an artifact - actual value is 0%
- Token counts inflated by ~3.2x
- False sequential patterns from transcriber interleaving

**Lesson:** ALWAYS start with `df = df[df['transcriber'] == 'H']`

---

## Checklist for New Scripts

Before committing any script that loads the transcript:

- [ ] Filter to `transcriber == 'H'`
- [ ] Handle empty words
- [ ] Handle asterisk (*) tokens appropriately
- [ ] Use correct column indices (0=word, 6=language, 12=transcriber)
- [ ] Document which language subset (A, B, or NA) is being analyzed
- [ ] Test with expected H-only counts (37,957 total, 11,415 A, 23,243 B, 3,299 NA)

---

*Last updated: 2026-01-15*
*This document prevents the transcriber filtering bug from recurring.*
