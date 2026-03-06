"""
Phase 543: Hazard-Class Decomposition at Atom Resolution
=========================================================

Maps the 5 hazard failure classes (C109) onto the atom-mechanical frame system
(HEAD x TERM combinations) established in Phases 523-535.

Research question: Which hazard class maps to which atom-mechanical frame?

Four test dimensions:
  A: Hazard class by HEAD x TERM frame
  B: Hazard class by modifier quenching
  C: Hazard class by PREFIX channel
  D: Hazard class by line zone (Q0-Q4)

Uses authoritative hazard class assignments from Phase 18
(phases/15-20_kernel_grammar/phase18c_failure_taxonomy.json).
"""

import sys
import os
import json
import numpy as np
from collections import defaultdict, Counter
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import Transcript, Morphology

# ============================================================================
# AUTHORITATIVE HAZARD CLASS ASSIGNMENTS (Phase 18, C109)
# Source: phases/15-20_kernel_grammar/phase18c_failure_taxonomy.json
# ============================================================================

HAZARD_CLASSES = {
    'PHASE_ORDERING': [
        ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
        ('dy', 'aiin'), ('dy', 'chey'),
        ('chey', 'chedy'), ('chey', 'shedy')
    ],
    'COMPOSITION_JUMP': [
        ('chedy', 'ee'), ('c', 'ee'),
        ('shedy', 'aiin'), ('shedy', 'o')
    ],
    'CONTAINMENT_TIMING': [
        ('chol', 'r'), ('l', 'chol'),
        ('or', 'dal'), ('he', 'or')
    ],
    'RATE_MISMATCH': [
        ('ar', 'dal')
    ],
    'ENERGY_OVERSHOOT': [
        ('he', 't')
    ]
}

# All 17 forbidden pairs as flat set for quick lookup
FORBIDDEN_PAIRS = set()
for cls, pairs in HAZARD_CLASSES.items():
    for src, tgt in pairs:
        FORBIDDEN_PAIRS.add((src, tgt))

# Reverse lookup: (src, tgt) -> hazard class
PAIR_TO_CLASS = {}
for cls, pairs in HAZARD_CLASSES.items():
    for src, tgt in pairs:
        PAIR_TO_CLASS[(src, tgt)] = cls

# ============================================================================
# ATOM CLASSIFICATION (from C1393-C1394)
# ============================================================================

HEAD_ATOMS = {'a', 'e', 'o', 'k', 't'}
MODIFIER_ATOMS = {'p', 'i', 'c', 'f', 'd', 's'}
TERMINAL_ATOMS = {'l', 'r', 'h', 'y', 'm', 'n'}
# k and t are dual-role (HEAD or TERMINAL)

def decompose_middle(middle):
    """Decompose a MIDDLE into HEAD, MOD*, TERM slots."""
    if not middle or len(middle) == 0:
        return None

    atoms = list(middle)
    if len(atoms) == 1:
        atom = atoms[0]
        return {
            'head': atom,
            'mods': [],
            'term': atom,  # single atom = both head and term
            'atoms': atoms,
            'raw': middle,
            'is_single': True
        }

    head = atoms[0]
    term = atoms[-1]
    mods = atoms[1:-1] if len(atoms) > 2 else []

    return {
        'head': head,
        'mods': mods,
        'term': term,
        'atoms': atoms,
        'raw': middle,
        'is_single': False
    }

def get_head_category(head):
    """Classify HEAD atom."""
    if head in HEAD_ATOMS:
        return head
    elif head in MODIFIER_ATOMS:
        return 'headless'
    elif head in TERMINAL_ATOMS:
        return 'headless'
    return head

def has_modifier(decomp):
    """Check if MIDDLE has any modifier atoms."""
    if decomp is None or decomp['is_single']:
        return False
    return len(decomp['mods']) > 0

def get_frame(decomp):
    """Get HEAD x TERM frame string."""
    if decomp is None:
        return None
    if decomp['is_single']:
        return f"{decomp['head']}->bare"
    return f"{decomp['head']}->{decomp['term']}"

# ============================================================================
# DATA COLLECTION
# ============================================================================

def collect_b_tokens():
    """Collect all Currier B tokens with full decomposition."""
    tx = Transcript()
    morph = Morphology()

    all_tokens = []
    adjacency_pairs = []
    tokens_by_folio_line = defaultdict(list)

    prev_token = None
    prev_folio_line = None

    for token in tx.currier_b():
        # Skip uncertain tokens
        if token.is_uncertain:
            continue
        # Skip empty
        word = token.word.strip()
        if not word:
            continue
        # Skip labels
        if token.is_label:
            continue

        # Morphological decomposition
        m = morph.extract(word)
        middle = m.middle if m else word
        prefix = m.prefix if m else ''
        suffix = m.suffix if m else ''
        articulator = m.articulator if m else ''

        # Decompose MIDDLE into atoms
        mid_decomp = decompose_middle(middle)

        # Determine suffix mode
        if suffix:
            # Terminal suffixes = Mode A (specification)
            terminal_suffixes = {'y', 'dy', 'edy', 'eedy', 'hy', 'ly', 'ry',
                                'or', 'ar', 'al', 'ol', 'am', 'om', 'aiin',
                                'iin', 'ain', 'oiin'}
            # Check if suffix matches terminal pattern
            if suffix in terminal_suffixes or suffix.endswith('y') or suffix.endswith('m') or suffix.endswith('r') or suffix.endswith('l'):
                suffix_mode = 'A'
            else:
                suffix_mode = 'B'
        else:
            suffix_mode = 'B'  # bare = Mode B (continuation)

        # Get line position info
        folio = token.folio
        line = token.line
        folio_line = (folio, line)

        token_info = {
            'word': word,
            'folio': folio,
            'line': line,
            'middle': middle,
            'prefix': prefix or '',
            'suffix': suffix or '',
            'articulator': articulator or '',
            'suffix_mode': suffix_mode,
            'decomp': mid_decomp,
            'frame': get_frame(mid_decomp),
            'has_modifier': has_modifier(mid_decomp),
            'head': mid_decomp['head'] if mid_decomp else None,
            'term': mid_decomp['term'] if mid_decomp else None,
        }

        all_tokens.append(token_info)
        tokens_by_folio_line[folio_line].append(token_info)

        # Build adjacency pairs (same line only)
        if prev_token is not None and prev_folio_line == folio_line:
            adjacency_pairs.append((prev_token, token_info))

        prev_token = token_info
        prev_folio_line = folio_line

    # Compute line positions (quintiles Q0-Q4)
    for folio_line, tokens in tokens_by_folio_line.items():
        n = len(tokens)
        for i, tok in enumerate(tokens):
            if n == 1:
                tok['line_pos'] = 0.5
                tok['quintile'] = 2  # middle
            else:
                tok['line_pos'] = i / (n - 1)
                tok['quintile'] = min(4, int(tok['line_pos'] * 5))

    return all_tokens, adjacency_pairs, tokens_by_folio_line


# ============================================================================
# DIMENSION A: Hazard class by HEAD x TERM frame
# ============================================================================

def analyze_dimension_a(adjacency_pairs):
    """Map each hazard class to its HEAD x TERM frame distribution."""
    print("\n=== DIMENSION A: Hazard class by HEAD x TERM frame ===\n")

    results = {}

    # For each forbidden pair, decompose source and target MIDDLEs
    pair_decompositions = {}
    for (src_mid, tgt_mid), haz_class in PAIR_TO_CLASS.items():
        src_decomp = decompose_middle(src_mid)
        tgt_decomp = decompose_middle(tgt_mid)

        src_frame = get_frame(src_decomp)
        tgt_frame = get_frame(tgt_decomp)
        src_head = get_head_category(src_decomp['head']) if src_decomp else None
        tgt_head = get_head_category(tgt_decomp['head']) if tgt_decomp else None

        pair_decompositions[(src_mid, tgt_mid)] = {
            'hazard_class': haz_class,
            'source_middle': src_mid,
            'target_middle': tgt_mid,
            'source_decomp': {
                'head': src_decomp['head'] if src_decomp else None,
                'mods': src_decomp['mods'] if src_decomp else [],
                'term': src_decomp['term'] if src_decomp else None,
                'frame': src_frame,
                'head_category': src_head,
                'has_modifier': has_modifier(src_decomp),
            },
            'target_decomp': {
                'head': tgt_decomp['head'] if tgt_decomp else None,
                'mods': tgt_decomp['mods'] if tgt_decomp else [],
                'term': tgt_decomp['term'] if tgt_decomp else None,
                'frame': tgt_frame,
                'head_category': tgt_head,
                'has_modifier': has_modifier(tgt_decomp),
            }
        }

    # Aggregate by hazard class
    class_frame_profiles = {}
    for haz_class in HAZARD_CLASSES:
        source_heads = Counter()
        target_heads = Counter()
        source_terms = Counter()
        target_terms = Counter()
        source_frames = Counter()
        target_frames = Counter()
        source_mods = Counter()
        target_mods = Counter()
        n_with_mods_src = 0
        n_with_mods_tgt = 0

        for src_mid, tgt_mid in HAZARD_CLASSES[haz_class]:
            pd = pair_decompositions[(src_mid, tgt_mid)]
            source_heads[pd['source_decomp']['head']] += 1
            target_heads[pd['target_decomp']['head']] += 1
            source_terms[pd['source_decomp']['term']] += 1
            target_terms[pd['target_decomp']['term']] += 1
            source_frames[pd['source_decomp']['frame']] += 1
            target_frames[pd['target_decomp']['frame']] += 1
            if pd['source_decomp']['has_modifier']:
                n_with_mods_src += 1
                for mod in pd['source_decomp']['mods']:
                    source_mods[mod] += 1
            if pd['target_decomp']['has_modifier']:
                n_with_mods_tgt += 1
                for mod in pd['target_decomp']['mods']:
                    target_mods[mod] += 1

        n_pairs = len(HAZARD_CLASSES[haz_class])

        class_frame_profiles[haz_class] = {
            'n_pairs': n_pairs,
            'source_heads': dict(source_heads),
            'target_heads': dict(target_heads),
            'source_terms': dict(source_terms),
            'target_terms': dict(target_terms),
            'source_frames': dict(source_frames),
            'target_frames': dict(target_frames),
            'source_mods': dict(source_mods),
            'target_mods': dict(target_mods),
            'source_modifier_rate': n_with_mods_src / n_pairs if n_pairs > 0 else 0,
            'target_modifier_rate': n_with_mods_tgt / n_pairs if n_pairs > 0 else 0,
        }

        print(f"\n{haz_class} ({n_pairs} pairs):")
        print(f"  Source HEADs: {dict(source_heads)}")
        print(f"  Target HEADs: {dict(target_heads)}")
        print(f"  Source TERMs: {dict(source_terms)}")
        print(f"  Target TERMs: {dict(target_terms)}")
        print(f"  Source frames: {dict(source_frames)}")
        print(f"  Target frames: {dict(target_frames)}")
        print(f"  Source modifier rate: {n_with_mods_src}/{n_pairs} = {n_with_mods_src/n_pairs:.1%}")
        print(f"  Target modifier rate: {n_with_mods_tgt}/{n_pairs} = {n_with_mods_tgt/n_pairs:.1%}")

    # Count actual violations by hazard class in the corpus
    class_violation_counts = Counter()
    class_near_miss_counts = Counter()

    for src_tok, tgt_tok in adjacency_pairs:
        pair = (src_tok['middle'], tgt_tok['middle'])
        if pair in PAIR_TO_CLASS:
            class_violation_counts[PAIR_TO_CLASS[pair]] += 1

    print("\n\nActual corpus violations by hazard class:")
    for haz_class in HAZARD_CLASSES:
        count = class_violation_counts.get(haz_class, 0)
        print(f"  {haz_class}: {count}")

    # Count near-misses: adjacency pairs where source or target is a forbidden MIDDLE
    forbidden_sources = set()
    forbidden_targets = set()
    for src, tgt in FORBIDDEN_PAIRS:
        forbidden_sources.add(src)
        forbidden_targets.add(tgt)

    # Near miss = source IS a forbidden source but actual target is NOT the forbidden target
    # OR target IS a forbidden target but actual source is NOT the forbidden source
    near_miss_by_class = defaultdict(lambda: {'source_appeared': 0, 'target_appeared': 0})

    source_to_classes = defaultdict(set)
    target_to_classes = defaultdict(set)
    for (src, tgt), cls in PAIR_TO_CLASS.items():
        source_to_classes[src].add(cls)
        target_to_classes[tgt].add(cls)

    for src_tok, tgt_tok in adjacency_pairs:
        src_mid = src_tok['middle']
        tgt_mid = tgt_tok['middle']

        if src_mid in forbidden_sources:
            for cls in source_to_classes[src_mid]:
                near_miss_by_class[cls]['source_appeared'] += 1
        if tgt_mid in forbidden_targets:
            for cls in target_to_classes[tgt_mid]:
                near_miss_by_class[cls]['target_appeared'] += 1

    print("\nNear-miss context (forbidden source/target appearances):")
    for haz_class in HAZARD_CLASSES:
        nm = near_miss_by_class.get(haz_class, {'source_appeared': 0, 'target_appeared': 0})
        violations = class_violation_counts.get(haz_class, 0)
        total_appearances = nm['source_appeared']
        avoidance_rate = 1 - (violations / total_appearances) if total_appearances > 0 else 1.0
        print(f"  {haz_class}: source appeared {nm['source_appeared']}x, target appeared {nm['target_appeared']}x, "
              f"violations={violations}, avoidance={avoidance_rate:.4f}")

    results['pair_decompositions'] = {f"{s}->{t}": v for (s, t), v in pair_decompositions.items()}
    results['class_frame_profiles'] = class_frame_profiles
    results['corpus_violations'] = dict(class_violation_counts)
    results['near_miss_context'] = {k: dict(v) for k, v in near_miss_by_class.items()}

    return results


# ============================================================================
# DIMENSION B: Hazard class by modifier quenching
# ============================================================================

def analyze_dimension_b(all_tokens, adjacency_pairs):
    """Test whether modifier quenching (C1450) is hazard-class selective."""
    print("\n=== DIMENSION B: Hazard class by modifier quenching ===\n")

    results = {}

    # For each hazard class, find tokens whose MIDDLEs participate in forbidden pairs
    # and check if having a modifier changes hazard exposure

    # Collect all MIDDLEs that are sources in forbidden pairs, grouped by class
    class_source_middles = defaultdict(set)
    class_target_middles = defaultdict(set)
    for cls, pairs in HAZARD_CLASSES.items():
        for src, tgt in pairs:
            class_source_middles[cls].add(src)
            class_target_middles[cls].add(tgt)

    # For each token, check if its MIDDLE's HEAD matches any forbidden source HEAD
    # and whether modifier presence changes hazard exposure

    # First, decompose all forbidden source MIDDLEs
    forbidden_source_decomps = {}
    for src_mid in set().union(*class_source_middles.values()):
        forbidden_source_decomps[src_mid] = decompose_middle(src_mid)

    # Group tokens by HEAD atom and modifier presence
    head_mod_hazard = defaultdict(lambda: {'with_mod': {'total': 0, 'hazard': 0},
                                            'no_mod': {'total': 0, 'hazard': 0}})

    # For hazard classification, use adjacency: a token is "hazardous" if it
    # appears as a source in a forbidden pair context
    token_hazard_status = {}
    for i, (src_tok, tgt_tok) in enumerate(adjacency_pairs):
        pair = (src_tok['middle'], tgt_tok['middle'])
        if pair in PAIR_TO_CLASS:
            token_hazard_status[id(src_tok)] = PAIR_TO_CLASS[pair]

    # Check all forbidden source MIDDLEs: which ones have modifiers?
    print("Forbidden source MIDDLEs and their modifier status:")
    for cls in HAZARD_CLASSES:
        print(f"\n  {cls}:")
        for src_mid in class_source_middles[cls]:
            d = forbidden_source_decomps[src_mid]
            print(f"    {src_mid}: HEAD={d['head']}, MODs={d['mods']}, TERM={d['term']}, "
                  f"has_modifier={has_modifier(d)}")

    # Now check: for each HEAD that participates in forbidden sources,
    # do MIDDLEs with modifiers added to that HEAD still participate?
    # i.e., if 'dy' is forbidden source (HEAD=d, TERM=y),
    # are 'diy', 'dcy', 'dpy' etc. also hazardous?

    # Collect all tokens grouped by HEAD
    tokens_by_head = defaultdict(list)
    for tok in all_tokens:
        if tok['head']:
            tokens_by_head[tok['head']].append(tok)

    # For each hazard class, look at the HEADs involved and check
    # whether modifier presence changes hazard proximity
    class_modifier_analysis = {}
    for cls in HAZARD_CLASSES:
        heads_involved = set()
        for src_mid in class_source_middles[cls]:
            d = decompose_middle(src_mid)
            heads_involved.add(d['head'])

        # For each HEAD involved, find all tokens with that HEAD
        # and compare hazard-adjacent rate with/without modifiers
        head_results = {}
        for head in heads_involved:
            head_tokens = tokens_by_head.get(head, [])
            with_mod = {'total': 0, 'near_forbidden': 0}
            without_mod = {'total': 0, 'near_forbidden': 0}

            for tok in head_tokens:
                is_near = tok['middle'] in class_source_middles[cls]
                if tok['has_modifier']:
                    with_mod['total'] += 1
                    if is_near:
                        with_mod['near_forbidden'] += 1
                else:
                    without_mod['total'] += 1
                    if is_near:
                        without_mod['near_forbidden'] += 1

            head_results[head] = {
                'with_modifier': with_mod,
                'without_modifier': without_mod,
            }

        class_modifier_analysis[cls] = {
            'heads_involved': list(heads_involved),
            'head_results': head_results,
        }

        print(f"\n{cls} - HEAD involvement:")
        for head, hr in head_results.items():
            wm = hr['with_modifier']
            nm = hr['without_modifier']
            wm_rate = wm['near_forbidden']/wm['total'] if wm['total'] > 0 else 0
            nm_rate = nm['near_forbidden']/nm['total'] if nm['total'] > 0 else 0
            print(f"  HEAD={head}: with_mod {wm['near_forbidden']}/{wm['total']} ({wm_rate:.3f}), "
                  f"no_mod {nm['near_forbidden']}/{nm['total']} ({nm_rate:.3f})")

    # Check which specific modifiers appear in forbidden MIDDLEs
    mod_in_forbidden = Counter()
    for src_mid in set().union(*class_source_middles.values()):
        d = decompose_middle(src_mid)
        for mod in d['mods']:
            mod_in_forbidden[mod] += 1
    for tgt_mid in set().union(*class_target_middles.values()):
        d = decompose_middle(tgt_mid)
        for mod in d['mods']:
            mod_in_forbidden[mod] += 1

    print(f"\nModifier atoms in forbidden MIDDLEs: {dict(mod_in_forbidden)}")

    # Which modifiers appear in which hazard class's forbidden MIDDLEs?
    class_mod_profile = {}
    for cls in HAZARD_CLASSES:
        mods_in_class = Counter()
        all_mids = class_source_middles[cls] | class_target_middles[cls]
        for mid in all_mids:
            d = decompose_middle(mid)
            for mod in d['mods']:
                mods_in_class[mod] += 1
        class_mod_profile[cls] = dict(mods_in_class)
        print(f"  {cls} modifiers: {dict(mods_in_class)}")

    # C1450 quenching test: do c/d/f/p/s modifiers quench all classes equally?
    quench_mods = {'c', 'd', 'f', 'p', 's'}

    # For each hazard class, count how many forbidden MIDDLEs contain quench modifiers
    quench_by_class = {}
    for cls in HAZARD_CLASSES:
        all_mids = list(class_source_middles[cls]) + [tgt for _, tgt in HAZARD_CLASSES[cls]]
        n_total = len(all_mids)
        n_with_quench = 0
        for mid in all_mids:
            d = decompose_middle(mid)
            if any(m in quench_mods for m in d['mods']):
                n_with_quench += 1
        quench_by_class[cls] = {
            'total_middles': n_total,
            'with_quench_mod': n_with_quench,
            'rate': n_with_quench / n_total if n_total > 0 else 0
        }
        print(f"  {cls}: {n_with_quench}/{n_total} forbidden MIDDLEs have quench modifiers "
              f"({quench_by_class[cls]['rate']:.1%})")

    results['class_modifier_analysis'] = class_modifier_analysis
    results['modifier_in_forbidden'] = dict(mod_in_forbidden)
    results['class_modifier_profile'] = class_mod_profile
    results['quench_by_class'] = quench_by_class

    return results


# ============================================================================
# DIMENSION C: Hazard class by PREFIX channel
# ============================================================================

def analyze_dimension_c(all_tokens, adjacency_pairs):
    """Test whether hazard class distribution differs across PREFIX channels."""
    print("\n=== DIMENSION C: Hazard class by PREFIX channel ===\n")

    results = {}

    # Define PREFIX channels
    def get_prefix_channel(prefix):
        if not prefix:
            return 'BARE'
        if prefix in ('ch', 'sh'):
            return 'CHSH'
        if prefix in ('ok', 'ot'):
            return 'OKOT'
        if prefix == 'qo':
            return 'QO'
        if prefix == 'da':
            return 'DA'
        if prefix in ('ol', 'or', 'al', 'ar'):
            return 'OL_FAMILY'
        if prefix in ('pch', 'tch', 'dch', 'lch', 'te'):
            return 'PREP'
        return 'OTHER'

    # For each adjacency pair that IS a forbidden pair, record the PREFIX of the source token
    violation_by_prefix_channel = defaultdict(lambda: defaultdict(int))

    # Also count total adjacency pairs by source PREFIX channel
    total_by_prefix_channel = Counter()

    for src_tok, tgt_tok in adjacency_pairs:
        src_channel = get_prefix_channel(src_tok['prefix'])
        total_by_prefix_channel[src_channel] += 1

        pair = (src_tok['middle'], tgt_tok['middle'])
        if pair in PAIR_TO_CLASS:
            haz_class = PAIR_TO_CLASS[pair]
            violation_by_prefix_channel[src_channel][haz_class] += 1

    print("Forbidden violations by PREFIX channel x hazard class:")
    for channel in sorted(total_by_prefix_channel.keys()):
        total = total_by_prefix_channel[channel]
        violations = violation_by_prefix_channel.get(channel, {})
        total_violations = sum(violations.values())
        rate = total_violations / total if total > 0 else 0
        print(f"\n  {channel} (N={total}, violations={total_violations}, rate={rate:.5f}):")
        for cls in HAZARD_CLASSES:
            v = violations.get(cls, 0)
            if v > 0:
                print(f"    {cls}: {v}")

    # Now look at the forbidden MIDDLEs themselves and their typical PREFIX contexts
    # For each forbidden source MIDDLE, what PREFIX does it typically carry?
    forbidden_source_mids = set()
    for pairs in HAZARD_CLASSES.values():
        for src, tgt in pairs:
            forbidden_source_mids.add(src)

    mid_prefix_dist = defaultdict(Counter)
    for tok in all_tokens:
        if tok['middle'] in forbidden_source_mids:
            channel = get_prefix_channel(tok['prefix'])
            mid_prefix_dist[tok['middle']][channel] += 1

    print("\n\nForbidden source MIDDLEs and their typical PREFIX channels:")
    for mid in sorted(forbidden_source_mids):
        dist = mid_prefix_dist.get(mid, Counter())
        total = sum(dist.values())
        # Find which hazard classes this MIDDLE participates in
        classes = [cls for cls, pairs in HAZARD_CLASSES.items()
                   for src, tgt in pairs if src == mid]
        print(f"  {mid} [{', '.join(classes)}] (N={total}): {dict(dist)}")

    # Aggregate: for each hazard class, what is the dominant PREFIX channel?
    class_prefix_profile = {}
    for cls in HAZARD_CLASSES:
        channel_counts = Counter()
        for src_mid in set(src for src, tgt in HAZARD_CLASSES[cls]):
            for channel, count in mid_prefix_dist.get(src_mid, {}).items():
                channel_counts[channel] += count
        total = sum(channel_counts.values())
        class_prefix_profile[cls] = {
            'total_tokens': total,
            'channel_distribution': {k: v/total if total > 0 else 0 for k, v in channel_counts.items()},
            'channel_counts': dict(channel_counts),
        }
        print(f"\n  {cls} PREFIX channel profile (N={total}):")
        for ch, frac in sorted(class_prefix_profile[cls]['channel_distribution'].items(),
                                key=lambda x: -x[1]):
            print(f"    {ch}: {frac:.1%} ({channel_counts.get(ch, 0)})")

    # Sister pair analysis: ch vs sh hazard class distribution
    ch_class_counts = Counter()
    sh_class_counts = Counter()
    ch_total = 0
    sh_total = 0

    for src_tok, tgt_tok in adjacency_pairs:
        if src_tok['prefix'] == 'ch':
            ch_total += 1
            pair = (src_tok['middle'], tgt_tok['middle'])
            if pair in PAIR_TO_CLASS:
                ch_class_counts[PAIR_TO_CLASS[pair]] += 1
        elif src_tok['prefix'] == 'sh':
            sh_total += 1
            pair = (src_tok['middle'], tgt_tok['middle'])
            if pair in PAIR_TO_CLASS:
                sh_class_counts[PAIR_TO_CLASS[pair]] += 1

    print(f"\n\nSister pair hazard class distribution:")
    print(f"  ch (N={ch_total}): {dict(ch_class_counts)}")
    print(f"  sh (N={sh_total}): {dict(sh_class_counts)}")

    results['violation_by_prefix_channel'] = {k: dict(v) for k, v in violation_by_prefix_channel.items()}
    results['total_by_prefix_channel'] = dict(total_by_prefix_channel)
    results['forbidden_source_prefix_distribution'] = {k: dict(v) for k, v in mid_prefix_dist.items()}
    results['class_prefix_profile'] = class_prefix_profile
    results['sister_pair_hazard'] = {
        'ch': {'total': ch_total, 'violations': dict(ch_class_counts)},
        'sh': {'total': sh_total, 'violations': dict(sh_class_counts)},
    }

    return results


# ============================================================================
# DIMENSION D: Hazard class by line zone
# ============================================================================

def analyze_dimension_d(all_tokens, adjacency_pairs):
    """Test whether hazard classes partition differently across line positions."""
    print("\n=== DIMENSION D: Hazard class by line zone (Q0-Q4) ===\n")

    results = {}

    # For each forbidden source MIDDLE, compute its positional distribution
    forbidden_source_mids = set()
    source_to_class = defaultdict(set)
    for cls, pairs in HAZARD_CLASSES.items():
        for src, tgt in pairs:
            forbidden_source_mids.add(src)
            source_to_class[src].add(cls)

    # Token quintile distribution for forbidden source MIDDLEs
    mid_quintile_dist = defaultdict(Counter)
    mid_position_values = defaultdict(list)

    for tok in all_tokens:
        if tok['middle'] in forbidden_source_mids and 'quintile' in tok:
            mid_quintile_dist[tok['middle']][tok['quintile']] += 1
            mid_position_values[tok['middle']].append(tok['line_pos'])

    print("Forbidden source MIDDLEs positional distribution:")
    for mid in sorted(forbidden_source_mids):
        qdist = mid_quintile_dist.get(mid, Counter())
        total = sum(qdist.values())
        positions = mid_position_values.get(mid, [])
        mean_pos = np.mean(positions) if positions else 0
        classes = source_to_class[mid]

        q_str = ' '.join(f"Q{q}:{qdist.get(q,0)}" for q in range(5))
        print(f"  {mid} [{', '.join(classes)}] (N={total}, mean_pos={mean_pos:.3f}): {q_str}")

    # Aggregate by hazard class
    class_quintile_profile = {}
    class_mean_positions = {}

    for cls in HAZARD_CLASSES:
        quintile_counts = Counter()
        all_positions = []

        for src_mid in set(src for src, tgt in HAZARD_CLASSES[cls]):
            for q, count in mid_quintile_dist.get(src_mid, {}).items():
                quintile_counts[q] += count
            all_positions.extend(mid_position_values.get(src_mid, []))

        total = sum(quintile_counts.values())
        mean_pos = np.mean(all_positions) if all_positions else 0

        class_quintile_profile[cls] = {
            'total_tokens': total,
            'quintile_distribution': {str(q): quintile_counts.get(q, 0) / total if total > 0 else 0
                                      for q in range(5)},
            'quintile_counts': {str(q): quintile_counts.get(q, 0) for q in range(5)},
            'mean_position': float(mean_pos),
        }
        class_mean_positions[cls] = float(mean_pos)

        q_str = ' '.join(f"Q{q}:{quintile_counts.get(q,0)}" for q in range(5))
        print(f"\n  {cls} (N={total}, mean_pos={mean_pos:.3f}): {q_str}")
        q_frac = ' '.join(f"Q{q}:{quintile_counts.get(q,0)/total:.1%}" for q in range(5)) if total > 0 else 'N/A'
        print(f"    fractions: {q_frac}")

    # Do actual violations cluster by position?
    violation_positions = defaultdict(list)
    for src_tok, tgt_tok in adjacency_pairs:
        pair = (src_tok['middle'], tgt_tok['middle'])
        if pair in PAIR_TO_CLASS:
            haz_class = PAIR_TO_CLASS[pair]
            if 'line_pos' in src_tok:
                violation_positions[haz_class].append(src_tok['line_pos'])

    print("\n\nActual violation positions:")
    for cls in HAZARD_CLASSES:
        positions = violation_positions.get(cls, [])
        if positions:
            print(f"  {cls}: {len(positions)} violations at positions {[f'{p:.3f}' for p in positions]}")
        else:
            print(f"  {cls}: 0 violations")

    # Overall forbidden source token distribution vs baseline
    all_quintiles = Counter()
    for tok in all_tokens:
        if 'quintile' in tok:
            all_quintiles[tok['quintile']] += 1

    total_all = sum(all_quintiles.values())
    print(f"\nBaseline quintile distribution (all tokens, N={total_all}):")
    for q in range(5):
        print(f"  Q{q}: {all_quintiles.get(q, 0)} ({all_quintiles.get(q, 0)/total_all:.1%})")

    # Chi-squared test: do hazard classes have different positional distributions?
    # Build contingency table: classes x quintiles
    classes_with_data = [cls for cls in HAZARD_CLASSES if class_quintile_profile[cls]['total_tokens'] > 0]
    if len(classes_with_data) >= 2:
        contingency = []
        for cls in classes_with_data:
            row = [class_quintile_profile[cls]['quintile_counts'].get(str(q), 0) for q in range(5)]
            contingency.append(row)

        contingency = np.array(contingency)
        # Only test if we have enough data
        if contingency.sum() > 0 and all(contingency.sum(axis=1) > 0):
            chi2, p, dof, expected = stats.chi2_contingency(contingency)
            V = np.sqrt(chi2 / (contingency.sum() * (min(contingency.shape) - 1))) if contingency.sum() > 0 else 0
            print(f"\nChi-squared test (class x quintile): chi2={chi2:.1f}, p={p:.6f}, V={V:.3f}")
            results['chi2_class_x_quintile'] = {
                'chi2': float(chi2), 'p': float(p), 'dof': int(dof), 'V': float(V),
                'classes_tested': classes_with_data,
            }

    results['class_quintile_profile'] = class_quintile_profile
    results['class_mean_positions'] = class_mean_positions
    results['violation_positions'] = {k: [float(p) for p in v] for k, v in violation_positions.items()}
    results['baseline_quintile'] = {str(q): all_quintiles.get(q, 0) for q in range(5)}

    return results


# ============================================================================
# SYNTHESIS: Cross-dimensional integration
# ============================================================================

def synthesize_results(dim_a, dim_b, dim_c, dim_d):
    """Cross-reference findings across all four dimensions."""
    print("\n=== SYNTHESIS: Cross-Dimensional Integration ===\n")

    synthesis = {}

    # For each hazard class, build a complete atom-mechanical profile
    for cls in HAZARD_CLASSES:
        n_pairs = len(HAZARD_CLASSES[cls])

        # From Dimension A: frame signature
        frame_profile = dim_a['class_frame_profiles'][cls]

        # From Dimension B: modifier involvement
        mod_profile = dim_b.get('class_modifier_profile', {}).get(cls, {})

        # From Dimension C: PREFIX channel
        prefix_profile = dim_c.get('class_prefix_profile', {}).get(cls, {})

        # From Dimension D: line position
        pos_profile = dim_d.get('class_quintile_profile', {}).get(cls, {})
        mean_pos = dim_d.get('class_mean_positions', {}).get(cls, None)

        # Determine dominant frame
        src_frames = frame_profile.get('source_frames', {})
        tgt_frames = frame_profile.get('target_frames', {})
        dominant_src_frame = max(src_frames, key=src_frames.get) if src_frames else None
        dominant_tgt_frame = max(tgt_frames, key=tgt_frames.get) if tgt_frames else None

        # Determine dominant HEAD
        src_heads = frame_profile.get('source_heads', {})
        tgt_heads = frame_profile.get('target_heads', {})
        dominant_src_head = max(src_heads, key=src_heads.get) if src_heads else None
        dominant_tgt_head = max(tgt_heads, key=tgt_heads.get) if tgt_heads else None

        # Determine dominant PREFIX channel
        prefix_dist = prefix_profile.get('channel_distribution', {})
        dominant_channel = max(prefix_dist, key=prefix_dist.get) if prefix_dist else None

        profile = {
            'n_pairs': n_pairs,
            'dominant_source_frame': dominant_src_frame,
            'dominant_target_frame': dominant_tgt_frame,
            'dominant_source_head': dominant_src_head,
            'dominant_target_head': dominant_tgt_head,
            'source_modifier_rate': frame_profile.get('source_modifier_rate', 0),
            'target_modifier_rate': frame_profile.get('target_modifier_rate', 0),
            'modifiers_in_forbidden': mod_profile,
            'dominant_prefix_channel': dominant_channel,
            'prefix_channel_distribution': prefix_dist,
            'mean_line_position': mean_pos,
            'corpus_violations': dim_a.get('corpus_violations', {}).get(cls, 0),
        }

        synthesis[cls] = profile

        print(f"\n{cls} ({n_pairs} pairs):")
        print(f"  Dominant source frame: {dominant_src_frame}")
        print(f"  Dominant target frame: {dominant_tgt_frame}")
        print(f"  Source HEAD: {dominant_src_head}, Target HEAD: {dominant_tgt_head}")
        print(f"  Modifier rate: source={profile['source_modifier_rate']:.1%}, "
              f"target={profile['target_modifier_rate']:.1%}")
        print(f"  Dominant PREFIX channel: {dominant_channel}")
        print(f"  Mean line position: {mean_pos:.3f}" if mean_pos else "  Mean line position: N/A")
        print(f"  Corpus violations: {profile['corpus_violations']}")

    # Cross-class differentiation assessment
    print("\n\n--- Cross-Class Differentiation ---")

    # Do hazard classes map to different HEAD atoms?
    head_overlap = {}
    classes = list(HAZARD_CLASSES.keys())
    for i, cls1 in enumerate(classes):
        for cls2 in classes[i+1:]:
            src_heads_1 = set(dim_a['class_frame_profiles'][cls1].get('source_heads', {}).keys())
            src_heads_2 = set(dim_a['class_frame_profiles'][cls2].get('source_heads', {}).keys())
            overlap = src_heads_1 & src_heads_2
            union = src_heads_1 | src_heads_2
            jaccard = len(overlap) / len(union) if union else 0
            head_overlap[f"{cls1}_vs_{cls2}"] = {
                'jaccard': float(jaccard),
                'overlap': list(overlap),
                'unique_1': list(src_heads_1 - src_heads_2),
                'unique_2': list(src_heads_2 - src_heads_1),
            }
            print(f"  {cls1} vs {cls2}: HEAD Jaccard={jaccard:.3f}, "
                  f"overlap={overlap}, unique_1={src_heads_1-src_heads_2}, unique_2={src_heads_2-src_heads_1}")

    synthesis['head_overlap'] = head_overlap

    return synthesis


# ============================================================================
# EXPERT PREDICTION VALIDATION
# ============================================================================

def validate_predictions(dim_a, dim_b, dim_c, dim_d, synthesis):
    """Validate the expert predictions from Phase 543 specification."""
    print("\n=== EXPERT PREDICTION VALIDATION ===\n")

    predictions = {}

    # P1: PHASE_ORDERING concentrates in a-HEAD territory
    # (a->r, a->l, a->n frames)
    po_profile = dim_a['class_frame_profiles']['PHASE_ORDERING']
    po_src_heads = po_profile.get('source_heads', {})

    # Check: source heads for PHASE_ORDERING
    # From decomposition: shey(s-HEAD), dy(d-HEAD), chey(c-HEAD)
    # These are headless compounds
    # IMPORTANT: the MIDDLEs involved are shey, dy, chey
    # shey: s=head, y=term -> headless
    # dy: d=head, y=term -> headless
    # chey: c=head, y=term -> headless
    # The prediction was that PO concentrates in a-HEAD territory
    # But actually the SOURCE MIDDLEs are all headless (s,d,c heads)
    # Let's also check TARGET frames
    po_tgt_heads = po_profile.get('target_heads', {})

    p1_src_a_frac = po_src_heads.get('a', 0) / sum(po_src_heads.values()) if po_src_heads else 0
    p1_tgt_a_frac = po_tgt_heads.get('a', 0) / sum(po_tgt_heads.values()) if po_tgt_heads else 0
    p1_confirmed = p1_src_a_frac > 0.3 or p1_tgt_a_frac > 0.3

    predictions['P1_PHASE_ORDERING_a_HEAD'] = {
        'prediction': 'PHASE_ORDERING concentrates in a-HEAD territory',
        'source_a_fraction': float(p1_src_a_frac),
        'target_a_fraction': float(p1_tgt_a_frac),
        'source_heads': po_src_heads,
        'target_heads': dict(po_tgt_heads),
        'confirmed': p1_confirmed,
        'note': 'Checking both source and target HEAD involvement',
    }
    print(f"P1 PHASE_ORDERING a-HEAD: source={p1_src_a_frac:.1%}, target={p1_tgt_a_frac:.1%} "
          f"-> {'CONFIRMED' if p1_confirmed else 'INVERTED'}")

    # P2: COMPOSITION_JUMP concentrates in o-HEAD territory
    cj_profile = dim_a['class_frame_profiles']['COMPOSITION_JUMP']
    cj_src_heads = cj_profile.get('source_heads', {})
    cj_tgt_heads = cj_profile.get('target_heads', {})

    p2_src_o_frac = cj_src_heads.get('o', 0) / sum(cj_src_heads.values()) if cj_src_heads else 0
    p2_tgt_o_frac = cj_tgt_heads.get('o', 0) / sum(cj_tgt_heads.values()) if cj_tgt_heads else 0
    p2_confirmed = p2_src_o_frac > 0.3 or p2_tgt_o_frac > 0.3

    predictions['P2_COMPOSITION_JUMP_o_HEAD'] = {
        'prediction': 'COMPOSITION_JUMP concentrates in o-HEAD or e-HEAD territory',
        'source_o_fraction': float(p2_src_o_frac),
        'target_o_fraction': float(p2_tgt_o_frac),
        'source_heads': dict(cj_src_heads),
        'target_heads': dict(cj_tgt_heads),
        'confirmed': p2_confirmed,
    }
    print(f"P2 COMPOSITION_JUMP o-HEAD: source={p2_src_o_frac:.1%}, target={p2_tgt_o_frac:.1%} "
          f"-> {'CONFIRMED' if p2_confirmed else 'INVERTED'}")

    # P3: CONTAINMENT_TIMING concentrates in l/r-terminal frames
    ct_profile = dim_a['class_frame_profiles']['CONTAINMENT_TIMING']
    ct_src_terms = ct_profile.get('source_terms', {})
    ct_tgt_terms = ct_profile.get('target_terms', {})

    lr_src = (ct_src_terms.get('l', 0) + ct_src_terms.get('r', 0))
    lr_src_frac = lr_src / sum(ct_src_terms.values()) if ct_src_terms else 0
    lr_tgt = (ct_tgt_terms.get('l', 0) + ct_tgt_terms.get('r', 0))
    lr_tgt_frac = lr_tgt / sum(ct_tgt_terms.values()) if ct_tgt_terms else 0
    p3_confirmed = lr_src_frac > 0.3 or lr_tgt_frac > 0.3

    predictions['P3_CONTAINMENT_l_r_terminal'] = {
        'prediction': 'CONTAINMENT_TIMING concentrates in l/r-terminal frames',
        'source_lr_fraction': float(lr_src_frac),
        'target_lr_fraction': float(lr_tgt_frac),
        'source_terms': dict(ct_src_terms),
        'target_terms': dict(ct_tgt_terms),
        'confirmed': p3_confirmed,
    }
    print(f"P3 CONTAINMENT l/r-terminal: source={lr_src_frac:.1%}, target={lr_tgt_frac:.1%} "
          f"-> {'CONFIRMED' if p3_confirmed else 'INVERTED'}")

    # P4: ENERGY_OVERSHOOT involves k or e HEAD
    eo_profile = dim_a['class_frame_profiles']['ENERGY_OVERSHOOT']
    eo_src_heads = eo_profile.get('source_heads', {})
    eo_tgt_heads = eo_profile.get('target_heads', {})

    ke_src = (eo_src_heads.get('k', 0) + eo_src_heads.get('e', 0) + eo_src_heads.get('h', 0))
    ke_src_frac = ke_src / sum(eo_src_heads.values()) if eo_src_heads else 0
    ke_tgt = (eo_tgt_heads.get('k', 0) + eo_tgt_heads.get('e', 0) + eo_tgt_heads.get('h', 0))
    ke_tgt_frac = ke_tgt / sum(eo_tgt_heads.values()) if eo_tgt_heads else 0
    p4_confirmed = ke_src_frac > 0.3 or ke_tgt_frac > 0.3

    predictions['P4_ENERGY_OVERSHOOT_kernel'] = {
        'prediction': 'ENERGY_OVERSHOOT involves k/e/h kernel atoms',
        'source_keh_fraction': float(ke_src_frac),
        'target_keh_fraction': float(ke_tgt_frac),
        'source_heads': dict(eo_src_heads),
        'target_heads': dict(eo_tgt_heads),
        'confirmed': p4_confirmed,
    }
    print(f"P4 ENERGY_OVERSHOOT kernel: source={ke_src_frac:.1%}, target={ke_tgt_frac:.1%} "
          f"-> {'CONFIRMED' if p4_confirmed else 'INVERTED'}")

    # P5: Hazard classes map to different line positions
    mean_positions = dim_d.get('class_mean_positions', {})
    positions_ordered = sorted(mean_positions.items(), key=lambda x: x[1])

    p5_range = max(mean_positions.values()) - min(mean_positions.values()) if mean_positions else 0
    p5_confirmed = p5_range > 0.05  # Meaningful spread

    predictions['P5_positional_differentiation'] = {
        'prediction': 'Hazard classes partition differently across line positions',
        'position_range': float(p5_range),
        'positions': {k: float(v) for k, v in positions_ordered},
        'confirmed': p5_confirmed,
    }
    print(f"P5 Positional differentiation: range={p5_range:.3f} "
          f"-> {'CONFIRMED' if p5_confirmed else 'INVERTED'}")
    print(f"   Order: {' < '.join(f'{cls}({pos:.3f})' for cls, pos in positions_ordered)}")

    # P6: Modifier quenching is selective (not uniform across classes)
    quench_rates = {cls: dim_b.get('quench_by_class', {}).get(cls, {}).get('rate', 0)
                    for cls in HAZARD_CLASSES}
    quench_range = max(quench_rates.values()) - min(quench_rates.values()) if quench_rates else 0
    p6_confirmed = quench_range > 0.1  # >10% range = selective

    predictions['P6_selective_quenching'] = {
        'prediction': 'Modifier quenching is hazard-class selective',
        'quench_rates': {k: float(v) for k, v in quench_rates.items()},
        'range': float(quench_range),
        'confirmed': p6_confirmed,
    }
    print(f"P6 Selective quenching: range={quench_range:.1%} "
          f"-> {'CONFIRMED' if p6_confirmed else 'INVERTED'}")

    # P7: PREFIX channel differentiates hazard classes
    prefix_profiles = dim_c.get('class_prefix_profile', {})
    dominant_channels = {cls: profile.get('dominant_prefix_channel', None)
                         for cls, profile in prefix_profiles.items() if profile}
    n_distinct = len(set(dominant_channels.values()))
    p7_confirmed = n_distinct >= 2  # At least 2 different dominant channels

    predictions['P7_prefix_differentiates'] = {
        'prediction': 'PREFIX channel differentiates hazard classes',
        'dominant_channels': dominant_channels,
        'n_distinct_channels': n_distinct,
        'confirmed': p7_confirmed,
    }
    print(f"P7 PREFIX differentiation: {n_distinct} distinct dominant channels "
          f"-> {'CONFIRMED' if p7_confirmed else 'INVERTED'}")

    # Summary
    confirmed = sum(1 for p in predictions.values() if p['confirmed'])
    total = len(predictions)
    print(f"\n\nPREDICTION SUMMARY: {confirmed}/{total} confirmed")

    return predictions


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("Phase 543: Hazard-Class Decomposition at Atom Resolution")
    print("=" * 60)

    # Collect data
    print("\nCollecting Currier B tokens...")
    all_tokens, adjacency_pairs, tokens_by_folio_line = collect_b_tokens()
    print(f"  Total tokens: {len(all_tokens)}")
    print(f"  Adjacency pairs: {len(adjacency_pairs)}")
    print(f"  Folio-lines: {len(tokens_by_folio_line)}")

    # Count actual forbidden violations
    violation_count = 0
    for src_tok, tgt_tok in adjacency_pairs:
        if (src_tok['middle'], tgt_tok['middle']) in FORBIDDEN_PAIRS:
            violation_count += 1
    print(f"  Forbidden violations found: {violation_count}")

    # Run all four dimensions
    dim_a = analyze_dimension_a(adjacency_pairs)
    dim_b = analyze_dimension_b(all_tokens, adjacency_pairs)
    dim_c = analyze_dimension_c(all_tokens, adjacency_pairs)
    dim_d = analyze_dimension_d(all_tokens, adjacency_pairs)

    # Synthesis
    synthesis = synthesize_results(dim_a, dim_b, dim_c, dim_d)

    # Validate predictions
    predictions = validate_predictions(dim_a, dim_b, dim_c, dim_d, synthesis)

    # Compile results
    results = {
        'phase': 543,
        'name': 'HAZARD_CLASS_ATOMIZATION',
        'total_tokens': len(all_tokens),
        'total_adjacency_pairs': len(adjacency_pairs),
        'total_forbidden_violations': violation_count,
        'hazard_class_assignments': {cls: [f"{s}->{t}" for s, t in pairs]
                                     for cls, pairs in HAZARD_CLASSES.items()},
        'dimension_a': dim_a,
        'dimension_b': dim_b,
        'dimension_c': dim_c,
        'dimension_d': dim_d,
        'synthesis': synthesis,
        'predictions': predictions,
    }

    # Save results
    output_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'hazard_class_atomization.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {output_path}")

    return results


if __name__ == '__main__':
    main()
