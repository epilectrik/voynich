"""
Grammar -> HT Trigger Deep Analysis V2 (C413 Extension)
=======================================================

CORRECTED VERSION: Uses the actual HT prefix definitions from C347/C348:
- HT tokens: y-initial tokens AND tokens starting with op-, pc-, do-, ta-, sa-, yk-, etc.
- EARLY prefixes: op-, pc-, do- (from C348)
- LATE prefixes: ta- (from C348)

Questions:
1. Full transition matrix for all grammar prefixes
2. Is the pattern bidirectional or one-way?
3. Distance effects (adjacent vs gaps)
4. What's special about ch-?
5. State vs transition annotation hypothesis
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# DATA LOADING AND DEFINITIONS
# =============================================================================

DATA_PATH = "C:/git/voynich/data/transcriptions/interlinear_full_words.txt"

# HT prefix classes (from C347/C348)
# These are NON-y-initial HT prefixes
HT_EARLY_PREFIXES = ['op', 'pc', 'do']  # EARLY phase markers
HT_LATE_PREFIXES = ['ta']  # LATE phase markers

# Y-initial prefixes (treated separately for some analyses)
Y_EARLY_PREFIXES = ['yk', 'yp', 'ypc']  # y + early pattern
Y_LATE_PREFIXES = ['yt', 'yta', 'ys']  # y + late pattern

# Grammar prefixes to analyze
GRAMMAR_PREFIXES = ['ch', 'sh', 'qo', 'ok', 'ol', 'or', 'ar', 'al', 'ot', 'da', 'sa']

# Single-char HT atoms
HT_ATOMS = set(['y', 'f', 'd', 'r'])

def load_data():
    """Load the interlinear transcription data."""
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
    # Filter to Currier B
    df_b = df[df['language'] == 'B'].copy()
    print(f"Loaded {len(df_b)} Currier B tokens")
    return df_b

def is_ht_token(word):
    """Check if token is HT (non-grammar prefix)."""
    if pd.isna(word) or not isinstance(word, str):
        return False
    word = word.strip('"').lower()

    # Single-char atoms
    if word in HT_ATOMS:
        return True

    # Y-initial (most HT)
    if word.startswith('y'):
        return True

    # Non-y HT prefixes
    for prefix in HT_EARLY_PREFIXES + HT_LATE_PREFIXES:
        if word.startswith(prefix):
            return True

    return False

def get_ht_prefix_class(word, include_y=True):
    """
    Classify HT token into EARLY/LATE/OTHER based on prefix.

    Args:
        word: The token
        include_y: If True, classify y-initial tokens too. If False, only non-y HT.
    """
    if pd.isna(word) or not isinstance(word, str):
        return None
    word = word.strip('"').lower()

    # Non-y HT prefixes (primary classification from C348)
    for prefix in HT_EARLY_PREFIXES:
        if word.startswith(prefix):
            return 'EARLY'

    for prefix in HT_LATE_PREFIXES:
        if word.startswith(prefix):
            return 'LATE'

    if not include_y:
        return None

    # Y-initial classification
    if not word.startswith('y'):
        return None

    # Single 'y' is neutral/other
    if word == 'y':
        return 'OTHER'

    # Y + late patterns
    for prefix in Y_LATE_PREFIXES:
        if word.startswith(prefix):
            return 'LATE'

    # Y + early patterns
    for prefix in Y_EARLY_PREFIXES:
        if word.startswith(prefix):
            return 'EARLY'

    # Other y-initial
    return 'OTHER'

def get_grammar_prefix(word):
    """Get grammar prefix from a token."""
    if pd.isna(word) or not isinstance(word, str):
        return None
    word = word.strip('"').lower()

    # Skip HT tokens
    if is_ht_token(word):
        return None

    # Check known grammar prefixes
    for prefix in sorted(GRAMMAR_PREFIXES, key=len, reverse=True):
        if word.startswith(prefix):
            return prefix

    return None

# =============================================================================
# ANALYSIS 1: FULL TRANSITION MATRIX (Primary HT only)
# =============================================================================

def build_transition_matrix_primary(df):
    """Build grammar prefix -> HT prefix class matrix using PRIMARY (non-y) HT only."""
    print("\n" + "="*80)
    print("ANALYSIS 1A: TRANSITION MATRIX (Non-Y HT Only)")
    print("Using C348 definitions: EARLY=op/pc/do, LATE=ta")
    print("="*80)

    # Get ordered tokens per line
    df_sorted = df.sort_values(['folio', 'line_number', 'line_initial'])

    # Track transitions
    transitions = defaultdict(lambda: defaultdict(int))
    baseline_ht_class = Counter()
    grammar_prefix_counts = Counter()

    # Process by folio/line
    for (folio, line), group in df_sorted.groupby(['folio', 'line_number']):
        words = group['word'].tolist()

        for i, word in enumerate(words):
            # Count baseline HT (non-y only)
            ht_class = get_ht_prefix_class(word, include_y=False)
            if ht_class:
                baseline_ht_class[ht_class] += 1

            # Check if current is grammar-prefixed
            gram_prefix = get_grammar_prefix(word)
            if gram_prefix:
                grammar_prefix_counts[gram_prefix] += 1
                # Look at next token
                if i + 1 < len(words):
                    next_word = words[i + 1]
                    next_ht_class = get_ht_prefix_class(next_word, include_y=False)
                    if next_ht_class:
                        transitions[gram_prefix][next_ht_class] += 1

    # Calculate baseline rates
    total_ht = sum(baseline_ht_class.values())
    baseline_rates = {k: v/total_ht for k, v in baseline_ht_class.items()}

    print(f"\nBaseline HT class distribution (NON-Y, n={total_ht}):")
    for cls, rate in sorted(baseline_rates.items()):
        print(f"  {cls}: {rate:.1%} ({baseline_ht_class[cls]})")

    # Build results table
    print(f"\n{'Grammar':<8} {'Count':<8} {'->EARLY':<12} {'->LATE':<12} {'LATE Enrich':<12} {'N Trans':<10}")
    print("-" * 62)

    results = []
    for gram in sorted(grammar_prefix_counts.keys(), key=lambda x: grammar_prefix_counts[x], reverse=True):
        trans = transitions[gram]
        total_trans = sum(trans.values())
        if total_trans < 5:
            continue

        early_rate = trans['EARLY'] / total_trans if total_trans > 0 else 0
        late_rate = trans['LATE'] / total_trans if total_trans > 0 else 0

        late_enrich = late_rate / baseline_rates.get('LATE', 0.01) if baseline_rates.get('LATE', 0) > 0 else 0
        early_enrich = early_rate / baseline_rates.get('EARLY', 0.01) if baseline_rates.get('EARLY', 0) > 0 else 0

        print(f"{gram:<8} {grammar_prefix_counts[gram]:<8} {early_rate:<12.1%} {late_rate:<12.1%} {late_enrich:<12.2f}x {total_trans:<10}")

        results.append({
            'grammar_prefix': gram,
            'count': grammar_prefix_counts[gram],
            'transitions': total_trans,
            'early_rate': early_rate,
            'late_rate': late_rate,
            'late_enrichment': late_enrich,
            'early_enrichment': early_enrich
        })

    return pd.DataFrame(results), baseline_rates

# =============================================================================
# ANALYSIS 1B: FULL TRANSITION MATRIX (All HT including Y)
# =============================================================================

def build_transition_matrix_all(df):
    """Build grammar prefix -> HT prefix class matrix using ALL HT."""
    print("\n" + "="*80)
    print("ANALYSIS 1B: TRANSITION MATRIX (All HT Including Y-Initial)")
    print("="*80)

    df_sorted = df.sort_values(['folio', 'line_number', 'line_initial'])

    transitions = defaultdict(lambda: defaultdict(int))
    baseline_ht_class = Counter()
    grammar_prefix_counts = Counter()

    for (folio, line), group in df_sorted.groupby(['folio', 'line_number']):
        words = group['word'].tolist()

        for i, word in enumerate(words):
            ht_class = get_ht_prefix_class(word, include_y=True)
            if ht_class:
                baseline_ht_class[ht_class] += 1

            gram_prefix = get_grammar_prefix(word)
            if gram_prefix:
                grammar_prefix_counts[gram_prefix] += 1
                if i + 1 < len(words):
                    next_word = words[i + 1]
                    next_ht_class = get_ht_prefix_class(next_word, include_y=True)
                    if next_ht_class:
                        transitions[gram_prefix][next_ht_class] += 1

    total_ht = sum(baseline_ht_class.values())
    baseline_rates = {k: v/total_ht for k, v in baseline_ht_class.items()}

    print(f"\nBaseline HT class distribution (ALL, n={total_ht}):")
    for cls, rate in sorted(baseline_rates.items()):
        print(f"  {cls}: {rate:.1%} ({baseline_ht_class[cls]})")

    print(f"\n{'Grammar':<8} {'Count':<8} {'->EARLY':<10} {'->LATE':<10} {'->OTHER':<10} {'LATE Enr':<10} {'N Trans':<8}")
    print("-" * 66)

    for gram in sorted(grammar_prefix_counts.keys(), key=lambda x: grammar_prefix_counts[x], reverse=True):
        trans = transitions[gram]
        total_trans = sum(trans.values())
        if total_trans < 10:
            continue

        early_rate = trans['EARLY'] / total_trans if total_trans > 0 else 0
        late_rate = trans['LATE'] / total_trans if total_trans > 0 else 0
        other_rate = trans['OTHER'] / total_trans if total_trans > 0 else 0

        late_enrich = late_rate / baseline_rates.get('LATE', 0.01)

        print(f"{gram:<8} {grammar_prefix_counts[gram]:<8} {early_rate:<10.1%} {late_rate:<10.1%} {other_rate:<10.1%} {late_enrich:<10.2f}x {total_trans:<8}")

    return baseline_rates

# =============================================================================
# ANALYSIS 2: BIDIRECTIONALITY TEST
# =============================================================================

def test_bidirectionality(df):
    """Test if HT prefixes predict following grammar prefixes."""
    print("\n" + "="*80)
    print("ANALYSIS 2: BIDIRECTIONALITY TEST")
    print("="*80)
    print("Question: Does HT -> Grammar direction also show association?")

    df_sorted = df.sort_values(['folio', 'line_number', 'line_initial'])

    forward_data = []  # Grammar -> HT
    backward_data = []  # HT -> Grammar

    for (folio, line), group in df_sorted.groupby(['folio', 'line_number']):
        words = group['word'].tolist()

        for i, word in enumerate(words):
            gram_prefix = get_grammar_prefix(word)
            ht_class = get_ht_prefix_class(word, include_y=False)

            # Forward: If grammar, what HT follows?
            if gram_prefix and i + 1 < len(words):
                next_ht_class = get_ht_prefix_class(words[i + 1], include_y=False)
                if next_ht_class:
                    forward_data.append((gram_prefix, next_ht_class))

            # Backward: If HT, what grammar follows?
            if ht_class and i + 1 < len(words):
                next_gram = get_grammar_prefix(words[i + 1])
                if next_gram:
                    backward_data.append((ht_class, next_gram))

    print(f"\n--- FORWARD DIRECTION: Grammar -> HT ---")
    print(f"N transitions: {len(forward_data)}")

    if len(forward_data) >= 10:
        forward_df = pd.DataFrame(forward_data, columns=['grammar', 'ht_class'])
        forward_table = pd.crosstab(forward_df['grammar'], forward_df['ht_class'])
        if forward_table.shape[0] > 1 and forward_table.shape[1] > 1:
            chi2_fwd, p_fwd, dof_fwd, _ = stats.chi2_contingency(forward_table)
            n_fwd = len(forward_data)
            v_fwd = np.sqrt(chi2_fwd / (n_fwd * (min(forward_table.shape) - 1)))
            print(f"Chi-square: {chi2_fwd:.2f}, p-value: {p_fwd:.2e}, Cramer's V: {v_fwd:.3f}")
        else:
            v_fwd = 0
            print("Insufficient categories for chi-square test")
    else:
        v_fwd = 0
        print("Insufficient data")

    print(f"\n--- BACKWARD DIRECTION: HT -> Grammar ---")
    print(f"N transitions: {len(backward_data)}")

    if len(backward_data) >= 10:
        backward_df = pd.DataFrame(backward_data, columns=['ht_class', 'grammar'])
        backward_table = pd.crosstab(backward_df['ht_class'], backward_df['grammar'])
        if backward_table.shape[0] > 1 and backward_table.shape[1] > 1:
            chi2_bwd, p_bwd, dof_bwd, _ = stats.chi2_contingency(backward_table)
            n_bwd = len(backward_data)
            v_bwd = np.sqrt(chi2_bwd / (n_bwd * (min(backward_table.shape) - 1)))
            print(f"Chi-square: {chi2_bwd:.2f}, p-value: {p_bwd:.2e}, Cramer's V: {v_bwd:.3f}")
        else:
            v_bwd = 0
            print("Insufficient categories for chi-square test")
    else:
        v_bwd = 0
        print("Insufficient data")

    print(f"\n--- COMPARISON ---")
    if v_fwd > 0 and v_bwd > 0:
        print(f"Forward (Grammar -> HT):  V = {v_fwd:.3f}")
        print(f"Backward (HT -> Grammar): V = {v_bwd:.3f}")
        ratio = v_fwd/v_bwd if v_bwd > 0 else float('inf')
        if v_fwd > v_bwd:
            print(f"Ratio: {ratio:.2f}x stronger forward (GRAMMAR CONTROLS HT)")
        else:
            print(f"Ratio: {1/ratio:.2f}x stronger backward")

    return v_fwd, v_bwd

# =============================================================================
# ANALYSIS 3: DISTANCE EFFECTS
# =============================================================================

def test_distance_effects(df):
    """Test if grammar trigger works at different distances."""
    print("\n" + "="*80)
    print("ANALYSIS 3: DISTANCE EFFECTS")
    print("="*80)
    print("Question: Does grammar -> HT trigger decay with distance?")
    print("Using NON-Y HT only (ta vs op/pc/do)")

    df_sorted = df.sort_values(['folio', 'line_number', 'line_initial'])

    # Track effects at different distances
    distance_data = {d: defaultdict(lambda: defaultdict(int)) for d in [1, 2, 3, 4, 5]}
    baseline_counts = {d: Counter() for d in [1, 2, 3, 4, 5]}

    for (folio, line), group in df_sorted.groupby(['folio', 'line_number']):
        words = group['word'].tolist()

        for i, word in enumerate(words):
            gram_prefix = get_grammar_prefix(word)

            for dist in [1, 2, 3, 4, 5]:
                if i + dist < len(words):
                    target_word = words[i + dist]
                    ht_class = get_ht_prefix_class(target_word, include_y=False)
                    if ht_class:
                        baseline_counts[dist][ht_class] += 1
                        if gram_prefix:
                            distance_data[dist][gram_prefix][ht_class] += 1

    print(f"\n{'Dist':<6} {'ch->LATE':<12} {'ch->EARLY':<12} {'sh->LATE':<12} {'sh->EARLY':<12} {'Baseline LATE':<14}")
    print("-" * 68)

    enrichments = []
    for dist in [1, 2, 3, 4, 5]:
        total_baseline = sum(baseline_counts[dist].values())
        if total_baseline == 0:
            continue

        baseline_late = baseline_counts[dist]['LATE'] / total_baseline
        baseline_early = baseline_counts[dist]['EARLY'] / total_baseline

        ch_data = distance_data[dist]['ch']
        ch_total = sum(ch_data.values())
        ch_late = ch_data['LATE'] / ch_total if ch_total > 0 else 0
        ch_early = ch_data['EARLY'] / ch_total if ch_total > 0 else 0

        sh_data = distance_data[dist]['sh']
        sh_total = sum(sh_data.values())
        sh_late = sh_data['LATE'] / sh_total if sh_total > 0 else 0
        sh_early = sh_data['EARLY'] / sh_total if sh_total > 0 else 0

        print(f"{dist:<6} {ch_late:<12.1%} {ch_early:<12.1%} {sh_late:<12.1%} {sh_early:<12.1%} {baseline_late:<14.1%}")

        ch_enrich = ch_late / baseline_late if baseline_late > 0 else 0
        sh_enrich = sh_late / baseline_late if baseline_late > 0 else 0
        enrichments.append((dist, ch_enrich, sh_enrich))

    print(f"\n--- LATE Enrichment by Distance ---")
    print(f"Distance:      " + " ".join(f"{d}".ljust(8) for d, _, _ in enrichments))
    print(f"ch->LATE:      " + " ".join(f"{e:.2f}x".ljust(8) for _, e, _ in enrichments))
    print(f"sh->LATE:      " + " ".join(f"{e:.2f}x".ljust(8) for _, _, e in enrichments))

    return enrichments

# =============================================================================
# ANALYSIS 4: CH vs SH COMPARISON
# =============================================================================

def compare_ch_sh(df):
    """Detailed comparison of ch- vs sh- (sister pair) triggering."""
    print("\n" + "="*80)
    print("ANALYSIS 4: CH vs SH COMPARISON (Sister Pair)")
    print("="*80)
    print("Question: Why does ch- trigger LATE HT but sh- doesn't?")
    print("Using NON-Y HT (ta vs op/pc/do)")

    df_sorted = df.sort_values(['folio', 'line_number', 'line_initial'])

    ch_contexts = []
    sh_contexts = []

    for (folio, line), group in df_sorted.groupby(['folio', 'line_number']):
        words = group['word'].tolist()

        for i, word in enumerate(words):
            gram_prefix = get_grammar_prefix(word)

            if gram_prefix in ['ch', 'sh'] and i + 1 < len(words):
                next_word = words[i + 1]
                ht_class = get_ht_prefix_class(next_word, include_y=False)

                # Get previous token's grammar prefix
                prev_gram = get_grammar_prefix(words[i-1]) if i > 0 else None

                # Get position info
                line_pos = i / len(words) if len(words) > 0 else 0

                context = {
                    'word': word,
                    'next_word': next_word,
                    'ht_class': ht_class,
                    'prev_gram': prev_gram,
                    'line_pos': line_pos,
                    'folio': folio,
                    'line': line
                }

                if gram_prefix == 'ch':
                    ch_contexts.append(context)
                else:
                    sh_contexts.append(context)

    ch_df = pd.DataFrame(ch_contexts)
    sh_df = pd.DataFrame(sh_contexts)

    print(f"\nch- tokens: {len(ch_df)}")
    print(f"sh- tokens: {len(sh_df)}")

    # Compare HT following rates
    ch_ht = ch_df[ch_df['ht_class'].notna()]
    sh_ht = sh_df[sh_df['ht_class'].notna()]

    print(f"\nch- followed by non-y HT: {len(ch_ht)} ({len(ch_ht)/len(ch_df)*100:.2f}%)")
    print(f"sh- followed by non-y HT: {len(sh_ht)} ({len(sh_ht)/len(sh_df)*100:.2f}%)")

    # HT class distribution
    print(f"\n--- HT Class Distribution After Each ---")
    for name, ht_df in [('ch-', ch_ht), ('sh-', sh_ht)]:
        if len(ht_df) > 0:
            class_dist = ht_df['ht_class'].value_counts(normalize=True)
            print(f"{name}: EARLY={class_dist.get('EARLY', 0):.1%}, LATE={class_dist.get('LATE', 0):.1%}")

    # What precedes when followed by LATE?
    print(f"\n--- Context Before ch/sh -> LATE ---")
    ch_late = ch_ht[ch_ht['ht_class'] == 'LATE']
    sh_late = sh_ht[sh_ht['ht_class'] == 'LATE']

    print(f"\nch- -> LATE ({len(ch_late)} cases):")
    if len(ch_late) > 0:
        prev_dist = ch_late['prev_gram'].value_counts().head(5)
        for gram, count in prev_dist.items():
            print(f"  prev={gram}: {count}")

    print(f"\nsh- -> LATE ({len(sh_late)} cases):")
    if len(sh_late) > 0:
        prev_dist = sh_late['prev_gram'].value_counts().head(5)
        for gram, count in prev_dist.items():
            print(f"  prev={gram}: {count}")

    return ch_df, sh_df

# =============================================================================
# ANALYSIS 5: SPECIFIC HT TOKEN PATTERNS
# =============================================================================

def analyze_specific_ht_tokens(df):
    """Look at which specific HT tokens follow which grammar prefixes."""
    print("\n" + "="*80)
    print("ANALYSIS 5: SPECIFIC HT TOKEN PATTERNS")
    print("="*80)

    df_sorted = df.sort_values(['folio', 'line_number', 'line_initial'])

    # Track specific HT tokens after each grammar prefix
    gram_to_ht_tokens = defaultdict(Counter)

    for (folio, line), group in df_sorted.groupby(['folio', 'line_number']):
        words = group['word'].tolist()

        for i, word in enumerate(words):
            gram_prefix = get_grammar_prefix(word)

            if gram_prefix and i + 1 < len(words):
                next_word = str(words[i + 1]).strip('"').lower()
                ht_class = get_ht_prefix_class(next_word, include_y=False)
                if ht_class:
                    gram_to_ht_tokens[gram_prefix][next_word] += 1

    print("\n--- Top HT tokens following each grammar prefix ---")
    for gram in ['ch', 'sh', 'qo', 'ok', 'ot']:
        tokens = gram_to_ht_tokens[gram]
        total = sum(tokens.values())
        if total < 5:
            continue

        print(f"\n{gram}- (N={total}):")
        for tok, count in tokens.most_common(8):
            ht_class = get_ht_prefix_class(tok, include_y=False)
            print(f"  {tok}: {count} ({ht_class})")

# =============================================================================
# ANALYSIS 6: STATISTICAL SIGNIFICANCE
# =============================================================================

def run_significance_tests(df, baseline_rates):
    """Run rigorous statistical tests on key findings."""
    print("\n" + "="*80)
    print("ANALYSIS 6: STATISTICAL SIGNIFICANCE")
    print("="*80)

    df_sorted = df.sort_values(['folio', 'line_number', 'line_initial'])

    # Collect ch- -> HT data
    ch_ht_classes = []
    all_ht_classes = []

    for (folio, line), group in df_sorted.groupby(['folio', 'line_number']):
        words = group['word'].tolist()

        for i, word in enumerate(words):
            ht_class = get_ht_prefix_class(word, include_y=False)
            if ht_class:
                all_ht_classes.append(ht_class)

            gram = get_grammar_prefix(word)
            if gram == 'ch' and i + 1 < len(words):
                next_ht = get_ht_prefix_class(words[i + 1], include_y=False)
                if next_ht:
                    ch_ht_classes.append(next_ht)

    if len(ch_ht_classes) < 10 or len(all_ht_classes) < 10:
        print("Insufficient data for significance tests")
        return

    n_ch_late = sum(1 for x in ch_ht_classes if x == 'LATE')
    n_ch_total = len(ch_ht_classes)

    n_all_late = sum(1 for x in all_ht_classes if x == 'LATE')
    n_all_total = len(all_ht_classes)

    baseline_late_rate = n_all_late / n_all_total
    observed_late_rate = n_ch_late / n_ch_total

    print(f"\n--- ch- -> LATE Enrichment Test ---")
    print(f"Baseline LATE rate: {baseline_late_rate:.1%} ({n_all_late}/{n_all_total})")
    print(f"ch- -> LATE rate: {observed_late_rate:.1%} ({n_ch_late}/{n_ch_total})")
    enrichment = observed_late_rate / baseline_late_rate if baseline_late_rate > 0 else 0
    print(f"Enrichment: {enrichment:.2f}x")

    # Z-test for proportions
    pooled = (n_ch_late + n_all_late) / (n_ch_total + n_all_total)
    se = np.sqrt(pooled * (1 - pooled) * (1/n_ch_total + 1/n_all_total))
    if se > 0:
        z = (observed_late_rate - baseline_late_rate) / se
        p_z = 2 * (1 - stats.norm.cdf(abs(z)))  # Two-tailed
        print(f"Z-test: z={z:.2f}, p={p_z:.2e}")

    # Bootstrap confidence interval
    print(f"\n--- Bootstrap 95% CI for ch- -> LATE ---")
    n_boot = 10000
    boot_rates = []
    for _ in range(n_boot):
        sample = np.random.choice(ch_ht_classes, size=len(ch_ht_classes), replace=True)
        boot_rates.append(sum(1 for x in sample if x == 'LATE') / len(sample))

    ci_low, ci_high = np.percentile(boot_rates, [2.5, 97.5])
    print(f"Observed: {observed_late_rate:.1%}")
    print(f"95% CI: [{ci_low:.1%}, {ci_high:.1%}]")
    print(f"Baseline ({baseline_late_rate:.1%}) {'NOT in CI - SIGNIFICANT' if baseline_late_rate < ci_low or baseline_late_rate > ci_high else 'IN CI - not significant'}")

# =============================================================================
# ANALYSIS 7: CONTINGENCY TABLE (Reproducing C413)
# =============================================================================

def reproduce_c413(df):
    """Attempt to reproduce the C413 findings exactly."""
    print("\n" + "="*80)
    print("ANALYSIS 7: REPRODUCING C413")
    print("="*80)
    print("C413 claims: ch- -> LATE at 46.6% vs baseline 24.0% (1.94x enrichment)")

    df_sorted = df.sort_values(['folio', 'line_number', 'line_initial'])

    # Build contingency table: Grammar Prefix vs HT Class
    data = []

    for (folio, line), group in df_sorted.groupby(['folio', 'line_number']):
        words = group['word'].tolist()

        for i, word in enumerate(words):
            gram_prefix = get_grammar_prefix(word)

            if gram_prefix and i + 1 < len(words):
                next_word = words[i + 1]
                ht_class = get_ht_prefix_class(next_word, include_y=False)
                if ht_class:
                    data.append({
                        'grammar': gram_prefix,
                        'ht_class': ht_class
                    })

    if len(data) < 10:
        print("Insufficient data")
        return

    result_df = pd.DataFrame(data)

    # Create contingency table
    contingency = pd.crosstab(result_df['grammar'], result_df['ht_class'])
    print("\n--- Contingency Table ---")
    print(contingency)

    # Calculate percentages
    print("\n--- Row Percentages (Grammar -> HT Class %) ---")
    row_pcts = contingency.div(contingency.sum(axis=1), axis=0) * 100
    print(row_pcts.round(1))

    # Chi-square test
    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    n = contingency.sum().sum()
    v = np.sqrt(chi2 / (n * (min(contingency.shape) - 1)))

    print(f"\n--- Chi-Square Test ---")
    print(f"Chi-square: {chi2:.2f}")
    print(f"p-value: {p:.2e}")
    print(f"Degrees of freedom: {dof}")
    print(f"Cramer's V: {v:.3f}")

    # Baseline rates
    baseline = contingency.sum() / contingency.sum().sum() * 100
    print(f"\n--- Baseline HT Class Distribution ---")
    print(baseline.round(1))

    # Key comparison: ch- vs baseline for LATE
    if 'ch' in row_pcts.index and 'LATE' in row_pcts.columns:
        ch_late = row_pcts.loc['ch', 'LATE']
        baseline_late = baseline['LATE']
        enrichment = ch_late / baseline_late if baseline_late > 0 else 0

        print(f"\n--- KEY FINDING: ch- -> LATE ---")
        print(f"ch- LATE rate: {ch_late:.1f}%")
        print(f"Baseline LATE rate: {baseline_late:.1f}%")
        print(f"Enrichment: {enrichment:.2f}x")

        # Compare to C413 claim
        print(f"\n--- Comparison to C413 ---")
        print(f"C413 claimed: ch- LATE = 46.6%, baseline = 24.0%, enrichment = 1.94x")
        print(f"We found:     ch- LATE = {ch_late:.1f}%, baseline = {baseline_late:.1f}%, enrichment = {enrichment:.2f}x")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("="*80)
    print("GRAMMAR -> HT TRIGGER DEEP ANALYSIS V2")
    print("C413 Extension Study")
    print("Using CORRECTED HT Definitions from C347/C348")
    print("="*80)

    # Load data
    df = load_data()

    # Run all analyses
    transition_df, baseline_rates = build_transition_matrix_primary(df)

    build_transition_matrix_all(df)

    v_fwd, v_bwd = test_bidirectionality(df)

    test_distance_effects(df)

    compare_ch_sh(df)

    analyze_specific_ht_tokens(df)

    run_significance_tests(df, baseline_rates)

    reproduce_c413(df)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

if __name__ == "__main__":
    main()
