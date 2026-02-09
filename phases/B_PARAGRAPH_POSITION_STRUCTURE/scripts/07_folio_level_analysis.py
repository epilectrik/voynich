"""
07_folio_level_analysis.py - Folio-level structural analysis

Analyze each B folio individually using LINE POSITION (not paragraph).
Divide folios into thirds: early lines / middle lines / late lines.

For each folio, measure:
- FL type distribution by position
- Prefix distribution by position
- Suffix distribution by position
- Token length patterns
- Vocabulary turnover (early vs late thirds)
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

# FL categories from C777
FL_CATEGORIES = {
    'ar': 'INITIAL', 'r': 'INITIAL', 'or': 'INITIAL',
    'al': 'LATE', 'l': 'LATE', 'ol': 'LATE',
    'aly': 'TERMINAL', 'am': 'TERMINAL', 'y': 'TERMINAL', 'dy': 'TERMINAL',
}

# Common prefixes
KERNEL_PREFIXES = {'ch', 'sh', 'cth', 'cph', 'ckh'}  # CHSH family
QO_PREFIXES = {'qo', 'o'}
AX_PREFIXES = {'ot', 'ok', 'op', 'of'}  # AX_INIT
INFRA_PREFIXES = {'da', 'do', 'sa', 'so'}

def classify_prefix(prefix):
    """Classify prefix into functional category."""
    if not prefix:
        return 'NONE'
    if prefix in KERNEL_PREFIXES:
        return 'CHSH'
    if prefix in QO_PREFIXES:
        return 'QO'
    if prefix in AX_PREFIXES:
        return 'AX'
    if prefix in INFRA_PREFIXES:
        return 'INFRA'
    if prefix and prefix[0] in {'k', 't', 'p', 'f'}:
        return 'GALLOWS'
    return 'OTHER'

def analyze_folio(folio, tokens, morph):
    """
    Comprehensive analysis of a single folio.

    Args:
        folio: folio identifier
        tokens: list of Token objects from that folio
        morph: Morphology instance

    Returns:
        dict with analysis results
    """
    # Group tokens by line
    lines = defaultdict(list)
    for t in tokens:
        lines[t.line].append(t)

    # Sort lines
    sorted_lines = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
    n_lines = len(sorted_lines)

    if n_lines < 3:
        return None

    # Divide into thirds
    third = n_lines // 3
    early_lines = sorted_lines[:third]
    middle_lines = sorted_lines[third:2*third]
    late_lines = sorted_lines[2*third:]

    def analyze_section(line_nums):
        """Analyze a section of lines."""
        section_tokens = []
        for ln in line_nums:
            section_tokens.extend(lines[ln])

        if not section_tokens:
            return None

        n = len(section_tokens)
        words = [t.word for t in section_tokens]

        # Morphological analysis
        prefixes = Counter()
        prefix_cats = Counter()
        suffixes = Counter()
        fl_types = Counter()
        middles = set()

        for word in words:
            m = morph.extract(word)
            if m:
                if m.prefix:
                    prefixes[m.prefix] += 1
                    prefix_cats[classify_prefix(m.prefix)] += 1
                else:
                    prefix_cats['NONE'] += 1

                if m.suffix:
                    suffixes[m.suffix] += 1
                    fl_type = FL_CATEGORIES.get(m.suffix)
                    if fl_type:
                        fl_types[fl_type] += 1

                if m.middle:
                    middles.add(m.middle)

        # Compute rates
        return {
            'n_tokens': n,
            'n_lines': len(line_nums),
            'unique_middles': len(middles),
            'vocab_density': len(middles) / n if n > 0 else 0,

            # FL rates
            'fl_initial_rate': fl_types.get('INITIAL', 0) / n,
            'fl_late_rate': fl_types.get('LATE', 0) / n,
            'fl_terminal_rate': fl_types.get('TERMINAL', 0) / n,
            'fl_total_rate': sum(fl_types.values()) / n,

            # Prefix category rates
            'chsh_rate': prefix_cats.get('CHSH', 0) / n,
            'qo_rate': prefix_cats.get('QO', 0) / n,
            'ax_rate': prefix_cats.get('AX', 0) / n,
            'infra_rate': prefix_cats.get('INFRA', 0) / n,
            'gallows_rate': prefix_cats.get('GALLOWS', 0) / n,

            # Raw counts for reference
            'fl_counts': dict(fl_types),
            'prefix_cats': dict(prefix_cats),
            'top_prefixes': prefixes.most_common(5),
            'top_suffixes': suffixes.most_common(5),
            'middles': middles,
        }

    early = analyze_section(early_lines)
    middle = analyze_section(middle_lines)
    late = analyze_section(late_lines)

    if not all([early, middle, late]):
        return None

    # Vocabulary overlap analysis
    early_vocab = early['middles']
    late_vocab = late['middles']

    vocab_overlap = len(early_vocab & late_vocab)
    vocab_early_only = len(early_vocab - late_vocab)
    vocab_late_only = len(late_vocab - early_vocab)

    jaccard = len(early_vocab & late_vocab) / len(early_vocab | late_vocab) if (early_vocab | late_vocab) else 0

    # Compute gradients (late - early)
    fl_terminal_gradient = late['fl_terminal_rate'] - early['fl_terminal_rate']
    fl_initial_gradient = late['fl_initial_rate'] - early['fl_initial_rate']
    ax_gradient = late['ax_rate'] - early['ax_rate']
    chsh_gradient = late['chsh_rate'] - early['chsh_rate']

    return {
        'folio': folio,
        'n_lines': n_lines,
        'n_tokens': early['n_tokens'] + middle['n_tokens'] + late['n_tokens'],

        'early': {k: v for k, v in early.items() if k != 'middles'},
        'middle': {k: v for k, v in middle.items() if k != 'middles'},
        'late': {k: v for k, v in late.items() if k != 'middles'},

        'vocabulary': {
            'early_unique': len(early_vocab),
            'late_unique': len(late_vocab),
            'overlap': vocab_overlap,
            'early_only': vocab_early_only,
            'late_only': vocab_late_only,
            'jaccard': jaccard,
        },

        'gradients': {
            'fl_terminal': fl_terminal_gradient,
            'fl_initial': fl_initial_gradient,
            'ax': ax_gradient,
            'chsh': chsh_gradient,
        }
    }

def main():
    tx = Transcript()
    morph = Morphology()

    # Group B tokens by folio
    folio_tokens = defaultdict(list)
    for t in tx.currier_b():
        folio_tokens[t.folio].append(t)

    print("=" * 80)
    print("FOLIO-LEVEL STRUCTURAL ANALYSIS - ALL B FOLIOS")
    print("=" * 80)
    print(f"\nTotal B folios: {len(folio_tokens)}")

    all_results = []

    # Aggregate metrics for summary
    terminal_gradients = []
    initial_gradients = []
    ax_gradients = []
    chsh_gradients = []
    jaccards = []

    print(f"\n{'Folio':<8} {'Lines':<6} {'Tok':<6} | {'FL_T early':<10} {'FL_T late':<10} {'dFL_T':<8} | {'AX early':<9} {'AX late':<9} {'dAX':<7} | {'Jaccard':<7}")
    print("-" * 110)

    for folio in sorted(folio_tokens.keys()):
        tokens = folio_tokens[folio]
        result = analyze_folio(folio, tokens, morph)

        if result is None:
            continue

        all_results.append(result)

        # Extract key metrics
        fl_t_early = result['early']['fl_terminal_rate']
        fl_t_late = result['late']['fl_terminal_rate']
        fl_t_grad = result['gradients']['fl_terminal']

        ax_early = result['early']['ax_rate']
        ax_late = result['late']['ax_rate']
        ax_grad = result['gradients']['ax']

        jacc = result['vocabulary']['jaccard']

        terminal_gradients.append(fl_t_grad)
        initial_gradients.append(result['gradients']['fl_initial'])
        ax_gradients.append(ax_grad)
        chsh_gradients.append(result['gradients']['chsh'])
        jaccards.append(jacc)

        # Highlight interesting cases
        highlight = ""
        if fl_t_grad > 0.05:
            highlight = "+FL_T"
        elif fl_t_grad < -0.05:
            highlight = "-FL_T"
        if ax_grad > 0.05:
            highlight += " +AX"
        elif ax_grad < -0.05:
            highlight += " -AX"

        print(f"{folio:<8} {result['n_lines']:<6} {result['n_tokens']:<6} | "
              f"{fl_t_early:>6.1%}     {fl_t_late:>6.1%}     {fl_t_grad:>+6.1%}   | "
              f"{ax_early:>6.1%}    {ax_late:>6.1%}    {ax_grad:>+5.1%}   | "
              f"{jacc:>5.2f}   {highlight}")

    # Summary statistics
    print("\n" + "=" * 80)
    print("AGGREGATE SUMMARY")
    print("=" * 80)

    print(f"\nFolios analyzed: {len(all_results)}")

    print(f"\n--- TERMINAL FL Gradient (late - early) ---")
    print(f"  Mean: {np.mean(terminal_gradients):+.3f}")
    print(f"  Std:  {np.std(terminal_gradients):.3f}")
    print(f"  Folios with increase (>0): {sum(1 for g in terminal_gradients if g > 0)} ({sum(1 for g in terminal_gradients if g > 0)/len(terminal_gradients)*100:.0f}%)")
    print(f"  Folios with decrease (<0): {sum(1 for g in terminal_gradients if g < 0)} ({sum(1 for g in terminal_gradients if g < 0)/len(terminal_gradients)*100:.0f}%)")

    print(f"\n--- AX Prefix Gradient (late - early) ---")
    print(f"  Mean: {np.mean(ax_gradients):+.3f}")
    print(f"  Std:  {np.std(ax_gradients):.3f}")
    print(f"  Folios with increase (>0): {sum(1 for g in ax_gradients if g > 0)} ({sum(1 for g in ax_gradients if g > 0)/len(ax_gradients)*100:.0f}%)")

    print(f"\n--- Vocabulary Overlap (early vs late thirds) ---")
    print(f"  Mean Jaccard: {np.mean(jaccards):.3f}")
    print(f"  Std:  {np.std(jaccards):.3f}")

    # Statistical tests
    from scipy import stats

    print(f"\n--- One-sample t-tests (is gradient different from 0?) ---")

    t_terminal, p_terminal = stats.ttest_1samp(terminal_gradients, 0)
    print(f"  FL_TERMINAL gradient: t={t_terminal:.2f}, p={p_terminal:.4f}")

    t_ax, p_ax = stats.ttest_1samp(ax_gradients, 0)
    print(f"  AX gradient: t={t_ax:.2f}, p={p_ax:.4f}")

    t_chsh, p_chsh = stats.ttest_1samp(chsh_gradients, 0)
    print(f"  CHSH gradient: t={t_chsh:.2f}, p={p_chsh:.4f}")

    # Interpretation
    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)

    if p_terminal < 0.05:
        direction = "INCREASES" if np.mean(terminal_gradients) > 0 else "DECREASES"
        print(f"\n[YES] TERMINAL FL {direction} from early to late lines (p={p_terminal:.4f})")
    else:
        print(f"\n[NO] No significant TERMINAL FL gradient (p={p_terminal:.4f})")

    if p_ax < 0.05:
        direction = "INCREASES" if np.mean(ax_gradients) > 0 else "DECREASES"
        print(f"[YES] AX prefix {direction} from early to late lines (p={p_ax:.4f})")
    else:
        print(f"[NO] No significant AX gradient (p={p_ax:.4f})")

    # Save results
    output = {
        'summary': {
            'folios_analyzed': len(all_results),
            'terminal_gradient_mean': float(np.mean(terminal_gradients)),
            'terminal_gradient_std': float(np.std(terminal_gradients)),
            'terminal_gradient_p': float(p_terminal),
            'ax_gradient_mean': float(np.mean(ax_gradients)),
            'ax_gradient_std': float(np.std(ax_gradients)),
            'ax_gradient_p': float(p_ax),
            'mean_jaccard': float(np.mean(jaccards)),
        },
        'folios': [
            {
                'folio': r['folio'],
                'n_lines': r['n_lines'],
                'n_tokens': r['n_tokens'],
                'gradients': r['gradients'],
                'vocabulary': r['vocabulary'],
                'early_fl_terminal': r['early']['fl_terminal_rate'],
                'late_fl_terminal': r['late']['fl_terminal_rate'],
                'early_ax': r['early']['ax_rate'],
                'late_ax': r['late']['ax_rate'],
            }
            for r in all_results
        ]
    }

    output_path = Path('C:/git/voynich/phases/B_PARAGRAPH_POSITION_STRUCTURE/results/07_folio_level_analysis.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return all_results

if __name__ == '__main__':
    main()
