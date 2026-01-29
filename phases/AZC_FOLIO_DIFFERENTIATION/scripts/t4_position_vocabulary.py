"""
T4: Position-Vocabulary Analysis

Question: Does diagram position (R, S, C, etc.) determine vocabulary profile?

Method:
1. Group AZC tokens by placement code (R1, R2, R3, S1, S2, C, etc.)
2. Compute PREFIX and MIDDLE profiles per position
3. Test: do different positions have different vocabulary signatures?

Key positions:
- R, R1-R4: Ring positions (continuous circular text)
- S, S0-S3: Star/spoke or nymph-interrupted positions
- C, C1-C2: Circle/center positions
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Collect AZC tokens by placement (diagram text only)
print("Collecting AZC tokens by placement...")
placement_tokens = defaultdict(list)
placement_prefixes = defaultdict(Counter)
placement_middles = defaultdict(Counter)

for token in tx.azc():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    placement = getattr(token, 'placement', '')
    if not placement or placement.startswith('P'):  # Skip P-text (Currier A)
        continue

    m = morph.extract(w)

    placement_tokens[placement].append(w)
    if m.prefix:
        placement_prefixes[placement][m.prefix] += 1
    if m.middle:
        placement_middles[placement][m.middle] += 1

print(f"Found {len(placement_tokens)} distinct placements")

# Show placement counts
print("\n" + "="*60)
print("PLACEMENT TOKEN COUNTS")
print("="*60)

for p in sorted(placement_tokens.keys(), key=lambda x: len(placement_tokens[x]), reverse=True):
    print(f"  {p:4}: {len(placement_tokens[p]):4} tokens")

# Group placements into categories
R_SERIES = ['R', 'R1', 'R2', 'R3', 'R4']
S_SERIES = ['S', 'S0', 'S1', 'S2', 'S3']
C_SERIES = ['C', 'C1', 'C2']
OTHER = [p for p in placement_tokens.keys() if p not in R_SERIES + S_SERIES + C_SERIES]

# Aggregate prefix profiles by category
def aggregate_counter(placements, counter_dict):
    """Aggregate counters across multiple placements."""
    result = Counter()
    for p in placements:
        if p in counter_dict:
            result.update(counter_dict[p])
    return result

r_prefixes = aggregate_counter(R_SERIES, placement_prefixes)
s_prefixes = aggregate_counter(S_SERIES, placement_prefixes)
c_prefixes = aggregate_counter(C_SERIES, placement_prefixes)

r_middles = aggregate_counter(R_SERIES, placement_middles)
s_middles = aggregate_counter(S_SERIES, placement_middles)
c_middles = aggregate_counter(C_SERIES, placement_middles)

print("\n" + "="*60)
print("PREFIX PROFILES BY POSITION CATEGORY")
print("="*60)

# Define canonical prefixes
PREFIXES = ['qo', 'ch', 'sh', 'ol', 'or', 'ok', 'ot', 'd', 's', 'o']

def profile_row(counter, prefixes):
    """Return prefix profile as percentage vector."""
    total = sum(counter.values())
    return [100.0 * counter.get(p, 0) / total if total > 0 else 0 for p in prefixes]

r_profile = profile_row(r_prefixes, PREFIXES)
s_profile = profile_row(s_prefixes, PREFIXES)
c_profile = profile_row(c_prefixes, PREFIXES)

# Token counts
r_total = sum(len(placement_tokens[p]) for p in R_SERIES if p in placement_tokens)
s_total = sum(len(placement_tokens[p]) for p in S_SERIES if p in placement_tokens)
c_total = sum(len(placement_tokens[p]) for p in C_SERIES if p in placement_tokens)

print(f"\n{'Prefix':<6} {'R-series':>10} {'S-series':>10} {'C-series':>10}")
print(f"{'      ':<6} {f'(n={r_total})':>10} {f'(n={s_total})':>10} {f'(n={c_total})':>10}")
print("-" * 40)
for i, p in enumerate(PREFIXES):
    print(f"{p:<6} {r_profile[i]:>9.1f}% {s_profile[i]:>9.1f}% {c_profile[i]:>9.1f}%")

# Compute cosine similarity between profiles
def cosine_sim(a, b):
    """Cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

print("\n" + "="*60)
print("PROFILE SIMILARITY (COSINE)")
print("="*60)

print(f"R-S similarity: {cosine_sim(r_profile, s_profile):.3f}")
print(f"R-C similarity: {cosine_sim(r_profile, c_profile):.3f}")
print(f"S-C similarity: {cosine_sim(s_profile, c_profile):.3f}")

# Subscript-level analysis (R1 vs R2 vs R3)
print("\n" + "="*60)
print("R-SERIES SUBSCRIPT COMPARISON")
print("="*60)

r_subscript_profiles = {}
for p in ['R1', 'R2', 'R3']:
    if p in placement_prefixes:
        profile = profile_row(placement_prefixes[p], PREFIXES)
        n = len(placement_tokens.get(p, []))
        r_subscript_profiles[p] = {'profile': profile, 'n': n}
        print(f"\n{p} (n={n}):")
        for i, pr in enumerate(PREFIXES):
            if profile[i] > 1:
                print(f"  {pr}: {profile[i]:.1f}%")

# R-series subscript similarity
if all(p in r_subscript_profiles for p in ['R1', 'R2', 'R3']):
    r1 = r_subscript_profiles['R1']['profile']
    r2 = r_subscript_profiles['R2']['profile']
    r3 = r_subscript_profiles['R3']['profile']
    print(f"\nR1-R2 similarity: {cosine_sim(r1, r2):.3f}")
    print(f"R1-R3 similarity: {cosine_sim(r1, r3):.3f}")
    print(f"R2-R3 similarity: {cosine_sim(r2, r3):.3f}")

# S-series subscript analysis (nymph vs spoke positions)
print("\n" + "="*60)
print("S-SERIES SUBSCRIPT COMPARISON")
print("="*60)

s_subscript_profiles = {}
for p in ['S', 'S0', 'S1', 'S2']:
    if p in placement_prefixes:
        profile = profile_row(placement_prefixes[p], PREFIXES)
        n = len(placement_tokens.get(p, []))
        s_subscript_profiles[p] = {'profile': profile, 'n': n}
        print(f"\n{p} (n={n}):")
        for i, pr in enumerate(PREFIXES):
            if profile[i] > 1:
                print(f"  {pr}: {profile[i]:.1f}%")

# Test: chi-squared for independence of position x prefix
print("\n" + "="*60)
print("STATISTICAL TESTS")
print("="*60)

# Build contingency table: positions x prefixes (only prefixes with nonzero counts)
positions = ['R_series', 'S_series', 'C_series']
position_counters = [r_prefixes, s_prefixes, c_prefixes]

# Filter to prefixes that have at least some counts
active_prefixes = [p for p in PREFIXES if any(c.get(p, 0) > 0 for c in position_counters)]

observed = []
for counter in position_counters:
    row = [counter.get(p, 0) for p in active_prefixes]
    observed.append(row)

# Check for zero columns
col_sums = [sum(observed[i][j] for i in range(len(observed))) for j in range(len(active_prefixes))]
final_prefixes = [p for p, s in zip(active_prefixes, col_sums) if s > 0]
observed = [[observed[i][j] for j, p in enumerate(active_prefixes) if col_sums[j] > 0] for i in range(len(observed))]

if len(final_prefixes) >= 2 and all(sum(row) > 0 for row in observed):
    chi2, p_val, dof, expected = stats.chi2_contingency(observed)
    print(f"Position x PREFIX independence test (prefixes: {final_prefixes}):")
    print(f"  Chi-squared: {chi2:.2f}, df={dof}, p={p_val:.6f}")
else:
    chi2, p_val, dof = 0, 1.0, 0
    print(f"Insufficient variance for chi-squared test")

# Effect size: Cramer's V
n = sum(sum(row) for row in observed)
min_dim = min(len(observed), len(observed[0])) - 1
cramers_v = np.sqrt(chi2 / (n * min_dim)) if n > 0 and min_dim > 0 else 0
print(f"  Cramer's V: {cramers_v:.3f}")

# Results
results = {
    'placement_counts': {p: len(tokens) for p, tokens in placement_tokens.items()},
    'r_series_total': r_total,
    's_series_total': s_total,
    'c_series_total': c_total,
    'r_profile': {PREFIXES[i]: r_profile[i] for i in range(len(PREFIXES))},
    's_profile': {PREFIXES[i]: s_profile[i] for i in range(len(PREFIXES))},
    'c_profile': {PREFIXES[i]: c_profile[i] for i in range(len(PREFIXES))},
    'similarity': {
        'r_s': cosine_sim(r_profile, s_profile),
        'r_c': cosine_sim(r_profile, c_profile),
        's_c': cosine_sim(s_profile, c_profile),
    },
    'chi2': float(chi2),
    'chi2_p': float(p_val),
    'cramers_v': float(cramers_v),
}

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

if p_val < 0.001 and cramers_v > 0.15:
    verdict = "POSITION_DETERMINES_VOCABULARY"
    print(f"Position SIGNIFICANTLY affects PREFIX profile (p<0.001, V={cramers_v:.3f})")
elif p_val < 0.05:
    verdict = "WEAK_POSITION_EFFECT"
    print(f"Weak position effect on PREFIX profile (p={p_val:.4f}, V={cramers_v:.3f})")
else:
    verdict = "NO_POSITION_EFFECT"
    print(f"Position does NOT significantly affect PREFIX profile (p={p_val:.4f})")

results['verdict'] = verdict

out_path = Path(__file__).parent.parent / 'results' / 't4_position_vocabulary.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print(f"\nResults saved to {out_path}")
