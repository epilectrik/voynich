"""
Phase 525: The e->y Safe Pathway and Recovery Architecture
===========================================================

C1448 identified e->y as the largest single safe frame in the grammar: 3,475
tokens at 0% hazard. C105 established that 54.7% of recovery paths converge
on the `e` operator. This phase investigates whether e->y is the backbone of
the grammar's recovery architecture.

Tests:
  T1.  e->y token inventory (MIDDLEs, modifiers, e-depth)
  T2.  e->y operational category profile
  T3.  e->y and recovery/post-hazard deployment
  T4.  e->y positional profile within lines
  T5.  e->y and PREFIX channels
  T6.  e->y and suffix behavior (mode, two-level closure)
  T7.  e->y as stability anchor: transition analysis (macro-state, before/after)
  T8.  e->y vs other safe frames (comparative safety analysis)
  T9.  e->y and paragraph structure
  T10. e->y and program forgiveness (AXM attractor correlation)

Output: phases/EY_SAFE_PATHWAY/results/ey_safe_pathway.json
"""

import sys
import io
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2_contingency, spearmanr, mannwhitneyu

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# ATOM AND SLOT DEFINITIONS (from C1393, C1394, C1408)
# ============================================================
HEAD_SET = {'a', 'e', 'o', 'k', 't'}
TERM_SET = {'l', 'r', 'h', 'y', 'm', 'n', 'k', 't'}
EXTENSIBLE = {'e', 'i'}

# Hazard categories (C1280)
HAZARD_CATS = {'FLOW', 'CONTAINMENT'}

# Terminal suffix set for Mode A identification (C1229, C1231)
TERMINAL_SUFFIXES = {'edy', 'ey', 'eey', 'dy', 'y', 'hy', 'ry', 'ly', 'eedy', 'chy', 'shy'}

# The 17 forbidden MIDDLE-level transitions (from C109, C627)
FORBIDDEN_PAIRS = set([
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'),
    ('dy', 'aiin'), ('dy', 'chey'),
    ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'),
    ('ar', 'dal'), ('c', 'ee'),
    ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o'),
])


# ============================================================
# DATA LOADING
# ============================================================

def load_token_class_map():
    """Load token -> 49-class mapping."""
    path = PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {t: int(c) for t, c in data['token_to_class'].items()}


def load_macro_state_map():
    """Load class -> macro state mapping from decoder_maps.json."""
    path = PROJECT_ROOT / 'data/decoder_maps.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    entries = data['maps']['macro_state']['entries']
    return {k: v['value'] for k, v in entries.items()}


# ============================================================
# MIDDLE ATOM DECOMPOSITION
# ============================================================

def atomize_middle(middle):
    """Split MIDDLE into atoms, respecting e/i extensibility."""
    atoms = []
    i = 0
    while i < len(middle):
        ch = middle[i]
        if ch in EXTENSIBLE:
            run = ch
            while i + 1 < len(middle) and middle[i + 1] == ch:
                run += ch
                i += 1
            atoms.append(run)
        else:
            atoms.append(ch)
        i += 1
    return atoms


def get_head_term(middle):
    """Get HEAD and TERMINAL atoms from MIDDLE."""
    if not middle:
        return None, None
    atoms = atomize_middle(middle)
    head = atoms[0]
    term = atoms[-1] if len(atoms) > 1 else None
    return head, term


def is_ey_middle(middle):
    """Check if MIDDLE has e-HEAD and y-TERMINAL."""
    head, term = get_head_term(middle)
    # HEAD must start with 'e'
    if head is None or head[0] != 'e':
        return False
    # TERM must be 'y'
    if term != 'y':
        return False
    return True


def get_e_depth(middle):
    """Get the e-depth of an e-HEAD MIDDLE (count of consecutive e's at start)."""
    atoms = atomize_middle(middle)
    head = atoms[0]
    if head[0] == 'e':
        return len(head)  # 'e'=1, 'ee'=2, 'eee'=3
    return 0


def get_modifiers(middle):
    """Get modifier atoms between HEAD and TERM."""
    atoms = atomize_middle(middle)
    if len(atoms) <= 2:
        return []
    return atoms[1:-1]


# ============================================================
# DATA COLLECTION
# ============================================================

def collect_b_tokens():
    """Collect all Currier B tokens with morphological decomposition and adjacency."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    token_class_map = load_token_class_map()
    macro_map = load_macro_state_map()

    tokens_by_folio_line = defaultdict(list)
    all_tokens = []
    folio_line_order = []  # track order of folio-line keys

    for tok in tx.currier_b():
        word = tok.word
        if not word or not word.strip() or '*' in word:
            continue

        m = morph.extract(word)
        if not m or not m.middle:
            continue

        middle = m.middle
        category = cc.classify(middle)
        head, term = get_head_term(middle)
        token_class = token_class_map.get(word)
        macro_state = macro_map.get(str(token_class)) if token_class is not None else None

        suffix = m.suffix or ''
        suffix_mode = 'A' if suffix in TERMINAL_SUFFIXES else 'B'

        is_hazard_cat = category in HAZARD_CATS

        entry = {
            'word': word,
            'folio': tok.folio,
            'line': tok.line,
            'prefix': m.prefix,
            'middle': middle,
            'suffix': suffix,
            'has_suffix': bool(suffix),
            'articulator': m.articulator,
            'category': category,
            'token_class': token_class,
            'macro_state': macro_state,
            'suffix_mode': suffix_mode,
            'head_atom': head,
            'term_atom': term,
            'is_ey': is_ey_middle(middle),
            'e_depth': get_e_depth(middle) if head and head[0] == 'e' else 0,
            'is_hazard_cat': is_hazard_cat,
        }

        key = (tok.folio, tok.line)
        if key not in tokens_by_folio_line:
            folio_line_order.append(key)
        tokens_by_folio_line[key].append(entry)
        all_tokens.append(entry)

    # Compute line positions
    for key, line_tokens in tokens_by_folio_line.items():
        n = len(line_tokens)
        for idx, entry in enumerate(line_tokens):
            if n <= 1:
                entry['line_pos_frac'] = 0.5
                entry['line_quintile'] = 2
            else:
                frac = idx / (n - 1)
                entry['line_pos_frac'] = frac
                entry['line_quintile'] = min(int(frac * 5), 4)
            entry['is_line_initial'] = (idx == 0)
            entry['is_line_final'] = (idx == n - 1)

    # Determine paragraph structure: gallows-initial lines
    folio_paragraphs = defaultdict(list)  # folio -> list of paragraph dicts
    gallows_chars = {'k', 'p', 'f', 't'}
    current_folio = None
    current_para_lines = []
    para_idx = 0

    for key in folio_line_order:
        folio, line = key
        if folio != current_folio:
            # Save previous paragraph
            if current_para_lines and current_folio:
                folio_paragraphs[current_folio].append({
                    'para_idx': para_idx,
                    'lines': current_para_lines,
                })
            current_folio = folio
            current_para_lines = [key]
            para_idx = 0
            continue

        # Check if this line starts a new paragraph (gallows-initial)
        line_tokens = tokens_by_folio_line[key]
        if line_tokens:
            first_word = line_tokens[0]['word']
            first_char = first_word[0] if first_word else ''
            if first_char in gallows_chars and len(current_para_lines) > 0:
                # Save current paragraph
                folio_paragraphs[current_folio].append({
                    'para_idx': para_idx,
                    'lines': current_para_lines,
                })
                para_idx += 1
                current_para_lines = [key]
                continue
        current_para_lines.append(key)

    # Save last paragraph
    if current_para_lines and current_folio:
        folio_paragraphs[current_folio].append({
            'para_idx': para_idx,
            'lines': current_para_lines,
        })

    # Annotate tokens with paragraph info
    for folio, paras in folio_paragraphs.items():
        n_paras = len(paras)
        for para in paras:
            n_lines = len(para['lines'])
            for line_idx, key in enumerate(para['lines']):
                for entry in tokens_by_folio_line[key]:
                    entry['para_idx'] = para['para_idx']
                    entry['n_paras_in_folio'] = n_paras
                    entry['line_in_para'] = line_idx
                    entry['n_lines_in_para'] = n_lines
                    entry['is_header_line'] = (line_idx == 0)

    # Build adjacency pairs
    adjacency_pairs = []
    for key in folio_line_order:
        line_tokens = tokens_by_folio_line[key]
        for i in range(len(line_tokens) - 1):
            src = line_tokens[i]
            tgt = line_tokens[i + 1]
            pair = (src['middle'], tgt['middle'])
            is_forbidden = pair in FORBIDDEN_PAIRS
            adjacency_pairs.append({
                'src': src,
                'tgt': tgt,
                'src_middle': src['middle'],
                'tgt_middle': tgt['middle'],
                'is_forbidden': is_forbidden,
            })

    return all_tokens, adjacency_pairs, tokens_by_folio_line, folio_paragraphs


# ============================================================
# STATISTICAL HELPERS
# ============================================================

def cramers_v(contingency_table):
    """Compute Cramer's V from a contingency table."""
    try:
        chi2, p, dof, expected = chi2_contingency(contingency_table)
        n = np.sum(contingency_table)
        min_dim = min(contingency_table.shape) - 1
        if min_dim <= 0 or n <= 0:
            return 0, 1.0
        v = math.sqrt(chi2 / (n * min_dim))
        return v, p
    except Exception:
        return 0, 1.0


def enrichment(observed, expected):
    """Compute enrichment ratio."""
    if expected == 0:
        return float('inf') if observed > 0 else 1.0
    return observed / expected


def safe_ratio(a, b):
    if b == 0:
        return float('inf') if a > 0 else 0.0
    return a / b


# ============================================================
# T1: e->y TOKEN INVENTORY
# ============================================================

def test_t1_ey_token_inventory(all_tokens):
    """T1: Catalog e->y MIDDLEs, modifiers, e-depth distribution."""
    print("  T1: e->y token inventory...")

    ey_tokens = [t for t in all_tokens if t['is_ey']]
    non_ey = [t for t in all_tokens if not t['is_ey']]

    # Count by MIDDLE
    middle_counts = Counter(t['middle'] for t in ey_tokens)
    top_middles = middle_counts.most_common(20)

    # e-depth distribution
    depth_counts = Counter(t['e_depth'] for t in ey_tokens)

    # Modifier distribution
    mod_counts = Counter()
    for t in ey_tokens:
        mods = get_modifiers(t['middle'])
        for mod in mods:
            mod_counts[mod] += 1
    if not any(get_modifiers(t['middle']) for t in ey_tokens):
        bare_ey = sum(1 for t in ey_tokens if len(atomize_middle(t['middle'])) == 2)
        mod_ey = len(ey_tokens) - bare_ey
    else:
        bare_ey = sum(1 for t in ey_tokens if not get_modifiers(t['middle']))
        mod_ey = len(ey_tokens) - bare_ey

    # Compare e->y diversity with other e-TERM combinations
    e_head_tokens = [t for t in all_tokens if t['head_atom'] and t['head_atom'][0] == 'e']
    e_term_dist = Counter(t['term_atom'] for t in e_head_tokens)

    # e->y token diversity (unique MIDDLEs)
    ey_unique = len(set(t['middle'] for t in ey_tokens))
    e_head_unique = len(set(t['middle'] for t in e_head_tokens))

    result = {
        'ey_total_tokens': len(ey_tokens),
        'ey_unique_middles': ey_unique,
        'ey_fraction_of_corpus': round(len(ey_tokens) / len(all_tokens), 4),
        'top_ey_middles': [{'middle': m, 'count': c} for m, c in top_middles],
        'e_depth_distribution': {str(k): v for k, v in sorted(depth_counts.items())},
        'bare_ey_count': bare_ey,
        'modified_ey_count': mod_ey,
        'modifier_counts': dict(mod_counts.most_common(10)),
        'e_head_terminal_dist': {str(k): v for k, v in e_term_dist.most_common()},
        'e_head_total': len(e_head_tokens),
        'ey_fraction_of_e_head': round(len(ey_tokens) / max(len(e_head_tokens), 1), 4),
    }

    print(f"    e->y: {len(ey_tokens)} tokens ({result['ey_fraction_of_corpus']:.1%} of corpus)")
    print(f"    Unique MIDDLEs: {ey_unique}")
    print(f"    Top 5: {top_middles[:5]}")
    print(f"    e-depth: {dict(sorted(depth_counts.items()))}")
    print(f"    Bare (e+y only): {bare_ey}, Modified: {mod_ey}")
    print(f"    e->y is {result['ey_fraction_of_e_head']:.1%} of all e-HEAD tokens")

    return result


# ============================================================
# T2: e->y OPERATIONAL CATEGORY PROFILE
# ============================================================

def test_t2_ey_category_profile(all_tokens):
    """T2: Category distribution of e->y vs overall and other e-HEAD frames."""
    print("  T2: e->y operational category profile...")

    ey_tokens = [t for t in all_tokens if t['is_ey']]
    non_ey = [t for t in all_tokens if not t['is_ey']]

    # Category distributions
    ey_cats = Counter(t['category'] for t in ey_tokens)
    all_cats = Counter(t['category'] for t in all_tokens)
    non_ey_cats = Counter(t['category'] for t in non_ey)

    total_ey = len(ey_tokens)
    total_all = len(all_tokens)

    # Enrichment by category
    cat_enrichment = {}
    categories = sorted(k for k in set(all_cats.keys()) if k is not None)
    for cat in categories:
        ey_rate = ey_cats.get(cat, 0) / max(total_ey, 1)
        all_rate = all_cats.get(cat, 0) / max(total_all, 1)
        cat_enrichment[cat] = {
            'ey_count': ey_cats.get(cat, 0),
            'ey_rate': round(ey_rate, 4),
            'corpus_rate': round(all_rate, 4),
            'enrichment': round(enrichment(ey_rate, all_rate), 3),
        }

    # Compare to other e-HEAD frames
    e_head_tokens = [t for t in all_tokens if t['head_atom'] and t['head_atom'][0] == 'e']
    other_e_frames = defaultdict(list)
    for t in e_head_tokens:
        term = t['term_atom']
        if term == 'y':
            other_e_frames['e->y'].append(t)
        elif term:
            other_e_frames[f'e->{term}'].append(t)
        else:
            other_e_frames['e->bare'].append(t)

    e_frame_cats = {}
    for frame, tokens in sorted(other_e_frames.items()):
        if len(tokens) < 20:
            continue
        cats = Counter(t['category'] for t in tokens)
        total = len(tokens)
        e_frame_cats[frame] = {
            'n': total,
            'cats': {c: round(n/total, 3) for c, n in cats.most_common()},
            'hazard_rate': round(sum(1 for t in tokens if t['is_hazard_cat']) / total, 4),
        }

    # e->y hazard rate
    ey_hazard = sum(1 for t in ey_tokens if t['is_hazard_cat'])
    ey_hazard_rate = ey_hazard / max(total_ey, 1)

    result = {
        'ey_category_enrichment': cat_enrichment,
        'ey_hazard_count': ey_hazard,
        'ey_hazard_rate': round(ey_hazard_rate, 4),
        'corpus_hazard_rate': round(sum(1 for t in all_tokens if t['is_hazard_cat']) / total_all, 4),
        'e_frame_category_profiles': e_frame_cats,
    }

    print(f"    e->y hazard rate: {ey_hazard_rate:.4f} ({ey_hazard}/{total_ey})")
    print(f"    Corpus hazard rate: {result['corpus_hazard_rate']:.4f}")
    for cat, info in sorted(cat_enrichment.items(), key=lambda x: -x[1]['enrichment']):
        if info['ey_count'] > 0:
            print(f"      {cat}: {info['ey_rate']:.3f} vs {info['corpus_rate']:.3f} = {info['enrichment']:.2f}x")

    return result


# ============================================================
# T3: e->y AND RECOVERY / POST-HAZARD DEPLOYMENT
# ============================================================

def test_t3_ey_recovery(all_tokens, adjacency_pairs):
    """T3: e->y deployment in post-hazard recovery positions."""
    print("  T3: e->y and recovery paths...")

    # Define "hazard-adjacent" tokens:
    # Source tokens in forbidden pairs, target tokens in forbidden pairs
    # Also tokens with hazard categories (FLOW/CONTAINMENT)
    hazard_source_middles = set()
    hazard_target_middles = set()
    for src, tgt in FORBIDDEN_PAIRS:
        hazard_source_middles.add(src)
        hazard_target_middles.add(tgt)

    # Find post-hazard tokens: tokens immediately following a hazard-category token
    post_hazard_tokens = []
    post_safe_tokens = []
    post_forbidden_target = []
    normal_tokens = []

    for pair in adjacency_pairs:
        src = pair['src']
        tgt = pair['tgt']

        if src['is_hazard_cat']:
            post_hazard_tokens.append(tgt)
        else:
            post_safe_tokens.append(tgt)

        if src['middle'] in hazard_source_middles:
            post_forbidden_target.append(tgt)

    # e->y rates in different contexts
    def ey_rate(tokens):
        if not tokens:
            return 0, 0, 0
        ey_count = sum(1 for t in tokens if t['is_ey'])
        return ey_count, len(tokens), round(ey_count / len(tokens), 4) if tokens else 0

    ey_post_hazard = ey_rate(post_hazard_tokens)
    ey_post_safe = ey_rate(post_safe_tokens)
    ey_post_forbidden = ey_rate(post_forbidden_target)
    ey_overall = ey_rate(all_tokens)

    # Enrichment of e->y in post-hazard
    post_hazard_enrichment = enrichment(ey_post_hazard[2], ey_overall[2])
    post_safe_enrichment = enrichment(ey_post_safe[2], ey_overall[2])

    # What comes AFTER e->y? (recovery exit analysis)
    post_ey_tokens = []
    for pair in adjacency_pairs:
        if pair['src']['is_ey']:
            post_ey_tokens.append(pair['tgt'])

    post_ey_cats = Counter(t['category'] for t in post_ey_tokens)
    post_ey_total = len(post_ey_tokens)
    post_ey_hazard = sum(1 for t in post_ey_tokens if t['is_hazard_cat'])

    # What comes BEFORE e->y? (recovery entry analysis)
    pre_ey_tokens = []
    for pair in adjacency_pairs:
        if pair['tgt']['is_ey']:
            pre_ey_tokens.append(pair['src'])

    pre_ey_cats = Counter(t['category'] for t in pre_ey_tokens)
    pre_ey_hazard = sum(1 for t in pre_ey_tokens if t['is_hazard_cat'])
    pre_ey_total = len(pre_ey_tokens)

    # Mann-Whitney test: is e->y specifically enriched after hazard?
    # Compare e->y rates post-hazard vs post-safe
    try:
        # Binary: 1 if e->y, 0 if not
        post_haz_binary = [1 if t['is_ey'] else 0 for t in post_hazard_tokens]
        post_safe_binary = [1 if t['is_ey'] else 0 for t in post_safe_tokens]
        if len(post_haz_binary) > 10 and len(post_safe_binary) > 10:
            mw_stat, mw_p = mannwhitneyu(post_haz_binary, post_safe_binary, alternative='two-sided')
        else:
            mw_stat, mw_p = 0, 1.0
    except Exception:
        mw_stat, mw_p = 0, 1.0

    result = {
        'ey_rate_overall': {'count': ey_overall[0], 'total': ey_overall[1], 'rate': ey_overall[2]},
        'ey_rate_post_hazard': {'count': ey_post_hazard[0], 'total': ey_post_hazard[1], 'rate': ey_post_hazard[2]},
        'ey_rate_post_safe': {'count': ey_post_safe[0], 'total': ey_post_safe[1], 'rate': ey_post_safe[2]},
        'ey_rate_post_forbidden_source': {'count': ey_post_forbidden[0], 'total': ey_post_forbidden[1], 'rate': ey_post_forbidden[2]},
        'post_hazard_enrichment': round(post_hazard_enrichment, 3),
        'post_safe_enrichment': round(post_safe_enrichment, 3),
        'mann_whitney_stat': round(float(mw_stat), 2),
        'mann_whitney_p': round(float(mw_p), 4),
        'post_ey_category_dist': {c: round(n/max(post_ey_total, 1), 3) for c, n in post_ey_cats.most_common()},
        'post_ey_hazard_rate': round(post_ey_hazard / max(post_ey_total, 1), 4),
        'post_ey_total': post_ey_total,
        'pre_ey_category_dist': {c: round(n/max(pre_ey_total, 1), 3) for c, n in pre_ey_cats.most_common()},
        'pre_ey_hazard_rate': round(pre_ey_hazard / max(pre_ey_total, 1), 4),
        'pre_ey_total': pre_ey_total,
    }

    print(f"    e->y rate overall: {ey_overall[2]:.4f}")
    print(f"    e->y rate post-hazard: {ey_post_hazard[2]:.4f} (enrichment: {post_hazard_enrichment:.2f}x)")
    print(f"    e->y rate post-safe: {ey_post_safe[2]:.4f} (enrichment: {post_safe_enrichment:.2f}x)")
    print(f"    Mann-Whitney p={mw_p:.4f}")
    print(f"    Post-e->y hazard rate: {result['post_ey_hazard_rate']:.4f}")
    print(f"    Pre-e->y hazard rate: {result['pre_ey_hazard_rate']:.4f}")

    return result


# ============================================================
# T4: e->y POSITIONAL PROFILE
# ============================================================

def test_t4_ey_positional_profile(all_tokens):
    """T4: Where do e->y tokens appear within lines?"""
    print("  T4: e->y positional profile...")

    ey_tokens = [t for t in all_tokens if t['is_ey']]
    non_ey = [t for t in all_tokens if not t['is_ey']]

    # Line position quintiles
    ey_quint = Counter(t.get('line_quintile', -1) for t in ey_tokens)
    all_quint = Counter(t.get('line_quintile', -1) for t in all_tokens)

    total_ey = len(ey_tokens)
    total_all = len(all_tokens)

    quint_enrichment = {}
    for q in range(5):
        ey_rate = ey_quint.get(q, 0) / max(total_ey, 1)
        all_rate = all_quint.get(q, 0) / max(total_all, 1)
        quint_enrichment[f'Q{q}'] = {
            'ey_count': ey_quint.get(q, 0),
            'ey_rate': round(ey_rate, 4),
            'corpus_rate': round(all_rate, 4),
            'enrichment': round(enrichment(ey_rate, all_rate), 3),
        }

    # Line-initial and line-final rates
    ey_initial = sum(1 for t in ey_tokens if t.get('is_line_initial', False))
    ey_final = sum(1 for t in ey_tokens if t.get('is_line_final', False))
    all_initial = sum(1 for t in all_tokens if t.get('is_line_initial', False))
    all_final = sum(1 for t in all_tokens if t.get('is_line_final', False))

    ey_initial_rate = ey_initial / max(total_ey, 1)
    ey_final_rate = ey_final / max(total_ey, 1)
    all_initial_rate = all_initial / max(total_all, 1)
    all_final_rate = all_final / max(total_all, 1)

    # Compare to e-HEAD overall and y-TERM overall
    e_head = [t for t in all_tokens if t['head_atom'] and t['head_atom'][0] == 'e']
    y_term = [t for t in all_tokens if t['term_atom'] == 'y']

    e_head_quint = Counter(t.get('line_quintile', -1) for t in e_head)
    y_term_quint = Counter(t.get('line_quintile', -1) for t in y_term)

    # Header vs body line
    ey_header = sum(1 for t in ey_tokens if t.get('is_header_line', False))
    ey_body = total_ey - ey_header
    all_header = sum(1 for t in all_tokens if t.get('is_header_line', False))
    all_body = total_all - all_header

    ey_header_rate = ey_header / max(total_ey, 1)
    all_header_rate = all_header / max(total_all, 1)

    # Mean position
    ey_mean_pos = np.mean([t['line_pos_frac'] for t in ey_tokens if 'line_pos_frac' in t])
    all_mean_pos = np.mean([t['line_pos_frac'] for t in all_tokens if 'line_pos_frac' in t])
    e_head_mean_pos = np.mean([t['line_pos_frac'] for t in e_head if 'line_pos_frac' in t]) if e_head else 0
    y_term_mean_pos = np.mean([t['line_pos_frac'] for t in y_term if 'line_pos_frac' in t]) if y_term else 0

    result = {
        'quintile_enrichment': quint_enrichment,
        'ey_mean_position': round(float(ey_mean_pos), 4),
        'corpus_mean_position': round(float(all_mean_pos), 4),
        'e_head_mean_position': round(float(e_head_mean_pos), 4),
        'y_term_mean_position': round(float(y_term_mean_pos), 4),
        'ey_initial_rate': round(ey_initial_rate, 4),
        'corpus_initial_rate': round(all_initial_rate, 4),
        'ey_initial_enrichment': round(enrichment(ey_initial_rate, all_initial_rate), 3),
        'ey_final_rate': round(ey_final_rate, 4),
        'corpus_final_rate': round(all_final_rate, 4),
        'ey_final_enrichment': round(enrichment(ey_final_rate, all_final_rate), 3),
        'ey_header_rate': round(ey_header_rate, 4),
        'corpus_header_rate': round(all_header_rate, 4),
        'ey_header_enrichment': round(enrichment(ey_header_rate, all_header_rate), 3),
    }

    print(f"    e->y mean position: {ey_mean_pos:.4f} (corpus: {all_mean_pos:.4f})")
    print(f"    e->y initial rate: {ey_initial_rate:.4f} (corpus: {all_initial_rate:.4f}, enrichment: {result['ey_initial_enrichment']:.2f}x)")
    print(f"    e->y final rate: {ey_final_rate:.4f} (corpus: {all_final_rate:.4f}, enrichment: {result['ey_final_enrichment']:.2f}x)")
    for q, info in sorted(quint_enrichment.items()):
        print(f"      {q}: e->y {info['ey_rate']:.3f} vs corpus {info['corpus_rate']:.3f} = {info['enrichment']:.2f}x")

    return result


# ============================================================
# T5: e->y AND PREFIX CHANNELS
# ============================================================

def test_t5_ey_prefix_channels(all_tokens):
    """T5: PREFIX co-occurrence with e->y MIDDLEs."""
    print("  T5: e->y and PREFIX channels...")

    ey_tokens = [t for t in all_tokens if t['is_ey']]
    non_ey = [t for t in all_tokens if not t['is_ey']]

    # PREFIX distribution for e->y
    ey_prefix = Counter(t['prefix'] or 'BARE' for t in ey_tokens)
    all_prefix = Counter(t['prefix'] or 'BARE' for t in all_tokens)

    total_ey = len(ey_tokens)
    total_all = len(all_tokens)

    prefix_enrichment = {}
    for pfx in sorted(set(list(ey_prefix.keys()) + list(all_prefix.keys()))):
        ey_rate = ey_prefix.get(pfx, 0) / max(total_ey, 1)
        all_rate = all_prefix.get(pfx, 0) / max(total_all, 1)
        if ey_prefix.get(pfx, 0) >= 5 or all_prefix.get(pfx, 0) >= 50:
            prefix_enrichment[pfx] = {
                'ey_count': ey_prefix.get(pfx, 0),
                'ey_rate': round(ey_rate, 4),
                'corpus_rate': round(all_rate, 4),
                'enrichment': round(enrichment(ey_rate, all_rate), 3),
            }

    # Thermal PREFIXes specifically
    thermal_pfxs = {'qo', 'ok', 'ch', 'sh', 'ot'}
    ey_thermal = sum(1 for t in ey_tokens if (t['prefix'] or '') in thermal_pfxs)
    all_thermal = sum(1 for t in all_tokens if (t['prefix'] or '') in thermal_pfxs)
    ey_thermal_rate = ey_thermal / max(total_ey, 1)
    all_thermal_rate = all_thermal / max(total_all, 1)

    # Sister pair analysis (ch vs sh)
    ey_ch = sum(1 for t in ey_tokens if t['prefix'] == 'ch')
    ey_sh = sum(1 for t in ey_tokens if t['prefix'] == 'sh')
    all_ch = sum(1 for t in all_tokens if t['prefix'] == 'ch')
    all_sh = sum(1 for t in all_tokens if t['prefix'] == 'sh')

    result = {
        'prefix_enrichment': prefix_enrichment,
        'ey_thermal_prefix_rate': round(ey_thermal_rate, 4),
        'corpus_thermal_prefix_rate': round(all_thermal_rate, 4),
        'thermal_enrichment': round(enrichment(ey_thermal_rate, all_thermal_rate), 3),
        'ey_ch_count': ey_ch,
        'ey_sh_count': ey_sh,
        'ey_ch_sh_ratio': round(safe_ratio(ey_ch, ey_sh), 3),
        'corpus_ch_sh_ratio': round(safe_ratio(all_ch, all_sh), 3),
    }

    print(f"    Thermal PREFIX rate in e->y: {ey_thermal_rate:.3f} (corpus: {all_thermal_rate:.3f}, enrichment: {result['thermal_enrichment']:.2f}x)")
    print(f"    ch/sh in e->y: {ey_ch}/{ey_sh} = {result['ey_ch_sh_ratio']:.2f}x (corpus: {result['corpus_ch_sh_ratio']:.2f}x)")
    print(f"    Top PREFIXes by enrichment:")
    for pfx, info in sorted(prefix_enrichment.items(), key=lambda x: -x[1]['enrichment'])[:8]:
        if info['ey_count'] >= 5:
            print(f"      {pfx}: {info['ey_count']} tokens, {info['enrichment']:.2f}x enrichment")

    return result


# ============================================================
# T6: e->y AND SUFFIX BEHAVIOR
# ============================================================

def test_t6_ey_suffix_behavior(all_tokens):
    """T6: Suffix rate, mode, and two-level closure interaction for e->y."""
    print("  T6: e->y and suffix behavior...")

    ey_tokens = [t for t in all_tokens if t['is_ey']]
    non_ey = [t for t in all_tokens if not t['is_ey']]

    # Suffix rate
    ey_suffixed = sum(1 for t in ey_tokens if t['has_suffix'])
    ey_suffix_rate = ey_suffixed / max(len(ey_tokens), 1)
    all_suffixed = sum(1 for t in all_tokens if t['has_suffix'])
    all_suffix_rate = all_suffixed / max(len(all_tokens), 1)

    # Suffix distribution for e->y
    ey_suffix_dist = Counter(t['suffix'] for t in ey_tokens if t['has_suffix'])

    # Suffix mode distribution
    ey_mode = Counter(t['suffix_mode'] for t in ey_tokens)
    all_mode = Counter(t['suffix_mode'] for t in all_tokens)

    ey_modeA_rate = ey_mode.get('A', 0) / max(len(ey_tokens), 1)
    all_modeA_rate = all_mode.get('A', 0) / max(len(all_tokens), 1)

    # y is an opaque terminal (C1440, 4.2% suffix rate from TWO_LEVEL_CLOSURE)
    # Verify: suffix rate for y-terminal tokens overall
    y_term_tokens = [t for t in all_tokens if t['term_atom'] == 'y']
    y_term_suffixed = sum(1 for t in y_term_tokens if t['has_suffix'])
    y_term_suffix_rate = y_term_suffixed / max(len(y_term_tokens), 1)

    # Suffix atoms for e->y tokens that DO have suffix
    suffix_atom_counts = Counter()
    for t in ey_tokens:
        if t['has_suffix']:
            for ch in t['suffix']:
                suffix_atom_counts[ch] += 1

    result = {
        'ey_suffix_rate': round(ey_suffix_rate, 4),
        'corpus_suffix_rate': round(all_suffix_rate, 4),
        'suffix_rate_ratio': round(safe_ratio(ey_suffix_rate, all_suffix_rate), 3),
        'ey_suffix_dist': dict(ey_suffix_dist.most_common(10)),
        'ey_suffixed_count': ey_suffixed,
        'ey_total': len(ey_tokens),
        'ey_mode_A_rate': round(ey_modeA_rate, 4),
        'corpus_mode_A_rate': round(all_modeA_rate, 4),
        'mode_A_enrichment': round(enrichment(ey_modeA_rate, all_modeA_rate), 3),
        'y_terminal_overall_suffix_rate': round(y_term_suffix_rate, 4),
        'suffix_atom_counts': dict(suffix_atom_counts.most_common(10)),
    }

    print(f"    e->y suffix rate: {ey_suffix_rate:.4f} (corpus: {all_suffix_rate:.4f}, ratio: {result['suffix_rate_ratio']:.2f}x)")
    print(f"    y-terminal overall suffix rate: {y_term_suffix_rate:.4f}")
    print(f"    e->y Mode A rate: {ey_modeA_rate:.4f} (corpus: {all_modeA_rate:.4f}, enrichment: {result['mode_A_enrichment']:.2f}x)")
    if ey_suffix_dist:
        print(f"    Top suffixes: {ey_suffix_dist.most_common(5)}")

    return result


# ============================================================
# T7: e->y AS STABILITY ANCHOR — TRANSITION ANALYSIS
# ============================================================

def test_t7_ey_stability_anchor(all_tokens, adjacency_pairs):
    """T7: Macro-state occupation, transition in/out patterns."""
    print("  T7: e->y as stability anchor...")

    ey_tokens = [t for t in all_tokens if t['is_ey']]
    non_ey = [t for t in all_tokens if not t['is_ey']]

    # Macro-state distribution
    ey_macro = Counter(t['macro_state'] for t in ey_tokens if t['macro_state'])
    all_macro = Counter(t['macro_state'] for t in all_tokens if t['macro_state'])

    total_ey_macro = sum(ey_macro.values())
    total_all_macro = sum(all_macro.values())

    macro_enrichment = {}
    for state in sorted(set(list(ey_macro.keys()) + list(all_macro.keys()))):
        ey_rate = ey_macro.get(state, 0) / max(total_ey_macro, 1)
        all_rate = all_macro.get(state, 0) / max(total_all_macro, 1)
        macro_enrichment[state] = {
            'ey_count': ey_macro.get(state, 0),
            'ey_rate': round(ey_rate, 4),
            'corpus_rate': round(all_rate, 4),
            'enrichment': round(enrichment(ey_rate, all_rate), 3),
        }

    # Transition analysis: what macro-state precedes e->y?
    pre_ey_macro = Counter()
    post_ey_macro = Counter()
    ey_self_chain = 0
    ey_transitions_in = 0
    ey_transitions_out = 0

    for pair in adjacency_pairs:
        if pair['tgt']['is_ey']:
            pre_state = pair['src'].get('macro_state')
            if pre_state:
                pre_ey_macro[pre_state] += 1
                ey_transitions_in += 1
        if pair['src']['is_ey']:
            post_state = pair['tgt'].get('macro_state')
            if post_state:
                post_ey_macro[post_state] += 1
                ey_transitions_out += 1
            if pair['tgt']['is_ey']:
                ey_self_chain += 1

    # Pre/post HEAD atom analysis
    pre_ey_head = Counter()
    post_ey_head = Counter()
    pre_ey_term = Counter()

    for pair in adjacency_pairs:
        if pair['tgt']['is_ey']:
            if pair['src']['head_atom']:
                pre_ey_head[pair['src']['head_atom']] += 1
            if pair['src']['term_atom']:
                pre_ey_term[pair['src']['term_atom']] += 1
        if pair['src']['is_ey']:
            if pair['tgt']['head_atom']:
                post_ey_head[pair['tgt']['head_atom']] += 1

    # Self-chaining rate
    ey_self_chain_rate = ey_self_chain / max(ey_transitions_out, 1)

    result = {
        'macro_state_enrichment': macro_enrichment,
        'pre_ey_macro_dist': {k: round(v/max(ey_transitions_in, 1), 3) for k, v in pre_ey_macro.most_common()},
        'post_ey_macro_dist': {k: round(v/max(ey_transitions_out, 1), 3) for k, v in post_ey_macro.most_common()},
        'ey_self_chain_count': ey_self_chain,
        'ey_self_chain_rate': round(ey_self_chain_rate, 4),
        'pre_ey_head_atoms': dict(pre_ey_head.most_common(8)),
        'post_ey_head_atoms': dict(post_ey_head.most_common(8)),
        'pre_ey_term_atoms': dict(pre_ey_term.most_common(8)),
    }

    print(f"    Macro-state enrichment:")
    for state, info in sorted(macro_enrichment.items(), key=lambda x: -x[1]['ey_count']):
        if info['ey_count'] > 0:
            print(f"      {state}: {info['ey_rate']:.3f} vs {info['corpus_rate']:.3f} = {info['enrichment']:.2f}x ({info['ey_count']})")
    print(f"    Self-chaining rate: {ey_self_chain_rate:.4f} ({ey_self_chain}/{ey_transitions_out})")
    print(f"    Pre-e->y top HEADs: {pre_ey_head.most_common(5)}")
    print(f"    Post-e->y top HEADs: {post_ey_head.most_common(5)}")

    return result


# ============================================================
# T8: e->y VS OTHER SAFE FRAMES
# ============================================================

def test_t8_ey_vs_other_safe_frames(all_tokens):
    """T8: Comparative analysis of all safe HEAD x TERM frames."""
    print("  T8: e->y vs other safe frames...")

    # Build HEAD x TERM frame hazard map
    frame_tokens = defaultdict(list)
    for t in all_tokens:
        head = t['head_atom']
        term = t['term_atom'] or 'bare'
        if head:
            frame_key = f"{head}->{term}"
            frame_tokens[frame_key].append(t)

    # Compute hazard rate for each frame
    safe_frames = []
    all_frames = []
    total_safe_tokens = 0

    for frame_key, tokens in frame_tokens.items():
        n = len(tokens)
        hazard = sum(1 for t in tokens if t['is_hazard_cat'])
        hazard_rate = hazard / n
        info = {
            'frame': frame_key,
            'n': n,
            'hazard_count': hazard,
            'hazard_rate': round(hazard_rate, 4),
        }
        all_frames.append(info)
        if hazard_rate == 0 and n >= 100:
            safe_frames.append(info)
            total_safe_tokens += n

    safe_frames.sort(key=lambda x: -x['n'])

    # What fraction of total safety is in e->y?
    ey_safe_n = sum(f['n'] for f in safe_frames if f['frame'] == 'e->y')
    ey_safety_fraction = ey_safe_n / max(total_safe_tokens, 1)

    # Top 10 safe frames
    top_safe = safe_frames[:10]

    # All frames with 0% hazard (any size)
    zero_hazard_frames = [f for f in all_frames if f['hazard_rate'] == 0 and f['n'] >= 10]
    zero_hazard_frames.sort(key=lambda x: -x['n'])

    # Total tokens in 0% hazard frames
    total_zero_hazard = sum(f['n'] for f in zero_hazard_frames)

    result = {
        'total_safe_frames_over_100': len(safe_frames),
        'total_safe_tokens_over_100': total_safe_tokens,
        'ey_safety_fraction': round(ey_safety_fraction, 4),
        'ey_safe_tokens': ey_safe_n,
        'top_safe_frames': top_safe,
        'total_zero_hazard_frames_over_10': len(zero_hazard_frames),
        'total_zero_hazard_tokens': total_zero_hazard,
        'top_zero_hazard_frames': zero_hazard_frames[:15],
    }

    print(f"    Safe frames (0% hazard, N>=100): {len(safe_frames)}")
    print(f"    Total safe tokens: {total_safe_tokens}")
    print(f"    e->y safety fraction: {ey_safety_fraction:.1%} ({ey_safe_n}/{total_safe_tokens})")
    print(f"    Top safe frames:")
    for f in top_safe[:8]:
        print(f"      {f['frame']}: {f['n']} tokens, {f['hazard_rate']:.1%} hazard")

    return result


# ============================================================
# T9: e->y AND PARAGRAPH STRUCTURE
# ============================================================

def test_t9_ey_paragraph_structure(all_tokens, folio_paragraphs, tokens_by_folio_line):
    """T9: e->y rate by paragraph position and depth."""
    print("  T9: e->y and paragraph structure...")

    # e->y rate by line position within paragraph
    para_line_ey = defaultdict(lambda: {'ey': 0, 'total': 0})
    for t in all_tokens:
        if 'line_in_para' in t:
            pos = t['line_in_para']
            # Normalize: header=0, early body=1-2, late body=3+
            if pos == 0:
                key = 'header'
            elif pos <= 2:
                key = 'early_body'
            else:
                key = 'late_body'
            para_line_ey[key]['total'] += 1
            if t['is_ey']:
                para_line_ey[key]['ey'] += 1

    para_line_rates = {}
    for key, counts in para_line_ey.items():
        rate = counts['ey'] / max(counts['total'], 1)
        para_line_rates[key] = {
            'ey_count': counts['ey'],
            'total': counts['total'],
            'rate': round(rate, 4),
        }

    # e->y rate by paragraph ordinal within folio
    para_ordinal_ey = defaultdict(lambda: {'ey': 0, 'total': 0})
    for t in all_tokens:
        if 'para_idx' in t and 'n_paras_in_folio' in t:
            n_paras = t['n_paras_in_folio']
            if n_paras <= 1:
                key = 'single'
            elif t['para_idx'] == 0:
                key = 'first'
            elif t['para_idx'] == n_paras - 1:
                key = 'last'
            else:
                key = 'middle'
            para_ordinal_ey[key]['total'] += 1
            if t['is_ey']:
                para_ordinal_ey[key]['ey'] += 1

    para_ordinal_rates = {}
    for key, counts in para_ordinal_ey.items():
        rate = counts['ey'] / max(counts['total'], 1)
        para_ordinal_rates[key] = {
            'ey_count': counts['ey'],
            'total': counts['total'],
            'rate': round(rate, 4),
        }

    # Per-paragraph e->y rate and its correlation with AXM fraction
    para_stats = []
    for folio, paras in folio_paragraphs.items():
        for para in paras:
            para_tokens = []
            for key in para['lines']:
                para_tokens.extend(tokens_by_folio_line[key])
            if len(para_tokens) < 5:
                continue
            ey_count = sum(1 for t in para_tokens if t['is_ey'])
            ey_rate = ey_count / len(para_tokens)
            axm_count = sum(1 for t in para_tokens if t.get('macro_state') == 'AXM')
            total_macro = sum(1 for t in para_tokens if t.get('macro_state'))
            axm_rate = axm_count / max(total_macro, 1)
            para_stats.append({
                'folio': folio,
                'para_idx': para['para_idx'],
                'n_tokens': len(para_tokens),
                'ey_rate': ey_rate,
                'axm_rate': axm_rate,
            })

    # Correlation: paragraph e->y rate vs AXM rate
    if len(para_stats) > 20:
        ey_rates = [p['ey_rate'] for p in para_stats]
        axm_rates = [p['axm_rate'] for p in para_stats]
        rho, p_val = spearmanr(ey_rates, axm_rates)
    else:
        rho, p_val = 0, 1.0

    result = {
        'para_line_position_rates': para_line_rates,
        'para_ordinal_rates': para_ordinal_rates,
        'ey_axm_correlation': {
            'spearman_rho': round(float(rho), 4),
            'p_value': round(float(p_val), 6),
            'n_paragraphs': len(para_stats),
        },
    }

    print(f"    Paragraph line position rates:")
    for key, info in sorted(para_line_rates.items()):
        print(f"      {key}: {info['rate']:.4f} ({info['ey_count']}/{info['total']})")
    print(f"    Paragraph ordinal rates:")
    for key, info in sorted(para_ordinal_rates.items()):
        print(f"      {key}: {info['rate']:.4f} ({info['ey_count']}/{info['total']})")
    print(f"    e->y vs AXM correlation: rho={rho:.4f}, p={p_val:.6f} (n={len(para_stats)})")

    return result


# ============================================================
# T10: e->y AND PROGRAM FORGIVENESS
# ============================================================

def test_t10_ey_forgiveness(all_tokens, tokens_by_folio_line):
    """T10: Does e->y rate predict program forgiveness (AXM attractor strength)?"""
    print("  T10: e->y and program forgiveness...")

    # Per-folio statistics
    folio_stats = defaultdict(lambda: {
        'total': 0, 'ey': 0, 'axm': 0, 'fq': 0,
        'hazard': 0, 'macro_total': 0
    })

    for t in all_tokens:
        folio = t['folio']
        folio_stats[folio]['total'] += 1
        if t['is_ey']:
            folio_stats[folio]['ey'] += 1
        if t['is_hazard_cat']:
            folio_stats[folio]['hazard'] += 1
        ms = t.get('macro_state')
        if ms:
            folio_stats[folio]['macro_total'] += 1
            if ms == 'AXM':
                folio_stats[folio]['axm'] += 1
            elif ms == 'FQ':
                folio_stats[folio]['fq'] += 1

    # Compute per-folio AXM self-transition rate
    # Need adjacency pairs per folio for self-transition
    folio_axm_self = defaultdict(lambda: {'axm_transitions': 0, 'axm_self': 0})
    for key in sorted(tokens_by_folio_line.keys()):
        folio, line = key
        line_tokens = tokens_by_folio_line[key]
        for i in range(len(line_tokens) - 1):
            src_ms = line_tokens[i].get('macro_state')
            tgt_ms = line_tokens[i+1].get('macro_state')
            if src_ms == 'AXM':
                folio_axm_self[folio]['axm_transitions'] += 1
                if tgt_ms == 'AXM':
                    folio_axm_self[folio]['axm_self'] += 1

    # Build folio-level dataframe
    folio_data = []
    for folio, stats in folio_stats.items():
        if stats['total'] < 30:
            continue
        ey_rate = stats['ey'] / stats['total']
        hazard_rate = stats['hazard'] / stats['total']
        axm_rate = stats['axm'] / max(stats['macro_total'], 1)
        fq_rate = stats['fq'] / max(stats['macro_total'], 1)

        axm_info = folio_axm_self[folio]
        axm_self_rate = axm_info['axm_self'] / max(axm_info['axm_transitions'], 1)

        folio_data.append({
            'folio': folio,
            'ey_rate': ey_rate,
            'axm_rate': axm_rate,
            'axm_self_rate': axm_self_rate,
            'fq_rate': fq_rate,
            'hazard_rate': hazard_rate,
            'total': stats['total'],
        })

    # Correlations
    if len(folio_data) > 10:
        ey_rates = [f['ey_rate'] for f in folio_data]
        axm_rates = [f['axm_rate'] for f in folio_data]
        axm_self_rates = [f['axm_self_rate'] for f in folio_data]
        fq_rates = [f['fq_rate'] for f in folio_data]
        hazard_rates = [f['hazard_rate'] for f in folio_data]

        rho_axm, p_axm = spearmanr(ey_rates, axm_rates)
        rho_self, p_self = spearmanr(ey_rates, axm_self_rates)
        rho_fq, p_fq = spearmanr(ey_rates, fq_rates)
        rho_hazard, p_hazard = spearmanr(ey_rates, hazard_rates)
    else:
        rho_axm = rho_self = rho_fq = rho_hazard = 0
        p_axm = p_self = p_fq = p_hazard = 1.0

    # Quartile analysis: split folios by e->y rate
    folio_data.sort(key=lambda f: f['ey_rate'])
    n = len(folio_data)
    q_size = n // 4
    quartiles = {}
    for qi, label in enumerate(['Q1_low_ey', 'Q2', 'Q3', 'Q4_high_ey']):
        start = qi * q_size
        end = (qi + 1) * q_size if qi < 3 else n
        q_folios = folio_data[start:end]
        if q_folios:
            quartiles[label] = {
                'n_folios': len(q_folios),
                'mean_ey_rate': round(np.mean([f['ey_rate'] for f in q_folios]), 4),
                'mean_axm_rate': round(np.mean([f['axm_rate'] for f in q_folios]), 4),
                'mean_axm_self_rate': round(np.mean([f['axm_self_rate'] for f in q_folios]), 4),
                'mean_fq_rate': round(np.mean([f['fq_rate'] for f in q_folios]), 4),
                'mean_hazard_rate': round(np.mean([f['hazard_rate'] for f in q_folios]), 4),
            }

    result = {
        'n_folios': len(folio_data),
        'correlations': {
            'ey_vs_axm_rate': {'rho': round(float(rho_axm), 4), 'p': round(float(p_axm), 6)},
            'ey_vs_axm_self_transition': {'rho': round(float(rho_self), 4), 'p': round(float(p_self), 6)},
            'ey_vs_fq_rate': {'rho': round(float(rho_fq), 4), 'p': round(float(p_fq), 6)},
            'ey_vs_hazard_rate': {'rho': round(float(rho_hazard), 4), 'p': round(float(p_hazard), 6)},
        },
        'quartile_analysis': quartiles,
    }

    print(f"    Folio-level correlations (n={len(folio_data)} folios):")
    print(f"      e->y vs AXM rate: rho={rho_axm:.4f}, p={p_axm:.6f}")
    print(f"      e->y vs AXM self-transition: rho={rho_self:.4f}, p={p_self:.6f}")
    print(f"      e->y vs FQ rate: rho={rho_fq:.4f}, p={p_fq:.6f}")
    print(f"      e->y vs hazard rate: rho={rho_hazard:.4f}, p={p_hazard:.6f}")
    print(f"    Quartile analysis:")
    for label, info in sorted(quartiles.items()):
        print(f"      {label}: ey={info['mean_ey_rate']:.3f}, AXM={info['mean_axm_rate']:.3f}, AXM_self={info['mean_axm_self_rate']:.3f}, FQ={info['mean_fq_rate']:.3f}, hazard={info['mean_hazard_rate']:.3f}")

    return result


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 525: e->y Safe Pathway and Recovery Architecture")
    print("=" * 60)

    print("\nLoading data...")
    all_tokens, adjacency_pairs, tokens_by_folio_line, folio_paragraphs = collect_b_tokens()
    print(f"  {len(all_tokens)} tokens, {len(adjacency_pairs)} adjacency pairs")
    print(f"  {sum(1 for t in all_tokens if t['is_ey'])} e->y tokens ({sum(1 for t in all_tokens if t['is_ey'])/len(all_tokens):.1%})")

    results = {}
    print("\nRunning tests...")

    results['T1_ey_inventory'] = test_t1_ey_token_inventory(all_tokens)
    results['T2_ey_category'] = test_t2_ey_category_profile(all_tokens)
    results['T3_ey_recovery'] = test_t3_ey_recovery(all_tokens, adjacency_pairs)
    results['T4_ey_position'] = test_t4_ey_positional_profile(all_tokens)
    results['T5_ey_prefix'] = test_t5_ey_prefix_channels(all_tokens)
    results['T6_ey_suffix'] = test_t6_ey_suffix_behavior(all_tokens)
    results['T7_ey_stability'] = test_t7_ey_stability_anchor(all_tokens, adjacency_pairs)
    results['T8_ey_vs_safe'] = test_t8_ey_vs_other_safe_frames(all_tokens)
    results['T9_ey_paragraph'] = test_t9_ey_paragraph_structure(all_tokens, folio_paragraphs, tokens_by_folio_line)
    results['T10_ey_forgiveness'] = test_t10_ey_forgiveness(all_tokens, tokens_by_folio_line)

    # Summary
    results['summary'] = {
        'total_b_tokens': len(all_tokens),
        'ey_tokens': sum(1 for t in all_tokens if t['is_ey']),
        'ey_fraction': round(sum(1 for t in all_tokens if t['is_ey']) / len(all_tokens), 4),
        'ey_hazard_rate': results['T2_ey_category']['ey_hazard_rate'],
        'ey_safety_fraction': results['T8_ey_vs_safe']['ey_safety_fraction'],
        'ey_axm_enrichment': results['T7_ey_stability']['macro_state_enrichment'].get('AXM', {}).get('enrichment', 0),
        'ey_post_hazard_enrichment': results['T3_ey_recovery']['post_hazard_enrichment'],
        'ey_folio_axm_correlation': results['T10_ey_forgiveness']['correlations']['ey_vs_axm_self_transition']['rho'],
    }

    # Save results
    output_path = RESULTS_DIR / 'ey_safe_pathway.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults saved to {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    s = results['summary']
    print(f"  e->y tokens: {s['ey_tokens']} ({s['ey_fraction']:.1%} of corpus)")
    print(f"  e->y hazard rate: {s['ey_hazard_rate']:.4f}")
    print(f"  e->y safety fraction (of safe frames >100): {s['ey_safety_fraction']:.1%}")
    print(f"  e->y AXM enrichment: {s['ey_axm_enrichment']:.2f}x")
    print(f"  e->y post-hazard enrichment: {s['ey_post_hazard_enrichment']:.2f}x")
    print(f"  e->y vs folio AXM self-transition: rho={s['ey_folio_axm_correlation']:.4f}")


if __name__ == '__main__':
    main()
