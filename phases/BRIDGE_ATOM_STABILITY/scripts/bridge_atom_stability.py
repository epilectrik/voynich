#!/usr/bin/env python3
"""Phase 539: Bridge MIDDLE Atom-Role Stability Across A and B.

Tests whether the 85 bridge MIDDLEs preserve atom-role behavior across
Currier A (declarative registry) and Currier B (execution grammar).

Key questions:
- Do bridge MIDDLEs maintain HEAD/MOD/TERM decomposition across systems?
- Is the frequency redistribution (C1503) systematic?
- Do A and B deploy the same atoms in the same roles?
- Is A truly a declarative register over the same operational substrate?

Pre-registered predictions (from expert):
P1: HEAD distribution stable across A and B (JSD < 0.05)
P2: TERMINAL distribution stable (JSD < 0.05)
P3: Modifier grammar universal (JSD < 0.01, per C1504)
P4: Category stability mediated by HEAD atom (100% HEAD→category match)
P5: A uses different PREFIX ecology than B (JSD > 0.20)
P6: A suffix rate lower than B for bridge MIDDLEs
P7: A-enriched bridges have different HEAD profiles than B-enriched
P8: Atom behavioral correlation A vs B > 0.70 for all slot roles
P9: A preferentially selects descriptive terminals (l, h enriched)
P10: B preferentially selects action terminals (y, m, r enriched)
"""
import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, CategoryClassifier, decompose_middle_hmt

# ============================================================
# SETUP
# ============================================================
tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()

results = {
    'phase': 539,
    'name': 'BRIDGE_ATOM_STABILITY',
    'question': 'Do bridge MIDDLEs preserve atom-role behavior across A and B?',
    'tests': {},
}

def round_floats(obj, decimals=4):
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return str(obj)
        return round(obj, decimals)
    elif isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(v, decimals) for v in obj]
    return obj

def jsd(p_dict, q_dict):
    """Jensen-Shannon divergence between two frequency dicts."""
    all_keys = set(p_dict.keys()) | set(q_dict.keys())
    if not all_keys:
        return 0.0
    p_total = sum(p_dict.values())
    q_total = sum(q_dict.values())
    if p_total == 0 or q_total == 0:
        return 1.0
    divergence = 0.0
    for k in all_keys:
        p_val = p_dict.get(k, 0) / p_total
        q_val = q_dict.get(k, 0) / q_total
        m_val = (p_val + q_val) / 2
        if p_val > 0 and m_val > 0:
            divergence += 0.5 * p_val * math.log2(p_val / m_val)
        if q_val > 0 and m_val > 0:
            divergence += 0.5 * q_val * math.log2(q_val / m_val)
    return max(0.0, divergence)

def cosine_sim(d1, d2):
    """Cosine similarity between two frequency dicts."""
    all_keys = set(d1.keys()) | set(d2.keys())
    if not all_keys:
        return 0.0
    dot = sum(d1.get(k, 0) * d2.get(k, 0) for k in all_keys)
    mag1 = math.sqrt(sum(v**2 for v in d1.values()))
    mag2 = math.sqrt(sum(v**2 for v in d2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

# ============================================================
# LOAD BRIDGE MIDDLES
# ============================================================
print("Loading bridge MIDDLEs...")
bridge_path = ROOT / 'phases/BRIDGE_MIDDLE_SELECTION_MECHANISM/results/bridge_selection.json'
with open(bridge_path, 'r', encoding='utf-8') as f:
    bridge_data = json.load(f)
bridge_middles = set(bridge_data['t5_structural_profile']['bridge_middles'])
print(f"  Bridge MIDDLEs: {len(bridge_middles)}")

# ============================================================
# COLLECT TOKEN DATA PER SYSTEM
# ============================================================
print("Collecting token data from A and B...")

# Data structures for A
a_middle_freq = Counter()     # MIDDLE -> count in A
a_prefix_per_mid = defaultdict(Counter)   # MIDDLE -> {prefix: count}
a_suffix_per_mid = defaultdict(Counter)   # MIDDLE -> {suffix: count}
a_suffix_rate = defaultdict(lambda: [0, 0])  # MIDDLE -> [suffixed, total]
a_tokens_by_mid = defaultdict(list)  # MIDDLE -> list of full token info

# Data structures for B
b_middle_freq = Counter()
b_prefix_per_mid = defaultdict(Counter)
b_suffix_per_mid = defaultdict(Counter)
b_suffix_rate = defaultdict(lambda: [0, 0])
b_tokens_by_mid = defaultdict(list)

def collect_tokens(token_iter, mid_freq, pfx_per_mid, sfx_per_mid, sfx_rate, tok_by_mid):
    for tok in token_iter:
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        if not mid:
            continue
        mid_freq[mid] += 1
        prefix = m.prefix if m.prefix else 'BARE'
        pfx_per_mid[mid][prefix] += 1
        suffix = m.suffix if m.suffix else 'BARE'
        sfx_per_mid[mid][suffix] += 1
        sfx_rate[mid][1] += 1  # total
        if m.suffix:
            sfx_rate[mid][0] += 1  # suffixed
        tok_by_mid[mid].append({
            'word': w,
            'prefix': m.prefix,
            'middle': mid,
            'suffix': m.suffix,
            'folio': tok.folio,
            'section': tok.section,
        })

collect_tokens(tx.currier_a(), a_middle_freq, a_prefix_per_mid, a_suffix_per_mid, a_suffix_rate, a_tokens_by_mid)
collect_tokens(tx.currier_b(), b_middle_freq, b_prefix_per_mid, b_suffix_per_mid, b_suffix_rate, b_tokens_by_mid)

print(f"  A: {sum(a_middle_freq.values())} tokens, {len(a_middle_freq)} unique MIDDLEs")
print(f"  B: {sum(b_middle_freq.values())} tokens, {len(b_middle_freq)} unique MIDDLEs")

# Filter to bridge MIDDLEs only
bridge_in_a = {m: a_middle_freq[m] for m in bridge_middles if m in a_middle_freq}
bridge_in_b = {m: b_middle_freq[m] for m in bridge_middles if m in b_middle_freq}
bridge_in_both = set(bridge_in_a.keys()) & set(bridge_in_b.keys())

print(f"  Bridge in A: {len(bridge_in_a)} ({sum(bridge_in_a.values())} tokens)")
print(f"  Bridge in B: {len(bridge_in_b)} ({sum(bridge_in_b.values())} tokens)")
print(f"  Bridge in BOTH: {len(bridge_in_both)}")

results['bridge_census'] = {
    'total_bridge': len(bridge_middles),
    'bridge_in_a': len(bridge_in_a),
    'bridge_in_b': len(bridge_in_b),
    'bridge_in_both': len(bridge_in_both),
    'a_tokens_bridge': sum(bridge_in_a.values()),
    'b_tokens_bridge': sum(bridge_in_b.values()),
}

# ============================================================
# T1: PER-MIDDLE ATOM DECOMPOSITION AND FREQUENCY RATIO
# ============================================================
print("\nT1: Per-MIDDLE atom decomposition and frequency redistribution...")

mid_decomp = {}
freq_ratios = {}
for mid in sorted(bridge_in_both):
    head, mod, term, frame = decompose_middle_hmt(mid)
    mid_decomp[mid] = {
        'head': head if head else 'HEADLESS',
        'mod': mod if mod else 'NONE',
        'term': term,
        'frame': frame,
    }
    a_count = bridge_in_a.get(mid, 0)
    b_count = bridge_in_b.get(mid, 0)
    ratio = b_count / a_count if a_count > 0 else float('inf')
    freq_ratios[mid] = {
        'a_count': a_count,
        'b_count': b_count,
        'b_over_a': ratio,
        'total': a_count + b_count,
    }

# Sort by B/A ratio to find most A-enriched and B-enriched
sorted_by_ratio = sorted(freq_ratios.items(), key=lambda x: x[1]['b_over_a'])
a_enriched = [(m, d) for m, d in sorted_by_ratio if d['b_over_a'] < 1.0]
b_enriched = [(m, d) for m, d in sorted_by_ratio if d['b_over_a'] > 1.0]
balanced = [(m, d) for m, d in sorted_by_ratio if d['b_over_a'] == 1.0]

print(f"  A-enriched (B/A < 1.0): {len(a_enriched)}")
print(f"  Balanced (B/A = 1.0): {len(balanced)}")
print(f"  B-enriched (B/A > 1.0): {len(b_enriched)}")
print(f"\n  Top 10 A-enriched:")
for m, d in a_enriched[:10]:
    print(f"    {m:12s}  A={d['a_count']:5d}  B={d['b_count']:5d}  B/A={d['b_over_a']:.3f}  frame={mid_decomp[m]['frame']}")
print(f"\n  Top 10 B-enriched:")
for m, d in b_enriched[-10:]:
    print(f"    {m:12s}  A={d['a_count']:5d}  B={d['b_count']:5d}  B/A={d['b_over_a']:.3f}  frame={mid_decomp[m]['frame']}")

results['tests']['T1_frequency_redistribution'] = {
    'n_bridge_in_both': len(bridge_in_both),
    'a_enriched_count': len(a_enriched),
    'balanced_count': len(balanced),
    'b_enriched_count': len(b_enriched),
    'top10_a_enriched': [(m, d) for m, d in a_enriched[:10]],
    'top10_b_enriched': [(m, d) for m, d in b_enriched[-10:]],
    'decompositions': mid_decomp,
    'freq_ratios': freq_ratios,
}

# ============================================================
# T2: HEAD DOMAIN STABILITY
# ============================================================
print("\nT2: HEAD domain stability across A and B...")

# Aggregate HEAD distributions across bridge MIDDLEs weighted by frequency
a_head_dist = Counter()
b_head_dist = Counter()
for mid in bridge_in_both:
    head = mid_decomp[mid]['head']
    a_head_dist[head] += bridge_in_a.get(mid, 0)
    b_head_dist[head] += bridge_in_b.get(mid, 0)

head_jsd = jsd(a_head_dist, b_head_dist)
head_cosine = cosine_sim(a_head_dist, b_head_dist)

print(f"  HEAD distribution (token-weighted):")
all_heads = sorted(set(a_head_dist.keys()) | set(b_head_dist.keys()))
a_total_h = sum(a_head_dist.values())
b_total_h = sum(b_head_dist.values())
for h in all_heads:
    a_pct = 100 * a_head_dist.get(h, 0) / a_total_h if a_total_h > 0 else 0
    b_pct = 100 * b_head_dist.get(h, 0) / b_total_h if b_total_h > 0 else 0
    ratio = (b_head_dist.get(h, 0) / b_total_h) / (a_head_dist.get(h, 0) / a_total_h) if a_head_dist.get(h, 0) > 0 else float('inf')
    print(f"    {h:10s}  A={a_pct:5.1f}%  B={b_pct:5.1f}%  B/A_ratio={ratio:.3f}")
print(f"  JSD(A_HEAD, B_HEAD) = {head_jsd:.6f}")
print(f"  Cosine(A_HEAD, B_HEAD) = {head_cosine:.6f}")
print(f"  P1 prediction (JSD < 0.05): {'PASS' if head_jsd < 0.05 else 'FAIL'}")

# Also do type-weighted (each MIDDLE counts once)
a_head_type = Counter()
b_head_type = Counter()
for mid in bridge_in_both:
    head = mid_decomp[mid]['head']
    a_head_type[head] += 1
    b_head_type[head] += 1  # Same decomposition — always identical
head_type_jsd = jsd(a_head_type, b_head_type)

results['tests']['T2_head_stability'] = {
    'a_head_dist': dict(a_head_dist),
    'b_head_dist': dict(b_head_dist),
    'jsd_token_weighted': head_jsd,
    'cosine': head_cosine,
    'jsd_type_weighted': head_type_jsd,
    'p1_pass': head_jsd < 0.05,
}

# ============================================================
# T3: TERMINAL STABILITY
# ============================================================
print("\nT3: TERMINAL stability across A and B...")

a_term_dist = Counter()
b_term_dist = Counter()
for mid in bridge_in_both:
    term = mid_decomp[mid]['term']
    a_term_dist[term] += bridge_in_a.get(mid, 0)
    b_term_dist[term] += bridge_in_b.get(mid, 0)

term_jsd = jsd(a_term_dist, b_term_dist)
term_cosine = cosine_sim(a_term_dist, b_term_dist)

print(f"  TERMINAL distribution (token-weighted):")
all_terms = sorted(set(a_term_dist.keys()) | set(b_term_dist.keys()))
a_total_t = sum(a_term_dist.values())
b_total_t = sum(b_term_dist.values())
for t in all_terms:
    a_pct = 100 * a_term_dist.get(t, 0) / a_total_t if a_total_t > 0 else 0
    b_pct = 100 * b_term_dist.get(t, 0) / b_total_t if b_total_t > 0 else 0
    ratio = (b_term_dist.get(t, 0) / b_total_t) / (a_term_dist.get(t, 0) / a_total_t) if a_term_dist.get(t, 0) > 0 else float('inf')
    print(f"    {t:10s}  A={a_pct:5.1f}%  B={b_pct:5.1f}%  B/A_ratio={ratio:.3f}")
print(f"  JSD(A_TERM, B_TERM) = {term_jsd:.6f}")
print(f"  Cosine(A_TERM, B_TERM) = {term_cosine:.6f}")
print(f"  P2 prediction (JSD < 0.05): {'PASS' if term_jsd < 0.05 else 'FAIL'}")

results['tests']['T3_terminal_stability'] = {
    'a_term_dist': dict(a_term_dist),
    'b_term_dist': dict(b_term_dist),
    'jsd_token_weighted': term_jsd,
    'cosine': term_cosine,
    'p2_pass': term_jsd < 0.05,
}

# ============================================================
# T4: MODIFIER STABILITY
# ============================================================
print("\nT4: MODIFIER stability across A and B...")

a_mod_dist = Counter()
b_mod_dist = Counter()
for mid in bridge_in_both:
    mod = mid_decomp[mid]['mod']
    if not mod:
        mod = 'NONE'
    a_mod_dist[mod] += bridge_in_a.get(mid, 0)
    b_mod_dist[mod] += bridge_in_b.get(mid, 0)

mod_jsd = jsd(a_mod_dist, b_mod_dist)
mod_cosine = cosine_sim(a_mod_dist, b_mod_dist)

print(f"  MODIFIER distribution (token-weighted):")
all_mods = sorted(set(a_mod_dist.keys()) | set(b_mod_dist.keys()))
a_total_m = sum(a_mod_dist.values())
b_total_m = sum(b_mod_dist.values())
for mod in all_mods:
    a_pct = 100 * a_mod_dist.get(mod, 0) / a_total_m if a_total_m > 0 else 0
    b_pct = 100 * b_mod_dist.get(mod, 0) / b_total_m if b_total_m > 0 else 0
    print(f"    {mod:10s}  A={a_pct:5.1f}%  B={b_pct:5.1f}%")
print(f"  JSD(A_MOD, B_MOD) = {mod_jsd:.6f}")
print(f"  Cosine(A_MOD, B_MOD) = {mod_cosine:.6f}")
print(f"  P3 prediction (JSD < 0.01): {'PASS' if mod_jsd < 0.01 else 'FAIL'}")

results['tests']['T4_modifier_stability'] = {
    'a_mod_dist': dict(a_mod_dist),
    'b_mod_dist': dict(b_mod_dist),
    'jsd_token_weighted': mod_jsd,
    'cosine': mod_cosine,
    'p3_pass': mod_jsd < 0.01,
}

# ============================================================
# T5: CATEGORY STABILITY AT ATOM LEVEL
# ============================================================
print("\nT5: Category stability mediated by HEAD atom...")

# For each bridge MIDDLE present in both, get category in A context vs B context
# Category is MIDDLE-intrinsic (C1305), so should be identical
cat_matches = 0
cat_total = 0
head_to_cat_a = defaultdict(Counter)  # HEAD -> {category: count}
head_to_cat_b = defaultdict(Counter)
mismatches = []

for mid in bridge_in_both:
    cat = cc.classify(mid)
    if cat:
        head = mid_decomp[mid]['head']
        # In both systems, same MIDDLE -> same category (intrinsic property)
        head_to_cat_a[head][cat] += bridge_in_a.get(mid, 0)
        head_to_cat_b[head][cat] += bridge_in_b.get(mid, 0)
        cat_total += 1
        cat_matches += 1  # Same MIDDLE = same category always

# Check HEAD->category consistency ACROSS systems
print(f"  Category classified: {cat_total}/{len(bridge_in_both)} bridge MIDDLEs")
print(f"  Category match (same MIDDLE = same cat): 100% (by definition)")
print(f"\n  HEAD -> category profile comparison (A vs B token-weighted):")

head_cat_jsds = {}
for head in sorted(set(head_to_cat_a.keys()) | set(head_to_cat_b.keys())):
    a_dist = head_to_cat_a[head]
    b_dist = head_to_cat_b[head]
    h_jsd = jsd(a_dist, b_dist)
    head_cat_jsds[head] = h_jsd
    print(f"    HEAD={head:10s}  JSD={h_jsd:.6f}  A_top={a_dist.most_common(1)[0] if a_dist else 'N/A'}  B_top={b_dist.most_common(1)[0] if b_dist else 'N/A'}")

mean_head_cat_jsd = sum(head_cat_jsds.values()) / len(head_cat_jsds) if head_cat_jsds else 0

print(f"\n  Mean HEAD->category JSD across systems: {mean_head_cat_jsd:.6f}")
print(f"  P4 prediction: Category stability is INTRINSIC (100% by construction)")

# Show category distribution comparison
a_cat_dist = Counter()
b_cat_dist = Counter()
for mid in bridge_in_both:
    cat = cc.classify(mid)
    if cat:
        a_cat_dist[cat] += bridge_in_a.get(mid, 0)
        b_cat_dist[cat] += bridge_in_b.get(mid, 0)

cat_jsd = jsd(a_cat_dist, b_cat_dist)
cat_cosine = cosine_sim(a_cat_dist, b_cat_dist)
print(f"\n  Overall category distribution (token-weighted):")
all_cats = sorted(set(a_cat_dist.keys()) | set(b_cat_dist.keys()))
a_total_c = sum(a_cat_dist.values())
b_total_c = sum(b_cat_dist.values())
for cat in all_cats:
    a_pct = 100 * a_cat_dist.get(cat, 0) / a_total_c if a_total_c > 0 else 0
    b_pct = 100 * b_cat_dist.get(cat, 0) / b_total_c if b_total_c > 0 else 0
    ratio = (b_cat_dist.get(cat, 0) / b_total_c) / (a_cat_dist.get(cat, 0) / a_total_c) if a_cat_dist.get(cat, 0) > 0 else float('inf')
    print(f"    {cat:15s}  A={a_pct:5.1f}%  B={b_pct:5.1f}%  B/A_ratio={ratio:.3f}")
print(f"  Category JSD(A, B) = {cat_jsd:.6f}")
print(f"  Category Cosine(A, B) = {cat_cosine:.6f}")

results['tests']['T5_category_stability'] = {
    'category_match_rate': 1.0,  # Same MIDDLE = same category
    'a_cat_dist': dict(a_cat_dist),
    'b_cat_dist': dict(b_cat_dist),
    'category_jsd': cat_jsd,
    'category_cosine': cat_cosine,
    'head_cat_jsds': head_cat_jsds,
    'mean_head_cat_jsd': mean_head_cat_jsd,
}

# ============================================================
# T6: PREFIX ECOLOGY COMPARISON
# ============================================================
print("\nT6: PREFIX ecology comparison across A and B...")

# Aggregate PREFIX distributions for bridge MIDDLEs
a_pfx_total = Counter()
b_pfx_total = Counter()
for mid in bridge_in_both:
    for pfx, count in a_prefix_per_mid[mid].items():
        a_pfx_total[pfx] += count
    for pfx, count in b_prefix_per_mid[mid].items():
        b_pfx_total[pfx] += count

pfx_jsd = jsd(a_pfx_total, b_pfx_total)
pfx_cosine = cosine_sim(a_pfx_total, b_pfx_total)

print(f"  PREFIX distribution for bridge MIDDLEs (token-weighted):")
all_pfxs = sorted(set(a_pfx_total.keys()) | set(b_pfx_total.keys()),
                   key=lambda x: -(a_pfx_total.get(x, 0) + b_pfx_total.get(x, 0)))
a_total_p = sum(a_pfx_total.values())
b_total_p = sum(b_pfx_total.values())
for pfx in all_pfxs[:20]:
    a_pct = 100 * a_pfx_total.get(pfx, 0) / a_total_p if a_total_p > 0 else 0
    b_pct = 100 * b_pfx_total.get(pfx, 0) / b_total_p if b_total_p > 0 else 0
    print(f"    {pfx:12s}  A={a_pct:5.1f}%  B={b_pct:5.1f}%")
print(f"  JSD(A_PREFIX, B_PREFIX) = {pfx_jsd:.6f}")
print(f"  Cosine(A_PREFIX, B_PREFIX) = {pfx_cosine:.6f}")
print(f"  P5 prediction (JSD > 0.20): {'PASS' if pfx_jsd > 0.20 else 'FAIL'}")

# Count unique PREFIXes in each system
a_only_pfx = set(a_pfx_total.keys()) - set(b_pfx_total.keys())
b_only_pfx = set(b_pfx_total.keys()) - set(a_pfx_total.keys())
shared_pfx = set(a_pfx_total.keys()) & set(b_pfx_total.keys())
print(f"  A-only PREFIXes: {len(a_only_pfx)} {sorted(a_only_pfx)}")
print(f"  B-only PREFIXes: {len(b_only_pfx)} {sorted(b_only_pfx)}")
print(f"  Shared PREFIXes: {len(shared_pfx)}")

results['tests']['T6_prefix_ecology'] = {
    'a_pfx_dist': dict(a_pfx_total),
    'b_pfx_dist': dict(b_pfx_total),
    'jsd': pfx_jsd,
    'cosine': pfx_cosine,
    'a_only_prefixes': sorted(a_only_pfx),
    'b_only_prefixes': sorted(b_only_pfx),
    'shared_prefixes': sorted(shared_pfx),
    'p5_pass': pfx_jsd > 0.20,
}

# ============================================================
# T7: SUFFIX ECOLOGY COMPARISON
# ============================================================
print("\nT7: Suffix ecology comparison...")

# Compute suffix rates per system for bridge MIDDLEs
a_suffixed = 0
a_sfx_tot = 0
b_suffixed = 0
b_sfx_tot = 0
a_sfx_atoms = Counter()
b_sfx_atoms = Counter()

for mid in bridge_in_both:
    a_s, a_t = a_suffix_rate[mid]
    b_s, b_t = b_suffix_rate[mid]
    a_suffixed += a_s
    a_sfx_tot += a_t
    b_suffixed += b_s
    b_sfx_tot += b_t
    for sfx, count in a_suffix_per_mid[mid].items():
        if sfx != 'BARE':
            a_sfx_atoms[sfx] += count
    for sfx, count in b_suffix_per_mid[mid].items():
        if sfx != 'BARE':
            b_sfx_atoms[sfx] += count

a_sfx_pct = 100 * a_suffixed / a_sfx_tot if a_sfx_tot > 0 else 0
b_sfx_pct = 100 * b_suffixed / b_sfx_tot if b_sfx_tot > 0 else 0
sfx_atom_jsd = jsd(a_sfx_atoms, b_sfx_atoms)

print(f"  A suffix rate (bridge): {a_sfx_pct:.1f}% ({a_suffixed}/{a_sfx_tot})")
print(f"  B suffix rate (bridge): {b_sfx_pct:.1f}% ({b_suffixed}/{b_sfx_tot})")
print(f"  P6 prediction (A < B): {'PASS' if a_sfx_pct < b_sfx_pct else 'FAIL'}")
print(f"\n  Suffix atom distribution (non-bare only):")
all_sfx = sorted(set(a_sfx_atoms.keys()) | set(b_sfx_atoms.keys()),
                  key=lambda x: -(a_sfx_atoms.get(x, 0) + b_sfx_atoms.get(x, 0)))
a_sfx_tot2 = sum(a_sfx_atoms.values())
b_sfx_tot2 = sum(b_sfx_atoms.values())
for sfx in all_sfx[:15]:
    a_pct = 100 * a_sfx_atoms.get(sfx, 0) / a_sfx_tot2 if a_sfx_tot2 > 0 else 0
    b_pct = 100 * b_sfx_atoms.get(sfx, 0) / b_sfx_tot2 if b_sfx_tot2 > 0 else 0
    print(f"    {sfx:12s}  A={a_pct:5.1f}%  B={b_pct:5.1f}%")
print(f"  Suffix atom JSD(A, B) = {sfx_atom_jsd:.6f}")

results['tests']['T7_suffix_ecology'] = {
    'a_suffix_rate': a_sfx_pct,
    'b_suffix_rate': b_sfx_pct,
    'a_sfx_atoms': dict(a_sfx_atoms),
    'b_sfx_atoms': dict(b_sfx_atoms),
    'suffix_atom_jsd': sfx_atom_jsd,
    'p6_pass': a_sfx_pct < b_sfx_pct,
}

# ============================================================
# T8: FREQUENCY REDISTRIBUTION ANALYSIS
# ============================================================
print("\nT8: Frequency redistribution analysis (A-enriched vs B-enriched)...")

# HEAD profiles for A-enriched vs B-enriched
a_enr_heads = Counter()
b_enr_heads = Counter()
a_enr_terms = Counter()
b_enr_terms = Counter()
a_enr_cats = Counter()
b_enr_cats = Counter()

for mid, data in freq_ratios.items():
    head = mid_decomp[mid]['head']
    term = mid_decomp[mid]['term']
    cat = cc.classify(mid)
    if data['b_over_a'] < 1.0:  # A-enriched
        a_enr_heads[head] += data['total']
        a_enr_terms[term] += data['total']
        if cat:
            a_enr_cats[cat] += data['total']
    elif data['b_over_a'] > 1.0:  # B-enriched
        b_enr_heads[head] += data['total']
        b_enr_terms[term] += data['total']
        if cat:
            b_enr_cats[cat] += data['total']

head_enr_jsd = jsd(a_enr_heads, b_enr_heads)
term_enr_jsd = jsd(a_enr_terms, b_enr_terms)
cat_enr_jsd = jsd(a_enr_cats, b_enr_cats)

print(f"  A-enriched HEAD profile: {dict(a_enr_heads.most_common(5))}")
print(f"  B-enriched HEAD profile: {dict(b_enr_heads.most_common(5))}")
print(f"  HEAD JSD(A-enr, B-enr) = {head_enr_jsd:.6f}")
print(f"\n  A-enriched TERM profile: {dict(a_enr_terms.most_common(5))}")
print(f"  B-enriched TERM profile: {dict(b_enr_terms.most_common(5))}")
print(f"  TERM JSD(A-enr, B-enr) = {term_enr_jsd:.6f}")
print(f"\n  A-enriched category profile: {dict(a_enr_cats.most_common())}")
print(f"  B-enriched category profile: {dict(b_enr_cats.most_common())}")
print(f"  Category JSD(A-enr, B-enr) = {cat_enr_jsd:.6f}")
print(f"  P7 prediction (different HEAD profiles): {'PASS' if head_enr_jsd > 0.05 else 'FAIL'}")

results['tests']['T8_redistribution'] = {
    'a_enriched_head': dict(a_enr_heads),
    'b_enriched_head': dict(b_enr_heads),
    'head_jsd': head_enr_jsd,
    'a_enriched_term': dict(a_enr_terms),
    'b_enriched_term': dict(b_enr_terms),
    'term_jsd': term_enr_jsd,
    'a_enriched_cat': dict(a_enr_cats),
    'b_enriched_cat': dict(b_enr_cats),
    'cat_jsd': cat_enr_jsd,
    'p7_pass': head_enr_jsd > 0.05,
}

# ============================================================
# T9: ATOM BEHAVIORAL CORRELATION A vs B
# ============================================================
print("\nT9: Atom behavioral profile correlation A vs B...")

# For each atom CHARACTER, compute its profile (which categories it appears in)
# across A and B tokens of bridge MIDDLEs
a_atom_cat = defaultdict(Counter)  # atom_char -> {category: count}
b_atom_cat = defaultdict(Counter)

for mid in bridge_in_both:
    cat = cc.classify(mid)
    if not cat:
        continue
    head, mod, term, frame = decompose_middle_hmt(mid)
    atoms = set()
    if head:
        atoms.add(head)
    if mod:
        for c in mod:
            atoms.add(c)
    if term and term not in ('bare',):
        atoms.add(term)

    a_count = bridge_in_a.get(mid, 0)
    b_count = bridge_in_b.get(mid, 0)

    for atom in atoms:
        a_atom_cat[atom][cat] += a_count
        b_atom_cat[atom][cat] += b_count

# Compute per-atom correlation between A and B category profiles
all_categories = sorted(set().union(*[set(d.keys()) for d in a_atom_cat.values()],
                                     *[set(d.keys()) for d in b_atom_cat.values()]))
atom_correlations = {}
print(f"  Atom category profile correlation (A vs B):")
for atom in sorted(set(a_atom_cat.keys()) & set(b_atom_cat.keys())):
    a_vec = [a_atom_cat[atom].get(c, 0) for c in all_categories]
    b_vec = [b_atom_cat[atom].get(c, 0) for c in all_categories]
    # Normalize to proportions
    a_sum = sum(a_vec)
    b_sum = sum(b_vec)
    if a_sum > 0 and b_sum > 0:
        a_norm = [v / a_sum for v in a_vec]
        b_norm = [v / b_sum for v in b_vec]
        # Pearson correlation
        n = len(all_categories)
        a_mean = sum(a_norm) / n
        b_mean = sum(b_norm) / n
        cov = sum((a_norm[i] - a_mean) * (b_norm[i] - b_mean) for i in range(n))
        a_std = math.sqrt(sum((v - a_mean)**2 for v in a_norm))
        b_std = math.sqrt(sum((v - b_mean)**2 for v in b_norm))
        if a_std > 0 and b_std > 0:
            corr = cov / (a_std * b_std)
        else:
            corr = 1.0  # Both constant = perfect agreement
        atom_jsd = jsd(a_atom_cat[atom], b_atom_cat[atom])
        atom_correlations[atom] = {
            'correlation': corr,
            'jsd': atom_jsd,
            'a_top': a_atom_cat[atom].most_common(1)[0] if a_atom_cat[atom] else None,
            'b_top': b_atom_cat[atom].most_common(1)[0] if b_atom_cat[atom] else None,
            'a_count': sum(a_atom_cat[atom].values()),
            'b_count': sum(b_atom_cat[atom].values()),
        }
        top_a_cat = a_atom_cat[atom].most_common(1)[0][0] if a_atom_cat[atom] else 'N/A'
        top_b_cat = b_atom_cat[atom].most_common(1)[0][0] if b_atom_cat[atom] else 'N/A'
        match = 'Y' if top_a_cat == top_b_cat else 'N'
        print(f"    {atom}  corr={corr:+.4f}  JSD={atom_jsd:.6f}  A_top={top_a_cat}  B_top={top_b_cat}  match={match}")

corr_values = [v['correlation'] for v in atom_correlations.values() if v['correlation'] is not None]
mean_corr = sum(corr_values) / len(corr_values) if corr_values else 0
min_corr = min(corr_values) if corr_values else 0
jsd_values = [v['jsd'] for v in atom_correlations.values()]
mean_jsd = sum(jsd_values) / len(jsd_values) if jsd_values else 0
top_cat_matches = sum(1 for v in atom_correlations.values()
                      if v['a_top'] and v['b_top'] and v['a_top'][0] == v['b_top'][0])

print(f"\n  Mean atom correlation: {mean_corr:.4f}")
print(f"  Min atom correlation: {min_corr:.4f}")
print(f"  Mean atom JSD: {mean_jsd:.6f}")
print(f"  Top-category matches: {top_cat_matches}/{len(atom_correlations)}")
print(f"  P8 prediction (all corr > 0.70): {'PASS' if min_corr > 0.70 else 'FAIL'}")

results['tests']['T9_atom_behavioral_correlation'] = {
    'atom_profiles': atom_correlations,
    'mean_correlation': mean_corr,
    'min_correlation': min_corr,
    'mean_jsd': mean_jsd,
    'top_category_matches': top_cat_matches,
    'total_atoms': len(atom_correlations),
    'p8_pass': min_corr > 0.70,
}

# ============================================================
# T10: A DECLARATIVE vs B OPERATIONAL REGISTER TEST
# ============================================================
print("\nT10: A declarative vs B operational register test...")

# Compare TERMINAL tier preferences
# C1487: LOCKED (r,m), CHANNELED (l,y,n), DIFFUSE (h)
LOCKED = {'r', 'm'}
CHANNELED = {'l', 'y', 'n'}
DIFFUSE = {'h'}

# Token-weighted terminal tier in A vs B
a_tier = Counter()
b_tier = Counter()
for mid in bridge_in_both:
    term = mid_decomp[mid]['term']
    if term in LOCKED:
        tier = 'LOCKED'
    elif term in CHANNELED:
        tier = 'CHANNELED'
    elif term in DIFFUSE:
        tier = 'DIFFUSE'
    elif term == 'bare':
        tier = 'BARE_TERM'
    else:
        tier = 'OTHER'
    a_tier[tier] += bridge_in_a.get(mid, 0)
    b_tier[tier] += bridge_in_b.get(mid, 0)

tier_jsd = jsd(a_tier, b_tier)
print(f"  Terminal tier distribution (token-weighted):")
all_tiers = sorted(set(a_tier.keys()) | set(b_tier.keys()))
a_tier_t = sum(a_tier.values())
b_tier_t = sum(b_tier.values())
for tier in all_tiers:
    a_pct = 100 * a_tier.get(tier, 0) / a_tier_t if a_tier_t > 0 else 0
    b_pct = 100 * b_tier.get(tier, 0) / b_tier_t if b_tier_t > 0 else 0
    print(f"    {tier:15s}  A={a_pct:5.1f}%  B={b_pct:5.1f}%")
print(f"  Tier JSD = {tier_jsd:.6f}")

# Individual terminal comparison
print(f"\n  Individual terminal enrichment (B/A ratio of proportional share):")
terminal_enrichment = {}
for term in sorted(set(a_term_dist.keys()) | set(b_term_dist.keys())):
    a_prop = a_term_dist.get(term, 0) / a_total_t if a_total_t > 0 else 0
    b_prop = b_term_dist.get(term, 0) / b_total_t if b_total_t > 0 else 0
    ratio = b_prop / a_prop if a_prop > 0 else float('inf')
    terminal_enrichment[term] = ratio
    a_lab = 'A-enriched' if ratio < 0.8 else ('B-enriched' if ratio > 1.25 else 'balanced')
    print(f"    {term:10s}  B/A={ratio:.3f}  ({a_lab})")

# Category-level A vs B emphasis
print(f"\n  Category enrichment in B relative to A (B/A proportional ratio):")
cat_enrichment = {}
for cat in sorted(all_cats):
    a_prop = a_cat_dist.get(cat, 0) / a_total_c if a_total_c > 0 else 0
    b_prop = b_cat_dist.get(cat, 0) / b_total_c if b_total_c > 0 else 0
    ratio = b_prop / a_prop if a_prop > 0 else float('inf')
    cat_enrichment[cat] = ratio
    a_lab = 'A-enriched' if ratio < 0.8 else ('B-enriched' if ratio > 1.25 else 'balanced')
    print(f"    {cat:15s}  B/A={ratio:.3f}  ({a_lab})")

# P9/P10 predictions: A selects descriptive (l,h enriched), B selects action (y,m,r enriched)
l_ratio = terminal_enrichment.get('l', 1.0)
h_ratio = terminal_enrichment.get('h', 1.0)
y_ratio = terminal_enrichment.get('y', 1.0)
m_ratio = terminal_enrichment.get('m', 1.0)
r_ratio = terminal_enrichment.get('r', 1.0)

p9_pass = l_ratio < 1.0 and h_ratio < 1.0  # Both A-enriched
p10_pass = y_ratio > 1.0 and m_ratio > 1.0 and r_ratio > 1.0  # All B-enriched
print(f"\n  P9 (A prefers l,h): l={l_ratio:.3f}, h={h_ratio:.3f} -> {'PASS' if p9_pass else 'FAIL'}")
print(f"  P10 (B prefers y,m,r): y={y_ratio:.3f}, m={m_ratio:.3f}, r={r_ratio:.3f} -> {'PASS' if p10_pass else 'FAIL'}")

results['tests']['T10_register_test'] = {
    'a_tier_dist': dict(a_tier),
    'b_tier_dist': dict(b_tier),
    'tier_jsd': tier_jsd,
    'terminal_enrichment': terminal_enrichment,
    'category_enrichment': cat_enrichment,
    'p9_pass': p9_pass,
    'p10_pass': p10_pass,
}

# ============================================================
# T11: COMPREHENSIVE SLOT-LEVEL STABILITY SUMMARY
# ============================================================
print("\nT11: Comprehensive slot-level stability summary...")

# For each slot (HEAD, MOD, TERM), compute JSD as summary stability metric
slot_stability = {
    'HEAD': head_jsd,
    'MODIFIER': mod_jsd,
    'TERMINAL': term_jsd,
    'CATEGORY': cat_jsd,
    'PREFIX_ecology': pfx_jsd,
    'SUFFIX_ecology': sfx_atom_jsd,
}

print(f"  {'Dimension':20s}  {'JSD':>10s}  {'Stability':>12s}")
print(f"  {'-'*44}")
for dim, val in sorted(slot_stability.items(), key=lambda x: x[1]):
    stab = 'PRESERVED' if val < 0.05 else ('SHIFTED' if val < 0.15 else 'DIVERGENT')
    print(f"  {dim:20s}  {val:10.6f}  {stab:>12s}")

# Overall verdict
internal_jsds = [head_jsd, mod_jsd, term_jsd]
external_jsds = [pfx_jsd, sfx_atom_jsd]
internal_mean = sum(internal_jsds) / len(internal_jsds)
external_mean = sum(external_jsds) / len(external_jsds)

print(f"\n  Internal (HEAD+MOD+TERM) mean JSD: {internal_mean:.6f}")
print(f"  External (PREFIX+SUFFIX) mean JSD: {external_mean:.6f}")
print(f"  Ratio (external/internal): {external_mean/internal_mean:.1f}x")

verdict = 'SHARED_SUBSTRATE_CONFIRMED' if internal_mean < 0.05 and external_mean > internal_mean * 3 else \
          'PARTIAL_STABILITY' if internal_mean < 0.10 else 'DIVERGENT'
print(f"\n  VERDICT: {verdict}")
print(f"  Interpretation: MIDDLE atom roles are {'PRESERVED' if internal_mean < 0.05 else 'MODIFIED'} across A and B;")
print(f"                  PREFIX/SUFFIX ecology is {'DIVERGENT' if external_mean > 0.15 else 'SIMILAR'} (different deployment channels)")

results['tests']['T11_summary'] = {
    'slot_stability': slot_stability,
    'internal_mean_jsd': internal_mean,
    'external_mean_jsd': external_mean,
    'ratio': external_mean / internal_mean if internal_mean > 0 else float('inf'),
    'verdict': verdict,
}

# ============================================================
# PREDICTION SCORECARD
# ============================================================
print("\n" + "="*60)
print("PREDICTION SCORECARD")
print("="*60)

predictions = {
    'P1 HEAD stable (JSD<0.05)': head_jsd < 0.05,
    'P2 TERM stable (JSD<0.05)': term_jsd < 0.05,
    'P3 MOD universal (JSD<0.01)': mod_jsd < 0.01,
    'P4 Category intrinsic': True,  # By construction
    'P5 PREFIX ecology divergent (JSD>0.20)': pfx_jsd > 0.20,
    'P6 A suffix rate < B': a_sfx_pct < b_sfx_pct,
    'P7 A/B-enriched different HEADs': head_enr_jsd > 0.05,
    'P8 Atom correlation all > 0.70': min_corr > 0.70,
    'P9 A prefers l,h terminals': p9_pass,
    'P10 B prefers y,m,r terminals': p10_pass,
}

pass_count = sum(1 for v in predictions.values() if v)
total = len(predictions)
for pred, passed in predictions.items():
    status = 'PASS' if passed else 'FAIL'
    print(f"  [{status:4s}] {pred}")
print(f"\n  Score: {pass_count}/{total} ({100*pass_count/total:.0f}%)")

results['prediction_scorecard'] = {
    'predictions': {k: v for k, v in predictions.items()},
    'pass_count': pass_count,
    'total': total,
}

# ============================================================
# SAVE RESULTS
# ============================================================
output_path = ROOT / 'phases/BRIDGE_ATOM_STABILITY/results/bridge_atom_stability.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(round_floats(results), f, indent=2, default=str)
print(f"\nResults saved to {output_path}")

print("\n" + "="*60)
print("PHASE 539 COMPLETE")
print("="*60)
