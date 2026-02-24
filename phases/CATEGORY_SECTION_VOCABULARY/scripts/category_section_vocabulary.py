"""
Phase 449: CATEGORY_SECTION_VOCABULARY
Tests whether sections use different specific MIDDLEs within the same
operational categories.

C1134 showed sections modulate FREQUENCIES of shared vocabulary (JS=0.124).
C1148 showed the dark pipeline achieves 3.9x SELECTION hyper-modulation.
This phase tests whether that selection is category-structured: do sections
select different MIDDLEs *within the same operational category*?

Uses full coverage (human + dark auto-assigned, 99.5% of B tokens per C1254).

5-test battery:
  T1: Within-category Jaccard divergence   (Null: permute section labels)
  T2: Section-enriched MIDDLEs per category (Null: hypergeometric)
  T3: Section classification from category  (Null: shuffled folio-section)
  T4: Category-conditioned vs raw JS        (partitioning effect)
  T5: Confidence tier stratification        (LOCKED/SOLID vs WEAK)
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

RESULTS_DIR = ROOT / "phases" / "CATEGORY_SECTION_VOCABULARY" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
P_THRESHOLD = 0.01
# Use 4 major sections with enough tokens for stable Jaccard
MIN_SECTION_TOKENS = 500

# ── Category mapping (from Phase 446/448) ─────────────────────────────
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
    'halt': 'TRANSITION',
    'frame': 'STAGING', 'step': 'STAGING', 'iterate': 'STAGING',
    'sequence': 'STAGING', 'continue': 'STAGING', 'repeat': 'STAGING',
    'cycle': 'STAGING', 'loop': 'STAGING', 'path': 'STAGING',
    'mark': 'MARKING', 'flag': 'MARKING', 'note': 'MARKING',
    'pause': 'MARKING', 'diagram': 'MARKING', 'hazard': 'MARKING',
    'danger': 'MARKING', 'link': 'MARKING', 'adjust': 'MARKING',
}

ALL_CATEGORIES = sorted(set(GLOSS_TO_CATEGORY.values()))

ATOM_GLOSSES = {
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'halt', 'a': 'yield', 'm': 'final',
    'd': 'mark', 't': 'transfer', 'c': 'adjust', 'p': 'pause',
    'f': 'flag', 's': 'sequence', 'g': 'complete', 'o': 'work',
    'l': 'frame', 'r': 'input',
}
ATOM_TO_CATEGORY = {atom: GLOSS_TO_CATEGORY[gloss] for atom, gloss in ATOM_GLOSSES.items()}

CONFIDENCE_RANK = {'KERNEL': 5, 'LOCKED': 4, 'SOLID': 3, 'PLAUSIBLE': 2, 'WEAK': 1}
ATOM_CONFIDENCE = {
    'k': 'KERNEL', 'e': 'KERNEL', 'h': 'KERNEL',
    'y': 'LOCKED', 'i': 'LOCKED', 'n': 'LOCKED', 'a': 'LOCKED', 'm': 'LOCKED',
    'd': 'SOLID', 't': 'SOLID',
    'c': 'PLAUSIBLE', 'p': 'PLAUSIBLE', 'f': 'PLAUSIBLE', 's': 'PLAUSIBLE', 'g': 'PLAUSIBLE',
    'o': 'WEAK', 'l': 'WEAK', 'r': 'WEAK',
}


# ── Auto-assignment (reused from Phase 448) ───────────────────────────

def auto_assign_category(autogloss_atoms):
    """Assign category via plurality vote over atoms."""
    if not autogloss_atoms:
        return None, None
    votes = Counter()
    for atom in autogloss_atoms:
        cat = ATOM_TO_CATEGORY.get(atom)
        if cat:
            votes[cat] += 1
    if not votes:
        return None, None
    max_count = max(votes.values())
    winners = [c for c, v in votes.items() if v == max_count]
    min_conf = min(
        CONFIDENCE_RANK.get(ATOM_CONFIDENCE.get(a, 'WEAK'), 1)
        for a in autogloss_atoms if a in ATOM_TO_CATEGORY
    )
    conf_label = {5: 'KERNEL', 4: 'LOCKED', 3: 'SOLID', 2: 'PLAUSIBLE', 1: 'WEAK'}[min_conf]
    if len(winners) == 1:
        return winners[0], conf_label
    # Tie-break by atom confidence
    best_conf, best_cat = -1, None
    for cat in winners:
        cat_atoms = [a for a in autogloss_atoms if ATOM_TO_CATEGORY.get(a) == cat]
        cat_max = max(CONFIDENCE_RANK.get(ATOM_CONFIDENCE.get(a, 'WEAK'), 1) for a in cat_atoms)
        if cat_max > best_conf:
            best_conf, best_cat = cat_max, cat
    return best_cat or 'MIXED', conf_label


# ── Data loading ──────────────────────────────────────────────────────

def load_all_data():
    """Load tokens with human + dark auto-assigned categories."""
    tx = Transcript()
    morph = Morphology()

    with open(ROOT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict = json.load(f)['middles']

    # Build human-glossed map
    human_mid_to_cat = {}
    for mid, minfo in mid_dict.items():
        gloss = minfo.get('gloss')
        if gloss and gloss in GLOSS_TO_CATEGORY:
            human_mid_to_cat[mid] = GLOSS_TO_CATEGORY[gloss]

    # Build dark auto-assigned map
    dark_mid_to_cat = {}
    dark_mid_confidence = {}
    for mid, minfo in mid_dict.items():
        if mid in human_mid_to_cat:
            continue
        atoms_str = minfo.get('autogloss_atoms', '')
        if atoms_str:
            cat, conf = auto_assign_category(list(atoms_str))
            if cat and cat != 'MIXED':
                dark_mid_to_cat[mid] = cat
                dark_mid_confidence[mid] = conf

    # Build token list
    raw_tokens = []
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        raw_tokens.append(token)

    tokens = []
    for token in raw_tokens:
        w = token.word.strip()
        m = morph.extract(w)
        mid = m.middle

        if mid and mid in human_mid_to_cat:
            cat = human_mid_to_cat[mid]
            cat_source = 'human'
            confidence = 'HUMAN'
        elif mid and mid in dark_mid_to_cat:
            cat = dark_mid_to_cat[mid]
            cat_source = 'auto'
            confidence = dark_mid_confidence.get(mid, 'WEAK')
        else:
            cat = None
            cat_source = 'none'
            confidence = None

        tokens.append({
            'word': w,
            'folio': token.folio,
            'section': token.section,
            'middle': mid,
            'gloss_category': cat,
            'cat_source': cat_source,
            'confidence': confidence,
        })

    return tokens, human_mid_to_cat, dark_mid_to_cat, dark_mid_confidence


# ── Utility ───────────────────────────────────────────────────────────

def jaccard_distance(set_a, set_b):
    """Jaccard distance = 1 - |A∩B| / |A∪B|."""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return 1.0 - intersection / union if union > 0 else 0.0


def jsd(p, q):
    """Jensen-Shannon divergence (squared)."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    p = p / (p.sum() + 1e-30)
    q = q / (q.sum() + 1e-30)
    return float(jensenshannon(p, q) ** 2)


def mean_pairwise(items, func):
    """Mean of pairwise function over all pairs."""
    vals = []
    keys = sorted(items.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            vals.append(func(items[keys[i]], items[keys[j]]))
    return np.mean(vals) if vals else 0.0


# ── T1: Within-Category Jaccard Divergence ────────────────────────────

def test_t1_jaccard(tokens, sections):
    """Do sections use different MIDDLEs within the same category?"""
    print("\n[2/6] T1: Within-Category Jaccard Divergence...")

    classified = [t for t in tokens if t['gloss_category'] and t['section'] in sections]

    # Per-category, per-section: set of MIDDLEs used
    cat_sec_middles = defaultdict(lambda: defaultdict(set))
    for t in classified:
        cat_sec_middles[t['gloss_category']][t['section']].add(t['middle'])

    # Compute mean within-category pairwise Jaccard distance
    per_cat_jaccards = {}
    valid_cats = []
    for cat in ALL_CATEGORIES:
        sec_sets = {s: cat_sec_middles[cat][s] for s in sections if len(cat_sec_middles[cat][s]) >= 3}
        if len(sec_sets) < 2:
            per_cat_jaccards[cat] = {'status': 'INSUFFICIENT', 'n_sections': len(sec_sets)}
            continue
        valid_cats.append(cat)
        mean_jd = mean_pairwise(sec_sets, jaccard_distance)
        per_cat_jaccards[cat] = {
            'mean_jaccard': round(mean_jd, 4),
            'n_sections': len(sec_sets),
            'section_counts': {s: len(sec_sets[s]) for s in sorted(sec_sets.keys())},
        }

    if not valid_cats:
        print("  No categories with sufficient section coverage -- SKIP")
        return {'status': 'SKIP'}

    # Overall mean across valid categories
    obs_mean = np.mean([per_cat_jaccards[c]['mean_jaccard'] for c in valid_cats])

    # Null: permute folio->section mapping, recompute
    rng = np.random.default_rng(42)

    # Pre-compute folio->section map and folio list
    folio_section = {}
    for t in classified:
        folio_section[t['folio']] = t['section']
    folios = sorted(folio_section.keys())
    section_list = [folio_section[f] for f in folios]

    null_means = []
    for _ in range(N_PERM):
        shuffled_sections = list(section_list)
        rng.shuffle(shuffled_sections)
        shuf_folio_sec = dict(zip(folios, shuffled_sections))

        shuf_cat_sec = defaultdict(lambda: defaultdict(set))
        for t in classified:
            shuf_sec = shuf_folio_sec.get(t['folio'], t['section'])
            if shuf_sec in sections:
                shuf_cat_sec[t['gloss_category']][shuf_sec].add(t['middle'])

        cat_jds = []
        for cat in valid_cats:
            sec_sets = {s: shuf_cat_sec[cat][s] for s in sections if len(shuf_cat_sec[cat][s]) >= 3}
            if len(sec_sets) >= 2:
                cat_jds.append(mean_pairwise(sec_sets, jaccard_distance))
        null_means.append(np.mean(cat_jds) if cat_jds else 0.0)

    p_val = (np.sum(np.array(null_means) >= obs_mean) + 1) / (N_PERM + 1)

    status = 'PASS' if p_val < P_THRESHOLD else 'FAIL'
    print(f"  {len(valid_cats)} categories tested across {len(sections)} sections")
    print(f"  Mean within-category Jaccard: {obs_mean:.4f} (null: {np.mean(null_means):.4f})")
    print(f"  -> {status} (p={p_val:.4f})")
    for cat in valid_cats:
        info = per_cat_jaccards[cat]
        print(f"    {cat}: J={info['mean_jaccard']:.3f} ({info['n_sections']}s, "
              f"{info['section_counts']})")

    return {
        'status': status,
        'obs_mean_jaccard': round(obs_mean, 4),
        'null_mean_jaccard': round(float(np.mean(null_means)), 4),
        'p_value_empirical': round(p_val, 4),
        'n_valid_categories': len(valid_cats),
        'per_category': per_cat_jaccards,
    }


# ── T2: Section-Enriched MIDDLEs per Category ────────────────────────

def test_t2_enrichment(tokens, sections):
    """How many MIDDLEs per category are section-enriched (>2x expected)?"""
    print("\n[3/6] T2: Section-Enriched MIDDLEs per Category...")

    classified = [t for t in tokens if t['gloss_category'] and t['section'] in sections]

    # Per MIDDLE: total count, per-section count
    mid_total = Counter()
    mid_sec = defaultdict(lambda: Counter())
    mid_cat = {}
    for t in classified:
        if t['middle']:
            mid_total[t['middle']] += 1
            mid_sec[t['middle']][t['section']] += 1
            mid_cat[t['middle']] = t['gloss_category']

    # Section baselines (fraction of total tokens)
    total_tokens = len(classified)
    sec_fraction = Counter()
    for t in classified:
        sec_fraction[t['section']] += 1
    sec_fraction = {s: c / total_tokens for s, c in sec_fraction.items()}

    # For each MIDDLE with >= 5 tokens, check if any section is >2x enriched
    enriched_count = 0
    total_tested = 0
    enriched_by_cat = defaultdict(int)
    tested_by_cat = defaultdict(int)
    enriched_details = defaultdict(list)

    for mid, count in mid_total.items():
        if count < 5:
            continue
        total_tested += 1
        cat = mid_cat[mid]
        tested_by_cat[cat] += 1

        is_enriched = False
        for sec in sections:
            sec_count = mid_sec[mid].get(sec, 0)
            expected = count * sec_fraction.get(sec, 0)
            if expected > 0:
                ratio = sec_count / expected
                if ratio > 2.0 and sec_count >= 3:
                    is_enriched = True
                    enriched_details[cat].append({
                        'middle': mid, 'section': sec,
                        'ratio': round(ratio, 2), 'observed': sec_count,
                        'expected': round(expected, 1),
                    })
        if is_enriched:
            enriched_count += 1
            enriched_by_cat[cat] += 1

    obs_rate = enriched_count / max(total_tested, 1)

    # Null: permute section labels on tokens (preserving MIDDLE structure)
    rng = np.random.default_rng(42)
    null_rates = []
    section_labels = [t['section'] for t in classified]
    for _ in range(N_PERM):
        shuf_sections = list(section_labels)
        rng.shuffle(shuf_sections)
        shuf_sec_frac = Counter()
        shuf_mid_sec = defaultdict(lambda: Counter())
        for t_idx, t in enumerate(classified):
            shuf_s = shuf_sections[t_idx]
            shuf_sec_frac[shuf_s] += 1
            if t['middle']:
                shuf_mid_sec[t['middle']][shuf_s] += 1
        shuf_sec_frac = {s: c / total_tokens for s, c in shuf_sec_frac.items()}

        shuf_enriched = 0
        for mid, count in mid_total.items():
            if count < 5:
                continue
            for sec in sections:
                sc = shuf_mid_sec[mid].get(sec, 0)
                exp = count * shuf_sec_frac.get(sec, 0)
                if exp > 0 and sc / exp > 2.0 and sc >= 3:
                    shuf_enriched += 1
                    break
        null_rates.append(shuf_enriched / max(total_tested, 1))

    p_val = (np.sum(np.array(null_rates) >= obs_rate) + 1) / (N_PERM + 1)

    status = 'PASS' if p_val < P_THRESHOLD else 'FAIL'
    print(f"  {enriched_count}/{total_tested} MIDDLEs section-enriched ({obs_rate:.1%})")
    print(f"  Null rate: {np.mean(null_rates):.1%}")
    print(f"  -> {status} (p={p_val:.4f})")
    for cat in ALL_CATEGORIES:
        if tested_by_cat[cat] > 0:
            print(f"    {cat}: {enriched_by_cat[cat]}/{tested_by_cat[cat]} enriched")

    # Top enriched examples (up to 5 per category)
    top_examples = {}
    for cat in ALL_CATEGORIES:
        examples = sorted(enriched_details.get(cat, []), key=lambda x: -x['ratio'])[:5]
        if examples:
            top_examples[cat] = examples

    return {
        'status': status,
        'enriched_count': enriched_count,
        'total_tested': total_tested,
        'enriched_rate': round(obs_rate, 4),
        'null_enriched_rate': round(float(np.mean(null_rates)), 4),
        'p_value_empirical': round(p_val, 4),
        'enriched_by_category': {c: enriched_by_cat[c] for c in ALL_CATEGORIES},
        'tested_by_category': {c: tested_by_cat[c] for c in ALL_CATEGORIES},
        'top_examples': top_examples,
    }


# ── T3: Section Classification from Category-MIDDLE Profile ──────────

def test_t3_classification(tokens, sections):
    """Can we predict section from within-category MIDDLE frequency profile?"""
    print("\n[4/6] T3: Section Classification from Category Profile...")

    classified = [t for t in tokens if t['gloss_category'] and t['section'] in sections]

    # Build per-folio, per-category MIDDLE frequency vectors
    folio_cat_middles = defaultdict(lambda: defaultdict(Counter))
    folio_section = {}
    for t in classified:
        if t['middle']:
            folio_cat_middles[t['folio']][t['gloss_category']][t['middle']] += 1
            folio_section[t['folio']] = t['section']

    # Get all MIDDLEs per category (vocabulary)
    cat_vocab = defaultdict(set)
    for t in classified:
        if t['middle'] and t['gloss_category']:
            cat_vocab[t['gloss_category']].add(t['middle'])

    # Build feature vectors: for each folio, concatenate normalized category-MIDDLE profiles
    folios = sorted(folio_section.keys())
    all_middles_by_cat = {cat: sorted(mids) for cat, mids in cat_vocab.items()}

    # Feature vector: for each category, fraction of tokens in that category per MIDDLE
    features = []
    labels = []
    for folio in folios:
        feat = []
        for cat in ALL_CATEGORIES:
            vocab = all_middles_by_cat.get(cat, [])
            counts = folio_cat_middles[folio].get(cat, Counter())
            total = sum(counts.values())
            if total == 0:
                feat.extend([0.0] * len(vocab))
            else:
                feat.extend([counts.get(m, 0) / total for m in vocab])
        features.append(feat)
        labels.append(folio_section[folio])

    features = np.array(features)
    labels = np.array(labels)

    if len(set(labels)) < 2:
        print("  Only 1 section -- SKIP")
        return {'status': 'SKIP'}

    # Leave-one-folio-out nearest centroid classification
    correct = 0
    total = len(folios)
    for i in range(total):
        train_mask = np.ones(total, dtype=bool)
        train_mask[i] = False
        train_feats = features[train_mask]
        train_labels = labels[train_mask]

        # Compute centroids
        centroids = {}
        for sec in sections:
            sec_mask = (train_labels == sec)
            if sec_mask.sum() > 0:
                centroids[sec] = train_feats[sec_mask].mean(axis=0)

        # Predict
        test_feat = features[i]
        best_sec = min(centroids.keys(),
                       key=lambda s: np.linalg.norm(test_feat - centroids[s]))
        if best_sec == labels[i]:
            correct += 1

    obs_accuracy = correct / total

    # Baseline: majority class
    sec_counts = Counter(labels)
    baseline_accuracy = max(sec_counts.values()) / total

    # Null: shuffle folio-section assignments
    rng = np.random.default_rng(42)
    null_accs = []
    for _ in range(N_PERM):
        shuf_labels = labels.copy()
        rng.shuffle(shuf_labels)
        shuf_correct = 0
        for i in range(total):
            train_mask = np.ones(total, dtype=bool)
            train_mask[i] = False
            train_feats = features[train_mask]
            train_labs = shuf_labels[train_mask]
            centroids = {}
            for sec in sections:
                sec_mask = (train_labs == sec)
                if sec_mask.sum() > 0:
                    centroids[sec] = train_feats[sec_mask].mean(axis=0)
            if not centroids:
                continue
            test_feat = features[i]
            best_sec = min(centroids.keys(),
                           key=lambda s: np.linalg.norm(test_feat - centroids[s]))
            if best_sec == shuf_labels[i]:
                shuf_correct += 1
        null_accs.append(shuf_correct / total)

    p_val = (np.sum(np.array(null_accs) >= obs_accuracy) + 1) / (N_PERM + 1)
    increment = obs_accuracy - baseline_accuracy

    status = 'PASS' if p_val < P_THRESHOLD else 'FAIL'
    print(f"  LOO accuracy: {obs_accuracy:.1%} (baseline: {baseline_accuracy:.1%}, "
          f"+{increment:.1%})")
    print(f"  Null mean: {np.mean(null_accs):.1%}")
    print(f"  -> {status} (p={p_val:.4f})")

    return {
        'status': status,
        'accuracy': round(obs_accuracy, 4),
        'baseline_accuracy': round(baseline_accuracy, 4),
        'increment': round(increment, 4),
        'p_value_empirical': round(p_val, 4),
        'null_accuracy_mean': round(float(np.mean(null_accs)), 4),
        'n_folios': total,
        'section_counts': {s: int(c) for s, c in sec_counts.items()},
    }


# ── T4: Category-Conditioned vs Raw JS ───────────────────────────────

def test_t4_partitioning(tokens, sections):
    """Does category conditioning increase section JS divergence?"""
    print("\n[5/6] T4: Category-Conditioned vs Raw JS Divergence...")

    classified = [t for t in tokens if t['gloss_category'] and t['section'] in sections]

    # Get all unique MIDDLEs
    all_middles = sorted(set(t['middle'] for t in classified if t['middle']))
    mid_idx = {m: i for i, m in enumerate(all_middles)}

    # Raw (unconditioned) section profiles over all MIDDLEs
    sec_raw_counts = defaultdict(lambda: np.zeros(len(all_middles)))
    for t in classified:
        if t['middle'] in mid_idx:
            sec_raw_counts[t['section']][mid_idx[t['middle']]] += 1

    raw_profiles = {s: v / (v.sum() + 1e-30) for s, v in sec_raw_counts.items()}

    # Raw mean pairwise JS
    sec_list = sorted(sections)
    raw_jsds = []
    for i in range(len(sec_list)):
        for j in range(i + 1, len(sec_list)):
            raw_jsds.append(jsd(raw_profiles[sec_list[i]], raw_profiles[sec_list[j]]))
    raw_mean_js = np.mean(raw_jsds)

    # Category-conditioned: per category, compute section profiles, then mean JS
    cat_mean_jsds = {}
    valid_cat_jsds = []
    for cat in ALL_CATEGORIES:
        cat_middles = sorted(set(t['middle'] for t in classified
                                 if t['middle'] and t['gloss_category'] == cat))
        if len(cat_middles) < 3:
            cat_mean_jsds[cat] = {'status': 'INSUFFICIENT', 'n_middles': len(cat_middles)}
            continue

        cat_mid_idx = {m: i for i, m in enumerate(cat_middles)}
        sec_cat_counts = defaultdict(lambda: np.zeros(len(cat_middles)))
        for t in classified:
            if t['gloss_category'] == cat and t['middle'] in cat_mid_idx:
                sec_cat_counts[t['section']][cat_mid_idx[t['middle']]] += 1

        valid_secs = {s: v / (v.sum() + 1e-30) for s, v in sec_cat_counts.items()
                      if v.sum() >= 5}
        if len(valid_secs) < 2:
            cat_mean_jsds[cat] = {'status': 'INSUFFICIENT', 'n_sections': len(valid_secs)}
            continue

        cat_jsds = []
        vs = sorted(valid_secs.keys())
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                cat_jsds.append(jsd(valid_secs[vs[i]], valid_secs[vs[j]]))
        mean_cat_js = np.mean(cat_jsds)
        cat_mean_jsds[cat] = {
            'mean_js': round(mean_cat_js, 4),
            'n_middles': len(cat_middles),
            'n_sections': len(valid_secs),
        }
        valid_cat_jsds.append(mean_cat_js)

    if not valid_cat_jsds:
        print("  No valid categories for conditioned JS -- SKIP")
        return {'status': 'SKIP'}

    cond_mean_js = np.mean(valid_cat_jsds)
    ratio = cond_mean_js / max(raw_mean_js, 1e-10)

    # Null: permute MIDDLE->category assignments, recompute conditioned JS
    rng = np.random.default_rng(42)

    # Get the MIDDLE->category mapping for classified tokens
    mid_to_cat = {}
    for t in classified:
        if t['middle'] and t['gloss_category']:
            mid_to_cat[t['middle']] = t['gloss_category']

    middles_list = sorted(mid_to_cat.keys())
    cats_list = [mid_to_cat[m] for m in middles_list]

    null_cond_means = []
    for _ in range(N_PERM):
        shuf_cats = list(cats_list)
        rng.shuffle(shuf_cats)
        shuf_mid_cat = dict(zip(middles_list, shuf_cats))

        shuf_cat_jsds = []
        for cat in ALL_CATEGORIES:
            cat_mids = [m for m, c in shuf_mid_cat.items() if c == cat]
            if len(cat_mids) < 3:
                continue
            cat_mid_idx_s = {m: i for i, m in enumerate(cat_mids)}
            sec_counts_s = defaultdict(lambda: np.zeros(len(cat_mids)))
            for t in classified:
                if t['middle'] in cat_mid_idx_s:
                    sec_counts_s[t['section']][cat_mid_idx_s[t['middle']]] += 1
            valid_s = {s: v / (v.sum() + 1e-30) for s, v in sec_counts_s.items() if v.sum() >= 5}
            if len(valid_s) < 2:
                continue
            vs = sorted(valid_s.keys())
            pair_js = []
            for i in range(len(vs)):
                for j in range(i + 1, len(vs)):
                    pair_js.append(jsd(valid_s[vs[i]], valid_s[vs[j]]))
            shuf_cat_jsds.append(np.mean(pair_js))

        null_cond_means.append(np.mean(shuf_cat_jsds) if shuf_cat_jsds else 0.0)

    p_val = (np.sum(np.array(null_cond_means) >= cond_mean_js) + 1) / (N_PERM + 1)

    status = 'PASS' if p_val < P_THRESHOLD else 'FAIL'
    print(f"  Raw JS: {raw_mean_js:.4f}")
    print(f"  Conditioned JS: {cond_mean_js:.4f} (ratio: {ratio:.2f}x)")
    print(f"  Null mean: {np.mean(null_cond_means):.4f}")
    print(f"  -> {status} (p={p_val:.4f})")
    for cat in ALL_CATEGORIES:
        info = cat_mean_jsds[cat]
        if 'mean_js' in info:
            print(f"    {cat}: JS={info['mean_js']:.4f} ({info['n_middles']}m, {info['n_sections']}s)")

    return {
        'status': status,
        'raw_mean_js': round(raw_mean_js, 4),
        'conditioned_mean_js': round(cond_mean_js, 4),
        'ratio': round(ratio, 2),
        'p_value_empirical': round(p_val, 4),
        'null_conditioned_mean': round(float(np.mean(null_cond_means)), 4),
        'per_category': cat_mean_jsds,
    }


# ── T5: Confidence Tier Stratification ────────────────────────────────

def test_t5_confidence(tokens, sections):
    """Do LOCKED/SOLID auto-assigned MIDDLEs show stronger section vocabulary
    differentiation than WEAK?"""
    print("\n[6/6] T5: Confidence Tier Stratification...")

    results = {}
    for tier_name, tier_set in [('LOCKED_SOLID', {'HUMAN', 'KERNEL', 'LOCKED', 'SOLID'}),
                                 ('WEAK', {'WEAK'})]:
        tier_tokens = [t for t in tokens if t['gloss_category'] and t['section'] in sections
                       and t['confidence'] in tier_set]

        if len(tier_tokens) < 100:
            results[tier_name] = {'status': 'INSUFFICIENT', 'n_tokens': len(tier_tokens)}
            continue

        # Compute within-category Jaccard (simplified version of T1 for this tier)
        cat_sec_middles = defaultdict(lambda: defaultdict(set))
        for t in tier_tokens:
            if t['middle']:
                cat_sec_middles[t['gloss_category']][t['section']].add(t['middle'])

        cat_jaccards = []
        for cat in ALL_CATEGORIES:
            sec_sets = {s: cat_sec_middles[cat][s] for s in sections
                        if len(cat_sec_middles[cat][s]) >= 2}
            if len(sec_sets) >= 2:
                cat_jaccards.append(mean_pairwise(sec_sets, jaccard_distance))

        if not cat_jaccards:
            results[tier_name] = {'status': 'NO_VALID_CATS', 'n_tokens': len(tier_tokens)}
            continue

        mean_jd = float(np.mean(cat_jaccards))

        # Count unique MIDDLEs per section
        sec_mid_counts = Counter()
        for t in tier_tokens:
            if t['middle']:
                sec_mid_counts[t['section']] += 1

        results[tier_name] = {
            'n_tokens': len(tier_tokens),
            'n_categories_tested': len(cat_jaccards),
            'mean_jaccard': round(mean_jd, 4),
            'section_token_counts': dict(sec_mid_counts),
        }

    # Compare: is LOCKED_SOLID Jaccard higher than WEAK?
    ls = results.get('LOCKED_SOLID', {})
    wk = results.get('WEAK', {})
    if 'mean_jaccard' in ls and 'mean_jaccard' in wk:
        direction = 'LOCKED_SOLID_HIGHER' if ls['mean_jaccard'] > wk['mean_jaccard'] \
            else 'WEAK_HIGHER'
        comparison = {
            'ls_jaccard': ls['mean_jaccard'],
            'weak_jaccard': wk['mean_jaccard'],
            'delta': round(ls['mean_jaccard'] - wk['mean_jaccard'], 4),
            'direction': direction,
        }
    else:
        comparison = {'note': 'insufficient data for comparison'}

    # Status: descriptive (no null model -- this is a stratification diagnostic)
    status = 'PASS' if ('mean_jaccard' in ls and 'mean_jaccard' in wk
                        and ls['mean_jaccard'] > wk['mean_jaccard']) else 'FAIL'

    print(f"  LOCKED_SOLID: {ls.get('mean_jaccard', 'N/A')} ({ls.get('n_tokens', 0)} tokens)")
    print(f"  WEAK: {wk.get('mean_jaccard', 'N/A')} ({wk.get('n_tokens', 0)} tokens)")
    if 'delta' in comparison:
        print(f"  Delta: {comparison['delta']:.4f} ({comparison['direction']})")
    print(f"  -> {status}")

    return {
        'status': status,
        'tiers': results,
        'comparison': comparison,
    }


# ── Synthesis ─────────────────────────────────────────────────────────

def synthesize(results):
    """Compute overall verdict."""
    statuses = []
    for key, val in results.items():
        if isinstance(val, dict) and 'status' in val:
            statuses.append(val['status'])

    pass_count = sum(1 for s in statuses if s == 'PASS')
    fail_count = sum(1 for s in statuses if s == 'FAIL')
    skip_count = sum(1 for s in statuses if s == 'SKIP')

    if pass_count >= 4:
        verdict = 'SECTION_PARAMETERIZED'
    elif pass_count >= 3:
        verdict = 'PARTIALLY_PARAMETERIZED'
    elif pass_count >= 1:
        verdict = 'WEAK_SIGNAL'
    else:
        verdict = 'SECTION_UNIVERSAL'

    return {
        'pass_count': pass_count,
        'fail_count': fail_count,
        'skip_count': skip_count,
        'total_tests': len(statuses),
        'verdict': verdict,
        'summary': f"{pass_count}/{len(statuses)} tests pass (p<{P_THRESHOLD}), {skip_count} skipped",
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("CATEGORY SECTION VOCABULARY")
    print("Do sections use different MIDDLEs within the same categories?")
    print("=" * 60)

    t0 = time.time()

    print("\n[1/6] Loading data...")
    tokens, human_mid_to_cat, dark_mid_to_cat, dark_mid_confidence = load_all_data()

    # Determine sections with enough tokens
    sec_counts = Counter(t['section'] for t in tokens if t['gloss_category'])
    sections = sorted(s for s, c in sec_counts.items() if c >= MIN_SECTION_TOKENS)
    n_classified = sum(1 for t in tokens if t['gloss_category'] and t['section'] in sections)

    print(f"  {len(tokens)} B tokens, {n_classified} classified in {len(sections)} sections")
    for s in sections:
        print(f"    {s}: {sec_counts[s]} tokens")

    results = {}
    results['T1_jaccard'] = test_t1_jaccard(tokens, sections)
    results['T2_enrichment'] = test_t2_enrichment(tokens, sections)
    results['T3_classification'] = test_t3_classification(tokens, sections)
    results['T4_partitioning'] = test_t4_partitioning(tokens, sections)
    results['T5_confidence'] = test_t5_confidence(tokens, sections)

    elapsed = time.time() - t0
    synthesis = synthesize(results)

    output = {
        '_metadata': {
            'phase': 'CATEGORY_SECTION_VOCABULARY',
            'phase_number': 449,
            'description': 'Section-specific vocabulary within operational categories',
            'n_tokens': len(tokens),
            'n_classified': n_classified,
            'sections_used': sections,
            'section_counts': {s: sec_counts[s] for s in sections},
            'n_permutations': N_PERM,
            'p_threshold': P_THRESHOLD,
            'elapsed_seconds': round(elapsed, 1),
        },
        'synthesis': synthesis,
        'tests': results,
    }

    out_path = RESULTS_DIR / "category_section_vocabulary.json"
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
