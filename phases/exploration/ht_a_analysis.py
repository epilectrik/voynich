"""
A-specific HT Pattern Analysis

Investigates:
1. The 'd' atom deep-dive in Currier A
2. Simplex vs Complex HT distribution
3. Labeling suffix analysis (-or, -ol, -hy)
4. A-only HT forms
5. Test: simplex=label vs complex=filler hypothesis

HT tokens: All tokens starting with 'y' OR single-char atoms (y, f, d, r)
"""

import pandas as pd
from collections import Counter, defaultdict
import re

# Load data
DATA_PATH = r"C:\git\voynich\data\transcriptions\interlinear_full_words.txt"

print("=" * 80)
print("A-SPECIFIC HT PATTERN ANALYSIS")
print("=" * 80)

# Read data
df = pd.read_csv(DATA_PATH, sep='\t')
print(f"\nTotal rows loaded: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Filter to Currier A only
df_a = df[df['language'] == 'A'].copy()
print(f"\nCurrier A tokens: {len(df_a)}")
print(f"Currier A folios: {df_a['folio'].nunique()}")
print(f"Currier A folio list: {sorted(df_a['folio'].unique())[:20]}...")

# Also get Currier B for comparison
df_b = df[df['language'] == 'B'].copy()
print(f"\nCurrier B tokens: {len(df_b)}")

# Define HT tokens for this analysis
# HT atoms: y, f, d, r (single character)
# HT tokens: anything starting with 'y'
def is_ht_token(word):
    """Identify HT tokens: y-initial OR single-char atoms"""
    if pd.isna(word):
        return False
    w = str(word).strip()
    # Single-char HT atoms
    if w in ['y', 'f', 'd', 'r']:
        return True
    # y-initial tokens
    if w.startswith('y'):
        return True
    return False

def classify_ht_complexity(word):
    """Classify HT token as simplex or complex"""
    if pd.isna(word):
        return None
    w = str(word).strip()
    if len(w) <= 2:
        return 'simplex'
    else:
        return 'complex'

# Apply HT classification
df_a['is_ht'] = df_a['word'].apply(is_ht_token)
df_a['ht_complexity'] = df_a['word'].apply(lambda x: classify_ht_complexity(x) if is_ht_token(x) else None)

df_b['is_ht'] = df_b['word'].apply(is_ht_token)
df_b['ht_complexity'] = df_b['word'].apply(lambda x: classify_ht_complexity(x) if is_ht_token(x) else None)

# Count HT in A and B
ht_a = df_a[df_a['is_ht']]
ht_b = df_b[df_b['is_ht']]

print("\n" + "=" * 80)
print("HT OVERVIEW")
print("=" * 80)
print(f"\nHT tokens in Currier A: {len(ht_a)} ({100*len(ht_a)/len(df_a):.2f}%)")
print(f"HT tokens in Currier B: {len(ht_b)} ({100*len(ht_b)/len(df_b):.2f}%)")

# ============================================================================
# 1. THE 'd' ATOM DEEP-DIVE
# ============================================================================
print("\n" + "=" * 80)
print("1. THE 'd' ATOM DEEP-DIVE")
print("=" * 80)

# Find all 'd' occurrences in A
d_in_a = df_a[df_a['word'] == 'd'].copy()
d_in_b = df_b[df_b['word'] == 'b'].copy()  # comparison

print(f"\n'd' occurrences in Currier A: {len(d_in_a)}")
print(f"'d' occurrences in Currier B: {len(d_in_b)}")

# Calculate enrichment
if len(df_a) > 0 and len(df_b) > 0:
    d_rate_a = len(d_in_a) / len(df_a) * 100
    d_rate_b = len(d_in_b) / len(df_b) * 100
    print(f"\n'd' rate in A: {d_rate_a:.4f}%")
    print(f"'d' rate in B: {d_rate_b:.4f}%")

# All single 'd' by folio
print("\n--- 'd' by folio ---")
d_by_folio = d_in_a.groupby('folio').size().sort_values(ascending=False)
print(f"Total folios with 'd': {len(d_by_folio)}")
print(f"Top folios with 'd': {d_by_folio.head(15).to_dict()}")

# 'd' by section
print("\n--- 'd' by section ---")
d_by_section = d_in_a.groupby('section').size()
print(d_by_section.to_dict())

# 'd' by line position
print("\n--- 'd' line position analysis ---")
d_line_initial = d_in_a[d_in_a['line_initial'] == 1]
d_line_final = d_in_a[d_in_a['line_final'] == 1]
print(f"'d' line-initial: {len(d_line_initial)} ({100*len(d_line_initial)/len(d_in_a) if len(d_in_a)>0 else 0:.1f}%)")
print(f"'d' line-final: {len(d_line_final)} ({100*len(d_line_final)/len(d_in_a) if len(d_in_a)>0 else 0:.1f}%)")

# What tokens surround 'd'?
print("\n--- Tokens surrounding 'd' in A ---")
# Need to work with line-level context
# Group by folio, line_number and get sequence

def get_surrounding_context(df, target_word, window=1):
    """Get tokens before and after target word"""
    before_tokens = Counter()
    after_tokens = Counter()

    for (folio, line), group in df.groupby(['folio', 'line_number']):
        words = group.sort_values('line_initial', ascending=False)['word'].tolist()
        for i, w in enumerate(words):
            if str(w) == target_word:
                if i > 0:
                    before_tokens[str(words[i-1])] += 1
                if i < len(words) - 1:
                    after_tokens[str(words[i+1])] += 1

    return before_tokens, after_tokens

before_d, after_d = get_surrounding_context(df_a, 'd', window=1)
print(f"\nTokens BEFORE 'd' (top 15): {before_d.most_common(15)}")
print(f"\nTokens AFTER 'd' (top 15): {after_d.most_common(15)}")

# ============================================================================
# 2. SIMPLEX vs COMPLEX DISTRIBUTION
# ============================================================================
print("\n" + "=" * 80)
print("2. SIMPLEX vs COMPLEX HT DISTRIBUTION")
print("=" * 80)

# In A
simplex_a = ht_a[ht_a['ht_complexity'] == 'simplex']
complex_a = ht_a[ht_a['ht_complexity'] == 'complex']

print(f"\nIn Currier A:")
print(f"  Simplex HT (1-2 chars): {len(simplex_a)} ({100*len(simplex_a)/len(ht_a) if len(ht_a)>0 else 0:.1f}%)")
print(f"  Complex HT (3+ chars): {len(complex_a)} ({100*len(complex_a)/len(ht_a) if len(ht_a)>0 else 0:.1f}%)")

# What are the simplex forms?
print(f"\nSimplex HT forms in A:")
simplex_forms_a = Counter(simplex_a['word'].tolist())
print(f"  {simplex_forms_a.most_common(20)}")

# What are the most common complex forms?
print(f"\nTop complex HT forms in A:")
complex_forms_a = Counter(complex_a['word'].tolist())
print(f"  {complex_forms_a.most_common(20)}")

# In B for comparison
simplex_b = ht_b[ht_b['ht_complexity'] == 'simplex']
complex_b = ht_b[ht_b['ht_complexity'] == 'complex']

print(f"\nIn Currier B:")
print(f"  Simplex HT (1-2 chars): {len(simplex_b)} ({100*len(simplex_b)/len(ht_b) if len(ht_b)>0 else 0:.1f}%)")
print(f"  Complex HT (3+ chars): {len(complex_b)} ({100*len(complex_b)/len(ht_b) if len(ht_b)>0 else 0:.1f}%)")

# Position analysis for simplex vs complex
print("\n--- Simplex vs Complex Position Analysis in A ---")
simplex_line_initial = simplex_a[simplex_a['line_initial'] == 1]
complex_line_initial = complex_a[complex_a['line_initial'] == 1]
print(f"Simplex line-initial: {len(simplex_line_initial)} ({100*len(simplex_line_initial)/len(simplex_a) if len(simplex_a)>0 else 0:.1f}%)")
print(f"Complex line-initial: {len(complex_line_initial)} ({100*len(complex_line_initial)/len(complex_a) if len(complex_a)>0 else 0:.1f}%)")

simplex_line_final = simplex_a[simplex_a['line_final'] == 1]
complex_line_final = complex_a[complex_a['line_final'] == 1]
print(f"Simplex line-final: {len(simplex_line_final)} ({100*len(simplex_line_final)/len(simplex_a) if len(simplex_a)>0 else 0:.1f}%)")
print(f"Complex line-final: {len(complex_line_final)} ({100*len(complex_line_final)/len(complex_a) if len(complex_a)>0 else 0:.1f}%)")

# ============================================================================
# 3. LABELING SUFFIX ANALYSIS (-or, -ol, -hy)
# ============================================================================
print("\n" + "=" * 80)
print("3. LABELING SUFFIX ANALYSIS (-or, -ol, -hy)")
print("=" * 80)

def has_labeling_suffix(word):
    """Check if word ends with A-style labeling suffix"""
    if pd.isna(word):
        return None
    w = str(word).strip()
    if w.endswith('or'):
        return '-or'
    elif w.endswith('ol'):
        return '-ol'
    elif w.endswith('hy'):
        return '-hy'
    return None

# Apply to HT tokens in A
ht_a_copy = ht_a.copy()
ht_a_copy['labeling_suffix'] = ht_a_copy['word'].apply(has_labeling_suffix)

# Count suffixes
suffix_counts = ht_a_copy[ht_a_copy['labeling_suffix'].notna()].groupby('labeling_suffix').size()
print(f"\nLabeling suffix counts in A HT:")
print(suffix_counts.to_dict())

# Total with labeling suffix
total_with_suffix = len(ht_a_copy[ht_a_copy['labeling_suffix'].notna()])
print(f"\nTotal HT tokens with labeling suffix in A: {total_with_suffix} ({100*total_with_suffix/len(ht_a) if len(ht_a)>0 else 0:.1f}%)")

# Position analysis for labeling suffix tokens
print("\n--- Labeling suffix position analysis ---")
for suffix in ['-or', '-ol', '-hy']:
    suffix_tokens = ht_a_copy[ht_a_copy['labeling_suffix'] == suffix]
    if len(suffix_tokens) > 0:
        line_initial = len(suffix_tokens[suffix_tokens['line_initial'] == 1])
        line_final = len(suffix_tokens[suffix_tokens['line_final'] == 1])
        print(f"\n{suffix}:")
        print(f"  Total: {len(suffix_tokens)}")
        print(f"  Line-initial: {line_initial} ({100*line_initial/len(suffix_tokens):.1f}%)")
        print(f"  Line-final: {line_final} ({100*line_final/len(suffix_tokens):.1f}%)")
        print(f"  Examples: {Counter(suffix_tokens['word'].tolist()).most_common(10)}")

# Compare with B's process suffixes
def has_process_suffix(word):
    """Check for B-style process suffix"""
    if pd.isna(word):
        return None
    w = str(word).strip()
    if w.endswith('edy'):
        return '-edy'
    elif w.endswith('dy'):
        return '-dy'
    return None

ht_b_copy = ht_b.copy()
ht_b_copy['process_suffix'] = ht_b_copy['word'].apply(has_process_suffix)
print(f"\nProcess suffix counts in B HT:")
print(ht_b_copy[ht_b_copy['process_suffix'].notna()].groupby('process_suffix').size().to_dict())

# ============================================================================
# 4. A-ONLY HT FORMS
# ============================================================================
print("\n" + "=" * 80)
print("4. A-ONLY HT FORMS")
print("=" * 80)

# Get unique HT forms in each system
ht_forms_a = set(ht_a['word'].dropna().unique())
ht_forms_b = set(ht_b['word'].dropna().unique())

# A-only forms
a_only_ht = ht_forms_a - ht_forms_b
print(f"\nHT forms unique to A: {len(a_only_ht)}")
print(f"HT forms unique to B: {len(ht_forms_b - ht_forms_a)}")
print(f"Shared HT forms: {len(ht_forms_a & ht_forms_b)}")

# List A-only forms sorted by length
a_only_sorted = sorted(a_only_ht, key=lambda x: (len(x), x))
print(f"\nA-only HT forms (sorted by length):")
print(f"  {a_only_sorted[:60]}")

# Analyze morphological patterns of A-only forms
print("\n--- Morphological analysis of A-only HT forms ---")

# By length
length_dist = Counter(len(f) for f in a_only_ht)
print(f"\nLength distribution: {dict(sorted(length_dist.items()))}")

# By starting pattern
starting_patterns = Counter()
for f in a_only_ht:
    if len(f) >= 2:
        starting_patterns[f[:2]] += 1
    else:
        starting_patterns[f] += 1
print(f"\nStarting patterns (first 2 chars): {starting_patterns.most_common(15)}")

# By ending pattern
ending_patterns = Counter()
for f in a_only_ht:
    if len(f) >= 2:
        ending_patterns[f[-2:]] += 1
    else:
        ending_patterns[f] += 1
print(f"\nEnding patterns (last 2 chars): {ending_patterns.most_common(15)}")

# Where do A-only forms appear?
print("\n--- Where do A-only HT forms cluster? ---")
a_only_occurrences = ht_a[ht_a['word'].isin(a_only_ht)]
print(f"Total A-only HT occurrences: {len(a_only_occurrences)}")

# By folio
a_only_by_folio = a_only_occurrences.groupby('folio').size().sort_values(ascending=False)
print(f"\nA-only HT by folio (top 15): {a_only_by_folio.head(15).to_dict()}")

# By section
a_only_by_section = a_only_occurrences.groupby('section').size()
print(f"\nA-only HT by section: {a_only_by_section.to_dict()}")

# ============================================================================
# 5. TEST: SIMPLEX = LABEL vs COMPLEX = FILLER
# ============================================================================
print("\n" + "=" * 80)
print("5. TEST: SIMPLEX = LABEL vs COMPLEX = FILLER HYPOTHESIS")
print("=" * 80)

print("""
HYPOTHESIS:
- Simplex HT (y, d, r, etc.) function as labels/markers
- Complex HT (ykal, yor, etc.) function as fillers

Predictions:
- Labels should appear at entry boundaries (line-initial/final)
- Fillers should be distributed more uniformly
- Labels should be more stereotyped in position
- Fillers should have more variation
""")

# Test 1: Position stereotypy
print("\n--- Test 1: Position Stereotypy ---")

def calculate_position_entropy(tokens_df):
    """Calculate entropy of position distribution"""
    from math import log2
    total = len(tokens_df)
    if total == 0:
        return 0
    line_initial = len(tokens_df[tokens_df['line_initial'] == 1])
    line_final = len(tokens_df[tokens_df['line_final'] == 1])
    middle = total - line_initial - line_final

    probs = []
    for count in [line_initial, line_final, middle]:
        if count > 0:
            p = count / total
            probs.append(p)

    if len(probs) == 0:
        return 0
    return -sum(p * log2(p) for p in probs if p > 0)

simplex_entropy = calculate_position_entropy(simplex_a)
complex_entropy = calculate_position_entropy(complex_a)

print(f"Simplex position entropy: {simplex_entropy:.3f}")
print(f"Complex position entropy: {complex_entropy:.3f}")
print(f"(Lower entropy = more stereotyped position)")

if simplex_entropy < complex_entropy:
    print("RESULT: Simplex IS more position-stereotyped (supports label hypothesis)")
else:
    print("RESULT: Simplex is NOT more position-stereotyped (contradicts label hypothesis)")

# Test 2: Section preference
print("\n--- Test 2: Section Preference ---")
simplex_by_section = simplex_a.groupby('section').size()
complex_by_section = complex_a.groupby('section').size()
print(f"Simplex by section: {simplex_by_section.to_dict()}")
print(f"Complex by section: {complex_by_section.to_dict()}")

# Test 3: Context variety
print("\n--- Test 3: Context Variety ---")

# What follows simplex vs complex HT?
before_simplex, after_simplex = get_surrounding_context(df_a, None, window=1)
simplex_words = set(simplex_a['word'].dropna().unique())
complex_words = set(complex_a['word'].dropna().unique())

# Context after simplex forms
after_simplex_context = Counter()
after_complex_context = Counter()

for (folio, line), group in df_a.groupby(['folio', 'line_number']):
    words = group.sort_values('line_initial', ascending=False)['word'].tolist()
    for i, w in enumerate(words):
        if str(w) in simplex_words and i < len(words) - 1:
            after_simplex_context[str(words[i+1])] += 1
        elif str(w) in complex_words and i < len(words) - 1:
            after_complex_context[str(words[i+1])] += 1

print(f"\nUnique tokens following simplex HT: {len(after_simplex_context)}")
print(f"Unique tokens following complex HT: {len(after_complex_context)}")
print(f"\nTop tokens following simplex: {after_simplex_context.most_common(10)}")
print(f"Top tokens following complex: {after_complex_context.most_common(10)}")

# Test 4: Individual atom analysis
print("\n--- Test 4: Individual Atom Analysis ---")
atoms = ['y', 'd', 'r', 'f']
for atom in atoms:
    atom_tokens = df_a[df_a['word'] == atom]
    if len(atom_tokens) > 0:
        line_init = len(atom_tokens[atom_tokens['line_initial'] == 1])
        line_fin = len(atom_tokens[atom_tokens['line_final'] == 1])
        print(f"\n'{atom}' in A:")
        print(f"  Total: {len(atom_tokens)}")
        print(f"  Line-initial: {line_init} ({100*line_init/len(atom_tokens):.1f}%)")
        print(f"  Line-final: {line_fin} ({100*line_fin/len(atom_tokens):.1f}%)")

        # Section distribution
        by_section = atom_tokens.groupby('section').size()
        print(f"  By section: {by_section.to_dict()}")

# Test 5: Enrichment comparison A vs B
print("\n--- Test 5: A vs B Enrichment for Key Atoms ---")
for atom in atoms:
    count_a = len(df_a[df_a['word'] == atom])
    count_b = len(df_b[df_b['word'] == atom])
    rate_a = 100 * count_a / len(df_a) if len(df_a) > 0 else 0
    rate_b = 100 * count_b / len(df_b) if len(df_b) > 0 else 0
    enrichment = rate_a / rate_b if rate_b > 0 else float('inf')
    print(f"'{atom}': A={count_a} ({rate_a:.3f}%), B={count_b} ({rate_b:.3f}%), A/B enrichment={enrichment:.2f}x")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"""
KEY FINDINGS:

1. THE 'd' ATOM:
   - 'd' occurrences in A: {len(d_in_a)}
   - 'd' line-initial rate: {100*len(d_line_initial)/len(d_in_a) if len(d_in_a)>0 else 0:.1f}%
   - Top tokens before 'd': {before_d.most_common(5)}
   - Top tokens after 'd': {after_d.most_common(5)}

2. SIMPLEX vs COMPLEX:
   - Simplex (1-2 char) in A: {len(simplex_a)} ({100*len(simplex_a)/len(ht_a) if len(ht_a)>0 else 0:.1f}%)
   - Complex (3+ char) in A: {len(complex_a)} ({100*len(complex_a)/len(ht_a) if len(ht_a)>0 else 0:.1f}%)
   - Position entropy: simplex={simplex_entropy:.3f}, complex={complex_entropy:.3f}

3. LABELING SUFFIXES:
   - -or: {suffix_counts.get('-or', 0)} tokens
   - -ol: {suffix_counts.get('-ol', 0)} tokens
   - -hy: {suffix_counts.get('-hy', 0)} tokens

4. A-ONLY HT FORMS:
   - Unique to A: {len(a_only_ht)} forms
   - Length distribution: {dict(sorted(length_dist.items()))}

5. LABEL vs FILLER HYPOTHESIS:
   - Simplex more position-stereotyped: {simplex_entropy < complex_entropy}
   - Supports categorical labeling function: {'YES' if simplex_entropy < complex_entropy else 'NEEDS MORE EVIDENCE'}
""")
