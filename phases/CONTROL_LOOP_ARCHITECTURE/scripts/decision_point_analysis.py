#!/usr/bin/env python3
"""
Gap 3: Decision Point Architecture

How do line-final tokens encode cycle continuation vs termination?
f75r P9 L44 showed `otam` (adjust-accept-final) next to `olaiin` (close-iterate-halt).
Are line-final tokens systematically different? Do they encode stop/continue decisions?

Output: phases/CONTROL_LOOP_ARCHITECTURE/results/decision_point_analysis.json
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'phases' / 'CONTROL_LOOP_ARCHITECTURE' / 'results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tx = Transcript()
morph = Morphology()

# Atom glosses for interpretation
CHAR_GLOSS = {
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'halt', 'a': 'accept', 'm': 'final',
    'd': 'seal', 't': 'drive', 'c': 'adjust', 'p': 'pause',
    'f': 'flag', 's': 'separate', 'g': 'complete',
    'o': 'vessel', 'l': 'collect', 'r': 'flow',
}

# Suffix categories
TERMINAL_SUFFIXES = {'dy', 'edy', 'eey', 'ey', 'hy', 'ry', 'ly', 'am', 'om'}
CHECKPOINT_SUFFIXES = {'ain', 'aiin', 'iin', 'oiin'}
ITERATIVE_SUFFIXES = {'in', 'an', 's'}

def classify_suffix(suffix):
    if suffix is None:
        return 'BARE'
    if suffix in TERMINAL_SUFFIXES:
        return 'TERMINAL'
    if suffix in CHECKPOINT_SUFFIXES:
        return 'CHECKPOINT'
    if suffix in ITERATIVE_SUFFIXES:
        return 'ITERATIVE'
    return 'OTHER'

def gloss_word(word):
    """Simple atom-level gloss."""
    m = morph.extract(word)
    parts = []
    if m.prefix:
        parts.append(m.prefix + ':')
    if m.middle:
        for c in m.middle:
            parts.append(CHAR_GLOSS.get(c, c))
    if m.suffix:
        parts.append(f'-{m.suffix}')
    return ' '.join(parts)

# ============================================================
# COLLECT DATA
# ============================================================
print("Analyzing line-final vs line-medial tokens in Currier B...")

folio_lines = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    if token.is_label:
        continue
    folio_lines[token.folio][token.line].append(token)

# Categorize tokens by position
final_tokens = []
penultimate_tokens = []
medial_tokens = []
initial_tokens = []

for folio in folio_lines:
    for line in folio_lines[folio]:
        tokens = folio_lines[folio][line]
        n = len(tokens)
        if n < 4:
            continue
        initial_tokens.append(tokens[0])
        for t in tokens[1:-2]:
            medial_tokens.append(t)
        penultimate_tokens.append(tokens[-2])
        final_tokens.append(tokens[-1])

print(f"  Final tokens: {len(final_tokens)}")
print(f"  Penultimate: {len(penultimate_tokens)}")
print(f"  Medial: {len(medial_tokens)}")
print(f"  Initial: {len(initial_tokens)}")

# ============================================================
# ANALYSIS 1: Suffix distribution by position
# ============================================================
print("\n=== SUFFIX CATEGORY BY POSITION ===")

for label, token_list in [('INITIAL', initial_tokens), ('MEDIAL', medial_tokens),
                           ('PENULTIMATE', penultimate_tokens), ('FINAL', final_tokens)]:
    cats = Counter()
    for t in token_list:
        m = morph.extract(t.word)
        cat = classify_suffix(m.suffix)
        cats[cat] += 1
    total = sum(cats.values())
    print(f"\n  {label} (n={total}):")
    for cat in ['TERMINAL', 'CHECKPOINT', 'ITERATIVE', 'BARE', 'OTHER']:
        print(f"    {cat:12s}: {cats[cat]:5d} ({cats[cat]/total*100:.1f}%)")

# ============================================================
# ANALYSIS 2: MIDDLE atom distribution at line-final position
# ============================================================
print("\n=== MIDDLE ATOMS AT LINE-FINAL vs MEDIAL ===")

def get_atom_dist(token_list):
    atoms = Counter()
    for t in token_list:
        m = morph.extract(t.word)
        if m.middle:
            for c in m.middle:
                if c in CHAR_GLOSS:
                    atoms[c] += 1
    return atoms

final_atoms = get_atom_dist(final_tokens)
medial_atoms = get_atom_dist(medial_tokens)

# Normalize
final_total = sum(final_atoms.values())
medial_total = sum(medial_atoms.values())

print(f"\n  Atom enrichment at FINAL position (vs MEDIAL):")
for atom in sorted(CHAR_GLOSS.keys()):
    f_rate = final_atoms[atom] / final_total if final_total > 0 else 0
    m_rate = medial_atoms[atom] / medial_total if medial_total > 0 else 0
    enrichment = f_rate / m_rate if m_rate > 0 else float('inf')
    if final_atoms[atom] >= 10:
        marker = '***' if enrichment > 2.0 or enrichment < 0.5 else ''
        print(f"    {atom} ({CHAR_GLOSS[atom]:8s}): FINAL={f_rate*100:5.1f}%  MEDIAL={m_rate*100:5.1f}%  enrichment={enrichment:.2f}x {marker}")

# ============================================================
# ANALYSIS 3: PREFIX distribution at line-final position
# ============================================================
print("\n=== PREFIX AT LINE-FINAL vs MEDIAL ===")

def get_prefix_dist(token_list):
    prefixes = Counter()
    for t in token_list:
        m = morph.extract(t.word)
        if m.prefix:
            prefixes[m.prefix] += 1
    return prefixes

final_prefixes = get_prefix_dist(final_tokens)
medial_prefixes = get_prefix_dist(medial_tokens)

final_p_total = sum(final_prefixes.values())
medial_p_total = sum(medial_prefixes.values())

print(f"\n  Top final prefixes (n={final_p_total}):")
for p, c in final_prefixes.most_common(10):
    f_rate = c / final_p_total
    m_rate = medial_prefixes[p] / medial_p_total if medial_p_total > 0 else 0
    enrichment = f_rate / m_rate if m_rate > 0 else float('inf')
    print(f"    {p:6s}: {c:4d} ({f_rate*100:5.1f}%), enrichment={enrichment:.2f}x")

# ============================================================
# ANALYSIS 4: Specific decision point patterns
# ============================================================
print("\n=== DECISION POINT PATTERNS ===")
print("(Line-final tokens that encode stop/continue)")

# Classify line-final tokens by their "decision"
stop_tokens = []  # Tokens suggesting termination (terminal suffix, m atom)
continue_tokens = []  # Tokens suggesting continuation (checkpoint suffix, i atom)
neutral_tokens = []

for t in final_tokens:
    m = morph.extract(t.word)
    cat = classify_suffix(m.suffix)
    has_m = m.middle and 'm' in m.middle
    has_i = m.middle and 'i' in m.middle
    has_n = m.middle and 'n' in m.middle

    if cat == 'TERMINAL' or has_m:
        stop_tokens.append(t)
    elif cat == 'CHECKPOINT' or cat == 'ITERATIVE' or (has_i and not has_m):
        continue_tokens.append(t)
    else:
        neutral_tokens.append(t)

total_final = len(final_tokens)
print(f"\n  STOP signals (terminal suffix or m-atom): {len(stop_tokens)} ({len(stop_tokens)/total_final*100:.1f}%)")
print(f"  CONTINUE signals (checkpoint/iter suffix or i-atom): {len(continue_tokens)} ({len(continue_tokens)/total_final*100:.1f}%)")
print(f"  NEUTRAL (bare/other): {len(neutral_tokens)} ({len(neutral_tokens)/total_final*100:.1f}%)")

# Top words in each category
stop_words = Counter(t.word for t in stop_tokens)
continue_words = Counter(t.word for t in continue_tokens)

print(f"\n  Top STOP words:")
for w, c in stop_words.most_common(15):
    print(f"    {w:15s}: {c:4d}  ({gloss_word(w)})")

print(f"\n  Top CONTINUE words:")
for w, c in continue_words.most_common(15):
    print(f"    {w:15s}: {c:4d}  ({gloss_word(w)})")

# ============================================================
# ANALYSIS 5: Penultimate-final pairs (decision context)
# ============================================================
print("\n=== PENULTIMATE-FINAL PAIRS ===")

pair_types = Counter()
for folio in folio_lines:
    for line in folio_lines[folio]:
        tokens = folio_lines[folio][line]
        n = len(tokens)
        if n < 3:
            continue
        penult = tokens[-2]
        final = tokens[-1]

        m_penult = morph.extract(penult.word)
        m_final = morph.extract(final.word)

        cat_penult = classify_suffix(m_penult.suffix)
        cat_final = classify_suffix(m_final.suffix)

        pair_types[(cat_penult, cat_final)] += 1

total_pairs = sum(pair_types.values())
print(f"\n  Penultimate suffix -> Final suffix (n={total_pairs}):")
for (p, f), c in pair_types.most_common(15):
    print(f"    {p:12s} -> {f:12s}: {c:4d} ({c/total_pairs*100:.1f}%)")

# ============================================================
# ANALYSIS 6: Whole-word patterns at line-final
# ============================================================
print("\n=== MOST COMMON LINE-FINAL WORDS ===")
final_word_counts = Counter(t.word for t in final_tokens)
for w, c in final_word_counts.most_common(25):
    m = morph.extract(w)
    cat = classify_suffix(m.suffix)
    print(f"    {w:15s}: {c:4d}  suffix={cat:12s}  gloss=({gloss_word(w)})")

# ============================================================
# COMPILE RESULTS
# ============================================================
# Suffix by position
suffix_by_pos = {}
for label, token_list in [('INITIAL', initial_tokens), ('MEDIAL', medial_tokens),
                           ('PENULTIMATE', penultimate_tokens), ('FINAL', final_tokens)]:
    cats = Counter()
    for t in token_list:
        m = morph.extract(t.word)
        cats[classify_suffix(m.suffix)] += 1
    total = sum(cats.values())
    suffix_by_pos[label] = {cat: round(cats[cat]/total*100, 1) for cat in ['TERMINAL', 'CHECKPOINT', 'ITERATIVE', 'BARE', 'OTHER']}

# Atom enrichment
atom_enrichment = {}
for atom in sorted(CHAR_GLOSS.keys()):
    f_rate = final_atoms[atom] / final_total if final_total > 0 else 0
    m_rate = medial_atoms[atom] / medial_total if medial_total > 0 else 0
    enrichment = round(f_rate / m_rate, 2) if m_rate > 0 else None
    if final_atoms[atom] >= 10:
        atom_enrichment[atom] = {
            'gloss': CHAR_GLOSS[atom],
            'final_pct': round(f_rate * 100, 1),
            'medial_pct': round(m_rate * 100, 1),
            'enrichment': enrichment,
        }

results = {
    'line_counts': {
        'final': len(final_tokens),
        'penultimate': len(penultimate_tokens),
        'medial': len(medial_tokens),
        'initial': len(initial_tokens),
    },
    'suffix_category_by_position': suffix_by_pos,
    'atom_enrichment_at_final': atom_enrichment,
    'decision_classification': {
        'stop_pct': round(len(stop_tokens)/total_final*100, 1),
        'continue_pct': round(len(continue_tokens)/total_final*100, 1),
        'neutral_pct': round(len(neutral_tokens)/total_final*100, 1),
    },
    'top_stop_words': [(w, c) for w, c in stop_words.most_common(15)],
    'top_continue_words': [(w, c) for w, c in continue_words.most_common(15)],
    'penultimate_final_suffix_pairs': [
        {'from': p, 'to': f, 'count': c, 'pct': round(c/total_pairs*100, 1)}
        for (p, f), c in pair_types.most_common(15)
    ],
    'top_final_words': [(w, c) for w, c in final_word_counts.most_common(20)],
}

output_path = OUTPUT_DIR / 'decision_point_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults written to: {output_path}")
