"""CH vs SH as SENSORY MODALITY DISCRIMINATOR.

Brunschwig hypothesis:
  ch = ACTIVE TEST (taste, touch, viscosity, finger test)
       You must INTERACT with the material to check it
  sh = PASSIVE OBSERVE (look, color, cloudiness, drip watching)
       You just WATCH without disturbing the process

If true, we should see independent confirming signals:

  1. POSITION: sh earlier (continuous monitoring), ch later (checkpoint testing)
  2. SUFFIX: sh + -ey/-y (visual confirmed/done), ch + -aiin/-ain (checkpoint)
  3. REGIME: ch peaks in R2 (balneum marie - sealed, must open to test),
            sh peaks in R3 (per ignem - visual monitoring of fire)
  4. BIGRAM: sh->ch common (look first, then test), ch->sh rare (test then look?)
  5. NEIGHBOR: sh near heat operations (watching fire), ch near collection (testing product)
  6. UNIQUE vs UNIVERSAL: Both should show this pattern regardless of middle spread
  7. LINE POSITION: sh spread throughout, ch concentrated at checkpoints
"""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
md = json.load(open('data/middle_dictionary.json', encoding='utf-8'))
regime_mapping = json.load(open('results/regime_folio_mapping.json', encoding='utf-8'))

folio_regime = {}
for regime, folios in regime_mapping.items():
    for f in folios:
        folio_regime[f] = regime

# Pre-compute positions
line_tokens = defaultdict(list)
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    line_tokens[(token.folio, token.line)].append(token)

token_positions = {}
for key, tokens in line_tokens.items():
    n = len(tokens)
    for i, tok in enumerate(tokens):
        pos = i / max(1, n - 1) if n > 1 else 0.5
        token_positions[(tok.folio, tok.line, i)] = pos

# Folio line counts for normalized line position
folio_max_line = defaultdict(int)
for (folio, line), tokens in line_tokens.items():
    try:
        line_num = int(line)
    except (ValueError, TypeError):
        line_num = 0
    if line_num > folio_max_line[folio]:
        folio_max_line[folio] = line_num

# Build sequential token lists per folio
folio_sequences = defaultdict(list)
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    m = morph.extract(token.word)
    folio_sequences[token.folio].append((token, m))

# ============================================================
# Collect data for ch vs sh
# ============================================================

ch_data = {
    'positions': [], 'line_numbers': [], 'suffixes': Counter(),
    'regimes': Counter(), 'next_prefix': Counter(), 'prev_prefix': Counter(),
    'next_middle_gloss': Counter(), 'prev_middle_gloss': Counter(),
    'unique_positions': [], 'universal_positions': [],
    'count': 0,
}
sh_data = {
    'positions': [], 'line_numbers': [], 'suffixes': Counter(),
    'regimes': Counter(), 'next_prefix': Counter(), 'prev_prefix': Counter(),
    'next_middle_gloss': Counter(), 'prev_middle_gloss': Counter(),
    'unique_positions': [], 'universal_positions': [],
    'count': 0,
}

# Middle spread classification
middle_folios = defaultdict(set)
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    m = morph.extract(token.word)
    if m.middle:
        middle_folios[m.middle].add(token.folio)

def spread_class(mid):
    nf = len(middle_folios.get(mid, set()))
    if nf >= 20: return 'universal'
    if nf >= 5: return 'regional'
    if nf >= 2: return 'concentrated'
    return 'unique'

# Positional collection
idx_tracker = defaultdict(int)
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    m = morph.extract(token.word)
    if m.prefix not in ('ch', 'sh'):
        idx_tracker[(token.folio, token.line)] += 1
        continue

    data = ch_data if m.prefix == 'ch' else sh_data
    data['count'] += 1

    # Suffix
    data['suffixes'][m.suffix or '(none)'] += 1

    # Regime
    regime = folio_regime.get(token.folio, 'UNKNOWN')
    data['regimes'][regime] += 1

    # Line position
    key = (token.folio, token.line)
    idx = idx_tracker[key]
    idx_tracker[key] += 1
    pos = token_positions.get((token.folio, token.line, idx))
    if pos is not None:
        data['positions'].append(pos)
        sc = spread_class(m.middle) if m.middle else 'none'
        if sc == 'unique':
            data['unique_positions'].append(pos)
        elif sc == 'universal':
            data['universal_positions'].append(pos)

    # Folio line position
    try:
        line_num = int(token.line)
        max_line = folio_max_line[token.folio]
        if max_line > 1:
            norm_line = (line_num - 1) / (max_line - 1)
        else:
            norm_line = 0.5
        data['line_numbers'].append(norm_line)
    except (ValueError, TypeError):
        pass

# Bigram collection
bigram_counts = Counter()
for folio, seq in folio_sequences.items():
    for i in range(len(seq) - 1):
        pfx1 = seq[i][1].prefix or ''
        pfx2 = seq[i+1][1].prefix or ''
        if pfx1 in ('ch', 'sh') and pfx2 in ('ch', 'sh'):
            bigram_counts[(pfx1, pfx2)] += 1

        # Neighbor analysis
        m_curr = seq[i][1]
        m_next = seq[i+1][1]

        if m_curr.prefix in ('ch', 'sh'):
            data = ch_data if m_curr.prefix == 'ch' else sh_data
            if m_next.prefix:
                data['next_prefix'][m_next.prefix] += 1
            if m_next.middle:
                gloss = md['middles'].get(m_next.middle, {}).get('gloss', '')
                if gloss:
                    data['next_middle_gloss'][gloss] += 1

        if m_next.prefix in ('ch', 'sh'):
            data = ch_data if m_next.prefix == 'ch' else sh_data
            if m_curr.prefix:
                data['prev_prefix'][m_curr.prefix] += 1
            if m_curr.middle:
                gloss = md['middles'].get(m_curr.middle, {}).get('gloss', '')
                if gloss:
                    data['prev_middle_gloss'][gloss] += 1

# ============================================================
# Print results
# ============================================================

print("=" * 90)
print("CH vs SH: SENSORY MODALITY DISCRIMINATION TEST")
print("=" * 90)
print(f"\n  Hypothesis: ch = ACTIVE TEST (taste/touch/interact)")
print(f"             sh = PASSIVE OBSERVE (look/watch)")
print(f"\n  ch tokens: {ch_data['count']}")
print(f"  sh tokens: {sh_data['count']}")

# ============================================================
# TEST 1: Position
# ============================================================

print(f"\n{'='*90}")
print(f"TEST 1: WITHIN-LINE POSITION")
print(f"{'='*90}")
print(f"\n  Prediction: sh earlier (continuous monitoring), ch later (checkpoint testing)\n")

for label, data in [('ch (active test)', ch_data), ('sh (passive observe)', sh_data)]:
    positions = data['positions']
    n = len(positions)
    mean = sum(positions) / n
    early = sum(1 for p in positions if p < 0.33) / n * 100
    mid = sum(1 for p in positions if 0.33 <= p < 0.67) / n * 100
    late = sum(1 for p in positions if p >= 0.67) / n * 100
    print(f"  {label:<25} mean={mean:.3f}  early={early:.1f}%  mid={mid:.1f}%  late={late:.1f}%")

ch_mean = sum(ch_data['positions']) / len(ch_data['positions'])
sh_mean = sum(sh_data['positions']) / len(sh_data['positions'])
delta = ch_mean - sh_mean
verdict = "PASS" if delta > 0.01 else "FAIL"
print(f"\n  Delta (ch - sh): {delta:+.3f}  [{verdict}]")
print(f"  ch appears {abs(delta)*100:.1f} percentage points {'LATER' if delta > 0 else 'EARLIER'} than sh")

# Also check by middle spread class
print(f"\n  Position by middle spread class:")
for sc_label, ch_pos, sh_pos in [
    ('Universal middles', ch_data['universal_positions'], sh_data['universal_positions']),
    ('Unique middles', ch_data['unique_positions'], sh_data['unique_positions']),
]:
    if ch_pos and sh_pos:
        ch_m = sum(ch_pos) / len(ch_pos)
        sh_m = sum(sh_pos) / len(sh_pos)
        print(f"    {sc_label:<22} ch={ch_m:.3f}  sh={sh_m:.3f}  delta={ch_m-sh_m:+.3f}")

# ============================================================
# TEST 2: Suffix distribution
# ============================================================

print(f"\n{'='*90}")
print(f"TEST 2: SUFFIX DISTRIBUTION")
print(f"{'='*90}")
print(f"\n  Prediction: sh + -ey/-y (visual confirmed)")
print(f"             ch + -aiin/-ain (checkpoint/taste test)\n")

SUFFIX_GLOSSES = {
    'y': 'done', 'dy': 'close', 'hy': 'verify/maintain',
    'ey': 'set', 'ly': 'settled', 'am': 'finalize',
    'aiin': 'check', 'ain': 'check', 'al': 'complete',
    'ar': 'close', 'or': 'portion', 's': 'next/boundary',
    'edy': 'thorough', 'r': 'input', 'iin': 'iterate',
    'ol': 'continue', '(none)': '(bare)',
}

ch_total = sum(ch_data['suffixes'].values())
sh_total = sum(sh_data['suffixes'].values())

print(f"  {'Suffix':<10} {'Gloss':<18} {'ch%':>8} {'sh%':>8} {'ch/sh':>8} {'Winner':<8}")
print(f"  {'-'*10} {'-'*18} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

all_suffixes = set(ch_data['suffixes'].keys()) | set(sh_data['suffixes'].keys())
suffix_rows = []
for sfx in sorted(all_suffixes, key=lambda s: -(ch_data['suffixes'].get(s, 0) + sh_data['suffixes'].get(s, 0))):
    ch_pct = ch_data['suffixes'].get(sfx, 0) / ch_total * 100
    sh_pct = sh_data['suffixes'].get(sfx, 0) / sh_total * 100
    ratio = ch_pct / sh_pct if sh_pct > 0 else float('inf')
    gloss = SUFFIX_GLOSSES.get(sfx, '?')
    winner = 'ch' if ratio > 1.3 else ('sh' if ratio < 0.77 else 'even')
    suffix_rows.append((sfx, gloss, ch_pct, sh_pct, ratio, winner))
    if ch_pct > 1 or sh_pct > 1:
        print(f"  {sfx:<10} {gloss:<18} {ch_pct:>7.1f}% {sh_pct:>7.1f}% {ratio:>7.2f}x {winner:<8}")

# Specific predictions
print(f"\n  Key predictions:")
ch_checkpoint = ch_data['suffixes'].get('aiin', 0) + ch_data['suffixes'].get('ain', 0)
sh_checkpoint = sh_data['suffixes'].get('aiin', 0) + sh_data['suffixes'].get('ain', 0)
ch_cp_pct = ch_checkpoint / ch_total * 100
sh_cp_pct = sh_checkpoint / sh_total * 100
verdict_cp = "PASS" if ch_cp_pct > sh_cp_pct * 1.3 else "FAIL"
print(f"    ch + checkpoint (-aiin/-ain): ch={ch_cp_pct:.1f}% vs sh={sh_cp_pct:.1f}%  [{verdict_cp}]")

ch_visual = ch_data['suffixes'].get('ey', 0) + ch_data['suffixes'].get('y', 0)
sh_visual = sh_data['suffixes'].get('ey', 0) + sh_data['suffixes'].get('y', 0)
ch_v_pct = ch_visual / ch_total * 100
sh_v_pct = sh_visual / sh_total * 100
verdict_v = "PASS" if sh_v_pct > ch_v_pct * 1.1 else "FAIL"
print(f"    sh + visual (-ey/-y):         ch={ch_v_pct:.1f}% vs sh={sh_v_pct:.1f}%  [{verdict_v}]")

ch_verify = ch_data['suffixes'].get('hy', 0)
sh_verify = sh_data['suffixes'].get('hy', 0)
ch_hy_pct = ch_verify / ch_total * 100
sh_hy_pct = sh_verify / sh_total * 100
print(f"    -hy (verify/maintain):        ch={ch_hy_pct:.1f}% vs sh={sh_hy_pct:.1f}%")

# ============================================================
# TEST 3: Regime distribution
# ============================================================

print(f"\n{'='*90}")
print(f"TEST 3: REGIME DISTRIBUTION")
print(f"{'='*90}")
print(f"\n  Prediction: ch peaks R2 (balneum marie - sealed, must open to test)")
print(f"             sh peaks R3 (per ignem - visual monitoring of fire)\n")

regime_totals = Counter()
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    r = folio_regime.get(token.folio)
    if r:
        regime_totals[r] += 1

print(f"  {'Regime':<12} {'ch rate':>10} {'sh rate':>10} {'ch/sh':>8}")
print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*8}")

for r_name in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    ch_rate = ch_data['regimes'].get(r_name, 0) / regime_totals.get(r_name, 1) * 100
    sh_rate = sh_data['regimes'].get(r_name, 0) / regime_totals.get(r_name, 1) * 100
    ratio = ch_rate / sh_rate if sh_rate > 0 else float('inf')
    print(f"  {r_name:<12} {ch_rate:>9.2f}% {sh_rate:>9.2f}% {ratio:>7.2f}x")

ch_r2 = ch_data['regimes'].get('REGIME_2', 0) / regime_totals.get('REGIME_2', 1) * 100
sh_r3 = sh_data['regimes'].get('REGIME_3', 0) / regime_totals.get('REGIME_3', 1) * 100
ch_r3 = ch_data['regimes'].get('REGIME_3', 0) / regime_totals.get('REGIME_3', 1) * 100
sh_r2 = sh_data['regimes'].get('REGIME_2', 0) / regime_totals.get('REGIME_2', 1) * 100

# Find ch peak and sh peak
ch_rates = {r: ch_data['regimes'].get(r, 0) / regime_totals.get(r, 1) * 100
            for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']}
sh_rates = {r: sh_data['regimes'].get(r, 0) / regime_totals.get(r, 1) * 100
            for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']}

ch_peak = max(ch_rates, key=ch_rates.get)
sh_peak = max(sh_rates, key=sh_rates.get)
print(f"\n  ch peaks: {ch_peak}")
print(f"  sh peaks: {sh_peak}")

# ============================================================
# TEST 4: Bigram sequences
# ============================================================

print(f"\n{'='*90}")
print(f"TEST 4: PREFIX BIGRAMS (ch/sh sequences)")
print(f"{'='*90}")
print(f"\n  Prediction: sh->ch common (look first, then test)")
print(f"             ch->sh less common (test then look back?)\n")

for (p1, p2), count in sorted(bigram_counts.items(), key=lambda x: -x[1]):
    print(f"  {p1} -> {p2}: {count}")

sh_ch = bigram_counts.get(('sh', 'ch'), 0)
ch_sh = bigram_counts.get(('ch', 'sh'), 0)
ratio = sh_ch / ch_sh if ch_sh > 0 else float('inf')
verdict_bigram = "PASS" if ratio > 1.2 else "FAIL"
print(f"\n  sh->ch / ch->sh ratio: {ratio:.2f}x  [{verdict_bigram}]")
print(f"  (look then test vs test then look)")

# ============================================================
# TEST 5: What operations surround ch vs sh?
# ============================================================

print(f"\n{'='*90}")
print(f"TEST 5: NEIGHBORING OPERATIONS")
print(f"{'='*90}")
print(f"\n  Prediction: sh near heat (watching fire), ch near collection (testing product)\n")

print(f"  PRECEDED BY:")
print(f"  {'Operation':<25} {'before ch':>10} {'before sh':>10} {'ch/sh':>8}")
print(f"  {'-'*25} {'-'*10} {'-'*10} {'-'*8}")

ch_prev_total = sum(ch_data['prev_middle_gloss'].values())
sh_prev_total = sum(sh_data['prev_middle_gloss'].values())
all_prev = set(ch_data['prev_middle_gloss'].keys()) | set(sh_data['prev_middle_gloss'].keys())

for gloss in sorted(all_prev, key=lambda g: -(ch_data['prev_middle_gloss'].get(g, 0) + sh_data['prev_middle_gloss'].get(g, 0)))[:15]:
    ch_pct = ch_data['prev_middle_gloss'].get(gloss, 0) / ch_prev_total * 100 if ch_prev_total else 0
    sh_pct = sh_data['prev_middle_gloss'].get(gloss, 0) / sh_prev_total * 100 if sh_prev_total else 0
    ratio = ch_pct / sh_pct if sh_pct > 0 else float('inf')
    marker = '<-- ch' if ratio > 1.5 else ('<-- sh' if ratio < 0.67 else '')
    print(f"  {gloss:<25} {ch_pct:>9.1f}% {sh_pct:>9.1f}% {ratio:>7.2f}x {marker}")

print(f"\n  FOLLOWED BY:")
print(f"  {'Operation':<25} {'after ch':>10} {'after sh':>10} {'ch/sh':>8}")
print(f"  {'-'*25} {'-'*10} {'-'*10} {'-'*8}")

ch_next_total = sum(ch_data['next_middle_gloss'].values())
sh_next_total = sum(sh_data['next_middle_gloss'].values())
all_next = set(ch_data['next_middle_gloss'].keys()) | set(sh_data['next_middle_gloss'].keys())

for gloss in sorted(all_next, key=lambda g: -(ch_data['next_middle_gloss'].get(g, 0) + sh_data['next_middle_gloss'].get(g, 0)))[:15]:
    ch_pct = ch_data['next_middle_gloss'].get(gloss, 0) / ch_next_total * 100 if ch_next_total else 0
    sh_pct = sh_data['next_middle_gloss'].get(gloss, 0) / sh_next_total * 100 if sh_next_total else 0
    ratio = ch_pct / sh_pct if sh_pct > 0 else float('inf')
    marker = '<-- ch' if ratio > 1.5 else ('<-- sh' if ratio < 0.67 else '')
    print(f"  {gloss:<25} {ch_pct:>9.1f}% {sh_pct:>9.1f}% {ratio:>7.2f}x {marker}")

# ============================================================
# TEST 6: Folio line position (program-level)
# ============================================================

print(f"\n{'='*90}")
print(f"TEST 6: FOLIO LINE POSITION (where in the program)")
print(f"{'='*90}")
print(f"\n  Prediction: sh distributed throughout (always watching)")
print(f"             ch concentrated at specific stages (testing at checkpoints)\n")

for label, data in [('ch (active test)', ch_data), ('sh (passive observe)', sh_data)]:
    lines = data['line_numbers']
    n = len(lines)
    if n == 0:
        continue
    mean = sum(lines) / n
    first = sum(1 for l in lines if l < 0.25) / n * 100
    second = sum(1 for l in lines if 0.25 <= l < 0.5) / n * 100
    third = sum(1 for l in lines if 0.5 <= l < 0.75) / n * 100
    fourth = sum(1 for l in lines if l >= 0.75) / n * 100
    print(f"  {label:<25} mean={mean:.3f}  Q1={first:.1f}%  Q2={second:.1f}%  Q3={third:.1f}%  Q4={fourth:.1f}%")

# Compute variance (spread)
import math
ch_var = sum((l - sum(ch_data['line_numbers'])/len(ch_data['line_numbers']))**2
             for l in ch_data['line_numbers']) / len(ch_data['line_numbers'])
sh_var = sum((l - sum(sh_data['line_numbers'])/len(sh_data['line_numbers']))**2
             for l in sh_data['line_numbers']) / len(sh_data['line_numbers'])

print(f"\n  Line position variance: ch={ch_var:.4f}  sh={sh_var:.4f}")
print(f"  {'ch more concentrated' if ch_var < sh_var else 'sh more concentrated'}")

# ============================================================
# TEST 7: Position histogram (fine-grained)
# ============================================================

print(f"\n{'='*90}")
print(f"TEST 7: WITHIN-LINE POSITION HISTOGRAM")
print(f"{'='*90}\n")

print(f"  {'Bin':<8} {'ch%':>8} {'sh%':>8} {'ch':>15} {'sh':>15}")
print(f"  {'-'*8} {'-'*8} {'-'*8} {'-'*15} {'-'*15}")

ch_n = len(ch_data['positions'])
sh_n = len(sh_data['positions'])

for bin_start in [i/10 for i in range(10)]:
    bin_end = bin_start + 0.1
    ch_in = sum(1 for p in ch_data['positions'] if bin_start <= p < bin_end)
    sh_in = sum(1 for p in sh_data['positions'] if bin_start <= p < bin_end)
    ch_pct = ch_in / ch_n * 100
    sh_pct = sh_in / sh_n * 100
    ch_bar = '#' * int(ch_pct)
    sh_bar = '#' * int(sh_pct)
    print(f"  {bin_start:.1f}    {ch_pct:>7.1f}% {sh_pct:>7.1f}% {ch_bar:<15} {sh_bar:<15}")

# ============================================================
# SUMMARY SCORECARD
# ============================================================

print(f"\n{'='*90}")
print(f"SCORECARD: ch = ACTIVE TEST vs sh = PASSIVE OBSERVE")
print(f"{'='*90}\n")

tests = [
    ("1. Position (sh earlier)",
     "PASS" if sh_mean < ch_mean - 0.01 else "FAIL",
     f"ch={ch_mean:.3f} sh={sh_mean:.3f} delta={ch_mean-sh_mean:+.3f}"),
    ("2. Suffix -aiin/-ain (ch > sh)",
     "PASS" if ch_cp_pct > sh_cp_pct * 1.2 else "FAIL",
     f"ch={ch_cp_pct:.1f}% sh={sh_cp_pct:.1f}%"),
    ("3. Suffix -ey/-y (sh > ch)",
     "PASS" if sh_v_pct > ch_v_pct * 1.05 else "FAIL",
     f"ch={ch_v_pct:.1f}% sh={sh_v_pct:.1f}%"),
    ("4. Bigram sh->ch > ch->sh",
     "PASS" if sh_ch > ch_sh * 1.1 else "FAIL",
     f"sh->ch={sh_ch} ch->sh={ch_sh} ratio={ratio:.2f}x"),
    ("5. ch more checkpoint-like",
     "PASS" if ch_var < sh_var else "FAIL",
     f"ch_var={ch_var:.4f} sh_var={sh_var:.4f}"),
]

pass_count = sum(1 for _, v, _ in tests if v == "PASS")
print(f"  {'Test':<35} {'Result':<8} {'Evidence'}")
print(f"  {'-'*35} {'-'*8} {'-'*40}")
for name, result, evidence in tests:
    print(f"  {name:<35} [{result}]   {evidence}")

print(f"\n  TOTAL: {pass_count}/{len(tests)} PASS")
verdict = "STRONG" if pass_count >= 4 else "MODERATE" if pass_count >= 3 else "WEAK"
print(f"  Verdict: {verdict} support for ch=active test, sh=passive observe")
