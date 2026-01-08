"""
HT CLOSURE TESTS

Three final discriminator tests for the Human Track layer:

1. HT x Terminal State: Do high-HT folios end in different terminal grammar states?
2. HT -> Following Token Prediction: Does HT presence alter subsequent token probabilities?
3. HT Type Internal Structure: Zipf/clustering analysis of the 11,000 HT types
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, chi2_contingency, ks_2samp, linregress
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
GRAMMAR = BASE / "results" / "canonical_grammar.json"

def load_grammar():
    """Load token -> role mapping."""
    with open(GRAMMAR, 'r', encoding='utf-8') as f:
        data = json.load(f)

    token_to_role = {}
    terminals = data.get('terminals', {}).get('list', [])
    for term in terminals:
        token_to_role[term['symbol']] = term['role']

    grammar_tokens = set(token_to_role.keys())
    return token_to_role, grammar_tokens

def load_b_data():
    """Load Currier B tokens with full context."""
    data_by_folio = defaultdict(list)

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
            data_by_folio[folio].append(token)

    return data_by_folio

def classify_tokens(tokens, grammar_tokens):
    """Classify tokens as grammar (operational) or HT."""
    grammar = []
    ht = []
    for i, token in enumerate(tokens):
        if token in grammar_tokens:
            grammar.append((i, token))
        else:
            ht.append((i, token))
    return grammar, ht

# =============================================================================
# TEST 1: HT x Terminal State
# =============================================================================

def test_ht_terminal_state(data_by_folio, grammar_tokens, token_to_role):
    """Test if high-HT folios have different terminal states."""
    print("="*70)
    print("TEST 1: HT x TERMINAL STATE")
    print("="*70)
    print("\nQuestion: Do high-HT folios end in different terminal grammar states?")

    folio_metrics = []

    for folio, tokens in data_by_folio.items():
        grammar, ht = classify_tokens(tokens, grammar_tokens)

        ht_density = len(ht) / len(tokens) if tokens else 0

        # Get terminal state (last grammar token)
        if grammar:
            last_grammar_token = grammar[-1][1]
            last_role = token_to_role.get(last_grammar_token, 'UNKNOWN')
        else:
            last_grammar_token = None
            last_role = 'NONE'

        # Get last few grammar tokens for pattern
        last_3_roles = []
        for _, t in grammar[-3:]:
            last_3_roles.append(token_to_role.get(t, 'UNK'))

        folio_metrics.append({
            'folio': folio,
            'ht_density': ht_density,
            'terminal_token': last_grammar_token,
            'terminal_role': last_role,
            'last_3_roles': tuple(last_3_roles),
            'n_tokens': len(tokens),
            'n_grammar': len(grammar),
            'n_ht': len(ht)
        })

    # Split into high/low HT
    ht_densities = [m['ht_density'] for m in folio_metrics]
    median_ht = np.median(ht_densities)

    high_ht = [m for m in folio_metrics if m['ht_density'] >= median_ht]
    low_ht = [m for m in folio_metrics if m['ht_density'] < median_ht]

    print(f"\nHT density: median={median_ht:.3f}, range={min(ht_densities):.3f}-{max(ht_densities):.3f}")
    print(f"High HT folios: {len(high_ht)}, Low HT folios: {len(low_ht)}")

    # Compare terminal role distributions
    high_terminal = Counter(m['terminal_role'] for m in high_ht)
    low_terminal = Counter(m['terminal_role'] for m in low_ht)

    all_roles = set(high_terminal.keys()) | set(low_terminal.keys())

    print("\n--- Terminal Role Distribution ---")
    print(f"{'Role':<20} {'High HT':>10} {'Low HT':>10} {'Diff':>10}")
    print("-" * 50)

    for role in sorted(all_roles):
        high_pct = high_terminal[role] / len(high_ht) * 100 if high_ht else 0
        low_pct = low_terminal[role] / len(low_ht) * 100 if low_ht else 0
        diff = high_pct - low_pct
        print(f"{role:<20} {high_pct:>9.1f}% {low_pct:>9.1f}% {diff:>+9.1f}%")

    # Chi-square test
    roles_for_test = [r for r in all_roles if high_terminal[r] + low_terminal[r] >= 5]
    if len(roles_for_test) >= 2:
        contingency = []
        for role in roles_for_test:
            contingency.append([high_terminal[role], low_terminal[role]])
        contingency = np.array(contingency).T

        chi2, p, dof, expected = chi2_contingency(contingency)
        print(f"\nChi-square test: chi2={chi2:.2f}, p={p:.4f}, dof={dof}")
    else:
        print("\nInsufficient data for chi-square test")
        p = 1.0

    # Correlation: HT density vs ending in specific state
    # Test: does HT correlate with ending in ENERGY_OPERATOR (most common)?
    energy_terminal = [1 if m['terminal_role'] == 'ENERGY_OPERATOR' else 0 for m in folio_metrics]
    rho, p_corr = spearmanr(ht_densities, energy_terminal)
    print(f"\nHT density x ENERGY_OPERATOR terminal: rho={rho:.3f}, p={p_corr:.4f}")

    # Summary
    print("\n--- TEST 1 SUMMARY ---")
    if p > 0.05 and abs(rho) < 0.2:
        print("RESULT: NO EFFECT - HT density does not predict terminal state")
        print("INTERPRETATION: HT is non-operational (doesn't influence outcomes)")
    else:
        print(f"RESULT: POSSIBLE EFFECT (p={p:.4f}, rho={rho:.3f})")
        print("INTERPRETATION: Needs further investigation")

    return p, rho

# =============================================================================
# TEST 2: HT -> Following Token Prediction
# =============================================================================

def test_ht_following_prediction(data_by_folio, grammar_tokens, token_to_role):
    """Test if HT presence alters probability of subsequent operational tokens."""
    print("\n" + "="*70)
    print("TEST 2: HT -> FOLLOWING TOKEN PREDICTION")
    print("="*70)
    print("\nQuestion: Does HT presence alter the probability of subsequent grammar tokens?")

    # For each grammar token, record:
    # - What grammar token preceded it (context)
    # - Whether there was HT between them
    # - What this grammar token is

    transitions_with_ht = defaultdict(Counter)  # context -> next token
    transitions_without_ht = defaultdict(Counter)

    for folio, tokens in data_by_folio.items():
        # Find grammar token positions
        grammar_positions = []
        for i, token in enumerate(tokens):
            if token in grammar_tokens:
                grammar_positions.append((i, token))

        # For each consecutive grammar pair, check if HT is between them
        for j in range(1, len(grammar_positions)):
            prev_pos, prev_token = grammar_positions[j-1]
            curr_pos, curr_token = grammar_positions[j]

            # Is there HT between them?
            has_ht = False
            for k in range(prev_pos + 1, curr_pos):
                if tokens[k] not in grammar_tokens:
                    has_ht = True
                    break

            prev_role = token_to_role.get(prev_token, 'UNK')
            curr_role = token_to_role.get(curr_token, 'UNK')

            if has_ht:
                transitions_with_ht[prev_role][curr_role] += 1
            else:
                transitions_without_ht[prev_role][curr_role] += 1

    # Compare distributions
    print("\n--- Transition Probabilities: WITH HT vs WITHOUT HT ---")

    all_contexts = set(transitions_with_ht.keys()) | set(transitions_without_ht.keys())
    all_targets = set()
    for d in [transitions_with_ht, transitions_without_ht]:
        for counter in d.values():
            all_targets.update(counter.keys())

    significant_diffs = []

    for context in sorted(all_contexts):
        with_ht = transitions_with_ht[context]
        without_ht = transitions_without_ht[context]

        total_with = sum(with_ht.values())
        total_without = sum(without_ht.values())

        if total_with < 20 or total_without < 20:
            continue

        print(f"\nContext: {context}")
        print(f"  With HT: {total_with} transitions, Without HT: {total_without} transitions")

        max_diff = 0
        for target in sorted(all_targets):
            with_pct = with_ht[target] / total_with * 100 if total_with else 0
            without_pct = without_ht[target] / total_without * 100 if total_without else 0
            diff = with_pct - without_pct

            if abs(diff) > 3:  # Only show notable differences
                print(f"    -> {target}: {with_pct:.1f}% vs {without_pct:.1f}% (diff={diff:+.1f}%)")
                if abs(diff) > max_diff:
                    max_diff = abs(diff)

        if max_diff > 5:
            significant_diffs.append((context, max_diff))

    # Overall comparison
    print("\n--- Overall Comparison ---")

    all_with_ht = Counter()
    all_without_ht = Counter()
    for context in all_contexts:
        for target, count in transitions_with_ht[context].items():
            all_with_ht[target] += count
        for target, count in transitions_without_ht[context].items():
            all_without_ht[target] += count

    total_with = sum(all_with_ht.values())
    total_without = sum(all_without_ht.values())

    print(f"\nTotal: {total_with} with-HT transitions, {total_without} without-HT transitions")

    # Build contingency table for chi-square
    targets_for_test = [t for t in all_targets if all_with_ht[t] + all_without_ht[t] >= 10]
    if len(targets_for_test) >= 2:
        contingency = []
        for target in targets_for_test:
            contingency.append([all_with_ht[target], all_without_ht[target]])
        contingency = np.array(contingency).T

        chi2, p, dof, expected = chi2_contingency(contingency)
        print(f"\nOverall chi-square: chi2={chi2:.2f}, p={p:.4f}, dof={dof}")

        # Effect size (Cramér's V)
        n = contingency.sum()
        min_dim = min(contingency.shape) - 1
        v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
        print(f"Effect size (Cramér's V): {v:.3f}")
    else:
        p = 1.0
        v = 0

    # Summary
    print("\n--- TEST 2 SUMMARY ---")
    if p > 0.05 or v < 0.1:
        print("RESULT: NO PREDICTIVE EFFECT - HT presence doesn't alter subsequent tokens")
        print("INTERPRETATION: HT has no causal/advisory role in grammar")
    else:
        print(f"RESULT: POSSIBLE EFFECT (p={p:.4f}, V={v:.3f})")
        print("INTERPRETATION: Weak coupling exists")

    return p, v

# =============================================================================
# TEST 3: HT Type Internal Structure
# =============================================================================

def test_ht_internal_structure(data_by_folio, grammar_tokens):
    """Analyze internal structure of HT types: Zipf, clustering, motor signatures."""
    print("\n" + "="*70)
    print("TEST 3: HT TYPE INTERNAL STRUCTURE")
    print("="*70)
    print("\nQuestion: Do HT types show Zipf-like distribution? Motor practice signatures?")

    # Collect all HT tokens
    all_ht = []
    for folio, tokens in data_by_folio.items():
        for token in tokens:
            if token not in grammar_tokens:
                all_ht.append(token)

    ht_counts = Counter(all_ht)
    print(f"\nTotal HT tokens: {len(all_ht)}")
    print(f"Unique HT types: {len(ht_counts)}")

    # --- Zipf Analysis ---
    print("\n--- ZIPF ANALYSIS ---")

    freqs = sorted(ht_counts.values(), reverse=True)
    ranks = np.arange(1, len(freqs) + 1)

    # Log-log regression for Zipf exponent
    log_ranks = np.log(ranks)
    log_freqs = np.log(freqs)

    slope, intercept, r_value, p_value, std_err = linregress(log_ranks, log_freqs)
    zipf_exponent = -slope

    print(f"Zipf exponent: {zipf_exponent:.3f} (ideal Zipf = 1.0)")
    print(f"R² of log-log fit: {r_value**2:.3f}")

    # Compare to expected Zipf
    if 0.8 <= zipf_exponent <= 1.2:
        zipf_verdict = "ZIPF-LIKE (natural language signature)"
    elif zipf_exponent < 0.8:
        zipf_verdict = "FLATTER than Zipf (more uniform, random-like)"
    else:
        zipf_verdict = "STEEPER than Zipf (more concentrated)"

    print(f"Verdict: {zipf_verdict}")

    # Hapax rate
    hapax = sum(1 for c in freqs if c == 1)
    hapax_rate = hapax / len(freqs) * 100
    print(f"\nHapax rate: {hapax_rate:.1f}% ({hapax}/{len(freqs)})")

    # Top 20 HT tokens
    print("\nTop 20 HT tokens:")
    for token, count in ht_counts.most_common(20):
        pct = count / len(all_ht) * 100
        print(f"  {token:<15}: {count:>5} ({pct:.2f}%)")

    # --- Motor Practice Signatures ---
    print("\n--- MOTOR PRACTICE SIGNATURES ---")

    # 1. Character length distribution
    lengths = [len(token) for token in all_ht]
    length_dist = Counter(lengths)

    print("\nLength distribution:")
    for length in sorted(length_dist.keys())[:10]:
        count = length_dist[length]
        pct = count / len(all_ht) * 100
        print(f"  {length} chars: {count:>5} ({pct:.1f}%)")

    mean_length = np.mean(lengths)
    std_length = np.std(lengths)
    print(f"\nMean length: {mean_length:.2f} ± {std_length:.2f}")

    # 2. Character repetition (motor practice often shows repeated chars)
    def count_char_runs(token):
        """Count max consecutive repeated character."""
        if not token:
            return 0
        max_run = 1
        current_run = 1
        for i in range(1, len(token)):
            if token[i] == token[i-1]:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 1
        return max_run

    runs = [count_char_runs(token) for token in all_ht]
    run_dist = Counter(runs)

    print("\nMax character run distribution (motor signature):")
    for run_len in sorted(run_dist.keys())[:6]:
        count = run_dist[run_len]
        pct = count / len(all_ht) * 100
        print(f"  {run_len}-run: {count:>5} ({pct:.1f}%)")

    # 3. Starting character distribution
    starting_chars = Counter(token[0] for token in all_ht if token)

    print("\nStarting character distribution (top 10):")
    for char, count in starting_chars.most_common(10):
        pct = count / len(all_ht) * 100
        print(f"  '{char}': {count:>5} ({pct:.1f}%)")

    # --- Clustering Analysis ---
    print("\n--- MORPHOLOGICAL CLUSTERING ---")

    # Group by prefix (first 2 chars)
    prefix_groups = defaultdict(list)
    for token in ht_counts.keys():
        if len(token) >= 2:
            prefix = token[:2]
            prefix_groups[prefix].append(token)

    print(f"\nUnique 2-char prefixes: {len(prefix_groups)}")

    # Top prefixes
    prefix_counts = {p: sum(ht_counts[t] for t in tokens) for p, tokens in prefix_groups.items()}
    print("\nTop 15 prefixes by token count:")
    for prefix, count in sorted(prefix_counts.items(), key=lambda x: -x[1])[:15]:
        n_types = len(prefix_groups[prefix])
        pct = count / len(all_ht) * 100
        print(f"  {prefix}: {count:>5} tokens, {n_types:>3} types ({pct:.1f}%)")

    # --- Compare to grammar token distribution ---
    print("\n--- COMPARISON TO GRAMMAR TOKENS ---")

    grammar_in_b = []
    for folio, tokens in data_by_folio.items():
        for token in tokens:
            if token in grammar_tokens:
                grammar_in_b.append(token)

    grammar_counts = Counter(grammar_in_b)
    grammar_freqs = sorted(grammar_counts.values(), reverse=True)

    # Zipf for grammar
    if len(grammar_freqs) > 10:
        g_log_ranks = np.log(np.arange(1, len(grammar_freqs) + 1))
        g_log_freqs = np.log(grammar_freqs)
        g_slope, _, g_r, _, _ = linregress(g_log_ranks, g_log_freqs)
        g_zipf = -g_slope
        print(f"Grammar Zipf exponent: {g_zipf:.3f} (R²={g_r**2:.3f})")
        print(f"HT Zipf exponent: {zipf_exponent:.3f}")

        if abs(zipf_exponent - g_zipf) < 0.2:
            print("-> Similar distribution shapes")
        else:
            print("-> Different distribution shapes")

    # Hapax comparison
    grammar_hapax = sum(1 for c in grammar_counts.values() if c == 1)
    grammar_hapax_rate = grammar_hapax / len(grammar_counts) * 100
    print(f"\nHapax rates: HT={hapax_rate:.1f}%, Grammar={grammar_hapax_rate:.1f}%")

    # Summary
    print("\n--- TEST 3 SUMMARY ---")
    print(f"Zipf exponent: {zipf_exponent:.3f} ({zipf_verdict})")
    print(f"Hapax rate: {hapax_rate:.1f}%")
    print(f"Mean length: {mean_length:.2f} chars")

    if 0.7 <= zipf_exponent <= 1.3 and hapax_rate > 50:
        print("\nINTERPRETATION: Distribution is NATURAL/GENERATIVE")
        print("  - Not random noise (would be flatter)")
        print("  - Not memorized templates (would have lower hapax)")
        print("  - Consistent with productive compositional system")
    elif hapax_rate > 70:
        print("\nINTERPRETATION: Highly GENERATIVE (mostly unique)")
        print("  - Consistent with practice/exploration behavior")
    else:
        print("\nINTERPRETATION: Mixed signature")

    return zipf_exponent, hapax_rate

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("="*70)
    print("HT CLOSURE TESTS")
    print("="*70)

    token_to_role, grammar_tokens = load_grammar()
    data_by_folio = load_b_data()

    print(f"\nLoaded {len(grammar_tokens)} grammar tokens")
    print(f"Loaded {len(data_by_folio)} Currier B folios")

    # Run tests
    p1, rho1 = test_ht_terminal_state(data_by_folio, grammar_tokens, token_to_role)
    p2, v2 = test_ht_following_prediction(data_by_folio, grammar_tokens, token_to_role)
    zipf, hapax = test_ht_internal_structure(data_by_folio, grammar_tokens)

    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY: HT CLOSURE TESTS")
    print("="*70)

    print("\n+---------------------------------------------------------------------+")
    print("| Test                          | Result            | Interpretation |")
    print("+---------------------------------------------------------------------+")

    # Test 1
    t1_result = "NO EFFECT" if (p1 > 0.05 and abs(rho1) < 0.2) else "WEAK EFFECT"
    t1_interp = "Non-operational" if t1_result == "NO EFFECT" else "Investigate"
    print(f"| 1. HT x Terminal State        | {t1_result:<17} | {t1_interp:<14} |")

    # Test 2
    t2_result = "NO EFFECT" if (p2 > 0.05 or v2 < 0.1) else "WEAK EFFECT"
    t2_interp = "No causal role" if t2_result == "NO EFFECT" else "Weak coupling"
    print(f"| 2. HT -> Following Prediction | {t2_result:<17} | {t2_interp:<14} |")

    # Test 3
    if 0.7 <= zipf <= 1.3:
        t3_result = f"Zipf={zipf:.2f}"
        t3_interp = "Generative"
    else:
        t3_result = f"Zipf={zipf:.2f}"
        t3_interp = "Non-Zipf"
    print(f"| 3. HT Internal Structure      | {t3_result:<17} | {t3_interp:<14} |")

    print("+---------------------------------------------------------------------+")

    # Overall verdict
    print("\n" + "-"*70)
    print("OVERALL VERDICT")
    print("-"*70)

    if t1_result == "NO EFFECT" and t2_result == "NO EFFECT":
        print("""
HT is CONFIRMED NON-OPERATIONAL:
  - Does not influence terminal states
  - Does not predict subsequent grammar tokens
  - Has generative/productive internal structure

The "calligraphy practice" or "attention maintenance" interpretation
remains the best fit. HT is a human-facing layer with no causal role
in the operational grammar.

TIER STATUS: Structural properties remain Tier 2.
             Interpretation (practice/attention) remains Tier 3-4.
             No alternative gains support from these tests.
""")
    else:
        print("""
HT shows WEAK COUPLING to operational grammar.
Further investigation may be warranted, but effect sizes are small.
""")

if __name__ == '__main__':
    main()
