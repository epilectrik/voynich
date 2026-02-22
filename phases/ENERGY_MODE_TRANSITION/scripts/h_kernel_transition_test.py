"""
ENERGY_MODE_TRANSITION_MECHANISM: H-Kernel Mediation Test
==========================================================
Phase 426 -- Tests whether h-kernel (monitoring) tokens mediate
energy mode transitions (k->e, e->k) within Currier B lines.

Hypothesis: Monitoring tokens detect conditions (rolling boil,
odd smell) and trigger switching between energy modes. The h-kernel
character encodes this monitoring function (C1154).

Context:
  - C1200: k/e carryover within lines (z=7.90)
  - C1154: h-kernel = monitoring, section-determined or program-specific
  - C929: ch = active testing, sh = passive monitoring
  - C908: H-enriched MIDDLEs: opch (1.55x), sh (1.42x), ch (1.41x), pch (1.36x)
  - C1174: LINK is morphological artifact (dead category)
  - C896: HIGH_H (h>35%) = distillation-class, HIGH_K_LOW_H = boiling-class

Tests:
  T1: H-kernel at transition points (3-token window)
  T2: ch/sh sensory modality at transitions
  T3: PREFIX routing at transitions
  T4: H-enriched MIDDLE enrichment at transitions
  T5: Section stratification (C1154 prediction)
"""
import json
import sys
import math
import random
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/ENERGY_MODE_TRANSITION/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERMUTATIONS = 1000
MIN_COUNT = 30

H_ENRICHED_MIDDLES = {'opch', 'sh', 'ch', 'pch'}  # C908

SECTION_NAMES = {
    'S': 'STARS_RECIPE',
    'H': 'HERBAL',
    'B': 'BIO',
    'C': 'COSMO',
    'P': 'PHARMA',
    'T': 'TEXT',
}

TRACKED_PREFIXES = ['qo', 'ch', 'sh', 'da', 'ok', 'ot', 'ol', 'ct', 'pch']


# ============================================================
# DATA LOADING
# ============================================================

def load_tokens_by_line():
    """Load Currier B tokens grouped by (folio, line), preserving order."""
    tx = Transcript()
    morph = Morphology()
    line_groups = defaultdict(list)

    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_':
            line_groups[(t.folio, t.line)].append({
                'word': t.word,
                'middle': m.middle,
                'prefix': m.prefix,
                'prefix2': m.prefix2,
                'suffix': m.suffix,
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
            })

    return line_groups


def has_h_kernel(token):
    """Check if token's MIDDLE contains h-kernel."""
    return 'h' in token['middle']


def has_ch_sh_prefix(token):
    """Check if token has ch or sh in prefix position."""
    p = token.get('prefix')
    p2 = token.get('prefix2')
    if p in ('ch', 'sh'):
        return p
    if p2 in ('ch', 'sh'):
        return p2
    return None


def fisher_exact_2x2(a, b, c, d):
    """Approximate Fisher exact test for 2x2 table using permutation.
    Table: [[a, b], [c, d]]
    Returns approximate p-value.
    """
    n = a + b + c + d
    if n == 0:
        return 1.0

    # Use log-factorials for numerical stability
    def log_fact(x):
        return sum(math.log(i) for i in range(1, x + 1))

    row1 = a + b
    row2 = c + d
    col1 = a + c
    col2 = b + d

    # Observed odds ratio direction
    observed = a * d - b * c

    # Enumerate all tables with same marginals
    p_total = 0.0
    p_extreme = 0.0

    min_a = max(0, col1 - row2)
    max_a = min(row1, col1)

    log_denom = log_fact(n)
    log_marginals = log_fact(row1) + log_fact(row2) + log_fact(col1) + log_fact(col2)

    for a_i in range(min_a, max_a + 1):
        b_i = row1 - a_i
        c_i = col1 - a_i
        d_i = row2 - c_i
        if b_i < 0 or c_i < 0 or d_i < 0:
            continue
        log_p = log_marginals - log_denom - log_fact(a_i) - log_fact(b_i) - log_fact(c_i) - log_fact(d_i)
        p = math.exp(log_p)
        p_total += p
        this_stat = a_i * d_i - b_i * c_i
        if observed >= 0 and this_stat >= observed:
            p_extreme += p
        elif observed < 0 and this_stat <= observed:
            p_extreme += p

    return p_extreme / p_total if p_total > 0 else 1.0


# ============================================================
# T1: H-KERNEL AT TRANSITION POINTS
# ============================================================

def test_h_at_transitions(line_groups):
    """Test if h-kernel tokens mediate k->e transitions (3-token window)."""
    print("=" * 70)
    print("T1: H-KERNEL AT TRANSITION POINTS (3-token window)")
    print("=" * 70)

    # Collect triples
    mediator_h = {
        'k_to_e': {'h': 0, 'total': 0},
        'k_to_k': {'h': 0, 'total': 0},
        'e_to_k': {'h': 0, 'total': 0},
        'e_to_e': {'h': 0, 'total': 0},
    }
    target_h = {
        'k_to_e': {'h': 0, 'total': 0},
        'k_to_k': {'h': 0, 'total': 0},
        'e_to_k': {'h': 0, 'total': 0},
        'e_to_e': {'h': 0, 'total': 0},
    }

    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        for i in range(len(tokens) - 2):
            a, b, c = tokens[i], tokens[i+1], tokens[i+2]
            term_a = a['middle'][-1]
            init_c = c['middle'][0]

            if term_a == 'k' and init_c == 'e':
                cat = 'k_to_e'
            elif term_a == 'k' and init_c == 'k':
                cat = 'k_to_k'
            elif term_a == 'e' and init_c == 'k':
                cat = 'e_to_k'
            elif term_a == 'e' and init_c == 'e':
                cat = 'e_to_e'
            else:
                continue

            mediator_h[cat]['total'] += 1
            if has_h_kernel(b):
                mediator_h[cat]['h'] += 1

            target_h[cat]['total'] += 1
            if has_h_kernel(c):
                target_h[cat]['h'] += 1

    print(f"\n  MEDIATOR (token B between A and C):")
    print(f"  {'Transition':<12} {'h-count':<10} {'total':<10} {'h-rate':<10}")
    print(f"  {'-'*42}")
    for cat in ['k_to_e', 'k_to_k', 'e_to_k', 'e_to_e']:
        d = mediator_h[cat]
        rate = d['h'] / d['total'] if d['total'] > 0 else 0
        print(f"  {cat:<12} {d['h']:<10} {d['total']:<10} {rate:.1%}")

    # Key comparison: k->e vs k->k mediator h-rate
    ke_rate = mediator_h['k_to_e']['h'] / mediator_h['k_to_e']['total'] if mediator_h['k_to_e']['total'] > 0 else 0
    kk_rate = mediator_h['k_to_k']['h'] / mediator_h['k_to_k']['total'] if mediator_h['k_to_k']['total'] > 0 else 0
    delta_mediator = ke_rate - kk_rate

    print(f"\n  MEDIATOR h-rate comparison:")
    print(f"    k->e transition: {ke_rate:.1%}")
    print(f"    k->k continuation: {kk_rate:.1%}")
    print(f"    Delta: {delta_mediator:+.3f} ({'h ENRICHED at transitions' if delta_mediator > 0 else 'h NOT enriched'})")

    print(f"\n  TARGET (token C at destination):")
    print(f"  {'Transition':<12} {'h-count':<10} {'total':<10} {'h-rate':<10}")
    print(f"  {'-'*42}")
    for cat in ['k_to_e', 'k_to_k', 'e_to_k', 'e_to_e']:
        d = target_h[cat]
        rate = d['h'] / d['total'] if d['total'] > 0 else 0
        print(f"  {cat:<12} {d['h']:<10} {d['total']:<10} {rate:.1%}")

    ke_target = target_h['k_to_e']['h'] / target_h['k_to_e']['total'] if target_h['k_to_e']['total'] > 0 else 0
    kk_target = target_h['k_to_k']['h'] / target_h['k_to_k']['total'] if target_h['k_to_k']['total'] > 0 else 0
    delta_target = ke_target - kk_target
    print(f"\n    k->e target h-rate: {ke_target:.1%}")
    print(f"    k->k target h-rate: {kk_target:.1%}")
    print(f"    Delta: {delta_target:+.3f}")

    # Permutation test: shuffle within-line order
    print(f"\n  Running {N_PERMUTATIONS} permutations...")
    observed_delta = delta_mediator

    perm_count = 0
    random.seed(42)
    for _ in range(N_PERMUTATIONS):
        perm_h = {'k_to_e': {'h': 0, 'total': 0}, 'k_to_k': {'h': 0, 'total': 0}}
        for key in line_groups:
            tokens = list(line_groups[key])
            middles = [t['middle'] for t in tokens]
            random.shuffle(middles)
            # Reassign middles to tokens for h-checking
            for i in range(len(tokens) - 2):
                term_a = middles[i][-1]
                init_c = middles[i+2][0]
                b_has_h = 'h' in middles[i+1]
                if term_a == 'k' and init_c == 'e':
                    perm_h['k_to_e']['total'] += 1
                    if b_has_h:
                        perm_h['k_to_e']['h'] += 1
                elif term_a == 'k' and init_c == 'k':
                    perm_h['k_to_k']['total'] += 1
                    if b_has_h:
                        perm_h['k_to_k']['h'] += 1

        pke = perm_h['k_to_e']['h'] / perm_h['k_to_e']['total'] if perm_h['k_to_e']['total'] > 0 else 0
        pkk = perm_h['k_to_k']['h'] / perm_h['k_to_k']['total'] if perm_h['k_to_k']['total'] > 0 else 0
        if pke - pkk >= observed_delta:
            perm_count += 1

    p_value = perm_count / N_PERMUTATIONS
    print(f"  Permutation p-value (mediator delta): {p_value:.4f}")

    # Also test e->k vs e->e
    ek_rate = mediator_h['e_to_k']['h'] / mediator_h['e_to_k']['total'] if mediator_h['e_to_k']['total'] > 0 else 0
    ee_rate = mediator_h['e_to_e']['h'] / mediator_h['e_to_e']['total'] if mediator_h['e_to_e']['total'] > 0 else 0
    delta_reverse = ek_rate - ee_rate
    print(f"\n  Reverse direction (e->k vs e->e):")
    print(f"    e->k mediator h-rate: {ek_rate:.1%}")
    print(f"    e->e mediator h-rate: {ee_rate:.1%}")
    print(f"    Delta: {delta_reverse:+.3f}")

    return {
        'mediator_h': {k: v for k, v in mediator_h.items()},
        'target_h': {k: v for k, v in target_h.items()},
        'delta_mediator_k': round(delta_mediator, 4),
        'delta_target_k': round(delta_target, 4),
        'delta_mediator_e': round(delta_reverse, 4),
        'p_value_mediator': p_value,
    }


# ============================================================
# T2: ch/sh SENSORY MODALITY AT TRANSITIONS
# ============================================================

def test_ch_sh_modality(line_groups):
    """Test if ch/sh prefix distribution differs at transitions vs continuations."""
    print("\n" + "=" * 70)
    print("T2: ch/sh SENSORY MODALITY AT TRANSITIONS")
    print("=" * 70)

    # For pairs A-B: classify by A's terminal and B's initial
    prefix_at = {
        'k_to_e': Counter(),  # A's prefix when A ends k, B starts e
        'k_to_k': Counter(),  # A's prefix when A ends k, B starts k
        'e_to_k': Counter(),
        'e_to_e': Counter(),
    }

    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        for i in range(len(tokens) - 1):
            a, b = tokens[i], tokens[i+1]
            term_a = a['middle'][-1]
            init_b = b['middle'][0]

            if term_a == 'k' and init_b == 'e':
                cat = 'k_to_e'
            elif term_a == 'k' and init_b == 'k':
                cat = 'k_to_k'
            elif term_a == 'e' and init_b == 'k':
                cat = 'e_to_k'
            elif term_a == 'e' and init_b == 'e':
                cat = 'e_to_e'
            else:
                continue

            # Record A's sensory modality prefix
            modality = has_ch_sh_prefix(a)
            if modality:
                prefix_at[cat][modality] += 1
            else:
                prefix_at[cat]['other'] += 1

    print(f"\n  PREFIX of token A (predecessor) by transition type:")
    print(f"  {'Type':<12} {'ch':<8} {'sh':<8} {'other':<8} {'total':<8} {'ch%':<8} {'sh%':<8}")
    print(f"  {'-'*56}")
    for cat in ['k_to_e', 'k_to_k', 'e_to_k', 'e_to_e']:
        d = prefix_at[cat]
        total = sum(d.values())
        ch_pct = d['ch'] / total if total > 0 else 0
        sh_pct = d['sh'] / total if total > 0 else 0
        print(f"  {cat:<12} {d['ch']:<8} {d['sh']:<8} {d['other']:<8} {total:<8} {ch_pct:.1%}   {sh_pct:.1%}")

    # Fisher exact: ch/sh ratio at k->e vs k->k
    a = prefix_at['k_to_e'].get('ch', 0)
    b = prefix_at['k_to_e'].get('sh', 0)
    c = prefix_at['k_to_k'].get('ch', 0)
    d_val = prefix_at['k_to_k'].get('sh', 0)

    print(f"\n  Fisher exact test (ch vs sh, transition vs continuation):")
    print(f"    k->e: ch={a}, sh={b}")
    print(f"    k->k: ch={c}, sh={d_val}")

    if a + b + c + d_val > 0:
        p_fisher = fisher_exact_2x2(a, b, c, d_val)
        print(f"    p = {p_fisher:.4f}")
    else:
        p_fisher = 1.0
        print(f"    Insufficient data")

    # Also look at the TARGET token's prefix
    target_prefix = {
        'k_to_e': Counter(),
        'k_to_k': Counter(),
    }
    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        for i in range(len(tokens) - 1):
            a_tok, b_tok = tokens[i], tokens[i+1]
            term_a = a_tok['middle'][-1]
            init_b = b_tok['middle'][0]

            if term_a == 'k' and init_b == 'e':
                cat = 'k_to_e'
            elif term_a == 'k' and init_b == 'k':
                cat = 'k_to_k'
            else:
                continue

            modality = has_ch_sh_prefix(b_tok)
            if modality:
                target_prefix[cat][modality] += 1
            else:
                target_prefix[cat]['other'] += 1

    print(f"\n  PREFIX of token B (target) at transitions:")
    for cat in ['k_to_e', 'k_to_k']:
        d = target_prefix[cat]
        total = sum(d.values())
        ch_pct = d.get('ch', 0) / total if total > 0 else 0
        sh_pct = d.get('sh', 0) / total if total > 0 else 0
        print(f"    {cat}: ch={d.get('ch', 0)} ({ch_pct:.1%}), sh={d.get('sh', 0)} ({sh_pct:.1%}), total={total}")

    return {
        'prefix_at_predecessor': {k: dict(v) for k, v in prefix_at.items()},
        'target_prefix': {k: dict(v) for k, v in target_prefix.items()},
        'fisher_p': round(p_fisher, 4),
    }


# ============================================================
# T3: PREFIX ROUTING AT TRANSITIONS
# ============================================================

def test_prefix_routing(line_groups):
    """Test if PREFIX of target token differs at mode switches vs continuations."""
    print("\n" + "=" * 70)
    print("T3: PREFIX ROUTING AT TRANSITIONS")
    print("=" * 70)

    switch_prefix = Counter()  # PREFIX of target at k->e or e->k
    continue_prefix = Counter()  # PREFIX of target at k->k or e->e

    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        for i in range(len(tokens) - 1):
            a, b = tokens[i], tokens[i+1]
            term_a = a['middle'][-1]
            init_b = b['middle'][0]

            if term_a not in ('k', 'e') or init_b not in ('k', 'e'):
                continue

            is_switch = (term_a != init_b)
            prefix = b.get('prefix') or 'none'

            if is_switch:
                switch_prefix[prefix] += 1
            else:
                continue_prefix[prefix] += 1

    total_switch = sum(switch_prefix.values())
    total_continue = sum(continue_prefix.values())

    print(f"\n  Total mode switches (k->e or e->k): {total_switch}")
    print(f"  Total mode continuations (k->k or e->e): {total_continue}")

    # Compute enrichment for each prefix
    all_prefixes = sorted(set(switch_prefix.keys()) | set(continue_prefix.keys()))

    print(f"\n  {'Prefix':<10} {'Switch':<10} {'S%':<8} {'Continue':<10} {'C%':<8} {'Enrichment':<12}")
    print(f"  {'-'*60}")

    enrichments = {}
    chi2 = 0
    for pfx in all_prefixes:
        s_count = switch_prefix.get(pfx, 0)
        c_count = continue_prefix.get(pfx, 0)
        s_rate = s_count / total_switch if total_switch > 0 else 0
        c_rate = c_count / total_continue if total_continue > 0 else 0
        enrichment = s_rate / c_rate if c_rate > 0 else float('inf') if s_rate > 0 else 1.0

        # Chi-squared contribution
        total_pfx = s_count + c_count
        exp_s = total_pfx * total_switch / (total_switch + total_continue) if (total_switch + total_continue) > 0 else 0
        exp_c = total_pfx * total_continue / (total_switch + total_continue) if (total_switch + total_continue) > 0 else 0
        if exp_s > 5 and exp_c > 5:
            chi2 += (s_count - exp_s)**2 / exp_s + (c_count - exp_c)**2 / exp_c

        if s_count + c_count >= 10:  # Only show meaningful prefixes
            enr_str = f"{enrichment:.2f}x" if enrichment < 100 else "inf"
            print(f"  {pfx:<10} {s_count:<10} {s_rate:.1%}   {c_count:<10} {c_rate:.1%}   {enr_str}")
            enrichments[pfx] = round(enrichment, 3)

    print(f"\n  Chi-squared (all prefixes): {chi2:.1f}")

    # Top switch-enriched prefixes
    top_switch = sorted(enrichments.items(), key=lambda x: -x[1])[:5]
    print(f"\n  Top switch-enriched prefixes: {', '.join(f'{p}({e:.2f}x)' for p, e in top_switch)}")

    return {
        'total_switch': total_switch,
        'total_continue': total_continue,
        'enrichments': enrichments,
        'chi2': round(chi2, 1),
    }


# ============================================================
# T4: H-ENRICHED MIDDLE ENRICHMENT
# ============================================================

def test_h_enriched_middles(line_groups):
    """Test if C908 h-enriched MIDDLEs appear before transitions."""
    print("\n" + "=" * 70)
    print("T4: H-ENRICHED MIDDLE ENRICHMENT AT TRANSITIONS")
    print("=" * 70)

    print(f"  H-enriched MIDDLEs (C908): {H_ENRICHED_MIDDLES}")

    # For pairs A-B: is A's MIDDLE h-enriched more at transitions?
    before_transition = {'h_enriched': 0, 'other': 0}
    before_continuation = {'h_enriched': 0, 'other': 0}

    # Also check: is B (target) h-enriched more at transitions?
    at_transition = {'h_enriched': 0, 'other': 0}
    at_continuation = {'h_enriched': 0, 'other': 0}

    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        for i in range(len(tokens) - 1):
            a, b = tokens[i], tokens[i+1]
            term_a = a['middle'][-1]
            init_b = b['middle'][0]

            if term_a == 'k' and init_b == 'e':
                # Transition
                if a['middle'] in H_ENRICHED_MIDDLES:
                    before_transition['h_enriched'] += 1
                else:
                    before_transition['other'] += 1
                if b['middle'] in H_ENRICHED_MIDDLES:
                    at_transition['h_enriched'] += 1
                else:
                    at_transition['other'] += 1
            elif term_a == 'k' and init_b == 'k':
                # Continuation
                if a['middle'] in H_ENRICHED_MIDDLES:
                    before_continuation['h_enriched'] += 1
                else:
                    before_continuation['other'] += 1
                if b['middle'] in H_ENRICHED_MIDDLES:
                    at_continuation['h_enriched'] += 1
                else:
                    at_continuation['other'] += 1

    bt_total = before_transition['h_enriched'] + before_transition['other']
    bc_total = before_continuation['h_enriched'] + before_continuation['other']
    bt_rate = before_transition['h_enriched'] / bt_total if bt_total > 0 else 0
    bc_rate = before_continuation['h_enriched'] / bc_total if bc_total > 0 else 0

    print(f"\n  PREDECESSOR (token A before B):")
    print(f"    Before k->e transition: {before_transition['h_enriched']}/{bt_total} h-enriched ({bt_rate:.1%})")
    print(f"    Before k->k continuation: {before_continuation['h_enriched']}/{bc_total} h-enriched ({bc_rate:.1%})")
    enr = bt_rate / bc_rate if bc_rate > 0 else float('inf')
    print(f"    Enrichment: {enr:.2f}x")

    p_before = fisher_exact_2x2(
        before_transition['h_enriched'], before_transition['other'],
        before_continuation['h_enriched'], before_continuation['other']
    )
    print(f"    Fisher p: {p_before:.4f}")

    at_total = at_transition['h_enriched'] + at_transition['other']
    ac_total = at_continuation['h_enriched'] + at_continuation['other']
    at_rate = at_transition['h_enriched'] / at_total if at_total > 0 else 0
    ac_rate = at_continuation['h_enriched'] / ac_total if ac_total > 0 else 0

    print(f"\n  TARGET (token B at destination):")
    print(f"    At k->e transition target: {at_transition['h_enriched']}/{at_total} h-enriched ({at_rate:.1%})")
    print(f"    At k->k continuation target: {at_continuation['h_enriched']}/{ac_total} h-enriched ({ac_rate:.1%})")
    enr_t = at_rate / ac_rate if ac_rate > 0 else float('inf')
    print(f"    Enrichment: {enr_t:.2f}x")

    p_at = fisher_exact_2x2(
        at_transition['h_enriched'], at_transition['other'],
        at_continuation['h_enriched'], at_continuation['other']
    )
    print(f"    Fisher p: {p_at:.4f}")

    return {
        'before_transition_rate': round(bt_rate, 4),
        'before_continuation_rate': round(bc_rate, 4),
        'before_enrichment': round(enr, 3),
        'before_fisher_p': round(p_before, 4),
        'at_transition_rate': round(at_rate, 4),
        'at_continuation_rate': round(ac_rate, 4),
        'at_enrichment': round(enr_t, 3),
        'at_fisher_p': round(p_at, 4),
    }


# ============================================================
# T5: SECTION STRATIFICATION
# ============================================================

def test_section_stratification(line_groups):
    """Run T1 mediator test per section."""
    print("\n" + "=" * 70)
    print("T5: SECTION STRATIFICATION")
    print("=" * 70)

    # Group lines by section
    section_lines = defaultdict(dict)
    for key, tokens in line_groups.items():
        if tokens:
            sec = tokens[0]['section']
            section_lines[sec][key] = tokens

    print(f"\n  {'Section':<16} {'Lines':<8} {'k->e':<8} {'k->k':<8} "
          f"{'h-rate k->e':<12} {'h-rate k->k':<12} {'Delta':<10}")
    print(f"  {'-'*76}")

    section_results = {}
    for sec_code in sorted(section_lines.keys()):
        sec_name = SECTION_NAMES.get(sec_code, sec_code)
        lines = section_lines[sec_code]

        # Compute mediator h-rates for k->e vs k->k
        ke_h, ke_total = 0, 0
        kk_h, kk_total = 0, 0

        for key in lines:
            tokens = lines[key]
            for i in range(len(tokens) - 2):
                a, b, c = tokens[i], tokens[i+1], tokens[i+2]
                term_a = a['middle'][-1]
                init_c = c['middle'][0]

                if term_a == 'k' and init_c == 'e':
                    ke_total += 1
                    if has_h_kernel(b):
                        ke_h += 1
                elif term_a == 'k' and init_c == 'k':
                    kk_total += 1
                    if has_h_kernel(b):
                        kk_h += 1

        ke_rate = ke_h / ke_total if ke_total > 0 else 0
        kk_rate = kk_h / kk_total if kk_total > 0 else 0
        delta = ke_rate - kk_rate

        n_lines = len(lines)
        sufficient = ke_total >= MIN_COUNT and kk_total >= MIN_COUNT

        if sufficient:
            print(f"  {sec_name:<16} {n_lines:<8} {ke_total:<8} {kk_total:<8} "
                  f"{ke_rate:.1%}       {kk_rate:.1%}       {delta:+.3f}")
        else:
            print(f"  {sec_name:<16} {n_lines:<8} {ke_total:<8} {kk_total:<8} "
                  f"(insufficient data)")

        section_results[sec_name] = {
            'n_lines': n_lines,
            'ke_total': ke_total,
            'kk_total': kk_total,
            'ke_h_rate': round(ke_rate, 4),
            'kk_h_rate': round(kk_rate, 4),
            'delta': round(delta, 4),
            'sufficient': sufficient,
        }

    # Check C1154 prediction: STARS_RECIPE should have strongest signal
    sufficient_sections = {k: v for k, v in section_results.items() if v['sufficient']}
    if sufficient_sections:
        ranked = sorted(sufficient_sections.items(), key=lambda x: -x[1]['delta'])
        print(f"\n  Ranked by delta (strongest h-mediation first):")
        for i, (sec, v) in enumerate(ranked):
            marker = " <-- C1154 predicts strongest" if sec == 'STARS_RECIPE' else ""
            print(f"    {i+1}. {sec}: {v['delta']:+.3f}{marker}")

        stars = section_results.get('STARS_RECIPE', {})
        stars_rank = next((i+1 for i, (s, _) in enumerate(ranked) if s == 'STARS_RECIPE'), None)
        print(f"\n  C1154 prediction (STARS_RECIPE = strongest): "
              f"{'CONFIRMED' if stars_rank == 1 else f'RANK {stars_rank}'}")

    return section_results


# ============================================================
# MAIN
# ============================================================

def main():
    print("ENERGY MODE TRANSITION MECHANISM TEST -- Phase 426")
    print("=" * 70)

    print("\nLoading data...")
    line_groups = load_tokens_by_line()
    n_tokens = sum(len(v) for v in line_groups.values())
    n_lines = len(line_groups)
    print(f"Loaded {n_tokens} tokens across {n_lines} lines")

    results = {}
    results['T1_h_at_transitions'] = test_h_at_transitions(line_groups)
    results['T2_ch_sh_modality'] = test_ch_sh_modality(line_groups)
    results['T3_prefix_routing'] = test_prefix_routing(line_groups)
    results['T4_h_enriched_middles'] = test_h_enriched_middles(line_groups)
    results['T5_section_stratification'] = test_section_stratification(line_groups)

    # Save
    output_path = RESULTS_DIR / "h_kernel_transition_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"Results saved to {output_path}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
