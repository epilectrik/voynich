"""Check kernel transition h->k: Is the 0 count real or artifact?"""
import pandas as pd
from collections import defaultdict, Counter

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

def get_kernel_class(word):
    """Classify token by kernel class (from counterfactual_grammar.py)."""
    if not word or pd.isna(word):
        return None
    word = str(word).lower()
    if word.endswith('k') or word in ['ok', 'yk', 'ak', 'ek']:
        return 'k'
    if word.endswith('h') or word in ['oh', 'yh', 'ah', 'eh']:
        return 'h'
    if word.endswith('ey') or word.endswith('eey') or word.endswith('edy') or word.endswith('dy'):
        return 'e'
    return None

# B-only
b_all = df[df['language'] == 'B'].copy()
b_h = df[(df['language'] == 'B') & (df['transcriber'] == 'H')].copy()

b_all['kernel'] = b_all['word'].apply(get_kernel_class)
b_h['kernel'] = b_h['word'].apply(get_kernel_class)

def count_transitions_sequential(df_subset):
    """Count transitions by reading rows sequentially (how the original code worked)."""
    trans = defaultdict(Counter)
    words = df_subset['kernel'].tolist()
    for i in range(1, len(words)):
        if words[i-1] and words[i]:
            trans[words[i-1]][words[i]] += 1
    return dict(trans)

def count_transitions_by_line(df_subset):
    """Count transitions properly grouped by line."""
    trans = defaultdict(Counter)
    for (folio, line_num), group in df_subset.groupby(['folio', 'line_number']):
        kernels = group['kernel'].tolist()
        for i in range(1, len(kernels)):
            if kernels[i-1] and kernels[i]:
                trans[kernels[i-1]][kernels[i]] += 1
    return dict(trans)

print("KERNEL TRANSITION ANALYSIS: h->k")
print("=" * 70)

# Sequential (how original code worked)
seq_all = count_transitions_sequential(b_all)
seq_h = count_transitions_sequential(b_h)

# Grouped (correct method)
grp_all = count_transitions_by_line(b_all)
grp_h = count_transitions_by_line(b_h)

print("\n1. SEQUENTIAL method (original code used this):")
print(f"   ALL transcribers:")
print(f"      h->k: {seq_all.get('h', {}).get('k', 0)}")
print(f"      k->h: {seq_all.get('k', {}).get('h', 0)}")
print(f"   H-only:")
print(f"      h->k: {seq_h.get('h', {}).get('k', 0)}")
print(f"      k->h: {seq_h.get('k', {}).get('h', 0)}")

print("\n2. GROUPED by line (correct method):")
print(f"   ALL transcribers:")
print(f"      h->k: {grp_all.get('h', {}).get('k', 0)}")
print(f"      k->h: {grp_all.get('k', {}).get('h', 0)}")
print(f"   H-only:")
print(f"      h->k: {grp_h.get('h', {}).get('k', 0)}")
print(f"      k->h: {grp_h.get('k', {}).get('h', 0)}")

print("\n" + "=" * 70)
print("C485 claims: h->k = 0 (perfectly forbidden)")
print("=" * 70)

# Check if h->k is actually 0 with proper method
hk_correct = grp_h.get('h', {}).get('k', 0)
if hk_correct == 0:
    print(f"\nVERDICT: h->k = {hk_correct} with H-only grouped method")
    print("C485 IS VALID (with correct methodology)")
else:
    print(f"\nVERDICT: h->k = {hk_correct} with H-only grouped method")
    print("C485 NEEDS REVIEW")
