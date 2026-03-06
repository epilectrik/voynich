"""
Phase 537: DISPLACED_HEAD_GRAMMAR
==================================
C1493 found that 35.7% of "headless" compound MIDDLEs contain a HEAD atom
{a,e,o,k,t} at a non-initial position -- a "displaced HEAD". This phase asks:

Is MOD+HEAD+TERM (or similar) a legitimate alternative compositional order?
What governs HEAD displacement? Does the displaced HEAD or the pseudo-HEAD
(first atom) better predict the token's category?

Core question: Are displaced-HEAD tokens actually a DIFFERENT compositional
mode, or are they true headless tokens where a HEAD-set character happens
to appear in a non-HEAD functional role?

12 analyses (a-l):
  a. Population census of displaced-HEAD tokens
  b. What precedes the displaced HEAD?
  c. Compositional patterns (slot templates)
  d. Which HEADs get displaced?
  e. Category comparison: displaced vs canonical HEAD
  f. PREFIX comparison
  g. Line position
  h. Hazard profile
  i. Suffix rate comparison
  j. Displacement predictors
  k. True alternative mode or coincidence?
  l. Displaced HEAD vs pseudo-HEAD category prediction
"""

import sys, os, json
import numpy as np
from collections import Counter, defaultdict
from scipy import stats
from scipy.spatial.distance import jensenshannon
from scipy.stats import chi2_contingency

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier,
    decompose_middle_hmt,
)

# ── Constants ──────────────────────────────────────────────────────────
HEAD_SET = {'a', 'e', 'o', 'k', 't'}
TERMINALS = {'y', 'l', 'r', 'h', 'm', 'n'}
MODIFIER_SET = {'p', 'c', 'i', 'f', 'd', 's'}
EXTENSIBLE = {'e', 'i'}

# HIGH hazard frames from C1448
HIGH_HAZARD_FRAMES = {
    ('o', 'bare'), ('d', 'y'), ('a', 'l'), ('a', 'r'),
    ('o', 'r'), ('e', 'e'), ('a', 'n'),
}


def atomize(middle):
    """Split MIDDLE into atoms respecting e/i extensibility (C1197)."""
    atoms = []
    i = 0
    while i < len(middle):
        ch = middle[i]
        if ch in EXTENSIBLE:
            run = ch
            j = i + 1
            while j < len(middle) and middle[j] == ch:
                run += ch
                j += 1
            atoms.append(run)
            i = j
        else:
            atoms.append(ch)
            i += 1
    return atoms


def classify_atom(a):
    """Classify an atom by its canonical slot."""
    base = a[0]
    if base in HEAD_SET:
        return 'H'
    elif base in MODIFIER_SET:
        return 'M'
    elif base in TERMINALS:
        return 'T'
    return '?'


def load_data():
    """Load and filter Currier B tokens with morphological decomposition."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    tokens = []
    for t in tx.currier_b():
        if '*' in t.word or not t.word.strip():
            continue
        m = morph.extract(t.word)
        if not m.middle or len(m.middle) < 2:
            continue  # Need compound MIDDLEs (2+ chars)

        head, mods, term, frame = decompose_middle_hmt(m.middle)
        cat = cc.classify(m.middle)
        atoms = atomize(m.middle)

        # Classify each atom position
        atom_slots = [classify_atom(a) for a in atoms]

        # Find displaced HEADs (HEAD atoms at non-initial position)
        displaced_heads = []
        for idx, a in enumerate(atoms):
            if idx == 0:
                continue  # Skip position 0
            base = a[0]
            if base in HEAD_SET:
                displaced_heads.append({
                    'atom': a,
                    'base': base,
                    'position': idx,
                    'position_norm': idx / (len(atoms) - 1) if len(atoms) > 1 else 0,
                })

        is_headless = head is None
        has_displaced_head = len(displaced_heads) > 0 and is_headless

        tokens.append({
            'word': t.word,
            'folio': t.folio,
            'line': getattr(t, 'line', None),
            'section': getattr(t, 'section', ''),
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'articulator': m.articulator,
            'head': head,
            'mods': mods,
            'term': term,
            'frame': frame,
            'category': cat,
            'first_char': m.middle[0] if m.middle else None,
            'atoms': atoms,
            'atom_slots': atom_slots,
            'is_headless': is_headless,
            'displaced_heads': displaced_heads,
            'has_displaced_head': has_displaced_head,
            'displaced_head_atom': displaced_heads[0]['base'] if displaced_heads else None,
            'line_initial': getattr(t, 'line_initial', False),
            'line_final': getattr(t, 'line_final', False),
            'par_initial': getattr(t, 'par_initial', False),
            'par_final': getattr(t, 'par_final', False),
        })

    return tokens


def add_line_positions(tokens):
    """Compute normalized line position for each token."""
    line_groups = defaultdict(list)
    for i, t in enumerate(tokens):
        key = (t['folio'], t.get('line', ''))
        line_groups[key].append(i)

    for key, indices in line_groups.items():
        n = len(indices)
        for rank, idx in enumerate(indices):
            tokens[idx]['line_pos'] = rank / max(n - 1, 1) if n > 1 else 0.5
            tokens[idx]['line_length'] = n

    return tokens


# ═══════════════════════════════════════════════════════════════════════
# POPULATIONS
# ═══════════════════════════════════════════════════════════════════════

def get_populations(tokens):
    """Split tokens into four populations for comparison."""
    canonical_headed = [t for t in tokens if not t['is_headless']]
    headless_displaced = [t for t in tokens if t['is_headless'] and t['has_displaced_head']]
    headless_genuine = [t for t in tokens if t['is_headless'] and not t['has_displaced_head']]
    all_headless = [t for t in tokens if t['is_headless']]
    return canonical_headed, headless_displaced, headless_genuine, all_headless


# ═══════════════════════════════════════════════════════════════════════
# ANALYSES
# ═══════════════════════════════════════════════════════════════════════

def analysis_a_census(tokens, canonical, displaced, genuine, all_headless):
    """(a) Population census of displaced-HEAD tokens."""
    # Count by displaced HEAD type
    dh_by_head = Counter(t['displaced_head_atom'] for t in displaced)

    # Count by MIDDLE type
    dh_types = set(t['middle'] for t in displaced)
    genuine_types = set(t['middle'] for t in genuine)

    # Position of displaced HEAD within atoms
    pos_dist = Counter()
    for t in displaced:
        for dh in t['displaced_heads']:
            pos_dist[dh['position']] += 1

    # Most common displaced-HEAD MIDDLEs
    dh_middle_counts = Counter(t['middle'] for t in displaced)

    # Fraction of headless that have displaced HEAD
    displaced_frac_tokens = len(displaced) / len(all_headless) if all_headless else 0
    displaced_frac_types = len(dh_types) / len(set(t['middle'] for t in all_headless)) if all_headless else 0

    # Count tokens with multiple displaced HEADs
    multi_dh = sum(1 for t in displaced if len(t['displaced_heads']) > 1)

    result = {
        'total_compound': len(tokens),
        'canonical_headed': len(canonical),
        'all_headless': len(all_headless),
        'displaced_head_tokens': len(displaced),
        'displaced_head_types': len(dh_types),
        'genuine_headless_tokens': len(genuine),
        'genuine_headless_types': len(genuine_types),
        'displaced_fraction_of_headless_tokens': round(displaced_frac_tokens, 4),
        'displaced_fraction_of_headless_types': round(displaced_frac_types, 4),
        'multi_displaced_head_count': multi_dh,
        'displaced_head_by_atom': {
            a: {'count': c, 'fraction': round(c / len(displaced), 4)}
            for a, c in sorted(dh_by_head.items(), key=lambda x: -x[1])
        },
        'displaced_head_position_distribution': {
            str(p): c for p, c in sorted(pos_dist.items())
        },
        'top_20_displaced_middles': {
            mid: count for mid, count in dh_middle_counts.most_common(20)
        },
    }
    return result


def analysis_b_what_precedes(tokens, displaced):
    """(b) What atom precedes the displaced HEAD?"""
    preceding_atoms = Counter()
    preceding_classes = Counter()
    preceding_by_dh = defaultdict(Counter)

    for t in displaced:
        for dh in t['displaced_heads']:
            pos = dh['position']
            if pos > 0:
                preceding = t['atoms'][pos - 1]
                prec_base = preceding[0]
                preceding_atoms[preceding] += 1

                prec_class = classify_atom(preceding)
                preceding_classes[prec_class] += 1
                preceding_by_dh[dh['base']][preceding] += 1

    total = sum(preceding_classes.values())
    result = {
        'preceding_atom_distribution': {
            a: {'count': c, 'fraction': round(c / total, 4)}
            for a, c in sorted(preceding_atoms.items(), key=lambda x: -x[1])[:15]
        },
        'preceding_class_distribution': {
            cl: {'count': c, 'fraction': round(c / total, 4)}
            for cl, c in sorted(preceding_classes.items(), key=lambda x: -x[1])
        },
        'preceding_by_displaced_head': {
            dh: {a: c for a, c in sorted(counts.items(), key=lambda x: -x[1])[:5]}
            for dh, counts in sorted(preceding_by_dh.items())
        },
        'total_observed': total,
    }
    return result


def analysis_c_compositional_patterns(displaced):
    """(c) Structural templates for displaced-HEAD tokens."""
    patterns = Counter()
    pattern_examples = defaultdict(list)

    for t in displaced:
        pattern = ''.join(t['atom_slots'])
        patterns[pattern] += 1
        if len(pattern_examples[pattern]) < 3:
            pattern_examples[pattern].append(t['middle'])

    total = sum(patterns.values())

    # Group by pattern family
    families = defaultdict(int)
    for pat, count in patterns.items():
        # Count HEAD positions
        head_positions = [i for i, c in enumerate(pat) if c == 'H']
        if len(head_positions) == 1:
            pos = head_positions[0]
            if pos == len(pat) - 1:
                families['...+H_FINAL'] += count
            else:
                families[f'...+H_pos{pos}+...'] += count
        elif len(head_positions) > 1:
            families['MULTI_HEAD'] += count
        else:
            families['NO_HEAD_VISIBLE'] += count  # shouldn't happen in displaced

    result = {
        'pattern_distribution': {
            p: {'count': c, 'fraction': round(c / total, 4),
                'examples': pattern_examples[p]}
            for p, c in sorted(patterns.items(), key=lambda x: -x[1])[:20]
        },
        'pattern_families': {
            f: {'count': c, 'fraction': round(c / total, 4)}
            for f, c in sorted(families.items(), key=lambda x: -x[1])
        },
        'unique_patterns': len(patterns),
        'total_tokens': total,
    }
    return result


def analysis_d_which_heads_displaced(displaced, canonical):
    """(d) Which HEADs are displaced and at what rate?"""
    # Displaced HEAD atom distribution
    dh_counts = Counter(t['displaced_head_atom'] for t in displaced)
    total_dh = sum(dh_counts.values())

    # Canonical HEAD distribution for comparison
    ch_counts = Counter(t['head'] for t in canonical if t['head'])
    total_ch = sum(ch_counts.values())

    # Enrichment: displaced vs canonical rates
    enrichments = {}
    for h in HEAD_SET:
        dh_frac = dh_counts.get(h, 0) / total_dh if total_dh > 0 else 0
        ch_frac = ch_counts.get(h, 0) / total_ch if total_ch > 0 else 0
        enrichments[h] = {
            'displaced_fraction': round(dh_frac, 4),
            'canonical_fraction': round(ch_frac, 4),
            'enrichment': round(dh_frac / ch_frac, 3) if ch_frac > 0 else float('inf'),
        }

    # Which HEADs are most concentrated at specific positions?
    pos_by_head = defaultdict(Counter)
    for t in displaced:
        for dh in t['displaced_heads']:
            pos_by_head[dh['base']][dh['position']] += 1

    result = {
        'displaced_head_counts': {
            h: {'count': dh_counts.get(h, 0),
                'fraction': round(dh_counts.get(h, 0) / total_dh, 4) if total_dh > 0 else 0}
            for h in sorted(HEAD_SET)
        },
        'canonical_head_counts': {
            h: {'count': ch_counts.get(h, 0),
                'fraction': round(ch_counts.get(h, 0) / total_ch, 4) if total_ch > 0 else 0}
            for h in sorted(HEAD_SET)
        },
        'enrichment_displaced_vs_canonical': enrichments,
        'position_by_head': {
            h: {str(p): c for p, c in sorted(pos_data.items())}
            for h, pos_data in sorted(pos_by_head.items())
        },
    }
    return result


def analysis_e_category_comparison(tokens, canonical, displaced, genuine):
    """(e) Category comparison: displaced vs canonical HEAD."""
    cc = CategoryClassifier()
    all_cats = sorted(cc.CATEGORIES)

    def get_cat_dist(token_list):
        cats = Counter(t['category'] for t in token_list if t['category'])
        total = sum(cats.values())
        return cats, total

    # Category distributions for each population
    can_cats, can_total = get_cat_dist(canonical)
    dis_cats, dis_total = get_cat_dist(displaced)
    gen_cats, gen_total = get_cat_dist(genuine)

    # Per-displaced-HEAD category profiles
    per_dh = {}
    for h in sorted(HEAD_SET):
        subset = [t for t in displaced if t['displaced_head_atom'] == h]
        cats, total = get_cat_dist(subset)
        if total > 0:
            per_dh[h] = {
                'distribution': {c: round(cats.get(c, 0) / total, 4) for c in all_cats},
                'dominant': cats.most_common(1)[0][0] if cats else None,
                'n': total,
            }

    # Canonical HEAD profiles for comparison
    per_canonical = {}
    for h in sorted(HEAD_SET):
        subset = [t for t in canonical if t['head'] == h]
        cats, total = get_cat_dist(subset)
        if total > 0:
            per_canonical[h] = {
                'distribution': {c: round(cats.get(c, 0) / total, 4) for c in all_cats},
                'dominant': cats.most_common(1)[0][0] if cats else None,
                'n': total,
            }

    # JSD: displaced-HEAD-h vs canonical-HEAD-h for each h
    jsd_same_head = {}
    for h in sorted(HEAD_SET):
        if h in per_dh and h in per_canonical:
            vec_d = np.array([per_dh[h]['distribution'].get(c, 0) for c in all_cats])
            vec_c = np.array([per_canonical[h]['distribution'].get(c, 0) for c in all_cats])
            # Ensure normalization
            if vec_d.sum() > 0:
                vec_d = vec_d / vec_d.sum()
            if vec_c.sum() > 0:
                vec_c = vec_c / vec_c.sum()
            jsd_same_head[h] = round(float(jensenshannon(vec_d, vec_c)), 4)

    # JSD: displaced aggregate vs canonical aggregate
    vec_dis = np.array([dis_cats.get(c, 0) for c in all_cats], dtype=float)
    vec_can = np.array([can_cats.get(c, 0) for c in all_cats], dtype=float)
    vec_gen = np.array([gen_cats.get(c, 0) for c in all_cats], dtype=float)
    for v in [vec_dis, vec_can, vec_gen]:
        s = v.sum()
        if s > 0:
            v /= s
    jsd_dis_vs_can = round(float(jensenshannon(vec_dis, vec_can)), 4)
    jsd_dis_vs_gen = round(float(jensenshannon(vec_dis, vec_gen)), 4)
    jsd_gen_vs_can = round(float(jensenshannon(vec_gen, vec_can)), 4)

    result = {
        'displaced_category_dist': {
            c: round(dis_cats.get(c, 0) / dis_total, 4) if dis_total > 0 else 0
            for c in all_cats
        },
        'canonical_category_dist': {
            c: round(can_cats.get(c, 0) / can_total, 4) if can_total > 0 else 0
            for c in all_cats
        },
        'genuine_headless_category_dist': {
            c: round(gen_cats.get(c, 0) / gen_total, 4) if gen_total > 0 else 0
            for c in all_cats
        },
        'jsd_displaced_vs_canonical': jsd_dis_vs_can,
        'jsd_displaced_vs_genuine_headless': jsd_dis_vs_gen,
        'jsd_genuine_vs_canonical': jsd_gen_vs_can,
        'per_displaced_head_profiles': per_dh,
        'per_canonical_head_profiles': per_canonical,
        'jsd_same_head_displaced_vs_canonical': jsd_same_head,
    }
    return result


def analysis_f_prefix_comparison(canonical, displaced, genuine):
    """(f) PREFIX comparison across populations."""
    def get_pfx_dist(tlist):
        counts = Counter(t['prefix'] or 'BARE' for t in tlist)
        total = sum(counts.values())
        return counts, total

    can_pfx, can_total = get_pfx_dist(canonical)
    dis_pfx, dis_total = get_pfx_dist(displaced)
    gen_pfx, gen_total = get_pfx_dist(genuine)

    # Does displaced pattern with canonical or headless?
    # JSD comparison
    all_pfx = sorted(set(list(can_pfx.keys()) + list(dis_pfx.keys()) + list(gen_pfx.keys())))
    vec_can = np.array([can_pfx.get(p, 0) / can_total for p in all_pfx])
    vec_dis = np.array([dis_pfx.get(p, 0) / dis_total for p in all_pfx])
    vec_gen = np.array([gen_pfx.get(p, 0) / gen_total for p in all_pfx])

    jsd_dis_can = round(float(jensenshannon(vec_dis, vec_can)), 4) if dis_total > 0 and can_total > 0 else None
    jsd_dis_gen = round(float(jensenshannon(vec_dis, vec_gen)), 4) if dis_total > 0 and gen_total > 0 else None

    # Per-displaced-HEAD PREFIX profiles
    per_dh_pfx = {}
    for h in sorted(HEAD_SET):
        subset = [t for t in displaced if t['displaced_head_atom'] == h]
        if subset:
            pfx_c = Counter(t['prefix'] or 'BARE' for t in subset)
            total = sum(pfx_c.values())
            per_dh_pfx[h] = {
                p: round(c / total, 4)
                for p, c in sorted(pfx_c.items(), key=lambda x: -x[1])[:5]
            }

    result = {
        'displaced_prefix_top10': {
            p: {'count': c, 'fraction': round(c / dis_total, 4)}
            for p, c in sorted(dis_pfx.items(), key=lambda x: -x[1])[:10]
        },
        'genuine_prefix_top10': {
            p: {'count': c, 'fraction': round(c / gen_total, 4)}
            for p, c in sorted(gen_pfx.items(), key=lambda x: -x[1])[:10]
        },
        'canonical_prefix_top10': {
            p: {'count': c, 'fraction': round(c / can_total, 4)}
            for p, c in sorted(can_pfx.items(), key=lambda x: -x[1])[:10]
        },
        'jsd_displaced_vs_canonical': jsd_dis_can,
        'jsd_displaced_vs_genuine_headless': jsd_dis_gen,
        'displaced_patterns_with': 'GENUINE_HEADLESS' if (jsd_dis_gen or 999) < (jsd_dis_can or 999) else 'CANONICAL_HEADED',
        'per_displaced_head_prefix': per_dh_pfx,
        'displaced_bare_rate': round(dis_pfx.get('BARE', 0) / dis_total, 4) if dis_total > 0 else 0,
        'genuine_bare_rate': round(gen_pfx.get('BARE', 0) / gen_total, 4) if gen_total > 0 else 0,
        'canonical_bare_rate': round(can_pfx.get('BARE', 0) / can_total, 4) if can_total > 0 else 0,
    }
    return result


def analysis_g_line_position(canonical, displaced, genuine):
    """(g) Line position of displaced-HEAD tokens."""
    def pos_stats(tlist):
        positions = [t['line_pos'] for t in tlist if 'line_pos' in t]
        initial = sum(1 for t in tlist if t.get('line_initial'))
        final = sum(1 for t in tlist if t.get('line_final'))
        n = len(tlist)
        return {
            'mean_pos': round(np.mean(positions), 4) if positions else None,
            'initial_rate': round(initial / n, 4) if n > 0 else 0,
            'final_rate': round(final / n, 4) if n > 0 else 0,
            'n': n,
        }

    can_stats = pos_stats(canonical)
    dis_stats = pos_stats(displaced)
    gen_stats = pos_stats(genuine)

    # Mann-Whitney: displaced vs canonical
    dis_pos = [t['line_pos'] for t in displaced if 'line_pos' in t]
    can_pos = [t['line_pos'] for t in canonical if 'line_pos' in t]
    gen_pos = [t['line_pos'] for t in genuine if 'line_pos' in t]

    mw_dis_can = stats.mannwhitneyu(dis_pos, can_pos, alternative='two-sided') if dis_pos and can_pos else (0, 1)
    mw_dis_gen = stats.mannwhitneyu(dis_pos, gen_pos, alternative='two-sided') if dis_pos and gen_pos else (0, 1)

    result = {
        'canonical_position': can_stats,
        'displaced_position': dis_stats,
        'genuine_headless_position': gen_stats,
        'mw_displaced_vs_canonical_p': float(mw_dis_can[1]),
        'mw_displaced_vs_genuine_p': float(mw_dis_gen[1]),
    }
    return result


def analysis_h_hazard_profile(canonical, displaced, genuine):
    """(h) Hazard profile using frame-based analysis (C1446-C1451)."""
    def get_frame(t):
        initial = t['first_char']
        if t['term'] and t['term'] != 'bare':
            terminal = t['term'][-1]
        else:
            terminal = 'bare'
        return (initial, terminal)

    def hazard_stats(tlist, label):
        frames = [get_frame(t) for t in tlist]
        high_count = sum(1 for f in frames if f in HIGH_HAZARD_FRAMES)
        r_term = sum(1 for f in frames if f[1] == 'r')
        n = len(tlist)
        return {
            'n': n,
            'high_frame_fraction': round(high_count / n, 4) if n > 0 else 0,
            'r_terminal_fraction': round(r_term / n, 4) if n > 0 else 0,
        }

    can_haz = hazard_stats(canonical, 'canonical')
    dis_haz = hazard_stats(displaced, 'displaced')
    gen_haz = hazard_stats(genuine, 'genuine')

    # Per displaced-HEAD hazard profile
    per_dh = {}
    for h in sorted(HEAD_SET):
        subset = [t for t in displaced if t['displaced_head_atom'] == h]
        if subset:
            per_dh[h] = hazard_stats(subset, f'displaced-{h}')

    result = {
        'canonical_hazard': can_haz,
        'displaced_hazard': dis_haz,
        'genuine_headless_hazard': gen_haz,
        'per_displaced_head_hazard': per_dh,
    }
    return result


def analysis_i_suffix_rate(canonical, displaced, genuine):
    """(i) Suffix rate comparison."""
    def suffix_stats(tlist):
        n = len(tlist)
        has_sfx = sum(1 for t in tlist if t['suffix'])
        return {
            'n': n,
            'suffix_rate': round(has_sfx / n, 4) if n > 0 else 0,
        }

    can_sfx = suffix_stats(canonical)
    dis_sfx = suffix_stats(displaced)
    gen_sfx = suffix_stats(genuine)

    # Per displaced HEAD
    per_dh = {}
    for h in sorted(HEAD_SET):
        subset = [t for t in displaced if t['displaced_head_atom'] == h]
        if subset:
            per_dh[h] = suffix_stats(subset)

    # Per pseudo-HEAD (first atom) of displaced
    per_pseudo = {}
    for a in sorted(set(t['first_char'] for t in displaced)):
        subset = [t for t in displaced if t['first_char'] == a]
        if subset:
            per_pseudo[a] = suffix_stats(subset)

    result = {
        'canonical_suffix': can_sfx,
        'displaced_suffix': dis_sfx,
        'genuine_headless_suffix': gen_sfx,
        'per_displaced_head_suffix': per_dh,
        'per_pseudo_head_suffix': per_pseudo,
    }
    return result


def analysis_j_displacement_predictors(displaced, genuine, all_headless):
    """(j) What predicts HEAD displacement?"""
    # Which first atoms (pseudo-HEADs) are associated with displacement?
    pseudo_displaced_rate = {}
    for a in sorted(set(t['first_char'] for t in all_headless)):
        total_a = sum(1 for t in all_headless if t['first_char'] == a)
        displaced_a = sum(1 for t in displaced if t['first_char'] == a)
        if total_a >= 10:
            pseudo_displaced_rate[a] = {
                'total': total_a,
                'displaced': displaced_a,
                'rate': round(displaced_a / total_a, 4),
            }

    # Which terminals are associated with displacement?
    term_displaced_rate = {}
    for term_char in sorted(TERMINALS | {'bare'}):
        total_t = sum(1 for t in all_headless if (t['term'] or 'bare') == term_char or
                      (t['term'] and t['term'][-1] == term_char))
        displaced_t = sum(1 for t in displaced if (t['term'] or 'bare') == term_char or
                          (t['term'] and t['term'][-1] == term_char))
        if total_t >= 10:
            term_displaced_rate[term_char] = {
                'total': total_t,
                'displaced': displaced_t,
                'rate': round(displaced_t / total_t, 4),
            }

    # Which PREFIXes are associated with displacement?
    pfx_displaced_rate = {}
    for pfx in sorted(set(t['prefix'] or 'BARE' for t in all_headless)):
        total_p = sum(1 for t in all_headless if (t['prefix'] or 'BARE') == pfx)
        displaced_p = sum(1 for t in displaced if (t['prefix'] or 'BARE') == pfx)
        if total_p >= 10:
            pfx_displaced_rate[pfx] = {
                'total': total_p,
                'displaced': displaced_p,
                'rate': round(displaced_p / total_p, 4),
            }

    # MIDDLE length and displacement
    dis_lengths = [len(t['middle']) for t in displaced]
    gen_lengths = [len(t['middle']) for t in genuine]
    length_diff = round(np.mean(dis_lengths) - np.mean(gen_lengths), 3) if dis_lengths and gen_lengths else None

    result = {
        'displacement_rate_by_pseudo_head': pseudo_displaced_rate,
        'displacement_rate_by_terminal': term_displaced_rate,
        'displacement_rate_by_prefix': pfx_displaced_rate,
        'mean_length_displaced': round(np.mean(dis_lengths), 3) if dis_lengths else None,
        'mean_length_genuine': round(np.mean(gen_lengths), 3) if gen_lengths else None,
        'length_difference': length_diff,
    }
    return result


def analysis_k_alternative_mode(displaced, genuine, canonical):
    """(k) Is displaced HEAD a different compositional mode?"""
    # Key test: if displaced-HEAD tokens were TRULY headed with HEAD at
    # non-initial position, they should share category profile with their
    # HEAD domain. If the HEAD-set character is NOT functioning as HEAD,
    # they should pattern with the pseudo-HEAD domain.

    # For each displaced-HEAD token, get category from:
    # 1. The displaced HEAD atom (e.g., 'e' in 'de' -> should predict THERMAL)
    # 2. The pseudo-HEAD first atom (e.g., 'd' in 'de' -> should predict CONTAINMENT)
    # 3. Actual category of the token

    cc = CategoryClassifier()
    atom_categories = cc.ATOM_CATEGORIES if hasattr(cc, 'ATOM_CATEGORIES') else {}

    # Manually build atom->category from ATOM_GLOSSES -> GLOSS_TO_CATEGORY
    atom_to_cat = {}
    for atom, gloss in cc.ATOM_GLOSSES.items():
        if gloss in cc.GLOSS_TO_CATEGORY:
            atom_to_cat[atom] = cc.GLOSS_TO_CATEGORY[gloss]

    pseudo_correct = 0  # pseudo-HEAD predicts actual category
    displaced_correct = 0  # displaced HEAD predicts actual category
    both_correct = 0
    neither_correct = 0
    total_testable = 0

    per_case = []

    for t in displaced:
        actual = t['category']
        if not actual:
            continue
        pseudo_head = t['first_char']
        dh = t['displaced_head_atom']

        pseudo_pred = atom_to_cat.get(pseudo_head)
        dh_pred = atom_to_cat.get(dh)

        if pseudo_pred and dh_pred:
            total_testable += 1
            p_match = (pseudo_pred == actual)
            d_match = (dh_pred == actual)

            if p_match:
                pseudo_correct += 1
            if d_match:
                displaced_correct += 1
            if p_match and d_match:
                both_correct += 1
            if not p_match and not d_match:
                neither_correct += 1

    # The key ratio: if pseudo > displaced, the first atom is the real
    # domain selector and the HEAD-set character is NOT functioning as HEAD.
    result = {
        'total_testable': total_testable,
        'pseudo_head_correct': pseudo_correct,
        'pseudo_head_accuracy': round(pseudo_correct / total_testable, 4) if total_testable > 0 else 0,
        'displaced_head_correct': displaced_correct,
        'displaced_head_accuracy': round(displaced_correct / total_testable, 4) if total_testable > 0 else 0,
        'both_correct': both_correct,
        'neither_correct': neither_correct,
        'verdict': (
            'PSEUDO_HEAD_DOMINATES' if pseudo_correct > displaced_correct * 1.5
            else 'DISPLACED_HEAD_DOMINATES' if displaced_correct > pseudo_correct * 1.5
            else 'AMBIGUOUS'
        ),
        'accuracy_ratio': round(pseudo_correct / displaced_correct, 3) if displaced_correct > 0 else float('inf'),
    }
    return result


def analysis_l_displaced_vs_pseudo_category(displaced, canonical, genuine):
    """(l) Detailed comparison: displaced HEAD vs pseudo-HEAD as category predictor."""
    cc = CategoryClassifier()
    all_cats = sorted(cc.CATEGORIES)

    # Build atom->expected category mapping
    atom_to_cat = {}
    for atom, gloss in cc.ATOM_GLOSSES.items():
        if gloss in cc.GLOSS_TO_CATEGORY:
            atom_to_cat[atom] = cc.GLOSS_TO_CATEGORY[gloss]

    # For each displaced-HEAD atom, compare:
    # actual category distribution of displaced tokens with that HEAD
    # vs canonical tokens with same HEAD in position 0
    comparisons = {}
    for h in sorted(HEAD_SET):
        displaced_h = [t for t in displaced if t['displaced_head_atom'] == h and t['category']]
        canonical_h = [t for t in canonical if t['head'] == h and t['category']]

        if not displaced_h or not canonical_h:
            continue

        dis_cats = Counter(t['category'] for t in displaced_h)
        can_cats = Counter(t['category'] for t in canonical_h)

        dis_total = sum(dis_cats.values())
        can_total = sum(can_cats.values())

        vec_d = np.array([dis_cats.get(c, 0) / dis_total for c in all_cats])
        vec_c = np.array([can_cats.get(c, 0) / can_total for c in all_cats])

        jsd = float(jensenshannon(vec_d, vec_c))

        # Do they share the same dominant category?
        dis_dom = dis_cats.most_common(1)[0][0]
        can_dom = can_cats.most_common(1)[0][0]

        comparisons[h] = {
            'displaced_dominant': dis_dom,
            'canonical_dominant': can_dom,
            'same_dominant': dis_dom == can_dom,
            'jsd': round(jsd, 4),
            'displaced_n': dis_total,
            'canonical_n': can_total,
            'displaced_dist': {c: round(dis_cats.get(c, 0) / dis_total, 4) for c in all_cats if dis_cats.get(c, 0) > 0},
            'canonical_dist': {c: round(can_cats.get(c, 0) / can_total, 4) for c in all_cats if can_cats.get(c, 0) > 0},
        }

    # Also compare: does the pseudo-HEAD of displaced tokens predict
    # the same category as genuine headless with same first atom?
    pseudo_comparisons = {}
    for a in sorted(set(t['first_char'] for t in displaced)):
        dis_a = [t for t in displaced if t['first_char'] == a and t['category']]
        gen_a = [t for t in genuine if t['first_char'] == a and t['category']]

        if not dis_a or not gen_a:
            continue

        dis_cats = Counter(t['category'] for t in dis_a)
        gen_cats = Counter(t['category'] for t in gen_a)
        dis_total = sum(dis_cats.values())
        gen_total = sum(gen_cats.values())

        vec_d = np.array([dis_cats.get(c, 0) / dis_total for c in all_cats])
        vec_g = np.array([gen_cats.get(c, 0) / gen_total for c in all_cats])

        jsd = float(jensenshannon(vec_d, vec_g))

        pseudo_comparisons[a] = {
            'displaced_dominant': dis_cats.most_common(1)[0][0],
            'genuine_dominant': gen_cats.most_common(1)[0][0],
            'same_dominant': dis_cats.most_common(1)[0][0] == gen_cats.most_common(1)[0][0],
            'jsd': round(jsd, 4),
            'displaced_n': dis_total,
            'genuine_n': gen_total,
        }

    result = {
        'head_atom_comparisons': comparisons,
        'pseudo_head_comparisons': pseudo_comparisons,
        'summary': {
            'same_dominant_head_matches': sum(1 for v in comparisons.values() if v['same_dominant']),
            'total_head_comparisons': len(comparisons),
            'mean_jsd_head': round(np.mean([v['jsd'] for v in comparisons.values()]), 4) if comparisons else None,
            'same_dominant_pseudo_matches': sum(1 for v in pseudo_comparisons.values() if v['same_dominant']),
            'total_pseudo_comparisons': len(pseudo_comparisons),
            'mean_jsd_pseudo': round(np.mean([v['jsd'] for v in pseudo_comparisons.values()]), 4) if pseudo_comparisons else None,
        }
    }
    return result


# ═══════════════════════════════════════════════════════════════════════
# SYNTHESIS
# ═══════════════════════════════════════════════════════════════════════

def synthesis(results):
    """Synthesize findings into a verdict."""
    evidence_real_mode = []
    evidence_coincidence = []

    # 1. Category prediction (analysis k)
    k = results['k_alternative_mode']
    if k['verdict'] == 'PSEUDO_HEAD_DOMINATES':
        evidence_coincidence.append(
            f"Pseudo-HEAD predicts category {k['accuracy_ratio']:.2f}x better than displaced HEAD "
            f"({k['pseudo_head_accuracy']:.1%} vs {k['displaced_head_accuracy']:.1%})")
    elif k['verdict'] == 'DISPLACED_HEAD_DOMINATES':
        evidence_real_mode.append(
            f"Displaced HEAD predicts category better than pseudo-HEAD "
            f"({k['displaced_head_accuracy']:.1%} vs {k['pseudo_head_accuracy']:.1%})")
    else:
        evidence_coincidence.append(
            f"Neither predictor dominates (pseudo={k['pseudo_head_accuracy']:.1%}, "
            f"displaced={k['displaced_head_accuracy']:.1%})")

    # 2. Category profile divergence (analysis l)
    l_sum = results['l_displaced_vs_pseudo']['summary']
    if l_sum.get('mean_jsd_head') and l_sum.get('mean_jsd_pseudo'):
        if l_sum['mean_jsd_head'] > l_sum['mean_jsd_pseudo']:
            evidence_coincidence.append(
                f"Displaced tokens are MORE similar to same-pseudo-HEAD genuine tokens "
                f"(JSD={l_sum['mean_jsd_pseudo']:.4f}) than to same-HEAD canonical tokens "
                f"(JSD={l_sum['mean_jsd_head']:.4f})")
        else:
            evidence_real_mode.append(
                f"Displaced tokens are MORE similar to same-HEAD canonical tokens "
                f"(JSD={l_sum['mean_jsd_head']:.4f}) than to same-pseudo-HEAD genuine tokens "
                f"(JSD={l_sum['mean_jsd_pseudo']:.4f})")

    # 3. PREFIX alignment (analysis f)
    f = results['f_prefix']
    if f['displaced_patterns_with'] == 'GENUINE_HEADLESS':
        evidence_coincidence.append(
            f"PREFIX profile patterns with genuine headless "
            f"(JSD to genuine={f['jsd_displaced_vs_genuine_headless']}, "
            f"JSD to canonical={f['jsd_displaced_vs_canonical']})")
    else:
        evidence_real_mode.append(
            f"PREFIX profile patterns with canonical headed tokens")

    # 4. Same dominant category (analysis l)
    same_head = l_sum.get('same_dominant_head_matches', 0)
    total_head = l_sum.get('total_head_comparisons', 0)
    same_pseudo = l_sum.get('same_dominant_pseudo_matches', 0)
    total_pseudo = l_sum.get('total_pseudo_comparisons', 0)

    if total_head > 0 and total_pseudo > 0:
        head_rate = same_head / total_head
        pseudo_rate = same_pseudo / total_pseudo
        if pseudo_rate > head_rate:
            evidence_coincidence.append(
                f"Same dominant category: pseudo-HEAD {same_pseudo}/{total_pseudo} "
                f"({pseudo_rate:.0%}) vs HEAD {same_head}/{total_head} ({head_rate:.0%})")
        else:
            evidence_real_mode.append(
                f"Same dominant category: HEAD {same_head}/{total_head} "
                f"({head_rate:.0%}) vs pseudo-HEAD {same_pseudo}/{total_pseudo} ({pseudo_rate:.0%})")

    # 5. Population size - if very small, less likely to be a real mode
    census = results['a_census']
    dis_frac = census['displaced_fraction_of_headless_tokens']
    if dis_frac < 0.25:
        evidence_coincidence.append(
            f"Small population ({dis_frac:.1%} of headless tokens)")
    elif dis_frac > 0.40:
        evidence_real_mode.append(
            f"Substantial population ({dis_frac:.1%} of headless tokens)")

    # Verdict
    real_score = len(evidence_real_mode)
    coinc_score = len(evidence_coincidence)

    if coinc_score >= real_score + 2:
        verdict = "HEAD_SET_CHARACTER_NOT_FUNCTIONING_AS_HEAD"
        explanation = ("Displaced HEAD-set characters are NOT functioning as domain selectors. "
                       "The first atom (pseudo-HEAD) determines category. The HEAD-set character "
                       "in non-initial position carries a different functional role (modifier/terminal).")
    elif real_score >= coinc_score + 2:
        verdict = "GENUINE_ALTERNATIVE_COMPOSITIONAL_ORDER"
        explanation = ("Displaced HEADs represent a real alternative compositional order where "
                       "the HEAD atom moves behind a modifier/terminal prefix.")
    else:
        verdict = "MIXED_POPULATION"
        explanation = ("Some displaced HEAD characters may function as true HEADs, others as "
                       "non-HEAD uses of HEAD-set characters. Population is heterogeneous.")

    return {
        'verdict': verdict,
        'explanation': explanation,
        'evidence_real_mode': evidence_real_mode,
        'evidence_coincidence': evidence_coincidence,
        'scores': {'real_mode': real_score, 'coincidence': coinc_score},
    }


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("Phase 537: DISPLACED_HEAD_GRAMMAR")
    print("=" * 60)

    print("\nLoading data...")
    tokens = load_data()
    tokens = add_line_positions(tokens)

    canonical, displaced, genuine, all_headless = get_populations(tokens)
    print(f"  Total compound tokens: {len(tokens)}")
    print(f"  Canonical headed:      {len(canonical)} ({len(canonical)/len(tokens):.1%})")
    print(f"  All headless:          {len(all_headless)} ({len(all_headless)/len(tokens):.1%})")
    print(f"  - Displaced HEAD:      {len(displaced)} ({len(displaced)/len(all_headless):.1%} of headless)")
    print(f"  - Genuine headless:    {len(genuine)} ({len(genuine)/len(all_headless):.1%} of headless)")

    results = {}

    # (a) Census
    print("\n(a) Population census...")
    results['a_census'] = analysis_a_census(tokens, canonical, displaced, genuine, all_headless)
    print(f"  Displaced tokens: {results['a_census']['displaced_head_tokens']}")
    print(f"  Displaced types:  {results['a_census']['displaced_head_types']}")
    dh_atoms = results['a_census']['displaced_head_by_atom']
    for a, info in dh_atoms.items():
        print(f"    {a}: {info['count']} ({info['fraction']:.1%})")
    print(f"  Multi-displaced: {results['a_census']['multi_displaced_head_count']}")

    # (b) What precedes displaced HEAD
    print("\n(b) What precedes the displaced HEAD...")
    results['b_preceding'] = analysis_b_what_precedes(tokens, displaced)
    print(f"  Preceding class distribution:")
    for cl, info in results['b_preceding']['preceding_class_distribution'].items():
        print(f"    {cl}: {info['count']} ({info['fraction']:.1%})")

    # (c) Compositional patterns
    print("\n(c) Compositional patterns...")
    results['c_patterns'] = analysis_c_compositional_patterns(displaced)
    print(f"  Unique patterns: {results['c_patterns']['unique_patterns']}")
    for pat, info in list(results['c_patterns']['pattern_distribution'].items())[:8]:
        print(f"    {pat}: {info['count']} ({info['fraction']:.1%}) e.g. {info['examples']}")

    # (d) Which HEADs displaced
    print("\n(d) Which HEADs get displaced...")
    results['d_which_heads'] = analysis_d_which_heads_displaced(displaced, canonical)
    for h, info in results['d_which_heads']['enrichment_displaced_vs_canonical'].items():
        print(f"    {h}: displaced {info['displaced_fraction']:.1%} vs canonical {info['canonical_fraction']:.1%} "
              f"({info['enrichment']:.2f}x)")

    # (e) Category comparison
    print("\n(e) Category comparison...")
    results['e_category'] = analysis_e_category_comparison(tokens, canonical, displaced, genuine)
    print(f"  JSD displaced vs canonical:        {results['e_category']['jsd_displaced_vs_canonical']}")
    print(f"  JSD displaced vs genuine headless:  {results['e_category']['jsd_displaced_vs_genuine_headless']}")
    print(f"  JSD genuine vs canonical:           {results['e_category']['jsd_genuine_vs_canonical']}")
    print(f"  Per-HEAD JSD (displaced vs canonical same-HEAD):")
    for h, jsd in results['e_category']['jsd_same_head_displaced_vs_canonical'].items():
        print(f"    {h}: JSD={jsd}")

    # (f) PREFIX comparison
    print("\n(f) PREFIX comparison...")
    results['f_prefix'] = analysis_f_prefix_comparison(canonical, displaced, genuine)
    print(f"  JSD displaced vs canonical:     {results['f_prefix']['jsd_displaced_vs_canonical']}")
    print(f"  JSD displaced vs genuine HL:    {results['f_prefix']['jsd_displaced_vs_genuine_headless']}")
    print(f"  Displaced patterns with:        {results['f_prefix']['displaced_patterns_with']}")

    # (g) Line position
    print("\n(g) Line position...")
    results['g_position'] = analysis_g_line_position(canonical, displaced, genuine)
    print(f"  Canonical:  mean={results['g_position']['canonical_position']['mean_pos']}")
    print(f"  Displaced:  mean={results['g_position']['displaced_position']['mean_pos']}")
    print(f"  Genuine HL: mean={results['g_position']['genuine_headless_position']['mean_pos']}")

    # (h) Hazard
    print("\n(h) Hazard profile...")
    results['h_hazard'] = analysis_h_hazard_profile(canonical, displaced, genuine)
    print(f"  Canonical r-term:  {results['h_hazard']['canonical_hazard']['r_terminal_fraction']}")
    print(f"  Displaced r-term:  {results['h_hazard']['displaced_hazard']['r_terminal_fraction']}")
    print(f"  Genuine HL r-term: {results['h_hazard']['genuine_headless_hazard']['r_terminal_fraction']}")

    # (i) Suffix rate
    print("\n(i) Suffix rate...")
    results['i_suffix'] = analysis_i_suffix_rate(canonical, displaced, genuine)
    print(f"  Canonical:  {results['i_suffix']['canonical_suffix']['suffix_rate']}")
    print(f"  Displaced:  {results['i_suffix']['displaced_suffix']['suffix_rate']}")
    print(f"  Genuine HL: {results['i_suffix']['genuine_headless_suffix']['suffix_rate']}")

    # (j) Displacement predictors
    print("\n(j) Displacement predictors...")
    results['j_predictors'] = analysis_j_displacement_predictors(displaced, genuine, all_headless)
    print(f"  Length: displaced={results['j_predictors']['mean_length_displaced']}, "
          f"genuine={results['j_predictors']['mean_length_genuine']}")
    print(f"  Top pseudo-HEAD displacement rates:")
    for a, info in sorted(results['j_predictors']['displacement_rate_by_pseudo_head'].items(),
                          key=lambda x: -x[1]['rate'])[:5]:
        print(f"    {a}: {info['rate']:.1%} ({info['displaced']}/{info['total']})")

    # (k) Alternative mode test
    print("\n(k) Alternative compositional mode test...")
    results['k_alternative_mode'] = analysis_k_alternative_mode(displaced, genuine, canonical)
    print(f"  Pseudo-HEAD accuracy:   {results['k_alternative_mode']['pseudo_head_accuracy']:.1%}")
    print(f"  Displaced HEAD accuracy: {results['k_alternative_mode']['displaced_head_accuracy']:.1%}")
    print(f"  Ratio (pseudo/displaced): {results['k_alternative_mode']['accuracy_ratio']:.2f}")
    print(f"  Verdict: {results['k_alternative_mode']['verdict']}")

    # (l) Detailed displaced vs pseudo-HEAD
    print("\n(l) Displaced HEAD vs pseudo-HEAD category prediction...")
    results['l_displaced_vs_pseudo'] = analysis_l_displaced_vs_pseudo_category(displaced, canonical, genuine)
    summ = results['l_displaced_vs_pseudo']['summary']
    print(f"  Same dominant (HEAD comparison):   {summ['same_dominant_head_matches']}/{summ['total_head_comparisons']}")
    print(f"  Mean JSD (HEAD comparison):        {summ['mean_jsd_head']}")
    print(f"  Same dominant (pseudo comparison): {summ['same_dominant_pseudo_matches']}/{summ['total_pseudo_comparisons']}")
    print(f"  Mean JSD (pseudo comparison):      {summ['mean_jsd_pseudo']}")

    # Synthesis
    print("\n" + "=" * 60)
    print("SYNTHESIS")
    print("=" * 60)
    results['synthesis'] = synthesis(results)
    print(f"\nVerdict: {results['synthesis']['verdict']}")
    print(f"Explanation: {results['synthesis']['explanation']}")
    print(f"\nEvidence for real alternative mode ({results['synthesis']['scores']['real_mode']}):")
    for e in results['synthesis']['evidence_real_mode']:
        print(f"  + {e}")
    print(f"\nEvidence for coincidence ({results['synthesis']['scores']['coincidence']}):")
    for e in results['synthesis']['evidence_coincidence']:
        print(f"  - {e}")

    # Save results
    output_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'displaced_head_grammar.json')

    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
            return str(obj)
        return obj

    def deep_convert(obj):
        if isinstance(obj, dict):
            return {str(k): deep_convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [deep_convert(v) for v in obj]
        elif isinstance(obj, tuple):
            return [deep_convert(v) for v in obj]
        else:
            return convert(obj)

    results_clean = deep_convert(results)
    with open(output_path, 'w') as f:
        json.dump(results_clean, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")
    print("Phase 537 complete.")


if __name__ == '__main__':
    main()
