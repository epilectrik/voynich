"""
F-F10: Alternative Discrimination (DECISIVE) -- 4 discriminants to score H1/H2/H3.

D1: Post-state-change timing (ACTOR/RESPONDER/NEUTRAL)
    H1 "flag": NEUTRAL >= 35% or ACTOR < 35% (sentinel stays put)
    H2 "format": ACTOR > 30% (active formatter)
    H3 "fill": NEUTRAL >= 40% (passive filler)

D2: R4 PRECISION enrichment
    H1 "flag": R4 >= 1.5x (marking used precisely)
    H2 "format": R4 >= 1.5x (format = precision)
    H3 "fill": R4 1.0-2.0x (generic)

D3: Mean line position
    H1 "flag": 0.45-0.65 (mid-line sentinel)
    H2 "format": 0.40-0.60 (early-to-mid structural)
    H3 "fill": 0.45-0.65 (mid-line loading)

D4: Line-1 enrichment
    H1 "flag": >= 20% (folio opener association)
    H2 "format": >= 20% (format at headers)
    H3 "fill": < 20% (fill is body operation)

Scoring: each discriminant awards points to matching hypotheses.
Pass: H1 scores >= 2/4.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, BFolioDecoder, CategoryClassifier

# -- Load data -----------------------------------------------------------------
tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()
decoder = BFolioDecoder()

CATEGORIES = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
              'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']

print("=" * 72)
print("F-F10: Alternative Discrimination -- 4 tests for H1/H2/H3")
print("=" * 72)
print()

# -- Gather Currier B tokens with line structure --------------------------------
line_tokens = defaultdict(list)
all_b_tokens = []

for token in tx.currier_b():
    m = morph.extract(token.word)
    if m is None or m.middle is None:
        continue
    ta = decoder.analyze_token(token.word)
    line_tokens[(token.folio, token.line)].append({
        'word': token.word, 'morph': m, 'folio': token.folio,
        'line': token.line, 'section': token.section,
        'macro_state': ta.macro_state if ta else None,
    })
    all_b_tokens.append({
        'word': token.word, 'morph': m, 'folio': token.folio,
        'line': token.line, 'section': token.section,
        'macro_state': ta.macro_state if ta else None,
    })

# Build folio regime lookup
folio_regimes = {}
for f in set(t['folio'] for t in all_b_tokens):
    fa = decoder.analyze_folio(f)
    if fa and fa.regime is not None:
        folio_regimes[f] = fa.regime

# Identify f-initial tokens
f_initial_tokens = [t for t in all_b_tokens if t['morph'].middle and t['morph'].middle[0] == 'f']

print(f"Total Currier B tokens: {len(all_b_tokens)}")
print(f"f-initial MIDDLE tokens: {len(f_initial_tokens)}")
print()

# -- D1: Post-state-change timing ----------------------------------------------
print("-" * 72)
print("D1: Post-state-change timing")
print("-" * 72)
print()

actor_count = 0
responder_count = 0
neutral_count = 0
d1_total = 0

for key in sorted(line_tokens.keys()):
    tokens_in_line = line_tokens[key]

    for idx, tok in enumerate(tokens_in_line):
        mid = tok['morph'].middle
        if not mid or mid[0] != 'f':
            continue

        curr_state = tok['macro_state']

        # First token in line - no previous context
        if idx == 0:
            neutral_count += 1
            d1_total += 1
            continue

        prev_state = tokens_in_line[idx - 1]['macro_state']

        if prev_state is None or curr_state is None:
            neutral_count += 1
            d1_total += 1
            continue

        if prev_state != curr_state:
            # State change just happened - this token is a RESPONDER
            responder_count += 1
        elif idx >= 2:
            prev2_state = tokens_in_line[idx - 2]['macro_state']
            if prev2_state is not None and prev2_state != prev_state:
                actor_count += 1
            else:
                neutral_count += 1
        else:
            neutral_count += 1
        d1_total += 1

if d1_total > 0:
    actor_pct = actor_count / d1_total * 100
    responder_pct = responder_count / d1_total * 100
    neutral_pct = neutral_count / d1_total * 100
else:
    actor_pct = responder_pct = neutral_pct = 0.0

print(f"  f-initial timing (N={d1_total}):")
print(f"    ACTOR (precedes change):    {actor_count:>4} ({actor_pct:.1f}%)")
print(f"    RESPONDER (follows change): {responder_count:>4} ({responder_pct:.1f}%)")
print(f"    NEUTRAL (no change):        {neutral_count:>4} ({neutral_pct:.1f}%)")
print()

# D1 scoring
d1_h1 = neutral_pct >= 35.0 or actor_pct < 35.0
d1_h2 = actor_pct > 30.0
d1_h3 = neutral_pct >= 40.0

print(f"  H1 'flag' (NEUTRAL>=35% or ACTOR<35%): {'MATCH' if d1_h1 else 'NO'}")
print(f"  H2 'format' (ACTOR >30%):              {'MATCH' if d1_h2 else 'NO'}")
print(f"  H3 'fill' (NEUTRAL >=40%):             {'MATCH' if d1_h3 else 'NO'}")
print(f"  Controls: p timing ~26.7% ACTOR, c timing ~31.6% ACTOR")
print()

# -- D2: R4 PRECISION enrichment -----------------------------------------------
print("-" * 72)
print("D2: R4 PRECISION enrichment")
print("-" * 72)
print()

regime_f_counts = defaultdict(int)
regime_total_counts = defaultdict(int)

for tok in all_b_tokens:
    folio = tok['folio']
    regime = folio_regimes.get(folio)
    if regime is None:
        continue
    regime_total_counts[regime] += 1
    if tok['morph'].middle and tok['morph'].middle[0] == 'f':
        regime_f_counts[regime] += 1

print(f"  {'REGIME':<14} {'f-init':>7} {'total':>7} {'rate%':>7} {'enrichment':>11}")
print(f"  {'-'*14} {'-'*7} {'-'*7} {'-'*7} {'-'*11}")

# Compute overall f rate for enrichment
total_f = sum(regime_f_counts.values())
total_all = sum(regime_total_counts.values())
overall_f_rate = total_f / total_all if total_all > 0 else 0.0

r4_enrichment = 0.0
for regime in sorted(regime_total_counts.keys()):
    f_ct = regime_f_counts[regime]
    tot = regime_total_counts[regime]
    rate = f_ct / tot if tot > 0 else 0.0
    enrich = rate / overall_f_rate if overall_f_rate > 0 else 0.0
    if '4' in str(regime):
        r4_enrichment = enrich
    print(f"  {regime:<14} {f_ct:>7} {tot:>7} {rate*100:>6.2f}% {enrich:>10.2f}x")

print(f"\n  Overall f-initial rate: {overall_f_rate*100:.3f}%")
print(f"  R4 enrichment: {r4_enrichment:.2f}x")
print()

# D2 scoring
d2_h1 = r4_enrichment >= 1.5
d2_h2 = r4_enrichment >= 1.5
d2_h3 = 1.0 <= r4_enrichment <= 2.0

print(f"  H1 'flag' (R4 >= 1.5x):    {'MATCH' if d2_h1 else 'NO'}")
print(f"  H2 'format' (R4 >= 1.5x):  {'MATCH' if d2_h2 else 'NO'}")
print(f"  H3 'fill' (R4 1.0-2.0x):   {'MATCH' if d2_h3 else 'NO'}")
print()

# -- D3: Mean line position ----------------------------------------------------
print("-" * 72)
print("D3: Mean line position of f-initial tokens")
print("-" * 72)
print()

positions = []
for key in sorted(line_tokens.keys()):
    tokens_in_line = line_tokens[key]
    n_line = len(tokens_in_line)
    if n_line < 2:
        continue
    for idx, tok in enumerate(tokens_in_line):
        if tok['morph'].middle and tok['morph'].middle[0] == 'f':
            pos = idx / (n_line - 1)
            positions.append(pos)

if positions:
    mean_pos = sum(positions) / len(positions)
    var = sum((p - mean_pos) ** 2 for p in positions) / len(positions)
    std_pos = var ** 0.5
else:
    mean_pos = 0.0
    std_pos = 0.0

print(f"  f-initial mean position: {mean_pos:.3f} +/- {std_pos:.3f} (N={len(positions)})")
print()

# D3 scoring
d3_h1 = 0.45 <= mean_pos <= 0.65
d3_h2 = 0.40 <= mean_pos <= 0.60
d3_h3 = 0.45 <= mean_pos <= 0.65

print(f"  H1 'flag' (0.45-0.65):    {'MATCH' if d3_h1 else 'NO'}")
print(f"  H2 'format' (0.40-0.60):  {'MATCH' if d3_h2 else 'NO'}")
print(f"  H3 'fill' (0.45-0.65):    {'MATCH' if d3_h3 else 'NO'}")
print()

# -- D4: Line-1 enrichment ----------------------------------------------------
print("-" * 72)
print("D4: Line-1 enrichment of f-initial tokens")
print("-" * 72)
print()

# Count f-initial tokens in line 1 vs all lines
f_line1 = 0
f_total = 0
all_line1 = 0
all_total = 0

for tok in all_b_tokens:
    all_total += 1
    if tok['line'] == '1':
        all_line1 += 1
    if tok['morph'].middle and tok['morph'].middle[0] == 'f':
        f_total += 1
        if tok['line'] == '1':
            f_line1 += 1

f_line1_frac = f_line1 / f_total * 100 if f_total > 0 else 0.0
baseline_line1_frac = all_line1 / all_total * 100 if all_total > 0 else 0.0
line1_enrichment = f_line1_frac / baseline_line1_frac if baseline_line1_frac > 0 else 0.0

print(f"  f-initial in line 1: {f_line1}/{f_total} = {f_line1_frac:.1f}%")
print(f"  Baseline line 1:     {all_line1}/{all_total} = {baseline_line1_frac:.1f}%")
print(f"  Line-1 enrichment:   {line1_enrichment:.2f}x")
print()

# D4 scoring: >= 20% of f-initial tokens in line 1
d4_h1 = f_line1_frac >= 20.0
d4_h2 = f_line1_frac >= 20.0
d4_h3 = f_line1_frac < 20.0

print(f"  H1 'flag' (>= 20%):   {'MATCH' if d4_h1 else 'NO'}")
print(f"  H2 'format' (>= 20%): {'MATCH' if d4_h2 else 'NO'}")
print(f"  H3 'fill' (< 20%):    {'MATCH' if d4_h3 else 'NO'}")
print()

# -- Overall scoring -----------------------------------------------------------
print("=" * 72)
print("OVERALL SCORING")
print("=" * 72)
print()

h1_score = sum([d1_h1, d2_h1, d3_h1, d4_h1])
h2_score = sum([d1_h2, d2_h2, d3_h2, d4_h2])
h3_score = sum([d1_h3, d2_h3, d3_h3, d4_h3])

print(f"  {'Discriminant':<30} {'H1 flag':>8} {'H2 fmt':>8} {'H3 fill':>8}")
print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*8}")
print(f"  {'D1: Post-state timing':<30} {'MATCH' if d1_h1 else '-':>8} {'MATCH' if d1_h2 else '-':>8} {'MATCH' if d1_h3 else '-':>8}")
print(f"  {'D2: R4 enrichment':<30} {'MATCH' if d2_h1 else '-':>8} {'MATCH' if d2_h2 else '-':>8} {'MATCH' if d2_h3 else '-':>8}")
print(f"  {'D3: Line position':<30} {'MATCH' if d3_h1 else '-':>8} {'MATCH' if d3_h2 else '-':>8} {'MATCH' if d3_h3 else '-':>8}")
print(f"  {'D4: Line-1 enrichment':<30} {'MATCH' if d4_h1 else '-':>8} {'MATCH' if d4_h2 else '-':>8} {'MATCH' if d4_h3 else '-':>8}")
print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*8}")
print(f"  {'TOTAL':<30} {h1_score:>6}/4 {h2_score:>6}/4 {h3_score:>6}/4")
print()

overall_pass = h1_score >= 2
print(f"Pass criterion: H1 >= 2/4: {'PASS' if overall_pass else 'FAIL'}")
print()

# Best hypothesis
best_score = max(h1_score, h2_score, h3_score)
winners = []
if h1_score == best_score:
    winners.append("H1 'flag'")
if h2_score == best_score:
    winners.append("H2 'format'")
if h3_score == best_score:
    winners.append("H3 'fill'")

print(f"Best hypothesis: {' / '.join(winners)} ({best_score}/4)")
