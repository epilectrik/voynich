#!/usr/bin/env python3
"""PHASE_782 engine (pre-registration v2): Currier B (ZL) and the Codex Seraphinianus (Ponzi OCR) as lines with TRUE
positions; OCR-like noise for B; the CS guard; fixed-count chunks; MI(first unit; line zone) minus its within-line
permutation mean; AUC with a moving-block bootstrap over chunks.

Exposure guard: the real Codex order is returned only when the environment variable PHASE782_RUN equals 'locked'
(set by the locked run script). Before the lock, Codex lines come back shuffled within lines."""
from __future__ import annotations

import hashlib
import math
import os
import re
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
PH = ROOT / 'phases/PHASE_782_SERAPHINIANUS_LINE_POSITION'
EXT = ROOT / 'external/phase782_seraphinianus'
ZL = ROOT / 'data/transcriptions/reference/ZL_official.txt'
CS_FILE = EXT / 'CS_OCR_TRANSLITERATION.txt'
CS_SHA256 = 'a0df6dc711b5ead2bc44c06b1ae850de65443a55248f2dbdfe08bbc6e452c5a6'
BR_FILE = ROOT / 'sources/brunschwig_1500/brunschwig_1500_corrected.txt'
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
ZONES = 3                       # 0 initial, 1 medial, 2 final
FRAGMENT_CUT = 0.10
SHORT_FRAC = 0.6


# ------------------------------------------------------------------------------------------------ lines
class Line:
    """toks: unit tuples, or None for an excluded token; first: paragraph-first (B) or paragraph-first analogue (CS);
    brk: per token, beside a drawing break (B); group: chunking group (B section); flags: sensitivity flags (CS)."""
    __slots__ = ('unit', 'first', 'toks', 'brk', 'group', 'flags')

    def __init__(self, unit, first, toks, brk=None, group=None, flags=None):
        self.unit, self.first, self.toks = unit, first, toks
        self.brk = brk if brk is not None else [False] * len(toks)
        self.group = group
        self.flags = flags or {}

    def copy(self, toks=None, brk=None):
        return Line(self.unit, self.first, list(self.toks) if toks is None else toks,
                    list(self.brk) if brk is None else brk, self.group, self.flags)


def _clean_zl(text):
    text = re.sub(r'<![^>]*>', '', text)
    para = text.startswith('<%>')
    text = text.replace('<%>', '').replace('<$>', '')
    text = re.sub(r'\[([^\]:]*)(:[^\]]*)?\]', r'\1', text)
    text = text.replace('{', '').replace('}', '')
    text = re.sub(r'@\d+;', '?', text)
    return text, para


def load_b():
    """ZL 3b Currier B paragraph text (P placement). Uncertain spaces (',') merged; unreadable tokens kept as None;
    words beside '<->' flagged; section from the page header $I."""
    lang, sec = None, None
    out = []
    for raw in open(ZL, encoding='utf-8', errors='replace'):
        m = re.match(r'^<(f\w+)>\s+<!(.*)>', raw)
        if m:
            L = re.search(r'\$L=(\w)', m.group(2))
            lang = L.group(1) if L else None
            J = re.search(r'\$I=(\w)', m.group(2))
            sec = J.group(1) if J else '?'
            continue
        m = re.match(r'^<(f\w+)\.(\d+),([@+=*&~])(\w+)>\s+(.*)$', raw.rstrip('\n'))
        if not m or lang != 'B' or not m.group(4).startswith('P'):
            continue
        text, para = _clean_zl(m.group(5))
        toks, brk = [], []
        segs = text.split('<->')
        for si, seg in enumerate(segs):
            seg = re.sub(r'<[^>]*>', '', seg).strip()
            parts = re.split(r'([.,])', seg)
            seg_toks, sep = [], None
            for p in parts:
                if p in ('.', ','):
                    sep = p
                elif p:
                    if sep == ',' and seg_toks:
                        seg_toks[-1] = seg_toks[-1] + p
                    else:
                        seg_toks.append(p)
                    sep = None
            for k, t in enumerate(seg_toks):
                ok = t and '?' not in t and '*' not in t
                toks.append(tuple(GLYPH_RE.findall(t)) if ok else None)
                brk.append((k == 0 and si > 0) or (k == len(seg_toks) - 1 and si < len(segs) - 1))
        if toks:
            out.append(Line(m.group(1), para, toks, brk, group=sec))
    return out


def _check_cs():
    h = hashlib.sha256(open(CS_FILE, 'rb').read()).hexdigest()
    assert h == CS_SHA256, 'Codex transliteration changed'


def _load_cs_raw(numerals_excluded=True):
    """Parser (E1): block headers match ^#\\s+cs-; '# DUPLICATED:' lines are comments; '###PAGE' starts a page.
    Paragraph-first analogue (E2): block-first lines and lines after a short line (chars < 0.6 x block median)."""
    _check_cs()
    blocks = []                    # (page, block_id, [raw line strings])
    page = None
    for ln in open(CS_FILE, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if ln.startswith('###PAGE'):
            page = ln.split()[1]
            continue
        if re.match(r'^#\s+cs-', ln):
            blocks.append((page, ln.split()[-1], []))
            continue
        if ln.startswith('#'):
            continue                                       # '# DUPLICATED:' comment
        if not ln.strip():
            continue
        if not blocks or blocks[-1][0] != page:
            blocks.append((page, f'cs-{page}-nohdr', []))
        blocks[-1][2].append(ln)
    out = []
    for page, bid, raws in blocks:
        lens = [len(r.strip()) for r in raws]
        med = float(np.median(lens)) if lens else 0.0
        code = bid.split('-')[-1].split('.')[0]
        for i, r in enumerate(raws):
            toks = []
            for t in r.split():
                if '?' in t or '.' in t or (numerals_excluded and set(t) == {'Z'}):
                    toks.append(None)
                else:
                    toks.append(tuple(t))
            first_block = i == 0
            after_short = i > 0 and lens[i - 1] < SHORT_FRAC * med
            flags = {'block_first': first_block, 'after_short': after_short, 'wide_block': med > 70,
                     'long_line': lens[i] > 1.6 * med, 'block_code_23': code in ('2', '3'), 'chars': lens[i]}
            out.append(Line(page, first_block or after_short, toks, group=None, flags=flags))
    return out


def load_cs(numerals_excluded=True, rng=None):
    """The Codex lines. Before the lock (PHASE782_RUN != 'locked') only a within-line-shuffled copy is returned."""
    lines = _load_cs_raw(numerals_excluded)
    if os.environ.get('PHASE782_RUN') == 'locked':
        return lines
    assert rng is not None, 'pre-lock: the Codex is returned shuffled within lines; pass an rng'
    return shuffle_lines(lines, rng)


def cs_marginals():
    """Marginals that ignore line position: fragment strokes (word-initial share < 0.10), one-character share."""
    lines = _load_cs_raw()
    toks = [t for L in lines for t in L.toks if t is not None]
    tot, ini = Counter(), Counter()
    for t in toks:
        tot.update(t)
        ini[t[0]] += 1
    share = {c: ini[c] / tot[c] for c in tot}
    frag = sorted(c for c, s in share.items() if s < FRAGMENT_CUT)
    return {'fragment_strokes': frag, 'initial_share': share, 'n_tokens': len(toks),
            'fragment_initial_tokens': sum(t[0] in frag for t in toks), 'one_char_tokens': sum(len(t) == 1 for t in toks)}


def guard(lines, frag):
    """Guarded CS: one-character tokens and fragment-initial tokens excluded without creating edges (lines whose
    first or last readable token is so excluded become ineligible through the edge rule)."""
    fr = set(frag)
    out = []
    for L in lines:
        toks = [None if (t is None or len(t) == 1 or t[0] in fr) else t for t in L.toks]
        out.append(L.copy(toks=toks))
    return out


def load_brunschwig():
    """Descriptive anchor (N4): Brunschwig 1500 as transcribed, print lines; a hyphenated word at either edge makes
    the line ineligible (the edge token is set to None)."""
    out = []
    prev_hyph = False
    for raw in open(BR_FILE, encoding='utf-8'):
        s = raw.strip()
        if not s or s.startswith('[') or s.startswith('---'):
            prev_hyph = False
            continue
        s2 = re.sub(r'\[[^\]]*\]', ' ', s).lower().replace('ſ', 's')
        hyph = bool(re.search(r'[-¬=]\s*$', s2))
        toks = [tuple(w) for w in re.findall(r'[a-zäöüßęů]+', s2)]
        if not toks:
            prev_hyph = False
            continue
        toks = list(toks)
        if prev_hyph:
            toks[0] = None
        if hyph:
            toks[-1] = None
        out.append(Line('br', False, toks))
        prev_hyph = hyph
    return out


# ------------------------------------------------------------------------------------------------ noise and plants
def unit_marginals(lines):
    allu = Counter(u for L in lines for t in L.toks if t is not None for u in t)
    first = Counter(t[0] for L in lines for t in L.toks if t is not None)
    return allu, first


def _draw(marg, n, rng):
    units, w = zip(*marg.items())
    p = np.array(w, float) / sum(w)
    return [units[i] for i in rng.choice(len(units), size=n, p=p)]


def degrade(lines, q, s, m, rng, margs):
    """OCR-like noise (E7): merges (prob m per boundary between readable words), splits at a random internal unit
    boundary (prob s per word), substitution (prob q per unit; a word's first unit from the first-unit marginal,
    other units from the all-unit marginal)."""
    allu, first = margs
    out = []
    for L in lines:
        merged, mbrk = [], []
        for t, b in zip(L.toks, L.brk):
            if merged and t is not None and merged[-1] is not None and m > 0 and rng.random() < m:
                merged[-1] = merged[-1] + t
                mbrk[-1] = mbrk[-1] or b
            else:
                merged.append(t)
                mbrk.append(b)
        split, sbrk = [], []
        for t, b in zip(merged, mbrk):
            if t is not None and len(t) >= 2 and s > 0 and rng.random() < s:
                k = int(rng.integers(1, len(t)))
                split += [t[:k], t[k:]]
                sbrk += [b, b]
            else:
                split.append(t)
                sbrk.append(b)
        if q > 0:
            new = []
            for t in split:
                if t is None:
                    new.append(None)
                    continue
                hit = rng.random(len(t)) < q
                if hit.any():
                    tl = list(t)
                    if hit[0]:
                        tl[0] = _draw(first, 1, rng)[0]
                    rest = np.flatnonzero(hit[1:]) + 1
                    if len(rest):
                        for i, u in zip(rest, _draw(allu, len(rest), rng)):
                            tl[i] = u
                    t = tuple(tl)
                new.append(t)
            split = new
        out.append(L.copy(toks=split, brk=sbrk))
    return out


def shuffle_lines(lines, rng):
    """Within-line shuffle of the readable tokens among the readable positions."""
    out = []
    for L in lines:
        idx = [i for i, t in enumerate(L.toks) if t is not None]
        perm = rng.permutation(idx)
        toks = list(L.toks)
        for i, j in zip(idx, perm):
            toks[i] = L.toks[j]
        out.append(L.copy(toks=toks))
    return out


def plant_truncation(lines, t, rng):
    """C5(a): with probability t the line-initial token of at least 2 units loses its first unit."""
    out = []
    for L in lines:
        toks = list(L.toks)
        if toks and toks[0] is not None and len(toks[0]) >= 2 and rng.random() < t:
            toks[0] = toks[0][1:]
        out.append(L.copy(toks=toks))
    return out


def plant_splits(lines, s, rng):
    """C5(b): each readable token of at least 2 units split at a random internal boundary with probability s."""
    out = []
    for L in lines:
        toks, brk = [], []
        for x, b in zip(L.toks, L.brk):
            if x is not None and len(x) >= 2 and rng.random() < s:
                k = int(rng.integers(1, len(x)))
                toks += [x[:k], x[k:]]
                brk += [b, b]
            else:
                toks.append(x)
                brk.append(b)
        out.append(L.copy(toks=toks, brk=brk))
    return out


def plant_edges(lines, p, tilt_I, tilt_F, rng):
    """C4b: on eligible-shaped lines, with probability p the first unit of the line-initial (line-final) readable
    token is redrawn from tilt_I (tilt_F)."""
    out = []
    for L in lines:
        toks = list(L.toks)
        if len(toks) >= 3:
            if toks[0] is not None and rng.random() < p:
                toks[0] = (_draw(tilt_I, 1, rng)[0],) + toks[0][1:]
            if toks[-1] is not None and rng.random() < p:
                toks[-1] = (_draw(tilt_F, 1, rng)[0],) + toks[-1][1:]
        out.append(L.copy(toks=toks))
    return out


# ------------------------------------------------------------------------------------------------ chunks
def eligible(L, include_first=False, min_pos=3):
    if L.first and not include_first:
        return False
    return len(L.toks) >= min_pos and L.toks[0] is not None and L.toks[-1] is not None


def first_unit(t, first_n):
    if first_n == 1:
        return t[0]
    return ''.join(t[:2]) if len(t) >= 2 else t[0] + '#'


class ChunkSet:
    """Chunks of L consecutive eligible lines (within groups when within_groups); per chunk the slot arrays for the
    vectorised permutation null. Roles: 0 initial, 1 sampled medial, 2 final, -1 unsampled medial."""

    def __init__(self, lines, rng, L=40, K=80, include_first=False, drop_break=False, first_n=1, topk=None,
                 topk_per_chunk=None, interior=False, within_groups=True, exclude=None):
        min_pos = 5 if interior else 3
        el = []
        for ln in lines:
            if exclude and exclude(ln):
                continue
            if drop_break:
                ln = ln.copy(toks=[t if (not b or i in (0, len(ln.toks) - 1)) else None
                                   for i, (t, b) in enumerate(zip(ln.toks, ln.brk))])
            if eligible(ln, include_first, min_pos):
                el.append(ln)
        self.n_eligible = len(el)
        groups = []
        if within_groups:
            order = list(dict.fromkeys(ln.group for ln in el))
            for g in order:
                groups.append([ln for ln in el if ln.group == g])
        else:
            groups.append(el)
        F1all = [first_unit(t, first_n) for ln in el for t in ln.toks if t is not None]
        if topk:
            common = [u for u, _ in Counter(F1all).most_common(topk - 1)]
            enc = {u: i for i, u in enumerate(common)}
            gl_other = len(common)
            nsym = topk
        elif topk_per_chunk:
            enc, gl_other, nsym = None, None, topk_per_chunk + 1
        else:
            enc = {u: i for i, u in enumerate(sorted(set(F1all)))}
            gl_other, nsym = None, len(enc)
        self.nsym = nsym
        self.chunks, self.chunk_group = [], []
        self.n_short_medial = 0
        self.n_leftover_lines = 0
        for grp in groups:
            self.n_leftover_lines += len(grp) % L
            for c0 in range(0, len(grp) - L + 1, L):
                block = grp[c0:c0 + L]
                raw_vals, line_id, role, wlen = [], [], [], []
                for li, ln in enumerate(block):
                    n = len(ln.toks)
                    for i, t in enumerate(ln.toks):
                        if t is None:
                            continue
                        raw_vals.append(first_unit(t, first_n))
                        line_id.append(li)
                        wlen.append(min(len(t), 6))
                        if i == 0:
                            role.append(0)
                        elif i == n - 1:
                            role.append(2)
                        elif interior and not (2 <= i <= n - 3):
                            role.append(-2)            # near-edge medial: never sampled in the interior variant
                        else:
                            role.append(1)
                if topk_per_chunk:
                    common = [u for u, _ in Counter(raw_vals).most_common(topk_per_chunk)]
                    cenc = {u: i for i, u in enumerate(common)}
                    vals = np.array([cenc.get(v, topk_per_chunk) for v in raw_vals])
                elif gl_other is not None:
                    vals = np.array([enc.get(v, gl_other) for v in raw_vals])
                else:
                    vals = np.array([enc[v] for v in raw_vals])
                line_id, role, wlen = np.array(line_id), np.array(role), np.array(wlen)
                med = np.flatnonzero(role == 1)
                if len(med) < K:
                    self.n_short_medial += 1
                    continue
                keep = rng.choice(med, size=K, replace=False)
                role[role == -2] = -1
                role[med] = -1
                role[keep] = 1
                self.chunks.append((vals, line_id, role, wlen))
                self.chunk_group.append(block[0].group)

    def _perms(self, line_id, R, rng, gid=None):
        n = len(line_id)
        g = line_id if gid is None else gid
        keys = rng.random((R, n)) + g[None, :] * 2.0
        order = np.argsort(keys, axis=1, kind='stable')
        base = np.argsort(g, kind='stable')
        perm = np.empty_like(order)
        perm[:, base] = order
        return perm

    def excess(self, R, rng, normalise=False, length_class=False, zone_parts=False):
        out, parts = [], []
        for vals, line_id, role, wlen in self.chunks:
            n = len(vals)
            gid = line_id * 8 + wlen if length_class else None
            perm = np.vstack([np.arange(n)[None, :], self._perms(line_id, R, rng, gid)])
            sel = role >= 0
            f = vals[perm][:, sel]
            z = np.broadcast_to(role[sel], f.shape)
            mi = mi_rows(f, z, self.nsym, ZONES)
            e = float(mi[0] - mi[1:].mean())
            if normalise:
                c = np.bincount(f[0], minlength=self.nsym).astype(float)
                p = c[c > 0] / c.sum()
                h = float(-(p * np.log2(p)).sum())
                e = e / h if h > 0 else float('nan')
            out.append(e)
            if zone_parts:
                parts.append(zone_terms(f, z, self.nsym))
        return (np.array(out), parts) if zone_parts else np.array(out)


def mi_rows(x, y, nx, ny):
    R, m = x.shape
    code = (np.arange(R)[:, None] * (nx * ny) + x * ny + y).ravel()
    J = np.bincount(code, minlength=R * nx * ny).reshape(R, nx, ny).astype(float) / m
    px = J.sum(2, keepdims=True)
    py = J.sum(1, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        t = J * np.log2(J / (px * py))
    return np.nansum(t, axis=(1, 2))


def zone_terms(f, z, nsym):
    """Descriptive (N5): per-zone excess contribution and the observed top-unit share of the MI."""
    R, m = f.shape
    code = (np.arange(R)[:, None] * (nsym * ZONES) + f * ZONES + z).ravel()
    J = np.bincount(code, minlength=R * nsym * ZONES).reshape(R, nsym, ZONES).astype(float) / m
    px = J.sum(2, keepdims=True)
    py = J.sum(1, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        t = np.nan_to_num(J * np.log2(J / (px * py)))
    by_zone = t.sum(1)                                  # R x 3
    by_unit = t[0].sum(1)
    tot = by_unit.sum()
    return {'zone_excess': (by_zone[0] - by_zone[1:].mean(0)).tolist(),
            'top_unit_share': float(by_unit.max() / tot) if tot > 0 else float('nan')}


# ------------------------------------------------------------------------------------------------ comparison
def auc(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float((a[:, None] > b[None, :]).mean() + 0.5 * (a[:, None] == b[None, :]).mean())


def _block_resample(n, rng, block=3):
    starts = np.arange(0, n, block)
    pick = rng.choice(starts, size=len(starts), replace=True)
    idx = np.concatenate([np.arange(s, min(s + block, n)) for s in pick])
    return idx


def auc_block(a_reals, b_reals, rng, B=2000, block=3, iid=False):
    """a_reals, b_reals: lists of chunk-excess arrays (noise realisations; a single array for a fixed corpus).
    Point AUC = mean over realisation pairs; each bootstrap resample draws one realisation per side and resamples
    blocks of consecutive chunks within each side."""
    a_reals = [np.asarray(x, float) for x in (a_reals if isinstance(a_reals, list) else [a_reals])]
    b_reals = [np.asarray(x, float) for x in (b_reals if isinstance(b_reals, list) else [b_reals])]
    point = float(np.mean([auc(a, b) for a in a_reals for b in b_reals]))
    bs = np.empty(B)
    for k in range(B):
        a = a_reals[int(rng.integers(len(a_reals)))]
        b = b_reals[int(rng.integers(len(b_reals)))]
        ia = rng.integers(0, len(a), len(a)) if iid else _block_resample(len(a), rng, block)
        ib = rng.integers(0, len(b), len(b)) if iid else _block_resample(len(b), rng, block)
        bs[k] = auc(a[ia], b[ib])
    return {'auc': point, 'lo': float(np.percentile(bs, 2.5)), 'hi': float(np.percentile(bs, 97.5)),
            'n_a': int(np.mean([len(x) for x in a_reals])), 'n_b': int(np.mean([len(x) for x in b_reals]))}


def label(not_reached_parts, reached_parts):
    """not_reached_parts: AUC dicts for NOT REACHED conditions (a), (b); reached_parts: for REACHED (a), (b)."""
    if all(d['lo'] >= 0.80 for d in not_reached_parts):
        return 'NOT REACHED'
    if all(d['hi'] <= 0.65 for d in reached_parts):
        return 'REACHED'
    return 'UNRESOLVED'
