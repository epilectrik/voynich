"""
German First-Letter Abbreviation Hypothesis Test

Tests the null hypothesis: German has enough distillation/workshop vocabulary
that for ANY random consonant-to-function assignment, you could find a plausible
German verb starting with that letter (i.e., the mappings are cherry-picked).

METHODOLOGY:
1. Compile comprehensive German distillation/alchemical/workshop verb inventory
2. Calculate letter coverage rate
3. Test probability of 11/11 matches by chance
4. Forward test: for each claimed letter, count matching vs non-matching verbs
5. Reverse test: for each function, list all German verbs regardless of first letter
6. Calculate statistical significance
"""

import json
import math
from collections import defaultdict
from itertools import combinations

# =============================================================================
# SECTION 1: COMPREHENSIVE GERMAN DISTILLATION/WORKSHOP VERB INVENTORY
# =============================================================================
# Compiled from:
# - Hieronymus Brunschwig's Liber de arte distillandi (1500)
# - Herzog August Bibliothek alchemical thesaurus
# - Standard German chemistry/laboratory terminology
# - Medieval brewing and distillery vocabulary
# - Historical alchemy operations (7 classical operations + extensions)
# - Modern German chemistry lab verb lists

VERBS = {
    # (verb, english_meaning, category)
    # Categories: HEAT, COOL, HOLD, SEAL, DRIVE, SEPARATE, COMPLETE, MEASURE,
    #             STIR, ALLOW, PAUSE, FILTER, DISSOLVE, CONDENSE, EVAPORATE,
    #             GRIND, POUR, WASH, MIX, BURN, FERMENT, CRYSTALLIZE, SUBLIME,
    #             PRESS, FILL, OPEN, CLOSE, CALCINE, TINCTURE, COAGULATE,
    #             EXTRACT, THICKEN, PREPARE, ADJUST, CUT, WEIGH, OBSERVE

    # === A ===
    "abkühlen": ("to cool down", "COOL"),
    "abdampfen": ("to evaporate off", "EVAPORATE"),
    "abdichten": ("to seal/make airtight", "SEAL"),
    "abfüllen": ("to bottle/fill off", "FILL"),
    "abgießen": ("to pour off/decant", "POUR"),
    "ablassen": ("to let off/drain", "ALLOW"),
    "abmessen": ("to measure out", "MEASURE"),
    "abreiben": ("to grind/abrade", "GRIND"),
    "abscheiden": ("to separate off", "SEPARATE"),
    "abseihen": ("to strain/sieve", "FILTER"),
    "absetzen": ("to settle/deposit", "SETTLE"),
    "abstoppen": ("to stop", "PAUSE"),
    "abwägen": ("to weigh out", "MEASURE"),
    "abziehen": ("to draw off/distill", "SEPARATE"),
    "anfeuern": ("to fire up/stoke", "HEAT"),
    "anheizen": ("to heat up/fire up", "HEAT"),
    "anrühren": ("to stir/mix", "STIR"),
    "ansetzen": ("to prepare/set up", "PREPARE"),
    "aufbewahren": ("to store/preserve", "HOLD"),
    "aufkochen": ("to bring to boil", "HEAT"),
    "auflösen": ("to dissolve", "DISSOLVE"),
    "ausfällen": ("to precipitate", "SEPARATE"),
    "auslaugen": ("to leach", "EXTRACT"),
    "auspressen": ("to press out", "PRESS"),
    "auswaschen": ("to wash out", "WASH"),

    # === B ===
    "beheizen": ("to heat", "HEAT"),
    "beizen": ("to etch/corrode", "DISSOLVE"),
    "binden": ("to bind", "SEAL"),
    "brauen": ("to brew", "HEAT"),
    "brennen": ("to burn/distill", "HEAT"),

    # === C ===  (very few native German words start with C)
    "calcinieren": ("to calcine", "HEAT"),

    # === D ===
    "dampfen": ("to steam", "EVAPORATE"),
    "destillieren": ("to distill", "SEPARATE"),
    "dichten": ("to seal/make tight", "SEAL"),
    "drehen": ("to turn/rotate", "STIR"),
    "drücken": ("to press", "PRESS"),
    "durchseihen": ("to strain through", "FILTER"),
    "durchrühren": ("to stir through", "STIR"),
    "dünsten": ("to steam/stew", "HEAT"),

    # === E ===
    "eindampfen": ("to evaporate down", "EVAPORATE"),
    "eindicken": ("to thicken/concentrate", "THICKEN"),
    "einfüllen": ("to fill in", "FILL"),
    "einheizen": ("to heat up", "HEAT"),
    "einkochen": ("to boil down/reduce", "HEAT"),
    "einlegen": ("to soak/macerate", "DISSOLVE"),
    "einrühren": ("to stir in", "STIR"),
    "einweichen": ("to soak", "DISSOLVE"),
    "erhalten": ("to maintain/preserve", "HOLD"),
    "erhitzen": ("to heat up", "HEAT"),
    "erkalten": ("to cool/grow cold", "COOL"),
    "erwärmen": ("to warm", "HEAT"),
    "extrahieren": ("to extract", "EXTRACT"),

    # === F ===
    "fermentieren": ("to ferment", "FERMENT"),
    "filtrieren": ("to filter", "FILTER"),
    "fixieren": ("to fix/make permanent", "SEAL"),

    # === G ===
    "gären": ("to ferment", "FERMENT"),
    "gießen": ("to pour/cast", "POUR"),
    "glühen": ("to glow/anneal", "HEAT"),

    # === H ===
    "halten": ("to hold/maintain", "HOLD"),
    "heizen": ("to heat", "HEAT"),
    "herstellen": ("to produce/prepare", "PREPARE"),

    # === I ===  (very few relevant)
    # No strong distillation verbs starting with I in German

    # === J ===
    "justieren": ("to adjust/calibrate", "MEASURE"),

    # === K ===
    "kochen": ("to boil/cook", "HEAT"),
    "klären": ("to clarify", "FILTER"),
    "kühlen": ("to cool", "COOL"),
    "kondensieren": ("to condense", "CONDENSE"),
    "kristallisieren": ("to crystallize", "CRYSTALLIZE"),

    # === L ===
    "lassen": ("to let/allow", "ALLOW"),
    "lagern": ("to store/age", "HOLD"),
    "läutern": ("to purify/clarify", "FILTER"),
    "lösen": ("to dissolve/loosen", "DISSOLVE"),
    "löschen": ("to quench/extinguish", "COOL"),
    "loten": ("to solder/seal with lead", "SEAL"),
    "lutieren": ("to lute/seal with clay", "SEAL"),

    # === M ===
    "maischen": ("to mash", "MIX"),
    "mahlen": ("to grind/mill", "GRIND"),
    "messen": ("to measure", "MEASURE"),
    "mischen": ("to mix", "MIX"),
    "mörsern": ("to mortar/grind", "GRIND"),

    # === N ===
    "nachfüllen": ("to refill", "FILL"),
    "niederschlagen": ("to precipitate", "SEPARATE"),

    # === O ===  (few relevant)
    # No strong distillation verbs starting with O in German

    # === P ===
    "pressen": ("to press", "PRESS"),
    "prüfen": ("to test/check", "MEASURE"),
    "putrefizieren": ("to putrefy", "FERMENT"),

    # === Q ===  (essentially none in native German)
    # No native German distillation verbs start with Q
    # (qo in the hypothesis maps to Latin coquo anyway)

    # === R ===
    "reiben": ("to rub/grind", "GRIND"),
    "reinigen": ("to clean/purify", "FILTER"),
    "rühren": ("to stir", "STIR"),
    "ruhen": ("to rest", "PAUSE"),
    "rösten": ("to roast", "HEAT"),

    # === S ===
    "scheiden": ("to separate", "SEPARATE"),
    "schmelzen": ("to melt", "HEAT"),
    "schneiden": ("to cut", "CUT"),
    "schütteln": ("to shake", "STIR"),
    "schütten": ("to pour", "POUR"),
    "sieden": ("to boil/simmer", "HEAT"),
    "sieben": ("to sieve", "FILTER"),
    "stampfen": ("to stamp/pound", "GRIND"),
    "stehen lassen": ("to let stand", "PAUSE"),
    "sublimieren": ("to sublimate", "SUBLIME"),

    # === T ===
    "tingieren": ("to tincture/color", "TINCTURE"),
    "treiben": ("to drive", "DRIVE"),
    "trennen": ("to separate", "SEPARATE"),
    "trocknen": ("to dry", "EVAPORATE"),

    # === U ===
    "umfüllen": ("to transfer/decant", "POUR"),
    "umrühren": ("to stir around", "STIR"),

    # === V ===
    "verdampfen": ("to evaporate", "EVAPORATE"),
    "verdichten": ("to densify/compress", "SEAL"),
    "verdünnen": ("to dilute", "MIX"),
    "verschließen": ("to close/seal up", "SEAL"),
    "verrühren": ("to stir together", "STIR"),

    # === W ===
    "wärmen": ("to warm", "HEAT"),
    "wägen": ("to weigh", "MEASURE"),
    "waschen": ("to wash", "WASH"),
    "wiegen": ("to weigh", "MEASURE"),

    # === X ===
    # No German distillation verbs start with X

    # === Y ===
    # No German distillation verbs start with Y

    # === Z ===
    "zerkleinern": ("to pulverize/reduce", "GRIND"),
    "zerreiben": ("to grind up", "GRIND"),
    "zersetzen": ("to decompose", "SEPARATE"),
    "zufügen": ("to add", "MIX"),
    "zudecken": ("to cover", "SEAL"),
    "zusammensetzen": ("to combine", "MIX"),
}

print("=" * 80)
print("GERMAN FIRST-LETTER ABBREVIATION HYPOTHESIS TEST")
print("=" * 80)
print(f"\nTotal verbs compiled: {len(VERBS)}")

# =============================================================================
# SECTION 2: LETTER COVERAGE ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 2: LETTER COVERAGE")
print("=" * 80)

# Get first letters of all verbs
first_letters = set()
letter_to_verbs = defaultdict(list)
for verb, (meaning, category) in VERBS.items():
    fl = verb[0].lower()
    first_letters.add(fl)
    letter_to_verbs[fl].append((verb, meaning, category))

all_letters = set("abcdefghijklmnopqrstuvwxyz")
covered = first_letters & all_letters
uncovered = all_letters - first_letters

print(f"\nLetters covered by at least one distillation verb: {len(covered)}/26")
print(f"Covered: {sorted(covered)}")
print(f"Uncovered: {sorted(uncovered)}")
print(f"\nCoverage rate: {len(covered)/26:.1%}")

print("\nVerbs per letter:")
for letter in sorted(all_letters):
    verbs = letter_to_verbs.get(letter, [])
    print(f"  {letter}: {len(verbs):2d} verbs", end="")
    if verbs:
        print(f"  ({', '.join(v[0] for v in verbs[:4])}", end="")
        if len(verbs) > 4:
            print(f", +{len(verbs)-4} more", end="")
        print(")")
    else:
        print("  (none)")

# =============================================================================
# SECTION 3: PROBABILITY OF 11/11 MATCHES (NAIVE TEST)
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 3: NAIVE PROBABILITY (letter coverage only)")
print("=" * 80)

# The hypothesis claims 11 consonant mappings (excluding qo which is Latin)
# Actually 12 mappings but qo is a digraph mapped to Latin, so test 11 single letters
claimed_letters = ['k', 'e', 'h', 'd', 't', 's', 'g', 'm', 'r', 'l', 'p']
print(f"\nClaimed letters: {claimed_letters}")

# How many of these 11 are covered?
claimed_covered = [l for l in claimed_letters if l in covered]
claimed_uncovered = [l for l in claimed_letters if l not in covered]
print(f"Covered: {len(claimed_covered)}/11: {claimed_covered}")
print(f"Uncovered: {len(claimed_uncovered)}/11: {claimed_uncovered}")

# Coverage rate
C = len(covered) / 26  # probability a random letter has at least one verb

# Probability all 11 letters have at least one verb
# This is a hypergeometric problem: drawing 11 letters from 26,
# what's probability all 11 are in the covered set?

# Hypergeometric: P(all 11 covered) = C(covered,11) * C(uncovered,0) / C(26,11)
n_covered = len(covered)
n_uncovered = 26 - n_covered

def comb(n, k):
    if k > n or k < 0:
        return 0
    return math.comb(n, k)

p_naive = comb(n_covered, 11) * comb(n_uncovered, 0) / comb(26, 11)
print(f"\nNaive probability (hypergeometric):")
print(f"  Drawing 11 letters from 26, all falling in {n_covered} covered letters")
print(f"  P = C({n_covered},11) / C(26,11) = {p_naive:.4f}")
print(f"  This is {'NOT' if p_naive > 0.05 else ''} significant at p<0.05")

# Also compute assuming independence (binomial approximation)
p_binomial = C ** 11
print(f"\nBinomial approximation (independence):")
print(f"  P = ({C:.3f})^11 = {p_binomial:.4f}")

print(f"\n>>> NAIVE TEST CONCLUSION: With coverage rate {C:.1%}, finding 11/11")
print(f"    letter matches is {'NOT surprising' if p_naive > 0.05 else 'somewhat surprising'}.")
print(f"    p = {p_naive:.4f}")
print(f"    This test DOES NOT account for semantic matching.")

# =============================================================================
# SECTION 4: FORWARD TEST — For each letter, do the verbs match the function?
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 4: FORWARD TEST (letter -> function specificity)")
print("=" * 80)

# The claimed function mappings
CLAIMED_FUNCTIONS = {
    'k': ("ENERGY_DRIVER (heating)", "HEAT"),
    'e': ("STABILITY_ANCHOR (cooling)", "COOL"),
    'h': ("PHASE_MANAGER (maintaining)", "HOLD"),
    'd': ("END-class (closing/sealing)", "SEAL"),
    't': ("transfer", "DRIVE"),
    's': ("break/separate", "SEPARATE"),
    'g': ("complete", "COMPLETE"),  # mapped to FERMENT (gar = done cooking)
    'm': ("measure", "MEASURE"),
    'r': ("stir", "STIR"),
    'l': ("late/continue/allow", "ALLOW"),
    'p': ("pause", "PAUSE"),
}

# For 'g' -> "complete/done", gar means "done cooking" which maps to FERMENT/COMPLETE
# We need to handle this specially

print("\nFor each claimed letter, ALL distillation verbs starting with that letter:")
print("Marking which ones match (+) or don't match (-) the claimed function.\n")

forward_results = {}

for letter in claimed_letters:
    function_name, function_cat = CLAIMED_FUNCTIONS[letter]
    verbs_for_letter = letter_to_verbs.get(letter, [])

    print(f"--- {letter.upper()} = {function_name} ---")

    matching = []
    non_matching = []

    for verb, meaning, category in verbs_for_letter:
        # Check if the verb's category matches the claimed function
        # We need semantic matching, not just category matching
        is_match = False

        if letter == 'k':
            is_match = category in ('HEAT', 'COOL', 'CONDENSE', 'CRYSTALLIZE')
            # kochen=HEAT yes, kühlen=COOL NO (opposite!), klären=FILTER NO
            is_match = category == 'HEAT'
        elif letter == 'e':
            is_match = category in ('COOL', 'EVAPORATE')
            # erkalten=COOL yes, but erhitzen=HEAT NO, einkochen=HEAT NO
            is_match = category == 'COOL'
        elif letter == 'h':
            is_match = category in ('HOLD', 'HEAT')
            # halten=HOLD yes, but heizen=HEAT NO (different function!)
            is_match = category == 'HOLD'
        elif letter == 'd':
            is_match = category in ('SEAL', 'CLOSE')
            # dichten=SEAL yes, but destillieren=SEPARATE NO
            is_match = category == 'SEAL'
        elif letter == 't':
            is_match = category in ('DRIVE', 'POUR')
            # treiben=DRIVE yes, but trennen=SEPARATE NO, trocknen=EVAPORATE NO
            is_match = category == 'DRIVE'
        elif letter == 's':
            is_match = category == 'SEPARATE'
            # scheiden=SEPARATE yes, but sieden=HEAT NO, sublimieren=SUBLIME NO
        elif letter == 'g':
            # "gar" = done/cooked, function=COMPLETE
            # gären=ferment is close but not "complete"
            # gießen=pour NO, glühen=glow NO
            is_match = category in ('FERMENT', 'COMPLETE')  # generous
        elif letter == 'm':
            is_match = category in ('MEASURE',)
            # messen=MEASURE yes, but mischen=MIX NO, mahlen=GRIND NO
        elif letter == 'r':
            is_match = category == 'STIR'
            # rühren=STIR yes, but reiben=GRIND NO, reinigen=FILTER NO
        elif letter == 'l':
            is_match = category in ('ALLOW', 'HOLD')
            # lassen=ALLOW yes, but lösen=DISSOLVE NO, läutern=FILTER NO
        elif letter == 'p':
            is_match = category == 'PAUSE'
            # No strong match — pressen=PRESS NO, prüfen=MEASURE NO
            # putrefizieren=FERMENT NO

        if is_match:
            matching.append((verb, meaning, category))
            print(f"  + {verb:20s} ({meaning:30s}) [{category}]")
        else:
            non_matching.append((verb, meaning, category))
            print(f"  - {verb:20s} ({meaning:30s}) [{category}]")

    n_match = len(matching)
    n_total = len(verbs_for_letter)
    ratio = n_match / n_total if n_total > 0 else 0

    forward_results[letter] = {
        'matching': n_match,
        'total': n_total,
        'non_matching': n_total - n_match,
        'ratio': ratio
    }

    print(f"  Score: {n_match}/{n_total} match ({ratio:.0%})")
    print()

# Summary
print("\n--- FORWARD TEST SUMMARY ---")
print(f"{'Letter':>6} {'Function':>30} {'Match':>5} {'Total':>5} {'Wrong':>5} {'Ratio':>6}")
total_match = 0
total_verbs = 0
for letter in claimed_letters:
    fr = forward_results[letter]
    fn = CLAIMED_FUNCTIONS[letter][0]
    total_match += fr['matching']
    total_verbs += fr['total']
    print(f"{letter:>6} {fn:>30} {fr['matching']:>5} {fr['total']:>5} {fr['non_matching']:>5} {fr['ratio']:>6.0%}")

avg_ratio = total_match / total_verbs if total_verbs > 0 else 0
print(f"\nOverall: {total_match}/{total_verbs} verbs match their claimed function ({avg_ratio:.1%})")
print(f"Average 'wrong' verbs per letter: {(total_verbs - total_match)/11:.1f}")

# =============================================================================
# SECTION 5: REVERSE TEST — For each function, what letters could work?
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 5: REVERSE TEST (function -> letter specificity)")
print("=" * 80)

# For each of the 11 functions, list ALL German verbs and their first letters
FUNCTION_VERBS = {
    "HEAT (heating/boiling)": {
        'claimed': 'k',
        'all_verbs': [
            ('kochen', 'k', 'to boil/cook'),
            ('heizen', 'h', 'to heat'),
            ('erhitzen', 'e', 'to heat up'),
            ('erwärmen', 'e', 'to warm'),
            ('sieden', 's', 'to boil/simmer'),
            ('brennen', 'b', 'to burn/distill'),
            ('glühen', 'g', 'to glow/anneal'),
            ('anfeuern', 'a', 'to fire up'),
            ('anheizen', 'a', 'to heat up'),
            ('aufkochen', 'a', 'to bring to boil'),
            ('beheizen', 'b', 'to heat'),
            ('einheizen', 'e', 'to heat up'),
            ('einkochen', 'e', 'to boil down'),
            ('schmelzen', 's', 'to melt'),
            ('rösten', 'r', 'to roast'),
            ('brauen', 'b', 'to brew'),
            ('dünsten', 'd', 'to steam/stew'),
            ('wärmen', 'w', 'to warm'),
            ('calcinieren', 'c', 'to calcine'),
        ],
    },
    "COOL (cooling)": {
        'claimed': 'e',
        'all_verbs': [
            ('erkalten', 'e', 'to cool/grow cold'),
            ('abkühlen', 'a', 'to cool down'),
            ('kühlen', 'k', 'to cool'),
            ('löschen', 'l', 'to quench'),
        ],
    },
    "HOLD (maintaining)": {
        'claimed': 'h',
        'all_verbs': [
            ('halten', 'h', 'to hold/maintain'),
            ('erhalten', 'e', 'to maintain/preserve'),
            ('aufbewahren', 'a', 'to store/preserve'),
            ('lagern', 'l', 'to store/age'),
            ('bewahren', 'b', 'to preserve'),
        ],
    },
    "SEAL (closing/sealing)": {
        'claimed': 'd',
        'all_verbs': [
            ('dichten', 'd', 'to seal/make tight'),
            ('abdichten', 'a', 'to seal/make airtight'),
            ('verschließen', 'v', 'to close/seal up'),
            ('lutieren', 'l', 'to lute/seal with clay'),
            ('loten', 'l', 'to solder/seal'),
            ('zudecken', 'z', 'to cover'),
            ('fixieren', 'f', 'to fix/make permanent'),
            ('binden', 'b', 'to bind'),
            ('verdichten', 'v', 'to compress/densify'),
        ],
    },
    "DRIVE/TRANSFER": {
        'claimed': 't',
        'all_verbs': [
            ('treiben', 't', 'to drive'),
            ('umfüllen', 'u', 'to transfer/decant'),
            ('abgießen', 'a', 'to pour off/decant'),
            ('gießen', 'g', 'to pour'),
            ('schütten', 's', 'to pour'),
        ],
    },
    "SEPARATE (break/separate)": {
        'claimed': 's',
        'all_verbs': [
            ('scheiden', 's', 'to separate'),
            ('trennen', 't', 'to separate'),
            ('destillieren', 'd', 'to distill/separate'),
            ('abscheiden', 'a', 'to separate off'),
            ('abziehen', 'a', 'to draw off/distill'),
            ('ausfällen', 'a', 'to precipitate'),
            ('niederschlagen', 'n', 'to precipitate'),
            ('zersetzen', 'z', 'to decompose'),
        ],
    },
    "COMPLETE (done/finished)": {
        'claimed': 'g',
        'all_verbs': [
            ('gar sein', 'g', 'to be done/cooked'),
            ('fertig sein', 'f', 'to be finished'),
            ('vollenden', 'v', 'to complete'),
            ('beenden', 'b', 'to end'),
            ('abschließen', 'a', 'to conclude'),
        ],
    },
    "MEASURE": {
        'claimed': 'm',
        'all_verbs': [
            ('messen', 'm', 'to measure'),
            ('wägen', 'w', 'to weigh'),
            ('wiegen', 'w', 'to weigh'),
            ('abmessen', 'a', 'to measure out'),
            ('abwägen', 'a', 'to weigh out'),
            ('prüfen', 'p', 'to test/check'),
            ('justieren', 'j', 'to adjust/calibrate'),
        ],
    },
    "STIR": {
        'claimed': 'r',
        'all_verbs': [
            ('rühren', 'r', 'to stir'),
            ('umrühren', 'u', 'to stir around'),
            ('einrühren', 'e', 'to stir in'),
            ('verrühren', 'v', 'to stir together'),
            ('durchrühren', 'd', 'to stir through'),
            ('anrühren', 'a', 'to stir/mix'),
            ('schütteln', 's', 'to shake'),
            ('drehen', 'd', 'to turn/rotate'),
        ],
    },
    "ALLOW (let/continue)": {
        'claimed': 'l',
        'all_verbs': [
            ('lassen', 'l', 'to let/allow'),
            ('stehen lassen', 's', 'to let stand'),
            ('ablassen', 'a', 'to let off/drain'),
            ('erlauben', 'e', 'to allow/permit'),
            ('gewähren', 'g', 'to grant/allow'),
            ('zulassen', 'z', 'to allow/permit'),
        ],
    },
    "PAUSE (rest/wait)": {
        'claimed': 'p',
        'all_verbs': [
            ('pausieren', 'p', 'to pause'),
            ('ruhen', 'r', 'to rest'),
            ('rasten', 'r', 'to rest/take a break'),
            ('warten', 'w', 'to wait'),
            ('innehalten', 'i', 'to pause/stop'),
            ('abstoppen', 'a', 'to stop'),
        ],
    },
}

print("\nFor each function, all German verbs and whether they start with the claimed letter:\n")

reverse_results = {}

for func_name, data in FUNCTION_VERBS.items():
    claimed = data['claimed']
    verbs = data['all_verbs']

    print(f"--- {func_name} (claimed: {claimed.upper()}) ---")

    matching = []
    non_matching = []
    alternative_letters = set()

    for verb, first_letter, meaning in verbs:
        fl = first_letter.lower()
        if fl == claimed:
            matching.append((verb, meaning))
            print(f"  + {verb:20s} ({meaning})")
        else:
            non_matching.append((verb, fl, meaning))
            alternative_letters.add(fl)
            print(f"  - {verb:20s} (starts with {fl.upper()}) ({meaning})")

    n_match = len(matching)
    n_total = len(verbs)

    reverse_results[func_name] = {
        'claimed': claimed,
        'matching': n_match,
        'total': n_total,
        'alternative_letters': sorted(alternative_letters),
        'n_alternatives': len(alternative_letters),
    }

    print(f"  Correct letter: {n_match}/{n_total} ({n_match/n_total:.0%})")
    print(f"  Alternative letters that could work: {sorted(alternative_letters)}")
    print()

# Summary
print("\n--- REVERSE TEST SUMMARY ---")
print(f"{'Function':>30} {'Claimed':>7} {'Match':>5} {'Total':>5} {'Alts':>5} {'Alt Letters'}")
total_match_r = 0
total_verbs_r = 0
total_alt_letters = set()
for func_name, rr in reverse_results.items():
    total_match_r += rr['matching']
    total_verbs_r += rr['total']
    total_alt_letters.update(rr['alternative_letters'])
    print(f"{func_name:>30} {rr['claimed']:>7} {rr['matching']:>5} {rr['total']:>5} {rr['n_alternatives']:>5} {rr['alternative_letters']}")

avg_ratio_r = total_match_r / total_verbs_r if total_verbs_r > 0 else 0
print(f"\nOverall: {total_match_r}/{total_verbs_r} verbs start with the claimed letter ({avg_ratio_r:.1%})")
print(f"Total unique alternative letters across all functions: {len(total_alt_letters)}")

# =============================================================================
# SECTION 6: COMBINED STATISTICAL ASSESSMENT
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 6: COMBINED STATISTICAL ASSESSMENT")
print("=" * 80)

# Test 1: Naive letter coverage
print(f"\n--- TEST 1: Letter Coverage (weak test) ---")
print(f"Coverage rate: {len(covered)}/26 = {len(covered)/26:.1%}")
print(f"P(11/11 covered by chance): {p_naive:.4f}")
print(f"Verdict: {'FAILS to reject H0' if p_naive > 0.05 else 'Rejects H0'}")

# Test 2: Semantic precision (forward)
# For each letter, what fraction of verbs match the claimed function?
# Under H0 (random assignment), the expected match rate for each letter
# depends on how many functional categories exist among its verbs.
#
# A rough model: if each letter has N verbs spanning C categories,
# and we randomly assign a function, the expected match rate is ~1/C.

print(f"\n--- TEST 2: Forward Semantic Precision ---")
print(f"Question: Given the letter, how specific is the verb match?")

# For each letter, count distinct categories
letter_specificity = {}
for letter in claimed_letters:
    verbs = letter_to_verbs.get(letter, [])
    cats = set(v[2] for v in verbs)
    n_match = forward_results[letter]['matching']
    n_total = forward_results[letter]['total']
    letter_specificity[letter] = {
        'n_categories': len(cats),
        'categories': sorted(cats),
        'match_ratio': n_match / n_total if n_total > 0 else 0,
        'expected_random': 1 / len(cats) if cats else 0,
    }

print(f"\n{'Letter':>6} {'Claimed Function':>25} {'Categories':>4} {'Match%':>7} {'Random%':>8} {'Better?':>8}")
wins = 0
for letter in claimed_letters:
    ls = letter_specificity[letter]
    fn = CLAIMED_FUNCTIONS[letter][0]
    better = "YES" if ls['match_ratio'] > ls['expected_random'] else "NO"
    if ls['match_ratio'] > ls['expected_random']:
        wins += 1
    print(f"{letter:>6} {fn:>25} {ls['n_categories']:>4} {ls['match_ratio']:>7.0%} {ls['expected_random']:>8.0%} {better:>8}")

print(f"\nLetters where match exceeds random baseline: {wins}/11")

# Test 3: Reverse semantic precision
# For each function, how many verbs start with the "wrong" letter?
# Under H0, the claimed letter is just one of the possible first letters.
# P(correct by chance) = 1 / (number of distinct first letters for that function)

print(f"\n--- TEST 3: Reverse Semantic Precision ---")
print(f"Question: Given the function, how likely is the specific letter?")

print(f"\n{'Function':>30} {'Claimed':>7} {'Possible Letters':>4} {'P(chance)':>10} {'Match?':>7}")
p_product = 1.0
for func_name, rr in reverse_results.items():
    all_letters_func = set([rr['claimed']])
    all_letters_func.update(rr['alternative_letters'])
    n_possible = len(all_letters_func)
    p_chance = 1.0 / n_possible
    p_product *= p_chance
    has_match = rr['matching'] > 0
    print(f"{func_name:>30} {rr['claimed']:>7} {n_possible:>4} {p_chance:>10.3f} {'YES' if has_match else 'NO':>7}")

print(f"\nP(all 11 correct by chance, assuming independence) = {p_product:.8f}")
print(f"  = approximately 1 in {1/p_product:,.0f}")

# Test 4: The STRONGEST version of H0 — random permutation test
# Take the 11 functions and the 11 claimed letters.
# For each of the 11! possible assignments of letters to functions,
# count how many would also have a "plausible" German verb.
# This is the most rigorous test.

print(f"\n--- TEST 4: Permutation Test ---")
print(f"Of all possible ways to assign 11 letters to 11 functions,")
print(f"how many produce at least as good a match as the claimed mapping?")

# For each function, which first letters have at least one matching verb?
function_valid_letters = {}
for func_name, data in FUNCTION_VERBS.items():
    valid = set()
    valid.add(data['claimed'])  # The claimed letter always works (we found a verb)
    for verb, fl, meaning in data['all_verbs']:
        valid.add(fl.lower())
    function_valid_letters[func_name] = valid

# Note: the hypothesis claims SPECIFIC letters for SPECIFIC functions.
# Under a permutation test, we ask: if we randomly permute the 11 letters
# across the 11 functions, how often would ALL 11 still have a valid verb?

# This is computationally feasible for 11! = 39,916,800 permutations,
# but let's be smarter.

# Actually, let's enumerate which letters are valid for each function:
func_names = list(FUNCTION_VERBS.keys())
valid_sets = [function_valid_letters[fn] for fn in func_names]

print(f"\nValid first letters for each function:")
for fn, vs in zip(func_names, valid_sets):
    print(f"  {fn:>30}: {sorted(vs)} ({len(vs)} options)")

# The question: of all 11! permutations of claimed_letters across functions,
# how many have ALL 11 letters falling in the valid set for that function?

from itertools import permutations

# This is 11! = ~40M, might take a while. Let's do it.
# Actually, let's be smarter - use the structure.

# For efficiency, use counting of perfect matchings in a bipartite graph
# (letters on one side, functions on other, edge if letter is valid for function)

# Build bipartite adjacency
func_indices = list(range(11))
letter_list = claimed_letters  # the 11 letters to assign

print(f"\nBipartite adjacency (which letters are valid for which functions):")
adjacency = []
for i, fn in enumerate(func_names):
    valid = valid_sets[i]
    row = []
    for j, letter in enumerate(letter_list):
        is_valid = letter in valid
        row.append(1 if is_valid else 0)
    adjacency.append(row)
    valid_letters_for_func = [letter_list[j] for j in range(11) if row[j]]
    print(f"  {fn:>30}: {valid_letters_for_func}")

# Count perfect matchings using inclusion-exclusion (permanent of matrix)
# For an 11x11 matrix, Ryser's formula computes the permanent efficiently.

def permanent_ryser(matrix):
    """Compute permanent of an n x n 0-1 matrix using Ryser's formula.
    Uses the Gray code variant for efficiency.
    permanent(A) = (-1)^n sum_{S subset [n]} (-1)^|S| prod_i (sum_{j in S} a_ij)
    """
    n = len(matrix)
    # Pre-compute row sums for the empty set (all zeros)
    # Ryser: perm = (-1)^n * sum over S of (-1)^|S| * prod_i(row_i dot indicator_S)

    # We iterate over all 2^n subsets of columns
    total = 0
    for s_mask in range(1 << n):
        s_size = bin(s_mask).count('1')

        # Compute product over rows of (sum of selected columns in that row)
        product = 1
        for i in range(n):
            row_sum = 0
            for j in range(n):
                if s_mask & (1 << j):
                    row_sum += matrix[i][j]
            product *= row_sum
            if product == 0:
                break  # optimization: if any row sum is 0, product is 0

        if s_size % 2 == (n % 2):
            total += product
        else:
            total -= product

    return total

print("\nComputing permanent of bipartite adjacency matrix (Ryser's formula)...")
n_valid_permutations = permanent_ryser(adjacency)
n_total_permutations = math.factorial(11)

p_permutation = n_valid_permutations / n_total_permutations if n_total_permutations > 0 else 0

print(f"\nTotal permutations: {n_total_permutations:,}")
print(f"Valid permutations (all letters match a function): {n_valid_permutations:,}")
print(f"P(random permutation is all-valid): {p_permutation:.6f}")
print(f"  = approximately 1 in {1/p_permutation:,.1f}" if p_permutation > 0 else "  = 0")

# Now the STRONGER test: of those valid permutations, how many match
# the SPECIFIC claimed assignment?
# Answer: exactly 1 (the claimed mapping itself).
# So P(getting exactly this mapping | random permutation) = 1/n_total_permutations
# But that's trivially small (1/40M). The real question is the coverage test above.

# =============================================================================
# SECTION 7: CRITICAL WEAKNESSES IN THE HYPOTHESIS
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 7: CRITICAL WEAKNESSES & CONFOUNDS")
print("=" * 80)

print("""
WEAKNESS 1: HEATING verbs start with MANY letters
  k (kochen), e (erhitzen, erwärmen, einheizen), h (heizen), s (sieden, schmelzen),
  b (brennen, brauen, beheizen), g (glühen), a (anfeuern, anheizen), d (dünsten),
  w (wärmen), r (rösten), c (calcinieren)
  -> 11 different first letters for "heat" alone
  -> Almost ANY letter could be mapped to "heat" via some verb

WEAKNESS 2: COOLING has few verbs, but 'e' is ambiguous
  'erkalten' starts with e = COOL — but so do:
  'erhitzen' starts with e = HEAT (opposite!)
  'erwärmen' starts with e = HEAT (opposite!)
  'einkochen' starts with e = HEAT
  The prefix 'er-' is one of the most common German verb prefixes.
  It could map to almost anything.

WEAKNESS 3: German prefix verbs inflate coverage artificially
  German compound verbs (ab-, an-, auf-, aus-, be-, ein-, er-, ver-, zu-, etc.)
  mean that letters a, b, e, v, z have artificially high coverage.
  This is a STRUCTURAL FEATURE of German, not evidence for the hypothesis.
  Specifically:
    a- (ab-, an-, auf-, aus-): covers almost every function
    e- (ein-, er-): covers almost every function
    v- (ver-): covers many functions
  These prefixes are so productive that ANY function maps to a/e/v.

WEAKNESS 4: The hypothesis is asymmetric
  k->kochen: clear, specific mapping
  e->erkalten: ONE of many er- verbs (erhitzen means the OPPOSITE)
  h->halten: works, but heizen (heat) also starts with h
  d->dichten: works, but destillieren (separate) also starts with d
  t->treiben: works, but trennen (separate) also starts with t
  s->scheiden: works, but sieden (boil) also starts with s
  g->gar: this is an ADJECTIVE, not a verb (gar sein = to be done)
  m->messen: works fairly well (mischen is different)
  r->rühren: works well (most specific match)
  l->lassen: works, but läutern/lösen also start with l
  p->pause: this is actually a NOUN, not a verb (pausieren)

WEAKNESS 5: Cherry-picking the "best" verb
  For k, you pick kochen and ignore kühlen (cool = OPPOSITE of claimed function)
  For e, you pick erkalten and ignore erhitzen (heat = OPPOSITE)
  For h, you pick halten and ignore heizen (different function)
  For d, you pick dichten and ignore destillieren (different function)
  For s, you pick scheiden and ignore sieden (different function)
  This IS the definition of cherry-picking.

WEAKNESS 6: 'qo' requires switching to Latin
  The hypothesis can't sustain itself within German alone.
  When the mapping fails (no German q- distillation verb), it switches
  to Latin 'coquo'. This is a degrees-of-freedom problem.
""")

# =============================================================================
# SECTION 8: WHAT ACTUALLY HOLDS UP
# =============================================================================

print("=" * 80)
print("SECTION 8: WHAT ACTUALLY HOLDS UP")
print("=" * 80)

print("""
STRENGTH 1: k->kochen is strong
  'kochen' is arguably THE primary German verb for boiling/cooking.
  No other letter maps to "heat" as directly as k->kochen.
  However: heizen (h), sieden (s), and brennen (b) are all common.

STRENGTH 2: r->rühren is fairly specific
  'rühren' is the primary German verb for stirring.
  Most stirring verbs are compounds: umrühren, einrühren, verrühren, durchrühren.
  The root form IS 'rühren', and it starts with r.

STRENGTH 3: m->messen is moderately specific
  'messen' is the primary German verb for measuring.
  The main alternatives (wägen, wiegen) start with w, not m.
  But mischen (mix) also starts with m.

STRENGTH 4: The STRUCTURAL functions were derived first
  The functions (ENERGY_DRIVER, STABILITY_ANCHOR, PHASE_MANAGER) were determined
  from distributional analysis BEFORE the German mapping was proposed.
  This means at least the functions aren't retrofitted to the German.
  The question is whether the letter-verb mapping is retrofitted.

WEAKNESS RECAP:
  The German distillation vocabulary is rich enough that for most consonants,
  you CAN find a verb starting with that letter whose meaning is in the
  general neighborhood of the claimed function. The high coverage rate
  ({coverage:.0%}) makes the naive letter-match test non-significant.

  The SEMANTIC precision test is more interesting but still undermined by
  the fact that for most letters, there are competing verbs that mean
  something entirely different.
""".format(coverage=len(covered)/26*100))

# =============================================================================
# SECTION 9: FINAL VERDICT
# =============================================================================

print("=" * 80)
print("SECTION 9: FINAL VERDICT")
print("=" * 80)

print(f"""
STATISTICAL SUMMARY:
  Test 1 (Letter coverage):     p = {p_naive:.4f} — NOT significant
  Test 2 (Forward precision):   {wins}/11 letters beat random baseline
  Test 3 (Reverse probability): p = {p_product:.8f} — 1 in {1/p_product:,.0f}
  Test 4 (Permutation):         p = {p_permutation:.6f}  — 1 in {1/p_permutation:,.1f} (valid permutations)

INTERPRETATION:

  Test 1 shows that finding A German distillation verb for any given letter
  is not hard. The coverage rate is very high. This is the null hypothesis's
  strongest point.

  Test 3 gives an apparently impressive p-value, but it ASSUMES that each
  function has only a small number of "valid" first letters (those found in
  our reverse test). This assumption is fragile — a more thorough search of
  German vocabulary would likely find more alternative verbs for each function,
  increasing the valid letter count and weakening the result.

  Test 4 (permutation test) asks: if you shuffled the 11 letter-function
  assignments randomly, how often would you get a valid matching?
  P = {p_permutation:.6f} means about 1 in {1/p_permutation:,.0f} random shuffles work.
  This is {'mildly interesting but not conclusive' if p_permutation > 0.01 else 'statistically suggestive' if p_permutation > 0.001 else 'statistically significant'}.

HONEST ASSESSMENT:

  The hypothesis IS partially cherry-picked. For most consonants, German
  offers MULTIPLE distillation verbs with DIFFERENT meanings, and the
  hypothesis selects the one that fits. The competing verbs (erhitzen vs
  erkalten for 'e', heizen vs halten for 'h', sieden vs scheiden for 's')
  show that the same letter could plausibly map to opposite functions.

  HOWEVER: The fact that the structural functions were derived INDEPENDENTLY
  from distributional analysis (not from German) is important. The hypothesis
  is not "what do these letters mean in German?" but rather "having determined
  what these letters DO structurally, is there a German verb that matches?"
  This ordering matters for cherry-picking analysis.

  The strongest individual mappings are:
    k -> kochen (heat): STRONG — kochen is THE heat verb
    r -> rühren (stir):  STRONG — rühren is THE stir verb
    m -> messen (measure): MODERATE — messen is A primary measure verb
    l -> lassen (allow): MODERATE — lassen is common for "let"

  The weakest are:
    e -> erkalten (cool): WEAK — e- prefix covers EVERYTHING (including erhitzen=heat)
    g -> gar (done): WEAK — adjective not verb, and gären means ferment
    p -> pause: WEAK — borrowed word, not a traditional German workshop term
    qo -> coquo: WEAK — requires switching to Latin

CONCLUSION:
  The German abbreviation hypothesis shows some genuine correspondences
  (k->kochen, r->rühren) mixed with likely cherry-picking (e->erkalten,
  g->gar, p->pause). The null hypothesis — that German's rich vocabulary
  allows post-hoc matching for any letter — cannot be rejected at
  conventional significance levels when considering the cherry-picking
  confound.

  Statistical evidence: INSUFFICIENT TO CONFIRM OR REJECT.
  The hypothesis is PLAUSIBLE for 3-4 of the 11 mappings and WEAK for
  the remaining 7-8.
""")

# Save results
results = {
    'total_verbs_compiled': len(VERBS),
    'letter_coverage': {
        'covered': len(covered),
        'total': 26,
        'rate': len(covered) / 26,
        'covered_letters': sorted(covered),
        'uncovered_letters': sorted(uncovered),
    },
    'naive_probability': {
        'p_hypergeometric': p_naive,
        'p_binomial': p_binomial,
        'significant_at_05': p_naive < 0.05,
    },
    'forward_test': forward_results,
    'reverse_test': {fn: {k: v for k, v in rr.items()} for fn, rr in reverse_results.items()},
    'permutation_test': {
        'total_permutations': n_total_permutations,
        'valid_permutations': n_valid_permutations,
        'p_value': p_permutation,
    },
    'reverse_combined_p': p_product,
    'forward_wins': wins,
    'strong_mappings': ['k_kochen', 'r_rühren', 'm_messen'],
    'weak_mappings': ['e_erkalten', 'g_gar', 'p_pause', 'qo_coquo'],
    'verdict': 'INSUFFICIENT_TO_CONFIRM_OR_REJECT',
}

import os
results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
os.makedirs(results_dir, exist_ok=True)
output_path = os.path.join(results_dir, 'german_abbreviation_test.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nResults saved to: {output_path}")
