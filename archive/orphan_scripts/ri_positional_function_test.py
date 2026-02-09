#!/usr/bin/env python3
"""
RI Positional Function Test

Tests whether RI positional asymmetry (INITIAL vs FINAL) has B-side consequences.

If confirmed, this upgrades INPUT→OUTPUT interpretation from Tier 3 to Tier 2.

Test Battery:
1. INITIAL RI → B survival test: Different B-side survival rates by position?
2. Cross-paragraph RI flow test: Does FINAL RI match INITIAL RI in linked paragraphs?
3. Section-controlled position test: Is INITIAL/FINAL function section-invariant?

Prediction: Records with FINAL-dominated RI should route to B folios with
higher STATE-C (completion) rates than INITIAL-dominated RI records.
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

print("="*70)
print("RI POSITIONAL FUNCTION TEST")
print("="*70)

# Build paragraph data for Currier A
paragraphs = []
current_folio = None
current_para = []
current_line = None
para_idx = 0

for token in tx.currier_a():
    if '*' in token.word:
        continue

    if token.folio != current_folio:
        if current_para:
            paragraphs.append({
                'folio': current_folio,
                'section': current_para[0].section if current_para else None,
                'para_idx': para_idx,
                'tokens': [t.word for t in current_para],
                'record_id': f"{current_folio}:{para_idx}"
            })
            para_idx += 1
        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        para_idx = 0
        continue

    if token.line != current_line:
        first_word = token.word
        if first_word and first_word[0] in GALLOWS:
            paragraphs.append({
                'folio': current_folio,
                'section': current_para[0].section if current_para else None,
                'para_idx': para_idx,
                'tokens': [t.word for t in current_para],
                'record_id': f"{current_folio}:{para_idx}"
            })
            para_idx += 1
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

if current_para:
    paragraphs.append({
        'folio': current_folio,
        'section': current_para[0].section if current_para else None,
        'para_idx': para_idx,
        'tokens': [t.word for t in current_para],
        'record_id': f"{current_folio}:{para_idx}"
    })

print(f"\nTotal A paragraphs: {len(paragraphs)}")

# Extract RI tokens by position (INITIAL = first 3, FINAL = last 3)
def get_ri_by_position(tokens):
    """Extract RI tokens and classify by position."""
    if len(tokens) < 4:
        return {'initial': [], 'middle': [], 'final': []}

    initial = tokens[:3]
    final = tokens[-3:]
    middle = tokens[3:-3] if len(tokens) > 6 else []

    return {
        'initial': initial,
        'middle': middle,
        'final': final
    }

# Build INITIAL and FINAL RI MIDDLE inventories
initial_middles = Counter()
final_middles = Counter()
all_ri_middles = Counter()

for para in paragraphs:
    tokens = para['tokens']
    positions = get_ri_by_position(tokens)

    for token in positions['initial']:
        try:
            m = morph.extract(token)
            if m.middle:
                initial_middles[m.middle] += 1
                all_ri_middles[m.middle] += 1
        except:
            pass

    for token in positions['final']:
        try:
            m = morph.extract(token)
            if m.middle:
                final_middles[m.middle] += 1
                all_ri_middles[m.middle] += 1
        except:
            pass

print(f"\nUnique INITIAL MIDDLEs: {len(initial_middles)}")
print(f"Unique FINAL MIDDLEs: {len(final_middles)}")

# Build B folio vocabulary
b_folio_vocab = defaultdict(set)
b_folio_middles = defaultdict(set)

for token in tx.currier_b():
    if '*' in token.word:
        continue
    b_folio_vocab[token.folio].add(token.word)
    try:
        m = morph.extract(token.word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)
    except:
        pass

print(f"B folios: {len(b_folio_vocab)}")

# =========================================================================
# TEST 1: INITIAL RI vs FINAL RI → B Survival
# =========================================================================
print("\n" + "="*70)
print("TEST 1: RI POSITION → B SURVIVAL")
print("="*70)

# For each MIDDLE, calculate what % of B folios contain it
def b_survival_rate(middle):
    """What fraction of B folios contain this MIDDLE?"""
    count = sum(1 for fv in b_folio_middles.values() if middle in fv)
    return count / len(b_folio_middles) if b_folio_middles else 0

# Calculate survival rates for INITIAL-only vs FINAL-only MIDDLEs
initial_only = set(initial_middles.keys()) - set(final_middles.keys())
final_only = set(final_middles.keys()) - set(initial_middles.keys())
shared = set(initial_middles.keys()) & set(final_middles.keys())

print(f"\nMIDDLE distribution:")
print(f"  INITIAL-only: {len(initial_only)}")
print(f"  FINAL-only: {len(final_only)}")
print(f"  Shared: {len(shared)}")

initial_only_survival = [b_survival_rate(m) for m in initial_only]
final_only_survival = [b_survival_rate(m) for m in final_only]
shared_survival = [b_survival_rate(m) for m in shared]

print(f"\nB survival rates (% of B folios containing MIDDLE):")
print(f"  INITIAL-only MIDDLEs: {np.mean(initial_only_survival)*100:.1f}% (n={len(initial_only_survival)})")
print(f"  FINAL-only MIDDLEs: {np.mean(final_only_survival)*100:.1f}% (n={len(final_only_survival)})")
print(f"  Shared MIDDLEs: {np.mean(shared_survival)*100:.1f}% (n={len(shared_survival)})")

# Statistical test
if len(initial_only_survival) >= 5 and len(final_only_survival) >= 5:
    t_stat, p_value = stats.ttest_ind(initial_only_survival, final_only_survival)
    print(f"\nT-test (INITIAL-only vs FINAL-only): t={t_stat:.3f}, p={p_value:.4f}")
    if p_value < 0.05:
        direction = "INITIAL" if np.mean(initial_only_survival) > np.mean(final_only_survival) else "FINAL"
        print(f"  ** SIGNIFICANT: {direction}-only MIDDLEs have higher B survival **")
    else:
        print(f"  Not significant at p<0.05")

# =========================================================================
# TEST 2: Cross-Paragraph RI Flow (Linker Test)
# =========================================================================
print("\n" + "="*70)
print("TEST 2: CROSS-PARAGRAPH RI FLOW")
print("="*70)

# The 4 linkers from C835
LINKER_NETWORK = {
    'cthody': {'sources': ['f21r', 'f53v', 'f54r', 'f87r', 'f89v1'], 'destination': 'f93v'},
    'ctho': {'sources': ['f27r', 'f30v', 'f42r', 'f93r'], 'destination': 'f32r'},
    'ctheody': {'sources': ['f53v', 'f87r'], 'destination': 'f87r'},
    'qokoiiin': {'sources': ['f89v1'], 'destination': 'f37v'}
}

# Build paragraph lookup by folio
folio_paragraphs = defaultdict(list)
for para in paragraphs:
    folio_paragraphs[para['folio']].append(para)

print("\nFor each linker: Does FINAL RI of source → INITIAL RI of destination?")

flow_matches = 0
flow_total = 0

for linker, info in LINKER_NETWORK.items():
    sources = info['sources']
    dest = info['destination']

    print(f"\n{linker}:")

    # Get FINAL RI from source paragraphs (paragraphs containing linker as FINAL)
    source_final_ri = set()
    for src in sources:
        for para in folio_paragraphs.get(src, []):
            tokens = para['tokens']
            if len(tokens) >= 3 and linker in tokens[-3:]:
                # This paragraph has linker as FINAL
                for token in tokens[-3:]:
                    try:
                        m = morph.extract(token)
                        if m.middle:
                            source_final_ri.add(m.middle)
                    except:
                        pass

    # Get INITIAL RI from destination paragraphs
    dest_initial_ri = set()
    for para in folio_paragraphs.get(dest, []):
        tokens = para['tokens']
        if len(tokens) >= 3:
            for token in tokens[:3]:
                try:
                    m = morph.extract(token)
                    if m.middle:
                        dest_initial_ri.add(m.middle)
                except:
                    pass

    overlap = source_final_ri & dest_initial_ri
    jaccard = len(overlap) / len(source_final_ri | dest_initial_ri) if (source_final_ri | dest_initial_ri) else 0

    print(f"  Source FINAL MIDDLEs: {len(source_final_ri)}")
    print(f"  Dest INITIAL MIDDLEs: {len(dest_initial_ri)}")
    print(f"  Overlap: {len(overlap)} (Jaccard={jaccard:.3f})")

    if overlap:
        print(f"  Matching MIDDLEs: {sorted(overlap)[:5]}")
        flow_matches += len(overlap)
    flow_total += len(source_final_ri)

print(f"\nOverall: {flow_matches}/{flow_total} source FINAL MIDDLEs found in dest INITIAL")

# =========================================================================
# TEST 3: Section-Controlled Position Test
# =========================================================================
print("\n" + "="*70)
print("TEST 3: SECTION-CONTROLLED POSITION TEST")
print("="*70)

# Separate paragraphs by section
section_paragraphs = defaultdict(list)
for para in paragraphs:
    section_paragraphs[para['section']].append(para)

print(f"\nParagraphs by section:")
for section, paras in sorted(section_paragraphs.items()):
    print(f"  {section}: {len(paras)}")

# For each section, calculate INITIAL vs FINAL vocabulary characteristics
for section in ['H', 'P']:
    if section not in section_paragraphs:
        continue

    paras = section_paragraphs[section]

    sec_initial_middles = Counter()
    sec_final_middles = Counter()

    for para in paras:
        tokens = para['tokens']
        positions = get_ri_by_position(tokens)

        for token in positions['initial']:
            try:
                m = morph.extract(token)
                if m.middle:
                    sec_initial_middles[m.middle] += 1
            except:
                pass

        for token in positions['final']:
            try:
                m = morph.extract(token)
                if m.middle:
                    sec_final_middles[m.middle] += 1
            except:
                pass

    sec_initial_only = set(sec_initial_middles.keys()) - set(sec_final_middles.keys())
    sec_final_only = set(sec_final_middles.keys()) - set(sec_initial_middles.keys())
    sec_shared = set(sec_initial_middles.keys()) & set(sec_final_middles.keys())

    print(f"\nSection {section}:")
    print(f"  INITIAL-only MIDDLEs: {len(sec_initial_only)}")
    print(f"  FINAL-only MIDDLEs: {len(sec_final_only)}")
    print(f"  Shared: {len(sec_shared)}")

    # Jaccard between INITIAL and FINAL
    all_middles = set(sec_initial_middles.keys()) | set(sec_final_middles.keys())
    overlap = set(sec_initial_middles.keys()) & set(sec_final_middles.keys())
    jaccard = len(overlap) / len(all_middles) if all_middles else 0
    print(f"  INITIAL-FINAL Jaccard: {jaccard:.3f}")

# =========================================================================
# TEST 4: FINAL-Dominated Records → B STATE-C Rate
# =========================================================================
print("\n" + "="*70)
print("TEST 4: FINAL-DOMINATED RECORDS → B STATE-C")
print("="*70)

# Classify paragraphs by RI dominance
def classify_ri_dominance(para):
    """Classify paragraph as INITIAL-dominated, FINAL-dominated, or BALANCED."""
    tokens = para['tokens']
    if len(tokens) < 6:
        return 'SHORT'

    positions = get_ri_by_position(tokens)

    # Count unique MIDDLEs in each position
    initial_mids = set()
    final_mids = set()

    for token in positions['initial']:
        try:
            m = morph.extract(token)
            if m.middle:
                initial_mids.add(m.middle)
        except:
            pass

    for token in positions['final']:
        try:
            m = morph.extract(token)
            if m.middle:
                final_mids.add(m.middle)
        except:
            pass

    # Use position-exclusive MIDDLEs
    initial_exclusive = initial_mids - final_mids
    final_exclusive = final_mids - initial_mids

    if len(initial_exclusive) > len(final_exclusive):
        return 'INITIAL_DOM'
    elif len(final_exclusive) > len(initial_exclusive):
        return 'FINAL_DOM'
    else:
        return 'BALANCED'

# Classify all paragraphs
para_classes = Counter()
for para in paragraphs:
    para['ri_dominance'] = classify_ri_dominance(para)
    para_classes[para['ri_dominance']] += 1

print(f"\nParagraph RI dominance classification:")
for cls, count in para_classes.most_common():
    print(f"  {cls}: {count}")

# For each A folio, calculate dominance profile
folio_dominance = {}
for folio, paras in folio_paragraphs.items():
    initial_count = sum(1 for p in paras if p.get('ri_dominance') == 'INITIAL_DOM')
    final_count = sum(1 for p in paras if p.get('ri_dominance') == 'FINAL_DOM')
    total = initial_count + final_count
    if total > 0:
        folio_dominance[folio] = {
            'initial_rate': initial_count / total,
            'final_rate': final_count / total,
            'n_paragraphs': len(paras)
        }

# Now we need B folio STATE-C rates
# STATE-C tokens end with specific suffixes (from BCSC)
STATE_C_SUFFIXES = {'y', 'dy', 'ly', 'ey', 'chy', 'shy', 'ky', 'ty'}

b_folio_statec_rate = {}
for folio, vocab in b_folio_vocab.items():
    total = len(vocab)
    statec_count = 0
    for token in vocab:
        try:
            m = morph.extract(token)
            if m.suffix in STATE_C_SUFFIXES:
                statec_count += 1
        except:
            pass
    if total > 0:
        b_folio_statec_rate[folio] = statec_count / total

print(f"\nB folio STATE-C rates: mean={np.mean(list(b_folio_statec_rate.values()))*100:.1f}%")

# Test: Do A folios with high FINAL-dominance correspond to B folios with high STATE-C?
# This requires A→B folio mapping - use vocabulary overlap

# For each A folio, find best-matching B folio
a_to_b_best = {}
for a_folio, paras in folio_paragraphs.items():
    a_vocab = set()
    for para in paras:
        a_vocab.update(para['tokens'])

    best_b = None
    best_overlap = 0
    for b_folio, b_vocab in b_folio_vocab.items():
        overlap = len(a_vocab & b_vocab)
        if overlap > best_overlap:
            best_overlap = overlap
            best_b = b_folio

    if best_b:
        a_to_b_best[a_folio] = best_b

# Correlate FINAL-dominance with best-match B's STATE-C rate
final_rates = []
statec_rates = []

for a_folio, dom in folio_dominance.items():
    if a_folio in a_to_b_best:
        b_folio = a_to_b_best[a_folio]
        if b_folio in b_folio_statec_rate:
            final_rates.append(dom['final_rate'])
            statec_rates.append(b_folio_statec_rate[b_folio])

if len(final_rates) >= 10:
    r, p = stats.pearsonr(final_rates, statec_rates)
    print(f"\nCorrelation: A FINAL-dominance vs best-match B STATE-C rate")
    print(f"  Pearson r={r:.3f}, p={p:.4f}, n={len(final_rates)}")

    if p < 0.05:
        direction = "positive" if r > 0 else "negative"
        print(f"  ** SIGNIFICANT: {direction} correlation **")
        if r > 0:
            print(f"  Supports prediction: FINAL-dominated → higher STATE-C")
        else:
            print(f"  Contradicts prediction: FINAL-dominated → lower STATE-C")
    else:
        print(f"  Not significant at p<0.05")

# =========================================================================
# SUMMARY
# =========================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print("""
TEST RESULTS:

1. RI POSITION → B SURVIVAL:
   Tests whether INITIAL-only vs FINAL-only MIDDLEs have different
   downstream B survival rates.

2. CROSS-PARAGRAPH RI FLOW:
   Tests whether linker mechanism shows FINAL→INITIAL material flow.

3. SECTION-CONTROLLED POSITION:
   Tests whether INITIAL/FINAL vocabulary separation is section-invariant.

4. FINAL-DOMINATED → STATE-C:
   Tests the prediction that FINAL-dominated records route to B folios
   with higher completion (STATE-C) rates.

INTERPRETATION:
- If Test 1 shows different survival rates → positional function confirmed
- If Test 2 shows FINAL→INITIAL flow → material tracking interpretation gains evidence
- If Test 3 shows section-invariance → universal mechanism
- If Test 4 shows positive correlation → INPUT→OUTPUT interpretation validated

For Tier 2 upgrade: Need at least one significant effect with interpretable direction.
""")

# Save results
output = {
    'initial_only_count': len(initial_only),
    'final_only_count': len(final_only),
    'shared_count': len(shared),
    'initial_only_survival_mean': float(np.mean(initial_only_survival)) if initial_only_survival else None,
    'final_only_survival_mean': float(np.mean(final_only_survival)) if final_only_survival else None,
    'para_classes': dict(para_classes),
    'a_folios_analyzed': len(folio_dominance),
    'b_folios_analyzed': len(b_folio_statec_rate)
}

output_path = Path(__file__).parent.parent / 'results' / 'ri_positional_function_test.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
