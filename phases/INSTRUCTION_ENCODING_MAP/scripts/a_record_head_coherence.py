"""
A Record HEAD Domain Coherence Test
====================================

Within multi-token Currier A registry entries, do tokens share the same
HEAD domain or mix domains?

Background:
- Currier A lines are independent records (C233)
- Records are 1-token control operators (0.6%) or 2+ token registry entries (99.4%)
- MIDDLEs follow HEAD + MOD* + TERM encoding (C1393/C1394)
- HEAD atoms: {a, e, o, k, t} set operational domains
- HEAD domain categories: k=THERMAL, t=FLOW, a=FLOW/TRANSITION,
  e=OPERATION/THERMAL, o=STAGING
- ~45% of A-exclusive MIDDLEs are headless

Tests:
  1. Basic HEAD coherence within records (same HEAD fraction)
  2. Dominant HEAD fraction (>50% of tokens)
  3. HEAD entropy within vs between records
  4. Permutation test (1000 shuffles)
  5. Record length vs coherence
  6. Section-specific coherence (H, P, T)
  7. TERMINAL atom coherence
  8. Comparison with B lines
  9. Preferred HEAD combinations in mixed records
  10. Domain-level coherence (grouping HEADs by domain)
"""

import sys
import os
import io
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# --- Configuration ------------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Atom classifications per C1393 / C1394
HEAD_ONLY = {'a', 'o'}
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE = {'k', 't'}
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}
EXTENSIBLE = {'e', 'i'}
HEAD_SET = HEAD_ONLY | FREE | {'e'}  # a, e, o, k, t

# Domain mapping for HEAD atoms (from C1388, C1384, C1386, etc.)
HEAD_DOMAIN = {
    'k': 'THERMAL',
    'e': 'THERMAL/OPERATION',
    'o': 'STAGING',
    'a': 'FLOW/TRANSITION',
    't': 'FLOW',
}

N_PERMUTATIONS = 1000

# --- Atom Decomposition -------------------------------------------

def atomize(middle):
    """Split a MIDDLE string into individual atoms.

    Respects:
    - e and i extensibility (ee, eee, ii kept as single units)
    - dy hard-fused as single TERM atom
    """
    atoms = []
    i = 0
    while i < len(middle):
        ch = middle[i]
        # Check for hard-fused dy
        if ch == 'd' and i + 1 < len(middle) and middle[i + 1] == 'y':
            atoms.append('dy')
            i += 2
            continue
        # Collect runs of extensible atoms
        if ch in EXTENSIBLE:
            run = ch
            while i + 1 < len(middle) and middle[i + 1] == ch:
                run += ch
                i += 1
            atoms.append(run)
        else:
            atoms.append(ch)
        i += 1
    return atoms


def get_head(middle):
    """Extract HEAD atom from a MIDDLE string.

    Returns: (head_atom, head_base_char) or (None, None) for headless.
    head_base_char is the single character (e.g., 'e' for 'ee').
    """
    if not middle:
        return None, None

    atoms = atomize(middle)
    if not atoms:
        return None, None

    first = atoms[0]
    first_base = first[0]  # Handle 'ee', 'eee' etc.

    if first_base in HEAD_SET:
        return first, first_base
    else:
        return None, None


def get_terminal(middle):
    """Extract TERMINAL atom from a MIDDLE string.

    Returns: (term_atom, term_base_char) or (None, None).
    """
    if not middle:
        return None, None

    atoms = atomize(middle)
    if len(atoms) < 2:
        # Single atom: it's both HEAD and itself, no separate TERM
        return None, None

    last = atoms[-1]
    last_base = last[0]

    # dy is already fused as a single atom
    if last == 'dy':
        return 'dy', 'dy'

    if last_base in TERM_ONLY or last_base in FREE:
        return last, last_base
    else:
        return None, None


# --- Data Loading -------------------------------------------------

def load_a_records():
    """Load Currier A records: group tokens by folio + line.

    Returns list of dicts with:
      folio, line, section, tokens (list of words), middles (list),
      heads (list of head_base or 'NONE'), terminals (list of term_base or 'NONE')
    """
    tx = Transcript()
    morph = Morphology()

    # Group tokens by folio + line
    lines = defaultdict(list)
    sections = {}

    for tok in tx.currier_a():
        if '*' in tok.word or not tok.word.strip():
            continue
        key = (tok.folio, tok.line)
        m = morph.extract(tok.word)
        mid = m.middle if m.middle else ''
        lines[key].append({
            'word': tok.word,
            'middle': mid,
            'prefix': m.prefix or '',
            'suffix': m.suffix or '',
        })
        # Determine section from folio
        if tok.folio not in sections:
            sections[tok.folio] = tok.section if hasattr(tok, 'section') else None

    records = []
    for (folio, line), tokens in lines.items():
        if len(tokens) < 2:
            continue  # Skip single-token control operators

        heads = []
        terminals = []
        middles = []
        for t in tokens:
            mid = t['middle']
            middles.append(mid)
            _, head_base = get_head(mid)
            heads.append(head_base if head_base else 'NONE')
            _, term_base = get_terminal(mid)
            terminals.append(term_base if term_base else 'NONE')

        records.append({
            'folio': folio,
            'line': line,
            'section': sections.get(folio, 'UNK'),
            'tokens': [t['word'] for t in tokens],
            'middles': middles,
            'heads': heads,
            'terminals': terminals,
            'n_tokens': len(tokens),
        })

    return records


def load_b_lines():
    """Load Currier B lines for comparison."""
    tx = Transcript()
    morph = Morphology()

    lines = defaultdict(list)
    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue
        key = (tok.folio, tok.line)
        m = morph.extract(tok.word)
        mid = m.middle if m.middle else ''
        lines[key].append(mid)

    b_lines = []
    for (folio, line), middles in lines.items():
        if len(middles) < 2:
            continue
        heads = []
        for mid in middles:
            _, head_base = get_head(mid)
            heads.append(head_base if head_base else 'NONE')
        b_lines.append({
            'folio': folio,
            'line': line,
            'heads': heads,
            'n_tokens': len(middles),
        })

    return b_lines


# --- Analysis Functions -------------------------------------------

def compute_coherence(heads_list):
    """Compute HEAD coherence for a single record.

    Returns dict with:
      - all_same: bool, all tokens have same HEAD
      - dominant_frac: fraction of most common HEAD
      - n_distinct: number of distinct HEADs
      - entropy: Shannon entropy of HEAD distribution
      - most_common: the most common HEAD
    """
    if not heads_list:
        return None

    counts = Counter(heads_list)
    n = len(heads_list)

    most_common_head, most_common_count = counts.most_common(1)[0]

    # Entropy
    entropy = 0.0
    for c in counts.values():
        p = c / n
        if p > 0:
            entropy -= p * math.log2(p)

    return {
        'all_same': len(counts) == 1,
        'dominant_frac': most_common_count / n,
        'n_distinct': len(counts),
        'entropy': entropy,
        'most_common': most_common_head,
    }


def compute_mean_entropy(records, key='heads'):
    """Mean within-record HEAD entropy."""
    entropies = []
    for rec in records:
        coh = compute_coherence(rec[key])
        if coh:
            entropies.append(coh['entropy'])
    return np.mean(entropies), np.std(entropies)


def between_record_entropy(records, key='heads'):
    """Entropy of HEAD distribution across entire corpus (pooled)."""
    all_heads = []
    for rec in records:
        all_heads.extend(rec[key])
    counts = Counter(all_heads)
    n = len(all_heads)
    entropy = 0.0
    for c in counts.values():
        p = c / n
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def permutation_test(records, n_perms=N_PERMUTATIONS, key='heads'):
    """Permutation test: shuffle HEADs across records, measure mean within-record entropy.

    If records are coherent, real entropy should be LOWER than shuffled.
    """
    real_mean, _ = compute_mean_entropy(records, key)

    # Pool all heads
    all_heads = []
    record_sizes = []
    for rec in records:
        all_heads.extend(rec[key])
        record_sizes.append(len(rec[key]))

    perm_means = []
    for _ in range(n_perms):
        shuffled = all_heads.copy()
        random.shuffle(shuffled)

        # Reconstruct records with shuffled heads
        idx = 0
        perm_entropies = []
        for size in record_sizes:
            chunk = shuffled[idx:idx + size]
            idx += size
            coh = compute_coherence(chunk)
            if coh:
                perm_entropies.append(coh['entropy'])
        perm_means.append(np.mean(perm_entropies))

    perm_means = np.array(perm_means)
    p_value = np.mean(perm_means <= real_mean)  # fraction of perms at or below real
    z_score = (real_mean - np.mean(perm_means)) / (np.std(perm_means) + 1e-10)

    return {
        'real_mean_entropy': round(real_mean, 4),
        'perm_mean_entropy': round(float(np.mean(perm_means)), 4),
        'perm_std': round(float(np.std(perm_means)), 4),
        'z_score': round(z_score, 4),
        'p_value': round(p_value, 4),
        'n_permutations': n_perms,
        'coherent': real_mean < float(np.mean(perm_means)),
        'entropy_reduction_pct': round(100 * (1 - real_mean / float(np.mean(perm_means))), 2)
            if float(np.mean(perm_means)) > 0 else 0.0,
    }


def head_combination_analysis(records):
    """For records with mixed HEADs, find preferred combinations."""
    pair_counts = Counter()
    pair_records = Counter()

    for rec in records:
        unique_heads = set(rec['heads'])
        if len(unique_heads) < 2:
            continue
        # Count pairs
        sorted_heads = sorted(unique_heads)
        for i, h1 in enumerate(sorted_heads):
            for h2 in sorted_heads[i+1:]:
                pair_counts[(h1, h2)] += 1
                pair_records[(h1, h2)] += 1

    # Convert to list of dicts
    combos = []
    for (h1, h2), count in pair_counts.most_common(20):
        d1 = HEAD_DOMAIN.get(h1, 'HEADLESS') if h1 != 'NONE' else 'HEADLESS'
        d2 = HEAD_DOMAIN.get(h2, 'HEADLESS') if h2 != 'NONE' else 'HEADLESS'
        combos.append({
            'head1': h1, 'head2': h2,
            'domain1': d1, 'domain2': d2,
            'records': count,
            'same_domain': d1 == d2,
        })

    return combos


def positional_head_analysis(records):
    """Check if HEAD varies by position within record.

    First token, last token, middle tokens.
    """
    first_heads = Counter()
    last_heads = Counter()
    interior_heads = Counter()

    for rec in records:
        heads = rec['heads']
        first_heads[heads[0]] += 1
        last_heads[heads[-1]] += 1
        for h in heads[1:-1]:
            interior_heads[h] += 1

    return {
        'first_token': dict(first_heads.most_common()),
        'last_token': dict(last_heads.most_common()),
        'interior_tokens': dict(interior_heads.most_common()),
    }


# --- Main ---------------------------------------------------------

def main():
    random.seed(42)
    np.random.seed(42)

    print("Loading Currier A records...")
    records = load_a_records()
    print(f"  {len(records)} multi-token records loaded")

    print("Loading Currier B lines for comparison...")
    b_lines = load_b_lines()
    print(f"  {len(b_lines)} B lines loaded")

    results = {}

    # ---- T0: Basic census ----
    print("\n=== T0: Basic Census ===")
    all_heads = []
    for rec in records:
        all_heads.extend(rec['heads'])
    head_dist = Counter(all_heads)
    n_total = len(all_heads)

    print(f"  Total tokens in records: {n_total}")
    print(f"  HEAD distribution:")
    for h, c in head_dist.most_common():
        domain = HEAD_DOMAIN.get(h, 'HEADLESS') if h != 'NONE' else 'HEADLESS'
        print(f"    {h:>6}: {c:>5} ({100*c/n_total:.1f}%) [{domain}]")

    # Record length distribution
    lengths = [rec['n_tokens'] for rec in records]
    len_dist = Counter(lengths)

    results['census'] = {
        'n_records': len(records),
        'n_tokens_total': n_total,
        'mean_record_length': round(np.mean(lengths), 2),
        'median_record_length': int(np.median(lengths)),
        'head_distribution': {h: c for h, c in head_dist.most_common()},
        'head_fractions': {h: round(c / n_total, 4) for h, c in head_dist.most_common()},
        'record_length_distribution': {str(k): v for k, v in sorted(len_dist.items())},
    }

    # ---- T1: Basic HEAD coherence ----
    print("\n=== T1: HEAD Coherence Within Records ===")

    all_same_count = 0
    dominant_count = 0
    dominant_fracs = []
    n_distinct_list = []

    for rec in records:
        coh = compute_coherence(rec['heads'])
        if coh['all_same']:
            all_same_count += 1
        if coh['dominant_frac'] > 0.5:
            dominant_count += 1
        dominant_fracs.append(coh['dominant_frac'])
        n_distinct_list.append(coh['n_distinct'])

    print(f"  Records with ALL tokens same HEAD: {all_same_count}/{len(records)} "
          f"({100*all_same_count/len(records):.1f}%)")
    print(f"  Records with dominant HEAD (>50%):  {dominant_count}/{len(records)} "
          f"({100*dominant_count/len(records):.1f}%)")
    print(f"  Mean dominant HEAD fraction: {np.mean(dominant_fracs):.3f}")
    print(f"  Mean distinct HEADs per record: {np.mean(n_distinct_list):.2f}")

    results['t1_basic_coherence'] = {
        'all_same_count': all_same_count,
        'all_same_fraction': round(all_same_count / len(records), 4),
        'dominant_count': dominant_count,
        'dominant_fraction': round(dominant_count / len(records), 4),
        'mean_dominant_frac': round(float(np.mean(dominant_fracs)), 4),
        'median_dominant_frac': round(float(np.median(dominant_fracs)), 4),
        'mean_n_distinct': round(float(np.mean(n_distinct_list)), 3),
    }

    # ---- T2: Entropy comparison (within vs between) ----
    print("\n=== T2: Within vs Between Record Entropy ===")

    within_mean, within_std = compute_mean_entropy(records, 'heads')
    between = between_record_entropy(records, 'heads')

    print(f"  Mean within-record entropy:  {within_mean:.4f} (std {within_std:.4f})")
    print(f"  Between-record (pooled) entropy: {between:.4f}")
    print(f"  Ratio (within/between): {within_mean/between:.4f}")

    results['t2_entropy'] = {
        'within_mean': round(within_mean, 4),
        'within_std': round(within_std, 4),
        'between_entropy': round(between, 4),
        'ratio': round(within_mean / between, 4) if between > 0 else None,
    }

    # ---- T3: Permutation test ----
    print("\n=== T3: Permutation Test (HEAD) ===")
    perm_result = permutation_test(records, N_PERMUTATIONS, 'heads')

    print(f"  Real mean within-record entropy:   {perm_result['real_mean_entropy']:.4f}")
    print(f"  Shuffled mean entropy:             {perm_result['perm_mean_entropy']:.4f}")
    print(f"  Z-score: {perm_result['z_score']:.2f}")
    print(f"  p-value: {perm_result['p_value']:.4f}")
    print(f"  Entropy reduction: {perm_result['entropy_reduction_pct']:.1f}%")
    print(f"  Verdict: {'COHERENT' if perm_result['coherent'] else 'NOT COHERENT'}")

    results['t3_permutation_head'] = perm_result

    # ---- T4: Record length vs coherence ----
    print("\n=== T4: Record Length vs Coherence ===")

    length_bins = defaultdict(list)
    for rec in records:
        coh = compute_coherence(rec['heads'])
        n = rec['n_tokens']
        if n <= 3:
            length_bins['2-3'].append(coh)
        elif n <= 5:
            length_bins['4-5'].append(coh)
        elif n <= 8:
            length_bins['6-8'].append(coh)
        else:
            length_bins['9+'].append(coh)

    length_results = {}
    for bin_name in ['2-3', '4-5', '6-8', '9+']:
        cohs = length_bins.get(bin_name, [])
        if not cohs:
            continue
        all_same = sum(1 for c in cohs if c['all_same'])
        mean_dom = np.mean([c['dominant_frac'] for c in cohs])
        mean_ent = np.mean([c['entropy'] for c in cohs])
        print(f"  Length {bin_name}: n={len(cohs)}, all_same={100*all_same/len(cohs):.1f}%, "
              f"mean_dominant={mean_dom:.3f}, mean_entropy={mean_ent:.3f}")
        length_results[bin_name] = {
            'n_records': len(cohs),
            'all_same_frac': round(all_same / len(cohs), 4),
            'mean_dominant_frac': round(float(mean_dom), 4),
            'mean_entropy': round(float(mean_ent), 4),
        }

    results['t4_length_vs_coherence'] = length_results

    # ---- T5: Section-specific coherence ----
    print("\n=== T5: Section-Specific Coherence ===")

    section_records = defaultdict(list)
    for rec in records:
        sec = rec['section'] or 'UNK'
        section_records[sec].append(rec)

    section_results = {}
    for sec in sorted(section_records.keys()):
        recs = section_records[sec]
        if len(recs) < 10:
            continue
        all_same = sum(1 for r in recs if compute_coherence(r['heads'])['all_same'])
        mean_ent, _ = compute_mean_entropy(recs, 'heads')
        perm = permutation_test(recs, 500, 'heads')

        print(f"  Section {sec}: n={len(recs)}, all_same={100*all_same/len(recs):.1f}%, "
              f"mean_entropy={mean_ent:.3f}, perm_z={perm['z_score']:.2f}, "
              f"reduction={perm['entropy_reduction_pct']:.1f}%")

        section_results[sec] = {
            'n_records': len(recs),
            'all_same_frac': round(all_same / len(recs), 4),
            'mean_entropy': round(mean_ent, 4),
            'permutation_z': perm['z_score'],
            'permutation_p': perm['p_value'],
            'entropy_reduction_pct': perm['entropy_reduction_pct'],
        }

    results['t5_section_coherence'] = section_results

    # ---- T6: TERMINAL coherence ----
    print("\n=== T6: TERMINAL Atom Coherence ===")

    # Same analysis but for terminals
    term_all_same = 0
    term_dominant_fracs = []
    for rec in records:
        coh = compute_coherence(rec['terminals'])
        if coh['all_same']:
            term_all_same += 1
        term_dominant_fracs.append(coh['dominant_frac'])

    term_perm = permutation_test(records, N_PERMUTATIONS, 'terminals')

    print(f"  TERMINAL all-same: {term_all_same}/{len(records)} "
          f"({100*term_all_same/len(records):.1f}%)")
    print(f"  TERMINAL mean dominant frac: {np.mean(term_dominant_fracs):.3f}")
    print(f"  TERMINAL perm z-score: {term_perm['z_score']:.2f}")
    print(f"  TERMINAL entropy reduction: {term_perm['entropy_reduction_pct']:.1f}%")

    results['t6_terminal_coherence'] = {
        'all_same_frac': round(term_all_same / len(records), 4),
        'mean_dominant_frac': round(float(np.mean(term_dominant_fracs)), 4),
        'permutation': term_perm,
    }

    # ---- T7: Comparison with B lines ----
    print("\n=== T7: Comparison with B Lines ===")

    b_all_same = 0
    b_dominant_fracs = []
    for bl in b_lines:
        coh = compute_coherence(bl['heads'])
        if coh['all_same']:
            b_all_same += 1
        b_dominant_fracs.append(coh['dominant_frac'])

    b_perm = permutation_test(b_lines, N_PERMUTATIONS, 'heads')

    print(f"  A records: all_same={100*all_same_count/len(records):.1f}%, "
          f"mean_dominant={np.mean(dominant_fracs):.3f}")
    print(f"  B lines:   all_same={100*b_all_same/len(b_lines):.1f}%, "
          f"mean_dominant={np.mean(b_dominant_fracs):.3f}")
    print(f"  A perm z-score: {perm_result['z_score']:.2f}, "
          f"B perm z-score: {b_perm['z_score']:.2f}")
    print(f"  A entropy reduction: {perm_result['entropy_reduction_pct']:.1f}%, "
          f"B entropy reduction: {b_perm['entropy_reduction_pct']:.1f}%")

    results['t7_a_vs_b'] = {
        'a_all_same_frac': round(all_same_count / len(records), 4),
        'b_all_same_frac': round(b_all_same / len(b_lines), 4),
        'a_mean_dominant': round(float(np.mean(dominant_fracs)), 4),
        'b_mean_dominant': round(float(np.mean(b_dominant_fracs)), 4),
        'a_perm_z': perm_result['z_score'],
        'b_perm_z': b_perm['z_score'],
        'a_entropy_reduction': perm_result['entropy_reduction_pct'],
        'b_entropy_reduction': b_perm['entropy_reduction_pct'],
        'b_permutation': b_perm,
    }

    # ---- T8: Preferred HEAD combinations in mixed records ----
    print("\n=== T8: Preferred HEAD Combinations (Mixed Records) ===")

    combos = head_combination_analysis(records)

    print(f"  Top 10 HEAD pair combinations in mixed records:")
    for c in combos[:10]:
        sd = "SAME" if c['same_domain'] else "DIFF"
        print(f"    {c['head1']:>4} + {c['head2']:<4}: {c['records']:>4} records  "
              f"[{c['domain1']} x {c['domain2']}] ({sd})")

    results['t8_preferred_combinations'] = combos[:20]

    # ---- T9: Domain-level coherence ----
    print("\n=== T9: Domain-Level Coherence ===")

    # Map HEADs to domains and test coherence at domain level
    domain_records = []
    for rec in records:
        domains = []
        for h in rec['heads']:
            if h == 'NONE':
                domains.append('HEADLESS')
            else:
                domains.append(HEAD_DOMAIN.get(h, 'UNKNOWN'))
        domain_records.append({'domains': domains, 'n_tokens': rec['n_tokens']})

    domain_all_same = sum(1 for dr in domain_records
                         if len(set(dr['domains'])) == 1)
    domain_dominant_fracs = []
    for dr in domain_records:
        counts = Counter(dr['domains'])
        most_common_count = counts.most_common(1)[0][1]
        domain_dominant_fracs.append(most_common_count / len(dr['domains']))

    # Simple permutation: shuffle domain assignments
    real_domain_entropy = np.mean([
        -sum((c/len(dr['domains'])) * math.log2(c/len(dr['domains']))
             for c in Counter(dr['domains']).values())
        for dr in domain_records
    ])

    all_domains_flat = [d for dr in domain_records for d in dr['domains']]
    sizes = [dr['n_tokens'] for dr in domain_records]
    perm_domain_ents = []
    for _ in range(N_PERMUTATIONS):
        shuffled = all_domains_flat.copy()
        random.shuffle(shuffled)
        idx = 0
        ents = []
        for sz in sizes:
            chunk = shuffled[idx:idx+sz]
            idx += sz
            counts = Counter(chunk)
            n = len(chunk)
            ent = -sum((c/n) * math.log2(c/n) for c in counts.values())
            ents.append(ent)
        perm_domain_ents.append(np.mean(ents))

    perm_domain_ents = np.array(perm_domain_ents)
    domain_z = (real_domain_entropy - np.mean(perm_domain_ents)) / (np.std(perm_domain_ents) + 1e-10)
    domain_p = np.mean(perm_domain_ents <= real_domain_entropy)
    domain_reduction = 100 * (1 - real_domain_entropy / np.mean(perm_domain_ents)) if np.mean(perm_domain_ents) > 0 else 0

    print(f"  Domain all-same: {domain_all_same}/{len(records)} "
          f"({100*domain_all_same/len(records):.1f}%)")
    print(f"  Domain mean dominant frac: {np.mean(domain_dominant_fracs):.3f}")
    print(f"  Domain entropy: real={real_domain_entropy:.4f}, "
          f"shuffled={np.mean(perm_domain_ents):.4f}")
    print(f"  Domain z-score: {domain_z:.2f}, p={domain_p:.4f}")
    print(f"  Domain entropy reduction: {domain_reduction:.1f}%")

    results['t9_domain_coherence'] = {
        'all_same_frac': round(domain_all_same / len(records), 4),
        'mean_dominant_frac': round(float(np.mean(domain_dominant_fracs)), 4),
        'real_entropy': round(float(real_domain_entropy), 4),
        'perm_entropy': round(float(np.mean(perm_domain_ents)), 4),
        'z_score': round(float(domain_z), 2),
        'p_value': round(float(domain_p), 4),
        'entropy_reduction_pct': round(float(domain_reduction), 2),
    }

    # ---- T10: Positional HEAD patterns within records ----
    print("\n=== T10: Positional HEAD Patterns ===")

    pos_analysis = positional_head_analysis(records)

    print("  First token HEAD distribution:")
    total_first = sum(pos_analysis['first_token'].values())
    for h, c in sorted(pos_analysis['first_token'].items(), key=lambda x: -x[1])[:6]:
        print(f"    {h:>6}: {c:>5} ({100*c/total_first:.1f}%)")

    print("  Last token HEAD distribution:")
    total_last = sum(pos_analysis['last_token'].values())
    for h, c in sorted(pos_analysis['last_token'].items(), key=lambda x: -x[1])[:6]:
        print(f"    {h:>6}: {c:>5} ({100*c/total_last:.1f}%)")

    if pos_analysis['interior_tokens']:
        print("  Interior token HEAD distribution:")
        total_int = sum(pos_analysis['interior_tokens'].values())
        for h, c in sorted(pos_analysis['interior_tokens'].items(), key=lambda x: -x[1])[:6]:
            print(f"    {h:>6}: {c:>5} ({100*c/total_int:.1f}%)")

    results['t10_positional'] = pos_analysis

    # ---- T11: Adjacent token HEAD transitions ----
    print("\n=== T11: Adjacent Token HEAD Transitions ===")

    head_bigrams = Counter()
    head_same_count = 0
    head_diff_count = 0

    for rec in records:
        heads = rec['heads']
        for i in range(len(heads) - 1):
            pair = (heads[i], heads[i+1])
            head_bigrams[pair] += 1
            if heads[i] == heads[i+1]:
                head_same_count += 1
            else:
                head_diff_count += 1

    total_transitions = head_same_count + head_diff_count
    same_frac = head_same_count / total_transitions if total_transitions > 0 else 0

    # Expected same-HEAD rate under independence
    head_freqs = {h: c / n_total for h, c in head_dist.items()}
    expected_same = sum(f**2 for f in head_freqs.values())

    print(f"  Same HEAD transitions: {head_same_count}/{total_transitions} "
          f"({100*same_frac:.1f}%)")
    print(f"  Expected under independence: {100*expected_same:.1f}%")
    print(f"  Enrichment: {same_frac/expected_same:.2f}x")

    print(f"\n  Top 10 HEAD bigrams:")
    for (h1, h2), c in head_bigrams.most_common(10):
        print(f"    {h1:>4} -> {h2:<4}: {c:>5} ({100*c/total_transitions:.1f}%)")

    results['t11_transitions'] = {
        'same_head_frac': round(same_frac, 4),
        'expected_same': round(expected_same, 4),
        'enrichment': round(same_frac / expected_same, 3) if expected_same > 0 else None,
        'n_transitions': total_transitions,
        'top_bigrams': [{'from': h1, 'to': h2, 'count': c,
                         'fraction': round(c/total_transitions, 4)}
                        for (h1, h2), c in head_bigrams.most_common(15)],
    }

    # ---- T12: Headless token analysis ----
    print("\n=== T12: Headless Token Analysis ===")

    headless_records = sum(1 for rec in records if 'NONE' in rec['heads'])
    all_headless_records = sum(1 for rec in records if all(h == 'NONE' for h in rec['heads']))

    # Among headed-only records: coherence
    headed_only = [rec for rec in records if 'NONE' not in rec['heads']]
    if headed_only:
        ho_same = sum(1 for rec in headed_only if compute_coherence(rec['heads'])['all_same'])
        ho_perm = permutation_test(headed_only, 500, 'heads')

        print(f"  Records with ANY headless token: {headless_records}/{len(records)} "
              f"({100*headless_records/len(records):.1f}%)")
        print(f"  Records ALL headless: {all_headless_records}/{len(records)} "
              f"({100*all_headless_records/len(records):.1f}%)")
        print(f"  Headed-only records: {len(headed_only)}")
        print(f"    all_same: {ho_same}/{len(headed_only)} ({100*ho_same/len(headed_only):.1f}%)")
        print(f"    perm z-score: {ho_perm['z_score']:.2f}")
        print(f"    entropy reduction: {ho_perm['entropy_reduction_pct']:.1f}%")

        results['t12_headless'] = {
            'any_headless_frac': round(headless_records / len(records), 4),
            'all_headless_frac': round(all_headless_records / len(records), 4),
            'headed_only_n': len(headed_only),
            'headed_only_all_same_frac': round(ho_same / len(headed_only), 4),
            'headed_only_perm_z': ho_perm['z_score'],
            'headed_only_entropy_reduction': ho_perm['entropy_reduction_pct'],
        }
    else:
        results['t12_headless'] = {'note': 'No headed-only records found'}

    # ---- Summary ----
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    verdict = "DOMAIN_COHERENT" if perm_result['z_score'] < -3.0 else \
              "WEAKLY_COHERENT" if perm_result['z_score'] < -2.0 else \
              "MIXED" if perm_result['z_score'] < 0 else "NOT_COHERENT"

    print(f"\n  HEAD coherence verdict: {verdict}")
    print(f"  All-same rate: {100*all_same_count/len(records):.1f}%")
    print(f"  Permutation z-score: {perm_result['z_score']:.2f}")
    print(f"  Entropy reduction vs chance: {perm_result['entropy_reduction_pct']:.1f}%")
    print(f"  Same-HEAD transition enrichment: {same_frac/expected_same:.2f}x")
    print(f"\n  TERMINAL coherence z-score: {term_perm['z_score']:.2f}")
    print(f"  DOMAIN coherence z-score: {domain_z:.2f}")
    print(f"\n  A vs B comparison:")
    print(f"    A entropy reduction: {perm_result['entropy_reduction_pct']:.1f}%")
    print(f"    B entropy reduction: {b_perm['entropy_reduction_pct']:.1f}%")

    results['summary'] = {
        'verdict': verdict,
        'n_records': len(records),
        'all_same_frac': round(all_same_count / len(records), 4),
        'head_permutation_z': perm_result['z_score'],
        'head_entropy_reduction_pct': perm_result['entropy_reduction_pct'],
        'same_head_transition_enrichment': round(same_frac / expected_same, 3) if expected_same > 0 else None,
        'terminal_permutation_z': term_perm['z_score'],
        'domain_permutation_z': round(float(domain_z), 2),
        'a_entropy_reduction': perm_result['entropy_reduction_pct'],
        'b_entropy_reduction': b_perm['entropy_reduction_pct'],
    }

    # Write results
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, (np.bool_,)):
                return bool(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    out_path = RESULTS_DIR / 'a_record_head_coherence.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
