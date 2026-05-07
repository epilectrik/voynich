# Voynich Scans (Beinecke IIIF, Max Resolution)

Clean dataset of all 213 canvases from the Beinecke Library's IIIF service, downloaded at maximum resolution. Replaces the older `data/scans/hires/` directory which was extracted from a PDF at lower resolution and had folio-mapping errors.

## Contents

| Path | Purpose |
|------|---------|
| `manifest.json` | Copy of Beinecke IIIF presentation manifest (v3) |
| `canvas_index.json` | Authoritative download index — canvas idx, label, file, dimensions |
| `folio_mapping.json` | Project-folio → Beinecke-canvas cross-reference |
| `images/` | 199 single-folio canvases (≤5000 px wide) |
| `foldouts/` | 14 multi-folio or wide foldout canvases (>5000 px wide) |

## Naming convention

Filenames are **canvas-index-keyed**, with the Beinecke label embedded:
- `canvas_NNN_LABEL.jpg`
- Examples: `canvas_134_75r.jpg`, `canvas_157_85v-and-86r-foldout.jpg`

The canvas index (000-212) is the primary key; the label is included in the filename for human readability. The canvas index never collides; project-internal folio names (e.g., `f75r`) are a SEPARATE mapping layer.

## Folio mapping categories

### SIMPLE (183 mappings)

Straightforward 1:1 mapping where Beinecke's `Nr`/`Nv` matches our project's `fNr`/`fNv`. These cover the majority of single-folio pages.

Six edge cases where Beinecke uses unsubdivided labels but our project uses subdivisions only:
- canvas 120 `67r` → project has f67r1, f67r2 (no plain f67r)
- canvas 121 `67v` → project has f67v1, f67v2 (no plain f67v)
- canvas 122 `68r` → project has f68r1, f68r2, f68r3 (no plain f68r)
- canvas 123 `68v` → project has f68v1, f68v2, f68v3 (no plain f68v)
- canvas 164 `90r` → project has f90r1, f90r2 (no plain f90r)
- canvas 171 `95v` → project has f95v1, f95v2 (no plain f95v)

These canvases are physically wide (4972-8135 px) and project subdivides them.

### FOLDOUT_COMBINED (8 canvases)

Beinecke encodes two folios on one canvas (e.g., "69v and 70r"). Project may further subdivide each side. Canvases:

| Canvas | Beinecke label | Project folios on this canvas |
|--------|----------------|-------------------------------|
| 125 | 69v and 70r | f69v + f70r1, f70r2 |
| 129 | 71v and 72r | f71v + f72r1, f72r2, f72r3 |
| 157 | 85v and 86r (foldout) | f85v2 + f86r (rosettes foldout) |
| 161 | 88v and 89r | f88v + f89r1, f89r2 |
| 163 | 89v (part) and 90r | f89v + f90r1, f90r2 |
| 169 | 94v and 95r | f94v + f95r1, f95r2 |
| 177 | 100v and 101r | f100v + f101r1 |
| 179 | 101v (part) and 102r | f101v2 + f102r1, f102r2 |

### FOLDOUT_SPLIT (4 base folios across 8 canvases)

Single Beinecke folios split across multiple canvases due to physical foldout structure:

| Project base | Beinecke canvases | Project sub-folios |
|--------------|-------------------|--------------------|
| f70v | 126, 127 | f70v1, f70v2 |
| f72v | 130, 131 | f72v1, f72v2, f72v3 |
| f85r | 154, 155 | f85r1, f85r2 (part of rosettes) |
| f102v | 180, 181 | f102v1, f102v2 |

For these, the canvas-to-sub-folio mapping requires manual visual inspection. **Not yet mapped** — to be done as needed for specific OCR work on foldout pages.

### NO_PROJECT_FOLIO (15 canvases)

Cover, flyleaf, edge views — not part of the project corpus:
- canvases 0, 1, 206, 207 (covers, flyleaves)
- canvases 208-211 (head, tail, fore-edge, spine)
- canvas 212 (back cover)

## Resolution upgrade vs old `data/scans/hires/`

| | Old PDF-extract | New IIIF max | Improvement |
|---|---|---|---|
| Typical page | 1166 × 1536 | 2700-2900 × 3700-3900 | ~6× more pixels |
| Per-character px | ~15-20 | ~40-50 | 2.5× larger |
| Per-page disk | ~0.3 MB | ~2-5 MB | ~10× |
| Total corpus | ~67 MB | 535 MB | 8× |

For OCR work, ~40-50 px/character puts us in comfortable handwriting recognition territory. Old resolution was at the edge.

## Mapping correction note

The previous `data/scans/hires/folio_to_page.json` had errors. Per Phase 690 work, we found that what we'd been calling `f75r` in the old extraction was actually Beinecke's `f83r` (canvas 150). All folio references should now use this dataset's authoritative Beinecke labels via `folio_mapping.json`.

## Source attribution

Beinecke Rare Book & Manuscript Library, Yale University. MS 408. Cipher manuscript ("Voynich Manuscript").

IIIF service: `https://collections.library.yale.edu/iiif/2/...`

Downloaded: 2026-05-07. 213 canvases, 535 MB total.

## Usage

```python
import json
from pathlib import Path
from PIL import Image

ROOT = Path('sources/voynich_scans')

# Load mapping
with open(ROOT / 'folio_mapping.json') as f:
    mapping = json.load(f)

# Find canvas for a project folio
def canvas_for_folio(project_folio):
    for m in mapping['mappings']:
        if m.get('project_folio') == project_folio:
            return m
    return None

m = canvas_for_folio('f75r')
img = Image.open(ROOT / m['file'])
print(f"Loaded {project_folio} from canvas {m['canvas_idx']}: {img.size}")
```

## TODOs

- [ ] Manual canvas-to-sub-folio mapping for FOLDOUT_SPLIT cases (f70v1/f70v2, f72v1/2/3, f85r1/r2, f102v1/v2)
- [ ] Verify FOLDOUT_COMBINED sub-divisions where applicable (e.g., is f70r1 left or right half of canvas 125?)
- [ ] Cross-reference with Phase 690 user annotations for nymph-page sub-folio assignments
