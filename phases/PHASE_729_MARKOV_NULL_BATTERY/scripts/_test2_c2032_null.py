"""Test 2: Does 5-gram-generated text reproduce C2032 lag2/lag1 = -0.66?

C2032 baseline (real Voynich Section B): r21 = -0.66 (period-2 sign-reversal)
NL baselines: Codicillus r21 = +0.05, Mesue r21 = -0.17 (near-zero, monotonic)

Crazy-expert prediction: 5-gram is character-Markov, not stem-class-Markov.
Should NOT reproduce -0.66. If it does, the engineered-substrate triad collapses.
"""
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, 'C:/git/voynich')
random.seed(42)
np.random.seed(42)

from scripts.voynich import Transcript

N_PERM = 200
CHUNK_SIZE = 1000


def class_chain_excess(seqs, target_class, lags=(1, 2, 3), n_perm=N_PERM):
    out = {}
    for lag in lags:
        obs_hits, obs_pairs = 0, 0
        for seq in seqs:
            for i in range(len(seq) - lag):
                if seq[i] == target_class:
                    obs_pairs += 1
                    if seq[i + lag] == target_class:
                        obs_hits += 1
        obs_rate = obs_hits / obs_pairs if obs_pairs else 0.0
        null_rates = []
        for _ in range(n_perm):
            null_hits, null_pairs = 0, 0
            for seq in seqs:
                perm = seq.copy()
                random.shuffle(perm)
                for i in range(len(perm) - lag):
                    if perm[i] == target_class:
                        null_pairs += 1
                        if perm[i + lag] == target_class:
                            null_hits += 1
            null_rates.append(null_hits / null_pairs if null_pairs else 0.0)
        null_rate = sum(null_rates) / len(null_rates)
        out[lag] = {'excess': obs_rate - null_rate, 'obs_rate': obs_rate, 'null_rate': null_rate, 'n_pairs': obs_pairs}
    return out


def chunk_into_sequences(words, chunk_size=CHUNK_SIZE):
    seqs = []
    for i in range(0, len(words), chunk_size):
        c = words[i:i + chunk_size]
        if len(c) >= 50:
            seqs.append(c)
    return seqs


def compute_r21(words, label):
    seqs = chunk_into_sequences(words)
    counter = Counter(words)
    target, _ = counter.most_common(1)[0]
    chain = class_chain_excess(seqs, target)
    l1, l2, l3 = chain[1]['excess'], chain[2]['excess'], chain[3]['excess']
    r21 = l2 / l1 if abs(l1) > 1e-9 else float('nan')
    print(f'{label:<28} target={target:<10} lag1={l1:+.4f}  lag2={l2:+.4f}  lag3={l3:+.4f}  r21={r21:+.3f}')
    return {'lag1': l1, 'lag2': l2, 'lag3': l3, 'r21': r21, 'target': target}


# ----------- 1. Real Currier B baseline -----------
tx = Transcript()
real_b = [t.word.strip() for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True) if t.word.strip()]
print(f'Real Currier B: {len(real_b)} tokens')

# ----------- 2. Train 5-gram and sample synthetic -----------
all_lines = []
lines_dict = defaultdict(list)
for t in tx.currier_b():
    w = t.word.strip()
    if not w or t.placement.startswith('L'):
        continue
    lines_dict[(t.folio, t.line)].append(w)
for k in sorted(lines_dict.keys()):
    all_lines.append(lines_dict[k])

def train_ngram(line_word_lists, order):
    counts = defaultdict(Counter)
    for words in line_word_lists:
        s = ' '.join(words)
        padded = '\x01' * (order - 1) + s + '\x02'
        for i in range(order - 1, len(padded)):
            ctx = padded[i - (order - 1):i]
            counts[ctx][padded[i]] += 1
    return counts


def sample_stream(counts, order, n_chars):
    out = []
    ctx = '\x01' * (order - 1)
    while len(out) < n_chars:
        cand = counts.get(ctx)
        if not cand:
            ctx = '\x01' * (order - 1)
            continue
        chars = list(cand.keys())
        weights = list(cand.values())
        ch = random.choices(chars, weights=weights, k=1)[0]
        if ch == '\x02':
            out.append(' ')
            ctx = '\x01' * (order - 1)
            continue
        out.append(ch)
        ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
    return ''.join(out)


print('\nTraining 5-gram...')
ngram = train_ngram(all_lines, 5)
print('Sampling synthetic stream...')
target_chars = sum(len(w) for w in real_b) + len(real_b)  # tokens + spaces
synth_text = sample_stream(ngram, 5, target_chars * 2)
synth_tokens = [t for t in synth_text.split() if t][:len(real_b)]
print(f'Synthetic: {len(synth_tokens)} tokens')

# ----------- 3. Compute r21 on both -----------
print('\n=== C2032 r21 comparison ===')
real_result = compute_r21(real_b, 'Real Currier B')
syn_result = compute_r21(synth_tokens, 'Synthetic 5-gram')

print('\n=== VERDICT ===')
print(f'Real Currier B r21 = {real_result["r21"]:+.3f}  (published Section B: -0.66; matched-S: +0.66)')
print(f'Synthetic 5-gram r21 = {syn_result["r21"]:+.3f}')
print(f'NL baselines (published): Codicillus +0.05, Mesue -0.17')
if abs(syn_result['r21'] - real_result['r21']) < 0.20:
    print('  → 5-gram REPRODUCES C2032 r21. Sequential stem-class structure is Markov-reproducible.')
elif abs(syn_result['r21']) < 0.20:
    print('  → 5-gram does NOT reproduce r21. C2032 signal survives Markov null.')
else:
    print('  → 5-gram PARTIALLY reproduces. r21 magnitude {:.2f} vs real {:.2f}'.format(
        syn_result['r21'], real_result['r21']))
