#!/usr/bin/env python3
"""
Analyze PREFIX patterns in pharma labels.

Question: Do prefixes reveal the organizational structure?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent

def get_prefix(token, max_len=3):
    """Extract prefix from token."""
    prefixes = ['qok', 'qot', 'cph', 'cth', 'pch', 'tch', 'ckh', 'qo', 'ch', 'sh',
                'ok', 'ot', 'op', 'ol', 'or', 'da', 'sa', 'so', 'ct', 'yk', 'do',
                'ar', 'po', 'oe', 'os', 'al', 'oe', 'of', 'cp', 'ko', 'yd', 'sy']

    for p in sorted(prefixes, key=len, reverse=True):
        if token.startswith(p):
            return p
    return token[:2] if len(token) >= 2 else token

def load_all_labels():
    """Load all jar and content labels from mapping files."""
    pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'

    results = []

    for json_file in pharma_dir.glob('*_mapping.json'):
        with open(json_file) as f:
            data = json.load(f)

        folio = data.get('folio', json_file.stem)
        plant_part = data.get('plant_part', 'unknown')

        if 'groups' in data:
            for group in data['groups']:
                row = group.get('row', group.get('placement', '?'))

                jar = group.get('jar')
                if jar and isinstance(jar, str):
                    results.append({
                        'folio': folio,
                        'row': row,
                        'type': 'jar',
                        'token': jar,
                        'prefix': get_prefix(jar),
                        'plant_part': plant_part
                    })

                # Content labels
                for key in ['roots', 'leaves', 'labels']:
                    if key in group:
                        for item in group[key]:
                            if isinstance(item, dict):
                                token = item.get('token', '')
                            else:
                                token = item
                            if token and isinstance(token, str) and '*' not in token:
                                results.append({
                                    'folio': folio,
                                    'row': row,
                                    'type': 'content',
                                    'token': token,
                                    'prefix': get_prefix(token),
                                    'plant_part': plant_part
                                })

        # Handle flat label lists
        if 'labels' in data and 'groups' not in data:
            for label in data['labels']:
                if isinstance(label, dict):
                    token = label.get('token', '')
                else:
                    token = label
                if token and isinstance(token, str) and '*' not in token:
                    results.append({
                        'folio': folio,
                        'row': '?',
                        'type': 'content',
                        'token': token,
                        'prefix': get_prefix(token),
                        'plant_part': plant_part
                    })

    return results

if __name__ == '__main__':
    print("=" * 70)
    print("PREFIX PATTERN ANALYSIS")
    print("=" * 70)

    labels = load_all_labels()
    print(f"\nLoaded {len(labels)} labels")

    # Separate jars and contents
    jars = [l for l in labels if l['type'] == 'jar']
    contents = [l for l in labels if l['type'] == 'content']

    print(f"Jars: {len(jars)}, Contents: {len(contents)}")

    # PREFIX distribution
    print("\n" + "=" * 70)
    print("PREFIX DISTRIBUTION")
    print("=" * 70)

    jar_prefixes = Counter(j['prefix'] for j in jars)
    content_prefixes = Counter(c['prefix'] for c in contents)

    print("\nJAR PREFIXES:")
    for prefix, count in jar_prefixes.most_common():
        print(f"  {prefix}: {count}")

    print("\nCONTENT PREFIXES (top 20):")
    for prefix, count in content_prefixes.most_common(20):
        print(f"  {prefix}: {count}")

    # PREFIX overlap
    print("\n" + "=" * 70)
    print("PREFIX VOCABULARY COMPARISON")
    print("=" * 70)

    jar_prefix_set = set(jar_prefixes.keys())
    content_prefix_set = set(content_prefixes.keys())

    print(f"\nJar prefix vocabulary: {len(jar_prefix_set)}")
    print(f"Content prefix vocabulary: {len(content_prefix_set)}")
    print(f"Overlap: {len(jar_prefix_set & content_prefix_set)}")
    print(f"Jar-only prefixes: {jar_prefix_set - content_prefix_set}")
    print(f"Content-only prefixes: {content_prefix_set - jar_prefix_set}")

    # Root vs Leaf prefix patterns
    print("\n" + "=" * 70)
    print("ROOT vs LEAF PREFIX PATTERNS")
    print("=" * 70)

    root_contents = [c for c in contents if c['plant_part'] == 'root']
    leaf_contents = [c for c in contents if c['plant_part'] == 'leaf']

    root_prefixes = Counter(c['prefix'] for c in root_contents)
    leaf_prefixes = Counter(c['prefix'] for c in leaf_contents)

    print(f"\nROOT prefixes ({len(root_contents)} labels):")
    for prefix, count in root_prefixes.most_common(15):
        print(f"  {prefix}: {count} ({100*count/len(root_contents):.1f}%)")

    print(f"\nLEAF prefixes ({len(leaf_contents)} labels):")
    for prefix, count in leaf_prefixes.most_common(15):
        print(f"  {prefix}: {count} ({100*count/len(leaf_contents):.1f}%)")

    # Prefix lean scores
    print("\n" + "=" * 70)
    print("PREFIX LEAN SCORES (root vs leaf preference)")
    print("=" * 70)

    all_prefixes = set(root_prefixes.keys()) | set(leaf_prefixes.keys())

    lean_scores = []
    for prefix in all_prefixes:
        root_count = root_prefixes.get(prefix, 0)
        leaf_count = leaf_prefixes.get(prefix, 0)
        total = root_count + leaf_count

        if total >= 3:  # Minimum occurrences
            lean = (root_count - leaf_count) / total  # +1 = all root, -1 = all leaf
            lean_scores.append((prefix, lean, root_count, leaf_count))

    print(f"\n{'Prefix':<8} {'Lean':<10} {'Root':<6} {'Leaf':<6} {'Direction'}")
    print("-" * 50)

    for prefix, lean, rc, lc in sorted(lean_scores, key=lambda x: x[1], reverse=True):
        direction = "ROOT" if lean > 0.3 else "LEAF" if lean < -0.3 else "MIXED"
        print(f"{prefix:<8} {lean:+.2f}      {rc:<6} {lc:<6} {direction}")

    # Folio-by-folio breakdown
    print("\n" + "=" * 70)
    print("FOLIO-BY-FOLIO PREFIX BREAKDOWN")
    print("=" * 70)

    folios = sorted(set(l['folio'] for l in labels))

    for folio in folios:
        folio_labels = [l for l in labels if l['folio'] == folio]
        folio_jars = [l for l in folio_labels if l['type'] == 'jar']
        folio_contents = [l for l in folio_labels if l['type'] == 'content']

        print(f"\n--- {folio.upper()} ---")
        if folio_jars:
            jar_strs = [f"{j['token']} ({j['prefix']})" for j in folio_jars]
            print(f"Jars: {', '.join(jar_strs)}")

        content_by_prefix = defaultdict(list)
        for c in folio_contents:
            content_by_prefix[c['prefix']].append(c['token'])

        print(f"Contents by prefix:")
        for prefix in sorted(content_by_prefix.keys()):
            tokens = content_by_prefix[prefix]
            print(f"  {prefix}: {len(tokens)} - {tokens[:5]}{'...' if len(tokens) > 5 else ''}")

    # Look for prefix sequences within folios
    print("\n" + "=" * 70)
    print("PREFIX SEQUENCES (f88v, f89r1, f89r2)")
    print("=" * 70)

    for folio in ['f88v', 'f89r1', 'f89r2']:
        folio_labels = [l for l in labels if l['folio'] == folio]

        # Group by row
        rows = defaultdict(list)
        for l in folio_labels:
            rows[l['row']].append(l)

        print(f"\n--- {folio.upper()} ---")
        for row in sorted(rows.keys(), key=str):
            row_labels = rows[row]
            prefix_seq = [l['prefix'] for l in row_labels]
            print(f"Row {row}: {' → '.join(prefix_seq)}")
