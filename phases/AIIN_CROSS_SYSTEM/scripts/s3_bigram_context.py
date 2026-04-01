#!/usr/bin/env python3
"""
s3_bigram_context.py — Full predecessor/successor bigram context analysis for
aiin-family tokens across all systems (A, B, AZC).

Phase: AIIN_CROSS_SYSTEM
Purpose: Test cross-system scope of known B-side bigram patterns:
  - or→aiin directional bigram (C561: 87.5% in B)
  - daiin→CHSH lane routing (C600/C817: 90.8%)
  - aiin→ain wind-down chain (C1244: 64.9%)

METHODOLOGICAL NOTE: Currier A is NON_SEQUENTIAL (C240). Bigrams in A
represent co-occurrence on the same line, NOT grammatical transitions.
Analysis and interpretation split accordingly.

Uses: scripts/voynich.py canonical library
"""

import sys
import io
import os
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

# Windows stdout encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ensure repo root on path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
os.chdir(REPO_ROOT)
sys.path.insert(0, str(REPO_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

RESULTS_DIR = REPO_ROOT / 'phases' / 'AIIN_CROSS_SYSTEM' / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATA LOADING — work with raw token list for positional info
# ============================================================

def load_filtered_tokens():
    """Load H-track, non-label, non-empty, non-uncertain tokens with position info."""
    import csv
    tokens = []
    path = REPO_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue
            word = row.get('word', '').strip().strip('"')
            if not word or '*' in word:
                continue
            placement = row.get('placement', '').strip().strip('"')
            if placement.startswith('L'):
                continue
            folio = row.get('folio', '').strip().strip('"')
            line = row.get('line_number', '').strip().strip('"')
            language = row.get('language', '').strip().strip('"')
            # line_initial is position from start (1-indexed)
            try:
                pos = int(row.get('line_initial', '0').strip().strip('"'))
            except ValueError:
                pos = 0
            tokens.append({
                'word': word,
                'folio': folio,
                'line': line,
                'language': language,
                'pos': pos,
            })
    # Sort by folio, line, position
    tokens.sort(key=lambda t: (t['folio'], t['line'], t['pos']))
    return tokens


def split_by_system(tokens):
    """Split tokens into A, B, AZC."""
    a, b, azc = [], [], []
    for t in tokens:
        if t['language'] == 'A':
            a.append(t)
        elif t['language'] == 'B':
            b.append(t)
        elif t['language'] == 'NA':
            azc.append(t)
    return a, b, azc


def group_by_line(tokens):
    """Group tokens by (folio, line), preserving position order."""
    lines = defaultdict(list)
    for t in tokens:
        lines[(t['folio'], t['line'])].append(t)
    # Ensure each line is sorted by position
    for key in lines:
        lines[key].sort(key=lambda t: t['pos'])
    return lines


def get_prefix(word):
    """Extract morphological prefix of a word."""
    m = morph.extract(word)
    return m.prefix


# ============================================================
# BIGRAM EXTRACTION
# ============================================================

def extract_bigrams(line_groups):
    """Extract predecessor/successor pairs from line-grouped tokens.
    Returns list of (predecessor_word, current_word, successor_word) triples.
    predecessor/successor = None if at line boundary."""
    triples = []
    for key, line_tokens in line_groups.items():
        for i, tok in enumerate(line_tokens):
            pred = line_tokens[i - 1]['word'] if i > 0 else None
            succ = line_tokens[i + 1]['word'] if i < len(line_tokens) - 1 else None
            triples.append((pred, tok['word'], succ))
    return triples


def get_predecessors(triples, target_word):
    """Get predecessor words for a target word."""
    preds = []
    for pred, word, succ in triples:
        if word == target_word and pred is not None:
            preds.append(pred)
    return preds


def get_successors(triples, target_word):
    """Get successor words for a target word."""
    succs = []
    for pred, word, succ in triples:
        if word == target_word and succ is not None:
            succs.append(succ)
    return succs


# ============================================================
# CONDITIONAL ENTROPY
# ============================================================

def entropy(word_list):
    """Shannon entropy of a word distribution (in bits)."""
    if not word_list:
        return 0.0
    c = Counter(word_list)
    total = sum(c.values())
    h = 0.0
    for count in c.values():
        p = count / total
        if p > 0:
            h -= p * math.log2(p)
    return h


def baseline_successor_entropy(triples, sample_size=500):
    """Compute average successor entropy for random tokens as baseline."""
    import random
    random.seed(42)
    # Collect all successor lists per word type
    succ_by_word = defaultdict(list)
    for pred, word, succ in triples:
        if succ is not None:
            succ_by_word[word].append(succ)
    # Sample word types that have enough successors
    eligible = [w for w, s in succ_by_word.items() if len(s) >= 3]
    if len(eligible) > sample_size:
        sampled = random.sample(eligible, sample_size)
    else:
        sampled = eligible
    entropies = [entropy(succ_by_word[w]) for w in sampled]
    return sum(entropies) / len(entropies) if entropies else 0.0


# ============================================================
# CO-OCCURRENCE ANALYSIS (for A system — non-sequential)
# ============================================================

def line_cooccurrence(line_groups, target_word, top_n=20):
    """Words that appear on the same line as target_word (excluding target itself)."""
    cowords = Counter()
    for key, line_tokens in line_groups.items():
        words_in_line = [t['word'] for t in line_tokens]
        if target_word in words_in_line:
            for w in words_in_line:
                if w != target_word:
                    cowords[w] += 1
    return cowords.most_common(top_n)


def jaccard_similarity(set1, set2):
    """Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union)


# ============================================================
# WIND-DOWN CHAIN ANALYSIS (C1244)
# ============================================================

def wind_down_analysis(line_groups):
    """Analyze aiin→ain wind-down patterns."""
    lines_with_aiin = 0
    lines_with_both = 0
    aiin_before_ain = 0
    three_step = 0  # aiin→ain→am

    for key, line_tokens in line_groups.items():
        words = [t['word'] for t in line_tokens]
        has_aiin = 'aiin' in words
        has_ain = 'ain' in words

        if has_aiin:
            lines_with_aiin += 1
            if has_ain:
                lines_with_both += 1
                # Check ordering: does aiin precede ain?
                aiin_pos = [i for i, w in enumerate(words) if w == 'aiin']
                ain_pos = [i for i, w in enumerate(words) if w == 'ain']
                if min(aiin_pos) < max(ain_pos):
                    aiin_before_ain += 1

        # Three-step: aiin...ain...am on same line
        has_am = 'am' in words
        if has_aiin and has_ain and has_am:
            aiin_p = min(i for i, w in enumerate(words) if w == 'aiin')
            ain_p = min(i for i, w in enumerate(words) if w == 'ain')
            am_p = min(i for i, w in enumerate(words) if w == 'am')
            if aiin_p < ain_p < am_p:
                three_step += 1

    return {
        'lines_with_aiin': lines_with_aiin,
        'lines_with_both_aiin_ain': lines_with_both,
        'pct_aiin_lines_also_ain': round(100.0 * lines_with_both / lines_with_aiin, 1) if lines_with_aiin else 0,
        'aiin_before_ain': aiin_before_ain,
        'pct_aiin_before_ain': round(100.0 * aiin_before_ain / lines_with_both, 1) if lines_with_both else 0,
        'three_step_aiin_ain_am': three_step,
    }


def paragraph_position_analysis(line_groups, all_line_groups_all_tokens):
    """Check if lines with aiin→ain co-occurrence tend to be later in paragraph.
    Use line number as proxy for position within folio."""
    both_lines = []
    aiin_only_lines = []
    for key, line_tokens in line_groups.items():
        words = [t['word'] for t in line_tokens]
        has_aiin = 'aiin' in words
        has_ain = 'ain' in words
        try:
            line_num = int(key[1])
        except ValueError:
            continue
        if has_aiin and has_ain:
            both_lines.append(line_num)
        elif has_aiin:
            aiin_only_lines.append(line_num)

    avg_both = sum(both_lines) / len(both_lines) if both_lines else 0
    avg_aiin_only = sum(aiin_only_lines) / len(aiin_only_lines) if aiin_only_lines else 0
    return {
        'avg_line_num_aiin_and_ain': round(avg_both, 2),
        'avg_line_num_aiin_only': round(avg_aiin_only, 2),
        'n_both': len(both_lines),
        'n_aiin_only': len(aiin_only_lines),
        'later_in_folio': avg_both > avg_aiin_only if both_lines and aiin_only_lines else None,
    }


# ============================================================
# MAIN ANALYSIS
# ============================================================

def main():
    print("=" * 70)
    print("S3: BIGRAM CONTEXT ANALYSIS — aiin-family across A, B, AZC")
    print("=" * 70)

    tokens = load_filtered_tokens()
    tok_a, tok_b, tok_azc = split_by_system(tokens)
    print(f"\nToken counts: A={len(tok_a)}, B={len(tok_b)}, AZC={len(tok_azc)}")

    lines_a = group_by_line(tok_a)
    lines_b = group_by_line(tok_b)
    lines_azc = group_by_line(tok_azc)

    triples_a = extract_bigrams(lines_a)
    triples_b = extract_bigrams(lines_b)
    triples_azc = extract_bigrams(lines_azc)

    results = {}

    # ----------------------------------------------------------
    # 1. KNOWN ANCHORS (B-side validation)
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("1. KNOWN ANCHORS — B-side validation")
    print("=" * 70)

    # or→aiin directionality
    or_succs_b = get_successors(triples_b, 'or')
    or_total_b = len(or_succs_b)
    or_to_aiin_b = sum(1 for s in or_succs_b if s == 'aiin')
    or_to_aiin_pct = round(100.0 * or_to_aiin_b / or_total_b, 1) if or_total_b else 0
    print(f"\nor→aiin in B: {or_to_aiin_b}/{or_total_b} = {or_to_aiin_pct}% (C561 target: 87.5%)")

    # daiin→CHSH lane
    daiin_succs_b = get_successors(triples_b, 'daiin')
    daiin_total_b = len(daiin_succs_b)
    chsh_count = 0
    for s in daiin_succs_b:
        pfx = get_prefix(s)
        if pfx in ('ch', 'sh'):
            chsh_count += 1
    chsh_pct = round(100.0 * chsh_count / daiin_total_b, 1) if daiin_total_b else 0
    print(f"daiin→CHSH in B: {chsh_count}/{daiin_total_b} = {chsh_pct}% (C817 target: 90.8%)")

    results['anchors_b'] = {
        'or_to_aiin_pct': or_to_aiin_pct,
        'or_to_aiin_count': or_to_aiin_b,
        'or_successor_total': or_total_b,
        'daiin_to_chsh_pct': chsh_pct,
        'daiin_to_chsh_count': chsh_count,
        'daiin_successor_total': daiin_total_b,
    }

    # ----------------------------------------------------------
    # 2. PREDECESSOR ANALYSIS
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("2. PREDECESSOR ANALYSIS — what comes before aiin/daiin")
    print("=" * 70)

    results['predecessors'] = {}
    for sys_name, triples, line_groups in [('A', triples_a, lines_a),
                                            ('B', triples_b, lines_b),
                                            ('AZC', triples_azc, lines_azc)]:
        print(f"\n--- {sys_name} ---")
        preds_aiin = get_predecessors(triples, 'aiin')
        preds_daiin = get_predecessors(triples, 'daiin')

        print(f"  aiin predecessors (n={len(preds_aiin)}):")
        for w, c in Counter(preds_aiin).most_common(15):
            print(f"    {w:15s} {c:4d}  ({100*c/len(preds_aiin):5.1f}%)")

        print(f"  daiin predecessors (n={len(preds_daiin)}):")
        for w, c in Counter(preds_daiin).most_common(15):
            print(f"    {w:15s} {c:4d}  ({100*c/len(preds_daiin):5.1f}%)")

        # or→aiin directionality
        or_pred_count = sum(1 for p in preds_aiin if p == 'or')
        or_pred_pct = round(100.0 * or_pred_count / len(preds_aiin), 1) if preds_aiin else 0

        # What % of or tokens are followed by aiin?
        or_succs = get_successors(triples, 'or')
        or_to_aiin = sum(1 for s in or_succs if s == 'aiin')
        or_to_aiin_pct2 = round(100.0 * or_to_aiin / len(or_succs), 1) if or_succs else 0

        print(f"\n  or→aiin directionality in {sys_name}:")
        print(f"    % of aiin preceded by or: {or_pred_pct}% ({or_pred_count}/{len(preds_aiin)})")
        print(f"    % of or followed by aiin: {or_to_aiin_pct2}% ({or_to_aiin}/{len(or_succs)})")

        results['predecessors'][sys_name] = {
            'aiin_top15': Counter(preds_aiin).most_common(15),
            'daiin_top15': Counter(preds_daiin).most_common(15),
            'aiin_total_with_pred': len(preds_aiin),
            'daiin_total_with_pred': len(preds_daiin),
            'or_precedes_aiin_pct': or_pred_pct,
            'or_followed_by_aiin_pct': or_to_aiin_pct2,
            'or_to_aiin_count': or_to_aiin,
            'or_total_successors': len(or_succs),
        }

    # ----------------------------------------------------------
    # 3. SUCCESSOR ANALYSIS
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("3. SUCCESSOR ANALYSIS — what comes after aiin/daiin")
    print("=" * 70)

    results['successors'] = {}
    for sys_name, triples, line_groups in [('A', triples_a, lines_a),
                                            ('B', triples_b, lines_b),
                                            ('AZC', triples_azc, lines_azc)]:
        print(f"\n--- {sys_name} ---")
        succs_aiin = get_successors(triples, 'aiin')
        succs_daiin = get_successors(triples, 'daiin')

        print(f"  aiin successors (n={len(succs_aiin)}):")
        for w, c in Counter(succs_aiin).most_common(15):
            print(f"    {w:15s} {c:4d}  ({100*c/len(succs_aiin):5.1f}%)")

        print(f"  daiin successors (n={len(succs_daiin)}):")
        for w, c in Counter(succs_daiin).most_common(15):
            print(f"    {w:15s} {c:4d}  ({100*c/len(succs_daiin):5.1f}%)")

        # PREFIX of successor for daiin
        daiin_succ_prefixes = Counter()
        for s in succs_daiin:
            pfx = get_prefix(s)
            daiin_succ_prefixes[pfx if pfx else '(none)'] += 1
        chsh_ct = daiin_succ_prefixes.get('ch', 0) + daiin_succ_prefixes.get('sh', 0)
        chsh_p = round(100.0 * chsh_ct / len(succs_daiin), 1) if succs_daiin else 0

        print(f"\n  daiin successor PREFIX distribution in {sys_name}:")
        for pfx, ct in daiin_succ_prefixes.most_common(10):
            print(f"    {str(pfx):10s} {ct:4d}  ({100*ct/len(succs_daiin):5.1f}%)")
        print(f"    CHSH lane total: {chsh_ct}/{len(succs_daiin)} = {chsh_p}%")

        # PREFIX of successor for aiin
        aiin_succ_prefixes = Counter()
        for s in succs_aiin:
            pfx = get_prefix(s)
            aiin_succ_prefixes[pfx if pfx else '(none)'] += 1
        aiin_chsh = aiin_succ_prefixes.get('ch', 0) + aiin_succ_prefixes.get('sh', 0)
        aiin_chsh_p = round(100.0 * aiin_chsh / len(succs_aiin), 1) if succs_aiin else 0

        print(f"\n  aiin successor PREFIX distribution in {sys_name}:")
        for pfx, ct in aiin_succ_prefixes.most_common(10):
            print(f"    {str(pfx):10s} {ct:4d}  ({100*ct/len(succs_aiin):5.1f}%)")
        print(f"    CHSH lane total: {aiin_chsh}/{len(succs_aiin)} = {aiin_chsh_p}%")

        results['successors'][sys_name] = {
            'aiin_top15': Counter(succs_aiin).most_common(15),
            'daiin_top15': Counter(succs_daiin).most_common(15),
            'aiin_total_with_succ': len(succs_aiin),
            'daiin_total_with_succ': len(succs_daiin),
            'daiin_succ_chsh_pct': chsh_p,
            'daiin_succ_chsh_count': chsh_ct,
            'daiin_succ_prefix_dist': daiin_succ_prefixes.most_common(10),
            'aiin_succ_chsh_pct': aiin_chsh_p,
            'aiin_succ_chsh_count': aiin_chsh,
            'aiin_succ_prefix_dist': aiin_succ_prefixes.most_common(10),
        }

    # ----------------------------------------------------------
    # 4. CONDITIONAL ENTROPY
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("4. CONDITIONAL ENTROPY — successor predictability")
    print("=" * 70)

    results['entropy'] = {}
    for sys_name, triples in [('A', triples_a), ('B', triples_b), ('AZC', triples_azc)]:
        succs_aiin = get_successors(triples, 'aiin')
        succs_daiin = get_successors(triples, 'daiin')
        h_aiin = entropy(succs_aiin)
        h_daiin = entropy(succs_daiin)
        h_baseline = baseline_successor_entropy(triples)

        print(f"\n--- {sys_name} ---")
        print(f"  H(next | aiin)   = {h_aiin:.3f} bits  (n={len(succs_aiin)})")
        print(f"  H(next | daiin)  = {h_daiin:.3f} bits  (n={len(succs_daiin)})")
        print(f"  H(next | random) = {h_baseline:.3f} bits  (baseline, avg over 500 word types)")
        if h_baseline > 0:
            print(f"  aiin constraint ratio:  {h_aiin/h_baseline:.3f}  (1.0 = no constraint)")
            print(f"  daiin constraint ratio: {h_daiin/h_baseline:.3f}")

        results['entropy'][sys_name] = {
            'h_aiin': round(h_aiin, 4),
            'h_daiin': round(h_daiin, 4),
            'h_baseline': round(h_baseline, 4),
            'n_aiin': len(succs_aiin),
            'n_daiin': len(succs_daiin),
            'aiin_constraint_ratio': round(h_aiin / h_baseline, 4) if h_baseline > 0 else None,
            'daiin_constraint_ratio': round(h_daiin / h_baseline, 4) if h_baseline > 0 else None,
        }

    # ----------------------------------------------------------
    # 5. A-SYSTEM CO-OCCURRENCE (non-sequential)
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("5. A-SYSTEM CO-OCCURRENCE (non-sequential, C240)")
    print("=" * 70)

    cooc_daiin_a = line_cooccurrence(lines_a, 'daiin', top_n=20)
    cooc_aiin_a = line_cooccurrence(lines_a, 'aiin', top_n=20)

    print(f"\n  Words on same line as daiin in A (top 20):")
    for w, c in cooc_daiin_a:
        print(f"    {w:15s} {c:4d}")

    print(f"\n  Words on same line as aiin in A (top 20):")
    for w, c in cooc_aiin_a:
        print(f"    {w:15s} {c:4d}")

    daiin_set = set(w for w, _ in cooc_daiin_a)
    aiin_set = set(w for w, _ in cooc_aiin_a)
    jacc = jaccard_similarity(daiin_set, aiin_set)
    print(f"\n  Jaccard similarity (top-20 sets): {jacc:.3f}")
    print(f"  Intersection: {daiin_set & aiin_set}")
    print(f"  daiin-only: {daiin_set - aiin_set}")
    print(f"  aiin-only: {aiin_set - daiin_set}")

    results['a_cooccurrence'] = {
        'daiin_top20': cooc_daiin_a,
        'aiin_top20': cooc_aiin_a,
        'jaccard_top20': round(jacc, 4),
        'intersection': sorted(daiin_set & aiin_set),
        'daiin_only': sorted(daiin_set - aiin_set),
        'aiin_only': sorted(aiin_set - daiin_set),
    }

    # ----------------------------------------------------------
    # 6. CROSS-SYSTEM SCOPE OF or→aiin
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("6. CROSS-SYSTEM SCOPE OF or->aiin")
    print("=" * 70)

    results['or_aiin_cross'] = {}
    for sys_name, triples in [('A', triples_a), ('B', triples_b), ('AZC', triples_azc)]:
        preds_aiin = get_predecessors(triples, 'aiin')
        or_succs = get_successors(triples, 'or')
        or_count_as_pred = sum(1 for p in preds_aiin if p == 'or')
        or_to_aiin_ct = sum(1 for s in or_succs if s == 'aiin')

        aiin_or_pct = round(100.0 * or_count_as_pred / len(preds_aiin), 1) if preds_aiin else 0
        or_aiin_pct = round(100.0 * or_to_aiin_ct / len(or_succs), 1) if or_succs else 0

        # Dominant predecessor for aiin
        pred_counter = Counter(preds_aiin)
        top_pred = pred_counter.most_common(1)[0] if pred_counter else ('(none)', 0)

        print(f"\n  {sys_name}:")
        print(f"    aiin tokens with predecessor: {len(preds_aiin)}")
        print(f"    or as predecessor of aiin: {or_count_as_pred} ({aiin_or_pct}%)")
        print(f"    or tokens with successor: {len(or_succs)}")
        print(f"    or→aiin: {or_to_aiin_ct} ({or_aiin_pct}%)")
        print(f"    Dominant predecessor: {top_pred[0]} ({top_pred[1]}x)")

        results['or_aiin_cross'][sys_name] = {
            'aiin_preceded_by_or_pct': aiin_or_pct,
            'aiin_preceded_by_or_count': or_count_as_pred,
            'or_followed_by_aiin_pct': or_aiin_pct,
            'or_followed_by_aiin_count': or_to_aiin_ct,
            'dominant_predecessor': top_pred[0],
            'dominant_predecessor_count': top_pred[1],
            'aiin_total_with_pred': len(preds_aiin),
            'or_total_with_succ': len(or_succs),
        }

    # ----------------------------------------------------------
    # 7. WIND-DOWN CHAIN (C1244): aiin→ain→am
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("7. WIND-DOWN CHAIN — aiin->ain->am (C1244)")
    print("=" * 70)

    results['wind_down'] = {}
    for sys_name, line_groups in [('B', lines_b), ('A', lines_a)]:
        wd = wind_down_analysis(line_groups)
        pp = paragraph_position_analysis(line_groups, line_groups)

        print(f"\n--- {sys_name} ---")
        print(f"  Lines with aiin: {wd['lines_with_aiin']}")
        print(f"  Lines with both aiin+ain: {wd['lines_with_both_aiin_ain']} "
              f"({wd['pct_aiin_lines_also_ain']}%)")
        print(f"  aiin precedes ain: {wd['aiin_before_ain']} "
              f"({wd['pct_aiin_before_ain']}% of co-occurring lines)")
        print(f"  Three-step aiin→ain→am: {wd['three_step_aiin_ain_am']}")
        print(f"\n  Paragraph position proxy (line number):")
        print(f"    Avg line# for aiin+ain lines: {pp['avg_line_num_aiin_and_ain']}")
        print(f"    Avg line# for aiin-only lines: {pp['avg_line_num_aiin_only']}")
        print(f"    aiin+ain later in folio? {pp['later_in_folio']}")

        results['wind_down'][sys_name] = {**wd, 'paragraph_position': pp}

    # ----------------------------------------------------------
    # SAVE
    # ----------------------------------------------------------
    out_path = RESULTS_DIR / 's3_bigram_context.json'
    # Convert Counter items (tuples) to serializable format
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(i) for i in obj]
        elif isinstance(obj, tuple):
            return list(obj)
        elif isinstance(obj, set):
            return sorted(obj)
        return obj

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(results), f, indent=2, ensure_ascii=False)

    print(f"\n\nResults saved to {out_path}")
    print("DONE.")


if __name__ == '__main__':
    main()
