#!/usr/bin/env python3
"""
Discriminate frog from other REGIME_4 animals.

Frog: UNKNOWN -> LINK (2 steps, simplest)
Chicken: e_ESCAPE -> AUX -> UNKNOWN -> e_ESCAPE (4 steps, escape-heavy)
Blood/milk: e_ESCAPE -> FLOW -> UNKNOWN -> UNKNOWN (4 steps, escape + flow)

Frog should have:
- FLATTEST PREFIX profile (no strong signal = UNKNOWN start)
- P(animal) = 1.00
- Moderate record size (not the biggest, not the smallest)
"""

import pandas as pd
from pathlib import Path
import json

PROJECT_ROOT = Path('C:/git/voynich')

df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()

PREFIXES = ['qo', 'da', 'ok', 'ot', 'ol', 'ch', 'sh', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)

def extract_prefix(token):
    if pd.isna(token): return None
    token = str(token)
    for p in ALL_PREFIXES:
        if token.startswith(p):
            return p
    return None

# Key animal candidates and their records
animal_candidates = {
    'eoschso': ('f90r1', '6'),    # Known chicken
    'ofy': [('f21r', '4'), ('f8r', '14')],
    'hdaoto': ('f100r', '1'),
    'cthso': ('f100r', '1'),
    'olfcho': ('f89r2', '4'),
    'eyd': ('f89r2', '1'),
    'chald': ('f23r', '4'),
    'ha': ('f47r', '8'),
    'eeees': ('f27v', '4'),
    'eoc': ('f89v1', '11'),
}

print("=" * 70)
print("FROG DISCRIMINATION: PREFIX Profile Analysis")
print("=" * 70)
print()

# Analyze PREFIX profile for each candidate's record
def analyze_record(folio, line):
    record = df_a[(df_a['folio'] == folio) & (df_a['line_number'] == str(line))]
    if len(record) == 0:
        return None

    record = record.copy()
    record['prefix'] = record['word'].apply(extract_prefix)
    prefix_counts = record['prefix'].value_counts()
    total = len(record)

    # Calculate "flatness" - how evenly distributed are prefixes?
    # Frog should have NO dominant prefix (UNKNOWN start)
    profile = {}
    for p in ['qo', 'da', 'ok', 'ot', 'ol', 'ch', 'sh']:
        count = prefix_counts.get(p, 0)
        profile[p] = count / total if total > 0 else 0

    # Calculate max ratio (flattest = lowest max ratio)
    max_ratio = max(profile.values()) if profile else 0

    return {
        'total': total,
        'profile': profile,
        'max_ratio': max_ratio,
        'words': list(record['word'])
    }

print(f"{'Token':<12} {'Location':<12} {'Size':<6} {'Max%':<8} {'qo%':<6} {'da%':<6} {'Signature':<15}")
print("-" * 75)

results = []
for token, loc in animal_candidates.items():
    if isinstance(loc, list):
        # Multiple locations - analyze first
        folio, line = loc[0]
    else:
        folio, line = loc

    analysis = analyze_record(folio, line)
    if analysis:
        sig = "ESCAPE-heavy" if analysis['profile']['qo'] > 0.25 else \
              "FLOW-heavy" if analysis['profile']['da'] > 0.15 else \
              "FLAT (frog?)" if analysis['max_ratio'] < 0.20 else "MODERATE"

        print(f"{token:<12} {folio}:{line:<6} {analysis['total']:<6} {analysis['max_ratio']*100:<8.1f} {analysis['profile']['qo']*100:<6.1f} {analysis['profile']['da']*100:<6.1f} {sig:<15}")

        results.append({
            'token': token,
            'folio': folio,
            'line': line,
            'total': analysis['total'],
            'max_ratio': analysis['max_ratio'],
            'qo': analysis['profile']['qo'],
            'da': analysis['profile']['da'],
            'sig': sig,
            'words': analysis['words']
        })

print()
print("=" * 70)
print("FLAT PREFIX PROFILES (Frog candidates)")
print("=" * 70)
print()

# Frog = UNKNOWN -> LINK = flattest profile, no dominant prefix
flat_candidates = [r for r in results if r['sig'] == 'FLAT (frog?)']

if flat_candidates:
    print(f"Found {len(flat_candidates)} candidates with FLAT prefix profile:")
    print()
    for r in flat_candidates:
        print(f"  {r['token']} in {r['folio']}:{r['line']}")
        print(f"    Size: {r['total']} tokens")
        print(f"    Max prefix ratio: {r['max_ratio']*100:.1f}%")
        print(f"    qo: {r['qo']*100:.1f}%, da: {r['da']*100:.1f}%")
        print(f"    Words: {r['words'][:8]}...")
        print()
else:
    print("No perfectly flat profiles found. Looking for most moderate:")
    moderate = [r for r in results if r['token'] != 'eoschso']
    moderate.sort(key=lambda x: x['max_ratio'])
    for r in moderate[:3]:
        print(f"  {r['token']}: max_ratio={r['max_ratio']*100:.1f}%")

print()
print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print()

# Sort by flatness (lowest max_ratio = most likely frog)
results_sorted = sorted([r for r in results if r['token'] != 'eoschso'],
                        key=lambda x: x['max_ratio'])

if results_sorted:
    best = results_sorted[0]
    print(f"Best frog candidate: {best['token']}")
    print(f"  Location: {best['folio']}:{best['line']}")
    print(f"  Reasoning: Flattest PREFIX profile (max_ratio = {best['max_ratio']*100:.1f}%)")
    print(f"  This matches frog's UNKNOWN->LINK pattern (no dominant prefix)")
