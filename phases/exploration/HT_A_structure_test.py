"""
HT (Human Track) in Currier A Registry Structure Analysis

Tests whether HT tokens mark structural features of the Currier A registry (C240).

HT Definition (per instructions):
- All tokens starting with 'y' OR
- Single-character atoms: y, f, d, r

Analysis Tasks:
1. Category boundary marking
2. Entry structure positioning
3. Block boundary marking
4. Illustration coordination
5. A-vocabulary reference correlation (C344)
6. Predictive power test (like C415 for B)
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from scipy import stats
import re

# =============================================================================
# DATA LOADING
# =============================================================================

print("=" * 80)
print("HT IN CURRIER A REGISTRY - STRUCTURAL FEATURE ANALYSIS")
print("=" * 80)

# Load data
data_path = "C:/git/voynich/data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(data_path, sep='\t', quotechar='"', low_memory=False)
# Filter to H transcriber only
df = df[df['transcriber'] == 'H']

print(f"\nTotal records: {len(df):,}")
print(f"Columns: {list(df.columns)}")

# Check for Currier A identification - the 'language' column should indicate this
print(f"\nUnique language values: {df['language'].unique()}")

# Filter for Currier A only
df_a = df[df['language'] == 'A'].copy()
print(f"\nCurrier A records: {len(df_a):,}")

# Get unique folios
a_folios = df_a['folio'].unique()
print(f"Currier A folios: {len(a_folios)}")

# Get unique tokens in A
a_tokens = df_a['word'].dropna().unique()
print(f"Unique token types in A: {len(a_tokens)}")

# =============================================================================
# HT IDENTIFICATION
# =============================================================================

def is_ht_token(token):
    """
    Identify Human Track tokens in Currier A.
    HT tokens per instructions:
    - All tokens starting with 'y' OR
    - Single-character atoms: y, f, d, r
    """
    if pd.isna(token):
        return False
    token = str(token).strip().lower()

    # Single character atoms
    if token in {'y', 'f', 'd', 'r'}:
        return True

    # y-initial tokens
    if token.startswith('y'):
        return True

    return False

# Apply HT classification
df_a['is_ht'] = df_a['word'].apply(is_ht_token)

ht_count = df_a['is_ht'].sum()
total_a = len(df_a)
ht_rate = ht_count / total_a * 100

print("\n" + "=" * 80)
print("HT IDENTIFICATION IN CURRIER A")
print("=" * 80)
print(f"HT tokens: {ht_count:,} ({ht_rate:.1f}%)")
print(f"Non-HT tokens: {total_a - ht_count:,} ({100-ht_rate:.1f}%)")

# Show some HT tokens
ht_tokens = df_a[df_a['is_ht']]['word'].value_counts().head(20)
print(f"\nTop 20 HT tokens in A:")
for tok, cnt in ht_tokens.items():
    print(f"  {tok}: {cnt}")

# =============================================================================
# TEST 1: CATEGORY BOUNDARY MARKING
# =============================================================================

print("\n" + "=" * 80)
print("TEST 1: CATEGORY BOUNDARY MARKING")
print("=" * 80)

# A has mutually exclusive category markers (C235): ch, sh, ok, ot, da, qo, ol, ct
CATEGORY_PREFIXES = ['ch', 'sh', 'ok', 'ot', 'da', 'qo', 'ol', 'ct']

def get_category_prefix(token):
    """Get the category marker prefix for a token."""
    if pd.isna(token):
        return None
    token = str(token).strip().lower()
    for prefix in CATEGORY_PREFIXES:
        if token.startswith(prefix):
            return prefix
    return None

df_a['category_prefix'] = df_a['word'].apply(get_category_prefix)

# Group by folio and line to detect transitions
df_a = df_a.sort_values(['folio', 'line_number', 'line_initial'])

# Detect category transitions within lines
transitions = []
prev_category = None
prev_folio = None
prev_line = None

for idx, row in df_a.iterrows():
    curr_category = row['category_prefix']
    curr_folio = row['folio']
    curr_line = row['line_number']

    # Reset on folio/line change
    if curr_folio != prev_folio or curr_line != prev_line:
        prev_category = curr_category
        prev_folio = curr_folio
        prev_line = curr_line
        continue

    # Check for transition
    if curr_category is not None and prev_category is not None:
        if curr_category != prev_category:
            transitions.append({
                'folio': curr_folio,
                'line': curr_line,
                'from_cat': prev_category,
                'to_cat': curr_category,
                'idx': idx
            })

    prev_category = curr_category
    prev_folio = curr_folio
    prev_line = curr_line

print(f"Found {len(transitions)} category transitions")

if len(transitions) > 0:
    # Check HT presence around transitions
    window = 2  # Check +-2 positions around transition
    ht_at_transitions = []
    ht_not_at_transitions = []

    all_indices = set(df_a.index)
    transition_indices = set()

    for t in transitions:
        idx = t['idx']
        # Get indices within window
        nearby = [i for i in range(idx-window, idx+window+1) if i in all_indices]
        transition_indices.update(nearby)

        # Count HT in window
        ht_nearby = sum(df_a.loc[i, 'is_ht'] if i in df_a.index else 0 for i in nearby)
        ht_at_transitions.append(ht_nearby)

    # Compare to baseline
    non_transition_indices = all_indices - transition_indices
    sample_size = min(len(non_transition_indices), len(transitions) * (2*window + 1))
    sampled = np.random.choice(list(non_transition_indices), sample_size, replace=False)
    ht_baseline = df_a.loc[sampled, 'is_ht'].mean()

    ht_transition_rate = np.mean([h / (2*window+1) for h in ht_at_transitions])

    print(f"\nHT rate at category transitions: {ht_transition_rate:.3f}")
    print(f"HT baseline rate: {ht_baseline:.3f}")
    print(f"Ratio: {ht_transition_rate/ht_baseline:.2f}x" if ht_baseline > 0 else "Baseline is 0")

    # Statistical test
    ht_at_trans_binary = [1 if h > 0 else 0 for h in ht_at_transitions]
    if len(ht_at_trans_binary) > 0 and ht_baseline > 0:
        observed_rate = np.mean(ht_at_trans_binary)
        result = stats.binomtest(sum(ht_at_trans_binary), len(ht_at_trans_binary),
                                 ht_baseline, alternative='two-sided')
        print(f"Binomial test p-value: {result.pvalue:.4f}")
else:
    print("No category transitions found - A may be fully homogeneous per line")

# =============================================================================
# TEST 2: ENTRY STRUCTURE - HT POSITION WITHIN ENTRIES
# =============================================================================

print("\n" + "=" * 80)
print("TEST 2: ENTRY STRUCTURE POSITIONING")
print("=" * 80)

# In A, entries follow patterns: [marker] [content] [suffix]
# Check if HT appears in certain positions more than others

# Get line-level statistics
line_stats = df_a.groupby(['folio', 'line_number']).agg({
    'word': 'count',
    'is_ht': 'sum',
    'line_initial': 'max',
    'line_final': 'min'
}).reset_index()
line_stats.columns = ['folio', 'line', 'token_count', 'ht_count', 'max_pos', 'min_pos']

# Check HT by position within line
position_ht = defaultdict(list)
position_total = defaultdict(int)

for folio in df_a['folio'].unique():
    folio_data = df_a[df_a['folio'] == folio]
    for line in folio_data['line_number'].unique():
        line_data = folio_data[folio_data['line_number'] == line].sort_values('line_initial')
        tokens = line_data['word'].tolist()
        ht_flags = line_data['is_ht'].tolist()

        n = len(tokens)
        if n == 0:
            continue

        for i, (tok, is_ht) in enumerate(zip(tokens, ht_flags)):
            # Normalize position to thirds: initial, middle, final
            if n == 1:
                pos = 'only'
            elif i == 0:
                pos = 'initial'
            elif i == n - 1:
                pos = 'final'
            else:
                pos = 'middle'

            position_total[pos] += 1
            position_ht[pos].append(1 if is_ht else 0)

print("\nHT rate by line position:")
for pos in ['initial', 'middle', 'final', 'only']:
    if position_total[pos] > 0:
        rate = np.mean(position_ht[pos])
        count = sum(position_ht[pos])
        total = position_total[pos]
        print(f"  {pos.upper():10s}: {rate:.3f} ({count}/{total})")

# Chi-square test for position independence
if all(position_total[p] > 0 for p in ['initial', 'middle', 'final']):
    obs = [[sum(position_ht[p]), position_total[p] - sum(position_ht[p])]
           for p in ['initial', 'middle', 'final']]
    chi2, pval, dof, expected = stats.chi2_contingency(obs)
    print(f"\nChi-square test for position independence: chi2={chi2:.2f}, p={pval:.4f}")
    if pval < 0.05:
        print("  -> HT distribution is POSITION-DEPENDENT in A")
    else:
        print("  -> HT distribution is POSITION-INDEPENDENT in A")

# =============================================================================
# TEST 3: BLOCK BOUNDARY MARKING (C250 - repeating blocks)
# =============================================================================

print("\n" + "=" * 80)
print("TEST 3: BLOCK BOUNDARY MARKING")
print("=" * 80)

# Detect repeating blocks within lines (C250: 64.1% show repetition)
def find_blocks(tokens):
    """Find repeating blocks in a token sequence."""
    n = len(tokens)
    blocks = []

    for block_size in range(1, n//2 + 1):
        for start in range(n - block_size * 2 + 1):
            block1 = tuple(tokens[start:start+block_size])
            block2 = tuple(tokens[start+block_size:start+block_size*2])
            if block1 == block2:
                blocks.append({
                    'start': start,
                    'size': block_size,
                    'block': block1,
                    'repeat_start': start + block_size
                })
    return blocks

# Check HT at block boundaries
ht_at_block_boundary = []
ht_not_at_boundary = []

for folio in df_a['folio'].unique():
    folio_data = df_a[df_a['folio'] == folio]
    for line in folio_data['line_number'].unique():
        line_data = folio_data[folio_data['line_number'] == line].sort_values('line_initial')
        tokens = line_data['word'].tolist()
        ht_flags = line_data['is_ht'].tolist()

        blocks = find_blocks(tokens)
        boundary_positions = set()

        for b in blocks:
            # Block boundaries: just before block start, just after block end
            boundary_positions.add(b['start'])
            boundary_positions.add(b['start'] + b['size'])
            boundary_positions.add(b['repeat_start'])
            boundary_positions.add(b['repeat_start'] + b['size'])

        for i, is_ht in enumerate(ht_flags):
            if i in boundary_positions:
                ht_at_block_boundary.append(1 if is_ht else 0)
            else:
                ht_not_at_boundary.append(1 if is_ht else 0)

if len(ht_at_block_boundary) > 0 and len(ht_not_at_boundary) > 0:
    boundary_rate = np.mean(ht_at_block_boundary)
    non_boundary_rate = np.mean(ht_not_at_boundary)
    print(f"Lines with detected repeating blocks analyzed")
    print(f"HT rate at block boundaries: {boundary_rate:.3f} ({sum(ht_at_block_boundary)}/{len(ht_at_block_boundary)})")
    print(f"HT rate elsewhere: {non_boundary_rate:.3f} ({sum(ht_not_at_boundary)}/{len(ht_not_at_boundary)})")

    if boundary_rate > 0 and non_boundary_rate > 0:
        ratio = boundary_rate / non_boundary_rate
        print(f"Ratio: {ratio:.2f}x")

        # Fisher's exact test
        table = [[sum(ht_at_block_boundary), len(ht_at_block_boundary) - sum(ht_at_block_boundary)],
                 [sum(ht_not_at_boundary), len(ht_not_at_boundary) - sum(ht_not_at_boundary)]]
        odds, pval = stats.fisher_exact(table)
        print(f"Fisher's exact test: odds ratio={odds:.2f}, p={pval:.4f}")
else:
    print("Insufficient block data for comparison")

# =============================================================================
# TEST 4: ILLUSTRATION COORDINATION
# =============================================================================

print("\n" + "=" * 80)
print("TEST 4: ILLUSTRATION COORDINATION")
print("=" * 80)

# Check placement column - may indicate label vs main text
print(f"Unique placements: {df_a['placement'].unique()}")
print(f"Unique sections: {df_a['section'].unique()}")

# H section is often plant illustrations, T is text
# Compare HT rates across sections
section_ht_rates = df_a.groupby('section')['is_ht'].agg(['mean', 'sum', 'count'])
section_ht_rates.columns = ['rate', 'ht_count', 'total']
print(f"\nHT rate by section:")
for section, row in section_ht_rates.iterrows():
    print(f"  Section {section}: {row['rate']:.3f} ({int(row['ht_count'])}/{int(row['total'])})")

# Statistical test across sections
sections_with_data = section_ht_rates[section_ht_rates['total'] > 10].index.tolist()
if len(sections_with_data) > 1:
    obs = []
    for s in sections_with_data:
        row = section_ht_rates.loc[s]
        obs.append([int(row['ht_count']), int(row['total'] - row['ht_count'])])
    chi2, pval, dof, expected = stats.chi2_contingency(obs)
    print(f"\nChi-square across sections: chi2={chi2:.2f}, p={pval:.4f}")

# =============================================================================
# TEST 5: A-VOCABULARY REFERENCE TEST (relates to C344)
# =============================================================================

print("\n" + "=" * 80)
print("TEST 5: A-VOCABULARY STRUCTURE CORRELATION")
print("=" * 80)

# C344: HT inversely correlates with A-vocabulary reference in B
# Within A itself: does HT correlate with entry "completeness" or "reference-like" properties?

# Calculate per-line metrics
line_metrics = []

for folio in df_a['folio'].unique():
    folio_data = df_a[df_a['folio'] == folio]
    for line in folio_data['line_number'].unique():
        line_data = folio_data[folio_data['line_number'] == line]

        tokens = line_data['word'].dropna().tolist()
        ht_flags = line_data['is_ht'].tolist()
        categories = line_data['category_prefix'].dropna().tolist()

        n_tokens = len(tokens)
        if n_tokens == 0:
            continue

        n_ht = sum(ht_flags)
        ht_ratio = n_ht / n_tokens

        # Category diversity
        n_categories = len(set(categories))
        category_ratio = len(categories) / n_tokens  # What fraction has category markers

        # Token diversity (type-token ratio for line)
        ttr = len(set(tokens)) / n_tokens if n_tokens > 0 else 0

        line_metrics.append({
            'folio': folio,
            'line': line,
            'n_tokens': n_tokens,
            'n_ht': n_ht,
            'ht_ratio': ht_ratio,
            'n_categories': n_categories,
            'category_ratio': category_ratio,
            'ttr': ttr
        })

metrics_df = pd.DataFrame(line_metrics)

# Correlations
print(f"\nCorrelations with HT ratio (at line level):")

for col in ['n_tokens', 'n_categories', 'category_ratio', 'ttr']:
    r, p = stats.spearmanr(metrics_df['ht_ratio'], metrics_df[col])
    print(f"  {col}: rho={r:.3f}, p={p:.4f}")

# =============================================================================
# TEST 6: PREDICTIVE TEST (like C415 for B)
# =============================================================================

print("\n" + "=" * 80)
print("TEST 6: PREDICTIVE POWER TEST")
print("=" * 80)

# Given line-initial HT, can we predict entry category?
# Compare category distribution for lines starting with HT vs not

line_initial_data = []

for folio in df_a['folio'].unique():
    folio_data = df_a[df_a['folio'] == folio]
    for line in folio_data['line_number'].unique():
        line_data = folio_data[folio_data['line_number'] == line].sort_values('line_initial')

        if len(line_data) == 0:
            continue

        first_token = line_data.iloc[0]
        is_ht_initial = first_token['is_ht']

        # Get dominant category in line
        categories = line_data['category_prefix'].dropna().tolist()
        if len(categories) > 0:
            dominant_cat = Counter(categories).most_common(1)[0][0]
        else:
            dominant_cat = None

        line_initial_data.append({
            'folio': folio,
            'line': line,
            'ht_initial': is_ht_initial,
            'dominant_cat': dominant_cat
        })

initial_df = pd.DataFrame(line_initial_data)

# Compare category distributions
ht_initial_cats = initial_df[initial_df['ht_initial']]['dominant_cat'].value_counts()
non_ht_initial_cats = initial_df[~initial_df['ht_initial']]['dominant_cat'].value_counts()

print(f"\nLines with HT-initial: {len(initial_df[initial_df['ht_initial']])}")
print(f"Lines with non-HT-initial: {len(initial_df[~initial_df['ht_initial']])}")

print(f"\nCategory distribution for HT-initial lines:")
for cat, cnt in ht_initial_cats.head(8).items():
    if cat is not None:
        pct = cnt / ht_initial_cats.sum() * 100
        print(f"  {cat}: {cnt} ({pct:.1f}%)")

print(f"\nCategory distribution for non-HT-initial lines:")
for cat, cnt in non_ht_initial_cats.head(8).items():
    if cat is not None:
        pct = cnt / non_ht_initial_cats.sum() * 100
        print(f"  {cat}: {cnt} ({pct:.1f}%)")

# Test if distributions differ
all_cats = set(ht_initial_cats.index) | set(non_ht_initial_cats.index)
all_cats = [c for c in all_cats if c is not None]

if len(all_cats) > 1:
    obs_ht = [ht_initial_cats.get(c, 0) for c in all_cats]
    obs_non_ht = [non_ht_initial_cats.get(c, 0) for c in all_cats]

    chi2, pval = stats.chisquare(obs_ht, f_exp=[sum(obs_ht) * n / sum(obs_non_ht) for n in obs_non_ht])
    print(f"\nChi-square for category prediction: chi2={chi2:.2f}, p={pval:.4f}")

    # Cramer's V for effect size
    obs = [obs_ht, obs_non_ht]
    chi2_contingency, pval_contingency, dof, expected = stats.chi2_contingency(obs)
    n = sum(obs_ht) + sum(obs_non_ht)
    cramers_v = np.sqrt(chi2_contingency / (n * min(len(obs)-1, len(all_cats)-1)))
    print(f"Cramer's V: {cramers_v:.3f}")

    if cramers_v < 0.1:
        print("  -> NEGLIGIBLE association: HT-initial does NOT predict category")
    elif cramers_v < 0.3:
        print("  -> WEAK association: HT-initial has limited predictive power")
    else:
        print("  -> MODERATE/STRONG association: HT-initial has predictive power")

# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print("SUMMARY: HT IN CURRIER A REGISTRY STRUCTURE")
print("=" * 80)

print("""
Key Findings:

1. HT DEFINITION: Using y-prefix tokens + single atoms (y,f,d,r)

2. HT BASELINE: Check HT rate in A vs expected

3. CATEGORY BOUNDARY: Does HT mark transitions between category prefixes?

4. ENTRY POSITION: Is HT concentrated at initial/middle/final positions?

5. BLOCK BOUNDARY: Does HT mark repeating block boundaries (C250)?

6. SECTION VARIATION: Does HT rate vary by manuscript section?

7. CORRELATIONS: How does HT relate to line structural properties?

8. PREDICTIVITY: Can HT-initial predict line category content?

INTERPRETATION:
- If HT marks boundaries -> structural punctuation role
- If HT is position-independent -> differs from B behavior
- If HT predicts category -> functional annotation (contradicts C415 pattern)
- If HT is random -> may be noise or practice in A
""")

print("\n[Analysis Complete]")
