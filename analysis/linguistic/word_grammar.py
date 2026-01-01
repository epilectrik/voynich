"""
Voynich Word Grammar Decomposition

Analyzes the prefix-middle-suffix structure of Voynich words to find
patterns that might reveal encoding rules or semantic content.

Based on research showing Voynich words follow a strict grammar:
    [INITIAL/PREFIX] + [MIDDLE/CORE] + [SUFFIX/ENDING]
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus


# Known Voynich word components based on frequency analysis
KNOWN_PREFIXES = [
    'qok', 'qot', 'qo',  # q-initial words
    'che', 'cho', 'ch',   # ch-initial
    'she', 'sho', 'sh',   # sh-initial
    'cth', 'ct',          # ct-initial
    'dai', 'da', 'd',     # d-initial
    'ot', 'ok', 'ol', 'o', # o-initial
    's', 'y', 'l', 'k', 'a', 't', 'p', 'f'  # single char
]

KNOWN_SUFFIXES = [
    'aiin', 'ain', 'iin',  # -iin family
    'eedy', 'edy', 'dy',   # -dy family
    'eey', 'ey', 'hy', 'y', # -y family
    'ar', 'or', 'ir',      # -r family
    'al', 'ol', 'el',      # -l family
    'am', 'an', 'in',      # -n/m family
    's', 'm', 'n', 'l', 'r', 'd'  # single char
]

# Common middle components
KNOWN_MIDDLES = [
    'ok', 'ot', 'ol',
    'eo', 'ee', 'ai',
    'ke', 'ka', 'ko',
    'ch', 'sh', 'th',
    'e', 'a', 'o', 'i'
]


@dataclass
class WordDecomposition:
    """Result of decomposing a Voynich word."""
    word: str
    prefix: str
    middle: str
    suffix: str
    confidence: float  # How well it fits the grammar


def decompose_word(word: str) -> WordDecomposition:
    """
    Decompose a Voynich word into prefix-middle-suffix.
    Uses longest-match for prefix and suffix.
    """
    if not word:
        return WordDecomposition(word, '', '', '', 0.0)

    # Find longest matching prefix
    prefix = ''
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if word.startswith(p):
            prefix = p
            break

    # Find longest matching suffix
    suffix = ''
    remaining_for_suffix = word[len(prefix):] if prefix else word
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if remaining_for_suffix.endswith(s):
            suffix = s
            break

    # Middle is what's left
    if prefix or suffix:
        start = len(prefix)
        end = len(word) - len(suffix) if suffix else len(word)
        middle = word[start:end]
    else:
        middle = word

    # Calculate confidence based on how much of the word we recognized
    recognized = len(prefix) + len(suffix)
    confidence = recognized / len(word) if word else 0.0

    return WordDecomposition(word, prefix, middle, suffix, confidence)


def analyze_components(words: List[str]) -> Dict:
    """Analyze word components across a corpus."""
    decompositions = [decompose_word(w) for w in words]

    prefix_counts = Counter(d.prefix for d in decompositions if d.prefix)
    suffix_counts = Counter(d.suffix for d in decompositions if d.suffix)
    middle_counts = Counter(d.middle for d in decompositions if d.middle)

    # Find prefix-suffix co-occurrences
    prefix_suffix_pairs = Counter(
        (d.prefix, d.suffix) for d in decompositions
        if d.prefix and d.suffix
    )

    # Calculate coverage
    total = len(words)
    has_prefix = sum(1 for d in decompositions if d.prefix)
    has_suffix = sum(1 for d in decompositions if d.suffix)
    has_both = sum(1 for d in decompositions if d.prefix and d.suffix)

    avg_confidence = sum(d.confidence for d in decompositions) / total if total > 0 else 0

    return {
        'total_words': total,
        'prefix_coverage': has_prefix / total if total > 0 else 0,
        'suffix_coverage': has_suffix / total if total > 0 else 0,
        'both_coverage': has_both / total if total > 0 else 0,
        'avg_confidence': avg_confidence,
        'prefix_counts': prefix_counts,
        'suffix_counts': suffix_counts,
        'middle_counts': middle_counts,
        'prefix_suffix_pairs': prefix_suffix_pairs,
        'decompositions': decompositions
    }


def analyze_by_section(corpus) -> Dict[str, Dict]:
    """Analyze word components by manuscript section."""
    section_words = defaultdict(list)

    for word in corpus.words:
        section_words[word.section].append(word.text)

    results = {}
    for section, words in section_words.items():
        if words:
            results[section] = analyze_components(words)

    return results


def find_semantic_patterns(section_analysis: Dict[str, Dict]) -> Dict:
    """
    Look for patterns that suggest semantic meaning in components.
    If certain prefixes/suffixes are more common in specific sections,
    they might carry meaning related to that section's content.
    """
    # Normalize component frequencies per section
    section_patterns = {}

    for section, analysis in section_analysis.items():
        total = analysis['total_words']
        if total < 100:  # Skip small sections
            continue

        # Get top prefixes for this section
        top_prefixes = {p: c/total for p, c in analysis['prefix_counts'].most_common(10)}
        top_suffixes = {s: c/total for s, c in analysis['suffix_counts'].most_common(10)}

        section_patterns[section] = {
            'top_prefixes': top_prefixes,
            'top_suffixes': top_suffixes,
            'total': total
        }

    # Find prefixes/suffixes that vary significantly between sections
    all_prefixes = set()
    all_suffixes = set()
    for sp in section_patterns.values():
        all_prefixes.update(sp['top_prefixes'].keys())
        all_suffixes.update(sp['top_suffixes'].keys())

    # Calculate variance for each component
    prefix_variance = {}
    for prefix in all_prefixes:
        rates = [sp['top_prefixes'].get(prefix, 0) for sp in section_patterns.values()]
        if len(rates) > 1:
            mean = sum(rates) / len(rates)
            variance = sum((r - mean) ** 2 for r in rates) / len(rates)
            prefix_variance[prefix] = (variance, mean, rates)

    suffix_variance = {}
    for suffix in all_suffixes:
        rates = [sp['top_suffixes'].get(suffix, 0) for sp in section_patterns.values()]
        if len(rates) > 1:
            mean = sum(rates) / len(rates)
            variance = sum((r - mean) ** 2 for r in rates) / len(rates)
            suffix_variance[suffix] = (variance, mean, rates)

    return {
        'section_patterns': section_patterns,
        'prefix_variance': sorted(prefix_variance.items(), key=lambda x: -x[1][0]),
        'suffix_variance': sorted(suffix_variance.items(), key=lambda x: -x[1][0])
    }


def main():
    print("Loading Voynich corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))
    print(f"Loaded {len(corpus.words)} words\n")

    # Overall analysis
    print("=" * 80)
    print("WORD GRAMMAR ANALYSIS")
    print("=" * 80)

    overall = analyze_components(corpus.all_words)

    print(f"\nCoverage Statistics:")
    print(f"  Words with recognized prefix: {overall['prefix_coverage']*100:.1f}%")
    print(f"  Words with recognized suffix: {overall['suffix_coverage']*100:.1f}%")
    print(f"  Words with both: {overall['both_coverage']*100:.1f}%")
    print(f"  Average confidence: {overall['avg_confidence']*100:.1f}%")

    print(f"\nTop 15 Prefixes:")
    for prefix, count in overall['prefix_counts'].most_common(15):
        pct = 100 * count / overall['total_words']
        print(f"  '{prefix}': {count:>5,} ({pct:>5.1f}%)")

    print(f"\nTop 15 Suffixes:")
    for suffix, count in overall['suffix_counts'].most_common(15):
        pct = 100 * count / overall['total_words']
        print(f"  '{suffix}': {count:>5,} ({pct:>5.1f}%)")

    print(f"\nTop 15 Middles:")
    for middle, count in overall['middle_counts'].most_common(15):
        pct = 100 * count / overall['total_words']
        print(f"  '{middle}': {count:>5,} ({pct:>5.1f}%)")

    print(f"\nTop 15 Prefix-Suffix Pairs:")
    for (prefix, suffix), count in overall['prefix_suffix_pairs'].most_common(15):
        pct = 100 * count / overall['total_words']
        print(f"  {prefix:>5} + {suffix:<6}: {count:>5,} ({pct:>5.1f}%)")

    # Section analysis
    print("\n" + "=" * 80)
    print("ANALYSIS BY SECTION")
    print("=" * 80)

    section_analysis = analyze_by_section(corpus)
    semantic = find_semantic_patterns(section_analysis)

    section_names = {
        'H': 'Herbal', 'A': 'Astronomical', 'B': 'Biological',
        'C': 'Cosmological', 'P': 'Pharmaceutical', 'S': 'Stars/Recipe',
        'Z': 'Zodiac', 'T': 'Text'
    }

    for section, sp in semantic['section_patterns'].items():
        name = section_names.get(section, section)
        print(f"\n{section} ({name}) - {sp['total']} words:")
        print(f"  Top prefixes: ", end="")
        for p, rate in list(sp['top_prefixes'].items())[:5]:
            print(f"'{p}':{rate*100:.1f}% ", end="")
        print()
        print(f"  Top suffixes: ", end="")
        for s, rate in list(sp['top_suffixes'].items())[:5]:
            print(f"'{s}':{rate*100:.1f}% ", end="")
        print()

    # Components that vary most between sections
    print("\n" + "=" * 80)
    print("COMPONENTS WITH HIGHEST VARIANCE BETWEEN SECTIONS")
    print("(These might carry section-specific semantic meaning)")
    print("=" * 80)

    print("\nPrefixes with high variance:")
    for prefix, (var, mean, rates) in semantic['prefix_variance'][:10]:
        print(f"  '{prefix}': variance={var:.4f}, mean={mean*100:.1f}%")

    print("\nSuffixes with high variance:")
    for suffix, (var, mean, rates) in semantic['suffix_variance'][:10]:
        print(f"  '{suffix}': variance={var:.4f}, mean={mean*100:.1f}%")

    # Example decompositions
    print("\n" + "=" * 80)
    print("EXAMPLE WORD DECOMPOSITIONS")
    print("=" * 80)

    example_words = ['daiin', 'chedy', 'qokeedy', 'shol', 'otaiin',
                     'chol', 'qokain', 'shedy', 'okeey', 'chor']
    print(f"\n{'Word':<12} {'Prefix':<8} {'Middle':<10} {'Suffix':<8} {'Conf':<6}")
    print("-" * 50)
    for word in example_words:
        d = decompose_word(word)
        print(f"{d.word:<12} {d.prefix:<8} {d.middle:<10} {d.suffix:<8} {d.confidence:.2f}")


if __name__ == "__main__":
    main()
