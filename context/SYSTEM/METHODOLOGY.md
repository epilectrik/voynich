# Methodology

**Purpose:** Warnings, common bugs, and patterns for safe analysis.

---

## Critical Warning: Prefix Matching vs Token Matching

**RECURRENT BUG: This has caused false results multiple times.**

The 17 forbidden transitions are about **specific token pairs or token-class pairs**, NOT blanket prefix-to-prefix rules.

| WRONG | RIGHT |
|-------|-------|
| "Any `ol-` followed by any `qo-` is forbidden" | Specific transitions between grammar classes are forbidden |
| Testing `olsheol → qokchy` as forbidden | These are different tokens than the forbidden pair |
| Finding thousands of "violations" | Real violations are 0 in valid Currier B text |

**When writing new analysis scripts:**
1. Check if you're matching PREFIXES or specific TOKENS
2. Verify against the canonical grammar (479 types in Currier B)
3. Test on small samples before drawing conclusions
4. If results seem too good or too bad, check parsing logic first

---

## File Organization

| File Type | Location |
|-----------|----------|
| Phase analysis scripts | `archive/scripts/` |
| Utility scripts | `archive/scripts/` |
| Generated reports | `archive/reports/` |
| Phase documentation | `phases/<PHASE_NAME>/` |
| Canonical data | `data/transcriptions/` |
| Frozen outputs | `results/` |
| Curated knowledge | `context/` |

**Main directory should contain only:**
- `CLAUDE.md` (redirect to context/)
- `README.md`
- Configuration files
- Core library code in `lib/`

---

## Script Patterns

### Loading Transcription Data

```python
from lib.transcription import load_transcription

# Default: original data, no patches
tokens = load_transcription()

# With recovery: apply high-confidence patches
tokens = load_transcription(apply_recovery=True, min_confidence='HIGH')
```

### Filtering by Currier Language

```python
# Currier B only (most analysis)
if currier == 'B' and transcriber == 'H' and token and '*' not in token:
    # process token

# Currier A only
if currier == 'A' and transcriber == 'H' and token and '*' not in token:
    # process token
```

### Checking Against Grammar

```python
# Load canonical grammar
with open('results/canonical_grammar.json') as f:
    grammar = json.load(f)

# Check if token is in grammar
canonical_types = set(grammar['token_types'])  # 479 types
is_canonical = token in canonical_types
```

---

## Common Analytical Errors

### 1. Sample Size Issues

- Currier A has ~37,000 tokens, B has ~75,000
- Some folios have <100 tokens
- Statistical tests need sufficient data

### 2. Section Confusion

- "Currier" = language classification (A or B)
- "Section" = manuscript section (H, B, C, S, T, P, etc.)
- These are NOT the same thing

### 3. Transition Direction

- `X → Y` is the transition FROM X TO Y
- Forbidden transitions are asymmetric (65%)
- Don't assume bidirectional rules

### 4. Tier Promotion

- Don't treat Tier 3 findings as structural
- Always cite the tier when referencing claims
- Keep speculative content quarantined

---

## Creating New Phases

1. **Create directory:** `phases/PHASE_NAME/`
2. **Include:**
   - `README.md` or `PHASE_SUMMARY.md`
   - Analysis scripts (copy to `archive/scripts/`)
   - Output data
3. **Document:**
   - Pre-defined success criteria
   - What tier the findings belong to
   - Which constraints are added/updated
4. **Update:**
   - `context/CLAIMS/INDEX.md` if new constraints
   - `context/MAPS/claim_to_phase.md`
   - `context/SYSTEM/CHANGELOG.md`

---

## Citing Constraints

Format: `Constraint ###` or `C###`

Example: "Currier A is folio-disjoint from B (C272)"

Always include the constraint number for traceability.

---

## What Cannot Be Recovered Internally

No amount of structural analysis can determine:

- Specific substances, materials, or products
- Natural language equivalents for any token
- Historical identity of author or school
- Precise dating or geographic origin
- Illustration meanings
- Physical apparatus construction details

These require external evidence and belong to Tier 3+.

---

## Navigation

← [STOP_CONDITIONS.md](STOP_CONDITIONS.md) | [HOW_TO_READ.md](HOW_TO_READ.md) →
