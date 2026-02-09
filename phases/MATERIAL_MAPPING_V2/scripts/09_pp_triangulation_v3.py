"""
09_pp_triangulation_v3.py

PP Triangulation - Correct structure:
- Initial RI = RI tokens in FIRST LINE of paragraph
- Final RI = RI tokens in LAST LINE of paragraph
- PP = PP tokens in middle lines (processing)
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import RecordAnalyzer, load_middle_classes

results_dir = Path(__file__).parent.parent / "results"
para_results = Path(__file__).parent.parent.parent / "PARAGRAPH_INTERNAL_PROFILING" / "results"

print("="*70)
print("PP TRIANGULATION V3 - First/Last LINE structure")
print("="*70)

# Load classification
ri_middles, pp_middles = load_middle_classes()
analyzer = RecordAnalyzer()
print(f"\nRI MIDDLEs: {len(ri_middles)}, PP MIDDLEs: {len(pp_middles)}")

# Load paragraphs
with open(para_results / "a_paragraph_tokens.json") as f:
    para_tokens = json.load(f)
print(f"A paragraphs: {len(para_tokens)}")

# Analyze each paragraph by line
paragraph_profiles = []

for para_id, tokens in para_tokens.items():
    if not tokens:
        continue

    # Group by line
    lines = defaultdict(list)
    for t in tokens:
        lines[t['line']].append(t)

    # Sort line numbers
    sorted_lines = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else 0)

    if not sorted_lines:
        continue

    first_line = sorted_lines[0]
    last_line = sorted_lines[-1]

    # Classify tokens in first line
    first_line_ri = []
    first_line_pp = []
    for t in lines[first_line]:
        word = t['word']
        if not word:
            continue
        analysis = analyzer.analyze_token(word)
        if analysis.token_class == 'RI':
            first_line_ri.append({'word': word, 'middle': analysis.middle})
        elif analysis.token_class == 'PP':
            first_line_pp.append({'word': word, 'middle': analysis.middle})

    # Classify tokens in last line
    last_line_ri = []
    last_line_pp = []
    if last_line != first_line:
        for t in lines[last_line]:
            word = t['word']
            if not word:
                continue
            analysis = analyzer.analyze_token(word)
            if analysis.token_class == 'RI':
                last_line_ri.append({'word': word, 'middle': analysis.middle})
            elif analysis.token_class == 'PP':
                last_line_pp.append({'word': word, 'middle': analysis.middle})

    # Middle lines PP
    middle_pp = []
    middle_ri = []
    for line_num in sorted_lines[1:-1] if len(sorted_lines) > 2 else []:
        for t in lines[line_num]:
            word = t['word']
            if not word:
                continue
            analysis = analyzer.analyze_token(word)
            if analysis.token_class == 'PP':
                middle_pp.append({'word': word, 'middle': analysis.middle})
            elif analysis.token_class == 'RI':
                middle_ri.append({'word': word, 'middle': analysis.middle})

    profile = {
        'para_id': para_id,
        'n_lines': len(sorted_lines),
        'total_tokens': len(tokens),
        'first_line_ri': first_line_ri,
        'first_line_pp': first_line_pp,
        'last_line_ri': last_line_ri,
        'middle_pp': middle_pp,
        'middle_ri': middle_ri,
    }
    paragraph_profiles.append(profile)

# Summary
has_first_ri = [p for p in paragraph_profiles if p['first_line_ri']]
has_last_ri = [p for p in paragraph_profiles if p['last_line_ri']]

print(f"\nAnalyzed {len(paragraph_profiles)} paragraphs")
print(f"With initial RI (first line): {len(has_first_ri)} ({100*len(has_first_ri)/len(paragraph_profiles):.1f}%)")
print(f"With final RI (last line): {len(has_last_ri)} ({100*len(has_last_ri)/len(paragraph_profiles):.1f}%)")

# Examples
print("\n" + "="*70)
print("EXAMPLES WITH INITIAL RI")
print("="*70)

for p in has_first_ri[:10]:
    ri_words = [t['word'] for t in p['first_line_ri']]
    ri_mids = [t['middle'] for t in p['first_line_ri']]
    pp_count = len(p['middle_pp']) + len(p['first_line_pp'])
    print(f"\n{p['para_id']} ({p['n_lines']} lines):")
    print(f"  Initial RI words: {ri_words[:3]}")
    print(f"  Initial RI MIDDLEs: {ri_mids[:3]}")
    print(f"  PP tokens: {pp_count}")

# Check eoschso
print("\n" + "="*70)
print("CHECKING eoschso")
print("="*70)

for p in paragraph_profiles:
    # Check all RI tokens
    all_ri = p['first_line_ri'] + p['last_line_ri'] + p['middle_ri']
    for t in all_ri:
        if t['middle'] == 'eoschso':
            print(f"\nFound in {p['para_id']}:")
            print(f"  Word: {t['word']}")
            print(f"  In first line RI: {t in p['first_line_ri']}")
            print(f"  In last line RI: {t in p['last_line_ri']}")
            print(f"  In middle RI: {t in p['middle_ri']}")
            print(f"  First line RI: {[x['middle'] for x in p['first_line_ri']]}")

# Save
output = {
    'total_paragraphs': len(paragraph_profiles),
    'with_initial_ri': len(has_first_ri),
    'with_final_ri': len(has_last_ri),
    'profiles': paragraph_profiles,
}

with open(results_dir / "pp_triangulation_v3.json", 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nSaved results")
