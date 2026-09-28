#!/usr/bin/env python3
"""PHASE_762 Part B — Testamentum audit tests. See ../PRE_REGISTRATION.md (locked, commit dd88045).

B1 per-source column-permutation nulls; B2 similarity-matched leaf-mate adjacency; B3 part -> section (bias-corrected V);
B5 demonstration of the optimized-vs-random permutation flaw (C1887 procedure).
The matcher is shared_628's pipeline; a numpy re-implementation (`fast_match`) is used for speed and is checked for
exact agreement with `shared_628.residual_match` before use.
Implementation note (fixed before results): two recipe features feed two dimensions each (heat_rate, monitoring_rate),
so column permutation shuffles the six underlying features, preserving the matcher's structure.
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'phases/RECIPE_FOLIO_CORRESPONDENCE/scripts'))
sys.path.insert(0, str(ROOT / 'phases/PER_DOMAIN_BRIDGE_CALIBRATION/scripts'))
sys.path.insert(0, str(ROOT / 'phases/PHASE_718_THEOPHILUS_8D_MATCHER/scripts'))
import shared_628 as S  # noqa: E402
import shared_627 as S7  # noqa: E402
from _featurize_theophilus import extract_chapters, featurize_chapter  # noqa: E402

OUT = ROOT / 'phases/PHASE_762_TESTAMENTUM_AUDIT/results'
OUT.mkdir(parents=True, exist_ok=True)
if '--smoke' in sys.argv:
    OUT = Path('C:/Users/EPILEC~1/AppData/Local/Temp/claude/C--git-voynich/e451f3a8-445d-45a0-bf5f-3a967a8e452a/scratchpad')
DIMS = S.TUNED_DIMS
FEATS = sorted({d[0] for d in DIMS})
ALPHA = 0.0167
N_SUB, N_COLPERM, N_PERM = 200, 100, 10_000
SMOKE = '--smoke' in sys.argv
if SMOKE:
    N_SUB, N_COLPERM, N_PERM = 2, 5, 200


def log(*a):
    print(*a, flush=True)


# ================================================================================================ data
def feat_value(ch, f):
    for key in ('k_channel', 'h_channel', 'e_channel', 't_channel'):
        if f in ch.get(key, {}):
            return float(ch[key][f] or 0.0)
    return float(ch.get(f, 0.0) or 0.0)


def pl_sources():
    e1 = S7.load_pl_chapters()
    orig = S.load_pl_channel_features()['T5_channel_signatures']['per_chapter']
    lines = S7.load_pl_english_lines()
    parity, original = [], []
    for i, (meta, oc) in enumerate(zip(e1, orig)):
        if oc.get('family') == 'theoretical':
            continue
        text = ''.join(lines[meta['en_line_start']:meta['en_line_end']])
        f = featurize_chapter(text)
        if f is None:
            continue
        base = {'part': meta['part'], 'number': meta['number'], 'idx': i, 'family': oc.get('family'),
                'n_words': f['n_words']}
        parity.append({**base, 'feat': np.array([feat_value(f, x) for x in FEATS])})
        original.append({**base, 'feat': np.array([feat_value(oc, x) for x in FEATS])})
    return parity, original


def theo_units(target_words):
    chs = extract_chapters(ROOT / 'sources/theophilus/theophilus_hendrie_1847.txt')
    by_book = defaultdict(list)
    for ch in chs:
        by_book[ch['book']].append(ch['text'])
    units = []
    for book, texts in by_book.items():
        cur, order = [], 0
        for t in texts:
            cur.append(t)
            if len(' '.join(cur).split()) >= target_words:
                units.append((book, order, ' '.join(cur)))
                order += 1
                cur = []
        if cur:
            if units and units[-1][0] == book and len(' '.join(cur).split()) < target_words / 2:
                b, o, t = units[-1]
                units[-1] = (b, o, t + ' ' + ' '.join(cur))
            else:
                units.append((book, order, ' '.join(cur)))
    out = []
    for book, order, text in units:
        f = featurize_chapter(text)
        if f is None:
            continue
        out.append({'part': book, 'number': order, 'n_words': f['n_words'],
                    'feat': np.array([feat_value(f, x) for x in FEATS])})
    return out


def codi_source():
    d = json.load(open(ROOT / 'sources/codicillus/codicillus_channel_features.json', encoding='utf-8'))
    segs = d.get('segments') or d.get('chapters') or d
    out = []
    for i, s in enumerate(segs):
        out.append({'part': 'Codicillus', 'number': i, 'feat': np.array([feat_value(s, x) for x in FEATS])})
    return out


# ================================================================================================ matcher
OP = S.load_b_operational_profiles()
DEP, _ = S.load_b_deployment_features()
REGIME = S.load_regime_mapping()


def v_matrix(pages):
    return np.array([S.build_v_vector(p, OP, DEP, DIMS) for p in pages], dtype=float)


def pl_matrix(feats):
    """feats: (n, len(FEATS)) -> (n, 8) with sign flips applied."""
    col = {f: i for i, f in enumerate(FEATS)}
    M = np.column_stack([feats[:, col[d[0]]] * d[2] for d in DIMS])
    return M


def distances(P, V):
    Pr = P - P.mean(axis=0)
    Vr = V - V.mean(axis=0)
    A = np.vstack([Pr, Vr])
    mu = A.mean(axis=0)
    sd = A.std(axis=0)
    sd[sd == 0] = 1.0
    Z = (A - mu) / sd
    Pz, Vz = Z[:len(P)], Z[len(P):]
    return np.sqrt(((Pz[:, None, :] - Vz[None, :, :]) ** 2).sum(axis=2)), Vz


def assign(dmat):
    n_pl, n_v = dmat.shape
    order = sorted((dmat[i, j], i, j) for i in range(n_pl) for j in range(n_v))
    a, used = {}, set()
    for _, i, j in order:
        if i in a or j in used:
            continue
        a[i] = j
        used.add(j)
        if len(a) == n_pl:
            break
    improved = True
    while improved:
        improved = False
        keys = list(a.keys())
        for x in range(len(keys)):
            for y in range(x + 1, len(keys)):
                i1, i2 = keys[x], keys[y]
                j1, j2 = a[i1], a[i2]
                if dmat[i1, j2] + dmat[i2, j1] < dmat[i1, j1] + dmat[i2, j2] - 1e-12:
                    a[i1], a[i2] = j2, j1
                    improved = True
        for i in keys:
            j_cur = a[i]
            aset = set(a.values())
            for j_new in range(n_v):
                if j_new in aset:
                    continue
                if dmat[i, j_new] < dmat[i, j_cur] - 1e-12:
                    a[i] = j_new
                    improved = True
                    j_cur = j_new
    return a


def match_stats(dmat):
    a = assign(dmat)
    ratios, conf = [], 0
    for i, j in a.items():
        d = dmat[i, j]
        others = np.delete(dmat[i], j)
        second = others.min() if len(others) else d
        r = second / d if d > 0.01 else 1.0
        r = round(float(r), 3)
        ratios.append(r)
        conf += r > 1.15
    return sum(ratios) / len(ratios), int(conf), a       # same arithmetic as shared_628


def fast_match(feats, V):
    dmat, _ = distances(pl_matrix(feats), V)
    return match_stats(dmat)


def check_equivalence(src, pages, rng):
    """Exact agreement with shared_628.residual_match on 5 random subsets."""
    for _ in range(5):
        idx = rng.choice(len(src), size=16, replace=False)
        chs = [{f: float(src[i]['feat'][k]) for k, f in enumerate(FEATS)} for i in idx]
        ref = S.residual_match(chs, pages, DIMS, OP, DEP)
        mr, nc, a = fast_match(np.array([src[i]['feat'] for i in idx]), v_matrix(pages))
        same_assign = {int(k): v for k, v in ref['assignment'].items()} == a
        assert same_assign and ref['n_confident'] == nc and abs(ref['mean_ratio'] - mr) <= 0.0006, \
            (same_assign, ref['n_confident'], nc, ref['mean_ratio'], mr)


# ================================================================================================ B1
def colperm(feats, rng):
    out = feats.copy()
    for k in range(feats.shape[1]):
        out[:, k] = rng.permutation(out[:, k])
    return out


def b1(src, V, seed0):
    res = []
    for s in range(N_SUB):
        rng = np.random.default_rng(seed0 + s)
        idx = rng.choice(len(src), size=16, replace=False)
        F = np.array([src[i]['feat'] for i in idx])
        mr, nc, _ = fast_match(F, V)
        nmr, nnc = [], []
        for _ in range(N_COLPERM):
            a, b, _ = fast_match(colperm(F, rng), V)
            nmr.append(a)
            nnc.append(b)
        nmr, nnc = np.array(nmr), np.array(nnc)
        res.append({'mean_ratio': mr, 'n_conf': nc,
                    'excess_ratio': mr - float(np.median(nmr)), 'excess_conf': nc - float(np.median(nnc)),
                    'p_ratio': float((1 + (nmr >= mr).sum()) / (1 + N_COLPERM)),
                    'p_conf': float((1 + (nnc >= nc).sum()) / (1 + N_COLPERM))})
    ex = np.array([r['excess_ratio'] for r in res])
    return {'n_subsets': len(res), 'median_mean_ratio': float(np.median([r['mean_ratio'] for r in res])),
            'median_excess_ratio': float(np.median(ex)), 'q95_excess_ratio': float(np.quantile(ex, 0.95)),
            'median_p_ratio': float(np.median([r['p_ratio'] for r in res])),
            'median_excess_conf': float(np.median([r['excess_conf'] for r in res])),
            'median_p_conf': float(np.median([r['p_conf'] for r in res]))}


def b1_verdict(pl, th):
    if pl['median_p_ratio'] >= ALPHA:
        return 'NO CORRESPONDENCE'
    if pl['median_excess_ratio'] > th['q95_excess_ratio']:
        return 'SPECIFIC'
    if th['median_p_ratio'] < ALPHA:
        return 'GENERIC'
    return 'INTERMEDIATE'


# ================================================================================================ B2 / B3
def page_sections():
    from scripts.voynich import Transcript
    sec = {}
    for t in Transcript().currier_b():
        sec.setdefault(t.folio, t.section)
    return sec


SEC = page_sections()


def leaves(pages):
    by = defaultdict(dict)
    for i, p in enumerate(pages):
        m = re.fullmatch(r'f(\d+)([rv])', p)
        if m:
            by[int(m.group(1))][m.group(2)] = i
    return [(d['r'], d['v']) for n, d in sorted(by.items()) if 'r' in d and 'v' in d]


def b2(src, pages, V, rng_seed):
    F = np.array([c['feat'] for c in src])
    dmat, Vz = distances(pl_matrix(F), V)
    nearest = dmat.argmin(axis=0)                      # per page
    part = [src[i]['part'] for i in nearest]
    num = [src[i]['number'] for i in nearest]
    n = len(pages)
    pdist = np.sqrt(((Vz[:, None, :] - Vz[None, :, :]) ** 2).sum(axis=2))
    lv = set(leaves(pages))
    pairs, is_leaf, adj, same = [], [], [], []
    for i in range(n):
        for j in range(i + 1, n):
            if SEC.get(pages[i]) is None or SEC.get(pages[i]) != SEC.get(pages[j]):
                continue
            pairs.append((i, j))
            is_leaf.append((i, j) in lv or (j, i) in lv)
            sp = part[i] == part[j]
            adj.append(sp and abs(num[i] - num[j]) == 1)
            same.append(sp and num[i] == num[j])
    pairs, is_leaf, adj, same = map(np.array, (pairs, is_leaf, adj, same))
    d = np.array([pdist[i, j] for i, j in pairs])
    dec = np.digitize(d, np.quantile(d, np.linspace(0.1, 0.9, 9)))
    secs = np.array([SEC[pages[i]] for i, _ in pairs])
    strata = defaultdict(list)
    for k, (s, q) in enumerate(zip(secs, dec)):
        strata[(s, q)].append(k)
    leaf_idx = np.flatnonzero(is_leaf)
    need = Counter((secs[k], dec[k]) for k in leaf_idx)
    obs_adj, obs_same = float(adj[leaf_idx].mean()), float(same[leaf_idx].mean())
    rng = np.random.default_rng(rng_seed)
    null_adj, null_same = [], []
    for _ in range(N_PERM):
        pick = np.concatenate([rng.choice(strata[s], size=c, replace=False) for s, c in need.items()])
        null_adj.append(adj[pick].mean())
        null_same.append(same[pick].mean())
    null_adj, null_same = np.array(null_adj), np.array(null_same)
    chance = float(adj.mean())
    return {'eligible_leaves': int(len(leaf_idx)), 'leaf_adjacent_rate': obs_adj, 'matched_null_mean': float(null_adj.mean()),
            'excess': obs_adj - float(null_adj.mean()), 'p': float((1 + (null_adj >= obs_adj).sum()) / (1 + N_PERM)),
            'chance_rate_all_same_section_pairs': chance,
            'relative_to_chance': obs_adj / chance if chance > 0 else None,
            'MDE80': 2.485 * float(null_adj.std()),
            'same_chapter_rate': obs_same, 'same_chapter_null_mean': float(null_same.mean()),
            'same_chapter_p': float((1 + (null_same >= obs_same).sum()) / (1 + N_PERM))}


def bias_corrected_v(table):
    t = np.asarray(table, float)
    t = t[t.sum(axis=1) > 0][:, t.sum(axis=0) > 0]
    n = t.sum()
    r, k = t.shape
    if r < 2 or k < 2:
        return 0.0
    exp = np.outer(t.sum(1), t.sum(0)) / n
    chi2 = ((t - exp) ** 2 / exp).sum()
    phi2 = chi2 / n
    phi2c = max(0.0, phi2 - (k - 1) * (r - 1) / (n - 1))
    rc = r - (r - 1) ** 2 / (n - 1)
    kc = k - (k - 1) ** 2 / (n - 1)
    den = min(kc - 1, rc - 1)
    return float(np.sqrt(phi2c / den)) if den > 0 else 0.0


def contingency(labels, sections):
    L = sorted(set(labels))
    Sx = sorted(set(sections))
    t = np.zeros((len(L), len(Sx)))
    for a, b in zip(labels, sections):
        t[L.index(a), Sx.index(b)] += 1
    return t


def b3(src, pages, V, seed, exclude=None, partition=None):
    F = np.array([c['feat'] for c in src])
    dmat, _ = distances(pl_matrix(F), V)
    keep = [j for j in range(len(pages)) if not exclude or pages[j] not in exclude]
    nearest = [keep[k] for k in dmat[:, keep].argmin(axis=1)]
    secs = [SEC.get(pages[j], '?') for j in nearest]
    labels = [partition(c) if partition else c['part'] for c in src]
    v = bias_corrected_v(contingency(labels, secs))
    rng = np.random.default_rng(seed)
    null = np.array([bias_corrected_v(contingency(list(rng.permutation(labels)), secs)) for _ in range(N_PERM)])
    sd = null.std()
    return {'V_bc': v, 'null_mean': float(null.mean()), 'z': float((v - null.mean()) / sd) if sd > 0 else None,
            'p': float((1 + (null >= v - 1e-12).sum()) / (1 + N_PERM)),
            'table': {lab: dict(Counter(s for l, s in zip(labels, secs) if l == lab)) for lab in sorted(set(labels))},
            'nearest_pages': [pages[j] for j in nearest]}


def three_way(pl_p, th_p):
    if pl_p >= ALPHA:
        return 'NO EFFECT'
    if th_p >= 0.05:
        return 'SPECIFIC'
    if th_p < ALPHA:
        return 'GENERIC'
    return 'INTERMEDIATE'


# ================================================================================================ B5
def b5(src_feats_list, pages, n_perm=200):
    """C1887's procedure (shared_628.permutation_test): optimized assignment vs random assignments on one matrix."""
    ps = []
    for F in src_feats_list:
        chs = [{f: float(row[k]) for k, f in enumerate(FEATS)} for row in F]
        r = S.permutation_test(chs, pages, DIMS, n_perm=n_perm, op_profiles=OP, deploy_features=DEP)
        ps.append(r.get('p_ratio', r.get('p_value')))
    ps = np.array(ps, dtype=float)
    return {'n_sets': len(ps), 'n_perm': n_perm, 'fraction_p_lt_0.01': float((ps < 0.01).mean()), 'median_p': float(np.median(ps))}


# ================================================================================================ main
def main():
    t0 = time.time()
    rng = np.random.default_rng(762)
    pl_par, pl_orig = pl_sources()
    med_words = int(np.median([c['n_words'] for c in pl_par]))
    theo = theo_units(med_words)
    codi = codi_source()
    pages_all = sorted(p for p in OP if p in SEC)
    pages_r1 = sorted(p for p in pages_all if REGIME.get(p) == 'REGIME_1')
    log(f"PL-PROC {len(pl_par)} chapters (median {med_words} words); THEO {len(theo)} units "
        f"(median {int(np.median([c['n_words'] for c in theo]))} words); CODI {len(codi)}; pages all {len(pages_all)}, R1 {len(pages_r1)}")
    check_equivalence(pl_par, pages_all, rng)
    log('fast matcher agrees exactly with shared_628.residual_match')
    out = {'phase': 'PHASE_762', 'pre_registration_commit': 'dd88045',
           'sizes': {'PL_PROC': len(pl_par), 'THEO_units': len(theo), 'CODI': len(codi), 'pages_all': len(pages_all),
                     'pages_R1': len(pages_r1), 'PL_median_words': med_words}}
    V_all, V_r1 = v_matrix(pages_all), v_matrix(pages_r1)
    # ---- B1
    out['B1'] = {}
    for name, src, V in (('PL_parity_all', pl_par, V_all), ('THEO_all', theo, V_all), ('CODI_all', codi, V_all),
                         ('PL_original_all', pl_orig, V_all), ('PL_parity_R1', pl_par, V_r1), ('THEO_R1', theo, V_r1)):
        out['B1'][name] = b1(src, V, 762000)
        log(f"B1 {name}: {out['B1'][name]}  ({time.time() - t0:.0f}s)")
    out['B1']['verdict_primary'] = b1_verdict(out['B1']['PL_parity_all'], out['B1']['THEO_all'])
    out['B1']['original_features_same_direction'] = out['B1']['PL_original_all']['median_excess_ratio'] > 0
    # ---- B2
    out['B2'] = {}
    for name, src in (('PL_parity', pl_par), ('THEO', theo), ('PL_original', pl_orig)):
        out['B2'][name] = b2(src, pages_all, V_all, 762)
        log(f"B2 {name}: {out['B2'][name]}")
    out['B2']['verdict_primary'] = three_way(out['B2']['PL_parity']['p'], out['B2']['THEO']['p'])
    # ---- B3
    out['B3'] = {}
    for name, src in (('PL_parity', pl_par), ('THEO', theo), ('PL_original', pl_orig)):
        out['B3'][name] = b3(src, pages_all, V_all, 762)
        log(f"B3 {name}: V_bc={out['B3'][name]['V_bc']:.3f} z={out['B3'][name]['z']} p={out['B3'][name]['p']:.4f} "
            f"table={out['B3'][name]['table']}")
    out['B3']['verdict_primary'] = three_way(out['B3']['PL_parity']['p'], out['B3']['THEO']['p'])
    pooled = Counter(out['B3']['PL_parity']['nearest_pages'] + out['B3']['THEO']['nearest_pages'])
    attractors = [p for p, _ in pooled.most_common(5)]
    out['B3']['attractors'] = attractors
    out['B3']['attractor_share'] = {k: float(np.mean([p in attractors for p in out['B3'][k]['nearest_pages']]))
                                    for k in ('PL_parity', 'THEO')}
    for name, src in (('PL_parity_noattr', pl_par), ('THEO_noattr', theo)):
        out['B3'][name] = b3(src, pages_all, V_all, 762, exclude=set(attractors))
        log(f"B3 {name}: V_bc={out['B3'][name]['V_bc']:.3f} p={out['B3'][name]['p']:.4f}")

    def merc_split(c):
        if c['part'] == 'Mercuriorum':
            return 'Merc<=28' if c['number'] <= 28 else 'Merc>=29'
        return c['part']
    out['B3']['secondary_merc_split'] = b3(pl_par, pages_all, V_all, 762, partition=merc_split)
    merc_lo = [(c, p) for c, p in zip(pl_par, out['B3']['PL_parity']['nearest_pages'])
               if c['part'] == 'Mercuriorum' and c['number'] <= 28]
    out['B3']['descriptive_merc_le28_in_section_B'] = float(np.mean([SEC.get(p) == 'B' for _, p in merc_lo])) if merc_lo else None
    for k in list(out['B3']):
        if isinstance(out['B3'][k], dict):
            out['B3'][k].pop('nearest_pages', None)
    # ---- B5
    rng5 = np.random.default_rng(762500)
    gauss = [rng5.normal(size=(16, len(FEATS))) for _ in range(100)]
    theo_sets = [np.array([theo[i]['feat'] for i in rng5.choice(len(theo), size=16, replace=False)]) for _ in range(100)]
    out['B5'] = {'gaussian': b5(gauss, pages_all), 'theophilus': b5(theo_sets, pages_all)}
    out['B5']['flaw_confirmed'] = out['B5']['gaussian']['fraction_p_lt_0.01'] >= 0.95
    log(f"B5: {out['B5']}")
    # direction gate: SPECIFIC needs the original-PL-features run to point the same way
    dirs = {'B1': out['B1']['PL_original_all']['median_excess_ratio'] > 0,
            'B2': out['B2']['PL_original']['excess'] > 0,
            'B3': (out['B3']['PL_original']['z'] or 0) > 0}
    for k, ok in dirs.items():
        out[k]['original_features_same_direction'] = bool(ok)
        if out[k]['verdict_primary'] == 'SPECIFIC' and not ok:
            out[k]['verdict_primary'] = 'INCONCLUSIVE'
    out['runtime_s'] = round(time.time() - t0, 1)
    json.dump(out, open(OUT / 'testamentum_audit.json', 'w', encoding='utf-8'), indent=1, default=float)
    log(f"VERDICTS (locked rules): B1 {out['B1']['verdict_primary']} | B2 {out['B2']['verdict_primary']} | "
        f"B3 {out['B3']['verdict_primary']} | B5 flaw confirmed {out['B5']['flaw_confirmed']}  ({out['runtime_s']}s)")


if __name__ == '__main__':
    main()
