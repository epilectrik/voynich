"""
08_b_role_composition.py - B Paragraph Role Composition

Metrics per B paragraph:
- cc_count, cc_rate (Control-Change)
- en_count, en_rate (Energy/thermal)
- fl_count, fl_rate (Flow/material)
- fq_count, fq_rate (Frequency/repetition)
- ax_count, ax_rate (Auxiliary)
- dominant_role
- role_evenness (entropy-based)

Role mapping from BCSC:
- CC: classes {10, 11, 12, 17}
- EN: classes {8, 31-37, 39, 41-49}
- FL: classes {7, 30, 38, 40}
- FQ: classes {9, 13, 14, 23}
- AX: remaining classified

Depends on: 00_build_paragraph_inventory.py
"""

import json
import sys
from pathlib import Path
from collections import Counter
import statistics
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Role class mappings from BCSC
CC_CLASSES = {10, 11, 12, 17}
EN_CLASSES = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}
FL_CLASSES = {7, 30, 38, 40}
FQ_CLASSES = {9, 13, 14, 23}
# AX = anything classified but not in above

def get_role(class_num):
    """Map class number to role."""
    if class_num in CC_CLASSES:
        return 'CC'
    elif class_num in EN_CLASSES:
        return 'EN'
    elif class_num in FL_CLASSES:
        return 'FL'
    elif class_num in FQ_CLASSES:
        return 'FQ'
    else:
        return 'AX'

def entropy(counts):
    """Calculate normalized Shannon entropy."""
    total = sum(counts.values())
    if total == 0:
        return 0
    probs = [c / total for c in counts.values() if c > 0]
    h = -sum(p * math.log2(p) for p in probs)
    # Normalize by max entropy (log2 of number of categories)
    max_h = math.log2(len(counts)) if len(counts) > 1 else 1
    return h / max_h if max_h > 0 else 0

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load class_token_map
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'

    if class_map_path.exists():
        with open(class_map_path) as f:
            raw_map = json.load(f)
        # Map is nested under 'token_to_class'
        class_map = raw_map.get('token_to_class', raw_map)
    else:
        print("WARNING: class_token_map.json not found")
        class_map = {}

    # Load inventory
    with open(results_dir / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    with open(results_dir / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    profiles = []

    for par in inventory['paragraphs']:
        par_id = par['par_id']
        tokens = tokens_by_par[par_id]

        # Count roles
        role_counts = Counter({'CC': 0, 'EN': 0, 'FL': 0, 'FQ': 0, 'AX': 0})
        classified_count = 0

        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue

            if word in class_map:
                class_num = class_map[word]
                role = get_role(class_num)
                role_counts[role] += 1
                classified_count += 1

        # Calculate rates
        total = classified_count if classified_count > 0 else 1

        # Dominant role
        dominant = role_counts.most_common(1)[0][0] if classified_count > 0 else None

        # Evenness
        role_evenness = round(entropy(role_counts), 3) if classified_count > 0 else 0

        profiles.append({
            'par_id': par_id,
            'folio': par['folio'],
            'section': par['section'],
            'folio_position': par['folio_position'],
            'role_profile': {
                'cc_count': role_counts['CC'],
                'cc_rate': round(role_counts['CC'] / total, 3),
                'en_count': role_counts['EN'],
                'en_rate': round(role_counts['EN'] / total, 3),
                'fl_count': role_counts['FL'],
                'fl_rate': round(role_counts['FL'] / total, 3),
                'fq_count': role_counts['FQ'],
                'fq_rate': round(role_counts['FQ'] / total, 3),
                'ax_count': role_counts['AX'],
                'ax_rate': round(role_counts['AX'] / total, 3),
                'classified_count': classified_count,
                'dominant_role': dominant,
                'role_evenness': role_evenness
            }
        })

    # Summary statistics
    en_rates = [p['role_profile']['en_rate'] for p in profiles]
    fl_rates = [p['role_profile']['fl_rate'] for p in profiles]
    fq_rates = [p['role_profile']['fq_rate'] for p in profiles]
    cc_rates = [p['role_profile']['cc_rate'] for p in profiles]
    evenness = [p['role_profile']['role_evenness'] for p in profiles]

    dominant_dist = Counter(p['role_profile']['dominant_role'] for p in profiles)

    summary = {
        'system': 'B',
        'paragraph_count': len(profiles),
        'role_rates': {
            'EN': {'mean': round(statistics.mean(en_rates), 3), 'stdev': round(statistics.stdev(en_rates), 3)},
            'FL': {'mean': round(statistics.mean(fl_rates), 3), 'stdev': round(statistics.stdev(fl_rates), 3)},
            'FQ': {'mean': round(statistics.mean(fq_rates), 3), 'stdev': round(statistics.stdev(fq_rates), 3)},
            'CC': {'mean': round(statistics.mean(cc_rates), 3), 'stdev': round(statistics.stdev(cc_rates), 3)}
        },
        'dominant_role_distribution': dict(dominant_dist.most_common()),
        'role_evenness': {
            'mean': round(statistics.mean(evenness), 3),
            'stdev': round(statistics.stdev(evenness), 3)
        }
    }

    # Print summary
    print("=== B PARAGRAPH ROLE COMPOSITION ===\n")
    print(f"Paragraphs: {summary['paragraph_count']}")

    print("\nRole rates (mean ± stdev):")
    for role in ['EN', 'FL', 'FQ', 'CC']:
        stats = summary['role_rates'][role]
        print(f"  {role}: {stats['mean']:.3f} ± {stats['stdev']:.3f}")

    print("\nDominant role distribution:")
    for role, count in dominant_dist.most_common():
        print(f"  {role}: {count} ({count/len(profiles):.1%})")

    print(f"\nRole evenness: {summary['role_evenness']['mean']:.3f} ± {summary['role_evenness']['stdev']:.3f}")

    # Save
    with open(results_dir / 'b_role_composition.json', 'w') as f:
        json.dump({
            'summary': summary,
            'profiles': profiles
        }, f, indent=2)

    print(f"\nSaved to {results_dir}/b_role_composition.json")

if __name__ == '__main__':
    main()
