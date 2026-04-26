"""
Phase 657 s1 — Catalan Numerical-Anchor Extractor

Reads CONNECTIVE_CORPUS.json, extracts REPETITION instances with adjacent
numerical counts per locked PRE_REGISTRATION.md section 1.

No fuzzy matching. N >= 3 inclusion bar.

Output: results/NUMERICAL_ANCHORS.json
"""

import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Locked patterns
RE_ROMAN = re.compile(r'\b\.?\s*([ivxlcdm]+)\.?\s*$', re.IGNORECASE)
RE_WORD = re.compile(
    r'\b(una|un|dos|dues|tres|quatre|cinch|cinc|sis|set|huit|vuit|nou|deu|onze|dotze)\s*$',
    re.IGNORECASE,
)
RE_ARAB = re.compile(r'\b(\d+)\s*$')

WORD_MAP = {
    'una': 1, 'un': 1,
    'dos': 2, 'dues': 2,
    'tres': 3,
    'quatre': 4,
    'cinch': 5, 'cinc': 5,
    'sis': 6,
    'set': 7,
    'huit': 8, 'vuit': 8,
    'nou': 9,
    'deu': 10,
    'onze': 11,
    'dotze': 12,
}

ROMAN_MAP = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000}


def roman_to_int(s):
    s = s.lower()
    if any(c not in ROMAN_MAP for c in s):
        return None
    total = 0
    prev = 0
    for c in reversed(s):
        v = ROMAN_MAP[c]
        if v < prev:
            total -= v
        else:
            total += v
            prev = v
    return total


def extract_count(context_left):
    """Return (count_int, kind, raw) or None."""
    tail = context_left[-30:]
    m = RE_ROMAN.search(tail)
    if m:
        v = roman_to_int(m.group(1))
        if v is not None:
            return v, 'roman', m.group(1)
    m = RE_WORD.search(tail)
    if m:
        w = m.group(1).lower()
        if w in WORD_MAP:
            return WORD_MAP[w], 'word', m.group(1)
    m = RE_ARAB.search(tail)
    if m:
        return int(m.group(1)), 'arab', m.group(1)
    return None


def main():
    repo_root = Path(__file__).resolve().parents[3]
    src = repo_root / 'phases' / 'PHASE_656_CATALAN_CONNECTIVE_CORPUS' / 'results' / 'CONNECTIVE_CORPUS.json'
    out_dir = repo_root / 'phases' / 'PHASE_657_CYCLE_ANCHOR_ALIGNMENT' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f'reading {src}')
    data = json.loads(src.read_text(encoding='utf-8'))
    rep_instances = [r for r in data['instances'] if r['category'] == 'REPETITION']
    print(f'  REPETITION instances: {len(rep_instances)}')

    anchors = []
    for r in rep_instances:
        c = extract_count(r['context_left'])
        if c is None:
            continue
        count_int, kind, raw = c
        anchors.append({
            'subrecipe_id': r['subrecipe_id'],
            'part': r['part'],
            'chapter_num': r['chapter_num'],
            'sub_idx': r['sub_idx'],
            'char_offset': r['char_offset'],
            'count': count_int,
            'count_kind': kind,
            'count_raw': raw,
            'surface_form': r['surface_form'],
            'context_left_tail': r['context_left'][-30:],
            'context_right_head': r['context_right'][:30],
        })

    # Apply N >= 3 inclusion bar (locked)
    in_set = [a for a in anchors if a['count'] >= 3]
    excluded = [a for a in anchors if a['count'] < 3]

    print(f'  with adjacent numerical count: {len(anchors)}')
    print(f'  passing N >= 3 inclusion bar:  {len(in_set)}')
    print(f'  excluded (N < 3):              {len(excluded)}')
    print()
    print('In-set items (locked test items):')
    for a in in_set:
        print(f'  {a["subrecipe_id"]:12s}  N={a["count"]:2d}  '
              f'({a["count_kind"]}: \'{a["count_raw"]}\')  '
              f'off={a["char_offset"]}  '
              f'ctx="...{a["context_left_tail"][-25:]}[{a["surface_form"]}]"')

    out_path = out_dir / 'NUMERICAL_ANCHORS.json'
    out_path.write_text(json.dumps({
        'phase': 657,
        'stage': 'B',
        'script': 's1',
        'pre_registration_commit': '7227532',
        'source_corpus': 'phases/PHASE_656_CATALAN_CONNECTIVE_CORPUS/results/CONNECTIVE_CORPUS.json',
        'inclusion_bar': 'N >= 3',
        'in_set_count': len(in_set),
        'in_set': in_set,
        'excluded_count': len(excluded),
        'excluded': excluded,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\nwrote {out_path}')


if __name__ == '__main__':
    main()
