#!/usr/bin/env python3
"""
Test 1: Kernel Context Profiling

Profile the contexts in which k, h, e kernel characters appear.
For each kernel operator, analyze:
- Predecessor distribution (what comes before)
- Successor distribution (what comes after)
- Line position distribution
- Role co-occurrence
- Section distribution

Goal: Determine if k, h, e have distinct functional profiles or are interchangeable grammar markers.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from voynich import Transcript, Morphology

def classify_role(word: str) -> str:
    """Simplified role classification based on PREFIX patterns."""
    morph = Morphology()
    m = morph.extract(word)

    # CC tokens
    if word in ['daiin', 'daiiin', 'saiin', 'sain']:
        return 'CC'
    if word.startswith('ol') and len(word) > 2:
        return 'CC'  # ol-derived
    if word == 'ol':
        return 'CC'

    # EN by prefix
    if m.prefix in ['ch', 'sh', 'qo']:
        return 'EN'

    # FL by characteristic MIDDLEs
    fl_middles = {'ar', 'or', 'al', 'ol', 'am', 'om', 'an', 'ain', 'aiin', 'air', 'dy', 'dal', 'dar'}
    if m.middle in fl_middles and not m.prefix:
        return 'FL'

    # FQ by pattern
    if m.prefix in ['ok', 'ot']:
        return 'FQ'
    if word in ['or', 'ar', 'ol', 'al', 'y', 'dy', 'aiin', 'ain']:
        return 'FQ'

    # Default to AX
    return 'AX'


def has_kernel_char(word: str, char: str) -> bool:
    """Check if word contains kernel character."""
    return char in word


def get_kernel_profile(word: str) -> dict:
    """Get kernel character profile for a word."""
    return {
        'has_k': 'k' in word,
        'has_h': 'h' in word,
        'has_e': 'e' in word,
        'k_count': word.count('k'),
        'h_count': word.count('h'),
        'e_count': word.count('e'),
    }


def main():
    print("=" * 60)
    print("Test 1: Kernel Context Profiling")
    print("=" * 60)

    tx = Transcript()

    # Collect all B tokens with context
    tokens = []
    for token in tx.currier_b():
        tokens.append({
            'word': token.word,
            'folio': token.folio,
            'line': token.line,
            'section': token.section,
        })

    print(f"\nTotal B tokens: {len(tokens)}")

    # Build line groups for predecessor/successor analysis
    line_groups = defaultdict(list)
    for i, t in enumerate(tokens):
        key = (t['folio'], t['line'])
        line_groups[key].append((i, t))

    # Analyze each kernel character
    results = {}

    for kernel_char in ['k', 'h', 'e']:
        print(f"\n{'='*40}")
        print(f"Analyzing kernel character: {kernel_char}")
        print(f"{'='*40}")

        # Find all tokens containing this kernel char
        kernel_tokens = []
        kernel_indices = set()

        for i, t in enumerate(tokens):
            if kernel_char in t['word']:
                kernel_tokens.append((i, t))
                kernel_indices.add(i)

        print(f"Tokens containing '{kernel_char}': {len(kernel_tokens)} ({100*len(kernel_tokens)/len(tokens):.1f}%)")

        # 1. Predecessor analysis
        predecessor_words = []
        predecessor_kernel = {'k': 0, 'h': 0, 'e': 0, 'none': 0}
        predecessor_roles = Counter()

        for i, t in kernel_tokens:
            # Find predecessor in same line
            key = (t['folio'], t['line'])
            line_toks = line_groups[key]

            # Find position in line
            pos_in_line = None
            for j, (idx, lt) in enumerate(line_toks):
                if idx == i:
                    pos_in_line = j
                    break

            if pos_in_line is not None and pos_in_line > 0:
                pred_idx, pred_tok = line_toks[pos_in_line - 1]
                predecessor_words.append(pred_tok['word'])
                predecessor_roles[classify_role(pred_tok['word'])] += 1

                # Kernel content of predecessor
                has_any = False
                for kc in ['k', 'h', 'e']:
                    if kc in pred_tok['word']:
                        predecessor_kernel[kc] += 1
                        has_any = True
                if not has_any:
                    predecessor_kernel['none'] += 1

        # 2. Successor analysis
        successor_words = []
        successor_kernel = {'k': 0, 'h': 0, 'e': 0, 'none': 0}
        successor_roles = Counter()

        for i, t in kernel_tokens:
            key = (t['folio'], t['line'])
            line_toks = line_groups[key]

            pos_in_line = None
            for j, (idx, lt) in enumerate(line_toks):
                if idx == i:
                    pos_in_line = j
                    break

            if pos_in_line is not None and pos_in_line < len(line_toks) - 1:
                succ_idx, succ_tok = line_toks[pos_in_line + 1]
                successor_words.append(succ_tok['word'])
                successor_roles[classify_role(succ_tok['word'])] += 1

                has_any = False
                for kc in ['k', 'h', 'e']:
                    if kc in succ_tok['word']:
                        successor_kernel[kc] += 1
                        has_any = True
                if not has_any:
                    successor_kernel['none'] += 1

        # 3. Line position distribution
        line_positions = []
        for i, t in kernel_tokens:
            key = (t['folio'], t['line'])
            line_toks = line_groups[key]
            if len(line_toks) > 1:
                pos_in_line = None
                for j, (idx, lt) in enumerate(line_toks):
                    if idx == i:
                        pos_in_line = j
                        break
                if pos_in_line is not None:
                    normalized_pos = pos_in_line / (len(line_toks) - 1)
                    line_positions.append(normalized_pos)

        # 4. Role of kernel-containing tokens
        self_roles = Counter()
        for i, t in kernel_tokens:
            self_roles[classify_role(t['word'])] += 1

        # 5. Section distribution
        section_dist = Counter()
        for i, t in kernel_tokens:
            section_dist[t['section']] += 1

        # Store results
        total_pred = sum(predecessor_kernel.values())
        total_succ = sum(successor_kernel.values())

        results[kernel_char] = {
            'count': len(kernel_tokens),
            'percentage': 100 * len(kernel_tokens) / len(tokens),
            'predecessor_kernel': {k: v/total_pred if total_pred > 0 else 0 for k, v in predecessor_kernel.items()},
            'predecessor_kernel_raw': dict(predecessor_kernel),
            'predecessor_roles': dict(predecessor_roles),
            'successor_kernel': {k: v/total_succ if total_succ > 0 else 0 for k, v in successor_kernel.items()},
            'successor_kernel_raw': dict(successor_kernel),
            'successor_roles': dict(successor_roles),
            'line_position_mean': np.mean(line_positions) if line_positions else 0,
            'line_position_std': np.std(line_positions) if line_positions else 0,
            'self_roles': dict(self_roles),
            'section_distribution': dict(section_dist),
        }

        # Print summary
        print(f"\nPredecessor kernel content:")
        for kc, v in predecessor_kernel.items():
            pct = 100 * v / total_pred if total_pred > 0 else 0
            print(f"  {kc}: {v} ({pct:.1f}%)")

        print(f"\nSuccessor kernel content:")
        for kc, v in successor_kernel.items():
            pct = 100 * v / total_succ if total_succ > 0 else 0
            print(f"  {kc}: {v} ({pct:.1f}%)")

        print(f"\nLine position: mean={np.mean(line_positions):.3f}, std={np.std(line_positions):.3f}")

        print(f"\nSelf roles:")
        for role, count in self_roles.most_common():
            print(f"  {role}: {count} ({100*count/len(kernel_tokens):.1f}%)")

    # Cross-kernel comparison
    print("\n" + "=" * 60)
    print("CROSS-KERNEL COMPARISON")
    print("=" * 60)

    # Position comparison
    print("\nLine Position Comparison:")
    print(f"  k mean: {results['k']['line_position_mean']:.3f}")
    print(f"  h mean: {results['h']['line_position_mean']:.3f}")
    print(f"  e mean: {results['e']['line_position_mean']:.3f}")

    # Successor flow comparison
    print("\nSuccessor Flow (what follows each kernel char):")
    print(f"  After k: k={results['k']['successor_kernel']['k']:.1%}, h={results['k']['successor_kernel']['h']:.1%}, e={results['k']['successor_kernel']['e']:.1%}")
    print(f"  After h: k={results['h']['successor_kernel']['k']:.1%}, h={results['h']['successor_kernel']['h']:.1%}, e={results['h']['successor_kernel']['e']:.1%}")
    print(f"  After e: k={results['e']['successor_kernel']['k']:.1%}, h={results['e']['successor_kernel']['h']:.1%}, e={results['e']['successor_kernel']['e']:.1%}")

    # Test if h has distinct profile
    print("\n" + "=" * 60)
    print("KEY QUESTION: Does h have a distinct 'hazard' profile?")
    print("=" * 60)

    # If h is hazardous, we'd expect:
    # 1. h -> e transition elevated (escape to safety)
    # 2. h isolated from k (danger zone separate from energy)
    # 3. Different line position (maybe concentrated somewhere)

    h_to_e = results['h']['successor_kernel']['e']
    k_to_e = results['k']['successor_kernel']['e']
    e_to_e = results['e']['successor_kernel']['e']

    print(f"\n1. Flow to e (stability):")
    print(f"   h->e: {h_to_e:.1%}")
    print(f"   k->e: {k_to_e:.1%}")
    print(f"   e->e: {e_to_e:.1%}")

    h_to_k = results['h']['successor_kernel']['k']
    k_to_h = results['k']['successor_kernel']['h']

    print(f"\n2. h-k isolation:")
    print(f"   h -> k: {h_to_k:.1%}")
    print(f"   k -> h: {k_to_h:.1%}")

    print(f"\n3. Line position:")
    print(f"   k: {results['k']['line_position_mean']:.3f}")
    print(f"   h: {results['h']['line_position_mean']:.3f}")
    print(f"   e: {results['e']['line_position_mean']:.3f}")

    # Interpretation
    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)

    if h_to_e > k_to_e and h_to_k < k_to_h:
        print("FINDING: h shows elevated flow to e and reduced flow to k")
        print("This is CONSISTENT with hazard interpretation (h escapes to e, avoids k)")
    elif abs(h_to_e - k_to_e) < 0.05 and abs(h_to_k - k_to_h) < 0.05:
        print("FINDING: h and k have similar successor profiles")
        print("This CONTRADICTS hazard interpretation (h is not special)")
    else:
        print("FINDING: Mixed evidence - h has some distinct properties")

    # Save results
    output_path = Path(__file__).parent.parent / "results" / "t1_kernel_context_profiling.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
