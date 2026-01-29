#!/usr/bin/env python3
"""
FQ_CLOSER_BOUNDARY_HAZARD - Script 2: Source Token Discrimination

Determines what distinguishes forbidden sources (dy, l) from non-forbidden
sources (y, am, s, r, d) within Class 23. Tests successor/predecessor
profiles, contextual neighborhoods, and morphological/identity properties.

Sections:
  1. Frequency and successor profile
  2. Predecessor profile
  3. Contextual neighborhood comparison (JSD, folio, section)
  4. Morphological and identity analysis

Constraint references:
  C597: Class 23 boundary dominance
  C593: FQ 3-group structure (BARE morphology)
  C627: 3 unexplained forbidden pairs from FQ_CLOSER
"""

import json
import sys
import math
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

# ============================================================
# CONSTANTS
# ============================================================
CLASS_23_TOKENS = {'dy', 'y', 'am', 's', 'r', 'l', 'd'}
FORBIDDEN_SOURCES = {'dy', 'l'}
NONFORBIDDEN_SOURCES = {'y', 'am', 's', 'r', 'd'}
HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}
EN_CHSH_CLASSES = {8, 31}

RESULTS_PATH = PROJECT_ROOT / 'phases' / 'FQ_CLOSER_BOUNDARY_HAZARD' / 'results' / 'fq_closer_source_discrimination.json'


# ============================================================
# LOAD DATA
# ============================================================
def load_class_token_map():
    path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_b_lines():
    """Build per-line token sequences with folio/section metadata."""
    tx = Transcript()
    lines = defaultdict(list)
    folio_section = {}
    for token in tx.currier_b():
        key = (token.folio, token.line)
        lines[key].append(token.word)
        if token.folio not in folio_section:
            folio_section[token.folio] = token.section
    return lines, folio_section


def build_folio_map():
    """Map each token occurrence to its folio."""
    tx = Transcript()
    token_folios = defaultdict(list)
    for token in tx.currier_b():
        token_folios[token.word].append(token.folio)
    return token_folios


# ============================================================
# SECTION 1: FREQUENCY AND SUCCESSOR PROFILE
# ============================================================
def section1_successor_profile(lines, token_to_class):
    print("=" * 70)
    print("SECTION 1: FREQUENCY AND SUCCESSOR PROFILE")
    print("=" * 70)
    print()

    # Pre-compute successors for each Class 23 token
    token_freq = Counter()
    successor_classes = defaultdict(lambda: Counter())
    successor_tokens = defaultdict(lambda: Counter())

    for key in sorted(lines.keys()):
        words = lines[key]
        for i, w in enumerate(words):
            if w in CLASS_23_TOKENS:
                token_freq[w] += 1
                if i < len(words) - 1:
                    succ = words[i + 1]
                    succ_cls = token_to_class.get(succ)
                    if succ_cls is not None:
                        successor_classes[w][succ_cls] += 1
                    successor_tokens[w][succ] += 1

    results = {}

    print(f"  {'Token':<6} {'Freq':>5} {'Succ':>5} {'Div':>4} {'Entropy':>7} {'Haz%':>6} {'EN_CHSH%':>8} {'c9%':>5} {'Forb?'}")
    print(f"  {'-'*6} {'-'*5} {'-'*5} {'-'*4} {'-'*7} {'-'*6} {'-'*8} {'-'*5} {'-'*5}")

    for tok in sorted(CLASS_23_TOKENS, key=lambda t: -token_freq[t]):
        sc = successor_classes[tok]
        total_succ = sum(sc.values())
        if total_succ == 0:
            continue

        diversity = len(sc)
        # Shannon entropy
        probs = [c / total_succ for c in sc.values()]
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)

        hazard_count = sum(sc.get(c, 0) for c in HAZARD_CLASSES)
        hazard_rate = hazard_count / total_succ

        en_chsh_count = sum(sc.get(c, 0) for c in EN_CHSH_CLASSES)
        en_chsh_rate = en_chsh_count / total_succ

        c9_count = sc.get(9, 0)
        c9_rate = c9_count / total_succ

        is_forb = tok in FORBIDDEN_SOURCES
        flag = 'YES' if is_forb else 'no'

        print(f"  {tok:<6} {token_freq[tok]:>5} {total_succ:>5} {diversity:>4} {entropy:>7.3f} "
              f"{hazard_rate*100:>5.1f}% {en_chsh_rate*100:>7.1f}% {c9_rate*100:>4.1f}% {flag}")

        results[tok] = {
            'frequency': token_freq[tok],
            'total_successors': total_succ,
            'diversity': diversity,
            'entropy': round(entropy, 4),
            'hazard_rate': round(hazard_rate, 4),
            'en_chsh_rate': round(en_chsh_rate, 4),
            'c9_rate': round(c9_rate, 4),
            'is_forbidden_source': is_forb,
            'top_5_successor_classes': dict(sc.most_common(5)),
        }

    # Compare forbidden vs non-forbidden
    print("\n  Forbidden vs Non-Forbidden Source Comparison:")
    forb_haz = [results[t]['hazard_rate'] for t in FORBIDDEN_SOURCES if t in results]
    nonf_haz = [results[t]['hazard_rate'] for t in NONFORBIDDEN_SOURCES if t in results]
    forb_en = [results[t]['en_chsh_rate'] for t in FORBIDDEN_SOURCES if t in results]
    nonf_en = [results[t]['en_chsh_rate'] for t in NONFORBIDDEN_SOURCES if t in results]
    forb_c9 = [results[t]['c9_rate'] for t in FORBIDDEN_SOURCES if t in results]
    nonf_c9 = [results[t]['c9_rate'] for t in NONFORBIDDEN_SOURCES if t in results]

    if forb_haz and nonf_haz:
        print(f"  Hazard rate: forbidden={sum(forb_haz)/len(forb_haz):.3f}, non-forbidden={sum(nonf_haz)/len(nonf_haz):.3f}")
        print(f"  EN_CHSH rate: forbidden={sum(forb_en)/len(forb_en):.3f}, non-forbidden={sum(nonf_en)/len(nonf_en):.3f}")
        print(f"  c9 rate: forbidden={sum(forb_c9)/len(forb_c9):.3f}, non-forbidden={sum(nonf_c9)/len(nonf_c9):.3f}")

    return results


# ============================================================
# SECTION 2: PREDECESSOR PROFILE
# ============================================================
def section2_predecessor_profile(lines, token_to_class):
    print()
    print("=" * 70)
    print("SECTION 2: PREDECESSOR PROFILE")
    print("=" * 70)
    print()

    predecessor_classes = defaultdict(lambda: Counter())

    for key in sorted(lines.keys()):
        words = lines[key]
        for i, w in enumerate(words):
            if w in CLASS_23_TOKENS and i > 0:
                pred = words[i - 1]
                pred_cls = token_to_class.get(pred)
                if pred_cls is not None:
                    predecessor_classes[w][pred_cls] += 1

    results = {}

    print(f"  {'Token':<6} {'Pred':>5} {'Div':>4} {'Entropy':>7} {'Haz%':>6} {'EN_CHSH%':>8} {'Forb?'}")
    print(f"  {'-'*6} {'-'*5} {'-'*4} {'-'*7} {'-'*6} {'-'*8} {'-'*5}")

    for tok in sorted(CLASS_23_TOKENS, key=lambda t: -sum(predecessor_classes[t].values())):
        pc = predecessor_classes[tok]
        total_pred = sum(pc.values())
        if total_pred == 0:
            continue

        diversity = len(pc)
        probs = [c / total_pred for c in pc.values()]
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)

        hazard_count = sum(pc.get(c, 0) for c in HAZARD_CLASSES)
        hazard_rate = hazard_count / total_pred

        en_chsh_count = sum(pc.get(c, 0) for c in EN_CHSH_CLASSES)
        en_chsh_rate = en_chsh_count / total_pred

        is_forb = tok in FORBIDDEN_SOURCES
        flag = 'YES' if is_forb else 'no'

        print(f"  {tok:<6} {total_pred:>5} {diversity:>4} {entropy:>7.3f} {hazard_rate*100:>5.1f}% "
              f"{en_chsh_rate*100:>7.1f}% {flag}")

        results[tok] = {
            'total_predecessors': total_pred,
            'diversity': diversity,
            'entropy': round(entropy, 4),
            'hazard_rate': round(hazard_rate, 4),
            'en_chsh_rate': round(en_chsh_rate, 4),
            'is_forbidden_source': is_forb,
            'top_5_predecessor_classes': dict(pc.most_common(5)),
        }

    # Compare
    print("\n  Forbidden vs Non-Forbidden Predecessor Comparison:")
    forb_haz = [results[t]['hazard_rate'] for t in FORBIDDEN_SOURCES if t in results]
    nonf_haz = [results[t]['hazard_rate'] for t in NONFORBIDDEN_SOURCES if t in results]
    forb_en = [results[t]['en_chsh_rate'] for t in FORBIDDEN_SOURCES if t in results]
    nonf_en = [results[t]['en_chsh_rate'] for t in NONFORBIDDEN_SOURCES if t in results]

    if forb_haz and nonf_haz:
        print(f"  Hazard predecessor rate: forbidden={sum(forb_haz)/len(forb_haz):.3f}, non-forbidden={sum(nonf_haz)/len(nonf_haz):.3f}")
        print(f"  EN_CHSH predecessor rate: forbidden={sum(forb_en)/len(forb_en):.3f}, non-forbidden={sum(nonf_en)/len(nonf_en):.3f}")

    return results


# ============================================================
# SECTION 3: CONTEXTUAL NEIGHBORHOOD COMPARISON
# ============================================================
def section3_contextual_neighborhood(lines, token_to_class, folio_section, token_folios):
    print()
    print("=" * 70)
    print("SECTION 3: CONTEXTUAL NEIGHBORHOOD COMPARISON")
    print("=" * 70)
    print()

    # 2-token left and right context class distributions
    left2_context = defaultdict(lambda: Counter())
    right2_context = defaultdict(lambda: Counter())

    for key in sorted(lines.keys()):
        words = lines[key]
        for i, w in enumerate(words):
            if w in CLASS_23_TOKENS:
                # Left context (up to 2 tokens)
                for offset in [1, 2]:
                    if i - offset >= 0:
                        pred = words[i - offset]
                        pred_cls = token_to_class.get(pred)
                        if pred_cls is not None:
                            left2_context[w][(f'L{offset}', pred_cls)] += 1
                # Right context (up to 2 tokens)
                for offset in [1, 2]:
                    if i + offset < len(words):
                        succ = words[i + offset]
                        succ_cls = token_to_class.get(succ)
                        if succ_cls is not None:
                            right2_context[w][(f'R{offset}', succ_cls)] += 1

    # Jensen-Shannon divergence between forbidden and non-forbidden contexts
    # Aggregate left+right context distributions
    forb_context = Counter()
    nonf_context = Counter()
    for tok in FORBIDDEN_SOURCES:
        forb_context.update(left2_context[tok])
        forb_context.update(right2_context[tok])
    for tok in NONFORBIDDEN_SOURCES:
        nonf_context.update(left2_context[tok])
        nonf_context.update(right2_context[tok])

    all_keys = set(forb_context.keys()) | set(nonf_context.keys())
    total_f = sum(forb_context.values())
    total_n = sum(nonf_context.values())

    if total_f > 0 and total_n > 0:
        p = {k: forb_context[k] / total_f for k in all_keys}
        q = {k: nonf_context[k] / total_n for k in all_keys}
        m = {k: (p.get(k, 0) + q.get(k, 0)) / 2.0 for k in all_keys}
        jsd = 0.5 * sum(p.get(k, 0) * math.log2(p[k] / m[k]) for k in all_keys if p.get(k, 0) > 0 and m[k] > 0) + \
              0.5 * sum(q.get(k, 0) * math.log2(q[k] / m[k]) for k in all_keys if q.get(k, 0) > 0 and m[k] > 0)
        print(f"  Jensen-Shannon divergence (forbidden vs non-forbidden context): {jsd:.6f}")
        print(f"  (Low = similar contexts; high = distinct contexts)")
    else:
        jsd = None
        print("  Insufficient context data for JSD")

    # Folio distribution
    print(f"\n  Folio distribution:")
    token_folio_sets = {}
    for tok in sorted(CLASS_23_TOKENS, key=lambda t: -len(token_folios.get(t, []))):
        folios = set(token_folios.get(tok, []))
        token_folio_sets[tok] = folios
        is_forb = tok in FORBIDDEN_SOURCES
        flag = 'YES' if is_forb else 'no'
        print(f"    {tok:<6} {len(folios):>3} folios   Forb={flag}")

    # Folio overlap: forbidden vs non-forbidden
    forb_folios = set()
    for tok in FORBIDDEN_SOURCES:
        forb_folios |= token_folio_sets.get(tok, set())
    nonf_folios = set()
    for tok in NONFORBIDDEN_SOURCES:
        nonf_folios |= token_folio_sets.get(tok, set())
    overlap = forb_folios & nonf_folios
    print(f"\n  Forbidden sources in {len(forb_folios)} folios, non-forbidden in {len(nonf_folios)} folios")
    print(f"  Overlap: {len(overlap)} folios ({len(overlap)/max(1,len(forb_folios|nonf_folios))*100:.1f}%)")

    # Section distribution
    print(f"\n  Section distribution:")
    section_counts = defaultdict(lambda: Counter())
    for tok in CLASS_23_TOKENS:
        for folio in token_folios.get(tok, []):
            sec = folio_section.get(folio, 'UNKNOWN')
            section_counts[tok][sec] += 1

    all_sections = set()
    for tok in CLASS_23_TOKENS:
        all_sections |= set(section_counts[tok].keys())

    for sec in sorted(all_sections):
        forb_rate = sum(section_counts[t].get(sec, 0) for t in FORBIDDEN_SOURCES) / max(1, sum(sum(section_counts[t].values()) for t in FORBIDDEN_SOURCES))
        nonf_rate = sum(section_counts[t].get(sec, 0) for t in NONFORBIDDEN_SOURCES) / max(1, sum(sum(section_counts[t].values()) for t in NONFORBIDDEN_SOURCES))
        print(f"    {sec:<15} forb={forb_rate*100:>5.1f}%  nonf={nonf_rate*100:>5.1f}%")

    results = {
        'jsd': round(jsd, 6) if jsd is not None else None,
        'folio_overlap': {
            'forbidden_folios': len(forb_folios),
            'nonforbidden_folios': len(nonf_folios),
            'overlap': len(overlap),
            'overlap_rate': round(len(overlap) / max(1, len(forb_folios | nonf_folios)), 4),
        },
        'folio_counts': {tok: len(token_folio_sets.get(tok, set())) for tok in CLASS_23_TOKENS},
    }
    return results


# ============================================================
# SECTION 4: MORPHOLOGICAL AND IDENTITY ANALYSIS
# ============================================================
def section4_morphological_identity(token_to_class):
    print()
    print("=" * 70)
    print("SECTION 4: MORPHOLOGICAL AND IDENTITY ANALYSIS")
    print("=" * 70)
    print()

    morph = Morphology()
    results = {}

    # Single-character kernel primitives (C085)
    KERNEL_PRIMITIVES = {'s', 'r', 'l', 'd', 'y', 'k', 'h', 'e', 'o', 'a'}

    # Check Currier A presence
    tx = Transcript()
    currier_a_tokens = Counter()
    azc_tokens = Counter()
    for token in tx.currier_a():
        currier_a_tokens[token.word] += 1
    for token in tx.azc():
        azc_tokens[token.word] += 1

    print(f"  {'Token':<6} {'Len':>3} {'Middle':<6} {'Prefix':<6} {'Suffix':<6} {'Artic':<6} {'Kernel?':<7} {'CurrA':>5} {'AZC':>5} {'Forb?'}")
    print(f"  {'-'*6} {'-'*3} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*7} {'-'*5} {'-'*5} {'-'*5}")

    for tok in sorted(CLASS_23_TOKENS, key=lambda t: t):
        m = morph.extract(tok)
        is_kernel = tok in KERNEL_PRIMITIVES
        in_a = currier_a_tokens.get(tok, 0)
        in_azc = azc_tokens.get(tok, 0)
        is_forb = tok in FORBIDDEN_SOURCES
        flag = 'YES' if is_forb else 'no'

        prefix = m.prefix if m.prefix else '-'
        middle = m.middle if m.middle else '-'
        suffix = m.suffix if m.suffix else '-'
        artic = m.articulator if m.articulator else '-'

        print(f"  {tok:<6} {len(tok):>3} {middle:<6} {prefix:<6} {suffix:<6} {artic:<6} "
              f"{'YES' if is_kernel else 'no':<7} {in_a:>5} {in_azc:>5} {flag}")

        results[tok] = {
            'length': len(tok),
            'middle': m.middle,
            'prefix': m.prefix,
            'suffix': m.suffix,
            'articulator': m.articulator,
            'is_kernel_primitive': is_kernel,
            'currier_a_count': in_a,
            'azc_count': in_azc,
            'is_forbidden_source': is_forb,
        }

    # Summary
    print("\n  Forbidden vs Non-Forbidden Identity Properties:")
    forb_tokens = [results[t] for t in FORBIDDEN_SOURCES if t in results]
    nonf_tokens = [results[t] for t in NONFORBIDDEN_SOURCES if t in results]

    forb_kernel = sum(1 for t in forb_tokens if t['is_kernel_primitive'])
    nonf_kernel = sum(1 for t in nonf_tokens if t['is_kernel_primitive'])
    print(f"  Kernel primitives: forbidden={forb_kernel}/{len(forb_tokens)}, non-forbidden={nonf_kernel}/{len(nonf_tokens)}")

    forb_len = [t['length'] for t in forb_tokens]
    nonf_len = [t['length'] for t in nonf_tokens]
    print(f"  Mean length: forbidden={sum(forb_len)/len(forb_len):.1f}, non-forbidden={sum(nonf_len)/len(nonf_len):.1f}")

    forb_a = sum(t['currier_a_count'] for t in forb_tokens)
    nonf_a = sum(t['currier_a_count'] for t in nonf_tokens)
    print(f"  Currier A total: forbidden={forb_a}, non-forbidden={nonf_a}")

    return results


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 70)
    print("FQ_CLOSER_BOUNDARY_HAZARD: SOURCE TOKEN DISCRIMINATION")
    print("=" * 70)
    print()
    print("Loading data...")

    ctm = load_class_token_map()
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    lines, folio_section = build_b_lines()
    token_folios = build_folio_map()
    print(f"  Lines: {len(lines)}, Tokens: {sum(len(v) for v in lines.values())}")
    print()

    s1 = section1_successor_profile(lines, token_to_class)
    s2 = section2_predecessor_profile(lines, token_to_class)
    s3 = section3_contextual_neighborhood(lines, token_to_class, folio_section, token_folios)
    s4 = section4_morphological_identity(token_to_class)

    output = {
        'metadata': {
            'phase': 'FQ_CLOSER_BOUNDARY_HAZARD',
            'script': 'fq_closer_source_discrimination',
            'timestamp': datetime.now().isoformat(),
        },
        'section1_successor_profile': s1,
        'section2_predecessor_profile': s2,
        'section3_contextual_neighborhood': s3,
        'section4_morphological_identity': s4,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == '__main__':
    main()
