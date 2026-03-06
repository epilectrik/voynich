"""
Phase 536: HEADLESS_COMPOUND_SUBGRAMMAR
========================================
Deep investigation of headless compound MIDDLEs (20.6% of B tokens)
whose initial atom is NOT a HEAD atom {a,e,o,k,t}.

Core question: Is "headless" a coherent sixth operational domain,
or a heterogeneous grab-bag unified only by the absence of a HEAD?

Uses the HEAD/TERMINAL taxonomy framework from C1475-C1487 to analyze
headless compounds through the lens of frame hazard maps, terminal opacity,
modifier exclusivity channels, and direct comparison to the 5 HEAD domains.

Builds on Phase 509 (HEADLESS_COMPOUND_GRAMMAR, C1397) which established
the basic census and functional grammar. This phase goes deeper with
atom-level analysis.

12 analyses (a-l):
  a. Population census
  b. First-atom profile (pseudo-HEAD characterization)
  c. Terminal profile (vs C1487 taxonomy)
  d. Modifier profile (vs C1472 avoidance rules)
  e. Category profile (vs C1475 HEAD domains)
  f. Hazard profile (vs C1446-C1451 frame map)
  g. Line position profile
  h. PREFIX selectivity
  i. Suffix rate and opacity
  j. Internal structure patterns
  k. Comparison to 5 HEAD domains
  l. Length distribution
"""

import sys, os, json
import numpy as np
from collections import Counter, defaultdict
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier,
    decompose_middle_hmt,
)

# These match the constants inside decompose_middle_hmt (C1393-C1394)
HEAD_SET = {'a', 'e', 'o', 'k', 't'}
TERMINALS = {'y', 'l', 'r', 'h', 'm', 'n'}

# ── Constants ──────────────────────────────────────────────────────────
MODIFIER_SET = {'p', 'c', 'i', 'f', 'd', 's'}
EXTENSIBLE = {'e', 'i'}
# C1487 terminal taxonomy
LOCKED_TERMINALS = {'r', 'm'}
CHANNELED_TERMINALS = {'l', 'y', 'n'}
DIFFUSE_TERMINALS = {'h'}
# C1484 terminal-modifier exclusivity
TERM_MOD_CHANNELS = {
    'n': {'i'},       # n pairs ONLY with i
    'y': {'d'},       # y pairs ONLY with d
    'h': {'c', 'p', 'f', 's'},  # h takes {c,p,f,s}
}
# C1475 HEAD domain categories
HEAD_DOMAINS = {
    'k': 'THERMAL',
    't': 'FLOW',
    'a': 'hazard_carrier',
    'e': 'balanced',
    'o': 'arrangement',
}

def atomize(middle):
    """Split MIDDLE into atoms respecting e/i extensibility."""
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

def get_first_char(middle):
    """Get the first single character of a MIDDLE."""
    return middle[0] if middle else None

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

        tokens.append({
            'word': t.word,
            'folio': t.folio,
            'line': getattr(t, 'line', None),
            'line_in_folio': getattr(t, 'line_in_folio', None),
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'articulator': m.articulator,
            'head': head,
            'mods': mods,
            'term': term,
            'frame': frame,
            'category': cat,
            'first_char': get_first_char(m.middle),
            'atoms': atomize(m.middle),
            'is_headless': head is None,
        })

    return tokens

def load_line_positions(tokens):
    """Compute normalized line position for each token."""
    # Group tokens by folio+line
    line_groups = defaultdict(list)
    for i, t in enumerate(tokens):
        key = (t['folio'], t.get('line_in_folio', t.get('line', '')))
        line_groups[key].append(i)

    # Assign normalized position within line
    for key, indices in line_groups.items():
        n = len(indices)
        for rank, idx in enumerate(indices):
            tokens[idx]['line_pos'] = rank / max(n - 1, 1) if n > 1 else 0.5
            tokens[idx]['is_line_initial'] = (rank == 0)
            tokens[idx]['is_line_final'] = (rank == n - 1)
            tokens[idx]['line_length'] = n

    return tokens

def load_forbidden_pairs():
    """Load forbidden MIDDLE pairs from decoder_maps."""
    maps_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'decoder_maps.json')
    try:
        with open(maps_path) as f:
            data = json.load(f)
        # Try to get forbidden pairs
        if 'maps' in data and 'forbidden_pairs' in data['maps']:
            return data['maps']['forbidden_pairs']
    except:
        pass
    return None

def compute_hazard_from_frames(tokens):
    """
    Compute hazard profile using the HEAD x TERM frame approach from C1446-C1451.

    For headless tokens, the first atom takes the HEAD slot in frame analysis.
    We compare: does this first-atom x terminal combination appear in hazardous
    frames at the same rate as actual HEAD atoms?

    Key C1446-C1451 findings:
    - k-HEAD: 0% hazard (complete immunity)
    - r-terminal: 92.58% of forbidden violations
    - HIGH hazard frames: o->bare, d->y, a->l, a->r, o->r, e->e, a->n
    - Modifiers {c,d,f,p,s} quench hazard to 0%
    - Mode B carries 100% of forbidden violations
    """
    # We need to identify which tokens participate in forbidden transitions
    # Since we don't have the exact forbidden pair list, we use the structural
    # frame approach: categorize by (first_atom, terminal) and check for
    # hazard-associated patterns

    # Build frame counts for headed vs headless
    headed_frames = Counter()
    headless_frames = Counter()

    for t in tokens:
        if not t.get('term'):
            frame_key = (t['first_char'], 'bare')
        else:
            frame_key = (t['first_char'], t['term'][-1] if t['term'] else 'bare')

        if t['is_headless']:
            headless_frames[frame_key] += 1
        else:
            headed_frames[frame_key] += 1

    return headed_frames, headless_frames

# ═══════════════════════════════════════════════════════════════════════
# ANALYSES
# ═══════════════════════════════════════════════════════════════════════

def analysis_a_census(tokens):
    """(a) Population census of headless compounds."""
    headless = [t for t in tokens if t['is_headless']]
    headed = [t for t in tokens if not t['is_headless']]

    # Count by first atom
    first_atom_counts = Counter(t['first_char'] for t in headless)
    first_atom_types = defaultdict(set)
    for t in headless:
        first_atom_types[t['first_char']].add(t['middle'])

    # Classify first atoms
    first_atom_class = {}
    for atom in first_atom_counts:
        if atom in MODIFIER_SET:
            first_atom_class[atom] = 'MODIFIER'
        elif atom in TERMINALS:
            first_atom_class[atom] = 'TERMINAL'
        else:
            first_atom_class[atom] = 'OTHER'

    # Summary by class
    mod_tokens = sum(c for a, c in first_atom_counts.items() if first_atom_class.get(a) == 'MODIFIER')
    term_tokens = sum(c for a, c in first_atom_counts.items() if first_atom_class.get(a) == 'TERMINAL')
    other_tokens = sum(c for a, c in first_atom_counts.items() if first_atom_class.get(a) == 'OTHER')

    result = {
        'total_compound_tokens': len(tokens),
        'headless_tokens': len(headless),
        'headed_tokens': len(headed),
        'headless_fraction': round(len(headless) / len(tokens), 4),
        'headless_types': len(set(t['middle'] for t in headless)),
        'headed_types': len(set(t['middle'] for t in headed)),
        'first_atom_distribution': {
            atom: {
                'tokens': first_atom_counts[atom],
                'types': len(first_atom_types[atom]),
                'class': first_atom_class.get(atom, 'UNKNOWN'),
                'fraction': round(first_atom_counts[atom] / len(headless), 4),
            }
            for atom in sorted(first_atom_counts, key=first_atom_counts.get, reverse=True)
        },
        'by_initial_class': {
            'MODIFIER_tokens': mod_tokens,
            'MODIFIER_fraction': round(mod_tokens / len(headless), 4) if headless else 0,
            'TERMINAL_tokens': term_tokens,
            'TERMINAL_fraction': round(term_tokens / len(headless), 4) if headless else 0,
            'OTHER_tokens': other_tokens,
            'OTHER_fraction': round(other_tokens / len(headless), 4) if headless else 0,
        },
    }
    return result

def analysis_b_first_atom_profile(tokens):
    """(b) First-atom profile: characterize each pseudo-HEAD."""
    headless = [t for t in tokens if t['is_headless']]

    profiles = {}
    for atom in sorted(set(t['first_char'] for t in headless)):
        subset = [t for t in headless if t['first_char'] == atom]

        # Category distribution
        cats = Counter(t['category'] for t in subset if t['category'])
        total_cat = sum(cats.values())

        # Terminal distribution
        terms = Counter()
        for t in subset:
            if t['term']:
                last_char = t['term'][-1] if t['term'] else None
                if last_char:
                    terms[last_char] += 1
            else:
                terms['bare'] += 1
        total_term = sum(terms.values())

        # Suffix rate
        has_suffix = sum(1 for t in subset if t['suffix'])

        # Mean length
        lengths = [len(t['middle']) for t in subset]

        profiles[atom] = {
            'tokens': len(subset),
            'types': len(set(t['middle'] for t in subset)),
            'category_distribution': {
                k: {'count': v, 'fraction': round(v / total_cat, 4)}
                for k, v in sorted(cats.items(), key=lambda x: -x[1])
            } if total_cat > 0 else {},
            'dominant_category': cats.most_common(1)[0][0] if cats else None,
            'category_concentration': round(cats.most_common(1)[0][1] / total_cat, 4) if cats and total_cat > 0 else 0,
            'terminal_distribution': {
                k: {'count': v, 'fraction': round(v / total_term, 4)}
                for k, v in sorted(terms.items(), key=lambda x: -x[1])
            } if total_term > 0 else {},
            'suffix_rate': round(has_suffix / len(subset), 4),
            'mean_length': round(np.mean(lengths), 3),
            'atom_class': 'MODIFIER' if atom in MODIFIER_SET else ('TERMINAL' if atom in TERMINALS else 'OTHER'),
        }

    return profiles

def analysis_c_terminal_profile(tokens):
    """(c) Terminal profile vs C1487 LOCKED/CHANNELED/DIFFUSE taxonomy."""
    headless = [t for t in tokens if t['is_headless']]
    headed = [t for t in tokens if not t['is_headless']]

    def get_terminal_char(t):
        if t['term']:
            return t['term'][-1]
        return 'bare'

    def classify_terminal(tc):
        if tc in LOCKED_TERMINALS:
            return 'LOCKED'
        elif tc in CHANNELED_TERMINALS:
            return 'CHANNELED'
        elif tc in DIFFUSE_TERMINALS:
            return 'DIFFUSE'
        elif tc == 'bare':
            return 'bare'
        return 'OTHER'

    # Terminal distribution for headless vs headed
    hl_terms = Counter(get_terminal_char(t) for t in headless)
    hd_terms = Counter(get_terminal_char(t) for t in headed)
    hl_total = sum(hl_terms.values())
    hd_total = sum(hd_terms.values())

    # Taxonomy tier distribution
    hl_tiers = Counter(classify_terminal(get_terminal_char(t)) for t in headless)
    hd_tiers = Counter(classify_terminal(get_terminal_char(t)) for t in headed)

    # Per first-atom terminal profiles
    per_atom = {}
    for atom in sorted(set(t['first_char'] for t in headless)):
        subset = [t for t in headless if t['first_char'] == atom]
        terms = Counter(get_terminal_char(t) for t in subset)
        total = sum(terms.values())
        tiers = Counter(classify_terminal(k) for k in terms.elements())
        per_atom[atom] = {
            'terminals': {k: round(v / total, 4) for k, v in sorted(terms.items(), key=lambda x: -x[1])},
            'tiers': {k: round(v / total, 4) for k, v in sorted(tiers.items(), key=lambda x: -x[1])},
            'n': total,
        }

    # Enrichment ratios (headless vs headed)
    enrichments = {}
    for term in set(list(hl_terms.keys()) + list(hd_terms.keys())):
        hl_frac = hl_terms.get(term, 0) / hl_total if hl_total > 0 else 0
        hd_frac = hd_terms.get(term, 0) / hd_total if hd_total > 0 else 0
        enrichments[term] = round(hl_frac / hd_frac, 3) if hd_frac > 0 else float('inf')

    result = {
        'headless_terminal_distribution': {
            k: {'count': v, 'fraction': round(v / hl_total, 4)}
            for k, v in sorted(hl_terms.items(), key=lambda x: -x[1])
        },
        'headed_terminal_distribution': {
            k: {'count': v, 'fraction': round(v / hd_total, 4)}
            for k, v in sorted(hd_terms.items(), key=lambda x: -x[1])
        },
        'headless_tier_distribution': {
            k: round(v / hl_total, 4) for k, v in sorted(hl_tiers.items(), key=lambda x: -x[1])
        },
        'headed_tier_distribution': {
            k: round(v / hd_total, 4) for k, v in sorted(hd_tiers.items(), key=lambda x: -x[1])
        },
        'enrichment_vs_headed': enrichments,
        'per_first_atom': per_atom,
    }
    return result

def analysis_d_modifier_profile(tokens):
    """(d) Modifier profile vs C1472 avoidance and C1484 exclusivity."""
    headless = [t for t in tokens if t['is_headless']]
    headed = [t for t in tokens if not t['is_headless']]

    def get_modifier_set(t):
        """Get set of modifier atoms in a token's MIDDLE."""
        mods = set()
        atoms = t['atoms']
        for a in atoms:
            base = a[0]  # handle ee, ii etc
            if base in MODIFIER_SET:
                mods.add(base)
        return mods

    # Modifier co-occurrence in headless
    hl_mod_counts = Counter()
    hl_mod_pairs = Counter()
    for t in headless:
        mods = get_modifier_set(t)
        for m in mods:
            hl_mod_counts[m] += 1
        for m1 in mods:
            for m2 in mods:
                if m1 < m2:
                    hl_mod_pairs[(m1, m2)] += 1

    # Same for headed
    hd_mod_counts = Counter()
    hd_mod_pairs = Counter()
    for t in headed:
        mods = get_modifier_set(t)
        for m in mods:
            hd_mod_counts[m] += 1
        for m1 in mods:
            for m2 in mods:
                if m1 < m2:
                    hd_mod_pairs[(m1, m2)] += 1

    # Check C1484 terminal-modifier exclusivity compliance
    # n pairs ONLY with i, y pairs ONLY with d, h takes {c,p,f,s}
    exclusivity_violations = defaultdict(list)
    exclusivity_compliance = defaultdict(lambda: {'compliant': 0, 'total': 0})

    for t in headless:
        if not t['term']:
            continue
        term_char = t['term'][-1] if t['term'] else None
        if term_char not in TERM_MOD_CHANNELS:
            continue

        allowed_mods = TERM_MOD_CHANNELS[term_char]
        actual_mods = get_modifier_set(t)
        # Remove the first atom if it's a modifier (it's the pseudo-HEAD, not a true modifier)
        first = t['first_char']
        if first in MODIFIER_SET:
            actual_mods = actual_mods - {first}

        exclusivity_compliance[term_char]['total'] += 1

        # Check if any actual modifier violates the exclusivity
        violating = actual_mods - allowed_mods
        if violating:
            exclusivity_violations[term_char].append({
                'middle': t['middle'],
                'violating_mods': list(violating),
                'allowed': list(allowed_mods),
            })
        else:
            exclusivity_compliance[term_char]['compliant'] += 1

    # Modifier count distribution
    hl_mod_count_dist = Counter(len(get_modifier_set(t)) for t in headless)
    hd_mod_count_dist = Counter(len(get_modifier_set(t)) for t in headed)

    result = {
        'headless_modifier_frequency': {
            k: {'count': v, 'fraction': round(v / len(headless), 4)}
            for k, v in sorted(hl_mod_counts.items(), key=lambda x: -x[1])
        },
        'headed_modifier_frequency': {
            k: {'count': v, 'fraction': round(v / len(headed), 4)}
            for k, v in sorted(hd_mod_counts.items(), key=lambda x: -x[1])
        },
        'headless_modifier_pairs': {
            f"{k[0]}+{k[1]}": v for k, v in sorted(hl_mod_pairs.items(), key=lambda x: -x[1])
        },
        'headed_modifier_pairs': {
            f"{k[0]}+{k[1]}": v for k, v in sorted(hd_mod_pairs.items(), key=lambda x: -x[1])
        },
        'headless_mod_count_distribution': dict(sorted(hl_mod_count_dist.items())),
        'headed_mod_count_distribution': dict(sorted(hd_mod_count_dist.items())),
        'C1484_exclusivity_compliance': {
            term: {
                'total': data['total'],
                'compliant': data['compliant'],
                'rate': round(data['compliant'] / data['total'], 4) if data['total'] > 0 else None,
                'violations': len(exclusivity_violations.get(term, [])),
                'violation_examples': exclusivity_violations.get(term, [])[:5],
            }
            for term, data in exclusivity_compliance.items()
        },
    }
    return result

def analysis_e_category_profile(tokens):
    """(e) Category profile vs C1475 HEAD domain categories."""
    headless = [t for t in tokens if t['is_headless']]
    headed = [t for t in tokens if not t['is_headless']]

    # Overall category distributions
    hl_cats = Counter(t['category'] for t in headless if t['category'])
    hd_cats = Counter(t['category'] for t in headed if t['category'])
    hl_total = sum(hl_cats.values())
    hd_total = sum(hd_cats.values())

    # Category distribution by HEAD atom (for comparison)
    head_cat_profiles = {}
    for head_atom in sorted(HEAD_SET):
        subset = [t for t in headed if t['head'] and t['head'][0] == head_atom]
        cats = Counter(t['category'] for t in subset if t['category'])
        total = sum(cats.values())
        if total > 0:
            head_cat_profiles[head_atom] = {
                k: round(v / total, 4) for k, v in sorted(cats.items(), key=lambda x: -x[1])
            }

    # Category by first atom of headless
    pseudo_head_profiles = {}
    for atom in sorted(set(t['first_char'] for t in headless)):
        subset = [t for t in headless if t['first_char'] == atom]
        cats = Counter(t['category'] for t in subset if t['category'])
        total = sum(cats.values())
        if total > 0:
            pseudo_head_profiles[atom] = {
                'distribution': {k: round(v / total, 4) for k, v in sorted(cats.items(), key=lambda x: -x[1])},
                'dominant': cats.most_common(1)[0][0],
                'concentration': round(cats.most_common(1)[0][1] / total, 4),
                'n': total,
            }

    # Compute V (Cramer's V) for pseudo-HEAD -> category
    from scipy.stats import chi2_contingency
    all_cats = sorted(set(t['category'] for t in headless if t['category']))
    all_atoms = sorted(set(t['first_char'] for t in headless))

    contingency = np.zeros((len(all_atoms), len(all_cats)))
    for t in headless:
        if t['category'] and t['first_char'] in all_atoms:
            i = all_atoms.index(t['first_char'])
            j = all_cats.index(t['category'])
            contingency[i][j] += 1

    # Filter out rows/cols with zero totals
    row_mask = contingency.sum(axis=1) > 0
    col_mask = contingency.sum(axis=0) > 0
    contingency_filtered = contingency[row_mask][:, col_mask]

    if contingency_filtered.shape[0] > 1 and contingency_filtered.shape[1] > 1:
        chi2, p, dof, _ = chi2_contingency(contingency_filtered)
        n = contingency_filtered.sum()
        k = min(contingency_filtered.shape) - 1
        V = np.sqrt(chi2 / (n * k)) if k > 0 and n > 0 else 0
    else:
        chi2, p, V = 0, 1, 0

    # Enrichment: headless vs headed per category
    enrichments = {}
    for cat in all_cats:
        hl_frac = hl_cats.get(cat, 0) / hl_total if hl_total > 0 else 0
        hd_frac = hd_cats.get(cat, 0) / hd_total if hd_total > 0 else 0
        enrichments[cat] = round(hl_frac / hd_frac, 3) if hd_frac > 0 else float('inf')

    result = {
        'headless_category_distribution': {
            k: {'count': v, 'fraction': round(v / hl_total, 4)}
            for k, v in sorted(hl_cats.items(), key=lambda x: -x[1])
        },
        'headed_category_distribution': {
            k: {'count': v, 'fraction': round(v / hd_total, 4)}
            for k, v in sorted(hd_cats.items(), key=lambda x: -x[1])
        },
        'enrichment_vs_headed': enrichments,
        'pseudo_head_V': round(V, 4),
        'pseudo_head_chi2': round(chi2, 2),
        'pseudo_head_p': p,
        'pseudo_head_profiles': pseudo_head_profiles,
        'head_atom_profiles_for_comparison': head_cat_profiles,
    }
    return result

def analysis_f_hazard_profile(tokens):
    """(f) Hazard profile using frame-based analysis (C1446-C1451).

    Key framework:
    - HEAD x TERM defines a 'frame' that predicts hazard
    - k-HEAD: 0% hazard (C1476 intrinsic immunity)
    - r-terminal: 92.58% of forbidden violations (C1447)
    - Modifiers {c,d,f,p,s} quench hazard to 0% (C1450)
    - Mode B carries 100% of forbidden violations (C1451)

    For headless tokens, the first atom substitutes for HEAD in frame analysis.
    """
    headless = [t for t in tokens if t['is_headless']]
    headed = [t for t in tokens if not t['is_headless']]

    def get_frame(t):
        """Get (initial, terminal) frame tuple."""
        initial = t['first_char']
        if t['term']:
            terminal = t['term'][-1]
        else:
            terminal = 'bare'
        return (initial, terminal)

    def has_quenching_modifier(t):
        """Check if token has a quenching modifier {c,d,f,p,s} per C1450."""
        quenchers = {'c', 'd', 'f', 'p', 's'}
        for atom in t['atoms'][1:]:  # Skip first atom (pseudo-HEAD or HEAD)
            base = atom[0]
            if base in quenchers:
                return True
        return False

    # Frame distributions
    hl_frames = Counter(get_frame(t) for t in headless)
    hd_frames = Counter(get_frame(t) for t in headed)

    # Quenching modifier rates
    hl_quenched = sum(1 for t in headless if has_quenching_modifier(t))
    hd_quenched = sum(1 for t in headed if has_quenching_modifier(t))

    # r-terminal concentration (C1447: 92.58% of violations)
    hl_r_term = sum(1 for t in headless if t['term'] and t['term'][-1] == 'r')
    hd_r_term = sum(1 for t in headed if t['term'] and t['term'][-1] == 'r')

    # Per-first-atom hazard exposure profile
    # Using the known HIGH hazard frames from C1448:
    HIGH_HAZARD_FRAMES = {
        ('o', 'bare'), ('d', 'y'), ('a', 'l'), ('a', 'r'),
        ('o', 'r'), ('e', 'e'), ('a', 'n'),
    }
    IMMUNE_FRAMES_PREFIX = {'k'}  # k-HEAD = 0% hazard

    per_atom_hazard = {}
    for atom in sorted(set(t['first_char'] for t in headless)):
        subset = [t for t in headless if t['first_char'] == atom]
        frames = [get_frame(t) for t in subset]

        # Count frames matching known HIGH hazard patterns
        # For headless, the first atom is NOT a HEAD, so it won't match HEAD-based frames exactly
        # But we check if the (first_atom, terminal) pair WOULD be hazardous if it were a HEAD
        high_count = sum(1 for f in frames if f in HIGH_HAZARD_FRAMES)
        r_term_count = sum(1 for f in frames if f[1] == 'r')
        quench_count = sum(1 for t in subset if has_quenching_modifier(t))

        per_atom_hazard[atom] = {
            'tokens': len(subset),
            'high_frame_matches': high_count,
            'high_frame_fraction': round(high_count / len(subset), 4) if subset else 0,
            'r_terminal_count': r_term_count,
            'r_terminal_fraction': round(r_term_count / len(subset), 4) if subset else 0,
            'quenched_fraction': round(quench_count / len(subset), 4) if subset else 0,
        }

    # Comparison: does headless have more/fewer r-terminals than headed?
    hl_r_frac = hl_r_term / len(headless) if headless else 0
    hd_r_frac = hd_r_term / len(headed) if headed else 0

    result = {
        'headless_r_terminal_fraction': round(hl_r_frac, 4),
        'headed_r_terminal_fraction': round(hd_r_frac, 4),
        'r_terminal_enrichment': round(hl_r_frac / hd_r_frac, 3) if hd_r_frac > 0 else float('inf'),
        'headless_quenched_fraction': round(hl_quenched / len(headless), 4) if headless else 0,
        'headed_quenched_fraction': round(hd_quenched / len(headed), 4) if headed else 0,
        'per_first_atom_hazard': per_atom_hazard,
        'top_headless_frames': {
            f"{k[0]}->{k[1]}": v
            for k, v in sorted(hl_frames.items(), key=lambda x: -x[1])[:20]
        },
        'note': 'Headless tokens lack true HEAD atoms, so frame-hazard mapping is structural comparison, not direct hazard prediction',
    }
    return result

def analysis_g_line_position(tokens):
    """(g) Line position profile for headless tokens."""
    headless = [t for t in tokens if t['is_headless'] and 'line_pos' in t]
    headed = [t for t in tokens if not t['is_headless'] and 'line_pos' in t]

    if not headless or not headed:
        return {'error': 'No position data available'}

    # Overall position
    hl_pos = [t['line_pos'] for t in headless]
    hd_pos = [t['line_pos'] for t in headed]

    # Line-initial and line-final rates
    hl_initial = sum(1 for t in headless if t.get('is_line_initial'))
    hl_final = sum(1 for t in headless if t.get('is_line_final'))
    hd_initial = sum(1 for t in headed if t.get('is_line_initial'))
    hd_final = sum(1 for t in headed if t.get('is_line_final'))

    # Per first-atom position profiles
    per_atom = {}
    for atom in sorted(set(t['first_char'] for t in headless)):
        subset = [t for t in headless if t['first_char'] == atom]
        positions = [t['line_pos'] for t in subset]
        initial_rate = sum(1 for t in subset if t.get('is_line_initial')) / len(subset) if subset else 0
        final_rate = sum(1 for t in subset if t.get('is_line_final')) / len(subset) if subset else 0

        per_atom[atom] = {
            'mean_pos': round(np.mean(positions), 4),
            'std_pos': round(np.std(positions), 4),
            'initial_rate': round(initial_rate, 4),
            'final_rate': round(final_rate, 4),
            'n': len(subset),
        }

    # Quintile distribution
    hl_quintiles = Counter()
    hd_quintiles = Counter()
    for t in headless:
        q = min(int(t['line_pos'] * 5), 4)
        hl_quintiles[q] += 1
    for t in headed:
        q = min(int(t['line_pos'] * 5), 4)
        hd_quintiles[q] += 1

    hl_q_total = sum(hl_quintiles.values())
    hd_q_total = sum(hd_quintiles.values())

    # Mann-Whitney U test
    stat, p = stats.mannwhitneyu(hl_pos, hd_pos, alternative='two-sided')

    result = {
        'headless_mean_pos': round(np.mean(hl_pos), 4),
        'headed_mean_pos': round(np.mean(hd_pos), 4),
        'headless_initial_rate': round(hl_initial / len(headless), 4),
        'headed_initial_rate': round(hd_initial / len(headed), 4),
        'headless_final_rate': round(hl_final / len(headless), 4),
        'headed_final_rate': round(hd_final / len(headed), 4),
        'mann_whitney_p': p,
        'quintile_enrichment': {
            f"Q{q}": round((hl_quintiles.get(q, 0) / hl_q_total) / (hd_quintiles.get(q, 0) / hd_q_total), 3)
            if hd_quintiles.get(q, 0) > 0 else float('inf')
            for q in range(5)
        },
        'per_first_atom': per_atom,
    }
    return result

def analysis_h_prefix_selectivity(tokens):
    """(h) PREFIX selectivity for headless tokens."""
    headless = [t for t in tokens if t['is_headless']]
    headed = [t for t in tokens if not t['is_headless']]

    # PREFIX distribution
    hl_pfx = Counter(t['prefix'] or 'BARE' for t in headless)
    hd_pfx = Counter(t['prefix'] or 'BARE' for t in headed)
    hl_total = sum(hl_pfx.values())
    hd_total = sum(hd_pfx.values())

    # Per first-atom PREFIX profiles
    per_atom_pfx = {}
    for atom in sorted(set(t['first_char'] for t in headless)):
        subset = [t for t in headless if t['first_char'] == atom]
        pfx = Counter(t['prefix'] or 'BARE' for t in subset)
        total = sum(pfx.values())
        per_atom_pfx[atom] = {
            k: round(v / total, 4) for k, v in sorted(pfx.items(), key=lambda x: -x[1])
        }

    # PREFIX enrichment
    enrichments = {}
    for pfx in set(list(hl_pfx.keys()) + list(hd_pfx.keys())):
        hl_frac = hl_pfx.get(pfx, 0) / hl_total if hl_total > 0 else 0
        hd_frac = hd_pfx.get(pfx, 0) / hd_total if hd_total > 0 else 0
        enrichments[pfx] = round(hl_frac / hd_frac, 3) if hd_frac > 0 else float('inf')

    # BARE rate comparison
    hl_bare = hl_pfx.get('BARE', 0) / hl_total if hl_total > 0 else 0
    hd_bare = hd_pfx.get('BARE', 0) / hd_total if hd_total > 0 else 0

    # Check C1415: 83 forbidden PREFIX x MIDDLE HEAD combinations
    # For headless, there IS no HEAD. Check if headless tokens avoid
    # certain PREFIXes that headed tokens freely use
    hl_pfx_set = set(hl_pfx.keys())
    hd_pfx_set = set(hd_pfx.keys())

    result = {
        'headless_prefix_distribution': {
            k: {'count': v, 'fraction': round(v / hl_total, 4)}
            for k, v in sorted(hl_pfx.items(), key=lambda x: -x[1])[:15]
        },
        'headed_prefix_distribution': {
            k: {'count': v, 'fraction': round(v / hd_total, 4)}
            for k, v in sorted(hd_pfx.items(), key=lambda x: -x[1])[:15]
        },
        'enrichment': {k: v for k, v in sorted(enrichments.items(), key=lambda x: -x[1])[:15]},
        'headless_bare_rate': round(hl_bare, 4),
        'headed_bare_rate': round(hd_bare, 4),
        'bare_enrichment': round(hl_bare / hd_bare, 3) if hd_bare > 0 else float('inf'),
        'per_first_atom_prefix': per_atom_pfx,
        'headless_only_prefixes': sorted(hl_pfx_set - hd_pfx_set),
        'headed_only_prefixes': sorted(hd_pfx_set - hl_pfx_set),
    }
    return result

def analysis_i_suffix_opacity(tokens):
    """(i) Suffix rate and opacity analysis (C1440-C1445)."""
    headless = [t for t in tokens if t['is_headless']]
    headed = [t for t in tokens if not t['is_headless']]

    def get_terminal_char(t):
        if t['term']:
            return t['term'][-1]
        return 'bare'

    # Overall suffix rates
    hl_suffix = sum(1 for t in headless if t['suffix'])
    hd_suffix = sum(1 for t in headed if t['suffix'])

    # Suffix rate by terminal (opacity check)
    hl_term_suffix = defaultdict(lambda: {'with': 0, 'without': 0})
    hd_term_suffix = defaultdict(lambda: {'with': 0, 'without': 0})

    for t in headless:
        tc = get_terminal_char(t)
        if t['suffix']:
            hl_term_suffix[tc]['with'] += 1
        else:
            hl_term_suffix[tc]['without'] += 1

    for t in headed:
        tc = get_terminal_char(t)
        if t['suffix']:
            hd_term_suffix[tc]['with'] += 1
        else:
            hd_term_suffix[tc]['without'] += 1

    # Compute suffix rates by terminal
    hl_opacity = {}
    hd_opacity = {}
    for tc in set(list(hl_term_suffix.keys()) + list(hd_term_suffix.keys())):
        hl_data = hl_term_suffix.get(tc, {'with': 0, 'without': 0})
        hl_total = hl_data['with'] + hl_data['without']
        hl_opacity[tc] = {
            'suffix_rate': round(hl_data['with'] / hl_total, 4) if hl_total > 0 else None,
            'n': hl_total,
        }

        hd_data = hd_term_suffix.get(tc, {'with': 0, 'without': 0})
        hd_total = hd_data['with'] + hd_data['without']
        hd_opacity[tc] = {
            'suffix_rate': round(hd_data['with'] / hd_total, 4) if hd_total > 0 else None,
            'n': hd_total,
        }

    # Per first-atom suffix rate
    per_atom = {}
    for atom in sorted(set(t['first_char'] for t in headless)):
        subset = [t for t in headless if t['first_char'] == atom]
        rate = sum(1 for t in subset if t['suffix']) / len(subset)
        per_atom[atom] = round(rate, 4)

    # Check C1440 three-tier opacity compliance
    # OPAQUE (m,n,y: <5% suffix), SEMI (l,r: 17-20%), TRANSPARENT (h: >98%)
    opacity_compliance = {}
    for tc, expected in [('m', '<5%'), ('n', '<5%'), ('y', '<5%'),
                         ('l', '17-20%'), ('r', '17-20%'), ('h', '>98%')]:
        hl_rate = hl_opacity.get(tc, {}).get('suffix_rate')
        hd_rate = hd_opacity.get(tc, {}).get('suffix_rate')
        opacity_compliance[tc] = {
            'expected': expected,
            'headless_rate': hl_rate,
            'headed_rate': hd_rate,
            'headless_n': hl_opacity.get(tc, {}).get('n', 0),
            'headed_n': hd_opacity.get(tc, {}).get('n', 0),
        }

    result = {
        'headless_overall_suffix_rate': round(hl_suffix / len(headless), 4) if headless else 0,
        'headed_overall_suffix_rate': round(hd_suffix / len(headed), 4) if headed else 0,
        'headless_opacity_by_terminal': hl_opacity,
        'headed_opacity_by_terminal': hd_opacity,
        'C1440_opacity_compliance': opacity_compliance,
        'per_first_atom_suffix_rate': per_atom,
    }
    return result

def analysis_j_internal_structure(tokens):
    """(j) Internal structure patterns of headless compounds."""
    headless = [t for t in tokens if t['is_headless']]

    # Classify internal structure pattern
    # For headless, pattern is like: MOD + (MOD*) + TERM, or TERM + MOD + ..., etc.
    patterns = Counter()
    slot_sequences = Counter()

    for t in headless:
        atoms = t['atoms']
        if len(atoms) < 2:
            continue

        # Classify each atom by its canonical slot
        slots = []
        for a in atoms:
            base = a[0]
            if base in HEAD_SET:
                slots.append('H')
            elif base in MODIFIER_SET:
                slots.append('M')
            elif base in TERMINALS:
                slots.append('T')
            else:
                slots.append('?')

        pattern = ''.join(slots)
        patterns[pattern] += 1
        slot_sequences[tuple(slots)] += 1

    # Analyze: do headless tokens have internal HEADs?
    # i.e., is there a HEAD atom in a non-initial position?
    internal_head_count = 0
    internal_head_examples = []
    for t in headless:
        atoms = t['atoms']
        for a in atoms[1:]:
            base = a[0]
            if base in HEAD_SET:
                internal_head_count += 1
                if len(internal_head_examples) < 10:
                    internal_head_examples.append({
                        'middle': t['middle'],
                        'atoms': [str(x) for x in atoms],
                        'internal_head': a,
                    })
                break

    # Count MIDDLEs with dual modifier, dual terminal, etc.
    dual_mod = sum(1 for t in headless if sum(1 for a in t['atoms'] if a[0] in MODIFIER_SET) >= 2)
    dual_term = sum(1 for t in headless if sum(1 for a in t['atoms'] if a[0] in TERMINALS) >= 2)

    # Most common patterns
    top_patterns = patterns.most_common(20)

    result = {
        'pattern_distribution': {p: c for p, c in top_patterns},
        'total_patterns': len(patterns),
        'internal_head_count': internal_head_count,
        'internal_head_fraction': round(internal_head_count / len(headless), 4) if headless else 0,
        'internal_head_examples': internal_head_examples,
        'dual_modifier_count': dual_mod,
        'dual_modifier_fraction': round(dual_mod / len(headless), 4) if headless else 0,
        'dual_terminal_count': dual_term,
        'dual_terminal_fraction': round(dual_term / len(headless), 4) if headless else 0,
        'note': 'Pattern codes: H=HEAD atom, M=MODIFIER atom, T=TERMINAL atom',
    }
    return result

def analysis_k_comparison_to_heads(tokens):
    """(k) Systematic comparison of headless to each of the 5 HEAD domains."""
    headless = [t for t in tokens if t['is_headless']]

    # Build profiles for each HEAD domain
    head_profiles = {}
    for head_atom in sorted(HEAD_SET):
        subset = [t for t in tokens if not t['is_headless'] and t['head'] and t['head'][0] == head_atom]
        if not subset:
            continue

        cats = Counter(t['category'] for t in subset if t['category'])
        total_cat = sum(cats.values())

        terms = Counter()
        for t in subset:
            if t['term']:
                terms[t['term'][-1]] += 1
            else:
                terms['bare'] += 1
        total_term = sum(terms.values())

        pfx = Counter(t['prefix'] or 'BARE' for t in subset)
        total_pfx = sum(pfx.values())

        suffix_rate = sum(1 for t in subset if t['suffix']) / len(subset)

        positions = [t['line_pos'] for t in subset if 'line_pos' in t]

        head_profiles[head_atom] = {
            'tokens': len(subset),
            'category': {k: round(v / total_cat, 4) for k, v in cats.items()} if total_cat > 0 else {},
            'terminal': {k: round(v / total_term, 4) for k, v in terms.items()} if total_term > 0 else {},
            'prefix_top5': {k: round(v / total_pfx, 4) for k, v in sorted(pfx.items(), key=lambda x: -x[1])[:5]} if total_pfx > 0 else {},
            'suffix_rate': round(suffix_rate, 4),
            'mean_pos': round(np.mean(positions), 4) if positions else None,
            'mean_length': round(np.mean([len(t['middle']) for t in subset]), 3),
        }

    # Build headless profile (aggregated)
    hl_cats = Counter(t['category'] for t in headless if t['category'])
    hl_total_cat = sum(hl_cats.values())
    hl_terms = Counter()
    for t in headless:
        if t['term']:
            hl_terms[t['term'][-1]] += 1
        else:
            hl_terms['bare'] += 1
    hl_total_term = sum(hl_terms.values())
    hl_pfx = Counter(t['prefix'] or 'BARE' for t in headless)
    hl_total_pfx = sum(hl_pfx.values())
    hl_suffix_rate = sum(1 for t in headless if t['suffix']) / len(headless) if headless else 0
    hl_positions = [t['line_pos'] for t in headless if 'line_pos' in t]

    headless_profile = {
        'tokens': len(headless),
        'category': {k: round(v / hl_total_cat, 4) for k, v in hl_cats.items()} if hl_total_cat > 0 else {},
        'terminal': {k: round(v / hl_total_term, 4) for k, v in hl_terms.items()} if hl_total_term > 0 else {},
        'prefix_top5': {k: round(v / hl_total_pfx, 4) for k, v in sorted(hl_pfx.items(), key=lambda x: -x[1])[:5]} if hl_total_pfx > 0 else {},
        'suffix_rate': round(hl_suffix_rate, 4),
        'mean_pos': round(np.mean(hl_positions), 4) if hl_positions else None,
        'mean_length': round(np.mean([len(t['middle']) for t in headless]), 3),
    }

    # Compute JSD between headless and each HEAD domain on category
    from scipy.spatial.distance import jensenshannon
    all_cats = sorted(set(t['category'] for t in tokens if t['category']))

    hl_cat_vec = np.array([hl_cats.get(c, 0) for c in all_cats], dtype=float)
    hl_cat_vec /= hl_cat_vec.sum() if hl_cat_vec.sum() > 0 else 1

    jsd_scores = {}
    for head_atom, profile in head_profiles.items():
        hd_cat_vec = np.array([profile['category'].get(c, 0) for c in all_cats], dtype=float)
        hd_cat_vec_sum = hd_cat_vec.sum()
        if hd_cat_vec_sum > 0:
            hd_cat_vec /= hd_cat_vec_sum
        jsd = jensenshannon(hl_cat_vec, hd_cat_vec)
        jsd_scores[head_atom] = round(jsd, 4)

    # Also per-pseudo-head JSD to each HEAD domain
    per_pseudo_jsd = {}
    for atom in sorted(set(t['first_char'] for t in headless)):
        subset = [t for t in headless if t['first_char'] == atom]
        cats = Counter(t['category'] for t in subset if t['category'])
        total = sum(cats.values())
        if total == 0:
            continue
        vec = np.array([cats.get(c, 0) for c in all_cats], dtype=float)
        vec /= vec.sum()

        per_pseudo_jsd[atom] = {}
        for head_atom, profile in head_profiles.items():
            hd_vec = np.array([profile['category'].get(c, 0) for c in all_cats], dtype=float)
            hd_sum = hd_vec.sum()
            if hd_sum > 0:
                hd_vec /= hd_sum
            per_pseudo_jsd[atom][head_atom] = round(jensenshannon(vec, hd_vec), 4)

    result = {
        'head_domain_profiles': head_profiles,
        'headless_aggregate_profile': headless_profile,
        'category_jsd_headless_vs_head': jsd_scores,
        'nearest_head_domain': min(jsd_scores, key=jsd_scores.get) if jsd_scores else None,
        'farthest_head_domain': max(jsd_scores, key=jsd_scores.get) if jsd_scores else None,
        'per_pseudo_head_jsd': per_pseudo_jsd,
    }
    return result

def analysis_l_length_distribution(tokens):
    """(l) Length distribution of headless vs headed compounds."""
    headless = [t for t in tokens if t['is_headless']]
    headed = [t for t in tokens if not t['is_headless']]

    hl_lengths = [len(t['middle']) for t in headless]
    hd_lengths = [len(t['middle']) for t in headed]

    # Per first-atom length distributions
    per_atom = {}
    for atom in sorted(set(t['first_char'] for t in headless)):
        subset = [len(t['middle']) for t in headless if t['first_char'] == atom]
        per_atom[atom] = {
            'mean': round(np.mean(subset), 3),
            'std': round(np.std(subset), 3),
            'min': min(subset),
            'max': max(subset),
            'n': len(subset),
            'distribution': dict(Counter(subset)),
        }

    # Length vs number of atoms
    hl_atom_counts = Counter(len(t['atoms']) for t in headless)
    hd_atom_counts = Counter(len(t['atoms']) for t in headed)

    # KS test
    ks_stat, ks_p = stats.ks_2samp(hl_lengths, hd_lengths)

    result = {
        'headless_mean_length': round(np.mean(hl_lengths), 3),
        'headed_mean_length': round(np.mean(hd_lengths), 3),
        'headless_std': round(np.std(hl_lengths), 3),
        'headed_std': round(np.std(hd_lengths), 3),
        'headless_length_dist': dict(Counter(hl_lengths)),
        'headed_length_dist': dict(Counter(hd_lengths)),
        'ks_stat': round(ks_stat, 4),
        'ks_p': ks_p,
        'headless_atom_count_dist': dict(sorted(hl_atom_counts.items())),
        'headed_atom_count_dist': dict(sorted(hd_atom_counts.items())),
        'per_first_atom': per_atom,
    }
    return result

# ═══════════════════════════════════════════════════════════════════════
# SYNTHESIS: Is headless a coherent sixth domain?
# ═══════════════════════════════════════════════════════════════════════

def synthesis(results):
    """Synthesize all analyses into a verdict."""

    # Evidence for coherent domain
    coherent_evidence = []
    # Evidence against (grab-bag)
    grabbag_evidence = []

    # 1. Category differentiation (from analysis_e)
    V = results['e_category']['pseudo_head_V']
    if V >= 0.3:
        coherent_evidence.append(f"Strong pseudo-HEAD category differentiation (V={V})")
    elif V >= 0.15:
        coherent_evidence.append(f"Moderate pseudo-HEAD category differentiation (V={V})")
    else:
        grabbag_evidence.append(f"Weak pseudo-HEAD category differentiation (V={V})")

    # 2. Do pseudo-HEADs match existing HEAD domains? (from analysis_k)
    jsd_scores = results['k_comparison']['category_jsd_headless_vs_head']
    nearest = results['k_comparison'].get('nearest_head_domain')
    nearest_jsd = jsd_scores.get(nearest, 1.0) if nearest else 1.0

    if nearest_jsd > 0.3:
        coherent_evidence.append(f"Headless aggregate is distant from all HEAD domains (nearest JSD={nearest_jsd})")
    else:
        grabbag_evidence.append(f"Headless aggregate overlaps with {nearest}-HEAD domain (JSD={nearest_jsd})")

    # 3. Internal heterogeneity (from per-pseudo-head profiles)
    # b_first_atom is already keyed by atom name directly
    pseudo_profiles = results.get('b_first_atom', {})

    # 4. Terminal opacity compliance (from analysis_i)
    opacity = results['i_suffix_opacity'].get('C1440_opacity_compliance', {})
    compliant = 0
    total_tested = 0
    for tc, data in opacity.items():
        if data.get('headless_rate') is not None and data.get('headless_n', 0) >= 10:
            total_tested += 1
            # Check if headless rate is in expected range
            expected = data['expected']
            rate = data['headless_rate']
            if expected == '<5%' and rate < 0.05:
                compliant += 1
            elif expected == '17-20%' and 0.10 <= rate <= 0.30:
                compliant += 1  # generous range
            elif expected == '>98%' and rate > 0.90:
                compliant += 1

    if total_tested > 0:
        compliance_rate = compliant / total_tested
        if compliance_rate >= 0.8:
            coherent_evidence.append(f"Terminal opacity follows same rules as headed ({compliant}/{total_tested} compliant)")
        else:
            grabbag_evidence.append(f"Terminal opacity deviates from headed ({compliant}/{total_tested} compliant)")

    # 5. Internal structure patterns (from analysis_j)
    internal_head_frac = results['j_internal_structure'].get('internal_head_fraction', 0)
    if internal_head_frac > 0.5:
        grabbag_evidence.append(f"Majority have internal HEAD atoms ({internal_head_frac:.1%}) - many are displaced-HEAD, not truly headless")
    elif internal_head_frac > 0.2:
        coherent_evidence.append(f"Some internal HEAD atoms ({internal_head_frac:.1%}) - mixed population")
    else:
        coherent_evidence.append(f"Few internal HEAD atoms ({internal_head_frac:.1%}) - genuinely headless")

    # 6. BARE rate difference (from analysis_h)
    bare_enrichment = results['h_prefix'].get('bare_enrichment', 1.0)
    if bare_enrichment > 1.5:
        coherent_evidence.append(f"Strong BARE enrichment ({bare_enrichment:.2f}x) - headless tokens resist PREFIX attachment")
    elif bare_enrichment > 1.2:
        coherent_evidence.append(f"Moderate BARE enrichment ({bare_enrichment:.2f}x)")

    # Verdict
    coherent_score = len(coherent_evidence)
    grabbag_score = len(grabbag_evidence)

    if coherent_score >= grabbag_score + 2:
        verdict = "HEADLESS_IS_COHERENT_DOMAIN"
        explanation = "Headless compounds form a structurally coherent group with distinctive properties"
    elif grabbag_score >= coherent_score + 2:
        verdict = "HEADLESS_IS_GRAB_BAG"
        explanation = "Headless compounds are heterogeneous, unified only by HEAD absence"
    else:
        verdict = "HEADLESS_IS_STRATIFIED"
        explanation = "Headless compounds are internally stratified: some pseudo-HEADs define domains, others are marginal"

    return {
        'verdict': verdict,
        'explanation': explanation,
        'coherent_evidence': coherent_evidence,
        'grabbag_evidence': grabbag_evidence,
        'scores': {
            'coherent': coherent_score,
            'grabbag': grabbag_score,
        },
    }

# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("Phase 536: HEADLESS_COMPOUND_SUBGRAMMAR")
    print("=" * 60)

    print("\nLoading data...")
    tokens = load_data()
    tokens = load_line_positions(tokens)

    total_compound = len(tokens)
    headless = sum(1 for t in tokens if t['is_headless'])
    print(f"  Compound tokens: {total_compound}")
    print(f"  Headless: {headless} ({headless/total_compound:.1%})")
    print(f"  Headed: {total_compound - headless} ({(total_compound-headless)/total_compound:.1%})")

    results = {}

    # (a) Population census
    print("\n(a) Population census...")
    results['a_census'] = analysis_a_census(tokens)
    print(f"  Headless: {results['a_census']['headless_tokens']} tokens, "
          f"{results['a_census']['headless_types']} types")
    print(f"  By class: MOD={results['a_census']['by_initial_class']['MODIFIER_fraction']:.1%}, "
          f"TERM={results['a_census']['by_initial_class']['TERMINAL_fraction']:.1%}")

    # (b) First-atom profile
    print("\n(b) First-atom pseudo-HEAD profiles...")
    results['b_first_atom'] = analysis_b_first_atom_profile(tokens)
    for atom, prof in results['b_first_atom'].items():
        if isinstance(prof, dict) and 'dominant_category' in prof:
            print(f"  {atom}: {prof['tokens']} tokens, dominant={prof['dominant_category']} "
                  f"({prof['category_concentration']:.1%})")

    # (c) Terminal profile
    print("\n(c) Terminal profile vs C1487 taxonomy...")
    results['c_terminal'] = analysis_c_terminal_profile(tokens)
    print(f"  Headless tier dist: {results['c_terminal']['headless_tier_distribution']}")
    print(f"  Headed tier dist:   {results['c_terminal']['headed_tier_distribution']}")

    # (d) Modifier profile
    print("\n(d) Modifier profile vs C1472/C1484...")
    results['d_modifier'] = analysis_d_modifier_profile(tokens)
    compliance = results['d_modifier']['C1484_exclusivity_compliance']
    for term, data in compliance.items():
        if data['total'] > 0:
            print(f"  C1484 {term}-terminal: {data['rate']:.1%} compliant ({data['total']} tokens, {data['violations']} violations)")

    # (e) Category profile
    print("\n(e) Category profile vs C1475 HEAD domains...")
    results['e_category'] = analysis_e_category_profile(tokens)
    print(f"  Pseudo-HEAD -> Category V={results['e_category']['pseudo_head_V']}")
    print(f"  Category enrichment vs headed: {results['e_category']['enrichment_vs_headed']}")

    # (f) Hazard profile
    print("\n(f) Hazard profile (C1446-C1451 frame analysis)...")
    results['f_hazard'] = analysis_f_hazard_profile(tokens)
    print(f"  Headless r-terminal: {results['f_hazard']['headless_r_terminal_fraction']:.4f}")
    print(f"  Headed r-terminal:   {results['f_hazard']['headed_r_terminal_fraction']:.4f}")
    print(f"  Enrichment: {results['f_hazard']['r_terminal_enrichment']:.3f}x")

    # (g) Line position
    print("\n(g) Line position profile...")
    results['g_position'] = analysis_g_line_position(tokens)
    print(f"  Headless mean pos: {results['g_position']['headless_mean_pos']}")
    print(f"  Headed mean pos:   {results['g_position']['headed_mean_pos']}")
    print(f"  Headless initial rate: {results['g_position']['headless_initial_rate']}")
    print(f"  Headless final rate:   {results['g_position']['headless_final_rate']}")

    # (h) PREFIX selectivity
    print("\n(h) PREFIX selectivity...")
    results['h_prefix'] = analysis_h_prefix_selectivity(tokens)
    print(f"  BARE rate: headless={results['h_prefix']['headless_bare_rate']:.4f}, "
          f"headed={results['h_prefix']['headed_bare_rate']:.4f}, "
          f"enrichment={results['h_prefix']['bare_enrichment']:.3f}x")

    # (i) Suffix rate and opacity
    print("\n(i) Suffix rate and opacity...")
    results['i_suffix_opacity'] = analysis_i_suffix_opacity(tokens)
    print(f"  Headless suffix rate: {results['i_suffix_opacity']['headless_overall_suffix_rate']}")
    print(f"  Headed suffix rate:   {results['i_suffix_opacity']['headed_overall_suffix_rate']}")

    # (j) Internal structure
    print("\n(j) Internal structure patterns...")
    results['j_internal_structure'] = analysis_j_internal_structure(tokens)
    top = list(results['j_internal_structure']['pattern_distribution'].items())[:5]
    for pat, count in top:
        print(f"  Pattern {pat}: {count}")
    print(f"  Internal HEAD atoms: {results['j_internal_structure']['internal_head_fraction']:.1%}")

    # (k) Comparison to HEAD domains
    print("\n(k) Comparison to 5 HEAD domains...")
    results['k_comparison'] = analysis_k_comparison_to_heads(tokens)
    print(f"  Category JSD headless vs HEAD domains:")
    for head, jsd in results['k_comparison']['category_jsd_headless_vs_head'].items():
        print(f"    {head}: JSD={jsd}")
    print(f"  Nearest: {results['k_comparison']['nearest_head_domain']}")
    print(f"  Farthest: {results['k_comparison']['farthest_head_domain']}")

    # (l) Length distribution
    print("\n(l) Length distribution...")
    results['l_length'] = analysis_l_length_distribution(tokens)
    print(f"  Headless mean length: {results['l_length']['headless_mean_length']}")
    print(f"  Headed mean length:   {results['l_length']['headed_mean_length']}")
    print(f"  KS test p={results['l_length']['ks_p']:.2e}")

    # Synthesis
    print("\n" + "=" * 60)
    print("SYNTHESIS")
    print("=" * 60)
    results['synthesis'] = synthesis(results)
    print(f"\nVerdict: {results['synthesis']['verdict']}")
    print(f"Explanation: {results['synthesis']['explanation']}")
    print(f"\nCoherent evidence ({results['synthesis']['scores']['coherent']}):")
    for e in results['synthesis']['coherent_evidence']:
        print(f"  + {e}")
    print(f"\nGrab-bag evidence ({results['synthesis']['scores']['grabbag']}):")
    for e in results['synthesis']['grabbag_evidence']:
        print(f"  - {e}")

    # Save results
    output_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'headless_compound_subgrammar.json')

    # Convert numpy types for JSON serialization
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
    print("Phase 536 complete.")

if __name__ == '__main__':
    main()
