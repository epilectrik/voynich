#!/usr/bin/env python3
"""
Extension Analysis: i-count and e-count as loop control signals.

i and e are the only extending characters in Voynichese.
Does the extension count carry operational information?

Tests:
A. i-count (i, ii, iii) distribution across paragraph position
B. e-count (e, ee, eee) distribution across paragraph position
C. i-count at line-final vs non-final
D. i-count on last body line vs non-last
E. Extension count vs Mode A/B
F. Extension count vs suffix type

Output: phases/CONTROL_LOOP_ARCHITECTURE/results/extension_analysis.json
"""

import sys
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'phases' / 'CONTROL_LOOP_ARCHITECTURE' / 'results'

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

def count_max_i_run(word):
    """Count the longest consecutive i-run in the word."""
    max_run = 0
    current = 0
    for c in word:
        if c == 'i':
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run

def count_max_e_run(word):
    """Count the longest consecutive e-run in the word."""
    max_run = 0
    current = 0
    for c in word:
        if c == 'e':
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run

# ============================================================
# DECODE ALL FOLIOS
# ============================================================
print("Decoding all B folios...")
b_folios = sorted(set(t.folio for t in tx.currier_b()))

all_paragraphs = []
for folio in b_folios:
    try:
        paras = decoder.analyze_folio_paragraphs(folio)
        for p in paras:
            all_paragraphs.append((folio, p))
    except:
        continue

print(f"  {len(all_paragraphs)} paragraphs from {len(b_folios)} folios")

# ============================================================
# BUILD TOKEN RECORDS
# ============================================================
print("\nBuilding token records...")

token_records = []
for folio, para in all_paragraphs:
    body_lines = [l for l in para.lines if not l.is_header]
    n_body = len(body_lines)
    if n_body < 2:
        continue

    for li, line_a in enumerate(body_lines):
        is_last_line = (li == n_body - 1)
        para_pos = li / max(n_body - 1, 1)
        mode = line_a.suffix_mode or '?'
        n_tokens = line_a.token_count

        for ti, tok in enumerate(line_a.tokens):
            is_line_final = (ti == n_tokens - 1)
            is_line_initial = (ti == 0)
            word = tok.word
            m = tok.morph

            i_count = count_max_i_run(word)
            e_count = count_max_e_run(word)

            token_records.append({
                'word': word,
                'i_count': i_count,
                'e_count': e_count,
                'is_line_final': is_line_final,
                'is_line_initial': is_line_initial,
                'is_last_line': is_last_line,
                'is_para_final': is_last_line and is_line_final,
                'para_pos': para_pos,
                'mode': mode,
                'suffix': m.suffix or 'BARE',
                'middle': m.middle or '',
                'prefix': m.prefix or '',
            })

print(f"  {len(token_records)} tokens")

# ============================================================
# TEST A: i-count distribution overview
# ============================================================
print("\n" + "="*70)
print("TEST A: i-count and e-count distribution overview")
print("="*70)

i_counts = Counter(r['i_count'] for r in token_records)
e_counts = Counter(r['e_count'] for r in token_records)
total = len(token_records)

print(f"\n  i-count distribution:")
for n in sorted(i_counts.keys()):
    pct = i_counts[n] / total * 100
    print(f"    i*{n}: {i_counts[n]:6d} ({pct:.1f}%)")

print(f"\n  e-count distribution:")
for n in sorted(e_counts.keys()):
    pct = e_counts[n] / total * 100
    print(f"    e*{n}: {e_counts[n]:6d} ({pct:.1f}%)")

# ============================================================
# TEST B: i-count by paragraph position
# ============================================================
print("\n" + "="*70)
print("TEST B: i-count by paragraph position (quintiles)")
print("="*70)

# For tokens with i >= 1, what's the mean i-count by paragraph position?
i_by_quintile = defaultdict(list)
for r in token_records:
    if r['i_count'] >= 1:
        q = min(int(r['para_pos'] * 5), 4)
        i_by_quintile[q].append(r['i_count'])

print(f"\n  {'Quintile':>10s} {'N':>6s} {'Mean_i':>8s} {'i=1%':>8s} {'i=2%':>8s} {'i=3+%':>8s}")
for q in range(5):
    vals = i_by_quintile[q]
    if not vals:
        continue
    n = len(vals)
    mean_i = sum(vals) / n
    i1 = sum(1 for v in vals if v == 1) / n * 100
    i2 = sum(1 for v in vals if v == 2) / n * 100
    i3 = sum(1 for v in vals if v >= 3) / n * 100
    label = f"Q{q} ({q*20}-{(q+1)*20}%)"
    print(f"  {label:>14s} {n:6d} {mean_i:8.3f} {i1:7.1f}% {i2:7.1f}% {i3:7.1f}%")

# ============================================================
# TEST C: i-count at line-final vs non-final
# ============================================================
print("\n" + "="*70)
print("TEST C: i-count at line-final vs non-final position")
print("="*70)

final_i = Counter(r['i_count'] for r in token_records if r['is_line_final'])
nonfinal_i = Counter(r['i_count'] for r in token_records if not r['is_line_final'])
final_total = sum(final_i.values()) or 1
nonfinal_total = sum(nonfinal_i.values()) or 1

print(f"\n  {'i-count':>8s} {'Final%':>8s} {'NonFin%':>8s} {'Enrich':>8s}")
for n in [0, 1, 2, 3]:
    f_pct = final_i[n] / final_total * 100
    nf_pct = nonfinal_i[n] / nonfinal_total * 100
    enr = f_pct / nf_pct if nf_pct > 0 else 99.9
    print(f"  {n:>8d} {f_pct:7.1f}% {nf_pct:7.1f}% {enr:7.2f}x")

# Same for line-initial
initial_i = Counter(r['i_count'] for r in token_records if r['is_line_initial'])
initial_total = sum(initial_i.values()) or 1
print(f"\n  {'i-count':>8s} {'Initial%':>8s} {'NonInit%':>8s} {'Enrich':>8s}")
noninitial_i = Counter(r['i_count'] for r in token_records if not r['is_line_initial'])
noninitial_total = sum(noninitial_i.values()) or 1
for n in [0, 1, 2, 3]:
    ini_pct = initial_i[n] / initial_total * 100
    nini_pct = noninitial_i[n] / noninitial_total * 100
    enr = ini_pct / nini_pct if nini_pct > 0 else 99.9
    print(f"  {n:>8d} {ini_pct:7.1f}% {nini_pct:7.1f}% {enr:7.2f}x")

# ============================================================
# TEST D: i-count on LAST body line vs non-last
# ============================================================
print("\n" + "="*70)
print("TEST D: i-count on LAST body line vs non-last")
print("="*70)

lastline_i = Counter(r['i_count'] for r in token_records if r['is_last_line'])
nonlastline_i = Counter(r['i_count'] for r in token_records if not r['is_last_line'])
ll_total = sum(lastline_i.values()) or 1
nll_total = sum(nonlastline_i.values()) or 1

print(f"\n  {'i-count':>8s} {'Last%':>8s} {'NonLst%':>8s} {'Enrich':>8s}")
for n in [0, 1, 2, 3]:
    l_pct = lastline_i[n] / ll_total * 100
    nl_pct = nonlastline_i[n] / nll_total * 100
    enr = l_pct / nl_pct if nl_pct > 0 else 99.9
    print(f"  {n:>8d} {l_pct:7.1f}% {nl_pct:7.1f}% {enr:7.2f}x")

# Paragraph-final token specifically
parafinal_i = Counter(r['i_count'] for r in token_records if r['is_para_final'])
nonparafinal_i = Counter(r['i_count'] for r in token_records if not r['is_para_final'])
pf_total = sum(parafinal_i.values()) or 1
npf_total = sum(nonparafinal_i.values()) or 1

print(f"\n  PARAGRAPH-FINAL token i-count:")
print(f"  {'i-count':>8s} {'ParaF%':>8s} {'Other%':>8s} {'Enrich':>8s}")
for n in [0, 1, 2, 3]:
    pf_pct = parafinal_i[n] / pf_total * 100
    npf_pct = nonparafinal_i[n] / npf_total * 100
    enr = pf_pct / npf_pct if npf_pct > 0 else 99.9
    print(f"  {n:>8d} {pf_pct:7.1f}% {npf_pct:7.1f}% {enr:7.2f}x")

# ============================================================
# TEST E: i-count vs Mode A/B
# ============================================================
print("\n" + "="*70)
print("TEST E: i-count vs Mode A/B")
print("="*70)

mode_a_i = Counter(r['i_count'] for r in token_records if r['mode'] == 'A')
mode_b_i = Counter(r['i_count'] for r in token_records if r['mode'] == 'B')
ma_total = sum(mode_a_i.values()) or 1
mb_total = sum(mode_b_i.values()) or 1

print(f"\n  {'i-count':>8s} {'ModeA%':>8s} {'ModeB%':>8s} {'A/B':>8s}")
for n in [0, 1, 2, 3]:
    a_pct = mode_a_i[n] / ma_total * 100
    b_pct = mode_b_i[n] / mb_total * 100
    ratio = a_pct / b_pct if b_pct > 0 else 99.9
    print(f"  {n:>8d} {a_pct:7.1f}% {b_pct:7.1f}% {ratio:7.2f}x")

# Same for e-count
print(f"\n  e-count vs Mode A/B:")
mode_a_e = Counter(r['e_count'] for r in token_records if r['mode'] == 'A')
mode_b_e = Counter(r['e_count'] for r in token_records if r['mode'] == 'B')

print(f"  {'e-count':>8s} {'ModeA%':>8s} {'ModeB%':>8s} {'A/B':>8s}")
for n in [0, 1, 2, 3]:
    a_pct = mode_a_e[n] / ma_total * 100
    b_pct = mode_b_e[n] / mb_total * 100
    ratio = a_pct / b_pct if b_pct > 0 else 99.9
    print(f"  {n:>8d} {a_pct:7.1f}% {b_pct:7.1f}% {ratio:7.2f}x")

# ============================================================
# TEST F: Specific suffix patterns with i-count
# ============================================================
print("\n" + "="*70)
print("TEST F: Suffix patterns by i-count")
print("="*70)

# For tokens with i >= 1, what suffixes do they have?
i1_suffixes = Counter(r['suffix'] for r in token_records if r['i_count'] == 1)
i2_suffixes = Counter(r['suffix'] for r in token_records if r['i_count'] == 2)

i1_total = sum(i1_suffixes.values()) or 1
i2_total = sum(i2_suffixes.values()) or 1

print(f"\n  Tokens with single-i (n={i1_total}):")
for suffix, count in i1_suffixes.most_common(10):
    pct = count / i1_total * 100
    print(f"    {suffix:>10s}: {count:5d} ({pct:.1f}%)")

print(f"\n  Tokens with double-i (n={i2_total}):")
for suffix, count in i2_suffixes.most_common(10):
    pct = count / i2_total * 100
    print(f"    {suffix:>10s}: {count:5d} ({pct:.1f}%)")

# ============================================================
# TEST G: Words ending -aiin vs -ain vs -in at paragraph-final
# ============================================================
print("\n" + "="*70)
print("TEST G: -aiin vs -ain vs -in at paragraph boundaries")
print("="*70)

# For each suffix pattern, enrichment at paragraph-final
patterns = {
    'aiin': lambda w: w.endswith('aiin'),
    'ain': lambda w: w.endswith('ain') and not w.endswith('aiin'),
    'in': lambda w: w.endswith('in') and not w.endswith('ain') and not w.endswith('iin'),
    'iin': lambda w: w.endswith('iin') and not w.endswith('aiin') and not w.endswith('oiin'),
    'oiin': lambda w: w.endswith('oiin'),
    'am': lambda w: w.endswith('am'),
    'edy': lambda w: w.endswith('edy'),
    'dy': lambda w: w.endswith('dy') and not w.endswith('edy'),
}

pf_tokens = [r for r in token_records if r['is_para_final']]
nonpf_tokens = [r for r in token_records if not r['is_para_final']]
pf_n = len(pf_tokens) or 1
nonpf_n = len(nonpf_tokens) or 1

print(f"\n  {'Pattern':>10s} {'ParaF':>6s} {'ParaF%':>8s} {'Other':>6s} {'Other%':>8s} {'Enrich':>8s}")
for name, test_fn in patterns.items():
    pf_count = sum(1 for r in pf_tokens if test_fn(r['word']))
    nonpf_count = sum(1 for r in nonpf_tokens if test_fn(r['word']))
    pf_pct = pf_count / pf_n * 100
    nonpf_pct = nonpf_count / nonpf_n * 100
    enr = pf_pct / nonpf_pct if nonpf_pct > 0 else 99.9
    marker = " <<<" if enr > 1.5 or enr < 0.5 else ""
    print(f"  {name:>10s} {pf_count:6d} {pf_pct:7.1f}% {nonpf_count:6d} {nonpf_pct:7.1f}% {enr:7.2f}x{marker}")

# Also: line-final enrichment for these patterns
lf_tokens = [r for r in token_records if r['is_line_final']]
nonlf_tokens = [r for r in token_records if not r['is_line_final']]
lf_n = len(lf_tokens) or 1
nonlf_n = len(nonlf_tokens) or 1

print(f"\n  Line-final enrichment (for comparison):")
print(f"  {'Pattern':>10s} {'LinF':>6s} {'LinF%':>8s} {'Other':>6s} {'Other%':>8s} {'Enrich':>8s}")
for name, test_fn in patterns.items():
    lf_count = sum(1 for r in lf_tokens if test_fn(r['word']))
    nonlf_count = sum(1 for r in nonlf_tokens if test_fn(r['word']))
    lf_pct = lf_count / lf_n * 100
    nonlf_pct = nonlf_count / nonlf_n * 100
    enr = lf_pct / nonlf_pct if nonlf_pct > 0 else 99.9
    marker = " <<<" if enr > 1.5 or enr < 0.5 else ""
    print(f"  {name:>10s} {lf_count:6d} {lf_pct:7.1f}% {nonlf_count:6d} {nonlf_pct:7.1f}% {enr:7.2f}x{marker}")

# ============================================================
# TEST H: e-extension analysis
# ============================================================
print("\n" + "="*70)
print("TEST H: e-extension parallel analysis")
print("="*70)

# e=1 vs e=2 position and role
e1_tokens = [r for r in token_records if r['e_count'] == 1]
e2_tokens = [r for r in token_records if r['e_count'] >= 2]

e1_final_rate = sum(1 for r in e1_tokens if r['is_line_final']) / len(e1_tokens) * 100 if e1_tokens else 0
e2_final_rate = sum(1 for r in e2_tokens if r['is_line_final']) / len(e2_tokens) * 100 if e2_tokens else 0
e1_initial_rate = sum(1 for r in e1_tokens if r['is_line_initial']) / len(e1_tokens) * 100 if e1_tokens else 0
e2_initial_rate = sum(1 for r in e2_tokens if r['is_line_initial']) / len(e2_tokens) * 100 if e2_tokens else 0
e1_lastline_rate = sum(1 for r in e1_tokens if r['is_last_line']) / len(e1_tokens) * 100 if e1_tokens else 0
e2_lastline_rate = sum(1 for r in e2_tokens if r['is_last_line']) / len(e2_tokens) * 100 if e2_tokens else 0

print(f"\n  {'Property':>16s} {'e=1':>8s} {'e>=2':>8s}")
print(f"  {'count':>16s} {len(e1_tokens):>8d} {len(e2_tokens):>8d}")
print(f"  {'line-final%':>16s} {e1_final_rate:7.1f}% {e2_final_rate:7.1f}%")
print(f"  {'line-initial%':>16s} {e1_initial_rate:7.1f}% {e2_initial_rate:7.1f}%")
print(f"  {'last-line%':>16s} {e1_lastline_rate:7.1f}% {e2_lastline_rate:7.1f}%")

# Mean paragraph position
e1_pos = sum(r['para_pos'] for r in e1_tokens) / len(e1_tokens) if e1_tokens else 0
e2_pos = sum(r['para_pos'] for r in e2_tokens) / len(e2_tokens) if e2_tokens else 0
print(f"  {'mean_para_pos':>16s} {e1_pos:8.3f} {e2_pos:8.3f}")

# e-extension suffix patterns
e2_suffixes = Counter(r['suffix'] for r in e2_tokens)
e2_total = len(e2_tokens) or 1
print(f"\n  e>=2 suffix distribution:")
for suffix, count in e2_suffixes.most_common(8):
    pct = count / e2_total * 100
    print(f"    {suffix:>10s}: {count:5d} ({pct:.1f}%)")

# Top e>=2 words
e2_words = Counter(r['word'] for r in e2_tokens)
print(f"\n  Top e>=2 words:")
for word, count in e2_words.most_common(15):
    pct = count / e2_total * 100
    print(f"    {word:>14s}: {count:5d} ({pct:.1f}%)")

# ============================================================
# TEST I: i-count mean position within line
# ============================================================
print("\n" + "="*70)
print("TEST I: Mean within-line position by i-count and e-count")
print("="*70)

# Recompute with within-line position
i_positions = defaultdict(list)
e_positions = defaultdict(list)

for folio, para in all_paragraphs:
    body_lines = [l for l in para.lines if not l.is_header]
    for line_a in body_lines:
        if line_a.token_count < 3:
            continue
        for ti, tok in enumerate(line_a.tokens):
            pos = ti / max(line_a.token_count - 1, 1)
            ic = count_max_i_run(tok.word)
            ec = count_max_e_run(tok.word)
            if ic >= 1:
                i_positions[ic].append(pos)
            if ec >= 1:
                e_positions[ec].append(pos)

print(f"\n  i-count  mean_line_pos  count")
for n in sorted(i_positions.keys()):
    vals = i_positions[n]
    mean = sum(vals) / len(vals)
    print(f"    i*{n}       {mean:.3f}        {len(vals)}")

print(f"\n  e-count  mean_line_pos  count")
for n in sorted(e_positions.keys()):
    vals = e_positions[n]
    mean = sum(vals) / len(vals)
    print(f"    e*{n}       {mean:.3f}        {len(vals)}")

# ============================================================
# COMPILE RESULTS
# ============================================================
results = {
    'i_count_distribution': dict(i_counts),
    'e_count_distribution': dict(e_counts),
    'i_count_paragraph_final': {
        n: round(parafinal_i[n] / pf_total * 100, 1) for n in [0, 1, 2, 3]
    },
    'i_count_paragraph_final_enrichment': {
        n: round((parafinal_i[n] / pf_total) / (nonparafinal_i[n] / npf_total), 2)
        if nonparafinal_i[n] > 0 else 0
        for n in [0, 1, 2, 3]
    },
    'i_mean_line_position': {
        n: round(sum(v) / len(v), 3) for n, v in i_positions.items()
    },
    'e_mean_line_position': {
        n: round(sum(v) / len(v), 3) for n, v in e_positions.items()
    },
}

output_path = OUTPUT_DIR / 'extension_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults written to: {output_path}")
