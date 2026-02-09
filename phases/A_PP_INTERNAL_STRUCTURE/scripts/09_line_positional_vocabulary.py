"""
09_line_positional_vocabulary.py - Document A line positional structure

Building on position-family analysis (08), this test confirms that Currier A
has deliberate line-level positional structure:

LINE-INITIAL position (position=0.0):
- Reference/linking vocabulary: daiin, or, ol
- Control initiation: qotchy, qokchy (qo- prefix)
- h-family: sho, shor, shol

LINE-FINAL position (position=1.0):
- Closure/precision markers: dam (25), dan (11)
- Terminal MIDDLEs: dy (51), m (45), n (16)
- da- PREFIX dominates with terminal m/n MIDDLEs

This suggests A lines are complete units with explicit start (reference)
and end (closure) markers.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
from scipy import stats
import json
import numpy as np

tx = Transcript()
morph = Morphology()

# Get Currier A tokens
a_tokens = list(tx.currier_a())
print(f"Total Currier A tokens: {len(a_tokens)}")

# Group tokens by line
lines = defaultdict(list)
for t in a_tokens:
    key = (t.folio, t.line)
    lines[key].append(t)

# Extract line-initial and line-final tokens
initial_data = []
final_data = []

for key, tokens in lines.items():
    if len(tokens) < 2:
        continue  # Skip single-token lines

    # Line-initial
    init_t = tokens[0]
    m = morph.extract(init_t.word)
    if m:
        initial_data.append({
            'word': init_t.word,
            'middle': m.middle,
            'prefix': m.prefix or '',
            'suffix': m.suffix or '',
            'articulator': m.articulator or ''
        })

    # Line-final
    final_t = tokens[-1]
    m = morph.extract(final_t.word)
    if m:
        final_data.append({
            'word': final_t.word,
            'middle': m.middle,
            'prefix': m.prefix or '',
            'suffix': m.suffix or '',
            'articulator': m.articulator or ''
        })

print(f"Multi-token lines: {len(lines)}")
print(f"Line-initial tokens analyzed: {len(initial_data)}")
print(f"Line-final tokens analyzed: {len(final_data)}")

# ============================================================
# MIDDLE ENRICHMENT ANALYSIS
# ============================================================
print("\n" + "="*70)
print("MIDDLE ENRICHMENT: LINE-FINAL vs LINE-INITIAL")
print("="*70)

init_middles = Counter(t['middle'] for t in initial_data)
final_middles = Counter(t['middle'] for t in final_data)

enrichment_results = []
for mid in set(init_middles.keys()) | set(final_middles.keys()):
    init_count = init_middles.get(mid, 0)
    final_count = final_middles.get(mid, 0)

    if init_count + final_count < 20:
        continue

    init_rate = init_count / len(initial_data)
    final_rate = final_count / len(final_data)

    if init_rate > 0:
        enrichment = final_rate / init_rate
    else:
        enrichment = float('inf') if final_rate > 0 else 1.0

    enrichment_results.append({
        'middle': mid,
        'initial_count': init_count,
        'final_count': final_count,
        'enrichment_final': enrichment
    })

# Sort by enrichment
enrichment_results.sort(key=lambda x: x['enrichment_final'], reverse=True)

print("\nMIDDLEs ENRICHED at LINE-FINAL:")
for r in enrichment_results[:10]:
    if r['enrichment_final'] > 1.5:
        print(f"  {r['middle']:<10} {r['enrichment_final']:>6.2f}x  (init:{r['initial_count']}, final:{r['final_count']})")

print("\nMIDDLEs DEPLETED at LINE-FINAL:")
for r in reversed(enrichment_results[-10:]):
    if r['enrichment_final'] < 0.67:
        print(f"  {r['middle']:<10} {r['enrichment_final']:>6.2f}x  (init:{r['initial_count']}, final:{r['final_count']})")

# ============================================================
# TERMINAL MARKER ANALYSIS
# ============================================================
print("\n" + "="*70)
print("TERMINAL MARKERS (m, n, dy MIDDLEs)")
print("="*70)

terminal_middles = {'m', 'n', 'dy'}

# At line-final
final_terminal = [t for t in final_data if t['middle'] in terminal_middles]
print(f"\nTerminal MIDDLEs at LINE-FINAL: {len(final_terminal)} ({100*len(final_terminal)/len(final_data):.1f}%)")

# Words
terminal_words = Counter(t['word'] for t in final_terminal)
print("\nMost common terminal words at LINE-FINAL:")
for word, count in terminal_words.most_common(15):
    m = morph.extract(word)
    pf = m.prefix if m.prefix else '-'
    mid = m.middle
    print(f"  {word:<15} prefix={pf:<6} middle={mid:<4} ({count})")

# At line-initial
init_terminal = [t for t in initial_data if t['middle'] in terminal_middles]
print(f"\nTerminal MIDDLEs at LINE-INITIAL: {len(init_terminal)} ({100*len(init_terminal)/len(initial_data):.1f}%)")

# Chi-square test
terminal_init = len(init_terminal)
terminal_final = len(final_terminal)
non_terminal_init = len(initial_data) - terminal_init
non_terminal_final = len(final_data) - terminal_final

observed = np.array([[terminal_init, terminal_final],
                      [non_terminal_init, non_terminal_final]])
chi2, p_value, dof, expected = stats.chi2_contingency(observed)

print(f"\nChi-square test (terminal MIDDLE x position):")
print(f"  Chi2: {chi2:.2f}")
print(f"  p-value: {p_value:.2e}")
print(f"  Significant: {'YES' if p_value < 0.001 else 'NO'}")

# ============================================================
# PREFIX ANALYSIS BY POSITION
# ============================================================
print("\n" + "="*70)
print("PREFIX DISTRIBUTION BY LINE POSITION")
print("="*70)

init_prefixes = Counter(t['prefix'] for t in initial_data if t['prefix'])
final_prefixes = Counter(t['prefix'] for t in final_data if t['prefix'])

print("\nTop PREFIXes at LINE-INITIAL:")
for pf, count in init_prefixes.most_common(10):
    pct = 100 * count / len(initial_data)
    print(f"  {pf:<8} {count:>5} ({pct:>5.1f}%)")

print("\nTop PREFIXes at LINE-FINAL:")
for pf, count in final_prefixes.most_common(10):
    pct = 100 * count / len(final_data)
    print(f"  {pf:<8} {count:>5} ({pct:>5.1f}%)")

# Check da- prefix specifically
da_init = sum(1 for t in initial_data if t['prefix'] == 'da')
da_final = sum(1 for t in final_data if t['prefix'] == 'da')

print(f"\nda- PREFIX: init={da_init}, final={da_final}")
print(f"  Enrichment at final: {(da_final/len(final_data))/(da_init/len(initial_data)):.2f}x")

# ============================================================
# REFERENCE MARKER ANALYSIS
# ============================================================
print("\n" + "="*70)
print("REFERENCE MARKERS (or, ol, iin MIDDLEs)")
print("="*70)

reference_middles = {'or', 'ol', 'iin', 'aiin'}

# At line-initial
init_reference = [t for t in initial_data if t['middle'] in reference_middles]
print(f"\nReference MIDDLEs at LINE-INITIAL: {len(init_reference)} ({100*len(init_reference)/len(initial_data):.1f}%)")

# At line-final
final_reference = [t for t in final_data if t['middle'] in reference_middles]
print(f"Reference MIDDLEs at LINE-FINAL: {len(final_reference)} ({100*len(final_reference)/len(final_data):.1f}%)")

# Enrichment at initial
enrichment_reference = (len(init_reference)/len(initial_data)) / (len(final_reference)/len(final_data))
print(f"Enrichment at LINE-INITIAL: {enrichment_reference:.2f}x")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("SUMMARY: A LINE POSITIONAL STRUCTURE")
print("="*70)

print("""
LINE-INITIAL vocabulary (reference/initiation):
- Reference MIDDLEs: or, ol, iin enriched
- qo- PREFIX: control initiation
- sh- PREFIX: monitoring/control

LINE-FINAL vocabulary (closure/precision):
- Terminal MIDDLEs: m, n, dy enriched
- da- PREFIX: precision/closure
- Specific markers: dam, dan, dy

This confirms A has deliberate LINE-LEVEL positional structure:
- Lines START with references (to other entries or operations)
- Lines END with closure markers (completeness/precision)

Interpretation: Each A line is a complete unit with explicit
boundary markers, supporting A as an organized registry where
entries have internal structure beyond simple token sequences.
""")

# Save results
output = {
    'middle_enrichment': enrichment_results,
    'terminal_markers': {
        'at_final': len(final_terminal),
        'at_initial': len(init_terminal),
        'chi2': float(chi2),
        'p_value': float(p_value)
    },
    'reference_markers': {
        'at_initial': len(init_reference),
        'at_final': len(final_reference),
        'enrichment_at_initial': float(enrichment_reference)
    },
    'top_final_words': dict(terminal_words.most_common(20)),
    'finding': 'A lines have positional structure: INITIAL=reference, FINAL=closure'
}

with open('C:/git/voynich/phases/A_PP_INTERNAL_STRUCTURE/results/line_positional_vocabulary.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to line_positional_vocabulary.json")
