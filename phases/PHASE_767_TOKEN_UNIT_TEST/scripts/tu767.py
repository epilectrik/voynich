"""PHASE_767 shared machinery: corpora (word-written, syllable-written, native syllabic, held-out word texts, B) and the
window features F1-F6.

A corpus is a list of SEGMENTS (lines); a segment is a list of tokens; a token is a tuple of units (letters, or B glyph
units). Every corpus is re-wrapped to B's line-length distribution (PHASE_765 rule), and features are computed on
windows of exactly N tokens.
"""
from __future__ import annotations

import glob
import importlib.util
import math
import re
import sys
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent
GB = ROOT / 'external/gaskell-bowern/data/meaningful.zip'
VIE = ROOT / 'external/token_unit/vie1934_readaloud.zip'


def _imp(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


G = _imp('g764_for767', ROOT / 'phases/PHASE_764_HUMAN_GIBBERISH_CONTROL/scripts/g764.py')
SY = _imp('syllabify767', HERE / 'syllabify.py')

EU = {'la': 'Historical - Latin - Literary - NT (Vulgate)',
      'it': 'Historical - Italian - Literary - NT - Diodati',
      'es': 'Historical - Spanish - Literary - NT - Sagradas Escrituras',
      'de': 'Historical - German - Literary - NT - Luther',
      'en': 'Historical - English - Literary - NT (KJV)'}
HELD_OUT_WORD = ['Historical - French - Literary - NT - Martin',
                 'Historical - Greek - Literary - NT - Textus Receptus',
                 'Historical - Russian - Literary - NT - Codex Marianus',
                 'Historical - Anglo-Saxon - Literary - NT - Hatton Gospels',
                 'Historical - Flemish - Literary - NT',
                 'Modern - Arabic - Literary - NT',
                 'Modern - Hebrew - Literary - NT',
                 'Modern - Maori - Literary - NT',
                 'Modern - Swahili - Literary - NT',
                 'Modern - Tagalog - Literary - NT - Ang Dating Biblia',
                 'Modern - Turkish - Literary - NT',
                 'Conlangs - Esperanto - Literary - NT',
                 'Conlangs - Interlingua - Literary - NT',
                 'Conlangs - Neo-Quenya - Literary - NT',
                 'Conlangs - Volapuk - Literary - NT']
PINYIN = 'Modern - Chinese (Pinyin) - Literary - NT - Matthew'


# ================================================================================================ loaders
def _gb(name):
    z = zipfile.ZipFile(GB)
    return z.read(f'texts/{name}.txt').decode('utf-8', errors='replace')


def eu_word(lang):
    return G.lines_from_text(_gb(EU[lang]))


def eu_syl(lang, maximal_onset=True):
    segs = []
    for seg in G.lines_from_text(_gb(EU[lang])):
        out = []
        for w in seg:
            sy = SY.syllabify(''.join(w), lang) if maximal_onset else _split_min(''.join(w), lang)
            out += [tuple(s) for s in sy]
        if out:
            segs.append(out)
    return segs


def syl_variant_spelling(segs, variants, seed):
    """Syllable text with spelling variation (a homophonic-style control): each syllable type gets `variants`
    distinct spellings (the syllable plus a variant marker unit, the first spelling unmarked), chosen uniformly at
    random for every token. Sequencing of syllable identities is unchanged; the inventory grows up to `variants`-fold."""
    rng = np.random.default_rng(seed)
    out = []
    for seg in segs:
        new = []
        for t in seg:
            k = int(rng.integers(variants))
            new.append(t if k == 0 else t + (f'#{k}',))
        out.append(new)
    return out


def _split_min(word, lang):
    """Variant syllabifier: a single consonant or any cluster splits after its first consonant (no onset clusters)."""
    parts = SY.syllabify(word, lang)
    joined = ''.join(parts)
    # re-cut: move all but the last consonant of each onset cluster back to the preceding syllable
    res = [parts[0]] if parts else []
    for p in parts[1:]:
        i = 0
        while i < len(p) - 1 and not SY._is_v(p[i]) and not SY._is_v(p[i + 1]):
            i += 1
        res[-1] += p[:i]
        res.append(p[i:])
    assert ''.join(res) == joined
    return [r for r in res if r]


def _clean_nfc(tok):
    t = unicodedata.normalize('NFC', tok.lower())
    return ''.join(c for c in t if c.isalpha())


def _segs_from_raw(text, split_re=r'\s+'):
    segs = []
    for raw in text.split('\n'):
        cur = []
        for tok in re.split(split_re, raw.strip()):
            w = _clean_nfc(tok) if tok else ''
            if w:
                cur.append(tuple(w))
            else:
                if cur:
                    segs.append(cur)
                cur = []
        if cur:
            segs.append(cur)
    return segs


def pinyin(tones=True):
    text = _gb(PINYIN)
    if not tones:
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if not unicodedata.combining(c))
    return _segs_from_raw(text)


def vietnamese():
    """Vietnamese 1923 NT (eBible vie1934, public domain): syllables split at spaces and hyphens."""
    z = zipfile.ZipFile(VIE)
    names = sorted(n for n in z.namelist() if re.match(r'vie1934_0(7\d|8\d|9\d)_[A-Z0-9]{3}_\d+_read\.txt', n)
                   and 70 <= int(n.split('_')[1]) <= 96)
    segs = []
    for n in names:
        segs += _segs_from_raw(z.read(n).decode('utf-8-sig', errors='replace'), split_re=r'[\s\-]+')
    return segs


def held_out_word(name):
    return G.lines_from_text(_gb(name))


CUV = ROOT / 'external/token_unit/cmn-cu89s_readaloud.zip'
LAHU = ROOT / 'external/token_unit/lhi_readaloud.zip'
UNIHAN = ROOT / 'external/token_unit/Unihan.zip'
_KM = None


def _kmandarin():
    """Unihan kMandarin: the first (most customary) toned Pinyin reading of each Han character."""
    global _KM
    if _KM is None:
        z = zipfile.ZipFile(UNIHAN)
        _KM = {}
        for line in z.read('Unihan_Readings.txt').decode('utf-8').splitlines():
            parts = line.split('\t')
            if len(parts) == 3 and parts[1] == 'kMandarin':
                _KM[chr(int(parts[0][2:], 16))] = unicodedata.normalize('NFC', parts[2].split()[0])
    return _KM


def _nt_files(zpath, prefix):
    z = zipfile.ZipFile(zpath)
    names = sorted(n for n in z.namelist() if re.match(rf'{re.escape(prefix)}_0\d\d_[A-Z0-9]{{3}}_\d+_read\.txt', n)
                   and 70 <= int(n.split('_')[-4]) <= 96)
    return z, names


def cuv_pinyin(tones=True):
    """Chinese Union Version NT (1919, public domain; eBible cmn-cu89s), each Han character transliterated to its
    first Unihan kMandarin reading (character-by-character, like the Gaskell & Bowern Pinyin). Punctuation is ignored
    (as in the G&B text, where it is attached to syllables); verse lines are the segments; characters without a
    reading are dropped."""
    km = _kmandarin()
    z, names = _nt_files(CUV, 'cmn-cu89s')
    segs = []
    for n in names:
        for raw in z.read(n).decode('utf-8-sig', errors='replace').split('\n'):
            cur = []
            for ch in raw:
                r = km.get(ch)
                if r:
                    if not tones:
                        r = ''.join(c for c in unicodedata.normalize('NFD', r) if not unicodedata.combining(c))
                    cur.append(tuple(r))
            if cur:
                segs.append(cur)
    return segs


def lahu():
    """Lahu Si NT (eBible lhi; copyright WBT, used locally for aggregate statistics only, not redistributed):
    a syllable-spaced orthography with tones written as final letters."""
    z, names = _nt_files(LAHU, 'lhi')
    segs = []
    for n in names:
        segs += _segs_from_raw(z.read(n).decode('utf-8-sig', errors='replace'), split_re=r'[\s\-]+')
    return segs


def b_segments(variant='ZL'):
    """Currier B segments in manuscript order: ZL merged (primary), ZL split at uncertain spaces, H-track, or EVA."""
    if variant == 'ZL':
        data = G.load_b_zl(merge_uncertain=True, unit='GLYPH')
    elif variant == 'ZL_SPLIT':
        data = G.load_b_zl(merge_uncertain=False, unit='GLYPH')
    elif variant == 'H':
        data = G.load_b_h(unit='GLYPH')
    elif variant == 'EVA':
        data = G.load_b_zl(merge_uncertain=True, unit='EVA')
    else:
        raise ValueError(variant)
    return [s for _, segs in data for s in segs], [(f, segs) for f, segs in data]


def zl_segments(lang, merge_uncertain=True, unit='GLYPH'):
    """ZL 3b P text of one Currier language, PHASE_761 cleaning; ',' merged; unreadable tokens split segments.
    For lang='B' this reproduces g764.load_b_zl (checked in the run script)."""
    SC = _imp('spacing767', ROOT / 'phases/PHASE_761_SPACING_ROBUSTNESS/scripts/spacing_check.py')
    cur_lang = None
    segs_out = []
    for raw in open(SC.ZL, encoding='utf-8', errors='replace'):
        m = re.match(r'^<(f\w+)>\s+<!(.*)>', raw)
        if m:
            L = re.search(r'\$L=(\w)', m.group(2))
            cur_lang = L.group(1) if L else None
            continue
        m = re.match(r'^<(f\w+)\.(\d+),([@+=*&~])(\w+)>\s+(.*)$', raw.rstrip('\n'))
        if not m or cur_lang != lang or not m.group(4).startswith('P'):
            continue
        text = SC.clean(m.group(5))
        for seg in text.split('<->'):
            seg = re.sub(r'<[^>]*>', '', seg).strip()
            toks, sep = [], None
            for p in re.split(r'([.,])', seg):
                if p in ('.', ','):
                    sep = p
                elif p:
                    toks.append((p, sep))
                    sep = None
            if merge_uncertain:
                merged = []
                for t, s in toks:
                    if s == ',' and merged:
                        merged[-1] = (merged[-1][0] + t, merged[-1][1])
                    else:
                        merged.append((t, s))
                toks = merged
            cur = []
            for t, _ in toks:
                if SC.readable(t) and t:
                    cur.append(G.units_b(t, unit))
                else:
                    if cur:
                        segs_out.append(cur)
                    cur = []
            if cur:
                segs_out.append(cur)
    return segs_out


def reference_generator(kind, seed):
    """Naibbe GV1 or Timm-Schinner output poured into B's skeleton (PHASE_765 gen_streams), as segments."""
    SC5 = _imp('step_compare767', ROOT / 'phases/PHASE_765_STEP_NOTATION_COMPARISON/scripts/step_compare.py')
    return [s for _, s in SC5.gen_streams(kind, seed, 'GLYPH')]


def b_line_lengths():
    """Line-length distribution for re-wrapping: lengths of B's ZL segments (tokens per segment)."""
    segs, _ = b_segments('ZL')
    return [len(s) for s in segs]


# ================================================================================================ windows
def windows(segs, N, lengths, rng, max_windows=5):
    """Re-wrap to B line lengths (lengths=None keeps the original lines), then cut consecutive windows of exactly N
    tokens (last line truncated)."""
    lines = G.rewrap(segs, lengths, rng) if lengths is not None else [s for s in segs if s]
    out, cur, got = [], [], 0
    for ln in lines:
        need = N - got
        if len(ln) >= need:
            cur.append(ln[:need])
            out.append(cur)
            if len(out) >= max_windows:
                break
            cur, got = [], 0
            rest = ln[need:]
            if rest:
                cur.append(rest)
                got = len(rest)
        else:
            cur.append(ln)
            got += len(ln)
    return out


# ================================================================================================ features
def f_vocab(win):
    toks = [t for ln in win for t in ln]
    return math.log10(len(set(toks)))


def f_heaps(win, block=2000):
    toks = [t for ln in win for t in ln]
    V = len(set(toks))
    vb = [len(set(toks[i:i + block])) for i in range(0, len(toks) - block + 1, block)]
    return math.log10(V / float(np.mean(vb)))


def f_bigram_gain(win, k=5):
    """Held-out bigram gain over in-vocabulary pairs: 1 - H(Witten-Bell bigram) / H(unigram), k contiguous folds."""
    n = sum(len(ln) for ln in win)
    fold_of, cum = [], 0
    for ln in win:
        fold_of.append(min(k - 1, int(k * cum / n)))
        cum += len(ln)
    Hu = Hb = 0.0
    for f in range(k):
        uni, big, foll = Counter(), Counter(), defaultdict(set)
        left = Counter()
        for ln, fo in zip(win, fold_of):
            if fo == f:
                continue
            uni.update(ln)
            for a, b in zip(ln, ln[1:]):
                big[(a, b)] += 1
                left[a] += 1
                foll[a].add(b)
        N = sum(uni.values())
        V = len(uni)
        denom = N + 0.5 * (V + 1)
        for ln, fo in zip(win, fold_of):
            if fo != f:
                continue
            for a, b in zip(ln, ln[1:]):
                if a not in uni or b not in uni:
                    continue
                pu = (uni[b] + 0.5) / denom
                T = len(foll[a])
                ca = left[a]
                pb = (big[(a, b)] + T * pu) / (ca + T) if ca > 0 else pu
                Hu -= math.log2(pu)
                Hb -= math.log2(pb)
    return 1.0 - Hb / Hu


def f_bigram_coverage(win, k=5):
    """Share of within-line test pairs (same folds as F3) whose two tokens both occur in training."""
    n = sum(len(ln) for ln in win)
    fold_of, cum = [], 0
    for ln in win:
        fold_of.append(min(k - 1, int(k * cum / n)))
        cum += len(ln)
    tot = cov = 0
    for f in range(k):
        vocab = set()
        for ln, fo in zip(win, fold_of):
            if fo != f:
                vocab.update(ln)
        for ln, fo in zip(win, fold_of):
            if fo == f:
                for a, b in zip(ln, ln[1:]):
                    tot += 1
                    cov += (a in vocab and b in vocab)
    return cov / tot if tot else float('nan')


def f_bigram_shuffle_delta(win, rng, R=20):
    """F3 minus its mean over R within-line shuffles (descriptive baseline for F3)."""
    obs = f_bigram_gain(win)
    vals = []
    for _ in range(R):
        sh = [list(ln) for ln in win]
        for ln in sh:
            rng.shuffle(ln)
        vals.append(f_bigram_gain(sh))
    return obs - float(np.mean(vals))


def f_vge2(win):
    """log10 of the number of types occurring at least twice in the window."""
    c = Counter(t for ln in win for t in ln)
    return math.log10(max(1, sum(1 for v in c.values() if v >= 2)))


def f_t80(win):
    """log10 of the number of types that together cover 80% of the window's tokens."""
    c = sorted(Counter(t for ln in win for t in ln).values(), reverse=True)
    target, cum = 0.8 * sum(c), 0
    for i, v in enumerate(c, 1):
        cum += v
        if cum >= target:
            return math.log10(i)
    return math.log10(len(c))


def extras(win):
    return {'X_vge2': f_vge2(win), 'X_t80': f_t80(win), 'X_pair_coverage': f_bigram_coverage(win)}


def _chunk(win):
    return G.Chunk(win)


def f_repeat(C):
    return G.repetition_S4(C)


def f_coupling(C, rng, R=200):
    o, m, p, e = G.shuffle_corrected(C, G.stat_S1, R, rng)
    h = G.entropy_F1(C)
    return e / h if h > 0 else float('nan')


def nr_matrix(types):
    """Boolean T x T: edit distance exactly 1 (PHASE_765 definition)."""
    T = len(types)
    M = np.zeros((T, T), bool)
    exact = {w: i for i, w in enumerate(types)}
    sub = defaultdict(list)
    for i, w in enumerate(types):
        for k in range(len(w)):
            sub[(len(w), k, w[:k] + w[k + 1:])].append(i)
            j = exact.get(w[:k] + w[k + 1:])
            if j is not None:
                M[i, j] = M[j, i] = True
    for idx in sub.values():
        if len(idx) > 1:
            for a in idx:
                for b in idx:
                    if a != b:
                        M[a, b] = True
    return M


def f_near_repeat(C, rng, R=200):
    types = [None] * (C.wid.max() + 1)
    for w, i in zip(C.words, C.wid):
        types[i] = w
    NR = nr_matrix(types)
    pp = C.pair_pos
    O = int(NR[C.wid[pp], C.wid[pp + 1]].sum())
    perm = C.perms(R, rng)
    E = float(NR[C.wid[perm[:, pp]], C.wid[perm[:, pp + 1]]].sum(1).mean())
    return float(np.log((O + 0.5) / (E + 0.5)))


FEATURES = ['F1_vocab', 'F2_heaps', 'F3_bigram_gain', 'F4_repeat', 'F5_coupling', 'F6_near_repeat']


def features(win, rng):
    C = _chunk(win)
    return {'F1_vocab': f_vocab(win), 'F2_heaps': f_heaps(win), 'F3_bigram_gain': f_bigram_gain(win),
            'F4_repeat': f_repeat(C), 'F5_coupling': f_coupling(C, rng), 'F6_near_repeat': f_near_repeat(C, rng)}


def corpus_features_full(segs, N, lengths, rng, max_windows=5):
    """Returns (median features, number of windows, per-window feature dicts)."""
    wins = windows(segs, N, lengths, rng, max_windows)
    if not wins:
        return None, 0, []
    per = [features(w, rng) for w in wins]
    return {f: float(np.median([p[f] for p in per])) for f in FEATURES}, len(wins), per


def corpus_features(segs, N, lengths, rng, max_windows=5):
    med, n, _ = corpus_features_full(segs, N, lengths, rng, max_windows)
    return med, n
