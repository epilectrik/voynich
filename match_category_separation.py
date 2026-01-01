#!/usr/bin/env python3
"""
TASK 6: Separate Match Categories Clearly

The expert noted we mixed lexical, structural, and thematic matches together.

Re-analyze Trotula correspondence with strict separation:

LEXICAL (highest standard):
- Exact word-to-word correspondence
- Same grammatical form
- Same procedural context

STRUCTURAL (medium standard):
- Same procedural template (PLANT then PROCESS then BODY)
- Same transition grammar
- Different specific vocabulary

THEMATIC (lowest standard):
- Same general subject matter
- Same domain (gynecology, fumigation)
- No specific correspondence

Only LEXICAL matches count as strong external validation.
"""

import json
from collections import defaultdict, Counter
from datetime import datetime

# =============================================================================
# TROTULA VOCABULARY (Documented Latin terms)
# =============================================================================

# LEXICAL TARGET: Exact word matches required
TROTULA_LEXICAL = {
    # Fumigation procedures
    'fumigatio': {'meaning': 'fumigation', 'context': 'vaginal steaming procedure'},
    'suffumigatio': {'meaning': 'fumigation from below', 'context': 'vaginal steam'},
    'subfumigate': {'meaning': 'to fumigate from below', 'context': 'treatment verb'},

    # Womb terms
    'matrix': {'meaning': 'womb', 'context': 'uterus'},
    'uterus': {'meaning': 'womb', 'context': 'uterus'},
    'vulva': {'meaning': 'vulva', 'context': 'external genitalia'},
    'os matricis': {'meaning': 'mouth of womb', 'context': 'cervix'},

    # Menstrual terms
    'menstrua': {'meaning': 'menses', 'context': 'menstrual blood'},
    'menstruatio': {'meaning': 'menstruation', 'context': 'monthly bleeding'},
    'purgatio': {'meaning': 'purgation', 'context': 'menstrual cleansing'},
    'provocare menstrua': {'meaning': 'to provoke menses', 'context': 'emmenagogue'},

    # Preparation terms
    'decoctio': {'meaning': 'decoction', 'context': 'boiled preparation'},
    'pessarium': {'meaning': 'pessary', 'context': 'vaginal suppository'},
    'balneum': {'meaning': 'bath', 'context': 'bathing treatment'},
    'lotio': {'meaning': 'washing', 'context': 'cleansing'},
    'unctio': {'meaning': 'anointing', 'context': 'oil application'},
}

# STRUCTURAL TARGET: Procedural template matches
TROTULA_TEMPLATES = {
    'FUMIGATION_PROCEDURE': {
        'pattern': 'HEAT + HERB + CONTAINER -> BODY_TARGET',
        'example': 'calefacere herbam in vase -> ad matricem',
        'voynich_equivalent': 'ke + ch + aiin -> qo',
    },
    'WASH_PROCEDURE': {
        'pattern': 'WASH + SUBSTANCE + BODY',
        'example': 'lavare cum aqua -> vulvam',
        'voynich_equivalent': 'lch + cth + qo',
    },
    'PREPARE_REMEDY': {
        'pattern': 'PREPARE + PLANT + MEDIUM',
        'example': 'praeparare herbam in oleo',
        'voynich_equivalent': 'tch + ch + ol',
    },
    'APPLY_TREATMENT': {
        'pattern': 'APPLY + MEDICINE + TARGET',
        'example': 'applicare medicamentum ad matricem',
        'voynich_equivalent': 'pch + (remedy) + qo',
    },
    'HEAT_SUBSTANCE': {
        'pattern': 'HEAT + SUBSTANCE + STATE',
        'example': 'calefacere succum -> calidum',
        'voynich_equivalent': 'ke + sh + chol',
    },
}

# THEMATIC TARGET: General domain matches
TROTULA_THEMES = [
    'gynecological treatment',
    'menstrual regulation',
    'fertility',
    'fumigation',
    'vaginal treatment',
    'womb health',
    'herbal preparation',
    'bathing procedure',
    'medical astrology timing',
    'humoral medicine',
]

# =============================================================================
# VOYNICH DECODED VOCABULARY
# =============================================================================

VOYNICH_DECODED = {
    # Claimed lexical correspondences
    'qo': {'claimed_meaning': 'womb', 'claimed_latin': 'matrix'},
    'ol': {'claimed_meaning': 'menses', 'claimed_latin': 'menstrua'},
    'qoke': {'claimed_meaning': 'womb-heat', 'claimed_latin': 'calefacere matricem'},
    'qokedy': {'claimed_meaning': 'fumigated', 'claimed_latin': 'fumigatum'},
    'lchedy': {'claimed_meaning': 'washed', 'claimed_latin': 'lotum'},
    'tchedy': {'claimed_meaning': 'prepared', 'claimed_latin': 'praeparatum'},
    'cthedy': {'claimed_meaning': 'purified', 'claimed_latin': 'purificatum'},
    'chedy': {'claimed_meaning': 'dried herb', 'claimed_latin': 'herba sicca'},
    'shedy': {'claimed_meaning': 'herb juice', 'claimed_latin': 'succus herbae'},
    'daiin': {'claimed_meaning': 'leaves', 'claimed_latin': 'folia'},
    'chol': {'claimed_meaning': 'hot', 'claimed_latin': 'calidus'},
    'keedy': {'claimed_meaning': 'heating', 'claimed_latin': 'calefaciens'},
}

# Sample corpus for testing
VOYNICH_CORPUS = [
    # High-frequency words
    'daiin', 'ol', 'chedy', 'qokedy', 'shedy', 'qokeedy', 'ar', 'chol',
    'or', 'qokey', 'okedy', 'okeedy', 'sho', 'dal', 'shy', 'otar',
    'otal', 'chor', 'shol', 'otaly', 'qokain', 'oly', 'chey', 'dain',
    'oteedy', 'cthy', 'dar', 'cheedy', 'olkeedy', 'qol', 'oky', 'aiin',
    'aiiin', 'otaiin', 'cthar', 'shor', 'sholy', 'cholar', 'okoldy', 'qotar',
    'lchedy', 'tchedy', 'cthedy', 'kchedy', 'ckhedy', 'pchedy',
    'qolchedy', 'oltchedy', 'qocthedy',
] * 100  # Repeat for frequency

# =============================================================================
# STRICT MATCHING ANALYSIS
# =============================================================================

def check_lexical_matches():
    """
    LEXICAL: Strictest standard
    - Must have exact word-to-word correspondence
    - Same grammatical form
    - Same procedural context
    """
    matches = []

    for voynich, data in VOYNICH_DECODED.items():
        claimed_latin = data.get('claimed_latin', '')

        # Check if claimed Latin exists in Trotula
        for trotula_term, trotula_data in TROTULA_LEXICAL.items():
            # Exact match check
            if claimed_latin.lower() == trotula_term.lower():
                matches.append({
                    'type': 'EXACT',
                    'voynich': voynich,
                    'claimed': claimed_latin,
                    'trotula': trotula_term,
                    'context': trotula_data['context'],
                    'strength': 'STRONG',
                })
            # Partial match (root word)
            elif claimed_latin.split()[0].lower() in trotula_term.lower():
                matches.append({
                    'type': 'PARTIAL',
                    'voynich': voynich,
                    'claimed': claimed_latin,
                    'trotula': trotula_term,
                    'context': trotula_data['context'],
                    'strength': 'WEAK',
                })

    return matches

def check_structural_matches():
    """
    STRUCTURAL: Medium standard
    - Same procedural template
    - Same transition grammar
    - Different specific vocabulary allowed
    """
    matches = []

    # Define Voynich procedural patterns
    voynich_patterns = {
        'FUMIGATION': {
            'regex': r'qoke|qokee',
            'template': 'BODY + HEAT',
            'count': 0,
        },
        'WASHING': {
            'regex': r'lch',
            'template': 'WASH action',
            'count': 0,
        },
        'PREPARATION': {
            'regex': r'tch|ckh|kch',
            'template': 'PREPARE action',
            'count': 0,
        },
        'HEATING': {
            'regex': r'ke[^e]|kee',
            'template': 'HEAT action',
            'count': 0,
        },
        'BODY_TARGET': {
            'regex': r'^qo',
            'template': 'WOMB target',
            'count': 0,
        },
        'MENSES_CONTEXT': {
            'regex': r'^ol',
            'template': 'MENSES context',
            'count': 0,
        },
    }

    import re

    for word in VOYNICH_CORPUS:
        for pattern_name, pattern_data in voynich_patterns.items():
            if re.search(pattern_data['regex'], word):
                pattern_data['count'] += 1

    # Match to Trotula templates
    for pattern_name, pattern_data in voynich_patterns.items():
        if pattern_data['count'] > 0:
            for template_name, template_data in TROTULA_TEMPLATES.items():
                # Check if pattern aligns with template
                if pattern_name.upper() in template_name.upper():
                    matches.append({
                        'voynich_pattern': pattern_name,
                        'voynich_count': pattern_data['count'],
                        'trotula_template': template_name,
                        'template_description': template_data['pattern'],
                        'alignment': 'STRUCTURAL',
                    })
                elif pattern_name == 'BODY_TARGET' and 'BODY' in template_data['pattern']:
                    matches.append({
                        'voynich_pattern': pattern_name,
                        'voynich_count': pattern_data['count'],
                        'trotula_template': template_name,
                        'template_description': template_data['pattern'],
                        'alignment': 'PARTIAL',
                    })

    return matches

def check_thematic_matches():
    """
    THEMATIC: Lowest standard
    - Same general subject matter
    - Same domain
    - No specific correspondence required
    """
    matches = []

    # Count words by semantic domain
    domains = {
        'gynecological': 0,
        'menstrual': 0,
        'fumigation': 0,
        'herbal': 0,
        'preparation': 0,
    }

    for word in VOYNICH_CORPUS:
        if 'qo' in word:
            domains['gynecological'] += 1
        if 'ol' in word and not word.startswith('chol'):
            domains['menstrual'] += 1
        if 'qoke' in word or 'qokee' in word:
            domains['fumigation'] += 1
        if word.startswith('ch') or word.startswith('sh') or word.startswith('da'):
            domains['herbal'] += 1
        if any(p in word for p in ['lch', 'tch', 'cth', 'kch', 'ckh']):
            domains['preparation'] += 1

    total = len(VOYNICH_CORPUS)

    for domain, count in domains.items():
        if count > 0:
            for theme in TROTULA_THEMES:
                if domain in theme.lower():
                    matches.append({
                        'voynich_domain': domain,
                        'voynich_count': count,
                        'voynich_rate': count / total,
                        'trotula_theme': theme,
                        'match_type': 'THEMATIC',
                    })

    return matches

def main():
    print("=" * 70)
    print("MATCH CATEGORY SEPARATION")
    print("Strict re-analysis of Trotula correspondence")
    print("=" * 70)

    # LEXICAL matches
    print("\n" + "=" * 50)
    print("LEXICAL MATCHES (Highest Standard)")
    print("=" * 50)
    print("Criteria: Exact word-to-word, same form, same context")

    lexical = check_lexical_matches()
    exact_lexical = [m for m in lexical if m['type'] == 'EXACT']
    partial_lexical = [m for m in lexical if m['type'] == 'PARTIAL']

    print(f"\n  EXACT matches: {len(exact_lexical)}")
    for m in exact_lexical:
        print(f"    {m['voynich']} -> {m['claimed']} = {m['trotula']} ({m['context']})")

    print(f"\n  PARTIAL matches: {len(partial_lexical)}")
    for m in partial_lexical[:5]:
        print(f"    {m['voynich']} -> {m['claimed']} ~ {m['trotula']} ({m['strength']})")

    # STRUCTURAL matches
    print("\n" + "=" * 50)
    print("STRUCTURAL MATCHES (Medium Standard)")
    print("=" * 50)
    print("Criteria: Same procedural template, different vocabulary OK")

    structural = check_structural_matches()
    structural_aligned = [m for m in structural if m['alignment'] == 'STRUCTURAL']
    structural_partial = [m for m in structural if m['alignment'] == 'PARTIAL']

    print(f"\n  ALIGNED templates: {len(structural_aligned)}")
    for m in structural_aligned:
        print(f"    Voynich {m['voynich_pattern']} ({m['voynich_count']}x) -> Trotula {m['trotula_template']}")
        print(f"      Template: {m['template_description']}")

    print(f"\n  PARTIAL templates: {len(structural_partial)}")
    for m in structural_partial[:5]:
        print(f"    Voynich {m['voynich_pattern']} ~ Trotula {m['trotula_template']}")

    # THEMATIC matches
    print("\n" + "=" * 50)
    print("THEMATIC MATCHES (Lowest Standard)")
    print("=" * 50)
    print("Criteria: Same general domain, no specific correspondence")

    thematic = check_thematic_matches()

    print(f"\n  Domain overlaps: {len(thematic)}")
    unique_domains = set(m['voynich_domain'] for m in thematic)
    for domain in unique_domains:
        domain_matches = [m for m in thematic if m['voynich_domain'] == domain]
        if domain_matches:
            m = domain_matches[0]
            print(f"    {m['voynich_domain']}: {m['voynich_count']} words ({m['voynich_rate']:.1%})")
            print(f"      Matches theme: {m['trotula_theme']}")

    # Summary
    print("\n" + "=" * 70)
    print("CATEGORY SUMMARY")
    print("=" * 70)

    print(f"""
  LEXICAL (strongest evidence):
    Exact matches:   {len(exact_lexical)}
    Partial matches: {len(partial_lexical)}

  STRUCTURAL (moderate evidence):
    Aligned templates: {len(structural_aligned)}
    Partial templates: {len(structural_partial)}

  THEMATIC (weakest evidence):
    Domain overlaps: {len(unique_domains)}
""")

    # Assessment
    print("\n" + "-" * 50)
    print("VALIDATION ASSESSMENT")
    print("-" * 50)

    if len(exact_lexical) >= 3:
        print("""
  LEXICAL VALIDATION: STRONG
  Multiple exact word correspondences found.
  This provides genuine external validation.
""")
    elif len(exact_lexical) >= 1:
        print("""
  LEXICAL VALIDATION: MODERATE
  Some exact correspondences, but limited.
  Requires additional confirmation.
""")
    else:
        print("""
  LEXICAL VALIDATION: WEAK
  No exact word-to-word correspondences confirmed.
  Our claimed meanings remain INTERNALLY CONSISTENT but not EXTERNALLY VALIDATED.

  CRITICAL ISSUE:
  All our "Trotula matches" are based on OUR OWN claimed meanings.
  We claim qo = womb, then check if Trotula has "womb" words.
  This is CIRCULAR - it validates our claims against themselves.

  WHAT WOULD BE STRONG:
  - Finding a Voynich sequence that phonetically matches a Latin word
  - Example: If "otaur" = "taurus" (zodiac label)
  - Example: If "chero" = "cera" (wax)

  WE DO NOT HAVE THIS.
""")

    if len(structural_aligned) >= 3:
        print("""
  STRUCTURAL VALIDATION: MODERATE
  Procedural templates align between Voynich and Trotula.
  This suggests similar medical text structure.
  However, this could reflect GENERAL medieval recipe format,
  not specifically Trotula correspondence.
""")
    else:
        print("""
  STRUCTURAL VALIDATION: WEAK
  Limited template alignment.
  May reflect general procedural text structure rather than specific correspondence.
""")

    print("""
  THEMATIC VALIDATION: INHERENTLY WEAK
  Thematic overlap only shows both texts discuss similar topics.
  This is expected if both are medical texts - not distinctive.
  Cannot distinguish gynecological from general medical vocabulary.
""")

    # Honest conclusion
    print("\n" + "-" * 50)
    print("HONEST CONCLUSION:")
    print("-" * 50)

    print("""
  Our "34,000+ Trotula matches" were THEMATIC, not LEXICAL.

  WHAT WE CLAIMED:
  - 34,592 total matches
  - 8,628 "exact" matches
  - 13,189 "structural" matches

  WHAT WE ACTUALLY HAVE:
  - LEXICAL (exact word): {exact} (strict definition)
  - STRUCTURAL (same template): {struct}
  - THEMATIC (same domain): Everything else

  The high match numbers came from counting every word that
  contained a morpheme we mapped to a gynecological concept.
  This is CIRCULAR VALIDATION.

  PROPER VALIDATION REQUIRES:
  1. Finding words that PHONETICALLY match external vocabulary
  2. Finding patterns that CANNOT be explained by chance
  3. Having INDEPENDENT scholars verify matches

  Until we have these, our Trotula correspondence is:
  - Suggestive but not probative
  - Based on internal consistency, not external proof
  - Subject to the same criticism as all Voynich "solutions"
""".format(exact=len(exact_lexical), struct=len(structural_aligned)))

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'lexical_matches': {
            'exact': len(exact_lexical),
            'partial': len(partial_lexical),
            'details': exact_lexical,
        },
        'structural_matches': {
            'aligned': len(structural_aligned),
            'partial': len(structural_partial),
            'details': structural_aligned,
        },
        'thematic_matches': {
            'domain_count': len(unique_domains),
            'details': thematic[:10],  # Sample
        },
        'assessment': {
            'lexical': 'WEAK' if len(exact_lexical) < 1 else 'MODERATE' if len(exact_lexical) < 3 else 'STRONG',
            'structural': 'WEAK' if len(structural_aligned) < 3 else 'MODERATE',
            'thematic': 'INHERENTLY_WEAK',
            'overall': 'CIRCULAR_VALIDATION - no external proof',
        },
    }

    with open('match_separation_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to match_separation_results.json")

    return output

if __name__ == "__main__":
    main()
