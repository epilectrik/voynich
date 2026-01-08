"""
Grammar Reduction Test (SHOT 1)

Question: Is 49 instruction classes the true minimum, or can some be merged
without loss of predictive power?

Success Criteria:
- If classes can be merged -> Tier 2 finding: "deliberate redundancy for ergonomics"
- If 49 is truly minimal -> closure: "grammar is already maximally compressed"

Phase SITD - Shot in the Dark Exploratory Tests
"""

import json
import math
from collections import defaultdict, Counter
from itertools import combinations

# Load the 49-class grammar
def load_grammar():
    """Load 49 instruction classes from Phase 20A output."""
    with open(r'C:\git\voynich\phases\01-09_early_hypothesis\phase20a_operator_equivalence.json', 'r') as f:
        data = json.load(f)
    return data['classes']

def load_currier_b_tokens():
    """Load Currier B token sequences."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    lines = defaultdict(list)
    seen = set()

    with open(filepath, 'r', encoding='latin-1') as f:
        header = None
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split('\t')
            parts = [p.strip('"') for p in parts]

            if header is None:
                header = parts
                continue

            if len(parts) < 14:
                continue

            token = parts[0]
            folio = parts[2]
            currier = parts[6]
            transcriber = parts[12]
            line_num = parts[11]

            if currier == 'B' and transcriber == 'H' and token and '*' not in token:
                key = (folio, line_num, len(lines[(folio, line_num)]))
                if key not in seen:
                    seen.add(key)
                    lines[(folio, line_num)].append(token)

    return lines

def build_token_to_class_map(classes):
    """Map each token to its class ID."""
    token_to_class = {}
    class_to_tokens = {}

    for cls in classes:
        class_id = cls['class_id']
        members = cls['members']
        class_to_tokens[class_id] = set(members)
        for token in members:
            if token:  # Skip empty strings
                token_to_class[token] = class_id

    return token_to_class, class_to_tokens

def build_class_transition_matrix(lines, token_to_class):
    """Build transition matrix at class level."""
    transitions = defaultdict(Counter)

    for (folio, line_num), tokens in lines.items():
        for i in range(len(tokens) - 1):
            t1, t2 = tokens[i], tokens[i+1]
            c1 = token_to_class.get(t1)
            c2 = token_to_class.get(t2)
            if c1 and c2:
                transitions[c1][c2] += 1

    return transitions

def compute_transition_entropy(transitions, class_ids):
    """Compute entropy of transition distribution."""
    total = 0
    entropy = 0

    for c1 in class_ids:
        row_total = sum(transitions[c1].values())
        if row_total > 0:
            for c2, count in transitions[c1].items():
                p = count / row_total
                if p > 0:
                    entropy -= p * math.log2(p) * row_total
                    total += row_total

    return entropy / total if total > 0 else 0

def compute_class_similarity(c1, c2, transitions, classes_dict):
    """Compute similarity between two classes based on transition patterns."""
    # Get transition profiles
    c1_out = transitions[c1]
    c2_out = transitions[c2]

    # Jaccard on outgoing transitions
    c1_targets = set(c1_out.keys())
    c2_targets = set(c2_out.keys())

    if not c1_targets and not c2_targets:
        jaccard_out = 1.0
    else:
        jaccard_out = len(c1_targets & c2_targets) / len(c1_targets | c2_targets) if (c1_targets | c2_targets) else 0

    # Jaccard on incoming transitions (who transitions TO these classes)
    c1_sources = set()
    c2_sources = set()
    for src, targets in transitions.items():
        if c1 in targets:
            c1_sources.add(src)
        if c2 in targets:
            c2_sources.add(src)

    if not c1_sources and not c2_sources:
        jaccard_in = 1.0
    else:
        jaccard_in = len(c1_sources & c2_sources) / len(c1_sources | c2_sources) if (c1_sources | c2_sources) else 0

    # Compare behavioral signatures
    b1 = classes_dict[c1]['behavioral_signature']
    b2 = classes_dict[c2]['behavioral_signature']

    sig_diff = 0
    for key in b1:
        sig_diff += abs(b1[key] - b2[key])
    sig_similarity = 1 / (1 + sig_diff)

    # Same functional role bonus
    role_match = 1.0 if classes_dict[c1]['functional_role'] == classes_dict[c2]['functional_role'] else 0.0

    # Combined similarity
    return 0.3 * jaccard_out + 0.3 * jaccard_in + 0.2 * sig_similarity + 0.2 * role_match

def check_forbidden_violations(merged_classes, original_forbidden):
    """Check if merging creates new forbidden transition violations.

    Original forbidden transitions are at token level.
    We need to ensure merging doesn't create class-level ambiguity that
    would allow formerly forbidden transitions.
    """
    # For now, return 0 - we'll check this more carefully if promising candidates emerge
    return 0

def attempt_class_merge(c1, c2, transitions, classes_dict, class_to_tokens):
    """Simulate merging two classes and measure impact."""
    # Compute entropy before merge
    all_classes = list(classes_dict.keys())
    entropy_before = compute_transition_entropy(transitions, all_classes)

    # Simulate merged transitions
    merged_transitions = defaultdict(Counter)
    new_class_id = f"{c1}+{c2}"

    # Mapping: old class -> new class
    class_map = {c: c for c in all_classes}
    class_map[c1] = new_class_id
    class_map[c2] = new_class_id

    # Rebuild transition matrix with merge
    for src, targets in transitions.items():
        new_src = class_map[src]
        for tgt, count in targets.items():
            new_tgt = class_map[tgt]
            merged_transitions[new_src][new_tgt] += count

    # Compute entropy after merge
    new_classes = [c for c in all_classes if c not in [c1, c2]] + [new_class_id]
    entropy_after = compute_transition_entropy(merged_transitions, new_classes)

    entropy_change = entropy_after - entropy_before

    return {
        'c1': c1,
        'c2': c2,
        'entropy_before': entropy_before,
        'entropy_after': entropy_after,
        'entropy_change': entropy_change,
        'entropy_change_pct': 100 * entropy_change / entropy_before if entropy_before > 0 else 0
    }

def main():
    print("=" * 70)
    print("GRAMMAR REDUCTION TEST (SHOT 1)")
    print("=" * 70)
    print("\nQuestion: Is 49 instruction classes the true minimum?")
    print("Success: If classes can merge without structural loss -> ergonomic redundancy\n")

    # Load data
    print("Loading data...")
    classes = load_grammar()
    lines = load_currier_b_tokens()

    token_to_class, class_to_tokens = build_token_to_class_map(classes)
    classes_dict = {c['class_id']: c for c in classes}

    print(f"  Classes: {len(classes)}")
    print(f"  B lines: {len(lines)}")
    print(f"  Tokens mapped: {len(token_to_class)}")

    # Build transition matrix
    print("\nBuilding class transition matrix...")
    transitions = build_class_transition_matrix(lines, token_to_class)

    active_classes = set(transitions.keys())
    for targets in transitions.values():
        active_classes.update(targets.keys())
    print(f"  Active classes in B: {len(active_classes)}")

    # Compute baseline entropy
    all_class_ids = list(classes_dict.keys())
    baseline_entropy = compute_transition_entropy(transitions, all_class_ids)
    print(f"  Baseline transition entropy: {baseline_entropy:.4f} bits")

    # === TEST 1: Pairwise class similarity ===
    print("\n" + "-" * 70)
    print("TEST 1: Pairwise Class Similarity")
    print("-" * 70)

    similarities = []
    for c1, c2 in combinations(classes_dict.keys(), 2):
        sim = compute_class_similarity(c1, c2, transitions, classes_dict)
        similarities.append((c1, c2, sim))

    similarities.sort(key=lambda x: -x[2])

    print("\n--- Top 20 most similar class pairs ---")
    print(f"{'C1':>4} {'C2':>4} {'Sim':>6}  {'Role1':<20} {'Role2':<20}")
    print("-" * 70)

    for c1, c2, sim in similarities[:20]:
        role1 = classes_dict[c1]['functional_role']
        role2 = classes_dict[c2]['functional_role']
        print(f"{c1:>4} {c2:>4} {sim:>6.3f}  {role1:<20} {role2:<20}")

    # === TEST 2: Merge impact for high-similarity pairs ===
    print("\n" + "-" * 70)
    print("TEST 2: Entropy Impact of Merging Top Candidates")
    print("-" * 70)

    merge_results = []
    for c1, c2, sim in similarities[:30]:  # Test top 30 candidates
        result = attempt_class_merge(c1, c2, transitions, classes_dict, class_to_tokens)
        result['similarity'] = sim
        merge_results.append(result)

    # Sort by entropy change (smallest = most mergeable)
    merge_results.sort(key=lambda x: x['entropy_change'])

    print("\n--- Merge candidates by entropy impact ---")
    print(f"{'C1':>4} {'C2':>4} {'Sim':>6} {'dH':>8} {'dH%':>7}")
    print("-" * 40)

    mergeable_count = 0
    for r in merge_results[:20]:
        delta = r['entropy_change']
        delta_pct = r['entropy_change_pct']
        status = "OK" if delta_pct < 1.0 else ""
        if delta_pct < 1.0:
            mergeable_count += 1
        print(f"{r['c1']:>4} {r['c2']:>4} {r['similarity']:>6.3f} {delta:>8.4f} {delta_pct:>6.2f}% {status}")

    # === TEST 3: Same-role mergeability ===
    print("\n" + "-" * 70)
    print("TEST 3: Within-Role Mergeability")
    print("-" * 70)

    # Group classes by role
    role_groups = defaultdict(list)
    for c in classes:
        role_groups[c['functional_role']].append(c['class_id'])

    print("\nClasses per role:")
    for role, cids in sorted(role_groups.items()):
        print(f"  {role}: {len(cids)} classes")

    # For each role, find most similar pairs
    print("\n--- Most similar pairs within each role ---")
    for role, cids in sorted(role_groups.items()):
        if len(cids) < 2:
            continue

        role_sims = []
        for c1, c2 in combinations(cids, 2):
            sim = compute_class_similarity(c1, c2, transitions, classes_dict)
            role_sims.append((c1, c2, sim))

        role_sims.sort(key=lambda x: -x[2])

        if role_sims:
            top = role_sims[0]
            result = attempt_class_merge(top[0], top[1], transitions, classes_dict, class_to_tokens)
            print(f"  {role}: classes {top[0]}+{top[1]}, sim={top[2]:.3f}, dH={result['entropy_change_pct']:.2f}%")

    # === TEST 4: Greedy reduction attempt ===
    print("\n" + "-" * 70)
    print("TEST 4: Greedy Reduction (iterative merging)")
    print("-" * 70)
    print("\nAttempting iterative merging with <1% entropy threshold...")

    current_transitions = dict(transitions)
    current_classes = dict(classes_dict)
    merges_made = []

    while True:
        # Find best mergeable pair
        best_merge = None
        best_delta = float('inf')

        class_ids = list(current_classes.keys())
        for c1, c2 in combinations(class_ids, 2):
            # Same role constraint
            if current_classes[c1]['functional_role'] != current_classes[c2]['functional_role']:
                continue

            result = attempt_class_merge(c1, c2, current_transitions, current_classes, class_to_tokens)
            if result['entropy_change_pct'] < 1.0 and result['entropy_change'] < best_delta:
                best_merge = (c1, c2)
                best_delta = result['entropy_change']

        if best_merge is None:
            break

        c1, c2 = best_merge
        merges_made.append(best_merge)
        print(f"  Merged: {c1} + {c2} (dH={best_delta:.4f})")

        # Actually perform the merge
        new_id = f"{c1}+{c2}"

        # Merge class info
        merged_class = {
            'class_id': new_id,
            'members': current_classes[c1]['members'] + current_classes[c2]['members'],
            'functional_role': current_classes[c1]['functional_role'],
            'behavioral_signature': current_classes[c1]['behavioral_signature']  # Simplified
        }

        del current_classes[c1]
        del current_classes[c2]
        current_classes[new_id] = merged_class

        # Merge transitions
        new_transitions = defaultdict(Counter)
        for src, targets in current_transitions.items():
            new_src = new_id if src in [c1, c2] else src
            for tgt, count in targets.items():
                new_tgt = new_id if tgt in [c1, c2] else tgt
                new_transitions[new_src][new_tgt] += count
        current_transitions = dict(new_transitions)

    print(f"\nTotal merges made: {len(merges_made)}")
    print(f"Reduced from 49 to {len(current_classes)} classes")

    # === SUMMARY ===
    print("\n" + "=" * 70)
    print("SUMMARY: Grammar Reduction Test")
    print("=" * 70)

    reduction = 49 - len(current_classes)
    reduction_pct = 100 * reduction / 49

    print(f"""
    Original classes:     49
    Reducible classes:    {reduction}
    Minimal classes:      {len(current_classes)}
    Reduction:            {reduction_pct:.1f}%

    Merges performed (same-role, <1% entropy increase):
    """)

    for c1, c2 in merges_made:
        print(f"      {c1} + {c2}")

    if reduction_pct > 10:
        print(f"""
    FINDING: Grammar has {reduction_pct:.0f}% REDUCIBLE REDUNDANCY

    This suggests DELIBERATE REDUNDANCY for human ergonomics:
    - Multiple similar classes distinguished for readability
    - Operators could use fewer classes but chose not to
    - Vocabulary diversity serves human factors, not machine efficiency

    STATUS: POTENTIAL TIER 2 FINDING
    """)
    else:
        print(f"""
    FINDING: Grammar is NEAR-MINIMAL

    Only {reduction_pct:.1f}% reduction possible with <1% entropy cost.
    49 classes represent the effective minimum for this system.

    STATUS: CLOSURE (grammar already maximally compressed)
    """)

if __name__ == '__main__':
    main()
