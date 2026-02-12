#!/usr/bin/env python3
"""Token-level safety buffer scan.

For every token in Currier B: if this token were removed, would the
resulting adjacency form a forbidden pair?

Answers: How tense is the grammar? How close does the system operate
to the forbidden boundary?
"""

import sys, json, functools
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ── Load data ──────────────────────────────────────────────────────

with open(PROJECT / 'data' / 'middle_affordance_table.json') as f:
    aff = json.load(f)

middle_to_bin = {}
bin_labels = {}
for mid, data in aff['middles'].items():
    middle_to_bin[mid] = data['affordance_bin']
for b, meta in aff['_metadata']['affordance_bins'].items():
    bin_labels[int(b)] = meta['label']

FUNCTIONAL_BINS = [0, 1, 2, 3, 5, 6, 7, 8, 9]

# Forbidden transitions
with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json') as f:
    inv = json.load(f)

forbidden_pairs = set()
for t in inv['transitions']:
    forbidden_pairs.add((t['source'], t['target']))

# ── Build corpus ───────────────────────────────────────────────────

tx = Transcript()
morph = Morphology()

corpus_lines = []
current_key = None
current_line = []

for token in tx.currier_b():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    mid = m.middle if m.middle else ''
    b = middle_to_bin.get(mid, -1)

    key = (token.folio, token.line)
    if key != current_key:
        if current_line:
            corpus_lines.append({'key': current_key, 'tokens': current_line})
        current_line = []
        current_key = key

    current_line.append({
        'word': word,
        'middle': mid,
        'bin': b,
    })

if current_line:
    corpus_lines.append({'key': current_key, 'tokens': current_line})

total_tokens = sum(len(line['tokens']) for line in corpus_lines)

print("=" * 70)
print("TOKEN-LEVEL SAFETY BUFFER SCAN")
print("=" * 70)
print(f"\nCorpus: {len(corpus_lines)} lines, {total_tokens} tokens")
print(f"Forbidden pairs: {len(forbidden_pairs)}")

# ── Scan ───────────────────────────────────────────────────────────

safety_buffers = []  # list of {token, bin, folio, line, left, right, forbidden_pair}

for line_data in corpus_lines:
    tokens = line_data['tokens']
    folio, line_num = line_data['key']
    n = len(tokens)

    for i in range(1, n - 1):  # skip first and last (no both-side adjacency)
        left_word = tokens[i - 1]['word']
        right_word = tokens[i + 1]['word']

        if (left_word, right_word) in forbidden_pairs:
            safety_buffers.append({
                'token': tokens[i]['word'],
                'middle': tokens[i]['middle'],
                'bin': tokens[i]['bin'],
                'folio': folio,
                'line': line_num,
                'position': i,
                'left': left_word,
                'right': right_word,
                'forbidden_pair': f"{left_word} -> {right_word}",
            })

print(f"\n{'=' * 70}")
print("RESULTS")
print("=" * 70)

print(f"\n  Total tokens scanned: {total_tokens}")
print(f"  Interior tokens (positions 1..n-2): {sum(max(len(l['tokens'])-2, 0) for l in corpus_lines)}")
print(f"  Safety buffer tokens found: {len(safety_buffers)}")
print(f"  Buffer rate: {100*len(safety_buffers)/total_tokens:.3f}%")

if not safety_buffers:
    print("\n  NO SAFETY BUFFERS FOUND.")
    print("  The grammar operates with thick safety margins.")
    print("  No single interior token removal creates a forbidden pair.")

    results = {
        'metadata': {
            'phase': 'BIN_HAZARD_NECESSITY',
            'test': 'SAFETY_BUFFER_SCAN',
            'total_tokens': total_tokens,
            'n_forbidden_pairs': len(forbidden_pairs),
        },
        'safety_buffers': [],
        'n_buffers': 0,
        'buffer_rate': 0,
        'verdict': 'THICK_SAFETY_BAND',
    }

    out_path = PROJECT / 'phases' / 'BIN_HAZARD_NECESSITY' / 'results' / 'safety_buffer_scan.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out_path}")
    sys.exit(0)

# ── Detailed analysis ──────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("SAFETY BUFFER INVENTORY")
print("=" * 70)

print(f"\n  {'#':>3} {'Folio':>8} {'Ln':>4} {'Pos':>4} {'Left':>10} {'[BUFFER]':>12} {'Right':>10} {'Bin':>4} {'Label':>25}")
print(f"  {'-' * 85}")
for i, buf in enumerate(safety_buffers):
    label = bin_labels.get(buf['bin'], 'BULK' if buf['bin'] == 4 else 'UNK')
    print(f"  {i+1:>3} {buf['folio']:>8} {buf['line']:>4} {buf['position']:>4} {buf['left']:>10} [{buf['token']:>10}] {buf['right']:>10} {buf['bin']:>4} {label:>25}")

# ── Aggregate by bin ───────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("SAFETY BUFFERS BY BIN")
print("=" * 70)

bin_buffer_count = Counter()
for buf in safety_buffers:
    bin_buffer_count[buf['bin']] += 1

# Count total tokens per bin for rate calculation
bin_total = Counter()
for line_data in corpus_lines:
    for tok in line_data['tokens']:
        bin_total[tok['bin']] += 1

print(f"\n  {'Bin':>4} {'Label':>25} {'Buffers':>8} {'BinTotal':>9} {'BufRate':>8}")
print(f"  {'-' * 56}")
all_bins = sorted(set(list(FUNCTIONAL_BINS) + [4]))
for b in all_bins:
    label = bin_labels.get(b, 'BULK' if b == 4 else 'UNK')
    n_buf = bin_buffer_count[b]
    total = bin_total[b]
    rate = 100 * n_buf / total if total > 0 else 0
    if n_buf > 0:
        print(f"  {b:>4} {label:>25} {n_buf:>8} {total:>9} {rate:>7.3f}%")

# ── Aggregate by forbidden pair ────────────────────────────────────

print(f"\n{'=' * 70}")
print("FORBIDDEN PAIRS PREVENTED")
print("=" * 70)

pair_count = Counter()
for buf in safety_buffers:
    pair_count[buf['forbidden_pair']] += 1

print(f"\n  {'Forbidden Pair':>25} {'Count':>6}")
print(f"  {'-' * 33}")
for pair, count in pair_count.most_common():
    print(f"  {pair:>25} {count:>6}")

# ── Aggregate by buffer token ──────────────────────────────────────

print(f"\n{'=' * 70}")
print("BUFFER TOKENS (which tokens serve as safety spacers?)")
print("=" * 70)

token_count = Counter()
for buf in safety_buffers:
    token_count[buf['token']] += 1

print(f"\n  {'Buffer Token':>15} {'Count':>6} {'MIDDLE':>10} {'Bin':>4}")
print(f"  {'-' * 38}")
for tok, count in token_count.most_common():
    m = morph.extract(tok)
    mid = m.middle if m.middle else '?'
    b = middle_to_bin.get(mid, -1)
    label = bin_labels.get(b, 'BULK' if b == 4 else 'UNK')[:15]
    print(f"  {tok:>15} {count:>6} {mid:>10} {b:>4}")

# ── Folio distribution ─────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("FOLIO DISTRIBUTION OF SAFETY BUFFERS")
print("=" * 70)

folio_count = Counter()
for buf in safety_buffers:
    folio_count[buf['folio']] += 1

if folio_count:
    print(f"\n  Folios with buffers: {len(folio_count)} / {len(set(l['key'][0] for l in corpus_lines))}")
    print(f"  Most buffered folios:")
    for folio, count in folio_count.most_common(10):
        print(f"    {folio}: {count} buffers")

# ── Verdict ────────────────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("VERDICT")
print("=" * 70)

n_buf = len(safety_buffers)
interior = sum(max(len(l['tokens']) - 2, 0) for l in corpus_lines)

if n_buf == 0:
    verdict = "THICK_SAFETY_BAND"
    print("\n  The grammar operates inside a THICK safety band.")
    print("  No single token removal creates a forbidden pair.")
elif n_buf < 10:
    verdict = "SPARSE_CRITICAL_BUFFERS"
    print(f"\n  The grammar has {n_buf} SPARSE safety-critical tokens.")
    print(f"  Buffer rate: {100*n_buf/interior:.4f}% of interior positions.")
    print("  The system operates near the forbidden boundary at specific points")
    print("  but maintains broad margins elsewhere.")
elif n_buf < 50:
    verdict = "MODERATE_TENSION"
    print(f"\n  The grammar has {n_buf} safety buffer tokens.")
    print(f"  Buffer rate: {100*n_buf/interior:.3f}% of interior positions.")
    print("  Moderate structural tension — the system is not fragile")
    print("  but has identifiable pressure points.")
else:
    verdict = "HIGH_TENSION"
    print(f"\n  The grammar has {n_buf} safety buffer tokens.")
    print(f"  Buffer rate: {100*n_buf/interior:.2f}% of interior positions.")
    print("  High structural tension — the system operates close to")
    print("  the forbidden boundary at many points.")

# Structural interpretation
if n_buf > 0:
    unique_pairs = len(pair_count)
    unique_buffers = len(token_count)
    unique_bins = len(bin_buffer_count)
    print(f"\n  {n_buf} buffer instances across {unique_pairs} forbidden pairs")
    print(f"  {unique_buffers} distinct buffer tokens from {unique_bins} bins")

    # Is safety concentrated or distributed?
    top_bin = bin_buffer_count.most_common(1)[0]
    top_pct = 100 * top_bin[1] / n_buf
    print(f"\n  Top buffer bin: {top_bin[0]} ({bin_labels.get(top_bin[0], '?')}) = {top_pct:.0f}% of all buffers")
    if top_pct > 60:
        print("  Safety load is CONCENTRATED in one bin.")
    else:
        print("  Safety load is DISTRIBUTED across bins.")

# ── Save results ───────────────────────────────────────────────────

results = {
    'metadata': {
        'phase': 'BIN_HAZARD_NECESSITY',
        'test': 'SAFETY_BUFFER_SCAN',
        'total_tokens': total_tokens,
        'interior_tokens': interior,
        'n_forbidden_pairs': len(forbidden_pairs),
    },
    'n_buffers': n_buf,
    'buffer_rate': round(n_buf / interior, 6) if interior > 0 else 0,
    'verdict': verdict,
    'buffers_by_bin': {str(b): bin_buffer_count[b] for b in bin_buffer_count},
    'forbidden_pairs_prevented': {pair: count for pair, count in pair_count.most_common()},
    'buffer_tokens': {tok: count for tok, count in token_count.most_common()},
    'folio_distribution': {f: c for f, c in folio_count.most_common()},
    'safety_buffers': safety_buffers,
}

out_path = PROJECT / 'phases' / 'BIN_HAZARD_NECESSITY' / 'results' / 'safety_buffer_scan.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {out_path}")
