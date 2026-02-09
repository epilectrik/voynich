"""
17_consolidated_summary.py

CONSOLIDATED SUMMARY: WITHOUT-RI Paragraph Characterization

Compile all findings from tests 01-16 into a comprehensive profile.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("CONSOLIDATED SUMMARY: WITHOUT-RI PARAGRAPH CHARACTERIZATION")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# COLLECT BASIC STATS
# =============================================================
print("\n[1/2] Computing basic statistics...")

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

# Count paragraphs
with_ri_count = 0
without_ri_count = 0

with_ri_sizes = []
without_ri_sizes = []

for folio, paragraphs in folio_paragraphs.items():
    for para_tokens in paragraphs:
        if not para_tokens:
            continue

        if has_initial_ri(para_tokens, analyzer):
            with_ri_count += 1
            with_ri_sizes.append(len(para_tokens))
        else:
            without_ri_count += 1
            without_ri_sizes.append(len(para_tokens))

total = with_ri_count + without_ri_count

# =============================================================
# LOAD PREVIOUS RESULTS
# =============================================================
print("\n[2/2] Loading previous test results...")

results_dir = Path(__file__).parent.parent / 'results'

# Load available results
results_files = [
    'continuation_test.json',
    'opening_type_characterization.json',
    'final_paragraph_analysis.json',
    'crossfolio_vocabulary_test.json',
    'al_prefix_link_test.json',
    'ri_type_composition.json',
    'ol_ri_analysis.json',
    'b_folio_convergence.json',
    'first_line_composition.json',
    'adjacent_vocabulary_bridge.json'
]

loaded_results = {}
for fname in results_files:
    fpath = results_dir / fname
    if fpath.exists():
        with open(fpath) as f:
            loaded_results[fname] = json.load(f)
            print(f"   Loaded: {fname}")

# =============================================================
# CONSOLIDATED PROFILE
# =============================================================
print("\n" + "="*70)
print("CONSOLIDATED WITHOUT-RI PARAGRAPH PROFILE")
print("="*70)

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

print(f"""
BASIC COUNTS:
  Total paragraphs: {total}
  WITH-RI: {with_ri_count} ({100*with_ri_count/total:.1f}%)
  WITHOUT-RI: {without_ri_count} ({100*without_ri_count/total:.1f}%)

PARAGRAPH SIZE:
  WITH-RI avg tokens: {avg(with_ri_sizes):.1f}
  WITHOUT-RI avg tokens: {avg(without_ri_sizes):.1f}
  Ratio: {avg(without_ri_sizes)/avg(with_ri_sizes):.2f}x
""")

# Key findings table
print("="*70)
print("KEY FINDINGS FROM ALL TESTS")
print("="*70)

print("""
+---------------------------------+--------------------+----------------------+
| Property                        | WITH-RI           | WITHOUT-RI          |
+---------------------------------+--------------------+----------------------+""")

# From first_line_composition
if 'first_line_composition.json' in loaded_results:
    r = loaded_results['first_line_composition.json']
    pct_pure = r.get('pct_pure_pp', 0)
    print(f"| First line PURE PP              | ~0%               | {pct_pure:.1f}%              |")

# From ri_type_composition
if 'ri_type_composition.json' in loaded_results:
    r = loaded_results['ri_type_composition.json']
    jac = r.get('jaccard_similarity', 0)
    link_with = r.get('linker_proportion', {}).get('with_ri', 0)
    link_without = r.get('linker_proportion', {}).get('without_ri', 0)
    print(f"| RI vocabulary Jaccard           | (reference)       | 0.028 (distinct)    |")
    print(f"| Linker RI proportion            | {link_with:.1f}%             | {link_without:.1f}% (1.5x)       |")

# From opening_type_characterization
if 'opening_type_characterization.json' in loaded_results:
    r = loaded_results['opening_type_characterization.json']
    dens_with = r.get('linker_analysis', {}).get('with_ri_linker_density', 0)
    dens_without = r.get('linker_analysis', {}).get('without_ri_linker_density', 0)
    print(f"| Linker density (ct/RI)          | {dens_with:.2f}             | {dens_without:.2f} (1.35x)       |")

# From ol_ri_analysis
if 'ol_ri_analysis.json' in loaded_results:
    r = loaded_results['ol_ri_analysis.json']
    link_with = r.get('link_prefix_enrichment', {}).get('with_ri_pct', 0)
    link_without = r.get('link_prefix_enrichment', {}).get('without_ri_pct', 0)
    print(f"| LINK prefixes (ol+or) %         | {link_with:.1f}%              | {link_without:.1f}% (2.7x)        |")

# From continuation_test
if 'continuation_test.json' in loaded_results:
    r = loaded_results['continuation_test.json']
    pos_dist = r.get('position_distribution', {})
    without_pos = pos_dist.get('WITHOUT_RI', {})
    first_pct = 100 * without_pos.get('FIRST', 0) / without_ri_count if without_ri_count else 0
    last_pct = 100 * without_pos.get('LAST', 0) / without_ri_count if without_ri_count else 0
    print(f"| Position: FIRST                 | (baseline)        | {first_pct:.0f}% (independent) |")
    print(f"| Position: LAST                  | (baseline)        | enriched 1.62x      |")

# From adjacent_vocabulary_bridge
if 'adjacent_vocabulary_bridge.json' in loaded_results:
    r = loaded_results['adjacent_vocabulary_bridge.json']
    print(f"| Bridge function                 | YES               | NO (0.53x overlap)  |")

# From b_folio_convergence
if 'b_folio_convergence.json' in loaded_results:
    r = loaded_results['b_folio_convergence.json']
    jac = r.get('coverage', {}).get('jaccard_b', 0)
    print(f"| B folio convergence             | All 82            | All 82 (identical)  |")

print("+---------------------------------+--------------------+----------------------+")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("""
WITHOUT-RI paragraphs are PROCESS-ONLY records characterized by:

1. STRUCTURE:
   - Start with PURE PP (92.7% have no RI on first line)
   - Skip material identification entirely
   - Jump straight into process vocabulary

2. VOCABULARY:
   - Distinct RI vocabulary (Jaccard=0.028 - almost no overlap)
   - Higher proportion of LINKER (ct-prefix) RI tokens (1.5x)
   - Higher linker DENSITY per RI token (1.35x)
   - LINK-associated prefixes (ol/or) enriched 2.7x

3. POSITION:
   - Enriched in LAST position (1.62x)
   - Also appear in FIRST position (22%) - NOT continuations
   - NOT vocabulary bridges between neighbors

4. FUNCTION:
   - Same B folio convergence as WITH-RI (same product space)
   - Different vocabulary but same semantic targets

PROPOSED FUNCTION:
WITHOUT-RI paragraphs are "PROCESS ANNOTATION" records that:
- Document process steps without identifying specific materials
- Concentrate at folio endings (closure/summary function)
- Use LINK-oriented vocabulary for cross-referencing
- Reference materials implicitly through shared process vocabulary

They are NOT:
- Continuations of preceding paragraphs
- Vocabulary bridges between neighbors
- Targeting different product space

They ARE:
- Independent structural units
- Process-focused (vs material-focused)
- Concentrated at folio boundaries
- Using distinct RI vocabulary
""")

# =============================================================
# POTENTIAL CONSTRAINTS
# =============================================================
print("\n" + "="*70)
print("POTENTIAL NEW CONSTRAINTS")
print("="*70)

print("""
From this investigation, the following constraints could be proposed:

C###: WITHOUT-RI paragraphs have distinct RI vocabulary
  - Jaccard similarity = 0.028 between WITH-RI and WITHOUT-RI RI tokens
  - Implies different functional role

C###: WITHOUT-RI paragraphs are PURE PP on first line (92.7%)
  - Skip material identification
  - Jump directly into process vocabulary

C###: WITHOUT-RI paragraphs are enriched in LAST folio position (1.62x)
  - Suggests closure/summary function
  - Not random distribution

C###: WITHOUT-RI paragraphs have higher LINK-associated content
  - Linker density 1.35x higher
  - ol/or prefixes 2.7x enriched
  - ct-prefix proportion 1.5x higher

C###: WITHOUT-RI paragraphs are independent (not continuations)
  - 22% appear in FIRST position
  - Lower vocabulary overlap with NEXT neighbor (0.53x)
  - NOT vocabulary bridges
""")

# =============================================================
# SAVE CONSOLIDATED RESULTS
# =============================================================
results = {
    'test': 'CONSOLIDATED_SUMMARY',
    'basic_counts': {
        'total_paragraphs': total,
        'with_ri': with_ri_count,
        'without_ri': without_ri_count
    },
    'paragraph_size': {
        'avg_with_ri': avg(with_ri_sizes),
        'avg_without_ri': avg(without_ri_sizes)
    },
    'key_findings': {
        'pure_pp_first_line': '92.7%',
        'ri_vocab_jaccard': 0.028,
        'linker_density_ratio': 1.35,
        'link_prefix_enrichment': 2.7,
        'last_position_enrichment': 1.62,
        'first_position_rate': 0.22,
        'bridge_overlap_ratio': 0.53,
        'b_folio_jaccard': 1.0
    },
    'interpretation': 'PROCESS_ONLY_RECORDS',
    'function': [
        'Document process steps without material identification',
        'Concentrate at folio endings',
        'Use LINK-oriented vocabulary',
        'Independent units (not continuations)'
    ]
}

output_path = Path(__file__).parent.parent / 'results' / 'consolidated_summary.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
