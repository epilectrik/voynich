"""Compare Voynich hapax/reuse rates to medieval Latin + other reference corpora.

For each corpus:
- Lowercase, strip punctuation
- Split on whitespace
- Compute: total tokens, unique types, TTR, hapax %, top-type concentration
- To allow apples-to-apples comparison, also report stats truncated to
  Voynich's 37,957-token size (Heaps' law: vocabulary scales with N).
"""
import re
from collections import Counter
from pathlib import Path
from scripts.voynich import Transcript

ROOT = Path('C:/git/voynich')

CORPORA = [
    ('Voynich H-track (all)',        None),
    ('Voynich Currier A',            None),
    ('Voynich Currier B',            None),
    ('PL Testamentum (Latin)',       'sources/pseudo_lull_testamentum/release/testamentum_complete_latin.txt'),
    ('PL Testamentum (English)',     'sources/pseudo_lull_testamentum/testamentum_complete_english.txt'),
    ('Codicillus (Latin)',           'sources/codicillus/codicillus_complete_latin.txt'),
    ('Antidotarium Nicolai (Latin)', 'sources/antidotarium_nicolai/antidotarium_nicolai_latin_plain.txt'),
    ('Mesue Grabadin (Latin)',       'sources/mesue_grabadin/mesue_grabadin_latin_full.txt'),
    ('Rupescissa (Latin)',           'sources/rupescissa/rupescissa_latin_1561.txt'),
    ('Caesar BG bk 1 (Cl. Latin)',   'sources/classical_latin/caesar_bg_book1.txt'),
    ('Cicero Cat. 1 (Cl. Latin)',    'sources/classical_latin/cicero_catilinarian_1.txt'),
    ('Brunschwig 1500 (German)',     'sources/brunschwig_1500/brunschwig_1500_corrected.txt'),
    ('Puff von Schrick (German)',    'sources/puff_von_schrick/puff_1501_german.txt'),
    ('Dante Inferno (Italian)',      'sources/italian_german/dante_inferno.txt'),
    ('Goethe Faust (German)',        'sources/italian_german/goethe_faust.txt'),
]

WORD_RE = re.compile(r"[A-Za-zÀ-ÿæœ]+")

def tokenize_text(text):
    return [w.lower() for w in WORD_RE.findall(text)]

def analyze(tokens, label, truncate_to=None):
    if truncate_to and len(tokens) > truncate_to:
        tokens = tokens[:truncate_to]
        suffix = f' (first {truncate_to:,})'
    else:
        suffix = ''
    counts = Counter(tokens)
    total = sum(counts.values())
    types = len(counts)
    hapax = sum(1 for c in counts.values() if c == 1)
    top10_share = sum(c for _, c in counts.most_common(10)) / total if total else 0
    return {
        'label': label + suffix,
        'total': total,
        'types': types,
        'ttr': types / total if total else 0,
        'hapax_types': hapax,
        'hapax_type_pct': 100 * hapax / types if types else 0,
        'hapax_token_pct': 100 * hapax / total if total else 0,
        'top10_share': 100 * top10_share,
    }

def get_voynich(which):
    tx = Transcript()
    if which == 'all':
        tokens = [t.word for t in tx.all() if t.word.strip()]
    elif which == 'A':
        tokens = [t.word for t in tx.currier_a() if t.word.strip()]
    elif which == 'B':
        tokens = [t.word for t in tx.currier_b() if t.word.strip()]
    return tokens

rows = []
for label, path in CORPORA:
    if path is None:
        if 'Currier A' in label:
            toks = get_voynich('A')
        elif 'Currier B' in label:
            toks = get_voynich('B')
        else:
            toks = get_voynich('all')
    else:
        fp = ROOT / path
        if not fp.exists():
            print(f'SKIP missing: {path}')
            continue
        text = fp.read_text(encoding='utf-8', errors='ignore')
        toks = tokenize_text(text)
    full = analyze(toks, label)
    trunc = analyze(toks, label, truncate_to=37957)
    rows.append((full, trunc))

print(f'{"Corpus":<35} {"Tokens":>10} {"Types":>7} {"TTR":>6} {"Hapax-T%":>9} {"Hapax-tok%":>10} {"Top10%":>7}')
print('-' * 100)
print('FULL CORPUS:')
for full, _ in rows:
    print(f'{full["label"]:<35} {full["total"]:>10,} {full["types"]:>7,} {full["ttr"]:>6.3f} '
          f'{full["hapax_type_pct"]:>8.1f}% {full["hapax_token_pct"]:>9.1f}% {full["top10_share"]:>6.1f}%')

print()
print('TRUNCATED to Voynich size (37,957 tokens) — apples-to-apples:')
for _, trunc in rows:
    print(f'{trunc["label"]:<35} {trunc["total"]:>10,} {trunc["types"]:>7,} {trunc["ttr"]:>6.3f} '
          f'{trunc["hapax_type_pct"]:>8.1f}% {trunc["hapax_token_pct"]:>9.1f}% {trunc["top10_share"]:>6.1f}%')
