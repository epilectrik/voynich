"""
06_b_ht_variance.py - B Paragraph HT Variance

Metrics per B paragraph:
- ht_count, ht_rate
- line1_ht_rate, body_ht_rate
- ht_delta (line1 - body)
- first_token_is_ht

HT = tokens not in class_token_map.json

Expected: 76% show positive delta (C840)

Depends on: 00_build_paragraph_inventory.py
"""

import json
import sys
from pathlib import Path
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load class_token_map for HT identification
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'

    if class_map_path.exists():
        with open(class_map_path) as f:
            class_map = json.load(f)
        # Map is nested under 'token_to_class'
        token_to_class = class_map.get('token_to_class', class_map)
        classified_tokens = set(token_to_class.keys())
    else:
        print("WARNING: class_token_map.json not found, using empty set")
        classified_tokens = set()

    # Load inventory
    with open(results_dir / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    with open(results_dir / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    profiles = []

    for par in inventory['paragraphs']:
        par_id = par['par_id']
        tokens = tokens_by_par[par_id]
        lines = par['lines']

        # Filter valid tokens
        valid_tokens = [t for t in tokens if t['word'] and '*' not in t['word']]

        # Count HT (not in class map = HT)
        ht_tokens = [t for t in valid_tokens if t['word'] not in classified_tokens]
        ht_count = len(ht_tokens)
        ht_rate = ht_count / len(valid_tokens) if valid_tokens else 0

        # Line 1 vs body
        if len(lines) >= 2:
            line1 = lines[0]
            line1_tokens = [t for t in valid_tokens if t['line'] == line1]
            body_tokens = [t for t in valid_tokens if t['line'] != line1]

            line1_ht = [t for t in line1_tokens if t['word'] not in classified_tokens]
            body_ht = [t for t in body_tokens if t['word'] not in classified_tokens]

            line1_ht_rate = len(line1_ht) / len(line1_tokens) if line1_tokens else 0
            body_ht_rate = len(body_ht) / len(body_tokens) if body_tokens else 0
            ht_delta = line1_ht_rate - body_ht_rate
        else:
            line1_ht_rate = ht_rate
            body_ht_rate = 0
            ht_delta = 0

        # First token HT?
        first_token_is_ht = valid_tokens[0]['word'] not in classified_tokens if valid_tokens else False

        profiles.append({
            'par_id': par_id,
            'folio': par['folio'],
            'section': par['section'],
            'folio_position': par['folio_position'],
            'ht_profile': {
                'ht_count': ht_count,
                'ht_rate': round(ht_rate, 3),
                'line1_ht_rate': round(line1_ht_rate, 3),
                'body_ht_rate': round(body_ht_rate, 3),
                'ht_delta': round(ht_delta, 3),
                'first_token_is_ht': first_token_is_ht
            }
        })

    # Summary statistics
    ht_rates = [p['ht_profile']['ht_rate'] for p in profiles]
    ht_deltas = [p['ht_profile']['ht_delta'] for p in profiles]
    line1_rates = [p['ht_profile']['line1_ht_rate'] for p in profiles]
    body_rates = [p['ht_profile']['body_ht_rate'] for p in profiles]

    # Count positive delta paragraphs (multi-line only)
    multi_line = [p for p in profiles if len(inventory['paragraphs'][profiles.index(p)]['lines']) >= 2]
    positive_delta = sum(1 for p in multi_line if p['ht_profile']['ht_delta'] > 0)
    positive_delta_rate = positive_delta / len(multi_line) if multi_line else 0

    summary = {
        'system': 'B',
        'paragraph_count': len(profiles),
        'classified_tokens_available': len(classified_tokens),
        'ht_rate': {
            'mean': round(statistics.mean(ht_rates), 3),
            'median': round(statistics.median(ht_rates), 3),
            'stdev': round(statistics.stdev(ht_rates), 3)
        },
        'line1_ht_rate': {
            'mean': round(statistics.mean(line1_rates), 3),
            'median': round(statistics.median(line1_rates), 3)
        },
        'body_ht_rate': {
            'mean': round(statistics.mean(body_rates), 3),
            'median': round(statistics.median(body_rates), 3)
        },
        'ht_delta': {
            'mean': round(statistics.mean(ht_deltas), 3),
            'median': round(statistics.median(ht_deltas), 3),
            'expected': 0.158  # From C840: +15.8pp
        },
        'positive_delta_rate': round(positive_delta_rate, 3),
        'positive_delta_count': positive_delta,
        'multi_line_count': len(multi_line),
        'first_token_ht_rate': round(sum(1 for p in profiles if p['ht_profile']['first_token_is_ht']) / len(profiles), 3)
    }

    # Print summary
    print("=== B PARAGRAPH HT VARIANCE ===\n")
    print(f"Paragraphs: {summary['paragraph_count']}")
    print(f"Classified tokens available: {summary['classified_tokens_available']}")

    print(f"\nHT rate: mean={summary['ht_rate']['mean']}, median={summary['ht_rate']['median']}")
    print(f"Line 1 HT rate: mean={summary['line1_ht_rate']['mean']}")
    print(f"Body HT rate: mean={summary['body_ht_rate']['mean']}")
    print(f"\nHT delta (line1 - body): mean={summary['ht_delta']['mean']}, expected={summary['ht_delta']['expected']}")
    print(f"Positive delta: {summary['positive_delta_count']}/{summary['multi_line_count']} ({summary['positive_delta_rate']}) - expected ~76%")
    print(f"\nFirst token is HT: {summary['first_token_ht_rate']}")

    # Save
    with open(results_dir / 'b_ht_variance.json', 'w') as f:
        json.dump({
            'summary': summary,
            'profiles': profiles
        }, f, indent=2)

    print(f"\nSaved to {results_dir}/b_ht_variance.json")

if __name__ == '__main__':
    main()
