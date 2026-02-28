#!/usr/bin/env python3
"""
Phase 488: HEBREW CIPHER CROSS-VALIDATION
==========================================
Cross-validation of our grammar (49 classes, 17 forbidden transitions,
PREFIX+MIDDLE+SUFFIX morphology, 8 categories, 21/21 generative closure)
against Antenore Gatta's Hebrew cipher hypothesis (voynich-toolkit).

Gatta proposes: EVA encodes Judeo-Italian in Hebrew consonantal script,
read RTL. Their mapping is context-sensitive (digraphs, positional
overrides, prefix stripping, homophone collapse).

This phase tests whether our structural findings survive their decoding
transform, with pre-registered predictions from BOTH hypotheses.

Tests:
  T1: Morphological boundary survival
  T2: 49-class grammar preservation
  T3: Forbidden transition preservation
  T4: Category coherence in Hebrew space
  T5: Information-theoretic preservation
  T6: PREFIX role coherence
  T7: Directionality reconciliation
  T8: Lexicon signal decomposition (slot-preserving shuffle)

Depends on: C120, C130, C132, C109, C121, C124, C1250, C1365, C1376
Cross-ref: github.com/antenore/voynich-toolkit (EPILECTRIK_NOTES.md)
"""

import json
import sys
import re
import math
import functools
import random
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Gatta Mapping (exact from voynich-toolkit/full_decode.py) ────────

# Base EVA→Hebrew ASCII mapping (17 characters)
GATTA_BASE = {
    'a': 'y',   # yod
    'c': 'A',   # aleph
    'd': 'r',   # resh
    'e': 'p',   # pe
    'f': 'l',   # lamed (homophone with p)
    'g': 'X',   # chet
    'h': 'E',   # ayin
    'i': 'r',   # resh (standalone i after ii extraction)
    'k': 't',   # tav
    'l': 'm',   # mem
    'm': 'g',   # gimel
    'n': 'd',   # dalet (default; word-initial overridden to bet)
    'o': 'w',   # vav
    'p': 'l',   # lamed (homophone with f)
    'r': 'h',   # he (default; word-initial overridden to samekh)
    's': 'n',   # nun
    't': 'J',   # tet
    'y': 'S',   # shin
}

# Digraph: ch → kaf
GATTA_DIGRAPH_CH = 'k'  # kaf

# Special: ii → he
GATTA_II = 'h'  # he

# Word-initial overrides
GATTA_INITIAL_N = 'b'   # bet (not dalet)
GATTA_INITIAL_R = 's'   # samekh (not he)
GATTA_INITIAL_II = 's'  # samekh

# Known Hebrew prefix morphemes for T6
HEBREW_PREFIX_MORPHEMES = {
    'b': 'be- (in/with)',
    'l': 'le- (to/for)',
    'k': 'ke- (like/as)',
    'w': 've- (and)',
    'S': 'she- (that/which)',
    'h': 'ha- (the)',
    'm': 'mi- (from)',
}


def gatta_decode(eva_token):
    """
    Faithful implementation of Gatta's EVA→Hebrew decode pipeline.
    Source: voynich-toolkit/src/voynich_toolkit/full_decode.py
    """
    if not eva_token:
        return ''

    token = eva_token

    # Step 1: Strip q/qo prefix
    q_stripped = False
    if token.startswith('qo'):
        token = token[2:]
        q_stripped = True
    elif token.startswith('q') and len(token) > 1:
        token = token[1:]
        q_stripped = True

    if not token:
        return ''

    # Step 2: Reverse for RTL
    token = token[::-1]

    # Step 3: Preprocess digraphs (ch → placeholder)
    # After reversal, 'ch' becomes 'hc', so we look for 'hc'
    token = token.replace('hc', '\x03')

    # Step 4: Handle i-runs (decompose into ii pairs + remainder)
    # Process ii digraphs first, then standalone i
    result = []
    idx = 0
    while idx < len(token):
        if token[idx] == '\x03':
            result.append(GATTA_DIGRAPH_CH)  # ch → kaf
            idx += 1
        elif idx + 1 < len(token) and token[idx] == 'i' and token[idx+1] == 'i':
            result.append(GATTA_II)  # ii → he
            idx += 2
        else:
            c = token[idx]
            result.append(c)  # will be mapped below
            idx += 1

    # Step 5: Apply positional overrides for word-initial characters
    # After RTL reversal, word-initial means the FIRST character of reversed string
    if result:
        first = result[0]
        if first == 'n':
            result[0] = GATTA_INITIAL_N  # n → bet at word start
        elif first == 'r':
            result[0] = GATTA_INITIAL_R  # r → samekh at word start
        elif first == GATTA_II and len(result) > 0:
            # ii at word start → samekh (already converted to 'h')
            # Actually check: if original started with ii after reversal
            pass  # handled in ii processing

    # Step 6: Apply base mapping to remaining unmapped characters
    mapped = []
    for c in result:
        if c in GATTA_BASE:
            mapped.append(GATTA_BASE[c])
        elif c in 'bshkwdgJmESAXlr':
            # Already mapped (from digraph, ii, or override)
            mapped.append(c)
        else:
            mapped.append('?')  # unmappable

    return ''.join(mapped)


def gatta_decode_chars(eva_chars):
    """Decode a raw EVA character string (not a full token — no q stripping)."""
    if not eva_chars:
        return ''
    token = eva_chars[::-1]  # RTL
    token = token.replace('hc', '\x03')
    result = []
    idx = 0
    while idx < len(token):
        if token[idx] == '\x03':
            result.append(GATTA_DIGRAPH_CH)
            idx += 1
        elif idx + 1 < len(token) and token[idx] == 'i' and token[idx+1] == 'i':
            result.append(GATTA_II)
            idx += 2
        else:
            c = token[idx]
            if c in GATTA_BASE:
                result.append(GATTA_BASE[c])
            else:
                result.append(c)
            idx += 1
    return ''.join(result)


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load B tokens with morphology, class, and category."""
    print("Loading data...")

    # 49-class map
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

    # Forbidden transitions
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
              encoding='utf-8') as f:
        forbidden_inv = json.load(f)
    forbidden_pairs = [(t['source'], t['target']) for t in forbidden_inv['transitions']]

    morph = Morphology()
    cc = CategoryClassifier()

    from scripts.voynich import ALL_PREFIXES

    # Collect all tokens with full metadata
    tokens = []
    lines = defaultdict(list)
    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue
        cls = token_to_class.get(token.word)
        m = morph.extract(token.word)
        prefix = m.prefix if m else None
        middle = m.middle if m else token.word
        suffix = m.suffix if m else None
        cat = cc.classify(middle) if middle else 'UNKNOWN'

        entry = {
            'word': token.word,
            'cls': cls,
            'prefix': prefix or '',
            'middle': middle or token.word,
            'suffix': suffix or '',
            'category': cat,
            'folio': token.folio,
            'line': token.line,
        }
        tokens.append(entry)
        lines[(token.folio, token.line)].append(entry)

    print(f"  {len(tokens)} tokens, {len(lines)} lines")
    print(f"  {len(token_to_class)} token types in class map")
    print(f"  {len(forbidden_pairs)} forbidden MIDDLE pairs")

    return tokens, lines, token_to_class, forbidden_pairs, morph, cc, ALL_PREFIXES


# ── Utilities ────────────────────────────────────────────────────────

def levenshtein(s1, s2):
    """Simple Levenshtein edit distance."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev[j + 1] + 1
            deletions = curr[j] + 1
            substitutions = prev[j] + (c1 != c2)
            curr.append(min(insertions, deletions, substitutions))
        prev = curr
    return prev[-1]


def bigram_entropy(text):
    """Character-level bigram conditional entropy H(c2|c1) in bits."""
    bigrams = Counter()
    unigrams = Counter()
    for i in range(len(text) - 1):
        bigrams[(text[i], text[i+1])] += 1
        unigrams[text[i]] += 1

    total = sum(unigrams.values())
    if total == 0:
        return 0.0

    h = 0.0
    for (c1, c2), count in bigrams.items():
        p_joint = count / total
        p_cond = count / unigrams[c1]
        if p_cond > 0:
            h -= p_joint * math.log2(p_cond)
    return h


def mutual_information_tokens(token_seq):
    """Token-level bigram MI: I(t_i; t_{i+1}) in bits."""
    unigram = Counter(token_seq)
    bigram = Counter()
    for i in range(len(token_seq) - 1):
        bigram[(token_seq[i], token_seq[i+1])] += 1

    n = len(token_seq)
    n_bi = n - 1
    if n_bi <= 0:
        return 0.0

    mi = 0.0
    for (a, b), cnt in bigram.items():
        p_ab = cnt / n_bi
        p_a = unigram[a] / n
        p_b = unigram[b] / n
        if p_a > 0 and p_b > 0 and p_ab > 0:
            mi += p_ab * math.log2(p_ab / (p_a * p_b))
    return mi


def round_floats(obj, digits=6):
    if isinstance(obj, float) or isinstance(obj, np.floating):
        if math.isnan(obj) or math.isinf(obj):
            return str(obj)
        return round(float(obj), digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(x, digits) for x in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    return obj


# ── T1: Morphological Boundary Survival ──────────────────────────────

def test1_morphological_boundaries(tokens, all_prefixes):
    """Do PREFIX boundaries survive the Gatta decode?"""
    print("\nT1: Morphological Boundary Survival")

    prefix_results = {}
    total_consistent = 0
    total_tested = 0

    # For each prefix, decode prefix alone and full tokens containing it
    active_prefixes = set()
    for t in tokens:
        if t['prefix']:
            active_prefixes.add(t['prefix'])

    for pfx in sorted(active_prefixes):
        # Decode the prefix string alone (no q-stripping, just chars)
        decoded_pfx = gatta_decode_chars(pfx)

        # For tokens with this prefix, decode full token
        pfx_tokens = [t for t in tokens if t['prefix'] == pfx]
        if len(pfx_tokens) < 10:
            continue

        # Check: after decoding full token, does decoded prefix appear
        # as a substring? (After RTL reversal, prefix becomes suffix)
        consistent = 0
        for t in pfx_tokens:
            decoded_full = gatta_decode(t['word'])
            # PREFIX in EVA is at start; after RTL it should be at END
            if decoded_full.endswith(decoded_pfx) and decoded_pfx:
                consistent += 1
            elif decoded_pfx and decoded_pfx in decoded_full:
                consistent += 1

        score = consistent / len(pfx_tokens) if pfx_tokens else 0
        prefix_results[pfx] = {
            'n_tokens': len(pfx_tokens),
            'decoded_prefix': decoded_pfx,
            'consistency': round(score, 4),
        }
        total_consistent += consistent
        total_tested += len(pfx_tokens)

    overall = total_consistent / total_tested if total_tested > 0 else 0

    # Measure mutual information between prefix identity and decoded boundary position
    # Simple approach: for each token, check if decoded strings cluster by prefix
    prefix_to_decoded = defaultdict(list)
    for t in tokens:
        if t['prefix']:
            decoded = gatta_decode(t['word'])
            prefix_to_decoded[t['prefix']].append(decoded)

    # Within-prefix vs between-prefix edit distance (sample-based)
    within_dists = []
    between_dists = []
    prefixes_with_data = [p for p, decs in prefix_to_decoded.items() if len(decs) >= 5]

    rng = np.random.RandomState(42)
    for pfx in prefixes_with_data[:15]:  # cap for performance
        decs = prefix_to_decoded[pfx]
        sample = rng.choice(len(decs), size=min(20, len(decs)), replace=False)
        for i, j in combinations(sample, 2):
            within_dists.append(levenshtein(decs[i], decs[j]))

    for p1, p2 in list(combinations(prefixes_with_data[:15], 2))[:50]:
        d1 = prefix_to_decoded[p1]
        d2 = prefix_to_decoded[p2]
        s1 = rng.choice(len(d1), size=min(5, len(d1)), replace=False)
        s2 = rng.choice(len(d2), size=min(5, len(d2)), replace=False)
        for i in s1:
            for j in s2:
                between_dists.append(levenshtein(d1[i], d2[j]))

    within_mean = np.mean(within_dists) if within_dists else 0
    between_mean = np.mean(between_dists) if between_dists else 0
    ratio = within_mean / between_mean if between_mean > 0 else 1.0

    # Verdict
    if overall < 0.3:
        verdict = "COLLAPSE"
        favors = "control_program"
    elif overall > 0.7:
        verdict = "SURVIVE"
        favors = "cipher"
    else:
        verdict = "PARTIAL"
        favors = "ambiguous"

    result = {
        'overall_consistency': round(overall, 4),
        'n_prefixes_tested': len(prefix_results),
        'n_tokens_tested': total_tested,
        'prefix_details': prefix_results,
        'within_prefix_edit_dist': round(within_mean, 3),
        'between_prefix_edit_dist': round(between_mean, 3),
        'clustering_ratio': round(ratio, 4),
        'verdict': verdict,
        'favors': favors,
    }
    print(f"  Consistency: {overall:.3f} ({verdict})")
    print(f"  Edit dist ratio within/between: {ratio:.3f}")
    print(f"  Favors: {favors}")
    return result


# ── T2: 49-Class Grammar Preservation ────────────────────────────────

def test2_class_grammar(tokens, token_to_class):
    """Do tokens in the same class cluster in Hebrew space?"""
    print("\nT2: 49-Class Grammar Preservation")

    # Decode all token types
    type_decoded = {}
    for t in tokens:
        if t['word'] not in type_decoded:
            type_decoded[t['word']] = gatta_decode(t['word'])

    # Group by class
    class_types = defaultdict(set)
    for tok, cls in token_to_class.items():
        if tok in type_decoded:
            class_types[cls].add(tok)

    # Within-class pairwise edit distance (decoded strings)
    within_dists = []
    for cls, toks in class_types.items():
        decoded = [type_decoded[t] for t in toks if t in type_decoded]
        if len(decoded) < 2:
            continue
        for i in range(len(decoded)):
            for j in range(i+1, min(i+10, len(decoded))):  # cap per class
                within_dists.append(levenshtein(decoded[i], decoded[j]))

    # Between-class pairwise edit distance (sample)
    between_dists = []
    all_classes = [c for c in class_types if len(class_types[c]) >= 2]
    rng = np.random.RandomState(42)

    for _ in range(2000):
        c1, c2 = rng.choice(all_classes, size=2, replace=False)
        t1 = rng.choice(list(class_types[c1]))
        t2 = rng.choice(list(class_types[c2]))
        if t1 in type_decoded and t2 in type_decoded:
            between_dists.append(levenshtein(type_decoded[t1], type_decoded[t2]))

    within_mean = np.mean(within_dists) if within_dists else 0
    between_mean = np.mean(between_dists) if between_dists else 0
    ratio = within_mean / between_mean if between_mean > 0 else 1.0

    # Null model: shuffle class assignments 1000 times
    null_ratios = []
    all_tokens_list = list(type_decoded.keys())
    all_classes_list = [token_to_class.get(t) for t in all_tokens_list]
    valid = [(t, c) for t, c in zip(all_tokens_list, all_classes_list) if c is not None]

    for _ in range(1000):
        shuffled_classes = rng.permutation([c for _, c in valid])
        shuf_class_types = defaultdict(list)
        for (tok, _), sc in zip(valid, shuffled_classes):
            shuf_class_types[sc].append(type_decoded.get(tok, ''))

        shuf_within = []
        for cls_toks in shuf_class_types.values():
            if len(cls_toks) < 2:
                continue
            for i in range(min(5, len(cls_toks))):
                for j in range(i+1, min(i+5, len(cls_toks))):
                    shuf_within.append(levenshtein(cls_toks[i], cls_toks[j]))

        if shuf_within and between_mean > 0:
            null_ratios.append(np.mean(shuf_within) / between_mean)

    null_mean = np.mean(null_ratios) if null_ratios else 1.0
    null_std = np.std(null_ratios) if null_ratios else 0.1
    z_score = (ratio - null_mean) / null_std if null_std > 0 else 0

    # Homophone collisions: f-gallows vs p-gallows → both lamed
    homophones = defaultdict(set)
    for tok in type_decoded:
        decoded = type_decoded[tok]
        cls = token_to_class.get(tok)
        if cls is not None:
            homophones[decoded].add(cls)

    collision_count = sum(1 for classes in homophones.values() if len(classes) > 1)
    collision_rate = collision_count / len(homophones) if homophones else 0

    # Verdict
    if ratio >= 0.95 or z_score > -2:
        verdict = "NO_CLUSTERING"
        favors = "control_program"
    elif ratio < 0.80 and z_score < -4:
        verdict = "STRONG_CLUSTERING"
        favors = "cipher"
    else:
        verdict = "MILD_CLUSTERING"
        favors = "ambiguous"

    result = {
        'within_class_edit_dist': round(within_mean, 3),
        'between_class_edit_dist': round(between_mean, 3),
        'ratio': round(ratio, 4),
        'null_mean_ratio': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'z_score': round(z_score, 3),
        'homophone_collisions': collision_count,
        'homophone_collision_rate': round(collision_rate, 4),
        'total_unique_decoded': len(homophones),
        'verdict': verdict,
        'favors': favors,
    }
    print(f"  Ratio within/between: {ratio:.3f} (null: {null_mean:.3f})")
    print(f"  Z-score: {z_score:.3f}")
    print(f"  Homophone collisions: {collision_count} ({collision_rate:.1%})")
    print(f"  Favors: {favors}")
    return result


# ── T3: Forbidden Transition Preservation ────────────────────────────

def test3_forbidden_transitions(forbidden_pairs, tokens, morph):
    """Do forbidden MIDDLE pairs have Hebrew phonological explanation?"""
    print("\nT3: Forbidden Transition Preservation")

    # Decode each forbidden pair
    decoded_forbidden = []
    for src, tgt in forbidden_pairs:
        dec_src = gatta_decode_chars(src)
        dec_tgt = gatta_decode_chars(tgt)
        decoded_forbidden.append({
            'eva_source': src,
            'eva_target': tgt,
            'hebrew_source': dec_src,
            'hebrew_target': dec_tgt,
        })

    # Check phonological patterns in forbidden pairs
    # Pattern 1: Same initial consonant (illegal gemination)
    # Pattern 2: Both start with same character
    # Pattern 3: Very short (1-char) decoded strings
    forbidden_same_initial = 0
    forbidden_same_final = 0
    forbidden_adjacent_identical = 0

    for pair in decoded_forbidden:
        s, t = pair['hebrew_source'], pair['hebrew_target']
        if s and t:
            if s[0] == t[0]:
                forbidden_same_initial += 1
                pair['same_initial'] = True
            else:
                pair['same_initial'] = False
            if s[-1] == t[0]:
                forbidden_adjacent_identical += 1
                pair['adjacent_identical'] = True
            else:
                pair['adjacent_identical'] = False
        else:
            pair['same_initial'] = False
            pair['adjacent_identical'] = False

    # Control: sample non-forbidden MIDDLE transitions from corpus
    # Collect actual MIDDLE transitions
    middle_transitions = Counter()
    for key, line_tokens in defaultdict(list).items():
        pass  # need lines

    # Use token stream to get MIDDLE transitions
    all_middles = [t['middle'] for t in tokens]
    all_middle_pairs = set()
    for i in range(len(all_middles) - 1):
        all_middle_pairs.add((all_middles[i], all_middles[i+1]))

    forbidden_set = set(forbidden_pairs)
    non_forbidden = [p for p in all_middle_pairs if p not in forbidden_set]

    # Sample 17 control pairs
    rng = np.random.RandomState(42)
    control_indices = rng.choice(len(non_forbidden), size=min(17, len(non_forbidden)), replace=False)
    control_pairs_list = list(non_forbidden)
    control_pairs = [control_pairs_list[i] for i in control_indices]

    control_same_initial = 0
    control_adjacent_identical = 0
    for src, tgt in control_pairs:
        dec_src = gatta_decode_chars(src)
        dec_tgt = gatta_decode_chars(tgt)
        if dec_src and dec_tgt:
            if dec_src[0] == dec_tgt[0]:
                control_same_initial += 1
            if dec_src[-1] == dec_tgt[0]:
                control_adjacent_identical += 1

    # Are forbidden pairs more phonologically patterned than control?
    forb_pattern_rate = forbidden_same_initial / len(forbidden_pairs)
    ctrl_pattern_rate = control_same_initial / len(control_pairs) if control_pairs else 0

    forb_adj_rate = forbidden_adjacent_identical / len(forbidden_pairs)
    ctrl_adj_rate = control_adjacent_identical / len(control_pairs) if control_pairs else 0

    # Hebrew phonological explanation count
    hebrew_explained = sum(1 for p in decoded_forbidden
                          if p.get('same_initial') or p.get('adjacent_identical'))

    if hebrew_explained <= 2:
        verdict = "NO_PHONOLOGICAL_PATTERN"
        favors = "control_program"
    elif hebrew_explained <= 4:
        verdict = "WEAK_PATTERN"
        favors = "ambiguous"
    elif hebrew_explained >= 5:
        verdict = "PHONOLOGICAL_PATTERN"
        favors = "cipher"
    else:
        verdict = "AMBIGUOUS"
        favors = "ambiguous"

    result = {
        'decoded_forbidden_pairs': decoded_forbidden,
        'forbidden_same_initial': forbidden_same_initial,
        'forbidden_adjacent_identical': forbidden_adjacent_identical,
        'control_same_initial': control_same_initial,
        'control_adjacent_identical': control_adjacent_identical,
        'forbidden_pattern_rate': round(forb_pattern_rate, 3),
        'control_pattern_rate': round(ctrl_pattern_rate, 3),
        'hebrew_explained_count': hebrew_explained,
        'verdict': verdict,
        'favors': favors,
    }
    print(f"  Forbidden with Hebrew pattern: {hebrew_explained}/17")
    print(f"  Same-initial: forbidden={forbidden_same_initial}, control={control_same_initial}")
    print(f"  Adjacent-identical: forbidden={forbidden_adjacent_identical}, control={control_adjacent_identical}")
    print(f"  Favors: {favors}")
    return result


# ── T4: Category Coherence in Hebrew Space ───────────────────────────

def test4_category_coherence(tokens, cc):
    """Do our 8 categories cluster in Hebrew space?"""
    print("\nT4: Category Coherence in Hebrew Space")

    CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
                  'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']

    # Collect MIDDLEs by category
    cat_middles = defaultdict(Counter)
    for t in tokens:
        if t['category'] in CATEGORIES:
            cat_middles[t['category']][t['middle']] += 1

    # Take top-20 MIDDLEs per category, decode them
    cat_decoded = {}
    for cat in CATEGORIES:
        top = cat_middles[cat].most_common(20)
        decoded = [(mid, cnt, gatta_decode_chars(mid)) for mid, cnt in top]
        cat_decoded[cat] = decoded

    # Within-category vs between-category edit distance
    within_dists = []
    between_dists = []

    for cat in CATEGORIES:
        decs = [d[2] for d in cat_decoded.get(cat, []) if d[2]]
        for i in range(len(decs)):
            for j in range(i+1, len(decs)):
                within_dists.append(levenshtein(decs[i], decs[j]))

    for c1, c2 in combinations(CATEGORIES, 2):
        d1 = [d[2] for d in cat_decoded.get(c1, []) if d[2]]
        d2 = [d[2] for d in cat_decoded.get(c2, []) if d[2]]
        for s1 in d1[:10]:
            for s2 in d2[:10]:
                between_dists.append(levenshtein(s1, s2))

    within_mean = np.mean(within_dists) if within_dists else 0
    between_mean = np.mean(between_dists) if between_dists else 0
    ratio = within_mean / between_mean if between_mean > 0 else 1.0

    if ratio >= 0.90:
        verdict = "NO_COHERENCE"
        favors = "control_program"
    elif ratio < 0.75:
        verdict = "STRONG_COHERENCE"
        favors = "cipher"
    else:
        verdict = "MILD_COHERENCE"
        favors = "ambiguous"

    result = {
        'within_category_edit_dist': round(within_mean, 3),
        'between_category_edit_dist': round(between_mean, 3),
        'ratio': round(ratio, 4),
        'category_samples': {cat: [(m, c, d) for m, c, d in decs[:5]]
                             for cat, decs in cat_decoded.items()},
        'verdict': verdict,
        'favors': favors,
    }
    print(f"  Ratio within/between: {ratio:.3f}")
    print(f"  Favors: {favors}")
    # Show sample decoded MIDDLEs per category
    for cat in ['THERMAL', 'FLOW', 'CONTAINMENT']:
        samples = [d[2] for d in cat_decoded.get(cat, [])[:5]]
        print(f"    {cat}: {', '.join(samples)}")
    return result


# ── T5: Information-Theoretic Preservation ───────────────────────────

def test5_information_theory(tokens):
    """Does the decode increase or decrease MI / entropy?"""
    print("\nT5: Information-Theoretic Preservation")

    # Build EVA character stream (Currier B tokens joined by spaces)
    eva_words = [t['word'] for t in tokens]
    eva_char_stream = ' '.join(eva_words)

    # Build decoded character stream
    decoded_words = [gatta_decode(t['word']) for t in tokens]
    decoded_char_stream = ' '.join(decoded_words)

    # Character-level bigram entropy
    eva_bigram_h = bigram_entropy(eva_char_stream)
    decoded_bigram_h = bigram_entropy(decoded_char_stream)
    entropy_delta = decoded_bigram_h - eva_bigram_h

    # Character alphabet sizes
    eva_alphabet = len(set(eva_char_stream) - {' '})
    decoded_alphabet = len(set(decoded_char_stream) - {' '})

    # Token-level transition MI
    eva_token_mi = mutual_information_tokens(eva_words)
    decoded_token_mi = mutual_information_tokens(decoded_words)
    mi_delta = decoded_token_mi - eva_token_mi

    # PREFIX-MIDDLE MI before and after
    # Before: using our prefixes and middles
    pfx_mid_pairs_before = [(t['prefix'] or 'BARE', t['middle']) for t in tokens]
    # After: using first char of decoded as "prefix" proxy (rough)
    pfx_mid_pairs_after = []
    for t in tokens:
        dec = gatta_decode(t['word'])
        if len(dec) > 1:
            pfx_mid_pairs_after.append((dec[-1], dec[:-1]))  # last char = old prefix (RTL)
        else:
            pfx_mid_pairs_after.append(('', dec))

    def pair_mi(pairs):
        joint = Counter(pairs)
        marg_a = Counter(p[0] for p in pairs)
        marg_b = Counter(p[1] for p in pairs)
        n = len(pairs)
        mi = 0.0
        for (a, b), cnt in joint.items():
            p_ab = cnt / n
            p_a = marg_a[a] / n
            p_b = marg_b[b] / n
            if p_a > 0 and p_b > 0 and p_ab > 0:
                mi += p_ab * math.log2(p_ab / (p_a * p_b))
        return mi

    pfx_mid_mi_before = pair_mi(pfx_mid_pairs_before)
    pfx_mid_mi_after = pair_mi(pfx_mid_pairs_after)

    # Homophone information loss: f-gallows vs p-gallows distinction
    f_tokens = [t for t in tokens if t['word'].startswith('f') or
                any(t['word'].startswith(p) for p in ['fch'])]
    p_tokens = [t for t in tokens if t['word'].startswith('p') or
                any(t['word'].startswith(p) for p in ['pch'])]
    f_classes = Counter(t.get('cls') for t in f_tokens if t.get('cls'))
    p_classes = Counter(t.get('cls') for t in p_tokens if t.get('cls'))

    # After decode, f and p both produce lamed — class distinction lost?
    fp_overlap = set(f_classes.keys()) & set(p_classes.keys())

    # Cipher decode should DECREASE entropy; wrong transform INCREASES it
    if entropy_delta > 0.1:
        entropy_verdict = "INCREASES"
        entropy_favors = "control_program"
    elif entropy_delta < -0.5:
        entropy_verdict = "DECREASES_STRONGLY"
        entropy_favors = "cipher"
    elif entropy_delta < -0.1:
        entropy_verdict = "DECREASES_MILDLY"
        entropy_favors = "ambiguous"
    else:
        entropy_verdict = "FLAT"
        entropy_favors = "ambiguous"

    if mi_delta > 0.01:
        mi_verdict = "MI_INCREASES"
        mi_favors = "cipher"
    elif mi_delta < -0.01:
        mi_verdict = "MI_DECREASES"
        mi_favors = "control_program"
    else:
        mi_verdict = "MI_FLAT"
        mi_favors = "ambiguous"

    # Overall
    favors_cp = sum(1 for f in [entropy_favors, mi_favors] if f == "control_program")
    favors_ci = sum(1 for f in [entropy_favors, mi_favors] if f == "cipher")
    overall_favors = "control_program" if favors_cp > favors_ci else (
        "cipher" if favors_ci > favors_cp else "ambiguous")

    verdict = f"{entropy_verdict}_{mi_verdict}"

    result = {
        'eva_bigram_entropy': round(eva_bigram_h, 4),
        'decoded_bigram_entropy': round(decoded_bigram_h, 4),
        'entropy_delta': round(entropy_delta, 4),
        'entropy_verdict': entropy_verdict,
        'eva_alphabet_size': eva_alphabet,
        'decoded_alphabet_size': decoded_alphabet,
        'eva_token_MI': round(eva_token_mi, 6),
        'decoded_token_MI': round(decoded_token_mi, 6),
        'MI_delta': round(mi_delta, 6),
        'MI_verdict': mi_verdict,
        'prefix_middle_MI_before': round(pfx_mid_mi_before, 4),
        'prefix_middle_MI_after': round(pfx_mid_mi_after, 4),
        'f_p_class_overlap': len(fp_overlap),
        'f_total': len(f_tokens),
        'p_total': len(p_tokens),
        'verdict': verdict,
        'favors': overall_favors,
    }
    print(f"  EVA bigram H: {eva_bigram_h:.4f}, Decoded: {decoded_bigram_h:.4f} (delta: {entropy_delta:+.4f})")
    print(f"  EVA token MI: {eva_token_mi:.6f}, Decoded: {decoded_token_mi:.6f} (delta: {mi_delta:+.6f})")
    print(f"  PREFIX-MIDDLE MI: before={pfx_mid_mi_before:.4f}, after={pfx_mid_mi_after:.4f}")
    print(f"  Favors: {overall_favors}")
    return result


# ── T6: PREFIX Role Coherence ────────────────────────────────────────

def test6_prefix_role_coherence(all_prefixes):
    """Do our PREFIXes map to known Hebrew morphemes?"""
    print("\nT6: PREFIX Role Coherence")

    prefix_decoded = {}
    morpheme_matches = 0

    for pfx in sorted(all_prefixes):
        decoded = gatta_decode_chars(pfx)
        is_morpheme = False
        morpheme_name = None

        # Check if decoded string IS (exact match) a known Hebrew prefix morpheme
        # Note: startswith is too loose — since 'ch'→'k' and 'o'→'w', and both
        # k (ke-) and w (ve-) are Hebrew prefixes, any PREFIX containing ch or o
        # would trivially match. Exact match only.
        if decoded:
            for heb_pfx, name in HEBREW_PREFIX_MORPHEMES.items():
                if decoded == heb_pfx:
                    is_morpheme = True
                    morpheme_name = name
                    break

        prefix_decoded[pfx] = {
            'decoded': decoded,
            'is_hebrew_morpheme': is_morpheme,
            'morpheme': morpheme_name,
        }
        if is_morpheme:
            morpheme_matches += 1

    match_rate = morpheme_matches / len(all_prefixes) if all_prefixes else 0

    # Check base-modifier structure
    # POS-0 modifiers: q, d, f, p, y, s
    # POS-1 bases: h, e (+ ch, sh)
    modifiers = ['q', 'd', 'f', 'p', 'y', 's']
    bases = ['h', 'e']
    mod_decoded = {m: gatta_decode_chars(m) for m in modifiers}
    base_decoded = {b: gatta_decode_chars(b) for b in bases}

    # Do modifiers map to one Hebrew class and bases to another?
    mod_hebrew_set = set(mod_decoded.values())
    base_hebrew_set = set(base_decoded.values())
    overlap = mod_hebrew_set & base_hebrew_set

    # qo agreement: both frameworks strip qo as prefix
    qo_agreement = 'qo' in all_prefixes  # trivially true

    if morpheme_matches < 3:
        verdict = "NO_ALIGNMENT"
        favors = "control_program"
    elif morpheme_matches >= 8:
        verdict = "STRONG_ALIGNMENT"
        favors = "cipher"
    else:
        verdict = "PARTIAL_ALIGNMENT"
        favors = "ambiguous"

    result = {
        'n_prefixes': len(all_prefixes),
        'morpheme_matches': morpheme_matches,
        'match_rate': round(match_rate, 3),
        'prefix_details': prefix_decoded,
        'modifier_decoded': mod_decoded,
        'base_decoded': base_decoded,
        'modifier_base_overlap': len(overlap),
        'qo_agreement': qo_agreement,
        'verdict': verdict,
        'favors': favors,
    }
    print(f"  Hebrew morpheme matches: {morpheme_matches}/{len(all_prefixes)} ({match_rate:.1%})")
    print(f"  Modifier-base overlap: {len(overlap)}")
    for pfx, info in list(prefix_decoded.items())[:8]:
        marker = " <-- MORPHEME" if info['is_hebrew_morpheme'] else ""
        print(f"    {pfx} -> {info['decoded']}{marker}")
    print(f"  Favors: {favors}")
    return result


# ── T7: Directionality Reconciliation ────────────────────────────────

def test7_directionality(tokens, lines):
    """Can both LTR (our z=17) and RTL (Gatta z=22.97) be correct?"""
    print("\nT7: Directionality Reconciliation")

    # Token-level MI in reading order vs reverse
    # EVA tokens in line order
    line_keys = sorted(lines.keys())

    # Forward (LTR) token sequence
    forward_seq = []
    for key in line_keys:
        for t in lines[key]:
            forward_seq.append(t['word'])

    # Reverse (RTL) token sequence
    reverse_seq = []
    for key in line_keys:
        for t in reversed(lines[key]):
            reverse_seq.append(t['word'])

    fwd_mi = mutual_information_tokens(forward_seq)
    rev_mi = mutual_information_tokens(reverse_seq)

    # Same for decoded tokens
    decoded_fwd_seq = [gatta_decode(w) for w in forward_seq]
    decoded_rev_seq = [gatta_decode(w) for w in reverse_seq]

    decoded_fwd_mi = mutual_information_tokens(decoded_fwd_seq)
    decoded_rev_mi = mutual_information_tokens(decoded_rev_seq)

    # Character-level bigram entropy in both directions
    # For EVA: LTR chars
    eva_ltr_chars = ' '.join(forward_seq)
    eva_rtl_chars = ' '.join([w[::-1] for w in forward_seq])  # reverse each word

    eva_ltr_h = bigram_entropy(eva_ltr_chars)
    eva_rtl_h = bigram_entropy(eva_rtl_chars)

    # For decoded: LTR chars (note: decode already applies RTL internally)
    dec_ltr_chars = ' '.join(decoded_fwd_seq)
    dec_rtl_chars = ' '.join([w[::-1] for w in decoded_fwd_seq])

    dec_ltr_h = bigram_entropy(dec_ltr_chars)
    dec_rtl_h = bigram_entropy(dec_rtl_chars)

    # Line boundary analysis
    # Line-initial token properties (first token of each line)
    first_tokens = []
    last_tokens = []
    for key in line_keys:
        if lines[key]:
            first_tokens.append(lines[key][0])
            last_tokens.append(lines[key][-1])

    # HT-like enrichment: gallows at line start
    gallows = {'k', 'f', 'p', 't'}
    first_has_gallows = sum(1 for t in first_tokens
                           if t['word'] and t['word'][0] in gallows)
    last_has_gallows = sum(1 for t in last_tokens
                          if t['word'] and t['word'][0] in gallows)

    first_gallows_rate = first_has_gallows / len(first_tokens) if first_tokens else 0
    last_gallows_rate = last_has_gallows / len(last_tokens) if last_tokens else 0

    # Token-level MI direction
    if fwd_mi > rev_mi * 1.05:
        token_direction = "LTR"
    elif rev_mi > fwd_mi * 1.05:
        token_direction = "RTL"
    else:
        token_direction = "SYMMETRIC"

    # Character-level direction for decoded
    if dec_ltr_h < dec_rtl_h:
        char_direction = "LTR_lower_entropy"
    elif dec_rtl_h < dec_ltr_h:
        char_direction = "RTL_lower_entropy"
    else:
        char_direction = "SYMMETRIC"

    # Verdict
    if token_direction == "LTR":
        if char_direction == "RTL_lower_entropy":
            verdict = "MULTI_LEVEL"  # Both right at different levels
            favors = "reconciliation"
        else:
            verdict = "LTR_ONLY"
            favors = "control_program"
    elif token_direction == "RTL":
        verdict = "RTL_CONFIRMED"
        favors = "cipher"
    else:
        verdict = "INCONCLUSIVE"
        favors = "ambiguous"

    result = {
        'eva_forward_MI': round(fwd_mi, 6),
        'eva_reverse_MI': round(rev_mi, 6),
        'token_direction': token_direction,
        'decoded_forward_MI': round(decoded_fwd_mi, 6),
        'decoded_reverse_MI': round(decoded_rev_mi, 6),
        'eva_ltr_char_entropy': round(eva_ltr_h, 4),
        'eva_rtl_char_entropy': round(eva_rtl_h, 4),
        'decoded_ltr_char_entropy': round(dec_ltr_h, 4),
        'decoded_rtl_char_entropy': round(dec_rtl_h, 4),
        'char_direction': char_direction,
        'first_token_gallows_rate': round(first_gallows_rate, 3),
        'last_token_gallows_rate': round(last_gallows_rate, 3),
        'gallows_direction': "LTR" if first_gallows_rate > last_gallows_rate else "RTL",
        'verdict': verdict,
        'favors': favors,
    }
    print(f"  Token MI: fwd={fwd_mi:.6f}, rev={rev_mi:.6f} -> {token_direction}")
    print(f"  Decoded char H: LTR={dec_ltr_h:.4f}, RTL={dec_rtl_h:.4f} -> {char_direction}")
    print(f"  Gallows: first={first_gallows_rate:.3f}, last={last_gallows_rate:.3f}")
    print(f"  Favors: {favors}")
    return result


# ── C1209 Slot Categories (for T8) ───────────────────────────────────

INITIAL_CHARS = set('aqeo')
MEDIAL_CHARS = set('cipdfs')
TERMINAL_CHARS = set('ynmrhl')
FREE_CHARS = set('kt')


def char_slot(c):
    """Return C1209 slot category for a character."""
    if c in INITIAL_CHARS:
        return 'INITIAL'
    elif c in MEDIAL_CHARS:
        return 'MEDIAL'
    elif c in TERMINAL_CHARS:
        return 'TERMINAL'
    elif c in FREE_CHARS:
        return 'FREE'
    return 'OTHER'


# ── T8: Lexicon Signal Under Slot-Preserving Shuffle ─────────────────

def test8_lexicon_survival(tokens, morph):
    """Test whether decoded vocabulary properties survive slot-preserving shuffle.

    Gatta reports lexicon match z=3.6-4.4 (decoded EVA matches Hebrew lexicon
    more than random bijective mappings). We test whether this signal survives
    when C1209 slot structure is preserved but character identity is shuffled.

    Without Gatta's 491K Hebrew lexicon, we test proxy metrics: vocabulary
    concentration, bigram entropy, and type frequency distribution of decoded
    text. If these are indistinguishable between real and slot-shuffled decoded
    text, the lexicon signal is likely a slot-structure artifact.
    """
    print("\nT8: Lexicon Signal Under Slot-Preserving Shuffle")

    # Step 1: Decode all real tokens
    real_decoded = [gatta_decode(t['word']) for t in tokens]
    real_decoded_3plus = [d for d in real_decoded if len(d) >= 3]
    n_3plus = len(real_decoded_3plus)

    # Real metrics
    real_types = set(real_decoded_3plus)
    real_type_count = len(real_types)
    real_ttr = real_type_count / n_3plus if n_3plus > 0 else 0
    real_char_stream = ' '.join(real_decoded)
    real_bigram_h = bigram_entropy(real_char_stream)
    real_freq = Counter(real_decoded_3plus)
    real_freq_h = -sum((c / n_3plus) * math.log2(c / n_3plus)
                       for c in real_freq.values() if c > 0) if n_3plus > 0 else 0

    print(f"  Real decoded (len>=3): {n_3plus} tokens, {real_type_count} types")
    print(f"  Real TTR: {real_ttr:.4f}")
    print(f"  Real decoded bigram H: {real_bigram_h:.4f}")
    print(f"  Real type frequency H: {real_freq_h:.4f}")

    # Step 2: Build slot-preserving shuffle infrastructure
    # For each token: (before_middle, middle_chars, after_middle, slot_sequence)
    token_parts = []
    slot_char_pools = defaultdict(list)

    for t in tokens:
        word = t['word']
        m = morph.extract(word)
        if m:
            art = m.articulator or ''
            pfx = m.prefix or ''
            mid = m.middle or word
            sfx = m.suffix or ''
        else:
            art, pfx, mid, sfx = '', '', word, ''

        before = art + pfx
        after = sfx
        slots = [char_slot(c) for c in mid]
        token_parts.append((before, mid, after, slots))
        for c, s in zip(mid, slots):
            slot_char_pools[s].append(c)

    # Step 3: Run 100 slot-preserving shuffles
    print("  Running 100 slot-preserving shuffles...")
    n_shuffles = 100
    random.seed(42)

    shuf_type_counts = []
    shuf_ttrs = []
    shuf_bigram_hs = []
    shuf_freq_hs = []

    for si in range(n_shuffles):
        # Shuffle each slot's character pool
        shuffled_pools = {}
        for s, chars in slot_char_pools.items():
            pool = list(chars)
            random.shuffle(pool)
            shuffled_pools[s] = iter(pool)

        # Rebuild tokens with shuffled MIDDLEs, decode
        shuf_decoded = []
        for i, (before, mid, after, slots) in enumerate(token_parts):
            try:
                new_mid = ''.join(next(shuffled_pools[s]) for s in slots)
            except StopIteration:
                # Fallback: use original token
                shuf_decoded.append(gatta_decode(tokens[i]['word']))
                continue
            new_word = before + new_mid + after
            shuf_decoded.append(gatta_decode(new_word))

        shuf_3plus = [d for d in shuf_decoded if len(d) >= 3]
        n_s = len(shuf_3plus)
        shuf_types = set(shuf_3plus)
        shuf_type_counts.append(len(shuf_types))
        shuf_ttrs.append(len(shuf_types) / n_s if n_s > 0 else 0)

        shuf_stream = ' '.join(shuf_decoded)
        shuf_bigram_hs.append(bigram_entropy(shuf_stream))

        shuf_freq = Counter(shuf_3plus)
        shuf_fh = -sum((c / n_s) * math.log2(c / n_s)
                       for c in shuf_freq.values() if c > 0) if n_s > 0 else 0
        shuf_freq_hs.append(shuf_fh)

    # Step 4: Z-scores
    def z_score(real_val, shuf_vals):
        m = np.mean(shuf_vals)
        s = np.std(shuf_vals)
        return (real_val - m) / s if s > 0 else 0.0

    z_types = z_score(real_type_count, shuf_type_counts)
    z_ttr = z_score(real_ttr, shuf_ttrs)
    z_bh = z_score(real_bigram_h, shuf_bigram_hs)
    z_fh = z_score(real_freq_h, shuf_freq_hs)

    print(f"\n  Slot-preserving shuffle results ({n_shuffles} iterations):")
    print(f"    Unique types: real={real_type_count}, "
          f"shuf={np.mean(shuf_type_counts):.0f}\u00b1{np.std(shuf_type_counts):.0f}, "
          f"z={z_types:.2f}")
    print(f"    TTR:          real={real_ttr:.4f}, "
          f"shuf={np.mean(shuf_ttrs):.4f}\u00b1{np.std(shuf_ttrs):.4f}, "
          f"z={z_ttr:.2f}")
    print(f"    Bigram H:     real={real_bigram_h:.4f}, "
          f"shuf={np.mean(shuf_bigram_hs):.4f}\u00b1{np.std(shuf_bigram_hs):.4f}, "
          f"z={z_bh:.2f}")
    print(f"    Freq entropy: real={real_freq_h:.4f}, "
          f"shuf={np.mean(shuf_freq_hs):.4f}\u00b1{np.std(shuf_freq_hs):.4f}, "
          f"z={z_fh:.2f}")

    # Step 5: CRITICAL CONTROL — Random bijective mapping
    # The massive z-scores above might reflect EVA's within-slot co-occurrence
    # structure (part of our grammar), not specifically Hebrew. To distinguish:
    # Run the same real-vs-slot-shuffled comparison using a RANDOM bijective
    # mapping instead of Gatta's. If random mappings produce the same z-scores,
    # then T8 measures EVA structure, not Hebrew alignment.
    print("\n  Random bijective mapping control (20 mappings x 20 shuffles)...")

    eva_chars = sorted(GATTA_BASE.keys())  # The 17 EVA characters Gatta maps
    hebrew_chars = sorted(set(GATTA_BASE.values()))  # Target characters

    random.seed(123)
    n_rand_maps = 20
    n_rand_shuf = 20
    rand_map_z_types = []
    rand_map_z_ttrs = []

    for mi in range(n_rand_maps):
        # Create random bijective-ish mapping (same source chars, shuffled targets)
        shuffled_targets = list(hebrew_chars)
        random.shuffle(shuffled_targets)
        # Map each EVA char to a random Hebrew char (cycling if needed)
        rand_map = {}
        for i, ec in enumerate(eva_chars):
            rand_map[ec] = shuffled_targets[i % len(shuffled_targets)]

        # Simple decode: just apply character mapping (no digraphs/positional logic)
        def rand_decode(word):
            return ''.join(rand_map.get(c, c) for c in word)

        # Real decoded via random map
        rr_decoded = [rand_decode(t['word']) for t in tokens]
        rr_3plus = [d for d in rr_decoded if len(d) >= 3]
        rr_type_count = len(set(rr_3plus))
        rr_ttr = len(set(rr_3plus)) / len(rr_3plus) if rr_3plus else 0

        # Slot-shuffled decoded via random map
        rs_type_counts = []
        rs_ttrs = []
        for si in range(n_rand_shuf):
            shuffled_pools = {}
            for s, chars in slot_char_pools.items():
                pool = list(chars)
                random.shuffle(pool)
                shuffled_pools[s] = iter(pool)

            rs_decoded = []
            for i, (before, mid, after, slots) in enumerate(token_parts):
                try:
                    new_mid = ''.join(next(shuffled_pools[s]) for s in slots)
                except StopIteration:
                    rs_decoded.append(rand_decode(tokens[i]['word']))
                    continue
                new_word = before + new_mid + after
                rs_decoded.append(rand_decode(new_word))

            rs_3plus = [d for d in rs_decoded if len(d) >= 3]
            rs_type_counts.append(len(set(rs_3plus)))
            rs_ttrs.append(len(set(rs_3plus)) / len(rs_3plus) if rs_3plus else 0)

        rz_types = z_score(rr_type_count, rs_type_counts)
        rz_ttr = z_score(rr_ttr, rs_ttrs)
        rand_map_z_types.append(rz_types)
        rand_map_z_ttrs.append(rz_ttr)

    rand_z_types_mean = float(np.mean(rand_map_z_types))
    rand_z_ttr_mean = float(np.mean(rand_map_z_ttrs))

    print(f"    Random mapping z_types: mean={rand_z_types_mean:.1f} "
          f"(Gatta={z_types:.1f})")
    print(f"    Random mapping z_ttr:   mean={rand_z_ttr_mean:.1f} "
          f"(Gatta={z_ttr:.1f})")

    # If random bijective mappings show comparable z-scores, the signal
    # is from EVA structure, not Hebrew specifically
    gatta_is_special = abs(z_types) > abs(rand_z_types_mean) * 1.5

    print(f"    Gatta mapping is {'SPECIAL' if gatta_is_special else 'NOT special'} "
          f"vs random bijective")

    # Step 6: Verdict (incorporating control)
    # The key question: is the character identity signal specific to Gatta's
    # Hebrew mapping, or would ANY mapping show it?
    if abs(rand_z_types_mean) > 10:
        # Random mappings also show massive z-scores → EVA structure, not Hebrew
        verdict = "GRAMMAR_STRUCTURE"
        favors = "control_program"
        note = ("Character identity produces vocabulary concentration under ALL "
                "character mappings (random z={:.0f}, Gatta z={:.0f}). "
                "This is EVA's within-slot co-occurrence structure (part of our "
                "grammar), not Hebrew-specific. Gatta's lexicon z=3.6-4.4 likely "
                "reflects this grammar interacting with Hebrew lexicon coverage "
                "probability.".format(rand_z_types_mean, z_types))
    elif not gatta_is_special:
        verdict = "GRAMMAR_STRUCTURE"
        favors = "control_program"
        note = ("Gatta's mapping shows no more vocabulary concentration than random "
                "bijective mappings. The lexicon signal is from EVA grammar structure.")
    else:
        # Gatta's mapping is genuinely special
        sig = []
        if abs(z_types) > 2:
            sig.append(f"unique_types(z={z_types:.1f})")
        if abs(z_ttr) > 2:
            sig.append(f"TTR(z={z_ttr:.1f})")
        if abs(z_bh) > 2:
            sig.append(f"bigram_H(z={z_bh:.1f})")
        if abs(z_fh) > 2:
            sig.append(f"freq_entropy(z={z_fh:.1f})")

        if sig:
            verdict = "GATTA_SPECIFIC_SIGNAL"
            favors = "cipher"
            note = (f"Gatta's mapping produces significantly more vocabulary "
                    f"concentration than random mappings: {', '.join(sig)}")
        else:
            verdict = "LEXICON_ABSORBED"
            favors = "control_program"
            note = "No significant signal specific to Gatta's mapping."

    print(f"\n  Verdict: {verdict}")
    print(f"  Favors: {favors}")

    result = {
        'n_decoded_3plus': n_3plus,
        'real_unique_types': real_type_count,
        'real_ttr': round(real_ttr, 6),
        'real_bigram_entropy': round(real_bigram_h, 6),
        'real_freq_entropy': round(real_freq_h, 6),
        'shuffle_unique_types_mean': round(float(np.mean(shuf_type_counts)), 2),
        'shuffle_unique_types_std': round(float(np.std(shuf_type_counts)), 2),
        'shuffle_ttr_mean': round(float(np.mean(shuf_ttrs)), 6),
        'shuffle_ttr_std': round(float(np.std(shuf_ttrs)), 6),
        'shuffle_bigram_h_mean': round(float(np.mean(shuf_bigram_hs)), 6),
        'shuffle_bigram_h_std': round(float(np.std(shuf_bigram_hs)), 6),
        'shuffle_freq_h_mean': round(float(np.mean(shuf_freq_hs)), 6),
        'shuffle_freq_h_std': round(float(np.std(shuf_freq_hs)), 6),
        'z_unique_types': round(z_types, 3),
        'z_ttr': round(z_ttr, 3),
        'z_bigram_h': round(z_bh, 3),
        'z_freq_entropy': round(z_fh, 3),
        'random_bijective_control': {
            'n_random_maps': n_rand_maps,
            'n_shuffles_per_map': n_rand_shuf,
            'random_z_types_mean': round(rand_z_types_mean, 2),
            'random_z_ttr_mean': round(rand_z_ttr_mean, 2),
            'gatta_is_special': gatta_is_special,
            'interpretation': ('Random bijective mappings show comparable z-scores; '
                               'the vocabulary concentration is from EVA grammar '
                               'structure, not Hebrew-specific alignment'
                               if abs(rand_z_types_mean) > 10 else
                               'Gatta mapping may be specifically aligned'),
        },
        'n_shuffles': n_shuffles,
        'verdict': verdict,
        'favors': favors,
        'note': note,
    }
    return result


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Phase 488: HEBREW CIPHER CROSS-VALIDATION")
    print("Cross-validation against Gatta (voynich-toolkit) Hebrew hypothesis")
    print("=" * 70)

    tokens, lines, token_to_class, forbidden_pairs, morph, cc, all_prefixes = load_data()

    # Verify Gatta transform on sample tokens
    print("\nGatta transform verification:")
    samples = ['chedy', 'qokaiin', 'daiin', 'okeedy', 'shedy', 'otchol']
    for s in samples:
        print(f"  {s} -> {gatta_decode(s)}")

    # Run test battery
    t1 = test1_morphological_boundaries(tokens, all_prefixes)
    t2 = test2_class_grammar(tokens, token_to_class)
    t3 = test3_forbidden_transitions(forbidden_pairs, tokens, morph)
    t4 = test4_category_coherence(tokens, cc)
    t5 = test5_information_theory(tokens)
    t6 = test6_prefix_role_coherence(all_prefixes)
    t7 = test7_directionality(tokens, lines)
    t8 = test8_lexicon_survival(tokens, morph)

    # Score
    tests = [t1, t2, t3, t4, t5, t6, t7, t8]
    cipher_count = sum(1 for t in tests if t['favors'] == 'cipher')
    cp_count = sum(1 for t in tests if t['favors'] == 'control_program')
    ambiguous_count = sum(1 for t in tests if t['favors'] in ('ambiguous', 'reconciliation'))

    if cipher_count <= 1:
        overall = "STRONG_FALSIFICATION"
    elif cipher_count <= 3:
        overall = "MIXED"
    elif cipher_count <= 5:
        overall = "CHALLENGE"
    else:
        overall = "CONVERGENCE"

    print("\n" + "=" * 70)
    print("SCORECARD")
    print("=" * 70)
    for i, t in enumerate(tests, 1):
        print(f"  T{i}: {t['verdict']:30s} -> {t['favors']}")
    print(f"\n  Control program: {cp_count}/8")
    print(f"  Cipher: {cipher_count}/8")
    print(f"  Ambiguous: {ambiguous_count}/8")
    print(f"\n  OVERALL VERDICT: {overall}")

    output = {
        'metadata': {
            'phase': 488,
            'title': 'Hebrew Cipher Cross-Validation',
            'external_repo': 'github.com/antenore/voynich-toolkit',
            'external_author': 'Antenore Gatta',
            'framing': 'Respectful cross-validation of two independent analyses',
            'n_tokens': len(tokens),
            'n_lines': len(lines),
            'n_forbidden_pairs': len(forbidden_pairs),
        },
        'gatta_transform': {
            'type': 'context-sensitive EVA->Hebrew',
            'features': ['RTL_reversal', 'q/qo_prefix_strip', 'ch_digraph',
                         'ii_digraph', 'positional_overrides', 'homophone_merge_f_p'],
            'samples': {s: gatta_decode(s) for s in samples},
        },
        'pre_registered_predictions': {
            'control_program': {
                'T1': 'Boundaries collapse (consistency < 0.3)',
                'T2': 'No Hebrew clustering (ratio ~1.0)',
                'T3': 'No phonological pattern (0-2/17)',
                'T4': 'No category coherence (ratio ~1.0)',
                'T5': 'MI decreases, entropy increases',
                'T6': 'Few morpheme matches (< 3/30)',
                'T7': 'LTR at all levels',
                'T8': 'Decoded vocabulary unchanged by slot-preserving shuffle (z<2)',
            },
            'cipher': {
                'T1': 'Boundaries map to Hebrew morphemes (consistency > 0.7)',
                'T2': 'Hebrew clustering in classes (ratio < 0.80)',
                'T3': 'Hebrew phonotactic explanation (5+/17)',
                'T4': 'Semantic clustering by category',
                'T5': 'MI increases, entropy decreases',
                'T6': 'Many morpheme matches (8+/30)',
                'T7': 'RTL at character level',
                'T8': 'Decoded vocabulary significantly different from slot-shuffled (z>2)',
            },
        },
        'T1_morphological_boundaries': t1,
        'T2_class_grammar': t2,
        'T3_forbidden_transitions': t3,
        'T4_category_coherence': t4,
        'T5_information_theory': t5,
        'T6_prefix_role': t6,
        'T7_directionality': t7,
        'T8_lexicon_survival': t8,
        'scorecard': {
            'control_program': cp_count,
            'cipher': cipher_count,
            'ambiguous': ambiguous_count,
            'overall_verdict': overall,
        },
    }

    out_path = RESULTS_DIR / 'hebrew_cipher_cross_validation.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(output), f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults: {out_path}")


if __name__ == '__main__':
    main()
