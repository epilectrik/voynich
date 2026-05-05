"""Scatter v3 — three crazy-expert top picks:
  Probe A: Negative-space atom pairs (atom-bigram cells with depleted co-occurrence)
  Probe B: Twin tokens (mutual nearest-neighbor pairs)
  Probe C: Folio-internal e-depth tempo (autocorrelation signature)
"""
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Build per-folio, per-line ordered token lists (Currier B, text only, no labels, no asterisks)
folio_lines = defaultdict(lambda: defaultdict(list))
folio_paras = defaultdict(lambda: defaultdict(list))  # folio -> paragraph -> [(line, token)]
all_tokens = []

for t in tx.currier_b():
    if not t.placement.startswith('P'):
        continue
    if not t.word or '*' in t.word:
        continue
    folio_lines[t.folio][t.line].append(t.word)
    all_tokens.append(t.word)

folios = sorted(folio_lines.keys())
print(f"Loaded {len(all_tokens)} tokens, {len(folios)} folios.\n")


# ============================================================
# PROBE A: Negative-space atom pairs (forbidden atom co-occurrence cells)
# ============================================================
print("="*70)
print("PROBE A: Negative-space atom pairs (forbidden atom-bigram cells)")
print("="*70)

# Approach: for every token, atomize the MIDDLE. Build atom-PAIR counts:
#   for each ordered adjacent pair (a_i, a_{i+1}) within MIDDLE atoms.
# Compute expected = freq(a) * freq(b) * (total pairs / total atoms^2)
# Find cells with actual / expected < threshold.

atom_pair_counts = Counter()  # (a, b) -> count
atom_counts = Counter()
n_pairs = 0
n_atoms = 0

for word in all_tokens:
    a = morph.atomize(word)
    if not a.atoms or len(a.atoms) < 2:
        # still count single atoms for marginal
        for atom_tuple in a.atoms:
            atom_counts[atom_tuple[0]] += 1
            n_atoms += 1
        continue
    atom_seq = [at[0] for at in a.atoms]
    for atom in atom_seq:
        atom_counts[atom] += 1
        n_atoms += 1
    for i in range(len(atom_seq) - 1):
        atom_pair_counts[(atom_seq[i], atom_seq[i+1])] += 1
        n_pairs += 1

print(f"  Total atoms (in MIDDLEs): {n_atoms}")
print(f"  Total atom-pairs (adjacent within MIDDLE): {n_pairs}")
print(f"  Distinct atoms: {len(atom_counts)}")
print(f"  Distinct atom-pairs: {len(atom_pair_counts)}")
print(f"  All-pairs cells (n_atoms x n_atoms): {len(atom_counts)**2}")

# Compute expected for each cell
atom_freq = {a: c / n_atoms for a, c in atom_counts.items()}

# Find depleted and absent cells (high-frequency atoms whose pair never appears)
print(f"\n  Marginal atom counts (top):")
for a, c in atom_counts.most_common():
    print(f"    '{a}': {c}")

# All ordered pairs among atoms with >= 100 occurrences
common_atoms = [a for a, c in atom_counts.items() if c >= 100]
print(f"\n  Atoms with >=100 occurrences: {common_atoms}")

# Build matrix
print(f"\n  Atom-pair (actual / expected) ratios for common-atom cells:")
print(f"  {'a':>3} -> {'b':>3}  {'actual':>8}  {'expected':>10}  {'ratio':>8}")
results = []
for a in common_atoms:
    for b in common_atoms:
        actual = atom_pair_counts.get((a, b), 0)
        expected = atom_freq[a] * atom_freq[b] * n_pairs
        if expected > 0:
            ratio = actual / expected
            results.append((a, b, actual, expected, ratio))
results.sort(key=lambda x: x[4])
print("\n  TOP 20 DEPLETED CELLS (lowest actual/expected):")
for a, b, act, exp, ratio in results[:20]:
    print(f"    {a:>3} -> {b:>3}  {act:>8d}  {exp:>10.1f}  {ratio:>8.3f}")
print("\n  TOP 10 ENRICHED CELLS (highest actual/expected):")
for a, b, act, exp, ratio in sorted(results, key=lambda x: -x[4])[:10]:
    print(f"    {a:>3} -> {b:>3}  {act:>8d}  {exp:>10.1f}  {ratio:>8.3f}")

# Statistical test for forbidden cells: Poisson (or chi-square)
# Null: actual ~ Poisson(expected). p-value = P(X <= actual) where X ~ Poisson(expected).
from scipy.stats import poisson
print("\n  Bonferroni-significant DEPLETIONS (cells where p < 0.05/n_cells):")
n_cells_tested = len(common_atoms) ** 2
threshold = 0.05 / n_cells_tested
sig_dep = []
for a, b, act, exp, ratio in results:
    if exp >= 5:  # need expected >= 5 for power
        p = poisson.cdf(act, exp)
        if p < threshold:
            sig_dep.append((a, b, act, exp, ratio, p))
sig_dep.sort(key=lambda x: x[5])
for a, b, act, exp, ratio, p in sig_dep[:20]:
    print(f"    {a:>3} -> {b:>3}  actual={act}  expected={exp:.1f}  ratio={ratio:.3f}  p={p:.2e}")
print(f"  Total significantly depleted at p<{threshold:.2e}: {len(sig_dep)}")


# ============================================================
# PROBE B: Twin tokens (mutual nearest-neighbor pairs)
# ============================================================
print()
print("="*70)
print("PROBE B: Twin tokens (mutual NN within line, freq>=20)")
print("="*70)

# For each token type T with freq>=20:
#   Find its highest-cooccurring partner within same-line window=any
#   Mutual pair: T's #1 = U AND U's #1 = T
# Co-occurrence count = number of lines where both T and U appear at least once.

token_freq = Counter(all_tokens)
common_tokens = [t for t, c in token_freq.items() if c >= 30]
print(f"  Tokens with freq>=30: {len(common_tokens)}")

# Co-occurrence (line-level): count lines where T and U both present
line_sets = []  # list of sets of tokens per line
for f, ld in folio_lines.items():
    for lid, lt in ld.items():
        if len(lt) >= 2:
            line_sets.append(set(lt))

# For each pair of common tokens, count co-occurring lines
from itertools import combinations
co_count = defaultdict(int)
for s in line_sets:
    common_in_line = s & set(common_tokens)
    for a, b in combinations(common_in_line, 2):
        if a < b:
            co_count[(a, b)] += 1
        else:
            co_count[(b, a)] += 1

# For each token, find its top co-occurring partner
top_partner = {}
for t in common_tokens:
    best = None
    best_n = 0
    for u in common_tokens:
        if u == t:
            continue
        key = (t, u) if t < u else (u, t)
        n = co_count.get(key, 0)
        if n > best_n:
            best_n = n
            best = u
    top_partner[t] = (best, best_n)

# Find mutual #1 pairs
mutual_pairs = set()
for t, (u, n) in top_partner.items():
    if u and top_partner.get(u, (None, 0))[0] == t:
        pair = tuple(sorted([t, u]))
        mutual_pairs.add((pair, n))

print(f"  Mutual NN pairs found: {len(mutual_pairs)}")
print(f"\n  Top 25 mutual pairs by co-occurrence count:")
for pair, n in sorted(mutual_pairs, key=lambda x: -x[1])[:25]:
    fa = token_freq[pair[0]]
    fb = token_freq[pair[1]]
    # PMI-like
    n_lines = len(line_sets)
    expected = (fa / len(all_tokens)) * (fb / len(all_tokens)) * n_lines * 5  # rough approx
    print(f"    ({pair[0]:10s}, {pair[1]:10s})  co={n:4d}  freq_a={fa:4d}  freq_b={fb:4d}")

# How many of the mutual pairs survive frequency-control?
# Permutation null: shuffle token positions across all lines preserving line lengths
print()
print("  FREQUENCY-CONTROLLED NULL (shuffle tokens across all lines, preserve line lens):")
rng = np.random.default_rng(42)

def get_mutual_pairs_from_line_sets(line_sets_list):
    co = defaultdict(int)
    for s in line_sets_list:
        c_in_line = s & set(common_tokens)
        for a, b in combinations(c_in_line, 2):
            key = (a, b) if a < b else (b, a)
            co[key] += 1
    tp = {}
    for t in common_tokens:
        best = None; bn = 0
        for u in common_tokens:
            if u == t: continue
            key = (t, u) if t < u else (u, t)
            nn = co.get(key, 0)
            if nn > bn:
                bn = nn; best = u
        tp[t] = (best, bn)
    mp = set()
    for t, (u, n) in tp.items():
        if u and tp.get(u, (None, 0))[0] == t:
            mp.add(tuple(sorted([t, u])))
    return mp

actual_mp = set([p for p, _ in mutual_pairs])
# Run 200 trials
null_counts = []
for trial in range(200):
    pool = list(all_tokens)
    rng.shuffle(pool)
    new_lines = []
    idx = 0
    for f, ld in folio_lines.items():
        for lid, lt in ld.items():
            L = len(lt)
            new_lines.append(set(pool[idx:idx+L]))
            idx += L
    null_mp = get_mutual_pairs_from_line_sets(new_lines)
    null_counts.append(len(null_mp))
print(f"    Actual mutual pairs: {len(actual_mp)}")
print(f"    Null mean: {np.mean(null_counts):.1f}, std: {np.std(null_counts):.1f}")
print(f"    z-score: {(len(actual_mp) - np.mean(null_counts)) / np.std(null_counts):.2f}")
print(f"    p(null >= actual): {sum(1 for n in null_counts if n >= len(actual_mp)) / len(null_counts):.4f}")


# ============================================================
# PROBE C: Folio-internal e-depth tempo (autocorrelation)
# ============================================================
print()
print("="*70)
print("PROBE C: Folio-internal e-depth tempo (lag-1 autocorrelation)")
print("="*70)

# For each folio, build e-depth sequence (in line-then-token order).
# Compute lag-1 autocorr: corr(e_t, e_{t+1}).
# Compare actual to within-folio shuffle null.

results = []
for f in folios:
    line_ids = sorted(folio_lines[f].keys(), key=lambda x: (len(x), x))
    e_seq = []
    for lid in line_ids:
        for tok in folio_lines[f][lid]:
            a = morph.atomize(tok)
            e_seq.append(a.e_depth)
    if len(e_seq) < 60:
        continue
    e_arr = np.array(e_seq)
    lag1 = np.corrcoef(e_arr[:-1], e_arr[1:])[0, 1]
    # Null: shuffle within folio
    rng_f = np.random.default_rng(hash(f) % 2**31)
    null_lags = []
    for _ in range(500):
        shuf = e_arr.copy()
        rng_f.shuffle(shuf)
        null_lags.append(np.corrcoef(shuf[:-1], shuf[1:])[0, 1])
    null_mean = np.mean(null_lags)
    null_std = np.std(null_lags)
    z = (lag1 - null_mean) / null_std if null_std > 0 else 0
    results.append((f, lag1, z, len(e_seq)))

print(f"  Folios with n_tokens>=60: {len(results)}")

# Distribution of z-scores
zs = [r[2] for r in results]
lag1s = [r[1] for r in results]
print(f"  Mean lag-1 autocorr: {np.mean(lag1s):.4f}")
print(f"  Std: {np.std(lag1s):.4f}")
print(f"  Mean z (vs within-folio shuffle): {np.mean(zs):.2f}")
print(f"  Std z: {np.std(zs):.2f}")

print(f"\n  Top 10 folios by z-score (most autocorrelated e-depth — programmed tempo):")
results.sort(key=lambda x: -x[2])
for f, lag1, z, n in results[:10]:
    print(f"    {f:8s}  lag1={lag1:+.3f}  z={z:+.2f}  n={n}")

print(f"\n  Bottom 10 (most anti-correlated):")
for f, lag1, z, n in sorted(results, key=lambda x: x[2])[:10]:
    print(f"    {f:8s}  lag1={lag1:+.3f}  z={z:+.2f}  n={n}")

# Pre-registered hypothesis test: how many folios have |z| > 2?
n_sig = sum(1 for r in results if abs(r[2]) > 2)
n_pos = sum(1 for r in results if r[2] > 2)
n_neg = sum(1 for r in results if r[2] < -2)
print(f"\n  Folios with |z|>2: {n_sig}/{len(results)} (expected by chance ~{0.05*len(results):.1f})")
print(f"    Positive (clustered): {n_pos}")
print(f"    Negative (alternating): {n_neg}")

print()
print("="*70)
print("SCATTER v3 COMPLETE")
print("="*70)
