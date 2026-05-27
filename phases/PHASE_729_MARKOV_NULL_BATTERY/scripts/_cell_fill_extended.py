"""Extend cell-fill comparison to mensural notation and programming languages.

Mensural: each note becomes a token: f'{pname}{oct}{dur}' e.g. 'c5_1', 'b4_breve'
Programming: pure surface tokenization (identifier-or-symbol runs)
"""
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from scripts.voynich import Transcript

ROOT = Path('C:/git/voynich')
WORD_RE = re.compile(r"[A-Za-zÀ-ÿæœ]+")
CODE_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")  # identifiers/keywords only

def tokenize_text(text):
    return [w.lower() for w in WORD_RE.findall(text)]

def tokenize_code(text):
    return [w.lower() for w in CODE_RE.findall(text)]

def extract_mei_notes(mei_path):
    """Extract note tokens from one MEI file."""
    try:
        tree = ET.parse(mei_path)
    except Exception:
        return []
    ns = '{http://www.music-encoding.org/ns/mei}'
    tokens = []
    for note in tree.iter(ns + 'note'):
        pname = note.get('pname', '?')
        oct_ = note.get('oct', '?')
        dur = note.get('dur', '?')
        accid = note.get('accid', '')
        tokens.append(f"{pname}{oct_}_{dur}{accid}")
    return tokens

def get_voynich():
    tx = Transcript()
    return [t.word for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True) if t.word.strip()]

def cell_fill(words, k_start=10, k_end=50, start_len=2, end_len=3, min_word_len=4, max_word_len=None):
    if max_word_len:
        words = [w for w in words if min_word_len <= len(w) <= max_word_len]
    else:
        words = [w for w in words if len(w) >= min_word_len]
    if not words:
        return None
    starts = Counter(w[:start_len] for w in words)
    ends = Counter(w[-end_len:] for w in words)
    top_starts = set(s for s, _ in starts.most_common(k_start))
    top_ends = set(e for e, _ in ends.most_common(k_end))
    attested = set()
    for w in words:
        s = w[:start_len]
        e = w[-end_len:]
        if s in top_starts and e in top_ends:
            attested.add((s, e))
    return {
        'fill_rate': 100 * len(attested) / (k_start * k_end),
        'attested_cells': len(attested),
        'total_cells': k_start * k_end,
        'distinct_starts': len(starts),
        'distinct_ends': len(ends),
        'words_qualifying': len(words),
        'top_start': starts.most_common(1)[0][0] if starts else '',
        'top_end': ends.most_common(1)[0][0] if ends else '',
    }

# Collect all mensural tokens
mensural_dir = ROOT / 'sources/mensural_notation/jekyll/assets/mei'
mensural_tokens = []
for mei in mensural_dir.glob('*.mei'):
    mensural_tokens.extend(extract_mei_notes(mei))
print(f'Mensural notation: {len(mensural_tokens):,} note tokens extracted from {len(list(mensural_dir.glob("*.mei")))} files')

# Programming corpora
prog_corpora = {
    'Python (combined)':  'sources/programming_languages/python_combined.py',
    'C (redis_server.c)': 'sources/programming_languages/redis_server.c',
    'Emacs Lisp':         'sources/programming_languages/emacs_simple.el',
    'LaTeX (Knuth)':      'sources/programming_languages/knuth_sample.tex',
}

CORPORA = [
    ('Voynich Currier B',          get_voynich),
    ('Mensural notation (notes)',  lambda: mensural_tokens),
]
for name, path in prog_corpora.items():
    fp = ROOT / path
    if fp.exists():
        text = fp.read_text(encoding='utf-8', errors='ignore')
        CORPORA.append((name, lambda t=text: tokenize_code(t)))

# NL baselines for context
nl_corpora = {
    'PL Testamentum Latin':       'sources/pseudo_lull_testamentum/release/testamentum_complete_latin.txt',
    'Rupescissa Latin':           'sources/rupescissa/rupescissa_latin_1561.txt',
    'Brunschwig 1500 German':     'sources/brunschwig_1500/brunschwig_1500_corrected.txt',
    'PL Testamentum English':     'sources/pseudo_lull_testamentum/testamentum_complete_english.txt',
}
for name, path in nl_corpora.items():
    fp = ROOT / path
    if fp.exists():
        text = fp.read_text(encoding='utf-8', errors='ignore')
        CORPORA.append((name, lambda t=text: tokenize_text(t)))

print()
print(f'{"Corpus":<32} {"Tokens":>10} {"all-len Fill%":>14} {"4-7char Fill%":>14} {"Top start":<12} {"Top end":<12}')
print('-' * 110)
for label, getter in CORPORA:
    toks = getter()
    sample = toks[:23000] if len(toks) > 23000 else toks
    r_all = cell_fill(sample)
    r_short = cell_fill(sample, min_word_len=4, max_word_len=7)
    if r_all is None:
        continue
    short_str = f'{r_short["fill_rate"]:>13.1f}%' if r_short else '         n/a'
    print(f'{label:<32} {len(sample):>10,} {r_all["fill_rate"]:>13.1f}% {short_str} {repr(r_all["top_start"]):<12} {repr(r_all["top_end"]):<12}')
