"""
Phase 448: DARK_PIPELINE_CHARACTERIZATION
Tests whether the 8 validated gloss categories (C1250) generalize to the
~11.4% of Currier B tokens not covered by human-glossed MIDDLEs.

1,144 dark MIDDLEs have autoglosses (atom-level compositions).  We auto-assign
categories via plurality vote over constituent atoms, then test whether those
assignments are structurally real.

6-test battery:
  T1: Auto-assignment coverage & distribution  (descriptive)
  T2: Behavioral silhouette validation         (Null A: random partition)
  T3: Line-position differentiation            (Null B: random token labels)
  T4: Section profile divergence               (Null A: random partition)
  T5: Within-line MI                           (Null B: random token labels)
  T6: Q-MIDDLE structural characterization     (descriptive + divergence)
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats
from scipy.spatial.distance import jensenshannon

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "DARK_PIPELINE_CHARACTERIZATION" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
P_THRESHOLD = 0.01  # per-test (battery-level)

# ── Category mapping from Phase 446 ──────────────────────────────────
GLOSS_TO_CATEGORY = {
    'heat': 'THERMAL', 'fire': 'THERMAL', 'cool': 'THERMAL',
    'sustain': 'THERMAL', 'pulse': 'THERMAL', 'steady': 'THERMAL',
    'extended': 'THERMAL', 'deep': 'THERMAL', 'long': 'THERMAL',
    'overnight': 'THERMAL',
    'seal': 'CONTAINMENT', 'hold': 'CONTAINMENT', 'lock': 'CONTAINMENT',
    'bind': 'CONTAINMENT', 'bond': 'CONTAINMENT', 'rigid': 'CONTAINMENT',
    'firm': 'CONTAINMENT', 'dense': 'CONTAINMENT',
    'transfer': 'FLOW', 'gather': 'FLOW', 'discharge': 'FLOW',
    'release': 'FLOW', 'vent': 'FLOW', 'route': 'FLOW',
    'portion': 'FLOW', 'input': 'FLOW', 'intake': 'FLOW',
    'watch': 'MONITORING', 'check': 'MONITORING', 'verify': 'MONITORING',
    'confirm': 'MONITORING', 'scan': 'MONITORING', 'measure': 'MONITORING',
    'control': 'MONITORING', 'regulate': 'MONITORING',
    'work': 'OPERATION', 'operate': 'OPERATION', 'batch': 'OPERATION',
    'pound': 'OPERATION', 'strip': 'OPERATION', 'exact': 'OPERATION',
    'precise': 'OPERATION', 'hard': 'OPERATION', 'wide': 'OPERATION',
    'start': 'TRANSITION', 'open': 'TRANSITION', 'close': 'TRANSITION',
    'end': 'TRANSITION', 'finish': 'TRANSITION', 'complete': 'TRANSITION',
    'finalize': 'TRANSITION', 'yield': 'TRANSITION', 'final': 'TRANSITION',
    'stand': 'TRANSITION', 'settle': 'TRANSITION', 'set': 'TRANSITION',
    'halt': 'TRANSITION',  # Extension: n=halt was not in C1250 map
    'frame': 'STAGING', 'step': 'STAGING', 'iterate': 'STAGING',
    'sequence': 'STAGING', 'continue': 'STAGING', 'repeat': 'STAGING',
    'cycle': 'STAGING', 'loop': 'STAGING', 'path': 'STAGING',
    'mark': 'MARKING', 'flag': 'MARKING', 'note': 'MARKING',
    'pause': 'MARKING', 'diagram': 'MARKING', 'hazard': 'MARKING',
    'danger': 'MARKING', 'link': 'MARKING', 'adjust': 'MARKING',
}

ALL_CATEGORIES = sorted(set(GLOSS_TO_CATEGORY.values()))

# Atom -> category mapping (derived from atom glosses -> GLOSS_TO_CATEGORY)
ATOM_GLOSSES = {
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'halt', 'a': 'yield', 'm': 'final',
    'd': 'mark', 't': 'transfer', 'c': 'adjust', 'p': 'pause',
    'f': 'flag', 's': 'sequence', 'g': 'complete', 'o': 'work',
    'l': 'frame', 'r': 'input',
}
ATOM_TO_CATEGORY = {atom: GLOSS_TO_CATEGORY[gloss] for atom, gloss in ATOM_GLOSSES.items()}

# Confidence tiers for tie-breaking (higher = stronger)
CONFIDENCE_RANK = {'KERNEL': 5, 'LOCKED': 4, 'SOLID': 3, 'PLAUSIBLE': 2, 'WEAK': 1}
ATOM_CONFIDENCE = {
    'k': 'KERNEL', 'e': 'KERNEL', 'h': 'KERNEL',
    'y': 'LOCKED', 'i': 'LOCKED', 'n': 'LOCKED', 'a': 'LOCKED', 'm': 'LOCKED',
    'd': 'SOLID', 't': 'SOLID',
    'c': 'PLAUSIBLE', 'p': 'PLAUSIBLE', 'f': 'PLAUSIBLE', 's': 'PLAUSIBLE', 'g': 'PLAUSIBLE',
    'o': 'WEAK', 'l': 'WEAK', 'r': 'WEAK',
}

BEHAVIORAL_FEATURES = [
    'k_ratio', 'e_ratio', 'h_ratio', 'qo_affinity',
    'regime_1_enrichment', 'regime_2_enrichment',
    'regime_3_enrichment', 'regime_4_enrichment',
    'initial_rate', 'final_rate', 'folio_spread',
]


# ── Auto-assignment algorithm ─────────────────────────────────────────

def auto_assign_category(autogloss_atoms):
    """Assign a category to a dark MIDDLE via plurality vote over atoms.

    Returns (category, confidence, margin) or ('MIXED', min_conf, 0) on tie.
    """
    if not autogloss_atoms:
        return None, None, 0

    # Count votes per category
    votes = Counter()
    for atom in autogloss_atoms:
        cat = ATOM_TO_CATEGORY.get(atom)
        if cat:
            votes[cat] += 1

    if not votes:
        return None, None, 0

    # Find max vote count
    max_count = max(votes.values())
    winners = [c for c, v in votes.items() if v == max_count]

    # Min confidence across all atoms in the compound
    min_conf = min(
        CONFIDENCE_RANK.get(ATOM_CONFIDENCE.get(a, 'WEAK'), 1)
        for a in autogloss_atoms if a in ATOM_TO_CATEGORY
    )
    conf_label = {5: 'KERNEL', 4: 'LOCKED', 3: 'SOLID', 2: 'PLAUSIBLE', 1: 'WEAK'}[min_conf]

    if len(winners) == 1:
        margin = max_count - (sorted(votes.values(), reverse=True)[1] if len(votes) > 1 else 0)
        return winners[0], conf_label, margin

    # Tie-breaking: pick the category whose atoms have highest max confidence
    best_conf = -1
    best_cat = None
    for cat in winners:
        cat_atoms = [a for a in autogloss_atoms if ATOM_TO_CATEGORY.get(a) == cat]
        cat_max_conf = max(CONFIDENCE_RANK.get(ATOM_CONFIDENCE.get(a, 'WEAK'), 1) for a in cat_atoms)
        if cat_max_conf > best_conf:
            best_conf = cat_max_conf
            best_cat = cat

    if best_cat:
        return best_cat, conf_label, 0  # margin=0 indicates tie-break

    return 'MIXED', conf_label, 0


# ── Data loading ─────────────────────────────────────────────────────

def load_all_data():
    """Load tokens, dictionaries, and affordance data."""
    tx = Transcript()
    morph = Morphology()

    with open(ROOT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict_raw = json.load(f)
    mid_dict = mid_dict_raw['middles']

    with open(ROOT / 'data' / 'regime_folio_mapping.json', encoding='utf-8') as f:
        regime_raw = json.load(f)
    folio_regime = {fol: v['regime'] for fol, v in regime_raw['regime_assignments'].items()}

    with open(ROOT / 'data' / 'middle_affordance_table.json', encoding='utf-8') as f:
        affordance_raw = json.load(f)
    affordance_middles = {k: v for k, v in affordance_raw.get('middles', affordance_raw).items()
                          if not k.startswith('_')}

    with open(ROOT / 'phases' / 'APPARATUS_VOCABULARY_CLASSIFICATION'
              / 'results' / 'apparatus_profiles.json', encoding='utf-8') as f:
        apparatus_raw = json.load(f)

    # Build human-glossed MIDDLE -> category map
    human_mid_to_cat = {}
    for mid, minfo in mid_dict.items():
        gloss = minfo.get('gloss')
        if gloss and gloss in GLOSS_TO_CATEGORY:
            human_mid_to_cat[mid] = GLOSS_TO_CATEGORY[gloss]

    # Build auto-assigned dark MIDDLE -> category map
    dark_mid_to_cat = {}
    dark_mid_confidence = {}
    dark_mid_margin = {}
    q_middles = set()
    mixed_middles = set()

    for mid, minfo in mid_dict.items():
        if mid in human_mid_to_cat:
            continue  # Already human-glossed
        autogloss = minfo.get('autogloss')
        atoms_str = minfo.get('autogloss_atoms', '')
        if autogloss and atoms_str:
            atoms = list(atoms_str)
            cat, conf, margin = auto_assign_category(atoms)
            if cat and cat != 'MIXED':
                dark_mid_to_cat[mid] = cat
                dark_mid_confidence[mid] = conf
                dark_mid_margin[mid] = margin
            elif cat == 'MIXED':
                mixed_middles.add(mid)
        elif not autogloss:
            # Check if it contains q (unautoglossable)
            if 'q' in mid:
                q_middles.add(mid)
            # else: no autogloss and no q -- rare edge case

    # Build token list
    line_counts = Counter()
    raw_tokens = []
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        raw_tokens.append(token)
        line_counts[(token.folio, token.line)] += 1

    line_pos_idx = defaultdict(int)
    tokens = []
    for token in raw_tokens:
        w = token.word.strip()
        key = (token.folio, token.line)
        idx = line_pos_idx[key]
        line_pos_idx[key] += 1
        total = line_counts[key]
        line_pos = idx / (total - 1) if total > 1 else 0.5

        m = morph.extract(w)
        mid = m.middle

        # Determine category source
        if mid and mid in human_mid_to_cat:
            cat = human_mid_to_cat[mid]
            cat_source = 'human'
        elif mid and mid in dark_mid_to_cat:
            cat = dark_mid_to_cat[mid]
            cat_source = 'auto'
        else:
            cat = None
            cat_source = 'none'

        tokens.append({
            'word': w,
            'folio': token.folio,
            'line': token.line,
            'section': token.section,
            'line_pos': line_pos,
            'middle': mid,
            'prefix': m.prefix,
            'suffix': m.suffix,
            'gloss_category': cat,
            'cat_source': cat_source,
            'regime': folio_regime.get(token.folio, 'UNK'),
        })

    return (tokens, human_mid_to_cat, dark_mid_to_cat, dark_mid_confidence,
            dark_mid_margin, q_middles, mixed_middles, affordance_middles, mid_dict)


# ── Utility functions ────────────────────────────────────────────────

def jsd(p, q):
    """Jensen-Shannon divergence between two probability vectors."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    p = p / (p.sum() + 1e-30)
    q = q / (q.sum() + 1e-30)
    return float(jensenshannon(p, q) ** 2)  # squared JSD


def silhouette_score(features, labels):
    """Compute silhouette score for given feature matrix and labels."""
    from scipy.spatial.distance import cdist
    unique_labels = sorted(set(labels))
    if len(unique_labels) < 2:
        return 0.0

    n = len(labels)
    label_arr = np.array(labels)

    # Compute pairwise distances
    dists = cdist(features, features, metric='euclidean')

    sil_scores = []
    for i in range(n):
        my_label = label_arr[i]
        same_mask = (label_arr == my_label)
        same_mask[i] = False

        if same_mask.sum() == 0:
            sil_scores.append(0.0)
            continue

        a_i = dists[i][same_mask].mean()

        b_i = np.inf
        for other_label in unique_labels:
            if other_label == my_label:
                continue
            other_mask = (label_arr == other_label)
            if other_mask.sum() == 0:
                continue
            b_candidate = dists[i][other_mask].mean()
            b_i = min(b_i, b_candidate)

        if b_i == np.inf:
            sil_scores.append(0.0)
            continue

        s_i = (b_i - a_i) / max(a_i, b_i, 1e-30)
        sil_scores.append(s_i)

    return float(np.mean(sil_scores))


def compute_mi(cat_pairs):
    """Compute mutual information from list of (cat_a, cat_b) pairs."""
    if not cat_pairs:
        return 0.0
    pair_counts = Counter(cat_pairs)
    total = len(cat_pairs)
    cats_a = Counter(a for a, _ in cat_pairs)
    cats_b = Counter(b for _, b in cat_pairs)

    mi = 0.0
    for (a, b), count in pair_counts.items():
        p_ab = count / total
        p_a = cats_a[a] / total
        p_b = cats_b[b] / total
        if p_ab > 0 and p_a > 0 and p_b > 0:
            mi += p_ab * np.log2(p_ab / (p_a * p_b))
    return float(mi)


# ── T1: Auto-Assignment Coverage ─────────────────────────────────────

def test_t1_coverage(dark_mid_to_cat, dark_mid_confidence, dark_mid_margin,
                     q_middles, mixed_middles, tokens, human_mid_to_cat):
    """T1: Descriptive -- coverage and distribution of auto-assignment."""
    print("\n[2/7] T1: Auto-Assignment Coverage and Distribution...")

    # Category distribution for dark auto-assigned
    dark_cat_counts = Counter(dark_mid_to_cat.values())
    # Confidence distribution
    conf_counts = Counter(dark_mid_confidence.values())

    # Token-level coverage
    n_human = sum(1 for t in tokens if t['cat_source'] == 'human')
    n_auto = sum(1 for t in tokens if t['cat_source'] == 'auto')
    n_none = sum(1 for t in tokens if t['cat_source'] == 'none')
    n_total = len(tokens)

    # Dark token category distribution
    dark_token_cats = Counter(t['gloss_category'] for t in tokens if t['cat_source'] == 'auto')

    # Human category distribution (for comparison)
    human_token_cats = Counter(t['gloss_category'] for t in tokens if t['cat_source'] == 'human')

    n_dark_middles_total = len(dark_mid_to_cat) + len(mixed_middles) + len(q_middles)
    # Count other unglossed (no autogloss, no q)
    all_mids = set(t['middle'] for t in tokens if t['middle'])
    other_unglossed = all_mids - set(human_mid_to_cat.keys()) - set(dark_mid_to_cat.keys()) - mixed_middles - q_middles
    n_dark_middles_total += len(other_unglossed)

    coverage_rate = len(dark_mid_to_cat) / max(n_dark_middles_total, 1)
    total_coverage = (n_human + n_auto) / max(n_total, 1)

    status = 'PASS' if coverage_rate >= 0.80 else 'FAIL'
    print(f"  Auto-assigned: {len(dark_mid_to_cat)} MIDDLEs -> {n_auto} tokens")
    print(f"  MIXED (tied): {len(mixed_middles)}")
    print(f"  Q-unglossable: {len(q_middles)}")
    print(f"  Other unglossed: {len(other_unglossed)}")
    print(f"  Coverage: {coverage_rate:.1%} of dark MIDDLEs assigned")
    print(f"  Total token coverage: {total_coverage:.1%} ({n_human}+{n_auto}/{n_total})")
    print(f"  -> {status}")

    return {
        'status': status,
        'n_dark_assigned': len(dark_mid_to_cat),
        'n_mixed': len(mixed_middles),
        'n_q_unglossable': len(q_middles),
        'n_other_unglossed': len(other_unglossed),
        'coverage_rate_middles': round(coverage_rate, 4),
        'total_token_coverage': round(total_coverage, 4),
        'n_human_tokens': n_human,
        'n_auto_tokens': n_auto,
        'n_uncovered_tokens': n_none,
        'dark_category_dist_middles': {c: dark_cat_counts.get(c, 0) for c in ALL_CATEGORIES},
        'dark_category_dist_tokens': {c: dark_token_cats.get(c, 0) for c in ALL_CATEGORIES},
        'human_category_dist_tokens': {c: human_token_cats.get(c, 0) for c in ALL_CATEGORIES},
        'confidence_distribution': dict(conf_counts),
    }


# ── T2: Behavioral Silhouette ────────────────────────────────────────

def test_t2_silhouette(dark_mid_to_cat, dark_mid_confidence, affordance_middles):
    """T2: Behavioral silhouette of auto-assigned categories vs random partition."""
    print("\n[3/7] T2: Behavioral Silhouette Validation...")

    # Build feature matrix for dark MIDDLEs with affordance data
    middles_with_data = []
    features = []
    labels = []
    confidences = []

    for mid, cat in dark_mid_to_cat.items():
        if mid in affordance_middles:
            bs = affordance_middles[mid].get('behavioral_signature', {})
            feat = [bs.get(f, 0.0) for f in BEHAVIORAL_FEATURES]
            if any(np.isnan(feat)):
                continue
            middles_with_data.append(mid)
            features.append(feat)
            labels.append(cat)
            confidences.append(dark_mid_confidence.get(mid, 'WEAK'))

    if len(middles_with_data) < 20:
        print(f"  Only {len(middles_with_data)} dark MIDDLEs with affordance data -- SKIP")
        return {'status': 'SKIP', 'reason': 'insufficient data', 'n_middles': len(middles_with_data)}

    features = np.array(features)
    # Standardize
    mu = features.mean(axis=0)
    sd = features.std(axis=0)
    sd[sd == 0] = 1.0
    features_std = (features - mu) / sd

    # Observed silhouette
    obs_sil = silhouette_score(features_std, labels)

    # Null A: random partition
    rng = np.random.default_rng(42)
    null_sils = []
    label_sizes = Counter(labels)
    for _ in range(N_PERM):
        shuffled = list(labels)
        rng.shuffle(shuffled)
        null_sils.append(silhouette_score(features_std, shuffled))

    p_val = (np.sum(np.array(null_sils) >= obs_sil) + 1) / (N_PERM + 1)

    # Stratified analysis
    strat_results = {}
    for tier_name, tier_set in [('LOCKED_SOLID', {'KERNEL', 'LOCKED', 'SOLID'}),
                                 ('PLAUSIBLE', {'PLAUSIBLE'}),
                                 ('WEAK', {'WEAK'})]:
        tier_idx = [i for i, c in enumerate(confidences) if c in tier_set]
        if len(tier_idx) < 10:
            strat_results[tier_name] = {'n': len(tier_idx), 'status': 'INSUFFICIENT'}
            continue
        tier_feats = features_std[tier_idx]
        tier_labels = [labels[i] for i in tier_idx]
        if len(set(tier_labels)) < 2:
            strat_results[tier_name] = {'n': len(tier_idx), 'status': 'SINGLE_CATEGORY'}
            continue
        tier_sil = silhouette_score(tier_feats, tier_labels)
        # Null for this tier
        tier_null_sils = []
        for _ in range(N_PERM):
            sh = list(tier_labels)
            rng.shuffle(sh)
            tier_null_sils.append(silhouette_score(tier_feats, sh))
        tier_p = (np.sum(np.array(tier_null_sils) >= tier_sil) + 1) / (N_PERM + 1)
        strat_results[tier_name] = {
            'n': len(tier_idx),
            'silhouette': round(tier_sil, 4),
            'p_value': round(tier_p, 4),
            'null_mean': round(np.mean(tier_null_sils), 4),
            'status': 'PASS' if tier_p < P_THRESHOLD else 'FAIL',
        }

    status = 'PASS' if p_val < P_THRESHOLD else 'FAIL'
    print(f"  {len(middles_with_data)} dark MIDDLEs with affordance data")
    print(f"  Silhouette: {obs_sil:.4f} (null mean: {np.mean(null_sils):.4f})")
    print(f"  -> {status} (p={p_val:.4f})")
    for tier, res in strat_results.items():
        if 'silhouette' in res:
            print(f"    {tier}: sil={res['silhouette']:.4f}, p={res['p_value']:.4f}, n={res['n']}")

    return {
        'status': status,
        'silhouette': round(obs_sil, 4),
        'p_value_empirical': round(p_val, 4),
        'null_mean': round(float(np.mean(null_sils)), 4),
        'n_middles': len(middles_with_data),
        'n_categories': len(set(labels)),
        'stratified': strat_results,
    }


# ── T3: Line-Position Differentiation ────────────────────────────────

def test_t3_line_position(tokens):
    """T3: Does auto-category labeling differentiate line position?"""
    print("\n[4/7] T3: Line-Position Differentiation...")

    dark_tokens = [t for t in tokens if t['cat_source'] == 'auto' and t['gloss_category']]
    if len(dark_tokens) < 50:
        print(f"  Only {len(dark_tokens)} dark tokens -- SKIP")
        return {'status': 'SKIP', 'n_tokens': len(dark_tokens)}

    # Group by category
    cat_positions = defaultdict(list)
    for t in dark_tokens:
        cat_positions[t['gloss_category']].append(t['line_pos'])

    # Only keep categories with >= 5 tokens
    valid_cats = {c: pos for c, pos in cat_positions.items() if len(pos) >= 5}
    if len(valid_cats) < 2:
        print(f"  Only {len(valid_cats)} categories with >=5 tokens -- SKIP")
        return {'status': 'SKIP', 'n_valid_categories': len(valid_cats)}

    # ANOVA F
    groups = [np.array(valid_cats[c]) for c in sorted(valid_cats.keys())]
    obs_f, obs_p = sp_stats.f_oneway(*groups)

    # Null B: random token labels from marginal
    rng = np.random.default_rng(42)
    all_positions = np.array([t['line_pos'] for t in dark_tokens])
    cat_list = [t['gloss_category'] for t in dark_tokens]
    cat_marginal = Counter(cat_list)
    cat_names = sorted(cat_marginal.keys())
    cat_probs = np.array([cat_marginal[c] for c in cat_names], dtype=float)
    cat_probs /= cat_probs.sum()

    null_fs = []
    for _ in range(N_PERM):
        shuffled_cats = rng.choice(cat_names, size=len(dark_tokens), p=cat_probs)
        shuf_groups = defaultdict(list)
        for pos, c in zip(all_positions, shuffled_cats):
            shuf_groups[c].append(pos)
        shuf_valid = [np.array(shuf_groups[c]) for c in sorted(shuf_groups.keys()) if len(shuf_groups[c]) >= 5]
        if len(shuf_valid) >= 2:
            f_val, _ = sp_stats.f_oneway(*shuf_valid)
            null_fs.append(f_val)
        else:
            null_fs.append(0.0)

    p_val = (np.sum(np.array(null_fs) >= obs_f) + 1) / (N_PERM + 1)
    ratio = obs_f / max(np.mean(null_fs), 1e-10)

    # Category mean positions
    cat_means = {c: round(np.mean(pos), 4) for c, pos in sorted(valid_cats.items())}

    status = 'PASS' if p_val < P_THRESHOLD else 'FAIL'
    print(f"  {len(dark_tokens)} dark tokens, {len(valid_cats)} categories")
    print(f"  F={obs_f:.1f}, ratio={ratio:.1f}x, p={p_val:.4f}")
    print(f"  -> {status}")

    return {
        'status': status,
        'F': round(obs_f, 2),
        'ratio_over_null': round(ratio, 1),
        'p_value_empirical': round(p_val, 4),
        'null_F_mean': round(float(np.mean(null_fs)), 2),
        'n_tokens': len(dark_tokens),
        'n_categories': len(valid_cats),
        'category_mean_positions': cat_means,
    }


# ── T4: Section Profile Divergence ───────────────────────────────────

def test_t4_section_divergence(tokens, dark_mid_to_cat):
    """T4: Do auto-assigned categories concentrate in different sections?"""
    print("\n[5/7] T4: Section Profile Divergence...")

    dark_tokens = [t for t in tokens if t['cat_source'] == 'auto' and t['gloss_category']]
    sections = sorted(set(t['section'] for t in dark_tokens))

    # Per-category section profile
    cat_section_counts = defaultdict(lambda: Counter())
    for t in dark_tokens:
        cat_section_counts[t['gloss_category']][t['section']] += 1

    valid_cats = {c: counts for c, counts in cat_section_counts.items()
                  if sum(counts.values()) >= 5}

    if len(valid_cats) < 2:
        print(f"  Only {len(valid_cats)} categories -- SKIP")
        return {'status': 'SKIP'}

    # Build profiles
    def build_profile(counts, sections):
        total = sum(counts.values())
        return np.array([counts.get(s, 0) / max(total, 1) for s in sections])

    cat_profiles = {c: build_profile(counts, sections) for c, counts in valid_cats.items()}

    # Mean pairwise JSD
    cats_sorted = sorted(cat_profiles.keys())
    jsds = []
    for i in range(len(cats_sorted)):
        for j in range(i + 1, len(cats_sorted)):
            jsds.append(jsd(cat_profiles[cats_sorted[i]], cat_profiles[cats_sorted[j]]))
    obs_jsd = np.mean(jsds)

    # Null A: random partition of dark MIDDLEs into same-size groups
    rng = np.random.default_rng(42)
    dark_middles_list = sorted(dark_mid_to_cat.keys())
    dark_cats_list = [dark_mid_to_cat[m] for m in dark_middles_list]

    # Pre-compute per-MIDDLE section token counts
    mid_section_counts = defaultdict(lambda: Counter())
    for t in dark_tokens:
        if t['middle']:
            mid_section_counts[t['middle']][t['section']] += 1

    null_jsds = []
    for _ in range(N_PERM):
        shuffled_cats = list(dark_cats_list)
        rng.shuffle(shuffled_cats)
        shuf_mid_to_cat = dict(zip(dark_middles_list, shuffled_cats))

        shuf_cat_section = defaultdict(lambda: Counter())
        for mid, cat in shuf_mid_to_cat.items():
            for sec, count in mid_section_counts[mid].items():
                shuf_cat_section[cat][sec] += count

        shuf_profiles = {}
        for c, counts in shuf_cat_section.items():
            if sum(counts.values()) >= 5:
                shuf_profiles[c] = build_profile(counts, sections)

        if len(shuf_profiles) >= 2:
            shuf_cats_sorted = sorted(shuf_profiles.keys())
            shuf_jsds = []
            for i in range(len(shuf_cats_sorted)):
                for j in range(i + 1, len(shuf_cats_sorted)):
                    shuf_jsds.append(jsd(shuf_profiles[shuf_cats_sorted[i]],
                                         shuf_profiles[shuf_cats_sorted[j]]))
            null_jsds.append(np.mean(shuf_jsds))
        else:
            null_jsds.append(0.0)

    p_val = (np.sum(np.array(null_jsds) >= obs_jsd) + 1) / (N_PERM + 1)

    status = 'PASS' if p_val < P_THRESHOLD else 'FAIL'
    print(f"  Mean pairwise JSD: {obs_jsd:.4f} (null mean: {np.mean(null_jsds):.4f})")
    print(f"  -> {status} (p={p_val:.4f})")

    return {
        'status': status,
        'mean_pairwise_jsd': round(obs_jsd, 4),
        'p_value_empirical': round(p_val, 4),
        'null_jsd_mean': round(float(np.mean(null_jsds)), 4),
        'n_categories': len(valid_cats),
        'category_profiles': {c: {s: round(float(p), 4) for s, p in zip(sections, prof)}
                              for c, prof in cat_profiles.items()},
    }


# ── T5: Within-Line MI ──────────────────────────────────────────────

def test_t5_within_line_mi(tokens):
    """T5: Does auto-assigned dark category carry sequential information?"""
    print("\n[6/7] T5: Within-Line MI...")

    # Group tokens by line
    lines = defaultdict(list)
    for t in tokens:
        lines[(t['folio'], t['line'])].append(t)

    # Build adjacent pairs where at least one token is dark-auto
    all_pairs = []
    dark_pairs = []  # both members have categories, at least one is auto
    for key in sorted(lines.keys()):
        line_toks = lines[key]
        for i in range(len(line_toks) - 1):
            a = line_toks[i]
            b = line_toks[i + 1]
            cat_a = a['gloss_category']
            cat_b = b['gloss_category']
            if cat_a and cat_b:
                all_pairs.append((cat_a, cat_b))
                if a['cat_source'] == 'auto' or b['cat_source'] == 'auto':
                    dark_pairs.append((cat_a, cat_b, a['cat_source'], b['cat_source']))

    if len(dark_pairs) < 50:
        print(f"  Only {len(dark_pairs)} dark-involved pairs -- SKIP")
        return {'status': 'SKIP', 'n_pairs': len(dark_pairs)}

    # MI for all pairs (human + auto)
    obs_mi_all = compute_mi(all_pairs)

    # MI for dark-involved pairs only
    dark_cat_pairs = [(a, b) for a, b, _, _ in dark_pairs]
    obs_mi_dark = compute_mi(dark_cat_pairs)

    # Null B: randomize dark token categories only, preserve human
    rng = np.random.default_rng(42)

    # Identify which tokens are dark-auto for shuffling
    dark_auto_cats = [t['gloss_category'] for t in tokens if t['cat_source'] == 'auto' and t['gloss_category']]
    dark_cat_marginal = Counter(dark_auto_cats)
    dark_cat_names = sorted(dark_cat_marginal.keys())
    dark_probs = np.array([dark_cat_marginal[c] for c in dark_cat_names], dtype=float)
    dark_probs /= dark_probs.sum()

    null_mis = []
    for perm_i in range(N_PERM):
        # Re-assign dark token categories from marginal
        shuffled_dark = rng.choice(dark_cat_names, size=len(dark_auto_cats), p=dark_probs)
        dark_idx = 0

        # Rebuild pairs
        perm_pairs = []
        for key in sorted(lines.keys()):
            line_toks = lines[key]
            line_cats = []
            for t in line_toks:
                if t['cat_source'] == 'auto' and t['gloss_category']:
                    line_cats.append(shuffled_dark[dark_idx])
                    dark_idx += 1
                else:
                    line_cats.append(t['gloss_category'])

            for i in range(len(line_cats) - 1):
                if line_cats[i] and line_cats[i + 1]:
                    src_a = line_toks[i]['cat_source']
                    src_b = line_toks[i + 1]['cat_source']
                    if src_a == 'auto' or src_b == 'auto':
                        perm_pairs.append((line_cats[i], line_cats[i + 1]))

        null_mis.append(compute_mi(perm_pairs))

    p_val = (np.sum(np.array(null_mis) >= obs_mi_dark) + 1) / (N_PERM + 1)
    ratio = obs_mi_dark / max(np.mean(null_mis), 1e-10)

    # Diagnostic: MI between human-adjacent-to-dark
    human_dark_pairs = [(a, b) for a, b, sa, sb in dark_pairs if sa != sb]
    mi_cross = compute_mi(human_dark_pairs) if len(human_dark_pairs) > 20 else None

    status = 'PASS' if p_val < P_THRESHOLD else 'FAIL'
    print(f"  {len(dark_pairs)} dark-involved pairs")
    print(f"  MI (dark-involved): {obs_mi_dark:.4f} (null mean: {np.mean(null_mis):.4f})")
    print(f"  MI (all pairs): {obs_mi_all:.4f}")
    if mi_cross is not None:
        print(f"  MI (human<->dark cross): {mi_cross:.4f}")
    print(f"  -> {status} (ratio={ratio:.1f}x, p={p_val:.4f})")

    result = {
        'status': status,
        'mi_dark_involved': round(obs_mi_dark, 4),
        'mi_all_pairs': round(obs_mi_all, 4),
        'p_value_empirical': round(p_val, 4),
        'ratio': round(ratio, 1),
        'null_mi_mean': round(float(np.mean(null_mis)), 4),
        'n_dark_pairs': len(dark_pairs),
        'n_all_pairs': len(all_pairs),
    }
    if mi_cross is not None:
        result['mi_human_dark_cross'] = round(mi_cross, 4)
        result['n_cross_pairs'] = len(human_dark_pairs)
    return result


# ── T6: Q-MIDDLE Structural Characterization ─────────────────────────

def test_t6_q_middles(tokens, q_middles, mixed_middles, dark_mid_to_cat,
                       affordance_middles, mid_dict):
    """T6: Q-MIDDLE structural characterization and 9th category test."""
    print("\n[7/7] T6: Q-MIDDLE Structural Characterization...")

    # Partition dark tokens
    auto_tokens = [t for t in tokens if t['cat_source'] == 'auto']
    q_tokens = [t for t in tokens if t['middle'] and t['middle'] in q_middles]
    none_tokens = [t for t in tokens if t['cat_source'] == 'none' and t['middle']
                   and t['middle'] not in q_middles]

    sections = sorted(set(t['section'] for t in tokens))

    def group_stats(tok_list, label):
        if not tok_list:
            return {'n_tokens': 0, 'n_middles': 0, 'label': label}
        section_counts = Counter(t['section'] for t in tok_list)
        total = len(tok_list)
        section_profile = {s: round(section_counts.get(s, 0) / total, 4) for s in sections}
        positions = [t['line_pos'] for t in tok_list]
        suffix_rate = sum(1 for t in tok_list if t['suffix']) / total
        middles_used = set(t['middle'] for t in tok_list if t['middle'])
        folio_counts = Counter(t['folio'] for t in tok_list)
        return {
            'label': label,
            'n_tokens': total,
            'n_middles': len(middles_used),
            'section_profile': section_profile,
            'mean_line_pos': round(np.mean(positions), 4),
            'std_line_pos': round(np.std(positions), 4),
            'suffix_rate': round(suffix_rate, 4),
            'mean_tokens_per_middle': round(total / max(len(middles_used), 1), 2),
            'n_folios': len(folio_counts),
        }

    auto_stats = group_stats(auto_tokens, 'auto_assigned')
    q_stats = group_stats(q_tokens, 'q_unglossable')
    other_stats = group_stats(none_tokens, 'other_unglossed')

    # Divergence test: q-MIDDLEs vs auto-assigned section profile
    if q_stats['n_tokens'] >= 10 and auto_stats['n_tokens'] >= 10:
        q_prof = np.array([q_stats['section_profile'].get(s, 0) for s in sections])
        auto_prof = np.array([auto_stats['section_profile'].get(s, 0) for s in sections])
        section_jsd = jsd(q_prof, auto_prof)

        # Mann-Whitney on line position
        q_positions = [t['line_pos'] for t in q_tokens]
        auto_positions = [t['line_pos'] for t in auto_tokens]
        u_stat, mw_p = sp_stats.mannwhitneyu(q_positions, auto_positions, alternative='two-sided')

        divergence = {
            'section_jsd': round(section_jsd, 4),
            'line_pos_U': round(float(u_stat), 1),
            'line_pos_p': round(float(mw_p), 4),
            'q_mean_pos': round(np.mean(q_positions), 4),
            'auto_mean_pos': round(np.mean(auto_positions), 4),
        }
    else:
        divergence = {'note': 'insufficient q tokens for divergence test'}

    # 9th category test: cluster residual MIDDLEs (q + mixed) in behavioral space
    residual_middles = q_middles | mixed_middles
    residual_features = []
    residual_labels = []
    for mid in residual_middles:
        if mid in affordance_middles:
            bs = affordance_middles[mid].get('behavioral_signature', {})
            feat = [bs.get(f, 0.0) for f in BEHAVIORAL_FEATURES]
            if not any(np.isnan(feat)):
                residual_features.append(feat)
                residual_labels.append(mid)

    ninth_category = {'n_middles_with_data': len(residual_features)}
    if len(residual_features) >= 10:
        from sklearn.cluster import KMeans
        features_arr = np.array(residual_features)
        mu = features_arr.mean(axis=0)
        sd = features_arr.std(axis=0)
        sd[sd == 0] = 1.0
        features_std = (features_arr - mu) / sd

        sils = {}
        for k in [2, 3]:
            if len(residual_features) >= k + 1:
                km = KMeans(n_clusters=k, n_init=10, random_state=42)
                km.fit(features_std)
                sil = silhouette_score(features_std, km.labels_.tolist())
                sils[str(k)] = round(sil, 4)

        ninth_category['silhouettes'] = sils
        ninth_category['verdict'] = 'NO_9TH_CATEGORY'  # default
        if sils:
            best_k = max(sils, key=sils.get)
            if sils[best_k] > 0.25:
                ninth_category['verdict'] = f'POSSIBLE_CLUSTERS_K{best_k}'
    else:
        ninth_category['verdict'] = 'INSUFFICIENT_DATA'

    # Overall status: divergence significant?
    if 'line_pos_p' in divergence:
        div_status = 'PASS' if divergence['line_pos_p'] < P_THRESHOLD else 'FAIL'
    else:
        div_status = 'SKIP'

    print(f"  Auto-assigned: {auto_stats['n_tokens']} tokens ({auto_stats['n_middles']} MIDDLEs)")
    print(f"  Q-unglossable: {q_stats['n_tokens']} tokens ({q_stats['n_middles']} MIDDLEs)")
    print(f"  Other: {other_stats['n_tokens']} tokens ({other_stats['n_middles']} MIDDLEs)")
    if 'section_jsd' in divergence:
        print(f"  Q vs auto section JSD: {divergence['section_jsd']:.4f}")
        print(f"  Q vs auto line position MW p={divergence.get('line_pos_p', 'N/A')}")
    print(f"  9th category: {ninth_category['verdict']}")
    print(f"  -> divergence {div_status}")

    return {
        'status': div_status,
        'auto_stats': auto_stats,
        'q_stats': q_stats,
        'other_stats': other_stats,
        'divergence': divergence,
        'ninth_category': ninth_category,
    }


# ── Synthesis ─────────────────────────────────────────────────────────

def synthesize(results):
    """Compute overall verdict from test results."""
    statuses = []
    for key, val in results.items():
        if isinstance(val, dict) and 'status' in val:
            statuses.append(val['status'])

    pass_count = sum(1 for s in statuses if s == 'PASS')
    fail_count = sum(1 for s in statuses if s == 'FAIL')
    skip_count = sum(1 for s in statuses if s == 'SKIP')

    if pass_count >= 5:
        verdict = 'GENERALIZES'
    elif pass_count >= 3:
        verdict = 'PARTIALLY_GENERALIZES'
    else:
        verdict = 'DOES_NOT_GENERALIZE'

    return {
        'pass_count': pass_count,
        'fail_count': fail_count,
        'skip_count': skip_count,
        'total_tests': len(statuses),
        'tests_run': len(statuses) - skip_count,
        'verdict': verdict,
        'summary': f"{pass_count}/{len(statuses)} tests pass (p<{P_THRESHOLD}), {skip_count} skipped",
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("DARK PIPELINE CHARACTERIZATION")
    print("Testing whether 8 gloss categories generalize to dark MIDDLEs")
    print("=" * 60)

    t0 = time.time()

    print("\n[1/7] Loading data...")
    (tokens, human_mid_to_cat, dark_mid_to_cat, dark_mid_confidence,
     dark_mid_margin, q_middles, mixed_middles, affordance_middles, mid_dict) = load_all_data()

    n_total = len(tokens)
    n_human = sum(1 for t in tokens if t['cat_source'] == 'human')
    n_auto = sum(1 for t in tokens if t['cat_source'] == 'auto')
    n_none = sum(1 for t in tokens if t['cat_source'] == 'none')
    print(f"  {n_total} B tokens: {n_human} human-glossed, {n_auto} auto-assigned, {n_none} uncovered")
    print(f"  {len(dark_mid_to_cat)} dark MIDDLEs auto-assigned, {len(mixed_middles)} MIXED, {len(q_middles)} q-unglossable")

    results = {}
    results['T1_coverage'] = test_t1_coverage(
        dark_mid_to_cat, dark_mid_confidence, dark_mid_margin,
        q_middles, mixed_middles, tokens, human_mid_to_cat)
    results['T2_silhouette'] = test_t2_silhouette(
        dark_mid_to_cat, dark_mid_confidence, affordance_middles)
    results['T3_line_position'] = test_t3_line_position(tokens)
    results['T4_section_divergence'] = test_t4_section_divergence(tokens, dark_mid_to_cat)
    results['T5_within_line_mi'] = test_t5_within_line_mi(tokens)
    results['T6_q_middles'] = test_t6_q_middles(
        tokens, q_middles, mixed_middles, dark_mid_to_cat,
        affordance_middles, mid_dict)

    elapsed = time.time() - t0
    synthesis = synthesize(results)

    output = {
        '_metadata': {
            'phase': 'DARK_PIPELINE_CHARACTERIZATION',
            'phase_number': 448,
            'description': 'Testing 8-category generalization to dark pipeline MIDDLEs',
            'n_tokens': n_total,
            'n_human_glossed_middles': len(human_mid_to_cat),
            'n_dark_auto_assigned': len(dark_mid_to_cat),
            'n_mixed': len(mixed_middles),
            'n_q_unglossable': len(q_middles),
            'n_permutations': N_PERM,
            'p_threshold': P_THRESHOLD,
            'elapsed_seconds': round(elapsed, 1),
        },
        'synthesis': synthesis,
        'tests': results,
    }

    out_path = RESULTS_DIR / "dark_pipeline_characterization.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 60}")
    print(f"VERDICT: {synthesis['verdict']}")
    print(f"  {synthesis['summary']}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"  Results: {out_path}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
