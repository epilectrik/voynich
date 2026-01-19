"""Phase S-2: Role Polarity Test.

For each candidate token, independently measure:
- Mean neighbors (content vs grammar)
- Positional bias (flat/mid-line vs grammar-slot constrained)
- Co-occurrence with hazards (required/forbidden in B)
- Pairing partners (none/loose vs tight/systematic)

We are looking for ROLE POLARITY - tokens that behave grammatically in B
but structurally/delimitively in A.
"""
from pathlib import Path
from collections import Counter, defaultdict
import json

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
grammar_path = project_root / 'results' / 'canonical_grammar.json'
hazards_path = project_root / 'vee' / 'app' / 'core' / 'hazards.py'

# Load grammar
with open(grammar_path) as f:
    grammar = json.load(f)

# Build token -> grammar class mapping
token_to_class = {}
terminals = grammar.get('terminals', {}).get('list', [])
for t in terminals:
    symbol = t.get('symbol')
    role = t.get('role')
    if symbol and role:
        token_to_class[symbol] = role

# Load hazards
import sys
sys.path.insert(0, str(project_root / 'vee' / 'app' / 'core'))
try:
    from hazards import FORBIDDEN_PAIRS
    hazard_tokens = set()
    for pair in FORBIDDEN_PAIRS:
        hazard_tokens.add(pair[0])
        hazard_tokens.add(pair[1])
except ImportError:
    FORBIDDEN_PAIRS = []
    hazard_tokens = set()

# Load data by system
a_lines = defaultdict(list)  # key -> [tokens]
b_lines = defaultdict(list)
a_tokens = []
b_tokens = []

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            # Filter to H (PRIMARY) transcriber track only
            transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
            if transcriber != 'H':
                continue
            word = parts[0].strip('"').strip().lower()
            folio = parts[2].strip('"').strip()
            lang = parts[6].strip('"').strip()
            line_num = parts[11].strip('"').strip()

            if not word:
                continue

            key = f'{folio}_{line_num}'
            if lang == 'A':
                a_tokens.append(word)
                a_lines[key].append(word)
            elif lang == 'B':
                b_tokens.append(word)
                b_lines[key].append(word)

# Define test candidates - include known structural primitives + S-1 candidates
# Plus high-frequency cross-system tokens for comparison
CANDIDATES = [
    'daiin',    # SP-01 confirmed (CORE_CONTROL)
    'ol',       # Likely co-primitive (CORE_CONTROL)
    'aiin',     # S-1 Tier-1 (HIGH_IMPACT)
    'saiin',    # S-1 Tier-1 (AUXILIARY)
    'dol',      # S-1 candidate (AUXILIARY)
    'dy',       # S-1 candidate (FREQUENT_OPERATOR)
    'or',       # Expert flagged as potential
    'dar',      # High-freq cross-system (FLOW_OPERATOR)
    'dal',      # High-freq cross-system
    'chol',     # High-freq A-enriched (FLOW_OPERATOR)
    's',        # High-freq single char
]

print("=" * 70)
print("PHASE S-2: ROLE POLARITY TEST")
print("=" * 70)

# =============================================================================
# TEST 1: NEIGHBOR ANALYSIS (Content vs Grammar neighbors)
# =============================================================================
print("\n" + "=" * 70)
print("TEST 1: NEIGHBOR ANALYSIS")
print("=" * 70)
print("\nQuestion: What types of tokens neighbor each candidate in A vs B?")
print("Grammar tokens = have grammar class; Content = no grammar class\n")

def analyze_neighbors(token_list, target):
    """Analyze what neighbors a target token."""
    before = Counter()
    after = Counter()
    before_grammar = 0
    before_content = 0
    after_grammar = 0
    after_content = 0

    for i, t in enumerate(token_list):
        if t == target:
            if i > 0:
                prev = token_list[i-1]
                before[prev] += 1
                if token_to_class.get(prev):
                    before_grammar += 1
                else:
                    before_content += 1
            if i < len(token_list) - 1:
                nxt = token_list[i+1]
                after[nxt] += 1
                if token_to_class.get(nxt):
                    after_grammar += 1
                else:
                    after_content += 1

    total_before = before_grammar + before_content
    total_after = after_grammar + after_content

    return {
        'before_grammar_pct': 100 * before_grammar / total_before if total_before else 0,
        'after_grammar_pct': 100 * after_grammar / total_after if total_after else 0,
        'top_before': before.most_common(5),
        'top_after': after.most_common(5)
    }

neighbor_results = {}
for tok in CANDIDATES:
    a_neighbors = analyze_neighbors(a_tokens, tok)
    b_neighbors = analyze_neighbors(b_tokens, tok)

    # Polarity = difference in grammar neighbor percentage
    before_diff = b_neighbors['before_grammar_pct'] - a_neighbors['before_grammar_pct']
    after_diff = b_neighbors['after_grammar_pct'] - a_neighbors['after_grammar_pct']
    neighbor_polarity = (abs(before_diff) + abs(after_diff)) / 2

    neighbor_results[tok] = {
        'a_before_grammar_pct': a_neighbors['before_grammar_pct'],
        'a_after_grammar_pct': a_neighbors['after_grammar_pct'],
        'b_before_grammar_pct': b_neighbors['before_grammar_pct'],
        'b_after_grammar_pct': b_neighbors['after_grammar_pct'],
        'neighbor_polarity': neighbor_polarity,
        'a_top_before': a_neighbors['top_before'],
        'a_top_after': a_neighbors['top_after'],
        'b_top_before': b_neighbors['top_before'],
        'b_top_after': b_neighbors['top_after']
    }

print(f"{'Token':<10} {'A bef%':>8} {'A aft%':>8} {'B bef%':>8} {'B aft%':>8} {'Polarity':>10}")
print("-" * 60)
for tok in sorted(neighbor_results.keys(), key=lambda x: neighbor_results[x]['neighbor_polarity'], reverse=True):
    r = neighbor_results[tok]
    print(f"{tok:<10} {r['a_before_grammar_pct']:>7.1f}% {r['a_after_grammar_pct']:>7.1f}% "
          f"{r['b_before_grammar_pct']:>7.1f}% {r['b_after_grammar_pct']:>7.1f}% {r['neighbor_polarity']:>10.1f}")

# =============================================================================
# TEST 2: POSITIONAL ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: POSITIONAL ANALYSIS")
print("=" * 70)
print("\nQuestion: Does position-in-line differ between A and B?")

def analyze_position(lines_dict, target):
    """Analyze relative position of target token within lines."""
    positions = []
    for key, tokens in lines_dict.items():
        if len(tokens) > 1:
            for i, t in enumerate(tokens):
                if t == target:
                    rel_pos = i / (len(tokens) - 1)
                    positions.append(rel_pos)
    if not positions:
        return {'mean': 0, 'std': 0, 'count': 0}

    mean_pos = sum(positions) / len(positions)
    variance = sum((p - mean_pos) ** 2 for p in positions) / len(positions)
    std_pos = variance ** 0.5

    return {'mean': mean_pos, 'std': std_pos, 'count': len(positions)}

position_results = {}
for tok in CANDIDATES:
    a_pos = analyze_position(a_lines, tok)
    b_pos = analyze_position(b_lines, tok)

    # Polarity = difference in mean position
    pos_diff = abs(a_pos['mean'] - b_pos['mean'])
    std_diff = abs(a_pos['std'] - b_pos['std'])

    position_results[tok] = {
        'a_mean': a_pos['mean'],
        'a_std': a_pos['std'],
        'a_count': a_pos['count'],
        'b_mean': b_pos['mean'],
        'b_std': b_pos['std'],
        'b_count': b_pos['count'],
        'position_polarity': pos_diff
    }

print(f"\n{'Token':<10} {'A mean':>8} {'A std':>8} {'A n':>6} {'B mean':>8} {'B std':>8} {'B n':>6} {'Polarity':>10}")
print("-" * 75)
for tok in sorted(position_results.keys(), key=lambda x: position_results[x]['position_polarity'], reverse=True):
    r = position_results[tok]
    print(f"{tok:<10} {r['a_mean']:>8.3f} {r['a_std']:>8.3f} {r['a_count']:>6} "
          f"{r['b_mean']:>8.3f} {r['b_std']:>8.3f} {r['b_count']:>6} {r['position_polarity']:>10.3f}")

# =============================================================================
# TEST 3: PAIRING ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: PAIRING ANALYSIS")
print("=" * 70)
print("\nQuestion: Does the token have tight pairing partners in one system but not the other?")

def analyze_pairing(token_list, target, top_n=5):
    """Analyze how concentrated bigram partners are."""
    partners = Counter()
    for i in range(len(token_list) - 1):
        if token_list[i] == target:
            partners[token_list[i+1]] += 1
        if token_list[i+1] == target:
            partners[token_list[i]] += 1

    total = sum(partners.values())
    if total == 0:
        return {'concentration': 0, 'top_partners': []}

    # Concentration = what % of pairings are with top N partners
    top_count = sum(c for _, c in partners.most_common(top_n))
    concentration = top_count / total

    return {
        'concentration': concentration,
        'top_partners': partners.most_common(top_n),
        'total': total
    }

pairing_results = {}
for tok in CANDIDATES:
    a_pair = analyze_pairing(a_tokens, tok)
    b_pair = analyze_pairing(b_tokens, tok)

    # Polarity = difference in concentration
    pair_polarity = abs(a_pair['concentration'] - b_pair['concentration'])

    pairing_results[tok] = {
        'a_concentration': a_pair['concentration'],
        'b_concentration': b_pair['concentration'],
        'pairing_polarity': pair_polarity,
        'a_top': a_pair['top_partners'],
        'b_top': b_pair['top_partners']
    }

print(f"\n{'Token':<10} {'A conc':>10} {'B conc':>10} {'Polarity':>10}")
print("-" * 45)
for tok in sorted(pairing_results.keys(), key=lambda x: pairing_results[x]['pairing_polarity'], reverse=True):
    r = pairing_results[tok]
    print(f"{tok:<10} {r['a_concentration']:>10.3f} {r['b_concentration']:>10.3f} {r['pairing_polarity']:>10.3f}")

# =============================================================================
# TEST 4: HAZARD PROXIMITY (B only)
# =============================================================================
print("\n" + "=" * 70)
print("TEST 4: HAZARD PROXIMITY (B only)")
print("=" * 70)
print("\nQuestion: How close does each token appear to hazard tokens in B?")

def analyze_hazard_proximity(token_list, target, hazard_set, window=3):
    """Count how often target appears within window of hazard tokens."""
    near_hazard = 0
    total = 0

    for i, t in enumerate(token_list):
        if t == target:
            total += 1
            # Check window around position
            start = max(0, i - window)
            end = min(len(token_list), i + window + 1)
            for j in range(start, end):
                if j != i and token_list[j] in hazard_set:
                    near_hazard += 1
                    break

    return {
        'near_hazard_pct': 100 * near_hazard / total if total else 0,
        'total': total
    }

hazard_results = {}
for tok in CANDIDATES:
    b_hazard = analyze_hazard_proximity(b_tokens, tok, hazard_tokens)
    hazard_results[tok] = b_hazard

print(f"\n{'Token':<10} {'Near Hazard %':>15} {'Total in B':>12}")
print("-" * 40)
for tok in sorted(hazard_results.keys(), key=lambda x: hazard_results[x]['near_hazard_pct'], reverse=True):
    r = hazard_results[tok]
    print(f"{tok:<10} {r['near_hazard_pct']:>14.1f}% {r['total']:>12}")

# =============================================================================
# COMPOSITE POLARITY SCORE
# =============================================================================
print("\n" + "=" * 70)
print("COMPOSITE POLARITY SCORE")
print("=" * 70)
print("\nCombining all polarity measures (higher = more structural primitive-like)")

composite_scores = {}
for tok in CANDIDATES:
    # Normalize each polarity to 0-1 scale
    neighbor_p = neighbor_results[tok]['neighbor_polarity'] / 50  # Max ~50
    position_p = position_results[tok]['position_polarity'] / 0.5  # Max ~0.5
    pairing_p = pairing_results[tok]['pairing_polarity']  # Already 0-1

    # Grammar class bonus
    gc = token_to_class.get(tok)
    grammar_bonus = 0.2 if gc else 0

    # CORE_CONTROL gets extra bonus (known structural)
    if gc == 'CORE_CONTROL':
        grammar_bonus = 0.4

    composite = (neighbor_p + position_p + pairing_p) / 3 + grammar_bonus

    composite_scores[tok] = {
        'neighbor_p': neighbor_p,
        'position_p': position_p,
        'pairing_p': pairing_p,
        'grammar_bonus': grammar_bonus,
        'composite': composite,
        'grammar_class': gc or '-'
    }

print(f"\n{'Token':<10} {'Neighbor':>10} {'Position':>10} {'Pairing':>10} {'Bonus':>8} {'TOTAL':>10} {'Class':<20}")
print("-" * 90)
for tok in sorted(composite_scores.keys(), key=lambda x: composite_scores[x]['composite'], reverse=True):
    r = composite_scores[tok]
    print(f"{tok:<10} {r['neighbor_p']:>10.3f} {r['position_p']:>10.3f} {r['pairing_p']:>10.3f} "
          f"{r['grammar_bonus']:>8.2f} {r['composite']:>10.3f} {r['grammar_class']:<20}")

# =============================================================================
# STRUCTURAL PRIMITIVE CLASSIFICATION
# =============================================================================
print("\n" + "=" * 70)
print("STRUCTURAL PRIMITIVE CLASSIFICATION")
print("=" * 70)

# Threshold for structural primitive
SP_THRESHOLD = 0.5

sp_candidates = [(tok, composite_scores[tok]['composite'])
                 for tok in CANDIDATES
                 if composite_scores[tok]['composite'] >= SP_THRESHOLD]

sp_candidates.sort(key=lambda x: x[1], reverse=True)

print(f"\nTokens meeting SP threshold ({SP_THRESHOLD}):")
for tok, score in sp_candidates:
    gc = token_to_class.get(tok, '-')
    a_ct = Counter(a_tokens)[tok]
    b_ct = Counter(b_tokens)[tok]
    ratio = a_ct / b_ct if b_ct > 0 else float('inf')
    affinity = "A-enriched" if ratio > 1.2 else ("B-enriched" if ratio < 0.8 else "Balanced")
    print(f"\n  SP: {tok}")
    print(f"    Composite score: {score:.3f}")
    print(f"    Grammar class: {gc}")
    print(f"    System affinity: {affinity} (A:B = {ratio:.2f})")
    print(f"    Top A neighbors: {neighbor_results[tok]['a_top_before'][:3]} -> {tok} -> {neighbor_results[tok]['a_top_after'][:3]}")
    print(f"    Top B neighbors: {neighbor_results[tok]['b_top_before'][:3]} -> {tok} -> {neighbor_results[tok]['b_top_after'][:3]}")

# =============================================================================
# SAVE RESULTS
# =============================================================================
results = {
    'candidates': CANDIDATES,
    'neighbor_results': neighbor_results,
    'position_results': position_results,
    'pairing_results': pairing_results,
    'hazard_results': hazard_results,
    'composite_scores': composite_scores,
    'sp_threshold': SP_THRESHOLD,
    'sp_candidates': [tok for tok, _ in sp_candidates]
}

output_path = Path(__file__).parent / 'sp_phase2_results.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n\nResults saved to {output_path}")
