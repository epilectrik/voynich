"""
Symmetric Forbidden Suppression (M5-SF)

C1032 finding: 16/17 forbidden pairs are one-directional.
M2 zeros these asymmetrically, creating directional bias.
Real data achieves symmetry despite asymmetric forbidden structure.

Approach: make forbidden suppression bidirectional.
For each forbidden pair (A->B), also suppress (B->A).
This is maximally targeted — only affects 16 additional cells.

This should:
- Fix B5 (reduce forward-backward asymmetry)
- Preserve B1 (spectral gap barely affected — only 16 cells change)
- Preserve B3 (zero violations — we're adding MORE zeros)

Compare with:
- M2 (asymmetric forbidden suppression)
- M2.5 (15% blending, C1032 — fixes B5 but regresses B1/B3)
- M5-SF (symmetric forbidden suppression — targeted fix)
"""

import sys, json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import entropy as scipy_entropy

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))

from scripts.voynich import Transcript, Morphology

N_CLASSES = 49
N_INST = 20

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}
CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

STATE_IDX = {'AXM': 0, 'AXm': 1, 'FQ': 2, 'CC': 3, 'FL_HAZ': 4, 'FL_SAFE': 5}

def normalize_rows(m):
    row_sums = m.sum(axis=1, keepdims=True)
    return m / np.maximum(row_sums, 1e-12)


# ── Load Data ─────────────────────────────────────────────────
print("Loading data...")
morph = Morphology()
tx = Transcript()

with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
          encoding='utf-8') as f:
    cmap = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
          encoding='utf-8') as f:
    forbidden_inv = json.load(f)

# Build real token stream
lines = []
current_line = []
prev_key = None

for token in tx.currier_b():
    if token.placement.startswith('L'):
        continue
    if not token.word or not token.word.strip() or '*' in token.word:
        continue
    cls = token_to_class.get(token.word)
    if cls is None:
        continue
    key = (token.folio, token.line)
    if key != prev_key and current_line:
        lines.append(current_line)
        current_line = []
    prev_key = key
    m = morph.extract(token.word)
    current_line.append({
        'word': token.word,
        'cls': cls,
        'middle': m.middle if m else token.word,
    })
if current_line:
    lines.append(current_line)

all_tokens = [t for line in lines for t in line]
n_tokens = len(all_tokens)
n_lines = len(lines)
line_lengths = [len(line) for line in lines]
print(f"  {n_tokens} tokens in {n_lines} lines")

# Class transition matrix
class_trans = np.zeros((N_CLASSES, N_CLASSES))
for line in lines:
    for i in range(len(line) - 1):
        class_trans[line[i]['cls'] - 1, line[i + 1]['cls'] - 1] += 1

# Opener distribution
opener_counts = Counter(line[0]['cls'] for line in lines if line)
opener_probs = np.zeros(N_CLASSES)
for cls, count in opener_counts.items():
    opener_probs[cls - 1] = count
opener_probs /= max(opener_probs.sum(), 1)

# Token frequency and class samplers
token_freq = Counter(t['word'] for t in all_tokens)
class_to_tokens_list = defaultdict(list)
for tok, cls in token_to_class.items():
    class_to_tokens_list[cls].append(tok)

class_token_probs = {}
for cls_id in range(1, N_CLASSES + 1):
    toks = class_to_tokens_list.get(cls_id, [])
    if toks:
        counts = [token_freq.get(t, 0) for t in toks]
        total = sum(counts)
        if total > 0:
            class_token_probs[cls_id] = (toks, np.array(counts, dtype=float) / total)


# ── T1: Forbidden Pair Analysis ───────────────────────────────
print("\n" + "=" * 70)
print("T1: FORBIDDEN PAIR ANALYSIS")
print("=" * 70)

# Map forbidden pairs to class pairs (same as M2)
forbidden_pairs_raw = [(t['source'], t['target']) for t in forbidden_inv['transitions']]
forbidden_middle_pairs = set(forbidden_pairs_raw)

print(f"\n{len(forbidden_pairs_raw)} forbidden transitions (token-level)")

# Map to MIDDLE-level class pairs
middle_to_classes = defaultdict(set)
for t in all_tokens:
    middle_to_classes[t['middle']].add(t['cls'])

# Build M2-style forbidden class pairs (token names treated as MIDDLEs)
m2_forbidden_cls = set()
m2_forbidden_extra = 0
for src_tok, tgt_tok in forbidden_pairs_raw:
    src_cls = token_to_class.get(src_tok)
    tgt_cls = token_to_class.get(tgt_tok)
    if src_cls and tgt_cls:
        m2_forbidden_cls.add((src_cls, tgt_cls))

# Check symmetry of forbidden class pairs
symmetric_pairs = 0
asymmetric_pairs = []
for src, tgt in m2_forbidden_cls:
    if (tgt, src) in m2_forbidden_cls:
        symmetric_pairs += 1
    else:
        asymmetric_pairs.append((src, tgt))

print(f"\nForbidden class pairs: {len(m2_forbidden_cls)}")
print(f"  Symmetric: {symmetric_pairs}")
print(f"  Asymmetric (one-directional): {len(asymmetric_pairs)}")

for src, tgt in asymmetric_pairs:
    fwd_count = class_trans[src - 1, tgt - 1]
    rev_count = class_trans[tgt - 1, src - 1]
    print(f"  {src:2d} -> {tgt:2d}: fwd={fwd_count:.0f}, rev={rev_count:.0f}")


# ── Build Models ──────────────────────────────────────────────

# M2: Asymmetric forbidden suppression
m2_trans = class_trans.copy()
for src, tgt in m2_forbidden_cls:
    m2_trans[src - 1, tgt - 1] = 0
m2_norm = normalize_rows(m2_trans)

# M5-SF: Symmetric forbidden suppression (bidirectional)
m5sf_trans = class_trans.copy()
all_forbidden_cls = set()
for src, tgt in m2_forbidden_cls:
    all_forbidden_cls.add((src, tgt))
    all_forbidden_cls.add((tgt, src))  # Add reverse!

for src, tgt in all_forbidden_cls:
    m5sf_trans[src - 1, tgt - 1] = 0
m5sf_norm = normalize_rows(m5sf_trans)

# M2.5: 15% blending (from C1032)
stationary = class_trans.sum(axis=1)
stationary /= stationary.sum()
m2_reverse = np.zeros_like(m2_trans)
for i in range(N_CLASSES):
    for j in range(N_CLASSES):
        if stationary[j] > 0:
            m2_reverse[i, j] = m2_norm[j, i] * stationary[j] / max(stationary[i], 1e-12)
m2_reverse = normalize_rows(m2_reverse)
m25_norm = 0.85 * m2_norm + 0.15 * m2_reverse

# Count suppressed cells
m2_zeros = int((m2_trans == 0).sum() - (class_trans == 0).sum())
m5sf_zeros = int((m5sf_trans == 0).sum() - (class_trans == 0).sum())
print(f"\nCells zeroed by M2: {m2_zeros}")
print(f"Cells zeroed by M5-SF: {m5sf_zeros}")
print(f"Additional cells from symmetrization: {m5sf_zeros - m2_zeros}")


# ── Generation & Metrics ─────────────────────────────────────

def generate(trans_norm, rng):
    """Generate corpus from a class Markov chain."""
    corpus = []
    for _ in range(n_lines):
        length = rng.choice(line_lengths)
        line = []
        cls = rng.choice(N_CLASSES, p=opener_probs) + 1
        for pos in range(length):
            if pos > 0:
                row = trans_norm[cls - 1]
                if row.sum() > 0:
                    cls = rng.choice(N_CLASSES, p=row) + 1
                else:
                    cls = rng.choice(N_CLASSES, p=opener_probs) + 1
            if cls in class_token_probs:
                toks, probs = class_token_probs[cls]
                word = rng.choice(toks, p=probs)
            else:
                word = f'UNK_C{cls}'
            line.append({'word': word, 'cls': cls})
        corpus.append(line)
    return corpus


def compute_b5(corpus):
    """B5: forward-backward JSD."""
    fwd = np.zeros((N_CLASSES, N_CLASSES))
    rev = np.zeros((N_CLASSES, N_CLASSES))
    for line in corpus:
        seq = [t['cls'] for t in line]
        for i in range(len(seq) - 1):
            fwd[seq[i] - 1, seq[i + 1] - 1] += 1
        for i in range(len(seq) - 1, 0, -1):
            rev[seq[i] - 1, seq[i - 1] - 1] += 1
    fwd_f = fwd.flatten() + 1e-12
    rev_f = rev.flatten() + 1e-12
    fwd_f /= fwd_f.sum()
    rev_f /= rev_f.sum()
    m = 0.5 * (fwd_f + rev_f)
    return float(0.5 * scipy_entropy(fwd_f, m, base=2) +
                0.5 * scipy_entropy(rev_f, m, base=2))


def compute_b1(corpus):
    """B1: spectral gap of 6-state transition matrix."""
    st = np.zeros((6, 6))
    for line in corpus:
        for i in range(len(line) - 1):
            s1 = STATE_IDX.get(CLASS_TO_STATE.get(line[i]['cls']))
            s2 = STATE_IDX.get(CLASS_TO_STATE.get(line[i + 1]['cls']))
            if s1 is not None and s2 is not None:
                st[s1, s2] += 1
    st_norm = normalize_rows(st)
    eigenvalues = np.sort(np.abs(np.linalg.eigvals(st_norm)))[::-1]
    return float(1.0 - eigenvalues[1]) if len(eigenvalues) > 1 else 1.0


def compute_b3(corpus):
    """B3: forbidden MIDDLE pair violations."""
    violations = 0
    for line in corpus:
        for i in range(len(line) - 1):
            w1 = line[i]['word']
            w2 = line[i + 1]['word']
            m1 = morph.extract(w1)
            m2m = morph.extract(w2)
            mid1 = m1.middle if m1 else w1
            mid2 = m2m.middle if m2m else w2
            if (mid1, mid2) in forbidden_middle_pairs:
                violations += 1
    return violations


# ── T2: Evaluate All Models ──────────────────────────────────
print("\n" + "=" * 70)
print("T2: MODEL EVALUATION (20 instantiations each)")
print("=" * 70)

real_b5 = compute_b5(lines)
real_b1 = compute_b1(lines)
real_b3 = compute_b3(lines)
print(f"\nReal: B5={real_b5:.4f}, B1={real_b1:.4f}, B3={real_b3}")

b5_tol = 0.50  # within 50%
b1_tol = 0.05  # within 0.05

models = {
    'M2': m2_norm,
    'M5-SF': m5sf_norm,
    'M2.5': m25_norm,
}

results_all = {}
rng = np.random.default_rng(42)

for name, trans in models.items():
    b5s, b1s, b3s = [], [], []
    for inst in range(N_INST):
        corpus = generate(trans, rng)
        b5s.append(compute_b5(corpus))
        b1s.append(compute_b1(corpus))
        b3s.append(compute_b3(corpus))

    b5_pass = sum(abs(v - real_b5) / max(real_b5, 1e-6) < b5_tol for v in b5s) / N_INST
    b1_pass = sum(abs(v - real_b1) < b1_tol for v in b1s) / N_INST
    b3_pass = sum(v == 0 for v in b3s) / N_INST

    results_all[name] = {
        'b5_mean': float(np.mean(b5s)),
        'b5_std': float(np.std(b5s)),
        'b5_pass': b5_pass,
        'b1_mean': float(np.mean(b1s)),
        'b1_std': float(np.std(b1s)),
        'b1_pass': b1_pass,
        'b3_mean': float(np.mean(b3s)),
        'b3_pass': b3_pass,
    }

    print(f"\n{name}:")
    print(f"  B5: {np.mean(b5s):.4f} +/- {np.std(b5s):.4f}  pass={b5_pass:.0%}")
    print(f"  B1: {np.mean(b1s):.4f} +/- {np.std(b1s):.4f}  pass={b1_pass:.0%}")
    print(f"  B3: {np.mean(b3s):.1f} +/- {np.std(b3s):.1f}  pass_0={b3_pass:.0%}")


# ── T3: Comparison Table ──────────────────────────────────────
print("\n" + "=" * 70)
print("T3: COMPARISON TABLE")
print("=" * 70)

print(f"\n{'Model':12s} {'B5':>8s} {'B5 pass':>8s} {'B1':>8s} {'B1 pass':>8s} {'B3':>6s} {'B3=0':>6s}")
print("-" * 60)
print(f"{'Real':12s} {real_b5:8.4f} {'--':>8s} {real_b1:8.4f} {'--':>8s} {real_b3:6d} {'--':>6s}")
for name, r in results_all.items():
    print(f"{name:12s} {r['b5_mean']:8.4f} {r['b5_pass']:8.0%} "
          f"{r['b1_mean']:8.4f} {r['b1_pass']:8.0%} "
          f"{r['b3_mean']:6.1f} {r['b3_pass']:6.0%}")


# ── T4: Why M5-SF May or May Not Work ────────────────────────
print("\n" + "=" * 70)
print("T4: MECHANISM ANALYSIS")
print("=" * 70)

# Check: how much of the JSD asymmetry comes from forbidden cells?
# Compare JSD with and without forbidden cells
fwd = np.zeros((N_CLASSES, N_CLASSES))
rev = np.zeros((N_CLASSES, N_CLASSES))
for line in lines:
    seq = [t['cls'] for t in line]
    for i in range(len(seq) - 1):
        fwd[seq[i] - 1, seq[i + 1] - 1] += 1
    for i in range(len(seq) - 1, 0, -1):
        rev[seq[i] - 1, seq[i - 1] - 1] += 1

# How asymmetric are the forbidden cells in M2?
print("\nForbidden cell asymmetry in generated data:")
for src, tgt in sorted(m2_forbidden_cls):
    fwd_val = fwd[src - 1, tgt - 1]
    rev_val = fwd[tgt - 1, src - 1]
    print(f"  ({src:2d},{tgt:2d}): fwd={fwd_val:5.0f}  rev={rev_val:5.0f}  "
          f"ratio={fwd_val/max(rev_val,1):.2f}")

# JSD contribution from forbidden cells
mask = np.zeros((N_CLASSES, N_CLASSES), dtype=bool)
for src, tgt in m2_forbidden_cls:
    mask[src - 1, tgt - 1] = True

print(f"\nForbidden cell count in transition matrix: {mask.sum()}")
total_transitions = fwd.sum()
forbidden_transitions = fwd[mask].sum()
print(f"Transitions in forbidden cells: {forbidden_transitions:.0f}/{total_transitions:.0f} "
      f"({forbidden_transitions/total_transitions:.4%})")


# ── T5: Second-Order Model ────────────────────────────────────
print("\n" + "=" * 70)
print("T5: SECOND-ORDER CLASS CHAIN (M5-2)")
print("=" * 70)
print("Testing whether higher-order context reduces asymmetry...")

# Build second-order transition: P(class_next | class_current, class_prev)
# State = (prev, current), predict next
# This is a (49*49) x 49 matrix but very sparse
bigram_trans = defaultdict(Counter)
for line in lines:
    for i in range(2, len(line)):
        prev = line[i - 2]['cls']
        cur = line[i - 1]['cls']
        nxt = line[i]['cls']
        bigram_trans[(prev, cur)][nxt] += 1

# Build normalized transition for generation
bigram_probs = {}
for state, counts in bigram_trans.items():
    total = sum(counts.values())
    if total > 0:
        classes = list(counts.keys())
        probs_vals = np.array([counts[c] for c in classes], dtype=float) / total
        bigram_probs[state] = (classes, probs_vals)

# Also suppress forbidden pairs in second-order model
for state, (classes, probs_vals) in list(bigram_probs.items()):
    prev, cur = state
    new_probs = probs_vals.copy()
    for idx, cls in enumerate(classes):
        if (cur, cls) in m2_forbidden_cls:
            new_probs[idx] = 0
    if new_probs.sum() > 0:
        bigram_probs[state] = (classes, new_probs / new_probs.sum())


def generate_m5_2(rng):
    """M5-2: Second-order class chain with forbidden suppression."""
    corpus = []
    for _ in range(n_lines):
        length = rng.choice(line_lengths)
        line = []
        # First two tokens
        cls = rng.choice(N_CLASSES, p=opener_probs) + 1
        if cls in class_token_probs:
            toks, probs = class_token_probs[cls]
            word = rng.choice(toks, p=probs)
        else:
            word = f'UNK_C{cls}'
        line.append({'word': word, 'cls': cls})

        if length > 1:
            row = m2_norm[cls - 1]
            if row.sum() > 0:
                cls2 = rng.choice(N_CLASSES, p=row) + 1
            else:
                cls2 = rng.choice(N_CLASSES, p=opener_probs) + 1
            if cls2 in class_token_probs:
                toks, probs = class_token_probs[cls2]
                word = rng.choice(toks, p=probs)
            else:
                word = f'UNK_C{cls2}'
            line.append({'word': word, 'cls': cls2})

            prev_cls = cls
            cur_cls = cls2

            for pos in range(2, length):
                state = (prev_cls, cur_cls)
                if state in bigram_probs:
                    classes, probs_vals = bigram_probs[state]
                    nxt = rng.choice(classes, p=probs_vals)
                else:
                    # Fallback to first-order
                    row = m2_norm[cur_cls - 1]
                    if row.sum() > 0:
                        nxt = rng.choice(N_CLASSES, p=row) + 1
                    else:
                        nxt = rng.choice(N_CLASSES, p=opener_probs) + 1

                if nxt in class_token_probs:
                    toks, probs = class_token_probs[nxt]
                    word = rng.choice(toks, p=probs)
                else:
                    word = f'UNK_C{nxt}'
                line.append({'word': word, 'cls': nxt})
                prev_cls = cur_cls
                cur_cls = nxt

        corpus.append(line)
    return corpus


rng2 = np.random.default_rng(42)
m52_b5s, m52_b1s, m52_b3s = [], [], []
for inst in range(N_INST):
    corpus = generate_m5_2(rng2)
    m52_b5s.append(compute_b5(corpus))
    m52_b1s.append(compute_b1(corpus))
    m52_b3s.append(compute_b3(corpus))

m52_b5_pass = sum(abs(v - real_b5) / max(real_b5, 1e-6) < b5_tol for v in m52_b5s) / N_INST
m52_b1_pass = sum(abs(v - real_b1) < b1_tol for v in m52_b1s) / N_INST

print(f"\nM5-2 (second-order + forbidden):")
print(f"  B5: {np.mean(m52_b5s):.4f} +/- {np.std(m52_b5s):.4f}  pass={m52_b5_pass:.0%}")
print(f"  B1: {np.mean(m52_b1s):.4f} +/- {np.std(m52_b1s):.4f}  pass={m52_b1_pass:.0%}")
print(f"  B3: {np.mean(m52_b3s):.1f} +/- {np.std(m52_b3s):.1f}")

results_all['M5-2'] = {
    'b5_mean': float(np.mean(m52_b5s)),
    'b5_std': float(np.std(m52_b5s)),
    'b5_pass': m52_b5_pass,
    'b1_mean': float(np.mean(m52_b1s)),
    'b1_std': float(np.std(m52_b1s)),
    'b1_pass': m52_b1_pass,
    'b3_mean': float(np.mean(m52_b3s)),
}


# ── Verdict ───────────────────────────────────────────────────
print("\n" + "=" * 70)
print("FINAL COMPARISON")
print("=" * 70)

print(f"\n{'Model':12s} {'B5':>8s} {'B5 pass':>8s} {'B1':>8s} {'B1 pass':>8s} {'B3':>6s}")
print("-" * 55)
print(f"{'Real':12s} {real_b5:8.4f} {'--':>8s} {real_b1:8.4f} {'--':>8s} {real_b3:6d}")
for name in ['M2', 'M5-SF', 'M2.5', 'M5-2']:
    r = results_all[name]
    print(f"{name:12s} {r['b5_mean']:8.4f} {r['b5_pass']:8.0%} "
          f"{r['b1_mean']:8.4f} {r['b1_pass']:8.0%} "
          f"{r['b3_mean']:6.1f}")

# Find best model
best = None
best_name = None
for name, r in results_all.items():
    if r['b5_pass'] > 0 and r['b1_pass'] > 0:
        if best is None or r['b5_pass'] > best['b5_pass']:
            best = r
            best_name = name

if best_name:
    verdict = f"BEST_MODEL_{best_name.replace('-','_')}"
    explanation = (f"{best_name} achieves B5 pass={best['b5_pass']:.0%}, "
                   f"B1 pass={best['b1_pass']:.0%}. "
                   f"B5={best['b5_mean']:.4f} vs real {real_b5:.4f}.")
else:
    # Check which model has best B5
    best_b5_name = max(results_all, key=lambda k: results_all[k]['b5_pass'])
    best_b5 = results_all[best_b5_name]
    verdict = "NO_FULL_FIX"
    explanation = (f"No model fully fixes B5 while preserving B1. "
                   f"Best B5: {best_b5_name} ({best_b5['b5_mean']:.4f}, pass={best_b5['b5_pass']:.0%}). "
                   f"The B5 asymmetry requires mechanisms beyond simple matrix modifications.")

print(f"\nVerdict: {verdict}")
print(f"\n{explanation}")

# ── Save ──────────────────────────────────────────────────────
out = {
    'real': {'b5': real_b5, 'b1': real_b1, 'b3': real_b3},
    'forbidden_analysis': {
        'total_class_pairs': len(m2_forbidden_cls),
        'symmetric': symmetric_pairs,
        'asymmetric': len(asymmetric_pairs),
        'm2_cells_zeroed': m2_zeros,
        'm5sf_cells_zeroed': m5sf_zeros,
    },
    'models': results_all,
    'verdict': verdict,
    'explanation': explanation,
}

out_dir = PROJECT / 'phases' / 'PREFIX_FACTORED_DESIGN' / 'results'
with open(out_dir / 'symmetric_forbidden.json', 'w') as f:
    json.dump(out, f, indent=2)

print(f"\nSaved to {out_dir / 'symmetric_forbidden.json'}")
