"""
AAZ Probe: Measure A-vocabulary overlap with AZC folios.

Purpose: Determine if A↔AZC coordination phase is worth pursuing.

Outcomes:
- <10% overlap: Phase closes (decoupling confirmed)
- 10-30% overlap: Proceed with AAZ tests
- >30% overlap: Surprising, needs interpretation
"""

from collections import defaultdict
import json

def load_data():
    """Load token data from canonical source."""
    tokens_by_lang = defaultdict(list)
    tokens_by_folio = defaultdict(list)
    folio_lang = {}

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"')
                folio = parts[2].strip('"')
                section = parts[3].strip('"') if len(parts) > 3 else ''
                lang = parts[6].strip('"')

                if word and word != 'NA':
                    tokens_by_lang[lang].append(word)
                    tokens_by_folio[folio].append((word, lang, section))

                    if folio not in folio_lang:
                        folio_lang[folio] = lang

    return tokens_by_lang, tokens_by_folio, folio_lang

def identify_azc_folios(tokens_by_folio):
    """Identify AZC folios (those with NA/unclassified language in A/Z/C sections)."""
    azc_folios = set()
    azc_sections = {'A', 'Z', 'C'}  # Astronomical, Zodiac, Cosmological

    for folio, tokens in tokens_by_folio.items():
        for word, lang, section in tokens:
            if lang == 'NA' or lang == '':
                # Check if in AZC sections
                if section in azc_sections:
                    azc_folios.add(folio)
                    break

    return azc_folios

def is_clean_token(token):
    """Filter out damaged/artifact tokens (containing asterisks)."""
    return '*' not in token and token.isalpha() and len(token) >= 2

def compute_overlap(tokens_by_lang, tokens_by_folio, azc_folios):
    """Compute vocabulary overlap between Currier A and AZC."""

    # Get Currier A vocabulary (unique types) - CLEAN only
    a_vocab = set(t for t in tokens_by_lang['A'] if is_clean_token(t))

    # Get AZC vocabulary (tokens from AZC folios) - CLEAN only
    azc_tokens = []
    azc_vocab = set()
    for folio in azc_folios:
        for word, lang, section in tokens_by_folio[folio]:
            if is_clean_token(word):
                azc_tokens.append(word)
                azc_vocab.add(word)

    # Also get Currier B vocabulary for comparison - CLEAN only
    b_vocab = set(t for t in tokens_by_lang['B'] if is_clean_token(t))

    # Compute overlaps
    a_in_azc = a_vocab & azc_vocab
    b_in_azc = b_vocab & azc_vocab

    # AZC-unique vocabulary
    azc_unique = azc_vocab - a_vocab - b_vocab

    return {
        'a_vocab_size': len(a_vocab),
        'b_vocab_size': len(b_vocab),
        'azc_vocab_size': len(azc_vocab),
        'azc_token_count': len(azc_tokens),
        'a_in_azc': len(a_in_azc),
        'a_in_azc_pct': len(a_in_azc) / len(a_vocab) * 100 if a_vocab else 0,
        'b_in_azc': len(b_in_azc),
        'b_in_azc_pct': len(b_in_azc) / len(b_vocab) * 100 if b_vocab else 0,
        'azc_unique': len(azc_unique),
        'azc_unique_pct': len(azc_unique) / len(azc_vocab) * 100 if azc_vocab else 0,
        'azc_covered_by_a': len(a_in_azc) / len(azc_vocab) * 100 if azc_vocab else 0,
        'azc_covered_by_b': len(b_in_azc) / len(azc_vocab) * 100 if azc_vocab else 0,
        'azc_folios': sorted(azc_folios),
        'sample_a_in_azc': sorted(list(a_in_azc))[:20],
        'sample_azc_unique': sorted(list(azc_unique))[:20]
    }

def main():
    print("=" * 60)
    print("AAZ PROBE: A-vocabulary overlap with AZC")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    tokens_by_lang, tokens_by_folio, folio_lang = load_data()

    print(f"  Currier A tokens: {len(tokens_by_lang['A']):,}")
    print(f"  Currier B tokens: {len(tokens_by_lang['B']):,}")
    print(f"  Unclassified (NA) tokens: {len(tokens_by_lang['NA']):,}")

    # Identify AZC folios
    azc_folios = identify_azc_folios(tokens_by_folio)
    print(f"\nAZC folios identified: {len(azc_folios)}")

    # Compute overlap
    results = compute_overlap(tokens_by_lang, tokens_by_folio, azc_folios)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(f"\nVocabulary sizes:")
    print(f"  Currier A vocabulary: {results['a_vocab_size']:,} types")
    print(f"  Currier B vocabulary: {results['b_vocab_size']:,} types")
    print(f"  AZC vocabulary: {results['azc_vocab_size']:,} types")
    print(f"  AZC token count: {results['azc_token_count']:,}")

    print(f"\nA -> AZC overlap:")
    print(f"  A types appearing in AZC: {results['a_in_azc']:,}")
    print(f"  As % of A vocabulary: {results['a_in_azc_pct']:.1f}%")
    print(f"  As % of AZC vocabulary: {results['azc_covered_by_a']:.1f}%")

    print(f"\nB -> AZC overlap (for comparison):")
    print(f"  B types appearing in AZC: {results['b_in_azc']:,}")
    print(f"  As % of B vocabulary: {results['b_in_azc_pct']:.1f}%")
    print(f"  As % of AZC vocabulary: {results['azc_covered_by_b']:.1f}%")

    print(f"\nAZC-unique vocabulary:")
    print(f"  Types unique to AZC: {results['azc_unique']:,}")
    print(f"  As % of AZC vocabulary: {results['azc_unique_pct']:.1f}%")

    print(f"\nSample A types in AZC: {results['sample_a_in_azc']}")
    print(f"Sample AZC-unique types: {results['sample_azc_unique']}")

    # Decision
    print("\n" + "=" * 60)
    print("DECISION")
    print("=" * 60)

    a_pct = results['a_in_azc_pct']
    azc_covered = results['azc_covered_by_a']

    if a_pct < 10 and azc_covered < 10:
        verdict = "MINIMAL_OVERLAP"
        recommendation = "Phase CLOSES - A and AZC are decoupled systems"
    elif a_pct < 30 and azc_covered < 30:
        verdict = "MODERATE_OVERLAP"
        recommendation = "Proceed with AAZ tests - coordination worth testing"
    else:
        verdict = "HIGH_OVERLAP"
        recommendation = "Surprising result - needs careful interpretation"

    print(f"\nVerdict: {verdict}")
    print(f"Recommendation: {recommendation}")

    # Save results
    with open('archive/reports/aaz_probe_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to archive/reports/aaz_probe_results.json")

    return results

if __name__ == '__main__':
    main()
