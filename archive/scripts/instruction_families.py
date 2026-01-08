"""
Probe: How many instruction families exist in Currier B?

Looking at natural clusters based on:
- Prefix type (kernel-heavy vs kernel-light)
- Suffix type (kernel-heavy vs kernel-light)
- Position (initial/final/mid)
- LINK affinity
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# Functional classifications from BPF/BSF
KERNEL_HEAVY_PREFIX = {'ch', 'sh', 'ok', 'lk', 'lch', 'yk', 'ke', 'ot'}
KERNEL_LIGHT_PREFIX = {'da', 'sa', 'al'}
KERNEL_MIXED_PREFIX = {'qo', 'ol', 'op'}

KERNEL_HEAVY_SUFFIX = {'edy', 'ey', 'dy', 'd', 'eey', 'ody', 'chy', 'shy'}
KERNEL_LIGHT_SUFFIX = {'in', 'l', 'r', 'am', 'om'}
KERNEL_MIXED_SUFFIX = {'aiin', 'ain', 'y', 'ar', 'or', 'al', 'ol', 'an', 's'}

LINE_INITIAL_PREFIX = {'so', 'ych', 'pch', 'sa', 'yk', 'yt'}
LINE_FINAL_SUFFIX = {'am', 'om', 'oly', 'y', 'dy', 'an'}

LINK_ATTRACTED_PREFIX = {'al', 'ol', 'da'}
LINK_ATTRACTED_SUFFIX = {'l', 'in', 'r'}

ALL_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ol', 'al', 'sa', 'so',
                'lk', 'lch', 'lsh', 'yk', 'yt', 'op', 'ke', 'ka', 'pch', 'ych']
ALL_SUFFIXES = ['edy', 'aiin', 'y', 'ar', 'ain', 'ey', 'ol', 'eey', 'al',
                'r', 'dy', 'l', 'or', 'in', 'ody', 'am', 's', 'd', 'chy', 'shy', 'om', 'an']

def get_prefix(token):
    for p in sorted(ALL_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return p
    return None

def get_suffix(token):
    for s in sorted(ALL_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            return s
    return None

def classify_prefix(prefix):
    if prefix in KERNEL_HEAVY_PREFIX:
        return 'K_HEAVY'
    elif prefix in KERNEL_LIGHT_PREFIX:
        return 'K_LIGHT'
    elif prefix in LINE_INITIAL_PREFIX:
        return 'LINE_INIT'
    else:
        return 'MIXED'

def classify_suffix(suffix):
    if suffix in KERNEL_HEAVY_SUFFIX:
        return 'K_HEAVY'
    elif suffix in KERNEL_LIGHT_SUFFIX:
        return 'K_LIGHT'
    elif suffix in LINE_FINAL_SUFFIX:
        return 'LINE_FINAL'
    else:
        return 'MIXED'

def load_b_data():
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('language') == 'B' and row.get('transcriber') == 'H':
                token = row.get('word', '')
                if token and '*' not in token:
                    data.append({
                        'token': token,
                        'line_initial': row.get('line_initial', '0') == '1',
                        'line_final': row.get('line_final', '0') == '1'
                    })
    return data

def main():
    print("="*70)
    print("INSTRUCTION FAMILY ANALYSIS")
    print("="*70)

    data = load_b_data()
    print(f"\nLoaded {len(data)} Currier B tokens")

    # Count prefix × suffix combinations
    combo_counts = Counter()
    family_counts = Counter()

    for row in data:
        token = row['token']
        prefix = get_prefix(token)
        suffix = get_suffix(token)

        if prefix and suffix:
            combo_counts[(prefix, suffix)] += 1

            # Classify into families
            p_class = classify_prefix(prefix)
            s_class = classify_suffix(suffix)
            family = f"{p_class}+{s_class}"
            family_counts[family] += 1

    # Show family distribution
    print("\n" + "="*70)
    print("INSTRUCTION FAMILIES (by prefix × suffix functional class)")
    print("="*70)

    total = sum(family_counts.values())
    print(f"\n{'Family':<25} {'Count':>10} {'%':>8}")
    print("-"*45)

    for family, count in sorted(family_counts.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"{family:<25} {count:>10} {pct:>7.1f}%")

    print(f"\nTotal classified: {total}")
    print(f"Unique families: {len(family_counts)}")

    # Reduce to major families
    print("\n" + "="*70)
    print("MAJOR INSTRUCTION FAMILIES (simplified)")
    print("="*70)

    # Group into interpretable categories
    major_families = {
        'INTERVENTION': 0,      # K_HEAVY + K_HEAVY
        'MONITORING': 0,        # K_LIGHT + K_LIGHT
        'TRANSITION_IN': 0,     # LINE_INIT + any
        'TRANSITION_OUT': 0,    # any + LINE_FINAL
        'HYBRID': 0             # mixed combinations
    }

    for family, count in family_counts.items():
        p_class, s_class = family.split('+')

        if p_class == 'K_HEAVY' and s_class == 'K_HEAVY':
            major_families['INTERVENTION'] += count
        elif p_class == 'K_LIGHT' and s_class == 'K_LIGHT':
            major_families['MONITORING'] += count
        elif p_class == 'LINE_INIT':
            major_families['TRANSITION_IN'] += count
        elif s_class == 'LINE_FINAL' or s_class == 'K_LIGHT':
            major_families['TRANSITION_OUT'] += count
        else:
            major_families['HYBRID'] += count

    print(f"\n{'Major Family':<20} {'Count':>10} {'%':>8} {'Interpretation':<30}")
    print("-"*75)

    interpretations = {
        'INTERVENTION': 'Active control actions (kernel-heavy)',
        'MONITORING': 'Passive observation (kernel-light, LINK-adjacent)',
        'TRANSITION_IN': 'Stage entry markers (line-initial)',
        'TRANSITION_OUT': 'Stage exit/completion markers',
        'HYBRID': 'Mixed/transitional instructions'
    }

    for family in ['INTERVENTION', 'MONITORING', 'TRANSITION_IN', 'TRANSITION_OUT', 'HYBRID']:
        count = major_families[family]
        pct = count / total * 100 if total > 0 else 0
        print(f"{family:<20} {count:>10} {pct:>7.1f}% {interpretations[family]:<30}")

    # Top specific combinations
    print("\n" + "="*70)
    print("TOP 20 PREFIX+SUFFIX COMBINATIONS")
    print("="*70)

    print(f"\n{'Prefix':<8} {'Suffix':<8} {'Count':>8} {'%':>8} {'Family':<20}")
    print("-"*55)

    for (prefix, suffix), count in combo_counts.most_common(20):
        pct = count / total * 100
        p_class = classify_prefix(prefix)
        s_class = classify_suffix(suffix)
        print(f"{prefix:<8} -{suffix:<7} {count:>8} {pct:>7.1f}% {p_class}+{s_class}")

    # How many combinations account for 80% of tokens?
    print("\n" + "="*70)
    print("CONCENTRATION ANALYSIS")
    print("="*70)

    sorted_combos = sorted(combo_counts.values(), reverse=True)
    cumsum = np.cumsum(sorted_combos)

    for threshold in [0.5, 0.8, 0.9, 0.95]:
        n_needed = np.searchsorted(cumsum, total * threshold) + 1
        print(f"{threshold*100:.0f}% of tokens covered by {n_needed} combinations")

    print(f"\nTotal unique prefix+suffix combinations: {len(combo_counts)}")

if __name__ == '__main__':
    main()
