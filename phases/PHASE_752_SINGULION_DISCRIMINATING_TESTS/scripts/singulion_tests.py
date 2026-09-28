#!/usr/bin/env python3
"""PHASE_752 - Two discriminating tests on Layfield & Davis (2026b) singulion paper.

Test 1: herbal A/B-interleaving confound on the conjoint > facing signal (Q1-Q7), plus B-section arm.
Test 2: best-of-N permutation null for the Q13 / Q20 reorderings, plus cross-toolchain scoring of
        their proposed sequences in our LSA space.

See PRE_REGISTRATION.md (locked 2026-09-15) for definitions and kill conditions.
"""
from __future__ import annotations
import sys, json, itertools, re
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path("C:/git/voynich"); sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript

OUT = ROOT / "phases/PHASE_752_SINGULION_DISCRIMINATING_TESTS/results"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 752
N_SHUF_T1 = 10000
N_SHUF_T2 = 5000
K_PRIMARY = 75
K_ROBUST = [50, 100, None]   # None = raw TF-IDF cosine

QUIRES = {'Q1': (1, 8), 'Q2': (9, 16), 'Q3': (17, 24), 'Q4': (25, 32), 'Q5': (33, 40),
          'Q6': (41, 48), 'Q7': (49, 56), 'Q13': (75, 84), 'Q20': (103, 116)}
MISSING_LEAVES = {12, 109, 110}
HERBAL = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7']
PURE_A = ['Q1', 'Q2', 'Q3']
BSECT = ['Q13', 'Q20']


# ----------------------------------------------------------------------------- data
def load_pages():
    tx = Transcript()
    docs = defaultdict(list); langs = defaultdict(Counter)
    for t in tx.all(h_only=True):
        w = t.word.strip()
        if not w or t.is_uncertain:
            continue
        if not (t.placement.startswith('P') or t.placement.startswith('R')):
            continue
        docs[t.folio].append(w); langs[t.folio][t.language] += 1
    pages = sorted(docs)
    lang = {p: langs[p].most_common(1)[0][0] for p in pages}
    return pages, {p: docs[p] for p in pages}, lang


def build_sims(pages, docs):
    texts = [' '.join(docs[p]) for p in pages]
    vec = TfidfVectorizer(token_pattern=r'\S+', lowercase=False)
    X = vec.fit_transform(texts)
    sims = {}
    for k in [K_PRIMARY] + K_ROBUST:
        Z = X if k is None else TruncatedSVD(n_components=k, random_state=SEED).fit_transform(X)
        S = cosine_similarity(Z)
        # append an all-zero row/col for ABSENT pages (index = len(pages))
        S2 = np.zeros((S.shape[0] + 1, S.shape[1] + 1)); S2[:-1, :-1] = S
        sims['raw' if k is None else f'k{k}'] = S2
    return sims


# ----------------------------------------------------------------------------- collation
def leaves(q):
    a, b = QUIRES[q]; return [n for n in range(a, b + 1) if n not in MISSING_LEAVES]


def bifolia(q):
    a, b = QUIRES[q]; L = list(range(a, b + 1)); n = len(L)
    out = []
    for i in range(n // 2):
        A, B = L[i], L[n - 1 - i]
        if A in MISSING_LEAVES or B in MISSING_LEAVES:
            continue   # 12|13 singleton, 109|110 missing: no conjoint
        out.append((A, B))
    return out


def pg(n, side):
    return f"f{n}{side}"


def quire_pairs(q, idx):
    """Return dict of pair-type -> list of (page_i, page_j) index pairs (present pages only)."""
    P = {}
    lv = leaves(q)
    conf = [(pg(n, 'r'), pg(n, 'v')) for n in lv]
    fac = [(pg(lv[i], 'v'), pg(lv[i + 1], 'r')) for i in range(len(lv) - 1)]
    conj = [(pg(A, 'v'), pg(B, 'r')) for A, B in bifolia(q)]
    conj_all = [(pg(A, s1), pg(B, s2)) for A, B in bifolia(q) for s1 in 'rv' for s2 in 'rv']
    same_sheet = set()
    for A, B in bifolia(q):
        sheet = [pg(A, 'r'), pg(A, 'v'), pg(B, 'r'), pg(B, 'v')]
        for x in sheet:
            for y in sheet:
                if x != y:
                    same_sheet.add((x, y))
    present = [p for n in lv for p in (pg(n, 'r'), pg(n, 'v')) if p in idx]
    named = set(conf) | set(fac) | set(conj) | {(b, a) for a, b in conf + fac + conj}
    other = [(x, y) for i, x in enumerate(present) for y in present[i + 1:]
             if (x, y) not in named and (x, y) not in same_sheet]

    def toidx(lst):
        return [(idx[a], idx[b]) for a, b in lst if a in idx and b in idx]
    P['confoliate'] = toidx(conf); P['facing'] = toidx(fac); P['conjoint'] = toidx(conj)
    P['conjoint_all'] = toidx(conj_all); P['other'] = toidx(other)
    P['present'] = [idx[p] for p in present]
    return P


# ----------------------------------------------------------------------------- Test 1
def mean_pairs(S, pairs):
    return float(np.mean([S[i, j] for i, j in pairs])) if pairs else float('nan')


def split_lang(pairs, lang_of):
    same = [(i, j) for i, j in pairs if lang_of[i] == lang_of[j]]
    cross = [(i, j) for i, j in pairs if lang_of[i] != lang_of[j]]
    return same, cross


def test1(S, pages, idx, lang, quires, label, rng, n_shuf=N_SHUF_T1, tokcount=None):
    lang_of = {idx[p]: lang[p] for p in pages}
    per_q = {}; pooled = defaultdict(list)
    for q in quires:
        P = quire_pairs(q, idx)
        fs, fc = split_lang(P['facing'], lang_of)
        os_, oc = split_lang(P['other'], lang_of)
        per_q[q] = {
            'n_pages': len(P['present']),
            'languages': dict(Counter(lang_of[i] for i in P['present'])),
            'confoliate': mean_pairs(S, P['confoliate']), 'n_confoliate': len(P['confoliate']),
            'facing': mean_pairs(S, P['facing']), 'n_facing': len(P['facing']),
            'facing_same_lang': mean_pairs(S, fs), 'n_facing_same': len(fs),
            'facing_cross_lang': mean_pairs(S, fc), 'n_facing_cross': len(fc),
            'conjoint': mean_pairs(S, P['conjoint']), 'n_conjoint': len(P['conjoint']),
            'conjoint_all': mean_pairs(S, P['conjoint_all']),
            'other_same_lang': mean_pairs(S, os_), 'n_other_same': len(os_),
            'other_cross_lang': mean_pairs(S, oc), 'n_other_cross': len(oc),
        }
        for key, lst in [('confoliate', P['confoliate']), ('facing', P['facing']), ('facing_same', fs),
                         ('facing_cross', fc), ('conjoint', P['conjoint']), ('conjoint_all', P['conjoint_all']),
                         ('other_same', os_), ('other_cross', oc)]:
            pooled[key].extend((q, i, j) for i, j in lst)

    def pm(key):
        return float(np.mean([S[i, j] for _, i, j in pooled[key]])) if pooled[key] else float('nan')
    obs = {k: pm(k) for k in pooled}
    stats = {
        'gap_conj_minus_facing_all': obs['conjoint'] - obs['facing'],
        'gap_conj_minus_facing_same': obs['conjoint'] - obs['facing_same'],
        'gap_conj_minus_other_same': obs['conjoint'] - obs['other_same'],
        'gap_conf_minus_other_same': obs['confoliate'] - obs['other_same'],
        'gap_facing_same_minus_cross': (obs['facing_same'] - obs['facing_cross']) if pooled['facing_cross'] else None,
    }
    # ---- permutation null: shuffle page labels within quire AND within language class
    quire_perm_groups = {}
    for q in quires:
        P = quire_pairs(q, idx)
        groups = defaultdict(list)
        for i in P['present']:
            groups[lang_of[i]].append(i)
        quire_perm_groups[q] = groups
    keys = ['conjoint', 'facing', 'facing_same', 'other_same', 'confoliate']
    arrs = {k: (np.array([i for _, i, _ in pooled[k]], dtype=int),
                np.array([j for _, _, j in pooled[k]], dtype=int)) for k in keys}
    null = {k: [] for k in ['gap_conj_minus_facing_all', 'gap_conj_minus_facing_same',
                            'gap_conj_minus_other_same', 'gap_conf_minus_other_same']}
    npg = S.shape[0]
    for _ in range(n_shuf):
        lab = np.arange(npg)
        for q in quires:
            for g, members in quire_perm_groups[q].items():
                m = np.array(members); lab[m] = rng.permutation(m)

        def pm_shuf(k):
            I, J = arrs[k]
            return float(S[lab[I], lab[J]].mean()) if len(I) else float('nan')
        c = pm_shuf('conjoint'); f = pm_shuf('facing'); fs_ = pm_shuf('facing_same')
        o = pm_shuf('other_same'); cf = pm_shuf('confoliate')
        null['gap_conj_minus_facing_all'].append(c - f)
        null['gap_conj_minus_facing_same'].append(c - fs_)
        null['gap_conj_minus_other_same'].append(c - o)
        null['gap_conf_minus_other_same'].append(cf - o)
    pvals = {}
    for k, arr in null.items():
        arr = np.array(arr); ob = stats[k]
        pvals[k] = {'p_one_sided_ge': float(np.mean(arr >= ob)), 'null_mean': float(arr.mean()),
                    'null_sd': float(arr.std()), 'z': float((ob - arr.mean()) / arr.std()) if arr.std() > 0 else None}
    # ---- length check
    length = None
    if tokcount is not None:
        tc = {idx[p]: tokcount[p] for p in pages}
        length = {k: {'median_min_len': float(np.median([min(tc[i], tc[j]) for _, i, j in pooled[k]]))}
                  for k in ['confoliate', 'facing', 'conjoint', 'other_same'] if pooled[k]}
        allpairs = [(k, i, j) for k in ['conjoint', 'other_same'] for _, i, j in pooled[k]]
        ml = np.array([min(tc[i], tc[j]) for _, i, j in allpairs])
        cuts = np.quantile(ml, [1 / 3, 2 / 3])
        strata = {}
        for b in range(3):
            lo = -1 if b == 0 else cuts[b - 1]; hi = cuts[b] if b < 2 else 1e9
            sel = [(k, i, j) for (k, i, j), m in zip(allpairs, ml) if lo < m <= hi]
            cj = [S[i, j] for k, i, j in sel if k == 'conjoint']
            ot = [S[i, j] for k, i, j in sel if k == 'other_same']
            strata[f'tertile_{b+1}'] = {'n_conjoint': len(cj), 'n_other': len(ot),
                                        'conjoint': float(np.mean(cj)) if cj else None,
                                        'other_same': float(np.mean(ot)) if ot else None,
                                        'gap': (float(np.mean(cj) - np.mean(ot)) if cj and ot else None)}
        length['stratified_conj_minus_other'] = strata
    return {'label': label, 'quires': quires, 'per_quire': per_q, 'pooled_means': obs,
            'stats': stats, 'null': pvals, 'n_shuffles': n_shuf, 'length_check': length}


# ----------------------------------------------------------------------------- Test 2
def section_bifolia_pages(q, idx, absent_idx, drop=None):
    bf = [b for b in bifolia(q) if b != drop]

    def gi(p):
        return idx.get(p, absent_idx)
    slots = [(gi(pg(A, 'r')), gi(pg(A, 'v')), gi(pg(B, 'r')), gi(pg(B, 'v'))) for A, B in bf]
    return bf, slots


def test2(S, idx, q, their_seqs, rng, drop=None, n_shuf=N_SHUF_T2, label=''):
    absent = S.shape[0] - 1
    inv = {i: p for p, i in idx.items()}
    bf, slots = section_bifolia_pages(q, idx, absent, drop=drop)
    n = len(bf)
    perms = np.array(list(itertools.permutations(range(n))))          # (N!, n)
    Ar = np.array([s[0] for s in slots]); Av = np.array([s[1] for s in slots])
    Br = np.array([s[2] for s in slots]); Bv = np.array([s[3] for s in slots])
    JB = Bv[perms[:, :-1]]; JA = Ar[perms[:, 1:]]                       # (N!, n-1)
    conj_pairs = list(zip(Av, Br))
    # current facing baseline (nested order) over present pages of the kept leaves
    P = quire_pairs(q, idx)
    keep_leaves = {x for A, B in bf for x in (A, B)}

    def leaf_of(i):
        return int(re.match(r'f(\d+)', inv[i]).group(1))
    fac = [(i, j) for i, j in P['facing'] if leaf_of(i) in keep_leaves and leaf_of(j) in keep_leaves]
    facI = np.array([i for i, _ in fac]); facJ = np.array([j for _, j in fac])

    def evaluate(lab):
        scores = S[lab[JB], lab[JA]].mean(axis=1)                       # objective A per permutation
        current_facing = S[lab[facI], lab[facJ]].mean()
        return scores, current_facing
    ident = np.arange(S.shape[0])
    scores, cur_fac = evaluate(ident)
    conj_const = float(np.mean([S[i, j] for i, j in conj_pairs]))
    scoresB = (scores * (n - 1) + conj_const * n) / (2 * n - 1)
    best_i = int(np.argmax(scores)); best = float(scores[best_i])
    perm_tuples = [tuple(p) for p in perms]
    identity_row = perm_tuples.index(tuple(range(n)))
    cur_objA = float(scores[identity_row])
    res = {
        'section': q, 'label': label, 'n_bifolia': n, 'n_perms': int(len(perms)),
        'bifolia': [f"{A}|{B}" for A, B in bf],
        'current_facing_nested': float(cur_fac), 'n_facing_pairs': len(fac),
        'current_objA_identity_order': cur_objA,
        'identity_rank_objA': int((scores > scores[identity_row]).sum() + 1),
        'best_objA': best, 'best_sequence': [f"{bf[i][0]}|{bf[i][1]}" for i in perms[best_i]],
        'improvement_vs_facing': best / cur_fac - 1, 'improvement_vs_identity_objA': best / cur_objA - 1,
        'best_objB': float(scoresB.max()), 'objB_improvement_vs_facing': float(scoresB.max() / cur_fac - 1),
        'conjoint_const': conj_const,
        'perm_score_quantiles': {q_: float(np.quantile(scores, float(q_))) for q_ in ['0.05', '0.5', '0.95', '1.0']},
    }
    theirs = {}
    for name, seq_labels in their_seqs.items():
        try:
            seq = tuple(res['bifolia'].index(s) for s in seq_labels)
        except ValueError:
            theirs[name] = {'note': 'sequence contains a dropped bifolium'}; continue
        row = perm_tuples.index(seq); sc = float(scores[row])
        theirs[name] = {'sequence': list(seq_labels), 'objA': sc, 'rank_of_N': int((scores > sc).sum() + 1),
                        'percentile_top': float((scores > sc).sum() + 1) / len(perms),
                        'improvement_vs_facing': sc / cur_fac - 1}
    res['their_sequences'] = theirs
    # Null 1: page-label shuffle within section (present pages only; absent slot stays absent)
    present = np.array(sorted({i for s in slots for i in s if i != absent}))
    null_imp, null_best, null_cur = [], [], []
    for _ in range(n_shuf):
        lab = ident.copy(); lab[present] = rng.permutation(present)
        sc, cf = evaluate(lab)
        null_best.append(sc.max()); null_cur.append(cf); null_imp.append(sc.max() / cf - 1)
    null_imp = np.array(null_imp); null_best = np.array(null_best)
    res['null1_label_shuffle'] = {
        'n': n_shuf, 'improvement_null_mean': float(null_imp.mean()), 'improvement_null_sd': float(null_imp.std()),
        'improvement_null_q05_q50_q95': [float(np.quantile(null_imp, x)) for x in (0.05, 0.5, 0.95)],
        'p_improvement_ge_observed': float(np.mean(null_imp >= res['improvement_vs_facing'])),
        'best_null_mean': float(null_best.mean()), 'p_best_ge_observed': float(np.mean(null_best >= best)),
    }
    # Null 2: exchangeable resample of off-diagonal similarities among present pages
    vals = np.array([S[i, j] for a, i in enumerate(present) for j in present[a + 1:]])
    null_imp2 = []
    iu = np.triu_indices(len(present), 1)
    for _ in range(n_shuf):
        M = np.zeros_like(S)
        R = np.zeros((len(present), len(present))); R[iu] = rng.choice(vals, size=len(iu[0]), replace=True); R = R + R.T
        M[np.ix_(present, present)] = R
        sc = M[JB, JA].mean(axis=1); cf = M[facI, facJ].mean()
        null_imp2.append(sc.max() / cf - 1)
    null_imp2 = np.array(null_imp2)
    res['null2_exchangeable'] = {'n': n_shuf, 'improvement_null_mean': float(null_imp2.mean()),
                                 'improvement_null_q05_q50_q95': [float(np.quantile(null_imp2, x)) for x in (0.05, 0.5, 0.95)],
                                 'p_improvement_ge_observed': float(np.mean(null_imp2 >= res['improvement_vs_facing']))}
    return res


# ----------------------------------------------------------------------------- main
def main():
    rng = np.random.default_rng(SEED)
    pages, docs, lang = load_pages()
    idx = {p: i for i, p in enumerate(pages)}
    tokcount = {p: len(docs[p]) for p in pages}
    sims = build_sims(pages, docs)
    print(f"pages={len(pages)}  sims={list(sims)}", flush=True)
    for q in QUIRES:
        P = quire_pairs(q, idx)
        print(f"  {q}: present={len(P['present'])} conf={len(P['confoliate'])} fac={len(P['facing'])} "
              f"conj={len(P['conjoint'])} other={len(P['other'])}", flush=True)

    target_pages = {pg(n, s) for q in QUIRES for n in leaves(q) for s in 'rv'}
    out = {'phase': 'PHASE_752', 'seed': SEED, 'n_pages_fit': len(pages), 'k_primary': K_PRIMARY,
           'page_languages_target': {p: lang[p] for p in pages if p in target_pages},
           'page_tokens_target': {p: tokcount[p] for p in pages if p in target_pages}}
    Sp = sims[f'k{K_PRIMARY}']
    # ---- Test 1
    print("Test 1 herbal Q1-Q7 ...", flush=True)
    out['test1_herbal_k75'] = test1(Sp, pages, idx, lang, HERBAL, 'herbal Q1-Q7, k=75', rng, tokcount=tokcount)
    print("Test 1 pure-A Q1-Q3 ...", flush=True)
    out['test1_pureA_k75'] = test1(Sp, pages, idx, lang, PURE_A, 'pure-A Q1-Q3, k=75', rng, tokcount=tokcount)
    print("Test 1 mixed Q4-Q7 ...", flush=True)
    out['test1_mixed_k75'] = test1(Sp, pages, idx, lang, ['Q4', 'Q5', 'Q6', 'Q7'], 'mixed Q4-Q7, k=75', rng, tokcount=tokcount)
    for q in BSECT:
        print(f"Test 1 B-arm {q} ...", flush=True)
        out[f'test1_{q}_k75'] = test1(Sp, pages, idx, lang, [q], f'{q}, k=75', rng, tokcount=tokcount)
    out['test1_robustness'] = {}
    for kname, S in sims.items():
        if kname == f'k{K_PRIMARY}':
            continue
        r = test1(S, pages, idx, lang, HERBAL, f'herbal {kname}', rng, n_shuf=2000)
        out['test1_robustness'][kname] = {'stats': r['stats'], 'null': r['null'], 'pooled_means': r['pooled_means']}
    # ---- Test 2
    THEIR = {
        'Q13': {'their_best_12pct': ['77|82', '78|81', '75|84', '76|83', '79|80'],
                'their_second_7pct': ['76|83', '77|82', '79|80', '75|84', '78|81']},
        'Q20': {'their_best_20pct': ['105|114', '104|115', '106|113', '107|112', '108|111', '103|116']},
    }
    for q in BSECT:
        print(f"Test 2 {q} ...", flush=True)
        out[f'test2_{q}_k75'] = test2(Sp, idx, q, THEIR[q], rng, label='k=75 primary')
    print("Test 2 Q20 drop 103|116 ...", flush=True)
    out['test2_Q20_drop103_116_k75'] = test2(Sp, idx, 'Q20', THEIR['Q20'], rng, drop=(103, 116), label='k=75, 103|116 dropped')
    out['test2_robustness'] = {}
    for kname, S in sims.items():
        if kname == f'k{K_PRIMARY}':
            continue
        out['test2_robustness'][kname] = {}
        for q in BSECT:
            r = test2(S, idx, q, THEIR[q], rng, n_shuf=1000, label=kname)
            out['test2_robustness'][kname][q] = {k: r[k] for k in ['current_facing_nested', 'best_objA', 'improvement_vs_facing',
                                                                    'best_sequence', 'their_sequences']}
            out['test2_robustness'][kname][q]['null1_p'] = r['null1_label_shuffle']['p_improvement_ge_observed']
            out['test2_robustness'][kname][q]['null1_q05_q50_q95'] = r['null1_label_shuffle']['improvement_null_q05_q50_q95']
    with open(OUT / 'singulion_tests.json', 'w') as f:
        json.dump(out, f, indent=2, default=float)
    print("written", OUT / 'singulion_tests.json', flush=True)


if __name__ == '__main__':
    main()
