#!/usr/bin/env python3
"""Find high-frequency B-exclusive MIDDLEs - the likely operators."""

import pandas as pd
from pathlib import Path
from collections import Counter

DATA_PATH = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

# Morphology
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = ['pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe', 'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)
SUFFIXES = ['odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin', 'otaiin', 'etaiin', 'ataiin', 'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin', 'chedy', 'shedy', 'kedy', 'tedy', 'cheey', 'sheey', 'keey', 'teey', 'chey', 'shey', 'key', 'tey', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry', 'edy', 'eey', 'ey', 'chol', 'shol', 'kol', 'tol', 'chor', 'shor', 'kor', 'tor', 'eeol', 'eol', 'ool', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en', 'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im', 'y', 'l', 'r', 'm', 'n', 's', 'g']


def extract_morphology(token):
    if pd.isna(token) or not token or '*' in str(token):
        return None, None, None
    token = str(token).strip()
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break
    if not prefix:
        return None, None, None
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
    return prefix, middle if middle else '_EMPTY_', suffix


def main():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']

    morph = df['word'].apply(extract_morphology)
    df['prefix'] = morph.apply(lambda x: x[0])
    df['middle'] = morph.apply(lambda x: x[1])
    df['suffix'] = morph.apply(lambda x: x[2])

    df_a = df[df['language'] == 'A']
    df_b = df[df['language'] == 'B']

    a_middles = set(df_a['middle'].dropna().unique())
    b_middles = set(df_b['middle'].dropna().unique())
    b_exclusive = b_middles - a_middles

    # Count B-exclusive MIDDLE frequencies
    b_excl_tokens = df_b[df_b['middle'].isin(b_exclusive)]
    middle_counts = Counter(b_excl_tokens['middle'].dropna())

    # Add position info
    df_b = df_b.copy()
    df_b['line_len'] = df_b.groupby(['folio', 'line_number'])['word'].transform('count')
    df_b['pos'] = df_b.groupby(['folio', 'line_number']).cumcount()
    df_b['is_initial'] = df_b['pos'] == 0
    df_b['is_final'] = df_b['pos'] == df_b['line_len'] - 1

    print(f"\n{'='*70}")
    print("TOP 30 B-EXCLUSIVE MIDDLEs BY FREQUENCY")
    print(f"{'='*70}\n")

    print(f"{'MIDDLE':<15} {'Count':>6} {'Init%':>7} {'Final%':>7} {'Bound%':>7} {'Prefixes'}")
    print("-" * 70)

    for middle, count in middle_counts.most_common(30):
        tokens = df_b[df_b['middle'] == middle]
        init_pct = tokens['is_initial'].mean() * 100
        final_pct = tokens['is_final'].mean() * 100
        bound_pct = (tokens['is_initial'] | tokens['is_final']).mean() * 100

        # Get prefixes used with this MIDDLE
        prefixes = tokens['prefix'].value_counts().head(3)
        prefix_str = ', '.join(f"{p}({c})" for p, c in prefixes.items())

        print(f"{middle:<15} {count:>6} {init_pct:>6.1f}% {final_pct:>6.1f}% {bound_pct:>6.1f}%  {prefix_str}")

    # L-compound analysis
    print(f"\n{'='*70}")
    print("L-COMPOUND B-EXCLUSIVE MIDDLEs (C298 grammar operators)")
    print(f"{'='*70}\n")

    l_compound_middles = [m for m in b_exclusive if m.startswith('l') and m != '_EMPTY_']
    l_counts = {m: middle_counts.get(m, 0) for m in l_compound_middles}

    print(f"Total L-compound B-exclusive MIDDLEs: {len(l_compound_middles)}")
    print(f"Total L-compound tokens: {sum(l_counts.values())}")
    print()

    for middle, count in sorted(l_counts.items(), key=lambda x: -x[1])[:15]:
        if count == 0:
            continue
        tokens = df_b[df_b['middle'] == middle]
        init_pct = tokens['is_initial'].mean() * 100
        print(f"  {middle:<15} count={count:>3}  line-initial={init_pct:.0f}%")

    # Summary stats
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")

    total_b_excl_tokens = len(b_excl_tokens)
    top10_coverage = sum(c for _, c in middle_counts.most_common(10)) / total_b_excl_tokens * 100

    print(f"Total B-exclusive token instances: {total_b_excl_tokens}")
    print(f"Total B-exclusive MIDDLE types: {len(b_exclusive)}")
    print(f"Top 10 MIDDLEs cover: {top10_coverage:.1f}% of B-exclusive tokens")

    # Singletons
    singletons = sum(1 for m, c in middle_counts.items() if c == 1)
    print(f"Singleton MIDDLEs (count=1): {singletons} ({singletons/len(b_exclusive)*100:.1f}%)")


if __name__ == '__main__':
    main()
