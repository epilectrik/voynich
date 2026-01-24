"""
Prep State Triangulation Test

Tests whether different prep states/plant parts of the same base material
map to different MIDDLEs in Currier A.

Materials tested:
1. Borage (herb vs flower) - different fire degrees + different preps
2. Elder (bark vs leaves vs flowers) - 3 variants
3. Birch (leaf vs sap) - same fire, totally different preps
"""
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Morphology extraction
PREFIXES = ['qok', 'qo', 'ok', 'ot', 'ch', 'sh', 'ck', 'ct', 'cth', 'yk', 'yt',
            'dch', 'kch', 'pch', 'tch', 'fch', 'da', 'sa', 'ol', 'al',
            's', 'k', 'd', 'l', 'r', 'y', 'p', 't', 'f']

SUFFIXES = ['aiin', 'ain', 'iin', 'in', 'ol', 'al', 'or', 'ar', 'dy', 'chy',
            'ky', 'ty', 'edy', 'ody', 'y', 'o', 'l', 'n', 'r', 'd', 'g', 'm', 's']


def extract_morphology(token):
    """Extract PREFIX, MIDDLE, SUFFIX from token."""
    if not token or token == '*':
        return '', '', ''

    # Try prefixes (longest match first)
    prefix = ''
    remainder = token
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p) and len(token) > len(p):
            prefix = p
            remainder = token[len(p):]
            break

    # Try suffixes (longest match first)
    suffix = ''
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            remainder = remainder[:-len(s)]
            break

    middle = remainder
    return prefix, middle, suffix


# Load data
print("Loading Voynich transcript...")
data_path = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

with open(data_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        # Filter to PRIMARY transcriber (H) only
        transcriber = row.get('transcriber', '').strip().strip('"')
        if transcriber != 'H':
            continue

        # Extract morphology
        word = row.get('word', '')
        prefix, middle, suffix = extract_morphology(word)
        row['prefix'] = prefix
        row['middle'] = middle
        row['suffix'] = suffix

        all_tokens.append(row)

# Separate by Currier language
a_tokens = [t for t in all_tokens if t.get('language', '') == 'A']
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']

print(f"Loaded {len(a_tokens)} A tokens, {len(b_tokens)} B tokens (H-track only)")

# Get vocabulary sets
a_middles = set(t['middle'] for t in a_tokens if t['middle'])
b_middles = set(t['middle'] for t in b_tokens if t['middle'])
shared_middles = a_middles & b_middles
a_only_middles = a_middles - b_middles  # RI vocabulary

print(f"Vocabulary: {len(a_middles)} A middles, {len(b_middles)} B middles")
print(f"Shared (PP): {len(shared_middles)}, A-only (RI): {len(a_only_middles)}")

# Compute B folio statistics
print("\nComputing B folio PREFIX profiles...")
b_folio_tokens = defaultdict(list)
for t in b_tokens:
    folio = t.get('folio', '')
    if folio:
        b_folio_tokens[folio].append(t)

b_folio_stats = {}
for folio, tokens in b_folio_tokens.items():
    total = len(tokens)
    prefix_counts = Counter(t['prefix'] for t in tokens)
    b_folio_stats[folio] = {
        'total': total,
        'qo_ratio': prefix_counts.get('qo', 0) / total if total > 0 else 0,
        'ok_ratio': prefix_counts.get('ok', 0) / total if total > 0 else 0,
        'ot_ratio': prefix_counts.get('ot', 0) / total if total > 0 else 0,
        'da_ratio': prefix_counts.get('da', 0) / total if total > 0 else 0,
        'ch_ratio': prefix_counts.get('ch', 0) / total if total > 0 else 0,
        'sh_ratio': prefix_counts.get('sh', 0) / total if total > 0 else 0,
        'aux_ratio': (prefix_counts.get('ok', 0) + prefix_counts.get('ot', 0)) / total if total > 0 else 0,
    }

# Compute average ratios
avg_qo = np.mean([s['qo_ratio'] for s in b_folio_stats.values()])
avg_aux = np.mean([s['aux_ratio'] for s in b_folio_stats.values()])
avg_da = np.mean([s['da_ratio'] for s in b_folio_stats.values()])
print(f"Average ratios - qo: {avg_qo:.3f}, aux: {avg_aux:.3f}, da: {avg_da:.3f}")

# Fire degree to REGIME mapping
FIRE_TO_REGIME = {
    1: 'REGIME_2',  # Gentle
    2: 'REGIME_1',  # Standard
    3: 'REGIME_3',  # Intense
    4: 'REGIME_4',  # Precision
}

# Infrastructure to exclude
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '', 'i'}

# Define test materials
TEST_MATERIALS = {
    'borage': [
        {'id': 16, 'name': 'borage herb', 'fire': 2, 'preps': ['GATHER', 'CHOP', 'POUND', 'DISTILL']},
        {'id': 17, 'name': 'borage flower', 'fire': 1, 'preps': ['GATHER', 'BREAK', 'CHOP', 'DISTILL']},
    ],
    'elder': [
        {'id': 86, 'name': 'elder bark', 'fire': 1, 'preps': ['STRIP', 'STRIP', 'DISTILL']},
        {'id': 87, 'name': 'elder leaves', 'fire': 2, 'preps': ['GATHER', 'CHOP', 'DISTILL']},
        {'id': 88, 'name': 'elder flowers', 'fire': 2, 'preps': ['STRIP', 'DISTILL']},
    ],
    'birch': [
        {'id': 22, 'name': 'birch leaf', 'fire': 2, 'preps': ['GATHER', 'CHOP', 'POUND', 'DISTILL']},
        {'id': 23, 'name': 'birch sap', 'fire': 2, 'preps': ['BORE', 'COLLECT', 'DISTILL']},
    ],
}


def get_candidate_folios(fire_degree, preps):
    """Get candidate B folios based on fire degree and prep sequence."""
    # Filter by PREFIX profile expectations
    has_escape = 'DISTILL' in preps or 'REDISTILL' in preps
    has_aux = any(p in preps for p in ['CHOP', 'POUND', 'STRIP', 'WASH', 'CLEAN', 'BREAK'])
    has_flow = any(p in preps for p in ['COLLECT', 'GATHER', 'BORE'])

    candidates = set()
    for folio, stats in b_folio_stats.items():
        score = 0
        if has_escape and stats['qo_ratio'] >= avg_qo * 0.7:
            score += 1
        if has_aux and stats['aux_ratio'] >= avg_aux * 0.7:
            score += 1
        if has_flow and stats['da_ratio'] >= avg_da * 0.7:
            score += 1

        if score >= 1:
            candidates.add(folio)

    return candidates if candidates else set(b_folio_stats.keys())


def get_discriminative_pp(folios):
    """Get discriminative PP vocabulary from candidate folios."""
    candidate_middles = set()
    for folio in folios:
        for t in b_folio_tokens.get(folio, []):
            if t['middle']:
                candidate_middles.add(t['middle'])

    discriminative_pp = (candidate_middles & shared_middles) - infrastructure
    return discriminative_pp


def find_converging_a_records(discriminative_pp, min_overlap=2):
    """Find A records with multiple PP convergence."""
    # Group A tokens by record (folio:line)
    a_records = defaultdict(lambda: {'middles': set(), 'suffixes': [], 'words': []})

    for t in a_tokens:
        folio = t.get('folio', '')
        line = t.get('line_number', '')
        key = f"{folio}:{line}"

        if t['middle']:
            a_records[key]['middles'].add(t['middle'])
        if t['suffix']:
            a_records[key]['suffixes'].append(t['suffix'])
        if t.get('word'):
            a_records[key]['words'].append(t.get('word'))

    # Calculate PP overlap and filter
    converging = []
    for key, record in a_records.items():
        pp_overlap = len(record['middles'] & discriminative_pp)
        if pp_overlap >= min_overlap:
            ri_tokens = record['middles'] & a_only_middles
            converging.append({
                'key': key,
                'middles': record['middles'],
                'pp_overlap': pp_overlap,
                'ri_tokens': ri_tokens,
                'suffixes': record['suffixes'],
                'words': record['words'],
            })

    return converging


def analyze_material(material_info):
    """Run triangulation for a single material variant."""
    print(f"\n  Analyzing: {material_info['name']} (fire={material_info['fire']})")
    print(f"    Preps: {' -> '.join(material_info['preps'])}")

    # Step 1: Get candidate B folios
    candidates = get_candidate_folios(material_info['fire'], material_info['preps'])
    print(f"    Candidate B folios: {len(candidates)}")

    # Step 2: Get discriminative PP
    disc_pp = get_discriminative_pp(candidates)
    print(f"    Discriminative PP: {len(disc_pp)}")

    # Step 3: Find converging A records
    converging = find_converging_a_records(disc_pp, min_overlap=2)
    print(f"    Converging A records (>=2 PP): {len(converging)}")

    # Collect all MIDDLEs from converging records
    all_middles = set()
    all_ri = set()
    all_pp = set()
    suffix_present = 0
    suffix_absent = 0

    for record in converging:
        all_middles.update(record['middles'])
        all_ri.update(record['ri_tokens'])
        all_pp.update(record['middles'] & shared_middles)

        if record['suffixes']:
            suffix_present += 1
        else:
            suffix_absent += 1

    result = {
        'name': material_info['name'],
        'fire': material_info['fire'],
        'regime': FIRE_TO_REGIME.get(material_info['fire'], 'REGIME_1'),
        'preps': material_info['preps'],
        'n_candidate_folios': len(candidates),
        'n_disc_pp': len(disc_pp),
        'n_converging_records': len(converging),
        'all_middles': all_middles,
        'ri_tokens': all_ri,
        'pp_tokens': all_pp - infrastructure,
        'suffix_present': suffix_present,
        'suffix_absent': suffix_absent,
    }

    print(f"    Total MIDDLEs: {len(all_middles)}, RI: {len(all_ri)}, PP: {len(result['pp_tokens'])}")
    print(f"    Suffix presence: {suffix_present} with, {suffix_absent} without")

    return result


# Run analysis
print("\n" + "=" * 70)
print("PREP STATE TRIANGULATION ANALYSIS")
print("=" * 70)

results = {}
for family, variants in TEST_MATERIALS.items():
    print(f"\n{'='*70}")
    print(f"FAMILY: {family.upper()}")
    print("=" * 70)

    family_results = []
    for variant in variants:
        result = analyze_material(variant)
        family_results.append(result)

    results[family] = family_results

# Compare MIDDLEs within families
print("\n" + "=" * 70)
print("MIDDLE COMPARISON ACROSS PREP VARIANTS")
print("=" * 70)

for family, variants in results.items():
    print(f"\n--- {family.upper()} ---")

    if len(variants) < 2:
        print("  Insufficient variants for comparison")
        continue

    variant_middles = {v['name']: v['all_middles'] for v in variants}
    variant_ri = {v['name']: v['ri_tokens'] for v in variants}

    all_names = list(variant_middles.keys())

    for i, name1 in enumerate(all_names):
        for name2 in all_names[i+1:]:
            m1, m2 = variant_middles[name1], variant_middles[name2]
            shared = m1 & m2
            only1 = m1 - m2
            only2 = m2 - m1

            jaccard = len(shared) / len(m1 | m2) if (m1 | m2) else 0

            print(f"\n  {name1} vs {name2}:")
            print(f"    Shared MIDDLEs: {len(shared)}")
            print(f"    Only in {name1}: {len(only1)}")
            print(f"    Only in {name2}: {len(only2)}")
            print(f"    Jaccard similarity: {jaccard:.3f}")

            ri1, ri2 = variant_ri[name1], variant_ri[name2]
            ri_shared = ri1 & ri2
            ri_only1 = ri1 - ri2
            ri_only2 = ri2 - ri1

            print(f"    RI shared: {len(ri_shared)}, only-{name1}: {len(ri_only1)}, only-{name2}: {len(ri_only2)}")

            if ri_only1:
                print(f"      {name1} unique RI: {sorted(ri_only1)[:10]}...")
            if ri_only2:
                print(f"      {name2} unique RI: {sorted(ri_only2)[:10]}...")

# Summary
print("\n" + "=" * 70)
print("SUMMARY: PREP STATE ENCODING EVIDENCE")
print("=" * 70)

for family, variants in results.items():
    print(f"\n{family.upper()}:")

    # Check same REGIME but different preps
    regime_groups = defaultdict(list)
    for v in variants:
        regime_groups[v['regime']].append(v)

    for regime, group in regime_groups.items():
        if len(group) >= 2:
            print(f"  Same REGIME ({regime}), different preps:")
            names = [g['name'] for g in group]
            middles = [g['all_middles'] for g in group]

            shared = middles[0]
            for m in middles[1:]:
                shared = shared & m

            total_unique = set()
            for m in middles:
                total_unique.update(m)

            differentiation = 1 - (len(shared) / len(total_unique)) if total_unique else 0
            print(f"    Variants: {names}")
            print(f"    MIDDLE differentiation: {differentiation:.1%}")

# Key test: Birch
print("\n" + "=" * 70)
print("KEY TEST: BIRCH (same REGIME, different preps)")
print("=" * 70)

birch_results = results.get('birch', [])
if len(birch_results) >= 2:
    leaf = next((v for v in birch_results if 'leaf' in v['name']), None)
    sap = next((v for v in birch_results if 'sap' in v['name']), None)

    if leaf and sap:
        shared = leaf['all_middles'] & sap['all_middles']
        leaf_only = leaf['all_middles'] - sap['all_middles']
        sap_only = sap['all_middles'] - leaf['all_middles']

        total = len(leaf['all_middles'] | sap['all_middles'])
        diff_rate = (len(leaf_only) + len(sap_only)) / total if total else 0

        print(f"\nBirch leaf MIDDLEs: {len(leaf['all_middles'])}")
        print(f"Birch sap MIDDLEs: {len(sap['all_middles'])}")
        print(f"Shared: {len(shared)}")
        print(f"Leaf-only: {len(leaf_only)}")
        print(f"Sap-only: {len(sap_only)}")
        print(f"Differentiation rate: {diff_rate:.1%}")

        # Show some unique MIDDLEs
        if leaf_only:
            print(f"\nLeaf-unique MIDDLEs (sample): {sorted(leaf_only)[:15]}")
        if sap_only:
            print(f"Sap-unique MIDDLEs (sample): {sorted(sap_only)[:15]}")

        # Verdict
        print("\n" + "-" * 40)
        if diff_rate > 0.3:
            print(f">>> EVIDENCE FOR PREP STATE ENCODING")
            print(f"    Same base material, same fire degree")
            print(f"    But {diff_rate:.0%} MIDDLE differentiation")
        elif diff_rate > 0.1:
            print(f">>> WEAK EVIDENCE - {diff_rate:.0%} differentiation")
        else:
            print(f">>> NO EVIDENCE - Only {diff_rate:.0%} differentiation")
            print(f"    Prep state may NOT be encoded in MIDDLE")

# Save results
output = {
    'test_materials': TEST_MATERIALS,
    'results': {
        family: [
            {
                'name': v['name'],
                'fire': v['fire'],
                'regime': v['regime'],
                'preps': v['preps'],
                'n_middles': len(v['all_middles']),
                'n_ri': len(v['ri_tokens']),
                'n_pp': len(v['pp_tokens']),
                'middles': sorted(list(v['all_middles'])),
                'ri_tokens': sorted(list(v['ri_tokens'])),
                'suffix_present': v['suffix_present'],
                'suffix_absent': v['suffix_absent'],
            }
            for v in variants
        ]
        for family, variants in results.items()
    },
}

output_path = PROJECT_ROOT / 'phases' / 'PREP_POSTURE_DIVERGENCE' / 'results' / 'prep_state_triangulation.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: {output_path}")
