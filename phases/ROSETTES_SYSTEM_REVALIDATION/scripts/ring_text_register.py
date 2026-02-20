"""Phase 404: Ring Text Register Characterization — 12-test battery.

Ring text (circumferential text on the 9 rosettes) shows a specific anomaly:
- 0/277 forbidden transition violations (C1130)
- Transition entropy 7.92 bits (vs B's ~0.41)

It obeys B's hard constraints but ignores soft ones. This phase characterizes
what KIND of text ring text is, using instruction class analysis, transition
matrix properties, compound rates, and per-rosette variation.

Phase 402 already established basic ring text metrics:
- 286 tokens, 52.45% grammar coverage, 37.06% kernel, 4.20% LINK
- 109 unique MIDDLEs, 52.29% PP, 1.83% RI

This phase goes deeper: instruction classes, transition matrix structure,
compound rates, PREFIX/SUFFIX profiles, per-rosette variation, positional
effects, and verdict assignment.
"""

import json
import math
import random
import sys
from pathlib import Path
from collections import defaultdict, Counter

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))

from scripts.voynich import (Transcript, Morphology, RosettesAnalyzer,
                              MiddleAnalyzer, load_middle_classes)

# ============================================================
# CONSTANTS
# ============================================================

KERNEL_CHARS = set('khe')

# ============================================================
# UTILITY
# ============================================================

def round_floats(obj, digits=4):
    if isinstance(obj, float):
        return round(obj, digits)
    elif isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    elif isinstance(obj, set):
        return sorted(obj)
    return obj


def jaccard(a, b):
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def cosine_sim(vec_a, vec_b):
    """Cosine similarity between two Counter-like dicts."""
    keys = set(vec_a) | set(vec_b)
    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in keys)
    mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def shannon_entropy(counts):
    """Shannon entropy in bits from a Counter or dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    ent = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            ent -= p * math.log2(p)
    return ent


def jensen_shannon(p_counts, q_counts):
    """Jensen-Shannon divergence between two count distributions."""
    all_keys = set(p_counts) | set(q_counts)
    p_total = sum(p_counts.values())
    q_total = sum(q_counts.values())
    if p_total == 0 or q_total == 0:
        return 1.0

    jsd = 0.0
    for k in all_keys:
        pk = p_counts.get(k, 0) / p_total
        qk = q_counts.get(k, 0) / q_total
        mk = (pk + qk) / 2
        if pk > 0:
            jsd += pk * math.log2(pk / mk) / 2
        if qk > 0:
            jsd += qk * math.log2(qk / mk) / 2
    return jsd


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load ring text tokens and all reference data."""
    print("Loading data...")
    morph = Morphology()
    tx = Transcript()
    ra = RosettesAnalyzer()

    # --- Ring text tokens ---
    ring_tokens = []
    ring_tokens_by_rosette = {}
    for rname in ra.get_rosettes():
        subs = ra.get_sub_regions(rname)
        if 'ring' in subs:
            rtoks = ra.get_entity_tokens(rname, sub_region='ring')
            ring_tokens.extend(rtoks)
            ring_tokens_by_rosette[rname] = rtoks
        else:
            ring_tokens_by_rosette[rname] = []

    ring_middles = set(t['middle'] for t in ring_tokens if t.get('middle'))
    print(f"  Ring text: {len(ring_tokens)} tokens, {len(ring_middles)} unique MIDDLEs, "
          f"{len(ring_tokens_by_rosette)} rosettes")

    # --- Non-ring rosettes tokens (for comparison) ---
    label_tokens = defaultdict(list)
    non_ring_tokens = []
    for ename in ra.get_entities():
        for sr in ra.get_sub_regions(ename):
            if sr != 'ring':
                toks = ra.get_entity_tokens(ename, sub_region=sr)
                non_ring_tokens.extend(toks)
                label_tokens[sr].extend(toks)

    non_ring_middles = set(t['middle'] for t in non_ring_tokens if t.get('middle'))

    # --- B corpus ---
    ros_folios = {'f85r1', 'f85r2', 'f85v2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}
    b_words = []
    b_prefix_counts = Counter()
    b_suffix_counts = Counter()
    b_all_middles = set()
    b_middle_seq = []  # for transition comparison
    b_folio_line_middles = defaultdict(list)

    for tok in tx.currier_b():
        if tok.folio in ros_folios:
            continue
        m = morph.extract(tok.word)
        b_words.append(tok.word)
        if m.middle:
            b_all_middles.add(m.middle)
            b_folio_line_middles[(tok.folio, tok.line)].append(m.middle)
        if m.prefix:
            b_prefix_counts[m.prefix] += 1
        if m.suffix:
            b_suffix_counts[m.suffix] += 1

    # B body class and role distributions
    ctm_path = PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm_data = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm_data['token_to_class'].items()}
    token_to_role = ctm_data.get('token_to_role', {})

    b_class_counts = Counter()
    b_role_counts = Counter()
    for w in b_words:
        cls = token_to_class.get(w)
        if cls is not None:
            b_class_counts[cls] += 1
        role = token_to_role.get(w)
        if role:
            b_role_counts[role] += 1

    # --- A and AZC corpus profiles ---
    a_prefix_counts = Counter()
    a_suffix_counts = Counter()
    for tok in tx.currier_a():
        m = morph.extract(tok.word)
        if m.prefix:
            a_prefix_counts[m.prefix] += 1
        if m.suffix:
            a_suffix_counts[m.suffix] += 1

    azc_prefix_counts = Counter()
    azc_suffix_counts = Counter()
    for tok in tx.azc():
        m = morph.extract(tok.word)
        if m.prefix:
            azc_prefix_counts[m.prefix] += 1
        if m.suffix:
            azc_suffix_counts[m.suffix] += 1

    # --- Bridge set ---
    bridge_path = PROJECT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(bridge_path, 'r', encoding='utf-8') as f:
        bd = json.load(f)
    bridge_set = set(bd['t5_structural_profile']['bridge_middles'])

    # --- RI/PP sets ---
    ri_set, pp_set = load_middle_classes()

    # --- MiddleAnalyzer ---
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # --- All corpus words (for hapax/uniqueness) ---
    all_corpus_words = set()
    for tok in tx.currier_b():
        all_corpus_words.add(tok.word)
    for tok in tx.currier_a():
        all_corpus_words.add(tok.word)
    for tok in tx.azc():
        all_corpus_words.add(tok.word)

    # --- Rosettes overall bridge fraction ---
    all_ros_middles = ra.all_middles()
    rosettes_bridge_frac = len(all_ros_middles & bridge_set) / len(all_ros_middles) if all_ros_middles else 0

    # --- B body bigram samples for transition matrix comparison ---
    # Build B MIDDLE bigrams from B lines (within-line only)
    b_bigrams = []
    for key in sorted(b_folio_line_middles):
        mids = b_folio_line_middles[key]
        for i in range(len(mids) - 1):
            b_bigrams.append((mids[i], mids[i + 1]))

    print(f"  B corpus: {len(b_words)} tokens, {len(b_all_middles)} unique MIDDLEs, "
          f"{len(b_bigrams)} bigrams")
    print(f"  Bridge set: {len(bridge_set)} MIDDLEs")
    print("  Data loaded.")

    return {
        'ring_tokens': ring_tokens,
        'ring_tokens_by_rosette': ring_tokens_by_rosette,
        'ring_middles': ring_middles,
        'non_ring_tokens': non_ring_tokens,
        'non_ring_middles': non_ring_middles,
        'label_tokens': dict(label_tokens),
        'b_words': b_words,
        'b_prefix_counts': b_prefix_counts,
        'b_suffix_counts': b_suffix_counts,
        'b_all_middles': b_all_middles,
        'b_class_counts': b_class_counts,
        'b_role_counts': b_role_counts,
        'b_bigrams': b_bigrams,
        'a_prefix_counts': a_prefix_counts,
        'a_suffix_counts': a_suffix_counts,
        'azc_prefix_counts': azc_prefix_counts,
        'azc_suffix_counts': azc_suffix_counts,
        'token_to_class': token_to_class,
        'token_to_role': token_to_role,
        'bridge_set': bridge_set,
        'ri_set': ri_set,
        'pp_set': pp_set,
        'mid_analyzer': mid_analyzer,
        'all_corpus_words': all_corpus_words,
        'rosettes_bridge_frac': rosettes_bridge_frac,
        'morph': morph,
    }


# ============================================================
# TIER A: VERDICT DISCRIMINATORS
# ============================================================

def a1_class_distribution(data):
    """A1: Map ring text to 49 B instruction classes."""
    print("\n=== A1: Instruction Class Distribution ===")

    ring_class_counts = Counter()
    unmapped = 0
    for tok in data['ring_tokens']:
        cls = data['token_to_class'].get(tok['word'])
        if cls is not None:
            ring_class_counts[cls] += 1
        else:
            unmapped += 1

    total_mapped = sum(ring_class_counts.values())
    n_classes_used = len(ring_class_counts)

    print(f"  Mapped: {total_mapped}/{len(data['ring_tokens'])} "
          f"({total_mapped/len(data['ring_tokens']):.1%})")
    print(f"  Classes used: {n_classes_used}/49")

    # JS divergence vs B body and vs uniform
    b_cc = data['b_class_counts']
    all_classes = set(ring_class_counts) | set(b_cc)
    uniform = {c: 1 for c in all_classes}

    js_vs_b = jensen_shannon(ring_class_counts, b_cc)
    js_vs_uniform = jensen_shannon(ring_class_counts, uniform)

    # Also compute JS of B body vs uniform (reference)
    js_b_vs_uniform = jensen_shannon(b_cc, uniform)

    print(f"  JS(ring, B body) = {js_vs_b:.4f}")
    print(f"  JS(ring, uniform) = {js_vs_uniform:.4f}")
    print(f"  JS(B body, uniform) = {js_b_vs_uniform:.4f} (reference)")

    # Class entropy
    ring_class_entropy = shannon_entropy(ring_class_counts)
    b_class_entropy = shannon_entropy(b_cc)
    max_entropy = math.log2(n_classes_used) if n_classes_used > 0 else 0
    print(f"  Ring class entropy: {ring_class_entropy:.2f} bits "
          f"(max {max_entropy:.2f} for {n_classes_used} classes)")
    print(f"  B class entropy: {b_class_entropy:.2f} bits")

    # Top 5 classes in ring text
    top5 = ring_class_counts.most_common(5)
    top5_frac = sum(c for _, c in top5) / total_mapped if total_mapped else 0
    print(f"  Top 5 classes capture {top5_frac:.1%} of mapped tokens:")
    for cls, cnt in top5:
        b_cnt = b_cc.get(cls, 0)
        b_total = sum(b_cc.values())
        b_pct = b_cnt / b_total if b_total else 0
        print(f"    Class {cls}: ring {cnt}/{total_mapped} ({cnt/total_mapped:.1%}), "
              f"B {b_cnt}/{b_total} ({b_pct:.1%})")

    # Over/under-represented classes (ring fraction / B fraction, at least 3 ring tokens)
    enriched = []
    depleted = []
    b_total = sum(b_cc.values())
    for cls in all_classes:
        r_frac = ring_class_counts.get(cls, 0) / total_mapped if total_mapped else 0
        b_frac = b_cc.get(cls, 0) / b_total if b_total else 0
        if b_frac > 0 and ring_class_counts.get(cls, 0) >= 3:
            ratio = r_frac / b_frac
            if ratio > 2.0:
                enriched.append((cls, ratio, ring_class_counts[cls]))
            elif ratio < 0.3 and b_cc.get(cls, 0) >= 50:
                depleted.append((cls, ratio, b_cc[cls]))

    enriched.sort(key=lambda x: -x[1])
    depleted.sort(key=lambda x: x[1])
    print(f"  Enriched classes (>2x B rate, >=3 ring tokens): {len(enriched)}")
    for cls, ratio, cnt in enriched[:5]:
        print(f"    Class {cls}: {ratio:.1f}x B rate ({cnt} ring tokens)")
    print(f"  Depleted classes (<0.3x B rate, >=50 B tokens): {len(depleted)}")
    for cls, ratio, bcnt in depleted[:5]:
        print(f"    Class {cls}: {ratio:.2f}x B rate ({bcnt} B tokens)")

    return {
        'ring_mapped': total_mapped,
        'ring_unmapped': unmapped,
        'ring_total': len(data['ring_tokens']),
        'n_classes_used': n_classes_used,
        'js_ring_vs_b': js_vs_b,
        'js_ring_vs_uniform': js_vs_uniform,
        'js_b_vs_uniform': js_b_vs_uniform,
        'ring_class_entropy': ring_class_entropy,
        'b_class_entropy': b_class_entropy,
        'top5_classes': [(cls, cnt, cnt / total_mapped) for cls, cnt in top5],
        'top5_fraction': top5_frac,
        'enriched_classes': [(cls, ratio) for cls, ratio, _ in enriched],
        'depleted_classes': [(cls, ratio) for cls, ratio, _ in depleted],
        'ring_class_counts': dict(ring_class_counts),
    }


def a2_role_distribution(data):
    """A2: Map ring text to 5 token role categories."""
    print("\n=== A2: Role Distribution ===")

    ring_role_counts = Counter()
    unmapped = 0
    for tok in data['ring_tokens']:
        role = data['token_to_role'].get(tok['word'])
        if role:
            ring_role_counts[role] += 1
        else:
            unmapped += 1

    total_mapped = sum(ring_role_counts.values())
    b_rc = data['b_role_counts']
    b_total = sum(b_rc.values())

    print(f"  Mapped: {total_mapped}/{len(data['ring_tokens'])}")
    all_roles = ['AUXILIARY', 'FLOW_OPERATOR', 'ENERGY_OPERATOR',
                 'FREQUENT_OPERATOR', 'CORE_CONTROL']
    for role in all_roles:
        r_cnt = ring_role_counts.get(role, 0)
        b_cnt = b_rc.get(role, 0)
        r_pct = r_cnt / total_mapped if total_mapped else 0
        b_pct = b_cnt / b_total if b_total else 0
        print(f"  {role:22s}: ring {r_cnt:4d} ({r_pct:.1%}), B {b_cnt:5d} ({b_pct:.1%})")

    js = jensen_shannon(ring_role_counts, b_rc)
    print(f"  JS(ring roles, B roles) = {js:.4f}")

    return {
        'ring_role_counts': dict(ring_role_counts),
        'b_role_counts': dict(b_rc),
        'ring_mapped': total_mapped,
        'ring_unmapped': unmapped,
        'js_ring_vs_b_roles': js,
    }


def a3_bridge_enrichment(data):
    """A3: Bridge MIDDLE enrichment specific to ring text."""
    print("\n=== A3: Bridge Enrichment (ring-specific) ===")

    ring_mids = data['ring_middles']
    bridge = data['bridge_set']
    ring_bridge = ring_mids & bridge
    ring_bridge_frac = len(ring_bridge) / len(ring_mids) if ring_mids else 0

    non_ring_mids = data['non_ring_middles']
    non_ring_bridge = non_ring_mids & bridge
    non_ring_bridge_frac = len(non_ring_bridge) / len(non_ring_mids) if non_ring_mids else 0

    print(f"  Ring bridge: {len(ring_bridge)}/{len(ring_mids)} = {ring_bridge_frac:.1%}")
    print(f"  Non-ring bridge: {len(non_ring_bridge)}/{len(non_ring_mids)} = {non_ring_bridge_frac:.1%}")
    print(f"  Rosettes overall: {data['rosettes_bridge_frac']:.1%}")

    # Bootstrap from B vocabulary
    b_mids = sorted(data['b_all_middles'])
    n = len(ring_mids)
    random.seed(42)
    bootstrap_fracs = []
    for _ in range(5000):
        sample = set(random.sample(b_mids, min(n, len(b_mids))))
        bootstrap_fracs.append(len(sample & bridge) / len(sample) if sample else 0)
    bootstrap_fracs.sort()
    p95 = bootstrap_fracs[int(0.95 * len(bootstrap_fracs))]
    p99 = bootstrap_fracs[int(0.99 * len(bootstrap_fracs))]
    percentile = sum(1 for f in bootstrap_fracs if f <= ring_bridge_frac) / len(bootstrap_fracs) * 100

    print(f"  B bootstrap p95: {p95:.4f}, p99: {p99:.4f}")
    print(f"  Ring percentile: {percentile:.1f}th")

    passed = ring_bridge_frac > p95
    elevated = ring_bridge_frac > non_ring_bridge_frac
    print(f"  PASS (> B p95): {passed}")
    print(f"  Ring > non-ring: {elevated}")

    return {
        'ring_bridge_fraction': ring_bridge_frac,
        'ring_bridge_count': len(ring_bridge),
        'ring_total_middles': len(ring_mids),
        'non_ring_bridge_fraction': non_ring_bridge_frac,
        'rosettes_overall': data['rosettes_bridge_frac'],
        'b_bootstrap_p95': p95,
        'b_bootstrap_p99': p99,
        'percentile': percentile,
        'pass': passed,
        'ring_elevated_vs_non_ring': elevated,
    }


def a4_classified_vs_un(data):
    """A4: Compare classified (in B grammar) vs unclassified ring tokens."""
    print("\n=== A4: Classified vs Unclassified Ring Tokens ===")

    classified = []
    unclassified = []
    for tok in data['ring_tokens']:
        if data['token_to_class'].get(tok['word']) is not None:
            classified.append(tok)
        else:
            unclassified.append(tok)

    print(f"  Classified: {len(classified)}, Unclassified: {len(unclassified)}")

    def profile(tokens, label):
        lengths = [len(t['word']) for t in tokens]
        mean_len = sum(lengths) / len(lengths) if lengths else 0
        mids = [t['middle'] for t in tokens if t.get('middle')]
        kernel_count = sum(1 for m in mids if any(c in KERNEL_CHARS for c in m))
        kernel_frac = kernel_count / len(mids) if mids else 0
        prefix_counts = Counter(t.get('prefix') for t in tokens if t.get('prefix'))
        compound_count = sum(1 for m in set(mids) if data['mid_analyzer'].is_compound(m))
        compound_frac = compound_count / len(set(mids)) if mids else 0
        bridge_mids = set(mids) & data['bridge_set']
        bridge_frac = len(bridge_mids) / len(set(mids)) if mids else 0
        print(f"  {label}: len={mean_len:.1f}, kernel={kernel_frac:.1%}, "
              f"compound={compound_frac:.1%}, bridge={bridge_frac:.1%}")
        return {
            'count': len(tokens),
            'mean_length': mean_len,
            'kernel_fraction': kernel_frac,
            'compound_fraction': compound_frac,
            'bridge_fraction': bridge_frac,
            'top_prefixes': prefix_counts.most_common(5),
        }

    cls_prof = profile(classified, "Classified")
    un_prof = profile(unclassified, "Unclassified")

    # Difference test: token lengths
    cls_lens = [len(t['word']) for t in classified]
    un_lens = [len(t['word']) for t in unclassified]
    cls_mean = sum(cls_lens) / len(cls_lens) if cls_lens else 0
    un_mean = sum(un_lens) / len(un_lens) if un_lens else 0
    print(f"  Length difference: classified {cls_mean:.2f} vs unclassified {un_mean:.2f}")

    return {
        'classified': cls_prof,
        'unclassified': un_prof,
        'length_difference': un_mean - cls_mean,
        'distinct_populations': abs(un_mean - cls_mean) > 0.5 or
            abs(cls_prof['kernel_fraction'] - un_prof['kernel_fraction']) > 0.1,
    }


# ============================================================
# TIER B: INTERNAL STRUCTURE
# ============================================================

def b1_transition_matrix(data):
    """B1: Transition matrix characterization beyond entropy."""
    print("\n=== B1: Transition Matrix Characterization ===")

    # Build ring text MIDDLE bigrams
    ring_bigrams = []
    ra_tokens = data['ring_tokens_by_rosette']
    for rname, toks in sorted(ra_tokens.items()):
        mids = [t['middle'] for t in toks if t.get('middle')]
        for i in range(len(mids) - 1):
            ring_bigrams.append((mids[i], mids[i + 1]))

    bigram_counts = Counter(ring_bigrams)
    total_bigrams = len(ring_bigrams)
    unique_bigrams = len(bigram_counts)

    # Source and target MIDDLE sets
    sources = set(b[0] for b in ring_bigrams)
    targets = set(b[1] for b in ring_bigrams)
    all_mids = sources | targets
    n_mids = len(all_mids)
    possible_bigrams = n_mids * n_mids
    sparsity = 1.0 - unique_bigrams / possible_bigrams if possible_bigrams > 0 else 0

    print(f"  Total bigrams: {total_bigrams}")
    print(f"  Unique bigrams: {unique_bigrams}")
    print(f"  Unique MIDDLEs in bigrams: {n_mids}")
    print(f"  Possible bigrams: {possible_bigrams}")
    print(f"  Sparsity: {sparsity:.4f}")

    # Overall bigram entropy (should match Phase 402: 7.92 bits)
    overall_entropy = shannon_entropy(bigram_counts)
    max_entropy = math.log2(unique_bigrams) if unique_bigrams > 0 else 0
    print(f"  Overall bigram entropy: {overall_entropy:.2f} bits (max: {max_entropy:.2f})")

    # Mean row entropy: average entropy of transition distributions per source MIDDLE
    source_counts = defaultdict(Counter)
    for (s, t), cnt in bigram_counts.items():
        source_counts[s][t] += cnt

    row_entropies = []
    for s in sources:
        row = source_counts[s]
        row_ent = shannon_entropy(row)
        row_total = sum(row.values())
        if row_total >= 2:  # Need at least 2 transitions for meaningful entropy
            row_entropies.append(row_ent)

    mean_row_entropy = sum(row_entropies) / len(row_entropies) if row_entropies else 0
    # Normalized by log2(n_targets)
    max_row_entropy = math.log2(len(targets)) if targets else 0
    normalized_row_entropy = mean_row_entropy / max_row_entropy if max_row_entropy > 0 else 0
    print(f"  Mean row entropy: {mean_row_entropy:.2f} bits "
          f"(of sources with >=2 transitions: {len(row_entropies)})")
    print(f"  Normalized row entropy: {normalized_row_entropy:.4f}")

    # Self-transition rate
    self_trans = sum(cnt for (s, t), cnt in bigram_counts.items() if s == t)
    self_rate = self_trans / total_bigrams if total_bigrams else 0
    print(f"  Self-transition rate: {self_rate:.2%}")

    # Enriched transitions: observed/expected > 3x and observed >= 2
    source_totals = Counter()
    target_totals = Counter()
    for (s, t), cnt in bigram_counts.items():
        source_totals[s] += cnt
        target_totals[t] += cnt

    enriched = []
    for (s, t), obs in bigram_counts.items():
        expected = (source_totals[s] * target_totals[t]) / total_bigrams if total_bigrams else 0
        if expected > 0 and obs >= 2:
            ratio = obs / expected
            if ratio > 3.0:
                enriched.append((s, t, obs, expected, ratio))
    enriched.sort(key=lambda x: -x[4])
    print(f"  Enriched transitions (>3x expected, >=2 obs): {len(enriched)}")
    for s, t, obs, exp, ratio in enriched[:10]:
        print(f"    ({s} -> {t}): obs={obs}, exp={exp:.2f}, ratio={ratio:.1f}x")

    # Random permutation baseline for mean row entropy
    random.seed(42)
    mid_sequence = []
    for rname, toks in sorted(ra_tokens.items()):
        mid_sequence.extend(t['middle'] for t in toks if t.get('middle'))

    perm_entropies = []
    for _ in range(1000):
        shuffled = mid_sequence[:]
        random.shuffle(shuffled)
        perm_bigrams = Counter()
        for i in range(len(shuffled) - 1):
            perm_bigrams[(shuffled[i], shuffled[i + 1])] += 1
        perm_source_counts = defaultdict(Counter)
        for (s, t), cnt in perm_bigrams.items():
            perm_source_counts[s][t] += cnt
        perm_row_ents = []
        for s, row in perm_source_counts.items():
            if sum(row.values()) >= 2:
                perm_row_ents.append(shannon_entropy(row))
        if perm_row_ents:
            perm_entropies.append(sum(perm_row_ents) / len(perm_row_ents))

    perm_entropies.sort()
    perm_mean = sum(perm_entropies) / len(perm_entropies) if perm_entropies else 0
    perm_percentile = sum(1 for e in perm_entropies
                          if e <= mean_row_entropy) / len(perm_entropies) * 100 if perm_entropies else 0
    print(f"  Random permutation baseline: mean={perm_mean:.2f} bits")
    print(f"  Observed row entropy percentile: {perm_percentile:.1f}th")

    # B body comparison: sample 286 tokens worth of B bigrams, compute entropy
    b_bigrams = data['b_bigrams']
    b_bigram_counts = Counter(b_bigrams)
    b_entropy = shannon_entropy(b_bigram_counts)
    b_source_counts = defaultdict(Counter)
    for (s, t), cnt in b_bigram_counts.items():
        b_source_counts[s][t] += cnt
    b_row_ents = []
    for s, row in b_source_counts.items():
        if sum(row.values()) >= 2:
            b_row_ents.append(shannon_entropy(row))
    b_mean_row_entropy = sum(b_row_ents) / len(b_row_ents) if b_row_ents else 0
    print(f"  B body bigram entropy: {b_entropy:.2f} bits, "
          f"mean row entropy: {b_mean_row_entropy:.2f} bits")

    return {
        'total_bigrams': total_bigrams,
        'unique_bigrams': unique_bigrams,
        'n_mids_in_bigrams': n_mids,
        'sparsity': sparsity,
        'overall_entropy': overall_entropy,
        'mean_row_entropy': mean_row_entropy,
        'normalized_row_entropy': normalized_row_entropy,
        'self_transition_rate': self_rate,
        'enriched_transitions': [(s, t, obs, ratio) for s, t, obs, _, ratio in enriched],
        'n_enriched': len(enriched),
        'permutation_baseline_mean': perm_mean,
        'permutation_percentile': perm_percentile,
        'b_body_bigram_entropy': b_entropy,
        'b_body_mean_row_entropy': b_mean_row_entropy,
    }


def b2_compound_rate(data):
    """B2: MIDDLE compound rate in ring text."""
    print("\n=== B2: MIDDLE Compound Rate ===")

    mid_analyzer = data['mid_analyzer']

    # Ring text MIDDLEs
    ring_mids = list(set(t['middle'] for t in data['ring_tokens'] if t.get('middle')))
    compound_count = sum(1 for m in ring_mids if mid_analyzer.is_compound(m))
    compound_frac = compound_count / len(ring_mids) if ring_mids else 0
    print(f"  Ring text: {compound_count}/{len(ring_mids)} compound = {compound_frac:.1%}")

    # Split by classified vs unclassified
    cls_mids = set()
    un_mids = set()
    for tok in data['ring_tokens']:
        mid = tok.get('middle')
        if not mid:
            continue
        if data['token_to_class'].get(tok['word']) is not None:
            cls_mids.add(mid)
        else:
            un_mids.add(mid)

    cls_compound = sum(1 for m in cls_mids if mid_analyzer.is_compound(m))
    un_compound = sum(1 for m in un_mids if mid_analyzer.is_compound(m))
    cls_frac = cls_compound / len(cls_mids) if cls_mids else 0
    un_frac = un_compound / len(un_mids) if un_mids else 0
    print(f"  Classified MIDDLEs: {cls_compound}/{len(cls_mids)} = {cls_frac:.1%}")
    print(f"  Unclassified MIDDLEs: {un_compound}/{len(un_mids)} = {un_frac:.1%}")

    # B body compound rate (from all B MIDDLEs)
    b_mids = list(data['b_all_middles'])
    b_compound = sum(1 for m in b_mids if mid_analyzer.is_compound(m))
    b_frac = b_compound / len(b_mids) if b_mids else 0
    print(f"  B body: {b_compound}/{len(b_mids)} = {b_frac:.1%}")

    # Non-ring rosettes
    non_ring_mids = list(data['non_ring_middles'])
    nr_compound = sum(1 for m in non_ring_mids if mid_analyzer.is_compound(m))
    nr_frac = nr_compound / len(non_ring_mids) if non_ring_mids else 0
    print(f"  Non-ring rosettes: {nr_compound}/{len(non_ring_mids)} = {nr_frac:.1%}")

    return {
        'ring_compound_fraction': compound_frac,
        'ring_compound_count': compound_count,
        'ring_total_middles': len(ring_mids),
        'classified_compound_fraction': cls_frac,
        'unclassified_compound_fraction': un_frac,
        'b_compound_fraction': b_frac,
        'non_ring_compound_fraction': nr_frac,
    }


def b3_prefix_profile(data):
    """B3: PREFIX distribution comparison."""
    print("\n=== B3: PREFIX Distribution ===")

    ring_pre = Counter(t.get('prefix') for t in data['ring_tokens'] if t.get('prefix'))
    total_ring = sum(ring_pre.values())

    # Reference distributions
    b_pre = data['b_prefix_counts']
    a_pre = data['a_prefix_counts']
    azc_pre = data['azc_prefix_counts']

    # Label-specific PREFIX distributions
    il_pre = Counter(t.get('prefix') for t in data['label_tokens'].get('inner_label', [])
                     if t.get('prefix'))
    ol_pre = Counter(t.get('prefix') for t in data['label_tokens'].get('outer_label', [])
                     if t.get('prefix'))

    # Cosine similarities
    cos_b = cosine_sim(ring_pre, b_pre)
    cos_a = cosine_sim(ring_pre, a_pre)
    cos_azc = cosine_sim(ring_pre, azc_pre)
    cos_il = cosine_sim(ring_pre, il_pre) if il_pre else 0
    cos_ol = cosine_sim(ring_pre, ol_pre) if ol_pre else 0

    print(f"  Ring vs B body: {cos_b:.4f}")
    print(f"  Ring vs A: {cos_a:.4f}")
    print(f"  Ring vs AZC: {cos_azc:.4f}")
    print(f"  Ring vs inner_label: {cos_il:.4f}")
    print(f"  Ring vs outer_label: {cos_ol:.4f}")

    # Top 5 ring prefixes
    print(f"  Top ring prefixes:")
    for pre, cnt in ring_pre.most_common(5):
        pct = cnt / total_ring if total_ring else 0
        print(f"    {pre}: {cnt} ({pct:.1%})")

    # o-prefix and qo-prefix fractions (compare to C525: labels have o=50%, qo~0%)
    o_frac = ring_pre.get('ot', 0) + ring_pre.get('ok', 0) + ring_pre.get('ol', 0)
    o_pct = o_frac / total_ring if total_ring else 0
    qo_cnt = ring_pre.get('qo', 0)
    qo_pct = qo_cnt / total_ring if total_ring else 0
    print(f"  o-family prefix fraction: {o_pct:.1%} (labels ref: ~50%, C525)")
    print(f"  qo-prefix fraction: {qo_pct:.1%} (labels ref: ~0%, C525)")

    return {
        'cosine_vs_b': cos_b,
        'cosine_vs_a': cos_a,
        'cosine_vs_azc': cos_azc,
        'cosine_vs_inner_label': cos_il,
        'cosine_vs_outer_label': cos_ol,
        'top5_prefixes': ring_pre.most_common(5),
        'o_family_fraction': o_pct,
        'qo_fraction': qo_pct,
        'ring_prefix_counts': dict(ring_pre),
    }


def b4_suffix_profile(data):
    """B4: SUFFIX distribution comparison."""
    print("\n=== B4: SUFFIX Distribution ===")

    ring_suf = Counter(t.get('suffix') for t in data['ring_tokens'] if t.get('suffix'))
    total_ring = sum(ring_suf.values())
    n_with_suffix = total_ring
    n_total = len(data['ring_tokens'])
    suffix_rate = n_with_suffix / n_total if n_total else 0

    b_suf = data['b_suffix_counts']
    azc_suf = data['azc_suffix_counts']
    a_suf = data['a_suffix_counts']

    cos_b = cosine_sim(ring_suf, b_suf)
    cos_azc = cosine_sim(ring_suf, azc_suf)
    cos_a = cosine_sim(ring_suf, a_suf)

    print(f"  Suffix rate: {suffix_rate:.1%} ({n_with_suffix}/{n_total})")
    print(f"  Ring vs B body: {cos_b:.4f}")
    print(f"  Ring vs AZC: {cos_azc:.4f}")
    print(f"  Ring vs A: {cos_a:.4f}")

    # Top 5 suffixes
    print(f"  Top ring suffixes:")
    for suf, cnt in ring_suf.most_common(5):
        pct = cnt / total_ring if total_ring else 0
        print(f"    {suf}: {cnt} ({pct:.1%})")

    # Kernel-heavy vs LINK-attr suffixes
    kernel_heavy = {'edy', 'ey', 'dy', 'eey', 'hy', 'ry'}
    link_attr = {'l', 'in', 'r', 'aiin', 'ain', 'iin', 'ar', 'oiin'}
    kh_count = sum(ring_suf.get(s, 0) for s in kernel_heavy)
    la_count = sum(ring_suf.get(s, 0) for s in link_attr)
    kh_frac = kh_count / total_ring if total_ring else 0
    la_frac = la_count / total_ring if total_ring else 0
    print(f"  Kernel-heavy suffixes: {kh_count} ({kh_frac:.1%})")
    print(f"  LINK-attr suffixes: {la_count} ({la_frac:.1%})")

    return {
        'suffix_rate': suffix_rate,
        'cosine_vs_b': cos_b,
        'cosine_vs_azc': cos_azc,
        'cosine_vs_a': cos_a,
        'top5_suffixes': ring_suf.most_common(5),
        'kernel_heavy_fraction': kh_frac,
        'link_attr_fraction': la_frac,
        'ring_suffix_counts': dict(ring_suf),
    }


# ============================================================
# TIER C: SECONDARY PROPERTIES
# ============================================================

def c1_per_rosette(data):
    """C1: Per-rosette variation in ring text properties."""
    print("\n=== C1: Per-Rosette Variation ===")

    rosette_stats = {}
    rosette_mid_sets = {}

    for rname, toks in sorted(data['ring_tokens_by_rosette'].items()):
        if not toks:
            continue
        mids = set(t['middle'] for t in toks if t.get('middle'))
        mid_list = [t['middle'] for t in toks if t.get('middle')]
        rosette_mid_sets[rname] = mids

        n_tokens = len(toks)
        kernel = sum(1 for m in mid_list if any(c in KERNEL_CHARS for c in m))
        kernel_frac = kernel / len(mid_list) if mid_list else 0
        mapped = sum(1 for t in toks if data['token_to_class'].get(t['word']) is not None)
        coverage = mapped / n_tokens if n_tokens else 0
        bridge_mids = mids & data['bridge_set']
        bridge_frac = len(bridge_mids) / len(mids) if mids else 0
        pp_mids = mids & data['pp_set']
        pp_frac = len(pp_mids) / len(mids) if mids else 0

        rosette_stats[rname] = {
            'n_tokens': n_tokens,
            'n_middles': len(mids),
            'kernel_fraction': kernel_frac,
            'grammar_coverage': coverage,
            'bridge_fraction': bridge_frac,
            'pp_fraction': pp_frac,
        }
        print(f"  {rname:8s}: {n_tokens:3d} tokens, {len(mids):3d} mids, "
              f"kernel={kernel_frac:.0%}, coverage={coverage:.0%}, "
              f"bridge={bridge_frac:.0%}, PP={pp_frac:.0%}")

    # Coefficient of variation for each metric
    def cv(values):
        if not values or len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        if mean == 0:
            return 0.0
        var = sum((v - mean) ** 2 for v in values) / len(values)
        return math.sqrt(var) / mean

    metrics = ['kernel_fraction', 'grammar_coverage', 'bridge_fraction', 'pp_fraction']
    cvs = {}
    for metric in metrics:
        values = [s[metric] for s in rosette_stats.values()]
        cvs[metric] = cv(values)
    print(f"\n  Coefficient of variation:")
    for metric, c in cvs.items():
        print(f"    {metric}: {c:.3f}")

    # Pairwise Jaccard of ring MIDDLE vocabulary per rosette
    rosette_names = sorted(rosette_mid_sets.keys())
    pairwise_jaccards = []
    for i in range(len(rosette_names)):
        for j in range(i + 1, len(rosette_names)):
            j_val = jaccard(rosette_mid_sets[rosette_names[i]],
                            rosette_mid_sets[rosette_names[j]])
            pairwise_jaccards.append(j_val)

    mean_jaccard = sum(pairwise_jaccards) / len(pairwise_jaccards) if pairwise_jaccards else 0
    print(f"\n  Mean pairwise ring text Jaccard: {mean_jaccard:.4f}")
    print(f"  (C1128 overall inter-rosette Jaccard: 0.322)")
    ring_more_similar = mean_jaccard > 0.322
    print(f"  Ring text MORE similar across rosettes than overall: {ring_more_similar}")

    return {
        'per_rosette': rosette_stats,
        'coefficient_of_variation': cvs,
        'mean_pairwise_jaccard': mean_jaccard,
        'c1128_reference': 0.322,
        'ring_more_similar_than_overall': ring_more_similar,
    }


def c2_length_hapax(data):
    """C2: Token length distribution and hapax/uniqueness."""
    print("\n=== C2: Token Length and Hapax ===")

    # Ring text lengths
    ring_lens = [len(t['word']) for t in data['ring_tokens']]
    ring_mean = sum(ring_lens) / len(ring_lens) if ring_lens else 0
    ring_median = sorted(ring_lens)[len(ring_lens) // 2] if ring_lens else 0

    # B body lengths
    b_lens = [len(w) for w in data['b_words']]
    b_mean = sum(b_lens) / len(b_lens) if b_lens else 0

    # AZC label lengths (inner + outer)
    label_toks = (data['label_tokens'].get('inner_label', []) +
                  data['label_tokens'].get('outer_label', []))
    label_lens = [len(t['word']) for t in label_toks]
    label_mean = sum(label_lens) / len(label_lens) if label_lens else 0

    print(f"  Ring text: mean={ring_mean:.2f}, median={ring_median}")
    print(f"  B body: mean={b_mean:.2f}")
    print(f"  Labels: mean={label_mean:.2f}")

    # Hapax rate (ring text token types appearing exactly once in ring text)
    ring_word_counts = Counter(t['word'] for t in data['ring_tokens'])
    n_types = len(ring_word_counts)
    hapax = sum(1 for c in ring_word_counts.values() if c == 1)
    hapax_rate = hapax / n_types if n_types else 0
    print(f"  Ring text types: {n_types}, hapax: {hapax} ({hapax_rate:.1%})")

    # Foldout-unique rate: ring text words absent from main corpus
    ring_words = set(t['word'] for t in data['ring_tokens'])
    corpus_words = data['all_corpus_words']
    foldout_unique = ring_words - corpus_words
    unique_rate = len(foldout_unique) / len(ring_words) if ring_words else 0
    print(f"  Foldout-unique types: {len(foldout_unique)}/{len(ring_words)} = {unique_rate:.1%}")
    if foldout_unique and len(foldout_unique) <= 20:
        print(f"    {sorted(foldout_unique)}")

    return {
        'ring_mean_length': ring_mean,
        'ring_median_length': ring_median,
        'b_mean_length': b_mean,
        'label_mean_length': label_mean,
        'ring_types': n_types,
        'hapax_count': hapax,
        'hapax_rate': hapax_rate,
        'foldout_unique_count': len(foldout_unique),
        'foldout_unique_rate': unique_rate,
        'foldout_unique_words': sorted(foldout_unique) if len(foldout_unique) <= 30 else [],
    }


def c3_positional(data):
    """C3: Positional effects within ring text."""
    print("\n=== C3: Positional Effects ===")

    first_half_kernel = 0
    first_half_total = 0
    second_half_kernel = 0
    second_half_total = 0
    first_half_prefix = Counter()
    second_half_prefix = Counter()

    for rname, toks in sorted(data['ring_tokens_by_rosette'].items()):
        if not toks:
            continue
        mid = len(toks) // 2
        for i, t in enumerate(toks):
            m = t.get('middle', '')
            p = t.get('prefix')
            has_kernel = any(c in KERNEL_CHARS for c in m) if m else False
            if i < mid:
                first_half_total += 1
                if has_kernel:
                    first_half_kernel += 1
                if p:
                    first_half_prefix[p] += 1
            else:
                second_half_total += 1
                if has_kernel:
                    second_half_kernel += 1
                if p:
                    second_half_prefix[p] += 1

    fh_kernel_frac = first_half_kernel / first_half_total if first_half_total else 0
    sh_kernel_frac = second_half_kernel / second_half_total if second_half_total else 0

    print(f"  First half: {first_half_total} tokens, kernel={fh_kernel_frac:.1%}")
    print(f"  Second half: {second_half_total} tokens, kernel={sh_kernel_frac:.1%}")
    print(f"  Kernel gradient: {abs(fh_kernel_frac - sh_kernel_frac):.2%}")

    # PREFIX cosine between halves
    cos_halves = cosine_sim(first_half_prefix, second_half_prefix)
    print(f"  PREFIX cosine (first vs second half): {cos_halves:.4f}")

    has_gradient = abs(fh_kernel_frac - sh_kernel_frac) > 0.1
    has_prefix_shift = cos_halves < 0.85
    print(f"  Gradient detected: {has_gradient}")
    print(f"  PREFIX shift detected: {has_prefix_shift}")

    return {
        'first_half_tokens': first_half_total,
        'second_half_tokens': second_half_total,
        'first_half_kernel': fh_kernel_frac,
        'second_half_kernel': sh_kernel_frac,
        'kernel_gradient': abs(fh_kernel_frac - sh_kernel_frac),
        'prefix_cosine_halves': cos_halves,
        'has_gradient': has_gradient,
        'has_prefix_shift': has_prefix_shift,
    }


def c4_non_ring_comparison(data):
    """C4: Same metrics for inner_label and outer_label as baseline."""
    print("\n=== C4: Non-Ring Entity Comparison ===")

    results = {}
    for entity_type in ['inner_label', 'outer_label']:
        toks = data['label_tokens'].get(entity_type, [])
        if not toks:
            results[entity_type] = {'n_tokens': 0}
            continue

        mids = set(t['middle'] for t in toks if t.get('middle'))
        mid_list = [t['middle'] for t in toks if t.get('middle')]

        n_tokens = len(toks)
        mapped = sum(1 for t in toks if data['token_to_class'].get(t['word']) is not None)
        coverage = mapped / n_tokens if n_tokens else 0
        kernel = sum(1 for m in mid_list if any(c in KERNEL_CHARS for c in m))
        kernel_frac = kernel / len(mid_list) if mid_list else 0
        bridge_mids = mids & data['bridge_set']
        bridge_frac = len(bridge_mids) / len(mids) if mids else 0

        # Class distribution
        cls_counts = Counter()
        for t in toks:
            c = data['token_to_class'].get(t['word'])
            if c is not None:
                cls_counts[c] += 1
        js_vs_b = jensen_shannon(cls_counts, data['b_class_counts']) if cls_counts else 1.0

        # Role distribution
        role_counts = Counter()
        for t in toks:
            r = data['token_to_role'].get(t['word'])
            if r:
                role_counts[r] += 1

        compound = sum(1 for m in mids if data['mid_analyzer'].is_compound(m))
        compound_frac = compound / len(mids) if mids else 0

        results[entity_type] = {
            'n_tokens': n_tokens,
            'n_middles': len(mids),
            'grammar_coverage': coverage,
            'kernel_fraction': kernel_frac,
            'bridge_fraction': bridge_frac,
            'compound_fraction': compound_frac,
            'js_class_vs_b': js_vs_b,
            'role_counts': dict(role_counts),
        }

        print(f"  {entity_type}: {n_tokens} tokens, coverage={coverage:.0%}, "
              f"kernel={kernel_frac:.0%}, bridge={bridge_frac:.0%}, "
              f"compound={compound_frac:.0%}, JS(class,B)={js_vs_b:.4f}")

    return results


# ============================================================
# VERDICT
# ============================================================

def verdict(results):
    """Apply decision tree to determine ring text register classification."""
    print("\n" + "=" * 70)
    print("VERDICT ASSIGNMENT")
    print("=" * 70)

    a1 = results['A1']
    a3 = results['A3']
    b1 = results['B1']

    # Key metrics
    js_uniform = a1['js_ring_vs_uniform']
    js_b = a1['js_ring_vs_b']
    top5_frac = a1['top5_fraction']
    bridge_elevated = a3['ring_elevated_vs_non_ring']
    bridge_pass = a3['pass']
    n_enriched = b1['n_enriched']
    perm_percentile = b1['permutation_percentile']

    print(f"\n  JS(ring, uniform) = {js_uniform:.4f} (threshold: 0.1)")
    print(f"  JS(ring, B body) = {js_b:.4f}")
    print(f"  Top-5 class concentration: {top5_frac:.1%}")
    print(f"  Bridge elevated vs non-ring: {bridge_elevated}")
    print(f"  Bridge > B p95: {bridge_pass}")
    print(f"  Enriched transitions: {n_enriched}")
    print(f"  Row entropy permutation percentile: {perm_percentile:.1f}th")

    # Decision tree
    if js_uniform < 0.1:
        v = 'CONSTRAINED_ENUMERATION'
        reason = (f"Class distribution near-uniform (JS={js_uniform:.4f} < 0.1). "
                  "Ring text randomly samples B-legal vocabulary under hard constraints.")
    elif bridge_elevated and bridge_pass:
        v = 'BRIDGE_VOCABULARY_INDEX'
        reason = (f"Structured class distribution (JS uniform={js_uniform:.4f}) "
                  f"with elevated bridge enrichment vs non-ring ({a3['ring_bridge_fraction']:.1%} "
                  f"vs {a3['non_ring_bridge_fraction']:.1%}). Ring text specifically samples "
                  "bridge vocabulary as cross-system index.")
    elif perm_percentile < 5:
        v = 'STRUCTURED_REGISTER'
        reason = (f"Row entropy below 5th percentile of random ({perm_percentile:.1f}th). "
                  "Transition matrix has hidden low-rank structure despite high overall entropy.")
    elif js_b < 0.05:
        v = 'HEADER_LIKE_INDEX'
        reason = (f"Class distribution matches B body closely (JS={js_b:.4f} < 0.05). "
                  "Ring text mirrors B class proportions.")
    else:
        v = 'VOCABULARY_SAMPLE'
        reason = (f"Structured class distribution (JS uniform={js_uniform:.4f}) "
                  f"but bridge not specifically elevated, transition matrix not low-rank "
                  f"(perm percentile={perm_percentile:.1f}). Ring text samples from "
                  "B-vocabulary space with class preferences but no hidden grammar.")

    print(f"\n  VERDICT: {v}")
    print(f"  REASON: {reason}")

    # Supporting evidence summary
    b2 = results['B2']
    c1 = results['C1']
    c2 = results['C2']
    c3 = results['C3']

    summary = {
        'verdict': v,
        'reason': reason,
        'key_metrics': {
            'js_ring_vs_uniform': js_uniform,
            'js_ring_vs_b': js_b,
            'top5_class_fraction': top5_frac,
            'bridge_fraction': a3['ring_bridge_fraction'],
            'bridge_elevated': bridge_elevated,
            'n_enriched_transitions': n_enriched,
            'perm_percentile': perm_percentile,
            'compound_fraction': b2['ring_compound_fraction'],
            'mean_pairwise_jaccard': c1['mean_pairwise_jaccard'],
            'hapax_rate': c2['hapax_rate'],
            'foldout_unique_rate': c2['foldout_unique_rate'],
            'has_positional_gradient': c3['has_gradient'],
        }
    }

    print(f"\n  Supporting:")
    print(f"    Compound rate: {b2['ring_compound_fraction']:.1%} "
          f"(B: {b2['b_compound_fraction']:.1%})")
    print(f"    Per-rosette Jaccard: {c1['mean_pairwise_jaccard']:.3f} "
          f"(C1128 ref: 0.322)")
    print(f"    Hapax rate: {c2['hapax_rate']:.1%}")
    print(f"    Foldout unique: {c2['foldout_unique_rate']:.1%}")
    print(f"    Positional gradient: {c3['has_gradient']}")

    return summary


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("Phase 404: Ring Text Register Characterization")
    print("=" * 70)

    data = load_data()

    results = {}
    results['A1'] = a1_class_distribution(data)
    results['A2'] = a2_role_distribution(data)
    results['A3'] = a3_bridge_enrichment(data)
    results['A4'] = a4_classified_vs_un(data)
    results['B1'] = b1_transition_matrix(data)
    results['B2'] = b2_compound_rate(data)
    results['B3'] = b3_prefix_profile(data)
    results['B4'] = b4_suffix_profile(data)
    results['C1'] = c1_per_rosette(data)
    results['C2'] = c2_length_hapax(data)
    results['C3'] = c3_positional(data)
    results['C4'] = c4_non_ring_comparison(data)

    v = verdict(results)

    output = {
        'phase': 404,
        'name': 'RING_TEXT_REGISTER_CHARACTERIZATION',
        'test_count': 12,
        'ring_token_count': len(data['ring_tokens']),
        'ring_middle_count': len(data['ring_middles']),
        'A1': results['A1'],
        'A2': results['A2'],
        'A3': results['A3'],
        'A4': results['A4'],
        'B1': results['B1'],
        'B2': results['B2'],
        'B3': results['B3'],
        'B4': results['B4'],
        'C1': results['C1'],
        'C2': results['C2'],
        'C3': results['C3'],
        'C4': results['C4'],
        'verdict': v,
    }

    out_path = PROJECT / 'phases' / 'ROSETTES_SYSTEM_REVALIDATION' / 'results' / 'ring_text_register.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(output), f, indent=2, ensure_ascii=False)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
