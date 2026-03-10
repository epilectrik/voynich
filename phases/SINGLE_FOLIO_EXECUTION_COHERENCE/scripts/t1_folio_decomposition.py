"""Phase 558 T1: Folio Decomposition — Token → Weighted Supervisory Contributions.

Maps each f43v token to a 5-field weighted supervisory instruction primitive:
  {domain_weights, permission_weights, guard_weights, routing_weights, scope_weights}

Verifies paragraph segmentation as blocking prerequisite.
Generates 4 null variants × 50 seeds.

Output: t1_folio_decomposition.json
"""
import sys, json, os, random
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt
from collections import Counter, defaultdict

SEED = 42
N_NULL_SEEDS = 50
FOLIO = 'f43v'

# ═══════════════════════════════════════════════════════════════
# WEIGHT TABLES — Pre-registered, constraint-derived
# All vectors sum to 1.0 within their field.
# ═══════════════════════════════════════════════════════════════

DOMAINS = ['THERMAL', 'FLOW', 'STABILIZE', 'TRANSITION', 'ARRANGE', 'CONTAIN']
PERMISSIONS = ['ALLOW', 'INHIBIT', 'HOLD', 'CLOSE', 'CHECK', 'SPECIFY']
GUARDS = ['SEALED', 'STAGED', 'FLAGGED', 'TRANSITION_ACTIVE', 'ANY']
ROUTINGS = ['CONTINUE', 'COMMIT_CLOSE', 'ROUTE_FLOW', 'STAGE_NEXT',
            'MONITOR_EXIT', 'ROUTE_CONTAIN', 'DEFAULT']
SCOPES = ['OPEN', 'CLOSED', 'REGISTER_A', 'REGISTER_B', 'IMMEDIATE']

def _vec(names, weights_dict):
    """Build a weight vector from a dict of {name: weight}, fill rest with 0."""
    v = [0.0] * len(names)
    for k, w in weights_dict.items():
        v[names.index(k)] = w
    total = sum(v)
    if total > 0:
        v = [x / total for x in v]  # renormalize
    return v

# Step 1: HEAD → domain weights (C1446, C1475-C1479, C1556)
HEAD_DOMAIN = {
    'k': _vec(DOMAINS, {'THERMAL': 0.85, 'STABILIZE': 0.15}),
    't': _vec(DOMAINS, {'FLOW': 0.75, 'THERMAL': 0.15, 'ARRANGE': 0.10}),
    'e': _vec(DOMAINS, {'STABILIZE': 0.60, 'THERMAL': 0.20, 'CONTAIN': 0.20}),
    'a': _vec(DOMAINS, {'TRANSITION': 0.70, 'CONTAIN': 0.20, 'ARRANGE': 0.10}),
    'o': _vec(DOMAINS, {'ARRANGE': 0.65, 'CONTAIN': 0.20, 'STABILIZE': 0.15}),
    None: _vec(DOMAINS, {'CONTAIN': 0.80, 'TRANSITION': 0.20}),  # headless
}

# Step 2: PREFIX → permission weights (C929, C1243, C1426-C1428, C1491, C1534-C1539)
# PREFIX families: group prefixes by base character and behavior
PREFIX_FAMILIES = {
    # qo family
    'qo': 'qo',
    # ch family (active checkpoint)
    'ch': 'ch', 'pch': 'ch', 'tch': 'ch', 'kch': 'ch', 'dch': 'ch',
    'fch': 'ch', 'rch': 'ch', 'sch': 'ch', 'lch': 'ch',
    # sh family (passive monitor)
    'sh': 'sh', 'lsh': 'sh',
    # ok/ot family (standard operational)
    'ok': 'ok_ot', 'ot': 'ok_ot', 'ct': 'ok_ot',
    # da family (yield/inhibit)
    'da': 'da',
    # Specification prefixes (po/dch/so/to)
    'po': 'specify', 'so': 'specify', 'to': 'specify', 'do': 'specify',
    'ko': 'specify',
    # Closure prefixes (ar/al/or)
    'ar': 'close', 'al': 'close', 'or': 'close', 'ol': 'close',
    # xE family — map to operational
    'ke': 'ok_ot', 'te': 'ok_ot', 'se': 'ok_ot', 'de': 'ok_ot', 'pe': 'ok_ot',
    # xK family
    'lk': 'ok_ot', 'yk': 'ok_ot',
    # xA family — transitional
    'ta': 'da', 'ka': 'da', 'sa': 'da',
}

PREFIX_PERMISSION = {
    'qo':      _vec(PERMISSIONS, {'ALLOW': 0.85, 'SPECIFY': 0.15}),
    'ch':      _vec(PERMISSIONS, {'CHECK': 0.70, 'HOLD': 0.20, 'ALLOW': 0.10}),
    'sh':      _vec(PERMISSIONS, {'HOLD': 0.65, 'CHECK': 0.20, 'ALLOW': 0.15}),
    'ok_ot':   _vec(PERMISSIONS, {'ALLOW': 0.75, 'HOLD': 0.15, 'SPECIFY': 0.10}),
    'da':      _vec(PERMISSIONS, {'INHIBIT': 0.80, 'CLOSE': 0.15, 'HOLD': 0.05}),
    'specify': _vec(PERMISSIONS, {'SPECIFY': 0.80, 'INHIBIT': 0.10, 'HOLD': 0.10}),
    'close':   _vec(PERMISSIONS, {'CLOSE': 0.75, 'INHIBIT': 0.15, 'HOLD': 0.10}),
    'bare':    _vec(PERMISSIONS, {'ALLOW': 0.50, 'INHIBIT': 0.30, 'HOLD': 0.20}),
}

# Step 3: MODIFIER → guard weights (C1472-C1474, C1479)
MOD_GUARD = {
    'd': _vec(GUARDS, {'SEALED': 0.70, 'ANY': 0.30}),
    'p': _vec(GUARDS, {'STAGED': 0.65, 'ANY': 0.35}),
    'f': _vec(GUARDS, {'FLAGGED': 0.70, 'ANY': 0.30}),
    'i': _vec(GUARDS, {'TRANSITION_ACTIVE': 0.65, 'ANY': 0.35}),
    'c': _vec(GUARDS, {'ANY': 0.90, 'STAGED': 0.10}),
    's': _vec(GUARDS, {'ANY': 0.95, 'STAGED': 0.05}),
    '': _vec(GUARDS, {'ANY': 1.0}),  # no modifier
}

# Step 4: TERMINAL → routing weights (C1434-C1439, C1440, C1483-C1487, C1563)
TERM_ROUTING = {
    'y': _vec(ROUTINGS, {'CONTINUE': 0.75, 'DEFAULT': 0.25}),
    'm': _vec(ROUTINGS, {'COMMIT_CLOSE': 0.90, 'ROUTE_CONTAIN': 0.10}),
    'r': _vec(ROUTINGS, {'ROUTE_FLOW': 0.85, 'CONTINUE': 0.15}),
    'l': _vec(ROUTINGS, {'STAGE_NEXT': 0.70, 'CONTINUE': 0.20, 'DEFAULT': 0.10}),
    'h': _vec(ROUTINGS, {'MONITOR_EXIT': 0.80, 'CONTINUE': 0.20}),
    'n': _vec(ROUTINGS, {'ROUTE_CONTAIN': 0.65, 'COMMIT_CLOSE': 0.20, 'DEFAULT': 0.15}),
    'bare': _vec(ROUTINGS, {'DEFAULT': 0.85, 'CONTINUE': 0.15}),
}

# Step 5: SUFFIX → scope weights (C1440-C1445, C1510-C1515)
# Determined by terminal transparency + suffix content
# Mode A atoms: a, i (from C1229-C1231)
# Mode B atoms: o, e (from C1229-C1231)
MODE_A_ATOMS = set('ai')
MODE_B_ATOMS = set('oe')


def get_scope_weights(suffix, terminal):
    """Compute scope weights from suffix content and terminal transparency."""
    if suffix is None:
        return _vec(SCOPES, {'IMMEDIATE': 1.0})

    # Terminal transparency affects scope
    if terminal == 'h':
        base = {'OPEN': 0.80, 'IMMEDIATE': 0.20}
    elif terminal in ('m', 'n', 'y'):
        base = {'CLOSED': 0.80, 'IMMEDIATE': 0.20}
    else:
        base = {'IMMEDIATE': 0.60, 'OPEN': 0.40}

    # Check suffix content for register bias
    suffix_chars = set(suffix)
    a_count = len(suffix_chars & MODE_A_ATOMS)
    b_count = len(suffix_chars & MODE_B_ATOMS)

    if a_count > b_count:
        # Blend register bias into scope
        result = {}
        for k, v in base.items():
            result[k] = v * 0.5
        result['REGISTER_A'] = result.get('REGISTER_A', 0) + 0.5
        return _vec(SCOPES, result)
    elif b_count > a_count:
        result = {}
        for k, v in base.items():
            result[k] = v * 0.5
        result['REGISTER_B'] = result.get('REGISTER_B', 0) + 0.5
        return _vec(SCOPES, result)

    return _vec(SCOPES, base)


def get_prefix_family(prefix):
    """Map a prefix string to its family key."""
    if prefix is None:
        return 'bare'
    if prefix in PREFIX_FAMILIES:
        return PREFIX_FAMILIES[prefix]
    # Try without first char as modifier (e.g., 'dch' -> 'ch' family)
    if len(prefix) > 1 and prefix[1:] in PREFIX_FAMILIES:
        return PREFIX_FAMILIES[prefix[1:]]
    return 'bare'


def decompose_token(word, morph):
    """Decompose a token into 5-field weighted supervisory instruction.

    Returns dict with keys: domain, permission, guard, routing, scope
    Each value is a list of floats (weight vector).
    Also returns metadata for diagnostics.
    """
    m = morph.extract(word)

    # Get MIDDLE decomposition
    head = None
    mods_str = ''
    term = 'bare'
    if m.middle and m.middle != '_EMPTY_':
        head, mods_str, term, frame = decompose_middle_hmt(m.middle)
    else:
        frame = 'none->bare'

    # Step 1: HEAD → domain
    domain = HEAD_DOMAIN.get(head, HEAD_DOMAIN[None])

    # Step 2: PREFIX → permission
    pfx_family = get_prefix_family(m.prefix)
    # Also consider prefix2
    if m.prefix2:
        pfx2_family = get_prefix_family(m.prefix2)
        # Blend primary and secondary prefix permissions (70/30)
        perm1 = PREFIX_PERMISSION.get(pfx_family, PREFIX_PERMISSION['bare'])
        perm2 = PREFIX_PERMISSION.get(pfx2_family, PREFIX_PERMISSION['bare'])
        permission = [0.7 * p1 + 0.3 * p2 for p1, p2 in zip(perm1, perm2)]
        total = sum(permission)
        permission = [x / total for x in permission] if total > 0 else permission
    else:
        permission = PREFIX_PERMISSION.get(pfx_family, PREFIX_PERMISSION['bare'])

    # Step 3: MODIFIER → guard
    # Use first modifier character if multiple
    mod_char = mods_str[0] if mods_str else ''
    guard = MOD_GUARD.get(mod_char, MOD_GUARD[''])

    # If multiple modifiers, blend (first modifier 70%, second 30%)
    if len(mods_str) > 1:
        mod2_char = mods_str[1]
        guard2 = MOD_GUARD.get(mod2_char, MOD_GUARD[''])
        guard = [0.7 * g1 + 0.3 * g2 for g1, g2 in zip(guard, guard2)]
        total = sum(guard)
        guard = [x / total for x in guard] if total > 0 else guard

    # Step 4: TERMINAL → routing
    routing = TERM_ROUTING.get(term, TERM_ROUTING['bare'])

    # Step 5: SUFFIX → scope
    scope = get_scope_weights(m.suffix, term)

    # Step 6: ARTICULATOR override
    has_articulator = m.has_articulator
    if has_articulator:
        # Boost SPECIFY permission, STABILIZE domain, HOLD routing
        # Articulator dominates but doesn't replace
        permission = [p * 0.3 for p in permission]
        permission[PERMISSIONS.index('SPECIFY')] += 0.70
        total = sum(permission)
        permission = [x / total for x in permission]

        domain = [d * 0.4 for d in domain]
        domain[DOMAINS.index('STABILIZE')] += 0.60
        total = sum(domain)
        domain = [x / total for x in domain]

        routing = [r * 0.5 for r in routing]
        routing[ROUTINGS.index('MONITOR_EXIT')] += 0.50
        total = sum(routing)
        routing = [x / total for x in routing]

    return {
        'domain': domain,
        'permission': permission,
        'guard': guard,
        'routing': routing,
        'scope': scope,
    }, {
        'word': word,
        'articulator': m.articulator,
        'prefix': m.prefix,
        'prefix2': m.prefix2,
        'middle': m.middle,
        'suffix': m.suffix,
        'head': head,
        'mods': mods_str,
        'terminal': term,
        'frame': frame,
        'has_articulator': has_articulator,
        'prefix_family': pfx_family,
    }


def assign_quintile(position, n_tokens):
    """Assign Q0-Q4 quintile based on position within line."""
    if n_tokens <= 0:
        return 0
    frac = position / max(n_tokens - 1, 1)
    return min(int(frac * 5), 4)


def main():
    tx = Transcript()
    morph = Morphology()

    # ═══════════════════════════════════════════════════════════════
    # BLOCKING PREREQUISITE: Verify paragraph segmentation
    # ═══════════════════════════════════════════════════════════════

    all_b_tokens = list(tx.currier_b(exclude_uncertain=True))
    tokens = [t for t in all_b_tokens if t.folio == FOLIO]

    print(f"=== f43v: {len(tokens)} tokens ===\n")

    # Method 1: par_initial field
    par_boundaries_field = []
    for i, t in enumerate(tokens):
        if t.par_initial:
            par_boundaries_field.append(i)
            print(f"  PAR_INITIAL (field): idx={i}, line={t.line}, word={t.word}")

    # Method 2: gallows-initial detection
    GALLOWS = set('ptkf')
    par_boundaries_gallows = []
    for i, t in enumerate(tokens):
        if t.line_initial and t.word and t.word[0] in GALLOWS:
            par_boundaries_gallows.append(i)
            print(f"  GALLOWS_INITIAL: idx={i}, line={t.line}, word={t.word}")

    # Compare
    segmentation_match = par_boundaries_field == par_boundaries_gallows
    print(f"\n  Segmentation match: {segmentation_match}")
    print(f"  Field paragraphs: {len(par_boundaries_field)}")
    print(f"  Gallows paragraphs: {len(par_boundaries_gallows)}")

    # Use par_initial as primary (transcript annotation is authoritative)
    paragraph_starts = par_boundaries_field

    # ═══════════════════════════════════════════════════════════════
    # Build paragraph → line → token structure
    # ═══════════════════════════════════════════════════════════════

    paragraphs = []
    for pi, start_idx in enumerate(paragraph_starts):
        end_idx = paragraph_starts[pi + 1] if pi + 1 < len(paragraph_starts) else len(tokens)
        para_tokens = tokens[start_idx:end_idx]
        paragraphs.append(para_tokens)

    # Build lines within paragraphs
    paragraph_data = []
    for pi, para_tokens in enumerate(paragraphs):
        lines = defaultdict(list)
        for t in para_tokens:
            lines[t.line].append(t)
        line_numbers = sorted(lines.keys())

        para_info = {
            'paragraph_index': pi,
            'line_range': [line_numbers[0], line_numbers[-1]],
            'n_lines': len(line_numbers),
            'n_tokens': len(para_tokens),
            'opens_with': para_tokens[0].word,
            'lines': [],
        }

        for ln in line_numbers:
            line_tokens = lines[ln]
            n_tok = len(line_tokens)
            line_data = {
                'line': ln,
                'n_tokens': n_tok,
                'tokens': [],
            }

            for pos, t in enumerate(line_tokens):
                weights, meta = decompose_token(t.word, morph)
                quintile = assign_quintile(pos, n_tok)

                line_data['tokens'].append({
                    'position': pos,
                    'quintile': quintile,
                    'word': t.word,
                    'weights': weights,
                    'meta': meta,
                    'line_initial': t.line_initial,
                    'line_final': t.line_final,
                })

            para_info['lines'].append(line_data)

        paragraph_data.append(para_info)

    # ═══════════════════════════════════════════════════════════════
    # Compute paragraph-level profiles (INFERRED emphases)
    # ═══════════════════════════════════════════════════════════════

    paragraph_profiles = []
    for pi, para in enumerate(paragraph_data):
        domain_accum = [0.0] * len(DOMAINS)
        permission_accum = [0.0] * len(PERMISSIONS)
        n = 0
        for line in para['lines']:
            for tok in line['tokens']:
                for di in range(len(DOMAINS)):
                    domain_accum[di] += tok['weights']['domain'][di]
                for pi2 in range(len(PERMISSIONS)):
                    permission_accum[pi2] += tok['weights']['permission'][pi2]
                n += 1

        if n > 0:
            domain_accum = [x / n for x in domain_accum]
            permission_accum = [x / n for x in permission_accum]

        # Find dominant domain and permission
        dom_domain = DOMAINS[domain_accum.index(max(domain_accum))]
        dom_permission = PERMISSIONS[permission_accum.index(max(permission_accum))]

        profile = {
            'paragraph_index': pi,
            'n_tokens': para['n_tokens'],
            'mean_domain_weights': dict(zip(DOMAINS, [round(x, 4) for x in domain_accum])),
            'mean_permission_weights': dict(zip(PERMISSIONS, [round(x, 4) for x in permission_accum])),
            'dominant_domain': dom_domain,
            'dominant_permission': dom_permission,
            'inferred_emphasis': f"{dom_domain}/{dom_permission}",
        }
        paragraph_profiles.append(profile)

    print("\n=== INFERRED PARAGRAPH PROFILES ===")
    for p in paragraph_profiles:
        print(f"  P{p['paragraph_index']+1}: {p['inferred_emphasis']} "
              f"({p['n_tokens']} tokens)")
        print(f"    Domains: {p['mean_domain_weights']}")
        print(f"    Permissions: {p['mean_permission_weights']}")

    # ═══════════════════════════════════════════════════════════════
    # Generate null variants
    # ═══════════════════════════════════════════════════════════════

    # Collect all B-corpus vocabulary for random-token null
    b_vocab = list(set(t.word for t in all_b_tokens if t.word and t.word.strip()))

    null_variants = {
        'token_shuffle': [],    # Shuffle tokens within each line
        'line_shuffle': [],     # Shuffle lines within each paragraph
        'cross_paragraph': [],  # Shuffle lines across all paragraphs
        'random_token': [],     # Replace with random B-corpus tokens
    }

    # Pre-decompose all tokens for efficiency
    all_decomposed = {}
    for w in set(t.word for t in tokens):
        all_decomposed[w] = decompose_token(w, morph)

    # Pre-decompose a sample of B-corpus vocabulary
    for w in b_vocab:
        if w not in all_decomposed:
            all_decomposed[w] = decompose_token(w, morph)

    for seed in range(N_NULL_SEEDS):
        rng = random.Random(SEED + seed)

        # NULL 1: Token-shuffle within each line
        ts_paragraphs = []
        for para in paragraph_data:
            ts_para = {'lines': []}
            for line in para['lines']:
                tok_words = [t['word'] for t in line['tokens']]
                rng.shuffle(tok_words)
                ts_line = {'line': line['line'], 'n_tokens': line['n_tokens'], 'tokens': []}
                for pos, w in enumerate(tok_words):
                    weights, meta = all_decomposed[w]
                    quintile = assign_quintile(pos, line['n_tokens'])
                    ts_line['tokens'].append({
                        'position': pos, 'quintile': quintile,
                        'word': w, 'weights': weights, 'meta': meta,
                    })
                ts_para['lines'].append(ts_line)
            ts_paragraphs.append(ts_para)
        null_variants['token_shuffle'].append(ts_paragraphs)

        # NULL 2: Line-shuffle within each paragraph
        ls_paragraphs = []
        for para in paragraph_data:
            shuffled_lines = list(para['lines'])
            rng.shuffle(shuffled_lines)
            ls_paragraphs.append({'lines': shuffled_lines})
        null_variants['line_shuffle'].append(ls_paragraphs)

        # NULL 3: Cross-paragraph shuffle
        all_lines = []
        for para in paragraph_data:
            all_lines.extend(para['lines'])
        rng.shuffle(all_lines)
        # Re-distribute to paragraphs (same paragraph sizes)
        cp_paragraphs = []
        idx = 0
        for para in paragraph_data:
            n_lines = len(para['lines'])
            cp_paragraphs.append({'lines': all_lines[idx:idx + n_lines]})
            idx += n_lines
        null_variants['cross_paragraph'].append(cp_paragraphs)

        # NULL 4: Random-token replacement
        rt_paragraphs = []
        for para in paragraph_data:
            rt_para = {'lines': []}
            for line in para['lines']:
                rt_line = {'line': line['line'], 'n_tokens': line['n_tokens'], 'tokens': []}
                for pos in range(line['n_tokens']):
                    w = rng.choice(b_vocab)
                    weights, meta = all_decomposed[w]
                    quintile = assign_quintile(pos, line['n_tokens'])
                    rt_line['tokens'].append({
                        'position': pos, 'quintile': quintile,
                        'word': w, 'weights': weights, 'meta': meta,
                    })
                rt_para['lines'].append(rt_line)
            rt_paragraphs.append(rt_para)
        null_variants['random_token'].append(rt_paragraphs)

    # ═══════════════════════════════════════════════════════════════
    # Diagnostic summary
    # ═══════════════════════════════════════════════════════════════

    print(f"\n=== DECOMPOSITION SUMMARY ===")
    print(f"  Tokens decomposed: {len(tokens)}")
    print(f"  Paragraphs: {len(paragraphs)}")
    for pi, para in enumerate(paragraph_data):
        print(f"  P{pi+1}: {para['n_lines']} lines, {para['n_tokens']} tokens, "
              f"lines {para['line_range'][0]}-{para['line_range'][1]}")

    # HEAD distribution
    head_counts = Counter()
    for t in tokens:
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_':
            h, _, _, _ = decompose_middle_hmt(m.middle)
            head_counts[h or 'headless'] += 1
        else:
            head_counts['headless'] += 1
    print(f"  HEAD distribution: {dict(head_counts.most_common())}")

    # PREFIX family distribution
    pfx_counts = Counter()
    for t in tokens:
        m = morph.extract(t.word)
        pfx_counts[get_prefix_family(m.prefix)] += 1
    print(f"  PREFIX family distribution: {dict(pfx_counts.most_common())}")

    # Terminal distribution
    term_counts = Counter()
    for t in tokens:
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_':
            _, _, term, _ = decompose_middle_hmt(m.middle)
            term_counts[term] += 1
        else:
            term_counts['bare'] += 1
    print(f"  TERMINAL distribution: {dict(term_counts.most_common())}")

    print(f"\n  Null variants generated: {N_NULL_SEEDS} seeds × 4 types")
    print(f"  B-corpus vocabulary size: {len(b_vocab)}")

    # ═══════════════════════════════════════════════════════════════
    # Save output (compact: exclude null variant details for size)
    # ═══════════════════════════════════════════════════════════════

    # For null variants, only store the weight vectors (not meta) to save space
    def compact_null(null_paragraphs):
        """Strip meta from null variant to reduce JSON size."""
        result = []
        for para in null_paragraphs:
            compact_para = {'lines': []}
            for line in para['lines']:
                compact_line = {
                    'line': line['line'],
                    'n_tokens': line['n_tokens'],
                    'tokens': [],
                }
                for tok in line['tokens']:
                    compact_line['tokens'].append({
                        'position': tok['position'],
                        'quintile': tok['quintile'],
                        'word': tok['word'],
                        'weights': tok['weights'],
                    })
                compact_para['lines'].append(compact_line)
            result.append(compact_para)
        return result

    compact_nulls = {}
    for null_type, seeds in null_variants.items():
        compact_nulls[null_type] = [compact_null(s) for s in seeds]

    output = {
        'folio': FOLIO,
        'n_tokens': len(tokens),
        'n_paragraphs': len(paragraphs),
        'segmentation': {
            'method': 'par_initial',
            'match_gallows': segmentation_match,
            'par_initial_indices': par_boundaries_field,
            'gallows_initial_indices': par_boundaries_gallows,
        },
        'field_names': {
            'domains': DOMAINS,
            'permissions': PERMISSIONS,
            'guards': GUARDS,
            'routings': ROUTINGS,
            'scopes': SCOPES,
        },
        'paragraphs': paragraph_data,
        'paragraph_profiles': paragraph_profiles,
        'null_variants': compact_nulls,
        'diagnostics': {
            'head_distribution': dict(head_counts),
            'prefix_family_distribution': dict(pfx_counts),
            'terminal_distribution': dict(term_counts),
            'b_vocab_size': len(b_vocab),
            'n_null_seeds': N_NULL_SEEDS,
        },
    }

    out_path = os.path.join(os.path.dirname(__file__), '..', 'results', 't1_folio_decomposition.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Output written to {out_path}")
    print(f"  Output size: {os.path.getsize(out_path) / 1024:.1f} KB")


if __name__ == '__main__':
    main()
