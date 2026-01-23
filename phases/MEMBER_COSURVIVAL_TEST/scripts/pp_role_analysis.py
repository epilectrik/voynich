"""Analysis 4: Pipeline-Participating (PP) MIDDLE Role Analysis.

Analyze PP MIDDLEs as legality activators:
1. Do PP MIDDLEs sit in high-degree regions of the co-survival graph?
2. Do PP-rich A records activate broader legality fields?
3. Is PP presence predictive of legal MIDDLE count?

PP Definition: A MIDDLE is Pipeline-Participating if it appears in:
- Currier A records
- AZC contexts
- Currier B text
"""
import json
import pandas as pd
from pathlib import Path
from collections import defaultdict
import statistics

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Morphology extraction
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)


def extract_middle(token):
    """Extract MIDDLE component from token."""
    if pd.isna(token):
        return None
    token = str(token)
    if not token.strip():
        return None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            remainder = remainder[:-len(s)]
            break
    return remainder if remainder else None


def main():
    print("=" * 70)
    print("ANALYSIS 4: PIPELINE-PARTICIPATING MIDDLE ROLE")
    print("=" * 70)

    # Load transcript to identify PP MIDDLEs
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']

    df_a = df[df['language'] == 'A'].copy()
    df_b = df[df['language'] == 'B'].copy()
    df_azc = df[df['language'].isna()].copy()

    print(f"Currier A: {len(df_a)} tokens")
    print(f"Currier B: {len(df_b)} tokens")
    print(f"AZC: {len(df_azc)} tokens")

    # Extract MIDDLEs
    df_a['middle'] = df_a['word'].apply(extract_middle)
    df_b['middle'] = df_b['word'].apply(extract_middle)
    df_azc['middle'] = df_azc['word'].apply(extract_middle)

    # Identify PP MIDDLEs (appear in A AND AZC AND B)
    a_middles = set(df_a['middle'].dropna())
    b_middles = set(df_b['middle'].dropna())
    azc_middles = set(df_azc['middle'].dropna())

    pp_middles = a_middles & azc_middles & b_middles
    bypass_middles = (a_middles & b_middles) - azc_middles  # A and B but not AZC
    a_only_middles = a_middles - b_middles - azc_middles  # A only

    print(f"\nMIDDLE populations:")
    print(f"  A-only: {len(a_only_middles)}")
    print(f"  PP (A + AZC + B): {len(pp_middles)}")
    print(f"  Bypass (A + B, no AZC): {len(bypass_middles)}")

    # Load member survivor data
    data_path = PROJECT_ROOT / 'phases' / 'MEMBER_COSURVIVAL_TEST' / 'results' / 'member_survivors.json'
    with open(data_path, 'r') as f:
        data = json.load(f)

    records = data['records']
    total_contexts = len(records)

    # Load co-survival data for degree analysis
    cosurvival_path = PROJECT_ROOT / 'phases' / 'MEMBER_COSURVIVAL_TEST' / 'results' / 'middle_cosurvival.json'
    try:
        with open(cosurvival_path, 'r') as f:
            cosurvival_data = json.load(f)
        middle_context_counts = cosurvival_data.get('middle_context_counts', {})
    except FileNotFoundError:
        print("\nWARNING: middle_cosurvival.json not found. Run middle_cosurvival_matrix.py first.")
        middle_context_counts = {}

    # Analyze PP presence per A record
    print("\n" + "-" * 70)
    print("PP PRESENCE VS LEGALITY FIELD SIZE")
    print("-" * 70)

    pp_counts = []
    non_pp_counts = []
    legality_sizes = []

    for r in records:
        a_middles_in_record = set(r['a_middles'])
        pp_count = len(a_middles_in_record & pp_middles)
        non_pp_count = len(a_middles_in_record - pp_middles)
        legality_size = r['legal_middle_count']

        pp_counts.append(pp_count)
        non_pp_counts.append(non_pp_count)
        legality_sizes.append(legality_size)

    # Correlate PP count with legality size
    pp_rich_records = [(pp, leg) for pp, leg in zip(pp_counts, legality_sizes) if pp >= 3]
    pp_sparse_records = [(pp, leg) for pp, leg in zip(pp_counts, legality_sizes) if pp <= 1]

    if pp_rich_records:
        pp_rich_avg_legality = statistics.mean([leg for _, leg in pp_rich_records])
    else:
        pp_rich_avg_legality = 0

    if pp_sparse_records:
        pp_sparse_avg_legality = statistics.mean([leg for _, leg in pp_sparse_records])
    else:
        pp_sparse_avg_legality = 0

    print(f"PP-rich records (3+ PP MIDDLEs): {len(pp_rich_records)}")
    print(f"  Average legality field size: {pp_rich_avg_legality:.1f}")
    print(f"\nPP-sparse records (0-1 PP MIDDLEs): {len(pp_sparse_records)}")
    print(f"  Average legality field size: {pp_sparse_avg_legality:.1f}")

    # Simple correlation
    if len(pp_counts) > 0 and len(legality_sizes) > 0:
        mean_pp = statistics.mean(pp_counts)
        mean_leg = statistics.mean(legality_sizes)

        cov = sum((p - mean_pp) * (l - mean_leg) for p, l in zip(pp_counts, legality_sizes)) / len(pp_counts)
        std_pp = statistics.stdev(pp_counts) if len(pp_counts) > 1 else 1
        std_leg = statistics.stdev(legality_sizes) if len(legality_sizes) > 1 else 1

        if std_pp > 0 and std_leg > 0:
            correlation = cov / (std_pp * std_leg)
        else:
            correlation = 0

        print(f"\nCorrelation (PP count vs legality size): {correlation:.3f}")
    else:
        correlation = 0

    # Analyze PP MIDDLE degree in co-survival graph
    print("\n" + "-" * 70)
    print("PP MIDDLE DEGREE ANALYSIS")
    print("-" * 70)

    if middle_context_counts:
        pp_degrees = [middle_context_counts.get(m, 0) for m in pp_middles if m in middle_context_counts]
        non_pp_in_cosurvival = [m for m in middle_context_counts if m not in pp_middles]
        non_pp_degrees = [middle_context_counts[m] for m in non_pp_in_cosurvival]

        if pp_degrees:
            pp_avg_degree = statistics.mean(pp_degrees)
            print(f"PP MIDDLEs in co-survival graph: {len(pp_degrees)}")
            print(f"  Average context count (degree): {pp_avg_degree:.1f}")

        if non_pp_degrees:
            non_pp_avg_degree = statistics.mean(non_pp_degrees)
            print(f"\nNon-PP MIDDLEs in co-survival graph: {len(non_pp_degrees)}")
            print(f"  Average context count (degree): {non_pp_avg_degree:.1f}")

        if pp_degrees and non_pp_degrees:
            ratio = pp_avg_degree / non_pp_avg_degree if non_pp_avg_degree > 0 else float('inf')
            print(f"\nDegree ratio (PP / non-PP): {ratio:.2f}")
    else:
        pp_avg_degree = 0
        non_pp_avg_degree = 0

    # Determine evidence strength
    if correlation > 0.5 and pp_rich_avg_legality > pp_sparse_avg_legality * 1.2:
        evidence = "strong"
    elif correlation > 0.2 or pp_rich_avg_legality > pp_sparse_avg_legality:
        evidence = "moderate"
    else:
        evidence = "weak"

    print(f"\n" + "=" * 70)
    print(f"PP AS LEGALITY ACTIVATOR: {evidence.upper()} EVIDENCE")
    print("=" * 70)

    # Save results
    output = {
        'metadata': {
            'total_contexts': total_contexts,
            'pp_middles_count': len(pp_middles),
            'bypass_middles_count': len(bypass_middles),
            'a_only_middles_count': len(a_only_middles)
        },
        'pp_middles': sorted(pp_middles),
        'bypass_middles': sorted(bypass_middles),
        'legality_analysis': {
            'pp_rich_count': len(pp_rich_records),
            'pp_rich_avg_legality': round(pp_rich_avg_legality, 2),
            'pp_sparse_count': len(pp_sparse_records),
            'pp_sparse_avg_legality': round(pp_sparse_avg_legality, 2),
            'correlation_pp_vs_legality': round(correlation, 4)
        },
        'degree_analysis': {
            'pp_avg_degree': round(pp_avg_degree, 2) if middle_context_counts else None,
            'non_pp_avg_degree': round(non_pp_avg_degree, 2) if middle_context_counts else None
        },
        'evidence_strength': evidence
    }

    output_path = PROJECT_ROOT / 'phases' / 'MEMBER_COSURVIVAL_TEST' / 'results' / 'pp_role_analysis.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")


if __name__ == '__main__':
    main()
