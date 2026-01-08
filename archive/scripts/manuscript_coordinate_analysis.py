"""
Phase MCS: Manuscript Coordinate System Reconstruction

Tests whether uncategorized tokens form coordinate systems layered over
the executable grammar.

LOCKED CONSTRAINT (from Phase UTC):
    Uncategorized tokens encode WHERE the operator is in the manuscript,
    not WHAT the operator does.

DO NOT:
- Analyze semantics or morphology
- Merge them into the grammar
- Treat them as operational content
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Set, Dict, List, Tuple
import statistics
from scipy import stats
import numpy as np

# Known prefix/suffix patterns from Phase PMS
KNOWN_PREFIXES = {
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo'
}

KNOWN_SUFFIXES = {
    'aiin', 'ol', 'or', 'ar', 'hy', 'ey', 'dy', 'edy', 'eey', 'eedy',
    'y', 'ain', 'in', 'al', 'am', 'an', 'om', 'on', 'os', 'es',
    'ys', 'ty', 'ny', 'ry'
}


def segment_word(word: str) -> tuple:
    """Segment word into (prefix, core, suffix) using longest-match."""
    if not word:
        return ('', '', '')

    prefix = ''
    suffix = ''

    # Prefix: check 2-char match
    if len(word) >= 2 and word[:2].lower() in KNOWN_PREFIXES:
        prefix = word[:2]

    # Suffix: check longest match (4, 3, 2, 1 chars)
    remainder = word[len(prefix):]
    for suf_len in [4, 3, 2, 1]:
        if len(remainder) >= suf_len and remainder[-suf_len:].lower() in KNOWN_SUFFIXES:
            suffix = remainder[-suf_len:]
            break

    core_end = len(word) - len(suffix) if suffix else len(word)
    core = word[len(prefix):core_end]

    return (prefix, core, suffix)


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


def load_categorized_tokens() -> Set[str]:
    """Load tokens from Phase 20A equivalence classes."""
    json_path = Path('phases/01-09_early_hypothesis/phase20a_operator_equivalence.json')
    categorized = set()

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for cls in data.get('classes', []):
        members = cls.get('members', [])
        for member in members:
            if member:
                categorized.add(member.lower())

    return categorized


def deduplicate_records(records: List[Dict]) -> List[Dict]:
    """Keep only one record per word position (multiple transcribers)."""
    seen = set()
    deduped = []
    for rec in records:
        key = (rec.get('folio', ''), rec.get('line_number', ''),
               rec.get('word', '').lower())
        if key not in seen:
            seen.add(key)
            deduped.append(rec)
    return deduped


# ============================================================
# MCS-1: LINE NUMBER ENCODING
# ============================================================

def analyze_line_number_encoding(records: List[Dict],
                                  categorized: Set[str]) -> Dict:
    """
    Test if uncategorized tokens correlate with line positions.
    """
    print("\n" + "="*60)
    print("MCS-1: LINE NUMBER ENCODING")
    print("="*60)

    # Build line distribution for each uncategorized token type
    uncat_line_dist = defaultdict(Counter)  # token -> Counter of line_numbers
    cat_line_dist = Counter()  # overall categorized line distribution

    for rec in records:
        word = rec.get('word', '').lower().strip()
        line_num = rec.get('line_number', '')
        if not word or word.startswith('*') or not line_num:
            continue

        try:
            line = int(line_num)
        except ValueError:
            continue

        if word in categorized:
            cat_line_dist[line] += 1
        else:
            uncat_line_dist[word][line] += 1

    # For tokens with sufficient data, test for non-uniform distribution
    MIN_FREQ = 10
    significant_tokens = []
    tested = 0

    for token, line_counts in uncat_line_dist.items():
        total = sum(line_counts.values())
        if total < MIN_FREQ:
            continue

        tested += 1

        # Chi-square test vs uniform
        lines = sorted(line_counts.keys())
        observed = [line_counts[l] for l in lines]
        expected_uniform = [total / len(lines)] * len(lines)

        try:
            chi2, p_value = stats.chisquare(observed, expected_uniform)
        except:
            continue

        if p_value < 0.01:
            # Find dominant line
            dominant_line = max(line_counts.keys(), key=lambda l: line_counts[l])
            dominant_pct = line_counts[dominant_line] / total
            significant_tokens.append({
                'token': token,
                'total': total,
                'dominant_line': dominant_line,
                'dominant_pct': dominant_pct,
                'p_value': p_value,
                'chi2': chi2
            })

    # Sort by significance
    significant_tokens.sort(key=lambda x: x['p_value'])

    print(f"\nTested {tested} uncategorized tokens (freq >= {MIN_FREQ})")
    print(f"Significant line-position affinity (p < 0.01): {len(significant_tokens)}")
    print(f"Percentage: {100*len(significant_tokens)/tested:.1f}%" if tested else "N/A")

    print(f"\nTop 20 line-position-correlated tokens:")
    for t in significant_tokens[:20]:
        print(f"  {t['token']:15s} n={t['total']:4d} line={t['dominant_line']:2d} "
              f"({100*t['dominant_pct']:.0f}%) p={t['p_value']:.2e}")

    # Verdict
    pct_significant = len(significant_tokens) / tested if tested else 0
    results = {
        'tested': tested,
        'significant': len(significant_tokens),
        'pct_significant': pct_significant,
        'top_tokens': significant_tokens[:20],
        'verdict': 'SUPPORTED' if pct_significant > 0.10 else 'FALSIFIED' if pct_significant < 0.03 else 'WEAK'
    }

    print(f"\n>>> MCS-1 VERDICT: {results['verdict']}")
    print(f"    Threshold: >10% = SUPPORTED, <3% = FALSIFIED")

    return results


# ============================================================
# MCS-2: QUIRE BOUNDARY MARKERS
# ============================================================

def analyze_quire_boundaries(records: List[Dict],
                              categorized: Set[str]) -> Dict:
    """
    Test if uncategorized tokens cluster at quire transitions.
    """
    print("\n" + "="*60)
    print("MCS-2: QUIRE BOUNDARY MARKERS")
    print("="*60)

    # Group folios by quire
    quire_folios = defaultdict(list)
    for rec in records:
        quire = rec.get('quire', '')
        folio = rec.get('folio', '')
        if quire and folio:
            if folio not in quire_folios[quire]:
                quire_folios[quire].append(folio)

    # Identify boundary folios (first and last in each quire)
    boundary_folios = set()
    for quire, folios in quire_folios.items():
        if len(folios) >= 1:
            boundary_folios.add(folios[0])  # first
            boundary_folios.add(folios[-1])  # last

    print(f"\nQuires found: {len(quire_folios)}")
    print(f"Boundary folios identified: {len(boundary_folios)}")

    # Compare uncategorized density at boundaries vs interior
    boundary_cat = 0
    boundary_uncat = 0
    interior_cat = 0
    interior_uncat = 0

    boundary_vocab = Counter()
    interior_vocab = Counter()

    for rec in records:
        word = rec.get('word', '').lower().strip()
        folio = rec.get('folio', '')
        if not word or word.startswith('*'):
            continue

        is_cat = word in categorized
        is_boundary = folio in boundary_folios

        if is_boundary:
            if is_cat:
                boundary_cat += 1
            else:
                boundary_uncat += 1
                boundary_vocab[word] += 1
        else:
            if is_cat:
                interior_cat += 1
            else:
                interior_uncat += 1
                interior_vocab[word] += 1

    boundary_total = boundary_cat + boundary_uncat
    interior_total = interior_cat + interior_uncat

    boundary_rate = boundary_uncat / boundary_total if boundary_total else 0
    interior_rate = interior_uncat / interior_total if interior_total else 0
    enrichment = boundary_rate / interior_rate if interior_rate else 0

    print(f"\nUncategorized rate:")
    print(f"  Boundary folios: {100*boundary_rate:.1f}% ({boundary_uncat}/{boundary_total})")
    print(f"  Interior folios: {100*interior_rate:.1f}% ({interior_uncat}/{interior_total})")
    print(f"  Enrichment: {enrichment:.2f}x")

    # Chi-square test
    observed = [[boundary_cat, boundary_uncat], [interior_cat, interior_uncat]]
    chi2, p_value, dof, expected = stats.chi2_contingency(observed)
    print(f"  Chi-square: {chi2:.1f}, p = {p_value:.2e}")

    # Boundary-only vocabulary
    boundary_only = set(boundary_vocab.keys()) - set(interior_vocab.keys())
    print(f"\nBoundary-only vocabulary: {len(boundary_only)} types")
    if boundary_only:
        top_boundary = sorted(boundary_only, key=lambda w: boundary_vocab[w], reverse=True)[:10]
        print(f"  Top boundary-only tokens: {', '.join(top_boundary)}")

    results = {
        'boundary_rate': boundary_rate,
        'interior_rate': interior_rate,
        'enrichment': enrichment,
        'p_value': p_value,
        'boundary_only_count': len(boundary_only),
        'verdict': 'SUPPORTED' if enrichment > 1.3 and p_value < 0.05 else 'FALSIFIED'
    }

    print(f"\n>>> MCS-2 VERDICT: {results['verdict']}")
    print(f"    Threshold: enrichment > 1.3x with p < 0.05 = SUPPORTED")

    return results


# ============================================================
# MCS-3: SECTION HEADER TOKENS
# ============================================================

def analyze_section_specificity(records: List[Dict],
                                 categorized: Set[str]) -> Dict:
    """
    Test if uncategorized tokens are section-specific markers.
    """
    print("\n" + "="*60)
    print("MCS-3: SECTION HEADER TOKENS")
    print("="*60)

    # Build section vocabulary
    section_vocab = defaultdict(Counter)  # section -> Counter of uncat tokens

    for rec in records:
        word = rec.get('word', '').lower().strip()
        section = rec.get('section', '')
        if not word or word.startswith('*') or not section:
            continue

        if word not in categorized:
            section_vocab[section][word] += 1

    # Count section-exclusive tokens
    all_uncat = set()
    for section, vocab in section_vocab.items():
        all_uncat.update(vocab.keys())

    section_exclusive = {}  # token -> exclusive section
    section_dominant = {}   # token -> (dominant section, pct)

    for token in all_uncat:
        sections_with_token = []
        total = 0
        for section, vocab in section_vocab.items():
            if token in vocab:
                sections_with_token.append((section, vocab[token]))
                total += vocab[token]

        if len(sections_with_token) == 1:
            section_exclusive[token] = sections_with_token[0][0]
        elif sections_with_token:
            dominant = max(sections_with_token, key=lambda x: x[1])
            if dominant[1] / total > 0.5:
                section_dominant[token] = (dominant[0], dominant[1] / total)

    print(f"\nTotal uncategorized token types: {len(all_uncat)}")
    print(f"Section-exclusive tokens: {len(section_exclusive)} ({100*len(section_exclusive)/len(all_uncat):.1f}%)")
    print(f"Section-dominant (>50%): {len(section_dominant)} ({100*len(section_dominant)/len(all_uncat):.1f}%)")

    # Breakdown by section
    print(f"\nSection-exclusive token counts:")
    section_counts = Counter(section_exclusive.values())
    for section in sorted(section_counts.keys()):
        count = section_counts[section]
        print(f"  Section {section}: {count} exclusive tokens")

    # Sample exclusive tokens
    print(f"\nSample section-exclusive tokens:")
    for section in sorted(section_vocab.keys())[:5]:
        excl = [t for t, s in section_exclusive.items() if s == section]
        if excl:
            # Sort by frequency
            excl_sorted = sorted(excl, key=lambda t: section_vocab[section][t], reverse=True)[:5]
            print(f"  Section {section}: {', '.join(excl_sorted)}")

    pct_exclusive = len(section_exclusive) / len(all_uncat) if all_uncat else 0
    results = {
        'total_uncat_types': len(all_uncat),
        'section_exclusive': len(section_exclusive),
        'section_dominant': len(section_dominant),
        'pct_exclusive': pct_exclusive,
        'section_counts': dict(section_counts),
        'verdict': 'SUPPORTED' if pct_exclusive > 0.20 else 'FALSIFIED' if pct_exclusive < 0.05 else 'WEAK'
    }

    print(f"\n>>> MCS-3 VERDICT: {results['verdict']}")
    print(f"    Threshold: >20% exclusive = SUPPORTED, <5% = FALSIFIED")

    return results


# ============================================================
# MCS-4: PREFIX/SUFFIX COORDINATE CORRELATION
# ============================================================

def analyze_prefix_suffix_correlation(records: List[Dict],
                                       categorized: Set[str]) -> Dict:
    """
    Test if uncategorized tokens use different prefix/suffix patterns.
    """
    print("\n" + "="*60)
    print("MCS-4: PREFIX/SUFFIX COORDINATE CORRELATION")
    print("="*60)

    cat_prefixes = Counter()
    cat_suffixes = Counter()
    uncat_prefixes = Counter()
    uncat_suffixes = Counter()

    for rec in records:
        word = rec.get('word', '').lower().strip()
        if not word or word.startswith('*'):
            continue

        prefix, core, suffix = segment_word(word)
        is_cat = word in categorized

        if is_cat:
            if prefix:
                cat_prefixes[prefix] += 1
            if suffix:
                cat_suffixes[suffix] += 1
        else:
            if prefix:
                uncat_prefixes[prefix] += 1
            if suffix:
                uncat_suffixes[suffix] += 1

    # Compare distributions
    all_prefixes = set(cat_prefixes.keys()) | set(uncat_prefixes.keys())
    all_suffixes = set(cat_suffixes.keys()) | set(uncat_suffixes.keys())

    print(f"\nPrefix analysis:")
    print(f"  Categorized distinct prefixes: {len(cat_prefixes)}")
    print(f"  Uncategorized distinct prefixes: {len(uncat_prefixes)}")

    print(f"\nTop prefixes comparison:")
    print(f"  {'Prefix':8s} {'Cat %':>8s} {'Uncat %':>8s} {'Ratio':>8s}")
    cat_total_pfx = sum(cat_prefixes.values())
    uncat_total_pfx = sum(uncat_prefixes.values())

    for pfx in sorted(all_prefixes, key=lambda p: cat_prefixes[p] + uncat_prefixes[p], reverse=True)[:10]:
        cat_pct = cat_prefixes[pfx] / cat_total_pfx if cat_total_pfx else 0
        uncat_pct = uncat_prefixes[pfx] / uncat_total_pfx if uncat_total_pfx else 0
        ratio = uncat_pct / cat_pct if cat_pct else float('inf')
        print(f"  {pfx:8s} {100*cat_pct:7.1f}% {100*uncat_pct:7.1f}% {ratio:7.2f}x")

    print(f"\nSuffix analysis:")
    print(f"  Categorized distinct suffixes: {len(cat_suffixes)}")
    print(f"  Uncategorized distinct suffixes: {len(uncat_suffixes)}")

    print(f"\nTop suffixes comparison:")
    print(f"  {'Suffix':8s} {'Cat %':>8s} {'Uncat %':>8s} {'Ratio':>8s}")
    cat_total_sfx = sum(cat_suffixes.values())
    uncat_total_sfx = sum(uncat_suffixes.values())

    for sfx in sorted(all_suffixes, key=lambda s: cat_suffixes[s] + uncat_suffixes[s], reverse=True)[:10]:
        cat_pct = cat_suffixes[sfx] / cat_total_sfx if cat_total_sfx else 0
        uncat_pct = uncat_suffixes[sfx] / uncat_total_sfx if uncat_total_sfx else 0
        ratio = uncat_pct / cat_pct if cat_pct else float('inf')
        print(f"  {sfx:8s} {100*cat_pct:7.1f}% {100*uncat_pct:7.1f}% {ratio:7.2f}x")

    # Chi-square test for prefix distribution difference
    common_prefixes = list(set(cat_prefixes.keys()) & set(uncat_prefixes.keys()))
    if len(common_prefixes) >= 2:
        cat_obs = [cat_prefixes[p] for p in common_prefixes]
        uncat_obs = [uncat_prefixes[p] for p in common_prefixes]
        chi2_pfx, p_pfx = stats.chisquare(uncat_obs, f_exp=[c * sum(uncat_obs) / sum(cat_obs) for c in cat_obs])
    else:
        p_pfx = 1.0

    common_suffixes = list(set(cat_suffixes.keys()) & set(uncat_suffixes.keys()))
    if len(common_suffixes) >= 2:
        cat_obs = [cat_suffixes[s] for s in common_suffixes]
        uncat_obs = [uncat_suffixes[s] for s in common_suffixes]
        chi2_sfx, p_sfx = stats.chisquare(uncat_obs, f_exp=[c * sum(uncat_obs) / sum(cat_obs) for c in cat_obs])
    else:
        p_sfx = 1.0

    print(f"\nDistribution difference tests:")
    print(f"  Prefix chi-square: p = {p_pfx:.2e}")
    print(f"  Suffix chi-square: p = {p_sfx:.2e}")

    results = {
        'cat_prefix_count': len(cat_prefixes),
        'uncat_prefix_count': len(uncat_prefixes),
        'cat_suffix_count': len(cat_suffixes),
        'uncat_suffix_count': len(uncat_suffixes),
        'p_prefix': p_pfx,
        'p_suffix': p_sfx,
        'verdict': 'SUPPORTED' if p_pfx < 0.001 or p_sfx < 0.001 else 'FALSIFIED'
    }

    print(f"\n>>> MCS-4 VERDICT: {results['verdict']}")
    print(f"    Threshold: p < 0.001 for either = SUPPORTED")

    return results


# ============================================================
# MCS-5: LINE-INITIAL VOCABULARY
# ============================================================

def analyze_line_initial_vocabulary(records: List[Dict],
                                     categorized: Set[str]) -> Dict:
    """
    Test if line-initial enrichment is driven by specific vocabulary.
    """
    print("\n" + "="*60)
    print("MCS-5: LINE-INITIAL VOCABULARY")
    print("="*60)

    line_initial_vocab = Counter()
    non_line_initial_vocab = Counter()
    line_initial_total = 0
    non_line_initial_total = 0

    for rec in records:
        word = rec.get('word', '').lower().strip()
        line_init = rec.get('line_initial', '')
        if not word or word.startswith('*'):
            continue

        if word in categorized:
            continue  # Only analyze uncategorized

        try:
            is_line_initial = int(line_init) == 1
        except:
            is_line_initial = False

        if is_line_initial:
            line_initial_vocab[word] += 1
            line_initial_total += 1
        else:
            non_line_initial_vocab[word] += 1
            non_line_initial_total += 1

    print(f"\nLine-initial uncategorized tokens: {line_initial_total}")
    print(f"Non-line-initial uncategorized tokens: {non_line_initial_total}")

    # Vocabulary overlap
    li_types = set(line_initial_vocab.keys())
    nli_types = set(non_line_initial_vocab.keys())
    shared = li_types & nli_types
    li_only = li_types - nli_types
    nli_only = nli_types - li_types

    print(f"\nVocabulary comparison:")
    print(f"  Line-initial types: {len(li_types)}")
    print(f"  Non-line-initial types: {len(nli_types)}")
    print(f"  Shared types: {len(shared)}")
    print(f"  Line-initial-only types: {len(li_only)}")

    jaccard = len(shared) / len(li_types | nli_types) if li_types | nli_types else 0
    print(f"  Jaccard similarity: {jaccard:.3f}")

    # Concentration analysis
    # How many token types account for 50% of line-initial occurrences?
    sorted_li = sorted(line_initial_vocab.items(), key=lambda x: x[1], reverse=True)
    cumulative = 0
    types_for_50pct = 0
    for tok, count in sorted_li:
        cumulative += count
        types_for_50pct += 1
        if cumulative >= line_initial_total * 0.5:
            break

    print(f"\nConcentration analysis:")
    print(f"  Types needed for 50% of line-initial occurrences: {types_for_50pct}")

    print(f"\nTop 20 line-initial tokens:")
    for tok, count in sorted_li[:20]:
        pct = 100 * count / line_initial_total
        # Check if this token is line-initial-specific
        nli_count = non_line_initial_vocab.get(tok, 0)
        specificity = count / (count + nli_count) if (count + nli_count) else 0
        marker = " [LI-SPECIFIC]" if specificity > 0.7 else ""
        print(f"  {tok:15s} {count:4d} ({pct:4.1f}%) spec={specificity:.0%}{marker}")

    # Line-initial-specific tokens (>70% of occurrences at line start)
    li_specific = []
    for tok in li_types:
        li_count = line_initial_vocab[tok]
        nli_count = non_line_initial_vocab.get(tok, 0)
        if li_count + nli_count >= 5:  # minimum frequency
            specificity = li_count / (li_count + nli_count)
            if specificity > 0.7:
                li_specific.append((tok, li_count, specificity))

    li_specific.sort(key=lambda x: x[1], reverse=True)
    print(f"\nLine-initial-specific tokens (>70% at line start, freq>=5): {len(li_specific)}")
    print(f"  Top 10: {', '.join([t[0] for t in li_specific[:10]])}")

    results = {
        'line_initial_total': line_initial_total,
        'li_types': len(li_types),
        'nli_types': len(nli_types),
        'jaccard': jaccard,
        'types_for_50pct': types_for_50pct,
        'li_specific_count': len(li_specific),
        'verdict': 'SUPPORTED' if types_for_50pct < 100 else 'FALSIFIED'
    }

    print(f"\n>>> MCS-5 VERDICT: {results['verdict']}")
    print(f"    Threshold: <100 types for 50% = SUPPORTED (concentrated)")

    return results


# ============================================================
# SUMMARY & VERDICT
# ============================================================

def generate_summary(results: Dict) -> None:
    """Generate final summary and verdicts."""
    print("\n" + "="*60)
    print("PHASE MCS: FINAL SUMMARY")
    print("="*60)

    verdicts = {
        'MCS-1 Line Number': results['mcs1']['verdict'],
        'MCS-2 Quire Boundary': results['mcs2']['verdict'],
        'MCS-3 Section Header': results['mcs3']['verdict'],
        'MCS-4 Prefix/Suffix': results['mcs4']['verdict'],
        'MCS-5 Line-Initial': results['mcs5']['verdict'],
    }

    print("\nHypothesis Verdicts:")
    print("-" * 50)
    supported = []
    falsified = []
    weak = []

    for name, verdict in verdicts.items():
        status = verdict
        print(f"  {name:25s}: {status}")
        if verdict == 'SUPPORTED':
            supported.append(name)
        elif verdict == 'FALSIFIED':
            falsified.append(name)
        else:
            weak.append(name)

    print("\n" + "-" * 50)
    print(f"SUPPORTED: {len(supported)}")
    print(f"FALSIFIED: {len(falsified)}")
    print(f"WEAK: {len(weak)}")

    # Interpretation
    print("\n" + "="*60)
    print("INTERPRETATION")
    print("="*60)

    if len(supported) >= 3:
        print("\n>>> MULTI-LAYER COORDINATE SYSTEM DETECTED")
        print("    Uncategorized tokens encode multiple positional dimensions:")
        for s in supported:
            print(f"      - {s}")
    elif len(supported) >= 1:
        print("\n>>> PARTIAL COORDINATE SYSTEM DETECTED")
        print("    Evidence for:")
        for s in supported:
            print(f"      - {s}")
        if falsified:
            print("    No evidence for:")
            for f in falsified:
                print(f"      - {f}")
    else:
        print("\n>>> NO COORDINATE SYSTEM DETECTED")
        print("    Uncategorized tokens do not form systematic positional markers.")
        print("    Recommend returning to Phase UTC findings.")


# ============================================================
# MAIN
# ============================================================

def main():
    print("="*60)
    print("PHASE MCS: MANUSCRIPT COORDINATE SYSTEM RECONSTRUCTION")
    print("="*60)
    print("\nLOCKED CONSTRAINT: Uncategorized tokens encode WHERE,")
    print("                   not WHAT the operator does.")

    # Load data
    print("\nLoading data...")
    records = load_transcription()
    print(f"  Loaded {len(records)} transcription records")

    # Deduplicate (keep one record per word position)
    records = deduplicate_records(records)
    print(f"  After deduplication: {len(records)} records")

    categorized = load_categorized_tokens()
    print(f"  Loaded {len(categorized)} categorized tokens")

    # Run all analyses
    results = {}

    results['mcs1'] = analyze_line_number_encoding(records, categorized)
    results['mcs2'] = analyze_quire_boundaries(records, categorized)
    results['mcs3'] = analyze_section_specificity(records, categorized)
    results['mcs4'] = analyze_prefix_suffix_correlation(records, categorized)
    results['mcs5'] = analyze_line_initial_vocabulary(records, categorized)

    # Summary
    generate_summary(results)

    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)

    return results


if __name__ == '__main__':
    main()
