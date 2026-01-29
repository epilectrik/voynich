"""
09_b_section_effects.py - B Section Effects

Section definitions (from C552):
- BIO: f74-f84 (biological/anatomical)
- HERBAL_B: f26-f56 (botanical, B-language)
- PHARMA: f57-f67 (pharmaceutical)
- RECIPE_B: f103+ (recipe section)

Tests:
- Chi-squared: Role distribution by section
- ANOVA: HT delta by section
- Validate C552: BIO +EN, HERBAL -EN, PHARMA +FL

Depends on: 05-08 scripts
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import statistics
import re

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# Section definitions
def get_b_section(folio):
    """Classify B folio into section."""
    # Extract folio number
    match = re.match(r'f(\d+)', folio)
    if not match:
        return 'other'

    num = int(match.group(1))

    if 74 <= num <= 84:
        return 'BIO'
    elif 26 <= num <= 56:
        return 'HERBAL_B'
    elif 57 <= num <= 67:
        return 'PHARMA'
    elif num >= 103:
        return 'RECIPE_B'
    else:
        return 'other'

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load previous results
    with open(results_dir / 'b_size_density.json') as f:
        size_data = json.load(f)

    with open(results_dir / 'b_ht_variance.json') as f:
        ht_data = json.load(f)

    with open(results_dir / 'b_gallows_markers.json') as f:
        gallows_data = json.load(f)

    with open(results_dir / 'b_role_composition.json') as f:
        role_data = json.load(f)

    # Merge profiles
    profiles = {}
    for p in size_data['profiles']:
        par_id = p['par_id']
        profiles[par_id] = {
            'par_id': par_id,
            'folio': p['folio'],
            'b_section': get_b_section(p['folio']),
            'folio_position': p['folio_position'],
            'size': p['size']
        }

    for p in ht_data['profiles']:
        if p['par_id'] in profiles:
            profiles[p['par_id']]['ht_profile'] = p['ht_profile']

    for p in gallows_data['profiles']:
        if p['par_id'] in profiles:
            profiles[p['par_id']]['initiation'] = p['initiation']

    for p in role_data['profiles']:
        if p['par_id'] in profiles:
            profiles[p['par_id']]['role_profile'] = p['role_profile']

    profiles = list(profiles.values())

    # Group by section
    by_section = defaultdict(list)
    for p in profiles:
        by_section[p['b_section']].append(p)

    results = {
        'by_section': {},
        'tests': {}
    }

    print("=== B SECTION EFFECTS ===\n")
    print("BY SECTION:")

    for sec in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B', 'other']:
        pars = by_section[sec]
        if not pars:
            continue

        # Collect metrics
        ht_deltas = [p['ht_profile']['ht_delta'] for p in pars if 'ht_profile' in p]
        en_rates = [p['role_profile']['en_rate'] for p in pars if 'role_profile' in p]
        fl_rates = [p['role_profile']['fl_rate'] for p in pars if 'role_profile' in p]
        fq_rates = [p['role_profile']['fq_rate'] for p in pars if 'role_profile' in p]
        gallows_rate = sum(1 for p in pars if p.get('initiation', {}).get('is_gallows_initial', False)) / len(pars)

        results['by_section'][sec] = {
            'count': len(pars),
            'ht_delta_mean': round(statistics.mean(ht_deltas), 3) if ht_deltas else None,
            'en_rate_mean': round(statistics.mean(en_rates), 3) if en_rates else None,
            'fl_rate_mean': round(statistics.mean(fl_rates), 3) if fl_rates else None,
            'fq_rate_mean': round(statistics.mean(fq_rates), 3) if fq_rates else None,
            'gallows_initial_rate': round(gallows_rate, 3)
        }

        print(f"\n  {sec}: n={len(pars)}")
        print(f"    HT delta: {results['by_section'][sec]['ht_delta_mean']}")
        print(f"    EN rate: {results['by_section'][sec]['en_rate_mean']}")
        print(f"    FL rate: {results['by_section'][sec]['fl_rate_mean']}")
        print(f"    FQ rate: {results['by_section'][sec]['fq_rate_mean']}")
        print(f"    Gallows-initial: {results['by_section'][sec]['gallows_initial_rate']}")

    # Statistical tests
    if HAS_SCIPY:
        # Kruskal-Wallis: HT delta by section
        ht_groups = []
        section_order = []
        for sec in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
            pars = by_section[sec]
            deltas = [p['ht_profile']['ht_delta'] for p in pars if 'ht_profile' in p]
            if len(deltas) > 1:
                ht_groups.append(deltas)
                section_order.append(sec)

        if len(ht_groups) >= 2:
            h_stat, p_val = scipy_stats.kruskal(*ht_groups)
            results['tests']['ht_delta_by_section'] = {
                'H': round(h_stat, 3),
                'p': round(p_val, 4),
                'significant': bool(p_val < 0.05),
                'sections': section_order
            }
            print(f"\nKruskal-Wallis (HT delta by section): H={h_stat:.3f}, p={p_val:.4f}")

        # Kruskal-Wallis: EN rate by section
        en_groups = []
        for sec in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
            pars = by_section[sec]
            rates = [p['role_profile']['en_rate'] for p in pars if 'role_profile' in p]
            if len(rates) > 1:
                en_groups.append(rates)

        if len(en_groups) >= 2:
            h_stat, p_val = scipy_stats.kruskal(*en_groups)
            results['tests']['en_rate_by_section'] = {
                'H': round(h_stat, 3),
                'p': round(p_val, 4),
                'significant': bool(p_val < 0.05)
            }
            print(f"Kruskal-Wallis (EN rate by section): H={h_stat:.3f}, p={p_val:.4f}")

    # C552 validation
    print("\n=== C552 VALIDATION ===")
    bio = results['by_section'].get('BIO', {})
    herbal = results['by_section'].get('HERBAL_B', {})
    pharma = results['by_section'].get('PHARMA', {})

    if bio and herbal:
        print(f"BIO EN rate ({bio.get('en_rate_mean')}) vs HERBAL EN rate ({herbal.get('en_rate_mean')})")
        if bio.get('en_rate_mean') and herbal.get('en_rate_mean'):
            if bio['en_rate_mean'] > herbal['en_rate_mean']:
                print("  [OK] BIO has higher EN (expected)")
            else:
                print("  [X] HERBAL has higher EN (unexpected)")

    if pharma and herbal:
        print(f"PHARMA FL rate ({pharma.get('fl_rate_mean')}) vs HERBAL FL rate ({herbal.get('fl_rate_mean')})")
        if pharma.get('fl_rate_mean') and herbal.get('fl_rate_mean'):
            if pharma['fl_rate_mean'] > herbal['fl_rate_mean']:
                print("  [OK] PHARMA has higher FL (expected)")
            else:
                print("  [?] FL comparison differs from expectation")

    # Save merged profiles
    with open(results_dir / 'b_paragraph_profiles.json', 'w') as f:
        json.dump({
            'system': 'B',
            'paragraph_count': len(profiles),
            'profiles': profiles
        }, f, indent=2)

    with open(results_dir / 'b_section_effects.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved to {results_dir}/")
    print("  - b_paragraph_profiles.json (merged)")
    print("  - b_section_effects.json")

if __name__ == '__main__':
    main()
