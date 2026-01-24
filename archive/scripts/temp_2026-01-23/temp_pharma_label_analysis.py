#!/usr/bin/env python3
"""
Analyze pharma labels using our new understanding of PP atoms and compression.

Questions:
1. What PP atoms appear in the plant labels?
2. Do jar labels and content labels share PP atoms?
3. Is there a compression/compatibility pattern?
"""

import json
import sys
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent

def extract_middle(token):
    """Extract MIDDLE from token using standard morphology."""
    # Standard prefixes and suffixes
    prefixes = ['qok', 'qot', 'cph', 'cth', 'pch', 'tch', 'ckh', 'qo', 'ch', 'sh',
                'ok', 'ot', 'op', 'ol', 'or', 'da', 'sa', 'so', 'ct', 'yk', 'do',
                'ar', 'po', 'oe', 'os', 'oe', 'al']
    suffixes = ['aiin', 'oiin', 'iin', 'ain', 'dy', 'hy', 'ky', 'ly', 'my', 'ny',
                'ry', 'sy', 'ty', 'am', 'an', 'al', 'ar', 'ol', 'or', 'y', 's',
                'g', 'd', 'l', 'r', 'n', 'm']

    middle = str(token).strip()

    # Strip prefix
    for p in sorted(prefixes, key=len, reverse=True):
        if middle.startswith(p) and len(middle) > len(p):
            middle = middle[len(p):]
            break

    # Strip suffix
    for s in sorted(suffixes, key=len, reverse=True):
        if middle.endswith(s) and len(middle) > len(s):
            middle = middle[:-len(s)]
            break

    return middle if middle and middle != token else None

def load_pp_middles():
    """Extract PP MIDDLEs from transcript - shared between A and B."""
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    df = df[~df['placement'].str.startswith('L', na=False)]

    # Get A and B tokens
    a_tokens = set(df[df['language'] == 'A']['word'].dropna().unique())
    b_tokens = set(df[df['language'] == 'B']['word'].dropna().unique())

    # PP = shared tokens
    pp_tokens = a_tokens & b_tokens

    # Extract MIDDLEs from PP tokens
    pp_middles = set()
    for token in pp_tokens:
        mid = extract_middle(token)
        if mid and len(mid) >= 1:
            pp_middles.add(mid)

    return pp_middles

# Load all pharma label files
def load_pharma_labels():
    """Load all jar and content labels from mapping files."""
    pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'

    jars = []
    roots = []
    leaves = []

    for json_file in pharma_dir.glob('*_mapping.json'):
        with open(json_file) as f:
            data = json.load(f)

        plant_part = data.get('plant_part', 'unknown')
        folio = data.get('folio', json_file.stem)

        # Extract jar labels
        if 'groups' in data:
            for group in data['groups']:
                jar = group.get('jar')
                if jar and isinstance(jar, str):
                    jars.append({'token': jar, 'folio': folio})

                # Extract content labels
                content_labels = group.get('roots', group.get('leaves', group.get('labels', [])))
                for label in content_labels:
                    if isinstance(label, dict):
                        token = label.get('token', '')
                    else:
                        token = label

                    if token and isinstance(token, str) and '*' not in token:
                        if plant_part == 'root':
                            roots.append({'token': token, 'folio': folio})
                        elif plant_part == 'leaf':
                            leaves.append({'token': token, 'folio': folio})
                        else:
                            roots.append({'token': token, 'folio': folio})  # default

        # Handle flat label lists
        if 'labels' in data and 'groups' not in data:
            for label in data['labels']:
                if isinstance(label, dict):
                    token = label.get('token', '')
                else:
                    token = label
                if token and isinstance(token, str) and '*' not in token:
                    if plant_part == 'root':
                        roots.append({'token': token, 'folio': folio})
                    else:
                        leaves.append({'token': token, 'folio': folio})

    return jars, roots, leaves

def find_pp_atoms_in_token(token, pp_middles):
    """Find all PP atoms that appear as substrings in a token."""
    found = []
    for pp in pp_middles:
        if pp in token:
            found.append(pp)
    return found

def find_overlapping_pp(token, pp_middles):
    """Find PP atoms that share characters (compression hinges)."""
    found = find_pp_atoms_in_token(token, pp_middles)
    if len(found) < 2:
        return []

    overlaps = []
    for i, pp1 in enumerate(found):
        for pp2 in found[i+1:]:
            # Check if they share a hinge
            for hinge_len in [1, 2]:
                if pp1[-hinge_len:] == pp2[:hinge_len]:
                    overlaps.append((pp1, pp2, pp1[-hinge_len:]))
                if pp2[-hinge_len:] == pp1[:hinge_len]:
                    overlaps.append((pp2, pp1, pp2[-hinge_len:]))
    return overlaps

if __name__ == '__main__':
    print("=" * 70)
    print("PHARMA LABEL ANALYSIS WITH PP ATOMS")
    print("=" * 70)

    # Load data
    pp_middles = load_pp_middles()
    print(f"\nLoaded {len(pp_middles)} PP MIDDLEs")

    jars, roots, leaves = load_pharma_labels()
    print(f"Loaded: {len(jars)} jar labels, {len(roots)} root labels, {len(leaves)} leaf labels")

    # Get unique tokens
    jar_tokens = list(set(j['token'] for j in jars))
    root_tokens = list(set(r['token'] for r in roots))
    leaf_tokens = list(set(l['token'] for l in leaves))

    print(f"\nUnique: {len(jar_tokens)} jars, {len(root_tokens)} roots, {len(leaf_tokens)} leaves")

    # Analyze PP atoms in each category
    print("\n" + "=" * 70)
    print("PP ATOM ANALYSIS")
    print("=" * 70)

    def analyze_category(tokens, name):
        pp_counts = Counter()
        tokens_with_pp = 0
        pp_per_token = []

        for token in tokens:
            found = find_pp_atoms_in_token(token, pp_middles)
            pp_per_token.append(len(found))
            if found:
                tokens_with_pp += 1
                for pp in found:
                    pp_counts[pp] += 1

        print(f"\n--- {name.upper()} ({len(tokens)} tokens) ---")
        print(f"Tokens with PP atoms: {tokens_with_pp} ({100*tokens_with_pp/len(tokens):.1f}%)")
        print(f"Mean PP atoms per token: {sum(pp_per_token)/len(pp_per_token):.2f}")
        print(f"Max PP atoms in single token: {max(pp_per_token)}")
        print(f"Unique PP atoms used: {len(pp_counts)}")
        print(f"\nTop 10 PP atoms:")
        for pp, count in pp_counts.most_common(10):
            print(f"  '{pp}': {count}")

        return pp_counts

    jar_pp = analyze_category(jar_tokens, "JARS")
    root_pp = analyze_category(root_tokens, "ROOTS")
    leaf_pp = analyze_category(leaf_tokens, "LEAVES")

    # Compare PP usage across categories
    print("\n" + "=" * 70)
    print("PP ATOM OVERLAP BETWEEN CATEGORIES")
    print("=" * 70)

    jar_pp_set = set(jar_pp.keys())
    root_pp_set = set(root_pp.keys())
    leaf_pp_set = set(leaf_pp.keys())

    def jaccard(a, b):
        if not a or not b:
            return 0
        return len(a & b) / len(a | b)

    print(f"\nJar-Root PP overlap: {len(jar_pp_set & root_pp_set)} atoms (Jaccard: {jaccard(jar_pp_set, root_pp_set):.3f})")
    print(f"Jar-Leaf PP overlap: {len(jar_pp_set & leaf_pp_set)} atoms (Jaccard: {jaccard(jar_pp_set, leaf_pp_set):.3f})")
    print(f"Root-Leaf PP overlap: {len(root_pp_set & leaf_pp_set)} atoms (Jaccard: {jaccard(root_pp_set, leaf_pp_set):.3f})")

    print(f"\nPP atoms unique to jars: {jar_pp_set - root_pp_set - leaf_pp_set}")
    print(f"PP atoms unique to roots: {root_pp_set - jar_pp_set - leaf_pp_set}")
    print(f"PP atoms unique to leaves: {leaf_pp_set - jar_pp_set - root_pp_set}")

    print(f"\nPP atoms shared by ALL: {jar_pp_set & root_pp_set & leaf_pp_set}")

    # Compression analysis
    print("\n" + "=" * 70)
    print("COMPRESSION PATTERNS (OVERLAPPING PP ATOMS)")
    print("=" * 70)

    def show_compression(tokens, name, limit=5):
        print(f"\n--- {name} ---")
        examples = []
        for token in tokens[:30]:  # Check first 30
            overlaps = find_overlapping_pp(token, pp_middles)
            if overlaps:
                examples.append((token, overlaps))

        print(f"Tokens with PP overlap compression: {len(examples)}/{min(30, len(tokens))}")
        for token, overlaps in examples[:limit]:
            print(f"  '{token}':")
            for pp1, pp2, hinge in overlaps:
                print(f"    {pp1} + {pp2} via hinge '{hinge}'")

    show_compression(jar_tokens, "JARS")
    show_compression(root_tokens, "ROOTS")
    show_compression(leaf_tokens, "LEAVES")

    # Extract MIDDLEs and look at patterns
    print("\n" + "=" * 70)
    print("MIDDLE EXTRACTION AND PATTERNS")
    print("=" * 70)

    def show_middles(tokens, name):
        middles = Counter()
        for token in tokens:
            mid = extract_middle(token)
            if mid:
                middles[mid] += 1

        print(f"\n--- {name} MIDDLEs ---")
        print(f"Unique MIDDLEs: {len(middles)}")
        print(f"Top 15:")
        for mid, count in middles.most_common(15):
            pp_in_mid = find_pp_atoms_in_token(mid, pp_middles)
            pp_str = f" [PP: {', '.join(pp_in_mid)}]" if pp_in_mid else ""
            print(f"  '{mid}': {count}{pp_str}")

        return middles

    jar_middles = show_middles(jar_tokens, "JAR")
    root_middles = show_middles(root_tokens, "ROOT")
    leaf_middles = show_middles(leaf_tokens, "LEAF")

    # Look at specific folios the user mentioned
    print("\n" + "=" * 70)
    print("F88V / F89R1 / F89R2 SPECIFIC ANALYSIS")
    print("=" * 70)

    target_folios = ['f88v', 'f89r1', 'f89r2']

    for folio in target_folios:
        folio_roots = [r['token'] for r in roots if r['folio'] == folio]
        folio_jars = [j['token'] for j in jars if j['folio'] == folio]

        print(f"\n--- {folio.upper()} ---")
        if folio_jars:
            print(f"Jar labels: {folio_jars}")
        print(f"Plant labels ({len(folio_roots)}):")

        # Group by prefix
        by_prefix = defaultdict(list)
        for token in folio_roots:
            prefix = token[:2] if len(token) >= 2 else token
            by_prefix[prefix].append(token)

        for prefix in sorted(by_prefix.keys()):
            tokens = by_prefix[prefix]
            print(f"  {prefix}-: {tokens}")

        # Check PP atoms used
        all_pp = set()
        for token in folio_roots:
            all_pp.update(find_pp_atoms_in_token(token, pp_middles))

        print(f"  PP atoms used: {sorted(all_pp)}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
Key observations:
1. PP atom usage shows whether labels use the shared vocabulary (B-compatible)
2. Compression patterns reveal morphological structure
3. MIDDLE extraction shows the discriminator layer
4. Comparing PP overlap between jars and contents tests if they share compatibility
""")
