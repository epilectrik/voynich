"""
Label Category Analysis

Investigates whether pharma label tokens show coherent internal divisions
between jar/root/leaf/flower categories.

Questions:
1. Do jar labels differ morphologically from content labels?
2. Do root labels differ from leaf labels?
3. Do labels cluster by plant part?
4. Does any pattern align with Brunschwig processing distinctions?
"""

import json
import os
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

# Morphology parsing (from project standard)
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk',
    'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po',
    'sa', 'ka', 'ta',
    'al', 'ar', 'or', 'op', 'oe',
]
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

SUFFIXES = ['y', 'dy', 'ey', 'aiin', 'ain', 'oiin', 'iin', 'al', 'ol', 'ar', 'or', 'am', 'om']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)


def parse_prefix(token):
    """Extract prefix from token."""
    token = token.lower().replace('*', '').replace('?', '')
    for p in ALL_PREFIXES:
        if token.startswith(p):
            return p
    return None


def parse_suffix(token):
    """Extract suffix from token."""
    token = token.lower().replace('*', '').replace('?', '')
    for s in ALL_SUFFIXES:
        if token.endswith(s):
            return s
    return None


def extract_middle(token):
    """Extract middle portion after removing prefix and suffix."""
    token = token.lower().replace('*', '').replace('?', '')
    prefix = parse_prefix(token)
    suffix = parse_suffix(token)

    start = len(prefix) if prefix else 0
    end = len(token) - len(suffix) if suffix else len(token)

    if start < end:
        return token[start:end]
    return None


# Load all mapping files
MAPPING_DIR = Path('phases/PHARMA_LABEL_DECODING')

def load_mappings():
    """Load all mapping JSON files and build unified dataset."""
    labels = []

    for json_file in MAPPING_DIR.glob('*_mapping.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        folio = data.get('folio', json_file.stem)
        plant_part = data.get('plant_part', 'unknown')

        # Skip reference pages
        if data.get('classification') == 'reference_page':
            continue

        # Handle different JSON structures
        if 'groups' in data:
            for group in data['groups']:
                # Jar label
                jar = group.get('jar')
                if jar and isinstance(jar, str):
                    labels.append({
                        'token': jar.lower(),
                        'folio': folio,
                        'plant_part': plant_part,
                        'label_type': 'jar'
                    })
                elif jar and isinstance(jar, list):
                    for j in jar:
                        if isinstance(j, str):
                            labels.append({
                                'token': j.lower(),
                                'folio': folio,
                                'plant_part': plant_part,
                                'label_type': 'jar'
                            })

                # Content labels (roots or leaves)
                content_key = 'roots' if 'roots' in group else 'leaves' if 'leaves' in group else 'labels'
                content = group.get(content_key, [])
                for item in content:
                    if isinstance(item, str):
                        token = item
                    elif isinstance(item, dict):
                        token = item.get('token', '')
                    else:
                        continue

                    if token:
                        labels.append({
                            'token': token.lower(),
                            'folio': folio,
                            'plant_part': plant_part,
                            'label_type': 'content'
                        })

        elif 'labels' in data:
            # Flat structure (e.g., f100r, f100v)
            for item in data['labels']:
                if isinstance(item, str):
                    token = item
                elif isinstance(item, dict):
                    token = item.get('token', '')
                else:
                    continue

                if token:
                    labels.append({
                        'token': token.lower(),
                        'folio': folio,
                        'plant_part': plant_part,
                        'label_type': 'content'
                    })

    return labels


def analyze_morphology(labels):
    """Parse morphology for all labels."""
    for label in labels:
        token = label['token']
        label['prefix'] = parse_prefix(token)
        label['suffix'] = parse_suffix(token)
        label['middle'] = extract_middle(token)
        label['length'] = len(token.replace('*', '').replace('?', ''))
    return labels


def compare_distributions(group1, group2, feature, name1, name2):
    """Compare a feature distribution between two groups."""
    dist1 = Counter(item.get(feature) for item in group1 if item.get(feature))
    dist2 = Counter(item.get(feature) for item in group2 if item.get(feature))

    total1 = sum(dist1.values())
    total2 = sum(dist2.values())

    if total1 == 0 or total2 == 0:
        return None

    # Normalize
    norm1 = {k: v/total1 for k, v in dist1.items()}
    norm2 = {k: v/total2 for k, v in dist2.items()}

    # All keys
    all_keys = set(norm1.keys()) | set(norm2.keys())

    # Calculate differences
    diffs = []
    for k in all_keys:
        v1 = norm1.get(k, 0)
        v2 = norm2.get(k, 0)
        diffs.append({
            'value': k,
            f'{name1}_pct': v1,
            f'{name2}_pct': v2,
            'diff': v1 - v2
        })

    diffs.sort(key=lambda x: -abs(x['diff']))

    return {
        'feature': feature,
        f'{name1}_count': total1,
        f'{name2}_count': total2,
        'top_differences': diffs[:10]
    }


def vocabulary_overlap(group1, group2):
    """Calculate vocabulary overlap between groups."""
    vocab1 = set(item['token'] for item in group1)
    vocab2 = set(item['token'] for item in group2)

    shared = vocab1 & vocab2
    union = vocab1 | vocab2

    jaccard = len(shared) / len(union) if union else 0

    return {
        'group1_types': len(vocab1),
        'group2_types': len(vocab2),
        'shared_types': len(shared),
        'shared_tokens': sorted(shared)[:20],
        'jaccard': jaccard
    }


def main():
    print("="*70)
    print("PHARMA LABEL CATEGORY ANALYSIS")
    print("="*70)

    # Step 1: Load data
    print("\n[1] Loading mapping files...")
    labels = load_mappings()
    print(f"    Loaded {len(labels)} labels")

    # Step 2: Parse morphology
    print("\n[2] Parsing morphology...")
    labels = analyze_morphology(labels)

    # Categorize
    jar_labels = [l for l in labels if l['label_type'] == 'jar']
    content_labels = [l for l in labels if l['label_type'] == 'content']
    root_labels = [l for l in labels if l['plant_part'] == 'root']
    leaf_labels = [l for l in labels if l['plant_part'] == 'leaf']

    print(f"    Jar labels: {len(jar_labels)}")
    print(f"    Content labels: {len(content_labels)}")
    print(f"    Root labels: {len(root_labels)}")
    print(f"    Leaf labels: {len(leaf_labels)}")

    results = {
        'summary': {
            'total_labels': len(labels),
            'jar_labels': len(jar_labels),
            'content_labels': len(content_labels),
            'root_labels': len(root_labels),
            'leaf_labels': len(leaf_labels)
        }
    }

    # =========================================================================
    # Q1: Jar vs Content Labels
    # =========================================================================
    print("\n" + "="*70)
    print("Q1: JAR vs CONTENT LABELS")
    print("="*70)

    if jar_labels and content_labels:
        # PREFIX comparison
        prefix_comp = compare_distributions(jar_labels, content_labels, 'prefix', 'jar', 'content')
        print(f"\nPREFIX distribution:")
        print(f"  Jar: {prefix_comp['jar_count']} tokens with prefixes")
        print(f"  Content: {prefix_comp['content_count']} tokens with prefixes")
        print(f"  Top differences:")
        for d in prefix_comp['top_differences'][:5]:
            print(f"    {d['value']}: jar={d['jar_pct']:.1%}, content={d['content_pct']:.1%}, diff={d['diff']:+.1%}")

        # SUFFIX comparison
        suffix_comp = compare_distributions(jar_labels, content_labels, 'suffix', 'jar', 'content')
        print(f"\nSUFFIX distribution:")
        for d in suffix_comp['top_differences'][:5]:
            print(f"    {d['value']}: jar={d['jar_pct']:.1%}, content={d['content_pct']:.1%}, diff={d['diff']:+.1%}")

        # Length comparison
        jar_lengths = [l['length'] for l in jar_labels]
        content_lengths = [l['length'] for l in content_labels]
        print(f"\nTOKEN LENGTH:")
        print(f"  Jar: mean={np.mean(jar_lengths):.1f}, median={np.median(jar_lengths):.0f}")
        print(f"  Content: mean={np.mean(content_lengths):.1f}, median={np.median(content_lengths):.0f}")

        # Vocabulary overlap
        vocab_overlap = vocabulary_overlap(jar_labels, content_labels)
        print(f"\nVOCABULARY OVERLAP:")
        print(f"  Jar types: {vocab_overlap['group1_types']}")
        print(f"  Content types: {vocab_overlap['group2_types']}")
        print(f"  Shared: {vocab_overlap['shared_types']} (Jaccard={vocab_overlap['jaccard']:.3f})")
        if vocab_overlap['shared_tokens']:
            print(f"  Shared tokens: {vocab_overlap['shared_tokens']}")

        results['jar_vs_content'] = {
            'prefix': prefix_comp,
            'suffix': suffix_comp,
            'length': {
                'jar_mean': float(np.mean(jar_lengths)),
                'content_mean': float(np.mean(content_lengths))
            },
            'vocabulary': vocab_overlap
        }

    # =========================================================================
    # Q2: Root vs Leaf Labels
    # =========================================================================
    print("\n" + "="*70)
    print("Q2: ROOT vs LEAF LABELS")
    print("="*70)

    if root_labels and leaf_labels:
        # PREFIX comparison
        prefix_comp = compare_distributions(root_labels, leaf_labels, 'prefix', 'root', 'leaf')
        print(f"\nPREFIX distribution:")
        print(f"  Root: {prefix_comp['root_count']} tokens with prefixes")
        print(f"  Leaf: {prefix_comp['leaf_count']} tokens with prefixes")
        print(f"  Top differences:")
        for d in prefix_comp['top_differences'][:8]:
            print(f"    {d['value']}: root={d['root_pct']:.1%}, leaf={d['leaf_pct']:.1%}, diff={d['diff']:+.1%}")

        # SUFFIX comparison
        suffix_comp = compare_distributions(root_labels, leaf_labels, 'suffix', 'root', 'leaf')
        print(f"\nSUFFIX distribution:")
        for d in suffix_comp['top_differences'][:5]:
            print(f"    {d['value']}: root={d['root_pct']:.1%}, leaf={d['leaf_pct']:.1%}, diff={d['diff']:+.1%}")

        # Length comparison
        root_lengths = [l['length'] for l in root_labels]
        leaf_lengths = [l['length'] for l in leaf_labels]
        print(f"\nTOKEN LENGTH:")
        print(f"  Root: mean={np.mean(root_lengths):.1f}, median={np.median(root_lengths):.0f}")
        print(f"  Leaf: mean={np.mean(leaf_lengths):.1f}, median={np.median(leaf_lengths):.0f}")

        # Vocabulary overlap
        vocab_overlap = vocabulary_overlap(root_labels, leaf_labels)
        print(f"\nVOCABULARY OVERLAP:")
        print(f"  Root types: {vocab_overlap['group1_types']}")
        print(f"  Leaf types: {vocab_overlap['group2_types']}")
        print(f"  Shared: {vocab_overlap['shared_types']} (Jaccard={vocab_overlap['jaccard']:.3f})")
        if vocab_overlap['shared_tokens']:
            print(f"  Shared tokens: {vocab_overlap['shared_tokens'][:10]}")

        results['root_vs_leaf'] = {
            'prefix': prefix_comp,
            'suffix': suffix_comp,
            'length': {
                'root_mean': float(np.mean(root_lengths)),
                'leaf_mean': float(np.mean(leaf_lengths))
            },
            'vocabulary': vocab_overlap
        }

    # =========================================================================
    # Q3: Clustering Analysis
    # =========================================================================
    print("\n" + "="*70)
    print("Q3: PREFIX CLUSTERING BY PLANT PART")
    print("="*70)

    # Check if certain prefixes are strongly associated with plant parts
    prefix_by_part = defaultdict(lambda: {'root': 0, 'leaf': 0})
    for l in labels:
        if l['prefix'] and l['plant_part'] in ['root', 'leaf']:
            prefix_by_part[l['prefix']][l['plant_part']] += 1

    print("\nPrefix associations (count >= 3):")
    print(f"{'PREFIX':<10} {'ROOT':<8} {'LEAF':<8} {'RATIO':<10} {'LEAN'}")
    print("-" * 50)

    prefix_associations = []
    for prefix, counts in sorted(prefix_by_part.items()):
        total = counts['root'] + counts['leaf']
        if total >= 3:
            root_ratio = counts['root'] / total
            leaf_ratio = counts['leaf'] / total
            lean = 'ROOT' if root_ratio > 0.6 else 'LEAF' if leaf_ratio > 0.6 else 'MIXED'
            print(f"{prefix:<10} {counts['root']:<8} {counts['leaf']:<8} {root_ratio:.0%}/{leaf_ratio:.0%}   {lean}")
            prefix_associations.append({
                'prefix': prefix,
                'root': counts['root'],
                'leaf': counts['leaf'],
                'root_ratio': root_ratio,
                'lean': lean
            })

    results['prefix_associations'] = prefix_associations

    # =========================================================================
    # Q4: Brunschwig Alignment
    # =========================================================================
    print("\n" + "="*70)
    print("Q4: BRUNSCHWIG ALIGNMENT")
    print("="*70)
    print("\nBrunschwig context:")
    print("  - Roots: aggressive extraction, higher heat")
    print("  - Leaves/flowers: gentler processing")

    # Check "intense" vs "gentle" prefix patterns (from earlier analysis)
    intense_prefixes = ['ok', 'ot', 'ko', 'to']
    gentle_prefixes = ['ch', 'sh', 'qo']

    root_intense = sum(1 for l in root_labels if l['prefix'] in intense_prefixes)
    root_gentle = sum(1 for l in root_labels if l['prefix'] in gentle_prefixes)
    leaf_intense = sum(1 for l in leaf_labels if l['prefix'] in intense_prefixes)
    leaf_gentle = sum(1 for l in leaf_labels if l['prefix'] in gentle_prefixes)

    root_total = len(root_labels)
    leaf_total = len(leaf_labels)

    print(f"\n'Intense' prefixes {intense_prefixes}:")
    print(f"  Root: {root_intense}/{root_total} = {root_intense/root_total:.1%}")
    print(f"  Leaf: {leaf_intense}/{leaf_total} = {leaf_intense/leaf_total:.1%}")

    print(f"\n'Gentle' prefixes {gentle_prefixes}:")
    print(f"  Root: {root_gentle}/{root_total} = {root_gentle/root_total:.1%}")
    print(f"  Leaf: {leaf_gentle}/{leaf_total} = {leaf_gentle/leaf_total:.1%}")

    intense_diff = (root_intense/root_total) - (leaf_intense/leaf_total)
    gentle_diff = (root_gentle/root_total) - (leaf_gentle/leaf_total)

    print(f"\nDifference (root - leaf):")
    print(f"  Intense: {intense_diff:+.1%}")
    print(f"  Gentle: {gentle_diff:+.1%}")

    if intense_diff > 0.05 and gentle_diff < -0.05:
        print("\n  --> MATCHES Brunschwig: roots more intense, leaves more gentle")
    else:
        print("\n  --> NO CLEAR Brunschwig alignment in prefix patterns")

    results['brunschwig'] = {
        'intense_prefixes': intense_prefixes,
        'gentle_prefixes': gentle_prefixes,
        'root_intense_pct': root_intense/root_total,
        'leaf_intense_pct': leaf_intense/leaf_total,
        'root_gentle_pct': root_gentle/root_total,
        'leaf_gentle_pct': leaf_gentle/leaf_total,
        'alignment': intense_diff > 0.05 and gentle_diff < -0.05
    }

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print(f"""
FINDINGS:

1. JAR vs CONTENT:
   - Jar labels: {len(jar_labels)} tokens
   - Content labels: {len(content_labels)} tokens
   - Vocabulary overlap: Jaccard={results.get('jar_vs_content', {}).get('vocabulary', {}).get('jaccard', 0):.3f}

2. ROOT vs LEAF:
   - Root labels: {len(root_labels)} tokens
   - Leaf labels: {len(leaf_labels)} tokens
   - Vocabulary overlap: Jaccard={results.get('root_vs_leaf', {}).get('vocabulary', {}).get('jaccard', 0):.3f}

3. PREFIX CLUSTERING:
   - Prefixes with strong plant-part lean: {sum(1 for p in prefix_associations if p['lean'] != 'MIXED')}
   - Mixed prefixes: {sum(1 for p in prefix_associations if p['lean'] == 'MIXED')}

4. BRUNSCHWIG ALIGNMENT:
   - Root intense vs leaf intense: {intense_diff:+.1%}
   - {'MATCHES' if results['brunschwig']['alignment'] else 'NO CLEAR MATCH'}
""")

    # Save results
    results_path = MAPPING_DIR / 'label_category_results.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {results_path}")


if __name__ == '__main__':
    main()
