"""
03_a_pp_composition.py - A Paragraph PP Composition

Metrics per A paragraph:
- pp_count, pp_rate
- pp_unique_middle_count
- pp_compound_rate (via MiddleAnalyzer)
- pp_core_rate (in 20+ folios)
- pp_folio_unique_rate (exactly 1 folio)
- daiin_count

Depends on: 00_build_paragraph_inventory.py
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

# RI prefixes for filtering
RI_PREFIXES = ['ct', 'ch', 'qo', 'po', 'do', 'sh', 'da', 'sa']

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load inventory
    with open(results_dir / 'a_paragraph_inventory.json') as f:
        inventory = json.load(f)

    with open(results_dir / 'a_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    morph = Morphology()

    # Build MIDDLE inventory for compound detection
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('A')

    # Get folio distribution for core/unique classification
    tx = Transcript()
    middle_folios = defaultdict(set)
    for token in tx.currier_a():
        if token.word and '*' not in token.word:
            m = morph.extract(token.word)
            if m.middle:
                middle_folios[m.middle].add(token.folio)

    # Classify MIDDLEs
    core_middles = {m for m, folios in middle_folios.items() if len(folios) >= 20}
    folio_unique = {m for m, folios in middle_folios.items() if len(folios) == 1}

    profiles = []

    for par in inventory['paragraphs']:
        par_id = par['par_id']
        tokens = tokens_by_par[par_id]

        # Extract PP tokens (non-RI)
        pp_middles = []
        daiin_count = 0

        for t in tokens:
            word = t['word']
            if word and '*' not in word:
                m = morph.extract(word)
                prefix = m.prefix or ''

                # Check if RI (skip)
                is_ri = any(prefix.startswith(p) for p in RI_PREFIXES)
                if is_ri:
                    continue

                if m.middle:
                    pp_middles.append(m.middle)
                    if m.middle == 'aiin' or word == 'daiin':
                        daiin_count += 1

        pp_count = len(pp_middles)
        total_tokens = len([t for t in tokens if t['word'] and '*' not in t['word']])
        pp_rate = pp_count / total_tokens if total_tokens > 0 else 0

        unique_middles = set(pp_middles)
        pp_unique_middle_count = len(unique_middles)

        # Compound rate
        compound_count = sum(1 for m in pp_middles if mid_analyzer.is_compound(m))
        pp_compound_rate = compound_count / pp_count if pp_count > 0 else 0

        # Core rate (in 20+ folios)
        core_count = sum(1 for m in pp_middles if m in core_middles)
        pp_core_rate = core_count / pp_count if pp_count > 0 else 0

        # Folio-unique rate
        unique_count = sum(1 for m in pp_middles if m in folio_unique)
        pp_folio_unique_rate = unique_count / pp_count if pp_count > 0 else 0

        profiles.append({
            'par_id': par_id,
            'folio': par['folio'],
            'section': par['section'],
            'folio_position': par['folio_position'],
            'pp_profile': {
                'pp_count': pp_count,
                'pp_rate': round(pp_rate, 3),
                'pp_unique_middle_count': pp_unique_middle_count,
                'pp_compound_rate': round(pp_compound_rate, 3),
                'pp_core_rate': round(pp_core_rate, 3),
                'pp_folio_unique_rate': round(pp_folio_unique_rate, 3),
                'daiin_count': daiin_count
            }
        })

    # Summary statistics
    pp_rates = [p['pp_profile']['pp_rate'] for p in profiles]
    compound_rates = [p['pp_profile']['pp_compound_rate'] for p in profiles]
    core_rates = [p['pp_profile']['pp_core_rate'] for p in profiles]
    unique_rates = [p['pp_profile']['pp_folio_unique_rate'] for p in profiles]
    daiin_counts = [p['pp_profile']['daiin_count'] for p in profiles]

    summary = {
        'system': 'A',
        'paragraph_count': len(profiles),
        'pp_rate': {
            'mean': round(statistics.mean(pp_rates), 3),
            'median': round(statistics.median(pp_rates), 3)
        },
        'pp_compound_rate': {
            'mean': round(statistics.mean(compound_rates), 3),
            'median': round(statistics.median(compound_rates), 3)
        },
        'pp_core_rate': {
            'mean': round(statistics.mean(core_rates), 3),
            'median': round(statistics.median(core_rates), 3)
        },
        'pp_folio_unique_rate': {
            'mean': round(statistics.mean(unique_rates), 3),
            'median': round(statistics.median(unique_rates), 3)
        },
        'daiin': {
            'total': sum(daiin_counts),
            'paragraphs_with_daiin': sum(1 for d in daiin_counts if d > 0),
            'rate': round(sum(1 for d in daiin_counts if d > 0) / len(profiles), 3)
        },
        'middle_inventory': {
            'core_count': len(core_middles),
            'folio_unique_count': len(folio_unique),
            'total_distinct': len(middle_folios)
        }
    }

    # Print summary
    print("=== A PARAGRAPH PP COMPOSITION ===\n")
    print(f"Paragraphs: {summary['paragraph_count']}")
    print(f"\nPP rate: mean={summary['pp_rate']['mean']}, median={summary['pp_rate']['median']}")
    print(f"Compound rate: mean={summary['pp_compound_rate']['mean']}")
    print(f"Core rate: mean={summary['pp_core_rate']['mean']}")
    print(f"Folio-unique rate: mean={summary['pp_folio_unique_rate']['mean']}")
    print(f"\ndaiin: {summary['daiin']['total']} total in {summary['daiin']['paragraphs_with_daiin']} paragraphs ({summary['daiin']['rate']})")

    print(f"\nMIDDLE inventory:")
    print(f"  Core (20+ folios): {summary['middle_inventory']['core_count']}")
    print(f"  Folio-unique: {summary['middle_inventory']['folio_unique_count']}")
    print(f"  Total distinct: {summary['middle_inventory']['total_distinct']}")

    # Save
    with open(results_dir / 'a_pp_composition.json', 'w') as f:
        json.dump({
            'summary': summary,
            'profiles': profiles
        }, f, indent=2)

    print(f"\nSaved to {results_dir}/a_pp_composition.json")

if __name__ == '__main__':
    main()
