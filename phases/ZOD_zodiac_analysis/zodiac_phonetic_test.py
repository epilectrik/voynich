#!/usr/bin/env python3
"""
Zodiac Phonetic Test

Test whether zodiac-unique words phonetically match constellation/month names.
Includes critical control comparison against non-zodiac folios.

NO SEMANTIC ASSUMPTIONS - purely phonetic pattern matching.
"""

import csv
import json
import random
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any


# Constellation names in multiple languages
CONSTELLATION_NAMES = {
    'Aries': {
        'latin': ['aries', 'arietis'],
        'italian': ['ariete'],
        'french': ['belier'],
        'german': ['widder']
    },
    'Taurus': {
        'latin': ['taurus', 'tauri'],
        'italian': ['toro'],
        'french': ['taureau'],
        'german': ['stier']
    },
    'Gemini': {
        'latin': ['gemini', 'geminorum'],
        'italian': ['gemelli'],
        'french': ['gemeaux'],
        'german': ['zwillinge']
    },
    'Cancer': {
        'latin': ['cancer', 'cancri'],
        'italian': ['cancro'],
        'french': ['cancer', 'ecrevisse'],
        'german': ['krebs']
    },
    'Leo': {
        'latin': ['leo', 'leonis'],
        'italian': ['leone'],
        'french': ['lion'],
        'german': ['lowe']
    },
    'Virgo': {
        'latin': ['virgo', 'virginis'],
        'italian': ['vergine'],
        'french': ['vierge'],
        'german': ['jungfrau']
    },
    'Libra': {
        'latin': ['libra', 'librae'],
        'italian': ['bilancia'],
        'french': ['balance'],
        'german': ['waage']
    },
    'Scorpio': {
        'latin': ['scorpio', 'scorpius', 'scorpionis'],
        'italian': ['scorpione'],
        'french': ['scorpion'],
        'german': ['skorpion']
    },
    'Sagittarius': {
        'latin': ['sagittarius', 'sagittarii'],
        'italian': ['sagittario'],
        'french': ['sagittaire'],
        'german': ['schutze']
    },
    'Capricorn': {
        'latin': ['capricornus', 'capricorni'],
        'italian': ['capricorno'],
        'french': ['capricorne'],
        'german': ['steinbock']
    },
    'Aquarius': {
        'latin': ['aquarius', 'aquarii'],
        'italian': ['acquario'],
        'french': ['verseau'],
        'german': ['wassermann']
    },
    'Pisces': {
        'latin': ['pisces', 'piscium'],
        'italian': ['pesci'],
        'french': ['poissons'],
        'german': ['fische']
    }
}

# Month names
MONTH_NAMES = {
    'January': {
        'latin': ['ianuarius', 'januarius'],
        'italian': ['gennaio'],
        'french': ['janvier'],
        'german': ['januar']
    },
    'February': {
        'latin': ['februarius'],
        'italian': ['febbraio'],
        'french': ['fevrier'],
        'german': ['februar']
    },
    'March': {
        'latin': ['martius', 'mars'],
        'italian': ['marzo'],
        'french': ['mars'],
        'german': ['marz']
    },
    'April': {
        'latin': ['aprilis'],
        'italian': ['aprile'],
        'french': ['avril'],
        'german': ['april']
    },
    'May': {
        'latin': ['maius'],
        'italian': ['maggio'],
        'french': ['mai'],
        'german': ['mai']
    },
    'June': {
        'latin': ['iunius', 'junius'],
        'italian': ['giugno'],
        'french': ['juin'],
        'german': ['juni']
    },
    'July': {
        'latin': ['iulius', 'julius'],
        'italian': ['luglio'],
        'french': ['juillet'],
        'german': ['juli']
    },
    'August': {
        'latin': ['augustus'],
        'italian': ['agosto'],
        'french': ['aout'],
        'german': ['august']
    },
    'September': {
        'latin': ['september'],
        'italian': ['settembre'],
        'french': ['septembre'],
        'german': ['september']
    },
    'October': {
        'latin': ['october'],
        'italian': ['ottobre'],
        'french': ['octobre'],
        'german': ['oktober']
    },
    'November': {
        'latin': ['november'],
        'italian': ['novembre'],
        'french': ['novembre'],
        'german': ['november']
    },
    'December': {
        'latin': ['december'],
        'italian': ['dicembre'],
        'french': ['decembre'],
        'german': ['dezember']
    }
}

# Zodiac-to-month mapping (approximate)
ZODIAC_MONTHS = {
    'Aries': ['March', 'April'],
    'Taurus': ['April', 'May'],
    'Gemini': ['May', 'June'],
    'Cancer': ['June', 'July'],
    'Leo': ['July', 'August'],
    'Virgo': ['August', 'September'],
    'Libra': ['September', 'October'],
    'Scorpio': ['October', 'November'],
    'Sagittarius': ['November', 'December'],
    'Capricorn': ['December', 'January'],
    'Aquarius': ['January', 'February'],
    'Pisces': ['February', 'March']
}

# Plant names for control comparison
PLANT_NAMES = [
    'artemisia', 'belladonna', 'calendula', 'digitalis', 'euphorbia',
    'foeniculum', 'gentiana', 'helleborus', 'iris', 'juniperus',
    'lavandula', 'mandragora', 'nasturtium', 'origanum', 'papaver',
    'quercus', 'rosmarinus', 'salvia', 'thymus', 'urtica', 'valeriana',
    'wormwood', 'yarrow', 'zingiber', 'aloe', 'basil', 'chamomile',
    'dill', 'elder', 'fennel', 'ginger', 'hyssop', 'ivy', 'jasmine'
]


def phonetic_score(voynich: str, target: str) -> float:
    """
    Score phonetic similarity between Voynich word and target word.
    Returns score from 0-5.

    Uses generous matching:
    - Match consonants in order
    - Allow vowel shifts
    - Partial credit for partial matches
    """
    # Clean inputs - remove special characters
    v_clean = ''.join(c for c in voynich.lower() if c.isalpha())
    t_clean = ''.join(c for c in target.lower() if c.isalpha())

    if not v_clean or not t_clean:
        return 0.0

    # Extract consonant sequences
    vowels = set('aeiou')
    v_consonants = [c for c in v_clean if c not in vowels]
    t_consonants = [c for c in t_clean if c not in vowels]

    # Match consonants using longest common subsequence approach
    def lcs_length(seq1, seq2):
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        return dp[m][n]

    consonant_matches = lcs_length(v_consonants, t_consonants)
    max_consonants = max(len(v_consonants), len(t_consonants))

    # Also match vowel patterns loosely
    v_vowels = [c for c in v_clean if c in vowels]
    t_vowels = [c for c in t_clean if c in vowels]
    vowel_matches = lcs_length(v_vowels, t_vowels)
    max_vowels = max(len(v_vowels), len(t_vowels)) if v_vowels or t_vowels else 1

    # Combined score (consonants weighted more heavily)
    if max_consonants == 0:
        consonant_score = 0
    else:
        consonant_score = consonant_matches / max_consonants

    vowel_score = vowel_matches / max_vowels if max_vowels > 0 else 0

    # Length penalty for very different lengths
    len_ratio = min(len(v_clean), len(t_clean)) / max(len(v_clean), len(t_clean))

    # Combined score (0-5 scale)
    raw_score = (consonant_score * 0.6 + vowel_score * 0.2 + len_ratio * 0.2) * 5

    return round(raw_score, 2)


def load_zodiac_unique_words() -> Dict:
    """Load zodiac unique words from previous extraction."""
    with open('zodiac_unique_words.json', 'r') as f:
        return json.load(f)


def load_corpus_for_control() -> Tuple[Dict[str, List[str]], Dict[str, Set[str]]]:
    """Load corpus for control comparison."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'

    folio_words = defaultdict(list)
    word_folios = defaultdict(set)

    seen = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # CRITICAL: Filter to H-only transcriber track
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip().strip('"')
            folio = row.get('folio', '').strip().strip('"')
            line_num = row.get('line_number', '').strip().strip('"')

            if not word or word.startswith('*') or len(word) < 2:
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                folio_words[folio].append(word)
                word_folios[word].add(folio)

    return dict(folio_words), dict(word_folios)


def get_single_folio_words_for_folio(folio: str, folio_words: Dict, word_folios: Dict) -> List[str]:
    """Get words that appear only on the specified folio."""
    if folio not in folio_words:
        return []
    return [w for w in set(folio_words[folio]) if word_folios.get(w, set()) == {folio}]


def test_zodiac_matches(zodiac_data: Dict, folio_words: Dict, word_folios: Dict) -> Dict:
    """Test phonetic matches for zodiac folios."""
    results = {}

    # Zodiac folio to sign mapping
    folio_map = zodiac_data['zodiac_folio_mapping']

    for folio, sign in folio_map.items():
        candidates = get_single_folio_words_for_folio(folio, folio_words, word_folios)

        if not candidates:
            continue

        best_constellation_match = None
        best_month_match = None

        # Get constellation names for this sign
        sign_names = CONSTELLATION_NAMES.get(sign, {})

        # Get month names for this sign
        sign_months = ZODIAC_MONTHS.get(sign, [])
        month_name_options = []
        for month in sign_months:
            month_name_options.extend(MONTH_NAMES.get(month, {}).values())
        month_name_options = [name for sublist in month_name_options for name in sublist]

        # Test each candidate against constellation names
        for word in candidates:
            for lang, names in sign_names.items():
                for target in names:
                    score = phonetic_score(word, target)
                    if best_constellation_match is None or score > best_constellation_match['score']:
                        best_constellation_match = {
                            'voynich_word': word,
                            'target': target,
                            'language': lang,
                            'sign': sign,
                            'score': score
                        }

            # Test against month names
            for target in month_name_options:
                score = phonetic_score(word, target)
                if best_month_match is None or score > best_month_match['score']:
                    best_month_match = {
                        'voynich_word': word,
                        'target': target,
                        'score': score
                    }

        results[folio] = {
            'zodiac_sign': sign,
            'candidates_tested': len(candidates),
            'best_constellation_match': best_constellation_match,
            'best_month_match': best_month_match
        }

    return results


def test_control_matches(folio_words: Dict, word_folios: Dict, num_folios: int = 12) -> Dict:
    """Test phonetic matches for random herbal folios (control)."""
    # Get herbal folios (f1-f66, excluding zodiac range)
    herbal_folios = [f for f in folio_words.keys()
                     if f.startswith('f') and not f.startswith('f6') and not f.startswith('f7')]
    herbal_folios = [f for f in herbal_folios
                     if any(f.startswith(f'f{i}') for i in range(1, 56))]

    # Random sample
    random.seed(42)  # Reproducible
    if len(herbal_folios) > num_folios:
        selected_folios = random.sample(herbal_folios, num_folios)
    else:
        selected_folios = herbal_folios

    results = {}

    for folio in selected_folios:
        candidates = get_single_folio_words_for_folio(folio, folio_words, word_folios)

        if not candidates:
            continue

        best_plant_match = None

        # Test each candidate against plant names
        for word in candidates:
            for plant in PLANT_NAMES:
                score = phonetic_score(word, plant)
                if best_plant_match is None or score > best_plant_match['score']:
                    best_plant_match = {
                        'voynich_word': word,
                        'target': plant,
                        'score': score
                    }

        results[folio] = {
            'candidates_tested': len(candidates),
            'best_plant_match': best_plant_match
        }

    return results


def compare_results(zodiac_results: Dict, control_results: Dict) -> Dict:
    """Compare zodiac matches to control matches."""
    # Get constellation match scores
    zodiac_scores = [r['best_constellation_match']['score']
                     for r in zodiac_results.values()
                     if r['best_constellation_match']]

    # Get control match scores
    control_scores = [r['best_plant_match']['score']
                      for r in control_results.values()
                      if r['best_plant_match']]

    if not zodiac_scores:
        zodiac_avg = 0
        zodiac_max = 0
    else:
        zodiac_avg = sum(zodiac_scores) / len(zodiac_scores)
        zodiac_max = max(zodiac_scores)

    if not control_scores:
        control_avg = 0
        control_max = 0
    else:
        control_avg = sum(control_scores) / len(control_scores)
        control_max = max(control_scores)

    # Count high matches (score >= 3.0)
    zodiac_high = sum(1 for s in zodiac_scores if s >= 3.0)
    control_high = sum(1 for s in control_scores if s >= 3.0)

    # Count very high matches (score >= 4.0)
    zodiac_very_high = sum(1 for s in zodiac_scores if s >= 4.0)
    control_very_high = sum(1 for s in control_scores if s >= 4.0)

    # Determine verdict
    if zodiac_avg > control_avg + 0.5 and zodiac_high >= 3:
        verdict = 'YES'
        explanation = f'Zodiac matches significantly better (avg {zodiac_avg:.2f} vs {control_avg:.2f})'
    elif zodiac_avg > control_avg + 0.2 and zodiac_high >= 2:
        verdict = 'WEAK_YES'
        explanation = f'Zodiac matches slightly better (avg {zodiac_avg:.2f} vs {control_avg:.2f})'
    elif abs(zodiac_avg - control_avg) <= 0.2:
        verdict = 'NO'
        explanation = f'No difference between zodiac and control (both ~{(zodiac_avg + control_avg)/2:.2f})'
    else:
        verdict = 'INCONCLUSIVE'
        explanation = 'Mixed results'

    return {
        'zodiac_statistics': {
            'folios_tested': len(zodiac_results),
            'average_best_score': round(zodiac_avg, 2),
            'max_score': round(zodiac_max, 2),
            'high_matches_gte_3': zodiac_high,
            'very_high_matches_gte_4': zodiac_very_high
        },
        'control_statistics': {
            'folios_tested': len(control_results),
            'average_best_score': round(control_avg, 2),
            'max_score': round(control_max, 2),
            'high_matches_gte_3': control_high,
            'very_high_matches_gte_4': control_very_high
        },
        'comparison': {
            'avg_difference': round(zodiac_avg - control_avg, 2),
            'zodiac_better': zodiac_avg > control_avg,
            'significance': 'Significant' if abs(zodiac_avg - control_avg) > 0.5 else 'Not significant'
        },
        'verdict': verdict,
        'explanation': explanation
    }


def main():
    print("=" * 70)
    print("ZODIAC PHONETIC TEST")
    print("Test phonetic matches for zodiac labels with control comparison")
    print("NO SEMANTIC ASSUMPTIONS - purely phonetic pattern matching")
    print("=" * 70)
    print()

    # Load data
    print("Loading zodiac extraction data...")
    zodiac_data = load_zodiac_unique_words()

    print("Loading corpus for control comparison...")
    folio_words, word_folios = load_corpus_for_control()

    # Test zodiac matches
    print("\n" + "=" * 50)
    print("TESTING ZODIAC FOLIOS")
    print("=" * 50)

    zodiac_results = test_zodiac_matches(zodiac_data, folio_words, word_folios)

    print("\n--- BEST CONSTELLATION MATCHES ---")
    for folio, data in sorted(zodiac_results.items()):
        match = data['best_constellation_match']
        if match:
            print(f"{folio} ({data['zodiac_sign']}): '{match['voynich_word']}' ~ '{match['target']}' ({match['language']}) = {match['score']:.2f}")

    print("\n--- BEST MONTH MATCHES ---")
    for folio, data in sorted(zodiac_results.items()):
        match = data['best_month_match']
        if match:
            print(f"{folio} ({data['zodiac_sign']}): '{match['voynich_word']}' ~ '{match['target']}' = {match['score']:.2f}")

    # Test control matches
    print("\n" + "=" * 50)
    print("TESTING CONTROL FOLIOS (HERBAL SECTION)")
    print("=" * 50)

    control_results = test_control_matches(folio_words, word_folios)

    print("\n--- BEST PLANT MATCHES ---")
    for folio, data in sorted(control_results.items()):
        match = data['best_plant_match']
        if match:
            print(f"{folio}: '{match['voynich_word']}' ~ '{match['target']}' = {match['score']:.2f}")

    # Compare results
    print("\n" + "=" * 70)
    print("COMPARISON AND VERDICT")
    print("=" * 70)

    comparison = compare_results(zodiac_results, control_results)

    print("\n--- ZODIAC STATISTICS ---")
    stats = comparison['zodiac_statistics']
    print(f"Folios tested: {stats['folios_tested']}")
    print(f"Average best score: {stats['average_best_score']}")
    print(f"Maximum score: {stats['max_score']}")
    print(f"High matches (>= 3.0): {stats['high_matches_gte_3']}")
    print(f"Very high matches (>= 4.0): {stats['very_high_matches_gte_4']}")

    print("\n--- CONTROL STATISTICS ---")
    stats = comparison['control_statistics']
    print(f"Folios tested: {stats['folios_tested']}")
    print(f"Average best score: {stats['average_best_score']}")
    print(f"Maximum score: {stats['max_score']}")
    print(f"High matches (>= 3.0): {stats['high_matches_gte_3']}")
    print(f"Very high matches (>= 4.0): {stats['very_high_matches_gte_4']}")

    print("\n--- COMPARISON ---")
    print(f"Average difference (zodiac - control): {comparison['comparison']['avg_difference']}")
    print(f"Zodiac better than control: {comparison['comparison']['zodiac_better']}")
    print(f"Statistical significance: {comparison['comparison']['significance']}")

    print("\n" + "=" * 70)
    print(f"VERDICT: {comparison['verdict']}")
    print(f"Explanation: {comparison['explanation']}")
    print("=" * 70)

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'methodology': 'Zodiac phonetic test with control comparison',
        'zodiac_matches': zodiac_results,
        'control_matches': control_results,
        'comparison': comparison
    }

    with open('zodiac_phonetic_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to zodiac_phonetic_test_results.json")


if __name__ == '__main__':
    main()
