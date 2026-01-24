#!/usr/bin/env python3
"""
Check if pharma plant labels appear in Currier A text.

Questions:
1. Do any pharma labels appear as complete tokens in Currier A?
2. Do they appear as PP (shared with B) or RI (A-exclusive)?
3. Do their MIDDLEs appear as substrings in Currier A MIDDLEs?
"""

import json
import sys
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent

def extract_middle(token):
    """Extract MIDDLE from token."""
    prefixes = ['qok', 'qot', 'cph', 'cth', 'pch', 'tch', 'ckh', 'qo', 'ch', 'sh',
                'ok', 'ot', 'op', 'ol', 'or', 'da', 'sa', 'so', 'ct', 'yk', 'do',
                'ar', 'po', 'oe', 'os', 'al', 'of', 'cp', 'ko', 'yd', 'sy']
    suffixes = ['aiin', 'oiin', 'iin', 'ain', 'dy', 'hy', 'ky', 'ly', 'my', 'ny',
                'ry', 'sy', 'ty', 'am', 'an', 'al', 'ar', 'ol', 'or', 'y', 's',
                'g', 'd', 'l', 'r', 'n', 'm']

    middle = str(token).strip()
    for p in sorted(prefixes, key=len, reverse=True):
        if middle.startswith(p) and len(middle) > len(p):
            middle = middle[len(p):]
            break
    for s in sorted(suffixes, key=len, reverse=True):
        if middle.endswith(s) and len(middle) > len(s):
            middle = middle[:-len(s)]
            break
    return middle if middle and middle != token else None

def load_pharma_labels():
    """Load all pharma labels."""
    pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'
    labels = set()

    for json_file in pharma_dir.glob('*_mapping.json'):
        with open(json_file) as f:
            data = json.load(f)

        if 'groups' in data:
            for group in data['groups']:
                jar = group.get('jar')
                if jar and isinstance(jar, str):
                    labels.add(jar)

                for key in ['roots', 'leaves', 'labels']:
                    if key in group:
                        for item in group[key]:
                            if isinstance(item, dict):
                                token = item.get('token', '')
                            else:
                                token = item
                            if token and isinstance(token, str) and '*' not in token:
                                labels.add(token)

        if 'labels' in data and 'groups' not in data:
            for label in data['labels']:
                if isinstance(label, dict):
                    token = label.get('token', '')
                else:
                    token = label
                if token and isinstance(token, str) and '*' not in token:
                    labels.add(token)

    return labels

if __name__ == '__main__':
    print("=" * 70)
    print("PHARMA LABELS IN CURRIER A CHECK")
    print("=" * 70)

    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']

    # Separate by language, excluding labels
    df_text = df[~df['placement'].str.startswith('L', na=False)]

    a_tokens = set(df_text[df_text['language'] == 'A']['word'].dropna().unique())
    b_tokens = set(df_text[df_text['language'] == 'B']['word'].dropna().unique())

    pp_tokens = a_tokens & b_tokens  # Shared
    ri_tokens = a_tokens - b_tokens  # A-exclusive

    print(f"\nCurrier A tokens: {len(a_tokens)}")
    print(f"  PP (shared with B): {len(pp_tokens)}")
    print(f"  RI (A-exclusive): {len(ri_tokens)}")

    # Load pharma labels
    pharma_labels = load_pharma_labels()
    print(f"\nPharma labels: {len(pharma_labels)}")

    # Check 1: Exact token matches
    print("\n" + "=" * 70)
    print("CHECK 1: EXACT TOKEN MATCHES")
    print("=" * 70)

    labels_in_a = pharma_labels & a_tokens
    labels_in_pp = pharma_labels & pp_tokens
    labels_in_ri = pharma_labels & ri_tokens
    labels_in_b_only = pharma_labels & (b_tokens - a_tokens)

    print(f"\nPharma labels that ARE Currier A tokens: {len(labels_in_a)}")
    print(f"  - As PP (shared): {len(labels_in_pp)}")
    print(f"  - As RI (A-exclusive): {len(labels_in_ri)}")
    print(f"  - In B only (not A): {len(labels_in_b_only)}")

    if labels_in_pp:
        print(f"\nPP matches: {sorted(labels_in_pp)}")
    if labels_in_ri:
        print(f"\nRI matches: {sorted(labels_in_ri)}")
    if labels_in_b_only:
        print(f"\nB-only matches: {sorted(labels_in_b_only)}")

    # Check 2: MIDDLE extraction and comparison
    print("\n" + "=" * 70)
    print("CHECK 2: MIDDLE COMPARISONS")
    print("=" * 70)

    # Extract MIDDLEs from pharma labels
    label_middles = {}
    for label in pharma_labels:
        mid = extract_middle(label)
        if mid and len(mid) >= 2:
            label_middles[label] = mid

    print(f"\nPharma labels with extractable MIDDLEs (≥2 chars): {len(label_middles)}")

    # Extract MIDDLEs from Currier A
    a_middles = {}
    for token in a_tokens:
        mid = extract_middle(token)
        if mid and len(mid) >= 2:
            a_middles[token] = mid

    pp_middles_set = set(a_middles[t] for t in pp_tokens if t in a_middles)
    ri_middles_set = set(a_middles[t] for t in ri_tokens if t in a_middles)

    print(f"Currier A MIDDLEs: {len(set(a_middles.values()))}")
    print(f"  PP MIDDLEs: {len(pp_middles_set)}")
    print(f"  RI MIDDLEs: {len(ri_middles_set)}")

    # Check exact MIDDLE matches
    label_middle_set = set(label_middles.values())

    middles_in_pp = label_middle_set & pp_middles_set
    middles_in_ri = label_middle_set & ri_middles_set

    print(f"\nLabel MIDDLEs that match PP MIDDLEs: {len(middles_in_pp)}")
    print(f"Label MIDDLEs that match RI MIDDLEs: {len(middles_in_ri)}")

    if middles_in_pp:
        # Show which labels have these middles
        print(f"\nPP MIDDLE matches:")
        for mid in sorted(middles_in_pp)[:20]:
            matching_labels = [l for l, m in label_middles.items() if m == mid]
            matching_pp = [t for t, m in a_middles.items() if m == mid and t in pp_tokens][:3]
            print(f"  '{mid}': labels={matching_labels[:3]}, PP tokens={matching_pp}")

    if middles_in_ri:
        print(f"\nRI MIDDLE matches:")
        for mid in sorted(middles_in_ri)[:20]:
            matching_labels = [l for l, m in label_middles.items() if m == mid]
            matching_ri = [t for t, m in a_middles.items() if m == mid and t in ri_tokens][:3]
            print(f"  '{mid}': labels={matching_labels[:3]}, RI tokens={matching_ri}")

    # Check 3: Label MIDDLEs as substrings in A MIDDLEs
    print("\n" + "=" * 70)
    print("CHECK 3: LABEL MIDDLES AS SUBSTRINGS IN CURRIER A")
    print("=" * 70)

    all_a_middles = set(a_middles.values())

    substring_matches = defaultdict(list)
    for label, label_mid in label_middles.items():
        if len(label_mid) >= 3:  # Only check meaningful substrings
            for a_mid in all_a_middles:
                if label_mid in a_mid and label_mid != a_mid:
                    substring_matches[label_mid].append(a_mid)

    print(f"\nLabel MIDDLEs (≥3 chars) found as substrings in A MIDDLEs: {len(substring_matches)}")

    if substring_matches:
        print("\nTop substring matches:")
        for label_mid, a_mids in sorted(substring_matches.items(), key=lambda x: -len(x[1]))[:15]:
            labels_with_mid = [l for l, m in label_middles.items() if m == label_mid]
            print(f"  '{label_mid}' (from {labels_with_mid[:2]}): found in {len(a_mids)} A MIDDLEs")
            print(f"    Examples: {a_mids[:5]}")

    # Check 4: Currier A MIDDLEs as substrings in label MIDDLEs
    print("\n" + "=" * 70)
    print("CHECK 4: CURRIER A MIDDLES AS SUBSTRINGS IN LABELS")
    print("=" * 70)

    a_in_label = defaultdict(list)
    for a_mid in all_a_middles:
        if len(a_mid) >= 3:
            for label, label_mid in label_middles.items():
                if a_mid in label_mid and a_mid != label_mid:
                    a_in_label[a_mid].append(label)

    print(f"\nA MIDDLEs (≥3 chars) found as substrings in label MIDDLEs: {len(a_in_label)}")

    # Which are PP vs RI?
    pp_in_labels = {m for m in a_in_label.keys() if m in pp_middles_set}
    ri_in_labels = {m for m in a_in_label.keys() if m in ri_middles_set}

    print(f"  PP MIDDLEs in labels: {len(pp_in_labels)}")
    print(f"  RI MIDDLEs in labels: {len(ri_in_labels)}")

    if pp_in_labels:
        print("\nPP MIDDLEs found in labels:")
        for mid in sorted(pp_in_labels, key=lambda x: -len(a_in_label[x]))[:10]:
            print(f"  '{mid}': in {len(a_in_label[mid])} labels - {a_in_label[mid][:5]}")

    if ri_in_labels:
        print("\nRI MIDDLEs found in labels:")
        for mid in sorted(ri_in_labels, key=lambda x: -len(a_in_label[x]))[:10]:
            print(f"  '{mid}': in {len(a_in_label[mid])} labels - {a_in_label[mid][:5]}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"""
Pharma labels checked: {len(pharma_labels)}

EXACT TOKEN MATCHES:
  In Currier A: {len(labels_in_a)} ({100*len(labels_in_a)/len(pharma_labels):.1f}%)
    - PP: {len(labels_in_pp)}
    - RI: {len(labels_in_ri)}

MIDDLE MATCHES:
  Label MIDDLEs = PP MIDDLEs: {len(middles_in_pp)}
  Label MIDDLEs = RI MIDDLEs: {len(middles_in_ri)}

SUBSTRING CONTAINMENT:
  Label MIDDLEs in A MIDDLEs: {len(substring_matches)}
  A MIDDLEs in Label MIDDLEs: {len(a_in_label)}
    - PP in labels: {len(pp_in_labels)}
    - RI in labels: {len(ri_in_labels)}
""")
