"""
AX_CLASS_BEHAVIOR Script 1: Per-class transition matrix analysis.
Build 20x20 AX-to-AX and 20x6 AX-to-role transition matrices.
Test whether per-class transitions are structured or uniform.
"""
import sys
sys.path.insert(0, 'C:/git/voynich')

import json
import math
from pathlib import Path
from collections import defaultdict, Counter
from scripts.voynich import Transcript

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
CENSUS_FILE = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_census.json'
RESULTS = BASE / 'phases/AX_CLASS_BEHAVIOR/results'

# Load class map
with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Load AX census
with open(CENSUS_FILE) as f:
    census = json.load(f)
AX_CLASSES = set(census['definitive_ax_classes'])

# Role mapping
ICC_CC = {10, 11, 12, 17}
ICC_EN = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}
ICC_FL = {7, 30, 38, 40}
ICC_FQ = {9, 13, 23}

def get_role(cls):
    if cls is None: return 'UN'
    if cls in ICC_CC: return 'CC'
    if cls in ICC_EN: return 'EN'
    if cls in ICC_FL: return 'FL'
    if cls in ICC_FQ: return 'FQ'
    if cls in AX_CLASSES: return 'AX'
    return 'UN'

# Load transcript and build line structures
tx = Transcript()
lines = defaultdict(list)
for token in tx.currier_b():
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    lines[(token.folio, token.line)].append({
        'word': word,
        'class': cls,
        'role': get_role(cls),
    })

print(f"Loaded {len(lines)} Currier B lines")

# ── Build transition matrices ──

# AX-to-immediate-next (any class)
ax_to_next_class = defaultdict(Counter)  # ax_class -> next_class counter
ax_to_next_role = defaultdict(Counter)   # ax_class -> next_role counter
ax_to_prev_role = defaultdict(Counter)   # ax_class -> prev_role counter

# AX-to-next-AX (skip non-AX tokens)
ax_to_next_ax = defaultdict(Counter)     # ax_class -> next_ax_class counter

ax_class_counts = Counter()

for line_key, toks in lines.items():
    n = len(toks)
    ax_indices = []

    for i, tok in enumerate(toks):
        cls = tok['class']
        role = tok['role']

        if role == 'AX' and cls is not None:
            ax_class_counts[cls] += 1
            ax_indices.append(i)

            # Immediate next token
            if i + 1 < n:
                next_tok = toks[i + 1]
                next_cls = next_tok['class']
                next_role = next_tok['role']
                ax_to_next_class[cls][next_cls] += 1
                ax_to_next_role[cls][next_role] += 1
            else:
                ax_to_next_role[cls]['LINE_END'] += 1

            # Immediate previous token
            if i > 0:
                prev_tok = toks[i - 1]
                prev_role = prev_tok['role']
                ax_to_prev_role[cls][prev_role] += 1
            else:
                ax_to_prev_role[cls]['LINE_START'] += 1

    # AX-to-next-AX transitions (within line)
    for j in range(len(ax_indices) - 1):
        curr_cls = toks[ax_indices[j]]['class']
        next_cls = toks[ax_indices[j + 1]]['class']
        ax_to_next_ax[curr_cls][next_cls] += 1

print(f"Total AX tokens: {sum(ax_class_counts.values())}")
print(f"AX classes found: {sorted(ax_class_counts.keys())}")

# ── Compute per-class metrics ──

total_ax = sum(ax_class_counts.values())
sorted_classes = sorted(AX_CLASSES)

per_class_metrics = {}
for cls in sorted_classes:
    n_tokens = ax_class_counts.get(cls, 0)

    # Self-chain rate (AX-to-AX)
    ax_successors = ax_to_next_ax[cls]
    total_ax_successors = sum(ax_successors.values())
    self_chain_count = ax_successors.get(cls, 0)
    self_chain_rate = self_chain_count / total_ax_successors if total_ax_successors > 0 else 0
    expected_self_chain = n_tokens / total_ax if total_ax > 0 else 0

    # Transition entropy
    if total_ax_successors > 0:
        probs = [c / total_ax_successors for c in ax_successors.values() if c > 0]
        entropy = -sum(p * math.log2(p) for p in probs)
        max_entropy = math.log2(len(ax_successors)) if len(ax_successors) > 1 else 0
    else:
        entropy = 0
        max_entropy = 0

    # Chi-squared test against marginal distribution
    chi2_stat = 0
    chi2_df = 0
    chi2_p = None

    if total_ax_successors >= 20:
        # Expected: proportional to marginal AX class frequencies
        observed = []
        expected = []
        for target_cls in sorted_classes:
            obs = ax_successors.get(target_cls, 0)
            exp = total_ax_successors * (ax_class_counts.get(target_cls, 0) / total_ax)
            if exp >= 1:  # Only include cells with expected >= 1
                observed.append(obs)
                expected.append(exp)

        if len(observed) > 1:
            chi2_stat = sum((o - e) ** 2 / e for o, e in zip(observed, expected))
            chi2_df = len(observed) - 1
            # Approximate p-value using chi-squared survival function
            # For large df, use normal approximation
            if chi2_df > 0:
                z = (chi2_stat - chi2_df) / math.sqrt(2 * chi2_df)
                # Normal CDF approximation for survival
                chi2_p = 0.5 * math.erfc(z / math.sqrt(2))

    # Preferred successor and predecessor (role level)
    role_successors = ax_to_next_role[cls]
    total_role_succ = sum(v for k, v in role_successors.items() if k != 'LINE_END')
    preferred_role_succ = role_successors.most_common(1)[0] if role_successors else (None, 0)

    role_predecessors = ax_to_prev_role[cls]
    total_role_pred = sum(v for k, v in role_predecessors.items() if k != 'LINE_START')
    preferred_role_pred = role_predecessors.most_common(1)[0] if role_predecessors else (None, 0)

    # Preferred AX successor
    preferred_ax_succ = ax_successors.most_common(1)[0] if ax_successors else (None, 0)

    per_class_metrics[str(cls)] = {
        'n_tokens': n_tokens,
        'total_ax_successors': total_ax_successors,
        'self_chain_count': self_chain_count,
        'self_chain_rate': round(self_chain_rate, 4),
        'expected_self_chain_rate': round(expected_self_chain, 4),
        'self_chain_enrichment': round(self_chain_rate / expected_self_chain, 3) if expected_self_chain > 0 else None,
        'transition_entropy': round(entropy, 3),
        'transition_max_entropy': round(max_entropy, 3),
        'transition_normalized_entropy': round(entropy / max_entropy, 3) if max_entropy > 0 else None,
        'chi_squared': {
            'statistic': round(chi2_stat, 2),
            'df': chi2_df,
            'p_value': round(chi2_p, 6) if chi2_p is not None else None,
            'is_structured': chi2_p < 0.01 if chi2_p is not None else None,
        },
        'preferred_ax_successor': {'class': preferred_ax_succ[0], 'count': preferred_ax_succ[1]},
        'preferred_role_successor': {'role': preferred_role_succ[0], 'count': preferred_role_succ[1]},
        'preferred_role_predecessor': {'role': preferred_role_pred[0], 'count': preferred_role_pred[1]},
        'role_successor_dist': dict(role_successors),
        'role_predecessor_dist': dict(role_predecessors),
    }

# ── Build matrix representations ──

ax_to_ax_matrix = {}
for cls in sorted_classes:
    ax_to_ax_matrix[str(cls)] = {str(t): ax_to_next_ax[cls].get(t, 0) for t in sorted_classes}

ax_to_role_matrix = {}
roles = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN', 'LINE_END']
for cls in sorted_classes:
    ax_to_role_matrix[str(cls)] = {r: ax_to_next_role[cls].get(r, 0) for r in roles}

# ── Summary statistics ──

structured_count = sum(
    1 for m in per_class_metrics.values()
    if m['chi_squared']['is_structured'] is True
)
insufficient_data = [
    int(k) for k, m in per_class_metrics.items()
    if m['total_ax_successors'] < 20
]
mean_self_chain = sum(
    m['self_chain_rate'] for m in per_class_metrics.values()
) / len(per_class_metrics)
mean_entropy = sum(
    m['transition_entropy'] for m in per_class_metrics.values()
    if m['transition_entropy'] > 0
) / max(1, sum(1 for m in per_class_metrics.values() if m['transition_entropy'] > 0))

# ── Print summary ──

print(f"\n=== AX Class Transition Analysis ===")
print(f"Classes with structured transitions (p<0.01): {structured_count}/20")
print(f"Classes with insufficient data (<20 AX successors): {len(insufficient_data)}")
print(f"Mean self-chain rate: {mean_self_chain:.4f}")
print(f"Mean transition entropy: {mean_entropy:.3f}")

print(f"\nPer-class summary:")
for cls in sorted_classes:
    m = per_class_metrics[str(cls)]
    struct = "STRUCTURED" if m['chi_squared']['is_structured'] else ("insufficient" if m['chi_squared']['p_value'] is None else "uniform")
    enrichment = m['self_chain_enrichment']
    enr_str = f"{enrichment:.2f}x" if enrichment is not None else "N/A"
    print(f"  Class {cls:2d}: {m['n_tokens']:4d} tokens, "
          f"self-chain {m['self_chain_rate']:.3f} ({enr_str}), "
          f"entropy {m['transition_entropy']:.2f}, "
          f"{struct}")

# ── Save results ──

results = {
    'ax_to_ax_matrix': ax_to_ax_matrix,
    'ax_to_role_matrix': ax_to_role_matrix,
    'per_class_metrics': per_class_metrics,
    'summary': {
        'total_ax_tokens': sum(ax_class_counts.values()),
        'n_classes': len(sorted_classes),
        'classes_with_structured_transitions': structured_count,
        'classes_insufficient_data': insufficient_data,
        'mean_self_chain_rate': round(mean_self_chain, 4),
        'mean_transition_entropy': round(mean_entropy, 3),
    }
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'ax_class_transition_matrix.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'ax_class_transition_matrix.json'}")
