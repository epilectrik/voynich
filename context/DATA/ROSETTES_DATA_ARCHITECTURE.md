# Rosettes Data Architecture

## Status

The EVA interlinear transcript (`voyn_de_ln.txt`) is **NOT used** for Rosettes analysis.
All Rosettes data comes from `data/rosettes_annotated.json`.

## Why the EVA Transcript Failed

The Stolfi/EVA interlinear transcript has critical deficiencies for the Rosettes foldout:

1. **Missing data**: 3 of 9 rosettes (NE, EAST, SE) had no ring text transcribed
2. **No spatial context**: All tokens are flattened into line-sequential order, losing critical spatial relationships (spoke arrangements, path tokens, inner vs outer positions)
3. **Transcriber gaps**: f85v2 (the central page with all 9 rosettes) has NO H-track data, requiring fallback to U/V tracks with quality/coverage issues
4. **No path awareness**: Tokens on connecting paths between rosettes were lumped with adjacent rosette labels

These issues were discovered during manual verification against the manuscript in Phase 396 (ROSETTES_FUNCTIONAL_ANATOMY).

## Current Data Source

### File: `data/rosettes_annotated.json`

**Version**: 2.0
**Source transcription**: ZL (Zandbergen) transcription from voynich.nu (`ZL3b-n.txt`)
**Annotation**: Manual spatial classification verified against the manuscript
**Coverage**: 137 loci, 443 words, 135/137 reviewed

### How It Was Built

1. ZL transcription (`data/zl_rosettes.txt`) was parsed from IVTFF format
2. User manually classified every locus using an interactive annotation tool (`phases/ROSETTES_FUNCTIONAL_ANATOMY/scripts/rosettes_annotation_tool.py`)
3. Classifications were merged with morphological analysis from `scripts/voynich.py`
4. Build script: `phases/ROSETTES_FUNCTIONAL_ANATOMY/scripts/build_rosettes_annotated.py`

### Entity Architecture

The Rosettes foldout is organized into **19 first-class entities**:

| Type | Entities | Count |
|------|----------|-------|
| Rosettes | NW, NORTH, NE, WEST, CENTER, EAST, SW, SOUTH, SE | 9 |
| Paths | PATH_WEST_NW, PATH_NW_NORTH, PATH_NORTH_NE, PATH_NE_EAST, PATH_EAST_SE, PATH_SE_SOUTH, PATH_SOUTH_SW, PATH_SW_WEST | 8 |
| Special | CLOCK | 1 |
| Other | UNCLASSIFIED | 1 |

Each entity has **sub-regions** (second-class types):
- `ring` — circumferential text around rosette diagrams
- `inner_label` — labels inside the rosette diagram
- `outer_label` — labels outside the rosette boundary
- `spiral` — spiral text element (NE rosette only)
- `paragraph` — extended text blocks
- `clock_text` — text associated with the clock element

### Token Structure

Each token has pre-computed morphological analysis:

```json
{
  "word": "ydekam",
  "articulator": "y",
  "prefix": "de",
  "middle": "k",
  "suffix": "am",
  "is_bridge": true
}
```

The `is_bridge` flag indicates whether the MIDDLE appears in the Currier B main corpus (based on 85 bridge MIDDLEs from `phases/BRIDGE_MIDDLE_SELECTION_MECHANISM/results/bridge_selection.json`).

### JSON Schema

```
{
  "_metadata": { version, source, totals },
  "summary": {
    "total_entities": 19,
    "total_loci": 137,
    "total_words": 443,
    "entities": { <name>: { loci_count, word_count, sub_regions } }
  },
  "entities": {
    "<ENTITY_NAME>": {
      "total_loci": int,
      "total_words": int,
      "unique_middles": [str],
      "bridge_middles": [str],
      "non_bridge_middles": [str],
      "sub_regions": {
        "<type>": {
          "loci_count": int,
          "word_count": int,
          "loci": [{
            "locus_id": "fRos.N",
            "position": "area:slot",
            "placement": "@Cc|@L0|+L0|...",
            "first_class": "ENTITY_NAME",
            "second_class": "sub_region_type",
            "text_raw": "original IVTFF text",
            "text_clean": "cleaned EVA",
            "words": [{ word, articulator, prefix, middle, suffix, is_bridge }],
            "word_count": int,
            "reviewed": bool,
            "notes": "annotation notes",
            "is_custom": bool
          }]
        }
      },
      "notes": ["entity-level annotation notes"]
    }
  }
}
```

## API Access

Use `RosettesAnalyzer` from `scripts/voynich.py`:

```python
from scripts.voynich import RosettesAnalyzer

ra = RosettesAnalyzer()

# List entities
ra.get_entities()      # All 19
ra.get_rosettes()      # Just the 9 rosettes
ra.get_paths()         # Just the 8 paths

# Get tokens and MIDDLEs
ra.get_entity_tokens('NW')                    # All tokens for NW
ra.get_entity_tokens('NE', sub_region='ring')  # Just ring text
ra.get_entity_middles('CENTER')                # Unique MIDDLEs
ra.get_entity_bridge_middles('WEST')           # Bridge MIDDLEs only
ra.get_entity_loci('SW')                       # Full locus entries

# Vocabulary analysis
ra.vocabulary_overlap()     # Overlap with B corpus
ra.per_rosette_middles()    # {position: set_of_middles} for all 9
ra.all_middles()            # All unique MIDDLEs across foldout
ra.corpus_middles()         # B corpus MIDDLEs (for comparison)

# Summary
ra.summary()     # Overview with counts and overlap stats
ra.metadata()    # File metadata
```

## Backup Files

| File | Description | Status |
|------|-------------|--------|
| `data/rosettes_annotated.json` | **CANONICAL** — current data source | Active |
| `data/rosettes_unified.json` | Phase 396 unified JSON (Stolfi + partial ZL) | Backup — do not use |
| `data/zl_rosettes.txt` | Raw ZL transcription in IVTFF format | Source file |
| `phases/ROSETTES_FUNCTIONAL_ANATOMY/results/rosettes_annotations.json` | User's manual annotation decisions | Archive |

## Constraint Status

All previous Rosettes constraints (C1088-C1098, C1100-C1101, C1109-C1115, C1122-C1123) were **invalidated and deleted** due to being derived from the incomplete EVA transcript data. Reanalysis using the corrected data is pending.
