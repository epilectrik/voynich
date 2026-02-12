"""
T2-T4: Three-Way Interaction Tests
====================================
Phase: PREFIX_MIDDLE_SUFFIX_SYNERGY

T2: R² increment from 2-way to 3-way interaction model
T3: Token atomicity — full token vs naive Bayes for next-token prediction
T4: Synergy concentration by suffix stratum (EN vs AX vs depleted)

Output: t2_interaction_r2.json, t3_token_atomicity.json, t4_synergy_by_stratum.json
"""

import sys
import json
import functools
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats as sp_stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)


def mi_plugin(joint_counts):
    """MI in bits with Miller-Madow correction."""
    N = joint_counts.sum()
    if N == 0:
        return 0.0
    px = joint_counts.sum(axis=1) / N
    py = joint_counts.sum(axis=0) / N
    pxy = joint_counts / N
    mi = 0.0
    for i in range(pxy.shape[0]):
        for j in range(pxy.shape[1]):
            if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += pxy[i, j] * np.log2(pxy[i, j] / (px[i] * py[j]))
    nx = np.sum(px > 0)
    ny = np.sum(py > 0)
    correction = (nx - 1) * (ny - 1) / (2 * N * np.log(2))
    return max(0.0, mi - correction)


def build_contingency(x_labels, y_labels, x_vocab, y_vocab):
    x_idx = {v: i for i, v in enumerate(x_vocab)}
    y_idx = {v: i for i, v in enumerate(y_vocab)}
    table = np.zeros((len(x_vocab), len(y_vocab)), dtype=float)
    for xi, yi in zip(x_labels, y_labels):
        if xi in x_idx and yi in y_idx:
            table[x_idx[xi], y_idx[yi]] += 1
    return table


def load_class_map():
    path = PROJECT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
    with open(path) as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    all_cls = sorted(set(token_to_class.values()))
    EN = ({8} | set(range(31, 50)) - {7, 30, 38, 40}) & set(all_cls)
    FL = {7, 30, 38, 40} & set(all_cls)
    CC = {10, 11, 12} & set(all_cls)
    FQ = {9, 13, 14, 23} & set(all_cls)
    AX = set(all_cls) - EN - FL - CC - FQ
    class_to_role = {}
    for c in all_cls:
        if c in CC: class_to_role[c] = 'CC'
        elif c in FQ: class_to_role[c] = 'FQ'
        elif c in EN: class_to_role[c] = 'EN'
        elif c in FL: class_to_role[c] = 'FL'
        elif c in AX: class_to_role[c] = 'AX'
    return token_to_class, class_to_role


def build_corpus():
    """Build common corpus data for all tests."""
    morph = Morphology()
    tx = Transcript()
    token_to_class, class_to_role = load_class_map()

    with open(PROJECT / 'data' / 'regime_folio_mapping.json') as f:
        regime_data = json.load(f)
    folio_to_regime = {
        f: d['regime']
        for f, d in regime_data['regime_assignments'].items()
    }

    unique_words = set()
    for token in tx.currier_b():
        w = token.word.strip()
        if w and '*' not in w:
            unique_words.add(w)
    word_morph = {w: morph.extract(w) for w in unique_words}

    line_tokens = defaultdict(list)
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        line_tokens[(token.folio, token.line)].append(token)

    # Build records with sequential context
    records = []
    for (folio, line), tokens in line_tokens.items():
        n = len(tokens)
        regime = folio_to_regime.get(folio, 'UNKNOWN')

        morphs = []
        for tok in tokens:
            w = tok.word.strip()
            m = word_morph.get(w)
            if m is None or not m.middle:
                continue
            cls = token_to_class.get(w)
            role = class_to_role.get(cls, 'UNKNOWN') if cls else 'UNKNOWN'
            morphs.append({
                'word': w,
                'prefix': m.prefix or 'BARE',
                'middle': m.middle,
                'suffix': m.suffix or 'NONE',
                'class': cls,
                'role': role,
                'regime': regime,
            })

        for i, rec in enumerate(morphs):
            rec['position'] = min(4, int((i / max(n-1, 1)) * 5)) if n > 1 else 2
            rec['next_class'] = morphs[i+1]['class'] if i < len(morphs)-1 else None
            records.append(rec)

    records = [r for r in records if r['role'] != 'UNKNOWN' and r['class'] is not None]
    return records, token_to_class, class_to_role


def run_t2(records):
    """T2: R² increment from adding three-way interaction."""
    print(f"\n{'='*70}")
    print(f"T2: THREE-WAY INTERACTION R² INCREMENT")
    print(f"{'='*70}")

    # Use one-hot for PREFIX, CLASS, SUFFIX to predict POSITION
    # Build numerical target
    y = np.array([r['position'] for r in records], dtype=float)
    n = len(y)
    ss_total = np.sum((y - np.mean(y))**2)

    pre_vocab = sorted(set(r['prefix'] for r in records))
    cls_vocab = sorted(set(str(r['class']) for r in records))
    suf_vocab = sorted(set(r['suffix'] for r in records))
    pre_idx = {v: i for i, v in enumerate(pre_vocab)}
    cls_idx = {v: i for i, v in enumerate(cls_vocab)}
    suf_idx = {v: i for i, v in enumerate(suf_vocab)}

    # Main effects
    X_pre = np.zeros((n, len(pre_vocab)))
    X_cls = np.zeros((n, len(cls_vocab)))
    X_suf = np.zeros((n, len(suf_vocab)))
    for i, r in enumerate(records):
        X_pre[i, pre_idx[r['prefix']]] = 1.0
        X_cls[i, cls_idx[str(r['class'])]] = 1.0
        X_suf[i, suf_idx[r['suffix']]] = 1.0

    def r2(X):
        try:
            coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
            pred = X @ coef
            ss_res = np.sum((y - pred)**2)
            return 1.0 - ss_res / ss_total
        except np.linalg.LinAlgError:
            return 0.0

    # Model 1: Main effects
    X_main = np.hstack([X_pre, X_cls, X_suf])
    r2_main = r2(X_main)
    p_main = X_main.shape[1]

    # Model 2: + Two-way interactions (PREFIX×CLASS, PREFIX×SUFFIX, CLASS×SUFFIX)
    # Use interaction as joint indicators for top combos only (avoid explosion)
    pc_combos = Counter()
    ps_combos = Counter()
    cs_combos = Counter()
    for r in records:
        pc_combos[(r['prefix'], str(r['class']))] += 1
        ps_combos[(r['prefix'], r['suffix'])] += 1
        cs_combos[(str(r['class']), r['suffix'])] += 1

    # Keep combos with count >= 10
    MIN_COMBO = 10
    pc_valid = {k for k, v in pc_combos.items() if v >= MIN_COMBO}
    ps_valid = {k for k, v in ps_combos.items() if v >= MIN_COMBO}
    cs_valid = {k for k, v in cs_combos.items() if v >= MIN_COMBO}

    pc_list = sorted(pc_valid)
    ps_list = sorted(ps_valid)
    cs_list = sorted(cs_valid)

    pc_map = {v: i for i, v in enumerate(pc_list)}
    ps_map = {v: i for i, v in enumerate(ps_list)}
    cs_map = {v: i for i, v in enumerate(cs_list)}

    X_pc = np.zeros((n, len(pc_list)))
    X_ps = np.zeros((n, len(ps_list)))
    X_cs = np.zeros((n, len(cs_list)))

    for i, r in enumerate(records):
        pc_key = (r['prefix'], str(r['class']))
        ps_key = (r['prefix'], r['suffix'])
        cs_key = (str(r['class']), r['suffix'])
        if pc_key in pc_map:
            X_pc[i, pc_map[pc_key]] = 1.0
        if ps_key in ps_map:
            X_ps[i, ps_map[ps_key]] = 1.0
        if cs_key in cs_map:
            X_cs[i, cs_map[cs_key]] = 1.0

    X_twoway = np.hstack([X_main, X_pc, X_ps, X_cs])
    r2_twoway = r2(X_twoway)
    p_twoway = X_twoway.shape[1]

    # Model 3: + Three-way (PREFIX×CLASS×SUFFIX) for top combos
    pcs_combos = Counter()
    for r in records:
        pcs_combos[(r['prefix'], str(r['class']), r['suffix'])] += 1
    pcs_valid = {k for k, v in pcs_combos.items() if v >= MIN_COMBO}
    pcs_list = sorted(pcs_valid)
    pcs_map = {v: i for i, v in enumerate(pcs_list)}

    X_pcs = np.zeros((n, len(pcs_list)))
    for i, r in enumerate(records):
        pcs_key = (r['prefix'], str(r['class']), r['suffix'])
        if pcs_key in pcs_map:
            X_pcs[i, pcs_map[pcs_key]] = 1.0

    X_threeway = np.hstack([X_twoway, X_pcs])
    r2_threeway = r2(X_threeway)
    p_threeway = X_threeway.shape[1]

    r2_increment = r2_threeway - r2_twoway

    print(f"\n  {'Model':<25s} {'Params':>7s} {'R²':>8s}")
    print(f"  {'-'*25} {'-'*7} {'-'*8}")
    print(f"  {'Main effects':<25s} {p_main:>7d} {r2_main:>8.4f}")
    print(f"  {'+ Two-way':<25s} {p_twoway:>7d} {r2_twoway:>8.4f}")
    print(f"  {'+ Three-way':<25s} {p_threeway:>7d} {r2_threeway:>8.4f}")
    print(f"\n  Three-way R² increment: {r2_increment:+.4f} ({r2_increment*100:+.2f}%)")

    # F-test for increment
    df1 = p_threeway - p_twoway
    df2 = n - p_threeway
    if df1 > 0 and df2 > 0 and r2_twoway < 1.0:
        f_stat = ((r2_threeway - r2_twoway) / df1) / ((1 - r2_threeway) / df2)
        f_p = sp_stats.f.sf(f_stat, df1, df2)
    else:
        f_stat = 0.0
        f_p = 1.0

    print(f"  F-test: F={f_stat:.2f}, df=({df1},{df2}), p={f_p:.2e}")

    if r2_increment > 0.01 and f_p < 0.001:
        t2_verdict = 'THREE_WAY_INTERACTION_SIGNIFICANT'
    elif r2_increment > 0.005 and f_p < 0.01:
        t2_verdict = 'THREE_WAY_INTERACTION_MARGINAL'
    else:
        t2_verdict = 'NO_THREE_WAY_INTERACTION'

    print(f"  VERDICT: {t2_verdict}")

    t2_result = {
        'r2_main': r2_main, 'r2_twoway': r2_twoway, 'r2_threeway': r2_threeway,
        'r2_increment': r2_increment,
        'f_stat': float(f_stat), 'f_p': float(f_p),
        'params_main': p_main, 'params_twoway': p_twoway,
        'params_threeway': p_threeway,
        'n_pcs_combos': len(pcs_list),
        'verdict': t2_verdict,
    }

    out_path = RESULTS_DIR / 't2_interaction_r2.json'
    with open(out_path, 'w') as f:
        json.dump(t2_result, f, indent=2)
    print(f"  Output: {out_path}")

    return t2_result


def run_t3(records):
    """T3: Token atomicity — full token vs naive Bayes for next-class."""
    print(f"\n{'='*70}")
    print(f"T3: TOKEN ATOMICITY (FULL TOKEN vs NAIVE BAYES)")
    print(f"{'='*70}")

    # Filter to tokens with next_class
    seq_records = [r for r in records if r['next_class'] is not None]
    print(f"  Sequential records: {len(seq_records)}")

    n = len(seq_records)
    n_folds = 5
    rng = np.random.default_rng(42)
    indices = rng.permutation(n)
    fold_size = n // n_folds

    class_vocab = sorted(set(r['next_class'] for r in seq_records))
    cls_idx = {c: i for i, c in enumerate(class_vocab)}
    n_cls = len(class_vocab)

    fold_results = []
    for fold in range(n_folds):
        test_idx = set(range(fold * fold_size, min((fold+1) * fold_size, n)))
        train_idx = [i for i in range(n) if i not in test_idx]
        test_idx = sorted(test_idx)

        train = [seq_records[indices[i]] for i in train_idx]
        test = [seq_records[indices[i]] for i in test_idx]

        # Full-token lookup: P(next_class | word)
        word_next_dist = defaultdict(lambda: np.zeros(n_cls))
        for r in train:
            word_next_dist[r['word']][cls_idx[r['next_class']]] += 1

        # Naive Bayes: P(next_class | prefix) * P(next_class | class) * P(next_class | suffix)
        pre_next = defaultdict(lambda: np.zeros(n_cls))
        mid_next = defaultdict(lambda: np.zeros(n_cls))
        suf_next = defaultdict(lambda: np.zeros(n_cls))
        marginal = np.zeros(n_cls)

        for r in train:
            c_idx = cls_idx[r['next_class']]
            pre_next[r['prefix']][c_idx] += 1
            mid_next[str(r['class'])][c_idx] += 1
            suf_next[r['suffix']][c_idx] += 1
            marginal[c_idx] += 1

        # Normalize with Laplace smoothing
        def normalize(dist):
            d = dist + 1.0  # Laplace
            return d / d.sum()

        marginal_p = normalize(marginal)
        pre_next_p = {k: normalize(v) for k, v in pre_next.items()}
        mid_next_p = {k: normalize(v) for k, v in mid_next.items()}
        suf_next_p = {k: normalize(v) for k, v in suf_next.items()}
        word_next_p = {k: normalize(v) for k, v in word_next_dist.items()}

        # Score test set
        ll_full = 0.0
        ll_nb = 0.0
        n_test = 0

        for r in test:
            c_idx = cls_idx[r['next_class']]

            # Full-token
            if r['word'] in word_next_p:
                p_full = word_next_p[r['word']][c_idx]
            else:
                p_full = marginal_p[c_idx]

            # Naive Bayes
            p_pre = pre_next_p.get(r['prefix'], marginal_p)[c_idx]
            p_mid = mid_next_p.get(str(r['class']), marginal_p)[c_idx]
            p_suf = suf_next_p.get(r['suffix'], marginal_p)[c_idx]
            # Combine: P ∝ P(c|pre) * P(c|mid) * P(c|suf) / P(c)^2
            p_nb_raw = p_pre * p_mid * p_suf / (marginal_p[c_idx] ** 2 + 1e-30)
            # Renormalize
            nb_all = np.array([
                pre_next_p.get(r['prefix'], marginal_p)[j] *
                mid_next_p.get(str(r['class']), marginal_p)[j] *
                suf_next_p.get(r['suffix'], marginal_p)[j] /
                (marginal_p[j] ** 2 + 1e-30)
                for j in range(n_cls)
            ])
            nb_all = nb_all / (nb_all.sum() + 1e-30)
            p_nb = nb_all[c_idx]

            ll_full += np.log2(max(p_full, 1e-30))
            ll_nb += np.log2(max(p_nb, 1e-30))
            n_test += 1

        ll_full_per = ll_full / n_test
        ll_nb_per = ll_nb / n_test
        improvement = ll_full_per - ll_nb_per

        fold_results.append({
            'fold': fold, 'n_test': n_test,
            'll_full': ll_full_per, 'll_nb': ll_nb_per,
            'improvement': improvement,
        })
        print(f"  Fold {fold}: full={ll_full_per:.4f}, NB={ll_nb_per:.4f}, "
              f"gain={improvement:+.4f} bits/token")

    mean_improvement = np.mean([f['improvement'] for f in fold_results])
    std_improvement = np.std([f['improvement'] for f in fold_results])
    improvements = [f['improvement'] for f in fold_results]
    t_stat, t_p = sp_stats.ttest_1samp(improvements, 0.0)

    print(f"\n  Mean improvement: {mean_improvement:+.4f} ± {std_improvement:.4f} bits/token")
    print(f"  t-test: t={t_stat:.2f}, p={t_p:.4f}")

    if mean_improvement > 0.05 and t_p < 0.01:
        t3_verdict = 'TOKEN_ATOMICITY_CONFIRMED'
    elif mean_improvement > 0.02 and t_p < 0.05:
        t3_verdict = 'TOKEN_ATOMICITY_WEAK'
    else:
        t3_verdict = 'NO_TOKEN_ATOMICITY'

    print(f"  VERDICT: {t3_verdict}")

    t3_result = {
        'folds': fold_results,
        'mean_improvement': float(mean_improvement),
        'std_improvement': float(std_improvement),
        't_stat': float(t_stat), 't_p': float(t_p),
        'verdict': t3_verdict,
    }

    out_path = RESULTS_DIR / 't3_token_atomicity.json'
    with open(out_path, 'w') as f:
        json.dump(t3_result, f, indent=2)
    print(f"  Output: {out_path}")

    return t3_result


def run_t4(records):
    """T4: Synergy concentration by suffix stratum."""
    print(f"\n{'='*70}")
    print(f"T4: SYNERGY CONCENTRATION BY SUFFIX STRATUM")
    print(f"{'='*70}")

    # Stratify by role (C588 strata)
    strata = {
        'EN_SUFFIX_RICH': [r for r in records if r['role'] == 'EN'],
        'AX_SUFFIX_MODERATE': [r for r in records if r['role'] == 'AX'],
        'DEPLETED': [r for r in records if r['role'] in ('FL', 'FQ', 'CC')],
    }

    stratum_results = {}
    for stratum_name, stratum_records in strata.items():
        print(f"\n  --- {stratum_name} (N={len(stratum_records)}) ---")

        if len(stratum_records) < 100:
            print(f"  Too few records, skipping")
            stratum_results[stratum_name] = {
                'n': len(stratum_records), 'skipped': True}
            continue

        # Compute Co-Information for POSITION target
        pre_arr = [r['prefix'] for r in stratum_records]
        cls_arr = [str(r['class']) for r in stratum_records]
        suf_arr = [r['suffix'] for r in stratum_records]
        y = [str(r['position']) for r in stratum_records]

        pre_vocab = sorted(set(pre_arr))
        cls_vocab = sorted(set(cls_arr))
        suf_vocab = sorted(set(suf_arr))
        y_vocab = [str(i) for i in range(5)]

        pc_arr = [f"{p}|{c}" for p, c in zip(pre_arr, cls_arr)]
        ps_arr = [f"{p}|{s}" for p, s in zip(pre_arr, suf_arr)]
        cs_arr = [f"{c}|{s}" for c, s in zip(cls_arr, suf_arr)]
        pcs_arr = [f"{p}|{c}|{s}" for p, c, s in zip(pre_arr, cls_arr, suf_arr)]

        mi_p = mi_plugin(build_contingency(pre_arr, y, pre_vocab, y_vocab))
        mi_c = mi_plugin(build_contingency(cls_arr, y, cls_vocab, y_vocab))
        mi_s = mi_plugin(build_contingency(suf_arr, y, suf_vocab, y_vocab))
        mi_pc = mi_plugin(build_contingency(pc_arr, y, sorted(set(pc_arr)), y_vocab))
        mi_ps = mi_plugin(build_contingency(ps_arr, y, sorted(set(ps_arr)), y_vocab))
        mi_cs = mi_plugin(build_contingency(cs_arr, y, sorted(set(cs_arr)), y_vocab))
        mi_pcs = mi_plugin(build_contingency(pcs_arr, y, sorted(set(pcs_arr)), y_vocab))

        co_info = mi_pcs - (mi_pc + mi_ps + mi_cs) + (mi_p + mi_c + mi_s)

        print(f"  Co-Info (POSITION): {co_info:+.4f} bits "
              f"({'SYNERGY' if co_info < 0 else 'REDUNDANCY'})")

        # Also for REGIME
        y_reg = [r['regime'] for r in stratum_records]
        y_reg_vocab = sorted(set(y_reg))
        mi_p_r = mi_plugin(build_contingency(pre_arr, y_reg, pre_vocab, y_reg_vocab))
        mi_c_r = mi_plugin(build_contingency(cls_arr, y_reg, cls_vocab, y_reg_vocab))
        mi_s_r = mi_plugin(build_contingency(suf_arr, y_reg, suf_vocab, y_reg_vocab))
        mi_pc_r = mi_plugin(build_contingency(pc_arr, y_reg, sorted(set(pc_arr)), y_reg_vocab))
        mi_ps_r = mi_plugin(build_contingency(ps_arr, y_reg, sorted(set(ps_arr)), y_reg_vocab))
        mi_cs_r = mi_plugin(build_contingency(cs_arr, y_reg, sorted(set(cs_arr)), y_reg_vocab))
        mi_pcs_r = mi_plugin(build_contingency(pcs_arr, y_reg, sorted(set(pcs_arr)), y_reg_vocab))
        co_info_r = mi_pcs_r - (mi_pc_r + mi_ps_r + mi_cs_r) + (mi_p_r + mi_c_r + mi_s_r)
        print(f"  Co-Info (REGIME):   {co_info_r:+.4f} bits")

        stratum_results[stratum_name] = {
            'n': len(stratum_records),
            'co_info_position': float(co_info),
            'co_info_regime': float(co_info_r),
            'skipped': False,
        }

    # Compare strata
    en_co = stratum_results.get('EN_SUFFIX_RICH', {}).get('co_info_position', 0)
    dep_co = stratum_results.get('DEPLETED', {}).get('co_info_position', 0)

    if en_co < -0.05 and dep_co > -0.01:
        t4_verdict = 'SYNERGY_EN_CONCENTRATED'
    elif abs(en_co - dep_co) < 0.02:
        t4_verdict = 'SYNERGY_UNIFORM'
    else:
        t4_verdict = 'SYNERGY_DISTRIBUTION_MIXED'

    print(f"\n  VERDICT: {t4_verdict}")
    print(f"  EN Co-Info: {en_co:+.4f}, Depleted Co-Info: {dep_co:+.4f}")

    t4_result = {
        'strata': stratum_results,
        'verdict': t4_verdict,
    }

    out_path = RESULTS_DIR / 't4_synergy_by_stratum.json'
    with open(out_path, 'w') as f:
        json.dump(t4_result, f, indent=2)
    print(f"  Output: {out_path}")

    return t4_result


def main():
    print("Building corpus...")
    records, _, _ = build_corpus()
    print(f"  Total records: {len(records)}")

    t2_result = run_t2(records)
    t3_result = run_t3(records)
    t4_result = run_t4(records)

    print(f"\n{'='*70}")
    print(f"ALL PHASE 2 TESTS COMPLETE")
    print(f"{'='*70}")
    print(f"  T2: {t2_result['verdict']}")
    print(f"  T3: {t3_result['verdict']}")
    print(f"  T4: {t4_result['verdict']}")


if __name__ == '__main__':
    main()
