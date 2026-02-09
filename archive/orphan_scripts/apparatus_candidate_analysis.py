#!/usr/bin/env python3
"""
Identify candidate apparatus tokens.

Apparatus tokens should have distinctive signatures:
1. HIGH STABILITY across folios/sections (same equipment used)
2. POSITIONAL BIAS (appear in setup positions - early in line/paragraph)
3. CO-OCCURRENCE with fire/phase operations
4. LOW KERNEL CONTENT (apparatus names don't encode process state)

We look for tokens that behave differently from process vocabulary.
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

# Load class map
class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {t: int(c) for t, c in class_data['token_to_class'].items()}
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

# Build token data
token_folios = defaultdict(set)
token_sections = defaultdict(set)
token_positions = defaultdict(list)  # normalized line position
token_line_initial = defaultdict(int)
token_para_initial = defaultdict(int)
token_total = Counter()
token_kernel_content = defaultdict(lambda: {'k': 0, 'h': 0, 'e': 0, 'total': 0})

folio_line_tokens = defaultdict(lambda: defaultdict(list))
folio_section = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    word = token.word
    folio = token.folio
    line = token.line

    folio_line_tokens[folio][line].append(token)
    if folio not in folio_section:
        folio_section[folio] = token.section

    token_folios[word].add(folio)
    token_sections[word].add(token.section)
    token_total[word] += 1

    # Kernel content
    token_kernel_content[word]['k'] += word.count('k')
    token_kernel_content[word]['h'] += word.count('h')
    token_kernel_content[word]['e'] += word.count('e')
    token_kernel_content[word]['total'] += 1

# Calculate normalized line positions
for folio in folio_line_tokens:
    for line in folio_line_tokens[folio]:
        tokens = folio_line_tokens[folio][line]
        n_tokens = len(tokens)
        if n_tokens == 0:
            continue

        for i, t in enumerate(tokens):
            word = t.word
            if '*' in word:
                continue
            # Normalized position: 0 = first token, 1 = last token
            if n_tokens > 1:
                norm_pos = i / (n_tokens - 1)
            else:
                norm_pos = 0.5
            token_positions[word].append(norm_pos)

            if i == 0:
                token_line_initial[word] += 1

# Paragraph-initial tokens
for folio in folio_line_tokens:
    lines = folio_line_tokens[folio]
    for line_num in sorted(lines.keys()):
        tokens = lines[line_num]
        if not tokens:
            continue
        first_word = tokens[0].word
        if '*' in first_word:
            continue
        if first_word and first_word[0] in GALLOWS:
            # This is paragraph-initial
            token_para_initial[first_word] += 1

print("="*70)
print("APPARATUS CANDIDATE ANALYSIS")
print("="*70)

# Calculate metrics for each token
token_metrics = {}

for word in token_total:
    if token_total[word] < 10:  # Need sufficient data
        continue

    n_folios = len(token_folios[word])
    n_sections = len(token_sections[word])
    mean_pos = np.mean(token_positions[word]) if token_positions[word] else 0.5
    line_initial_rate = token_line_initial[word] / token_total[word]
    para_initial_rate = token_para_initial[word] / token_total[word]

    # Kernel content per occurrence
    kc = token_kernel_content[word]
    k_per_occ = kc['k'] / kc['total']
    h_per_occ = kc['h'] / kc['total']
    e_per_occ = kc['e'] / kc['total']
    total_kernel = k_per_occ + h_per_occ + e_per_occ

    # Folio coverage (what fraction of folios is this token in?)
    folio_coverage = n_folios / 83  # 83 B folios

    token_metrics[word] = {
        'count': token_total[word],
        'n_folios': n_folios,
        'n_sections': n_sections,
        'folio_coverage': folio_coverage,
        'mean_pos': mean_pos,
        'line_initial_rate': line_initial_rate,
        'para_initial_rate': para_initial_rate,
        'k_per_occ': k_per_occ,
        'h_per_occ': h_per_occ,
        'e_per_occ': e_per_occ,
        'total_kernel': total_kernel,
        'role': token_to_role.get(word, 'UNKNOWN'),
    }

print(f"\nTokens analyzed: {len(token_metrics)}")

# ============================================================
# CRITERION 1: HIGH STABILITY (appears across many folios)
# ============================================================
print(f"\n{'='*70}")
print("CRITERION 1: HIGH FOLIO STABILITY (apparatus = widely used)")
print("="*70)

# Top tokens by folio coverage
sorted_by_coverage = sorted(token_metrics.items(), key=lambda x: -x[1]['folio_coverage'])

print(f"\n{'Token':<15} {'Count':<8} {'Folios':<8} {'Coverage':<10} {'Role':<20}")
print("-"*65)

for word, m in sorted_by_coverage[:20]:
    print(f"{word:<15} {m['count']:<8} {m['n_folios']:<8} {m['folio_coverage']:<10.2f} {m['role']:<20}")

# ============================================================
# CRITERION 2: LINE-INITIAL BIAS (setup positions)
# ============================================================
print(f"\n{'='*70}")
print("CRITERION 2: LINE-INITIAL BIAS (apparatus = setup position)")
print("="*70)

# Filter to tokens with meaningful line-initial rate
# Baseline: random would be ~1/avg_line_length ~ 0.1-0.15
high_initial = [(w, m) for w, m in token_metrics.items()
                if m['line_initial_rate'] > 0.3 and m['count'] >= 20]
high_initial.sort(key=lambda x: -x[1]['line_initial_rate'])

print(f"\nTokens with >30% line-initial rate (n>=20):")
print(f"\n{'Token':<15} {'Count':<8} {'Initial%':<10} {'Mean Pos':<10} {'Role':<20}")
print("-"*65)

for word, m in high_initial[:15]:
    print(f"{word:<15} {m['count']:<8} {100*m['line_initial_rate']:<10.1f} {m['mean_pos']:<10.2f} {m['role']:<20}")

# ============================================================
# CRITERION 3: LOW KERNEL CONTENT (apparatus != process state)
# ============================================================
print(f"\n{'='*70}")
print("CRITERION 3: LOW KERNEL CONTENT (apparatus != process state)")
print("="*70)

# Tokens with very low kernel content
low_kernel = [(w, m) for w, m in token_metrics.items()
              if m['total_kernel'] < 0.3 and m['count'] >= 20]
low_kernel.sort(key=lambda x: x[1]['total_kernel'])

print(f"\nTokens with <0.3 kernel chars per occurrence (n>=20):")
print(f"\n{'Token':<15} {'Count':<8} {'k/occ':<8} {'h/occ':<8} {'e/occ':<8} {'Total':<8} {'Role':<15}")
print("-"*70)

for word, m in low_kernel[:15]:
    print(f"{word:<15} {m['count']:<8} {m['k_per_occ']:<8.2f} {m['h_per_occ']:<8.2f} {m['e_per_occ']:<8.2f} {m['total_kernel']:<8.2f} {m['role']:<15}")

# ============================================================
# CRITERION 4: PARAGRAPH-INITIAL (setup statements)
# ============================================================
print(f"\n{'='*70}")
print("CRITERION 4: PARAGRAPH-INITIAL (apparatus = procedure start)")
print("="*70)

high_para_initial = [(w, m) for w, m in token_metrics.items()
                     if m['para_initial_rate'] > 0.1 and m['count'] >= 10]
high_para_initial.sort(key=lambda x: -x[1]['para_initial_rate'])

print(f"\nTokens with >10% paragraph-initial rate:")
print(f"\n{'Token':<15} {'Count':<8} {'Para Init%':<12} {'Line Init%':<12} {'Role':<15}")
print("-"*65)

for word, m in high_para_initial[:15]:
    print(f"{word:<15} {m['count']:<8} {100*m['para_initial_rate']:<12.1f} {100*m['line_initial_rate']:<12.1f} {m['role']:<15}")

# ============================================================
# COMBINED SCORE: Apparatus likelihood
# ============================================================
print(f"\n{'='*70}")
print("COMBINED ANALYSIS: APPARATUS CANDIDATES")
print("="*70)

# Score: high coverage + early position + low kernel
apparatus_scores = []

for word, m in token_metrics.items():
    if m['count'] < 20:
        continue

    # Components (higher = more apparatus-like)
    coverage_score = m['folio_coverage']  # 0-1
    position_score = 1 - m['mean_pos']  # 0-1, higher = earlier
    initial_score = m['line_initial_rate']  # 0-1
    low_kernel_score = 1 - min(m['total_kernel'] / 2, 1)  # 0-1, higher = less kernel

    # Combined score
    combined = (coverage_score * 0.3 +
                position_score * 0.2 +
                initial_score * 0.3 +
                low_kernel_score * 0.2)

    apparatus_scores.append((word, combined, m))

apparatus_scores.sort(key=lambda x: -x[1])

print(f"\nTop apparatus candidates (combined score):")
print(f"\n{'Token':<15} {'Score':<8} {'Count':<8} {'Coverage':<10} {'MeanPos':<10} {'Init%':<10} {'Kernel':<10} {'Role':<15}")
print("-"*95)

for word, score, m in apparatus_scores[:25]:
    print(f"{word:<15} {score:<8.3f} {m['count']:<8} {m['folio_coverage']:<10.2f} {m['mean_pos']:<10.2f} {100*m['line_initial_rate']:<10.1f} {m['total_kernel']:<10.2f} {m['role']:<15}")

# ============================================================
# ROLE ANALYSIS: Which roles are apparatus-like?
# ============================================================
print(f"\n{'='*70}")
print("ROLE ANALYSIS: WHICH ROLES ARE APPARATUS-LIKE?")
print("="*70)

role_apparatus_scores = defaultdict(list)
for word, score, m in apparatus_scores:
    role_apparatus_scores[m['role']].append(score)

print(f"\n{'Role':<25} {'Mean Score':<12} {'Count':<10}")
print("-"*50)

for role in sorted(role_apparatus_scores.keys(), key=lambda r: -np.mean(role_apparatus_scores[r])):
    scores = role_apparatus_scores[role]
    if len(scores) >= 5:
        print(f"{role:<25} {np.mean(scores):<12.3f} {len(scores):<10}")

# ============================================================
# SPECIFIC ANALYSIS: GALLOWS TOKENS (paragraph markers)
# ============================================================
print(f"\n{'='*70}")
print("GALLOWS TOKEN ANALYSIS (Paragraph Markers)")
print("="*70)

gallows_tokens = [(w, m) for w, m in token_metrics.items() if w and w[0] in GALLOWS]
gallows_tokens.sort(key=lambda x: -x[1]['count'])

print(f"\nTop gallows tokens:")
print(f"\n{'Token':<15} {'Count':<8} {'Coverage':<10} {'Para Init%':<12} {'Role':<20}")
print("-"*70)

for word, m in gallows_tokens[:15]:
    print(f"{word:<15} {m['count']:<8} {m['folio_coverage']:<10.2f} {100*m['para_initial_rate']:<12.1f} {m['role']:<20}")

print("""
INTERPRETATION:
---------------
Gallows tokens (k, t, p, f initial) mark paragraph boundaries.
They might encode:
1. Procedure TYPE (distillation, decoction, extraction)
2. Apparatus SETUP (which equipment configuration)
3. Fire DEGREE (per Brunschwig's 4 degrees)

Note: Gallows are by definition paragraph-initial in the B grammar.
""")

# Save results
output = {
    'n_tokens': len(token_metrics),
    'top_apparatus_candidates': [
        {'token': w, 'score': float(s), 'metrics': {k: float(v) if isinstance(v, (int, float)) else v
                                                     for k, v in m.items()}}
        for w, s, m in apparatus_scores[:50]
    ],
}

output_path = Path(__file__).parent.parent / 'results' / 'apparatus_candidates.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
