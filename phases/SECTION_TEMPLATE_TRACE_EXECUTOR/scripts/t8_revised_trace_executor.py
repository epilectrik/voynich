"""Phase 562b T8: Revised Token Trace Executor

Re-run T4 token trace executor with exactly TWO changes:
  1. Closure axis: Gaussian LL on continuous CTS (instead of categorical 5-class)
  2. Hazard axis at E3+: paragraph hazard envelope blend

Everything else is IDENTICAL to T4 — domain, routing, headless scoring at all
levels; hazard at E1/E2; all constants, derive functions, utilities.

Input:
  - t1_domain_decomposition.json (corpus)
  - t1_section_templates.json
  - t2_folio_budgets.json
  - t3_line_packets.json
  - t7_closure_cts.json  (NEW: CTS data from T7)

Output: t8_revised_traces.json
"""
import json
import math
import time
from pathlib import Path
from collections import Counter, defaultdict

# ═══════════════════════════════════════════════════════════════
# Constants  (IDENTICAL to T4)
# ═══════════════════════════════════════════════════════════════

DOMAINS = ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY', 'ARRANGEMENT', 'HEADLESS']
DOMAIN_IDX = {d: i for i, d in enumerate(DOMAINS)}

HAZARD_POSTURES = ['IMMUNE', 'ZERO', 'LOW', 'HIGH']
HAZARD_IDX = {h: i for i, h in enumerate(HAZARD_POSTURES)}

CLOSURE_CLASSES = ['SPEC_OPEN', 'WORK_TRANSPARENT', 'WORK_SEMI',
                   'CLOSE_OPAQUE', 'CLOSE_TRANSITIONAL']
CLOSURE_IDX = {c: i for i, c in enumerate(CLOSURE_CLASSES)}

HEADLESS_SUBTYPES = ['PSEUDO_D', 'PSEUDO_I', 'PSEUDO_L',
                     'PARAMETRIC_CPF', 'OTHER_HEADLESS']
HL_IDX = {h: i for i, h in enumerate(HEADLESS_SUBTYPES)}

# Routing (C1563)
CORE_ROUTE = {'r': 'ACTIVE', 'y': 'THERMAL', 'h': 'FLOW', 'm': 'ARRANGEMENT'}
EXPLORATORY_ROUTE = {'n': 'ACTIVE', 'l': 'STABILITY'}
PRIMARY_ROUTE = {**CORE_ROUTE, **EXPLORATORY_ROUTE, 'bare': 'NEUTRAL'}

ROUTING_TARGETS = ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY',
                   'ARRANGEMENT', 'NEUTRAL']
ROUTE_IDX = {r: i for i, r in enumerate(ROUTING_TARGETS)}

ALPHA = 0.01  # Laplace smoothing

# Closure phase mask DISABLED (same as T4)
CLOSURE_PHASE_MASK = None

# Routing enrichment factors
ROUTING_BOOST = {
    'r': ('ACTIVE', 2.231),
    'y': ('THERMAL', 1.597),
    'h': ('FLOW', 1.892),
    'm': ('ARRANGEMENT', 1.554),
    'n': ('ACTIVE', 1.424),
    'l': ('STABILITY', 1.246),
}

# Axis weights for composite LL
AXIS_WEIGHTS = {
    'domain': 1.0,
    'hazard': 0.5,
    'routing': 0.5,
    'closure': 0.5,
    'headless': 0.5,
}

DIAG_PER_SECTION = 100

# Hazard envelope types (for E3 paragraph blend)
HAZARD_ENVELOPE_TYPES = ['SAFE_OPEN', 'THERMAL_INTERIOR', 'DANGEROUS_CLOSE']


# ═══════════════════════════════════════════════════════════════
# Derived evaluation targets  (IDENTICAL to T4)
# ═══════════════════════════════════════════════════════════════

def derive_hazard_posture(token):
    if token.get('head') == 'k':
        return 'IMMUNE'
    if token.get('head') == 'e' and token.get('term') == 'y':
        return 'ZERO'
    if token.get('head') == 'a' and (token.get('i_count') or 0) >= 2:
        return 'ZERO'
    if token.get('has_quenching_mod') and token.get('head') in ('e', 'o', 't'):
        return 'ZERO'
    if token.get('is_safe_pathway'):
        return 'ZERO'
    if token.get('head') == 'a' and token.get('term') in ('l', 'r'):
        return 'HIGH'
    if not token.get('source_immune') and token.get('frame_hazard') == 'HIGH':
        return 'HIGH'
    return 'LOW'


def derive_closure_class(token):
    """Still needed for diagnostic traces."""
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
    term = token.get('term')
    if term is None:
        return 'NEUTRAL'
    return PRIMARY_ROUTE.get(term, 'NEUTRAL')


# ═══════════════════════════════════════════════════════════════
# Utility  (IDENTICAL to T4)
# ═══════════════════════════════════════════════════════════════

def normalize(d, categories, alpha=ALPHA):
    """Normalize dict of categories with Laplace smoothing."""
    total = sum(d.get(c, 0) for c in categories) + alpha * len(categories)
    return {c: (d.get(c, 0) + alpha) / total for c in categories}


def smooth_dist(dist, categories, alpha=ALPHA):
    """Apply Laplace smoothing to an existing distribution."""
    total = sum(dist.get(c, 0) for c in categories) + alpha * len(categories)
    return {c: (dist.get(c, 0) + alpha) / total for c in categories}


def log_prob(prior, actual, categories):
    """Log probability of actual under prior (smoothed)."""
    p = prior.get(actual, ALPHA / len(categories))
    if p <= 0:
        p = 1e-10
    return math.log(p)


def euclidean(v1, v2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


def vec_mean(vectors):
    if not vectors:
        return [0.0] * 6
    n = len(vectors)
    result = [0.0] * 6
    for v in vectors:
        for i in range(6):
            result[i] += v[i]
    return [x / n for x in result]


def build_routing_mask(prev_term):
    """Build domain routing mask from previous terminal."""
    mask = {d: 1.0 for d in DOMAINS}
    if prev_term and prev_term in ROUTING_BOOST:
        target_domain, boost_factor = ROUTING_BOOST[prev_term]
        for d in DOMAINS:
            if d == target_domain:
                mask[d] = boost_factor
            elif d == 'HEADLESS':
                mask[d] = 1.0
            else:
                mask[d] = max(0.5, 1.0 / boost_factor)
    return mask


def adjust_hazard_by_envelope(hazard_dist, envelope):
    """Adjust hazard distribution based on line hazard envelope."""
    adj = dict(hazard_dist)
    if envelope == 'SAFE_OPEN':
        adj['IMMUNE'] = adj.get('IMMUNE', 0) * 1.5
        adj['ZERO'] = adj.get('ZERO', 0) * 1.5
        adj['HIGH'] = adj.get('HIGH', 0) * 0.2
    elif envelope == 'DANGEROUS_CLOSE':
        adj['HIGH'] = adj.get('HIGH', 0) * 2.0
        adj['IMMUNE'] = adj.get('IMMUNE', 0) * 0.5
    # THERMAL_INTERIOR: no adjustment (default)
    return normalize(adj, HAZARD_POSTURES)


# ═══════════════════════════════════════════════════════════════
# NEW: Gaussian LL for CTS closure axis
# ═══════════════════════════════════════════════════════════════

def gaussian_ll(x, mu, sigma):
    """Gaussian log-likelihood of x under N(mu, sigma).

    Returns log p(x | mu, sigma) for a normal distribution.
    """
    return -0.5 * math.log(2 * math.pi) - math.log(sigma) - 0.5 * ((x - mu) / sigma) ** 2


# ═══════════════════════════════════════════════════════════════
# NEW: Paragraph-blended hazard envelope adjustment
# ═══════════════════════════════════════════════════════════════

def weighted_hazard_adjustment(base_hazard, folio_env_dist, para_env_dist,
                               blend_weight=0.3):
    """Probability-weighted mixture of envelope adjustments using paragraph blend.

    Creates a blended envelope distribution (folio + paragraph), then applies
    a probability-weighted mixture of what adjust_hazard_by_envelope would
    produce under each possible envelope.
    """
    blended_env = {}
    for env in HAZARD_ENVELOPE_TYPES:
        blended_env[env] = ((1 - blend_weight) * folio_env_dist.get(env, 0.333) +
                            blend_weight * para_env_dist.get(env, 0.333))

    result = {h: 0.0 for h in HAZARD_POSTURES}
    for env, env_prob in blended_env.items():
        adj = adjust_hazard_by_envelope(dict(base_hazard), env)
        for h in HAZARD_POSTURES:
            result[h] += env_prob * adj[h]

    return normalize(result, HAZARD_POSTURES)


# ═══════════════════════════════════════════════════════════════
# Helper functions for prior construction  (IDENTICAL to T4)
# ═══════════════════════════════════════════════════════════════

def _build_section_routing_prior(tmpl):
    """Build routing target prior from section terminal distribution."""
    term_dist = tmpl['routing_grammar'].get('marginal_terminal_dist', {})
    routing_counts = defaultdict(float)
    for term, frac in term_dist.items():
        target = PRIMARY_ROUTE.get(term, 'NEUTRAL')
        routing_counts[target] += frac
    return smooth_dist(dict(routing_counts), ROUTING_TARGETS)


def _build_folio_routing_prior(budget):
    """Build routing target prior from folio terminal distribution."""
    term_dist = budget.get('terminal_dist', {})
    routing_counts = defaultdict(float)
    for term, frac in term_dist.items():
        target = PRIMARY_ROUTE.get(term, 'NEUTRAL')
        routing_counts[target] += frac
    return smooth_dist(dict(routing_counts), ROUTING_TARGETS)


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    print("=== Phase 562b T8: Revised Token Trace Executor ===")
    print("  Changes from T4: (1) CTS Gaussian LL for closure, "
          "(2) paragraph hazard envelope blend at E3+")

    base = Path(__file__).resolve().parents[2]
    corpus_path = (base / 'WITHIN_DOMAIN_COMPOSITIONAL_CONTROL' /
                   'results' / 't1_domain_decomposition.json')
    tmpl_path = (base / 'SECTION_TEMPLATE_TRACE_EXECUTOR' /
                 'results' / 't1_section_templates.json')
    budget_path = (base / 'SECTION_TEMPLATE_TRACE_EXECUTOR' /
                   'results' / 't2_folio_budgets.json')
    packet_path = (base / 'SECTION_TEMPLATE_TRACE_EXECUTOR' /
                   'results' / 't3_line_packets.json')
    cts_path = (base / 'SECTION_TEMPLATE_TRACE_EXECUTOR' /
                'results' / 't7_closure_cts.json')

    # ───────────────────────────────────────────────────
    # Load all inputs
    # ───────────────────────────────────────────────────
    print("  Loading inputs...")
    with open(corpus_path) as f:
        corpus = json.load(f)['corpus_tokens']
    print(f"    Corpus: {len(corpus)} tokens")

    with open(tmpl_path) as f:
        templates_data = json.load(f)['templates']
    print(f"    Templates: {list(templates_data.keys())}")

    with open(budget_path) as f:
        budgets_data = json.load(f)['folio_budgets']
    print(f"    Budgets: {len(budgets_data)} folios")

    with open(packet_path) as f:
        packets_data = json.load(f)
    line_packets = packets_data['line_packets']
    print(f"    Line packets: {len(line_packets)}")

    with open(cts_path) as f:
        cts_data = json.load(f)
    print(f"    CTS data: {len(cts_data['line_cts'])} lines, "
          f"{len(cts_data['section_cts_dist'])} sections, "
          f"{len(cts_data['folio_cts_dist'])} folios, "
          f"{len(cts_data['paragraph_cts_dist'])} paragraphs")

    # ───────────────────────────────────────────────────
    # Build O(1) lookup structures  (IDENTICAL to T4)
    # ───────────────────────────────────────────────────
    print("  Building lookup structures...")

    # Section templates (smoothed priors)
    section_priors = {}
    for sec, tmpl in templates_data.items():
        section_priors[sec] = {
            'domain': smooth_dist(tmpl['domain_priors']['fracs'], DOMAINS),
            'hazard': smooth_dist(tmpl['hazard_posture_prior'], HAZARD_POSTURES),
            'closure': smooth_dist(tmpl['closure_class_prior'], CLOSURE_CLASSES),
            'headless': smooth_dist(tmpl['headless_subtype_prior'],
                                    HEADLESS_SUBTYPES),
            'routing': _build_section_routing_prior(tmpl),
            'phase_domain': tmpl.get('phase_domain_dist', {}),
        }

    # Folio budgets (smoothed priors)
    folio_priors = {}
    for fol, budget in budgets_data.items():
        folio_priors[fol] = {
            'domain': smooth_dist(budget['domain_budget']['fracs'], DOMAINS),
            'hazard': smooth_dist(budget['hazard_posture_dist'], HAZARD_POSTURES),
            'closure': smooth_dist(budget['closure_class_dist'], CLOSURE_CLASSES),
            'headless': smooth_dist(budget['headless_regime']['subtype_dist'],
                                    HEADLESS_SUBTYPES),
            'routing': _build_folio_routing_prior(budget),
            'terminal_dist': budget.get('terminal_dist', {}),
            'section': budget['section'],
        }

    # Folio -> section mapping
    folio_to_section = {fol: b['section'] for fol, b in budgets_data.items()}

    # Paragraph clouds per folio: folio -> {paragraph_idx: domain_vec}
    para_clouds = {}
    for fol, budget in budgets_data.items():
        pc = budget['paragraph_cloud']
        paras = pc.get('paragraphs', [])
        cloud = {}
        for p in paras:
            cloud[p['paragraph_idx']] = p['domain_vec']
        para_clouds[fol] = cloud

    # Line packet states: "folio|line" -> packet_state
    packet_states = {}
    for key, lp in line_packets.items():
        packet_states[key] = lp['packet_state']

    # ───────────────────────────────────────────────────
    # NEW: CTS lookup structures
    # ───────────────────────────────────────────────────
    print("  Building CTS lookup structures...")

    # Line CTS values: "folio|line" -> float
    line_cts_values = {}
    for key, val in cts_data['line_cts'].items():
        line_cts_values[key] = val['cts']

    # Section CTS distributions
    section_cts = cts_data['section_cts_dist']  # sec -> {mean, std, n}

    # Folio CTS distributions
    folio_cts = cts_data['folio_cts_dist']  # fol -> {mean, std, n}

    # Paragraph CTS distributions
    paragraph_cts = cts_data['paragraph_cts_dist']
    # para_key -> {mean, std, n_lines, loo_means: {line_num: float}}

    # Folio hazard envelope distributions
    folio_hazard_env = cts_data['folio_hazard_envelope_dist']
    # fol -> {SAFE_OPEN: float, THERMAL_INTERIOR: float, DANGEROUS_CLOSE: float}

    # Paragraph hazard envelope distributions
    paragraph_hazard_env = cts_data['paragraph_hazard_envelope_dist']
    # para_key -> {SAFE_OPEN: float, ...}

    # ───────────────────────────────────────────────────
    # Pre-compute E4 closure delta: per-section, per-phase mean CTS
    # ───────────────────────────────────────────────────
    print("  Pre-computing E4 phase CTS deltas...")

    # Accumulate CTS by (section, packet_phase)
    phase_cts_accum = defaultdict(list)  # (section, phase) -> [cts values]
    for key, cts_val in line_cts_values.items():
        fol = key.split('|')[0]
        sec = folio_to_section.get(fol)
        if sec is None:
            continue
        pstate = packet_states.get(key)
        phase = pstate['packet_phase'] if pstate else 'WORK'
        phase_cts_accum[(sec, phase)].append(cts_val)

    section_phase_mean_cts = {}
    for (sec, phase), vals in phase_cts_accum.items():
        section_phase_mean_cts[(sec, phase)] = sum(vals) / len(vals)

    print(f"    Phase CTS deltas computed for "
          f"{len(section_phase_mean_cts)} (section, phase) pairs")
    for (sec, phase), mean_val in sorted(section_phase_mean_cts.items()):
        sec_mean = section_cts[sec]['mean']
        delta = mean_val - sec_mean
        print(f"      {sec}/{phase}: mean_cts={mean_val:.4f}, "
              f"sec_mean={sec_mean:.4f}, delta={delta:+.4f}")

    # ───────────────────────────────────────────────────
    # Pre-compute per-line closure LL for all 4 modes
    # ───────────────────────────────────────────────────
    print("  Pre-computing per-line closure LL...")

    # All tokens on the same line share the same CTS and therefore
    # the same closure LL at each mode level.
    line_closure_ll = {}  # line_key -> {'E1': float, 'E2': float, ...}

    # Collect all unique line keys from the corpus
    all_line_keys = set()
    for tok in corpus:
        lk = f"{tok['folio']}|{tok['line']}"
        all_line_keys.add(lk)

    n_with_cts = 0
    n_missing_cts = 0

    for lk in all_line_keys:
        if lk not in line_cts_values:
            # No CTS data for this line — use a default penalty
            line_closure_ll[lk] = {'E1': -3.0, 'E2': -3.0,
                                   'E3': -3.0, 'E4': -3.0}
            n_missing_cts += 1
            continue

        n_with_cts += 1
        actual_cts = line_cts_values[lk]
        fol = lk.split('|')[0]
        line_num = lk.split('|')[1]
        sec = folio_to_section.get(fol, 'S')

        # E1: section-level CTS distribution
        sec_dist = section_cts.get(sec, {'mean': 0.3, 'std': 0.2})
        sec_mean = sec_dist['mean']
        sec_std = max(sec_dist['std'], 0.05)  # safety floor
        e1_cl = gaussian_ll(actual_cts, sec_mean, sec_std)

        # E2: folio-level CTS distribution
        fol_dist = folio_cts.get(fol, sec_dist)
        fol_mean = fol_dist['mean']
        fol_std = max(fol_dist['std'], 0.05)
        e2_cl = gaussian_ll(actual_cts, fol_mean, fol_std)

        # E3: paragraph LOO mean (fall back to E2)
        # Find paragraph key for this line
        # We need folio + paragraph_idx; we'll fill this below via token lookup
        # For now, store folio/line info for deferred computation
        e3_cl = e2_cl  # default fallback
        e3_cts_mu = fol_mean
        e3_cts_sigma = fol_std

        # Check all paragraph CTS entries for this folio to find one
        # containing this line number in its loo_means
        para_key_found = None
        para_loo_mean = None
        para_std = None
        for pk, pd in paragraph_cts.items():
            if pk.startswith(fol + '|'):
                if line_num in pd.get('loo_means', {}):
                    para_key_found = pk
                    para_loo_mean = pd['loo_means'][line_num]
                    para_std = max(pd['std'], 0.05)
                    break

        if para_loo_mean is not None:
            e3_cl = gaussian_ll(actual_cts, para_loo_mean, para_std)
            e3_cts_mu = para_loo_mean
            e3_cts_sigma = para_std

        # E4: E3 base + phase delta
        pstate = packet_states.get(lk)
        phase = pstate['packet_phase'] if pstate else 'WORK'
        sec_phase_mean = section_phase_mean_cts.get(
            (sec, phase), sec_mean)
        delta = sec_phase_mean - sec_mean  # how much this phase deviates
        # Clamp delta to +/- 0.5 * folio_std
        delta = max(-0.5 * fol_std, min(delta, 0.5 * fol_std))

        e4_cts_mu = e3_cts_mu + delta
        e4_cts_sigma = e3_cts_sigma
        e4_cl = gaussian_ll(actual_cts, e4_cts_mu, e4_cts_sigma)

        line_closure_ll[lk] = {
            'E1': e1_cl, 'E2': e2_cl, 'E3': e3_cl, 'E4': e4_cl,
        }

    print(f"    Lines with CTS: {n_with_cts}, missing: {n_missing_cts}")

    # ───────────────────────────────────────────────────
    # Pre-compute E3 hazard: paragraph-blended envelope
    # ───────────────────────────────────────────────────
    print("  Pre-computing E3 paragraph hazard blend...")

    # For each (folio, paragraph_idx), pre-compute the blended hazard
    # adjustment if paragraph hazard envelope data is available.
    # We need to know the folio's hazard prior (e2_hazard) at compute time,
    # so we store the paragraph and folio envelope distributions for
    # on-the-fly computation during the main loop.
    # (Already loaded above as paragraph_hazard_env and folio_hazard_env)

    n_para_haz = sum(1 for k in paragraph_hazard_env if k)
    print(f"    Paragraph hazard envelopes available: {n_para_haz}")

    # ───────────────────────────────────────────────────
    # Derive evaluation targets for ALL tokens  (IDENTICAL to T4)
    # ───────────────────────────────────────────────────
    print("  Deriving evaluation targets...")
    for tok in corpus:
        tok['hazard_posture'] = derive_hazard_posture(tok)
        tok['routing_target'] = derive_routing_target(tok)
        tok['closure_class'] = derive_closure_class(tok)
        tok['hl_subtype'] = derive_headless_subtype(tok)

    # ───────────────────────────────────────────────────
    # Pre-compute E3 leave-one-out paragraph priors  (IDENTICAL to T4)
    # ───────────────────────────────────────────────────
    print("  Pre-computing E3 leave-one-out paragraph priors...")
    e3_para_priors = {}  # (folio, para_idx) -> 6D domain prior

    for fol, cloud in para_clouds.items():
        if not cloud:
            continue
        para_indices = sorted(cloud.keys())
        para_vecs = {pi: cloud[pi] for pi in para_indices}

        for pi in para_indices:
            p_vec = para_vecs[pi]
            other_vecs = [para_vecs[pj] for pj in para_indices if pj != pi]

            if len(other_vecs) >= 3:
                k = min(3, len(other_vecs))
                dists = [euclidean(p_vec, v) for v in other_vecs]
                indexed = sorted(range(len(dists)), key=lambda i: dists[i])
                nn_vecs = [other_vecs[i] for i in indexed[:k]]
                nn_centroid = vec_mean(nn_vecs)
                folio_centroid = vec_mean(other_vecs)
                blended = [0.7 * nn_centroid[i] + 0.3 * folio_centroid[i]
                           for i in range(6)]
            elif len(other_vecs) >= 1:
                blended = vec_mean(other_vecs)
            else:
                fd = folio_priors.get(fol, {}).get('domain', {})
                blended = [fd.get(d, 1.0 / 6) for d in DOMAINS]

            prior = {DOMAINS[i]: blended[i] for i in range(6)}
            e3_para_priors[(fol, pi)] = smooth_dist(prior, DOMAINS)

    print(f"    E3 priors computed for {len(e3_para_priors)} paragraphs")

    # ───────────────────────────────────────────────────
    # MAIN TRACE EXECUTION: Single pass through all tokens
    # ───────────────────────────────────────────────────
    print("  Executing trace across all tokens...")

    n = len(corpus)
    axis_names = ['domain', 'hazard', 'routing', 'closure', 'headless']
    modes = ['E1', 'E2', 'E3', 'E4']

    # Flat arrays for per-token LLs
    composite_ll = {m: [0.0] * n for m in modes}
    axis_ll = {ax: {m: [0.0] * n for m in modes} for ax in axis_names}

    # Counters
    coverage = {
        'total': n,
        'with_para_cloud': 0,
        'with_line_packet': 0,
        'headless_tokens': 0,
        'with_para_hazard_env': 0,
        'with_line_cts': 0,
    }

    # Diagnostic traces
    diag_traces = []
    diag_counts = Counter()

    for idx, tok in enumerate(corpus):
        fol = tok['folio']
        sec = folio_to_section.get(fol, tok.get('section', 'S'))
        pi = tok['paragraph_idx']
        line_key = f"{fol}|{tok['line']}"
        para_key = f"{fol}|{pi}"

        # Evaluation targets
        actual_domain = tok['domain']
        actual_hazard = tok['hazard_posture']
        actual_routing = tok['routing_target']
        actual_closure = tok['closure_class']
        actual_hl = tok['hl_subtype']
        is_headless = actual_hl != 'HEADED'

        if is_headless:
            coverage['headless_tokens'] += 1

        has_cloud = (fol, pi) in e3_para_priors
        has_packet = line_key in packet_states
        has_para_haz = para_key in paragraph_hazard_env
        has_cts = line_key in line_cts_values

        if has_cloud:
            coverage['with_para_cloud'] += 1
        if has_packet:
            coverage['with_line_packet'] += 1
        if has_para_haz:
            coverage['with_para_hazard_env'] += 1
        if has_cts:
            coverage['with_line_cts'] += 1

        # ─── E1: Section only  (IDENTICAL to T4) ───
        sp = section_priors.get(sec, section_priors['S'])
        e1_domain = sp['domain']
        e1_hazard = sp['hazard']
        e1_routing = sp['routing']
        e1_headless = sp['headless']

        # ─── E2: + folio budget  (IDENTICAL to T4) ───
        fp = folio_priors.get(fol, sp)
        e2_domain = fp['domain']
        e2_hazard = fp['hazard']
        e2_routing = fp['routing']
        e2_headless = fp['headless']

        # ─── E3: + paragraph cloud  (domain IDENTICAL to T4) ───
        if has_cloud:
            e3_domain = e2_domain
        else:
            e3_domain = e2_domain

        e3_routing = e2_routing
        e3_headless = e2_headless

        # CHANGED: E3 hazard — paragraph envelope blend
        if has_para_haz and fol in folio_hazard_env:
            fol_env = folio_hazard_env[fol]
            para_env = paragraph_hazard_env[para_key]
            e3_hazard = weighted_hazard_adjustment(
                e2_hazard, fol_env, para_env, blend_weight=0.3)
        else:
            e3_hazard = e2_hazard

        # ─── E4: + line packet state + routing + headless regime ───
        # (domain, routing, headless IDENTICAL to T4)
        prev_term = tok.get('prev_term_same_line')
        pstate = packet_states.get(line_key)
        phase = pstate['packet_phase'] if pstate else 'WORK'
        hazard_env = pstate['hazard_envelope'] if pstate else 'THERMAL_INTERIOR'

        # Domain: E3 domain * dampened phase adjustment * routing mask
        phase_domain = section_priors.get(sec, sp).get(
            'phase_domain', {}).get(phase, {})
        if phase_domain:
            phase_adj = {}
            for d in DOMAINS:
                sec_d = sp['domain'].get(d, 1.0 / 6)
                ph_d = phase_domain.get(d, sec_d)
                raw_adj = ph_d / max(sec_d, 0.001)
                phase_adj[d] = math.sqrt(raw_adj) if raw_adj > 0 else 0.01
        else:
            phase_adj = {d: 1.0 for d in DOMAINS}

        routing_mask = build_routing_mask(prev_term)

        e4_domain_raw = {}
        for d in DOMAINS:
            e4_domain_raw[d] = (e3_domain.get(d, ALPHA) *
                                phase_adj.get(d, 1.0) *
                                routing_mask.get(d, 1.0))
        e4_domain = normalize(e4_domain_raw, DOMAINS)

        # Hazard E4: UNCHANGED from T4 — uses actual line envelope
        e4_hazard = adjust_hazard_by_envelope(e2_hazard, hazard_env)

        # Routing: folio terminal dist modulated by phase (same as T4)
        e4_routing = e2_routing

        # Headless: folio-level regime (same as T4)
        e4_headless = e2_headless

        # ─── Score all modes across all axes ───
        # Non-closure priors
        priors = {
            'E1': {'domain': e1_domain, 'hazard': e1_hazard,
                   'routing': e1_routing, 'headless': e1_headless},
            'E2': {'domain': e2_domain, 'hazard': e2_hazard,
                   'routing': e2_routing, 'headless': e2_headless},
            'E3': {'domain': e3_domain, 'hazard': e3_hazard,
                   'routing': e3_routing, 'headless': e3_headless},
            'E4': {'domain': e4_domain, 'hazard': e4_hazard,
                   'routing': e4_routing, 'headless': e4_headless},
        }

        # Look up pre-computed closure LL for this line
        cl_ll = line_closure_ll.get(line_key,
                                    {'E1': -3.0, 'E2': -3.0,
                                     'E3': -3.0, 'E4': -3.0})

        for mode in modes:
            mp = priors[mode]
            ll_d = log_prob(mp['domain'], actual_domain, DOMAINS)
            ll_h = log_prob(mp['hazard'], actual_hazard, HAZARD_POSTURES)
            ll_r = log_prob(mp['routing'], actual_routing, ROUTING_TARGETS)

            # CHANGED: closure LL is now Gaussian on CTS (pre-computed per line)
            ll_c = cl_ll[mode]

            axis_ll['domain'][mode][idx] = ll_d
            axis_ll['hazard'][mode][idx] = ll_h
            axis_ll['routing'][mode][idx] = ll_r
            axis_ll['closure'][mode][idx] = ll_c

            comp = (AXIS_WEIGHTS['domain'] * ll_d +
                    AXIS_WEIGHTS['hazard'] * ll_h +
                    AXIS_WEIGHTS['routing'] * ll_r +
                    AXIS_WEIGHTS['closure'] * ll_c)

            if is_headless:
                ll_hl = log_prob(mp['headless'], actual_hl, HEADLESS_SUBTYPES)
                axis_ll['headless'][mode][idx] = ll_hl
                comp += AXIS_WEIGHTS['headless'] * ll_hl
            else:
                axis_ll['headless'][mode][idx] = 0.0

            composite_ll[mode][idx] = comp

        # Diagnostic trace
        if diag_counts[sec] < DIAG_PER_SECTION:
            diag_counts[sec] += 1
            diag_traces.append({
                'word': tok['word'],
                'folio': fol,
                'section': sec,
                'paragraph_idx': pi,
                'line': tok['line'],
                'quintile': tok.get('quintile'),
                'eval_targets': {
                    'domain': actual_domain,
                    'hazard_posture': actual_hazard,
                    'routing_target': actual_routing,
                    'closure_class': actual_closure,
                    'headless_subtype': actual_hl,
                },
                'cts': {
                    'actual_cts': line_cts_values.get(line_key),
                    'has_para_cts': para_key in paragraph_cts,
                    'has_para_haz': has_para_haz,
                    'line_phase': phase,
                },
                'LL': {
                    mode: {
                        'domain': round(axis_ll['domain'][mode][idx], 4),
                        'hazard': round(axis_ll['hazard'][mode][idx], 4),
                        'routing': round(axis_ll['routing'][mode][idx], 4),
                        'closure': round(axis_ll['closure'][mode][idx], 4),
                        'headless': round(axis_ll['headless'][mode][idx], 4),
                        'composite': round(composite_ll[mode][idx], 4),
                    } for mode in modes
                },
                'context': {
                    'line_packet_phase': phase,
                    'hazard_envelope': hazard_env,
                    'prev_term': prev_term,
                    'has_cloud': has_cloud,
                    'has_packet': has_packet,
                },
            })

    print(f"  Trace complete: {n} tokens")

    # ───────────────────────────────────────────────────
    # Compute summary statistics  (IDENTICAL to T4 structure)
    # ───────────────────────────────────────────────────
    print("  Computing summary statistics...")

    def mean_ll(arr):
        return sum(arr) / len(arr) if arr else 0.0

    # Global means
    mean_composite = {m: mean_ll(composite_ll[m]) for m in modes}
    mean_axis = {
        ax: {m: mean_ll(axis_ll[ax][m]) for m in modes}
        for ax in axis_names
    }

    # Headless-only means for headless axis
    hl_indices = [i for i, t in enumerate(corpus)
                  if t.get('domain') == 'HEADLESS']
    if hl_indices:
        mean_axis['headless'] = {
            m: sum(axis_ll['headless'][m][i] for i in hl_indices) / len(hl_indices)
            for m in modes
        }

    # Per-section means
    per_section = {}
    section_indices = defaultdict(list)
    for i, t in enumerate(corpus):
        sec = folio_to_section.get(t['folio'], t.get('section', 'S'))
        section_indices[sec].append(i)

    for sec, indices in section_indices.items():
        sec_composite = {
            m: sum(composite_ll[m][i] for i in indices) / len(indices)
            for m in modes
        }
        sec_axis = {
            ax: {m: sum(axis_ll[ax][m][i] for i in indices) / len(indices)
                 for m in modes}
            for ax in axis_names
        }
        sec_hl = [i for i in indices if corpus[i].get('domain') == 'HEADLESS']
        if sec_hl:
            sec_axis['headless'] = {
                m: sum(axis_ll['headless'][m][i] for i in sec_hl) / len(sec_hl)
                for m in modes
            }
        per_section[sec] = {
            'n_tokens': len(indices),
            'n_headless': len(sec_hl),
            'mean_composite_LL': {m: round(v, 5) for m, v in sec_composite.items()},
            'mean_axis_LL': {
                ax: {m: round(v, 5) for m, v in axd.items()}
                for ax, axd in sec_axis.items()
            },
        }

    # Monotonic improvement check
    global_monotonic = (mean_composite['E4'] >= mean_composite['E3'] >=
                        mean_composite['E2'] > mean_composite['E1'])
    section_e4_gt_e1 = {}
    for sec, data in per_section.items():
        sc = data['mean_composite_LL']
        section_e4_gt_e1[sec] = sc['E4'] > sc['E1']

    # ───────────────────────────────────────────────────
    # Print summary
    # ───────────────────────────────────────────────────
    print("\n=== Summary ===")
    print(f"  Global mean composite LL:")
    for m in modes:
        print(f"    {m}: {mean_composite[m]:.5f}")
    print(f"  Monotonic (E4>=E3>=E2>E1): {global_monotonic}")
    print(f"  Section E4>E1: {section_e4_gt_e1}")

    print(f"\n  Per-axis means:")
    for ax in axis_names:
        vals = [f"{m}={mean_axis[ax][m]:.4f}" for m in modes]
        print(f"    {ax}: {', '.join(vals)}")

    print(f"\n  Coverage:")
    for k, v in coverage.items():
        print(f"    {k}: {v}")

    print(f"\n  Per-section composite LL:")
    for sec in sorted(per_section.keys()):
        d = per_section[sec]['mean_composite_LL']
        print(f"    {sec} (n={per_section[sec]['n_tokens']}): "
              + " ".join(f"{m}={d[m]:.4f}" for m in modes))

    # ───────────────────────────────────────────────────
    # Validation
    # ───────────────────────────────────────────────────
    print("\n=== Validation ===")
    validations = {}
    all_pass = True

    # V1: All tokens traced
    v = n == len(corpus)
    validations['all_traced'] = {'pass': v, 'n': n}
    print(f"  All {n} tokens traced: {'PASS' if v else 'FAIL'}")
    if not v:
        all_pass = False

    # V2: Global monotonic
    validations['global_monotonic'] = {
        'pass': global_monotonic,
        'values': {m: round(mean_composite[m], 5) for m in modes},
    }
    print(f"  Global monotonic E4>=E3>=E2>E1: "
          f"{'PASS' if global_monotonic else 'FAIL'}")
    if not global_monotonic:
        all_pass = False

    # V3: No NaN or -inf
    has_bad = False
    for m in modes:
        for i in range(n):
            v = composite_ll[m][i]
            if math.isnan(v) or math.isinf(v):
                has_bad = True
                break
    validations['no_nan_inf'] = {'pass': not has_bad}
    print(f"  No NaN/-inf: {'PASS' if not has_bad else 'FAIL'}")
    if has_bad:
        all_pass = False

    # V4: Coverage
    cloud_pct = coverage['with_para_cloud'] / n * 100
    packet_pct = coverage['with_line_packet'] / n * 100
    cts_pct = coverage['with_line_cts'] / n * 100
    v_cloud = cloud_pct > 50
    v_packet = packet_pct > 85
    v_cts = cts_pct > 85
    validations['coverage'] = {
        'cloud_pct': round(cloud_pct, 1),
        'packet_pct': round(packet_pct, 1),
        'cts_pct': round(cts_pct, 1),
        'cloud_pass': v_cloud,
        'packet_pass': v_packet,
        'cts_pass': v_cts,
    }
    print(f"  Para cloud coverage: {cloud_pct:.1f}% "
          f"(>50%: {'PASS' if v_cloud else 'FAIL'})")
    print(f"  Line packet coverage: {packet_pct:.1f}% "
          f"(>85%: {'PASS' if v_packet else 'FAIL'})")
    print(f"  CTS coverage: {cts_pct:.1f}% "
          f"(>85%: {'PASS' if v_cts else 'FAIL'})")
    if not v_cloud or not v_packet or not v_cts:
        all_pass = False

    # V5: Closure axis improvement (E2 > E1 expected from folio specificity)
    cl_e1 = mean_axis['closure']['E1']
    cl_e2 = mean_axis['closure']['E2']
    cl_improves = cl_e2 > cl_e1
    validations['closure_e2_gt_e1'] = {
        'pass': cl_improves,
        'E1': round(cl_e1, 5),
        'E2': round(cl_e2, 5),
    }
    print(f"  Closure E2>E1: {'PASS' if cl_improves else 'FAIL'} "
          f"(E1={cl_e1:.4f}, E2={cl_e2:.4f})")

    print(f"\n  Overall validation: {'PASS' if all_pass else 'FAIL'}")

    # ───────────────────────────────────────────────────
    # Save output
    # ───────────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': '562b',
            'task': 'T8_revised_trace_executor',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_tokens': n,
            'axis_weights': AXIS_WEIGHTS,
            'alpha': ALPHA,
            'changes_from_t4': [
                'closure: Gaussian LL on continuous CTS (was categorical 5-class)',
                'hazard E3: paragraph envelope blend 0.3 weight',
            ],
        },
        'summary': {
            'mean_composite_LL': {m: round(v, 6) for m, v in mean_composite.items()},
            'mean_axis_LL': {
                ax: {m: round(v, 6) for m, v in axd.items()}
                for ax, axd in mean_axis.items()
            },
            'per_section': per_section,
            'monotonic_improvement': {
                'global': global_monotonic,
                'per_section': section_e4_gt_e1,
            },
            'coverage': coverage,
        },
        'per_token_composite_LL': {
            m: [round(v, 5) for v in composite_ll[m]] for m in modes
        },
        'per_token_axis_LL': {
            ax: {m: [round(v, 5) for v in axis_ll[ax][m]] for m in modes}
            for ax in axis_names
        },
        'diagnostic_traces': diag_traces,
        'validations': validations,
        'validation_pass': all_pass,
    }

    out_path = (Path(__file__).parent.parent / 'results' /
                't8_revised_traces.json')
    print(f"\n  Writing to {out_path}...")
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    import os
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    elapsed = time.time() - t0
    print(f"  Size: {size_mb:.1f} MB")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"\n=== T8 Complete (validation: "
          f"{'PASS' if all_pass else 'FAIL'}) ===")


if __name__ == '__main__':
    main()
