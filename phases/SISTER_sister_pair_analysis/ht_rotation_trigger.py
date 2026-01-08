"""
HT Prefix Rotation Trigger Analysis

Known (C348): HT prefixes are phase-synchronized
- EARLY: op-, pc-, do-
- LATE: ta-
- Grammar synchrony V=0.136 (p<0.0001)

Question: What TRIGGERS the rotation?
- Does it correlate with specific grammar events?
- Does it happen at line boundaries?
- Is it triggered by kernel contact?

Tier 2 investigation - mechanism identification.
"""

import json
from collections import defaultdict, Counter
import statistics
import math

def load_data_with_positions():
    """Load all tokens with detailed position information."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    data = []
    folio_data = defaultdict(list)

    with open(filepath, 'r', encoding='latin-1') as f:
        header = None
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split('\t')
            parts = [p.strip('"') for p in parts]

            if header is None:
                header = parts
                continue

            if len(parts) < 14:
                continue

            token = parts[0]
            folio = parts[2]
            section = parts[3]
            currier = parts[6]
            transcriber = parts[12]
            line_num = parts[11]
            line_init = parts[13] == '1'
            line_final = parts[14] == '1' if len(parts) > 14 else False

            if transcriber == 'H' and token and '*' not in token:
                entry = {
                    'token': token,
                    'folio': folio,
                    'section': section,
                    'currier': currier,
                    'line': line_num,
                    'line_init': line_init,
                    'line_final': line_final
                }
                data.append(entry)
                folio_data[folio].append(entry)

    return data, folio_data

# Known B grammar vocabulary (479 types - simplified check)
# Using prefix-based classification
B_GRAMMAR_PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'al', 'ct']

# HT prefixes (from C347)
HT_PREFIXES_EARLY = ['op', 'pc', 'do']
HT_PREFIXES_LATE = ['ta']
HT_PREFIXES_ALL = ['yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc', 'ta', 'do']

# Kernel tokens
KERNEL_TOKENS = {'s', 'e', 't', 'd', 'l', 'o', 'h', 'c', 'k', 'r'}

def get_ht_prefix(token):
    """Get HT prefix if token is HT, else None."""
    for p in HT_PREFIXES_ALL:
        if token.startswith(p):
            return p
    return None

def is_ht_token(token):
    """Check if token is likely HT (not in B grammar vocabulary)."""
    # Simplified: HT tokens have HT prefixes
    return get_ht_prefix(token) is not None

def is_b_grammar_token(token):
    """Check if token is likely B grammar."""
    for p in B_GRAMMAR_PREFIXES:
        if token.startswith(p):
            return True
    return False

def has_kernel_contact(token):
    """Check if token contains kernel primitives."""
    return any(k in token for k in KERNEL_TOKENS)

def cramers_v(contingency):
    """Compute Cramer's V from contingency table (dict of dicts)."""
    # Convert to lists
    rows = list(contingency.keys())
    cols = set()
    for row_data in contingency.values():
        cols.update(row_data.keys())
    cols = list(cols)

    if len(rows) < 2 or len(cols) < 2:
        return 0

    # Build matrix
    matrix = []
    for r in rows:
        row = [contingency[r].get(c, 0) for c in cols]
        matrix.append(row)

    # Compute chi-square
    n = sum(sum(row) for row in matrix)
    if n == 0:
        return 0

    row_sums = [sum(row) for row in matrix]
    col_sums = [sum(matrix[i][j] for i in range(len(rows))) for j in range(len(cols))]

    chi2 = 0
    for i in range(len(rows)):
        for j in range(len(cols)):
            expected = row_sums[i] * col_sums[j] / n
            if expected > 0:
                chi2 += (matrix[i][j] - expected) ** 2 / expected

    # Cramer's V
    k = min(len(rows), len(cols))
    if k <= 1 or n <= 1:
        return 0
    v = math.sqrt(chi2 / (n * (k - 1)))
    return v

def main():
    print("=" * 70)
    print("HT PREFIX ROTATION TRIGGER ANALYSIS")
    print("=" * 70)
    print("\nKnown: HT prefixes are phase-synchronized (C348)")
    print("  EARLY: op-, pc-, do-")
    print("  LATE: ta-")
    print("\nQuestion: What TRIGGERS the prefix rotation?\n")

    # Load data
    data, folio_data = load_data_with_positions()
    print(f"Loaded {len(data)} tokens from {len(folio_data)} folios")

    # Filter to Currier B folios only
    b_folios = {f: tokens for f, tokens in folio_data.items()
                if tokens and tokens[0]['currier'] == 'B'}
    print(f"Currier B folios: {len(b_folios)}")

    # ========================================================================
    # TEST 1: HT prefix distribution by line position
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 1: HT Prefix by Line Position")
    print("-" * 70)

    ht_by_position = {'initial': Counter(), 'final': Counter(), 'mid': Counter()}

    for folio, tokens in b_folios.items():
        for entry in tokens:
            prefix = get_ht_prefix(entry['token'])
            if prefix:
                if entry['line_init']:
                    ht_by_position['initial'][prefix] += 1
                elif entry['line_final']:
                    ht_by_position['final'][prefix] += 1
                else:
                    ht_by_position['mid'][prefix] += 1

    print(f"\n{'Prefix':<10} {'Initial':>10} {'Mid':>10} {'Final':>10} {'Init%':>10}")
    print("-" * 55)

    for prefix in sorted(set(ht_by_position['initial'].keys()) |
                         set(ht_by_position['mid'].keys()) |
                         set(ht_by_position['final'].keys())):
        init = ht_by_position['initial'][prefix]
        mid = ht_by_position['mid'][prefix]
        final = ht_by_position['final'][prefix]
        total = init + mid + final
        init_pct = init / total * 100 if total > 0 else 0
        print(f"{prefix:<10} {init:>10} {mid:>10} {final:>10} {init_pct:>9.1f}%")

    # ========================================================================
    # TEST 2: HT prefix by relative position within line
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 2: HT Prefix by Relative Position in Line")
    print("-" * 70)

    # Group tokens by line, compute relative position
    ht_by_rel_pos = {'early': Counter(), 'middle': Counter(), 'late': Counter()}

    for folio, tokens in b_folios.items():
        # Group by line
        lines = defaultdict(list)
        for i, entry in enumerate(tokens):
            lines[entry['line']].append((i, entry))

        for line_tokens in lines.values():
            n = len(line_tokens)
            if n < 3:
                continue

            for idx, (_, entry) in enumerate(line_tokens):
                prefix = get_ht_prefix(entry['token'])
                if prefix:
                    rel_pos = idx / (n - 1) if n > 1 else 0.5
                    if rel_pos < 0.33:
                        ht_by_rel_pos['early'][prefix] += 1
                    elif rel_pos < 0.67:
                        ht_by_rel_pos['middle'][prefix] += 1
                    else:
                        ht_by_rel_pos['late'][prefix] += 1

    print(f"\n{'Prefix':<10} {'Early(0-33%)':>12} {'Mid(33-67%)':>12} {'Late(67-100%)':>14}")
    print("-" * 55)

    all_prefixes = set()
    for pos_data in ht_by_rel_pos.values():
        all_prefixes.update(pos_data.keys())

    for prefix in sorted(all_prefixes):
        early = ht_by_rel_pos['early'][prefix]
        middle = ht_by_rel_pos['middle'][prefix]
        late = ht_by_rel_pos['late'][prefix]
        print(f"{prefix:<10} {early:>12} {middle:>12} {late:>14}")

    # ========================================================================
    # TEST 3: HT prefix by preceding B grammar token
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 3: HT Prefix by Preceding Grammar Token")
    print("-" * 70)

    # What B grammar token precedes each HT prefix?
    preceding_grammar = defaultdict(Counter)

    for folio, tokens in b_folios.items():
        for i in range(1, len(tokens)):
            curr = tokens[i]
            prev = tokens[i-1]

            ht_prefix = get_ht_prefix(curr['token'])
            if ht_prefix and is_b_grammar_token(prev['token']):
                # Get prefix of preceding grammar token
                for gp in B_GRAMMAR_PREFIXES:
                    if prev['token'].startswith(gp):
                        preceding_grammar[ht_prefix][gp] += 1
                        break

    print("\nHT prefix distribution by PRECEDING grammar prefix:")
    print(f"\n{'HT Prefix':<10}", end="")
    for gp in B_GRAMMAR_PREFIXES[:6]:  # Top 6
        print(f"{gp:>8}", end="")
    print()
    print("-" * 60)

    for ht_prefix in sorted(preceding_grammar.keys()):
        counts = preceding_grammar[ht_prefix]
        total = sum(counts.values())
        print(f"{ht_prefix:<10}", end="")
        for gp in B_GRAMMAR_PREFIXES[:6]:
            pct = counts[gp] / total * 100 if total > 0 else 0
            print(f"{pct:>7.1f}%", end="")
        print()

    # ========================================================================
    # TEST 4: HT prefix by kernel contact of neighbors
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 4: HT Prefix by Kernel Contact Context")
    print("-" * 70)

    kernel_context = {'kernel_before': Counter(), 'no_kernel_before': Counter()}

    for folio, tokens in b_folios.items():
        for i in range(1, len(tokens)):
            curr = tokens[i]
            prev = tokens[i-1]

            ht_prefix = get_ht_prefix(curr['token'])
            if ht_prefix:
                if has_kernel_contact(prev['token']):
                    kernel_context['kernel_before'][ht_prefix] += 1
                else:
                    kernel_context['no_kernel_before'][ht_prefix] += 1

    print(f"\n{'Prefix':<10} {'After Kernel':>15} {'After Non-Kernel':>18} {'Kernel Ratio':>15}")
    print("-" * 65)

    for prefix in sorted(set(kernel_context['kernel_before'].keys()) |
                         set(kernel_context['no_kernel_before'].keys())):
        k = kernel_context['kernel_before'][prefix]
        nk = kernel_context['no_kernel_before'][prefix]
        total = k + nk
        ratio = k / total if total > 0 else 0
        print(f"{prefix:<10} {k:>15} {nk:>18} {ratio:>14.1%}")

    # ========================================================================
    # TEST 5: HT prefix transitions (what follows what)
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 5: HT Prefix Transitions")
    print("-" * 70)

    ht_transitions = defaultdict(Counter)

    for folio, tokens in b_folios.items():
        prev_ht = None
        for entry in tokens:
            curr_ht = get_ht_prefix(entry['token'])
            if curr_ht and prev_ht:
                ht_transitions[prev_ht][curr_ht] += 1
            if curr_ht:
                prev_ht = curr_ht
            elif is_b_grammar_token(entry['token']):
                # Reset on grammar token
                prev_ht = None

    print("\nHT prefix transition matrix (row -> col):")
    active_prefixes = sorted(set(ht_transitions.keys()) |
                            set(p for counts in ht_transitions.values() for p in counts.keys()))

    if active_prefixes:
        header = "From\\To"
        print(f"\n{header:<8}", end="")
        for p in active_prefixes[:8]:
            print(f"{p:>8}", end="")
        print()
        print("-" * 75)

        for from_p in active_prefixes[:8]:
            print(f"{from_p:<8}", end="")
            total = sum(ht_transitions[from_p].values())
            for to_p in active_prefixes[:8]:
                count = ht_transitions[from_p][to_p]
                pct = count / total * 100 if total > 0 else 0
                print(f"{pct:>7.1f}%", end="")
            print()

    # ========================================================================
    # TEST 6: Section boundaries
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 6: HT Prefix by Section")
    print("-" * 70)

    ht_by_section = defaultdict(Counter)

    for folio, tokens in b_folios.items():
        for entry in tokens:
            prefix = get_ht_prefix(entry['token'])
            if prefix:
                ht_by_section[entry['section']][prefix] += 1

    print(f"\n{'Section':<10}", end="")
    for p in HT_PREFIXES_ALL[:8]:
        print(f"{p:>8}", end="")
    print()
    print("-" * 75)

    for section in sorted(ht_by_section.keys()):
        print(f"{section:<10}", end="")
        total = sum(ht_by_section[section].values())
        for p in HT_PREFIXES_ALL[:8]:
            count = ht_by_section[section][p]
            pct = count / total * 100 if total > 0 else 0
            print(f"{pct:>7.1f}%", end="")
        print()

    # Compute Cramer's V for section x HT prefix
    contingency = {s: dict(counts) for s, counts in ht_by_section.items()}
    v = cramers_v(contingency)
    print(f"\nCramer's V (Section x HT Prefix): {v:.3f}")

    # ========================================================================
    # TEST 7: EARLY vs LATE prefix triggers
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 7: EARLY vs LATE Prefix Comparison")
    print("-" * 70)

    early_contexts = {'line_init': 0, 'line_final': 0, 'kernel_before': 0, 'total': 0}
    late_contexts = {'line_init': 0, 'line_final': 0, 'kernel_before': 0, 'total': 0}

    for folio, tokens in b_folios.items():
        for i, entry in enumerate(tokens):
            prefix = get_ht_prefix(entry['token'])
            if prefix in HT_PREFIXES_EARLY:
                ctx = early_contexts
            elif prefix in HT_PREFIXES_LATE:
                ctx = late_contexts
            else:
                continue

            ctx['total'] += 1
            if entry['line_init']:
                ctx['line_init'] += 1
            if entry['line_final']:
                ctx['line_final'] += 1
            if i > 0 and has_kernel_contact(tokens[i-1]['token']):
                ctx['kernel_before'] += 1

    print(f"\n{'Context':<20} {'EARLY (op,pc,do)':>20} {'LATE (ta)':>20}")
    print("-" * 65)

    for ctx_name in ['line_init', 'line_final', 'kernel_before']:
        early_pct = early_contexts[ctx_name] / early_contexts['total'] * 100 if early_contexts['total'] > 0 else 0
        late_pct = late_contexts[ctx_name] / late_contexts['total'] * 100 if late_contexts['total'] > 0 else 0
        print(f"{ctx_name:<20} {early_pct:>19.1f}% {late_pct:>19.1f}%")

    print(f"\n{'Total count':<20} {early_contexts['total']:>20} {late_contexts['total']:>20}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("""
    Key findings:

    1. LINE POSITION: Check if EARLY prefixes cluster at line start,
       LATE prefixes at line end

    2. PRECEDING TOKEN: Check if specific grammar prefixes trigger
       specific HT prefixes

    3. KERNEL CONTACT: Check if kernel contact triggers rotation

    4. SECTION: Cramer's V indicates section-level conditioning
    """)

    # Save results
    results = {
        'ht_by_position': {pos: dict(counts) for pos, counts in ht_by_position.items()},
        'section_cramers_v': v,
        'early_contexts': early_contexts,
        'late_contexts': late_contexts
    }

    with open('ht_rotation_trigger_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Results saved to ht_rotation_trigger_results.json")

if __name__ == '__main__':
    main()
