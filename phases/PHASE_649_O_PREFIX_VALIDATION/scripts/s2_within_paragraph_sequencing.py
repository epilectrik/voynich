"""
Phase 649 Step 2: Within-paragraph sequencing test.

Crazy-expert's "lock-in" recommendation. The fire/vessel architecture predicts
a specific transition topology at line/paragraph scale:

PREDICTED ENRICHED:
- qo -> ol  (driver -> vessel-content state change)
- qo -> ok  (driver -> thermal observer)
- qo -> ot  (driver -> transfer observer)
- ol -> ok  (state -> thermal aspect)
- ol -> ot  (state -> transfer aspect)
- ok -> ch  (observation -> event check)
- ot -> ch  (transfer -> event check)
- sh -> qo  (continuous monitor -> driver decision)
- ch -> qo  (event monitor -> driver decision)

PREDICTED SUPPRESSED:
- ch -> ch  (don't event-check twice in a row)
- ch -> sh  (mode switch unusual)
- sh -> sh  (back-to-back continuous monitors)

If the predicted topology shows up in line-bigram counts at significantly
above null-shuffle baseline, the channels are not just statistically present
in folio profiles — they participate in the predicted control loop.

Method:
1. Extract all adjacent prefix-prefix bigrams within lines (Currier B)
2. Count enrichment vs marginal-product null
3. Compare predicted-enriched vs predicted-suppressed observed enrichments
4. Permutation test: shuffle prefix labels within line, recompute, see
   how often null produces same pattern
"""
import sys
import json
import math
import random
sys.path.insert(0, '.')
from scripts.voynich import Transcript
from collections import defaultdict, Counter

tx = Transcript()

# Group tokens by (folio, line)
lines = defaultdict(list)
for t in tx.currier_b():
    lines[(t.folio, t.line)].append(t)

def prefix_of(w):
    if w.startswith('ch'): return 'ch'
    if w.startswith('sh'): return 'sh'
    if w.startswith('qo'): return 'qo'
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k','t','l','r'):
        return 'o' + w[1]
    return None

prefixes = ['ch','sh','qo','ok','ot','ol','or']

# Build a per-line prefix sequence (None for non-targeted prefixes)
line_seqs = []
for key, toks in lines.items():
    seq = [prefix_of(t.word) for t in toks]
    # Keep only positions where there's a target prefix
    seq_filt = [p for p in seq if p is not None]
    if len(seq_filt) >= 2:
        line_seqs.append(seq_filt)

print(f"Lines with >=2 prefix tokens: {len(line_seqs):,}")
total_bigrams = sum(len(s) - 1 for s in line_seqs)
print(f"Total adjacent prefix bigrams: {total_bigrams:,}")

# Count observed bigrams
observed = Counter()
for seq in line_seqs:
    for a, b in zip(seq, seq[:-1] + [None]):  # safer: zip pairs
        pass
# Re-do properly
observed = Counter()
for seq in line_seqs:
    for i in range(len(seq) - 1):
        observed[(seq[i], seq[i+1])] += 1

# Marginal counts for null
marginal = Counter()
for seq in line_seqs:
    for p in seq:
        marginal[p] += 1
total_tokens = sum(marginal.values())

# Expected under marginal-product null (no sequence structure)
expected = {}
for p1 in prefixes:
    for p2 in prefixes:
        # Probability of p1 then p2 if independent of position
        # Number of bigrams where 1st = p1: roughly marginal[p1] / total_tokens * total_bigrams
        # Conditional on 1st = p1, probability 2nd = p2: marginal[p2] / total_tokens
        if marginal[p1] == 0 or marginal[p2] == 0:
            expected[(p1, p2)] = 0
            continue
        p1_starts = marginal[p1]
        # Of those, how many have a successor at all? Approximate via avg line length
        # Simpler: use observed count of bigrams where p1 is first as denom
        bg_starting_p1 = sum(observed[(p1, p2_)] for p2_ in prefixes)
        if bg_starting_p1 == 0:
            expected[(p1, p2)] = 0
            continue
        # Expected fraction = marginal[p2] / total
        expected[(p1, p2)] = bg_starting_p1 * marginal[p2] / total_tokens

# Print enrichment matrix
print()
print("="*72)
print("BIGRAM ENRICHMENT MATRIX (observed / expected)")
print("="*72)
print("Cell = log2(obs/exp). >0 enriched, <0 suppressed.")
print()
print("        " + "  ".join(f"{p:>6s}" for p in prefixes))
enrichment = {}
for p1 in prefixes:
    row = [f"{p1:>4s}  "]
    for p2 in prefixes:
        obs = observed[(p1, p2)]
        exp = expected[(p1, p2)]
        if exp < 0.5 or obs == 0:
            row.append(f"{'  --':>6s}")
            enrichment[(p1, p2)] = None
            continue
        r = math.log2(obs / exp)
        enrichment[(p1, p2)] = r
        row.append(f"{r:>+6.2f}")
    print("  ".join(row))

# Predictions
PREDICTED_ENRICHED = [
    ('qo','ol'), ('qo','ok'), ('qo','ot'),
    ('ol','ok'), ('ol','ot'),
    ('ok','ch'), ('ot','ch'),
    ('sh','qo'), ('ch','qo'),
]
PREDICTED_SUPPRESSED = [
    ('ch','ch'), ('ch','sh'), ('sh','sh'),
]

print()
print("="*72)
print("PREDICTED ENRICHED transitions (should be > 0)")
print("="*72)
hits_enr = 0
for pair in PREDICTED_ENRICHED:
    e = enrichment.get(pair)
    obs = observed.get(pair, 0)
    exp = expected.get(pair, 0)
    if e is None:
        verdict = '  --'
    elif e > 0.2:
        verdict = 'YES (>+0.2)'
        hits_enr += 1
    elif e > 0:
        verdict = 'directional'
    else:
        verdict = 'FAIL (<= 0)'
    e_str = f"{e:+.2f}" if e is not None else '--'
    print(f"  {pair[0]} -> {pair[1]}:  obs={obs:5d}  exp={exp:7.1f}  log2(o/e)={e_str:>6s}   {verdict}")

print(f"\nEnriched hits: {hits_enr}/{len(PREDICTED_ENRICHED)}")

print()
print("="*72)
print("PREDICTED SUPPRESSED transitions (should be < 0)")
print("="*72)
hits_sup = 0
for pair in PREDICTED_SUPPRESSED:
    e = enrichment.get(pair)
    obs = observed.get(pair, 0)
    exp = expected.get(pair, 0)
    if e is None:
        verdict = '  --'
    elif e < -0.2:
        verdict = 'YES (<-0.2)'
        hits_sup += 1
    elif e < 0:
        verdict = 'directional'
    else:
        verdict = 'FAIL (>= 0)'
    e_str = f"{e:+.2f}" if e is not None else '--'
    print(f"  {pair[0]} -> {pair[1]}:  obs={obs:5d}  exp={exp:7.1f}  log2(o/e)={e_str:>6s}   {verdict}")

print(f"\nSuppressed hits: {hits_sup}/{len(PREDICTED_SUPPRESSED)}")

# Permutation null: shuffle prefix labels within line, recompute, see how often
# the same hit-rate or better emerges by chance.
print()
print("="*72)
print("PERMUTATION NULL on prediction hit rate")
print("="*72)
rng = random.Random(42)
n_perm = 200
real_total_hits = hits_enr + hits_sup
real_total_predictions = len(PREDICTED_ENRICHED) + len(PREDICTED_SUPPRESSED)

def compute_hits(seqs):
    obs = Counter()
    for seq in seqs:
        for i in range(len(seq) - 1):
            obs[(seq[i], seq[i+1])] += 1
    marg = Counter()
    for seq in seqs:
        for p in seq:
            marg[p] += 1
    tot = sum(marg.values())
    h_e = h_s = 0
    for pair in PREDICTED_ENRICHED:
        bg_start = sum(obs[(pair[0], p2_)] for p2_ in prefixes)
        if bg_start == 0 or marg[pair[1]] == 0: continue
        exp_v = bg_start * marg[pair[1]] / tot
        if exp_v < 0.5: continue
        if obs[pair] / exp_v > 1.15:  # log2 > 0.2
            h_e += 1
    for pair in PREDICTED_SUPPRESSED:
        bg_start = sum(obs[(pair[0], p2_)] for p2_ in prefixes)
        if bg_start == 0 or marg[pair[1]] == 0: continue
        exp_v = bg_start * marg[pair[1]] / tot
        if exp_v < 0.5: continue
        if obs[pair] / exp_v < 0.87:  # log2 < -0.2
            h_s += 1
    return h_e, h_s

null_results = []
for _ in range(n_perm):
    shuffled = []
    for seq in line_seqs:
        sh = list(seq)
        rng.shuffle(sh)
        shuffled.append(sh)
    null_results.append(compute_hits(shuffled))

null_total_hits = [a + b for a, b in null_results]
n_above_real = sum(1 for h in null_total_hits if h >= real_total_hits)
p_value = n_above_real / n_perm

print(f"Real total hits: {real_total_hits}/{real_total_predictions}")
print(f"   Enriched: {hits_enr}/{len(PREDICTED_ENRICHED)}")
print(f"   Suppressed: {hits_sup}/{len(PREDICTED_SUPPRESSED)}")
print(f"Null distribution from {n_perm} within-line shuffles:")
mean_null = sum(null_total_hits)/n_perm
print(f"   Mean total hits in null: {mean_null:.2f}")
print(f"   Max in null: {max(null_total_hits)}")
print(f"   p-value (one-sided): {p_value:.4f}")

# Save
out = {
    'enrichment_matrix': {f'{p1}->{p2}': enrichment.get((p1,p2))
                          for p1 in prefixes for p2 in prefixes},
    'observed_bigrams': {f'{k[0]}->{k[1]}': v for k, v in observed.items()},
    'predictions': {
        'enriched': {f'{p1}->{p2}': enrichment.get((p1,p2))
                     for p1, p2 in PREDICTED_ENRICHED},
        'suppressed': {f'{p1}->{p2}': enrichment.get((p1,p2))
                       for p1, p2 in PREDICTED_SUPPRESSED},
    },
    'hits': {'enriched': hits_enr, 'suppressed': hits_sup,
             'total': real_total_hits, 'total_predictions': real_total_predictions},
    'permutation': {'p_value': p_value, 'mean_null_hits': mean_null,
                    'max_null_hits': max(null_total_hits), 'n_perm': n_perm},
}
with open('phases/PHASE_649_O_PREFIX_VALIDATION/results/sequencing_test.json', 'w') as f:
    json.dump(out, f, indent=2)
print()
print("Saved: phases/PHASE_649_O_PREFIX_VALIDATION/results/sequencing_test.json")
