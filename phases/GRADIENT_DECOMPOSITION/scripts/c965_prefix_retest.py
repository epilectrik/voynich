"""
Phase 451 follow-up: Faithful PREFIX-based retest of C965 (body kernel composition shift).

C965 found h_fraction rises (+0.10, p=0.0004) and e_fraction falls (-0.086, p=0.002)
through paragraph body, using PREFIX-based kernel classification.

Phase 451 T4 accidentally used MIDDLE-character-based classification (different variable).
This script uses the EXACT C965 methodology, then decomposes by suffix mode.

Methodology (matching C965 original):
- Kernel class from PREFIX: k in prefix -> k-kernel, ch/sh in prefix -> h-kernel, else -> e-kernel
- Paragraphs with 5+ lines, header excluded
- Partial Spearman rho controlling for line length via OLS residualization
- 1000-permutation shuffle test, Bonferroni alpha = 0.002
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import numpy as np
from scipy import stats
from collections import defaultdict
from scripts.voynich import Transcript, Morphology

# ── Configuration ──
MIN_PARA_LINES = 5
N_PERMS = 1000
SEED = 42
BONFERRONI_ALPHA = 0.01 / 5  # 0.002, matching C965

# ── Suffix mode centroids (C1231) ──
MODE_A_CENTROID = np.array([0.349, 0.088, 0.014, 0.044])
MODE_B_CENTROID = np.array([0.128, 0.031, 0.006, 0.265])
SUFFIX_CATS = {
    'y': 'terminal', 'dy': 'terminal', 'ty': 'terminal', 'ry': 'terminal',
    'ly': 'terminal', 'ky': 'terminal', 'my': 'terminal', 'ny': 'terminal',
    'ey': 'connector', 'edy': 'connector', 'eey': 'connector',
    'oly': 'connector', 'aly': 'connector', 'ary': 'connector',
    'aiy': 'connector', 'oiy': 'connector',
    'am': 'iterate', 'aim': 'iterate', 'al': 'iterate',
    'ol': 'iterate', 'or': 'iterate', 'ar': 'iterate',
}

def classify_suffix_mode(tokens, morph):
    """Assign Mode A or Mode B to a line based on suffix profile (C1231)."""
    counts = {'terminal': 0, 'connector': 0, 'iterate': 0, 'bare': 0}
    n = 0
    for t in tokens:
        w = t['word'] if isinstance(t, dict) else t.word
        if not w.strip() or '*' in w:
            continue
        m = morph.extract(w)
        if m.suffix and m.suffix in SUFFIX_CATS:
            counts[SUFFIX_CATS[m.suffix]] += 1
        elif m.suffix:
            counts['terminal'] += 1
        else:
            counts['bare'] += 1
        n += 1
    if n < 3:
        return None
    vec = np.array([counts['terminal']/n, counts['connector']/n,
                    counts['iterate']/n, counts['bare']/n])
    da = np.linalg.norm(vec - MODE_A_CENTROID)
    db = np.linalg.norm(vec - MODE_B_CENTROID)
    return 'A' if da < db else 'B'

def classify_kernel(prefix):
    """Classify kernel type from PREFIX string (C965 method)."""
    if prefix is None:
        return None
    if 'k' in prefix:
        return 'k'
    if 'ch' in prefix or 'sh' in prefix:
        return 'h'
    return 'e'

def partial_spearman(x, y, covariate):
    """Partial Spearman rho: residualize both x and y against covariate via OLS."""
    A = np.column_stack([covariate, np.ones(len(covariate))])
    # Residualize x
    coef_x, _, _, _ = np.linalg.lstsq(A, x, rcond=None)
    resid_x = x - A @ coef_x
    # Residualize y
    coef_y, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    resid_y = y - A @ coef_y
    rho, p = stats.spearmanr(resid_x, resid_y)
    return rho, p

def main():
    tx = Transcript()
    morph = Morphology()

    # ── Build paragraphs ──
    tokens_b = list(tx.currier_b())

    # Group by folio, then by line
    folio_lines = defaultdict(lambda: defaultdict(list))
    for t in tokens_b:
        folio_lines[t.folio][t.line].append(t)

    # Build paragraphs using par_initial
    paragraphs = []
    for folio in sorted(folio_lines.keys()):
        lines_sorted = sorted(folio_lines[folio].keys())
        current_para = []
        for line_num in lines_sorted:
            line_tokens = folio_lines[folio][line_num]
            is_par_initial = any(
                hasattr(t, 'par_initial') and t.par_initial for t in line_tokens
            )
            if is_par_initial and current_para:
                paragraphs.append(current_para)
                current_para = []
            current_para.append({
                'folio': folio,
                'line': line_num,
                'tokens': line_tokens
            })
        if current_para:
            paragraphs.append(current_para)

    # Filter to MIN_PARA_LINES
    paragraphs = [p for p in paragraphs if len(p) >= MIN_PARA_LINES]
    print(f"Paragraphs with {MIN_PARA_LINES}+ lines: {len(paragraphs)}")

    # ── Classify each line ──
    records = []  # Each: {pos, h_frac, e_frac, k_frac, n_class, line_len, mode}

    for para in paragraphs:
        body = para[1:]  # Skip header
        n_body = len(body)
        if n_body < 2:
            continue

        # Classify paragraph lines for suffix mode
        line_modes = []
        for line_info in body:
            toks_for_mode = [{'word': t.word} for t in line_info['tokens']
                           if t.word.strip() and '*' not in t.word]
            mode = classify_suffix_mode(toks_for_mode, morph)
            line_modes.append(mode)

        for i, line_info in enumerate(body):
            norm_pos = i / (n_body - 1)

            # Classify kernels
            kernels = []
            for t in line_info['tokens']:
                w = t.word
                if not w.strip() or '*' in w:
                    continue
                m = morph.extract(w)
                # Need prefix or non-empty middle
                if m.prefix:
                    k = classify_kernel(m.prefix)
                    kernels.append(k)
                elif m.middle and m.middle.strip():
                    kernels.append('e')  # No prefix, has middle -> e-kernel

            if len(kernels) == 0:
                continue

            n_class = len(kernels)
            h_count = kernels.count('h')
            e_count = kernels.count('e')
            k_count = kernels.count('k')

            records.append({
                'pos': norm_pos,
                'h_frac': h_count / n_class,
                'e_frac': e_count / n_class,
                'k_frac': k_count / n_class,
                'n_class': n_class,
                'line_len': n_class,
                'mode': line_modes[i],
                'n_distinct': len(set(kernels)),
            })

    print(f"Total body lines analyzed: {len(records)}")

    # Convert to arrays
    all_pos = np.array([r['pos'] for r in records])
    all_h = np.array([r['h_frac'] for r in records])
    all_e = np.array([r['e_frac'] for r in records])
    all_k = np.array([r['k_frac'] for r in records])
    all_len = np.array([r['line_len'] for r in records])
    all_modes = [r['mode'] for r in records]

    # ── Quintile means (aggregate) ──
    quintiles_agg = {q: {'h': [], 'e': [], 'k': []} for q in range(5)}
    for r in records:
        q = min(int(r['pos'] * 5), 4)
        quintiles_agg[q]['h'].append(r['h_frac'])
        quintiles_agg[q]['e'].append(r['e_frac'])
        quintiles_agg[q]['k'].append(r['k_frac'])

    print("\n-- Aggregate quintile means (PREFIX-based kernel) --")
    print(f"{'Q':>3} {'n':>5} {'h_frac':>8} {'e_frac':>8} {'k_frac':>8}")
    for q in range(5):
        n = len(quintiles_agg[q]['h'])
        h_m = np.mean(quintiles_agg[q]['h']) if n > 0 else 0
        e_m = np.mean(quintiles_agg[q]['e']) if n > 0 else 0
        k_m = np.mean(quintiles_agg[q]['k']) if n > 0 else 0
        print(f"{q:>3} {n:>5} {h_m:>8.4f} {e_m:>8.4f} {k_m:>8.4f}")

    # ── Partial Spearman (aggregate) ──
    h_rho, h_p = partial_spearman(all_pos, all_h, all_len)
    e_rho, e_p = partial_spearman(all_pos, all_e, all_len)
    k_rho, k_p = partial_spearman(all_pos, all_k, all_len)

    print(f"\n-- Aggregate partial Spearman (controlling line length) --")
    print(f"  h_fraction: rho={h_rho:+.4f}, p={h_p:.6f} {'***' if h_p < BONFERRONI_ALPHA else ''}")
    print(f"  e_fraction: rho={e_rho:+.4f}, p={e_p:.6f} {'***' if e_p < BONFERRONI_ALPHA else ''}")
    print(f"  k_fraction: rho={k_rho:+.4f}, p={k_p:.6f} {'***' if k_p < BONFERRONI_ALPHA else ''}")
    print(f"  C965 reference: h=+0.1005, e=-0.0863, k=-0.0027")

    # ── Shuffle test (aggregate) ──
    rng = np.random.RandomState(SEED)
    h_null = np.zeros(N_PERMS)
    e_null = np.zeros(N_PERMS)
    k_null = np.zeros(N_PERMS)

    for perm in range(N_PERMS):
        shuffled_pos = rng.permutation(all_pos)
        h_null[perm], _ = partial_spearman(shuffled_pos, all_h, all_len)
        e_null[perm], _ = partial_spearman(shuffled_pos, all_e, all_len)
        k_null[perm], _ = partial_spearman(shuffled_pos, all_k, all_len)

    h_perm_p = np.mean(np.abs(h_null) >= np.abs(h_rho))
    e_perm_p = np.mean(np.abs(e_null) >= np.abs(e_rho))
    k_perm_p = np.mean(np.abs(k_null) >= np.abs(k_rho))

    print(f"\n-- Shuffle test (1000 perms) --")
    print(f"  h_fraction: perm_p={h_perm_p:.3f}")
    print(f"  e_fraction: perm_p={e_perm_p:.3f}")
    print(f"  k_fraction: perm_p={k_perm_p:.3f}")

    # ── Mode decomposition ──
    mode_results = {}
    for mode_label in ['A', 'B']:
        idx = [i for i, m in enumerate(all_modes) if m == mode_label]
        if len(idx) < 20:
            mode_results[mode_label] = {'n': len(idx), 'insufficient': True}
            continue

        m_pos = all_pos[idx]
        m_h = all_h[idx]
        m_e = all_e[idx]
        m_k = all_k[idx]
        m_len = all_len[idx]

        mh_rho, mh_p = partial_spearman(m_pos, m_h, m_len)
        me_rho, me_p = partial_spearman(m_pos, m_e, m_len)
        mk_rho, mk_p = partial_spearman(m_pos, m_k, m_len)

        # Quintile means per mode
        q_means = {q: {'h': [], 'e': [], 'k': []} for q in range(5)}
        for i_idx in idx:
            q = min(int(all_pos[i_idx] * 5), 4)
            q_means[q]['h'].append(all_h[i_idx])
            q_means[q]['e'].append(all_e[i_idx])
            q_means[q]['k'].append(all_k[i_idx])

        mode_results[mode_label] = {
            'n': len(idx),
            'h_rho': round(mh_rho, 4), 'h_p': round(mh_p, 6),
            'e_rho': round(me_rho, 4), 'e_p': round(me_p, 6),
            'k_rho': round(mk_rho, 4), 'k_p': round(mk_p, 6),
            'quintile_h': [round(np.mean(q_means[q]['h']), 4) if q_means[q]['h'] else None for q in range(5)],
            'quintile_e': [round(np.mean(q_means[q]['e']), 4) if q_means[q]['e'] else None for q in range(5)],
            'quintile_k': [round(np.mean(q_means[q]['k']), 4) if q_means[q]['k'] else None for q in range(5)],
            'quintile_n': [len(q_means[q]['h']) for q in range(5)],
        }

        print(f"\n-- Mode {mode_label} (n={len(idx)}) partial Spearman --")
        print(f"  h_fraction: rho={mh_rho:+.4f}, p={mh_p:.6f} {'***' if mh_p < BONFERRONI_ALPHA else ''}")
        print(f"  e_fraction: rho={me_rho:+.4f}, p={me_p:.6f} {'***' if me_p < BONFERRONI_ALPHA else ''}")
        print(f"  k_fraction: rho={mk_rho:+.4f}, p={mk_p:.6f} {'***' if mk_p < BONFERRONI_ALPHA else ''}")

        print(f"  Quintile h: {mode_results[mode_label]['quintile_h']}")
        print(f"  Quintile e: {mode_results[mode_label]['quintile_e']}")

    # ── Unclassified lines ──
    n_unclass = sum(1 for m in all_modes if m is None)
    print(f"\n-- Unclassified lines (< 3 tokens): {n_unclass} --")

    # ── Verdict ──
    h_replicates = (h_p < BONFERRONI_ALPHA and h_rho > 0)
    e_replicates = (e_p < BONFERRONI_ALPHA and e_rho < 0)

    if h_replicates and e_replicates:
        agg_verdict = "REPLICATES"
    elif h_replicates or e_replicates:
        agg_verdict = "PARTIAL_REPLICATION"
    else:
        agg_verdict = "DOES_NOT_REPLICATE"

    # Mode B decomposition verdict
    if 'B' in mode_results and not mode_results['B'].get('insufficient'):
        mb = mode_results['B']
        mb_h_sig = mb['h_p'] < BONFERRONI_ALPHA and mb['h_rho'] > 0
        mb_e_sig = mb['e_p'] < BONFERRONI_ALPHA and mb['e_rho'] < 0
        if mb_h_sig and mb_e_sig:
            mode_verdict = "GENUINE"
        elif mb_h_sig or mb_e_sig:
            mode_verdict = "PARTIAL"
        else:
            mode_verdict = "NOT_IN_MODE_B"
    else:
        mode_verdict = "INSUFFICIENT_DATA"

    print(f"\n== VERDICT ==")
    print(f"  Aggregate replication: {agg_verdict}")
    print(f"  C965 h=+0.10 -> this test h={h_rho:+.4f}")
    print(f"  C965 e=-0.09 -> this test e={e_rho:+.4f}")
    print(f"  Mode B decomposition: {mode_verdict}")

    # ── Save results ──
    results = {
        'phase': 'Phase 451 follow-up: C965 PREFIX-based retest',
        'aggregate': {
            'n_paragraphs': len(paragraphs),
            'n_body_lines': len(records),
            'h_rho': round(h_rho, 4), 'h_p': round(h_p, 6),
            'e_rho': round(e_rho, 4), 'e_p': round(e_p, 6),
            'k_rho': round(k_rho, 4), 'k_p': round(k_p, 6),
            'h_perm_p': round(h_perm_p, 3),
            'e_perm_p': round(e_perm_p, 3),
            'k_perm_p': round(k_perm_p, 3),
            'quintile_h': [round(np.mean(quintiles_agg[q]['h']), 4) for q in range(5)],
            'quintile_e': [round(np.mean(quintiles_agg[q]['e']), 4) for q in range(5)],
            'quintile_k': [round(np.mean(quintiles_agg[q]['k']), 4) for q in range(5)],
            'quintile_n': [len(quintiles_agg[q]['h']) for q in range(5)],
            'verdict': agg_verdict,
        },
        'c965_reference': {
            'h_rho': 0.1005, 'h_p': 0.000352,
            'e_rho': -0.0863, 'e_p': 0.002164,
            'k_rho': -0.0027, 'k_p': 0.923,
            'n_paragraphs': 187, 'n_body_lines': 1261,
        },
        'mode_b': mode_results.get('B', {}),
        'mode_a': mode_results.get('A', {}),
        'mode_verdict': mode_verdict,
        'n_unclassified': n_unclass,
    }

    out_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'c965_prefix_retest.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_path}")

if __name__ == '__main__':
    main()
