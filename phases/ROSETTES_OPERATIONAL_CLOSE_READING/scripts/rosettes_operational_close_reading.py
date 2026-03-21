#!/usr/bin/env python3
"""Phase 620: Rosettes Operational Close Reading

RESEARCH QUESTION: What do the rosettes encode operationally? Apply the full
atom gloss, 8-category, and instruction encoding toolkit to produce per-entity
operational fingerprints and annotated token dumps for expert close reading.

Background:
  C1813: Shared atom substrate (Jaccard=0.950 with B)
  C1814: o-HEAD arrangement enrichment 3.30x (37.1%) — manuscript highest
  C1815: Bridge backbone A-side HEAD deployment
  C1816: Dual population converges at atom level (HEAD JSD=0.021)
  C1126: Rosettes metalayer confirmed
  C1127: AZC-like grammar
  C1128: Generic (not specific) indexing
  C1131: Ring text BRIDGE_VOCABULARY_INDEX
  C1132: Ring text dual population structure

Data source: data/rosettes_annotated.json (ZL transcription, 443 words,
19 entities). NOT the EVA interlinear transcript.

Produces:
  1. results/rosettes_operational_close_reading.json (quantitative)
  2. data/rosettes_entity_dumps.txt (annotated token sequences for AI reading)
"""

import sys
import json
import math
import random
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier, decompose_middle_hmt,
    RosettesAnalyzer, MiddleAnalyzer
)

RESULTS_DIR = PROJECT_ROOT / 'phases' / 'ROSETTES_OPERATIONAL_CLOSE_READING' / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = PROJECT_ROOT / 'phases' / 'ROSETTES_OPERATIONAL_CLOSE_READING' / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

try:
    from scipy.cluster.hierarchy import linkage, fcluster
    from scipy.spatial.distance import squareform
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# ============================================================
# CONSTANTS
# ============================================================

HEADS = {'a', 'e', 'o', 'k', 't'}
TERMINALS = {'y', 'l', 'r', 'h', 'm', 'n'}
MODIFIERS = {'p', 'c', 'i', 'f', 'd', 's'}
KNOWN_ATOMS = HEADS | TERMINALS | MODIFIERS | {'g', 'x'}

HEAD_LABELS = ['a', 'e', 'o', 'k', 't', 'headless']
TERM_LABELS = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']
MOD_LABELS = ['p', 'c', 'i', 'f', 'd', 's']
CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']

HEAD_DOMAIN = {
    'k': 'THERMAL', 't': 'TRANSFER', 'a': 'ITERATION',
    'e': 'BALANCED', 'o': 'ARRANGEMENT'
}

TERM_TIER = {
    'r': 'LOCKED', 'm': 'LOCKED',
    'l': 'CHANNELED', 'y': 'CHANNELED', 'n': 'CHANNELED',
    'h': 'DIFFUSE', 'bare': 'BARE'
}

ROSETTES_FOLIOS = {'f85r1', 'f85r2', 'f85v2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# Spatial adjacency: octagonal ring derived from PATH entities
# CENTER has no path connections -> non-adjacent to all
ADJACENCY = [
    frozenset({'WEST', 'NW'}), frozenset({'NW', 'NORTH'}),
    frozenset({'NORTH', 'NE'}), frozenset({'NE', 'EAST'}),
    frozenset({'EAST', 'SE'}), frozenset({'SE', 'SOUTH'}),
    frozenset({'SOUTH', 'SW'}), frozenset({'SW', 'WEST'}),
]

ROSETTE_NAMES = ['CENTER', 'NORTH', 'NE', 'EAST', 'SE', 'SOUTH', 'SW', 'WEST', 'NW']
SUB_REGION_ORDER = ['ring', 'paragraph', 'spiral', 'inner_label', 'outer_label', 'clock_text']


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


def round_floats(obj, digits=4):
    if isinstance(obj, float):
        return round(obj, digits)
    elif isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    elif isinstance(obj, set):
        return sorted(obj)
    elif isinstance(obj, frozenset):
        return sorted(obj)
    return obj


def cosine_sim(p: Dict, q: Dict, labels: List[str]) -> float:
    """Cosine similarity between two distributions."""
    pv = [p.get(k, 0) for k in labels]
    qv = [q.get(k, 0) for k in labels]
    dot = sum(a * b for a, b in zip(pv, qv))
    np = math.sqrt(sum(a * a for a in pv))
    nq = math.sqrt(sum(b * b for b in qv))
    if np == 0 or nq == 0:
        return 0.0
    return dot / (np * nq)


def head_profile_from_tokens(tokens, decomp_cache):
    """Compute HEAD distribution from token list."""
    counts = Counter()
    for t in tokens:
        mid = t.get('middle', '')
        if mid in decomp_cache:
            h = decomp_cache[mid]['head']
            counts[h if h else 'headless'] += 1
    return counts


def term_profile_from_tokens(tokens, decomp_cache):
    """Compute TERMINAL distribution from token list."""
    counts = Counter()
    for t in tokens:
        mid = t.get('middle', '')
        if mid in decomp_cache:
            counts[decomp_cache[mid]['term']] += 1
    return counts


def category_profile_from_tokens(tokens, decomp_cache, cc):
    """Compute 8-category distribution from token list."""
    counts = Counter()
    unclassified = 0
    for t in tokens:
        mid = t.get('middle', '')
        cat = cc.classify(mid)
        if cat:
            counts[cat] += 1
        else:
            unclassified += 1
    return counts, unclassified


def frame_hazard_for_token(head, frame_str, fh_map):
    """Compute frame hazard. k-HEAD and o-HEAD → IMMUNE per C1446/C1561."""
    if head == 'k' or head == 'o':
        return 'IMMUNE'
    if frame_str and frame_str in fh_map:
        return fh_map[frame_str]
    return 'LOW'


def atom_gloss_string(middle):
    """Dot-separated per-atom glosses from C1195."""
    glosses = CategoryClassifier.ATOM_GLOSSES
    return '.'.join(glosses.get(c, c) for c in middle)


def terminal_tier(term):
    """Return terminal tier per C1487."""
    return TERM_TIER.get(term, 'BARE')


def kernel_from_middle(middle):
    """Extract kernel characters from MIDDLE."""
    return [c for c in middle if c in {'k', 'h', 'e'}]


def bootstrap_category_jsd_null(all_middles_list, entity_sizes, cc, n_bootstrap=1000):
    """Bootstrap null for T1: resample pooled MIDDLEs into groups matching entity sizes.
    Returns 95th percentile of mean pairwise category JSD."""
    random.seed(42)
    null_means = []
    n_entities = len(entity_sizes)
    for _ in range(n_bootstrap):
        random.shuffle(all_middles_list)
        groups = []
        offset = 0
        for sz in entity_sizes:
            group_mids = all_middles_list[offset:offset + sz]
            offset += sz
            cat_counts = Counter()
            for mid in group_mids:
                cat = cc.classify(mid)
                if cat:
                    cat_counts[cat] += 1
            groups.append(normalize(cat_counts, CATEGORIES))
        # Mean pairwise JSD
        jsds = []
        for i in range(n_entities):
            for j in range(i + 1, n_entities):
                jsds.append(jsd(groups[i], groups[j], CATEGORIES))
        if jsds:
            null_means.append(sum(jsds) / len(jsds))
    null_means.sort()
    p95 = null_means[int(0.95 * len(null_means))] if null_means else 0.10
    return p95, null_means


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    print("Loading data...")
    tx = Transcript()
    morph = Morphology()
    ra = RosettesAnalyzer()
    cc = CategoryClassifier()

    # --- Rosettes tokens ---
    ros_tokens_raw = ra.all_tokens()
    ros_tokens = []
    unparseable = 0
    for t in ros_tokens_raw:
        mid = t.get('middle')
        if not mid or not mid.strip():
            continue
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

    # --- A baseline ---
    a_middle_freq = Counter()
    for tok in tx.currier_a():
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m.middle:
            a_middle_freq[m.middle] += 1

    # --- AZC baseline ---
    azc_middle_freq = Counter()
    for tok in tx.azc():
        w = tok.word.strip() if hasattr(tok.word, 'strip') else str(tok.word)
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m.middle:
            azc_middle_freq[m.middle] += 1

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

    # --- Class token map ---
    ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm_data = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm_data['token_to_class'].items()}

    # --- Frame hazard map (direct load, bypass BFolioDecoder) ---
    dm_path = PROJECT_ROOT / 'data' / 'decoder_maps.json'
    with open(dm_path, 'r', encoding='utf-8') as f:
        dm = json.load(f)
    fh_entries = dm['maps']['frame_hazard']['entries']
    frame_hazard_map = {k: v['value'] for k, v in fh_entries.items()}

    # --- MiddleAnalyzer ---
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # --- Pre-decompose all rosettes MIDDLEs ---
    ros_decomp = {}
    for mid in ros_middles_set:
        head, mods, term, frame = decompose_middle_hmt(mid)
        ros_decomp[mid] = {'head': head, 'mods': mods, 'term': term, 'frame': frame}

    # --- Build baseline HEAD/category profiles ---
    def build_baseline_profiles(freq_counter):
        head_counts = Counter()
        cat_counts = Counter()
        kern_counts = Counter()
        total = 0
        for mid, count in freq_counter.items():
            h, _, t, _ = decompose_middle_hmt(mid)
            label = h if h else 'headless'
            head_counts[label] += count
            cat = cc.classify(mid)
            if cat:
                cat_counts[cat] += count
            for c in mid:
                if c in {'k', 'h', 'e'}:
                    kern_counts[c] += count
            total += count
        return {
            'head': normalize(head_counts, HEAD_LABELS),
            'category': normalize(cat_counts, CATEGORIES),
            'kernel': normalize(kern_counts, ['k', 'h', 'e']),
            'total_tokens': total,
        }

    b_baseline = build_baseline_profiles(b_middle_freq)
    a_baseline = build_baseline_profiles(a_middle_freq)
    azc_baseline = build_baseline_profiles(azc_middle_freq)

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
        'a_middle_freq': a_middle_freq,
        'azc_middle_freq': azc_middle_freq,
        'bridge_set': bridge_set,
        'dark_set': dark_set,
        'token_to_class': token_to_class,
        'frame_hazard_map': frame_hazard_map,
        'mid_analyzer': mid_analyzer,
        'cc': cc,
        'morph': morph,
        'tx': tx,
        'ra': ra,
        'b_baseline': b_baseline,
        'a_baseline': a_baseline,
        'azc_baseline': azc_baseline,
    }


# ============================================================
# POWER-ACCOUNTING PREAMBLE
# ============================================================

def power_preamble(data):
    ros_tokens = data['ros_tokens']
    ra = data['ra']
    token_to_class = data['token_to_class']

    classified = [t for t in ros_tokens if t.get('word') in token_to_class]
    unclassified = [t for t in ros_tokens if t.get('word') not in token_to_class]

    print(f"\n{'='*70}")
    print("POWER-ACCOUNTING PREAMBLE")
    print(f"{'='*70}")
    print(f"Raw tokens: {data['ros_tokens_raw_count']}")
    print(f"Filtered (comma/ZL): {data['unparseable']}")
    print(f"Valid tokens: {len(ros_tokens)}")
    print(f"Ring tokens: {len(data['ring_tokens'])}")
    print(f"Non-ring tokens: {len(data['nonring_tokens'])}")
    print(f"Classified: {len(classified)}")
    print(f"Unclassified: {len(unclassified)}")

    print(f"\nPer-entity token counts:")
    entity_counts = {}
    for ename in ra.get_entities():
        toks = [t for t in ra.get_entity_tokens(ename)
                if t.get('middle') and ',' not in t.get('middle', '')
                and '?' not in t.get('middle', '')
                and not any(c in t.get('middle', '') for c in 'jqz')]
        entity_counts[ename] = len(toks)
        flag = " *** LOW POWER" if len(toks) < 15 else ""
        print(f"  {ename:20s}: {len(toks):4d}{flag}")

    print(f"\nBaseline sizes:")
    print(f"  B tokens: {data['b_baseline']['total_tokens']}")
    print(f"  AZC tokens: {data['azc_baseline']['total_tokens']}")
    print(f"  A tokens: {data['a_baseline']['total_tokens']}")

    return entity_counts


# ============================================================
# PER-ENTITY FINGERPRINTING
# ============================================================

def fingerprint_entity(entity_name, tokens, data):
    """Compute comprehensive operational fingerprint for an entity."""
    decomp = data['ros_decomp']
    cc = data['cc']
    bridge_set = data['bridge_set']
    dark_set = data['dark_set']
    token_to_class = data['token_to_class']
    mid_analyzer = data['mid_analyzer']
    fh_map = data['frame_hazard_map']

    n = len(tokens)
    if n == 0:
        return None

    middles = [t['middle'] for t in tokens]
    mid_freq = Counter(middles)

    # 1. HEAD distribution
    head_counts = head_profile_from_tokens(tokens, decomp)
    head_norm = normalize(head_counts, HEAD_LABELS)
    dominant_head = max(HEAD_LABELS, key=lambda k: head_norm[k])

    # 2. Headless rate
    headless_rate = head_norm.get('headless', 0)

    # 3. TERMINAL distribution + tier
    term_counts = term_profile_from_tokens(tokens, decomp)
    term_norm = normalize(term_counts, TERM_LABELS)
    tier_counts = Counter()
    for t_tok in tokens:
        mid = t_tok.get('middle', '')
        if mid in decomp:
            tier_counts[terminal_tier(decomp[mid]['term'])] += 1
    tier_norm = normalize(tier_counts, ['LOCKED', 'CHANNELED', 'DIFFUSE', 'BARE'])
    dominant_tier = max(['LOCKED', 'CHANNELED', 'DIFFUSE', 'BARE'], key=lambda k: tier_norm[k])

    # 4. MOD presence profile
    mod_counts = Counter()
    for t_tok in tokens:
        mid = t_tok.get('middle', '')
        if mid in decomp:
            for c in decomp[mid]['mods']:
                if c in MODIFIERS:
                    mod_counts[c] += 1
    mod_rates = {m: mod_counts.get(m, 0) / n for m in MOD_LABELS}

    # 5. Category distribution + confidence
    cat_counts, cat_unclass = category_profile_from_tokens(tokens, decomp, cc)
    cat_norm = normalize(cat_counts, CATEGORIES)
    cat_coverage = (n - cat_unclass) / n if n > 0 else 0
    # Confidence breakdown
    conf_counts = Counter()
    for mid in middles:
        conf = cc.confidence(mid)
        conf_counts[conf if conf else 'NONE'] += 1

    # 6. Kernel ratios
    kern_counts = Counter()
    for mid in middles:
        for c in mid:
            if c in {'k', 'h', 'e'}:
                kern_counts[c] += 1
    kern_total = sum(kern_counts.values()) or 1
    k_ratio = kern_counts.get('k', 0) / kern_total
    h_ratio = kern_counts.get('h', 0) / kern_total
    e_ratio = kern_counts.get('e', 0) / kern_total
    kern_frac = sum(kern_counts.values()) / sum(len(m) for m in middles) if middles else 0
    if e_ratio > 0.45:
        kern_balance = 'ESCAPE_DOMINANT'
    elif k_ratio > 0.50:
        kern_balance = 'ENERGY_DOMINANT'
    elif h_ratio > 0.30:
        kern_balance = 'HAZARD_HEAVY'
    else:
        kern_balance = 'BALANCED'

    # 7. Frame hazard summary
    hazard_counts = Counter()
    for t_tok in tokens:
        mid = t_tok.get('middle', '')
        if mid in decomp:
            d = decomp[mid]
            hz = frame_hazard_for_token(d['head'], d['frame'], fh_map)
            hazard_counts[hz] += 1
    hazard_norm = {k: hazard_counts.get(k, 0) / n for k in ['IMMUNE', 'ZERO', 'HIGH', 'LOW']}

    # 8. PREFIX distribution
    pfx_counts = Counter()
    for t_tok in tokens:
        pfx = t_tok.get('prefix')
        if pfx:
            pfx_counts[pfx] += 1
    pfx_rate = sum(pfx_counts.values()) / n
    # da/sa/ta fraction (headless gateway PREFIX per C1537)
    gateway_pfx = sum(pfx_counts.get(p, 0) for p in ['da', 'sa', 'ta'])
    gateway_frac = gateway_pfx / n

    # 9. Suffix rate
    sfx_count = sum(1 for t_tok in tokens if t_tok.get('suffix'))
    sfx_rate = sfx_count / n

    # 10. Bridge, dark, compound rates
    bridge_count = sum(1 for t_tok in tokens if t_tok.get('is_bridge'))
    bridge_rate = bridge_count / n
    dark_count = sum(1 for t_tok in tokens if t_tok.get('middle') in dark_set)
    dark_rate = dark_count / n
    compound_count = sum(1 for mid in middles if mid_analyzer.is_compound(mid))
    compound_rate = compound_count / n

    # 11. Classified/unclassified split with sub-profiles
    classified_toks = [t for t in tokens if t.get('word') in token_to_class]
    unclassified_toks = [t for t in tokens if t.get('word') not in token_to_class]
    classified_n = len(classified_toks)
    unclassified_n = len(unclassified_toks)

    def sub_profile(sub_toks):
        if not sub_toks:
            return {'n': 0, 'head': {}, 'category': {}, 'bridge_rate': 0, 'compound_rate': 0}
        sub_head = normalize(head_profile_from_tokens(sub_toks, decomp), HEAD_LABELS)
        sub_cat, _ = category_profile_from_tokens(sub_toks, decomp, cc)
        sub_cat_norm = normalize(sub_cat, CATEGORIES)
        sub_bridge = sum(1 for t in sub_toks if t.get('is_bridge')) / len(sub_toks)
        sub_compound = sum(1 for t in sub_toks if mid_analyzer.is_compound(t.get('middle', ''))) / len(sub_toks)
        return {
            'n': len(sub_toks),
            'head': sub_head,
            'category': sub_cat_norm,
            'bridge_rate': sub_bridge,
            'compound_rate': sub_compound,
        }

    classified_profile = sub_profile(classified_toks)
    unclassified_profile = sub_profile(unclassified_toks)

    # 12. Top-5 frames, top-5 MIDDLEs
    frame_counts = Counter()
    for mid in middles:
        if mid in decomp:
            frame_counts[decomp[mid]['frame']] += 1
    top_frames = frame_counts.most_common(5)
    top_middles = mid_freq.most_common(5)

    return {
        'token_count': n,
        'head': head_norm,
        'head_counts': dict(head_counts),
        'dominant_head': dominant_head,
        'headless_rate': headless_rate,
        'terminal': term_norm,
        'terminal_tier': tier_norm,
        'dominant_tier': dominant_tier,
        'mod_rates': mod_rates,
        'category': cat_norm,
        'category_coverage': cat_coverage,
        'confidence': {k: v / n for k, v in conf_counts.items()},
        'kernel': {'k': k_ratio, 'h': h_ratio, 'e': e_ratio},
        'kernel_fraction': kern_frac,
        'kernel_balance': kern_balance,
        'hazard': hazard_norm,
        'prefix_rate': pfx_rate,
        'prefix_inventory': dict(pfx_counts.most_common(10)),
        'gateway_prefix_fraction': gateway_frac,
        'suffix_rate': sfx_rate,
        'bridge_rate': bridge_rate,
        'dark_rate': dark_rate,
        'compound_rate': compound_rate,
        'classified': classified_profile,
        'unclassified': unclassified_profile,
        'top_frames': top_frames,
        'top_middles': top_middles,
    }


# ============================================================
# CROSS-ENTITY COMPARISONS
# ============================================================

def cross_entity_comparisons(entity_profiles, data):
    cc = data['cc']
    ros_middles_list = list(data['ros_middles_list'])  # mutable copy for bootstrap

    # Only 9 rosettes with sufficient tokens
    powered = [e for e in ROSETTE_NAMES if e in entity_profiles and entity_profiles[e]['token_count'] >= 20]
    print(f"\nCross-entity: {len(powered)} powered rosettes: {powered}")

    # 1. JSD matrices
    head_jsd_matrix = {}
    cat_jsd_matrix = {}
    for i, e1 in enumerate(powered):
        for j, e2 in enumerate(powered):
            if j <= i:
                continue
            pair = f"{e1}-{e2}"
            head_jsd_matrix[pair] = jsd(entity_profiles[e1]['head'],
                                        entity_profiles[e2]['head'], HEAD_LABELS)
            cat_jsd_matrix[pair] = jsd(entity_profiles[e1]['category'],
                                       entity_profiles[e2]['category'], CATEGORIES)

    head_jsds = list(head_jsd_matrix.values())
    cat_jsds = list(cat_jsd_matrix.values())
    mean_head_jsd = sum(head_jsds) / len(head_jsds) if head_jsds else 0
    mean_cat_jsd = sum(cat_jsds) / len(cat_jsds) if cat_jsds else 0
    max_cat_jsd = max(cat_jsds) if cat_jsds else 0
    max_cat_pair = max(cat_jsd_matrix, key=cat_jsd_matrix.get) if cat_jsd_matrix else ''

    # Flag pairs where both entities have < 30 tokens
    small_pairs = [pair for pair in cat_jsd_matrix
                   if entity_profiles[pair.split('-')[0]]['token_count'] < 30
                   and entity_profiles[pair.split('-')[1]]['token_count'] < 30]

    # 2. Bootstrap null for T1
    entity_sizes = [entity_profiles[e]['token_count'] for e in powered]
    total_needed = sum(entity_sizes)
    # Extend middles list to cover total (resample with replacement if needed)
    pooled = ros_middles_list[:total_needed] if len(ros_middles_list) >= total_needed else ros_middles_list * 3
    pooled = pooled[:total_needed]
    t1_threshold, null_dist = bootstrap_category_jsd_null(pooled, entity_sizes, cc, n_bootstrap=1000)
    print(f"  Bootstrap T1 threshold (95th pctl): {t1_threshold:.4f}")
    print(f"  Observed mean category JSD: {mean_cat_jsd:.4f}")

    # 3. Ring vs non-ring — 4-way split (classified/unclassified × ring/nonring)
    ring_toks = data['ring_tokens']
    nonring_toks = data['nonring_tokens']
    token_to_class = data['token_to_class']
    decomp = data['ros_decomp']

    def split_cat_profile(toks):
        cat_c, _ = category_profile_from_tokens(toks, decomp, cc)
        return normalize(cat_c, CATEGORIES)

    ring_classified = [t for t in ring_toks if t.get('word') in token_to_class]
    ring_unclassified = [t for t in ring_toks if t.get('word') not in token_to_class]
    nonring_classified = [t for t in nonring_toks if t.get('word') in token_to_class]
    nonring_unclassified = [t for t in nonring_toks if t.get('word') not in token_to_class]

    ring_nonring_profiles = {
        'ring_classified': {'n': len(ring_classified), 'category': split_cat_profile(ring_classified),
                            'head': normalize(head_profile_from_tokens(ring_classified, decomp), HEAD_LABELS)},
        'ring_unclassified': {'n': len(ring_unclassified), 'category': split_cat_profile(ring_unclassified),
                              'head': normalize(head_profile_from_tokens(ring_unclassified, decomp), HEAD_LABELS)},
        'nonring_classified': {'n': len(nonring_classified), 'category': split_cat_profile(nonring_classified),
                               'head': normalize(head_profile_from_tokens(nonring_classified, decomp), HEAD_LABELS)},
        'nonring_unclassified': {'n': len(nonring_unclassified), 'category': split_cat_profile(nonring_unclassified),
                                 'head': normalize(head_profile_from_tokens(nonring_unclassified, decomp), HEAD_LABELS)},
    }
    ring_all_cat = split_cat_profile(ring_toks)
    nonring_all_cat = split_cat_profile(nonring_toks)
    ring_nonring_jsd = jsd(ring_all_cat, nonring_all_cat, CATEGORIES)

    # Non-execution category enrichment for ring text (T2: MARKING+STAGING+OPERATION)
    non_exec_cats = ['MARKING', 'STAGING', 'OPERATION']
    ring_nonexec = sum(ring_all_cat.get(c, 0) for c in non_exec_cats)
    nonring_nonexec = sum(nonring_all_cat.get(c, 0) for c in non_exec_cats)

    # 4. Entity-type aggregate profiles
    entity_type_profiles = {}
    for etype, filter_fn in [
        ('rosettes', lambda e: e in ROSETTE_NAMES),
        ('paths', lambda e: e.startswith('PATH_')),
        ('clock', lambda e: e == 'CLOCK'),
    ]:
        toks = []
        for ename, prof in entity_profiles.items():
            if filter_fn(ename):
                # Reconstruct tokens from entity
                ra = data['ra']
                for t in ra.get_entity_tokens(ename):
                    mid = t.get('middle', '')
                    if mid and ',' not in mid and '?' not in mid and not any(c in mid for c in 'jqz'):
                        toks.append(t)
        if toks:
            cat_c, _ = category_profile_from_tokens(toks, decomp, cc)
            entity_type_profiles[etype] = {
                'n': len(toks),
                'head': normalize(head_profile_from_tokens(toks, decomp), HEAD_LABELS),
                'category': normalize(cat_c, CATEGORIES),
            }

    # 5. Spatial adjacency test
    adj_jsds = []
    nonadj_jsds = []
    for i, e1 in enumerate(powered):
        for j, e2 in enumerate(powered):
            if j <= i:
                continue
            pair_set = frozenset({e1, e2})
            d = cat_jsd_matrix[f"{e1}-{e2}"]
            if pair_set in ADJACENCY:
                adj_jsds.append(d)
            else:
                nonadj_jsds.append(d)
    mean_adj = sum(adj_jsds) / len(adj_jsds) if adj_jsds else 0
    mean_nonadj = sum(nonadj_jsds) / len(nonadj_jsds) if nonadj_jsds else 0
    adj_delta = abs(mean_adj - mean_nonadj)

    # 6. Ward clustering
    clustering = None
    if HAS_SCIPY and len(powered) >= 3:
        cat_vectors = []
        for e in powered:
            cat_vectors.append([entity_profiles[e]['category'].get(c, 0) for c in CATEGORIES])
        # Build condensed distance matrix from JSD
        condensed = []
        for i in range(len(powered)):
            for j in range(i + 1, len(powered)):
                condensed.append(cat_jsd_matrix[f"{powered[i]}-{powered[j]}"])
        Z = linkage(condensed, method='ward')
        labels_3 = fcluster(Z, t=3, criterion='maxclust')
        clustering = {
            'entities': powered,
            'linkage': Z.tolist(),
            'clusters_k3': {powered[i]: int(labels_3[i]) for i in range(len(powered))},
        }

    # 7. Outlier detection
    entity_mean_jsd = {}
    for e in powered:
        dsds = [cat_jsd_matrix.get(f"{min(e,e2)}-{max(e,e2)}", cat_jsd_matrix.get(f"{e2}-{e}", 0))
                for e2 in powered if e2 != e]
        # Rebuild properly
        dsds = []
        for e2 in powered:
            if e2 == e:
                continue
            pair_key = f"{e}-{e2}" if f"{e}-{e2}" in cat_jsd_matrix else f"{e2}-{e}"
            dsds.append(cat_jsd_matrix.get(pair_key, 0))
        entity_mean_jsd[e] = sum(dsds) / len(dsds) if dsds else 0
    max_outlier = max(entity_mean_jsd, key=entity_mean_jsd.get) if entity_mean_jsd else None
    max_outlier_jsd = entity_mean_jsd.get(max_outlier, 0)
    is_outlier = max_outlier_jsd > 2 * mean_cat_jsd if mean_cat_jsd > 0 else False

    return {
        'powered_entities': powered,
        'head_jsd_matrix': head_jsd_matrix,
        'cat_jsd_matrix': cat_jsd_matrix,
        'mean_head_jsd': mean_head_jsd,
        'mean_cat_jsd': mean_cat_jsd,
        'max_cat_jsd': max_cat_jsd,
        'max_cat_pair': max_cat_pair,
        'small_n_pairs': small_pairs,
        't1_bootstrap_threshold': t1_threshold,
        'ring_nonring': ring_nonring_profiles,
        'ring_all_category': ring_all_cat,
        'nonring_all_category': nonring_all_cat,
        'ring_nonring_jsd': ring_nonring_jsd,
        'ring_nonexec_share': ring_nonexec,
        'nonring_nonexec_share': nonring_nonexec,
        'entity_type_profiles': entity_type_profiles,
        'adjacency': {
            'adjacent_pairs': len(adj_jsds),
            'nonadjacent_pairs': len(nonadj_jsds),
            'mean_adj_jsd': mean_adj,
            'mean_nonadj_jsd': mean_nonadj,
            'delta': adj_delta,
        },
        'clustering': clustering,
        'outlier': {
            'entity': max_outlier,
            'mean_jsd_to_others': max_outlier_jsd,
            'is_outlier': is_outlier,
            'entity_mean_jsds': entity_mean_jsd,
        },
    }


# ============================================================
# BASELINE COMPARISONS
# ============================================================

def baseline_comparisons(entity_profiles, data):
    b_bl = data['b_baseline']
    a_bl = data['a_baseline']
    azc_bl = data['azc_baseline']

    # Rosettes aggregate profile
    ros_head_all = Counter()
    ros_cat_all = Counter()
    for ename in ROSETTE_NAMES:
        if ename in entity_profiles:
            for h, c in entity_profiles[ename].get('head_counts', {}).items():
                ros_head_all[h] += c
    ros_head_norm = normalize(ros_head_all, HEAD_LABELS)
    # Recompute category from all tokens
    decomp = data['ros_decomp']
    cc = data['cc']
    all_ros_toks = [t for t in data['ros_tokens']]
    ros_cat_all_c, _ = category_profile_from_tokens(all_ros_toks, decomp, cc)
    ros_cat_norm = normalize(ros_cat_all_c, CATEGORIES)

    # JSD to each baseline
    head_jsd_to = {
        'B': jsd(ros_head_norm, b_bl['head'], HEAD_LABELS),
        'A': jsd(ros_head_norm, a_bl['head'], HEAD_LABELS),
        'AZC': jsd(ros_head_norm, azc_bl['head'], HEAD_LABELS),
    }
    cat_jsd_to = {
        'B': jsd(ros_cat_norm, b_bl['category'], CATEGORIES),
        'A': jsd(ros_cat_norm, a_bl['category'], CATEGORIES),
        'AZC': jsd(ros_cat_norm, azc_bl['category'], CATEGORIES),
    }
    # Cosine similarity
    head_cos_to = {
        'B': cosine_sim(ros_head_norm, b_bl['head'], HEAD_LABELS),
        'A': cosine_sim(ros_head_norm, a_bl['head'], HEAD_LABELS),
        'AZC': cosine_sim(ros_head_norm, azc_bl['head'], HEAD_LABELS),
    }
    cat_cos_to = {
        'B': cosine_sim(ros_cat_norm, b_bl['category'], CATEGORIES),
        'A': cosine_sim(ros_cat_norm, a_bl['category'], CATEGORIES),
        'AZC': cosine_sim(ros_cat_norm, azc_bl['category'], CATEGORIES),
    }

    # Per-entity JSD to AZC (primary baseline)
    per_entity_azc_jsd = {}
    for ename in ROSETTE_NAMES:
        if ename in entity_profiles:
            per_entity_azc_jsd[ename] = {
                'head': jsd(entity_profiles[ename]['head'], azc_bl['head'], HEAD_LABELS),
                'category': jsd(entity_profiles[ename]['category'], azc_bl['category'], CATEGORIES),
            }

    return {
        'rosettes_aggregate': {
            'head': ros_head_norm,
            'category': ros_cat_norm,
        },
        'head_jsd_to_baselines': head_jsd_to,
        'category_jsd_to_baselines': cat_jsd_to,
        'head_cosine_to_baselines': head_cos_to,
        'category_cosine_to_baselines': cat_cos_to,
        'per_entity_azc_jsd': per_entity_azc_jsd,
        'closest_baseline_head': min(head_jsd_to, key=head_jsd_to.get),
        'closest_baseline_category': min(cat_jsd_to, key=cat_jsd_to.get),
    }


# ============================================================
# PREDICTIONS AND VERDICT
# ============================================================

def evaluate_predictions(cross, entity_profiles, data):
    results = {}

    # T1: Entity uniformity (bootstrap null)
    t1_threshold = cross['t1_bootstrap_threshold']
    t1_observed = cross['mean_cat_jsd']
    t1_pass = t1_observed < t1_threshold
    results['T1'] = {
        'name': 'Entity category uniformity',
        'observed': t1_observed,
        'threshold': t1_threshold,
        'method': 'bootstrap_95pctl',
        'pass': t1_pass,
    }

    # T2: Ring text non-execution enrichment (C1131 consistency)
    ring_nonexec = cross['ring_nonexec_share']
    nonring_nonexec = cross['nonring_nonexec_share']
    t2_pass = ring_nonexec > nonring_nonexec  # Ring should have higher non-execution share
    results['T2'] = {
        'name': 'Ring non-execution enrichment (C1131 consistency)',
        'ring_nonexec_share': ring_nonexec,
        'nonring_nonexec_share': nonring_nonexec,
        'enrichment': ring_nonexec / nonring_nonexec if nonring_nonexec > 0 else float('inf'),
        'pass': t2_pass,
    }

    # T3: Spatial non-coherence
    adj = cross['adjacency']
    t3_pass = adj['delta'] < 0.02
    results['T3'] = {
        'name': 'Spatial non-coherence',
        'mean_adj_jsd': adj['mean_adj_jsd'],
        'mean_nonadj_jsd': adj['mean_nonadj_jsd'],
        'delta': adj['delta'],
        'threshold': 0.02,
        'pass': t3_pass,
    }

    # T4: Dual population per-entity divergence
    decomp = data['ros_decomp']
    cc = data['cc']
    token_to_class = data['token_to_class']
    ra = data['ra']
    t4_entity_results = {}
    for ename in ROSETTE_NAMES:
        if ename not in entity_profiles or entity_profiles[ename]['token_count'] < 20:
            continue
        toks = [t for t in ra.get_entity_tokens(ename)
                if t.get('middle') and ',' not in t.get('middle', '')
                and '?' not in t.get('middle', '')
                and not any(c in t.get('middle', '') for c in 'jqz')]
        c_toks = [t for t in toks if t.get('word') in token_to_class]
        u_toks = [t for t in toks if t.get('word') not in token_to_class]
        if len(c_toks) >= 5 and len(u_toks) >= 5:
            c_cat, _ = category_profile_from_tokens(c_toks, decomp, cc)
            u_cat, _ = category_profile_from_tokens(u_toks, decomp, cc)
            c_cat_n = normalize(c_cat, CATEGORIES)
            u_cat_n = normalize(u_cat, CATEGORIES)
            dual_jsd = jsd(c_cat_n, u_cat_n, CATEGORIES)
            t4_entity_results[ename] = {
                'classified_n': len(c_toks),
                'unclassified_n': len(u_toks),
                'category_jsd': dual_jsd,
            }
    t4_mean_jsd = (sum(r['category_jsd'] for r in t4_entity_results.values()) / len(t4_entity_results)
                   if t4_entity_results else 0)
    results['T4'] = {
        'name': 'Dual population per-entity category divergence',
        'per_entity': t4_entity_results,
        'mean_jsd': t4_mean_jsd,
        'note': 'Reported separately from verdict; tests C1132 at category level',
    }

    # Verdict
    is_outlier = cross['outlier']['is_outlier']
    if t1_pass and t2_pass and t3_pass and not is_outlier:
        verdict = 'UNIFORM_OPERATIONAL_INDEX'
    elif t1_pass and is_outlier:
        verdict = 'UNIFORM_WITH_OUTLIER'
    elif t1_pass and not t3_pass:
        verdict = 'SPATIAL_CLUSTERING'
    elif not t1_pass and t2_pass:
        verdict = 'DIFFERENTIATED_INDEX'
    elif not t1_pass:
        verdict = 'ENTITY_DIFFERENTIATED'
    else:
        verdict = 'UNIFORM_OPERATIONAL_INDEX'

    results['verdict'] = verdict
    core_pass = sum(1 for k in ['T1', 'T2', 'T3'] if results[k]['pass'])
    results['core_pass'] = core_pass
    results['core_total'] = 3

    return results


# ============================================================
# ANNOTATED DUMP GENERATION
# ============================================================

def generate_dump_header():
    """Generate the legend header for the dump file."""
    return """ROSETTES OPERATIONAL CLOSE READING - ANNOTATED TOKEN DUMPS
Phase 620 | Generated from data/rosettes_annotated.json (ZL transcription)
================================================================================

LEGEND:
  HEAD domains (C1475): a=ITERATION, e=BALANCED, o=ARRANGEMENT, k=THERMAL, t=TRANSFER
  TERMINAL tiers (C1487): LOCKED={r,m}, CHANNELED={l,y,n}, DIFFUSE={h}, BARE=no terminal
  Categories (C1250): TH=THERMAL, FL=FLOW, CN=CONTAINMENT, ST=STAGING,
                      OP=OPERATION, TR=TRANSITION, MK=MARKING, MN=MONITORING
  B/D column: B=bridge, D=dark, BD=both, -=neither
  C/U column: C=classified (in 49-class system), U=unclassified
  Hazard: IMMUNE (k/o-HEAD, C1446/C1561), ZERO/HIGH/LOW (C1448 frame_hazard)
  Conf: Category confidence (H=HIGH, M=MEDIUM, L=LOW from C1195 atom tiers)
  Atom gloss [T4]: Tier 4 QUARANTINED glosses (C1195-C1196). NOT structural findings.
    k=heat, e=cool, h=watch, y=end, i=iterate, n=halt, a=yield, m=final,
    d=mark, t=transfer, c=adjust, p=pause, f=flag, s=sequence, g=complete,
    o=work, l=frame, r=input

================================================================================
"""


def generate_entity_dump(entity_name, entity_profile, tokens_by_subregion, data):
    """Generate annotated dump for one entity."""
    decomp = data['ros_decomp']
    cc = data['cc']
    token_to_class = data['token_to_class']
    dark_set = data['dark_set']
    fh_map = data['frame_hazard_map']
    prof = entity_profile

    # Determine entity type
    if entity_name in ROSETTE_NAMES:
        etype = 'ROSETTE'
    elif entity_name.startswith('PATH_'):
        etype = 'PATH'
    elif entity_name == 'CLOCK':
        etype = 'CLOCK'
    else:
        etype = 'OTHER'

    subs = list(tokens_by_subregion.keys())
    n = prof['token_count']

    lines = []
    lines.append(f"{'='*90}")
    lines.append(f"ENTITY: {entity_name} -- {n} tokens, {len(subs)} sub-regions ({', '.join(subs)})")
    lines.append(f"ENTITY TYPE: {etype}")
    lines.append(f"{'-'*90}")

    # HEAD profile
    h = prof['head']
    head_items = sorted(HEAD_LABELS, key=lambda k: -h.get(k, 0))
    head_str = '  '.join(f"{k}={h.get(k,0):.1%}" for k in head_items)
    lines.append(f"HEAD: {head_str}")
    dom = prof['dominant_head']
    dom_label = HEAD_DOMAIN.get(dom, dom)
    lines.append(f"  [Dominant: {dom} = {dom_label}]  Headless rate: {prof['headless_rate']:.1%}")

    # Category profile
    cat = prof['category']
    cat_items = sorted(CATEGORIES, key=lambda c: -cat.get(c, 0))
    cat_str = '  '.join(f"{c[:4]}={cat.get(c,0):.1%}" for c in cat_items if cat.get(c, 0) > 0.005)
    lines.append(f"CATEGORY: {cat_str}")
    lines.append(f"  [Coverage: {prof['category_coverage']:.1%} of MIDDLEs classified]")

    # Kernel
    k = prof['kernel']
    lines.append(f"KERNEL: k={k['k']:.1%} h={k['h']:.1%} e={k['e']:.1%} | fraction={prof['kernel_fraction']:.1%} | {prof['kernel_balance']}")

    # Terminal tier
    tt = prof['terminal_tier']
    lines.append(f"TERMINAL TIER: {prof['dominant_tier']}  LOCKED={tt.get('LOCKED',0):.1%}  CHAN={tt.get('CHANNELED',0):.1%}  DIFF={tt.get('DIFFUSE',0):.1%}  BARE={tt.get('BARE',0):.1%}")

    # PREFIX
    lines.append(f"PREFIX: rate={prof['prefix_rate']:.1%}  da/sa/ta={prof['gateway_prefix_fraction']:.1%}  top: {prof['prefix_inventory']}")

    # Suffix
    lines.append(f"SUFFIX: rate={prof['suffix_rate']:.1%}")

    # Bridge/Dark/Compound
    lines.append(f"BRIDGE={prof['bridge_rate']:.1%}  DARK={prof['dark_rate']:.1%}  COMPOUND={prof['compound_rate']:.1%}")

    # Classified/Unclassified
    cp = prof['classified']
    up = prof['unclassified']
    lines.append(f"CLASSIFIED: {cp['n']}/{n} ({cp['n']/n:.1%})  UNCLASSIFIED: {up['n']}/{n} ({up['n']/n:.1%})")

    # Hazard summary
    hz = prof['hazard']
    lines.append(f"HAZARD: IMMUNE={hz.get('IMMUNE',0):.1%}  ZERO={hz.get('ZERO',0):.1%}  HIGH={hz.get('HIGH',0):.1%}  LOW={hz.get('LOW',0):.1%}")

    # Top frames and MIDDLEs
    tf_str = ', '.join(f"{f}({c})" for f, c in prof['top_frames'])
    tm_str = ', '.join(f"{m}({c})" for m, c in prof['top_middles'])
    lines.append(f"TOP FRAMES: {tf_str}")
    lines.append(f"TOP MIDDLEs: {tm_str}")
    lines.append(f"{'='*90}")

    # Per sub-region token tables
    for sr in SUB_REGION_ORDER:
        if sr not in tokens_by_subregion:
            continue
        sr_toks = tokens_by_subregion[sr]
        lines.append(f"\n--- SUB-REGION: {sr} ({len(sr_toks)} tokens) ---\n")

        # Header row
        lines.append(f"  {'#':>3s}  {'word':16s} {'pfx':6s} {'MIDDLE':12s} {'sfx':4s} {'HEAD_domain':16s} {'MODs':6s} {'TERM':5s} {'category':12s} {'cf':2s} {'BD':2s} {'CU':2s} {'hazard':6s} {'prev>next':14s} atom_gloss [T4]")
        lines.append(f"  {'─'*3}  {'─'*16} {'─'*6} {'─'*12} {'─'*4} {'─'*16} {'─'*6} {'─'*5} {'─'*12} {'─'*2} {'─'*2} {'─'*2} {'─'*6} {'─'*14} {'─'*20}")

        for idx, t_tok in enumerate(sr_toks):
            word = t_tok.get('word', '')
            pfx = t_tok.get('prefix') or '-'
            mid = t_tok.get('middle', '')
            sfx = t_tok.get('suffix') or '-'

            if mid and mid in decomp:
                d = decomp[mid]
                head = d['head']
                mods = d['mods'] or '-'
                term = d['term']
                head_dom = f"{head}:{HEAD_DOMAIN[head]}" if head else "headless"
                cat = cc.classify(mid) or '?'
                conf_raw = cc.confidence(mid)
                conf = conf_raw[0] if conf_raw else '?'  # H/M/L
                hz = frame_hazard_for_token(head, d['frame'], fh_map)
                gloss = atom_gloss_string(mid)
            else:
                head_dom = '?'
                mods = '-'
                term = '-'
                cat = '?'
                conf = '?'
                hz = '?'
                gloss = ''

            # Bridge/Dark
            is_bridge = t_tok.get('is_bridge', False)
            is_dark = mid in data['dark_set']
            if is_bridge and is_dark:
                bd = 'BD'
            elif is_bridge:
                bd = 'B'
            elif is_dark:
                bd = 'D'
            else:
                bd = '-'

            # Classified/Unclassified
            cu = 'C' if word in token_to_class else 'U'

            # Neighbors (prev/next MIDDLE)
            prev_mid = sr_toks[idx - 1].get('middle', '') if idx > 0 else ''
            next_mid = sr_toks[idx + 1].get('middle', '') if idx < len(sr_toks) - 1 else ''
            neighbors = f"{prev_mid[:6]}>{next_mid[:6]}"

            lines.append(
                f"  {idx+1:3d}  {word:16s} {pfx:6s} {mid:12s} {sfx:4s} {head_dom:16s} {mods:6s} {term:5s} {cat:12s} {conf:2s} {bd:2s} {cu:2s} {hz:6s} {neighbors:14s} {gloss}"
            )

    lines.append("")
    return '\n'.join(lines)


# ============================================================
# SCORECARD
# ============================================================

def print_scorecard(predictions, cross, baselines):
    print(f"\n{'='*70}")
    print("PREDICTION SCORECARD")
    print(f"{'='*70}")
    for key in ['T1', 'T2', 'T3']:
        p = predictions[key]
        status = "PASS" if p['pass'] else "FAIL"
        print(f"  {key}: {p['name']}: {status}")
        if key == 'T1':
            print(f"       observed={p['observed']:.4f} threshold={p['threshold']:.4f} (bootstrap 95th)")
        elif key == 'T2':
            print(f"       ring_nonexec={p['ring_nonexec_share']:.3f} nonring_nonexec={p['nonring_nonexec_share']:.3f}")
        elif key == 'T3':
            print(f"       mean_adj={p['mean_adj_jsd']:.4f} mean_nonadj={p['mean_nonadj_jsd']:.4f} delta={p['delta']:.4f}")

    print(f"\n  T4 (reported separately): Dual population per-entity divergence")
    t4 = predictions['T4']
    print(f"       mean within-entity classified/unclassified JSD: {t4['mean_jsd']:.4f}")
    for ename, r in t4.get('per_entity', {}).items():
        print(f"         {ename}: JSD={r['category_jsd']:.4f} (C={r['classified_n']}, U={r['unclassified_n']})")

    print(f"\n  VERDICT: {predictions['verdict']} ({predictions['core_pass']}/{predictions['core_total']} core)")

    # Outlier
    outlier = cross['outlier']
    if outlier['is_outlier']:
        print(f"  OUTLIER: {outlier['entity']} (mean JSD to others={outlier['mean_jsd_to_others']:.4f})")

    # Baseline positioning
    print(f"\n  BASELINE POSITIONING:")
    print(f"    HEAD closest to: {baselines['closest_baseline_head']} (JSD: {baselines['head_jsd_to_baselines']})")
    print(f"    CATEGORY closest to: {baselines['closest_baseline_category']} (JSD: {baselines['category_jsd_to_baselines']})")
    print(f"    HEAD cosine: {baselines['head_cosine_to_baselines']}")
    print(f"    CATEGORY cosine: {baselines['category_cosine_to_baselines']}")


# ============================================================
# MAIN
# ============================================================

def main():
    data = load_data()
    entity_counts = power_preamble(data)
    ra = data['ra']
    decomp = data['ros_decomp']

    # Per-entity fingerprinting
    print("\nComputing per-entity fingerprints...")
    entity_profiles = {}
    tokens_by_entity_subregion = {}
    for ename in ra.get_entities():
        toks = [t for t in ra.get_entity_tokens(ename)
                if t.get('middle') and ',' not in t.get('middle', '')
                and '?' not in t.get('middle', '')
                and not any(c in t.get('middle', '') for c in 'jqz')]
        if not toks:
            continue
        profile = fingerprint_entity(ename, toks, data)
        if profile:
            entity_profiles[ename] = profile

        # Tokens by sub-region for dump
        sr_tokens = {}
        for sr in ra.get_sub_regions(ename):
            sr_toks = [t for t in ra.get_entity_tokens(ename, sub_region=sr)
                       if t.get('middle') and ',' not in t.get('middle', '')
                       and '?' not in t.get('middle', '')
                       and not any(c in t.get('middle', '') for c in 'jqz')]
            if sr_toks:
                sr_tokens[sr] = sr_toks
        tokens_by_entity_subregion[ename] = sr_tokens

    print(f"  Fingerprinted {len(entity_profiles)} entities")

    # Cross-entity comparisons
    print("\nComputing cross-entity comparisons...")
    cross = cross_entity_comparisons(entity_profiles, data)

    # Baseline comparisons
    print("\nComputing baseline comparisons...")
    baselines = baseline_comparisons(entity_profiles, data)

    # Predictions
    print("\nEvaluating predictions...")
    predictions = evaluate_predictions(cross, entity_profiles, data)
    print_scorecard(predictions, cross, baselines)

    # Save JSON results
    results = {
        'phase': 620,
        'name': 'ROSETTES_OPERATIONAL_CLOSE_READING',
        'entity_profiles': entity_profiles,
        'cross_entity': cross,
        'baselines': baselines,
        'predictions': predictions,
        'verdict': predictions['verdict'],
    }
    results_path = RESULTS_DIR / 'rosettes_operational_close_reading.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, default=str)
    print(f"\nResults saved to {results_path}")

    # Generate annotated dumps
    print("\nGenerating annotated entity dumps...")
    dump_parts = [generate_dump_header()]

    # Order: 9 rosettes by token count desc, then paths, then CLOCK, then other
    rosette_order = sorted([e for e in entity_profiles if e in ROSETTE_NAMES],
                           key=lambda e: -entity_profiles[e]['token_count'])
    path_order = sorted([e for e in entity_profiles if e.startswith('PATH_')])
    other_order = [e for e in entity_profiles if e not in rosette_order and e not in path_order]

    for ename in rosette_order + path_order + other_order:
        dump_parts.append(generate_entity_dump(
            ename, entity_profiles[ename],
            tokens_by_entity_subregion.get(ename, {}), data
        ))

    dump_path = DATA_DIR / 'rosettes_entity_dumps.txt'
    with open(dump_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(dump_parts))
    print(f"Dumps saved to {dump_path}")

    print(f"\n{'='*70}")
    print(f"Phase 620 complete. Verdict: {predictions['verdict']}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
