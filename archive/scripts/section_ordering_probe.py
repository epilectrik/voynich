"""
Quick probe: Are there incrementing/decrementing patterns within sections?
"""

import csv
from collections import defaultdict
import numpy as np
from scipy.stats import spearmanr

# Load data
data = []
with open('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber') == 'H':
            data.append(row)

# Group by section -> folio order
section_folios = defaultdict(list)
folio_order = {}
order_idx = 0
seen = set()

for row in data:
    f = row['folio']
    s = row.get('section', '')
    if f not in seen:
        seen.add(f)
        folio_order[f] = order_idx
        order_idx += 1
        if s:
            section_folios[s].append(f)

print('Section folio counts:')
for s in sorted(section_folios.keys()):
    folios = section_folios[s]
    print(f'  {s}: {len(folios)} folios')

# Compute metrics per folio
folio_metrics = defaultdict(dict)
folio_vocab = defaultdict(set)
folio_tokens = defaultdict(int)
folio_unique = defaultdict(set)  # track unique vocab per folio

# First pass: collect vocab
for row in data:
    f = row['folio']
    w = row.get('word', '')
    if w:
        folio_vocab[f].add(w)
        folio_tokens[f] += 1

# Build global vocab to track "novelty"
global_vocab = set()
for f in folio_vocab:
    global_vocab.update(folio_vocab[f])

for f in folio_vocab:
    folio_metrics[f]['vocab_size'] = len(folio_vocab[f])
    folio_metrics[f]['token_count'] = folio_tokens[f]
    folio_metrics[f]['ttr'] = len(folio_vocab[f]) / folio_tokens[f] if folio_tokens[f] > 0 else 0

# Test monotonic trends within sections
print()
print("="*60)
print("TESTING FOR ORDERING PATTERNS WITHIN SECTIONS")
print("="*60)

results = {}

for section in ['S', 'H', 'B', 'P', 'T', 'C', 'Z', 'A']:
    folios = section_folios.get(section, [])
    if len(folios) < 5:
        continue

    positions = list(range(len(folios)))
    vocab_sizes = [folio_metrics[f]['vocab_size'] for f in folios]
    ttrs = [folio_metrics[f]['ttr'] for f in folios]
    token_counts = [folio_metrics[f]['token_count'] for f in folios]

    # Track cumulative "novelty" - what % of folio vocab is new to section so far
    section_seen = set()
    novelty_rates = []
    for f in folios:
        fv = folio_vocab[f]
        if fv:
            new_tokens = fv - section_seen
            novelty = len(new_tokens) / len(fv)
            novelty_rates.append(novelty)
            section_seen.update(fv)
        else:
            novelty_rates.append(0)

    rho_vocab, p_vocab = spearmanr(positions, vocab_sizes)
    rho_ttr, p_ttr = spearmanr(positions, ttrs)
    rho_tok, p_tok = spearmanr(positions, token_counts)
    rho_nov, p_nov = spearmanr(positions, novelty_rates) if len(novelty_rates) > 2 else (0, 1)

    print(f'\nSection {section} ({len(folios)} folios):')
    print(f'  Vocab size vs position:  rho={rho_vocab:+.3f}, p={p_vocab:.4f}')
    print(f'  TTR vs position:         rho={rho_ttr:+.3f}, p={p_ttr:.4f}')
    print(f'  Token count vs position: rho={rho_tok:+.3f}, p={p_tok:.4f}')
    print(f'  Novelty vs position:     rho={rho_nov:+.3f}, p={p_nov:.4f}')

    # Flag significant trends
    sig = []
    if p_vocab < 0.05:
        direction = "INCREASING" if rho_vocab > 0 else "DECREASING"
        sig.append(f"vocab_size {direction}")
    if p_ttr < 0.05:
        direction = "INCREASING" if rho_ttr > 0 else "DECREASING"
        sig.append(f"TTR {direction}")
    if p_tok < 0.05:
        direction = "INCREASING" if rho_tok > 0 else "DECREASING"
        sig.append(f"token_count {direction}")
    if p_nov < 0.05:
        direction = "INCREASING" if rho_nov > 0 else "DECREASING"
        sig.append(f"novelty {direction}")

    if sig:
        print(f'  ** SIGNIFICANT: {", ".join(sig)}')
    else:
        print(f'  (no significant trends)')

    results[section] = {
        'n_folios': len(folios),
        'rho_vocab': rho_vocab, 'p_vocab': p_vocab,
        'rho_ttr': rho_ttr, 'p_ttr': p_ttr,
        'rho_tok': rho_tok, 'p_tok': p_tok,
        'rho_nov': rho_nov, 'p_nov': p_nov
    }

# Summary
print()
print("="*60)
print("SUMMARY")
print("="*60)

any_signal = False
for section, r in results.items():
    sigs = []
    if r['p_vocab'] < 0.01:
        sigs.append(f"vocab rho={r['rho_vocab']:+.2f}")
    if r['p_ttr'] < 0.01:
        sigs.append(f"TTR rho={r['rho_ttr']:+.2f}")
    if r['p_nov'] < 0.01:
        sigs.append(f"novelty rho={r['rho_nov']:+.2f}")

    if sigs:
        print(f"Section {section}: {', '.join(sigs)}")
        any_signal = True

if not any_signal:
    print("No strong (p<0.01) ordering patterns detected in any section.")

# Expected pattern: novelty should DECREASE (early folios introduce vocab, later reuse)
print()
print("Expected: Novelty should DECREASE (early folios introduce vocab)")
print("Check if this is universal or section-specific...")
