"""PHASE_765 corpus extraction for step notations (SN) and procedural prose (PP).

Corpora are returned as {name: list of segments}, a segment = list of words, a word = tuple of units, the same
representation as PHASE_764's g764 module. Raw files live in external/ (git-ignored).
"""
from __future__ import annotations

import glob
import re
import unicodedata
from pathlib import Path

ROOT = Path('C:/git/voynich')
EXT = ROOT / 'external'
ABBREV = re.compile(r'^(k|p|st|sts|ch|sc|dc|hdc|tr|dtr|sl|yo|yon|yrn|tog|rep|rnd|rnds|inc|dec|beg|sp|sps|lp|lps|psso|'
                    r'sk|skp|blo|flo|pat|patt|m|mc|cc|s|c|d|h|tbl|wyif|wyib|pc|cl|bl|lp)\d*(tog)?$')
NUMERAL = re.compile(r'^\d+(st|nd|rd|th)?$')
NOTATION_MIN_DENSITY = 0.30
MIN_WORDS = 1500


def _norm(tok, keep_case=False):
    t = unicodedata.normalize('NFD', tok if keep_case else tok.lower())
    return ''.join(c for c in t if c.isalnum())


def _gutenberg_body(text):
    s = text.find('*** START OF')
    e = text.find('*** END OF')
    if s >= 0:
        s = text.find('\n', s) + 1
    return text[s if s >= 0 else 0: e if e > 0 else len(text)]


def _para_segments(para):
    """A paragraph becomes one word stream; a token that is empty after normalisation splits it (no bridging)."""
    segs, cur = [], []
    for tok in para.split():
        w = _norm(tok)
        if w:
            cur.append(tuple(w))
        else:
            if cur:
                segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    return segs


def needlework(threshold=None):
    """Returns (notation corpora, prose corpora): per book, paragraphs with abbreviation density >= 0.35 are
    notation, the rest prose; a book contributes a corpus of each kind that has >= MIN_WORDS words."""
    notation, prose, stats = {}, {}, {}
    for f in sorted(glob.glob(str(EXT / 'step_notation/gutenberg/pg*.txt'))):
        name = Path(f).stem
        body = _gutenberg_body(open(f, encoding='utf-8', errors='replace').read())
        paras = re.split(r'\n\s*\n', body)
        nseg, pseg = [], []
        for para in paras:
            segs = _para_segments(para)
            words = [w for s in segs for w in s]
            if len(words) < 5:
                continue
            dens = sum(bool(ABBREV.match(''.join(w)) or NUMERAL.match(''.join(w))) for w in words) / len(words)
            (nseg if dens >= (threshold or NOTATION_MIN_DENSITY) else pseg).extend(segs)
        nw = sum(len(s) for s in nseg)
        pw = sum(len(s) for s in pseg)
        stats[name] = (nw, pw)
        if nw >= MIN_WORDS:
            notation[f'KNIT_{name}'] = nseg
        if pw >= MIN_WORDS:
            prose[f'NEEDLEPROSE_{name}'] = pseg
    return notation, prose, stats


def chess():
    """SAN movetext per game (case kept: piece letters are semantic); headers, comments, variations, move numbers,
    results and annotation glyphs removed. One segment per game."""
    out = {}
    for f in sorted(glob.glob(str(EXT / 'step_notation/chess/*.pgn'))):
        text = open(f, encoding='utf-8', errors='replace').read()
        games = re.split(r'\n\s*\n(?=\[Event)', text)
        segs = []
        for g in games:
            mv = '\n'.join(l for l in g.split('\n') if not l.startswith('['))
            mv = re.sub(r'\{[^}]*\}', ' ', mv)
            while re.search(r'\([^()]*\)', mv):
                mv = re.sub(r'\([^()]*\)', ' ', mv)
            mv = re.sub(r'\d+\.(\.\.)?', ' ', mv)
            mv = re.sub(r'(1-0|0-1|1/2-1/2|\*)', ' ', mv)
            toks = [_norm(t, keep_case=True) for t in mv.split()]
            toks = [tuple(t) for t in toks if t]
            if len(toks) >= 10:
                segs.append(toks)
        out[f'CHESS_{Path(f).stem}'] = segs
    return out


def apollo():
    """AGC assembly, comments removed; one segment per source file (the instruction stream)."""
    out = {}
    for prog in ('Comanche055', 'Luminary099'):
        segs = []
        for f in sorted(glob.glob(str(EXT / 'apollo-11' / prog / '*.agc'))):
            stream = []
            for line in open(f, encoding='utf-8', errors='replace'):
                line = line.split('#', 1)[0]
                for tok in line.split():
                    w = _norm(tok)
                    if w:
                        stream.append(tuple(w))
            if len(stream) >= 10:
                segs.append(stream)
        out[f'AGC_{prog}'] = segs
    return out
