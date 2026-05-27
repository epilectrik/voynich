"""Test 4: Generate synthetic Currier B as 82 'folios' via 5-gram.
Compute operational profile per synthetic folio.
Compare to real folio operational profiles.

If synthetic folio profiles are statistically indistinguishable from real,
the 8D matcher's apparent confident matches on real folios are equally
producible on Markov-generated folios -> matcher is permissive.

If synthetic profiles diverge from real, the matcher actually discriminates.
"""
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

sys.path.insert(0, 'C:/git/voynich')
random.seed(42)
np.random.seed(42)

from scripts.voynich import Transcript, Morphology

morph = Morphology()
tx = Transcript()

# ----------- Real folio operational profiles -----------
def compute_profile(tokens):
    """Compute basic operational features used by 8D matcher."""
    if len(tokens) < 20:
        return None
    n = len(tokens)
    qo = 0; ch = 0; sh = 0; ok = 0; ot = 0
    dar = 0; dal = 0; daiin = 0
    e_depth_sum = 0; gentle_n = 0
    for t in tokens:
        try:
            a = morph.atomize(t)
            if a.prefix == 'qo': qo += 1
            elif a.prefix == 'ch': ch += 1
            elif a.prefix == 'sh': sh += 1
            elif a.prefix == 'ok': ok += 1
            elif a.prefix == 'ot': ot += 1
            if a.e_depth >= 2:
                gentle_n += 1
            e_depth_sum += a.e_depth
        except Exception:
            pass
        if t == 'dar': dar += 1
        elif t == 'dal': dal += 1
        elif t == 'daiin': daiin += 1
    return {
        'n_tokens': n,
        'qo_rate': qo / n,
        'ch_rate': ch / n,
        'sh_rate': sh / n,
        'ok_rate': ok / n,
        'ot_rate': ot / n,
        'dar': dar,
        'dal': dal,
        'daiin': daiin,
        'gentle': gentle_n / n,
        'mean_e_depth': e_depth_sum / n,
    }


# Real folios
folio_lines = defaultdict(list)
for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w:
        continue
    folio_lines[t.folio].append(w)
real_profiles = {f: compute_profile(toks) for f, toks in folio_lines.items()}
real_profiles = {f: p for f, p in real_profiles.items() if p is not None}
print(f'Real folios with profiles: {len(real_profiles)}')

# ----------- 5-gram training and synthesis -----------
def get_train_lines():
    by_line = defaultdict(list)
    for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
        w = t.word.strip()
        if not w:
            continue
        by_line[(t.folio, t.line)].append(w)
    return [ws for ws in by_line.values()]


def train_ngram(line_lists, order):
    counts = defaultdict(Counter)
    for ws in line_lists:
        s = ' '.join(ws)
        padded = '\x01' * (order - 1) + s + '\x02'
        for i in range(order - 1, len(padded)):
            ctx = padded[i - (order - 1):i]
            counts[ctx][padded[i]] += 1
    return counts


def sample_stretch(counts, order, n_tokens):
    out = []; ctx = '\x01' * (order - 1); buf = []; attempts = 0
    while len(out) < n_tokens and attempts < n_tokens * 30:
        attempts += 1
        cand = counts.get(ctx)
        if not cand:
            ctx = '\x01' * (order - 1); continue
        chars = list(cand.keys()); weights = list(cand.values())
        ch = random.choices(chars, weights=weights, k=1)[0]
        if ch == '\x02':
            if buf:
                out.append(''.join(buf)); buf = []
            ctx = '\x01' * (order - 1); continue
        if ch == ' ':
            if buf:
                out.append(''.join(buf)); buf = []
            ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''; continue
        buf.append(ch); ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
    return out[:n_tokens]


print('Training 5-gram...')
ngram = train_ngram(get_train_lines(), 5)

# Generate synthetic "folios" matched to real folio token counts
print('Generating synthetic folios...')
synthetic_profiles = {}
for folio, tokens in folio_lines.items():
    if len(tokens) < 20:
        continue
    syn_toks = sample_stretch(ngram, 5, len(tokens))
    synthetic_profiles[f'syn_{folio}'] = compute_profile(syn_toks)
synthetic_profiles = {f: p for f, p in synthetic_profiles.items() if p is not None}
print(f'Synthetic folios with profiles: {len(synthetic_profiles)}')

# ----------- Compare profile distributions -----------
metrics = ['qo_rate', 'ch_rate', 'sh_rate', 'ok_rate', 'ot_rate', 'gentle', 'mean_e_depth']

print('\n=== Profile statistics: Real vs Synthetic ===')
print(f'{"Metric":<15} {"Real mean+/-sd":<22} {"Synth mean+/-sd":<22} {"|dmean|/sd_pool":<15}')
print('-' * 80)
for m in metrics:
    real_vals = np.array([p[m] for p in real_profiles.values()])
    syn_vals = np.array([p[m] for p in synthetic_profiles.values()])
    rm, rs = real_vals.mean(), real_vals.std()
    sm, ss = syn_vals.mean(), syn_vals.std()
    pooled = np.sqrt((rs**2 + ss**2) / 2)
    delta = abs(rm - sm) / pooled if pooled > 0 else 0
    print(f'{m:<15} {rm:.4f} ± {rs:.4f}    {sm:.4f} ± {ss:.4f}    {delta:.3f}')

# Range checks: does synthetic profile space overlap with real folio space?
print('\n=== Range overlap ===')
for m in metrics:
    real_vals = np.array([p[m] for p in real_profiles.values()])
    syn_vals = np.array([p[m] for p in synthetic_profiles.values()])
    real_min, real_max = real_vals.min(), real_vals.max()
    syn_min, syn_max = syn_vals.min(), syn_vals.max()
    syn_in_real = np.mean((syn_vals >= real_min) & (syn_vals <= real_max))
    real_in_syn = np.mean((real_vals >= syn_min) & (real_vals <= syn_max))
    print(f'{m:<15} real range [{real_min:.3f}, {real_max:.3f}]  synth range [{syn_min:.3f}, {syn_max:.3f}]  synth-in-real-range={syn_in_real:.1%}')

# Categorical features: dar counts, dal counts, daiin counts per folio
print('\n=== Categorical features (per-folio counts) ===')
for cat in ['dar', 'dal', 'daiin']:
    real_vals = np.array([p[cat] for p in real_profiles.values()])
    syn_vals = np.array([p[cat] for p in synthetic_profiles.values()])
    print(f'{cat:<6} real: mean={real_vals.mean():.2f} sd={real_vals.std():.2f} max={real_vals.max()}    synth: mean={syn_vals.mean():.2f} sd={syn_vals.std():.2f} max={syn_vals.max()}')

# Mahalanobis-style: how often does a synthetic folio profile fall within the real-folio cloud?
print('\n=== Multivariate divergence (Mahalanobis distance to real folio centroid) ===')
X_real = np.array([[p[m] for m in metrics] for p in real_profiles.values()])
X_syn = np.array([[p[m] for m in metrics] for p in synthetic_profiles.values()])
mu = X_real.mean(axis=0)
cov = np.cov(X_real.T) + 1e-6 * np.eye(len(metrics))
inv = np.linalg.inv(cov)
def maha(x):
    d = x - mu
    return float(np.sqrt(d @ inv @ d))
real_d = np.array([maha(x) for x in X_real])
syn_d = np.array([maha(x) for x in X_syn])
print(f'Real folios Mahalanobis-to-real-centroid: mean={real_d.mean():.2f} sd={real_d.std():.2f} median={np.median(real_d):.2f}')
print(f'Synth folios Mahalanobis-to-real-centroid: mean={syn_d.mean():.2f} sd={syn_d.std():.2f} median={np.median(syn_d):.2f}')

# How many synth folios fall within the real folio cloud (Mahalanobis within max real)?
real_max_d = real_d.max()
syn_in_cloud = (syn_d <= real_max_d).mean()
print(f'\nFraction of synthetic folios within real-folio Mahalanobis cloud: {syn_in_cloud:.1%}')
if syn_in_cloud > 0.7:
    print('  --> Synthetic profiles are LARGELY INDISTINGUISHABLE from real folios.')
    print('  --> 8D matcher would produce equally "confident" matches on Markov-generated folios.')
elif syn_in_cloud > 0.3:
    print('  --> Synthetic profiles PARTIALLY overlap real folios; matcher is partly permissive.')
else:
    print('  --> Synthetic profiles DIVERGE from real folios; matcher discriminates real signal.')
