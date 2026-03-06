#!/usr/bin/env python3
"""
Phase 523: Hazard Topology Atom-Level Decomposition

Decomposes the 17 forbidden transitions (hazard topology) at the atom level
using the HEAD+MOD*+TERM framework (C1393-C1394).

Tests:
  T1: Hub MIDDLE atom decomposition (23 hub MIDDLEs -> HEAD/MOD/TERM -> sub-role)
  T2: Hazard class atom signatures (5 classes -> distinctive atom patterns)
  T3: HEAD atom hazard exposure (per HEAD: forbidden involvement, source/target)
  T4: TERMINAL atom hazard exposure (validate m-terminal 0%, extend)
  T5: HEAD x TERM frame hazard map (matrix of hazard rates)
  T6: PREFIX channel hazard exposure (per PREFIX: hazard rates, sister differences)
  T7: Hazard and line position (across SPECIFICATION -> WORK -> CLOSURE)
  T8: Hazard and two-level closure system (suffix rate, terminal opacity, hazard routing)
  T9: Hazard and suffix mode (Mode A vs Mode B hazard concentration)
  T10: Modifier stack and hazard modulation (hazard-quenching modifiers)

Output: phases/HAZARD_ATOM_DECOMPOSITION/results/hazard_atom_decomposition.json
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

# ============================================================================
# DATA LOADING
# ============================================================================

def load_token_class_map():
    """Load token -> 49-class mapping."""
    path = PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {t: int(c) for t, c in data['token_to_class'].items()}

def load_hub_sub_roles():
    """Load hub sub-role assignments from decoder_maps.json."""
    path = PROJECT_ROOT / 'data/decoder_maps.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    entries = data['maps']['hub_sub_role']['entries']
    return {k: v['value'] for k, v in entries.items()}

def load_macro_state_map():
    """Load class -> macro state mapping from decoder_maps.json."""
    path = PROJECT_ROOT / 'data/decoder_maps.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    entries = data['maps']['macro_state']['entries']
    return {k: v['value'] for k, v in entries.items()}

# The 17 forbidden MIDDLE-level transitions (from C109, C627, t4_hazard_residual.json)
FORBIDDEN_PAIRS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'),
    ('dy', 'aiin'), ('dy', 'chey'),
    ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'),
    ('ar', 'dal'), ('c', 'ee'),
    ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o'),
]

# The 5 hazard failure classes (C109)
HAZARD_CLASSES = {
    'PHASE_ORDERING': [  # 7/17 = 41%
        ('chey', 'chedy'), ('chey', 'shedy'), ('chedy', 'ee'),
        ('shedy', 'aiin'), ('shedy', 'o'), ('shey', 'aiin'), ('shey', 'al'),
    ],
    'COMPOSITION_JUMP': [  # 4/17 = 24%
        ('dy', 'aiin'), ('dy', 'chey'), ('ar', 'dal'), ('or', 'dal'),
    ],
    'CONTAINMENT_TIMING': [  # 4/17 = 24%
        ('he', 't'), ('he', 'or'), ('l', 'chol'), ('shey', 'c'),
    ],
    'RATE_MISMATCH': [  # 1/17 = 6%
        ('c', 'ee'),
    ],
    'ENERGY_OVERSHOOT': [  # 1/17 = 6%
        ('chol', 'r'),
    ],
}

# Hazard-involved instruction classes and their tokens (C541)
HAZARD_TOKENS = {
    7: ['ar', 'al'],                       # FL_HAZ
    8: ['chedy', 'shedy', 'chol'],          # EN_CHSH
    9: ['aiin', 'or', 'o'],                 # FQ_CONN
    23: ['dy', 's', 'y'],                   # FQ_CLOSER
    30: ['dar', 'dal', 'dain'],             # FL_HAZ
    31: ['chey', 'shey', 'chor'],           # EN_CHSH
}

# Hub MIDDLE sub-roles (C1000)
HUB_MIDDLES = {
    'HAZARD_SOURCE': ['ar', 'dy', 'ey', 'l', 'ol', 'or'],
    'HAZARD_TARGET': ['aiin', 'al', 'ee', 'o', 'r', 't'],
    'SAFETY_BUFFER': ['eol', 'k', 'od'],
    'PURE_CONNECTOR': ['d', 'e', 'eey', 'ek', 'eo', 'iin', 's', 'y'],
}

# HEAD+MOD+TERM slot classification (C1393)
HEAD_ATOMS = {'a', 'e', 'o'}  # primary HEADs
MODIFIER_ATOMS = {'p', 'f', 'i', 'c', 'd', 's'}
TERMINAL_ATOMS = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE_ATOMS = {'k', 't'}  # role-dual

def classify_atom_slot(atom, position_in_middle, middle_length):
    """Classify an atom into HEAD/MOD/TERM/FREE based on C1393."""
    if atom in FREE_ATOMS:
        if position_in_middle == 0:
            return 'HEAD'
        elif position_in_middle == middle_length - 1:
            return 'TERM'
        else:
            return 'FREE'
    if atom in HEAD_ATOMS:
        return 'HEAD'
    if atom in MODIFIER_ATOMS:
        return 'MOD'
    if atom in TERMINAL_ATOMS:
        return 'TERM'
    return 'UNKNOWN'

def decompose_middle(middle):
    """Decompose a MIDDLE into its atom slots per C1393-C1394."""
    if not middle:
        return None
    atoms = list(middle)
    if len(atoms) == 1:
        return {'head': atoms[0], 'mods': [], 'term': None, 'atoms': atoms, 'raw': middle}

    head = atoms[0]
    term = atoms[-1]
    mods = atoms[1:-1] if len(atoms) > 2 else []

    return {'head': head, 'mods': mods, 'term': term, 'atoms': atoms, 'raw': middle}


# ============================================================================
# DATA COLLECTION
# ============================================================================

def collect_b_tokens():
    """Collect all Currier B tokens with morphological decomposition and adjacency."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    token_class_map = load_token_class_map()
    hub_roles = load_hub_sub_roles()
    macro_map = load_macro_state_map()

    # Build forbidden pair set for quick lookup at MIDDLE level
    forbidden_set = set(FORBIDDEN_PAIRS)

    # Collect all tokens in folio/line order
    tokens_by_folio_line = defaultdict(list)
    all_tokens = []

    for tok in tx.currier_b():
        word = tok.word
        if not word or not word.strip() or '*' in word:
            continue

        m = morph.extract(word)
        if not m or not m.middle:
            continue

        category = cc.classify(m.middle)
        decomp = decompose_middle(m.middle)
        token_class = token_class_map.get(word)
        hub_role = hub_roles.get(m.middle)
        macro_state = macro_map.get(str(token_class)) if token_class is not None else None

        # Suffix mode: determine from suffix pattern (C1229, C1231)
        # Mode A: terminal suffixes (edy, ey, eey, etc.) - specification
        # Mode B: bare or continuation suffixes (bare, aiin, ol, etc.)
        suffix = m.suffix or ''
        terminal_suffixes = {'edy', 'ey', 'eey', 'dy', 'y', 'hy', 'ry', 'ly', 'eedy', 'chy', 'shy'}
        if suffix in terminal_suffixes:
            suffix_mode = 'A'
        elif suffix == '':
            suffix_mode = 'B'
        else:
            suffix_mode = 'B'  # non-terminal suffixes are Mode B (continuation)

        entry = {
            'word': word,
            'folio': tok.folio,
            'line': tok.line,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': suffix,
            'has_suffix': bool(suffix),
            'articulator': m.articulator,
            'category': category,
            'decomp': decomp,
            'token_class': token_class,
            'hub_role': hub_role,
            'macro_state': macro_state,
            'suffix_mode': suffix_mode,
            'head_atom': decomp['head'] if decomp else None,
            'term_atom': decomp['term'] if decomp else None,
        }

        key = (tok.folio, tok.line)
        tokens_by_folio_line[key].append(entry)
        all_tokens.append(entry)

    # Compute line position quintiles
    for key, line_tokens in tokens_by_folio_line.items():
        n = len(line_tokens)
        for idx, entry in enumerate(line_tokens):
            if n <= 1:
                entry['line_pos_frac'] = 0.5
                entry['line_quintile'] = 2  # middle
            else:
                frac = idx / (n - 1)
                entry['line_pos_frac'] = frac
                entry['line_quintile'] = min(int(frac * 5), 4)

            entry['is_line_initial'] = (idx == 0)
            entry['is_line_final'] = (idx == n - 1)

    # Build adjacency pairs (within-line transitions at MIDDLE level)
    adjacency_pairs = []
    for key in sorted(tokens_by_folio_line.keys()):
        line_tokens = tokens_by_folio_line[key]
        for i in range(len(line_tokens) - 1):
            src = line_tokens[i]
            tgt = line_tokens[i + 1]
            pair = (src['middle'], tgt['middle'])
            is_forbidden = pair in forbidden_set
            adjacency_pairs.append({
                'src': src,
                'tgt': tgt,
                'src_middle': src['middle'],
                'tgt_middle': tgt['middle'],
                'is_forbidden': is_forbidden,
                'folio': src['folio'],
            })

    return all_tokens, adjacency_pairs, tokens_by_folio_line


# ============================================================================
# TEST IMPLEMENTATIONS
# ============================================================================

def test_t1_hub_middle_atom_decomposition(all_tokens):
    """T1: Hub MIDDLE atom decomposition."""
    print("  T1: Hub MIDDLE atom decomposition...")

    hub_results = {}
    all_hub_middles = {}
    for role, middles in HUB_MIDDLES.items():
        for mid in middles:
            all_hub_middles[mid] = role

    for mid, role in all_hub_middles.items():
        decomp = decompose_middle(mid)
        atoms = list(mid)
        slots = []
        for pos, atom in enumerate(atoms):
            slot = classify_atom_slot(atom, pos, len(atoms))
            slots.append({'atom': atom, 'position': pos, 'slot': slot})

        # Count tokens
        token_count = sum(1 for t in all_tokens if t['middle'] == mid)

        # Get category distribution
        cat_counts = Counter(t['category'] for t in all_tokens if t['middle'] == mid)
        total = sum(cat_counts.values())
        cat_dist = {k: round(v/total, 4) if total > 0 else 0 for k, v in cat_counts.most_common()}

        hub_results[mid] = {
            'sub_role': role,
            'atoms': atoms,
            'slots': slots,
            'head': decomp['head'] if decomp else None,
            'mods': decomp['mods'] if decomp else [],
            'term': decomp['term'] if decomp else None,
            'token_count': token_count,
            'category_dist': cat_dist,
        }

    # Analyze HEAD distribution by sub-role
    head_by_role = defaultdict(list)
    for mid, info in hub_results.items():
        head_by_role[info['sub_role']].append(info['head'])

    head_summary = {}
    for role in ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER', 'PURE_CONNECTOR']:
        heads = head_by_role.get(role, [])
        head_counts = Counter(heads)
        head_summary[role] = dict(head_counts)

    # Analyze TERMINAL distribution by sub-role
    term_by_role = defaultdict(list)
    for mid, info in hub_results.items():
        if info['term']:
            term_by_role[info['sub_role']].append(info['term'])

    term_summary = {}
    for role in ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER', 'PURE_CONNECTOR']:
        terms = term_by_role.get(role, [])
        term_counts = Counter(terms)
        term_summary[role] = dict(term_counts)

    return {
        'hub_middles': hub_results,
        'head_by_sub_role': head_summary,
        'term_by_sub_role': term_summary,
        'total_hub_middles': len(hub_results),
    }


def test_t2_hazard_class_atom_signatures(all_tokens, adjacency_pairs):
    """T2: Hazard class atom signatures."""
    print("  T2: Hazard class atom signatures...")

    class_results = {}
    for hc_name, pairs in HAZARD_CLASSES.items():
        # Collect all MIDDLEs involved as source or target in this class
        sources = set()
        targets = set()
        for src, tgt in pairs:
            sources.add(src)
            targets.add(tgt)

        all_middles = sources | targets

        # Atom frequency in sources
        src_atom_counts = Counter()
        for mid in sources:
            for atom in mid:
                src_atom_counts[atom] += 1

        # Atom frequency in targets
        tgt_atom_counts = Counter()
        for mid in targets:
            for atom in mid:
                tgt_atom_counts[atom] += 1

        # HEAD atoms in sources/targets
        src_heads = Counter()
        src_terms = Counter()
        tgt_heads = Counter()
        tgt_terms = Counter()

        for mid in sources:
            decomp = decompose_middle(mid)
            if decomp:
                src_heads[decomp['head']] += 1
                if decomp['term']:
                    src_terms[decomp['term']] += 1

        for mid in targets:
            decomp = decompose_middle(mid)
            if decomp:
                tgt_heads[decomp['head']] += 1
                if decomp['term']:
                    tgt_terms[decomp['term']] += 1

        # Category distribution of involved MIDDLEs
        cat_counts = Counter()
        for t in all_tokens:
            if t['middle'] in all_middles:
                cat_counts[t['category']] += 1
        total = sum(cat_counts.values())
        cat_dist = {k: round(v/total, 4) if total > 0 else 0 for k, v in cat_counts.most_common()}

        class_results[hc_name] = {
            'pairs': [(s, t) for s, t in pairs],
            'sources': sorted(sources),
            'targets': sorted(targets),
            'source_atom_profile': dict(src_atom_counts.most_common()),
            'target_atom_profile': dict(tgt_atom_counts.most_common()),
            'source_heads': dict(src_heads),
            'source_terms': dict(src_terms),
            'target_heads': dict(tgt_heads),
            'target_terms': dict(tgt_terms),
            'category_dist': cat_dist,
            'n_pairs': len(pairs),
        }

    return class_results


def test_t3_head_atom_hazard_exposure(all_tokens, adjacency_pairs):
    """T3: HEAD atom hazard exposure rates."""
    print("  T3: HEAD atom hazard exposure...")

    # Build set of all MIDDLEs that participate in forbidden pairs
    forbidden_sources = set()
    forbidden_targets = set()
    for src, tgt in FORBIDDEN_PAIRS:
        forbidden_sources.add(src)
        forbidden_targets.add(tgt)
    forbidden_all = forbidden_sources | forbidden_targets

    # For each HEAD atom, compute hazard exposure
    head_stats = {}
    unique_heads = set()
    for t in all_tokens:
        if t['head_atom']:
            unique_heads.add(t['head_atom'])

    for head in sorted(unique_heads):
        # Tokens with this HEAD
        head_tokens = [t for t in all_tokens if t['head_atom'] == head]
        n_total = len(head_tokens)

        # How many have MIDDLEs in forbidden sources/targets
        n_source = sum(1 for t in head_tokens if t['middle'] in forbidden_sources)
        n_target = sum(1 for t in head_tokens if t['middle'] in forbidden_targets)
        n_any = sum(1 for t in head_tokens if t['middle'] in forbidden_all)

        # Actual forbidden transitions involving this HEAD
        n_forbidden_src = sum(1 for p in adjacency_pairs
                              if p['is_forbidden'] and p['src'].get('head_atom') == head)
        n_forbidden_tgt = sum(1 for p in adjacency_pairs
                              if p['is_forbidden'] and p['tgt'].get('head_atom') == head)

        # Category distribution
        cat_counts = Counter(t['category'] for t in head_tokens)
        cat_dist = {k: round(v/n_total, 4) if n_total > 0 else 0 for k, v in cat_counts.most_common()}

        # Hub sub-role distribution
        hub_counts = Counter(t['hub_role'] for t in head_tokens if t['hub_role'])

        head_stats[head] = {
            'n_tokens': n_total,
            'n_source_middles': n_source,
            'n_target_middles': n_target,
            'n_any_hazard': n_any,
            'source_rate': round(n_source / n_total, 4) if n_total > 0 else 0,
            'target_rate': round(n_target / n_total, 4) if n_total > 0 else 0,
            'any_hazard_rate': round(n_any / n_total, 4) if n_total > 0 else 0,
            'n_forbidden_as_source': n_forbidden_src,
            'n_forbidden_as_target': n_forbidden_tgt,
            'category_dist': cat_dist,
            'hub_roles': dict(hub_counts),
        }

    return head_stats


def test_t4_terminal_atom_hazard_exposure(all_tokens, adjacency_pairs):
    """T4: TERMINAL atom hazard exposure rates."""
    print("  T4: TERMINAL atom hazard exposure...")

    forbidden_sources = set(src for src, _ in FORBIDDEN_PAIRS)
    forbidden_targets = set(tgt for _, tgt in FORBIDDEN_PAIRS)
    forbidden_all = forbidden_sources | forbidden_targets

    # For each TERMINAL atom, compute hazard exposure
    term_stats = {}
    unique_terms = set()
    for t in all_tokens:
        if t['term_atom']:
            unique_terms.add(t['term_atom'])

    for term in sorted(unique_terms):
        term_tokens = [t for t in all_tokens if t['term_atom'] == term]
        n_total = len(term_tokens)

        n_source = sum(1 for t in term_tokens if t['middle'] in forbidden_sources)
        n_target = sum(1 for t in term_tokens if t['middle'] in forbidden_targets)
        n_any = sum(1 for t in term_tokens if t['middle'] in forbidden_all)

        # FLOW + CONTAINMENT category rate (hazard categories per C1280)
        n_flow_cont = sum(1 for t in term_tokens if t['category'] in ('FLOW', 'CONTAINMENT'))

        # Category distribution
        cat_counts = Counter(t['category'] for t in term_tokens)
        cat_dist = {k: round(v/n_total, 4) if n_total > 0 else 0 for k, v in cat_counts.most_common()}

        term_stats[term] = {
            'n_tokens': n_total,
            'n_source_middles': n_source,
            'n_target_middles': n_target,
            'n_any_hazard': n_any,
            'source_rate': round(n_source / n_total, 4) if n_total > 0 else 0,
            'target_rate': round(n_target / n_total, 4) if n_total > 0 else 0,
            'any_hazard_rate': round(n_any / n_total, 4) if n_total > 0 else 0,
            'flow_containment_rate': round(n_flow_cont / n_total, 4) if n_total > 0 else 0,
            'category_dist': cat_dist,
        }

    return term_stats


def test_t5_head_term_frame_hazard_map(all_tokens, adjacency_pairs):
    """T5: HEAD x TERM frame hazard map."""
    print("  T5: HEAD x TERM frame hazard map...")

    forbidden_all = set()
    for src, tgt in FORBIDDEN_PAIRS:
        forbidden_all.add(src)
        forbidden_all.add(tgt)

    # Build frame matrix
    frame_counts = defaultdict(int)  # (head, term) -> token count
    frame_hazard = defaultdict(int)  # (head, term) -> hazard token count
    frame_categories = defaultdict(lambda: Counter())  # (head, term) -> category counts

    for t in all_tokens:
        h = t['head_atom']
        tr = t['term_atom']
        if h and tr:
            key = (h, tr)
            frame_counts[key] += 1
            if t['middle'] in forbidden_all:
                frame_hazard[key] += 1
            frame_categories[key][t['category']] += 1

    # Also include single-atom MIDDLEs (head only, no term)
    for t in all_tokens:
        if t['head_atom'] and not t['term_atom']:
            key = (t['head_atom'], '_NONE_')
            frame_counts[key] += 1
            if t['middle'] in forbidden_all:
                frame_hazard[key] += 1
            frame_categories[key][t['category']] += 1

    # Build the matrix
    all_heads = sorted(set(k[0] for k in frame_counts.keys()))
    all_terms = sorted(set(k[1] for k in frame_counts.keys()))

    matrix = {}
    for h in all_heads:
        row = {}
        for tr in all_terms:
            key = (h, tr)
            n = frame_counts.get(key, 0)
            n_haz = frame_hazard.get(key, 0)
            if n > 0:
                cats = dict(frame_categories[key].most_common(3))
                row[tr] = {
                    'n': n,
                    'hazard_n': n_haz,
                    'hazard_rate': round(n_haz / n, 4),
                    'top_categories': cats,
                }
        if row:
            matrix[h] = row

    # Compute marginal hazard rates
    head_marginal = {}
    for h in all_heads:
        total = sum(frame_counts.get((h, tr), 0) for tr in all_terms)
        haz = sum(frame_hazard.get((h, tr), 0) for tr in all_terms)
        head_marginal[h] = {'n': total, 'hazard_n': haz, 'rate': round(haz/total, 4) if total > 0 else 0}

    term_marginal = {}
    for tr in all_terms:
        total = sum(frame_counts.get((h, tr), 0) for h in all_heads)
        haz = sum(frame_hazard.get((h, tr), 0) for h in all_heads)
        term_marginal[tr] = {'n': total, 'hazard_n': haz, 'rate': round(haz/total, 4) if total > 0 else 0}

    return {
        'matrix': matrix,
        'head_marginal': head_marginal,
        'term_marginal': term_marginal,
        'all_heads': all_heads,
        'all_terms': all_terms,
    }


def test_t6_prefix_channel_hazard(all_tokens, adjacency_pairs):
    """T6: PREFIX channel hazard exposure."""
    print("  T6: PREFIX channel hazard exposure...")

    forbidden_sources = set(src for src, _ in FORBIDDEN_PAIRS)
    forbidden_targets = set(tgt for _, tgt in FORBIDDEN_PAIRS)
    forbidden_all = forbidden_sources | forbidden_targets

    prefix_stats = {}
    unique_prefixes = set()
    for t in all_tokens:
        pfx = t['prefix'] if t['prefix'] else 'BARE'
        unique_prefixes.add(pfx)

    for pfx in sorted(unique_prefixes):
        pfx_tokens = [t for t in all_tokens if (t['prefix'] if t['prefix'] else 'BARE') == pfx]
        n_total = len(pfx_tokens)

        n_source = sum(1 for t in pfx_tokens if t['middle'] in forbidden_sources)
        n_target = sum(1 for t in pfx_tokens if t['middle'] in forbidden_targets)
        n_any = sum(1 for t in pfx_tokens if t['middle'] in forbidden_all)

        # Actual forbidden transitions
        n_forbidden = sum(1 for p in adjacency_pairs
                          if p['is_forbidden'] and
                          (p['src'].get('prefix') if p['src'].get('prefix') else 'BARE') == pfx)

        # FLOW + CONTAINMENT rate
        n_flow_cont = sum(1 for t in pfx_tokens if t['category'] in ('FLOW', 'CONTAINMENT'))

        # Category distribution
        cat_counts = Counter(t['category'] for t in pfx_tokens)
        cat_dist = {k: round(v/n_total, 4) if n_total > 0 else 0 for k, v in cat_counts.most_common()}

        prefix_stats[pfx] = {
            'n_tokens': n_total,
            'n_source': n_source,
            'n_target': n_target,
            'n_any_hazard': n_any,
            'source_rate': round(n_source / n_total, 4) if n_total > 0 else 0,
            'target_rate': round(n_target / n_total, 4) if n_total > 0 else 0,
            'hazard_rate': round(n_any / n_total, 4) if n_total > 0 else 0,
            'flow_containment_rate': round(n_flow_cont / n_total, 4) if n_total > 0 else 0,
            'n_actual_forbidden': n_forbidden,
            'category_dist': cat_dist,
        }

    # Sister pair comparisons
    sister_pairs = [('ch', 'sh'), ('ok', 'ot')]
    sister_comparison = {}
    for s1, s2 in sister_pairs:
        if s1 in prefix_stats and s2 in prefix_stats:
            r1 = prefix_stats[s1]['hazard_rate']
            r2 = prefix_stats[s2]['hazard_rate']
            sister_comparison[f'{s1}_vs_{s2}'] = {
                f'{s1}_hazard_rate': r1,
                f'{s2}_hazard_rate': r2,
                'ratio': round(r1 / r2, 4) if r2 > 0 else float('inf'),
                f'{s1}_flow_cont': prefix_stats[s1]['flow_containment_rate'],
                f'{s2}_flow_cont': prefix_stats[s2]['flow_containment_rate'],
            }

    return {
        'prefix_stats': prefix_stats,
        'sister_comparison': sister_comparison,
    }


def test_t7_hazard_line_position(all_tokens, adjacency_pairs):
    """T7: Hazard and line position."""
    print("  T7: Hazard and line position...")

    forbidden_all = set()
    for src, tgt in FORBIDDEN_PAIRS:
        forbidden_all.add(src)
        forbidden_all.add(tgt)

    # By quintile
    quintile_stats = {}
    for q in range(5):
        q_tokens = [t for t in all_tokens if t.get('line_quintile') == q]
        n_total = len(q_tokens)
        n_hazard = sum(1 for t in q_tokens if t['middle'] in forbidden_all)
        n_flow_cont = sum(1 for t in q_tokens if t['category'] in ('FLOW', 'CONTAINMENT'))

        cat_counts = Counter(t['category'] for t in q_tokens)
        cat_dist = {k: round(v/n_total, 4) if n_total > 0 else 0 for k, v in cat_counts.most_common()}

        quintile_stats[f'Q{q}'] = {
            'n_tokens': n_total,
            'hazard_token_rate': round(n_hazard / n_total, 4) if n_total > 0 else 0,
            'flow_containment_rate': round(n_flow_cont / n_total, 4) if n_total > 0 else 0,
            'category_dist': cat_dist,
        }

    # Forbidden TRANSITIONS by source quintile
    transition_by_quintile = {}
    for q in range(5):
        q_pairs = [p for p in adjacency_pairs if p['src'].get('line_quintile') == q]
        n_total = len(q_pairs)
        n_forbidden = sum(1 for p in q_pairs if p['is_forbidden'])
        transition_by_quintile[f'Q{q}'] = {
            'n_transitions': n_total,
            'n_forbidden': n_forbidden,
            'forbidden_rate': round(n_forbidden / n_total, 6) if n_total > 0 else 0,
        }

    # Initial vs final position
    initial_tokens = [t for t in all_tokens if t.get('is_line_initial')]
    final_tokens = [t for t in all_tokens if t.get('is_line_final')]
    body_tokens = [t for t in all_tokens if not t.get('is_line_initial') and not t.get('is_line_final')]

    position_stats = {}
    for name, subset in [('initial', initial_tokens), ('final', final_tokens), ('body', body_tokens)]:
        n = len(subset)
        n_haz = sum(1 for t in subset if t['middle'] in forbidden_all)
        n_fc = sum(1 for t in subset if t['category'] in ('FLOW', 'CONTAINMENT'))
        position_stats[name] = {
            'n': n,
            'hazard_rate': round(n_haz / n, 4) if n > 0 else 0,
            'flow_containment_rate': round(n_fc / n, 4) if n > 0 else 0,
        }

    return {
        'quintile_stats': quintile_stats,
        'transition_by_quintile': transition_by_quintile,
        'position_stats': position_stats,
    }


def test_t8_hazard_closure_system(all_tokens, adjacency_pairs):
    """T8: Hazard and two-level closure system."""
    print("  T8: Hazard and two-level closure system...")

    forbidden_all = set()
    for src, tgt in FORBIDDEN_PAIRS:
        forbidden_all.add(src)
        forbidden_all.add(tgt)

    # Terminal opacity tiers (C1440)
    opacity_tiers = {
        'OPAQUE': {'n', 'y', 'm'},      # suffix rate < 5%
        'SEMI_TRANSPARENT': {'l', 'r'},   # suffix rate 17-20%
        'TRANSPARENT': {'h'},             # suffix rate ~99%
    }

    tier_stats = {}
    for tier_name, term_set in opacity_tiers.items():
        tier_tokens = [t for t in all_tokens if t['term_atom'] in term_set]
        n = len(tier_tokens)
        n_hazard = sum(1 for t in tier_tokens if t['middle'] in forbidden_all)
        n_has_suffix = sum(1 for t in tier_tokens if t['has_suffix'])
        n_flow_cont = sum(1 for t in tier_tokens if t['category'] in ('FLOW', 'CONTAINMENT'))

        tier_stats[tier_name] = {
            'terminals': sorted(term_set),
            'n_tokens': n,
            'hazard_rate': round(n_hazard / n, 4) if n > 0 else 0,
            'suffix_rate': round(n_has_suffix / n, 4) if n > 0 else 0,
            'flow_containment_rate': round(n_flow_cont / n, 4) if n > 0 else 0,
        }

    # Suffixed vs unsuffixed hazard rates
    suffixed = [t for t in all_tokens if t['has_suffix']]
    unsuffixed = [t for t in all_tokens if not t['has_suffix']]

    n_suf = len(suffixed)
    n_unsuf = len(unsuffixed)
    n_suf_haz = sum(1 for t in suffixed if t['middle'] in forbidden_all)
    n_unsuf_haz = sum(1 for t in unsuffixed if t['middle'] in forbidden_all)

    suffix_hazard = {
        'suffixed': {
            'n': n_suf,
            'hazard_rate': round(n_suf_haz / n_suf, 4) if n_suf > 0 else 0,
        },
        'unsuffixed': {
            'n': n_unsuf,
            'hazard_rate': round(n_unsuf_haz / n_unsuf, 4) if n_unsuf > 0 else 0,
        },
    }

    # Cross-reference C623: hazard tokens are universally suffix-less
    hazard_tokens_with_suffix = []
    for t in all_tokens:
        if t['middle'] in forbidden_all and t['has_suffix']:
            hazard_tokens_with_suffix.append(t['word'])

    return {
        'tier_stats': tier_stats,
        'suffix_hazard': suffix_hazard,
        'hazard_tokens_with_suffix_count': len(hazard_tokens_with_suffix),
        'hazard_tokens_with_suffix_examples': hazard_tokens_with_suffix[:20],
    }


def test_t9_hazard_suffix_mode(all_tokens, adjacency_pairs):
    """T9: Hazard and suffix mode (Mode A vs Mode B)."""
    print("  T9: Hazard and suffix mode...")

    forbidden_all = set()
    for src, tgt in FORBIDDEN_PAIRS:
        forbidden_all.add(src)
        forbidden_all.add(tgt)

    mode_stats = {}
    for mode in ['A', 'B']:
        mode_tokens = [t for t in all_tokens if t['suffix_mode'] == mode]
        n = len(mode_tokens)
        n_hazard = sum(1 for t in mode_tokens if t['middle'] in forbidden_all)
        n_flow_cont = sum(1 for t in mode_tokens if t['category'] in ('FLOW', 'CONTAINMENT'))

        cat_counts = Counter(t['category'] for t in mode_tokens)
        cat_dist = {k: round(v/n, 4) if n > 0 else 0 for k, v in cat_counts.most_common()}

        # HEAD distribution
        head_counts = Counter(t['head_atom'] for t in mode_tokens if t['head_atom'])
        head_n = sum(head_counts.values())
        head_dist = {k: round(v/head_n, 4) if head_n > 0 else 0 for k, v in head_counts.most_common()}

        mode_stats[mode] = {
            'n_tokens': n,
            'hazard_rate': round(n_hazard / n, 4) if n > 0 else 0,
            'flow_containment_rate': round(n_flow_cont / n, 4) if n > 0 else 0,
            'category_dist': cat_dist,
            'head_dist': head_dist,
        }

    # Forbidden transitions by mode of source token
    mode_forbidden = {}
    for mode in ['A', 'B']:
        mode_pairs = [p for p in adjacency_pairs if p['src']['suffix_mode'] == mode]
        n = len(mode_pairs)
        n_f = sum(1 for p in mode_pairs if p['is_forbidden'])
        mode_forbidden[mode] = {
            'n_transitions': n,
            'n_forbidden': n_f,
            'forbidden_rate': round(n_f / n, 6) if n > 0 else 0,
        }

    return {
        'mode_stats': mode_stats,
        'mode_forbidden_transitions': mode_forbidden,
    }


def test_t10_modifier_hazard_modulation(all_tokens, adjacency_pairs):
    """T10: Modifier stack and hazard modulation."""
    print("  T10: Modifier stack hazard modulation...")

    forbidden_all = set()
    for src, tgt in FORBIDDEN_PAIRS:
        forbidden_all.add(src)
        forbidden_all.add(tgt)

    # For each modifier atom, compare hazard rate when present vs absent
    modifier_stats = {}
    for mod in sorted(MODIFIER_ATOMS):
        with_mod = [t for t in all_tokens if t['decomp'] and mod in t['decomp']['mods']]
        without_mod = [t for t in all_tokens if t['decomp'] and mod not in t['decomp']['mods']]

        n_with = len(with_mod)
        n_without = len(without_mod)

        haz_with = sum(1 for t in with_mod if t['middle'] in forbidden_all)
        haz_without = sum(1 for t in without_mod if t['middle'] in forbidden_all)

        fc_with = sum(1 for t in with_mod if t['category'] in ('FLOW', 'CONTAINMENT'))
        fc_without = sum(1 for t in without_mod if t['category'] in ('FLOW', 'CONTAINMENT'))

        rate_with = haz_with / n_with if n_with > 0 else 0
        rate_without = haz_without / n_without if n_without > 0 else 0

        fc_rate_with = fc_with / n_with if n_with > 0 else 0
        fc_rate_without = fc_without / n_without if n_without > 0 else 0

        modifier_stats[mod] = {
            'n_with': n_with,
            'n_without': n_without,
            'hazard_rate_with': round(rate_with, 4),
            'hazard_rate_without': round(rate_without, 4),
            'hazard_ratio': round(rate_with / rate_without, 4) if rate_without > 0 else 0,
            'flow_cont_rate_with': round(fc_rate_with, 4),
            'flow_cont_rate_without': round(fc_rate_without, 4),
        }

    # Compound length vs hazard
    length_stats = {}
    for length in range(1, 7):
        length_tokens = [t for t in all_tokens if t['decomp'] and len(t['decomp']['atoms']) == length]
        n = len(length_tokens)
        n_haz = sum(1 for t in length_tokens if t['middle'] in forbidden_all)
        length_stats[length] = {
            'n_tokens': n,
            'hazard_rate': round(n_haz / n, 4) if n > 0 else 0,
        }

    # Modifier count vs hazard
    mod_count_stats = {}
    for mc in range(4):
        mc_tokens = [t for t in all_tokens if t['decomp'] and len(t['decomp']['mods']) == mc]
        n = len(mc_tokens)
        n_haz = sum(1 for t in mc_tokens if t['middle'] in forbidden_all)
        mod_count_stats[mc] = {
            'n_tokens': n,
            'hazard_rate': round(n_haz / n, 4) if n > 0 else 0,
        }

    return {
        'modifier_stats': modifier_stats,
        'length_stats': length_stats,
        'mod_count_stats': mod_count_stats,
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("Phase 523: Hazard Topology Atom-Level Decomposition")
    print("=" * 60)

    print("\nCollecting Currier B tokens and adjacency pairs...")
    all_tokens, adjacency_pairs, tokens_by_folio_line = collect_b_tokens()
    print(f"  {len(all_tokens)} tokens, {len(adjacency_pairs)} adjacency pairs")

    # Count actual forbidden violations
    n_forbidden = sum(1 for p in adjacency_pairs if p['is_forbidden'])
    print(f"  {n_forbidden} forbidden pair violations found in corpus")

    print("\nRunning tests...")
    results = {
        'phase': 'HAZARD_ATOM_DECOMPOSITION',
        'phase_number': 523,
        'total_tokens': len(all_tokens),
        'total_adjacency_pairs': len(adjacency_pairs),
        'total_forbidden_violations': n_forbidden,
        'n_forbidden_pair_types': len(FORBIDDEN_PAIRS),
    }

    results['T1_hub_atom_decomposition'] = test_t1_hub_middle_atom_decomposition(all_tokens)
    results['T2_hazard_class_signatures'] = test_t2_hazard_class_atom_signatures(all_tokens, adjacency_pairs)
    results['T3_head_atom_hazard'] = test_t3_head_atom_hazard_exposure(all_tokens, adjacency_pairs)
    results['T4_terminal_atom_hazard'] = test_t4_terminal_atom_hazard_exposure(all_tokens, adjacency_pairs)
    results['T5_frame_hazard_map'] = test_t5_head_term_frame_hazard_map(all_tokens, adjacency_pairs)
    results['T6_prefix_channel_hazard'] = test_t6_prefix_channel_hazard(all_tokens, adjacency_pairs)
    results['T7_hazard_line_position'] = test_t7_hazard_line_position(all_tokens, adjacency_pairs)
    results['T8_hazard_closure_system'] = test_t8_hazard_closure_system(all_tokens, adjacency_pairs)
    results['T9_hazard_suffix_mode'] = test_t9_hazard_suffix_mode(all_tokens, adjacency_pairs)
    results['T10_modifier_hazard'] = test_t10_modifier_hazard_modulation(all_tokens, adjacency_pairs)

    # ========================================================================
    # SUMMARY STATISTICS
    # ========================================================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # T1 summary
    t1 = results['T1_hub_atom_decomposition']
    print(f"\nT1: {t1['total_hub_middles']} hub MIDDLEs decomposed")
    for role in ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER', 'PURE_CONNECTOR']:
        heads = t1['head_by_sub_role'].get(role, {})
        terms = t1['term_by_sub_role'].get(role, {})
        print(f"  {role}: HEADs={heads}, TERMs={terms}")

    # T3 summary
    t3 = results['T3_head_atom_hazard']
    print(f"\nT3: HEAD atom hazard exposure")
    for h in sorted(t3.keys()):
        info = t3[h]
        print(f"  {h}: hazard={info['any_hazard_rate']:.1%} ({info['n_any_hazard']}/{info['n_tokens']})")

    # T4 summary
    t4 = results['T4_terminal_atom_hazard']
    print(f"\nT4: TERMINAL atom hazard exposure")
    for tr in sorted(t4.keys()):
        info = t4[tr]
        print(f"  {tr}: hazard={info['any_hazard_rate']:.1%} FLOW+CONT={info['flow_containment_rate']:.1%} ({info['n_tokens']} tokens)")

    # T5 summary
    t5 = results['T5_frame_hazard_map']
    print(f"\nT5: Highest-hazard frames:")
    all_frames = []
    for h, row in t5['matrix'].items():
        for tr, cell in row.items():
            if cell['hazard_rate'] > 0 and cell['n'] >= 10:
                all_frames.append((h, tr, cell['hazard_rate'], cell['n']))
    all_frames.sort(key=lambda x: -x[2])
    for h, tr, rate, n in all_frames[:10]:
        print(f"  {h}->{tr}: {rate:.1%} hazard ({n} tokens)")

    # T6 summary
    t6 = results['T6_prefix_channel_hazard']
    print(f"\nT6: PREFIX hazard rates (top):")
    pfx_list = [(k, v['hazard_rate'], v['n_tokens'])
                for k, v in t6['prefix_stats'].items() if v['n_tokens'] >= 50]
    pfx_list.sort(key=lambda x: -x[1])
    for pfx, rate, n in pfx_list[:10]:
        print(f"  {pfx}: {rate:.1%} ({n} tokens)")

    for pair, comp in t6['sister_comparison'].items():
        print(f"  Sister {pair}: ratio={comp['ratio']:.2f}")

    # T7 summary
    t7 = results['T7_hazard_line_position']
    print(f"\nT7: Hazard by line position:")
    for pos, info in t7['position_stats'].items():
        print(f"  {pos}: hazard={info['hazard_rate']:.1%} F+C={info['flow_containment_rate']:.1%}")

    # T8 summary
    t8 = results['T8_hazard_closure_system']
    print(f"\nT8: Hazard by opacity tier:")
    for tier, info in t8['tier_stats'].items():
        print(f"  {tier}: hazard={info['hazard_rate']:.1%} suffix={info['suffix_rate']:.1%}")
    print(f"  Hazard tokens with suffix: {t8['hazard_tokens_with_suffix_count']}")

    # T9 summary
    t9 = results['T9_hazard_suffix_mode']
    print(f"\nT9: Hazard by suffix mode:")
    for mode, info in t9['mode_stats'].items():
        print(f"  Mode {mode}: hazard={info['hazard_rate']:.1%} F+C={info['flow_containment_rate']:.1%}")

    # T10 summary
    t10 = results['T10_modifier_hazard']
    print(f"\nT10: Modifier hazard modulation:")
    for mod in sorted(t10['modifier_stats'].keys()):
        info = t10['modifier_stats'][mod]
        print(f"  {mod}: with={info['hazard_rate_with']:.1%} without={info['hazard_rate_without']:.1%} ratio={info['hazard_ratio']:.2f}")

    print(f"\n  Compound length vs hazard:")
    for length in sorted(t10['length_stats'].keys()):
        info = t10['length_stats'][length]
        print(f"    {length}-atom: {info['hazard_rate']:.1%} ({info['n_tokens']} tokens)")

    # ========================================================================
    # SAVE
    # ========================================================================
    output_path = PROJECT_ROOT / 'phases/HAZARD_ATOM_DECOMPOSITION/results/hazard_atom_decomposition.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
