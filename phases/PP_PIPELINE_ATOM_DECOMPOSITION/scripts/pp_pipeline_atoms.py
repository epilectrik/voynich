"""Phase 408: PP Pipeline Architecture Closure + Dark Pipeline Atom Decomposition.

Verifies the 404 PP MIDDLE partition is exhaustive (85 bridge + 4 non-bridge
matched + 300 dark pipeline + 15 phantom = 404), then decomposes dark-pipeline
compound MIDDLEs into atoms to test whether bridge atoms appear inside them.

Tests:
  1. Partition closure: exhaustive, mutually exclusive 4-way split
  2. Atom inventory: decompose dark-pipeline compounds, classify atoms
  3. Atom pool overlap: Jaccard between grammar, dark, and all-B atom pools
  4. Atom-section structure: do shared atoms predict section concentration?
  5. Construction grammar: compare dark-pipeline bigrams to C1065 ordering
"""
import json
import sys
import math
import random
import os
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer


# --- Utility functions ---

def round_floats(obj, digits=4):
    """Recursively round floats in nested dicts/lists."""
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    return obj


def herfindahl(counts):
    """Herfindahl index (sum of squared shares). 1/N=uniform, 1.0=concentrated."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return sum((c / total) ** 2 for c in counts.values())


def jaccard(set_a, set_b):
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


# --- Data loading ---

def load_data():
    """Load all input files, build populations, MiddleAnalyzer, single B + A pass."""

    # 1. Load static data files
    with open(ROOT / 'phases/A_TO_B_ROLE_PROJECTION/results/pp_role_foundation.json',
              encoding='utf-8') as f:
        pp_role_data = json.load(f)

    with open(ROOT / 'phases/CROSS_SYSTEM_VOCABULARY_FLOW/results/ab_vocabulary_flow.json',
              encoding='utf-8') as f:
        vocab_flow = json.load(f)

    with open(ROOT / 'phases/BRIDGE_MIDDLE_SELECTION_MECHANISM/results/bridge_selection.json',
              encoding='utf-8') as f:
        bridge_data = json.load(f)

    with open(ROOT / 'phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t3_atom_bigram_grammar.json',
              encoding='utf-8') as f:
        c1065_data = json.load(f)

    # 2. Build population sets
    pp_role_map = pp_role_data['pp_role_map']
    all_pp_set = set(pp_role_map.keys())  # 404

    unmatched_pp_list = pp_role_data['unmatched_pp']  # 315
    b_absent_set = set(vocab_flow['b1']['b_absent_middles'])  # 15
    dark_pipeline_set = set(unmatched_pp_list) - b_absent_set  # 300

    matched_pp_set = set()
    for mid, info in pp_role_map.items():
        if info['n_classes'] > 0:
            matched_pp_set.add(mid)  # 89

    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])  # 85
    nonbridge_matched_set = matched_pp_set - bridge_set  # ~4

    # 3. Initialize MiddleAnalyzer
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')
    core_middles = mid_analyzer.get_core_middles()

    # 4. Initialize transcript and morphology
    tx = Transcript()
    morph = Morphology()

    # 5. Single pass over B tokens
    middle_b_freq = Counter()
    middle_b_folios = defaultdict(set)
    middle_section_freq = defaultdict(Counter)
    n_b_scanned = 0

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        n_b_scanned += 1
        m = morph.extract(word)
        mid = m.middle
        if mid:
            middle_b_freq[mid] += 1
            middle_b_folios[mid].add(token.folio)
            middle_section_freq[mid][token.section] += 1

    # 6. Single pass over A tokens (for phantom profiling)
    middle_a_freq = Counter()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        mid = m.middle
        if mid:
            middle_a_freq[mid] += 1

    print(f"Scanned {n_b_scanned} B tokens, {sum(middle_a_freq.values())} A tokens")
    print(f"  all_pp: {len(all_pp_set)}, bridge: {len(bridge_set)}, "
          f"matched_pp: {len(matched_pp_set)}, nonbridge_matched: {len(nonbridge_matched_set)}")
    print(f"  dark_pipeline: {len(dark_pipeline_set)}, b_absent: {len(b_absent_set)}")
    print(f"  Core MIDDLEs (B inventory): {len(core_middles)}")

    return {
        'all_pp_set': all_pp_set,
        'bridge_set': bridge_set,
        'matched_pp_set': matched_pp_set,
        'nonbridge_matched_set': nonbridge_matched_set,
        'dark_pipeline_set': dark_pipeline_set,
        'b_absent_set': b_absent_set,
        'pp_role_map': pp_role_map,
        'mid_analyzer': mid_analyzer,
        'core_middles': core_middles,
        'middle_b_freq': middle_b_freq,
        'middle_b_folios': middle_b_folios,
        'middle_section_freq': middle_section_freq,
        'middle_a_freq': middle_a_freq,
        'c1065_data': c1065_data,
        'n_b_scanned': n_b_scanned,
    }


# --- Test 1: PP Partition Closure ---

def test1_partition_closure(data):
    """Verify 404 PP partition is exhaustive and mutually exclusive."""
    all_pp = data['all_pp_set']
    bridge = data['bridge_set']
    nbm = data['nonbridge_matched_set']
    dark = data['dark_pipeline_set']
    absent = data['b_absent_set']
    pp_role_map = data['pp_role_map']
    mid_analyzer = data['mid_analyzer']
    middle_b_freq = data['middle_b_freq']
    middle_b_folios = data['middle_b_folios']
    middle_a_freq = data['middle_a_freq']

    # 1. Exhaustive check
    reconstructed = bridge | nbm | dark | absent
    partition_complete = (reconstructed == all_pp)
    total_check = len(bridge) + len(nbm) + len(dark) + len(absent)

    # 2. Mutual exclusivity
    pairs = [
        ('bridge', 'nonbridge_matched', bridge, nbm),
        ('bridge', 'dark_pipeline', bridge, dark),
        ('bridge', 'b_absent', bridge, absent),
        ('nonbridge_matched', 'dark_pipeline', nbm, dark),
        ('nonbridge_matched', 'b_absent', nbm, absent),
        ('dark_pipeline', 'b_absent', dark, absent),
    ]
    overlaps = {}
    all_disjoint = True
    for name_a, name_b, set_a, set_b in pairs:
        ov = len(set_a & set_b)
        overlaps[f"{name_a}_vs_{name_b}"] = ov
        if ov > 0:
            all_disjoint = False

    # 3. Profile non-bridge matched PPs
    nbm_profiles = {}
    for mid in sorted(nbm):
        info = pp_role_map[mid]
        nbm_profiles[mid] = {
            'b_classes': info['b_classes'],
            'n_classes': info['n_classes'],
            'dominant_role': info['dominant_role'],
            'b_token_count': middle_b_freq.get(mid, 0),
            'b_folio_count': len(middle_b_folios.get(mid, set())),
            'is_compound': mid_analyzer.is_compound(mid),
            'char_length': len(mid),
        }

    # 4. Profile B-absent phantoms
    phantom_profiles = {}
    for mid in sorted(absent):
        phantom_profiles[mid] = {
            'a_token_count': middle_a_freq.get(mid, 0),
            'is_compound': mid_analyzer.is_compound(mid),
            'char_length': len(mid),
            'atoms': mid_analyzer.get_maximal_atoms(mid) if mid_analyzer.is_compound(mid) else [],
        }

    phantom_compound_rate = sum(1 for m in absent if mid_analyzer.is_compound(m)) / len(absent) if absent else 0
    phantom_mean_a = sum(middle_a_freq.get(m, 0) for m in absent) / len(absent) if absent else 0
    phantom_mean_len = sum(len(m) for m in absent) / len(absent) if absent else 0

    # Common prefix patterns in phantoms
    phantom_prefixes = Counter()
    for mid in absent:
        if len(mid) >= 2:
            phantom_prefixes[mid[:2]] += 1

    # Verdict
    if partition_complete and all_disjoint and total_check == len(all_pp):
        verdict = 'PARTITION_COMPLETE'
    else:
        verdict = 'PARTITION_GAP'

    print(f"\nTest 1: PP Partition Closure")
    print(f"  Total PP MIDDLEs: {len(all_pp)}")
    print(f"  Bridge: {len(bridge)}, Non-bridge matched: {len(nbm)}, "
          f"Dark pipeline: {len(dark)}, B-absent: {len(absent)}")
    print(f"  Sum: {total_check} (expect {len(all_pp)})")
    print(f"  Exhaustive: {partition_complete}, Disjoint: {all_disjoint}")
    print(f"  Non-bridge matched: {sorted(nbm)}")
    print(f"  Phantom prefix pattern: {dict(phantom_prefixes)}")
    print(f"  Verdict: {verdict}")

    return {
        'partition_counts': {
            'all_pp': len(all_pp),
            'bridge': len(bridge),
            'nonbridge_matched': len(nbm),
            'dark_pipeline': len(dark),
            'b_absent': len(absent),
            'sum': total_check,
        },
        'partition_complete': partition_complete,
        'all_disjoint': all_disjoint,
        'pairwise_overlaps': overlaps,
        'nonbridge_matched_profiles': nbm_profiles,
        'phantom_profiles': phantom_profiles,
        'phantom_summary': {
            'compound_rate': phantom_compound_rate,
            'mean_a_token_count': phantom_mean_a,
            'mean_char_length': phantom_mean_len,
            'prefix_pattern': dict(phantom_prefixes),
        },
        'verdict': verdict,
    }


# --- Test 2: Dark Pipeline Atom Inventory ---

def test2_dark_atom_inventory(data):
    """Decompose dark-pipeline compounds into atoms, classify each atom."""
    dark = data['dark_pipeline_set']
    bridge = data['bridge_set']
    matched = data['matched_pp_set']
    mid_analyzer = data['mid_analyzer']

    # Separate compound vs atomic
    dark_compound = sorted(m for m in dark if mid_analyzer.is_compound(m))
    dark_atomic = sorted(m for m in dark if not mid_analyzer.is_compound(m))

    # Decompose all compounds
    atom_freq = Counter()           # atom -> count of compounds containing it
    atom_to_compounds = defaultdict(list)
    compound_atom_counts = []       # atoms per compound
    compound_details = {}           # mid -> {atoms, atom_count}

    for mid in dark_compound:
        atoms = mid_analyzer.get_maximal_atoms(mid)
        compound_atom_counts.append(len(atoms))
        compound_details[mid] = {
            'atoms': atoms,
            'atom_count': len(atoms),
            'char_length': len(mid),
        }
        for atom in atoms:
            atom_freq[atom] += 1
            atom_to_compounds[atom].append(mid)

    unique_atoms = set(atom_freq.keys())

    # Classify each atom
    atom_classification = {}
    for atom in unique_atoms:
        if atom in bridge:
            cls = 'BRIDGE'
        elif atom in matched:
            cls = 'MATCHED_PP'
        elif atom in dark:
            cls = 'DARK_PIPELINE'
        else:
            cls = 'OTHER'
        atom_classification[atom] = cls

    # Classification counts
    cls_counts = Counter(atom_classification.values())
    cls_type_fractions = {c: n / len(unique_atoms) for c, n in cls_counts.items()} if unique_atoms else {}

    # Occurrence-weighted classification
    total_occ = sum(atom_freq.values())
    cls_occ = Counter()
    for atom, cnt in atom_freq.items():
        cls_occ[atom_classification[atom]] += cnt
    cls_occ_fractions = {c: n / total_occ for c, n in cls_occ.items()} if total_occ else {}

    bridge_atoms = {a for a in unique_atoms if atom_classification[a] == 'BRIDGE'}
    bridge_type_frac = len(bridge_atoms) / len(unique_atoms) if unique_atoms else 0
    bridge_occ_frac = cls_occ.get('BRIDGE', 0) / total_occ if total_occ else 0

    # Bridge compound coverage: fraction of compounds containing >= 1 bridge atom
    compounds_with_bridge = sum(
        1 for mid in dark_compound
        if any(a in bridge for a in mid_analyzer.get_maximal_atoms(mid))
    )
    bridge_coverage = compounds_with_bridge / len(dark_compound) if dark_compound else 0

    # Mean atoms per compound
    mean_atoms = sum(compound_atom_counts) / len(compound_atom_counts) if compound_atom_counts else 0

    # Atom count distribution
    atom_count_dist = Counter(compound_atom_counts)

    # Top-20 atoms
    top_atoms = []
    for atom, cnt in atom_freq.most_common(20):
        top_atoms.append({
            'atom': atom,
            'frequency': cnt,
            'classification': atom_classification[atom],
            'char_length': len(atom),
        })

    # Verdict
    if bridge_occ_frac > 0.50:
        verdict = 'BRIDGE_ATOMS_PREVALENT'
    elif bridge_occ_frac >= 0.20:
        verdict = 'BRIDGE_ATOMS_PRESENT'
    else:
        verdict = 'BRIDGE_ATOMS_RARE'

    print(f"\nTest 2: Dark Pipeline Atom Inventory")
    print(f"  Compound: {len(dark_compound)}, Atomic: {len(dark_atomic)}, "
          f"Rate: {len(dark_compound)/len(dark):.3f}")
    print(f"  Unique atoms found: {len(unique_atoms)}")
    print(f"  Atom classification (types): {dict(cls_counts)}")
    print(f"  Atom classification (occurrences): {dict(cls_occ)}")
    print(f"  Bridge type fraction: {bridge_type_frac:.3f}")
    print(f"  Bridge occurrence fraction: {bridge_occ_frac:.3f}")
    print(f"  Bridge compound coverage: {bridge_coverage:.3f} "
          f"({compounds_with_bridge}/{len(dark_compound)})")
    print(f"  Mean atoms/compound: {mean_atoms:.2f}")
    print(f"  Verdict: {verdict}")

    return {
        'n_compound_dark': len(dark_compound),
        'n_atomic_dark': len(dark_atomic),
        'compound_rate': len(dark_compound) / len(dark) if dark else 0,
        'n_unique_atoms': len(unique_atoms),
        'atom_classification_types': dict(cls_counts),
        'atom_classification_type_fractions': cls_type_fractions,
        'atom_classification_occurrences': dict(cls_occ),
        'atom_classification_occurrence_fractions': cls_occ_fractions,
        'bridge_atom_type_fraction': bridge_type_frac,
        'bridge_atom_occurrence_fraction': bridge_occ_frac,
        'bridge_compound_coverage': bridge_coverage,
        'n_compounds_with_bridge_atom': compounds_with_bridge,
        'mean_atoms_per_compound': mean_atoms,
        'atom_count_distribution': {str(k): v for k, v in sorted(atom_count_dist.items())},
        'top_20_atoms': top_atoms,
        'bridge_atoms_list': sorted(bridge_atoms),
        'verdict': verdict,
    }


# --- Test 3: Atom Pool Overlap ---

def test3_atom_pool_overlap(data):
    """Compare atom inventories across grammar, dark-pipeline, and all-B compounds."""
    matched = data['matched_pp_set']
    dark = data['dark_pipeline_set']
    mid_analyzer = data['mid_analyzer']

    def get_atom_pool(middles):
        pool = set()
        for mid in middles:
            if mid_analyzer.is_compound(mid):
                pool.update(mid_analyzer.get_maximal_atoms(mid))
        return pool

    def compound_count(middles):
        return sum(1 for m in middles if mid_analyzer.is_compound(m))

    # (a) Grammar compounds: matched-PP MIDDLEs that are compound
    grammar_compounds = [m for m in matched if mid_analyzer.is_compound(m)]
    grammar_atoms = get_atom_pool(matched)

    # (b) Dark-pipeline compounds
    dark_compounds = [m for m in dark if mid_analyzer.is_compound(m)]
    dark_atoms = get_atom_pool(dark)

    # (c) All B compounds from MiddleAnalyzer inventory
    all_b_middles = set()
    for mid in mid_analyzer._inventory:
        all_b_middles.add(mid)
    all_b_atoms = get_atom_pool(all_b_middles)

    # Pairwise Jaccard
    j_gd = jaccard(grammar_atoms, dark_atoms)
    j_ga = jaccard(grammar_atoms, all_b_atoms)
    j_da = jaccard(dark_atoms, all_b_atoms)

    # Set algebra
    shared_gd = grammar_atoms & dark_atoms
    dark_exclusive = dark_atoms - grammar_atoms
    grammar_exclusive = grammar_atoms - dark_atoms

    # Verdict
    if j_gd > 0.8:
        verdict = 'SHARED_ATOM_POOL'
    elif j_gd >= 0.4:
        verdict = 'OVERLAPPING_POOLS'
    else:
        verdict = 'DISTINCT_POOLS'

    print(f"\nTest 3: Atom Pool Overlap")
    print(f"  Grammar compounds: {len(grammar_compounds)}, atoms: {len(grammar_atoms)}")
    print(f"  Dark compounds: {len(dark_compounds)}, atoms: {len(dark_atoms)}")
    print(f"  All B compounds: {compound_count(all_b_middles)}, atoms: {len(all_b_atoms)}")
    print(f"  Jaccard(grammar,dark): {j_gd:.3f}")
    print(f"  Jaccard(grammar,all_b): {j_ga:.3f}")
    print(f"  Jaccard(dark,all_b): {j_da:.3f}")
    print(f"  Shared: {len(shared_gd)}, Dark-exclusive: {len(dark_exclusive)}, "
          f"Grammar-exclusive: {len(grammar_exclusive)}")
    print(f"  Dark-exclusive atoms: {sorted(dark_exclusive)}")
    print(f"  Verdict: {verdict}")

    return {
        'n_grammar_compounds': len(grammar_compounds),
        'n_dark_compounds': len(dark_compounds),
        'n_all_b_compounds': compound_count(all_b_middles),
        'n_grammar_atoms': len(grammar_atoms),
        'n_dark_atoms': len(dark_atoms),
        'n_all_b_atoms': len(all_b_atoms),
        'jaccard_grammar_dark': j_gd,
        'jaccard_grammar_allb': j_ga,
        'jaccard_dark_allb': j_da,
        'n_shared': len(shared_gd),
        'n_dark_exclusive': len(dark_exclusive),
        'n_grammar_exclusive': len(grammar_exclusive),
        'shared_atoms': sorted(shared_gd),
        'dark_exclusive_atoms': sorted(dark_exclusive),
        'grammar_exclusive_atoms': sorted(grammar_exclusive),
        'verdict': verdict,
    }


# --- Test 4: Atom-Section Structure ---

def test4_atom_section_structure(data):
    """Test whether dark-pipeline atoms predict section concentration."""
    dark = data['dark_pipeline_set']
    mid_analyzer = data['mid_analyzer']
    middle_section_freq = data['middle_section_freq']

    random.seed(42)

    dark_compounds = [m for m in dark if mid_analyzer.is_compound(m)]

    # Build: atom -> list of section distributions from compounds containing it
    atom_compound_sections = defaultdict(list)
    compound_sec_dists = {}  # mid -> Counter (for shuffling)

    for mid in dark_compounds:
        atoms = mid_analyzer.get_maximal_atoms(mid)
        sec_dist = middle_section_freq.get(mid, Counter())
        compound_sec_dists[mid] = sec_dist
        for atom in atoms:
            atom_compound_sections[atom].append(mid)

    # Filter to atoms in >= 5 dark-pipeline compounds
    testable_atoms = {a: mids for a, mids in atom_compound_sections.items()
                      if len(mids) >= 5}

    if not testable_atoms:
        print(f"\nTest 4: Atom-Section Structure")
        print(f"  No testable atoms (none in >= 5 dark-pipeline compounds)")
        return {'verdict': 'INSUFFICIENT_DATA', 'n_testable_atoms': 0}

    # Compute observed mean Herfindahl
    atom_herfs = {}
    atom_details = []
    for atom, mids in sorted(testable_atoms.items()):
        pooled = Counter()
        for mid in mids:
            pooled.update(compound_sec_dists.get(mid, Counter()))
        h = herfindahl(pooled)
        atom_herfs[atom] = h

        # Dominant section
        dom_sec = pooled.most_common(1)[0][0] if pooled else 'none'
        atom_details.append({
            'atom': atom,
            'n_compounds': len(mids),
            'pooled_herf': h,
            'dominant_section': dom_sec,
        })

    observed_mean_herf = sum(atom_herfs.values()) / len(atom_herfs)

    # Permutation null: shuffle compound-section associations
    # Pool all section distributions for dark compounds
    all_sec_dists = [compound_sec_dists.get(mid, Counter()) for mid in dark_compounds]

    n_shuffles = 1000
    null_herfs = []

    # For each shuffle: randomly reassign section distributions to compounds
    # Then recompute atom-level pooled Herfindahls
    for _ in range(n_shuffles):
        shuffled = list(all_sec_dists)
        random.shuffle(shuffled)

        # Create a shuffled mapping: dark_compounds[i] -> shuffled[i]
        shuffled_map = {mid: shuffled[i] for i, mid in enumerate(dark_compounds)}

        trial_herfs = []
        for atom, mids in testable_atoms.items():
            pooled = Counter()
            for mid in mids:
                pooled.update(shuffled_map.get(mid, Counter()))
            trial_herfs.append(herfindahl(pooled))

        null_herfs.append(sum(trial_herfs) / len(trial_herfs))

    null_mean = sum(null_herfs) / len(null_herfs)
    perm_p = sum(1 for nh in null_herfs if nh >= observed_mean_herf) / n_shuffles

    # Verdict
    if perm_p < 0.05:
        verdict = 'ATOM_SECTION_STRUCTURED'
    else:
        verdict = 'ATOM_SECTION_INDEPENDENT'

    print(f"\nTest 4: Atom-Section Structure")
    print(f"  Testable atoms (>= 5 compounds): {len(testable_atoms)}")
    print(f"  Observed mean Herfindahl: {observed_mean_herf:.4f}")
    print(f"  Null mean Herfindahl: {null_mean:.4f}")
    print(f"  Permutation p-value: {perm_p:.4f} (n={n_shuffles})")
    print(f"  Verdict: {verdict}")

    return {
        'n_testable_atoms': len(testable_atoms),
        'observed_mean_herf': observed_mean_herf,
        'null_mean_herf': null_mean,
        'perm_p': perm_p,
        'n_shuffles': n_shuffles,
        'atom_details': atom_details,
        'verdict': verdict,
    }


# --- Test 5: Construction Grammar ---

def test5_construction_grammar(data):
    """Compare dark-pipeline atom bigrams to C1065's ordering grammar."""
    dark = data['dark_pipeline_set']
    mid_analyzer = data['mid_analyzer']
    c1065_data = data['c1065_data']

    dark_compounds = [m for m in dark if mid_analyzer.is_compound(m)]

    # 1. Extract atom bigrams from dark-pipeline compounds
    dark_bigrams = Counter()
    dark_positions = defaultdict(list)  # atom -> [normalized positions]
    n_with_bigrams = 0

    for mid in dark_compounds:
        atoms = mid_analyzer.get_maximal_atoms(mid)
        if len(atoms) < 2:
            continue

        # Locate each atom's position in the MIDDLE string
        atom_positions = []
        for atom in atoms:
            pos = mid.find(atom)
            if pos >= 0:
                atom_positions.append((pos, atom))

        # Sort by position
        atom_positions.sort(key=lambda x: x[0])

        if len(atom_positions) < 2:
            continue

        n_with_bigrams += 1

        # Record normalized positions
        mid_len = len(mid)
        for pos, atom in atom_positions:
            norm_pos = pos / mid_len if mid_len > 0 else 0
            dark_positions[atom].append(norm_pos)

        # Extract consecutive bigrams
        for i in range(len(atom_positions) - 1):
            a = atom_positions[i][1]
            b = atom_positions[i + 1][1]
            dark_bigrams[(a, b)] += 1

    # 2. Dark-pipeline asymmetric pairs (>80% dominance, n >= 3)
    pair_counts = defaultdict(lambda: [0, 0])
    for (a, b), n in dark_bigrams.items():
        key = tuple(sorted([a, b]))
        if (a, b) == (key[0], key[1]):
            pair_counts[key][0] += n
        else:
            pair_counts[key][1] += n

    dark_asymmetric = []
    for (a, b), (fwd, rev) in pair_counts.items():
        total = fwd + rev
        if total >= 3:
            rate = max(fwd, rev) / total
            if rate > 0.80:
                if fwd >= rev:
                    first, second = a, b
                else:
                    first, second = b, a
                dark_asymmetric.append({
                    'first': first,
                    'second': second,
                    'dominant_count': max(fwd, rev),
                    'subordinate_count': min(fwd, rev),
                    'total': total,
                    'rate': rate,
                })

    # 3. Compare with C1065 asymmetric pairs
    c1065_pairs = c1065_data.get('asymmetric_pairs', [])

    matches = 0
    mismatches = 0
    not_found = 0
    comparison_details = []

    for pair in c1065_pairs:
        dom = pair['dominant']
        sub = pair['subordinate']
        fwd = pair['fwd']  # count of dom-before-sub
        rev = pair['rev']  # count of sub-before-dom

        # Determine established direction
        if fwd >= rev:
            established_first = dom
            established_second = sub
        else:
            established_first = sub
            established_second = dom

        # Check dark pipeline
        dark_same = dark_bigrams.get((established_first, established_second), 0)
        dark_opposite = dark_bigrams.get((established_second, established_first), 0)

        detail = {
            'c1065_first': established_first,
            'c1065_second': established_second,
            'c1065_total': pair['total'],
        }

        if dark_same + dark_opposite == 0:
            not_found += 1
            detail['dark_status'] = 'NOT_FOUND'
        elif dark_same >= dark_opposite:
            matches += 1
            detail['dark_status'] = 'MATCH'
            detail['dark_same'] = dark_same
            detail['dark_opposite'] = dark_opposite
        else:
            mismatches += 1
            detail['dark_status'] = 'MISMATCH'
            detail['dark_same'] = dark_same
            detail['dark_opposite'] = dark_opposite

        comparison_details.append(detail)

    total_tested = matches + mismatches
    agreement_rate = matches / total_tested if total_tested > 0 else 0

    # 4. Gateway/terminal atom position check
    gateway_atoms = {'opch', 'eol', 'op'}
    terminal_atoms = {'ai', 'kc', 'ed', 'eod'}

    gateway_positions = []
    terminal_positions = []
    for atom in gateway_atoms:
        if atom in dark_positions:
            gateway_positions.extend(dark_positions[atom])
    for atom in terminal_atoms:
        if atom in dark_positions:
            terminal_positions.extend(dark_positions[atom])

    gateway_mean = sum(gateway_positions) / len(gateway_positions) if gateway_positions else None
    terminal_mean = sum(terminal_positions) / len(terminal_positions) if terminal_positions else None

    positional_preserved = None
    if gateway_mean is not None and terminal_mean is not None:
        positional_preserved = gateway_mean < terminal_mean

    # Verdict
    if total_tested == 0:
        verdict = 'INSUFFICIENT_DATA'
    elif agreement_rate > 0.70:
        verdict = 'SAME_GRAMMAR'
    elif agreement_rate >= 0.30:
        verdict = 'MODIFIED_GRAMMAR'
    else:
        verdict = 'DISTINCT_GRAMMAR'

    print(f"\nTest 5: Construction Grammar")
    print(f"  Dark compounds with bigrams: {n_with_bigrams}")
    print(f"  Dark bigram types: {len(dark_bigrams)}, tokens: {sum(dark_bigrams.values())}")
    print(f"  Dark asymmetric pairs (>80%, n>=3): {len(dark_asymmetric)}")
    print(f"  C1065 comparison: tested={total_tested}, "
          f"matches={matches}, mismatches={mismatches}, not_found={not_found}")
    print(f"  Agreement rate: {agreement_rate:.3f}")
    print(f"  Gateway mean pos: {gateway_mean:.3f}" if gateway_mean is not None else "  Gateway: no data")
    print(f"  Terminal mean pos: {terminal_mean:.3f}" if terminal_mean is not None else "  Terminal: no data")
    print(f"  Positional preserved: {positional_preserved}")
    print(f"  Verdict: {verdict}")

    return {
        'n_compounds_with_bigrams': n_with_bigrams,
        'n_dark_bigram_types': len(dark_bigrams),
        'n_dark_bigram_tokens': sum(dark_bigrams.values()),
        'n_dark_asymmetric_pairs': len(dark_asymmetric),
        'dark_asymmetric_pairs': dark_asymmetric,
        'c1065_comparison': {
            'n_c1065_pairs': len(c1065_pairs),
            'n_tested': total_tested,
            'matches': matches,
            'mismatches': mismatches,
            'not_found': not_found,
            'agreement_rate': agreement_rate,
        },
        'comparison_details': comparison_details,
        'gateway_terminal_check': {
            'gateway_atoms': sorted(gateway_atoms),
            'terminal_atoms': sorted(terminal_atoms),
            'gateway_mean_pos': gateway_mean,
            'terminal_mean_pos': terminal_mean,
            'gateway_n': len(gateway_positions),
            'terminal_n': len(terminal_positions),
            'positional_preserved': positional_preserved,
        },
        'verdict': verdict,
    }


# --- Synthesis ---

def synthesize(results):
    """Combine all test verdicts into an overall assessment."""
    verdicts = {
        'test1': results['test1']['verdict'],
        'test2': results['test2']['verdict'],
        'test3': results['test3']['verdict'],
        'test4': results['test4']['verdict'],
        'test5': results['test5']['verdict'],
    }

    t1 = verdicts['test1']
    t2 = verdicts['test2']
    t3 = verdicts['test3']
    t4 = verdicts['test4']
    t5 = verdicts['test5']

    # Core architecture assessment from Test 2 + Test 3
    if t1 != 'PARTITION_COMPLETE':
        overall = 'PARTITION_INCOMPLETE'
        summary = 'PP MIDDLE partition failed verification.'
    elif t2 in ('BRIDGE_ATOMS_PREVALENT', 'BRIDGE_ATOMS_PRESENT'):
        if t3 == 'SHARED_ATOM_POOL' and t5 == 'SAME_GRAMMAR':
            overall = 'UNIFIED_CONSTRUCTION_ARCHITECTURE'
            summary = ('PP pipeline fully partitioned. Dark-pipeline compounds are '
                       'built from bridge atoms using the same construction grammar '
                       'as general B compounds. Unified compositional system.')
        elif t3 == 'SHARED_ATOM_POOL':
            overall = 'SHARED_ATOMS_VARIANT_GRAMMAR'
            summary = ('PP pipeline fully partitioned. Dark-pipeline compounds use '
                       'bridge atoms from a shared atom pool but with '
                       + ('same' if t5 == 'SAME_GRAMMAR' else 'modified')
                       + ' ordering rules.')
        elif t5 in ('SAME_GRAMMAR', 'MODIFIED_GRAMMAR'):
            overall = 'BRIDGE_SUBSTRATE_OVERLAPPING_POOLS'
            summary = ('PP pipeline fully partitioned. Dark-pipeline compounds contain '
                       'bridge atoms with overlapping but not identical atom pools.')
        else:
            overall = 'BRIDGE_SUBSTRATE_DISTINCT_GRAMMAR'
            summary = ('PP pipeline fully partitioned. Dark-pipeline compounds contain '
                       'bridge atoms but assemble them using a distinct grammar.')
    elif t2 == 'BRIDGE_ATOMS_RARE':
        overall = 'INDEPENDENT_CONSTRUCTION'
        summary = ('PP pipeline fully partitioned but dark-pipeline compounds rarely '
                   'use bridge atoms. Independent construction vocabulary.')
    else:
        overall = 'UNRESOLVED'
        summary = 'Could not synthesize a clear verdict from test results.'

    # Append section finding
    if t4 == 'ATOM_SECTION_STRUCTURED':
        summary += ' Atom choice predicts section concentration.'
    elif t4 == 'ATOM_SECTION_INDEPENDENT':
        summary += ' Section concentration is not atom-driven.'

    verdicts['overall'] = overall
    verdicts['summary'] = summary

    print(f"\n{'='*60}")
    print(f"OVERALL VERDICT: {overall}")
    print(f"  {summary}")
    print(f"{'='*60}")

    return verdicts


# --- Main ---

def main():
    print("Phase 408: PP Pipeline Architecture Closure + Atom Decomposition")
    print("=" * 60)

    data = load_data()

    # Validation
    print(f"\nValidation:")
    print(f"  All PP MIDDLEs: {len(data['all_pp_set'])} (expect 404)")
    print(f"  Bridge: {len(data['bridge_set'])} (expect 85)")
    print(f"  Matched PP: {len(data['matched_pp_set'])} (expect 89)")
    print(f"  Non-bridge matched: {len(data['nonbridge_matched_set'])} (expect ~4)")
    print(f"  Dark pipeline: {len(data['dark_pipeline_set'])} (expect 300)")
    print(f"  B-absent: {len(data['b_absent_set'])} (expect 15)")
    print(f"  Core MIDDLEs: {len(data['core_middles'])}")
    print(f"  B tokens scanned: {data['n_b_scanned']} (expect ~23243)")

    results = {}
    results['test1'] = test1_partition_closure(data)
    results['test2'] = test2_dark_atom_inventory(data)
    results['test3'] = test3_atom_pool_overlap(data)
    results['test4'] = test4_atom_section_structure(data)
    results['test5'] = test5_construction_grammar(data)
    results['verdicts'] = synthesize(results)

    results['metadata'] = {
        'phase': 'PP_PIPELINE_ATOM_DECOMPOSITION',
        'phase_number': 408,
        'script': 'pp_pipeline_atoms.py',
        'n_all_pp': len(data['all_pp_set']),
        'n_bridge': len(data['bridge_set']),
        'n_matched_pp': len(data['matched_pp_set']),
        'n_nonbridge_matched': len(data['nonbridge_matched_set']),
        'n_dark_pipeline': len(data['dark_pipeline_set']),
        'n_b_absent': len(data['b_absent_set']),
        'n_core_middles': len(data['core_middles']),
        'n_b_tokens_scanned': data['n_b_scanned'],
    }

    # Write output
    out_dir = ROOT / 'phases/PP_PIPELINE_ATOM_DECOMPOSITION/results'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'pp_pipeline_atoms.json'

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to {out_path}")
    size = out_path.stat().st_size
    print(f"Output size: {size:,} bytes")


if __name__ == '__main__':
    main()
