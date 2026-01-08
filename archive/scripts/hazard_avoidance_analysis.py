"""
HAZARD AVOIDANCE ANALYSIS

Since forbidden transitions never occur, we analyze:
1. What FOLLOWS hazard SOURCE tokens (tokens that are the first element of a forbidden pair)
2. What PRECEDES hazard TARGET tokens (tokens that are the second element)
3. How does the grammar AVOID creating the forbidden pair?

This reveals the "hazard avoidance grammar" - the positive constraints that prevent errors.
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import chi2_contingency

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
GRAMMAR = BASE / "results" / "canonical_grammar.json"
SIGNATURES = BASE / "results" / "control_signatures.json"

def load_forbidden_transitions():
    """Load forbidden transitions from canonical grammar."""
    with open(GRAMMAR, 'r', encoding='utf-8') as f:
        data = json.load(f)

    forbidden = set()
    constraints = data.get('constraints', {})
    samples = constraints.get('sample', [])

    for item in samples:
        if item.get('type') == 'FORBIDDEN':
            pattern = item.get('pattern', '')
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
    """Load folio control signatures."""
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

def analyze_hazard_source_avoidance(sequences, forbidden, token_to_role):
    """Analyze what follows hazard SOURCE tokens to avoid creating forbidden pairs."""
    print("="*70)
    print("HAZARD SOURCE AVOIDANCE ANALYSIS")
    print("="*70)

    # Get unique source tokens
    source_tokens = set(t1 for t1, t2 in forbidden)
    target_by_source = defaultdict(set)
    for t1, t2 in forbidden:
        target_by_source[t1].add(t2)

    print(f"\nForbidden transition sources: {source_tokens}")

    # For each source, analyze what actually follows it
    source_followers = defaultdict(Counter)
    total_token_followers = Counter()

    for folio, tokens in sequences.items():
        for i in range(len(tokens) - 1):
            total_token_followers[tokens[i+1]] += 1

            if tokens[i] in source_tokens:
                source_followers[tokens[i]][tokens[i+1]] += 1

    total_followers = sum(total_token_followers.values())

    print("\n" + "-"*70)
    print("WHAT FOLLOWS HAZARD SOURCE TOKENS")
    print("-"*70)

    for source in sorted(source_tokens):
        followers = source_followers[source]
        total = sum(followers.values())

        if total < 10:
            continue

        forbidden_targets = target_by_source[source]

        print(f"\n{source} (forbidden targets: {forbidden_targets}):")
        print(f"  Total occurrences followed: {total}")

        # Top 10 actual followers
        for token, count in followers.most_common(10):
            pct = count / total * 100
            is_forbidden = "** SHOULD BE FORBIDDEN **" if token in forbidden_targets else ""
            base_pct = total_token_followers[token] / total_followers * 100
            ratio = pct / base_pct if base_pct > 0 else float('inf')
            role = token_to_role.get(token, 'UNK')
            print(f"    {token:<12} ({role:<15}): {count:>4} ({pct:>5.1f}%) ratio={ratio:.2f}x {is_forbidden}")

        # Role-level summary
        role_counts = Counter()
        for token, count in followers.items():
            role = token_to_role.get(token)
            if role:
                role_counts[role] += count

        if role_counts:
            print(f"\n  Role distribution after {source}:")
            role_total = sum(role_counts.values())
            for role, count in role_counts.most_common():
                pct = count / role_total * 100
                print(f"    {role:<20}: {pct:>5.1f}%")

def analyze_hazard_target_avoidance(sequences, forbidden, token_to_role):
    """Analyze what precedes hazard TARGET tokens."""
    print("\n" + "="*70)
    print("HAZARD TARGET AVOIDANCE ANALYSIS")
    print("="*70)

    # Get unique target tokens
    target_tokens = set(t2 for t1, t2 in forbidden)
    source_by_target = defaultdict(set)
    for t1, t2 in forbidden:
        source_by_target[t2].add(t1)

    print(f"\nForbidden transition targets: {target_tokens}")

    # For each target, analyze what actually precedes it
    target_preceders = defaultdict(Counter)
    total_token_preceders = Counter()

    for folio, tokens in sequences.items():
        for i in range(1, len(tokens)):
            total_token_preceders[tokens[i-1]] += 1

            if tokens[i] in target_tokens:
                target_preceders[tokens[i]][tokens[i-1]] += 1

    total_preceders = sum(total_token_preceders.values())

    print("\n" + "-"*70)
    print("WHAT PRECEDES HAZARD TARGET TOKENS")
    print("-"*70)

    for target in sorted(target_tokens):
        preceders = target_preceders[target]
        total = sum(preceders.values())

        if total < 10:
            continue

        forbidden_sources = source_by_target[target]

        print(f"\n{target} (forbidden sources: {forbidden_sources}):")
        print(f"  Total preceded occurrences: {total}")

        # Top 10 actual preceders
        for token, count in preceders.most_common(10):
            pct = count / total * 100
            is_forbidden = "** SHOULD BE FORBIDDEN **" if token in forbidden_sources else ""
            base_pct = total_token_preceders[token] / total_preceders * 100
            ratio = pct / base_pct if base_pct > 0 else float('inf')
            role = token_to_role.get(token, 'UNK')
            print(f"    {token:<12} ({role:<15}): {count:>4} ({pct:>5.1f}%) ratio={ratio:.2f}x {is_forbidden}")

        # Role-level summary
        role_counts = Counter()
        for token, count in preceders.items():
            role = token_to_role.get(token)
            if role:
                role_counts[role] += count

        if role_counts:
            print(f"\n  Role distribution before {target}:")
            role_total = sum(role_counts.values())
            for role, count in role_counts.most_common():
                pct = count / role_total * 100
                print(f"    {role:<20}: {pct:>5.1f}%")

def analyze_avoidance_mechanism(sequences, forbidden, token_to_role):
    """Analyze how the grammar avoids creating forbidden pairs."""
    print("\n" + "="*70)
    print("AVOIDANCE MECHANISM ANALYSIS")
    print("="*70)

    # For each forbidden pair (A -> B), find cases where:
    # - A appears
    # - B appears 2-3 tokens later
    # - What's in between?

    print("\nSearching for 'near-miss' patterns (source ... target with gaps)...")

    for source, target in forbidden:
        gaps = defaultdict(Counter)

        for folio, tokens in sequences.items():
            for i in range(len(tokens)):
                if tokens[i] == source:
                    # Look ahead
                    for gap in range(2, 5):  # 1, 2, 3 token gap
                        if i + gap < len(tokens) and tokens[i + gap] == target:
                            # What's in between?
                            between = tuple(tokens[i+1:i+gap])
                            gaps[gap][between] += 1

        total_gaps = sum(sum(g.values()) for g in gaps.values())
        if total_gaps > 5:
            print(f"\n{source} -> ... -> {target} ({total_gaps} near-misses)")

            for gap_size in sorted(gaps.keys()):
                print(f"\n  Gap={gap_size} tokens:")
                for pattern, count in gaps[gap_size].most_common(5):
                    pattern_str = " -> ".join(pattern)
                    roles = [token_to_role.get(t, 'UNK') for t in pattern]
                    role_str = " -> ".join(roles)
                    print(f"    {pattern_str}")
                    print(f"      ({role_str}) x{count}")

def analyze_escape_routes(sequences, forbidden, token_to_role):
    """For each hazard source, analyze which tokens 'escape' the hazard."""
    print("\n" + "="*70)
    print("ESCAPE ROUTE ANALYSIS")
    print("="*70)

    source_tokens = set(t1 for t1, t2 in forbidden)
    target_by_source = defaultdict(set)
    for t1, t2 in forbidden:
        target_by_source[t1].add(t2)

    # Get all unique tokens
    all_tokens = set()
    for tokens in sequences.values():
        all_tokens.update(tokens)

    print("\nFor each hazard source, identifying 'escape' tokens...")
    print("(Escape = tokens that frequently follow the source, avoiding the hazard)")

    for source in sorted(source_tokens):
        forbidden_targets = target_by_source[source]

        # Count what follows source
        followers = Counter()
        for folio, tokens in sequences.items():
            for i in range(len(tokens) - 1):
                if tokens[i] == source:
                    followers[tokens[i+1]] += 1

        total = sum(followers.values())
        if total < 10:
            continue

        # Escape tokens are followers that are NOT forbidden
        escapes = [(t, c) for t, c in followers.most_common() if t not in forbidden_targets]

        print(f"\n{source} (must avoid: {forbidden_targets}):")
        print(f"  Total transitions from source: {total}")

        # Group by role
        role_escapes = defaultdict(list)
        for token, count in escapes[:20]:
            role = token_to_role.get(token, 'UNK')
            role_escapes[role].append((token, count))

        # Show top escape roles
        role_totals = {role: sum(c for _, c in tokens) for role, tokens in role_escapes.items()}
        for role in sorted(role_totals.keys(), key=lambda r: -role_totals[r])[:4]:
            pct = role_totals[role] / total * 100
            print(f"\n  {role} ({pct:.1f}% of escapes):")
            for token, count in role_escapes[role][:3]:
                pct = count / total * 100
                print(f"    {token}: {count} ({pct:.1f}%)")

def summarize():
    """Final summary."""
    print("\n" + "="*70)
    print("SUMMARY: HAZARD AVOIDANCE MECHANISMS")
    print("="*70)

    print("""
Key questions answered:

1. SOURCE AVOIDANCE:
   - When a hazard source token appears, what tokens follow?
   - How does the grammar redirect away from forbidden targets?

2. TARGET AVOIDANCE:
   - What tokens precede hazard targets?
   - Which tokens never precede targets (implicit avoidance)?

3. NEAR-MISSES:
   - When source and target appear close but not adjacent...
   - What tokens appear in between?
   - These are the "buffer" or "interlock" tokens.

4. ESCAPE ROUTES:
   - Which tokens/roles serve as safe exits from hazard sources?
   - Are escape routes stereotyped or diverse?

INTERPRETATION:
- If escapes are stereotyped: grammar has explicit "safe paths"
- If escapes are diverse: hazard avoidance is distributed across many tokens
- Either way, this reveals the POSITIVE constraints (what TO do) rather
  than just the NEGATIVE constraints (what NOT to do).
""")

def main():
    forbidden = load_forbidden_transitions()
    token_to_role = load_grammar()
    sequences = load_sequences()
    signatures = load_signatures()
    families = classify_families(signatures)

    print(f"Loaded {len(forbidden)} forbidden transitions")
    print(f"Loaded {len(token_to_role)} token-role mappings")
    print(f"Loaded {len(sequences)} Currier B folios")

    print("\nForbidden transitions:")
    for t1, t2 in sorted(forbidden):
        r1 = token_to_role.get(t1, 'UNK')
        r2 = token_to_role.get(t2, 'UNK')
        print(f"  {t1} ({r1}) -> {t2} ({r2})")

    analyze_hazard_source_avoidance(sequences, forbidden, token_to_role)
    analyze_hazard_target_avoidance(sequences, forbidden, token_to_role)
    analyze_avoidance_mechanism(sequences, forbidden, token_to_role)
    analyze_escape_routes(sequences, forbidden, token_to_role)
    summarize()

if __name__ == '__main__':
    main()
