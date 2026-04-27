"""
Phase 658 s1 — Lexeme-Identity Cluster Specificity Test

Locked methodology per PRE_REGISTRATION.md (commit f0f151e).

Cluster def: maximal run of N>=2 consecutive identical `word` field tokens
within a line or spanning at most 1 line break.

Match rule: folio has cluster of size >= N (inclusive >= reading per
pre-reg section 4).

Inputs:
  phases/PHASE_657_CYCLE_ANCHOR_ALIGNMENT/results/NUMERICAL_ANCHORS.json

Outputs:
  results/LEXEME_CLUSTERS.json   (per-folio cluster inventory)
  results/SPECIFICITY_TEST.json  (T1 + T2 + T3)
  results/FINDINGS.md            (verdict)
"""

import io
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.voynich import Transcript

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MIN_CLUSTER_SIZE = 2

MATCHED_TABLE = {
    'III.19': 'f75r',  'III.11': 'f112r', 'III.28': 'f82v',
    'II.18':  'f76r',  'II.14':  'f84r',  'III.12': 'f79r',
    'III.22': 'f82r',  'III.16': 'f103r', 'III.15': 'f76v',
    'III.27': 'f77v',  'III.18': 'f81v',  'III.1':  'f112v',
    'III.4':  'f116r', 'III.44': 'f107r',
}


def chapter_id(subrecipe_id):
    return '.'.join(subrecipe_id.split('.')[:2])


def enumerate_lexeme_clusters(folio_tokens):
    """Returns list of (size, lexeme, line_start, line_end, token_indices)."""
    seq = []
    for idx, t in enumerate(folio_tokens):
        if not t.word:
            continue
        try:
            ln = int(t.line)
        except (ValueError, TypeError):
            ln = t.line
        seq.append((idx, t.word, ln))

    clusters = []
    i = 0
    n = len(seq)
    while i < n:
        word = seq[i][1]
        line_breaks = 0
        prev_line = seq[i][2]
        j = i + 1
        while j < n:
            cur_line = seq[j][2]
            if cur_line != prev_line:
                line_breaks += 1
                if line_breaks > 1:
                    break
            if seq[j][1] != word:
                break
            prev_line = cur_line
            j += 1
        size = j - i
        if size >= MIN_CLUSTER_SIZE:
            clusters.append({
                'size': size,
                'lexeme': word,
                'line_start': seq[i][2],
                'line_end': seq[j - 1][2],
                'token_indices': [seq[k][0] for k in range(i, j)],
            })
        i = j if size >= MIN_CLUSTER_SIZE else i + 1
    return clusters


def folio_has_cluster_of_size_at_least(clusters, n):
    return any(c['size'] >= n for c in clusters)


def folio_max_lexeme_cluster_size(clusters):
    return max((c['size'] for c in clusters), default=0)


def main():
    out_dir = REPO_ROOT / 'phases' / 'PHASE_658_LEXEME_CLUSTER_RETEST' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    # ----- Build VMS-side cluster inventory -----
    print('Loading Currier B tokens...')
    tx = Transcript()
    by_folio = defaultdict(list)
    for tok in tx.currier_b():
        by_folio[tok.folio].append(tok)
    print(f'  {len(by_folio)} folios, {sum(len(v) for v in by_folio.values())} tokens.')

    folio_clusters = {}
    for f, toks in sorted(by_folio.items()):
        folio_clusters[f] = enumerate_lexeme_clusters(toks)

    # Distribution
    print('\nLexeme-cluster size distribution (across all folios):')
    size_counts = defaultdict(int)
    for f, cs in folio_clusters.items():
        for c in cs:
            size_counts[c['size']] += 1
    for s in sorted(size_counts):
        print(f'  size={s}: {size_counts[s]:5d} clusters')

    # Pre-registered key folios
    print('\nPre-registered key folios:')
    for f in ['f75r', 'f112r', 'f82v']:
        cs = folio_clusters.get(f, [])
        print(f'  {f}: max-cluster-size = {folio_max_lexeme_cluster_size(cs)}, '
              f'{len(cs)} clusters total (size>=2)')
        for c in cs:
            if c['size'] >= 3:
                print(f'    L{c["line_start"]}-L{c["line_end"]}: '
                      f'{c["lexeme"]} x {c["size"]}')

    # ----- Load Catalan anchors -----
    anchors_path = REPO_ROOT / 'phases' / 'PHASE_657_CYCLE_ANCHOR_ALIGNMENT' / 'results' / 'NUMERICAL_ANCHORS.json'
    anchors = json.loads(anchors_path.read_text(encoding='utf-8'))['in_set']

    primary, control = [], []
    for a in anchors:
        ch = chapter_id(a['subrecipe_id'])
        f = MATCHED_TABLE.get(ch)
        if f:
            a2 = dict(a)
            a2['matched_folio'] = f
            primary.append(a2)
        else:
            control.append(a)

    # ----- T1: matched-pair specificity -----
    print('\n=== T1: Matched-pair specificity (>= match rule) ===')
    primary_results = []
    observed_matches = 0
    for p in primary:
        n = p['count']
        f = p['matched_folio']
        cs = folio_clusters.get(f, [])
        match = folio_has_cluster_of_size_at_least(cs, n)
        # report the size of the largest cluster on this folio
        max_size = folio_max_lexeme_cluster_size(cs)
        # find the matching cluster lexemes if any
        match_clusters = [c for c in cs if c['size'] >= n]
        lex_str = ', '.join(f'{c["lexeme"]}x{c["size"]}@L{c["line_start"]}'
                            for c in match_clusters[:3])
        primary_results.append({
            'subrecipe_id': p['subrecipe_id'],
            'count': n,
            'matched_folio': f,
            'has_lexeme_cluster_size_ge_N': match,
            'matched_clusters': match_clusters,
            'folio_max_cluster_size': max_size,
        })
        if match:
            observed_matches += 1
        print(f'  {p["subrecipe_id"]:12s} N>={n:2d} -> {f:8s}  '
              f'max_size={max_size:2d}  '
              f'{"MATCH" if match else "no match"}  '
              f'{lex_str}')
    print(f'\n  Observed: {observed_matches}/{len(primary)}')

    # Null distribution
    rng = random.Random(20260426)
    by_chapter = {}
    for p in primary:
        by_chapter.setdefault(chapter_id(p['subrecipe_id']), []).append(p)

    n_perm = 10000
    null_counts = []
    all_folios = sorted(folio_clusters.keys())
    for trial in range(n_perm):
        used = set()
        ch_to_folio = {}
        chs = list(by_chapter.keys())
        rng.shuffle(chs)
        for ch in chs:
            pool = [f for f in all_folios if f not in used]
            if not pool:
                pool = all_folios
            f = rng.choice(pool)
            ch_to_folio[ch] = f
            used.add(f)
        m = 0
        for ch, items in by_chapter.items():
            f = ch_to_folio[ch]
            cs = folio_clusters.get(f, [])
            for it in items:
                if folio_has_cluster_of_size_at_least(cs, it['count']):
                    m += 1
        null_counts.append(m)

    p_value = sum(1 for x in null_counts if x >= observed_matches) / n_perm
    null_mean = sum(null_counts) / n_perm
    print(f'  Null mean: {null_mean:.3f}   p-value (>=observed): {p_value:.4f}')

    # ----- T2: triviality -----
    print('\n=== T2: Triviality check ===')
    n_folios = len(all_folios)
    test_counts = sorted({p['count'] for p in primary} |
                         {c['count'] for c in control})
    triviality = {}
    for n in test_counts:
        nf = sum(1 for f in all_folios
                 if folio_has_cluster_of_size_at_least(folio_clusters.get(f, []), n))
        pct = 100.0 * nf / n_folios
        triviality[n] = {'n_folios': nf, 'pct': pct, 'trivial': pct > 50}
        print(f'  N={n:2d}: {nf}/{n_folios} ({pct:.1f}%) '
              f'{"TRIVIAL" if pct > 50 else "specific"}')

    # ----- T3: f75r over-determination -----
    print('\n=== T3: f75r over-determination ===')
    f75r_cs = folio_clusters.get('f75r', [])
    f75r_max = folio_max_lexeme_cluster_size(f75r_cs)
    has_4 = any(c['size'] >= 4 for c in f75r_cs)
    has_9 = any(c['size'] >= 9 for c in f75r_cs)
    print(f'  f75r max lexeme cluster: {f75r_max}')
    print(f'  has cluster size>=4: {has_4}')
    print(f'  has cluster size>=9: {has_9}')

    # Folios with size>=4 cluster
    folios_ge_4 = [f for f in all_folios
                   if any(c['size'] >= 4 for c in folio_clusters.get(f, []))]
    folios_ge_9 = [f for f in all_folios
                   if any(c['size'] >= 9 for c in folio_clusters.get(f, []))]
    print(f'  folios with size>=4 cluster: {len(folios_ge_4)} total: {folios_ge_4[:10]}'
          f'{"..." if len(folios_ge_4)>10 else ""}')
    print(f'  folios with size>=9 cluster: {len(folios_ge_9)}: {folios_ge_9}')

    # Specifically: which folios have a qokedy x>=4 run?
    qokedy_x4_folios = []
    for f in all_folios:
        for c in folio_clusters.get(f, []):
            if c['lexeme'] == 'qokedy' and c['size'] >= 4:
                qokedy_x4_folios.append((f, c['size'], c['line_start']))
                break
    print(f'  folios with "qokedy" x >=4: {qokedy_x4_folios}')

    if not has_9 and len(folios_ge_9) == 0:
        ot_verdict = 'DEGENERATE (size>=9 cluster corpus-vacuous)'
    elif folios_ge_4 == ['f75r']:
        ot_verdict = 'CONFIRMED (f75r uniquely has size>=4 cluster)'
    elif 'f75r' in folios_ge_4 and len(folios_ge_4) > 1:
        ot_verdict = (
            f'PARTIAL (f75r has size>=4, but so do {len(folios_ge_4)-1} other folios)'
        )
    else:
        ot_verdict = 'NOT CONFIRMED'

    # ----- Verdict -----
    print('\n=== VERDICT ===')
    n_primary = len(primary)
    non_trivial_matches = sum(
        1 for r in primary_results
        if r['has_lexeme_cluster_size_ge_N']
        and not triviality[r['count']]['trivial']
    )
    non_trivial_total = sum(1 for p in primary
                            if not triviality[p['count']]['trivial'])

    print(f'  observed_matches: {observed_matches}/{n_primary}')
    print(f'  non-trivial matches: {non_trivial_matches}/{non_trivial_total}')
    print(f'  null p-value: {p_value:.4f}')

    if observed_matches == 0:
        verdict = 'FALSIFIED'
    elif non_trivial_total == 0:
        verdict = 'DEGENERATE (all counts trivial)'
    elif (non_trivial_matches / non_trivial_total >= 2/3) and p_value <= 0.05:
        verdict = 'SUPPORTED'
    elif (non_trivial_matches / non_trivial_total >= 1/3) and p_value <= 0.20:
        verdict = 'DIRECTIONAL'
    else:
        verdict = 'INCONCLUSIVE'

    print(f'  T1 verdict: {verdict}')
    print(f'  T3 verdict: {ot_verdict}')

    # ----- Persist -----
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / 'LEXEME_CLUSTERS.json').write_text(json.dumps({
        'phase': 658,
        'pre_registration_commit': 'f0f151e',
        'min_size': MIN_CLUSTER_SIZE,
        'folios': folio_clusters,
        'size_distribution': dict(size_counts),
    }, indent=2), encoding='utf-8')

    (out_dir / 'SPECIFICITY_TEST.json').write_text(json.dumps({
        'phase': 658,
        'pre_registration_commit': 'f0f151e',
        'T1': {
            'observed_matches': observed_matches,
            'n_primary': n_primary,
            'null_mean': null_mean,
            'null_p_value': p_value,
            'per_item': primary_results,
        },
        'T2': {
            'triviality': triviality,
        },
        'T3': {
            'verdict': ot_verdict,
            'f75r_max_cluster_size': f75r_max,
            'folios_with_size_ge_4': folios_ge_4,
            'folios_with_size_ge_9': folios_ge_9,
            'qokedy_x4_folios': qokedy_x4_folios,
        },
        'final_verdict': {
            'T1': verdict,
            'T3': ot_verdict,
        },
    }, indent=2), encoding='utf-8')

    print(f'\nWrote SPECIFICITY_TEST.json + LEXEME_CLUSTERS.json')

    # Return for direct inspection
    return {
        'verdict': verdict,
        'ot': ot_verdict,
        'observed': observed_matches,
        'p': p_value,
        'qokedy_x4_folios': qokedy_x4_folios,
        'primary_results': primary_results,
    }


if __name__ == '__main__':
    main()
