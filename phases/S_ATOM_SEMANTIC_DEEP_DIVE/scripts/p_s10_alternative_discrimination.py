"""
S-S10: Alternative Discrimination — 4 discriminants to score H1/H2/H3.

D1: Post-state-change timing (ACTOR/RESPONDER/NEUTRAL)
D2: R4 PRECISION enrichment
D3: Mean line position
D4: sh-family (Xsh compounds) MONITORING fraction

Scoring: each discriminant awards points to matching hypotheses.
Pass: H1 scores >= 2/4.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, BFolioDecoder, CategoryClassifier

# ── Load data ──────────────────────────────────────────────────────────────
tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()
decoder = BFolioDecoder()

CATEGORIES = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
              'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']

print("=" * 72)
print("S-S10: Alternative Discrimination -- 4 tests for H1/H2/H3")
print("=" * 72)
print()

# ── Gather Currier B tokens with line structure ────────────────────────────
# Build line-indexed structure: {(folio, line): [token_list]}
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

# Identify s-initial tokens
s_initial_tokens = [t for t in all_b_tokens if t['morph'].middle and t['morph'].middle[0] == 's']

print(f"Total Currier B tokens: {len(all_b_tokens)}")
print(f"s-initial MIDDLE tokens: {len(s_initial_tokens)}")
print()

# ── D1: Post-state-change timing ──────────────────────────────────────────
print("-" * 72)
print("D1: Post-state-change timing")
print("-" * 72)
print()

# Identify state-change boundaries using BFolioDecoder
# A "state change" is when consecutive tokens change macro-state
actor_count = 0
responder_count = 0
neutral_count = 0
d1_total = 0

for key in sorted(line_tokens.keys()):
    tokens_in_line = line_tokens[key]

    for idx, tok in enumerate(tokens_in_line):
        mid = tok['morph'].middle
        if not mid or mid[0] != 's':
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

print(f"  s-initial timing (N={d1_total}):")
print(f"    ACTOR (precedes change):    {actor_count:>4} ({actor_pct:.1f}%)")
print(f"    RESPONDER (follows change): {responder_count:>4} ({responder_pct:.1f}%)")
print(f"    NEUTRAL (no change):        {neutral_count:>4} ({neutral_pct:.1f}%)")
print()

# D1 scoring
d1_h1 = 35.0 <= neutral_pct <= 55.0 or actor_pct < 35.0
d1_h2 = responder_pct > 55.0
d1_h3 = 35.0 <= neutral_pct <= 55.0

print(f"  H1 'sequence' (NEUTRAL 35-55% or ACTOR<35%): {'MATCH' if d1_h1 else 'NO'}")
print(f"  H2 'sift' (RESPONDER >55%):                  {'MATCH' if d1_h2 else 'NO'}")
print(f"  H3 'step' (NEUTRAL 35-55%):                  {'MATCH' if d1_h3 else 'NO'}")
print(f"  Controls: p timing 26.7% ACTOR, c timing 31.6% ACTOR")
print()

# ── D2: R4 PRECISION enrichment ───────────────────────────────────────────
print("-" * 72)
print("D2: R4 PRECISION enrichment")
print("-" * 72)
print()

regime_s_counts = defaultdict(int)
regime_total_counts = defaultdict(int)

for tok in all_b_tokens:
    folio = tok['folio']
    regime = folio_regimes.get(folio)
    if regime is None:
        continue
    regime_total_counts[regime] += 1
    if tok['morph'].middle and tok['morph'].middle[0] == 's':
        regime_s_counts[regime] += 1

print(f"  {'REGIME':<12} {'s-init':>7} {'total':>7} {'rate%':>7} {'enrichment':>11}")
print(f"  {'-'*12} {'-'*7} {'-'*7} {'-'*7} {'-'*11}")

# Compute overall s rate for enrichment
total_s = sum(regime_s_counts.values())
total_all = sum(regime_total_counts.values())
overall_s_rate = total_s / total_all if total_all > 0 else 0.0

r4_enrichment = 0.0
for regime in sorted(regime_total_counts.keys()):
    s_ct = regime_s_counts[regime]
    tot = regime_total_counts[regime]
    rate = s_ct / tot if tot > 0 else 0.0
    enrich = rate / overall_s_rate if overall_s_rate > 0 else 0.0
    if '4' in str(regime):
        r4_enrichment = enrich
    print(f"  {regime:<14} {s_ct:>7} {tot:>7} {rate*100:>6.2f}% {enrich:>10.2f}x")

print(f"\n  Overall s-initial rate: {overall_s_rate*100:.2f}%")
print(f"  R4 enrichment: {r4_enrichment:.2f}x")
print()

# D2 scoring
d2_h1 = r4_enrichment >= 2.0
d2_h2 = r4_enrichment >= 2.0
d2_h3 = 1.5 <= r4_enrichment <= 3.0

print(f"  H1 'sequence' (R4 >= 2.0x): {'MATCH' if d2_h1 else 'NO'}")
print(f"  H2 'sift' (R4 >= 2.0x):     {'MATCH' if d2_h2 else 'NO'}")
print(f"  H3 'step' (R4 1.5-3.0x):    {'MATCH' if d2_h3 else 'NO'}")
print()

# ── D3: Mean line position ────────────────────────────────────────────────
print("-" * 72)
print("D3: Mean line position of s-initial tokens")
print("-" * 72)
print()

positions = []
for key in sorted(line_tokens.keys()):
    tokens_in_line = line_tokens[key]
    n_line = len(tokens_in_line)
    if n_line < 2:
        continue
    for idx, tok in enumerate(tokens_in_line):
        if tok['morph'].middle and tok['morph'].middle[0] == 's':
            pos = idx / (n_line - 1)
            positions.append(pos)

if positions:
    mean_pos = sum(positions) / len(positions)
    # Compute std
    var = sum((p - mean_pos) ** 2 for p in positions) / len(positions)
    std_pos = var ** 0.5
else:
    mean_pos = 0.0
    std_pos = 0.0

print(f"  s-initial mean position: {mean_pos:.3f} +/- {std_pos:.3f} (N={len(positions)})")
print()

# D3 scoring
d3_h1 = 0.45 <= mean_pos <= 0.65
d3_h2 = 0.50 <= mean_pos <= 0.70
d3_h3 = 0.35 <= mean_pos <= 0.55

print(f"  H1 'sequence' (0.45-0.65): {'MATCH' if d3_h1 else 'NO'}")
print(f"  H2 'sift' (0.50-0.70):     {'MATCH' if d3_h2 else 'NO'}")
print(f"  H3 'step' (0.35-0.55):     {'MATCH' if d3_h3 else 'NO'}")
print()

# ── D4: sh-family (Xsh compounds) MONITORING fraction ─────────────────────
print("-" * 72)
print("D4: Xsh compound (ksh, lsh, osh, tsh, ...) MONITORING fraction")
print("-" * 72)
print()

# Find tokens whose MIDDLE contains "sh" junction but initial atom is NOT s
# i.e., compounds like ksh, lsh, osh, tsh (NOT standalone sh)
xsh_cats = defaultdict(int)
xsh_total = 0
xsh_examples = defaultdict(list)

for tok in all_b_tokens:
    mid = tok['morph'].middle
    if not mid or len(mid) < 3:
        continue
    # Must contain 'sh' but not start with 's'
    if 'sh' in mid and mid[0] != 's':
        cat = cc.classify(mid)
        if cat and cat != 'UNK':
            xsh_cats[cat] += 1
            xsh_total += 1
            if len(xsh_examples[mid]) < 3:
                xsh_examples[mid].append(tok['word'])

print(f"  Xsh compounds found: {xsh_total} tokens")
print(f"  Unique MIDDLEs: {len(xsh_examples)}")

if xsh_examples:
    print("  Examples:")
    for mid in sorted(xsh_examples.keys(), key=lambda x: -len(xsh_examples.get(x, []))):
        examples = xsh_examples[mid]
        print(f"    {mid}: {', '.join(examples[:3])}")
        if len(list(xsh_examples.keys())) > 8:
            break

print()
if xsh_total > 0:
    print(f"  Category distribution:")
    for cat in CATEGORIES:
        ct = xsh_cats.get(cat, 0)
        pct = ct / xsh_total * 100
        marker = " <--" if cat == 'MONITORING' else ""
        print(f"    {cat:<14}: {ct:>4} ({pct:>5.1f}%){marker}")

    mon_frac = xsh_cats.get('MONITORING', 0) / xsh_total * 100
else:
    mon_frac = 0.0

print(f"\n  MONITORING fraction: {mon_frac:.1f}%")
print()

# D4 scoring
d4_h1 = 40.0 <= mon_frac <= 70.0
d4_h2 = mon_frac > 70.0
d4_h3 = 40.0 <= mon_frac <= 65.0

print(f"  H1 'sequence' (40-70%): {'MATCH' if d4_h1 else 'NO'}")
print(f"  H2 'sift' (>70%):       {'MATCH' if d4_h2 else 'NO'}")
print(f"  H3 'step' (40-65%):     {'MATCH' if d4_h3 else 'NO'}")
print()

# ── Overall scoring ───────────────────────────────────────────────────────
print("=" * 72)
print("OVERALL SCORING")
print("=" * 72)
print()

h1_score = sum([d1_h1, d2_h1, d3_h1, d4_h1])
h2_score = sum([d1_h2, d2_h2, d3_h2, d4_h2])
h3_score = sum([d1_h3, d2_h3, d3_h3, d4_h3])

print(f"  {'Discriminant':<30} {'H1 seq':>8} {'H2 sift':>8} {'H3 step':>8}")
print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*8}")
print(f"  {'D1: Post-state timing':<30} {'MATCH' if d1_h1 else '-':>8} {'MATCH' if d1_h2 else '-':>8} {'MATCH' if d1_h3 else '-':>8}")
print(f"  {'D2: R4 enrichment':<30} {'MATCH' if d2_h1 else '-':>8} {'MATCH' if d2_h2 else '-':>8} {'MATCH' if d2_h3 else '-':>8}")
print(f"  {'D3: Line position':<30} {'MATCH' if d3_h1 else '-':>8} {'MATCH' if d3_h2 else '-':>8} {'MATCH' if d3_h3 else '-':>8}")
print(f"  {'D4: Xsh MON fraction':<30} {'MATCH' if d4_h1 else '-':>8} {'MATCH' if d4_h2 else '-':>8} {'MATCH' if d4_h3 else '-':>8}")
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
    winners.append("H1 'sequence'")
if h2_score == best_score:
    winners.append("H2 'sift'")
if h3_score == best_score:
    winners.append("H3 'step'")

print(f"Best hypothesis: {' / '.join(winners)} ({best_score}/4)")
