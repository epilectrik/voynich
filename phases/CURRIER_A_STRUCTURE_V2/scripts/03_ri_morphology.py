"""
03_ri_morphology.py

TEST 3: RI MORPHOLOGY BY POSITION

Compare PREFIX profiles of initial-RI vs middle-RI vs final-RI.

Different morphology → different functions
Same morphology → same function, different placement
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import math

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("TEST 3: RI MORPHOLOGY BY POSITION")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD PARAGRAPH STRUCTURE AND COLLECT RI
# =============================================================
print("\n[1/4] Building paragraph structure and collecting RI...")

# Build paragraph structure
folio_paragraphs = defaultdict(list)
current_para_tokens = []
current_folio = None

for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue

    if t.folio != current_folio:
        if current_para_tokens:
            folio_paragraphs[current_folio].append(current_para_tokens)
        current_folio = t.folio
        current_para_tokens = []

    if t.par_initial and current_para_tokens:
        folio_paragraphs[current_folio].append(current_para_tokens)
        current_para_tokens = []

    current_para_tokens.append(t)

if current_para_tokens and current_folio:
    folio_paragraphs[current_folio].append(current_para_tokens)

# Classify RI by position within paragraph
initial_ri = []  # First line of paragraph
middle_ri = []   # Middle lines
final_ri = []    # Last line of paragraph

for folio, paragraphs in folio_paragraphs.items():
    for para_tokens in paragraphs:
        if not para_tokens:
            continue

        # Get line boundaries
        lines = sorted(set(t.line for t in para_tokens))
        if not lines:
            continue

        first_line = lines[0]
        last_line = lines[-1]

        # Analyze each line for RI tokens
        for line in lines:
            try:
                record = analyzer.analyze_record(folio, line)
                if not record:
                    continue
            except:
                continue

            for t in record.tokens:
                if t.token_class != 'RI':
                    continue

                entry = {
                    'folio': folio,
                    'line': line,
                    'word': t.word
                }

                if line == first_line:
                    initial_ri.append(entry)
                elif line == last_line and len(lines) > 1:
                    final_ri.append(entry)
                else:
                    middle_ri.append(entry)

print(f"   Initial RI (first line): {len(initial_ri)}")
print(f"   Middle RI (middle lines): {len(middle_ri)}")
print(f"   Final RI (last line): {len(final_ri)}")

# =============================================================
# STEP 2: ANALYZE PREFIX DISTRIBUTION
# =============================================================
print("\n[2/4] Analyzing PREFIX distribution...")

def get_prefix_distribution(ri_list):
    """Get PREFIX distribution for a list of RI tokens."""
    prefixes = Counter()
    for entry in ri_list:
        try:
            m = morph.extract(entry['word'])
            if m.prefix:
                prefixes[m.prefix] += 1
            else:
                prefixes['NO_PREFIX'] += 1
        except:
            prefixes['UNKNOWN'] += 1
    return prefixes

initial_prefixes = get_prefix_distribution(initial_ri)
middle_prefixes = get_prefix_distribution(middle_ri)
final_prefixes = get_prefix_distribution(final_ri)

# All prefixes
all_prefixes = sorted(set(initial_prefixes.keys()) | set(middle_prefixes.keys()) | set(final_prefixes.keys()))

# Normalize
total_initial = sum(initial_prefixes.values())
total_middle = sum(middle_prefixes.values())
total_final = sum(final_prefixes.values())

print(f"\n{'PREFIX':<12} {'INITIAL':>10} {'MIDDLE':>10} {'FINAL':>10}")
print("-" * 44)

prefix_data = {}
for prefix in all_prefixes:
    pct_initial = 100 * initial_prefixes[prefix] / total_initial if total_initial > 0 else 0
    pct_middle = 100 * middle_prefixes[prefix] / total_middle if total_middle > 0 else 0
    pct_final = 100 * final_prefixes[prefix] / total_final if total_final > 0 else 0

    prefix_data[prefix] = {
        'initial_pct': pct_initial,
        'middle_pct': pct_middle,
        'final_pct': pct_final,
        'initial_n': initial_prefixes[prefix],
        'middle_n': middle_prefixes[prefix],
        'final_n': final_prefixes[prefix]
    }

    print(f"{prefix:<12} {pct_initial:>9.1f}% {pct_middle:>9.1f}% {pct_final:>9.1f}%")

# =============================================================
# STEP 3: ANALYZE SUFFIX DISTRIBUTION
# =============================================================
print("\n[3/4] Analyzing SUFFIX distribution...")

def get_suffix_distribution(ri_list):
    """Get SUFFIX distribution for a list of RI tokens."""
    suffixes = Counter()
    for entry in ri_list:
        try:
            m = morph.extract(entry['word'])
            if m.suffix:
                suffixes[m.suffix] += 1
            else:
                suffixes['NO_SUFFIX'] += 1
        except:
            suffixes['UNKNOWN'] += 1
    return suffixes

initial_suffixes = get_suffix_distribution(initial_ri)
middle_suffixes = get_suffix_distribution(middle_ri)
final_suffixes = get_suffix_distribution(final_ri)

# All suffixes
all_suffixes = sorted(set(initial_suffixes.keys()) | set(middle_suffixes.keys()) | set(final_suffixes.keys()))

print(f"\n{'SUFFIX':<12} {'INITIAL':>10} {'MIDDLE':>10} {'FINAL':>10}")
print("-" * 44)

suffix_data = {}
for suffix in list(all_suffixes)[:15]:  # Top 15
    pct_initial = 100 * initial_suffixes[suffix] / total_initial if total_initial > 0 else 0
    pct_middle = 100 * middle_suffixes[suffix] / total_middle if total_middle > 0 else 0
    pct_final = 100 * final_suffixes[suffix] / total_final if total_final > 0 else 0

    suffix_data[suffix] = {
        'initial_pct': pct_initial,
        'middle_pct': pct_middle,
        'final_pct': pct_final
    }

    print(f"{suffix:<12} {pct_initial:>9.1f}% {pct_middle:>9.1f}% {pct_final:>9.1f}%")

# =============================================================
# STEP 4: STATISTICAL COMPARISON
# =============================================================
print("\n[4/4] Statistical comparison...")

# Cosine similarity between distributions
def cosine_similarity(dist1, dist2, keys):
    """Compute cosine similarity between two distributions."""
    vec1 = [dist1.get(k, 0) for k in keys]
    vec2 = [dist2.get(k, 0) for k in keys]

    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5

    return dot / (norm1 * norm2) if norm1 * norm2 > 0 else 0

prefix_keys = list(all_prefixes)
initial_middle_sim = cosine_similarity(initial_prefixes, middle_prefixes, prefix_keys)
initial_final_sim = cosine_similarity(initial_prefixes, final_prefixes, prefix_keys)
middle_final_sim = cosine_similarity(middle_prefixes, final_prefixes, prefix_keys)

print("\nPREFIX distribution cosine similarity:")
print(f"  Initial vs Middle: {initial_middle_sim:.3f}")
print(f"  Initial vs Final:  {initial_final_sim:.3f}")
print(f"  Middle vs Final:   {middle_final_sim:.3f}")

# Check for position-specific prefixes
print("\nPosition-specific PREFIX patterns:")
for prefix in all_prefixes:
    pct_i = prefix_data[prefix]['initial_pct']
    pct_m = prefix_data[prefix]['middle_pct']
    pct_f = prefix_data[prefix]['final_pct']

    # Check for strong position preference
    if pct_i > 0 and pct_m > 0:
        ratio = pct_i / pct_m if pct_m > 0 else float('inf')
        if ratio >= 2.0:
            print(f"  {prefix}: INITIAL-preferred ({ratio:.1f}x vs middle)")
        elif ratio <= 0.5:
            print(f"  {prefix}: MIDDLE-preferred ({1/ratio:.1f}x vs initial)")

    if pct_f > 0 and (pct_i + pct_m) > 0:
        avg_non_final = (pct_i + pct_m) / 2
        ratio = pct_f / avg_non_final if avg_non_final > 0 else float('inf')
        if ratio >= 2.0:
            print(f"  {prefix}: FINAL-preferred ({ratio:.1f}x vs others)")

# =============================================================
# LINKER ANALYSIS
# =============================================================
print("\n" + "="*70)
print("LINKER RI ANALYSIS")
print("="*70)

# Find ct-prefix RI (linkers)
linkers_initial = [e for e in initial_ri if e['word'] and e['word'].startswith('ct')]
linkers_middle = [e for e in middle_ri if e['word'] and e['word'].startswith('ct')]
linkers_final = [e for e in final_ri if e['word'] and e['word'].startswith('ct')]

print(f"\nLinker RI (ct-prefix) distribution:")
print(f"  Initial: {len(linkers_initial)}")
print(f"  Middle: {len(linkers_middle)}")
print(f"  Final: {len(linkers_final)}")

if linkers_initial:
    print(f"\nInitial linkers: {[e['word'] for e in linkers_initial]}")
if linkers_middle:
    print(f"Middle linkers: {[e['word'] for e in linkers_middle]}")
if linkers_final:
    print(f"Final linkers: {[e['word'] for e in linkers_final]}")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

avg_similarity = (initial_middle_sim + initial_final_sim + middle_final_sim) / 3

if avg_similarity > 0.9:
    print(f"\n→ HIGH SIMILARITY ({avg_similarity:.2f}): All RI positions have SAME morphology")
    print("  RI function is UNIFORM regardless of position")
    verdict = "UNIFORM_FUNCTION"
elif avg_similarity > 0.7:
    print(f"\n→ MODERATE SIMILARITY ({avg_similarity:.2f}): Some positional variation")
    verdict = "MODERATE_VARIATION"
else:
    print(f"\n→ LOW SIMILARITY ({avg_similarity:.2f}): DISTINCT morphology by position")
    print("  Different RI positions have DIFFERENT functions")
    verdict = "DISTINCT_FUNCTIONS"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'RI_MORPHOLOGY_BY_POSITION',
    'counts': {
        'initial': len(initial_ri),
        'middle': len(middle_ri),
        'final': len(final_ri)
    },
    'prefix_distribution': prefix_data,
    'suffix_distribution': suffix_data,
    'similarity': {
        'initial_middle': initial_middle_sim,
        'initial_final': initial_final_sim,
        'middle_final': middle_final_sim,
        'average': avg_similarity
    },
    'linkers': {
        'initial': len(linkers_initial),
        'middle': len(linkers_middle),
        'final': len(linkers_final)
    },
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'ri_morphology_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
