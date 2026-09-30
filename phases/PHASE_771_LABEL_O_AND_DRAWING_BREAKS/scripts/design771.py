#!/usr/bin/env python3
"""PHASE_771 design stage: sample sizes, reference distributions and power. Blind by construction:
- labels: only counts (token totals, o-initial and qo-initial counts); the glyph after a label's initial 'o' is NOT read;
- drawing breaks: only counts and within-line positions; the glyphs of the tokens next to a break are NOT read.
References are built from paragraph text alone (labels) and from lines without a drawing break (breaks).
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import zl771 as Z  # noqa: E402

OUT = Z.ROOT / 'phases/PHASE_771_LABEL_O_AND_DRAWING_BREAKS/results'
OUT.mkdir(parents=True, exist_ok=True)
SEED = 771

CATS = ['k', 't', 'l', 'r', 'd', 'a', 'e', 'o', 'y', 's', 'ch', 'sh', 'pf', 'bench', 'minim', 'q', 'other']


def cat(u):
    if u in ('k', 't', 'l', 'r', 'd', 'a', 'e', 'o', 'y', 's', 'ch', 'sh', 'q'):
        return u
    if u in ('p', 'f'):
        return 'pf'
    if u in ('cth', 'ckh', 'cph', 'cfh'):
        return 'bench'
    if u.startswith('i'):
        return 'minim'
    return 'other'


def dist(counter, smooth=0.5):
    v = np.array([counter.get(c, 0) for c in CATS], float) + smooth
    return v / v.sum()


def jsd(p, q):
    m = 0.5 * (p + q)
    kl = lambda a, b: float(np.sum(a * np.log2(a / b)))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def em_weights(x_idx, comps, iters=300):
    """Mixture weights over fixed component distributions (rows of comps) for category indices x_idx."""
    L = comps[:, x_idx]                                   # K x N likelihoods
    w = np.full(comps.shape[0], 1 / comps.shape[0])
    for _ in range(iters):
        r = w[:, None] * L
        r /= r.sum(0, keepdims=True)
        w = r.mean(1)
    return w


def label_arm(recs):
    tot = Counter()
    by = defaultdict(Counter)
    refs = {k: defaultdict(Counter) for k in ('A', 'B', 'all')}
    for r in recs:
        words = [w for seg in r['segments'] for w, _ in seg]
        if r['kind'].startswith('L'):
            grp = (r['kind'], r['section'], r['lang'])
            for w in words:
                tot['label_tokens'] += 1
                if not Z.readable(w):
                    continue
                tot['label_readable'] += 1
                by[grp]['readable'] += 1
                if w.startswith('qo'):
                    by[grp]['qo_initial'] += 1
                elif w.startswith('o') and len(w) > 1:
                    by[grp]['o_initial'] += 1          # counted only; what follows the 'o' is not read here
        elif r['kind'].startswith('P'):
            for w in words:
                if not Z.readable(w):
                    continue
                u = Z.units(w)
                for key in (r['lang'], 'all'):
                    if key not in refs:
                        continue
                    refs[key]['init'][cat(u[0])] += 1
                    if w.startswith('qo') and len(u) > 2:
                        refs[key]['qo'][cat(u[2])] += 1
                    elif u[0] == 'o' and len(u) > 1:
                        refs[key]['o'][cat(u[1])] += 1
    n_o = sum(c['o_initial'] for c in by.values())
    out = {'totals': dict(tot), 'o_initial_labels': n_o,
           'by_kind_section_lang': {'|'.join(k): dict(v) for k, v in sorted(by.items())}}
    D = {}
    for key, rr in refs.items():
        ds = {n: dist(rr[n]) for n in ('qo', 'o', 'init')}
        D[key] = ds
        out[f'ref_{key}'] = {n: {c: round(float(p), 4) for c, p in zip(CATS, ds[n])} for n in ds}
        out[f'ref_{key}_n'] = {n: int(sum(rr[n].values())) for n in ds}
        out[f'jsd_{key}'] = {'qo_o': round(jsd(ds['qo'], ds['o']), 4), 'qo_init': round(jsd(ds['qo'], ds['init']), 4),
                             'o_init': round(jsd(ds['o'], ds['init']), 4)}
    # quick iid separability check: expected per-observation log-likelihood advantage of the true reference
    comps = {n: D['all'][n] for n in ('qo', 'o', 'init')}
    sep = {}
    for t in comps:
        for a in comps:
            if a != t:
                sep[f'{t}_vs_{a}_bits_per_obs'] = round(float(np.sum(comps[t] * np.log2(comps[t] / comps[a]))), 3)
    out['kl_separability_all'] = sep
    return out


def break_arm(recs):
    counts = Counter()
    by = Counter()
    post_idx, pre_idx = Counter(), Counter()
    first_init, first_mid, last_fin, last_mid = (defaultdict(Counter) for _ in range(4))
    for r in recs:
        if not r['kind'].startswith('P') or r['lang'] not in ('A', 'B'):
            continue
        segs = [s for s in r['segments']]
        if len(segs) > 1:
            n_line = sum(len(s) for s in segs)
            before = 0
            for j in range(len(segs) - 1):
                before += len(segs[j])
                left, right = segs[j], segs[j + 1]
                counts['breaks'] += 1
                if not left or not right:
                    counts['empty_side'] += 1
                    continue
                pre_w, post_w = left[-1][0], right[0][0]
                if not (Z.readable(pre_w) and Z.readable(post_w)):
                    counts['unreadable_side'] += 1
                    continue
                counts['usable'] += 1
                by[(r['lang'], r['section'])] += 1
                post_idx[min(before, 8)] += 1                       # tokens before the post-break word
                pre_idx[min(n_line - before, 8)] += 1               # tokens from the pre-break word to line end
            continue
        words = [w for w, _ in segs[0]]
        if len(words) < 3:
            continue
        lang = r['lang']
        for i, w in enumerate(words):
            if not Z.readable(w):
                continue
            u = Z.units(w)
            if i == 0:
                first_init[lang][u[0]] += 1
            elif i < len(words) - 1:
                first_mid[lang][u[0]] += 1
                last_mid[lang][u[-1]] += 1
            if i == len(words) - 1:
                last_fin[lang][u[-1]] += 1
    out = {'counts': dict(counts), 'usable_by_lang_section': {'|'.join(k): v for k, v in sorted(by.items())},
           'post_break_tokens_before': dict(sorted(post_idx.items())),
           'pre_break_tokens_to_end': dict(sorted(pre_idx.items()))}
    # separation of line-edge glyph models on unbroken lines (design information only)
    for lang in ('A', 'B'):
        sep = {}
        for name, e, m in (('start', first_init[lang], first_mid[lang]), ('end', last_fin[lang], last_mid[lang])):
            keys = sorted(set(e) | set(m))
            pe = {k: (e[k] + 0.5) / (sum(e.values()) + 0.5 * len(keys)) for k in keys}
            pm = {k: (m[k] + 0.5) / (sum(m.values()) + 0.5 * len(keys)) for k in keys}
            llr = {k: np.log(pe[k] / pm[k]) for k in keys}
            top = sorted(keys, key=lambda k: -llr[k])[:6]
            # AUC of the unit-level LLR score between edge tokens and mid tokens (in-sample, design only)
            se = np.repeat([llr[k] for k in keys], [e[k] for k in keys])
            sm = np.repeat([llr[k] for k in keys], [m[k] for k in keys])
            rng = np.random.default_rng(SEED)
            a = rng.choice(se, 4000)
            b = rng.choice(sm, 4000)
            auc = float(np.mean(a[:, None] > b[None, :1000]) + 0.5 * np.mean(a[:, None] == b[None, :1000]))
            sep[name] = {'n_edge': int(sum(e.values())), 'n_mid': int(sum(m.values())), 'auc_in_sample': round(auc, 3),
                         'mean_llr_edge': round(float(se.mean()), 3), 'mean_llr_mid': round(float(sm.mean()), 3),
                         'top_edge_units': {k: [e[k], m[k], round(float(llr[k]), 2)] for k in top}}
        out[f'edge_models_{lang}'] = sep
    return out


def main():
    recs = Z.load()
    res = {'labels': label_arm(recs), 'breaks': break_arm(recs)}
    (OUT / 'design_counts.json').write_text(json.dumps(res, indent=1))
    L, B = res['labels'], res['breaks']
    print('LABELS', L['totals'], 'o-initial:', L['o_initial_labels'])
    for k in ('A', 'B', 'all'):
        print(' ref', k, L[f'ref_{k}_n'], 'JSD', L[f'jsd_{k}'])
    print(' separability', L['kl_separability_all'])
    print('BREAKS', B['counts'])
    print(' by lang|section', B['usable_by_lang_section'])
    print(' post-break index', B['post_break_tokens_before'], ' pre-break to end', B['pre_break_tokens_to_end'])
    for lang in ('A', 'B'):
        print(' edge models', lang, json.dumps(B[f'edge_models_{lang}']))


if __name__ == '__main__':
    main()
