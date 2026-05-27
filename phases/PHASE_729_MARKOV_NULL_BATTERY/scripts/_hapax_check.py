from scripts.voynich import Transcript
from collections import Counter

tx = Transcript()

def analyze(tokens, label):
    counts = Counter(t.word for t in tokens)
    total_tokens = sum(counts.values())
    total_types = len(counts)
    hapax = [w for w, c in counts.items() if c == 1]
    reusable = [w for w, c in counts.items() if c >= 2]
    hapax_tokens = sum(counts[w] for w in hapax)
    reusable_tokens = sum(counts[w] for w in reusable)
    once = sum(1 for c in counts.values() if c == 1)
    twice = sum(1 for c in counts.values() if c == 2)
    three_five = sum(1 for c in counts.values() if 3 <= c <= 5)
    six_twenty = sum(1 for c in counts.values() if 6 <= c <= 20)
    twentyone_hundred = sum(1 for c in counts.values() if 21 <= c <= 100)
    over_hundred = sum(1 for c in counts.values() if c > 100)
    print(f'=== {label} ===')
    print(f'Total tokens: {total_tokens:,}')
    print(f'Unique types: {total_types:,}')
    print(f'Type-token ratio: {total_types/total_tokens:.4f}')
    print(f'Hapax types (count=1): {len(hapax):,} ({100*len(hapax)/total_types:.1f}%)')
    print(f'Reusable types (count>=2): {len(reusable):,} ({100*len(reusable)/total_types:.1f}%)')
    print(f'Hapax tokens in running text: {hapax_tokens:,} ({100*hapax_tokens/total_tokens:.1f}%)')
    print(f'Reusable tokens in running text: {reusable_tokens:,} ({100*reusable_tokens/total_tokens:.1f}%)')
    print(f'Type frequency tiers:')
    print(f'  count=1   (hapax):       {once:>5} types')
    print(f'  count=2   (dis-legomena):{twice:>5} types')
    print(f'  count=3-5:               {three_five:>5} types')
    print(f'  count=6-20:              {six_twenty:>5} types')
    print(f'  count=21-100:            {twentyone_hundred:>5} types')
    print(f'  count>100:               {over_hundred:>5} types')
    print(f'Top 10 most-reused:')
    for w, c in counts.most_common(10):
        print(f'  {w:<14} {c:>5}')
    print()

analyze(list(tx.all()), 'All H-track (A+B+AZC)')
analyze(list(tx.currier_a()), 'Currier A')
analyze(list(tx.currier_b()), 'Currier B')
analyze(list(tx.azc()), 'AZC')
