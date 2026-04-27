"""
Phase 659 s1 — Window-Density Specificity Test

Locked methodology per PRE_REGISTRATION.md (commit d1318ad).

Window: 2 consecutive lines, sliding stride 1.
Class: word.startswith('qok').
Match rule: matched folio has any 2-line window with >=N qok tokens.

Tests:
  T1: matched-pair specificity (4 primary items, 10k null permutation)
  T2: triviality check
  T3: f75r over-determination (Q1: unique with >=9 qok in 2-line window?)
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

WINDOW_SIZE = 2
QOK_PREFIX = 'qok'

MATCHED_TABLE = {
    'III.19': 'f75r',  'III.11': 'f112r', 'III.28': 'f82v',
    'II.18':  'f76r',  'II.14':  'f84r',  'III.12': 'f79r',
    'III.22': 'f82r',  'III.16': 'f103r', 'III.15': 'f76v',
    'III.27': 'f77v',  'III.18': 'f81v',  'III.1':  'f112v',
    'III.4':  'f116r', 'III.44': 'f107r',
}


def chapter_id(s):
    return '.'.join(s.split('.')[:2])


def folio_qok_per_line(folio_tokens):
    """Return dict {line_int: qok_count} for one folio."""
    counts = defaultdict(int)
    for t in folio_tokens:
        if t.word.startswith(QOK_PREFIX):
            try:
                ln = int(t.line)
            except (ValueError, TypeError):
                continue
            counts[ln] += 1
    return counts


def folio_max_window_qok(per_line, window=WINDOW_SIZE):
    """Max qok tokens in any sliding window of `window` consecutive lines."""
    if not per_line:
        return 0, []
    lines = sorted(per_line.keys())
    if not lines:
        return 0, []
    max_n = 0
    max_windows = []  # all windows that reach max_n
    # Use the actual line range (gaps allowed); only count window if lines are
    # CONSECUTIVE integers (line_start, line_start+1).
    for ln in lines:
        # Window = [ln, ln+1]
        n = per_line.get(ln, 0) + per_line.get(ln + 1, 0)
        if n > max_n:
            max_n = n
            max_windows = [(ln, ln + 1, n)]
        elif n == max_n and max_n > 0:
            max_windows.append((ln, ln + 1, n))
    return max_n, max_windows


def folio_has_window_ge(per_line, n, window=WINDOW_SIZE):
    max_n, _ = folio_max_window_qok(per_line, window)
    return max_n >= n


def main():
    out_dir = REPO_ROOT / 'phases' / 'PHASE_659_WINDOW_DENSITY_SPECIFICITY' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    print('Loading Currier B tokens...')
    tx = Transcript()
    by_folio = defaultdict(list)
    for tok in tx.currier_b():
        by_folio[tok.folio].append(tok)
    print(f'  {len(by_folio)} folios.')

    folio_per_line = {f: folio_qok_per_line(toks) for f, toks in by_folio.items()}
    folio_max = {f: folio_max_window_qok(pl) for f, pl in folio_per_line.items()}

    # Distribution of max-window-qok across folios
    print('\nMax 2-line window qok-count per folio (top 15):')
    ranked = sorted(folio_max.items(), key=lambda x: -x[1][0])[:15]
    for f, (mx, ws) in ranked:
        ws_str = ', '.join(f'L{a}-L{b}={c}' for a, b, c in ws[:3])
        print(f'  {f}: max={mx}  windows: {ws_str}')

    # Histogram of max values
    bins = defaultdict(int)
    for f, (mx, _) in folio_max.items():
        bins[mx] += 1
    print('\nHistogram of folio max-window-qok:')
    for k in sorted(bins.keys()):
        bar = '#' * bins[k]
        print(f'  {k:2d}: {bins[k]:3d} {bar}')

    # Coverage at thresholds
    print('\nFolio coverage at each N threshold (>=N in any 2-line window):')
    n_folios = len(folio_max)
    for n in range(2, max(bins.keys()) + 2):
        nf = sum(1 for _, (mx, _) in folio_max.items() if mx >= n)
        pct = 100.0 * nf / n_folios
        print(f'  N>={n:2d}: {nf}/{n_folios} ({pct:5.1f}%)')

    # ----- Catalan anchors -----
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
    print('\n=== T1: Matched-pair specificity (>= rule, 2-line window) ===')
    primary_results = []
    observed_matches = 0
    for p in primary:
        n = p['count']
        f = p['matched_folio']
        per_line = folio_per_line.get(f, {})
        match = folio_has_window_ge(per_line, n)
        max_n, windows = folio_max_window_qok(per_line)
        primary_results.append({
            'subrecipe_id': p['subrecipe_id'],
            'count': n,
            'matched_folio': f,
            'folio_max_window_qok': max_n,
            'matching_windows': [(a, b, c) for (a, b, c) in windows[:5]],
            'match': match,
        })
        if match:
            observed_matches += 1
        ws_str = ', '.join(f'L{a}-L{b}={c}' for a, b, c in windows[:3])
        print(f'  {p["subrecipe_id"]:12s} N>={n:2d} -> {f:8s}  '
              f'max={max_n:2d}  '
              f'{"MATCH" if match else "no match"}  {ws_str}')
    print(f'\n  Observed: {observed_matches}/{len(primary)}')

    # Null
    rng = random.Random(20260426)
    by_chapter = {}
    for p in primary:
        by_chapter.setdefault(chapter_id(p['subrecipe_id']), []).append(p)

    n_perm = 10000
    null_counts = []
    all_folios = sorted(folio_per_line.keys())
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
            pl = folio_per_line.get(f, {})
            for it in items:
                if folio_has_window_ge(pl, it['count']):
                    m += 1
        null_counts.append(m)
    p_value = sum(1 for x in null_counts if x >= observed_matches) / n_perm
    null_mean = sum(null_counts) / n_perm
    print(f'  Null mean: {null_mean:.3f}, p-value: {p_value:.4f}')
    null_hist = {i: 0 for i in range(len(primary) + 1)}
    for x in null_counts:
        null_hist[x] = null_hist.get(x, 0) + 1
    print(f'  Null hist:')
    for k in sorted(null_hist):
        print(f'    {k}: {null_hist[k]:5d}')

    # ----- T2: triviality -----
    print('\n=== T2: Triviality ===')
    test_counts = sorted({p['count'] for p in primary} | {c['count'] for c in control})
    triviality = {}
    for n in test_counts:
        nf = sum(1 for f in all_folios if folio_has_window_ge(folio_per_line[f], n))
        pct = 100.0 * nf / n_folios
        triviality[n] = {'n_folios': nf, 'pct': pct, 'trivial': pct > 50}
        print(f'  N={n:2d}: {nf}/{n_folios} ({pct:5.1f}%) '
              f'{"TRIVIAL" if pct > 50 else "specific"}')

    # ----- T3: f75r over-determination -----
    print('\n=== T3: f75r over-determination ===')
    # Q1: f75r unique with >=9 in 2-line window?
    f75r_max = folio_max['f75r'][0]
    f75r_windows = folio_max['f75r'][1]
    print(f'  f75r max 2-line qok-window: {f75r_max}')
    print(f'  f75r window detail: {f75r_windows}')

    folios_ge_9 = [f for f, (mx, _) in folio_max.items() if mx >= 9]
    folios_ge_8 = [f for f, (mx, _) in folio_max.items() if mx >= 8]
    folios_ge_7 = [f for f, (mx, _) in folio_max.items() if mx >= 7]
    folios_ge_4 = [f for f, (mx, _) in folio_max.items() if mx >= 4]

    print(f'  Folios with max>=4: {len(folios_ge_4)} / {n_folios}')
    print(f'  Folios with max>=7: {len(folios_ge_7)}: {folios_ge_7}')
    print(f'  Folios with max>=8: {len(folios_ge_8)}: {folios_ge_8}')
    print(f'  Folios with max>=9: {len(folios_ge_9)}: {folios_ge_9}')

    if folios_ge_9 == ['f75r']:
        ot_q1 = 'CONFIRMED: f75r uniquely has >=9 qok-class tokens in some 2-line window'
    elif 'f75r' in folios_ge_9 and len(folios_ge_9) > 1:
        ot_q1 = (f'PARTIAL: f75r reaches >=9 but so do {len(folios_ge_9)-1} other folios: '
                 f'{[f for f in folios_ge_9 if f != "f75r"]}')
    elif 'f75r' not in folios_ge_9:
        ot_q1 = (f'NOT CONFIRMED: f75r max ({f75r_max}) is below threshold; '
                 f'reaching folios: {folios_ge_9}')
    else:
        ot_q1 = 'UNKNOWN'

    # ----- Verdict -----
    print('\n=== VERDICT ===')
    n_primary = len(primary)
    non_trivial_matches = sum(
        1 for r in primary_results
        if r['match'] and not triviality[r['count']]['trivial']
    )
    non_trivial_total = sum(
        1 for p in primary if not triviality[p['count']]['trivial']
    )

    if observed_matches == 0:
        t1 = 'FALSIFIED'
    elif non_trivial_total == 0:
        t1 = 'DEGENERATE (all counts trivial)'
    elif (non_trivial_matches / non_trivial_total >= 2/3) and p_value <= 0.05:
        t1 = 'SUPPORTED'
    elif (non_trivial_matches / non_trivial_total >= 1/3) and p_value <= 0.20:
        t1 = 'DIRECTIONAL'
    else:
        t1 = 'INCONCLUSIVE'

    if 'CONFIRMED' in ot_q1 and 'NOT' not in ot_q1 and 'PARTIAL' not in ot_q1:
        x9_verdict = 'SUPPORTED (categorical specificity)'
    elif 'PARTIAL' in ot_q1:
        x9_verdict = 'DIRECTIONAL'
    else:
        x9_verdict = 'INCONCLUSIVE or NOT CONFIRMED'

    print(f'  T1 (matched-pair, all anchors): {t1}')
    print(f'  T3-Q1 (f75r x9 over-det):       {ot_q1}')
    print(f'  Phase verdict on x9 anchor:     {x9_verdict}')

    out = {
        'phase': 659,
        'pre_registration_commit': 'd1318ad',
        'window_size': WINDOW_SIZE,
        'class_prefix': QOK_PREFIX,
        'folio_max_window_qok': {f: {'max': mx, 'windows': ws} for f, (mx, ws) in folio_max.items()},
        'T1': {
            'observed_matches': observed_matches,
            'n_primary': n_primary,
            'null_mean': null_mean,
            'null_p_value': p_value,
            'null_hist': null_hist,
            'per_item': primary_results,
        },
        'T2': triviality,
        'T3': {
            'f75r_max_window': f75r_max,
            'f75r_windows': f75r_windows,
            'folios_ge_4': folios_ge_4,
            'folios_ge_7': folios_ge_7,
            'folios_ge_8': folios_ge_8,
            'folios_ge_9': folios_ge_9,
            'Q1_verdict': ot_q1,
        },
        'final_verdict': {
            'T1_all_anchors': t1,
            'x9_anchor_specifically': x9_verdict,
        },
    }
    (out_dir / 'WINDOW_DENSITY_TEST.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'\nWrote results.')


if __name__ == '__main__':
    main()
