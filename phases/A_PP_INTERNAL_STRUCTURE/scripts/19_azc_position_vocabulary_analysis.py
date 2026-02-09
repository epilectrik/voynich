#!/usr/bin/env python3
"""
Analyze what AZC positions represent based on their vocabulary signatures.

For each major position type (C, P, R-series, S-series):
1. What MIDDLEs are characteristic?
2. What PREFIX patterns dominate?
3. What B-side roles do these MIDDLEs fill?
4. What morphological patterns exist?
5. What might the positions represent?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter
import json

def load_azc_tokens():
    """Load AZC tokens with full morphology."""
    sys.path.insert(0, str(Path('C:/git/voynich/archive/scripts')))
    from archive.scripts.currier_a_token_generator import decompose_token

    filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

    tokens = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue
                currier = parts[6].strip('"').strip()
                if currier == 'NA':  # AZC tokens
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip()
                    placement = parts[10].strip('"').strip()

                    if token and placement:
                        result = decompose_token(token)
                        prefix = result[0] if result[0] else 'NONE'
                        middle = result[1] if result[1] else ''
                        suffix = result[2] if len(result) > 2 and result[2] else ''

                        tokens.append({
                            'token': token,
                            'folio': folio,
                            'placement': placement,
                            'prefix': prefix,
                            'middle': middle,
                            'suffix': suffix
                        })
    return tokens

def load_class_map():
    """Load token -> class mapping."""
    class_map_path = Path('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json')
    with open(class_map_path) as f:
        class_data = json.load(f)

    token_to_class = {}
    if "token_to_class" in class_data:
        for token, class_id in class_data["token_to_class"].items():
            token_to_class[token.lower()] = int(class_id)
    return token_to_class

def get_role_for_class(class_id):
    """Map class ID to role."""
    # From BCSC
    cc_classes = {10, 11, 12, 17}
    en_classes = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}
    ax_classes = {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}
    fq_classes = {9, 13, 14, 23}
    fl_classes = {7, 30, 38, 40}

    if class_id in cc_classes:
        return 'CC'
    elif class_id in en_classes:
        return 'EN'
    elif class_id in ax_classes:
        return 'AX'
    elif class_id in fq_classes:
        return 'FQ'
    elif class_id in fl_classes:
        return 'FL'
    return 'UNK'

def analyze_position(tokens, position_filter, token_to_class):
    """Analyze vocabulary at a specific position or position group."""
    pos_tokens = [t for t in tokens if t['placement'].startswith(position_filter)
                  or t['placement'] == position_filter]

    if not pos_tokens:
        return None

    # PREFIX distribution
    prefix_counts = Counter(t['prefix'] for t in pos_tokens)

    # MIDDLE distribution
    middle_counts = Counter(t['middle'] for t in pos_tokens if t['middle'])

    # Suffix distribution
    suffix_counts = Counter(t['suffix'] for t in pos_tokens if t['suffix'])

    # B-side class distribution (for tokens that appear in B)
    class_counts = Counter()
    role_counts = Counter()
    for t in pos_tokens:
        if t['token'] in token_to_class:
            c = token_to_class[t['token']]
            class_counts[c] += 1
            role_counts[get_role_for_class(c)] += 1

    # Kernel character analysis
    kernel_chars = {'k', 'h', 'e'}
    kernel_count = sum(1 for t in pos_tokens
                       if any(c in t['middle'] for c in kernel_chars))
    kernel_rate = kernel_count / len(pos_tokens) if pos_tokens else 0

    # Specific character patterns in MIDDLEs
    char_counts = Counter()
    for t in pos_tokens:
        for c in t['middle']:
            char_counts[c] += 1

    return {
        'count': len(pos_tokens),
        'prefix_dist': prefix_counts,
        'middle_dist': middle_counts,
        'suffix_dist': suffix_counts,
        'class_dist': class_counts,
        'role_dist': role_counts,
        'kernel_rate': kernel_rate,
        'char_counts': char_counts,
        'unique_middles': len(set(t['middle'] for t in pos_tokens if t['middle'])),
        'tokens': pos_tokens
    }

def main():
    print("=" * 70)
    print("AZC POSITION VOCABULARY ANALYSIS")
    print("What do the positions represent?")
    print("=" * 70)
    print()

    tokens = load_azc_tokens()
    token_to_class = load_class_map()

    print(f"Total AZC tokens: {len(tokens)}")
    print()

    # Analyze major position groups
    positions = ['C', 'P', 'R1', 'R2', 'R3', 'S', 'S0', 'S1', 'S2']

    for pos in positions:
        analysis = analyze_position(tokens, pos, token_to_class)
        if not analysis or analysis['count'] < 20:
            continue

        print("=" * 70)
        print(f"POSITION: {pos} ({analysis['count']} tokens)")
        print("=" * 70)
        print()

        # PREFIX signature
        print("PREFIX SIGNATURE:")
        total = sum(analysis['prefix_dist'].values())
        for prefix, count in analysis['prefix_dist'].most_common(6):
            pct = count / total * 100
            print(f"  {prefix:8} {pct:5.1f}%  {'#' * int(pct/2)}")
        print()

        # Top MIDDLEs
        print("TOP MIDDLEs:")
        for middle, count in analysis['middle_dist'].most_common(8):
            pct = count / analysis['count'] * 100
            print(f"  {middle:12} {count:4} ({pct:4.1f}%)")
        print()

        # B-side role distribution
        if analysis['role_dist']:
            print("B-SIDE ROLE DISTRIBUTION:")
            role_total = sum(analysis['role_dist'].values())
            for role in ['EN', 'AX', 'FQ', 'FL', 'CC']:
                count = analysis['role_dist'].get(role, 0)
                pct = count / role_total * 100 if role_total else 0
                print(f"  {role:4} {pct:5.1f}%  {'#' * int(pct/2)}")
            print()

        # Kernel rate
        print(f"KERNEL RATE (k/h/e in MIDDLE): {analysis['kernel_rate']*100:.1f}%")
        print()

        # Character frequency in MIDDLEs
        print("TOP MIDDLE CHARACTERS:")
        char_total = sum(analysis['char_counts'].values())
        for char, count in analysis['char_counts'].most_common(8):
            pct = count / char_total * 100
            print(f"  '{char}' {pct:5.1f}%")
        print()

        # Suffix pattern
        if analysis['suffix_dist']:
            print("SUFFIX PATTERN:")
            suffix_total = sum(analysis['suffix_dist'].values())
            for suffix, count in analysis['suffix_dist'].most_common(5):
                pct = count / suffix_total * 100
                print(f"  -{suffix:6} {pct:5.1f}%")
        else:
            print("SUFFIX PATTERN: (mostly bare)")
        print()

    # ===========================================
    # CROSS-POSITION COMPARISON
    # ===========================================
    print()
    print("=" * 70)
    print("CROSS-POSITION COMPARISON")
    print("=" * 70)
    print()

    # Compare key metrics across positions
    print(f"{'Position':<8} {'N':>6} {'Kernel%':>8} {'EN%':>8} {'AX%':>8} {'qo%':>8} {'ok/ot%':>8}")
    print("-" * 58)

    for pos in positions:
        analysis = analyze_position(tokens, pos, token_to_class)
        if not analysis or analysis['count'] < 20:
            continue

        n = analysis['count']
        kernel = analysis['kernel_rate'] * 100

        role_total = sum(analysis['role_dist'].values())
        en_pct = analysis['role_dist'].get('EN', 0) / role_total * 100 if role_total else 0
        ax_pct = analysis['role_dist'].get('AX', 0) / role_total * 100 if role_total else 0

        prefix_total = sum(analysis['prefix_dist'].values())
        qo_pct = analysis['prefix_dist'].get('qo', 0) / prefix_total * 100
        okot_pct = (analysis['prefix_dist'].get('ok', 0) + analysis['prefix_dist'].get('ot', 0)) / prefix_total * 100

        print(f"{pos:<8} {n:>6} {kernel:>7.1f}% {en_pct:>7.1f}% {ax_pct:>7.1f}% {qo_pct:>7.1f}% {okot_pct:>7.1f}%")

    # ===========================================
    # INTERPRETATION
    # ===========================================
    print()
    print("=" * 70)
    print("INTERPRETATION: What might the positions represent?")
    print("=" * 70)
    print()

    # Analyze R-series progression
    print("R-SERIES PROGRESSION (R1 -> R2 -> R3):")
    r_analyses = {pos: analyze_position(tokens, pos, token_to_class) for pos in ['R1', 'R2', 'R3']}

    metrics = []
    for pos in ['R1', 'R2', 'R3']:
        a = r_analyses[pos]
        if a and a['count'] >= 20:
            prefix_total = sum(a['prefix_dist'].values())
            qo = a['prefix_dist'].get('qo', 0) / prefix_total * 100
            okot = (a['prefix_dist'].get('ok', 0) + a['prefix_dist'].get('ot', 0)) / prefix_total * 100
            metrics.append((pos, a['kernel_rate']*100, qo, okot))

    if metrics:
        print(f"  {'Pos':<4} {'Kernel%':>10} {'qo%':>10} {'ok/ot%':>10}")
        for pos, kernel, qo, okot in metrics:
            print(f"  {pos:<4} {kernel:>10.1f} {qo:>10.1f} {okot:>10.1f}")
        print()

    # S vs R comparison
    print("S-SERIES vs R-SERIES:")
    s_all = analyze_position(tokens, 'S', token_to_class)
    r_all = [analyze_position(tokens, f'R{i}', token_to_class) for i in range(1, 4)]

    # Combine R-series
    r_combined_prefixes = Counter()
    r_combined_count = 0
    for r in r_all:
        if r:
            r_combined_prefixes.update(r['prefix_dist'])
            r_combined_count += r['count']

    if s_all and r_combined_count > 0:
        s_prefix_total = sum(s_all['prefix_dist'].values())
        r_prefix_total = sum(r_combined_prefixes.values())

        print(f"  S-series ok/ot: {(s_all['prefix_dist'].get('ok',0) + s_all['prefix_dist'].get('ot',0))/s_prefix_total*100:.1f}%")
        print(f"  R-series ok/ot: {(r_combined_prefixes.get('ok',0) + r_combined_prefixes.get('ot',0))/r_prefix_total*100:.1f}%")
        print(f"  S-series ch/sh: {(s_all['prefix_dist'].get('ch',0) + s_all['prefix_dist'].get('sh',0))/s_prefix_total*100:.1f}%")
        print(f"  R-series ch/sh: {(r_combined_prefixes.get('ch',0) + r_combined_prefixes.get('sh',0))/r_prefix_total*100:.1f}%")

    print()
    print("HYPOTHESES:")
    print()
    print("1. S-SERIES = BOUNDARY/STABILIZATION VOCABULARY")
    print("   - High ok/ot (stabilization prefixes)")
    print("   - Low qo (energy input)")
    print("   - Boundary position in lines (C311)")
    print()
    print("2. R-SERIES = INTERIOR/PROCESSING VOCABULARY")
    print("   - Ordered progression R1->R2->R3")
    print("   - Higher ch/sh (active processing)")
    print("   - Interior position in lines")
    print()
    print("3. C/P = CORE VOCABULARY")
    print("   - High kernel contact")
    print("   - High hazard class involvement")
    print("   - Central diagram positions")

if __name__ == "__main__":
    main()
