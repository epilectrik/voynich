#!/usr/bin/env python3
"""
HT Perceptual Load Test
=======================

Research Question:
Does HT PREFIX index perceptual regime (load level)?

Correct Framing (Expert-Validated):
- HT is a grammar-generated perceptual load signal
- HT reflects how many sensory cues must be jointly integrated
- HT does NOT specify which sensory modalities to use
- Factor by PREFIX level (not subtract tokens)

Expected if true:
- EARLY prefixes (op-, pc-, do-) -> lower perceptual load -> visual-dominant contexts
- LATE prefixes (ta-) -> higher perceptual load -> olfactory-dominant contexts

Interpretation:
- Results show perceptual regime INDEXING, not modality ENCODING
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from scipy import stats
import json
from pathlib import Path

DATA_PATH = "C:/git/voynich/data/transcriptions/interlinear_full_words.txt"

# HT PREFIX definitions from C347/C348
HT_EARLY_PREFIXES = ['op', 'pc', 'do']
HT_LATE_PREFIXES = ['ta']
ALL_HT_PREFIXES = HT_EARLY_PREFIXES + HT_LATE_PREFIXES

# Grammar prefixes for context
GRAMMAR_PREFIXES = ['ch', 'sh', 'qo', 'ok', 'ol', 'or', 'ar', 'al', 'ot', 'da', 'sa']

# MIDDLE extraction (simplified)
def extract_middle(token):
    """Extract MIDDLE from token (between prefix and suffix)."""
    if not isinstance(token, str) or '*' in token:
        return None
    token = token.strip().lower()

    # Skip pure atoms
    if len(token) <= 2:
        return None

    # Try to extract middle portion
    # Common middles: 'o', 'a', 'e', 'y', etc.
    if len(token) >= 4:
        # Rough heuristic: middle is character 2-3 area
        middle = token[2:4] if len(token) > 4 else token[2:3]
        return middle
    return None


def get_ht_prefix_class(word):
    """Classify HT token by PREFIX (EARLY vs LATE)."""
    if pd.isna(word) or not isinstance(word, str):
        return None
    word = word.strip('"').lower()

    for prefix in HT_EARLY_PREFIXES:
        if word.startswith(prefix):
            return 'EARLY'
    for prefix in HT_LATE_PREFIXES:
        if word.startswith(prefix):
            return 'LATE'
    return None


def get_ht_prefix(word):
    """Get specific HT prefix."""
    if pd.isna(word) or not isinstance(word, str):
        return None
    word = word.strip('"').lower()

    for prefix in ALL_HT_PREFIXES:
        if word.startswith(prefix):
            return prefix
    return None


def is_ht_token(word):
    """Check if token is HT (including y-forms)."""
    if pd.isna(word) or not isinstance(word, str):
        return False
    word = word.strip('"').lower()

    # y-forms are HT
    if word.startswith('y'):
        return True
    # Named HT prefixes
    for prefix in ALL_HT_PREFIXES:
        if word.startswith(prefix):
            return True
    # Single letters
    if word in ['y', 'f', 'd', 'r']:
        return True
    return False


def is_grammar_token(word):
    """Check if token is grammar (not HT)."""
    if pd.isna(word) or not isinstance(word, str):
        return False
    word = word.strip('"').lower()

    if is_ht_token(word):
        return False
    if '*' in word:
        return False
    return len(word) >= 2


def compute_context_complexity(context_tokens):
    """
    Compute perceptual complexity proxy for a context.

    Uses:
    - MIDDLE rarity (rare = high complexity = olfactory-dominant)
    - Token diversity (high diversity = high complexity)
    """
    if not context_tokens:
        return {'middle_rarity': 0, 'diversity': 0, 'n_tokens': 0}

    middles = [extract_middle(t) for t in context_tokens if extract_middle(t)]
    unique_middles = len(set(middles))

    return {
        'n_tokens': len(context_tokens),
        'n_middles': len(middles),
        'unique_middles': unique_middles,
        'diversity': unique_middles / len(middles) if middles else 0
    }


def main():
    print("=" * 80)
    print("HT PERCEPTUAL LOAD TEST")
    print("=" * 80)
    print("\nResearch Question: Does HT PREFIX index perceptual regime (load level)?")
    print("\nCorrect Interpretation: HT as PERCEPTUAL LOAD signal, not modality encoding")

    # Load data
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
    # Filter to PRIMARY transcriber (H) only
    df = df[df['transcriber'] == 'H']
    df_b = df[df['language'] == 'B'].copy()

    print(f"\nLoaded {len(df_b)} Currier B tokens (H transcriber only)")

    # =========================================================================
    # ANALYSIS 1: HT PREFIX Distribution
    # =========================================================================
    print("\n" + "=" * 80)
    print("ANALYSIS 1: HT PREFIX DISTRIBUTION (Factored by Morphological Level)")
    print("=" * 80)

    prefix_counts = Counter()
    class_counts = Counter()

    for word in df_b['word']:
        prefix = get_ht_prefix(word)
        if prefix:
            prefix_counts[prefix] += 1
            cls = get_ht_prefix_class(word)
            if cls:
                class_counts[cls] += 1

    total_classified = sum(class_counts.values())

    print(f"\n{'PREFIX':<10} {'Count':<10} {'%':<10} {'Class':<10}")
    print("-" * 40)
    for prefix in sorted(prefix_counts.keys()):
        count = prefix_counts[prefix]
        pct = count / total_classified * 100 if total_classified > 0 else 0
        cls = 'EARLY' if prefix in HT_EARLY_PREFIXES else 'LATE'
        print(f"{prefix:<10} {count:<10} {pct:.1f}%      {cls:<10}")

    print(f"\n{'CLASS':<10} {'Count':<10} {'%':<10}")
    print("-" * 30)
    for cls in ['EARLY', 'LATE']:
        count = class_counts[cls]
        pct = count / total_classified * 100 if total_classified > 0 else 0
        print(f"{cls:<10} {count:<10} {pct:.1f}%")

    # =========================================================================
    # ANALYSIS 2: Context Complexity by HT PREFIX Class
    # =========================================================================
    print("\n" + "=" * 80)
    print("ANALYSIS 2: CONTEXT COMPLEXITY BY HT PREFIX CLASS")
    print("=" * 80)
    print("\nHypothesis: LATE prefixes appear in higher-complexity (olfactory) contexts")

    # Collect contexts around EARLY vs LATE HT tokens
    early_contexts = []
    late_contexts = []

    df_sorted = df_b.sort_values(['folio', 'line_number'])

    for (folio, line), group in df_sorted.groupby(['folio', 'line_number']):
        words = group['word'].tolist()

        for i, word in enumerate(words):
            cls = get_ht_prefix_class(word)
            if not cls:
                continue

            # Get context window (±3 tokens)
            context_start = max(0, i - 3)
            context_end = min(len(words), i + 4)
            context = [w for w in words[context_start:context_end]
                      if is_grammar_token(w)]

            complexity = compute_context_complexity(context)

            if cls == 'EARLY':
                early_contexts.append(complexity)
            else:
                late_contexts.append(complexity)

    # Compare
    print(f"\nEARLY contexts: n={len(early_contexts)}")
    print(f"LATE contexts: n={len(late_contexts)}")

    if early_contexts and late_contexts:
        early_diversity = [c['diversity'] for c in early_contexts if c['diversity'] > 0]
        late_diversity = [c['diversity'] for c in late_contexts if c['diversity'] > 0]

        if early_diversity and late_diversity:
            early_mean = np.mean(early_diversity)
            late_mean = np.mean(late_diversity)

            stat, p_value = stats.mannwhitneyu(early_diversity, late_diversity,
                                               alternative='two-sided')

            print(f"\nMIDDLE Diversity (proxy for perceptual complexity):")
            print(f"  EARLY mean: {early_mean:.4f}")
            print(f"  LATE mean:  {late_mean:.4f}")
            print(f"  Ratio (LATE/EARLY): {late_mean/early_mean:.3f}x")
            print(f"  Mann-Whitney U: {stat:.1f}, p={p_value:.4f}")

            if p_value < 0.05 and late_mean > early_mean:
                print("\n  -> LATE prefixes appear in HIGHER complexity contexts")
                print("  -> Consistent with LATE indexing higher perceptual load")
            elif p_value < 0.05 and early_mean > late_mean:
                print("\n  -> EARLY prefixes appear in HIGHER complexity contexts")
                print("  -> UNEXPECTED - needs investigation")
            else:
                print("\n  -> No significant difference in complexity")

    # =========================================================================
    # ANALYSIS 3: Grammar Prefix Association by HT Class
    # =========================================================================
    print("\n" + "=" * 80)
    print("ANALYSIS 3: GRAMMAR PREFIX ASSOCIATION BY HT CLASS")
    print("=" * 80)
    print("\nHypothesis: LATE appears more near k-type (ENERGY) contexts")
    print("           EARLY appears more near h-type (PHASE) contexts")

    # Collect grammar prefixes in EARLY vs LATE contexts
    early_grammar = Counter()
    late_grammar = Counter()

    for (folio, line), group in df_sorted.groupby(['folio', 'line_number']):
        words = group['word'].tolist()

        for i, word in enumerate(words):
            cls = get_ht_prefix_class(word)
            if not cls:
                continue

            # Look at adjacent grammar tokens
            for j in range(max(0, i-2), min(len(words), i+3)):
                if j == i:
                    continue
                adj_word = words[j]
                if not is_grammar_token(adj_word):
                    continue

                adj_word = adj_word.strip('"').lower()
                for prefix in GRAMMAR_PREFIXES:
                    if adj_word.startswith(prefix):
                        if cls == 'EARLY':
                            early_grammar[prefix] += 1
                        else:
                            late_grammar[prefix] += 1
                        break

    # Compute enrichment
    total_early = sum(early_grammar.values())
    total_late = sum(late_grammar.values())

    print(f"\n{'Grammar':<10} {'EARLY':<10} {'LATE':<10} {'LATE/EARLY':<12} {'Interpretation':<20}")
    print("-" * 70)

    enrichments = []
    for prefix in sorted(set(early_grammar.keys()) | set(late_grammar.keys())):
        e_count = early_grammar.get(prefix, 0)
        l_count = late_grammar.get(prefix, 0)

        e_rate = e_count / total_early if total_early > 0 else 0
        l_rate = l_count / total_late if total_late > 0 else 0

        enrichment = l_rate / e_rate if e_rate > 0 else float('inf')

        # Interpretation based on prefix type
        if prefix in ['ch', 'sh', 'ok']:
            interp = 'INTERVENTION (k-type)'
        elif prefix in ['da', 'sa']:
            interp = 'MONITORING'
        else:
            interp = 'OPERATIONAL'

        enrichments.append({
            'prefix': prefix,
            'early': e_count,
            'late': l_count,
            'enrichment': enrichment,
            'interp': interp
        })

        print(f"{prefix:<10} {e_count:<10} {l_count:<10} {enrichment:.2f}x        {interp:<20}")

    # Check if INTERVENTION prefixes are enriched in LATE
    intervention_prefixes = ['ch', 'sh', 'ok']
    intervention_early = sum(early_grammar.get(p, 0) for p in intervention_prefixes)
    intervention_late = sum(late_grammar.get(p, 0) for p in intervention_prefixes)

    int_early_rate = intervention_early / total_early if total_early > 0 else 0
    int_late_rate = intervention_late / total_late if total_late > 0 else 0
    int_enrichment = int_late_rate / int_early_rate if int_early_rate > 0 else 0

    print(f"\n{'INTERVENTION TOTAL':<10} {intervention_early:<10} {intervention_late:<10} {int_enrichment:.2f}x")

    if int_enrichment > 1.1:
        print("\n  -> LATE prefixes enriched near INTERVENTION contexts")
        print("  -> Consistent with LATE indexing higher perceptual load (k-type operations)")
    elif int_enrichment < 0.9:
        print("\n  -> EARLY prefixes enriched near INTERVENTION contexts")
        print("  -> UNEXPECTED pattern")
    else:
        print("\n  -> No significant enrichment difference")

    # =========================================================================
    # ANALYSIS 4: Section Distribution by HT Class
    # =========================================================================
    print("\n" + "=" * 80)
    print("ANALYSIS 4: SECTION DISTRIBUTION BY HT CLASS")
    print("=" * 80)
    print("\nHypothesis: LATE enriched in H section (highest MIDDLE diversity)")

    early_sections = Counter()
    late_sections = Counter()

    for _, row in df_b.iterrows():
        word = row['word']
        section = row.get('section', 'UNK')

        cls = get_ht_prefix_class(word)
        if cls == 'EARLY':
            early_sections[section] += 1
        elif cls == 'LATE':
            late_sections[section] += 1

    total_early = sum(early_sections.values())
    total_late = sum(late_sections.values())

    print(f"\n{'Section':<10} {'EARLY':<10} {'EARLY%':<10} {'LATE':<10} {'LATE%':<10} {'LATE/EARLY':<12}")
    print("-" * 65)

    for section in sorted(set(early_sections.keys()) | set(late_sections.keys())):
        e_count = early_sections.get(section, 0)
        l_count = late_sections.get(section, 0)

        e_pct = e_count / total_early * 100 if total_early > 0 else 0
        l_pct = l_count / total_late * 100 if total_late > 0 else 0

        enrichment = (l_pct / e_pct) if e_pct > 0 else float('inf')

        print(f"{section:<10} {e_count:<10} {e_pct:.1f}%      {l_count:<10} {l_pct:.1f}%      {enrichment:.2f}x")

    # =========================================================================
    # SUMMARY AND VERDICT
    # =========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY: HT PREFIX AS PERCEPTUAL LOAD INDEXER")
    print("=" * 80)

    results = {
        'test': 'HT Perceptual Load Test',
        'question': 'Does HT PREFIX index perceptual regime (load level)?',
        'interpretation': 'HT as perceptual load signal, not modality encoding',
        'prefix_distribution': {
            'EARLY': class_counts.get('EARLY', 0),
            'LATE': class_counts.get('LATE', 0)
        },
        'analyses': {
            'context_complexity': {
                'early_mean_diversity': float(np.mean(early_diversity)) if early_diversity else 0,
                'late_mean_diversity': float(np.mean(late_diversity)) if late_diversity else 0,
                'ratio': float(np.mean(late_diversity) / np.mean(early_diversity)) if early_diversity and late_diversity else 0
            },
            'intervention_enrichment': float(int_enrichment),
            'section_distribution': {
                'early': dict(early_sections),
                'late': dict(late_sections)
            }
        }
    }

    # Determine verdict
    evidence_for = []
    evidence_against = []

    if late_diversity and early_diversity:
        if np.mean(late_diversity) > np.mean(early_diversity):
            evidence_for.append("LATE appears in higher-complexity contexts")
        else:
            evidence_against.append("LATE does NOT appear in higher-complexity contexts")

    if int_enrichment > 1.1:
        evidence_for.append("LATE enriched near INTERVENTION (k-type) operations")
    elif int_enrichment < 0.9:
        evidence_against.append("LATE depleted near INTERVENTION operations")

    print(f"\nEvidence FOR perceptual load indexing:")
    for e in evidence_for:
        print(f"  + {e}")

    print(f"\nEvidence AGAINST perceptual load indexing:")
    for e in evidence_against:
        print(f"  - {e}")

    if len(evidence_for) >= 2:
        verdict = "SUPPORTED"
        print(f"\n-> VERDICT: {verdict}")
        print("  HT PREFIX correlates with perceptual regime")
        print("  EARLY = lower load (visual-dominant)")
        print("  LATE = higher load (multi-sensory integration)")
    elif len(evidence_against) >= 2:
        verdict = "NOT SUPPORTED"
        print(f"\n-> VERDICT: {verdict}")
        print("  HT PREFIX does not clearly index perceptual load")
    else:
        verdict = "INCONCLUSIVE"
        print(f"\n-> VERDICT: {verdict}")
        print("  Mixed evidence - further investigation needed")

    results['verdict'] = verdict
    results['evidence_for'] = evidence_for
    results['evidence_against'] = evidence_against

    # Save results
    output_path = Path("C:/git/voynich/results/ht_perceptual_load_test.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Final interpretation
    print("\n" + "=" * 80)
    print("EPISTEMIC NOTE")
    print("=" * 80)
    print("""
Even if SUPPORTED, this means:
  - HT PREFIX indexes DEGREE of perceptual integration required
  - HT PREFIX does NOT encode WHICH modalities to use
  - The mapping is: higher load -> more senses must be jointly integrated

This is perceptual COMPLEXITY indexing, not sensory INSTRUCTION.
The trained operator already knows which senses resolve which discrimination types.
HT marks WHERE careful multi-sensory integration is needed.
""")

    return results


if __name__ == '__main__':
    main()
