"""
RI_BINDING_ANALYSIS Phase - Discriminating Tests for RI Function

Tests whether RI tokens have semantic binding to co-occurring PP,
or whether RI is an independent label with no relationship to
the PP on the same line.

Expert-recommended tests:
  T1: Cross-Folio RI Reuse PP Similarity (Model A vs B)
      For non-singleton RI MIDDLEs appearing on 2+ folios,
      does the same RI co-occur with similar PP MIDDLEs?
  T2: Section-Specificity of RI Sharing
      Are shared RI MIDDLEs reused within-section or cross-section?
  T3: RI PREFIX Bifurcation x PP Profile (C528)
      Do PREFIX-REQUIRED and PREFIX-FORBIDDEN RI tokens
      co-occur with different PP profiles?
  T4: Gallows Domain Coherence for Shared RI (C530)
      For non-singleton RI, does gallows-domain consistency
      predict which folios share RI?
  T5: Within-Line RI-PP Co-occurrence Specificity
      When the same RI MIDDLE appears on multiple lines,
      does it co-occur with consistent PP MIDDLEs?
  T6: RI-Adjacent PP Token Analysis
      Are the PP tokens immediately adjacent to RI tokens
      more consistent than random PP from the same line?

Gate: 4/6 pass -> RI has semantic binding (Model B)
      2/6 or fewer -> RI is independent label (Model A)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats as scipy_stats
from itertools import combinations

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology, RecordAnalyzer

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'

print("=" * 70)
print("RI_BINDING_ANALYSIS - Discriminating Tests for RI Function")
print("=" * 70)

# -- Load data --
tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

folios = analyzer.get_folios()
print(f"A folios: {len(folios)}")

# -- Pre-compute all records --
folio_records = {}
all_records = []
for fol in folios:
    records = analyzer.analyze_folio(fol)
    folio_records[fol] = records
    all_records.extend(records)

print(f"Total A records: {len(all_records)}")

# -- Load middle_classes.json for RI/PP classification --
mid_classes_path = PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json'
with open(mid_classes_path, 'r') as f:
    mid_classes = json.load(f)

ri_middles_set = set(mid_classes['a_exclusive_middles'])
pp_middles_list = mid_classes.get('a_shared_middles', [])
pp_middles_set = set(pp_middles_list) if pp_middles_list else set()

# If a_shared_middles not directly available, derive from tokens
if not pp_middles_set:
    # PP = shared middles (appear in both A and B)
    a_middles = set()
    b_middles = set()
    for token in tx.currier_a():
        m = morph.extract(token.word)
        if m.middle:
            a_middles.add(m.middle)
    for token in tx.currier_b():
        m = morph.extract(token.word)
        if m.middle:
            b_middles.add(m.middle)
    pp_middles_set = a_middles & b_middles

print(f"RI MIDDLE types: {len(ri_middles_set)}")
print(f"PP MIDDLE types: {len(pp_middles_set)}")

# -- Pre-compute per-record data in single pass --
# For each record: folio, line, RI middles, PP middles, all tokens with positions
record_data = []
for fol in folios:
    for rec in folio_records[fol]:
        ri_mids = []
        pp_mids = []
        token_sequence = []  # (word, middle, is_ri, is_pp, prefix, suffix)
        for t in rec.tokens:
            is_ri = t.is_ri if hasattr(t, 'is_ri') else (t.middle in ri_middles_set if t.middle else False)
            is_pp = t.is_pp if hasattr(t, 'is_pp') else (t.middle in pp_middles_set if t.middle else False)
            if is_ri and t.middle:
                ri_mids.append(t.middle)
            if is_pp and t.middle:
                pp_mids.append(t.middle)
            m = morph.extract(t.word) if t.word else None
            token_sequence.append({
                'word': t.word,
                'middle': t.middle,
                'is_ri': is_ri,
                'is_pp': is_pp,
                'prefix': m.prefix if m else None,
                'suffix': m.suffix if m else None,
            })
        record_data.append({
            'folio': fol,
            'ri_middles': ri_mids,
            'pp_middles': pp_mids,
            'ri_middles_set': set(ri_mids),
            'pp_middles_set': set(pp_mids),
            'tokens': token_sequence,
            'n_tokens': len(token_sequence),
        })

# -- Pre-compute RI MIDDLE -> list of records --
ri_mid_to_records = defaultdict(list)
for i, rd in enumerate(record_data):
    for rm in rd['ri_middles_set']:
        ri_mid_to_records[rm].append(i)

# Non-singleton RI MIDDLEs (appear on 2+ records)
non_singleton_ri = {rm: idxs for rm, idxs in ri_mid_to_records.items() if len(idxs) >= 2}
print(f"Non-singleton RI MIDDLEs: {len(non_singleton_ri)} (appear on 2+ records)")

# -- Pre-compute folio sections --
# Get section from transcript
folio_section = {}
for token in tx.currier_a():
    fol = token.folio
    if fol not in folio_section:
        folio_section[fol] = token.section if hasattr(token, 'section') else None

# If section not available from token, try to get from quire/section mapping
if all(v is None for v in folio_section.values()):
    # Fallback: use the transcript's section info
    import pandas as pd
    df = tx._df  # Access underlying dataframe
    df_h = df[df['transcriber'] == 'H']
    for fol in folios:
        fol_df = df_h[df_h['folio'] == fol]
        if len(fol_df) > 0 and 'section' in fol_df.columns:
            folio_section[fol] = fol_df.iloc[0]['section']

print(f"Sections mapped: {len([v for v in folio_section.values() if v is not None])}/{len(folios)}")
section_counts = Counter(folio_section.values())
print(f"Section distribution: {dict(section_counts)}")

# -- Pre-compute gallows extraction per MIDDLE --
def get_gallows(middle):
    """Extract gallows letter(s) from a MIDDLE string."""
    gallows = []
    for ch in ['k', 't', 'p', 'f']:
        if ch in middle:
            gallows.append(ch)
    return gallows

results = {
    'metadata': {
        'phase': 'RI_BINDING_ANALYSIS',
        'script': 'ri_binding_tests.py',
        'n_folios': len(folios),
        'n_records': len(all_records),
        'non_singleton_ri': len(non_singleton_ri),
    },
}

pass_count = 0

# ============================================================
# T1: Cross-Folio RI Reuse PP Similarity
# ============================================================
print()
print("-" * 60)
print("T1: Cross-Folio RI Reuse PP Similarity")
print("-" * 60)

# For each non-singleton RI MIDDLE: collect PP MIDDLE sets from each record
# Compare within-RI-group PP Jaccard vs random baseline

# RI that appears on 2+ different folios
cross_folio_ri = {}
for rm, idxs in non_singleton_ri.items():
    folio_set = set(record_data[i]['folio'] for i in idxs)
    if len(folio_set) >= 2:
        cross_folio_ri[rm] = idxs

print(f"  RI MIDDLEs on 2+ folios: {len(cross_folio_ri)}")

if len(cross_folio_ri) >= 5:
    # Within-group: Jaccard of PP sets between records sharing same RI
    within_jaccards = []
    for rm, idxs in cross_folio_ri.items():
        pp_sets = [record_data[i]['pp_middles_set'] for i in idxs]
        for a, b in combinations(range(len(pp_sets)), 2):
            if pp_sets[a] or pp_sets[b]:
                union = pp_sets[a] | pp_sets[b]
                inter = pp_sets[a] & pp_sets[b]
                if union:
                    within_jaccards.append(len(inter) / len(union))

    # Between-group baseline: random pairs of RI-bearing records from different folios
    np.random.seed(42)
    ri_bearing_indices = [i for i, rd in enumerate(record_data) if rd['ri_middles']]
    between_jaccards = []
    n_samples = min(len(within_jaccards) * 3, 5000)
    for _ in range(n_samples):
        a, b = np.random.choice(ri_bearing_indices, 2, replace=False)
        if record_data[a]['folio'] != record_data[b]['folio']:
            pa = record_data[a]['pp_middles_set']
            pb = record_data[b]['pp_middles_set']
            union = pa | pb
            if union:
                between_jaccards.append(len(pa & pb) / len(union))

    within_mean = float(np.mean(within_jaccards)) if within_jaccards else 0
    between_mean = float(np.mean(between_jaccards)) if between_jaccards else 0

    if within_jaccards and between_jaccards:
        u1, p1 = scipy_stats.mannwhitneyu(within_jaccards, between_jaccards, alternative='greater')
    else:
        u1, p1 = 0, 1.0

    ratio_t1 = within_mean / between_mean if between_mean > 0 else float('inf')
    t1_pass = ratio_t1 > 1.3 and p1 < 0.01

    print(f"  Within-RI-group PP Jaccard:  mean={within_mean:.4f} (n={len(within_jaccards)})")
    print(f"  Between-group PP Jaccard:    mean={between_mean:.4f} (n={len(between_jaccards)})")
    print(f"  Ratio: {ratio_t1:.3f}")
    print(f"  Mann-Whitney p={p1:.4e}")
    print(f"  T1 {'PASS' if t1_pass else 'FAIL'}: {'Records sharing RI have more similar PP' if t1_pass else 'No PP similarity enrichment for shared RI'}")
else:
    t1_pass = False
    within_mean = 0
    between_mean = 0
    ratio_t1 = 0
    p1 = 1.0
    print(f"  Insufficient cross-folio RI (need 5+, got {len(cross_folio_ri)})")

if t1_pass:
    pass_count += 1

results['T1_cross_folio_pp_similarity'] = {
    'cross_folio_ri_count': len(cross_folio_ri),
    'within_group_jaccard': round(within_mean, 4),
    'between_group_jaccard': round(between_mean, 4),
    'ratio': round(ratio_t1, 3),
    'mann_whitney_p': float(p1),
    'pass': t1_pass,
}

# ============================================================
# T2: Section-Specificity of RI Sharing
# ============================================================
print()
print("-" * 60)
print("T2: Section-Specificity of RI Sharing")
print("-" * 60)

# For non-singleton RI appearing on 2+ folios: are they shared
# within-section or cross-section?
within_section_sharing = 0
cross_section_sharing = 0
total_sharing_pairs = 0

for rm, idxs in non_singleton_ri.items():
    folio_set = list(set(record_data[i]['folio'] for i in idxs))
    if len(folio_set) < 2:
        continue
    sections = [folio_section.get(f) for f in folio_set]
    for a, b in combinations(range(len(folio_set)), 2):
        total_sharing_pairs += 1
        if sections[a] is not None and sections[b] is not None:
            if sections[a] == sections[b]:
                within_section_sharing += 1
            else:
                cross_section_sharing += 1

# Expected within-section sharing under null (proportional to section sizes)
section_folio_counts = Counter()
for fol in folios:
    s = folio_section.get(fol)
    if s:
        section_folio_counts[s] += 1

total_folios_with_section = sum(section_folio_counts.values())
expected_within = sum(
    (c / total_folios_with_section) ** 2
    for c in section_folio_counts.values()
) if total_folios_with_section > 0 else 0

classified_pairs = within_section_sharing + cross_section_sharing
observed_within_frac = within_section_sharing / classified_pairs if classified_pairs > 0 else 0

print(f"  Total RI sharing folio pairs: {total_sharing_pairs}")
print(f"  Within-section: {within_section_sharing}")
print(f"  Cross-section:  {cross_section_sharing}")
print(f"  Within-section fraction: {observed_within_frac:.4f}")
print(f"  Expected (null): {expected_within:.4f}")

# Binomial test
if classified_pairs > 0:
    binom_result = scipy_stats.binomtest(within_section_sharing, classified_pairs, expected_within, alternative='greater')
    binom_p = binom_result.pvalue
else:
    binom_p = 1.0

ratio_t2 = observed_within_frac / expected_within if expected_within > 0 else 0
t2_pass = ratio_t2 > 1.3 and binom_p < 0.01

print(f"  Enrichment ratio: {ratio_t2:.3f}")
print(f"  Binomial p={binom_p:.4e}")
print(f"  T2 {'PASS' if t2_pass else 'FAIL'}: {'RI sharing is section-specific' if t2_pass else 'RI sharing is NOT section-specific'}")

if t2_pass:
    pass_count += 1

results['T2_section_specificity'] = {
    'within_section': within_section_sharing,
    'cross_section': cross_section_sharing,
    'total_pairs': classified_pairs,
    'within_section_frac': round(observed_within_frac, 4),
    'expected_within_frac': round(expected_within, 4),
    'enrichment_ratio': round(ratio_t2, 3),
    'binom_p': float(binom_p),
    'pass': t2_pass,
}

# ============================================================
# T3: RI PREFIX Bifurcation x PP Profile (C528)
# ============================================================
print()
print("-" * 60)
print("T3: RI PREFIX Bifurcation x PP Profile (C528)")
print("-" * 60)

# Classify each RI MIDDLE as PREFIX-REQUIRED vs PREFIX-FORBIDDEN
# based on whether it ever appears with a prefix
ri_mid_prefix_counts = defaultdict(lambda: {'with': 0, 'without': 0})

for rd in record_data:
    for tok in rd['tokens']:
        if tok['is_ri'] and tok['middle']:
            if tok['prefix']:
                ri_mid_prefix_counts[tok['middle']]['with'] += 1
            else:
                ri_mid_prefix_counts[tok['middle']]['without'] += 1

prefix_required = set()
prefix_forbidden = set()
for mid, counts in ri_mid_prefix_counts.items():
    if counts['with'] > 0 and counts['without'] == 0:
        prefix_required.add(mid)
    elif counts['without'] > 0 and counts['with'] == 0:
        prefix_forbidden.add(mid)

print(f"  PREFIX-REQUIRED RI MIDDLEs: {len(prefix_required)}")
print(f"  PREFIX-FORBIDDEN RI MIDDLEs: {len(prefix_forbidden)}")

# For each group: collect co-occurring PP MIDDLEs
pp_with_prefix_req = Counter()
pp_with_prefix_forb = Counter()
n_lines_prefix_req = 0
n_lines_prefix_forb = 0

for rd in record_data:
    has_req = any(rm in prefix_required for rm in rd['ri_middles'])
    has_forb = any(rm in prefix_forbidden for rm in rd['ri_middles'])

    if has_req:
        n_lines_prefix_req += 1
        for pm in rd['pp_middles']:
            pp_with_prefix_req[pm] += 1
    if has_forb:
        n_lines_prefix_forb += 1
        for pm in rd['pp_middles']:
            pp_with_prefix_forb[pm] += 1

# Jaccard between the PP profiles of the two RI groups
req_pp_set = set(pp_with_prefix_req.keys())
forb_pp_set = set(pp_with_prefix_forb.keys())
pp_union = req_pp_set | forb_pp_set
pp_inter = req_pp_set & forb_pp_set
pp_jaccard = len(pp_inter) / len(pp_union) if pp_union else 0

print(f"  Lines with PREFIX-REQUIRED RI: {n_lines_prefix_req}")
print(f"  Lines with PREFIX-FORBIDDEN RI: {n_lines_prefix_forb}")
print(f"  PP MIDDLE types co-occurring with PREFIX-REQ: {len(req_pp_set)}")
print(f"  PP MIDDLE types co-occurring with PREFIX-FORB: {len(forb_pp_set)}")
print(f"  PP Jaccard between groups: {pp_jaccard:.4f}")

# Frequency-weighted comparison: for shared PP MIDDLEs, do they show bias?
# Normalize by line count
if n_lines_prefix_req > 0 and n_lines_prefix_forb > 0:
    shared_pp = req_pp_set & forb_pp_set
    biases = []
    for pm in shared_pp:
        rate_req = pp_with_prefix_req[pm] / n_lines_prefix_req
        rate_forb = pp_with_prefix_forb[pm] / n_lines_prefix_forb
        total_rate = rate_req + rate_forb
        if total_rate > 0:
            biases.append(rate_req / total_rate)

    bias_mean = float(np.mean(biases)) if biases else 0.5
    # Expected: 0.5 if no difference
    bias_deviation = abs(bias_mean - 0.5)

    # Chi-squared: top-30 PP MIDDLEs
    top_pp = sorted(shared_pp, key=lambda m: pp_with_prefix_req.get(m, 0) + pp_with_prefix_forb.get(m, 0), reverse=True)[:30]
    if top_pp:
        obs_req = np.array([pp_with_prefix_req[m] for m in top_pp], dtype=float)
        obs_forb = np.array([pp_with_prefix_forb[m] for m in top_pp], dtype=float)
        totals = obs_req + obs_forb
        expected_req = totals * (n_lines_prefix_req / (n_lines_prefix_req + n_lines_prefix_forb))
        expected_forb = totals * (n_lines_prefix_forb / (n_lines_prefix_req + n_lines_prefix_forb))

        chi2 = float(np.sum((obs_req - expected_req)**2 / np.where(expected_req > 0, expected_req, 1) +
                            (obs_forb - expected_forb)**2 / np.where(expected_forb > 0, expected_forb, 1)))
        chi2_df = len(top_pp) - 1
        chi2_p = float(scipy_stats.chi2.sf(chi2, chi2_df))
    else:
        chi2, chi2_df, chi2_p = 0, 0, 1.0
else:
    bias_mean = 0.5
    bias_deviation = 0
    chi2, chi2_df, chi2_p = 0, 0, 1.0

# PASS if PP profiles differ: low Jaccard OR significant chi-squared
t3_pass = pp_jaccard < 0.5 or chi2_p < 0.01

print(f"  Shared PP bias toward PREFIX-REQ: {bias_mean:.4f} (0.5=neutral)")
print(f"  Chi-squared (top-30 PP): chi2={chi2:.2f}, df={chi2_df}, p={chi2_p:.4e}")
print(f"  T3 {'PASS' if t3_pass else 'FAIL'}: {'PREFIX bifurcation associates with different PP profiles' if t3_pass else 'PREFIX bifurcation does NOT differentiate PP profiles'}")

if t3_pass:
    pass_count += 1

results['T3_prefix_bifurcation_pp'] = {
    'prefix_required_count': len(prefix_required),
    'prefix_forbidden_count': len(prefix_forbidden),
    'lines_prefix_req': n_lines_prefix_req,
    'lines_prefix_forb': n_lines_prefix_forb,
    'pp_jaccard': round(pp_jaccard, 4),
    'bias_mean': round(bias_mean, 4),
    'chi2': round(chi2, 2),
    'chi2_df': chi2_df,
    'chi2_p': float(chi2_p),
    'pass': t3_pass,
}

# ============================================================
# T4: Gallows Domain Coherence for Shared RI (C530)
# ============================================================
print()
print("-" * 60)
print("T4: Gallows Domain Coherence for Shared RI (C530)")
print("-" * 60)

# For non-singleton RI MIDDLEs: when the same RI appears on multiple records,
# do those records share a gallows domain in their PP?

# Per record: dominant gallows in PP
def get_record_gallows_profile(rd):
    """Get gallows frequency in PP tokens for a record."""
    gallows_counts = Counter()
    for tok in rd['tokens']:
        if tok['is_pp'] and tok['middle']:
            for g in get_gallows(tok['middle']):
                gallows_counts[g] += 1
    return gallows_counts

# Pre-compute gallows profiles
record_gallows = [get_record_gallows_profile(rd) for rd in record_data]

# For non-singleton RI: compute gallows similarity between records sharing RI
within_gallows_sim = []
between_gallows_sim = []

def gallows_cosine(g1, g2):
    """Cosine similarity between two gallows Counter profiles."""
    all_g = set(g1.keys()) | set(g2.keys())
    if not all_g:
        return 0.0
    v1 = np.array([g1.get(g, 0) for g in sorted(all_g)], dtype=float)
    v2 = np.array([g2.get(g, 0) for g in sorted(all_g)], dtype=float)
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (n1 * n2))

for rm, idxs in non_singleton_ri.items():
    if len(idxs) < 2:
        continue
    for a, b in combinations(idxs, 2):
        sim = gallows_cosine(record_gallows[a], record_gallows[b])
        within_gallows_sim.append(sim)

# Baseline: random RI-bearing record pairs
np.random.seed(43)
ri_indices = [i for i, rd in enumerate(record_data) if rd['ri_middles']]
for _ in range(min(len(within_gallows_sim) * 3, 5000)):
    a, b = np.random.choice(ri_indices, 2, replace=False)
    sim = gallows_cosine(record_gallows[a], record_gallows[b])
    between_gallows_sim.append(sim)

within_g_mean = float(np.mean(within_gallows_sim)) if within_gallows_sim else 0
between_g_mean = float(np.mean(between_gallows_sim)) if between_gallows_sim else 0

if within_gallows_sim and between_gallows_sim:
    u4, p4 = scipy_stats.mannwhitneyu(within_gallows_sim, between_gallows_sim, alternative='greater')
else:
    u4, p4 = 0, 1.0

ratio_t4 = within_g_mean / between_g_mean if between_g_mean > 0 else 0
t4_pass = ratio_t4 > 1.1 and p4 < 0.01

print(f"  Within-RI-group gallows cosine: mean={within_g_mean:.4f} (n={len(within_gallows_sim)})")
print(f"  Between-group gallows cosine:   mean={between_g_mean:.4f} (n={len(between_gallows_sim)})")
print(f"  Ratio: {ratio_t4:.3f}")
print(f"  Mann-Whitney p={p4:.4e}")
print(f"  T4 {'PASS' if t4_pass else 'FAIL'}: {'Shared RI predicts gallows domain' if t4_pass else 'Shared RI does NOT predict gallows domain'}")

if t4_pass:
    pass_count += 1

results['T4_gallows_domain'] = {
    'within_group_cosine': round(within_g_mean, 4),
    'between_group_cosine': round(between_g_mean, 4),
    'ratio': round(ratio_t4, 3),
    'mann_whitney_p': float(p4),
    'pass': t4_pass,
}

# ============================================================
# T5: Within-Line RI-PP Co-occurrence Consistency
# ============================================================
print()
print("-" * 60)
print("T5: Within-Line RI-PP Co-occurrence Consistency")
print("-" * 60)

# For each non-singleton RI MIDDLE: across its appearances,
# how consistent is the PP MIDDLE set?
# Measure: mean pairwise Jaccard of PP sets across records with same RI

ri_consistency_scores = []
null_consistency_scores = []

np.random.seed(44)

for rm, idxs in non_singleton_ri.items():
    if len(idxs) < 2:
        continue
    pp_sets = [record_data[i]['pp_middles_set'] for i in idxs]
    # Within-RI consistency
    jaccards = []
    for a, b in combinations(range(len(pp_sets)), 2):
        union = pp_sets[a] | pp_sets[b]
        if union:
            jaccards.append(len(pp_sets[a] & pp_sets[b]) / len(union))
    if jaccards:
        ri_consistency_scores.append(float(np.mean(jaccards)))

    # Null: same number of random RI-bearing records
    null_jacs = []
    for _ in range(100):
        sample = np.random.choice(ri_indices, len(idxs), replace=False)
        sample_pp = [record_data[s]['pp_middles_set'] for s in sample]
        sj = []
        for a, b in combinations(range(len(sample_pp)), 2):
            union = sample_pp[a] | sample_pp[b]
            if union:
                sj.append(len(sample_pp[a] & sample_pp[b]) / len(union))
        if sj:
            null_jacs.append(float(np.mean(sj)))
    if null_jacs:
        null_consistency_scores.append(float(np.mean(null_jacs)))

obs_consistency = float(np.mean(ri_consistency_scores)) if ri_consistency_scores else 0
null_consistency = float(np.mean(null_consistency_scores)) if null_consistency_scores else 0

if ri_consistency_scores and null_consistency_scores:
    # Paired comparison
    min_len = min(len(ri_consistency_scores), len(null_consistency_scores))
    t5_stat, t5_p = scipy_stats.ttest_rel(
        ri_consistency_scores[:min_len],
        null_consistency_scores[:min_len],
        alternative='greater'
    )
else:
    t5_stat, t5_p = 0, 1.0

ratio_t5 = obs_consistency / null_consistency if null_consistency > 0 else 0
t5_pass = ratio_t5 > 1.3 and t5_p < 0.01

print(f"  Observed PP consistency for shared RI: mean={obs_consistency:.4f} (n={len(ri_consistency_scores)})")
print(f"  Null PP consistency (random groups):   mean={null_consistency:.4f}")
print(f"  Ratio: {ratio_t5:.3f}")
print(f"  Paired t-test p={t5_p:.4e}")
print(f"  T5 {'PASS' if t5_pass else 'FAIL'}: {'Same RI -> consistent PP co-occurrence' if t5_pass else 'Same RI does NOT predict PP co-occurrence'}")

if t5_pass:
    pass_count += 1

results['T5_pp_consistency'] = {
    'observed_consistency': round(obs_consistency, 4),
    'null_consistency': round(null_consistency, 4),
    'ratio': round(ratio_t5, 3),
    'paired_t_p': float(t5_p),
    'n_ri_middles_tested': len(ri_consistency_scores),
    'pass': t5_pass,
}

# ============================================================
# T6: RI-Adjacent PP Token Analysis
# ============================================================
print()
print("-" * 60)
print("T6: RI-Adjacent PP Token Analysis")
print("-" * 60)

# For each RI token in a record: what PP MIDDLE is immediately
# before and after it? Is this more consistent than random PP position?

# For non-singleton RI: collect adjacent PP across all occurrences
ri_adjacent_pp = defaultdict(list)  # ri_middle -> list of (prev_pp, next_pp)

for rd in record_data:
    tokens = rd['tokens']
    for i, tok in enumerate(tokens):
        if tok['is_ri'] and tok['middle']:
            prev_pp = None
            next_pp = None
            # Look backward for nearest PP
            for j in range(i - 1, -1, -1):
                if tokens[j]['is_pp'] and tokens[j]['middle']:
                    prev_pp = tokens[j]['middle']
                    break
            # Look forward for nearest PP
            for j in range(i + 1, len(tokens)):
                if tokens[j]['is_pp'] and tokens[j]['middle']:
                    next_pp = tokens[j]['middle']
                    break
            ri_adjacent_pp[tok['middle']].append((prev_pp, next_pp))

# For non-singleton RI: measure consistency of adjacent PP
adjacent_consistency = []
null_adjacent_consistency = []

# Build pool of all adjacent PP for null model
all_prev_pp = [prev for pairs in ri_adjacent_pp.values() for prev, _ in pairs if prev]
all_next_pp = [nxt for pairs in ri_adjacent_pp.values() for _, nxt in pairs if nxt]

np.random.seed(45)

for rm in non_singleton_ri:
    pairs = ri_adjacent_pp.get(rm, [])
    if len(pairs) < 2:
        continue

    # Observed: fraction of occurrences sharing same prev_pp or next_pp
    prev_set = [p for p, _ in pairs if p]
    next_set = [n for _, n in pairs if n]

    if len(prev_set) >= 2:
        prev_counter = Counter(prev_set)
        most_common_frac = prev_counter.most_common(1)[0][1] / len(prev_set)
        adjacent_consistency.append(most_common_frac)

        # Null: random sample of same size from all prev_pp
        null_fracs = []
        for _ in range(200):
            sample = np.random.choice(all_prev_pp, len(prev_set), replace=True)
            sc = Counter(sample)
            null_fracs.append(sc.most_common(1)[0][1] / len(sample))
        null_adjacent_consistency.append(float(np.mean(null_fracs)))

obs_adj = float(np.mean(adjacent_consistency)) if adjacent_consistency else 0
null_adj = float(np.mean(null_adjacent_consistency)) if null_adjacent_consistency else 0

if adjacent_consistency and null_adjacent_consistency:
    min_len = min(len(adjacent_consistency), len(null_adjacent_consistency))
    t6_stat, t6_p = scipy_stats.ttest_rel(
        adjacent_consistency[:min_len],
        null_adjacent_consistency[:min_len],
        alternative='greater'
    )
else:
    t6_stat, t6_p = 0, 1.0

ratio_t6 = obs_adj / null_adj if null_adj > 0 else 0
t6_pass = ratio_t6 > 1.3 and t6_p < 0.01

print(f"  Adjacent PP consistency for shared RI: mean={obs_adj:.4f} (n={len(adjacent_consistency)})")
print(f"  Null (random adjacent PP):             mean={null_adj:.4f}")
print(f"  Ratio: {ratio_t6:.3f}")
print(f"  Paired t-test p={t6_p:.4e}")
print(f"  T6 {'PASS' if t6_pass else 'FAIL'}: {'RI predicts adjacent PP' if t6_pass else 'RI does NOT predict adjacent PP'}")

if t6_pass:
    pass_count += 1

results['T6_adjacent_pp'] = {
    'observed_consistency': round(obs_adj, 4),
    'null_consistency': round(null_adj, 4),
    'ratio': round(ratio_t6, 3),
    'paired_t_p': float(t6_p),
    'n_ri_tested': len(adjacent_consistency),
    'pass': t6_pass,
}

# ============================================================
# Summary
# ============================================================
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\n  Tests passed: {pass_count}/6")
print()
test_names = [
    ('T1', 'Cross-folio RI reuse PP similarity', results['T1_cross_folio_pp_similarity']['pass']),
    ('T2', 'Section-specificity of RI sharing', results['T2_section_specificity']['pass']),
    ('T3', 'PREFIX bifurcation x PP profile', results['T3_prefix_bifurcation_pp']['pass']),
    ('T4', 'Gallows domain coherence', results['T4_gallows_domain']['pass']),
    ('T5', 'Within-line PP consistency', results['T5_pp_consistency']['pass']),
    ('T6', 'RI-adjacent PP consistency', results['T6_adjacent_pp']['pass']),
]

for tid, name, passed in test_names:
    status = "PASS" if passed else "FAIL"
    print(f"  {tid} [{status}] {name}")

print()
if pass_count >= 4:
    verdict = "MODEL B SUPPORTED: RI has semantic binding to co-occurring PP."
    verdict_code = "MODEL_B"
elif pass_count <= 2:
    verdict = "MODEL A SUPPORTED: RI is an independent label with no PP relationship."
    verdict_code = "MODEL_A"
else:
    verdict = "INCONCLUSIVE: Mixed evidence for RI-PP binding."
    verdict_code = "MIXED"

print(f"  VERDICT: {verdict}")

results['summary'] = {
    'pass_count': pass_count,
    'total_tests': 6,
    'verdict': verdict,
    'verdict_code': verdict_code,
}

# Save
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
output_path = RESULTS_DIR / 'ri_binding_tests.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {output_path}")
