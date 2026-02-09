#!/usr/bin/env python3
"""
Test 7: Class-Level Transition Analysis

Test whether the 49-class grammar shows directional patterns that
the character-level (k, h, e) analysis didn't find.

Key questions:
1. Do class-level transitions show strong preferences/avoidances?
2. Are there truly "forbidden" class pairs?
3. Is there structure at the class level that doesn't exist at character level?
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from voynich import Transcript

# Class definitions based on PREFIX patterns (simplified version)
# This maps tokens to one of 49 classes based on morphological patterns

def get_class(word: str) -> int:
    """
    Assign token to one of the 49 instruction classes.
    This is a simplified classification based on documented patterns.
    """
    # CC tokens (Classes 10, 11, 12, 17)
    if word == 'daiin' or word == 'daiiin':
        return 10
    if word == 'ol':
        return 11
    if word == 'k':
        return 12
    if word.startswith('ol') and len(word) > 2:
        return 17

    # EN classes by prefix (Classes 31-49 for qo/ch/sh prefixed)
    if word.startswith('qo'):
        if 'k' in word[2:]:
            return 31  # qok-
        elif 'ch' in word[2:]:
            return 32
        elif 'e' in word[2:]:
            return 33
        else:
            return 34  # other qo-

    if word.startswith('ch'):
        if 'k' in word[2:]:
            return 35
        elif 'e' in word[2:]:
            return 36
        elif 'o' in word[2:]:
            return 37
        else:
            return 38  # other ch-

    if word.startswith('sh'):
        if 'k' in word[2:]:
            return 39
        elif 'e' in word[2:]:
            return 40
        elif 'o' in word[2:]:
            return 41
        else:
            return 42  # other sh-

    # FQ classes (Classes 9, 13, 14, 23)
    if word.startswith('ok'):
        return 13
    if word.startswith('ot'):
        return 14
    if word in ['or', 'ar']:
        return 9
    if word in ['y', 'dy', 'am']:
        return 23

    # FL classes (Classes 7, 30, 38, 40)
    if word in ['dar', 'dal']:
        return 30
    if word in ['ar', 'or', 'al', 'ol'] and len(word) == 2:
        return 7
    if word.endswith('dy') and len(word) <= 3:
        return 38
    if word in ['aiin', 'ain', 'aiiin']:
        return 40

    # AX classes (various) - assign based on initial character
    if word.startswith('s') and not word.startswith('sh'):
        return 1
    if word.startswith('d') and word != 'daiin' and word != 'daiiin':
        return 2
    if word.startswith('l'):
        return 3
    if word.startswith('o') and not word.startswith('ok') and not word.startswith('ot') and not word.startswith('ol'):
        return 4
    if word.startswith('a'):
        return 5
    if word.startswith('c') and not word.startswith('ch'):
        return 6
    if word.startswith('t'):
        return 15
    if word.startswith('k') and word != 'k':
        return 16
    if word.startswith('p'):
        return 18
    if word.startswith('f'):
        return 19
    if word.startswith('r'):
        return 20
    if word.startswith('e'):
        return 21
    if word.startswith('i'):
        return 22
    if word.startswith('y') and word != 'y':
        return 24
    if word.startswith('n'):
        return 25
    if word.startswith('m'):
        return 26

    # Default class for unclassified
    return 0


def get_role(class_id: int) -> str:
    """Map class to role."""
    if class_id in [10, 11, 12, 17]:
        return 'CC'
    if class_id in [31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]:
        return 'EN'
    if class_id in [7, 30]:
        return 'FL'
    if class_id in [9, 13, 14, 23]:
        return 'FQ'
    if class_id in [1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29]:
        return 'AX'
    return 'UNK'


def main():
    print("=" * 60)
    print("Test 7: Class-Level Transition Analysis")
    print("=" * 60)

    tx = Transcript()

    # Collect all B tokens organized by line
    line_data = defaultdict(list)
    for token in tx.currier_b():
        key = (token.folio, token.line)
        line_data[key].append(token.word)

    lines = list(line_data.values())
    print(f"\nTotal lines: {len(lines)}")

    # Classify all tokens
    all_classes = []
    class_counts = Counter()

    for line in lines:
        for word in line:
            c = get_class(word)
            all_classes.append(c)
            class_counts[c] += 1

    print(f"Total tokens classified: {len(all_classes)}")
    print(f"Unique classes used: {len(class_counts)}")

    # Show class distribution
    print("\nTop 20 classes by frequency:")
    for cls, count in class_counts.most_common(20):
        role = get_role(cls)
        pct = 100 * count / len(all_classes)
        print(f"  Class {cls:2d} ({role:3s}): {count:5d} ({pct:5.1f}%)")

    # Build class-level bigrams
    class_bigrams = []
    for line in lines:
        classes = [get_class(word) for word in line]
        for i in range(len(classes) - 1):
            class_bigrams.append((classes[i], classes[i + 1]))

    print(f"\nTotal class bigrams: {len(class_bigrams)}")

    # Count transitions
    trans_counts = Counter(class_bigrams)

    # Compute observed/expected ratios
    total_bigrams = len(class_bigrams)
    source_counts = Counter(bg[0] for bg in class_bigrams)
    target_counts = Counter(bg[1] for bg in class_bigrams)

    # For each class pair, compute O/E ratio
    ratios = {}
    for (src, tgt), obs in trans_counts.items():
        p_src = source_counts[src] / total_bigrams
        p_tgt = target_counts[tgt] / total_bigrams
        expected = p_src * p_tgt * total_bigrams
        ratio = obs / expected if expected > 0 else 0
        ratios[(src, tgt)] = {
            'observed': obs,
            'expected': expected,
            'ratio': ratio,
        }

    # Find strongly disfavored (ratio < 0.5) and elevated (ratio > 2.0)
    disfavored = [(k, v) for k, v in ratios.items() if v['ratio'] < 0.5 and v['observed'] >= 5]
    elevated = [(k, v) for k, v in ratios.items() if v['ratio'] > 2.0 and v['observed'] >= 10]

    # Sort by ratio
    disfavored.sort(key=lambda x: x[1]['ratio'])
    elevated.sort(key=lambda x: -x[1]['ratio'])

    print("\n" + "=" * 50)
    print("STRONGLY DISFAVORED CLASS TRANSITIONS (ratio < 0.5)")
    print("=" * 50)
    if disfavored:
        for (src, tgt), data in disfavored[:20]:
            src_role = get_role(src)
            tgt_role = get_role(tgt)
            print(f"  {src:2d}({src_role})->{tgt:2d}({tgt_role}): {data['ratio']:.2f}x (obs={data['observed']}, exp={data['expected']:.0f})")
    else:
        print("  None found with obs >= 5")

    print("\n" + "=" * 50)
    print("STRONGLY ELEVATED CLASS TRANSITIONS (ratio > 2.0)")
    print("=" * 50)
    if elevated:
        for (src, tgt), data in elevated[:20]:
            src_role = get_role(src)
            tgt_role = get_role(tgt)
            print(f"  {src:2d}({src_role})->{tgt:2d}({tgt_role}): {data['ratio']:.2f}x (obs={data['observed']}, exp={data['expected']:.0f})")
    else:
        print("  None found with obs >= 10")

    # Role-level transition analysis
    print("\n" + "=" * 50)
    print("ROLE-LEVEL TRANSITION ANALYSIS")
    print("=" * 50)

    role_bigrams = []
    for line in lines:
        roles = [get_role(get_class(word)) for word in line]
        for i in range(len(roles) - 1):
            role_bigrams.append((roles[i], roles[i + 1]))

    role_trans = Counter(role_bigrams)
    role_source = Counter(bg[0] for bg in role_bigrams)
    role_target = Counter(bg[1] for bg in role_bigrams)
    total_role_bg = len(role_bigrams)

    print("\nRole transition matrix (O/E ratios):")
    roles = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UNK']
    print("        ", end="")
    for tgt in roles:
        print(f"{tgt:>6s}", end=" ")
    print()

    role_ratios = {}
    for src in roles:
        print(f"  {src:3s} ->", end="")
        for tgt in roles:
            obs = role_trans.get((src, tgt), 0)
            p_src = role_source.get(src, 0) / total_role_bg if total_role_bg > 0 else 0
            p_tgt = role_target.get(tgt, 0) / total_role_bg if total_role_bg > 0 else 0
            exp = p_src * p_tgt * total_role_bg
            ratio = obs / exp if exp > 0 else 0
            role_ratios[(src, tgt)] = ratio
            if ratio < 0.7:
                print(f" {ratio:5.2f}*", end="")  # Mark disfavored
            elif ratio > 1.3:
                print(f" {ratio:5.2f}+", end="")  # Mark elevated
            else:
                print(f" {ratio:5.2f} ", end="")
        print()

    print("\n  (* = disfavored <0.7, + = elevated >1.3)")

    # Check for truly forbidden pairs (0 observations with high expected)
    print("\n" + "=" * 50)
    print("TRULY FORBIDDEN? (0 observed, expected > 10)")
    print("=" * 50)

    forbidden_candidates = []
    for src in class_counts.keys():
        for tgt in class_counts.keys():
            if (src, tgt) not in trans_counts:
                p_src = source_counts.get(src, 0) / total_bigrams if total_bigrams > 0 else 0
                p_tgt = target_counts.get(tgt, 0) / total_bigrams if total_bigrams > 0 else 0
                exp = p_src * p_tgt * total_bigrams
                if exp > 10:
                    forbidden_candidates.append((src, tgt, exp))

    forbidden_candidates.sort(key=lambda x: -x[2])

    if forbidden_candidates:
        print(f"Found {len(forbidden_candidates)} pairs with 0 observed, expected > 10:")
        for src, tgt, exp in forbidden_candidates[:20]:
            src_role = get_role(src)
            tgt_role = get_role(tgt)
            print(f"  {src:2d}({src_role})->{tgt:2d}({tgt_role}): 0 observed, {exp:.0f} expected")
    else:
        print("  No truly forbidden pairs found (all expected pairs occur at least once)")

    # Summary statistics
    print("\n" + "=" * 50)
    print("SUMMARY STATISTICS")
    print("=" * 50)

    all_ratios = [v['ratio'] for v in ratios.values() if v['observed'] >= 5]
    print(f"\nClass transition ratio distribution (n={len(all_ratios)} pairs with obs>=5):")
    print(f"  Mean ratio: {np.mean(all_ratios):.2f}")
    print(f"  Std ratio: {np.std(all_ratios):.2f}")
    print(f"  Min ratio: {np.min(all_ratios):.2f}")
    print(f"  Max ratio: {np.max(all_ratios):.2f}")
    print(f"  % below 0.5: {100 * sum(1 for r in all_ratios if r < 0.5) / len(all_ratios):.1f}%")
    print(f"  % above 2.0: {100 * sum(1 for r in all_ratios if r > 2.0) / len(all_ratios):.1f}%")

    # Compare to character-level
    print("\n" + "=" * 60)
    print("COMPARISON: Class-Level vs Character-Level")
    print("=" * 60)

    char_ratios = [0.87, 0.96, 0.97, 1.03, 1.04, 1.11, 1.15, 1.15, 1.21]  # From T2
    print(f"\nCharacter-level (k,h,e) ratio range: {min(char_ratios):.2f} - {max(char_ratios):.2f}")
    print(f"Class-level ratio range: {np.min(all_ratios):.2f} - {np.max(all_ratios):.2f}")

    if np.max(all_ratios) > 2.0 or np.min(all_ratios) < 0.5:
        print("\n** CLASS-LEVEL SHOWS STRONGER STRUCTURE THAN CHARACTER-LEVEL **")
        print("   The 49-class grammar has real transition preferences/avoidances")
        print("   that don't exist at the character level.")
    else:
        print("\n** CLASS-LEVEL ALSO SHOWS WEAK STRUCTURE **")
        print("   Both levels have approximately uniform transitions.")

    # Interpretation
    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)

    n_disfavored = len(disfavored)
    n_elevated = len(elevated)
    n_forbidden = len(forbidden_candidates)

    print(f"\nStructure indicators:")
    print(f"  Strongly disfavored pairs (ratio < 0.5): {n_disfavored}")
    print(f"  Strongly elevated pairs (ratio > 2.0): {n_elevated}")
    print(f"  Truly forbidden pairs (0 obs, exp > 10): {n_forbidden}")

    if n_disfavored > 10 or n_elevated > 10 or n_forbidden > 5:
        print("\n** VERDICT: CLASS-LEVEL GRAMMAR HAS REAL STRUCTURE **")
        print("   There are genuine transition preferences at the class level")
        print("   that constitute a 'grammar' - not uniform transitions.")
    else:
        print("\n** VERDICT: CLASS-LEVEL GRAMMAR HAS WEAK STRUCTURE **")
        print("   Transitions are mostly uniform at class level too.")

    # Save results
    results = {
        'total_bigrams': len(class_bigrams),
        'unique_classes': len(class_counts),
        'n_disfavored': n_disfavored,
        'n_elevated': n_elevated,
        'n_forbidden': n_forbidden,
        'ratio_mean': float(np.mean(all_ratios)),
        'ratio_std': float(np.std(all_ratios)),
        'ratio_min': float(np.min(all_ratios)),
        'ratio_max': float(np.max(all_ratios)),
        'pct_below_0.5': 100 * sum(1 for r in all_ratios if r < 0.5) / len(all_ratios),
        'pct_above_2.0': 100 * sum(1 for r in all_ratios if r > 2.0) / len(all_ratios),
        'disfavored_pairs': [(f"{k[0]}->{k[1]}", v['ratio']) for k, v in disfavored[:20]],
        'elevated_pairs': [(f"{k[0]}->{k[1]}", v['ratio']) for k, v in elevated[:20]],
        'role_ratios': {f"{k[0]}->{k[1]}": v for k, v in role_ratios.items()},
    }

    output_path = Path(__file__).parent.parent / "results" / "t7_class_level_transitions.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
