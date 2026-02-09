#!/usr/bin/env python3
"""
Test 5: Alternative Framing Fit Test

Systematically test which interpretation best fits the observed data:
- HAZARD: h is danger, e is safety, flow is escape
- SEQUENTIAL: k->h->e is correct order, violations are sequence errors
- ENERGY: k=high, h=mid, e=low, flow is dissipation
- PHASE: k=init, h=active, e=complete, flow is phase progression

For each framing, generate predictions and score against observations.
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
    print("Test 5: Alternative Framing Fit Test")
    print("=" * 60)

    tx = Transcript()

    # Collect all B tokens organized by line
    line_data = defaultdict(list)
    for token in tx.currier_b():
        key = (token.folio, token.line)
        line_data[key].append(token.word)

    lines = list(line_data.values())
    print(f"\nTotal lines: {len(lines)}")

    # Build transition matrix
    transitions = defaultdict(int)
    total_by_source = defaultdict(int)

    for line in lines:
        for i in range(len(line) - 1):
            w1, w2 = line[i], line[i + 1]
            # Dominant kernel
            k1 = 'k' if 'k' in w1 else ('h' if 'h' in w1 else ('e' if 'e' in w1 else 'n'))
            k2 = 'k' if 'k' in w2 else ('h' if 'h' in w2 else ('e' if 'e' in w2 else 'n'))
            transitions[(k1, k2)] += 1
            total_by_source[k1] += 1

    # Compute transition probabilities
    trans_probs = {}
    for (k1, k2), count in transitions.items():
        prob = count / total_by_source[k1] if total_by_source[k1] > 0 else 0
        trans_probs[(k1, k2)] = prob

    print("\nObserved transition probabilities:")
    for k1 in ['k', 'h', 'e', 'n']:
        print(f"  From {k1}:")
        for k2 in ['k', 'h', 'e', 'n']:
            prob = trans_probs.get((k1, k2), 0)
            count = transitions.get((k1, k2), 0)
            print(f"    -> {k2}: {prob:.3f} (n={count})")

    # Compute position statistics
    position_by_kernel = defaultdict(list)

    for line in lines:
        if len(line) < 2:
            continue
        for i, word in enumerate(line):
            norm_pos = i / (len(line) - 1)
            k = 'k' if 'k' in word else ('h' if 'h' in word else ('e' if 'e' in word else 'n'))
            position_by_kernel[k].append(norm_pos)

    print("\nMean line position by kernel:")
    for k in ['k', 'h', 'e', 'n']:
        if position_by_kernel[k]:
            print(f"  {k}: mean={np.mean(position_by_kernel[k]):.3f}, n={len(position_by_kernel[k])}")

    # Define framings and their predictions
    framings = {
        'HAZARD': {
            'description': 'h is danger, e is safety, flow is escape',
            'predictions': {
                'h->e elevated': ('h', 'e', 'elevated'),  # escape to safety
                'h->k suppressed': ('h', 'k', 'suppressed'),  # avoid energy in danger
                'e->h suppressed': ('e', 'h', 'suppressed'),  # don't return to danger
                'h isolated': 'h has distinct position',
                'h->h suppressed': ('h', 'h', 'suppressed'),  # don't linger in danger
            }
        },
        'SEQUENTIAL': {
            'description': 'k->h->e is correct order, violations are errors',
            'predictions': {
                'k->h elevated': ('k', 'h', 'elevated'),  # forward flow
                'h->e elevated': ('h', 'e', 'elevated'),  # forward flow
                'h->k suppressed': ('h', 'k', 'suppressed'),  # no backward
                'e->k suppressed': ('e', 'k', 'suppressed'),  # no restart
                'position ordering': 'k < h < e in position',
            }
        },
        'ENERGY': {
            'description': 'k=high, h=mid, e=low, flow is dissipation',
            'predictions': {
                'k->e elevated': ('k', 'e', 'elevated'),  # energy drop
                'e->k suppressed': ('e', 'k', 'suppressed'),  # no energy pump
                'e->h suppressed': ('e', 'h', 'suppressed'),  # stay low
                'k early position': 'k earlier than e in line',
                'energy decreases': 'net energy flow negative',
            }
        },
        'PHASE': {
            'description': 'k=init, h=active, e=complete',
            'predictions': {
                'k->h elevated': ('k', 'h', 'elevated'),  # init to active
                'h->e elevated': ('h', 'e', 'elevated'),  # active to complete
                'e->k elevated': ('e', 'k', 'elevated'),  # restart cycle
                'k initial position': 'k concentrated at line start',
                'e final position': 'e concentrated at line end',
            }
        }
    }

    # Compute baseline for "elevated" vs "suppressed"
    # Use expected under independence
    total_trans = sum(transitions.values())
    expected = {}
    for k1 in ['k', 'h', 'e', 'n']:
        for k2 in ['k', 'h', 'e', 'n']:
            # Expected = P(source=k1) * P(target=k2) * total
            p_src = total_by_source[k1] / total_trans if total_trans > 0 else 0
            tgt_count = sum(transitions.get((x, k2), 0) for x in ['k', 'h', 'e', 'n'])
            p_tgt = tgt_count / total_trans if total_trans > 0 else 0
            expected[(k1, k2)] = p_src * p_tgt * total_trans

    # Compute observed/expected ratios
    obs_exp_ratio = {}
    for (k1, k2), obs in transitions.items():
        exp = expected.get((k1, k2), 1)
        obs_exp_ratio[(k1, k2)] = obs / exp if exp > 0 else 0

    print("\nObserved/Expected ratios:")
    for k1 in ['k', 'h', 'e']:
        for k2 in ['k', 'h', 'e']:
            ratio = obs_exp_ratio.get((k1, k2), 0)
            status = 'ELEVATED' if ratio > 1.2 else 'SUPPRESSED' if ratio < 0.8 else 'NEUTRAL'
            print(f"  {k1}->{k2}: {ratio:.2f}x [{status}]")

    # Score each framing
    print("\n" + "=" * 60)
    print("FRAMING SCORES")
    print("=" * 60)

    results = {}

    for framing_name, framing in framings.items():
        print(f"\n{framing_name}: {framing['description']}")
        score = 0
        max_score = 0

        for pred_name, pred in framing['predictions'].items():
            max_score += 1

            if isinstance(pred, tuple):
                # Transition prediction
                src, tgt, expected_type = pred
                ratio = obs_exp_ratio.get((src, tgt), 1.0)

                if expected_type == 'elevated':
                    if ratio > 1.2:
                        score += 1
                        print(f"  + {pred_name}: ratio={ratio:.2f}x (CORRECT)")
                    else:
                        print(f"  - {pred_name}: ratio={ratio:.2f}x (WRONG - expected elevated)")
                elif expected_type == 'suppressed':
                    if ratio < 0.8:
                        score += 1
                        print(f"  + {pred_name}: ratio={ratio:.2f}x (CORRECT)")
                    else:
                        print(f"  - {pred_name}: ratio={ratio:.2f}x (WRONG - expected suppressed)")

            elif 'position' in pred_name.lower():
                # Position prediction
                if 'k < h < e' in pred:
                    k_pos = np.mean(position_by_kernel['k']) if position_by_kernel['k'] else 0.5
                    h_pos = np.mean(position_by_kernel['h']) if position_by_kernel['h'] else 0.5
                    e_pos = np.mean(position_by_kernel['e']) if position_by_kernel['e'] else 0.5
                    if k_pos < h_pos < e_pos:
                        score += 1
                        print(f"  + {pred_name}: k={k_pos:.3f} < h={h_pos:.3f} < e={e_pos:.3f} (CORRECT)")
                    else:
                        print(f"  - {pred_name}: k={k_pos:.3f}, h={h_pos:.3f}, e={e_pos:.3f} (WRONG)")
                elif 'k earlier' in pred:
                    k_pos = np.mean(position_by_kernel['k']) if position_by_kernel['k'] else 0.5
                    e_pos = np.mean(position_by_kernel['e']) if position_by_kernel['e'] else 0.5
                    if k_pos < e_pos:
                        score += 1
                        print(f"  + {pred_name}: k={k_pos:.3f} < e={e_pos:.3f} (CORRECT)")
                    else:
                        print(f"  - {pred_name}: k={k_pos:.3f}, e={e_pos:.3f} (WRONG)")
                elif 'k initial' in pred or 'k concentrated at line start' in pred:
                    k_pos = np.mean(position_by_kernel['k']) if position_by_kernel['k'] else 0.5
                    if k_pos < 0.4:
                        score += 1
                        print(f"  + {pred_name}: k mean pos={k_pos:.3f} (CORRECT)")
                    else:
                        print(f"  - {pred_name}: k mean pos={k_pos:.3f} (WRONG)")
                elif 'e final' in pred or 'e concentrated at line end' in pred:
                    e_pos = np.mean(position_by_kernel['e']) if position_by_kernel['e'] else 0.5
                    if e_pos > 0.6:
                        score += 1
                        print(f"  + {pred_name}: e mean pos={e_pos:.3f} (CORRECT)")
                    else:
                        print(f"  - {pred_name}: e mean pos={e_pos:.3f} (WRONG)")
                elif 'h has distinct' in pred:
                    # Test if h position is significantly different from k and e
                    k_positions = position_by_kernel['k']
                    h_positions = position_by_kernel['h']
                    e_positions = position_by_kernel['e']
                    _, p_kh = stats.mannwhitneyu(k_positions, h_positions) if k_positions and h_positions else (0, 1)
                    _, p_he = stats.mannwhitneyu(h_positions, e_positions) if h_positions and e_positions else (0, 1)
                    if p_kh < 0.05 or p_he < 0.05:
                        score += 1
                        print(f"  + {pred_name}: h distinct (p_kh={p_kh:.3f}, p_he={p_he:.3f}) (CORRECT)")
                    else:
                        print(f"  - {pred_name}: h not distinct (p_kh={p_kh:.3f}, p_he={p_he:.3f}) (WRONG)")

            elif 'energy decreases' in pred:
                # Check if net energy flow is negative
                net_flow = 0
                for (k1, k2), count in transitions.items():
                    # Energy: k=+1, h=0, e=-1
                    e1 = 1 if k1 == 'k' else (0 if k1 == 'h' else (-1 if k1 == 'e' else 0))
                    e2 = 1 if k2 == 'k' else (0 if k2 == 'h' else (-1 if k2 == 'e' else 0))
                    net_flow += (e2 - e1) * count
                if net_flow < 0:
                    score += 1
                    print(f"  + {pred_name}: net flow={net_flow} (CORRECT)")
                else:
                    print(f"  - {pred_name}: net flow={net_flow} (WRONG)")

        pct = 100 * score / max_score if max_score > 0 else 0
        print(f"  SCORE: {score}/{max_score} ({pct:.0f}%)")

        results[framing_name] = {
            'description': framing['description'],
            'score': score,
            'max_score': max_score,
            'percentage': pct,
        }

    # Determine winner
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    sorted_framings = sorted(results.items(), key=lambda x: -x[1]['percentage'])

    print("\nRanking:")
    for i, (name, data) in enumerate(sorted_framings, 1):
        print(f"  {i}. {name}: {data['score']}/{data['max_score']} ({data['percentage']:.0f}%)")

    winner = sorted_framings[0]
    runner_up = sorted_framings[1] if len(sorted_framings) > 1 else None

    print(f"\n** BEST FIT: {winner[0]} ({winner[1]['percentage']:.0f}%) **")
    print(f"   {winner[1]['description']}")

    if runner_up and winner[1]['percentage'] - runner_up[1]['percentage'] < 20:
        print(f"\n   Note: {runner_up[0]} is close ({runner_up[1]['percentage']:.0f}%)")
        print(f"   Multiple interpretations may be valid.")

    # Additional data
    results['transition_ratios'] = {f"{k1}->{k2}": ratio for (k1, k2), ratio in obs_exp_ratio.items()}
    results['position_means'] = {k: float(np.mean(v)) for k, v in position_by_kernel.items() if v}

    # Save results
    output_path = Path(__file__).parent.parent / "results" / "t5_framing_fit_test.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
