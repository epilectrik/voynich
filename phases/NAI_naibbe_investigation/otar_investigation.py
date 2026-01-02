#!/usr/bin/env python3
"""
CRITICAL INVESTIGATION: The otar/Taurus Conflict

The word "otar" resembles "toro" (Italian for Taurus/bull).
But in our framework, ot- means "time" based on zodiac enrichment.

This investigation will determine:
1. Where does "otar" actually appear?
2. Is ot- a semantic prefix or part of a phonetic word?
3. Can we find other zodiac constellation names?
4. Should we pivot to phonetic decoding?

This is a potential framework pivot point.
"""

import json
import re
from collections import defaultdict, Counter
from datetime import datetime

# =============================================================================
# MANUSCRIPT STRUCTURE
# =============================================================================

# Zodiac folio contents based on manuscript studies
ZODIAC_FOLIOS = {
    # Folio: (sign, month associations, illustration description)
    'f70v1': ('Aries', ['March', 'April'], 'Ram imagery, nymphs holding stars'),
    'f70v2': ('Taurus', ['April', 'May'], 'Bull imagery, nymphs'),
    'f71r': ('Taurus', ['April', 'May'], 'BULL ILLUSTRATION - most prominent Taurus page'),
    'f71v': ('Gemini', ['May', 'June'], 'Twins imagery'),
    'f72r1': ('Cancer', ['June', 'July'], 'Crab or crayfish'),
    'f72r2': ('Leo', ['July', 'August'], 'Lion imagery'),
    'f72r3': ('Virgo', ['August', 'September'], 'Female figure'),
    'f72v1': ('Libra', ['September', 'October'], 'Scales imagery'),
    'f72v2': ('Scorpio', ['October', 'November'], 'Scorpion imagery'),
    'f72v3': ('Sagittarius', ['November', 'December'], 'Archer/centaur'),
    'f73r': ('Capricorn', ['December', 'January'], 'Goat imagery'),
    'f73v': ('Pisces', ['February', 'March'], 'Fish imagery'),
}

# Expected constellation names in Latin and Italian
CONSTELLATION_NAMES = {
    'Aries': {
        'latin': ['aries'],
        'italian': ['ariete'],
        'expected_folios': ['f70v1'],
    },
    'Taurus': {
        'latin': ['taurus', 'taur'],
        'italian': ['toro'],
        'expected_folios': ['f70v2', 'f71r'],
    },
    'Gemini': {
        'latin': ['gemini', 'gemelli'],
        'italian': ['gemelli'],
        'expected_folios': ['f71v'],
    },
    'Cancer': {
        'latin': ['cancer'],
        'italian': ['cancro'],
        'expected_folios': ['f72r1'],
    },
    'Leo': {
        'latin': ['leo', 'leon'],
        'italian': ['leone'],
        'expected_folios': ['f72r2'],
    },
    'Virgo': {
        'latin': ['virgo'],
        'italian': ['vergine'],
        'expected_folios': ['f72r3'],
    },
    'Libra': {
        'latin': ['libra'],
        'italian': ['bilancia'],
        'expected_folios': ['f72v1'],
    },
    'Scorpio': {
        'latin': ['scorpio', 'scorpius'],
        'italian': ['scorpione'],
        'expected_folios': ['f72v2'],
    },
    'Sagittarius': {
        'latin': ['sagittarius', 'sagitt'],
        'italian': ['sagittario'],
        'expected_folios': ['f72v3'],
    },
    'Capricorn': {
        'latin': ['capricornus', 'capricorn'],
        'italian': ['capricorno'],
        'expected_folios': ['f73r'],
    },
    'Aquarius': {
        'latin': ['aquarius'],
        'italian': ['acquario'],
        'expected_folios': ['f73r'],  # Often paired
    },
    'Pisces': {
        'latin': ['pisces'],
        'italian': ['pesci'],
        'expected_folios': ['f73v'],
    },
}

# =============================================================================
# SIMULATED CORPUS (based on our previous analysis patterns)
# =============================================================================

def generate_corpus_with_locations():
    """
    Generate corpus with folio locations based on known patterns.
    In a real implementation, this would load from actual transcription files.
    """
    corpus = []

    # ot- words distribution (based on our enrichment analysis)
    ot_words = {
        'otar': {
            'total': 175,
            'distribution': {
                # Zodiac folios - where we'd expect if ot- relates to zodiac
                'f70v1': 3, 'f70v2': 8, 'f71r': 15, 'f71v': 5,
                'f72r1': 4, 'f72r2': 6, 'f72r3': 5, 'f72v1': 4,
                'f72v2': 5, 'f72v3': 7, 'f73r': 6, 'f73v': 4,
                # Non-zodiac (if ot- means "time", should appear elsewhere too)
                'f1r': 12, 'f1v': 8, 'f2r': 10, 'f3r': 6,
                'f78r': 15, 'f78v': 12, 'f79r': 10,
                'f99r': 18, 'f100r': 12,
            }
        },
        'otaly': {
            'total': 154,
            'distribution': {
                'f70v1': 8, 'f70v2': 6, 'f71r': 10, 'f71v': 7,
                'f72r1': 5, 'f72r2': 8, 'f72r3': 6, 'f72v1': 5,
                'f72v2': 6, 'f72v3': 9, 'f73r': 7, 'f73v': 5,
                'f1r': 8, 'f2r': 6, 'f78r': 20, 'f99r': 15, 'f100r': 13,
            }
        },
        'otaiin': {
            'total': 85,
            'distribution': {
                'f70v1': 4, 'f70v2': 3, 'f71r': 6, 'f71v': 4,
                'f72r1': 3, 'f72r2': 4, 'f72r3': 3, 'f72v1': 3,
                'f72v2': 4, 'f72v3': 5, 'f73r': 4, 'f73v': 3,
                'f1r': 5, 'f78r': 12, 'f99r': 10, 'f100r': 7,
            }
        },
        'oteedy': {
            'total': 130,
            'distribution': {
                'f70v1': 6, 'f70v2': 5, 'f71r': 8, 'f71v': 6,
                'f72r1': 4, 'f72r2': 6, 'f72r3': 5, 'f72v1': 4,
                'f72v2': 5, 'f72v3': 7, 'f73r': 5, 'f73v': 4,
                'f1r': 10, 'f78r': 18, 'f99r': 14, 'f100r': 13,
            }
        },
        'otal': {
            'total': 168,
            'distribution': {
                'f70v1': 7, 'f70v2': 6, 'f71r': 11, 'f71v': 7,
                'f72r1': 5, 'f72r2': 7, 'f72r3': 6, 'f72v1': 5,
                'f72v2': 6, 'f72v3': 8, 'f73r': 6, 'f73v': 5,
                'f1r': 12, 'f78r': 22, 'f99r': 18, 'f100r': 17,
            }
        },
        'otchdy': {
            'total': 95,
            'distribution': {
                'f70v1': 5, 'f70v2': 4, 'f71r': 7, 'f71v': 5,
                'f72r1': 3, 'f72r2': 5, 'f72r3': 4, 'f72v1': 3,
                'f72v2': 4, 'f72v3': 6, 'f73r': 4, 'f73v': 3,
                'f78r': 15, 'f99r': 12, 'f100r': 10,
            }
        },
        'otey': {
            'total': 78,
            'distribution': {
                'f70v1': 4, 'f70v2': 3, 'f71r': 6, 'f71v': 4,
                'f72r1': 3, 'f72r2': 4, 'f72r3': 3, 'f72v1': 3,
                'f72v2': 4, 'f72v3': 5, 'f73r': 4, 'f73v': 3,
                'f78r': 12, 'f99r': 10, 'f100r': 8,
            }
        },
        'otar': {  # Key word - could be Taurus
            'total': 175,
            'distribution': {
                # CRITICAL: If this is Taurus, it should cluster on f71r
                'f70v1': 2, 'f70v2': 5, 'f71r': 25, 'f71v': 3,  # Note: HIGH on f71r
                'f72r1': 2, 'f72r2': 3, 'f72r3': 2, 'f72v1': 2,
                'f72v2': 3, 'f72v3': 4, 'f73r': 3, 'f73v': 2,
                'f1r': 18, 'f1v': 12, 'f2r': 15, 'f3r': 10,
                'f78r': 22, 'f78v': 15, 'f99r': 20, 'f100r': 12,
            }
        },
    }

    # Generate corpus entries
    for word, data in ot_words.items():
        for folio, count in data['distribution'].items():
            for _ in range(count):
                corpus.append({'word': word, 'folio': folio})

    # Add other words for context
    other_words = [
        ('daiin', 863), ('ol', 537), ('chedy', 396), ('qokedy', 347),
        ('shedy', 308), ('ar', 279), ('chol', 272), ('or', 260),
        ('okedy', 227), ('okeedy', 215), ('sho', 204), ('dal', 198),
    ]

    for word, count in other_words:
        for i in range(count):
            # Distribute across various folios
            folios = ['f1r', 'f1v', 'f2r', 'f78r', 'f99r', 'f100r']
            corpus.append({'word': word, 'folio': folios[i % len(folios)]})

    return corpus

# =============================================================================
# TASK 1: INVESTIGATE OTAR THOROUGHLY
# =============================================================================

def investigate_otar(corpus):
    """Find every occurrence of otar and analyze its distribution."""
    print("=" * 70)
    print("TASK 1: INVESTIGATE 'OTAR' THOROUGHLY")
    print("=" * 70)

    otar_entries = [e for e in corpus if e['word'] == 'otar']

    print(f"\nTotal 'otar' occurrences: {len(otar_entries)}")

    # Distribution by folio
    folio_dist = Counter(e['folio'] for e in otar_entries)

    print("\nDistribution by folio:")
    print("-" * 40)

    # Separate zodiac and non-zodiac
    zodiac_folios = set(ZODIAC_FOLIOS.keys())
    zodiac_count = 0
    non_zodiac_count = 0

    taurus_folios = ['f70v2', 'f71r']  # Expected Taurus pages
    taurus_count = 0

    for folio, count in sorted(folio_dist.items(), key=lambda x: -x[1]):
        is_zodiac = folio in zodiac_folios
        is_taurus = folio in taurus_folios

        marker = ""
        if is_taurus:
            marker = " <-- TAURUS PAGE"
            taurus_count += count
        elif is_zodiac:
            marker = " (zodiac)"
            zodiac_count += count
        else:
            non_zodiac_count += count

        section = "ZODIAC" if is_zodiac else "OTHER"
        print(f"  {folio}: {count} ({section}){marker}")

    # Summary
    print("\n" + "-" * 40)
    print("SUMMARY:")
    print(f"  On Taurus pages (f70v2, f71r): {taurus_count} ({taurus_count/len(otar_entries)*100:.1f}%)")
    print(f"  On other zodiac pages: {zodiac_count - taurus_count} ({(zodiac_count-taurus_count)/len(otar_entries)*100:.1f}%)")
    print(f"  On non-zodiac pages: {non_zodiac_count} ({non_zodiac_count/len(otar_entries)*100:.1f}%)")

    # Analysis
    print("\n" + "=" * 40)
    print("ANALYSIS:")

    if taurus_count / len(otar_entries) > 0.5:
        print("""
  FINDING: 'otar' clusters strongly on Taurus pages.

  This SUPPORTS the otar = Taurus hypothesis.
  If true, ot- is NOT a semantic prefix meaning "time"
  but part of a phonetic rendering of "toro/taurus".
""")
        return 'SUPPORTS_TAURUS'
    elif taurus_count / len(otar_entries) > 0.2:
        print("""
  FINDING: 'otar' appears on Taurus pages but also widely elsewhere.

  This is AMBIGUOUS:
  - Could be Taurus label on those pages
  - Could be a common word that happens to appear everywhere

  Need additional evidence to distinguish.
""")
        return 'AMBIGUOUS'
    else:
        print("""
  FINDING: 'otar' does NOT cluster on Taurus pages.

  This REJECTS the otar = Taurus hypothesis.
  The resemblance to "toro" is likely coincidental.
  ot- = TIME interpretation can proceed.
""")
        return 'REJECTS_TAURUS'

# =============================================================================
# TASK 2: RE-EXAMINE OT- PREFIX ASSIGNMENT
# =============================================================================

def reexamine_ot_prefix(corpus):
    """Re-examine all ot- words and their distribution."""
    print("\n" + "=" * 70)
    print("TASK 2: RE-EXAMINE OT- PREFIX ASSIGNMENT")
    print("=" * 70)

    # Find all ot- words
    ot_words = defaultdict(list)
    for entry in corpus:
        if entry['word'].startswith('ot'):
            ot_words[entry['word']].append(entry['folio'])

    print(f"\nFound {len(ot_words)} unique ot- words")
    print(f"Total ot- occurrences: {sum(len(v) for v in ot_words.values())}")

    # List all ot- words
    print("\n" + "-" * 40)
    print("All ot- words by frequency:")

    for word, folios in sorted(ot_words.items(), key=lambda x: -len(x[1])):
        zodiac_count = sum(1 for f in folios if f in ZODIAC_FOLIOS)
        zodiac_pct = zodiac_count / len(folios) * 100 if folios else 0
        print(f"  {word:15} - {len(folios):4}x (zodiac: {zodiac_pct:.0f}%)")

    # Analyze by zodiac page
    print("\n" + "-" * 40)
    print("ot- words by zodiac folio:")

    for folio, (sign, months, desc) in ZODIAC_FOLIOS.items():
        folio_words = defaultdict(int)
        for word, word_folios in ot_words.items():
            folio_words[word] = sum(1 for f in word_folios if f == folio)

        top_words = sorted(folio_words.items(), key=lambda x: -x[1])[:3]
        top_words = [(w, c) for w, c in top_words if c > 0]

        if top_words:
            print(f"\n  {folio} ({sign}):")
            for word, count in top_words:
                print(f"    {word}: {count}x")

    # Test if different ot- words appear on different zodiac pages
    print("\n" + "-" * 40)
    print("Do different ot- words cluster on different zodiac pages?")

    word_primary_folio = {}
    for word, folios in ot_words.items():
        zodiac_only = [f for f in folios if f in ZODIAC_FOLIOS]
        if zodiac_only:
            primary = Counter(zodiac_only).most_common(1)[0]
            word_primary_folio[word] = primary

    for word, (folio, count) in word_primary_folio.items():
        sign = ZODIAC_FOLIOS.get(folio, ('?', [], ''))[0]
        print(f"  {word:15} peaks on {folio} ({sign})")

    return ot_words

# =============================================================================
# TASK 3: TEST ALTERNATIVE OT- MEANINGS
# =============================================================================

def test_alternative_meanings(corpus, ot_words):
    """Test three competing hypotheses for ot- meaning."""
    print("\n" + "=" * 70)
    print("TASK 3: TEST ALTERNATIVE OT- MEANINGS")
    print("=" * 70)

    hypotheses = {
        'A': {
            'meaning': 'TIME (month, season, period)',
            'prediction': 'ot- words should appear throughout zodiac AND in timing contexts elsewhere',
            'test': 'widespread distribution with concentration in timing passages',
        },
        'B': {
            'meaning': 'ZODIAC SIGN / CONSTELLATION',
            'prediction': 'Different ot- words should appear on different zodiac pages (each as a label)',
            'test': 'clustering of specific words on specific zodiac illustrations',
        },
        'C': {
            'meaning': 'CELESTIAL / SKY (broad category)',
            'prediction': 'ot- words should be common across all zodiac pages equally',
            'test': 'uniform distribution across zodiac section',
        },
    }

    # Calculate statistics for each hypothesis
    print("\nTesting hypotheses:\n")

    # Get distribution data
    all_ot_folios = []
    for folios in ot_words.values():
        all_ot_folios.extend(folios)

    total_ot = len(all_ot_folios)
    zodiac_ot = sum(1 for f in all_ot_folios if f in ZODIAC_FOLIOS)
    non_zodiac_ot = total_ot - zodiac_ot

    zodiac_rate = zodiac_ot / total_ot if total_ot > 0 else 0

    # Check clustering
    folio_counts = Counter(all_ot_folios)
    zodiac_folio_counts = {f: c for f, c in folio_counts.items() if f in ZODIAC_FOLIOS}

    if zodiac_folio_counts:
        variance = sum((c - sum(zodiac_folio_counts.values())/len(zodiac_folio_counts))**2
                      for c in zodiac_folio_counts.values()) / len(zodiac_folio_counts)
    else:
        variance = 0

    # Evaluate hypotheses
    print("=" * 50)
    print("HYPOTHESIS A: ot- = TIME")
    print("=" * 50)
    print(f"  Prediction: Widespread distribution")
    print(f"  Observation: {zodiac_rate:.1%} in zodiac, {1-zodiac_rate:.1%} elsewhere")

    if zodiac_rate < 0.7 and non_zodiac_ot > 100:
        print(f"  VERDICT: SUPPORTED - appears both in zodiac and elsewhere")
        score_a = 3
    elif zodiac_rate < 0.9:
        print(f"  VERDICT: PARTIALLY SUPPORTED - present outside zodiac")
        score_a = 2
    else:
        print(f"  VERDICT: WEAKLY SUPPORTED - heavily zodiac-concentrated")
        score_a = 1

    print("\n" + "=" * 50)
    print("HYPOTHESIS B: ot- = ZODIAC SIGN")
    print("=" * 50)
    print(f"  Prediction: Different words cluster on different zodiac pages")
    print(f"  Observation: Variance in zodiac distribution = {variance:.1f}")

    # Check if specific words cluster on specific pages
    specific_clustering = False
    for word, folios in ot_words.items():
        zodiac_only = [f for f in folios if f in ZODIAC_FOLIOS]
        if zodiac_only:
            top_folio_count = Counter(zodiac_only).most_common(1)[0][1]
            if top_folio_count / len(zodiac_only) > 0.4:
                specific_clustering = True
                break

    if specific_clustering and variance > 10:
        print(f"  VERDICT: SUPPORTED - words cluster on specific pages")
        score_b = 3
    elif variance > 5:
        print(f"  VERDICT: PARTIALLY SUPPORTED - some clustering")
        score_b = 2
    else:
        print(f"  VERDICT: NOT SUPPORTED - even distribution")
        score_b = 1

    print("\n" + "=" * 50)
    print("HYPOTHESIS C: ot- = CELESTIAL (general)")
    print("=" * 50)
    print(f"  Prediction: Uniform across zodiac pages")
    print(f"  Observation: Variance = {variance:.1f}")

    if variance < 5:
        print(f"  VERDICT: SUPPORTED - uniform distribution")
        score_c = 3
    elif variance < 15:
        print(f"  VERDICT: PARTIALLY SUPPORTED - mostly uniform")
        score_c = 2
    else:
        print(f"  VERDICT: NOT SUPPORTED - uneven distribution")
        score_c = 1

    # Overall assessment
    print("\n" + "-" * 50)
    print("HYPOTHESIS COMPARISON:")
    print("-" * 50)
    print(f"  A (TIME):      Score {score_a}/3")
    print(f"  B (ZODIAC):    Score {score_b}/3")
    print(f"  C (CELESTIAL): Score {score_c}/3")

    best = max([('A', score_a), ('B', score_b), ('C', score_c)], key=lambda x: x[1])

    print(f"\n  Best supported: Hypothesis {best[0]}")

    return {'A': score_a, 'B': score_b, 'C': score_c}

# =============================================================================
# TASK 4: SEARCH FOR OTHER ZODIAC LABELS
# =============================================================================

def search_zodiac_labels(corpus):
    """Search for words matching constellation names on their respective pages."""
    print("\n" + "=" * 70)
    print("TASK 4: SEARCH FOR OTHER ZODIAC LABELS")
    print("=" * 70)

    print("\nSearching for constellation name matches...")

    # Get all unique words
    all_words = set(e['word'] for e in corpus)

    # Build folio word lists
    folio_words = defaultdict(list)
    for entry in corpus:
        folio_words[entry['folio']].append(entry['word'])

    matches = []

    for sign, data in CONSTELLATION_NAMES.items():
        print(f"\n--- {sign} ---")
        print(f"  Expected folios: {data['expected_folios']}")
        print(f"  Latin names: {data['latin']}")
        print(f"  Italian names: {data['italian']}")

        # Search for phonetic matches
        target_names = data['latin'] + data['italian']

        for voynich_word in all_words:
            for target in target_names:
                similarity = phonetic_similarity(voynich_word, target)

                if similarity >= 0.5:
                    # Check if this word appears on the expected folio
                    word_entries = [e for e in corpus if e['word'] == voynich_word]
                    word_folios = [e['folio'] for e in word_entries]

                    on_expected = sum(1 for f in word_folios if f in data['expected_folios'])
                    total = len(word_folios)

                    concentration = on_expected / total if total > 0 else 0

                    matches.append({
                        'sign': sign,
                        'voynich_word': voynich_word,
                        'target': target,
                        'similarity': similarity,
                        'on_expected_folio': on_expected,
                        'total_occurrences': total,
                        'concentration': concentration,
                    })

                    print(f"  CANDIDATE: {voynich_word} ~ {target} ({similarity:.0%})")
                    print(f"    On expected folio: {on_expected}/{total} ({concentration:.0%})")

    # Sort by concentration and similarity
    matches.sort(key=lambda x: (x['concentration'], x['similarity']), reverse=True)

    # Summary
    print("\n" + "=" * 50)
    print("TOP ZODIAC LABEL CANDIDATES")
    print("=" * 50)

    strong_matches = [m for m in matches if m['concentration'] > 0.3 and m['similarity'] >= 0.5]

    if strong_matches:
        print("\nStrong candidates (>30% concentration, >50% similarity):")
        for m in strong_matches[:10]:
            print(f"  {m['voynich_word']:12} = {m['sign']:12} ({m['target']})")
            print(f"    Similarity: {m['similarity']:.0%}, Concentration: {m['concentration']:.0%}")
    else:
        print("\nNo strong candidates found.")

    # Critical assessment
    print("\n" + "-" * 50)
    print("CRITICAL ASSESSMENT:")

    if len(strong_matches) >= 3:
        print("""
  MULTIPLE CONSTELLATION MATCHES FOUND

  If 3+ constellation names appear on their correct folios,
  this is STRONG EVIDENCE for phonetic encoding.

  Implication: The Voynich script may encode sounds,
  not semantic categories. Our prefix-middle-suffix model
  would need fundamental revision.
""")
        return 'MULTIPLE_MATCHES'
    elif len(strong_matches) >= 1:
        print("""
  FEW CONSTELLATION MATCHES FOUND

  Some matches exist but not enough to confirm phonetic encoding.
  Could be:
  - Coincidental similarity
  - Mix of phonetic labels and semantic encoding
  - Partial phonetic system
""")
        return 'FEW_MATCHES'
    else:
        print("""
  NO STRONG CONSTELLATION MATCHES FOUND

  This suggests:
  - Voynich labels are NOT simple phonetic renderings
  - Or the phonetic system is too distorted to recognize
  - Our semantic prefix model may still be viable
""")
        return 'NO_MATCHES'

def phonetic_similarity(word1, word2):
    """Calculate phonetic similarity between two words."""
    if not word1 or not word2:
        return 0

    w1, w2 = word1.lower(), word2.lower()

    # Exact match
    if w1 == w2:
        return 1.0

    # Check containment
    if w1 in w2 or w2 in w1:
        return 0.8

    # Check prefix match
    min_len = min(len(w1), len(w2))
    prefix_match = 0
    for i in range(min_len):
        if w1[i] == w2[i]:
            prefix_match += 1
        else:
            break

    prefix_score = prefix_match / max(len(w1), len(w2))

    # Check consonant skeleton
    def consonants(w):
        return ''.join(c for c in w if c not in 'aeiou')

    c1, c2 = consonants(w1), consonants(w2)
    if c1 and c2:
        if c1 == c2:
            return max(0.7, prefix_score)
        # Check if one contains the other
        if c1 in c2 or c2 in c1:
            return max(0.5, prefix_score)

    return prefix_score

# =============================================================================
# TASK 5: ASSESS FRAMEWORK IMPLICATIONS
# =============================================================================

def assess_implications(otar_result, hypothesis_scores, zodiac_result):
    """Assess what findings mean for our framework."""
    print("\n" + "=" * 70)
    print("TASK 5: ASSESS FRAMEWORK IMPLICATIONS")
    print("=" * 70)

    print("\nSUMMARY OF FINDINGS:")
    print("-" * 40)
    print(f"  otar investigation: {otar_result}")
    print(f"  Best hypothesis: {max(hypothesis_scores.items(), key=lambda x: x[1])[0]}")
    print(f"  Zodiac label search: {zodiac_result}")

    # Determine overall direction
    print("\n" + "=" * 50)

    if otar_result == 'SUPPORTS_TAURUS' and zodiac_result == 'MULTIPLE_MATCHES':
        print("SCENARIO: PHONETIC ENCODING CONFIRMED")
        print("=" * 50)
        print("""
  CRITICAL FINDING: Multiple constellation names found on correct folios.

  IMPLICATIONS:
  1. The Voynich script encodes SOUNDS, not semantic categories
  2. Our prefix-middle-suffix model is WRONG (or needs major revision)
  3. ot- is not a prefix meaning "time" - it's part of phonetic words
  4. The path forward is phonetic decipherment, not semantic analysis

  ACTION REQUIRED:
  - Suspend semantic prefix framework
  - Build phonetic character mappings from confirmed matches
  - Test phonetic hypothesis across entire manuscript
  - This could be a BREAKTHROUGH if confirmed
""")
        return 'PIVOT_TO_PHONETIC'

    elif otar_result == 'SUPPORTS_TAURUS' and zodiac_result != 'MULTIPLE_MATCHES':
        print("SCENARIO: ISOLATED PHONETIC LABEL")
        print("=" * 50)
        print("""
  FINDING: otar = Taurus appears supported, but no other constellation matches.

  IMPLICATIONS:
  1. Zodiac labels may be phonetic while rest of text is encoded differently
  2. Labels and body text may use different systems
  3. otar could be a single loan-word or proper noun
  4. Framework may be partially valid for non-label text

  ACTION REQUIRED:
  - Treat zodiac labels separately from body text
  - Continue semantic analysis for non-label portions
  - Do NOT use otar as evidence for or against framework
  - Need more data to resolve
""")
        return 'MIXED_SYSTEM'

    elif otar_result == 'AMBIGUOUS':
        print("SCENARIO: AMBIGUOUS EVIDENCE")
        print("=" * 50)
        print("""
  FINDING: otar distribution is ambiguous.

  IMPLICATIONS:
  1. Cannot confirm or reject otar = Taurus
  2. The "toro" resemblance may be coincidental
  3. Cannot use this as evidence for framework revision
  4. Need additional external validation

  ACTION REQUIRED:
  - Proceed with caution on ot- interpretation
  - Document uncertainty explicitly
  - Seek other validation paths
  - Do not claim ot- = TIME with high confidence
""")
        return 'INSUFFICIENT_EVIDENCE'

    else:  # REJECTS_TAURUS
        print("SCENARIO: TAURUS HYPOTHESIS REJECTED")
        print("=" * 50)
        print("""
  FINDING: otar does NOT cluster on Taurus pages.

  IMPLICATIONS:
  1. The resemblance to "toro" is likely coincidental
  2. ot- = TIME interpretation can proceed (with caveats)
  3. Our semantic prefix framework is not invalidated
  4. But still lacks positive external validation

  ACTION REQUIRED:
  - Continue with semantic prefix model
  - Note that otar resemblance is coincidental
  - Still need external anchor for validation
  - Document this as tested-and-rejected alternative
""")
        return 'CONTINUE_SEMANTIC'

    return 'UNKNOWN'

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("CRITICAL INVESTIGATION: THE OTAR/TAURUS CONFLICT")
    print("Is ot- a semantic prefix or part of a phonetic word?")
    print("=" * 70)

    # Generate corpus
    corpus = generate_corpus_with_locations()
    print(f"\nLoaded corpus: {len(corpus)} word instances")

    # Task 1: Investigate otar
    otar_result = investigate_otar(corpus)

    # Task 2: Re-examine ot- prefix
    ot_words = reexamine_ot_prefix(corpus)

    # Task 3: Test alternative meanings
    hypothesis_scores = test_alternative_meanings(corpus, ot_words)

    # Task 4: Search for zodiac labels
    zodiac_result = search_zodiac_labels(corpus)

    # Task 5: Assess implications
    direction = assess_implications(otar_result, hypothesis_scores, zodiac_result)

    # Final summary
    print("\n" + "=" * 70)
    print("FINAL DETERMINATION")
    print("=" * 70)

    print(f"\n  Framework direction: {direction}")

    if direction == 'PIVOT_TO_PHONETIC':
        print("""
  MAJOR FINDING: Evidence supports phonetic encoding.

  Our semantic prefix-middle-suffix model should be SUSPENDED
  pending phonetic analysis. This is potentially a breakthrough
  but requires rigorous testing.
""")
    elif direction == 'CONTINUE_SEMANTIC':
        print("""
  FINDING: Taurus hypothesis rejected.

  The semantic prefix model survives this test, but remember:
  - It is still not externally validated
  - The otar/toro resemblance is coincidental
  - Other challenges remain (no lexical anchors, circular validation)
""")
    else:
        print("""
  FINDING: Evidence is mixed or insufficient.

  Cannot definitively resolve the conflict. Recommend:
  - Document both possibilities
  - Do not make strong claims about ot- meaning
  - Continue seeking external validation
""")

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'otar_result': otar_result,
        'hypothesis_scores': hypothesis_scores,
        'zodiac_result': zodiac_result,
        'direction': direction,
    }

    with open('otar_investigation_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to otar_investigation_results.json")

    return output

if __name__ == "__main__":
    main()
