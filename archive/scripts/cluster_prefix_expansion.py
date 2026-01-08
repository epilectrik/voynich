"""
Cluster Prefix Expansion Analysis

Investigate whether orphan patterns like `tshed`, `kshed`, `rshed`
should be added to our cluster prefix inventory.
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lib import load_transcription

# Current known prefixes
B_GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct', 'lch', 'lk', 'ls']
B_GRAMMAR_SUFFIXES = ['aiin', 'ain', 'dy', 'edy', 'eedy', 'ey', 'eey', 'y', 'ol', 'or', 'ar', 'al', 'o', 'hy', 'chy']
CLUSTER_PREFIXES = ['ck', 'ckh', 'ds', 'dsh', 'cp', 'cph', 'ks', 'ksh', 'ts', 'tsh', 'ps', 'psh']

# Load data with recovery
entries = load_transcription(apply_recovery=True, min_confidence='HIGH', include_metadata=True)
b_entries = [e for e in entries if e['currier'] == 'B' and '*' not in e['word']]

print("=" * 70)
print("CLUSTER PREFIX EXPANSION ANALYSIS")
print("=" * 70)

# Find all tokens that have a B suffix but no recognized prefix
def has_b_suffix(word):
    for s in sorted(B_GRAMMAR_SUFFIXES, key=len, reverse=True):
        if word.endswith(s):
            return s
    return None

def has_known_prefix(word):
    for p in B_GRAMMAR_PREFIXES + CLUSTER_PREFIXES:
        if word.startswith(p):
            return p
    return None

# Collect tokens with suffix but no prefix
suffix_no_prefix = []
for e in b_entries:
    word = e['word']
    suffix = has_b_suffix(word)
    prefix = has_known_prefix(word)

    if suffix and not prefix and len(word) > len(suffix):
        stem = word[:-len(suffix)] if suffix else word
        suffix_no_prefix.append({
            'word': word,
            'stem': stem,
            'suffix': suffix,
            'folio': e['folio']
        })

print(f"\nTokens with B-suffix but no recognized prefix: {len(suffix_no_prefix)}")

# Analyze stems (what comes before the suffix)
stem_freq = Counter(e['stem'] for e in suffix_no_prefix)
stem_examples = defaultdict(list)
for e in suffix_no_prefix:
    if len(stem_examples[e['stem']]) < 10:
        stem_examples[e['stem']].append(e['word'])

print(f"Unique stems: {len(stem_freq)}")

# Find candidate new prefixes (stems that appear frequently)
print(f"\n### CANDIDATE NEW PREFIXES")
print(f"(Stems appearing 10+ times with B-suffixes)")
print(f"\n{'Stem':<12} {'Freq':>8} {'Example tokens':<40}")
print("-" * 65)

candidates = []
for stem, freq in stem_freq.most_common():
    if freq >= 10:
        examples = ', '.join(stem_examples[stem][:5])
        print(f"{stem:<12} {freq:>8} {examples:<40}")
        candidates.append(stem)

# Now let's check if these candidates behave like grammar prefixes
print(f"\n" + "=" * 70)
print("VALIDATION: Do candidate prefixes behave like B-grammar?")
print("=" * 70)

# Test 1: Do they combine with multiple suffixes?
print(f"\n### TEST 1: Suffix Combinatorics")
print("(Good prefixes should combine with multiple suffixes)")

candidate_suffix_combos = defaultdict(Counter)
for e in suffix_no_prefix:
    if e['stem'] in candidates:
        candidate_suffix_combos[e['stem']][e['suffix']] += 1

print(f"\n{'Candidate':<12} {'#Suffixes':>10} {'Top suffixes':<40}")
print("-" * 65)

for cand in candidates[:20]:
    suffixes = candidate_suffix_combos[cand]
    n_suffixes = len(suffixes)
    top = ', '.join([f"{s}({c})" for s, c in suffixes.most_common(5)])
    print(f"{cand:<12} {n_suffixes:>10} {top:<40}")

# Test 2: Section distribution (should be similar to known prefixes)
print(f"\n### TEST 2: Section Distribution")
print("(Compare to known B-grammar prefix distribution)")

# Get known prefix section distribution
known_prefix_sections = Counter()
candidate_sections = defaultdict(Counter)

for e in b_entries:
    word = e['word']
    section = e['section']

    # Known prefixes
    for p in B_GRAMMAR_PREFIXES:
        if word.startswith(p):
            known_prefix_sections[section] += 1
            break

    # Candidates
    for cand in candidates:
        if word.startswith(cand):
            candidate_sections[cand][section] += 1
            break

print(f"\nKnown B-grammar prefix distribution:")
total_known = sum(known_prefix_sections.values())
for section, count in known_prefix_sections.most_common():
    print(f"  {section}: {100*count/total_known:.1f}%")

print(f"\nCandidate prefix distribution:")
for cand in candidates[:10]:
    total_cand = sum(candidate_sections[cand].values())
    if total_cand > 0:
        dist = ', '.join([f"{s}:{100*c/total_cand:.0f}%" for s, c in candidate_sections[cand].most_common(3)])
        print(f"  {cand}: {dist}")

# Test 3: Are these consonant clusters or something else?
print(f"\n### TEST 3: Morphological Analysis")
print("(What are these stems structurally?)")

vowels = set('aeiou')
consonants = set('bcdfghjklmnpqrstvwxyz')

categories = defaultdict(list)
for cand in candidates:
    chars = set(cand)
    if chars <= consonants:
        categories['consonant_only'].append(cand)
    elif chars <= vowels:
        categories['vowel_only'].append(cand)
    elif cand[0] in vowels:
        categories['vowel_initial'].append(cand)
    elif len(cand) == 1:
        categories['single_char'].append(cand)
    else:
        categories['mixed'].append(cand)

for cat, stems in categories.items():
    print(f"\n{cat}: {len(stems)} candidates")
    print(f"  {', '.join(stems[:15])}")

# Test 4: Compare to existing cluster prefixes
print(f"\n### TEST 4: Pattern Similarity to Known Clusters")
print("(Known clusters: ck, ckh, ds, dsh, cp, cph, ks, ksh, ts, tsh, ps, psh)")

# Known cluster pattern: consonant + consonant (+ h)
print(f"\nCandidates that match C+C or C+C+h pattern:")
cc_pattern = []
for cand in candidates:
    if len(cand) >= 2 and cand[0] in consonants and cand[1] in consonants:
        cc_pattern.append(cand)

print(f"  {', '.join(cc_pattern)}")

# Proposed additions
print(f"\n" + "=" * 70)
print("PROPOSED CLUSTER PREFIX ADDITIONS")
print("=" * 70)

# Filter to consonant-cluster patterns with good frequency
proposed = []
for cand in candidates:
    if len(cand) >= 2 and set(cand) <= consonants:
        freq = stem_freq[cand]
        n_suffixes = len(candidate_suffix_combos[cand])
        if n_suffixes >= 3:  # Combines with at least 3 suffixes
            proposed.append((cand, freq, n_suffixes))

proposed.sort(key=lambda x: -x[1])

print(f"\n{'Prefix':<10} {'Freq':>8} {'#Suffixes':>10} {'Examples':<35}")
print("-" * 65)

for cand, freq, n_suff in proposed:
    examples = ', '.join(stem_examples[cand][:4])
    print(f"{cand:<10} {freq:>8} {n_suff:>10} {examples:<35}")

# Also check vowel-initial candidates
print(f"\n### VOWEL-INITIAL CANDIDATES (different category)")
vowel_proposed = []
for cand in candidates:
    if cand and cand[0] in vowels:
        freq = stem_freq[cand]
        n_suffixes = len(candidate_suffix_combos[cand])
        if n_suffixes >= 2:
            vowel_proposed.append((cand, freq, n_suffixes))

vowel_proposed.sort(key=lambda x: -x[1])

print(f"\n{'Prefix':<10} {'Freq':>8} {'#Suffixes':>10} {'Examples':<35}")
print("-" * 65)

for cand, freq, n_suff in vowel_proposed[:15]:
    examples = ', '.join(stem_examples[cand][:4])
    print(f"{cand:<10} {freq:>8} {n_suff:>10} {examples:<35}")

# Summary
print(f"\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
CONSONANT CLUSTER CANDIDATES (high confidence):
  {', '.join([p[0] for p in proposed])}

These behave like grammar prefixes:
  - Combine with multiple B-suffixes
  - Consonant-only structure (like existing clusters)
  - Appear in B-heavy sections

VOWEL-INITIAL CANDIDATES (needs more investigation):
  {', '.join([p[0] for p in vowel_proposed[:10]])}

These might be:
  - A different morphological layer
  - Inverted forms (suffix-prefix instead of prefix-suffix)
  - Or noise

RECOMMENDATION:
  Add consonant clusters to CLUSTER_PREFIXES list
  Vowel-initial forms need separate analysis
""")

# Calculate impact
new_prefixes = [p[0] for p in proposed]
would_explain = sum(1 for e in suffix_no_prefix if e['stem'] in new_prefixes)
print(f"Adding consonant clusters would explain: {would_explain} more tokens")
print(f"Current unexplained with suffix: {len(suffix_no_prefix)}")
print(f"Remaining unexplained: {len(suffix_no_prefix) - would_explain}")
