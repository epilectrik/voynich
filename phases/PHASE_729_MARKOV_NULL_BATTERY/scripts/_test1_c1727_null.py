"""Test 1: Does 5-gram-generated text reproduce C1727 line-ordering smoothness?

C1727 baseline (real Currier B):
  obs smoothness < shuffled smoothness → real lines have intentional ordering
  Stouffer z = -6.048 (lower = smoother than shuffle null)

Test: replace real tokens with 5-gram-generated tokens (matched line counts,
matched token counts per line), recompute the metric.

If 5-gram-synthetic also shows z ≈ -6, the line-ordering smoothness is a Markov
artifact. If synthetic shows z near 0, line-ordering smoothness requires
intentional folio-level structure that the 5-gram can't reproduce.
"""
from __future__ import annotations
import json
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
sys.path.insert(0, 'C:/git/voynich')
random.seed(42)
np.random.seed(42)

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

HEAD_TYPES = ['a', 'e', 'o', 'k', 't', 'headless']
TERM_TYPES = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']
HEAD_IDX = {h: i for i, h in enumerate(HEAD_TYPES)}
TERM_IDX = {t: i for i, t in enumerate(TERM_TYPES)}

MODE_A_ATOMS = {'d', 'e', 'ee', 'h', 'y'}
MODE_B_ATOMS = {'a', 'i', 'ii', 'l', 'm', 'n', 'o', 'r', 's'}


def atomize_suffix(suffix):
    if not suffix:
        return []
    atoms = []
    i = 0
    while i < len(suffix):
        if i + 1 < len(suffix) and suffix[i] == suffix[i+1] and suffix[i] in ('e', 'i'):
            atoms.append(suffix[i:i+2])
            i += 2
        else:
            atoms.append(suffix[i])
            i += 1
    return atoms


def get_line_mode(suffixes):
    a_count, b_count = 0, 0
    for suffix in suffixes:
        if suffix:
            for atom in atomize_suffix(suffix):
                if atom in MODE_A_ATOMS:
                    a_count += 1
                elif atom in MODE_B_ATOMS:
                    b_count += 1
    if a_count + b_count == 0:
        return None
    return 'A' if a_count > b_count else 'B'


def build_line_features_from_words(words, morph):
    """Same as build_line_features but takes a list of token strings, not Transcript tokens."""
    head_counts = np.zeros(len(HEAD_TYPES))
    term_counts = np.zeros(len(TERM_TYPES))
    suffixes = []
    n_valid = 0
    for w in words:
        w = w.strip()
        if not w or '*' in w:
            continue
        try:
            m = morph.extract(w)
        except Exception:
            continue
        if m.middle:
            try:
                head, mods, term, frame = decompose_middle_hmt(m.middle)
            except Exception:
                head, term = None, None
            head = head if head else 'headless'
            if head in HEAD_IDX:
                head_counts[HEAD_IDX[head]] += 1
            if term in TERM_IDX:
                term_counts[TERM_IDX[term]] += 1
            n_valid += 1
        suffixes.append(m.suffix if m else None)
    if n_valid == 0:
        return None
    head_frac = head_counts / n_valid
    term_frac = term_counts / n_valid
    mode = get_line_mode(suffixes)
    mode_val = 1.0 if mode == 'A' else 0.0 if mode == 'B' else 0.5
    line_len = float(len(words))
    return np.concatenate([head_frac, term_frac, [mode_val], [line_len]])


def sequential_structure_score(feature_matrix):
    if len(feature_matrix) < 2:
        return 0.0
    diffs = np.diff(feature_matrix, axis=0)
    return float(np.sum(diffs ** 2))


# ----------- 1. Load real Currier B, compute baseline -----------
tx = Transcript()
morph = Morphology()
lines_dict = defaultdict(list)
for t in tx.currier_b():
    w = t.word.strip()
    if not w:
        continue
    if t.placement.startswith('L'):
        continue
    lines_dict[(t.folio, t.line)].append(w)

folio_lines = defaultdict(list)
for (folio, line_num), words in sorted(lines_dict.items()):
    folio_lines[folio].append((line_num, words))
paragraphs = {f: [w for _, w in lines] for f, lines in folio_lines.items() if len(lines) >= 3}
print(f'Loaded {len(paragraphs)} folios (paragraphs) with >=3 lines')


def compute_score(paragraph_word_lists, morph):
    total = 0.0
    n_pairs = 0
    for words_per_line in paragraph_word_lists.values():
        features = [build_line_features_from_words(w, morph) for w in words_per_line]
        features = [f for f in features if f is not None]
        if len(features) >= 2:
            total += sequential_structure_score(np.array(features))
            n_pairs += len(features) - 1
    return total, n_pairs


def shuffle_null(paragraph_word_lists, morph, n_shuffles=200, seed=42):
    rng = np.random.default_rng(seed)
    null_scores = []
    para_features = {}
    for f, lines in paragraph_word_lists.items():
        feats = [build_line_features_from_words(w, morph) for w in lines]
        feats = [x for x in feats if x is not None]
        if len(feats) >= 2:
            para_features[f] = np.array(feats)
    for _ in range(n_shuffles):
        score = 0.0
        for feats in para_features.values():
            perm = rng.permutation(len(feats))
            score += sequential_structure_score(feats[perm])
        null_scores.append(score)
    return np.array(null_scores)


print('\n--- Baseline: real Currier B ---')
obs, n_pairs = compute_score(paragraphs, morph)
null = shuffle_null(paragraphs, morph, n_shuffles=200)
nm, ns = null.mean(), null.std()
z_real = (obs - nm) / ns
print(f'  obs={obs:.2f}  null={nm:.2f}±{ns:.2f}  z={z_real:+.3f}  n_pairs={n_pairs}')

# ----------- 2. Train 5-gram on full Currier B (line-by-line) -----------
def train_ngram(line_word_lists, order):
    counts = defaultdict(Counter)
    for words in line_word_lists:
        s = ' '.join(words)
        padded = '\x01' * (order - 1) + s + '\x02'
        for i in range(order - 1, len(padded)):
            ctx = padded[i - (order - 1):i]
            counts[ctx][padded[i]] += 1
    return counts


def sample_line(counts, order, target_token_count):
    """Sample a line of exactly target_token_count tokens."""
    out_tokens = []
    ctx = '\x01' * (order - 1)
    buf = []
    attempts = 0
    while len(out_tokens) < target_token_count and attempts < target_token_count * 30:
        attempts += 1
        cand = counts.get(ctx)
        if not cand:
            ctx = '\x01' * (order - 1)
            continue
        chars = list(cand.keys())
        weights = list(cand.values())
        ch = random.choices(chars, weights=weights, k=1)[0]
        if ch == '\x02':
            if buf:
                out_tokens.append(''.join(buf))
                buf = []
            ctx = '\x01' * (order - 1)
            if len(out_tokens) >= target_token_count:
                break
            continue
        if ch == ' ':
            if buf:
                out_tokens.append(''.join(buf))
                buf = []
            ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
            continue
        buf.append(ch)
        ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
    if buf and len(out_tokens) < target_token_count:
        out_tokens.append(''.join(buf))
    return out_tokens[:target_token_count]


order = 5
print(f'\nTraining {order}-gram on Currier B lines...')
all_lines = []
for f, lines in paragraphs.items():
    for w in lines:
        all_lines.append(w)
print(f'Training data: {len(all_lines)} lines')
ngram_counts = train_ngram(all_lines, order)

# ----------- 3. Generate synthetic Currier B with matched structure -----------
print('Generating synthetic Currier B with matched paragraph structure...')
synthetic_paragraphs = {}
for folio, lines in paragraphs.items():
    syn_lines = []
    for w in lines:
        target_n = len(w)
        syn_line = sample_line(ngram_counts, order, target_n)
        syn_lines.append(syn_line)
    synthetic_paragraphs[folio] = syn_lines
print(f'Generated {len(synthetic_paragraphs)} synthetic folios')

# ----------- 4. Compute smoothness on synthetic + shuffled-synthetic -----------
print('\n--- Synthetic 5-gram ---')
syn_obs, syn_n = compute_score(synthetic_paragraphs, morph)
syn_null = shuffle_null(synthetic_paragraphs, morph, n_shuffles=200, seed=123)
snm, sns = syn_null.mean(), syn_null.std()
z_syn = (syn_obs - snm) / sns
print(f'  obs={syn_obs:.2f}  null={snm:.2f}±{sns:.2f}  z={z_syn:+.3f}  n_pairs={syn_n}')

print('\n=== VERDICT ===')
print(f'Real Currier B z = {z_real:+.3f}  (negative = smoother than shuffle null = C1727 signal)')
print(f'Synthetic 5-gram z = {z_syn:+.3f}')
if z_syn < -3.0:
    print('  → 5-gram REPRODUCES C1727 smoothness. Effect is Markov artifact.')
elif abs(z_syn) < 1.5:
    print('  → 5-gram does NOT reproduce C1727 smoothness. Folio-level intentional ordering survives.')
else:
    print('  → 5-gram PARTIALLY reproduces. Intermediate; warrants more analysis.')
