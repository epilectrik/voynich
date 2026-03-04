"""
Three untested predictions from the crazy expert's gloss analysis.

P6: n-terminal MIDDLEs should appear more at Mode A/B transition boundaries
    (if n = "bind," it connects iterations at mode transitions)
P7: o-initial MIDDLEs should correlate with apparatus (AZC) vocabulary
    (if o = "vessel," it should appear in apparatus contexts)
P8: f-containing tokens should be enriched in REGIME_3
    (if f = "fire," it should cluster where fire is actively managed)
"""
import sys, os, json, math
from collections import defaultdict, Counter
from functools import partial
from scipy import stats
print = partial(print, flush=True)

sys.path.insert(0, os.path.dirname(__file__))
from scripts.voynich import Transcript, Morphology

# ---- Setup ----
tx = Transcript()
morph = Morphology()

# Suffix mode classification (from suffix_mode_assignment.py)
TERMINAL_SUFFIXES = {'y', 'ey', 'dy', 'edy', 'eedy', 'hy', 'chy', 'shy',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}

MODE_A_CENTROID = [0.430, 0.019, 0.086, 0.466]
MODE_B_CENTROID = [0.155, 0.031, 0.072, 0.741]
SUFFIX_CATS = ['terminal', 'connector', 'iterate', 'bare']

def suffix_category(suffix):
    if not suffix:
        return 'bare'
    if suffix in TERMINAL_SUFFIXES:
        return 'terminal'
    if suffix in CONNECTOR_SUFFIXES:
        return 'connector'
    if suffix in ITERATE_SUFFIXES:
        return 'iterate'
    return 'bare'

def euclidean_dist(a, b):
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))

def classify_suffix_mode(line_toks):
    if len(line_toks) < 3:
        return None
    counts = Counter(t['suffix_cat'] for t in line_toks)
    n = len(line_toks)
    vec = [counts.get(c, 0) / n for c in SUFFIX_CATS]
    d_a = euclidean_dist(vec, MODE_A_CENTROID)
    d_b = euclidean_dist(vec, MODE_B_CENTROID)
    return 'A' if d_a < d_b else 'B'

# Load regime mapping
regime_data = json.load(open('data/regime_folio_mapping.json'))
regime_map = {f: v['regime'] for f, v in regime_data['regime_assignments'].items()}

# ---- Get all B tokens with morphology ----
tokens = [t for t in tx.currier_b() if not t.placement.startswith('L') and '*' not in t.word]
print(f"Currier B tokens: {len(tokens)}")

# Build per-line data
line_data = defaultdict(list)
for t in tokens:
    m = morph.extract(t.word)
    mid = m.middle or ''
    sfx = m.suffix or ''
    pfx = m.prefix or ''
    line_data[(t.folio, t.line)].append({
        'word': t.word, 'middle': mid, 'suffix': sfx, 'prefix': pfx,
        'suffix_cat': suffix_category(sfx),
        'folio': t.folio, 'section': t.section,
    })

# Classify each line's suffix mode
line_modes = {}
for key, toks in line_data.items():
    mode = classify_suffix_mode(toks)
    if mode:
        line_modes[key] = mode

print(f"Lines with mode assignment: {len(line_modes)}")
mode_counts = Counter(line_modes.values())
print(f"  Mode A: {mode_counts['A']}, Mode B: {mode_counts['B']}")

# ========================================================================
# P6: n-TERMINAL MIDDLEs AT MODE TRANSITIONS
# ========================================================================
print(f"\n{'='*70}")
print("P6: n-TERMINAL MIDDLEs AT MODE A/B BOUNDARIES")
print(f"{'='*70}")

# Sort lines within each folio
folio_lines = defaultdict(list)
for key in line_modes:
    folio_lines[key[0]].append(key)

def line_sort_key(key):
    ln = key[1]
    try:
        return (int(ln), '')
    except ValueError:
        num = ''
        alpha = ''
        for c in ln:
            if c.isdigit():
                num += c
            else:
                alpha += c
        return (int(num) if num else 0, alpha)

for folio in folio_lines:
    folio_lines[folio].sort(key=line_sort_key)

# Find transition lines (where mode changes from previous line)
transition_lines = set()
non_transition_lines = set()

for folio, lines in folio_lines.items():
    for i in range(1, len(lines)):
        prev_mode = line_modes.get(lines[i-1])
        curr_mode = line_modes.get(lines[i])
        if prev_mode and curr_mode:
            if prev_mode != curr_mode:
                transition_lines.add(lines[i])
            else:
                non_transition_lines.add(lines[i])

print(f"\nTransition lines: {len(transition_lines)}")
print(f"Non-transition lines: {len(non_transition_lines)}")

# Count n-terminal MIDDLEs on each type
def n_terminal_rate(line_keys):
    n_total = 0
    n_nterm = 0
    for key in line_keys:
        for tok in line_data[key]:
            mid = tok['middle']
            if mid:
                n_total += 1
                if mid.endswith('n'):
                    n_nterm += 1
    return n_nterm, n_total

trans_n, trans_total = n_terminal_rate(transition_lines)
nontrans_n, nontrans_total = n_terminal_rate(non_transition_lines)

trans_rate = trans_n / trans_total if trans_total else 0
nontrans_rate = nontrans_n / nontrans_total if nontrans_total else 0

print(f"\nn-terminal MIDDLE rate:")
print(f"  Transition lines:     {trans_n}/{trans_total} = {trans_rate:.4f}")
print(f"  Non-transition lines: {nontrans_n}/{nontrans_total} = {nontrans_rate:.4f}")
if nontrans_rate > 0:
    print(f"  Ratio: {trans_rate/nontrans_rate:.3f}x")

# Chi-squared test
table = [[trans_n, trans_total - trans_n], [nontrans_n, nontrans_total - nontrans_n]]
chi2, p_chi, dof, expected = stats.chi2_contingency(table)
print(f"  Chi-squared: chi2={chi2:.3f}, p={p_chi:.4f}")

if p_chi < 0.05 and trans_rate > nontrans_rate:
    print(f"  RESULT: CONFIRMED - n-terminal MIDDLEs enriched at mode transitions")
elif p_chi < 0.05:
    print(f"  RESULT: SIGNIFICANT but INVERTED - n-terminal MIDDLEs depleted at transitions")
else:
    print(f"  RESULT: NULL - no significant difference")

# Also check: which specific n-terminal MIDDLEs appear at transitions?
trans_n_mids = Counter()
nontrans_n_mids = Counter()
for key in transition_lines:
    for tok in line_data[key]:
        if tok['middle'].endswith('n'):
            trans_n_mids[tok['middle']] += 1
for key in non_transition_lines:
    for tok in line_data[key]:
        if tok['middle'].endswith('n'):
            nontrans_n_mids[tok['middle']] += 1

print(f"\nTop n-terminal MIDDLEs at transitions vs non-transitions:")
all_n_mids = set(trans_n_mids.keys()) | set(nontrans_n_mids.keys())
for mid in sorted(all_n_mids, key=lambda m: -(trans_n_mids.get(m, 0) + nontrans_n_mids.get(m, 0)))[:10]:
    tc = trans_n_mids.get(mid, 0)
    nc = nontrans_n_mids.get(mid, 0)
    t_rate_m = tc / len(transition_lines) if transition_lines else 0
    n_rate_m = nc / len(non_transition_lines) if non_transition_lines else 0
    ratio = t_rate_m / n_rate_m if n_rate_m > 0 else 0
    print(f"  {mid:<12s} trans={tc:>5d} nontrans={nc:>5d} ratio={ratio:.2f}x")

# ========================================================================
# P7: o-INITIAL MIDDLEs AND APPARATUS (AZC) VOCABULARY
# ========================================================================
print(f"\n{'='*70}")
print("P7: o-INITIAL MIDDLEs AND APPARATUS VOCABULARY")
print(f"{'='*70}")

# Get AZC tokens
azc_tokens = [t for t in tx.azc() if '*' not in t.word and t.word.strip()]
azc_words = set(t.word for t in azc_tokens)

# Get B-only words (not in AZC)
b_words = set(t.word for t in tokens)
azc_exclusive = azc_words - b_words
azc_shared = azc_words & b_words

print(f"\nAZC tokens: {len(azc_tokens)}, unique words: {len(azc_words)}")
print(f"AZC-exclusive words: {len(azc_exclusive)}")
print(f"AZC-B shared words: {len(azc_shared)}")

# Extract MIDDLEs from AZC tokens
azc_middles = Counter()
for t in azc_tokens:
    m = morph.extract(t.word)
    if m.middle:
        azc_middles[m.middle] += 1

# Check o-initial rate in AZC vs B
b_middles = Counter()
for t in tokens:
    m = morph.extract(t.word)
    if m.middle:
        b_middles[m.middle] += 1

azc_o_init = sum(v for k, v in azc_middles.items() if k.startswith('o'))
azc_total = sum(azc_middles.values())
b_o_init = sum(v for k, v in b_middles.items() if k.startswith('o'))
b_total = sum(b_middles.values())

azc_o_rate = azc_o_init / azc_total if azc_total else 0
b_o_rate = b_o_init / b_total if b_total else 0

print(f"\no-initial MIDDLE rate:")
print(f"  AZC:      {azc_o_init}/{azc_total} = {azc_o_rate:.4f}")
print(f"  Currier B: {b_o_init}/{b_total} = {b_o_rate:.4f}")
if b_o_rate > 0:
    print(f"  AZC/B ratio: {azc_o_rate/b_o_rate:.3f}x")

table2 = [[azc_o_init, azc_total - azc_o_init], [b_o_init, b_total - b_o_init]]
if min(azc_o_init, azc_total - azc_o_init, b_o_init, b_total - b_o_init) > 0:
    chi2_7, p_7, _, _ = stats.chi2_contingency(table2)
    print(f"  Chi-squared: chi2={chi2_7:.3f}, p={p_7:.4f}")
else:
    chi2_7, p_7 = 0, 1
    print(f"  Insufficient data for chi-squared")

# Also: among B sections, does o-initial rate vary by section?
# Section H has highest apparatus diversity (C1249)
section_o = defaultdict(lambda: {'o': 0, 'total': 0})
for t in tokens:
    m = morph.extract(t.word)
    if m.middle:
        section_o[t.section]['total'] += 1
        if m.middle.startswith('o'):
            section_o[t.section]['o'] += 1

print(f"\no-initial MIDDLE rate by Currier B section:")
print(f"  {'Section':<10s} {'o-init':>8s} {'total':>8s} {'rate':>8s}")
print(f"  {'-'*36}")
for sec in sorted(section_o.keys()):
    d = section_o[sec]
    rate = d['o'] / d['total'] if d['total'] else 0
    print(f"  {sec:<10s} {d['o']:>8d} {d['total']:>8d} {rate:>7.4f}")

# Check: are o-initial MIDDLEs enriched in AZC-shared vocabulary?
shared_o_init = 0
shared_total = 0
exclusive_b_o_init = 0
exclusive_b_total = 0
for t in tokens:
    m = morph.extract(t.word)
    if m.middle:
        if t.word in azc_shared:
            shared_total += 1
            if m.middle.startswith('o'):
                shared_o_init += 1
        else:
            exclusive_b_total += 1
            if m.middle.startswith('o'):
                exclusive_b_o_init += 1

shared_rate = shared_o_init / shared_total if shared_total else 0
excl_rate = exclusive_b_o_init / exclusive_b_total if exclusive_b_total else 0
print(f"\no-initial rate in B tokens that also appear in AZC: {shared_o_init}/{shared_total} = {shared_rate:.4f}")
print(f"o-initial rate in B-only tokens:                    {exclusive_b_o_init}/{exclusive_b_total} = {excl_rate:.4f}")
if excl_rate > 0:
    print(f"Shared/exclusive ratio: {shared_rate/excl_rate:.3f}x")

if p_7 < 0.05 and azc_o_rate > b_o_rate:
    print(f"\n  RESULT: CONFIRMED - o-initial MIDDLEs enriched in AZC (apparatus)")
elif p_7 < 0.05:
    print(f"\n  RESULT: SIGNIFICANT but INVERTED")
else:
    print(f"\n  RESULT: NULL - no significant AZC enrichment for o-initial MIDDLEs")

# ========================================================================
# P8: f-ATOMS ENRICHED IN REGIME_3
# ========================================================================
print(f"\n{'='*70}")
print("P8: f-ATOM ENRICHMENT IN REGIME_3")
print(f"{'='*70}")

# Count f-containing tokens per regime
regime_f = defaultdict(lambda: {'f': 0, 'total': 0})
for t in tokens:
    folio = t.folio
    regime = regime_map.get(folio)
    if not regime:
        continue
    m = morph.extract(t.word)
    mid = m.middle or ''
    pfx = m.prefix or ''
    has_f = 'f' in mid or 'f' in pfx
    regime_f[regime]['total'] += 1
    if has_f:
        regime_f[regime]['f'] += 1

print(f"\nf-atom rate by REGIME:")
print(f"  {'REGIME':<12s} {'f-tokens':>10s} {'total':>8s} {'rate':>10s}")
print(f"  {'-'*42}")
regime_rates = {}
for reg in sorted(regime_f.keys()):
    d = regime_f[reg]
    rate = d['f'] / d['total'] if d['total'] else 0
    regime_rates[reg] = rate
    print(f"  {reg:<12s} {d['f']:>10d} {d['total']:>8d} {rate:>9.4f}")

# Is REGIME_3 the highest?
if regime_rates:
    max_regime = max(regime_rates, key=regime_rates.get)
    print(f"\n  Highest f-rate: {max_regime} ({regime_rates[max_regime]:.4f})")
    if max_regime == 'REGIME_3':
        print(f"  PREDICTION DIRECTION: CORRECT - REGIME_3 has highest f-rate")
    else:
        print(f"  PREDICTION DIRECTION: WRONG - {max_regime} has highest, not REGIME_3")

# Chi-squared across regimes
observed_f = [regime_f[r]['f'] for r in sorted(regime_f.keys())]
totals = [regime_f[r]['total'] for r in sorted(regime_f.keys())]
overall_f_rate = sum(observed_f) / sum(totals)
expected_f = [overall_f_rate * t for t in totals]
if all(e >= 5 for e in expected_f):
    chi2_8, p_8 = stats.chisquare(observed_f, expected_f)
    print(f"  Chi-squared (f across regimes): chi2={chi2_8:.3f}, p={p_8:.4f}")
else:
    print(f"  Expected counts too low for chi-squared, using Fisher's exact approach")
    # Fallback: just compare REGIME_3 vs rest
    r3_f = regime_f.get('REGIME_3', {}).get('f', 0)
    r3_total = regime_f.get('REGIME_3', {}).get('total', 0)
    rest_f = sum(d['f'] for r, d in regime_f.items() if r != 'REGIME_3')
    rest_total = sum(d['total'] for r, d in regime_f.items() if r != 'REGIME_3')
    table3 = [[r3_f, r3_total - r3_f], [rest_f, rest_total - rest_f]]
    chi2_8, p_8, _, _ = stats.chi2_contingency(table3)
    print(f"  REGIME_3 vs rest: chi2={chi2_8:.3f}, p={p_8:.4f}")

# Also break down by f in PREFIX vs f in MIDDLE
print(f"\nf-atom location breakdown by REGIME:")
regime_f_loc = defaultdict(lambda: {'f_pfx': 0, 'f_mid': 0, 'total': 0})
for t in tokens:
    folio = t.folio
    regime = regime_map.get(folio)
    if not regime:
        continue
    m = morph.extract(t.word)
    mid = m.middle or ''
    pfx = m.prefix or ''
    regime_f_loc[regime]['total'] += 1
    if 'f' in pfx:
        regime_f_loc[regime]['f_pfx'] += 1
    if 'f' in mid:
        regime_f_loc[regime]['f_mid'] += 1

print(f"  {'REGIME':<12s} {'f-PREFIX':>10s} {'f-MIDDLE':>10s} {'total':>8s} {'pfx_rate':>10s} {'mid_rate':>10s}")
print(f"  {'-'*55}")
for reg in sorted(regime_f_loc.keys()):
    d = regime_f_loc[reg]
    pr = d['f_pfx'] / d['total'] if d['total'] else 0
    mr = d['f_mid'] / d['total'] if d['total'] else 0
    print(f"  {reg:<12s} {d['f_pfx']:>10d} {d['f_mid']:>10d} {d['total']:>8d} {pr:>9.4f} {mr:>9.4f}")

# ========================================================================
# SUMMARY
# ========================================================================
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print(f"\nP6 (n at mode boundaries): ", end='')
if p_chi < 0.05 and trans_rate > nontrans_rate:
    print(f"CONFIRMED (ratio={trans_rate/nontrans_rate:.2f}x, p={p_chi:.4f})")
elif p_chi < 0.05:
    print(f"INVERTED (ratio={trans_rate/nontrans_rate:.2f}x, p={p_chi:.4f})")
else:
    print(f"NULL (ratio={trans_rate/nontrans_rate:.2f}x, p={p_chi:.4f})")

print(f"P7 (o-initial in AZC):     ", end='')
if p_7 < 0.05 and azc_o_rate > b_o_rate:
    print(f"CONFIRMED (AZC/B={azc_o_rate/b_o_rate:.2f}x, p={p_7:.4f})")
elif p_7 < 0.05:
    print(f"INVERTED (AZC/B={azc_o_rate/b_o_rate:.2f}x, p={p_7:.4f})")
else:
    print(f"NULL (AZC/B={azc_o_rate/b_o_rate:.2f}x, p={p_7:.4f})")

print(f"P8 (f in REGIME_3):        ", end='')
if regime_rates and max(regime_rates, key=regime_rates.get) == 'REGIME_3':
    print(f"DIRECTION CORRECT (R3={regime_rates.get('REGIME_3',0):.4f})")
else:
    print(f"DIRECTION WRONG (max={max_regime}={regime_rates.get(max_regime,0):.4f})")
