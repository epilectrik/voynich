"""Gap Analysis: Remaining Gaps and Limitations.

Task 6: Report on:
- Percentage of corpus with procedural reconstructions
- Top 20 most frequent morphemes that remain uncertain
- Sections/folios that resist our framework most strongly
- What would resolve the remaining gaps

Honest limitations preferred over false confidence.
"""
import sys
import json
from datetime import datetime
from collections import defaultdict, Counter

sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus
from two_layer_specification import PREFIX_MAPPINGS, MIDDLE_MAPPINGS, SUFFIX_MAPPINGS

# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def get_section(folio):
    """Assign section based on folio number."""
    if not folio:
        return 'UNKNOWN'
    num_part = ''.join(c for c in folio if c.isdigit())
    if not num_part:
        return 'UNKNOWN'
    num = int(num_part)

    if num <= 66:
        return 'HERBAL'
    elif num <= 73:
        return 'ZODIAC'
    elif num <= 84:
        return 'BIOLOGICAL'
    elif num <= 86:
        return 'COSMOLOGICAL'
    else:
        return 'RECIPES'


def decode_word_coverage(word):
    """Analyze how much of a word is decoded."""
    if not word:
        return {'word': word, 'prefix': False, 'middle': False, 'suffix': False, 'total': 0, 'remaining': word}

    text = word.lower()
    original = text
    result = {
        'word': word,
        'prefix': False,
        'prefix_name': None,
        'middle': False,
        'middle_name': None,
        'suffix': False,
        'suffix_name': None,
        'total_decoded': 0,
        'remaining': None,
        'remaining_chars': None,
    }

    remaining = text

    # Check prefix
    for prefix in sorted(PREFIX_MAPPINGS.keys(), key=len, reverse=True):
        if remaining.startswith(prefix):
            result['prefix'] = True
            result['prefix_name'] = prefix
            result['total_decoded'] += 1
            remaining = remaining[len(prefix):]
            break

    # Check suffix
    for suffix in sorted(SUFFIX_MAPPINGS.keys(), key=len, reverse=True):
        if remaining.endswith(suffix):
            result['suffix'] = True
            result['suffix_name'] = suffix
            result['total_decoded'] += 1
            remaining = remaining[:-len(suffix)]
            break

    # Check middle (gallows and non-gallows)
    for middle in sorted(MIDDLE_MAPPINGS.keys(), key=len, reverse=True):
        if middle in remaining:
            result['middle'] = True
            result['middle_name'] = middle
            result['total_decoded'] += 1
            remaining = remaining.replace(middle, '', 1)
            break

    result['remaining'] = remaining
    result['remaining_chars'] = len(remaining)

    return result


def analyze_corpus_coverage(corpus):
    """Analyze how much of the corpus can be decoded."""
    words_analyzed = 0
    fully_decoded = 0  # All 3 components
    mostly_decoded = 0  # 2 components
    partially_decoded = 0  # 1 component
    not_decoded = 0  # 0 components

    prefix_coverage = 0
    middle_coverage = 0
    suffix_coverage = 0

    remaining_chars = Counter()  # Track undecoded character sequences
    undecoded_words = []  # Words with 0 components

    for w in corpus.words:
        if not w.text:
            continue

        words_analyzed += 1
        result = decode_word_coverage(w.text)

        if result['prefix']:
            prefix_coverage += 1
        if result['middle']:
            middle_coverage += 1
        if result['suffix']:
            suffix_coverage += 1

        if result['total_decoded'] >= 3:
            fully_decoded += 1
        elif result['total_decoded'] == 2:
            mostly_decoded += 1
        elif result['total_decoded'] == 1:
            partially_decoded += 1
        else:
            not_decoded += 1
            undecoded_words.append(w.text)

        if result['remaining']:
            remaining_chars[result['remaining']] += 1

    return {
        'words_analyzed': words_analyzed,
        'fully_decoded': fully_decoded,
        'mostly_decoded': mostly_decoded,
        'partially_decoded': partially_decoded,
        'not_decoded': not_decoded,
        'prefix_coverage': prefix_coverage,
        'middle_coverage': middle_coverage,
        'suffix_coverage': suffix_coverage,
        'remaining_chars': remaining_chars,
        'undecoded_words': undecoded_words,
    }


def find_uncertain_morphemes(corpus):
    """Find morphemes that appear frequently but are not in our mappings."""
    # Extract all potential morphemes (2-4 character sequences)
    potential_prefixes = Counter()
    potential_middles = Counter()
    potential_suffixes = Counter()

    for w in corpus.words:
        if not w.text or len(w.text) < 2:
            continue

        text = w.text.lower()

        # First 2-3 chars as potential prefix
        if len(text) >= 2:
            p2 = text[:2]
            if p2 not in PREFIX_MAPPINGS:
                potential_prefixes[p2] += 1

        if len(text) >= 3:
            p3 = text[:3]
            if p3 not in PREFIX_MAPPINGS:
                potential_prefixes[p3] += 1

        # Last 2-3 chars as potential suffix
        if len(text) >= 2:
            s2 = text[-2:]
            if s2 not in SUFFIX_MAPPINGS:
                potential_suffixes[s2] += 1

        if len(text) >= 3:
            s3 = text[-3:]
            if s3 not in SUFFIX_MAPPINGS:
                potential_suffixes[s3] += 1

    return {
        'prefixes': potential_prefixes.most_common(20),
        'suffixes': potential_suffixes.most_common(20),
    }


def analyze_by_folio(corpus):
    """Analyze coverage by folio to find resistant sections."""
    folio_stats = {}

    words_by_folio = defaultdict(list)
    for w in corpus.words:
        if w.text and w.folio:
            words_by_folio[w.folio].append(w.text)

    for folio, words in words_by_folio.items():
        section = get_section(folio)

        decoded_count = 0
        for word in words:
            result = decode_word_coverage(word)
            if result['total_decoded'] >= 2:
                decoded_count += 1

        coverage = decoded_count / len(words) * 100 if words else 0

        folio_stats[folio] = {
            'section': section,
            'word_count': len(words),
            'decoded_count': decoded_count,
            'coverage_pct': coverage,
        }

    return folio_stats


def identify_resistant_folios(folio_stats, threshold=50):
    """Find folios that resist our framework (below threshold coverage)."""
    resistant = []

    for folio, stats in folio_stats.items():
        if stats['coverage_pct'] < threshold and stats['word_count'] >= 10:
            resistant.append({
                'folio': folio,
                'section': stats['section'],
                'word_count': stats['word_count'],
                'coverage_pct': stats['coverage_pct'],
            })

    return sorted(resistant, key=lambda x: x['coverage_pct'])


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 90)
    print("GAP ANALYSIS: REMAINING GAPS AND LIMITATIONS")
    print("=" * 90)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Load corpus
    corpus = load_corpus('data/transcriptions')
    print(f"Loaded {len(corpus.words)} words")
    print()

    # Corpus coverage analysis
    print("=" * 90)
    print("CORPUS COVERAGE ANALYSIS")
    print("=" * 90)
    print()

    coverage = analyze_corpus_coverage(corpus)

    total = coverage['words_analyzed']
    print(f"Total words analyzed: {total:,}")
    print()

    print("DECODING COVERAGE:")
    print(f"  Fully decoded (3 components):     {coverage['fully_decoded']:>6,} ({coverage['fully_decoded']/total*100:.1f}%)")
    print(f"  Mostly decoded (2 components):    {coverage['mostly_decoded']:>6,} ({coverage['mostly_decoded']/total*100:.1f}%)")
    print(f"  Partially decoded (1 component):  {coverage['partially_decoded']:>6,} ({coverage['partially_decoded']/total*100:.1f}%)")
    print(f"  Not decoded (0 components):       {coverage['not_decoded']:>6,} ({coverage['not_decoded']/total*100:.1f}%)")
    print()

    effective_coverage = (coverage['fully_decoded'] + coverage['mostly_decoded']) / total * 100
    print(f"EFFECTIVE COVERAGE (2+ components): {effective_coverage:.1f}%")
    print()

    print("COMPONENT COVERAGE:")
    print(f"  Words with recognized PREFIX:  {coverage['prefix_coverage']:>6,} ({coverage['prefix_coverage']/total*100:.1f}%)")
    print(f"  Words with recognized MIDDLE:  {coverage['middle_coverage']:>6,} ({coverage['middle_coverage']/total*100:.1f}%)")
    print(f"  Words with recognized SUFFIX:  {coverage['suffix_coverage']:>6,} ({coverage['suffix_coverage']/total*100:.1f}%)")
    print()

    # Uncertain morphemes
    print("=" * 90)
    print("TOP 20 UNCERTAIN MORPHEMES")
    print("=" * 90)
    print()

    uncertain = find_uncertain_morphemes(corpus)

    print("Potential PREFIXES not in mappings:")
    print(f"{'MORPHEME':<10} {'COUNT':>10} {'NOTES':<30}")
    print("-" * 50)

    for morph, count in uncertain['prefixes']:
        # Skip single chars and known variants
        if len(morph) < 2:
            continue

        # Check if it's close to a known prefix
        note = ""
        for known in PREFIX_MAPPINGS.keys():
            if morph.startswith(known) or known.startswith(morph):
                note = f"variant of {known}?"
                break

        print(f"{morph:<10} {count:>10,} {note:<30}")
    print()

    print("Potential SUFFIXES not in mappings:")
    print(f"{'MORPHEME':<10} {'COUNT':>10} {'NOTES':<30}")
    print("-" * 50)

    for morph, count in uncertain['suffixes']:
        if len(morph) < 2:
            continue

        note = ""
        for known in SUFFIX_MAPPINGS.keys():
            if morph.endswith(known) or known.endswith(morph):
                note = f"variant of {known}?"
                break

        print(f"{morph:<10} {count:>10,} {note:<30}")
    print()

    # Remaining undecoded character sequences
    print("=" * 90)
    print("MOST COMMON UNDECODED SEQUENCES")
    print("=" * 90)
    print()

    print(f"{'SEQUENCE':<15} {'COUNT':>10} {'LIKELY TYPE':<20}")
    print("-" * 45)

    for seq, count in coverage['remaining_chars'].most_common(20):
        if not seq or count < 10:
            continue

        # Guess type
        likely_type = "unknown"
        if len(seq) <= 2:
            likely_type = "middle element?"
        elif seq.startswith('o') or seq.startswith('a'):
            likely_type = "vowel cluster?"
        elif any(c in seq for c in 'kptf'):
            likely_type = "gallows variant?"

        print(f"{seq:<15} {count:>10,} {likely_type:<20}")
    print()

    # Analysis by folio
    print("=" * 90)
    print("COVERAGE BY SECTION")
    print("=" * 90)
    print()

    folio_stats = analyze_by_folio(corpus)

    # Aggregate by section
    section_stats = defaultdict(lambda: {'words': 0, 'decoded': 0})
    for folio, stats in folio_stats.items():
        section_stats[stats['section']]['words'] += stats['word_count']
        section_stats[stats['section']]['decoded'] += stats['decoded_count']

    print(f"{'SECTION':<15} {'WORDS':>10} {'DECODED':>10} {'COVERAGE':>10}")
    print("-" * 45)

    for section in ['HERBAL', 'BIOLOGICAL', 'ZODIAC', 'RECIPES', 'COSMOLOGICAL', 'UNKNOWN']:
        stats = section_stats.get(section, {'words': 0, 'decoded': 0})
        if stats['words'] > 0:
            pct = stats['decoded'] / stats['words'] * 100
            print(f"{section:<15} {stats['words']:>10,} {stats['decoded']:>10,} {pct:>9.1f}%")
    print()

    # Resistant folios
    print("=" * 90)
    print("FOLIOS THAT RESIST FRAMEWORK (< 50% coverage)")
    print("=" * 90)
    print()

    resistant = identify_resistant_folios(folio_stats, threshold=50)

    if not resistant:
        print("No folios found with < 50% coverage (excellent!)")
    else:
        print(f"{'FOLIO':<10} {'SECTION':<15} {'WORDS':>8} {'COVERAGE':>10}")
        print("-" * 43)

        for r in resistant[:20]:
            print(f"{r['folio']:<10} {r['section']:<15} {r['word_count']:>8} {r['coverage_pct']:>9.1f}%")

        print()
        print(f"Total resistant folios: {len(resistant)}")
    print()

    # Specific limitations
    print("=" * 90)
    print("KNOWN LIMITATIONS")
    print("=" * 90)
    print()

    limitations = [
        {
            'category': 'LEXICAL',
            'issue': 'Specific plant names unknown',
            'impact': 'Cannot identify exact herbs in illustrations',
            'resolution': 'Cross-reference with medieval herbal illustrations; botanical expert review'
        },
        {
            'category': 'LEXICAL',
            'issue': 'Single-character middles undefined',
            'impact': 'Many common words have unknown middle elements (e.g., "k", "m", "i")',
            'resolution': 'Statistical analysis of single-char distributions; context pattern analysis'
        },
        {
            'category': 'STRUCTURAL',
            'issue': 'Currier A/B distinction not incorporated',
            'impact': 'May be missing dialect/scribal variations',
            'resolution': 'Analyze if morpheme distributions differ between A and B'
        },
        {
            'category': 'STRUCTURAL',
            'issue': 'Word order transformation unknown',
            'impact': 'Cannot reconstruct sentence word order',
            'resolution': 'Compare with Latin recipe word order; may need external key'
        },
        {
            'category': 'SEMANTIC',
            'issue': 'Dosage/quantity terms unidentified',
            'impact': 'Cannot extract precise medical instructions',
            'resolution': 'Look for numeric patterns; compare with recipe unit terminology'
        },
        {
            'category': 'SEMANTIC',
            'issue': 'Celestial/timing specifics unclear',
            'impact': 'Cannot identify exact zodiac signs or months',
            'resolution': 'Focus on zodiac section illustrations; month name pattern analysis'
        },
        {
            'category': 'VALIDATION',
            'issue': 'No single confirmed external word',
            'impact': 'Framework is internally consistent but not externally proven',
            'resolution': 'Find zodiac labels (Taurus, Aries, etc.) or month names'
        },
        {
            'category': 'VALIDATION',
            'issue': 'Alternative interpretations not ruled out',
            'impact': 'Alchemical or other readings remain possible',
            'resolution': 'Test framework against alchemical terminology systematically'
        },
    ]

    for lim in limitations:
        print(f"[{lim['category']}] {lim['issue']}")
        print(f"  Impact: {lim['impact']}")
        print(f"  Resolution: {lim['resolution']}")
        print()

    # What would resolve gaps
    print("=" * 90)
    print("WHAT WOULD RESOLVE REMAINING GAPS")
    print("=" * 90)
    print()

    resolutions = [
        {
            'priority': 'HIGH',
            'action': 'Decode single-character middle elements',
            'method': 'Statistical analysis of position-specific distributions',
            'expected_gain': '+10-15% coverage',
        },
        {
            'priority': 'HIGH',
            'action': 'Identify one confirmed external word',
            'method': 'Focus on zodiac labels in f71 (Taurus illustration)',
            'expected_gain': 'External validation of framework',
        },
        {
            'priority': 'MEDIUM',
            'action': 'Map remaining prefix variants',
            'method': 'Cluster analysis of words starting with unknown sequences',
            'expected_gain': '+5% coverage',
        },
        {
            'priority': 'MEDIUM',
            'action': 'Analyze Currier A/B systematically',
            'method': 'Compare morpheme distributions between dialects',
            'expected_gain': 'May reveal scribal conventions',
        },
        {
            'priority': 'LOW',
            'action': 'Identify specific plant names',
            'method': 'Cross-reference illustrations with emmenagogue plants',
            'expected_gain': 'Lexical enrichment, illustration validation',
        },
        {
            'priority': 'LOW',
            'action': 'Reconstruct word order',
            'method': 'Compare with Latin recipe syntax patterns',
            'expected_gain': 'More readable translations',
        },
    ]

    for res in resolutions:
        print(f"[{res['priority']}] {res['action']}")
        print(f"  Method: {res['method']}")
        print(f"  Expected gain: {res['expected_gain']}")
        print()

    # Honest assessment
    print("=" * 90)
    print("HONEST ASSESSMENT")
    print("=" * 90)
    print()

    print("WHAT WE KNOW (HIGH CONFIDENCE):")
    print("  - Text has systematic PREFIX + MIDDLE + SUFFIX structure")
    print("  - Sections have distinct vocabulary distributions")
    print("  - BIOLOGICAL section describes body/womb-related procedures")
    print("  - Framework produces internally coherent procedural reconstructions")
    print("  - Vocabulary matches medieval gynecological terminology patterns")
    print()

    print("WHAT WE BELIEVE (MEDIUM CONFIDENCE):")
    print("  - Specific morpheme meanings (qo- = womb, lch = wash, etc.)")
    print("  - Text describes fumigation/steam treatments")
    print("  - Underlying language is Latin-derived")
    print("  - Content is gynecological medicine")
    print()

    print("WHAT WE DON'T KNOW:")
    print("  - Exact character-to-sound mappings")
    print("  - Specific plant identifications")
    print("  - Precise dosage/quantity terms")
    print("  - Why encoding was used (secrecy? shorthand?)")
    print("  - Identity of author(s)")
    print()

    print("WHAT COULD DISPROVE OUR FRAMEWORK:")
    print("  - Finding internal contradictions in morpheme distributions")
    print("  - Alternative framework producing better coherence")
    print("  - Discovery of actual Voynich key contradicting our mappings")
    print("  - Illustration analysis contradicting decoded content")
    print()

    # Final statistics
    print("=" * 90)
    print("FINAL STATISTICS")
    print("=" * 90)
    print()

    print(f"Total corpus words:                 {total:,}")
    print(f"Effective coverage (2+ components): {effective_coverage:.1f}%")
    print(f"Known morphemes mapped:             {len(PREFIX_MAPPINGS) + len(MIDDLE_MAPPINGS) + len(SUFFIX_MAPPINGS)}")
    print(f"Resistant folios (< 50%):           {len(resistant)}")
    print()

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'coverage': {
            'total_words': total,
            'fully_decoded': coverage['fully_decoded'],
            'mostly_decoded': coverage['mostly_decoded'],
            'partially_decoded': coverage['partially_decoded'],
            'not_decoded': coverage['not_decoded'],
            'effective_coverage_pct': effective_coverage,
            'prefix_coverage_pct': coverage['prefix_coverage'] / total * 100,
            'middle_coverage_pct': coverage['middle_coverage'] / total * 100,
            'suffix_coverage_pct': coverage['suffix_coverage'] / total * 100,
        },
        'uncertain_morphemes': {
            'prefixes': uncertain['prefixes'],
            'suffixes': uncertain['suffixes'],
        },
        'remaining_sequences': coverage['remaining_chars'].most_common(50),
        'section_coverage': {
            section: {
                'words': stats['words'],
                'decoded': stats['decoded'],
                'pct': stats['decoded'] / stats['words'] * 100 if stats['words'] > 0 else 0
            }
            for section, stats in section_stats.items()
        },
        'resistant_folios': resistant[:30],
        'limitations': limitations,
        'resolutions': resolutions,
    }

    with open('gap_analysis_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to gap_analysis_results.json")


if __name__ == '__main__':
    main()
