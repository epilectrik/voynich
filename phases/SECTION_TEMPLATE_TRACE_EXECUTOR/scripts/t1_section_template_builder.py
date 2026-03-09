"""Phase 562 T1: Section Template Builder

Constructs a SectionTemplate for each of the 5 sections (S, H, B, C, T)
by aggregating corpus statistics from the Phase 560 T1 corpus.

Per-section template contents:
  A. Domain priors (mean fracs + covariance)
  B. Paragraph cloud prior (raw 6D vectors + mean + dispersion)
  C. Line packet priors (per-quintile domain, hazard, Q4 closure)
  D. Headless ecology prior
  E. Routing grammar priors (core + exploratory split)
  F. Hazard posture prior
  G. Closure class prior
  H. Headless subtype prior

Input:  phases/WITHIN_DOMAIN_COMPOSITIONAL_CONTROL/results/t1_domain_decomposition.json
Output: phases/SECTION_TEMPLATE_TRACE_EXECUTOR/results/t1_section_templates.json
"""
import json
import time
import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

# ═══════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════

DOMAINS = ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY', 'ARRANGEMENT', 'HEADLESS']
DOMAIN_ORDER = {d: i for i, d in enumerate(DOMAINS)}

# Routing grammar (C1563 canonical set)
CORE_ROUTE = {
    'r': 'ACTIVE',       # r→a 2.231x
    'y': 'THERMAL',      # y→k 1.597x
    'h': 'FLOW',         # h→t 1.892x
    'm': 'ARRANGEMENT',  # m→o 1.554x
}
EXPLORATORY_ROUTE = {
    'n': 'ACTIVE',       # n→a 1.424x (candidate)
    'l': 'STABILITY',    # l→e 1.246x (candidate)
}
PRIMARY_ROUTE = {**CORE_ROUTE, **EXPLORATORY_ROUTE, 'bare': 'NEUTRAL'}

# C1563 reference enrichments for validation
C1563_ENRICHMENTS = {
    'r': ('ACTIVE', 2.231),
    'y': ('THERMAL', 1.597),
    'h': ('FLOW', 1.892),
    'm': ('ARRANGEMENT', 1.554),
    'n': ('ACTIVE', 1.424),
    'l': ('STABILITY', 1.246),
}

HAZARD_POSTURES = ['IMMUNE', 'ZERO', 'LOW', 'HIGH']
CLOSURE_CLASSES = ['SPEC_OPEN', 'WORK_TRANSPARENT', 'WORK_SEMI',
                   'CLOSE_OPAQUE', 'CLOSE_TRANSITIONAL']
HEADLESS_SUBTYPES = ['PSEUDO_D', 'PSEUDO_I', 'PSEUDO_L',
                     'PARAMETRIC_CPF', 'OTHER_HEADLESS']

MIN_PARA_BODY_LINES = 3
MIN_PARA_TOKENS = 15

SMALL_SECTION_THRESHOLD = 2000  # tokens (C=1480, T=662)


# ═══════════════════════════════════════════════════════════════
# Derived evaluation target functions (from plan)
# ═══════════════════════════════════════════════════════════════

def derive_hazard_posture(token):
    """Derive hazard posture from token composition using Tier 2 rules.

    IMMUNE = k-HEAD: 0% source AND 0% target across ALL frames (C1446, C1476)
    ZERO   = explicit safe frames: e->y (C1458), a+ii (C1482), quenching (C1450),
             safe_pathway. These tokens may be targets but are in validated safe
             configurations.
    HIGH   = explicit high-hazard frames: a->l/r (C1477: 98.5-98.9% target),
             or EXPOSED (not source_immune) with frame_hazard HIGH (C1448).
    LOW    = default: headed non-k tokens not in special frames, or headless
             tokens not in high-hazard configurations.

    Note: source_immune (C1546) covers ALL headed tokens + quench-modified
    headless, NOT just k-HEAD. We use head=='k' for IMMUNE, not source_immune.
    """
    # Priority 1: k-HEAD intrinsic immunity (C1446, C1476: 0% source AND target)
    if token.get('head') == 'k':
        return 'IMMUNE'

    # Priority 2: Explicit safe frames with strong validation
    if token.get('head') == 'e' and token.get('term') == 'y':
        return 'ZERO'     # C1458: 3475 tokens, 0.06%
    if token.get('head') == 'a' and (token.get('i_count') or 0) >= 2:
        return 'ZERO'     # C1482: 887 tokens, 0.0%
    if token.get('has_quenching_mod') and token.get('head') in ('e', 'o', 't'):
        return 'ZERO'     # C1450: quenching validated
    if token.get('is_safe_pathway'):
        return 'ZERO'

    # Priority 3: Explicit high-hazard frames
    if token.get('head') == 'a' and token.get('term') in ('l', 'r'):
        return 'HIGH'     # C1477: 98.5-98.9% target hazard
    if not token.get('source_immune') and token.get('frame_hazard') == 'HIGH':
        return 'HIGH'     # C1448: EXPOSED headless in high-hazard frame

    # Priority 4: Default
    return 'LOW'


def derive_closure_class(token):
    """Derive closure class from terminal opacity and line zone."""
    opacity = token.get('terminal_opacity')
    term = token.get('term')
    zone = token.get('line_zone', 'WORK')
    if term == 'm':
        return 'CLOSE_TRANSITIONAL'
    if zone == 'SPEC' and opacity == 'TRANSPARENT':
        return 'SPEC_OPEN'
    if zone == 'WORK' and opacity == 'TRANSPARENT':
        return 'WORK_TRANSPARENT'
    if zone == 'CLOSE' and opacity == 'OPAQUE':
        return 'CLOSE_OPAQUE'
    if opacity in ('OPAQUE', None) and zone == 'WORK':
        return 'WORK_SEMI'
    return 'WORK_SEMI'


def derive_headless_subtype(token):
    """Derive headless subtype from pseudo-head atom."""
    if token.get('domain') != 'HEADLESS':
        return 'HEADED'
    ph = token.get('pseudo_head_atom')
    if ph == 'd':
        return 'PSEUDO_D'
    if ph == 'i':
        return 'PSEUDO_I'
    if ph == 'l':
        return 'PSEUDO_L'
    if ph in ('c', 'p', 'f'):
        return 'PARAMETRIC_CPF'
    return 'OTHER_HEADLESS'


def derive_routing_target(token):
    """Derive routing target from terminal atom."""
    term = token.get('term')
    if term is None:
        return 'NEUTRAL'
    return PRIMARY_ROUTE.get(term, 'NEUTRAL')


# ═══════════════════════════════════════════════════════════════
# Utility functions
# ═══════════════════════════════════════════════════════════════

def dist_from_counter(counter, categories):
    """Convert Counter to normalized distribution over fixed categories."""
    total = sum(counter.values())
    if total == 0:
        return {c: 1.0 / len(categories) for c in categories}
    return {c: counter.get(c, 0) / total for c in categories}


def covariance_6d(vectors):
    """Compute 6x6 covariance matrix from list of 6D vectors."""
    n = len(vectors)
    if n < 2:
        return [[0.0] * 6 for _ in range(6)]
    # Compute means
    means = [0.0] * 6
    for v in vectors:
        for i in range(6):
            means[i] += v[i]
    means = [m / n for m in means]
    # Compute covariance
    cov = [[0.0] * 6 for _ in range(6)]
    for v in vectors:
        for i in range(6):
            for j in range(6):
                cov[i][j] += (v[i] - means[i]) * (v[j] - means[j])
    for i in range(6):
        for j in range(6):
            cov[i][j] /= (n - 1)
    return cov


def jsd(p_vec, q_vec):
    """Jensen-Shannon divergence between two distributions (as lists)."""
    n = len(p_vec)
    m_vec = [(p_vec[i] + q_vec[i]) / 2.0 for i in range(n)]
    div = 0.0
    for i in range(n):
        if p_vec[i] > 0 and m_vec[i] > 0:
            div += p_vec[i] * math.log2(p_vec[i] / m_vec[i])
        if q_vec[i] > 0 and m_vec[i] > 0:
            div += q_vec[i] * math.log2(q_vec[i] / m_vec[i])
    return div / 2.0


def token_to_domain_vec(tokens):
    """Convert list of tokens to 6D domain fraction vector."""
    if not tokens:
        return [1.0 / 6] * 6
    counter = Counter(t['domain'] for t in tokens)
    total = len(tokens)
    return [counter.get(d, 0) / total for d in DOMAINS]


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    print("=== Phase 562 T1: Section Template Builder ===")

    # Load Phase 560 T1 corpus
    corpus_path = (Path(__file__).resolve().parents[2] /
                   'WITHIN_DOMAIN_COMPOSITIONAL_CONTROL' / 'results' /
                   't1_domain_decomposition.json')
    print(f"  Loading corpus from {corpus_path}...")
    with open(corpus_path) as f:
        data = json.load(f)
    corpus = data['corpus_tokens']
    print(f"  Loaded {len(corpus)} tokens")

    # ───────────────────────────────────────────────────────
    # Step 0: Derive evaluation targets for all tokens
    # ───────────────────────────────────────────────────────
    print("  Deriving evaluation targets...")
    for tok in corpus:
        tok['hazard_posture'] = derive_hazard_posture(tok)
        tok['routing_target'] = derive_routing_target(tok)
        tok['closure_class'] = derive_closure_class(tok)
        tok['headless_subtype_derived'] = derive_headless_subtype(tok)

    # ───────────────────────────────────────────────────────
    # Step 1: Group tokens by section, folio, paragraph, line
    # ───────────────────────────────────────────────────────
    print("  Grouping tokens...")
    by_section = defaultdict(list)
    by_section_folio = defaultdict(lambda: defaultdict(list))
    by_section_folio_para = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list)))
    by_section_folio_para_line = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))

    for tok in corpus:
        sec = tok['section']
        fol = tok['folio']
        pi = tok['paragraph_idx']
        li = tok['line']
        by_section[sec].append(tok)
        by_section_folio[sec][fol].append(tok)
        by_section_folio_para[sec][fol][pi].append(tok)
        by_section_folio_para_line[sec][fol][pi][li].append(tok)

    sections = sorted(by_section.keys())
    print(f"  Sections: {sections}")
    for sec in sections:
        print(f"    {sec}: {len(by_section[sec])} tokens, "
              f"{len(by_section_folio[sec])} folios")

    # ───────────────────────────────────────────────────────
    # Step 2: Build templates
    # ───────────────────────────────────────────────────────
    templates = {}

    for sec in sections:
        print(f"\n  Building template for section {sec}...")
        sec_tokens = by_section[sec]
        sec_folios = by_section_folio[sec]
        n_tokens = len(sec_tokens)
        is_small = n_tokens < SMALL_SECTION_THRESHOLD

        # ═══ A. Domain priors ═══
        # Per-folio domain fracs, then mean + covariance
        folio_domain_vecs = []
        for fol, ftoks in sec_folios.items():
            folio_domain_vecs.append(token_to_domain_vec(ftoks))

        # Section-level domain fracs (from all tokens, not mean-of-folios)
        domain_counter = Counter(t['domain'] for t in sec_tokens)
        domain_fracs = dist_from_counter(domain_counter, DOMAINS)

        # Covariance of folio-level domain vectors
        domain_cov = covariance_6d(folio_domain_vecs)

        # ═══ B. Paragraph cloud prior ═══
        para_cloud_vectors = []
        para_cloud_meta = []

        for fol in sec_folios:
            paras = by_section_folio_para[sec][fol]
            for pi, ptoks in paras.items():
                # Count body lines (not HEADER, not TAIL)
                lines_in_para = by_section_folio_para_line[sec][fol][pi]
                n_lines = len(lines_in_para)
                # Body lines = total - 1 (header) - 1 (tail) if >= 3 lines
                body_lines = max(0, n_lines - 2) if n_lines >= 3 else 0
                if body_lines < MIN_PARA_BODY_LINES:
                    continue
                if len(ptoks) < MIN_PARA_TOKENS:
                    continue
                vec = token_to_domain_vec(ptoks)
                para_cloud_vectors.append(vec)
                para_cloud_meta.append({'folio': fol, 'paragraph_idx': pi,
                                        'n_tokens': len(ptoks)})

        # Cloud mean and dispersion
        if para_cloud_vectors:
            cloud_mean = [0.0] * 6
            for v in para_cloud_vectors:
                for i in range(6):
                    cloud_mean[i] += v[i]
            cloud_mean = [m / len(para_cloud_vectors) for m in cloud_mean]
            cloud_cov = covariance_6d(para_cloud_vectors)
        else:
            cloud_mean = [1.0 / 6] * 6
            cloud_cov = [[0.0] * 6 for _ in range(6)]

        # ═══ C. Line packet priors ═══
        # Per-quintile domain distributions + hazard + closure features
        quintile_tokens = defaultdict(list)  # q -> [tokens]
        for tok in sec_tokens:
            q = tok.get('quintile', 2)
            quintile_tokens[q].append(tok)

        per_quintile = {}
        for q in range(5):
            qtoks = quintile_tokens[q]
            if not qtoks:
                per_quintile[q] = {
                    'domain_dist': {d: 1.0 / 6 for d in DOMAINS},
                    'hazard_high_frac': 0.0,
                    'hazard_zero_frac': 0.0,
                    'safe_pathway_frac': 0.0,
                    'm_terminal_rate': 0.0,
                    'opaque_rate': 0.0,
                    'n_tokens': 0,
                }
                continue

            q_domain = Counter(t['domain'] for t in qtoks)
            q_hazard = Counter(t['hazard_posture'] for t in qtoks)
            n = len(qtoks)
            m_terms = sum(1 for t in qtoks if t.get('term') == 'm')
            opaque = sum(1 for t in qtoks
                         if t.get('terminal_opacity') == 'OPAQUE')
            safe = sum(1 for t in qtoks if t.get('is_safe_pathway'))

            per_quintile[q] = {
                'domain_dist': dist_from_counter(q_domain, DOMAINS),
                'hazard_high_frac': q_hazard.get('HIGH', 0) / n,
                'hazard_zero_frac': (q_hazard.get('ZERO', 0) +
                                     q_hazard.get('IMMUNE', 0)) / n,
                'safe_pathway_frac': safe / n,
                'm_terminal_rate': m_terms / n,
                'opaque_rate': opaque / n,
                'n_tokens': n,
            }

        # Q3→Q4 HEAD JSD
        q3_domain = per_quintile[3]['domain_dist']
        q4_domain = per_quintile[4]['domain_dist']
        q3_vec = [q3_domain[d] for d in DOMAINS]
        q4_vec = [q4_domain[d] for d in DOMAINS]
        q3q4_jsd = jsd(q3_vec, q4_vec)

        # Q2→Q3 HEAD JSD for comparison
        q2_domain = per_quintile[2]['domain_dist']
        q2_vec = [q2_domain[d] for d in DOMAINS]
        q2q3_jsd = jsd(q2_vec, q3_vec)

        # ═══ D. Headless ecology prior ═══
        hl_tokens = [t for t in sec_tokens if t['domain'] == 'HEADLESS']
        hl_rate = len(hl_tokens) / n_tokens if n_tokens > 0 else 0

        pseudo_head_counter = Counter(
            t.get('pseudo_head_atom', 'unknown') for t in hl_tokens)
        pseudo_atoms = ['d', 'i', 'l', 'c', 'p', 'f']
        pseudo_head_dist = {}
        hl_total = len(hl_tokens) if hl_tokens else 1
        for atom in pseudo_atoms:
            pseudo_head_dist[atom] = pseudo_head_counter.get(atom, 0) / hl_total
        pseudo_head_dist['other'] = sum(
            v for k, v in pseudo_head_counter.items()
            if k not in pseudo_atoms) / hl_total

        # Displaced head terminal rate (non-kt only per C1574)
        displaced = sum(1 for t in hl_tokens
                        if t.get('has_displaced_head_terminal'))
        displaced_nonkt_rate = displaced / hl_total if hl_total > 0 else 0

        # Suffix bifurcation
        hl_with_sfx = sum(1 for t in hl_tokens
                          if t.get('suffix') and len(t['suffix']) > 0)
        # Binary suffix = suffix of length 1 (single atom)
        hl_binary_sfx = sum(1 for t in hl_tokens
                            if t.get('suffix') and len(t['suffix']) == 1)
        # Parametric suffix = any suffix (for parametric subtypes)
        parametric_hl = [t for t in hl_tokens
                         if t.get('pseudo_head_atom') in ('c', 'p', 'f')]
        parametric_sfx_rate = (
            sum(1 for t in parametric_hl
                if t.get('suffix') and len(t['suffix']) > 0) /
            max(len(parametric_hl), 1))

        headless_ecology = {
            'hl_rate': round(hl_rate, 4),
            'pseudo_head_dist': {k: round(v, 4)
                                 for k, v in pseudo_head_dist.items()},
            'displaced_nonkt_rate': round(displaced_nonkt_rate, 4),
            'suffix_bifurcation': {
                'binary_sfx_rate': round(hl_binary_sfx / max(hl_total, 1), 4),
                'parametric_sfx_rate': round(parametric_sfx_rate, 4),
            },
        }

        # ═══ E. Routing grammar priors ═══
        # Build terminal → next HEAD transition matrix
        term_counter = Counter()
        term_to_next_head = defaultdict(Counter)  # term -> {domain: count}
        marginal_head = Counter()

        for tok in sec_tokens:
            term = tok.get('term')
            head = tok.get('head')
            if head:
                marginal_head[head] += 1
            if term:
                term_counter[term] += 1
                # Use next_domain_same_line for routing
                next_dom = tok.get('next_domain_same_line')
                if next_dom:
                    term_to_next_head[term][next_dom] += 1

        # Compute enrichment ratios
        # Marginal domain distribution (all tokens)
        marginal_domain = dist_from_counter(
            Counter(t['domain'] for t in sec_tokens), DOMAINS)

        routing_enrichments = {}
        for term_atom, (target_domain, ref_ratio) in C1563_ENRICHMENTS.items():
            nexts = term_to_next_head.get(term_atom)
            if not nexts:
                routing_enrichments[term_atom] = {
                    'target_domain': target_domain,
                    'ref_enrichment': ref_ratio,
                    'observed_enrichment': None,
                    'deviation_pct': None,
                    'n_transitions': 0,
                }
                continue
            total_nexts = sum(nexts.values())
            observed_frac = nexts.get(target_domain, 0) / total_nexts
            expected_frac = marginal_domain.get(target_domain, 1.0 / 6)
            if expected_frac > 0:
                observed_ratio = observed_frac / expected_frac
            else:
                observed_ratio = 0
            deviation = (observed_ratio - ref_ratio) / ref_ratio * 100

            routing_enrichments[term_atom] = {
                'target_domain': target_domain,
                'ref_enrichment': ref_ratio,
                'observed_enrichment': round(observed_ratio, 3),
                'deviation_pct': round(deviation, 1),
                'n_transitions': total_nexts,
            }

        # Per-terminal full enrichment vectors
        terminal_enrichment_vectors = {}
        for term_atom, nexts in term_to_next_head.items():
            total_nexts = sum(nexts.values())
            if total_nexts == 0:
                continue
            vec = {}
            for d in DOMAINS:
                obs_frac = nexts.get(d, 0) / total_nexts
                exp_frac = marginal_domain.get(d, 1.0 / 6)
                vec[d] = round(obs_frac / max(exp_frac, 0.001), 3)
            terminal_enrichment_vectors[term_atom] = vec

        # Marginal terminal distribution
        all_terms = ['h', 'r', 'y', 'n', 'm', 'l', 'bare']
        marginal_terminal = {}
        total_terms = sum(term_counter.values())
        for t in all_terms:
            marginal_terminal[t] = round(
                term_counter.get(t, 0) / max(total_terms, 1), 4)

        # ═══ F. Hazard posture prior ═══
        hazard_counter = Counter(t['hazard_posture'] for t in sec_tokens)
        hazard_prior = dist_from_counter(hazard_counter, HAZARD_POSTURES)

        # ═══ G. Closure class prior ═══
        closure_counter = Counter(t['closure_class'] for t in sec_tokens)
        closure_prior = dist_from_counter(closure_counter, CLOSURE_CLASSES)

        # ═══ H. Headless subtype prior ═══
        hl_subtype_counter = Counter(
            t['headless_subtype_derived'] for t in hl_tokens)
        headless_subtype_prior = dist_from_counter(
            hl_subtype_counter, HEADLESS_SUBTYPES)

        # ═══ Phase-specific domain distributions ═══
        # For E4 phase_adjustment: domain dist per line zone
        phase_domain_dist = {}
        for zone in ['SPEC', 'WORK', 'CLOSE']:
            zone_toks = [t for t in sec_tokens
                         if t.get('line_zone') == zone]
            zone_counter = Counter(t['domain'] for t in zone_toks)
            phase_domain_dist[zone] = dist_from_counter(
                zone_counter, DOMAINS)

        # ═══ Assemble template ═══
        template = {
            'section': sec,
            'n_tokens': n_tokens,
            'n_folios': len(sec_folios),
            'small_section': is_small,
            'domain_priors': {
                'fracs': {d: round(v, 5) for d, v in domain_fracs.items()},
                'covariance': [[round(c, 6) for c in row]
                               for row in domain_cov],
                'n_folio_vectors': len(folio_domain_vecs),
            },
            'paragraph_cloud_prior': {
                'n_qualifying_paragraphs': len(para_cloud_vectors),
                'vectors': [[round(v, 5) for v in vec]
                            for vec in para_cloud_vectors],
                'meta': para_cloud_meta,
                'mean': [round(v, 5) for v in cloud_mean],
                'covariance': [[round(c, 6) for c in row]
                               for row in cloud_cov],
            },
            'line_packet_priors': {
                'per_quintile': {str(q): qdata
                                 for q, qdata in per_quintile.items()},
                'q3q4_head_jsd': round(q3q4_jsd, 5),
                'q2q3_head_jsd': round(q2q3_jsd, 5),
            },
            'headless_ecology': headless_ecology,
            'routing_grammar': {
                'core_enrichments': {
                    k: routing_enrichments[k] for k in CORE_ROUTE
                    if k in routing_enrichments
                },
                'exploratory_enrichments': {
                    k: routing_enrichments[k] for k in EXPLORATORY_ROUTE
                    if k in routing_enrichments
                },
                'terminal_enrichment_vectors': terminal_enrichment_vectors,
                'marginal_terminal_dist': marginal_terminal,
                'marginal_head_dist': {
                    h: round(marginal_head.get(h, 0) /
                             max(sum(marginal_head.values()), 1), 4)
                    for h in ['k', 't', 'a', 'e', 'o']
                },
            },
            'hazard_posture_prior': {
                k: round(v, 5) for k, v in hazard_prior.items()
            },
            'closure_class_prior': {
                k: round(v, 5) for k, v in closure_prior.items()
            },
            'headless_subtype_prior': {
                k: round(v, 5) for k, v in headless_subtype_prior.items()
            },
            'phase_domain_dist': {
                zone: {d: round(v, 5) for d, v in dists.items()}
                for zone, dists in phase_domain_dist.items()
            },
        }

        templates[sec] = template

    # ───────────────────────────────────────────────────────
    # Step 3: Validation
    # ───────────────────────────────────────────────────────
    print("\n=== Validation ===")
    validations = {}
    all_pass = True

    # V1: All 5 sections represented
    v = len(templates) == 5
    validations['all_5_sections'] = {
        'pass': v, 'sections': list(templates.keys())}
    print(f"  All 5 sections: {v} ({list(templates.keys())})")
    if not v:
        all_pass = False

    # V2: Domain fracs sum to ~1.0
    for sec, tmpl in templates.items():
        frac_sum = sum(tmpl['domain_priors']['fracs'].values())
        v = abs(frac_sum - 1.0) < 0.001
        validations[f'{sec}_fracs_sum'] = {
            'pass': v, 'sum': round(frac_sum, 5)}
        if not v:
            all_pass = False
            print(f"  {sec} domain fracs sum: {frac_sum:.5f} -> FAIL")

    # V3: Routing enrichments match C1563 within 5%
    routing_checks = []
    for sec, tmpl in templates.items():
        if tmpl['small_section']:
            continue  # Skip C/T for routing validation
        for term_atom in CORE_ROUTE:
            enr = tmpl['routing_grammar']['core_enrichments'].get(term_atom)
            if enr and enr['deviation_pct'] is not None:
                within_5 = abs(enr['deviation_pct']) <= 5.0
                routing_checks.append({
                    'section': sec, 'terminal': term_atom,
                    'ref': enr['ref_enrichment'],
                    'observed': enr['observed_enrichment'],
                    'deviation_pct': enr['deviation_pct'],
                    'within_5pct': within_5,
                })
                if not within_5:
                    print(f"  WARNING: {sec} routing {term_atom}->"
                          f"{enr['target_domain']}: "
                          f"{enr['observed_enrichment']}x vs "
                          f"{enr['ref_enrichment']}x "
                          f"({enr['deviation_pct']:+.1f}%)")

    # Routing check is WARNING not FAIL (section-level may deviate)
    validations['routing_enrichments'] = routing_checks

    # V4: C/T flagged as small sections
    for sec in ['C', 'T']:
        if sec in templates:
            v = templates[sec]['small_section']
            validations[f'{sec}_small_section'] = {'pass': v}
            if not v:
                all_pass = False
                print(f"  {sec} small_section flag: FAIL")

    # V5: Paragraph cloud counts
    for sec, tmpl in templates.items():
        n_paras = tmpl['paragraph_cloud_prior']['n_qualifying_paragraphs']
        print(f"  {sec} qualifying paragraphs: {n_paras}")

    print(f"\n  Overall validation: {'PASS' if all_pass else 'FAIL'}")

    # ───────────────────────────────────────────────────────
    # Step 4: Summary statistics
    # ───────────────────────────────────────────────────────
    print("\n=== Summary ===")
    for sec in sections:
        tmpl = templates[sec]
        fracs = tmpl['domain_priors']['fracs']
        print(f"\n  Section {sec} ({tmpl['n_tokens']} tokens, "
              f"{tmpl['n_folios']} folios"
              f"{', SMALL' if tmpl['small_section'] else ''}):")
        print(f"    Domain fracs: "
              + " ".join(f"{d[0]}={fracs[d]:.3f}" for d in DOMAINS))
        print(f"    Hazard: "
              + " ".join(f"{k}={v:.3f}"
                         for k, v in tmpl['hazard_posture_prior'].items()))
        print(f"    Closure: "
              + " ".join(f"{k}={v:.3f}"
                         for k, v in tmpl['closure_class_prior'].items()))
        print(f"    HL subtype: "
              + " ".join(f"{k}={v:.3f}"
                         for k, v in tmpl['headless_subtype_prior'].items()))
        print(f"    Q3>Q4 JSD: {tmpl['line_packet_priors']['q3q4_head_jsd']:.4f}"
              f"  Q2>Q3 JSD: {tmpl['line_packet_priors']['q2q3_head_jsd']:.4f}")
        # Routing
        for label, enrs in [('Core', 'core_enrichments'),
                            ('Exploratory', 'exploratory_enrichments')]:
            items = tmpl['routing_grammar'][enrs]
            if items:
                parts = []
                for term, info in items.items():
                    obs = info.get('observed_enrichment')
                    if obs is not None:
                        parts.append(f"{term}->{info['target_domain'][0]}: "
                                     f"{obs:.2f}x")
                print(f"    Routing ({label}): {', '.join(parts)}")

    # ───────────────────────────────────────────────────────
    # Step 5: Save output
    # ───────────────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': '562',
            'task': 'T1_section_template_builder',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'corpus_path': str(corpus_path),
            'n_total_tokens': len(corpus),
        },
        'templates': templates,
        'validations': validations,
        'validation_pass': all_pass,
    }

    out_path = (Path(__file__).parent.parent / 'results' /
                't1_section_templates.json')
    print(f"\n  Writing to {out_path}...")
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    import os
    size_kb = os.path.getsize(out_path) / 1024
    elapsed = time.time() - t0
    print(f"  Size: {size_kb:.1f} KB")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"\n=== T1 Complete (validation: {'PASS' if all_pass else 'FAIL'}) ===")


if __name__ == '__main__':
    main()
