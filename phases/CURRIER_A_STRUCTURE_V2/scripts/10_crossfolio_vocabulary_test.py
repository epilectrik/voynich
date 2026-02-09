"""
10_crossfolio_vocabulary_test.py

CONFIRMING TEST: Cross-folio vocabulary analysis

If WITHOUT-RI paragraphs are relational/index records:
1. Their PP vocabulary should appear in MORE other folios (wider coverage)
2. They should reference vocabulary from multiple sources
3. They should have more "common" vocabulary (high-frequency cross-folio tokens)

This tests whether WITHOUT-RI paragraphs serve a cross-referencing function.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("CROSS-FOLIO VOCABULARY TEST")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD FOLIO-LEVEL PP VOCABULARY INDEX
# =============================================================
print("\n[1/4] Building folio-level PP vocabulary index...")

# Collect PP MIDDLEs per folio
folio_pp_middles = defaultdict(set)
for t in tx.currier_a():
    if t.word and '*' not in t.word:
        try:
            m = morph.extract(t.word)
            if m.middle:
                folio_pp_middles[t.folio].add(m.middle)
        except:
            pass

# Build reverse index: MIDDLE -> which folios contain it
middle_to_folios = defaultdict(set)
for folio, middles in folio_pp_middles.items():
    for middle in middles:
        middle_to_folios[middle].add(folio)

n_folios = len(folio_pp_middles)
print(f"   Total A folios: {n_folios}")
print(f"   Unique PP MIDDLEs: {len(middle_to_folios)}")

# Classify MIDDLEs by coverage
universal = [m for m, folios in middle_to_folios.items() if len(folios) >= n_folios * 0.5]
common = [m for m, folios in middle_to_folios.items() if n_folios * 0.2 <= len(folios) < n_folios * 0.5]
rare = [m for m, folios in middle_to_folios.items() if len(folios) < n_folios * 0.2]

print(f"   Universal MIDDLEs (>50% folios): {len(universal)}")
print(f"   Common MIDDLEs (20-50% folios): {len(common)}")
print(f"   Rare MIDDLEs (<20% folios): {len(rare)}")

# =============================================================
# STEP 2: BUILD PARAGRAPH INVENTORY WITH PP VOCABULARY
# =============================================================
print("\n[2/4] Building paragraph inventory...")

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

def has_initial_ri(para_tokens, analyzer):
    if not para_tokens:
        return False
    folio = para_tokens[0].folio
    first_line = para_tokens[0].line
    try:
        record = analyzer.analyze_record(folio, first_line)
        if record:
            for t in record.tokens:
                if t.token_class == 'RI':
                    return True
    except:
        pass
    return False

def get_para_pp_middles(para_tokens, analyzer, morph):
    """Get PP MIDDLEs from a paragraph."""
    if not para_tokens:
        return set()

    folio = para_tokens[0].folio
    lines = sorted(set(t.line for t in para_tokens))
    middles = set()

    for line in lines:
        try:
            record = analyzer.analyze_record(folio, line)
            if record:
                for t in record.tokens:
                    if t.token_class == 'PP' and t.word:
                        try:
                            m = morph.extract(t.word)
                            if m.middle:
                                middles.add(m.middle)
                        except:
                            pass
        except:
            pass
    return middles

# Collect paragraphs with their PP vocabulary
with_ri_paras = []
without_ri_paras = []

for folio, paragraphs in folio_paragraphs.items():
    for para_tokens in paragraphs:
        if not para_tokens:
            continue

        pp_middles = get_para_pp_middles(para_tokens, analyzer, morph)
        entry = {
            'folio': folio,
            'pp_middles': pp_middles,
            'n_middles': len(pp_middles)
        }

        if has_initial_ri(para_tokens, analyzer):
            with_ri_paras.append(entry)
        else:
            without_ri_paras.append(entry)

print(f"   WITH-RI paragraphs: {len(with_ri_paras)}")
print(f"   WITHOUT-RI paragraphs: {len(without_ri_paras)}")

# =============================================================
# STEP 3: COMPUTE CROSS-FOLIO COVERAGE METRICS
# =============================================================
print("\n[3/4] Computing cross-folio coverage metrics...")

def compute_coverage_metrics(para_entry, middle_to_folios, n_folios):
    """Compute cross-folio coverage for a paragraph's vocabulary."""
    pp_middles = para_entry['pp_middles']
    own_folio = para_entry['folio']

    if not pp_middles:
        return None

    # For each MIDDLE, count how many OTHER folios contain it
    cross_folio_counts = []
    for middle in pp_middles:
        other_folios = middle_to_folios[middle] - {own_folio}
        cross_folio_counts.append(len(other_folios))

    # Metrics
    avg_other_folios = sum(cross_folio_counts) / len(cross_folio_counts)
    max_other_folios = max(cross_folio_counts)

    # % of vocabulary that appears in >20% of folios
    threshold = n_folios * 0.2
    pct_common = 100 * sum(1 for c in cross_folio_counts if c >= threshold) / len(cross_folio_counts)

    # % of vocabulary that is folio-unique
    pct_unique = 100 * sum(1 for c in cross_folio_counts if c == 0) / len(cross_folio_counts)

    return {
        'avg_other_folios': avg_other_folios,
        'max_other_folios': max_other_folios,
        'pct_common_vocab': pct_common,
        'pct_unique_vocab': pct_unique,
        'n_middles': len(pp_middles)
    }

# Compute for all paragraphs
with_ri_metrics = [compute_coverage_metrics(p, middle_to_folios, n_folios) for p in with_ri_paras]
without_ri_metrics = [compute_coverage_metrics(p, middle_to_folios, n_folios) for p in without_ri_paras]

# Filter out None values
with_ri_metrics = [m for m in with_ri_metrics if m is not None]
without_ri_metrics = [m for m in without_ri_metrics if m is not None]

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

print(f"\nCROSS-FOLIO COVERAGE COMPARISON:")
print(f"{'Metric':<35} {'WITH-RI':>12} {'WITHOUT-RI':>14} {'Ratio':>10}")
print("-" * 73)

# Average other folios per MIDDLE
avg_with = avg([m['avg_other_folios'] for m in with_ri_metrics])
avg_without = avg([m['avg_other_folios'] for m in without_ri_metrics])
ratio = avg_without / avg_with if avg_with > 0 else float('inf')
marker = ">> WITHOUT" if ratio > 1.1 else "<< WITH" if ratio < 0.9 else ""
print(f"{'Avg other folios per MIDDLE:':<35} {avg_with:>12.2f} {avg_without:>14.2f} {ratio:>9.2f}x {marker}")

# % common vocabulary
avg_with = avg([m['pct_common_vocab'] for m in with_ri_metrics])
avg_without = avg([m['pct_common_vocab'] for m in without_ri_metrics])
ratio = avg_without / avg_with if avg_with > 0 else float('inf')
marker = ">> WITHOUT" if ratio > 1.1 else "<< WITH" if ratio < 0.9 else ""
print(f"{'% common vocabulary (>20% folios):':<35} {avg_with:>11.1f}% {avg_without:>13.1f}% {ratio:>9.2f}x {marker}")

# % unique vocabulary
avg_with = avg([m['pct_unique_vocab'] for m in with_ri_metrics])
avg_without = avg([m['pct_unique_vocab'] for m in without_ri_metrics])
ratio = avg_without / avg_with if avg_with > 0 else float('inf')
marker = ">> WITHOUT" if ratio > 1.1 else "<< WITH" if ratio < 0.9 else ""
print(f"{'% unique vocabulary (folio-only):':<35} {avg_with:>11.1f}% {avg_without:>13.1f}% {ratio:>9.2f}x {marker}")

# Vocabulary size
avg_with = avg([m['n_middles'] for m in with_ri_metrics])
avg_without = avg([m['n_middles'] for m in without_ri_metrics])
ratio = avg_without / avg_with if avg_with > 0 else float('inf')
print(f"{'Avg vocabulary size (MIDDLEs):':<35} {avg_with:>12.1f} {avg_without:>14.1f} {ratio:>9.2f}x")

# =============================================================
# STEP 4: STATISTICAL TEST
# =============================================================
print("\n[4/4] Statistical significance test...")

# Welch's t-test for avg_other_folios
def welch_t_test(a, b):
    if len(a) < 2 or len(b) < 2:
        return 0, 1.0
    mean_a = avg(a)
    mean_b = avg(b)
    var_a = sum((x - mean_a)**2 for x in a) / (len(a) - 1)
    var_b = sum((x - mean_b)**2 for x in b) / (len(b) - 1)
    se = ((var_a / len(a)) + (var_b / len(b))) ** 0.5
    if se == 0:
        return 0, 1.0
    t = (mean_a - mean_b) / se
    # Rough p-value: |t| > 2 roughly p < 0.05, |t| > 2.6 roughly p < 0.01
    if abs(t) > 2.6:
        p = 0.01
    elif abs(t) > 2.0:
        p = 0.05
    else:
        p = 0.5
    return t, p

with_ri_coverage = [m['avg_other_folios'] for m in with_ri_metrics]
without_ri_coverage = [m['avg_other_folios'] for m in without_ri_metrics]

t_stat, p_val = welch_t_test(with_ri_coverage, without_ri_coverage)
print(f"\nCross-folio coverage difference:")
print(f"   t-statistic: {t_stat:.2f}")
print(f"   p-value: {'< 0.01' if p_val <= 0.01 else '< 0.05' if p_val <= 0.05 else '>= 0.05'}")

if p_val <= 0.05:
    if avg(without_ri_coverage) > avg(with_ri_coverage):
        print(f"   SIGNIFICANT: WITHOUT-RI has HIGHER cross-folio coverage")
        significance = "WITHOUT_RI_HIGHER"
    else:
        print(f"   SIGNIFICANT: WITH-RI has HIGHER cross-folio coverage")
        significance = "WITH_RI_HIGHER"
else:
    print(f"   NOT SIGNIFICANT")
    significance = "NOT_SIGNIFICANT"

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION: Is the relational/index hypothesis confirmed?")
print("="*70)

print("\nHypothesis: WITHOUT-RI paragraphs are relational/index records")
print("           serving a cross-referencing function.")
print("\nPrediction: WITHOUT-RI should have HIGHER cross-folio vocabulary coverage")
print("-" * 70)

avg_coverage_with = avg(with_ri_coverage)
avg_coverage_without = avg(without_ri_coverage)

if avg_coverage_without > avg_coverage_with * 1.05 and significance != "WITH_RI_HIGHER":
    print(f"\n✓ CONFIRMED: WITHOUT-RI vocabulary appears in {avg_coverage_without:.1f} other folios")
    print(f"             vs WITH-RI vocabulary in {avg_coverage_with:.1f} other folios")
    print(f"             ({avg_coverage_without/avg_coverage_with:.2f}x ratio)")
    verdict = "CONFIRMED"
elif avg_coverage_with > avg_coverage_without * 1.05:
    print(f"\n✗ CONTRADICTED: WITH-RI actually has HIGHER cross-folio coverage")
    print(f"                ({avg_coverage_with:.1f} vs {avg_coverage_without:.1f})")
    verdict = "CONTRADICTED"
else:
    print(f"\n? INCONCLUSIVE: Similar coverage ({avg_coverage_with:.1f} vs {avg_coverage_without:.1f})")
    verdict = "INCONCLUSIVE"

# Additional evidence
print("\nAdditional evidence:")
common_with = avg([m['pct_common_vocab'] for m in with_ri_metrics])
common_without = avg([m['pct_common_vocab'] for m in without_ri_metrics])
if common_without > common_with * 1.05:
    print(f"  + WITHOUT-RI has more common vocabulary ({common_without:.1f}% vs {common_with:.1f}%)")
else:
    print(f"  - WITHOUT-RI does NOT have more common vocabulary ({common_without:.1f}% vs {common_with:.1f}%)")

unique_with = avg([m['pct_unique_vocab'] for m in with_ri_metrics])
unique_without = avg([m['pct_unique_vocab'] for m in without_ri_metrics])
if unique_with > unique_without * 1.05:
    print(f"  + WITH-RI has more unique vocabulary ({unique_with:.1f}% vs {unique_without:.1f}%)")
    print(f"    -> Supports: WITH-RI = substance records with specific identifiers")
else:
    print(f"  - WITH-RI does NOT have more unique vocabulary ({unique_with:.1f}% vs {unique_without:.1f}%)")

# Final verdict
print("\n" + "="*70)
print("FINAL VERDICT")
print("="*70)

if verdict == "CONFIRMED":
    print("""
WITHOUT-RI paragraphs ARE relational/index records:
- Higher cross-folio vocabulary coverage (connects to more other folios)
- Combined with: higher linker density, fewer RI tokens, LAST position enrichment
- Function: Cross-reference sections linking materials across the registry
""")
elif verdict == "CONTRADICTED":
    print("""
Relational/index hypothesis NOT supported by cross-folio vocabulary.
Alternative interpretation needed.
""")
else:
    print("""
Cross-folio evidence is INCONCLUSIVE.
The hypothesis remains plausible based on other evidence:
- Higher linker density (1.35x)
- LAST position enrichment (1.62x)
- Fewer RI tokens overall
""")

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'CROSSFOLIO_VOCABULARY_TEST',
    'n_folios': n_folios,
    'vocabulary_classification': {
        'universal': len(universal),
        'common': len(common),
        'rare': len(rare)
    },
    'coverage_metrics': {
        'with_ri_avg_other_folios': avg(with_ri_coverage),
        'without_ri_avg_other_folios': avg(without_ri_coverage),
        'with_ri_pct_common': avg([m['pct_common_vocab'] for m in with_ri_metrics]),
        'without_ri_pct_common': avg([m['pct_common_vocab'] for m in without_ri_metrics]),
        'with_ri_pct_unique': avg([m['pct_unique_vocab'] for m in with_ri_metrics]),
        'without_ri_pct_unique': avg([m['pct_unique_vocab'] for m in without_ri_metrics])
    },
    'statistical_test': {
        't_statistic': t_stat,
        'significance': significance
    },
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'crossfolio_vocabulary_test.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
