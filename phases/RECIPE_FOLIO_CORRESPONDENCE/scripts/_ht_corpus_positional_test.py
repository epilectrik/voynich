"""
HT Articulator Positional Test — Corpus-Wide (all 83 Currier B folios)

Hypothesis: HT token articulators fall into two positional groups:
  LINE-OPENERS (p, t, f, d): predominantly line-initial (>50%)
    → monitoring directives: "before anything, check THIS"
  LINE-EMBEDDED (l, r): predominantly interior (<15% initial)
    → monitoring annotations: "while doing this, watch THIS"
  y: mixed (most common articulator, does both)
  k, s: secondary patterns

Test: Does the two-group positional split hold across all B folios,
or is it an artifact of f75r specifically?

Pass criteria:
  - p, t, f, d articulators: >50% line-initial across corpus
  - l, r articulators: <20% line-initial across corpus
  - The split is statistically significant (chi-squared)
"""

import sys, os, io
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES

tx = Transcript()
morph = Morphology()

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]
print(f"Currier B tokens: {len(all_b)}")

# ═══ 1. IDENTIFY ALL HT TOKENS AND THEIR LINE POSITIONS ═══

# Build line-position index: for each token, is it line-initial, interior, or final?
# Group by folio+line to get position
folio_line_tokens = defaultdict(list)
for t in all_b:
    folio_line_tokens[(t.folio, t.line)].append(t)

# Now classify each HT token
ht_data = []  # (token, morph, articulator, position, folio, line)

for (folio, line), line_toks in folio_line_tokens.items():
    for idx, t in enumerate(line_toks):
        m = morph.extract(t.word)
        if m.articulator:
            if idx == 0:
                pos = 'INITIAL'
            elif idx == len(line_toks) - 1:
                pos = 'FINAL'
            else:
                pos = 'INTERIOR'
            ht_data.append({
                'word': t.word,
                'art': m.articulator,
                'prefix': m.prefix,
                'pos': pos,
                'folio': folio,
                'line': line,
            })

print(f"HT tokens: {len(ht_data)}")

# ═══ 2. POSITIONAL DISTRIBUTION BY ARTICULATOR ═══
print("\n" + "=" * 100)
print("POSITIONAL DISTRIBUTION BY ARTICULATOR (ALL CURRIER B)")
print("=" * 100)

art_pos = defaultdict(Counter)
art_total = Counter()
for ht in ht_data:
    art_pos[ht['art']][ht['pos']] += 1
    art_total[ht['art']] += 1

print(f"\n  {'Art':4s} {'Gloss':10s} {'Total':>6s} {'INIT':>6s} {'INTR':>6s} {'FINAL':>6s} {'Init%':>7s} {'Group':>12s}")
print(f"  {'-' * 70}")

opener_arts = set()
embedded_arts = set()

for art in sorted(art_total.keys(), key=lambda a: -art_total[a]):
    total = art_total[art]
    ini = art_pos[art].get('INITIAL', 0)
    intr = art_pos[art].get('INTERIOR', 0)
    fin = art_pos[art].get('FINAL', 0)
    ini_pct = 100 * ini / total if total > 0 else 0
    gloss = ATOM_GLOSSES.get(art, '?')

    # Classify
    if ini_pct > 50:
        group = 'OPENER'
        opener_arts.add(art)
    elif ini_pct < 20:
        group = 'EMBEDDED'
        embedded_arts.add(art)
    else:
        group = 'MIXED'

    print(f"  {art:4s} {gloss:10s} {total:6d} {ini:6d} {intr:6d} {fin:6d} {ini_pct:6.1f}% {group:>12s}")

# ═══ 3. HYPOTHESIS TEST ═══
print("\n" + "=" * 100)
print("HYPOTHESIS TEST: Two-group positional split")
print("=" * 100)

# Group 1 (predicted openers): p, t, f, d
# Group 2 (predicted embedded): l, r
predicted_openers = {'p', 't', 'f', 'd'}
predicted_embedded = {'l', 'r'}

opener_ini = sum(art_pos[a].get('INITIAL', 0) for a in predicted_openers)
opener_total = sum(art_total[a] for a in predicted_openers)
embedded_ini = sum(art_pos[a].get('INITIAL', 0) for a in predicted_embedded)
embedded_total = sum(art_total[a] for a in predicted_embedded)

opener_pct = 100 * opener_ini / opener_total if opener_total > 0 else 0
embedded_pct = 100 * embedded_ini / embedded_total if embedded_total > 0 else 0

print(f"\n  Predicted OPENERS (p,t,f,d): {opener_ini}/{opener_total} initial ({opener_pct:.1f}%)")
print(f"  Predicted EMBEDDED (l,r):    {embedded_ini}/{embedded_total} initial ({embedded_pct:.1f}%)")
print(f"  Difference: {opener_pct - embedded_pct:.1f} percentage points")

# Chi-squared test
# 2x2 table: [openers, embedded] x [initial, non-initial]
a = opener_ini
b = opener_total - opener_ini
c = embedded_ini
d = embedded_total - embedded_ini
n = a + b + c + d

if n > 0 and (a+b) > 0 and (c+d) > 0 and (a+c) > 0 and (b+d) > 0:
    expected_a = (a+b) * (a+c) / n
    expected_b = (a+b) * (b+d) / n
    expected_c = (c+d) * (a+c) / n
    expected_d = (c+d) * (b+d) / n

    chi2 = ((a - expected_a)**2 / expected_a +
            (b - expected_b)**2 / expected_b +
            (c - expected_c)**2 / expected_c +
            (d - expected_d)**2 / expected_d)

    print(f"\n  Chi-squared (1 df): {chi2:.1f}")
    if chi2 > 10.83:
        print(f"  p < 0.001 *** HIGHLY SIGNIFICANT")
    elif chi2 > 6.63:
        print(f"  p < 0.01 ** SIGNIFICANT")
    elif chi2 > 3.84:
        print(f"  p < 0.05 * SIGNIFICANT")
    else:
        print(f"  p > 0.05 — NOT SIGNIFICANT")

# Pass/fail
print(f"\n  PASS CRITERIA:")
opener_pass = opener_pct > 50
embedded_pass = embedded_pct < 20
print(f"    Openers >50% initial: {opener_pct:.1f}% — {'PASS' if opener_pass else 'FAIL'}")
print(f"    Embedded <20% initial: {embedded_pct:.1f}% — {'PASS' if embedded_pass else 'FAIL'}")

# ═══ 4. PER-ARTICULATOR DETAIL ═══
print("\n" + "=" * 100)
print("PER-ARTICULATOR DETAIL")
print("=" * 100)

for art in sorted(predicted_openers | predicted_embedded, key=lambda a: -art_total.get(a, 0)):
    total = art_total.get(art, 0)
    if total < 5:
        continue
    ini = art_pos[art].get('INITIAL', 0)
    ini_pct = 100 * ini / total if total > 0 else 0
    gloss = ATOM_GLOSSES.get(art, '?')
    predicted = 'OPENER' if art in predicted_openers else 'EMBEDDED'
    actual = 'OPENER' if ini_pct > 50 else ('EMBEDDED' if ini_pct < 20 else 'MIXED')
    match = 'MATCH' if predicted == actual else 'MISMATCH'

    print(f"\n  {art} ({gloss}): {total} tokens, {ini_pct:.1f}% initial")
    print(f"    Predicted: {predicted}, Actual: {actual} — {match}")

    # Show which prefixes this articulator pairs with
    art_prefixes = Counter()
    for ht in ht_data:
        if ht['art'] == art:
            art_prefixes[ht['prefix'] or 'NONE'] += 1
    top_pre = art_prefixes.most_common(5)
    print(f"    Top prefixes: {', '.join(f'{p}:{c}' for p, c in top_pre)}")

# ═══ 5. y-ARTICULATOR SPECIAL ANALYSIS ═══
print("\n" + "=" * 100)
print("y-ARTICULATOR: THE DOMINANT HT TYPE")
print("=" * 100)

y_total = art_total.get('y', 0)
y_ini = art_pos['y'].get('INITIAL', 0)
y_intr = art_pos['y'].get('INTERIOR', 0)
y_fin = art_pos['y'].get('FINAL', 0)
print(f"\n  y-art: {y_total} tokens ({100*y_total/len(ht_data):.1f}% of all HT)")
print(f"    INITIAL: {y_ini} ({100*y_ini/y_total:.1f}%)")
print(f"    INTERIOR: {y_intr} ({100*y_intr/y_total:.1f}%)")
print(f"    FINAL: {y_fin} ({100*y_fin/y_total:.1f}%)")

# y-art by prefix
y_by_prefix = Counter()
y_ini_by_prefix = Counter()
for ht in ht_data:
    if ht['art'] == 'y':
        pre = ht['prefix'] or 'NONE'
        y_by_prefix[pre] += 1
        if ht['pos'] == 'INITIAL':
            y_ini_by_prefix[pre] += 1

print(f"\n  y-art prefix distribution (initial vs total):")
for pre, ct in y_by_prefix.most_common(10):
    ini = y_ini_by_prefix.get(pre, 0)
    ini_pct = 100 * ini / ct if ct > 0 else 0
    print(f"    {pre:8s}: {ct:4d} total, {ini:4d} initial ({ini_pct:.0f}%)")

# ═══ 6. FOLIO-LEVEL CONSISTENCY ═══
print("\n" + "=" * 100)
print("FOLIO-LEVEL CONSISTENCY: Does the split hold per-folio?")
print("=" * 100)

# For each folio, compute opener vs embedded initial rates
folio_stats = defaultdict(lambda: {'opener_ini': 0, 'opener_total': 0,
                                     'embedded_ini': 0, 'embedded_total': 0})
for ht in ht_data:
    art = ht['art']
    if art in predicted_openers:
        folio_stats[ht['folio']]['opener_total'] += 1
        if ht['pos'] == 'INITIAL':
            folio_stats[ht['folio']]['opener_ini'] += 1
    elif art in predicted_embedded:
        folio_stats[ht['folio']]['embedded_total'] += 1
        if ht['pos'] == 'INITIAL':
            folio_stats[ht['folio']]['embedded_ini'] += 1

# How many folios have enough data to test?
testable = 0
consistent = 0
for folio, stats in folio_stats.items():
    if stats['opener_total'] >= 3 and stats['embedded_total'] >= 3:
        testable += 1
        o_pct = 100 * stats['opener_ini'] / stats['opener_total']
        e_pct = 100 * stats['embedded_ini'] / stats['embedded_total']
        if o_pct > e_pct:
            consistent += 1

print(f"\n  Folios with 3+ openers AND 3+ embedded: {testable}")
if testable > 0:
    print(f"  Folios where opener_init% > embedded_init%: {consistent}/{testable} ({100*consistent/testable:.0f}%)")

# ═══ 7. k AND s ARTICULATORS ═══
print("\n" + "=" * 100)
print("k AND s ARTICULATORS (not in either predicted group)")
print("=" * 100)

for art in ['k', 's']:
    total = art_total.get(art, 0)
    if total < 5:
        print(f"  {art}: only {total} tokens, skipping")
        continue
    ini = art_pos[art].get('INITIAL', 0)
    ini_pct = 100 * ini / total
    gloss = ATOM_GLOSSES.get(art, '?')
    group = 'OPENER' if ini_pct > 50 else ('EMBEDDED' if ini_pct < 20 else 'MIXED')
    print(f"  {art} ({gloss}): {total} tokens, {ini_pct:.1f}% initial → {group}")

# ═══ VERDICT ═══
print("\n" + "=" * 100)
print("VERDICT")
print("=" * 100)

all_pass = opener_pass and embedded_pass and chi2 > 6.63
print(f"""
  Two-group positional split:
    Openers (p,t,f,d): {opener_pct:.1f}% initial — {'PASS' if opener_pass else 'FAIL'} (>50%)
    Embedded (l,r):    {embedded_pct:.1f}% initial — {'PASS' if embedded_pass else 'FAIL'} (<20%)
    Chi-squared:       {chi2:.1f} — {'SIGNIFICANT' if chi2 > 6.63 else 'NOT SIGNIFICANT'}
    Folio consistency: {consistent}/{testable} folios ({100*consistent/testable:.0f}% if testable > 0)

  OVERALL: {'PASS — Two-group split confirmed corpus-wide' if all_pass else 'FAIL or PARTIAL — needs investigation'}
""")

print("=" * 100)
print("DONE")
print("=" * 100)
