#!/usr/bin/env python3
"""
Test: Does "STOP" at line-final actually predict paragraph endings?

If STOP = paragraph termination, then:
- The LAST body line should have much higher STOP rate than other lines
- Non-final STOP lines should be rare

If STOP = batch-close (not paragraph termination), then:
- STOP rate should be similar on last vs non-last lines
- Something ELSE must signal paragraph endings

Output: phases/CONTROL_LOOP_ARCHITECTURE/results/stop_vs_ending.json
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'phases' / 'CONTROL_LOOP_ARCHITECTURE' / 'results'

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

TERMINAL_SUFFIXES = {'dy', 'edy', 'eey', 'ey', 'hy', 'ry', 'ly', 'am', 'om'}
CHECKPOINT_SUFFIXES = {'ain', 'aiin', 'iin', 'oiin'}

def classify_final(tok):
    """Classify a token as STOP, CONTINUE, or NEUTRAL."""
    m = tok.morph
    has_m = m.middle and 'm' in m.middle
    has_i = m.middle and 'i' in m.middle
    cat = None
    if m.suffix in TERMINAL_SUFFIXES:
        cat = 'TERMINAL'
    elif m.suffix in CHECKPOINT_SUFFIXES:
        cat = 'CHECKPOINT'

    if cat == 'TERMINAL' or has_m:
        return 'STOP'
    elif cat == 'CHECKPOINT' or (has_i and not has_m):
        return 'CONTINUE'
    return 'NEUTRAL'

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
# TEST A: STOP rate on LAST line vs NON-LAST lines
# ============================================================
print("\n" + "="*70)
print("TEST A: STOP rate on LAST vs NON-LAST body lines")
print("="*70)

last_decisions = Counter()
nonlast_decisions = Counter()
last_words = Counter()
nonlast_stop_words = Counter()

for folio, para in all_paragraphs:
    body_lines = [l for l in para.lines if not l.is_header]
    if len(body_lines) < 3:
        continue

    for li, line_a in enumerate(body_lines):
        if line_a.token_count < 2:
            continue
        final_tok = line_a.tokens[-1]
        decision = classify_final(final_tok)
        is_last = (li == len(body_lines) - 1)

        if is_last:
            last_decisions[decision] += 1
            last_words[final_tok.word] += 1
        else:
            nonlast_decisions[decision] += 1
            if decision == 'STOP':
                nonlast_stop_words[final_tok.word] += 1

last_total = sum(last_decisions.values()) or 1
nonlast_total = sum(nonlast_decisions.values()) or 1

print(f"\n  LAST body line (n={last_total}):")
for d in ['STOP', 'CONTINUE', 'NEUTRAL']:
    pct = last_decisions[d] / last_total * 100
    print(f"    {d:10s}: {last_decisions[d]:5d} ({pct:.1f}%)")

print(f"\n  NON-LAST body lines (n={nonlast_total}):")
for d in ['STOP', 'CONTINUE', 'NEUTRAL']:
    pct = nonlast_decisions[d] / nonlast_total * 100
    print(f"    {d:10s}: {nonlast_decisions[d]:5d} ({pct:.1f}%)")

# Enrichment
last_stop_rate = last_decisions['STOP'] / last_total
nonlast_stop_rate = nonlast_decisions['STOP'] / nonlast_total
enrichment = last_stop_rate / nonlast_stop_rate if nonlast_stop_rate > 0 else float('inf')
print(f"\n  STOP enrichment on last line: {enrichment:.2f}x")
if enrichment > 1.5:
    print(f"  -> STOP DOES predict paragraph endings ({enrichment:.1f}x enriched)")
elif enrichment > 1.1:
    print(f"  -> STOP WEAKLY predicts paragraph endings ({enrichment:.1f}x)")
else:
    print(f"  -> STOP does NOT predict paragraph endings ({enrichment:.1f}x)")

# ============================================================
# TEST B: What appears on the LAST line that doesn't appear elsewhere?
# ============================================================
print("\n" + "="*70)
print("TEST B: What is unique about LAST body lines?")
print("="*70)

# Suffix distribution: last vs non-last
last_suffix = Counter()
nonlast_suffix = Counter()
last_suffix_modes = Counter()
nonlast_suffix_modes = Counter()

# Word-level features
last_features = defaultdict(int)
nonlast_features = defaultdict(int)

for folio, para in all_paragraphs:
    body_lines = [l for l in para.lines if not l.is_header]
    if len(body_lines) < 3:
        continue

    for li, line_a in enumerate(body_lines):
        if line_a.token_count < 2:
            continue
        is_last = (li == len(body_lines) - 1)
        final_tok = line_a.tokens[-1]
        m = final_tok.morph

        suffix = m.suffix or 'BARE'
        mode = line_a.suffix_mode or '?'

        if is_last:
            last_suffix[suffix] += 1
            last_suffix_modes[mode] += 1
            if m.middle:
                for c in set(m.middle):
                    last_features[f'mid_{c}'] += 1
            if m.prefix:
                last_features[f'prefix_{m.prefix}'] += 1
        else:
            nonlast_suffix[suffix] += 1
            nonlast_suffix_modes[mode] += 1

# Suffix enrichment on last line
print(f"\n  Suffix enrichment on LAST line (vs non-last):")
print(f"  {'Suffix':>10s} {'Last':>6s} {'Last%':>7s} {'NonL':>6s} {'NonL%':>7s} {'Enrich':>7s}")
for suffix in sorted(set(list(last_suffix.keys()) + list(nonlast_suffix.keys())),
                     key=lambda s: last_suffix[s] + nonlast_suffix[s], reverse=True)[:15]:
    l_ct = last_suffix[suffix]
    nl_ct = nonlast_suffix[suffix]
    l_pct = l_ct / last_total * 100
    nl_pct = nl_ct / nonlast_total * 100
    enr = l_pct / nl_pct if nl_pct > 0 else 99.9
    marker = " <<<" if enr > 2.0 or enr < 0.3 else ""
    print(f"  {suffix:>10s} {l_ct:6d} {l_pct:6.1f}% {nl_ct:6d} {nl_pct:6.1f}% {enr:6.2f}x{marker}")

# Mode enrichment
print(f"\n  Mode on LAST line:")
for mode in ['A', 'B', '?']:
    l_ct = last_suffix_modes[mode]
    l_pct = l_ct / last_total * 100
    print(f"    Mode {mode}: {l_ct} ({l_pct:.1f}%)")

# ============================================================
# TEST C: Per-suffix STOP type breakdown
# ============================================================
print("\n" + "="*70)
print("TEST C: What suffix types appear at paragraph-final?")
print("="*70)

# For each paragraph, what is the VERY LAST TOKEN's suffix?
para_final_suffixes = Counter()
para_final_words = Counter()
para_final_decisions = Counter()

for folio, para in all_paragraphs:
    body_lines = [l for l in para.lines if not l.is_header]
    if not body_lines:
        continue
    last_line = body_lines[-1]
    if not last_line.tokens:
        continue
    final_tok = last_line.tokens[-1]
    m = final_tok.morph
    suffix = m.suffix or 'BARE'
    para_final_suffixes[suffix] += 1
    para_final_words[final_tok.word] += 1
    para_final_decisions[classify_final(final_tok)] += 1

print(f"\n  Paragraph-final token suffixes (n={sum(para_final_suffixes.values())}):")
for suffix, count in para_final_suffixes.most_common(15):
    pct = count / sum(para_final_suffixes.values()) * 100
    print(f"    {suffix:>10s}: {count:5d} ({pct:.1f}%)")

print(f"\n  Paragraph-final token words (top 20):")
for word, count in para_final_words.most_common(20):
    pct = count / sum(para_final_words.values()) * 100
    print(f"    {word:>14s}: {count:5d} ({pct:.1f}%)")

print(f"\n  Paragraph-final decision classification:")
pf_total = sum(para_final_decisions.values()) or 1
for d in ['STOP', 'CONTINUE', 'NEUTRAL']:
    pct = para_final_decisions[d] / pf_total * 100
    print(f"    {d:10s}: {para_final_decisions[d]:5d} ({pct:.1f}%)")

# ============================================================
# TEST D: PENULTIMATE line vs LAST line
# ============================================================
print("\n" + "="*70)
print("TEST D: Penultimate vs Last line comparison")
print("="*70)

penult_decisions = Counter()
for folio, para in all_paragraphs:
    body_lines = [l for l in para.lines if not l.is_header]
    if len(body_lines) < 4:
        continue
    penult_line = body_lines[-2]
    if penult_line.token_count < 2:
        continue
    final_tok = penult_line.tokens[-1]
    penult_decisions[classify_final(final_tok)] += 1

penult_total = sum(penult_decisions.values()) or 1
print(f"\n  Penultimate line (n={penult_total}):")
for d in ['STOP', 'CONTINUE', 'NEUTRAL']:
    pct = penult_decisions[d] / penult_total * 100
    print(f"    {d:10s}: {penult_decisions[d]:5d} ({pct:.1f}%)")

print(f"\n  Last line (n={last_total}):")
for d in ['STOP', 'CONTINUE', 'NEUTRAL']:
    pct = last_decisions[d] / last_total * 100
    print(f"    {d:10s}: {last_decisions[d]:5d} ({pct:.1f}%)")

# ============================================================
# TEST E: Does the last line have different TOKEN-LEVEL properties?
# ============================================================
print("\n" + "="*70)
print("TEST E: Token-level properties of LAST vs NON-LAST lines")
print("="*70)

last_line_lengths = []
nonlast_line_lengths = []
last_kernel_counts = Counter()
nonlast_kernel_counts = Counter()
last_bare_rate = []
nonlast_bare_rate = []

for folio, para in all_paragraphs:
    body_lines = [l for l in para.lines if not l.is_header]
    if len(body_lines) < 3:
        continue

    for li, line_a in enumerate(body_lines):
        is_last = (li == len(body_lines) - 1)
        n_bare = sum(1 for t in line_a.tokens if not t.morph.suffix)
        bare_rate = n_bare / line_a.token_count if line_a.token_count > 0 else 0

        if is_last:
            last_line_lengths.append(line_a.token_count)
            last_bare_rate.append(bare_rate)
            for t in line_a.tokens:
                for k in t.kernels:
                    last_kernel_counts[k] += 1
        else:
            nonlast_line_lengths.append(line_a.token_count)
            nonlast_bare_rate.append(bare_rate)
            for t in line_a.tokens:
                for k in t.kernels:
                    nonlast_kernel_counts[k] += 1

avg_last_len = sum(last_line_lengths) / len(last_line_lengths) if last_line_lengths else 0
avg_nonlast_len = sum(nonlast_line_lengths) / len(nonlast_line_lengths) if nonlast_line_lengths else 0
avg_last_bare = sum(last_bare_rate) / len(last_bare_rate) if last_bare_rate else 0
avg_nonlast_bare = sum(nonlast_bare_rate) / len(nonlast_bare_rate) if nonlast_bare_rate else 0

print(f"\n  Token count:   last={avg_last_len:.1f}  non-last={avg_nonlast_len:.1f}")
print(f"  Bare rate:     last={avg_last_bare:.3f}  non-last={avg_nonlast_bare:.3f}")

# Kernel distribution
last_k_total = sum(last_kernel_counts.values()) or 1
nonlast_k_total = sum(nonlast_kernel_counts.values()) or 1
print(f"\n  Kernel distribution:")
for k in ['k', 'e', 'h']:
    l_pct = last_kernel_counts[k] / last_k_total * 100
    nl_pct = nonlast_kernel_counts[k] / nonlast_k_total * 100
    print(f"    {k}: last={l_pct:.1f}%  non-last={nl_pct:.1f}%")

# ============================================================
# COMPILE RESULTS
# ============================================================
results = {
    'test_a_stop_vs_ending': {
        'last_line': dict(last_decisions),
        'nonlast_lines': dict(nonlast_decisions),
        'last_stop_rate': round(last_stop_rate * 100, 1),
        'nonlast_stop_rate': round(nonlast_stop_rate * 100, 1),
        'enrichment': round(enrichment, 2),
    },
    'test_b_last_line_suffixes': {
        'top_enriched': [],
    },
    'test_c_para_final': {
        'decisions': dict(para_final_decisions),
        'top_suffixes': dict(para_final_suffixes.most_common(10)),
        'top_words': dict(para_final_words.most_common(15)),
    },
    'test_e_line_properties': {
        'avg_last_length': round(avg_last_len, 1),
        'avg_nonlast_length': round(avg_nonlast_len, 1),
        'avg_last_bare_rate': round(avg_last_bare, 3),
        'avg_nonlast_bare_rate': round(avg_nonlast_bare, 3),
    },
}

output_path = OUTPUT_DIR / 'stop_vs_ending.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults written to: {output_path}")
