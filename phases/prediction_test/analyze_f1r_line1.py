#!/usr/bin/env python
"""Analyze f1r line 1 tokens through the full morphological pipeline."""
import sys
sys.path.insert(0, r'C:\git\voynich')
from scripts.voynich import Morphology, RecordAnalyzer, MiddleAnalyzer, Transcript

morph = Morphology()
analyzer = RecordAnalyzer()
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('A')  # Currier A inventory

tokens = ['fachys', 'ykal', 'ar', 'ataiin', 'shol', 'shory', 'cthres', 'ykos', 'sholdy']

print("=" * 70)
print("f1r LINE 1: Morphological Analysis")
print("=" * 70)
print()

# Get record analysis for f1r line 1
try:
    record = analyzer.analyze_record('f1r', '1')
    print(f"Record analysis: {len(record.tokens)} tokens")
    print(f"Record type: folio=f1r, line=1")
    for t in record.tokens:
        print(f"  {t.word}: class={t.token_class}")
    print()
except Exception as e:
    print(f"Record analysis error: {e}")
    print()

print("TOKEN-BY-TOKEN DECOMPOSITION")
print("-" * 70)

for word in tokens:
    m = morph.extract(word)
    print(f"\n  {word}")
    print(f"    Articulator: {m.articulator or '-'}")
    print(f"    Prefix:      {m.prefix or '-'}")
    print(f"    MIDDLE:      {m.middle or '-'}")
    print(f"    Suffix:      {m.suffix or '-'}")

    # Check if MIDDLE is compound
    if m.middle:
        atoms = mid_analyzer.get_maximal_atoms(m.middle)
        if len(atoms) > 1:
            print(f"    Compound:    {' + '.join(atoms)}")

        # Check if core or compound
        if mid_analyzer.is_compound(m.middle):
            print(f"    Type:        COMPOUND")
        else:
            print(f"    Type:        BASE")

# Also check what Currier language f1r is
tx = Transcript()
f1r_tokens = [t for t in tx.all() if t.folio == 'f1r' and t.line == '1' and t.word.strip()]
print(f"\n\nf1r line 1 from transcript:")
for t in f1r_tokens:
    print(f"  '{t.word}' language={t.language} placement={t.placement} line_initial={t.line_initial} line_final={t.line_final}")

print(f"\n\nCurrier language for f1r: {f1r_tokens[0].language if f1r_tokens else 'unknown'}")
print("NOTE: f1r is Currier A. Tier 3 operational glosses (energy, monitor, etc.)")
print("are validated for Currier B only. For Currier A, we show structural decomposition")
print("and token class (RI/PP/INFRA), but operational interpretation is speculative.")
