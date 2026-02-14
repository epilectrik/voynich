"""
Comprehensive M5 Design Analysis

Tests all candidate B5 fixes using BOTH forbidden mapping strategies:
1. Token-direct: map forbidden token pairs to class pairs (10 pairs, light)
2. C1025-MIDDLE: expand through MIDDLE extraction (heavier, matches C1025)

Models tested:
- M2: Class Markov + asymmetric forbidden suppression
- M5-SF: Symmetric forbidden suppression (bidirectional)
- M2.5: 15% detailed-balance blending
- M5-PFX: PREFIX-factored (through conditional routing)

For each model and forbidden strategy, evaluate B5, B1, B3.
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

class_to_tokens_list = defaultdict(list)
for tok, cls in token_to_class.items():
    class_to_tokens_list[cls].append(tok)

with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
          encoding='utf-8') as f:
    forbidden_inv = json.load(f)
forbidden_pairs_raw = [(t['source'], t['target']) for t in forbidden_inv['transitions']]
forbidden_middle_pairs = set(forbidden_pairs_raw)

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

# Empirical matrices
class_trans = np.zeros((N_CLASSES, N_CLASSES))
for line in lines:
    for i in range(len(line) - 1):
        class_trans[line[i]['cls'] - 1, line[i + 1]['cls'] - 1] += 1

opener_counts = Counter(line[0]['cls'] for line in lines if line)
opener_probs = np.zeros(N_CLASSES)
for cls, count in opener_counts.items():
    opener_probs[cls - 1] = count
opener_probs /= max(opener_probs.sum(), 1)

token_freq = Counter(t['word'] for t in all_tokens)
class_token_probs = {}
for cls_id in range(1, N_CLASSES + 1):
    toks = class_to_tokens_list.get(cls_id, [])
    if toks:
        counts = [token_freq.get(t, 0) for t in toks]
        total = sum(counts)
        if total > 0:
            class_token_probs[cls_id] = (toks, np.array(counts, dtype=float) / total)

# ── Two Forbidden Mapping Strategies ──────────────────────────
print("\n" + "=" * 70)
print("FORBIDDEN MAPPING STRATEGIES")
print("=" * 70)

# Strategy 1: Token-direct (simpler, lighter)
token_direct_pairs = set()
for src_tok, tgt_tok in forbidden_pairs_raw:
    src_cls = token_to_class.get(src_tok)
    tgt_cls = token_to_class.get(tgt_tok)
    if src_cls and tgt_cls:
        token_direct_pairs.add((src_cls, tgt_cls))

# Strategy 2: C1025-MIDDLE expansion (matches generative_sufficiency.py)
c1025_pairs = set()
for src_tok, tgt_tok in forbidden_pairs_raw:
    src_m = morph.extract(src_tok)
    tgt_m = morph.extract(tgt_tok)
    src_mid = src_m.middle if src_m else src_tok
    tgt_mid = tgt_m.middle if tgt_m else tgt_tok
    src_classes = set()
    tgt_classes = set()
    for cls_id, tok_list in class_to_tokens_list.items():
        for tok in tok_list:
            m = morph.extract(tok)
            mid = m.middle if m else tok
            if mid == src_mid:
                src_classes.add(cls_id)
            if mid == tgt_mid:
                tgt_classes.add(cls_id)
    for sc in src_classes:
        for tc in tgt_classes:
            c1025_pairs.add((sc, tc))

print(f"\nToken-direct: {len(token_direct_pairs)} class pairs suppressed")
print(f"C1025-MIDDLE: {len(c1025_pairs)} class pairs suppressed")


# ── Build All Model Variants ──────────────────────────────────

def build_models(forbidden_cls_pairs, label):
    """Build M2, M5-SF, M2.5 from a forbidden pair set."""
    # M2: asymmetric suppression
    m2 = class_trans.copy()
    for src, tgt in forbidden_cls_pairs:
        m2[src - 1, tgt - 1] = 0
    m2_n = normalize_rows(m2)

    # M5-SF: symmetric suppression
    sym_pairs = set()
    for src, tgt in forbidden_cls_pairs:
        sym_pairs.add((src, tgt))
        sym_pairs.add((tgt, src))
    m5sf = class_trans.copy()
    for src, tgt in sym_pairs:
        m5sf[src - 1, tgt - 1] = 0
    m5sf_n = normalize_rows(m5sf)

    # M2.5: 15% detailed-balance blending
    stationary = m2.sum(axis=1)
    stationary /= max(stationary.sum(), 1e-12)
    m2_rev = np.zeros_like(m2)
    for i in range(N_CLASSES):
        for j in range(N_CLASSES):
            if stationary[j] > 0:
                m2_rev[i, j] = m2_n[j, i] * stationary[j] / max(stationary[i], 1e-12)
    m2_rev = normalize_rows(m2_rev)
    m25_n = 0.85 * m2_n + 0.15 * m2_rev

    cells_m2 = int((m2 == 0).sum() - (class_trans == 0).sum())
    cells_sf = int((m5sf == 0).sum() - (class_trans == 0).sum())

    print(f"\n{label}:")
    print(f"  M2 cells zeroed: {cells_m2}")
    print(f"  M5-SF cells zeroed: {cells_sf} (+{cells_sf - cells_m2})")
    print(f"  Asymmetric pairs: {len(forbidden_cls_pairs) - sum(1 for s,t in forbidden_cls_pairs if (t,s) in forbidden_cls_pairs)//1}")

    return {'M2': m2_n, 'M5-SF': m5sf_n, 'M2.5': m25_n}


# ── Evaluation Functions ──────────────────────────────────────

def compute_b5(corpus):
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

def generate(trans_norm, rng):
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


# ── Evaluate ──────────────────────────────────────────────────
real_b5 = compute_b5(lines)
real_b1 = compute_b1(lines)
real_b3 = compute_b3(lines)
print(f"\nReal: B5={real_b5:.4f}, B1={real_b1:.4f}, B3={real_b3}")

b5_tol = 0.50
b1_tol = 0.05

results = {}

for strategy_name, forbidden_pairs in [
    ("Token-Direct", token_direct_pairs),
    ("C1025-MIDDLE", c1025_pairs),
]:
    print(f"\n{'=' * 70}")
    print(f"STRATEGY: {strategy_name} ({len(forbidden_pairs)} class pairs)")
    print(f"{'=' * 70}")

    models = build_models(forbidden_pairs, strategy_name)
    strategy_results = {}

    for model_name, trans in models.items():
        rng = np.random.default_rng(42)
        b5s, b1s, b3s = [], [], []
        for inst in range(N_INST):
            corpus = generate(trans, rng)
            b5s.append(compute_b5(corpus))
            b1s.append(compute_b1(corpus))
            b3s.append(compute_b3(corpus))

        b5_pass = sum(abs(v - real_b5) / max(real_b5, 1e-6) < b5_tol for v in b5s) / N_INST
        b1_pass = sum(abs(v - real_b1) < b1_tol for v in b1s) / N_INST
        b3_zero = sum(v == 0 for v in b3s) / N_INST

        strategy_results[model_name] = {
            'b5_mean': float(np.mean(b5s)),
            'b5_std': float(np.std(b5s)),
            'b5_pass': b5_pass,
            'b1_mean': float(np.mean(b1s)),
            'b1_std': float(np.std(b1s)),
            'b1_pass': b1_pass,
            'b3_mean': float(np.mean(b3s)),
            'b3_zero': b3_zero,
        }

        print(f"\n  {model_name}:")
        print(f"    B5: {np.mean(b5s):.4f} +/- {np.std(b5s):.4f}  pass={b5_pass:.0%}")
        print(f"    B1: {np.mean(b1s):.4f} +/- {np.std(b1s):.4f}  pass={b1_pass:.0%}")
        print(f"    B3: {np.mean(b3s):.1f}  zero={b3_zero:.0%}")

    results[strategy_name] = strategy_results

# ── Final Summary ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

print(f"\n{'Strategy':16s} {'Model':8s} {'B5':>8s} {'B5%':>6s} {'B1':>8s} {'B1%':>6s} {'B3':>6s} {'All':>6s}")
print("-" * 70)
print(f"{'Real':16s} {'':8s} {real_b5:8.4f} {'':>6s} {real_b1:8.4f} {'':>6s} {real_b3:6d} {'':>6s}")

for strat, models_r in results.items():
    for model, r in models_r.items():
        all_pass = "YES" if r['b5_pass'] >= 0.8 and r['b1_pass'] >= 0.8 else "no"
        print(f"{strat:16s} {model:8s} {r['b5_mean']:8.4f} {r['b5_pass']:6.0%} "
              f"{r['b1_mean']:8.4f} {r['b1_pass']:6.0%} "
              f"{r['b3_mean']:6.1f} {all_pass:>6s}")

# Determine verdict
# Find the model that passes B5 and B1 with the C1025-MIDDLE mapping (the reference)
c1025_models = results.get("C1025-MIDDLE", {})
best_model = None
for name, r in c1025_models.items():
    if r['b5_pass'] >= 0.8 and r['b1_pass'] >= 0.8:
        if best_model is None or r['b5_pass'] > c1025_models[best_model]['b5_pass']:
            best_model = name

if best_model:
    r = c1025_models[best_model]
    verdict = f"{best_model}_FIXES_B5"
    explanation = (f"Under C1025-MIDDLE forbidden mapping, {best_model} passes both B5 ({r['b5_pass']:.0%}) "
                   f"and B1 ({r['b1_pass']:.0%}). B5={r['b5_mean']:.4f} vs real {real_b5:.4f}.")
else:
    verdict = "NO_SIMPLE_FIX"
    explanation = ("No model under the C1025-MIDDLE forbidden mapping passes both B5 and B1 simultaneously. "
                   "The B5 failure under heavy forbidden suppression requires a fundamentally different approach.")

print(f"\nVerdict: {verdict}")
print(explanation)

# ── Save ──────────────────────────────────────────────────────
out = {
    'real': {'b5': real_b5, 'b1': real_b1, 'b3': real_b3},
    'strategies': {
        'Token-Direct': {
            'n_class_pairs': len(token_direct_pairs),
            'models': results['Token-Direct'],
        },
        'C1025-MIDDLE': {
            'n_class_pairs': len(c1025_pairs),
            'models': results['C1025-MIDDLE'],
        },
    },
    'verdict': verdict,
    'explanation': explanation,
}

out_dir = PROJECT / 'phases' / 'PREFIX_FACTORED_DESIGN' / 'results'
with open(out_dir / 'm5_comprehensive.json', 'w') as f:
    json.dump(out, f, indent=2)

print(f"\nSaved to {out_dir / 'm5_comprehensive.json'}")
