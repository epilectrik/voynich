#!/usr/bin/env python3
"""
Phase 394: Stars Paradox Resolution -- 3-gate, 15-test battery

The Stars Paradox: Section S (Stars/Recipe, 23 folios) has the MOST REGIME
diversity but the LOWEST AXM variance (0.0059 vs B=0.0078, H=0.0148).
Phase 392 falsified vocabulary clamping (C1108). This phase tests 4
alternative mechanisms.

Gate 1: Paradox Confirmation (2 tests)
Gate 2: 4 Mechanisms (11 tests)
  M1: LINK Regulation (3 tests)
  M2: CC Trigger Channeling (3 tests)
  M3: Paragraph Constraint (2 tests)
  M4: De Facto Forbidden Transitions (3 tests)
Gate 3: Sufficiency (2 tests, for passing mechanisms only)

Grounding constraints:
  C109 (17 forbidden transitions), C976 (6-state macro partition),
  C1007 (gatekeeper classes), C1084 (section AXM ordering),
  C1107 (Stars LINK elevation 7.4x), C1108 (vocabulary clamping falsified)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats as sp_stats
from itertools import combinations

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, BFolioDecoder, BTokenAnalysis

RESULTS = ROOT / "phases" / "STARS_PARADOX_RESOLUTION" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

# --- Constants ---

MACRO_NAMES = ['FL_HAZ', 'FQ', 'CC', 'AXm', 'AXM', 'FL_SAFE']
MACRO_PARTITION = {
    'FL_HAZ': {7, 30},
    'FQ': {9, 13, 14, 23},
    'CC': {10, 11, 12},
    'AXm': {3, 5, 18, 19, 42, 45},
    'AXM': {1, 2, 4, 6, 8, 15, 16, 17, 20, 21, 22, 24, 25, 26, 27, 28, 29,
            31, 32, 33, 34, 35, 36, 37, 39, 41, 43, 44, 46, 47, 48, 49},
    'FL_SAFE': {38, 40},
}
CLASS_TO_MACRO = {}
for _macro, _classes in MACRO_PARTITION.items():
    for _c in _classes:
        CLASS_TO_MACRO[_c] = _macro

GATEKEEPER_CLASSES = {15, 20, 21, 22, 25}

CC_TRIGGERS = {
    'daiin': 'CHSH_PRECISION', 'dain': 'CHSH_PRECISION',
    'aiin': 'FQ_FREQUENT', 'ain': 'FQ_FREQUENT',
    'ol': 'QO_ENERGY',
    'or': 'CLOSE_FLOW', 'al': 'CLOSE_FLOW', 'ar': 'CLOSE_FLOW',
}
CC_TRIGGER_TYPES = sorted(set(CC_TRIGGERS.values()))

N_BOOTSTRAP = 10000
RNG_SEED = 42


# ===================================================================
# Utilities
# ===================================================================

def round_floats(obj, decimals=4):
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return round(float(obj), decimals)
    if isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(x, decimals) for x in obj]
    return obj


def compute_jsd(p, q):
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    ps, qs = p.sum(), q.sum()
    if ps == 0 or qs == 0:
        return 0.0
    p, q = p / ps, q / qs
    m = 0.5 * (p + q)
    return float(0.5 * (sp_stats.entropy(p, m, base=2) + sp_stats.entropy(q, m, base=2)))


# ===================================================================
# Initialize
# ===================================================================
print("=" * 70)
print("PHASE 394: STARS PARADOX RESOLUTION")
print("=" * 70)
print()

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# Load regime mapping
regime_path = ROOT / 'data' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)
folio_regime = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}

# Build per-folio data from Currier B
folio_tokens = defaultdict(list)
folio_lines = defaultdict(lambda: defaultdict(list))
folio_section = {}

for tok in tx.currier_b():
    w = tok.word.strip()
    if not w or '*' in w:
        continue
    folio_tokens[tok.folio].append(tok)
    if tok.folio not in folio_section:
        folio_section[tok.folio] = tok.section

    # Build macro-state line sequences
    cls = decoder._token_to_class.get(w)
    macro = CLASS_TO_MACRO.get(cls) if cls is not None else None
    folio_lines[tok.folio][tok.line].append({
        'word': w, 'class': cls, 'macro': macro,
    })

# Partition
stars_folios = set(f for f, s in folio_section.items() if s == 'S')
non_stars_folios = set(f for f, s in folio_section.items() if s in ('B', 'H'))
all_folios = stars_folios | non_stars_folios

print(f"Stars folios: {len(stars_folios)}")
print(f"Non-Stars folios (B+H): {len(non_stars_folios)}")
print(f"Stars REGIME: {Counter(folio_regime.get(f, 'X') for f in stars_folios)}")
print(f"Non-Stars REGIME: {Counter(folio_regime.get(f, 'X') for f in non_stars_folios)}")
print()

# --- Pre-compute per-folio metrics ---

# AXM self-transition rate
def compute_axm_self(folio):
    states = []
    for line_key in sorted(folio_lines[folio].keys()):
        for tok in folio_lines[folio][line_key]:
            if tok['macro']:
                states.append(tok['macro'])
    axm_trans = sum(1 for i in range(len(states) - 1) if states[i] == 'AXM')
    axm_self = sum(1 for i in range(len(states) - 1)
                   if states[i] == 'AXM' and states[i + 1] == 'AXM')
    return axm_self / axm_trans if axm_trans > 5 else None


# AXM run lengths per folio (within lines)
def compute_axm_runs(folio):
    runs = []
    for line_key in sorted(folio_lines[folio].keys()):
        seq = folio_lines[folio][line_key]
        if len(seq) < 2:
            continue
        current = seq[0]['macro']
        run_len = 1
        for tok in seq[1:]:
            if tok['macro'] == current:
                run_len += 1
            else:
                if current == 'AXM':
                    runs.append(run_len)
                current = tok['macro']
                run_len = 1
        if current == 'AXM':
            runs.append(run_len)
    return runs


# LINK density
def compute_link_density(folio):
    toks = folio_tokens[folio]
    if not toks:
        return 0.0
    link_count = 0
    for tok in toks:
        m = morph.extract(tok.word)
        if m.prefix:
            lane = BTokenAnalysis._get_prefix_lane(m.prefix)
            if lane == 'LINK':
                link_count += 1
    return link_count / len(toks)


# CC trigger entropy per folio
def compute_cc_entropy(folio):
    counts = Counter()
    for tok in folio_tokens[folio]:
        if tok.word in CC_TRIGGERS:
            counts[CC_TRIGGERS[tok.word]] += 1
    total = sum(counts.values())
    if total < 3:
        return None
    probs = np.array([counts.get(ct, 0) / total for ct in CC_TRIGGER_TYPES])
    probs = probs[probs > 0]
    return float(sp_stats.entropy(probs, base=2))


# Gatekeeper entropy at AXM exits
def compute_gk_entropy(folio):
    exit_classes = Counter()
    for line_key in sorted(folio_lines[folio].keys()):
        seq = folio_lines[folio][line_key]
        for i in range(len(seq) - 1):
            if seq[i]['macro'] == 'AXM' and seq[i + 1]['macro'] != 'AXM':
                cls = seq[i]['class']
                if cls in GATEKEEPER_CLASSES:
                    exit_classes[cls] += 1
    total = sum(exit_classes.values())
    if total < 3:
        return None
    probs = np.array([exit_classes.get(c, 0) / total for c in sorted(GATEKEEPER_CLASSES)])
    probs = probs[probs > 0]
    return float(sp_stats.entropy(probs, base=2))


# Class-level transition counter
def compute_class_transitions(folio):
    trans = Counter()
    for line_key in sorted(folio_lines[folio].keys()):
        seq = folio_lines[folio][line_key]
        for i in range(len(seq) - 1):
            c1, c2 = seq[i]['class'], seq[i + 1]['class']
            if c1 is not None and c2 is not None:
                trans[(c1, c2)] += 1
    return trans


print("Pre-computing per-folio metrics...")
axm_rates = {}
link_densities = {}
cc_entropies = {}
gk_entropies = {}
class_transitions = {}

for f in all_folios:
    axm_rates[f] = compute_axm_self(f)
    link_densities[f] = compute_link_density(f)
    cc_entropies[f] = compute_cc_entropy(f)
    gk_entropies[f] = compute_gk_entropy(f)
    class_transitions[f] = compute_class_transitions(f)

# AXM rates by section
stars_axm = [axm_rates[f] for f in stars_folios if axm_rates[f] is not None]
herbal_folios = set(f for f in non_stars_folios if folio_section[f] == 'H')
bio_folios = set(f for f in non_stars_folios if folio_section[f] == 'B')
herbal_axm = [axm_rates[f] for f in herbal_folios if axm_rates[f] is not None]
bio_axm = [axm_rates[f] for f in bio_folios if axm_rates[f] is not None]
ns_axm = [axm_rates[f] for f in non_stars_folios if axm_rates[f] is not None]

stars_var = float(np.var(stars_axm, ddof=1))
herbal_var = float(np.var(herbal_axm, ddof=1))
bio_var = float(np.var(bio_axm, ddof=1))

print(f"  AXM variance: Stars={stars_var:.6f}, Herbal={herbal_var:.6f}, Bio={bio_var:.6f}")
print(f"  Stars AXM rates: n={len(stars_axm)}, mean={np.mean(stars_axm):.4f}")
print(f"  Herbal AXM rates: n={len(herbal_axm)}, mean={np.mean(herbal_axm):.4f}")
print(f"  Bio AXM rates: n={len(bio_axm)}, mean={np.mean(bio_axm):.4f}")

# Paragraph analyses
print("  Computing paragraph analyses...")
folio_paragraphs = {}
for f in all_folios:
    try:
        folio_paragraphs[f] = decoder.analyze_folio_paragraphs(f)
    except Exception:
        folio_paragraphs[f] = []

print(f"  Paragraphs computed for {len(folio_paragraphs)} folios")
print()


# ===================================================================
# GATE 1: PARADOX CONFIRMATION
# ===================================================================
print("=" * 70)
print("GATE 1: PARADOX CONFIRMATION")
print("=" * 70)
print()

# --- G1.1: Bootstrap AXM Variance ---
print("-" * 70)
print("G1.1: Bootstrap Stars Folio Count from Herbal")
print("-" * 70)
print()

rng = np.random.RandomState(RNG_SEED)
n_stars = len(stars_axm)
herbal_arr = np.array(herbal_axm)

boot_vars = np.empty(N_BOOTSTRAP)
for i in range(N_BOOTSTRAP):
    sample = herbal_arr[rng.choice(len(herbal_arr), size=n_stars, replace=True)]
    boot_vars[i] = np.var(sample, ddof=1)

g1_1_percentile = float(np.mean(boot_vars <= stars_var) * 100)
g1_1_p5 = float(np.percentile(boot_vars, 5))

print(f"  Stars AXM variance: {stars_var:.6f}")
print(f"  Herbal bootstrap 5th percentile: {g1_1_p5:.6f}")
print(f"  Stars percentile in bootstrap: {g1_1_percentile:.1f}th")
g1_1_passed = g1_1_percentile < 5.0
print(f"  G1.1 VERDICT: {'PASS' if g1_1_passed else 'FAIL'}")
print()

g1_1_data = {
    'stars_axm_var': stars_var,
    'herbal_axm_var': herbal_var,
    'bootstrap_5th_pct': g1_1_p5,
    'stars_percentile': g1_1_percentile,
    'n_stars': n_stars,
    'n_herbal': len(herbal_axm),
    'n_boot': N_BOOTSTRAP,
    'passed': g1_1_passed,
}

# --- G1.2: REGIME-Matched Variance ---
print("-" * 70)
print("G1.2: REGIME-Matched AXM Variance Comparison")
print("-" * 70)
print()

g1_2_results = {}
for regime in ['REGIME_1', 'REGIME_3']:
    s_rates = [axm_rates[f] for f in stars_folios
               if folio_regime.get(f) == regime and axm_rates.get(f) is not None]
    ns_rates = [axm_rates[f] for f in non_stars_folios
                if folio_regime.get(f) == regime and axm_rates.get(f) is not None]

    if len(s_rates) < 3 or len(ns_rates) < 3:
        g1_2_results[regime] = {'note': 'insufficient data', 'passed': False}
        print(f"  {regime}: insufficient data (Stars={len(s_rates)}, NS={len(ns_rates)})")
        continue

    s_var = np.var(s_rates, ddof=1)
    ns_var = np.var(ns_rates, ddof=1)
    ratio = ns_var / s_var if s_var > 0 else float('inf')

    # MW on |deviation from regime mean|
    regime_mean = np.mean(s_rates + ns_rates)
    s_devs = [abs(r - regime_mean) for r in s_rates]
    ns_devs = [abs(r - regime_mean) for r in ns_rates]
    u, p = sp_stats.mannwhitneyu(ns_devs, s_devs, alternative='greater')

    g1_2_results[regime] = {
        'stars_var': float(s_var), 'non_stars_var': float(ns_var),
        'ratio': float(ratio), 'u_stat': float(u), 'p': float(p),
        'n_stars': len(s_rates), 'n_non_stars': len(ns_rates),
        'passed': ratio > 2.0 or p < 0.05,
    }
    print(f"  {regime}: Stars var={s_var:.6f}, NS var={ns_var:.6f}, "
          f"ratio={ratio:.2f}, MW p={p:.4f}")

g1_2_any_pass = any(r.get('passed', False) for r in g1_2_results.values())
print(f"\n  G1.2 VERDICT: {'PASS' if g1_2_any_pass else 'FAIL'}")
print()

g1_2_data = {'regime_results': g1_2_results, 'passed': g1_2_any_pass}

gate1_passed = g1_1_passed and g1_2_any_pass
print(f"GATE 1 OVERALL: {'PASS — paradox confirmed' if gate1_passed else 'FAIL — paradox not confirmed'}")
print()


# ===================================================================
# GATE 2: MECHANISMS
# ===================================================================
print("=" * 70)
print("GATE 2: MECHANISM TESTS")
print("=" * 70)
print()

# --- M1: LINK REGULATION ---
print("-" * 70)
print("M1: LINK Regulation")
print("-" * 70)
print()

# M1.1: Within-Stars LINK-AXM deviation correlation
stars_mean_axm = np.mean(stars_axm)
m1_1_link, m1_1_dev = [], []
for f in stars_folios:
    if axm_rates.get(f) is not None:
        m1_1_link.append(link_densities[f])
        m1_1_dev.append(abs(axm_rates[f] - stars_mean_axm))

m1_1_rho, m1_1_p = sp_stats.spearmanr(m1_1_link, m1_1_dev)
m1_1_passed = m1_1_rho < -0.30 and m1_1_p < 0.05

print(f"  M1.1: Within-Stars LINK vs |AXM deviation|")
print(f"    Spearman rho = {m1_1_rho:.4f}, p = {m1_1_p:.4f}, n = {len(m1_1_link)}")
print(f"    VERDICT: {'PASS' if m1_1_passed else 'FAIL'}")

m1_1_data = {
    'rho': float(m1_1_rho), 'p': float(m1_1_p), 'n': len(m1_1_link),
    'passed': m1_1_passed,
}

# M1.2: LINK removal effect
print(f"\n  M1.2: LINK Token Removal Effect")

# Identify LINK words in Stars
link_words = set()
for f in stars_folios:
    for tok in folio_tokens[f]:
        m = morph.extract(tok.word)
        if m.prefix and BTokenAnalysis._get_prefix_lane(m.prefix) == 'LINK':
            link_words.add(tok.word)

# Original run lengths
orig_runs = []
for f in stars_folios:
    orig_runs.extend(compute_axm_runs(f))
orig_mean_rl = np.mean(orig_runs) if orig_runs else 0

# Build stripped folio lines (exclude LINK words)
stripped_lines = defaultdict(lambda: defaultdict(list))
for f in stars_folios:
    for line_key, seq in folio_lines[f].items():
        stripped = [tok for tok in seq if tok['word'] not in link_words]
        if stripped:
            stripped_lines[f][line_key] = stripped

# Stripped run lengths
stripped_runs = []
for f in stars_folios:
    for line_key in sorted(stripped_lines[f].keys()):
        seq = stripped_lines[f][line_key]
        if len(seq) < 2:
            continue
        current = seq[0]['macro']
        run_len = 1
        for tok in seq[1:]:
            if tok['macro'] == current:
                run_len += 1
            else:
                if current == 'AXM':
                    stripped_runs.append(run_len)
                current = tok['macro']
                run_len = 1
        if current == 'AXM':
            stripped_runs.append(run_len)

stripped_mean_rl = np.mean(stripped_runs) if stripped_runs else 0

# Stripped AXM variance
stripped_axm_rates = []
for f in stars_folios:
    states = []
    for line_key in sorted(stripped_lines[f].keys()):
        for tok in stripped_lines[f][line_key]:
            if tok['macro']:
                states.append(tok['macro'])
    axm_trans = sum(1 for i in range(len(states) - 1) if states[i] == 'AXM')
    axm_self = sum(1 for i in range(len(states) - 1)
                   if states[i] == 'AXM' and states[i + 1] == 'AXM')
    if axm_trans > 5:
        stripped_axm_rates.append(axm_self / axm_trans)

stripped_var = np.var(stripped_axm_rates, ddof=1) if len(stripped_axm_rates) > 1 else 0

rl_change = (stripped_mean_rl - orig_mean_rl) / orig_mean_rl if orig_mean_rl > 0 else 0
var_change = (stripped_var - stars_var) / stars_var if stars_var > 0 else 0
m1_2_passed = rl_change > 0.15 and var_change > 0.20

print(f"    LINK words removed: {len(link_words)}")
print(f"    Run length: {orig_mean_rl:.3f} -> {stripped_mean_rl:.3f} ({rl_change * 100:+.1f}%)")
print(f"    AXM variance: {stars_var:.6f} -> {stripped_var:.6f} ({var_change * 100:+.1f}%)")
print(f"    VERDICT: {'PASS' if m1_2_passed else 'FAIL'}")

m1_2_data = {
    'orig_mean_run_length': float(orig_mean_rl),
    'stripped_mean_run_length': float(stripped_mean_rl),
    'run_length_change_pct': float(100 * rl_change),
    'orig_axm_var': stars_var,
    'stripped_axm_var': float(stripped_var),
    'variance_change_pct': float(100 * var_change),
    'n_link_words': len(link_words),
    'passed': m1_2_passed,
}

# M1.3: Cross-section partial correlation
print(f"\n  M1.3: Cross-Section LINK -> AXM Deviation (partial)")

section_means = {}
for sec in ['S', 'B', 'H']:
    sec_rates = [axm_rates[f] for f in all_folios
                 if folio_section.get(f) == sec and axm_rates.get(f) is not None]
    if sec_rates:
        section_means[sec] = np.mean(sec_rates)

m1_3_links, m1_3_devs, m1_3_sec, m1_3_reg, m1_3_is_stars = [], [], [], [], []
REGIME_RANK = {'REGIME_1': 0, 'REGIME_2': 1, 'REGIME_3': 2, 'REGIME_4': 3}

for f in all_folios:
    sec = folio_section.get(f)
    if sec in section_means and axm_rates.get(f) is not None:
        m1_3_links.append(link_densities[f])
        m1_3_devs.append(abs(axm_rates[f] - section_means[sec]))
        m1_3_sec.append({'S': 0, 'B': 1, 'H': 2}[sec])
        m1_3_reg.append(REGIME_RANK.get(folio_regime.get(f, ''), 0))
        m1_3_is_stars.append(1 if sec == 'S' else 0)

m1_3_links = np.array(m1_3_links)
m1_3_devs = np.array(m1_3_devs)
X_ctrl = np.column_stack([
    np.ones(len(m1_3_links)),
    np.array(m1_3_sec, dtype=float),
    np.array(m1_3_reg, dtype=float),
])
beta_l = np.linalg.lstsq(X_ctrl, m1_3_links, rcond=None)[0]
beta_d = np.linalg.lstsq(X_ctrl, m1_3_devs, rcond=None)[0]
links_resid = m1_3_links - X_ctrl @ beta_l
devs_resid = m1_3_devs - X_ctrl @ beta_d

m1_3_rho, m1_3_p = sp_stats.spearmanr(links_resid, devs_resid)

# Outlier check
stars_mask = np.array(m1_3_is_stars, dtype=bool)
ns_resid_mean = np.mean(devs_resid[~stars_mask])
ns_resid_std = np.std(devs_resid[~stars_mask], ddof=1)
stars_resid_mean = np.mean(devs_resid[stars_mask])
is_outlier = abs(stars_resid_mean - ns_resid_mean) > 2 * ns_resid_std

m1_3_passed = m1_3_rho < -0.20 and m1_3_p < 0.05 and not is_outlier

print(f"    Partial rho = {m1_3_rho:.4f}, p = {m1_3_p:.4f}, n = {len(m1_3_links)}")
print(f"    Stars outlier: {is_outlier}")
print(f"    VERDICT: {'PASS' if m1_3_passed else 'FAIL'}")

m1_3_data = {
    'partial_rho': float(m1_3_rho), 'p': float(m1_3_p),
    'stars_is_outlier': bool(is_outlier), 'n': len(m1_3_links),
    'passed': m1_3_passed,
}

m1_pass_count = sum([m1_1_passed, m1_2_passed, m1_3_passed])
m1_passed = m1_pass_count >= 2
print(f"\n  M1 OVERALL: {m1_pass_count}/3 -> {'PASS' if m1_passed else 'FAIL'}")
print()

# --- M2: CC TRIGGER CHANNELING ---
print("-" * 70)
print("M2: CC Trigger Channeling")
print("-" * 70)
print()

# M2.1: Stars CC trigger entropy
stars_cc_ent = [cc_entropies[f] for f in stars_folios if cc_entropies[f] is not None]
ns_cc_ent = [cc_entropies[f] for f in non_stars_folios if cc_entropies[f] is not None]

if len(stars_cc_ent) >= 3 and len(ns_cc_ent) >= 3:
    m2_1_u, m2_1_p = sp_stats.mannwhitneyu(stars_cc_ent, ns_cc_ent, alternative='less')
else:
    m2_1_u, m2_1_p = 0, 1.0

m2_1_passed = m2_1_p < 0.05

print(f"  M2.1: Stars CC Trigger Entropy")
print(f"    Stars mean: {np.mean(stars_cc_ent):.4f} (n={len(stars_cc_ent)})")
print(f"    Non-Stars mean: {np.mean(ns_cc_ent):.4f} (n={len(ns_cc_ent)})")
print(f"    MW U={m2_1_u:.0f}, p={m2_1_p:.4f}")
print(f"    VERDICT: {'PASS' if m2_1_passed else 'FAIL'}")

m2_1_data = {
    'stars_mean': float(np.mean(stars_cc_ent)),
    'ns_mean': float(np.mean(ns_cc_ent)),
    'mw_u': float(m2_1_u), 'mw_p': float(m2_1_p),
    'n_stars': len(stars_cc_ent), 'n_ns': len(ns_cc_ent),
    'passed': m2_1_passed,
}

# M2.2: CC->next effective diversity
print(f"\n  M2.2: CC->Next-State Effective Diversity")


def cc_exit_distribution(folio_set):
    exit_counts = Counter()
    for f in folio_set:
        for line_key in sorted(folio_lines[f].keys()):
            seq = folio_lines[f][line_key]
            for i in range(len(seq) - 1):
                if seq[i]['macro'] == 'CC' and seq[i + 1]['macro'] != 'CC':
                    exit_counts[seq[i + 1]['macro']] += 1
    total = sum(exit_counts.values())
    if total == 0:
        return {}, 0.0, 0
    probs = {s: exit_counts[s] / total for s in exit_counts}
    p_arr = np.array(list(probs.values()))
    ent = sp_stats.entropy(p_arr, base=np.e)
    return probs, float(np.exp(ent)), total


stars_cc_dist, stars_cc_eff, stars_cc_n = cc_exit_distribution(stars_folios)
ns_cc_dist, ns_cc_eff, ns_cc_n = cc_exit_distribution(non_stars_folios)

m2_2_passed = stars_cc_eff < 2.0 and ns_cc_eff > 2.5

print(f"    Stars: effective diversity={stars_cc_eff:.3f} (n={stars_cc_n})")
print(f"    Non-Stars: effective diversity={ns_cc_eff:.3f} (n={ns_cc_n})")
print(f"    Stars dist: {stars_cc_dist}")
print(f"    VERDICT: {'PASS' if m2_2_passed else 'FAIL'}")

m2_2_data = {
    'stars_effective': float(stars_cc_eff), 'ns_effective': float(ns_cc_eff),
    'stars_n': stars_cc_n, 'ns_n': ns_cc_n,
    'stars_dist': {k: round(v, 4) for k, v in stars_cc_dist.items()},
    'ns_dist': {k: round(v, 4) for k, v in ns_cc_dist.items()},
    'passed': m2_2_passed,
}

# M2.3: Gatekeeper entropy
print(f"\n  M2.3: Gatekeeper Entropy at AXM Exits")

stars_gk = [gk_entropies[f] for f in stars_folios if gk_entropies[f] is not None]
ns_gk = [gk_entropies[f] for f in non_stars_folios if gk_entropies[f] is not None]

stars_gk_mean = np.mean(stars_gk) if stars_gk else None
ns_gk_p5 = np.percentile(ns_gk, 5) if ns_gk else None

m2_3_passed = (stars_gk_mean is not None and ns_gk_p5 is not None
               and stars_gk_mean < ns_gk_p5)

print(f"    Stars mean GK entropy: {stars_gk_mean:.4f} (n={len(stars_gk)})" if stars_gk_mean else "    Stars: insufficient data")
print(f"    Non-Stars 5th percentile: {ns_gk_p5:.4f} (n={len(ns_gk)})" if ns_gk_p5 else "    NS: insufficient data")
print(f"    VERDICT: {'PASS' if m2_3_passed else 'FAIL'}")

m2_3_data = {
    'stars_mean': float(stars_gk_mean) if stars_gk_mean is not None else None,
    'ns_5th_pct': float(ns_gk_p5) if ns_gk_p5 is not None else None,
    'ns_mean': float(np.mean(ns_gk)) if ns_gk else None,
    'n_stars': len(stars_gk), 'n_ns': len(ns_gk),
    'passed': m2_3_passed,
}

m2_pass_count = sum([m2_1_passed, m2_2_passed, m2_3_passed])
m2_passed = m2_pass_count >= 2
print(f"\n  M2 OVERALL: {m2_pass_count}/3 -> {'PASS' if m2_passed else 'FAIL'}")
print()

# --- M3: PARAGRAPH CONSTRAINT ---
print("-" * 70)
print("M3: Paragraph Constraint")
print("-" * 70)
print()

# M3.1: Inter-paragraph JSD
print(f"  M3.1: Inter-Paragraph Macro-State JSD")


def folio_para_jsd(folio):
    paras = folio_paragraphs.get(folio, [])
    if len(paras) < 2:
        return None
    dists = []
    for para in paras:
        counts = Counter()
        for la in para.lines:
            line_key = la.line_id
            if line_key in folio_lines[folio]:
                for tok in folio_lines[folio][line_key]:
                    if tok['macro']:
                        counts[tok['macro']] += 1
        total = sum(counts.values())
        if total > 0:
            dists.append(np.array([counts.get(s, 0) / total for s in MACRO_NAMES]))
    if len(dists) < 2:
        return None
    jsds = [compute_jsd(d1, d2) for d1, d2 in combinations(dists, 2)]
    return float(np.mean(jsds)) if jsds else None


stars_jsds = [folio_para_jsd(f) for f in stars_folios]
stars_jsds = [j for j in stars_jsds if j is not None]

ns_jsds_by_sec = defaultdict(list)
for f in non_stars_folios:
    j = folio_para_jsd(f)
    if j is not None:
        ns_jsds_by_sec[folio_section[f]].append(j)

ns_all_jsds = [j for vals in ns_jsds_by_sec.values() for j in vals]

stars_mean_jsd = np.mean(stars_jsds) if stars_jsds else None

if len(stars_jsds) >= 3 and len(ns_all_jsds) >= 3:
    m3_1_u, m3_1_p = sp_stats.mannwhitneyu(stars_jsds, ns_all_jsds, alternative='less')
else:
    m3_1_u, m3_1_p = 0, 1.0

m3_1_passed = (stars_mean_jsd is not None and stars_mean_jsd < 0.05
               and m3_1_p < 0.05)

print(f"    Stars mean JSD: {stars_mean_jsd:.4f} (n={len(stars_jsds)})" if stars_mean_jsd else "    Stars: insufficient data")
for sec, vals in ns_jsds_by_sec.items():
    print(f"    Section {sec} mean JSD: {np.mean(vals):.4f} (n={len(vals)})")
print(f"    MW p={m3_1_p:.4f}")
print(f"    VERDICT: {'PASS' if m3_1_passed else 'FAIL'}")

m3_1_data = {
    'stars_mean_jsd': float(stars_mean_jsd) if stars_mean_jsd is not None else None,
    'section_jsds': {s: float(np.mean(v)) for s, v in ns_jsds_by_sec.items()},
    'mw_p': float(m3_1_p),
    'n_stars': len(stars_jsds), 'n_ns': len(ns_all_jsds),
    'passed': m3_1_passed,
}

# M3.2: Paragraph count x Stars interaction
print(f"\n  M3.2: Paragraph Count × Stars Interaction")

m3_2_pc, m3_2_is_s, m3_2_dev = [], [], []
for f in all_folios:
    sec = folio_section.get(f)
    if sec in section_means and axm_rates.get(f) is not None and f in folio_paragraphs:
        n_paras = len(folio_paragraphs[f])
        if n_paras == 0:
            continue
        m3_2_pc.append(n_paras)
        m3_2_is_s.append(1 if sec == 'S' else 0)
        m3_2_dev.append(abs(axm_rates[f] - section_means[sec]))

m3_2_pc = np.array(m3_2_pc, dtype=float)
m3_2_is_s = np.array(m3_2_is_s, dtype=float)
m3_2_dev = np.array(m3_2_dev)
m3_2_inter = m3_2_pc * m3_2_is_s

X_m3 = np.column_stack([np.ones(len(m3_2_pc)), m3_2_pc, m3_2_is_s, m3_2_inter])
beta_m3 = np.linalg.lstsq(X_m3, m3_2_dev, rcond=None)[0]

n_m3 = len(m3_2_dev)
p_m3 = X_m3.shape[1]
if n_m3 > p_m3:
    resid_m3 = m3_2_dev - X_m3 @ beta_m3
    mse_m3 = np.sum(resid_m3 ** 2) / (n_m3 - p_m3)
    try:
        var_beta = mse_m3 * np.linalg.inv(X_m3.T @ X_m3)
        se_inter = np.sqrt(var_beta[3, 3])
        t_inter = beta_m3[3] / se_inter if se_inter > 0 else 0
        p_inter = 2 * sp_stats.t.sf(abs(t_inter), n_m3 - p_m3)
    except np.linalg.LinAlgError:
        t_inter, p_inter = 0, 1.0
else:
    t_inter, p_inter = 0, 1.0

m3_2_passed = beta_m3[3] < 0 and p_inter < 0.05

print(f"    Interaction coefficient: {beta_m3[3]:.6f}")
print(f"    t = {t_inter:.3f}, p = {p_inter:.4f}")
print(f"    VERDICT: {'PASS' if m3_2_passed else 'FAIL'}")

m3_2_data = {
    'interaction_coeff': float(beta_m3[3]),
    't_stat': float(t_inter), 'p': float(p_inter),
    'n': n_m3,
    'passed': m3_2_passed,
}

m3_pass_count = sum([m3_1_passed, m3_2_passed])
m3_passed = m3_pass_count >= 1
print(f"\n  M3 OVERALL: {m3_pass_count}/2 -> {'PASS' if m3_passed else 'FAIL'}")
print()

# --- M4: DE FACTO FORBIDDEN TRANSITIONS ---
print("-" * 70)
print("M4: De Facto Forbidden Transitions")
print("-" * 70)
print()

# M4.1: Excess zero class-pair transitions
print(f"  M4.1: Stars Excess Zero-Transitions")

# Aggregate Stars transitions
stars_trans_total = Counter()
for f in stars_folios:
    stars_trans_total += class_transitions[f]

# All observed classes in the corpus
all_classes = set()
for f in all_folios:
    for line_key, seq in folio_lines[f].items():
        for tok in seq:
            if tok['class'] is not None:
                all_classes.add(tok['class'])

n_classes = len(all_classes)
n_possible = n_classes ** 2
stars_observed_pairs = len(set(stars_trans_total.keys()))
stars_zeros = n_possible - stars_observed_pairs

# Bootstrap: draw matched folio count from non-Stars
rng_m4 = np.random.RandomState(RNG_SEED)
ns_folio_list = sorted(non_stars_folios)
n_boot_m4 = 1000
boot_zeros = []

for _ in range(n_boot_m4):
    sample = rng_m4.choice(ns_folio_list, size=min(len(stars_folios), len(ns_folio_list)), replace=True)
    boot_trans = Counter()
    for f in sample:
        boot_trans += class_transitions[f]
    boot_zeros.append(n_possible - len(set(boot_trans.keys())))

boot_mean_zeros = np.mean(boot_zeros)
excess_pct = (stars_zeros - boot_mean_zeros) / boot_mean_zeros * 100 if boot_mean_zeros > 0 else 0
m4_1_p = float(np.mean([bz >= stars_zeros for bz in boot_zeros]))
m4_1_passed = excess_pct > 20 and m4_1_p < 0.05

print(f"    Classes in corpus: {n_classes}, possible pairs: {n_possible}")
print(f"    Stars observed pairs: {stars_observed_pairs}, zeros: {stars_zeros}")
print(f"    Bootstrap mean zeros: {boot_mean_zeros:.1f}")
print(f"    Excess: {excess_pct:.1f}%, p = {m4_1_p:.4f}")
print(f"    VERDICT: {'PASS' if m4_1_passed else 'FAIL'}")

m4_1_data = {
    'n_classes': n_classes, 'n_possible': n_possible,
    'stars_zeros': stars_zeros, 'boot_mean_zeros': float(boot_mean_zeros),
    'excess_pct': float(excess_pct), 'p': m4_1_p,
    'passed': m4_1_passed,
}

# M4.2: Universally absent class pairs
print(f"\n  M4.2: Universally Absent Class Pairs")

ns_trans_total = Counter()
ns_total_count = 0
for f in non_stars_folios:
    ct = class_transitions[f]
    ns_trans_total += ct
    ns_total_count += sum(ct.values())

stars_total_count = sum(stars_trans_total.values())

absent_in_stars = {}
for pair, ns_count in ns_trans_total.items():
    if pair not in stars_trans_total or stars_trans_total[pair] == 0:
        ns_rate = ns_count / ns_total_count if ns_total_count > 0 else 0
        expected = ns_rate * stars_total_count
        poisson_p = float(np.exp(-expected)) if expected < 700 else 0.0
        absent_in_stars[pair] = {
            'ns_count': int(ns_count),
            'expected_in_stars': float(expected),
            'poisson_p': poisson_p,
        }

n_bonf = len(absent_in_stars)
significant_pairs = []
for pair, data in absent_in_stars.items():
    corrected_p = data['poisson_p'] * n_bonf
    data['bonferroni_p'] = float(corrected_p)
    if corrected_p < 0.01:
        significant_pairs.append({
            'class_a': int(pair[0]), 'class_b': int(pair[1]),
            **data,
        })

significant_pairs.sort(key=lambda x: x['bonferroni_p'])
m4_2_passed = len(significant_pairs) >= 3

print(f"    Pairs absent in Stars but present in NS: {len(absent_in_stars)}")
print(f"    Bonferroni tests: {n_bonf}")
print(f"    Significant (corrected p < 0.01): {len(significant_pairs)}")
for sp in significant_pairs[:5]:
    macro_a = CLASS_TO_MACRO.get(sp['class_a'], '?')
    macro_b = CLASS_TO_MACRO.get(sp['class_b'], '?')
    print(f"      ({sp['class_a']}->{sp['class_b']}) [{macro_a}->{macro_b}]: "
          f"NS={sp['ns_count']}, expected={sp['expected_in_stars']:.2f}, "
          f"p_bonf={sp['bonferroni_p']:.6f}")
print(f"    VERDICT: {'PASS' if m4_2_passed else 'FAIL'}")

m4_2_data = {
    'n_absent': len(absent_in_stars),
    'n_bonferroni': n_bonf,
    'n_significant': len(significant_pairs),
    'significant_pairs': significant_pairs[:10],
    'passed': m4_2_passed,
}

# M4.3: Markov model reproduction
print(f"\n  M4.3: Markov + Forbidden Pairs Simulation")

forbidden_pairs_m4 = [(sp['class_a'], sp['class_b']) for sp in significant_pairs]

if len(forbidden_pairs_m4) == 0:
    m4_3_data = {'note': 'no forbidden pairs from M4.2', 'passed': False}
    m4_3_passed = False
    print(f"    Skipped — no forbidden pairs identified in M4.2")
    print(f"    VERDICT: FAIL (skipped)")
else:
    # Build transition matrix from Stars class sequences
    sorted_classes = sorted(all_classes)
    class_idx = {c: i for i, c in enumerate(sorted_classes)}
    n_cls = len(sorted_classes)
    trans_matrix = np.zeros((n_cls, n_cls))
    for f in stars_folios:
        for pair, count in class_transitions[f].items():
            if pair[0] in class_idx and pair[1] in class_idx:
                trans_matrix[class_idx[pair[0]], class_idx[pair[1]]] += count

    # Constrained model: zero out forbidden pairs
    constrained = trans_matrix.copy()
    for (ca, cb) in forbidden_pairs_m4:
        if ca in class_idx and cb in class_idx:
            constrained[class_idx[ca], class_idx[cb]] = 0

    row_sums = constrained.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    constrained_probs = constrained / row_sums

    # Simulate
    rng_sim = np.random.RandomState(RNG_SEED)
    folio_sizes = {f: sum(len(seq) for seq in folio_lines[f].values()) for f in stars_folios}
    n_sims = 1000

    sim_vars = []
    for _ in range(n_sims):
        sim_rates = []
        for f in stars_folios:
            seq_len = folio_sizes.get(f, 100)
            if seq_len < 10:
                continue
            state = rng_sim.choice(n_cls)
            states_sim = [sorted_classes[state]]
            for _ in range(seq_len - 1):
                probs = constrained_probs[state]
                if probs.sum() == 0:
                    state = rng_sim.choice(n_cls)
                else:
                    state = rng_sim.choice(n_cls, p=probs)
                states_sim.append(sorted_classes[state])

            macros = [CLASS_TO_MACRO.get(c) for c in states_sim]
            axm_trans = sum(1 for i in range(len(macros) - 1) if macros[i] == 'AXM')
            axm_self = sum(1 for i in range(len(macros) - 1)
                           if macros[i] == 'AXM' and macros[i + 1] == 'AXM')
            if axm_trans > 5:
                sim_rates.append(axm_self / axm_trans)

        if len(sim_rates) > 1:
            sim_vars.append(np.var(sim_rates, ddof=1))

    sim_mean_var = np.mean(sim_vars) if sim_vars else None
    if sim_mean_var is not None and stars_var > 0:
        error_pct = abs(sim_mean_var - stars_var) / stars_var * 100
    else:
        error_pct = None

    m4_3_passed = error_pct is not None and error_pct < 20

    print(f"    Forbidden pairs used: {len(forbidden_pairs_m4)}")
    print(f"    Observed Stars AXM var: {stars_var:.6f}")
    print(f"    Simulated mean AXM var: {sim_mean_var:.6f}" if sim_mean_var else "    Simulation failed")
    print(f"    Error: {error_pct:.1f}%" if error_pct else "    Error: N/A")
    print(f"    VERDICT: {'PASS' if m4_3_passed else 'FAIL'}")

    m4_3_data = {
        'n_forbidden': len(forbidden_pairs_m4),
        'observed_var': stars_var,
        'simulated_var': float(sim_mean_var) if sim_mean_var else None,
        'error_pct': float(error_pct) if error_pct else None,
        'n_sims': n_sims,
        'passed': m4_3_passed,
    }

m4_pass_count = sum([m4_1_passed, m4_2_passed, m4_3_passed])
m4_passed = m4_pass_count >= 2
print(f"\n  M4 OVERALL: {m4_pass_count}/3 -> {'PASS' if m4_passed else 'FAIL'}")
print()


# ===================================================================
# GATE 3: SUFFICIENCY
# ===================================================================
print("=" * 70)
print("GATE 3: SUFFICIENCY")
print("=" * 70)
print()

passing_mechanisms = []
if m1_passed:
    passing_mechanisms.append('M1')
if m2_passed:
    passing_mechanisms.append('M2')
if m3_passed:
    passing_mechanisms.append('M3')
if m4_passed:
    passing_mechanisms.append('M4')

print(f"Passing mechanisms: {passing_mechanisms if passing_mechanisms else 'NONE'}")

g3_1_data = None
g3_2_data = None

if not passing_mechanisms:
    print("No mechanisms passed Gate 2. Skipping Gate 3.")
    g3_passed = False
else:
    # Build mechanism features per folio
    mechanism_features = {}
    feature_names = []

    for f in all_folios:
        features = {}
        if 'M1' in passing_mechanisms:
            features['link_density'] = link_densities.get(f, 0)
        if 'M2' in passing_mechanisms:
            features['cc_entropy'] = cc_entropies.get(f, 0) or 0
            features['gk_entropy'] = gk_entropies.get(f, 0) or 0
        if 'M3' in passing_mechanisms:
            j = folio_para_jsd(f)
            features['mean_para_jsd'] = j if j is not None else 0
            features['n_paragraphs'] = len(folio_paragraphs.get(f, []))
        if 'M4' in passing_mechanisms:
            ct = class_transitions.get(f, Counter())
            features['n_observed_pairs'] = len(set(ct.keys()))
        mechanism_features[f] = features

    if mechanism_features:
        feature_names = sorted(next(iter(mechanism_features.values())).keys())

    # G3.1: Regression residual reduction
    print(f"\n  G3.1: Regression Residual Reduction")

    g3_is_stars, g3_devs, g3_feats = [], [], []
    for f in all_folios:
        sec = folio_section.get(f)
        if sec in section_means and axm_rates.get(f) is not None and f in mechanism_features:
            g3_is_stars.append(1 if sec == 'S' else 0)
            g3_devs.append(abs(axm_rates[f] - section_means[sec]))
            g3_feats.append([mechanism_features[f].get(fn, 0) for fn in feature_names])

    g3_is_stars = np.array(g3_is_stars, dtype=float)
    g3_devs = np.array(g3_devs)
    g3_feats = np.array(g3_feats)

    # Baseline: AXM dev ~ is_stars
    X_base = np.column_stack([np.ones(len(g3_is_stars)), g3_is_stars])
    beta_base = np.linalg.lstsq(X_base, g3_devs, rcond=None)[0]
    resid_base = g3_devs - X_base @ beta_base
    stars_mask_g3 = g3_is_stars > 0.5
    stars_mse_base = float(np.mean(resid_base[stars_mask_g3] ** 2))

    # Full: AXM dev ~ is_stars + mechanism features
    X_full = np.column_stack([np.ones(len(g3_is_stars)), g3_is_stars, g3_feats])
    beta_full = np.linalg.lstsq(X_full, g3_devs, rcond=None)[0]
    resid_full = g3_devs - X_full @ beta_full
    stars_mse_full = float(np.mean(resid_full[stars_mask_g3] ** 2))

    reduction = (1 - stars_mse_full / stars_mse_base) * 100 if stars_mse_base > 0 else 0
    g3_1_passed = reduction > 50

    print(f"    Stars MSE baseline: {stars_mse_base:.6f}")
    print(f"    Stars MSE with features: {stars_mse_full:.6f}")
    print(f"    Reduction: {reduction:.1f}%")
    print(f"    Features used: {feature_names}")
    print(f"    VERDICT: {'PASS' if g3_1_passed else 'FAIL'}")

    g3_1_data = {
        'stars_mse_baseline': stars_mse_base,
        'stars_mse_with_features': stars_mse_full,
        'reduction_pct': float(reduction),
        'feature_names': feature_names,
        'passed': g3_1_passed,
    }

    # G3.2: Counterfactual
    print(f"\n  G3.2: Counterfactual Simulation")

    # Non-Stars feature means
    ns_feat_means = {}
    for fn in feature_names:
        ns_vals = [mechanism_features[f].get(fn, 0) for f in non_stars_folios
                   if f in mechanism_features]
        ns_feat_means[fn] = np.mean(ns_vals) if ns_vals else 0

    # Fit on non-Stars: AXM rate ~ features
    X_ns, y_ns = [], []
    for f in non_stars_folios:
        if f in mechanism_features and axm_rates.get(f) is not None:
            X_ns.append([mechanism_features[f].get(fn, 0) for fn in feature_names])
            y_ns.append(axm_rates[f])

    if len(X_ns) > len(feature_names) + 1:
        X_ns = np.array(X_ns)
        y_ns = np.array(y_ns)
        X_ns_full = np.column_stack([np.ones(len(X_ns)), X_ns])
        beta_cf = np.linalg.lstsq(X_ns_full, y_ns, rcond=None)[0]

        # Predict Stars rates with NS feature means
        cf_rates = []
        for f in stars_folios:
            if axm_rates.get(f) is not None:
                x_cf = np.array([1.0] + [ns_feat_means[fn] for fn in feature_names])
                cf_rates.append(float(np.dot(beta_cf, x_cf)))

        if len(cf_rates) > 1:
            cf_var = float(np.var(cf_rates, ddof=1))
            ratio_cf = cf_var / stars_var if stars_var > 0 else 0
        else:
            cf_var, ratio_cf = None, None
    else:
        cf_var, ratio_cf = None, None

    g3_2_passed = cf_var is not None and ratio_cf is not None and ratio_cf > 1.5

    print(f"    Stars actual AXM var: {stars_var:.6f}")
    print(f"    Counterfactual AXM var: {cf_var:.6f}" if cf_var else "    Counterfactual: failed")
    print(f"    Ratio (CF/actual): {ratio_cf:.2f}" if ratio_cf else "    Ratio: N/A")
    print(f"    VERDICT: {'PASS' if g3_2_passed else 'FAIL'}")

    g3_2_data = {
        'stars_actual_var': stars_var,
        'counterfactual_var': float(cf_var) if cf_var is not None else None,
        'ratio': float(ratio_cf) if ratio_cf is not None else None,
        'passed': g3_2_passed,
    }

    g3_passed = (g3_1_data is not None and g3_1_data.get('passed', False))

print()


# ===================================================================
# SYNTHESIS
# ===================================================================
print("=" * 70)
print("PHASE 394 SYNTHESIS")
print("=" * 70)
print()

mechanism_verdicts = {
    'M1': {'sub_pass': m1_pass_count, 'total': 3, 'passed': m1_passed},
    'M2': {'sub_pass': m2_pass_count, 'total': 3, 'passed': m2_passed},
    'M3': {'sub_pass': m3_pass_count, 'total': 2, 'passed': m3_passed},
    'M4': {'sub_pass': m4_pass_count, 'total': 3, 'passed': m4_passed},
}

for name, mv in mechanism_verdicts.items():
    status = "PASS" if mv['passed'] else "FAIL"
    print(f"  {name}: {mv['sub_pass']}/{mv['total']} -> {status}")

print()
print(f"  Gate 1: {'PASS' if gate1_passed else 'FAIL'}")
print(f"  Passing mechanisms: {passing_mechanisms if passing_mechanisms else 'NONE'}")
print(f"  Gate 3: {'PASS' if g3_1_data and g3_1_data.get('passed') else 'FAIL (or skipped)'}")
print()

if not gate1_passed:
    overall = "PARADOX_NOT_CONFIRMED"
    summary = ("The Stars Paradox did not survive controls. Stars AXM variance is not "
               "significantly below expected after sample-size and REGIME matching.")
elif not passing_mechanisms:
    overall = "NO_MECHANISM_FOUND"
    summary = ("Paradox confirmed but none of the 4 tested mechanisms (LINK regulation, "
               "CC channeling, paragraph constraint, de facto forbidden transitions) explain it.")
elif g3_1_data and g3_1_data.get('passed'):
    overall = f"RESOLVED_{'_'.join(passing_mechanisms)}"
    summary = f"Paradox confirmed and resolved by: {', '.join(passing_mechanisms)}."
else:
    overall = f"PARTIAL_{'_'.join(passing_mechanisms)}"
    summary = (f"Mechanism(s) {', '.join(passing_mechanisms)} pass Gate 2 "
               f"but fail sufficiency (Gate 3).")

print(f"OVERALL VERDICT: {overall}")
print(f"  {summary}")
print()

# --- Build per-folio data for output ---
folio_data = {}
for f in all_folios:
    folio_data[f] = {
        'section': folio_section.get(f),
        'regime': folio_regime.get(f),
        'axm_self': axm_rates.get(f),
        'link_density': link_densities.get(f),
        'cc_entropy': cc_entropies.get(f),
        'gk_entropy': gk_entropies.get(f),
        'n_class_pairs': len(set(class_transitions.get(f, {}).keys())),
        'n_paragraphs': len(folio_paragraphs.get(f, [])),
        'n_tokens': len(folio_tokens.get(f, [])),
    }

# --- JSON output ---
results = round_floats({
    'phase': 394,
    'name': 'STARS_PARADOX_RESOLUTION',
    'test_count': 15,
    'n_stars': len(stars_folios),
    'n_non_stars': len(non_stars_folios),
    'stars_axm_var': stars_var,
    'herbal_axm_var': herbal_var,
    'bio_axm_var': bio_var,
    'gate1': {
        'g1_1': g1_1_data,
        'g1_2': g1_2_data,
        'passed': gate1_passed,
    },
    'gate2': {
        'M1': {'m1_1': m1_1_data, 'm1_2': m1_2_data, 'm1_3': m1_3_data},
        'M2': {'m2_1': m2_1_data, 'm2_2': m2_2_data, 'm2_3': m2_3_data},
        'M3': {'m3_1': m3_1_data, 'm3_2': m3_2_data},
        'M4': {'m4_1': m4_1_data, 'm4_2': m4_2_data, 'm4_3': m4_3_data},
    },
    'gate3': {
        'g3_1': g3_1_data,
        'g3_2': g3_2_data,
    },
    'synthesis': {
        'gate1_passed': gate1_passed,
        'mechanism_verdicts': mechanism_verdicts,
        'passing_mechanisms': passing_mechanisms,
        'gate3_passed': g3_1_data is not None and g3_1_data.get('passed', False),
        'overall': overall,
        'summary': summary,
    },
    'folio_data': folio_data,
})

output_path = RESULTS / 'stars_paradox_resolution.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to: {output_path}")
