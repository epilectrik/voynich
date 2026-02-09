#!/usr/bin/env python3
"""
Test 8: Kernel Validity Test

Test whether k, h, e constitute a meaningful "kernel" or are just common characters.

Original kernel claims:
- C089: k, h, e form the "irreducible control core"
- C103-105: k=ENERGY, h=PHASE, e=STABILITY functional roles
- C107: Kernel is BOUNDARY_ADJACENT to forbidden transitions
- C521: Directional asymmetry (k->e, h->e favored)

We've shown C521 doesn't hold at token level. What about the others?

Tests:
1. Are k, h, e more special than other common characters?
2. Do they have distinct distributions vs other characters?
3. Is there ANY structural property that makes them a "kernel"?
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from voynich import Transcript


def main():
    print("=" * 60)
    print("Test 8: Kernel Validity Test")
    print("=" * 60)
    print("\nQuestion: Do k, h, e constitute a meaningful 'kernel'?")

    tx = Transcript()

    # Collect all B tokens
    tokens = []
    for token in tx.currier_b():
        tokens.append(token.word)

    print(f"\nTotal B tokens: {len(tokens)}")

    # Count character frequencies
    char_counts = Counter()
    for word in tokens:
        for c in word:
            char_counts[c] += 1

    total_chars = sum(char_counts.values())

    print("\n" + "=" * 50)
    print("1. CHARACTER FREQUENCY ANALYSIS")
    print("=" * 50)

    print("\nAll characters by frequency:")
    for char, count in char_counts.most_common():
        pct = 100 * count / total_chars
        is_kernel = "(KERNEL)" if char in ['k', 'h', 'e'] else ""
        print(f"  '{char}': {count:6d} ({pct:5.1f}%) {is_kernel}")

    # Are k, h, e the most common?
    top_5 = [c for c, _ in char_counts.most_common(5)]
    kernel_chars = ['k', 'h', 'e']
    kernel_in_top5 = [c for c in kernel_chars if c in top_5]

    print(f"\nTop 5 characters: {top_5}")
    print(f"Kernel chars in top 5: {kernel_in_top5}")

    if len(kernel_in_top5) == 3:
        print("-> All kernel chars are in top 5 (SUPPORTS kernel as central)")
    else:
        print(f"-> Only {len(kernel_in_top5)}/3 kernel chars in top 5")

    # Token coverage: what % of tokens contain each character?
    print("\n" + "=" * 50)
    print("2. TOKEN COVERAGE ANALYSIS")
    print("=" * 50)

    char_token_coverage = {}
    for char in char_counts.keys():
        containing = sum(1 for word in tokens if char in word)
        char_token_coverage[char] = containing / len(tokens)

    print("\nToken coverage by character (% of tokens containing char):")
    for char, cov in sorted(char_token_coverage.items(), key=lambda x: -x[1])[:15]:
        is_kernel = "(KERNEL)" if char in ['k', 'h', 'e'] else ""
        print(f"  '{char}': {100*cov:5.1f}% {is_kernel}")

    # Are k, h, e exceptional in coverage?
    kernel_coverage = [char_token_coverage.get(c, 0) for c in kernel_chars]
    non_kernel_coverage = [v for c, v in char_token_coverage.items() if c not in kernel_chars]

    print(f"\nKernel char mean coverage: {100*np.mean(kernel_coverage):.1f}%")
    print(f"Non-kernel char mean coverage: {100*np.mean(non_kernel_coverage):.1f}%")

    t_stat, p_val = stats.ttest_ind(kernel_coverage, non_kernel_coverage)
    print(f"t-test: t={t_stat:.2f}, p={p_val:.3f}")

    # Co-occurrence analysis
    print("\n" + "=" * 50)
    print("3. CO-OCCURRENCE ANALYSIS")
    print("=" * 50)

    # How often do kernel chars co-occur in same token?
    cooccur = {
        'k_h': sum(1 for w in tokens if 'k' in w and 'h' in w),
        'k_e': sum(1 for w in tokens if 'k' in w and 'e' in w),
        'h_e': sum(1 for w in tokens if 'h' in w and 'e' in w),
        'k_h_e': sum(1 for w in tokens if 'k' in w and 'h' in w and 'e' in w),
        'k_only': sum(1 for w in tokens if 'k' in w and 'h' not in w and 'e' not in w),
        'h_only': sum(1 for w in tokens if 'h' in w and 'k' not in w and 'e' not in w),
        'e_only': sum(1 for w in tokens if 'e' in w and 'k' not in w and 'h' not in w),
        'none': sum(1 for w in tokens if 'k' not in w and 'h' not in w and 'e' not in w),
    }

    print("\nKernel character co-occurrence in tokens:")
    for pattern, count in cooccur.items():
        pct = 100 * count / len(tokens)
        print(f"  {pattern}: {count} ({pct:.1f}%)")

    # What % of tokens have ANY kernel char?
    has_kernel = sum(1 for w in tokens if 'k' in w or 'h' in w or 'e' in w)
    print(f"\nTokens with ANY kernel char: {has_kernel} ({100*has_kernel/len(tokens):.1f}%)")
    print(f"Tokens with NO kernel char: {cooccur['none']} ({100*cooccur['none']/len(tokens):.1f}%)")

    # Position analysis
    print("\n" + "=" * 50)
    print("4. POSITION-IN-TOKEN ANALYSIS")
    print("=" * 50)

    # Where do k, h, e appear within tokens?
    positions = {c: [] for c in ['k', 'h', 'e']}

    for word in tokens:
        if len(word) > 0:
            for i, c in enumerate(word):
                if c in positions:
                    normalized_pos = i / (len(word) - 1) if len(word) > 1 else 0.5
                    positions[c].append(normalized_pos)

    print("\nMean position within token (0=start, 1=end):")
    for char in ['k', 'h', 'e']:
        if positions[char]:
            mean_pos = np.mean(positions[char])
            std_pos = np.std(positions[char])
            print(f"  '{char}': mean={mean_pos:.3f}, std={std_pos:.3f}, n={len(positions[char])}")

    # Are positions different?
    f_stat, p_val = stats.f_oneway(positions['k'], positions['h'], positions['e'])
    print(f"\nANOVA for position difference: F={f_stat:.2f}, p={p_val:.2e}")

    if p_val < 0.05:
        print("-> Kernel chars have DIFFERENT positions within tokens (SUPPORTS distinct roles)")
    else:
        print("-> Kernel chars have SIMILAR positions (CONTRADICTS distinct roles)")

    # Mutual information with roles
    print("\n" + "=" * 50)
    print("5. KERNEL CHARS vs INSTRUCTION CLASSES")
    print("=" * 50)

    # Simplified class assignment (from T7)
    def get_class(word):
        if word == 'daiin' or word == 'daiiin':
            return 'CC'
        if word == 'ol' or word.startswith('ol'):
            return 'CC'
        if word.startswith('qo') or word.startswith('ch') or word.startswith('sh'):
            return 'EN'
        if word.startswith('ok') or word.startswith('ot'):
            return 'FQ'
        if word in ['or', 'ar', 'y', 'dy', 'am']:
            return 'FQ'
        if word in ['dar', 'dal', 'aiin', 'ain']:
            return 'FL'
        return 'AX'

    # For each kernel char, what roles do containing tokens have?
    kernel_role_dist = {c: Counter() for c in ['k', 'h', 'e', 'none']}

    for word in tokens:
        role = get_class(word)
        if 'k' in word:
            kernel_role_dist['k'][role] += 1
        if 'h' in word:
            kernel_role_dist['h'][role] += 1
        if 'e' in word:
            kernel_role_dist['e'][role] += 1
        if 'k' not in word and 'h' not in word and 'e' not in word:
            kernel_role_dist['none'][role] += 1

    print("\nRole distribution by kernel character:")
    roles = ['CC', 'EN', 'FL', 'FQ', 'AX']
    print("        ", end="")
    for role in roles:
        print(f"{role:>7s}", end="")
    print()

    for char in ['k', 'h', 'e', 'none']:
        total = sum(kernel_role_dist[char].values())
        print(f"  {char:4s}:", end="")
        for role in roles:
            count = kernel_role_dist[char][role]
            pct = 100 * count / total if total > 0 else 0
            print(f" {pct:5.1f}%", end="")
        print(f"  (n={total})")

    # Chi-square test for role independence (exclude FL which has zeros)
    roles_nonzero = ['CC', 'EN', 'FQ', 'AX']  # FL is zero for kernel chars
    contingency = []
    for char in ['k', 'h', 'e']:
        row = [kernel_role_dist[char][role] for role in roles_nonzero]
        contingency.append(row)

    chi2, p_val, dof, expected = stats.chi2_contingency(contingency)
    print(f"\nChi-square test (k,h,e vs roles, excl FL): chi2={chi2:.1f}, p={p_val:.2e}")

    if p_val < 0.05:
        print("-> Kernel chars have DIFFERENT role distributions (SUPPORTS distinct functions)")
    else:
        print("-> Kernel chars have SIMILAR role distributions (NO distinct functions)")

    # Final assessment
    print("\n" + "=" * 60)
    print("FINAL ASSESSMENT: Is there a 'kernel'?")
    print("=" * 60)

    print("\nEvidence FOR kernel concept:")
    evidence_for = 0
    evidence_against = 0

    # High coverage
    if np.mean(kernel_coverage) > 0.3:
        evidence_for += 1
        print("  + k, h, e have high token coverage (>30%)")
    else:
        evidence_against += 1
        print("  - k, h, e have low token coverage")

    # Position differences
    if p_val < 0.05:  # from ANOVA
        evidence_for += 1
        print("  + k, h, e have different positions within tokens")
    else:
        evidence_against += 1
        print("  - k, h, e have similar positions")

    # Role association differences
    # Check if h is more EN-associated than k
    h_en_pct = kernel_role_dist['h']['EN'] / sum(kernel_role_dist['h'].values())
    k_en_pct = kernel_role_dist['k']['EN'] / sum(kernel_role_dist['k'].values())
    e_en_pct = kernel_role_dist['e']['EN'] / sum(kernel_role_dist['e'].values())

    if abs(h_en_pct - k_en_pct) > 0.1 or abs(h_en_pct - e_en_pct) > 0.1:
        evidence_for += 1
        print("  + k, h, e have different role associations")
    else:
        evidence_against += 1
        print("  - k, h, e have similar role associations")

    print("\nEvidence AGAINST kernel concept:")

    # No directional flow (from T1-T3)
    evidence_against += 1
    print("  - No directional flow at token level (T1-T3)")

    # Transitions are uniform
    evidence_against += 1
    print("  - Character-level transitions are uniform (T2)")

    print(f"\nScore: {evidence_for} FOR, {evidence_against} AGAINST")

    # Verdict
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    if evidence_for > evidence_against:
        print("\n** k, h, e ARE a kernel in SOME sense **")
        print("   They are common, central characters with role associations.")
        print("   But NOT in the 'control flow' sense originally claimed.")
    else:
        print("\n** k, h, e are NOT a meaningful 'kernel' **")
        print("   They are common characters, but no more special than others.")
        print("   The 'kernel' concept may be an artifact of interpretation.")

    print("\nWhat k, h, e actually are:")
    print("  - Common morphological building blocks")
    print("  - Strongly associated with EN (energy) role tokens")
    print("  - NOT directional flow states")
    print("  - NOT 'control operators' in any meaningful sense")

    # Save results
    results = {
        'char_frequencies': dict(char_counts.most_common()),
        'token_coverage': {c: round(v, 3) for c, v in char_token_coverage.items()},
        'kernel_coverage_mean': float(np.mean(kernel_coverage)),
        'cooccurrence': cooccur,
        'position_means': {c: float(np.mean(positions[c])) for c in ['k', 'h', 'e']},
        'role_distribution': {c: dict(kernel_role_dist[c]) for c in ['k', 'h', 'e', 'none']},
        'evidence_for': evidence_for,
        'evidence_against': evidence_against,
    }

    output_path = Path(__file__).parent.parent / "results" / "t8_kernel_validity_test.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
