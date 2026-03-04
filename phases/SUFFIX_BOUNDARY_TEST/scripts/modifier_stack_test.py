"""
Phase 505+: Modifier Stack Structure Test
==========================================
Investigates the internal structure of the modifier stack in compound MIDDLEs.

C1393 found compound MIDDLEs follow HEAD + MODIFIER* + TERMINAL slot grammar.
This test probes the modifier stack: depth, co-occurrence, ordering, and
dependency on HEAD/TERMINAL identity.

Six tests:
  1. Compound Size Distribution — atom counts and modifier depth
  2. Modifier Co-occurrence Matrix — which modifiers appear together?
  3. Modifier Ordering — is there consistent internal ordering?
  4. Extended Modifier Sequences — what 3+ modifier stacks look like
  5. Modifier Count by HEAD — does HEAD predict modifier depth?
  6. Modifier Count by TERMINAL — does TERMINAL predict modifier depth?

Output: phases/SUFFIX_BOUNDARY_TEST/results/modifier_stack_test.json
"""

import sys
import os
import json
import math
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

# ============================================================
# C1393 Atom Role Sets
# ============================================================
HEAD_ATOMS = {'a', 'e', 'o'}
MOD_ATOMS = {'p', 'c', 'i', 'f', 'd', 's'}
TERM_ATOMS = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE_ATOMS = {'k', 't'}

ALL_ATOMS = HEAD_ATOMS | MOD_ATOMS | TERM_ATOMS | FREE_ATOMS


def atom_class(ch):
    """Return the atom class for a single character."""
    if ch in HEAD_ATOMS:
        return 'HEAD'
    elif ch in MOD_ATOMS:
        return 'MOD'
    elif ch in TERM_ATOMS:
        return 'TERM'
    elif ch in FREE_ATOMS:
        return 'FREE'
    else:
        return 'UNK'


def classify_position(mid):
    """
    Classify each character in a MIDDLE by its POSITIONAL role.

    Returns list of dicts with:
      - char: the character
      - atom_class: HEAD/MOD/TERM/FREE/UNK (intrinsic class)
      - pos_role: HEAD/MOD/TERM (positional role based on position)

    Rules:
      - First atom: HEAD role if HEAD or FREE class; else MOD role
      - Last atom: TERM role if TERM or FREE class; else MOD role
      - Middle atoms: MOD role regardless of class
      - Single-atom MIDDLEs: classified by atom class only
    """
    if not mid:
        return []

    chars = list(mid)
    n = len(chars)

    if n == 1:
        ac = atom_class(chars[0])
        return [{'char': chars[0], 'atom_class': ac, 'pos_role': ac}]

    result = []
    for idx, ch in enumerate(chars):
        ac = atom_class(ch)

        if idx == 0:
            # First position: HEAD if HEAD or FREE
            if ac in ('HEAD', 'FREE'):
                pos_role = 'HEAD'
            else:
                pos_role = 'MOD'
        elif idx == n - 1:
            # Last position: TERM if TERM or FREE
            if ac in ('TERM', 'FREE'):
                pos_role = 'TERM'
            else:
                pos_role = 'MOD'
        else:
            # Interior positions: always MOD
            pos_role = 'MOD'

        result.append({
            'char': ch,
            'atom_class': ac,
            'pos_role': pos_role,
        })

    return result


def get_modifier_atoms(mid):
    """
    Extract the modifier atoms from a compound MIDDLE.

    Returns a list of characters in modifier position (interior atoms,
    plus edge atoms that don't match their expected role).
    """
    classified = classify_position(mid)
    return [c for c in classified if c['pos_role'] == 'MOD']


# ============================================================
# Data Loading
# ============================================================
print("=" * 70)
print("MODIFIER STACK STRUCTURE TEST")
print("=" * 70)

tx = Transcript()
morph = Morphology()

# Collect all Currier B tokens with morphology
# Exclude labels, uncertain tokens, empty words
tokens_b = []
for token in tx.currier_b():
    if '*' in token.word or not token.word.strip():
        continue
    if token.placement.startswith('L'):
        continue
    m = morph.extract(token.word)
    if m.middle and len(m.middle) >= 1:
        tokens_b.append({
            'word': token.word,
            'folio': token.folio,
            'middle': m.middle,
        })

print(f"Loaded {len(tokens_b)} Currier B tokens with valid MIDDLEs")

# Build MIDDLE -> count and MIDDLE -> set of unique types
middle_counts = Counter(t['middle'] for t in tokens_b)
unique_middles = set(middle_counts.keys())
print(f"Unique MIDDLEs: {len(unique_middles)}")

# Filter to compound MIDDLEs (2+ chars)
compound_middles = {m for m in unique_middles if len(m) >= 2}
compound_tokens = [t for t in tokens_b if len(t['middle']) >= 2]
print(f"Compound MIDDLEs (2+ chars): {len(compound_middles)} types, {len(compound_tokens)} tokens")

# Verify all chars are known atoms
unk_chars = set()
for mid in compound_middles:
    for ch in mid:
        if ch not in ALL_ATOMS:
            unk_chars.add(ch)
if unk_chars:
    print(f"WARNING: Unknown characters in MIDDLEs: {sorted(unk_chars)}")
else:
    print("All characters in compound MIDDLEs are known atoms.")

results = {}

# ============================================================
# TEST 1: COMPOUND SIZE DISTRIBUTION
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: COMPOUND SIZE DISTRIBUTION")
print("=" * 70)

# Count by number of atoms
size_type_counts = Counter()
size_token_counts = Counter()
modifier_depth_type = Counter()  # number of modifiers per compound (types)
modifier_depth_token = Counter()  # number of modifiers per compound (tokens)

for mid in compound_middles:
    n_atoms = len(mid)
    size_type_counts[n_atoms] += 1
    size_token_counts[n_atoms] += middle_counts[mid]

    mods = get_modifier_atoms(mid)
    n_mods = len(mods)
    modifier_depth_type[n_mods] += 1
    modifier_depth_token[n_mods] += middle_counts[mid]

print("\n--- Compound size distribution ---")
print(f"{'Size':>6s}  {'Types':>8s}  {'%Types':>8s}  {'Tokens':>8s}  {'%Tokens':>8s}")
total_types = sum(size_type_counts.values())
total_tokens = sum(size_token_counts.values())
for size in sorted(size_type_counts.keys()):
    tc = size_type_counts[size]
    tkc = size_token_counts[size]
    print(f"{size:6d}  {tc:8d}  {tc/total_types:8.1%}  {tkc:8d}  {tkc/total_tokens:8.1%}")

print("\n--- Modifier depth distribution ---")
print(f"{'#Mods':>6s}  {'Types':>8s}  {'%Types':>8s}  {'Tokens':>8s}  {'%Tokens':>8s}")
for n_mods in sorted(modifier_depth_type.keys()):
    tc = modifier_depth_type[n_mods]
    tkc = modifier_depth_token[n_mods]
    print(f"{n_mods:6d}  {tc:8d}  {tc/total_types:8.1%}  {tkc:8d}  {tkc/total_tokens:8.1%}")

# Show examples for each depth
print("\n--- Examples by modifier depth ---")
for n_mods in sorted(modifier_depth_type.keys()):
    examples = []
    for mid in sorted(compound_middles, key=lambda m: -middle_counts[m]):
        mods = get_modifier_atoms(mid)
        if len(mods) == n_mods:
            classified = classify_position(mid)
            roles_str = ''.join(c['pos_role'][0] for c in classified)
            atom_classes_str = ''.join(c['atom_class'][0] for c in classified)
            examples.append(f"{mid}({roles_str}/{atom_classes_str}, n={middle_counts[mid]})")
            if len(examples) >= 5:
                break
    print(f"  {n_mods} modifiers: {', '.join(examples)}")

# Cross-tabulation: size vs modifier count
print("\n--- Size x Modifier count (types) ---")
size_mod_cross = defaultdict(Counter)
for mid in compound_middles:
    n_atoms = len(mid)
    mods = get_modifier_atoms(mid)
    n_mods = len(mods)
    size_mod_cross[n_atoms][n_mods] += 1

all_mod_counts = sorted(set(n for counts in size_mod_cross.values() for n in counts))
header = f"{'Size':>6s}" + "".join(f"  {f'{n}mod':>6s}" for n in all_mod_counts)
print(header)
for size in sorted(size_mod_cross.keys()):
    row = f"{size:6d}"
    for n_mods in all_mod_counts:
        row += f"  {size_mod_cross[size][n_mods]:6d}"
    print(row)

results['test1'] = {
    'size_distribution_types': {str(k): v for k, v in sorted(size_type_counts.items())},
    'size_distribution_tokens': {str(k): v for k, v in sorted(size_token_counts.items())},
    'modifier_depth_types': {str(k): v for k, v in sorted(modifier_depth_type.items())},
    'modifier_depth_tokens': {str(k): v for k, v in sorted(modifier_depth_token.items())},
    'total_compound_types': total_types,
    'total_compound_tokens': total_tokens,
}


# ============================================================
# TEST 2: MODIFIER CO-OCCURRENCE MATRIX
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: MODIFIER CO-OCCURRENCE MATRIX")
print("=" * 70)

# Count individual modifier atom frequencies
mod_atom_freq_type = Counter()  # How many compound types contain each modifier atom
mod_atom_freq_token = Counter()  # Weighted by frequency

# Count modifier co-occurrence
mod_pair_cooc_type = Counter()
mod_pair_cooc_token = Counter()

# Track which compounds have 2+ modifiers
compounds_with_2plus_mods = []

for mid in compound_middles:
    mods = get_modifier_atoms(mid)
    mod_chars = [m['char'] for m in mods]

    # Unique modifier atoms present (for co-occurrence, count each type once per MIDDLE)
    unique_mod_chars = set(mod_chars)

    for mc in unique_mod_chars:
        mod_atom_freq_type[mc] += 1
        mod_atom_freq_token[mc] += middle_counts[mid]

    if len(unique_mod_chars) >= 2:
        compounds_with_2plus_mods.append(mid)
        for pair in combinations(sorted(unique_mod_chars), 2):
            mod_pair_cooc_type[pair] += 1
            mod_pair_cooc_token[pair] += middle_counts[mid]

# Also count compounds with repeated modifier atoms (e.g., ii, iii)
repeated_mods = Counter()
for mid in compound_middles:
    mods = get_modifier_atoms(mid)
    mod_chars = [m['char'] for m in mods]
    char_counts = Counter(mod_chars)
    for ch, cnt in char_counts.items():
        if cnt >= 2:
            repeated_mods[ch] += 1

n_compounds_total = len(compound_middles)

print(f"\nCompounds with 2+ distinct modifier atoms: {len(compounds_with_2plus_mods)}")
print(f"Compounds with repeated modifier atoms:")
for ch, cnt in repeated_mods.most_common():
    print(f"  {ch}: {cnt} types have {ch} repeated")

# Individual modifier atom frequency
print(f"\n--- Modifier atom frequencies (among {n_compounds_total} compound types) ---")
all_mod_chars = sorted(MOD_ATOMS)
for mc in all_mod_chars:
    tc = mod_atom_freq_type.get(mc, 0)
    tkc = mod_atom_freq_token.get(mc, 0)
    print(f"  {mc}: {tc:5d} types ({tc/n_compounds_total:.1%}), {tkc:6d} tokens")

# Co-occurrence matrix
print(f"\n--- Modifier co-occurrence matrix (types) ---")
print(f"  Obs/Exp ratios (expected = P(mod1) * P(mod2) * total_compounds)")
header = "      " + "  ".join(f"{mc:>6s}" for mc in all_mod_chars)
print(header)

cooc_results = {}
for mc1 in all_mod_chars:
    row = f"  {mc1:3s}  "
    for mc2 in all_mod_chars:
        if mc1 >= mc2:
            row += f"{'---':>6s}  "
            continue
        pair = (mc1, mc2)
        obs = mod_pair_cooc_type.get(pair, 0)
        p1 = mod_atom_freq_type.get(mc1, 0) / n_compounds_total
        p2 = mod_atom_freq_type.get(mc2, 0) / n_compounds_total
        exp = p1 * p2 * n_compounds_total
        ratio = obs / exp if exp > 0 else float('inf')

        cooc_results[f"{mc1},{mc2}"] = {
            'observed': obs,
            'expected': round(exp, 2),
            'ratio': round(ratio, 2),
            'p1': round(p1, 4),
            'p2': round(p2, 4),
        }

        if obs == 0:
            row += f"{'0':>6s}  "
        else:
            row += f"{ratio:6.2f}  "
    print(row)

# Print notable pairs
print("\n--- Notable co-occurrence pairs ---")
for pair_key, vals in sorted(cooc_results.items(), key=lambda x: -x[1]['ratio']):
    if vals['observed'] >= 2:
        label = "ENRICHED" if vals['ratio'] > 2.0 else ("DEPLETED" if vals['ratio'] < 0.5 else "EXPECTED")
        print(f"  ({pair_key}): obs={vals['observed']}, exp={vals['expected']:.1f}, "
              f"ratio={vals['ratio']:.2f} [{label}]")

results['test2'] = {
    'n_compounds_with_2plus_distinct_mods': len(compounds_with_2plus_mods),
    'repeated_modifier_atoms': {ch: cnt for ch, cnt in repeated_mods.most_common()},
    'modifier_atom_frequencies_types': {mc: mod_atom_freq_type.get(mc, 0) for mc in all_mod_chars},
    'modifier_atom_frequencies_tokens': {mc: mod_atom_freq_token.get(mc, 0) for mc in all_mod_chars},
    'co_occurrence': cooc_results,
}


# ============================================================
# TEST 3: MODIFIER ORDERING
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: MODIFIER ORDERING")
print("=" * 70)

# For compounds with 2+ modifier atoms in modifier position,
# check which comes first
ordered_pair_counts_type = Counter()  # (X,Y) where X appears before Y
ordered_pair_counts_token = Counter()

for mid in compound_middles:
    mods = get_modifier_atoms(mid)
    mod_chars = [m['char'] for m in mods]

    if len(mod_chars) < 2:
        continue

    # For all pairs of modifier characters, record ordering
    for i in range(len(mod_chars)):
        for j in range(i+1, len(mod_chars)):
            pair = (mod_chars[i], mod_chars[j])
            ordered_pair_counts_type[pair] += 1
            ordered_pair_counts_token[pair] += middle_counts[mid]

# Build ordering analysis
print("\n--- Modifier ordering (X before Y) ---")
print(f"{'Pair':>8s}  {'X>Y types':>10s}  {'Y>X types':>10s}  {'Asym':>8s}  {'X>Y tok':>10s}  {'Y>X tok':>10s}")

ordering_results = {}
all_ordered_pairs = set()
for (a, b), cnt in ordered_pair_counts_type.items():
    all_ordered_pairs.add(tuple(sorted((a, b))))

for pair in sorted(all_ordered_pairs):
    a, b = pair
    ab_types = ordered_pair_counts_type.get((a, b), 0)
    ba_types = ordered_pair_counts_type.get((b, a), 0)
    ab_tokens = ordered_pair_counts_token.get((a, b), 0)
    ba_tokens = ordered_pair_counts_token.get((b, a), 0)

    total = ab_types + ba_types
    if total == 0:
        continue

    asym = max(ab_types, ba_types) / max(min(ab_types, ba_types), 1)
    dominant = a if ab_types >= ba_types else b

    label = f"{a},{b}"
    print(f"  {label:>6s}  {ab_types:10d}  {ba_types:10d}  {asym:8.1f}x  {ab_tokens:10d}  {ba_tokens:10d}  "
          f"[{dominant} first]")

    ordering_results[label] = {
        'ab_types': ab_types,
        'ba_types': ba_types,
        'ab_tokens': ab_tokens,
        'ba_tokens': ba_tokens,
        'asymmetry_ratio': round(asym, 2),
        'dominant_first': dominant,
    }

# Mean position of each modifier within the modifier stack
print("\n--- Mean modifier position within stack (0=first modifier, 1=last) ---")
mod_positions = defaultdict(list)  # char -> list of normalized positions within stack

for mid in compound_middles:
    mods = get_modifier_atoms(mid)
    if len(mods) < 2:
        # Single modifier: position = 0 by default, skip for ordering
        continue
    mod_chars = [m['char'] for m in mods]
    n_mods = len(mod_chars)
    for idx, ch in enumerate(mod_chars):
        # Normalize position: 0 = first, 1 = last
        norm_pos = idx / (n_mods - 1) if n_mods > 1 else 0.5
        # Weight by frequency
        for _ in range(middle_counts[mid]):
            mod_positions[ch].append(norm_pos)

print(f"{'Atom':>6s}  {'Mean pos':>10s}  {'N obs':>8s}  {'Rank':>6s}")
mod_mean_positions = {}
for ch in sorted(MOD_ATOMS):
    positions = mod_positions.get(ch, [])
    if positions:
        mean_pos = np.mean(positions)
        mod_mean_positions[ch] = mean_pos
    else:
        mod_mean_positions[ch] = None

# Rank by mean position (lower = earlier)
ranked = sorted([(ch, pos) for ch, pos in mod_mean_positions.items() if pos is not None],
                key=lambda x: x[1])
for rank_idx, (ch, pos) in enumerate(ranked, 1):
    n_obs = len(mod_positions.get(ch, []))
    print(f"  {ch:>4s}  {pos:10.3f}  {n_obs:8d}  {rank_idx:6d}")

inferred_order = [ch for ch, _ in ranked]
print(f"\nInferred modifier ordering (earliest to latest): {' > '.join(inferred_order)}")

results['test3'] = {
    'ordered_pairs': ordering_results,
    'mean_positions': {ch: round(pos, 4) if pos is not None else None
                       for ch, pos in mod_mean_positions.items()},
    'inferred_order': inferred_order,
}


# ============================================================
# TEST 4: EXTENDED MODIFIER SEQUENCES
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: EXTENDED MODIFIER SEQUENCES (3+ modifier atoms)")
print("=" * 70)

extended_mod_examples = []
mod_repeat_counts = Counter()  # e.g., 'ii', 'iii'
heterogeneous_stacks = []

for mid in sorted(compound_middles, key=lambda m: -middle_counts[m]):
    mods = get_modifier_atoms(mid)
    mod_chars = [m['char'] for m in mods]

    if len(mod_chars) < 3:
        continue

    classified = classify_position(mid)
    roles_str = ''.join(c['pos_role'][0] for c in classified)
    atom_classes_str = ''.join(c['atom_class'][0] for c in classified)

    mod_str = ''.join(mod_chars)
    unique_mods = set(mod_chars)
    is_homogeneous = len(unique_mods) == 1

    entry = {
        'middle': mid,
        'tokens': middle_counts[mid],
        'modifier_sequence': mod_str,
        'n_modifiers': len(mod_chars),
        'unique_mod_atoms': sorted(unique_mods),
        'homogeneous': is_homogeneous,
        'pos_pattern': roles_str,
        'atom_pattern': atom_classes_str,
    }
    extended_mod_examples.append(entry)

    if not is_homogeneous:
        heterogeneous_stacks.append(entry)

# Check for repeated modifiers (same char 2+ times in modifier position)
for mid in compound_middles:
    mods = get_modifier_atoms(mid)
    mod_chars = [m['char'] for m in mods]
    char_counts = Counter(mod_chars)
    for ch, cnt in char_counts.items():
        if cnt >= 2:
            mod_repeat_counts[(ch, cnt)] += 1

print(f"\nCompounds with 3+ modifier atoms: {len(extended_mod_examples)} types")

print("\n--- Top 20 by frequency ---")
for entry in extended_mod_examples[:20]:
    print(f"  {entry['middle']:12s}  mods={entry['modifier_sequence']:6s}  "
          f"n={entry['tokens']:5d}  pattern={entry['pos_pattern']}  "
          f"classes={entry['atom_pattern']}  "
          f"{'HOMO' if entry['homogeneous'] else 'HETERO':5s}  "
          f"unique_mods={entry['unique_mod_atoms']}")

# Modifier repetition patterns
print(f"\n--- Modifier repetition patterns ---")
for (ch, cnt), n_types in mod_repeat_counts.most_common():
    print(f"  {ch}x{cnt}: {n_types} compound types")

# Heterogeneous stacks
print(f"\n--- Heterogeneous modifier stacks (multiple distinct mod atoms): {len(heterogeneous_stacks)} ---")
for entry in heterogeneous_stacks[:20]:
    print(f"  {entry['middle']:12s}  mods={entry['modifier_sequence']:6s}  "
          f"n={entry['tokens']:5d}  unique_mods={entry['unique_mod_atoms']}")

# Most common 3+ modifier sequences
mod_seq_counts = Counter()
for entry in extended_mod_examples:
    mod_seq_counts[entry['modifier_sequence']] += 1

print(f"\n--- Most common 3+ modifier sequences ---")
for seq, cnt in mod_seq_counts.most_common(15):
    total_tokens = sum(middle_counts[e['middle']] for e in extended_mod_examples
                       if e['modifier_sequence'] == seq)
    print(f"  {seq:10s}: {cnt:4d} types, {total_tokens:6d} tokens")

results['test4'] = {
    'n_extended_compounds': len(extended_mod_examples),
    'n_heterogeneous': len(heterogeneous_stacks),
    'modifier_repetitions': {f"{ch}x{cnt}": n for (ch, cnt), n in mod_repeat_counts.most_common()},
    'top_modifier_sequences': {seq: cnt for seq, cnt in mod_seq_counts.most_common(20)},
    'examples': extended_mod_examples[:30],
}


# ============================================================
# TEST 5: MODIFIER COUNT BY HEAD
# ============================================================
print("\n" + "=" * 70)
print("TEST 5: MODIFIER COUNT BY HEAD ATOM")
print("=" * 70)

# For each compound, identify the HEAD atom and count modifiers
head_mod_counts_type = defaultdict(list)  # head_char -> [n_mods, ...]
head_mod_counts_token = defaultdict(list)

for mid in compound_middles:
    classified = classify_position(mid)
    if not classified:
        continue

    # HEAD is the first atom if its positional role is HEAD
    first = classified[0]
    if first['pos_role'] != 'HEAD':
        # First atom is a modifier (not HEAD/FREE) - record as "no_head"
        head_char = f"[{first['char']}]mod"
    else:
        head_char = first['char']

    mods = get_modifier_atoms(mid)
    n_mods = len(mods)

    head_mod_counts_type[head_char].append(n_mods)
    for _ in range(middle_counts[mid]):
        head_mod_counts_token[head_char].append(n_mods)

print(f"\n--- Modifier depth by HEAD atom ---")
print(f"{'HEAD':>8s}  {'Class':>6s}  {'N types':>8s}  {'Mean mods':>10s}  {'0mod':>6s}  {'1mod':>6s}  {'2mod':>6s}  {'3+mod':>6s}  {'Mean tok':>10s}")

head_results = {}
for head_char in sorted(head_mod_counts_type.keys()):
    type_mods = head_mod_counts_type[head_char]
    token_mods = head_mod_counts_token[head_char]
    n_types = len(type_mods)
    mean_type = np.mean(type_mods)
    mean_token = np.mean(token_mods) if token_mods else 0

    # Distribution of modifier counts
    type_mod_dist = Counter(type_mods)
    pct_0 = type_mod_dist.get(0, 0) / n_types
    pct_1 = type_mod_dist.get(1, 0) / n_types
    pct_2 = type_mod_dist.get(2, 0) / n_types
    pct_3plus = sum(v for k, v in type_mod_dist.items() if k >= 3) / n_types

    ac = atom_class(head_char[0]) if not head_char.startswith('[') else 'MOD'

    print(f"  {head_char:>6s}  {ac:>6s}  {n_types:8d}  {mean_type:10.2f}  "
          f"{pct_0:6.1%}  {pct_1:6.1%}  {pct_2:6.1%}  {pct_3plus:6.1%}  {mean_token:10.2f}")

    head_results[head_char] = {
        'atom_class': ac,
        'n_types': n_types,
        'mean_mods_type': round(mean_type, 3),
        'mean_mods_token': round(mean_token, 3),
        'distribution': {str(k): v for k, v in sorted(type_mod_dist.items())},
    }

# Summary: HEAD class differences
print("\n--- Summary by HEAD class ---")
class_mod_counts = defaultdict(list)
for head_char, type_mods in head_mod_counts_type.items():
    ac = atom_class(head_char[0]) if not head_char.startswith('[') else 'MOD'
    class_mod_counts[ac].extend(type_mods)

for ac in sorted(class_mod_counts.keys()):
    vals = class_mod_counts[ac]
    print(f"  {ac:>6s}: mean={np.mean(vals):.2f}, median={np.median(vals):.1f}, "
          f"max={max(vals)}, n_types={len(vals)}")

results['test5'] = {
    'by_head': head_results,
}


# ============================================================
# TEST 6: MODIFIER COUNT BY TERMINAL
# ============================================================
print("\n" + "=" * 70)
print("TEST 6: MODIFIER COUNT BY TERMINAL ATOM")
print("=" * 70)

term_mod_counts_type = defaultdict(list)
term_mod_counts_token = defaultdict(list)

for mid in compound_middles:
    classified = classify_position(mid)
    if not classified:
        continue

    # TERMINAL is the last atom if its positional role is TERM
    last = classified[-1]
    if last['pos_role'] != 'TERM':
        term_char = f"[{last['char']}]mod"
    else:
        term_char = last['char']

    mods = get_modifier_atoms(mid)
    n_mods = len(mods)

    term_mod_counts_type[term_char].append(n_mods)
    for _ in range(middle_counts[mid]):
        term_mod_counts_token[term_char].append(n_mods)

print(f"\n--- Modifier depth by TERMINAL atom ---")
print(f"{'TERM':>8s}  {'Class':>6s}  {'N types':>8s}  {'Mean mods':>10s}  {'0mod':>6s}  {'1mod':>6s}  {'2mod':>6s}  {'3+mod':>6s}  {'Mean tok':>10s}")

term_results = {}
for term_char in sorted(term_mod_counts_type.keys()):
    type_mods = term_mod_counts_type[term_char]
    token_mods = term_mod_counts_token[term_char]
    n_types = len(type_mods)
    mean_type = np.mean(type_mods)
    mean_token = np.mean(token_mods) if token_mods else 0

    type_mod_dist = Counter(type_mods)
    pct_0 = type_mod_dist.get(0, 0) / n_types
    pct_1 = type_mod_dist.get(1, 0) / n_types
    pct_2 = type_mod_dist.get(2, 0) / n_types
    pct_3plus = sum(v for k, v in type_mod_dist.items() if k >= 3) / n_types

    ac = atom_class(term_char[0]) if not term_char.startswith('[') else 'MOD'

    print(f"  {term_char:>6s}  {ac:>6s}  {n_types:8d}  {mean_type:10.2f}  "
          f"{pct_0:6.1%}  {pct_1:6.1%}  {pct_2:6.1%}  {pct_3plus:6.1%}  {mean_token:10.2f}")

    term_results[term_char] = {
        'atom_class': ac,
        'n_types': n_types,
        'mean_mods_type': round(mean_type, 3),
        'mean_mods_token': round(mean_token, 3),
        'distribution': {str(k): v for k, v in sorted(type_mod_dist.items())},
    }

# Summary: TERM class differences
print("\n--- Summary by TERMINAL class ---")
class_mod_counts_term = defaultdict(list)
for term_char, type_mods in term_mod_counts_type.items():
    ac = atom_class(term_char[0]) if not term_char.startswith('[') else 'MOD'
    class_mod_counts_term[ac].extend(type_mods)

for ac in sorted(class_mod_counts_term.keys()):
    vals = class_mod_counts_term[ac]
    print(f"  {ac:>6s}: mean={np.mean(vals):.2f}, median={np.median(vals):.1f}, "
          f"max={max(vals)}, n_types={len(vals)}")

results['test6'] = {
    'by_terminal': term_results,
}


# ============================================================
# ADDITIONAL: Atom class in modifier position
# ============================================================
print("\n" + "=" * 70)
print("BONUS: ATOM CLASS DISTRIBUTION IN MODIFIER POSITION")
print("=" * 70)

# What atom classes appear in modifier positions?
mod_position_classes = Counter()
mod_position_classes_token = Counter()

for mid in compound_middles:
    mods = get_modifier_atoms(mid)
    for m in mods:
        mod_position_classes[m['atom_class']] += 1
        mod_position_classes_token[m['atom_class']] += middle_counts[mid]

total_mod_pos = sum(mod_position_classes.values())
total_mod_pos_tok = sum(mod_position_classes_token.values())

print(f"\nAtom classes appearing in modifier POSITION (types, N={total_mod_pos}):")
for ac in ['MOD', 'HEAD', 'TERM', 'FREE', 'UNK']:
    cnt = mod_position_classes.get(ac, 0)
    tok = mod_position_classes_token.get(ac, 0)
    if cnt > 0:
        print(f"  {ac:>6s}: {cnt:6d} ({cnt/total_mod_pos:6.1%} types)  "
              f"{tok:8d} ({tok/total_mod_pos_tok:6.1%} tokens)")

# Individual character breakdown in modifier position
print(f"\n--- Individual characters in modifier position ---")
mod_char_counts = Counter()
mod_char_counts_tok = Counter()

for mid in compound_middles:
    mods = get_modifier_atoms(mid)
    for m in mods:
        mod_char_counts[m['char']] += 1
        mod_char_counts_tok[m['char']] += middle_counts[mid]

total_chars = sum(mod_char_counts.values())
total_chars_tok = sum(mod_char_counts_tok.values())

print(f"{'Char':>6s}  {'Class':>6s}  {'Types':>8s}  {'%Types':>8s}  {'Tokens':>8s}  {'%Tokens':>8s}")
for ch, cnt in mod_char_counts.most_common():
    ac = atom_class(ch)
    tok = mod_char_counts_tok.get(ch, 0)
    print(f"  {ch:>4s}  {ac:>6s}  {cnt:8d}  {cnt/total_chars:8.1%}  {tok:8d}  {tok/total_chars_tok:8.1%}")

results['bonus_mod_position_classes'] = {
    'by_class': {ac: mod_position_classes.get(ac, 0) for ac in ['MOD', 'HEAD', 'TERM', 'FREE']},
    'by_char': {ch: cnt for ch, cnt in mod_char_counts.most_common()},
    'by_char_tokens': {ch: cnt for ch, cnt in mod_char_counts_tok.most_common()},
}


# ============================================================
# SAVE RESULTS
# ============================================================
output_path = PROJECT_ROOT / 'phases' / 'SUFFIX_BOUNDARY_TEST' / 'results' / 'modifier_stack_test.json'

# Make serializable
def make_serializable(obj):
    if isinstance(obj, dict):
        return {str(k): make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, set):
        return sorted(obj)
    else:
        return obj

results_serializable = make_serializable(results)

with open(output_path, 'w') as f:
    json.dump(results_serializable, f, indent=2)

print(f"\n{'=' * 70}")
print(f"Results saved to: {output_path}")
print(f"{'=' * 70}")
