"""
Phase 451 Follow-up: MODE B STATE TRACKING

Does any state variable propagate sequentially through the Mode B track?

For consecutive B->B line pairs within paragraphs:
  S1: FL state propagation (end FL of B-line-N -> start FL of B-line-N+1)
  S2: Energy balance evolution (k-frac, e-frac, k/e ratio)
  S3: qo engagement (qo-prefix fraction)
  S4: Suffix terminal fraction (loop closure intensity)
  S5: Ordinal progression (does B-track position predict any state monotonically?)

Control: folio-shuffled permutation (break sequential order, preserve folio identity)

References: C1031, C1258, C777
"""

import sys, json
import numpy as np
from collections import defaultdict
from pathlib import Path
from scipy.stats import spearmanr, pearsonr

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RNG = np.random.RandomState(42)
N_PERM = 1000

TERMINAL_SUFFIXES = {'edy', 'dy', 'eey', 'ey', 'y', 'hy', 'iry', 'oly',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}
MODE_A_CENTROID = np.array([0.430, 0.019, 0.086, 0.466])
MODE_B_CENTROID = np.array([0.155, 0.031, 0.072, 0.741])

FL_MIDDLES = {
    'ii': 'INITIAL', 'i': 'INITIAL',
    'in': 'EARLY',
    'r': 'MEDIAL', 'ar': 'MEDIAL',
    'al': 'LATE', 'l': 'LATE', 'ol': 'LATE',
    'o': 'FINAL', 'ly': 'FINAL', 'am': 'FINAL',
    'm': 'TERMINAL', 'dy': 'TERMINAL', 'ry': 'TERMINAL', 'y': 'TERMINAL',
}
FL_RANK = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}


def classify_suffix_mode(line_toks):
    if len(line_toks) < 3:
        return None
    n = len(line_toks)
    cats = [0, 0, 0, 0]
    for tok in line_toks:
        sfx = tok['suffix']
        if sfx in TERMINAL_SUFFIXES:
            cats[0] += 1
        elif sfx in CONNECTOR_SUFFIXES:
            cats[1] += 1
        elif sfx in ITERATE_SUFFIXES:
            cats[2] += 1
        else:
            cats[3] += 1
    vec = np.array(cats, dtype=float) / n
    dist_a = np.linalg.norm(vec - MODE_A_CENTROID)
    dist_b = np.linalg.norm(vec - MODE_B_CENTROID)
    return 'A' if dist_a < dist_b else 'B'


def load_data():
    tx = Transcript()
    morph = Morphology()
    tokens = []
    for t in tx.currier_b():
        if t.placement.startswith('L') or '*' in t.word or not t.word.strip():
            continue
        m = morph.extract(t.word)
        tokens.append({
            'folio': t.folio, 'line': t.line, 'word': t.word,
            'middle': m.middle if m else '', 'suffix': m.suffix if m else '',
            'prefix': m.prefix if m else '',
            'par_initial': t.par_initial,
            'kernels': [c for c in 'khe' if c in (m.middle if m else '')],
        })

    folio_tokens = defaultdict(list)
    for tok in tokens:
        folio_tokens[tok['folio']].append(tok)

    folios = {}
    for folio, ftoks in folio_tokens.items():
        ftoks.sort(key=lambda t: t['line'])
        lines_dict = defaultdict(list)
        for tok in ftoks:
            lines_dict[tok['line']].append(tok)
        line_nums = sorted(lines_dict.keys())
        paragraphs = []
        current_para = []
        for ln in line_nums:
            line_toks = lines_dict[ln]
            if line_toks[0]['par_initial'] and current_para:
                paragraphs.append(current_para)
                current_para = []
            current_para.append((ln, line_toks))
        if current_para:
            paragraphs.append(current_para)
        folios[folio] = paragraphs
    return folios


def extract_line_state(toks):
    """Extract state variables from a line's tokens."""
    n = len(toks)
    if n == 0:
        return None

    # Kernel fractions
    k_count = sum(1 for t in toks if 'k' in t['kernels'])
    e_count = sum(1 for t in toks if 'e' in t['kernels'])
    h_count = sum(1 for t in toks if 'h' in t['kernels'])
    k_frac = k_count / n
    e_frac = e_count / n
    ke_ratio = k_count / max(e_count, 1)  # k/e ratio (avoid div0)

    # qo engagement
    qo_frac = sum(1 for t in toks if t['prefix'] == 'qo') / n

    # Suffix terminal fraction
    terminal_frac = sum(1 for t in toks if t['suffix'] in TERMINAL_SUFFIXES) / n
    bare_frac = sum(1 for t in toks if not t['suffix']) / n

    # FL: first and last FL stage in the line
    first_fl = None
    last_fl = None
    fl_stages = []
    for t in toks:
        stage = FL_MIDDLES.get(t['middle'])
        if stage:
            if first_fl is None:
                first_fl = stage
            last_fl = stage
            fl_stages.append(FL_RANK[stage])

    first_fl_rank = FL_RANK.get(first_fl, -1) if first_fl else -1
    last_fl_rank = FL_RANK.get(last_fl, -1) if last_fl else -1
    mean_fl = np.mean(fl_stages) if fl_stages else -1

    return {
        'k_frac': k_frac,
        'e_frac': e_frac,
        'ke_ratio': ke_ratio,
        'qo_frac': qo_frac,
        'terminal_frac': terminal_frac,
        'bare_frac': bare_frac,
        'first_fl_rank': first_fl_rank,
        'last_fl_rank': last_fl_rank,
        'mean_fl': mean_fl,
        'n_toks': n,
    }


def extract_bb_pairs(folios, min_body=4):
    """Extract consecutive B->B line pairs within paragraphs."""
    pairs = []
    para_bb_sequences = []  # for ordinal progression test

    for folio, paragraphs in folios.items():
        for para in paragraphs:
            if len(para) < 2:
                continue
            body_lines = para[1:]
            if len(body_lines) < min_body:
                continue

            # Annotate with mode and state
            annotated = []
            for ln, toks in body_lines:
                mode = classify_suffix_mode(toks)
                state = extract_line_state(toks)
                if mode and state:
                    annotated.append({'mode': mode, 'state': state, 'folio': folio})

            # Extract B-track subsequence
            b_lines = [a for a in annotated if a['mode'] == 'B']
            if len(b_lines) >= 2:
                para_bb_sequences.append(b_lines)
                for i in range(len(b_lines) - 1):
                    pairs.append((b_lines[i], b_lines[i + 1]))

    return pairs, para_bb_sequences


def s1_fl_propagation(pairs):
    """S1: Does end FL of B-line-N predict start FL of B-line-N+1?"""
    print("\nS1: FL State Propagation (B-track)")
    print("-" * 60)

    # Filter to pairs where both have valid FL
    valid = [(a, b) for a, b in pairs
             if a['state']['last_fl_rank'] >= 0 and b['state']['first_fl_rank'] >= 0]

    if len(valid) < 20:
        print("  SKIP: too few valid pairs")
        return {'verdict': 'SKIP'}

    x = np.array([a['state']['last_fl_rank'] for a, b in valid])
    y = np.array([b['state']['first_fl_rank'] for a, b in valid])

    rho, p = spearmanr(x, y)

    # Also: mean FL propagation
    mean_x = np.mean(x)
    mean_y = np.mean(y)

    # Forward vs reset
    n_forward = sum(1 for xi, yi in zip(x, y) if yi >= xi)
    n_reset = sum(1 for xi, yi in zip(x, y) if yi < xi)

    # Permutation: shuffle y values
    perm_rhos = []
    for _ in range(N_PERM):
        perm_y = RNG.permutation(y)
        pr, _ = spearmanr(x, perm_y)
        perm_rhos.append(abs(pr))
    perm_p = np.mean([pr >= abs(rho) for pr in perm_rhos])

    print(f"  End FL (line N) -> Start FL (line N+1)")
    print(f"  Spearman rho: {rho:.4f} (parametric p={p:.6f}, perm p={perm_p:.4f})")
    print(f"  Mean end FL rank: {mean_x:.2f}, Mean start FL rank: {mean_y:.2f}")
    print(f"  Forward: {n_forward}/{len(valid)} ({100*n_forward/len(valid):.1f}%), Reset: {n_reset}/{len(valid)} ({100*n_reset/len(valid):.1f}%)")
    print(f"  n={len(valid)} B->B pairs")

    sig = perm_p < 0.01
    print(f"  {'SIGNAL' if sig else 'NULL'}")

    return {
        'test': 'S1_fl_propagation',
        'rho': round(float(rho), 4),
        'parametric_p': round(float(p), 6),
        'perm_p': round(float(perm_p), 4),
        'mean_end_fl': round(float(mean_x), 3),
        'mean_start_fl': round(float(mean_y), 3),
        'n_forward': int(n_forward),
        'n_reset': int(n_reset),
        'n_pairs': len(valid),
        'signal': bool(sig),
    }


def s2_energy_balance(pairs):
    """S2: Does energy state (k, e, k/e) propagate through B track?"""
    print("\nS2: Energy Balance Propagation (B-track)")
    print("-" * 60)

    results = {}
    for var_name in ['k_frac', 'e_frac', 'ke_ratio', 'qo_frac']:
        x = np.array([a['state'][var_name] for a, b in pairs])
        y = np.array([b['state'][var_name] for a, b in pairs])

        if np.std(x) < 1e-10 or np.std(y) < 1e-10:
            results[var_name] = {'rho': 0.0, 'perm_p': 1.0, 'signal': False}
            continue

        rho, p = pearsonr(x, y)

        # Permutation
        perm_rhos = []
        for _ in range(N_PERM):
            perm_y = RNG.permutation(y)
            if np.std(perm_y) > 1e-10:
                pr, _ = pearsonr(x, perm_y)
                perm_rhos.append(abs(pr))
            else:
                perm_rhos.append(0.0)
        perm_p = np.mean([pr >= abs(rho) for pr in perm_rhos])

        sig = perm_p < 0.01
        results[var_name] = {
            'rho': round(float(rho), 4),
            'perm_p': round(float(perm_p), 4),
            'mean_N': round(float(np.mean(x)), 4),
            'mean_N1': round(float(np.mean(y)), 4),
            'signal': bool(sig),
        }
        print(f"  {var_name}: rho={rho:.4f} (perm p={perm_p:.4f}) {'SIGNAL' if sig else 'null'}")

    return {
        'test': 'S2_energy_balance',
        'variables': results,
        'n_pairs': len(pairs),
    }


def s3_suffix_state(pairs):
    """S3: Does suffix composition propagate through B track?"""
    print("\nS3: Suffix State Propagation (B-track)")
    print("-" * 60)

    results = {}
    for var_name in ['terminal_frac', 'bare_frac']:
        x = np.array([a['state'][var_name] for a, b in pairs])
        y = np.array([b['state'][var_name] for a, b in pairs])

        if np.std(x) < 1e-10 or np.std(y) < 1e-10:
            results[var_name] = {'rho': 0.0, 'perm_p': 1.0, 'signal': False}
            continue

        rho, p = pearsonr(x, y)

        perm_rhos = []
        for _ in range(N_PERM):
            perm_y = RNG.permutation(y)
            if np.std(perm_y) > 1e-10:
                pr, _ = pearsonr(x, perm_y)
                perm_rhos.append(abs(pr))
            else:
                perm_rhos.append(0.0)
        perm_p = np.mean([pr >= abs(rho) for pr in perm_rhos])

        sig = perm_p < 0.01
        results[var_name] = {
            'rho': round(float(rho), 4),
            'perm_p': round(float(perm_p), 4),
            'signal': bool(sig),
        }
        print(f"  {var_name}: rho={rho:.4f} (perm p={perm_p:.4f}) {'SIGNAL' if sig else 'null'}")

    return {
        'test': 'S3_suffix_state',
        'variables': results,
        'n_pairs': len(pairs),
    }


def s4_ordinal_progression(bb_sequences):
    """S4: Does B-track position predict any state variable monotonically?

    For each paragraph, assign B-lines ordinal position (0, 1, 2, ...)
    within the B subsequence. Test Spearman rho of state vs ordinal position.
    """
    print("\nS4: Ordinal Progression Within B-Track")
    print("-" * 60)

    # Collect (normalized B-track position, state) across all paragraphs
    positions = []
    states = {v: [] for v in ['k_frac', 'e_frac', 'ke_ratio', 'qo_frac',
                               'terminal_frac', 'bare_frac', 'mean_fl', 'n_toks']}

    for b_lines in bb_sequences:
        n = len(b_lines)
        if n < 3:
            continue
        for i, bl in enumerate(b_lines):
            norm_pos = i / (n - 1)
            positions.append(norm_pos)
            for var in states:
                val = bl['state'].get(var, 0)
                if val == -1:  # FL missing
                    val = np.nan
                states[var].append(val)

    if len(positions) < 30:
        print("  SKIP: too few B-track lines")
        return {'verdict': 'SKIP'}

    positions = np.array(positions)
    results = {}
    for var in states:
        vals = np.array(states[var])
        mask = ~np.isnan(vals)
        if np.sum(mask) < 30:
            results[var] = {'rho': 0.0, 'p': 1.0, 'signal': False}
            continue

        rho, p = spearmanr(positions[mask], vals[mask])
        sig = abs(rho) > 0.05 and p < 0.005
        results[var] = {
            'rho': round(float(rho), 4),
            'p': round(float(p), 6),
            'signal': bool(sig),
        }
        marker = 'SIGNAL' if sig else 'null'
        print(f"  {var}: rho={rho:.4f} (p={p:.6f}) {marker}")

    return {
        'test': 'S4_ordinal_progression',
        'variables': results,
        'n_lines': len(positions),
        'n_sequences': len([s for s in bb_sequences if len(s) >= 3]),
    }


def s5_lag_autocorrelation(bb_sequences):
    """S5: Lag-1 autocorrelation of state variables within B-track.

    For each state variable, compute the lag-1 autocorrelation across
    all B-track subsequences. Compare to shuffled-within-paragraph null.
    """
    print("\nS5: Lag-1 Autocorrelation Within B-Track")
    print("-" * 60)

    var_names = ['k_frac', 'e_frac', 'ke_ratio', 'qo_frac',
                 'terminal_frac', 'bare_frac', 'mean_fl']

    # Build lag-1 pairs from all sequences
    lag_pairs = {v: [] for v in var_names}
    for b_lines in bb_sequences:
        if len(b_lines) < 3:
            continue
        for i in range(len(b_lines) - 1):
            for v in var_names:
                val_n = b_lines[i]['state'].get(v, np.nan)
                val_n1 = b_lines[i + 1]['state'].get(v, np.nan)
                if val_n != -1 and val_n1 != -1 and not np.isnan(val_n) and not np.isnan(val_n1):
                    lag_pairs[v].append((val_n, val_n1))

    results = {}
    for v in var_names:
        lp = lag_pairs[v]
        if len(lp) < 20:
            results[v] = {'autocorr': 0.0, 'perm_p': 1.0, 'signal': False}
            continue

        x = np.array([p[0] for p in lp])
        y = np.array([p[1] for p in lp])

        if np.std(x) < 1e-10 or np.std(y) < 1e-10:
            results[v] = {'autocorr': 0.0, 'perm_p': 1.0, 'signal': False}
            continue

        autocorr, _ = pearsonr(x, y)

        # Permutation: shuffle within each paragraph's B-subsequence
        perm_autocorrs = []
        for _ in range(N_PERM):
            perm_pairs = []
            for b_lines in bb_sequences:
                if len(b_lines) < 3:
                    continue
                vals = [bl['state'].get(v, np.nan) for bl in b_lines]
                vals = [val for val in vals if val != -1 and not np.isnan(val)]
                if len(vals) < 3:
                    continue
                RNG.shuffle(vals)
                for i in range(len(vals) - 1):
                    perm_pairs.append((vals[i], vals[i + 1]))

            if len(perm_pairs) < 20:
                perm_autocorrs.append(0.0)
                continue
            px = np.array([p[0] for p in perm_pairs])
            py = np.array([p[1] for p in perm_pairs])
            if np.std(px) > 1e-10 and np.std(py) > 1e-10:
                pac, _ = pearsonr(px, py)
                perm_autocorrs.append(abs(pac))
            else:
                perm_autocorrs.append(0.0)

        perm_p = np.mean([pa >= abs(autocorr) for pa in perm_autocorrs])
        sig = perm_p < 0.01
        results[v] = {
            'autocorr': round(float(autocorr), 4),
            'perm_p': round(float(perm_p), 4),
            'n_pairs': len(lp),
            'signal': bool(sig),
        }
        marker = 'SIGNAL' if sig else 'null'
        print(f"  {v}: autocorr={autocorr:.4f} (perm p={perm_p:.4f}) {marker}")

    return {
        'test': 'S5_lag_autocorrelation',
        'variables': results,
    }


def main():
    print("Phase 451 Follow-up: MODE B STATE TRACKING")
    print("=" * 60)

    print("\nLoading data...")
    folios = load_data()

    print("Extracting B->B pairs...")
    pairs, bb_sequences = extract_bb_pairs(folios, min_body=4)
    print(f"  {len(pairs)} B->B consecutive pairs")
    print(f"  {len(bb_sequences)} B-track subsequences")
    total_b_lines = sum(len(s) for s in bb_sequences)
    print(f"  {total_b_lines} total B-track lines")

    r1 = s1_fl_propagation(pairs)
    r2 = s2_energy_balance(pairs)
    r3 = s3_suffix_state(pairs)
    r4 = s4_ordinal_progression(bb_sequences)
    r5 = s5_lag_autocorrelation(bb_sequences)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY: Mode B State Tracking")
    print("-" * 60)

    all_signals = []
    if r1.get('signal'):
        all_signals.append('FL_propagation')
        print("  SIGNAL: FL state propagates through B-track")

    for test_result in [r2, r3]:
        for v, vals in test_result.get('variables', {}).items():
            if vals.get('signal'):
                all_signals.append(v)
                print(f"  SIGNAL: {v} propagates through B-track")

    for test_result in [r4]:
        for v, vals in test_result.get('variables', {}).items():
            if vals.get('signal'):
                all_signals.append(f"ordinal_{v}")
                print(f"  SIGNAL: {v} shows ordinal progression in B-track")

    for v, vals in r5.get('variables', {}).items():
        if vals.get('signal'):
            if f"autocorr_{v}" not in [s for s in all_signals if s.startswith('autocorr')]:
                all_signals.append(f"autocorr_{v}")
                print(f"  SIGNAL: {v} has lag-1 autocorrelation in B-track")

    if not all_signals:
        print("  NO state variables propagate through Mode B track")
        verdict = "NULL -- B-track lines are stateless (independent similar loops)"
    elif len(all_signals) <= 2:
        print(f"\n  {len(all_signals)} state variable(s) show propagation")
        verdict = "WEAK -- isolated state tracking, mostly independent"
    else:
        print(f"\n  {len(all_signals)} state variables show propagation")
        verdict = "STATE_TRACKING -- B-track carries sequential state"

    print(f"\n  VERDICT: {verdict}")
    print(f"  Signals: {all_signals}")

    output = {
        'phase': 'Phase 451 Follow-up: MODE_B_STATE_TRACKING',
        'verdict': verdict,
        'signals': all_signals,
        'n_signals': len(all_signals),
        'S1': r1, 'S2': r2, 'S3': r3, 'S4': r4, 'S5': r5,
        'data_summary': {
            'n_bb_pairs': len(pairs),
            'n_bb_sequences': len(bb_sequences),
            'n_b_lines': total_b_lines,
        },
    }

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.bool_, np.integer)):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    out_path = Path(__file__).resolve().parents[1] / 'results' / 'mode_b_state_tracking.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
