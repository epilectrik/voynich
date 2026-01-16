"""Check if Currier B grammar (transitions) is affected by transcriber issue."""
import pandas as pd
from collections import defaultdict, Counter
import numpy as np

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

def extract_primitive(word):
    """Extract primitive from word (simplified from grammar code)."""
    if pd.isna(word):
        return None
    word = str(word).lower()
    if len(word) == 1:
        return word
    # Last character if ends in vowel-like
    if word[-1] in 'aeiouy':
        return word[-1]
    # Check for common suffixes
    for suffix in ['dy', 'ey', 'ed', 'ol', 'or', 'al', 'ar', 'an', 'am', 'in', 'ir']:
        if word.endswith(suffix):
            return suffix
    return word[-1] if word else None

def build_transitions_sequential(df_subset):
    """Build transitions by reading sequentially (how original code worked)."""
    trans = defaultdict(Counter)
    current_folio = None
    prev_prim = None

    for _, row in df_subset.iterrows():
        if row['folio'] != current_folio:
            current_folio = row['folio']
            prev_prim = None
            continue

        prim = extract_primitive(row['word'])
        if prim and prev_prim:
            trans[prev_prim][prim] += 1
        prev_prim = prim

    return dict(trans)

def build_transitions_by_line(df_subset):
    """Build transitions properly grouped by line."""
    trans = defaultdict(Counter)

    for (folio, line_num), group in df_subset.groupby(['folio', 'line_number']):
        prims = [extract_primitive(w) for w in group['word']]
        prims = [p for p in prims if p]
        for i in range(1, len(prims)):
            trans[prims[i-1]][prims[i]] += 1

    return dict(trans)

# Currier B only
b_all = df[df['language'] == 'B']
b_h = df[(df['language'] == 'B') & (df['transcriber'] == 'H')]

print("CURRIER B GRAMMAR CHECK")
print("=" * 70)

# Build transition matrices
seq_all = build_transitions_sequential(b_all)
seq_h = build_transitions_sequential(b_h)
grp_all = build_transitions_by_line(b_all)
grp_h = build_transitions_by_line(b_h)

# Count total transitions
def count_total(trans):
    return sum(sum(v.values()) for v in trans.values())

print("\nTotal transitions:")
print(f"  Sequential ALL: {count_total(seq_all)}")
print(f"  Sequential H:   {count_total(seq_h)}")
print(f"  Grouped ALL:    {count_total(grp_all)}")
print(f"  Grouped H:      {count_total(grp_h)}")

# Check key forbidden transitions
print("\n" + "-" * 70)
print("Forbidden transitions (should be 0 or near-0):")

forbidden = [
    ('h', 'k'), ('shey', 'aiin'), ('chol', 'r'), ('dy', 'aiin')
]

for src, tgt in forbidden:
    seq_all_ct = seq_all.get(src, {}).get(tgt, 0)
    seq_h_ct = seq_h.get(src, {}).get(tgt, 0)
    grp_all_ct = grp_all.get(src, {}).get(tgt, 0)
    grp_h_ct = grp_h.get(src, {}).get(tgt, 0)
    print(f"  {src}->{tgt}: SeqAll={seq_all_ct}, SeqH={seq_h_ct}, GrpAll={grp_all_ct}, GrpH={grp_h_ct}")

# Check common transitions
print("\n" + "-" * 70)
print("Top 10 transitions comparison:")

# Get top from grouped H (most reliable)
all_trans_h = []
for src, targets in grp_h.items():
    for tgt, ct in targets.items():
        all_trans_h.append((src, tgt, ct))
all_trans_h.sort(key=lambda x: -x[2])

print(f"\n{'Transition':<15} {'Grp-H':>8} {'Grp-All':>8} {'Seq-H':>8} {'Seq-All':>8}")
print("-" * 55)
for src, tgt, ct in all_trans_h[:10]:
    grp_a = grp_all.get(src, {}).get(tgt, 0)
    seq_h_ct = seq_h.get(src, {}).get(tgt, 0)
    seq_a = seq_all.get(src, {}).get(tgt, 0)
    print(f"{src}->{tgt:<10} {ct:>8} {grp_a:>8} {seq_h_ct:>8} {seq_a:>8}")

# Check if the PATTERN is preserved
print("\n" + "=" * 70)
print("PATTERN PRESERVATION CHECK")
print("=" * 70)

# Compare top 20 transitions between methods
def get_top_n(trans, n=20):
    all_t = []
    for src, targets in trans.items():
        for tgt, ct in targets.items():
            all_t.append((f"{src}->{tgt}", ct))
    all_t.sort(key=lambda x: -x[1])
    return set(t[0] for t in all_t[:n])

top_grp_h = get_top_n(grp_h, 20)
top_seq_all = get_top_n(seq_all, 20)

overlap = len(top_grp_h & top_seq_all)
print(f"\nTop 20 overlap (Grp-H vs Seq-All): {overlap}/20 ({100*overlap/20:.0f}%)")

if overlap >= 15:
    print("VERDICT: Core grammar patterns LIKELY PRESERVED")
else:
    print("VERDICT: Grammar patterns MAY BE AFFECTED")
