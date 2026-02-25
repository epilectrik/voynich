"""
Phase 452: A_CATEGORY_SCATTERSHOT

8-test battery probing whether the 8-category operational system (C1250)
organizes Currier A's registry structure. Tests apply category assignments
(human gloss + dark auto-assign) to A tokens and check for non-random
patterns at record, paragraph, prefix-context, pipeline-channel, atom,
and section levels.

Bonferroni threshold: p < 0.00625 (0.05 / 8 tests).

Tests:
  T1: A record category coherence (entropy)
  T2: PP mode affinity in A records
  T3: RI extension character predicts gloss category
  T4: A paragraph category specialization
  T5: Bridge vs dark pipeline category distribution
  T6: ch/sh category context in A records
  T7: A record atom-profile coherence
  T8: A section atom balance vs B section profiles

References: C1250, C1258, C913, C1039, C1139, C929, C1207, C946
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, load_middle_classes

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "A_CATEGORY_SCATTERSHOT" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
BONFERRONI_P = 0.00625
SEED = 42

# ================================================================
# CATEGORY MAPPING (from Phase 446/448/449)
# ================================================================
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
ATOM_TO_CATEGORY = {atom: GLOSS_TO_CATEGORY[gloss]
                    for atom, gloss in ATOM_GLOSSES.items()}

# C1207 AXIS clusters (from atom_profiles.py)
AXIS = {
    'a': 'ITERATION', 'i': 'ITERATION', 'n': 'ITERATION', 'r': 'ITERATION',
    'c': 'MONITORING', 'h': 'MONITORING',
    'k': 'ENERGY', 'l': 'ENERGY',
    'd': 'CLOSURE', 'y': 'CLOSURE',
    'o': 'STRUCTURAL', 'p': 'STRUCTURAL',
    'e': 'STABILITY',
    't': 'FREE',
    'f': 'OTHER', 's': 'OTHER', 'm': 'OTHER', 'q': 'OTHER',
}
AXIS_NAMES = sorted(set(AXIS.values()))

# C1231 suffix centroids for mode classification
TERMINAL_SUFFIXES = {'edy', 'dy', 'eey', 'ey', 'y', 'hy', 'iry', 'oly',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}
MODE_A_CENTROID = np.array([0.430, 0.019, 0.086, 0.466])
MODE_B_CENTROID = np.array([0.155, 0.031, 0.072, 0.741])


# ================================================================
# NUMPY JSON ENCODER
# ================================================================
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


# ================================================================
# AUTO CATEGORY ASSIGNMENT
# ================================================================
def auto_assign_category(autogloss_atoms):
    """Assign category via plurality vote over atoms."""
    if not autogloss_atoms:
        return None
    votes = Counter()
    for atom in autogloss_atoms:
        cat = ATOM_TO_CATEGORY.get(atom)
        if cat:
            votes[cat] += 1
    if not votes:
        return None
    max_count = max(votes.values())
    winners = [c for c, v in votes.items() if v == max_count]
    if len(winners) == 1:
        return winners[0]
    # Tie-break: alphabetical (deterministic)
    return sorted(winners)[0]


def build_category_map():
    """Build mid_to_category dict from middle_dictionary.json."""
    with open(ROOT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict = json.load(f)['middles']

    mid_to_cat = {}

    # Human-glossed first (priority)
    for mid, minfo in mid_dict.items():
        gloss = minfo.get('gloss')
        if gloss and gloss in GLOSS_TO_CATEGORY:
            mid_to_cat[mid] = GLOSS_TO_CATEGORY[gloss]

    # Dark auto-assigned
    for mid, minfo in mid_dict.items():
        if mid in mid_to_cat:
            continue
        atoms_str = minfo.get('autogloss_atoms', '')
        if atoms_str:
            cat = auto_assign_category(list(atoms_str))
            if cat:
                mid_to_cat[mid] = cat

    return mid_to_cat


# ================================================================
# DATA LOADING
# ================================================================
def load_all_data():
    """Load A tokens, B tokens, PP/RI classes, category map, bridges, dark pipeline."""
    t0 = time.time()
    tx = Transcript()
    morph = Morphology()

    # Category map
    mid_to_cat = build_category_map()
    print(f"  Category map: {len(mid_to_cat)} MIDDLEs assigned")

    # PP/RI classes
    ri_middles, pp_middles = load_middle_classes()
    print(f"  PP: {len(pp_middles)}, RI: {len(ri_middles)}")

    # A tokens with morphology
    a_tokens = []
    for token in tx.currier_a():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        tc = 'PP' if mid in pp_middles else ('RI' if mid in ri_middles else 'UNK')
        cat = mid_to_cat.get(mid) if mid else None
        a_tokens.append({
            'word': w, 'folio': token.folio, 'line': token.line,
            'section': token.section,
            'prefix': m.prefix, 'middle': mid, 'suffix': m.suffix,
            'articulator': m.articulator,
            'token_class': tc, 'category': cat,
            'par_initial': token.par_initial, 'par_final': token.par_final,
            'line_initial': token.line_initial, 'line_final': token.line_final,
        })
    print(f"  A tokens: {len(a_tokens)}")

    # B tokens with morphology (for T2 mode classification)
    b_tokens = []
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        tc = 'PP' if mid in pp_middles else ('RI' if mid in ri_middles else 'UNK')
        b_tokens.append({
            'word': w, 'folio': token.folio, 'line': token.line,
            'section': token.section,
            'prefix': m.prefix, 'middle': mid, 'suffix': m.suffix,
            'token_class': tc,
        })
    print(f"  B tokens: {len(b_tokens)}")

    # Bridge MIDDLEs
    bridge_path = (ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM'
                   / 'results' / 'bridge_selection.json')
    with open(bridge_path, encoding='utf-8') as f:
        bridge_data = json.load(f)
    bridge_middles = set(bridge_data['t5_structural_profile']['bridge_middles'])
    print(f"  Bridge MIDDLEs: {len(bridge_middles)}")

    # Dark pipeline MIDDLEs
    dark_path = ROOT / 'data' / 'dark_pipeline_middles.json'
    with open(dark_path, encoding='utf-8') as f:
        dark_data = json.load(f)
    dark_middles = set(dark_data['middles'])
    print(f"  Dark pipeline MIDDLEs: {len(dark_middles)}")

    dt = time.time() - t0
    print(f"  Data loaded in {dt:.1f}s")

    return (a_tokens, b_tokens, mid_to_cat, ri_middles, pp_middles,
            bridge_middles, dark_middles)


# ================================================================
# UTILITY
# ================================================================
def entropy(counts):
    """Shannon entropy from a Counter or dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = np.array([c / total for c in counts.values() if c > 0], dtype=float)
    return float(-np.sum(probs * np.log2(probs)))


def cosine_sim(v1, v2):
    """Cosine similarity between two vectors."""
    d1 = np.dot(v1, v2)
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(d1 / (n1 * n2))


def middle_to_atom_vector(mid):
    """Convert a MIDDLE string to an AXIS cluster frequency vector."""
    vec = np.zeros(len(AXIS_NAMES), dtype=float)
    if not mid:
        return vec
    axis_idx = {name: i for i, name in enumerate(AXIS_NAMES)}
    for ch in mid:
        ax = AXIS.get(ch)
        if ax:
            vec[axis_idx[ax]] += 1
    total = vec.sum()
    if total > 0:
        vec /= total
    return vec


def verdict(p_val, effect=None, effect_threshold=None):
    """Return PASS/FAIL/WEAK verdict."""
    if p_val < BONFERRONI_P:
        if effect_threshold is not None and effect is not None:
            if abs(effect) < effect_threshold:
                return 'WEAK'
        return 'PASS'
    elif p_val < 0.05:
        return 'WEAK'
    return 'FAIL'


# ================================================================
# T1: A Record Category Coherence
# ================================================================
def test_t1(a_tokens, rng):
    """Do A records draw PP MIDDLEs from fewer categories than random?"""
    print("\n=== T1: A Record Category Coherence ===")
    t0 = time.time()

    # Group A tokens by (folio, line) = record
    records = defaultdict(list)
    for tok in a_tokens:
        if tok['token_class'] == 'PP' and tok['category']:
            records[(tok['folio'], tok['line'])].append(tok['category'])

    # Filter to records with 2+ categorized PP MIDDLEs
    valid_records = {k: v for k, v in records.items() if len(v) >= 2}
    n_records = len(valid_records)
    print(f"  Records with 2+ categorized PP: {n_records}")

    if n_records < 10:
        print("  SKIP: Too few records")
        return {'test': 'T1', 'verdict': 'SKIP', 'reason': 'too_few_records',
                'n_records': n_records}

    # Observed mean entropy
    record_entropies = []
    for cats in valid_records.values():
        record_entropies.append(entropy(Counter(cats)))
    obs_mean = np.mean(record_entropies)
    print(f"  Observed mean entropy: {obs_mean:.4f}")

    # Pool all category labels for shuffling
    all_cats = []
    record_sizes = []
    for cats in valid_records.values():
        all_cats.extend(cats)
        record_sizes.append(len(cats))
    all_cats = np.array(all_cats)

    # Null: shuffle category labels, recompute per-record entropy
    null_means = []
    for _ in range(N_PERM):
        shuffled = all_cats.copy()
        rng.shuffle(shuffled)
        idx = 0
        perm_entropies = []
        for sz in record_sizes:
            chunk = shuffled[idx:idx+sz]
            perm_entropies.append(entropy(Counter(chunk)))
            idx += sz
        null_means.append(np.mean(perm_entropies))

    null_means = np.array(null_means)
    p_val = float(np.mean(null_means <= obs_mean))
    effect = float((np.mean(null_means) - obs_mean) / (np.std(null_means) + 1e-12))

    vrd = verdict(p_val)
    dt = time.time() - t0
    print(f"  Null mean: {np.mean(null_means):.4f} +/- {np.std(null_means):.4f}")
    print(f"  Effect (Cohen d): {effect:.3f}")
    print(f"  p = {p_val:.6f}  -> {vrd}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T1', 'verdict': vrd, 'p_value': p_val,
        'obs_mean_entropy': obs_mean,
        'null_mean_entropy': float(np.mean(null_means)),
        'null_std_entropy': float(np.std(null_means)),
        'effect_cohen_d': effect,
        'n_records': n_records,
        'n_pp_middles': len(all_cats),
    }


# ================================================================
# T2: PP Mode Affinity in A Records
# ================================================================
def test_t2(a_tokens, b_tokens, pp_middles, rng):
    """Do A records cluster by B-mode affinity?"""
    print("\n=== T2: PP Mode Affinity in A Records ===")
    t0 = time.time()

    # Step 1: Classify B lines by mode (C1231 suffix centroids)
    b_lines = defaultdict(list)
    for tok in b_tokens:
        b_lines[(tok['folio'], tok['line'])].append(tok)

    def classify_line_mode(line_toks):
        if len(line_toks) < 3:
            return None
        n = len(line_toks)
        cats = [0, 0, 0, 0]
        for t in line_toks:
            sfx = t['suffix'] or ''
            if sfx in TERMINAL_SUFFIXES:
                cats[0] += 1
            elif sfx in CONNECTOR_SUFFIXES:
                cats[1] += 1
            elif sfx in ITERATE_SUFFIXES:
                cats[2] += 1
            else:
                cats[3] += 1
        vec = np.array(cats, dtype=float) / n
        dist_a = np.linalg.norm(vec - MODE_A_CENTROID)
        dist_b = np.linalg.norm(vec - MODE_B_CENTROID)
        return 'A' if dist_a < dist_b else 'B'

    line_modes = {}
    for key, toks in b_lines.items():
        mode = classify_line_mode(toks)
        if mode:
            line_modes[key] = mode

    print(f"  B lines classified: {len(line_modes)} "
          f"(A: {sum(1 for v in line_modes.values() if v == 'A')}, "
          f"B: {sum(1 for v in line_modes.values() if v == 'B')})")

    # Step 2: For each PP MIDDLE, count appearances in Mode A vs Mode B lines
    mid_mode_counts = defaultdict(lambda: {'A': 0, 'B': 0})
    for key, toks in b_lines.items():
        mode = line_modes.get(key)
        if not mode:
            continue
        for t in toks:
            mid = t['middle']
            if mid and mid in pp_middles:
                mid_mode_counts[mid][mode] += 1

    # Classify each PP MIDDLE by mode affinity
    mid_affinity = {}
    for mid, counts in mid_mode_counts.items():
        a_ct = counts['A']
        b_ct = counts['B']
        total = a_ct + b_ct
        if total < 3:
            continue
        ratio = (a_ct + 0.5) / (b_ct + 0.5)  # Laplace smoothing
        if ratio > 1.5:
            mid_affinity[mid] = 'A_ENRICHED'
        elif ratio < 0.67:
            mid_affinity[mid] = 'B_ENRICHED'
        else:
            mid_affinity[mid] = 'NEUTRAL'

    aff_counts = Counter(mid_affinity.values())
    print(f"  PP MIDDLEs with affinity: {len(mid_affinity)} "
          f"(A_enr: {aff_counts.get('A_ENRICHED', 0)}, "
          f"B_enr: {aff_counts.get('B_ENRICHED', 0)}, "
          f"neutral: {aff_counts.get('NEUTRAL', 0)})")

    # Step 3: For each A record, compute fraction A-enriched vs B-enriched
    a_records = defaultdict(list)
    for tok in a_tokens:
        mid = tok['middle']
        if tok['token_class'] == 'PP' and mid and mid in mid_affinity:
            a_records[(tok['folio'], tok['line'])].append(mid_affinity[mid])

    valid = {k: v for k, v in a_records.items() if len(v) >= 2}
    n_valid = len(valid)
    print(f"  A records with 2+ affinity-classified PP: {n_valid}")

    if n_valid < 10:
        print("  SKIP: Too few records")
        return {'test': 'T2', 'verdict': 'SKIP', 'reason': 'too_few_records',
                'n_records': n_valid}

    # Metric: within-record affinity concentration
    # For each record, fraction that is the dominant affinity class
    def concentration(labels):
        c = Counter(labels)
        return max(c.values()) / len(labels)

    obs_concs = [concentration(v) for v in valid.values()]
    obs_mean = np.mean(obs_concs)

    # Pool all affinity labels
    all_labels = []
    record_sizes = []
    for v in valid.values():
        all_labels.extend(v)
        record_sizes.append(len(v))
    all_labels = np.array(all_labels)

    # Null: shuffle affinity labels
    null_means = []
    for _ in range(N_PERM):
        shuffled = all_labels.copy()
        rng.shuffle(shuffled)
        idx = 0
        perm_concs = []
        for sz in record_sizes:
            chunk = shuffled[idx:idx+sz]
            perm_concs.append(concentration(chunk))
            idx += sz
        null_means.append(np.mean(perm_concs))

    null_means = np.array(null_means)
    p_val = float(np.mean(null_means >= obs_mean))
    effect = float((obs_mean - np.mean(null_means)) / (np.std(null_means) + 1e-12))

    vrd = verdict(p_val)
    dt = time.time() - t0
    print(f"  Observed mean concentration: {obs_mean:.4f}")
    print(f"  Null mean: {np.mean(null_means):.4f} +/- {np.std(null_means):.4f}")
    print(f"  Effect (Cohen d): {effect:.3f}")
    print(f"  p = {p_val:.6f}  -> {vrd}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T2', 'verdict': vrd, 'p_value': p_val,
        'obs_mean_concentration': float(obs_mean),
        'null_mean_concentration': float(np.mean(null_means)),
        'null_std': float(np.std(null_means)),
        'effect_cohen_d': effect,
        'n_records': n_valid,
        'n_classified_pp': len(all_labels),
        'affinity_counts': dict(aff_counts),
        'b_mode_counts': {
            'A': sum(1 for v in line_modes.values() if v == 'A'),
            'B': sum(1 for v in line_modes.values() if v == 'B'),
        },
    }


# ================================================================
# T3: RI Extension Character Predicts Gloss Category
# ================================================================
def test_t3(a_tokens, pp_middles, mid_to_cat):
    """Does extension character in RI MIDDLEs predict PP base category?"""
    print("\n=== T3: RI Extension Character Predicts Category ===")
    t0 = time.time()

    # For each RI MIDDLE, find longest PP substring (C913 methodology)
    ri_decompositions = []
    seen_ri = set()

    for tok in a_tokens:
        mid = tok['middle']
        if not mid or tok['token_class'] != 'RI':
            continue
        if mid in seen_ri:
            continue
        seen_ri.add(mid)

        # Find longest PP base that is a substring from the start
        best_base = None
        best_ext = None
        for length in range(len(mid) - 1, 0, -1):
            candidate = mid[:length]
            if candidate in pp_middles:
                best_base = candidate
                best_ext = mid[length:]
                break

        if best_base and best_ext and len(best_ext) <= 3:
            base_cat = mid_to_cat.get(best_base)
            if base_cat:
                ext_char = best_ext[0]  # First extension character
                ri_decompositions.append({
                    'ri_middle': mid,
                    'pp_base': best_base,
                    'extension': best_ext,
                    'ext_char': ext_char,
                    'base_category': base_cat,
                })

    print(f"  RI MIDDLEs decomposed: {len(ri_decompositions)} "
          f"(of {len(seen_ri)} unique RI)")

    if len(ri_decompositions) < 20:
        print("  SKIP: Too few decompositions")
        return {'test': 'T3', 'verdict': 'SKIP', 'reason': 'too_few_decompositions',
                'n_decomposed': len(ri_decompositions)}

    # Build contingency table: ext_char x base_category
    ext_chars = sorted(set(d['ext_char'] for d in ri_decompositions))
    cats = sorted(set(d['base_category'] for d in ri_decompositions))

    # Filter to ext_chars with 3+ occurrences
    ext_counts = Counter(d['ext_char'] for d in ri_decompositions)
    ext_chars = [e for e in ext_chars if ext_counts[e] >= 3]

    if len(ext_chars) < 2 or len(cats) < 2:
        print(f"  SKIP: Need 2+ ext chars and 2+ categories "
              f"(got {len(ext_chars)} ext, {len(cats)} cats)")
        return {'test': 'T3', 'verdict': 'SKIP',
                'reason': 'insufficient_variety',
                'n_ext_chars': len(ext_chars), 'n_categories': len(cats)}

    # Filter decompositions to those with valid ext_chars
    filtered = [d for d in ri_decompositions if d['ext_char'] in ext_chars]

    contingency = np.zeros((len(ext_chars), len(cats)), dtype=int)
    ext_idx = {e: i for i, e in enumerate(ext_chars)}
    cat_idx = {c: i for i, c in enumerate(cats)}
    for d in filtered:
        contingency[ext_idx[d['ext_char']], cat_idx[d['base_category']]] += 1

    print(f"  Contingency table: {len(ext_chars)} ext chars x {len(cats)} categories")
    print(f"  Total observations: {contingency.sum()}")

    # Print contingency table
    header = "       " + "  ".join(f"{c:>10}" for c in cats)
    print(header)
    for i, ec in enumerate(ext_chars):
        row = f"  {ec:>3}  " + "  ".join(f"{contingency[i,j]:>10}" for j in range(len(cats)))
        print(row)

    # Chi-squared test
    # Check for minimum expected frequency
    row_sums = contingency.sum(axis=1)
    col_sums = contingency.sum(axis=0)
    total = contingency.sum()
    expected = np.outer(row_sums, col_sums) / total
    min_expected = expected.min()
    print(f"  Min expected frequency: {min_expected:.2f}")

    if min_expected < 1.0:
        # Use Fisher's exact or permutation test instead
        print("  Low expected counts: using permutation chi-sq")
        obs_chi2 = float(sp_stats.chi2_contingency(contingency)[0])
        # Permutation test
        all_ext = [d['ext_char'] for d in filtered]
        all_base_cat = [d['base_category'] for d in filtered]
        rng = np.random.RandomState(SEED)
        n_exceed = 0
        for _ in range(N_PERM):
            perm_ext = list(all_ext)
            rng.shuffle(perm_ext)
            perm_table = np.zeros_like(contingency)
            for pe, bc in zip(perm_ext, all_base_cat):
                if pe in ext_idx:
                    perm_table[ext_idx[pe], cat_idx[bc]] += 1
            try:
                perm_chi2 = sp_stats.chi2_contingency(perm_table)[0]
            except ValueError:
                perm_chi2 = 0.0
            if perm_chi2 >= obs_chi2:
                n_exceed += 1
        p_val = (n_exceed + 1) / (N_PERM + 1)
        cramers_v = float(np.sqrt(obs_chi2 / (total * (min(len(ext_chars), len(cats)) - 1))))
    else:
        chi2, p_val, dof, expected = sp_stats.chi2_contingency(contingency)
        obs_chi2 = float(chi2)
        p_val = float(p_val)
        cramers_v = float(np.sqrt(chi2 / (total * (min(len(ext_chars), len(cats)) - 1))))

    vrd = verdict(p_val, cramers_v, 0.1)
    dt = time.time() - t0
    print(f"  Chi-sq: {obs_chi2:.2f}, Cramer's V: {cramers_v:.3f}")
    print(f"  p = {p_val:.6f}  -> {vrd}")
    print(f"  ({dt:.1f}s)")

    # Top ext_char-category associations
    top_assoc = []
    for i, ec in enumerate(ext_chars):
        row = contingency[i]
        if row.sum() > 0:
            dominant_cat = cats[np.argmax(row)]
            frac = row.max() / row.sum()
            top_assoc.append({'ext_char': ec, 'dominant_category': dominant_cat,
                              'fraction': float(frac), 'count': int(row.sum())})

    return {
        'test': 'T3', 'verdict': vrd, 'p_value': p_val,
        'chi_squared': obs_chi2, 'cramers_v': cramers_v,
        'n_decomposed': len(ri_decompositions),
        'n_filtered': len(filtered),
        'ext_chars': ext_chars,
        'categories': cats,
        'contingency': contingency.tolist(),
        'top_associations': top_assoc,
    }


# ================================================================
# T4: A Paragraph Category Specialization
# ================================================================
def test_t4(a_tokens, rng):
    """Do A paragraphs specialize by operational category?"""
    print("\n=== T4: A Paragraph Category Specialization ===")
    t0 = time.time()

    # Group tokens into paragraphs
    # A paragraph = consecutive tokens between par_initial and par_final flags
    paragraphs = defaultdict(list)
    current_par = None
    par_id = 0

    # Sort tokens by folio, line, position (they come in order from transcript)
    for tok in a_tokens:
        if tok['par_initial']:
            par_id += 1
            current_par = par_id
        if current_par is not None and tok['token_class'] == 'PP' and tok['category']:
            paragraphs[current_par].append(tok['category'])
        if tok['par_final']:
            current_par = None

    # Filter to paragraphs with 3+ categorized PP MIDDLEs
    valid = {k: v for k, v in paragraphs.items() if len(v) >= 3}
    n_pars = len(valid)
    print(f"  Paragraphs with 3+ categorized PP: {n_pars}")

    if n_pars < 5:
        print("  SKIP: Too few paragraphs")
        return {'test': 'T4', 'verdict': 'SKIP', 'reason': 'too_few_paragraphs',
                'n_paragraphs': n_pars}

    # Observed mean entropy
    par_entropies = []
    for cats in valid.values():
        par_entropies.append(entropy(Counter(cats)))
    obs_mean = np.mean(par_entropies)
    print(f"  Observed mean entropy: {obs_mean:.4f}")

    # Pool all category labels for shuffling
    all_cats = []
    par_sizes = []
    for cats in valid.values():
        all_cats.extend(cats)
        par_sizes.append(len(cats))
    all_cats = np.array(all_cats)

    # Null: shuffle category labels across paragraphs
    null_means = []
    for _ in range(N_PERM):
        shuffled = all_cats.copy()
        rng.shuffle(shuffled)
        idx = 0
        perm_entropies = []
        for sz in par_sizes:
            chunk = shuffled[idx:idx+sz]
            perm_entropies.append(entropy(Counter(chunk)))
            idx += sz
        null_means.append(np.mean(perm_entropies))

    null_means = np.array(null_means)
    p_val = float(np.mean(null_means <= obs_mean))
    effect = float((np.mean(null_means) - obs_mean) / (np.std(null_means) + 1e-12))

    vrd = verdict(p_val)
    dt = time.time() - t0
    print(f"  Null mean: {np.mean(null_means):.4f} +/- {np.std(null_means):.4f}")
    print(f"  Effect (Cohen d): {effect:.3f}")
    print(f"  p = {p_val:.6f}  -> {vrd}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T4', 'verdict': vrd, 'p_value': p_val,
        'obs_mean_entropy': float(obs_mean),
        'null_mean_entropy': float(np.mean(null_means)),
        'null_std_entropy': float(np.std(null_means)),
        'effect_cohen_d': effect,
        'n_paragraphs': n_pars,
        'n_pp_middles': len(all_cats),
        'par_size_median': float(np.median(par_sizes)),
        'par_size_range': [int(min(par_sizes)), int(max(par_sizes))],
    }


# ================================================================
# T5: Bridge vs Dark Pipeline Category Distribution
# ================================================================
def test_t5(bridge_middles, dark_middles, mid_to_cat):
    """Do bridge and dark pipeline MIDDLEs differ in category profile?"""
    print("\n=== T5: Bridge vs Dark Pipeline Category Distribution ===")
    t0 = time.time()

    # Get categories for bridge and dark pipeline MIDDLEs
    bridge_cats = [mid_to_cat[m] for m in bridge_middles if m in mid_to_cat]
    dark_cats = [mid_to_cat[m] for m in dark_middles if m in mid_to_cat]
    print(f"  Bridge with category: {len(bridge_cats)} / {len(bridge_middles)}")
    print(f"  Dark with category: {len(dark_cats)} / {len(dark_middles)}")

    if len(bridge_cats) < 10 or len(dark_cats) < 10:
        print("  SKIP: Too few categorized MIDDLEs")
        return {'test': 'T5', 'verdict': 'SKIP', 'reason': 'too_few_categorized'}

    # Category distributions
    bridge_dist = Counter(bridge_cats)
    dark_dist = Counter(dark_cats)

    # 2x8 contingency table
    cats = ALL_CATEGORIES
    contingency = np.zeros((2, len(cats)), dtype=int)
    for i, c in enumerate(cats):
        contingency[0, i] = bridge_dist.get(c, 0)
        contingency[1, i] = dark_dist.get(c, 0)

    # Remove columns with all zeros
    nonzero = contingency.sum(axis=0) > 0
    cats_active = [c for c, nz in zip(cats, nonzero) if nz]
    contingency = contingency[:, nonzero]

    print(f"  Active categories: {len(cats_active)}")
    print(f"  Bridge: {dict(bridge_dist)}")
    print(f"  Dark:   {dict(dark_dist)}")

    if contingency.shape[1] < 2:
        print("  SKIP: <2 active categories")
        return {'test': 'T5', 'verdict': 'SKIP', 'reason': 'too_few_categories'}

    # Chi-squared
    chi2, p_val, dof, expected = sp_stats.chi2_contingency(contingency)
    total = contingency.sum()
    cramers_v = float(np.sqrt(chi2 / (total * (min(2, len(cats_active)) - 1))))

    # If min expected < 5, also do permutation
    min_exp = expected.min()
    if min_exp < 5:
        print(f"  Min expected = {min_exp:.1f}, adding permutation check")
        obs_chi2 = chi2
        all_labels = bridge_cats + dark_cats
        group = ['bridge'] * len(bridge_cats) + ['dark'] * len(dark_cats)
        rng_t5 = np.random.RandomState(SEED)
        n_exceed = 0
        for _ in range(N_PERM):
            perm_group = list(group)
            rng_t5.shuffle(perm_group)
            p_bridge = [l for l, g in zip(all_labels, perm_group) if g == 'bridge']
            p_dark = [l for l, g in zip(all_labels, perm_group) if g == 'dark']
            p_b_dist = Counter(p_bridge)
            p_d_dist = Counter(p_dark)
            p_ct = np.zeros((2, len(cats_active)), dtype=int)
            for i, c in enumerate(cats_active):
                p_ct[0, i] = p_b_dist.get(c, 0)
                p_ct[1, i] = p_d_dist.get(c, 0)
            try:
                perm_chi2 = sp_stats.chi2_contingency(p_ct)[0]
            except ValueError:
                perm_chi2 = 0.0
            if perm_chi2 >= obs_chi2:
                n_exceed += 1
        p_val = (n_exceed + 1) / (N_PERM + 1)

    # Length-controlled check
    bridge_lens = [len(m) for m in bridge_middles if m in mid_to_cat]
    dark_lens = [len(m) for m in dark_middles if m in mid_to_cat]
    len_bins = {'short': (1, 2), 'medium': (3, 4), 'long': (5, 99)}
    length_control = {}
    for bname, (lo, hi) in len_bins.items():
        b_in = [mid_to_cat[m] for m in bridge_middles
                if m in mid_to_cat and lo <= len(m) <= hi]
        d_in = [mid_to_cat[m] for m in dark_middles
                if m in mid_to_cat and lo <= len(m) <= hi]
        if len(b_in) >= 5 and len(d_in) >= 5:
            b_ct = Counter(b_in)
            d_ct = Counter(d_in)
            active = sorted(set(list(b_ct.keys()) + list(d_ct.keys())))
            ct = np.zeros((2, len(active)), dtype=int)
            for i, c in enumerate(active):
                ct[0, i] = b_ct.get(c, 0)
                ct[1, i] = d_ct.get(c, 0)
            if ct.shape[1] >= 2:
                try:
                    lc_chi2, lc_p, _, _ = sp_stats.chi2_contingency(ct)
                    length_control[bname] = {
                        'chi2': float(lc_chi2), 'p': float(lc_p),
                        'n_bridge': len(b_in), 'n_dark': len(d_in)}
                except ValueError:
                    length_control[bname] = {'error': 'chi2_failed'}
            else:
                length_control[bname] = {'skip': 'too_few_cats'}
        else:
            length_control[bname] = {'skip': 'too_few_samples',
                                      'n_bridge': len(b_in), 'n_dark': len(d_in)}

    vrd = verdict(float(p_val), cramers_v, 0.1)
    dt = time.time() - t0
    print(f"  Chi-sq: {float(chi2):.2f}, Cramer's V: {cramers_v:.3f}")
    print(f"  p = {float(p_val):.6f}  -> {vrd}")
    print(f"  Length-controlled: {length_control}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T5', 'verdict': vrd, 'p_value': float(p_val),
        'chi_squared': float(chi2), 'cramers_v': cramers_v,
        'n_bridge': len(bridge_cats), 'n_dark': len(dark_cats),
        'bridge_dist': dict(bridge_dist), 'dark_dist': dict(dark_dist),
        'categories': cats_active,
        'contingency': contingency.tolist(),
        'length_control': length_control,
    }


# ================================================================
# T6: ch/sh Category Context in A Records
# ================================================================
def test_t6(a_tokens, rng):
    """Do ch and sh prefixes appear alongside different category MIDDLEs?"""
    print("\n=== T6: ch/sh Category Context in A Records ===")
    t0 = time.time()

    # Group tokens by (folio, line) = record
    records = defaultdict(list)
    for tok in a_tokens:
        records[(tok['folio'], tok['line'])].append(tok)

    # For ch-containing and sh-containing lines, collect OTHER tokens' categories
    ch_context_cats = []
    sh_context_cats = []

    for key, toks in records.items():
        has_ch = any(t['prefix'] in ('ch', 'pch', 'tch', 'kch', 'dch', 'fch',
                                      'rch', 'sch', 'lch') for t in toks)
        has_sh = any(t['prefix'] in ('sh', 'lsh') for t in toks)

        # Collect categories of other PP tokens on this line
        other_cats = [t['category'] for t in toks
                      if t['token_class'] == 'PP' and t['category']]

        if not other_cats:
            continue

        if has_ch:
            ch_context_cats.extend(other_cats)
        if has_sh:
            sh_context_cats.extend(other_cats)

    print(f"  ch-context categories: {len(ch_context_cats)}")
    print(f"  sh-context categories: {len(sh_context_cats)}")

    if len(ch_context_cats) < 20 or len(sh_context_cats) < 20:
        # Aggregate at folio level as fallback
        print("  Per-line too sparse, aggregating by folio...")
        folio_records = defaultdict(list)
        for tok in a_tokens:
            folio_records[tok['folio']].append(tok)

        ch_context_cats = []
        sh_context_cats = []
        for folio, toks in folio_records.items():
            has_ch = any(t['prefix'] in ('ch', 'pch', 'tch', 'kch', 'dch',
                                          'fch', 'rch', 'sch', 'lch') for t in toks)
            has_sh = any(t['prefix'] in ('sh', 'lsh') for t in toks)
            other_cats = [t['category'] for t in toks
                          if t['token_class'] == 'PP' and t['category']]
            if not other_cats:
                continue
            if has_ch:
                ch_context_cats.extend(other_cats)
            if has_sh:
                sh_context_cats.extend(other_cats)
        print(f"  Folio-level ch-context: {len(ch_context_cats)}")
        print(f"  Folio-level sh-context: {len(sh_context_cats)}")

    if len(ch_context_cats) < 10 or len(sh_context_cats) < 10:
        print("  SKIP: Too few samples even at folio level")
        return {'test': 'T6', 'verdict': 'SKIP', 'reason': 'too_few_samples'}

    # Compare distributions
    ch_dist = Counter(ch_context_cats)
    sh_dist = Counter(sh_context_cats)
    print(f"  ch context: {dict(ch_dist)}")
    print(f"  sh context: {dict(sh_dist)}")

    cats = sorted(set(list(ch_dist.keys()) + list(sh_dist.keys())))
    contingency = np.zeros((2, len(cats)), dtype=int)
    for i, c in enumerate(cats):
        contingency[0, i] = ch_dist.get(c, 0)
        contingency[1, i] = sh_dist.get(c, 0)

    if contingency.shape[1] < 2:
        print("  SKIP: <2 shared categories")
        return {'test': 'T6', 'verdict': 'SKIP', 'reason': 'too_few_categories'}

    # Chi-squared
    chi2, p_val, dof, expected = sp_stats.chi2_contingency(contingency)
    total = contingency.sum()
    cramers_v = float(np.sqrt(chi2 / (total * (min(2, len(cats)) - 1))))

    # JSD for effect measure
    ch_vec = np.array([ch_dist.get(c, 0) for c in cats], dtype=float)
    sh_vec = np.array([sh_dist.get(c, 0) for c in cats], dtype=float)
    ch_prob = ch_vec / (ch_vec.sum() + 1e-30)
    sh_prob = sh_vec / (sh_vec.sum() + 1e-30)
    from scipy.spatial.distance import jensenshannon
    jsd_val = float(jensenshannon(ch_prob, sh_prob) ** 2)

    vrd = verdict(float(p_val), cramers_v, 0.05)
    dt = time.time() - t0
    print(f"  Chi-sq: {float(chi2):.2f}, Cramer's V: {cramers_v:.3f}")
    print(f"  JSD: {jsd_val:.4f}")
    print(f"  p = {float(p_val):.6f}  -> {vrd}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T6', 'verdict': vrd, 'p_value': float(p_val),
        'chi_squared': float(chi2), 'cramers_v': cramers_v,
        'jsd': jsd_val,
        'n_ch_context': len(ch_context_cats),
        'n_sh_context': len(sh_context_cats),
        'ch_dist': dict(ch_dist), 'sh_dist': dict(sh_dist),
        'categories': cats,
        'contingency': contingency.tolist(),
    }


# ================================================================
# T7: A Record Atom-Profile Coherence
# ================================================================
def test_t7(a_tokens, mid_to_cat, t1_result, rng):
    """Are A records more atom-coherent than random?"""
    print("\n=== T7: A Record Atom-Profile Coherence ===")
    t0 = time.time()

    # Group A tokens by record
    records = defaultdict(list)
    for tok in a_tokens:
        mid = tok['middle']
        if tok['token_class'] == 'PP' and mid:
            records[(tok['folio'], tok['line'])].append(mid)

    # Filter to records with 2+ PP MIDDLEs
    valid = {k: v for k, v in records.items() if len(v) >= 2}
    n_records = len(valid)
    print(f"  Records with 2+ PP MIDDLEs: {n_records}")

    if n_records < 10:
        print("  SKIP: Too few records")
        return {'test': 'T7', 'verdict': 'SKIP', 'reason': 'too_few_records',
                'n_records': n_records}

    # Pre-compute atom vectors for all unique MIDDLEs
    all_middles = set()
    for mids in valid.values():
        all_middles.update(mids)
    mid_vectors = {m: middle_to_atom_vector(m) for m in all_middles}

    # Observed mean pairwise cosine within records
    def record_coherence(mids):
        vecs = [mid_vectors[m] for m in mids if m in mid_vectors]
        if len(vecs) < 2:
            return None
        sims = []
        for i in range(len(vecs)):
            for j in range(i + 1, len(vecs)):
                sims.append(cosine_sim(vecs[i], vecs[j]))
        return np.mean(sims) if sims else None

    obs_coherences = []
    for mids in valid.values():
        c = record_coherence(mids)
        if c is not None:
            obs_coherences.append(c)
    obs_mean = np.mean(obs_coherences)
    print(f"  Observed mean coherence: {obs_mean:.4f}")

    # Pool all MIDDLEs for shuffling
    all_mids = []
    record_sizes = []
    for mids in valid.values():
        all_mids.extend(mids)
        record_sizes.append(len(mids))
    all_mids_arr = np.array(all_mids)

    # Null: shuffle MIDDLEs across records
    null_means = []
    for _ in range(N_PERM):
        shuffled = all_mids_arr.copy()
        rng.shuffle(shuffled)
        idx = 0
        perm_cohs = []
        for sz in record_sizes:
            chunk = list(shuffled[idx:idx+sz])
            c = record_coherence(chunk)
            if c is not None:
                perm_cohs.append(c)
            idx += sz
        null_means.append(np.mean(perm_cohs) if perm_cohs else 0.0)

    null_means = np.array(null_means)
    p_val = float(np.mean(null_means >= obs_mean))
    effect = float((obs_mean - np.mean(null_means)) / (np.std(null_means) + 1e-12))

    vrd = verdict(p_val)
    dt_main = time.time() - t0
    print(f"  Null mean: {np.mean(null_means):.4f} +/- {np.std(null_means):.4f}")
    print(f"  Effect (Cohen d): {effect:.3f}")
    print(f"  p = {p_val:.6f}  -> {vrd}")

    # Redundancy check: regress out T1 category signal
    residual_effect = None
    if t1_result.get('verdict') in ('PASS', 'WEAK'):
        # Control for category: within same-category pairs only
        records_with_cats = defaultdict(list)
        for tok in a_tokens:
            mid = tok['middle']
            cat = tok['category']
            if tok['token_class'] == 'PP' and mid and cat:
                records_with_cats[(tok['folio'], tok['line'])].append((mid, cat))

        same_cat_sims = []
        for pairs in records_with_cats.values():
            if len(pairs) < 2:
                continue
            for i in range(len(pairs)):
                for j in range(i + 1, len(pairs)):
                    if pairs[i][1] == pairs[j][1]:  # Same category
                        v1 = mid_vectors.get(pairs[i][0])
                        v2 = mid_vectors.get(pairs[j][0])
                        if v1 is not None and v2 is not None:
                            same_cat_sims.append(cosine_sim(v1, v2))

        if same_cat_sims:
            # Compare to all-pairs from null
            residual_effect = float(np.mean(same_cat_sims) - np.mean(null_means))
            print(f"  Residual (same-cat pairs): {np.mean(same_cat_sims):.4f}")
            print(f"  Residual vs null: {residual_effect:.4f}")
        else:
            print("  Residual check: no same-category pairs found")
    else:
        print("  Residual check: T1 not significant, skipping")

    print(f"  ({dt_main + (time.time() - t0 - dt_main):.1f}s)")

    return {
        'test': 'T7', 'verdict': vrd, 'p_value': p_val,
        'obs_mean_coherence': float(obs_mean),
        'null_mean_coherence': float(np.mean(null_means)),
        'null_std': float(np.std(null_means)),
        'effect_cohen_d': effect,
        'n_records': n_records,
        'residual_effect': residual_effect,
    }


# ================================================================
# T8: A Section Atom Balance vs B Section Profiles
# ================================================================
def test_t8(a_tokens, b_tokens, pp_middles):
    """Do A folios show atom-level section differentiation?"""
    print("\n=== T8: A Section Atom Balance vs B Section Profiles ===")
    t0 = time.time()

    # Per A section: compute atom frequency vector across all PP MIDDLE atoms
    a_section_atoms = defaultdict(lambda: np.zeros(len(AXIS_NAMES)))
    axis_idx = {name: i for i, name in enumerate(AXIS_NAMES)}

    for tok in a_tokens:
        mid = tok['middle']
        sec = tok['section']
        if tok['token_class'] != 'PP' or not mid or not sec:
            continue
        for ch in mid:
            ax = AXIS.get(ch)
            if ax:
                a_section_atoms[sec][axis_idx[ax]] += 1

    # Normalize to fractions
    a_section_profiles = {}
    for sec, vec in a_section_atoms.items():
        total = vec.sum()
        if total > 0:
            a_section_profiles[sec] = vec / total
        else:
            a_section_profiles[sec] = vec

    print(f"  A sections with atoms: {list(a_section_profiles.keys())}")
    for sec, prof in sorted(a_section_profiles.items()):
        counts = a_section_atoms[sec]
        total = counts.sum()
        detail = ", ".join(f"{name}={prof[i]:.3f}" for i, name in enumerate(AXIS_NAMES))
        print(f"    {sec} (n={int(total)}): {detail}")

    # Kruskal-Wallis per atom across A sections
    # Need per-folio atom profiles
    a_folio_section = {}
    a_folio_atoms = defaultdict(lambda: Counter())
    for tok in a_tokens:
        mid = tok['middle']
        if tok['token_class'] != 'PP' or not mid:
            continue
        folio = tok['folio']
        sec = tok['section']
        if sec:
            a_folio_section[folio] = sec
        for ch in mid:
            ax = AXIS.get(ch)
            if ax:
                a_folio_atoms[folio][ax] += 1

    # Convert to fraction vectors per folio
    folio_profiles = {}
    for folio, counts in a_folio_atoms.items():
        total = sum(counts.values())
        if total >= 5:  # Minimum 5 atoms for stable profile
            folio_profiles[folio] = {ax: counts.get(ax, 0) / total for ax in AXIS_NAMES}

    # Filter to sections with 3+ folios
    sec_folios = defaultdict(list)
    for folio, profile in folio_profiles.items():
        sec = a_folio_section.get(folio)
        if sec:
            sec_folios[sec].append((folio, profile))

    valid_secs = {s: fs for s, fs in sec_folios.items() if len(fs) >= 3}
    print(f"  Sections with 3+ folios: {list(valid_secs.keys())}")

    if len(valid_secs) < 2:
        print("  SKIP: Need 2+ sections with enough folios")
        return {'test': 'T8', 'verdict': 'SKIP', 'reason': 'too_few_sections'}

    # Kruskal-Wallis per axis
    kw_results = {}
    sec_names = sorted(valid_secs.keys())
    for ax in AXIS_NAMES:
        groups = []
        for sec in sec_names:
            vals = [p[ax] for _, p in valid_secs[sec]]
            groups.append(vals)
        if all(len(g) >= 2 for g in groups):
            stat, p = sp_stats.kruskal(*groups)
            kw_results[ax] = {'H': float(stat), 'p': float(p),
                              'means': {sec: float(np.mean([p[ax] for _, p in valid_secs[sec]]))
                                        for sec in sec_names}}
        else:
            kw_results[ax] = {'skip': 'too_few'}

    print("  Kruskal-Wallis per axis:")
    n_sig = 0
    for ax in AXIS_NAMES:
        r = kw_results[ax]
        if 'H' in r:
            sig = '*' if r['p'] < 0.05 else ''
            bsig = '**' if r['p'] < BONFERRONI_P else ''
            flag = bsig or sig
            if r['p'] < 0.05:
                n_sig += 1
            means_str = ", ".join(f"{s}={r['means'][s]:.3f}" for s in sec_names)
            print(f"    {ax:12s}: H={r['H']:.2f} p={r['p']:.4f} {flag}  [{means_str}]")
        else:
            print(f"    {ax:12s}: skipped")

    # B-side section profiles for correlation
    b_section_atoms = defaultdict(lambda: np.zeros(len(AXIS_NAMES)))
    for tok in b_tokens:
        mid = tok['middle']
        sec = tok['section']
        if tok['token_class'] != 'PP' or not mid or not sec:
            continue
        for ch in mid:
            ax = AXIS.get(ch)
            if ax:
                b_section_atoms[sec][axis_idx[ax]] += 1

    b_section_profiles = {}
    for sec, vec in b_section_atoms.items():
        total = vec.sum()
        if total > 0:
            b_section_profiles[sec] = vec / total

    # Cross-system correlation: do A and B section profiles correlate?
    shared_secs = sorted(set(a_section_profiles.keys()) & set(b_section_profiles.keys()))
    cross_corr = None
    if len(shared_secs) >= 3:
        a_flat = np.concatenate([a_section_profiles[s] for s in shared_secs])
        b_flat = np.concatenate([b_section_profiles[s] for s in shared_secs])
        r_val, r_p = sp_stats.pearsonr(a_flat, b_flat)
        cross_corr = {'r': float(r_val), 'p': float(r_p),
                       'shared_sections': shared_secs}
        print(f"  A-B section profile correlation: r={r_val:.3f}, p={r_p:.4f}")
    else:
        print(f"  Cross-system: only {len(shared_secs)} shared sections, skipping")

    # Overall verdict: any axis significant at Bonferroni?
    any_bonf = any(r.get('p', 1.0) < BONFERRONI_P for r in kw_results.values())
    overall_p = min((r.get('p', 1.0) for r in kw_results.values()), default=1.0)
    vrd = 'PASS' if any_bonf else ('WEAK' if n_sig >= 2 else 'FAIL')

    dt = time.time() - t0
    print(f"  Overall: {n_sig} axes at p<0.05, any Bonferroni={any_bonf}")
    print(f"  Verdict: {vrd}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T8', 'verdict': vrd,
        'min_p': float(overall_p),
        'n_sig_axes': n_sig, 'any_bonferroni': any_bonf,
        'kruskal_wallis': kw_results,
        'a_section_profiles': {s: p.tolist() for s, p in a_section_profiles.items()},
        'b_section_profiles': {s: p.tolist() for s, p in b_section_profiles.items()},
        'cross_system_correlation': cross_corr,
        'axis_names': AXIS_NAMES,
        'sections_tested': sec_names if len(valid_secs) >= 2 else [],
        'n_folios_per_section': {s: len(fs) for s, fs in valid_secs.items()},
    }


# ================================================================
# MAIN
# ================================================================
def main():
    print("=" * 60)
    print("Phase 452: A_CATEGORY_SCATTERSHOT")
    print("8-test battery: category system vs A registry structure")
    print("=" * 60)

    t_start = time.time()
    rng = np.random.RandomState(SEED)

    # Load data
    print("\n--- Loading data ---")
    (a_tokens, b_tokens, mid_to_cat, ri_middles, pp_middles,
     bridge_middles, dark_middles) = load_all_data()

    # Category coverage stats
    n_a_with_cat = sum(1 for t in a_tokens if t['category'])
    n_a_pp_with_cat = sum(1 for t in a_tokens
                          if t['token_class'] == 'PP' and t['category'])
    n_a_pp = sum(1 for t in a_tokens if t['token_class'] == 'PP')
    print(f"\n  A tokens with category: {n_a_with_cat} / {len(a_tokens)}")
    print(f"  A PP tokens with category: {n_a_pp_with_cat} / {n_a_pp} "
          f"({100*n_a_pp_with_cat/n_a_pp:.1f}%)")

    results = {
        'phase': 'A_CATEGORY_SCATTERSHOT',
        'phase_number': 452,
        'n_perm': N_PERM,
        'bonferroni_p': BONFERRONI_P,
        'seed': SEED,
        'data_summary': {
            'n_a_tokens': len(a_tokens),
            'n_b_tokens': len(b_tokens),
            'n_middles_with_category': len(mid_to_cat),
            'n_pp_middles': len(pp_middles),
            'n_ri_middles': len(ri_middles),
            'n_bridge_middles': len(bridge_middles),
            'n_dark_middles': len(dark_middles),
            'a_pp_category_coverage': f"{100*n_a_pp_with_cat/n_a_pp:.1f}%",
        },
        'tests': {},
    }

    # Run tests
    t1 = test_t1(a_tokens, rng)
    results['tests']['T1'] = t1

    t2 = test_t2(a_tokens, b_tokens, pp_middles, rng)
    results['tests']['T2'] = t2

    t3 = test_t3(a_tokens, pp_middles, mid_to_cat)
    results['tests']['T3'] = t3

    t4 = test_t4(a_tokens, rng)
    results['tests']['T4'] = t4

    t5 = test_t5(bridge_middles, dark_middles, mid_to_cat)
    results['tests']['T5'] = t5

    t6 = test_t6(a_tokens, rng)
    results['tests']['T6'] = t6

    t7 = test_t7(a_tokens, mid_to_cat, t1, rng)
    results['tests']['T7'] = t7

    t8 = test_t8(a_tokens, b_tokens, pp_middles)
    results['tests']['T8'] = t8

    # Summary
    all_tests = [t1, t2, t3, t4, t5, t6, t7, t8]
    pass_count = sum(1 for t in all_tests if t.get('verdict') == 'PASS')
    weak_count = sum(1 for t in all_tests if t.get('verdict') == 'WEAK')
    fail_count = sum(1 for t in all_tests if t.get('verdict') == 'FAIL')
    skip_count = sum(1 for t in all_tests if t.get('verdict') == 'SKIP')

    if pass_count >= 4:
        overall = 'CATEGORY_ORGANIZED'
    elif pass_count >= 2:
        overall = 'PARTIAL_SIGNAL'
    else:
        overall = 'NULL'

    results['summary'] = {
        'pass': pass_count,
        'weak': weak_count,
        'fail': fail_count,
        'skip': skip_count,
        'overall_verdict': overall,
    }

    total_time = time.time() - t_start
    results['runtime_seconds'] = round(total_time, 1)

    # Print summary table
    print("\n" + "=" * 60)
    print("SUMMARY TABLE")
    print("=" * 60)
    print(f"{'Test':<6} {'Verdict':<10} {'p-value':<12} {'Effect':<10}")
    print("-" * 40)
    for t in all_tests:
        name = t['test']
        vrd = t.get('verdict', '?')
        p = t.get('p_value', t.get('min_p', '-'))
        if isinstance(p, float):
            p_str = f"{p:.6f}"
        else:
            p_str = str(p)
        eff = t.get('effect_cohen_d', t.get('cramers_v', '-'))
        if isinstance(eff, float):
            eff_str = f"{eff:.3f}"
        else:
            eff_str = str(eff)
        print(f"{name:<6} {vrd:<10} {p_str:<12} {eff_str:<10}")

    print(f"\nPASS: {pass_count}, WEAK: {weak_count}, FAIL: {fail_count}, SKIP: {skip_count}")
    print(f"OVERALL: {overall}")
    print(f"Runtime: {total_time:.1f}s")

    # Save
    out_path = RESULTS_DIR / "a_category_scattershot.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
