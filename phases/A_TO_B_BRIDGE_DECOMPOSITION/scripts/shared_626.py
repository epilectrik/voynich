"""
Phase 626: A_TO_B_BRIDGE_DECOMPOSITION -- Shared utilities.

Provides data loaders for PP classification, A-record profiles,
B-operational profiles, manifold scores, bridge/dark MIDDLE sets,
and REGIME mapping. Also provides per-folio aggregation functions
and statistical utilities.
"""

import json
import math
import random
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Any, Optional

import sys
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier,
    load_middle_classes, decompose_middle_hmt,
)

# ============================================================
# Constants
# ============================================================

PROJECT_ROOT = _PROJECT_ROOT
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'A_TO_B_BRIDGE_DECOMPOSITION' / 'results'

N_PERM = 1000
RNG = random.Random(626)

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']

MATERIAL_CLASSES = ['ANIMAL', 'HERB', 'NEUTRAL', 'MIXED']

# ============================================================
# Data Loaders
# ============================================================

def load_pp_classification() -> Dict[str, dict]:
    """Load PP MIDDLE -> {material_class, animal_rate, herb_rate, cluster}."""
    path = PROJECT_ROOT / 'phases' / 'PP_CLASSIFICATION' / 'results' / 'pp_classification.json'
    with open(path) as f:
        data = json.load(f)
    return data['pp_classification']


def load_a_record_profiles() -> list:
    """Load 1,063 A-records with pp_tokens, ri_tokens, b_convergence, etc."""
    path = PROJECT_ROOT / 'phases' / 'MATERIAL_MAPPING_V2' / 'results' / 'a_record_profiles.json'
    with open(path) as f:
        data = json.load(f)
    return data['profiles']


def load_b_operational_profiles() -> Dict[str, dict]:
    """Load B folio -> 12 operational dimensions."""
    path = PROJECT_ROOT / 'results' / 'folio_operational_profiles.json'
    with open(path) as f:
        data = json.load(f)
    result = {}
    dims = data['dimensions']
    for p in data['profiles']:
        folio = p['folio']
        result[folio] = {d: p[d] for d in dims}
        result[folio]['material_category'] = p.get('material_category')
        result[folio]['output_category'] = p.get('output_category')
        result[folio]['kernel_balance'] = p.get('kernel_balance')
    return result


def load_b_deployment_features() -> Tuple[Dict[str, dict], list]:
    """Load B folio -> 56-feature vector, and feature names list."""
    path = (PROJECT_ROOT / 'phases' / 'WITHIN_DOMAIN_COMPOSITIONAL_CONTROL' /
            'results' / 't1b_deployment_features.json')
    with open(path) as f:
        data = json.load(f)
    # Flatten feature names
    all_names = []
    for group in ['zone', 'adjacency', 'closure', 'headless', 'paragraph']:
        all_names.extend(data['feature_names'].get(group, []))
    # Build folio -> feature dict
    result = {}
    for folio, features in data['folio_features'].items():
        result[folio] = {name: features.get(name, 0.0) for name in all_names}
    return result, all_names


def load_manifold_scores() -> Dict[str, dict]:
    """Load B folio -> PC1-PC5 scores from apparatus manifold."""
    path = (PROJECT_ROOT / 'phases' / 'APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS' /
            'results' / 't1_manifold_embedding.json')
    with open(path) as f:
        data = json.load(f)
    scores = data['space_A']['folio_scores']
    result = {}
    pcs = ['PC1', 'PC2', 'PC3', 'PC4', 'PC5']
    for folio, vals in scores.items():
        result[folio] = {pc: vals[pc] for pc in pcs}
    return result


def load_bridge_dark_sets() -> Tuple[set, set]:
    """Load bridge (85) and dark (300) MIDDLE sets."""
    bridge_path = (PROJECT_ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' /
                   'results' / 'bridge_selection.json')
    with open(bridge_path) as f:
        bdata = json.load(f)
    bridge_set = set(bdata['t5_structural_profile']['bridge_middles'])

    dark_path = PROJECT_ROOT / 'data' / 'dark_pipeline_middles.json'
    with open(dark_path) as f:
        ddata = json.load(f)
    dark_set = set(ddata['middles'])

    return bridge_set, dark_set


def load_regime_mapping() -> Dict[str, str]:
    """Load B folio -> REGIME string."""
    path = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
    with open(path) as f:
        data = json.load(f)
    result = {}
    for folio, info in data['regime_assignments'].items():
        result[folio] = info['regime']
    return result


# ============================================================
# Per-Folio Aggregation
# ============================================================

def group_records_by_folio(records: list) -> Dict[str, list]:
    """Group A-record profiles by folio."""
    by_folio = defaultdict(list)
    for rec in records:
        by_folio[rec['folio']].append(rec)
    return dict(by_folio)


def compute_folio_pp_set(records: list, pp_middles: set) -> set:
    """Compute set of PP MIDDLEs for a folio's records."""
    result = set()
    for rec in records:
        for tok in rec.get('pp_tokens', []):
            # Extract MIDDLE from token
            morph = Morphology()
            m = morph.extract(tok)
            if m.middle and m.middle in pp_middles:
                result.add(m.middle)
    return result


def compute_folio_pp_set_from_profiles(folio_records: list) -> set:
    """Compute set of PP MIDDLEs directly from a_record_profiles pp_tokens field.
    
    Note: pp_tokens in a_record_profiles are already full tokens, not MIDDLEs.
    We need to extract MIDDLEs from them.
    """
    morph = Morphology()
    result = set()
    for rec in folio_records:
        for tok in rec.get('pp_tokens', []):
            m = morph.extract(tok)
            if m.middle:
                result.add(m.middle)
    return result


def compute_folio_ri_set(folio_records: list) -> set:
    """Compute set of RI MIDDLEs for a folio's records."""
    morph = Morphology()
    result = set()
    for rec in folio_records:
        for tok in rec.get('ri_tokens', []):
            m = morph.extract(tok)
            if m.middle:
                result.add(m.middle)
    return result


def compute_folio_bridge_inventory(folio_records: list, bridge_set: set) -> Dict[str, int]:
    """Compute bridge MIDDLE frequency for a folio's records."""
    morph = Morphology()
    counts = Counter()
    for rec in folio_records:
        for tok in rec.get('pp_tokens', []):
            m = morph.extract(tok)
            if m.middle and m.middle in bridge_set:
                counts[m.middle] += 1
    return dict(counts)


def get_a_folio_section(folio: str) -> str:
    """Determine section (H or P) for an A folio based on folio number."""
    import re
    match = re.search(r'(\d+)', folio)
    if not match:
        return 'H'
    num = int(match.group(1))
    # P (Pharma) folios: f87-f102
    if 87 <= num <= 102:
        return 'P'
    return 'H'


# ============================================================
# Statistical Utilities
# ============================================================

def jaccard_similarity(s1: set, s2: set) -> float:
    """Jaccard similarity between two sets."""
    if not s1 and not s2:
        return 0.0
    union = s1 | s2
    if not union:
        return 0.0
    return len(s1 & s2) / len(union)


def jsd(p: list, q: list) -> float:
    """Jensen-Shannon divergence between two probability distributions."""
    p = [max(x, 1e-12) for x in p]
    q = [max(x, 1e-12) for x in q]
    sp = sum(p)
    sq = sum(q)
    p = [x / sp for x in p]
    q = [x / sq for x in q]
    m = [(pi + qi) / 2 for pi, qi in zip(p, q)]
    kl_pm = sum(pi * math.log(pi / mi) for pi, mi in zip(p, m) if pi > 0)
    kl_qm = sum(qi * math.log(qi / mi) for qi, mi in zip(q, m) if qi > 0)
    return (kl_pm + kl_qm) / 2


def cosine_sim(a: list, b: list) -> float:
    """Cosine similarity between two vectors."""
    dot = sum(ai * bi for ai, bi in zip(a, b))
    na = math.sqrt(sum(ai * ai for ai in a))
    nb = math.sqrt(sum(bi * bi for bi in b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return dot / (na * nb)


def cohens_d(a: list, b: list) -> float:
    """Cohen's d effect size."""
    if len(a) < 2 or len(b) < 2:
        return 0.0
    mean_a = sum(a) / len(a)
    mean_b = sum(b) / len(b)
    var_a = sum((x - mean_a) ** 2 for x in a) / (len(a) - 1)
    var_b = sum((x - mean_b) ** 2 for x in b) / (len(b) - 1)
    pooled_sd = math.sqrt(((len(a) - 1) * var_a + (len(b) - 1) * var_b) /
                          (len(a) + len(b) - 2))
    if pooled_sd < 1e-12:
        return 0.0
    return (mean_a - mean_b) / pooled_sd


def mantel_test(D1: list, D2: list, n_perm: int = N_PERM,
                rng: random.Random = RNG) -> Tuple[float, float]:
    """Mantel test: correlation between two distance matrices (flat upper-triangle).
    
    Returns (r, p_value).
    """
    import numpy as np
    d1 = np.array(D1, dtype=float)
    d2 = np.array(D2, dtype=float)
    
    if len(d1) == 0 or len(d2) == 0:
        return 0.0, 1.0
    
    # Pearson correlation
    r_obs = float(np.corrcoef(d1, d2)[0, 1])
    if np.isnan(r_obs):
        return 0.0, 1.0
    
    # Permutation test: shuffle one distance matrix by permuting indices
    n = int((1 + math.sqrt(1 + 8 * len(d1))) / 2)  # recover n from n*(n-1)/2
    
    count_ge = 0
    indices = list(range(n))
    for _ in range(n_perm):
        perm = indices[:]
        rng.shuffle(perm)
        # Reorder d2 according to permutation
        d2_perm = []
        for i in range(n):
            for j in range(i + 1, n):
                pi, pj = perm[i], perm[j]
                ii, jj = min(pi, pj), max(pi, pj)
                idx = ii * n - ii * (ii + 1) // 2 + jj - ii - 1
                d2_perm.append(d2[idx])
        r_perm = float(np.corrcoef(d1, np.array(d2_perm))[0, 1])
        if not np.isnan(r_perm) and r_perm >= r_obs:
            count_ge += 1
    
    p_value = (count_ge + 1) / (n_perm + 1)
    return r_obs, p_value


def round_floats(obj, digits=6):
    """Round all floats in a nested structure."""
    if isinstance(obj, float):
        return round(obj, digits)
    elif isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [round_floats(x, digits) for x in obj]
    return obj
