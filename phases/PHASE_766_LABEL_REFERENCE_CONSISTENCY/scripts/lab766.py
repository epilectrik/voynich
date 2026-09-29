"""PHASE_766 shared machinery: herbal-page text, pharmaceutical label words, glyph-unit edit distance.

Text rules (pre-registration E1): ZL 3b P text of herbal pages ($I=H), labels excluded; first reading of ZL alternates
([a:b] -> a); uncertain spaces (',') merged; tokens containing '?' or '*' dropped; glyph units c[tkpf]h|[cs]h|i+[nrlm]|.
Label words follow the same rules: a label string splits at '.', merges at ','; separate label strings of one item are
separate words.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
ZL = ROOT / 'data/transcriptions/reference/ZL_official.txt'
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
MIN_TOKENS = 40

# The 13 pre-registered pairs: item -> (pharmaceutical folio, herbal page, match wording class)
PAIRS = [(61, 'f89v2', 'f48r', 'same'), (80, 'f99r', 'f51r', 'sim'), (94, 'f99r', 'f96v', 'sim'),
         (95, 'f99v', 'f44r', 'sim'), (110, 'f99v', 'f34v', 'sim'), (116, 'f100r', 'f96v', 'sim'),
         (133, 'f100v', 'f13v', 'sim'), (136, 'f100v', 'f90v2', 'sim'), (203, 'f102r1', 'f37v', 'same'),
         (212, 'f102r2', 'f18v', 'same'), (213, 'f102r2', 'f23r', 'same'), (225, 'f102v2', 'f36r', 'sim'),
         (240, 'f102v1', 'f19r', 'same')]
JAR_ITEMS = {80, 94, 95}          # items whose container ('a') label exists (variant V2)
CONTAINER_CODED = {203}           # item whose only label is coded as a container (variant V3)


def clean(text):
    """PHASE_761 cleaning: comments dropped, first reading of alternates, ligature braces dropped, rare glyphs '?'."""
    text = re.sub(r'<![^>]*>', '', text)
    text = text.replace('<%>', '').replace('<$>', '')
    text = re.sub(r'\[([^\]:]*)(:[^\]]*)?\]', r'\1', text)
    text = text.replace('{', '').replace('}', '')
    text = re.sub(r'@\d+;', '?', text)
    return text


def split_words(text):
    """Split cleaned ZL text into readable words: '.' and '<->' split, ',' merges, '?'/'*' words dropped."""
    out = []
    for seg in text.split('<->'):
        seg = re.sub(r'<[^>]*>', '', seg).strip().replace(',', '')
        for w in seg.split('.'):
            w = w.strip()
            if w and '?' not in w and '*' not in w:
                out.append(w)
    return out


def units(w, unit='GLYPH'):
    return tuple(GLYPH_RE.findall(w)) if unit == 'GLYPH' else tuple(w)


def load_pages():
    """All ZL pages: page -> {'I': illustration type, 'L': Currier language, 'lines': [[word, ...], ...]} (P text)."""
    pages = {}
    folio = None
    for raw in open(ZL, encoding='utf-8', errors='replace'):
        m = re.match(r'^<(f\w+)>\s+<!(.*)>', raw)
        if m:
            folio = m.group(1)
            I = re.search(r'\$I=(\w)', m.group(2))
            L = re.search(r'\$L=(\w)', m.group(2))
            pages[folio] = {'I': I.group(1) if I else None, 'L': L.group(1) if L else None, 'lines': []}
            continue
        m = re.match(r'^<(f\w+)\.(\d+),([@+=*&~])(\w+)>\s+(.*)$', raw.rstrip('\n'))
        if not m or not m.group(4).startswith('P'):
            continue
        words = split_words(clean(m.group(5)))
        if words:
            pages[m.group(1)]['lines'].append(words)
    return pages


def herbal_pages(pages, min_tokens=MIN_TOKENS):
    """Reference set R: herbal ($I=H) pages with >= min_tokens readable P-text tokens, in manuscript order."""
    return [p for p, d in pages.items() if d['I'] == 'H' and sum(len(l) for l in d['lines']) >= min_tokens]


def label_strings():
    """Pharmaceutical label lines (f88-f102) carrying a ZL item tag: list of (item, suffix, folio, raw string)."""
    out = []
    for raw in open(ZL, encoding='utf-8', errors='replace'):
        m = re.match(r'^<(f(\d+)[rv]\d?)\.(\d+),([@+=*&~])(L\w*)>\s+(.*)$', raw.rstrip('\n'))
        if not m or not (88 <= int(m.group(2)) <= 102):
            continue
        tag = re.search(r'<!(\d+)([a-z]?)>', m.group(6))
        if tag:
            out.append((int(tag.group(1)), tag.group(2), m.group(1), m.group(5), m.group(6)))
    return out


def label_words(item, with_jar=False):
    """Label words of an item: every tagged label string except a container ('Lc') label, unless the item has no
    other label (item 203) or with_jar is set (V2)."""
    rows = [r for r in label_strings() if r[0] == item]
    frag = [r for r in rows if not r[3].startswith('Lc')]
    use = rows if (with_jar or not frag) else frag
    words = []
    for r in use:
        words += split_words(clean(r[4]))
    return list(dict.fromkeys(words))


def load_h_pages():
    """H-track P text (labels excluded, uncertain tokens dropped) by folio: folio -> [[word, ...], ...] (V5)."""
    from scripts.voynich import Transcript
    tx = Transcript()
    lines = defaultdict(list)
    order = []
    for t in tx.all(h_only=True):
        if not (t.placement and t.placement.startswith('P')):
            continue
        w = t.word.strip()
        if not w or t.is_uncertain:
            continue
        key = (t.folio, t.line)
        if key not in lines:
            order.append(key)
        lines[key].append(w)
    out = defaultdict(list)
    for key in order:
        out[key[0]].append(lines[key])
    return out


def edit_distance(a, b, cap=3):
    """Unit-cost Levenshtein distance between unit tuples, returned as min(d, cap) (early exit)."""
    la, lb = len(a), len(b)
    if abs(la - lb) >= cap:
        return cap
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        best = cur[0]
        ai = a[i - 1]
        for j in range(1, lb + 1):
            c = prev[j - 1] + (ai != b[j - 1])
            if prev[j] + 1 < c:
                c = prev[j] + 1
            if cur[j - 1] + 1 < c:
                c = cur[j - 1] + 1
            cur[j] = c
            if c < best:
                best = c
        if best >= cap:
            return cap
        prev = cur
    return min(prev[lb], cap)


def full_edit_distance(a, b):
    """Uncapped unit-cost Levenshtein distance."""
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j - 1] + (a[i - 1] != b[j - 1]), prev[j] + 1, cur[j - 1] + 1)
        prev = cur
    return prev[len(b)]
