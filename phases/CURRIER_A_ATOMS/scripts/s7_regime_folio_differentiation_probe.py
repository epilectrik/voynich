#!/usr/bin/env python3
"""
s7_regime_folio_differentiation_probe.py — Probe whether atom-level features
can differentiate individual B folios within the same section.

Background:
  - C1169: ~27% design freedom in B folios (constrained channels + free channels)
  - B folios share aggregate properties (kernel composition, escape rate) within
    REGIME + section groups
  - Question: What atom-level choices make individual programs DISTINCT within
    the same operational group?

Tests:
  1. Per-folio atom profiles (HEAD, MOD, TERM, PREFIX distributions + depths)
  2. Within-section variance decomposition (which features are free vs constrained)
  3. Pairwise JSD within section (which atoms differentiate folios)
  4. Feature importance ranking (between-folio / total variance)
  5. Section comparison (do different sections use different freedom channels?)
  6. Specific folio pairs (most similar / most different within Herbal)
  7. Connection to operational profiles (atom variance vs operational variance)
"""

import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

import math
import numpy as np
from collections import defaultdict, Counter
from itertools import combinations
from scripts.voynich import Transcript, Morphology

# ============================================================
# SECTION NAME MAP
# ============================================================
SECTION_NAMES = {'H': 'Herbal', 'S': 'Stars', 'B': 'Bio', 'T': 'Pharma', 'C': 'Cosmo'}

# ============================================================
# CONFIG
# ============================================================
MIN_TOKENS = 50
EPSILON = 1e-10

HEAD_ATOMS = ['a', 'e', 'o', 'k', 't']
MOD_ATOMS = ['p', 'f', 'i', 'c', 'd', 's']
TERM_ATOMS = ['y', 'n', 'l', 'r', 'm', 'h']
PREFIX_LIST = ['ch', 'sh', 'qo', 'ok', 'ot', 'da', 'ol', 'ct']

# ============================================================
# LOAD DATA
# ============================================================
tx = Transcript()
morph = Morphology()

print("=" * 70)
print("S7: REGIME FOLIO DIFFERENTIATION PROBE")
print("=" * 70)

# Collect B tokens
folio_tokens = defaultdict(list)  # folio -> list of tokens
folio_section = {}

for token in tx.currier_b():
    if token.placement.startswith('L'):
        continue
    folio_tokens[token.folio].append(token)
    folio_section[token.folio] = token.section

# Filter to folios with >= MIN_TOKENS
valid_folios = {f for f, toks in folio_tokens.items() if len(toks) >= MIN_TOKENS}
print(f"\nB folios with >= {MIN_TOKENS} tokens: {len(valid_folios)}")

# ============================================================
# 1. PER-FOLIO ATOM PROFILES
# ============================================================
print("\n" + "=" * 70)
print("1. COMPUTING PER-FOLIO ATOM PROFILES")
print("=" * 70)

folio_profiles = {}

for folio in sorted(valid_folios):
    tokens = folio_tokens[folio]
    n = len(tokens)

    # Atomize all tokens
    head_counts = Counter()
    mod_counts = Counter()
    term_counts = Counter()
    prefix_counts = Counter()
    e_depths = []
    i_depths = []
    token_lengths = []
    headless_count = 0
    no_prefix_count = 0

    for tok in tokens:
        a = morph.atomize(tok.word)
        token_lengths.append(len(tok.word))

        # HEAD
        head_char = a.head
        if head_char:
            head_counts[head_char] += 1
        if a.is_headless:
            headless_count += 1

        # PREFIX
        if a.prefix:
            prefix_counts[a.prefix] += 1
        else:
            no_prefix_count += 1

        # MOD and TERM from atoms
        for char, role, _ in a.atoms:
            if role == 'MOD':
                mod_counts[char] += 1
            elif role == 'TERM':
                term_counts[char] += 1

        # Depths
        e_depths.append(a.e_depth)
        if a.i_depth > 0:
            i_depths.append(a.i_depth)

    # Build profile dict
    profile = {
        'section': folio_section[folio],
        'n_tokens': n,
    }

    # HEAD distribution
    total_heads = sum(head_counts.values()) + headless_count
    for h in HEAD_ATOMS:
        profile[f'head_{h}'] = head_counts[h] / total_heads if total_heads > 0 else 0
    profile['head_headless'] = headless_count / total_heads if total_heads > 0 else 0

    # MOD distribution
    total_mods = sum(mod_counts.values())
    for m in MOD_ATOMS:
        profile[f'mod_{m}'] = mod_counts[m] / max(total_mods, 1)

    # TERM distribution
    total_terms = sum(term_counts.values())
    for t in TERM_ATOMS:
        profile[f'term_{t}'] = term_counts[t] / max(total_terms, 1)

    # PREFIX distribution
    for p in PREFIX_LIST:
        profile[f'pfx_{p}'] = prefix_counts[p] / n
    profile['pfx_none'] = no_prefix_count / n

    # Depths and length
    profile['e_depth_mean'] = np.mean(e_depths) if e_depths else 0
    profile['i_depth_mean'] = np.mean(i_depths) if i_depths else 0
    profile['token_len_mean'] = np.mean(token_lengths) if token_lengths else 0

    folio_profiles[folio] = profile

# Summary
section_counts = Counter(folio_section[f] for f in valid_folios)
for sec in sorted(section_counts):
    print(f"  Section {SECTION_NAMES.get(sec, sec)} ({sec}): {section_counts[sec]} folios")

# ============================================================
# FEATURE NAMES
# ============================================================
FEATURE_NAMES = (
    [f'head_{h}' for h in HEAD_ATOMS] + ['head_headless'] +
    [f'mod_{m}' for m in MOD_ATOMS] +
    [f'term_{t}' for t in TERM_ATOMS] +
    [f'pfx_{p}' for p in PREFIX_LIST] + ['pfx_none'] +
    ['e_depth_mean', 'i_depth_mean', 'token_len_mean']
)

# ============================================================
# 2. WITHIN-SECTION VARIANCE DECOMPOSITION
# ============================================================
print("\n" + "=" * 70)
print("2. WITHIN-SECTION VARIANCE DECOMPOSITION")
print("=" * 70)

section_folios = defaultdict(list)
for f in valid_folios:
    section_folios[folio_section[f]].append(f)

feature_variance_by_section = {}  # section -> {feature: variance}
feature_cv_by_section = {}  # section -> {feature: coefficient_of_variation}

for sec in sorted(section_folios):
    folios = section_folios[sec]
    if len(folios) < 3:
        continue

    variance_dict = {}
    cv_dict = {}
    for feat in FEATURE_NAMES:
        vals = [folio_profiles[f][feat] for f in folios]
        v = np.var(vals)
        m = np.mean(vals)
        variance_dict[feat] = float(v)
        cv_dict[feat] = float(np.sqrt(v) / m) if m > 1e-8 else 0.0

    feature_variance_by_section[sec] = variance_dict
    feature_cv_by_section[sec] = cv_dict

    # Report top/bottom 5 by CV
    sorted_by_cv = sorted(cv_dict.items(), key=lambda x: -x[1])
    print(f"\n  Section {SECTION_NAMES.get(sec, sec)} ({len(folios)} folios):")
    print(f"    HIGHEST variance (design freedom channels):")
    for feat, cv in sorted_by_cv[:5]:
        print(f"      {feat:20s}  CV={cv:.3f}  var={variance_dict[feat]:.6f}")
    print(f"    LOWEST variance (constrained channels):")
    for feat, cv in sorted_by_cv[-5:]:
        print(f"      {feat:20s}  CV={cv:.3f}  var={variance_dict[feat]:.6f}")


# ============================================================
# 3. PAIRWISE JSD WITHIN SECTION
# ============================================================
print("\n" + "=" * 70)
print("3. PAIRWISE JENSEN-SHANNON DIVERGENCE WITHIN SECTION")
print("=" * 70)

def kl_divergence(p, q):
    """KL(P||Q) with epsilon smoothing."""
    result = 0.0
    for pi, qi in zip(p, q):
        pi = pi + EPSILON
        qi = qi + EPSILON
        result += pi * math.log2(pi / qi)
    return result

def jsd(p, q):
    """Jensen-Shannon divergence."""
    m = [(pi + qi) / 2 for pi, qi in zip(p, q)]
    return 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)

def get_distribution(profile, feature_prefix, keys):
    """Extract a probability distribution from profile."""
    vals = [profile.get(f'{feature_prefix}_{k}', 0) for k in keys]
    s = sum(vals)
    if s < EPSILON:
        return [1.0 / len(vals)] * len(vals)
    return [v / s for v in vals]

# Compute pairwise JSD for HEAD, MOD, TERM distributions
head_keys = HEAD_ATOMS + ['headless']
mod_keys = MOD_ATOMS
term_keys = TERM_ATOMS
pfx_keys = PREFIX_LIST + ['none']

jsd_results = {}  # section -> list of (f1, f2, head_jsd, mod_jsd, term_jsd, pfx_jsd)

for sec in sorted(section_folios):
    folios = sorted(section_folios[sec])
    if len(folios) < 2:
        continue

    pairs = []
    for f1, f2 in combinations(folios, 2):
        p1, p2 = folio_profiles[f1], folio_profiles[f2]

        head_jsd = jsd(
            get_distribution(p1, 'head', head_keys),
            get_distribution(p2, 'head', head_keys)
        )
        mod_jsd = jsd(
            get_distribution(p1, 'mod', mod_keys),
            get_distribution(p2, 'mod', mod_keys)
        )
        term_jsd = jsd(
            get_distribution(p1, 'term', term_keys),
            get_distribution(p2, 'term', term_keys)
        )
        pfx_jsd = jsd(
            get_distribution(p1, 'pfx', pfx_keys),
            get_distribution(p2, 'pfx', pfx_keys)
        )

        pairs.append({
            'f1': f1, 'f2': f2,
            'head_jsd': head_jsd, 'mod_jsd': mod_jsd,
            'term_jsd': term_jsd, 'pfx_jsd': pfx_jsd,
            'total_jsd': head_jsd + mod_jsd + term_jsd + pfx_jsd
        })

    jsd_results[sec] = sorted(pairs, key=lambda x: x['total_jsd'])

    print(f"\n  Section {SECTION_NAMES.get(sec, sec)} ({len(pairs)} pairs):")
    jsds_total = [p['total_jsd'] for p in pairs]
    print(f"    Total JSD: mean={np.mean(jsds_total):.4f}  std={np.std(jsds_total):.4f}  "
          f"min={np.min(jsds_total):.4f}  max={np.max(jsds_total):.4f}")

    # Which distribution type contributes most?
    mean_head = np.mean([p['head_jsd'] for p in pairs])
    mean_mod = np.mean([p['mod_jsd'] for p in pairs])
    mean_term = np.mean([p['term_jsd'] for p in pairs])
    mean_pfx = np.mean([p['pfx_jsd'] for p in pairs])
    total = mean_head + mean_mod + mean_term + mean_pfx
    print(f"    Contribution: HEAD={mean_head/total:.1%}  MOD={mean_mod/total:.1%}  "
          f"TERM={mean_term/total:.1%}  PFX={mean_pfx/total:.1%}")


# ============================================================
# 4. FEATURE IMPORTANCE RANKING
# ============================================================
print("\n" + "=" * 70)
print("4. FEATURE IMPORTANCE RANKING (between-folio / total variance)")
print("=" * 70)

# Compute across ALL sections: ratio of between-folio variance to total variance
all_b_folios = list(valid_folios)
feature_importance = {}

for feat in FEATURE_NAMES:
    all_vals = [folio_profiles[f][feat] for f in all_b_folios]
    total_var = np.var(all_vals)

    # Within-section variance (pooled)
    within_var_sum = 0
    n_total = 0
    for sec, folios in section_folios.items():
        if len(folios) < 2:
            continue
        sec_vals = [folio_profiles[f][feat] for f in folios]
        within_var_sum += np.var(sec_vals) * len(sec_vals)
        n_total += len(sec_vals)

    within_var = within_var_sum / max(n_total, 1)
    # Between = total - within (approximately)
    between_var = max(total_var - within_var, 0)

    # Importance = within-section variance / total (design freedom = what varies WITHIN section)
    importance = within_var / total_var if total_var > EPSILON else 0
    feature_importance[feat] = {
        'total_var': float(total_var),
        'within_var': float(within_var),
        'between_var': float(between_var),
        'within_fraction': float(importance)
    }

sorted_importance = sorted(feature_importance.items(), key=lambda x: -x[1]['within_fraction'])
print("\n  TOP 10 design freedom channels (high within-section variance):")
for feat, info in sorted_importance[:10]:
    print(f"    {feat:20s}  within_frac={info['within_fraction']:.3f}  "
          f"within_var={info['within_var']:.6f}  total_var={info['total_var']:.6f}")

print("\n  BOTTOM 10 constrained channels (low within-section variance):")
for feat, info in sorted_importance[-10:]:
    print(f"    {feat:20s}  within_frac={info['within_fraction']:.3f}  "
          f"within_var={info['within_var']:.6f}  total_var={info['total_var']:.6f}")


# ============================================================
# 5. SECTION COMPARISON
# ============================================================
print("\n" + "=" * 70)
print("5. SECTION COMPARISON: Do different sections use different freedom channels?")
print("=" * 70)

sections_with_data = [s for s in feature_cv_by_section if len(section_folios[s]) >= 5]
if len(sections_with_data) >= 2:
    for s1, s2 in combinations(sorted(sections_with_data), 2):
        # Rank features by CV in each section, compare rankings
        rank1 = sorted(feature_cv_by_section[s1].items(), key=lambda x: -x[1])
        rank2 = sorted(feature_cv_by_section[s2].items(), key=lambda x: -x[1])

        top5_s1 = {f for f, _ in rank1[:5]}
        top5_s2 = {f for f, _ in rank2[:5]}
        overlap = top5_s1 & top5_s2

        print(f"\n  {SECTION_NAMES.get(s1, s1)} vs {SECTION_NAMES.get(s2, s2)}:")
        print(f"    Top-5 overlap: {len(overlap)}/5 features")
        print(f"    {SECTION_NAMES.get(s1, s1)} top-5: {[f for f,_ in rank1[:5]]}")
        print(f"    {SECTION_NAMES.get(s2, s2)} top-5: {[f for f,_ in rank2[:5]]}")
        if overlap:
            print(f"    Shared: {sorted(overlap)}")

        # Spearman rank correlation on CV rankings
        feat_to_rank1 = {f: i for i, (f, _) in enumerate(rank1)}
        feat_to_rank2 = {f: i for i, (f, _) in enumerate(rank2)}
        common_feats = set(feat_to_rank1.keys()) & set(feat_to_rank2.keys())
        ranks1 = [feat_to_rank1[f] for f in common_feats]
        ranks2 = [feat_to_rank2[f] for f in common_feats]
        n_f = len(common_feats)
        d_sq = sum((r1 - r2) ** 2 for r1, r2 in zip(ranks1, ranks2))
        rho = 1 - 6 * d_sq / (n_f * (n_f ** 2 - 1)) if n_f > 1 else 0
        print(f"    CV rank correlation (Spearman rho): {rho:.3f}")
else:
    print("  Not enough sections with >= 5 folios for comparison.")


# ============================================================
# 6. SPECIFIC FOLIO PAIRS (largest section)
# ============================================================
print("\n" + "=" * 70)
print("6. SPECIFIC FOLIO PAIRS (most/least similar within largest section)")
print("=" * 70)

# Find largest section
largest_sec = max(section_folios, key=lambda s: len(section_folios[s]))
print(f"\n  Largest section: {SECTION_NAMES.get(largest_sec, largest_sec)} "
      f"({len(section_folios[largest_sec])} folios)")

if largest_sec in jsd_results and len(jsd_results[largest_sec]) >= 3:
    pairs = jsd_results[largest_sec]

    # 3 most similar
    print(f"\n  3 MOST SIMILAR pairs:")
    for pair in pairs[:3]:
        f1, f2 = pair['f1'], pair['f2']
        print(f"\n    {f1} vs {f2}  (total JSD={pair['total_jsd']:.4f})")
        print(f"      HEAD={pair['head_jsd']:.4f}  MOD={pair['mod_jsd']:.4f}  "
              f"TERM={pair['term_jsd']:.4f}  PFX={pair['pfx_jsd']:.4f}")

        # Find features with largest absolute difference
        diffs = []
        for feat in FEATURE_NAMES:
            d = abs(folio_profiles[f1][feat] - folio_profiles[f2][feat])
            diffs.append((feat, d, folio_profiles[f1][feat], folio_profiles[f2][feat]))
        diffs.sort(key=lambda x: -x[1])
        print(f"      Top differentiating features:")
        for feat, d, v1, v2 in diffs[:3]:
            print(f"        {feat}: {v1:.3f} vs {v2:.3f} (diff={d:.3f})")

    # 3 most different
    print(f"\n  3 MOST DIFFERENT pairs:")
    for pair in pairs[-3:]:
        f1, f2 = pair['f1'], pair['f2']
        print(f"\n    {f1} vs {f2}  (total JSD={pair['total_jsd']:.4f})")
        print(f"      HEAD={pair['head_jsd']:.4f}  MOD={pair['mod_jsd']:.4f}  "
              f"TERM={pair['term_jsd']:.4f}  PFX={pair['pfx_jsd']:.4f}")

        diffs = []
        for feat in FEATURE_NAMES:
            d = abs(folio_profiles[f1][feat] - folio_profiles[f2][feat])
            diffs.append((feat, d, folio_profiles[f1][feat], folio_profiles[f2][feat]))
        diffs.sort(key=lambda x: -x[1])
        print(f"      Top differentiating features:")
        for feat, d, v1, v2 in diffs[:5]:
            print(f"        {feat}: {v1:.3f} vs {v2:.3f} (diff={d:.3f})")

    # Sample unique tokens from the most different pair
    print(f"\n  UNIQUE TOKEN SAMPLES from most different pair:")
    most_diff = pairs[-1]
    f1, f2 = most_diff['f1'], most_diff['f2']
    words_f1 = Counter(t.word for t in folio_tokens[f1])
    words_f2 = Counter(t.word for t in folio_tokens[f2])
    unique_to_f1 = set(words_f1.keys()) - set(words_f2.keys())
    unique_to_f2 = set(words_f2.keys()) - set(words_f1.keys())

    # Pick top-5 by frequency from each
    top_f1 = sorted(unique_to_f1, key=lambda w: -words_f1[w])[:5]
    top_f2 = sorted(unique_to_f2, key=lambda w: -words_f2[w])[:5]

    print(f"\n    Tokens unique to {f1}:")
    for w in top_f1:
        a = morph.atomize(w)
        atoms_str = ' '.join(f'{c}({r[0]})' for c, r, _ in a.atoms)
        print(f"      {w:15s}  pfx={a.prefix or '-':4s}  atoms=[{atoms_str}]  "
              f"e_depth={a.e_depth}  headless={a.is_headless}")

    print(f"\n    Tokens unique to {f2}:")
    for w in top_f2:
        a = morph.atomize(w)
        atoms_str = ' '.join(f'{c}({r[0]})' for c, r, _ in a.atoms)
        print(f"      {w:15s}  pfx={a.prefix or '-':4s}  atoms=[{atoms_str}]  "
              f"e_depth={a.e_depth}  headless={a.is_headless}")


# ============================================================
# 7. CONNECTION TO OPERATIONAL PROFILES
# ============================================================
print("\n" + "=" * 70)
print("7. CONNECTION TO OPERATIONAL PROFILES")
print("=" * 70)

ops_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'results',
                        'folio_operational_profiles_v3.json')
try:
    with open(ops_path, 'r') as f:
        ops_data = json.load(f)

    ops_by_folio = {p['folio']: p for p in ops_data['profiles']}
    ops_features = ['k_ratio', 'h_ratio', 'e_ratio', 'iteration_rate',
                    'checkpoint_rate', 'terminal_rate']

    # For each atom feature, correlate with each operational feature across valid folios
    common_folios = [f for f in valid_folios if f in ops_by_folio]
    print(f"\n  Folios with both atom profiles and operational profiles: {len(common_folios)}")

    # Spearman correlation
    def spearman(x, y):
        n = len(x)
        if n < 3:
            return 0.0
        rx = np.argsort(np.argsort(x)).astype(float)
        ry = np.argsort(np.argsort(y)).astype(float)
        d = rx - ry
        return 1 - 6 * np.sum(d**2) / (n * (n**2 - 1))

    print(f"\n  Top atom-operational correlations (|rho| > 0.3):")
    strong_correlations = []
    for atom_feat in FEATURE_NAMES:
        atom_vals = np.array([folio_profiles[f][atom_feat] for f in common_folios])
        for ops_feat in ops_features:
            ops_vals = np.array([ops_by_folio[f][ops_feat] for f in common_folios])
            rho = spearman(atom_vals, ops_vals)
            if abs(rho) > 0.3:
                strong_correlations.append((atom_feat, ops_feat, rho))

    strong_correlations.sort(key=lambda x: -abs(x[2]))
    for atom_f, ops_f, rho in strong_correlations[:20]:
        print(f"    {atom_f:20s} x {ops_f:20s}  rho={rho:+.3f}")

    if not strong_correlations:
        print("    (no correlations with |rho| > 0.3)")

    # Does within-section atom variance predict within-section operational variance?
    print(f"\n  Within-section variance correlation (atom vs operational):")
    for sec in sorted(section_folios):
        folios = [f for f in section_folios[sec] if f in ops_by_folio]
        if len(folios) < 5:
            continue

        # Atom variance vector (across features)
        atom_vars = []
        for feat in FEATURE_NAMES:
            vals = [folio_profiles[f][feat] for f in folios]
            atom_vars.append(np.var(vals))

        # Operational variance vector
        ops_vars = []
        for feat in ops_features:
            vals = [ops_by_folio[f][feat] for f in folios]
            ops_vars.append(np.var(vals))

        # For each folio, compute its "atom deviation" (mean abs diff from section mean)
        # and "ops deviation" — then correlate
        atom_means = {feat: np.mean([folio_profiles[f][feat] for f in folios])
                      for feat in FEATURE_NAMES}
        ops_means = {feat: np.mean([ops_by_folio[f][feat] for f in folios])
                     for feat in ops_features}

        atom_devs = []
        ops_devs = []
        for f in folios:
            ad = np.mean([abs(folio_profiles[f][feat] - atom_means[feat])
                          for feat in FEATURE_NAMES])
            od = np.mean([abs(ops_by_folio[f][feat] - ops_means[feat])
                          for feat in ops_features])
            atom_devs.append(ad)
            ops_devs.append(od)

        rho = spearman(np.array(atom_devs), np.array(ops_devs))
        print(f"    {SECTION_NAMES.get(sec, sec):10s}: atom_dev vs ops_dev rho={rho:+.3f} "
              f"(n={len(folios)})")

except FileNotFoundError:
    print("  Operational profiles not found — skipping section 7.")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Compute overall stats
all_within_fracs = [feature_importance[f]['within_fraction'] for f in FEATURE_NAMES]
print(f"\n  Total features analyzed: {len(FEATURE_NAMES)}")
print(f"  Mean within-section variance fraction: {np.mean(all_within_fracs):.3f}")
print(f"  Features with >70% within-section variance: "
      f"{sum(1 for x in all_within_fracs if x > 0.7)}/{len(FEATURE_NAMES)}")
print(f"  Features with <30% within-section variance: "
      f"{sum(1 for x in all_within_fracs if x < 0.3)}/{len(FEATURE_NAMES)}")

# Overall JSD range
all_jsds = []
for pairs in jsd_results.values():
    all_jsds.extend(p['total_jsd'] for p in pairs)
if all_jsds:
    print(f"\n  Within-section JSD range: [{min(all_jsds):.4f}, {max(all_jsds):.4f}]")
    print(f"  Mean within-section JSD: {np.mean(all_jsds):.4f}")
    # Folios ARE differentiable if JSD > 0
    print(f"  Signal exists: {'YES' if np.mean(all_jsds) > 0.01 else 'WEAK'} "
          f"(mean JSD={'>>0' if np.mean(all_jsds) > 0.01 else '~0'})")


# ============================================================
# SAVE JSON
# ============================================================
output = {
    'test': 's7_regime_folio_differentiation_probe',
    'question': 'Can atom-level features differentiate B folios within same section?',
    'n_folios': len(valid_folios),
    'min_tokens': MIN_TOKENS,
    'features_analyzed': len(FEATURE_NAMES),
    'feature_names': FEATURE_NAMES,
    'folio_profiles': {f: {k: round(v, 6) if isinstance(v, float) else v
                           for k, v in p.items()}
                       for f, p in folio_profiles.items()},
    'feature_importance': {f: {k: round(v, 6) for k, v in info.items()}
                           for f, info in feature_importance.items()},
    'top5_design_freedom': [f for f, _ in sorted_importance[:5]],
    'top5_constrained': [f for f, _ in sorted_importance[-5:]],
    'jsd_summary': {},
    'section_cv_rankings': {},
}

for sec, pairs in jsd_results.items():
    jsds = [p['total_jsd'] for p in pairs]
    output['jsd_summary'][sec] = {
        'n_pairs': len(pairs),
        'mean_jsd': round(float(np.mean(jsds)), 6),
        'std_jsd': round(float(np.std(jsds)), 6),
        'min_pair': {'f1': pairs[0]['f1'], 'f2': pairs[0]['f2'],
                     'jsd': round(pairs[0]['total_jsd'], 6)} if pairs else None,
        'max_pair': {'f1': pairs[-1]['f1'], 'f2': pairs[-1]['f2'],
                     'jsd': round(pairs[-1]['total_jsd'], 6)} if pairs else None,
    }

for sec, cv_dict in feature_cv_by_section.items():
    sorted_cv = sorted(cv_dict.items(), key=lambda x: -x[1])
    output['section_cv_rankings'][sec] = {
        'top5': [(f, round(v, 4)) for f, v in sorted_cv[:5]],
        'bottom5': [(f, round(v, 4)) for f, v in sorted_cv[-5:]],
    }

results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(results_dir, exist_ok=True)
out_path = os.path.join(results_dir, 's7_regime_folio_differentiation_probe.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\n  Results saved to: {out_path}")
print("\nDone.")
