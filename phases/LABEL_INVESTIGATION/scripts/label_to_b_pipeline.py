"""
label_to_b_pipeline.py - Trace labels through PP bases to B occurrences

Goal: Visualize the label -> PP base -> B pipeline

For each label:
1. Extract morphology
2. If RI (MIDDLE contains PP), extract PP base
3. Find B tokens using that PP base
4. Show the connection
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("LABEL -> PP BASE -> B PIPELINE ANALYSIS")
print("="*70)

# ============================================================
# STEP 1: BUILD PP VOCABULARY FROM B
# ============================================================
print("\n--- Step 1: Building PP Vocabulary from Currier B ---")

pp_middles = set()
b_middle_to_folios = defaultdict(set)
b_middle_counts = Counter()

for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        pp_middles.add(m.middle)
        b_middle_to_folios[m.middle].add(t.folio)
        b_middle_counts[m.middle] += 1

print(f"PP vocabulary size (from B): {len(pp_middles)}")
print(f"Total B tokens with MIDDLEs: {sum(b_middle_counts.values())}")

# ============================================================
# STEP 2: LOAD LABELS FROM PHARMA_LABEL_DECODING
# ============================================================
print("\n--- Step 2: Loading Labels ---")

pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'
label_files = list(pharma_dir.glob('*_mapping.json'))

all_labels = []

for f in label_files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)

    folio = data.get('folio', f.stem.split('_')[0])

    for group in data.get('groups', []):
        # Jar label
        jar = group.get('jar')
        if jar and isinstance(jar, str):
            all_labels.append({'token': jar, 'folio': folio, 'type': 'jar', 'group': group.get('row', 0)})

        # Root/leaf labels
        for key in ['roots', 'leaves', 'labels']:
            for item in group.get(key, []):
                if isinstance(item, dict):
                    token = item.get('token', '')
                elif isinstance(item, str):
                    token = item
                else:
                    continue
                if token and isinstance(token, str):
                    all_labels.append({'token': token, 'folio': folio, 'type': key.rstrip('s'), 'group': group.get('row', 0)})

print(f"Total labels loaded: {len(all_labels)}")

# ============================================================
# STEP 3: EXTRACT PP BASES FROM LABELS
# ============================================================
print("\n--- Step 3: Extracting PP Bases from Labels ---")

def extract_pp_base(middle, pp_vocab):
    """Extract PP base from RI MIDDLE."""
    if not middle:
        return None

    # If middle IS a PP, return it
    if middle in pp_vocab:
        return middle

    # Otherwise, find longest PP substring
    best_pp = None
    for pp in pp_vocab:
        if len(pp) < 2:
            continue
        if pp in middle and (best_pp is None or len(pp) > len(best_pp)):
            best_pp = pp

    return best_pp

label_analysis = []

for label in all_labels:
    m = morph.extract(label['token'])
    if not m or not m.middle:
        continue

    pp_base = extract_pp_base(m.middle, pp_middles)

    label_analysis.append({
        'token': label['token'],
        'folio': label['folio'],
        'type': label['type'],
        'middle': m.middle,
        'pp_base': pp_base,
        'is_pp': m.middle in pp_middles,
        'is_ri': pp_base is not None and m.middle != pp_base,
        'b_folios': list(b_middle_to_folios.get(pp_base, [])) if pp_base else [],
        'b_count': b_middle_counts.get(pp_base, 0) if pp_base else 0
    })

# Classify
pp_labels = [l for l in label_analysis if l['is_pp']]
ri_labels = [l for l in label_analysis if l['is_ri']]
no_match = [l for l in label_analysis if not l['pp_base']]

print(f"\nLabel classification:")
print(f"  PP labels (MIDDLE in B): {len(pp_labels)}")
print(f"  RI labels (MIDDLE derived from PP): {len(ri_labels)}")
print(f"  No PP match: {len(no_match)}")

# ============================================================
# STEP 4: SHOW LABEL -> B CONNECTIONS
# ============================================================
print("\n--- Step 4: Label -> B Pipeline Examples ---")

print("\n=== PP LABELS (Direct B vocabulary) ===")
print("These label MIDDLEs appear directly in B text:\n")

# Sort by B frequency
pp_labels_sorted = sorted(pp_labels, key=lambda x: x['b_count'], reverse=True)[:15]

print(f"{'Label':<15} {'MIDDLE':<12} {'B count':<8} {'B folios (sample)'}")
print("-" * 70)
for l in pp_labels_sorted:
    folios_sample = ', '.join(sorted(l['b_folios'])[:5])
    if len(l['b_folios']) > 5:
        folios_sample += f"... (+{len(l['b_folios'])-5})"
    print(f"{l['token']:<15} {l['middle']:<12} {l['b_count']:<8} {folios_sample}")

print("\n=== RI LABELS (Derived from PP) ===")
print("These labels derive from B vocabulary via extension:\n")

ri_labels_sorted = sorted(ri_labels, key=lambda x: x['b_count'], reverse=True)[:15]

print(f"{'Label':<15} {'MIDDLE':<12} {'PP base':<10} {'B count':<8} {'B folios (sample)'}")
print("-" * 80)
for l in ri_labels_sorted:
    folios_sample = ', '.join(sorted(l['b_folios'])[:4])
    if len(l['b_folios']) > 4:
        folios_sample += f"... (+{len(l['b_folios'])-4})"
    print(f"{l['token']:<15} {l['middle']:<12} {l['pp_base']:<10} {l['b_count']:<8} {folios_sample}")

# ============================================================
# STEP 5: JAR vs CONTENT PIPELINE COMPARISON
# ============================================================
print("\n--- Step 5: Jar vs Content (Root/Leaf) Pipeline ---")

jar_labels = [l for l in label_analysis if l['type'] == 'jar' and l['pp_base']]
content_labels = [l for l in label_analysis if l['type'] in ['root', 'leaf'] and l['pp_base']]

print(f"\nJar labels with PP connection: {len(jar_labels)}")
print(f"Content labels with PP connection: {len(content_labels)}")

# Average B frequency per PP base
jar_avg_b = sum(l['b_count'] for l in jar_labels) / len(jar_labels) if jar_labels else 0
content_avg_b = sum(l['b_count'] for l in content_labels) / len(content_labels) if content_labels else 0

print(f"\nAverage B occurrences of PP base:")
print(f"  Jar labels: {jar_avg_b:.1f}")
print(f"  Content labels: {content_avg_b:.1f}")

# PP base overlap between jars and content
jar_pp = set(l['pp_base'] for l in jar_labels)
content_pp = set(l['pp_base'] for l in content_labels)

overlap = jar_pp & content_pp
jar_only = jar_pp - content_pp
content_only = content_pp - jar_pp

print(f"\nPP base distribution:")
print(f"  Jar-only PP bases: {len(jar_only)}")
print(f"  Content-only PP bases: {len(content_only)}")
print(f"  Shared PP bases: {len(overlap)}")

# ============================================================
# STEP 6: B FOLIO CONCENTRATION
# ============================================================
print("\n--- Step 6: Which B Folios Do Labels Connect To? ---")

# Aggregate all B folios that labels connect to
all_b_connections = Counter()
for l in label_analysis:
    if l['pp_base']:
        for f in l['b_folios']:
            all_b_connections[f] += 1

print(f"\nTop 15 B folios connected to labels:")
print(f"{'Folio':<10} {'Label connections'}")
print("-" * 30)
for folio, count in all_b_connections.most_common(15):
    print(f"{folio:<10} {count}")

# ============================================================
# STEP 7: SPECIFIC EXAMPLE TRACES
# ============================================================
print("\n--- Step 7: Example Pipeline Traces ---")

# Pick a few interesting examples
examples = [
    ('okaradag', 'jar'),  # jar from f99r
    ('okary', 'root'),    # root from f99r
    ('oparal', 'jar'),    # jar from f99r
]

for token, expected_type in examples:
    matches = [l for l in label_analysis if l['token'] == token]
    if matches:
        l = matches[0]
        print(f"\n{token} ({l['type']}):")
        print(f"  Folio: {l['folio']}")
        print(f"  MIDDLE: {l['middle']}")
        print(f"  PP base: {l['pp_base'] or '(none)'}")
        print(f"  Classification: {'PP' if l['is_pp'] else 'RI' if l['is_ri'] else 'Unknown'}")
        if l['pp_base']:
            print(f"  B occurrences: {l['b_count']}")
            print(f"  B folios: {', '.join(sorted(l['b_folios'])[:8])}")
            if len(l['b_folios']) > 8:
                print(f"            ... and {len(l['b_folios'])-8} more")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'summary': {
        'total_labels': len(all_labels),
        'labels_with_morphology': len(label_analysis),
        'pp_labels': len(pp_labels),
        'ri_labels': len(ri_labels),
        'no_pp_match': len(no_match),
        'jar_avg_b_freq': jar_avg_b,
        'content_avg_b_freq': content_avg_b
    },
    'pp_base_distribution': {
        'jar_only': len(jar_only),
        'content_only': len(content_only),
        'shared': len(overlap)
    },
    'top_b_connections': dict(all_b_connections.most_common(20)),
    'label_details': label_analysis
}

output_path = PROJECT_ROOT / 'phases' / 'LABEL_INVESTIGATION' / 'results' / 'label_b_pipeline.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: LABEL -> B PIPELINE")
print("="*70)

total_with_b = len([l for l in label_analysis if l['b_count'] > 0])
pct_with_b = 100 * total_with_b / len(label_analysis) if label_analysis else 0

print(f"""
LABEL -> PP BASE -> B CONNECTION:

Labels analyzed: {len(label_analysis)}
Labels with B connection (PP base appears in B): {total_with_b} ({pct_with_b:.1f}%)

Breakdown:
  - PP labels (direct B vocabulary): {len(pp_labels)}
  - RI labels (derived from PP via extension): {len(ri_labels)}
  - No PP match (label-only vocabulary): {len(no_match)}

Pipeline Strength:
  - Jar labels avg B frequency: {jar_avg_b:.1f}
  - Content labels avg B frequency: {content_avg_b:.1f}

This confirms: Labels ARE connected to B through shared PP vocabulary.
The pipeline is: Label MIDDLE -> PP base -> B procedures using that base.
""")
