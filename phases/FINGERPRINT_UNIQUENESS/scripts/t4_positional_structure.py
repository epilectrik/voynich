#!/usr/bin/env python3
"""
T4: Positional Structure Null Model (F9)
FINGERPRINT_UNIQUENESS phase

Tests: How rare is the boundary-constrained-free-interior pattern?

F9: Zone exclusivity (192/334 tokens zone-exclusive, 2.72x shuffle) (C956, C964)
    + Entropy gradient (low boundary H, high interior H)
    + MI(role, position) (strong positional grammar)

Enhanced per expert: Tests not just "is there boundary bias?" but
"is the STRENGTH of boundary constraint vs interior freedom unusual
given N=49 classes and ~23K tokens?"

Two null ensembles:
  NULL-J: Within-line token shuffle (preserves line lengths + token freq)
  NULL-K: Position-role shuffle (shuffle role assignments, preserve positions)
"""

import sys
import json
import time
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'
N_SAMPLES = 5000
RNG = np.random.default_rng(42)

# Position zones (relative to line)
BOUNDARY_POS = {0, -1}  # First and last position
MIN_TOKEN_FREQ = 5  # Minimum frequency to count as "common"


# ============================================================
# DATA LOADING
# ============================================================

def load_class_map():
    path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path) as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
    class_to_role[17] = 'CORE_CONTROL'

    all_classes = set(token_to_class.values())
    EN = ({8} | set(range(31, 50)) - {7, 30, 38, 40}) & all_classes
    FL = {7, 30, 38, 40}
    CC = {10, 11, 12}
    FQ = {9, 13, 14, 23}
    AX = all_classes - EN - FL - CC - FQ

    def get_role(cls):
        if cls in CC: return 'CC'
        if cls in FL: return 'FL'
        if cls in FQ: return 'FQ'
        if cls in EN: return 'EN'
        if cls in AX: return 'AX'
        return 'UN'

    return token_to_class, class_to_role, get_role


def load_b_lines():
    """Load Currier B tokens organized by line with positional info."""
    tx = Transcript()
    token_to_class, class_to_role, get_role = load_class_map()

    lines = defaultdict(list)
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        cls = token_to_class.get(w)
        if cls is None:
            continue
        role = get_role(cls)
        lines[(token.folio, token.line)].append({
            'word': w,
            'cls': cls,
            'role': role,
        })

    return dict(lines), token_to_class, get_role


# ============================================================
# F9: POSITIONAL METRICS
# ============================================================

def compute_zone_exclusivity(lines, min_freq=MIN_TOKEN_FREQ):
    """Compute fraction of common tokens that are zone-exclusive.

    Zone-exclusive: a token appears ONLY in boundary positions or ONLY in
    interior positions across the entire corpus.

    C956: 192/334 common tokens zone-exclusive (2.72x shuffle).
    """
    # Count token occurrences by zone
    token_boundary = Counter()  # tokens in boundary positions
    token_interior = Counter()  # tokens in interior positions

    for line_tokens in lines.values():
        n = len(line_tokens)
        if n < 3:
            # Too short to have meaningful interior
            continue
        for i, t in enumerate(line_tokens):
            w = t['word']
            if i == 0 or i == n - 1:
                token_boundary[w] += 1
            else:
                token_interior[w] += 1

    # Common tokens (appear >= min_freq total)
    all_tokens = set(token_boundary.keys()) | set(token_interior.keys())
    common_tokens = set()
    for w in all_tokens:
        total = token_boundary.get(w, 0) + token_interior.get(w, 0)
        if total >= min_freq:
            common_tokens.add(w)

    if not common_tokens:
        return 0.0, 0, 0

    # Zone-exclusive: appears in exactly one zone
    n_exclusive = 0
    for w in common_tokens:
        in_boundary = token_boundary.get(w, 0) > 0
        in_interior = token_interior.get(w, 0) > 0
        if in_boundary != in_interior:  # XOR = exclusive to one zone
            n_exclusive += 1

    exclusivity = n_exclusive / len(common_tokens)
    return exclusivity, n_exclusive, len(common_tokens)


def compute_entropy_gradient(lines):
    """Compute entropy H(token | position) at each relative position.

    Boundary positions should have LOWER entropy (restricted vocabulary),
    interior positions should have HIGHER entropy (open vocabulary).
    """
    # Normalize position to relative (0=first, 1=last, middle normalized)
    # Use absolute positions: 0, 1, 2, ..., -3, -2, -1
    pos_tokens = defaultdict(Counter)  # position -> token counter

    for line_tokens in lines.values():
        n = len(line_tokens)
        if n < 3:
            continue
        for i, t in enumerate(line_tokens):
            # Use first 3 and last 3 positions, rest = "interior"
            if i <= 2:
                pos = i
            elif i >= n - 3:
                pos = -(n - i)
            else:
                pos = 'interior'
            pos_tokens[pos][t['word']] += 1

    # Compute entropy at each position
    entropies = {}
    for pos, counter in sorted(pos_tokens.items(), key=lambda x: str(x[0])):
        total = sum(counter.values())
        if total == 0:
            continue
        probs = np.array(list(counter.values())) / total
        H = -np.sum(probs * np.log2(probs + 1e-15))
        entropies[str(pos)] = {'entropy': round(float(H), 3), 'n_tokens': total,
                                'n_types': len(counter)}

    # Gradient: boundary H vs interior H
    boundary_H = []
    interior_H = []
    for pos, data in entropies.items():
        if pos in ['0', '-1']:
            boundary_H.append(data['entropy'])
        elif pos == 'interior':
            interior_H.append(data['entropy'])

    gradient = 0.0
    if boundary_H and interior_H:
        gradient = np.mean(interior_H) - np.mean(boundary_H)

    return entropies, gradient


def compute_role_position_mi(lines):
    """Compute mutual information between role and position-in-line.

    Higher MI = stronger positional grammar. C956 documents 192/334
    zone-exclusive tokens, implying strong role-position coupling.
    """
    # Use 3 zones: FIRST (pos 0), LAST (pos -1), MIDDLE (rest)
    joint = Counter()  # (role, zone) counts
    role_margin = Counter()
    zone_margin = Counter()

    for line_tokens in lines.values():
        n = len(line_tokens)
        for i, t in enumerate(line_tokens):
            if i == 0:
                zone = 'FIRST'
            elif i == n - 1:
                zone = 'LAST'
            else:
                zone = 'MID'
            role = t['role']
            joint[(role, zone)] += 1
            role_margin[role] += 1
            zone_margin[zone] += 1

    total = sum(joint.values())
    if total == 0:
        return 0.0

    mi = 0.0
    for (role, zone), count in joint.items():
        p_rz = count / total
        p_r = role_margin[role] / total
        p_z = zone_margin[zone] / total
        if p_rz > 0 and p_r > 0 and p_z > 0:
            mi += p_rz * np.log2(p_rz / (p_r * p_z))

    return float(mi)


def compute_fingerprint(lines):
    excl, n_excl, n_common = compute_zone_exclusivity(lines)
    entropies, gradient = compute_entropy_gradient(lines)
    mi = compute_role_position_mi(lines)

    return {
        'zone_exclusivity': excl,
        'n_exclusive': n_excl,
        'n_common': n_common,
        'entropy_gradient': gradient,
        'entropies': entropies,
        'role_position_mi': mi,
    }


# ============================================================
# NULL ENSEMBLE GENERATORS
# ============================================================

def generate_null_j(lines, rng):
    """NULL-J: Within-line token shuffle. Preserves line lengths and global token freq."""
    new_lines = {}
    for key, line_tokens in lines.items():
        shuffled = list(line_tokens)
        rng.shuffle(shuffled)
        new_lines[key] = shuffled
    return new_lines


def generate_null_k(lines, rng):
    """NULL-K: Cross-line position shuffle. Shuffle tokens at the SAME position
    across lines. This preserves positional structure but randomizes which
    token gets which position.
    """
    # Group tokens by position
    max_len = max(len(lt) for lt in lines.values())
    pos_pools = defaultdict(list)  # position -> list of (key, token_dict)

    for key, line_tokens in lines.items():
        n = len(line_tokens)
        for i, t in enumerate(line_tokens):
            # Normalize: first 2 positions, last 2, rest = interior
            if i <= 1:
                norm_pos = i
            elif i >= n - 2:
                norm_pos = -(n - i)
            else:
                norm_pos = 'mid'
            pos_pools[norm_pos].append((key, i, t))

    # Shuffle within each position pool
    new_lines = {key: list(lt) for key, lt in lines.items()}

    for pos, pool in pos_pools.items():
        tokens_only = [t for _, _, t in pool]
        rng.shuffle(tokens_only)
        for idx, (key, line_pos, _) in enumerate(pool):
            new_lines[key][line_pos] = tokens_only[idx]

    return new_lines


# ============================================================
# MAIN
# ============================================================

def run():
    t_start = time.time()
    print("=" * 70)
    print("T4: Positional Structure Null Model (F9)")
    print("FINGERPRINT_UNIQUENESS phase")
    print("=" * 70)

    # 1. Load data
    print("\n[1/4] Loading data...")
    lines, token_to_class, get_role = load_b_lines()
    print(f"  Lines: {len(lines)}")
    total_tokens = sum(len(lt) for lt in lines.values())
    print(f"  Tokens: {total_tokens}")

    # 2. Observed fingerprint
    print("\n[2/4] Computing observed fingerprint...")
    obs = compute_fingerprint(lines)

    print(f"  F9 - Zone exclusivity: {obs['zone_exclusivity']:.3f} "
          f"({obs['n_exclusive']}/{obs['n_common']} common tokens)")
    print(f"  F9 - Entropy gradient: {obs['entropy_gradient']:.3f} bits "
          f"(interior - boundary)")
    print(f"  F9 - Role-position MI: {obs['role_position_mi']:.4f} bits")
    print(f"  Entropy by position:")
    for pos, data in sorted(obs['entropies'].items(), key=lambda x: str(x[0])):
        print(f"    pos={pos}: H={data['entropy']:.3f} "
              f"({data['n_types']} types, {data['n_tokens']} tokens)")

    # 3. Null ensembles
    ensemble_results = {}

    for step, (label, gen_fn) in enumerate([
        ('NULL_J_within_line', lambda rng: generate_null_j(lines, rng)),
        ('NULL_K_cross_line', lambda rng: generate_null_k(lines, rng)),
    ], 3):
        print(f"\n[{step}/4] Running {label} ({N_SAMPLES} samples)...")
        t_ens = time.time()

        null_excl = np.zeros(N_SAMPLES)
        null_grad = np.zeros(N_SAMPLES)
        null_mi = np.zeros(N_SAMPLES)

        for s in range(N_SAMPLES):
            nl = gen_fn(RNG)
            fp = compute_fingerprint(nl)
            null_excl[s] = fp['zone_exclusivity']
            null_grad[s] = fp['entropy_gradient']
            null_mi[s] = fp['role_position_mi']

            if (s + 1) % 1000 == 0:
                elapsed = time.time() - t_ens
                rate = (s + 1) / elapsed
                print(f"    {s + 1}/{N_SAMPLES} ({rate:.1f}/s, "
                      f"ETA {(N_SAMPLES - s - 1) / rate:.0f}s)")

        dt = time.time() - t_ens

        p_excl = float(np.mean(null_excl >= obs['zone_exclusivity']))
        p_grad = float(np.mean(null_grad >= obs['entropy_gradient']))
        p_mi = float(np.mean(null_mi >= obs['role_position_mi']))
        p_joint = float(np.mean(
            (null_excl >= obs['zone_exclusivity']) &
            (null_grad >= obs['entropy_gradient']) &
            (null_mi >= obs['role_position_mi'])
        ))

        # Compute exclusivity ratio vs null mean
        excl_ratio = obs['zone_exclusivity'] / np.mean(null_excl) if np.mean(null_excl) > 0 else float('inf')

        ensemble_results[label] = {
            'p_exclusivity': p_excl,
            'p_gradient': p_grad,
            'p_mi': p_mi,
            'p_joint_F9': p_joint,
            'null_excl_mean': round(float(np.mean(null_excl)), 4),
            'null_excl_std': round(float(np.std(null_excl)), 4),
            'null_grad_mean': round(float(np.mean(null_grad)), 4),
            'null_mi_mean': round(float(np.mean(null_mi)), 4),
            'exclusivity_ratio': round(float(excl_ratio), 2),
            'time_seconds': round(dt, 1),
        }

        print(f"  Completed in {dt:.1f}s")
        print(f"  P(exclusivity >= {obs['zone_exclusivity']:.3f}): {p_excl:.4f} "
              f"[null: {np.mean(null_excl):.3f}, ratio: {excl_ratio:.2f}x]")
        print(f"  P(gradient >= {obs['entropy_gradient']:.3f}): {p_grad:.4f} "
              f"[null: {np.mean(null_grad):.3f}]")
        print(f"  P(MI >= {obs['role_position_mi']:.4f}): {p_mi:.4f} "
              f"[null: {np.mean(null_mi):.4f}]")
        print(f"  P(joint F9): {p_joint:.6f}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\nObserved fingerprint:")
    print(f"  Zone exclusivity:    {obs['zone_exclusivity']:.3f} "
          f"({obs['n_exclusive']}/{obs['n_common']})")
    print(f"  Entropy gradient:    {obs['entropy_gradient']:.3f} bits")
    print(f"  Role-position MI:    {obs['role_position_mi']:.4f} bits")

    print(f"\nPer-ensemble joint p-values:")
    for label, res in ensemble_results.items():
        print(f"  {label}: {res['p_joint_F9']:.6f} "
              f"(exclusivity ratio: {res['exclusivity_ratio']}x)")

    best_p = min(r['p_joint_F9'] for r in ensemble_results.values())
    worst_p = max(r['p_joint_F9'] for r in ensemble_results.values())

    if worst_p < 0.01:
        verdict = "RARE"
    elif worst_p < 0.05:
        verdict = "UNCOMMON"
    else:
        verdict = "NOT_RARE"
    print(f"\nT4 Verdict (worst-case p = {worst_p:.6f}): {verdict}")

    # Save
    results = {
        'test': 'T4_positional_structure',
        'properties': ['F9_boundary_constrained_free_interior'],
        'observed': {
            'zone_exclusivity': obs['zone_exclusivity'],
            'n_exclusive': obs['n_exclusive'],
            'n_common': obs['n_common'],
            'entropy_gradient': obs['entropy_gradient'],
            'role_position_mi': obs['role_position_mi'],
            'entropies': obs['entropies'],
        },
        'ensembles': ensemble_results,
        'verdict': verdict,
        'best_joint_p': best_p,
        'worst_joint_p': worst_p,
        'n_samples': N_SAMPLES,
        'n_lines': len(lines),
        'n_tokens': total_tokens,
        'elapsed_seconds': round(time.time() - t_start, 1),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 't4_positional.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")
    print(f"Total time: {time.time() - t_start:.1f}s")

    return results


if __name__ == '__main__':
    run()
