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

### By Placement Type (H-only)

| Category | Total | A | B |
|----------|-------|---|---|
| TEXT (P*) | 33,128 | 11,081 | 21,649 |
| LABEL (L*) | 350 | 183 | 99 |
| RING (R*) | 2,245 | 19 | 844 |
| CIRCLE (C*) | 830 | 4 | 191 |
| STAR (S*) | 505 | - | - |
| OTHER | 899 | 128 | 460 |

**Note:** STAR and most RING/CIRCLE tokens are in AZC sections (language=NA), not A or B.

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

## Placement Type Taxonomy

**CRITICAL:** The `placement` column distinguishes TOKEN TYPES, not just positions. Different placement types represent fundamentally different content.

### Placement Categories

| Category | Codes | Meaning | Primary Use |
|----------|-------|---------|-------------|
| **TEXT** | P, P1, P2, P3, P4 | Paragraph/main text | Standard analysis |
| **LABEL** | L, L1, L2, L3, L4 | Illustration labels | Exclude from text analysis |
| **RING** | R, R1, R2, R3, R4 | Ring/circular text (AZC) | AZC-specific analysis |
| **CIRCLE** | C, C1, C2 | Circular text | AZC-specific analysis |
| **STAR** | S, S0, S1, S2, S3 | Star/sector text | AZC-specific analysis |
| **OTHER** | B, F, I, K, M, N, O, Q, T, T1-T4, U, W, X, Y, Z, b, m, t | Special positions | Case-by-case |

### Token Breakdown by Placement (H-only)

**Currier A:**
| Category | Tokens | % | Vocab Types |
|----------|--------|---|-------------|
| TEXT | 11,081 | 97.1% | 3,270 |
| LABEL | 183 | 1.6% | 161 |
| OTHER | 128 | 1.1% | 121 |
| RING | 19 | 0.2% | 18 |
| CIRCLE | 4 | <0.1% | 4 |

**Currier B:**
| Category | Tokens | % | Vocab Types |
|----------|--------|---|-------------|
| TEXT | 21,649 | 93.1% | 4,662 |
| RING | 844 | 3.6% | 422 |
| OTHER | 460 | 2.0% | 302 |
| CIRCLE | 191 | 0.8% | 145 |
| LABEL | 99 | 0.4% | 91 |

### Label vs Text Vocabulary

- **Label types (A):** 161 unique
- **Text types (A):** 3,270 unique
- **Overlap:** 61 types (37.9% of labels appear in text)
- **Label-only:** 100 types unique to labels

### Filtering Conventions

```python
# TEXT ONLY (standard analysis)
df_text = df[df['placement'].str.startswith('P')]

# LABELS ONLY (illustration annotation analysis)
df_labels = df[df['placement'].str.startswith('L')]

# EXCLUDE LABELS from text analysis
df_no_labels = df[~df['placement'].str.startswith('L')]

# AZC RING/CIRCLE/STAR
df_rings = df[df['placement'].str.startswith('R')]
df_circles = df[df['placement'].str.startswith('C')]
df_stars = df[df['placement'].str.startswith('S')]
```

### Historical Note

The placement distinction was discovered in the TRANSCRIPT-ARCHITECTURE-AUDIT (2026-01-16). Prior analyses may have inadvertently included labels in text analysis. Impact is minimal for Currier B (0.4% labels) but more significant for Currier A (1.6% labels).

---

## AZC Placement Codes (Detailed Reference)

For comprehensive AZC encoding documentation, see: **[ARCHITECTURE/azc_transcript_encoding.md](../ARCHITECTURE/azc_transcript_encoding.md)**

Key findings from AZC_INTERFACE_VALIDATION (2026-01-19):

| Finding | Implication |
|---------|-------------|
| P-text is linguistically Currier A | Exclude from AZC analysis |
| S-placement meaning is context-dependent | Spokes on standard diagrams, interrupted rings on nymph pages |
| Diagram types show same functional signature | Visual variation is interface-only |
| Center tokens are legality-participating | Include in standard analysis |
| Nymph S-positions show 75% o-prefix | Positional encoding near illustrations |

### Quick Reference (H-only counts)

| Code | Meaning | Count |
|------|---------|-------|
| P | Paragraph (main text) | ~33,000 |
| C, C1, C2 | Circular text | 830 |
| R, R1-R4 | Ring positions | 2,245 |
| S, S0-S3 | Sector/interrupted text | 505 |
| L, L1-L4 | Labels | 350 |
| X, Y | Special positions | ~180 |
| Q | Quadrant | ~60 |
| O | Other | ~50 |

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

## Canonical Library: scripts/voynich.py

**PREFERRED: Use this library instead of writing custom data loading code.**

The `scripts/voynich.py` module provides:
- Automatic H-track filtering
- Proper placement type handling
- Morphological analysis (PREFIX/MIDDLE/SUFFIX)
- Token classification (RI/PP/INFRA)
- Record-level analysis

### Basic Usage

```python
from scripts.voynich import Transcript, Morphology, RecordAnalyzer, MiddleAnalyzer

# Iterate Currier A tokens (H-track, labels excluded, uncertain excluded)
tx = Transcript()
for token in tx.currier_a():
    print(token.word, token.folio, token.line)

# Morphological analysis
morph = Morphology()
m = morph.extract('chody')
# m.articulator, m.prefix, m.middle, m.suffix

# Full record analysis with classification
analyzer = RecordAnalyzer()
record = analyzer.analyze_record('f1r', '1')
print(f"Composition: {record.composition}")  # MIXED, PURE_RI, PURE_PP
for t in record.tokens:
    print(f"{t.word}: {t.token_class} (MID={t.middle})")

# MIDDLE compound structure analysis (see COMPOUND_MIDDLE_ARCHITECTURE phase)
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')  # Build from Currier B
print(mid_analyzer.is_compound('opcheodai'))  # True if contains core MIDDLEs
print(mid_analyzer.get_contained_atoms('opcheodai'))  # List of core substrings
```

### Token Classes

| Class | Meaning | Source |
|-------|---------|--------|
| RI | Registry-Internal | MIDDLE in a_exclusive_middles |
| PP | Pipeline-Participant | MIDDLE in a_shared_middles |
| INFRA | Infrastructure | DA-family prefix + short MIDDLE (C407) |
| UNKNOWN | Unclassified | MIDDLE not in either set |

### Key Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `Transcript().currier_a()` | Iterator[Token] | All Currier A tokens |
| `Transcript().currier_b()` | Iterator[Token] | All Currier B tokens |
| `Transcript().azc()` | Iterator[Token] | All AZC tokens |
| `Morphology().extract(word)` | MorphAnalysis | Parse into ART/PRE/MID/SUF |
| `RecordAnalyzer().analyze_record(folio, line)` | RecordAnalysis | Full record breakdown |
| `RecordAnalyzer().analyze_folio(folio)` | List[RecordAnalysis] | All records in folio |
| `RecordAnalyzer().iter_records()` | Iterator[RecordAnalysis] | All Currier A records |
| `MiddleAnalyzer().build_inventory(system)` | None | Build MIDDLE inventory from A/B/all |
| `MiddleAnalyzer().is_compound(middle)` | bool | True if contains core MIDDLEs |
| `MiddleAnalyzer().get_contained_atoms(middle)` | List[str] | Core MIDDLEs in compound |
| `MiddleAnalyzer().get_folio_unique_middles()` | Set[str] | MIDDLEs in exactly 1 folio |
| `MiddleAnalyzer().classify_middle(middle)` | str | CORE/COMMON/RARE/FOLIO_UNIQUE |
| `MiddleAnalyzer().summary()` | dict | Inventory statistics |

### Morphology Notes

- MIDDLE is always non-empty (per C293 - MIDDLE is primary discriminator)
- Gallows-initial tokens (cph-, cfh-, ckh-) are correctly prefixless (C528)
- Articulators detected when followed by known prefix
- Atomic suffix list only (compound suffixes moved to MIDDLE)

### MiddleAnalyzer Notes

The MiddleAnalyzer class provides compound MIDDLE detection based on findings from the COMPOUND_MIDDLE_ARCHITECTURE phase:

- **Compound MIDDLEs:** Longer MIDDLEs built by combining core MIDDLEs as substrings
- **Core MIDDLEs:** Appear in 20+ folios (75 types in B, 5.6% of inventory)
- **Folio-unique MIDDLEs:** Appear in exactly 1 folio (858 types in B, 64.1%)
- **Key finding:** 84.8% of line-1 folio-unique MIDDLEs are compound (+29.9pp above chance)

Use cases:
- Detecting identification vocabulary (folio-unique compound forms)
- Analyzing compositional structure of HT/UN tokens
- Testing compound rates for label vs body text

---

## Checklist for New Scripts

Before committing any script that loads the transcript:

- [ ] **PREFERRED: Use `scripts/voynich.py` library** (handles all filtering automatically)
- [ ] If writing custom loader: Filter to `transcriber == 'H'`
- [ ] **Filter by placement type** (TEXT vs LABEL vs RING, etc.)
- [ ] Handle empty words
- [ ] Handle asterisk (*) tokens appropriately
- [ ] Use correct column indices (0=word, 6=language, 10=placement, 12=transcriber)
- [ ] Document which language subset (A, B, or NA) is being analyzed
- [ ] Document which placement types are included
- [ ] Test with expected H-only counts (37,957 total, 11,415 A, 23,243 B, 3,299 NA)

---

*Last updated: 2026-01-28*
*This document prevents the transcriber filtering bug from recurring.*
*Placement type taxonomy added from TRANSCRIPT-ARCHITECTURE-AUDIT (2026-01-16).*
*AZC encoding cross-reference added from AZC_INTERFACE_VALIDATION (2026-01-19).*
*MiddleAnalyzer added from COMPOUND_MIDDLE_ARCHITECTURE (2026-01-28).*
