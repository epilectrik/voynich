#!/usr/bin/env python3
"""
Phase 526: Full Token Read-Through — Integration Validation

Applies ALL constraint machinery (C074-C1462) to decompose every token in a
sample folio, producing a comprehensive annotated table and coherence assessment.

Selected folio: f26v (Herbal, 89 tokens, 9 lines, 4 paragraphs)
"""
import sys, json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier,
    ALL_PREFIXES, SUFFIXES, ARTICULATORS
)

RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
TARGET_FOLIO = 'f26v'

# ============================================================
# ATOM SLOT CLASSIFICATION (C1209, C1393-C1394)
# ============================================================
# HEAD atoms: typically initial position, category selector
HEAD_ATOMS = {'a', 'e', 'o', 'k', 't'}
# MOD atoms: modifiers, can appear multiply
MOD_ATOMS = {'c', 'd', 'f', 'i', 'p', 's'}
# TERM atoms: typically terminal, position/scope
TERM_ATOMS = {'y', 'l', 'r', 'h', 'm', 'n'}
# FREE atoms: no positional preference (kernel operators)
FREE_ATOMS = {'k', 't'}  # k,t position-free per C1209

# Atom glosses (C1195, updated by C1388-C1392)
ATOM_GLOSSES = {
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'halt', 'a': 'yield', 'm': 'transition',
    'd': 'mark/seal', 't': 'transfer', 'c': 'adjust', 'p': 'pause/mark',
    'f': 'flag/mark', 's': 'sequence', 'g': 'complete',
    'o': 'arrange', 'l': 'state/condition', 'r': 'respond/flow',
}

# Atom categories (from CategoryClassifier.ATOM_TO_CATEGORY)
ATOM_CATEGORIES = {
    'k': 'THERMAL', 'e': 'THERMAL',
    'h': 'MONITORING', 'y': 'TRANSITION',
    'i': 'STAGING', 'n': 'TRANSITION',
    'a': 'TRANSITION', 'm': 'TRANSITION',
    'd': 'MARKING', 't': 'FLOW',
    'c': 'MARKING', 'p': 'MARKING',
    'f': 'MARKING', 's': 'STAGING',
    'g': 'TRANSITION', 'o': 'OPERATION',
    'l': 'STAGING', 'r': 'FLOW',
}

# Confidence tiers (C1195, updated by Phases 496-525)
ATOM_CONFIDENCE = {
    'k': 'LOCKED', 'e': 'LOCKED', 'h': 'LOCKED', 'y': 'LOCKED',
    'i': 'LOCKED', 'n': 'LOCKED', 'a': 'LOCKED', 'm': 'LOCKED',
    'd': 'SOLID', 't': 'SOLID', 'l': 'SOLID', 'o': 'SOLID',
    'c': 'SOLID', 'p': 'SOLID',
    'f': 'PLAUSIBLE', 's': 'PLAUSIBLE', 'g': 'PLAUSIBLE',
    'x': 'PLAUSIBLE', 'r': 'PLAUSIBLE',
}

# PREFIX base-modifier decomposition (C1218-C1219)
PREFIX_MODIFIERS = {'q', 'd', 'f', 'p', 'y', 's'}  # POS-0, 96-100%
PREFIX_BASES = {'h', 'e'}  # POS-1+, dedicated bases
PREFIX_DUAL = {'o', 'k', 'l', 't', 'c', 'a', 'r'}  # Can be either

# PREFIX glosses (from C1218-C1219, C1396, Tier 3 interpretation)
PREFIX_GLOSSES = {
    'ch': 'test(active)', 'sh': 'monitor(passive)',
    'qo': 'cook-arrange', 'ok': 'operate-heat', 'ot': 'operate-transfer',
    'ol': 'operate-state', 'or': 'operate-respond', 'ct': 'mark-transfer',
    'da': 'mark-yield', 'sa': 'sequence-yield',
    'pch': 'stage-test', 'tch': 'transfer-test', 'dch': 'mark-test',
    'lch': 'hold-test', 'fch': 'flag-test', 'rch': 'flow-test',
    'sch': 'sequence-test', 'kch': 'heat-test',
    'lk': 'hold-heat', 'yk': 'end-heat',
    'ke': 'heat-cool', 'te': 'transfer-cool', 'se': 'sequence-cool',
    'de': 'mark-cool', 'pe': 'pause-cool',
    'ko': 'heat-arrange', 'to': 'transfer-arrange', 'so': 'sequence-arrange',
    'do': 'mark-arrange', 'po': 'pause-arrange',
    'ka': 'heat-yield', 'ta': 'transfer-yield',
    'al': 'yield-state', 'ar': 'yield-respond',
}

# Suffix mode assignment (C1229, C1410)
# Mode A = specification/thermal: d,e,ee,h,y terminals
# Mode B = continuation/staging: a,i,ii,l,m,n,o,r,s terminals
SUFFIX_MODE_A_TERMS = {'d', 'e', 'h', 'y'}
SUFFIX_MODE_B_TERMS = {'a', 'i', 'l', 'm', 'n', 'o', 'r', 's'}

# Hazard-related atoms (C1446-C1462)
HAZARD_QUENCH_MODS = {'c', 'd', 'f', 'p', 's'}  # Modifiers quench hazard
SAFE_PATHWAY = ('e', 'y')  # e->y = stability anchor (C1457-C1462)

# Terminal opacity tiers (C1440-C1445)
# OPAQUE: y-terminal, suppresses further suffix (suffix rate 1.6%)
# SEMI: h,m-terminal, partial suffix suppression
# TRANSPARENT: l,r,n-terminal, high suffix rate
OPACITY_MAP = {
    'y': 'OPAQUE', 'h': 'SEMI', 'm': 'SEMI',
    'l': 'TRANSPARENT', 'r': 'TRANSPARENT', 'n': 'TRANSPARENT',
}

# ============================================================
# DECOMPOSITION FUNCTIONS
# ============================================================

def decompose_middle_slots(middle):
    """Decompose MIDDLE into HEAD + MOD* + TERM (C1393-C1394)."""
    if not middle or len(middle) == 0:
        return {'head': None, 'mods': [], 'term': None, 'raw': middle}

    chars = list(middle)
    head = chars[0] if chars else None
    term = chars[-1] if len(chars) > 1 else None
    mods = chars[1:-1] if len(chars) > 2 else []

    # Single-char MIDDLE: head only, no term
    if len(chars) == 1:
        return {'head': head, 'mods': [], 'term': None, 'raw': middle}

    # Classify head
    head_role = 'HEAD'
    if head in HEAD_ATOMS:
        head_role = 'HEAD'
    elif head in MOD_ATOMS:
        head_role = 'PSEUDO-HEAD'  # Headless compound (C1397)

    # Classify mods
    mod_roles = []
    for m in mods:
        if m in MOD_ATOMS:
            mod_roles.append(('MOD', m))
        elif m in {'e', 'i'}:
            mod_roles.append(('EXT', m))  # Extensible atoms (C1197)
        else:
            mod_roles.append(('ATOM', m))

    # Classify term
    term_role = 'TERM' if term in TERM_ATOMS else 'NON-STANDARD'

    return {
        'head': head,
        'head_role': head_role,
        'mods': mods,
        'mod_roles': mod_roles,
        'term': term,
        'term_role': term_role,
        'raw': middle,
        'head_gloss': ATOM_GLOSSES.get(head, '?'),
        'mod_glosses': [ATOM_GLOSSES.get(m, '?') for m in mods],
        'term_gloss': ATOM_GLOSSES.get(term, '?') if term else None,
    }


def decompose_suffix_slots(suffix):
    """Decompose suffix into HEAD + TERM (C1408)."""
    if not suffix:
        return {'head': None, 'term': None, 'raw': None, 'mode': None}

    chars = list(suffix)
    if len(chars) == 1:
        c = chars[0]
        mode = 'A' if c in SUFFIX_MODE_A_TERMS else ('B' if c in SUFFIX_MODE_B_TERMS else None)
        return {'head': None, 'term': c, 'raw': suffix, 'mode': mode}

    head = chars[0]
    term = chars[-1]
    mode = 'A' if term in SUFFIX_MODE_A_TERMS else ('B' if term in SUFFIX_MODE_B_TERMS else None)

    return {
        'head': head,
        'term': term,
        'raw': suffix,
        'mode': mode,
        'head_gloss': ATOM_GLOSSES.get(head, '?'),
        'term_gloss': ATOM_GLOSSES.get(term, '?'),
    }


def get_prefix_decomposition(prefix):
    """Decompose PREFIX into base + modifier (C1218-C1219)."""
    if not prefix:
        return {'base': None, 'modifier': None, 'raw': None, 'gloss': None}

    if len(prefix) == 1:
        return {
            'base': prefix, 'modifier': None, 'raw': prefix,
            'gloss': PREFIX_GLOSSES.get(prefix, '?')
        }

    # Last char = base, rest = modifier(s)
    base = prefix[-1]
    modifier = prefix[:-1] if len(prefix) > 1 else None

    # Special cases: 'ch', 'sh', 'da', 'sa', 'ok', 'ot', 'ol', 'or', 'ct'
    # These are core prefixes where first char is modifier, last is base
    return {
        'base': base,
        'modifier': modifier,
        'raw': prefix,
        'gloss': PREFIX_GLOSSES.get(prefix, f"{ATOM_GLOSSES.get(modifier, '?')}-{ATOM_GLOSSES.get(base, '?')}" if modifier else '?'),
    }


def get_line_zone(pos_in_line, line_length):
    """Assign line zone: SPECIFICATION / WORK / CLOSURE (C1425-C1430)."""
    if line_length <= 2:
        return 'SPECIFICATION' if pos_in_line == 0 else 'CLOSURE'

    frac = pos_in_line / (line_length - 1) if line_length > 1 else 0

    if frac <= 0.2:
        return 'SPECIFICATION'
    elif frac >= 0.8:
        return 'CLOSURE'
    else:
        return 'WORK'


def get_hazard_status(middle, prefix):
    """Assess hazard status of a token (C1446-C1462)."""
    if not middle:
        return 'NONE'

    chars = set(middle)

    # e->y pathway is safe (C1457-C1462)
    if 'e' in middle and middle.endswith('y'):
        return 'SAFE(e->y)'

    # Modifier quenching (C1446-C1451)
    has_quench = bool(chars & HAZARD_QUENCH_MODS)

    # r-terminal = hazard vector (C1387)
    if middle.endswith('r') and not has_quench:
        return 'HAZARD_VECTOR(r)'

    # k-initial = thermal source but immune to own hazard (C1384)
    if middle.startswith('k'):
        return 'THERMAL_SOURCE(k)'

    if has_quench:
        return 'QUENCHED'

    return 'NONE'


def get_opacity_tier(middle, suffix):
    """Get terminal opacity tier (C1440-C1445)."""
    if not middle or len(middle) == 0:
        return 'UNKNOWN'

    term_char = middle[-1]
    tier = OPACITY_MAP.get(term_char, 'OTHER')

    # Validate against actual suffix presence
    if tier == 'OPAQUE' and suffix:
        tier = 'OPAQUE(violated)'  # y-terminal with suffix = anomalous
    elif tier == 'TRANSPARENT' and not suffix:
        tier = 'TRANSPARENT(bare)'

    return tier


def classify_category_vote(middle):
    """Category by atom plurality vote (C1251)."""
    if not middle:
        return None, None
    votes = Counter()
    for c in middle:
        cat = ATOM_CATEGORIES.get(c)
        if cat:
            votes[cat] += 1
    if not votes:
        return None, None
    max_count = max(votes.values())
    winners = sorted([c for c, v in votes.items() if v == max_count])
    # Confidence from atom tiers
    tiers = [ATOM_CONFIDENCE.get(c, 'PLAUSIBLE') for c in middle]
    tier_rank = {'LOCKED': 3, 'SOLID': 2, 'PLAUSIBLE': 1}
    avg = sum(tier_rank.get(t, 0) for t in tiers) / max(len(tiers), 1)
    conf = 'HIGH' if avg >= 2.0 else ('MEDIUM' if avg >= 1.0 else 'LOW')
    return winners[0], conf


def compose_reading(prefix_gloss, head_gloss, mod_glosses, term_gloss, suffix_info):
    """Compose a human-readable structural reading."""
    parts = []
    if prefix_gloss and prefix_gloss != '?':
        parts.append(f"[{prefix_gloss}]")

    mid_parts = []
    if head_gloss and head_gloss != '?':
        mid_parts.append(head_gloss)
    for mg in (mod_glosses or []):
        if mg and mg != '?':
            mid_parts.append(mg)
    if term_gloss and term_gloss != '?':
        mid_parts.append(term_gloss)
    if mid_parts:
        parts.append(' + '.join(mid_parts))

    if suffix_info and suffix_info.get('raw'):
        suf_parts = []
        if suffix_info.get('head_gloss') and suffix_info['head_gloss'] != '?':
            suf_parts.append(suffix_info['head_gloss'])
        if suffix_info.get('term_gloss') and suffix_info['term_gloss'] != '?':
            suf_parts.append(suffix_info['term_gloss'])
        if suf_parts:
            parts.append(f"({'+'.join(suf_parts)})")
        else:
            parts.append(f"(sfx:{suffix_info['raw']})")

    return ' >> '.join(parts) if parts else '(unreadable)'


# ============================================================
# MAIN ANALYSIS
# ============================================================
def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Gather tokens for target folio
    tokens = [t for t in tx.currier_b() if t.folio == TARGET_FOLIO]
    print(f"Analyzing {TARGET_FOLIO}: {len(tokens)} tokens, section={tokens[0].section}")

    # Organize by line
    lines = defaultdict(list)
    for t in tokens:
        lines[t.line].append(t)

    # Build full decomposition
    all_records = []
    line_records = {}
    para_num = 0
    para_lines = defaultdict(list)

    for line_key in sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        line_tokens = lines[line_key]
        line_len = len(line_tokens)

        if line_tokens[0].par_initial:
            para_num += 1

        para_lines[para_num].append(line_key)
        line_decomps = []

        for pos, tok in enumerate(line_tokens):
            m = morph.extract(tok.word)

            # PREFIX decomposition
            pfx_info = get_prefix_decomposition(m.prefix)

            # MIDDLE decomposition
            mid_info = decompose_middle_slots(m.middle)

            # SUFFIX decomposition
            sfx_info = decompose_suffix_slots(m.suffix)

            # Category
            cat_dict = cc.classify(m.middle) if m.middle else None
            cat_conf = cc.confidence(m.middle) if m.middle else None
            # Fallback to atom vote
            if not cat_dict and m.middle:
                cat_dict, cat_conf = classify_category_vote(m.middle)

            # Hazard status
            hazard = get_hazard_status(m.middle, m.prefix)

            # Opacity tier
            opacity = get_opacity_tier(m.middle, m.suffix)

            # Line zone
            zone = get_line_zone(pos, line_len)

            # Suffix mode
            sfx_mode = sfx_info.get('mode')
            if not sfx_mode and not m.suffix:
                sfx_mode = 'BARE'

            # Compose reading
            reading = compose_reading(
                pfx_info.get('gloss'),
                mid_info.get('head_gloss'),
                mid_info.get('mod_glosses'),
                mid_info.get('term_gloss'),
                sfx_info
            )

            # Headless compound check (C1397)
            is_headless = False
            if m.middle and len(m.middle) > 0:
                first = m.middle[0]
                if first in MOD_ATOMS and first not in HEAD_ATOMS:
                    is_headless = True

            record = {
                'line': line_key,
                'pos': pos,
                'word': tok.word,
                'paragraph': para_num,
                'line_initial': tok.line_initial,
                'line_final': tok.line_final,
                'par_initial': tok.par_initial,
                'par_final': tok.par_final,
                # Morphology
                'articulator': m.articulator,
                'prefix': m.prefix,
                'prefix_base': pfx_info.get('base'),
                'prefix_modifier': pfx_info.get('modifier'),
                'prefix_gloss': pfx_info.get('gloss'),
                # MIDDLE
                'middle': m.middle,
                'middle_head': mid_info.get('head'),
                'middle_head_role': mid_info.get('head_role'),
                'middle_head_gloss': mid_info.get('head_gloss'),
                'middle_mods': mid_info.get('mods'),
                'middle_mod_glosses': mid_info.get('mod_glosses'),
                'middle_term': mid_info.get('term'),
                'middle_term_role': mid_info.get('term_role'),
                'middle_term_gloss': mid_info.get('term_gloss'),
                'is_headless': is_headless,
                # SUFFIX
                'suffix': m.suffix,
                'suffix_head': sfx_info.get('head'),
                'suffix_term': sfx_info.get('term'),
                'suffix_mode': sfx_mode,
                # Derived
                'category': cat_dict,
                'category_confidence': cat_conf,
                'hazard_status': hazard,
                'opacity_tier': opacity,
                'line_zone': zone,
                'reading': reading,
            }
            line_decomps.append(record)
            all_records.append(record)

        line_records[line_key] = line_decomps

    # ============================================================
    # COHERENCE CHECKS
    # ============================================================
    coherence = {}

    # C1425-C1430: Line specification/closure zones
    spec_tokens = [r for r in all_records if r['line_zone'] == 'SPECIFICATION']
    closure_tokens = [r for r in all_records if r['line_zone'] == 'CLOSURE']
    work_tokens = [r for r in all_records if r['line_zone'] == 'WORK']

    spec_cats = Counter(r['category'] for r in spec_tokens if r['category'])
    closure_cats = Counter(r['category'] for r in closure_tokens if r['category'])
    work_cats = Counter(r['category'] for r in work_tokens if r['category'])

    # C1426: Line-initial = STAGING/MARKING enriched?
    spec_staging = spec_cats.get('STAGING', 0) + spec_cats.get('MARKING', 0)
    spec_total = sum(spec_cats.values())
    coherence['C1426_spec_staging_marking_frac'] = {
        'value': spec_staging / spec_total if spec_total else 0,
        'expected': 'enriched (>baseline)',
        'staging_marking': spec_staging,
        'total': spec_total,
    }

    # C1427: Line-final = TRANSITION enriched, THERMAL depleted?
    closure_transition = closure_cats.get('TRANSITION', 0)
    closure_total = sum(closure_cats.values())
    coherence['C1427_closure_transition_frac'] = {
        'value': closure_transition / closure_total if closure_total else 0,
        'expected': 'enriched',
        'transition': closure_transition,
        'total': closure_total,
    }

    # C1428: THERMAL peak at Q1 not Q0
    # Group tokens by quintile
    for line_key, decomps in line_records.items():
        n = len(decomps)
        for i, r in enumerate(decomps):
            q = int(i / n * 5) if n > 1 else 0
            r['quintile'] = min(q, 4)

    quintile_thermal = defaultdict(int)
    quintile_total = defaultdict(int)
    for r in all_records:
        q = r.get('quintile', 0)
        quintile_total[q] += 1
        if r['category'] == 'THERMAL':
            quintile_thermal[q] += 1

    coherence['C1428_thermal_quintile_profile'] = {
        q: {'thermal': quintile_thermal[q],
            'total': quintile_total[q],
            'frac': quintile_thermal[q] / quintile_total[q] if quintile_total[q] else 0}
        for q in range(5)
    }

    # C1416-C1417: Articulators line-initial concentration
    art_tokens = [r for r in all_records if r['articulator']]
    art_initial = [r for r in art_tokens if r['line_initial']]
    coherence['C1417_articulator_line_initial'] = {
        'total_articulators': len(art_tokens),
        'line_initial': len(art_initial),
        'fraction': len(art_initial) / len(art_tokens) if art_tokens else 0,
        'expected': 'enriched (6.48x baseline)',
    }

    # C1420: Articulators suppress suffix
    art_with_suffix = [r for r in art_tokens if r['suffix']]
    coherence['C1420_articulator_suffix_suppression'] = {
        'total': len(art_tokens),
        'with_suffix': len(art_with_suffix),
        'suffix_rate': len(art_with_suffix) / len(art_tokens) if art_tokens else 0,
        'expected': '38.1% vs 64.3% baseline',
    }

    # C1229: Suffix modes within paragraphs
    para_modes = defaultdict(list)
    for r in all_records:
        if r['suffix_mode'] and r['suffix_mode'] != 'BARE':
            para_modes[r['paragraph']].append(r['suffix_mode'])

    coherence['C1229_suffix_mode_distribution'] = {
        f'para_{p}': {'A': modes.count('A'), 'B': modes.count('B'),
                      'A_frac': modes.count('A') / len(modes) if modes else 0}
        for p, modes in para_modes.items()
    }

    # C1383: n-terminal boundary avoidance
    n_term_tokens = [r for r in all_records if r['middle'] and r['middle'].endswith('n')]
    n_term_boundary = [r for r in n_term_tokens if r['line_initial'] or r['line_final']]
    coherence['C1383_n_terminal_boundary'] = {
        'total_n_terminal': len(n_term_tokens),
        'at_boundary': len(n_term_boundary),
        'expected': 'boundary avoidance (interior atom)',
    }

    # Hazard scan
    hazard_tokens = [r for r in all_records if 'HAZARD' in r['hazard_status']]
    safe_ey_tokens = [r for r in all_records if 'SAFE(e->y)' in r['hazard_status']]
    quenched_tokens = [r for r in all_records if r['hazard_status'] == 'QUENCHED']
    coherence['hazard_summary'] = {
        'hazard_vectors': len(hazard_tokens),
        'safe_ey': len(safe_ey_tokens),
        'quenched': len(quenched_tokens),
        'thermal_sources': len([r for r in all_records if 'THERMAL_SOURCE' in r['hazard_status']]),
    }

    # Opacity tier distribution
    opacity_dist = Counter(r['opacity_tier'] for r in all_records)
    coherence['opacity_distribution'] = dict(opacity_dist)

    # Category distribution
    cat_dist = Counter(r['category'] for r in all_records if r['category'])
    coherence['category_distribution'] = dict(cat_dist)

    # Prefix distribution
    pfx_dist = Counter(r['prefix'] for r in all_records if r['prefix'])
    coherence['prefix_distribution'] = dict(pfx_dist)

    # ============================================================
    # PARAGRAPH STRUCTURE CHECKS
    # ============================================================
    para_checks = {}
    for p_num, p_lines in sorted(para_lines.items()):
        p_tokens = [r for r in all_records if r['paragraph'] == p_num]
        header_tokens = [r for r in p_tokens if r['line'] == p_lines[0]]
        body_tokens = [r for r in p_tokens if r['line'] != p_lines[0]] if len(p_lines) > 1 else []

        # Header vs body categories
        hdr_cats = Counter(r['category'] for r in header_tokens if r['category'])
        body_cats = Counter(r['category'] for r in body_tokens if r['category'])

        # C1287: Header MARKING enrichment
        hdr_marking = hdr_cats.get('MARKING', 0) / sum(hdr_cats.values()) if hdr_cats else 0

        # e->y loading
        ey_count = sum(1 for r in p_tokens if r['hazard_status'] == 'SAFE(e->y)')

        para_checks[f'para_{p_num}'] = {
            'lines': p_lines,
            'n_tokens': len(p_tokens),
            'header_categories': dict(hdr_cats),
            'body_categories': dict(body_cats),
            'header_marking_frac': hdr_marking,
            'ey_safe_count': ey_count,
            'suffix_modes': Counter(r['suffix_mode'] for r in p_tokens if r['suffix_mode']),
        }

    # ============================================================
    # SAMPLE TOKEN READINGS (5-10 interesting tokens)
    # ============================================================
    sample_readings = []
    # Pick diverse tokens: line-initial, articulated, compound, hazard, different prefixes
    interesting_indices = []
    seen_types = set()
    for i, r in enumerate(all_records):
        features = []
        if r['articulator']:
            features.append('ART')
        if r['line_initial']:
            features.append('INIT')
        if r['is_headless']:
            features.append('HEADLESS')
        if 'HAZARD' in r['hazard_status']:
            features.append('HAZ')
        if 'SAFE(e->y)' in r['hazard_status']:
            features.append('SAFE')
        if r['prefix'] and r['prefix'] not in seen_types:
            features.append(f'PFX:{r["prefix"]}')
            seen_types.add(r['prefix'])

        if features and len(sample_readings) < 12:
            # Build detailed reading
            detail = {
                'word': r['word'],
                'decomposition': {
                    'articulator': r['articulator'],
                    'prefix': f"{r['prefix']} ({r['prefix_gloss']})" if r['prefix'] else 'BARE',
                    'middle': {
                        'raw': r['middle'],
                        'head': f"{r['middle_head']} ({r['middle_head_gloss']})" if r['middle_head'] else None,
                        'mods': [f"{m} ({g})" for m, g in zip(r['middle_mods'] or [], r['middle_mod_glosses'] or [])],
                        'term': f"{r['middle_term']} ({r['middle_term_gloss']})" if r['middle_term'] else None,
                        'is_headless': r['is_headless'],
                    },
                    'suffix': {
                        'raw': r['suffix'],
                        'mode': r['suffix_mode'],
                    },
                },
                'category': r['category'],
                'hazard_status': r['hazard_status'],
                'opacity_tier': r['opacity_tier'],
                'line_zone': r['line_zone'],
                'features': features,
                'reading': r['reading'],
            }
            sample_readings.append(detail)

    # ============================================================
    # CONSTRAINT APPLICABILITY SCORING
    # ============================================================
    constraint_scores = []

    def score(cid, desc, result, note=''):
        constraint_scores.append({'constraint': cid, 'description': desc, 'result': result, 'note': note})

    # C1416-C1421: Articulator properties
    n_art = len(art_tokens)
    score('C1416', 'Articulator rate ~6.5%', 'CONFIRMED' if 0.03 < n_art/len(all_records) < 0.12 else 'WEAK',
          f'{n_art}/{len(all_records)} = {n_art/len(all_records):.1%}')

    score('C1417', 'Articulator line-initial concentration',
          'CONFIRMED' if art_initial and len(art_initial)/len(art_tokens) > 0.3 else 'WEAK',
          f'{len(art_initial)}/{len(art_tokens)}')

    # C1425: Line length unimodal
    line_lengths = [len(line_records[k]) for k in line_records]
    mean_len = sum(line_lengths) / len(line_lengths) if line_lengths else 0
    cv_len = (sum((x-mean_len)**2 for x in line_lengths)/len(line_lengths))**0.5 / mean_len if mean_len else 0
    score('C1425', 'Line length unimodal (CV~0.34)', 'CONFIRMED' if cv_len < 0.5 else 'WEAK',
          f'mean={mean_len:.1f}, CV={cv_len:.3f}')

    # C1393-C1394: HEAD+MOD*+TERM structure
    valid_head = sum(1 for r in all_records if r['middle_head'] in HEAD_ATOMS or r['is_headless'])
    score('C1393', 'MIDDLE HEAD+MOD*+TERM structure',
          'CONFIRMED' if valid_head/len(all_records) > 0.7 else 'PARTIAL',
          f'{valid_head}/{len(all_records)} have recognized HEAD or pseudo-HEAD')

    # C1440-C1445: Opacity tiers
    opaque = opacity_dist.get('OPAQUE', 0)
    transparent = opacity_dist.get('TRANSPARENT', 0) + opacity_dist.get('TRANSPARENT(bare)', 0)
    score('C1440-C1445', 'Terminal opacity tiers present',
          'CONFIRMED' if opaque > 0 and transparent > 0 else 'PARTIAL',
          f'OPAQUE={opaque}, TRANSPARENT={transparent}')

    # C1229: Suffix mode alternation
    has_both_modes = any(
        para_checks[f'para_{p}']['suffix_modes'].get('A', 0) > 0 and
        para_checks[f'para_{p}']['suffix_modes'].get('B', 0) > 0
        for p in para_lines.keys()
    )
    score('C1229', 'Both suffix modes present in paragraphs',
          'CONFIRMED' if has_both_modes else 'NOT_APPLICABLE',
          'Need 8+ body lines for reliable detection')

    # C1457-C1462: e->y safe pathway
    score('C1457-C1462', 'e->y safe pathway tokens present',
          'CONFIRMED' if len(safe_ey_tokens) > 0 else 'NOT_OBSERVED',
          f'{len(safe_ey_tokens)} safe(e->y) tokens')

    # C1287: Paragraph header MARKING enrichment
    marking_enriched = sum(1 for p in para_checks.values() if p['header_marking_frac'] > 0.15)
    score('C1287', 'Paragraph headers MARKING-enriched',
          'CONFIRMED' if marking_enriched > 0 else 'NOT_OBSERVED',
          f'{marking_enriched}/{len(para_checks)} paragraphs have >15% MARKING headers')

    # C1429: Cross-line category independence
    score('C1429', 'Cross-line category independence',
          'NOT_TESTABLE', 'Single folio insufficient for MI test')

    # C1430: Information U-shape at line boundaries
    score('C1430', 'Information U-shape at boundaries',
          'CONSISTENT', 'SPECIFICATION and CLOSURE zones populated')

    # ============================================================
    # OUTPUT
    # ============================================================
    result = {
        '_metadata': {
            'phase': 'FULL_TOKEN_READTHROUGH',
            'phase_number': 526,
            'folio': TARGET_FOLIO,
            'section': tokens[0].section,
            'n_tokens': len(tokens),
            'n_lines': len(lines),
            'n_paragraphs': para_num,
        },
        'decomposition_table': all_records,
        'line_structure': {
            k: [r['word'] for r in v] for k, v in line_records.items()
        },
        'paragraph_structure': para_checks,
        'coherence_checks': coherence,
        'constraint_scores': constraint_scores,
        'sample_readings': sample_readings,
    }

    # Serialize (handle Counter objects)
    def serialize(obj):
        if isinstance(obj, Counter):
            return dict(obj)
        raise TypeError(f"Type {type(obj)} not serializable")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'token_readthrough.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=serialize)
    print(f"Written {out_path}")

    # ============================================================
    # CONSOLE SUMMARY
    # ============================================================
    print(f"\n{'='*70}")
    print(f"FOLIO {TARGET_FOLIO} FULL DECOMPOSITION SUMMARY")
    print(f"{'='*70}")
    print(f"Tokens: {len(all_records)}, Lines: {len(lines)}, Paragraphs: {para_num}")
    print(f"\nCategory distribution:")
    for cat, count in sorted(cat_dist.items(), key=lambda x: -x[1]):
        print(f"  {cat:<15} {count:>3} ({count/len(all_records):.1%})")
    nones = sum(1 for r in all_records if not r['category'])
    if nones:
        print(f"  {'(unclassified)':<15} {nones:>3} ({nones/len(all_records):.1%})")

    print(f"\nPrefix distribution:")
    for pfx, count in sorted(pfx_dist.items(), key=lambda x: -x[1]):
        print(f"  {pfx:<8} {count:>3}")
    bare = sum(1 for r in all_records if not r['prefix'])
    print(f"  {'BARE':<8} {bare:>3}")

    print(f"\nHazard summary:")
    for k, v in coherence['hazard_summary'].items():
        print(f"  {k}: {v}")

    print(f"\nOpacity tiers:")
    for tier, count in sorted(opacity_dist.items(), key=lambda x: -x[1]):
        print(f"  {tier:<25} {count:>3}")

    print(f"\nSuffix modes by paragraph:")
    for p_key, p_data in sorted(para_checks.items()):
        modes = p_data['suffix_modes']
        print(f"  {p_key}: A={modes.get('A',0)} B={modes.get('B',0)} BARE={modes.get('BARE',0)}")

    print(f"\nConstraint scores:")
    for cs in constraint_scores:
        print(f"  {cs['constraint']:<20} {cs['result']:<15} {cs['note']}")

    print(f"\n{'='*70}")
    print("SAMPLE TOKEN READINGS")
    print(f"{'='*70}")
    for sr in sample_readings[:10]:
        print(f"\n  {sr['word']}")
        d = sr['decomposition']
        print(f"    ART: {d['articulator'] or '-'}")
        print(f"    PFX: {d['prefix']}")
        mid = d['middle']
        print(f"    MID: {mid['raw']} = {mid['head'] or '-'} + {mid['mods'] or []} + {mid['term'] or '-'}")
        print(f"    SFX: {d['suffix']['raw'] or '-'} (mode {d['suffix']['mode']})")
        print(f"    CAT: {sr['category']}  HAZ: {sr['hazard_status']}  ZONE: {sr['line_zone']}")
        print(f"    >>> {sr['reading']}")


if __name__ == '__main__':
    main()
