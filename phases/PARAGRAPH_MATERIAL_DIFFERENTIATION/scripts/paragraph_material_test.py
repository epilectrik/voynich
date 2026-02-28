"""
Phase 492: Paragraph-Level Material Differentiation Test

HYPOTHESIS: Each Voynich Currier B folio represents a multi-material
processing session on a single apparatus (furnace/oven), where each
paragraph encodes a distinct material's procedure.

Historical basis: Brunschwig's 1512 Large Book shows a water bath with
6 stills around a central copper flue. 15th-century woodcuts show
4-vent furnaces with 4 separate stills. Multi-material batch processing
on a single apparatus was standard practice.

Structural basis:
  C845:  Paragraphs are self-contained mini-programs (independent cucurbits)
  C855:  Same-folio paragraphs share role profile but NOT vocabulary (Jaccard 0.061)
  C1257: Consecutive paragraphs share MIDDLEs but NOT kernel/suffix profiles
  C1083: HT density is paragraph-ordinal neutral (parallel, not sequential)
  C1288: Within-folio paragraphs MORE category-similar than cross-folio
         (= same apparatus/fire degree -> same category envelope)
  C1325: All paragraphs in a folio share the same REGIME (= fire degree)
  C1377: Puff folio-level test NULL (signal washed out by multi-material averaging)

KEY INSIGHT: C1288 is a CONFIRMATION, not a conflict. Materials batched
on the same furnace share a fire degree, so their category profiles
converge. Differentiation should appear at MIDDLE vocabulary level
(different materials -> different specific MIDDLEs).

Tests:
  T1: Within-folio MIDDLE Jaccard diversity vs between-folio-same-REGIME
  T2: Dark-pipeline MIDDLE diversity (identification substrate, C1135/C1139)
  T3: Bridge MIDDLE diversity (shared backbone, C1139) — CONTROL
  T4: Header vs body MIDDLE diversity within folio
  T5: Paragraph count distributions (EXPLORATORY)

Pre-registered predictions:
  T1: Within-folio MIDDLE diversity > between-folio-same-REGIME (p<0.01)
  T2: Dark-pipeline within-folio diversity > between-folio-same-REGIME (p<0.01)
  T3: Bridge within-folio diversity = between-folio (NULL expected — control)
  T4: Header MIDDLE diversity > body MIDDLE diversity within folio (p<0.01)

FALSIFIER: Within-folio dark-pipeline MIDDLE diversity <= between-folio-same-REGIME

Statistical design:
  - Permutation tests (10,000 iterations, shuffle paragraph-folio within REGIME)
  - Only folios with 3+ paragraphs
  - Only paragraphs with 5+ tokens (sufficient for MIDDLE inventory)
  - Bonferroni correction: 4 hypothesis tests -> p < 0.0025
  - Condition on REGIME and section
"""

import json
import random
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, BFolioDecoder

# ============================================================
# CONSTANTS
# ============================================================

RESULTS_DIR = PROJECT_ROOT / 'phases' / 'PARAGRAPH_MATERIAL_DIFFERENTIATION' / 'results'
N_PERMUTATIONS = 10000
BONFERRONI_THRESHOLD = 0.0025  # 0.01 / 4 hypothesis tests
MIN_TOKENS_PER_PARA = 5        # Minimum tokens for meaningful MIDDLE inventory
MIN_PARAS_PER_FOLIO = 3        # Minimum paragraphs for pairwise diversity
RANDOM_SEED = 492               # Phase number

# ============================================================
# DATA LOADING
# ============================================================

def load_dark_pipeline_middles():
    """Load the 300 dark-pipeline MIDDLEs (C1135, C1137)."""
    path = PROJECT_ROOT / 'data' / 'dark_pipeline_middles.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(data['middles'])

def load_bridge_middles():
    """Load the 85 bridge MIDDLEs (C1013, C1139)."""
    path = PROJECT_ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(data['t5_structural_profile']['bridge_middles'])

def load_regime_mapping():
    """Load REGIME assignments per folio (string: folio -> REGIME name)."""
    path = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    raw = data.get('regime_assignments', {})
    # Values may be dicts with 'regime' key or plain strings
    result = {}
    for folio, val in raw.items():
        if isinstance(val, dict):
            result[folio] = val.get('regime', 'UNKNOWN')
        else:
            result[folio] = str(val)
    return result

def load_section_mapping():
    """Load section assignments per folio from transcript."""
    tx = Transcript()
    section_map = {}
    for token in tx.currier_b():
        if token.section and token.folio not in section_map:
            section_map[token.folio] = token.section
    return section_map

# ============================================================
# PARAGRAPH MIDDLE EXTRACTION
# ============================================================

def extract_paragraph_middles(decoder, folio, dark_set, bridge_set):
    """
    Extract per-paragraph MIDDLE inventories for a folio.

    Returns list of dicts, each containing:
      - folio, para_id, token_count
      - all_middles: set of all MIDDLEs
      - dark_middles: set of dark-pipeline MIDDLEs
      - bridge_middles: set of bridge MIDDLEs
      - header_middles: set of MIDDLEs from header line(s)
      - body_middles: set of MIDDLEs from body lines
    """
    paragraphs = decoder.analyze_folio_paragraphs(folio)
    if not paragraphs:
        return []

    results = []
    for para in paragraphs:
        if para.token_count < MIN_TOKENS_PER_PARA:
            continue

        all_middles = set()
        dark_middles = set()
        bridge_middles_found = set()
        header_middles = set()
        body_middles = set()

        for line in para.lines:
            for token in line.tokens:
                mid = token.morph.middle if token.morph else None
                if not mid:
                    continue

                all_middles.add(mid)

                if mid in dark_set:
                    dark_middles.add(mid)
                if mid in bridge_set:
                    bridge_middles_found.add(mid)

                # Zone assignment (header = first line, body = rest)
                zone = getattr(line, 'paragraph_zone', None)
                if zone == 'HEADER':
                    header_middles.add(mid)
                else:
                    body_middles.add(mid)

        results.append({
            'folio': folio,
            'para_id': para.paragraph_id,
            'token_count': para.token_count,
            'line_count': para.line_count,
            'all_middles': all_middles,
            'dark_middles': dark_middles,
            'bridge_middles': bridge_middles_found,
            'header_middles': header_middles,
            'body_middles': body_middles,
        })

    return results

# ============================================================
# DIVERSITY METRICS
# ============================================================

def jaccard_distance(set_a, set_b):
    """Jaccard distance = 1 - Jaccard similarity. Higher = more different."""
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    if not union:
        return 0.0
    intersection = set_a & set_b
    return 1.0 - len(intersection) / len(union)


def mean_pairwise_jaccard_distance(middle_sets):
    """Mean pairwise Jaccard distance between a list of sets."""
    if len(middle_sets) < 2:
        return 0.0

    distances = []
    for i, j in combinations(range(len(middle_sets)), 2):
        d = jaccard_distance(middle_sets[i], middle_sets[j])
        distances.append(d)

    return sum(distances) / len(distances) if distances else 0.0


def within_folio_diversity(folio_paragraphs, middle_key='all_middles'):
    """
    Compute mean within-folio pairwise Jaccard distance.
    Returns (mean_distance, n_pairs, per_folio_distances).
    """
    all_distances = []
    per_folio = {}

    # Group by folio
    by_folio = defaultdict(list)
    for p in folio_paragraphs:
        by_folio[p['folio']].append(p)

    for folio, paras in by_folio.items():
        if len(paras) < 2:
            continue
        sets = [p[middle_key] for p in paras]
        distances = []
        for i, j in combinations(range(len(sets)), 2):
            d = jaccard_distance(sets[i], sets[j])
            distances.append(d)

        mean_d = sum(distances) / len(distances)
        per_folio[folio] = mean_d
        all_distances.extend(distances)

    overall = sum(all_distances) / len(all_distances) if all_distances else 0.0
    return overall, len(all_distances), per_folio


def between_folio_same_regime_diversity(folio_paragraphs, regime_map, middle_key='all_middles'):
    """
    Compute mean between-folio (same REGIME) pairwise Jaccard distance.
    For each REGIME, take one random paragraph per folio and compute
    cross-folio pairwise distances.
    """
    # Group by REGIME then folio
    by_regime_folio = defaultdict(lambda: defaultdict(list))
    for p in folio_paragraphs:
        regime = regime_map.get(p['folio'], 'UNKNOWN')
        by_regime_folio[regime][p['folio']].append(p)

    all_distances = []

    for regime, folio_dict in by_regime_folio.items():
        if regime == 'UNKNOWN':
            continue
        folios_with_paras = list(folio_dict.keys())
        if len(folios_with_paras) < 2:
            continue

        # Take one representative paragraph per folio (the one with most tokens)
        representatives = []
        for folio in folios_with_paras:
            paras = folio_dict[folio]
            best = max(paras, key=lambda p: p['token_count'])
            representatives.append(best)

        # Pairwise distances between different folios
        for i, j in combinations(range(len(representatives)), 2):
            d = jaccard_distance(
                representatives[i][middle_key],
                representatives[j][middle_key]
            )
            all_distances.append(d)

    overall = sum(all_distances) / len(all_distances) if all_distances else 0.0
    return overall, len(all_distances)

# ============================================================
# PERMUTATION TEST
# ============================================================

def permutation_test(folio_paragraphs, regime_map, middle_key, n_perm=N_PERMUTATIONS):
    """
    Test whether within-folio diversity exceeds between-folio-same-REGIME diversity.

    H0: Within-folio paragraph MIDDLE diversity = between-folio-same-REGIME diversity
    H1: Within-folio > between-folio (different materials within folio)

    Permutation: shuffle paragraph-folio assignments within REGIME.
    """
    # Observed statistic
    obs_within, n_within, _ = within_folio_diversity(folio_paragraphs, middle_key)
    obs_between, n_between = between_folio_same_regime_diversity(
        folio_paragraphs, regime_map, middle_key)
    obs_diff = obs_within - obs_between

    # Permutation null: shuffle paragraph-folio assignments within REGIME
    rng = random.Random(RANDOM_SEED)

    # Group paragraphs by REGIME
    by_regime = defaultdict(list)
    for p in folio_paragraphs:
        regime = regime_map.get(p['folio'], 'UNKNOWN')
        by_regime[regime].append(p)

    count_ge = 0

    for _ in range(n_perm):
        # Create shuffled version: reassign paragraphs to random folios within REGIME
        shuffled = []
        for regime, paras in by_regime.items():
            if regime == 'UNKNOWN':
                continue
            # Get all folios in this REGIME
            folios = list(set(p['folio'] for p in paras))
            if len(folios) < 2:
                shuffled.extend(paras)
                continue

            # Shuffle: assign each paragraph to a random folio within same REGIME
            shuffled_paras = []
            for p in paras:
                new_folio = rng.choice(folios)
                shuffled_p = dict(p)
                shuffled_p['folio'] = new_folio
                shuffled_paras.append(shuffled_p)
            shuffled.extend(shuffled_paras)

        perm_within, _, _ = within_folio_diversity(shuffled, middle_key)
        perm_between, _ = between_folio_same_regime_diversity(
            shuffled, regime_map, middle_key)
        perm_diff = perm_within - perm_between

        if perm_diff >= obs_diff:
            count_ge += 1

    p_value = (count_ge + 1) / (n_perm + 1)

    return {
        'observed_within': obs_within,
        'observed_between': obs_between,
        'observed_diff': obs_diff,
        'ratio': obs_within / obs_between if obs_between > 0 else float('inf'),
        'n_within_pairs': n_within,
        'n_between_pairs': n_between,
        'p_value': p_value,
        'n_permutations': n_perm,
        'significant': p_value < BONFERRONI_THRESHOLD,
    }

# ============================================================
# TEST 4: HEADER VS BODY DIVERSITY
# ============================================================

def header_vs_body_test(folio_paragraphs, n_perm=N_PERMUTATIONS):
    """
    Test whether within-folio header MIDDLE diversity exceeds
    within-folio body MIDDLE diversity.

    Prediction: Headers identify materials, so they should be MORE
    diverse within a folio than body MIDDLEs (which share operational vocab).
    """
    # Group by folio
    by_folio = defaultdict(list)
    for p in folio_paragraphs:
        by_folio[p['folio']].append(p)

    header_distances = []
    body_distances = []

    for folio, paras in by_folio.items():
        if len(paras) < 2:
            continue

        # Filter paragraphs with non-empty headers/bodies
        h_paras = [p for p in paras if p['header_middles']]
        b_paras = [p for p in paras if p['body_middles']]

        if len(h_paras) >= 2:
            for i, j in combinations(range(len(h_paras)), 2):
                d = jaccard_distance(h_paras[i]['header_middles'], h_paras[j]['header_middles'])
                header_distances.append(d)

        if len(b_paras) >= 2:
            for i, j in combinations(range(len(b_paras)), 2):
                d = jaccard_distance(b_paras[i]['body_middles'], b_paras[j]['body_middles'])
                body_distances.append(d)

    obs_header = sum(header_distances) / len(header_distances) if header_distances else 0.0
    obs_body = sum(body_distances) / len(body_distances) if body_distances else 0.0
    obs_diff = obs_header - obs_body

    # Permutation: shuffle header/body labels within each folio
    rng = random.Random(RANDOM_SEED + 4)
    count_ge = 0

    for _ in range(n_perm):
        perm_header_d = []
        perm_body_d = []

        for folio, paras in by_folio.items():
            if len(paras) < 2:
                continue

            # Collect all header and body MIDDLE sets
            all_h = [p['header_middles'] for p in paras if p['header_middles']]
            all_b = [p['body_middles'] for p in paras if p['body_middles']]

            # Pool and reshuffle
            combined = all_h + all_b
            rng.shuffle(combined)

            perm_h = combined[:len(all_h)]
            perm_b = combined[len(all_h):]

            if len(perm_h) >= 2:
                for i, j in combinations(range(len(perm_h)), 2):
                    d = jaccard_distance(perm_h[i], perm_h[j])
                    perm_header_d.append(d)

            if len(perm_b) >= 2:
                for i, j in combinations(range(len(perm_b)), 2):
                    d = jaccard_distance(perm_b[i], perm_b[j])
                    perm_body_d.append(d)

        ph = sum(perm_header_d) / len(perm_header_d) if perm_header_d else 0.0
        pb = sum(perm_body_d) / len(perm_body_d) if perm_body_d else 0.0
        if (ph - pb) >= obs_diff:
            count_ge += 1

    p_value = (count_ge + 1) / (n_perm + 1)

    return {
        'observed_header_diversity': obs_header,
        'observed_body_diversity': obs_body,
        'observed_diff': obs_diff,
        'ratio': obs_header / obs_body if obs_body > 0 else float('inf'),
        'n_header_pairs': len(header_distances),
        'n_body_pairs': len(body_distances),
        'p_value': p_value,
        'n_permutations': n_perm,
        'significant': p_value < BONFERRONI_THRESHOLD,
    }

# ============================================================
# TEST 5: PARAGRAPH COUNT DISTRIBUTIONS (EXPLORATORY)
# ============================================================

def paragraph_count_analysis(folio_paragraphs, regime_map, section_map):
    """Exploratory: paragraph count distributions by REGIME and section."""
    by_folio = defaultdict(list)
    for p in folio_paragraphs:
        by_folio[p['folio']].append(p)

    # Per-folio paragraph counts
    folio_counts = {}
    for folio, paras in by_folio.items():
        folio_counts[folio] = len(paras)

    # Group by REGIME
    by_regime = defaultdict(list)
    for folio, count in folio_counts.items():
        regime = regime_map.get(folio, 'UNKNOWN')
        by_regime[regime].append(count)

    # Group by section
    by_section = defaultdict(list)
    for folio, count in folio_counts.items():
        section = section_map.get(folio, 'UNKNOWN')
        by_section[section].append(count)

    results = {
        'overall': {
            'mean': sum(folio_counts.values()) / len(folio_counts) if folio_counts else 0,
            'min': min(folio_counts.values()) if folio_counts else 0,
            'max': max(folio_counts.values()) if folio_counts else 0,
            'n_folios': len(folio_counts),
        },
        'by_regime': {},
        'by_section': {},
    }

    for regime, counts in sorted(by_regime.items()):
        results['by_regime'][regime] = {
            'mean': sum(counts) / len(counts),
            'min': min(counts),
            'max': max(counts),
            'n': len(counts),
            'counts': sorted(counts),
        }

    for section, counts in sorted(by_section.items()):
        results['by_section'][section] = {
            'mean': sum(counts) / len(counts),
            'min': min(counts),
            'max': max(counts),
            'n': len(counts),
            'counts': sorted(counts),
        }

    return results

# ============================================================
# SECTION-STRATIFIED ANALYSIS
# ============================================================

def section_stratified_test(folio_paragraphs, regime_map, section_map, middle_key):
    """Run within vs between diversity test stratified by section."""
    results = {}

    # Group paragraphs by section
    by_section = defaultdict(list)
    for p in folio_paragraphs:
        section = section_map.get(p['folio'], 'UNKNOWN')
        by_section[section].append(p)

    for section, paras in sorted(by_section.items()):
        if section == 'UNKNOWN':
            continue

        # Need at least 2 folios with 3+ paragraphs in this section
        by_folio = defaultdict(list)
        for p in paras:
            by_folio[p['folio']].append(p)

        qualifying_folios = [f for f, ps in by_folio.items() if len(ps) >= 2]
        if len(qualifying_folios) < 2:
            results[section] = {'status': 'INSUFFICIENT_DATA', 'n_folios': len(qualifying_folios)}
            continue

        obs_within, n_w, _ = within_folio_diversity(paras, middle_key)
        obs_between, n_b = between_folio_same_regime_diversity(paras, regime_map, middle_key)

        results[section] = {
            'within_diversity': obs_within,
            'between_diversity': obs_between,
            'diff': obs_within - obs_between,
            'ratio': obs_within / obs_between if obs_between > 0 else float('inf'),
            'n_within_pairs': n_w,
            'n_between_pairs': n_b,
            'n_paragraphs': len(paras),
            'n_qualifying_folios': len(qualifying_folios),
        }

    return results

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("Phase 492: PARAGRAPH_MATERIAL_DIFFERENTIATION")
    print("=" * 70)

    # Load data
    print("\nLoading data...")
    dark_set = load_dark_pipeline_middles()
    bridge_set = load_bridge_middles()
    regime_map = load_regime_mapping()
    section_map = load_section_mapping()

    print(f"  Dark-pipeline MIDDLEs: {len(dark_set)}")
    print(f"  Bridge MIDDLEs: {len(bridge_set)}")
    print(f"  REGIME assignments: {len(regime_map)} folios")
    print(f"  Section assignments: {len(section_map)} folios")

    # Extract paragraph MIDDLEs for all Currier B folios
    print("\nExtracting paragraph-level MIDDLE inventories...")
    decoder = BFolioDecoder()

    all_paragraphs = []
    folio_count = 0
    skipped_folios = 0

    for folio in sorted(regime_map.keys()):
        paras = extract_paragraph_middles(decoder, folio, dark_set, bridge_set)
        if len(paras) >= MIN_PARAS_PER_FOLIO:
            all_paragraphs.extend(paras)
            folio_count += 1
        else:
            skipped_folios += 1

    print(f"  Qualifying folios (>={MIN_PARAS_PER_FOLIO} paragraphs): {folio_count}")
    print(f"  Skipped folios: {skipped_folios}")
    print(f"  Total paragraphs: {len(all_paragraphs)}")

    # Summary stats
    middle_counts = [len(p['all_middles']) for p in all_paragraphs]
    dark_counts = [len(p['dark_middles']) for p in all_paragraphs]
    bridge_counts = [len(p['bridge_middles']) for p in all_paragraphs]

    print(f"\n  MIDDLE types per paragraph:")
    print(f"    All:    mean={sum(middle_counts)/len(middle_counts):.1f}, "
          f"min={min(middle_counts)}, max={max(middle_counts)}")
    print(f"    Dark:   mean={sum(dark_counts)/len(dark_counts):.1f}, "
          f"min={min(dark_counts)}, max={max(dark_counts)}")
    print(f"    Bridge: mean={sum(bridge_counts)/len(bridge_counts):.1f}, "
          f"min={min(bridge_counts)}, max={max(bridge_counts)}")

    # --------------------------------------------------------
    # PRE-REGISTRATION
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("PRE-REGISTERED PREDICTIONS")
    print("=" * 70)
    print("""
    T1: Within-folio ALL MIDDLE diversity > between-folio-same-REGIME
        (p < 0.0025, ratio > 1.15x)
    T2: Within-folio DARK MIDDLE diversity > between-folio-same-REGIME
        (p < 0.0025, ratio > 1.15x) [KEY TEST]
    T3: Within-folio BRIDGE MIDDLE diversity = between-folio-same-REGIME
        (p > 0.05 expected) [CONTROL — bridges are shared backbone]
    T4: Header MIDDLE diversity > body MIDDLE diversity within folio
        (p < 0.0025)

    FALSIFIER: T2 observed_within <= observed_between
    """)

    # Save pre-registration
    prereg = {
        'predictions': {
            'T1': 'within > between for all MIDDLEs',
            'T2': 'within > between for dark-pipeline MIDDLEs (KEY TEST)',
            'T3': 'within = between for bridge MIDDLEs (CONTROL)',
            'T4': 'header diversity > body diversity within folio',
        },
        'falsifier': 'T2 observed_within <= observed_between',
        'thresholds': {
            'p_threshold': BONFERRONI_THRESHOLD,
            'min_ratio': 1.15,
            'n_permutations': N_PERMUTATIONS,
            'min_tokens_per_para': MIN_TOKENS_PER_PARA,
            'min_paras_per_folio': MIN_PARAS_PER_FOLIO,
        },
        'sample': {
            'n_folios': folio_count,
            'n_paragraphs': len(all_paragraphs),
            'skipped_folios': skipped_folios,
        }
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    prereg_path = RESULTS_DIR / 'pre_registration.json'
    with open(prereg_path, 'w', encoding='utf-8') as f:
        json.dump(prereg, f, indent=2)
    print(f"\nPre-registration saved to {prereg_path}")

    # --------------------------------------------------------
    # TEST 1: All MIDDLEs
    # --------------------------------------------------------
    print("\n" + "-" * 70)
    print("TEST 1: All MIDDLE within-folio vs between-folio-same-REGIME diversity")
    print("-" * 70)

    t1 = permutation_test(all_paragraphs, regime_map, 'all_middles')

    print(f"  Within-folio diversity:  {t1['observed_within']:.4f} ({t1['n_within_pairs']} pairs)")
    print(f"  Between-folio diversity: {t1['observed_between']:.4f} ({t1['n_between_pairs']} pairs)")
    print(f"  Difference:              {t1['observed_diff']:+.4f}")
    print(f"  Ratio (within/between):  {t1['ratio']:.3f}x")
    print(f"  p-value:                 {t1['p_value']:.4f}")
    print(f"  Significant (p<{BONFERRONI_THRESHOLD}): {t1['significant']}")

    verdict_t1 = 'PASS' if t1['significant'] and t1['observed_diff'] > 0 else 'NULL'
    print(f"  VERDICT: {verdict_t1}")

    # --------------------------------------------------------
    # TEST 2: Dark-pipeline MIDDLEs (KEY TEST)
    # --------------------------------------------------------
    print("\n" + "-" * 70)
    print("TEST 2: Dark-pipeline MIDDLE within vs between diversity [KEY TEST]")
    print("-" * 70)

    # Filter to paragraphs with at least 1 dark-pipeline MIDDLE
    dark_paras = [p for p in all_paragraphs if p['dark_middles']]
    print(f"  Paragraphs with dark-pipeline MIDDLEs: {len(dark_paras)}/{len(all_paragraphs)}")

    t2 = permutation_test(dark_paras, regime_map, 'dark_middles')

    print(f"  Within-folio diversity:  {t2['observed_within']:.4f} ({t2['n_within_pairs']} pairs)")
    print(f"  Between-folio diversity: {t2['observed_between']:.4f} ({t2['n_between_pairs']} pairs)")
    print(f"  Difference:              {t2['observed_diff']:+.4f}")
    print(f"  Ratio (within/between):  {t2['ratio']:.3f}x")
    print(f"  p-value:                 {t2['p_value']:.4f}")
    print(f"  Significant (p<{BONFERRONI_THRESHOLD}): {t2['significant']}")

    # Check falsifier
    falsified = t2['observed_within'] <= t2['observed_between']
    print(f"  FALSIFIER CHECK: within ({t2['observed_within']:.4f}) "
          f"{'<=' if falsified else '>'} "
          f"between ({t2['observed_between']:.4f})")

    verdict_t2 = 'PASS' if t2['significant'] and t2['observed_diff'] > 0 else 'NULL'
    if falsified:
        verdict_t2 = 'FALSIFIED'
    print(f"  VERDICT: {verdict_t2}")

    # --------------------------------------------------------
    # TEST 3: Bridge MIDDLEs (CONTROL)
    # --------------------------------------------------------
    print("\n" + "-" * 70)
    print("TEST 3: Bridge MIDDLE within vs between diversity [CONTROL]")
    print("-" * 70)

    bridge_paras = [p for p in all_paragraphs if p['bridge_middles']]
    print(f"  Paragraphs with bridge MIDDLEs: {len(bridge_paras)}/{len(all_paragraphs)}")

    t3 = permutation_test(bridge_paras, regime_map, 'bridge_middles')

    print(f"  Within-folio diversity:  {t3['observed_within']:.4f} ({t3['n_within_pairs']} pairs)")
    print(f"  Between-folio diversity: {t3['observed_between']:.4f} ({t3['n_between_pairs']} pairs)")
    print(f"  Difference:              {t3['observed_diff']:+.4f}")
    print(f"  Ratio (within/between):  {t3['ratio']:.3f}x")
    print(f"  p-value:                 {t3['p_value']:.4f}")

    # Control prediction: bridge should NOT differentiate (p > 0.05)
    bridge_null = t3['p_value'] > 0.05
    verdict_t3 = 'CONTROL_PASS' if bridge_null else 'CONTROL_FAIL'
    print(f"  Control (expect p>0.05): {'PASS' if bridge_null else 'FAIL'}")
    print(f"  VERDICT: {verdict_t3}")

    # --------------------------------------------------------
    # TEST 4: Header vs Body diversity
    # --------------------------------------------------------
    print("\n" + "-" * 70)
    print("TEST 4: Header vs body MIDDLE diversity within folio")
    print("-" * 70)

    t4 = header_vs_body_test(all_paragraphs)

    print(f"  Header diversity: {t4['observed_header_diversity']:.4f} ({t4['n_header_pairs']} pairs)")
    print(f"  Body diversity:   {t4['observed_body_diversity']:.4f} ({t4['n_body_pairs']} pairs)")
    print(f"  Difference:       {t4['observed_diff']:+.4f}")
    print(f"  Ratio (H/B):      {t4['ratio']:.3f}x")
    print(f"  p-value:          {t4['p_value']:.4f}")
    print(f"  Significant (p<{BONFERRONI_THRESHOLD}): {t4['significant']}")

    verdict_t4 = 'PASS' if t4['significant'] and t4['observed_diff'] > 0 else 'NULL'
    print(f"  VERDICT: {verdict_t4}")

    # --------------------------------------------------------
    # TEST 5: Paragraph count distributions (EXPLORATORY)
    # --------------------------------------------------------
    print("\n" + "-" * 70)
    print("TEST 5: Paragraph count distributions [EXPLORATORY]")
    print("-" * 70)

    t5 = paragraph_count_analysis(all_paragraphs, regime_map, section_map)

    print(f"  Overall: mean={t5['overall']['mean']:.1f}, "
          f"range=[{t5['overall']['min']}-{t5['overall']['max']}], "
          f"n={t5['overall']['n_folios']}")

    print(f"\n  By REGIME:")
    for regime, stats in sorted(t5['by_regime'].items()):
        print(f"    {regime}: mean={stats['mean']:.1f}, "
              f"range=[{stats['min']}-{stats['max']}], n={stats['n']}")

    print(f"\n  By Section:")
    for section, stats in sorted(t5['by_section'].items()):
        print(f"    {section}: mean={stats['mean']:.1f}, "
              f"range=[{stats['min']}-{stats['max']}], n={stats['n']}")

    # --------------------------------------------------------
    # SECTION-STRATIFIED ANALYSIS
    # --------------------------------------------------------
    print("\n" + "-" * 70)
    print("SECTION-STRATIFIED: Dark-pipeline diversity by section")
    print("-" * 70)

    strat = section_stratified_test(dark_paras, regime_map, section_map, 'dark_middles')

    for section, stats in sorted(strat.items()):
        if stats.get('status') == 'INSUFFICIENT_DATA':
            print(f"  {section}: INSUFFICIENT DATA ({stats['n_folios']} folios)")
            continue
        print(f"  {section}: within={stats['within_diversity']:.4f}, "
              f"between={stats['between_diversity']:.4f}, "
              f"ratio={stats['ratio']:.3f}x, "
              f"n_paras={stats['n_paragraphs']}, "
              f"n_folios={stats['n_qualifying_folios']}")

    # --------------------------------------------------------
    # COMPILE RESULTS
    # --------------------------------------------------------
    results = {
        'phase': 492,
        'name': 'PARAGRAPH_MATERIAL_DIFFERENTIATION',
        'hypothesis': 'Each folio = multi-material session; each paragraph = one material',
        'historical_basis': 'Brunschwig 6-still water bath; 15th-C 4-vent furnace; Norton athanor',
        'structural_basis': ['C845', 'C855', 'C1257', 'C1083', 'C1288', 'C1325', 'C1377'],
        'test_T1_all_middles': t1,
        'test_T2_dark_pipeline': t2,
        'test_T3_bridge_control': t3,
        'test_T4_header_vs_body': t4,
        'test_T5_paragraph_counts': t5,
        'section_stratified': strat,
        'verdicts': {
            'T1': verdict_t1,
            'T2': verdict_t2,
            'T3': verdict_t3,
            'T4': verdict_t4,
            'T5': 'EXPLORATORY',
        },
        'overall_verdict': None,  # Set below
    }

    # Overall verdict
    if verdict_t2 == 'FALSIFIED':
        results['overall_verdict'] = 'HYPOTHESIS FALSIFIED'
        results['interpretation'] = (
            'Within-folio dark-pipeline MIDDLE diversity does not exceed '
            'between-folio diversity. Paragraphs within a folio do NOT encode '
            'different materials at the identification vocabulary level. '
            'The semantic ceiling (C171) extends to paragraph granularity.'
        )
    elif verdict_t2 == 'PASS' and verdict_t3 in ('CONTROL_PASS',):
        results['overall_verdict'] = 'HYPOTHESIS SUPPORTED'
        results['interpretation'] = (
            'Within-folio paragraphs show elevated dark-pipeline MIDDLE diversity '
            '(identification vocabulary) while bridge MIDDLEs (shared backbone) '
            'show no such effect. Consistent with multi-material processing: '
            'same apparatus (shared operational grammar), different materials '
            '(different identification vocabulary).'
        )
    elif verdict_t2 == 'NULL':
        results['overall_verdict'] = 'HYPOTHESIS NULL'
        results['interpretation'] = (
            'No statistically significant dark-pipeline MIDDLE differentiation '
            'detected at paragraph level. The semantic ceiling (C171) may extend '
            'to paragraph granularity, or the effect is too small to detect with '
            'current sample size. Multi-material model remains plausible but '
            'unconfirmed by internal analysis.'
        )

    # Save results
    results_path = RESULTS_DIR / 'paragraph_material_test.json'

    # Convert sets to lists for JSON serialization
    def make_serializable(obj):
        if isinstance(obj, set):
            return sorted(list(obj))
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        if isinstance(obj, float) and (obj == float('inf') or obj == float('-inf')):
            return str(obj)
        return obj

    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(results), f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"OVERALL VERDICT: {results['overall_verdict']}")
    print(f"{'=' * 70}")
    print(f"\n{results['interpretation']}")
    print(f"\nResults saved to {results_path}")


if __name__ == '__main__':
    main()
