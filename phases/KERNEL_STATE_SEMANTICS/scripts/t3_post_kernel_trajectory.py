#!/usr/bin/env python3
"""
Test 3: Post-Kernel Trajectory Analysis

Track what happens AFTER tokens containing k, h, e:
- How many tokens until next e-containing token?
- Is there a consistent "recovery" pattern after h?
- What breaks the e-state?

Goal: Determine if h-tokens trigger recovery patterns or are just intermediate.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from voynich import Transcript

def has_kernel(word: str, char: str) -> bool:
    """Check if word contains kernel character."""
    return char in word


def get_dominant_kernel(word: str) -> str:
    """Get the dominant kernel character (most frequent, or priority k>h>e)."""
    counts = {'k': word.count('k'), 'h': word.count('h'), 'e': word.count('e')}
    if counts['k'] > 0:
        return 'k'
    if counts['h'] > 0:
        return 'h'
    if counts['e'] > 0:
        return 'e'
    return 'none'


def main():
    print("=" * 60)
    print("Test 3: Post-Kernel Trajectory Analysis")
    print("=" * 60)

    tx = Transcript()

    # Collect all B tokens organized by line
    line_data = defaultdict(list)
    for token in tx.currier_b():
        key = (token.folio, token.line)
        line_data[key].append(token.word)

    # Convert to list of lines
    lines = list(line_data.values())
    print(f"\nTotal lines: {len(lines)}")
    print(f"Total tokens: {sum(len(line) for line in lines)}")

    results = {}

    # For each kernel character, analyze trajectories
    for start_kernel in ['k', 'h', 'e']:
        print(f"\n{'='*50}")
        print(f"Analyzing trajectories starting from '{start_kernel}'-containing tokens")
        print(f"{'='*50}")

        # Track: distance to next occurrence of each kernel char
        distances_to_k = []
        distances_to_h = []
        distances_to_e = []
        distances_to_any = []  # distance to any kernel char

        # Track: immediate successor kernel content
        immediate_successors = {'k': 0, 'h': 0, 'e': 0, 'none': 0}

        # Track: trajectory patterns (sequence of kernel chars in next 5 tokens)
        trajectory_patterns = Counter()

        for line in lines:
            for i, word in enumerate(line):
                if has_kernel(word, start_kernel):
                    # Look at subsequent tokens in same line
                    trajectory = []

                    found_k = False
                    found_h = False
                    found_e = False

                    for j in range(i + 1, len(line)):
                        next_word = line[j]
                        dom = get_dominant_kernel(next_word)
                        trajectory.append(dom)

                        if not found_k and 'k' in next_word:
                            distances_to_k.append(j - i)
                            found_k = True

                        if not found_h and 'h' in next_word:
                            distances_to_h.append(j - i)
                            found_h = True

                        if not found_e and 'e' in next_word:
                            distances_to_e.append(j - i)
                            found_e = True

                        if not found_k and not found_h and not found_e:
                            if 'k' in next_word or 'h' in next_word or 'e' in next_word:
                                distances_to_any.append(j - i)

                    # Immediate successor
                    if i + 1 < len(line):
                        next_word = line[i + 1]
                        if 'k' in next_word:
                            immediate_successors['k'] += 1
                        elif 'h' in next_word:
                            immediate_successors['h'] += 1
                        elif 'e' in next_word:
                            immediate_successors['e'] += 1
                        else:
                            immediate_successors['none'] += 1

                    # Trajectory pattern (first 5)
                    if trajectory:
                        pattern = '-'.join(trajectory[:5])
                        trajectory_patterns[pattern] += 1

        # Summary statistics
        total_starts = sum(immediate_successors.values())

        print(f"\nStarting points (tokens with '{start_kernel}'): {total_starts}")

        print(f"\nImmediate successor kernel content:")
        for k, v in immediate_successors.items():
            pct = 100 * v / total_starts if total_starts > 0 else 0
            print(f"  -> {k}: {v} ({pct:.1f}%)")

        print(f"\nDistance to next kernel character:")
        if distances_to_k:
            print(f"  -> k: mean={np.mean(distances_to_k):.2f}, median={np.median(distances_to_k):.1f}, n={len(distances_to_k)}")
        else:
            print(f"  -> k: no occurrences found")

        if distances_to_h:
            print(f"  -> h: mean={np.mean(distances_to_h):.2f}, median={np.median(distances_to_h):.1f}, n={len(distances_to_h)}")
        else:
            print(f"  -> h: no occurrences found")

        if distances_to_e:
            print(f"  -> e: mean={np.mean(distances_to_e):.2f}, median={np.median(distances_to_e):.1f}, n={len(distances_to_e)}")
        else:
            print(f"  -> e: no occurrences found")

        print(f"\nTop trajectory patterns (first 5 tokens):")
        for pattern, count in trajectory_patterns.most_common(10):
            pct = 100 * count / total_starts if total_starts > 0 else 0
            print(f"  {pattern}: {count} ({pct:.1f}%)")

        # Store results
        results[start_kernel] = {
            'total_starts': total_starts,
            'immediate_successors': immediate_successors,
            'immediate_successors_pct': {k: v/total_starts if total_starts > 0 else 0 for k, v in immediate_successors.items()},
            'distance_to_k': {
                'mean': float(np.mean(distances_to_k)) if distances_to_k else None,
                'median': float(np.median(distances_to_k)) if distances_to_k else None,
                'n': len(distances_to_k),
            },
            'distance_to_h': {
                'mean': float(np.mean(distances_to_h)) if distances_to_h else None,
                'median': float(np.median(distances_to_h)) if distances_to_h else None,
                'n': len(distances_to_h),
            },
            'distance_to_e': {
                'mean': float(np.mean(distances_to_e)) if distances_to_e else None,
                'median': float(np.median(distances_to_e)) if distances_to_e else None,
                'n': len(distances_to_e),
            },
            'top_trajectories': dict(trajectory_patterns.most_common(20)),
        }

    # Comparative analysis
    print("\n" + "=" * 60)
    print("COMPARATIVE ANALYSIS")
    print("=" * 60)

    # Key question: Does h show "recovery" pattern (fast path to e)?
    print("\n1. Recovery speed comparison (distance to e):")
    k_to_e = results['k']['distance_to_e']['mean']
    h_to_e = results['h']['distance_to_e']['mean']
    e_to_e = results['e']['distance_to_e']['mean']

    print(f"   From k: {k_to_e:.2f} tokens")
    print(f"   From h: {h_to_e:.2f} tokens")
    print(f"   From e: {e_to_e:.2f} tokens")

    if h_to_e and k_to_e:
        if h_to_e < k_to_e:
            print(f"   -> h reaches e FASTER than k ({h_to_e:.2f} vs {k_to_e:.2f})")
            print(f"   -> SUPPORTS hazard interpretation (h triggers faster recovery)")
        else:
            print(f"   -> h reaches e SLOWER than k ({h_to_e:.2f} vs {k_to_e:.2f})")
            print(f"   -> CONTRADICTS hazard interpretation")

    # Key question: Does e "hold" (low rate of leaving)?
    print("\n2. State persistence (immediate successor same as current):")
    k_to_k = results['k']['immediate_successors_pct'].get('k', 0)
    h_to_h = results['h']['immediate_successors_pct'].get('h', 0)
    e_to_e_imm = results['e']['immediate_successors_pct'].get('e', 0)

    print(f"   k->k (self-loop): {k_to_k:.1%}")
    print(f"   h->h (self-loop): {h_to_h:.1%}")
    print(f"   e->e (self-loop): {e_to_e_imm:.1%}")

    if e_to_e_imm > k_to_k and e_to_e_imm > h_to_h:
        print(f"   -> e is most persistent (SUPPORTS absorbing state interpretation)")

    # Key question: Does h avoid k?
    print("\n3. h->k avoidance:")
    h_to_k = results['h']['immediate_successors_pct'].get('k', 0)
    k_to_h = results['k']['immediate_successors_pct'].get('h', 0)

    print(f"   h->k (immediate): {h_to_k:.1%}")
    print(f"   k->h (immediate): {k_to_h:.1%}")

    if h_to_k < k_to_h:
        print(f"   -> h avoids k more than k avoids h (SUPPORTS hazard interpretation)")
    else:
        print(f"   -> No asymmetric avoidance (CONTRADICTS hazard interpretation)")

    # Interpretation
    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)

    hazard_evidence = 0
    sequential_evidence = 0
    energy_evidence = 0

    # Hazard: h should recover to e faster
    if h_to_e and k_to_e and h_to_e < k_to_e:
        hazard_evidence += 1
        print("- h->e faster than k->e: SUPPORTS HAZARD")
    else:
        print("- h->e not faster than k->e: CONTRADICTS HAZARD")

    # Hazard: h should avoid k
    if h_to_k < 0.1:
        hazard_evidence += 1
        print("- h->k strongly suppressed: SUPPORTS HAZARD")
    else:
        print("- h->k not strongly suppressed: CONTRADICTS HAZARD")

    # Energy: k should be high-energy (diverse successors), e should be low (stable)
    if e_to_e_imm > k_to_k:
        energy_evidence += 1
        print("- e more stable than k: SUPPORTS ENERGY")

    # Sequential: should see k->h->e ordering
    k_to_h_rate = results['k']['immediate_successors_pct'].get('h', 0)
    h_to_e_rate = results['h']['immediate_successors_pct'].get('e', 0)
    if k_to_h_rate > 0.1 and h_to_e_rate > 0.1:
        sequential_evidence += 1
        print("- k->h and h->e both common: SUPPORTS SEQUENTIAL")

    print(f"\nEvidence summary:")
    print(f"  Hazard interpretation: {hazard_evidence}/2")
    print(f"  Energy interpretation: {energy_evidence}/1")
    print(f"  Sequential interpretation: {sequential_evidence}/1")

    # Save results
    output_path = Path(__file__).parent.parent / "results" / "t3_post_kernel_trajectory.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
