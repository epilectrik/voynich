"""P-L12: l-terminal tokens predict extended same-state dwell.

If l = "hold" (steady-state continuation), then l-terminal tokens should
appear within LONGER runs of same-macro-state tokens (extended dwell).

Test 1: Mean same-state run length around l-terminal tokens vs non-l tokens.
Test 2: l-terminal fraction vs mean run length at line level.
Test 3: l-terminal tokens' next-token same-state probability.
"""

import json
import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

PROJECT = Path(__file__).resolve().parent


def normal_cdf(z):
    if z < -8: return 0.0
    if z > 8: return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if z >= 0 else -1
    t = 1.0 / (1.0 + p * abs(z))
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z * z / 2.0)
    return 0.5 * (1.0 + sign * y)


def spearman_rho(x, y):
    n = len(x)
    if n < 3: return 0.0, 1.0
    def rankdata(vals):
        indexed = sorted(enumerate(vals), key=lambda t: t[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n and indexed[j][1] == indexed[i][1]:
                j += 1
            avg = (i + j - 1) / 2.0 + 1
            for kk in range(i, j):
                ranks[indexed[kk][0]] = avg
            i = j
        return ranks
    rx, ry = rankdata(x), rankdata(y)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    if dx == 0 or dy == 0: return 0.0, 1.0
    rho = num / (dx * dy)
    if abs(rho) >= 1.0: return rho, 0.0
    t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2))
    p = 2 * (1 - normal_cdf(abs(t_stat)))
    return rho, p


tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# Load section data
with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
          'axm_residual_decomposition.json', encoding='utf-8') as f:
    axm_data = json.load(f)
folio_section = {f: d['section'] for f, d in axm_data['folio_data'].items()}

# ============================================================
# Build per-line token sequences with macro-state and l-terminal info
# ============================================================
print("Building per-line sequences...")

line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

print(f"  Total lines: {len(line_tokens)}")

# For each line, build token sequence with: (word, middle, is_l_terminal, macro_state)
line_sequences = {}

for (folio, line_id), words in line_tokens.items():
    if len(words) < 4:
        continue
    sec = folio_section.get(folio)
    if not sec:
        continue

    seq = []
    for w in words:
        mid = morph.extract(w).middle
        if not mid:
            continue
        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        if not ms:
            continue
        is_l_term = (len(mid) >= 2 and mid[-1] == 'l')
        term_atom = mid[-1] if len(mid) >= 2 else mid[0]
        seq.append({
            'word': w, 'mid': mid, 'is_l_term': is_l_term,
            'term': term_atom, 'ms': ms
        })

    if len(seq) >= 3:
        line_sequences[(folio, line_id)] = seq

print(f"  Lines with >=3 classified tokens: {len(line_sequences)}")

# ============================================================
# Test 1: Run length around each token
# ============================================================
print(f"\n{'='*70}")
print("TEST 1: SAME-STATE RUN LENGTH AROUND l-TERMINAL vs OTHER TOKENS")
print(f"{'='*70}")
print("For each token, compute the length of its same-state run")
print("(consecutive tokens sharing the same macro-state, including itself)")
print("Prediction: l-terminal tokens are in LONGER runs\n")

# For each line, compute run lengths
# terminal_atom -> list of run lengths
term_run_lengths = defaultdict(list)
l_term_runs = []
nonl_term_runs = []

for (folio, line_id), seq in line_sequences.items():
    # Compute run membership for each position
    states = [t['ms'] for t in seq]
    n = len(states)

    # For each position, find the run it belongs to
    run_lengths = [0] * n
    i = 0
    while i < n:
        j = i
        while j < n and states[j] == states[i]:
            j += 1
        run_len = j - i
        for k_idx in range(i, j):
            run_lengths[k_idx] = run_len
        i = j

    # Record
    for idx, t in enumerate(seq):
        rl = run_lengths[idx]
        term_run_lengths[t['term']].append(rl)
        if t['is_l_term']:
            l_term_runs.append(rl)
        elif len(t['mid']) >= 2:  # compound non-l
            nonl_term_runs.append(rl)

l_mean_run = sum(l_term_runs) / len(l_term_runs) if l_term_runs else 0
nonl_mean_run = sum(nonl_term_runs) / len(nonl_term_runs) if nonl_term_runs else 0
ratio = l_mean_run / nonl_mean_run if nonl_mean_run > 0 else 0

print(f"  l-terminal tokens: mean run length = {l_mean_run:.4f} (n={len(l_term_runs)})")
print(f"  non-l compound tokens: mean run = {nonl_mean_run:.4f} (n={len(nonl_term_runs)})")
print(f"  Ratio: {ratio:.4f}x")

# Per terminal atom ranking
print(f"\n  {'Term':<5s} {'mean run':>10s} {'n':>8s}")
print(f"  {'-'*5} {'-'*10} {'-'*8}")

term_results = []
for term in sorted(term_run_lengths.keys()):
    runs = term_run_lengths[term]
    if len(runs) < 100:
        continue
    mean_r = sum(runs) / len(runs)
    term_results.append((term, mean_r, len(runs)))

term_results.sort(key=lambda x: -x[1])
for term, mr, n in term_results:
    marker = ' <-- l' if term == 'l' else ''
    print(f"  {term:<5s} {mr:>10.4f} {n:>8d}{marker}")

# ============================================================
# Test 2: Next-token same-state probability
# ============================================================
print(f"\n{'='*70}")
print("TEST 2: NEXT-TOKEN SAME-STATE PROBABILITY")
print(f"{'='*70}")
print("After l-terminal token, how often is the next token in the same macro-state?")
print("Compare to baseline and per-terminal-atom\n")

# For each token (except last on line), check if next token has same state
term_same_next = defaultdict(lambda: {'same': 0, 'diff': 0})
l_same = 0
l_diff = 0
nonl_same = 0
nonl_diff = 0

for (folio, line_id), seq in line_sequences.items():
    for i in range(len(seq) - 1):
        same = (seq[i]['ms'] == seq[i+1]['ms'])
        t = seq[i]

        if same:
            term_same_next[t['term']]['same'] += 1
        else:
            term_same_next[t['term']]['diff'] += 1

        if t['is_l_term']:
            if same:
                l_same += 1
            else:
                l_diff += 1
        elif len(t['mid']) >= 2:
            if same:
                nonl_same += 1
            else:
                nonl_diff += 1

l_total_next = l_same + l_diff
nonl_total_next = nonl_same + nonl_diff
l_same_rate = l_same / l_total_next if l_total_next > 0 else 0
nonl_same_rate = nonl_same / nonl_total_next if nonl_total_next > 0 else 0
same_ratio = l_same_rate / nonl_same_rate if nonl_same_rate > 0 else 0

print(f"  l-terminal: same-state rate = {l_same_rate:.4f} ({l_same}/{l_total_next})")
print(f"  non-l compound: same-state rate = {nonl_same_rate:.4f} ({nonl_same}/{nonl_total_next})")
print(f"  Ratio: {same_ratio:.4f}x")

# Per terminal atom
print(f"\n  {'Term':<5s} {'same%':>8s} {'n':>8s}")
print(f"  {'-'*5} {'-'*8} {'-'*8}")

next_results = []
for term in sorted(term_same_next.keys()):
    d = term_same_next[term]
    total = d['same'] + d['diff']
    if total < 100:
        continue
    rate = d['same'] / total
    next_results.append((term, rate, total))

next_results.sort(key=lambda x: -x[1])
for term, rate, n in next_results:
    marker = ' <-- l' if term == 'l' else ''
    print(f"  {term:<5s} {rate*100:>7.2f}% {n:>8d}{marker}")

# ============================================================
# Test 3: Line-level: l-terminal fraction vs mean run length
# ============================================================
print(f"\n{'='*70}")
print("TEST 3: LINE-LEVEL l-TERMINAL FRACTION vs MEAN RUN LENGTH")
print(f"{'='*70}")

line_lf_runs = []
for (folio, line_id), seq in line_sequences.items():
    n_classified = len(seq)
    n_l_term = sum(1 for t in seq if t['is_l_term'])
    l_frac = n_l_term / n_classified

    # Mean run length for this line
    states = [t['ms'] for t in seq]
    runs = []
    i = 0
    while i < len(states):
        j = i
        while j < len(states) and states[j] == states[i]:
            j += 1
        runs.append(j - i)
        i = j
    mean_run = sum(runs) / len(runs) if runs else 0

    line_lf_runs.append((l_frac, mean_run))

l_fracs = [d[0] for d in line_lf_runs]
run_lens = [d[1] for d in line_lf_runs]
rho, p = spearman_rho(l_fracs, run_lens)
print(f"  l-terminal fraction vs mean run length: rho={rho:+.4f}, p={p:.6f}, n={len(line_lf_runs)}")
print(f"  (Positive = more l -> longer same-state runs)")

# ============================================================
# Test 4: Comprehensive — all terminal atoms' same-state run contribution
# ============================================================
print(f"\n{'='*70}")
print("COMPREHENSIVE: ALL TERMINAL ATOMS — SAME-STATE RUN CORRELATION")
print(f"{'='*70}")
print("(Which terminal atoms predict long same-state runs at line level?)\n")

atoms = 'a d e h k o n i m y c p f s t r l q'.split()

line_comp_data = []
for (folio, line_id), seq in line_sequences.items():
    n = len(seq)
    term_counts = Counter()
    for t in seq:
        if len(t['mid']) >= 2:
            term_counts[t['term']] += 1

    states = [t['ms'] for t in seq]
    runs = []
    i = 0
    while i < len(states):
        j = i
        while j < len(states) and states[j] == states[i]:
            j += 1
        runs.append(j - i)
        i = j
    mean_run = sum(runs) / len(runs) if runs else 0

    entry = {'mean_run': mean_run}
    for atom in atoms:
        entry[atom] = term_counts.get(atom, 0) / n
    line_comp_data.append(entry)

mr_vals = [d['mean_run'] for d in line_comp_data]

print(f"  {'Atom':<5s} {'rho':>8s} {'p':>10s} {'direction':>14s}")
print(f"  {'-'*5} {'-'*8} {'-'*10} {'-'*14}")

comp_results = []
for atom in atoms:
    af = [d[atom] for d in line_comp_data]
    r, p_val = spearman_rho(af, mr_vals)
    comp_results.append((atom, r, p_val))

comp_results.sort(key=lambda x: -x[1])
for atom, r, p_val in comp_results:
    sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''
    direction = 'long-dwell' if r > 0.05 else 'short-dwell' if r < -0.05 else 'neutral'
    marker = ' <-- l' if atom == 'l' else ''
    print(f"  {atom:<5s} {r:>+8.4f} {p_val:>10.6f} {direction:>14s} {sig}{marker}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L12 SUMMARY")
print(f"{'='*70}")

print(f"\n  Test 1 (run length): l={l_mean_run:.4f} vs non-l={nonl_mean_run:.4f} = {ratio:.4f}x")
print(f"  Test 2 (next same-state): l={l_same_rate:.4f} vs non-l={nonl_same_rate:.4f} = {same_ratio:.4f}x")
print(f"  Test 3 (line-level): rho={rho:+.4f}, p={p:.6f}")

# Overall assessment
evidence_for_hold = 0
if ratio > 1.05:
    evidence_for_hold += 1
    print(f"\n  Run length: SUPPORTS 'hold' (l in longer runs)")
elif ratio > 1.00:
    print(f"\n  Run length: WEAKLY supports (ratio={ratio:.4f}x)")
else:
    print(f"\n  Run length: DOES NOT support (ratio={ratio:.4f}x)")

if same_ratio > 1.05:
    evidence_for_hold += 1
    print(f"  Next-token: SUPPORTS 'hold' (l followed by same state more often)")
elif same_ratio > 1.00:
    print(f"  Next-token: WEAKLY supports (ratio={same_ratio:.4f}x)")
else:
    print(f"  Next-token: DOES NOT support (ratio={same_ratio:.4f}x)")

if rho > 0.10 and p < 0.05:
    evidence_for_hold += 1
    print(f"  Line-level: SUPPORTS 'hold' (l fraction predicts longer runs)")
elif rho > 0:
    print(f"  Line-level: WEAKLY supports (rho={rho:+.4f})")
else:
    print(f"  Line-level: DOES NOT support (rho={rho:+.4f})")

if evidence_for_hold >= 2:
    print(f"\n  OVERALL: CONFIRMED ({evidence_for_hold}/3 tests support 'hold')")
elif evidence_for_hold >= 1:
    print(f"\n  OVERALL: PARTIAL ({evidence_for_hold}/3 tests support)")
else:
    print(f"\n  OVERALL: FAILED (0/3 tests support 'hold')")
