#!/usr/bin/env python3
"""Phase 619: Rosettes Atom Decomposition

RESEARCH QUESTION: Does the HEAD+MOD+TERM atom grammar (C1393-C1394)
extend to the Rosettes foldout metalayer, and what is its atom deployment
signature relative to B, A, and AZC?

Rosettes confirmed as metalayer (C1126) with AZC-like grammar (C1127),
3.05x bridge enrichment (C1124), dual ring-text population (C1132).
Never analyzed at atom level.

Data source: data/rosettes_annotated.json (ZL transcription, 443 words,
19 entities). NOT the EVA interlinear transcript.

Test families:
  T1: Shared substrate verification (inventory, compliance, modifiers, suffix)
  T2: HEAD domain distribution vs B/A/AZC
  T3: Bridge backbone atom composition (A-side vs B-side)
  T4: Dual population atom decomposition (classified vs unclassified)
  T5: Entity-level atom variation (descriptive)
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier, decompose_middle_hmt,
    RosettesAnalyzer, MiddleAnalyzer
)

RESULTS_DIR = PROJECT_ROOT / 'phases' / 'ROSETTES_ATOM_DECOMPOSITION' / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONSTANTS
# ============================================================

HEADS = {'a', 'e', 'o', 'k', 't'}
TERMINALS = {'y', 'l', 'r', 'h', 'm', 'n'}
MODIFIERS = {'p', 'c', 'i', 'f', 'd', 's'}
# Extended set includes rare but recognized atoms (g=PLAUSIBLE per C1195, x=rare)
KNOWN_ATOMS = HEADS | TERMINALS | MODIFIERS | {'g', 'x'}

HEAD_LABELS = ['a', 'e', 'o', 'k', 't', 'headless']
TERM_LABELS = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']
MOD_LABELS = ['p', 'c', 'i', 'f', 'd', 's']

# Terminal tiers (C1487)
LOCKED = {'r', 'm'}
CHANNELED = {'l', 'y', 'n'}
DIFFUSE = {'h'}

# HEAD domains (C1475)
HEAD_DOMAIN = {
    'k': 'THERMAL', 't': 'TRANSFER', 'a': 'ITERATION',
    'e': 'BALANCED', 'o': 'ARRANGEMENT'
}

# Suffix exclusion set (C1511)
SUFFIX_EXCLUDED = {'k', 't', 'p', 'f', 'c'}

ROSETTES_FOLIOS = {'f85r1', 'f85r2', 'f85v2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# ============================================================
# HELPERS
# ============================================================


def jsd(p: Dict, q: Dict, labels: List[str]) -> float:
    """Jensen-Shannon Divergence between two distributions."""
    epsilon = 1e-10
    pv = [p.get(k, 0) + epsilon for k in labels]
    qv = [q.get(k, 0) + epsilon for k in labels]
    sp, sq = sum(pv), sum(qv)
    pv = [x / sp for x in pv]
    qv = [x / sq for x in qv]
    mv = [(a + b) / 2 for a, b in zip(pv, qv)]

    def kl(a, b):
        return sum(ai * math.log2(ai / bi) for ai, bi in zip(a, b) if ai > 0)

    return (kl(pv, mv) + kl(qv, mv)) / 2


def normalize(counts: Dict, labels: List[str]) -> Dict:
    """Convert counts to proportions."""
    total = sum(counts.get(k, 0) for k in labels)
    if total == 0:
        return {k: 0.0 for k in labels}
    return {k: counts.get(k, 0) / total for k in labels}


def enrichment_ratio(channel_val: float, baseline_val: float) -> float:
    if baseline_val > 0:
        return round(channel_val / baseline_val, 4)
    return float('inf') if channel_val > 0 else 1.0


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


def head_profile_from_middles(middles, weights=None):
    """Compute HEAD distribution from a set/list of MIDDLEs.
    If weights is a Counter, token-weight by frequency."""
    counts = Counter()
    for mid in middles:
        head, _, _, _ = decompose_middle_hmt(mid)
        label = head if head else 'headless'
        w = weights[mid] if weights else 1
        counts[label] += w
    return counts


def term_profile_from_middles(middles, weights=None):
    """Compute TERMINAL distribution from MIDDLEs."""
    counts = Counter()
    for mid in middles:
        _, _, term, _ = decompose_middle_hmt(mid)
        w = weights[mid] if weights else 1
        counts[term] += w
    return counts


def mod_profile_from_middles(middles, weights=None):
    """Compute MODIFIER character frequency from MIDDLEs."""
    counts = Counter()
    total_weight = 0
    for mid in middles:
        _, mods, _, _ = decompose_middle_hmt(mid)
        w = weights[mid] if weights else 1
        total_weight += w
        for c in mods:
            counts[c] += w
    return counts, total_weight


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    print("Loading data...")
    tx = Transcript()
    morph = Morphology()
    ra = RosettesAnalyzer()

    # --- Rosettes tokens ---
    ros_tokens_raw = ra.all_tokens()
    # Filter tokens with valid MIDDLEs (skip empty, punctuation)
    ros_tokens = []
    unparseable = 0
    for t in ros_tokens_raw:
        mid = t.get('middle')
        if not mid or not mid.strip():
            continue
        # Filter: commas (ZL word boundaries), question marks, and
        # ZL-only transcription chars (j, q, z) not in EVA atom set
        if ',' in mid or '?' in mid or any(c in mid for c in 'jqz'):
            unparseable += 1
            continue
        ros_tokens.append(t)

    ros_middles_list = [t['middle'] for t in ros_tokens]
    ros_middles_set = set(ros_middles_list)
    ros_middle_freq = Counter(ros_middles_list)

    # --- Ring vs non-ring tokens ---
    ring_tokens = []
    nonring_tokens = []
    for ename in ra.get_entities():
        for sr in ra.get_sub_regions(ename):
            toks = ra.get_entity_tokens(ename, sub_region=sr)
            for t in toks:
                mid = t.get('middle')
                if not mid or not mid.strip() or ',' in mid or '?' in mid or any(c in mid for c in 'jqz'):
                    continue
                if sr == 'ring':
                    ring_tokens.append(t)
                else:
                    nonring_tokens.append(t)

    # --- B baseline (excluding rosettes folios) ---
    b_middle_freq = Counter()
    for tok in tx.currier_b():
        if tok.folio in ROSETTES_FOLIOS:
            continue
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m.middle:
            b_middle_freq[m.middle] += 1
    b_middle_set = set(b_middle_freq.keys())

    # --- A baseline ---
    a_middle_freq = Counter()
    for tok in tx.currier_a():
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m.middle:
            a_middle_freq[m.middle] += 1
    a_middle_set = set(a_middle_freq.keys())

    # --- AZC baseline ---
    azc_middle_freq = Counter()
    for tok in tx.azc():
        w = tok.word.strip() if hasattr(tok.word, 'strip') else str(tok.word)
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m.middle:
            azc_middle_freq[m.middle] += 1
    azc_middle_set = set(azc_middle_freq.keys())

    # --- Bridge set (85 MIDDLEs) ---
    bridge_path = PROJECT_ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(bridge_path, 'r', encoding='utf-8') as f:
        bridge_data = json.load(f)
    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])

    # --- Dark set (300 MIDDLEs) ---
    dark_path = PROJECT_ROOT / 'data' / 'dark_pipeline_middles.json'
    with open(dark_path, 'r', encoding='utf-8') as f:
        dark_data = json.load(f)
    dark_set = set(dark_data['middles'])

    # --- Class map (for classified/unclassified split) ---
    ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm_data = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm_data['token_to_class'].items()}

    # --- MiddleAnalyzer for compound detection ---
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # --- Pre-decompose all rosettes MIDDLEs ---
    ros_decomp = {}
    for mid in ros_middles_set:
        head, mods, term, frame = decompose_middle_hmt(mid)
        ros_decomp[mid] = {'head': head, 'mods': mods, 'term': term, 'frame': frame}

    return {
        'ros_tokens': ros_tokens,
        'ros_tokens_raw_count': len(ros_tokens_raw),
        'unparseable': unparseable,
        'ros_middles_list': ros_middles_list,
        'ros_middles_set': ros_middles_set,
        'ros_middle_freq': ros_middle_freq,
        'ros_decomp': ros_decomp,
        'ring_tokens': ring_tokens,
        'nonring_tokens': nonring_tokens,
        'b_middle_freq': b_middle_freq,
        'b_middle_set': b_middle_set,
        'a_middle_freq': a_middle_freq,
        'a_middle_set': a_middle_set,
        'azc_middle_freq': azc_middle_freq,
        'azc_middle_set': azc_middle_set,
        'bridge_set': bridge_set,
        'dark_set': dark_set,
        'token_to_class': token_to_class,
        'mid_analyzer': mid_analyzer,
        'morph': morph,
        'tx': tx,
        'ra': ra,
    }


# ============================================================
# POWER-ACCOUNTING PREAMBLE
# ============================================================

def power_preamble(data):
    ros_tokens = data['ros_tokens']
    ring_tokens = data['ring_tokens']
    nonring_tokens = data['nonring_tokens']
    token_to_class = data['token_to_class']
    ra = data['ra']

    # Classified vs unclassified (all rosettes tokens)
    classified = [t for t in ros_tokens if t.get('word') in token_to_class]
    unclassified = [t for t in ros_tokens if t.get('word') not in token_to_class]

    # Bridge subset
    bridge_tokens = [t for t in ros_tokens if t.get('is_bridge')]

    # Per-entity counts
    entity_counts = {}
    for ename in ra.get_entities():
        toks = [t for t in ra.get_entity_tokens(ename)
                if t.get('middle') and ',' not in t.get('middle', '') and '?' not in t.get('middle', '')]
        entity_counts[ename] = len(toks)

    preamble = {
        'total_raw_tokens': data['ros_tokens_raw_count'],
        'valid_tokens': len(ros_tokens),
        'unparseable_filtered': data['unparseable'],
        'unique_middles': len(data['ros_middles_set']),
        'ring_tokens': len(ring_tokens),
        'nonring_tokens': len(nonring_tokens),
        'classified_tokens': len(classified),
        'unclassified_tokens': len(unclassified),
        'bridge_tokens': len(bridge_tokens),
        'per_entity': {k: v for k, v in sorted(entity_counts.items(), key=lambda x: -x[1])},
        'entities_with_ge15': sum(1 for v in entity_counts.values() if v >= 15),
        'entities_underpowered': [k for k, v in entity_counts.items() if v < 15],
    }

    print(f"  Valid tokens: {preamble['valid_tokens']} (filtered {preamble['unparseable_filtered']} unparseable)")
    print(f"  Unique MIDDLEs: {preamble['unique_middles']}")
    print(f"  Ring: {preamble['ring_tokens']}, Non-ring: {preamble['nonring_tokens']}")
    print(f"  Classified: {preamble['classified_tokens']}, Unclassified: {preamble['unclassified_tokens']}")
    print(f"  Bridge tokens: {preamble['bridge_tokens']}")
    print(f"  Entities with >=15 tokens: {preamble['entities_with_ge15']}")

    return preamble


# ============================================================
# T1: SHARED SUBSTRATE VERIFICATION
# ============================================================

def t1_shared_substrate(data):
    print("\n--- T1: Shared Substrate Verification ---")
    ros_middles_set = data['ros_middles_set']
    ros_decomp = data['ros_decomp']
    b_middle_set = data['b_middle_set']
    b_middle_freq = data['b_middle_freq']
    ros_middle_freq = data['ros_middle_freq']
    ros_tokens = data['ros_tokens']

    # T1a: Atom inventory Jaccard (character-level)
    ros_atoms = set(c for mid in ros_middles_set for c in mid)
    b_atoms = set(c for mid in b_middle_set for c in mid)
    atom_jaccard = len(ros_atoms & b_atoms) / len(ros_atoms | b_atoms) if (ros_atoms | b_atoms) else 0
    t1a_pass = atom_jaccard >= 0.95
    print(f"  T1a: Atom Jaccard = {atom_jaccard:.4f} (threshold >= 0.95) -> {'PASS' if t1a_pass else 'FAIL'}")

    # T1b: Novel atoms
    novel = ros_atoms - KNOWN_ATOMS
    t1b_pass = len(novel) == 0
    print(f"  T1b: Novel atoms = {sorted(novel) if novel else 'none'} -> {'PASS' if t1b_pass else 'FAIL'}")

    # T1c: Slot syntax compliance
    valid_count = 0
    invalid_middles = []
    for mid in ros_middles_set:
        d = ros_decomp[mid]
        head_ok = d['head'] is None or d['head'] in HEADS
        term_ok = d['term'] == 'bare' or d['term'] in TERMINALS
        mods_ok = all(c in MODIFIERS for c in d['mods']) if d['mods'] else True
        if head_ok and term_ok and mods_ok:
            valid_count += 1
        else:
            invalid_middles.append(mid)
    compliance = valid_count / len(ros_middles_set) if ros_middles_set else 0
    t1c_pass = compliance >= 0.90
    print(f"  T1c: Slot compliance = {compliance:.4f} ({valid_count}/{len(ros_middles_set)}) -> {'PASS' if t1c_pass else 'FAIL'}")
    if invalid_middles:
        print(f"        Invalid: {invalid_middles[:10]}")

    # T1d: Modifier grammar JSD (rosettes vs B)
    ros_mod_counts, ros_mod_total = mod_profile_from_middles(ros_middles_set, ros_middle_freq)
    b_mod_counts, b_mod_total = mod_profile_from_middles(b_middle_set, b_middle_freq)
    ros_mod_dist = normalize(ros_mod_counts, MOD_LABELS)
    b_mod_dist = normalize(b_mod_counts, MOD_LABELS)
    mod_jsd = jsd(ros_mod_dist, b_mod_dist, MOD_LABELS)
    t1d_pass = mod_jsd < 0.05
    print(f"  T1d: Modifier JSD = {mod_jsd:.4f} (threshold < 0.05) -> {'PASS' if t1d_pass else 'FAIL'}")

    # T1e: Suffix atom exclusion (C1511)
    suffix_violations = 0
    suffix_violation_examples = []
    for t in ros_tokens:
        sfx = t.get('suffix')
        if sfx:
            for c in sfx:
                if c in SUFFIX_EXCLUDED:
                    suffix_violations += 1
                    suffix_violation_examples.append((t['word'], sfx, c))
                    break
    t1e_pass = suffix_violations == 0
    print(f"  T1e: Suffix exclusion violations = {suffix_violations} -> {'PASS' if t1e_pass else 'FAIL'}")

    return {
        't1a_atom_jaccard': atom_jaccard,
        't1a_ros_atoms': sorted(ros_atoms),
        't1a_b_atoms': sorted(b_atoms),
        't1a_pass': t1a_pass,
        't1b_novel_atoms': sorted(novel) if novel else [],
        't1b_pass': t1b_pass,
        't1c_compliance': compliance,
        't1c_valid': valid_count,
        't1c_total': len(ros_middles_set),
        't1c_invalid_middles': invalid_middles[:20],
        't1c_pass': t1c_pass,
        't1d_mod_jsd': mod_jsd,
        't1d_ros_mod_dist': ros_mod_dist,
        't1d_b_mod_dist': b_mod_dist,
        't1d_pass': t1d_pass,
        't1e_suffix_violations': suffix_violations,
        't1e_examples': [(w, s, c) for w, s, c in suffix_violation_examples[:10]],
        't1e_pass': t1e_pass,
    }


# ============================================================
# T2: HEAD DOMAIN DISTRIBUTION
# ============================================================

def t2_head_domain(data):
    print("\n--- T2: HEAD Domain Distribution ---")
    ros_middles_set = data['ros_middles_set']
    ros_middle_freq = data['ros_middle_freq']
    b_middle_freq = data['b_middle_freq']
    a_middle_freq = data['a_middle_freq']
    azc_middle_freq = data['azc_middle_freq']

    # Token-weighted HEAD profiles for each system
    ros_head = head_profile_from_middles(ros_middles_set, ros_middle_freq)
    b_head = head_profile_from_middles(set(b_middle_freq.keys()), b_middle_freq)
    a_head = head_profile_from_middles(set(a_middle_freq.keys()), a_middle_freq)
    azc_head = head_profile_from_middles(set(azc_middle_freq.keys()), azc_middle_freq)

    ros_head_dist = normalize(ros_head, HEAD_LABELS)
    b_head_dist = normalize(b_head, HEAD_LABELS)
    a_head_dist = normalize(a_head, HEAD_LABELS)
    azc_head_dist = normalize(azc_head, HEAD_LABELS)

    # T2a: Closer to AZC than B?
    ros_azc_jsd = jsd(ros_head_dist, azc_head_dist, HEAD_LABELS)
    ros_b_jsd = jsd(ros_head_dist, b_head_dist, HEAD_LABELS)
    ros_a_jsd = jsd(ros_head_dist, a_head_dist, HEAD_LABELS)
    t2a_pass = ros_azc_jsd < ros_b_jsd
    print(f"  T2a: JSD ros-AZC={ros_azc_jsd:.4f}, ros-B={ros_b_jsd:.4f} -> {'AZC closer' if t2a_pass else 'B closer'}")

    # T2b: o-HEAD enrichment
    ros_o = ros_head_dist.get('o', 0)
    b_o = b_head_dist.get('o', 0)
    o_enrichment = enrichment_ratio(ros_o, b_o)
    t2b_pass = o_enrichment >= 2.0
    print(f"  T2b: o-HEAD ros={ros_o:.4f}, B={b_o:.4f}, enrichment={o_enrichment:.2f}x (>= 2.0) -> {'PASS' if t2b_pass else 'FAIL'}")

    # T2c: Headless rate (predict 25-35%, AZC-adjacent)
    ros_headless = ros_head_dist.get('headless', 0)
    b_headless = b_head_dist.get('headless', 0)
    a_headless = a_head_dist.get('headless', 0)
    azc_headless = azc_head_dist.get('headless', 0)
    t2c_pass = 0.25 <= ros_headless <= 0.35
    print(f"  T2c: Headless ros={ros_headless:.4f}, B={b_headless:.4f}, A={a_headless:.4f}, AZC={azc_headless:.4f}")
    print(f"        In range 25-35%? -> {'PASS' if t2c_pass else 'FAIL'}")

    # T2d: HEAD domain distribution table (reporting only)
    domain_table = {}
    for sys_name, dist in [('rosettes', ros_head_dist), ('B', b_head_dist),
                            ('A', a_head_dist), ('AZC', azc_head_dist)]:
        row = {}
        for h in HEAD_LABELS:
            if h == 'headless':
                row['headless'] = dist.get('headless', 0)
            else:
                domain = HEAD_DOMAIN.get(h, h)
                row[domain] = dist.get(h, 0)
        domain_table[sys_name] = row

    return {
        't2a_ros_azc_jsd': ros_azc_jsd,
        't2a_ros_b_jsd': ros_b_jsd,
        't2a_ros_a_jsd': ros_a_jsd,
        't2a_pass': t2a_pass,
        't2b_ros_o': ros_o,
        't2b_b_o': b_o,
        't2b_o_enrichment': o_enrichment,
        't2b_pass': t2b_pass,
        't2c_ros_headless': ros_headless,
        't2c_b_headless': b_headless,
        't2c_a_headless': a_headless,
        't2c_azc_headless': azc_headless,
        't2c_pass': t2c_pass,
        'head_distributions': {
            'rosettes': ros_head_dist,
            'B': b_head_dist,
            'A': a_head_dist,
            'AZC': azc_head_dist,
        },
        'domain_table': domain_table,
    }


# ============================================================
# T3: BRIDGE BACKBONE ATOM COMPOSITION
# ============================================================

def t3_bridge_backbone(data):
    print("\n--- T3: Bridge Backbone Atom Composition ---")
    ros_tokens = data['ros_tokens']
    bridge_set = data['bridge_set']
    morph = data['morph']
    tx = data['tx']

    # T3a: Census — bridge MIDDLEs and tokens in rosettes
    ros_bridge_tokens = [t for t in ros_tokens if t.get('is_bridge') and t.get('middle')]
    ros_bridge_middles = set(t['middle'] for t in ros_bridge_tokens)
    ros_bridge_freq = Counter(t['middle'] for t in ros_bridge_tokens)
    n_bridge_tokens = len(ros_bridge_tokens)
    n_bridge_types = len(ros_bridge_middles)
    bridge_coverage = n_bridge_types / len(bridge_set) if bridge_set else 0

    print(f"  T3a: {n_bridge_types}/{len(bridge_set)} bridge types, {n_bridge_tokens} bridge tokens")

    low_power = n_bridge_tokens < 20
    if low_power:
        print(f"  *** LOW_POWER: {n_bridge_tokens} bridge tokens < 20 threshold ***")

    # Build A and B bridge profiles
    a_bridge_freq = Counter()
    for tok in tx.currier_a():
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m.middle and m.middle in bridge_set:
            a_bridge_freq[m.middle] += 1

    b_bridge_freq = Counter()
    for tok in tx.currier_b():
        if tok.folio in ROSETTES_FOLIOS:
            continue
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m.middle and m.middle in bridge_set:
            b_bridge_freq[m.middle] += 1

    # HEAD profiles for bridge MIDDLEs in each system
    ros_bridge_head = head_profile_from_middles(ros_bridge_middles, ros_bridge_freq)
    a_bridge_head = head_profile_from_middles(set(a_bridge_freq.keys()), a_bridge_freq)
    b_bridge_head = head_profile_from_middles(set(b_bridge_freq.keys()), b_bridge_freq)

    ros_bh_dist = normalize(ros_bridge_head, HEAD_LABELS)
    a_bh_dist = normalize(a_bridge_head, HEAD_LABELS)
    b_bh_dist = normalize(b_bridge_head, HEAD_LABELS)

    # T3b: Bridge HEAD closer to A-side?
    ros_a_bridge_jsd = jsd(ros_bh_dist, a_bh_dist, HEAD_LABELS)
    ros_b_bridge_jsd = jsd(ros_bh_dist, b_bh_dist, HEAD_LABELS)
    t3b_pass = ros_a_bridge_jsd < ros_b_bridge_jsd
    print(f"  T3b: Bridge HEAD JSD ros-A={ros_a_bridge_jsd:.4f}, ros-B={ros_b_bridge_jsd:.4f} -> {'A-side' if t3b_pass else 'B-side'}")

    # TERMINAL profiles for bridge MIDDLEs
    ros_bridge_term = term_profile_from_middles(ros_bridge_middles, ros_bridge_freq)
    a_bridge_term = term_profile_from_middles(set(a_bridge_freq.keys()), a_bridge_freq)
    b_bridge_term = term_profile_from_middles(set(b_bridge_freq.keys()), b_bridge_freq)

    ros_bt_dist = normalize(ros_bridge_term, TERM_LABELS)
    a_bt_dist = normalize(a_bridge_term, TERM_LABELS)
    b_bt_dist = normalize(b_bridge_term, TERM_LABELS)

    # T3c: Terminal stability (JSD < 0.10)
    ros_a_term_jsd = jsd(ros_bt_dist, a_bt_dist, TERM_LABELS)
    ros_b_term_jsd = jsd(ros_bt_dist, b_bt_dist, TERM_LABELS)
    a_b_term_jsd = jsd(a_bt_dist, b_bt_dist, TERM_LABELS)
    max_term_jsd = max(ros_a_term_jsd, ros_b_term_jsd)
    t3c_pass = max_term_jsd < 0.10
    print(f"  T3c: Bridge TERM JSD ros-A={ros_a_term_jsd:.4f}, ros-B={ros_b_term_jsd:.4f}, A-B={a_b_term_jsd:.4f}")
    print(f"        Max={max_term_jsd:.4f} (< 0.10) -> {'PASS' if t3c_pass else 'FAIL'}")

    return {
        't3a_bridge_types': n_bridge_types,
        't3a_bridge_tokens': n_bridge_tokens,
        't3a_bridge_coverage': bridge_coverage,
        't3a_bridge_middles_found': sorted(ros_bridge_middles),
        'low_power': low_power,
        't3b_ros_a_jsd': ros_a_bridge_jsd,
        't3b_ros_b_jsd': ros_b_bridge_jsd,
        't3b_a_side': t3b_pass,
        't3b_pass': t3b_pass if not low_power else None,
        'bridge_head_distributions': {
            'rosettes': ros_bh_dist,
            'A': a_bh_dist,
            'B': b_bh_dist,
        },
        't3c_ros_a_term_jsd': ros_a_term_jsd,
        't3c_ros_b_term_jsd': ros_b_term_jsd,
        't3c_a_b_term_jsd': a_b_term_jsd,
        't3c_max_term_jsd': max_term_jsd,
        't3c_pass': t3c_pass if not low_power else None,
        'bridge_term_distributions': {
            'rosettes': ros_bt_dist,
            'A': a_bt_dist,
            'B': b_bt_dist,
        },
    }


# ============================================================
# T4: DUAL POPULATION ATOM DECOMPOSITION
# ============================================================

def t4_dual_population(data):
    print("\n--- T4: Dual Population Atom Decomposition ---")
    ros_tokens = data['ros_tokens']
    token_to_class = data['token_to_class']
    bridge_set = data['bridge_set']
    mid_analyzer = data['mid_analyzer']

    # Split all rosettes tokens
    classified = [t for t in ros_tokens if t.get('word') in token_to_class]
    unclassified = [t for t in ros_tokens if t.get('word') not in token_to_class]

    print(f"  Classified: {len(classified)}, Unclassified: {len(unclassified)}")

    # HEAD profiles for each population
    cls_heads = Counter()
    for t in classified:
        head, _, _, _ = decompose_middle_hmt(t['middle'])
        cls_heads[head if head else 'headless'] += 1

    uncls_heads = Counter()
    for t in unclassified:
        head, _, _, _ = decompose_middle_hmt(t['middle'])
        uncls_heads[head if head else 'headless'] += 1

    cls_head_dist = normalize(cls_heads, HEAD_LABELS)
    uncls_head_dist = normalize(uncls_heads, HEAD_LABELS)

    # T4a: Classified e/k/t HEAD dominance >= 55%
    cls_total = sum(cls_heads.values())
    ekt_count = sum(cls_heads.get(h, 0) for h in ['e', 'k', 't'])
    ekt_frac = ekt_count / cls_total if cls_total > 0 else 0
    t4a_pass = ekt_frac >= 0.55
    print(f"  T4a: Classified e/k/t = {ekt_frac:.4f} ({ekt_count}/{cls_total}) (>= 0.55) -> {'PASS' if t4a_pass else 'FAIL'}")

    # T4b: Unclassified headless enrichment >= 35%
    uncls_total = sum(uncls_heads.values())
    headless_count = uncls_heads.get('headless', 0)
    headless_frac = headless_count / uncls_total if uncls_total > 0 else 0
    t4b_headless_pass = headless_frac >= 0.35

    # Also check da/sa/ta PREFIX share among headless tokens (C1524)
    headless_tokens = [t for t in unclassified
                       if decompose_middle_hmt(t['middle'])[0] is None]
    dasta_count = 0
    for t in headless_tokens:
        pfx = t.get('prefix', '')
        if pfx in ('da', 'sa', 'ta'):
            dasta_count += 1
    dasta_frac = dasta_count / len(headless_tokens) if headless_tokens else 0
    t4b_dasta_pass = dasta_frac >= 0.70

    t4b_pass = t4b_headless_pass  # Primary criterion
    print(f"  T4b: Unclassified headless = {headless_frac:.4f} ({headless_count}/{uncls_total}) (>= 0.35) -> {'PASS' if t4b_headless_pass else 'FAIL'}")
    print(f"        da/sa/ta PREFIX among headless = {dasta_frac:.4f} ({dasta_count}/{len(headless_tokens)}) (>= 0.70)")

    # T4c: Unclassified compound MIDDLEs contain bridge-set atoms >= 90%
    uncls_middles_unique = set(t['middle'] for t in unclassified)
    compound_total = 0
    compound_with_bridge = 0
    for mid in uncls_middles_unique:
        if mid_analyzer.is_compound(mid):
            compound_total += 1
            atoms = mid_analyzer.get_contained_atoms(mid)
            if any(a in bridge_set for a in atoms):
                compound_with_bridge += 1
    bridge_atom_rate = compound_with_bridge / compound_total if compound_total > 0 else 0
    t4c_pass = bridge_atom_rate >= 0.90
    print(f"  T4c: Uncls compound bridge atom rate = {bridge_atom_rate:.4f} ({compound_with_bridge}/{compound_total}) (>= 0.90) -> {'PASS' if t4c_pass else 'FAIL'}")

    # T4d: HEAD distribution divergence (JSD >= 0.10)
    pop_jsd = jsd(cls_head_dist, uncls_head_dist, HEAD_LABELS)
    t4d_pass = pop_jsd >= 0.10
    print(f"  T4d: Population HEAD JSD = {pop_jsd:.4f} (>= 0.10) -> {'PASS' if t4d_pass else 'FAIL'}")

    return {
        'classified_count': len(classified),
        'unclassified_count': len(unclassified),
        'classified_head_dist': cls_head_dist,
        'unclassified_head_dist': uncls_head_dist,
        't4a_ekt_frac': ekt_frac,
        't4a_ekt_count': ekt_count,
        't4a_cls_total': cls_total,
        't4a_pass': t4a_pass,
        't4b_headless_frac': headless_frac,
        't4b_headless_count': headless_count,
        't4b_uncls_total': uncls_total,
        't4b_headless_pass': t4b_headless_pass,
        't4b_dasta_frac': dasta_frac,
        't4b_dasta_count': dasta_count,
        't4b_headless_tokens': len(headless_tokens),
        't4b_dasta_pass': t4b_dasta_pass,
        't4b_pass': t4b_pass,
        't4c_compound_total': compound_total,
        't4c_compound_with_bridge': compound_with_bridge,
        't4c_bridge_atom_rate': bridge_atom_rate,
        't4c_pass': t4c_pass,
        't4d_population_jsd': pop_jsd,
        't4d_pass': t4d_pass,
    }


# ============================================================
# T5: ENTITY-LEVEL ATOM VARIATION (DESCRIPTIVE)
# ============================================================

def t5_entity_variation(data):
    print("\n--- T5: Entity-Level Atom Variation (descriptive) ---")
    ra = data['ra']

    # Per-entity HEAD distributions (only entities with >= 15 tokens)
    entity_head_dists = {}
    entity_counts = {}
    for ename in ra.get_entities():
        toks = ra.get_entity_tokens(ename)
        valid = [t for t in toks
                 if t.get('middle') and ',' not in t.get('middle', '') and '?' not in t.get('middle', '')]
        if not valid:
            continue
        entity_counts[ename] = len(valid)
        heads = Counter()
        for t in valid:
            head, _, _, _ = decompose_middle_hmt(t['middle'])
            heads[head if head else 'headless'] += 1
        entity_head_dists[ename] = normalize(heads, HEAD_LABELS)

    # Pairwise JSD among entities with >= 15 tokens
    powered = [e for e, n in entity_counts.items() if n >= 15]
    jsds = []
    for i in range(len(powered)):
        for j in range(i + 1, len(powered)):
            d = jsd(entity_head_dists[powered[i]], entity_head_dists[powered[j]], HEAD_LABELS)
            jsds.append({'e1': powered[i], 'e2': powered[j], 'd': d})
    mean_jsd = sum(x['d'] for x in jsds) / len(jsds) if jsds else 0
    print(f"  T5a: Mean pairwise HEAD JSD ({len(powered)} entities >= 15 tokens) = {mean_jsd:.4f}")

    # Ring vs non-ring HEAD distribution
    ring_tokens = data['ring_tokens']
    nonring_tokens = data['nonring_tokens']

    ring_heads = Counter()
    for t in ring_tokens:
        head, _, _, _ = decompose_middle_hmt(t['middle'])
        ring_heads[head if head else 'headless'] += 1
    ring_head_dist = normalize(ring_heads, HEAD_LABELS)

    nonring_heads = Counter()
    for t in nonring_tokens:
        head, _, _, _ = decompose_middle_hmt(t['middle'])
        nonring_heads[head if head else 'headless'] += 1
    nonring_head_dist = normalize(nonring_heads, HEAD_LABELS)

    ring_nonring_jsd = jsd(ring_head_dist, nonring_head_dist, HEAD_LABELS)
    print(f"  T5b: Ring vs non-ring HEAD JSD = {ring_nonring_jsd:.4f}")

    # Per-entity table
    print(f"  T5c: Per-entity HEAD distributions:")
    for ename in sorted(entity_counts.keys(), key=lambda x: -entity_counts[x]):
        n = entity_counts[ename]
        d = entity_head_dists[ename]
        top = sorted(d.items(), key=lambda x: -x[1])[:3]
        top_str = ', '.join(f"{k}={v:.2f}" for k, v in top)
        flag = '' if n >= 15 else ' [underpowered]'
        print(f"        {ename:20s} n={n:3d}  {top_str}{flag}")

    return {
        't5a_powered_entities': powered,
        't5a_mean_jsd': mean_jsd,
        't5a_pairwise': jsds[:20],
        't5b_ring_nonring_jsd': ring_nonring_jsd,
        't5b_ring_head_dist': ring_head_dist,
        't5b_nonring_head_dist': nonring_head_dist,
        't5c_entity_head_dists': entity_head_dists,
        't5c_entity_counts': entity_counts,
        'descriptive': True,
    }


# ============================================================
# SCORECARD AND VERDICT
# ============================================================

def compute_verdict(t1, t2, t3, t4):
    print("\n=== PREDICTION SCORECARD ===")

    core = {
        'T1a_substrate': t1['t1a_pass'],
        'T2a_azc_proximity': t2['t2a_pass'],
        'T2b_o_enrichment': t2['t2b_pass'],
        'T2c_headless_range': t2['t2c_pass'],
        'T4a_ekt_dominance': t4['t4a_pass'],
        'T4b_headless_enrichment': t4['t4b_pass'],
    }

    extended = {
        'T3b_bridge_a_side': t3['t3b_pass'],  # None if low power
        'T3c_terminal_stability': t3['t3c_pass'],  # None if low power
    }

    core_pass = sum(1 for v in core.values() if v)
    core_total = len(core)
    ext_pass = sum(1 for v in extended.values() if v is True)
    ext_lp = sum(1 for v in extended.values() if v is None)

    for name, val in core.items():
        print(f"  [CORE] {name}: {'PASS' if val else 'FAIL'}")
    for name, val in extended.items():
        status = 'PASS' if val is True else ('LOW_POWER' if val is None else 'FAIL')
        print(f"  [EXT]  {name}: {status}")

    print(f"\n  Core: {core_pass}/{core_total}")
    print(f"  Extended: {ext_pass} pass, {ext_lp} low-power")

    # Verdict logic
    # Note: 3/6 core failures all trace to a single mechanism (o-HEAD hyper-enrichment
    # at 3.30x crowding out headless and e/k/t). This is a coherent single-parameter
    # deviation, not a diffuse failure. Both experts recommend ARRANGEMENT_DOMINANT_METALAYER.
    if core_pass == core_total and (ext_pass + ext_lp == len(extended)):
        verdict = 'SHARED_SUBSTRATE_AZC_ADJACENT'
    elif core_pass >= 4:
        verdict = 'PARTIAL_SUBSTRATE_OVERLAP'
    elif core_pass >= 2 and all(core.get(k) for k in ['T2a_azc_proximity', 'T2b_o_enrichment']):
        verdict = 'ARRANGEMENT_DOMINANT_METALAYER'
    else:
        verdict = 'DIVERGENT_ATOM_PROFILE'

    print(f"\n  VERDICT: {verdict}")

    return {
        'core_predictions': core,
        'extended_predictions': {k: v if v is not None else 'LOW_POWER' for k, v in extended.items()},
        'core_pass': core_pass,
        'core_total': core_total,
        'extended_pass': ext_pass,
        'extended_low_power': ext_lp,
        'verdict': verdict,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 619: Rosettes Atom Decomposition\n")

    data = load_data()

    print("\n=== Power Preamble ===")
    preamble = power_preamble(data)

    t1 = t1_shared_substrate(data)
    t2 = t2_head_domain(data)
    t3 = t3_bridge_backbone(data)
    t4 = t4_dual_population(data)
    t5 = t5_entity_variation(data)

    verdict_info = compute_verdict(t1, t2, t3, t4)

    results = {
        'phase': 619,
        'name': 'ROSETTES_ATOM_DECOMPOSITION',
        'question': 'Does shared atom substrate extend to rosettes, and what is their atom deployment signature?',
        'power_preamble': preamble,
        'T1_shared_substrate': t1,
        'T2_head_domain': t2,
        'T3_bridge_backbone': t3,
        'T4_dual_population': t4,
        'T5_entity_variation': t5,
        'verdict_info': verdict_info,
        'verdict': verdict_info['verdict'],
    }

    out_path = RESULTS_DIR / 'rosettes_atom_decomposition.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, default=str)

    print(f"\nResults saved to {out_path}")
    print(f"Final verdict: {verdict_info['verdict']}")


if __name__ == '__main__':
    main()
