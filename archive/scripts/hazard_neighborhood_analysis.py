"""
HAZARD-NEIGHBORHOOD MICROSTRUCTURE ANALYSIS

Questions:
1. What tokens appear 1-2 steps BEFORE hazard-adjacent positions?
2. What tokens appear 1-2 steps AFTER recovery?
3. What is the mean/variance of recovery path lengths per hazard class?
4. Is hazard handling stereotyped or flexible?
5. Is it family-specific or universal?

This probes the "error recovery grammar" - one of the last under-specified pieces.

Now working at TOKEN LEVEL using actual 17 forbidden transitions from Phase 18.
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import chi2_contingency, kruskal

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
GRAMMAR = BASE / "results" / "canonical_grammar.json"
SIGNATURES = BASE / "results" / "control_signatures.json"

def load_forbidden_transitions():
    """Load the 17 forbidden token-level transitions from canonical grammar."""
    with open(GRAMMAR, 'r', encoding='utf-8') as f:
        data = json.load(f)

    forbidden = set()
    constraints = data.get('constraints', {})
    samples = constraints.get('sample', [])

    for item in samples:
        if item.get('type') == 'FORBIDDEN':
            pattern = item.get('pattern', '')
            # Pattern format: "token1 -> token2"
            parts = pattern.split(' -> ')
            if len(parts) == 2:
                forbidden.add((parts[0].strip(), parts[1].strip()))

    return forbidden

def load_grammar():
    """Load token -> role mapping."""
    with open(GRAMMAR, 'r', encoding='utf-8') as f:
        data = json.load(f)

    token_to_role = {}
    terminals = data.get('terminals', {}).get('list', [])
    for term in terminals:
        token_to_role[term['symbol']] = term['role']

    return token_to_role

def load_sequences():
    """Load Currier B token sequences by folio."""
    sequences = defaultdict(list)

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            if row.get('language') != 'B':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']
            sequences[folio].append(token)

    return sequences

def load_signatures():
    """Load folio control signatures for family classification."""
    with open(SIGNATURES, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('signatures', {})

def classify_families(signatures):
    """Classify folios into intensity families."""
    families = {}

    link_densities = [s['link_density'] for s in signatures.values()]
    hazard_densities = [s['hazard_density'] for s in signatures.values()]
    kernel_ratios = [s['kernel_contact_ratio'] for s in signatures.values()]

    link_median = np.median(link_densities)
    hazard_median = np.median(hazard_densities)
    kernel_median = np.median(kernel_ratios)

    for folio, sig in signatures.items():
        score = 0
        if sig['link_density'] < link_median:
            score += 1
        if sig['hazard_density'] > hazard_median:
            score += 1
        if sig['kernel_contact_ratio'] > kernel_median:
            score += 1

        if score >= 2:
            families[folio] = 'AGGRESSIVE'
        elif score <= 0:
            families[folio] = 'CONSERVATIVE'
        else:
            families[folio] = 'MODERATE'

    return families

def find_suppressed_transitions(sequences, forbidden):
    """
    Find additionally suppressed transitions (beyond the 17 forbidden).
    These are transitions that occur much less frequently than expected.
    """
    # Count all bigram transitions
    transition_counts = Counter()
    token_counts = Counter()
    total_transitions = 0

    for folio, tokens in sequences.items():
        for token in tokens:
            token_counts[token] += 1
        for i in range(len(tokens) - 1):
            transition_counts[(tokens[i], tokens[i+1])] += 1
            total_transitions += 1

    total_tokens = sum(token_counts.values())

    # Find suppressed (< 0.3x expected, with expected > 3)
    suppressed = set()
    for (t1, t2), count in transition_counts.items():
        expected = (token_counts[t1] / total_tokens) * (token_counts[t2] / total_tokens) * total_transitions
        if expected > 3 and count / expected < 0.3:
            suppressed.add((t1, t2))

    # Add forbidden (zero-count)
    suppressed.update(forbidden)

    return suppressed, transition_counts, token_counts

def find_hazard_adjacent_positions(sequences, forbidden, suppressed):
    """
    Find all positions that are 1-2 steps before or after a forbidden/suppressed transition.

    Returns:
    - pre_positions: list of (folio, idx, token, distance_to_hazard)
    - post_positions: list of (folio, idx, token, distance_from_hazard)
    """
    pre_positions = []
    post_positions = []

    hazard_set = forbidden | suppressed

    for folio, tokens in sequences.items():
        for i in range(len(tokens) - 1):
            t1, t2 = tokens[i], tokens[i+1]

            if (t1, t2) in hazard_set:
                # This IS a hazard transition
                # Record positions before
                if i >= 1:
                    pre_positions.append((folio, i-1, tokens[i-1], 1))
                if i >= 2:
                    pre_positions.append((folio, i-2, tokens[i-2], 2))

                # Record positions after
                if i + 2 < len(tokens):
                    post_positions.append((folio, i+2, tokens[i+2], 1))
                if i + 3 < len(tokens):
                    post_positions.append((folio, i+3, tokens[i+3], 2))

    return pre_positions, post_positions

def analyze_pre_hazard_context(pre_positions, token_counts, token_to_role):
    """Analyze tokens appearing before hazard transitions."""
    print("="*70)
    print("PRE-HAZARD CONTEXT ANALYSIS")
    print("="*70)

    pre_1 = Counter()  # 1 step before
    pre_2 = Counter()  # 2 steps before

    for (folio, idx, token, distance) in pre_positions:
        if distance == 1:
            pre_1[token] += 1
        else:
            pre_2[token] += 1

    total_1 = sum(pre_1.values())
    total_2 = sum(pre_2.values())
    total_baseline = sum(token_counts.values())

    print(f"\nPositions 1 step before hazard: {total_1}")
    print(f"Positions 2 steps before hazard: {total_2}")

    if total_1 > 20:
        print("\n" + "-"*70)
        print("TOKEN ENRICHMENT 1 STEP BEFORE HAZARD (top 15)")
        print("-"*70)

        print(f"\n{'Token':<15} {'Role':<18} {'Baseline':>10} {'Pre-Haz':>10} {'Ratio':>10}")
        print("-" * 68)

        # Calculate enrichment
        enrichments = []
        for token, count in pre_1.most_common(50):
            base_pct = token_counts.get(token, 0) / total_baseline
            pre_pct = count / total_1
            ratio = pre_pct / base_pct if base_pct > 0 else float('inf')
            role = token_to_role.get(token, 'UNK')
            enrichments.append((token, role, base_pct, pre_pct, ratio))

        # Sort by ratio
        enrichments.sort(key=lambda x: -x[4])
        for token, role, base_pct, pre_pct, ratio in enrichments[:15]:
            sig = ""
            if ratio > 2.0:
                sig = " +++ STRONG"
            elif ratio > 1.5:
                sig = " ++ ENRICHED"
            elif ratio < 0.5:
                sig = " -- DEPLETED"
            print(f"{token:<15} {role:<18} {base_pct:>9.2%} {pre_pct:>9.2%} {ratio:>9.2f}x{sig}")

    # Aggregate by role
    print("\n" + "-"*70)
    print("ROLE-LEVEL ENRICHMENT BEFORE HAZARD")
    print("-"*70)

    role_pre_1 = Counter()
    role_baseline = Counter()

    for token, count in pre_1.items():
        role = token_to_role.get(token)
        if role:
            role_pre_1[role] += count

    for token, count in token_counts.items():
        role = token_to_role.get(token)
        if role:
            role_baseline[role] += count

    total_role_baseline = sum(role_baseline.values())
    total_role_pre = sum(role_pre_1.values())

    print(f"\n{'Role':<20} {'Baseline':>10} {'Pre-Haz':>10} {'Ratio':>10}")
    print("-" * 55)

    for role in sorted(role_baseline.keys()):
        base_pct = role_baseline[role] / total_role_baseline
        pre_pct = role_pre_1.get(role, 0) / total_role_pre if total_role_pre > 0 else 0
        ratio = pre_pct / base_pct if base_pct > 0 else 0

        sig = ""
        if ratio > 1.5:
            sig = " ++ ENRICHED"
        elif ratio < 0.5:
            sig = " -- DEPLETED"

        print(f"{role:<20} {base_pct:>9.1%} {pre_pct:>9.1%} {ratio:>9.2f}x{sig}")

    return pre_1, pre_2

def analyze_post_hazard_recovery(post_positions, token_counts, token_to_role, sequences, forbidden, suppressed):
    """Analyze recovery patterns after hazard transitions."""
    print("\n" + "="*70)
    print("POST-HAZARD RECOVERY ANALYSIS")
    print("="*70)

    post_1 = Counter()  # 1 step after
    post_2 = Counter()  # 2 steps after

    for (folio, idx, token, distance) in post_positions:
        if distance == 1:
            post_1[token] += 1
        else:
            post_2[token] += 1

    total_1 = sum(post_1.values())
    total_2 = sum(post_2.values())
    total_baseline = sum(token_counts.values())

    print(f"\nPositions 1 step after hazard: {total_1}")
    print(f"Positions 2 steps after hazard: {total_2}")

    if total_1 > 20:
        print("\n" + "-"*70)
        print("TOKEN ENRICHMENT 1 STEP AFTER HAZARD (top 15)")
        print("-"*70)

        print(f"\n{'Token':<15} {'Role':<18} {'Baseline':>10} {'Post-Haz':>10} {'Ratio':>10}")
        print("-" * 68)

        enrichments = []
        for token, count in post_1.most_common(50):
            base_pct = token_counts.get(token, 0) / total_baseline
            post_pct = count / total_1
            ratio = post_pct / base_pct if base_pct > 0 else float('inf')
            role = token_to_role.get(token, 'UNK')
            enrichments.append((token, role, base_pct, post_pct, ratio))

        enrichments.sort(key=lambda x: -x[4])
        for token, role, base_pct, post_pct, ratio in enrichments[:15]:
            sig = ""
            if ratio > 2.0:
                sig = " +++ STRONG"
            elif ratio > 1.5:
                sig = " ++ ENRICHED"
            elif ratio < 0.5:
                sig = " -- DEPLETED"
            print(f"{token:<15} {role:<18} {base_pct:>9.2%} {post_pct:>9.2%} {ratio:>9.2f}x{sig}")

    # Role-level analysis
    print("\n" + "-"*70)
    print("ROLE-LEVEL ENRICHMENT AFTER HAZARD")
    print("-"*70)

    role_post_1 = Counter()
    role_baseline = Counter()

    for token, count in post_1.items():
        role = token_to_role.get(token)
        if role:
            role_post_1[role] += count

    for token, count in token_counts.items():
        role = token_to_role.get(token)
        if role:
            role_baseline[role] += count

    total_role_baseline = sum(role_baseline.values())
    total_role_post = sum(role_post_1.values())

    print(f"\n{'Role':<20} {'Baseline':>10} {'Post-Haz':>10} {'Ratio':>10}")
    print("-" * 55)

    for role in sorted(role_baseline.keys()):
        base_pct = role_baseline[role] / total_role_baseline
        post_pct = role_post_1.get(role, 0) / total_role_post if total_role_post > 0 else 0
        ratio = post_pct / base_pct if base_pct > 0 else 0

        sig = ""
        if ratio > 1.5:
            sig = " ++ ENRICHED"
        elif ratio < 0.5:
            sig = " -- DEPLETED"

        print(f"{role:<20} {base_pct:>9.1%} {post_pct:>9.1%} {ratio:>9.2f}x{sig}")

    # Recovery path length analysis
    print("\n" + "-"*70)
    print("RECOVERY PATH LENGTHS (to ENERGY_OPERATOR)")
    print("-"*70)

    hazard_set = forbidden | suppressed
    recovery_paths = []

    for folio, tokens in sequences.items():
        for i in range(len(tokens) - 1):
            if (tokens[i], tokens[i+1]) in hazard_set:
                # Find path to stability (ENERGY_OPERATOR role)
                for j in range(i+2, min(i+12, len(tokens))):
                    role = token_to_role.get(tokens[j])
                    if role == 'ENERGY_OPERATOR':
                        recovery_paths.append(j - i - 1)
                        break

    if recovery_paths:
        print(f"\nRecovery instances found: {len(recovery_paths)}")
        print(f"Mean path length: {np.mean(recovery_paths):.2f}")
        print(f"Std path length: {np.std(recovery_paths):.2f}")
        print(f"Min: {min(recovery_paths)}, Max: {max(recovery_paths)}")

        path_dist = Counter(recovery_paths)
        print("\nPath length distribution:")
        for length in sorted(path_dist.keys())[:10]:
            pct = path_dist[length] / len(recovery_paths) * 100
            bar = "#" * int(pct / 2)
            print(f"  {length} steps: {path_dist[length]:>4} ({pct:>5.1f}%) {bar}")

    return post_1, post_2, recovery_paths

def analyze_hazard_class_patterns(sequences, forbidden, token_to_role):
    """Group hazards by the SOURCE token and analyze approach patterns."""
    print("\n" + "="*70)
    print("HAZARD CLASS PATTERNS (by source token)")
    print("="*70)

    # Group forbidden by source
    hazard_by_source = defaultdict(list)
    for (t1, t2) in forbidden:
        hazard_by_source[t1].append(t2)

    print(f"\nForbidden transitions by source token:")
    for source, targets in sorted(hazard_by_source.items(), key=lambda x: -len(x[1])):
        role = token_to_role.get(source, 'UNK')
        print(f"\n  {source} ({role}):")
        for t in targets:
            t_role = token_to_role.get(t, 'UNK')
            print(f"    -> {t} ({t_role})")

    # Analyze what comes BEFORE each hazard source
    print("\n" + "-"*70)
    print("APPROACH TOKENS BY HAZARD SOURCE")
    print("-"*70)

    for source in hazard_by_source.keys():
        approach = Counter()
        for folio, tokens in sequences.items():
            for i in range(1, len(tokens) - 1):
                if tokens[i] == source:
                    # Check if next transition is forbidden
                    if i + 1 < len(tokens) and (tokens[i], tokens[i+1]) in forbidden:
                        approach[tokens[i-1]] += 1

        if sum(approach.values()) > 5:
            total = sum(approach.values())
            role = token_to_role.get(source, 'UNK')
            print(f"\nBefore hazard source '{source}' ({role}) [{total} events]:")
            for token, count in approach.most_common(5):
                pct = count / total * 100
                t_role = token_to_role.get(token, 'UNK')
                print(f"  {token} ({t_role}): {pct:.1f}%")

def analyze_family_specific_patterns(sequences, forbidden, suppressed, families, token_to_role):
    """Check if different families handle hazards differently."""
    print("\n" + "="*70)
    print("FAMILY-SPECIFIC HAZARD HANDLING")
    print("="*70)

    hazard_set = forbidden | suppressed

    family_hazard_counts = Counter()
    family_token_counts = Counter()
    family_recovery_paths = defaultdict(list)
    family_post_hazard = defaultdict(Counter)

    for folio, tokens in sequences.items():
        if folio not in families:
            continue

        family = families[folio]
        family_token_counts[family] += len(tokens)

        for i in range(len(tokens) - 1):
            if (tokens[i], tokens[i+1]) in hazard_set:
                family_hazard_counts[family] += 1

                # Post-hazard token
                if i + 2 < len(tokens):
                    role = token_to_role.get(tokens[i+2])
                    if role:
                        family_post_hazard[family][role] += 1

                # Recovery path
                for j in range(i+2, min(i+12, len(tokens))):
                    role = token_to_role.get(tokens[j])
                    if role == 'ENERGY_OPERATOR':
                        family_recovery_paths[family].append(j - i - 1)
                        break

    print(f"\n{'Family':<15} {'Tokens':>10} {'Hazards':>10} {'Rate':>12}")
    print("-" * 50)

    for family in ['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE']:
        tokens = family_token_counts.get(family, 0)
        hazards = family_hazard_counts.get(family, 0)
        rate = hazards / tokens * 1000 if tokens > 0 else 0
        print(f"{family:<15} {tokens:>10} {hazards:>10} {rate:>10.2f}/1k")

    print("\n" + "-"*70)
    print("RECOVERY PATH LENGTH BY FAMILY")
    print("-"*70)

    print(f"\n{'Family':<15} {'N Paths':>10} {'Mean':>10} {'Std':>10}")
    print("-" * 50)

    for family in ['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE']:
        paths = family_recovery_paths.get(family, [])
        if paths:
            print(f"{family:<15} {len(paths):>10} {np.mean(paths):>10.2f} {np.std(paths):>10.2f}")
        else:
            print(f"{family:<15} {'N/A':>10}")

    # Statistical test
    groups = [family_recovery_paths[f] for f in ['CONSERVATIVE', 'AGGRESSIVE'] if family_recovery_paths.get(f)]
    if len(groups) == 2 and all(len(g) > 5 for g in groups):
        stat, p = kruskal(*groups)
        print(f"\nKruskal-Wallis (Conservative vs Aggressive): H={stat:.2f}, p={p:.4f}")
        if p < 0.05:
            print("-> SIGNIFICANT: Families recover differently!")
        else:
            print("-> NOT SIGNIFICANT: Universal recovery pattern")

    print("\n" + "-"*70)
    print("POST-HAZARD ROLE DISTRIBUTION BY FAMILY")
    print("-"*70)

    all_roles = set()
    for roles in family_post_hazard.values():
        all_roles.update(roles.keys())

    print(f"\n{'Role':<20}", end="")
    for family in ['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE']:
        print(f"{family[:12]:>14}", end="")
    print()
    print("-" * 65)

    for role in sorted(all_roles):
        print(f"{role:<20}", end="")
        for family in ['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE']:
            counts = family_post_hazard.get(family, {})
            total = sum(counts.values())
            pct = counts.get(role, 0) / total if total > 0 else 0
            print(f"{pct:>13.1%}", end="")
        print()

def analyze_stereotyped_vs_flexible(sequences, forbidden, token_to_role):
    """Determine if hazard handling is stereotyped or flexible."""
    print("\n" + "="*70)
    print("STEREOTYPED vs FLEXIBLE HAZARD HANDLING")
    print("="*70)

    # For each hazard source, collect the distribution of approach tokens
    hazard_approach_entropy = {}

    for source_token, _ in forbidden:
        approach = Counter()
        for folio, tokens in sequences.items():
            for i in range(1, len(tokens) - 1):
                if tokens[i] == source_token:
                    if i + 1 < len(tokens) and (tokens[i], tokens[i+1]) in forbidden:
                        approach[tokens[i-1]] += 1

        total = sum(approach.values())
        if total > 10:
            # Calculate entropy
            probs = [c/total for c in approach.values()]
            entropy = -sum(p * np.log2(p) for p in probs if p > 0)
            max_entropy = np.log2(len(approach)) if len(approach) > 1 else 1
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

            hazard_approach_entropy[source_token] = {
                'entropy': normalized_entropy,
                'unique_approaches': len(approach),
                'total': total,
                'top_approach': approach.most_common(1)[0] if approach else None
            }

    if hazard_approach_entropy:
        print(f"\n{'Source Token':<15} {'Entropy':>10} {'Unique':>10} {'N':>8} {'Top Approach':<20}")
        print("-" * 70)

        for token, stats in sorted(hazard_approach_entropy.items(), key=lambda x: x[1]['entropy']):
            top = stats['top_approach']
            top_str = f"{top[0]} ({top[1]})" if top else "N/A"
            print(f"{token:<15} {stats['entropy']:>10.3f} {stats['unique_approaches']:>10} {stats['total']:>8} {top_str:<20}")

        mean_entropy = np.mean([s['entropy'] for s in hazard_approach_entropy.values()])
        print(f"\nMean normalized entropy: {mean_entropy:.3f}")

        if mean_entropy < 0.5:
            print("-> STEREOTYPED: Hazards are approached via predictable paths")
        elif mean_entropy > 0.8:
            print("-> FLEXIBLE: Many different paths lead to hazard-adjacent positions")
        else:
            print("-> MIXED: Some hazards stereotyped, others flexible")

def summarize():
    """Final summary."""
    print("\n" + "="*70)
    print("SUMMARY: HAZARD-NEIGHBORHOOD MICROSTRUCTURE")
    print("="*70)

    print("""
Key questions answered:

1. PRE-HAZARD CONTEXT:
   - Which tokens/roles typically precede hazard transitions?
   - Are there "warning" tokens that signal approaching danger?

2. POST-HAZARD RECOVERY:
   - Which tokens/roles appear immediately after hazards?
   - How many steps to reach stability (ENERGY_OPERATOR)?

3. HAZARD CLASS PATTERNS:
   - Do different hazard sources have different approach signatures?
   - Are forbidden transitions from the same source handled similarly?

4. FAMILY SPECIFICITY:
   - Do aggressive/conservative programs recover differently?
   - Universal vs family-specific error handling?

5. STEREOTYPED vs FLEXIBLE:
   - Is hazard approach predictable (low entropy) or variable (high entropy)?
   - Does the grammar have "error avoidance routines"?
""")

def main():
    # Load data
    forbidden = load_forbidden_transitions()
    token_to_role = load_grammar()
    sequences = load_sequences()
    signatures = load_signatures()
    families = classify_families(signatures)

    print(f"Loaded {len(forbidden)} forbidden transitions")
    print(f"Loaded {len(token_to_role)} token-role mappings")
    print(f"Loaded {len(sequences)} Currier B folios")
    print(f"Classified {len(families)} folios into families")

    # Find additional suppressed transitions
    suppressed, transition_counts, token_counts = find_suppressed_transitions(sequences, forbidden)
    suppressed_only = suppressed - forbidden

    print(f"\nIdentified {len(suppressed_only)} additional suppressed transitions")
    print(f"Total hazard transitions: {len(suppressed)}")

    # Find hazard-adjacent positions
    pre_positions, post_positions = find_hazard_adjacent_positions(sequences, forbidden, suppressed)
    print(f"\nFound {len(pre_positions)} pre-hazard positions")
    print(f"Found {len(post_positions)} post-hazard positions")

    # Run analyses
    analyze_pre_hazard_context(pre_positions, token_counts, token_to_role)
    analyze_post_hazard_recovery(post_positions, token_counts, token_to_role, sequences, forbidden, suppressed)
    analyze_hazard_class_patterns(sequences, forbidden, token_to_role)
    analyze_family_specific_patterns(sequences, forbidden, suppressed, families, token_to_role)
    analyze_stereotyped_vs_flexible(sequences, forbidden, token_to_role)
    summarize()

if __name__ == '__main__':
    main()
