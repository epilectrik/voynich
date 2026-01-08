"""Check kernel classification distribution."""
from collections import Counter

def get_kernel_class(word):
    if not word:
        return None
    if word.endswith('k') or word in ['ok', 'yk', 'ak', 'ek']:
        return 'k'
    if word.endswith('h') or word in ['oh', 'yh', 'ah', 'eh']:
        return 'h'
    if word.endswith('ey') or word.endswith('eey') or word.endswith('edy') or word.endswith('dy'):
        return 'e'
    return None

tokens = []
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    next(f)
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 7:
            word = parts[0].strip('"')
            lang = parts[6].strip('"')
            if lang == 'B' and word and word != 'NA':
                tokens.append(word)

print(f'Total B tokens: {len(tokens)}')
kernel_classes = [get_kernel_class(w) for w in tokens]
counts = Counter(kernel_classes)
print(f'Kernel distribution: {dict(counts)}')
print(f'k examples: {[w for w in tokens if get_kernel_class(w)=="k"][:10]}')
print(f'h examples: {[w for w in tokens if get_kernel_class(w)=="h"][:10]}')
print(f'e examples: {[w for w in tokens if get_kernel_class(w)=="e"][:10]}')

# Check what the top tokens look like
top_tokens = Counter(tokens).most_common(30)
print("\nTop 30 tokens:")
for t, c in top_tokens:
    kc = get_kernel_class(t)
    print(f"  {t}: {c} (kernel={kc})")
