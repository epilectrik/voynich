#!/usr/bin/env python3
"""
Currier A PP Role Breakdown

Analyzes the PP zone of A paragraphs by functional role.
Shows what A records are "doing" in terms of operations.
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

# Role taxonomy from BCSC/constraint system
PREFIX_ROLES = {
    # Core operators
    'ch': 'CORE',
    'sh': 'CORE',

    # Control flow
    'qo': 'ESCAPE',
    'ok': 'AUXILIARY',
    'ol': 'LINK',
    'or': 'LINK',

    # Cross-reference
    'ct': 'CROSS-REF',

    # Closure/output
    'da': 'CLOSURE',
    'do': 'CLOSURE',

    # Gallows compounds
    'kch': 'GALLOWS-CH',
    'tch': 'GALLOWS-CH',
    'pch': 'GALLOWS-CH',
    'fch': 'GALLOWS-CH',
    'sch': 'GALLOWS-CH',
    'dch': 'GALLOWS-CH',

    # Input markers
    'po': 'INPUT',
    'so': 'INPUT',
    'to': 'INPUT',
    'ko': 'INPUT',

    # Other
    'ot': 'OTHER',
    'yk': 'OTHER',
    'ar': 'OTHER',
    'al': 'OTHER',
}

def get_role(prefix):
    """Get functional role for a PREFIX."""
    if prefix in PREFIX_ROLES:
        return PREFIX_ROLES[prefix]
    # Check for gallows-ch patterns
    if prefix and len(prefix) >= 2 and prefix[-2:] == 'ch':
        return 'GALLOWS-CH'
    if prefix and prefix.endswith('o') and len(prefix) == 2:
        return 'INPUT'
    return 'UNCLASSIFIED'

print("="*70)
print("CURRIER A PP ROLE BREAKDOWN")
print("="*70)

# Build paragraph data
paragraphs = []
current_folio = None
current_para = []
current_line = None
current_section = None

for token in tx.currier_a():
    if '*' in token.word:
        continue

    if token.folio != current_folio:
        if current_para:
            paragraphs.append({
                'folio': current_folio,
                'section': current_section,
                'tokens': [t.word for t in current_para]
            })
        current_folio = token.folio
        current_section = token.section
        current_para = [token]
        current_line = token.line
        continue

    if token.line != current_line:
        if token.word and token.word[0] in GALLOWS:
            paragraphs.append({
                'folio': current_folio,
                'section': current_section,
                'tokens': [t.word for t in current_para]
            })
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

if current_para:
    paragraphs.append({
        'folio': current_folio,
        'section': current_section,
        'tokens': [t.word for t in current_para]
    })

print(f"\nTotal A paragraphs: {len(paragraphs)}")

# Extract PP tokens (middle zone: positions 3 to -3)
all_pp_tokens = []
pp_by_section = defaultdict(list)

for para in paragraphs:
    tokens = para['tokens']
    if len(tokens) > 6:
        pp_tokens = tokens[3:-3]
    elif len(tokens) > 3:
        pp_tokens = tokens[3:]
    else:
        pp_tokens = []

    all_pp_tokens.extend(pp_tokens)
    pp_by_section[para['section']].extend(pp_tokens)

print(f"Total PP tokens: {len(all_pp_tokens)}")

# Analyze by PREFIX and role
prefix_counts = Counter()
role_counts = Counter()
prefix_to_role = {}

for token in all_pp_tokens:
    try:
        m = morph.extract(token)
        if m.prefix:
            prefix_counts[m.prefix] += 1
            role = get_role(m.prefix)
            role_counts[role] += 1
            prefix_to_role[m.prefix] = role
    except:
        pass

total_with_prefix = sum(prefix_counts.values())

print("\n" + "="*70)
print("ROLE DISTRIBUTION (All Currier A PP)")
print("="*70)

print(f"\n{'Role':<15} {'Count':<10} {'%':<10}")
print("-"*35)

for role, count in role_counts.most_common():
    pct = count / total_with_prefix * 100 if total_with_prefix > 0 else 0
    print(f"{role:<15} {count:<10} {pct:>6.1f}%")

# Show prefixes within each role
print("\n" + "="*70)
print("PREFIXES BY ROLE")
print("="*70)

role_prefixes = defaultdict(list)
for prefix, role in prefix_to_role.items():
    role_prefixes[role].append((prefix, prefix_counts[prefix]))

for role in ['CORE', 'ESCAPE', 'AUXILIARY', 'LINK', 'CROSS-REF', 'CLOSURE', 'GALLOWS-CH', 'INPUT']:
    if role in role_prefixes:
        prefixes = sorted(role_prefixes[role], key=lambda x: -x[1])
        prefix_str = ", ".join(f"{p}({c})" for p, c in prefixes[:8])
        print(f"\n{role}:")
        print(f"  {prefix_str}")

# Section comparison
print("\n" + "="*70)
print("ROLE DISTRIBUTION BY SECTION")
print("="*70)

for section in ['H', 'P', 'T']:
    if section not in pp_by_section:
        continue

    tokens = pp_by_section[section]
    sec_role_counts = Counter()
    sec_total = 0

    for token in tokens:
        try:
            m = morph.extract(token)
            if m.prefix:
                role = get_role(m.prefix)
                sec_role_counts[role] += 1
                sec_total += 1
        except:
            pass

    print(f"\nSection {section} ({len(tokens)} PP tokens):")
    print(f"  {'Role':<15} {'Count':<8} {'%':<8}")
    print(f"  " + "-"*30)

    for role in ['CORE', 'ESCAPE', 'AUXILIARY', 'LINK', 'CROSS-REF', 'CLOSURE', 'GALLOWS-CH', 'INPUT']:
        count = sec_role_counts.get(role, 0)
        pct = count / sec_total * 100 if sec_total > 0 else 0
        print(f"  {role:<15} {count:<8} {pct:>5.1f}%")

# Example folio breakdown
print("\n" + "="*70)
print("EXAMPLE FOLIO BREAKDOWN")
print("="*70)

# Pick a representative H folio with multiple paragraphs
example_folios = ['f2r', 'f3r', 'f4r']

for example_folio in example_folios:
    folio_paras = [p for p in paragraphs if p['folio'] == example_folio]
    if not folio_paras:
        continue

    print(f"\n{example_folio} ({len(folio_paras)} paragraphs):")

    folio_role_counts = Counter()
    folio_total = 0

    for para in folio_paras:
        tokens = para['tokens']
        if len(tokens) > 6:
            pp_tokens = tokens[3:-3]
        elif len(tokens) > 3:
            pp_tokens = tokens[3:]
        else:
            pp_tokens = []

        for token in pp_tokens:
            try:
                m = morph.extract(token)
                if m.prefix:
                    role = get_role(m.prefix)
                    folio_role_counts[role] += 1
                    folio_total += 1
            except:
                pass

    print(f"  PP tokens: {folio_total}")
    for role, count in folio_role_counts.most_common():
        pct = count / folio_total * 100 if folio_total > 0 else 0
        print(f"    {role:<15} {count:<5} ({pct:>5.1f}%)")

# Summary
print("\n" + "="*70)
print("SUMMARY: WHAT A PP TOKENS DO")
print("="*70)

print("""
Role breakdown shows what operations A records encode:

CORE (ch/sh):       Primary operators - the main "verbs"
ESCAPE (qo):        Safety/recovery operations
AUXILIARY (ok):     Supporting operations
LINK (ol/or):       Monitoring and intervention boundaries
CROSS-REF (ct):     Links to other entries (ct-ho vocabulary)
CLOSURE (da/do):    Output/completion markers
GALLOWS-CH:         Compound operators (kch, tch, pch, etc.)
INPUT:              Input specification markers

The distribution reveals what A records emphasize:
- High CORE = procedural content
- High ESCAPE = safety protocols
- High CROSS-REF = indexing/linking function
- High CLOSURE = output-focused records
""")
