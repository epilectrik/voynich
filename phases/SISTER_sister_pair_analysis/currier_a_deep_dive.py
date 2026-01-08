"""
Currier A Deep Dive: DA Anomaly + Universal MIDDLEs

Exploring:
1. Why is DA so different? (7.88x attraction to -in, 0.08x avoidance of -ol)
2. What are the universal MIDDLEs and what do they tell us?

Tier 4 - Exploratory
"""

import os
import re
from collections import defaultdict, Counter

# Known prefixes and suffixes
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = ['aiin', 'ain', 'ar', 'al', 'or', 'ol', 'am', 'an', 'in', 'y', 'dy', 'ey', 'edy', 'eedy', 'chy', 'shy', 'r', 'l', 's', 'd', 'n', 'm']
SUFFIX_PATTERNS = sorted(SUFFIXES, key=len, reverse=True)

def load_currier_a_tokens():
    """Load tokens from Currier A folios."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    tokens = []
    seen = set()

    with open(filepath, 'r', encoding='latin-1') as f:
        header = None
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split('\t')
            parts = [p.strip('"') for p in parts]

            if header is None:
                header = parts
                continue

            if len(parts) < 7:
                continue

            token = parts[0]
            folio = parts[2]
            section = parts[3]
            currier = parts[6]
            transcriber = parts[12] if len(parts) > 12 else ''

            if currier == 'A' and transcriber == 'H' and token and '*' not in token:
                key = (folio, token)
                if key not in seen:
                    seen.add(key)
                    tokens.append({'folio': folio, 'token': token, 'section': section})

    return tokens

def decompose_token(token):
    """Decompose token into PREFIX + MIDDLE + SUFFIX."""
    prefix = None
    remainder = token

    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            remainder = token[len(p):]
            break

    if not prefix:
        return None, None, None

    suffix = None
    middle = remainder

    for s in SUFFIX_PATTERNS:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            middle = remainder[:-len(s)]
            break
        elif remainder == s:
            suffix = s
            middle = ''
            break

    if not suffix:
        if len(remainder) >= 2:
            suffix = remainder[-2:]
            middle = remainder[:-2]
        elif len(remainder) == 1:
            suffix = remainder
            middle = ''
        else:
            suffix = ''
            middle = ''

    return prefix, middle, suffix

def analyze_da_anomaly(tokens):
    """Deep dive into the DA prefix anomaly."""

    print("=" * 70)
    print("DEEP DIVE 1: The DA Anomaly")
    print("=" * 70)

    # Decompose all tokens
    decomposed = []
    for t in tokens:
        prefix, middle, suffix = decompose_token(t['token'])
        if prefix:
            decomposed.append({
                'token': t['token'],
                'folio': t['folio'],
                'section': t['section'],
                'prefix': prefix,
                'middle': middle,
                'suffix': suffix
            })

    # Separate DA from others
    da_tokens = [d for d in decomposed if d['prefix'] == 'da']
    other_tokens = [d for d in decomposed if d['prefix'] != 'da']

    print(f"\nDA tokens: {len(da_tokens)}")
    print(f"Other tokens: {len(other_tokens)}")

    # === DA suffix distribution vs others ===
    print("\n--- Suffix Distribution: DA vs Others ---")

    da_suffixes = Counter(d['suffix'] for d in da_tokens)
    other_suffixes = Counter(d['suffix'] for d in other_tokens)

    print(f"\n{'Suffix':<10} {'DA':<10} {'DA %':<10} {'Others':<10} {'Others %':<10} {'Ratio':<10}")
    print("-" * 60)

    all_suffixes = set(da_suffixes.keys()) | set(other_suffixes.keys())
    suffix_data = []
    for suffix in all_suffixes:
        da_count = da_suffixes[suffix]
        other_count = other_suffixes[suffix]
        da_pct = 100 * da_count / len(da_tokens) if da_tokens else 0
        other_pct = 100 * other_count / len(other_tokens) if other_tokens else 0
        ratio = da_pct / other_pct if other_pct > 0 else float('inf')
        suffix_data.append((suffix, da_count, da_pct, other_count, other_pct, ratio))

    # Sort by ratio descending
    suffix_data.sort(key=lambda x: -x[5] if x[5] != float('inf') else -9999)

    for suffix, da_c, da_p, oth_c, oth_p, ratio in suffix_data[:15]:
        ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "INF"
        print(f"{suffix:<10} {da_c:<10} {da_p:<10.1f} {oth_c:<10} {oth_p:<10.1f} {ratio_str:<10}")

    # === DA middle distribution ===
    print("\n--- DA Middle Components ---")

    da_middles = Counter(d['middle'] for d in da_tokens)
    print(f"\nUnique DA middles: {len(da_middles)}")
    print("\nTop 15 DA middles:")
    for middle, count in da_middles.most_common(15):
        pct = 100 * count / len(da_tokens)
        # Show full tokens with this middle
        examples = [d['token'] for d in da_tokens if d['middle'] == middle][:5]
        print(f"  -{middle}- : {count} ({pct:.1f}%) - e.g., {', '.join(examples)}")

    # === DA section distribution vs others ===
    print("\n--- Section Distribution: DA vs Others ---")

    da_sections = Counter(d['section'] for d in da_tokens)
    other_sections = Counter(d['section'] for d in other_tokens)

    print(f"\n{'Section':<10} {'DA':<10} {'DA %':<10} {'Others':<10} {'Others %':<10}")
    print("-" * 50)

    for section in sorted(set(da_sections.keys()) | set(other_sections.keys())):
        da_c = da_sections[section]
        oth_c = other_sections[section]
        da_p = 100 * da_c / len(da_tokens) if da_tokens else 0
        oth_p = 100 * oth_c / len(other_tokens) if other_tokens else 0
        print(f"{section:<10} {da_c:<10} {da_p:<10.1f} {oth_c:<10} {oth_p:<10.1f}")

    # === What tokens end in -in? ===
    print("\n--- All tokens ending in -in (DA's favorite suffix) ---")

    in_tokens = [d for d in decomposed if d['suffix'] == 'in']
    in_by_prefix = Counter(d['prefix'] for d in in_tokens)

    print(f"\nTotal -in tokens: {len(in_tokens)}")
    print("By prefix:")
    for prefix, count in in_by_prefix.most_common():
        pct = 100 * count / len(in_tokens)
        print(f"  {prefix}: {count} ({pct:.1f}%)")

    # === What tokens end in -ol? (DA avoids this) ===
    print("\n--- All tokens ending in -ol (DA avoids this) ---")

    ol_tokens = [d for d in decomposed if d['suffix'] == 'ol']
    ol_by_prefix = Counter(d['prefix'] for d in ol_tokens)

    print(f"\nTotal -ol tokens: {len(ol_tokens)}")
    print("By prefix:")
    for prefix, count in ol_by_prefix.most_common():
        pct = 100 * count / len(ol_tokens)
        print(f"  {prefix}: {count} ({pct:.1f}%)")

    # === DA's actual tokens ===
    print("\n--- Most common DA tokens ---")
    da_token_counts = Counter(d['token'] for d in da_tokens)
    print(f"\nTop 20 DA tokens:")
    for token, count in da_token_counts.most_common(20):
        print(f"  {token}: {count}")

    # === Is DA more like a structural element? ===
    print("\n--- DA Pattern Analysis ---")

    # Check if daiin is dominant
    daiin_count = sum(1 for d in da_tokens if d['token'] == 'daiin')
    dain_count = sum(1 for d in da_tokens if d['token'] == 'dain')
    dar_count = sum(1 for d in da_tokens if d['token'] == 'dar')

    print(f"\n'daiin' alone: {daiin_count} ({100*daiin_count/len(da_tokens):.1f}% of all DA)")
    print(f"'dain' alone: {dain_count} ({100*dain_count/len(da_tokens):.1f}% of all DA)")
    print(f"'dar' alone: {dar_count} ({100*dar_count/len(da_tokens):.1f}% of all DA)")
    print(f"These three: {daiin_count + dain_count + dar_count} ({100*(daiin_count+dain_count+dar_count)/len(da_tokens):.1f}%)")

    return decomposed

def analyze_universal_middles(decomposed):
    """Deep dive into universal MIDDLEs."""

    print("\n" + "=" * 70)
    print("DEEP DIVE 2: Universal MIDDLEs (Cross-Family Properties)")
    print("=" * 70)

    # Find middles that appear with 4+ prefixes
    middle_to_data = defaultdict(lambda: {'prefixes': set(), 'tokens': [], 'suffixes': Counter()})

    for d in decomposed:
        if d['middle']:
            middle_to_data[d['middle']]['prefixes'].add(d['prefix'])
            middle_to_data[d['middle']]['tokens'].append(d)
            middle_to_data[d['middle']]['suffixes'][d['suffix']] += 1

    # Universal = 4+ prefixes
    universal = [(m, data) for m, data in middle_to_data.items() if len(data['prefixes']) >= 4]
    universal.sort(key=lambda x: -len(x[1]['tokens']))

    print(f"\nUniversal MIDDLEs (appear with 4+ prefixes): {len(universal)}")

    print("\n--- Universal MIDDLEs Detail ---")
    for middle, data in universal[:20]:
        prefixes = sorted(data['prefixes'])
        token_count = len(data['tokens'])
        top_suffixes = data['suffixes'].most_common(3)

        print(f"\n  -{middle}-")
        print(f"    Prefixes ({len(prefixes)}): {', '.join(prefixes)}")
        print(f"    Total tokens: {token_count}")
        print(f"    Top suffixes: {', '.join(f'{s}({c})' for s, c in top_suffixes)}")

        # Show examples
        examples = {}
        for d in data['tokens'][:20]:
            if d['prefix'] not in examples:
                examples[d['prefix']] = d['token']
        print(f"    Examples: {', '.join(f'{p}:{t}' for p, t in sorted(examples.items()))}")

    # === Are universal middles the "simple" ones? ===
    print("\n--- Universal vs Exclusive: Complexity Analysis ---")

    exclusive = [(m, data) for m, data in middle_to_data.items() if len(data['prefixes']) == 1]

    universal_lengths = [len(m) for m, _ in universal]
    exclusive_lengths = [len(m) for m, _ in exclusive]

    avg_universal = sum(universal_lengths) / len(universal_lengths) if universal_lengths else 0
    avg_exclusive = sum(exclusive_lengths) / len(exclusive_lengths) if exclusive_lengths else 0

    print(f"\nAverage MIDDLE length:")
    print(f"  Universal (4+ prefixes): {avg_universal:.2f} chars")
    print(f"  Exclusive (1 prefix): {avg_exclusive:.2f} chars")

    # === What suffixes pair with universal middles? ===
    print("\n--- Suffix patterns with Universal MIDDLEs ---")

    universal_suffix_counts = Counter()
    for _, data in universal:
        universal_suffix_counts.update(data['suffixes'])

    exclusive_suffix_counts = Counter()
    for _, data in exclusive:
        exclusive_suffix_counts.update(data['suffixes'])

    print(f"\n{'Suffix':<10} {'Universal':<12} {'Univ %':<10} {'Exclusive':<12} {'Excl %':<10}")
    print("-" * 55)

    total_univ = sum(universal_suffix_counts.values())
    total_excl = sum(exclusive_suffix_counts.values())

    all_suff = set(universal_suffix_counts.keys()) | set(exclusive_suffix_counts.keys())
    for suffix in sorted(all_suff, key=lambda s: -universal_suffix_counts[s]):
        u_c = universal_suffix_counts[suffix]
        e_c = exclusive_suffix_counts[suffix]
        u_p = 100 * u_c / total_univ if total_univ else 0
        e_p = 100 * e_c / total_excl if total_excl else 0
        if u_c > 20 or e_c > 20:
            print(f"{suffix:<10} {u_c:<12} {u_p:<10.1f} {e_c:<12} {e_p:<10.1f}")

    # === Cross-tabulation: which prefixes share which middles? ===
    print("\n--- Prefix Similarity via Shared MIDDLEs ---")

    # Build prefix-prefix similarity matrix based on shared middles
    prefix_middles = defaultdict(set)
    for d in decomposed:
        if d['middle']:
            prefix_middles[d['prefix']].add(d['middle'])

    print(f"\n{'':8}", end='')
    for p in PREFIXES:
        print(f"{p:>8}", end='')
    print()

    for p1 in PREFIXES:
        print(f"{p1:8}", end='')
        for p2 in PREFIXES:
            shared = len(prefix_middles[p1] & prefix_middles[p2])
            print(f"{shared:>8}", end='')
        print()

    # === Jaccard similarity ===
    print("\n--- Prefix Jaccard Similarity (shared middles / union) ---")

    print(f"\n{'':8}", end='')
    for p in PREFIXES:
        print(f"{p:>8}", end='')
    print()

    for p1 in PREFIXES:
        print(f"{p1:8}", end='')
        for p2 in PREFIXES:
            union = len(prefix_middles[p1] | prefix_middles[p2])
            shared = len(prefix_middles[p1] & prefix_middles[p2])
            jaccard = shared / union if union > 0 else 0
            print(f"{jaccard:>8.2f}", end='')
        print()

    # === Which prefixes are most similar? ===
    print("\n--- Most Similar Prefix Pairs (by shared middles) ---")

    pairs = []
    for i, p1 in enumerate(PREFIXES):
        for p2 in PREFIXES[i+1:]:
            union = len(prefix_middles[p1] | prefix_middles[p2])
            shared = len(prefix_middles[p1] & prefix_middles[p2])
            jaccard = shared / union if union > 0 else 0
            pairs.append((p1, p2, shared, jaccard))

    pairs.sort(key=lambda x: -x[3])
    print("\nTop 10 most similar:")
    for p1, p2, shared, jaccard in pairs[:10]:
        print(f"  {p1}-{p2}: {shared} shared middles, Jaccard={jaccard:.3f}")

    print("\nBottom 5 (most different):")
    for p1, p2, shared, jaccard in pairs[-5:]:
        print(f"  {p1}-{p2}: {shared} shared middles, Jaccard={jaccard:.3f}")

def analyze_prefix_families(decomposed):
    """Try to cluster prefixes into families based on behavior."""

    print("\n" + "=" * 70)
    print("DEEP DIVE 3: Prefix Family Clustering")
    print("=" * 70)

    # Build feature vectors for each prefix
    features = {}

    for prefix in PREFIXES:
        prefix_tokens = [d for d in decomposed if d['prefix'] == prefix]

        if not prefix_tokens:
            continue

        # Features:
        suffix_dist = Counter(d['suffix'] for d in prefix_tokens)
        section_dist = Counter(d['section'] for d in prefix_tokens)
        middle_lengths = [len(d['middle']) for d in prefix_tokens]

        features[prefix] = {
            'count': len(prefix_tokens),
            'top_suffix': suffix_dist.most_common(1)[0][0] if suffix_dist else '',
            'top_suffix_pct': 100 * suffix_dist.most_common(1)[0][1] / len(prefix_tokens) if suffix_dist else 0,
            'avg_middle_len': sum(middle_lengths) / len(middle_lengths) if middle_lengths else 0,
            'unique_middles': len(set(d['middle'] for d in prefix_tokens)),
            'section_H_pct': 100 * section_dist.get('H', 0) / len(prefix_tokens),
            'section_P_pct': 100 * section_dist.get('P', 0) / len(prefix_tokens),
            'section_T_pct': 100 * section_dist.get('T', 0) / len(prefix_tokens),
            'in_pct': 100 * suffix_dist.get('in', 0) / len(prefix_tokens),
            'ol_pct': 100 * suffix_dist.get('ol', 0) / len(prefix_tokens),
            'y_pct': 100 * suffix_dist.get('y', 0) / len(prefix_tokens),
        }

    print("\n--- Prefix Feature Comparison ---")
    print(f"\n{'Prefix':<8} {'Count':<8} {'TopSuf':<8} {'TopSuf%':<10} {'AvgMidLen':<12} {'UniqMid':<10}")
    print("-" * 60)
    for prefix in PREFIXES:
        if prefix in features:
            f = features[prefix]
            print(f"{prefix:<8} {f['count']:<8} {f['top_suffix']:<8} {f['top_suffix_pct']:<10.1f} {f['avg_middle_len']:<12.2f} {f['unique_middles']:<10}")

    print("\n--- Section Distribution by Prefix ---")
    print(f"\n{'Prefix':<8} {'H %':<10} {'P %':<10} {'T %':<10}")
    print("-" * 40)
    for prefix in PREFIXES:
        if prefix in features:
            f = features[prefix]
            print(f"{prefix:<8} {f['section_H_pct']:<10.1f} {f['section_P_pct']:<10.1f} {f['section_T_pct']:<10.1f}")

    print("\n--- Key Suffix Distribution by Prefix ---")
    print(f"\n{'Prefix':<8} {'-in %':<10} {'-ol %':<10} {'-y %':<10}")
    print("-" * 40)
    for prefix in PREFIXES:
        if prefix in features:
            f = features[prefix]
            print(f"{prefix:<8} {f['in_pct']:<10.1f} {f['ol_pct']:<10.1f} {f['y_pct']:<10.1f}")

    # === Proposed groupings ===
    print("\n--- Proposed Prefix Groups (based on behavior) ---")

    # Group by dominant suffix behavior
    in_heavy = [p for p in PREFIXES if features.get(p, {}).get('in_pct', 0) > 20]
    ol_heavy = [p for p in PREFIXES if features.get(p, {}).get('ol_pct', 0) > 15]
    y_heavy = [p for p in PREFIXES if features.get(p, {}).get('y_pct', 0) > 15]

    print(f"\n'-in' heavy (>20%): {in_heavy}")
    print(f"'-ol' heavy (>15%): {ol_heavy}")
    print(f"'-y' heavy (>15%): {y_heavy}")

if __name__ == '__main__':
    tokens = load_currier_a_tokens()
    decomposed = analyze_da_anomaly(tokens)
    analyze_universal_middles(decomposed)
    analyze_prefix_families(decomposed)
