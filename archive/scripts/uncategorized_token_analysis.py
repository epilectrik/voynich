"""
Behavioral Role Analysis of Uncategorized Tokens

MODEL DIAGNOSTIC - Not grammar expansion.
Tests hypotheses H1-H5 from the investigation directive.

This script analyzes what role ~12,000 uncategorized tokens play
in the frozen system by testing against observable structure.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Set, Dict, List, Tuple
import statistics

# ============================================================
# DATA LOADING
# ============================================================

def load_transcription() -> List[Dict]:
    """Load transcription data with all metadata."""
    records = []
    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        header = [h.strip('"') for h in header]

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= len(header):
                record = {}
                for i, col in enumerate(header):
                    val = parts[i].strip('"') if i < len(parts) else ''
                    record[col] = val
                records.append(record)
    return records


def load_categorized_tokens() -> Tuple[Set[str], Dict[str, Dict]]:
    """Load tokens from Phase 20A equivalence classes."""
    json_path = Path('phases/01-09_early_hypothesis/phase20a_operator_equivalence.json')
    categorized = set()
    token_info = {}

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for cls in data.get('classes', []):
        class_id = cls['class_id']
        role = cls['functional_role']
        members = cls.get('members', [])

        for member in members:
            if member:
                tok = member.lower()
                categorized.add(tok)
                token_info[tok] = {
                    'class_id': class_id,
                    'role': role,
                    'representative': cls['representative']
                }

    return categorized, token_info


def load_forbidden_pairs() -> Set[Tuple[str, str]]:
    """Load forbidden transitions from hazards."""
    pairs = set()
    transitions = [
        ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
        ('chol', 'r'), ('chedy', 'ee'), ('chey', 'chedy'),
        ('l', 'chol'), ('dy', 'aiin'), ('dy', 'chey'),
        ('or', 'dal'), ('ar', 'chol'), ('qo', 'shey'),
        ('qo', 'shy'), ('ok', 'shol'), ('ol', 'shor'),
        ('dar', 'qokaiin'), ('qokaiin', 'qokedy')
    ]
    for a, b in transitions:
        pairs.add((a, b))
        pairs.add((b, a))
    return pairs


def get_hazard_involved_tokens() -> Set[str]:
    """Get tokens that participate in forbidden transitions."""
    tokens = set()
    transitions = [
        ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
        ('chol', 'r'), ('chedy', 'ee'), ('chey', 'chedy'),
        ('l', 'chol'), ('dy', 'aiin'), ('dy', 'chey'),
        ('or', 'dal'), ('ar', 'chol'), ('qo', 'shey'),
        ('qo', 'shy'), ('ok', 'shol'), ('ol', 'shor'),
        ('dar', 'qokaiin'), ('qokaiin', 'qokedy')
    ]
    for a, b in transitions:
        tokens.add(a)
        tokens.add(b)
    return tokens


# ============================================================
# ANALYSIS 1: POSITIONAL DISTRIBUTION
# ============================================================

def analyze_positional_distribution(records: List[Dict],
                                    categorized: Set[str]) -> Dict:
    """
    Compare positional distribution of categorized vs uncategorized tokens.
    Tests H1 (boundary conditions) and H4 (navigation markers).
    """
    print("\n" + "="*60)
    print("ANALYSIS 1: POSITIONAL DISTRIBUTION")
    print("="*60)

    # Group by folio
    folios = defaultdict(list)
    for rec in records:
        folio = rec.get('folio', '')
        word = rec.get('word', '').lower().strip()
        if folio and word and not word.startswith('*'):
            folios[folio].append(word)

    # For each folio, compute position metrics
    cat_positions = []  # normalized position 0-1 within folio
    uncat_positions = []
    cat_start_counts = 0  # first 10% of folio
    uncat_start_counts = 0
    cat_end_counts = 0  # last 10% of folio
    uncat_end_counts = 0

    cat_line_initial = 0
    uncat_line_initial = 0
    cat_par_initial = 0
    uncat_par_initial = 0

    total_cat = 0
    total_uncat = 0

    for folio, tokens in folios.items():
        n = len(tokens)
        if n == 0:
            continue
        for i, tok in enumerate(tokens):
            pos = i / n  # normalized position
            is_cat = tok in categorized

            if is_cat:
                cat_positions.append(pos)
                total_cat += 1
                if pos < 0.1:
                    cat_start_counts += 1
                if pos > 0.9:
                    cat_end_counts += 1
            else:
                uncat_positions.append(pos)
                total_uncat += 1
                if pos < 0.1:
                    uncat_start_counts += 1
                if pos > 0.9:
                    uncat_end_counts += 1

    # Also check line_initial and par_initial markers
    for rec in records:
        word = rec.get('word', '').lower().strip()
        if not word or word.startswith('*'):
            continue

        is_cat = word in categorized
        line_init = rec.get('line_initial', '')
        par_init = rec.get('par_initial', '')

        try:
            if line_init and int(line_init) == 1:
                if is_cat:
                    cat_line_initial += 1
                else:
                    uncat_line_initial += 1
        except:
            pass

        try:
            if par_init and int(par_init) == 1:
                if is_cat:
                    cat_par_initial += 1
                else:
                    uncat_par_initial += 1
        except:
            pass

    results = {
        'cat_mean_position': statistics.mean(cat_positions) if cat_positions else 0,
        'uncat_mean_position': statistics.mean(uncat_positions) if uncat_positions else 0,
        'cat_start_rate': cat_start_counts / total_cat if total_cat else 0,
        'uncat_start_rate': uncat_start_counts / total_uncat if total_uncat else 0,
        'cat_end_rate': cat_end_counts / total_cat if total_cat else 0,
        'uncat_end_rate': uncat_end_counts / total_uncat if total_uncat else 0,
        'cat_line_initial_rate': cat_line_initial / total_cat if total_cat else 0,
        'uncat_line_initial_rate': uncat_line_initial / total_uncat if total_uncat else 0,
        'total_categorized': total_cat,
        'total_uncategorized': total_uncat,
    }

    print(f"\nTotal tokens: {total_cat + total_uncat}")
    print(f"  Categorized: {total_cat} ({100*total_cat/(total_cat+total_uncat):.1f}%)")
    print(f"  Uncategorized: {total_uncat} ({100*total_uncat/(total_cat+total_uncat):.1f}%)")

    print(f"\nMean position within folio (0=start, 1=end):")
    print(f"  Categorized:   {results['cat_mean_position']:.3f}")
    print(f"  Uncategorized: {results['uncat_mean_position']:.3f}")

    print(f"\nFolio START concentration (first 10%):")
    print(f"  Categorized:   {100*results['cat_start_rate']:.2f}%")
    print(f"  Uncategorized: {100*results['uncat_start_rate']:.2f}%")

    print(f"\nFolio END concentration (last 10%):")
    print(f"  Categorized:   {100*results['cat_end_rate']:.2f}%")
    print(f"  Uncategorized: {100*results['uncat_end_rate']:.2f}%")

    print(f"\nLine-initial position rate:")
    print(f"  Categorized:   {100*results['cat_line_initial_rate']:.2f}%")
    print(f"  Uncategorized: {100*results['uncat_line_initial_rate']:.2f}%")

    # H1 assessment
    start_ratio = results['uncat_start_rate'] / results['cat_start_rate'] if results['cat_start_rate'] else 0
    print(f"\n>>> H1 INDICATOR (boundary concentration):")
    print(f"    Uncategorized/Categorized start ratio: {start_ratio:.2f}x")
    if start_ratio > 1.5:
        print("    STATUS: ELEVATED - uncategorized tokens cluster at folio starts")
    elif start_ratio < 0.67:
        print("    STATUS: DEPLETED - uncategorized tokens avoid folio starts")
    else:
        print("    STATUS: NEUTRAL - no significant positional bias")

    return results


# ============================================================
# ANALYSIS 2: CONSTRAINT NEIGHBORHOOD
# ============================================================

def analyze_constraint_neighborhood(records: List[Dict],
                                    categorized: Set[str],
                                    token_info: Dict,
                                    hazard_tokens: Set[str],
                                    forbidden_pairs: Set[Tuple[str, str]]) -> Dict:
    """
    Measure whether uncategorized tokens appear in low-risk zones
    or cluster near hazard-involved tokens.
    Tests H2 (sensory judgment markers).
    """
    print("\n" + "="*60)
    print("ANALYSIS 2: CONSTRAINT NEIGHBORHOOD")
    print("="*60)

    # Build sequence by folio
    folios = defaultdict(list)
    for rec in records:
        folio = rec.get('folio', '')
        word = rec.get('word', '').lower().strip()
        if folio and word and not word.startswith('*'):
            folios[folio].append(word)

    # For each uncategorized token, check neighbors
    uncat_near_hazard = 0  # within 3 positions of hazard token
    uncat_not_near_hazard = 0
    cat_near_hazard = 0
    cat_not_near_hazard = 0

    # Check if uncategorized tokens avoid forbidden pair positions
    uncat_at_forbidden_seam = 0
    cat_at_forbidden_seam = 0
    total_forbidden_seams = 0

    window = 3  # check within 3 tokens

    for folio, tokens in folios.items():
        n = len(tokens)
        for i, tok in enumerate(tokens):
            is_cat = tok in categorized

            # Check if near a hazard-involved token
            near_hazard = False
            for j in range(max(0, i-window), min(n, i+window+1)):
                if j != i and tokens[j] in hazard_tokens:
                    near_hazard = True
                    break

            if is_cat:
                if near_hazard:
                    cat_near_hazard += 1
                else:
                    cat_not_near_hazard += 1
            else:
                if near_hazard:
                    uncat_near_hazard += 1
                else:
                    uncat_not_near_hazard += 1

            # Check forbidden seams (between consecutive tokens)
            if i < n - 1:
                next_tok = tokens[i + 1]
                if (tok, next_tok) in forbidden_pairs or (next_tok, tok) in forbidden_pairs:
                    total_forbidden_seams += 1
                    # Who is at the seam?
                    if tok not in categorized or next_tok not in categorized:
                        uncat_at_forbidden_seam += 1
                    else:
                        cat_at_forbidden_seam += 1

    total_cat = cat_near_hazard + cat_not_near_hazard
    total_uncat = uncat_near_hazard + uncat_not_near_hazard

    results = {
        'cat_near_hazard_rate': cat_near_hazard / total_cat if total_cat else 0,
        'uncat_near_hazard_rate': uncat_near_hazard / total_uncat if total_uncat else 0,
        'total_forbidden_seams': total_forbidden_seams,
        'uncat_at_seam': uncat_at_forbidden_seam,
        'cat_at_seam': cat_at_forbidden_seam,
    }

    print(f"\nProximity to hazard-involved tokens (within {window} positions):")
    print(f"  Categorized near hazard:   {100*results['cat_near_hazard_rate']:.1f}%")
    print(f"  Uncategorized near hazard: {100*results['uncat_near_hazard_rate']:.1f}%")

    hazard_ratio = results['uncat_near_hazard_rate'] / results['cat_near_hazard_rate'] if results['cat_near_hazard_rate'] else 0
    print(f"\n  Ratio (uncat/cat): {hazard_ratio:.2f}x")

    print(f"\nForbidden transition seams found: {total_forbidden_seams}")
    if total_forbidden_seams > 0:
        print(f"  Uncategorized at seam: {uncat_at_forbidden_seam} ({100*uncat_at_forbidden_seam/total_forbidden_seams:.1f}%)")
        print(f"  Categorized at seam:   {cat_at_forbidden_seam} ({100*cat_at_forbidden_seam/total_forbidden_seams:.1f}%)")

    # H2 assessment
    print(f"\n>>> H2 INDICATOR (sensory checkpoint proximity):")
    if hazard_ratio > 1.3:
        print("    STATUS: ELEVATED - uncategorized tokens cluster near hazard zones")
        print("    INTERPRETATION: May represent checkpoints before risky operations")
    elif hazard_ratio < 0.7:
        print("    STATUS: DEPLETED - uncategorized tokens avoid hazard zones")
        print("    INTERPRETATION: May represent safe/neutral annotations")
    else:
        print("    STATUS: NEUTRAL - no significant hazard proximity bias")

    return results


# ============================================================
# ANALYSIS 3: REPETITION & SEQUENCE PATTERNING
# ============================================================

def analyze_repetition_patterns(records: List[Dict],
                                categorized: Set[str]) -> Dict:
    """
    Analyze whether uncategorized tokens repeat locally, form runs,
    or behave like counters/tallies.
    Tests H3 (quantitative markers).
    """
    print("\n" + "="*60)
    print("ANALYSIS 3: REPETITION & SEQUENCE PATTERNING")
    print("="*60)

    # Build folio sequences
    folios = defaultdict(list)
    for rec in records:
        folio = rec.get('folio', '')
        word = rec.get('word', '').lower().strip()
        if folio and word and not word.startswith('*'):
            folios[folio].append(word)

    # Count immediate repetitions (same token twice in a row)
    cat_immediate_repeat = 0
    uncat_immediate_repeat = 0
    cat_total_transitions = 0
    uncat_total_transitions = 0

    # Count runs (3+ same token)
    cat_runs = []
    uncat_runs = []

    # Count local repetitions within window
    window = 10
    cat_local_repeat = 0
    uncat_local_repeat = 0

    for folio, tokens in folios.items():
        n = len(tokens)
        i = 0
        while i < n:
            tok = tokens[i]
            is_cat = tok in categorized

            # Check immediate repeat
            if i < n - 1 and tokens[i + 1] == tok:
                if is_cat:
                    cat_immediate_repeat += 1
                else:
                    uncat_immediate_repeat += 1

            # Track transitions
            if is_cat:
                cat_total_transitions += 1
            else:
                uncat_total_transitions += 1

            # Check for runs
            run_len = 1
            while i + run_len < n and tokens[i + run_len] == tok:
                run_len += 1

            if run_len >= 3:
                if is_cat:
                    cat_runs.append(run_len)
                else:
                    uncat_runs.append(run_len)

            # Check local repetition (same token within window)
            local_count = 0
            for j in range(max(0, i - window), min(n, i + window + 1)):
                if j != i and tokens[j] == tok:
                    local_count += 1
            if local_count > 0:
                if is_cat:
                    cat_local_repeat += 1
                else:
                    uncat_local_repeat += 1

            i += 1

    results = {
        'cat_immediate_repeat_rate': cat_immediate_repeat / cat_total_transitions if cat_total_transitions else 0,
        'uncat_immediate_repeat_rate': uncat_immediate_repeat / uncat_total_transitions if uncat_total_transitions else 0,
        'cat_runs': len(cat_runs),
        'uncat_runs': len(uncat_runs),
        'cat_local_repeat_rate': cat_local_repeat / cat_total_transitions if cat_total_transitions else 0,
        'uncat_local_repeat_rate': uncat_local_repeat / uncat_total_transitions if uncat_total_transitions else 0,
    }

    print(f"\nImmediate repetition (same token twice in a row):")
    print(f"  Categorized:   {100*results['cat_immediate_repeat_rate']:.2f}%")
    print(f"  Uncategorized: {100*results['uncat_immediate_repeat_rate']:.2f}%")

    print(f"\nRuns (3+ consecutive identical tokens):")
    print(f"  Categorized runs:   {len(cat_runs)}")
    print(f"  Uncategorized runs: {len(uncat_runs)}")
    if cat_runs:
        print(f"    Cat max run: {max(cat_runs)}, mean: {statistics.mean(cat_runs):.1f}")
    if uncat_runs:
        print(f"    Uncat max run: {max(uncat_runs)}, mean: {statistics.mean(uncat_runs):.1f}")

    print(f"\nLocal repetition (same token within {window}-token window):")
    print(f"  Categorized:   {100*results['cat_local_repeat_rate']:.2f}%")
    print(f"  Uncategorized: {100*results['uncat_local_repeat_rate']:.2f}%")

    repeat_ratio = results['uncat_immediate_repeat_rate'] / results['cat_immediate_repeat_rate'] if results['cat_immediate_repeat_rate'] else 0

    print(f"\n>>> H3 INDICATOR (quantitative/count-like behavior):")
    print(f"    Immediate repeat ratio (uncat/cat): {repeat_ratio:.2f}x")
    if repeat_ratio > 2.0:
        print("    STATUS: ELEVATED - uncategorized tokens repeat more frequently")
        print("    INTERPRETATION: May encode counts, tallies, or emphasis")
    elif repeat_ratio < 0.5:
        print("    STATUS: DEPLETED - uncategorized tokens rarely repeat")
    else:
        print("    STATUS: NEUTRAL - similar repetition behavior")

    return results


# ============================================================
# ANALYSIS 4: CO-OCCURRENCE WITH KNOWN CLASSES
# ============================================================

def analyze_cooccurrence(records: List[Dict],
                         categorized: Set[str],
                         token_info: Dict) -> Dict:
    """
    Test whether uncategorized tokens co-occur with specific instruction classes.
    Tests H4 (navigation scaffolding) and H5 (scribal variants).
    """
    print("\n" + "="*60)
    print("ANALYSIS 4: CO-OCCURRENCE WITH KNOWN CLASSES")
    print("="*60)

    # Build folio sequences
    folios = defaultdict(list)
    for rec in records:
        folio = rec.get('folio', '')
        word = rec.get('word', '').lower().strip()
        if folio and word and not word.startswith('*'):
            folios[folio].append(word)

    # For each uncategorized token type, count neighbors by role
    uncat_neighbor_roles = defaultdict(Counter)  # uncat_token -> Counter of neighbor roles
    role_neighbor_uncat = defaultdict(Counter)   # role -> Counter of nearby uncat tokens

    window = 2

    for folio, tokens in folios.items():
        n = len(tokens)
        for i, tok in enumerate(tokens):
            if tok in categorized:
                # This is categorized - check if uncategorized neighbors
                role = token_info[tok]['role']
                for j in range(max(0, i - window), min(n, i + window + 1)):
                    if j != i and tokens[j] not in categorized:
                        neighbor = tokens[j]
                        role_neighbor_uncat[role][neighbor] += 1
            else:
                # This is uncategorized - check categorized neighbors
                for j in range(max(0, i - window), min(n, i + window + 1)):
                    if j != i and tokens[j] in categorized:
                        neighbor_role = token_info[tokens[j]]['role']
                        uncat_neighbor_roles[tok][neighbor_role] += 1

    # Aggregate by role
    role_totals = Counter()
    for uncat_tok, role_counts in uncat_neighbor_roles.items():
        for role, count in role_counts.items():
            role_totals[role] += count

    print(f"\nUncategorized tokens neighboring each instruction role:")
    total_cooc = sum(role_totals.values())
    for role, count in role_totals.most_common():
        pct = 100 * count / total_cooc if total_cooc else 0
        print(f"  {role:20s}: {count:6d} ({pct:.1f}%)")

    # Find uncategorized tokens that strongly prefer certain roles
    print(f"\nTop uncategorized tokens by role preference:")
    uncat_freq = Counter()
    for folio, tokens in folios.items():
        for tok in tokens:
            if tok not in categorized:
                uncat_freq[tok] += 1

    # For top 20 most frequent uncategorized tokens, show their neighbor role profile
    print(f"\n  Top 20 uncategorized tokens and their dominant neighbor role:")
    for tok, freq in uncat_freq.most_common(20):
        if tok in uncat_neighbor_roles and uncat_neighbor_roles[tok]:
            dominant_role = uncat_neighbor_roles[tok].most_common(1)[0]
            total_neighbors = sum(uncat_neighbor_roles[tok].values())
            pct = 100 * dominant_role[1] / total_neighbors if total_neighbors else 0
            print(f"    {tok:15s} (n={freq:4d}): {dominant_role[0]:20s} ({pct:.0f}%)")

    results = {
        'role_cooccurrence': dict(role_totals),
        'unique_uncat_with_neighbors': len(uncat_neighbor_roles),
    }

    # H4 assessment - do uncategorized tokens act as boundaries between roles?
    print(f"\n>>> H4 INDICATOR (navigation/indexing behavior):")
    if len(role_totals) > 0:
        max_role = role_totals.most_common(1)[0]
        min_role = role_totals.most_common()[-1]
        ratio = max_role[1] / min_role[1] if min_role[1] else float('inf')
        print(f"    Role co-occurrence spread: {max_role[0]}={max_role[1]} to {min_role[0]}={min_role[1]}")
        print(f"    Max/min ratio: {ratio:.1f}x")
        if ratio > 3:
            print("    STATUS: UNEVEN - uncategorized tokens cluster near specific roles")
        else:
            print("    STATUS: DISTRIBUTED - uncategorized tokens appear across all roles")

    return results


# ============================================================
# ANALYSIS 5: TEMPORAL / FOLIO-BLOCK STRATIFICATION
# ============================================================

def analyze_temporal_stratification(records: List[Dict],
                                    categorized: Set[str]) -> Dict:
    """
    Segment manuscript into blocks and measure uncategorized token distribution.
    Tests for scribal drift, hand variation, or evolving practice.
    """
    print("\n" + "="*60)
    print("ANALYSIS 5: TEMPORAL / FOLIO-BLOCK STRATIFICATION")
    print("="*60)

    # Group by quire and section
    quire_stats = defaultdict(lambda: {'cat': 0, 'uncat': 0, 'uncat_types': set()})
    section_stats = defaultdict(lambda: {'cat': 0, 'uncat': 0, 'uncat_types': set()})
    hand_stats = defaultdict(lambda: {'cat': 0, 'uncat': 0, 'uncat_types': set()})
    folio_stats = defaultdict(lambda: {'cat': 0, 'uncat': 0, 'uncat_types': set()})

    folio_order = []
    seen_folios = set()

    for rec in records:
        word = rec.get('word', '').lower().strip()
        if not word or word.startswith('*'):
            continue

        quire = rec.get('quire', 'UNK')
        section = rec.get('section', 'UNK')
        hand = rec.get('hand', 'UNK')
        folio = rec.get('folio', 'UNK')

        if folio not in seen_folios:
            folio_order.append(folio)
            seen_folios.add(folio)

        is_cat = word in categorized

        for stats, key in [(quire_stats, quire), (section_stats, section),
                           (hand_stats, hand), (folio_stats, folio)]:
            if is_cat:
                stats[key]['cat'] += 1
            else:
                stats[key]['uncat'] += 1
                stats[key]['uncat_types'].add(word)

    print(f"\nBy QUIRE:")
    for quire in sorted(quire_stats.keys()):
        s = quire_stats[quire]
        total = s['cat'] + s['uncat']
        uncat_rate = s['uncat'] / total if total else 0
        diversity = len(s['uncat_types']) / s['uncat'] if s['uncat'] else 0
        print(f"  {quire}: {100*uncat_rate:.1f}% uncategorized, {len(s['uncat_types'])} types, diversity={diversity:.3f}")

    print(f"\nBy SECTION:")
    for section in sorted(section_stats.keys()):
        s = section_stats[section]
        total = s['cat'] + s['uncat']
        uncat_rate = s['uncat'] / total if total else 0
        print(f"  {section}: {100*uncat_rate:.1f}% uncategorized ({s['uncat']} tokens, {len(s['uncat_types'])} types)")

    print(f"\nBy HAND:")
    for hand in sorted(hand_stats.keys()):
        s = hand_stats[hand]
        total = s['cat'] + s['uncat']
        if total > 100:  # only show hands with significant data
            uncat_rate = s['uncat'] / total if total else 0
            print(f"  Hand {hand}: {100*uncat_rate:.1f}% uncategorized ({total} tokens)")

    # Compute temporal trend (by folio order)
    print(f"\nTemporal trend (first third / middle third / last third of folios):")
    n_folios = len(folio_order)
    third = n_folios // 3

    periods = [
        ('FIRST_THIRD', folio_order[:third]),
        ('MIDDLE_THIRD', folio_order[third:2*third]),
        ('LAST_THIRD', folio_order[2*third:])
    ]

    period_rates = []
    for name, period_folios in periods:
        cat_total = sum(folio_stats[f]['cat'] for f in period_folios)
        uncat_total = sum(folio_stats[f]['uncat'] for f in period_folios)
        total = cat_total + uncat_total
        rate = uncat_total / total if total else 0
        period_rates.append(rate)
        print(f"  {name}: {100*rate:.1f}% uncategorized")

    # Check for vocabulary drift
    first_types = set()
    last_types = set()
    for f in folio_order[:third]:
        first_types.update(folio_stats[f]['uncat_types'])
    for f in folio_order[2*third:]:
        last_types.update(folio_stats[f]['uncat_types'])

    shared = first_types & last_types
    first_only = first_types - last_types
    last_only = last_types - first_types

    print(f"\nVocabulary overlap (first vs last third):")
    print(f"  First third unique types: {len(first_types)}")
    print(f"  Last third unique types:  {len(last_types)}")
    print(f"  Shared types:             {len(shared)} ({100*len(shared)/len(first_types|last_types):.1f}%)")
    print(f"  First-only types:         {len(first_only)}")
    print(f"  Last-only types:          {len(last_only)}")

    results = {
        'quire_stats': {k: {'cat': v['cat'], 'uncat': v['uncat'], 'types': len(v['uncat_types'])}
                        for k, v in quire_stats.items()},
        'period_rates': period_rates,
        'vocabulary_overlap': len(shared) / len(first_types | last_types) if first_types | last_types else 0,
    }

    # H5 assessment
    print(f"\n>>> H5 INDICATOR (scribal drift / hand variation):")
    trend = period_rates[2] - period_rates[0]  # last minus first
    print(f"    Temporal trend (last - first): {100*trend:+.1f} percentage points")
    overlap = results['vocabulary_overlap']
    print(f"    Vocabulary overlap (first/last): {100*overlap:.1f}%")

    if abs(trend) > 5 or overlap < 0.5:
        print("    STATUS: DRIFT DETECTED - uncategorized vocabulary changes through manuscript")
    else:
        print("    STATUS: STABLE - uncategorized vocabulary consistent throughout")

    return results


# ============================================================
# HYPOTHESIS EVALUATION
# ============================================================

def evaluate_hypotheses(results: Dict) -> None:
    """Generate hypothesis evaluation summary."""
    print("\n" + "="*60)
    print("HYPOTHESIS EVALUATION SUMMARY")
    print("="*60)

    p = results['positional']
    c = results['constraint']
    r = results['repetition']
    o = results['cooccurrence']
    t = results['temporal']

    print("""
+-----------------------------------------------------------------------------+
| HYPOTHESIS                | EVIDENCE FOR       | EVIDENCE AGAINST | VERDICT |
+-----------------------------------------------------------------------------+""")

    # H1: Initial/Boundary Conditions
    h1_for = []
    h1_against = []
    start_ratio = p['uncat_start_rate'] / p['cat_start_rate'] if p['cat_start_rate'] else 0
    if start_ratio > 1.2:
        h1_for.append("Higher start concentration")
    elif start_ratio < 0.8:
        h1_against.append("Lower start concentration")
    else:
        h1_against.append("No positional bias")

    h1_verdict = "WEAK" if len(h1_against) > len(h1_for) else "MODERATE" if h1_for else "NULL"

    print(f"| H1: Boundary Conditions   | {','.join(h1_for) or 'None':18s} | {','.join(h1_against) or 'None':16s} | {h1_verdict:7s} |")

    # H2: Sensory Judgment
    h2_for = []
    h2_against = []
    hazard_ratio = c['uncat_near_hazard_rate'] / c['cat_near_hazard_rate'] if c['cat_near_hazard_rate'] else 0
    if hazard_ratio > 1.2:
        h2_for.append("Cluster near hazards")
    elif hazard_ratio < 0.8:
        h2_against.append("Avoid hazard zones")
    else:
        h2_against.append("No hazard preference")

    h2_verdict = "MODERATE" if h2_for else "WEAK" if h2_against else "NULL"

    print(f"| H2: Sensory Checkpoints   | {','.join(h2_for) or 'None':18s} | {','.join(h2_against) or 'None':16s} | {h2_verdict:7s} |")

    # H3: Quantitative Markers
    h3_for = []
    h3_against = []
    repeat_ratio = r['uncat_immediate_repeat_rate'] / r['cat_immediate_repeat_rate'] if r['cat_immediate_repeat_rate'] else 0
    if repeat_ratio > 1.5:
        h3_for.append("Higher repetition")
    if r['uncat_runs'] > r['cat_runs'] * 1.5:
        h3_for.append("More runs")
    if repeat_ratio < 0.8:
        h3_against.append("Lower repetition")
    if not h3_for and not h3_against:
        h3_against.append("Similar repetition")

    h3_verdict = "MODERATE" if len(h3_for) >= 2 else "WEAK" if h3_for else "NULL"

    print(f"| H3: Quantitative Markers  | {','.join(h3_for) or 'None':18s} | {','.join(h3_against) or 'None':16s} | {h3_verdict:7s} |")

    # H4: Navigation/Indexing
    h4_for = []
    h4_against = []
    # Check if role distribution is uneven
    role_counts = list(o['role_cooccurrence'].values()) if o['role_cooccurrence'] else [1]
    if max(role_counts) / min(role_counts) > 3 if min(role_counts) else False:
        h4_for.append("Uneven role clustering")
    else:
        h4_against.append("Distributed across roles")

    h4_verdict = "MODERATE" if h4_for else "WEAK"

    print(f"| H4: Navigation Scaffolding| {','.join(h4_for) or 'None':18s} | {','.join(h4_against) or 'None':16s} | {h4_verdict:7s} |")

    # H5: Scribal Variants
    h5_for = []
    h5_against = []
    trend = abs(t['period_rates'][2] - t['period_rates'][0])
    overlap = t['vocabulary_overlap']
    if trend > 0.05:
        h5_for.append("Temporal variation")
    if overlap < 0.5:
        h5_for.append("Vocabulary drift")
    if trend < 0.03 and overlap > 0.6:
        h5_against.append("Stable through MS")

    h5_verdict = "MODERATE" if len(h5_for) >= 2 else "WEAK" if h5_for else "NULL"

    print(f"| H5: Scribal Variants      | {','.join(h5_for) or 'None':18s} | {','.join(h5_against) or 'None':16s} | {h5_verdict:7s} |")

    print("+-----------------------------------------------------------------------------+")

    print("""
KEY FINDINGS:
""")

    # Determine strongest signal
    verdicts = {
        'H1 Boundary Conditions': (h1_verdict, h1_for, h1_against),
        'H2 Sensory Checkpoints': (h2_verdict, h2_for, h2_against),
        'H3 Quantitative Markers': (h3_verdict, h3_for, h3_against),
        'H4 Navigation Scaffolding': (h4_verdict, h4_for, h4_against),
        'H5 Scribal Variants': (h5_verdict, h5_for, h5_against),
    }

    strong = [k for k, v in verdicts.items() if v[0] == 'MODERATE']
    null = [k for k, v in verdicts.items() if v[0] == 'NULL']

    if strong:
        print(f"  STRONGEST SIGNALS: {', '.join(strong)}")
    if null:
        print(f"  NO SUPPORT: {', '.join(null)}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("="*60)
    print("BEHAVIORAL ROLE ANALYSIS OF UNCATEGORIZED TOKENS")
    print("MODEL DIAGNOSTIC - NOT GRAMMAR EXPANSION")
    print("="*60)

    # Load data
    print("\nLoading data...")
    records = load_transcription()
    print(f"  Loaded {len(records)} transcription records")

    categorized, token_info = load_categorized_tokens()
    print(f"  Loaded {len(categorized)} categorized tokens (Phase 20A)")

    forbidden_pairs = load_forbidden_pairs()
    print(f"  Loaded {len(forbidden_pairs)//2} forbidden transitions")

    hazard_tokens = get_hazard_involved_tokens()
    print(f"  Identified {len(hazard_tokens)} hazard-involved tokens")

    # Run all analyses
    results = {}

    results['positional'] = analyze_positional_distribution(records, categorized)
    results['constraint'] = analyze_constraint_neighborhood(records, categorized,
                                                            token_info, hazard_tokens,
                                                            forbidden_pairs)
    results['repetition'] = analyze_repetition_patterns(records, categorized)
    results['cooccurrence'] = analyze_cooccurrence(records, categorized, token_info)
    results['temporal'] = analyze_temporal_stratification(records, categorized)

    # Final evaluation
    evaluate_hypotheses(results)

    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)

    return results


if __name__ == '__main__':
    main()
