#!/usr/bin/env python3
"""PHASE_772 — zodiac nymph labels (ZL 3b): loader, normalisations, statistics, verdict logic, simulation models
(v2 after the lean-expert lock audit).

Label = one Lz locus on a zodiac page with a clock position; its form is its words joined without separators;
alternative readings [a:b] take the first reading; labels with unreadable glyphs are excluded from the statistics
(but kept, flagged, for the adjacency descriptive). Signs group the zodiac pages (Aries and Taurus span two pages).
The Pisces central label (no clock position) is not a nymph label and is excluded.
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
ZL = ROOT / 'data/transcriptions/reference/ZL_official.txt'
H = ROOT / 'data/transcriptions/interlinear_full_words.txt'
SIGN = {'f70v2': 'Pisces', 'f70v1': 'Aries', 'f71r': 'Aries', 'f71v': 'Taurus', 'f72r1': 'Taurus',
        'f72r2': 'Gemini', 'f72r3': 'Cancer', 'f72v3': 'Leo', 'f72v2': 'Virgo', 'f72v1': 'Libra',
        'f73r': 'Scorpius', 'f73v': 'Sagittarius'}
TOP_ROW_PAGES = {'f72r2', 'f73r', 'f73v'}      # labels before the first ring text sit on a short arc (ring 0)
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
LAM_GRID = (0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0)


def clean(text):
    text = re.sub(r'<![^>]*>', '', text)
    text = text.replace('<%>', '').replace('<$>', '').replace('<->', '')
    text = re.sub(r'\[([^\]:]*)(:[^\]]*)?\]', r'\1', text)
    text = text.replace('{', '').replace('}', '')
    text = re.sub(r'@\d+;', '?', text)
    return re.sub(r'<[^>]*>', '', text)


def units(w):
    return GLYPH_RE.findall(w)


def load_labels(include_unreadable=False):
    """dict(folio, sign, ring, clock, form, words, readable). ring 0 = labels before the first ring text (top rows);
    words = the label split at definite spaces (uncertain spaces joined)."""
    out, cur, ring = [], None, 0
    for raw in open(ZL, encoding='utf-8', errors='replace'):
        m = re.match(r'^<(f\w+)>', raw)
        if m and not re.match(r'^<f\w+\.', raw):
            cur, ring = (m.group(1) if m.group(1) in SIGN else None), 0
            continue
        if cur is None:
            continue
        m = re.match(r'^<(f\w+)\.(\w+),([@+=*&~])(\w+)>\s+(.*)$', raw.rstrip('\n'))
        if not m or m.group(1) != cur:
            continue
        kind, body = m.group(4), m.group(5)
        clock = re.match(r'<!(\d\d):(\d\d)>', body)
        if kind[0] in 'CR':
            ring += 1
            continue
        if not kind.startswith('L') or clock is None:
            continue
        text = clean(body)
        words = [''.join(p.split(',')) for p in text.split('.') if p.replace(',', '')]
        form = ''.join(words)
        readable = bool(form) and re.fullmatch(r'[a-z]+', form) is not None
        if not readable and not include_unreadable:
            continue
        out.append({'folio': cur, 'sign': SIGN[cur], 'ring': ring,
                    'clock': int(clock.group(1)) % 12 + int(clock.group(2)) / 60.0, 'form': form,
                    'words': words, 'readable': readable})
    return out


def load_labels_h():
    """H-track zodiac labels (placement S), one label per (folio, line); readable only (descriptive replication)."""
    lab = defaultdict(list)
    with open(H, encoding='utf-8') as fh:
        for r in csv.DictReader(fh, delimiter='\t'):
            r = {k: (v.strip('"') if v else '') for k, v in r.items()}
            if r['transcriber'] != 'H' or r['folio'] not in SIGN or not r['placement'].startswith('S'):
                continue
            lab[(r['folio'], r['placement'], r['line_number'])].append(r['word'].strip())
    out = []
    for (f, pl, ln), ws in lab.items():
        form = ''.join(ws)
        if form and re.fullmatch(r'[a-z]+', form):
            out.append({'folio': f, 'sign': SIGN[f], 'form': form, 'words': ws})
    return out


def currier_a_words(min_units=4, max_units=8):
    """Readable Currier A paragraph words of 4-8 glyph units (ZL), the base pool for the simulation models."""
    out, lang = [], None
    for raw in open(ZL, encoding='utf-8', errors='replace'):
        m = re.match(r'^<(f\w+)>\s+<!(.*)>', raw)
        if m:
            L = re.search(r'\$L=(\w)', m.group(2))
            lang = L.group(1) if L else None
            continue
        m = re.match(r'^<(f\w+)\.(\w+),([@+=*&~])(\w+)>\s+(.*)$', raw.rstrip('\n'))
        if not m or lang != 'A' or not m.group(4).startswith('P'):
            continue
        for w in re.split(r'[.,]', clean(m.group(5))):
            if re.fullmatch(r'[a-z]+', w or '') and min_units <= len(units(w)) <= max_units:
                out.append(w)
    return out


# ---------------------------------------------------------------------------------------------------- normalisation
def n0(w):
    return w


def n1(w):
    """Free-variation layer collapsed: e-runs -> e, i-runs -> i (the final n/r/l/m kept)."""
    w = re.sub(r'e+', 'e', w)
    return re.sub(r'i+', 'i', w)


def n2(w):
    """Maximal collapse: N1 plus sh -> ch, benched gallows -> ckh, t/p/f -> k."""
    w = n1(w)
    w = w.replace('sh', 'ch')
    w = re.sub(r'c[tkpf]h', 'ckh', w)
    return re.sub(r'[tpf]', 'k', w)


NORMS = {'N0': n0, 'N1': n1, 'N2': n2}


# ------------------------------------------------------------------------------------------------------- statistics
def dup_stats(forms, signs):
    """R = share of labels whose form occurs in at least one other sign; D_w / D_a = within- / across-sign pairs of
    labels sharing a form; W = D_w / (D_w + D_a); W_exp = within-sign share of all label pairs."""
    by_form = defaultdict(Counter)
    for f, s in zip(forms, signs):
        by_form[f][s] += 1
    n = len(forms)
    rec = sum(1 for f, s in zip(forms, signs) if sum(c for t, c in by_form[f].items() if t != s) > 0)
    dw = da = 0
    for f, cs in by_form.items():
        tot = sum(cs.values())
        within = sum(c * (c - 1) // 2 for c in cs.values())
        dw += within
        da += tot * (tot - 1) // 2 - within
    sizes = Counter(signs)
    pairs_w = sum(k * (k - 1) // 2 for k in sizes.values())
    w_exp = pairs_w / (n * (n - 1) // 2)
    W = dw / (dw + da) if dw + da else float('nan')
    return {'R': rec / n, 'D_w': dw, 'D_a': da, 'W': W, 'W_exp': w_exp, 'n_types': len(by_form)}


def r_words(word_lists, signs):
    """Conservative recurrence: a label recurs if any of its words occurs among the words of another sign's labels."""
    by_word = defaultdict(set)
    for ws, s in zip(word_lists, signs):
        for w in ws:
            by_word[w].add(s)
    return sum(1 for ws, s in zip(word_lists, signs) if any(by_word[w] - {s} for w in ws)) / len(signs)


def perm_W(forms, signs, rng, nperm):
    """Permutation distribution of W (labels shuffled across signs, sign sizes fixed)."""
    signs = np.array(signs)
    out = np.empty(nperm)
    for i in range(nperm):
        out[i] = dup_stats(forms, list(rng.permutation(signs)))['W']
    return out


def w_test(forms, signs, rng, nperm):
    st = dup_stats(forms, signs)
    null = perm_W(forms, signs, rng, nperm)
    null = null[np.isfinite(null)]
    if not np.isfinite(st['W']) or len(null) == 0:
        st.update({'p_low': 1.0, 'p_high': 1.0, 'W_null_mean': float('nan'), 'p_min': 1.0})
        return st
    st['p_low'] = float((1 + np.sum(null <= st['W'])) / (len(null) + 1))
    st['p_high'] = float((1 + np.sum(null >= st['W'])) / (len(null) + 1))
    st['W_null_mean'] = float(null.mean())
    st['p_min'] = float((1 + np.sum(null <= null.min())) / (len(null) + 1))    # smallest attainable one-sided p
    return st


def verdict(n1s, n2s, r2, rw2, thr):
    """Pre-registered verdict. n1s/n2s: w_test outputs at N1/N2; r2 / rw2: R and conservative word-level R at N2;
    thr: {lam: {'q01': .., 'q05': ..}} for R(N2) under the pure inventory model (unrounded)."""
    low1, low2 = n1s['p_low'] < 0.01, n2s['p_low'] < 0.01
    high1 = n1s['p_high'] < 0.01
    if low1 and low2 and r2 >= thr['3.0']['q05']:
        return 'INVENTORY', None
    lam_star = None
    for lam in LAM_GRID:
        q = thr[str(lam)]['q01']
        if r2 < q and rw2 < q:
            lam_star = lam
        else:
            break
    calls = []
    if lam_star is not None and lam_star >= 1.0 and not low1 and not low2:
        calls.append(f'NO INVENTORY (bounded, lam* = {lam_star})')
    if high1 and not low2:
        calls.append('PALETTE')
    if not calls:
        calls.append('UNRESOLVED')
    return ' + '.join(calls), lam_star


# ------------------------------------------------------------------------------------------------ simulation models
def edits(w, rng, lam):
    """Apply Poisson(lam) attempted spelling-variant edits (some are no-ops): e-run length, minim-run length,
    ch/sh, a gallows among k/t/p/f, the initial o/y/q, the ending -y/-dy/-ey and -l/-r/-m."""
    ops = ['e', 'i', 'chsh', 'gallows', 'init', 'end']
    for _ in range(rng.poisson(lam)):
        op = ops[rng.integers(len(ops))]
        if op in ('e', 'i'):
            m = [x.start() for x in re.finditer(op + '+', w)]
            if m:
                j = m[rng.integers(len(m))]
                run = re.match(op + '+', w[j:]).group(0)
                new = op * max(1, len(run) + (1 if rng.random() < 0.5 else -1))
                w = w[:j] + new + w[j + len(run):]
        elif op == 'chsh':
            if 'ch' in w or 'sh' in w:
                w = w.replace('ch', 'sh', 1) if 'ch' in w and rng.random() < 0.5 else w.replace('sh', 'ch', 1)
        elif op == 'gallows':
            m = [x.start() for x in re.finditer(r'[ktpf]', w)]
            if m:
                j = m[rng.integers(len(m))]
                w = w[:j] + 'ktpf'[rng.integers(4)] + w[j + 1:]
        elif op == 'init':
            if w and w[0] in 'oyq':
                w = 'oyq'[rng.integers(3)] + w[1:] if rng.random() < 0.7 else w[1:]
            else:
                w = 'o' + w
        elif op == 'end':
            for a, bs in (('dy', ['y', 'ey']), ('ey', ['y', 'dy']), ('y', ['dy', 'ey']), ('l', ['r', 'm']),
                          ('r', ['l', 'm']), ('m', ['l', 'r'])):
                if w.endswith(a):
                    w = w[: -len(a)] + bs[rng.integers(2)]
                    break
    return w


def simulate(sizes, pool, rng, lam, phi=1.0, remainder='unique'):
    """Labels for signs of the given sizes. A share phi of positions are noisy copies of a shared inventory (one base
    form per position, from the pool); the rest are either palette draws (8 sign-specific base forms from the pool,
    with lam edits) or random Currier A words (token-weighted, drawn with replacement; remainder 'unique').
    Returns (forms, signs, visibly-changed flags of the inventory copies at N2)."""
    kmax = max(sizes.values())
    base = [pool[i] for i in rng.choice(len(pool), size=kmax, replace=False)]
    forms, signs, vis = [], [], []
    for s, k in sizes.items():
        n_inv = int(round(phi * k))
        pos = rng.permutation(k)
        palette = [pool[i] for i in rng.choice(len(pool), size=8, replace=False)] if remainder == 'palette' else None
        for j in range(k):
            if j < n_inv:
                w = edits(base[pos[j]], rng, lam)
                vis.append(n2(w) != n2(base[pos[j]]))
            elif remainder == 'palette':
                w = edits(palette[rng.integers(8)], rng, lam)
            else:
                w = pool[rng.integers(len(pool))]
            forms.append(w)
            signs.append(s)
    return forms, signs, vis
