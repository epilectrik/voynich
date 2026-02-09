#!/usr/bin/env python3
"""
Deep analysis of f107v - highest intra-paragraph kernel variance
"""

import sys
from pathlib import Path
from collections import defaultdict
import json

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data.get('token_to_role', {})

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

def analyze_para(para):
    all_tokens = []
    for line_num, tokens in para:
        all_tokens.extend(tokens)
    words = [t.word for t in all_tokens]

    first_word = words[0] if words else ""
    gallows = first_word[0] if first_word else "?"

    k_count = sum(w.count('k') for w in words)
    h_count = sum(w.count('h') for w in words)
    e_count = sum(w.count('e') for w in words)
    total = k_count + h_count + e_count

    qo_count = sum(1 for w in words if w.startswith('qo'))
    ch_sh_count = sum(1 for w in words if w.startswith('ch') or w.startswith('sh'))

    roles = defaultdict(int)
    for w in words:
        role = token_to_role.get(w, 'UNK')
        roles[role] += 1

    return {
        'gallows': gallows,
        'first': first_word,
        'lines': len(para),
        'tokens': len(all_tokens),
        'k_pct': 100*k_count/total if total > 0 else 0,
        'h_pct': 100*h_count/total if total > 0 else 0,
        'e_pct': 100*e_count/total if total > 0 else 0,
        'qo': qo_count,
        'chsh': ch_sh_count,
        'roles': dict(roles),
        'words': words
    }

# Analyze f107v
folio = 'f107v'
paras = get_paragraphs(folio)

print(f"{'='*90}")
print(f"DEEP ANALYSIS: {folio} ({len(paras)} paragraphs)")
print("="*90)

stats = [analyze_para(p) for p in paras]

# Summary table
print(f"\n{'Par':<4} {'G':<3} {'L':<3} {'Tok':<5} {'k%':<6} {'h%':<6} {'e%':<6} {'qo':<4} {'chsh':<5} {'First Token':<20} {'Signature'}")
print("-"*90)

for i, s in enumerate(stats):
    # Determine signature
    if s['k_pct'] > 35:
        sig = "***HIGH-K***"
    elif s['h_pct'] > 40:
        sig = "***HIGH-H***"
    elif s['e_pct'] > 65:
        sig = "HIGH-E"
    elif s['k_pct'] < 10:
        sig = "LOW-K"
    elif s['h_pct'] < 10:
        sig = "LOW-H"
    else:
        sig = "balanced"

    print(f"{i+1:<4} {s['gallows']:<3} {s['lines']:<3} {s['tokens']:<5} "
          f"{s['k_pct']:<6.0f} {s['h_pct']:<6.0f} {s['e_pct']:<6.0f} "
          f"{s['qo']:<4} {s['chsh']:<5} {s['first'][:20]:<20} {sig}")

# Find extreme paragraphs
print(f"\n{'='*90}")
print("EXTREME PARAGRAPHS")
print("="*90)

# Sort by k%
by_k = sorted(enumerate(stats), key=lambda x: x[1]['k_pct'])
print(f"\nLowest k%: Par {by_k[0][0]+1} ({by_k[0][1]['k_pct']:.0f}%)")
print(f"  First token: {by_k[0][1]['first']}")
print(f"  Words: {' '.join(by_k[0][1]['words'][:15])}...")

print(f"\nHighest k%: Par {by_k[-1][0]+1} ({by_k[-1][1]['k_pct']:.0f}%)")
print(f"  First token: {by_k[-1][1]['first']}")
print(f"  Words: {' '.join(by_k[-1][1]['words'][:15])}...")

# Sort by h%
by_h = sorted(enumerate(stats), key=lambda x: x[1]['h_pct'])
print(f"\nLowest h%: Par {by_h[0][0]+1} ({by_h[0][1]['h_pct']:.0f}%)")
print(f"  First token: {by_h[0][1]['first']}")
print(f"  Words: {' '.join(by_h[0][1]['words'][:15])}...")

print(f"\nHighest h%: Par {by_h[-1][0]+1} ({by_h[-1][1]['h_pct']:.0f}%)")
print(f"  First token: {by_h[-1][1]['first']}")
print(f"  Words: {' '.join(by_h[-1][1]['words'][:15])}...")

# Role distribution comparison
print(f"\n{'='*90}")
print("ROLE DISTRIBUTION BY PARAGRAPH (% of tokens)")
print("="*90)

all_roles = set()
for s in stats:
    all_roles.update(s['roles'].keys())
all_roles = sorted(all_roles)

# Focus on major roles
major_roles = ['ENERGY_OPERATOR', 'FREQUENT_OPERATOR', 'FLOW_OPERATOR', 'CORE_CONTROL', 'UNK']

print(f"\n{'Par':<4}", end="")
for role in major_roles:
    print(f"{role[:8]:<10}", end="")
print()
print("-"*60)

for i, s in enumerate(stats):
    total = s['tokens']
    print(f"{i+1:<4}", end="")
    for role in major_roles:
        pct = 100 * s['roles'].get(role, 0) / total if total > 0 else 0
        print(f"{pct:<10.1f}", end="")
    print()

# Look for patterns
print(f"\n{'='*90}")
print("PATTERN ANALYSIS")
print("="*90)

# Group by gallows
gallows_groups = defaultdict(list)
for i, s in enumerate(stats):
    gallows_groups[s['gallows']].append((i+1, s))

print("\nBy gallows marker:")
for g in ['p', 't', 'k', 'f']:
    if g in gallows_groups:
        paras_in_group = gallows_groups[g]
        avg_k = sum(s['k_pct'] for _, s in paras_in_group) / len(paras_in_group)
        avg_h = sum(s['h_pct'] for _, s in paras_in_group) / len(paras_in_group)
        avg_e = sum(s['e_pct'] for _, s in paras_in_group) / len(paras_in_group)
        print(f"  {g}: {len(paras_in_group)} paragraphs, avg k={avg_k:.0f}% h={avg_h:.0f}% e={avg_e:.0f}%")
        for par_num, s in paras_in_group:
            print(f"      Par {par_num}: k={s['k_pct']:.0f}% h={s['h_pct']:.0f}% e={s['e_pct']:.0f}% | {s['first']}")

# Sequential pattern
print("\nSequential kernel progression:")
for i, s in enumerate(stats):
    bar_k = '*' * int(s['k_pct']/5)
    bar_h = '#' * int(s['h_pct']/5)
    print(f"  P{i+1:2d} k:{bar_k:<15} h:{bar_h:<15}")
