"""
Phase 397: Rosettes Ring Text Grammar Test

Tests whether rosette ring texts follow Currier B program grammar rules.
Uses data/rosettes_unified.json as the primary data source.

9 tests across 3 tiers:
  Tier 1 - Construction: PREFIX-MIDDLE selectivity, kernel grammar, suffix distribution
  Tier 2 - Transition: forbidden MIDDLE pairs, macro-state transitions
  Tier 3 - Distribution: role distribution, affordance bins, PREFIX lanes, B-class coverage

Baselines: matched-length B paragraphs (primary), AZC diagram text (negative control)
"""

import json
import math
import random
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))

from scripts.voynich import Transcript, Morphology, BFolioDecoder

random.seed(42)

# ============================================================
# Role taxonomy from BCSC role_taxonomy (class -> role)
# ============================================================
CLASS_TO_ROLE = {}
for c in [10, 11, 12, 17]:
    CLASS_TO_ROLE[c] = 'CC'
for c in [8] + list(range(31, 38)) + [39] + list(range(41, 50)):
    CLASS_TO_ROLE[c] = 'EN'
for c in [1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29]:
    CLASS_TO_ROLE[c] = 'AX'
for c in [9, 13, 14, 23]:
    CLASS_TO_ROLE[c] = 'FQ'
for c in [7, 30, 38, 40]:
    CLASS_TO_ROLE[c] = 'FO'

# B corpus role proportions (from BCSC)
B_ROLE_PROPORTIONS = {
    'CC': 0.044, 'EN': 0.312, 'AX': 0.166, 'FQ': 0.125, 'FO': 0.047
}

# B macro-state transition matrix (BCSC lines 1049-1054)
B_MACRO_MATRIX = {
    'AXM':     {'AXM': 0.697, 'AXm': 0.029, 'FL_HAZ': 0.052, 'FQ': 0.173, 'CC': 0.042, 'FL_SAFE': 0.008},
    'AXm':     {'AXM': 0.682, 'AXm': 0.025, 'FL_HAZ': 0.062, 'FQ': 0.189, 'CC': 0.032, 'FL_SAFE': 0.010},
    'FL_HAZ':  {'AXM': 0.565, 'AXm': 0.026, 'FL_HAZ': 0.106, 'FQ': 0.239, 'CC': 0.049, 'FL_SAFE': 0.016},
    'FQ':      {'AXM': 0.591, 'AXm': 0.033, 'FL_HAZ': 0.073, 'FQ': 0.250, 'CC': 0.043, 'FL_SAFE': 0.009},
    'CC':      {'AXM': 0.672, 'AXm': 0.033, 'FL_HAZ': 0.070, 'FQ': 0.176, 'CC': 0.041, 'FL_SAFE': 0.008},
    'FL_SAFE': {'AXM': 0.698, 'AXm': 0.023, 'FL_HAZ': 0.070, 'FQ': 0.093, 'CC': 0.093, 'FL_SAFE': 0.023},
}
B_STATIONARY = {'AXM': 0.667, 'AXm': 0.029, 'FL_HAZ': 0.060, 'FQ': 0.192, 'CC': 0.043, 'FL_SAFE': 0.008}
MACRO_STATES = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']


def load_data():
    """Load all data sources."""
    # Unified rosettes JSON
    with open(PROJECT / 'data' / 'rosettes_unified.json', 'r', encoding='utf-8') as f:
        unified = json.load(f)

    # 17 forbidden MIDDLE pairs
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
              'r', encoding='utf-8') as f:
        forbidden_inv = json.load(f)
    forbidden_middle_pairs = set()
    for t in forbidden_inv['transitions']:
        forbidden_middle_pairs.add((t['source'], t['target']))

    # 102 forbidden PREFIX x MIDDLE combinations
    with open(PROJECT / 'phases' / 'MIDDLE_SEMANTIC_DEEPENING' / 'results' / 'prefix_middle_interaction.json',
              'r', encoding='utf-8') as f:
        pm_data = json.load(f)
    forbidden_pm = set()
    for pair in pm_data['forbidden_pairs']:
        p = pair['prefix'] if pair['prefix'] != '(none)' else None
        forbidden_pm.add((p, pair['middle']))

    return {
        'unified': unified,
        'forbidden_middle_pairs': forbidden_middle_pairs,
        'forbidden_pm': forbidden_pm,
    }


def extract_ring_texts(unified):
    """Extract the 5 transcribed ring text token sequences."""
    ring_texts = {}
    for pos in ['NW', 'NORTH', 'WEST', 'CENTER', 'SOUTH']:
        rt = unified['rosette_grid'][pos]['ring_text']
        if rt.get('status') != 'NOT_TRANSCRIBED':
            ring_texts[pos] = rt['tokens']
    return ring_texts


def pool_ring_tokens(ring_texts):
    """Return flat list of all ring text tokens."""
    tokens = []
    for pos in ['NW', 'NORTH', 'WEST', 'CENTER', 'SOUTH']:
        if pos in ring_texts:
            tokens.extend(ring_texts[pos])
    return tokens


def build_b_baselines():
    """Build B corpus baselines: matched-length paragraphs + AZC negative control."""
    print("Building B corpus baselines...")
    tx = Transcript()
    morph = Morphology()
    decoder = BFolioDecoder()

    # --- B paragraph baselines ---
    # Get all B folio names
    b_folios = sorted(set(t.folio for t in tx.currier_b()))
    print(f"  B folios: {len(b_folios)}")

    # Token->class lookup for b_class
    token_to_class = decoder._token_to_class

    # Get all B folio lines as token lists, then build consecutive windows
    # matching ring text sizes (23-37 tokens)
    all_b_lines = []  # list of (folio, line_tokens)
    for folio_name in b_folios:
        lines = decoder.analyze_folio_lines(folio_name)
        if not lines:
            continue
        for la in lines:
            line_tokens = []
            for t in la.tokens:
                bc = token_to_class.get(t.word)
                line_tokens.append({
                    'word': t.word,
                    'prefix': t.morph.prefix,
                    'middle': t.morph.middle,
                    'suffix': t.morph.suffix,
                    'macro_state': t.macro_state,
                    'b_class': bc,
                    'affordance_bin': t.middle_affordance_bin,
                    'prefix_lane': t.prefix_zone,
                })
            all_b_lines.append((folio_name, line_tokens))

    # Build matched-size paragraphs by concatenating consecutive lines within a folio
    b_paragraphs = []
    folio_groups = defaultdict(list)
    for folio_name, line_tokens in all_b_lines:
        folio_groups[folio_name].append(line_tokens)

    for folio_name, folio_lines in folio_groups.items():
        # Slide a window of consecutive lines, accumulating tokens until 23-37 range
        current = []
        for line_tokens in folio_lines:
            current.extend(line_tokens)
            if len(current) >= 23:
                b_paragraphs.append(current[:37])  # Cap at 37
                current = []
        # Keep remainder if 15+ tokens (wider range for more samples)
        if len(current) >= 15:
            b_paragraphs.append(current)

    # Filter to matched length (23-37 tokens, matching ring text range)
    matched_paras = [p for p in b_paragraphs if 23 <= len(p) <= 37]
    print(f"  B paragraphs total: {len(b_paragraphs)}")
    print(f"  Matched-length (23-37 tokens): {len(matched_paras)}")

    # If not enough matched paragraphs, widen the range
    if len(matched_paras) < 50:
        matched_paras = [p for p in b_paragraphs if 15 <= len(p) <= 45]
        print(f"  Widened to 15-45 tokens: {len(matched_paras)}")

    # Sample up to 200
    if len(matched_paras) > 200:
        baseline_paras = random.sample(matched_paras, 200)
    else:
        baseline_paras = matched_paras

    # --- Also build within-line transition data for transition baselines ---
    b_within_line_transitions = []
    for folio_name in b_folios:
        lines = decoder.analyze_folio_lines(folio_name)
        for la in lines:
            middles = [t.morph.middle for t in la.tokens if t.morph.middle]
            states = [t.macro_state for t in la.tokens if t.macro_state]
            for i in range(len(middles) - 1):
                b_within_line_transitions.append((middles[i], middles[i+1]))

    # --- AZC negative control ---
    azc_tokens = []
    for token in tx.azc():
        if token.folio.startswith('f85') or token.folio.startswith('f86'):
            continue  # Exclude Rosettes-related folios
        m = morph.extract(token.word)
        analysis = decoder.analyze_token(token.word, False, False)
        bc = token_to_class.get(token.word)
        azc_tokens.append({
            'word': token.word,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'macro_state': analysis.macro_state,
            'b_class': bc,
            'affordance_bin': analysis.middle_affordance_bin,
            'prefix_lane': analysis.prefix_zone,
        })

    print(f"  AZC negative control tokens (non-Rosettes): {len(azc_tokens)}")
    print(f"  B within-line transitions: {len(b_within_line_transitions)}")

    return {
        'b_paragraphs': baseline_paras,
        'b_within_line_transitions': b_within_line_transitions,
        'azc_tokens': azc_tokens,
    }


# ============================================================
# TIER 1: CONSTRUCTION COMPLIANCE
# ============================================================

def test_prefix_middle_selectivity(ring_texts, forbidden_pm):
    """Test 1: Check ring text tokens against 102 forbidden PREFIX x MIDDLE combinations."""
    print("\n" + "="*70)
    print("TEST 1: PREFIX-MIDDLE Selectivity (C911)")
    print("="*70)

    violations = []
    tested = 0
    per_ring = {}

    for pos, tokens in ring_texts.items():
        ring_violations = []
        ring_tested = 0
        for tok in tokens:
            prefix = tok.get('prefix')
            middle = tok.get('middle')
            if middle:  # All tokens with a MIDDLE are testable
                ring_tested += 1
                tested += 1
                if (prefix, middle) in forbidden_pm:
                    violation = {'word': tok['word'], 'prefix': prefix, 'middle': middle, 'ring': pos}
                    violations.append(violation)
                    ring_violations.append(violation)
        per_ring[pos] = {'tested': ring_tested, 'violations': len(ring_violations)}

    print(f"  Tokens tested: {tested}")
    print(f"  Violations: {len(violations)}")
    if violations:
        print(f"  VIOLATION DETAILS:")
        for v in violations:
            print(f"    {v['ring']}: {v['word']} (prefix={v['prefix']}, middle={v['middle']})")
    print(f"  B baseline: 0 violations (by construction)")
    verdict = "PASS" if len(violations) == 0 else f"FAIL ({len(violations)} violations)"
    print(f"  Verdict: {verdict}")

    return {
        'test': 'PREFIX_MIDDLE_SELECTIVITY',
        'constraint': 'C911',
        'n_forbidden_rules': len(forbidden_pm),
        'n_tested': tested,
        'n_violations': len(violations),
        'violations': violations,
        'per_ring': per_ring,
        'b_baseline': 0,
        'verdict': verdict,
    }


def test_kernel_construction(ring_texts):
    """Test 2: Check within-token kernel character ordering (C521)."""
    print("\n" + "="*70)
    print("TEST 2: Kernel Construction Grammar (C521)")
    print("="*70)

    # Kernel characters and their expected ordering
    kernel_chars = {'k', 'h', 'e'}
    # Expected: k->e elevated, h->e elevated, e->h blocked, h->k suppressed
    pair_expectations = {
        ('k', 'e'): 'elevated',
        ('h', 'e'): 'elevated',
        ('e', 'h'): 'blocked',
        ('h', 'k'): 'suppressed',
        ('e', 'k'): 'neutral',
        ('k', 'h'): 'neutral',
    }

    # Count kernel character pair orderings within MIDDLEs
    pair_counts = Counter()
    tokens_with_kernel = 0
    tokens_with_multi_kernel = 0
    total_tokens = 0
    per_ring = {}

    for pos, tokens in ring_texts.items():
        ring_pairs = Counter()
        ring_multi = 0
        for tok in tokens:
            total_tokens += 1
            middle = tok.get('middle', '') or ''
            # Find kernel characters and their positions
            kc_positions = []
            for i, ch in enumerate(middle):
                if ch in kernel_chars:
                    kc_positions.append((i, ch))
            if kc_positions:
                tokens_with_kernel += 1
            if len(kc_positions) >= 2:
                tokens_with_multi_kernel += 1
                # Check all pairs
                for i in range(len(kc_positions)):
                    for j in range(i + 1, len(kc_positions)):
                        pair = (kc_positions[i][1], kc_positions[j][1])
                        pair_counts[pair] += 1
                        ring_pairs[pair] += 1
                        ring_multi += 1
        per_ring[pos] = {'multi_kernel_tokens': ring_multi,
                        'pairs': {f"{a}->{b}": c for (a,b), c in ring_pairs.items()}}

    print(f"  Total tokens: {total_tokens}")
    print(f"  Tokens with kernel chars: {tokens_with_kernel} ({100*tokens_with_kernel/max(total_tokens,1):.1f}%)")
    print(f"  Tokens with 2+ kernel chars: {tokens_with_multi_kernel}")
    print(f"  Kernel pair ordering counts:")
    for pair, expected in pair_expectations.items():
        count = pair_counts.get(pair, 0)
        print(f"    {pair[0]}->{pair[1]}: {count} (expected: {expected})")

    # Check compliance: k->e and h->e should dominate over e->k, e->h
    ke_forward = pair_counts.get(('k', 'e'), 0)
    ek_backward = pair_counts.get(('e', 'k'), 0)
    he_forward = pair_counts.get(('h', 'e'), 0)
    eh_backward = pair_counts.get(('e', 'h'), 0)
    hk_backward = pair_counts.get(('h', 'k'), 0)
    kh_forward = pair_counts.get(('k', 'h'), 0)

    compliance_notes = []
    if ke_forward + ek_backward > 0:
        ke_ratio = ke_forward / max(ek_backward, 0.5)
        compliance_notes.append(f"k->e / e->k = {ke_ratio:.1f}x (B: 4.02x)")
    if he_forward + eh_backward > 0:
        he_ratio = he_forward / max(eh_backward, 0.5)
        compliance_notes.append(f"h->e / e->h = {he_ratio:.1f}x (B: 6.09x)")

    for note in compliance_notes:
        print(f"  {note}")

    return {
        'test': 'KERNEL_CONSTRUCTION_GRAMMAR',
        'constraint': 'C521',
        'n_total_tokens': total_tokens,
        'n_with_kernel': tokens_with_kernel,
        'n_with_multi_kernel': tokens_with_multi_kernel,
        'pair_counts': {f"{a}->{b}": c for (a,b), c in pair_counts.items()},
        'pair_expectations': {f"{a}->{b}": e for (a,b), e in pair_expectations.items()},
        'compliance_notes': compliance_notes,
        'per_ring': per_ring,
    }


def test_suffix_distribution(ring_texts, baselines):
    """Test 3: Compare suffix distribution to B corpus (C588)."""
    print("\n" + "="*70)
    print("TEST 3: SUFFIX Distribution (C588)")
    print("="*70)

    # Ring text suffix counts
    ring_suffixes = Counter()
    ring_total = 0
    ring_bare = 0
    for tokens in ring_texts.values():
        for tok in tokens:
            ring_total += 1
            s = tok.get('suffix')
            if s:
                ring_suffixes[s] += 1
            else:
                ring_bare += 1

    # B baseline suffix counts
    b_suffixes = Counter()
    b_total = 0
    b_bare = 0
    for para in baselines['b_paragraphs']:
        for tok in para:
            b_total += 1
            s = tok.get('suffix')
            if s:
                b_suffixes[s] += 1
            else:
                b_bare += 1

    # AZC suffix counts
    azc_suffixes = Counter()
    azc_total = 0
    azc_bare = 0
    for tok in baselines['azc_tokens']:
        azc_total += 1
        s = tok.get('suffix')
        if s:
            azc_suffixes[s] += 1
        else:
            azc_bare += 1

    ring_bare_pct = 100 * ring_bare / max(ring_total, 1)
    b_bare_pct = 100 * b_bare / max(b_total, 1)
    azc_bare_pct = 100 * azc_bare / max(azc_total, 1)

    print(f"  Ring text: {ring_total} tokens, {ring_bare} bare ({ring_bare_pct:.1f}%)")
    print(f"  B baseline: {b_total} tokens, {b_bare} bare ({b_bare_pct:.1f}%)")
    print(f"  AZC control: {azc_total} tokens, {azc_bare} bare ({azc_bare_pct:.1f}%)")

    # Top suffixes comparison
    print(f"\n  Top suffixes (ring text):")
    for suffix, count in ring_suffixes.most_common(10):
        b_rate = 100 * b_suffixes.get(suffix, 0) / max(b_total, 1)
        r_rate = 100 * count / max(ring_total, 1)
        print(f"    {suffix:>6}: {count:>3} ({r_rate:.1f}%)  B: {b_rate:.1f}%")

    return {
        'test': 'SUFFIX_DISTRIBUTION',
        'constraint': 'C588',
        'ring': {
            'n_tokens': ring_total,
            'n_bare': ring_bare,
            'bare_pct': round(ring_bare_pct, 1),
            'suffix_counts': dict(ring_suffixes.most_common()),
        },
        'b_baseline': {
            'n_tokens': b_total,
            'n_bare': b_bare,
            'bare_pct': round(b_bare_pct, 1),
            'top_suffixes': dict(b_suffixes.most_common(15)),
        },
        'azc_control': {
            'n_tokens': azc_total,
            'n_bare': azc_bare,
            'bare_pct': round(azc_bare_pct, 1),
        },
    }


# ============================================================
# TIER 2: TRANSITION COMPLIANCE
# ============================================================

def test_forbidden_transitions(ring_texts, forbidden_middle_pairs, baselines):
    """Test 4: Check MIDDLE bigram compliance with 17 forbidden pairs (C109, C789)."""
    print("\n" + "="*70)
    print("TEST 4: Forbidden MIDDLE Transition Compliance (C109, C789)")
    print("="*70)

    # Build set of source MIDDLEs that participate in forbidden pairs
    forbidden_sources = set(s for s, t in forbidden_middle_pairs)

    # Ring text analysis
    ring_eligible = 0
    ring_violations = 0
    ring_total_bigrams = 0
    violation_details = []
    per_ring = {}

    for pos, tokens in ring_texts.items():
        middles = [tok.get('middle') for tok in tokens if tok.get('middle')]
        r_elig = 0
        r_viol = 0
        for i in range(len(middles) - 1):
            ring_total_bigrams += 1
            src, tgt = middles[i], middles[i+1]
            if src in forbidden_sources:
                r_elig += 1
                ring_eligible += 1
                if (src, tgt) in forbidden_middle_pairs:
                    r_viol += 1
                    ring_violations += 1
                    violation_details.append({
                        'ring': pos,
                        'source': src,
                        'target': tgt,
                        'position': i
                    })
        per_ring[pos] = {
            'n_bigrams': len(middles) - 1,
            'n_eligible': r_elig,
            'n_violations': r_viol,
            'violation_rate': round(r_viol / max(r_elig, 1), 3),
        }

    ring_violation_rate = ring_violations / max(ring_eligible, 1)

    # B baseline: compute from within-line transitions
    b_eligible = 0
    b_violations = 0
    for src, tgt in baselines['b_within_line_transitions']:
        if src in forbidden_sources:
            b_eligible += 1
            if (src, tgt) in forbidden_middle_pairs:
                b_violations += 1
    b_violation_rate = b_violations / max(b_eligible, 1)

    print(f"  Ring text: {ring_total_bigrams} bigrams, {ring_eligible} eligible, "
          f"{ring_violations} violations ({100*ring_violation_rate:.1f}%)")
    print(f"  B baseline: {b_eligible} eligible, {b_violations} violations ({100*b_violation_rate:.1f}%)")
    print(f"  B expected (C789): ~35% violation rate")

    if violation_details:
        print(f"  Violation details:")
        for v in violation_details:
            print(f"    {v['ring']} pos {v['position']}: {v['source']} -> {v['target']}")

    for pos, data in per_ring.items():
        print(f"  {pos}: {data['n_eligible']} eligible, {data['n_violations']} violations")

    # Fisher's exact test approximation (2x2: ring vs B, violated vs compliant)
    # Just report the numbers; formal test with scipy if available
    try:
        from scipy.stats import fisher_exact
        table = [[ring_violations, ring_eligible - ring_violations],
                 [b_violations, b_eligible - b_violations]]
        odds_ratio, p_value = fisher_exact(table)
        print(f"  Fisher's exact: OR={odds_ratio:.3f}, p={p_value:.4f}")
        fisher_result = {'odds_ratio': round(odds_ratio, 4), 'p_value': round(p_value, 6)}
    except ImportError:
        fisher_result = None
        print("  (scipy not available for Fisher's exact test)")

    return {
        'test': 'FORBIDDEN_MIDDLE_TRANSITIONS',
        'constraint': 'C109, C789',
        'n_forbidden_pairs': len(forbidden_middle_pairs),
        'ring': {
            'n_bigrams': ring_total_bigrams,
            'n_eligible': ring_eligible,
            'n_violations': ring_violations,
            'violation_rate': round(ring_violation_rate, 4),
        },
        'b_baseline': {
            'n_eligible': b_eligible,
            'n_violations': b_violations,
            'violation_rate': round(b_violation_rate, 4),
        },
        'violation_details': violation_details,
        'per_ring': per_ring,
        'fisher_exact': fisher_result,
    }


def test_macro_state_transitions(ring_texts, baselines):
    """Test 5: Compare macro-state transition matrix to B corpus (C976, C978)."""
    print("\n" + "="*70)
    print("TEST 5: Macro-State Transition Matrix (C976, C978)")
    print("="*70)

    # Ring text macro-state sequences (pooled)
    ring_states = []
    per_ring_states = {}
    for pos, tokens in ring_texts.items():
        states = [tok.get('macro_state') for tok in tokens if tok.get('macro_state')]
        ring_states.extend(states)
        per_ring_states[pos] = states

    # Build ring transition matrix
    ring_trans = defaultdict(Counter)
    for i in range(len(ring_states) - 1):
        ring_trans[ring_states[i]][ring_states[i+1]] += 1

    # Ring stationary distribution
    ring_dist = Counter(ring_states)
    ring_total = sum(ring_dist.values())

    print(f"  Ring text tokens with macro_state: {ring_total} / {sum(len(t) for t in ring_texts.values())}")
    print(f"\n  Ring stationary distribution vs B:")
    for state in MACRO_STATES:
        r_pct = 100 * ring_dist.get(state, 0) / max(ring_total, 1)
        b_pct = 100 * B_STATIONARY[state]
        delta = r_pct - b_pct
        marker = " ***" if abs(delta) > 10 else ""
        print(f"    {state:>8}: ring={r_pct:5.1f}%  B={b_pct:5.1f}%  delta={delta:+6.1f}%{marker}")

    # JSD between ring and B stationary distributions
    def jsd(p, q):
        """Jensen-Shannon divergence."""
        m = {}
        all_keys = set(list(p.keys()) + list(q.keys()))
        for k in all_keys:
            m[k] = 0.5 * (p.get(k, 0) + q.get(k, 0))
        kl_pm = sum(p.get(k, 0) * math.log2(p[k] / m[k]) for k in p if p[k] > 0 and m[k] > 0)
        kl_qm = sum(q.get(k, 0) * math.log2(q[k] / m[k]) for k in q if q[k] > 0 and m[k] > 0)
        return 0.5 * (kl_pm + kl_qm)

    ring_norm = {s: ring_dist.get(s, 0) / max(ring_total, 1) for s in MACRO_STATES}
    stationary_jsd = jsd(ring_norm, B_STATIONARY)
    print(f"\n  JSD(ring, B_stationary) = {stationary_jsd:.4f}")

    # Bootstrap: sample 200 random B paragraph-length chunks and compute JSD
    bootstrap_jsds = []
    for para in baselines['b_paragraphs']:
        para_states = [tok.get('macro_state') for tok in para if tok.get('macro_state')]
        if len(para_states) < 5:
            continue
        para_dist = Counter(para_states)
        para_total = sum(para_dist.values())
        para_norm = {s: para_dist.get(s, 0) / para_total for s in MACRO_STATES}
        bootstrap_jsds.append(jsd(para_norm, B_STATIONARY))

    if bootstrap_jsds:
        bootstrap_jsds.sort()
        p95 = bootstrap_jsds[int(0.95 * len(bootstrap_jsds))]
        p99 = bootstrap_jsds[int(0.99 * len(bootstrap_jsds))]
        mean_jsd = sum(bootstrap_jsds) / len(bootstrap_jsds)
        # Where does ring text fall?
        rank = sum(1 for j in bootstrap_jsds if j < stationary_jsd) / len(bootstrap_jsds)
        print(f"  Bootstrap (n={len(bootstrap_jsds)} B paragraphs):")
        print(f"    Mean JSD: {mean_jsd:.4f}, 95th: {p95:.4f}, 99th: {p99:.4f}")
        print(f"    Ring text rank: {100*rank:.1f}th percentile")
        bootstrap_result = {
            'n_samples': len(bootstrap_jsds),
            'mean_jsd': round(mean_jsd, 5),
            'p95': round(p95, 5),
            'p99': round(p99, 5),
            'ring_percentile': round(100 * rank, 1),
        }
    else:
        bootstrap_result = None

    # Transition matrix details
    print(f"\n  Ring transition matrix (counts):")
    print(f"    {'':>8}", end="")
    for s in MACRO_STATES:
        print(f"  {s:>7}", end="")
    print()
    for from_s in MACRO_STATES:
        row_total = sum(ring_trans[from_s].values())
        print(f"    {from_s:>8}", end="")
        for to_s in MACRO_STATES:
            count = ring_trans[from_s].get(to_s, 0)
            print(f"  {count:>7}", end="")
        print(f"  (n={row_total})")

    return {
        'test': 'MACRO_STATE_TRANSITIONS',
        'constraint': 'C976, C978',
        'ring_mapped_tokens': ring_total,
        'ring_mapped_pct': round(100 * ring_total / max(sum(len(t) for t in ring_texts.values()), 1), 1),
        'ring_distribution': {s: round(ring_dist.get(s, 0) / max(ring_total, 1), 4) for s in MACRO_STATES},
        'b_stationary': B_STATIONARY,
        'jsd_ring_vs_b': round(stationary_jsd, 5),
        'ring_transition_matrix': {
            from_s: {to_s: ring_trans[from_s].get(to_s, 0) for to_s in MACRO_STATES}
            for from_s in MACRO_STATES
        },
        'bootstrap': bootstrap_result,
        'per_ring_counts': {pos: dict(Counter(states)) for pos, states in per_ring_states.items()},
    }


# ============================================================
# TIER 3: DISTRIBUTION COMPLIANCE
# ============================================================

def test_role_distribution(ring_texts, baselines):
    """Test 6: Compare role distribution to B corpus (C591)."""
    print("\n" + "="*70)
    print("TEST 6: Role Distribution (C591)")
    print("="*70)

    # Ring text roles
    ring_roles = Counter()
    ring_classified = 0
    ring_total = 0
    for tokens in ring_texts.values():
        for tok in tokens:
            ring_total += 1
            bc = tok.get('b_class')
            if bc is not None:
                ring_classified += 1
                role = CLASS_TO_ROLE.get(bc, 'UNKNOWN')
                ring_roles[role] += 1

    # B baseline roles
    b_roles = Counter()
    b_classified = 0
    for para in baselines['b_paragraphs']:
        for tok in para:
            bc = tok.get('b_class')
            if bc is not None:
                b_classified += 1
                role = CLASS_TO_ROLE.get(bc, 'UNKNOWN')
                b_roles[role] += 1

    # AZC roles
    azc_roles = Counter()
    azc_classified = 0
    for tok in baselines['azc_tokens']:
        bc = tok.get('b_class')
        if bc is not None:
            azc_classified += 1
            role = CLASS_TO_ROLE.get(bc, 'UNKNOWN')
            azc_roles[role] += 1

    all_roles = ['CC', 'EN', 'AX', 'FQ', 'FO']
    print(f"  Ring: {ring_classified}/{ring_total} classified ({100*ring_classified/max(ring_total,1):.1f}%)")
    print(f"  B baseline: {b_classified} classified")
    print(f"  AZC control: {azc_classified} classified")

    print(f"\n  {'Role':>6}  {'Ring':>8}  {'B base':>8}  {'B ref':>8}  {'AZC':>8}")
    print(f"  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}")
    for role in all_roles:
        r_pct = 100 * ring_roles.get(role, 0) / max(ring_classified, 1)
        b_pct = 100 * b_roles.get(role, 0) / max(b_classified, 1)
        ref_pct = 100 * B_ROLE_PROPORTIONS.get(role, 0)
        a_pct = 100 * azc_roles.get(role, 0) / max(azc_classified, 1)
        print(f"  {role:>6}  {r_pct:7.1f}%  {b_pct:7.1f}%  {ref_pct:7.1f}%  {a_pct:7.1f}%")

    return {
        'test': 'ROLE_DISTRIBUTION',
        'constraint': 'C591',
        'ring': {
            'n_classified': ring_classified,
            'n_total': ring_total,
            'pct_classified': round(100 * ring_classified / max(ring_total, 1), 1),
            'distribution': {r: round(ring_roles.get(r, 0) / max(ring_classified, 1), 4) for r in all_roles},
        },
        'b_baseline': {
            'n_classified': b_classified,
            'distribution': {r: round(b_roles.get(r, 0) / max(b_classified, 1), 4) for r in all_roles},
        },
        'b_reference': B_ROLE_PROPORTIONS,
        'azc_control': {
            'n_classified': azc_classified,
            'distribution': {r: round(azc_roles.get(r, 0) / max(azc_classified, 1), 4) for r in all_roles},
        },
    }


def test_affordance_bins(ring_texts, baselines):
    """Test 7: Compare affordance bin distribution (C995, C1097)."""
    print("\n" + "="*70)
    print("TEST 7: Affordance Bin Distribution (C995, C1097)")
    print("="*70)

    # Ring text bins
    ring_bins = Counter()
    ring_total = 0
    for tokens in ring_texts.values():
        for tok in tokens:
            ab = tok.get('affordance_bin')
            if ab:
                ring_bins[ab] += 1
                ring_total += 1

    # B baseline bins
    b_bins = Counter()
    b_total = 0
    for para in baselines['b_paragraphs']:
        for tok in para:
            ab = tok.get('affordance_bin')
            if ab:
                b_bins[ab] += 1
                b_total += 1

    # AZC bins
    azc_bins = Counter()
    azc_total = 0
    for tok in baselines['azc_tokens']:
        ab = tok.get('affordance_bin')
        if ab:
            azc_bins[ab] += 1
            azc_total += 1

    # All bins seen
    all_bins = sorted(set(list(ring_bins.keys()) + list(b_bins.keys()) + list(azc_bins.keys())))

    print(f"  Ring: {ring_total} tokens with bins")
    print(f"  B baseline: {b_total} tokens with bins")
    print(f"  AZC control: {azc_total} tokens with bins")

    print(f"\n  {'Bin':<25} {'Ring':>8} {'B base':>8} {'AZC':>8} {'Ring/B':>8}")
    print(f"  {'-'*25} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    enrichments = {}
    for ab in all_bins:
        r_pct = 100 * ring_bins.get(ab, 0) / max(ring_total, 1)
        b_pct = 100 * b_bins.get(ab, 0) / max(b_total, 1)
        a_pct = 100 * azc_bins.get(ab, 0) / max(azc_total, 1)
        ratio = r_pct / max(b_pct, 0.1)
        enrichments[ab] = round(ratio, 2)
        marker = " ***" if ratio > 1.5 or ratio < 0.5 else ""
        print(f"  {ab:<25} {r_pct:7.1f}% {b_pct:7.1f}% {a_pct:7.1f}% {ratio:7.2f}x{marker}")

    return {
        'test': 'AFFORDANCE_BIN_DISTRIBUTION',
        'constraint': 'C995, C1097',
        'ring': {
            'n_tokens': ring_total,
            'distribution': {ab: round(ring_bins.get(ab, 0) / max(ring_total, 1), 4) for ab in all_bins},
        },
        'b_baseline': {
            'n_tokens': b_total,
            'distribution': {ab: round(b_bins.get(ab, 0) / max(b_total, 1), 4) for ab in all_bins},
        },
        'azc_control': {
            'n_tokens': azc_total,
            'distribution': {ab: round(azc_bins.get(ab, 0) / max(azc_total, 1), 4) for ab in all_bins},
        },
        'enrichment_vs_b': enrichments,
    }


def test_prefix_lanes(ring_texts, baselines):
    """Test 8: PREFIX lane balance and evenness (C643, C647, C1098)."""
    print("\n" + "="*70)
    print("TEST 8: PREFIX Lane Balance & Evenness (C643, C647, C1098)")
    print("="*70)

    def compute_lane_stats(tokens_list):
        """Compute PREFIX distribution and evenness for a token list.
        Uses actual prefix strings for evenness (not lane/zone categories,
        which differ between unified JSON and BFolioDecoder)."""
        prefixes = Counter()
        for tok in tokens_list:
            p = tok.get('prefix')
            if p:
                prefixes[p] += 1
        total = sum(prefixes.values())
        # Shannon evenness over prefix types
        if total > 0 and len(prefixes) > 1:
            probs = [c / total for c in prefixes.values()]
            entropy = -sum(p * math.log2(p) for p in probs if p > 0)
            max_entropy = math.log2(len(prefixes))
            evenness = entropy / max_entropy if max_entropy > 0 else 0
        else:
            entropy = 0
            evenness = 0
        return {
            'prefixes': dict(prefixes.most_common()),
            'total': total,
            'n_prefix_types': len(prefixes),
            'evenness': round(evenness, 3),
            'entropy': round(entropy, 3),
        }

    # Ring text
    ring_flat = pool_ring_tokens(ring_texts)
    ring_stats = compute_lane_stats(ring_flat)

    # B baseline
    b_flat = [tok for para in baselines['b_paragraphs'] for tok in para]
    b_stats = compute_lane_stats(b_flat)

    # AZC
    azc_stats = compute_lane_stats(baselines['azc_tokens'])

    print(f"  PREFIX evenness (Shannon H / H_max):")
    print(f"    Ring text:  {ring_stats['evenness']:.3f} ({ring_stats['n_prefix_types']} types, {ring_stats['total']} tokens)")
    print(f"    B baseline: {b_stats['evenness']:.3f} ({b_stats['n_prefix_types']} types, {b_stats['total']} tokens)")
    print(f"    AZC control: {azc_stats['evenness']:.3f} ({azc_stats['n_prefix_types']} types, {azc_stats['total']} tokens)")
    print(f"    C1098 reference: Rosettes=0.791, B=0.738")

    # Top prefix comparison
    all_prefixes = sorted(set(list(ring_stats['prefixes'].keys()) + list(b_stats['prefixes'].keys())))
    print(f"\n  Top prefixes:")
    print(f"  {'Prefix':<8} {'Ring':>8} {'B base':>8} {'AZC':>8}")
    for prefix in sorted(ring_stats['prefixes'].keys(),
                         key=lambda x: ring_stats['prefixes'].get(x, 0), reverse=True)[:10]:
        r_pct = 100 * ring_stats['prefixes'].get(prefix, 0) / max(ring_stats['total'], 1)
        b_pct = 100 * b_stats['prefixes'].get(prefix, 0) / max(b_stats['total'], 1)
        a_pct = 100 * azc_stats['prefixes'].get(prefix, 0) / max(azc_stats['total'], 1)
        print(f"  {prefix:<8} {r_pct:7.1f}% {b_pct:7.1f}% {a_pct:7.1f}%")

    return {
        'test': 'PREFIX_LANE_BALANCE',
        'constraint': 'C643, C647, C1098',
        'ring': ring_stats,
        'b_baseline': b_stats,
        'azc_control': azc_stats,
        'c1098_reference': {'rosettes_evenness': 0.791, 'b_evenness': 0.738},
    }


def test_b_class_coverage(ring_texts):
    """Test 9: B-class coverage rate (diagnostic)."""
    print("\n" + "="*70)
    print("TEST 9: B-Class Coverage Rate (diagnostic)")
    print("="*70)

    total = 0
    classified = 0
    per_ring = {}
    for pos, tokens in ring_texts.items():
        r_total = len(tokens)
        r_classified = sum(1 for t in tokens if t.get('b_class') is not None)
        total += r_total
        classified += r_classified
        per_ring[pos] = {
            'n_tokens': r_total,
            'n_classified': r_classified,
            'coverage_pct': round(100 * r_classified / max(r_total, 1), 1),
        }

    coverage = 100 * classified / max(total, 1)
    print(f"  Total ring text tokens: {total}")
    print(f"  B-class classified: {classified} ({coverage:.1f}%)")
    print(f"  C1088 full Rosettes: 64.7%")
    print(f"  B corpus: ~69.5% (HT/UN = 30.5% per C609)")

    for pos, data in per_ring.items():
        print(f"    {pos}: {data['n_classified']}/{data['n_tokens']} ({data['coverage_pct']:.1f}%)")

    return {
        'test': 'B_CLASS_COVERAGE',
        'constraint': 'C740, C1088',
        'n_total': total,
        'n_classified': classified,
        'coverage_pct': round(coverage, 1),
        'reference': {
            'c1088_full_rosettes': 64.7,
            'b_corpus_classified': 69.5,
        },
        'per_ring': per_ring,
    }


# ============================================================
# SUMMARY
# ============================================================

def compute_summary(t1, t2, t3, t4, t5, t6, t7, t8, t9):
    """Compute overall summary from all test results."""
    summary = {
        'tier1_construction': {
            'prefix_middle_violations': t1['n_violations'],
            'prefix_middle_verdict': t1['verdict'],
            'kernel_tokens_tested': t2['n_with_multi_kernel'],
            'suffix_bare_rate': t3['ring']['bare_pct'],
        },
        'tier2_transition': {
            'forbidden_eligible': t4['ring']['n_eligible'],
            'forbidden_violations': t4['ring']['n_violations'],
            'forbidden_violation_rate': t4['ring']['violation_rate'],
            'b_baseline_violation_rate': t4['b_baseline']['violation_rate'],
            'macro_jsd': t5['jsd_ring_vs_b'],
            'macro_bootstrap_percentile': t5.get('bootstrap', {}).get('ring_percentile'),
        },
        'tier3_distribution': {
            'b_class_coverage': t9['coverage_pct'],
            'prefix_evenness': t8['ring']['evenness'],
            'b_prefix_evenness': t8['b_baseline']['evenness'],
        },
    }

    # Overall verdict
    verdicts = []
    if t1['n_violations'] == 0:
        verdicts.append("PREFIX-MIDDLE construction: B-COMPLIANT")
    else:
        verdicts.append(f"PREFIX-MIDDLE construction: {t1['n_violations']} violations")

    if t4['ring']['n_eligible'] > 0:
        if abs(t4['ring']['violation_rate'] - t4['b_baseline']['violation_rate']) < 0.15:
            verdicts.append("Forbidden transitions: B-LIKE rate")
        else:
            verdicts.append(f"Forbidden transitions: DIFFERENT from B "
                          f"({100*t4['ring']['violation_rate']:.0f}% vs {100*t4['b_baseline']['violation_rate']:.0f}%)")
    else:
        verdicts.append("Forbidden transitions: insufficient eligible pairs")

    if t5.get('bootstrap', {}).get('ring_percentile', 0) < 95:
        verdicts.append("Macro-state distribution: WITHIN B range")
    else:
        verdicts.append("Macro-state distribution: OUTSIDE B range")

    summary['verdicts'] = verdicts
    return summary


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 397: Rosettes Ring Text Grammar Test")
    print("="*70)

    # Load data
    print("\nLoading data...")
    data = load_data()
    ring_texts = extract_ring_texts(data['unified'])
    total_tokens = sum(len(t) for t in ring_texts.values())
    print(f"Ring texts: {len(ring_texts)} regions, {total_tokens} tokens")
    for pos, tokens in ring_texts.items():
        print(f"  {pos}: {len(tokens)} tokens")

    # Build baselines
    baselines = build_b_baselines()

    # Tier 1: Construction
    print("\n" + "#"*70)
    print("# TIER 1: CONSTRUCTION COMPLIANCE")
    print("#"*70)
    t1 = test_prefix_middle_selectivity(ring_texts, data['forbidden_pm'])
    t2 = test_kernel_construction(ring_texts)
    t3 = test_suffix_distribution(ring_texts, baselines)

    # Tier 2: Transition
    print("\n" + "#"*70)
    print("# TIER 2: TRANSITION COMPLIANCE")
    print("#"*70)
    t4 = test_forbidden_transitions(ring_texts, data['forbidden_middle_pairs'], baselines)
    t5 = test_macro_state_transitions(ring_texts, baselines)

    # Tier 3: Distribution
    print("\n" + "#"*70)
    print("# TIER 3: DISTRIBUTION COMPLIANCE")
    print("#"*70)
    t6 = test_role_distribution(ring_texts, baselines)
    t7 = test_affordance_bins(ring_texts, baselines)
    t8 = test_prefix_lanes(ring_texts, baselines)
    t9 = test_b_class_coverage(ring_texts)

    # Summary
    summary = compute_summary(t1, t2, t3, t4, t5, t6, t7, t8, t9)

    print("\n" + "#"*70)
    print("# SUMMARY")
    print("#"*70)
    for v in summary['verdicts']:
        print(f"  -> {v}")

    # Save results
    results = {
        'metadata': {
            'phase': 397,
            'name': 'ROSETTES_RING_TEXT_GRAMMAR',
            'n_ring_texts': len(ring_texts),
            'total_ring_tokens': total_tokens,
            'rings': {pos: len(tokens) for pos, tokens in ring_texts.items()},
            'n_b_baseline_paragraphs': len(baselines['b_paragraphs']),
            'n_azc_control_tokens': len(baselines['azc_tokens']),
        },
        'tier1_construction': {
            'test1_prefix_middle_selectivity': t1,
            'test2_kernel_construction': t2,
            'test3_suffix_distribution': t3,
        },
        'tier2_transition': {
            'test4_forbidden_transitions': t4,
            'test5_macro_state_transitions': t5,
        },
        'tier3_distribution': {
            'test6_role_distribution': t6,
            'test7_affordance_bins': t7,
            'test8_prefix_lanes': t8,
            'test9_b_class_coverage': t9,
        },
        'summary': summary,
    }

    out_path = PROJECT / 'phases' / 'ROSETTES_RING_TEXT_GRAMMAR' / 'results' / 'ring_text_grammar_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
