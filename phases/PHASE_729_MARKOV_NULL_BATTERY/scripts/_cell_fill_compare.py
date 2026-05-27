"""Compare combinatorial cell-fill rate across languages.

Voynich uses prefix/middle/suffix decomposition from atomize(). For Latin/German
we don't have that, so use language-agnostic surface n-grams:
  - For each word, extract its first-2-char start and last-3-char end
  - Find the K most common starts and the K most common ends
  - Cell = (start, end) pair
  - Fill rate = fraction of cells that appear in at least one real word

If Voynich is combinatorially over-regular, its fill rate will be HIGHER than
NL fill rates at matched K.

Also test: shorter words (3-6 chars) only, to control for word-length distribution.
"""
import re
from collections import Counter
from pathlib import Path
from scripts.voynich import Transcript

ROOT = Path('C:/git/voynich')
WORD_RE = re.compile(r"[A-Za-zÀ-ÿæœ]+")
N = 23000  # tokens per corpus

CORPORA = [
    ('Voynich Currier B',          None),
    ('PL Testamentum Latin',       'sources/pseudo_lull_testamentum/release/testamentum_complete_latin.txt'),
    ('Codicillus Latin',           'sources/codicillus/codicillus_complete_latin.txt'),
    ('Rupescissa Latin',           'sources/rupescissa/rupescissa_latin_1561.txt'),
    ('Antidotarium Nicolai Latin', 'sources/antidotarium_nicolai/antidotarium_nicolai_latin_plain.txt'),
    ('Caesar BG bk1 (Cl. Latin)',  'sources/classical_latin/caesar_bg_book1.txt'),
    ('Cicero Cat. 1 (Cl. Latin)',  'sources/classical_latin/cicero_catilinarian_1.txt'),
    ('Brunschwig 1500 German',     'sources/brunschwig_1500/brunschwig_1500_corrected.txt'),
    ('Goethe Faust German',        'sources/italian_german/goethe_faust.txt'),
    ('Dante Inferno Italian',      'sources/italian_german/dante_inferno.txt'),
    ('PL Testamentum English',     'sources/pseudo_lull_testamentum/testamentum_complete_english.txt'),
]

def tokenize_text(text):
    return [w.lower() for w in WORD_RE.findall(text)]

def get_voynich():
    tx = Transcript()
    return [t.word for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True) if t.word.strip()]

def cell_fill(words, k_start=10, k_end=50, start_len=2, end_len=3, min_word_len=4):
    """For words with len>=min_word_len, extract (first start_len chars, last end_len chars).
    Return fill rate: how many of the (top-k_start, top-k_end) cells are attested."""
    words = [w for w in words if len(w) >= min_word_len]
    starts = Counter(w[:start_len] for w in words)
    ends = Counter(w[-end_len:] for w in words)
    top_starts = [s for s, _ in starts.most_common(k_start)]
    top_ends = [e for e, _ in ends.most_common(k_end)]
    attested = set()
    for w in words:
        s = w[:start_len]
        e = w[-end_len:]
        if s in top_starts and e in top_ends:
            attested.add((s, e))
    total_cells = k_start * k_end
    return {
        'fill_rate': 100 * len(attested) / total_cells,
        'attested_cells': len(attested),
        'total_cells': total_cells,
        'top_starts': top_starts[:5],
        'top_ends': top_ends[:5],
        'distinct_starts': len(starts),
        'distinct_ends': len(ends),
        'words_qualifying': len(words),
    }

print(f'CELL FILL RATE: (top-{10} start-2chars x top-{50} end-3chars), words >= 4 chars')
print(f'Each corpus truncated to {N:,} tokens.')
print('-' * 100)
print(f'{"Corpus":<32} {"Fill%":>7} {"Cells":>9} {"#starts":>9} {"#ends":>9} {"Top start":<10} {"Top end":<10}')
print('-' * 100)

results = []
for label, path in CORPORA:
    if path is None:
        toks = get_voynich()
    else:
        fp = ROOT / path
        if not fp.exists():
            continue
        toks = tokenize_text(fp.read_text(encoding='utf-8', errors='ignore'))
    if len(toks) < 10000:
        sample = toks
    else:
        sample = toks[:N]
    r = cell_fill(sample)
    results.append((label, r))
    print(f'{label:<32} {r["fill_rate"]:>6.1f}% {r["attested_cells"]:>4}/{r["total_cells"]:<4} {r["distinct_starts"]:>9,} {r["distinct_ends"]:>9,} {repr(r["top_starts"][0]):<10} {repr(r["top_ends"][0]):<10}')

# Also do for word lengths 4-7 only (control for word-length distribution)
print()
print('CONTROL: only words 4-7 chars (Voynich-typical length range):')
print('-' * 80)
print(f'{"Corpus":<32} {"Fill%":>7} {"Cells":>9} {"#starts":>9} {"#ends":>9}')
print('-' * 80)

for label, path in CORPORA:
    if path is None:
        toks = get_voynich()
    else:
        fp = ROOT / path
        if not fp.exists():
            continue
        toks = tokenize_text(fp.read_text(encoding='utf-8', errors='ignore'))
    if len(toks) < 10000:
        sample = toks
    else:
        sample = toks[:N]
    # restrict to 4-7 char words
    sample = [w for w in sample if 4 <= len(w) <= 7]
    r = cell_fill(sample, min_word_len=4)
    print(f'{label:<32} {r["fill_rate"]:>6.1f}% {r["attested_cells"]:>4}/{r["total_cells"]:<4} {r["distinct_starts"]:>9,} {r["distinct_ends"]:>9,}')

# Wider grid
print()
print('WIDER GRID: top-20 starts x top-100 ends, words >= 4 chars (2000 cells max):')
print('-' * 80)
for label, path in CORPORA:
    if path is None:
        toks = get_voynich()
    else:
        fp = ROOT / path
        if not fp.exists():
            continue
        toks = tokenize_text(fp.read_text(encoding='utf-8', errors='ignore'))
    if len(toks) < 10000:
        sample = toks
    else:
        sample = toks[:N]
    r = cell_fill(sample, k_start=20, k_end=100)
    print(f'{label:<32} {r["fill_rate"]:>6.1f}% {r["attested_cells"]:>5}/{r["total_cells"]:<5}')
