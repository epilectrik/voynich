# Script Explorer - App Structure

## Directory Layout

```
apps/script_explorer/
├── main.py              # Entry point
├── requirements.txt     # PyQt5 dependency
├── core/                # Data models and loaders
│   ├── __init__.py      # Package marker
│   ├── constraints.py   # Constraint loading and lookup
│   ├── grammar.py       # Grammar rules (C121, etc.)
│   └── transcription.py # Folio transcription loading
├── parsing/             # Text analysis (system-agnostic)
│   ├── __init__.py      # Package marker
│   └── currier_a.py     # Currier A two-gate parsing
├── ui/                  # PyQt5 user interface
│   ├── __init__.py      # Package marker
│   ├── main_window.py   # Main application window
│   ├── folio_viewer.py  # Token display and view modes
│   └── constraint_panel.py # Constraint reference panel
└── fonts/               # Voynich EVA font files
    └── VoynichEVA.ttf   # EVA transcription font
```

## Layer Responsibilities

### `core/` - Data Layer
- Load and cache external data (transcriptions, constraints, grammar)
- Provide lookup interfaces
- **Must NOT** import from `parsing/` or `ui/`

### `parsing/` - Analysis Layer
- Implement token parsing and validation
- Return structured results (dataclasses/enums)
- **Must NOT** import from `ui/`
- **May** import from `core/` for reference data

### `ui/` - Presentation Layer
- Consume parsing results
- Display tokens with classification-based coloring
- Build detail panels from structured data
- **Must NOT** reinterpret parsing results
- **May** import from `core/` and `parsing/`

## Import Rules

```
core/  ←  parsing/  ←  ui/
```

No reverse imports. `ui/` may import from both `core/` and `parsing/`.

## Key Interfaces

### From `parsing/currier_a.py`:
- `parse_currier_a_token(token) → CurrierAParseResult`
- `AStatus` enum: VALID_REGISTRY_ENTRY, VALID_MINIMAL, PREFIX_VALID_MORPH_INCOMPLETE, AMBIGUOUS_MORPHOLOGY, ILLEGAL_PREFIX

### From `ui/folio_viewer.py`:
- `ViewMode` enum: View mode selection
- `get_token_primary_system(token, folio_system) → str`
- Color palette constants: `*_COLORS` dicts

## Constraint Compliance

Parsing logic must comply with frozen constraints:
- C240: Marker legality (8 families)
- C267: Morphological completeness
- C349: Extended prefix mappings
- C383: Global type system

See `context/CLAIMS/` for authoritative constraint definitions.

## Modification Guidelines

1. **Adding new parsing** → Add to `parsing/` module
2. **Adding new view modes** → Modify `ui/folio_viewer.py`
3. **Adding data sources** → Add to `core/` module
4. **Changing constraint interpretation** → **ESCALATE** to context system first
