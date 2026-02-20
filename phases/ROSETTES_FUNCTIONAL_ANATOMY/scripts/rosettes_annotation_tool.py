"""Rosettes Annotation Tool

Generates interactive HTML for spatial annotation of ZL Rosettes transcription.
Each locus gets:
  - First-class assignment (rosette, path, or special area)
  - Second-class type (ring, inner_label, outer_label, path_label, etc.)
  - Free-text notes
"""

import json
import re
import shutil
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent.parent

# ZL area number → rosette
AREA_TO_ROSETTE = {
    '1': 'NW', '2': 'WEST', '3': 'SW', '4': 'NORTH',
    '5': 'CENTER', '6': 'SOUTH', '7': 'NE', '8': 'EAST', '9': 'SE',
}

# Ring text locus number → rosette (determined by surrounding context)
RING_TO_ROSETTE = {
    2: 'NW', 20: 'NORTH', 35: 'NE',
    47: 'WEST', 62: 'CENTER', 87: 'EAST',
    94: 'SW', 122: 'SOUTH', 133: 'SE',
}

SPECIAL_LOCI = {
    36: ('SPIRAL', 'spiral'),       # fRos.36 <!Spiral>
    112: ('CLOCK', 'clock_text'),   # fRos.112 <!left of clock>
    113: ('CLOCK', 'clock_text'),   # fRos.113 <!above clock>
    114: ('CLOCK', 'clock_text'),   # fRos.114 <!below clock>
    115: ('CLOCK', 'clock_text'),   # fRos.115 <!right of clock>
}

# Roman numeral positions (outside face)
ROMAN_POSITIONS = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'}


def clean_eva(text):
    """Strip IVTFF markup for Voynich font rendering."""
    s = text
    s = re.sub(r'\[([^:]+):[^\]]+\]', r'\1', s)   # [a:b] → a
    s = re.sub(r'\{[^}]+\}', '', s)                 # {xxx} → remove
    s = s.replace('<%>', '').replace('<$>', '')
    s = s.replace('<->', ' ')
    s = re.sub(r'@\d+;', '', s)                     # @213; etc
    s = s.replace('?', '').replace("'", '')
    return s.strip()


def parse_zl_data():
    """Parse ZL Rosettes transcription into structured loci."""
    zl_file = PROJECT / 'data' / 'zl_rosettes.txt'
    text = zl_file.read_text(encoding='utf-8')

    loci = []
    skip_continuations = False
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('<fRos>') or line.startswith('</'):
            continue

        m = re.match(r'<fRos\.(\d+),([^>]+)>\s+(.+)', line)
        if not m:
            continue

        num = int(m.group(1))
        placement = m.group(2)
        rest = m.group(3)

        # Extract position comments and text
        positions = re.findall(r'<!([^>]+)>', rest)
        text_part = re.sub(r'<![^>]+>', '', rest).strip()
        position_str = '; '.join(positions) if positions else ''

        is_continuation = placement[0] in ('+', '*', '/')
        text_clean = clean_eva(text_part)

        # Word count (split on dots and spaces)
        words = [w for w in re.split(r'[.\s]+', text_part) if w.strip()]
        word_count = len(words)

        # Default assignments
        first_class = 'UNCLASSIFIED'
        second_class = 'unclassified'

        # 1. Check special loci first
        if num in SPECIAL_LOCI:
            first_class, second_class = SPECIAL_LOCI[num]
        # 2. Check ring text
        elif 'Cc' in placement or 'Ca' in placement:
            if num in RING_TO_ROSETTE:
                first_class = RING_TO_ROSETTE[num]
                second_class = 'ring'
            else:
                second_class = 'ring'
        # 3. Check paragraph blocks
        elif 'Pb' in placement:
            # Check if Roman numeral position (outside face)
            is_outside = any(p.strip() in ROMAN_POSITIONS for p in positions)
            if is_outside:
                first_class = 'OUTSIDE_FACE'
                second_class = 'paragraph'
            else:
                # Paragraph inside a rosette area
                second_class = 'paragraph'
                area_m = re.match(r'(\d+):', position_str)
                if area_m and area_m.group(1) in AREA_TO_ROSETTE:
                    first_class = AREA_TO_ROSETTE[area_m.group(1)]
        # 4. Check labels
        elif 'L0' in placement:
            # Check Roman numerals (outside face labels)
            is_outside = any(p.strip() in ROMAN_POSITIONS for p in positions)
            if is_outside:
                first_class = 'OUTSIDE_FACE'
                second_class = 'outer_label'
            else:
                second_class = 'inner_label'

        # 5. Fall back to area mapping if still unclassified
        if first_class == 'UNCLASSIFIED' and position_str:
            area_m = re.match(r'(\d+):', position_str)
            if area_m and area_m.group(1) in AREA_TO_ROSETTE:
                first_class = AREA_TO_ROSETTE[area_m.group(1)]

        # Handle continuations for outside face paragraphs
        if is_continuation and first_class == 'UNCLASSIFIED' and loci:
            prev = loci[-1]
            if prev['default_first_class'] == 'OUTSIDE_FACE':
                first_class = 'OUTSIDE_FACE'
                second_class = prev['default_second_class']

            # Skip outside face tokens (Roman numerals I-VIII, fRos.137-160)
        # Also skip their continuation lines
        if first_class == 'OUTSIDE_FACE':
            skip_continuations = True
            continue
        if is_continuation and skip_continuations:
            continue
        skip_continuations = False

        loci.append({
            'id': f'fRos.{num}',
            'num': num,
            'placement': placement,
            'position': position_str,
            'text_raw': text_part,
            'text_clean': text_clean,
            'is_continuation': is_continuation,
            'word_count': word_count,
            'default_first_class': first_class,
            'default_second_class': second_class,
        })

    return loci


def generate_html(loci):
    """Generate the full annotation tool HTML."""
    loci_json = json.dumps(loci, indent=None)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Rosettes Annotation Tool</title>
<style>
@font-face {{
    font-family: 'EVA2';
    src: url('EVA2.ttf') format('truetype');
}}
@font-face {{
    font-family: 'VoynichEVA';
    src: url('VoynichEVA.ttf') format('truetype');
}}
@font-face {{
    font-family: 'VoynichEVAHandA';
    src: url('VoynichEVAHandA.ttf') format('truetype');
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
    padding: 12px;
    background: #fafafa;
}}
h1 {{ font-size: 18px; margin-bottom: 4px; }}
.subtitle {{ color: #666; font-size: 12px; margin-bottom: 12px; }}

/* Controls */
.controls {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 12px;
    padding: 8px 12px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
}}
.controls button {{
    padding: 5px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: #fff;
    cursor: pointer;
    font-size: 12px;
}}
.controls button:hover {{ background: #f0f0f0; }}
.controls button.primary {{
    background: #1976d2;
    color: #fff;
    border-color: #1565c0;
}}
.controls button.primary:hover {{ background: #1565c0; }}
.controls select, .controls input[type="text"] {{
    padding: 4px 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 12px;
}}
.controls label {{ font-size: 12px; color: #555; }}
#stats {{
    font-size: 12px;
    color: #333;
    font-weight: 600;
    margin-left: auto;
}}

/* Table */
.table-wrap {{
    overflow-x: auto;
    border: 1px solid #ddd;
    border-radius: 6px;
    background: #fff;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}}
thead th {{
    position: sticky;
    top: 0;
    background: #f5f5f5;
    border-bottom: 2px solid #ccc;
    padding: 6px 8px;
    text-align: left;
    font-size: 11px;
    text-transform: uppercase;
    color: #555;
    white-space: nowrap;
    z-index: 10;
}}
/* Column widths */
.col-num {{ width: 50px; }}
.col-pos {{ width: 90px; }}
.col-voynich {{ width: 200px; }}
.col-eva {{ width: 200px; }}
.col-wc {{ width: 40px; text-align: center; }}
.col-fc {{ width: 170px; }}
.col-sc {{ width: 130px; }}
.col-notes {{ width: auto; min-width: 200px; }}

tbody tr {{
    border-bottom: 1px solid #eee;
    transition: background-color 0.15s;
}}
tbody tr:hover {{
    filter: brightness(0.96);
}}
tbody tr.continuation {{
    opacity: 0.85;
}}
tbody td {{
    padding: 4px 8px;
    vertical-align: middle;
    font-size: 12px;
}}
td.num {{ text-align: center; color: #888; font-size: 11px; }}
td.pos {{ font-family: monospace; font-size: 11px; color: #555; }}
td.voynich {{
    font-family: 'EVA2', 'VoynichEVAHandA', 'VoynichEVA', serif;
    font-size: 22px;
    line-height: 1.3;
    overflow: hidden;
    text-overflow: ellipsis;
    max-height: 60px;
}}
td.voynich.ring-text {{
    font-size: 16px;
    max-height: 80px;
    overflow-y: auto;
    word-break: break-all;
}}
td.eva {{
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 11px;
    color: #333;
    word-break: break-all;
    max-height: 60px;
    overflow-y: auto;
}}
td.wc {{ text-align: center; color: #888; font-size: 11px; }}

/* Dropdowns in table */
td select {{
    width: 100%;
    padding: 3px 4px;
    border: 1px solid #ddd;
    border-radius: 3px;
    font-size: 11px;
    background: #fff;
}}
td select:focus {{
    border-color: #1976d2;
    outline: none;
    box-shadow: 0 0 0 2px rgba(25,118,210,0.15);
}}
td select.modified {{
    border-color: #ff9800;
    background: #fff8e1;
}}

/* Notes */
td textarea {{
    width: 100%;
    min-height: 24px;
    max-height: 80px;
    padding: 3px 6px;
    border: 1px solid #ddd;
    border-radius: 3px;
    font-size: 11px;
    font-family: inherit;
    resize: vertical;
    line-height: 1.4;
}}
td textarea:focus {{
    border-color: #1976d2;
    outline: none;
    box-shadow: 0 0 0 2px rgba(25,118,210,0.15);
}}
td textarea.has-content {{
    border-color: #4caf50;
    background: #f1f8e9;
}}

/* Continuation marker */
.cont-marker {{
    color: #999;
    font-size: 10px;
    margin-right: 4px;
}}

/* Modified indicator */
.mod-dot {{
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #ff9800;
    margin-left: 4px;
    vertical-align: middle;
}}

/* Hidden file input */
#file-input {{ display: none; }}

/* Group headers */
tr.group-header td {{
    padding: 8px 10px 4px 10px;
    font-weight: 700;
    font-size: 13px;
    border-bottom: 2px solid #999;
    border-top: 2px solid #ccc;
    cursor: pointer;
    user-select: none;
}}
tr.group-header td .group-count {{
    font-weight: 400;
    font-size: 11px;
    color: #777;
    margin-left: 6px;
}}
tr.group-header td .group-toggle {{
    font-size: 11px;
    color: #999;
    margin-right: 6px;
}}
tr.subgroup-header td {{
    padding: 4px 10px 2px 24px;
    font-weight: 600;
    font-size: 11px;
    color: #555;
    border-bottom: 1px solid #ccc;
    font-style: italic;
}}

/* Active sort button */
.controls button.active {{
    background: #1976d2;
    color: #fff;
    border-color: #1565c0;
}}

/* Add panels */
.add-panel {{
    display: none;
    margin-bottom: 12px;
    padding: 10px 14px;
    background: #fff;
    border: 2px solid #1976d2;
    border-radius: 6px;
}}
.add-panel.open {{ display: block; }}
.add-panel h3 {{
    font-size: 13px;
    margin-bottom: 8px;
    color: #1976d2;
}}
.add-panel .form-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
    flex-wrap: wrap;
}}
.add-panel label {{
    font-size: 12px;
    color: #555;
    min-width: 80px;
}}
.add-panel input, .add-panel select, .add-panel textarea {{
    padding: 4px 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 12px;
}}
.add-panel input[type="text"] {{ flex: 1; min-width: 150px; }}
.add-panel textarea {{ flex: 1; min-width: 200px; min-height: 28px; }}
.add-panel .btn-row {{
    display: flex;
    gap: 8px;
    margin-top: 8px;
}}
.add-panel button {{
    padding: 5px 14px;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
}}
.add-panel button.add-btn {{
    background: #4caf50;
    color: #fff;
    border-color: #43a047;
}}
.add-panel button.add-btn:hover {{ background: #43a047; }}
.add-panel button.cancel-btn:hover {{ background: #f0f0f0; }}

/* Custom token indicator */
tr.custom-row {{
    border-left: 3px solid #4caf50;
}}
td .custom-badge {{
    font-size: 9px;
    background: #4caf50;
    color: #fff;
    padding: 1px 4px;
    border-radius: 3px;
    margin-left: 4px;
    vertical-align: middle;
}}
/* Custom category indicator */
.custom-cat {{
    color: #4caf50;
    font-style: italic;
}}

/* Legend */
.legend {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 12px;
    padding: 8px 12px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
}}
.legend-item {{
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
}}
.legend-swatch {{
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid rgba(0,0,0,0.15);
}}
</style>
</head>
<body>

<h1>Rosettes Annotation Tool</h1>
<div class="subtitle">ZL3b-n Rosettes transcription &mdash; 161 loci &mdash; spatial classification</div>

<div class="controls">
    <button class="primary" onclick="saveToFile()">Save JSON</button>
    <button onclick="document.getElementById('file-input').click()">Load JSON</button>
    <input type="file" id="file-input" accept=".json" onchange="loadFromFile(event)">
    <button onclick="resetAll()">Reset All</button>
    <span style="color:#ccc">|</span>
    <button onclick="togglePanel('add-token-panel')" style="background:#e8f5e9;border-color:#4caf50">+ Token</button>
    <button onclick="togglePanel('add-category-panel')" style="background:#e8f5e9;border-color:#4caf50">+ Category</button>
    <span style="color:#ccc">|</span>
    <label>Sort:</label>
    <button id="sort-file" class="active" onclick="setSortMode('file')">File Order</button>
    <button id="sort-grouped" onclick="setSortMode('grouped')">Grouped</button>
    <span style="color:#ccc">|</span>
    <label>Filter:</label>
    <select id="filter-fc" onchange="renderTable()">
        <option value="ALL">All loci</option>
        <option value="MODIFIED">Modified only</option>
        <option value="WITH_NOTES">With notes</option>
        <option value="UNCLASSIFIED">Unclassified</option>
        <optgroup label="Rosettes">
            <option value="NW">NW</option>
            <option value="NORTH">NORTH</option>
            <option value="NE">NE</option>
            <option value="WEST">WEST</option>
            <option value="CENTER">CENTER</option>
            <option value="EAST">EAST</option>
            <option value="SW">SW</option>
            <option value="SOUTH">SOUTH</option>
            <option value="SE">SE</option>
        </optgroup>
        <optgroup label="Paths">
            <option value="__PATHS__">All paths</option>
            <option value="PATH_NW_NORTH">NW &#8596; NORTH</option>
            <option value="PATH_NORTH_NE">NORTH &#8596; NE</option>
            <option value="PATH_NE_EAST">NE &#8596; EAST</option>
            <option value="PATH_EAST_SE">EAST &#8596; SE</option>
            <option value="PATH_SE_SOUTH">SE &#8596; SOUTH</option>
            <option value="PATH_SOUTH_SW">SOUTH &#8596; SW</option>
            <option value="PATH_SW_WEST">SW &#8596; WEST</option>
            <option value="PATH_WEST_NW">WEST &#8596; NW</option>
            <option value="PATH_NW_CENTER">NW &#8596; CENTER</option>
            <option value="PATH_NORTH_CENTER">NORTH &#8596; CENTER</option>
            <option value="PATH_NE_CENTER">NE &#8596; CENTER</option>
            <option value="PATH_EAST_CENTER">EAST &#8596; CENTER</option>
            <option value="PATH_SE_CENTER">SE &#8596; CENTER</option>
            <option value="PATH_SOUTH_CENTER">SOUTH &#8596; CENTER</option>
            <option value="PATH_SW_CENTER">SW &#8596; CENTER</option>
            <option value="PATH_WEST_CENTER">WEST &#8596; CENTER</option>
        </optgroup>
        <optgroup label="Special">
            <option value="CLOCK">Clock</option>
            <option value="SPIRAL">Spiral</option>
            <option value="OUTSIDE_FACE">Outside face</option>
            <option value="INTERSTITIAL">Interstitial</option>
        </optgroup>
    </select>
    <label>Search:</label>
    <input type="text" id="search-box" placeholder="EVA text..." oninput="renderTable()" style="width:140px">
    <label style="font-size:11px;cursor:pointer"><input type="checkbox" id="search-prefix" checked onchange="renderTable()"> prefix only</label>
    <span style="color:#ccc">|</span>
    <label style="font-size:11px;cursor:pointer"><input type="checkbox" id="hide-reviewed" onchange="renderTable()"> hide checked</label>
    <span id="stats"></span>
</div>

<div id="add-token-panel" class="add-panel">
    <h3>Add New Token</h3>
    <div class="form-row">
        <label>EVA text:</label>
        <input type="text" id="new-token-text" placeholder="e.g. okedar">
        <span style="font-family:'EVA2','VoynichEVAHandA','VoynichEVA',serif;font-size:22px" id="new-token-preview"></span>
    </div>
    <div class="form-row">
        <label>Position:</label>
        <input type="text" id="new-token-pos" placeholder="e.g. between NW and NORTH, inside circle, etc.">
    </div>
    <div class="form-row">
        <label>First-class:</label>
        <select id="new-token-fc"></select>
        <label>Second-class:</label>
        <select id="new-token-sc"></select>
    </div>
    <div class="form-row">
        <label>Notes:</label>
        <textarea id="new-token-notes" placeholder="Describe what you see and where..."></textarea>
    </div>
    <div class="btn-row">
        <button class="add-btn" onclick="addCustomToken()">Add Token</button>
        <button class="cancel-btn" onclick="togglePanel('add-token-panel')">Cancel</button>
    </div>
</div>

<div id="add-category-panel" class="add-panel">
    <h3>Add Custom Category</h3>
    <div class="form-row">
        <label>Type:</label>
        <select id="new-cat-type">
            <option value="first_class">First-class (entity)</option>
            <option value="second_class">Second-class (type)</option>
        </select>
    </div>
    <div class="form-row">
        <label>Name:</label>
        <input type="text" id="new-cat-name" placeholder="e.g. PATH_NW_NORTH_INNER or border_label">
    </div>
    <div class="form-row">
        <label>Color:</label>
        <input type="color" id="new-cat-color" value="#c8e6c9" style="min-width:40px;padding:2px">
        <span style="font-size:11px;color:#888">(for first-class only)</span>
    </div>
    <div class="btn-row">
        <button class="add-btn" onclick="addCustomCategory()">Add Category</button>
        <button class="cancel-btn" onclick="togglePanel('add-category-panel')">Cancel</button>
    </div>
</div>

<div class="table-wrap">
<table>
<thead>
<tr>
    <th class="col-chk" style="width:30px;text-align:center">&#10003;</th>
    <th class="col-num">#</th>
    <th class="col-pos">Position</th>
    <th class="col-voynich">Voynich</th>
    <th class="col-eva">EVA Text</th>
    <th class="col-wc">Wds</th>
    <th class="col-fc">First-Class</th>
    <th class="col-sc">Second-Class</th>
    <th class="col-notes">Notes</th>
</tr>
</thead>
<tbody id="loci-table"></tbody>
</table>
</div>

<div class="legend" id="legend"></div>

<script>
// ── Data ──
const LOCI = {loci_json};

const ROSETTES = ['NW','NORTH','NE','WEST','CENTER','EAST','SW','SOUTH','SE'];

const PERIMETER_PATHS = [
    'PATH_NW_NORTH','PATH_NORTH_NE','PATH_NE_EAST','PATH_EAST_SE',
    'PATH_SE_SOUTH','PATH_SOUTH_SW','PATH_SW_WEST','PATH_WEST_NW'
];
const RADIAL_PATHS = [
    'PATH_NW_CENTER','PATH_NORTH_CENTER','PATH_NE_CENTER','PATH_EAST_CENTER',
    'PATH_SE_CENTER','PATH_SOUTH_CENTER','PATH_SW_CENTER','PATH_WEST_CENTER'
];
const ALL_PATHS = [...PERIMETER_PATHS, ...RADIAL_PATHS];

const SPECIAL = ['CLOCK','SPIRAL','OUTSIDE_FACE','INTERSTITIAL'];
let customFC = [];   // user-added first-class categories
let customSC = [];   // user-added second-class categories
let customLoci = []; // user-added tokens
let nextCustomId = 1;

function getAllFC() {{ return [...ROSETTES, ...ALL_PATHS, ...SPECIAL, ...customFC, 'UNCLASSIFIED']; }}
function getAllSC() {{ return [...SECOND_CLASS, ...customSC]; }}
function getAllLoci() {{ return [...LOCI, ...customLoci]; }}

const SECOND_CLASS = [
    'ring','inner_label','outer_label','path_label',
    'paragraph','spiral','clock_text','arc','unclassified'
];

// Display names for paths
const FC_DISPLAY = {{}};
ROSETTES.forEach(r => FC_DISPLAY[r] = r);
ALL_PATHS.forEach(p => {{
    const parts = p.replace('PATH_','').split('_');
    FC_DISPLAY[p] = parts.join(' \\u2194 ');
}});
FC_DISPLAY['CLOCK'] = 'Clock';
FC_DISPLAY['SPIRAL'] = 'Spiral';
FC_DISPLAY['OUTSIDE_FACE'] = 'Outside Face';
FC_DISPLAY['INTERSTITIAL'] = 'Interstitial';
FC_DISPLAY['UNCLASSIFIED'] = 'Unclassified';

const SC_DISPLAY = {{
    'ring': 'Ring text',
    'inner_label': 'Inner label',
    'outer_label': 'Outer label',
    'path_label': 'Path label',
    'paragraph': 'Paragraph',
    'spiral': 'Spiral',
    'clock_text': 'Clock text',
    'arc': 'Arc text',
    'unclassified': 'Unclassified'
}};

// Colors
const COLORS = {{
    'NW': '#e3f2fd', 'NORTH': '#e8f5e9', 'NE': '#fff9c4',
    'WEST': '#f3e5f5', 'CENTER': '#fce4ec', 'EAST': '#fff3e0',
    'SW': '#e0f2f1', 'SOUTH': '#efebe9', 'SE': '#eceff1',
    'CLOCK': '#e8eaf6', 'SPIRAL': '#fbe9e7',
    'OUTSIDE_FACE': '#e0e0e0', 'INTERSTITIAL': '#fff',
    'UNCLASSIFIED': '#fff',
}};
// Paths get a lighter shade
ALL_PATHS.forEach(p => COLORS[p] = '#fffde7');

// ── State ──
let annotations = {{}};

function getAnn(id) {{
    if (annotations[id]) return annotations[id];
    const locus = getAllLoci().find(l => l.id === id);
    return {{
        first_class: locus.default_first_class,
        second_class: locus.default_second_class,
        notes: ''
    }};
}}

function setAnn(id, field, value) {{
    if (!annotations[id]) {{
        const locus = getAllLoci().find(l => l.id === id);
        annotations[id] = {{
            first_class: locus.default_first_class,
            second_class: locus.default_second_class,
            notes: ''
        }};
    }}
    annotations[id][field] = value;
    autoSave();
    updateStats();

    // In file mode, update row in-place for speed
    if (sortMode === 'file') {{
        const row = document.querySelector(`tr[data-id="${{id}}"]`);
        if (row) {{
            row.style.backgroundColor = COLORS[annotations[id].first_class] || '#fff';
            const locus = getAllLoci().find(l => l.id === id);
            const isModified = annotations[id].first_class !== locus.default_first_class
                || annotations[id].second_class !== locus.default_second_class
                || annotations[id].notes.trim() !== '';
            const dot = row.querySelector('.mod-dot');
            if (dot) dot.style.display = isModified ? 'inline-block' : 'none';
            row.querySelectorAll('select').forEach(sel => {{
                const f = sel.dataset.field;
                const def = locus['default_' + f];
                sel.classList.toggle('modified', sel.value !== def);
            }});
            const ta = row.querySelector('textarea');
            if (ta) ta.classList.toggle('has-content', ta.value.trim() !== '');
        }}
    }}
}}

// ── Render ──
function buildFCSelect(selected) {{
    let html = '';
    html += '<optgroup label="Rosettes">';
    ROSETTES.forEach(r => html += `<option value="${{r}}" ${{r===selected?'selected':''}}>${{FC_DISPLAY[r] || r}}</option>`);
    html += '</optgroup>';
    html += '<optgroup label="Perimeter Paths">';
    PERIMETER_PATHS.forEach(p => html += `<option value="${{p}}" ${{p===selected?'selected':''}}>${{FC_DISPLAY[p] || p}}</option>`);
    html += '</optgroup>';
    html += '<optgroup label="Radial Paths">';
    RADIAL_PATHS.forEach(p => html += `<option value="${{p}}" ${{p===selected?'selected':''}}>${{FC_DISPLAY[p] || p}}</option>`);
    html += '</optgroup>';
    html += '<optgroup label="Special">';
    SPECIAL.forEach(s => html += `<option value="${{s}}" ${{s===selected?'selected':''}}>${{FC_DISPLAY[s] || s}}</option>`);
    html += '</optgroup>';
    if (customFC.length > 0) {{
        html += '<optgroup label="Custom">';
        customFC.forEach(c => html += `<option value="${{c}}" ${{c===selected?'selected':''}}>${{FC_DISPLAY[c] || c}}</option>`);
        html += '</optgroup>';
    }}
    html += `<option value="UNCLASSIFIED" ${{selected==='UNCLASSIFIED'?'selected':''}}>Unclassified</option>`;
    return html;
}}

function buildSCSelect(selected) {{
    const all = getAllSC();
    return all.map(s =>
        `<option value="${{s}}" ${{s===selected?'selected':''}}>${{SC_DISPLAY[s] || s}}</option>`
    ).join('');
}}

let sortMode = 'file';  // 'file' or 'grouped'
let collapsedGroups = {{}};  // track collapsed first-class groups

function setSortMode(mode) {{
    sortMode = mode;
    document.getElementById('sort-file').classList.toggle('active', mode === 'file');
    document.getElementById('sort-grouped').classList.toggle('active', mode === 'grouped');
    renderTable();
}}

function toggleGroup(fc) {{
    collapsedGroups[fc] = !collapsedGroups[fc];
    renderTable();
}}

function filterLocus(locus) {{
    const filter = document.getElementById('filter-fc').value;
    const search = document.getElementById('search-box').value.toLowerCase().trim();
    const ann = getAnn(locus.id);
    const isModified = annotations[locus.id] !== undefined;
    const hasNotes = ann.notes.trim() !== '';

    const isReviewed = !!(annotations[locus.id] && annotations[locus.id].reviewed);
    const hideReviewed = document.getElementById('hide-reviewed').checked;

    if (hideReviewed && isReviewed) return false;
    if (filter === 'MODIFIED' && !isModified) return false;
    if (filter === 'WITH_NOTES' && !hasNotes) return false;
    if (filter === 'UNCLASSIFIED' && ann.first_class !== 'UNCLASSIFIED') return false;
    if (filter === '__PATHS__' && !ALL_PATHS.includes(ann.first_class)) return false;
    if (getAllFC().includes(filter) && filter !== 'UNCLASSIFIED' && ann.first_class !== filter) return false;

    if (search) {{
        const prefixOnly = document.getElementById('search-prefix').checked;
        // Split into individual tokens
        const rawWords = locus.text_raw.toLowerCase().replace(/[<>%$\[\]{{}}?'@;]/g,'').split(/[.\s,]+/).filter(w => w);
        const cleanWords = locus.text_clean.toLowerCase().split(/[.\s,]+/).filter(w => w);
        const allWords = [...new Set([...rawWords, ...cleanWords])];
        const matchesToken = prefixOnly
            ? allWords.some(w => w.startsWith(search))
            : allWords.some(w => w.includes(search));
        const matchesId = locus.id.toLowerCase().includes(search);
        const matchesNotes = ann.notes.toLowerCase().includes(search);
        if (!matchesToken && !matchesId && !matchesNotes) return false;
    }}

    return true;
}}

function buildLocusRow(locus) {{
    const ann = getAnn(locus.id);
    const hasNotes = ann.notes.trim() !== '';
    const fcModified = ann.first_class !== locus.default_first_class;
    const scModified = ann.second_class !== locus.default_second_class;
    const anyModified = fcModified || scModified || hasNotes;
    const isRing = ann.second_class === 'ring' || locus.placement.includes('Cc');

    const isCustom = locus.id.startsWith('custom.');
    const tr = document.createElement('tr');
    tr.dataset.id = locus.id;
    tr.style.backgroundColor = COLORS[ann.first_class] || '#fff';
    if (locus.is_continuation) tr.classList.add('continuation');
    if (isCustom) tr.classList.add('custom-row');

    const isReviewed = !!(annotations[locus.id] && annotations[locus.id].reviewed);

    tr.innerHTML = `
        <td style="text-align:center">
            <input type="checkbox" ${{isReviewed ? 'checked' : ''}}
                onchange="setAnn('${{locus.id}}','reviewed',this.checked); if(document.getElementById('filter-fc').value==='UNREVIEWED') renderTable();"
                title="Mark as reviewed">
        </td>
        <td class="num">
            ${{locus.is_continuation ? '<span class="cont-marker">&#8627;</span>' : ''}}
            ${{isCustom ? locus.id.replace('custom.','C') : locus.num}}
            ${{isCustom ? '<span class="custom-badge">new</span>' : ''}}
            ${{anyModified ? '<span class="mod-dot"></span>' : '<span class="mod-dot" style="display:none"></span>'}}
        </td>
        <td class="pos">${{locus.position}}</td>
        <td class="voynich ${{isRing ? 'ring-text' : ''}}">${{escapeHtml(locus.text_clean)}}</td>
        <td class="eva">${{escapeHtml(locus.text_raw)}}</td>
        <td class="wc">${{locus.word_count}}</td>
        <td>
            <select data-field="first_class" class="${{fcModified?'modified':''}}"
                onchange="setAnn('${{locus.id}}','first_class',this.value); renderTable();">
                ${{buildFCSelect(ann.first_class)}}
            </select>
        </td>
        <td>
            <select data-field="second_class" class="${{scModified?'modified':''}}"
                onchange="setAnn('${{locus.id}}','second_class',this.value)">
                ${{buildSCSelect(ann.second_class)}}
            </select>
        </td>
        <td>
            <textarea class="${{hasNotes?'has-content':''}}"
                oninput="setAnn('${{locus.id}}','notes',this.value)"
                placeholder="Notes...">${{escapeHtml(ann.notes)}}</textarea>
        </td>
    `;
    return tr;
}}

function renderTable() {{
    const tbody = document.getElementById('loci-table');
    tbody.innerHTML = '';

    const filtered = getAllLoci().filter(l => filterLocus(l));

    if (sortMode === 'file') {{
        // Simple file order
        for (const locus of filtered) {{
            tbody.appendChild(buildLocusRow(locus));
        }}
    }} else {{
        // Grouped by first-class, then second-class
        // Build groups
        const groups = {{}};
        for (const locus of filtered) {{
            const ann = getAnn(locus.id);
            const fc = ann.first_class;
            const sc = ann.second_class;
            if (!groups[fc]) groups[fc] = {{}};
            if (!groups[fc][sc]) groups[fc][sc] = [];
            groups[fc][sc].push(locus);
        }}

        // Order: rosettes first, then paths, then special, then custom, then unclassified
        const fcOrder = [...ROSETTES, ...ALL_PATHS, ...SPECIAL, ...customFC, 'UNCLASSIFIED'];
        const scOrder = [...SECOND_CLASS, ...customSC];

        for (const fc of fcOrder) {{
            if (!groups[fc]) continue;

            const allInGroup = Object.values(groups[fc]).flat();
            const isCollapsed = collapsedGroups[fc] === true;

            // Group header row
            const hdr = document.createElement('tr');
            hdr.classList.add('group-header');
            hdr.style.backgroundColor = COLORS[fc] || '#fff';
            hdr.onclick = () => toggleGroup(fc);
            hdr.innerHTML = `<td colspan="9">
                <span class="group-toggle">${{isCollapsed ? '&#9654;' : '&#9660;'}}</span>
                ${{FC_DISPLAY[fc] || fc}}
                <span class="group-count">${{allInGroup.length}} loci</span>
            </td>`;
            tbody.appendChild(hdr);

            if (isCollapsed) continue;

            // Subgroups by second-class
            const subclasses = Object.keys(groups[fc]);
            const hasMultipleSC = subclasses.length > 1;

            for (const sc of scOrder) {{
                if (!groups[fc][sc]) continue;

                // Subgroup header (only if multiple second-class types in this group)
                if (hasMultipleSC) {{
                    const shdr = document.createElement('tr');
                    shdr.classList.add('subgroup-header');
                    shdr.style.backgroundColor = COLORS[fc] || '#fff';
                    shdr.innerHTML = `<td colspan="9">${{SC_DISPLAY[sc] || sc}}
                        <span class="group-count">${{groups[fc][sc].length}}</span>
                    </td>`;
                    tbody.appendChild(shdr);
                }}

                // Locus rows (sorted by locus number within subgroup)
                for (const locus of groups[fc][sc].sort((a,b) => a.num - b.num)) {{
                    tbody.appendChild(buildLocusRow(locus));
                }}
            }}
        }}
    }}
    updateStats();
}}

function escapeHtml(s) {{
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
            .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}}

// ── Stats ──
function updateStats() {{
    const allLoci = getAllLoci();
    const modified = Object.keys(annotations).filter(id => {{
        const locus = allLoci.find(l => l.id === id);
        if (!locus) return false;
        const a = annotations[id];
        return a.first_class !== locus.default_first_class
            || a.second_class !== locus.default_second_class
            || a.notes.trim() !== '';
    }}).length;
    const withNotes = Object.values(annotations).filter(a => a.notes.trim() !== '').length;
    const visible = document.querySelectorAll('#loci-table tr:not(.group-header):not(.subgroup-header)').length;
    const reviewed = Object.values(annotations).filter(a => a.reviewed).length;
    document.getElementById('stats').textContent =
        `${{allLoci.length}} loci | ${{reviewed}} reviewed | ${{modified}} modified | ${{withNotes}} notes | ${{visible}} shown`;
}}

// ── Persistence ──
const STORAGE_KEY = 'rosettes_annotations_v1';

function getFullState() {{
    return {{
        annotations: annotations,
        customLoci: customLoci,
        customFC: customFC,
        customSC: customSC,
        nextCustomId: nextCustomId
    }};
}}

function loadFullState(state) {{
    annotations = state.annotations || {{}};
    customLoci = state.customLoci || [];
    customFC = state.customFC || [];
    customSC = state.customSC || [];
    nextCustomId = state.nextCustomId || (customLoci.length + 1);
    // Restore custom display names and colors
    customFC.forEach(c => {{
        if (!FC_DISPLAY[c]) FC_DISPLAY[c] = c;
        if (!COLORS[c]) COLORS[c] = '#c8e6c9';
    }});
    customSC.forEach(c => {{
        if (!SC_DISPLAY[c]) SC_DISPLAY[c] = c;
    }});
}}

function autoSave() {{
    try {{
        localStorage.setItem(STORAGE_KEY, JSON.stringify(getFullState()));
    }} catch(e) {{
        console.warn('localStorage save failed:', e);
    }}
}}

function autoLoad() {{
    try {{
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {{
            const state = JSON.parse(saved);
            // Handle v1 format (annotations only) vs v2 (full state)
            if (state.annotations && (state.customLoci !== undefined || state.customFC !== undefined)) {{
                loadFullState(state);
            }} else if (state.annotations) {{
                annotations = state.annotations;
            }} else {{
                // Legacy: bare annotations object
                annotations = state;
            }}
        }}
    }} catch(e) {{
        console.warn('localStorage load failed:', e);
    }}
}}

function saveToFile() {{
    const data = {{
        version: 2,
        timestamp: new Date().toISOString(),
        source: 'ZL3b-n Rosettes transcription',
        locus_count: getAllLoci().length,
        ...getFullState()
    }};
    const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rosettes_annotations.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}}

function loadFromFile(event) {{
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {{
        try {{
            const data = JSON.parse(e.target.result);
            if (data.version === 2 || data.customLoci) {{
                loadFullState(data);
            }} else if (data.annotations) {{
                annotations = data.annotations;
            }}
            autoSave();
            renderTable();
            alert(`Loaded ${{getAllLoci().length}} loci (${{customLoci.length}} custom).`);
        }} catch(err) {{
            alert('Error loading file: ' + err.message);
        }}
    }};
    reader.readAsText(file);
    event.target.value = '';
}}

function resetAll() {{
    if (!confirm('Reset ALL annotations, custom tokens, and custom categories? This cannot be undone.')) return;
    annotations = {{}};
    customLoci = [];
    customFC = [];
    customSC = [];
    nextCustomId = 1;
    autoSave();
    renderTable();
}}

// ── Add Token ──
function togglePanel(id) {{
    const panel = document.getElementById(id);
    panel.classList.toggle('open');
    // Populate dropdowns when opening add-token panel
    if (id === 'add-token-panel' && panel.classList.contains('open')) {{
        document.getElementById('new-token-fc').innerHTML = buildFCSelect('UNCLASSIFIED');
        document.getElementById('new-token-sc').innerHTML = buildSCSelect('unclassified');
        document.getElementById('new-token-text').focus();
    }}
}}

// Live preview of EVA text in Voynich font
document.addEventListener('DOMContentLoaded', () => {{
    const inp = document.getElementById('new-token-text');
    if (inp) inp.addEventListener('input', () => {{
        document.getElementById('new-token-preview').textContent = inp.value;
    }});
}});

function addCustomToken() {{
    const text = document.getElementById('new-token-text').value.trim();
    if (!text) {{ alert('Please enter EVA text.'); return; }}

    const pos = document.getElementById('new-token-pos').value.trim();
    const fc = document.getElementById('new-token-fc').value;
    const sc = document.getElementById('new-token-sc').value;
    const notes = document.getElementById('new-token-notes').value.trim();

    const id = `custom.${{nextCustomId++}}`;
    const words = text.split(/[.\s,]+/).filter(w => w);

    const locus = {{
        id: id,
        num: 0,
        placement: 'custom',
        position: pos,
        text_raw: text,
        text_clean: text.replace(/[?']/g, ''),
        is_continuation: false,
        word_count: words.length,
        default_first_class: fc,
        default_second_class: sc,
    }};
    customLoci.push(locus);

    // Set annotation with notes
    annotations[id] = {{
        first_class: fc,
        second_class: sc,
        notes: notes
    }};

    // Clear form
    document.getElementById('new-token-text').value = '';
    document.getElementById('new-token-pos').value = '';
    document.getElementById('new-token-notes').value = '';
    document.getElementById('new-token-preview').textContent = '';

    autoSave();
    renderTable();
    togglePanel('add-token-panel');
}}

// ── Add Category ──
function addCustomCategory() {{
    const type = document.getElementById('new-cat-type').value;
    const name = document.getElementById('new-cat-name').value.trim();
    if (!name) {{ alert('Please enter a category name.'); return; }}

    // Sanitize: replace spaces with underscores, uppercase for FC
    const key = type === 'first_class'
        ? name.toUpperCase().replace(/\s+/g, '_')
        : name.toLowerCase().replace(/\s+/g, '_');

    // Check for duplicates
    if (type === 'first_class') {{
        if (getAllFC().includes(key)) {{ alert(`"${{key}}" already exists.`); return; }}
        customFC.push(key);
        FC_DISPLAY[key] = name;
        COLORS[key] = document.getElementById('new-cat-color').value;
    }} else {{
        if (getAllSC().includes(key)) {{ alert(`"${{key}}" already exists.`); return; }}
        customSC.push(key);
        SC_DISPLAY[key] = name;
    }}

    // Clear form
    document.getElementById('new-cat-name').value = '';

    autoSave();
    renderTable();
    togglePanel('add-category-panel');
    alert(`Added ${{type === 'first_class' ? 'first' : 'second'}}-class category: ${{name}}`);
}}

// ── Legend ──
function buildLegend() {{
    const legend = document.getElementById('legend');
    const entries = [
        ...ROSETTES.map(r => [r, COLORS[r]]),
        ['Paths', '#fffde7'],
        ['Clock', COLORS.CLOCK],
        ['Spiral', COLORS.SPIRAL],
        ['Outside', COLORS.OUTSIDE_FACE],
    ];
    legend.innerHTML = entries.map(([name, color]) =>
        `<div class="legend-item">
            <div class="legend-swatch" style="background:${{color}}"></div>
            <span>${{name}}</span>
        </div>`
    ).join('');
}}

// ── Init ──
autoLoad();
buildLegend();
renderTable();
</script>
</body>
</html>'''


def main():
    loci = parse_zl_data()
    print(f"Parsed {len(loci)} loci from ZL data")

    html = generate_html(loci)

    out_dir = PROJECT / 'phases' / 'ROSETTES_FUNCTIONAL_ANATOMY' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / 'rosettes_annotation_tool.html'
    out_file.write_text(html, encoding='utf-8')

    # Copy fonts
    font_dir = PROJECT / 'vee' / 'app' / 'fonts'
    for font_name in ['EVA2.ttf', 'VoynichEVA.ttf', 'VoynichEVAHandA.ttf']:
        src = font_dir / font_name
        if src.exists():
            shutil.copy2(src, out_dir / font_name)
            print(f"  Copied {font_name}")

    print(f"\nAnnotation tool: {out_file}")
    print("Open in browser to begin annotating.")


if __name__ == '__main__':
    main()
