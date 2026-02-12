#!/usr/bin/env python3
"""
T3: Compositional Sparsity Null Model (F7, F8, F11)
FINGERPRINT_UNIQUENESS phase

F7:  MIDDLE incompatibility (fraction of pairs never co-occurring in same line)
F8:  Hub rationing (actual hub usage vs greedy baseline)
F11: Suffix-role stratification (chi2 of suffix presence vs role)

Three null ensembles:
  NULL-G: Token shuffle (permute tokens across records)
  NULL-H: Class reassignment (random token->class mapping)
  NULL-I: Latent feature model (3-5 dims, tests dimensional necessity)

NOTE: Incompatibility measured at B line level. C475's 95.7% is A-scope
at record level with different MIDDLE inventory. Our B measurement is the
consistent baseline for null comparison.
"""

import sys
import json
import time
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import chi2_contingency

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)  # Force flush on Windows
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'
N_SAMPLES = 1000
RNG = np.random.default_rng(42)


# ============================================================
# DATA LOADING (pre-compute everything once)
# ============================================================

def load_data():
    """Load all data and pre-compute structures for fast null generation."""
    t0 = time.time()

    with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
    class_to_role[17] = 'CORE_CONTROL'

    all_cls = set(token_to_class.values())
    EN = ({8} | set(range(31, 50)) - {7, 30, 38, 40}) & all_cls
    FL = {7, 30, 38, 40}
    CC = {10, 11, 12}
    FQ = {9, 13, 14, 23}
    AX = all_cls - EN - FL - CC - FQ

    def get_role(c):
        if c in CC: return 'CC'
        if c in FL: return 'FL'
        if c in FQ: return 'FQ'
        if c in EN: return 'EN'
        if c in AX: return 'AX'
        return 'UN'

    tx = Transcript()
    morph = Morphology()

    # Build flat token list and record structure
    records = []  # list of (key, [token_dicts])
    all_token_list = []  # flat list of all token dicts (for shuffling)
    record_sizes = []

    current_key = None
    current_rec = []

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        cls = token_to_class.get(w)
        if cls is None:
            continue
        key = (token.folio, token.line)
        m = morph.extract(w)
        td = {
            'word': w,
            'middle': m.middle if m.middle else '_NONE_',
            'suffix': m.suffix,
            'cls': cls,
            'role': get_role(cls),
        }
        if key != current_key:
            if current_rec:
                records.append((current_key, current_rec))
                record_sizes.append(len(current_rec))
            current_rec = []
            current_key = key
        current_rec.append(td)
        all_token_list.append(td)

    if current_rec:
        records.append((current_key, current_rec))
        record_sizes.append(len(current_rec))

    print(f"  Loaded {len(records)} records, {len(all_token_list)} tokens in {time.time()-t0:.1f}s")

    return records, all_token_list, record_sizes, token_to_class, get_role


# ============================================================
# FAST METRIC COMPUTATION
# ============================================================

def compute_incompatibility(token_records):
    """Fast incompatibility: fraction of MIDDLE pairs never co-occurring."""
    all_middles = set()
    record_middles = []
    for rec in token_records:
        mids = set(t['middle'] for t in rec if t['middle'] != '_NONE_')
        if len(mids) >= 2:
            record_middles.append(mids)
            all_middles.update(mids)

    mid_list = sorted(all_middles)
    n_mid = len(mid_list)
    if n_mid < 2:
        return 0.0, n_mid

    mid_idx = {m: i for i, m in enumerate(mid_list)}
    cooccur = set()
    for mids in record_middles:
        idx = sorted(mid_idx[m] for m in mids)
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                cooccur.add((idx[a], idx[b]))

    n_possible = n_mid * (n_mid - 1) // 2
    return 1.0 - len(cooccur) / n_possible, n_mid


def compute_hub_savings(token_records, hub_frac=0.15):
    """Hub rationing: actual hub usage vs greedy."""
    mid_record_count = Counter()
    all_mids_lists = []
    n_rec = 0

    for rec in token_records:
        mids = [t['middle'] for t in rec if t['middle'] != '_NONE_']
        if mids:
            n_rec += 1
            for m in set(mids):
                mid_record_count[m] += 1
            all_mids_lists.append(mids)

    if n_rec == 0:
        return 0.0

    hub_thresh = hub_frac * n_rec
    hubs = {m for m, c in mid_record_count.items() if c >= hub_thresh}
    if not hubs:
        return 0.0

    total = sum(len(ml) for ml in all_mids_lists)
    actual_hub = sum(1 for ml in all_mids_lists for m in ml if m in hubs)
    greedy_hub = sum(len(ml) for ml in all_mids_lists if set(ml) & hubs)

    actual_frac = actual_hub / total
    greedy_frac = greedy_hub / total
    return greedy_frac - actual_frac


def compute_suffix_chi2(token_records):
    """Chi-squared for suffix presence vs role."""
    role_has = Counter()
    role_no = Counter()
    for rec in token_records:
        for t in rec:
            if t['suffix'] is not None:
                role_has[t['role']] += 1
            else:
                role_no[t['role']] += 1

    roles = sorted(set(list(role_has.keys()) + list(role_no.keys())))
    if len(roles) < 2:
        return 0.0

    table = np.array([[role_has.get(r, 0), role_no.get(r, 0)] for r in roles])
    if table.min() < 0 or table.sum() == 0:
        return 0.0

    try:
        chi2, _, _, _ = chi2_contingency(table)
        return chi2
    except Exception:
        return 0.0


def compute_all(token_records):
    """Compute all three metrics."""
    incomp, n_mid = compute_incompatibility(token_records)
    savings = compute_hub_savings(token_records)
    chi2 = compute_suffix_chi2(token_records)
    return incomp, savings, chi2, n_mid


# ============================================================
# NULL GENERATORS (return list of token-record lists)
# ============================================================

def null_g_shuffle(all_tokens, record_sizes, rng):
    """Token shuffle: redistribute all tokens randomly across records."""
    shuffled = list(all_tokens)
    rng.shuffle(shuffled)
    result = []
    idx = 0
    for size in record_sizes:
        result.append(shuffled[idx:idx + size])
        idx += size
    return result


def null_h_class_reassign(all_tokens, record_sizes, token_to_class, get_role, rng):
    """Random class reassignment: shuffle token->class mapping."""
    # Build shuffled mapping
    all_tok_types = sorted(token_to_class.keys())
    class_ids = [token_to_class[t] for t in all_tok_types]
    rng.shuffle(class_ids)
    new_t2c = dict(zip(all_tok_types, class_ids))

    # Rebuild all tokens with new roles
    new_tokens = []
    for t in all_tokens:
        new_cls = new_t2c.get(t['word'], t['cls'])
        new_tokens.append({
            'word': t['word'],
            'middle': t['middle'],
            'suffix': t['suffix'],
            'cls': new_cls,
            'role': get_role(new_cls),
        })

    # Redistribute to records
    result = []
    idx = 0
    for size in record_sizes:
        result.append(new_tokens[idx:idx + size])
        idx += size
    return result


def null_i_latent(all_tokens, record_sizes, n_dims, rng,
                  _mid_token_indices=None, _all_middles=None):
    """Latent feature model using bitmask vectorization for speed."""
    if _all_middles is None:
        _all_middles = sorted(set(t['middle'] for t in all_tokens if t['middle'] != '_NONE_'))
    if not _all_middles:
        result = []
        idx = 0
        for size in record_sizes:
            result.append(list(all_tokens[idx:idx + size]))
            idx += size
        return result

    n_rec = len(record_sizes)
    n_mid = len(_all_middles)
    max_mask = (1 << n_dims) - 1  # e.g. 7 for d=3

    # Random non-empty bitmasks (vectorized)
    rec_masks = rng.integers(1, max_mask + 1, size=n_rec, dtype=np.int32)
    mid_masks = rng.integers(1, max_mask + 1, size=n_mid, dtype=np.int32)

    # Vectorized compatibility: (n_rec, n_mid) boolean
    compat_matrix = (rec_masks[:, None] & mid_masks[None, :]) != 0

    # Pre-compute compatible MIDDLE indices per record
    compat_indices = []
    for r in range(n_rec):
        ci = np.nonzero(compat_matrix[r])[0]
        if len(ci) == 0:
            ci = np.arange(min(5, n_mid))
        compat_indices.append(ci)

    # Rebuild tokens with reassigned MIDDLEs (batch choices per record)
    new_tokens = list(all_tokens)
    idx = 0
    for rec_idx, size in enumerate(record_sizes):
        ci = compat_indices[rec_idx]
        need = [i for i in range(size) if all_tokens[idx + i]['middle'] != '_NONE_']
        if need:
            choices = rng.choice(ci, size=len(need))
            for j, i in enumerate(need):
                new_tokens[idx + i] = dict(all_tokens[idx + i],
                                           middle=_all_middles[choices[j]])
        idx += size

    # Split into records
    result = []
    idx = 0
    for size in record_sizes:
        result.append(new_tokens[idx:idx + size])
        idx += size
    return result


# ============================================================
# MAIN
# ============================================================

def run():
    t_start = time.time()
    print("=" * 70)
    print("T3: Compositional Sparsity Null Model (F7, F8, F11)")
    print("FINGERPRINT_UNIQUENESS phase")
    print("=" * 70)

    # 1. Load
    print("\n[1/5] Loading data...")
    records, all_tokens, record_sizes, token_to_class, get_role = load_data()

    # Extract record token lists for metrics
    obs_rec_lists = [rec for _, rec in records]

    # 2. Observed
    print("\n[2/5] Computing observed fingerprint...")
    obs_incomp, obs_savings, obs_chi2, n_mid = compute_all(obs_rec_lists)

    print(f"  F7  Incompatibility: {obs_incomp:.4f} ({n_mid} MIDDLEs)")
    print(f"  F8  Hub savings:     {obs_savings:.4f}")
    print(f"  F11 Suffix-role chi2: {obs_chi2:.1f}")

    # Per-role suffix detail
    role_has = Counter()
    role_no = Counter()
    role_stypes = defaultdict(set)
    for rec in obs_rec_lists:
        for t in rec:
            if t['suffix']:
                role_has[t['role']] += 1
                role_stypes[t['role']].add(t['suffix'])
            else:
                role_no[t['role']] += 1
    suffix_detail = {}
    for r in sorted(set(list(role_has.keys()) + list(role_no.keys()))):
        total = role_has.get(r, 0) + role_no.get(r, 0)
        suffix_detail[r] = {
            'suffix_less_frac': round(role_no.get(r, 0) / total, 4) if total else 0,
            'n_suffix_types': len(role_stypes.get(r, set())),
            'n_tokens': total,
        }
        print(f"       {r}: {suffix_detail[r]['suffix_less_frac']:.1%} suffix-less, "
              f"{suffix_detail[r]['n_suffix_types']} types")

    # 3. Null ensembles
    ensemble_results = {}

    def run_ensemble(label, gen_fn, n_samples):
        print(f"\n  Running {label} ({n_samples} samples)...")
        t0 = time.time()
        incomps, savings, chi2s = [], [], []
        for s in range(n_samples):
            recs = gen_fn()
            i, sv, c, _ = compute_all(recs)
            incomps.append(i)
            savings.append(sv)
            chi2s.append(c)
            if (s + 1) % 200 == 0:
                el = time.time() - t0
                rate = (s + 1) / el
                print(f"    {s+1}/{n_samples} ({rate:.1f}/s, ETA {(n_samples-s-1)/rate:.0f}s)")

        dt = time.time() - t0
        incomps = np.array(incomps)
        savings_arr = np.array(savings)
        chi2s = np.array(chi2s)

        p_i = float(np.mean(incomps >= obs_incomp))
        p_s = float(np.mean(savings_arr >= obs_savings))
        p_c = float(np.mean(chi2s >= obs_chi2))
        p_j = float(np.mean((incomps >= obs_incomp) & (savings_arr >= obs_savings) & (chi2s >= obs_chi2)))

        res = {
            'p_incompatibility': p_i,
            'p_hub_savings': p_s,
            'p_suffix_chi2': p_c,
            'p_joint': p_j,
            'null_incomp_mean': round(float(np.mean(incomps)), 4),
            'null_incomp_std': round(float(np.std(incomps)), 4),
            'null_savings_mean': round(float(np.mean(savings_arr)), 4),
            'null_chi2_mean': round(float(np.mean(chi2s)), 1),
            'time_seconds': round(dt, 1),
        }
        print(f"  {label}: P(incomp>={obs_incomp:.3f})={p_i:.4f} "
              f"[null={np.mean(incomps):.3f}] | "
              f"P(chi2>={obs_chi2:.0f})={p_c:.4f} | P(joint)={p_j:.6f}")
        return res

    # NULL-G
    print("\n[3/5] NULL-G: Token shuffle")
    ensemble_results['NULL_G_shuffle'] = run_ensemble(
        'NULL_G', lambda: null_g_shuffle(all_tokens, record_sizes, RNG), N_SAMPLES)

    # NULL-H
    print("\n[4/5] NULL-H: Class reassignment")
    ensemble_results['NULL_H_class_reassign'] = run_ensemble(
        'NULL_H', lambda: null_h_class_reassign(all_tokens, record_sizes, token_to_class, get_role, RNG),
        N_SAMPLES)

    # NULL-I: Latent feature model (d=3,4,5)
    print("\n[5/5] NULL-I: Latent feature model")
    # Pre-compute MIDDLE list once for all NULL-I runs
    _all_mids = sorted(set(t['middle'] for t in all_tokens if t['middle'] != '_NONE_'))
    null_i_results = {}
    for d in [3, 4, 5]:
        null_i_results[f'd={d}'] = run_ensemble(
            f'NULL_I_d{d}',
            lambda d=d: null_i_latent(all_tokens, record_sizes, d, RNG,
                                      _all_middles=_all_mids),
            N_SAMPLES)
    ensemble_results['NULL_I_latent'] = null_i_results

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nObserved: incomp={obs_incomp:.4f}, savings={obs_savings:.4f}, chi2={obs_chi2:.1f}")

    all_joints = [ensemble_results['NULL_G_shuffle']['p_joint'],
                  ensemble_results['NULL_H_class_reassign']['p_joint']]
    for res in null_i_results.values():
        all_joints.append(res['p_joint'])

    for label in ['NULL_G_shuffle', 'NULL_H_class_reassign']:
        print(f"  {label}: p_joint={ensemble_results[label]['p_joint']:.6f}")
    for dk, res in null_i_results.items():
        print(f"  NULL_I_{dk}: p_joint={res['p_joint']:.6f} "
              f"[incomp_mean={res['null_incomp_mean']:.3f}]")

    worst_p = max(all_joints)
    best_p = min(all_joints)

    if worst_p < 0.01:
        verdict = "RARE"
    elif worst_p < 0.05:
        verdict = "UNCOMMON"
    else:
        verdict = "NOT_RARE"
    print(f"\nBest p={best_p:.6f}, Worst p={worst_p:.6f}")
    print(f"T3 Verdict: {verdict}")

    # Dimensional necessity check
    for dk, res in null_i_results.items():
        if res['null_incomp_mean'] >= obs_incomp * 0.95:
            print(f"  WARNING: {dk} achieves near-observed incompatibility!")
        else:
            print(f"  OK: {dk} incomp={res['null_incomp_mean']:.3f} < observed {obs_incomp:.3f}")

    # Save
    results = {
        'test': 'T3_compositional_sparsity',
        'properties': ['F7_incompatibility', 'F8_hub_rationing', 'F11_suffix_role'],
        'observed': {
            'incompatibility': obs_incomp,
            'n_middles': n_mid,
            'hub_savings': obs_savings,
            'suffix_chi2': obs_chi2,
            'suffix_detail': suffix_detail,
        },
        'ensembles': ensemble_results,
        'verdict': verdict,
        'best_joint_p': best_p,
        'worst_joint_p': worst_p,
        'n_samples': N_SAMPLES,
        'n_records': len(records),
        'n_tokens': len(all_tokens),
        'elapsed_seconds': round(time.time() - t_start, 1),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't3_composition.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't3_composition.json'}")
    print(f"Total time: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    run()
