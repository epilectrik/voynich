#!/usr/bin/env python3
"""PHASE_761 — boundary glyph coupling vs word-spacing uncertainty. See ../PRE_REGISTRATION.md (locked, cd7d887).

ZL 3b IVTFF, Currier B paragraph text. Shuffle-corrected MI(last glyph unit of left token; first glyph unit of right
token) at definite ('.') vs uncertain (',') spaces, with tokens merged across uncertain spaces, and a size-matched
comparison. Reference: PHASE_757's D2 definition on ZL (second-transcription replication of C1212/C1563).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT / 'phases/PHASE_757_NAIBBE_RIVAL_PANEL/scripts'))
import panel_stats as PS  # noqa: E402

ZL = ROOT / 'data/transcriptions/reference/ZL_official.txt'
OUT = ROOT / 'phases/PHASE_761_SPACING_ROBUSTNESS/results'
OUT.mkdir(parents=True, exist_ok=True)
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
SEED, NPERM, NSUB, NSUB_PERM = 761, 1000, 1000, 50


def log(*a):
    print(*a, flush=True)


def clean(text):
    text = re.sub(r'<![^>]*>', '', text)
    text = text.replace('<%>', '').replace('<$>', '')
    text = re.sub(r'\[([^\]:]*)(:[^\]]*)?\]', r'\1', text)      # [a:b] -> a
    text = text.replace('{', '').replace('}', '')
    text = re.sub(r'@\d+;', '?', text)                          # rare-glyph codes -> unreadable
    return text


def load():
    """Returns list of lines: each line = (folio, [segments]); segment = list of (token, sep_before) with sep '.'/','."""
    lang, folio = None, None
    lines = []
    for raw in open(ZL, encoding='utf-8', errors='replace'):
        m = re.match(r'^<(f\w+)>\s+<!(.*)>', raw)
        if m:
            folio = m.group(1)
            L = re.search(r'\$L=(\w)', m.group(2))
            lang = L.group(1) if L else None
            continue
        m = re.match(r'^<(f\w+)\.(\d+),([@+=*&~])(\w+)>\s+(.*)$', raw.rstrip('\n'))
        if not m or lang != 'B' or not m.group(4).startswith('P'):
            continue
        text = clean(m.group(5))
        segs = []
        for seg in text.split('<->'):
            seg = re.sub(r'<[^>]*>', '', seg).strip()
            parts = re.split(r'([.,])', seg)
            toks = []
            sep = None
            for p in parts:
                if p in ('.', ','):
                    sep = p
                elif p:
                    toks.append((p, sep))
                    sep = None
            if toks:
                segs.append(toks)
        lines.append((m.group(1), segs))
    return lines


def readable(t):
    return t and '?' not in t and '*' not in t


def boundaries(lines, merge_uncertain=False):
    """(last unit of left, first unit of right, sep) for usable within-segment boundaries."""
    out = []
    for _, segs in lines:
        for seg in segs:
            toks = seg
            if merge_uncertain:
                merged = []
                for t, sep in toks:
                    if sep == ',' and merged:
                        merged[-1] = (merged[-1][0] + t, merged[-1][1])
                    else:
                        merged.append((t, sep))
                toks = merged
            for (a, _), (b, sep) in zip(toks, toks[1:]):
                if sep is None or not readable(a) or not readable(b):
                    continue
                ua, ub = GLYPH_RE.findall(a), GLYPH_RE.findall(b)
                out.append((ua[-1], ub[0], sep))
    return out


def mi(x, y, nx, ny):
    j = np.bincount(x * ny + y, minlength=nx * ny).astype(float).reshape(nx, ny)
    p = j / j.sum()
    px, py = p.sum(1, keepdims=True), p.sum(0, keepdims=True)
    nz = p > 0
    return float((p[nz] * np.log2(p[nz] / (px @ py)[nz])).sum())


def coupling(x, y, nx, ny, rng, nperm=NPERM):
    obs = mi(x, y, nx, ny)
    perm = np.array([mi(x, rng.permutation(y), nx, ny) for _ in range(nperm)])
    return {'n': int(len(x)), 'mi': obs, 'perm_mean': float(perm.mean()), 'C': obs - float(perm.mean()),
            'p': float((1 + (perm >= obs).sum()) / (1 + nperm))}


def main():
    lines = load()
    rng = np.random.default_rng(SEED)
    B = boundaries(lines)
    Bm = boundaries(lines, merge_uncertain=True)
    lefts = sorted({b[0] for b in B + Bm})
    rights = sorted({b[1] for b in B + Bm})
    li, ri = {u: i for i, u in enumerate(lefts)}, {u: i for i, u in enumerate(rights)}
    nx, ny = len(lefts), len(rights)

    def arr(bs):
        return (np.array([li[b[0]] for b in bs], dtype=np.int64), np.array([ri[b[1]] for b in bs], dtype=np.int64))
    x_all, y_all = arr(B)
    dmask = np.array([b[2] == '.' for b in B])
    res = {'lines': len(lines), 'boundaries_all': len(B), 'definite': int(dmask.sum()), 'uncertain': int((~dmask).sum())}
    res['C_all'] = coupling(x_all, y_all, nx, ny, rng)
    res['C_def'] = coupling(x_all[dmask], y_all[dmask], nx, ny, rng)
    res['C_unc'] = coupling(x_all[~dmask], y_all[~dmask], nx, ny, rng)
    xm, ym = arr(Bm)
    res['C_merged'] = coupling(xm, ym, nx, ny, rng)
    # size-matched definite subsets
    di = np.flatnonzero(dmask)
    nu = int((~dmask).sum())
    sub = []
    for _ in range(NSUB):
        s = rng.choice(di, size=nu, replace=False)
        sub.append(coupling(x_all[s], y_all[s], nx, ny, rng, NSUB_PERM)['C'])
    res['C_def_size_matched'] = {'n': nu, 'median': float(np.median(sub)), 'q025': float(np.quantile(sub, 0.025)),
                                 'q975': float(np.quantile(sub, 0.975)),
                                 'fraction_below_C_unc': float(np.mean(np.array(sub) < res['C_unc']['C']))}
    # D2 replication on ZL (PHASE_757 definition: within-line pairs, full within-line shuffle baseline)
    corpus, folios = [], []
    for folio, segs in lines:
        toks = [t if readable(t) else None for seg in segs for t, _ in seg]
        if toks:
            corpus.append(toks)
            folios.append(folio)
    C = PS.Corpus(corpus, folios)
    res['D2_ZL'] = float(PS.d2(C, np.random.default_rng(SEED)))
    res['D2_H_reference'] = json.load(open(ROOT / 'phases/PHASE_757_NAIBBE_RIVAL_PANEL/results/controls_certification.json'))['B']['D2']
    ca = res['C_all']['C']
    rd, rm = res['C_def']['C'] / ca, res['C_merged']['C'] / ca
    res['ratio_def_to_all'], res['ratio_merged_to_all'] = rd, rm
    if rd >= 0.75 and rm >= 0.75 and res['C_def']['p'] < 0.001 and res['C_merged']['p'] < 0.001:
        verdict = 'ROBUST'
    elif rd < 0.50 or rm < 0.50:
        verdict = 'SPACING-DEPENDENT'
    else:
        verdict = 'INTERMEDIATE'
    res['verdict'] = verdict
    json.dump(res, open(OUT / 'spacing_check.json', 'w', encoding='utf-8'), indent=1)
    for k in ('C_all', 'C_def', 'C_unc', 'C_merged'):
        log(f"{k}: {res[k]}")
    log(f"size-matched C_def: {res['C_def_size_matched']}")
    log(f"D2 on ZL {res['D2_ZL']:.4f} vs H {res['D2_H_reference']:.4f}")
    log(f"ratios def/all {rd:.3f}, merged/all {rm:.3f}  ->  VERDICT (locked rules): {verdict}")


if __name__ == '__main__':
    main()
