"""Phase 336: Gloss Structural Validation.

Tests whether the core MIDDLE glosses are structurally constrained
(adversarial permutation on forbidden transitions) and whether glossed
MIDDLEs with similar semantic roles occupy similar distributional niches
(bigram context clustering).

Non-circularity: Forbidden pairs from Phase 18 (zero-count bigrams, 2025-12-31).
Glosses from Brunschwig alignment + kernel profiles (Phase 330).
Context vectors from B-corpus bigram statistics.
Gloss categories from keyword semantics.
Four independent derivation paths.

Key design note: Forbidden pair entities (e.g. "shey", "chol") are
PREFIX+MIDDLE compounds. This script resolves each entity to its
extracted MIDDLE via Morphology, then uses the MIDDLE dictionary gloss
for categorization. Permutation shuffles MIDDLE glosses.
"""

import json
import random
import sys
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
from sklearn.metrics import adjusted_rand_score

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))

from scripts.voynich import Transcript, Morphology

random.seed(42)
np.random.seed(42)


# ── Pre-registered gloss categories ──────────────────────────────

GLOSS_CATEGORIES = {
    'THERMAL': [
        'cool', 'heat', 'fire', 'warm', 'deep', 'extended', 'overnight',
        'settle', 'steady',
    ],
    'CONTAINMENT': [
        'seal', 'close', 'lock', 'frame', 'hold', 'bind', 'rigid', 'firm',
        'hard',
    ],
    'FLOW': [
        'intake', 'open', 'transfer', 'collect', 'gather', 'route',
        'discharge', 'vent', 'release', 'pour',
    ],
    'MONITORING': [
        'check', 'watch', 'verify', 'scan', 'observe', 'control', 'exact',
        'precise', 'measure', 'danger', 'hazard',
    ],
    'OPERATION': [
        'set', 'portion', 'work', 'operate', 'step', 'pound', 'strip',
        'adjust', 'regulate', 'pulse', 'sustain',
    ],
    'TRANSITION': [
        'end', 'break', 'halt', 'finish', 'finalize', 'yield', 'pause',
        'complete',
    ],
    'STAGING': [
        'start', 'early', 'mid', 'late', 'final', 'batch', 'cycle',
        'iterate', 'repeat', 'continue', 'loop',
    ],
    'STRUCTURAL': [
        'stand', 'flag', 'mark', 'path', 'link', 'diagram', 'bond',
        'dense', 'wide', 'long',
    ],
}


def categorize_gloss(gloss):
    """Assign a gloss string to a pre-registered category."""
    if not gloss:
        return 'UNGLOSSED'
    gloss_lower = gloss.lower()
    for cat, keywords in GLOSS_CATEGORIES.items():
        for kw in keywords:
            if kw in gloss_lower:
                return cat
    return 'OTHER'


# ── Load data ────────────────────────────────────────────────────

print("Loading data...")

morph = Morphology()

# 17 forbidden pairs (Phase 18, 2025-12-31)
with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
          encoding='utf-8') as f:
    inventory = json.load(f)

# MIDDLE dictionary (glosses)
with open(PROJECT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
    mid_dict = json.load(f)

# Build gloss lookup: all MIDDLEs with non-null glosses
glossed_middles = {}
for mid, info in mid_dict['middles'].items():
    if info.get('gloss'):
        glossed_middles[mid] = info['gloss']

print(f"  Loaded {len(inventory['transitions'])} forbidden pairs")
print(f"  Loaded {len(glossed_middles)} glossed MIDDLEs")


# ── Resolve forbidden pair entities to MIDDLEs ───────────────────

print("\nResolving forbidden pair entities to extracted MIDDLEs...")


def resolve_entity(entity):
    """Resolve a forbidden pair entity string to its extracted MIDDLE."""
    m = morph.extract(entity)
    if m and m.middle:
        return m.middle
    return entity  # fallback: use as-is


# Build raw forbidden pairs excluding 'c' (too rare, per Phase 334)
raw_pairs = [(t['source'], t['target']) for t in inventory['transitions']]
raw_pairs = [(s, t) for s, t in raw_pairs if s != 'c' and t != 'c']

# Resolve entities to MIDDLEs
resolved_pairs = []
for s_entity, t_entity in raw_pairs:
    s_mid = resolve_entity(s_entity)
    t_mid = resolve_entity(t_entity)
    s_gloss = glossed_middles.get(s_mid)
    t_gloss = glossed_middles.get(t_mid)
    resolved_pairs.append({
        'source_entity': s_entity,
        'target_entity': t_entity,
        'source_middle': s_mid,
        'target_middle': t_mid,
        'source_gloss': s_gloss,
        'target_gloss': t_gloss,
        'both_glossed': s_gloss is not None and t_gloss is not None,
    })

testable_pairs = [p for p in resolved_pairs if p['both_glossed']]
untestable = [p for p in resolved_pairs if not p['both_glossed']]

print(f"  Forbidden pairs (excl. c): {len(raw_pairs)}")
print(f"  Testable pairs (both MIDDLEs glossed): {len(testable_pairs)}")
print(f"  Untestable pairs: {len(untestable)}")

for p in testable_pairs:
    s_cat = categorize_gloss(p['source_gloss'])
    t_cat = categorize_gloss(p['target_gloss'])
    print(f"    {p['source_entity']}({p['source_middle']}={p['source_gloss']},{s_cat}) -> "
          f"{p['target_entity']}({p['target_middle']}={p['target_gloss']},{t_cat})")

if untestable:
    print("  Untestable (unglossed MIDDLE):")
    for p in untestable:
        print(f"    {p['source_entity']}({p['source_middle']}) -> "
              f"{p['target_entity']}({p['target_middle']})")

# Extract the MIDDLE-level pairs for testing
testable_mid_pairs = [(p['source_middle'], p['target_middle']) for p in testable_pairs]


# ── Build category mapping ───────────────────────────────────────

print("\nBuilding gloss categories...")
middle_to_cat = {mid: categorize_gloss(gloss) for mid, gloss in glossed_middles.items()}
cat_counts = Counter(middle_to_cat.values())
print(f"  Category distribution: {dict(sorted(cat_counts.items()))}")
n_other = cat_counts.get('OTHER', 0)
print(f"  OTHER rate: {n_other}/{len(glossed_middles)} = {n_other/len(glossed_middles)*100:.1f}%")


# ── Extract B bigrams ────────────────────────────────────────────

print("\nExtracting B bigrams...")
tx = Transcript()

# Group B tokens by (folio, line) to build sequences
line_tokens = defaultdict(list)
for tok in tx.currier_b():
    word = tok.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    if m and m.middle:
        line_tokens[(tok.folio, tok.line)].append(m.middle)

# Build bigram data structures
bigrams = []
pred_counts = defaultdict(Counter)   # middle -> {predecessor_middle: count}
succ_counts = defaultdict(Counter)   # middle -> {successor_middle: count}

for (folio, line), middles in line_tokens.items():
    for i in range(len(middles)):
        if i > 0:
            pred_counts[middles[i]][middles[i-1]] += 1
            bigrams.append((middles[i-1], middles[i]))
        if i < len(middles) - 1:
            succ_counts[middles[i]][middles[i+1]] += 1

# Top 49 most frequent MIDDLEs (context vocabulary)
middle_freq = Counter()
for middles in line_tokens.values():
    middle_freq.update(middles)

top49 = [m for m, _ in middle_freq.most_common(49)]
top49_idx = {m: i for i, m in enumerate(top49)}

print(f"  Total bigrams: {len(bigrams)}")
print(f"  MIDDLEs with predecessor data: {len(pred_counts)}")
print(f"  Top 49 MIDDLEs: {top49[:10]}...")


# ── Determine dominant PREFIX per MIDDLE ─────────────────────────

print("\nDetermining dominant PREFIXes...")
middle_prefix_counts = defaultdict(Counter)
for tok in tx.currier_b():
    word = tok.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    if m and m.middle:
        prefix = m.prefix if m.prefix else '_NONE'
        middle_prefix_counts[m.middle][prefix] += 1

dominant_prefix = {}
for mid in glossed_middles:
    if mid in middle_prefix_counts and middle_prefix_counts[mid]:
        dominant_prefix[mid] = middle_prefix_counts[mid].most_common(1)[0][0]
    else:
        dominant_prefix[mid] = '_UNKNOWN'

prefix_groups = defaultdict(list)
for mid, pfx in dominant_prefix.items():
    prefix_groups[pfx].append(mid)

multi_member_groups = {pfx: mids for pfx, mids in prefix_groups.items()
                       if len(mids) > 1}
print(f"  PREFIX groups: {len(prefix_groups)} total, "
      f"{len(multi_member_groups)} with >1 member")
print(f"  MIDDLEs in multi-member groups: "
      f"{sum(len(v) for v in multi_member_groups.values())}")


# ── Build context vectors ────────────────────────────────────────

print("\nBuilding context vectors...")


def build_context_vectors():
    """Build 98-dim context vectors for glossed MIDDLEs with >= 20 bigram contexts."""
    vectors = {}
    for mid in glossed_middles:
        total_contexts = sum(pred_counts[mid].values()) + sum(succ_counts[mid].values())
        if total_contexts < 20:
            continue

        vec = np.zeros(98)
        # Predecessor dimensions [0:49]
        for pred_mid, count in pred_counts[mid].items():
            if pred_mid in top49_idx:
                vec[top49_idx[pred_mid]] += count
        # Successor dimensions [49:98]
        for succ_mid, count in succ_counts[mid].items():
            if succ_mid in top49_idx:
                vec[49 + top49_idx[succ_mid]] += count

        # L1 normalize
        total = vec.sum()
        if total > 0:
            vec = vec / total
        vectors[mid] = vec

    return vectors


context_vectors = build_context_vectors()
print(f"  Built vectors for {len(context_vectors)} MIDDLEs (>= 20 bigram contexts)")


# ── T1: Full Adversarial Gloss Permutation ───────────────────────

def count_distinct_cat_pairs(mid_to_gloss, pairs):
    """Count distinct directed (source_cat, target_cat) pairs."""
    cat_pairs = set()
    for s, t in pairs:
        s_gloss = mid_to_gloss.get(s)
        t_gloss = mid_to_gloss.get(t)
        s_cat = categorize_gloss(s_gloss)
        t_cat = categorize_gloss(t_gloss)
        cat_pairs.add((s_cat, t_cat))
    return len(cat_pairs)


def run_t1():
    print("\n" + "="*60)
    print("T1: Full Adversarial Gloss Permutation")
    print("="*60)

    if len(testable_mid_pairs) < 5:
        print(f"  UNDERPOWERED: only {len(testable_mid_pairs)} testable pairs (need >= 5)")
        return {'pass': False, 'reason': 'UNDERPOWERED',
                'testable_pairs': len(testable_mid_pairs)}

    # Real concentration
    real_distinct = count_distinct_cat_pairs(glossed_middles, testable_mid_pairs)

    # Show the real category pairs
    real_cat_pairs = set()
    for s, t in testable_mid_pairs:
        s_cat = categorize_gloss(glossed_middles.get(s))
        t_cat = categorize_gloss(glossed_middles.get(t))
        real_cat_pairs.add((s_cat, t_cat))
    print(f"  Real distinct category pairs: {real_distinct}")
    for p in sorted(real_cat_pairs):
        print(f"    {p[0]} -> {p[1]}")

    # Permutation test: shuffle all glosses among all glossed MIDDLEs
    middles_list = list(glossed_middles.keys())
    glosses_list = list(glossed_middles.values())
    n_perm = 10000
    perm_distincts = []
    n_leq = 0

    for _ in range(n_perm):
        shuffled = glosses_list.copy()
        random.shuffle(shuffled)
        perm_mapping = dict(zip(middles_list, shuffled))
        perm_distinct = count_distinct_cat_pairs(perm_mapping, testable_mid_pairs)
        perm_distincts.append(perm_distinct)
        if perm_distinct <= real_distinct:
            n_leq += 1

    p_value = n_leq / n_perm
    mean_perm = np.mean(perm_distincts)
    std_perm = np.std(perm_distincts)

    passed = p_value < 0.01
    print(f"\n  Permutation mean: {mean_perm:.2f} +/- {std_perm:.2f}")
    print(f"  Real: {real_distinct}, p = {p_value:.4f}")
    print(f"  T1 {'PASS' if passed else 'FAIL'} (threshold: p < 0.01)")

    return {
        'pass': passed,
        'real_distinct': real_distinct,
        'perm_mean': float(mean_perm),
        'perm_std': float(std_perm),
        'p_value': p_value,
        'n_permutations': n_perm,
        'testable_pairs': len(testable_mid_pairs),
        'real_cat_pairs': [list(p) for p in sorted(real_cat_pairs)],
        'threshold': 'p < 0.01',
    }


# ── T2: PREFIX-Constrained Adversarial Permutation ───────────────

def run_t2():
    print("\n" + "="*60)
    print("T2: PREFIX-Constrained Adversarial Permutation")
    print("="*60)

    if len(testable_mid_pairs) < 5:
        print(f"  UNDERPOWERED: only {len(testable_mid_pairs)} testable pairs")
        return {'pass': False, 'reason': 'UNDERPOWERED'}

    # Check if enough multi-member groups exist
    shuffleable = sum(len(v) for v in multi_member_groups.values())
    total_glossed = len(glossed_middles)
    print(f"  Shuffleable MIDDLEs: {shuffleable}/{total_glossed} "
          f"({shuffleable/total_glossed*100:.0f}%)")

    if shuffleable < total_glossed * 0.3:
        print(f"  UNDERPOWERED: only {shuffleable/total_glossed*100:.0f}% "
              f"in multi-member PREFIX groups")
        return {
            'pass': False,
            'reason': 'UNDERPOWERED',
            'shuffleable': shuffleable,
            'total_glossed': total_glossed,
        }

    real_distinct = count_distinct_cat_pairs(glossed_middles, testable_mid_pairs)

    # Build indexed structure for within-group shuffling
    middles_list = list(glossed_middles.keys())
    glosses_list = list(glossed_middles.values())
    mid_to_idx = {m: i for i, m in enumerate(middles_list)}

    n_perm = 10000
    perm_distincts = []
    n_leq = 0

    for _ in range(n_perm):
        shuffled = glosses_list.copy()
        # Shuffle within each PREFIX group
        for pfx, group_mids in prefix_groups.items():
            if len(group_mids) <= 1:
                continue
            indices = [mid_to_idx[m] for m in group_mids if m in mid_to_idx]
            group_glosses = [shuffled[i] for i in indices]
            random.shuffle(group_glosses)
            for j, idx in enumerate(indices):
                shuffled[idx] = group_glosses[j]

        perm_mapping = dict(zip(middles_list, shuffled))
        perm_distinct = count_distinct_cat_pairs(perm_mapping, testable_mid_pairs)
        perm_distincts.append(perm_distinct)
        if perm_distinct <= real_distinct:
            n_leq += 1

    p_value = n_leq / n_perm
    mean_perm = np.mean(perm_distincts)
    std_perm = np.std(perm_distincts)

    passed = p_value < 0.05
    print(f"  Permutation mean: {mean_perm:.2f} +/- {std_perm:.2f}")
    print(f"  Real: {real_distinct}, p = {p_value:.4f}")
    print(f"  T2 {'PASS' if passed else 'FAIL'} (threshold: p < 0.05)")

    return {
        'pass': passed,
        'real_distinct': real_distinct,
        'perm_mean': float(mean_perm),
        'perm_std': float(std_perm),
        'p_value': p_value,
        'n_permutations': n_perm,
        'n_prefix_groups': len(prefix_groups),
        'n_multi_member_groups': len(multi_member_groups),
        'shuffleable_middles': shuffleable,
        'threshold': 'p < 0.05',
    }


# ── T3: Distributional Context Alignment ─────────────────────────

def run_t3():
    print("\n" + "="*60)
    print("T3: Distributional Context Alignment")
    print("="*60)

    # Filter to glossed MIDDLEs with context vectors
    eligible = {mid: vec for mid, vec in context_vectors.items()
                if mid in middle_to_cat and middle_to_cat[mid] != 'UNGLOSSED'}

    if len(eligible) < 20:
        print(f"  UNDERPOWERED: only {len(eligible)} eligible MIDDLEs")
        return {'pass': False, 'reason': 'UNDERPOWERED', 'eligible': len(eligible)}

    middles = list(eligible.keys())
    X = np.array([eligible[m] for m in middles])
    labels = [middle_to_cat[m] for m in middles]

    # k = number of non-empty categories
    unique_cats = sorted(set(labels))
    k = len(unique_cats)

    print(f"  Eligible MIDDLEs: {len(middles)}")
    print(f"  Categories (k): {k}")
    cat_size = Counter(labels)
    for cat in unique_cats:
        print(f"    {cat}: {cat_size[cat]}")

    # Hierarchical clustering (Ward linkage)
    Z = linkage(X, method='ward')
    cluster_labels = fcluster(Z, t=k, criterion='maxclust')

    # ARI between context clusters and gloss categories
    real_ari = adjusted_rand_score(labels, cluster_labels)
    print(f"\n  Real ARI: {real_ari:.4f}")

    # Permutation baseline: shuffle category labels
    n_perm = 10000
    n_geq = 0
    perm_aris = []

    for _ in range(n_perm):
        shuffled_labels = labels.copy()
        random.shuffle(shuffled_labels)
        perm_ari = adjusted_rand_score(shuffled_labels, cluster_labels)
        perm_aris.append(perm_ari)
        if perm_ari >= real_ari:
            n_geq += 1

    p_value = n_geq / n_perm
    mean_perm_ari = np.mean(perm_aris)
    std_perm_ari = np.std(perm_aris)

    passed = real_ari > 0 and p_value < 0.05
    print(f"  Permutation mean ARI: {mean_perm_ari:.4f} +/- {std_perm_ari:.4f}")
    print(f"  p = {p_value:.4f}")
    print(f"  T3 {'PASS' if passed else 'FAIL'} (threshold: ARI > 0, p < 0.05)")

    return {
        'pass': passed,
        'real_ari': float(real_ari),
        'perm_mean_ari': float(mean_perm_ari),
        'perm_std_ari': float(std_perm_ari),
        'p_value': p_value,
        'n_permutations': n_perm,
        'eligible_middles': len(middles),
        'k_clusters': k,
        'category_sizes': dict(cat_size),
        'threshold': 'ARI > 0, p < 0.05',
    }


# ── T4: Within-Category Context Cohesion ─────────────────────────

def run_t4():
    print("\n" + "="*60)
    print("T4: Within-Category Context Cohesion")
    print("="*60)

    # Filter to glossed MIDDLEs with context vectors and non-OTHER categories
    eligible = {mid: vec for mid, vec in context_vectors.items()
                if mid in middle_to_cat
                and middle_to_cat[mid] not in ('UNGLOSSED', 'OTHER')}

    if len(eligible) < 20:
        print(f"  UNDERPOWERED: only {len(eligible)} eligible MIDDLEs")
        return {'pass': False, 'reason': 'UNDERPOWERED', 'eligible': len(eligible)}

    # Group by category
    cat_groups = defaultdict(list)
    for mid, vec in eligible.items():
        cat_groups[middle_to_cat[mid]].append((mid, vec))

    # Filter to categories with >= 3 members
    testable_cats = {cat: members for cat, members in cat_groups.items()
                     if len(members) >= 3}

    print(f"  Eligible MIDDLEs: {len(eligible)}")
    print(f"  Testable categories (>= 3 members): {len(testable_cats)}")

    all_vecs = [vec for vec in eligible.values()]
    n_random = 1000
    results_per_cat = {}

    for cat in sorted(testable_cats):
        members = testable_cats[cat]
        vecs = np.array([v for _, v in members])
        n = len(members)

        if n < 2:
            continue

        # Real mean pairwise cosine similarity
        dists = pdist(vecs, metric='cosine')
        real_sim = 1.0 - np.mean(dists)

        # Random baseline
        n_better = 0
        for _ in range(n_random):
            rand_indices = np.random.choice(len(all_vecs), size=n, replace=False)
            rand_vecs = np.array([all_vecs[i] for i in rand_indices])
            rand_dists = pdist(rand_vecs, metric='cosine')
            rand_sim = 1.0 - np.mean(rand_dists)
            if rand_sim < real_sim:
                n_better += 1

        cohesion = n_better / n_random
        results_per_cat[cat] = {
            'n_members': n,
            'real_mean_cosine_sim': float(real_sim),
            'cohesion_score': float(cohesion),
        }
        print(f"  {cat}: {n} members, sim={real_sim:.3f}, cohesion={cohesion:.3f}")

    if not results_per_cat:
        print("  No testable categories")
        return {'pass': False, 'reason': 'NO_TESTABLE_CATEGORIES'}

    mean_cohesion = np.mean([r['cohesion_score'] for r in results_per_cat.values()])

    passed = mean_cohesion > 0.60
    print(f"\n  Mean cohesion: {mean_cohesion:.3f}")
    print(f"  T4 {'PASS' if passed else 'FAIL'} (threshold: > 0.60)")

    return {
        'pass': passed,
        'mean_cohesion': float(mean_cohesion),
        'per_category': results_per_cat,
        'n_testable_categories': len(testable_cats),
        'threshold': '> 0.60',
    }


# ── Verdict ──────────────────────────────────────────────────────

def synthesize_verdict(t1, t2, t3, t4):
    t1p = t1['pass']
    t2p = t2['pass']
    t3p = t3['pass']
    t4p = t4['pass']

    if t1p and t3p and (t2p or t4p):
        verdict = 'GLOSS_STRUCTURALLY_VALIDATED'
    elif t1p and (t3p or t4p):
        verdict = 'VALIDATED_PARTIAL'
    elif t3p and t4p and not t1p:
        verdict = 'DISTRIBUTIONAL_ONLY'
    elif t1p and not t3p and not t4p:
        verdict = 'ADVERSARIAL_ONLY'
    else:
        verdict = 'GLOSS_NOT_CONSTRAINED'

    return {
        'verdict': verdict,
        'tests_passed': sum([t1p, t2p, t3p, t4p]),
        'tests_total': 4,
        't1_pass': t1p,
        't2_pass': t2p,
        't3_pass': t3p,
        't4_pass': t4p,
    }


# ── Main ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Phase 336: GLOSS_STRUCTURAL_VALIDATION")
    print("="*60)

    # Run all four tests
    t1 = run_t1()
    t2 = run_t2()
    t3 = run_t3()
    t4 = run_t4()

    # Synthesize verdict
    synthesis = synthesize_verdict(t1, t2, t3, t4)

    print("\n" + "="*60)
    print(f"VERDICT: {synthesis['verdict']}")
    print(f"Tests passed: {synthesis['tests_passed']}/{synthesis['tests_total']}")
    print("="*60)

    # Write results
    output = {
        'phase': 336,
        'title': 'GLOSS_STRUCTURAL_VALIDATION',
        'tests': {
            't1_full_adversarial': t1,
            't2_prefix_constrained': t2,
            't3_distributional_alignment': t3,
            't4_within_category_cohesion': t4,
        },
        'synthesis': synthesis,
        'metadata': {
            'n_glossed_middles': len(glossed_middles),
            'n_forbidden_pairs_total': len(inventory['transitions']),
            'n_forbidden_pairs_excl_c': len(raw_pairs),
            'n_testable_pairs': len(testable_mid_pairs),
            'n_categories': len([c for c in cat_counts
                                 if c not in ('UNGLOSSED', 'OTHER')]),
            'category_distribution': dict(cat_counts),
            'n_context_vectors': len(context_vectors),
            'top49_middles': top49,
            'entity_resolution': [
                {'entity': p['source_entity'], 'middle': p['source_middle'],
                 'gloss': p['source_gloss']}
                for p in resolved_pairs
            ] + [
                {'entity': p['target_entity'], 'middle': p['target_middle'],
                 'gloss': p['target_gloss']}
                for p in resolved_pairs
            ],
        },
    }

    out_path = (PROJECT / 'phases' / 'GLOSS_STRUCTURAL_VALIDATION' /
                'results' / 'gloss_structural_validation.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nResults written to {out_path}")
    print(f"\nFINAL VERDICT: {synthesis['verdict']}")
