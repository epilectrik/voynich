"""Phase 407: Dark Pipeline Functional Test -- 5-test battery.

Tests the structural fate of 300 'dark-pipeline' PP MIDDLEs that bridge
A and B vocabularies but don't match any of B's 49 grammar classes (C1135).

Tests:
  1. Classification trace: grammar-classified vs HT/UN
  2. Construction grammar: PREFIX/SUFFIX patterns and bifurcation
  3. Bridge overlap: intersection with 85 bridge MIDDLEs
  4. Paragraph position: line-1 concentration vs HT baseline
  5. Section profile: JS divergence comparison
"""
import json
import sys
import math
import os
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import (Transcript, Morphology, MiddleAnalyzer,
                              CORE_PREFIXES, EXTENDED_PREFIXES)

# Prefix classification sets
GRAMMAR_STANDARD = set(CORE_PREFIXES)   # {ch, sh, qo, da, ok, ot, ol, ct}
EXTENDED_SET = set(EXTENDED_PREFIXES) - GRAMMAR_STANDARD


# --- Utility functions (from Phase 406 pattern) ---

def round_floats(obj, digits=4):
    """Recursively round floats in nested dicts/lists."""
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    return obj


def shannon_entropy(counts):
    """Shannon entropy in bits from a Counter/dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def herfindahl(counts):
    """Herfindahl index (sum of squared shares). 1/N=uniform, 1.0=concentrated."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return sum((c / total) ** 2 for c in counts.values())


def jensen_shannon(p_counts, q_counts):
    """Jensen-Shannon divergence between two count distributions."""
    all_keys = set(p_counts.keys()) | set(q_counts.keys())
    p_total = sum(p_counts.values())
    q_total = sum(q_counts.values())
    if p_total == 0 or q_total == 0:
        return 0.0

    js = 0.0
    for k in all_keys:
        p = p_counts.get(k, 0) / p_total
        q = q_counts.get(k, 0) / q_total
        m = (p + q) / 2
        if p > 0 and m > 0:
            js += 0.5 * p * math.log2(p / m)
        if q > 0 and m > 0:
            js += 0.5 * q * math.log2(q / m)
    return js


# --- Data loading ---

def load_data():
    """Load all input files and pre-compute all lookup structures via single B-token pass."""

    # 1. Load static data files
    with open(ROOT / 'phases/A_TO_B_ROLE_PROJECTION/results/pp_role_foundation.json',
              encoding='utf-8') as f:
        pp_role_data = json.load(f)

    with open(ROOT / 'phases/CROSS_SYSTEM_VOCABULARY_FLOW/results/ab_vocabulary_flow.json',
              encoding='utf-8') as f:
        vocab_flow = json.load(f)

    with open(ROOT / 'phases/BRIDGE_MIDDLE_SELECTION_MECHANISM/results/bridge_selection.json',
              encoding='utf-8') as f:
        bridge_data = json.load(f)

    with open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json',
              encoding='utf-8') as f:
        class_map = json.load(f)

    # 2. Build population sets
    unmatched_pp_list = pp_role_data['unmatched_pp']  # 315 MIDDLEs
    b_absent = set(vocab_flow['b1']['b_absent_middles'])  # 15 to exclude
    dark_pipeline_set = set(unmatched_pp_list) - b_absent  # 300 B-present

    # Matched PP set: MIDDLEs with n_classes > 0
    matched_pp_set = set()
    for mid, info in pp_role_data['pp_role_map'].items():
        if info['n_classes'] > 0:
            matched_pp_set.add(mid)

    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])  # 85

    token_to_class = class_map['token_to_class']  # word -> class_id
    token_to_role = class_map.get('token_to_role', {})
    classified_set = set(token_to_class.keys())  # 480 grammar words

    # 3. Initialize API
    tx = Transcript()
    morph = Morphology()

    # 4. Single pass over B tokens
    dark_tokens = []
    grammar_tokens = []
    ht_tokens = []
    matched_pp_tokens = []

    # Per-MIDDLE aggregators for dark pipeline
    dark_middle_tokens = defaultdict(list)  # middle -> [token records]

    # Per-MIDDLE frequency and section tracking (all MIDDLEs)
    middle_b_freq = Counter()
    middle_section_freq = defaultdict(Counter)

    # Paragraph first-line detection
    par_first_lines = set()

    # Section counters per population
    dark_section = Counter()
    ht_section = Counter()
    grammar_section = Counter()

    n_scanned = 0
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue

        n_scanned += 1
        m = morph.extract(word)
        mid = m.middle

        is_grammar = word in classified_set
        is_dark = (mid in dark_pipeline_set) if mid else False
        is_matched_pp = (mid in matched_pp_set) if mid else False

        record = {
            'word': word,
            'folio': token.folio,
            'line': token.line,
            'section': token.section,
            'middle': mid,
            'prefix': m.prefix,
            'suffix': m.suffix,
            'articulator': m.articulator,
            'is_grammar': is_grammar,
            'is_line1': token.line == '1',
            'par_initial': token.par_initial,
        }

        if is_grammar:
            grammar_tokens.append(record)
            grammar_section[token.section] += 1
        else:
            ht_tokens.append(record)
            ht_section[token.section] += 1

        if is_dark:
            dark_tokens.append(record)
            dark_middle_tokens[mid].append(record)
            dark_section[token.section] += 1

        if is_matched_pp:
            matched_pp_tokens.append(record)

        if mid:
            middle_b_freq[mid] += 1
            middle_section_freq[mid][token.section] += 1

        if token.par_initial:
            par_first_lines.add((token.folio, token.line))

    print(f"Scanned {n_scanned} B tokens")
    print(f"  Grammar: {len(grammar_tokens)}, HT/UN: {len(ht_tokens)}")
    print(f"  Dark-pipeline tokens: {len(dark_tokens)} (from {len(dark_pipeline_set)} MIDDLEs)")
    print(f"  Matched-PP tokens: {len(matched_pp_tokens)}")

    return {
        'dark_pipeline_set': dark_pipeline_set,
        'matched_pp_set': matched_pp_set,
        'bridge_set': bridge_set,
        'classified_set': classified_set,
        'token_to_class': token_to_class,
        'token_to_role': token_to_role,
        'dark_tokens': dark_tokens,
        'grammar_tokens': grammar_tokens,
        'ht_tokens': ht_tokens,
        'matched_pp_tokens': matched_pp_tokens,
        'dark_middle_tokens': dark_middle_tokens,
        'middle_b_freq': middle_b_freq,
        'middle_section_freq': middle_section_freq,
        'par_first_lines': par_first_lines,
        'dark_section': dark_section,
        'ht_section': ht_section,
        'grammar_section': grammar_section,
        'n_scanned': n_scanned,
    }


# --- Test 1: Classification Trace ---

def test1_classification_trace(data):
    """For each dark-pipeline MIDDLE's B tokens, classify as GRAMMAR or HT/UN."""
    dark_tokens = data['dark_tokens']
    matched_pp_tokens = data['matched_pp_tokens']
    dark_middle_tokens = data['dark_middle_tokens']
    classified_set = data['classified_set']

    if not dark_tokens:
        return {'verdict': 'NO_DATA', 'error': 'No dark-pipeline tokens found'}

    # Aggregate classification
    n_grammar = sum(1 for t in dark_tokens if t['is_grammar'])
    n_ht = len(dark_tokens) - n_grammar
    grammar_frac = n_grammar / len(dark_tokens)
    ht_frac = n_ht / len(dark_tokens)

    # Type-level
    dark_types = set(t['word'] for t in dark_tokens)
    grammar_types = dark_types & classified_set
    ht_types = dark_types - classified_set

    # Per-MIDDLE breakdown
    per_middle = {}
    for mid, tokens in dark_middle_tokens.items():
        mg = sum(1 for t in tokens if t['is_grammar'])
        mh = len(tokens) - mg
        per_middle[mid] = {
            'n_tokens': len(tokens),
            'n_grammar': mg,
            'n_ht': mh,
            'grammar_frac': mg / len(tokens) if tokens else 0,
        }

    # How many MIDDLEs produce ONLY HT tokens?
    pure_ht_middles = sum(1 for m in per_middle.values() if m['n_grammar'] == 0)
    pure_grammar_middles = sum(1 for m in per_middle.values() if m['n_ht'] == 0)
    mixed_middles = len(per_middle) - pure_ht_middles - pure_grammar_middles

    # Matched-PP comparison
    mp_grammar = sum(1 for t in matched_pp_tokens if t['is_grammar'])
    mp_ht = len(matched_pp_tokens) - mp_grammar

    # Mean tokens per dark MIDDLE (validation of C1135's 5.7)
    token_counts = [len(tokens) for tokens in dark_middle_tokens.values()]
    mean_tokens = sum(token_counts) / len(token_counts) if token_counts else 0

    # Verdict
    if ht_frac > 0.90:
        verdict = 'CONFIRMED_HT_SUBSTRATE'
    elif ht_frac > 0.50:
        verdict = 'MIXED_PIPELINE'
    else:
        verdict = 'FALSIFIED'

    print(f"\nTest 1: Classification Trace")
    print(f"  Dark tokens: {len(dark_tokens)} (grammar={n_grammar}, HT/UN={n_ht})")
    print(f"  HT fraction: {ht_frac:.3f}")
    print(f"  Dark types: {len(dark_types)} (grammar={len(grammar_types)}, HT={len(ht_types)})")
    print(f"  Per-MIDDLE: {pure_ht_middles} pure-HT, {pure_grammar_middles} pure-grammar, {mixed_middles} mixed")
    print(f"  Mean tokens/MIDDLE: {mean_tokens:.1f} (C1135 baseline: 5.7)")
    print(f"  Matched-PP comparison: grammar={mp_grammar}, HT={mp_ht}")
    print(f"  Verdict: {verdict}")

    return {
        'n_dark_tokens': len(dark_tokens),
        'n_grammar': n_grammar,
        'n_ht_un': n_ht,
        'grammar_fraction': grammar_frac,
        'ht_fraction': ht_frac,
        'n_dark_word_types': len(dark_types),
        'n_grammar_types': len(grammar_types),
        'n_ht_types': len(ht_types),
        'n_dark_middles_with_tokens': len(per_middle),
        'pure_ht_middles': pure_ht_middles,
        'pure_grammar_middles': pure_grammar_middles,
        'mixed_middles': mixed_middles,
        'mean_tokens_per_middle': mean_tokens,
        'c1135_baseline_mean': 5.7,
        'matched_pp_comparison': {
            'n_tokens': len(matched_pp_tokens),
            'n_grammar': mp_grammar,
            'n_ht': mp_ht,
            'grammar_fraction': mp_grammar / len(matched_pp_tokens) if matched_pp_tokens else 0,
        },
        'verdict': verdict,
    }


# --- Test 2: Construction Grammar ---

def test2_construction_grammar(data):
    """PREFIX/SUFFIX/ARTICULATOR analysis for dark-pipeline tokens."""
    dark_tokens = data['dark_tokens']
    ht_tokens = data['ht_tokens']
    grammar_tokens = data['grammar_tokens']

    if not dark_tokens:
        return {'verdict': 'NO_DATA'}

    def prefix_profile(tokens):
        """Classify prefixes into grammar_standard / extended / no_prefix."""
        gs = 0
        ext = 0
        no_pfx = 0
        prefix_counts = Counter()
        suffix_count = 0
        artic_count = 0

        for t in tokens:
            pfx = t['prefix']
            if pfx is None:
                no_pfx += 1
            elif pfx in GRAMMAR_STANDARD:
                gs += 1
                prefix_counts[pfx] += 1
            elif pfx in EXTENDED_SET:
                ext += 1
                prefix_counts[pfx] += 1
            else:
                # Prefix extracted but not in either known set
                ext += 1
                prefix_counts[pfx] += 1

            if t['suffix'] is not None:
                suffix_count += 1
            if t['articulator'] is not None:
                artic_count += 1

        total = len(tokens)
        return {
            'grammar_standard': {'count': gs, 'fraction': gs / total if total else 0},
            'extended': {'count': ext, 'fraction': ext / total if total else 0},
            'no_prefix': {'count': no_pfx, 'fraction': no_pfx / total if total else 0},
            'suffix_rate': suffix_count / total if total else 0,
            'articulator_rate': artic_count / total if total else 0,
            'top_prefixes': dict(prefix_counts.most_common(15)),
            'total': total,
        }

    dark_profile = prefix_profile(dark_tokens)
    ht_profile = prefix_profile(ht_tokens)
    grammar_profile = prefix_profile(grammar_tokens)

    # Bifurcation analysis: compare dark vs general HT ratios
    dark_gs_frac = dark_profile['grammar_standard']['fraction']
    dark_ext_frac = dark_profile['extended']['fraction']
    ht_gs_frac = ht_profile['grammar_standard']['fraction']
    ht_ext_frac = ht_profile['extended']['fraction']

    # Ratio of grammar-standard to extended in each population
    dark_ratio = dark_gs_frac / dark_ext_frac if dark_ext_frac > 0 else float('inf')
    ht_ratio = ht_gs_frac / ht_ext_frac if ht_ext_frac > 0 else float('inf')

    # Significant difference?  If ratio differs by >50%, consider bifurcation
    if dark_ratio != float('inf') and ht_ratio != float('inf'):
        ratio_diff = abs(dark_ratio - ht_ratio) / ht_ratio if ht_ratio > 0 else 0
    else:
        ratio_diff = 0

    if ratio_diff > 0.50:
        verdict = 'DUAL_CONSTRUCTION'
    elif dark_profile['grammar_standard']['fraction'] > 0.70:
        verdict = 'GRAMMAR_CONSTRUCTION'
    else:
        verdict = 'HT_CONSISTENT'

    print(f"\nTest 2: Construction Grammar")
    print(f"  Dark PREFIX: grammar_standard={dark_profile['grammar_standard']['fraction']:.3f}, "
          f"extended={dark_profile['extended']['fraction']:.3f}, "
          f"no_prefix={dark_profile['no_prefix']['fraction']:.3f}")
    print(f"  HT baseline: grammar_standard={ht_profile['grammar_standard']['fraction']:.3f}, "
          f"extended={ht_profile['extended']['fraction']:.3f}")
    print(f"  Grammar baseline: grammar_standard={grammar_profile['grammar_standard']['fraction']:.3f}, "
          f"extended={grammar_profile['extended']['fraction']:.3f}")
    print(f"  Suffix rate: dark={dark_profile['suffix_rate']:.3f} "
          f"(HT baseline 0.773, grammar baseline 0.387)")
    print(f"  Articulator rate: dark={dark_profile['articulator_rate']:.3f} "
          f"(HT baseline 0.101, grammar baseline 0.019)")
    print(f"  GS/EXT ratio: dark={dark_ratio:.2f}, HT={ht_ratio:.2f}, "
          f"diff={ratio_diff:.2f}")
    print(f"  Verdict: {verdict}")

    return {
        'dark_pipeline': dark_profile,
        'ht_baseline': ht_profile,
        'grammar_baseline': grammar_profile,
        'bifurcation_analysis': {
            'dark_gs_ext_ratio': dark_ratio if dark_ratio != float('inf') else 'inf',
            'ht_gs_ext_ratio': ht_ratio if ht_ratio != float('inf') else 'inf',
            'ratio_difference': ratio_diff,
            'threshold': 0.50,
        },
        'c610_baselines': {
            'ht_suffix_rate': 0.773,
            'ht_articulator_rate': 0.101,
            'grammar_suffix_rate': 0.387,
            'grammar_articulator_rate': 0.019,
        },
        'verdict': verdict,
    }


# --- Test 3: Bridge Overlap ---

def test3_bridge_overlap(data):
    """Set intersection of 300 dark-pipeline MIDDLEs with 85 bridge MIDDLEs."""
    dark_set = data['dark_pipeline_set']
    bridge_set = data['bridge_set']
    middle_b_freq = data['middle_b_freq']
    middle_section_freq = data['middle_section_freq']

    overlap = dark_set & bridge_set
    dark_only = dark_set - bridge_set
    bridge_only = bridge_set - dark_set

    overlap_frac_dark = len(overlap) / len(dark_set) if dark_set else 0
    overlap_frac_bridge = len(overlap) / len(bridge_set) if bridge_set else 0

    # Structural comparison: mean B frequency and Herfindahl
    def population_stats(middles):
        freqs = [middle_b_freq.get(m, 0) for m in middles]
        herfs = []
        for m in middles:
            sec_counts = middle_section_freq.get(m, Counter())
            if sum(sec_counts.values()) > 0:
                herfs.append(herfindahl(sec_counts))
        return {
            'count': len(middles),
            'mean_b_freq': sum(freqs) / len(freqs) if freqs else 0,
            'median_b_freq': sorted(freqs)[len(freqs) // 2] if freqs else 0,
            'mean_herfindahl': sum(herfs) / len(herfs) if herfs else 0,
        }

    overlap_stats = population_stats(overlap)
    dark_only_stats = population_stats(dark_only)

    # Verdict
    if overlap_frac_dark > 0.20:
        verdict = 'BRIDGE_INTEGRATED'
    elif overlap_frac_dark > 0.05:
        verdict = 'PARTIAL_OVERLAP'
    else:
        verdict = 'BRIDGE_DISJOINT'

    print(f"\nTest 3: Bridge Overlap")
    print(f"  Overlap: {len(overlap)}/{len(dark_set)} dark-pipeline MIDDLEs "
          f"({overlap_frac_dark:.3f} of dark, {overlap_frac_bridge:.3f} of bridges)")
    print(f"  Dark-only: {len(dark_only)}, Bridge-only: {len(bridge_only)}")
    print(f"  Overlap mean freq: {overlap_stats['mean_b_freq']:.1f}, "
          f"dark-only mean freq: {dark_only_stats['mean_b_freq']:.1f}")
    print(f"  Overlap mean Herf: {overlap_stats['mean_herfindahl']:.3f}, "
          f"dark-only mean Herf: {dark_only_stats['mean_herfindahl']:.3f}")
    print(f"  Overlap MIDDLEs: {sorted(overlap)}")
    print(f"  Verdict: {verdict}")

    return {
        'n_overlap': len(overlap),
        'overlap_middles': sorted(overlap),
        'overlap_fraction_of_dark': overlap_frac_dark,
        'overlap_fraction_of_bridges': overlap_frac_bridge,
        'n_dark_only': len(dark_only),
        'n_bridge_only': len(bridge_only),
        'overlap_stats': overlap_stats,
        'dark_only_stats': dark_only_stats,
        'verdict': verdict,
    }


# --- Test 4: Paragraph Position ---

def test4_paragraph_position(data):
    """Line-1 and paragraph-line-1 concentration for dark-pipeline tokens."""
    dark_tokens = data['dark_tokens']
    ht_tokens = data['ht_tokens']
    grammar_tokens = data['grammar_tokens']
    matched_pp_tokens = data['matched_pp_tokens']
    par_first_lines = data['par_first_lines']

    if not dark_tokens:
        return {'verdict': 'NO_DATA'}

    def position_rates(tokens, label):
        """Compute folio-line-1 and paragraph-line-1 rates."""
        n = len(tokens)
        if n == 0:
            return {'folio_line1_rate': 0, 'par_line1_rate': 0, 'n': 0}

        folio_l1 = sum(1 for t in tokens if t['is_line1'])
        par_l1 = sum(1 for t in tokens
                     if (t['folio'], t['line']) in par_first_lines)

        return {
            'folio_line1_rate': folio_l1 / n,
            'par_line1_rate': par_l1 / n,
            'n': n,
            'folio_line1_count': folio_l1,
            'par_line1_count': par_l1,
        }

    dark_pos = position_rates(dark_tokens, 'dark')
    ht_pos = position_rates(ht_tokens, 'ht')
    grammar_pos = position_rates(grammar_tokens, 'grammar')
    matched_pos = position_rates(matched_pp_tokens, 'matched_pp')

    # Comparison: is dark-pipeline MORE concentrated on line-1 than general HT?
    dark_fl1 = dark_pos['folio_line1_rate']
    ht_fl1 = ht_pos['folio_line1_rate']
    delta_fl1 = dark_fl1 - ht_fl1

    dark_pl1 = dark_pos['par_line1_rate']
    ht_pl1 = ht_pos['par_line1_rate']
    delta_pl1 = dark_pl1 - ht_pl1

    # Verdict based on folio-line-1 comparison
    if delta_fl1 > 0.05:
        verdict = 'HEADER_ENRICHED'
    elif delta_fl1 < -0.05:
        verdict = 'BODY_ENRICHED'
    else:
        verdict = 'HEADER_NEUTRAL'

    print(f"\nTest 4: Paragraph Position")
    print(f"  Folio line-1 rate: dark={dark_fl1:.3f}, HT={ht_fl1:.3f}, "
          f"grammar={grammar_pos['folio_line1_rate']:.3f}, "
          f"matched_pp={matched_pos['folio_line1_rate']:.3f}")
    print(f"  Delta (dark - HT): {delta_fl1:+.3f}")
    print(f"  Par line-1 rate: dark={dark_pl1:.3f}, HT={ht_pl1:.3f}")
    print(f"  Delta (dark - HT): {delta_pl1:+.3f}")
    print(f"  C747 baseline: HT line-1 fraction of line-1 tokens = 0.502")
    print(f"  Verdict: {verdict}")

    return {
        'dark': dark_pos,
        'ht': ht_pos,
        'grammar': grammar_pos,
        'matched_pp': matched_pos,
        'delta_folio_line1': delta_fl1,
        'delta_par_line1': delta_pl1,
        'c747_baseline': 0.502,
        'c842_baseline': 0.452,
        'verdict': verdict,
    }


# --- Test 5: Section Profile ---

def test5_section_profile(data):
    """Section distribution comparison via JS divergence."""
    dark_section = data['dark_section']
    ht_section = data['ht_section']
    grammar_section = data['grammar_section']

    if sum(dark_section.values()) == 0:
        return {'verdict': 'NO_DATA'}

    # Normalize to fractions for display
    def normalize(counts):
        total = sum(counts.values())
        return {k: v / total for k, v in counts.items()} if total else {}

    dark_profile = normalize(dark_section)
    ht_profile = normalize(ht_section)
    grammar_profile = normalize(grammar_section)

    # Pairwise JS divergences
    js_dark_ht = jensen_shannon(dark_section, ht_section)
    js_dark_grammar = jensen_shannon(dark_section, grammar_section)
    js_ht_grammar = jensen_shannon(ht_section, grammar_section)

    # Token-level Herfindahl for dark pipeline
    dark_herf = herfindahl(dark_section)

    # Verdict
    if js_dark_ht < js_dark_grammar * 0.5:
        verdict = 'HT_ALIGNED'
    elif js_dark_grammar < js_dark_ht * 0.5:
        verdict = 'GRAMMAR_ALIGNED'
    else:
        verdict = 'INDEPENDENT_DISTRIBUTION'

    print(f"\nTest 5: Section Profile")
    print(f"  Dark profile: {dict(sorted(dark_profile.items()))}")
    print(f"  HT profile:   {dict(sorted(ht_profile.items()))}")
    print(f"  Grammar profile: {dict(sorted(grammar_profile.items()))}")
    print(f"  JS(dark,HT)={js_dark_ht:.4f}, JS(dark,grammar)={js_dark_grammar:.4f}, "
          f"JS(HT,grammar)={js_ht_grammar:.4f}")
    print(f"  Token-level Herfindahl: {dark_herf:.4f} "
          f"(C1135 MIDDLE-level: 0.716)")
    print(f"  Verdict: {verdict}")

    return {
        'dark_section_profile': dark_profile,
        'ht_section_profile': ht_profile,
        'grammar_section_profile': grammar_profile,
        'js_dark_vs_ht': js_dark_ht,
        'js_dark_vs_grammar': js_dark_grammar,
        'js_ht_vs_grammar': js_ht_grammar,
        'token_level_herfindahl': dark_herf,
        'c1135_middle_level_herfindahl': 0.716,
        'verdict': verdict,
    }


# --- Synthesis ---

def synthesize(results):
    """Combine all test verdicts into an overall assessment."""
    verdicts = {
        'test1': results['test1']['verdict'],
        'test2': results['test2']['verdict'],
        'test3': results['test3']['verdict'],
        'test4': results['test4']['verdict'],
        'test5': results['test5']['verdict'],
    }

    # Overall summary
    t1 = verdicts['test1']
    t2 = verdicts['test2']
    t3 = verdicts['test3']

    if t1 == 'CONFIRMED_HT_SUBSTRATE' and t2 == 'HT_CONSISTENT':
        overall = 'STANDARD_HT_SUBSTRATE'
        summary = ('Dark pipeline MIDDLEs produce standard HT/UN tokens with '
                   'the same construction grammar as general HT vocabulary.')
    elif t1 == 'CONFIRMED_HT_SUBSTRATE' and t2 == 'DUAL_CONSTRUCTION':
        overall = 'HT_WITH_DISTINCT_CONSTRUCTION'
        summary = ('Dark pipeline MIDDLEs produce HT/UN tokens but with a '
                   'different PREFIX distribution than general HT -- distinct '
                   'construction grammar for this population.')
    elif t1 == 'MIXED_PIPELINE':
        overall = 'DUAL_FUNCTION_PIPELINE'
        summary = ('Dark pipeline MIDDLEs produce BOTH grammar-classified and '
                   'HT/UN tokens -- the pipeline serves two structural functions.')
    elif t1 == 'FALSIFIED':
        overall = 'HYPOTHESIS_FALSIFIED'
        summary = ('Dark pipeline MIDDLEs mostly produce grammar-classified tokens, '
                   'not HT/UN. The HT substrate hypothesis is falsified.')
    else:
        overall = 'UNRESOLVED'
        summary = 'Could not synthesize a clear verdict from the test results.'

    # Append bridge finding
    if t3 == 'BRIDGE_INTEGRATED':
        summary += (' Bridge overlap is substantial -- dark pipeline and manifold '
                    'backbone share vocabulary.')
    elif t3 == 'BRIDGE_DISJOINT':
        summary += (' Bridge overlap is minimal -- dark pipeline and manifold '
                    'backbone are separate populations.')

    verdicts['overall'] = overall
    verdicts['summary'] = summary

    print(f"\n{'='*60}")
    print(f"OVERALL VERDICT: {overall}")
    print(f"  {summary}")
    print(f"{'='*60}")

    return verdicts


# --- Main ---

def main():
    print("Phase 407: Dark Pipeline Functional Test")
    print("=" * 50)

    data = load_data()

    # Validation
    print(f"\nValidation:")
    print(f"  Dark pipeline MIDDLEs: {len(data['dark_pipeline_set'])} (expect 300)")
    print(f"  Matched PP MIDDLEs: {len(data['matched_pp_set'])} (expect 89)")
    print(f"  Bridge MIDDLEs: {len(data['bridge_set'])} (expect 85)")
    print(f"  Classified tokens: {len(data['classified_set'])} (expect 480)")
    print(f"  B tokens scanned: {data['n_scanned']} (expect ~23243)")

    results = {}
    results['test1'] = test1_classification_trace(data)
    results['test2'] = test2_construction_grammar(data)
    results['test3'] = test3_bridge_overlap(data)
    results['test4'] = test4_paragraph_position(data)
    results['test5'] = test5_section_profile(data)
    results['verdicts'] = synthesize(results)

    results['metadata'] = {
        'phase': 'DARK_PIPELINE_FUNCTIONAL_TEST',
        'phase_number': 407,
        'script': 'dark_pipeline_test.py',
        'n_dark_pipeline_middles': len(data['dark_pipeline_set']),
        'n_matched_pp_middles': len(data['matched_pp_set']),
        'n_bridge_middles': len(data['bridge_set']),
        'n_classified_tokens': len(data['classified_set']),
        'n_b_tokens_scanned': data['n_scanned'],
    }

    # Write output
    out_dir = ROOT / 'phases/DARK_PIPELINE_FUNCTIONAL_TEST/results'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'dark_pipeline_test.json'

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to {out_path}")
    size = out_path.stat().st_size
    print(f"Output size: {size:,} bytes")


if __name__ == '__main__':
    main()
