"""
Phase 535: TERMINAL Functional Taxonomy
=========================================
Comprehensive characterization of the 6 TERMINAL atoms {y, l, r, h, m, n} + bare
across multiple behavioral dimensions, paralleling Phase 533 (HEAD Domain
Differentiation).

Dimensions:
  T1:  Category profile per TERMINAL
  T2:  Opacity verification (suffix attachment rate, C1440)
  T3:  HEAD compatibility (HEAD x TERM frequency and enrichment)
  T4:  Modifier compatibility per TERMINAL
  T5:  Hazard profile per TERMINAL (forbidden violation rate from adjacency)
  T6:  Line position profile (quintile distribution)
  T7:  PREFIX selectivity per TERMINAL
  T8:  Token frequency and type count (population census)
  T9:  Bare terminal comparison
  T10: Pairwise behavioral distance (JSD)
  T11: Category determination power (Cramer's V per terminal)
  T12: Full HEAD x TERM frame category matrix

Output: phases/TERM_FUNCTIONAL_TAXONOMY/results/term_functional_taxonomy.json
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

TERMINAL_LABELS = sorted(TERMINALS) + ['bare']

# 17 forbidden MIDDLE-level pairs (C109)
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

# Terminal suffixes for Mode A/B classification (C1229, C1231)
TERMINAL_SUFFIXES = {'edy', 'ey', 'eey', 'dy', 'y', 'hy', 'ry', 'ly', 'eedy', 'chy', 'shy'}


# ============================================================
# Utility functions
# ============================================================

def jsd(p, q, categories):
    """Jensen-Shannon divergence between two distributions."""
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
    """Normalize counter to probability distribution."""
    total = sum(counter.values())
    if total == 0:
        return {}
    if categories:
        return {c: counter.get(c, 0) / total for c in categories}
    return {k: v / total for k, v in counter.items()}


def enrichment_ratio(sub_count, sub_total, base_count, base_total):
    """Enrichment ratio with small-sample protection."""
    if sub_total == 0 or base_total == 0 or base_count == 0:
        return None
    sub_rate = sub_count / sub_total
    base_rate = base_count / base_total
    if base_rate == 0:
        return None
    return sub_rate / base_rate


def cramers_v(contingency):
    """Cramer's V from a dict-of-dicts contingency table."""
    # Get all row and column keys
    row_keys = sorted(contingency.keys())
    col_keys = set()
    for row in contingency.values():
        col_keys.update(row.keys())
    col_keys = sorted(col_keys)

    n = sum(sum(row.values()) for row in contingency.values())
    if n == 0:
        return 0.0

    # Row and column totals
    row_totals = {r: sum(contingency[r].values()) for r in row_keys}
    col_totals = {c: sum(contingency.get(r, {}).get(c, 0) for r in row_keys) for c in col_keys}

    chi2 = 0.0
    for r in row_keys:
        for c in col_keys:
            obs = contingency.get(r, {}).get(c, 0)
            exp = row_totals[r] * col_totals[c] / n if n > 0 else 0
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp

    k = min(len(row_keys), len(col_keys))
    if k <= 1 or n == 0:
        return 0.0
    return math.sqrt(chi2 / (n * (k - 1)))


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
            'head': head,
            'mods': mods,
            'term': term,
            'frame_str': frame_str,
            'suffix_mode': suffix_mode,
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
    """T1: Category distribution per TERMINAL."""
    print("  T1: Category profile per TERMINAL...")

    # Baseline
    base_cat = Counter(t['category'] for t in all_tokens if t['category'])
    base_total = sum(base_cat.values())
    base_dist = normalize(base_cat, ALL_CATEGORIES)

    results = {}
    for term in TERMINAL_LABELS:
        toks = [t for t in all_tokens if t['term'] == term]
        cat_counts = Counter(t['category'] for t in toks if t['category'])
        cat_total = sum(cat_counts.values())
        cat_dist = normalize(cat_counts, ALL_CATEGORIES)

        enrichments = {}
        for c in ALL_CATEGORIES:
            er = enrichment_ratio(cat_counts.get(c, 0), cat_total,
                                  base_cat.get(c, 0), base_total)
            enrichments[c] = round(er, 3) if er is not None else None

        dominant = cat_counts.most_common(1)[0][0] if cat_counts else None

        results[term] = {
            'n_tokens': len(toks),
            'n_categorized': cat_total,
            'distribution': {c: round(v, 4) for c, v in cat_dist.items()},
            'enrichment_vs_baseline': enrichments,
            'dominant_category': dominant,
            'jsd_vs_baseline': round(jsd(cat_dist, base_dist, ALL_CATEGORIES), 4),
        }

    results['_baseline'] = {c: round(v, 4) for c, v in base_dist.items()}
    return results


def test_t2_opacity(all_tokens):
    """T2: Suffix attachment rate per TERMINAL (verify C1440 gradient)."""
    print("  T2: Opacity verification...")
    results = {}

    for term in TERMINAL_LABELS:
        toks = [t for t in all_tokens if t['term'] == term]
        n = len(toks)
        if n == 0:
            continue
        n_with_suffix = sum(1 for t in toks if t['has_suffix'])
        suffix_rate = n_with_suffix / n

        # Classify opacity tier
        if suffix_rate < 0.05:
            opacity_tier = 'OPAQUE'
        elif suffix_rate < 0.25:
            opacity_tier = 'SEMI_TRANSPARENT'
        else:
            opacity_tier = 'TRANSPARENT'

        results[term] = {
            'n_tokens': n,
            'n_with_suffix': n_with_suffix,
            'suffix_rate': round(suffix_rate, 4),
            'opacity_tier': opacity_tier,
        }

    return results


def test_t3_head_compatibility(all_tokens):
    """T3: HEAD x TERMINAL frequency and enrichment."""
    print("  T3: HEAD compatibility...")

    head_labels = sorted(HEADS) + ['None']

    # Build HEAD x TERM contingency
    contingency = defaultdict(lambda: defaultdict(int))
    head_totals = Counter()
    term_totals = Counter()
    grand_total = 0

    for t in all_tokens:
        h = t['head'] or 'None'
        term = t['term']
        contingency[h][term] += 1
        head_totals[h] += 1
        term_totals[term] += 1
        grand_total += 1

    # Enrichment ratios and distributions
    results = {}
    for term in TERMINAL_LABELS:
        head_dist = {}
        head_enrichment = {}
        for h in head_labels:
            count = contingency[h][term]
            # P(HEAD=h | TERM=term)
            head_dist[h] = round(count / term_totals[term], 4) if term_totals[term] > 0 else 0
            # Enrichment: P(HEAD=h | TERM=term) / P(HEAD=h)
            er = enrichment_ratio(count, term_totals[term],
                                  head_totals[h], grand_total)
            head_enrichment[h] = round(er, 3) if er is not None else None

        results[term] = {
            'head_distribution': head_dist,
            'head_enrichment': head_enrichment,
            'n_tokens': term_totals[term],
        }

    # Also include raw contingency for reference
    results['_contingency'] = {h: dict(contingency[h]) for h in head_labels}
    results['_head_totals'] = dict(head_totals)
    results['_term_totals'] = dict(term_totals)

    return results


def test_t4_modifier_compatibility(all_tokens):
    """T4: Modifier atom compatibility per TERMINAL."""
    print("  T4: Modifier compatibility...")

    # Only tokens with mods region
    mod_chars = sorted(MODIFIERS)

    # Baseline modifier rates
    base_mod = Counter()
    base_n = 0
    for t in all_tokens:
        for ch in (t['mods'] or ''):
            if ch in MODIFIERS:
                base_mod[ch] += 1
        base_n += 1

    results = {}
    for term in TERMINAL_LABELS:
        toks = [t for t in all_tokens if t['term'] == term]
        n = len(toks)

        mod_counts = Counter()
        has_any_mod = 0
        for t in toks:
            mods_str = t['mods'] or ''
            mod_present = False
            for ch in mods_str:
                if ch in MODIFIERS:
                    mod_counts[ch] += 1
                    mod_present = True
            if mod_present:
                has_any_mod += 1

        mod_rate = has_any_mod / n if n > 0 else 0

        # Per-modifier enrichment
        enrichments = {}
        for mc in mod_chars:
            er = enrichment_ratio(mod_counts.get(mc, 0), n,
                                  base_mod.get(mc, 0), base_n)
            enrichments[mc] = round(er, 3) if er is not None else None

        results[term] = {
            'n_tokens': n,
            'has_any_modifier_rate': round(mod_rate, 4),
            'modifier_counts': {mc: mod_counts.get(mc, 0) for mc in mod_chars},
            'modifier_enrichment': enrichments,
        }

    return results


def test_t5_hazard_profile(adjacency_pairs, all_tokens):
    """T5: Hazard rate per TERMINAL (as source of forbidden violation)."""
    print("  T5: Hazard profile...")

    # Count forbidden violations per source terminal
    src_term_forbidden = Counter()
    src_term_total = Counter()

    for pair in adjacency_pairs:
        src_term = pair['src']['term']
        src_term_forbidden[src_term] += int(pair['is_forbidden'])
        src_term_total[src_term] += 1

    # Also per target terminal
    tgt_term_forbidden = Counter()
    tgt_term_total = Counter()
    for pair in adjacency_pairs:
        tgt_term = pair['tgt']['term']
        tgt_term_forbidden[tgt_term] += int(pair['is_forbidden'])
        tgt_term_total[tgt_term] += 1

    total_violations = sum(src_term_forbidden.values())
    total_pairs = sum(src_term_total.values())

    results = {}
    for term in TERMINAL_LABELS:
        src_viol = src_term_forbidden.get(term, 0)
        src_tot = src_term_total.get(term, 0)
        src_rate = src_viol / src_tot if src_tot > 0 else 0.0

        tgt_viol = tgt_term_forbidden.get(term, 0)
        tgt_tot = tgt_term_total.get(term, 0)
        tgt_rate = tgt_viol / tgt_tot if tgt_tot > 0 else 0.0

        # Share of total violations
        share = src_viol / total_violations if total_violations > 0 else 0

        results[term] = {
            'as_source_violations': src_viol,
            'as_source_transitions': src_tot,
            'as_source_rate': round(src_rate, 6),
            'as_target_violations': tgt_viol,
            'as_target_transitions': tgt_tot,
            'as_target_rate': round(tgt_rate, 6),
            'share_of_total_violations': round(share, 4),
        }

    results['_total_violations'] = total_violations
    results['_total_pairs'] = total_pairs

    return results


def test_t6_line_position(all_tokens):
    """T6: Line position profile (quintile distribution) per TERMINAL."""
    print("  T6: Line position profile...")

    results = {}
    quintiles = [0, 1, 2, 3, 4]

    for term in TERMINAL_LABELS:
        toks = [t for t in all_tokens if t['term'] == term]
        n = len(toks)
        if n == 0:
            continue

        q_counts = Counter(t['line_quintile'] for t in toks)
        q_dist = {f'Q{q}': round(q_counts.get(q, 0) / n, 4) for q in quintiles}

        mean_pos = sum(t['line_pos_frac'] for t in toks) / n
        initial_rate = sum(1 for t in toks if t['is_line_initial']) / n
        final_rate = sum(1 for t in toks if t['is_line_final']) / n

        results[term] = {
            'n_tokens': n,
            'quintile_distribution': q_dist,
            'mean_position': round(mean_pos, 4),
            'line_initial_rate': round(initial_rate, 4),
            'line_final_rate': round(final_rate, 4),
        }

    return results


def test_t7_prefix_selectivity(all_tokens):
    """T7: PREFIX selectivity per TERMINAL."""
    print("  T7: PREFIX selectivity...")

    # Baseline PREFIX distribution
    base_pfx = Counter()
    for t in all_tokens:
        pfx = t['prefix'] or 'BARE'
        base_pfx[pfx] += 1
    base_total = sum(base_pfx.values())
    top_prefixes = [p for p, _ in base_pfx.most_common(15)]

    results = {}
    for term in TERMINAL_LABELS:
        toks = [t for t in all_tokens if t['term'] == term]
        n = len(toks)
        if n == 0:
            continue

        pfx_counts = Counter(t['prefix'] or 'BARE' for t in toks)
        pfx_dist = normalize(pfx_counts)

        # Enrichment for top prefixes
        enrichments = {}
        for pfx in top_prefixes:
            er = enrichment_ratio(pfx_counts.get(pfx, 0), n,
                                  base_pfx.get(pfx, 0), base_total)
            enrichments[pfx] = round(er, 3) if er is not None else None

        # Top 5 PREFIXes for this terminal
        top5 = pfx_counts.most_common(5)

        results[term] = {
            'n_tokens': n,
            'n_prefix_types': len(pfx_counts),
            'top5_prefixes': [(p, c, round(c / n, 4)) for p, c in top5],
            'enrichment_vs_baseline': enrichments,
        }

    return results


def test_t8_population_census(all_tokens):
    """T8: Token frequency and type count per TERMINAL."""
    print("  T8: Population census...")
    total = len(all_tokens)

    results = {}
    for term in TERMINAL_LABELS:
        toks = [t for t in all_tokens if t['term'] == term]
        n = len(toks)
        unique_middles = len(set(t['middle'] for t in toks))
        unique_words = len(set(t['word'] for t in toks))

        results[term] = {
            'n_tokens': n,
            'frac_of_total': round(n / total, 4) if total > 0 else 0,
            'unique_middles': unique_middles,
            'unique_words': unique_words,
            'tokens_per_middle': round(n / unique_middles, 2) if unique_middles > 0 else 0,
        }

    results['_total_tokens'] = total
    return results


def test_t9_bare_comparison(all_tokens):
    """T9: Bare terminal comparison vs terminated tokens."""
    print("  T9: Bare terminal comparison...")

    bare = [t for t in all_tokens if t['term'] == 'bare']
    terminated = [t for t in all_tokens if t['term'] != 'bare']

    def profile(toks):
        n = len(toks)
        if n == 0:
            return {}
        cat_counts = Counter(t['category'] for t in toks if t['category'])
        return {
            'n': n,
            'suffix_rate': round(sum(1 for t in toks if t['has_suffix']) / n, 4),
            'mode_A_rate': round(sum(1 for t in toks if t['suffix_mode'] == 'A') / n, 4),
            'has_head_rate': round(sum(1 for t in toks if t['head'] is not None) / n, 4),
            'has_modifier_rate': round(
                sum(1 for t in toks if any(c in MODIFIERS for c in (t['mods'] or ''))) / n, 4),
            'mean_middle_length': round(
                sum(len(t['middle']) for t in toks) / n, 2),
            'category_distribution': {c: round(v, 4) for c, v in
                                      normalize(cat_counts, ALL_CATEGORIES).items()},
            'mean_position': round(sum(t.get('line_pos_frac', 0.5) for t in toks) / n, 4),
            'line_initial_rate': round(
                sum(1 for t in toks if t.get('is_line_initial', False)) / n, 4),
            'line_final_rate': round(
                sum(1 for t in toks if t.get('is_line_final', False)) / n, 4),
        }

    bare_profile = profile(bare)
    term_profile = profile(terminated)

    # Category JSD between bare and terminated
    if bare_profile and term_profile:
        jsd_val = jsd(
            bare_profile.get('category_distribution', {}),
            term_profile.get('category_distribution', {}),
            ALL_CATEGORIES
        )
    else:
        jsd_val = None

    return {
        'bare': bare_profile,
        'terminated': term_profile,
        'jsd_bare_vs_terminated': round(jsd_val, 4) if jsd_val is not None else None,
    }


def test_t10_pairwise_distance(all_tokens):
    """T10: Pairwise JSD between all terminals + bare."""
    print("  T10: Pairwise behavioral distance...")

    # Build multi-dimensional profile for each terminal
    profiles = {}
    for term in TERMINAL_LABELS:
        toks = [t for t in all_tokens if t['term'] == term]
        n = len(toks)
        if n == 0:
            continue
        cat_counts = Counter(t['category'] for t in toks if t['category'])
        profiles[term] = normalize(cat_counts, ALL_CATEGORIES)

    # Compute pairwise JSD
    terms = sorted(profiles.keys())
    matrix = {}
    for i, t1 in enumerate(terms):
        for t2 in terms[i + 1:]:
            d = jsd(profiles[t1], profiles[t2], ALL_CATEGORIES)
            matrix[f'{t1}_vs_{t2}'] = round(d, 4)

    # Find most similar and most distant
    if matrix:
        most_similar = min(matrix.items(), key=lambda x: x[1])
        most_distant = max(matrix.items(), key=lambda x: x[1])
    else:
        most_similar = most_distant = (None, None)

    return {
        'pairwise_jsd': matrix,
        'most_similar': {'pair': most_similar[0], 'jsd': most_similar[1]},
        'most_distant': {'pair': most_distant[0], 'jsd': most_distant[1]},
    }


def test_t11_category_determination(all_tokens):
    """T11: Category determination power per TERMINAL (Cramer's V)."""
    print("  T11: Category determination power...")

    results = {}

    # For each terminal, build a contingency table of
    # MIDDLE_identity x CATEGORY to see how much the terminal
    # constrains category. Also compute the overall V(TERM, CATEGORY)
    # and per-terminal category entropy.

    # Overall TERMINAL x CATEGORY contingency
    overall_ct = defaultdict(lambda: defaultdict(int))
    for t in all_tokens:
        if t['category']:
            overall_ct[t['term']][t['category']] += 1

    overall_v = cramers_v(dict(overall_ct))

    # Per-terminal: how many categories does each terminal participate in?
    for term in TERMINAL_LABELS:
        toks = [t for t in all_tokens if t['term'] == term and t['category']]
        n = len(toks)
        if n == 0:
            continue

        cat_counts = Counter(t['category'] for t in toks)
        # Entropy
        total = sum(cat_counts.values())
        entropy = 0.0
        for c_count in cat_counts.values():
            p = c_count / total
            if p > 0:
                entropy -= p * math.log2(p)
        max_entropy = math.log2(len(ALL_CATEGORIES))

        # Concentration: fraction in dominant category
        dominant_frac = cat_counts.most_common(1)[0][1] / total if cat_counts else 0

        # Number of categories with >5% share
        significant_cats = sum(1 for c, cnt in cat_counts.items() if cnt / total > 0.05)

        results[term] = {
            'n_categorized': n,
            'entropy': round(entropy, 4),
            'max_entropy': round(max_entropy, 4),
            'normalized_entropy': round(entropy / max_entropy, 4) if max_entropy > 0 else 0,
            'dominant_frac': round(dominant_frac, 4),
            'significant_categories': significant_cats,
            'dominant_category': cat_counts.most_common(1)[0][0] if cat_counts else None,
        }

    results['_overall_cramers_v'] = round(overall_v, 4)
    return results


def test_t12_head_term_frame_matrix(all_tokens):
    """T12: Full HEAD x TERM category matrix (frame-level categories)."""
    print("  T12: HEAD x TERM frame category matrix...")

    head_labels = sorted(HEADS) + ['None']
    results = {}

    for h in head_labels:
        for term in TERMINAL_LABELS:
            toks = [t for t in all_tokens
                    if (t['head'] or 'None') == h and t['term'] == term
                    and t['category']]
            n = len(toks)
            if n < 5:
                continue

            cat_counts = Counter(t['category'] for t in toks)
            dominant = cat_counts.most_common(1)[0]

            # Suffix rate for this frame
            all_frame = [t for t in all_tokens
                         if (t['head'] or 'None') == h and t['term'] == term]
            n_all = len(all_frame)
            suffix_rate = sum(1 for t in all_frame if t['has_suffix']) / n_all if n_all > 0 else 0

            frame_key = f'{h}->{term}'
            results[frame_key] = {
                'n_tokens': n_all,
                'n_categorized': n,
                'dominant_category': dominant[0],
                'dominant_frac': round(dominant[1] / n, 4),
                'category_dist': {c: round(v, 4) for c, v in
                                  normalize(cat_counts, ALL_CATEGORIES).items()},
                'suffix_rate': round(suffix_rate, 4),
            }

    return results


# ============================================================
# Summary and Synthesis
# ============================================================

def build_synthesis(results):
    """Build synthesis from all test results."""
    print("\n" + "=" * 70)
    print("SYNTHESIS: TERMINAL FUNCTIONAL TAXONOMY")
    print("=" * 70)

    t1 = results['T1_category_profile']
    t2 = results['T2_opacity']
    t5 = results['T5_hazard_profile']
    t8 = results['T8_population_census']
    t10 = results['T10_pairwise_distance']
    t11 = results['T11_category_determination']

    # --- Population summary ---
    print("\n--- Population Census ---")
    for term in TERMINAL_LABELS:
        p = t8.get(term, {})
        print(f"  {term:5s}: {p.get('n_tokens', 0):6d} tokens ({p.get('frac_of_total', 0):.1%}), "
              f"{p.get('unique_middles', 0)} unique MIDDLEs, "
              f"{p.get('tokens_per_middle', 0):.1f} tok/type")

    # --- Opacity gradient ---
    print("\n--- Opacity Gradient (suffix rate) ---")
    opacity_order = sorted(
        [(term, t2[term]['suffix_rate']) for term in TERMINAL_LABELS if term in t2],
        key=lambda x: x[1]
    )
    for term, rate in opacity_order:
        tier = t2[term]['opacity_tier']
        print(f"  {term:5s}: {rate:.1%} suffix -> {tier}")

    # --- Category dominance ---
    print("\n--- Category Profile ---")
    baseline = t1.get('_baseline', {})
    print(f"  Baseline: ", end="")
    for c in ALL_CATEGORIES:
        print(f"{c[:4]}={baseline.get(c, 0):.1%} ", end="")
    print()

    for term in TERMINAL_LABELS:
        td = t1.get(term, {})
        dom = td.get('dominant_category', '?')
        dist = td.get('distribution', {})
        jsd_val = td.get('jsd_vs_baseline', 0)
        dom_frac = dist.get(dom, 0)
        print(f"  {term:5s}: dominant={dom:12s} ({dom_frac:.1%}), "
              f"JSD vs baseline={jsd_val:.4f}")

    # --- Category determination power ---
    print("\n--- Category Determination Power ---")
    overall_v = t11.get('_overall_cramers_v', 0)
    print(f"  Overall TERMINAL x CATEGORY Cramer's V = {overall_v:.4f}")
    for term in TERMINAL_LABELS:
        td = t11.get(term, {})
        ent = td.get('normalized_entropy', 0)
        dom = td.get('dominant_category', '?')
        dom_f = td.get('dominant_frac', 0)
        sig_cats = td.get('significant_categories', 0)
        print(f"  {term:5s}: norm_entropy={ent:.3f}, dominant={dom:12s} ({dom_f:.1%}), "
              f"sig_cats={sig_cats}")

    # --- Hazard profile ---
    print("\n--- Hazard Profile (as source) ---")
    total_viol = t5.get('_total_violations', 0)
    print(f"  Total violations: {total_viol}")
    for term in TERMINAL_LABELS:
        hd = t5.get(term, {})
        src_rate = hd.get('as_source_rate', 0)
        src_viol = hd.get('as_source_violations', 0)
        share = hd.get('share_of_total_violations', 0)
        print(f"  {term:5s}: rate={src_rate:.4%}, violations={src_viol}, "
              f"share={share:.1%}")

    # --- Line position ---
    print("\n--- Line Position ---")
    t6 = results['T6_line_position']
    for term in TERMINAL_LABELS:
        tp = t6.get(term, {})
        mp = tp.get('mean_position', 0)
        init = tp.get('line_initial_rate', 0)
        final = tp.get('line_final_rate', 0)
        print(f"  {term:5s}: mean_pos={mp:.3f}, initial={init:.1%}, final={final:.1%}")

    # --- Pairwise distances ---
    print("\n--- Pairwise Category JSD ---")
    ms = t10.get('most_similar', {})
    md = t10.get('most_distant', {})
    print(f"  Most similar: {ms.get('pair', '?')} (JSD={ms.get('jsd', 0):.4f})")
    print(f"  Most distant: {md.get('pair', '?')} (JSD={md.get('jsd', 0):.4f})")

    # --- Functional grouping attempt ---
    print("\n--- Proposed Functional Groups ---")

    # Group by dominant category + opacity
    groups = defaultdict(list)
    for term in TERMINAL_LABELS:
        dom = t1.get(term, {}).get('dominant_category', 'UNK')
        opac = t2.get(term, {}).get('opacity_tier', 'UNK')
        groups[(dom, opac)].append(term)

    for (dom, opac), members in sorted(groups.items()):
        print(f"  {dom:12s} + {opac:16s}: {members}")

    print()

    synthesis = {
        'total_tokens': t8.get('_total_tokens', 0),
        'overall_cramers_v': overall_v,
        'opacity_gradient': [(term, t2.get(term, {}).get('suffix_rate', 0))
                             for term in TERMINAL_LABELS if term in t2],
        'most_similar_pair': ms,
        'most_distant_pair': md,
    }
    return synthesis


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 535: TERMINAL Functional Taxonomy")
    print("=" * 50)

    print("\nCollecting data...")
    all_tokens, adjacency_pairs, tokens_by_folio_line = collect_data()
    print(f"  {len(all_tokens)} tokens, {len(adjacency_pairs)} adjacency pairs")

    results = {}

    results['T1_category_profile'] = test_t1_category_profile(all_tokens)
    results['T2_opacity'] = test_t2_opacity(all_tokens)
    results['T3_head_compatibility'] = test_t3_head_compatibility(all_tokens)
    results['T4_modifier_compatibility'] = test_t4_modifier_compatibility(all_tokens)
    results['T5_hazard_profile'] = test_t5_hazard_profile(adjacency_pairs, all_tokens)
    results['T6_line_position'] = test_t6_line_position(all_tokens)
    results['T7_prefix_selectivity'] = test_t7_prefix_selectivity(all_tokens)
    results['T8_population_census'] = test_t8_population_census(all_tokens)
    results['T9_bare_comparison'] = test_t9_bare_comparison(all_tokens)
    results['T10_pairwise_distance'] = test_t10_pairwise_distance(all_tokens)
    results['T11_category_determination'] = test_t11_category_determination(all_tokens)
    results['T12_head_term_frame_matrix'] = test_t12_head_term_frame_matrix(all_tokens)

    synthesis = build_synthesis(results)
    results['synthesis'] = synthesis

    # Save results
    outpath = PROJECT_ROOT / 'phases' / 'TERM_FUNCTIONAL_TAXONOMY' / 'results' / 'term_functional_taxonomy.json'
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with open(outpath, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {outpath}")


if __name__ == '__main__':
    main()
