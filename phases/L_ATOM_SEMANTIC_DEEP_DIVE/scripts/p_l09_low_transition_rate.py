"""P-L9: l-terminal MIDDLEs predict LOW macro-state transition rate at line level.

If l = "continue/sustain", lines with more l-terminal tokens should show
fewer macro-state changes (higher self-transition, lower cross-state rate).
Prediction: Spearman rho(l-terminal fraction, transition rate) < 0, rho ~ -0.15 to -0.25.
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
# Build per-line: l-terminal fraction and macro-state transition rate
# ============================================================

# Collect tokens by (folio, line) preserving order
line_tokens = defaultdict(list)  # (folio, line) -> [(word, position), ...]
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

print(f"Total lines: {len(line_tokens)}")

# For each line, compute:
# 1. l-terminal fraction
# 2. macro-state transition rate (# state changes / # possible transitions)
line_data = []

for (folio, line_id), words in line_tokens.items():
    if len(words) < 4:  # need at least 4 tokens for meaningful transition rate
        continue
    sec = folio_section.get(folio)
    if not sec:
        continue

    n_tokens = 0
    n_l_terminal = 0
    macro_states = []

    for w in words:
        m = morph.extract(w).middle
        if not m:
            continue
        n_tokens += 1

        # l-terminal
        if m[-1] == 'l':
            n_l_terminal += 1

        # macro state
        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        if ms:
            macro_states.append(ms)

    if n_tokens < 4 or len(macro_states) < 3:
        continue

    # Transition rate: fraction of adjacent pairs that are different states
    n_transitions = len(macro_states) - 1
    n_changes = sum(1 for i in range(n_transitions) if macro_states[i] != macro_states[i + 1])
    transition_rate = n_changes / n_transitions

    # Self-transition rate (complement)
    self_rate = 1.0 - transition_rate

    l_frac = n_l_terminal / n_tokens

    line_data.append({
        'folio': folio, 'line': line_id, 'sec': sec,
        'l_frac': l_frac, 'trans_rate': transition_rate,
        'self_rate': self_rate, 'n_tokens': n_tokens,
        'n_states': len(macro_states), 'n_changes': n_changes
    })

print(f"Lines with >=4 tokens and >=3 classified: {len(line_data)}")

# ============================================================
# P-L9: l-terminal fraction vs transition rate
# ============================================================
print(f"\n{'='*70}")
print("P-L9: l-TERMINAL FRACTION vs MACRO-STATE TRANSITION RATE")
print(f"{'='*70}")
print("Prediction: rho < 0 (l-rich lines have fewer state changes)")
print(f"Expected: rho between -0.15 and -0.25\n")

l_fracs = [d['l_frac'] for d in line_data]
trans_rates = [d['trans_rate'] for d in line_data]

rho_global, p_global = spearman_rho(l_fracs, trans_rates)
print(f"  Global: rho={rho_global:+.4f}, p={p_global:.6f}, n={len(line_data)}")

# Within-section
print(f"\n  Within-section:")
for sec in sorted(set(d['sec'] for d in line_data)):
    sec_d = [d for d in line_data if d['sec'] == sec]
    if len(sec_d) < 30:
        continue
    sl = [d['l_frac'] for d in sec_d]
    st = [d['trans_rate'] for d in sec_d]
    sr, sp = spearman_rho(sl, st)
    print(f"    {sec} (n={len(sec_d):>4d}): rho={sr:+.4f} p={sp:.6f}")

# ============================================================
# Comprehensive: ALL terminal atoms vs transition rate
# ============================================================
print(f"\n{'='*70}")
print("ALL TERMINAL ATOMS vs MACRO-STATE TRANSITION RATE")
print(f"{'='*70}")
print("(Which terminal atoms predict low transition rate?)\n")

# Per-line terminal atom fractions
atoms = 'a d e h k o n i m y c p f s t r l q'.split()

# Rebuild with all terminal atom fractions
line_term_data = []
for (folio, line_id), words in line_tokens.items():
    if len(words) < 4:
        continue
    sec = folio_section.get(folio)
    if not sec:
        continue

    n_tokens = 0
    term_counts = Counter()
    macro_states = []

    for w in words:
        m = morph.extract(w).middle
        if not m:
            continue
        n_tokens += 1
        term_counts[m[-1]] += 1
        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        if ms:
            macro_states.append(ms)

    if n_tokens < 4 or len(macro_states) < 3:
        continue

    n_transitions = len(macro_states) - 1
    n_changes = sum(1 for i in range(n_transitions) if macro_states[i] != macro_states[i + 1])
    transition_rate = n_changes / n_transitions

    entry = {'trans_rate': transition_rate}
    for atom in atoms:
        entry[atom] = term_counts.get(atom, 0) / n_tokens
    line_term_data.append(entry)

print(f"  {'Atom':<5s} {'rho':>8s} {'p':>10s} {'direction':>14s}")
print(f"  {'-'*5} {'-'*8} {'-'*10} {'-'*14}")

atom_results = []
tr = [d['trans_rate'] for d in line_term_data]
for atom in atoms:
    af = [d[atom] for d in line_term_data]
    r, p = spearman_rho(af, tr)
    atom_results.append((atom, r, p))

atom_results.sort(key=lambda x: x[1])
for atom, r, p in atom_results:
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    direction = 'low-trans' if r < -0.05 else 'high-trans' if r > 0.05 else 'neutral'
    marker = ' <-- l' if atom == 'l' else ''
    print(f"  {atom:<5s} {r:>+8.4f} {p:>10.6f} {direction:>14s} {sig}{marker}")

# ============================================================
# Also test: l-terminal vs SELF-transition rate (should be positive)
# ============================================================
print(f"\n{'='*70}")
print("l-TERMINAL vs SELF-TRANSITION RATE (should be POSITIVE)")
print(f"{'='*70}")

self_rates = [d['self_rate'] for d in line_data]
rho_self, p_self = spearman_rho(l_fracs, self_rates)
print(f"  l-terminal vs self-transition: rho={rho_self:+.4f}, p={p_self:.6f}")

# ============================================================
# Control: ol-only vs all-l-terminal
# ============================================================
print(f"\n{'='*70}")
print("CONTROL: ol-SPECIFIC vs ALL l-TERMINAL")
print(f"{'='*70}")
print("(Is the effect driven entirely by ol, or do other l-compounds contribute?)\n")

# Per-line: ol fraction vs non-ol l-terminal fraction
line_ol_data = []
for (folio, line_id), words in line_tokens.items():
    if len(words) < 4:
        continue
    sec = folio_section.get(folio)
    if not sec:
        continue

    n_tokens = 0
    n_ol = 0
    n_other_l_term = 0
    macro_states = []

    for w in words:
        m = morph.extract(w).middle
        if not m:
            continue
        n_tokens += 1
        if m == 'ol':
            n_ol += 1
        elif m[-1] == 'l' and m != 'ol':
            n_other_l_term += 1
        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        if ms:
            macro_states.append(ms)

    if n_tokens < 4 or len(macro_states) < 3:
        continue

    n_transitions = len(macro_states) - 1
    n_changes = sum(1 for i in range(n_transitions) if macro_states[i] != macro_states[i + 1])
    transition_rate = n_changes / n_transitions

    line_ol_data.append({
        'ol_frac': n_ol / n_tokens,
        'other_l_frac': n_other_l_term / n_tokens,
        'all_l_frac': (n_ol + n_other_l_term) / n_tokens,
        'trans_rate': transition_rate
    })

ol_f = [d['ol_frac'] for d in line_ol_data]
other_l_f = [d['other_l_frac'] for d in line_ol_data]
all_l_f = [d['all_l_frac'] for d in line_ol_data]
tr2 = [d['trans_rate'] for d in line_ol_data]

rho_ol, p_ol = spearman_rho(ol_f, tr2)
rho_other, p_other = spearman_rho(other_l_f, tr2)
rho_all, p_all = spearman_rho(all_l_f, tr2)

print(f"  ol-only vs transition rate:     rho={rho_ol:+.4f}, p={p_ol:.6f}")
print(f"  other-l-term vs transition rate: rho={rho_other:+.4f}, p={p_other:.6f}")
print(f"  all-l-term vs transition rate:   rho={rho_all:+.4f}, p={p_all:.6f}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L9 SUMMARY")
print(f"{'='*70}")
print(f"\n  l-terminal vs transition rate: rho={rho_global:+.4f}, p={p_global:.6f}")
print(f"  Predicted: rho between -0.15 and -0.25")

if -0.30 <= rho_global <= -0.10 and p_global < 0.05:
    print(f"  RESULT: CONFIRMED (rho={rho_global:+.4f} in expected range)")
elif rho_global < -0.05 and p_global < 0.05:
    print(f"  RESULT: SIGNIFICANT negative (rho={rho_global:+.4f})")
elif rho_global < 0 and p_global < 0.10:
    print(f"  RESULT: WEAK negative trend (rho={rho_global:+.4f}, p={p_global:.6f})")
elif rho_global < 0:
    print(f"  RESULT: DIRECTIONALLY CORRECT but not significant (p={p_global:.6f})")
elif rho_global > 0:
    print(f"  RESULT: FAILED (rho={rho_global:+.4f} is positive, not negative)")

print(f"\n  ol-specific effect: rho={rho_ol:+.4f}")
print(f"  non-ol l-terminal effect: rho={rho_other:+.4f}")
if abs(rho_ol) > 2 * abs(rho_other):
    print(f"  --> Effect is primarily ol-driven")
elif abs(rho_other) > 0.05 and p_other < 0.10:
    print(f"  --> Non-ol l-terminals contribute independently")
else:
    print(f"  --> Non-ol l-terminals show no independent effect")
