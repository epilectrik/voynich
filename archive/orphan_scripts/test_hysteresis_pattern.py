#!/usr/bin/env python3
"""
Test if paragraph sequences show hysteresis pattern (alternating HIGH-K and HIGH-H)
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

folio_line_tokens = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_line_tokens[token.folio][token.line].append(token)

def get_paragraphs(folio):
    lines = folio_line_tokens[folio]
    paragraphs = []
    current_para = []
    for line_num in sorted(lines.keys()):
        tokens = lines[line_num]
        if not tokens:
            continue
        first_word = tokens[0].word
        if first_word and first_word[0] in GALLOWS:
            if current_para:
                paragraphs.append(current_para)
            current_para = [(line_num, tokens)]
        else:
            current_para.append((line_num, tokens))
    if current_para:
        paragraphs.append(current_para)
    return paragraphs

def get_kernel_profile(para):
    words = []
    for line_num, tokens in para:
        words.extend([t.word for t in tokens])

    k = sum(w.count('k') for w in words)
    h = sum(w.count('h') for w in words)
    e = sum(w.count('e') for w in words)
    total = k + h + e

    if total < 10:  # Too small
        return None

    k_pct = 100 * k / total
    h_pct = 100 * h / total

    # Classify
    if k_pct > 35 and h_pct < 20:
        return 'K'  # Energy phase
    elif h_pct > 35 and k_pct < 20:
        return 'H'  # Monitor phase
    elif k_pct > h_pct + 10:
        return 'k'  # Mild energy bias
    elif h_pct > k_pct + 10:
        return 'h'  # Mild monitor bias
    else:
        return 'B'  # Balanced

# Test f107v specifically
print("="*70)
print("f107v HYSTERESIS PATTERN TEST")
print("="*70)

paras = get_paragraphs('f107v')
profiles = []
for i, p in enumerate(paras):
    profile = get_kernel_profile(p)
    if profile:
        profiles.append((i+1, profile))

print("\nParagraph sequence (K=HIGH-K, H=HIGH-H, k=mild-K, h=mild-H, B=balanced):")
print("  " + " -> ".join([f"P{n}:{p}" for n, p in profiles]))

# Count transitions
transitions = defaultdict(int)
for i in range(len(profiles)-1):
    t = profiles[i][1] + "->" + profiles[i+1][1]
    transitions[t] += 1

print("\nTransitions:")
for t, count in sorted(transitions.items(), key=lambda x: -x[1]):
    print(f"  {t}: {count}")

# Check for alternation
alternations = 0
same_phase = 0
for i in range(len(profiles)-1):
    p1, p2 = profiles[i][1], profiles[i+1][1]
    # K/k vs H/h alternation
    if (p1 in 'Kk' and p2 in 'Hh') or (p1 in 'Hh' and p2 in 'Kk'):
        alternations += 1
    elif (p1 in 'Kk' and p2 in 'Kk') or (p1 in 'Hh' and p2 in 'Hh'):
        same_phase += 1

print(f"\nK<->H alternations: {alternations}")
print(f"Same-phase consecutive: {same_phase}")

# Test ALL folios for hysteresis pattern
print("\n" + "="*70)
print("ALL FOLIOS: HYSTERESIS PATTERN STRENGTH")
print("="*70)

folio_results = []
for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    if len(paras) < 4:
        continue

    profiles = []
    for p in paras:
        profile = get_kernel_profile(p)
        if profile:
            profiles.append(profile)

    if len(profiles) < 4:
        continue

    # Count alternations vs same-phase
    alt = 0
    same = 0
    for i in range(len(profiles)-1):
        p1, p2 = profiles[i], profiles[i+1]
        if (p1 in 'Kk' and p2 in 'Hh') or (p1 in 'Hh' and p2 in 'Kk'):
            alt += 1
        elif (p1 in 'Kk' and p2 in 'Kk') or (p1 in 'Hh' and p2 in 'Hh'):
            same += 1

    total_transitions = alt + same
    if total_transitions > 0:
        alt_ratio = alt / total_transitions
        folio_results.append((folio, len(profiles), alt, same, alt_ratio, profiles))

# Sort by alternation ratio
folio_results.sort(key=lambda x: -x[4])

print(f"\n{'Folio':<10} {'Paras':<6} {'Alt':<5} {'Same':<5} {'Alt%':<7} {'Sequence'}")
print("-"*80)
for folio, n, alt, same, ratio, profiles in folio_results[:20]:
    seq = ''.join(profiles[:15])
    if len(profiles) > 15:
        seq += "..."
    print(f"{folio:<10} {n:<6} {alt:<5} {same:<5} {100*ratio:<7.0f} {seq}")

# Statistical summary
print("\n" + "="*70)
print("SUMMARY STATISTICS")
print("="*70)

all_alt = sum(x[2] for x in folio_results)
all_same = sum(x[3] for x in folio_results)
print(f"\nTotal K<->H alternations across all folios: {all_alt}")
print(f"Total same-phase consecutive: {all_same}")
if all_alt + all_same > 0:
    print(f"Overall alternation ratio: {100*all_alt/(all_alt+all_same):.1f}%")
    print(f"\nIf random, expected ~50% alternation")
    print(f"If pure hysteresis, expected ~100% alternation")
    print(f"If sequential (K->K->K->H->H->H), expected ~0% alternation")
