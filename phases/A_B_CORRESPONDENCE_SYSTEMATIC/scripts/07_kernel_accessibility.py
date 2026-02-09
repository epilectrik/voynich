"""
07_kernel_accessibility.py

Test kernel character accessibility matching between A and B.

From C503.c: Kernel access varies by A record (h=95.6%, k=81.1%, e=60.8% mean).

Hypothesis: A paragraphs with e-depleted profiles should match B paragraphs
with FL-heavy execution (since FL has 0% kernel content).
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("KERNEL ACCESSIBILITY MATCHING")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    return word and word[0] in GALLOWS

def build_paragraphs(tokens_iter):
    by_folio_line = defaultdict(list)
    for t in tokens_iter:
        if t.word and '*' not in t.word:
            by_folio_line[(t.folio, t.line)].append(t)

    paragraphs = []
    current_para = {'tokens': [], 'folio': None}
    current_folio = None

    for (folio, line) in sorted(by_folio_line.keys()):
        tokens = by_folio_line[(folio, line)]
        if tokens and (starts_with_gallows(tokens[0].word) or folio != current_folio):
            if current_para['tokens']:
                paragraphs.append(current_para)
            current_para = {'tokens': [], 'folio': folio}
            current_folio = folio
        current_para['tokens'].extend(tokens)

    if current_para['tokens']:
        paragraphs.append(current_para)

    return paragraphs

def compute_kernel_profile(tokens):
    """Compute kernel character rates for token list."""
    k_count = 0
    h_count = 0
    e_count = 0
    n_middles = 0

    for t in tokens:
        word = t.word if hasattr(t, 'word') else t['word']
        try:
            m = morph.extract(word)
            if m.middle:
                n_middles += 1
                if 'k' in m.middle:
                    k_count += 1
                if 'h' in m.middle:
                    h_count += 1
                if 'e' in m.middle:
                    e_count += 1
        except:
            pass

    return {
        'k_rate': k_count / n_middles if n_middles > 0 else 0,
        'h_rate': h_count / n_middles if n_middles > 0 else 0,
        'e_rate': e_count / n_middles if n_middles > 0 else 0,
        'total_kernel': (k_count + h_count + e_count) / n_middles if n_middles > 0 else 0,
        'n_middles': n_middles
    }

# =============================================================
# BUILD PARAGRAPHS
# =============================================================
print("\nBuilding paragraphs...")

a_paras = build_paragraphs(tx.currier_a())
b_paras = build_paragraphs(tx.currier_b())

print(f"A paragraphs: {len(a_paras)}")
print(f"B paragraphs: {len(b_paras)}")

# =============================================================
# COMPUTE KERNEL PROFILES
# =============================================================
print("\n" + "="*70)
print("COMPUTING KERNEL PROFILES")
print("="*70)

a_kernels = []
for i, para in enumerate(a_paras):
    profile = compute_kernel_profile(para['tokens'])
    profile['idx'] = i
    profile['folio'] = para['folio']
    a_kernels.append(profile)

b_kernels = []
for i, para in enumerate(b_paras):
    profile = compute_kernel_profile(para['tokens'])
    profile['idx'] = i
    profile['folio'] = para['folio']
    b_kernels.append(profile)

# Filter to paragraphs with enough data
a_kernels = [k for k in a_kernels if k['n_middles'] >= 5]
b_kernels = [k for k in b_kernels if k['n_middles'] >= 5]

print(f"A paragraphs with >=5 MIDDLEs: {len(a_kernels)}")
print(f"B paragraphs with >=5 MIDDLEs: {len(b_kernels)}")

# Summary
print(f"\nKernel rates:")
print(f"        k        h        e        total")
print(f"A:    {sum(k['k_rate'] for k in a_kernels)/len(a_kernels):.3f}    {sum(k['h_rate'] for k in a_kernels)/len(a_kernels):.3f}    {sum(k['e_rate'] for k in a_kernels)/len(a_kernels):.3f}    {sum(k['total_kernel'] for k in a_kernels)/len(a_kernels):.3f}")
print(f"B:    {sum(k['k_rate'] for k in b_kernels)/len(b_kernels):.3f}    {sum(k['h_rate'] for k in b_kernels)/len(b_kernels):.3f}    {sum(k['e_rate'] for k in b_kernels)/len(b_kernels):.3f}    {sum(k['total_kernel'] for k in b_kernels)/len(b_kernels):.3f}")

# =============================================================
# KERNEL PROFILE MATCHING
# =============================================================
print("\n" + "="*70)
print("KERNEL PROFILE MATCHING")
print("="*70)

def kernel_distance(a, b):
    """Euclidean distance in kernel space."""
    dk = (a['k_rate'] - b['k_rate']) ** 2
    dh = (a['h_rate'] - b['h_rate']) ** 2
    de = (a['e_rate'] - b['e_rate']) ** 2
    return (dk + dh + de) ** 0.5

# For each A, find best kernel-matching B
results = []
for a in a_kernels:
    best_b = None
    best_dist = float('inf')

    for b in b_kernels:
        dist = kernel_distance(a, b)
        if dist < best_dist:
            best_dist = dist
            best_b = b

    results.append({
        'a_idx': a['idx'],
        'a_folio': a['folio'],
        'a_k': a['k_rate'],
        'a_h': a['h_rate'],
        'a_e': a['e_rate'],
        'best_b_idx': best_b['idx'] if best_b else -1,
        'best_b_folio': best_b['folio'] if best_b else None,
        'b_k': best_b['k_rate'] if best_b else 0,
        'b_h': best_b['h_rate'] if best_b else 0,
        'b_e': best_b['e_rate'] if best_b else 0,
        'distance': best_dist
    })

distances = [r['distance'] for r in results]
print(f"\nKernel distance (0 = perfect match):")
print(f"  Mean: {sum(distances)/len(distances):.3f}")
print(f"  Min: {min(distances):.3f}")
print(f"  Max: {max(distances):.3f}")
print(f"  Close matches (<0.1): {sum(1 for d in distances if d < 0.1)}")
print(f"  Close matches (<0.05): {sum(1 for d in distances if d < 0.05)}")

# =============================================================
# CORRELATION ANALYSIS
# =============================================================
print("\n" + "="*70)
print("CORRELATION: A kernel -> matched B kernel")
print("="*70)

def correlation(x, y):
    n = len(x)
    if n == 0:
        return 0
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den_x = sum((xi - mx)**2 for xi in x) ** 0.5
    den_y = sum((yi - my)**2 for yi in y) ** 0.5
    return num / (den_x * den_y) if den_x * den_y > 0 else 0

a_ks = [r['a_k'] for r in results]
b_ks = [r['b_k'] for r in results]
a_hs = [r['a_h'] for r in results]
b_hs = [r['b_h'] for r in results]
a_es = [r['a_e'] for r in results]
b_es = [r['b_e'] for r in results]

print(f"\nCorrelation by kernel character:")
print(f"  k: {correlation(a_ks, b_ks):.3f}")
print(f"  h: {correlation(a_hs, b_hs):.3f}")
print(f"  e: {correlation(a_es, b_es):.3f}")

# =============================================================
# E-DEPLETED ANALYSIS
# =============================================================
print("\n" + "="*70)
print("E-DEPLETED ANALYSIS")
print("="*70)

# Find A paragraphs with low e (bottom quartile)
e_rates = [k['e_rate'] for k in a_kernels]
e_threshold = sorted(e_rates)[len(e_rates)//4]

e_depleted = [k for k in a_kernels if k['e_rate'] <= e_threshold]
e_rich = [k for k in a_kernels if k['e_rate'] > sorted(e_rates)[3*len(e_rates)//4]]

print(f"E-depleted A paragraphs (e <= {e_threshold:.3f}): {len(e_depleted)}")
print(f"E-rich A paragraphs: {len(e_rich)}")

# What's the mean matched B kernel profile for each group?
e_depleted_matched = [r for r in results if r['a_idx'] in [k['idx'] for k in e_depleted]]
e_rich_matched = [r for r in results if r['a_idx'] in [k['idx'] for k in e_rich]]

if e_depleted_matched:
    print(f"\nE-depleted A -> matched B kernel:")
    print(f"  k: {sum(r['b_k'] for r in e_depleted_matched)/len(e_depleted_matched):.3f}")
    print(f"  h: {sum(r['b_h'] for r in e_depleted_matched)/len(e_depleted_matched):.3f}")
    print(f"  e: {sum(r['b_e'] for r in e_depleted_matched)/len(e_depleted_matched):.3f}")

if e_rich_matched:
    print(f"\nE-rich A -> matched B kernel:")
    print(f"  k: {sum(r['b_k'] for r in e_rich_matched)/len(e_rich_matched):.3f}")
    print(f"  h: {sum(r['b_h'] for r in e_rich_matched)/len(e_rich_matched):.3f}")
    print(f"  e: {sum(r['b_e'] for r in e_rich_matched)/len(e_rich_matched):.3f}")

# =============================================================
# SAVE RESULTS
# =============================================================
out_path = Path(__file__).parent.parent / 'results' / 'kernel_accessibility.json'
with open(out_path, 'w') as f:
    json.dump({
        'n_a_paras': len(a_kernels),
        'n_b_paras': len(b_kernels),
        'mean_distance': sum(distances)/len(distances),
        'correlation_k': correlation(a_ks, b_ks),
        'correlation_h': correlation(a_hs, b_hs),
        'correlation_e': correlation(a_es, b_es),
        'close_matches_01': sum(1 for d in distances if d < 0.1),
    }, f, indent=2)

print(f"\nSaved to {out_path.name}")
