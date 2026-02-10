"""
LINE_CONTROL_BLOCK_GRAMMAR - Test 00: Token-Shape Negative Control

Purpose: Separate structural (role/position) effects from genuinely lexical
(token-identity) effects. Build a synthetic corpus where token strings are
replaced with new unique IDs but role, position, prefix family, and suffix
presence are preserved. Run core logic of Tests 01, 02, 04, 05 on synthetic
data. If effects survive -> structural. If effects vanish -> genuinely lexical.
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, str(Path('C:/git/voynich').resolve()))
from scripts.voynich import Transcript, Morphology

# ---------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path('C:/git/voynich').resolve()
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
RESULTS_PATH = PROJECT_ROOT / "phases/LINE_CONTROL_BLOCK_GRAMMAR/results/00_token_shape_negative_control.json"

with open(CLASS_MAP_PATH, 'r', encoding='utf-8') as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data['token_to_class'].items()}
class_to_role = {int(k): v for k, v in class_data['class_to_role'].items()}

tx = Transcript()
morph = Morphology()
rng = np.random.default_rng(42)
N_SHUFFLES = 1000

# ---------------------------------------------------------------------------
# BUILD LINES
# ---------------------------------------------------------------------------
lines = defaultdict(list)
for t in tx.currier_b():
    word = t.word.replace('*', '').strip()
    if not word:
        continue
    lines[(t.folio, t.line)].append(word)

# Annotate each token with structural properties
def get_structural_shape(word):
    """Extract structural properties: role, prefix_family, has_suffix."""
    cls = token_to_class.get(word, -1)
    role = class_to_role.get(cls, 'UNK') if cls >= 0 else 'UNK'
    m = morph.extract(word)
    prefix_family = 'none'
    has_suffix = False
    if m:
        if m.prefix:
            # Collapse to family: ch, sh, qo, da, ok, ot, ol, ct, other
            pf = m.prefix
            if pf in ('ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct'):
                prefix_family = pf
            else:
                prefix_family = 'other'
        has_suffix = m.suffix is not None and len(m.suffix) > 0
    return (role, prefix_family, has_suffix)

# Build annotated lines
annotated_lines = {}
for key, words in lines.items():
    ann = []
    for i, w in enumerate(words):
        shape = get_structural_shape(w)
        ann.append({
            'word': w,
            'role': shape[0],
            'prefix_family': shape[1],
            'has_suffix': shape[2],
            'is_initial': (i == 0),
            'is_final': (i == len(words) - 1),
            'is_medial': (i > 0 and i < len(words) - 1),
        })
    annotated_lines[key] = ann

# ---------------------------------------------------------------------------
# BUILD SYNTHETIC CORPUS
# ---------------------------------------------------------------------------
# Replace token identity with a synthetic ID based on structural shape
# Each unique (role, prefix_family, has_suffix) combo gets IDs syn_0, syn_1, ...
# Tokens with the same shape get DIFFERENT synthetic IDs (preserving type count)
# but identity is randomized within shape group

shape_to_words = defaultdict(list)
for key, ann in annotated_lines.items():
    for tok in ann:
        shape = (tok['role'], tok['prefix_family'], tok['has_suffix'])
        shape_to_words[shape].append(tok['word'])

# Create mapping: real word -> synthetic word
# Within each shape group, randomly reassign tokens
word_to_synthetic = {}
for shape, word_list in shape_to_words.items():
    unique_words = list(set(word_list))
    shuffled = rng.permutation(unique_words).tolist()
    for orig, syn in zip(unique_words, shuffled):
        word_to_synthetic[orig] = f"syn_{shape[0]}_{shape[1]}_{syn}"

# Build synthetic annotated lines
synthetic_lines = {}
for key, ann in annotated_lines.items():
    syn_ann = []
    for tok in ann:
        syn_tok = dict(tok)
        syn_tok['word'] = word_to_synthetic.get(tok['word'], f"syn_UNK_{tok['word']}")
        syn_ann.append(syn_tok)
    synthetic_lines[key] = syn_ann

print("=" * 70)
print("TEST 00: TOKEN-SHAPE NEGATIVE CONTROL")
print("=" * 70)
print(f"  Lines: {len(annotated_lines)}")
print(f"  Unique real tokens: {len(set(w for ann in annotated_lines.values() for w in [t['word'] for t in ann]))}")
print(f"  Unique synthetic tokens: {len(set(w for ann in synthetic_lines.values() for w in [t['word'] for t in ann]))}")
print(f"  Shape groups: {len(shape_to_words)}")
print()

# ---------------------------------------------------------------------------
# CONTROL A: Positional Exclusivity (mirrors Test 01)
# ---------------------------------------------------------------------------
print("-" * 70)
print("CONTROL A: Positional Exclusivity (Test 01 mirror)")
print("-" * 70)

def compute_exclusivity(line_data, use_key='word'):
    """Count tokens that are exclusive to certain positions."""
    token_zone = defaultdict(lambda: {'INITIAL': 0, 'MEDIAL': 0, 'FINAL': 0})
    for key, ann in line_data.items():
        for tok in ann:
            zone = 'INITIAL' if tok['is_initial'] else ('FINAL' if tok['is_final'] else 'MEDIAL')
            token_zone[tok[use_key]][zone] += 1

    n_exclusive = 0
    n_tested = 0
    for token, zones in token_zone.items():
        total = sum(zones.values())
        if total < 10:
            continue
        n_tested += 1
        if any(v == 0 for v in zones.values()):
            n_exclusive += 1
    return n_exclusive, n_tested

# Real data
real_excl, real_tested = compute_exclusivity(annotated_lines)
# Synthetic data
syn_excl, syn_tested = compute_exclusivity(synthetic_lines)

# Shuffle baseline for real
shuf_excl_real = []
for _ in range(N_SHUFFLES):
    shuffled = {}
    for key, ann in annotated_lines.items():
        n = len(ann)
        perm = rng.permutation(n)
        new_ann = []
        for j, idx in enumerate(perm):
            tok = dict(ann[idx])
            tok['is_initial'] = (j == 0)
            tok['is_final'] = (j == n - 1)
            tok['is_medial'] = (j > 0 and j < n - 1)
            new_ann.append(tok)
        shuffled[key] = new_ann
    se, _ = compute_exclusivity(shuffled)
    shuf_excl_real.append(se)

# Shuffle baseline for synthetic
shuf_excl_syn = []
for _ in range(N_SHUFFLES):
    shuffled = {}
    for key, ann in synthetic_lines.items():
        n = len(ann)
        perm = rng.permutation(n)
        new_ann = []
        for j, idx in enumerate(perm):
            tok = dict(ann[idx])
            tok['is_initial'] = (j == 0)
            tok['is_final'] = (j == n - 1)
            tok['is_medial'] = (j > 0 and j < n - 1)
            new_ann.append(tok)
        shuffled[key] = new_ann
    se, _ = compute_exclusivity(shuffled)
    shuf_excl_syn.append(se)

real_p = sum(1 for s in shuf_excl_real if s >= real_excl) / N_SHUFFLES
syn_p = sum(1 for s in shuf_excl_syn if s >= syn_excl) / N_SHUFFLES

print(f"  Real: {real_excl}/{real_tested} exclusive (shuffle mean {np.mean(shuf_excl_real):.1f}, p={real_p:.4f})")
print(f"  Synthetic: {syn_excl}/{syn_tested} exclusive (shuffle mean {np.mean(shuf_excl_syn):.1f}, p={syn_p:.4f})")
print(f"  Survives control: {'YES' if syn_p < 0.01 else 'NO (structural)'}")
print()

# ---------------------------------------------------------------------------
# CONTROL B: Forbidden Bigrams (mirrors Test 02)
# ---------------------------------------------------------------------------
print("-" * 70)
print("CONTROL B: Forbidden Bigrams (Test 02 mirror)")
print("-" * 70)

def compute_forbidden_bigrams(line_data, use_key='word', min_count=10):
    """Count forbidden bigrams (obs=0, expected>=5)."""
    # Count tokens and bigrams
    token_counts = Counter()
    bigram_counts = Counter()
    total_bigrams = 0

    for key, ann in line_data.items():
        for tok in ann:
            token_counts[tok[use_key]] += 1
        for i in range(len(ann) - 1):
            bigram_counts[(ann[i][use_key], ann[i+1][use_key])] += 1
            total_bigrams += 1

    # Filter to common tokens
    common = {t for t, c in token_counts.items() if c >= min_count}

    n_forbidden = 0
    forbidden_list = []
    for a in common:
        for b in common:
            obs = bigram_counts.get((a, b), 0)
            exp = token_counts[a] * token_counts[b] / total_bigrams if total_bigrams > 0 else 0
            if obs == 0 and exp >= 5.0:
                n_forbidden += 1
                forbidden_list.append((a, b, exp))

    return n_forbidden, len(common), forbidden_list

real_forb, real_common, _ = compute_forbidden_bigrams(annotated_lines)
syn_forb, syn_common, _ = compute_forbidden_bigrams(synthetic_lines)

# Shuffle for real
shuf_forb_real = []
for _ in range(N_SHUFFLES):
    shuffled = {}
    for key, ann in annotated_lines.items():
        perm = rng.permutation(len(ann)).tolist()
        shuffled[key] = [ann[i] for i in perm]
    sf, _, _ = compute_forbidden_bigrams(shuffled)
    shuf_forb_real.append(sf)

# Shuffle for synthetic
shuf_forb_syn = []
for _ in range(N_SHUFFLES):
    shuffled = {}
    for key, ann in synthetic_lines.items():
        perm = rng.permutation(len(ann)).tolist()
        shuffled[key] = [ann[i] for i in perm]
    sf, _, _ = compute_forbidden_bigrams(shuffled)
    shuf_forb_syn.append(sf)

real_forb_p = sum(1 for s in shuf_forb_real if s >= real_forb) / N_SHUFFLES
syn_forb_p = sum(1 for s in shuf_forb_syn if s >= syn_forb) / N_SHUFFLES

print(f"  Real: {real_forb} forbidden (common tokens: {real_common}, shuffle mean {np.mean(shuf_forb_real):.1f}, p={real_forb_p:.4f})")
print(f"  Synthetic: {syn_forb} forbidden (common tokens: {syn_common}, shuffle mean {np.mean(shuf_forb_syn):.1f}, p={syn_forb_p:.4f})")
print(f"  Survives control: {'YES' if syn_forb_p < 0.01 else 'NO (structural)'}")
print()

# ---------------------------------------------------------------------------
# CONTROL C: Opener Prediction (mirrors Test 04)
# ---------------------------------------------------------------------------
print("-" * 70)
print("CONTROL C: Opener Classification (Test 04 mirror)")
print("-" * 70)

def compute_opener_classification(line_data, use_key='word'):
    """Nearest-centroid classifier: predict opener role from body tokens."""
    from collections import Counter

    # Group lines by opener role
    role_bodies = defaultdict(list)
    for key, ann in line_data.items():
        if len(ann) < 3:
            continue
        opener_role = ann[0]['role']
        if opener_role == 'UNK':
            continue
        body_tokens = [tok[use_key] for tok in ann[1:]]
        role_bodies[opener_role].append(Counter(body_tokens))

    # Only roles with 30+ lines
    valid_roles = {r for r, bodies in role_bodies.items() if len(bodies) >= 30}
    if len(valid_roles) < 2:
        return 0.0, 0.0, 0

    # Build vocabulary
    all_tokens = set()
    all_samples = []
    all_labels = []
    for role in sorted(valid_roles):
        for body_counter in role_bodies[role]:
            all_tokens.update(body_counter.keys())
            all_samples.append(body_counter)
            all_labels.append(role)

    vocab = sorted(all_tokens)
    vocab_idx = {t: i for i, t in enumerate(vocab)}

    # Vectorize
    X = np.zeros((len(all_samples), len(vocab)))
    for i, counter in enumerate(all_samples):
        total = sum(counter.values())
        for tok, cnt in counter.items():
            if tok in vocab_idx:
                X[i, vocab_idx[tok]] = cnt / total

    labels = np.array(all_labels)
    unique_labels = sorted(valid_roles)

    # LOO nearest centroid
    correct = 0
    for i in range(len(X)):
        # Compute centroids without sample i
        centroids = {}
        for lbl in unique_labels:
            mask = (labels != labels[i]) if False else np.array([j != i and labels[j] == lbl for j in range(len(labels))])
            if mask.sum() == 0:
                continue
            centroids[lbl] = X[mask].mean(axis=0)

        # Predict
        best_dist = float('inf')
        pred = None
        for lbl, centroid in centroids.items():
            dist = np.sum((X[i] - centroid) ** 2)
            if dist < best_dist:
                best_dist = dist
                pred = lbl

        if pred == labels[i]:
            correct += 1

    accuracy = correct / len(X) if len(X) > 0 else 0
    chance = 1.0 / len(unique_labels) if unique_labels else 0
    return accuracy, chance, len(X)

real_acc, real_chance, real_n = compute_opener_classification(annotated_lines)
syn_acc, syn_chance, syn_n = compute_opener_classification(synthetic_lines)

print(f"  Real: accuracy={real_acc:.3f} (chance={real_chance:.3f}, n={real_n})")
print(f"  Synthetic: accuracy={syn_acc:.3f} (chance={syn_chance:.3f}, n={syn_n})")
print(f"  Survives control: {'YES' if syn_acc > real_chance * 1.5 else 'NO (structural)'}")
print()

# ---------------------------------------------------------------------------
# CONTROL D: Boundary Gini (mirrors Test 05)
# ---------------------------------------------------------------------------
print("-" * 70)
print("CONTROL D: Boundary Gini (Test 05 mirror)")
print("-" * 70)

def compute_gini(values):
    """Compute Gini coefficient."""
    arr = np.array(sorted(values), dtype=float)
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * arr) - (n + 1) * arr.sum()) / (n * arr.sum())

def compute_boundary_gini(line_data, use_key='word'):
    """Compute Gini coefficient for initial and final token distributions."""
    initial_counts = Counter()
    final_counts = Counter()
    for key, ann in line_data.items():
        if len(ann) >= 2:
            initial_counts[ann[0][use_key]] += 1
            final_counts[ann[-1][use_key]] += 1

    init_gini = compute_gini(list(initial_counts.values()))
    final_gini = compute_gini(list(final_counts.values()))
    return init_gini, final_gini

real_init_gini, real_final_gini = compute_boundary_gini(annotated_lines)
syn_init_gini, syn_final_gini = compute_boundary_gini(synthetic_lines)

# Shuffle for real
shuf_init_ginis = []
shuf_final_ginis = []
for _ in range(N_SHUFFLES):
    shuffled = {}
    for key, ann in annotated_lines.items():
        perm = rng.permutation(len(ann)).tolist()
        shuffled[key] = [ann[i] for i in perm]
    ig, fg = compute_boundary_gini(shuffled)
    shuf_init_ginis.append(ig)
    shuf_final_ginis.append(fg)

print(f"  Real initial Gini: {real_init_gini:.4f} (shuffle mean {np.mean(shuf_init_ginis):.4f})")
print(f"  Real final Gini: {real_final_gini:.4f} (shuffle mean {np.mean(shuf_final_ginis):.4f})")
print(f"  Synthetic initial Gini: {syn_init_gini:.4f}")
print(f"  Synthetic final Gini: {syn_final_gini:.4f}")
print(f"  Gini survives control: {'YES' if syn_init_gini > 0.6 else 'NO (structural)'}")
print()

# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------
print("=" * 70)
print("SUMMARY: Token-Shape Negative Control")
print("=" * 70)

controls = {
    'exclusivity': {
        'real': real_excl, 'synthetic': syn_excl,
        'real_shuffle_mean': float(np.mean(shuf_excl_real)),
        'real_p': real_p, 'syn_p': syn_p,
        'survives': syn_p < 0.01,
    },
    'forbidden_bigrams': {
        'real': real_forb, 'synthetic': syn_forb,
        'real_shuffle_mean': float(np.mean(shuf_forb_real)),
        'real_p': real_forb_p, 'syn_p': syn_forb_p,
        'survives': syn_forb_p < 0.01,
    },
    'opener_classification': {
        'real_accuracy': real_acc, 'synthetic_accuracy': syn_acc,
        'chance': real_chance, 'n': real_n,
        'survives': syn_acc > real_chance * 1.5,
    },
    'boundary_gini': {
        'real_initial': real_init_gini, 'real_final': real_final_gini,
        'synthetic_initial': syn_init_gini, 'synthetic_final': syn_final_gini,
        'shuffle_initial_mean': float(np.mean(shuf_init_ginis)),
        'shuffle_final_mean': float(np.mean(shuf_final_ginis)),
        'survives': syn_init_gini > 0.6,
    },
}

n_survive = sum(1 for c in controls.values() if c['survives'])
print(f"  Controls surviving: {n_survive}/4")
for name, ctrl in controls.items():
    status = "STRUCTURAL (survives)" if ctrl['survives'] else "LEXICAL (vanishes)"
    print(f"  {name}: {status}")

interpretation = (
    "Most effects are structural (role/position driven)" if n_survive >= 3
    else "Mixed: some structural, some lexical" if n_survive >= 1
    else "Effects are genuinely lexical (token-identity driven)"
)
print(f"\n  Interpretation: {interpretation}")

# ---------------------------------------------------------------------------
# JSON OUTPUT
# ---------------------------------------------------------------------------
output = {
    'test': 'Token-Shape Negative Control',
    'purpose': 'Separate structural (role/position) effects from lexical (token-identity) effects',
    'method': 'Build synthetic corpus preserving role, prefix_family, has_suffix but randomizing token identity',
    'n_lines': len(annotated_lines),
    'n_shape_groups': len(shape_to_words),
    'n_shuffles': N_SHUFFLES,
    'controls': {k: {kk: (float(vv) if isinstance(vv, (np.floating, np.integer)) else (bool(vv) if isinstance(vv, np.bool_) else vv)) for kk, vv in v.items()} for k, v in controls.items()},
    'n_survive': int(n_survive),
    'interpretation': interpretation,
}

with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {RESULTS_PATH}")
