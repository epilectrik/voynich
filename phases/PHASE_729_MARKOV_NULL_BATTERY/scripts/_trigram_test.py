"""Off-books: sample from a 3-gram trained on Voynich, run the full stats
battery on the sample, compare to real Currier B.

If the 3-gram reproduces Zipf + coverage + cell-fill + hapax % within
sampling noise, then Voynichese is a pure local-Markov process at the
character level. No deeper grammar required.
"""
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('C:/git/voynich')
random.seed(42)

# ---------- 1. Load training data (same split as PHASE_691) ----------
train_path = ROOT / 'phases/PHASE_691_VOYNICH_CHARLM/data/corpus_train.jsonl'
if not train_path.exists():
    # Fallback: build from full Currier B
    from scripts.voynich import Transcript
    tx = Transcript()
    by_line = defaultdict(list)
    for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
        w = t.word.strip()
        if w:
            by_line[(t.folio, t.line)].append(w)
    train_lines = [v for v in by_line.values()]
    print(f'Built from Currier B: {len(train_lines)} lines')
else:
    train_lines = []
    with open(train_path, encoding='utf-8') as f:
        for line in f:
            train_lines.append(json.loads(line)['tokens'])
    print(f'Loaded PHASE_691 train: {len(train_lines)} lines')


def line_to_chars(tokens):
    return ' '.join(tokens)


# ---------- 2. Train n-grams ----------
def train_ngram(lines, order):
    counts = defaultdict(Counter)
    vocab = set()
    for tokens in lines:
        s = line_to_chars(tokens)
        padded = '\x01' * (order - 1) + s + '\x02'
        for c in padded:
            vocab.add(c)
        for i in range(order - 1, len(padded)):
            ctx = padded[i - (order - 1):i]
            ch = padded[i]
            counts[ctx][ch] += 1
    return counts, sorted(vocab)


def sample_from_ngram(counts, vocab, order, n_chars):
    """Generate n_chars of synthetic text by sampling from the n-gram."""
    ctx = '\x01' * (order - 1)
    out = []
    while len(out) < n_chars:
        cand = counts.get(ctx)
        if not cand:
            ctx = '\x01' * (order - 1)
            continue
        chars = list(cand.keys())
        weights = list(cand.values())
        ch = random.choices(chars, weights=weights, k=1)[0]
        if ch == '\x02':
            # End of line - restart
            ctx = '\x01' * (order - 1)
            out.append(' ')
            continue
        out.append(ch)
        ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
    return ''.join(out)


# ---------- 3. Sample and tokenize ----------
def sample_tokens(counts, vocab, order, target_tokens=23000):
    # Need ~6 chars per token on average; sample 10x to be safe
    txt = sample_from_ngram(counts, vocab, order, target_tokens * 8)
    toks = [t for t in txt.split() if t]
    return toks[:target_tokens]


# ---------- 4. Statistics battery ----------
def hapax_stats(tokens, label):
    counts = Counter(tokens)
    total = sum(counts.values())
    types = len(counts)
    hapax = sum(1 for c in counts.values() if c == 1)
    return {
        'label': label,
        'tokens': total,
        'types': types,
        'ttr': types / total,
        'hapax_type_pct': 100 * hapax / types,
        'hapax_token_pct': 100 * hapax / total,
    }


def zipf_slope(counts):
    s = sorted(counts.values(), reverse=True)
    xs = [math.log(r + 1) for r in range(len(s))]
    ys = [math.log(c) for c in s]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den = sum((xs[i] - mx) ** 2 for i in range(n))
    return num / den


def coverage(tokens):
    counts = Counter(tokens)
    sorted_c = sorted(counts.values(), reverse=True)
    total = sum(sorted_c)
    out = {}
    cumul = 0
    for i, c in enumerate(sorted_c, 1):
        cumul += c
        if i in (10, 50, 100, 250, 500, 1000):
            out[i] = 100 * cumul / total
    return out


def cell_fill(tokens, k_start=10, k_end=50, start_len=2, end_len=3, min_len=4, max_len=None):
    if max_len:
        ws = [w for w in tokens if min_len <= len(w) <= max_len]
    else:
        ws = [w for w in tokens if len(w) >= min_len]
    starts = Counter(w[:start_len] for w in ws)
    ends = Counter(w[-end_len:] for w in ws)
    top_s = set(s for s, _ in starts.most_common(k_start))
    top_e = set(e for e, _ in ends.most_common(k_end))
    cells = set()
    for w in ws:
        if w[:start_len] in top_s and w[-end_len:] in top_e:
            cells.add((w[:start_len], w[-end_len:]))
    return {
        'fill_pct': 100 * len(cells) / (k_start * k_end),
        'distinct_starts': len(starts),
    }


# ---------- 5. Compare ----------
# Real Currier B at matched size
from scripts.voynich import Transcript
tx = Transcript()
real_b = [t.word.strip() for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True) if t.word.strip()]

results = {}
results['real_B'] = {
    **hapax_stats(real_b, 'Real Currier B'),
    'zipf': zipf_slope(Counter(real_b)),
    'cov': coverage(real_b),
    'cell_all': cell_fill(real_b),
    'cell_47': cell_fill(real_b, min_len=4, max_len=7),
}

for order in (2, 3, 4, 5):
    print(f'\nTraining {order}-gram and sampling...')
    counts, vocab = train_ngram(train_lines, order)
    syn = sample_tokens(counts, vocab, order, target_tokens=len(real_b))
    print(f'  sampled {len(syn)} synthetic tokens')
    results[f'syn_{order}gram'] = {
        **hapax_stats(syn, f'Synthetic ({order}-gram)'),
        'zipf': zipf_slope(Counter(syn)),
        'cov': coverage(syn),
        'cell_all': cell_fill(syn),
        'cell_47': cell_fill(syn, min_len=4, max_len=7),
    }

# Print table
print(f'\n{"Source":<26} {"Tokens":>7} {"Types":>6} {"TTR":>5} {"Hapax-T%":>9} {"Hapax-tok%":>10} {"Zipf":>6}')
print('-' * 100)
for key, r in results.items():
    print(f'{r["label"]:<26} {r["tokens"]:>7,} {r["types"]:>6,} {r["ttr"]:>5.3f} '
          f'{r["hapax_type_pct"]:>8.1f}% {r["hapax_token_pct"]:>9.1f}% {r["zipf"]:>+6.3f}')

print()
print(f'{"Source":<26} {"top10":>7} {"top50":>7} {"top100":>7} {"top250":>7} {"top500":>7} {"top1k":>7}')
print('-' * 100)
for key, r in results.items():
    c = r['cov']
    print(f'{r["label"]:<26} {c[10]:>6.1f}% {c[50]:>6.1f}% {c[100]:>6.1f}% {c[250]:>6.1f}% {c[500]:>6.1f}% {c[1000]:>6.1f}%')

print()
print(f'{"Source":<26} {"Cell-fill all-len":>18} {"Cell-fill 4-7":>15} {"distinct-starts":>17}')
print('-' * 100)
for key, r in results.items():
    print(f'{r["label"]:<26} {r["cell_all"]["fill_pct"]:>17.1f}% {r["cell_47"]["fill_pct"]:>14.1f}% {r["cell_47"]["distinct_starts"]:>17}')
