#!/usr/bin/env python3
"""
Test 4: Energy Flow Model Test

Test the energy interpretation:
- k = high energy (input)
- h = transitional (mid-energy)
- e = low energy (ground state)

If true:
- Energy should decrease across lines
- "Disfavored" transitions should be energy-increasing
- Lines should show dissipation pattern

Goal: Quantitatively test the energy cascade hypothesis.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from voynich import Transcript


def compute_energy_score(word: str, model: str = 'simple') -> float:
    """
    Compute energy score for a word.

    Models:
    - 'simple': k=+1, h=0, e=-1
    - 'weighted': k=+2, h=+1, e=0 (all positive, e is ground)
    - 'count': sum of (k_count - e_count)
    """
    k_count = word.count('k')
    h_count = word.count('h')
    e_count = word.count('e')

    if model == 'simple':
        return k_count - e_count
    elif model == 'weighted':
        return 2 * k_count + h_count
    elif model == 'count':
        return k_count - e_count
    else:
        return k_count - e_count


def main():
    print("=" * 60)
    print("Test 4: Energy Flow Model Test")
    print("=" * 60)

    tx = Transcript()

    # Collect all B tokens organized by line
    line_data = defaultdict(list)
    for token in tx.currier_b():
        key = (token.folio, token.line)
        line_data[key].append(token.word)

    lines = list(line_data.values())
    print(f"\nTotal lines: {len(lines)}")

    # Filter to lines with at least 5 tokens for trajectory analysis
    long_lines = [line for line in lines if len(line) >= 5]
    print(f"Lines with 5+ tokens: {len(long_lines)}")

    results = {}

    for model_name in ['simple', 'weighted']:
        print(f"\n{'='*50}")
        print(f"Energy Model: {model_name}")
        print(f"{'='*50}")

        # Compute energy trajectory for each line
        line_trajectories = []
        position_energies = defaultdict(list)  # energy by normalized position

        for line in long_lines:
            energies = [compute_energy_score(word, model_name) for word in line]
            line_trajectories.append(energies)

            # Normalized positions
            for i, e in enumerate(energies):
                norm_pos = i / (len(line) - 1)
                # Bin to quintiles
                quintile = int(norm_pos * 5)
                if quintile == 5:
                    quintile = 4
                position_energies[quintile].append(e)

        # 1. Test: Does energy decrease across lines?
        print("\n1. Energy by line position (quintiles):")
        quintile_means = {}
        for q in range(5):
            energies = position_energies[q]
            mean_e = np.mean(energies)
            std_e = np.std(energies)
            quintile_means[q] = mean_e
            print(f"   Q{q+1} (pos {q*20}-{(q+1)*20}%): mean={mean_e:.3f}, std={std_e:.3f}, n={len(energies)}")

        # Linear regression: energy vs position
        all_positions = []
        all_energies = []
        for line in long_lines:
            for i, word in enumerate(line):
                all_positions.append(i / (len(line) - 1))
                all_energies.append(compute_energy_score(word, model_name))

        slope, intercept, r_value, p_value, std_err = stats.linregress(all_positions, all_energies)

        print(f"\n   Linear trend: slope={slope:.4f}, r={r_value:.3f}, p={p_value:.2e}")
        if slope < 0 and p_value < 0.05:
            print(f"   -> ENERGY DECREASES across line (SUPPORTS energy model)")
        elif slope > 0 and p_value < 0.05:
            print(f"   -> ENERGY INCREASES across line (CONTRADICTS energy model)")
        else:
            print(f"   -> No significant trend (NEUTRAL)")

        # 2. Test: First vs Last token energy
        first_energies = [compute_energy_score(line[0], model_name) for line in long_lines]
        last_energies = [compute_energy_score(line[-1], model_name) for line in long_lines]

        t_stat, p_val = stats.ttest_rel(first_energies, last_energies)

        print(f"\n2. First vs Last token energy:")
        print(f"   First token mean: {np.mean(first_energies):.3f}")
        print(f"   Last token mean: {np.mean(last_energies):.3f}")
        print(f"   Paired t-test: t={t_stat:.2f}, p={p_val:.2e}")

        if np.mean(first_energies) > np.mean(last_energies) and p_val < 0.05:
            print(f"   -> First has MORE energy than last (SUPPORTS energy cascade)")
        elif np.mean(first_energies) < np.mean(last_energies) and p_val < 0.05:
            print(f"   -> First has LESS energy than last (CONTRADICTS energy cascade)")
        else:
            print(f"   -> No significant difference (NEUTRAL)")

        # 3. Test: Energy change distribution
        energy_changes = []
        for line in long_lines:
            for i in range(len(line) - 1):
                e1 = compute_energy_score(line[i], model_name)
                e2 = compute_energy_score(line[i + 1], model_name)
                energy_changes.append(e2 - e1)

        print(f"\n3. Token-to-token energy change:")
        print(f"   Mean change: {np.mean(energy_changes):.4f}")
        print(f"   Median change: {np.median(energy_changes):.4f}")
        print(f"   % negative (energy decreasing): {100 * sum(1 for x in energy_changes if x < 0) / len(energy_changes):.1f}%")
        print(f"   % positive (energy increasing): {100 * sum(1 for x in energy_changes if x > 0) / len(energy_changes):.1f}%")
        print(f"   % zero (stable): {100 * sum(1 for x in energy_changes if x == 0) / len(energy_changes):.1f}%")

        # One-sample t-test: is mean change different from 0?
        t_stat, p_val = stats.ttest_1samp(energy_changes, 0)
        print(f"   t-test vs 0: t={t_stat:.2f}, p={p_val:.2e}")

        if np.mean(energy_changes) < 0 and p_val < 0.05:
            print(f"   -> Energy DECREASES on average (SUPPORTS energy cascade)")
        else:
            print(f"   -> Energy does NOT consistently decrease (CONTRADICTS/NEUTRAL)")

        # 4. Test: Kernel transition energy analysis
        print(f"\n4. Kernel transition energy patterns:")

        # For each kernel transition, what is the energy change?
        kernel_trans_energy = defaultdict(list)

        for line in long_lines:
            for i in range(len(line) - 1):
                w1, w2 = line[i], line[i + 1]
                # Identify kernel content
                k1 = 'k' if 'k' in w1 else ('h' if 'h' in w1 else ('e' if 'e' in w1 else 'n'))
                k2 = 'k' if 'k' in w2 else ('h' if 'h' in w2 else ('e' if 'e' in w2 else 'n'))
                trans = f"{k1}->{k2}"

                e1 = compute_energy_score(w1, model_name)
                e2 = compute_energy_score(w2, model_name)
                kernel_trans_energy[trans].append(e2 - e1)

        print(f"   Transition energy changes:")
        for trans in ['k->k', 'k->h', 'k->e', 'h->k', 'h->h', 'h->e', 'e->k', 'e->h', 'e->e']:
            if trans in kernel_trans_energy and kernel_trans_energy[trans]:
                changes = kernel_trans_energy[trans]
                mean_change = np.mean(changes)
                direction = "DOWN" if mean_change < -0.1 else "UP" if mean_change > 0.1 else "FLAT"
                print(f"     {trans}: mean_change={mean_change:+.3f} [{direction}], n={len(changes)}")

        # Store results for this model
        results[model_name] = {
            'quintile_means': quintile_means,
            'linear_slope': slope,
            'linear_r': r_value,
            'linear_p': p_value,
            'first_token_mean': float(np.mean(first_energies)),
            'last_token_mean': float(np.mean(last_energies)),
            'mean_energy_change': float(np.mean(energy_changes)),
            'pct_decreasing': 100 * sum(1 for x in energy_changes if x < 0) / len(energy_changes),
            'pct_increasing': 100 * sum(1 for x in energy_changes if x > 0) / len(energy_changes),
            'kernel_trans_energy': {k: float(np.mean(v)) for k, v in kernel_trans_energy.items() if v},
        }

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY: Energy Model Validity")
    print("=" * 60)

    simple = results['simple']
    weighted = results['weighted']

    supports_energy = 0
    contradicts_energy = 0

    # Check slope
    if simple['linear_slope'] < 0 and simple['linear_p'] < 0.05:
        supports_energy += 1
        print("- Energy decreases across line: SUPPORTS")
    else:
        print("- Energy does NOT decrease across line: CONTRADICTS/NEUTRAL")

    # Check first vs last
    if simple['first_token_mean'] > simple['last_token_mean']:
        supports_energy += 1
        print("- First token higher energy than last: SUPPORTS")
    else:
        print("- First token NOT higher energy: CONTRADICTS")

    # Check mean change
    if simple['mean_energy_change'] < 0:
        supports_energy += 1
        print("- Mean token-to-token change is negative: SUPPORTS")
    else:
        print("- Mean change is not negative: CONTRADICTS")

    # Check key transitions
    k_to_e = simple['kernel_trans_energy'].get('k->e', 0)
    h_to_e = simple['kernel_trans_energy'].get('h->e', 0)
    e_to_k = simple['kernel_trans_energy'].get('e->k', 0)

    if k_to_e < 0 and h_to_e < 0:
        supports_energy += 1
        print("- k->e and h->e both decrease energy: SUPPORTS")

    print(f"\nEnergy model support: {supports_energy}/4 criteria met")

    if supports_energy >= 3:
        print("\n** VERDICT: ENERGY MODEL HAS STRONG SUPPORT **")
        print("   k, h, e may represent energy levels (high -> mid -> low)")
    elif supports_energy >= 2:
        print("\n** VERDICT: ENERGY MODEL HAS MODERATE SUPPORT **")
    else:
        print("\n** VERDICT: ENERGY MODEL HAS WEAK SUPPORT **")

    # Save results
    output_path = Path(__file__).parent.parent / "results" / "t4_energy_flow_model.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
