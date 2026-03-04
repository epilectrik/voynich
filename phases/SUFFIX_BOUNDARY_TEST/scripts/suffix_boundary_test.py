"""
Phase 505: Suffix Boundary Test
================================
Tests whether the SUFFIX layer is a genuine morphological boundary or
whether it is just the TERMINAL portion of compound MIDDLEs being
erroneously stripped by the morphology code.

Five tests:
  1. Suffix Decomposition Audit — do all suffixes follow C1393 slot grammar?
  2. Suffix Independence Test — is suffix choice independent of MIDDLE identity?
  3. Merged vs Split Grammar Quality — does merging MIDDLE+SUFFIX help or hurt?
  4. Terminal Atom Provenance — are compound MIDDLE terminals also suffix chars?
  5. Stripped MIDDLE Structure — do stripped MIDDLEs still end in TERMINAL atoms?

Output: phases/SUFFIX_BOUNDARY_TEST/results/suffix_boundary_test.json
"""

import sys
import os
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2_contingency

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, SUFFIXES

# ============================================================
# C1393 Atom Role Assignment
# ============================================================
HEAD = {'a', 'e', 'o'}
MODIFIER = {'p', 'c', 'i', 'f', 'd', 's'}
TERMINAL = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE = {'k', 't'}

ALL_ATOMS = HEAD | MODIFIER | TERMINAL | FREE

def classify_char(ch):
    """Return the slot role for a single character."""
    if ch in HEAD:
        return 'HEAD'
    elif ch in MODIFIER:
        return 'MODIFIER'
    elif ch in TERMINAL:
        return 'TERMINAL'
    elif ch in FREE:
        return 'FREE'
    else:
        return 'UNKNOWN'


def decompose_suffix(suf):
    """Decompose a suffix into its slot pattern."""
    return [classify_char(c) for c in suf]


def is_valid_slot_pattern(roles):
    """
    Check if a sequence of slot roles is a valid compound pattern.
    Valid: HEAD? MODIFIER* FREE* TERMINAL+ (roughly)
    More precisely: HEAD before MODIFIER, MODIFIER before TERMINAL,
    must end in TERMINAL (or FREE).
    """
    if not roles:
        return False
    # Must end in TERMINAL or FREE
    if roles[-1] not in ('TERMINAL', 'FREE'):
        return False
    # No HEAD after MODIFIER or TERMINAL
    seen_non_head = False
    for r in roles:
        if r in ('MODIFIER', 'TERMINAL', 'FREE'):
            seen_non_head = True
        elif r == 'HEAD' and seen_non_head:
            return False  # HEAD after non-HEAD
    return True


# ============================================================
# Data Loading
# ============================================================
print("=" * 70)
print("PHASE 505: SUFFIX BOUNDARY TEST")
print("=" * 70)

tx = Transcript()
morph = Morphology()

# Collect all Currier B tokens with morphology
tokens_b = []
for token in tx.currier_b():
    if '*' in token.word or not token.word.strip():
        continue
    m = morph.extract(token.word)
    if m.middle:
        tokens_b.append({
            'word': token.word,
            'folio': token.folio,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'prefix2': m.prefix2 if hasattr(m, 'prefix2') else None,
        })

print(f"\nLoaded {len(tokens_b)} Currier B tokens with valid MIDDLEs")

# Unique suffix list (as defined in code)
suffix_list = sorted(set(SUFFIXES), key=len, reverse=True)
print(f"Suffix inventory: {len(suffix_list)} unique suffixes")


# ============================================================
# TEST 1: SUFFIX DECOMPOSITION AUDIT
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: SUFFIX DECOMPOSITION AUDIT")
print("=" * 70)

test1_results = []
valid_count = 0
total_count = len(suffix_list)

# Classify each suffix
for suf in sorted(suffix_list, key=lambda x: (len(x), x)):
    chars = list(suf)
    roles = decompose_suffix(suf)
    pattern = '+'.join(roles)

    # All characters known?
    all_known = all(r != 'UNKNOWN' for r in roles)

    # Ends in terminal?
    ends_terminal = roles[-1] == 'TERMINAL' if roles else False

    # Valid ordering?
    valid = is_valid_slot_pattern(roles) and all_known
    if valid:
        valid_count += 1

    entry = {
        'suffix': suf,
        'chars': chars,
        'roles': roles,
        'pattern': pattern,
        'all_known': all_known,
        'ends_terminal': ends_terminal,
        'valid_pattern': valid,
    }
    test1_results.append(entry)

    status = "VALID" if valid else "INVALID"
    print(f"  {suf:8s} -> {pattern:40s} [{status}]")

# Pattern distribution
pattern_counts = Counter(e['pattern'] for e in test1_results)
print(f"\nPattern distribution:")
for pat, cnt in pattern_counts.most_common():
    print(f"  {pat:40s}: {cnt}")

# Summary
ends_term_frac = sum(1 for e in test1_results if e['ends_terminal']) / total_count
valid_frac = valid_count / total_count
print(f"\nSuffixes ending in TERMINAL atom: {ends_term_frac:.1%} ({sum(1 for e in test1_results if e['ends_terminal'])}/{total_count})")
print(f"Suffixes with valid slot pattern: {valid_frac:.1%} ({valid_count}/{total_count})")

# The 'g' and 's' suffixes
non_terminal_endings = [e for e in test1_results if not e['ends_terminal']]
if non_terminal_endings:
    print(f"\nSuffixes NOT ending in TERMINAL:")
    for e in non_terminal_endings:
        print(f"  {e['suffix']:8s} -> {e['pattern']}")


# ============================================================
# TEST 2: SUFFIX INDEPENDENCE TEST
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: SUFFIX INDEPENDENCE TEST")
print("=" * 70)

# Group by stripped MIDDLE -> suffix distribution
middle_suffix_dist = defaultdict(Counter)
middle_total = Counter()

for t in tokens_b:
    mid = t['middle']
    suf = t['suffix'] if t['suffix'] else '__BARE__'
    middle_suffix_dist[mid][suf] += 1
    middle_total[mid] += 1

# Filter to MIDDLEs with 5+ tokens for meaningful statistics
freq_middles = {m: c for m, c in middle_total.items() if c >= 5}
print(f"MIDDLEs with 5+ tokens: {len(freq_middles)}")

# How many suffixes per MIDDLE?
suffix_counts = {}
for mid in freq_middles:
    n_suffixes = len(middle_suffix_dist[mid])
    suffix_counts[mid] = n_suffixes

# Distribution of suffix variety
variety_dist = Counter(suffix_counts.values())
print(f"\nSuffix variety distribution (MIDDLEs with 5+ tokens):")
for n_suf in sorted(variety_dist.keys()):
    print(f"  {n_suf} suffix(es): {variety_dist[n_suf]} MIDDLEs")

frac_3plus = sum(1 for v in suffix_counts.values() if v >= 3) / len(suffix_counts)
frac_1only = sum(1 for v in suffix_counts.values() if v == 1) / len(suffix_counts)
print(f"\nMIDDLEs with 3+ different suffixes: {frac_3plus:.1%}")
print(f"MIDDLEs with exactly 1 suffix form: {frac_1only:.1%}")

# Entropy of suffix choice given MIDDLE
def entropy(counter):
    total = sum(counter.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counter.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)

entropy_per_middle = {}
for mid in freq_middles:
    entropy_per_middle[mid] = entropy(middle_suffix_dist[mid])

mean_entropy = np.mean(list(entropy_per_middle.values()))
median_entropy = np.median(list(entropy_per_middle.values()))
print(f"\nSuffix entropy given MIDDLE (freq >= 5):")
print(f"  Mean:   {mean_entropy:.3f} bits")
print(f"  Median: {median_entropy:.3f} bits")

# Compare compound vs single-atom MIDDLEs
single_atom_entropies = []
compound_entropies = []

for mid in freq_middles:
    ent = entropy_per_middle[mid]
    if len(mid) == 1:
        single_atom_entropies.append(ent)
    elif len(mid) >= 2:
        compound_entropies.append(ent)

print(f"\nSingle-atom MIDDLEs (len=1): n={len(single_atom_entropies)}")
if single_atom_entropies:
    print(f"  Mean entropy: {np.mean(single_atom_entropies):.3f} bits")
    print(f"  Median:       {np.median(single_atom_entropies):.3f} bits")

print(f"Compound MIDDLEs (len>=2): n={len(compound_entropies)}")
if compound_entropies:
    print(f"  Mean entropy: {np.mean(compound_entropies):.3f} bits")
    print(f"  Median:       {np.median(compound_entropies):.3f} bits")

if single_atom_entropies and compound_entropies:
    ratio = np.mean(compound_entropies) / np.mean(single_atom_entropies) if np.mean(single_atom_entropies) > 0 else float('inf')
    print(f"  Ratio (compound/single): {ratio:.3f}")
    print(f"  Interpretation: {'INDEPENDENT layers (compound has similar/higher entropy)' if ratio >= 0.7 else 'COUPLED (compound has much lower entropy -> suffix is part of MIDDLE)'}")

# Show top examples
print(f"\nTop 10 MIDDLEs by suffix variety (freq >= 10):")
top_variety = sorted(
    [(m, len(middle_suffix_dist[m]), middle_total[m], entropy_per_middle[m])
     for m in freq_middles if middle_total[m] >= 10],
    key=lambda x: (-x[1], -x[3])
)[:10]
for mid, n_suf, n_tok, ent in top_variety:
    suffixes = middle_suffix_dist[mid].most_common(5)
    suf_str = ', '.join(f"{s}({c})" for s, c in suffixes)
    print(f"  {mid:12s} [{n_tok:5d} tok, {n_suf} suf, H={ent:.2f}]: {suf_str}")

# Show examples of locked MIDDLEs (1 suffix only)
print(f"\nExamples of suffix-locked MIDDLEs (1 form only, freq >= 10):")
locked = [(m, list(middle_suffix_dist[m].items())[0])
          for m in freq_middles
          if suffix_counts[m] == 1 and middle_total[m] >= 10]
locked.sort(key=lambda x: -x[1][1])
for mid, (suf, cnt) in locked[:10]:
    print(f"  {mid:12s} -> always {suf:8s} ({cnt} tokens)")


# ============================================================
# TEST 3: MERGED VS SPLIT GRAMMAR QUALITY
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: MERGED VS SPLIT GRAMMAR QUALITY")
print("=" * 70)

def compute_positional_grammar(items, label):
    """
    Given a list of (atom_char, fractional_position) pairs,
    compute chi² of atom x position-tercile.

    items: list of (atom_char, frac_pos) where frac_pos in [0, 1]
    Returns: chi2, V, df, p, n, atom_positions dict
    """
    # Assign terciles
    terciles = []
    for atom, pos in items:
        if pos < 0.333:
            tercile = 'FIRST'
        elif pos < 0.667:
            tercile = 'MIDDLE'
        else:
            tercile = 'LAST'
        terciles.append((atom, tercile))

    # Build contingency table
    atoms = sorted(set(a for a, _ in terciles))
    positions = ['FIRST', 'MIDDLE', 'LAST']

    if len(atoms) < 2:
        return None

    table = np.zeros((len(atoms), len(positions)), dtype=int)
    atom_idx = {a: i for i, a in enumerate(atoms)}
    pos_idx = {p: i for i, p in enumerate(positions)}

    for atom, tercile in terciles:
        table[atom_idx[atom], pos_idx[tercile]] += 1

    # Remove atoms with 0 total (shouldn't happen but be safe)
    row_sums = table.sum(axis=1)
    keep = row_sums > 0
    table = table[keep]
    atoms = [a for a, k in zip(atoms, keep) if k]

    if table.shape[0] < 2 or table.shape[1] < 2:
        return None

    try:
        chi2, p, df, expected = chi2_contingency(table)
    except ValueError:
        return None

    n = table.sum()
    min_dim = min(table.shape[0] - 1, table.shape[1] - 1)
    V = math.sqrt(chi2 / (n * min_dim)) if n > 0 and min_dim > 0 else 0

    # Mean position per atom
    atom_positions = {}
    for atom in atoms:
        positions_of_atom = [pos for a, pos in items if a == atom]
        if positions_of_atom:
            atom_positions[atom] = float(np.mean(positions_of_atom))

    return {
        'chi2': float(chi2),
        'p': float(p),
        'df': int(df),
        'V': float(V),
        'n': int(n),
        'n_atoms': len(atoms),
        'atom_positions': atom_positions,
        'label': label,
    }


# SPLIT model: use suffix-stripped MIDDLEs (current behavior)
split_items = []
for t in tokens_b:
    mid = t['middle']
    if len(mid) < 2:
        continue
    # Only chars that are known atoms
    chars = [c for c in mid if c in ALL_ATOMS]
    if len(chars) < 2:
        continue
    for i, c in enumerate(chars):
        frac_pos = i / (len(chars) - 1) if len(chars) > 1 else 0.5
        split_items.append((c, frac_pos))

split_result = compute_positional_grammar(split_items, 'SPLIT (suffix stripped)')
if split_result:
    print(f"\nSPLIT model (suffix-stripped MIDDLEs, len >= 2):")
    print(f"  n = {split_result['n']}, atoms = {split_result['n_atoms']}")
    print(f"  chi2 = {split_result['chi2']:.1f}, V = {split_result['V']:.4f}, p = {split_result['p']:.2e}")
    print(f"  Mean positions:")
    for atom, pos in sorted(split_result['atom_positions'].items(), key=lambda x: x[1]):
        role = classify_char(atom)
        print(f"    {atom} ({role:8s}): {pos:.3f}")

# MERGED model: concatenate MIDDLE + SUFFIX
merged_items = []
for t in tokens_b:
    mid = t['middle']
    suf = t['suffix'] if t['suffix'] else ''
    merged = mid + suf
    if len(merged) < 2:
        continue
    chars = [c for c in merged if c in ALL_ATOMS]
    if len(chars) < 2:
        continue
    for i, c in enumerate(chars):
        frac_pos = i / (len(chars) - 1) if len(chars) > 1 else 0.5
        merged_items.append((c, frac_pos))

merged_result = compute_positional_grammar(merged_items, 'MERGED (MIDDLE + SUFFIX)')
if merged_result:
    print(f"\nMERGED model (MIDDLE + SUFFIX concatenated, len >= 2):")
    print(f"  n = {merged_result['n']}, atoms = {merged_result['n_atoms']}")
    print(f"  chi2 = {merged_result['chi2']:.1f}, V = {merged_result['V']:.4f}, p = {merged_result['p']:.2e}")
    print(f"  Mean positions:")
    for atom, pos in sorted(merged_result['atom_positions'].items(), key=lambda x: x[1]):
        role = classify_char(atom)
        print(f"    {atom} ({role:8s}): {pos:.3f}")

if split_result and merged_result:
    v_ratio = merged_result['V'] / split_result['V'] if split_result['V'] > 0 else float('inf')
    print(f"\n  V ratio (MERGED / SPLIT): {v_ratio:.4f}")
    if v_ratio > 1.05:
        verdict = "MERGED is BETTER -> suffix may be part of compound MIDDLE"
    elif v_ratio < 0.95:
        verdict = "SPLIT is BETTER -> suffix is a separate layer (merging adds noise)"
    else:
        verdict = "EQUIVALENT -> ambiguous"
    print(f"  Verdict: {verdict}")


# ============================================================
# TEST 4: TERMINAL ATOM PROVENANCE
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: TERMINAL ATOM PROVENANCE")
print("=" * 70)

# Suffix characters (all single chars that appear in any suffix)
suffix_chars = set()
for suf in suffix_list:
    for c in suf:
        suffix_chars.add(c)

print(f"Characters appearing in any suffix: {sorted(suffix_chars)}")

# For each compound MIDDLE (suffix-stripped, 2+ chars), check terminal atom
compound_middles = set()
terminal_in_suffix_chars = 0
terminal_is_suffix_itself = 0
terminal_in_terminal_set = 0
total_compounds = 0

# Also check: does the last 1-3 chars of the MIDDLE match any suffix?
terminal_match_suffix_list = 0

suffix_set = set(suffix_list)

compound_examples = []

for t in tokens_b:
    mid = t['middle']
    if len(mid) < 2:
        continue

    # Only count each unique MIDDLE once
    if mid in compound_middles:
        continue
    compound_middles.add(mid)
    total_compounds += 1

    last_char = mid[-1]

    in_suffix_chars = last_char in suffix_chars
    in_terminal_set = last_char in TERMINAL

    # Check if trailing 1-3 chars match any suffix
    matches_suffix = False
    matching_suffix = None
    for length in [3, 2, 1]:
        if len(mid) >= length + 1:  # Must leave at least 1 char as non-suffix
            candidate = mid[-length:]
            if candidate in suffix_set:
                matches_suffix = True
                matching_suffix = candidate
                break

    if in_suffix_chars:
        terminal_in_suffix_chars += 1
    if in_terminal_set:
        terminal_in_terminal_set += 1
    if matches_suffix:
        terminal_match_suffix_list += 1

    if matches_suffix and total_compounds <= 300:
        compound_examples.append({
            'middle': mid,
            'terminal_char': last_char,
            'matching_suffix': matching_suffix,
            'remaining_if_split': mid[:-len(matching_suffix)] if matching_suffix else None,
        })

print(f"\nCompound MIDDLEs (suffix-stripped, 2+ chars): {total_compounds}")
print(f"  Terminal char is in suffix char set: {terminal_in_suffix_chars}/{total_compounds} = {terminal_in_suffix_chars/total_compounds:.1%}")
print(f"  Terminal char is in TERMINAL set:    {terminal_in_terminal_set}/{total_compounds} = {terminal_in_terminal_set/total_compounds:.1%}")
print(f"  Trailing 1-3 chars match a suffix:   {terminal_match_suffix_list}/{total_compounds} = {terminal_match_suffix_list/total_compounds:.1%}")

# Show examples where trailing chars match a suffix
print(f"\nExamples where compound MIDDLE trailing chars match a suffix:")
for ex in compound_examples[:20]:
    if ex['matching_suffix']:
        print(f"  {ex['middle']:12s} -> trailing '{ex['matching_suffix']}' is a suffix "
              f"(remaining: '{ex['remaining_if_split']}')")

# Now check: what does the terminal char distribution look like?
terminal_char_dist = Counter()
for mid in compound_middles:
    terminal_char_dist[mid[-1]] += 1

print(f"\nTerminal character distribution in compound MIDDLEs:")
for char, cnt in terminal_char_dist.most_common():
    role = classify_char(char)
    pct = cnt / total_compounds * 100
    in_suf = "YES" if char in suffix_chars else "NO"
    print(f"  {char} ({role:8s}, in suffix: {in_suf}): {cnt:4d} = {pct:5.1f}%")


# ============================================================
# TEST 5: STRIPPED MIDDLE STRUCTURE
# ============================================================
print("\n" + "=" * 70)
print("TEST 5: STRIPPED MIDDLE STRUCTURE")
print("=" * 70)

# Take all suffix-stripped MIDDLEs with 2+ atoms
# Check what their LAST character role is

stripped_compound_middles = set()
for t in tokens_b:
    mid = t['middle']
    if len(mid) >= 2:
        stripped_compound_middles.add(mid)

total_stripped = len(stripped_compound_middles)
ending_terminal = 0
ending_modifier = 0
ending_head = 0
ending_free = 0
ending_unknown = 0

ending_details = defaultdict(list)

for mid in stripped_compound_middles:
    last = mid[-1]
    role = classify_char(last)
    if role == 'TERMINAL':
        ending_terminal += 1
    elif role == 'MODIFIER':
        ending_modifier += 1
    elif role == 'HEAD':
        ending_head += 1
    elif role == 'FREE':
        ending_free += 1
    else:
        ending_unknown += 1
    ending_details[role].append(mid)

print(f"Suffix-stripped compound MIDDLEs (2+ chars): {total_stripped}")
print(f"  Ending in TERMINAL atom: {ending_terminal}/{total_stripped} = {ending_terminal/total_stripped:.1%}")
print(f"  Ending in MODIFIER atom: {ending_modifier}/{total_stripped} = {ending_modifier/total_stripped:.1%}")
print(f"  Ending in HEAD atom:     {ending_head}/{total_stripped} = {ending_head/total_stripped:.1%}")
print(f"  Ending in FREE atom:     {ending_free}/{total_stripped} = {ending_free/total_stripped:.1%}")
print(f"  Ending in UNKNOWN:       {ending_unknown}/{total_stripped} = {ending_unknown/total_stripped:.1%}")

# Interpretation
if ending_terminal / total_stripped > 0.7:
    structure_verdict = ("TERMINAL atoms dominate stripped MIDDLEs -> suffix stripping does NOT remove "
                         "all terminals. MIDDLE has its OWN terminal layer independent of suffix.")
elif ending_terminal / total_stripped < 0.3:
    structure_verdict = ("TERMINAL atoms rare in stripped MIDDLEs -> suffix stripping removes most "
                         "terminals. Suffix IS the terminal layer.")
else:
    structure_verdict = ("Mixed terminal presence in stripped MIDDLEs -> partial overlap between "
                         "MIDDLE terminal atoms and suffix layer.")

print(f"\nVerdict: {structure_verdict}")

# Show examples for each ending type
for role in ['TERMINAL', 'MODIFIER', 'HEAD', 'FREE']:
    examples = ending_details.get(role, [])
    if examples:
        # Sort by frequency
        freq = Counter()
        for t in tokens_b:
            if t['middle'] in examples:
                freq[t['middle']] += 1
        top = freq.most_common(8)
        example_str = ', '.join(f"{m}({c})" for m, c in top)
        print(f"\n  {role}-ending examples: {example_str}")

# Also check: for MIDDLEs that appear with AND without suffix
# Does the suffix-less form end differently than the suffixed form's MIDDLE?
print(f"\n--- Same MIDDLE with/without suffix ---")
both_forms = []
for mid in freq_middles:
    has_bare = '__BARE__' in middle_suffix_dist[mid]
    has_suffixed = any(s != '__BARE__' for s in middle_suffix_dist[mid])
    if has_bare and has_suffixed:
        bare_count = middle_suffix_dist[mid]['__BARE__']
        suffixed_count = sum(c for s, c in middle_suffix_dist[mid].items() if s != '__BARE__')
        both_forms.append((mid, bare_count, suffixed_count))

both_forms.sort(key=lambda x: -(x[1] + x[2]))
print(f"MIDDLEs appearing both bare and suffixed (freq>=5): {len(both_forms)}")

# Check terminal character of these MIDDLEs
both_terminal_dist = Counter()
for mid, bare_c, suf_c in both_forms:
    both_terminal_dist[classify_char(mid[-1])] += 1

if both_forms:
    print(f"Terminal character roles (MIDDLEs with both forms):")
    for role, cnt in both_terminal_dist.most_common():
        print(f"  {role}: {cnt} ({cnt/len(both_forms):.1%})")

print(f"\nTop 15 MIDDLEs appearing both bare and suffixed:")
for mid, bare_c, suf_c in both_forms[:15]:
    last_role = classify_char(mid[-1])
    suffixes = [(s, c) for s, c in middle_suffix_dist[mid].items() if s != '__BARE__']
    suffixes.sort(key=lambda x: -x[1])
    suf_str = ', '.join(f"{s}({c})" for s, c in suffixes[:4])
    print(f"  {mid:12s} [{last_role:8s}]: bare={bare_c:4d}, suffixed={suf_c:4d} -> {suf_str}")


# ============================================================
# SYNTHESIS
# ============================================================
print("\n" + "=" * 70)
print("SYNTHESIS")
print("=" * 70)

# Gather key metrics
synthesis = {}

# T1: Suffix slot compliance
synthesis['T1_suffix_slot_compliance'] = valid_frac
synthesis['T1_ends_terminal'] = ends_term_frac

# T2: Suffix independence
synthesis['T2_mean_entropy'] = float(mean_entropy)
synthesis['T2_frac_3plus_suffixes'] = float(frac_3plus)
synthesis['T2_frac_1_suffix_only'] = float(frac_1only)
if single_atom_entropies and compound_entropies:
    synthesis['T2_single_atom_entropy'] = float(np.mean(single_atom_entropies))
    synthesis['T2_compound_entropy'] = float(np.mean(compound_entropies))
    synthesis['T2_entropy_ratio'] = float(ratio)

# T3: Grammar quality
if split_result and merged_result:
    synthesis['T3_split_V'] = split_result['V']
    synthesis['T3_merged_V'] = merged_result['V']
    synthesis['T3_V_ratio'] = float(v_ratio)

# T4: Terminal provenance
synthesis['T4_terminal_in_suffix_chars'] = terminal_in_suffix_chars / total_compounds
synthesis['T4_terminal_matches_suffix'] = terminal_match_suffix_list / total_compounds

# T5: Stripped structure
synthesis['T5_ending_terminal'] = ending_terminal / total_stripped
synthesis['T5_ending_modifier'] = ending_modifier / total_stripped
synthesis['T5_ending_head'] = ending_head / total_stripped

# Overall verdict
print("\nKey findings:")
print(f"  T1: {valid_frac:.0%} of suffixes follow C1393 slot grammar")
print(f"      {ends_term_frac:.0%} end in TERMINAL atoms")
print(f"  T2: Mean suffix entropy = {mean_entropy:.3f} bits")
print(f"      {frac_3plus:.0%} of MIDDLEs have 3+ suffixes")
if single_atom_entropies and compound_entropies:
    print(f"      Single-atom entropy: {np.mean(single_atom_entropies):.3f}, "
          f"Compound entropy: {np.mean(compound_entropies):.3f}")
if split_result and merged_result:
    print(f"  T3: SPLIT V={split_result['V']:.4f}, MERGED V={merged_result['V']:.4f} "
          f"(ratio={v_ratio:.4f})")
print(f"  T4: {terminal_in_suffix_chars/total_compounds:.0%} of compound MIDDLE terminals "
      f"are suffix chars")
print(f"      {terminal_match_suffix_list/total_compounds:.0%} trailing chars match suffix list")
print(f"  T5: {ending_terminal/total_stripped:.0%} of stripped compound MIDDLEs end in TERMINAL")

# Determine overall verdict
if (frac_3plus > 0.3 and mean_entropy > 0.8 and
    ending_terminal / total_stripped > 0.5):
    overall = ("SUFFIX IS A GENUINE SEPARATE LAYER: High suffix variety (T2), "
               "stripped MIDDLEs retain terminal atoms (T5), suffix is independently "
               "selectable. The TERMINAL signal in C1393 is NOT an artifact of "
               "suffix contamination.")
elif (frac_1only > 0.7 and mean_entropy < 0.3 and
      ending_terminal / total_stripped < 0.3):
    overall = ("SUFFIX IS PART OF MIDDLE: Low suffix variety (T2), "
               "stripped MIDDLEs lose terminal atoms (T5), suffix choice is "
               "determined by MIDDLE. C1393 TERMINAL signal may be partially "
               "or fully an artifact.")
else:
    overall = ("MIXED EVIDENCE: Suffix shows partial independence from MIDDLE. "
               "The boundary is real but porous — some 'suffixes' may be MIDDLE "
               "terminals, while others are genuinely independent.")

print(f"\n  OVERALL: {overall}")
synthesis['overall_verdict'] = overall


# ============================================================
# SAVE RESULTS
# ============================================================
results = {
    'test1_suffix_decomposition': {
        'suffixes': test1_results,
        'valid_fraction': float(valid_frac),
        'ends_terminal_fraction': float(ends_term_frac),
        'pattern_distribution': dict(pattern_counts),
    },
    'test2_suffix_independence': {
        'n_middles_freq5': len(freq_middles),
        'mean_entropy': float(mean_entropy),
        'median_entropy': float(median_entropy),
        'frac_3plus_suffixes': float(frac_3plus),
        'frac_1_suffix_only': float(frac_1only),
        'single_atom_mean_entropy': float(np.mean(single_atom_entropies)) if single_atom_entropies else None,
        'compound_mean_entropy': float(np.mean(compound_entropies)) if compound_entropies else None,
        'entropy_ratio': float(ratio) if (single_atom_entropies and compound_entropies) else None,
    },
    'test3_grammar_quality': {
        'split': split_result,
        'merged': merged_result,
        'V_ratio': float(v_ratio) if (split_result and merged_result) else None,
    },
    'test4_terminal_provenance': {
        'total_compound_middles': total_compounds,
        'terminal_in_suffix_chars': terminal_in_suffix_chars,
        'terminal_in_suffix_chars_frac': terminal_in_suffix_chars / total_compounds,
        'terminal_in_terminal_set': terminal_in_terminal_set,
        'terminal_in_terminal_set_frac': terminal_in_terminal_set / total_compounds,
        'terminal_matches_suffix_list': terminal_match_suffix_list,
        'terminal_matches_suffix_list_frac': terminal_match_suffix_list / total_compounds,
        'terminal_char_distribution': dict(terminal_char_dist),
    },
    'test5_stripped_structure': {
        'total_stripped_compounds': total_stripped,
        'ending_terminal': ending_terminal,
        'ending_terminal_frac': ending_terminal / total_stripped,
        'ending_modifier': ending_modifier,
        'ending_modifier_frac': ending_modifier / total_stripped,
        'ending_head': ending_head,
        'ending_head_frac': ending_head / total_stripped,
        'ending_free': ending_free,
        'ending_free_frac': ending_free / total_stripped,
        'n_both_forms': len(both_forms),
        'both_forms_terminal_dist': dict(both_terminal_dist),
    },
    'synthesis': synthesis,
}

outpath = PROJECT_ROOT / 'phases' / 'SUFFIX_BOUNDARY_TEST' / 'results' / 'suffix_boundary_test.json'
with open(outpath, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {outpath}")
print("DONE")
