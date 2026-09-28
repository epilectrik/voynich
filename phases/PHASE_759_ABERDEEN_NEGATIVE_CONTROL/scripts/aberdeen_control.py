#!/usr/bin/env python3
"""PHASE_759 — Aberdeen Bestiary negative control for the PHASE_752 bifolium pipeline.

See ../PRE_REGISTRATION.md (locked, commit 84d8339). Pipeline identical to PHASE_752 v1 (TF-IDF \\S+, TruncatedSVD,
cosine). Statistics: residualized T_sheet under the re-pairing null, distance-stratified T_strat, T_face sanity gate,
MDE80, token-level plant, length-matched runs; Voynich comparison unless MISSPECIFICATION.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
OUT = ROOT / 'phases/PHASE_759_ABERDEEN_NEGATIVE_CONTROL/results'
OUT.mkdir(parents=True, exist_ok=True)
SEED = 759
N_NULL = 10_000
MIN_WORDS = 20
K_PRIMARY, K_ROBUST = 75, [50, 100, None]
PRIMARY_Q = ['E', 'F', 'G', 'I', 'K', 'M']
SECONDARY_Q = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'K', 'L', 'M', 'N', 'O', 'P']
Z80 = 1.645 + 0.84


def log(*a):
    print(*a, flush=True)


# ================================================================================================ manuscripts
class MS:
    """pages: {page_id: [tokens]}; quires: {q: {'slots': {slot: leaf}, 'pairs': [(leafA, leafB)]}};
    leaf_pages: {leaf: [(page_id, side)]} with side 0 = recto, 1 = verso."""

    def __init__(self, pages, quires, leaf_pages):
        self.pages = pages
        self.quires = quires
        self.leaf_pages = leaf_pages


def aberdeen():
    recs = json.load(open(ROOT / 'sources/aberdeen_bestiary/aberdeen_pages.json', encoding='utf-8'))
    coll = json.load(open(ROOT / 'sources/aberdeen_bestiary/collation.json', encoding='utf-8'))
    pages = {r['folio']: r['latin_norm'].split() for r in recs if r['n_words'] >= MIN_WORDS}
    quires, leaf_pages = {}, {}
    for q in coll['quires']:
        if q['status'] != 'determined':
            continue
        slots = {int(s): leaf for s, leaf in q['positions'].items() if leaf is not None}
        pairs = [tuple(p) for p in q['conjugate_pairs']]
        quires[q['quire']] = {'slots': slots, 'pairs': pairs}
        for leaf in slots.values():
            if isinstance(leaf, str):                 # '93a' carries f93r, '93b' carries f93v (glued leaves)
                n, half = int(leaf[:-1]), leaf[-1]
                cand = [(f'f{n}r', 0)] if half == 'a' else [(f'f{n}v', 1)]
            else:
                cand = [(f'f{leaf}r', 0), (f'f{leaf}v', 1)]
            leaf_pages[leaf] = [(pid, s) for pid, s in cand if pid in pages]
    return MS(pages, quires, leaf_pages)


V_QUIRES = {'Q1': (1, 8), 'Q2': (9, 16), 'Q3': (17, 24), 'Q13': (75, 84), 'Q20': (103, 116)}
V_MISSING = {12, 109, 110}
V_STRATA = {'pureA_Q1-Q3': ['Q1', 'Q2', 'Q3'], 'Q13': ['Q13'], 'Q20': ['Q20']}


def voynich():
    from scripts.voynich import Transcript
    tx = Transcript()
    docs = defaultdict(list)
    for t in tx.all(h_only=True):
        w = t.word.strip()
        if not w or t.is_uncertain:
            continue
        if not (t.placement.startswith('P') or t.placement.startswith('R')):
            continue
        docs[t.folio].append(w)
    all_docs = dict(docs)
    pages = {p: d for p, d in all_docs.items() if len(d) >= MIN_WORDS}
    quires, leaf_pages = {}, {}
    for q, (a, b) in V_QUIRES.items():
        L = list(range(a, b + 1))
        n = len(L)
        slots = {i + 1: leaf for i, leaf in enumerate(L) if leaf not in V_MISSING}
        pairs = [(L[i], L[n - 1 - i]) for i in range(n // 2) if L[i] not in V_MISSING and L[n - 1 - i] not in V_MISSING]
        quires[q] = {'slots': slots, 'pairs': pairs}
        for leaf in slots.values():
            leaf_pages[leaf] = [(pid, s) for pid, s in ((f'f{leaf}r', 0), (f'f{leaf}v', 1)) if pid in pages]
    return MS(pages, quires, leaf_pages), all_docs


# ================================================================================================ similarity
def similarity(fit_docs, k):
    ids = sorted(fit_docs)
    X = TfidfVectorizer(token_pattern=r'\S+', lowercase=False).fit_transform([' '.join(fit_docs[i]) for i in ids])
    Z = X if k is None else TruncatedSVD(n_components=k, random_state=SEED).fit_transform(X)
    return {p: i for i, p in enumerate(ids)}, cosine_similarity(Z)


# ================================================================================================ pairs
def build_pairs(ms, qs, idx, S):
    """Cross-leaf page pairs of the stratum with covariates and labels."""
    rows = []
    for q in qs:
        Q = ms.quires[q]
        slot_of = {leaf: s for s, leaf in Q['slots'].items()}
        conj = {frozenset(p) for p in Q['pairs']}
        leaves = [Q['slots'][s] for s in sorted(Q['slots'])]
        for la, lb in itertools.combinations(leaves, 2):
            for pa, sa in ms.leaf_pages[la]:
                for pb, sb in ms.leaf_pages[lb]:
                    posa = 2 * (slot_of[la] - 1) + sa
                    posb = 2 * (slot_of[lb] - 1) + sb
                    first, second = ((pa, posa, slot_of[la]), (pb, posb, slot_of[lb])) if posa < posb else \
                                    ((pb, posb, slot_of[lb]), (pa, posa, slot_of[la]))
                    facing = (second[2] == first[2] + 1 and first[1] % 2 == 1 and second[1] % 2 == 0)
                    rows.append({'q': q, 'la': la, 'lb': lb, 'pa': pa, 'pb': pb,
                                 'sim': float(S[idx[pa], idx[pb]]), 'pdist': abs(posa - posb),
                                 'ldist': abs(slot_of[la] - slot_of[lb]),
                                 'wmin': min(len(ms.pages[pa]), len(ms.pages[pb])),
                                 'wmax': max(len(ms.pages[pa]), len(ms.pages[pb])),
                                 'sheet': frozenset((la, lb)) in conj, 'facing': facing})
    for r in rows:
        if r['sheet']:
            r['facing'] = False
    return rows


def residualize(rows, qs, linear_leaf=False):
    y = np.array([r['sim'] for r in rows])
    cols = []
    if linear_leaf:
        cols.append([r['ldist'] for r in rows])
    else:
        cols.append([np.log(r['pdist']) for r in rows])
        cols.append([1.0 if r['pdist'] == 1 else 0.0 for r in rows])
    cols.append([np.log(r['wmin']) for r in rows])
    cols.append([np.log(r['wmax']) for r in rows])
    for q in qs:
        cols.append([1.0 if r['q'] == q else 0.0 for r in rows])
    X = np.column_stack(cols)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    return res, float(res.std(ddof=X.shape[1]))


def matchings(items):
    if not items:
        yield []
        return
    a = items[0]
    for i in range(1, len(items)):
        rest = items[1:i] + items[i + 1:]
        for m in matchings(rest):
            yield [(a, items[i])] + m


def t_sheet_test(ms, qs, rows, res, rng, n_null=N_NULL):
    """Mean residual over sheet page pairs; re-pairing null over leaves in conjugate pairs."""
    lp_sum, lp_cnt = defaultdict(float), defaultdict(int)
    for r, e in zip(rows, res):
        key = (r['q'], frozenset((r['la'], r['lb'])))
        lp_sum[key] += e
        lp_cnt[key] += 1
    paired = {q: [l for p in ms.quires[q]['pairs'] for l in p] for q in qs}
    real = [(q, frozenset(p)) for q in qs for p in ms.quires[q]['pairs']]

    def T(pairs):
        s = sum(lp_sum.get(k, 0.0) for k in pairs)
        c = sum(lp_cnt.get(k, 0) for k in pairs)
        return s / c if c else float('nan')
    t_real = T(real)
    null = np.empty(n_null)
    for i in range(n_null):
        pairs = []
        for q in qs:
            L = list(paired[q])
            rng.shuffle(L)
            pairs.extend((q, frozenset((L[j], L[j + 1]))) for j in range(0, len(L), 2))
        null[i] = T(pairs)
    per_q = {}
    for q in qs:
        L = paired[q]
        if len(L) < 4:
            continue
        vals = [T([(q, frozenset(p)) for p in m]) for m in matchings(list(L))]
        tq = T([(q, frozenset(p)) for p in ms.quires[q]['pairs']])
        per_q[q] = {'T': tq, 'n_matchings': len(vals), 'p_up_exact': float(np.mean([v >= tq - 1e-12 for v in vals]))}
    return {'T': t_real, 'p_up': float((1 + (null >= t_real - 1e-12).sum()) / (1 + n_null)),
            'p_low': float((1 + (null <= t_real + 1e-12).sum()) / (1 + n_null)),
            'null_mean': float(null.mean()), 'null_sd': float(null.std()), 'per_quire': per_q}


def t_strat_test(ms, qs, rows, rng, n_null=N_NULL):
    """Sheet vs non-sheet page pairs at the same leaf distance d in {1,3,5}, within quire."""
    cells = defaultdict(lambda: defaultdict(list))       # (q, d) -> leafpair -> [sims]
    sheets = defaultdict(set)
    for r in rows:
        if r['ldist'] in (1, 3, 5):
            key = frozenset((r['la'], r['lb']))
            cells[(r['q'], r['ldist'])][key].append(r['sim'])
            if r['sheet']:
                sheets[(r['q'], r['ldist'])].add(key)
    usable = [c for c in cells if sheets[c] and len(cells[c]) > len(sheets[c])]

    def stat(choice):
        num = den = 0.0
        for c in usable:
            sel = choice[c]
            s_sims = [x for lp in sel for x in cells[c][lp]]
            o_sims = [x for lp, v in cells[c].items() if lp not in sel for x in v]
            if not s_sims or not o_sims:
                continue
            w = len(s_sims)
            num += w * (np.mean(s_sims) - np.mean(o_sims))
            den += w
        return num / den if den else float('nan')
    t_real = stat({c: sheets[c] for c in usable})
    keys = {c: list(cells[c]) for c in usable}
    null = np.empty(n_null)
    for i in range(n_null):
        choice = {c: set(rng.choice(len(keys[c]), size=len(sheets[c]), replace=False).tolist()) for c in usable}
        null[i] = stat({c: {keys[c][j] for j in choice[c]} for c in usable})
    return {'T': t_real, 'p_up': float((1 + (null >= t_real - 1e-12).sum()) / (1 + n_null)),
            'p_low': float((1 + (null <= t_real + 1e-12).sum()) / (1 + n_null)),
            'null_mean': float(null.mean()), 'null_sd': float(null.std()), 'cells': len(usable)}


def t_face_test(ms, qs, idx, S, rng, n_null=N_NULL):
    """Facing minus other (raw); null permutes page labels among the quire's page positions."""
    quires = []
    for q in qs:
        Q = ms.quires[q]
        slot_of = {leaf: s for s, leaf in Q['slots'].items()}
        conj = {frozenset(p) for p in Q['pairs']}
        pos = []                                          # (page_id, leaf, slot, side)
        for leaf in (Q['slots'][s] for s in sorted(Q['slots'])):
            for pid, side in ms.leaf_pages[leaf]:
                pos.append((pid, leaf, slot_of[leaf], side))
        fac, oth = [], []
        for i, j in itertools.combinations(range(len(pos)), 2):
            a, b = pos[i], pos[j]
            if a[1] == b[1] or frozenset((a[1], b[1])) in conj:
                continue
            first, second = (a, b) if (2 * a[2] + a[3]) < (2 * b[2] + b[3]) else (b, a)
            if second[2] == first[2] + 1 and first[3] == 1 and second[3] == 0:
                fac.append((i, j))
            else:
                oth.append((i, j))
        quires.append(([idx[p[0]] for p in pos], fac, oth))

    def stat(perms):
        fs, os_ = [], []
        for (ids, fac, oth), perm in zip(quires, perms):
            ids = [ids[k] for k in perm]
            fs.extend(S[ids[i], ids[j]] for i, j in fac)
            os_.extend(S[ids[i], ids[j]] for i, j in oth)
        return float(np.mean(fs) - np.mean(os_))
    t_real = stat([list(range(len(ids))) for ids, _, _ in quires])
    null = np.array([stat([rng.permutation(len(ids)).tolist() for ids, _, _ in quires]) for _ in range(n_null)])
    return {'T': t_real, 'p_up': float((1 + (null >= t_real).sum()) / (1 + n_null)), 'null_mean': float(null.mean())}


def run_stratum(ms, fit_docs, qs, k, rng, n_null=N_NULL, with_face=True, linear_diag=True):
    idx, S = similarity(fit_docs, k)
    rows = build_pairs(ms, qs, idx, S)
    res, rsd = residualize(rows, qs)
    ts = t_sheet_test(ms, qs, rows, res, rng, n_null)
    tt = t_strat_test(ms, qs, rows, rng, n_null)
    out = {'k': k, 'n_pairs': len(rows), 'n_sheet_pairs': sum(r['sheet'] for r in rows), 'resid_sd': rsd,
           'T_sheet': ts, 'T_strat': tt,
           'T_sheet_resid_sd_units': ts['T'] / rsd, 'T_strat_resid_sd_units': tt['T'] / rsd,
           'MDE80_T_sheet_resid_sd': Z80 * ts['null_sd'] / rsd, 'MDE80_T_strat_resid_sd': Z80 * tt['null_sd'] / rsd,
           'distance_slope_raw': float(np.polyfit([r['pdist'] for r in rows], [r['sim'] for r in rows], 1)[0]),
           'raw_sheet_minus_other': float(np.mean([r['sim'] for r in rows if r['sheet']]) -
                                          np.mean([r['sim'] for r in rows if not r['sheet'] and not r['facing']]))}
    if with_face:
        out['T_face'] = t_face_test(ms, qs, idx, S, rng, n_null)
    if linear_diag:
        res_l, rsd_l = residualize(rows, qs, linear_leaf=True)
        out['diagnostic_linear_leaf_model_T_sheet'] = t_sheet_test(ms, qs, rows, res_l, rng, 2000)
    return out


def plant(ms, fit_docs, qs, rng):
    """Token-level plant: 10% of each page's length, drawn from the conjugate leaf's pages, appended."""
    docs = {p: list(v) for p, v in fit_docs.items()}
    for q in qs:
        for la, lb in ms.quires[q]['pairs']:
            for src, dst in ((lb, la), (la, lb)):
                pool = [w for pid, _ in ms.leaf_pages[src] for w in ms.pages[pid]]
                if not pool:
                    continue
                for pid, _ in ms.leaf_pages[dst]:
                    n = max(1, round(0.1 * len(ms.pages[pid])))
                    docs[pid] = docs[pid] + [pool[i] for i in rng.integers(0, len(pool), n)]
    ms2 = MS({p: docs[p] for p in ms.pages}, ms.quires, ms.leaf_pages)
    out = {}
    for k in (K_PRIMARY, None):
        base = run_stratum(ms, fit_docs, qs, k, np.random.default_rng(SEED), 2000, False, False)
        pl = run_stratum(ms2, docs, qs, k, np.random.default_rng(SEED), 2000, False, False)
        out['raw' if k is None else f'k{k}'] = {
            'T_sheet_shift_resid_sd': pl['T_sheet_resid_sd_units'] - base['T_sheet_resid_sd_units'],
            'T_strat_shift_resid_sd': pl['T_strat_resid_sd_units'] - base['T_strat_resid_sd_units'],
            'planted_p_up_T_sheet': pl['T_sheet']['p_up'], 'planted_p_up_T_strat': pl['T_strat']['p_up']}
    return out


def length_matched(ms, fit_docs, qs, target_lengths, seeds):
    reps = []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        cut = {}
        for p, toks in fit_docs.items():
            L = int(target_lengths[rng.integers(len(target_lengths))])
            if len(toks) > L:
                o = int(rng.integers(0, len(toks) - L + 1))
                cut[p] = toks[o:o + L]
            else:
                cut[p] = list(toks)
        ms2 = MS({p: cut[p] for p in ms.pages}, ms.quires, ms.leaf_pages)
        r = run_stratum(ms2, cut, qs, K_PRIMARY, rng, N_NULL, False, False)
        reps.append({'p_up_T_sheet': r['T_sheet']['p_up'], 'p_up_T_strat': r['T_strat']['p_up'],
                     'p_low_T_sheet': r['T_sheet']['p_low'], 'p_low_T_strat': r['T_strat']['p_low'],
                     'MDE80_T_sheet': r['MDE80_T_sheet_resid_sd'], 'MDE80_T_strat': r['MDE80_T_strat_resid_sd']})
    med = {k: float(np.median([x[k] for x in reps])) for k in reps[0]}
    return {'replicates': reps, 'median': med}


# ================================================================================================ main
def main():
    t0 = time.time()
    ab = aberdeen()
    ab_fit = dict(ab.pages)
    log(f"Aberdeen: {len(ab.pages)} text pages; quires {sorted(ab.quires)}")
    rng = np.random.default_rng(SEED)
    out = {'phase': 'PHASE_759', 'pre_registration_commit': '84d8339'}
    prim = run_stratum(ab, ab_fit, PRIMARY_Q, K_PRIMARY, rng)
    out['aberdeen_primary'] = prim
    log(f"PRIMARY k75: T_sheet {prim['T_sheet']['T']:+.4f} p_up {prim['T_sheet']['p_up']:.4f} p_low {prim['T_sheet']['p_low']:.4f} | "
        f"T_strat {prim['T_strat']['T']:+.4f} p_up {prim['T_strat']['p_up']:.4f} p_low {prim['T_strat']['p_low']:.4f} | "
        f"T_face {prim['T_face']['T']:+.4f} p {prim['T_face']['p_up']:.4f} | MDE80 sheet {prim['MDE80_T_sheet_resid_sd']:.3f} "
        f"strat {prim['MDE80_T_strat_resid_sd']:.3f} (resid-SD units) | slope {prim['distance_slope_raw']:+.5f}")
    out['aberdeen_primary_robust'] = {}
    for k in K_ROBUST:
        r = run_stratum(ab, ab_fit, PRIMARY_Q, k, np.random.default_rng(SEED), N_NULL, True, False)
        out['aberdeen_primary_robust']['raw' if k is None else f'k{k}'] = r
        log(f"  robust {k}: T_sheet p_up {r['T_sheet']['p_up']:.4f} p_low {r['T_sheet']['p_low']:.4f}; "
            f"T_strat p_up {r['T_strat']['p_up']:.4f} p_low {r['T_strat']['p_low']:.4f}; T_face p {r['T_face']['p_up']:.4f}")
    sec = run_stratum(ab, ab_fit, SECONDARY_Q, K_PRIMARY, np.random.default_rng(SEED))
    out['aberdeen_secondary'] = sec
    log(f"SECONDARY: T_sheet p_up {sec['T_sheet']['p_up']:.4f} p_low {sec['T_sheet']['p_low']:.4f}; "
        f"T_strat p_up {sec['T_strat']['p_up']:.4f} p_low {sec['T_strat']['p_low']:.4f}; T_face p {sec['T_face']['p_up']:.4f}")
    out['plant'] = plant(ab, ab_fit, PRIMARY_Q, np.random.default_rng(SEED))
    log(f"plant: {out['plant']}")

    # Voynich page lengths per stratum (for length-matched runs) and the comparison
    vms, v_all = voynich()
    lens = {s: [len(vms.pages[pid]) for q in qs for leaf in vms.quires[q]['slots'].values()
                for pid, _ in vms.leaf_pages[leaf]] for s, qs in V_STRATA.items()}
    out['voynich_page_lengths'] = {s: {'n': len(v), 'median': float(np.median(v))} for s, v in lens.items()}
    out['length_matched'] = {}
    for s, L in lens.items():
        out['length_matched'][s] = length_matched(ab, ab_fit, PRIMARY_Q, np.array(L), range(7590, 7610))
        log(f"length-matched to {s} (median {np.median(L):.0f} words): {out['length_matched'][s]['median']}")

    misspec = prim['T_sheet']['p_low'] < 0.05 or prim['T_strat']['p_low'] < 0.05
    face_fail = prim['T_face']['p_up'] >= 0.01
    nonspec = (prim['T_sheet']['p_up'] < 0.05 or prim['T_strat']['p_up'] < 0.05 or
               any(v['median']['p_up_T_sheet'] < 0.01 or v['median']['p_up_T_strat'] < 0.01
                   for v in out['length_matched'].values()))
    out['voynich'] = {}
    if not misspec:
        for s, qs in V_STRATA.items():
            r = run_stratum(vms, v_all, qs, K_PRIMARY, np.random.default_rng(SEED), N_NULL, True, False)
            out['voynich'][s] = r
            log(f"VOYNICH {s}: T_sheet {r['T_sheet_resid_sd_units']:+.3f} SD p_up {r['T_sheet']['p_up']:.4f}; "
                f"T_strat {r['T_strat_resid_sd_units']:+.3f} SD p_up {r['T_strat']['p_up']:.4f}; T_face p {r['T_face']['p_up']:.4f}")
    underpowered = False
    if not misspec and not face_fail and not nonspec:
        for s, r in out['voynich'].items():
            for stat, mkey in (('T_sheet', 'MDE80_T_sheet'), ('T_strat', 'MDE80_T_strat')):
                if r[stat]['p_up'] < 0.01:
                    eff = r[f'{stat}_resid_sd_units']
                    mde = max(prim[f'MDE80_{stat}_resid_sd'], out['length_matched'][s]['median'][mkey])
                    if mde > eff:
                        underpowered = True
    if misspec:
        verdict = 'MISSPECIFICATION'
    elif face_fail:
        verdict = 'POSITIVE-CONTROL FAIL'
    elif nonspec:
        verdict = 'NON-SPECIFIC'
    elif underpowered:
        verdict = 'INCONCLUSIVE-UNDERPOWERED'
    else:
        verdict = 'SPECIFIC'
    out['verdict'] = verdict
    out['runtime_s'] = round(time.time() - t0, 1)

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        return o
    json.dump(clean(out), open(OUT / 'aberdeen_control.json', 'w', encoding='utf-8'), indent=1)
    log(f"VERDICT (locked rules): {verdict}  ({out['runtime_s']}s)")


if __name__ == '__main__':
    main()
