"""Compare frequency distributions of Voynich vs reference corpora.

Key questions:
1. What share of running text is covered by top-K types? (coverage curve)
2. What is the Zipf slope? (NL is typically -1.0 to -1.1)
3. Above the hapax line, is the frequency-mass distribution NL-shaped?
4. Is there enough reusable vocabulary to encode natural language?
"""
import re
import math
from collections import Counter
from pathlib import Path
from scripts.voynich import Transcript

ROOT = Path('C:/git/voynich')

CORPORA = [
    ('Voynich H-track',               None),
    ('Voynich Currier B',             None),
    ('PL Testamentum Latin',          'sources/pseudo_lull_testamentum/release/testamentum_complete_latin.txt'),
    ('Codicillus Latin',              'sources/codicillus/codicillus_complete_latin.txt'),
    ('Rupescissa Latin',              'sources/rupescissa/rupescissa_latin_1561.txt'),
    ('Mesue Grabadin Latin',          'sources/mesue_grabadin/mesue_grabadin_latin_full.txt'),
    ('Antidotarium Nicolai',          'sources/antidotarium_nicolai/antidotarium_nicolai_latin_plain.txt'),
    ('Caesar BG bk1',                 'sources/classical_latin/caesar_bg_book1.txt'),
    ('Cicero Catilinarian 1',         'sources/classical_latin/cicero_catilinarian_1.txt'),
    ('Brunschwig 1500 German',        'sources/brunschwig_1500/brunschwig_1500_corrected.txt'),
    ('Dante Inferno Italian',         'sources/italian_german/dante_inferno.txt'),
    ('Goethe Faust German',           'sources/italian_german/goethe_faust.txt'),
    ('PL Testamentum English',        'sources/pseudo_lull_testamentum/testamentum_complete_english.txt'),
]

WORD_RE = re.compile(r"[A-Za-zÀ-ÿæœ]+")
N = 23000  # use Currier B size as the matching window so Voynich fits

def tokenize_text(text):
    return [w.lower() for w in WORD_RE.findall(text)]

def get_voynich(which):
    tx = Transcript()
    if which == 'all':
        return [t.word for t in tx.all() if t.word.strip()]
    if which == 'B':
        return [t.word for t in tx.currier_b() if t.word.strip()]

def zipf_slope(counts):
    sorted_counts = sorted(counts.values(), reverse=True)
    xs = [math.log(r + 1) for r in range(len(sorted_counts))]
    ys = [math.log(c) for c in sorted_counts]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den = sum((xs[i] - mx) ** 2 for i in range(n))
    return num / den

def analyze(tokens, label):
    tokens = tokens[:N]
    if len(tokens) < N - 1000:
        return None
    counts = Counter(tokens)
    total = sum(counts.values())
    sorted_pairs = counts.most_common()
    cumul = 0
    coverage = {}
    for i, (_, c) in enumerate(sorted_pairs, 1):
        cumul += c
        if i in (10, 50, 100, 250, 500, 1000, 2000):
            coverage[i] = 100 * cumul / total
    # frequency tiers
    tier_2_5 = sum(c for c in counts.values() if 2 <= c <= 5)
    tier_6_20 = sum(c for c in counts.values() if 6 <= c <= 20)
    tier_21_100 = sum(c for c in counts.values() if 21 <= c <= 100)
    tier_100plus = sum(c for c in counts.values() if c > 100)
    return {
        'label': label,
        'types': len(counts),
        'reusable_types': sum(1 for c in counts.values() if c >= 2),
        'high_freq_types': sum(1 for c in counts.values() if c >= 6),
        'cov': coverage,
        'zipf_slope': zipf_slope(counts),
        'tier_pct': {
            '2-5':    100 * tier_2_5 / total,
            '6-20':   100 * tier_6_20 / total,
            '21-100': 100 * tier_21_100 / total,
            '>100':   100 * tier_100plus / total,
        },
    }

rows = []
for label, path in CORPORA:
    if path is None:
        if 'Currier B' in label:
            toks = get_voynich('B')
        else:
            toks = get_voynich('all')
    else:
        fp = ROOT / path
        if not fp.exists():
            continue
        toks = tokenize_text(fp.read_text(encoding='utf-8', errors='ignore'))
    r = analyze(toks, label)
    if r:
        rows.append(r)

# coverage table
print('COVERAGE: % of running text (37,957 tokens) covered by top-K types')
print('-' * 105)
print(f'{"Corpus":<28} {"top10":>7} {"top50":>7} {"top100":>7} {"top250":>7} {"top500":>7} {"top1k":>7} {"top2k":>7}')
print('-' * 105)
for r in rows:
    cv = r['cov']
    print(f'{r["label"]:<28} {cv[10]:>6.1f}% {cv[50]:>6.1f}% {cv[100]:>6.1f}% {cv[250]:>6.1f}% {cv[500]:>6.1f}% {cv[1000]:>6.1f}% {cv[2000]:>6.1f}%')

# zipf
print()
print('ZIPF SLOPE (NL is typically -1.0 to -1.1):')
for r in rows:
    print(f'  {r["label"]:<28} {r["zipf_slope"]:+.3f}')

# tier mass
print()
print('% of running text by frequency tier:')
print('-' * 80)
print(f'{"Corpus":<28} {"2-5":>7} {"6-20":>7} {"21-100":>7} {">100":>7} {"Hapax":>7}')
for r in rows:
    t = r['tier_pct']
    hapax = 100 - sum(t.values())
    print(f'{r["label"]:<28} {t["2-5"]:>6.1f}% {t["6-20"]:>6.1f}% {t["21-100"]:>6.1f}% {t[">100"]:>6.1f}% {hapax:>6.1f}%')

# vocab budgets
print()
print('REUSABLE VOCABULARY BUDGET:')
print('-' * 70)
print(f'{"Corpus":<28} {"types>=2":>10} {"types>=6":>10} {"all types":>10}')
for r in rows:
    print(f'{r["label"]:<28} {r["reusable_types"]:>10,} {r["high_freq_types"]:>10,} {r["types"]:>10,}')
