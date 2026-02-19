"""Phase 401: Rosettes-B Vocabulary Tracing

Traces Rosettes vocabulary into B programs to determine:
1. Which rosettes connect to which B folios
2. Whether the connection is specific (each rosette → distinct B folios) or generic
3. Where rosette-shared vocabulary appears within B programs

6-test battery:
  T1: Vocabulary Partition Census (feasibility gate)
  T2: C1091 Pharma Folio Validation (highest priority)
  T3: Section Discrimination via Rosettes Regions
  T4: Positional Pattern in B Programs (most novel)
  T5: Label vs Ring-Text Discrimination Power
  T6: Per-Rosette B-Folio Affinity Profiles (synthesis)

References: C1091, C1093, C1098, C1101, C1109, C1113, C932
"""

import json
import math
import random
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer, RosettesAnalyzer

RESULTS_DIR = PROJECT / 'phases' / 'ROSETTES_B_VOCABULARY_TRACING' / 'results'

# C1091 target folios (pharmaceutical convergence)
C1091_TARGETS = {'f76r', 'f108r', 'f111r', 'f108v', 'f116r'}

# Label regions vs ring-text (description) regions on f85v2
LABEL_REGIONS = {'B1', 'B2', 'B3', 'M1', 'M2', 'U1', 'U2', 'U3'}
RING_REGIONS = {'C2', 'N1', 'N2', 'V1', 'V2'}

MIN_BODY_LINES = 4


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def jaccard(set_a, set_b):
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def overlap_coefficient(small_set, big_set):
    """Fraction of small_set found in big_set."""
    if not small_set:
        return 0.0
    return len(small_set & big_set) / len(small_set)


def normal_cdf(x):
    if x < -8: return 0.0
    if x > 8: return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if x >= 0 else -1
    t = 1.0 / (1.0 + p * abs(x))
    y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1) * t * math.exp(-x*x/2)
    return 0.5 * (1.0 + sign * y)


def wilcoxon_signed_rank(values):
    nonzero = [(abs(v), 1 if v > 0 else -1) for v in values if v != 0]
    n = len(nonzero)
    if n < 5:
        return 0, 0.0, 1.0, n
    nonzero.sort(key=lambda p: p[0])
    ranks = []
    i = 0
    while i < n:
        j = i
        while j < n and nonzero[j][0] == nonzero[i][0]:
            j += 1
        avg_rank = (i + j - 1) / 2.0 + 1.0
        for k in range(i, j):
            ranks.append((avg_rank, nonzero[k][1]))
        i = j
    W_plus = sum(r for r, s in ranks if s > 0)
    W_minus = sum(r for r, s in ranks if s < 0)
    W = min(W_plus, W_minus)
    mu = n * (n + 1) / 4.0
    sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)
    if sigma == 0:
        return W, 0.0, 1.0, n
    z = (W - mu) / sigma
    p = 2 * normal_cdf(-abs(z))
    return W, z, p, n


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data():
    """Load all data needed for the 6-test battery."""
    tx = Transcript()
    morph = Morphology()
    ra = RosettesAnalyzer()
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # 1. Per-rosette MIDDLE lists
    prof_path = PROJECT / 'phases' / 'ROSETTES_FUNCTIONAL_ANATOMY' / 'results' / 'rosettes_functional_profiling.json'
    with open(prof_path) as f:
        prof_data = json.load(f)
    rosette_middles = {k: set(v) for k, v in prof_data['rosette_middles'].items()}
    rosette_regions = prof_data['rosette_regions']  # rosette_name → [region_codes]

    # 2. Bridge MIDDLEs
    bridge_path = PROJECT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(bridge_path) as f:
        bridge_data = json.load(f)
    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])

    # 3. Rosettes-exclusive MIDDLEs (via RosettesAnalyzer)
    vocab_overlap = ra.vocabulary_overlap()
    exclusive_set = set(vocab_overlap['unique_list'])

    # 4. All B corpus MIDDLEs (per folio)
    b_folio_middles = defaultdict(set)
    folio_section = {}
    b_folio_tokens = defaultdict(list)  # for positional analysis

    lines = defaultdict(list)
    for tok in tx.currier_b():
        word = tok.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle != '_EMPTY_':
            b_folio_middles[tok.folio].add(m.middle)
        folio_section[tok.folio] = tok.section
        lines[(tok.folio, tok.line)].append(tok)

    b_corpus_middles = set()
    for ms in b_folio_middles.values():
        b_corpus_middles |= ms

    # 5. Build paragraphs for positional analysis
    folio_lines = defaultdict(list)
    for (f, l), toks in sorted(lines.items()):
        folio_lines[f].append((l, toks))

    paragraphs = []
    for f in sorted(folio_lines):
        curr_par = []
        for l, toks in folio_lines[f]:
            if toks[0].par_initial and curr_par:
                paragraphs.append({'folio': f, 'lines': curr_par})
                curr_par = []
            curr_par.append((l, toks))
        if curr_par:
            paragraphs.append({'folio': f, 'lines': curr_par})

    # 6. Per-region MIDDLE sets (label vs ring classification)
    anat_path = PROJECT / 'phases' / 'ROSETTES_FUNCTIONAL_ANATOMY' / 'results' / 'rosettes_functional_anatomy.json'
    with open(anat_path) as f:
        anat_data = json.load(f)

    label_middles = set()
    ring_middles = set()
    for key, region_data in anat_data.items():
        if not key.startswith('f85v2:'):
            continue
        region_code = key.split(':')[1]
        if 'middle_coverage' in region_data:
            for mid in region_data['middle_coverage']:
                if region_code in LABEL_REGIONS:
                    label_middles.add(mid)
                elif region_code in RING_REGIONS:
                    ring_middles.add(mid)

    print(f"Loaded: {len(rosette_middles)} rosettes, {len(bridge_set)} bridges, "
          f"{len(exclusive_set)} exclusives, {len(b_folio_middles)} B folios")
    print(f"Label region MIDDLEs: {len(label_middles)}, Ring region MIDDLEs: {len(ring_middles)}")

    return {
        'rosette_middles': rosette_middles,
        'rosette_regions': rosette_regions,
        'bridge_set': bridge_set,
        'exclusive_set': exclusive_set,
        'b_corpus_middles': b_corpus_middles,
        'b_folio_middles': dict(b_folio_middles),
        'folio_section': folio_section,
        'paragraphs': paragraphs,
        'morph': morph,
        'mid_analyzer': mid_analyzer,
        'label_middles': label_middles,
        'ring_middles': ring_middles,
    }


# ---------------------------------------------------------------------------
# T1: Vocabulary Partition Census
# ---------------------------------------------------------------------------

def t1_vocabulary_census(data):
    """Per-rosette partition: bridge / exclusive / informative."""
    print("\n=== T1: Vocabulary Partition Census ===")

    rosette_middles = data['rosette_middles']
    bridge_set = data['bridge_set']
    exclusive_set = data['exclusive_set']
    b_corpus_middles = data['b_corpus_middles']

    census = {}
    total_informative = set()
    feasible_rosettes = 0

    for name in sorted(rosette_middles.keys()):
        middles = rosette_middles[name]
        n_total = len(middles)
        n_bridge = len(middles & bridge_set)
        n_exclusive = len(middles & exclusive_set)
        # Informative = in rosette AND in B corpus AND NOT bridge
        in_b = middles & b_corpus_middles
        informative = in_b - bridge_set
        n_informative = len(informative)
        total_informative |= informative

        if n_informative >= 5:
            feasible_rosettes += 1

        census[name] = {
            'total': n_total,
            'bridge': n_bridge,
            'exclusive': n_exclusive,
            'in_b_corpus': len(in_b),
            'informative': n_informative,
            'informative_list': sorted(informative),
        }

        print(f"  {name:8s}: total={n_total:2d}  bridge={n_bridge:2d}  "
              f"excl={n_exclusive:2d}  inform={n_informative:2d}  "
              f"{'OK' if n_informative >= 5 else 'SPARSE'}")

    feasible = feasible_rosettes >= 5
    print(f"\n  Total informative MIDDLEs (union): {len(total_informative)}")
    print(f"  Rosettes with 5+ informative: {feasible_rosettes}/9")
    print(f"  Gate: {'FEASIBLE' if feasible else 'GROUP_AND_RETRY'}")

    return {
        'verdict': 'FEASIBLE' if feasible else 'GROUP_AND_RETRY',
        'census': {k: {kk: vv for kk, vv in v.items() if kk != 'informative_list'}
                   for k, v in census.items()},
        'informative_lists': {k: v['informative_list'] for k, v in census.items()},
        'total_informative': len(total_informative),
        'feasible_rosettes': feasible_rosettes,
    }


# ---------------------------------------------------------------------------
# T2: C1091 Pharma Folio Validation
# ---------------------------------------------------------------------------

def t2_pharma_folio_validation(data, t1_result):
    """Jaccard overlap with C1091 target folios using informative MIDDLEs."""
    print("\n=== T2: C1091 Pharma Folio Validation ===")

    random.seed(42)
    b_folio_middles = data['b_folio_middles']
    informative_lists = t1_result['informative_lists']

    # Pool all informative MIDDLEs
    all_informative = set()
    for middles in informative_lists.values():
        all_informative.update(middles)

    if not all_informative:
        print("  No informative MIDDLEs!")
        return {'verdict': 'NO_DATA'}

    # Compute per-folio overlap with pooled informative set
    folio_overlaps = {}
    for folio, middles in b_folio_middles.items():
        folio_informative = middles & all_informative
        folio_overlaps[folio] = {
            'n_shared': len(folio_informative),
            'jaccard': jaccard(all_informative, middles),
            'overlap_coeff': overlap_coefficient(all_informative, middles),
            'shared_list': sorted(folio_informative),
        }

    # Sort by overlap coefficient
    ranked = sorted(folio_overlaps.items(), key=lambda x: x[1]['n_shared'], reverse=True)

    # Target vs non-target
    target_overlaps = [v['n_shared'] for f, v in folio_overlaps.items() if f in C1091_TARGETS]
    nontarget_overlaps = [v['n_shared'] for f, v in folio_overlaps.items() if f not in C1091_TARGETS]

    target_mean = sum(target_overlaps) / len(target_overlaps) if target_overlaps else 0
    nontarget_mean = sum(nontarget_overlaps) / len(nontarget_overlaps) if nontarget_overlaps else 0
    lift = target_mean / nontarget_mean if nontarget_mean > 0 else float('inf')

    # Permutation test
    N_PERM = 1000
    n_targets = len(C1091_TARGETS & set(b_folio_middles.keys()))
    all_overlaps = [v['n_shared'] for v in folio_overlaps.values()]
    perm_lifts = []
    for _ in range(N_PERM):
        perm_sample = random.sample(all_overlaps, min(n_targets, len(all_overlaps)))
        perm_rest = [x for x in all_overlaps if x not in perm_sample]
        if not perm_rest:
            continue
        perm_mean = sum(perm_sample) / len(perm_sample)
        rest_mean = sum(perm_rest) / len(perm_rest)
        if rest_mean > 0:
            perm_lifts.append(perm_mean / rest_mean)

    p_val = sum(1 for l in perm_lifts if l >= lift) / len(perm_lifts) if perm_lifts else 1.0

    print(f"  Target folios found: {n_targets} of {len(C1091_TARGETS)}")
    print(f"  Target mean shared: {target_mean:.1f}")
    print(f"  Non-target mean shared: {nontarget_mean:.1f}")
    print(f"  Lift: {lift:.2f}x")
    print(f"  Permutation p-value: {p_val:.4f}")

    print(f"\n  Top 10 B folios by shared informative MIDDLEs:")
    for i, (folio, ov) in enumerate(ranked[:10]):
        marker = " ***TARGET***" if folio in C1091_TARGETS else ""
        print(f"    {i+1:2d}. {folio}: {ov['n_shared']} shared{marker}")

    if lift >= 2.0 and p_val < 0.05:
        verdict = 'C1091_VALIDATED_AT_INFORMATIVE_LEVEL'
    elif lift >= 1.5 and p_val < 0.10:
        verdict = 'C1091_PARTIAL_VALIDATION'
    else:
        verdict = 'C1091_NOT_CONFIRMED'

    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_informative_pool': len(all_informative),
        'n_targets_found': n_targets,
        'target_mean_shared': round(target_mean, 2),
        'nontarget_mean_shared': round(nontarget_mean, 2),
        'lift': round(lift, 3),
        'perm_p': round(p_val, 4),
        'top_10': [(f, ov['n_shared']) for f, ov in ranked[:10]],
    }


# ---------------------------------------------------------------------------
# T3: Section Discrimination
# ---------------------------------------------------------------------------

def t3_section_discrimination(data, t1_result):
    """Per-rosette ANOVA of section on informative overlap."""
    print("\n=== T3: Section Discrimination via Rosettes ===")

    b_folio_middles = data['b_folio_middles']
    folio_section = data['folio_section']
    informative_lists = t1_result['informative_lists']

    rosette_results = {}
    n_significant = 0

    for rosette_name in sorted(informative_lists.keys()):
        inf_set = set(informative_lists[rosette_name])
        if len(inf_set) < 3:
            continue

        # Per-folio overlap
        section_overlaps = defaultdict(list)
        for folio, middles in b_folio_middles.items():
            sec = folio_section.get(folio)
            if not sec:
                continue
            n_shared = len(middles & inf_set)
            section_overlaps[sec].append(n_shared)

        if len(section_overlaps) < 2:
            continue

        # One-way ANOVA
        all_vals = []
        groups = []
        for sec, vals in section_overlaps.items():
            for v in vals:
                all_vals.append(v)
                groups.append(sec)

        grand_mean = sum(all_vals) / len(all_vals)
        k = len(section_overlaps)
        n_total = len(all_vals)

        ss_between = sum(len(vals) * (sum(vals)/len(vals) - grand_mean)**2
                         for vals in section_overlaps.values())
        ss_within = sum(sum((v - sum(vals)/len(vals))**2 for v in vals)
                        for vals in section_overlaps.values())

        df_b = k - 1
        df_w = n_total - k

        if df_w > 0 and ss_within > 0:
            f_ratio = (ss_between / df_b) / (ss_within / df_w)
        else:
            f_ratio = 0

        # Identify top section
        section_means = {sec: sum(vals)/len(vals) for sec, vals in section_overlaps.items()}
        top_section = max(section_means, key=section_means.get)

        # Rough p-value from F-distribution (using permutation)
        random.seed(42)
        n_perm = 500
        perm_f_count = 0
        for _ in range(n_perm):
            shuffled = all_vals[:]
            random.shuffle(shuffled)
            perm_groups = defaultdict(list)
            idx = 0
            for sec, vals in section_overlaps.items():
                for _ in vals:
                    perm_groups[sec].append(shuffled[idx])
                    idx += 1
            perm_grand = sum(shuffled) / len(shuffled)
            perm_ssb = sum(len(perm_groups[s]) * (sum(perm_groups[s])/len(perm_groups[s]) - perm_grand)**2
                           for s in perm_groups)
            perm_ssw = sum(sum((v - sum(perm_groups[s])/len(perm_groups[s]))**2 for v in perm_groups[s])
                           for s in perm_groups)
            if perm_ssw > 0:
                perm_f = (perm_ssb / df_b) / (perm_ssw / df_w)
                if perm_f >= f_ratio:
                    perm_f_count += 1
        perm_p = perm_f_count / n_perm

        is_sig = perm_p < 0.05
        if is_sig:
            n_significant += 1

        section_means_rounded = {s: round(m, 3) for s, m in sorted(section_means.items())}
        print(f"  {rosette_name:8s}: F={f_ratio:5.2f} p={perm_p:.3f} "
              f"top={top_section} means={section_means_rounded} "
              f"{'*SIG*' if is_sig else ''}")

        rosette_results[rosette_name] = {
            'f_ratio': round(f_ratio, 3),
            'perm_p': round(perm_p, 4),
            'top_section': top_section,
            'section_means': section_means_rounded,
            'significant': is_sig,
        }

    if n_significant >= 3:
        verdict = 'SECTION_SPECIFIC_INDEXING'
    else:
        verdict = 'GENERIC_INDEXING'

    print(f"\n  Significant rosettes: {n_significant}/{len(rosette_results)}")
    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_significant': n_significant,
        'n_tested': len(rosette_results),
        'per_rosette': rosette_results,
    }


# ---------------------------------------------------------------------------
# T4: Positional Pattern in B Programs
# ---------------------------------------------------------------------------

def t4_positional_pattern(data, t1_result):
    """Where do rosette-shared MIDDLEs appear within B paragraphs?"""
    print("\n=== T4: Positional Pattern in B Programs ===")

    morph = data['morph']
    mid_analyzer = data['mid_analyzer']
    paragraphs = data['paragraphs']

    # Pool all informative MIDDLEs
    all_informative = set()
    for middles in t1_result['informative_lists'].values():
        all_informative.update(middles)

    if not all_informative:
        print("  No informative MIDDLEs!")
        return {'verdict': 'NO_DATA'}

    # For frequency control: compute median log-frequency of informative MIDDLEs
    inf_freqs = []
    for mid in all_informative:
        stats = mid_analyzer.get_stats(mid)
        if stats:
            inf_freqs.append(stats.token_count)
    inf_median_freq = sorted(inf_freqs)[len(inf_freqs)//2] if inf_freqs else 0

    # Track positions of rosette-shared vs all tokens
    rosette_positions = []  # (paragraph_relative_position, is_rosette_shared)
    all_positions = []
    spec_zone_rosette = 0
    exec_zone_rosette = 0
    spec_zone_all = 0
    exec_zone_all = 0

    n_qualifying = 0
    for para in paragraphs:
        if len(para['lines']) < 2:
            continue
        body_lines = para['lines'][1:]
        if len(body_lines) < MIN_BODY_LINES:
            continue
        n_qualifying += 1
        n_body = len(body_lines)

        for li, (line_id, toks) in enumerate(body_lines):
            rel_pos = li / max(n_body - 1, 1)
            for tok in toks:
                word = tok.word.strip()
                if not word or '*' in word:
                    continue
                m = morph.extract(word)
                if not m.middle or m.middle == '_EMPTY_':
                    continue

                is_rosette = m.middle in all_informative
                all_positions.append(rel_pos)
                if rel_pos < 0.4:
                    spec_zone_all += 1
                else:
                    exec_zone_all += 1

                if is_rosette:
                    rosette_positions.append(rel_pos)
                    if rel_pos < 0.4:
                        spec_zone_rosette += 1
                    else:
                        exec_zone_rosette += 1

    if not rosette_positions:
        print("  No rosette-shared tokens found in qualifying paragraphs!")
        return {'verdict': 'NO_DATA'}

    mean_ros_pos = sum(rosette_positions) / len(rosette_positions)
    mean_all_pos = sum(all_positions) / len(all_positions)

    # Test: is rosette position different from all-token position?
    deviations = [p - mean_all_pos for p in rosette_positions]
    W, z, p_val, n_nz = wilcoxon_signed_rank(deviations)

    # Zone fractions
    ros_spec_frac = spec_zone_rosette / len(rosette_positions)
    all_spec_frac = spec_zone_all / len(all_positions)

    # Frequency control: compare rosette MIDDLEs to frequency-matched non-rosette
    freq_matched_positions = []
    for para in paragraphs:
        if len(para['lines']) < 2:
            continue
        body_lines = para['lines'][1:]
        if len(body_lines) < MIN_BODY_LINES:
            continue
        n_body = len(body_lines)
        for li, (line_id, toks) in enumerate(body_lines):
            rel_pos = li / max(n_body - 1, 1)
            for tok in toks:
                word = tok.word.strip()
                if not word or '*' in word:
                    continue
                m = morph.extract(word)
                if not m.middle or m.middle == '_EMPTY_':
                    continue
                if m.middle in all_informative:
                    continue  # skip rosette MIDDLEs
                stats = mid_analyzer.get_stats(m.middle)
                if stats and abs(stats.token_count - inf_median_freq) < inf_median_freq * 0.5:
                    freq_matched_positions.append(rel_pos)

    mean_freq_matched = sum(freq_matched_positions) / len(freq_matched_positions) if freq_matched_positions else 0.5
    ros_vs_matched_diff = mean_ros_pos - mean_freq_matched

    print(f"  Qualifying paragraphs: {n_qualifying}")
    print(f"  Rosette-shared tokens: {len(rosette_positions)}")
    print(f"  Mean position (rosette): {mean_ros_pos:.4f}")
    print(f"  Mean position (all): {mean_all_pos:.4f}")
    print(f"  Mean position (freq-matched): {mean_freq_matched:.4f}")
    print(f"  Wilcoxon z={z:.2f}, p={p_val:.4f}")
    print(f"  Spec zone (rosette): {ros_spec_frac:.3f} vs (all): {all_spec_frac:.3f}")
    print(f"  Rosette vs freq-matched diff: {ros_vs_matched_diff:.4f}")

    if p_val < 0.05 and abs(ros_vs_matched_diff) > 0.02:
        verdict = 'GENUINE_POSITIONAL_SPECIFICITY'
    elif p_val < 0.05:
        verdict = 'C932_RARITY_ARTIFACT'
    else:
        verdict = 'NO_POSITIONAL_CONCENTRATION'

    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_paragraphs': n_qualifying,
        'n_rosette_tokens': len(rosette_positions),
        'n_all_tokens': len(all_positions),
        'mean_pos_rosette': round(mean_ros_pos, 4),
        'mean_pos_all': round(mean_all_pos, 4),
        'mean_pos_freq_matched': round(mean_freq_matched, 4),
        'wilcoxon_z': round(z, 3),
        'wilcoxon_p': round(p_val, 6),
        'spec_frac_rosette': round(ros_spec_frac, 3),
        'spec_frac_all': round(all_spec_frac, 3),
        'rosette_vs_matched_diff': round(ros_vs_matched_diff, 4),
        'inf_median_freq': inf_median_freq,
        'n_freq_matched': len(freq_matched_positions),
    }


# ---------------------------------------------------------------------------
# T5: Label vs Ring-Text Discrimination Power
# ---------------------------------------------------------------------------

def t5_label_vs_ring(data):
    """Compare discrimination power of label vs ring-text vocabulary."""
    print("\n=== T5: Label vs Ring-Text Discrimination Power ===")

    bridge_set = data['bridge_set']
    exclusive_set = data['exclusive_set']
    b_corpus_middles = data['b_corpus_middles']
    b_folio_middles = data['b_folio_middles']

    # Label informative = label_middles ∩ B_corpus - bridge
    label_inf = (data['label_middles'] & b_corpus_middles) - bridge_set
    ring_inf = (data['ring_middles'] & b_corpus_middles) - bridge_set

    print(f"  Label informative MIDDLEs: {len(label_inf)}")
    print(f"  Ring-text informative MIDDLEs: {len(ring_inf)}")

    if not label_inf or not ring_inf:
        print("  Insufficient vocabulary for comparison!")
        return {'verdict': 'NO_DATA'}

    # Per-folio overlap with each set
    label_overlaps = []
    ring_overlaps = []
    for folio, middles in b_folio_middles.items():
        label_overlaps.append(len(middles & label_inf))
        ring_overlaps.append(len(middles & ring_inf))

    # Variance comparison
    label_mean = sum(label_overlaps) / len(label_overlaps)
    ring_mean = sum(ring_overlaps) / len(ring_overlaps)
    label_var = sum((x - label_mean)**2 for x in label_overlaps) / len(label_overlaps)
    ring_var = sum((x - ring_mean)**2 for x in ring_overlaps) / len(ring_overlaps)

    # Coefficient of variation (normalized by mean to account for different pool sizes)
    label_cv = math.sqrt(label_var) / label_mean if label_mean > 0 else 0
    ring_cv = math.sqrt(ring_var) / ring_mean if ring_mean > 0 else 0

    print(f"  Label: mean={label_mean:.2f}, var={label_var:.2f}, CV={label_cv:.3f}")
    print(f"  Ring:  mean={ring_mean:.2f}, var={ring_var:.2f}, CV={ring_cv:.3f}")

    if label_cv > ring_cv:
        verdict = 'LABEL_DISCRIMINATES_MORE'
    else:
        verdict = 'RING_ALSO_DISCRIMINATIVE'

    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_label_informative': len(label_inf),
        'n_ring_informative': len(ring_inf),
        'label_inf_list': sorted(label_inf),
        'ring_inf_list': sorted(ring_inf),
        'label_mean': round(label_mean, 3),
        'label_var': round(label_var, 3),
        'label_cv': round(label_cv, 4),
        'ring_mean': round(ring_mean, 3),
        'ring_var': round(ring_var, 3),
        'ring_cv': round(ring_cv, 4),
    }


# ---------------------------------------------------------------------------
# T6: Per-Rosette B-Folio Affinity Profiles
# ---------------------------------------------------------------------------

def t6_folio_affinity(data, t1_result):
    """Per-rosette top-connected B folios and cross-rosette divergence."""
    print("\n=== T6: Per-Rosette B-Folio Affinity Profiles ===")

    b_folio_middles = data['b_folio_middles']
    folio_section = data['folio_section']
    informative_lists = t1_result['informative_lists']

    # Only use rosettes with 5+ informative MIDDLEs
    viable_rosettes = {k: set(v) for k, v in informative_lists.items() if len(v) >= 5}

    if len(viable_rosettes) < 2:
        print("  Fewer than 2 viable rosettes!")
        return {'verdict': 'INSUFFICIENT_ROSETTES'}

    # Per-rosette overlap with each B folio
    rosette_folio_matrix = {}
    rosette_top5 = {}

    for ros_name, inf_set in sorted(viable_rosettes.items()):
        folio_scores = {}
        for folio, middles in b_folio_middles.items():
            n_shared = len(middles & inf_set)
            folio_scores[folio] = n_shared
        rosette_folio_matrix[ros_name] = folio_scores

        # Top 5
        ranked = sorted(folio_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        rosette_top5[ros_name] = [f for f, _ in ranked]
        top5_info = [(f, s, folio_section.get(f, '?')) for f, s in ranked]
        parts = [f"{f}({s},{sec})" for f, s, sec in top5_info]
        print(f"  {ros_name:8s}: top5 = {', '.join(parts)}")

    # Cross-rosette divergence: Jaccard between top-5 sets
    ros_names = sorted(viable_rosettes.keys())
    top5_jaccards = []
    for i in range(len(ros_names)):
        for j in range(i+1, len(ros_names)):
            j_val = jaccard(set(rosette_top5[ros_names[i]]),
                            set(rosette_top5[ros_names[j]]))
            top5_jaccards.append(j_val)

    mean_top5_jaccard = sum(top5_jaccards) / len(top5_jaccards) if top5_jaccards else 0

    # Per-folio: which rosette is it most affiliated with?
    folio_affinity = {}
    for folio in b_folio_middles:
        best_ros = None
        best_score = -1
        for ros_name, scores in rosette_folio_matrix.items():
            if scores.get(folio, 0) > best_score:
                best_score = scores[folio]
                best_ros = ros_name
        folio_affinity[folio] = {'rosette': best_ros, 'score': best_score}

    # Count folios per rosette affinity
    affinity_counts = Counter(v['rosette'] for v in folio_affinity.values())

    print(f"\n  Mean top-5 cross-rosette Jaccard: {mean_top5_jaccard:.3f}")
    print(f"  (Low = different targets, High = same targets)")
    print(f"  Folio affinity distribution: {dict(sorted(affinity_counts.items()))}")

    if mean_top5_jaccard < 0.3:
        verdict = 'SPECIFIC_INDEXING_ARCHITECTURE'
    elif mean_top5_jaccard < 0.5:
        verdict = 'PARTIALLY_SPECIFIC'
    else:
        verdict = 'GENERIC_VOCABULARY_POOL'

    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_viable_rosettes': len(viable_rosettes),
        'rosette_top5': rosette_top5,
        'mean_top5_jaccard': round(mean_top5_jaccard, 4),
        'folio_affinity_counts': dict(sorted(affinity_counts.items())),
        'rosette_folio_matrix': {
            ros: {f: s for f, s in sorted(scores.items(), key=lambda x: -x[1])[:10]}
            for ros, scores in rosette_folio_matrix.items()
        },
    }


# ---------------------------------------------------------------------------
# Combined verdict
# ---------------------------------------------------------------------------

def combined_verdict(results):
    print("\n" + "=" * 60)
    print("COMBINED VERDICT")
    print("=" * 60)

    votes = {
        't1': results['t1']['verdict'],
        't2': results['t2']['verdict'],
        't3': results['t3']['verdict'],
        't4': results['t4']['verdict'],
        't5': results['t5']['verdict'],
        't6': results['t6']['verdict'],
    }

    print("\n  Per-test verdicts:")
    for test, verdict in votes.items():
        print(f"    {test}: {verdict}")

    t2_validated = 'VALIDATED' in votes['t2'] or 'PARTIAL' in votes['t2']
    t3_specific = votes['t3'] == 'SECTION_SPECIFIC_INDEXING'
    t6_specific = votes['t6'] == 'SPECIFIC_INDEXING_ARCHITECTURE'

    if t2_validated and t3_specific and t6_specific:
        overall = 'ROSETTES_SPECIFIC_INDEX'
        reasoning = ('C1091 validated at informative level, rosettes show section-specific '
                     'discrimination, and different rosettes connect to different B folios.')
    elif t2_validated and (t3_specific or t6_specific):
        overall = 'ROSETTES_PARTIALLY_SPECIFIC_INDEX'
        reasoning = ('C1091 validated but specificity evidence is mixed — '
                     'some rosettes discriminate by section, not all connect to distinct targets.')
    elif t2_validated:
        overall = 'ROSETTES_GENERIC_INDEX'
        reasoning = ('C1091 validated but rosettes index generically — '
                     'no section specificity or target differentiation.')
    else:
        overall = 'ROSETTES_BRIDGE_MEDIATED_ONLY'
        reasoning = ('C1091 not confirmed at informative level. '
                     'Rosettes-B connection is bridge-mediated only (extends C1109).')

    print(f"\n  OVERALL: {overall}")
    print(f"  Reasoning: {reasoning}")

    return {
        'overall': overall,
        'reasoning': reasoning,
        'per_test_verdicts': votes,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Phase 401: Rosettes-B Vocabulary Tracing")
    print("=" * 50)

    data = load_data()

    results = {}
    results['t1'] = t1_vocabulary_census(data)
    results['t2'] = t2_pharma_folio_validation(data, results['t1'])
    results['t3'] = t3_section_discrimination(data, results['t1'])
    results['t4'] = t4_positional_pattern(data, results['t1'])
    results['t5'] = t5_label_vs_ring(data)
    results['t6'] = t6_folio_affinity(data, results['t1'])
    results['combined'] = combined_verdict(results)

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / 'rosettes_b_tracing_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
