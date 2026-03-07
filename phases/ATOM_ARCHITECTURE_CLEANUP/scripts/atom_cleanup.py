#!/usr/bin/env python3
"""
Phase 549: Atom Architecture Cleanup

Closes remaining empirical gaps in atom-level characterization with four sub-analyses:

  Q1: Articulator (y-) Characterization
  Q2: Sequential Atom Couplings (cross-token HEAD/TERM handoffs)
  Q3: Paragraph Atom Signatures (header vs body, convergence)
  Q4: Line-Position Atom Gradient (quintile-resolved HEAD/MOD/TERM)

Output: phases/ATOM_ARCHITECTURE_CLEANUP/results/atom_cleanup.json
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier, decompose_middle_hmt
)

# ============================================================================
# CONSTANTS
# ============================================================================
HEAD_ATOMS = set('aeokt')
MOD_ATOMS = set('picfds')
TERM_ATOMS = set('ylrhmn')
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
FORBIDDEN_SET = set(FORBIDDEN_PAIRS)


# ============================================================================
# HELPERS
# ============================================================================
def get_head(middle):
    if not middle or middle == '_EMPTY_':
        return None
    return middle[0] if middle[0] in HEAD_ATOMS else 'HEADLESS'


def get_terminal(middle):
    if not middle or middle == '_EMPTY_':
        return None
    if middle[-1] in TERM_ATOMS:
        return middle[-1]
    return 'bare'


def get_modifiers(middle):
    if not middle or middle == '_EMPTY_':
        return set()
    h, mods, t, _ = decompose_middle_hmt(middle)
    return set(c for c in mods if c in MOD_ATOMS)


def chi2_test(observed, expected, min_expected=5):
    """Simple chi-squared statistic. Returns (chi2, dof)."""
    chi2 = 0.0
    dof = 0
    for k in set(list(observed.keys()) + list(expected.keys())):
        o = observed.get(k, 0)
        e = expected.get(k, 0)
        if e < min_expected:
            continue
        chi2 += (o - e) ** 2 / e
        dof += 1
    return chi2, max(dof - 1, 1)


def cramers_v(chi2, n, k):
    """Cramer's V from chi2, N, and min(rows, cols)."""
    if n == 0 or k <= 1:
        return 0.0
    return math.sqrt(chi2 / (n * (k - 1)))


def jsd(p, q):
    """Jensen-Shannon divergence between two distributions (as dicts)."""
    keys = set(list(p.keys()) + list(q.keys()))
    total_p = sum(p.values()) or 1
    total_q = sum(q.values()) or 1
    m = {}
    for k in keys:
        m[k] = 0.5 * (p.get(k, 0) / total_p + q.get(k, 0) / total_q)
    div = 0.0
    for k in keys:
        pk = p.get(k, 0) / total_p
        qk = q.get(k, 0) / total_q
        mk = m[k]
        if pk > 0 and mk > 0:
            div += 0.5 * pk * math.log2(pk / mk)
        if qk > 0 and mk > 0:
            div += 0.5 * qk * math.log2(qk / mk)
    return div


def enrichment(count, total, base_count, base_total):
    """Enrichment ratio with small-sample safety."""
    if total == 0 or base_total == 0 or base_count == 0:
        return 0.0
    obs_rate = count / total
    base_rate = base_count / base_total
    if base_rate == 0:
        return float('inf')
    return obs_rate / base_rate


# ============================================================================
# DATA LOADING
# ============================================================================
def load_all_data():
    """Load and preprocess tokens with full morphological analysis."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    systems = {'A': [], 'B': [], 'NA': []}

    for token in tx.all(h_only=True):
        if not token.word or token.word.strip() == '' or '*' in token.word:
            continue
        if token.placement and token.placement.startswith('L'):
            continue

        m = morph.extract(token.word)
        middle = m.middle if m.middle and m.middle != '_EMPTY_' else None
        head = get_head(middle) if middle else None
        term = get_terminal(middle) if middle else None
        mods = get_modifiers(middle) if middle else set()
        cat = cc.classify(middle) if middle else None

        rec = {
            'word': token.word,
            'folio': token.folio,
            'line': token.line,
            'section': token.section,
            'language': token.language,
            'articulator': m.articulator,
            'prefix': m.prefix,
            'middle': middle,
            'suffix': m.suffix,
            'head': head,
            'terminal': term,
            'modifiers': sorted(mods),
            'category': cat,
            'line_initial': token.line_initial,
            'line_final': token.line_final,
            'par_initial': token.par_initial,
            'par_final': token.par_final,
        }

        lang = token.language if token.language in systems else None
        if lang:
            systems[lang].append(rec)

    return systems


# ============================================================================
# Q1: ARTICULATOR CHARACTERIZATION
# ============================================================================
def analyze_articulators(systems):
    """Comprehensive articulator (y-) analysis."""
    results = {}

    # 1a. Rate across systems
    rates = {}
    for sys_name, tokens in systems.items():
        total = len(tokens)
        art_count = sum(1 for t in tokens if t['articulator'] is not None)
        y_count = sum(1 for t in tokens if t['articulator'] == 'y')
        art_types = Counter(t['articulator'] for t in tokens if t['articulator'] is not None)
        rates[sys_name] = {
            'total': total,
            'articulator_count': art_count,
            'articulator_rate': round(art_count / total, 4) if total > 0 else 0,
            'y_count': y_count,
            'y_rate': round(y_count / total, 4) if total > 0 else 0,
            'type_distribution': {k: v for k, v in art_types.most_common(10)},
        }
    results['system_rates'] = rates

    # Focus on B for detailed analysis
    b_tokens = systems['B']
    art_b = [t for t in b_tokens if t['articulator'] is not None]
    non_art_b = [t for t in b_tokens if t['articulator'] is None]

    # 1b. HEAD distribution: articulated vs non-articulated
    art_heads = Counter(t['head'] for t in art_b if t['head'])
    non_art_heads = Counter(t['head'] for t in non_art_b if t['head'])
    head_jsd = jsd(dict(art_heads), dict(non_art_heads))
    results['head_divergence'] = {
        'articulated_heads': {k: v for k, v in art_heads.most_common()},
        'non_articulated_heads': {k: v for k, v in non_art_heads.most_common()},
        'jsd': round(head_jsd, 4),
    }

    # Enrichment per HEAD
    head_enrichments = {}
    total_art = len(art_b)
    total_non = len(non_art_b)
    for h in set(list(art_heads.keys()) + list(non_art_heads.keys())):
        if h is None:
            continue
        e = enrichment(art_heads.get(h, 0), total_art,
                       non_art_heads.get(h, 0), total_non)
        head_enrichments[h] = round(e, 3)
    results['head_enrichments'] = head_enrichments

    # 1c. TERMINAL distribution: articulated vs non-articulated
    art_terms = Counter(t['terminal'] for t in art_b if t['terminal'])
    non_art_terms = Counter(t['terminal'] for t in non_art_b if t['terminal'])
    term_jsd = jsd(dict(art_terms), dict(non_art_terms))
    results['terminal_divergence'] = {
        'articulated_terminals': {k: v for k, v in art_terms.most_common()},
        'non_articulated_terminals': {k: v for k, v in non_art_terms.most_common()},
        'jsd': round(term_jsd, 4),
    }

    # 1d. Suffix attachment: articulated vs non-articulated
    art_suf_rate = sum(1 for t in art_b if t['suffix']) / len(art_b) if art_b else 0
    non_suf_rate = sum(1 for t in non_art_b if t['suffix']) / len(non_art_b) if non_art_b else 0
    results['suffix_rates'] = {
        'articulated': round(art_suf_rate, 4),
        'non_articulated': round(non_suf_rate, 4),
        'ratio': round(art_suf_rate / non_suf_rate, 3) if non_suf_rate > 0 else None,
    }

    # 1e. Category distribution
    art_cats = Counter(t['category'] for t in art_b if t['category'])
    non_art_cats = Counter(t['category'] for t in non_art_b if t['category'])
    cat_jsd = jsd(dict(art_cats), dict(non_art_cats))
    results['category_divergence'] = {
        'articulated_categories': {k: v for k, v in art_cats.most_common()},
        'non_articulated_categories': {k: v for k, v in non_art_cats.most_common()},
        'jsd': round(cat_jsd, 4),
    }

    # 1f. Positional bias
    art_li = sum(1 for t in art_b if t['line_initial']) / len(art_b) if art_b else 0
    non_li = sum(1 for t in non_art_b if t['line_initial']) / len(non_art_b) if non_art_b else 0
    art_pi = sum(1 for t in art_b if t['par_initial']) / len(art_b) if art_b else 0
    non_pi = sum(1 for t in non_art_b if t['par_initial']) / len(non_art_b) if non_art_b else 0
    results['positional_bias'] = {
        'line_initial_art': round(art_li, 4),
        'line_initial_non': round(non_li, 4),
        'line_initial_enrichment': round(art_li / non_li, 3) if non_li > 0 else None,
        'par_initial_art': round(art_pi, 4),
        'par_initial_non': round(non_pi, 4),
        'par_initial_enrichment': round(art_pi / non_pi, 3) if non_pi > 0 else None,
    }

    # 1g. PREFIX interaction
    art_pfx = Counter(t['prefix'] for t in art_b)
    non_art_pfx = Counter(t['prefix'] for t in non_art_b)
    # Focus on main PREFIXes
    pfx_enrichments = {}
    for p in ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', None]:
        p_key = p if p else 'BARE'
        e = enrichment(art_pfx.get(p, 0), total_art, non_art_pfx.get(p, 0), total_non)
        pfx_enrichments[p_key] = round(e, 3)
    results['prefix_interaction'] = pfx_enrichments

    # 1h. Hazard involvement
    # Check if articulated tokens participate in forbidden transitions
    art_middles = Counter(t['middle'] for t in art_b if t['middle'])
    forbidden_middles = set()
    for src, tgt in FORBIDDEN_PAIRS:
        forbidden_middles.add(src)
        forbidden_middles.add(tgt)
    art_forbidden_count = sum(art_middles.get(m, 0) for m in forbidden_middles)
    non_art_middle_counts = Counter(t['middle'] for t in non_art_b if t['middle'])
    non_forbidden_count = sum(non_art_middle_counts.get(m, 0) for m in forbidden_middles)
    results['hazard_involvement'] = {
        'articulated_forbidden_tokens': art_forbidden_count,
        'articulated_forbidden_rate': round(art_forbidden_count / total_art, 4) if total_art > 0 else 0,
        'non_articulated_forbidden_tokens': non_forbidden_count,
        'non_articulated_forbidden_rate': round(non_forbidden_count / total_non, 4) if total_non > 0 else 0,
    }

    # 1i. y-articulator vs y-terminal comparison
    y_art_tokens = [t for t in b_tokens if t['articulator'] == 'y']
    y_term_tokens = [t for t in b_tokens if t['terminal'] == 'y' and t['articulator'] != 'y']
    y_art_heads = Counter(t['head'] for t in y_art_tokens if t['head'])
    y_term_heads = Counter(t['head'] for t in y_term_tokens if t['head'])
    y_compare_jsd = jsd(dict(y_art_heads), dict(y_term_heads))
    results['y_art_vs_y_term'] = {
        'y_art_count': len(y_art_tokens),
        'y_term_count': len(y_term_tokens),
        'y_art_heads': {k: v for k, v in y_art_heads.most_common()},
        'y_term_heads': {k: v for k, v in y_term_heads.most_common()},
        'jsd': round(y_compare_jsd, 4),
    }

    return results


# ============================================================================
# Q2: SEQUENTIAL ATOM COUPLINGS
# ============================================================================
def analyze_sequential_couplings(systems):
    """Cross-token atom couplings within lines."""
    results = {}
    b_tokens = systems['B']

    # Build lines: group tokens by folio+line
    lines = defaultdict(list)
    for t in b_tokens:
        key = (t['folio'], t['line'])
        lines[key].append(t)

    # 2a. HEAD→HEAD transitions
    head_transitions = Counter()
    head_total = Counter()
    term_to_head = Counter()
    term_total = Counter()
    suffix_effect_transitions = defaultdict(Counter)  # suffix_present -> HEAD(N+1)

    for key, line_tokens in lines.items():
        for i in range(len(line_tokens) - 1):
            t1 = line_tokens[i]
            t2 = line_tokens[i + 1]
            h1 = t1['head']
            h2 = t2['head']
            term1 = t1['terminal']

            if h1 and h2:
                head_transitions[(h1, h2)] += 1
                head_total[h1] += 1

            if term1 and h2:
                term_to_head[(term1, h2)] += 1
                term_total[term1] += 1

            # Suffix effect on next HEAD
            if h2:
                suf_present = 'suffixed' if t1['suffix'] else 'bare'
                suffix_effect_transitions[suf_present][h2] += 1

    # HEAD→HEAD matrix with enrichment
    all_heads = sorted(set(h for h, _ in head_transitions) | set(h for _, h in head_transitions))
    total_trans = sum(head_transitions.values())
    head_marginal = Counter()
    for (h1, h2), c in head_transitions.items():
        head_marginal[h2] += c

    head_head_matrix = {}
    for h1 in all_heads:
        row = {}
        for h2 in all_heads:
            obs = head_transitions.get((h1, h2), 0)
            # Expected = P(h1 as source) * P(h2 as target) * total
            exp = (head_total.get(h1, 0) / total_trans) * (head_marginal.get(h2, 0) / total_trans) * total_trans if total_trans > 0 else 0
            enrich = obs / exp if exp > 5 else None
            row[h2] = {
                'count': obs,
                'enrichment': round(enrich, 3) if enrich is not None else None,
            }
        head_head_matrix[h1] = row
    results['head_head_transitions'] = head_head_matrix

    # 2b. TERMINAL→HEAD handoff matrix
    all_terms = sorted(set(t for t, _ in term_to_head))
    term_head_matrix = {}
    total_th_trans = sum(term_to_head.values())
    th_marginal = Counter()
    for (t1, h2), c in term_to_head.items():
        th_marginal[h2] += c

    for t1 in all_terms:
        row = {}
        for h2 in all_heads:
            obs = term_to_head.get((t1, h2), 0)
            exp = (term_total.get(t1, 0) / total_th_trans) * (th_marginal.get(h2, 0) / total_th_trans) * total_th_trans if total_th_trans > 0 else 0
            enrich = obs / exp if exp > 5 else None
            row[h2] = {
                'count': obs,
                'enrichment': round(enrich, 3) if enrich is not None else None,
            }
        term_head_matrix[t1] = row
    results['terminal_head_handoffs'] = term_head_matrix

    # 2c. Suffix presence effect on next HEAD
    suf_jsd = jsd(dict(suffix_effect_transitions.get('suffixed', {})),
                  dict(suffix_effect_transitions.get('bare', {})))
    results['suffix_effect_on_next_head'] = {
        'suffixed_next_heads': {k: v for k, v in suffix_effect_transitions.get('suffixed', {}).most_common()},
        'bare_next_heads': {k: v for k, v in suffix_effect_transitions.get('bare', {}).most_common()},
        'jsd': round(suf_jsd, 4),
    }

    # 2d. Most common 2-token HEAD sequences
    head_bigrams = Counter()
    for key, line_tokens in lines.items():
        for i in range(len(line_tokens) - 1):
            h1 = line_tokens[i]['head']
            h2 = line_tokens[i + 1]['head']
            if h1 and h2:
                head_bigrams[(h1, h2)] += 1

    results['top_head_bigrams'] = [
        {'pair': f"{h1}->{h2}", 'count': c}
        for (h1, h2), c in head_bigrams.most_common(20)
    ]

    # 2e. Safe vs hazard handoff patterns
    # Safe = k→k (both immune), Hazard-related = HEADLESS→a
    safe_handoffs = Counter()
    hazard_handoffs = Counter()
    for (h1, h2), c in head_transitions.items():
        if h1 == 'k' or h2 == 'k':
            safe_handoffs[(h1, h2)] = c
        if h1 == 'HEADLESS' and h2 == 'a':
            hazard_handoffs[('HEADLESS', 'a')] = c
        if h1 == 'a':
            hazard_handoffs[('a', h2)] = c

    results['safe_handoff_count'] = sum(safe_handoffs.values())
    results['hazard_handoff_count'] = sum(hazard_handoffs.values())
    results['safe_handoffs_top'] = [
        {'pair': f"{h1}->{h2}", 'count': c}
        for (h1, h2), c in safe_handoffs.most_common(10)
    ]
    results['hazard_handoffs_top'] = [
        {'pair': f"{h1}->{h2}", 'count': c}
        for (h1, h2), c in hazard_handoffs.most_common(10)
    ]

    # 2f. Self-transition rates per HEAD
    self_rates = {}
    for h in all_heads:
        self_count = head_transitions.get((h, h), 0)
        total_from_h = head_total.get(h, 0)
        self_rates[h] = {
            'self_count': self_count,
            'total_from': total_from_h,
            'self_rate': round(self_count / total_from_h, 4) if total_from_h > 0 else 0,
        }
    results['head_self_transition_rates'] = self_rates

    return results


# ============================================================================
# Q3: PARAGRAPH ATOM SIGNATURES
# ============================================================================
def analyze_paragraph_signatures(systems):
    """Paragraph header vs body atom profiles and convergence."""
    results = {}
    b_tokens = systems['B']

    # Build paragraphs: group by folio, detect paragraph boundaries
    # par_initial=True marks first token of paragraph
    folio_lines = defaultdict(lambda: defaultdict(list))
    for t in b_tokens:
        folio_lines[t['folio']][t['line']].append(t)

    # Build paragraph groups: list of (folio, [(line_num, [tokens]), ...])
    paragraphs = []
    for folio in sorted(folio_lines.keys()):
        line_nums = sorted(folio_lines[folio].keys(), key=lambda x: int(x) if x.isdigit() else 0)
        current_para = []
        for ln in line_nums:
            tokens = folio_lines[folio][ln]
            if tokens and tokens[0]['par_initial'] and current_para:
                paragraphs.append((folio, current_para))
                current_para = []
            current_para.append((ln, tokens))
        if current_para:
            paragraphs.append((folio, current_para))

    # 3a. Header (line 1) vs body (lines 2+) HEAD distribution
    header_heads = Counter()
    body_heads = Counter()
    header_terms = Counter()
    body_terms = Counter()
    header_mods = Counter()
    body_mods = Counter()
    header_cats = Counter()
    body_cats = Counter()

    for folio, para_lines in paragraphs:
        if len(para_lines) < 2:
            continue  # Need at least 2 lines
        # Header = first line
        for t in para_lines[0][1]:
            if t['head']:
                header_heads[t['head']] += 1
            if t['terminal']:
                header_terms[t['terminal']] += 1
            for mod in t['modifiers']:
                header_mods[mod] += 1
            if t['category']:
                header_cats[t['category']] += 1

        # Body = lines 2+
        for ln, tokens in para_lines[1:]:
            for t in tokens:
                if t['head']:
                    body_heads[t['head']] += 1
                if t['terminal']:
                    body_terms[t['terminal']] += 1
                for mod in t['modifiers']:
                    body_mods[mod] += 1
                if t['category']:
                    body_cats[t['category']] += 1

    results['header_vs_body_head'] = {
        'header': {k: v for k, v in header_heads.most_common()},
        'body': {k: v for k, v in body_heads.most_common()},
        'jsd': round(jsd(dict(header_heads), dict(body_heads)), 4),
    }
    results['header_vs_body_terminal'] = {
        'header': {k: v for k, v in header_terms.most_common()},
        'body': {k: v for k, v in body_terms.most_common()},
        'jsd': round(jsd(dict(header_terms), dict(body_terms)), 4),
    }
    results['header_vs_body_modifiers'] = {
        'header': {k: v for k, v in header_mods.most_common()},
        'body': {k: v for k, v in body_mods.most_common()},
        'jsd': round(jsd(dict(header_mods), dict(body_mods)), 4),
    }
    results['header_vs_body_category'] = {
        'header': {k: v for k, v in header_cats.most_common()},
        'body': {k: v for k, v in body_cats.most_common()},
        'jsd': round(jsd(dict(header_cats), dict(body_cats)), 4),
    }

    # HEAD enrichment header vs body
    total_header = sum(header_heads.values())
    total_body = sum(body_heads.values())
    head_enrichments = {}
    for h in set(list(header_heads.keys()) + list(body_heads.keys())):
        e = enrichment(header_heads.get(h, 0), total_header,
                       body_heads.get(h, 0), total_body)
        head_enrichments[h] = round(e, 3)
    results['header_head_enrichments'] = head_enrichments

    # TERMINAL enrichment header vs body
    total_header_t = sum(header_terms.values())
    total_body_t = sum(body_terms.values())
    term_enrichments = {}
    for t in set(list(header_terms.keys()) + list(body_terms.keys())):
        e = enrichment(header_terms.get(t, 0), total_header_t,
                       body_terms.get(t, 0), total_body_t)
        term_enrichments[t] = round(e, 3)
    results['header_terminal_enrichments'] = term_enrichments

    # 3b. Atomic convergence: do later lines look more similar?
    # For paragraphs with 4+ lines, compute JSD(line_i_heads, line_j_heads)
    # Compare early pairs (1 vs 2) vs late pairs (N-1 vs N)
    convergence_data = {'early_jsds': [], 'late_jsds': [], 'header_body_jsds': []}
    for folio, para_lines in paragraphs:
        if len(para_lines) < 4:
            continue

        line_head_profiles = []
        for ln, tokens in para_lines:
            heads = Counter(t['head'] for t in tokens if t['head'])
            line_head_profiles.append(dict(heads))

        # Header vs first body
        if len(line_head_profiles) >= 2:
            convergence_data['header_body_jsds'].append(
                jsd(line_head_profiles[0], line_head_profiles[1]))

        # Early body (lines 2-3) vs late body (lines N-1, N)
        if len(line_head_profiles) >= 4:
            early_jsd_val = jsd(line_head_profiles[1], line_head_profiles[2])
            late_jsd_val = jsd(line_head_profiles[-2], line_head_profiles[-1])
            convergence_data['early_jsds'].append(early_jsd_val)
            convergence_data['late_jsds'].append(late_jsd_val)

    results['convergence'] = {
        'n_paragraphs': len([p for _, p in paragraphs if len(p) >= 4]),
        'mean_header_body_jsd': round(sum(convergence_data['header_body_jsds']) / len(convergence_data['header_body_jsds']), 4) if convergence_data['header_body_jsds'] else None,
        'mean_early_jsd': round(sum(convergence_data['early_jsds']) / len(convergence_data['early_jsds']), 4) if convergence_data['early_jsds'] else None,
        'mean_late_jsd': round(sum(convergence_data['late_jsds']) / len(convergence_data['late_jsds']), 4) if convergence_data['late_jsds'] else None,
        'convergence_detected': None,  # Will be set below
    }
    if convergence_data['early_jsds'] and convergence_data['late_jsds']:
        early_mean = sum(convergence_data['early_jsds']) / len(convergence_data['early_jsds'])
        late_mean = sum(convergence_data['late_jsds']) / len(convergence_data['late_jsds'])
        results['convergence']['convergence_detected'] = late_mean < early_mean
        results['convergence']['early_late_ratio'] = round(late_mean / early_mean, 3) if early_mean > 0 else None

    # 3c. Paragraph "types" based on HEAD composition
    # Cluster paragraphs by dominant HEAD
    para_types = Counter()
    for folio, para_lines in paragraphs:
        all_heads = Counter()
        for ln, tokens in para_lines:
            for t in tokens:
                if t['head']:
                    all_heads[t['head']] += 1
        if all_heads:
            dominant = all_heads.most_common(1)[0][0]
            para_types[dominant] += 1
    results['paragraph_dominant_head_types'] = {k: v for k, v in para_types.most_common()}

    return results


# ============================================================================
# Q4: LINE-POSITION ATOM GRADIENT
# ============================================================================
def analyze_line_position_gradient(systems):
    """Quintile-resolved HEAD/MOD/TERM distributions across line positions."""
    results = {}
    b_tokens = systems['B']

    # Build lines and assign quintile positions
    lines = defaultdict(list)
    for t in b_tokens:
        key = (t['folio'], t['line'])
        lines[key].append(t)

    quintile_heads = {q: Counter() for q in range(5)}
    quintile_terms = {q: Counter() for q in range(5)}
    quintile_mods = {q: Counter() for q in range(5)}
    quintile_cats = {q: Counter() for q in range(5)}
    quintile_counts = Counter()

    for key, line_tokens in lines.items():
        n = len(line_tokens)
        if n < 3:
            continue  # Skip very short lines

        for i, t in enumerate(line_tokens):
            # Assign quintile: Q0 = first 20%, Q4 = last 20%
            q = min(int(i / n * 5), 4)
            quintile_counts[q] += 1

            if t['head']:
                quintile_heads[q][t['head']] += 1
            if t['terminal']:
                quintile_terms[q][t['terminal']] += 1
            for mod in t['modifiers']:
                quintile_mods[q][mod] += 1
            if t['category']:
                quintile_cats[q][t['category']] += 1

    # 4a. HEAD distribution by quintile
    head_by_quintile = {}
    all_heads = sorted(set(h for q in range(5) for h in quintile_heads[q]))
    for h in all_heads:
        profile = []
        total_h = sum(quintile_heads[q].get(h, 0) for q in range(5))
        for q in range(5):
            count = quintile_heads[q].get(h, 0)
            total_q = sum(quintile_heads[q].values())
            rate = count / total_q if total_q > 0 else 0
            profile.append(round(rate, 4))
        # Q0/Q4 ratio
        q0_rate = profile[0]
        q4_rate = profile[4]
        ratio = round(q0_rate / q4_rate, 3) if q4_rate > 0 else None
        head_by_quintile[h] = {
            'profile': profile,
            'Q0_Q4_ratio': ratio,
            'total': total_h,
        }
    results['head_by_quintile'] = head_by_quintile

    # 4b. TERMINAL distribution by quintile
    term_by_quintile = {}
    all_terms = sorted(set(t for q in range(5) for t in quintile_terms[q]))
    for t in all_terms:
        profile = []
        total_t = sum(quintile_terms[q].get(t, 0) for q in range(5))
        for q in range(5):
            count = quintile_terms[q].get(t, 0)
            total_q = sum(quintile_terms[q].values())
            rate = count / total_q if total_q > 0 else 0
            profile.append(round(rate, 4))
        q0_rate = profile[0]
        q4_rate = profile[4]
        ratio = round(q0_rate / q4_rate, 3) if q4_rate > 0 else None
        term_by_quintile[t] = {
            'profile': profile,
            'Q0_Q4_ratio': ratio,
            'total': total_t,
        }
    results['terminal_by_quintile'] = term_by_quintile

    # 4c. MODIFIER distribution by quintile
    mod_by_quintile = {}
    all_mods_set = sorted(set(m for q in range(5) for m in quintile_mods[q]))
    for m in all_mods_set:
        profile = []
        total_m = sum(quintile_mods[q].get(m, 0) for q in range(5))
        for q in range(5):
            count = quintile_mods[q].get(m, 0)
            total_q = sum(quintile_mods[q].values())
            rate = count / total_q if total_q > 0 else 0
            profile.append(round(rate, 4))
        q0_rate = profile[0]
        q4_rate = profile[4]
        ratio = round(q0_rate / q4_rate, 3) if q4_rate > 0 else None
        mod_by_quintile[m] = {
            'profile': profile,
            'Q0_Q4_ratio': ratio,
            'total': total_m,
        }
    results['modifier_by_quintile'] = mod_by_quintile

    # 4d. Category distribution by quintile
    cat_by_quintile = {}
    all_cats = sorted(set(c for q in range(5) for c in quintile_cats[q]))
    for c in all_cats:
        profile = []
        total_c = sum(quintile_cats[q].get(c, 0) for q in range(5))
        for q in range(5):
            count = quintile_cats[q].get(c, 0)
            total_q = sum(quintile_cats[q].values())
            rate = count / total_q if total_q > 0 else 0
            profile.append(round(rate, 4))
        q0_rate = profile[0]
        q4_rate = profile[4]
        ratio = round(q0_rate / q4_rate, 3) if q4_rate > 0 else None
        cat_by_quintile[c] = {
            'profile': profile,
            'Q0_Q4_ratio': ratio,
            'total': total_c,
        }
    results['category_by_quintile'] = cat_by_quintile

    # 4e. Gradient smoothness: compute pairwise adjacent-quintile JSD for HEADs
    adjacent_jsds = []
    for q in range(4):
        d = jsd(dict(quintile_heads[q]), dict(quintile_heads[q + 1]))
        adjacent_jsds.append(round(d, 4))
    results['head_adjacent_quintile_jsd'] = adjacent_jsds

    # Also for TERMINALs
    term_adjacent_jsds = []
    for q in range(4):
        d = jsd(dict(quintile_terms[q]), dict(quintile_terms[q + 1]))
        term_adjacent_jsds.append(round(d, 4))
    results['terminal_adjacent_quintile_jsd'] = term_adjacent_jsds

    # Q0 vs Q4 overall JSD
    results['head_Q0_Q4_jsd'] = round(jsd(dict(quintile_heads[0]), dict(quintile_heads[4])), 4)
    results['terminal_Q0_Q4_jsd'] = round(jsd(dict(quintile_terms[0]), dict(quintile_terms[4])), 4)

    results['quintile_token_counts'] = {str(q): quintile_counts[q] for q in range(5)}

    return results


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("Phase 549: Atom Architecture Cleanup")
    print("=" * 60)

    print("\nLoading data...")
    systems = load_all_data()
    print(f"  A: {len(systems['A'])} tokens")
    print(f"  B: {len(systems['B'])} tokens")
    print(f"  AZC: {len(systems['NA'])} tokens")

    results = {}

    print("\nQ1: Articulator Characterization...")
    results['Q1_articulators'] = analyze_articulators(systems)
    print(f"  B articulator rate: {results['Q1_articulators']['system_rates']['B']['articulator_rate']}")
    print(f"  HEAD divergence JSD: {results['Q1_articulators']['head_divergence']['jsd']}")

    print("\nQ2: Sequential Atom Couplings...")
    results['Q2_sequential'] = analyze_sequential_couplings(systems)
    top_bigram = results['Q2_sequential']['top_head_bigrams'][0] if results['Q2_sequential']['top_head_bigrams'] else None
    if top_bigram:
        print(f"  Top HEAD bigram: {top_bigram['pair']} ({top_bigram['count']})")

    print("\nQ3: Paragraph Atom Signatures...")
    results['Q3_paragraphs'] = analyze_paragraph_signatures(systems)
    print(f"  Header-body HEAD JSD: {results['Q3_paragraphs']['header_vs_body_head']['jsd']}")

    print("\nQ4: Line-Position Atom Gradient...")
    results['Q4_gradient'] = analyze_line_position_gradient(systems)
    print(f"  HEAD Q0-Q4 JSD: {results['Q4_gradient']['head_Q0_Q4_jsd']}")
    print(f"  TERM Q0-Q4 JSD: {results['Q4_gradient']['terminal_Q0_Q4_jsd']}")

    # Save results
    out_path = PROJECT_ROOT / 'phases' / 'ATOM_ARCHITECTURE_CLEANUP' / 'results' / 'atom_cleanup.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")

    # Print key summary
    print("\n" + "=" * 60)
    print("KEY FINDINGS SUMMARY")
    print("=" * 60)

    # Q1 summary
    q1 = results['Q1_articulators']
    print(f"\nQ1 - Articulator:")
    print(f"  B rate: {q1['system_rates']['B']['articulator_rate']} ({q1['system_rates']['B']['articulator_count']}/{q1['system_rates']['B']['total']})")
    print(f"  A rate: {q1['system_rates']['A']['articulator_rate']} ({q1['system_rates']['A']['articulator_count']}/{q1['system_rates']['A']['total']})")
    print(f"  HEAD divergence (art vs non): JSD={q1['head_divergence']['jsd']}")
    print(f"  TERMINAL divergence: JSD={q1['terminal_divergence']['jsd']}")
    print(f"  Category divergence: JSD={q1['category_divergence']['jsd']}")
    print(f"  Suffix rate art: {q1['suffix_rates']['articulated']} vs non: {q1['suffix_rates']['non_articulated']}")
    print(f"  Line-initial enrichment: {q1['positional_bias']['line_initial_enrichment']}")
    print(f"  Par-initial enrichment: {q1['positional_bias']['par_initial_enrichment']}")
    print(f"  PREFIX interaction:")
    for p, e in sorted(q1['prefix_interaction'].items(), key=lambda x: -x[1]):
        if e > 1.5 or e < 0.5:
            print(f"    {p}: {e}x")
    print(f"  y-art vs y-term JSD: {q1['y_art_vs_y_term']['jsd']}")

    # Q2 summary
    q2 = results['Q2_sequential']
    print(f"\nQ2 - Sequential Couplings:")
    print(f"  Self-transition rates:")
    for h, data in sorted(q2['head_self_transition_rates'].items()):
        print(f"    {h}: {data['self_rate']} ({data['self_count']}/{data['total_from']})")
    print(f"  Top HEAD bigrams:")
    for bg in q2['top_head_bigrams'][:5]:
        print(f"    {bg['pair']}: {bg['count']}")
    print(f"  Suffix effect JSD: {q2['suffix_effect_on_next_head']['jsd']}")

    # Q3 summary
    q3 = results['Q3_paragraphs']
    print(f"\nQ3 - Paragraph Signatures:")
    print(f"  Header-body HEAD JSD: {q3['header_vs_body_head']['jsd']}")
    print(f"  Header-body TERMINAL JSD: {q3['header_vs_body_terminal']['jsd']}")
    print(f"  Header-body MODIFIER JSD: {q3['header_vs_body_modifiers']['jsd']}")
    print(f"  Header-body CATEGORY JSD: {q3['header_vs_body_category']['jsd']}")
    print(f"  Header HEAD enrichments:")
    for h, e in sorted(q3['header_head_enrichments'].items(), key=lambda x: -x[1]):
        print(f"    {h}: {e}x")
    print(f"  Convergence:")
    conv = q3['convergence']
    print(f"    Header-body JSD: {conv['mean_header_body_jsd']}")
    print(f"    Early body JSD: {conv['mean_early_jsd']}")
    print(f"    Late body JSD: {conv['mean_late_jsd']}")
    print(f"    Late/early ratio: {conv.get('early_late_ratio')}")
    print(f"  Paragraph dominant HEAD types: {q3['paragraph_dominant_head_types']}")

    # Q4 summary
    q4 = results['Q4_gradient']
    print(f"\nQ4 - Line-Position Gradient:")
    print(f"  HEAD Q0-Q4 JSD: {q4['head_Q0_Q4_jsd']}")
    print(f"  TERMINAL Q0-Q4 JSD: {q4['terminal_Q0_Q4_jsd']}")
    print(f"  HEAD quintile profiles (rate across Q0..Q4):")
    for h, data in sorted(q4['head_by_quintile'].items()):
        prof = ' '.join(f"{v:.3f}" for v in data['profile'])
        print(f"    {h:10s}: [{prof}] Q0/Q4={data['Q0_Q4_ratio']}")
    print(f"  TERMINAL quintile profiles:")
    for t, data in sorted(q4['terminal_by_quintile'].items()):
        prof = ' '.join(f"{v:.3f}" for v in data['profile'])
        print(f"    {t:10s}: [{prof}] Q0/Q4={data['Q0_Q4_ratio']}")
    print(f"  HEAD adjacent-Q JSD: {q4['head_adjacent_quintile_jsd']}")
    print(f"  TERM adjacent-Q JSD: {q4['terminal_adjacent_quintile_jsd']}")


if __name__ == '__main__':
    main()
