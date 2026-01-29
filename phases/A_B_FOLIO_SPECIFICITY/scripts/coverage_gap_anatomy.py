#!/usr/bin/env python3
"""
Coverage Gap Anatomy

What's in the gap between A-folio coverage and full B-folio vocabulary?
Are the uncovered tokens a specific class? Is the gap uniform across
B folios? Could any A folio fully serve any B folio at a high threshold?
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, RecordAnalyzer

print("=" * 70)
print("Coverage Gap Anatomy")
print("=" * 70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

morph_cache = {}
def get_morph(word):
    if word not in morph_cache:
        morph_cache[word] = morph.extract(word)
    return morph_cache[word]

# ============================================================
# Load role taxonomy
# ============================================================
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm_raw = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in ctm_raw['token_to_class'].items()}

CLASS_TO_ROLE = {
    10: 'CC', 11: 'CC', 12: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 35: 'EN',
    36: 'EN', 37: 'EN', 39: 'EN', 41: 'EN', 42: 'EN', 43: 'EN',
    44: 'EN', 45: 'EN', 46: 'EN', 47: 'EN', 48: 'EN', 49: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 13: 'FQ', 14: 'FQ', 23: 'FQ',
}
for c in list(range(1, 7)) + list(range(15, 17)) + list(range(18, 23)) + list(range(24, 30)):
    if c not in CLASS_TO_ROLE:
        CLASS_TO_ROLE[c] = 'AX'

def get_role(word):
    cls = token_to_class.get(word)
    if cls is None:
        return 'UNCLASSED'
    return CLASS_TO_ROLE.get(cls, 'UN')

# ============================================================
# Build A folio PP pools and legal sets
# ============================================================
print("\n--- Building data ---")
a_folios = sorted(analyzer.get_folios())
a_folio_pp = {}
for fol in a_folios:
    records = analyzer.analyze_folio(fol)
    mids, prefs, sufs = set(), set(), set()
    for rec in records:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                mids.add(t.middle)
                m = get_morph(t.word)
                if m.prefix:
                    prefs.add(m.prefix)
                if m.suffix:
                    sufs.add(m.suffix)
    a_folio_pp[fol] = (mids, prefs, sufs)

# B token inventory
b_tokens = {}
for token in tx.currier_b():
    w = token.word
    if w not in b_tokens:
        m = get_morph(w)
        if m.middle:
            b_tokens[w] = (m.prefix, m.middle, m.suffix)

b_middles_set = set(mid for _, mid, _ in b_tokens.values())
b_prefixes_set = set(pref for pref, _, _ in b_tokens.values() if pref)
b_suffixes_set = set(suf for _, _, suf in b_tokens.values() if suf)

# Per-A-folio legal sets
a_folio_legal = {}
for fol in a_folios:
    mids, prefs, sufs = a_folio_pp[fol]
    shared_mids = mids & b_middles_set
    shared_prefs = prefs & b_prefixes_set
    shared_sufs = sufs & b_suffixes_set
    legal = set()
    for tok, (pref, mid, suf) in b_tokens.items():
        if mid in shared_mids:
            if (pref is None or pref in shared_prefs):
                if (suf is None or suf in shared_sufs):
                    legal.add(tok)
    a_folio_legal[fol] = legal

# Union of all legal
union_legal = set()
for legal in a_folio_legal.values():
    union_legal |= legal

never_legal = set(b_tokens.keys()) - union_legal
print(f"B token types: {len(b_tokens)}")
print(f"Union legal: {len(union_legal)} ({len(union_legal)/len(b_tokens)*100:.1f}%)")
print(f"Never legal: {len(never_legal)} ({len(never_legal)/len(b_tokens)*100:.1f}%)")

# B folio vocabularies
b_folio_vocab = defaultdict(set)
b_folio_token_counts = defaultdict(lambda: defaultdict(int))
for token in tx.currier_b():
    w = token.word
    if w in b_tokens:
        b_folio_vocab[token.folio].add(w)
        b_folio_token_counts[token.folio][w] += 1

b_folios = sorted(b_folio_vocab.keys())

# ============================================================
# Q1: What roles are the never-legal tokens?
# ============================================================
print("\n--- Q1: Role Composition of Never-Legal Tokens ---")

role_counts_never = defaultdict(int)
role_counts_legal = defaultdict(int)
role_counts_all = defaultdict(int)

for tok in never_legal:
    role_counts_never[get_role(tok)] += 1
for tok in union_legal:
    role_counts_legal[get_role(tok)] += 1
for tok in b_tokens:
    role_counts_all[get_role(tok)] += 1

all_roles = sorted(set(list(role_counts_never.keys()) + list(role_counts_legal.keys())))
print(f"\n{'Role':<12} {'All B':>8} {'Legal':>8} {'Never':>8} {'% Never':>10}")
print("-" * 50)
for role in all_roles:
    total = role_counts_all[role]
    legal = role_counts_legal[role]
    never = role_counts_never[role]
    pct = never / total * 100 if total > 0 else 0
    print(f"{role:<12} {total:>8} {legal:>8} {never:>8} {pct:>9.1f}%")

# ============================================================
# Q2: WHY are never-legal tokens never legal?
# ============================================================
print("\n--- Q2: Why Are Tokens Never Legal? ---")

# Decompose: is it MIDDLE, PREFIX, or SUFFIX that blocks?
all_a_mids = set()
all_a_prefs = set()
all_a_sufs = set()
for mids, prefs, sufs in a_folio_pp.values():
    all_a_mids.update(mids)
    all_a_prefs.update(prefs)
    all_a_sufs.update(sufs)

mid_block = 0
pref_block = 0
suf_block = 0
multi_block = 0

for tok in never_legal:
    pref, mid, suf = b_tokens[tok]
    mid_fail = mid not in all_a_mids
    pref_fail = pref is not None and pref not in all_a_prefs
    suf_fail = suf is not None and suf not in all_a_sufs

    fails = sum([mid_fail, pref_fail, suf_fail])
    if fails > 1:
        multi_block += 1
    elif mid_fail:
        mid_block += 1
    elif pref_fail:
        pref_block += 1
    elif suf_fail:
        suf_block += 1
    else:
        # All components exist somewhere but never all together in one A folio
        pass

# Tokens where all components exist in A but never co-occur in one A folio
combinatorial_block = len(never_legal) - mid_block - pref_block - suf_block - multi_block

print(f"Never-legal tokens: {len(never_legal)}")
print(f"  Blocked by MIDDLE (not in any A pool): {mid_block} ({mid_block/len(never_legal)*100:.1f}%)")
print(f"  Blocked by PREFIX only: {pref_block} ({pref_block/len(never_legal)*100:.1f}%)")
print(f"  Blocked by SUFFIX only: {suf_block} ({suf_block/len(never_legal)*100:.1f}%)")
print(f"  Multiple axes blocked: {multi_block} ({multi_block/len(never_legal)*100:.1f}%)")
print(f"  Combinatorial (all parts exist, never together): {combinatorial_block} ({combinatorial_block/len(never_legal)*100:.1f}%)")

# How many unique MIDDLEs are B-exclusive?
b_exclusive_mids = b_middles_set - all_a_mids
print(f"\nB-exclusive MIDDLEs (not in any A pool): {len(b_exclusive_mids)}")
print(f"Total B MIDDLEs: {len(b_middles_set)}")
print(f"Shared MIDDLEs: {len(b_middles_set & all_a_mids)}")

# ============================================================
# Q3: Per-B-folio gap composition
# ============================================================
print("\n--- Q3: Per-B-Folio Gap Composition ---")

# For each B folio: what fraction is never-legal, and what's its role?
b_never_fracs = []
b_never_role_fracs = defaultdict(list)

for b_fol in b_folios:
    vocab = b_folio_vocab[b_fol]
    n_total = len(vocab)
    n_never = len(vocab & never_legal)
    frac = n_never / n_total if n_total > 0 else 0
    b_never_fracs.append(frac)

    # Role breakdown of never-legal in this B folio
    for role in all_roles:
        n_role_never = sum(1 for t in vocab & never_legal if get_role(t) == role)
        b_never_role_fracs[role].append(n_role_never / n_total if n_total > 0 else 0)

b_never_fracs = np.array(b_never_fracs)
print(f"Never-legal fraction per B folio:")
print(f"  Mean: {np.mean(b_never_fracs):.4f}")
print(f"  Median: {np.median(b_never_fracs):.4f}")
print(f"  Min: {np.min(b_never_fracs):.4f}")
print(f"  Max: {np.max(b_never_fracs):.4f}")
print(f"  Std: {np.std(b_never_fracs):.4f}")

print(f"\nNever-legal fraction by role (mean across B folios):")
for role in all_roles:
    vals = np.array(b_never_role_fracs[role])
    if np.mean(vals) > 0.001:
        print(f"  {role}: {np.mean(vals):.4f}")

# ============================================================
# Q4: Best coverage by ANY A folio for each B folio
# ============================================================
print("\n--- Q4: Best Single-A Coverage Per B Folio ---")

best_cov_per_b = []
for b_fol in b_folios:
    vocab = b_folio_vocab[b_fol]
    best = 0
    best_a = None
    for a_fol in a_folios:
        cov = len(a_folio_legal[a_fol] & vocab) / len(vocab) if vocab else 0
        if cov > best:
            best = cov
            best_a = a_fol
    best_cov_per_b.append((b_fol, best, best_a))

best_cov_per_b.sort(key=lambda x: x[1])
best_vals = [x[1] for x in best_cov_per_b]

print(f"Best single-A coverage per B folio:")
print(f"  Mean: {np.mean(best_vals):.4f}")
print(f"  Median: {np.median(best_vals):.4f}")
print(f"  Min: {best_cov_per_b[0][0]} = {best_cov_per_b[0][1]:.4f}")
print(f"  Max: {best_cov_per_b[-1][0]} = {best_cov_per_b[-1][1]:.4f}")

# Distribution
thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
for t in thresholds:
    n_above = sum(1 for v in best_vals if v >= t)
    print(f"  B folios with best-A >= {t:.0%}: {n_above}/{len(b_folios)} ({n_above/len(b_folios)*100:.1f}%)")

# ============================================================
# Q5: What if we exclude never-legal tokens?
# ============================================================
print("\n--- Q5: Coverage Excluding Never-Legal Tokens ---")

# If we remove B-exclusive vocabulary, how much can the best A folio cover?
best_cov_excl = []
for b_fol in b_folios:
    vocab = b_folio_vocab[b_fol] - never_legal  # only tokens that COULD be legal
    if not vocab:
        best_cov_excl.append((b_fol, 0, None))
        continue
    best = 0
    best_a = None
    for a_fol in a_folios:
        cov = len(a_folio_legal[a_fol] & vocab) / len(vocab)
        if cov > best:
            best = cov
            best_a = a_fol
    best_cov_excl.append((b_fol, best, best_a))

best_excl_vals = [x[1] for x in best_cov_excl]
print(f"Best single-A coverage (excluding never-legal):")
print(f"  Mean: {np.mean(best_excl_vals):.4f}")
print(f"  Median: {np.median(best_excl_vals):.4f}")
print(f"  Min: {np.min(best_excl_vals):.4f}")
print(f"  Max: {np.max(best_excl_vals):.4f}")

for t in thresholds:
    n_above = sum(1 for v in best_excl_vals if v >= t)
    print(f"  B folios with best-A >= {t:.0%}: {n_above}/{len(b_folios)} ({n_above/len(b_folios)*100:.1f}%)")

# ============================================================
# Q6: Token frequency weight
# ============================================================
print("\n--- Q6: Token-Weighted Coverage (by occurrence count) ---")

# Maybe rare types are never-legal but common tokens are?
# Weight by occurrence count instead of type count
best_weighted_cov = []
for b_fol in b_folios:
    vocab = b_folio_vocab[b_fol]
    counts = b_folio_token_counts[b_fol]
    total_occ = sum(counts[t] for t in vocab)
    best = 0
    for a_fol in a_folios:
        legal_occ = sum(counts[t] for t in a_folio_legal[a_fol] & vocab)
        cov = legal_occ / total_occ if total_occ > 0 else 0
        if cov > best:
            best = cov
    best_weighted_cov.append(best)

print(f"Best single-A token-weighted coverage per B folio:")
print(f"  Mean: {np.mean(best_weighted_cov):.4f}")
print(f"  Median: {np.median(best_weighted_cov):.4f}")
print(f"  Min: {np.min(best_weighted_cov):.4f}")
print(f"  Max: {np.max(best_weighted_cov):.4f}")

for t in thresholds:
    n_above = sum(1 for v in best_weighted_cov if v >= t)
    print(f"  B folios with best-A >= {t:.0%}: {n_above}/{len(b_folios)} ({n_above/len(b_folios)*100:.1f}%)")

# What fraction of B token OCCURRENCES are never-legal?
never_legal_occ_fracs = []
for b_fol in b_folios:
    counts = b_folio_token_counts[b_fol]
    total_occ = sum(counts.values())
    never_occ = sum(counts[t] for t in b_folio_vocab[b_fol] & never_legal)
    never_legal_occ_fracs.append(never_occ / total_occ if total_occ > 0 else 0)

print(f"\nNever-legal token OCCURRENCE fraction per B folio:")
print(f"  Mean: {np.mean(never_legal_occ_fracs):.4f}")
print(f"  Median: {np.median(never_legal_occ_fracs):.4f}")
print(f"  Min: {np.min(never_legal_occ_fracs):.4f}")
print(f"  Max: {np.max(never_legal_occ_fracs):.4f}")

# ============================================================
# Q7: What are the B-exclusive MIDDLEs?
# ============================================================
print("\n--- Q7: B-Exclusive MIDDLE Analysis ---")

# Tokens with B-exclusive MIDDLEs
b_excl_mid_tokens = [t for t in never_legal if b_tokens[t][1] in b_exclusive_mids]
print(f"Never-legal tokens with B-exclusive MIDDLE: {len(b_excl_mid_tokens)} "
      f"({len(b_excl_mid_tokens)/len(never_legal)*100:.1f}% of never-legal)")

# Role distribution of B-exclusive MIDDLE tokens
role_excl = defaultdict(int)
for tok in b_excl_mid_tokens:
    role_excl[get_role(tok)] += 1
print(f"\nRole distribution of B-exclusive-MIDDLE tokens:")
for role in sorted(role_excl, key=role_excl.get, reverse=True):
    print(f"  {role}: {role_excl[role]} ({role_excl[role]/len(b_excl_mid_tokens)*100:.1f}%)")

# How frequent are B-exclusive MIDDLEs?
b_excl_mid_freq = defaultdict(int)
for token in tx.currier_b():
    m = get_morph(token.word)
    if m.middle and m.middle in b_exclusive_mids:
        b_excl_mid_freq[m.middle] += 1

total_b_excl_occ = sum(b_excl_mid_freq.values())
total_b_occ = sum(1 for _ in tx.currier_b())
print(f"\nB-exclusive MIDDLE token occurrences: {total_b_excl_occ} / {total_b_occ} ({total_b_excl_occ/total_b_occ*100:.1f}%)")

# Top 10 most frequent B-exclusive MIDDLEs
top_excl = sorted(b_excl_mid_freq.items(), key=lambda x: -x[1])[:15]
print(f"\nTop 15 B-exclusive MIDDLEs by frequency:")
for mid, count in top_excl:
    n_b_fol = len(b_mid_to_folios[mid]) if mid in b_mid_to_folios else 0
    # Find example tokens
    examples = [t for t in b_excl_mid_tokens if b_tokens[t][1] == mid][:3]
    print(f"  {mid}: {count} occ, {n_b_fol} B folios, e.g. {examples}")

# Where does b_mid_to_folios come from? Need to build it
b_mid_to_folios = defaultdict(set)
for token in tx.currier_b():
    m = get_morph(token.word)
    if m.middle:
        b_mid_to_folios[m.middle].add(token.folio)

# Redo top 15 with proper data
print(f"\nTop 15 B-exclusive MIDDLEs (corrected):")
for mid, count in top_excl:
    n_b_fol = len(b_mid_to_folios[mid])
    examples = [t for t in b_excl_mid_tokens if b_tokens[t][1] == mid][:3]
    print(f"  {mid}: {count} occ, {n_b_fol} B folios, e.g. {examples}")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\nNever-legal tokens: {len(never_legal)} / {len(b_tokens)} ({len(never_legal)/len(b_tokens)*100:.1f}%)")
print(f"  Blocked by B-exclusive MIDDLE: {mid_block} ({mid_block/len(never_legal)*100:.1f}%)")
print(f"  Blocked by PREFIX/SUFFIX/combo: {pref_block + suf_block + multi_block} ({(pref_block + suf_block + multi_block)/len(never_legal)*100:.1f}%)")
print(f"  Combinatorial mismatch: {combinatorial_block} ({combinatorial_block/len(never_legal)*100:.1f}%)")

print(f"\nBest single-A coverage:")
print(f"  By type: mean {np.mean(best_vals):.1%}, max {np.max(best_vals):.1%}")
print(f"  By occurrence: mean {np.mean(best_weighted_cov):.1%}, max {np.max(best_weighted_cov):.1%}")
print(f"  Excluding never-legal: mean {np.mean(best_excl_vals):.1%}, max {np.max(best_excl_vals):.1%}")

print(f"\nNever-legal occurrence fraction: {np.mean(never_legal_occ_fracs):.1%} of B token occurrences")

print("\nDONE")
