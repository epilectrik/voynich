"""
Phase 628 Script 1: Recipe-Folio Matching (Distillation -> R1)

Core PL chapter-to-V folio matching for the distillation->REGIME_1 training set.

T1: Distillation->R1 residual matching
T2: Cross-validation stability
T3: Per-dimension contribution for content-validated matches
T4: Match summary table with English content snippets
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from shared_628 import (
    load_family_chapters,
    load_regime_folios,
    load_pl_chapters,
    load_pl_english_lines,
    load_b_operational_profiles,
    load_b_deployment_features,
    residual_match,
    cv_stability,
    round_floats,
    TUNED_DIMS,
    RESULTS_DIR,
)

DIM_NAMES = [
    'heat_rate -> -k_ratio',
    'monitoring_rate -> h_ratio',
    'correction_rate -> e_ratio',
    'termination_rate -> terminal_rate',
    'consistency_frac -> -m_linefinal_rate',
    'heat_rate -> -suffix_transparency',
    'monitoring_rate -> -header_enrichment',
    'heat_transition_rate -> thermo_ke',
]


def get_english_snippet(en_lines: list, start: int, end: int) -> str:
    """Extract first meaningful line from chapter's English text."""
    for i in range(start, min(end, len(en_lines))):
        line = en_lines[i].strip()
        # Skip empty lines, chapter headers, page markers, and very short lines
        if len(line) < 15:
            continue
        up = line.upper()
        if up.startswith('CHAPTER') or up.startswith('CAP.') or up.startswith('CAPVT'):
            continue
        if up.startswith('--- PAGE'):
            continue
        # Truncate to reasonable length
        if len(line) > 120:
            line = line[:117] + '...'
        return line
    return '(no content)'


def run_t1(dist_chs, r1_fols, op_profiles, deploy_features):
    """T1: Distillation -> R1 matching."""
    print('=' * 70)
    print('T1: DISTILLATION -> R1 MATCHING (TRAINING SET)')
    print('=' * 70)
    print(f'  PL chapters (distillation): {len(dist_chs)}')
    print(f'  V folios (REGIME_1):         {len(r1_fols)}')
    print(f'  Dimensions:                  {len(TUNED_DIMS)}')
    print()

    result = residual_match(dist_chs, r1_fols, TUNED_DIMS,
                            op_profiles, deploy_features)

    print(f'  Mean distance:    {result["mean_distance"]:.4f}')
    print(f'  Mean ratio:       {result["mean_ratio"]:.3f}')
    print(f'  Confident (>1.15): {result["n_confident"]} / {result["n_pl"]}')
    print(f'  Unique NN:        {result["n_unique_nn"]} / {result["n_v"]}')
    print()

    print(f'  {"Ch#":>4} {"Folio":<8} {"Dist":>7} {"2nd":>7} {"Ratio":>6} {"Conf":>5}')
    print(f'  {"----":>4} {"-----":<8} {"----":>7} {"---":>7} {"-----":>6} {"----":>5}')
    for m in result['match_table']:
        conf = 'Y' if m['confident'] else ''
        print(f'  {m["chapter_number"]:>4} {m["folio"]:<8} '
              f'{m["distance"]:7.4f} {m["second_distance"]:7.4f} '
              f'{m["ratio"]:6.3f} {conf:>5}')
    print()

    # Strip non-serializable large arrays from result for JSON
    t1_out = {k: v for k, v in result.items()
              if k not in ('dmat', 'pl_std', 'v_std')}
    return result, t1_out


def run_t2(dist_chs, r1_fols, op_profiles, deploy_features):
    """T2: Cross-validation stability."""
    print('=' * 70)
    print('T2: CROSS-VALIDATION STABILITY')
    print('=' * 70)

    cv = cv_stability(dist_chs, r1_fols, TUNED_DIMS,
                      op_profiles=op_profiles,
                      deploy_features=deploy_features)

    print(f'  Trials: {cv["n_trials"]}')
    print(f'  Consensus (>40%): {cv["n_consensus"]} / {cv["n_chapters"]}')
    print()

    print(f'  {"Ch#":>4} {"TopMatch":<8} {"Freq":>6} {"2ndMatch":<8} {"2ndF":>6} {"Cons":>5}')
    print(f'  {"----":>4} {"--------":<8} {"----":>6} {"--------":<8} {"----":>6} {"----":>5}')
    for row in cv['cv_table']:
        cons = 'Y' if row['consensus'] else ''
        second = row['second_match'] or '-'
        print(f'  {row["chapter_number"]:>4} {row["top_match"]:<8} '
              f'{row["top_freq"]:6.3f} {second:<8} '
              f'{row["second_freq"]:6.3f} {cons:>5}')
    print()

    return cv


def run_t3(dist_chs, r1_fols, op_profiles, deploy_features):
    """T3: Per-dimension contribution for content-validated matches."""
    print('=' * 70)
    print('T3: PER-DIMENSION CONTRIBUTION (CONTENT-VALIDATED MATCHES)')
    print('=' * 70)

    t3_results = {}

    # --- Match 1: Ch19 -> f75r (distillation -> R1) ---
    # --- Match 2: Ch18 -> f76r (distillation -> R1) ---
    # Both use the distillation -> R1 match
    dist_result = residual_match(dist_chs, r1_fols, TUNED_DIMS,
                                 op_profiles, deploy_features)

    target_matches = [
        ('Ch19_f75r', 19, 'f75r', 'distillation->R1'),
        ('Ch18_f76r', 18, 'f76r', 'distillation->R1'),
    ]

    for label, ch_num, target_folio, context in target_matches:
        print(f'\n  --- {label} ({context}) ---')
        found = None
        for m in dist_result['match_table']:
            if m['chapter_number'] == ch_num and m['folio'] == target_folio:
                found = m
                break

        if found is None:
            # The match may not have landed on the target folio via greedy
            # assignment. Search for the closest match to find this chapter's
            # actual assignment and report it, plus report distance to target.
            actual = [m for m in dist_result['match_table']
                      if m['chapter_number'] == ch_num]
            if actual:
                found = actual[0]
                print(f'  NOTE: Ch{ch_num} matched to {found["folio"]} '
                      f'(not {target_folio})')
            else:
                # If there are duplicate chapter numbers, grab the first match
                # for this chapter number from the full table
                print(f'  WARNING: Ch{ch_num} not found in match table')
                t3_results[label] = {'error': f'Ch{ch_num} not in match table'}
                continue

        per_dim = found['per_dim_dist_sq']
        total_sq = sum(per_dim)
        print(f'  Total distance: {found["distance"]:.4f}')
        print(f'  Matched folio:  {found["folio"]}')
        print(f'  Ratio:          {found["ratio"]:.3f}')
        print()
        print(f'  {"Dimension":<45} {"Sq.Dist":>8} {"% of total":>10}')
        print(f'  {"-" * 45} {"-------":>8} {"----------":>10}')
        dim_contribs = []
        for d_idx, d_name in enumerate(DIM_NAMES):
            sq = per_dim[d_idx]
            pct = 100 * sq / total_sq if total_sq > 0 else 0
            print(f'  {d_name:<45} {sq:8.4f} {pct:9.1f}%')
            dim_contribs.append({
                'dimension': d_name,
                'sq_distance': round(sq, 4),
                'pct_of_total': round(pct, 1),
            })

        t3_results[label] = {
            'chapter_number': ch_num,
            'matched_folio': found['folio'],
            'target_folio': target_folio,
            'distance': found['distance'],
            'ratio': found['ratio'],
            'per_dim': dim_contribs,
        }

    # --- Match 3: Ch12 -> f113v (sublimation -> R3) ---
    label = 'Ch12_f113v'
    ch_num = 12
    target_folio = 'f113v'
    context_str = 'sublimation->R3'
    print(f'\n  --- {label} ({context_str}) ---')

    sub_chs = load_family_chapters('sublimation')
    r3_fols = load_regime_folios('REGIME_3')
    print(f'  Sublimation chapters: {len(sub_chs)}')
    print(f'  REGIME_3 folios:      {len(r3_fols)}')

    sub_result = residual_match(sub_chs, r3_fols, TUNED_DIMS,
                                op_profiles, deploy_features)

    found = None
    for m in sub_result['match_table']:
        if m['chapter_number'] == ch_num and m['folio'] == target_folio:
            found = m
            break

    if found is None:
        actual = [m for m in sub_result['match_table']
                  if m['chapter_number'] == ch_num]
        if actual:
            found = actual[0]
            print(f'  NOTE: Ch{ch_num} matched to {found["folio"]} '
                  f'(not {target_folio})')
        else:
            print(f'  WARNING: Ch{ch_num} not found in sublimation match table')
            t3_results[label] = {'error': f'Ch{ch_num} not in sublimation match'}

    if found is not None:
        per_dim = found['per_dim_dist_sq']
        total_sq = sum(per_dim)
        print(f'  Total distance: {found["distance"]:.4f}')
        print(f'  Matched folio:  {found["folio"]}')
        print(f'  Ratio:          {found["ratio"]:.3f}')
        print()
        print(f'  {"Dimension":<45} {"Sq.Dist":>8} {"% of total":>10}')
        print(f'  {"-" * 45} {"-------":>8} {"----------":>10}')
        dim_contribs = []
        for d_idx, d_name in enumerate(DIM_NAMES):
            sq = per_dim[d_idx]
            pct = 100 * sq / total_sq if total_sq > 0 else 0
            print(f'  {d_name:<45} {sq:8.4f} {pct:9.1f}%')
            dim_contribs.append({
                'dimension': d_name,
                'sq_distance': round(sq, 4),
                'pct_of_total': round(pct, 1),
            })

        t3_results[label] = {
            'chapter_number': ch_num,
            'matched_folio': found['folio'],
            'target_folio': target_folio,
            'distance': found['distance'],
            'ratio': found['ratio'],
            'per_dim': dim_contribs,
        }

    print()
    return t3_results


def run_t4(dist_result, cv_result):
    """T4: Match summary table with content snippets."""
    print('=' * 70)
    print('T4: MATCH SUMMARY TABLE WITH CONTENT')
    print('=' * 70)

    en_lines = load_pl_english_lines()
    pl_chapters = load_pl_chapters()

    # Build lookup: chapter_idx -> E1 chapter info
    # E1 chapters are indexed by position in list, and channel features
    # use chapter_idx matching that position
    ch_lookup = {}
    for i, ch in enumerate(pl_chapters):
        ch_lookup[i] = ch

    # Build CV lookup: chapter_number -> top_freq
    cv_lookup = {}
    for row in cv_result.get('cv_table', []):
        key = row['chapter_number']
        cv_lookup[key] = row['top_freq']

    summary_table = []
    print()
    print(f'  {"Ch#":>4} {"Part":<14} {"Family":<14} {"Folio":<8} '
          f'{"Dist":>7} {"Ratio":>6} {"CV%":>5}  Content')
    print(f'  {"----":>4} {"----":<14} {"------":<14} {"-----":<8} '
          f'{"----":>7} {"-----":>6} {"---":>5}  -------')

    for m in dist_result['match_table']:
        ch_idx = m.get('chapter_idx', 0)
        ch_info = ch_lookup.get(ch_idx, {})
        part = ch_info.get('part', '?')
        family = m.get('family', ch_info.get('primary_family', '?'))

        # Get English snippet
        start = ch_info.get('en_line_start', 0)
        end = ch_info.get('en_line_end', 0)
        snippet = get_english_snippet(en_lines, start, end)

        # CV consensus %
        cv_freq = cv_lookup.get(m['chapter_number'], 0.0)
        cv_pct = f'{cv_freq * 100:.0f}' if cv_freq > 0 else '-'

        print(f'  {m["chapter_number"]:>4} {part:<14} {family:<14} '
              f'{m["folio"]:<8} {m["distance"]:7.4f} {m["ratio"]:6.3f} '
              f'{cv_pct:>5}  {snippet[:80]}')

        summary_table.append({
            'chapter_number': m['chapter_number'],
            'chapter_idx': ch_idx,
            'part': part,
            'family': family,
            'folio': m['folio'],
            'distance': m['distance'],
            'ratio': m['ratio'],
            'confident': m['confident'],
            'cv_consensus_pct': round(cv_freq * 100, 1),
            'content_snippet': snippet,
        })

    print()
    return summary_table


def main():
    print('Phase 628 Script 1: Recipe-Folio Matching')
    print('=' * 70)

    # Pre-load shared data once
    op_profiles = load_b_operational_profiles()
    deploy_features, _ = load_b_deployment_features()

    # Load distillation chapters and R1 folios
    dist_chs = load_family_chapters('distillation')
    r1_fols = load_regime_folios('REGIME_1')
    print(f'Loaded: {len(dist_chs)} distillation chapters, '
          f'{len(r1_fols)} REGIME_1 folios')
    print()

    # T1: Core matching
    dist_result, t1_out = run_t1(dist_chs, r1_fols,
                                  op_profiles, deploy_features)

    # T2: Cross-validation
    cv_result = run_t2(dist_chs, r1_fols, op_profiles, deploy_features)

    # T3: Per-dimension decomposition
    t3_results = run_t3(dist_chs, r1_fols, op_profiles, deploy_features)

    # T4: Summary table with content
    t4_table = run_t4(dist_result, cv_result)

    # ---- Save output ----
    output = {
        'T1_distillation_matching': round_floats(t1_out, 4),
        'T2_cross_validation': round_floats(cv_result, 4),
        'T3_per_dimension': round_floats(t3_results, 4),
        'T4_match_summary': round_floats(t4_table, 4),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'recipe_matching.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f'Output saved: {out_path}')
    print('Done.')


if __name__ == '__main__':
    main()
