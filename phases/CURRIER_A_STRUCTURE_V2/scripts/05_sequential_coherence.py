"""
05_sequential_coherence.py

TEST 5: SEQUENTIAL COHERENCE WITHIN PARAGRAPH TYPES

Do different paragraph types have different internal coherence patterns?

If YES → Cluster types reflect functional differences
If NO → Cluster types are measurement artifacts
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import math

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("TEST 5: SEQUENTIAL COHERENCE WITHIN PARAGRAPH TYPES")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD PARAGRAPH INVENTORY WITH CLUSTER TYPES
# =============================================================
print("\n[1/5] Building paragraph inventory...")

# Build paragraph structure
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

def classify_paragraph(para_tokens):
    """Classify paragraph into cluster types."""
    if not para_tokens:
        return "EMPTY"

    folio = para_tokens[0].folio
    lines = sorted(set(t.line for t in para_tokens))

    if not lines:
        return "EMPTY"

    first_line = lines[0]

    # Collect RI across all lines
    ri_tokens = []
    pp_tokens = []

    for line in lines:
        try:
            record = analyzer.analyze_record(folio, line)
            if record:
                for t in record.tokens:
                    if t.token_class == 'RI':
                        ri_tokens.append((line, t))
                    elif t.token_class == 'PP':
                        pp_tokens.append((line, t))
        except:
            pass

    n_lines = len(lines)
    n_tokens = len(para_tokens)

    # Check for linkers
    linker_ri = [t for l, t in ri_tokens if t.word and t.word.startswith('ct')]
    has_linker = len(linker_ri) > 0

    # Check RI positions
    first_line_ri = [t for l, t in ri_tokens if l == first_line]
    other_line_ri = [t for l, t in ri_tokens if l != first_line]

    # Classification
    if len(ri_tokens) == 0:
        return "NO_RI"
    if has_linker:
        return "LINKER_RICH"
    if n_lines <= 3 and len(ri_tokens) / max(n_tokens, 1) > 0.15:
        return "SHORT_RI_HEAVY"
    if len(first_line_ri) == 0 and len(other_line_ri) > 0:
        return "MIDDLE_RI_ONLY"

    return "STANDARD"

# Classify all paragraphs and collect PP sequences
paragraph_data = []
for folio, paragraphs in folio_paragraphs.items():
    for para_tokens in paragraphs:
        if not para_tokens:
            continue

        cluster_type = classify_paragraph(para_tokens)
        lines = sorted(set(t.line for t in para_tokens))

        # Get PP token sequence across all lines
        pp_sequence = []
        for line in lines:
            try:
                record = analyzer.analyze_record(folio, line)
                if record:
                    for t in record.tokens:
                        if t.token_class == 'PP' and t.word:
                            pp_sequence.append(t.word)
            except:
                pass

        paragraph_data.append({
            'folio': folio,
            'cluster_type': cluster_type,
            'pp_sequence': pp_sequence,
            'n_lines': len(lines),
            'n_tokens': len(para_tokens)
        })

print(f"   Classified {len(paragraph_data)} paragraphs")

# Distribution
cluster_dist = Counter(p['cluster_type'] for p in paragraph_data)
print(f"\nCluster type distribution:")
for ct, count in cluster_dist.most_common():
    print(f"   {ct}: {count} ({100*count/len(paragraph_data):.1f}%)")

# =============================================================
# STEP 2: COMPUTE COHERENCE METRICS
# =============================================================
print("\n[2/5] Computing coherence metrics...")

def compute_coherence(pp_sequence):
    """
    Compute coherence metrics for a PP sequence.

    Metrics:
    1. PREFIX continuity: How often consecutive tokens share PREFIX
    2. MIDDLE repetition: How often same MIDDLE appears
    3. Bigram entropy: How predictable is the next token given previous
    """
    if len(pp_sequence) < 2:
        return None

    # Extract morphology
    morphs = []
    for word in pp_sequence:
        try:
            m = morph.extract(word)
            morphs.append(m)
        except:
            morphs.append(None)

    # 1. PREFIX continuity
    prefix_matches = 0
    prefix_total = 0
    for i in range(len(morphs) - 1):
        if morphs[i] and morphs[i+1]:
            if morphs[i].prefix and morphs[i+1].prefix:
                prefix_total += 1
                if morphs[i].prefix == morphs[i+1].prefix:
                    prefix_matches += 1

    prefix_continuity = prefix_matches / prefix_total if prefix_total > 0 else 0

    # 2. MIDDLE repetition
    middles = [m.middle for m in morphs if m and m.middle]
    middle_counts = Counter(middles)
    if middles:
        max_repeat = max(middle_counts.values())
        middle_repetition = max_repeat / len(middles)
    else:
        middle_repetition = 0

    # 3. Bigram predictability (lower entropy = more coherent)
    bigram_counts = Counter()
    unigram_counts = Counter()
    for i in range(len(pp_sequence) - 1):
        bigram_counts[(pp_sequence[i], pp_sequence[i+1])] += 1
        unigram_counts[pp_sequence[i]] += 1

    # Conditional entropy H(next|prev)
    cond_entropy = 0
    total_bigrams = sum(bigram_counts.values())
    if total_bigrams > 0:
        for (prev, nxt), count in bigram_counts.items():
            p_bigram = count / total_bigrams
            p_next_given_prev = count / unigram_counts[prev]
            if p_next_given_prev > 0:
                cond_entropy -= p_bigram * math.log2(p_next_given_prev)

    # 4. Token uniqueness (lower = more repetitive)
    unique_ratio = len(set(pp_sequence)) / len(pp_sequence)

    return {
        'prefix_continuity': prefix_continuity,
        'middle_repetition': middle_repetition,
        'cond_entropy': cond_entropy,
        'unique_ratio': unique_ratio,
        'sequence_length': len(pp_sequence)
    }

# Compute for each paragraph
for p in paragraph_data:
    coherence = compute_coherence(p['pp_sequence'])
    p['coherence'] = coherence

# =============================================================
# STEP 3: COMPARE COHERENCE BY CLUSTER TYPE
# =============================================================
print("\n[3/5] Comparing coherence by cluster type...")

coherence_by_type = defaultdict(list)
for p in paragraph_data:
    if p['coherence']:
        coherence_by_type[p['cluster_type']].append(p['coherence'])

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

print(f"\n{'Cluster Type':<18} {'Prefix Cont':>12} {'Middle Rep':>12} {'Cond Entropy':>13} {'Unique Ratio':>13} {'N':>6}")
print("-" * 78)

coherence_summary = {}
for ct in sorted(coherence_by_type.keys()):
    metrics = coherence_by_type[ct]
    if not metrics:
        continue

    prefix_cont = avg([m['prefix_continuity'] for m in metrics])
    middle_rep = avg([m['middle_repetition'] for m in metrics])
    cond_ent = avg([m['cond_entropy'] for m in metrics])
    unique_rat = avg([m['unique_ratio'] for m in metrics])

    coherence_summary[ct] = {
        'prefix_continuity': prefix_cont,
        'middle_repetition': middle_rep,
        'cond_entropy': cond_ent,
        'unique_ratio': unique_rat,
        'n': len(metrics)
    }

    print(f"{ct:<18} {prefix_cont:>12.3f} {middle_rep:>12.3f} {cond_ent:>13.3f} {unique_rat:>13.3f} {len(metrics):>6}")

# =============================================================
# STEP 4: STATISTICAL SIGNIFICANCE
# =============================================================
print("\n[4/5] Testing statistical significance...")

# Compare STANDARD vs each other type
standard_metrics = coherence_by_type.get('STANDARD', [])

if standard_metrics:
    standard_prefix = [m['prefix_continuity'] for m in standard_metrics]
    standard_entropy = [m['cond_entropy'] for m in standard_metrics]

    print("\nComparison to STANDARD type:")
    for ct in coherence_by_type.keys():
        if ct == 'STANDARD' or not coherence_by_type[ct]:
            continue

        other_prefix = [m['prefix_continuity'] for m in coherence_by_type[ct]]
        other_entropy = [m['cond_entropy'] for m in coherence_by_type[ct]]

        # Simple t-test approximation (Welch's)
        def welch_t(a, b):
            if len(a) < 2 or len(b) < 2:
                return 0, 1.0
            mean_a, mean_b = avg(a), avg(b)
            var_a = sum((x - mean_a)**2 for x in a) / (len(a) - 1)
            var_b = sum((x - mean_b)**2 for x in b) / (len(b) - 1)
            se = ((var_a / len(a)) + (var_b / len(b))) ** 0.5
            if se == 0:
                return 0, 1.0
            t = (mean_a - mean_b) / se
            return t, 0.05 if abs(t) > 2 else 0.5

        t_prefix, p_prefix = welch_t(standard_prefix, other_prefix)
        t_entropy, p_entropy = welch_t(standard_entropy, other_entropy)

        prefix_diff = avg(other_prefix) - avg(standard_prefix)
        entropy_diff = avg(other_entropy) - avg(standard_entropy)

        sig_prefix = "**" if abs(t_prefix) > 2 else ""
        sig_entropy = "**" if abs(t_entropy) > 2 else ""

        print(f"\n   {ct} vs STANDARD:")
        print(f"      PREFIX continuity: {prefix_diff:+.3f} (t={t_prefix:.2f}) {sig_prefix}")
        print(f"      Conditional entropy: {entropy_diff:+.3f} (t={t_entropy:.2f}) {sig_entropy}")

# =============================================================
# STEP 5: PATTERN DISCOVERY
# =============================================================
print("\n[5/5] Pattern discovery...")

# Find paragraphs with unusual coherence
high_coherence = [p for p in paragraph_data if p['coherence'] and p['coherence']['prefix_continuity'] > 0.5]
low_entropy = [p for p in paragraph_data if p['coherence'] and p['coherence']['cond_entropy'] < 0.5]

print(f"\nHigh PREFIX continuity paragraphs (>0.5): {len(high_coherence)}")
for p in high_coherence[:5]:
    print(f"   {p['folio']} ({p['cluster_type']}) - continuity={p['coherence']['prefix_continuity']:.2f}")

print(f"\nLow conditional entropy paragraphs (<0.5): {len(low_entropy)}")
for p in low_entropy[:5]:
    print(f"   {p['folio']} ({p['cluster_type']}) - entropy={p['coherence']['cond_entropy']:.2f}")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

# Check if cluster types have different coherence profiles
if coherence_summary:
    # Range of metrics across types
    prefix_range = max(c['prefix_continuity'] for c in coherence_summary.values()) - min(c['prefix_continuity'] for c in coherence_summary.values())
    entropy_range = max(c['cond_entropy'] for c in coherence_summary.values()) - min(c['cond_entropy'] for c in coherence_summary.values())

    print(f"\nMetric ranges across cluster types:")
    print(f"   PREFIX continuity range: {prefix_range:.3f}")
    print(f"   Conditional entropy range: {entropy_range:.3f}")

    if prefix_range > 0.1 or entropy_range > 0.5:
        print(f"\n→ SIGNIFICANT VARIATION: Different cluster types have DIFFERENT coherence patterns")
        print("   This suggests cluster types reflect FUNCTIONAL differences")
        verdict = "FUNCTIONAL_DIFFERENCES"
    else:
        print(f"\n→ MINIMAL VARIATION: Cluster types have SIMILAR coherence patterns")
        print("   This suggests cluster types are MEASUREMENT ARTIFACTS")
        verdict = "MEASUREMENT_ARTIFACTS"
else:
    verdict = "INSUFFICIENT_DATA"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'SEQUENTIAL_COHERENCE',
    'n_paragraphs': len(paragraph_data),
    'cluster_distribution': dict(cluster_dist),
    'coherence_by_type': {k: {
        'prefix_continuity': avg([m['prefix_continuity'] for m in v]),
        'middle_repetition': avg([m['middle_repetition'] for m in v]),
        'cond_entropy': avg([m['cond_entropy'] for m in v]),
        'unique_ratio': avg([m['unique_ratio'] for m in v]),
        'n': len(v)
    } for k, v in coherence_by_type.items() if v},
    'high_coherence_examples': [
        {'folio': p['folio'], 'cluster_type': p['cluster_type'],
         'prefix_continuity': p['coherence']['prefix_continuity']}
        for p in high_coherence[:10]
    ],
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'sequential_coherence_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
