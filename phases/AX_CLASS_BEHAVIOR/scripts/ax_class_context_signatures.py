"""
AX_CLASS_BEHAVIOR Script 3: Per-class context signatures.
Neighborhood analysis: what appears around each AX class?
Can context alone predict AX class identity?
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
sorted_classes = sorted(AX_CLASSES)

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

ROLES = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']

# Load transcript and build line structures
tx = Transcript()
lines = defaultdict(list)
for token in tx.currier_b():
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    lines[(token.folio, token.line)].append({
        'class': cls,
        'role': get_role(cls),
    })

print(f"Loaded {len(lines)} Currier B lines")

# ── Collect context per AX class ──

# Per-class context: left_role, right_role
class_left_roles = defaultdict(Counter)
class_right_roles = defaultdict(Counter)
class_tokens_count = Counter()

# Per-token context vectors for classification
token_contexts = []  # list of (ax_class, left_role_idx, right_role_idx)

role_to_idx = {r: i for i, r in enumerate(ROLES)}
role_to_idx['LINE_START'] = len(ROLES)
role_to_idx['LINE_END'] = len(ROLES) + 1
N_CONTEXT_FEATURES = len(ROLES) + 2  # 6 roles + LINE_START + LINE_END = 8

for line_key, toks in lines.items():
    n = len(toks)
    for i, tok in enumerate(toks):
        cls = tok['class']
        role = tok['role']
        if role != 'AX' or cls is None:
            continue

        class_tokens_count[cls] += 1

        # Left context
        if i > 0:
            left_role = toks[i - 1]['role']
        else:
            left_role = 'LINE_START'
        class_left_roles[cls][left_role] += 1

        # Right context
        if i + 1 < n:
            right_role = toks[i + 1]['role']
        else:
            right_role = 'LINE_END'
        class_right_roles[cls][right_role] += 1

        # Store for classification
        token_contexts.append((cls, left_role, right_role))

print(f"Total AX tokens with context: {len(token_contexts)}")

# ── Build per-class context distributions ──

all_context_roles = ROLES + ['LINE_START', 'LINE_END']

per_class_context = {}
for cls in sorted_classes:
    n = class_tokens_count.get(cls, 0)
    left_dist = {r: class_left_roles[cls].get(r, 0) for r in all_context_roles}
    right_dist = {r: class_right_roles[cls].get(r, 0) for r in all_context_roles}

    left_rates = {r: round(v / n, 4) if n > 0 else 0 for r, v in left_dist.items()}
    right_rates = {r: round(v / n, 4) if n > 0 else 0 for r, v in right_dist.items()}

    per_class_context[str(cls)] = {
        'n_tokens': n,
        'left_role_counts': left_dist,
        'right_role_counts': right_dist,
        'left_role_rates': left_rates,
        'right_role_rates': right_rates,
    }

# ── Compute population baseline (all AX tokens) ──

pop_left = Counter()
pop_right = Counter()
total_pop = len(token_contexts)

for cls, left, right in token_contexts:
    pop_left[left] += 1
    pop_right[right] += 1

pop_left_rates = {r: round(pop_left.get(r, 0) / total_pop, 4) for r in all_context_roles}
pop_right_rates = {r: round(pop_right.get(r, 0) / total_pop, 4) for r in all_context_roles}

# ── Bigram enrichment ──

bigram_enrichment = {}
for cls in sorted_classes:
    n = class_tokens_count.get(cls, 0)
    if n == 0:
        continue
    enrichments = {}
    for r in all_context_roles:
        # Left enrichment
        obs_left = class_left_roles[cls].get(r, 0) / n if n > 0 else 0
        exp_left = pop_left_rates.get(r, 0)
        enr_left = round(obs_left / exp_left, 3) if exp_left > 0.001 else None

        # Right enrichment
        obs_right = class_right_roles[cls].get(r, 0) / n if n > 0 else 0
        exp_right = pop_right_rates.get(r, 0)
        enr_right = round(obs_right / exp_right, 3) if exp_right > 0.001 else None

        enrichments[f'left_{r}'] = {
            'observed': round(obs_left, 4),
            'expected': round(exp_left, 4),
            'enrichment': enr_left,
        }
        enrichments[f'right_{r}'] = {
            'observed': round(obs_right, 4),
            'expected': round(exp_right, 4),
            'enrichment': enr_right,
        }
    bigram_enrichment[str(cls)] = enrichments

# ── Classification: nearest centroid using role context vectors ──

# Build class centroids (16D: 8 left + 8 right)
centroids = {}
for cls in sorted_classes:
    ctx = per_class_context[str(cls)]
    vec = []
    for r in all_context_roles:
        vec.append(ctx['left_role_rates'].get(r, 0))
    for r in all_context_roles:
        vec.append(ctx['right_role_rates'].get(r, 0))
    centroids[cls] = vec

def euclidean_dist(v1, v2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

# Leave-one-out classification
correct = 0
per_class_correct = Counter()
per_class_total = Counter()
confusion = Counter()  # (true, predicted) pairs

for ax_cls, left_role, right_role in token_contexts:
    # Build this token's context vector
    token_vec = [0.0] * (2 * len(all_context_roles))
    left_idx = all_context_roles.index(left_role) if left_role in all_context_roles else -1
    right_idx = all_context_roles.index(right_role) if right_role in all_context_roles else -1
    if left_idx >= 0:
        token_vec[left_idx] = 1.0
    if right_idx >= 0:
        token_vec[len(all_context_roles) + right_idx] = 1.0

    # Find nearest centroid
    best_cls = None
    best_dist = float('inf')
    for candidate_cls, centroid in centroids.items():
        d = euclidean_dist(token_vec, centroid)
        if d < best_dist:
            best_dist = d
            best_cls = candidate_cls

    per_class_total[ax_cls] += 1
    if best_cls == ax_cls:
        correct += 1
        per_class_correct[ax_cls] += 1
    else:
        confusion[(ax_cls, best_cls)] += 1

overall_accuracy = correct / len(token_contexts) if token_contexts else 0

# Weighted random baseline: sum(p_i^2)
class_fracs = {cls: class_tokens_count[cls] / total_pop for cls in sorted_classes}
weighted_baseline = sum(f ** 2 for f in class_fracs.values())

per_class_accuracy = {}
for cls in sorted_classes:
    total = per_class_total.get(cls, 0)
    corr = per_class_correct.get(cls, 0)
    per_class_accuracy[str(cls)] = round(corr / total, 4) if total > 0 else 0

# Top confusion pairs
top_confusion = confusion.most_common(10)

# ── Print summary ──

print(f"\n=== Context Signature Classification ===")
print(f"Overall accuracy: {overall_accuracy:.4f} ({correct}/{len(token_contexts)})")
print(f"Weighted random baseline: {weighted_baseline:.4f}")
print(f"Lift over baseline: {overall_accuracy / weighted_baseline:.2f}x" if weighted_baseline > 0 else "N/A")

print(f"\nPer-class accuracy:")
for cls in sorted_classes:
    acc = per_class_accuracy[str(cls)]
    n = per_class_total.get(cls, 0)
    print(f"  Class {cls:2d} (n={n:4d}): {acc:.3f}")

print(f"\nTop confusion pairs (true -> predicted):")
for (true_cls, pred_cls), count in top_confusion:
    print(f"  {true_cls} -> {pred_cls}: {count}")

# Find most contextually distinct classes
# (highest per-class accuracy)
most_distinct = sorted(
    [(cls, per_class_accuracy[str(cls)]) for cls in sorted_classes],
    key=lambda x: x[1], reverse=True
)[:5]

print(f"\nMost contextually distinct classes:")
for cls, acc in most_distinct:
    print(f"  Class {cls}: accuracy {acc:.3f}")

# ── Save results ──

results = {
    'per_class_context': per_class_context,
    'population_baseline': {
        'left_rates': pop_left_rates,
        'right_rates': pop_right_rates,
    },
    'bigram_enrichment': bigram_enrichment,
    'classification': {
        'method': 'nearest_centroid_one_hot_context',
        'features': f'{2 * len(all_context_roles)}D (8 left + 8 right role one-hot centroids)',
        'overall_accuracy': round(overall_accuracy, 4),
        'weighted_random_baseline': round(weighted_baseline, 4),
        'lift_over_baseline': round(overall_accuracy / weighted_baseline, 2) if weighted_baseline > 0 else None,
        'per_class_accuracy': per_class_accuracy,
        'top_confusion': [
            {'true': tc, 'predicted': pc, 'count': cnt}
            for (tc, pc), cnt in top_confusion
        ],
    },
    'summary': {
        'total_ax_tokens': total_pop,
        'n_classes': len(sorted_classes),
        'most_contextually_distinct': [{'class': c, 'accuracy': a} for c, a in most_distinct],
        'context_predicts_class': overall_accuracy > 2 * weighted_baseline,
    }
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'ax_class_context_signatures.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'ax_class_context_signatures.json'}")
