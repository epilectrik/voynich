#!/usr/bin/env python3
"""PHASE_771 — ZL 3b loader shared by the design and run scripts.

Paragraph text (locus type P*) and labels (locus type L*), with drawing breaks ('<->') kept as segment boundaries.
Page variables ($L language, $I section, $H hand) come from the page headers. Text rules follow PHASE_761:
comments removed, [a:b] -> a, ligature braces dropped, rare-glyph codes -> '?' (unreadable). Words are split at
definite ('.') and uncertain (',') spaces; the separator before each word is kept.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path('C:/git/voynich')
ZL = ROOT / 'data/transcriptions/reference/ZL_official.txt'
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
BREAK = '<->'


def clean(text):
    text = re.sub(r'<![^>]*>', '', text)
    text = text.replace('<%>', '').replace('<$>', '')
    text = re.sub(r'\[([^\]:]*)(:[^\]]*)?\]', r'\1', text)      # [a:b] -> a
    text = text.replace('{', '').replace('}', '')
    text = re.sub(r'@\d+;', '?', text)                          # rare-glyph codes -> unreadable
    return text


def units(w):
    return GLYPH_RE.findall(w)


def readable(w):
    return bool(w) and re.fullmatch(r'[a-z]+', w) is not None


def split_words(seg):
    """[(word, sep_before)] for one segment; sep is '.', ',' or None (segment start)."""
    seg = re.sub(r'<[^>]*>', '', seg).strip()
    out, sep = [], None
    for p in re.split(r'([.,])', seg):
        if p in ('.', ','):
            sep = p
        elif p.strip():
            out.append((p.strip(), sep))
            sep = None
    return out


def load():
    """Records in file order: dict(folio, locus, kind, lang, section, hand, par_start, par_end, segments).
    kind is the locus type code (e.g. 'P0', 'Pb', 'Lf', 'Lz'); segments is a list of word lists split at '<->'."""
    pv, folio, recs = {}, None, []
    for raw in open(ZL, encoding='utf-8', errors='replace'):
        m = re.match(r'^<(f\w+)>\s+<!(.*)>', raw)
        if m:
            folio = m.group(1)
            pv[folio] = dict(re.findall(r'\$(\w)=(\w*)', m.group(2)))
            continue
        m = re.match(r'^<(f\w+)\.(\w+),([@+=*&~])(\w+)>\s+(.*)$', raw.rstrip('\n'))
        if not m:
            continue
        f, locus, _, kind, body = m.groups()
        v = pv.get(f, {})
        par_start, par_end = '<%>' in body, '<$>' in body
        text = clean(body)
        segs = [split_words(s) for s in text.split(BREAK)]
        recs.append({'folio': f, 'locus': locus, 'kind': kind, 'lang': v.get('L', 'NA') or 'NA',
                     'section': v.get('I', '?'), 'hand': v.get('H', '?'), 'par_start': par_start,
                     'par_end': par_end, 'segments': segs})
    return recs
