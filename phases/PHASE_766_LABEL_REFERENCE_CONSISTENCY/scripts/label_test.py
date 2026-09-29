#!/usr/bin/env python3
"""PHASE_766: label-page consistency test (pre-registration locked at 0b24813).

Stage 1 (power) uses no real pairing: labels are scored against surrogate herbal pages with planted label words.
Stage 2 runs the primary test and variants V1-V8 on the 13 real pairs. Stage 3 writes descriptives.
"""
from __future__ import annotations

import itertools
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab766 as L  # noqa: E402

OUT = L.ROOT / 'phases/PHASE_766_LABEL_REFERENCE_CONSISTENCY/results'
OUT.mkdir(parents=True, exist_ok=True)
SEED = 766
NPERM = 100_000
NPERM_POWER = 10_000
DRAWS = 200
ALPHA = 0.05
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


# ================================================================================================ scoring machinery
class Scorer:
    """Distances from label words to page tokens and the surprisal calibration over the reference set R."""

    def __init__(self, page_tokens, R, words, unit):
        # page_tokens: page -> list of unit tuples; R: list of pages; words: list of unit tuples
        self.R = list(R)
        self.nR = len(self.R)
        self.words = list(dict.fromkeys(words))
        self.unit = unit
        self.page_tokens = page_tokens
        types = sorted({t for p in self.R for t in page_tokens[p]})
        self._dtype = {w: {t: L.edit_distance(w, t) for t in types} for w in self.words}
        # per-token distance arrays, per word and page
        self.pertok = {w: {p: np.array([self._dtype[w][t] for t in page_tokens[p]], dtype=np.int8)
                           for p in self.R} for w in self.words}
        self.dmin = {w: {p: int(a.min()) if len(a) else 3 for p, a in self.pertok[w].items()} for w in self.words}
        self.counts = {w: self._counts(self.dmin[w].values()) for w in self.words}

    @staticmethod
    def _counts(ds):
        c = Counter(ds)
        return [c[0], c[0] + c[1], c[0] + c[1] + c[2]]          # #{r: d <= 0}, <= 1, <= 2

    def h_word(self, w, d, counts=None):
        if d > 2:
            return 0.0
        n = (counts or self.counts[w])[d]
        return -math.log2((1 + n) / (1 + self.nR))

    def h(self, label_words, page, dmin=None, counts=None):
        best = 0.0
        for w in label_words:
            d = (dmin or self.dmin)[w][page]
            v = self.h_word(w, d, None if counts is None else counts[w])
            if v > best:
                best = v
        return best


def matrix(scorer, labels, slots):
    return np.array([[scorer.h(labels[i], slots[j]) for j in range(len(slots))] for i in range(len(labels))])


def perm_p(H, nperm, rng):
    n = H.shape[0]
    t_obs = float(np.trace(H))
    perms = rng.permuted(np.tile(np.arange(n), (nperm, 1)), axis=1)
    t_perm = H[np.arange(n)[None, :], perms].sum(axis=1)
    ge = int((t_perm >= t_obs - 1e-9).sum())
    return t_obs, (1 + ge) / (1 + nperm), float(t_perm.mean())


def exact_p(H, groups):
    """Exact permutation p over permutations within index groups (identity included)."""
    n = H.shape[0]
    t_obs = float(np.trace(H))
    per_group = [list(itertools.permutations(g)) for g in groups]
    ge = total = 0
    for combo in itertools.product(*per_group):
        perm = list(range(n))
        for g, pg in zip(groups, combo):
            for a, b in zip(g, pg):
                perm[a] = b
        t = sum(H[i, perm[i]] for i in range(n))
        total += 1
        ge += t >= t_obs - 1e-9
    return t_obs, ge / total, total


# ================================================================================================ data
def build(unit='GLYPH', text='ZL', first_line=False, with_jar=False, pair_filter=None):
    pages = L.load_pages()
    R = L.herbal_pages(pages)
    if text == 'ZL':
        src = {p: pages[p]['lines'] for p in R}
    else:
        H = L.load_h_pages()
        src = {p: H[p] for p in R}
    if first_line:
        src = {p: (lines[:1] if lines else []) for p, lines in src.items()}
    page_tokens = {p: [L.units(w, unit) for line in src[p] for w in line] for p in R}
    pairs = [x for x in L.PAIRS if (pair_filter is None or x[0] in pair_filter)]
    labels = [[L.units(w, unit) for w in L.label_words(it, with_jar=with_jar)] for it, *_ in pairs]
    slots = [hp for _, _, hp, _ in pairs]
    words = [w for lab in labels for w in lab]
    return pages, R, page_tokens, pairs, labels, slots, Scorer(page_tokens, R, words, unit)


# ================================================================================================ stage 1: power
def power(pages, R, page_tokens, pairs, labels, slots, sc):
    rng = np.random.default_rng(SEED)
    matched = list(dict.fromkeys(slots))
    ntok = {p: len(page_tokens[p]) for p in R}
    lo, hi = min(ntok[p] for p in matched), max(ntok[p] for p in matched)
    pools = {lang: [p for p in R if p not in matched and pages[p]['L'] == lang and lo <= ntok[p] <= hi]
             for lang in ('A', 'B')}
    log(f'power: token range {lo}-{hi}; pools A={len(pools["A"])} B={len(pools["B"])}; matched langs',
        Counter(pages[p]['L'] for p in matched))
    unit_freq = Counter(u for p in R for t in page_tokens[p] for u in t)
    units_list = list(unit_freq)
    probs = np.array([unit_freq[u] for u in units_list], dtype=float)
    probs /= probs.sum()
    longest = [max(lab, key=len) for lab in labels]
    n = len(labels)

    def substitute(w):
        pos = int(rng.integers(len(w)))
        while True:
            u = units_list[int(rng.choice(len(units_list), p=probs))]
            if u != w[pos]:
                return w[:pos] + (u,) + w[pos + 1:]

    res = {}
    for form in ('a', 'b'):
        for k in range(0, n + 1):
            if form == 'b' and k == 0:
                res[f'b_{k}'] = res['a_0']
                continue
            hits = 0
            for _ in range(DRAWS):
                # surrogate assignment: one surrogate per distinct matched page, same language, without replacement
                sur = {}
                for lang in ('A', 'B'):
                    need = [p for p in matched if pages[p]['L'] == lang]
                    pick = rng.choice(len(pools[lang]), size=len(need), replace=False)
                    for p, j in zip(need, pick):
                        sur[p] = pools[lang][int(j)]
                sslots = [sur[p] for p in slots]
                planted = sorted(rng.choice(n, size=k, replace=False).tolist()) if k else []
                # modifications per surrogate page: list of (position, word)
                mods = {}
                for i in planted:
                    v = longest[i] if form == 'a' else substitute(longest[i])
                    mods.setdefault(sslots[i], []).append(v)
                dmin = sc.dmin
                counts = None
                if mods:
                    dmin = {w: dict(sc.dmin[w]) for w in sc.words}
                    counts = {}
                    for p, vs in mods.items():
                        pos = rng.choice(ntok[p], size=len(vs), replace=False)
                        for w in sc.words:
                            arr = sc.pertok[w][p].copy()
                            for q, v in zip(pos, vs):
                                arr[int(q)] = L.edit_distance(w, v)
                            dmin[w][p] = int(arr.min())
                    for w in sc.words:
                        counts[w] = Scorer._counts(dmin[w].values())
                Hm = np.array([[sc.h(labels[i], sslots[j], dmin=dmin, counts=counts) for j in range(n)]
                               for i in range(n)])
                _, p, _ = perm_p(Hm, NPERM_POWER, rng)
                hits += p <= ALPHA
            res[f'{form}_{k}'] = hits / DRAWS
            log(f'power form {form} k={k:2d}: {hits / DRAWS:.3f}')
    mde = {}
    for form in ('a', 'b'):
        ks = [k for k in range(1, n + 1) if res[f'{form}_{k}'] >= 0.80]
        mde[form] = min(ks) if ks else None
    # per label: h of an exact plant and its percentile among the label's h over R
    per_label = []
    for i, (it, *_rest) in enumerate(pairs):
        w = longest[i]
        n0 = sc.counts[w][0]
        h_exact = -math.log2((2 + n0) / (1 + sc.nR))
        hs = np.array([sc.h(labels[i], r) for r in R])
        per_label.append({'item': it, 'word': ''.join(w), 'units': len(w), 'pages_with_exact': n0,
                          'h_exact_plant': round(h_exact, 3),
                          'pct_R_below': round(float((hs < h_exact - 1e-9).mean()), 3),
                          'pct_R_at_or_above': round(float((hs >= h_exact - 1e-9).mean()), 3)})
    return {'rates': res, 'MDE80_a': mde['a'], 'MDE80_b': mde['b'], 'token_range': [lo, hi],
            'pools': {k: len(v) for k, v in pools.items()}, 'per_label_exact_plant': per_label}


# ================================================================================================ stage 2/3
def primary_and_descriptives(pages, R, page_tokens, pairs, labels, slots, sc):
    rng = np.random.default_rng(SEED)
    Hm = matrix(sc, labels, slots)
    t_obs, p, t_mean = perm_p(Hm, NPERM, rng)
    out = {'T_obs': round(t_obs, 4), 'p': p, 'T_perm_mean': round(t_mean, 4), 'H_diag': [round(x, 3) for x in np.diag(Hm)]}
    # leave-one-pair-out and leave-f96v-out
    loo = []
    for drop in range(len(pairs)):
        keep = [i for i in range(len(pairs)) if i != drop]
        _, pl, _ = perm_p(Hm[np.ix_(keep, keep)], NPERM, rng)
        loo.append({'dropped_item': pairs[drop][0], 'p': pl})
    out['leave_one_out'] = loo
    keep = [i for i, x in enumerate(pairs) if x[2] != 'f96v']
    _, pf, _ = perm_p(Hm[np.ix_(keep, keep)], NPERM, rng)
    out['leave_f96v_out_p'] = pf
    # per pair
    per = []
    for i, (it, pf_, hp, cls) in enumerate(pairs):
        best = None
        for w in labels[i]:
            d = sc.dmin[w][hp]
            toks = sorted({''.join(t) for t in page_tokens[hp] if L.edit_distance(w, t) == d}) if d <= 2 else []
            cand = (sc.h_word(w, d), -d, ''.join(w), d, toks[:5], sc.counts[w][d] if d <= 2 else None)
            if best is None or cand > best:
                best = cand
        row_rank = float((Hm[i] < Hm[i, i] - 1e-9).mean())
        per.append({'item': it, 'page': hp, 'match': cls, 'h': round(best[0], 3), 'label_word': best[2], 'd': best[3],
                    'best_tokens': best[4], 'R_pages_reaching_d': best[5],
                    'pct_slots_below_matched': round(row_rank, 3)})
    out['per_pair'] = per
    out['pairs_exact_or_ed1'] = sum(1 for x in per if x['d'] <= 1)
    return Hm, out


def label_pair_distance(labels, pairs):
    """Glyph-unit edit distance between labels 94 and 116, ranked among all 78 label pairs (no herbal text)."""
    idx = {it: i for i, (it, *_r) in enumerate(pairs)}
    dist = {}
    for a, b in itertools.combinations(range(len(labels)), 2):
        dist[(a, b)] = min(L.full_edit_distance(x, y) for x in labels[a] for y in labels[b])
    vals = np.array(list(dist.values()))
    d94 = dist[tuple(sorted((idx[94], idx[116])))]
    rank_mid = float((vals < d94).sum() + ((vals == d94).sum() + 1) / 2)
    return {'d_94_116': int(d94), 'midrank_among_78': rank_mid, 'n_pairs': int(len(vals)),
            'n_pairs_closer': int((vals < d94).sum()), 'n_ties': int((vals == d94).sum() - 1),
            'median_d': float(np.median(vals))}


def draft_statistic(page_tokens, labels, slots, rng):
    """V7: max over label words and page tokens of 1 - ED / max(len), glyph units."""
    n = len(labels)
    Hm = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            best = 0.0
            for w in labels[i]:
                for t in set(page_tokens[slots[j]]):
                    s = 1 - L.full_edit_distance(w, t) / max(len(w), len(t))
                    if s > best:
                        best = s
            Hm[i, j] = best
    return perm_p(Hm, NPERM, rng)


def variant(name, **kw):
    pages, R, page_tokens, pairs, labels, slots, sc = build(**kw)
    Hm = matrix(sc, labels, slots)
    rng = np.random.default_rng(SEED)
    t, p, m = perm_p(Hm, NPERM, rng)
    log(f'{name}: T={t:.3f} p={p:.4f} (perm mean {m:.3f}; {len(pairs)} pairs)')
    return {'T_obs': round(t, 4), 'p': p, 'T_perm_mean': round(m, 4), 'n_pairs': len(pairs)}


def main():
    log('build primary')
    pages, R, page_tokens, pairs, labels, slots, sc = build()
    log(f'R={len(R)} pages; {len(pairs)} pairs; {len(sc.words)} label words')
    results = {'pre_registration': '0b24813', 'R_size': len(R)}

    log('stage 1: power (no real pairing)')
    results['power'] = power(pages, R, page_tokens, pairs, labels, slots, sc)
    json.dump(results, open(OUT / 'label_test_interim.json', 'w'), indent=1)
    log('MDE80(a) =', results['power']['MDE80_a'], '| MDE80(b) =', results['power']['MDE80_b'])

    log('stage 2: primary test')
    Hm, prim = primary_and_descriptives(pages, R, page_tokens, pairs, labels, slots, sc)
    results['primary'] = prim
    log(f'primary: T={prim["T_obs"]} p={prim["p"]:.4f} (perm mean {prim["T_perm_mean"]})')

    # V1 same-plant pairs, exact
    same = [i for i, x in enumerate(pairs) if x[3] == 'same']
    t1, p1, n1 = exact_p(Hm[np.ix_(same, same)], [list(range(len(same)))])
    results['V1_same_exact'] = {'T_obs': round(t1, 4), 'p': p1, 'n_perms': n1}
    log(f'V1: T={t1:.3f} p={p1:.4f} ({n1} perms)')
    # V8 restricted within pharma-folio groups, exact
    grp = {'f99': [], 'f100': [], 'f102': []}
    for i, (it, pf, hp, cls) in enumerate(pairs):
        for g in grp:
            if pf.startswith(g + 'r') or pf.startswith(g + 'v'):
                grp[g].append(i)
    t8, p8, n8 = exact_p(Hm, [grp['f99'], grp['f100'], grp['f102']])
    results['V8_restricted_exact'] = {'T_obs': round(t8, 4), 'p': p8, 'n_perms': n8,
                                      'groups': {g: [pairs[i][0] for i in v] for g, v in grp.items()}}
    log(f'V8: T={t8:.3f} p={p8:.4f} ({n8} perms)')
    results['V2_jar'] = variant('V2 jar labels', with_jar=True)
    results['V3_no203'] = variant('V3 no item 203', pair_filter={x[0] for x in L.PAIRS} - {203})
    results['V4_first_line'] = variant('V4 first line', first_line=True)
    results['V5_H_track'] = variant('V5 H-track', text='H')
    results['V6_EVA'] = variant('V6 EVA', unit='EVA')
    t7, p7, m7 = draft_statistic(page_tokens, labels, slots, np.random.default_rng(SEED))
    results['V7_draft_statistic'] = {'T_obs': round(t7, 4), 'p': p7, 'T_perm_mean': round(m7, 4)}
    log(f'V7: T={t7:.3f} p={p7:.4f}')

    results['labels_94_116'] = label_pair_distance(labels, pairs)
    log('labels 94/116:', results['labels_94_116'])

    # decision
    p = prim['p']
    mde_a = results['power']['MDE80_a']
    if p <= ALPHA:
        verdict = 'ABOVE NULL'
    elif mde_a is not None and mde_a <= 4:
        verdict = 'NO SIGNAL (bounded)'
    else:
        verdict = 'UNINFORMATIVE'
    loo_flip = [x['dropped_item'] for x in prim['leave_one_out'] if (x['p'] <= ALPHA) != (p <= ALPHA)]
    results['verdict'] = verdict
    results['single_pair_driven'] = loo_flip
    results['runtime_s'] = round(time.time() - T0, 1)
    json.dump(results, open(OUT / 'label_test.json', 'w'), indent=1)
    log(f'VERDICT: {verdict} (p={p:.4f}, MDE80(a)={mde_a}, MDE80(b)={results["power"]["MDE80_b"]}); '
        f'LOO flips: {loo_flip}')


if __name__ == '__main__':
    main()
