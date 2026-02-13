#!/usr/bin/env python3
"""Phase 335: PP MIDDLE Extension.

Tests whether the PP MIDDLE glossing frontier can be extended via
behavioral similarity, validates that auto-composed compound glosses
are behaviorally appropriate, and checks folio-level coherence.

Non-circularity: PP/RI classification (Phase A_INTERNAL_STRATIFICATION)
is from A/B presence. Behavioral signatures (affordance table) from
distributional statistics. Glosses from Brunschwig alignment + kernel
profiles. Folio boundaries are codicological. Hub sub-roles from
forbidden pair participation. Five independent derivation paths.

Tests:
  T1: PP inventory audit (descriptive)
  T2: Behavioral similarity validation (auto-composed vs atom)
  T3: Compound composition coherence (affordance bin agreement)
  T4: Folio thematic coherence (entropy vs shuffled baseline)
  T5: Hub sub-role gloss alignment (pre-registered mapping)
"""

import json
import sys
import functools
import random
import math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy import stats
from scipy.spatial.distance import cosine

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

from scripts.voynich import Morphology, Transcript, MiddleAnalyzer

# ── Constants ──────────────────────────────────────────────────

BEHAVIORAL_FEATURES = [
    'length', 'k_ratio', 'e_ratio', 'h_ratio', 'is_compound',
    'qo_affinity', 'regime_1_enrichment', 'regime_2_enrichment',
    'regime_3_enrichment', 'regime_4_enrichment', 'regime_entropy',
    'initial_rate', 'final_rate', 'folio_spread',
]

# Hub sub-role expected gloss categories (pre-registered)
HUB_ROLE_EXPECTED_GLOSSES = {
    'HAZARD_SOURCE': {
        'description': 'State-change ops that CREATE transitions',
        'keywords': ['close', 'seal', 'portion', 'set', 'continue', 'frame',
                     'flow-close', 'flow', 'sustain'],
    },
    'HAZARD_TARGET': {
        'description': 'Receiving ops vulnerable to disruption',
        'keywords': ['check', 'complete', 'extended-cool', 'work', 'input',
                     'transfer', 'cool', 'batch', 'settle'],
    },
    'SAFETY_BUFFER': {
        'description': 'Stabilization/energy intervention ops',
        'keywords': ['sustain-output', 'heat', 'collect', 'energy', 'output'],
    },
    'PURE_CONNECTOR': {
        'description': 'Neutral grammar connectors',
        'keywords': ['end', 'cool', 'extended-cool', 'precision', 'cool-open',
                     'iterate', 'break', 'open', 'checkpoint'],
    },
}

# ── Data Loading ───────────────────────────────────────────────

def load_data():
    """Load all required data files."""
    # PP MIDDLE list
    with open(PROJECT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' /
              'middle_classes.json', encoding='utf-8') as f:
        mc = json.load(f)
    pp_middles = set(mc['a_shared_middles'])

    # MIDDLE dictionary (glosses)
    with open(PROJECT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict = json.load(f)

    # Affordance table (behavioral signatures)
    with open(PROJECT / 'data' / 'middle_affordance_table.json', encoding='utf-8') as f:
        affordance = json.load(f)

    # Hub sub-role partition
    with open(PROJECT / 'phases' / 'HUB_ROLE_DECOMPOSITION' / 'results' /
              't1_hub_sub_role_partition.json', encoding='utf-8') as f:
        hub_data = json.load(f)

    return pp_middles, mid_dict, affordance, hub_data


def get_behavioral_vector(middle_entry):
    """Extract behavioral signature as numpy vector."""
    sig = middle_entry.get('behavioral_signature', {})
    vec = []
    for feat in BEHAVIORAL_FEATURES:
        val = sig.get(feat, 0.0)
        vec.append(float(val))
    return np.array(vec)


def compute_global_stats(affordance):
    """Compute global mean/std for z-scoring behavioral signatures."""
    all_vecs = []
    for mid, entry in affordance.get('middles', {}).items():
        vec = get_behavioral_vector(entry)
        all_vecs.append(vec)
    all_vecs = np.array(all_vecs)
    means = np.mean(all_vecs, axis=0)
    stds = np.std(all_vecs, axis=0)
    stds[stds == 0] = 1.0  # avoid division by zero
    return means, stds


def zscore_vec(vec, means, stds):
    """Z-score a behavioral vector."""
    return (vec - means) / stds


def cosine_sim(a, b):
    """Cosine similarity (1 - cosine distance). Returns 0 if either is zero."""
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return 1.0 - cosine(a, b)


# ── T1: PP Inventory Audit ─────────────────────────────────────

def run_t1(pp_middles, mid_dict, affordance, mid_analyzer):
    """Classify each PP MIDDLE: GLOSSED, AUTO_COMPOSABLE, FEATURES_ONLY, DARK."""
    print("\n=== T1: PP INVENTORY AUDIT ===")

    middles_data = mid_dict.get('middles', {})
    affordance_middles = affordance.get('middles', {})
    glossed_set = set()

    # Build set of MIDDLEs with persistent glosses
    for mid, entry in middles_data.items():
        if entry.get('gloss') is not None:
            glossed_set.add(mid)

    results = []
    counts = Counter()

    for mid in sorted(pp_middles):
        has_gloss = mid in glossed_set
        has_features = mid in affordance_middles

        # Check auto-composable: is compound with at least one glossed atom
        can_auto = False
        atom_source = None
        if not has_gloss and mid_analyzer.is_compound(mid):
            atoms = mid_analyzer.get_maximal_atoms(mid)
            for atom in atoms:
                if atom in glossed_set:
                    can_auto = True
                    atom_source = atom
                    break

        if has_gloss:
            category = 'GLOSSED'
        elif can_auto:
            category = 'AUTO_COMPOSABLE'
        elif has_features:
            category = 'FEATURES_ONLY'
        else:
            category = 'DARK'

        counts[category] += 1
        results.append({
            'middle': mid,
            'category': category,
            'has_gloss': has_gloss,
            'has_features': has_features,
            'can_auto_compose': can_auto,
            'atom_source': atom_source,
            'gloss': middles_data.get(mid, {}).get('gloss'),
        })

    total = len(pp_middles)
    reachable = counts['GLOSSED'] + counts['AUTO_COMPOSABLE']
    reachable_pct = 100.0 * reachable / total if total > 0 else 0

    print(f"  Total PP MIDDLEs: {total}")
    print(f"  GLOSSED: {counts['GLOSSED']}")
    print(f"  AUTO_COMPOSABLE: {counts['AUTO_COMPOSABLE']}")
    print(f"  FEATURES_ONLY: {counts['FEATURES_ONLY']}")
    print(f"  DARK: {counts['DARK']}")
    print(f"  Reachable (GLOSSED + AUTO): {reachable} ({reachable_pct:.1f}%)")

    prediction_met = reachable_pct >= 70.0
    verdict = 'PASS' if prediction_met else 'FAIL'
    print(f"  Prediction (>= 70%): {verdict}")

    return {
        'test': 'T1_PP_INVENTORY_AUDIT',
        'total_pp': total,
        'counts': dict(counts),
        'reachable': reachable,
        'reachable_pct': round(reachable_pct, 1),
        'prediction_met': prediction_met,
        'verdict': verdict,
        'details': results,
    }


# ── T2: Behavioral Similarity Validation ───────────────────────

def run_t2(t1_results, mid_dict, affordance):
    """Test: auto-composed MIDDLEs resemble their atoms more than random."""
    print("\n=== T2: BEHAVIORAL SIMILARITY VALIDATION ===")

    middles_data = mid_dict.get('middles', {})
    aff_middles = affordance.get('middles', {})

    # Compute global z-score parameters
    means, stds = compute_global_stats(affordance)

    # Get glossed MIDDLEs that have features (for random baseline)
    glossed_with_features = []
    for mid, entry in middles_data.items():
        if entry.get('gloss') is not None and mid in aff_middles:
            glossed_with_features.append(mid)

    # Get AUTO_COMPOSABLE entries from T1
    auto_entries = [e for e in t1_results['details'] if e['category'] == 'AUTO_COMPOSABLE']

    atom_sims = []
    random_sims = []
    pair_details = []

    for entry in auto_entries:
        compound = entry['middle']
        atom = entry['atom_source']

        # Both must be in affordance table
        if compound not in aff_middles or atom not in aff_middles:
            continue

        compound_vec = zscore_vec(get_behavioral_vector(aff_middles[compound]), means, stds)
        atom_vec = zscore_vec(get_behavioral_vector(aff_middles[atom]), means, stds)

        atom_sim = cosine_sim(compound_vec, atom_vec)

        # Random baseline: 100 random glossed MIDDLEs
        rand_sims_for_this = []
        candidates = [m for m in glossed_with_features if m != atom and m != compound]
        sample_size = min(100, len(candidates))
        if sample_size == 0:
            continue

        random.seed(42 + hash(compound))  # reproducible per compound
        sample = random.sample(candidates, sample_size)
        for rand_mid in sample:
            rand_vec = zscore_vec(get_behavioral_vector(aff_middles[rand_mid]), means, stds)
            rand_sims_for_this.append(cosine_sim(compound_vec, rand_vec))

        mean_rand = float(np.mean(rand_sims_for_this))
        atom_sims.append(atom_sim)
        random_sims.append(mean_rand)

        pair_details.append({
            'compound': compound,
            'atom': atom,
            'atom_similarity': round(atom_sim, 4),
            'random_similarity': round(mean_rand, 4),
            'delta': round(atom_sim - mean_rand, 4),
        })

    n_tested = len(atom_sims)
    if n_tested < 5:
        print(f"  Only {n_tested} testable pairs — insufficient data")
        return {
            'test': 'T2_BEHAVIORAL_SIMILARITY',
            'n_tested': n_tested,
            'verdict': 'INSUFFICIENT_DATA',
            'prediction_met': False,
        }

    mean_atom = float(np.mean(atom_sims))
    mean_random = float(np.mean(random_sims))

    # Paired t-test: atom_sim > random_sim
    t_stat, p_val = stats.ttest_rel(atom_sims, random_sims, alternative='greater')

    print(f"  Testable pairs: {n_tested}")
    print(f"  Mean atom similarity: {mean_atom:.4f}")
    print(f"  Mean random similarity: {mean_random:.4f}")
    print(f"  Delta: {mean_atom - mean_random:.4f}")
    print(f"  Paired t-test: t={t_stat:.3f}, p={p_val:.6f}")

    sim_pass = mean_atom >= 0.5
    stat_pass = p_val < 0.05
    verdict = 'PASS' if (sim_pass and stat_pass) else 'FAIL'

    print(f"  Mean >= 0.5: {'PASS' if sim_pass else 'FAIL'}")
    print(f"  p < 0.05: {'PASS' if stat_pass else 'FAIL'}")
    print(f"  Overall: {verdict}")

    return {
        'test': 'T2_BEHAVIORAL_SIMILARITY',
        'n_tested': n_tested,
        'mean_atom_similarity': round(mean_atom, 4),
        'mean_random_similarity': round(mean_random, 4),
        'delta': round(mean_atom - mean_random, 4),
        't_statistic': round(float(t_stat), 4),
        'p_value': round(float(p_val), 6),
        'sim_pass': sim_pass,
        'stat_pass': stat_pass,
        'verdict': verdict,
        'prediction_met': verdict == 'PASS',
        'pairs': sorted(pair_details, key=lambda x: -x['delta'])[:20],  # top 20
    }


# ── T3: Compound Composition Coherence ─────────────────────────

def run_t3(t1_results, affordance, mid_analyzer):
    """Test: compound affordance bins match at least one atom's bin."""
    print("\n=== T3: COMPOUND COMPOSITION COHERENCE ===")

    aff_middles = affordance.get('middles', {})

    # Get all compounds with features (GLOSSED or AUTO_COMPOSABLE that are compound)
    testable = []
    for entry in t1_results['details']:
        mid = entry['middle']
        if mid not in aff_middles:
            continue
        if not mid_analyzer.is_compound(mid):
            continue
        atoms = mid_analyzer.get_maximal_atoms(mid)
        # Need at least one atom in affordance table
        atoms_in_aff = [a for a in atoms if a in aff_middles]
        if not atoms_in_aff:
            continue
        testable.append((mid, atoms_in_aff))

    # Count bin sizes for chance calculation
    bin_counts = Counter()
    for mid, entry in aff_middles.items():
        b = entry.get('affordance_bin')
        if b is not None:
            bin_counts[b] += 1
    total_in_bins = sum(bin_counts.values())

    n_bins = len(bin_counts)
    # Chance of matching any one specific bin
    # For each compound, chance of matching at least one atom's bin
    # Approximate: 1/n_bins per atom, 1 - (1 - 1/n_bins)^n_atoms
    # Use simple 1/n_bins as conservative lower bound
    chance_rate = 1.0 / n_bins if n_bins > 0 else 0

    agreements = 0
    details = []
    for compound, atoms in testable:
        compound_bin = aff_middles[compound].get('affordance_bin')
        atom_bins = [aff_middles[a].get('affordance_bin') for a in atoms]

        match = compound_bin in atom_bins
        if match:
            agreements += 1

        details.append({
            'compound': compound,
            'compound_bin': compound_bin,
            'compound_label': aff_middles[compound].get('affordance_label', ''),
            'atoms': atoms,
            'atom_bins': atom_bins,
            'match': match,
        })

    n_tested = len(testable)
    if n_tested < 10:
        print(f"  Only {n_tested} testable compounds — insufficient data")
        return {
            'test': 'T3_COMPOUND_COHERENCE',
            'n_tested': n_tested,
            'verdict': 'INSUFFICIENT_DATA',
            'prediction_met': False,
        }

    agreement_rate = agreements / n_tested
    expected = chance_rate * n_tested

    # Chi-squared: observed agreements vs expected by chance
    # 2x2: match/no-match vs observed/expected
    observed = np.array([agreements, n_tested - agreements])
    expected_arr = np.array([expected, n_tested - expected])
    # Use binomial test instead (more appropriate for binary outcome)
    binom_result = stats.binomtest(agreements, n_tested, chance_rate, alternative='greater')
    binom_p = binom_result.pvalue

    print(f"  Testable compounds: {n_tested}")
    print(f"  Bin agreements: {agreements} ({100*agreement_rate:.1f}%)")
    print(f"  Chance rate: {100*chance_rate:.1f}% ({n_bins} bins)")
    print(f"  Expected by chance: {expected:.1f}")
    print(f"  Binomial test p: {binom_p:.6f}")

    rate_pass = agreement_rate >= 0.20
    stat_pass = binom_p < 0.05
    verdict = 'PASS' if (rate_pass and stat_pass) else 'FAIL'

    print(f"  Rate >= 20%: {'PASS' if rate_pass else 'FAIL'}")
    print(f"  p < 0.05: {'PASS' if stat_pass else 'FAIL'}")
    print(f"  Overall: {verdict}")

    return {
        'test': 'T3_COMPOUND_COHERENCE',
        'n_tested': n_tested,
        'agreements': agreements,
        'agreement_rate': round(agreement_rate, 4),
        'chance_rate': round(chance_rate, 4),
        'n_bins': n_bins,
        'binomial_p': round(float(binom_p), 6),
        'rate_pass': rate_pass,
        'stat_pass': stat_pass,
        'verdict': verdict,
        'prediction_met': verdict == 'PASS',
        'sample_matches': [d for d in details if d['match']][:10],
        'sample_mismatches': [d for d in details if not d['match']][:10],
    }


# ── T4: Folio Thematic Coherence ───────────────────────────────

def run_t4(t1_results, mid_dict):
    """Test: glossed folios have lower gloss entropy than shuffled baselines."""
    print("\n=== T4: FOLIO THEMATIC COHERENCE ===")

    middles_data = mid_dict.get('middles', {})
    morph = Morphology()
    tx = Transcript()

    # Build glossable set: MIDDLEs with glosses (persistent)
    glossable = set()
    for mid, entry in middles_data.items():
        if entry.get('gloss') is not None:
            glossable.add(mid)

    # Also add AUTO_COMPOSABLE from T1 (use atom's gloss)
    auto_map = {}  # compound -> atom source gloss
    for entry in t1_results['details']:
        if entry['category'] == 'AUTO_COMPOSABLE' and entry['atom_source']:
            atom_gloss = middles_data.get(entry['atom_source'], {}).get('gloss')
            if atom_gloss:
                auto_map[entry['middle']] = atom_gloss

    hub_middles = {
        'aiin', 'al', 'ar', 'd', 'dy', 'e', 'ee', 'eey', 'ek', 'eo',
        'eol', 'ey', 'iin', 'k', 'l', 'o', 'od', 'ol', 'or', 'r', 's', 't', 'y'
    }

    # Collect all B tokens by folio with their MIDDLE glosses
    folio_tokens = defaultdict(list)
    all_glosses = []  # corpus-wide for shuffling

    for token in tx.currier_b():
        m = morph.extract(token.word)
        mid = m.middle
        if not mid:
            continue

        gloss = None
        if mid in glossable:
            gloss = middles_data[mid]['gloss']
        elif mid in auto_map:
            gloss = auto_map[mid]

        is_hub = mid in hub_middles
        folio_tokens[token.folio].append({
            'gloss': gloss,
            'is_hub': is_hub,
        })
        if gloss:
            all_glosses.append(gloss)

    # Filter to folios with >= 90% glossable tokens
    eligible_folios = {}
    for folio, tokens in folio_tokens.items():
        glossed_count = sum(1 for t in tokens if t['gloss'] is not None)
        total = len(tokens)
        if total >= 10 and glossed_count / total >= 0.90:
            eligible_folios[folio] = tokens

    print(f"  Eligible folios (>= 90% glossable, >= 10 tokens): {len(eligible_folios)}")

    if len(eligible_folios) < 10:
        print("  Too few eligible folios — insufficient data")
        return {
            'test': 'T4_FOLIO_COHERENCE',
            'n_folios': len(eligible_folios),
            'verdict': 'INSUFFICIENT_DATA',
            'prediction_met': False,
        }

    def shannon_entropy(glosses):
        """Compute Shannon entropy of a gloss distribution."""
        if not glosses:
            return 0.0
        counts = Counter(glosses)
        total = len(glosses)
        ent = 0.0
        for c in counts.values():
            p = c / total
            if p > 0:
                ent -= p * math.log2(p)
        return ent

    random.seed(335)
    n_perms = 1000

    # Pre-compute no-hub gloss pool (OUTSIDE the loop)
    hub_gloss_set = {middles_data.get(h, {}).get('gloss') for h in hub_middles}
    hub_gloss_set.discard(None)
    nohub_gloss_pool = [g for g in all_glosses if g not in hub_gloss_set]

    # Compute coherence ratios
    coherence_all = []   # all glosses
    coherence_nohub = [] # excluding hubs

    folio_details = []

    for folio, tokens in sorted(eligible_folios.items()):
        # Real folio glosses
        real_glosses = [t['gloss'] for t in tokens if t['gloss']]
        real_nohub = [t['gloss'] for t in tokens if t['gloss'] and not t['is_hub']]

        real_ent = shannon_entropy(real_glosses)
        real_ent_nohub = shannon_entropy(real_nohub)

        n_tokens = len(real_glosses)
        n_nohub = len(real_nohub)

        # Shuffled baselines
        shuffled_ents = []
        shuffled_ents_nohub = []

        for _ in range(n_perms):
            # Draw n_tokens random glosses from corpus
            sample = random.choices(all_glosses, k=n_tokens)
            shuffled_ents.append(shannon_entropy(sample))

            if n_nohub > 0 and nohub_gloss_pool:
                sample_nh = random.choices(nohub_gloss_pool, k=n_nohub)
                shuffled_ents_nohub.append(shannon_entropy(sample_nh))

        mean_shuf = float(np.mean(shuffled_ents)) if shuffled_ents else 0
        mean_shuf_nh = float(np.mean(shuffled_ents_nohub)) if shuffled_ents_nohub else 0

        cr = mean_shuf / real_ent if real_ent > 0 else 1.0
        cr_nh = mean_shuf_nh / real_ent_nohub if real_ent_nohub > 0 else 1.0

        coherence_all.append(cr)
        if real_ent_nohub > 0:
            coherence_nohub.append(cr_nh)

        folio_details.append({
            'folio': folio,
            'n_tokens': n_tokens,
            'real_entropy': round(real_ent, 4),
            'shuffled_entropy': round(mean_shuf, 4),
            'coherence_ratio': round(cr, 4),
            'coherence_ratio_nohub': round(cr_nh, 4),
        })

    mean_cr = float(np.mean(coherence_all))
    mean_cr_nh = float(np.mean(coherence_nohub)) if coherence_nohub else 0

    # One-sample t-test: coherence_ratio > 1.0
    t_stat, p_val = stats.ttest_1samp(coherence_all, 1.0)
    # We want one-sided (greater than 1.0)
    p_one = p_val / 2 if t_stat > 0 else 1.0 - p_val / 2

    t_stat_nh, p_val_nh = (0, 1)
    p_one_nh = 1.0
    if len(coherence_nohub) >= 5:
        t_stat_nh, p_val_nh = stats.ttest_1samp(coherence_nohub, 1.0)
        p_one_nh = p_val_nh / 2 if t_stat_nh > 0 else 1.0 - p_val_nh / 2

    print(f"  Mean coherence ratio (all): {mean_cr:.4f}")
    print(f"  Mean coherence ratio (no hub): {mean_cr_nh:.4f}")
    print(f"  t-test (all): t={t_stat:.3f}, p(one-sided)={p_one:.6f}")
    if len(coherence_nohub) >= 5:
        print(f"  t-test (no hub): t={t_stat_nh:.3f}, p(one-sided)={p_one_nh:.6f}")

    ratio_pass = mean_cr >= 1.10
    stat_pass = p_one < 0.01
    verdict = 'PASS' if (ratio_pass and stat_pass) else 'FAIL'

    print(f"  Ratio >= 1.10: {'PASS' if ratio_pass else 'FAIL'}")
    print(f"  p < 0.01: {'PASS' if stat_pass else 'FAIL'}")
    print(f"  Overall: {verdict}")

    return {
        'test': 'T4_FOLIO_COHERENCE',
        'n_folios': len(eligible_folios),
        'n_permutations': n_perms,
        'mean_coherence_ratio': round(mean_cr, 4),
        'mean_coherence_ratio_nohub': round(mean_cr_nh, 4),
        't_statistic': round(float(t_stat), 4),
        'p_value_one_sided': round(float(p_one), 6),
        't_statistic_nohub': round(float(t_stat_nh), 4) if len(coherence_nohub) >= 5 else None,
        'p_value_nohub': round(float(p_one_nh), 6) if len(coherence_nohub) >= 5 else None,
        'ratio_pass': ratio_pass,
        'stat_pass': stat_pass,
        'verdict': verdict,
        'prediction_met': verdict == 'PASS',
        'folio_details': sorted(folio_details, key=lambda x: -x['coherence_ratio'])[:15],
    }


# ── T5: Hub Sub-Role Gloss Alignment ──────────────────────────

def run_t5(hub_data, mid_dict):
    """Test: hub MIDDLE glosses align with structural sub-roles."""
    print("\n=== T5: HUB SUB-ROLE GLOSS ALIGNMENT ===")

    middles_data = mid_dict.get('middles', {})
    primary_roles = hub_data.get('primary_roles', {})

    concordant = 0
    details = []

    for mid, role in sorted(primary_roles.items()):
        gloss = middles_data.get(mid, {}).get('gloss', '')
        if not gloss:
            gloss = f'[unglosed: {mid}]'

        expected = HUB_ROLE_EXPECTED_GLOSSES.get(role, {})
        keywords = expected.get('keywords', [])

        # Check if gloss matches any expected keyword
        gloss_lower = gloss.lower()
        match = any(kw.lower() in gloss_lower for kw in keywords)

        # Also check exact gloss match
        if not match:
            match = gloss_lower in [kw.lower() for kw in keywords]

        if match:
            concordant += 1

        details.append({
            'middle': mid,
            'primary_role': role,
            'gloss': gloss,
            'expected_category': expected.get('description', ''),
            'concordant': match,
        })

    total = len(primary_roles)
    print(f"  Hub MIDDLEs tested: {total}")
    print(f"  Concordant: {concordant}/{total}")

    for d in details:
        status = 'OK' if d['concordant'] else 'MISMATCH'
        print(f"    {d['middle']:6s} | {d['primary_role']:16s} | {d['gloss']:20s} | {status}")

    verdict = 'PASS' if concordant >= 15 else 'FAIL'
    print(f"  Prediction (>= 15/23): {verdict}")

    return {
        'test': 'T5_HUB_SUBROLE_ALIGNMENT',
        'total_hubs': total,
        'concordant': concordant,
        'concordance_rate': round(concordant / total, 4) if total > 0 else 0,
        'verdict': verdict,
        'prediction_met': concordant >= 15,
        'details': details,
    }


# ── Synthesis ──────────────────────────────────────────────────

def synthesize_verdict(t1, t2, t3, t4, t5):
    """Apply verdict gate logic."""
    print("\n=== SYNTHESIS ===")

    t1_pass = t1['verdict'] == 'PASS'
    t2_pass = t2['verdict'] == 'PASS'
    t3_pass = t3['verdict'] == 'PASS'
    t4_pass = t4['verdict'] == 'PASS'
    t5_pass = t5['verdict'] == 'PASS'

    others_pass = sum([t2_pass, t3_pass, t4_pass, t5_pass])

    if t1_pass and t2_pass and t4_pass and (t3_pass or t5_pass):
        verdict = 'PP_EXTENSION_VALIDATED'
    elif t1_pass and t2_pass and (t3_pass or t4_pass or t5_pass):
        verdict = 'PARTIAL_VALIDATION'
    elif t1_pass and others_pass >= 1:
        verdict = 'WEAK_SIGNAL'
    else:
        verdict = 'EXTENSION_UNSUPPORTED'

    print(f"  T1: {t1['verdict']}")
    print(f"  T2: {t2['verdict']}")
    print(f"  T3: {t3['verdict']}")
    print(f"  T4: {t4['verdict']}")
    print(f"  T5: {t5['verdict']}")
    print(f"  VERDICT: {verdict}")

    return {
        'verdict': verdict,
        'gate_results': {
            'T1': t1['verdict'],
            'T2': t2['verdict'],
            'T3': t3['verdict'],
            'T4': t4['verdict'],
            'T5': t5['verdict'],
        },
        'key_numbers': {
            'pp_reachable_pct': t1.get('reachable_pct'),
            'mean_atom_similarity': t2.get('mean_atom_similarity'),
            'compound_agreement_rate': t3.get('agreement_rate'),
            'mean_coherence_ratio': t4.get('mean_coherence_ratio'),
            'hub_concordance': f"{t5.get('concordant', 0)}/{t5.get('total_hubs', 0)}",
        },
    }


# ── Main ───────────────────────────────────────────────────────

def main():
    print("Phase 335: PP MIDDLE Extension")
    print("=" * 60)

    # Load data
    pp_middles, mid_dict, affordance, hub_data = load_data()
    print(f"Loaded {len(pp_middles)} PP MIDDLEs")

    # Build MiddleAnalyzer
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')
    summary = mid_analyzer.summary()
    print(f"MiddleAnalyzer: {summary['total_middles']} MIDDLEs, {summary['core_count']} core")

    # Run tests
    t1 = run_t1(pp_middles, mid_dict, affordance, mid_analyzer)
    t2 = run_t2(t1, mid_dict, affordance)
    t3 = run_t3(t1, affordance, mid_analyzer)
    t4 = run_t4(t1, mid_dict)
    t5 = run_t5(hub_data, mid_dict)

    # Synthesize
    synthesis = synthesize_verdict(t1, t2, t3, t4, t5)

    # Output
    output = {
        'phase': 'PP_MIDDLE_EXTENSION',
        'phase_number': 335,
        'tests': {
            'T1': t1,
            'T2': t2,
            'T3': t3,
            'T4': t4,
            'T5': t5,
        },
        'synthesis': synthesis,
        'metadata': {
            'pp_middles': len(pp_middles),
            'glossed_in_dict': t1['counts'].get('GLOSSED', 0),
            'affordance_entries': len(affordance.get('middles', {})),
            'hub_middles': len(hub_data.get('primary_roles', {})),
        },
    }

    out_path = PROJECT / 'phases' / 'PP_MIDDLE_EXTENSION' / 'results' / 'pp_middle_extension.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nResults saved to {out_path}")
    print(f"\nFINAL VERDICT: {synthesis['verdict']}")


if __name__ == '__main__':
    main()
