#!/usr/bin/env python3
"""PHASE_757 — Naibbe harness: published generator (unmodified), plaintexts, B skeleton, layouts, noise, controls.

See ../PRE_REGISTRATION.md (locked, commit a5506cb). This module generates corpora; statistics live in
panel_stats.py. Corpus format: list of lines; each line is a list of tokens (str) or None (blocker).
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
NAIBBE_DIR = ROOT / 'external/naibbe-cipher'
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
SR_RATE = 0.03
_MODS = {}


def glyphs(word):
    return GLYPH_RE.findall(word)


# ================================================================================================ generator
def load_version(v):
    """GV1 = naibbe.py (52-card), GV2 = naibbe_v2.py (78-card). Imported unmodified from the pinned clone."""
    if v in _MODS:
        return _MODS[v]
    fn = NAIBBE_DIR / ('naibbe.py' if v == 'GV1' else 'naibbe_v2.py')
    cwd = os.getcwd()
    os.chdir(NAIBBE_DIR)                       # the module reads references/naibbe_tables.csv relative to cwd
    try:
        spec = importlib.util.spec_from_file_location(f'naibbe_{v}', fn)
        m = importlib.util.module_from_spec(spec)
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(m)
    finally:
        os.chdir(cwd)
    _MODS[v] = m
    return m


def encrypt_line(m, text):
    """One call of the published encrypt_naibbe on one cleaned line. Returns (tokens, respaced plaintext chunks)."""
    buf = io.StringIO()
    ct = m.encrypt_naibbe(text, m.naibbe_tables, m.placeholder_to_glyph, use_78=m.USE_78_CARD_DECK,
                          pre_plaintext_file=buf)
    return ct, buf.getvalue().split()


def space_remove(m, tokens):
    return m.respace_line(' '.join(tokens), SR_RATE).split()


# ================================================================================================ plaintexts
ENGLISH_MARKERS = {'the', 'of', 'and', 'with', 'page', 'text', 'this', 'that', 'which', 'appears', 'possibly',
                   'visible', 'ink', 'written', 'blank', 'illegible', 'no', 'image', 'margin', 'figure', 'drawing',
                   'red', 'top', 'bottom', 'left', 'right', 'line', 'lines', 'section', 'header', 'notes', 'from',
                   'on', 'are', 'by', 'to', 'in', 'hand', 'label', 'labels', 'circle', 'circles'}


def _codicillus_raw_lines():
    """Latin transcription lines only. Markup stripped: headings, rules, fences, list items, English
    translations in parentheses, notes sections, and lines with >= 2 English marker words. `[?]` removed,
    `{red: ...}` unwrapped, bracketed expansions kept (p[ro] -> pro)."""
    out = []
    in_notes = False
    for line in open(ROOT / 'sources/codicillus/codicillus_complete_latin.txt', encoding='utf-8'):
        s = line.strip()
        if s.startswith('#'):
            in_notes = 'note' in s.lower() or 'content notes' in s.lower() or 'provenance' in s.lower()
            continue
        if in_notes or not s or s.startswith(('---', '```', '- ', '* ', '(', '|', '>', '[1', '**')):
            continue
        s = s.replace('[?]', ' ')
        s = re.sub(r'\{red:\s*', '', s).replace('}', ' ')
        s = s.replace('[', '').replace(']', '')
        words = re.findall(r'[A-Za-z]+', s)
        if not words:
            continue
        if sum(w.lower() in ENGLISH_MARKERS for w in words) >= 2:
            continue
        out.append(s)
    return out


def _dante_inferno_raw_lines():
    lines = open(ROOT / 'sources/italian_german/dante_inferno.txt', encoding='utf-8-sig').read().split('\n')
    start = next(i for i, l in enumerate(lines) if '*** START OF' in l) + 1
    end = next(i for i, l in enumerate(lines) if l.strip() == 'PURGATORIO')
    return lines[start:end]


def _antidotarium_raw_lines():
    out = []
    for line in open(ROOT / 'sources/antidotarium_nicolai/antidotarium_nicolai_latin_plain.txt', encoding='utf-8'):
        if line.startswith('#'):
            continue
        out.append(re.sub(r'\(f\.\s*\d+\s*[rv]\.?\)', ' ', line))
    return out


def _pliny_raw_lines():
    return open(NAIBBE_DIR / 'input/examples/nathist_book16.txt', encoding='utf-8').read().split('\n')


RAW = {'P-REC': _codicillus_raw_lines, 'P-PHA': _antidotarium_raw_lines, 'P-ITA': _dante_inferno_raw_lines,
       'P-NH': _pliny_raw_lines}


def plaintext(pid, m):
    """Cleaned plaintext for a version's clean_line: (lines, words, word index of each line start)."""
    lines, words, starts = [], [], []
    for raw in RAW[pid]():
        # clean_line keeps any alphabetic character (e.g. the drachm sign ʒ); the cipher's alphabet is a-z only
        ws = [re.sub(r'[^a-z]', '', m.clean_line(w)) for w in raw.split()]
        ws = [w for w in ws if w]
        if not ws:
            continue
        starts.append(len(words))
        words.extend(ws)
        lines.append(''.join(ws))
    return lines, words, starts


# ================================================================================================ B skeleton
def load_skeleton():
    """Currier B, H, P placement; blockers = uncertain tokens (PHASE_756 primary data)."""
    from scripts.voynich import Transcript
    tx = Transcript()
    lines, folio = defaultdict(list), {}
    for t in tx.currier_b(exclude_uncertain=False):
        if not (t.placement and t.placement.startswith('P')):
            continue
        w = t.word.strip()
        if not w:
            continue
        key = (t.folio, t.line)
        lines[key].append(None if t.is_uncertain else w)
        folio[key] = t.folio
    keys = list(lines)
    B = [lines[k] for k in keys]
    return {'B': B, 'folio': [folio[k] for k in keys], 'keys': keys,
            'n_certain': sum(w is not None for ln in B for w in ln)}


def pour(stream, B):
    """Pour a token stream into B's certain positions; blockers stay."""
    it = iter(stream)
    return [[None if w is None else next(it) for w in ln] for ln in B]


def place_blockers(lines, B):
    """L-WRAP: insert blockers at B's (line, position) where that line exists (clipped to line length)."""
    out = []
    for li, ln in enumerate(lines):
        ln = list(ln)
        if li < len(B):
            for p, w in enumerate(B[li]):
                if w is None:
                    ln.insert(min(p, len(ln)), None)
        out.append(ln)
    return out


# ================================================================================================ layouts
def gen_stream(m, pt, rng_seed, n_needed, sr):
    random.seed(rng_seed)
    lines = pt[0]
    i = random.randrange(len(lines))
    toks, chunks = [], []
    while len(toks) < n_needed:
        ct, ch = encrypt_line(m, lines[i % len(lines)])
        if sr:
            ct = space_remove(m, ct)
        toks.extend(ct)
        chunks.extend(ch)
        i += 1
    return toks[:n_needed], chunks


def gen_wrap(m, pt, rng_seed, skel_lens, target, sr):
    """Each skeleton line from whole plaintext words, filled to the word boundary nearest the target length
    (actual ciphertext counts). Stops at the first line boundary with total >= 0.99 * target."""
    random.seed(rng_seed)
    _, words, starts = pt
    nw = len(words)
    w = starts[random.randrange(len(starts))]
    out, chunks, total, li = [], [], 0, 0
    while total < 0.99 * target:
        L = skel_lens[li % len(skel_lens)]
        best = None
        k = 1
        while True:
            text = ''.join(words[(w + j) % nw] for j in range(k))
            ct, ch = encrypt_line(m, text)
            if sr:
                ct = space_remove(m, ct)
            cand = (abs(len(ct) - L), k, ct, ch)
            if best is None or cand[0] <= best[0]:
                best = cand
            if len(ct) >= L or k > 60:
                break
            k += 1
        _, k, ct, ch = best
        out.append(ct)
        chunks.extend(ch)
        total += len(ct)
        w = (w + k) % nw
        li += 1
    return out, chunks


# ================================================================================================ noise
def noise_model():
    """rho = half the H-F token disagreement on aligned tokens (Currier B, P lines, equal token counts);
    edit-distance-1 glyph-unit edits (H -> F) as the edit distribution."""
    cache = ROOT / 'phases/PHASE_757_NAIBBE_RIVAL_PANEL/results/noise_model.json'
    if cache.exists():
        return json.load(open(cache, encoding='utf-8'))
    from scripts.voynich import Transcript
    tx = Transcript()
    tr_lines = {'H': defaultdict(list), 'F': defaultdict(list)}
    for t in tx.all(h_only=False):
        if t.transcriber not in tr_lines or t.language != 'B' or t.is_label:
            continue
        if not (t.placement and t.placement.startswith('P')):
            continue
        w = t.word.strip()
        if w:
            tr_lines[t.transcriber][(t.folio, t.line)].append(w)
    pairs = differ = 0
    edits = []
    for key, h in tr_lines['H'].items():
        f = tr_lines['F'].get(key)
        if not f or len(f) != len(h):
            continue
        for a, b in zip(h, f):
            if '*' in a or '*' in b:
                continue
            pairs += 1
            if a == b:
                continue
            differ += 1
            ga, gb = glyphs(a), glyphs(b)
            if len(ga) == len(gb):
                d = [i for i in range(len(ga)) if ga[i] != gb[i]]
                if len(d) == 1:
                    edits.append(('sub', ga[d[0]], gb[d[0]]))
            elif abs(len(ga) - len(gb)) == 1:
                lo, hi = (ga, gb) if len(ga) < len(gb) else (gb, ga)
                for i in range(len(hi)):
                    if hi[:i] + hi[i + 1:] == lo:
                        edits.append(('ins', '', hi[i]) if len(gb) > len(ga) else ('del', hi[i], ''))
                        break
    model = {'aligned_pairs': pairs, 'differing': differ, 'disagreement_rate': differ / pairs,
             'rho': 0.5 * differ / pairs, 'n_edit1': len(edits), 'edits': edits,
             'edit_type_counts': dict(Counter(e[0] for e in edits))}
    cache.parent.mkdir(parents=True, exist_ok=True)
    json.dump(model, open(cache, 'w', encoding='utf-8'), indent=1)
    return model


def apply_noise(corpus, model, rng):
    rho, edits = model['rho'], model['edits']
    out = []
    for ln in corpus:
        new = []
        for w in ln:
            if w is not None and rng.random() < rho:
                w = corrupt(w, edits, rng)
            new.append(w)
        out.append(new)
    return out


def corrupt(word, edits, rng):
    g = glyphs(word)
    for _ in range(20):
        typ, a, b = edits[rng.integers(len(edits))]
        if typ == 'ins':
            p = rng.integers(len(g) + 1)
            return ''.join(g[:p] + [b] + g[p:])
        idx = [i for i, u in enumerate(g) if u == a]
        if not idx:
            continue
        i = idx[rng.integers(len(idx))]
        if typ == 'sub':
            return ''.join(g[:i] + [b] + g[i + 1:])
        if len(g) > 1:
            return ''.join(g[:i] + g[i + 1:])
    return word


# ================================================================================================ positive controls
class M1:
    """50-state first-order class Markov (49 classes + UN bucket) with class-conditional emission."""

    def __init__(self, B):
        ctm = json.load(open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', encoding='utf-8'))
        t2c = {t: int(c) for t, c in ctm['token_to_class'].items()}
        cls = lambda w: t2c.get(w, -1)
        starts, trans, emis = Counter(), defaultdict(Counter), defaultdict(Counter)
        for ln in B:
            seq = [w for w in ln if w is not None]
            if not seq:
                continue
            starts[cls(seq[0])] += 1
            for a, b in zip(seq, seq[1:]):
                trans[cls(a)][cls(b)] += 1
            for w in seq:
                emis[cls(w)][w] += 1
        self.start = self._s(starts)
        self.trans = {k: self._s(v) for k, v in trans.items()}
        self.emis = {k: self._s(v) for k, v in emis.items()}

    @staticmethod
    def _s(counter):
        ks = list(counter)
        p = np.array([counter[k] for k in ks], float)
        return ks, np.cumsum(p / p.sum())

    @staticmethod
    def _draw(s, rng):
        ks, cp = s
        return ks[min(int(np.searchsorted(cp, rng.random(), side='right')), len(ks) - 1)]

    def generate(self, B, rng):
        out = []
        for ln in B:
            new, c = [], None
            for w in ln:
                if w is None:
                    new.append(None)
                    continue
                c = self._draw(self.start, rng) if c is None else self._draw(self.trans.get(c, self.start), rng)
                new.append(self._draw(self.emis[c], rng))
            out.append(new)
        return out


class GEdge:
    """PHASE_753 N2 on the P skeleton: INITIAL kept; later tokens drawn from real tokens in the same zone that follow
    a token ending in the same EVA character as the previously generated token (zone pool after a blocker)."""

    def __init__(self, B):
        self.pool, self.zone_pool = defaultdict(list), defaultdict(list)
        for ln in B:
            n = len(ln)
            for p in range(1, n):
                w = ln[p]
                if w is None:
                    continue
                z = 2 if p == n - 1 else 1
                self.zone_pool[z].append(w)
                if ln[p - 1] is not None:
                    self.pool[(ln[p - 1][-1], z)].append(w)

    def generate(self, B, rng):
        out = []
        for ln in B:
            n = len(ln)
            new = [ln[0]]
            for p in range(1, n):
                if ln[p] is None:
                    new.append(None)
                    continue
                z = 2 if p == n - 1 else 1
                prev = new[p - 1]
                src = self.pool.get((prev[-1], z)) if prev is not None else None
                if not src:
                    src = self.zone_pool[z]
                new.append(src[rng.integers(len(src))])
            out.append(new)
        return out


class Timm:
    """Reference member: the SELF_CITATION_HEAD_TO_HEAD fitted Timm & Schinner self-citation generator (p2_battery
    `generate`), ported to the P skeleton (first line of each folio seeded from B; blockers kept in place)."""

    def __init__(self, B, folios):
        fit = json.load(open(ROOT / 'phases/SELF_CITATION_HEAD_TO_HEAD/results/p1_generator_fit.json', encoding='utf-8'))
        self.params = tuple(fit['best_params'])
        self.alpha = sorted({c for ln in B for w in ln if w for c in w})
        self.by_folio = defaultdict(list)
        for li, f in enumerate(folios):
            self.by_folio[f].append(li)

    def _pos(self, n, p_edge, rng):
        if n <= 1:
            return 0
        if rng.random() < p_edge:
            return 0 if rng.random() < 0.5 else n - 1
        return int(rng.integers(0, n))

    def _mutate(self, w, p_sub, p_ins, p_del, p_edge, rng):
        A = self.alpha
        r = rng.random()
        if r < p_sub or (len(w) <= 1 and r >= p_sub + p_ins):
            i = self._pos(len(w), p_edge, rng)
            return w[:i] + A[int(rng.integers(0, len(A)))] + w[i + 1:]
        if r < p_sub + p_ins:
            i = self._pos(len(w) + 1, p_edge, rng)
            return w[:i] + A[int(rng.integers(0, len(A)))] + w[i:]
        i = self._pos(len(w), p_edge, rng)
        return w[:i] + w[i + 1:] if len(w) > 1 else w

    def generate(self, B, rng):
        q, w_above, p_exact, p_sub, p_ins, p_second, p_edge, p_far = self.params
        p_del = max(0.0, 1.0 - p_sub - p_ins)
        out = [None] * len(B)
        for f, lis in self.by_folio.items():
            first = B[lis[0]]
            out[lis[0]] = list(first)
            stream = [w for w in first if w is not None]
            above = [w for w in first if w is not None]
            for li in lis[1:]:
                cur = []
                for slot in B[li]:
                    if slot is None:
                        cur.append(None)
                        continue
                    r = rng.random()
                    if above and r < w_above:
                        src = above[int(rng.integers(0, len(above)))]
                    elif r < w_above + p_far and stream:
                        src = stream[int(rng.integers(0, len(stream)))]
                    elif stream:
                        d = max(1, int(rng.geometric(1.0 - q)))
                        src = stream[-min(d, len(stream))]
                    else:
                        src = slot
                    w = src
                    if rng.random() >= p_exact:
                        w = self._mutate(w, p_sub, p_ins, p_del, p_edge, rng)
                        if rng.random() < p_second:
                            w = self._mutate(w, p_sub, p_ins, p_del, p_edge, rng)
                    cur.append(w)
                    stream.append(w)
                out[li] = cur
                above = [w for w in cur if w is not None]
        return out
