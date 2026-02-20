"""Build annotated Rosettes JSON from ZL transcription + user spatial annotations.

Inputs:
  - data/zl_rosettes.txt (ZL transcription)
  - User annotations JSON (spatial classifications)
  - scripts/voynich.py (morphological analysis)

Output:
  - data/rosettes_annotated.json
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))

from scripts.voynich import Morphology, MiddleAnalyzer

# ZL area → rosette
AREA_TO_ROSETTE = {
    '1': 'NW', '2': 'WEST', '3': 'SW', '4': 'NORTH',
    '5': 'CENTER', '6': 'SOUTH', '7': 'NE', '8': 'EAST', '9': 'SE',
}

RING_TO_ROSETTE = {
    2: 'NW', 20: 'NORTH', 35: 'NE',
    47: 'WEST', 62: 'CENTER', 87: 'EAST',
    94: 'SW', 122: 'SOUTH', 133: 'SE',
}

ROMAN_POSITIONS = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'}


def clean_eva(text):
    """Strip IVTFF markup, return clean EVA."""
    s = text
    s = re.sub(r'\[([^:]+):[^\]]+\]', r'\1', s)
    s = re.sub(r'\{[^}]+\}', '', s)
    s = s.replace('<%>', '').replace('<$>', '')
    s = s.replace('<->', '.')
    s = re.sub(r'@\d+;', '', s)
    s = s.replace("'", '')
    return s.strip()


def split_words(text):
    """Split EVA text into individual tokens."""
    clean = clean_eva(text)
    words = [w.strip() for w in re.split(r'[.\s]+', clean) if w.strip()]
    # Remove lone punctuation and question marks
    words = [w for w in words if w and w != '?' and not all(c in ',?!' for c in w)]
    return words


def parse_zl():
    """Parse ZL transcription into loci."""
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

        positions = re.findall(r'<!([^>]+)>', rest)
        text_part = re.sub(r'<![^>]+>', '', rest).strip()
        position_str = '; '.join(positions) if positions else ''

        is_continuation = placement[0] in ('+', '*', '/')

        # Detect outside face
        is_outside = any(p.strip() in ROMAN_POSITIONS for p in positions)
        if is_outside:
            skip_continuations = True
            continue
        if is_continuation and skip_continuations:
            continue
        skip_continuations = False

        words = split_words(text_part)

        loci.append({
            'id': f'fRos.{num}',
            'num': num,
            'placement': placement,
            'position': position_str,
            'text_raw': text_part,
            'text_clean': clean_eva(text_part),
            'words': words,
            'is_continuation': is_continuation,
        })

    return loci


def load_annotations(path):
    """Load user annotations JSON."""
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    annotations = data.get('annotations', {})
    custom_loci = data.get('customLoci', [])
    return annotations, custom_loci


def analyze_token(word, morph, bridge_set):
    """Morphological analysis of a single token."""
    w = word.strip().rstrip(',')
    if not w or w == '?':
        return None

    try:
        m = morph.extract(w)
        middle = m.middle if m else None
        result = {
            'word': w,
            'articulator': m.articulator if m else None,
            'prefix': m.prefix if m else None,
            'middle': middle,
            'suffix': m.suffix if m else None,
            'is_bridge': middle in bridge_set if middle else False,
        }
        return result
    except Exception:
        return {
            'word': w,
            'articulator': None,
            'prefix': None,
            'middle': None,
            'suffix': None,
            'is_bridge': False,
        }


def main():
    annotations_path = PROJECT / 'phases' / 'ROSETTES_FUNCTIONAL_ANATOMY' / 'results' / 'rosettes_annotations.json'

    # Check for annotations file
    desktop_path = Path(r'C:\Users\epilectrik\Desktop\fb\rosettes_annotations.json')
    if desktop_path.exists():
        ann_path = desktop_path
    elif annotations_path.exists():
        ann_path = annotations_path
    else:
        print("ERROR: No annotations file found.")
        print(f"  Checked: {desktop_path}")
        print(f"  Checked: {annotations_path}")
        return

    print(f"Annotations: {ann_path}")
    annotations, custom_loci = load_annotations(ann_path)

    # Parse ZL data
    loci = parse_zl()
    print(f"ZL loci: {len(loci)}")

    # Add custom loci
    for cl in custom_loci:
        cl['words'] = split_words(cl['text_raw'])
        cl['is_continuation'] = False
        loci.append(cl)
    print(f"Custom loci: {len(custom_loci)}")

    # Build morphology + bridge set
    morph = Morphology()
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')
    bridge_set = set(mid_analyzer.get_bridge_middles()) if hasattr(mid_analyzer, 'get_bridge_middles') else set()

    # If bridge set not available from MiddleAnalyzer, load from file
    if not bridge_set:
        bridge_file = PROJECT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
        if bridge_file.exists():
            bd = json.loads(bridge_file.read_text(encoding='utf-8'))
            bridge_set = set(bd.get('t5_structural_profile', {}).get('bridge_middles', []))
            print(f"Bridge MIDDLEs loaded: {len(bridge_set)}")

    # Build output structure organized by first-class entity
    entities = defaultdict(lambda: {
        'tokens': [],
        'sub_regions': defaultdict(list),
        'total_words': 0,
        'loci': [],
        'notes': [],
    })

    unclassified_loci = []

    for locus in loci:
        lid = locus['id']
        ann = annotations.get(lid, {})

        first_class = ann.get('first_class', None)
        second_class = ann.get('second_class', None)
        notes = ann.get('notes', '')
        reviewed = ann.get('reviewed', False)

        # Fall back to defaults if no annotation
        if not first_class:
            # Determine from ZL data
            num = locus.get('num', 0)
            if num in RING_TO_ROSETTE:
                first_class = RING_TO_ROSETTE[num]
                second_class = 'ring'
            elif locus.get('position'):
                area_m = re.match(r'(\d+):', locus['position'])
                if area_m and area_m.group(1) in AREA_TO_ROSETTE:
                    first_class = AREA_TO_ROSETTE[area_m.group(1)]
                    second_class = second_class or 'inner_label'
            if not first_class:
                first_class = 'UNCLASSIFIED'
                second_class = second_class or 'unclassified'

        if not second_class:
            second_class = 'unclassified'

        # Analyze tokens
        analyzed_words = []
        for w in locus.get('words', []):
            tok = analyze_token(w, morph, bridge_set)
            if tok:
                analyzed_words.append(tok)

        locus_entry = {
            'locus_id': lid,
            'position': locus.get('position', ''),
            'placement': locus.get('placement', ''),
            'first_class': first_class,
            'second_class': second_class,
            'text_raw': locus.get('text_raw', ''),
            'text_clean': locus.get('text_clean', ''),
            'words': analyzed_words,
            'word_count': len(analyzed_words),
            'reviewed': reviewed,
            'notes': notes,
            'is_custom': lid.startswith('custom.'),
        }

        entity = entities[first_class]
        entity['loci'].append(locus_entry)
        entity['sub_regions'][second_class].append(lid)
        entity['total_words'] += len(analyzed_words)
        entity['tokens'].extend(analyzed_words)
        if notes and notes != 'x':
            entity['notes'].append(f"{lid}: {notes}")

    # Build summary
    summary = {
        'total_entities': len(entities),
        'total_loci': len(loci),
        'total_words': sum(e['total_words'] for e in entities.values()),
        'reviewed': sum(1 for l in loci if annotations.get(l['id'], {}).get('reviewed', False)),
        'entities': {}
    }

    for name, entity in sorted(entities.items()):
        summary['entities'][name] = {
            'loci_count': len(entity['loci']),
            'word_count': entity['total_words'],
            'sub_regions': {k: len(v) for k, v in entity['sub_regions'].items()},
        }

    # Build output
    output = {
        '_metadata': {
            'version': '2.0',
            'description': 'Annotated Rosettes foldout — ZL transcription + manual spatial classification',
            'zl_source': 'voynich.nu ZL3b-n.txt (Zandbergen transcription)',
            'annotations_source': str(ann_path.name),
            'annotations_timestamp': json.loads(ann_path.read_text(encoding='utf-8')).get('timestamp', 'unknown'),
            'total_loci': len(loci),
            'total_words': summary['total_words'],
            'reviewed_loci': summary['reviewed'],
            'entity_count': len(entities),
            'bridge_middles_available': len(bridge_set),
            'notes': [
                'First-class = spatial entity (rosette, path, clock, etc.)',
                'Second-class = token type within entity (ring, inner_label, outer_label, etc.)',
                'Paths are first-class entities connecting adjacent rosettes',
                'Transcription corrections noted in individual locus notes',
                'Outside face tokens (Roman numerals I-VIII) excluded — separate treatment needed',
            ],
        },
        'summary': summary,
        'entities': {},
    }

    # Sort entities: rosettes, then paths, then special
    rosette_order = ['NW', 'NORTH', 'NE', 'WEST', 'CENTER', 'EAST', 'SW', 'SOUTH', 'SE']
    path_keys = sorted([k for k in entities if k.startswith('PATH_')])
    special_keys = sorted([k for k in entities if k not in rosette_order and not k.startswith('PATH_')])
    entity_order = [k for k in rosette_order if k in entities] + path_keys + special_keys

    for name in entity_order:
        entity = entities[name]
        # Build sub-region structure
        sub_regions = {}
        for sc, locus_ids in entity['sub_regions'].items():
            sc_loci = [l for l in entity['loci'] if l['locus_id'] in locus_ids]
            sub_regions[sc] = {
                'loci_count': len(sc_loci),
                'word_count': sum(l['word_count'] for l in sc_loci),
                'loci': sc_loci,
            }

        # Collect all unique MIDDLEs
        all_middles = set()
        bridge_middles = set()
        non_bridge_middles = set()
        for tok in entity['tokens']:
            if tok['middle']:
                all_middles.add(tok['middle'])
                if tok['is_bridge']:
                    bridge_middles.add(tok['middle'])
                else:
                    non_bridge_middles.add(tok['middle'])

        output['entities'][name] = {
            'total_loci': len(entity['loci']),
            'total_words': entity['total_words'],
            'unique_middles': sorted(all_middles),
            'bridge_middles': sorted(bridge_middles),
            'non_bridge_middles': sorted(non_bridge_middles),
            'sub_regions': sub_regions,
            'notes': entity['notes'] if entity['notes'] else [],
        }

    # Write output
    out_file = PROJECT / 'data' / 'rosettes_annotated.json'
    out_file.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')

    # Print summary
    print(f"\nOutput: {out_file}")
    print(f"Total entities: {len(entities)}")
    print(f"Total loci: {len(loci)}")
    print(f"Total words: {summary['total_words']}")
    print(f"Reviewed: {summary['reviewed']}/{len(loci)}")
    print()
    for name in entity_order:
        e = summary['entities'][name]
        subs = ', '.join(f"{k}:{v}" for k, v in e['sub_regions'].items())
        print(f"  {name:25s} {e['loci_count']:3d} loci  {e['word_count']:4d} words  [{subs}]")


if __name__ == '__main__':
    main()
