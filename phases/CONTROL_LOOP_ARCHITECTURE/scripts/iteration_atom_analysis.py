#!/usr/bin/env python3
"""
Gap 2: Iteration Atom Grammar

How do i, n, and their compounds (aiin, iin, in, ain) function as loop controllers?
- i="iterate", n="halt" — but what determines iteration count?
- aiin = accept-iterate-iterate-halt: a bounded loop?
- Where do iteration atoms cluster? Line-final? Decision points?

Output: phases/CONTROL_LOOP_ARCHITECTURE/results/iteration_atom_analysis.json
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'phases' / 'CONTROL_LOOP_ARCHITECTURE' / 'results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tx = Transcript()
morph = Morphology()

# Iteration compounds to analyze
ITER_COMPOUNDS = ['aiin', 'iin', 'in', 'ain', 'oiin', 'ii', 'i', 'n']

# ============================================================
# COLLECT DATA
# ============================================================
print("Analyzing iteration atoms in Currier B...")

# Group tokens by folio -> line
folio_lines = defaultdict(lambda: defaultdict(list))
token_positions = []  # (token, line_pos_frac, is_line_initial, is_line_final)
all_tokens = list(tx.currier_b())

for token in all_tokens:
    if token.is_label:
        continue
    folio_lines[token.folio][token.line].append(token)

# Build line position index
for folio in folio_lines:
    for line in folio_lines[folio]:
        tokens = folio_lines[folio][line]
        n = len(tokens)
        for i, t in enumerate(tokens):
            pos_frac = i / max(n - 1, 1)
            token_positions.append({
                'token': t,
                'pos_frac': pos_frac,
                'pos_idx': i,
                'line_len': n,
                'is_first': i == 0,
                'is_last': i == n - 1,
                'is_penultimate': i == n - 2,
            })

# ============================================================
# ANALYSIS 1: MIDDLE-level iteration compound statistics
# ============================================================
print("\n=== ITERATION COMPOUND STATISTICS ===")

compound_stats = {}
for compound in ITER_COMPOUNDS:
    # Find all tokens where MIDDLE equals or contains this compound
    exact_matches = []  # MIDDLE is exactly this compound
    contains_matches = []  # MIDDLE contains this compound

    for tp in token_positions:
        m = morph.extract(tp['token'].word)
        if m.middle is None:
            continue
        if m.middle == compound:
            exact_matches.append(tp)
        elif compound in m.middle and len(compound) > 1:
            contains_matches.append(tp)

    if not exact_matches and not contains_matches:
        continue

    # Position analysis for exact matches
    positions = [tp['pos_frac'] for tp in exact_matches]
    line_final_rate = sum(1 for tp in exact_matches if tp['is_last']) / max(len(exact_matches), 1)
    line_initial_rate = sum(1 for tp in exact_matches if tp['is_first']) / max(len(exact_matches), 1)
    penultimate_rate = sum(1 for tp in exact_matches if tp['is_penultimate']) / max(len(exact_matches), 1)

    # Prefix distribution for exact matches
    prefix_counts = Counter()
    for tp in exact_matches:
        m = morph.extract(tp['token'].word)
        if m.prefix:
            prefix_counts[m.prefix] += 1

    # Suffix distribution for exact matches
    suffix_counts = Counter()
    bare_count = 0
    for tp in exact_matches:
        m = morph.extract(tp['token'].word)
        if m.suffix:
            suffix_counts[m.suffix] += 1
        else:
            bare_count += 1

    mean_pos = sum(positions) / len(positions) if positions else 0

    stats = {
        'exact_count': len(exact_matches),
        'contains_count': len(contains_matches),
        'mean_position': round(mean_pos, 3),
        'line_final_rate': round(line_final_rate * 100, 1),
        'line_initial_rate': round(line_initial_rate * 100, 1),
        'penultimate_rate': round(penultimate_rate * 100, 1),
        'bare_suffix_rate': round(bare_count / max(len(exact_matches), 1) * 100, 1),
        'top_prefixes': prefix_counts.most_common(8),
        'top_suffixes': suffix_counts.most_common(8),
    }
    compound_stats[compound] = stats

    print(f"\n  {compound}:")
    print(f"    Exact: {stats['exact_count']}, Contains: {stats['contains_count']}")
    print(f"    Mean position: {stats['mean_position']}")
    print(f"    Line-final: {stats['line_final_rate']}%, Initial: {stats['line_initial_rate']}%, Penultimate: {stats['penultimate_rate']}%")
    print(f"    Bare suffix: {stats['bare_suffix_rate']}%")
    print(f"    Top prefixes: {stats['top_prefixes'][:5]}")
    print(f"    Top suffixes: {stats['top_suffixes'][:5]}")

# ============================================================
# ANALYSIS 2: SUFFIX-level iteration compounds
# ============================================================
print("\n\n=== ITERATION COMPOUNDS AS SUFFIXES ===")

suffix_iter_stats = {}
for compound in ITER_COMPOUNDS:
    # Find tokens where suffix matches
    suffix_matches = []
    for tp in token_positions:
        m = morph.extract(tp['token'].word)
        if m.suffix == compound:
            suffix_matches.append(tp)
        elif m.suffix and compound in m.suffix:
            suffix_matches.append(tp)

    if not suffix_matches:
        continue

    positions = [tp['pos_frac'] for tp in suffix_matches]
    line_final_rate = sum(1 for tp in suffix_matches if tp['is_last']) / len(suffix_matches)
    mean_pos = sum(positions) / len(positions)

    # What MIDDLEs pair with this suffix?
    middle_counts = Counter()
    for tp in suffix_matches:
        m = morph.extract(tp['token'].word)
        if m.middle:
            middle_counts[m.middle] += 1

    # Kernel content of those MIDDLEs
    kernel_counts = Counter()
    for tp in suffix_matches:
        m = morph.extract(tp['token'].word)
        if m.middle:
            for c in m.middle:
                if c in 'keh':
                    kernel_counts[c] += 1

    stats = {
        'count': len(suffix_matches),
        'mean_position': round(mean_pos, 3),
        'line_final_rate': round(line_final_rate * 100, 1),
        'top_middles': middle_counts.most_common(10),
        'kernel_in_middle': dict(kernel_counts.most_common()),
    }
    suffix_iter_stats[compound] = stats

    print(f"\n  -{compound} (suffix):")
    print(f"    Count: {stats['count']}")
    print(f"    Mean position: {stats['mean_position']}")
    print(f"    Line-final: {stats['line_final_rate']}%")
    print(f"    Top MIDDLEs: {stats['top_middles'][:5]}")
    print(f"    Kernels in MIDDLE: {dict(kernel_counts)}")

# ============================================================
# ANALYSIS 3: i-count patterns (number of i's in iteration compound)
# ============================================================
print("\n\n=== i-COUNT PATTERNS ===")

# Count i characters in MIDDLEs
i_count_data = defaultdict(list)
for tp in token_positions:
    m = morph.extract(tp['token'].word)
    if m.middle is None:
        continue
    i_count = m.middle.count('i')
    if i_count > 0:
        i_count_data[i_count].append(tp)

for count in sorted(i_count_data.keys()):
    tps = i_count_data[count]
    n = len(tps)
    mean_pos = sum(tp['pos_frac'] for tp in tps) / n
    final_rate = sum(1 for tp in tps if tp['is_last']) / n

    # n-count in same MIDDLE
    n_co = sum(1 for tp in tps if 'n' in morph.extract(tp['token'].word).middle)
    a_co = sum(1 for tp in tps if 'a' in morph.extract(tp['token'].word).middle)

    print(f"  i-count={count}: {n} tokens, mean_pos={mean_pos:.3f}, final={final_rate*100:.1f}%, n_co={n_co/n*100:.1f}%, a_co={a_co/n*100:.1f}%")

# ============================================================
# ANALYSIS 4: Iteration atoms at decision points
# ============================================================
print("\n\n=== DECISION POINT CLUSTERING ===")
# Are iteration compounds enriched at specific line positions?
# Compare line-final and penultimate positions

# Overall baseline: what fraction of ALL tokens are at each position?
all_final = sum(1 for tp in token_positions if tp['is_last'])
all_penult = sum(1 for tp in token_positions if tp['is_penultimate'])
total = len(token_positions)

print(f"  Baseline final rate: {all_final/total*100:.1f}%")
print(f"  Baseline penultimate rate: {all_penult/total*100:.1f}%")

# For each iteration compound, compare
for compound in ['aiin', 'iin', 'in', 'ain']:
    matches = []
    for tp in token_positions:
        m = morph.extract(tp['token'].word)
        if m.middle == compound or (m.suffix and compound in m.suffix):
            matches.append(tp)
    if not matches:
        continue
    n = len(matches)
    final = sum(1 for tp in matches if tp['is_last'])
    penult = sum(1 for tp in matches if tp['is_penultimate'])
    enrichment_final = (final/n) / (all_final/total) if all_final > 0 else 0
    enrichment_penult = (penult/n) / (all_penult/total) if all_penult > 0 else 0
    print(f"\n  {compound}:")
    print(f"    Total: {n}")
    print(f"    Final: {final} ({final/n*100:.1f}%), enrichment: {enrichment_final:.2f}x")
    print(f"    Penult: {penult} ({penult/n*100:.1f}%), enrichment: {enrichment_penult:.2f}x")

# ============================================================
# ANALYSIS 5: Sequence patterns — what comes before/after iteration tokens
# ============================================================
print("\n\n=== CONTEXT PATTERNS (BEFORE/AFTER ITERATION TOKENS) ===")

# For tokens with MIDDLE containing aiin/iin, what is the NEXT token's MIDDLE?
for compound in ['aiin', 'iin', 'ain']:
    before_middles = Counter()
    after_middles = Counter()

    for folio in folio_lines:
        for line in folio_lines[folio]:
            tokens = folio_lines[folio][line]
            for i, t in enumerate(tokens):
                m = morph.extract(t.word)
                if m.middle != compound and not (m.suffix and m.suffix == compound):
                    continue
                # Previous token's MIDDLE
                if i > 0:
                    pm = morph.extract(tokens[i-1].word)
                    if pm.middle:
                        before_middles[pm.middle] += 1
                # Next token's MIDDLE
                if i < len(tokens) - 1:
                    nm = morph.extract(tokens[i+1].word)
                    if nm.middle:
                        after_middles[nm.middle] += 1

    if before_middles or after_middles:
        print(f"\n  {compound}:")
        print(f"    Before: {before_middles.most_common(8)}")
        print(f"    After:  {after_middles.most_common(8)}")

# ============================================================
# COMPILE RESULTS
# ============================================================
results = {
    'iteration_compounds_as_middle': {},
    'iteration_compounds_as_suffix': {},
    'i_count_patterns': {},
    'decision_point_enrichment': {},
}

for compound, stats in compound_stats.items():
    results['iteration_compounds_as_middle'][compound] = {
        'exact_count': stats['exact_count'],
        'mean_position': stats['mean_position'],
        'line_final_rate': stats['line_final_rate'],
        'line_initial_rate': stats['line_initial_rate'],
        'bare_suffix_rate': stats['bare_suffix_rate'],
        'top_prefixes': stats['top_prefixes'][:5],
    }

for compound, stats in suffix_iter_stats.items():
    results['iteration_compounds_as_suffix'][compound] = {
        'count': stats['count'],
        'mean_position': stats['mean_position'],
        'line_final_rate': stats['line_final_rate'],
        'top_middles': stats['top_middles'][:5],
        'kernel_in_middle': stats['kernel_in_middle'],
    }

for count in sorted(i_count_data.keys()):
    tps = i_count_data[count]
    n = len(tps)
    results['i_count_patterns'][str(count)] = {
        'token_count': n,
        'mean_position': round(sum(tp['pos_frac'] for tp in tps) / n, 3),
        'line_final_rate': round(sum(1 for tp in tps if tp['is_last']) / n * 100, 1),
    }

output_path = OUTPUT_DIR / 'iteration_atom_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults written to: {output_path}")
