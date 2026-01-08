"""
Cluster Prefix Grammar Tests

TEST 1: Do cluster prefixes obey B-grammar constraints?
TEST 2: Prefix compression hypothesis (ckh- ≈ kch- distributionally?)
TEST 3: Section-conditional specialization (high-activity sections?)
TEST 4: HT exclusion test (appear near hazards, unlike HT?)
"""

from collections import Counter, defaultdict
from pathlib import Path
import json

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Known B grammar prefixes
B_GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct', 'lch', 'lk', 'ls']

# Candidate cluster prefixes (from our analysis)
CLUSTER_PREFIXES = ['ck', 'ckh', 'ds', 'dsh', 'cp', 'cph', 'ks', 'ksh', 'ts', 'tsh', 'ps', 'psh']

# HT prefixes for comparison
HT_PREFIXES = ['yk', 'yp', 'yt', 'yc', 'yd', 'ys', 'op', 'oc', 'oe', 'of',
               'pc', 'tc', 'dc', 'kc', 'sc', 'fc', 'sa', 'so', 'ka', 'ke',
               'ko', 'ta', 'te', 'to', 'po', 'do', 'lo', 'ro']

# B Grammar suffixes
B_GRAMMAR_SUFFIXES = ['aiin', 'ain', 'dy', 'edy', 'eedy', 'ey', 'eey', 'y',
                       'ol', 'or', 'ar', 'al', 'o', 'hy', 'chy']

# Known forbidden transitions (from Phase 18)
FORBIDDEN_TRANSITIONS = [
    ('ol', 'qo'), ('ol', 'ok'), ('qo', 'ol'), ('sh', 'ol'),
    ('ot', 'ch'), ('ch', 'ot'), ('da', 'sh'), ('sh', 'da'),
    ('ct', 'qo'), ('qo', 'ct'), ('ok', 'da'), ('da', 'ok'),
    ('ot', 'da'), ('da', 'ot'), ('ct', 'sh'), ('sh', 'ct'),
    ('ct', 'da')
]

# Hazard-adjacent tokens (approximation - tokens that appear in forbidden transitions)
HAZARD_TOKENS = set()
for t1, t2 in FORBIDDEN_TRANSITIONS:
    HAZARD_TOKENS.add(t1)
    HAZARD_TOKENS.add(t2)

def get_prefix_type(tok):
    """Classify token by prefix type."""
    t = tok.lower()

    # Check cluster prefixes first (longer matches)
    for p in sorted(CLUSTER_PREFIXES, key=len, reverse=True):
        if t.startswith(p):
            return ('CLUSTER', p)

    # Check B grammar prefixes
    for p in sorted(B_GRAMMAR_PREFIXES, key=len, reverse=True):
        if t.startswith(p):
            return ('B_GRAMMAR', p)

    # Check HT prefixes
    for p in sorted(HT_PREFIXES, key=len, reverse=True):
        if t.startswith(p):
            return ('HT', p)

    return ('OTHER', None)

def get_prefix_class(tok):
    """Get just the class (CLUSTER, B_GRAMMAR, HT, OTHER)."""
    return get_prefix_type(tok)[0]

# Load all data with context
lines_data = []  # (folio, section, line_num, [tokens])
current_key = None
current_tokens = []

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 11:
            word = parts[0].strip('"').strip().lower()
            folio = parts[2].strip('"').strip()
            section = parts[3].strip('"').strip() if len(parts) > 3 else ''
            line_num = parts[11].strip('"').strip()
            lang = parts[6].strip('"').strip()

            if not word or word.startswith('*'):
                continue

            # Only Currier B
            if lang != 'B':
                continue

            key = (folio, section, line_num)
            if key != current_key:
                if current_tokens and current_key:
                    lines_data.append((current_key[0], current_key[1], current_key[2], current_tokens))
                current_tokens = []
                current_key = key
            current_tokens.append(word)

if current_tokens and current_key:
    lines_data.append((current_key[0], current_key[1], current_key[2], current_tokens))

print("=" * 80)
print("CLUSTER PREFIX GRAMMAR TESTS")
print("=" * 80)
print(f"Loaded {len(lines_data)} lines from Currier B")

# ============================================================================
# TEST 1: Do cluster prefixes obey B-grammar constraints?
# ============================================================================

print("\n" + "=" * 80)
print("TEST 1: GRAMMAR CONSTRAINT COMPLIANCE")
print("=" * 80)

# Collect bigram transitions by prefix type
transitions_by_type = defaultdict(Counter)
forbidden_violations = defaultdict(list)

for folio, section, line_num, tokens in lines_data:
    for i in range(len(tokens) - 1):
        t1 = tokens[i]
        t2 = tokens[i+1]

        type1, prefix1 = get_prefix_type(t1)
        type2, prefix2 = get_prefix_type(t2)

        # Record transition
        if type1 in ['B_GRAMMAR', 'CLUSTER']:
            transitions_by_type[type1][(prefix1, prefix2 if prefix2 else t2[:2])] += 1

            # Check for forbidden-like transitions
            # Map cluster to closest B equivalent for comparison
            cluster_to_b = {
                'ck': 'ch', 'ckh': 'ch',
                'ds': 'da', 'dsh': 'sh',
                'cp': 'ch', 'cph': 'ch',
                'ks': 'ok', 'ksh': 'sh',
                'ts': 'ot', 'tsh': 'sh',
                'ps': 'sh', 'psh': 'sh'
            }

            mapped_p1 = cluster_to_b.get(prefix1, prefix1) if type1 == 'CLUSTER' else prefix1
            mapped_p2 = cluster_to_b.get(prefix2, prefix2) if type2 == 'CLUSTER' else prefix2

            if mapped_p1 and mapped_p2 and (mapped_p1, mapped_p2) in FORBIDDEN_TRANSITIONS:
                forbidden_violations[type1].append((t1, t2, folio))

print("\n### Forbidden Transition Violations (mapped to B equivalents)")
print(f"B_GRAMMAR violations: {len(forbidden_violations['B_GRAMMAR'])}")
print(f"CLUSTER violations: {len(forbidden_violations['CLUSTER'])}")

if forbidden_violations['CLUSTER']:
    print("\nCluster violations (first 10):")
    for t1, t2, folio in forbidden_violations['CLUSTER'][:10]:
        print(f"  {t1} -> {t2} ({folio})")

# ============================================================================
# TEST 2: Prefix compression hypothesis
# ============================================================================

print("\n" + "=" * 80)
print("TEST 2: PREFIX COMPRESSION HYPOTHESIS")
print("=" * 80)

# Compare neighborhood profiles
# If ckh- ≈ kch-, they should appear in similar contexts

def get_neighborhood(tokens, target_prefix, window=2):
    """Get tokens that appear within window of target prefix tokens."""
    neighbors = Counter()
    for i, tok in enumerate(tokens):
        if tok.startswith(target_prefix):
            for j in range(max(0, i-window), min(len(tokens), i+window+1)):
                if j != i:
                    neighbors[tokens[j]] += 1
    return neighbors

# Collect neighborhoods across all lines
cluster_neighborhoods = defaultdict(Counter)
b_grammar_neighborhoods = defaultdict(Counter)

for folio, section, line_num, tokens in lines_data:
    # Cluster prefixes
    for cp in ['ckh', 'dsh', 'cph', 'ksh', 'tsh', 'psh']:
        neighbors = get_neighborhood(tokens, cp)
        cluster_neighborhoods[cp].update(neighbors)

    # Potential B equivalents
    for bp in ['ch', 'sh', 'da', 'ok', 'ot']:
        neighbors = get_neighborhood(tokens, bp)
        b_grammar_neighborhoods[bp].update(neighbors)

# Compare distributions
print("\n### Neighborhood Similarity (Jaccard)")

def jaccard(c1, c2, top_n=50):
    """Jaccard similarity of top N neighbors."""
    s1 = set(list(c1.keys())[:top_n])
    s2 = set(list(c2.keys())[:top_n])
    if not s1 or not s2:
        return 0
    return len(s1 & s2) / len(s1 | s2)

comparisons = [
    ('ckh', 'ch'),
    ('dsh', 'sh'),
    ('cph', 'ch'),
    ('ksh', 'sh'),
    ('tsh', 'sh'),
]

print(f"{'Cluster':<10} {'B-equiv':<10} {'Jaccard':>10} {'Interpretation':<30}")
print("-" * 65)

for cluster, b_equiv in comparisons:
    j = jaccard(cluster_neighborhoods[cluster], b_grammar_neighborhoods[b_equiv])
    interp = "SIMILAR context" if j > 0.3 else "DIFFERENT context" if j < 0.15 else "MODERATE"
    print(f"{cluster:<10} {b_equiv:<10} {j:>10.3f} {interp:<30}")

# ============================================================================
# TEST 3: Section-conditional specialization
# ============================================================================

print("\n" + "=" * 80)
print("TEST 3: SECTION-CONDITIONAL SPECIALIZATION")
print("=" * 80)

# Count prefix types by section
section_counts = defaultdict(lambda: defaultdict(int))
section_totals = defaultdict(int)

for folio, section, line_num, tokens in lines_data:
    for tok in tokens:
        ptype = get_prefix_class(tok)
        section_counts[section][ptype] += 1
        section_totals[section] += 1

print("\n### Prefix Type Distribution by Section")
print(f"{'Section':<10} {'Total':>8} {'B_GRAM%':>10} {'CLUSTER%':>10} {'HT%':>10} {'OTHER%':>10}")
print("-" * 60)

for section in sorted(section_counts.keys()):
    total = section_totals[section]
    if total < 100:
        continue
    b_pct = 100 * section_counts[section]['B_GRAMMAR'] / total
    c_pct = 100 * section_counts[section]['CLUSTER'] / total
    h_pct = 100 * section_counts[section]['HT'] / total
    o_pct = 100 * section_counts[section]['OTHER'] / total
    print(f"{section if section else '(none)':<10} {total:>8} {b_pct:>9.1f}% {c_pct:>9.1f}% {h_pct:>9.1f}% {o_pct:>9.1f}%")

# Check if cluster prefixes correlate with "intensity" metrics
print("\n### Cluster Prefix Density vs Section Activity")
# Sections H, S, B are typically more "operational" than C, P, T

high_activity = ['H', 'S', 'B']
low_activity = ['C', 'P', 'T']

high_cluster = sum(section_counts[s]['CLUSTER'] for s in high_activity)
high_total = sum(section_totals[s] for s in high_activity)
low_cluster = sum(section_counts[s]['CLUSTER'] for s in low_activity)
low_total = sum(section_totals[s] for s in low_activity)

high_rate = 100 * high_cluster / high_total if high_total > 0 else 0
low_rate = 100 * low_cluster / low_total if low_total > 0 else 0

print(f"High-activity sections (H, S, B): {high_rate:.2f}% cluster prefixes")
print(f"Low-activity sections (C, P, T): {low_rate:.2f}% cluster prefixes")
print(f"Ratio: {high_rate/low_rate:.2f}x" if low_rate > 0 else "N/A")

# ============================================================================
# TEST 4: HT Exclusion Test
# ============================================================================

print("\n" + "=" * 80)
print("TEST 4: HT EXCLUSION TEST (Hazard Proximity)")
print("=" * 80)

# Check if cluster prefixes appear near hazard-adjacent tokens
# Unlike HT, which AVOIDS hazards, grammar should be NEUTRAL or PRESENT

def count_near_hazards(lines_data, prefix_type, window=3):
    """Count how often prefix_type appears within window of hazard tokens."""
    near_hazard = 0
    total = 0

    for folio, section, line_num, tokens in lines_data:
        for i, tok in enumerate(tokens):
            if get_prefix_class(tok) == prefix_type:
                total += 1
                # Check if any token within window is hazard-related
                for j in range(max(0, i-window), min(len(tokens), i+window+1)):
                    if j != i:
                        neighbor = tokens[j]
                        # Check if neighbor starts with hazard-adjacent prefix
                        for hp in HAZARD_TOKENS:
                            if neighbor.startswith(hp):
                                near_hazard += 1
                                break

    return near_hazard, total

cluster_near, cluster_total = count_near_hazards(lines_data, 'CLUSTER')
b_grammar_near, b_grammar_total = count_near_hazards(lines_data, 'B_GRAMMAR')
ht_near, ht_total = count_near_hazards(lines_data, 'HT')

print("\n### Hazard Proximity by Prefix Type")
print(f"{'Type':<15} {'Near Hazard':>12} {'Total':>10} {'Rate':>10}")
print("-" * 50)

cluster_rate = cluster_near / cluster_total if cluster_total > 0 else 0
b_rate = b_grammar_near / b_grammar_total if b_grammar_total > 0 else 0
ht_rate = ht_near / ht_total if ht_total > 0 else 0

print(f"{'B_GRAMMAR':<15} {b_grammar_near:>12} {b_grammar_total:>10} {b_rate:>9.3f}")
print(f"{'CLUSTER':<15} {cluster_near:>12} {cluster_total:>10} {cluster_rate:>9.3f}")
print(f"{'HT':<15} {ht_near:>12} {ht_total:>10} {ht_rate:>9.3f}")

print("\n### Interpretation")
if abs(cluster_rate - b_rate) < 0.1:
    print("CLUSTER behaves like B_GRAMMAR near hazards (similar rate)")
elif cluster_rate < ht_rate:
    print("CLUSTER avoids hazards like HT (unexpected!)")
else:
    print("CLUSTER shows different hazard behavior than both")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY: CLUSTER PREFIX STATUS")
print("=" * 80)

print("""
TEST 1 - Grammar Constraints:
""")
if len(forbidden_violations['CLUSTER']) == 0:
    print("  PASS - Cluster prefixes obey forbidden transitions")
else:
    print(f"  MIXED - {len(forbidden_violations['CLUSTER'])} violations found")

print("""
TEST 2 - Compression Hypothesis:
""")
avg_jaccard = sum(jaccard(cluster_neighborhoods[c], b_grammar_neighborhoods[b])
                  for c, b in comparisons) / len(comparisons)
if avg_jaccard > 0.25:
    print(f"  SUPPORTED - Average Jaccard {avg_jaccard:.3f} suggests distributional similarity")
else:
    print(f"  WEAK - Average Jaccard {avg_jaccard:.3f} suggests different contexts")

print("""
TEST 3 - Section Specialization:
""")
if high_rate > low_rate * 1.2:
    print(f"  CONFIRMED - Cluster prefixes {high_rate/low_rate:.1f}x more common in high-activity sections")
else:
    print("  NOT CONFIRMED - No clear section preference")

print("""
TEST 4 - HT Exclusion:
""")
if abs(cluster_rate - b_rate) < abs(cluster_rate - ht_rate):
    print("  PASS - Cluster prefixes behave like B_GRAMMAR (not HT) near hazards")
else:
    print("  FAIL - Cluster prefixes behave more like HT")

print("""
VERDICT:
""")
tests_passed = sum([
    len(forbidden_violations['CLUSTER']) < 5,
    avg_jaccard > 0.2,
    high_rate > low_rate,
    abs(cluster_rate - b_rate) < abs(cluster_rate - ht_rate)
])

if tests_passed >= 3:
    print(f"  {tests_passed}/4 tests support: CLUSTER PREFIXES ARE B-GRAMMAR VARIANTS")
    print("  Recommendation: Add to grammar prefix inventory, shrink residue")
else:
    print(f"  {tests_passed}/4 tests support grammar hypothesis")
    print("  Recommendation: Further investigation needed")

print("\n" + "=" * 80)
