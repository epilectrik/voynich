"""
08_pp_triangulation_v2.py

PP Triangulation using voynich library properly.

Uses RecordAnalyzer for correct RI/PP classification,
aggregated at paragraph level.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import RecordAnalyzer, load_middle_classes

# Paths
results_dir = Path(__file__).parent.parent / "results"
para_results = Path(__file__).parent.parent.parent / "PARAGRAPH_INTERNAL_PROFILING" / "results"

print("="*70)
print("PP TRIANGULATION V2 - Using voynich library")
print("="*70)

# Load pre-computed RI/PP classification
ri_middles, pp_middles = load_middle_classes()
print(f"\nRI MIDDLEs (A-exclusive): {len(ri_middles)}")
print(f"PP MIDDLEs (A+B shared): {len(pp_middles)}")

# Load paragraph tokens
with open(para_results / "a_paragraph_tokens.json") as f:
    para_tokens = json.load(f)
print(f"A paragraphs: {len(para_tokens)}")

# Initialize analyzer (uses same classification)
analyzer = RecordAnalyzer()

# Analyze each paragraph
print("\n" + "="*70)
print("PARAGRAPH ANALYSIS")
print("="*70)

paragraph_profiles = []

for para_id, tokens in para_tokens.items():
    # Classify each token using the analyzer
    ri_tokens = []
    pp_tokens = []
    infra_tokens = []
    unknown_tokens = []

    for t in tokens:
        word = t['word']
        if not word or word.strip() == '':
            continue

        analysis = analyzer.analyze_token(word)

        if analysis.token_class == 'RI':
            ri_tokens.append({'word': word, 'middle': analysis.middle})
        elif analysis.token_class == 'PP':
            pp_tokens.append({'word': word, 'middle': analysis.middle})
        elif analysis.token_class == 'INFRA':
            infra_tokens.append({'word': word, 'middle': analysis.middle})
        else:
            unknown_tokens.append({'word': word, 'middle': analysis.middle})

    # Find initial RI (first RI tokens before first PP)
    initial_ri = []
    for t in tokens:
        word = t['word']
        if not word:
            continue
        analysis = analyzer.analyze_token(word)
        if analysis.token_class == 'RI':
            initial_ri.append({'word': word, 'middle': analysis.middle})
        elif analysis.token_class == 'PP':
            break  # Stop at first PP

    # Find final RI (last RI tokens after last PP)
    final_ri = []
    for t in reversed(tokens):
        word = t['word']
        if not word:
            continue
        analysis = analyzer.analyze_token(word)
        if analysis.token_class == 'RI':
            final_ri.insert(0, {'word': word, 'middle': analysis.middle})
        elif analysis.token_class == 'PP':
            break

    profile = {
        'para_id': para_id,
        'total_tokens': len(tokens),
        'ri_count': len(ri_tokens),
        'pp_count': len(pp_tokens),
        'infra_count': len(infra_tokens),
        'unknown_count': len(unknown_tokens),
        'initial_ri': initial_ri,
        'final_ri': final_ri,
        'ri_tokens': ri_tokens,
        'pp_tokens': pp_tokens,
    }

    paragraph_profiles.append(profile)

# Summary
print(f"\nAnalyzed {len(paragraph_profiles)} paragraphs")

# Count paragraphs with initial RI
has_initial_ri = [p for p in paragraph_profiles if p['initial_ri']]
print(f"Paragraphs with initial RI: {len(has_initial_ri)}")
print(f"Paragraphs WITHOUT initial RI: {len(paragraph_profiles) - len(has_initial_ri)}")

# Show examples
print("\n" + "="*70)
print("EXAMPLE PARAGRAPHS WITH INITIAL RI")
print("="*70)

for p in has_initial_ri[:10]:
    init_words = [t['word'] for t in p['initial_ri'][:3]]
    init_mids = [t['middle'] for t in p['initial_ri'][:3]]
    print(f"\n{p['para_id']}:")
    print(f"  Initial RI words: {init_words}")
    print(f"  Initial RI MIDDLEs: {init_mids}")
    print(f"  Total: {p['total_tokens']} tokens, {p['ri_count']} RI, {p['pp_count']} PP")

# Check for eoschso
print("\n" + "="*70)
print("CHECKING FOR eoschso")
print("="*70)

for p in paragraph_profiles:
    for t in p['ri_tokens']:
        if t['middle'] == 'eoschso':
            print(f"\nFound in {p['para_id']}:")
            print(f"  Word: {t['word']}")
            print(f"  Initial RI: {[x['middle'] for x in p['initial_ri'][:3]]}")
            print(f"  Is initial RI: {'eoschso' in [x['middle'] for x in p['initial_ri']]}")

# Statistics
print("\n" + "="*70)
print("STATISTICS")
print("="*70)

ri_counts = [p['ri_count'] for p in paragraph_profiles]
pp_counts = [p['pp_count'] for p in paragraph_profiles]
init_ri_counts = [len(p['initial_ri']) for p in paragraph_profiles]

import numpy as np
print(f"\nRI per paragraph: mean={np.mean(ri_counts):.1f}, median={np.median(ri_counts):.0f}")
print(f"PP per paragraph: mean={np.mean(pp_counts):.1f}, median={np.median(pp_counts):.0f}")
print(f"Initial RI count: mean={np.mean(init_ri_counts):.1f}, median={np.median(init_ri_counts):.0f}")

# Save results
output = {
    'total_paragraphs': len(paragraph_profiles),
    'with_initial_ri': len(has_initial_ri),
    'without_initial_ri': len(paragraph_profiles) - len(has_initial_ri),
    'ri_middles_count': len(ri_middles),
    'pp_middles_count': len(pp_middles),
    'profiles': paragraph_profiles[:50],  # First 50 for inspection
}

output_path = results_dir / "pp_triangulation_v2.json"
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nSaved to {output_path}")
