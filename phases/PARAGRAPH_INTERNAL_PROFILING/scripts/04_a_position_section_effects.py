"""
04_a_position_section_effects.py - A Position and Section Effects

Tests:
- ANOVA: RI rate by folio_position
- ANOVA: PP composition by section (H/P/T)
- Kruskal-Wallis for non-normal distributions

Depends on: 01-03 scripts
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

def cohens_d(group1, group2):
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return None
    var1, var2 = statistics.variance(group1), statistics.variance(group2)
    pooled_std = ((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2)
    pooled_std = pooled_std ** 0.5
    if pooled_std == 0:
        return None
    return (statistics.mean(group1) - statistics.mean(group2)) / pooled_std

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load profiles from previous scripts
    with open(results_dir / 'a_size_density.json') as f:
        size_data = json.load(f)

    with open(results_dir / 'a_ri_profile.json') as f:
        ri_data = json.load(f)

    with open(results_dir / 'a_pp_composition.json') as f:
        pp_data = json.load(f)

    # Merge profiles
    profiles = {}
    for p in size_data['profiles']:
        profiles[p['par_id']] = {
            'par_id': p['par_id'],
            'folio': p['folio'],
            'section': p['section'],
            'folio_position': p['folio_position'],
            'size': p['size']
        }

    for p in ri_data['profiles']:
        if p['par_id'] in profiles:
            profiles[p['par_id']]['ri_profile'] = p['ri_profile']

    for p in pp_data['profiles']:
        if p['par_id'] in profiles:
            profiles[p['par_id']]['pp_profile'] = p['pp_profile']

    profiles = list(profiles.values())

    # Group by folio_position
    by_position = defaultdict(list)
    for p in profiles:
        by_position[p['folio_position']].append(p)

    # Group by section
    by_section = defaultdict(list)
    for p in profiles:
        section = p['section'] if p['section'] in ['H', 'P', 'T'] else 'other'
        by_section[section].append(p)

    results = {
        'by_folio_position': {},
        'by_section': {},
        'tests': {}
    }

    # === FOLIO POSITION ANALYSIS ===
    print("=== A POSITION AND SECTION EFFECTS ===\n")
    print("BY FOLIO POSITION:")

    ri_by_pos = {}
    pp_by_pos = {}

    for pos in ['first', 'middle', 'last', 'only']:
        pars = by_position[pos]
        if not pars:
            continue

        ri_rates = [p['ri_profile']['ri_rate'] for p in pars if 'ri_profile' in p]
        pp_rates = [p['pp_profile']['pp_rate'] for p in pars if 'pp_profile' in p]

        ri_by_pos[pos] = ri_rates
        pp_by_pos[pos] = pp_rates

        results['by_folio_position'][pos] = {
            'count': len(pars),
            'ri_rate_mean': round(statistics.mean(ri_rates), 3) if ri_rates else None,
            'ri_rate_stdev': round(statistics.stdev(ri_rates), 3) if len(ri_rates) > 1 else None,
            'pp_rate_mean': round(statistics.mean(pp_rates), 3) if pp_rates else None,
            'pp_rate_stdev': round(statistics.stdev(pp_rates), 3) if len(pp_rates) > 1 else None
        }

        print(f"  {pos}: n={len(pars)}, RI={results['by_folio_position'][pos]['ri_rate_mean']}, PP={results['by_folio_position'][pos]['pp_rate_mean']}")

    # Statistical tests
    if HAS_SCIPY:
        # Kruskal-Wallis for RI by position
        pos_groups = [ri_by_pos[p] for p in ['first', 'middle', 'last'] if p in ri_by_pos and len(ri_by_pos[p]) > 1]
        if len(pos_groups) >= 2:
            h_stat, p_val = scipy_stats.kruskal(*pos_groups)
            results['tests']['ri_by_position_kruskal'] = {
                'H': round(float(h_stat), 3),
                'p': round(float(p_val), 4),
                'significant': bool(p_val < 0.05)
            }
            print(f"\n  Kruskal-Wallis (RI by position): H={h_stat:.3f}, p={p_val:.4f}")

        # First vs Last comparison
        if 'first' in ri_by_pos and 'last' in ri_by_pos:
            d = cohens_d(ri_by_pos['first'], ri_by_pos['last'])
            if d is not None:
                results['tests']['ri_first_vs_last_cohens_d'] = round(d, 3)
                print(f"  Cohen's d (first vs last RI): {d:.3f}")

    # === SECTION ANALYSIS ===
    print("\nBY SECTION:")

    ri_by_sec = {}
    pp_by_sec = {}
    compound_by_sec = {}

    for sec in ['H', 'P', 'T', 'other']:
        pars = by_section[sec]
        if not pars:
            continue

        ri_rates = [p['ri_profile']['ri_rate'] for p in pars if 'ri_profile' in p]
        pp_rates = [p['pp_profile']['pp_rate'] for p in pars if 'pp_profile' in p]
        compound_rates = [p['pp_profile']['pp_compound_rate'] for p in pars if 'pp_profile' in p]

        ri_by_sec[sec] = ri_rates
        pp_by_sec[sec] = pp_rates
        compound_by_sec[sec] = compound_rates

        results['by_section'][sec] = {
            'count': len(pars),
            'ri_rate_mean': round(statistics.mean(ri_rates), 3) if ri_rates else None,
            'pp_rate_mean': round(statistics.mean(pp_rates), 3) if pp_rates else None,
            'pp_compound_rate_mean': round(statistics.mean(compound_rates), 3) if compound_rates else None
        }

        print(f"  {sec}: n={len(pars)}, RI={results['by_section'][sec]['ri_rate_mean']}, PP={results['by_section'][sec]['pp_rate_mean']}, compound={results['by_section'][sec]['pp_compound_rate_mean']}")

    # Section tests
    if HAS_SCIPY:
        sec_groups = [ri_by_sec[s] for s in ['H', 'P', 'T'] if s in ri_by_sec and len(ri_by_sec[s]) > 1]
        if len(sec_groups) >= 2:
            h_stat, p_val = scipy_stats.kruskal(*sec_groups)
            results['tests']['ri_by_section_kruskal'] = {
                'H': round(float(h_stat), 3),
                'p': round(float(p_val), 4),
                'significant': bool(p_val < 0.05)
            }
            print(f"\n  Kruskal-Wallis (RI by section): H={h_stat:.3f}, p={p_val:.4f}")

    # Save merged profiles
    with open(results_dir / 'a_paragraph_profiles.json', 'w') as f:
        json.dump({
            'system': 'A',
            'paragraph_count': len(profiles),
            'profiles': profiles
        }, f, indent=2)

    # Save analysis results
    with open(results_dir / 'a_position_section_effects.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved to {results_dir}/")
    print("  - a_paragraph_profiles.json (merged)")
    print("  - a_position_section_effects.json")

if __name__ == '__main__':
    main()
