"""PHASE_774 control generators: ciphers with known plaintext whose spellings vary, laid into B's skeleton.

Spelling material comes from Currier A only (never from B's forms): A's MIDDLE inventory for stems and A's
(articulator, prefix, secondary prefix, suffix) frames for affixes. B supplies only its skeleton (lines, lengths,
uncertain-token blockers, sections, folios).

Families (the hidden unit is returned alongside every token):
  HRC-S   stem codebook: each plaintext word type has one stem (an A MIDDLE, by frequency rank); every occurrence gets
          an affix frame. frames='free' draws the frame from A's frame distribution; frames='rule' draws it from A's
          within-line frame-to-frame transitions (a local spelling rule).
  HRC-SE  HRC-S whose stems also vary: each e-run in the stem is lengthened with a folio-level probability that drifts
          from folio to folio (an e-dial selector).
  CB-k    word codebook with k unrelated whole-token spellings per word type (A tokens by frequency rank, then
          synthetic A-like tokens), one chosen at random per occurrence.
  NAIBBE  Naibbe GV1 ciphertext (published generator), unit = the plaintext chunk behind each token.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'phases/PHASE_768_HIDDEN_REPEATS/scripts'))
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')


def _imp(name, rel):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


HR = _imp('hr768', 'phases/PHASE_768_HIDDEN_REPEATS/scripts/hr768.py')
HR2 = _imp('hr768v2', 'phases/PHASE_768_HIDDEN_REPEATS/scripts/hr768v2.py')
NH = HR.NH


# ------------------------------------------------------------------------------------------------ Currier A material
_A = None


def a_material():
    """Currier A (H track, text placements, labels and uncertain tokens excluded): token counts, MIDDLE counts,
    frame counts and within-line frame transitions."""
    global _A
    if _A is not None:
        return _A
    from scripts.voynich import Transcript, Morphology
    morph = Morphology()
    tx = Transcript()
    lines = defaultdict(list)
    for t in tx.currier_a():
        w = t.word.strip()
        if w and '*' not in w:
            lines[(t.folio, t.line)].append(w)
    tok, mid, frame = Counter(), Counter(), Counter()
    trans = defaultdict(Counter)
    for ln in lines.values():
        prev = None
        for w in ln:
            m = morph.extract(w)
            md = m.middle or w
            fr = (m.articulator or '', m.prefix or '', getattr(m, 'prefix2', None) or '', m.suffix or '')
            tok[w] += 1
            mid[md] += 1
            frame[fr] += 1
            trans[prev][fr] += 1
            prev = fr
    _A = {'tokens': tok, 'middles': mid, 'frames': frame, 'frame_trans': trans, 'n_lines': len(lines)}
    return _A


def _sampler(counter, rng):
    keys = list(counter)
    p = np.array([counter[k] for k in keys], dtype=float)
    cum = np.cumsum(p / p.sum())
    return lambda: keys[min(int(np.searchsorted(cum, rng.random())), len(keys) - 1)]


def synthetic_strings(types, n_needed, exclude, seed, min_len=1, max_len=8):
    """New distinct strings from a glyph-unit trigram model over a type list (each type counted once)."""
    rng = np.random.default_rng(seed)
    tri = defaultdict(Counter)
    for w in types:
        g = ['^', '^'] + GLYPH_RE.findall(w) + ['$']
        for x, y, z in zip(g, g[1:], g[2:]):
            tri[(x, y)][z] += 1
    cum = {k: (list(v), np.cumsum(np.array(list(v.values()), dtype=float) / sum(v.values()))) for k, v in tri.items()}
    out, seen = [], set(exclude)
    while len(out) < n_needed:
        x, y, s = '^', '^', []
        while True:
            keys, cm = cum[(x, y)]
            z = keys[min(int(np.searchsorted(cm, rng.random())), len(keys) - 1)]
            if z == '$' or len(s) > 12:
                break
            s.append(z)
            x, y = y, z
        w = ''.join(s)
        if min_len <= len(s) <= max_len and w not in seen:
            seen.add(w)
            out.append(w)
    return out


def _rank_map(words, inventory_counter, seed, synth_len=(1, 6)):
    """Plaintext word types -> inventory items by frequency rank (ties random); synthetic items when exhausted."""
    rng = np.random.default_rng(seed)
    wc = Counter(words)
    wt = sorted(wc, key=lambda w: (-wc[w], rng.random()))
    inv = sorted(inventory_counter, key=lambda x: (-inventory_counter[x], x))
    if len(wt) > len(inv):
        inv = inv + synthetic_strings(list(inventory_counter), len(wt) - len(inv), set(inv), seed + 7,
                                      *synth_len)
    return {w: inv[i] for i, w in enumerate(wt)}


# ------------------------------------------------------------------------------------------------ families
def plain_stream(words, sk, offset=0):
    """The plaintext word stream aligned with B's certain tokens (texts shorter than B are refused: cycling a text
    would manufacture repeats)."""
    n = HR.n_certain(sk)
    assert offset + n <= len(words), f'plaintext too short: {len(words)} words for {n} tokens'
    return list(words[offset:offset + n])


def segment_stream(words, sk, k):
    """Segment k of a plaintext: words [k*n, (k+1)*n) with n = B's certain tokens; k = 'last' takes the final n words.
    Segment 0 is plain_stream (the design segment)."""
    n = HR.n_certain(sk)
    off = len(words) - n if k == 'last' else k * n
    assert 0 <= off and off + n <= len(words), f'segment {k} out of range ({len(words)} words)'
    return list(words[off:off + n])


def plaintext_p5(stream, sk):
    """P5: the plaintext's own phrase repetition in B's layout -- the number of within-line windows of 5 consecutive
    words (no blocker inside) whose word sequence occurs >= 2 times."""
    lines = HR.pour(stream, sk)
    occ = Counter()
    wins = []
    for ln in lines:
        for i in range(len(ln) - 4):
            w = ln[i:i + 5]
            if any(x is None for x in w):
                continue
            t = tuple(w)
            occ[t] += 1
            wins.append(t)
    return sum(occ[t] >= 2 for t in wins)


def section_fitted(gen, sk, seed):
    """A no-message generator fitted separately within each of B's sections (B's adjacent-pair transitions within a
    section; declared exposure), output reassembled in B's line order (lock-audit HET arm)."""
    by = defaultdict(list)
    for i, s in enumerate(sk['sections']):
        by[s].append(i)
    out = [None] * len(sk['lines'])
    for j, (s, idx) in enumerate(sorted(by.items())):
        sub = {'lines': [sk['lines'][i] for i in idx], 'sections': [sk['sections'][i] for i in idx],
               'folios': [sk['folios'][i] for i in idx]}
        for i, ln in zip(idx, gen(sub, seed + 101 * j)):
            out[i] = ln
    return out


def twin_stream(stream, sk, seed):
    """Shuffled-plaintext twin: the same words, order shuffled within each folio's span of certain tokens."""
    rng = np.random.default_rng(seed)
    fol = [f for ln, f in zip(sk['lines'], sk['folios']) for w in ln if w is not None]
    out = list(stream)
    by = defaultdict(list)
    for i, f in enumerate(fol):
        by[f].append(i)
    for f, idx in by.items():
        vals = [out[i] for i in idx]
        rng.shuffle(vals)
        for i, v in zip(idx, vals):
            out[i] = v
    return out


def lemma5(w):
    return w[:5]


def hrc_stem(words, sk, seed, frames='free', edial=False, edial_sd=0.25, stream=None):
    """HRC-S / HRC-SE in B's skeleton. Returns (lines, units) where units aligns with the certain tokens."""
    A = a_material()
    rng = np.random.default_rng(seed)
    n = HR.n_certain(sk)
    if stream is None:
        stream = plain_stream(words, sk)
    assert len(stream) == n
    stem = _rank_map(stream, A['middles'], seed + 1)          # the codebook covers the enciphered words
    free = _sampler(A['frames'], rng)
    rule = {k: _sampler(v, rng) for k, v in A['frame_trans'].items() if sum(v.values()) >= 5}
    fol_p = {}
    if edial:
        z = 0.0
        for f in dict.fromkeys(sk['folios']):
            z = 0.8 * z + rng.normal(0, edial_sd)          # drifting folio-level e-dial
            fol_p[f] = float(1 / (1 + np.exp(-(z - 1.0))))
    out, units, it = [], [], iter(stream)
    for ln, fol in zip(sk['lines'], sk['folios']):
        prev, cur = None, []
        for w in ln:
            if w is None:
                cur.append(None)
                prev = None
                continue
            u = next(it)
            s = stem[u]
            if edial:
                p = fol_p[fol]
                s = re.sub(r'e+', lambda m: m.group(0) + ('e' if rng.random() < p else ''), s)
            fr = free() if frames == 'free' or prev not in rule else rule[prev]()
            art, pre, pre2, suf = fr
            cur.append(art + pre + pre2 + s + suf)
            units.append(u)
            prev = fr
        out.append(cur)
    return out, units


def hrc_lemma(words, sk, seed, n_frames=3, frames='rule', stream=None):
    """HRC-L: lemma codebook. Each plaintext lemma (first five letters) has one stem (an A MIDDLE by frequency rank)
    and a small fixed set of n_frames affix frames drawn from A's frame distribution; each occurrence takes one of its
    stem's frames, chosen by A's frame-to-frame transitions restricted to that set (frames='rule') or uniformly
    ('free'). Inflection is not written. Units = lemmas."""
    A = a_material()
    rng = np.random.default_rng(seed)
    n = HR.n_certain(sk)
    if stream is None:
        stream = plain_stream(words, sk)
    assert len(stream) == n
    lem_words = [lemma5(w) for w in stream]                   # the codebook covers the enciphered words
    stem = _rank_map(lem_words, A['middles'], seed + 1)
    fkeys = list(A['frames'])
    fp = np.array([A['frames'][k] for k in fkeys], dtype=float)
    fp /= fp.sum()
    allowed = {}
    for L in sorted(set(lem_words)):
        m = min(n_frames, len(fkeys))
        allowed[L] = [fkeys[i] for i in rng.choice(len(fkeys), size=m, replace=False, p=fp)]
    trans = A['frame_trans']
    out, units, it = [], [], iter(stream)
    for ln in sk['lines']:
        prev, cur = None, []
        for w in ln:
            if w is None:
                cur.append(None)
                prev = None
                continue
            L = lemma5(next(it))
            opts = allowed[L]
            if frames == 'rule':
                wts = np.array([trans[prev].get(f, 0) + 0.5 for f in opts], dtype=float)
            else:
                wts = np.ones(len(opts))
            fr = opts[int(rng.choice(len(opts), p=wts / wts.sum()))]
            art, pre, pre2, suf = fr
            cur.append(art + pre + pre2 + stem[L] + suf)
            units.append(L)
            prev = fr
        out.append(cur)
    return out, units


# ------------------------------------------------------------------------------------------------ B-form codes
_B = None


def b_material(sk):
    """B's marginals only (declared, like the PHASE_768 habit generators and B-form codebooks): token counts, MIDDLE
    counts, P(frame | MIDDLE) and within-line frame-to-frame transitions. No sequence of B's MIDDLEs is used."""
    global _B
    if _B is not None:
        return _B
    from scripts.voynich import Morphology
    morph = Morphology()
    tok, mid = Counter(), Counter()
    fr_by_mid = defaultdict(Counter)
    frame = Counter()
    trans = defaultdict(Counter)
    for ln in sk['lines']:
        prev = None
        for w in ln:
            if w is None:
                prev = None
                continue
            m = morph.extract(w)
            md = m.middle or w
            fr = (m.articulator or '', m.prefix or '', m.prefix2 or '', m.suffix or '')
            if m.middle is None or (fr[0] + fr[1] + fr[2] + md + fr[3]) != w:
                fr = ('', '', '', '')
                md = w
            tok[w] += 1
            mid[md] += 1
            fr_by_mid[md][fr] += 1
            frame[fr] += 1
            trans[prev][fr] += 1
            prev = fr
    _B = {'tokens': tok, 'middles': mid, 'fr_by_mid': fr_by_mid, 'frames': frame, 'frame_trans': trans}
    return _B


def deficit_map(units_stream, target_counter, seed):
    """Many-to-one map of plaintext unit types onto target items so that the mapped stream reproduces the target's
    frequency profile: unit types in descending frequency, each to the target item with the largest remaining
    deficit (target share of the stream minus what is already assigned). Ties broken at random."""
    rng = np.random.default_rng(seed)
    uc = Counter(units_stream)
    n = sum(uc.values())
    tot = sum(target_counter.values())
    items = list(target_counter)
    deficit = np.array([target_counter[t] / tot * n for t in items], dtype=float)
    deficit += rng.random(len(items)) * 1e-6
    order = sorted(uc, key=lambda u: (-uc[u], rng.random()))
    mp = {}
    import heapq
    heap = [(-d, i) for i, d in enumerate(deficit)]
    heapq.heapify(heap)
    for u in order:
        negd, i = heapq.heappop(heap)
        mp[u] = items[i]
        heapq.heappush(heap, (negd + uc[u], i))
    return mp


def bform_stem(words, sk, seed, frames='rule', unit='lemma', stream=None):
    """HRC-B: a stem code in B's forms. Plaintext units (lemmas, or whole words) -> B MIDDLEs by deficit matching
    (reproduces B's MIDDLE frequency profile, many-to-one where needed); each occurrence takes a frame drawn from
    B's P(frame | MIDDLE), combined with B's frame-to-frame transition (frames='rule') or not ('free').
    Units = the plaintext units."""
    Bm = b_material(sk)
    rng = np.random.default_rng(seed)
    n = HR.n_certain(sk)
    if stream is None:
        stream = plain_stream(words, sk)
    assert len(stream) == n
    ustream = [lemma5(w) for w in stream] if unit == 'lemma' else list(stream)
    mp = deficit_map(ustream, Bm['middles'], seed + 1)
    fr_marg = Bm['frames']
    ftot = sum(fr_marg.values())
    fr_cache = {}

    def frames_for(md):
        if md not in fr_cache:
            c = Bm['fr_by_mid'][md]
            fr_cache[md] = (list(c), np.array(list(c.values()), dtype=float))
        return fr_cache[md]
    out, units, it = [], [], iter(ustream)
    for ln in sk['lines']:
        prev, cur = None, []
        for w in ln:
            if w is None:
                cur.append(None)
                prev = None
                continue
            u = next(it)
            md = mp[u]
            keys, wts = frames_for(md)
            if frames == 'rule' and len(keys) > 1:
                tr = Bm['frame_trans'].get(prev)
                if tr:
                    trt = sum(tr.values())
                    wts = wts * np.array([(tr.get(f, 0) + 0.5) / trt / (fr_marg[f] / ftot) for f in keys])
            fr = keys[int(rng.choice(len(keys), p=wts / wts.sum()))]
            cur.append(fr[0] + fr[1] + fr[2] + md + fr[3])
            units.append(u)
            prev = fr
        out.append(cur)
    return out, units


def bform_codebook(words, sk, seed, stream=None):
    """CB-B: a whole-word code in B's token forms (deficit matching onto B's token frequency profile)."""
    Bm = b_material(sk)
    n = HR.n_certain(sk)
    if stream is None:
        stream = plain_stream(words, sk)
    assert len(stream) == n
    mp = deficit_map(stream, Bm['tokens'], seed + 1)
    return HR.pour([mp[u] for u in stream], sk), list(stream)


def codebook(words, sk, k, seed, stream=None):
    """CB-k: k unrelated whole-token spellings per word type (A tokens by frequency rank, then synthetic)."""
    A = a_material()
    rng = np.random.default_rng(seed)
    n = HR.n_certain(sk)
    if stream is None:
        stream = plain_stream(words, sk)
    assert len(stream) == n
    wc = Counter(stream)                                      # the codebook covers the enciphered words
    wt = sorted(wc, key=lambda w: (-wc[w], rng.random()))
    inv = sorted(A['tokens'], key=lambda x: (-A['tokens'][x], x))
    need = len(wt) * k
    if need > len(inv):
        inv = inv + synthetic_strings(list(A['tokens']), need - len(inv), set(inv), seed + 3, 2, 10)
    spell = {w: inv[i * k:(i + 1) * k] for i, w in enumerate(wt)}
    toks = [spell[u][int(rng.integers(k))] for u in stream]
    return HR.pour(toks, sk), stream


def naibbe(pid, sk, seed):
    n = HR.n_certain(sk)
    toks, chunks = HR.naibbe_stream(pid, seed, n)
    return HR.pour(toks, sk), chunks


def plaintext_words(name):
    if name == 'LAT_rec':
        return list(NH.plaintext('P-REC', NH.load_version('GV1'))[1])
    if name == 'LAT_pha':
        return list(NH.plaintext('P-PHA', NH.load_version('GV1'))[1])
    if name == 'ITA_dante':
        return list(NH.plaintext('P-ITA', NH.load_version('GV1'))[1])
    if name in ('LAT_mesue', 'LAT_rupescissa', 'LAT_sismel', 'TUR_nt'):
        return [w.lower() for w in HR2.heldout_stream(name)]
    if name.startswith('NT_'):
        return [w.lower() for w in HR.natural_stream(name[3:])]
    raise ValueError(name)


def bform_codebook_k(words, sk, k, seed, stream=None):
    """CB-Bk: a whole-word code in B's token forms with k spellings per word (each occurrence picks one of its word's
    k spellings at random; the word#spelling units are deficit-matched onto B's token frequency profile)."""
    Bm = b_material(sk)
    rng = np.random.default_rng(seed)
    n = HR.n_certain(sk)
    if stream is None:
        stream = plain_stream(words, sk)
    assert len(stream) == n
    ustream = [f'{u}#{int(rng.integers(k))}' for u in stream]
    mp = deficit_map(ustream, Bm['tokens'], seed + 1)
    return HR.pour([mp[u] for u in ustream], sk), list(stream)


def timm_unseeded(sk, seed):
    """Timm-Schinner self-citation (PHASE_757 port) whose first line in each folio is drawn from B's token marginal
    instead of B's actual first line (so no sequence of B's tokens enters the control)."""
    Bm = b_material(sk)
    rng = np.random.default_rng(seed)
    draw = _sampler(Bm['tokens'], rng)
    NHsk = NH.load_skeleton()
    assert [len(x) for x in NHsk['B']] == [len(x) for x in sk['lines']], 'skeleton mismatch'
    B2 = [list(ln) for ln in NHsk['B']]
    seen = set()
    for li, f in enumerate(NHsk['folio']):
        if f not in seen:
            seen.add(f)
            B2[li] = [None if w is None else draw() for w in B2[li]]
    return NH.Timm(B2, NHsk['folio']).generate(B2, np.random.default_rng(seed + 1))


def m1_lines(sk, seed):
    """PHASE_757 M1: 50-state first-order class Markov with class-conditional emission (fitted on B's marginals)."""
    NHsk = NH.load_skeleton()
    return NH.M1(NHsk['B']).generate(NHsk['B'], np.random.default_rng(seed))
