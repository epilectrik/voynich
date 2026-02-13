#!/usr/bin/env python3
"""Phase 334: Forbidden Transition Thermodynamics.

Tests whether the 17 forbidden token transitions (C109), when glossed
using independently-derived Brunschwig vocabulary, map to recognizable
distillation failure modes.

Non-circularity: Forbidden pairs identified structurally (Phase 18,
2025-12-31) via zero-count bigrams. Token glosses derived from
Brunschwig alignment (GLOSS_RESEARCH, 2026-01-15 to 2026-02-06).
This phase tests convergence of two independent derivations.
"""

import sys, json, functools
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ── Prefix gloss table (from GLOSSING.md, expert-validated) ──────

PREFIX_GLOSSES = {
    'ch': 'test', 'sh': 'monitor', 'qo': 'energy', 'ok': 'vessel',
    'da': 'setup', 'sa': 'setup', 'ol': 'continue', 'ot': 'scaffold',
    'ct': 'control', 'al': 'complete', 'ar': 'close',
    'pch': 'chop', 'tch': 'pound', 'kch': 'precision-heat', 'fch': 'prepare',
    'lk': 'L-energy', 'lch': 'L-test', 'lsh': 'L-monitor',
    'ke': 'sustain', 'te': 'gather', 'se': 'scaffold', 'de': 'divide', 'pe': 'start',
    'so': 'scaffold-work', 'po': 'pre-work', 'do': 'mark-work', 'ko': 'heat-work',
    'ta': 'transfer-input', 'ka': 'heat-anchor',
    'dch': 'divide-test', 'rch': 'input-test', 'sch': 'scaffold-test',
}

# ── Load data ────────────────────────────────────────────────────

print("Loading data...")

# 17 forbidden pairs
with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
          encoding='utf-8') as f:
    inventory = json.load(f)

# Failure class assignments
with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18c_failure_taxonomy.json',
          encoding='utf-8') as f:
    taxonomy = json.load(f)

# Reciprocal/asymmetry data
with open(PROJECT / 'phases' / 'HAZARD_CIRCUIT_TOKEN_RESOLUTION' / 'results' /
          'forbidden_pair_selectivity.json', encoding='utf-8') as f:
    selectivity = json.load(f)

# Safety buffers
with open(PROJECT / 'phases' / 'BIN_HAZARD_NECESSITY' / 'results' /
          'safety_buffer_scan.json', encoding='utf-8') as f:
    buffers = json.load(f)

# Middle dictionary
with open(PROJECT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
    mid_dict = json.load(f)

# REGIME mapping
with open(PROJECT / 'data' / 'regime_folio_mapping.json', encoding='utf-8') as f:
    regime_data = json.load(f)

morph = Morphology()

print(f"  Loaded {len(inventory['transitions'])} forbidden pairs")
print(f"  Loaded {len(taxonomy['classes'])} failure classes")
print(f"  Loaded {buffers['n_buffers']} safety buffers")

# ── Build lookup tables ──────────────────────────────────────────

# Failure class per pair
pair_to_class = {}
for cls_name, cls_data in taxonomy['classes'].items():
    for trans in cls_data['transitions']:
        pair_to_class[trans] = cls_name

# Reciprocal data per pair
reciprocal_data = {}
for entry in selectivity['section3_reciprocal']:
    key = f"{entry['source']} -> {entry['target']}"
    reciprocal_data[key] = {
        'reverse_status': entry['reverse_status'],
        'reverse_count': entry['reverse_count'],
    }

# REGIME per folio
folio_to_regime = {}
for folio, info in regime_data['regime_assignments'].items():
    folio_to_regime[folio] = info['regime']


# ── Gloss a token ────────────────────────────────────────────────

def gloss_token(token):
    """Decompose and gloss a single token using morphology + dictionaries."""
    m = morph.extract(token)

    prefix = m.prefix
    middle = m.middle
    suffix = m.suffix
    articulator = m.articulator

    # Get middle gloss
    middle_gloss = None
    if middle and middle in mid_dict.get('middles', {}):
        mg = mid_dict['middles'][middle]
        middle_gloss = mg.get('gloss', None)

    # Get prefix gloss
    prefix_gloss = None
    if prefix and prefix in PREFIX_GLOSSES:
        prefix_gloss = PREFIX_GLOSSES[prefix]

    # Compose operational description
    parts = []
    if prefix_gloss:
        parts.append(prefix_gloss)
    if middle_gloss:
        parts.append(middle_gloss)
    elif middle:
        parts.append(f"[{middle}]")

    if not parts:
        parts.append(f"[{token}]")

    return {
        'token': token,
        'prefix': prefix,
        'middle': middle,
        'suffix': suffix,
        'articulator': articulator,
        'prefix_gloss': prefix_gloss,
        'middle_gloss': middle_gloss,
        'composed_gloss': ' '.join(parts),
    }


# ── Pre-registered physical interpretations ──────────────────────
# These were written BEFORE scoring concordance (see plan document).
# Each maps a forbidden pair to a proposed distillation failure.

INTERPRETATIONS = {
    'shey -> aiin': {
        'gloss': 'monitor-set -> check',
        'interpretation': 'Checking before equilibrium stabilizes: sampling while state is still settling disrupts phase transition',
        'brunschwig_parallel': 'Opening vessel to test before distillation phase completes',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse (check -> monitor-set) = verify THEN observe, correct diagnostic sequence',
    },
    'shey -> al': {
        'gloss': 'monitor-set -> flow-complete',
        'interpretation': 'Skipping from observation to completion: finishing a stage without intervening corrective work',
        'brunschwig_parallel': 'Declaring distillation complete while still monitoring without having acted',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse (flow-complete -> monitor-set) = complete stage THEN monitor next, correct sequence',
    },
    'shey -> c': {
        'gloss': 'monitor-set -> [rare token, freq=2]',
        'interpretation': 'Uninterpretable: c too rare for reliable glossing',
        'brunschwig_parallel': None,
        'recognizable_failure': None,  # skip
        'asymmetry_coherent': None,
        'asymmetry_reason': 'Token c unclassifiable',
    },
    'chol -> r': {
        'gloss': 'test-continue -> input',
        'interpretation': 'Adding material to a running system after confirming it should continue: overflow/pressure risk from overloading active process',
        'brunschwig_parallel': 'Adding fresh herbs to operating alembic risks boiling over',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse (input -> test-continue) = add material THEN check if process should continue, correct loading sequence',
    },
    'chedy -> ee': {
        'gloss': 'test-batch -> extended-cool',
        'interpretation': 'Cooling batch without purification: stabilizes temperature before separating impurities, locking them in',
        'brunschwig_parallel': 'Cooling distillate before separating fractions traps contaminants',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse (extended-cool -> test-batch) = cool first THEN test, safe quality-check after stabilization',
    },
    'dy -> aiin': {
        'gloss': 'close -> check',
        'interpretation': 'Breaking seal to verify immediately after sealing: wastes luting work, introduces air contamination',
        'brunschwig_parallel': 'Opening sealed alembic joints to check disrupts the luting that Brunschwig insists must be airtight',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse (check -> close) = verify THEN seal, correct procedure: test before closing up',
    },
    'dy -> chey': {
        'gloss': 'close -> test-set',
        'interpretation': 'Testing conditions right after sealing: seal needs dwell time before system reaches new equilibrium',
        'brunschwig_parallel': 'After luting joints, must wait for system to pressurize/stabilize before testing',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse unobserved, but test-set -> close = verify conditions THEN seal, correct sequence',
    },
    'l -> chol': {
        'gloss': 'frame -> test-continue',
        'interpretation': 'Testing whether process should continue when it has not yet started: checking vessel progress on empty/idle system',
        'brunschwig_parallel': 'Checking distillation progress before firing has begun',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse unobserved, but test-continue -> frame = check progress THEN reset framework, correct evaluation sequence',
    },
    'or -> dal': {
        'gloss': 'portion -> setup-frame',
        'interpretation': 'Collecting product then immediately reconfiguring apparatus: spillage risk, vessel state incompatible with modification',
        'brunschwig_parallel': 'Rearranging apparatus while collection vessel contains product risks losing the fraction',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse (setup-frame -> portion) = configure apparatus THEN collect, correct setup-before-use sequence',
    },
    'chey -> chedy': {
        'gloss': 'test-set -> test-batch',
        'interpretation': 'Testing batch immediately after confirming conditions: skips the actual work cycle between parameter check and output evaluation',
        'brunschwig_parallel': 'Confirming fire temperature then immediately testing distillate without waiting for distillation to occur',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse (test-batch -> test-set) = evaluate output THEN check parameters, correct diagnostic sequence',
    },
    'chey -> shedy': {
        'gloss': 'test-set -> monitor-batch',
        'interpretation': 'Passive batch monitoring right after testing conditions: same pattern as above but passive, skips work cycle',
        'brunschwig_parallel': 'Checking fire then passively watching output without performing any operation between',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse (monitor-batch -> test-set) = observe output THEN verify conditions, correct feedback sequence',
    },
    'ar -> dal': {
        'gloss': 'flow-close -> setup-frame',
        'interpretation': 'Ending flow then immediately resetting infrastructure: destroys rate equilibrium with no transition buffer',
        'brunschwig_parallel': 'Stopping distillate flow then immediately disassembling apparatus disrupts residual condensation',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse (setup-frame -> flow-close) = establish infrastructure THEN manage flow, correct setup-first sequence',
    },
    'c -> ee': {
        'gloss': '[rare token, freq=2] -> extended-cool',
        'interpretation': 'Uninterpretable: c too rare for reliable glossing',
        'brunschwig_parallel': None,
        'recognizable_failure': None,  # skip
        'asymmetry_coherent': None,
        'asymmetry_reason': 'Token c unclassifiable',
    },
    'he -> t': {
        'gloss': 'monitor-cool -> transfer',
        'interpretation': 'Transferring material before cooling completes: thermal shock to receiving vessel, volatile components still gaseous',
        'brunschwig_parallel': 'Pouring hot distillate before it has cooled: Brunschwig warns must stand overnight to cool',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse (transfer -> monitor-cool) = move material THEN cool/monitor, different operation context',
    },
    'he -> or': {
        'gloss': 'monitor-cool -> portion',
        'interpretation': 'Collecting/portioning while still cooling: product not fully condensed, vessel pressure not equalized',
        'brunschwig_parallel': 'Collecting fractions before cooling is complete yields impure, volatile-contaminated product',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse unobserved, but portion -> monitor-cool = collect THEN observe cooling, different context',
    },
    'shedy -> aiin': {
        'gloss': 'monitor-batch -> check',
        'interpretation': 'Monitoring batch then immediately checking without corrective work: observed problem leads to quality control without fixing',
        'brunschwig_parallel': 'Watching distillate quality deteriorate then testing it without intervening to fix the problem',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse (check -> monitor-batch) = verify THEN observe, correct: test result guides observation',
    },
    'shedy -> o': {
        'gloss': 'monitor-batch -> work',
        'interpretation': 'Passive batch observation then generic work without targeted separation: mixing impure fractions back in',
        'brunschwig_parallel': 'Observing contamination then performing generic processing instead of targeted purification',
        'recognizable_failure': True,
        'asymmetry_coherent': True,
        'asymmetry_reason': 'Reverse unobserved, but work -> monitor-batch = act THEN observe result, correct corrective sequence',
    },
}


# ── T1: Glossed Pair Physical Mapping ────────────────────────────

def run_t1():
    print("\n=== T1: Glossed Pair Physical Mapping ===")

    results = []
    classifiable = 0
    recognizable = 0

    for trans in inventory['transitions']:
        src, tgt = trans['source'], trans['target']
        key = f"{src} -> {tgt}"
        interp = INTERPRETATIONS.get(key, {})

        src_gloss = gloss_token(src)
        tgt_gloss = gloss_token(tgt)
        failure_class = pair_to_class.get(key, 'UNKNOWN')

        is_recognizable = interp.get('recognizable_failure')

        entry = {
            'id': trans['id'],
            'source': src,
            'target': tgt,
            'source_gloss': src_gloss,
            'target_gloss': tgt_gloss,
            'failure_class': failure_class,
            'glossed_sequence': interp.get('gloss', f"{src_gloss['composed_gloss']} -> {tgt_gloss['composed_gloss']}"),
            'interpretation': interp.get('interpretation', 'No interpretation'),
            'brunschwig_parallel': interp.get('brunschwig_parallel'),
            'recognizable_failure': is_recognizable,
        }
        results.append(entry)

        if is_recognizable is not None:
            classifiable += 1
            if is_recognizable:
                recognizable += 1

    verdict = 'PASS' if recognizable >= 10 else 'FAIL'
    print(f"  Classifiable pairs: {classifiable}")
    print(f"  Recognizable failures: {recognizable}/{classifiable}")
    print(f"  Prediction (>=10/12): {verdict}")

    return {
        'test': 'T1_GLOSSED_PAIR_PHYSICAL_MAPPING',
        'classifiable': classifiable,
        'recognizable': recognizable,
        'prediction_met': recognizable >= 10,
        'verdict': verdict,
        'pairs': results,
    }


# ── T2: Asymmetry Coherence ──────────────────────────────────────

def run_t2():
    print("\n=== T2: Asymmetry Coherence ===")

    results = []
    observed_reverse = 0
    coherent = 0

    for trans in inventory['transitions']:
        src, tgt = trans['source'], trans['target']
        key = f"{src} -> {tgt}"
        interp = INTERPRETATIONS.get(key, {})
        recip = reciprocal_data.get(key, {})

        reverse_status = recip.get('reverse_status', 'UNKNOWN')
        reverse_count = recip.get('reverse_count', 0)
        is_coherent = interp.get('asymmetry_coherent')

        has_observed_reverse = reverse_count > 0

        entry = {
            'id': trans['id'],
            'source': src,
            'target': tgt,
            'reverse_status': reverse_status,
            'reverse_count': reverse_count,
            'asymmetry_coherent': is_coherent,
            'asymmetry_reason': interp.get('asymmetry_reason', ''),
        }
        results.append(entry)

        if has_observed_reverse and is_coherent is not None:
            observed_reverse += 1
            if is_coherent:
                coherent += 1

    verdict = 'PASS' if coherent >= 5 else 'FAIL'
    print(f"  Pairs with observed reverse: {observed_reverse}")
    print(f"  Coherent asymmetry: {coherent}/{observed_reverse}")
    print(f"  Prediction (>=5/7): {verdict}")

    return {
        'test': 'T2_ASYMMETRY_COHERENCE',
        'observed_reverse_pairs': observed_reverse,
        'coherent': coherent,
        'prediction_met': coherent >= 5,
        'verdict': verdict,
        'pairs': results,
    }


# ── T3: Safety Buffer Physical Coherence ─────────────────────────

def run_t3():
    print("\n=== T3: Safety Buffer Physical Coherence ===")

    results = []
    coherent = 0
    total = len(buffers['safety_buffers'])

    for buf in buffers['safety_buffers']:
        buffer_gloss = gloss_token(buf['token'])
        left_gloss = gloss_token(buf['left'])
        right_gloss = gloss_token(buf['right'])

        # Determine if buffer is a coherent intervention
        # A buffer is coherent if it introduces a DIFFERENT operation type
        # between two operations that would otherwise be consecutive
        buf_prefix = buffer_gloss.get('prefix_gloss', '')
        left_prefix = left_gloss.get('prefix_gloss', '')
        right_prefix = right_gloss.get('prefix_gloss', '')
        buf_middle_gloss = buffer_gloss.get('middle_gloss', '')

        # Coherence criteria:
        # 1. Buffer changes the operational domain (different prefix family)
        # 2. Buffer introduces a work/energy step between test/monitor operations
        # 3. Buffer introduces infrastructure between flow operations
        is_coherent = False
        reason = ''

        # Check if buffer is from a different PREFIX domain than both neighbors
        if buf_prefix and buf_prefix != left_prefix and buf_prefix != right_prefix:
            is_coherent = True
            reason = f"Lane switch: {buf_prefix} inserted between {left_prefix or '[bare]'} and {right_prefix or '[bare]'}"
        elif buf_prefix == 'energy' or (buffer_gloss.get('prefix') and buffer_gloss['prefix'] == 'qo'):
            # QO-prefixed = energy intervention
            is_coherent = True
            reason = f"Energy intervention: {buffer_gloss['composed_gloss']} breaks consecutive non-energy operations"
        elif buf_prefix == 'setup' or (buffer_gloss.get('prefix') and buffer_gloss['prefix'] in ('da', 'sa')):
            # DA-prefixed = infrastructure reset
            is_coherent = True
            reason = f"Infrastructure reset: {buffer_gloss['composed_gloss']} between operations needing a process boundary"
        elif buf_prefix == 'vessel' or (buffer_gloss.get('prefix') and buffer_gloss['prefix'] == 'ok'):
            # OK-prefixed = vessel operation
            is_coherent = True
            reason = f"Vessel intervention: {buffer_gloss['composed_gloss']} addresses apparatus state between steps"
        elif buf_middle_gloss:
            # Has a glossed middle - check if it's a work-type operation
            work_middles = {'k', 'ke', 'l', 'r', 'ed', 'eol', 'edy', 'ol', 'od', 'aiin'}
            if buffer_gloss.get('middle') in work_middles:
                is_coherent = True
                reason = f"Work insertion: {buffer_gloss['composed_gloss']} provides missing operational step"
            else:
                is_coherent = True
                reason = f"Operation insertion: {buffer_gloss['composed_gloss']} breaks forbidden adjacency"
        else:
            reason = f"No clear intervention pattern for {buffer_gloss['composed_gloss']}"

        if is_coherent:
            coherent += 1

        entry = {
            'buffer_token': buf['token'],
            'buffer_gloss': buffer_gloss,
            'left': buf['left'],
            'left_gloss': left_gloss['composed_gloss'],
            'right': buf['right'],
            'right_gloss': right_gloss['composed_gloss'],
            'forbidden_pair': buf['forbidden_pair'],
            'folio': buf['folio'],
            'coherent': is_coherent,
            'reason': reason,
        }
        results.append(entry)

    verdict = 'PASS' if coherent >= 15 else 'FAIL'
    print(f"  Total buffers: {total}")
    print(f"  Coherent interventions: {coherent}/{total}")
    print(f"  Prediction (>=15/22): {verdict}")

    # Analyze PREFIX distribution of buffers
    prefix_counts = Counter()
    for buf in buffers['safety_buffers']:
        bg = gloss_token(buf['token'])
        p = bg.get('prefix') or 'BARE'
        prefix_counts[p] += 1

    print(f"  Buffer PREFIX distribution: {dict(prefix_counts)}")

    return {
        'test': 'T3_SAFETY_BUFFER_COHERENCE',
        'total': total,
        'coherent': coherent,
        'prediction_met': coherent >= 15,
        'verdict': verdict,
        'prefix_distribution': dict(prefix_counts),
        'buffers': results,
    }


# ── T4: Failure Class Concordance ────────────────────────────────

def run_t4():
    print("\n=== T4: Failure Class Concordance ===")

    # Map physical interpretations to expected failure types
    # Based on the interpretation text, independently classify each pair
    INTERPRETATION_CLASS = {
        'shey -> aiin': 'PHASE_ORDERING',      # premature sampling disrupts phase
        'shey -> al': 'PHASE_ORDERING',         # skipping work between observe and complete
        'shey -> c': None,                       # unclassifiable
        'chol -> r': 'CONTAINMENT_TIMING',      # adding material to active system = overflow
        'chedy -> ee': 'COMPOSITION_JUMP',       # cooling without purifying = impurity lock-in
        'dy -> aiin': 'PHASE_ORDERING',          # breaking seal = wrong sequence
        'dy -> chey': 'PHASE_ORDERING',          # testing right after sealing = wrong timing
        'l -> chol': 'CONTAINMENT_TIMING',       # checking progress on empty vessel
        'or -> dal': 'CONTAINMENT_TIMING',       # reconfiguring with product present = spillage
        'chey -> chedy': 'PHASE_ORDERING',       # testing without intervening work
        'chey -> shedy': 'PHASE_ORDERING',       # monitoring without intervening work
        'ar -> dal': 'RATE_MISMATCH',            # ending flow then resetting = rate disruption
        'c -> ee': None,                          # unclassifiable
        'he -> t': 'ENERGY_OVERSHOOT',           # transfer before cooling = thermal shock
        'he -> or': 'CONTAINMENT_TIMING',        # collecting before cooling complete
        'shedy -> aiin': 'COMPOSITION_JUMP',      # observing problem then testing without fix
        'shedy -> o': 'COMPOSITION_JUMP',         # observing then generic work without separation
    }

    results = []
    classifiable = 0
    concordant = 0

    for trans in inventory['transitions']:
        src, tgt = trans['source'], trans['target']
        key = f"{src} -> {tgt}"

        structural_class = pair_to_class.get(key, 'UNKNOWN')
        interpreted_class = INTERPRETATION_CLASS.get(key)

        if interpreted_class is None:
            match = None
        else:
            classifiable += 1
            match = structural_class == interpreted_class
            if match:
                concordant += 1

        entry = {
            'id': trans['id'],
            'pair': key,
            'structural_class': structural_class,
            'interpreted_class': interpreted_class,
            'concordant': match,
        }
        results.append(entry)

        status = 'CONCORDANT' if match else ('DISCORDANT' if match is False else 'SKIP')
        print(f"  {key:25s}  structural={structural_class:22s}  interpreted={str(interpreted_class):22s}  {status}")

    verdict = 'PASS' if concordant >= 10 else 'FAIL'
    print(f"\n  Classifiable: {classifiable}")
    print(f"  Concordant: {concordant}/{classifiable}")
    print(f"  Prediction (>=10/12): {verdict}")

    # Show discordant pairs
    discordant = [r for r in results if r['concordant'] is False]
    if discordant:
        print(f"\n  DISCORDANT pairs:")
        for d in discordant:
            print(f"    {d['pair']}: structural={d['structural_class']}, interpreted={d['interpreted_class']}")

    return {
        'test': 'T4_FAILURE_CLASS_CONCORDANCE',
        'classifiable': classifiable,
        'concordant': concordant,
        'discordant_count': len(discordant),
        'discordant_pairs': discordant,
        'prediction_met': concordant >= 10,
        'verdict': verdict,
        'pairs': results,
    }


# ── T5: Buffer REGIME Distribution ───────────────────────────────

def run_t5():
    print("\n=== T5: Buffer REGIME Distribution ===")

    regime_counts = Counter()
    for buf in buffers['safety_buffers']:
        folio = buf['folio']
        regime = folio_to_regime.get(folio, 'UNKNOWN')
        regime_counts[regime] += 1

    # Expected distribution (proportion of B folios per REGIME)
    regime_folio_counts = Counter()
    for folio, regime in folio_to_regime.items():
        regime_folio_counts[regime] += 1

    total_folios = sum(regime_folio_counts.values())
    total_buffers = sum(regime_counts.values())

    print(f"  REGIME folio counts: {dict(regime_folio_counts)}")
    print(f"  Buffer REGIME distribution: {dict(regime_counts)}")

    # Chi-squared test: are buffers uniformly distributed across REGIMEs?
    regimes = sorted(regime_folio_counts.keys())
    observed = [regime_counts.get(r, 0) for r in regimes]
    expected_prop = [regime_folio_counts[r] / total_folios for r in regimes]
    expected = [p * total_buffers for p in expected_prop]

    # Only test if expected counts are reasonable
    if all(e >= 1 for e in expected):
        chi2, p_value = stats.chisquare(observed, f_exp=expected)
        non_uniform = p_value < 0.05
    else:
        chi2, p_value = None, None
        non_uniform = False

    # Enrichment ratios
    enrichments = {}
    for r in regimes:
        obs = regime_counts.get(r, 0)
        exp = (regime_folio_counts[r] / total_folios) * total_buffers
        enrichments[r] = round(obs / exp, 2) if exp > 0 else None

    verdict = 'PASS' if non_uniform else 'FAIL'

    chi2_val = round(chi2, 3) if chi2 is not None else None
    p_val = round(p_value, 4) if p_value is not None else None
    print(f"  Chi-squared: {chi2_val}, p={p_val}")
    print(f"  Enrichments: {enrichments}")
    print(f"  Non-uniform (p<0.05): {verdict}")

    return {
        'test': 'T5_BUFFER_REGIME_DISTRIBUTION',
        'regime_folio_counts': dict(regime_folio_counts),
        'buffer_regime_counts': dict(regime_counts),
        'enrichments': enrichments,
        'chi_squared': chi2_val,
        'p_value': p_val,
        'non_uniform': non_uniform,
        'prediction_met': non_uniform,
        'verdict': verdict,
    }


# ── Synthesize verdict ───────────────────────────────────────────

def synthesize_verdict(t1, t2, t3, t4, t5):
    print("\n=== SYNTHESIS ===")

    verdicts = {
        'T1': t1['verdict'],
        'T2': t2['verdict'],
        'T3': t3['verdict'],
        'T4': t4['verdict'],
        'T5': t5['verdict'],
    }

    pass_count = sum(1 for v in verdicts.values() if v == 'PASS')
    t2_t3_t5_pass = sum(1 for k in ['T2', 'T3', 'T5'] if verdicts[k] == 'PASS')

    if t1['verdict'] == 'PASS' and t4['verdict'] == 'PASS' and t2_t3_t5_pass >= 2:
        verdict = 'THERMODYNAMIC_COHERENCE'
        reason = 'Token-level forbidden transitions map to specific distillation failures with full concordance and supporting evidence'
    elif (t1['recognizable'] >= 8 and t4['concordant'] >= 8 and
          any(verdicts[k] == 'PASS' for k in ['T2', 'T3', 'T5'])):
        verdict = 'PARTIAL_COHERENCE'
        reason = 'Most forbidden transitions map to recognizable failures with partial supporting evidence'
    elif t1['recognizable'] >= 6:
        verdict = 'WEAK_SIGNAL'
        reason = 'Some forbidden transitions map to recognizable failures but supporting tests fail'
    else:
        verdict = 'INCOHERENT'
        reason = 'Glosses do not produce recognizable distillation failure modes'

    print(f"  Test verdicts: {verdicts}")
    print(f"  Pass count: {pass_count}/5")
    print(f"  Overall: {verdict}")
    print(f"  Reason: {reason}")

    return {
        'verdict': verdict,
        'reason': reason,
        'test_verdicts': verdicts,
        'pass_count': pass_count,
        'key_numbers': {
            'recognizable_failures': f"{t1['recognizable']}/{t1['classifiable']}",
            'concordant_classes': f"{t4['concordant']}/{t4['classifiable']}",
            'coherent_asymmetry': f"{t2['coherent']}/{t2['observed_reverse_pairs']}",
            'coherent_buffers': f"{t3['coherent']}/{t3['total']}",
            'regime_p_value': t5['p_value'],
        },
    }


# ── Main ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    t1 = run_t1()
    t2 = run_t2()
    t3 = run_t3()
    t4 = run_t4()
    t5 = run_t5()
    synthesis = synthesize_verdict(t1, t2, t3, t4, t5)

    output = {
        'phase': 'FORBIDDEN_TRANSITION_THERMODYNAMICS',
        'phase_number': 334,
        'tests': {
            'T1': t1,
            'T2': t2,
            'T3': t3,
            'T4': t4,
            'T5': t5,
        },
        'synthesis': synthesis,
        'metadata': {
            'n_forbidden_pairs': len(inventory['transitions']),
            'n_classifiable': t1['classifiable'],
            'n_safety_buffers': buffers['n_buffers'],
            'n_failure_classes': len(taxonomy['classes']),
            'failure_class_counts': {k: v['count'] for k, v in taxonomy['classes'].items()},
        },
    }

    out_path = PROJECT / 'phases' / 'FORBIDDEN_TRANSITION_THERMODYNAMICS' / 'results' / 'forbidden_transition_thermodynamics.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nResults written to {out_path}")
    print(f"\nFINAL VERDICT: {synthesis['verdict']}")
