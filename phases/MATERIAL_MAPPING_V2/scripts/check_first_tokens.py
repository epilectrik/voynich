"""Check first tokens of paragraphs without initial RI."""
import json
import sys
sys.path.insert(0, 'scripts')
from voynich import RecordAnalyzer, load_middle_classes

ri_middles, pp_middles = load_middle_classes()
analyzer = RecordAnalyzer()

para_tokens = json.load(open('phases/PARAGRAPH_INTERNAL_PROFILING/results/a_paragraph_tokens.json'))

print("Paragraphs where first token is NOT RI:")
print("="*70)

no_init_count = 0
for para_id, tokens in list(para_tokens.items()):
    if not tokens:
        continue
    first_word = tokens[0]['word']
    if not first_word:
        continue
    analysis = analyzer.analyze_token(first_word)
    if analysis.token_class != 'RI':
        no_init_count += 1
        if no_init_count <= 15:  # Show first 15
            mid = analysis.middle
            print(f"\n{para_id}: first={first_word}")
            print(f"  MIDDLE={mid}")
            print(f"  Class={analysis.token_class}")
            print(f"  In ri_middles: {mid in ri_middles}")
            print(f"  In pp_middles: {mid in pp_middles}")

print(f"\n\nTotal without initial RI: {no_init_count}/{len(para_tokens)}")
