"""Phase S-3: Substitutability & Removal Tests.

For each candidate:
- Remove token from A entries: Does record structure collapse?
- Remove token from B sequences: Does execution fail?

Structural tokens will:
- Break structure when removed
- Without breaking content identity
"""
from pathlib import Path
from collections import Counter, defaultdict
import json

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
grammar_path = project_root / 'results' / 'canonical_grammar.json'

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

# Load data by system
a_lines = defaultdict(list)
b_lines = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 11:
            word = parts[0].strip('"').strip().lower()
            folio = parts[2].strip('"').strip()
            lang = parts[6].strip('"').strip()
            line_num = parts[11].strip('"').strip()

            if not word:
                continue

            key = f'{folio}_{line_num}'
            if lang == 'A':
                a_lines[key].append(word)
            elif lang == 'B':
                b_lines[key].append(word)

CANDIDATES = ['daiin', 'ol', 'aiin', 'saiin', 'dol', 'dy', 'or', 'dar', 'dal', 'chol', 's']

print("=" * 70)
print("PHASE S-3: SUBSTITUTABILITY & REMOVAL TESTS")
print("=" * 70)

# =============================================================================
# TEST A: Currier A Entry Structure Collapse
# =============================================================================
print("\n" + "=" * 70)
print("TEST A: CURRIER A - ENTRY STRUCTURE AFTER REMOVAL")
print("=" * 70)
print("\nQuestion: If we remove token X from A entries, what happens to structure?")
print("Metrics: avg length change, % entries affected, % entries becoming empty")

def analyze_a_removal(lines_dict, target):
    """Analyze effect of removing target from A entries."""
    entries_with_target = 0
    entries_becoming_empty = 0
    entries_becoming_singleton = 0
    total_length_before = 0
    total_length_after = 0
    total_entries = len(lines_dict)

    for key, tokens in lines_dict.items():
        if target in tokens:
            entries_with_target += 1
            before_len = len(tokens)
            after_len = len([t for t in tokens if t != target])
            total_length_before += before_len
            total_length_after += after_len

            if after_len == 0:
                entries_becoming_empty += 1
            elif after_len == 1:
                entries_becoming_singleton += 1

    if entries_with_target == 0:
        return {
            'pct_affected': 0,
            'pct_empty': 0,
            'pct_singleton': 0,
            'avg_length_before': 0,
            'avg_length_after': 0,
            'length_ratio': 1.0
        }

    return {
        'pct_affected': 100 * entries_with_target / total_entries,
        'pct_empty': 100 * entries_becoming_empty / entries_with_target,
        'pct_singleton': 100 * entries_becoming_singleton / entries_with_target,
        'avg_length_before': total_length_before / entries_with_target,
        'avg_length_after': total_length_after / entries_with_target,
        'length_ratio': total_length_after / total_length_before if total_length_before else 1.0
    }

a_removal_results = {}
for tok in CANDIDATES:
    result = analyze_a_removal(a_lines, tok)
    a_removal_results[tok] = result

print(f"\n{'Token':<10} {'Affected%':>10} {'Empty%':>10} {'Single%':>10} {'Before':>10} {'After':>10} {'Ratio':>10}")
print("-" * 75)
for tok in sorted(a_removal_results.keys(), key=lambda x: a_removal_results[x]['pct_affected'], reverse=True):
    r = a_removal_results[tok]
    print(f"{tok:<10} {r['pct_affected']:>9.1f}% {r['pct_empty']:>9.1f}% {r['pct_singleton']:>9.1f}% "
          f"{r['avg_length_before']:>10.2f} {r['avg_length_after']:>10.2f} {r['length_ratio']:>10.3f}")

# =============================================================================
# TEST B: Currier B Grammar Token Removal
# =============================================================================
print("\n" + "=" * 70)
print("TEST B: CURRIER B - GRAMMAR VALIDITY AFTER REMOVAL")
print("=" * 70)
print("\nQuestion: If we remove token X from B sequences, how many grammar transitions break?")

def analyze_b_removal(lines_dict, target):
    """Analyze effect of removing target from B sequences on grammar validity."""
    total_transitions_before = 0
    total_transitions_after = 0
    valid_transitions_before = 0
    valid_transitions_after = 0
    lines_affected = 0

    for key, tokens in lines_dict.items():
        if target in tokens:
            lines_affected += 1

        # Before removal
        for i in range(len(tokens) - 1):
            total_transitions_before += 1
            t1_class = token_to_class.get(tokens[i])
            t2_class = token_to_class.get(tokens[i+1])
            if t1_class and t2_class:
                valid_transitions_before += 1

        # After removal
        filtered = [t for t in tokens if t != target]
        for i in range(len(filtered) - 1):
            total_transitions_after += 1
            t1_class = token_to_class.get(filtered[i])
            t2_class = token_to_class.get(filtered[i+1])
            if t1_class and t2_class:
                valid_transitions_after += 1

    validity_before = valid_transitions_before / total_transitions_before if total_transitions_before else 0
    validity_after = valid_transitions_after / total_transitions_after if total_transitions_after else 0

    return {
        'lines_affected': lines_affected,
        'total_lines': len(lines_dict),
        'pct_affected': 100 * lines_affected / len(lines_dict),
        'validity_before': 100 * validity_before,
        'validity_after': 100 * validity_after,
        'validity_change': 100 * (validity_after - validity_before)
    }

b_removal_results = {}
for tok in CANDIDATES:
    result = analyze_b_removal(b_lines, tok)
    b_removal_results[tok] = result

print(f"\n{'Token':<10} {'Affected%':>10} {'Valid Before':>12} {'Valid After':>12} {'Change':>10}")
print("-" * 60)
for tok in sorted(b_removal_results.keys(), key=lambda x: abs(b_removal_results[x]['validity_change']), reverse=True):
    r = b_removal_results[tok]
    print(f"{tok:<10} {r['pct_affected']:>9.1f}% {r['validity_before']:>11.1f}% "
          f"{r['validity_after']:>11.1f}% {r['validity_change']:>+9.1f}%")

# =============================================================================
# TEST C: Structure Differentiation (Content vs Structure)
# =============================================================================
print("\n" + "=" * 70)
print("TEST C: STRUCTURE vs CONTENT DIFFERENTIATION")
print("=" * 70)
print("\nQuestion: Does removing the token change structure or content?")
print("Structural tokens: affect entry count, segmentation, transitions")
print("Content tokens: affect semantic density but not structure")

def compute_structural_impact(a_result, b_result):
    """Compute structural impact score."""
    # Structural impact indicators:
    # - High % affected in both systems
    # - Creates empty/singleton entries in A
    # - Changes validity in B

    a_impact = (
        a_result['pct_affected'] / 100 * 0.3 +       # Presence weight
        a_result['pct_empty'] / 100 * 0.2 +          # Structural collapse
        a_result['pct_singleton'] / 100 * 0.1 +      # Structural reduction
        (1 - a_result['length_ratio']) * 0.4         # Length reduction
    )

    b_impact = (
        b_result['pct_affected'] / 100 * 0.3 +       # Presence weight
        abs(b_result['validity_change']) / 100 * 0.7 # Grammar impact
    )

    # Cross-system impact = structural primitive indicator
    cross_system = min(a_impact, b_impact)  # Must affect both

    return {
        'a_impact': a_impact,
        'b_impact': b_impact,
        'cross_system_impact': cross_system,
        'structural_score': (a_impact + b_impact + cross_system) / 3
    }

structural_results = {}
for tok in CANDIDATES:
    impact = compute_structural_impact(a_removal_results[tok], b_removal_results[tok])
    structural_results[tok] = impact

print(f"\n{'Token':<10} {'A Impact':>10} {'B Impact':>10} {'Cross-Sys':>10} {'SCORE':>10}")
print("-" * 55)
for tok in sorted(structural_results.keys(), key=lambda x: structural_results[x]['structural_score'], reverse=True):
    r = structural_results[tok]
    print(f"{tok:<10} {r['a_impact']:>10.3f} {r['b_impact']:>10.3f} "
          f"{r['cross_system_impact']:>10.3f} {r['structural_score']:>10.3f}")

# =============================================================================
# FINAL STRUCTURAL PRIMITIVE ASSESSMENT
# =============================================================================
print("\n" + "=" * 70)
print("FINAL STRUCTURAL PRIMITIVE ASSESSMENT")
print("=" * 70)

# Load S-2 results for composite score
s2_path = Path(__file__).parent / 'sp_phase2_results.json'
s2_results = {}
if s2_path.exists():
    with open(s2_path) as f:
        s2_data = json.load(f)
        s2_results = s2_data.get('composite_scores', {})

print("\nCombined assessment (S-2 Role Polarity + S-3 Structural Impact):")
print(f"\n{'Token':<10} {'S-2 Score':>10} {'S-3 Score':>10} {'COMBINED':>10} {'Class':<20}")
print("-" * 65)

combined_scores = {}
for tok in CANDIDATES:
    s2_score = s2_results.get(tok, {}).get('composite', 0)
    s3_score = structural_results[tok]['structural_score']
    combined = (s2_score + s3_score) / 2
    gc = token_to_class.get(tok, '-')
    combined_scores[tok] = {'s2': s2_score, 's3': s3_score, 'combined': combined, 'class': gc}

for tok in sorted(combined_scores.keys(), key=lambda x: combined_scores[x]['combined'], reverse=True):
    r = combined_scores[tok]
    print(f"{tok:<10} {r['s2']:>10.3f} {r['s3']:>10.3f} {r['combined']:>10.3f} {r['class']:<20}")

# =============================================================================
# STRUCTURAL PRIMITIVE VERDICT
# =============================================================================
print("\n" + "=" * 70)
print("STRUCTURAL PRIMITIVE VERDICT")
print("=" * 70)

# Criteria for SP status:
# 1. Has grammar class (known functional role in B)
# 2. Combined score > 0.25
# 3. Present in both A and B (cross-system)

sp_confirmed = []
sp_likely = []
sp_rejected = []

for tok in CANDIDATES:
    gc = token_to_class.get(tok)
    combined = combined_scores[tok]['combined']
    a_affected = a_removal_results[tok]['pct_affected']
    b_affected = b_removal_results[tok]['pct_affected']

    if gc and combined > 0.25 and a_affected > 5 and b_affected > 5:
        if gc == 'CORE_CONTROL':
            sp_confirmed.append(tok)
        else:
            sp_likely.append(tok)
    else:
        sp_rejected.append(tok)

print(f"\n[CONFIRMED] STRUCTURAL PRIMITIVES:")
for tok in sp_confirmed:
    gc = token_to_class.get(tok, '-')
    print(f"   SP: {tok} ({gc})")

print(f"\n[LIKELY] STRUCTURAL PRIMITIVES:")
for tok in sp_likely:
    gc = token_to_class.get(tok, '-')
    print(f"   Candidate: {tok} ({gc})")

print(f"\n[REJECTED] (not structural primitives):")
for tok in sp_rejected:
    gc = token_to_class.get(tok, '-')
    reason = []
    if not gc:
        reason.append("no grammar class")
    if combined_scores[tok]['combined'] <= 0.25:
        reason.append(f"low score ({combined_scores[tok]['combined']:.3f})")
    if a_removal_results[tok]['pct_affected'] <= 5:
        reason.append("rare in A")
    if b_removal_results[tok]['pct_affected'] <= 5:
        reason.append("rare in B")
    print(f"   {tok}: {', '.join(reason)}")

# =============================================================================
# SAVE RESULTS
# =============================================================================
results = {
    'a_removal_results': a_removal_results,
    'b_removal_results': b_removal_results,
    'structural_results': structural_results,
    'combined_scores': combined_scores,
    'sp_confirmed': sp_confirmed,
    'sp_likely': sp_likely,
    'sp_rejected': sp_rejected
}

output_path = Path(__file__).parent / 'sp_phase3_results.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n\nResults saved to {output_path}")
