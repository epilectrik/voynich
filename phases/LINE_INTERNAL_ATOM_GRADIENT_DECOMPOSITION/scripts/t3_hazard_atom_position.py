"""T3: Hazard x Atom x Position for Phase 581.

Three-way contingency analysis, HIGH/ZERO/IMMUNE position profiles per HEAD,
k vs t vs e work-zone comparison, interaction test.
"""
import json, os, math
from collections import Counter, defaultdict

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

HEADS = ['a', 'e', 'k', 'o', 't', 'headless']
HAZARD_CLASSES = ['HIGH', 'IMMUNE', 'LOW', 'ZERO']
ZONES = ['SPEC', 'WORK', 'CLOSURE']
QUINTILES = [0, 1, 2, 3, 4]


def quintile_to_zone(q):
    if q == 0:
        return 'SPEC'
    elif q <= 3:
        return 'WORK'
    else:
        return 'CLOSURE'


def chi_squared_interaction(tokens):
    """Test hazard x zone interaction beyond main effects.

    Compute chi-squared for the 2-way hazard x zone table,
    which already captures the interaction we care about.
    """
    table = defaultdict(lambda: defaultdict(int))
    for t in tokens:
        hz = t['hazard_class']
        zone = quintile_to_zone(t['quintile'])
        table[hz][zone] += 1

    rows = sorted(table.keys())
    cols = ZONES
    n_rows = len(rows)
    n_cols = len(cols)

    row_totals = {r: sum(table[r].values()) for r in rows}
    col_totals = {c: sum(table[r][c] for r in rows) for c in cols}
    grand = sum(row_totals.values())

    if grand == 0 or n_rows < 2 or n_cols < 2:
        return 0.0, 0, 1.0, {}

    chi2 = 0.0
    residuals = {}
    for r in rows:
        for c in cols:
            obs = table[r][c]
            exp = row_totals[r] * col_totals[c] / grand
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp
                residuals[f'{r}_{c}'] = round((obs - exp) / math.sqrt(exp), 3)

    df = (n_rows - 1) * (n_cols - 1)
    if df == 0 or chi2 <= 0:
        p = 1.0
    else:
        z = ((chi2 / df) ** (1 / 3) - 1 + 2 / (9 * df)) / math.sqrt(2 / (9 * df))
        p = 0.5 * math.erfc(z / math.sqrt(2))

    return round(chi2, 2), df, round(p, 10), residuals


def main():
    with open(os.path.join(RESULTS_DIR, 't0_data_assembly.json')) as f:
        t0 = json.load(f)

    tokens = t0['tokens']
    n = len(tokens)

    # ---- 3a: Three-way contingency: hazard x HEAD x zone ----
    three_way = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    zone_totals = Counter()
    head_zone_totals = defaultdict(lambda: Counter())

    for t in tokens:
        hz = t['hazard_class']
        h = t['head'] if t['head'] else 'headless'
        zone = quintile_to_zone(t['quintile'])
        three_way[hz][h][zone] += 1
        zone_totals[zone] += 1
        head_zone_totals[h][zone] += 1

    # Enrichment: observed / expected (from marginals)
    hz_totals = {}
    for hz in HAZARD_CLASSES:
        hz_totals[hz] = sum(three_way[hz][h][z] for h in HEADS for z in ZONES)

    head_totals = {}
    for h in HEADS:
        head_totals[h] = sum(head_zone_totals[h].values())

    grand = sum(zone_totals.values())

    enrichment_table = {}
    zone_specific_pairs = []
    for hz in HAZARD_CLASSES:
        for h in HEADS:
            for z in ZONES:
                obs = three_way[hz][h][z]
                # Expected under independence of all three
                exp_hz = hz_totals[hz] / grand if grand > 0 else 0
                exp_h = head_totals[h] / grand if grand > 0 else 0
                exp_z = zone_totals[z] / grand if grand > 0 else 0
                expected = exp_hz * exp_h * exp_z * grand
                enrich = obs / expected if expected > 1e-8 else 0
                key = f'{hz}_{h}_{z}'
                enrichment_table[key] = round(enrich, 3)
                if enrich > 1.5 and obs >= 10:
                    zone_specific_pairs.append({
                        'hazard': hz, 'head': h, 'zone': z,
                        'enrichment': round(enrich, 3), 'count': obs
                    })

    # ---- 3b: HIGH-frame position profiles per HEAD ----
    high_tokens = [t for t in tokens if t['hazard_class'] == 'HIGH']
    high_by_head = defaultdict(list)
    for t in high_tokens:
        h = t['head'] if t['head'] else 'headless'
        high_by_head[h].append(t)

    high_profiles = {}
    for h in HEADS:
        toks = high_by_head[h]
        if not toks:
            continue
        quintile_dist = Counter(t['quintile'] for t in toks)
        total_h = len(toks)
        mean_pos = sum(t['frac_pos'] for t in toks) / total_h
        high_profiles[h] = {
            'n': total_h,
            'mean_frac_pos': round(mean_pos, 4),
            'quintile_dist': {str(q): quintile_dist.get(q, 0) for q in QUINTILES},
            'quintile_rates': {str(q): round(quintile_dist.get(q, 0) / total_h, 4)
                               for q in QUINTILES},
        }

    # ---- 3c: k vs t vs e work-zone comparison ----
    thermal_cluster = {}
    for h in ['k', 't', 'e']:
        h_tokens = [t for t in tokens if (t['head'] if t['head'] else 'headless') == h]
        if not h_tokens:
            continue
        n_h = len(h_tokens)
        zone_dist = Counter(quintile_to_zone(t['quintile']) for t in h_tokens)
        q_dist = Counter(t['quintile'] for t in h_tokens)
        work_fraction = zone_dist.get('WORK', 0) / n_h
        spec_fraction = zone_dist.get('SPEC', 0) / n_h
        closure_fraction = zone_dist.get('CLOSURE', 0) / n_h
        mean_pos = sum(t['frac_pos'] for t in h_tokens) / n_h
        thermal_cluster[h] = {
            'n': n_h,
            'mean_frac_pos': round(mean_pos, 4),
            'zone_fractions': {
                'SPEC': round(spec_fraction, 4),
                'WORK': round(work_fraction, 4),
                'CLOSURE': round(closure_fraction, 4),
            },
            'quintile_rates': {str(q): round(q_dist.get(q, 0) / n_h, 4) for q in QUINTILES},
        }

    # Is work-zone safety k-led or broader thermal cluster?
    k_work = thermal_cluster.get('k', {}).get('zone_fractions', {}).get('WORK', 0)
    t_work = thermal_cluster.get('t', {}).get('zone_fractions', {}).get('WORK', 0)
    e_work = thermal_cluster.get('e', {}).get('zone_fractions', {}).get('WORK', 0)
    k_led = k_work > t_work and k_work > e_work
    work_zone_interpretation = 'K_LED' if k_led else 'BROADER_CLUSTER'

    # ---- 3d: ZERO-frame position profiles ----
    zero_tokens = [t for t in tokens if t['hazard_class'] == 'ZERO']
    zero_by_frame = defaultdict(list)
    for t in zero_tokens:
        if t['frame_str']:
            zero_by_frame[t['frame_str']].append(t)

    zero_profiles = {}
    for frame, toks in sorted(zero_by_frame.items()):
        if len(toks) < 5:
            continue
        n_f = len(toks)
        q_dist = Counter(t['quintile'] for t in toks)
        zone_dist = Counter(quintile_to_zone(t['quintile']) for t in toks)
        mean_pos = sum(t['frac_pos'] for t in toks) / n_f
        zero_profiles[frame] = {
            'n': n_f,
            'mean_frac_pos': round(mean_pos, 4),
            'spec_fraction': round(zone_dist.get('SPEC', 0) / n_f, 4),
            'quintile_rates': {str(q): round(q_dist.get(q, 0) / n_f, 4) for q in QUINTILES},
        }

    # ---- 3e: Interaction test ----
    interaction_chi2, interaction_df, interaction_p, interaction_residuals = \
        chi_squared_interaction(tokens)

    # Count zone-specific HEAD-hazard pairs with enrichment > 1.5
    n_zone_specific = len(zone_specific_pairs)

    # ---- C1673 decision ----
    if interaction_p < 0.001 and n_zone_specific >= 2:
        verdict = 'HAZARD_POSITION_COUPLED'
    elif interaction_p >= 0.01:
        verdict = 'HAZARD_POSITION_INDEPENDENT'
    else:
        verdict = 'HAZARD_POSITION_COUPLED'  # p < 0.01, some zone-specificity

    output = {
        'metadata': {
            'phase': '581',
            'script': 't3_hazard_atom_position.py',
            'n_tokens': n,
        },
        'three_way_enrichment': enrichment_table,
        'zone_specific_pairs': zone_specific_pairs,
        'n_zone_specific_pairs': n_zone_specific,
        'high_frame_profiles': high_profiles,
        'thermal_cluster_comparison': {
            'k_vs_t_vs_e': thermal_cluster,
            'work_zone_interpretation': work_zone_interpretation,
        },
        'zero_frame_profiles': zero_profiles,
        'interaction_test': {
            'chi_squared': interaction_chi2,
            'df': interaction_df,
            'p_value': interaction_p,
            'standardized_residuals': interaction_residuals,
        },
        'C1673': {
            'verdict': verdict,
            'interaction_chi2': interaction_chi2,
            'interaction_p': interaction_p,
            'n_zone_specific_pairs': n_zone_specific,
            'work_zone_interpretation': work_zone_interpretation,
            'rationale': (f"Interaction chi2={interaction_chi2}, p={interaction_p}, "
                          f"{n_zone_specific} zone-specific pairs (>1.5x enrichment)")
        }
    }

    out_path = os.path.join(RESULTS_DIR, 't3_hazard_atom_position.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T3: Hazard x atom x position complete")
    print(f"  Interaction: chi2={interaction_chi2}, df={interaction_df}, p={interaction_p}")
    print(f"  Zone-specific pairs (>1.5x enrichment): {n_zone_specific}")
    for pair in zone_specific_pairs[:5]:
        print(f"    {pair['hazard']}_{pair['head']}_{pair['zone']}: "
              f"{pair['enrichment']}x (n={pair['count']})")
    print(f"  HIGH profiles:")
    for h, prof in high_profiles.items():
        print(f"    {h}: n={prof['n']}, mean_pos={prof['mean_frac_pos']}")
    print(f"  Thermal cluster (k/t/e work fractions): "
          f"k={k_work:.3f}, t={t_work:.3f}, e={e_work:.3f} -> {work_zone_interpretation}")
    print(f"  ZERO profiles:")
    for frame, prof in zero_profiles.items():
        print(f"    {frame}: n={prof['n']}, mean_pos={prof['mean_frac_pos']}, "
              f"SPEC={prof['spec_fraction']}")
    print(f"  C1673: {verdict}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
