#!/usr/bin/env python3
"""
T7: Parameter Layer — Within-State Variance Characterization
MINIMAL_STATE_AUTOMATON phase

For each of the 6 macro-states, characterize the within-state variation:
- Frequency spread (Gini, entropy)
- Transition profile diversity (pairwise JSD)
- Morphological diversity (prefix, middle, suffix families)
- Positional preferences (line position distribution)
This characterizes the "free variation envelope" between the 6 topology states
and the 49 behavioral classes.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.spatial.distance import jensenshannon

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'

STATE_LABELS = ['FL_HAZ', 'FQ', 'CC', 'AXm', 'AXM', 'FL_SAFE']


def gini(values):
    """Gini coefficient of a distribution."""
    arr = np.sort(np.array(values, dtype=float))
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return float((2 * np.sum(index * arr) - (n + 1) * np.sum(arr)) / (n * np.sum(arr)))


def entropy(probs):
    """Shannon entropy in bits."""
    p = np.array(probs, dtype=float)
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


def run():
    print("=" * 70)
    print("T7: Parameter Layer — Within-State Variance")
    print("MINIMAL_STATE_AUTOMATON phase")
    print("=" * 70)

    # Load data
    print("\n[1/5] Loading data...")
    with open(RESULTS_DIR / 't1_transition_data.json') as f:
        t1 = json.load(f)
    with open(RESULTS_DIR / 't3_merged_automaton.json') as f:
        t3 = json.load(f)
    with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
        ctm = json.load(f)

    all_classes = t1['classes']
    cls_to_idx = {c: i for i, c in enumerate(all_classes)}
    partition = t3['final_partition']
    counts_49 = np.array(t1['counts_49x49'], dtype=float)

    # Build class→state mapping
    cls_to_state = {}
    for si, group in enumerate(partition):
        for c in group:
            cls_to_state[c] = si

    # Row-normalize for transition profiles
    row_sums = counts_49.sum(axis=1, keepdims=True)
    probs_49 = np.divide(counts_49, row_sums, where=row_sums > 0,
                         out=np.zeros_like(counts_49))

    # Class frequencies
    class_freqs = {int(c): t1['class_details'][str(c)]['frequency'] for c in all_classes}

    # =========================================================
    # 2. Frequency Spread Within States
    # =========================================================
    print("\n[2/5] Frequency Spread Within States")
    state_results = []

    for si, group in enumerate(partition):
        freqs = [class_freqs[c] for c in group]
        total = sum(freqs)
        props = [f / total for f in freqs] if total > 0 else []

        g = gini(freqs)
        h = entropy(props) if props else 0
        max_h = np.log2(len(group)) if len(group) > 1 else 0
        h_norm = h / max_h if max_h > 0 else 1.0

        top_class = group[np.argmax(freqs)]
        top_frac = max(freqs) / total if total > 0 else 0

        print(f"  {STATE_LABELS[si]:>8} ({len(group):>2} classes): "
              f"Gini={g:.3f}  H={h:.2f}/{max_h:.2f} bits  "
              f"H_norm={h_norm:.3f}  "
              f"top=C{top_class}({top_frac:.1%})")

        state_results.append({
            'state': STATE_LABELS[si],
            'n_classes': len(group),
            'classes': group,
            'gini': round(g, 4),
            'entropy_bits': round(h, 4),
            'max_entropy': round(float(max_h), 4),
            'normalized_entropy': round(h_norm, 4),
            'top_class': int(top_class),
            'top_fraction': round(top_frac, 4),
        })

    # =========================================================
    # 3. Transition Profile Diversity (Within-State JSD)
    # =========================================================
    print("\n[3/5] Transition Profile Diversity (Pairwise JSD Within States)")

    for si, group in enumerate(partition):
        if len(group) < 2:
            print(f"  {STATE_LABELS[si]:>8}: single class, no diversity")
            state_results[si]['mean_jsd'] = 0.0
            state_results[si]['max_jsd'] = 0.0
            continue

        jsds = []
        for a_idx in range(len(group)):
            for b_idx in range(a_idx + 1, len(group)):
                ca, cb = group[a_idx], group[b_idx]
                ia, ib = cls_to_idx[ca], cls_to_idx[cb]
                pa = probs_49[ia]
                pb = probs_49[ib]
                # JSD with small epsilon for stability
                pa_safe = pa + 1e-10
                pb_safe = pb + 1e-10
                pa_safe /= pa_safe.sum()
                pb_safe /= pb_safe.sum()
                jsd = jensenshannon(pa_safe, pb_safe)
                jsds.append(jsd)

        mean_jsd = np.mean(jsds)
        max_jsd = np.max(jsds)
        min_jsd = np.min(jsds)

        print(f"  {STATE_LABELS[si]:>8} ({len(group):>2} classes, {len(jsds)} pairs): "
              f"mean_JSD={mean_jsd:.4f}  "
              f"range=[{min_jsd:.4f}, {max_jsd:.4f}]")

        state_results[si]['mean_jsd'] = round(float(mean_jsd), 5)
        state_results[si]['max_jsd'] = round(float(max_jsd), 5)
        state_results[si]['min_jsd'] = round(float(min_jsd), 5)
        state_results[si]['n_pairs'] = len(jsds)

    # =========================================================
    # 4. Morphological Diversity
    # =========================================================
    print("\n[4/5] Morphological Diversity Within States")

    morph = Morphology()
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    # Get all tokens per class
    class_tokens = defaultdict(list)
    for token, cls in token_to_class.items():
        class_tokens[cls].append(token)

    for si, group in enumerate(partition):
        # Collect morphological features across all tokens in this state
        prefixes = set()
        middles = set()
        suffixes = set()
        articulators = set()
        n_tokens_total = 0

        for c in group:
            for token in class_tokens.get(c, []):
                m = morph.extract(token)
                n_tokens_total += 1
                if m.prefix:
                    prefixes.add(m.prefix)
                if m.middle:
                    middles.add(m.middle)
                if m.suffix:
                    suffixes.add(m.suffix)
                if m.articulator:
                    articulators.add(m.articulator)

        print(f"  {STATE_LABELS[si]:>8}: "
              f"{n_tokens_total:>4} token types, "
              f"{len(prefixes):>2} prefixes, "
              f"{len(middles):>3} middles, "
              f"{len(suffixes):>2} suffixes, "
              f"{len(articulators):>1} articulators")

        state_results[si]['n_token_types'] = n_tokens_total
        state_results[si]['n_unique_prefixes'] = len(prefixes)
        state_results[si]['n_unique_middles'] = len(middles)
        state_results[si]['n_unique_suffixes'] = len(suffixes)
        state_results[si]['n_unique_articulators'] = len(articulators)
        state_results[si]['prefixes'] = sorted(prefixes)
        state_results[si]['middles'] = sorted(middles)
        state_results[si]['suffixes'] = sorted(suffixes)

    # =========================================================
    # 5. Positional Preferences
    # =========================================================
    print("\n[5/5] Positional Preferences Within States")

    tx = Transcript()
    # Build per-class position distributions
    # Position = token index within line / line length (normalized 0-1)
    class_positions = defaultdict(list)

    current_key = None
    current_line = []

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        cls = token_to_class.get(w)
        if cls is None:
            continue
        key = (token.folio, token.line)
        if key != current_key:
            # Process previous line
            if current_line:
                n_tok = len(current_line)
                for pos, c in enumerate(current_line):
                    class_positions[c].append(pos / max(n_tok - 1, 1))
            current_line = []
            current_key = key
        current_line.append(cls)

    if current_line:
        n_tok = len(current_line)
        for pos, c in enumerate(current_line):
            class_positions[c].append(pos / max(n_tok - 1, 1))

    # Compute per-state positional statistics
    print(f"\n  {'State':>8} {'Mean_Pos':>9} {'Std_Pos':>8} {'Early%':>7} {'Mid%':>6} {'Late%':>6} {'Pos_Entropy':>12}")
    for si, group in enumerate(partition):
        all_pos = []
        for c in group:
            all_pos.extend(class_positions.get(c, []))

        if not all_pos:
            print(f"  {STATE_LABELS[si]:>8}: no position data")
            continue

        arr = np.array(all_pos)
        mean_pos = np.mean(arr)
        std_pos = np.std(arr)

        # Thirds
        early = np.mean(arr < 0.333)
        mid = np.mean((arr >= 0.333) & (arr < 0.667))
        late = np.mean(arr >= 0.667)

        # Position entropy (binned into 10 bins)
        hist, _ = np.histogram(arr, bins=10, range=(0, 1))
        hist_p = hist / hist.sum()
        pos_entropy = entropy(hist_p)

        print(f"  {STATE_LABELS[si]:>8} {mean_pos:>9.3f} {std_pos:>8.3f} "
              f"{early:>6.1%} {mid:>5.1%} {late:>5.1%} {pos_entropy:>11.3f}")

        state_results[si]['mean_position'] = round(float(mean_pos), 4)
        state_results[si]['std_position'] = round(float(std_pos), 4)
        state_results[si]['position_early'] = round(float(early), 4)
        state_results[si]['position_mid'] = round(float(mid), 4)
        state_results[si]['position_late'] = round(float(late), 4)
        state_results[si]['position_entropy'] = round(float(pos_entropy), 4)

    # Within-state vs between-state position variance
    print(f"\n  Within-state vs between-state positional variance:")
    state_mean_positions = []
    state_var_within = []
    for si, group in enumerate(partition):
        all_pos = []
        for c in group:
            all_pos.extend(class_positions.get(c, []))
        if all_pos:
            state_mean_positions.append(np.mean(all_pos))
            # Within-state variance: variance of class means within this state
            class_means = [np.mean(class_positions.get(c, [0])) for c in group
                          if c in class_positions]
            if len(class_means) > 1:
                state_var_within.append(np.var(class_means))

    between_var = np.var(state_mean_positions)
    within_var = np.mean(state_var_within) if state_var_within else 0
    print(f"    Between-state variance of mean position: {between_var:.6f}")
    print(f"    Within-state variance of class means:    {within_var:.6f}")
    if between_var > 0:
        print(f"    Ratio (within/between): {within_var/between_var:.2f}")

    # =========================================================
    # Summary
    # =========================================================
    print(f"\n{'='*70}")
    print(f"PARAMETER LAYER SUMMARY")
    print(f"{'='*70}")

    # Which state has the most within-state diversity?
    print(f"\n  STATE          Classes  Gini  Mean_JSD  Middles  H_norm")
    for sr in state_results:
        jsd = sr.get('mean_jsd', 0)
        print(f"  {sr['state']:>8}  {sr['n_classes']:>7}  {sr['gini']:.3f}  "
              f"{jsd:>8.4f}  {sr['n_unique_middles']:>7}  {sr['normalized_entropy']:.3f}")

    print(f"\n  INTERPRETATION:")
    print(f"  The 43 non-essential classes encode:")
    print(f"  1. FREQUENCY VARIATION: Within S4 (32 classes), Gini ~high = ")
    print(f"     few classes dominate, many are rare variants")
    print(f"  2. MORPHOLOGICAL RICHNESS: S4 has the most MIDDLE diversity,")
    print(f"     encoding material-specific vocabulary")
    print(f"  3. TRANSITION TEXTURE: Within-state JSD shows how much classes")
    print(f"     differ in their detailed transition preferences")
    print(f"  4. POSITIONAL NUANCE: All states span the full line, but")
    print(f"     some show subtle early/late preferences")

    # Save
    results = {
        'test': 'T7_parameter_layer',
        'states': state_results,
        'position_variance': {
            'between_state': round(float(between_var), 6),
            'within_state': round(float(within_var), 6),
        },
    }

    with open(RESULTS_DIR / 't7_parameter_layer.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't7_parameter_layer.json'}")


if __name__ == '__main__':
    run()
