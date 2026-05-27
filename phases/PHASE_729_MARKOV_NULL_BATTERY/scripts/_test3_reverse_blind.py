"""Test 3: Reverse-blind matches against 5-gram null + negative control.

For each documented match (f77r, f39r, f103v, f115r, f43v):
1. Train 5-gram on Currier B \ {target_folio}
2. Sample 1000 synthetic token streams matched to target length
3. Score each sample against the registered predictions
4. Compute p_emp = fraction hitting >= same K/M as published

Also run negative control: pick an unmatched B folio, apply ALL prediction
templates, see how many it accidentally satisfies.
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

# Predictions from FOLIOS/*.md
# Format: list of (name, predicate, is_specific) tuples
# predicate takes a list of token strings and returns bool

def feat_dar(toks): return sum(1 for t in toks if t == 'dar')
def feat_dal(toks): return sum(1 for t in toks if t == 'dal')
def feat_daiin(toks): return sum(1 for t in toks if t == 'daiin')
def feat_prefix_rate(toks, p):
    n = 0
    for t in toks:
        try:
            m = morph.extract(t)
            if m.prefix == p:
                n += 1
        except Exception:
            pass
    return n / len(toks) if toks else 0
def feat_gentle(toks):
    n = 0
    for t in toks:
        try:
            a = morph.atomize(t)
            if a.e_depth >= 2:
                n += 1
        except Exception:
            pass
    return n / len(toks) if toks else 0
def feat_iter(toks):
    n = 0
    for t in toks:
        try:
            m = morph.extract(t)
            if m.middle and ('iin' in m.middle or m.middle.endswith('in')):
                n += 1
        except Exception:
            pass
    return n / len(toks) if toks else 0


TARGETS = {
    'f77r': {
        'predictions': [
            ('dar=0',         lambda toks: feat_dar(toks) == 0, True),
            ('dal>=2',        lambda toks: feat_dal(toks) >= 2, False),
            ('daiin>=4',      lambda toks: feat_daiin(toks) >= 4, True),
            ('sh>8%',         lambda toks: feat_prefix_rate(toks, 'sh') > 0.08, False),
            ('gentle>15%',    lambda toks: feat_gentle(toks) > 0.15, False),
            ('qo>25%',        lambda toks: feat_prefix_rate(toks, 'qo') > 0.25, True),
            ('length 100-200',lambda toks: 100 <= len(toks) <= 200, False),
        ],
        'k_pass': 7,  # published 7/7
    },
    'f39r': {
        'predictions': [
            ('qo<12%',        lambda toks: feat_prefix_rate(toks, 'qo') < 0.12, True),
            ('da>=6%',        lambda toks: sum(1 for t in toks if t.startswith('da')) / len(toks) > 0.06, True),
            ('dar>=3',        lambda toks: feat_dar(toks) >= 3, True),
            ('sh>10%',        lambda toks: feat_prefix_rate(toks, 'sh') > 0.10, False),
            ('gentle<10%',    lambda toks: feat_gentle(toks) < 0.10, True),
            ('ch>15%',        lambda toks: feat_prefix_rate(toks, 'ch') > 0.15, True),
            ('length 120-200',lambda toks: 120 <= len(toks) <= 200, False),
        ],
        'k_pass': 6,  # published 6/7
    },
    'f103v': {
        'predictions': [
            ('dar>=2',        lambda toks: feat_dar(toks) >= 2, True),
            ('gentle 12-22%', lambda toks: 0.12 <= feat_gentle(toks) <= 0.22, True),
            ('sh>10%',        lambda toks: feat_prefix_rate(toks, 'sh') > 0.10, False),
            ('length 350-550',lambda toks: 350 <= len(toks) <= 550, False),
            ('daiin>=6',      lambda toks: feat_daiin(toks) >= 6, True),
            ('dal>=1',        lambda toks: feat_dal(toks) >= 1, False),
        ],
        'k_pass': 6,
    },
    'f115r': {
        'predictions': [
            ('ch>15%',        lambda toks: feat_prefix_rate(toks, 'ch') > 0.15, True),
            ('dar>=4',        lambda toks: feat_dar(toks) >= 4, True),
            ('gentle<22%',    lambda toks: feat_gentle(toks) < 0.22, False),
            ('length 350-550',lambda toks: 350 <= len(toks) <= 550, False),
        ],
        'k_pass': 4,
    },
    'f43v': {
        'predictions': [
            ('dar>=2',        lambda toks: feat_dar(toks) >= 2, True),
            ('ch>20%',        lambda toks: feat_prefix_rate(toks, 'ch') > 0.20, True),
            ('ok+ot>10%',     lambda toks: feat_prefix_rate(toks, 'ok') + feat_prefix_rate(toks, 'ot') > 0.10, False),
            ('length 120-200',lambda toks: 120 <= len(toks) <= 200, False),
        ],
        'k_pass': 4,
    },
}


# ----------- Train 5-gram on Currier B minus target -----------
def get_lines_by_folio():
    by_folio_line = defaultdict(list)
    for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
        w = t.word.strip()
        if not w:
            continue
        by_folio_line[(t.folio, t.line)].append(w)
    folio_lines = defaultdict(list)
    for (f, ln), ws in sorted(by_folio_line.items()):
        folio_lines[f].append(ws)
    return folio_lines


def train_ngram(line_lists, order):
    counts = defaultdict(Counter)
    for words in line_lists:
        s = ' '.join(words)
        padded = '\x01' * (order - 1) + s + '\x02'
        for i in range(order - 1, len(padded)):
            ctx = padded[i - (order - 1):i]
            counts[ctx][padded[i]] += 1
    return counts


def sample_stretch(counts, order, n_tokens):
    out_tokens = []
    ctx = '\x01' * (order - 1)
    buf = []
    attempts = 0
    while len(out_tokens) < n_tokens and attempts < n_tokens * 30:
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
                out_tokens.append(''.join(buf)); buf = []
            ctx = '\x01' * (order - 1)
            continue
        if ch == ' ':
            if buf:
                out_tokens.append(''.join(buf)); buf = []
            ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
            continue
        buf.append(ch)
        ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
    return out_tokens[:n_tokens]


folio_lines = get_lines_by_folio()

# Get real folio token streams
def get_folio_tokens(folio):
    flat = []
    if folio in folio_lines:
        for line in folio_lines[folio]:
            flat.extend(line)
    return flat


real_lens = {f: len(get_folio_tokens(f)) for f in TARGETS}
print('Real folio lengths:', real_lens)

N_SAMPLES = 1000
results = {}

# Pick negative control: unmatched B folio similar in length
unmatched_candidates = [f for f in folio_lines if f not in TARGETS and f not in ('f75r','f75v','f78v','f80r','f82r','f84r','f84v','f112r','f113r')]

print(f'\nRunning {N_SAMPLES} samples per target + negative control...\n')

for target, spec in TARGETS.items():
    print(f'--- {target} (k_pass = {spec["k_pass"]}/{len(spec["predictions"])}) ---')
    # Train on B minus target folio
    train_lines = []
    for f, lines in folio_lines.items():
        if f != target:
            train_lines.extend(lines)
    ngram = train_ngram(train_lines, 5)
    target_len = real_lens[target]
    if target_len < 30:
        print(f'  SKIP: target too short ({target_len} tokens)')
        continue

    # Sample and score
    pass_counts = []
    specific_pass_counts = []
    individual_pass = [0] * len(spec['predictions'])
    for sample_i in range(N_SAMPLES):
        toks = sample_stretch(ngram, 5, target_len)
        n_pass = 0
        n_spec_pass = 0
        for pi, (name, fn, is_spec) in enumerate(spec['predictions']):
            try:
                if fn(toks):
                    n_pass += 1
                    individual_pass[pi] += 1
                    if is_spec:
                        n_spec_pass += 1
            except Exception:
                pass
        pass_counts.append(n_pass)
        specific_pass_counts.append(n_spec_pass)

    # Score real folio
    real_toks = get_folio_tokens(target)
    real_pass = 0
    real_spec_pass = 0
    for name, fn, is_spec in spec['predictions']:
        try:
            if fn(real_toks):
                real_pass += 1
                if is_spec:
                    real_spec_pass += 1
        except Exception:
            pass

    p_emp_full = sum(1 for c in pass_counts if c >= spec['k_pass']) / N_SAMPLES
    n_spec = sum(1 for _, _, s in spec['predictions'] if s)
    p_emp_spec = (sum(1 for c in specific_pass_counts if c >= real_spec_pass) / N_SAMPLES) if n_spec else float('nan')

    print(f'  Real: {real_pass}/{len(spec["predictions"])} ({real_spec_pass}/{n_spec} SPECIFIC)')
    print(f'  Synthetic 5-gram null:')
    print(f'    Fraction reaching {spec["k_pass"]}+ predictions: {p_emp_full:.3f}')
    print(f'    Fraction reaching {real_spec_pass}+ SPECIFIC predictions: {p_emp_spec:.3f}')
    print(f'    Mean predictions hit: {np.mean(pass_counts):.2f}, max: {max(pass_counts)}')
    for pi, (name, fn, is_spec) in enumerate(spec['predictions']):
        spec_tag = ' [SPECIFIC]' if is_spec else ''
        print(f'      "{name}": {individual_pass[pi]/N_SAMPLES:.2%} of synthetic samples pass{spec_tag}')
    print()

    results[target] = {
        'real_pass': real_pass,
        'real_spec_pass': real_spec_pass,
        'k_pass_threshold': spec['k_pass'],
        'p_emp_full': p_emp_full,
        'p_emp_spec': p_emp_spec,
        'individual_pass': individual_pass,
    }

# ----------- Negative control: pick 3 unmatched folios -----------
neg_targets = unmatched_candidates[:3]
print(f'\n=== NEGATIVE CONTROL ===')
print(f'Applying ALL prediction templates to unmatched folios: {neg_targets}\n')
for neg in neg_targets:
    toks = get_folio_tokens(neg)
    if len(toks) < 30:
        continue
    print(f'{neg} ({len(toks)} tokens):')
    for target, spec in TARGETS.items():
        n_pass = 0
        for name, fn, is_spec in spec['predictions']:
            try:
                if fn(toks):
                    n_pass += 1
            except Exception:
                pass
        print(f'  Hits {target} template: {n_pass}/{len(spec["predictions"])}')
    print()

print('=== SUMMARY ===')
print(f'{"Folio":<8} {"Real":<8} {"k_pass":<8} {"p(syn>=k)":<12} {"p(syn>=spec)":<13}')
print('-' * 60)
for t, r in results.items():
    print(f'{t:<8} {r["real_pass"]}/{len(TARGETS[t]["predictions"]):<6} {r["k_pass_threshold"]:<8} {r["p_emp_full"]:<12.3f} {r["p_emp_spec"]:<13.3f}')
