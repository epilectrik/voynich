"""
05_b_size_density_profile.py - B Paragraph Size/Density Metrics

Metrics per B paragraph:
- line_count, token_count
- tokens_per_line

Expected: Mean ~4.4 lines (from B_PARAGRAPH_STRUCTURE)

Depends on: 00_build_paragraph_inventory.py
"""

import json
import sys
from pathlib import Path
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load inventory
    with open(results_dir / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    profiles = []
    for par in inventory['paragraphs']:
        line_count = par['line_count']
        token_count = par['token_count']

        profiles.append({
            'par_id': par['par_id'],
            'folio': par['folio'],
            'section': par['section'],
            'folio_position': par['folio_position'],
            'size': {
                'line_count': line_count,
                'token_count': token_count,
                'tokens_per_line': round(token_count / line_count, 2) if line_count > 0 else 0
            }
        })

    # Summary statistics
    line_counts = [p['size']['line_count'] for p in profiles]
    token_counts = [p['size']['token_count'] for p in profiles]
    tokens_per_line = [p['size']['tokens_per_line'] for p in profiles]

    summary = {
        'system': 'B',
        'paragraph_count': len(profiles),
        'line_count': {
            'mean': round(statistics.mean(line_counts), 2),
            'median': statistics.median(line_counts),
            'stdev': round(statistics.stdev(line_counts), 2),
            'min': min(line_counts),
            'max': max(line_counts)
        },
        'token_count': {
            'mean': round(statistics.mean(token_counts), 2),
            'median': statistics.median(token_counts),
            'stdev': round(statistics.stdev(token_counts), 2),
            'min': min(token_counts),
            'max': max(token_counts)
        },
        'tokens_per_line': {
            'mean': round(statistics.mean(tokens_per_line), 2),
            'median': round(statistics.median(tokens_per_line), 2)
        }
    }

    # By folio_position
    by_position = {}
    for pos in ['first', 'middle', 'last', 'only']:
        pos_pars = [p for p in profiles if p['folio_position'] == pos]
        if pos_pars:
            by_position[pos] = {
                'count': len(pos_pars),
                'mean_lines': round(statistics.mean([p['size']['line_count'] for p in pos_pars]), 2),
                'mean_tokens': round(statistics.mean([p['size']['token_count'] for p in pos_pars]), 2)
            }

    summary['by_folio_position'] = by_position

    # Print summary
    print("=== B PARAGRAPH SIZE/DENSITY PROFILE ===\n")
    print(f"Paragraphs: {summary['paragraph_count']}")
    print(f"\nLine count: mean={summary['line_count']['mean']}, median={summary['line_count']['median']}, range=[{summary['line_count']['min']}, {summary['line_count']['max']}]")
    print(f"Token count: mean={summary['token_count']['mean']}, median={summary['token_count']['median']}")
    print(f"Tokens/line: mean={summary['tokens_per_line']['mean']}")

    print("\nBy folio position:")
    for pos, stats in by_position.items():
        print(f"  {pos}: n={stats['count']}, mean_lines={stats['mean_lines']}, mean_tokens={stats['mean_tokens']}")

    # Save
    with open(results_dir / 'b_size_density.json', 'w') as f:
        json.dump({
            'summary': summary,
            'profiles': profiles
        }, f, indent=2)

    print(f"\nSaved to {results_dir}/b_size_density.json")

if __name__ == '__main__':
    main()
