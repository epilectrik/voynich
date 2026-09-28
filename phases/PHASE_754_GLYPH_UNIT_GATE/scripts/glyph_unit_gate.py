#!/usr/bin/env python3
"""PHASE_754 — glyph-unit orthography gate. See ../PRE_REGISTRATION.md (locked, commit e9d7f1e)."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript  # noqa: E402

OUT = ROOT / 'phases/PHASE_754_GLYPH_UNIT_GATE/results'
OUT.mkdir(parents=True, exist_ok=True)
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
BENCHES = {'ch', 'sh'}
BENCHED_GALLOWS = {'cth', 'ckh', 'cph', 'cfh'}
SEED = 754


def glyphize(word):
    return GLYPH_RE.findall(word)


def is_minim(g):
    return len(g) >= 2 and g[0] == 'i'


def log(*a):
    print(*a, flush=True)


def load(which):
    tx = Transcript()
    it = tx.currier_b() if which == 'B' else tx.currier_a()
    toks = []
    for t in it:
        w = t.word.replace('*', '').strip()
        if w:
            toks.append((t.folio, w))
    return toks


res = {'phase': 'PHASE_754', 'pre_registration_commit': 'e9d7f1e'}
for which in ('B', 'A'):
    toks = load(which)
    words = [w for _, w in toks]
    # ------------------------------------------------------------------ Part A: context determinism
    occ = Counter()
    inside = Counter()
    left = defaultdict(Counter)
    right = defaultdict(Counter)
    for w in words:
        glyphs = glyphize(w)
        for g in glyphs:
            for ch in g:
                occ[ch] += 1
                if len(g) > 1:
                    inside[ch] += 1
        for i, ch in enumerate(w):
            left[ch][w[i - 1] if i > 0 else '^'] += 1
            right[ch][w[i + 1] if i < len(w) - 1 else '$'] += 1
    partA = {}
    for ch in sorted(occ, key=lambda c: -occ[c]):
        partA[ch] = {'n': occ[ch], 'inside_multiletter_glyph': round(inside[ch] / occ[ch], 4),
                     'top_left': left[ch].most_common(5), 'top_right': right[ch].most_common(5)}

    # ------------------------------------------------------------------ Part B
    gl_tokens = [glyphize(w) for w in words]
    final = Counter()
    total = Counter()
    for gs in gl_tokens:
        for i, g in enumerate(gs):
            total[g] += 1
            if i == len(gs) - 1:
                final[g] += 1

    def share_final(pred):
        n = sum(total[g] for g in total if pred(g))
        f = sum(final[g] for g in total if pred(g))
        return {'n': n, 'token_final_share': round(f / n, 4) if n else None}

    B1 = {'bench_and_benched_gallows': share_final(lambda g: g in BENCHES | BENCHED_GALLOWS),
          'benches_only': share_final(lambda g: g in BENCHES),
          'all_other_glyphs': share_final(lambda g: g not in BENCHES | BENCHED_GALLOWS)}
    B2 = {'minim_groups': share_final(is_minim),
          'minim_group_inventory': {g: {'n': total[g], 'final_share': round(final[g] / total[g], 4)}
                                    for g in sorted((g for g in total if is_minim(g)), key=lambda g: -total[g])[:12]},
          'bare_n': {'n': total.get('n', 0), 'final_share': round(final.get('n', 0) / total['n'], 4) if total.get('n') else None}}

    # B3: e -> bench/benched-gallows transitions within tokens vs within-token glyph shuffle
    def count_e_bench(gl_list):
        c = 0
        for gs in gl_list:
            for a, b in zip(gs, gs[1:]):
                if a == 'e' and (b in BENCHES or b in BENCHED_GALLOWS):
                    c += 1
        return c

    def count_bench_e(gl_list):
        c = 0
        for gs in gl_list:
            for a, b in zip(gs, gs[1:]):
                if (a in BENCHES or a in BENCHED_GALLOWS) and b == 'e':
                    c += 1
        return c

    obs_eb, obs_be = count_e_bench(gl_tokens), count_bench_e(gl_tokens)
    rng = np.random.default_rng(SEED)
    null_eb, null_be = [], []
    for _ in range(200):
        sh = []
        for gs in gl_tokens:
            if len(gs) > 1:
                p = rng.permutation(len(gs))
                sh.append([gs[k] for k in p])
            else:
                sh.append(gs)
        null_eb.append(count_e_bench(sh))
        null_be.append(count_bench_e(sh))
    B3 = {'e_to_bench_observed': obs_eb, 'e_to_bench_shuffle_mean': float(np.mean(null_eb)),
          'bench_to_e_observed': obs_be, 'bench_to_e_shuffle_mean': float(np.mean(null_be)),
          'eva_e_to_h_count': sum(1 for w in words for a, b in zip(w, w[1:]) if a == 'e' and b == 'h')}

    # B4: folio-level correlations (raw counts and per-letter proportions)
    fol_letters = defaultdict(Counter)
    fol_glyphs = defaultdict(Counter)
    for (folio, w), gs in zip(toks, gl_tokens):
        fol_letters[folio].update(w)
        for g in gs:
            key = 'MIN_n' if is_minim(g) and g[-1] == 'n' else 'MIN_r' if is_minim(g) and g[-1] == 'r' else g
            fol_glyphs[folio][key] += 1
    folios = sorted(f for f in fol_letters if sum(fol_letters[f].values()) >= 200)

    def corr(counter_by_folio, a, b, proportional):
        xa, xb = [], []
        for f in folios:
            tot = sum(counter_by_folio[f].values())
            va, vb = counter_by_folio[f].get(a, 0), counter_by_folio[f].get(b, 0)
            if proportional:
                va, vb = va / tot, vb / tot
            xa.append(va)
            xb.append(vb)
        if np.std(xa) == 0 or np.std(xb) == 0:
            return None
        return round(float(np.corrcoef(xa, xb)[0, 1]), 3)

    B4 = {'n_folios': len(folios), 'eva': {}, 'glyph': {}}
    for a, b in [('c', 'h'), ('a', 'i'), ('a', 'n'), ('a', 'r'), ('i', 'n'), ('i', 'r'), ('n', 'r')]:
        B4['eva'][f'{a}-{b}'] = {'raw': corr(fol_letters, a, b, False), 'prop': corr(fol_letters, a, b, True)}
    for a, b in [('ch', 'sh'), ('a', 'MIN_n'), ('a', 'MIN_r'), ('a', 'r'), ('MIN_n', 'MIN_r')]:
        B4['glyph'][f'{a}-{b}'] = {'raw': corr(fol_glyphs, a, b, False), 'prop': corr(fol_glyphs, a, b, True)}

    # B5: C1484 exclusivity rules as spelling rules
    def prev_share(letter, allowed):
        tot = sum(left[letter].values())
        return round(sum(v for k, v in left[letter].items() if k in allowed) / tot, 4) if tot else None

    B5 = {'n_preceded_by_i': prev_share('n', {'i'}), 'n_preceded_by_i_or_a': prev_share('n', {'i', 'a'}),
          'h_preceded_by_c_s_or_gallows': prev_share('h', {'c', 's', 'k', 't', 'p', 'f'})}

    # ------------------------------------------------------------------ classification (locked rule)
    def cls(letters):
        d = min(partA[l]['inside_multiletter_glyph'] for l in letters if l in partA)
        return ('IDENTITY' if d >= 0.99 else 'PARTLY ORTHOGRAPHIC' if d >= 0.90 else 'NOT ORTHOGRAPHIC'), round(d, 4)

    claims = {
        'C1440 (h transparent terminal)': ['h'],
        'C1209 (n terminal)': ['n'],
        'C1484 (n<-i only; h<-c)': ['n', 'h'],
        'C1207 {c,h} cluster': ['c', 'h'],
        'C1207 {a,i,n,r} cluster': ['a', 'i', 'n', 'r'],
        'C1207 {i,n} core': ['i', 'n'],
        'C521 (e->h = 0)': ['h'],
    }
    classification = {k: dict(zip(('class', 'min_determinism'), cls(v))) for k, v in claims.items()}
    res[which] = {'n_tokens': len(words), 'partA': partA, 'B1': B1, 'B2': B2, 'B3': B3, 'B4': B4, 'B5': B5,
                  'classification': classification}
    log(f"\n=== Currier {which}: {len(words)} tokens ===")
    for ch in ['h', 'c', 'i', 'n', 'r', 'l', 'm', 'e', 'a', 's']:
        if ch in partA:
            log(f"  {ch}: n={partA[ch]['n']:6d} inside multi-letter glyph={partA[ch]['inside_multiletter_glyph']:.4f}  "
                f"left={partA[ch]['top_left'][:3]}")
    log(f"  B1 {B1}")
    log(f"  B2 minim final share={B2['minim_groups']}; bare n={B2['bare_n']}")
    log(f"  B3 {B3}")
    log(f"  B4 {B4}")
    log(f"  B5 {B5}")
    for k, v in classification.items():
        log(f"  {k}: {v}")

json.dump(res, open(OUT / 'glyph_unit_gate.json', 'w', encoding='utf-8'), indent=1)
log(f"\nwritten {OUT / 'glyph_unit_gate.json'}")
