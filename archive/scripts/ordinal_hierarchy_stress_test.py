"""
Phase HOT: Hierarchical Ordinal Testing
Stress test for ordinal regime encoding in human-track tokens.

Goal: Prove or falsify that human-track tokens encode ordered qualitative regimes
(e.g., low->medium->high heat, gentle->violent reflux, low->critical risk)
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import Dict, List, Tuple, Set, Optional
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# FIXED DATA (from Phase 20A and HTCS)
# ============================================================================

CATEGORIZED_TOKENS = {
    'daiin', 'aiin', 'chedy', 'chey', 'ol', 'ar', 'or', 'al', 'shedy',
    'qokaiin', 'qokedy', 'qokeedy', 'qokeey', 'chol', 'chor', 'shor',
    'shol', 'dar', 'dal', 'kaiin', 'taiin', 'saiin', 'raiin',
    'okaiin', 'okedy', 'okeedy', 'okeey', 'dain', 'chain', 'shain',
    'kain', 'rain', 'lain', 'sain', 'ckhey', 'ckhy', 'shy', 'dy',
    'ty', 'ky', 'ry', 'ly', 'sy', 'dol', 'dor', 'otal', 'otar',
    'char', 'shar', 'kar', 'rar', 'lar', 'sar', 'chal', 'shal',
    'kal', 'ral', 'lal', 'sal', 'chol', 'shol', 'kol', 'rol', 'lol', 'sol',
    'qol', 'qor', 'qokal', 'qokar', 'qokol', 'qokor', 'qotar', 'qotal',
    'qotol', 'qotor', 'qodaiin', 'qotaiin', 'qosaiin', 'qoraiin',
    'okain', 'okal', 'okar', 'okol', 'okor', 'otar', 'otal',
    'otol', 'otor', 'odaiin', 'otaiin', 'osaiin', 'oraiin',
    'cheol', 'cheor', 'chear', 'cheal', 'sheol', 'sheor', 'shear', 'sheal',
    'ched', 'shed', 'ked', 'red', 'led', 'sed', 'ted',
    'chod', 'shod', 'kod', 'rod', 'lod', 'sod', 'tod',
    'cheedy', 'sheedy', 'keedy', 'reedy', 'leedy', 'seedy', 'teedy',
    'chey', 'shey', 'key', 'rey', 'ley', 'sey', 'tey',
    'qokain', 'qokchy', 'qokey', 'okchy', 'okey', 'otchy', 'otey',
    'dchy', 'tchy', 'kchy', 'lchy', 'schy', 'rchy',
    'ctho', 'cthe', 'cthy', 'pcho', 'pche', 'pchy',
    'qo', 'ok', 'ot', 'od', 'op', 'ol', 'or', 'ar', 'al', 'am',
    's', 'r', 'l', 'd', 'y', 'o', 'e', 'a', 'n', 'm',
    'sh', 'ch', 'ck', 'ct', 'cp', 'cf',
    'ain', 'aiin', 'aiiin', 'an', 'am',
    'iin', 'in', 'ir', 'il',
    'oiin', 'oin', 'oir', 'oil',
    'eedy', 'edy', 'ey', 'ee', 'eey',
    'ody', 'oy', 'oly', 'ory', 'ary', 'aly',
    'cth', 'pch', 'ckh', 'cph', 'cfh',
    'cho', 'che', 'chy', 'sho', 'she',
    'ko', 'ke', 'ky', 'to', 'te',
    'lo', 'le', 'ly', 'ro', 're',
    'so', 'se', 'do', 'de',
    'chok', 'shok', 'cthok', 'pchok',
    'chot', 'shot', 'cthot', 'pchot',
    'cheok', 'sheok', 'ctheok', 'pcheok',
    'cheot', 'sheot', 'ctheot', 'pcheot',
    'qokeol', 'qokeor', 'qokeal', 'qokear',
    'okeol', 'okeor', 'okeal', 'okear',
    'dainy', 'sainy', 'rainy', 'lainy', 'tainy', 'kainy',
    'chdy', 'shdy', 'kdy', 'tdy', 'ldy', 'sdy', 'rdy',
    'daiiin', 'saiiin', 'raiiin', 'laiiin', 'taiiin', 'kaiiin',
    'qotedy', 'qotey', 'qoteedy', 'qoteey',
    'otedy', 'otey', 'oteedy', 'oteey',
    'chedy', 'shedy', 'tedy', 'kedy', 'ledy', 'sedy', 'redy',
    'qokchedy', 'qokchey', 'okchedy', 'okchey',
    'chedaiin', 'shedaiin', 'kedaiin', 'tedaiin',
    'darol', 'daror', 'daral', 'darar',
    'sarol', 'saror', 'saral', 'sarar',
    'tarol', 'taror', 'taral', 'tarar',
    'dairol', 'dairor', 'dairal', 'dairar',
    'qotchedy', 'qotchey', 'otchedy', 'otchey',
    'qodainy', 'qotainy', 'qosainy', 'qorainy',
    'odainy', 'otainy', 'osainy', 'orainy',
    'okchol', 'okchor', 'okchal', 'okchar',
    'qokchol', 'qokchor', 'qokchal', 'qokchar',
    'sholy', 'choly', 'koly', 'toly', 'loly', 'soly', 'roly',
    'shory', 'chory', 'kory', 'tory', 'lory', 'sory', 'rory',
    'shary', 'chary', 'kary', 'tary', 'lary', 'sary', 'rary',
    'shaly', 'chaly', 'kaly', 'taly', 'laly', 'saly', 'raly',
    'daiiiny', 'saiiiny', 'raiiiny', 'laiiiny',
    'cheody', 'sheody', 'keody', 'teody', 'leody', 'seody', 'reody',
    'qokchdy', 'okchdy', 'otchdy', 'qotchdy',
    'chckhy', 'shckhy', 'kckhy', 'tckhy', 'lckhy', 'sckhy', 'rckhy',
    'qoteol', 'qoteor', 'qoteal', 'qotear',
    'oteol', 'oteor', 'oteal', 'otear',
    'opcheol', 'opcheor', 'opcheal', 'opchear',
    'qopcheol', 'qopcheor', 'qopcheal', 'qopchear',
    'daly', 'saly', 'raly', 'laly', 'taly', 'kaly',
    'dary', 'sary', 'rary', 'lary', 'tary', 'kary',
    'doly', 'soly', 'roly', 'loly', 'toly', 'koly',
    'dory', 'sory', 'rory', 'lory', 'tory', 'kory',
    'qotchol', 'qotchor', 'qotchal', 'qotchar',
    'otchol', 'otchor', 'otchal', 'otchar',
    'qokoly', 'qokory', 'qokaly', 'qokary',
    'okoly', 'okory', 'okaly', 'okary',
    'dshedy', 'dshey', 'dsheedy', 'dsheey',
    'oeshedy', 'oeshey', 'oesheedy', 'oesheey',
    'qopchedy', 'qopchey', 'qopcheedy', 'qopcheey',
    'opchedy', 'opchey', 'opcheedy', 'opcheey',
    'dchedy', 'dchey', 'dcheedy', 'dcheey',
    'ckhedy', 'ckhey', 'ckheedy', 'ckheey',
    'qodchedy', 'qodchey', 'qodcheedy', 'qodcheey',
    'odchedy', 'odchey', 'odcheedy', 'odcheey',
    'dshol', 'dshor', 'dshal', 'dshar',
    'oeshol', 'oeshor', 'oeshal', 'oeshar',
    'qopchol', 'qopchor', 'qopchal', 'qopchar',
    'opchol', 'opchor', 'opchal', 'opchar',
    'dchol', 'dchor', 'dchal', 'dchar',
    'ckhol', 'ckhor', 'ckhal', 'ckhar',
    'qodchol', 'qodchor', 'qodchal', 'qodchar',
    'odchol', 'odchor', 'odchal', 'odchar',
}

LINK_INDICATORS = {'qo', 'ok', 'ol', 'or', 'ar', 'al', 'daiin', 'saiin', 'raiin'}
KERNEL_CHARS = {'k', 'h', 'e'}

# Semantic labels from Phase SSI
SEMANTIC_LABELS = {
    'ESTABLISHING': 'CF-1',  # Section entry
    'RUNNING': 'CF-3',       # Wait marker
    'HOLDING': 'CF-5',       # Persistence marker
    'APPROACHING': 'CF-6',   # Constraint rise
    'RELAXING': 'CF-7',      # Constraint fall
    'EXHAUSTING': 'CF-2',    # Section exit
}

# ============================================================================
# DATA LOADING
# ============================================================================

def load_transcription():
    """Load interlinear transcription."""
    df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
    return df

def get_section(folio: str) -> str:
    """Determine section from folio ID."""
    section_map = {
        'H': ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
              'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23',
              'f24', 'f25'],
        'S': ['f103', 'f104', 'f105', 'f106', 'f107', 'f108', 'f109', 'f110', 'f111', 'f112',
              'f113', 'f114', 'f115', 'f116'],
        'C': ['f75', 'f76', 'f77', 'f78', 'f79', 'f80', 'f81', 'f82', 'f83', 'f84'],
        'A': ['f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73'],
        'B': ['f26', 'f27', 'f28', 'f29', 'f30', 'f31', 'f32', 'f33', 'f34', 'f35',
              'f36', 'f37', 'f38', 'f39', 'f40', 'f41', 'f42', 'f43', 'f44', 'f45',
              'f46', 'f47', 'f48', 'f49', 'f50', 'f51', 'f52', 'f53', 'f54', 'f55',
              'f56'],
        'P': ['f85', 'f86', 'f87', 'f88', 'f89', 'f90'],
        'T': ['f58', 'f65', 'f66'],
        'Z': ['f70', 'f71', 'f72', 'f73', 'f74'],
    }
    folio_base = folio.split('v')[0].split('r')[0]
    for section, folios in section_map.items():
        for f in folios:
            if folio_base.startswith(f) or folio.startswith(f):
                return section
    return 'U'

# ============================================================================
# STRESS METRICS
# ============================================================================

@dataclass
class TokenStressProfile:
    """Stress metrics for a token in context."""
    token: str
    constraint_density: float      # Kernel chars in neighborhood
    hazard_proximity: float        # Distance to hazard-involved tokens
    instruction_aggressiveness: float  # Proportion of non-LINK neighbors
    kernel_k_presence: float       # k character presence rate
    link_proximity: float          # Closeness to LINK contexts
    section: str
    position_in_section: float     # 0-1 normalized

def compute_neighborhood_metrics(df: pd.DataFrame, idx: int, window: int = 5) -> dict:
    """Compute stress metrics for a token position."""
    token = df.iloc[idx]['word'] if 'word' in df.columns else df.iloc[idx]['token']

    # Get neighbors
    start = max(0, idx - window)
    end = min(len(df), idx + window + 1)
    neighbors = df.iloc[start:end]

    # Constraint density (kernel character rate)
    kernel_count = 0
    total_chars = 0
    for _, row in neighbors.iterrows():
        w = row['word'] if 'word' in row else row['token']
        if pd.notna(w):
            total_chars += len(str(w))
            kernel_count += sum(1 for c in str(w) if c in KERNEL_CHARS)
    constraint_density = kernel_count / max(total_chars, 1)

    # Instruction aggressiveness (non-LINK categorized tokens)
    cat_count = 0
    link_count = 0
    for _, row in neighbors.iterrows():
        w = row['word'] if 'word' in row else row['token']
        if pd.notna(w) and str(w) in CATEGORIZED_TOKENS:
            cat_count += 1
            if any(link in str(w) for link in LINK_INDICATORS):
                link_count += 1
    aggressiveness = (cat_count - link_count) / max(cat_count, 1)

    # Kernel-k presence
    k_count = 0
    for _, row in neighbors.iterrows():
        w = row['word'] if 'word' in row else row['token']
        if pd.notna(w) and 'k' in str(w):
            k_count += 1
    k_presence = k_count / len(neighbors)

    # LINK proximity
    link_tokens = 0
    for _, row in neighbors.iterrows():
        w = row['word'] if 'word' in row else row['token']
        if pd.notna(w):
            if any(link in str(w) for link in LINK_INDICATORS):
                link_tokens += 1
    link_proximity = link_tokens / len(neighbors)

    return {
        'constraint_density': constraint_density,
        'instruction_aggressiveness': aggressiveness,
        'kernel_k_presence': k_presence,
        'link_proximity': link_proximity,
    }

# ============================================================================
# BEHAVIORAL CLASSIFICATION (from HTCS)
# ============================================================================

def classify_token_behavior(df: pd.DataFrame, token: str) -> str:
    """Classify token into behavioral cluster."""
    word_col = 'word' if 'word' in df.columns else 'token'
    token_rows = df[df[word_col] == token]

    if len(token_rows) < 5:
        return 'LOW_FREQ'

    # Get section info
    sections = token_rows['folio'].apply(get_section)
    section_counts = sections.value_counts()

    # Calculate early/late rates
    positions = []
    for idx in token_rows.index:
        folio = df.iloc[idx]['folio']
        folio_rows = df[df['folio'] == folio]
        if len(folio_rows) > 0:
            pos = (idx - folio_rows.index[0]) / max(len(folio_rows), 1)
            positions.append(pos)

    if not positions:
        return 'POSITION_NEUTRAL'

    mean_pos = np.mean(positions)
    early_rate = sum(1 for p in positions if p < 0.2) / len(positions)
    late_rate = sum(1 for p in positions if p > 0.8) / len(positions)

    # Classify
    if early_rate > 0.4:
        return 'ESTABLISHING'  # CF-1
    elif late_rate > 0.4:
        return 'EXHAUSTING'    # CF-2
    elif mean_pos < 0.35:
        return 'ESTABLISHING'
    elif mean_pos > 0.65:
        return 'EXHAUSTING'
    else:
        return 'RUNNING'       # CF-3 default

def get_constraint_gradient(df: pd.DataFrame, token: str) -> str:
    """Determine constraint gradient direction for token."""
    word_col = 'word' if 'word' in df.columns else 'token'
    token_indices = df[df[word_col] == token].index.tolist()

    if len(token_indices) < 5:
        return 'NEUTRAL'

    before_densities = []
    after_densities = []

    for idx in token_indices[:100]:  # Sample up to 100
        if idx < 5 or idx >= len(df) - 5:
            continue
        before = compute_neighborhood_metrics(df, idx - 3, window=3)
        after = compute_neighborhood_metrics(df, idx + 3, window=3)
        before_densities.append(before['constraint_density'])
        after_densities.append(after['constraint_density'])

    if not before_densities:
        return 'NEUTRAL'

    mean_before = np.mean(before_densities)
    mean_after = np.mean(after_densities)

    if mean_after > mean_before * 1.1:
        return 'APPROACHING'   # CF-6
    elif mean_after < mean_before * 0.9:
        return 'RELAXING'      # CF-7
    else:
        return 'RUNNING'

def get_run_length(df: pd.DataFrame, token: str) -> float:
    """Get mean consecutive run length for token."""
    word_col = 'word' if 'word' in df.columns else 'token'
    tokens = df[word_col].tolist()

    runs = []
    current_run = 0
    for t in tokens:
        if t == token:
            current_run += 1
        else:
            if current_run > 0:
                runs.append(current_run)
            current_run = 0
    if current_run > 0:
        runs.append(current_run)

    return np.mean(runs) if runs else 0

# ============================================================================
# TEST 1: GLOBAL MONOTONIC ORDERING
# ============================================================================

def test_global_monotonic_ordering(df: pd.DataFrame) -> dict:
    """
    Test if semantic labels can be placed on a single stress axis.
    """
    print("\n" + "="*70)
    print("TEST 1: GLOBAL MONOTONIC ORDERING")
    print("="*70)

    word_col = 'word' if 'word' in df.columns else 'token'

    # Collect metrics per semantic label
    label_metrics = defaultdict(lambda: {
        'constraint_density': [],
        'instruction_aggressiveness': [],
        'kernel_k_presence': [],
        'link_proximity': [],
    })

    # Sample tokens for each behavioral class
    uncategorized = df[~df[word_col].isin(CATEGORIZED_TOKENS)]
    token_counts = uncategorized[word_col].value_counts()
    frequent_tokens = token_counts[token_counts >= 10].index.tolist()[:500]

    print(f"Analyzing {len(frequent_tokens)} frequent human-track tokens...")

    token_labels = {}
    for token in frequent_tokens:
        behavior = classify_token_behavior(df, token)
        gradient = get_constraint_gradient(df, token)
        run_len = get_run_length(df, token)

        # Assign label based on behaviors
        if behavior == 'ESTABLISHING':
            label = 'ESTABLISHING'
        elif behavior == 'EXHAUSTING':
            label = 'EXHAUSTING'
        elif gradient == 'APPROACHING':
            label = 'APPROACHING'
        elif gradient == 'RELAXING':
            label = 'RELAXING'
        elif run_len > 1.5:
            label = 'HOLDING'
        else:
            label = 'RUNNING'

        token_labels[token] = label

        # Collect metrics for this token
        token_rows = df[df[word_col] == token]
        for idx in token_rows.index[:50]:  # Sample up to 50 occurrences
            metrics = compute_neighborhood_metrics(df, idx)
            for metric, value in metrics.items():
                label_metrics[label][metric].append(value)

    # Compute median metrics per label
    print("\nMedian stress metrics per semantic label:")
    print("-" * 70)

    results = {}
    for label in ['ESTABLISHING', 'RUNNING', 'HOLDING', 'APPROACHING', 'RELAXING', 'EXHAUSTING']:
        if label not in label_metrics or not label_metrics[label]['constraint_density']:
            results[label] = {'constraint_density': 0, 'instruction_aggressiveness': 0,
                             'kernel_k_presence': 0, 'link_proximity': 0}
            continue

        results[label] = {
            'constraint_density': np.median(label_metrics[label]['constraint_density']),
            'instruction_aggressiveness': np.median(label_metrics[label]['instruction_aggressiveness']),
            'kernel_k_presence': np.median(label_metrics[label]['kernel_k_presence']),
            'link_proximity': np.median(label_metrics[label]['link_proximity']),
        }

        print(f"{label:15} | CD={results[label]['constraint_density']:.3f} | "
              f"AGG={results[label]['instruction_aggressiveness']:.3f} | "
              f"K={results[label]['kernel_k_presence']:.3f} | "
              f"LINK={results[label]['link_proximity']:.3f}")

    # Test for monotonic ordering
    # Hypothesized hierarchy: ESTABLISHING < RUNNING < HOLDING < APPROACHING
    # (with RELAXING and EXHAUSTING as transitions back down)

    hypothesized_order = ['ESTABLISHING', 'RUNNING', 'HOLDING', 'APPROACHING']

    # Check constraint density ordering
    cd_values = [results[l]['constraint_density'] for l in hypothesized_order if l in results]
    cd_monotonic = all(cd_values[i] <= cd_values[i+1] for i in range(len(cd_values)-1))

    # Check instruction aggressiveness ordering
    agg_values = [results[l]['instruction_aggressiveness'] for l in hypothesized_order if l in results]
    agg_monotonic = all(agg_values[i] <= agg_values[i+1] for i in range(len(agg_values)-1))

    # Check kernel-k ordering
    k_values = [results[l]['kernel_k_presence'] for l in hypothesized_order if l in results]
    k_monotonic = all(k_values[i] <= k_values[i+1] for i in range(len(k_values)-1))

    print("\nMonotonicity tests (ESTABLISHING->RUNNING->HOLDING->APPROACHING):")
    print(f"  Constraint density monotonic: {cd_monotonic}")
    print(f"  Instruction aggressiveness monotonic: {agg_monotonic}")
    print(f"  Kernel-k presence monotonic: {k_monotonic}")

    # Section invariance check
    print("\nSection-by-section ordering check:")
    section_orderings = {}
    for section in ['H', 'S', 'B', 'C', 'A', 'P', 'T', 'Z']:
        section_df = df[df['folio'].apply(get_section) == section]
        if len(section_df) < 100:
            continue

        section_metrics = {}
        for label in hypothesized_order:
            tokens_in_section = [t for t, l in token_labels.items() if l == label]
            densities = []
            for token in tokens_in_section[:20]:
                token_rows = section_df[section_df[word_col] == token]
                for idx in token_rows.index[:10]:
                    if idx in df.index:
                        m = compute_neighborhood_metrics(df, idx)
                        densities.append(m['constraint_density'])
            section_metrics[label] = np.median(densities) if densities else 0

        if all(section_metrics.get(l, 0) > 0 for l in hypothesized_order):
            cd_order = [section_metrics[l] for l in hypothesized_order]
            is_monotonic = all(cd_order[i] <= cd_order[i+1] for i in range(len(cd_order)-1))
            section_orderings[section] = is_monotonic
            print(f"  Section {section}: {'MONOTONIC' if is_monotonic else 'NOT MONOTONIC'}")

    # Verdict
    monotonic_count = sum(1 for v in section_orderings.values() if v)
    total_sections = len(section_orderings)

    verdict = {
        'cd_monotonic': cd_monotonic,
        'agg_monotonic': agg_monotonic,
        'k_monotonic': k_monotonic,
        'sections_tested': total_sections,
        'sections_monotonic': monotonic_count,
        'global_ordering_stable': monotonic_count >= total_sections * 0.7,
        'label_metrics': results,
        'token_labels': token_labels,
    }

    return verdict

# ============================================================================
# TEST 2: ANTISYMMETRIC SUBSTITUTION TEST
# ============================================================================

def test_antisymmetric_substitution(df: pd.DataFrame, token_labels: dict) -> dict:
    """
    Test if hierarchical tiers freely substitute in same contexts.
    True hierarchy: tiers should NOT substitute.
    """
    print("\n" + "="*70)
    print("TEST 2: ANTISYMMETRIC SUBSTITUTION TEST")
    print("="*70)

    word_col = 'word' if 'word' in df.columns else 'token'

    # Define context by: preceding 2 tokens + following 2 tokens (categorized only)
    def get_context(idx: int) -> tuple:
        context = []
        for offset in [-2, -1, 1, 2]:
            check_idx = idx + offset
            if 0 <= check_idx < len(df):
                w = df.iloc[check_idx][word_col]
                if pd.notna(w) and str(w) in CATEGORIZED_TOKENS:
                    context.append(str(w))
                else:
                    context.append('_')
            else:
                context.append('_')
        return tuple(context)

    # Collect contexts per label
    label_contexts = defaultdict(set)
    context_labels = defaultdict(set)

    for token, label in list(token_labels.items())[:200]:
        token_rows = df[df[word_col] == token]
        for idx in token_rows.index[:30]:
            ctx = get_context(idx)
            if ctx != ('_', '_', '_', '_'):  # Skip empty contexts
                label_contexts[label].add(ctx)
                context_labels[ctx].add(label)

    # Compute substitution matrix
    labels = ['ESTABLISHING', 'RUNNING', 'HOLDING', 'APPROACHING', 'RELAXING', 'EXHAUSTING']
    substitution_matrix = {}

    print("\nContext overlap between label pairs:")
    print("-" * 50)

    for i, label1 in enumerate(labels):
        for j, label2 in enumerate(labels):
            if i >= j:
                continue
            contexts1 = label_contexts.get(label1, set())
            contexts2 = label_contexts.get(label2, set())
            if not contexts1 or not contexts2:
                continue
            overlap = len(contexts1 & contexts2)
            union = len(contexts1 | contexts2)
            jaccard = overlap / max(union, 1)
            substitution_matrix[(label1, label2)] = jaccard
            print(f"  {label1:15} <-> {label2:15}: {jaccard:.3f} ({overlap}/{union})")

    # Check if hierarchically adjacent labels substitute less than non-adjacent
    hierarchy = ['ESTABLISHING', 'RUNNING', 'HOLDING', 'APPROACHING']
    adjacent_subs = []
    non_adjacent_subs = []

    for (l1, l2), jac in substitution_matrix.items():
        if l1 in hierarchy and l2 in hierarchy:
            idx1, idx2 = hierarchy.index(l1), hierarchy.index(l2)
            if abs(idx1 - idx2) == 1:
                adjacent_subs.append(jac)
            else:
                non_adjacent_subs.append(jac)

    mean_adjacent = np.mean(adjacent_subs) if adjacent_subs else 0
    mean_non_adjacent = np.mean(non_adjacent_subs) if non_adjacent_subs else 0

    print(f"\nMean substitution (adjacent tiers): {mean_adjacent:.3f}")
    print(f"Mean substitution (non-adjacent tiers): {mean_non_adjacent:.3f}")

    # In true hierarchy: adjacent < non_adjacent (tiers don't blur)
    # In attention system: adjacent ≈ non_adjacent (all substitute)

    hierarchy_signal = mean_adjacent < mean_non_adjacent * 0.8

    verdict = {
        'substitution_matrix': substitution_matrix,
        'mean_adjacent_substitution': mean_adjacent,
        'mean_non_adjacent_substitution': mean_non_adjacent,
        'supports_hierarchy': hierarchy_signal,
        'interpretation': 'Tiers are distinct' if hierarchy_signal else 'Tiers freely substitute',
    }

    return verdict

# ============================================================================
# TEST 3: TRANSITION DIRECTIONALITY TEST
# ============================================================================

def test_transition_directionality(df: pd.DataFrame, token_labels: dict) -> dict:
    """
    Test if transitions between labels are directional (hierarchy)
    or symmetric (attention/navigation).
    """
    print("\n" + "="*70)
    print("TEST 3: TRANSITION DIRECTIONALITY TEST")
    print("="*70)

    word_col = 'word' if 'word' in df.columns else 'token'

    # Assign labels to all positions
    position_labels = []
    for idx in range(len(df)):
        token = df.iloc[idx][word_col]
        if pd.notna(token) and str(token) in token_labels:
            position_labels.append((idx, token_labels[str(token)]))

    # Count transitions
    transition_counts = defaultdict(int)
    for i in range(len(position_labels) - 1):
        idx1, label1 = position_labels[i]
        idx2, label2 = position_labels[i + 1]
        if idx2 - idx1 <= 3:  # Within 3 positions
            transition_counts[(label1, label2)] += 1

    # Build transition matrix
    labels = ['ESTABLISHING', 'RUNNING', 'HOLDING', 'APPROACHING', 'RELAXING', 'EXHAUSTING']

    print("\nTransition matrix (row->column):")
    print("-" * 80)
    header = "From \\ To    " + " ".join(f"{l[:6]:>8}" for l in labels)
    print(header)

    for from_label in labels:
        row_counts = [transition_counts.get((from_label, to_label), 0) for to_label in labels]
        total = sum(row_counts) or 1
        row_probs = [c / total for c in row_counts]
        row_str = f"{from_label[:12]:12}" + " ".join(f"{p:8.2f}" for p in row_probs)
        print(row_str)

    # Test directionality
    # Hypothesized forward: ESTABLISHING->RUNNING->HOLDING->APPROACHING
    # Hypothesized backward: RELAXING->RUNNING, EXHAUSTING->end

    forward_transitions = [
        ('ESTABLISHING', 'RUNNING'),
        ('RUNNING', 'HOLDING'),
        ('HOLDING', 'APPROACHING'),
    ]

    backward_transitions = [
        ('RUNNING', 'ESTABLISHING'),
        ('HOLDING', 'RUNNING'),
        ('APPROACHING', 'HOLDING'),
    ]

    forward_count = sum(transition_counts.get(t, 0) for t in forward_transitions)
    backward_count = sum(transition_counts.get(t, 0) for t in backward_transitions)

    print(f"\nForward transitions (UP hierarchy): {forward_count}")
    print(f"Backward transitions (DOWN hierarchy): {backward_count}")

    if forward_count + backward_count > 0:
        directionality_bias = forward_count / (forward_count + backward_count)
    else:
        directionality_bias = 0.5

    print(f"Directionality bias (forward): {directionality_bias:.3f}")
    print(f"  (0.5 = symmetric, >0.6 = directional, >0.8 = strongly directional)")

    verdict = {
        'transition_counts': dict(transition_counts),
        'forward_count': forward_count,
        'backward_count': backward_count,
        'directionality_bias': directionality_bias,
        'supports_hierarchy': directionality_bias > 0.6,
        'interpretation': 'Directional flow' if directionality_bias > 0.6 else 'Symmetric/random flow',
    }

    return verdict

# ============================================================================
# TEST 4: LOCAL SLOPE STEEPNESS TEST
# ============================================================================

def test_local_slope_steepness(df: pd.DataFrame, token_labels: dict) -> dict:
    """
    Test if label probabilities change step-like (hierarchy)
    or smoothly (attention gradients).
    """
    print("\n" + "="*70)
    print("TEST 4: LOCAL SLOPE STEEPNESS TEST")
    print("="*70)

    word_col = 'word' if 'word' in df.columns else 'token'

    # Bin positions by constraint density
    bins = 10
    densities = []
    labels_by_density = defaultdict(list)

    for token, label in list(token_labels.items())[:200]:
        token_rows = df[df[word_col] == token]
        for idx in token_rows.index[:30]:
            metrics = compute_neighborhood_metrics(df, idx)
            densities.append(metrics['constraint_density'])
            labels_by_density[label].append(metrics['constraint_density'])

    if not densities:
        return {'supports_hierarchy': False, 'interpretation': 'Insufficient data'}

    # Create density bins
    min_d, max_d = min(densities), max(densities)
    bin_edges = np.linspace(min_d, max_d, bins + 1)

    print("\nLabel distribution by constraint density bin:")
    print("-" * 70)

    labels = ['ESTABLISHING', 'RUNNING', 'HOLDING', 'APPROACHING', 'RELAXING', 'EXHAUSTING']
    label_by_bin = defaultdict(lambda: defaultdict(int))

    for label in labels:
        for d in labels_by_density.get(label, []):
            bin_idx = min(int((d - min_d) / (max_d - min_d + 0.001) * bins), bins - 1)
            label_by_bin[bin_idx][label] += 1

    # Print distribution
    print("Bin   " + " ".join(f"{l[:6]:>8}" for l in labels))
    for b in range(bins):
        total = sum(label_by_bin[b].values()) or 1
        probs = [label_by_bin[b].get(l, 0) / total for l in labels]
        print(f"{b:4d}  " + " ".join(f"{p:8.2f}" for p in probs))

    # Measure "step-ness" - do labels dominate in specific bins?
    dominance_scores = []
    for b in range(bins):
        total = sum(label_by_bin[b].values())
        if total >= 5:
            max_count = max(label_by_bin[b].values())
            dominance = max_count / total
            dominance_scores.append(dominance)

    mean_dominance = np.mean(dominance_scores) if dominance_scores else 0

    print(f"\nMean bin dominance: {mean_dominance:.3f}")
    print("  (>0.5 = step-like, <0.4 = smooth overlap)")

    verdict = {
        'mean_bin_dominance': mean_dominance,
        'supports_hierarchy': mean_dominance > 0.5,
        'interpretation': 'Step-like distribution' if mean_dominance > 0.5 else 'Smooth gradient overlap',
    }

    return verdict

# ============================================================================
# TEST 5: SECTION-INVARIANCE TEST
# ============================================================================

def test_section_invariance(df: pd.DataFrame, token_labels: dict) -> dict:
    """
    Test if hierarchy is apparatus-global or section-local.
    """
    print("\n" + "="*70)
    print("TEST 5: SECTION-INVARIANCE TEST")
    print("="*70)

    word_col = 'word' if 'word' in df.columns else 'token'

    # Compute label rankings per section
    section_rankings = {}

    hierarchy_labels = ['ESTABLISHING', 'RUNNING', 'HOLDING', 'APPROACHING']

    for section in ['H', 'S', 'B', 'C', 'A', 'P']:
        section_df = df[df['folio'].apply(get_section) == section]
        if len(section_df) < 100:
            continue

        label_densities = {}
        for label in hierarchy_labels:
            tokens_with_label = [t for t, l in token_labels.items() if l == label]
            densities = []
            for token in tokens_with_label[:30]:
                token_rows = section_df[section_df[word_col] == token]
                for idx in token_rows.index[:10]:
                    if idx in df.index:
                        m = compute_neighborhood_metrics(df, idx)
                        densities.append(m['constraint_density'])
            label_densities[label] = np.median(densities) if densities else 0

        # Rank labels by density
        ranking = sorted(label_densities.keys(), key=lambda l: label_densities[l])
        section_rankings[section] = ranking

        print(f"Section {section}: {' < '.join(ranking)}")

    # Check if rankings are consistent
    if len(section_rankings) < 2:
        return {'supports_hierarchy': False, 'interpretation': 'Insufficient sections'}

    reference_ranking = list(section_rankings.values())[0]
    matching_sections = 0

    for section, ranking in section_rankings.items():
        if ranking == reference_ranking:
            matching_sections += 1

    consistency = matching_sections / len(section_rankings)

    print(f"\nRanking consistency across sections: {consistency:.2%}")
    print(f"  (>70% = global hierarchy, <50% = section-local)")

    verdict = {
        'section_rankings': section_rankings,
        'consistency': consistency,
        'supports_global_hierarchy': consistency > 0.7,
        'interpretation': 'Global hierarchy' if consistency > 0.7 else 'Section-local only',
    }

    return verdict

# ============================================================================
# TIER MODEL FITTING
# ============================================================================

def fit_ordinal_models(df: pd.DataFrame, token_labels: dict) -> dict:
    """
    Attempt to fit 3-tier and 4-tier ordinal models.
    """
    print("\n" + "="*70)
    print("ORDINAL MODEL FITTING")
    print("="*70)

    word_col = 'word' if 'word' in df.columns else 'token'

    # Collect all token stress values
    token_stress = {}
    for token, label in list(token_labels.items())[:200]:
        token_rows = df[df[word_col] == token]
        densities = []
        for idx in token_rows.index[:30]:
            m = compute_neighborhood_metrics(df, idx)
            densities.append(m['constraint_density'])
        if densities:
            token_stress[token] = np.median(densities)

    if not token_stress:
        return {'error': 'No stress data'}

    stress_values = list(token_stress.values())

    # 3-tier model
    print("\n3-TIER MODEL:")
    tier3_thresholds = np.percentile(stress_values, [33, 67])
    tier3_assignment = {}
    for token, stress in token_stress.items():
        if stress < tier3_thresholds[0]:
            tier3_assignment[token] = 'LOW'
        elif stress < tier3_thresholds[1]:
            tier3_assignment[token] = 'MEDIUM'
        else:
            tier3_assignment[token] = 'HIGH'

    tier3_counts = Counter(tier3_assignment.values())
    print(f"  Tier counts: {dict(tier3_counts)}")
    print(f"  Thresholds: LOW<{tier3_thresholds[0]:.3f}<MEDIUM<{tier3_thresholds[1]:.3f}<HIGH")

    # 4-tier model
    print("\n4-TIER MODEL:")
    tier4_thresholds = np.percentile(stress_values, [25, 50, 75])
    tier4_assignment = {}
    for token, stress in token_stress.items():
        if stress < tier4_thresholds[0]:
            tier4_assignment[token] = 'MINIMAL'
        elif stress < tier4_thresholds[1]:
            tier4_assignment[token] = 'LOW'
        elif stress < tier4_thresholds[2]:
            tier4_assignment[token] = 'ELEVATED'
        else:
            tier4_assignment[token] = 'HIGH'

    tier4_counts = Counter(tier4_assignment.values())
    print(f"  Tier counts: {dict(tier4_counts)}")
    print(f"  Thresholds: MINIMAL<{tier4_thresholds[0]:.3f}<LOW<{tier4_thresholds[1]:.3f}<ELEVATED<{tier4_thresholds[2]:.3f}<HIGH")

    # Compute model error: do semantic labels map cleanly to tiers?
    label_tier_confusion = defaultdict(lambda: defaultdict(int))
    for token, label in token_labels.items():
        if token in tier4_assignment:
            tier = tier4_assignment[token]
            label_tier_confusion[label][tier] += 1

    print("\n4-TIER MODEL: Label-to-Tier Confusion Matrix:")
    print("-" * 50)
    tiers = ['MINIMAL', 'LOW', 'ELEVATED', 'HIGH']
    labels = ['ESTABLISHING', 'RUNNING', 'HOLDING', 'APPROACHING', 'RELAXING', 'EXHAUSTING']

    header = "Label        " + " ".join(f"{t:>8}" for t in tiers)
    print(header)
    for label in labels:
        row = [label_tier_confusion[label].get(t, 0) for t in tiers]
        total = sum(row) or 1
        row_pct = [r / total for r in row]
        print(f"{label[:12]:12} " + " ".join(f"{p:8.2f}" for p in row_pct))

    # Model purity: does each semantic label map primarily to one tier?
    purity_scores = []
    for label in labels:
        row = [label_tier_confusion[label].get(t, 0) for t in tiers]
        total = sum(row)
        if total > 0:
            purity = max(row) / total
            purity_scores.append(purity)

    mean_purity = np.mean(purity_scores) if purity_scores else 0

    print(f"\nMean label purity (4-tier model): {mean_purity:.3f}")
    print("  (>0.6 = clean tier mapping, <0.4 = diffuse across tiers)")

    verdict = {
        'tier3_thresholds': tier3_thresholds.tolist(),
        'tier4_thresholds': tier4_thresholds.tolist(),
        'mean_purity_4tier': mean_purity,
        'clean_tier_mapping': mean_purity > 0.6,
    }

    return verdict

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("PHASE HOT: HIERARCHICAL ORDINAL TESTING")
    print("Stress test for ordinal regime encoding in human-track")
    print("="*70)

    # Load data
    print("\nLoading transcription data...")
    df = load_transcription()
    print(f"Loaded {len(df)} tokens")

    word_col = 'word' if 'word' in df.columns else 'token'
    total_tokens = len(df)
    uncategorized = df[~df[word_col].isin(CATEGORIZED_TOKENS)]
    print(f"Human-track tokens: {len(uncategorized)} ({100*len(uncategorized)/total_tokens:.1f}%)")

    # Run all tests
    results = {}

    # Test 1: Global Monotonic Ordering
    test1 = test_global_monotonic_ordering(df)
    results['test1_global_ordering'] = test1
    token_labels = test1['token_labels']

    # Test 2: Antisymmetric Substitution
    test2 = test_antisymmetric_substitution(df, token_labels)
    results['test2_substitution'] = test2

    # Test 3: Transition Directionality
    test3 = test_transition_directionality(df, token_labels)
    results['test3_directionality'] = test3

    # Test 4: Local Slope Steepness
    test4 = test_local_slope_steepness(df, token_labels)
    results['test4_slope'] = test4

    # Test 5: Section Invariance
    test5 = test_section_invariance(df, token_labels)
    results['test5_section_invariance'] = test5

    # Ordinal Model Fitting
    model_fit = fit_ordinal_models(df, token_labels)
    results['model_fit'] = model_fit

    # Final Summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)

    print("\n| Test | Result | Supports Hierarchy? |")
    print("|------|--------|---------------------|")

    tests = [
        ("1. Global Monotonic Ordering", test1.get('global_ordering_stable', False)),
        ("2. Antisymmetric Substitution", test2.get('supports_hierarchy', False)),
        ("3. Transition Directionality", test3.get('supports_hierarchy', False)),
        ("4. Local Slope Steepness", test4.get('supports_hierarchy', False)),
        ("5. Section Invariance", test5.get('supports_global_hierarchy', False)),
    ]

    passes = 0
    for name, passed in tests:
        result = "PASS" if passed else "FAIL"
        supports = "YES" if passed else "NO"
        print(f"| {name:30} | {result:6} | {supports:19} |")
        if passed:
            passes += 1

    print(f"\nTests passed: {passes}/5")

    # Verdict
    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)

    if passes >= 4:
        verdict = "SUPPORTED"
        conclusion = "Human-track encodes ordinal regimes (stress/intensity hierarchy)"
    elif passes <= 1:
        verdict = "FALSIFIED"
        conclusion = "Hierarchy incompatible with data; tokens are navigational only"
    else:
        verdict = "WEAK / LOCAL"
        conclusion = "Only section-local or weak ordering exists; not apparatus-global"

    print(f"\n  {verdict}")
    print(f"\n  {conclusion}")

    # Counter-evidence summary
    print("\n" + "-"*70)
    print("COUNTER-EVIDENCE:")
    print("-"*70)

    if not test1.get('global_ordering_stable', False):
        print("- Global ordering is NOT stable across sections")
    if not test2.get('supports_hierarchy', False):
        print("- Labels freely substitute in equivalent contexts")
    if not test3.get('supports_hierarchy', False):
        print(f"- Transitions are symmetric (bias={test3.get('directionality_bias', 0):.2f})")
    if not test4.get('supports_hierarchy', False):
        print(f"- Label distributions overlap smoothly (dominance={test4.get('mean_bin_dominance', 0):.2f})")
    if not test5.get('supports_global_hierarchy', False):
        print(f"- Rankings inconsistent across sections (consistency={test5.get('consistency', 0):.2%})")

    return results

if __name__ == '__main__':
    results = main()
