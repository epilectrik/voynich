"""
Phase 533: HEAD Domain Differentiation
========================================
Characterizes the 5 HEAD atoms {a, e, o, k, t} + headless tokens across
multiple behavioral dimensions. Tests whether k-HEAD's complete hazard
immunity (C1446) is intrinsic (HEAD-level property) or compositional
(k just attracts low-hazard modifier/terminal combinations).

Dimensions:
  T1: Category profile per HEAD
  T2: Modifier compatibility per HEAD
  T3: Terminal compatibility per HEAD
  T4: Frame hazard map per HEAD (HEAD x TERM)
  T5: Line position profile per HEAD (quintile distribution)
  T6: PREFIX selectivity per HEAD
  T7: Suffix rate per HEAD
  T8: e-depth analysis (single-e vs ee vs eee)
  T9: Headless comparison vs headed
  T10: Population census (token count, type count)
  T11: k-immunity mechanism test (intrinsic vs compositional)
  T12: Pairwise behavioral distance (JSD between HEADs)

Output: phases/HEAD_DOMAIN_DIFFERENTIATION/results/head_domain_differentiation.json
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, CategoryClassifier, decompose_middle_hmt

# ============================================================
# Constants
# ============================================================

HEADS = {'a', 'e', 'o', 'k', 't'}
TERMINALS = {'y', 'l', 'r', 'h', 'm', 'n'}
MODIFIERS = {'p', 'c', 'i', 'f', 'd', 's'}
ALL_CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
                  'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']

# 17 forbidden MIDDLE-level pairs (C109, from HAZARD_ATOM_DECOMPOSITION)
FORBIDDEN_PAIRS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'),
    ('dy', 'aiin'), ('dy', 'chey'),
    ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'),
    ('ar', 'dal'), ('c', 'ee'),
    ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o'),
]

# Terminal suffix sets for Mode A/B classification (C1229, C1231)
TERMINAL_SUFFIXES = {'edy', 'ey', 'eey', 'dy', 'y', 'hy', 'ry', 'ly', 'eedy', 'chy', 'shy'}


# ============================================================
# Utility functions
# ============================================================

def jsd(p, q, categories):
    """Jensen-Shannon divergence between two distributions over fixed categories."""
    eps = 1e-12
    m = {}
    for c in categories:
        m[c] = 0.5 * (p.get(c, 0) + q.get(c, 0))

    kl_pm = 0.0
    kl_qm = 0.0
    for c in categories:
        pc = p.get(c, 0) + eps
        qc = q.get(c, 0) + eps
        mc = m[c] + eps
        kl_pm += pc * math.log2(pc / mc)
        kl_qm += qc * math.log2(qc / mc)

    return 0.5 * kl_pm + 0.5 * kl_qm


def normalize(counter, categories=None):
    """Normalize a counter to a probability distribution."""
    total = sum(counter.values())
    if total == 0:
        return {}
    if categories:
        return {c: counter.get(c, 0) / total for c in categories}
    return {k: v / total for k, v in counter.items()}


def enrichment_ratio(head_count, head_total, base_count, base_total):
    """Compute enrichment ratio with small-sample protection."""
    if head_total == 0 or base_total == 0 or base_count == 0:
        return None
    head_rate = head_count / head_total
    base_rate = base_count / base_total
    if base_rate == 0:
        return None
    return head_rate / base_rate


def chi2_one_cell(obs, exp):
    """Simple chi-square contribution for one cell."""
    if exp == 0:
        return 0
    return (obs - exp) ** 2 / exp


# ============================================================
# Data Loading
# ============================================================

def collect_data():
    """Collect all Currier B tokens with full decomposition."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    forbidden_set = set(FORBIDDEN_PAIRS)
    forbidden_sources = set(src for src, _ in FORBIDDEN_PAIRS)
    forbidden_targets = set(tgt for _, tgt in FORBIDDEN_PAIRS)
    forbidden_all = forbidden_sources | forbidden_targets

    tokens_by_folio_line = defaultdict(list)
    all_tokens = []

    for tok in tx.currier_b():
        word = tok.word
        if not word or not word.strip() or '*' in word:
            continue

        m = morph.extract(word)
        if not m or not m.middle:
            continue

        head, mods, term, frame_str = decompose_middle_hmt(m.middle)

        category = cc.classify(m.middle)
        suffix = m.suffix or ''
        suffix_mode = 'A' if suffix in TERMINAL_SUFFIXES else 'B'

        # e-depth: count leading 'e' chars for e-HEAD
        e_depth = 0
        if head == 'e':
            for ch in m.middle:
                if ch == 'e':
                    e_depth += 1
                else:
                    break

        entry = {
            'word': word,
            'folio': tok.folio,
            'line': tok.line,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': suffix,
            'has_suffix': bool(suffix),
            'articulator': m.articulator,
            'category': category,
            'head': head,          # None for headless
            'mods': mods,
            'term': term,          # 'bare' for no terminal
            'frame_str': frame_str,
            'suffix_mode': suffix_mode,
            'e_depth': e_depth,
            'in_forbidden': m.middle in forbidden_all,
        }

        key = (tok.folio, tok.line)
        tokens_by_folio_line[key].append(entry)
        all_tokens.append(entry)

    # Compute line position quintiles and initial/final flags
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

    # Build adjacency pairs for hazard computation
    adjacency_pairs = []
    for key in sorted(tokens_by_folio_line.keys()):
        line_tokens = tokens_by_folio_line[key]
        for i in range(len(line_tokens) - 1):
            src = line_tokens[i]
            tgt = line_tokens[i + 1]
            pair = (src['middle'], tgt['middle'])
            adjacency_pairs.append({
                'src': src,
                'tgt': tgt,
                'src_middle': src['middle'],
                'tgt_middle': tgt['middle'],
                'is_forbidden': pair in forbidden_set,
            })

    return all_tokens, adjacency_pairs, tokens_by_folio_line


# ============================================================
# Test implementations
# ============================================================

def test_t1_category_profile(all_tokens):
    """T1: Category distribution per HEAD."""
    print("  T1: Category profile per HEAD...")
    head_labels = sorted(HEADS) + ['None']
    results = {}

    # Baseline category distribution
    base_cat = Counter(t['category'] for t in all_tokens if t['category'])
    base_total = sum(base_cat.values())
    base_dist = normalize(base_cat, ALL_CATEGORIES)

    for h in head_labels:
        toks = [t for t in all_tokens if (t['head'] or 'None') == h]
        cat_counts = Counter(t['category'] for t in toks if t['category'])
        cat_total = sum(cat_counts.values())
        cat_dist = normalize(cat_counts, ALL_CATEGORIES)

        # Enrichment vs baseline
        enrichments = {}
        for c in ALL_CATEGORIES:
            er = enrichment_ratio(cat_counts.get(c, 0), cat_total,
                                  base_cat.get(c, 0), base_total)
            enrichments[c] = round(er, 3) if er is not None else None

        # Dominant category
        if cat_counts:
            dominant = cat_counts.most_common(1)[0][0]
        else:
            dominant = None

        results[h] = {
            'n_tokens': len(toks),
            'n_categorized': cat_total,
            'distribution': {c: round(v, 4) for c, v in cat_dist.items()},
            'enrichment_vs_baseline': enrichments,
            'dominant_category': dominant,
            'jsd_vs_baseline': round(jsd(cat_dist, base_dist, ALL_CATEGORIES), 4),
        }

    results['_baseline'] = {c: round(v, 4) for c, v in base_dist.items()}
    return results


def test_t2_modifier_compatibility(all_tokens):
    """T2: Modifier atom compatibility per HEAD."""
    print("  T2: Modifier compatibility per HEAD...")
    head_labels = sorted(HEADS) + ['None']
    results = {}

    # Baseline modifier rates
    all_headed = [t for t in all_tokens if t['mods'] is not None]
    base_mod_counts = Counter()
    for t in all_headed:
        for ch in t['mods']:
            if ch in MODIFIERS:
                base_mod_counts[ch] += 1
    base_total = len(all_headed)

    for h in head_labels:
        toks = [t for t in all_tokens if (t['head'] or 'None') == h and t['mods'] is not None]
        n = len(toks)
        if n == 0:
            results[h] = {'n': 0}
            continue

        mod_counts = Counter()
        for t in toks:
            for ch in t['mods']:
                if ch in MODIFIERS:
                    mod_counts[ch] += 1

        # Rate = fraction of tokens that contain this modifier
        mod_rates = {m: mod_counts.get(m, 0) / n for m in sorted(MODIFIERS)}
        base_rates = {m: base_mod_counts.get(m, 0) / base_total for m in sorted(MODIFIERS)}

        enrichments = {}
        for m in sorted(MODIFIERS):
            if base_rates[m] > 0:
                enrichments[m] = round(mod_rates[m] / base_rates[m], 3)
            else:
                enrichments[m] = None

        # Any modifier present?
        has_any_mod = sum(1 for t in toks if any(ch in MODIFIERS for ch in t['mods']))
        any_mod_rate = has_any_mod / n

        results[h] = {
            'n': n,
            'modifier_rates': {m: round(v, 4) for m, v in mod_rates.items()},
            'enrichment_vs_baseline': enrichments,
            'any_modifier_rate': round(any_mod_rate, 4),
        }

    results['_baseline_rates'] = {m: round(base_mod_counts.get(m, 0) / base_total, 4)
                                  for m in sorted(MODIFIERS)}
    return results


def test_t3_terminal_compatibility(all_tokens):
    """T3: Terminal atom compatibility per HEAD."""
    print("  T3: Terminal compatibility per HEAD...")
    head_labels = sorted(HEADS) + ['None']
    term_labels = sorted(TERMINALS) + ['bare']
    results = {}

    # Baseline terminal distribution
    base_term = Counter(t['term'] for t in all_tokens)
    base_total = sum(base_term.values())
    base_dist = normalize(base_term, term_labels)

    for h in head_labels:
        toks = [t for t in all_tokens if (t['head'] or 'None') == h]
        term_counts = Counter(t['term'] for t in toks)
        n = sum(term_counts.values())
        term_dist = normalize(term_counts, term_labels)

        enrichments = {}
        for trm in term_labels:
            er = enrichment_ratio(term_counts.get(trm, 0), n,
                                  base_term.get(trm, 0), base_total)
            enrichments[trm] = round(er, 3) if er is not None else None

        results[h] = {
            'n': n,
            'distribution': {t: round(v, 4) for t, v in term_dist.items()},
            'enrichment_vs_baseline': enrichments,
            'dominant_terminal': term_counts.most_common(1)[0][0] if term_counts else None,
        }

    results['_baseline'] = {t: round(v, 4) for t, v in base_dist.items()}
    return results


def test_t4_frame_hazard(all_tokens, adjacency_pairs):
    """T4: Frame hazard profile per HEAD."""
    print("  T4: Frame hazard map per HEAD...")

    forbidden_set = set(FORBIDDEN_PAIRS)
    forbidden_all = set()
    for src, tgt in FORBIDDEN_PAIRS:
        forbidden_all.add(src)
        forbidden_all.add(tgt)

    # For each MIDDLE, count how many times it appears in a forbidden pair
    # as either source or target
    middle_forbidden_count = Counter()
    middle_total_transitions = Counter()

    for pair in adjacency_pairs:
        middle_total_transitions[pair['src_middle']] += 1
        middle_total_transitions[pair['tgt_middle']] += 1
        if pair['is_forbidden']:
            middle_forbidden_count[pair['src_middle']] += 1
            middle_forbidden_count[pair['tgt_middle']] += 1

    # Build frame -> hazard stats
    # Group tokens by (head, term) frame
    frame_stats = defaultdict(lambda: {'n_tokens': 0, 'n_in_forbidden': 0,
                                       'middles': Counter()})

    for t in all_tokens:
        h = t['head'] or 'None'
        trm = t['term']
        frame_key = f"{h}->{trm}"
        frame_stats[frame_key]['n_tokens'] += 1
        frame_stats[frame_key]['middles'][t['middle']] += 1
        if t['in_forbidden']:
            frame_stats[frame_key]['n_in_forbidden'] += 1

    # Now compute per-HEAD summary
    head_labels = sorted(HEADS) + ['None']
    results = {}

    for h in head_labels:
        h_frames = {k: v for k, v in frame_stats.items() if k.startswith(f"{h}->")}
        total_tokens = sum(v['n_tokens'] for v in h_frames.values())
        total_forbidden = sum(v['n_in_forbidden'] for v in h_frames.values())

        frame_details = {}
        for fk, fv in sorted(h_frames.items()):
            n = fv['n_tokens']
            n_forb = fv['n_in_forbidden']
            rate = n_forb / n if n > 0 else 0
            frame_details[fk] = {
                'n_tokens': n,
                'n_in_forbidden': n_forb,
                'forbidden_rate': round(rate, 4),
                'n_unique_middles': len(fv['middles']),
            }

        results[h] = {
            'total_tokens': total_tokens,
            'total_in_forbidden_middles': total_forbidden,
            'overall_forbidden_rate': round(total_forbidden / total_tokens, 4) if total_tokens > 0 else 0,
            'n_frames': len(h_frames),
            'frames': frame_details,
        }

    return results


def test_t5_line_position(all_tokens):
    """T5: Line position profile per HEAD."""
    print("  T5: Line position profile per HEAD...")
    head_labels = sorted(HEADS) + ['None']
    results = {}

    # Baseline quintile distribution
    base_q = Counter(t['line_quintile'] for t in all_tokens if 'line_quintile' in t)
    base_total = sum(base_q.values())

    for h in head_labels:
        toks = [t for t in all_tokens if (t['head'] or 'None') == h and 'line_quintile' in t]
        n = len(toks)
        q_counts = Counter(t['line_quintile'] for t in toks)
        q_dist = {str(q): q_counts.get(q, 0) / n if n > 0 else 0 for q in range(5)}

        # Mean position
        mean_pos = sum(t['line_pos_frac'] for t in toks) / n if n > 0 else 0.5

        # Initial/final rates
        n_initial = sum(1 for t in toks if t.get('is_line_initial'))
        n_final = sum(1 for t in toks if t.get('is_line_final'))

        # Enrichment per quintile
        enrichments = {}
        for q in range(5):
            er = enrichment_ratio(q_counts.get(q, 0), n,
                                  base_q.get(q, 0), base_total)
            enrichments[str(q)] = round(er, 3) if er is not None else None

        results[h] = {
            'n': n,
            'mean_position': round(mean_pos, 4),
            'quintile_distribution': {k: round(v, 4) for k, v in q_dist.items()},
            'quintile_enrichment': enrichments,
            'initial_rate': round(n_initial / n, 4) if n > 0 else 0,
            'final_rate': round(n_final / n, 4) if n > 0 else 0,
        }

    return results


def test_t6_prefix_selectivity(all_tokens):
    """T6: PREFIX selectivity per HEAD."""
    print("  T6: PREFIX selectivity per HEAD...")
    head_labels = sorted(HEADS) + ['None']
    results = {}

    # Baseline prefix distribution
    base_pfx = Counter(t['prefix'] or 'BARE' for t in all_tokens)
    base_total = sum(base_pfx.values())

    # Top prefixes for readability
    top_prefixes = [p for p, _ in base_pfx.most_common(15)]

    for h in head_labels:
        toks = [t for t in all_tokens if (t['head'] or 'None') == h]
        n = len(toks)
        pfx_counts = Counter(t['prefix'] or 'BARE' for t in toks)

        # Top 10 most enriched
        enrichments = {}
        for p in top_prefixes:
            er = enrichment_ratio(pfx_counts.get(p, 0), n,
                                  base_pfx.get(p, 0), base_total)
            enrichments[p] = round(er, 3) if er is not None else None

        # Most enriched prefix
        all_enrichments = {}
        for p in pfx_counts:
            er = enrichment_ratio(pfx_counts.get(p, 0), n,
                                  base_pfx.get(p, 0), base_total)
            if er is not None:
                all_enrichments[p] = er

        top_enriched = sorted(all_enrichments.items(), key=lambda x: -x[1])[:5]
        top_depleted = sorted(all_enrichments.items(), key=lambda x: x[1])[:5]

        results[h] = {
            'n': n,
            'prefix_enrichments': enrichments,
            'top_enriched': [(p, round(v, 3)) for p, v in top_enriched],
            'top_depleted': [(p, round(v, 3)) for p, v in top_depleted],
            'n_unique_prefixes': len(pfx_counts),
        }

    return results


def test_t7_suffix_rate(all_tokens):
    """T7: Suffix rate per HEAD."""
    print("  T7: Suffix rate per HEAD...")
    head_labels = sorted(HEADS) + ['None']
    results = {}

    base_suffix_rate = sum(1 for t in all_tokens if t['has_suffix']) / len(all_tokens)
    base_mode_a_rate = sum(1 for t in all_tokens if t['suffix_mode'] == 'A') / len(all_tokens)

    for h in head_labels:
        toks = [t for t in all_tokens if (t['head'] or 'None') == h]
        n = len(toks)
        n_suffix = sum(1 for t in toks if t['has_suffix'])
        n_mode_a = sum(1 for t in toks if t['suffix_mode'] == 'A')

        suffix_rate = n_suffix / n if n > 0 else 0
        mode_a_rate = n_mode_a / n if n > 0 else 0

        results[h] = {
            'n': n,
            'suffix_rate': round(suffix_rate, 4),
            'suffix_enrichment': round(suffix_rate / base_suffix_rate, 3) if base_suffix_rate > 0 else None,
            'mode_a_rate': round(mode_a_rate, 4),
            'mode_a_enrichment': round(mode_a_rate / base_mode_a_rate, 3) if base_mode_a_rate > 0 else None,
        }

    results['_baseline'] = {
        'suffix_rate': round(base_suffix_rate, 4),
        'mode_a_rate': round(base_mode_a_rate, 4),
    }
    return results


def test_t8_e_depth(all_tokens):
    """T8: e-depth analysis for e-HEAD tokens."""
    print("  T8: e-depth analysis...")

    e_tokens = [t for t in all_tokens if t['head'] == 'e']
    results = {}

    for depth in sorted(set(t['e_depth'] for t in e_tokens)):
        toks = [t for t in e_tokens if t['e_depth'] == depth]
        n = len(toks)
        cat_counts = Counter(t['category'] for t in toks if t['category'])
        cat_total = sum(cat_counts.values())
        cat_dist = normalize(cat_counts, ALL_CATEGORIES)

        # Terminal distribution
        term_counts = Counter(t['term'] for t in toks)
        term_total = sum(term_counts.values())

        # Suffix rate
        n_suffix = sum(1 for t in toks if t['has_suffix'])

        # Mean line position
        positions = [t['line_pos_frac'] for t in toks if 'line_pos_frac' in t]
        mean_pos = sum(positions) / len(positions) if positions else 0.5

        # Forbidden MIDDLE rate
        n_forbidden = sum(1 for t in toks if t['in_forbidden'])

        results[f"e_depth_{depth}"] = {
            'n_tokens': n,
            'n_unique_middles': len(set(t['middle'] for t in toks)),
            'category_distribution': {c: round(v, 4) for c, v in cat_dist.items()},
            'terminal_distribution': {k: round(v / term_total, 4) if term_total > 0 else 0
                                      for k, v in term_counts.most_common()},
            'suffix_rate': round(n_suffix / n, 4) if n > 0 else 0,
            'mean_line_position': round(mean_pos, 4),
            'forbidden_middle_rate': round(n_forbidden / n, 4) if n > 0 else 0,
            'sample_middles': [m for m, _ in Counter(t['middle'] for t in toks).most_common(10)],
        }

    return results


def test_t9_headless_comparison(all_tokens):
    """T9: Headless vs headed token comparison."""
    print("  T9: Headless vs headed comparison...")

    headless = [t for t in all_tokens if t['head'] is None]
    headed = [t for t in all_tokens if t['head'] is not None]

    def profile(toks):
        n = len(toks)
        if n == 0:
            return {}
        cat_counts = Counter(t['category'] for t in toks if t['category'])
        cat_total = sum(cat_counts.values())
        cat_dist = normalize(cat_counts, ALL_CATEGORIES)

        term_counts = Counter(t['term'] for t in toks)
        term_total = sum(term_counts.values())

        n_suffix = sum(1 for t in toks if t['has_suffix'])
        n_forbidden = sum(1 for t in toks if t['in_forbidden'])
        positions = [t['line_pos_frac'] for t in toks if 'line_pos_frac' in t]

        return {
            'n': n,
            'n_unique_middles': len(set(t['middle'] for t in toks)),
            'category_distribution': {c: round(v, 4) for c, v in cat_dist.items()},
            'terminal_distribution': {k: round(v / term_total, 4) if term_total > 0 else 0
                                      for k, v in sorted(term_counts.items(), key=lambda x: -x[1])},
            'suffix_rate': round(n_suffix / n, 4),
            'forbidden_middle_rate': round(n_forbidden / n, 4),
            'mean_line_position': round(sum(positions) / len(positions), 4) if positions else 0.5,
        }

    hl_prof = profile(headless)
    hd_prof = profile(headed)

    # JSD between category distributions
    if hl_prof and hd_prof:
        cat_jsd = jsd(hl_prof['category_distribution'], hd_prof['category_distribution'],
                      ALL_CATEGORIES)
    else:
        cat_jsd = None

    return {
        'headless': hl_prof,
        'headed': hd_prof,
        'category_jsd': round(cat_jsd, 4) if cat_jsd is not None else None,
    }


def test_t10_population(all_tokens):
    """T10: Population census per HEAD."""
    print("  T10: Population census...")
    head_labels = sorted(HEADS) + ['None']
    results = {}
    total = len(all_tokens)

    for h in head_labels:
        toks = [t for t in all_tokens if (t['head'] or 'None') == h]
        n = len(toks)
        unique_middles = set(t['middle'] for t in toks)
        mean_middle_len = sum(len(t['middle']) for t in toks) / n if n > 0 else 0

        results[h] = {
            'n_tokens': n,
            'pct_of_total': round(100 * n / total, 2),
            'n_unique_middles': len(unique_middles),
            'mean_middle_length': round(mean_middle_len, 2),
            'top_middles': [m for m, _ in Counter(t['middle'] for t in toks).most_common(10)],
        }

    return results


def test_t11_k_immunity_mechanism(all_tokens, adjacency_pairs):
    """T11: Test whether k-HEAD immunity is intrinsic or compositional.

    Strategy:
    1. Get the modifier+terminal profile of k-HEAD tokens.
    2. For each other HEAD, compute: "If this HEAD had k's modifier/terminal
       distribution, what would its hazard rate be?"
    3. Compare with actual hazard rates.
    4. If other HEADs would ALSO be immune with k's profile -> compositional.
       If other HEADs would NOT be immune -> intrinsic.
    """
    print("  T11: k-immunity mechanism test...")

    forbidden_set = set(FORBIDDEN_PAIRS)
    forbidden_all = set()
    for src, tgt in FORBIDDEN_PAIRS:
        forbidden_all.add(src)
        forbidden_all.add(tgt)

    # Get k-HEAD modifier/terminal profile
    k_tokens = [t for t in all_tokens if t['head'] == 'k']
    k_mod_profile = Counter()
    k_term_profile = Counter()
    for t in k_tokens:
        for ch in t['mods']:
            if ch in MODIFIERS:
                k_mod_profile[ch] += 1
        k_term_profile[t['term']] += 1
    k_mod_total = sum(k_mod_profile.values())
    k_term_total = sum(k_term_profile.values())

    # For each HEAD, compute its actual forbidden-MIDDLE rate
    head_labels = sorted(HEADS) + ['None']
    actual_rates = {}
    for h in head_labels:
        toks = [t for t in all_tokens if (t['head'] or 'None') == h]
        n = len(toks)
        n_forb = sum(1 for t in toks if t['in_forbidden'])
        actual_rates[h] = {
            'n': n,
            'n_in_forbidden': n_forb,
            'forbidden_rate': round(n_forb / n, 4) if n > 0 else 0,
        }

    # Test: for each HEAD, check if k's modifier set EVER co-occurs with
    # forbidden MIDDLEs for that HEAD
    # More precisely: check which modifiers appear in forbidden-participating
    # MIDDLEs for each HEAD
    head_forbidden_mod_profiles = {}
    for h in sorted(HEADS):
        h_forb_toks = [t for t in all_tokens if t['head'] == h and t['in_forbidden']]
        h_safe_toks = [t for t in all_tokens if t['head'] == h and not t['in_forbidden']]

        forb_mods = Counter()
        safe_mods = Counter()
        forb_terms = Counter()
        safe_terms = Counter()

        for t in h_forb_toks:
            for ch in t['mods']:
                if ch in MODIFIERS:
                    forb_mods[ch] += 1
            forb_terms[t['term']] += 1

        for t in h_safe_toks:
            for ch in t['mods']:
                if ch in MODIFIERS:
                    safe_mods[ch] += 1
            safe_terms[t['term']] += 1

        head_forbidden_mod_profiles[h] = {
            'n_forbidden_tokens': len(h_forb_toks),
            'n_safe_tokens': len(h_safe_toks),
            'forbidden_modifier_counts': dict(forb_mods),
            'safe_modifier_counts': dict(safe_mods),
            'forbidden_terminal_counts': dict(forb_terms),
            'safe_terminal_counts': dict(safe_terms),
            'forbidden_has_any_modifier': sum(1 for t in h_forb_toks
                                              if any(ch in MODIFIERS for ch in t['mods'])),
        }

    # Key test: k-HEAD tokens with modifiers {c,d,f,p,s} quench hazard (C1450).
    # Do other HEADs also quench to 0% when they have modifiers?
    head_mod_quench = {}
    for h in sorted(HEADS):
        toks = [t for t in all_tokens if t['head'] == h]
        has_mod = [t for t in toks if any(ch in MODIFIERS for ch in t['mods'])]
        no_mod = [t for t in toks if not any(ch in MODIFIERS for ch in t['mods'])]

        n_has = len(has_mod)
        n_no = len(no_mod)
        forb_has = sum(1 for t in has_mod if t['in_forbidden'])
        forb_no = sum(1 for t in no_mod if t['in_forbidden'])

        head_mod_quench[h] = {
            'with_modifier_n': n_has,
            'with_modifier_forbidden': forb_has,
            'with_modifier_rate': round(forb_has / n_has, 4) if n_has > 0 else 0,
            'without_modifier_n': n_no,
            'without_modifier_forbidden': forb_no,
            'without_modifier_rate': round(forb_no / n_no, 4) if n_no > 0 else 0,
        }

    # Check k's specific composites: every k+terminal = 0?
    k_frame_check = {}
    for t in k_tokens:
        frame = f"k->{t['term']}"
        if frame not in k_frame_check:
            k_frame_check[frame] = {'n': 0, 'n_forbidden': 0}
        k_frame_check[frame]['n'] += 1
        if t['in_forbidden']:
            k_frame_check[frame]['n_forbidden'] += 1

    for frame in k_frame_check:
        v = k_frame_check[frame]
        v['rate'] = round(v['n_forbidden'] / v['n'], 4) if v['n'] > 0 else 0

    # Check: do k-HEAD tokens EVER appear as forbidden pair source or target?
    k_in_pairs = {'as_source': 0, 'as_target': 0, 'total_pairs': 0}
    for pair in adjacency_pairs:
        if pair['src']['head'] == 'k':
            k_in_pairs['total_pairs'] += 1
            if pair['is_forbidden']:
                k_in_pairs['as_source'] += 1
        if pair['tgt']['head'] == 'k':
            if pair['is_forbidden']:
                k_in_pairs['as_target'] += 1

    return {
        'actual_forbidden_rates': actual_rates,
        'k_modifier_profile': {k: v for k, v in k_mod_profile.most_common()},
        'k_terminal_profile': {k: v for k, v in k_term_profile.most_common()},
        'head_forbidden_modifier_profiles': head_forbidden_mod_profiles,
        'modifier_quench_test': head_mod_quench,
        'k_frame_check': k_frame_check,
        'k_in_forbidden_pairs': k_in_pairs,
    }


def test_t12_pairwise_distance(all_tokens):
    """T12: Pairwise JSD between all HEAD types across multiple dimensions."""
    print("  T12: Pairwise behavioral distance...")
    head_labels = sorted(HEADS) + ['None']

    # Build profiles per HEAD
    profiles = {}
    for h in head_labels:
        toks = [t for t in all_tokens if (t['head'] or 'None') == h]
        n = len(toks)
        if n == 0:
            profiles[h] = {}
            continue

        # Category distribution
        cat_counts = Counter(t['category'] for t in toks if t['category'])
        cat_dist = normalize(cat_counts, ALL_CATEGORIES)

        # Terminal distribution
        term_labels_full = sorted(TERMINALS) + ['bare']
        term_counts = Counter(t['term'] for t in toks)
        term_dist = normalize(term_counts, term_labels_full)

        # Quintile distribution
        q_counts = Counter(t.get('line_quintile', 2) for t in toks)
        q_dist = normalize(q_counts, list(range(5)))

        profiles[h] = {
            'category': cat_dist,
            'terminal': term_dist,
            'position': q_dist,
        }

    # Compute pairwise JSD for each dimension
    dimensions = ['category', 'terminal', 'position']
    dim_categories = {
        'category': ALL_CATEGORIES,
        'terminal': sorted(TERMINALS) + ['bare'],
        'position': list(range(5)),
    }

    pairwise = {}
    for i, h1 in enumerate(head_labels):
        for h2 in head_labels[i + 1:]:
            pair_key = f"{h1}_vs_{h2}"
            distances = {}
            for dim in dimensions:
                p1 = profiles.get(h1, {}).get(dim, {})
                p2 = profiles.get(h2, {}).get(dim, {})
                cats = dim_categories[dim]
                # Convert int keys to string for position
                if dim == 'position':
                    p1 = {k: v for k, v in p1.items()}
                    p2 = {k: v for k, v in p2.items()}
                distances[dim] = round(jsd(p1, p2, cats), 4)

            # Mean JSD across dimensions
            distances['mean'] = round(sum(distances.values()) / len(distances), 4)
            pairwise[pair_key] = distances

    # Rank by mean distance
    ranked = sorted(pairwise.items(), key=lambda x: x[1]['mean'])

    return {
        'pairwise_jsd': pairwise,
        'most_similar': [(k, v['mean']) for k, v in ranked[:3]],
        'most_different': [(k, v['mean']) for k, v in ranked[-3:]],
    }


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 533: HEAD Domain Differentiation")
    print("=" * 60)

    print("\nCollecting Currier B data...")
    all_tokens, adjacency_pairs, tokens_by_folio_line = collect_data()
    print(f"  Collected {len(all_tokens)} tokens, {len(adjacency_pairs)} adjacency pairs")

    # Quick census
    head_counts = Counter(t['head'] or 'None' for t in all_tokens)
    print(f"  HEAD distribution: {dict(head_counts.most_common())}")

    results = {
        'meta': {
            'phase': 533,
            'name': 'HEAD_DOMAIN_DIFFERENTIATION',
            'n_tokens': len(all_tokens),
            'n_adjacency_pairs': len(adjacency_pairs),
            'head_counts': dict(head_counts),
        }
    }

    # Run all tests
    results['T1_category_profile'] = test_t1_category_profile(all_tokens)
    results['T2_modifier_compatibility'] = test_t2_modifier_compatibility(all_tokens)
    results['T3_terminal_compatibility'] = test_t3_terminal_compatibility(all_tokens)
    results['T4_frame_hazard'] = test_t4_frame_hazard(all_tokens, adjacency_pairs)
    results['T5_line_position'] = test_t5_line_position(all_tokens)
    results['T6_prefix_selectivity'] = test_t6_prefix_selectivity(all_tokens)
    results['T7_suffix_rate'] = test_t7_suffix_rate(all_tokens)
    results['T8_e_depth'] = test_t8_e_depth(all_tokens)
    results['T9_headless_comparison'] = test_t9_headless_comparison(all_tokens)
    results['T10_population'] = test_t10_population(all_tokens)
    results['T11_k_immunity'] = test_t11_k_immunity_mechanism(all_tokens, adjacency_pairs)
    results['T12_pairwise_distance'] = test_t12_pairwise_distance(all_tokens)

    # ============================================================
    # Summary printout
    # ============================================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # T1 summary: dominant categories
    print("\n--- T1: Category Profile per HEAD ---")
    t1 = results['T1_category_profile']
    base = t1['_baseline']
    print(f"  Baseline: {', '.join(f'{c}={base[c]:.1%}' for c in ALL_CATEGORIES if base.get(c,0) > 0.05)}")
    for h in sorted(HEADS) + ['None']:
        r = t1[h]
        dom = r['dominant_category']
        n = r['n_tokens']
        dist = r['distribution']
        enr = r['enrichment_vs_baseline']
        top_enrich = sorted([(c, enr[c]) for c in ALL_CATEGORIES if enr.get(c)],
                           key=lambda x: -x[1])[:3]
        top_str = ', '.join(f'{c}={v:.2f}x' for c, v in top_enrich)
        print(f"  {h:>5}: N={n:>5}, dominant={dom:<12}, top enrichments: {top_str}, "
              f"JSD vs baseline={r['jsd_vs_baseline']:.4f}")

    # T4 summary: forbidden rates
    print("\n--- T4: Forbidden-MIDDLE Rate per HEAD ---")
    t4 = results['T4_frame_hazard']
    for h in sorted(HEADS) + ['None']:
        r = t4[h]
        rate = r['overall_forbidden_rate']
        n = r['total_tokens']
        n_forb = r['total_in_forbidden_middles']
        print(f"  {h:>5}: N={n:>5}, in_forbidden={n_forb:>4}, rate={rate:.4f} ({rate:.1%})")

        # Show individual frames
        for fk, fv in sorted(r['frames'].items(), key=lambda x: -x[1]['forbidden_rate']):
            if fv['n_tokens'] >= 20:
                print(f"         {fk}: N={fv['n_tokens']:>4}, rate={fv['forbidden_rate']:.4f} ({fv['forbidden_rate']:.1%})")

    # T5 summary: mean positions
    print("\n--- T5: Mean Line Position per HEAD ---")
    t5 = results['T5_line_position']
    for h in sorted(HEADS) + ['None']:
        r = t5[h]
        print(f"  {h:>5}: mean_pos={r['mean_position']:.4f}, "
              f"initial={r['initial_rate']:.3f}, final={r['final_rate']:.3f}")

    # T7 summary: suffix rates
    print("\n--- T7: Suffix Rate per HEAD ---")
    t7 = results['T7_suffix_rate']
    for h in sorted(HEADS) + ['None']:
        r = t7[h]
        print(f"  {h:>5}: suffix_rate={r['suffix_rate']:.3f} ({r['suffix_enrichment']:.2f}x), "
              f"mode_A={r['mode_a_rate']:.3f} ({r['mode_a_enrichment']:.2f}x)")

    # T8 summary: e-depth
    print("\n--- T8: e-Depth Analysis ---")
    t8 = results['T8_e_depth']
    for k, v in sorted(t8.items()):
        print(f"  {k}: N={v['n_tokens']}, types={v['n_unique_middles']}, "
              f"suffix={v['suffix_rate']:.3f}, "
              f"forbidden={v['forbidden_middle_rate']:.3f}, "
              f"pos={v['mean_line_position']:.3f}")

    # T10 summary: population
    print("\n--- T10: Population Census ---")
    t10 = results['T10_population']
    for h in sorted(HEADS) + ['None']:
        r = t10[h]
        print(f"  {h:>5}: N={r['n_tokens']:>5} ({r['pct_of_total']:.1f}%), "
              f"types={r['n_unique_middles']:>4}, "
              f"mean_len={r['mean_middle_length']:.2f}")

    # T11 summary: k-immunity
    print("\n--- T11: k-Immunity Mechanism ---")
    t11 = results['T11_k_immunity']
    print("  Actual forbidden-MIDDLE rates:")
    for h, r in sorted(t11['actual_forbidden_rates'].items()):
        print(f"    {h:>5}: {r['forbidden_rate']:.4f} ({r['n_in_forbidden']}/{r['n']})")

    print("  Modifier quench test (with modifier vs without):")
    for h, r in sorted(t11['modifier_quench_test'].items()):
        print(f"    {h}: with_mod={r['with_modifier_rate']:.4f} (N={r['with_modifier_n']}), "
              f"without_mod={r['without_modifier_rate']:.4f} (N={r['without_modifier_n']})")

    print(f"  k in forbidden pairs: source={t11['k_in_forbidden_pairs']['as_source']}, "
          f"target={t11['k_in_forbidden_pairs']['as_target']}")

    print("  k per-frame check:")
    for frame, r in sorted(t11['k_frame_check'].items()):
        print(f"    {frame}: {r['rate']:.4f} ({r['n_forbidden']}/{r['n']})")

    # T12 summary: distances
    print("\n--- T12: Pairwise JSD ---")
    t12 = results['T12_pairwise_distance']
    print("  Most similar pairs:")
    for pair, dist in t12['most_similar']:
        print(f"    {pair}: mean JSD = {dist:.4f}")
    print("  Most different pairs:")
    for pair, dist in t12['most_different']:
        print(f"    {pair}: mean JSD = {dist:.4f}")

    # Save results
    out_path = PROJECT_ROOT / 'phases' / 'HEAD_DOMAIN_DIFFERENTIATION' / 'results' / 'head_domain_differentiation.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
