"""
ATOM_EXTENSIBILITY: Character Repetition and Ratio Family Analysis
===================================================================
Phase 425 -- Tests whether character-level repetition within MIDDLEs
forms systematic ratio families, and whether only specific atoms
(e, i) support consecutive repetition.

Context:
  - C901: Extended e-sequences form stability gradient in Currier A
  - C483: TOKEN-level repetition is ordinal (different phenomenon -- whole
          token repeating on a line, NOT character repetition within MIDDLE)
  - C1190-C1194: Behavioral atomicity and position-specific profiles
  - C1195-C1196: Atom gloss confidence tiers and autogloss coverage

Tests:
  T1: Extensibility Census -- which atoms repeat consecutively?
  T2: Ratio Family Mapping -- geometric decay? combinatorial artifact?
  T3: Order Sensitivity -- does kee differ behaviorally from eek?
  T4: Paragraph Position -- do ratios differ in headers vs bodies?
  T5: Folio Ratio Profiles -- do folios prefer different ratios?
"""
import json
import sys
import math
import re
import random
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/ATOM_EXTENSIBILITY/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MIN_TOKENS = 30
N_PERMUTATIONS = 1000


# ============================================================
# UTILITY
# ============================================================

def vec_correlation(v1, v2):
    """Pearson correlation between two vectors."""
    n = len(v1)
    if n < 2:
        return 0.0
    m1 = sum(v1) / n
    m2 = sum(v2) / n
    num = sum((a - m1) * (b - m2) for a, b in zip(v1, v2))
    d1 = math.sqrt(sum((a - m1) ** 2 for a in v1))
    d2 = math.sqrt(sum((b - m2) ** 2 for b in v2))
    if d1 == 0 or d2 == 0:
        return 0.0
    return num / (d1 * d2)


def has_consecutive_repeat(s, char):
    """Check if char appears consecutively (2+) in string s."""
    return char * 2 in s


def get_consecutive_groups(s):
    """Split string into groups of consecutive identical chars.
    e.g., 'keee' -> [('k',1), ('e',3)]
    """
    if not s:
        return []
    groups = []
    current = s[0]
    count = 1
    for c in s[1:]:
        if c == current:
            count += 1
        else:
            groups.append((current, count))
            current = c
            count = 1
    groups.append((current, count))
    return groups


def char_ratio(middle):
    """Get character frequency ratio as dict. e.g., 'kee' -> {'k': 1/3, 'e': 2/3}"""
    if not middle:
        return {}
    counts = Counter(middle)
    total = len(middle)
    return {c: n / total for c, n in counts.items()}


def ratio_signature(middle):
    """Get sorted atom set for ratio family grouping. e.g., 'kee' -> frozenset({'k','e'})"""
    return frozenset(middle)


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load Currier B tokens with MIDDLEs and metadata."""
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_':
            tokens.append({
                'word': t.word,
                'middle': m.middle,
                'prefix': m.prefix,
                'suffix': m.suffix,
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
                'line_initial': t.line_initial,
                'line_final': t.line_final,
                'par_initial': t.par_initial,
                'par_final': t.par_final,
                'placement': t.placement,
            })
    return tokens


def compute_behavioral_profile(tokens_subset, all_middles_set):
    """Compute a behavioral profile vector for a set of tokens.
    Profile = [folio distribution entropy, section distribution,
               line position mean, prefix diversity, suffix diversity,
               line-initial rate, line-final rate, ...]
    Returns a dict of feature_name -> value.
    """
    if not tokens_subset:
        return {}

    n = len(tokens_subset)

    # Folio distribution
    folio_counts = Counter(t['folio'] for t in tokens_subset)
    folio_entropy = -sum((c/n) * math.log2(c/n) for c in folio_counts.values() if c > 0)

    # Section distribution
    sec_counts = Counter(t['section'] for t in tokens_subset)
    sections = ['HERBAL', 'RECIPE', 'BIO', 'PHARMA']
    sec_fracs = {s: sec_counts.get(s, 0) / n for s in sections}

    # Line position features
    li_rate = sum(1 for t in tokens_subset if t['line_initial']) / n
    lf_rate = sum(1 for t in tokens_subset if t['line_final']) / n
    pi_rate = sum(1 for t in tokens_subset if t['par_initial']) / n

    # Prefix diversity
    prefixes = [t['prefix'] for t in tokens_subset if t['prefix']]
    prefix_types = len(set(prefixes))
    prefix_rate = len(prefixes) / n

    # Suffix diversity
    suffixes = [t['suffix'] for t in tokens_subset if t['suffix']]
    suffix_types = len(set(suffixes))
    suffix_rate = len(suffixes) / n

    profile = {
        'folio_entropy': folio_entropy,
        'n_folios': len(folio_counts),
        'li_rate': li_rate,
        'lf_rate': lf_rate,
        'pi_rate': pi_rate,
        'prefix_rate': prefix_rate,
        'prefix_types': prefix_types,
        'suffix_rate': suffix_rate,
        'suffix_types': suffix_types,
    }
    for s in sections:
        profile[f'sec_{s}'] = sec_fracs.get(s, 0)

    return profile


def profile_to_vector(profile, keys=None):
    """Convert profile dict to vector using consistent key ordering."""
    if keys is None:
        keys = sorted(profile.keys())
    return [profile.get(k, 0) for k in keys]


# ============================================================
# T1: EXTENSIBILITY CENSUS
# ============================================================

def test_extensibility_census(tokens):
    """Establish which atoms can repeat consecutively at structural levels."""
    print("=" * 70)
    print("T1: EXTENSIBILITY CENSUS")
    print("=" * 70)

    # Count MIDDLEs containing consecutive repeats of each character
    alphabet = set()
    for t in tokens:
        alphabet.update(t['middle'])
    alphabet = sorted(alphabet)

    # For each character, find MIDDLEs with consecutive repetition
    results = {}
    for char in alphabet:
        middles_with_repeat = defaultdict(int)
        for t in tokens:
            if has_consecutive_repeat(t['middle'], char):
                middles_with_repeat[t['middle']] += 1
        if middles_with_repeat:
            total_tokens = sum(middles_with_repeat.values())
            results[char] = {
                'unique_middles': len(middles_with_repeat),
                'total_tokens': total_tokens,
                'top_examples': sorted(middles_with_repeat.items(),
                                       key=lambda x: -x[1])[:5],
            }

    # Classification: structural (>20 tokens) vs trace
    STRUCTURAL_THRESHOLD = 20
    structural = {}
    trace = {}
    never = []

    for char in alphabet:
        if char in results:
            if results[char]['total_tokens'] > STRUCTURAL_THRESHOLD:
                structural[char] = results[char]
            else:
                trace[char] = results[char]
        else:
            never.append(char)

    print(f"\nAlphabet size: {len(alphabet)} characters")
    print(f"Threshold: >{STRUCTURAL_THRESHOLD} tokens for structural")
    print()

    print("STRUCTURAL (extensible atoms):")
    print(f"  {'Char':<6} {'Unique MIDDLEs':<18} {'Total Tokens':<15} Top Examples")
    print(f"  {'----':<6} {'-'*16:<18} {'-'*12:<15} {'-'*30}")
    for char in sorted(structural, key=lambda c: -structural[c]['total_tokens']):
        r = structural[char]
        examples = ', '.join(f"{m}({c})" for m, c in r['top_examples'][:3])
        print(f"  {char:<6} {r['unique_middles']:<18} {r['total_tokens']:<15} {examples}")

    print(f"\nTRACE (noise / transcription artifacts):")
    for char in sorted(trace, key=lambda c: -trace[c]['total_tokens']):
        r = trace[char]
        examples = ', '.join(f"{m}({c})" for m, c in r['top_examples'][:3])
        print(f"  {char:<6} {r['unique_middles']:<18} {r['total_tokens']:<15} {examples}")

    print(f"\nNEVER REPEAT: {', '.join(never)} ({len(never)} atoms)")

    # Binary vs extensible partition
    extensible = sorted(structural.keys())
    binary = sorted(set(alphabet) - set(extensible))
    print(f"\n--- PARTITION ---")
    print(f"EXTENSIBLE ({len(extensible)}): {', '.join(extensible)}")
    print(f"BINARY ({len(binary)}): {', '.join(binary)}")

    return {
        'structural': {c: {'unique_middles': v['unique_middles'],
                          'total_tokens': v['total_tokens']}
                      for c, v in structural.items()},
        'trace': {c: {'unique_middles': v['unique_middles'],
                     'total_tokens': v['total_tokens']}
                 for c, v in trace.items()},
        'never': never,
        'extensible': extensible,
        'binary': binary,
        'threshold': STRUCTURAL_THRESHOLD,
    }


# ============================================================
# T2: RATIO FAMILY MAPPING
# ============================================================

def test_ratio_families(tokens):
    """Map ratio families and test for geometric decay."""
    print("\n" + "=" * 70)
    print("T2: RATIO FAMILY MAPPING")
    print("=" * 70)

    # Build MIDDLE -> count map
    middle_counts = Counter(t['middle'] for t in tokens)

    # Group MIDDLEs into ratio families by atom set
    families = defaultdict(list)
    for middle, count in middle_counts.items():
        atoms = frozenset(middle)
        families[atoms].append((middle, count, len(middle)))

    # Filter to families with 2+ members where at least one has consecutive repeat
    ratio_families = {}
    for atoms, members in families.items():
        if len(members) < 2:
            continue
        has_repeat = any(
            any(has_consecutive_repeat(m, c) for c in m)
            for m, _, _ in members
        )
        if not has_repeat:
            continue
        members_sorted = sorted(members, key=lambda x: -x[1])
        total = sum(c for _, c, _ in members_sorted)
        ratio_families[atoms] = {
            'members': members_sorted,
            'total_tokens': total,
        }

    # Sort families by total tokens
    sorted_families = sorted(ratio_families.items(), key=lambda x: -x[1]['total_tokens'])

    print(f"\nTotal ratio families (2+ members, has repeat): {len(sorted_families)}")
    print()

    # Show top 15 families
    print("TOP 15 RATIO FAMILIES:")
    print()
    geometric_fits = []

    for i, (atoms, fam) in enumerate(sorted_families[:15]):
        atom_str = '+'.join(sorted(atoms))
        print(f"  Family #{i+1}: {{{atom_str}}} — {fam['total_tokens']} tokens, "
              f"{len(fam['members'])} members")
        for middle, count, length in fam['members']:
            ratio = char_ratio(middle)
            ratio_str = ', '.join(f"{c}:{r:.2f}" for c, r in sorted(ratio.items()))
            print(f"    {middle:<12} {count:>6}  len={length}  ({ratio_str})")

        # Test geometric decay: does each additional repeat divide by constant?
        counts_by_length = defaultdict(int)
        for middle, count, length in fam['members']:
            counts_by_length[length] += count
        lengths = sorted(counts_by_length.keys())
        if len(lengths) >= 3:
            ratios_between = []
            for j in range(len(lengths) - 1):
                c1 = counts_by_length[lengths[j]]
                c2 = counts_by_length[lengths[j + 1]]
                if c2 > 0:
                    ratios_between.append(c1 / c2)
            if ratios_between:
                mean_ratio = sum(ratios_between) / len(ratios_between)
                cv = (sum((r - mean_ratio)**2 for r in ratios_between) /
                      len(ratios_between))**0.5 / mean_ratio if mean_ratio > 0 else float('inf')
                geometric_fits.append({
                    'family': atom_str,
                    'decay_ratios': ratios_between,
                    'mean_decay': mean_ratio,
                    'cv': cv,
                })
                print(f"    Decay ratios: {[f'{r:.1f}' for r in ratios_between]} "
                      f"(mean={mean_ratio:.1f}, CV={cv:.2f})")
        print()

    # Aggregate geometric decay analysis
    print("GEOMETRIC DECAY ANALYSIS:")
    if geometric_fits:
        all_decay = [g['mean_decay'] for g in geometric_fits]
        global_mean = sum(all_decay) / len(all_decay)
        print(f"  Families with 3+ length variants: {len(geometric_fits)}")
        print(f"  Mean decay ratio across families: {global_mean:.1f}x per additional character")
        print(f"  Range: {min(all_decay):.1f}x - {max(all_decay):.1f}x")

        # Is it consistent (geometric) or variable (not geometric)?
        all_cv = [g['cv'] for g in geometric_fits]
        mean_cv = sum(all_cv) / len(all_cv)
        print(f"  Mean CV within families: {mean_cv:.2f} "
              f"({'consistent' if mean_cv < 0.5 else 'variable'} decay)")
    else:
        print("  No families with 3+ length variants.")

    return {
        'n_families': len(sorted_families),
        'top_families': [
            {'atoms': '+'.join(sorted(atoms)),
             'total_tokens': fam['total_tokens'],
             'n_members': len(fam['members']),
             'members': [{'middle': m, 'count': c, 'length': l}
                        for m, c, l in fam['members']]}
            for atoms, fam in sorted_families[:20]
        ],
        'geometric_fits': geometric_fits,
    }


# ============================================================
# T3: ORDER SENSITIVITY
# ============================================================

def test_order_sensitivity(tokens):
    """Test whether same-ratio-different-order MIDDLEs have different behavioral profiles."""
    print("\n" + "=" * 70)
    print("T3: ORDER SENSITIVITY")
    print("=" * 70)

    # Find ratio-equivalent pairs: same character counts, different order
    middle_counts = Counter(t['middle'] for t in tokens)

    # Group by character count signature (sorted character counts)
    count_sig_groups = defaultdict(list)
    for middle, count in middle_counts.items():
        if count < 10:  # Need minimum tokens for profile
            continue
        sig = tuple(sorted(Counter(middle).items()))
        count_sig_groups[sig].append((middle, count))

    # Filter to groups with 2+ members (same ratio, different order)
    order_pairs = []
    for sig, members in count_sig_groups.items():
        if len(members) >= 2:
            order_pairs.append({
                'signature': dict(sig),
                'members': sorted(members, key=lambda x: -x[1]),
            })

    order_pairs.sort(key=lambda x: -sum(c for _, c in x['members']))

    print(f"\nRatio-equivalent groups (same chars, different order, >=10 tokens each): "
          f"{len(order_pairs)}")

    if not order_pairs:
        print("  No qualifying pairs found.")
        return {'n_pairs': 0, 'pairs': []}

    # Build per-MIDDLE token lists
    middle_tokens = defaultdict(list)
    for t in tokens:
        middle_tokens[t['middle']].append(t)

    # Compute behavioral profiles and compare within vs between groups
    all_middles = set(middle_counts.keys())
    profile_keys = None
    within_sims = []
    between_sims = []

    print(f"\nORDER-EQUIVALENT PAIRS:")
    pair_results = []
    for group in order_pairs[:20]:
        members = group['members']
        sig_str = ''.join(f"{c}{n}" for c, n in sorted(group['signature'].items()))
        profiles = {}
        for middle, count in members:
            toks = middle_tokens[middle]
            p = compute_behavioral_profile(toks, all_middles)
            if profile_keys is None:
                profile_keys = sorted(p.keys())
            profiles[middle] = profile_to_vector(p, profile_keys)

        # Compute pairwise similarities within this group
        member_names = [m for m, _ in members]
        group_sims = []
        for a in range(len(member_names)):
            for b in range(a + 1, len(member_names)):
                sim = vec_correlation(profiles[member_names[a]],
                                      profiles[member_names[b]])
                group_sims.append(sim)
                within_sims.append(sim)

        mean_sim = sum(group_sims) / len(group_sims) if group_sims else 0

        member_str = ', '.join(f"{m}({c})" for m, c in members)
        print(f"  [{sig_str}] {member_str}")
        print(f"    Intra-group similarity: {mean_sim:.3f}")

        pair_results.append({
            'signature': sig_str,
            'members': [{'middle': m, 'count': c} for m, c in members],
            'intra_similarity': mean_sim,
        })

    # Compute between-group baseline (random pairs of different-ratio MIDDLEs)
    all_profiled = []
    for group in order_pairs[:20]:
        for middle, count in group['members']:
            toks = middle_tokens[middle]
            p = compute_behavioral_profile(toks, all_middles)
            all_profiled.append((middle, profile_to_vector(p, profile_keys)))

    random.seed(42)
    for _ in range(min(500, len(all_profiled) * 10)):
        if len(all_profiled) < 2:
            break
        i, j = random.sample(range(len(all_profiled)), 2)
        # Only count if from different ratio groups
        mi, pi = all_profiled[i]
        mj, pj = all_profiled[j]
        if Counter(mi) != Counter(mj):
            sim = vec_correlation(pi, pj)
            between_sims.append(sim)

    mean_within = sum(within_sims) / len(within_sims) if within_sims else 0
    mean_between = sum(between_sims) / len(between_sims) if between_sims else 0

    print(f"\n--- SUMMARY ---")
    print(f"Mean within-group similarity (same ratio, different order): {mean_within:.3f}")
    print(f"Mean between-group similarity (different ratio): {mean_between:.3f}")
    print(f"Separation: {mean_within - mean_between:+.3f}")

    if mean_within > mean_between + 0.05:
        verdict = "ORDER_SECONDARY"
        print(f"Verdict: {verdict} — same-ratio pairs are more similar than different-ratio pairs.")
        print("  Order carries LESS information than ratio. Ratio dominates.")
    elif abs(mean_within - mean_between) <= 0.05:
        verdict = "ORDER_INDEPENDENT"
        print(f"Verdict: {verdict} — same-ratio pairs are no more similar than random pairs.")
        print("  Order carries AS MUCH information as ratio. Both matter equally.")
    else:
        verdict = "ORDER_DOMINANT"
        print(f"Verdict: {verdict} — same-ratio pairs are LESS similar than random pairs.")
        print("  Order dominates over ratio.")

    # Permutation test: is within > between significant?
    pooled = within_sims + between_sims
    n_within = len(within_sims)
    observed_diff = mean_within - mean_between

    perm_count = 0
    random.seed(42)
    for _ in range(N_PERMUTATIONS):
        random.shuffle(pooled)
        perm_within = sum(pooled[:n_within]) / n_within if n_within else 0
        perm_between = sum(pooled[n_within:]) / len(pooled[n_within:]) if len(pooled[n_within:]) else 0
        if perm_within - perm_between >= observed_diff:
            perm_count += 1
    p_value = perm_count / N_PERMUTATIONS

    print(f"Permutation test: p={p_value:.4f} (observed diff={observed_diff:.3f})")

    return {
        'n_pairs': len(order_pairs),
        'pair_results': pair_results,
        'mean_within': mean_within,
        'mean_between': mean_between,
        'separation': mean_within - mean_between,
        'verdict': verdict,
        'p_value': p_value,
    }


# ============================================================
# T4: PARAGRAPH POSITION DISTRIBUTION
# ============================================================

def test_paragraph_distribution(tokens):
    """Test whether e/i extension ratios differ between paragraph headers and bodies."""
    print("\n" + "=" * 70)
    print("T4: PARAGRAPH POSITION DISTRIBUTION")
    print("=" * 70)

    # Classify each token by paragraph position
    # par_initial=True tokens are in the first line of a paragraph (header zone)
    # We'll use a simpler heuristic: line_initial tokens on par_initial lines = header

    # For each token, classify: HEADER (par_initial line) vs BODY (not par_initial)
    # Then check if MIDDLEs with extensions (ee, ii) distribute differently

    header_tokens = [t for t in tokens if t['par_initial']]
    body_tokens = [t for t in tokens if not t['par_initial']]

    print(f"\nHeader tokens (par_initial lines): {len(header_tokens)}")
    print(f"Body tokens: {len(body_tokens)}")

    def compute_extension_stats(tok_list, label):
        """Compute extension statistics for a token set."""
        n = len(tok_list)
        if n == 0:
            return {}

        # Count tokens with ee, ii patterns
        n_ee = sum(1 for t in tok_list if 'ee' in t['middle'])
        n_ii = sum(1 for t in tok_list if 'ii' in t['middle'])
        n_extended = sum(1 for t in tok_list
                        if 'ee' in t['middle'] or 'ii' in t['middle'])

        # Average extension length for e-containing MIDDLEs
        e_lengths = []
        for t in tok_list:
            m = t['middle']
            if 'e' in m:
                # Count max consecutive e's
                max_e = max(len(run) for run in re.findall(r'e+', m))
                e_lengths.append(max_e)

        i_lengths = []
        for t in tok_list:
            m = t['middle']
            if 'i' in m:
                max_i = max(len(run) for run in re.findall(r'i+', m))
                i_lengths.append(max_i)

        mean_e_ext = sum(e_lengths) / len(e_lengths) if e_lengths else 0
        mean_i_ext = sum(i_lengths) / len(i_lengths) if i_lengths else 0

        stats = {
            'n': n,
            'ee_rate': n_ee / n,
            'ii_rate': n_ii / n,
            'extended_rate': n_extended / n,
            'mean_e_extension': mean_e_ext,
            'mean_i_extension': mean_i_ext,
            'n_ee': n_ee,
            'n_ii': n_ii,
        }

        print(f"\n  {label} (n={n}):")
        print(f"    ee-containing: {n_ee} ({n_ee/n:.1%})")
        print(f"    ii-containing: {n_ii} ({n_ii/n:.1%})")
        print(f"    Any extension: {n_extended} ({n_extended/n:.1%})")
        print(f"    Mean e-run length (in e-containing): {mean_e_ext:.2f}")
        print(f"    Mean i-run length (in i-containing): {mean_i_ext:.2f}")

        return stats

    header_stats = compute_extension_stats(header_tokens, "HEADER")
    body_stats = compute_extension_stats(body_tokens, "BODY")

    # Statistical test: chi-squared for extension rate difference
    # H0: extension rate is the same in headers and bodies
    h_ext = int(header_stats['n_ee'] + header_stats['n_ii'])
    h_noext = header_stats['n'] - h_ext
    b_ext = int(body_stats['n_ee'] + body_stats['n_ii'])
    b_noext = body_stats['n'] - b_ext

    total = h_ext + h_noext + b_ext + b_noext
    exp_h_ext = (h_ext + b_ext) * (h_ext + h_noext) / total
    exp_h_noext = (h_noext + b_noext) * (h_ext + h_noext) / total
    exp_b_ext = (h_ext + b_ext) * (b_ext + b_noext) / total
    exp_b_noext = (h_noext + b_noext) * (b_ext + b_noext) / total

    chi2 = 0
    for obs, exp in [(h_ext, exp_h_ext), (h_noext, exp_h_noext),
                     (b_ext, exp_b_ext), (b_noext, exp_b_noext)]:
        if exp > 0:
            chi2 += (obs - exp) ** 2 / exp

    # Approximate p-value from chi2 with 1 df
    # Using survival function approximation
    p_approx = math.exp(-chi2 / 2) if chi2 < 20 else 0.0

    print(f"\n--- HEADER vs BODY COMPARISON ---")
    print(f"  Header extension rate: {header_stats.get('extended_rate', 0):.1%}")
    print(f"  Body extension rate: {body_stats.get('extended_rate', 0):.1%}")
    print(f"  Chi-squared: {chi2:.2f}")
    print(f"  p (approx): {p_approx:.4f}")

    # Also test: does MEAN extension length differ?
    # (Do headers use longer runs than bodies?)
    e_diff = header_stats.get('mean_e_extension', 0) - body_stats.get('mean_e_extension', 0)
    i_diff = header_stats.get('mean_i_extension', 0) - body_stats.get('mean_i_extension', 0)
    print(f"  Mean e-extension diff (header-body): {e_diff:+.3f}")
    print(f"  Mean i-extension diff (header-body): {i_diff:+.3f}")

    # Line-position analysis: extension rate by line position within paragraph
    # Group by line number relative to paragraph start
    # Using line number directly (line 1 = first line of folio section)
    line_extension = defaultdict(lambda: {'extended': 0, 'total': 0})
    for t in tokens:
        try:
            line_num = int(t['line'])
        except (ValueError, TypeError):
            continue
        bucket = min(line_num, 10)  # Cap at 10+
        has_ext = 'ee' in t['middle'] or 'ii' in t['middle']
        line_extension[bucket]['total'] += 1
        if has_ext:
            line_extension[bucket]['extended'] += 1

    print(f"\n  Extension rate by line number:")
    print(f"  {'Line':<8} {'Total':<8} {'Extended':<10} {'Rate':<8}")
    for line_num in sorted(line_extension.keys()):
        d = line_extension[line_num]
        rate = d['extended'] / d['total'] if d['total'] > 0 else 0
        print(f"  {line_num:<8} {d['total']:<8} {d['extended']:<10} {rate:.1%}")

    return {
        'header_stats': header_stats,
        'body_stats': body_stats,
        'chi2': chi2,
        'p_approx': p_approx,
        'e_extension_diff': e_diff,
        'i_extension_diff': i_diff,
    }


# ============================================================
# T5: FOLIO RATIO PROFILES
# ============================================================

def test_folio_ratio_profiles(tokens):
    """Test whether different folios prefer different extension ratios."""
    print("\n" + "=" * 70)
    print("T5: FOLIO RATIO PROFILES")
    print("=" * 70)

    # For each folio, compute:
    # - Rate of ee-containing MIDDLEs
    # - Rate of ii-containing MIDDLEs
    # - Mean e-extension length (among e-containing)
    # - Mean i-extension length (among i-containing)
    # - Ratio of single-e to double-e (e vs ee preference)

    folio_tokens = defaultdict(list)
    for t in tokens:
        folio_tokens[t['folio']].append(t)

    folio_profiles = {}
    for folio in sorted(folio_tokens):
        toks = folio_tokens[folio]
        n = len(toks)
        if n < 30:
            continue

        # e-extension analysis
        e_toks = [t for t in toks if 'e' in t['middle']]
        e_runs = []
        for t in e_toks:
            runs = re.findall(r'e+', t['middle'])
            if runs:
                e_runs.append(max(len(r) for r in runs))

        single_e = sum(1 for r in e_runs if r == 1)
        double_e = sum(1 for r in e_runs if r >= 2)
        mean_e = sum(e_runs) / len(e_runs) if e_runs else 0

        # i-extension analysis
        i_toks = [t for t in toks if 'i' in t['middle']]
        i_runs = []
        for t in i_toks:
            runs = re.findall(r'i+', t['middle'])
            if runs:
                i_runs.append(max(len(r) for r in runs))

        single_i = sum(1 for r in i_runs if r == 1)
        double_i = sum(1 for r in i_runs if r >= 2)
        mean_i = sum(i_runs) / len(i_runs) if i_runs else 0

        ee_rate = double_e / len(e_toks) if e_toks else 0
        ii_rate = double_i / len(i_toks) if i_toks else 0

        folio_profiles[folio] = {
            'n': n,
            'section': toks[0]['section'],
            'e_tokens': len(e_toks),
            'mean_e_ext': mean_e,
            'ee_rate': ee_rate,
            'i_tokens': len(i_toks),
            'mean_i_ext': mean_i,
            'ii_rate': ii_rate,
        }

    # Sort by ee_rate to find extremes
    by_ee = sorted(folio_profiles.items(), key=lambda x: x[1]['ee_rate'])

    print(f"\nFolios analyzed: {len(folio_profiles)} (>= 30 tokens)")

    print(f"\nLOWEST ee-rate folios (minimal extension):")
    print(f"  {'Folio':<12} {'Section':<10} {'n':<6} {'e-toks':<8} {'ee%':<8} {'mean_e':<8}")
    for folio, p in by_ee[:10]:
        print(f"  {folio:<12} {p['section']:<10} {p['n']:<6} "
              f"{p['e_tokens']:<8} {p['ee_rate']:.1%}   {p['mean_e_ext']:.2f}")

    print(f"\nHIGHEST ee-rate folios (maximal extension):")
    for folio, p in by_ee[-10:]:
        print(f"  {folio:<12} {p['section']:<10} {p['n']:<6} "
              f"{p['e_tokens']:<8} {p['ee_rate']:.1%}   {p['mean_e_ext']:.2f}")

    # Test: does section predict ee_rate?
    section_ee = defaultdict(list)
    section_ii = defaultdict(list)
    for folio, p in folio_profiles.items():
        section_ee[p['section']].append(p['ee_rate'])
        section_ii[p['section']].append(p['ii_rate'])

    print(f"\nSECTION-LEVEL EXTENSION RATES:")
    print(f"  {'Section':<12} {'n_folios':<10} {'mean_ee%':<12} {'std_ee%':<12} "
          f"{'mean_ii%':<12} {'std_ii%':<12}")
    section_means = {}
    for sec in sorted(section_ee):
        vals_e = section_ee[sec]
        vals_i = section_ii[sec]
        mean_e = sum(vals_e) / len(vals_e)
        std_e = (sum((v - mean_e)**2 for v in vals_e) / len(vals_e))**0.5
        mean_i = sum(vals_i) / len(vals_i)
        std_i = (sum((v - mean_i)**2 for v in vals_i) / len(vals_i))**0.5
        section_means[sec] = {'mean_ee': mean_e, 'std_ee': std_e,
                              'mean_ii': mean_i, 'std_ii': std_i,
                              'n': len(vals_e)}
        print(f"  {sec:<12} {len(vals_e):<10} {mean_e:.1%}       {std_e:.1%}       "
              f"{mean_i:.1%}       {std_i:.1%}")

    # Kruskal-Wallis-like test: do section means differ significantly?
    # Using permutation test on between-section variance
    all_ee_rates = [(p['ee_rate'], p['section']) for _, p in folio_profiles.items()]
    section_labels = [sec for _, sec in all_ee_rates]
    ee_vals = [v for v, _ in all_ee_rates]

    def between_section_var(vals, labels):
        """Compute between-section variance of means."""
        sec_groups = defaultdict(list)
        for v, l in zip(vals, labels):
            sec_groups[l].append(v)
        means = [sum(g) / len(g) for g in sec_groups.values() if len(g) >= 3]
        if len(means) < 2:
            return 0
        grand_mean = sum(means) / len(means)
        return sum((m - grand_mean)**2 for m in means) / len(means)

    observed_var = between_section_var(ee_vals, section_labels)
    perm_count = 0
    random.seed(42)
    for _ in range(N_PERMUTATIONS):
        shuffled = section_labels.copy()
        random.shuffle(shuffled)
        perm_var = between_section_var(ee_vals, shuffled)
        if perm_var >= observed_var:
            perm_count += 1
    p_section = perm_count / N_PERMUTATIONS

    print(f"\n  Between-section variance test (ee_rate): p={p_section:.4f}")

    # Same for ii
    all_ii_rates = [(p['ii_rate'], p['section']) for _, p in folio_profiles.items()]
    ii_vals = [v for v, _ in all_ii_rates]
    observed_var_ii = between_section_var(ii_vals, section_labels)
    perm_count_ii = 0
    random.seed(42)
    for _ in range(N_PERMUTATIONS):
        shuffled = section_labels.copy()
        random.shuffle(shuffled)
        perm_var = between_section_var(ii_vals, shuffled)
        if perm_var >= observed_var_ii:
            perm_count_ii += 1
    p_section_ii = perm_count_ii / N_PERMUTATIONS

    print(f"  Between-section variance test (ii_rate): p={p_section_ii:.4f}")

    # Folio-level variance test: do folios within the same section differ?
    # (i.e., is there folio-level parameterization beyond section?)
    within_section_vars = {}
    for sec, vals in section_ee.items():
        if len(vals) >= 5:
            mean_v = sum(vals) / len(vals)
            var_v = sum((v - mean_v)**2 for v in vals) / len(vals)
            within_section_vars[sec] = {'variance': var_v, 'n': len(vals),
                                         'cv': var_v**0.5 / mean_v if mean_v > 0 else 0}

    print(f"\n  Within-section folio variance (ee_rate):")
    for sec in sorted(within_section_vars):
        v = within_section_vars[sec]
        print(f"    {sec:<12} var={v['variance']:.4f}  CV={v['cv']:.2f}  n={v['n']}")

    return {
        'n_folios': len(folio_profiles),
        'section_means': section_means,
        'p_section_ee': p_section,
        'p_section_ii': p_section_ii,
        'within_section_vars': within_section_vars,
        'folio_profiles': {f: p for f, p in list(folio_profiles.items())},
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("ATOM EXTENSIBILITY TEST — Phase 425")
    print("=" * 70)

    print("\nLoading data...")
    tokens = load_data()
    print(f"Loaded {len(tokens)} Currier B tokens with MIDDLEs")

    results = {}

    # T1
    results['T1_extensibility_census'] = test_extensibility_census(tokens)

    # T2
    results['T2_ratio_families'] = test_ratio_families(tokens)

    # T3
    results['T3_order_sensitivity'] = test_order_sensitivity(tokens)

    # T4
    results['T4_paragraph_distribution'] = test_paragraph_distribution(tokens)

    # T5
    results['T5_folio_ratio_profiles'] = test_folio_ratio_profiles(tokens)

    # Save results
    output_path = RESULTS_DIR / "atom_extensibility_results.json"

    # Clean results for JSON serialization
    def clean_for_json(obj):
        if isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_for_json(v) for v in obj]
        elif isinstance(obj, (set, frozenset)):
            return sorted(obj)
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return round(obj, 6)
        return obj

    with open(output_path, 'w') as f:
        json.dump(clean_for_json(results), f, indent=2)

    print(f"\n{'='*70}")
    print(f"Results saved to {output_path}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
