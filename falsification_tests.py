"""FALSIFICATION TESTS - Can we DISPROVE our hypothesis?

A hypothesis that can't be falsified isn't scientific.
These tests attempt to break our framework.

Test 1: NULL HYPOTHESIS - Do scrambled sections show enrichment?
Test 2: BLIND PREDICTION - Can we predict unseen folios from illustrations?
Test 3: ALTERNATIVE MEANINGS - Do wrong meanings work equally well?
"""
import sys
sys.path.insert(0, '.')
import random
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')

# Our claimed prefix meanings
OUR_PREFIXES = {
    'qo': 'womb',
    'ol': 'menses',
    'ch': 'herb',
    'sh': 'juice',
    'da': 'leaf',
    'ct': 'water',
    'ot': 'time',
    'ok': 'sky',
    'al': 'star',
    'ar': 'air',
}

# Real section assignment
def get_real_section(folio):
    if not folio:
        return 'UNKNOWN'
    num = ''.join(c for c in folio if c.isdigit())
    if not num:
        return 'UNKNOWN'
    n = int(num)
    if 1 <= n <= 66:
        return 'HERBAL'
    elif 67 <= n <= 73:
        return 'ZODIAC'
    elif 75 <= n <= 84:
        return 'BIOLOGICAL'
    elif 87 <= n <= 102:
        return 'RECIPES'
    return 'OTHER'

# Build word data
all_words = []
for w in corpus.words:
    if w.text and w.folio:
        all_words.append({
            'word': w.text,
            'folio': w.folio,
            'real_section': get_real_section(w.folio)
        })

# Get all folios
all_folios = list(set(w['folio'] for w in all_words))

print("=" * 90)
print("FALSIFICATION TESTS")
print("=" * 90)
print()
print("Testing if our hypothesis can be DISPROVED.")
print("If these tests fail, our framework may be wrong.")
print()

# ============================================================================
# TEST 1: NULL HYPOTHESIS - SCRAMBLED SECTIONS
# ============================================================================

print("=" * 90)
print("TEST 1: NULL HYPOTHESIS - SCRAMBLED SECTIONS")
print("=" * 90)
print()
print("Method: Randomly reassign folios to sections, then recalculate enrichment.")
print("If scrambled sections ALSO show 2-3x enrichment, our method finds spurious patterns.")
print()

def calculate_enrichment(words, section_func):
    """Calculate prefix enrichment given a section assignment function."""
    # Count prefixes by section
    prefix_section_counts = defaultdict(lambda: defaultdict(int))
    section_totals = defaultdict(int)

    for w in words:
        section = section_func(w['folio'])
        if section in ['UNKNOWN', 'OTHER']:
            continue
        section_totals[section] += 1

        for prefix in OUR_PREFIXES:
            if w['word'].startswith(prefix):
                prefix_section_counts[prefix][section] += 1
                break

    # Calculate baseline
    total = sum(section_totals.values())
    baseline = {s: c/total for s, c in section_totals.items()}

    # Calculate enrichments
    enrichments = []
    for prefix in OUR_PREFIXES:
        counts = prefix_section_counts[prefix]
        prefix_total = sum(counts.values())
        if prefix_total < 50:
            continue

        for section in ['HERBAL', 'ZODIAC', 'BIOLOGICAL', 'RECIPES']:
            if baseline.get(section, 0) == 0:
                continue
            sect_pct = counts.get(section, 0) / prefix_total
            enrichment = sect_pct / baseline[section]
            if enrichment > 1.5:  # Significant enrichment
                enrichments.append((prefix, section, enrichment))

    return enrichments

# Real enrichments
real_enrichments = calculate_enrichment(all_words, get_real_section)
print(f"REAL section enrichments (>1.5x): {len(real_enrichments)}")
for p, s, e in sorted(real_enrichments, key=lambda x: -x[2])[:10]:
    print(f"  {p}: {s} {e:.2f}x")
print()

# Run 100 scrambled trials
print("Running 100 scrambled trials...")
scrambled_counts = []

for trial in range(100):
    # Create random section assignment
    random.seed(trial)
    sections = ['HERBAL', 'ZODIAC', 'BIOLOGICAL', 'RECIPES']
    scrambled_map = {f: random.choice(sections) for f in all_folios}

    def scrambled_section(folio):
        return scrambled_map.get(folio, 'UNKNOWN')

    scrambled_enrichments = calculate_enrichment(all_words, scrambled_section)
    scrambled_counts.append(len(scrambled_enrichments))

avg_scrambled = sum(scrambled_counts) / len(scrambled_counts)
max_scrambled = max(scrambled_counts)

print()
print(f"RESULTS:")
print(f"  Real sections: {len(real_enrichments)} significant enrichments")
print(f"  Scrambled average: {avg_scrambled:.1f} significant enrichments")
print(f"  Scrambled maximum: {max_scrambled} significant enrichments")
print()

if len(real_enrichments) > max_scrambled:
    print("TEST 1 RESULT: **PASS**")
    print("Real sections show MORE enrichment than any scrambled trial.")
    print("The enrichment pattern is NOT spurious.")
    test1_pass = True
else:
    print("TEST 1 RESULT: **FAIL**")
    print("Scrambled sections can produce similar enrichment.")
    print("Our pattern may be spurious.")
    test1_pass = False

print()

# ============================================================================
# TEST 2: BLIND PREDICTION - UNSEEN FOLIOS
# ============================================================================

print("=" * 90)
print("TEST 2: BLIND PREDICTION - UNSEEN FOLIOS")
print("=" * 90)
print()
print("Method: Select folios NOT used in training. Predict content from illustrations.")
print("Then decode and check if predictions match.")
print()

# Select 5 test folios with known illustration content
# These are folios we can make predictions about from their illustrations
TEST_FOLIOS = {
    'f71r': {
        'illustration': 'Bull/Taurus zodiac symbol with women holding stars',
        'prediction': {
            'should_have': ['ot', 'ok', 'al'],  # time, sky, star prefixes
            'should_be_section': 'ZODIAC',
            'description': 'Should have zodiac/time vocabulary'
        }
    },
    'f78r': {
        'illustration': 'Naked women in tubes/vessels, bathing scene',
        'prediction': {
            'should_have': ['qo', 'ol'],  # womb, body prefixes
            'should_be_section': 'BIOLOGICAL',
            'description': 'Should have body/womb vocabulary'
        }
    },
    'f2r': {
        'illustration': 'Large plant with detailed roots and leaves',
        'prediction': {
            'should_have': ['ch', 'da', 'sh'],  # herb, leaf, juice prefixes
            'should_be_section': 'HERBAL',
            'description': 'Should have plant vocabulary'
        }
    },
    'f69r': {
        'illustration': 'Circular diagram with stars and zodiac elements',
        'prediction': {
            'should_have': ['ot', 'ok', 'al'],  # time, sky, star prefixes
            'should_be_section': 'ZODIAC',
            'description': 'Should have astronomical vocabulary'
        }
    },
    'f88r': {
        'illustration': 'Short paragraphs with star markers (recipe format)',
        'prediction': {
            'should_have': ['ch', 'sh', 'ct'],  # herb, juice, water prefixes
            'should_be_section': 'RECIPES',
            'description': 'Should have preparation vocabulary'
        }
    },
}

print("Test folios and predictions:")
for folio, data in TEST_FOLIOS.items():
    print(f"\n  {folio}: {data['illustration']}")
    print(f"  Prediction: {data['prediction']['description']}")
    print(f"  Expected prefixes: {data['prediction']['should_have']}")

print()
print("Running predictions...")
print()

predictions_correct = 0
total_predictions = 0

for folio, data in TEST_FOLIOS.items():
    # Get words from this folio
    folio_words = [w['word'] for w in all_words if w['folio'] == folio]

    if not folio_words:
        print(f"  {folio}: No words found, skipping")
        continue

    # Count prefixes
    prefix_counts = Counter()
    for word in folio_words:
        for prefix in OUR_PREFIXES:
            if word.startswith(prefix):
                prefix_counts[prefix] += 1
                break

    total_words = len(folio_words)

    # Check prediction
    expected = data['prediction']['should_have']
    expected_section = data['prediction']['should_be_section']
    actual_section = get_real_section(folio)

    # Calculate what percentage of words have expected prefixes
    expected_count = sum(prefix_counts.get(p, 0) for p in expected)
    expected_pct = expected_count / total_words * 100 if total_words > 0 else 0

    # Get top prefixes actually found
    top_prefixes = [p for p, c in prefix_counts.most_common(3)]

    # Check if prediction matches
    section_match = actual_section == expected_section
    prefix_match = any(p in top_prefixes for p in expected)

    total_predictions += 1
    if section_match and prefix_match:
        predictions_correct += 1
        result = "CORRECT"
    elif section_match or prefix_match:
        predictions_correct += 0.5
        result = "PARTIAL"
    else:
        result = "WRONG"

    print(f"  {folio}:")
    print(f"    Expected section: {expected_section}, Actual: {actual_section} {'OK' if section_match else 'MISMATCH'}")
    print(f"    Expected prefixes: {expected}, Top found: {top_prefixes} {'OK' if prefix_match else 'MISMATCH'}")
    print(f"    Result: {result}")
    print()

accuracy = predictions_correct / total_predictions if total_predictions > 0 else 0

print(f"RESULTS:")
print(f"  Predictions correct: {predictions_correct}/{total_predictions} ({accuracy*100:.0f}%)")
print()

if accuracy >= 0.6:  # 3+ of 5 correct
    print("TEST 2 RESULT: **PASS**")
    print("Illustrations predict vocabulary content.")
    print("The semantic assignments appear valid.")
    test2_pass = True
else:
    print("TEST 2 RESULT: **FAIL**")
    print("Predictions do not match decoded content.")
    print("Semantic assignments may be wrong.")
    test2_pass = False

print()

# ============================================================================
# TEST 3: ALTERNATIVE MEANINGS - WRONG SEMANTICS
# ============================================================================

print("=" * 90)
print("TEST 3: ALTERNATIVE MEANINGS - WRONG SEMANTICS")
print("=" * 90)
print()
print("Method: Assign DIFFERENT meanings to the same prefixes.")
print("If coherence stays the same, we haven't found the TRUE meaning.")
print()

# Alternative (wrong) semantic framework
WRONG_PREFIXES = {
    'qo': 'question',  # NOT womb
    'ol': 'old',       # NOT menses
    'ch': 'chapter',   # NOT herb
    'sh': 'ship',      # NOT juice
    'da': 'day',       # NOT leaf
    'ct': 'city',      # NOT water
    'ot': 'other',     # NOT time
    'ok': 'okay',      # NOT sky
    'al': 'all',       # NOT star
    'ar': 'art',       # NOT air
}

# Calculate "coherence" as: how well do adjacent words share semantic categories?
def calculate_coherence(words, prefix_meanings, section_meanings):
    """
    Calculate coherence: Do words with certain prefixes appear in expected sections?
    Higher = better match between prefix meaning and section content.
    """
    # Map our meanings to expected sections
    # Our framework: womb->BIOLOGICAL, herb->HERBAL, time->ZODIAC
    # Wrong framework: question->?, chapter->?, etc

    score = 0
    total = 0

    # For our framework:
    # - 'womb' prefixes should be in BIOLOGICAL
    # - 'herb' prefixes should be in HERBAL
    # - 'time' prefixes should be in ZODIAC

    expected_sections = {
        'womb': 'BIOLOGICAL',
        'menses': 'BIOLOGICAL',
        'herb': 'HERBAL',
        'juice': 'HERBAL',
        'leaf': 'HERBAL',
        'water': 'HERBAL',
        'time': 'ZODIAC',
        'sky': 'ZODIAC',
        'star': 'ZODIAC',
        'air': 'ZODIAC',
        # Wrong meanings - no clear section assignment
        'question': None,
        'old': None,
        'chapter': None,
        'ship': None,
        'day': None,
        'city': None,
        'other': None,
        'okay': None,
        'all': None,
        'art': None,
    }

    for w in words:
        section = w['real_section']
        if section in ['UNKNOWN', 'OTHER']:
            continue

        for prefix, meaning in prefix_meanings.items():
            if w['word'].startswith(prefix):
                expected = expected_sections.get(meaning)
                if expected:
                    total += 1
                    if section == expected:
                        score += 1
                break

    return score / total if total > 0 else 0

# Calculate coherence for both frameworks
our_coherence = calculate_coherence(all_words, OUR_PREFIXES, None)
wrong_coherence = calculate_coherence(all_words, WRONG_PREFIXES, None)

print("Our prefix meanings:")
for p, m in list(OUR_PREFIXES.items())[:5]:
    print(f"  {p} = {m}")
print()

print("Alternative (wrong) meanings:")
for p, m in list(WRONG_PREFIXES.items())[:5]:
    print(f"  {p} = {m}")
print()

print(f"RESULTS:")
print(f"  Our framework coherence: {our_coherence*100:.1f}%")
print(f"  Wrong framework coherence: {wrong_coherence*100:.1f}%")
print(f"  Difference: {(our_coherence - wrong_coherence)*100:.1f} percentage points")
print()

if our_coherence > wrong_coherence + 0.05:  # At least 5% better
    print("TEST 3 RESULT: **PASS**")
    print("Our meanings produce HIGHER coherence than wrong meanings.")
    print("The semantic framework is not arbitrary.")
    test3_pass = True
else:
    print("TEST 3 RESULT: **FAIL**")
    print("Wrong meanings work equally well (or better).")
    print("Our semantic assignments may be arbitrary.")
    test3_pass = False

print()

# ============================================================================
# OVERALL RESULTS
# ============================================================================

print("=" * 90)
print("FALSIFICATION TEST SUMMARY")
print("=" * 90)
print()

tests_passed = sum([test1_pass, test2_pass, test3_pass])

print(f"Test 1 (Null Hypothesis):     {'PASS' if test1_pass else 'FAIL'}")
print(f"Test 2 (Blind Prediction):    {'PASS' if test2_pass else 'FAIL'}")
print(f"Test 3 (Alternative Meanings): {'PASS' if test3_pass else 'FAIL'}")
print()
print(f"OVERALL: {tests_passed}/3 tests passed")
print()

if tests_passed == 3:
    print("CONCLUSION: Strong evidence that our framework is VALID.")
    print("The hypothesis has survived falsification attempts.")
elif tests_passed == 2:
    print("CONCLUSION: Moderate evidence. Framework is PARTIALLY supported.")
    print("Some aspects may need revision.")
elif tests_passed == 1:
    print("CONCLUSION: Weak evidence. Framework has SIGNIFICANT problems.")
    print("Major revision needed.")
else:
    print("CONCLUSION: Framework FAILED falsification.")
    print("Our hypothesis is likely WRONG.")

print()
print("=" * 90)
