"""Phase 402: Rosettes System Revalidation — 13-test battery.

Supersedes Phase 387/388H (ROSETTES_SYSTEM_CLASSIFICATION).
All 21 prior Rosettes constraints were invalidated due to incomplete EVA data.
This phase uses corrected ZL transcription + manual spatial annotation.

Data source: data/rosettes_annotated.json (via RosettesAnalyzer)

Tier 1 (System Classification, S1-S6):
  Establish what system each entity TYPE belongs to (B, AZC, A, or hybrid)

Tier 2 (Cross-Reference Validation, X1-X4):
  Establish whether the foldout functions as an index/metalayer

Tier 3 (Spatial Structure, P1-P3):
  Exploit spatial granularity unique to the corrected data
"""

import json
import math
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

# 17 forbidden MIDDLE bigrams (C109)
FORBIDDEN_MIDDLE_PAIRS = {
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('dy', 'chey'), ('chey', 'chedy'),
    ('chey', 'shedy'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('c', 'ee'), ('shedy', 'aiin'),
    ('l', 'chol'), ('ar', 'dal'), ('he', 't'), ('shedy', 'o'),
    ('or', 'dal'), ('he', 'or'),
}

KERNEL_CHARS = set('khe')

# 3x3 grid positions for spatial distance
GRID_POS = {
    'NW': (0, 0), 'NORTH': (0, 1), 'NE': (0, 2),
    'WEST': (1, 0), 'CENTER': (1, 1), 'EAST': (1, 2),
    'SW': (2, 0), 'SOUTH': (2, 1), 'SE': (2, 2),
}

# Path endpoint parsing
PATH_ENDPOINTS = {
    'PATH_WEST_NW': ('WEST', 'NW'),
    'PATH_NW_NORTH': ('NW', 'NORTH'),
    'PATH_NORTH_NE': ('NORTH', 'NE'),
    'PATH_NE_EAST': ('NE', 'EAST'),
    'PATH_EAST_SE': ('EAST', 'SE'),
    'PATH_SE_SOUTH': ('SE', 'SOUTH'),
    'PATH_SOUTH_SW': ('SOUTH', 'SW'),
    'PATH_SW_WEST': ('SW', 'WEST'),
}


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


# ============================================================
# DATA LOADING
# ============================================================

def load_references(morph):
    """Pre-compute all reference data structures."""
    tx = Transcript()

    # B corpus by section and by folio (excluding Rosettes folios)
    ros_folios = {'f85r1', 'f85r2', 'f85v2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}
    section_middles = defaultdict(set)
    folio_middles = defaultdict(set)
    folio_section = {}
    b_all_middles = set()
    b_prefix_counts = Counter()
    b_suffix_counts = Counter()
    b_token_count = 0
    b_kernel_count = 0
    b_middle_count = 0
    b_link_count = 0
    # For co-occurrence: which MIDDLEs appear together on the same line
    b_line_middles = defaultdict(set)

    for tok in tx.currier_b():
        if tok.folio in ros_folios:
            continue
        m = morph.extract(tok.word)
        b_token_count += 1
        if m.middle:
            section_middles[tok.section].add(m.middle)
            folio_middles[tok.folio].add(m.middle)
            b_all_middles.add(m.middle)
            b_line_middles[(tok.folio, tok.line)].add(m.middle)
            b_middle_count += 1
            if any(c in KERNEL_CHARS for c in m.middle):
                b_kernel_count += 1
            if m.middle == 'ol':
                b_link_count += 1
        if m.prefix:
            b_prefix_counts[m.prefix] += 1
        if m.suffix:
            b_suffix_counts[m.suffix] += 1
        folio_section[tok.folio] = tok.section

    # A corpus profile
    a_all_middles = set()
    a_prefix_counts = Counter()
    a_suffix_counts = Counter()
    for tok in tx.currier_a():
        m = morph.extract(tok.word)
        if m.middle:
            a_all_middles.add(m.middle)
        if m.prefix:
            a_prefix_counts[m.prefix] += 1
        if m.suffix:
            a_suffix_counts[m.suffix] += 1

    # AZC corpus profile
    azc_prefix_counts = Counter()
    azc_suffix_counts = Counter()
    azc_middles = set()
    azc_token_count = 0
    azc_kernel_count = 0
    azc_middle_count = 0
    for tok in tx.azc():
        m = morph.extract(tok.word)
        azc_token_count += 1
        if m.middle:
            azc_middles.add(m.middle)
            azc_middle_count += 1
            if any(c in KERNEL_CHARS for c in m.middle):
                azc_kernel_count += 1
        if m.prefix:
            azc_prefix_counts[m.prefix] += 1
        if m.suffix:
            azc_suffix_counts[m.suffix] += 1

    # Build co-occurrence set (pairs of MIDDLEs on the same B line)
    b_cooccurrence = set()
    for line_mids in b_line_middles.values():
        mids = sorted(line_mids)
        for i in range(len(mids)):
            for j in range(i + 1, len(mids)):
                b_cooccurrence.add((mids[i], mids[j]))

    # 49-class token map
    ctm_path = PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm_data = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm_data['token_to_class'].items()}

    # Bridge set
    bridge_path = PROJECT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(bridge_path, 'r', encoding='utf-8') as f:
        bd = json.load(f)
    bridge_set = set(bd['t5_structural_profile']['bridge_middles'])

    # RI/PP sets
    ri_set, pp_set = load_middle_classes()

    return {
        'section_middles': dict(section_middles),
        'folio_middles': dict(folio_middles),
        'folio_section': folio_section,
        'b_all_middles': b_all_middles,
        'b_prefix_counts': b_prefix_counts,
        'b_suffix_counts': b_suffix_counts,
        'b_token_count': b_token_count,
        'b_kernel_count': b_kernel_count,
        'b_middle_count': b_middle_count,
        'b_link_count': b_link_count,
        'b_cooccurrence': b_cooccurrence,
        'a_all_middles': a_all_middles,
        'a_prefix_counts': a_prefix_counts,
        'a_suffix_counts': a_suffix_counts,
        'azc_prefix_counts': azc_prefix_counts,
        'azc_suffix_counts': azc_suffix_counts,
        'azc_middles': azc_middles,
        'azc_token_count': azc_token_count,
        'azc_kernel_count': azc_kernel_count,
        'azc_middle_count': azc_middle_count,
        'token_to_class': token_to_class,
        'bridge_set': bridge_set,
        'ri_set': ri_set,
        'pp_set': pp_set,
    }


def group_by_entity_type(ra):
    """Group all Rosettes tokens by entity type (second-class / sub-region).

    Returns {type_name: [token_dicts]} and also per-entity breakdown.
    """
    type_groups = defaultdict(list)
    entity_groups = defaultdict(list)

    for ename in ra.get_entities():
        entity = ra.get_entity(ename)
        if not entity:
            continue
        for sr_name, sr_data in entity['sub_regions'].items():
            for locus in sr_data['loci']:
                for tok in locus.get('words', []):
                    type_groups[sr_name].append(tok)
                    entity_groups[ename].append(tok)

    return dict(type_groups), dict(entity_groups)


# ============================================================
# TIER 1: SYSTEM CLASSIFICATION (S1-S6)
# ============================================================

def s1_grammar_coverage(type_groups, entity_groups, token_to_class, refs):
    """S1: What fraction of tokens map to the 49 B instruction classes?"""
    print("\n=== S1: Grammar Coverage (49-class) ===")

    # B reference
    b_mapped = sum(1 for t in token_to_class)  # All mapped tokens are B
    # Compute from B corpus count
    b_cov = len(token_to_class)  # total B token types that have a class

    per_type = {}
    for tname, tokens in sorted(type_groups.items()):
        mapped = sum(1 for t in tokens if t['word'] in token_to_class)
        total = len(tokens)
        rate = mapped / total if total else 0
        per_type[tname] = {'mapped': mapped, 'total': total, 'coverage': rate}
        print(f"  {tname:20s}: {mapped}/{total} = {rate:.1%}")

    per_entity = {}
    for ename, tokens in sorted(entity_groups.items()):
        mapped = sum(1 for t in tokens if t['word'] in token_to_class)
        total = len(tokens)
        rate = mapped / total if total else 0
        per_entity[ename] = {'mapped': mapped, 'total': total, 'coverage': rate}

    # Overall
    all_tokens = [t for tokens in type_groups.values() for t in tokens]
    all_mapped = sum(1 for t in all_tokens if t['word'] in token_to_class)
    overall_rate = all_mapped / len(all_tokens) if all_tokens else 0
    print(f"  OVERALL: {all_mapped}/{len(all_tokens)} = {overall_rate:.1%}")

    # Verdict per type
    verdicts = {}
    for tname, d in per_type.items():
        if d['coverage'] > 0.80:
            verdicts[tname] = 'B_LIKE'
        elif d['coverage'] < 0.60:
            verdicts[tname] = 'AZC_LIKE'
        else:
            verdicts[tname] = 'INTERMEDIATE'

    return {
        'per_type': per_type,
        'per_entity': per_entity,
        'overall_coverage': overall_rate,
        'verdicts': verdicts,
    }


def s2_kernel_density(type_groups, entity_groups, refs):
    """S2: What fraction of tokens have kernel characters (k/h/e) in MIDDLE?"""
    print("\n=== S2: Kernel Density ===")

    b_rate = refs['b_kernel_count'] / refs['b_middle_count'] if refs['b_middle_count'] else 0
    azc_rate = refs['azc_kernel_count'] / refs['azc_middle_count'] if refs['azc_middle_count'] else 0
    print(f"  Reference: B={b_rate:.1%}, AZC={azc_rate:.1%}")

    per_type = {}
    for tname, tokens in sorted(type_groups.items()):
        with_mid = [t for t in tokens if t.get('middle')]
        with_kernel = sum(1 for t in with_mid if any(c in KERNEL_CHARS for c in t['middle']))
        total = len(with_mid)
        rate = with_kernel / total if total else 0
        per_type[tname] = {'kernel': with_kernel, 'total': total, 'rate': rate}
        print(f"  {tname:20s}: {with_kernel}/{total} = {rate:.1%}")

    per_entity = {}
    for ename, tokens in sorted(entity_groups.items()):
        with_mid = [t for t in tokens if t.get('middle')]
        with_kernel = sum(1 for t in with_mid if any(c in KERNEL_CHARS for c in t['middle']))
        total = len(with_mid)
        per_entity[ename] = {'kernel': with_kernel, 'total': total,
                             'rate': with_kernel / total if total else 0}

    verdicts = {}
    for tname, d in per_type.items():
        if d['rate'] > 0.50:
            verdicts[tname] = 'B_LIKE'
        elif d['rate'] < 0.15:
            verdicts[tname] = 'AZC_LIKE'
        else:
            verdicts[tname] = 'INTERMEDIATE'

    return {
        'b_reference': b_rate,
        'azc_reference': azc_rate,
        'per_type': per_type,
        'per_entity': per_entity,
        'verdicts': verdicts,
    }


def s3_link_density(type_groups, entity_groups, refs):
    """S3: What fraction of tokens are LINK (MIDDLE == 'ol')?"""
    print("\n=== S3: LINK Density ===")

    b_rate = refs['b_link_count'] / refs['b_token_count'] if refs['b_token_count'] else 0
    print(f"  Reference: B={b_rate:.1%}")

    per_type = {}
    for tname, tokens in sorted(type_groups.items()):
        links = sum(1 for t in tokens if t.get('middle') == 'ol')
        total = len(tokens)
        rate = links / total if total else 0
        per_type[tname] = {'links': links, 'total': total, 'rate': rate}
        print(f"  {tname:20s}: {links}/{total} = {rate:.1%}")

    per_entity = {}
    for ename, tokens in sorted(entity_groups.items()):
        links = sum(1 for t in tokens if t.get('middle') == 'ol')
        total = len(tokens)
        per_entity[ename] = {'links': links, 'total': total,
                             'rate': links / total if total else 0}

    verdicts = {}
    for tname, d in per_type.items():
        if d['rate'] > 0.05:
            verdicts[tname] = 'B_LIKE'
        elif d['rate'] < 0.01:
            verdicts[tname] = 'AZC_LIKE'
        else:
            verdicts[tname] = 'INTERMEDIATE'

    return {
        'b_reference': b_rate,
        'per_type': per_type,
        'per_entity': per_entity,
        'verdicts': verdicts,
    }


def s4_pp_ri_composition(type_groups, entity_groups, refs):
    """S4: Are MIDDLEs PP (shared A+B), RI (A-exclusive), or unclassified?"""
    print("\n=== S4: PP vs RI Composition ===")

    ri_set = refs['ri_set']
    pp_set = refs['pp_set']

    per_type = {}
    for tname, tokens in sorted(type_groups.items()):
        middles = [t['middle'] for t in tokens if t.get('middle')]
        unique_mids = set(middles)
        pp_count = len(unique_mids & pp_set)
        ri_count = len(unique_mids & ri_set)
        neither = len(unique_mids) - pp_count - ri_count
        total = len(unique_mids)
        pp_frac = pp_count / total if total else 0
        ri_frac = ri_count / total if total else 0
        per_type[tname] = {
            'unique_middles': total, 'pp': pp_count, 'ri': ri_count,
            'neither': neither, 'pp_frac': pp_frac, 'ri_frac': ri_frac,
        }
        print(f"  {tname:20s}: {total} unique MIDDLEs — PP={pp_count} ({pp_frac:.0%}), "
              f"RI={ri_count} ({ri_frac:.0%}), other={neither}")

    per_entity = {}
    for ename, tokens in sorted(entity_groups.items()):
        middles = set(t['middle'] for t in tokens if t.get('middle'))
        pp_count = len(middles & pp_set)
        ri_count = len(middles & ri_set)
        per_entity[ename] = {
            'unique_middles': len(middles), 'pp': pp_count, 'ri': ri_count,
            'pp_frac': pp_count / len(middles) if middles else 0,
            'ri_frac': ri_count / len(middles) if middles else 0,
        }

    verdicts = {}
    for tname, d in per_type.items():
        if d['ri_frac'] > 0.15:
            verdicts[tname] = 'A_LIKE'
        elif d['pp_frac'] > 0.60:
            verdicts[tname] = 'B_LIKE'
        else:
            verdicts[tname] = 'MIXED'

    return {
        'per_type': per_type,
        'per_entity': per_entity,
        'verdicts': verdicts,
    }


def s5_sequential_grammar(ra, morph):
    """S5: Do ring text MIDDLEs follow B grammar (forbidden transitions, structure)?"""
    print("\n=== S5: Sequential Grammar (ring text) ===")

    # Collect sequential MIDDLE lists from ring text loci
    # Ring text has the most sequential tokens
    all_bigrams = []
    ring_middles_seq = []

    for ename in ra.get_rosettes():
        ring_tokens = ra.get_entity_tokens(ename, sub_region='ring')
        middles = [t['middle'] for t in ring_tokens if t.get('middle')]
        ring_middles_seq.extend(middles)
        for i in range(len(middles) - 1):
            all_bigrams.append((middles[i], middles[i + 1]))

    total_bigrams = len(all_bigrams)
    print(f"  Ring text MIDDLE bigrams: {total_bigrams}")

    if total_bigrams < 10:
        print("  INSUFFICIENT DATA for sequential grammar test")
        return {
            'total_bigrams': total_bigrams,
            'verdict': 'INSUFFICIENT_DATA',
        }

    # Forbidden transition check
    violations = sum(1 for b in all_bigrams if b in FORBIDDEN_MIDDLE_PAIRS)
    violation_rate = violations / total_bigrams if total_bigrams else 0
    print(f"  Forbidden violations: {violations}/{total_bigrams} = {violation_rate:.2%}")

    # Bigram entropy (how structured are the transitions?)
    bigram_counts = Counter(all_bigrams)
    total = sum(bigram_counts.values())
    entropy = 0.0
    for count in bigram_counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    print(f"  Bigram entropy: {entropy:.2f} bits (B reference: ~0.41, A reference: ~3.0)")

    # Self-transition rate (AXM)
    self_trans = sum(1 for a, b in all_bigrams if a == b)
    self_rate = self_trans / total_bigrams if total_bigrams else 0
    print(f"  Self-transition rate: {self_rate:.2%} (B reference: ~4.35%)")

    if violation_rate < 0.01 and entropy < 2.0:
        verdict = 'B_LIKE_COMPLIANT'
    elif violation_rate < 0.05:
        verdict = 'MOSTLY_COMPLIANT'
    else:
        verdict = 'UNSTRUCTURED'

    return {
        'total_bigrams': total_bigrams,
        'violations': violations,
        'violation_rate': violation_rate,
        'bigram_entropy': entropy,
        'self_transition_rate': self_rate,
        'unique_bigrams': len(bigram_counts),
        'verdict': verdict,
    }


def s6_morphological_profile(type_groups, refs):
    """S6: Which system does each entity type's PREFIX/SUFFIX profile resemble?"""
    print("\n=== S6: Morphological Profile ===")

    # Build reference profiles (normalized)
    def normalize(counter):
        total = sum(counter.values())
        return {k: v / total for k, v in counter.items()} if total else {}

    b_pre = normalize(refs['b_prefix_counts'])
    a_pre = normalize(refs['a_prefix_counts'])
    azc_pre = normalize(refs['azc_prefix_counts'])
    b_suf = normalize(refs['b_suffix_counts'])
    a_suf = normalize(refs['a_suffix_counts'])
    azc_suf = normalize(refs['azc_suffix_counts'])

    per_type = {}
    for tname, tokens in sorted(type_groups.items()):
        pre_counts = Counter(t.get('prefix') for t in tokens if t.get('prefix'))
        suf_counts = Counter(t.get('suffix') for t in tokens if t.get('suffix'))
        ros_pre = normalize(pre_counts)
        ros_suf = normalize(suf_counts)

        cos_b = cosine_sim(ros_pre, b_pre)
        cos_a = cosine_sim(ros_pre, a_pre)
        cos_azc = cosine_sim(ros_pre, azc_pre)

        cos_b_suf = cosine_sim(ros_suf, b_suf)
        cos_a_suf = cosine_sim(ros_suf, a_suf)
        cos_azc_suf = cosine_sim(ros_suf, azc_suf)

        # Combined (average prefix + suffix cosine)
        combined_b = (cos_b + cos_b_suf) / 2
        combined_a = (cos_a + cos_a_suf) / 2
        combined_azc = (cos_azc + cos_azc_suf) / 2

        best = max([('B', combined_b), ('A', combined_a), ('AZC', combined_azc)],
                   key=lambda x: x[1])

        per_type[tname] = {
            'prefix_cosine': {'B': cos_b, 'A': cos_a, 'AZC': cos_azc},
            'suffix_cosine': {'B': cos_b_suf, 'A': cos_a_suf, 'AZC': cos_azc_suf},
            'combined_cosine': {'B': combined_b, 'A': combined_a, 'AZC': combined_azc},
            'best_match': best[0],
            'best_cosine': best[1],
            'top_prefixes': pre_counts.most_common(5),
            'top_suffixes': suf_counts.most_common(5),
        }
        print(f"  {tname:20s}: B={combined_b:.3f} A={combined_a:.3f} AZC={combined_azc:.3f} -> {best[0]}")

    verdicts = {tname: d['best_match'] for tname, d in per_type.items()}
    return {'per_type': per_type, 'verdicts': verdicts}


# ============================================================
# TIER 2: CROSS-REFERENCE VALIDATION (X1-X4)
# ============================================================

def x1_bridge_enrichment(ra, type_groups, refs):
    """X1: Are bridge MIDDLEs over-represented in Rosettes?"""
    print("\n=== X1: Bridge Enrichment ===")

    bridge_set = refs['bridge_set']
    b_middles = refs['b_all_middles']
    b_bridge_frac = len(bridge_set & b_middles) / len(b_middles) if b_middles else 0
    print(f"  B corpus bridge fraction: {b_bridge_frac:.1%} ({len(bridge_set & b_middles)}/{len(b_middles)})")

    # Overall Rosettes
    all_mids = ra.all_middles()
    ros_bridge = all_mids & bridge_set
    ros_frac = len(ros_bridge) / len(all_mids) if all_mids else 0
    enrichment = ros_frac / b_bridge_frac if b_bridge_frac else 0
    print(f"  Rosettes bridge fraction: {ros_frac:.1%} ({len(ros_bridge)}/{len(all_mids)})")
    print(f"  Enrichment: {enrichment:.2f}x")

    # Per entity type
    per_type = {}
    for tname, tokens in sorted(type_groups.items()):
        mids = set(t['middle'] for t in tokens if t.get('middle'))
        bridge_count = len(mids & bridge_set)
        total = len(mids)
        frac = bridge_count / total if total else 0
        per_type[tname] = {'bridge': bridge_count, 'total': total, 'fraction': frac,
                           'enrichment': frac / b_bridge_frac if b_bridge_frac else 0}
        print(f"  {tname:20s}: {bridge_count}/{total} = {frac:.1%} ({per_type[tname]['enrichment']:.2f}x)")

    # Per rosette
    per_rosette = {}
    for rname in ra.get_rosettes():
        mids = ra.get_entity_middles(rname)
        bridge_count = len(mids & bridge_set)
        total = len(mids)
        frac = bridge_count / total if total else 0
        per_rosette[rname] = {'bridge': bridge_count, 'total': total, 'fraction': frac}

    if ros_frac > 0.14:
        verdict = 'BRIDGE_ENRICHED'
    elif ros_frac > 0.07:
        verdict = 'MODERATE'
    else:
        verdict = 'NOT_ENRICHED'

    return {
        'b_bridge_fraction': b_bridge_frac,
        'rosettes_bridge_fraction': ros_frac,
        'enrichment': enrichment,
        'bridge_middles_found': sorted(ros_bridge),
        'per_type': per_type,
        'per_rosette': per_rosette,
        'verdict': verdict,
    }


def x2_section_correlation(ra, refs, morph):
    """X2: Which B sections do rosettes correlate with?"""
    print("\n=== X2: Section Correlation ===")

    section_middles = refs['section_middles']

    per_rosette = {}
    best_sections = []

    for rname in ra.get_rosettes():
        r_mids = ra.get_entity_middles(rname)
        if not r_mids:
            continue

        section_jaccards = {}
        for sec, sec_mids in section_middles.items():
            section_jaccards[sec] = jaccard(r_mids, sec_mids)

        best_sec = max(section_jaccards, key=section_jaccards.get) if section_jaccards else '?'
        best_sections.append(best_sec)

        per_rosette[rname] = {
            'middles_count': len(r_mids),
            'section_jaccards': section_jaccards,
            'best_section': best_sec,
            'best_jaccard': section_jaccards.get(best_sec, 0),
        }
        sec_str = ', '.join(f"{s}={j:.3f}" for s, j in sorted(section_jaccards.items()))
        print(f"  {rname:10s}: {sec_str} -> {best_sec}")

    # Are all rosettes pointing to the same section?
    unique_best = set(best_sections)
    if len(unique_best) == 1:
        verdict = 'SINGLE_SECTION'
    elif len(unique_best) <= 2:
        verdict = 'DUAL_SECTION'
    else:
        verdict = 'MULTI_SECTION'

    print(f"  Best sections: {Counter(best_sections)}")
    print(f"  Verdict: {verdict}")

    return {
        'per_rosette': per_rosette,
        'best_section_distribution': dict(Counter(best_sections)),
        'verdict': verdict,
    }


def x3_folio_crossref(ra, refs, morph):
    """X3: Do different rosettes point to different B folios?"""
    print("\n=== X3: B Folio Cross-Reference ===")

    folio_middles = refs['folio_middles']

    per_rosette_top5 = {}
    for rname in ra.get_rosettes():
        r_mids = ra.get_entity_middles(rname)
        if not r_mids:
            continue

        folio_jaccards = {}
        for folio, f_mids in folio_middles.items():
            folio_jaccards[folio] = jaccard(r_mids, f_mids)

        top5 = sorted(folio_jaccards.items(), key=lambda x: -x[1])[:5]
        per_rosette_top5[rname] = {
            'top5': [(f, j) for f, j in top5],
            'top5_folios': set(f for f, j in top5),
            'mean_top5_jaccard': sum(j for _, j in top5) / 5 if top5 else 0,
        }
        top_str = ', '.join(f"{f}={j:.3f}" for f, j in top5)
        print(f"  {rname:10s}: {top_str}")

    # Compare top-5 sets across rosettes: are they the same or different?
    rosette_names = list(per_rosette_top5.keys())
    overlap_jaccards = []
    for i in range(len(rosette_names)):
        for j in range(i + 1, len(rosette_names)):
            ri = rosette_names[i]
            rj = rosette_names[j]
            si = per_rosette_top5[ri]['top5_folios']
            sj = per_rosette_top5[rj]['top5_folios']
            overlap_jaccards.append(jaccard(si, sj))

    mean_overlap = sum(overlap_jaccards) / len(overlap_jaccards) if overlap_jaccards else 0
    print(f"  Mean top-5 overlap Jaccard between rosettes: {mean_overlap:.3f}")

    if mean_overlap < 0.30:
        verdict = 'SPECIFIC_INDEX'
    elif mean_overlap < 0.60:
        verdict = 'MODERATE_SPECIFICITY'
    else:
        verdict = 'GENERIC_INDEX'

    # Clean up sets for JSON
    for rname in per_rosette_top5:
        per_rosette_top5[rname]['top5_folios'] = sorted(per_rosette_top5[rname]['top5_folios'])

    return {
        'per_rosette': per_rosette_top5,
        'mean_overlap_jaccard': mean_overlap,
        'n_pairs': len(overlap_jaccards),
        'verdict': verdict,
    }


def x4_middle_compatibility(ra, refs):
    """X4: Do Rosettes MIDDLEs show elevated co-occurrence compatibility?"""
    print("\n=== X4: MIDDLE Compatibility ===")

    b_cooccurrence = refs['b_cooccurrence']

    # For each rosette, get MIDDLE set and test pairwise compatibility
    all_ros_middles = sorted(ra.all_middles())
    total_pairs = 0
    compatible_pairs = 0

    for i in range(len(all_ros_middles)):
        for j in range(i + 1, len(all_ros_middles)):
            a, b = all_ros_middles[i], all_ros_middles[j]
            total_pairs += 1
            if (a, b) in b_cooccurrence or (b, a) in b_cooccurrence:
                compatible_pairs += 1

    compat_rate = compatible_pairs / total_pairs if total_pairs else 0
    print(f"  Total MIDDLE pairs: {total_pairs}")
    print(f"  Compatible (co-occur in B lines): {compatible_pairs} ({compat_rate:.1%})")
    print(f"  Reference: B random pairs ~4.3% compatible (C475)")

    # Per rosette
    per_rosette = {}
    for rname in ra.get_rosettes():
        mids = sorted(ra.get_entity_middles(rname))
        pairs = 0
        compat = 0
        for i in range(len(mids)):
            for j in range(i + 1, len(mids)):
                pairs += 1
                a, b = mids[i], mids[j]
                if (a, b) in b_cooccurrence or (b, a) in b_cooccurrence:
                    compat += 1
        per_rosette[rname] = {
            'pairs': pairs, 'compatible': compat,
            'rate': compat / pairs if pairs else 0,
        }

    if compat_rate > 0.50:
        verdict = 'HIGH_COMPATIBILITY'
    elif compat_rate > 0.20:
        verdict = 'MODERATE'
    else:
        verdict = 'BASELINE'

    return {
        'total_pairs': total_pairs,
        'compatible_pairs': compatible_pairs,
        'compatibility_rate': compat_rate,
        'per_rosette': per_rosette,
        'verdict': verdict,
    }


# ============================================================
# TIER 3: SPATIAL STRUCTURE (P1-P3)
# ============================================================

def p1_path_bridging(ra):
    """P1: Do paths share vocabulary with their endpoint rosettes?"""
    print("\n=== P1: Path Vocabulary Bridging ===")

    per_path = {}
    path_jaccards = []
    random_jaccards = []

    all_rosettes = ra.get_rosettes()
    rosette_middles = {r: ra.get_entity_middles(r) for r in all_rosettes}

    for path_name in ra.get_paths():
        path_mids = ra.get_entity_middles(path_name)
        if not path_mids:
            per_path[path_name] = {'middles': 0, 'jaccard_endpoints': 0, 'note': 'empty'}
            continue

        if path_name not in PATH_ENDPOINTS:
            continue

        ep1, ep2 = PATH_ENDPOINTS[path_name]
        endpoint_union = rosette_middles.get(ep1, set()) | rosette_middles.get(ep2, set())
        j_endpoint = jaccard(path_mids, endpoint_union)
        path_jaccards.append(j_endpoint)

        per_path[path_name] = {
            'middles': len(path_mids),
            'endpoints': [ep1, ep2],
            'jaccard_endpoints': j_endpoint,
            'shared_with_endpoints': sorted(path_mids & endpoint_union),
        }
        print(f"  {path_name:20s}: J(path, {ep1}+{ep2}) = {j_endpoint:.3f}")

        # Random baseline: Jaccard with random rosette pairs
        for r1 in all_rosettes:
            for r2 in all_rosettes:
                if r1 >= r2:
                    continue
                if (r1, r2) == (ep1, ep2) or (r2, r1) == (ep1, ep2):
                    continue
                rand_union = rosette_middles.get(r1, set()) | rosette_middles.get(r2, set())
                random_jaccards.append(jaccard(path_mids, rand_union))

    mean_endpoint = sum(path_jaccards) / len(path_jaccards) if path_jaccards else 0
    mean_random = sum(random_jaccards) / len(random_jaccards) if random_jaccards else 0
    print(f"  Mean endpoint Jaccard: {mean_endpoint:.3f}")
    print(f"  Mean random baseline: {mean_random:.3f}")

    if mean_endpoint > mean_random * 1.5 and mean_endpoint > 0.05:
        verdict = 'BRIDGING'
    else:
        verdict = 'INDEPENDENT'

    return {
        'per_path': per_path,
        'mean_endpoint_jaccard': mean_endpoint,
        'mean_random_baseline': mean_random,
        'verdict': verdict,
    }


def p2_adjacency_gradient(ra):
    """P2: Does vocabulary similarity decay with spatial distance?"""
    print("\n=== P2: Spatial Adjacency Gradient ===")

    rosette_middles = {r: ra.get_entity_middles(r) for r in ra.get_rosettes()}

    pairs = []
    for r1 in ra.get_rosettes():
        for r2 in ra.get_rosettes():
            if r1 >= r2:
                continue
            pos1 = GRID_POS.get(r1)
            pos2 = GRID_POS.get(r2)
            if not pos1 or not pos2:
                continue
            dist = math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
            j = jaccard(rosette_middles.get(r1, set()), rosette_middles.get(r2, set()))
            pairs.append({'r1': r1, 'r2': r2, 'distance': dist, 'jaccard': j})
            print(f"  {r1:7s}-{r2:7s}: dist={dist:.2f} J={j:.3f}")

    if len(pairs) < 5:
        return {'pairs': pairs, 'verdict': 'INSUFFICIENT_DATA'}

    # Spearman rank correlation (manual — no scipy dependency)
    n = len(pairs)
    dist_ranks = _rank([p['distance'] for p in pairs])
    jacc_ranks = _rank([p['jaccard'] for p in pairs])
    d_sq = sum((dist_ranks[i] - jacc_ranks[i]) ** 2 for i in range(n))
    rho = 1 - (6 * d_sq) / (n * (n ** 2 - 1))

    # Approximate p-value for Spearman (t-test approximation)
    if abs(rho) < 1.0:
        t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2))
    else:
        t_stat = float('inf')

    print(f"  Spearman rho: {rho:.3f} (n={n})")

    if rho < -0.3 and n >= 10:
        verdict = 'GRADIENT_PRESENT'
    elif rho < -0.15:
        verdict = 'WEAK_GRADIENT'
    else:
        verdict = 'NO_GRADIENT'

    return {
        'pairs': pairs,
        'n_pairs': n,
        'spearman_rho': rho,
        't_stat': t_stat,
        'verdict': verdict,
    }


def _rank(values):
    """Simple ranking (average rank for ties)."""
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 1) / 2  # 1-based average
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def p3_cardinal_kernel(ra, morph):
    """P3: Does cardinal position predict kernel character balance?"""
    print("\n=== P3: Cardinal Kernel Profile ===")

    per_rosette = {}
    for rname in ra.get_rosettes():
        tokens = ra.get_entity_tokens(rname)
        k_count = h_count = e_count = 0
        total_kernel = 0
        for t in tokens:
            mid = t.get('middle', '')
            if mid:
                for c in mid:
                    if c == 'k':
                        k_count += 1
                    elif c == 'h':
                        h_count += 1
                    elif c == 'e':
                        e_count += 1
                total_kernel += sum(1 for c in mid if c in KERNEL_CHARS)

        total_chars = k_count + h_count + e_count
        per_rosette[rname] = {
            'k': k_count, 'h': h_count, 'e': e_count,
            'total_kernel_chars': total_chars,
            'k_frac': k_count / total_chars if total_chars else 0,
            'h_frac': h_count / total_chars if total_chars else 0,
            'e_frac': e_count / total_chars if total_chars else 0,
            'token_count': len(tokens),
        }
        print(f"  {rname:10s}: k={k_count} h={h_count} e={e_count} "
              f"({per_rosette[rname]['k_frac']:.0%}/{per_rosette[rname]['h_frac']:.0%}/{per_rosette[rname]['e_frac']:.0%})")

    # Check variance: does position predict kernel balance?
    k_fracs = [d['k_frac'] for d in per_rosette.values() if d['total_kernel_chars'] >= 5]
    if len(k_fracs) >= 5:
        mean_k = sum(k_fracs) / len(k_fracs)
        var_k = sum((x - mean_k) ** 2 for x in k_fracs) / len(k_fracs)
        cv_k = math.sqrt(var_k) / mean_k if mean_k else 0
        print(f"  k-fraction CV: {cv_k:.3f} (higher = more position-dependent)")
    else:
        cv_k = 0

    if cv_k > 0.30:
        verdict = 'POSITION_PREDICTS_KERNEL'
    else:
        verdict = 'UNIFORM_KERNEL'

    return {
        'per_rosette': per_rosette,
        'k_fraction_cv': cv_k,
        'verdict': verdict,
    }


# ============================================================
# COMBINED VERDICT
# ============================================================

def combined_verdict(results):
    """Synthesize all 13 tests into overall classification."""

    # Tier 1: System classification by entity type
    # Collect verdicts across S1-S4 for each entity type
    entity_types = set()
    for test_key in ['S1', 'S2', 'S3', 'S4']:
        if test_key in results and 'verdicts' in results[test_key]:
            entity_types.update(results[test_key]['verdicts'].keys())

    type_classifications = {}
    for etype in entity_types:
        signals = {'B': 0, 'AZC': 0, 'A': 0, 'OTHER': 0}
        for test_key in ['S1', 'S2', 'S3', 'S4']:
            v = results.get(test_key, {}).get('verdicts', {}).get(etype, '')
            if 'B_LIKE' in v:
                signals['B'] += 1
            elif 'AZC_LIKE' in v:
                signals['AZC'] += 1
            elif 'A_LIKE' in v:
                signals['A'] += 1
            else:
                signals['OTHER'] += 1
        best = max(signals, key=signals.get)
        type_classifications[etype] = {'signals': signals, 'classification': best}

    unique_systems = set(d['classification'] for d in type_classifications.values())
    tier1 = 'MULTI_SYSTEM' if len(unique_systems) >= 2 else 'SINGLE_SYSTEM'

    # Add S6 morphological profile
    if 'S6' in results:
        for etype, verdict in results['S6'].get('verdicts', {}).items():
            if etype in type_classifications:
                type_classifications[etype]['morphological_match'] = verdict

    # Tier 2: Cross-reference
    x1_verdict = results.get('X1', {}).get('verdict', '')
    x2_verdict = results.get('X2', {}).get('verdict', '')
    x3_verdict = results.get('X3', {}).get('verdict', '')
    x4_verdict = results.get('X4', {}).get('verdict', '')

    bridge_enriched = x1_verdict == 'BRIDGE_ENRICHED'
    multi_section = x2_verdict in ('MULTI_SECTION', 'DUAL_SECTION')
    specific_index = x3_verdict in ('SPECIFIC_INDEX', 'MODERATE_SPECIFICITY')

    if bridge_enriched and (multi_section or specific_index):
        tier2 = 'METALAYER_CONFIRMED'
    elif bridge_enriched:
        tier2 = 'BRIDGE_MEDIATED_ONLY'
    else:
        tier2 = 'NO_METALAYER_SIGNAL'

    # Tier 3: Spatial structure
    p1_verdict = results.get('P1', {}).get('verdict', '')
    p2_verdict = results.get('P2', {}).get('verdict', '')

    if p1_verdict == 'BRIDGING' and p2_verdict in ('GRADIENT_PRESENT', 'WEAK_GRADIENT'):
        tier3 = 'SPATIALLY_ORGANIZED'
    elif p1_verdict == 'BRIDGING' or p2_verdict in ('GRADIENT_PRESENT', 'WEAK_GRADIENT'):
        tier3 = 'PARTIAL_SPATIAL_STRUCTURE'
    else:
        tier3 = 'SPATIAL_STRUCTURE_ABSENT'

    # Overall
    if tier1 == 'MULTI_SYSTEM' and tier2 == 'METALAYER_CONFIRMED' and tier3 == 'SPATIALLY_ORGANIZED':
        overall = 'ROSETTES_CONFIRMED_SPATIAL_METALAYER'
    elif tier1 == 'MULTI_SYSTEM' and tier2 == 'METALAYER_CONFIRMED':
        overall = 'ROSETTES_CONFIRMED_METALAYER'
    elif tier1 == 'MULTI_SYSTEM' and tier2 == 'BRIDGE_MEDIATED_ONLY':
        overall = 'ROSETTES_VOCABULARY_HUB'
    elif tier1 == 'SINGLE_SYSTEM':
        overall = 'ROSETTES_SINGLE_SYSTEM_PAGE'
    else:
        overall = 'ROSETTES_INCONCLUSIVE'

    return {
        'tier1_classification': tier1,
        'tier2_crossref': tier2,
        'tier3_spatial': tier3,
        'overall': overall,
        'type_classifications': type_classifications,
        'unique_systems': sorted(unique_systems),
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 402: Rosettes System Revalidation")
    print("=" * 60)

    morph = Morphology()
    ra = RosettesAnalyzer()

    print("\nLoading reference data...")
    refs = load_references(morph)
    print(f"  B corpus: {refs['b_token_count']} tokens, {len(refs['b_all_middles'])} unique MIDDLEs")
    print(f"  Bridge set: {len(refs['bridge_set'])} MIDDLEs")
    print(f"  RI/PP: {len(refs['ri_set'])} RI, {len(refs['pp_set'])} PP")
    print(f"  49-class map: {len(refs['token_to_class'])} token types")

    print("\nGrouping Rosettes tokens by entity type...")
    type_groups, entity_groups = group_by_entity_type(ra)
    for tname, tokens in sorted(type_groups.items()):
        print(f"  {tname:20s}: {len(tokens)} tokens")

    results = {
        'phase': 402,
        'name': 'ROSETTES_SYSTEM_REVALIDATION',
        'supersedes': 'Phase 387/388H (ROSETTES_SYSTEM_CLASSIFICATION)',
        'data_source': 'data/rosettes_annotated.json (ZL + manual annotation)',
        'test_count': 13,
    }

    # ---- TIER 1: System Classification ----
    print("\n" + "=" * 60)
    print("TIER 1: SYSTEM CLASSIFICATION")
    print("=" * 60)

    results['S1'] = s1_grammar_coverage(type_groups, entity_groups, refs['token_to_class'], refs)
    results['S2'] = s2_kernel_density(type_groups, entity_groups, refs)
    results['S3'] = s3_link_density(type_groups, entity_groups, refs)
    results['S4'] = s4_pp_ri_composition(type_groups, entity_groups, refs)
    results['S5'] = s5_sequential_grammar(ra, morph)
    results['S6'] = s6_morphological_profile(type_groups, refs)

    # ---- TIER 2: Cross-Reference Validation ----
    print("\n" + "=" * 60)
    print("TIER 2: CROSS-REFERENCE VALIDATION")
    print("=" * 60)

    results['X1'] = x1_bridge_enrichment(ra, type_groups, refs)
    results['X2'] = x2_section_correlation(ra, refs, morph)
    results['X3'] = x3_folio_crossref(ra, refs, morph)
    results['X4'] = x4_middle_compatibility(ra, refs)

    # ---- TIER 3: Spatial Structure ----
    print("\n" + "=" * 60)
    print("TIER 3: SPATIAL STRUCTURE")
    print("=" * 60)

    results['P1'] = p1_path_bridging(ra)
    results['P2'] = p2_adjacency_gradient(ra)
    results['P3'] = p3_cardinal_kernel(ra, morph)

    # ---- COMBINED VERDICT ----
    print("\n" + "=" * 60)
    print("COMBINED VERDICT")
    print("=" * 60)

    verdict = combined_verdict(results)
    results['verdict'] = verdict

    print(f"\n  Tier 1 (System Classification): {verdict['tier1_classification']}")
    print(f"    Entity type systems: {verdict['unique_systems']}")
    for etype, info in sorted(verdict['type_classifications'].items()):
        print(f"      {etype:20s}: {info['classification']} (signals: {info['signals']})")
    print(f"  Tier 2 (Cross-Reference): {verdict['tier2_crossref']}")
    print(f"  Tier 3 (Spatial Structure): {verdict['tier3_spatial']}")
    print(f"\n  OVERALL: {verdict['overall']}")

    # ---- SAVE ----
    out_path = PROJECT / 'phases' / 'ROSETTES_SYSTEM_REVALIDATION' / 'results' / 'rosettes_revalidation_results.json'
    out_path.write_text(json.dumps(round_floats(results), indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\nResults saved: {out_path}")


if __name__ == '__main__':
    main()
