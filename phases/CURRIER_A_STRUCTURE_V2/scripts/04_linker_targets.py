"""
04_linker_targets.py

TEST 4: LINKER TARGET CHARACTERIZATION

Are collector folios (f93v, f32r) structurally distinct from other folios?

Questions:
- Do they have broader PP pools?
- Different cluster distribution?
- What makes them linker targets?
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import math

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("TEST 4: LINKER TARGET CHARACTERIZATION")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: IDENTIFY LINKER TARGETS
# =============================================================
print("\n[1/5] Identifying linker targets...")

# Build folio token inventory
folio_tokens = defaultdict(list)
for t in tx.currier_a():
    if t.word and '*' not in t.word:
        folio_tokens[t.folio].append(t)

# Find linker RI tokens (ct-prefix)
linker_ri = []
for folio, tokens in folio_tokens.items():
    # Get unique lines in folio
    lines = sorted(set(t.line for t in tokens))

    for line in lines:
        try:
            record = analyzer.analyze_record(folio, line)
            if not record:
                continue
            for t in record.tokens:
                if t.token_class == 'RI' and t.word and t.word.startswith('ct'):
                    linker_ri.append({
                        'folio': folio,
                        'line': line,
                        'word': t.word
                    })
        except:
            pass

print(f"   Found {len(linker_ri)} linker RI tokens")
for linker in linker_ri:
    print(f"   - {linker['word']} in {linker['folio']}:{linker['line']}")

# Known linker targets from previous analysis
known_targets = ['f93v', 'f32r']

linker_sources = set(l['folio'] for l in linker_ri)
print(f"\n   Linker source folios: {sorted(linker_sources)}")
print(f"   Known target folios: {known_targets}")

# =============================================================
# STEP 2: COMPARE TARGET vs NON-TARGET FOLIOS
# =============================================================
print("\n[2/5] Comparing target vs non-target folios...")

def analyze_folio(folio):
    """Comprehensive folio analysis."""
    tokens = folio_tokens.get(folio, [])
    lines = sorted(set(t.line for t in tokens))

    all_ri = []
    all_pp = []

    for line in lines:
        try:
            record = analyzer.analyze_record(folio, line)
            if record:
                for t in record.tokens:
                    if t.token_class == 'RI':
                        all_ri.append(t)
                    elif t.token_class == 'PP':
                        all_pp.append(t)
        except:
            pass

    # PP vocabulary
    pp_vocab = set(t.word for t in all_pp if t.word)

    # PP prefix distribution
    pp_prefixes = Counter()
    for t in all_pp:
        if t.word:
            try:
                m = morph.extract(t.word)
                if m.prefix:
                    pp_prefixes[m.prefix] += 1
            except:
                pass

    # RI vocabulary
    ri_vocab = set(t.word for t in all_ri if t.word)

    return {
        'folio': folio,
        'n_lines': len(lines),
        'n_tokens': len(tokens),
        'n_ri': len(all_ri),
        'n_pp': len(all_pp),
        'pp_vocab_size': len(pp_vocab),
        'ri_vocab_size': len(ri_vocab),
        'pp_prefixes': dict(pp_prefixes),
        'pp_vocab': pp_vocab,
        'ri_vocab': ri_vocab
    }

# Get all A folios
a_folios = sorted(folio_tokens.keys())
print(f"   Total Currier A folios: {len(a_folios)}")

# Analyze all folios
folio_analyses = {}
for folio in a_folios:
    folio_analyses[folio] = analyze_folio(folio)

# Separate targets and non-targets
target_analyses = [folio_analyses[f] for f in known_targets if f in folio_analyses]
non_target_analyses = [folio_analyses[f] for f in a_folios if f not in known_targets]

print(f"\n   Target folios analyzed: {len(target_analyses)}")
print(f"   Non-target folios analyzed: {len(non_target_analyses)}")

# =============================================================
# STEP 3: STATISTICAL COMPARISON
# =============================================================
print("\n[3/5] Statistical comparison...")

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

metrics = ['n_lines', 'n_tokens', 'n_ri', 'n_pp', 'pp_vocab_size', 'ri_vocab_size']

print(f"\n{'Metric':<22} {'Targets':>12} {'Non-Targets':>14} {'Ratio':>10}")
print("-" * 60)

comparison_results = {}
for metric in metrics:
    target_vals = [a[metric] for a in target_analyses]
    non_target_vals = [a[metric] for a in non_target_analyses]

    target_avg = avg(target_vals)
    non_target_avg = avg(non_target_vals)
    ratio = target_avg / non_target_avg if non_target_avg > 0 else float('inf')

    comparison_results[metric] = {
        'target_avg': target_avg,
        'non_target_avg': non_target_avg,
        'ratio': ratio if ratio != float('inf') else 999
    }

    ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "∞"
    marker = ""
    if ratio >= 1.5:
        marker = "↑↑"
    elif ratio >= 1.2:
        marker = "↑"
    elif ratio <= 0.5:
        marker = "↓↓"
    elif ratio <= 0.8:
        marker = "↓"

    print(f"{metric:<22} {target_avg:>12.1f} {non_target_avg:>14.1f} {ratio_str:>8} {marker}")

# =============================================================
# STEP 4: PP VOCABULARY OVERLAP ANALYSIS
# =============================================================
print("\n[4/5] PP vocabulary overlap analysis...")

# Target folios' combined PP vocabulary
target_pp_combined = set()
for a in target_analyses:
    target_pp_combined.update(a['pp_vocab'])

# Each non-target's overlap with target
overlaps = []
for a in non_target_analyses:
    overlap = len(a['pp_vocab'] & target_pp_combined)
    total = len(a['pp_vocab'])
    pct = 100 * overlap / total if total > 0 else 0
    overlaps.append((a['folio'], overlap, total, pct))

overlaps.sort(key=lambda x: x[3], reverse=True)

print(f"\nTarget PP vocabulary size (combined): {len(target_pp_combined)}")
print(f"\nTop 10 non-targets by overlap with target PP vocabulary:")
print(f"{'Folio':<10} {'Overlap':>10} {'Total':>10} {'%':>10}")
print("-" * 42)
for folio, overlap, total, pct in overlaps[:10]:
    print(f"{folio:<10} {overlap:>10} {total:>10} {pct:>9.1f}%")

print(f"\nBottom 5 (least overlap):")
for folio, overlap, total, pct in overlaps[-5:]:
    print(f"{folio:<10} {overlap:>10} {total:>10} {pct:>9.1f}%")

# Average overlap
avg_overlap_pct = avg([o[3] for o in overlaps])
print(f"\nAverage overlap: {avg_overlap_pct:.1f}%")

# =============================================================
# STEP 5: PREFIX PROFILE COMPARISON
# =============================================================
print("\n[5/5] PREFIX profile comparison...")

# Combine prefix counts for targets vs non-targets
target_prefixes = Counter()
non_target_prefixes = Counter()

for a in target_analyses:
    target_prefixes.update(a['pp_prefixes'])

for a in non_target_analyses:
    non_target_prefixes.update(a['pp_prefixes'])

all_prefixes = sorted(set(target_prefixes.keys()) | set(non_target_prefixes.keys()))

total_target = sum(target_prefixes.values())
total_non_target = sum(non_target_prefixes.values())

print(f"\n{'PREFIX':<12} {'Targets':>10} {'Non-Targets':>14} {'Ratio':>10}")
print("-" * 48)

prefix_comparison = {}
for prefix in all_prefixes:
    pct_target = 100 * target_prefixes[prefix] / total_target if total_target > 0 else 0
    pct_non_target = 100 * non_target_prefixes[prefix] / total_non_target if total_non_target > 0 else 0
    ratio = pct_target / pct_non_target if pct_non_target > 0 else float('inf') if pct_target > 0 else 1.0

    prefix_comparison[prefix] = {
        'target_pct': pct_target,
        'non_target_pct': pct_non_target,
        'ratio': ratio if ratio != float('inf') else 999
    }

    if pct_target > 1 or pct_non_target > 1:  # Only show significant prefixes
        ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "∞"
        marker = ""
        if ratio >= 1.5:
            marker = "↑↑"
        elif ratio <= 0.5:
            marker = "↓↓"
        print(f"{prefix:<12} {pct_target:>9.1f}% {pct_non_target:>13.1f}% {ratio_str:>8} {marker}")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

# Check for distinctive features
distinctive_features = []

# PP vocabulary size
if comparison_results['pp_vocab_size']['ratio'] >= 1.3:
    distinctive_features.append(f"BROADER PP vocabulary ({comparison_results['pp_vocab_size']['ratio']:.2f}x)")
elif comparison_results['pp_vocab_size']['ratio'] <= 0.7:
    distinctive_features.append(f"NARROWER PP vocabulary ({comparison_results['pp_vocab_size']['ratio']:.2f}x)")

# Line count
if comparison_results['n_lines']['ratio'] >= 1.3:
    distinctive_features.append(f"MORE lines ({comparison_results['n_lines']['ratio']:.2f}x)")

# RI count
if comparison_results['n_ri']['ratio'] >= 1.3:
    distinctive_features.append(f"MORE RI tokens ({comparison_results['n_ri']['ratio']:.2f}x)")

# Prefix differences
for prefix, data in prefix_comparison.items():
    if data['ratio'] >= 2.0:
        distinctive_features.append(f"ENRICHED for {prefix} prefix ({data['ratio']:.1f}x)")
    elif data['ratio'] <= 0.5:
        distinctive_features.append(f"DEPLETED for {prefix} prefix ({data['ratio']:.1f}x)")

if distinctive_features:
    print("\nDistinctive features of target folios:")
    for feature in distinctive_features:
        print(f"  - {feature}")
    verdict = "STRUCTURALLY_DISTINCT"
else:
    print("\nNo distinctive structural features found")
    verdict = "NOT_DISTINCT"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'LINKER_TARGET_CHARACTERIZATION',
    'linker_ri': linker_ri,
    'known_targets': known_targets,
    'n_target_folios': len(target_analyses),
    'n_non_target_folios': len(non_target_analyses),
    'metric_comparison': comparison_results,
    'prefix_comparison': prefix_comparison,
    'pp_vocabulary_overlap': {
        'target_combined_size': len(target_pp_combined),
        'avg_overlap_pct': avg_overlap_pct,
        'top_overlapping': [(o[0], o[3]) for o in overlaps[:10]]
    },
    'distinctive_features': distinctive_features,
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'linker_target_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
