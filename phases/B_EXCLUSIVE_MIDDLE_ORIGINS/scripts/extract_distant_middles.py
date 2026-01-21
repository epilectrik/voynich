#!/usr/bin/env python3
"""Extract the 49 distant B-exclusive MIDDLEs (edit distance >= 3)."""

import pandas as pd
from pathlib import Path
from collections import Counter

DATA_PATH = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

# Morphology
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = ['pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe', 'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)
SUFFIXES = ['odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin', 'otaiin', 'etaiin', 'ataiin', 'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin', 'chedy', 'shedy', 'kedy', 'tedy', 'cheey', 'sheey', 'keey', 'teey', 'chey', 'shey', 'key', 'tey', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry', 'edy', 'eey', 'ey', 'chol', 'shol', 'kol', 'tol', 'chor', 'shor', 'kor', 'tor', 'eeol', 'eol', 'ool', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en', 'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im', 'y', 'l', 'r', 'm', 'n', 's', 'g']


def extract_middle(token):
    if pd.isna(token) or not token or '*' in str(token):
        return None
    token = str(token).strip()
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break
    if not prefix:
        return None
    remainder = token[len(prefix):]
    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break
    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder
    return middle if middle else '_EMPTY_'


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j+1]+1, curr[j]+1, prev[j]+(c1 != c2)))
        prev = curr
    return prev[-1]


def main():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    df['middle'] = df['word'].apply(extract_middle)

    df_a = df[df['language'] == 'A']
    df_b = df[df['language'] == 'B']

    a_middles = set(df_a['middle'].dropna().unique())
    b_middles = set(df_b['middle'].dropna().unique())
    shared = a_middles & b_middles
    b_exclusive = b_middles - a_middles

    print(f"B-exclusive MIDDLEs: {len(b_exclusive)}")
    print(f"Shared MIDDLEs: {len(shared)}")

    # Find distant MIDDLEs (distance >= 3)
    shared_list = [m for m in shared if m != '_EMPTY_']

    print("\nComputing edit distances...")
    distant = []
    for i, b_mid in enumerate(b_exclusive):
        if b_mid == '_EMPTY_':
            continue
        min_dist = min(levenshtein(b_mid, s_mid) for s_mid in shared_list)
        if min_dist >= 3:
            distant.append((b_mid, min_dist))
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(b_exclusive)}...")

    print(f"\n{'='*60}")
    print(f"DISTANT B-EXCLUSIVE MIDDLEs (edit distance >= 3): {len(distant)}")
    print(f"{'='*60}\n")

    # Get counts and positions
    for mid, dist in sorted(distant, key=lambda x: (-x[1], x[0])):
        tokens = df_b[df_b['middle'] == mid]
        count = len(tokens)

        # Check boundary position
        df_b_copy = df_b.copy()
        df_b_copy['line_len'] = df_b_copy.groupby(['folio', 'line_number'])['word'].transform('count')
        df_b_copy['pos'] = df_b_copy.groupby(['folio', 'line_number']).cumcount()

        mid_tokens = df_b_copy[df_b_copy['middle'] == mid]
        if len(mid_tokens) > 0:
            initial = (mid_tokens['pos'] == 0).sum()
            final = (mid_tokens['pos'] == mid_tokens['line_len'] - 1).sum()
            pos_str = f"init={initial}, final={final}"
        else:
            pos_str = "N/A"

        print(f"  {mid:25s} dist={dist}  count={count:3d}  {pos_str}")

    # Check for L-compounds
    print(f"\n{'='*60}")
    print("L-COMPOUND CHECK (lch, lk, lsh patterns)")
    print(f"{'='*60}\n")

    l_compound_distant = [m for m, d in distant if m.startswith('l')]
    print(f"L-compound distant MIDDLEs: {len(l_compound_distant)}")
    for mid in sorted(l_compound_distant):
        count = len(df_b[df_b['middle'] == mid])
        print(f"  {mid}: {count} occurrences")


if __name__ == '__main__':
    main()
