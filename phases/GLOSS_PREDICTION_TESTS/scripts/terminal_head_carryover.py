"""
Terminal → Head Carry-Over Test

Tests whether the TERMINAL atom of one compound MIDDLE predicts the HEAD atom
of the NEXT token's compound MIDDLE. Validates the "terminal carries state forward"
hypothesis from C1200 at full atom resolution.

Method:
1. Iterate through all Currier B tokens in line order
2. For consecutive tokens with compound MIDDLEs (2+ atoms), record:
   - Terminal atom of token N
   - Head atom of token N+1
3. Build transition matrix and test with chi-squared
4. Compare within-line vs across-line (C1200 showed carry-over resets at boundaries)
5. Identify strongest terminal→head transitions
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency
import numpy as np
import json

ATOMS = set('kehyinamdtlocpfsgrx')

tx = Transcript()
morph = Morphology()

def get_atom_sequence(middle):
    return [ch for ch in middle if ch in ATOMS]

# Collect all B tokens in order, grouped by folio+line
tokens_by_line = defaultdict(list)
for token in tx.currier_b():
    w = token.word
    if not w.strip() or '*' in w:
        continue
    m = morph.extract(w)
    if not m.middle:
        continue
    seq = get_atom_sequence(m.middle)
    if len(seq) < 2:
        continue  # only compound MIDDLEs

    key = (token.folio, token.line)
    tokens_by_line[key].append({
        'word': w,
        'middle': m.middle,
        'atoms': seq,
        'head': seq[0],
        'terminal': seq[-1],
        'position': token.position if hasattr(token, 'position') else None
    })

# Build transition matrix: terminal(N) → head(N+1)
# Within-line only
within_line_transitions = Counter()
# Across-line (consecutive lines on same folio)
across_line_transitions = Counter()

# Within-line
for key, tokens in tokens_by_line.items():
    for i in range(len(tokens) - 1):
        terminal = tokens[i]['terminal']
        head = tokens[i+1]['head']
        within_line_transitions[(terminal, head)] += 1

# Across-line: last token of line N → first token of line N+1
folio_lines = defaultdict(list)
for key in sorted(tokens_by_line.keys()):
    folio, line = key
    folio_lines[folio].append(line)

for folio, lines in folio_lines.items():
    lines_sorted = sorted(set(lines))
    for i in range(len(lines_sorted) - 1):
        current_line = lines_sorted[i]
        next_line = lines_sorted[i+1]

        current_tokens = tokens_by_line.get((folio, current_line), [])
        next_tokens = tokens_by_line.get((folio, next_line), [])

        if current_tokens and next_tokens:
            terminal = current_tokens[-1]['terminal']
            head = next_tokens[0]['head']
            across_line_transitions[(terminal, head)] += 1

# Analysis
print(f"{'='*70}")
print(f"TERMINAL -> HEAD CARRY-OVER TEST")
print(f"{'='*70}")
print(f"Within-line transitions: {sum(within_line_transitions.values())}")
print(f"Across-line transitions: {sum(across_line_transitions.values())}")

# Get all terminals and heads
all_terminals = sorted(set(t for t, h in within_line_transitions.keys()))
all_heads = sorted(set(h for t, h in within_line_transitions.keys()))

print(f"Unique terminals: {all_terminals}")
print(f"Unique heads: {all_heads}")

# Build contingency table for within-line
def analyze_transitions(transitions, label):
    print(f"\n{'='*70}")
    print(f"{label}")
    print(f"{'='*70}")

    terminals = sorted(set(t for t, h in transitions.keys()))
    heads = sorted(set(h for t, h in transitions.keys()))

    # Build matrix
    matrix = np.zeros((len(terminals), len(heads)), dtype=int)
    for i, t in enumerate(terminals):
        for j, h in enumerate(heads):
            matrix[i, j] = transitions.get((t, h), 0)

    total = matrix.sum()
    if total == 0:
        print("  No data")
        return None

    # Print transition matrix
    print(f"\n  Transition matrix (terminal -> head):")
    print(f"  {'':>8}", end='')
    for h in heads:
        print(f"  {h:>6}", end='')
    print(f"  {'Total':>6}")

    for i, t in enumerate(terminals):
        row_total = matrix[i].sum()
        if row_total == 0:
            continue
        print(f"  {t:>6} ->", end='')
        for j, h in enumerate(heads):
            val = matrix[i, j]
            if row_total > 0:
                pct = 100 * val / row_total
                if pct > 0:
                    print(f"  {pct:>5.1f}%", end='')
                else:
                    print(f"  {'---':>6}", end='')
            else:
                print(f"  {'---':>6}", end='')
        print(f"  {row_total:>5}")

    # Chi-squared test
    # Filter to rows/cols with enough data
    row_sums = matrix.sum(axis=1)
    col_sums = matrix.sum(axis=0)
    keep_rows = row_sums >= 10
    keep_cols = col_sums >= 10

    filtered = matrix[keep_rows][:, keep_cols]
    filtered_terminals = [t for t, k in zip(terminals, keep_rows) if k]
    filtered_heads = [h for h, k in zip(heads, keep_cols) if k]

    if filtered.shape[0] >= 2 and filtered.shape[1] >= 2:
        chi2, p, dof, expected = chi2_contingency(filtered)
        V = np.sqrt(chi2 / (filtered.sum() * (min(filtered.shape) - 1)))
        print(f"\n  Chi-sq = {chi2:.1f}, p = {p:.2e}, dof = {dof}, Cramer's V = {V:.3f}")
        print(f"  {'CARRY-OVER CONFIRMED' if p < 0.001 else 'NO CARRY-OVER'}")

        # Find strongest deviations from expected
        print(f"\n  Strongest carry-over effects (observed/expected ratio):")
        ratios = []
        for i, t in enumerate(filtered_terminals):
            for j, h in enumerate(filtered_heads):
                obs = filtered[i, j]
                exp = expected[i, j]
                if exp > 5 and obs > 5:
                    ratio = obs / exp
                    ratios.append((t, h, obs, exp, ratio))

        ratios.sort(key=lambda x: -x[4])
        print(f"  {'Terminal':>8} -> {'Head':>6}  {'Obs':>5} {'Exp':>5} {'Ratio':>6}")
        for t, h, obs, exp, ratio in ratios[:10]:
            marker = '***' if ratio > 1.5 or ratio < 0.67 else ''
            print(f"  {t:>8} -> {h:>6}  {obs:>5} {exp:>5.0f} {ratio:>5.2f}x {marker}")

        print(f"\n  Strongest avoidances:")
        ratios.sort(key=lambda x: x[4])
        for t, h, obs, exp, ratio in ratios[:5]:
            if ratio < 1:
                print(f"  {t:>8} -> {h:>6}  {obs:>5} {exp:>5.0f} {ratio:>5.2f}x")

        return {'chi2': float(chi2), 'p': float(p), 'V': float(V), 'n': int(filtered.sum())}
    else:
        print(f"\n  Insufficient data for chi-sq test (matrix shape {filtered.shape})")
        return None

within_result = analyze_transitions(within_line_transitions, "WITHIN-LINE CARRY-OVER")
across_result = analyze_transitions(across_line_transitions, "ACROSS-LINE CARRY-OVER")

# Compare within vs across (C1200 showed within >> across)
if within_result and across_result:
    print(f"\n{'='*70}")
    print(f"LINE BOUNDARY RESET TEST (C1200 replication)")
    print(f"{'='*70}")
    print(f"  Within-line Cramer's V: {within_result['V']:.3f}")
    print(f"  Across-line Cramer's V: {across_result['V']:.3f}")
    ratio = within_result['V'] / across_result['V'] if across_result['V'] > 0 else float('inf')
    print(f"  Within/Across ratio: {ratio:.1f}x")
    print(f"  C1200 found carry-over within > across")
    if ratio > 2:
        print(f"  CONSISTENT: within-line carry-over substantially stronger")
    elif ratio > 1.2:
        print(f"  WEAKLY CONSISTENT: within-line carry-over modestly stronger")
    else:
        print(f"  NOT CONSISTENT: carry-over similar across boundary")

# Head marginal distribution (baseline)
print(f"\n{'='*70}")
print(f"HEAD ATOM MARGINAL DISTRIBUTION (baseline)")
print(f"{'='*70}")
head_counts = Counter()
for key, tokens in tokens_by_line.items():
    for t in tokens:
        head_counts[t['head']] += 1
total_heads = sum(head_counts.values())
print(f"  {'Atom':>6}  {'Count':>6}  {'%':>6}")
for atom, count in head_counts.most_common():
    print(f"  {atom:>6}  {count:>6}  {100*count/total_heads:>5.1f}%")

# Terminal marginal distribution
print(f"\n{'='*70}")
print(f"TERMINAL ATOM MARGINAL DISTRIBUTION")
print(f"{'='*70}")
terminal_counts = Counter()
for key, tokens in tokens_by_line.items():
    for t in tokens:
        terminal_counts[t['terminal']] += 1
total_terminals = sum(terminal_counts.values())
print(f"  {'Atom':>6}  {'Count':>6}  {'%':>6}")
for atom, count in terminal_counts.most_common():
    print(f"  {atom:>6}  {count:>6}  {100*count/total_terminals:>5.1f}%")

# Save
output_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'terminal_head_carryover.json')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
output = {
    'within_line': within_result,
    'across_line': across_result,
    'within_line_n': sum(within_line_transitions.values()),
    'across_line_n': sum(across_line_transitions.values()),
}
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nResults saved to {output_path}")
