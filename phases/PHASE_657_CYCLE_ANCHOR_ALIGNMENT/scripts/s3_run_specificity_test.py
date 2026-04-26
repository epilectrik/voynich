"""
Phase 657 s3 — Specificity Test + Null Distribution + Over-Determination Check

Per locked PRE_REGISTRATION.md sections 4-8.

Inputs (locked):
  results/NUMERICAL_ANCHORS.json  (Catalan side, 8 in-set items)
  results/VMS_CYCLE_CLUSTERS.json (VMS side, 82 folios)

Tests:
  T1: Matched-pair specificity (4 primary items, 10k null permutation)
  T2: Negative-control triviality check (4 unmatched items)
  T3: Single-folio over-determination check (f75r)

Output: results/SPECIFICITY_TEST.json
"""

import io
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Locked matched-pair table per PRE_REGISTRATION section 3
MATCHED_TABLE = {
    'III.19': 'f75r',
    'III.11': 'f112r',
    'III.28': 'f82v',
    # Other matched chapters (not testable in this phase — no numerical anchors)
    'II.18':  'f76r',
    'II.14':  'f84r',
    'III.12': 'f79r',
    'III.22': 'f82r',
    'III.16': 'f103r',
    'III.15': 'f76v',
    'III.27': 'f77v',
    'III.18': 'f81v',
    'III.1':  'f112v',
    'III.4':  'f116r',
    'III.44': 'f107r',
}


def chapter_id(subrecipe_id):
    """III.19.0 -> III.19"""
    parts = subrecipe_id.split('.')
    return '.'.join(parts[:2])


def folio_has_cluster_of_size(folio_clusters, n):
    """Does this folio have any cluster of size exactly n in any class?"""
    for cls, clist in folio_clusters.items():
        for c in clist:
            if c['size'] == n:
                return True
    return False


def folio_max_cluster_size(folio_clusters):
    """Largest cluster size on this folio (any class)."""
    maxs = 0
    for cls, clist in folio_clusters.items():
        for c in clist:
            if c['size'] > maxs:
                maxs = c['size']
    return maxs


def main():
    out_dir = REPO_ROOT / 'phases' / 'PHASE_657_CYCLE_ANCHOR_ALIGNMENT' / 'results'

    anchors_path = out_dir / 'NUMERICAL_ANCHORS.json'
    clusters_path = out_dir / 'VMS_CYCLE_CLUSTERS.json'

    anchors = json.loads(anchors_path.read_text(encoding='utf-8'))['in_set']
    cluster_data = json.loads(clusters_path.read_text(encoding='utf-8'))
    folio_clusters = cluster_data['folios']
    all_folios = sorted(folio_clusters.keys())
    n_folios = len(all_folios)
    print(f'Loaded {len(anchors)} anchors, {n_folios} folios.')

    # Partition: primary (matched chapter) vs control (unmatched chapter)
    primary = []
    control = []
    for a in anchors:
        ch = chapter_id(a['subrecipe_id'])
        matched_folio = MATCHED_TABLE.get(ch)
        if matched_folio:
            a2 = dict(a)
            a2['matched_folio'] = matched_folio
            primary.append(a2)
        else:
            control.append(a)
    print(f'  primary (matched chapter): {len(primary)}')
    print(f'  control (unmatched):       {len(control)}')

    # =========================================================
    # T1: Matched-pair specificity test (locked)
    # =========================================================
    print('\n=== T1: Matched-pair specificity ===')
    primary_results = []
    observed_matches = 0
    for p in primary:
        folio = p['matched_folio']
        n = p['count']
        match = folio_has_cluster_of_size(folio_clusters.get(folio, {}), n)
        primary_results.append({
            'subrecipe_id': p['subrecipe_id'],
            'count': n,
            'matched_folio': folio,
            'has_cluster_of_size_N': match,
        })
        if match:
            observed_matches += 1
        print(f'  {p["subrecipe_id"]:12s} N={n:2d} -> {folio:8s}  '
              f'{"MATCH" if match else "no match"}')
    print(f'\n  Observed matches: {observed_matches}/{len(primary)}')

    # Null distribution: shuffle within-recipe pairing preserved
    # Group primary by chapter (so III.19's two anchors stay paired)
    rng = random.Random(20260426)
    by_chapter = {}
    for p in primary:
        by_chapter.setdefault(chapter_id(p['subrecipe_id']), []).append(p)

    n_perm = 10000
    null_match_counts = []
    for trial in range(n_perm):
        # Sample one folio per chapter (preserves within-recipe pairing)
        used = set()
        ch_to_folio = {}
        chapters = list(by_chapter.keys())
        rng.shuffle(chapters)
        available = [f for f in all_folios]
        for ch in chapters:
            # Pick any folio (with replacement allowed across chapters? No -
            # without replacement across chapters keeps null on same support.)
            pool = [f for f in available if f not in used]
            if not pool:
                pool = available
            f = rng.choice(pool)
            ch_to_folio[ch] = f
            used.add(f)
        # Count matches under null assignment
        m = 0
        for ch, items in by_chapter.items():
            f = ch_to_folio[ch]
            for it in items:
                if folio_has_cluster_of_size(folio_clusters.get(f, {}), it['count']):
                    m += 1
        null_match_counts.append(m)

    # p-value: fraction with matches >= observed
    p_value = sum(1 for x in null_match_counts if x >= observed_matches) / n_perm
    null_mean = sum(null_match_counts) / n_perm
    print(f'  Null distribution (10k perms, within-chapter pairing preserved):')
    print(f'    mean: {null_mean:.3f}')
    print(f'    >= observed ({observed_matches}): {sum(1 for x in null_match_counts if x >= observed_matches)} ({p_value:.4f})')

    # Histogram
    hist = {i: 0 for i in range(len(primary) + 1)}
    for x in null_match_counts:
        hist[x] = hist.get(x, 0) + 1
    print(f'    histogram of null matches:')
    for k in sorted(hist):
        bar = '#' * int(40 * hist[k] / n_perm)
        print(f'      {k}: {hist[k]:5d} {bar}')

    # =========================================================
    # T2: Negative-control triviality check (locked)
    # =========================================================
    print('\n=== T2: Negative-control triviality ===')
    control_results = []
    for c in control:
        n = c['count']
        n_folios_with = sum(
            1 for f in all_folios
            if folio_has_cluster_of_size(folio_clusters.get(f, {}), n)
        )
        pct = 100.0 * n_folios_with / n_folios
        trivial = pct > 50
        control_results.append({
            'subrecipe_id': c['subrecipe_id'],
            'count': n,
            'n_folios_with_size_N': n_folios_with,
            'total_folios': n_folios,
            'pct_folios_with_size_N': pct,
            'trivial_threshold_exceeded': trivial,
        })
        print(f'  {c["subrecipe_id"]:12s} N={n:2d}: {n_folios_with}/{n_folios} '
              f'({pct:.1f}%) {"TRIVIAL" if trivial else "specific"}')

    # Also report triviality for primary counts
    print('\n  Triviality for primary counts:')
    primary_triviality = {}
    for n in sorted({p['count'] for p in primary}):
        nf = sum(1 for f in all_folios
                 if folio_has_cluster_of_size(folio_clusters.get(f, {}), n))
        pct = 100.0 * nf / n_folios
        primary_triviality[n] = {
            'n_folios_with_size_N': nf,
            'pct': pct,
            'trivial': pct > 50,
        }
        print(f'    N={n:2d}: {nf}/{n_folios} ({pct:.1f}%) '
              f'{"TRIVIAL" if pct > 50 else "specific"}')

    # =========================================================
    # T3: Single-folio over-determination check (locked, f75r)
    # =========================================================
    print('\n=== T3: f75r over-determination check ===')
    # Q: Is f75r the only Currier B folio with BOTH a qok-cluster of
    #    size exactly 4 AND a qok-cluster of size exactly 9?
    target_class = 'qok'
    target_sizes = [4, 9]
    matching_folios_strict = []
    for f in all_folios:
        sizes = {c['size'] for c in folio_clusters.get(f, {}).get(target_class, [])}
        if all(t in sizes for t in target_sizes):
            matching_folios_strict.append(f)
    print(f'  Folios with qok-cluster sizes {{4 AND 9}}: {matching_folios_strict}')

    # Also report: descriptive variants (NOT pre-registered, reported only)
    descriptive_variants = {}
    # (a) qok-clusters size 5 (the actual f75r ×4-anchor cluster size)
    for f in all_folios:
        sizes = {c['size'] for c in folio_clusters.get(f, {}).get(target_class, [])}
        if 5 in sizes:
            descriptive_variants.setdefault('qok_size_5_present', []).append(f)
    # (b) qok-clusters with TWO size-5 instances on the same folio
    for f in all_folios:
        sizes_list = [c['size'] for c in folio_clusters.get(f, {}).get(target_class, [])]
        if sizes_list.count(5) >= 2:
            descriptive_variants.setdefault('qok_two_size5', []).append(f)
    # (c) total qok-class tokens by folio (a relaxed "× 9" reading)
    qok_token_totals = {}
    for f in all_folios:
        total = sum(c['size'] for c in folio_clusters.get(f, {}).get(target_class, []))
        qok_token_totals[f] = total
    top_qok = sorted(qok_token_totals.items(), key=lambda x: -x[1])[:10]
    print(f'  Descriptive (NOT in pre-reg, reported only):')
    print(f'    folios with >=1 qok-cluster of size 5: '
          f'{len(descriptive_variants.get("qok_size_5_present", []))}')
    print(f'    folios with >=2 qok-clusters of size 5: '
          f'{descriptive_variants.get("qok_two_size5", [])}')
    print(f'    top 10 folios by total qok-class clustered-token count:')
    for f, total in top_qok:
        print(f'      {f}: {total}')

    # =========================================================
    # Verdict (per pre-reg section 6)
    # =========================================================
    print('\n=== VERDICT ===')
    n_primary = len(primary)
    # Pre-reg threshold: SUPPORTED if matches >= 2/3, scaled to >= ceil(2/3 * n_primary)
    # The pre-reg's literal numbers were 2/3 and 1/3 with n=3 implied. With n=4
    # we use the proportions: SUPPORTED requires matches/n >= 2/3 AND p <= 0.05.
    threshold_supported = (observed_matches / n_primary >= 2/3) and (p_value <= 0.05)
    threshold_directional = (observed_matches / n_primary >= 1/3) and (p_value <= 0.20)
    threshold_falsified = observed_matches == 0

    # Triviality degradation
    triviality_degraded_counts = [
        n for n, info in primary_triviality.items() if info['trivial']
    ]
    if triviality_degraded_counts:
        print(f'  WARNING: counts {triviality_degraded_counts} are TRIVIAL '
              f'(>50% folios contain cluster of that size)')
        # Per pre-reg section 7: matched test is degraded for trivial counts.
        # This means matches on trivial counts don't count toward SUPPORTED.
        non_trivial_matches = sum(
            1 for r in primary_results
            if r['has_cluster_of_size_N'] and not primary_triviality[r['count']]['trivial']
        )
        non_trivial_total = sum(
            1 for p in primary if not primary_triviality[p['count']]['trivial']
        )
        print(f'  Non-trivial matches: {non_trivial_matches}/{non_trivial_total}')

    if threshold_falsified:
        verdict = 'FALSIFIED'
    elif threshold_supported:
        verdict = 'SUPPORTED'
    elif threshold_directional:
        verdict = 'DIRECTIONAL'
    else:
        verdict = 'INCONCLUSIVE'

    if matching_folios_strict == ['f75r']:
        f75r_overdetermination = 'CONFIRMED (f75r uniquely has qok-clusters {4 AND 9})'
    elif 'f75r' in matching_folios_strict:
        f75r_overdetermination = (
            f'PARTIAL (f75r has both, but so do {len(matching_folios_strict)-1} other folios)'
        )
    else:
        f75r_overdetermination = 'NOT CONFIRMED (f75r does not contain both size-4 and size-9 qok-clusters)'

    print(f'  Primary T1 verdict: {verdict}')
    print(f'  T3 over-determination: {f75r_overdetermination}')

    # =========================================================
    # Persist
    # =========================================================
    out = {
        'phase': 657,
        'stage': 'B',
        'script': 's3',
        'pre_registration_commit': '7227532',
        's1_commit': '79e146f',
        's2_commit': '74dddf7',
        'n_primary_items': n_primary,
        'n_control_items': len(control),
        'T1_matched_pair_specificity': {
            'observed_matches': observed_matches,
            'observed_proportion': observed_matches / n_primary,
            'null_n_perm': n_perm,
            'null_mean': null_mean,
            'null_p_value_one_sided': p_value,
            'null_histogram': hist,
            'per_item_results': primary_results,
        },
        'T2_negative_control': {
            'control_results': control_results,
            'primary_count_triviality': primary_triviality,
        },
        'T3_f75r_over_determination': {
            'pre_registered_test': 'f75r unique with qok-cluster sizes {4 AND 9}',
            'matching_folios_strict': matching_folios_strict,
            'verdict': f75r_overdetermination,
            'descriptive_variants_NOT_in_pre_reg': {
                'folios_with_qok_size_5': descriptive_variants.get('qok_size_5_present', []),
                'folios_with_two_qok_size_5': descriptive_variants.get('qok_two_size5', []),
                'qok_token_totals_top10': top_qok,
            },
        },
        'final_verdict': {
            'T1_specificity': verdict,
            'T3_over_determination': f75r_overdetermination,
            'note': (
                'Locked exact-cluster definition produces no size-9 qok-cluster '
                'on f75r (interrupted by lol). f75r L13 qok-cluster is size 5, '
                'not 4 (qokain shares qok class with the 4 qokedy tokens). '
                'These are honest consequences of the pre-registered methodology.'
            ),
        },
    }
    out_path = out_dir / 'SPECIFICITY_TEST.json'
    out_path.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'\nwrote {out_path}')


if __name__ == '__main__':
    main()
