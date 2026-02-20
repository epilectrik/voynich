"""Phase 406: Cross-System Vocabulary Flow — 6-test battery.

Core question: How does section-UNIVERSAL pipeline vocabulary (C1049: Herfindahl 0.701)
produce section-SPECIFIC B execution output (C909: 96% section-specific)?

Tier A: Section-specificity mechanism
  A1: Frequency modulation test
  A2: Specificity source decomposition

Tier B: Pipeline population characterization
  B1: Unmatched PP characterization (dark matter)
  B2: A-section -> B vocabulary routing

Tier C: Flow architecture
  C1: A-folio -> B-folio coverage matrix
  C2: Pipeline sufficiency / bottleneck
"""

import json
import sys
import math
import os
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, load_middle_classes, MiddleAnalyzer


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def round_floats(obj, digits=4):
    """Recursively round floats in nested structures."""
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(x, digits) for x in obj]
    return obj


def shannon_entropy(counts):
    """Shannon entropy in bits from a dict/Counter of counts."""
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
    """Jensen-Shannon divergence (base 2) between two count dicts."""
    all_keys = set(p_counts) | set(q_counts)
    p_total = sum(p_counts.values())
    q_total = sum(q_counts.values())
    if p_total == 0 or q_total == 0:
        return float('nan')

    js = 0.0
    for k in all_keys:
        p = p_counts.get(k, 0) / p_total
        q = q_counts.get(k, 0) / q_total
        m = (p + q) / 2
        if p > 0 and m > 0:
            js += p * math.log2(p / m)
        if q > 0 and m > 0:
            js += q * math.log2(q / m)
    return js / 2


def jaccard(set_a, set_b):
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union > 0 else 0.0


def herfindahl(counts):
    """Herfindahl-Hirschman Index from a dict of counts. 1/N = uniform, 1.0 = monopoly."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return sum((c / total) ** 2 for c in counts.values())


def cosine_sim(vec_a, vec_b):
    """Cosine similarity between two dicts (sparse vectors)."""
    keys = set(vec_a) | set(vec_b)
    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in keys)
    mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data():
    """Load all data needed for the 6-test battery."""
    tx = Transcript()
    morph = Morphology()

    # Canonical PP/RI split
    ri_middles, pp_middles = load_middle_classes()
    ri_set = set(ri_middles)
    pp_set = set(pp_middles)

    # Bridge MIDDLEs
    bridge_path = ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(bridge_path) as f:
        bridge_data = json.load(f)
    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])

    # Class/role mapping
    class_map_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        cm = json.load(f)
    token_to_class = cm['token_to_class']
    token_to_role = cm['token_to_role']
    class_to_role = cm['class_to_role']

    # PP role foundation (matched vs unmatched)
    pp_role_path = ROOT / 'phases' / 'A_TO_B_ROLE_PROJECTION' / 'results' / 'pp_role_foundation.json'
    with open(pp_role_path) as f:
        pp_role_data = json.load(f)
    pp_role_map = pp_role_data['pp_role_map']

    matched_pp = set()
    unmatched_pp = set()
    for mid, info in pp_role_map.items():
        if info['n_classes'] > 0:
            matched_pp.add(mid)
        else:
            unmatched_pp.add(mid)

    # Regime mapping
    regime_path = ROOT / 'data' / 'regime_folio_mapping.json'
    with open(regime_path) as f:
        regime_data = json.load(f)
    folio_regime = {f: info['regime'] for f, info in regime_data['regime_assignments'].items()}

    # Build per-folio and per-section data for A and B
    # A side
    a_folio_middles = defaultdict(set)
    a_folio_mid_freq = defaultdict(lambda: defaultdict(int))
    a_folio_section = {}
    a_section_mid_freq = defaultdict(lambda: defaultdict(int))
    a_folio_tokens = defaultdict(int)

    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m and m.middle:
            a_folio_middles[token.folio].add(m.middle)
            a_folio_mid_freq[token.folio][m.middle] += 1
            a_section_mid_freq[token.section][m.middle] += 1
            a_folio_section[token.folio] = token.section
            a_folio_tokens[token.folio] += 1

    # B side
    b_folio_middles = defaultdict(set)
    b_folio_mid_freq = defaultdict(lambda: defaultdict(int))
    b_folio_section = {}
    b_section_mid_freq = defaultdict(lambda: defaultdict(int))
    b_section_middles = defaultdict(set)
    b_folio_tokens = defaultdict(int)

    # Also track full tokens per MIDDLE in B (for B1 context analysis)
    b_middle_tokens = defaultdict(set)  # middle -> set of full tokens
    b_middle_section_freq = defaultdict(lambda: defaultdict(int))  # middle -> {section: count}
    b_middle_folio_set = defaultdict(set)  # middle -> set of folios

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m and m.middle:
            mid = m.middle
            b_folio_middles[token.folio].add(mid)
            b_folio_mid_freq[token.folio][mid] += 1
            b_section_mid_freq[token.section][mid] += 1
            b_section_middles[token.section].add(mid)
            b_folio_section[token.folio] = token.section
            b_folio_tokens[token.folio] += 1
            b_middle_tokens[mid].add(word)
            b_middle_section_freq[mid][token.section] += 1
            b_middle_folio_set[mid].add(token.folio)

    # Compute B-exclusive MIDDLEs (appear in B but not A)
    all_a_middles = set()
    for mids in a_folio_middles.values():
        all_a_middles.update(mids)
    all_b_middles = set()
    for mids in b_folio_middles.values():
        all_b_middles.update(mids)
    b_exclusive_middles = all_b_middles - all_a_middles

    # Major B sections (with enough statistical power)
    b_sections_sorted = sorted(b_section_middles.keys(),
                               key=lambda s: sum(b_section_mid_freq[s].values()),
                               reverse=True)

    data = {
        'tx': tx, 'morph': morph,
        'ri_set': ri_set, 'pp_set': pp_set,
        'bridge_set': bridge_set,
        'token_to_class': token_to_class,
        'token_to_role': token_to_role,
        'class_to_role': class_to_role,
        'pp_role_map': pp_role_map,
        'matched_pp': matched_pp, 'unmatched_pp': unmatched_pp,
        'folio_regime': folio_regime,
        # A side
        'a_folio_middles': dict(a_folio_middles),
        'a_folio_mid_freq': {f: dict(d) for f, d in a_folio_mid_freq.items()},
        'a_folio_section': a_folio_section,
        'a_section_mid_freq': {s: dict(d) for s, d in a_section_mid_freq.items()},
        'a_folio_tokens': dict(a_folio_tokens),
        'all_a_middles': all_a_middles,
        # B side
        'b_folio_middles': dict(b_folio_middles),
        'b_folio_mid_freq': {f: dict(d) for f, d in b_folio_mid_freq.items()},
        'b_folio_section': b_folio_section,
        'b_section_mid_freq': {s: dict(d) for s, d in b_section_mid_freq.items()},
        'b_section_middles': {s: mids for s, mids in b_section_middles.items()},
        'b_folio_tokens': dict(b_folio_tokens),
        'all_b_middles': all_b_middles,
        'b_exclusive_middles': b_exclusive_middles,
        'b_middle_tokens': {m: list(toks) for m, toks in b_middle_tokens.items()},
        'b_middle_section_freq': {m: dict(d) for m, d in b_middle_section_freq.items()},
        'b_middle_folio_set': {m: fols for m, fols in b_middle_folio_set.items()},
        'b_sections_sorted': b_sections_sorted,
    }

    # Validation
    n_a_folios = len(a_folio_middles)
    n_b_folios = len(b_folio_middles)
    a_sections = Counter(a_folio_section.values())
    b_sections = Counter(b_folio_section.values())
    total_b_tokens = sum(b_folio_tokens.values())

    print(f"A folios: {n_a_folios}, B folios: {n_b_folios}")
    print(f"A sections: {dict(a_sections)}")
    print(f"B sections: {dict(b_sections)}")
    print(f"PP: {len(pp_set)}, RI: {len(ri_set)}, Bridge: {len(bridge_set)}")
    print(f"Matched PP: {len(matched_pp)}, Unmatched PP: {len(unmatched_pp)}")
    print(f"B-exclusive MIDDLEs: {len(b_exclusive_middles)}")
    print(f"All A MIDDLEs: {len(all_a_middles)}, All B MIDDLEs: {len(all_b_middles)}")
    print(f"Total B tokens: {total_b_tokens}")

    data['validation'] = {
        'n_a_folios': n_a_folios,
        'n_b_folios': n_b_folios,
        'a_sections': dict(a_sections),
        'b_sections': dict(b_sections),
        'n_pp': len(pp_set),
        'n_ri': len(ri_set),
        'n_bridge': len(bridge_set),
        'n_matched_pp': len(matched_pp),
        'n_unmatched_pp': len(unmatched_pp),
        'n_b_exclusive': len(b_exclusive_middles),
        'n_all_a_middles': len(all_a_middles),
        'n_all_b_middles': len(all_b_middles),
        'total_b_tokens': total_b_tokens,
    }

    return data


# ---------------------------------------------------------------------------
# Tier A: Section-Specificity Mechanism
# ---------------------------------------------------------------------------

def a1_frequency_modulation(data):
    """Test whether section-specificity comes from frequency modulation of shared vocabulary.

    Compare section discrimination using:
    (a) Binary presence/absence only (mean pairwise Jaccard complement)
    (b) Frequency-weighted profiles (mean pairwise JS divergence)
    """
    print("\n=== A1: Frequency Modulation Test ===")

    b_section_mid_freq = data['b_section_mid_freq']
    pp_set = data['pp_set']
    b_exclusive_middles = data['b_exclusive_middles']

    # Use sections with substantial token counts (>1000 tokens)
    major_sections = []
    for sec in data['b_sections_sorted']:
        total = sum(b_section_mid_freq[sec].values())
        if total >= 1000:
            major_sections.append(sec)
    print(f"Major B sections (>=1000 tokens): {major_sections}")

    # Build per-section MIDDLE sets and frequency profiles, split by vocabulary partition
    section_pp_sets = {}
    section_pp_freq = {}
    section_bexcl_sets = {}
    section_bexcl_freq = {}
    section_all_freq = {}

    for sec in major_sections:
        freq = b_section_mid_freq[sec]
        # PP partition
        pp_freq = {m: c for m, c in freq.items() if m in pp_set}
        section_pp_sets[sec] = set(pp_freq.keys())
        section_pp_freq[sec] = pp_freq
        # B-exclusive partition
        bx_freq = {m: c for m, c in freq.items() if m in b_exclusive_middles}
        section_bexcl_sets[sec] = set(bx_freq.keys())
        section_bexcl_freq[sec] = bx_freq
        # All
        section_all_freq[sec] = freq

    # Pairwise comparison: presence/absence (1-Jaccard) vs JS divergence
    pairs = []
    for i in range(len(major_sections)):
        for j in range(i + 1, len(major_sections)):
            s1, s2 = major_sections[i], major_sections[j]
            pair_name = f"{s1}-{s2}"

            # PP: presence/absence
            pp_jac = jaccard(section_pp_sets[s1], section_pp_sets[s2])
            # PP: frequency-weighted JS
            pp_js = jensen_shannon(section_pp_freq[s1], section_pp_freq[s2])

            # B-exclusive: presence/absence
            bx_jac = jaccard(section_bexcl_sets[s1], section_bexcl_sets[s2])
            # B-exclusive: frequency-weighted JS
            bx_js = jensen_shannon(section_bexcl_freq[s1], section_bexcl_freq[s2])

            # All: JS
            all_js = jensen_shannon(section_all_freq[s1], section_all_freq[s2])

            pairs.append({
                'pair': pair_name,
                'pp_jaccard': pp_jac,
                'pp_jaccard_distance': 1 - pp_jac,
                'pp_js': pp_js,
                'bexcl_jaccard': bx_jac,
                'bexcl_jaccard_distance': 1 - bx_jac,
                'bexcl_js': bx_js,
                'all_js': all_js,
            })
            print(f"  {pair_name}: PP Jaccard={pp_jac:.3f} PP JS={pp_js:.4f} | "
                  f"B-excl Jaccard={bx_jac:.3f} B-excl JS={bx_js:.4f} | All JS={all_js:.4f}")

    # Summary statistics
    mean_pp_jac_dist = sum(p['pp_jaccard_distance'] for p in pairs) / len(pairs)
    mean_pp_js = sum(p['pp_js'] for p in pairs) / len(pairs)
    mean_bx_jac_dist = sum(p['bexcl_jaccard_distance'] for p in pairs) / len(pairs)
    mean_bx_js = sum(p['bexcl_js'] for p in pairs) / len(pairs)
    mean_all_js = sum(p['all_js'] for p in pairs) / len(pairs)

    # Frequency modulation ratio: how much more discriminating is JS than Jaccard distance?
    # Higher ratio = frequency adds more information beyond presence/absence
    # Normalize: JS/Jaccard_distance for PP
    freq_mod_ratios = []
    for p in pairs:
        if p['pp_jaccard_distance'] > 0.001:
            freq_mod_ratios.append(p['pp_js'] / p['pp_jaccard_distance'])
    mean_freq_mod_ratio = sum(freq_mod_ratios) / len(freq_mod_ratios) if freq_mod_ratios else 0

    # Section vocabulary sizes
    section_sizes = {}
    for sec in major_sections:
        section_sizes[sec] = {
            'pp_types': len(section_pp_sets[sec]),
            'bexcl_types': len(section_bexcl_sets[sec]),
            'total_types': len(set(section_all_freq[sec].keys())),
            'pp_tokens': sum(section_pp_freq[sec].values()),
            'bexcl_tokens': sum(section_bexcl_freq[sec].values()),
            'total_tokens': sum(section_all_freq[sec].values()),
            'pp_token_fraction': sum(section_pp_freq[sec].values()) / max(1, sum(section_all_freq[sec].values())),
        }

    result = {
        'major_sections': major_sections,
        'section_sizes': section_sizes,
        'pairwise': pairs,
        'mean_pp_jaccard_distance': mean_pp_jac_dist,
        'mean_pp_js': mean_pp_js,
        'mean_bexcl_jaccard_distance': mean_bx_jac_dist,
        'mean_bexcl_js': mean_bx_js,
        'mean_all_js': mean_all_js,
        'mean_freq_modulation_ratio': mean_freq_mod_ratio,
    }

    print(f"\nMean PP Jaccard distance: {mean_pp_jac_dist:.4f}")
    print(f"Mean PP JS divergence:   {mean_pp_js:.4f}")
    print(f"Mean B-excl Jaccard dist: {mean_bx_jac_dist:.4f}")
    print(f"Mean B-excl JS divergence: {mean_bx_js:.4f}")
    print(f"Mean all JS divergence:  {mean_all_js:.4f}")
    print(f"Frequency modulation ratio (PP JS/Jaccard_dist): {mean_freq_mod_ratio:.4f}")

    return result


def a2_specificity_source_decomposition(data):
    """Decompose section-specificity: how much comes from shared vs B-exclusive vocabulary?

    For each section pair, compute JS divergence using:
    (a) ONLY shared/PP MIDDLE frequencies
    (b) ONLY B-exclusive MIDDLE frequencies
    (c) ALL MIDDLE frequencies
    Then compute what fraction of total divergence each source contributes.
    """
    print("\n=== A2: Specificity Source Decomposition ===")

    b_section_mid_freq = data['b_section_mid_freq']
    pp_set = data['pp_set']
    b_exclusive_middles = data['b_exclusive_middles']

    # Major sections
    major_sections = []
    for sec in data['b_sections_sorted']:
        total = sum(b_section_mid_freq[sec].values())
        if total >= 1000:
            major_sections.append(sec)

    decomposition = []
    for i in range(len(major_sections)):
        for j in range(i + 1, len(major_sections)):
            s1, s2 = major_sections[i], major_sections[j]

            freq1 = b_section_mid_freq[s1]
            freq2 = b_section_mid_freq[s2]

            # Partition into shared and B-exclusive
            pp_freq1 = {m: c for m, c in freq1.items() if m in pp_set}
            pp_freq2 = {m: c for m, c in freq2.items() if m in pp_set}
            bx_freq1 = {m: c for m, c in freq1.items() if m in b_exclusive_middles}
            bx_freq2 = {m: c for m, c in freq2.items() if m in b_exclusive_middles}
            # "Other" = neither PP nor B-exclusive (could be A-exclusive MIDDLEs appearing in B)
            other_freq1 = {m: c for m, c in freq1.items() if m not in pp_set and m not in b_exclusive_middles}
            other_freq2 = {m: c for m, c in freq2.items() if m not in pp_set and m not in b_exclusive_middles}

            js_pp = jensen_shannon(pp_freq1, pp_freq2)
            js_bx = jensen_shannon(bx_freq1, bx_freq2)
            js_all = jensen_shannon(freq1, freq2)
            js_other = jensen_shannon(other_freq1, other_freq2) if other_freq1 and other_freq2 else 0.0

            # Token-weighted contribution: weight each partition's JS by its share of tokens
            total_tokens = sum(freq1.values()) + sum(freq2.values())
            pp_tokens = sum(pp_freq1.values()) + sum(pp_freq2.values())
            bx_tokens = sum(bx_freq1.values()) + sum(bx_freq2.values())
            other_tokens = sum(other_freq1.values()) + sum(other_freq2.values())

            pp_token_share = pp_tokens / total_tokens if total_tokens > 0 else 0
            bx_token_share = bx_tokens / total_tokens if total_tokens > 0 else 0

            # Weighted JS contribution (approximate decomposition)
            # JS(all) ≈ pp_share * JS(pp) + bx_share * JS(bx) + other_share * JS(other) + mixing term
            weighted_pp = pp_token_share * js_pp if not math.isnan(js_pp) else 0
            weighted_bx = bx_token_share * js_bx if not math.isnan(js_bx) else 0

            entry = {
                'pair': f"{s1}-{s2}",
                'js_pp': js_pp,
                'js_bexcl': js_bx,
                'js_all': js_all,
                'js_other': js_other,
                'pp_token_share': pp_token_share,
                'bexcl_token_share': bx_token_share,
                'weighted_pp_contribution': weighted_pp,
                'weighted_bexcl_contribution': weighted_bx,
            }
            decomposition.append(entry)
            print(f"  {s1}-{s2}: JS(pp)={js_pp:.4f} JS(bexcl)={js_bx:.4f} JS(all)={js_all:.4f} "
                  f"| PP share={pp_token_share:.3f} B-excl share={bx_token_share:.3f}")

    # Mean contributions
    mean_js_pp = sum(d['js_pp'] for d in decomposition) / len(decomposition)
    mean_js_bx = sum(d['js_bexcl'] for d in decomposition) / len(decomposition)
    mean_js_all = sum(d['js_all'] for d in decomposition) / len(decomposition)
    mean_pp_share = sum(d['pp_token_share'] for d in decomposition) / len(decomposition)

    # Which partition is more discriminating per unit token?
    # PP per-token JS vs B-exclusive per-token JS
    pp_per_token_js = mean_js_pp  # already per-type, but within PP partition
    bx_per_token_js = mean_js_bx

    # Verdict component: what fraction of section discrimination comes from shared vocab?
    # Use ratio of within-partition JS divergences
    if mean_js_all > 0:
        pp_fraction = mean_js_pp / mean_js_all
        bx_fraction = mean_js_bx / mean_js_all
    else:
        pp_fraction = 0
        bx_fraction = 0

    result = {
        'decomposition': decomposition,
        'mean_js_pp': mean_js_pp,
        'mean_js_bexcl': mean_js_bx,
        'mean_js_all': mean_js_all,
        'mean_pp_token_share': mean_pp_share,
        'pp_js_fraction_of_all': pp_fraction,
        'bexcl_js_fraction_of_all': bx_fraction,
        'pp_per_token_discriminability': pp_per_token_js,
        'bexcl_per_token_discriminability': bx_per_token_js,
    }

    print(f"\nMean JS(PP): {mean_js_pp:.4f}, Mean JS(B-excl): {mean_js_bx:.4f}, Mean JS(all): {mean_js_all:.4f}")
    print(f"PP fraction of all JS: {pp_fraction:.3f}")
    print(f"B-excl fraction of all JS: {bx_fraction:.3f}")
    print(f"PP token share: {mean_pp_share:.3f}")

    return result


# ---------------------------------------------------------------------------
# Tier B: Pipeline Population Characterization
# ---------------------------------------------------------------------------

def b1_unmatched_pp_characterization(data):
    """Characterize the 315 unmatched PP MIDDLEs — the pipeline 'dark matter'.

    For each: B presence, token count, folio count, section distribution,
    compound status, Herfindahl concentration.
    """
    print("\n=== B1: Unmatched PP Characterization ===")

    unmatched_pp = data['unmatched_pp']
    matched_pp = data['matched_pp']
    b_middle_tokens = data['b_middle_tokens']
    b_middle_section_freq = data['b_middle_section_freq']
    b_middle_folio_set = data['b_middle_folio_set']
    pp_set = data['pp_set']

    # Build MiddleAnalyzer for compound detection
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # Classify each unmatched PP
    b_present = []
    b_absent = []

    for mid in sorted(unmatched_pp):
        b_tokens = b_middle_tokens.get(mid, [])
        b_sec_freq = b_middle_section_freq.get(mid, {})
        b_folios = b_middle_folio_set.get(mid, set())
        b_token_count = sum(b_sec_freq.values())

        is_compound = mid_analyzer.is_compound(mid)
        atoms = mid_analyzer.get_maximal_atoms(mid) if is_compound else []
        herf = herfindahl(b_sec_freq) if b_sec_freq else 0.0

        entry = {
            'middle': mid,
            'b_token_count': b_token_count,
            'b_folio_count': len(b_folios),
            'b_section_freq': b_sec_freq,
            'herfindahl': herf,
            'is_compound': is_compound,
            'compound_atoms': atoms,
            'char_length': len(mid),
            'n_b_token_types': len(b_tokens),
        }

        if b_token_count > 0:
            b_present.append(entry)
        else:
            b_absent.append(entry)

    # Similarly for matched PP (for comparison)
    matched_stats = []
    for mid in sorted(matched_pp):
        b_sec_freq = b_middle_section_freq.get(mid, {})
        b_folios = b_middle_folio_set.get(mid, set())
        b_token_count = sum(b_sec_freq.values())
        is_compound = mid_analyzer.is_compound(mid)
        herf = herfindahl(b_sec_freq) if b_sec_freq else 0.0

        matched_stats.append({
            'middle': mid,
            'b_token_count': b_token_count,
            'b_folio_count': len(b_folios),
            'herfindahl': herf,
            'is_compound': is_compound,
            'char_length': len(mid),
        })

    # Summary statistics
    def summarize(entries):
        if not entries:
            return {}
        return {
            'count': len(entries),
            'mean_b_tokens': sum(e['b_token_count'] for e in entries) / len(entries),
            'median_b_tokens': sorted(e['b_token_count'] for e in entries)[len(entries) // 2],
            'mean_b_folios': sum(e['b_folio_count'] for e in entries) / len(entries),
            'mean_herfindahl': sum(e['herfindahl'] for e in entries) / len(entries),
            'compound_rate': sum(1 for e in entries if e['is_compound']) / len(entries),
            'mean_char_length': sum(e['char_length'] for e in entries) / len(entries),
        }

    present_summary = summarize(b_present)
    absent_summary = summarize(b_absent)
    matched_summary = summarize(matched_stats)

    # Section concentration comparison
    present_universal = sum(1 for e in b_present if e['herfindahl'] < 0.5)
    present_concentrated = sum(1 for e in b_present if e['herfindahl'] >= 0.5)

    print(f"Unmatched PP: {len(unmatched_pp)} total")
    print(f"  B-present: {len(b_present)} ({len(b_present)/len(unmatched_pp)*100:.1f}%)")
    print(f"  B-absent:  {len(b_absent)} ({len(b_absent)/len(unmatched_pp)*100:.1f}%)")
    if present_summary:
        print(f"  B-present mean tokens: {present_summary['mean_b_tokens']:.1f}, "
              f"mean folios: {present_summary['mean_b_folios']:.1f}, "
              f"mean Herf: {present_summary['mean_herfindahl']:.3f}, "
              f"compound: {present_summary['compound_rate']:.3f}")
    if absent_summary:
        print(f"  B-absent mean char_length: {absent_summary['mean_char_length']:.1f}, "
              f"compound: {absent_summary['compound_rate']:.3f}")
    print(f"  B-present: {present_universal} universal (Herf<0.5), {present_concentrated} concentrated")
    print(f"Matched PP for comparison: mean tokens={matched_summary.get('mean_b_tokens', 0):.1f}, "
          f"mean folios={matched_summary.get('mean_b_folios', 0):.1f}, "
          f"mean Herf={matched_summary.get('mean_herfindahl', 0):.3f}")

    result = {
        'n_unmatched': len(unmatched_pp),
        'n_b_present': len(b_present),
        'n_b_absent': len(b_absent),
        'b_present_fraction': len(b_present) / len(unmatched_pp) if unmatched_pp else 0,
        'b_present_summary': present_summary,
        'b_absent_summary': absent_summary,
        'matched_pp_summary': matched_summary,
        'b_present_universal_count': present_universal,
        'b_present_concentrated_count': present_concentrated,
        # Top 20 most frequent B-present unmatched PPs
        'top_b_present': sorted(b_present, key=lambda e: -e['b_token_count'])[:20],
        # All B-absent PPs (should be small or zero — "shared" means appears in both)
        'b_absent_middles': [e['middle'] for e in b_absent],
    }

    return result


def b2_a_section_routing(data):
    """Test whether different vocabulary partitions are sourced from different A sections.

    A has 2 sections: H (herbal, ~95 folios) and P (pharmaceutical, ~16 folios).
    For each partition (bridge, matched-non-bridge, unmatched-PP, B-exclusive),
    compute A-H vs A-P prevalence.
    """
    print("\n=== B2: A-Section -> B Vocabulary Routing ===")

    a_section_mid_freq = data['a_section_mid_freq']
    pp_set = data['pp_set']
    bridge_set = data['bridge_set']
    matched_pp = data['matched_pp']
    unmatched_pp = data['unmatched_pp']
    b_exclusive_middles = data['b_exclusive_middles']
    all_a_middles = data['all_a_middles']

    # A sections available
    a_sections = sorted(a_section_mid_freq.keys())
    print(f"A sections: {a_sections}")
    for sec in a_sections:
        n_types = len(a_section_mid_freq[sec])
        n_tokens = sum(a_section_mid_freq[sec].values())
        print(f"  {sec}: {n_types} types, {n_tokens} tokens")

    # For each MIDDLE, compute A-section prevalence
    def a_section_profile(middles_set):
        """For a set of MIDDLEs, compute A-section distribution."""
        section_counts = defaultdict(int)
        present_in_a = 0
        for mid in middles_set:
            in_a = False
            for sec in a_sections:
                if mid in a_section_mid_freq[sec]:
                    section_counts[sec] += a_section_mid_freq[sec][mid]
                    in_a = True
            if in_a:
                present_in_a += 1

        total = sum(section_counts.values())
        fractions = {sec: section_counts[sec] / total if total > 0 else 0 for sec in a_sections}
        return {
            'n_in_set': len(middles_set),
            'n_present_in_a': present_in_a,
            'a_presence_rate': present_in_a / len(middles_set) if middles_set else 0,
            'section_token_counts': dict(section_counts),
            'section_token_fractions': fractions,
            'total_a_tokens': total,
        }

    # Define partitions
    classified_non_bridge = matched_pp - bridge_set
    partitions = {
        'bridge': bridge_set & pp_set,  # bridges that are PP (should be most/all)
        'classified_non_bridge': classified_non_bridge,
        'unmatched_pp': unmatched_pp,
        'b_exclusive': b_exclusive_middles,
    }

    results = {}
    for name, middles in partitions.items():
        profile = a_section_profile(middles)
        results[name] = profile
        fracs = profile['section_token_fractions']
        frac_str = ', '.join(f"{s}={fracs.get(s, 0):.3f}" for s in a_sections)
        print(f"  {name}: {profile['n_in_set']} MIDDLEs, "
              f"{profile['n_present_in_a']} in A ({profile['a_presence_rate']:.3f}), "
              f"A-section fractions: {frac_str}")

    # Also compute overall A-section distribution for comparison
    all_pp_profile = a_section_profile(pp_set)
    results['all_pp'] = all_pp_profile

    # Bridge A-section enrichment test:
    # Are A-P-enriched bridges in different B roles than A-H-enriched bridges?
    bridge_a_section_role = []
    pp_role_map = data['pp_role_map']
    for mid in bridge_set & pp_set:
        h_count = a_section_mid_freq.get('H', {}).get(mid, 0)
        p_count = a_section_mid_freq.get('P', {}).get(mid, 0)
        total = h_count + p_count
        if total == 0:
            continue
        h_frac = h_count / total
        role_info = pp_role_map.get(mid, {})
        dominant_role = role_info.get('dominant_role', 'UNKNOWN') if role_info else 'UNKNOWN'
        bridge_a_section_role.append({
            'middle': mid,
            'h_fraction': h_frac,
            'p_fraction': 1 - h_frac,
            'dominant_role': dominant_role,
        })

    # Group by A-section dominance
    h_dominant_bridges = [b for b in bridge_a_section_role if b['h_fraction'] > 0.7]
    p_enriched_bridges = [b for b in bridge_a_section_role if b['p_fraction'] > 0.3]
    h_roles = Counter(b['dominant_role'] for b in h_dominant_bridges)
    p_roles = Counter(b['dominant_role'] for b in p_enriched_bridges)

    results['bridge_a_section_role'] = {
        'n_bridges_with_a_data': len(bridge_a_section_role),
        'h_dominant_count': len(h_dominant_bridges),
        'p_enriched_count': len(p_enriched_bridges),
        'h_dominant_roles': dict(h_roles),
        'p_enriched_roles': dict(p_roles),
    }

    print(f"\nBridge A-section role analysis:")
    print(f"  H-dominant bridges (H>70%): {len(h_dominant_bridges)}, roles: {dict(h_roles)}")
    print(f"  P-enriched bridges (P>30%): {len(p_enriched_bridges)}, roles: {dict(p_roles)}")

    return results


# ---------------------------------------------------------------------------
# Tier C: Flow Architecture
# ---------------------------------------------------------------------------

def c1_folio_coverage_matrix(data):
    """Compute A-folio -> B-folio MIDDLE coverage matrix and test for cluster structure."""
    print("\n=== C1: A-Folio -> B-Folio Coverage Matrix ===")

    a_folio_middles = data['a_folio_middles']
    b_folio_middles = data['b_folio_middles']
    pp_set = data['pp_set']
    a_folio_section = data['a_folio_section']
    b_folio_section = data['b_folio_section']
    folio_regime = data['folio_regime']

    # Filter A folio MIDDLEs to PP only
    a_folio_pp = {}
    for f, mids in a_folio_middles.items():
        pp_mids = mids & pp_set
        if pp_mids:
            a_folio_pp[f] = pp_mids

    a_folios = sorted(a_folio_pp.keys())
    b_folios = sorted(b_folio_middles.keys())

    print(f"Computing {len(a_folios)} x {len(b_folios)} coverage matrix...")

    # Compute coverage: fraction of B-folio MIDDLEs covered by each A-folio's PP set
    # coverage[a][b] = |A_pp ∩ B_mids| / |B_mids|
    coverage_matrix = {}
    for af in a_folios:
        a_pp = a_folio_pp[af]
        row = {}
        for bf in b_folios:
            b_mids = b_folio_middles[bf]
            if b_mids:
                row[bf] = len(a_pp & b_mids) / len(b_mids)
            else:
                row[bf] = 0.0
        coverage_matrix[af] = row

    # Per-A-folio: mean coverage, best B-folio, worst B-folio
    a_folio_stats = {}
    for af in a_folios:
        coverages = list(coverage_matrix[af].values())
        best_bf = max(coverage_matrix[af], key=coverage_matrix[af].get)
        a_folio_stats[af] = {
            'section': a_folio_section.get(af, '?'),
            'n_pp_middles': len(a_folio_pp[af]),
            'mean_coverage': sum(coverages) / len(coverages),
            'max_coverage': max(coverages),
            'min_coverage': min(coverages),
            'best_b_folio': best_bf,
            'best_b_section': b_folio_section.get(best_bf, '?'),
        }

    # Per-B-folio: which A-folio provides best coverage?
    b_folio_best_a = {}
    for bf in b_folios:
        best_af = max(a_folios, key=lambda af: coverage_matrix[af][bf])
        b_folio_best_a[bf] = {
            'best_a_folio': best_af,
            'best_a_section': a_folio_section.get(best_af, '?'),
            'best_coverage': coverage_matrix[best_af][bf],
            'b_section': b_folio_section.get(bf, '?'),
            'regime': folio_regime.get(bf, '?'),
        }

    # Cluster test: do A-folio coverage vectors cluster by A-section?
    # Simple approach: compute mean coverage per B-section for each A-folio
    b_section_folios = defaultdict(list)
    for bf in b_folios:
        sec = b_folio_section.get(bf, '?')
        b_section_folios[sec].append(bf)

    a_folio_b_section_coverage = {}
    for af in a_folios:
        sec_cov = {}
        for b_sec, b_fols in b_section_folios.items():
            if b_fols:
                sec_cov[b_sec] = sum(coverage_matrix[af][bf] for bf in b_fols) / len(b_fols)
        a_folio_b_section_coverage[af] = sec_cov

    # Test: does A-section predict which B-section an A-folio covers best?
    a_section_b_preferences = defaultdict(lambda: defaultdict(list))
    for af in a_folios:
        a_sec = a_folio_section.get(af, '?')
        for b_sec, cov in a_folio_b_section_coverage[af].items():
            a_section_b_preferences[a_sec][b_sec].append(cov)

    # Mean coverage by A-section -> B-section
    cross_tab = {}
    for a_sec in sorted(a_section_b_preferences.keys()):
        cross_tab[a_sec] = {}
        for b_sec in sorted(a_section_b_preferences[a_sec].keys()):
            vals = a_section_b_preferences[a_sec][b_sec]
            cross_tab[a_sec][b_sec] = sum(vals) / len(vals)

    print("\nA-section -> B-section mean coverage:")
    b_secs = sorted(set(b_folio_section.values()))
    header = "A\\B\t" + "\t".join(b_secs)
    print(header)
    for a_sec in sorted(cross_tab.keys()):
        row_str = a_sec + "\t" + "\t".join(f"{cross_tab[a_sec].get(bs, 0):.3f}" for bs in b_secs)
        print(row_str)

    # Cosine similarity between A-H and A-P coverage vectors (averaged)
    a_h_mean = {}
    a_p_mean = {}
    for b_sec in b_secs:
        h_vals = a_section_b_preferences.get('H', {}).get(b_sec, [])
        p_vals = a_section_b_preferences.get('P', {}).get(b_sec, [])
        a_h_mean[b_sec] = sum(h_vals) / len(h_vals) if h_vals else 0
        a_p_mean[b_sec] = sum(p_vals) / len(p_vals) if p_vals else 0

    h_p_cosine = cosine_sim(a_h_mean, a_p_mean)
    print(f"\nA-H vs A-P coverage profile cosine: {h_p_cosine:.4f}")

    # Coverage variance: is there more within-A-section variance than between?
    # Compute for each A-section the variance of coverage vectors
    a_section_variance = {}
    for a_sec in sorted(a_section_b_preferences.keys()):
        coverages_by_folio = []
        for af in a_folios:
            if a_folio_section.get(af) == a_sec:
                vec = [a_folio_b_section_coverage[af].get(bs, 0) for bs in b_secs]
                coverages_by_folio.append(vec)
        if len(coverages_by_folio) > 1:
            # Mean pairwise cosine within group
            cosines = []
            for ii in range(len(coverages_by_folio)):
                for jj in range(ii + 1, len(coverages_by_folio)):
                    v1 = {bs: coverages_by_folio[ii][k] for k, bs in enumerate(b_secs)}
                    v2 = {bs: coverages_by_folio[jj][k] for k, bs in enumerate(b_secs)}
                    cosines.append(cosine_sim(v1, v2))
            a_section_variance[a_sec] = {
                'n_folios': len(coverages_by_folio),
                'mean_within_cosine': sum(cosines) / len(cosines) if cosines else 0,
            }

    print(f"\nWithin-A-section coverage similarity:")
    for a_sec, stats in a_section_variance.items():
        print(f"  {a_sec}: {stats['n_folios']} folios, mean within-cosine: {stats['mean_within_cosine']:.4f}")

    result = {
        'n_a_folios': len(a_folios),
        'n_b_folios': len(b_folios),
        'cross_tab': cross_tab,
        'a_h_vs_a_p_cosine': h_p_cosine,
        'a_section_within_variance': a_section_variance,
        # Top 10 A folios by mean coverage
        'top_a_folios': sorted(
            [{'folio': af, **stats} for af, stats in a_folio_stats.items()],
            key=lambda x: -x['mean_coverage']
        )[:10],
        # B-folio best-A summary
        'b_folio_best_a_section_distribution': dict(Counter(
            v['best_a_section'] for v in b_folio_best_a.values()
        )),
    }

    return result


def c2_pipeline_sufficiency(data):
    """Greedy forward selection: how many A folios needed to cover B's grammar?

    Tests coverage of:
    (a) B's 88 classified MIDDLEs (operational grammar)
    (b) B's full MIDDLE inventory (including HT/UN)
    """
    print("\n=== C2: Pipeline Sufficiency / Bottleneck ===")

    a_folio_middles = data['a_folio_middles']
    pp_set = data['pp_set']
    matched_pp = data['matched_pp']
    all_b_middles = data['all_b_middles']

    # Filter A folio MIDDLEs to PP only
    a_folio_pp = {}
    for f, mids in a_folio_middles.items():
        pp_mids = mids & pp_set
        if pp_mids:
            a_folio_pp[f] = pp_mids

    a_folios = sorted(a_folio_pp.keys())

    # Target sets
    # (a) Classified B MIDDLEs — these are the PP MIDDLEs that match B grammar classes
    classified_target = matched_pp & pp_set
    # (b) All B MIDDLEs that are also in PP (to focus on pipeline-relevant vocabulary)
    all_pp_in_b = pp_set & all_b_middles
    # (c) Full B MIDDLE inventory (including B-exclusive)
    full_b_target = all_b_middles

    def greedy_coverage(a_folio_sets, target):
        """Greedy forward selection: pick A folios that maximize incremental coverage."""
        remaining = set(target)
        selected = []
        coverage_curve = []

        available = set(a_folio_sets.keys())
        while remaining and available:
            # Pick A folio that covers most remaining target MIDDLEs
            best_folio = None
            best_gain = 0
            for af in available:
                gain = len(a_folio_sets[af] & remaining)
                if gain > best_gain:
                    best_gain = gain
                    best_folio = af
            if best_folio is None or best_gain == 0:
                break

            remaining -= a_folio_sets[best_folio]
            selected.append(best_folio)
            available.remove(best_folio)
            covered = len(target) - len(remaining)
            coverage_curve.append({
                'step': len(selected),
                'folio': best_folio,
                'section': data['a_folio_section'].get(best_folio, '?'),
                'gain': best_gain,
                'cumulative_covered': covered,
                'cumulative_fraction': covered / len(target),
            })

        return selected, coverage_curve

    # (a) Classified MIDDLEs
    print(f"\nTarget (a): {len(classified_target)} classified B MIDDLEs")
    sel_class, curve_class = greedy_coverage(a_folio_pp, classified_target)

    # Find milestones
    def find_milestone(curve, threshold):
        for entry in curve:
            if entry['cumulative_fraction'] >= threshold:
                return entry['step']
        return len(curve)

    class_90 = find_milestone(curve_class, 0.90)
    class_95 = find_milestone(curve_class, 0.95)
    class_99 = find_milestone(curve_class, 0.99)
    class_100 = find_milestone(curve_class, 1.00)
    print(f"  Milestones: 90%={class_90} folios, 95%={class_95}, 99%={class_99}, 100%={class_100}")

    # (b) All PP in B
    print(f"\nTarget (b): {len(all_pp_in_b)} PP MIDDLEs present in B")
    sel_pp_b, curve_pp_b = greedy_coverage(a_folio_pp, all_pp_in_b)

    pp_b_90 = find_milestone(curve_pp_b, 0.90)
    pp_b_95 = find_milestone(curve_pp_b, 0.95)
    pp_b_99 = find_milestone(curve_pp_b, 0.99)
    print(f"  Milestones: 90%={pp_b_90} folios, 95%={pp_b_95}, 99%={pp_b_99}")

    # (c) Full B inventory (using all A MIDDLEs, not just PP)
    a_folio_all = {}
    for f, mids in data['a_folio_middles'].items():
        a_folio_all[f] = mids
    print(f"\nTarget (c): {len(full_b_target)} all B MIDDLEs")
    sel_full, curve_full = greedy_coverage(a_folio_all, full_b_target)

    full_90 = find_milestone(curve_full, 0.90)
    full_95 = find_milestone(curve_full, 0.95)
    full_max = curve_full[-1]['cumulative_fraction'] if curve_full else 0
    print(f"  Milestones: 90%={full_90}, 95%={full_95}")
    print(f"  Max coverage with all A folios: {full_max:.3f}")

    # Hub analysis: are the first few selected folios special?
    hub_folios = curve_class[:10] if len(curve_class) >= 10 else curve_class
    hub_sections = Counter(e['section'] for e in hub_folios)
    print(f"\nTop-10 hub A folios (classified grammar):")
    for e in hub_folios:
        print(f"  Step {e['step']}: {e['folio']} (section {e['section']}, "
              f"gain={e['gain']}, cumul={e['cumulative_fraction']:.3f})")
    print(f"Hub section distribution: {dict(hub_sections)}")

    result = {
        'classified_target_size': len(classified_target),
        'pp_in_b_target_size': len(all_pp_in_b),
        'full_b_target_size': len(full_b_target),
        'classified_milestones': {'90%': class_90, '95%': class_95, '99%': class_99, '100%': class_100},
        'pp_in_b_milestones': {'90%': pp_b_90, '95%': pp_b_95, '99%': pp_b_99},
        'full_b_milestones': {'90%': full_90, '95%': full_95},
        'full_b_max_coverage': full_max,
        'classified_coverage_curve': curve_class[:20],  # First 20 steps
        'hub_folios': hub_folios,
        'hub_section_distribution': dict(hub_sections),
        'total_a_folios_available': len(a_folios),
    }

    return result


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def verdict(results):
    """Synthesize verdicts from all 6 tests."""
    print("\n" + "=" * 60)
    print("VERDICT SYNTHESIS")
    print("=" * 60)

    verdicts = {}

    # --- Tier A verdict: Section-specificity mechanism ---
    a1 = results['a1']
    a2 = results['a2']

    # Key metric: PP JS fraction of all JS
    pp_fraction = a2['pp_js_fraction_of_all']
    bx_fraction = a2['bexcl_js_fraction_of_all']
    pp_js = a2['mean_js_pp']
    bx_js = a2['mean_js_bexcl']

    if pp_fraction < 0.3 and bx_fraction > 0.7:
        mechanism = 'SPECIFICITY_IS_B_INTERNAL'
        mechanism_detail = (f"B-exclusive vocabulary drives {bx_fraction:.0%} of section divergence. "
                           f"Shared/PP vocabulary is nearly section-uniform (JS={pp_js:.4f}).")
    elif pp_fraction > 0.7:
        mechanism = 'SPECIFICITY_IS_FREQUENCY_MODULATED'
        mechanism_detail = (f"Shared/PP vocabulary drives {pp_fraction:.0%} of section divergence "
                           f"through frequency modulation (JS={pp_js:.4f}).")
    else:
        mechanism = 'DUAL_MECHANISM'
        mechanism_detail = (f"Both contribute: PP drives {pp_fraction:.0%} (JS={pp_js:.4f}), "
                           f"B-exclusive drives {bx_fraction:.0%} (JS={bx_js:.4f}).")

    verdicts['section_specificity_mechanism'] = mechanism
    print(f"\nTier A: {mechanism}")
    print(f"  {mechanism_detail}")

    # Check frequency modulation ratio from A1
    freq_mod = a1['mean_freq_modulation_ratio']
    print(f"  Frequency modulation ratio: {freq_mod:.3f}")
    if freq_mod > 0.5:
        print(f"  -> Frequency adds substantial discrimination beyond presence/absence")
    else:
        print(f"  -> Presence/absence already captures most section discrimination")

    # --- Tier B verdict: Pipeline dark matter ---
    b1 = results['b1']

    b_present_frac = b1['b_present_fraction']
    if b_present_frac > 0.8:
        dark_matter = 'DARK_PIPELINE'
        dark_detail = (f"{b1['n_b_present']}/{b1['n_unmatched']} unmatched PPs appear in B tokens. "
                      f"Large HT/UN substrate carrying pipeline vocabulary outside classified grammar.")
    elif b_present_frac < 0.2:
        dark_matter = 'PHANTOM_SHARING'
        dark_detail = (f"Only {b1['n_b_present']}/{b1['n_unmatched']} unmatched PPs appear in B. "
                      f"Most 'shared' vocabulary is incidental MIDDLE collision.")
    else:
        dark_matter = 'PARTIAL_PIPELINE'
        dark_detail = (f"{b1['n_b_present']}/{b1['n_unmatched']} ({b_present_frac:.0%}) present in B. "
                      f"Mixed: some genuine pipeline, some phantom sharing.")

    verdicts['dark_matter'] = dark_matter
    print(f"\nTier B: {dark_matter}")
    print(f"  {dark_detail}")

    # --- Tier C verdict: Flow architecture ---
    c1 = results['c1']
    c2 = results['c2']

    h_p_cosine = c1['a_h_vs_a_p_cosine']
    if h_p_cosine < 0.9:
        flow_structure = 'STRUCTURED_FLOW'
        flow_detail = (f"A-H and A-P have different B-coverage profiles (cosine={h_p_cosine:.3f}). "
                      f"Pipeline has section architecture.")
    else:
        flow_structure = 'UNIFORM_POOL'
        flow_detail = (f"A-H and A-P have nearly identical B-coverage profiles (cosine={h_p_cosine:.3f}). "
                      f"Pipeline is a uniform pool (confirming C846).")

    verdicts['flow_architecture'] = flow_structure
    print(f"\nTier C: {flow_structure}")
    print(f"  {flow_detail}")

    # Pipeline concentration
    class_100 = c2['classified_milestones']['100%']
    class_90 = c2['classified_milestones']['90%']
    total_a = c2['total_a_folios_available']
    print(f"\n  Pipeline concentration: {class_90} A folios cover 90% of classified grammar, "
          f"{class_100} for 100% (of {total_a} available)")

    if class_100 <= 5:
        verdicts['pipeline_concentration'] = 'HIGHLY_CONCENTRATED'
        print(f"  -> HIGHLY CONCENTRATED: {class_100} folios suffice for complete grammar")
    elif class_100 <= 20:
        verdicts['pipeline_concentration'] = 'MODERATELY_CONCENTRATED'
        print(f"  -> MODERATELY CONCENTRATED")
    else:
        verdicts['pipeline_concentration'] = 'DISTRIBUTED'
        print(f"  -> DISTRIBUTED: {class_100} folios needed for complete grammar")

    # Overall synthesis
    print(f"\n{'=' * 60}")
    print(f"OVERALL:")
    print(f"  Mechanism: {mechanism}")
    print(f"  Dark matter: {dark_matter}")
    print(f"  Flow: {flow_structure}")
    print(f"  Concentration: {verdicts['pipeline_concentration']}")
    print(f"{'=' * 60}")

    return verdicts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Phase 406: Cross-System Vocabulary Flow")
    print("=" * 60)

    data = load_data()

    results = {}
    results['a1'] = a1_frequency_modulation(data)
    results['a2'] = a2_specificity_source_decomposition(data)
    results['b1'] = b1_unmatched_pp_characterization(data)
    results['b2'] = b2_a_section_routing(data)
    results['c1'] = c1_folio_coverage_matrix(data)
    results['c2'] = c2_pipeline_sufficiency(data)

    verdicts = verdict(results)
    results['verdicts'] = verdicts
    results['validation'] = data['validation']

    # Save
    out_path = ROOT / 'phases' / 'CROSS_SYSTEM_VOCABULARY_FLOW' / 'results' / 'ab_vocabulary_flow.json'
    with open(out_path, 'w') as f:
        json.dump(round_floats(results), f, indent=2, default=str)

    print(f"\nResults saved to {out_path}")
    print(f"File size: {os.path.getsize(out_path):,} bytes")


if __name__ == '__main__':
    main()
