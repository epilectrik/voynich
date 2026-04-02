#!/usr/bin/env python3
"""
Featurize the top 20 compound recipes from Brunschwig's 1512 Large Book
for matching against Voynich folios.

Extracts 4-channel features (k/h/t/e) plus structural metadata from
each recipe's actual text.

Output: brunschwig_1512_compound_features.json
"""

import json
import re
import os

# ── Recipe definitions ──────────────────────────────────────────────

RECIPES = [
    {
        "recipe_idx": 0,
        "name": "Quintessence (pelican method)",
        "lines": "3687-3784",
        "start": 3687, "end": 3784,
    },
    {
        "recipe_idx": 1,
        "name": "Albertus Magnus Aqua Vitae",
        "lines": "11875-11918",
        "start": 11875, "end": 11918,
    },
    {
        "recipe_idx": 2,
        "name": "Drink of Youth / Second Balsam",
        "lines": "12293-12329",
        "start": 12293, "end": 12329,
    },
    {
        "recipe_idx": 3,
        "name": "Anti-pestilence Aqua Vitae (1511)",
        "lines": "12445-12543",
        "start": 12445, "end": 12543,
    },
    {
        "recipe_idx": 4,
        "name": "Fourth Aqua Vitae Composita",
        "lines": "12596-12621",
        "start": 12596, "end": 12621,
    },
    {
        "recipe_idx": 5,
        "name": "Pfalzgraf Aqua Vitae",
        "lines": "12630-12675",
        "start": 12630, "end": 12675,
    },
    {
        "recipe_idx": 6,
        "name": "Sixth Aqua Vitae / Water of Life",
        "lines": "12684-12760",
        "start": 12684, "end": 12760,
    },
    {
        "recipe_idx": 7,
        "name": "Turpentine/Honey Aqua Vitae",
        "lines": "13098-13236",
        "start": 13098, "end": 13236,
    },
    {
        "recipe_idx": 8,
        "name": "Bishop of Strasbourg's Aqua Vitae",
        "lines": "13490-13530",
        "start": 13490, "end": 13530,
    },
    {
        "recipe_idx": 9,
        "name": "Grand Aqua Vitae Composita",
        "lines": "15426-15641",
        "start": 15426, "end": 15641,
    },
    {
        "recipe_idx": 10,
        "name": "Theriac (Andromachus + Galen)",
        "lines": "16083-16688",
        "start": 16083, "end": 16688,
    },
    {
        "recipe_idx": 11,
        "name": "Mithridate",
        "lines": "16288-16423",
        "start": 16288, "end": 16423,
    },
    {
        "recipe_idx": 12,
        "name": "Artificial Balsam (Gentile's)",
        "lines": "8608-8663",
        "start": 8608, "end": 8663,
    },
    {
        "recipe_idx": 13,
        "name": "Aurum Potabile (amalgam method)",
        "lines": "22157-22261",
        "start": 22157, "end": 22261,
    },
    {
        "recipe_idx": 14,
        "name": "Hair growth water",
        "lines": "33407-33419",
        "start": 33407, "end": 33419,
    },
    {
        "recipe_idx": 15,
        "name": "Hair color-change water",
        "lines": "33431-33449",
        "start": 33431, "end": 33449,
    },
    {
        "recipe_idx": 16,
        "name": "Noble Memory Water",
        "lines": "33520-33596",
        "start": 33520, "end": 33596,
    },
    {
        "recipe_idx": 17,
        "name": "Anti-melancholy Heart Water",
        "lines": "33724-33741",
        "start": 33724, "end": 33741,
    },
    {
        "recipe_idx": 18,
        "name": "Cold-type Dizziness Water",
        "lines": "33638-33645",
        "start": 33638, "end": 33645,
    },
    {
        "recipe_idx": 19,
        "name": "Anti-drunkenness Water",
        "lines": "33649-33655",
        "start": 33649, "end": 33655,
    },
]


# ── Keyword patterns ────────────────────────────────────────────────

# k_channel: heat/thermal keywords
K_PATTERNS = {
    'gentle': [r'\bgentle\s+fire\b', r'\bgentle\s+heat\b', r'\bgentle\b.*\bfire\b',
               r'\blukewarm\b', r'\bpleasantly\s+warm\b', r'\bwarm\b(?!.*\bstrong\b)'],
    'moderate': [r'\bash\s*(?:bath|bed)\b', r'\bsand\s*(?:bath|bed)\b', r'\bmoderate\b',
                 r'\bcoal\b', r'\bcoals\b'],
    'strong': [r'\bstrong\s+fire\b', r'\bincrease\s+(?:the\s+)?fire\b', r'\bflame\b',
               r'\bboil(?:ing|ed|s)?\b', r'\bred\s+(?:as|like|hot)\b', r'\bglowing\b',
               r'\bfury\b', r'\brushing\b'],
}

K_ALL = [
    r'\bfire\b', r'\bheat(?:ed|ing|s)?\b', r'\bwarm(?:th|ed|ing|s)?\b',
    r'\bhot\b', r'\bburn(?:ed|t|ing|s)?\b', r'\bflame\b',
    r'\bcoal(?:s)?\b', r'\bfurnace\b', r'\bbalneum\b', r'\bbath\b',
    r'\bash\b(?!\s+tree)', r'\bgentle\s+fire\b', r'\bstrong\s+fire\b',
    r'\bdegree\b', r'\bboil(?:ing|ed|s)?\b', r'\bglowing\b',
    r'\blukewarm\b',
]

# h_channel: monitoring/observation keywords
H_COLOR = [
    r'\bred\b', r'\bwhite\b', r'\byellow\b', r'\bblack\b',
    r'\bclear\b', r'\bsky-?blue\b', r'\bgreen\b', r'\bgold(?:en)?\b',
    r'\bbrown(?:ish)?\b', r'\btransparent\b',
]

H_CONSISTENCY = [
    r'\bthick\b', r'\bthin\b', r'\bconsistency\b', r'\bviscous\b',
    r'\blike\s+oil\b', r'\blike\s+honey\b', r'\bpaste\b', r'\bmush\b',
    r'\bpowder(?:ed)?\b', r'\bfine(?:ly)?\b', r'\bcoarse(?:ly)?\b',
]

H_VOLATILITY = [
    r'\bvapor\b', r'\bfume(?:s)?\b', r'\bsmoke\b', r'\bspirit(?:s)?\b',
    r'\bevaporat(?:e|ed|es|ing)\b', r'\bescap(?:e|es|ed|ing)\b',
    r'\brising\b', r'\bdescending\b', r'\bfragran(?:ce|t)\b',
    r'\bscent\b', r'\bsmell\b', r'\bflavor\b', r'\btaste\b',
]

H_ALL = [
    r'\bsee(?:s|n)?\b', r'\bobserv(?:e|ed|ing)\b', r'\bwatch\b',
    r'\bappear(?:s|ed|ing)?\b', r'\bcolor\b', r'\bsmell(?:s|ed)?\b',
    r'\btaste\b', r'\bsign(?:s)?\b', r'\bnotice\b', r'\blook\b',
    r'\btest\b', r'\bverif(?:y|ied)\b', r'\bexamine\b', r'\binspect\b',
    r'\bdisplay(?:ed)?\b', r'\bproven\b',
] + H_COLOR + H_CONSISTENCY + H_VOLATILITY

# t_channel: termination/endpoint keywords
T_THRESHOLD = [
    r'\buntil\b', r'\bwhen\b(?!.*\byear\b)', r'\bonce\b.*\b(?:done|complete|ready)\b',
    r'\bready\b', r'\bcomplete(?:ly|d|ion)?\b',
]

T_TIME = [
    r'\b\d+\s*(?:day|days|night|nights|hour|hours|week|weeks|month|months|year|years)\b',
    r'\bthree\s+(?:day|days|week|weeks)\b', r'\beight\s+(?:day|days)\b',
    r'\bforty\s+(?:day|days)\b', r'\bfourteen\s+(?:day|days)\b',
    r'\bthirty\s+(?:day|days)\b', r'\bsix\s+(?:month|months)\b',
]

T_ALL = [
    r'\buntil\b', r'\bwhen\b', r'\bcomplete(?:ly|d|ion)?\b',
    r'\bfinish(?:ed|ing)?\b', r'\bcease(?:s|d)?\b', r'\bstop\b',
    r'\bdone\b', r'\benough\b', r'\bperfect(?:ly|ed)?\b',
    r'\bsufficient(?:ly)?\b', r'\bready\b',
]

# e_channel: correction/caution keywords
E_RECOVERABLE = [
    r'\badd\s+(?:more|thereto)\b', r'\bpour\s+(?:back|it\s+back)\b',
    r'\bif\s+.*\btoo\b', r'\bstir\b',
]

E_FATAL = [
    r'\bdestroy(?:ed|ing)?\b', r'\bspoil(?:ed|ing|s)?\b',
    r'\bcorrupt(?:ed|ing)?\b', r'\blost?\b.*\b(?:strength|power|virtue)\b',
    r'\bruined\b', r'\birrecoverable\b',
]

E_ALL = [
    r'\bcareful(?:ly)?\b', r'\berror(?:s)?\b', r'\bspoil(?:ed|ing|s)?\b',
    r'\bcorrupt(?:ed|ing)?\b', r'\bdanger(?:ous)?\b', r'\bburn(?:ed|t)?\b',
    r'\bdestroy(?:ed|ing)?\b', r'\bfail(?:ed|ing|s)?\b',
    r'\bdamage(?:d|s)?\b', r'\bharm(?:ed|ful)?\b',
    r'\bnot\b', r'\blest\b', r'\bgreat\s+care\b',
    r'\bwell\s+sealed\b', r'\bno\s+(?:vapor|air)\b',
    r'\blose(?:s)?\b', r'\bpoisonous\b', r'\bfrightful\b',
    r'\bincorrect\b', r'\bfalsely\b',
]

E_DRIFT = [
    r'\bdiminish(?:ed|ing)?\b', r'\btoo\s+(?:much|little|hot|cold|old)\b',
    r'\bnot\s+(?:properly|correctly|well)\b', r'\bweaken(?:ed)?\b',
    r'\bchange(?:d|s)?\b.*\bturn\b',
]


# ── Helper functions ────────────────────────────────────────────────

def count_pattern_matches(text, patterns):
    """Count total matches across multiple regex patterns in text."""
    total = 0
    for pat in patterns:
        total += len(re.findall(pat, text, re.IGNORECASE))
    return total


def count_words(text):
    """Count words in text, excluding page markers and woodcut notes."""
    # Remove page markers and woodcut annotations
    cleaned = re.sub(r'---\s*Page\s+\d+.*?---', '', text)
    cleaned = re.sub(r'\[WOODCUT:.*?\]', '', cleaned)
    words = re.findall(r'[a-zA-Z]+', cleaned)
    return len(words)


def extract_heat_mentions(text):
    """Classify heat mentions by intensity level (1=gentle, 2=moderate, 3=strong)."""
    mentions = []
    for pat in K_PATTERNS['gentle']:
        for m in re.finditer(pat, text, re.IGNORECASE):
            mentions.append((m.start(), 1))
    for pat in K_PATTERNS['moderate']:
        for m in re.finditer(pat, text, re.IGNORECASE):
            mentions.append((m.start(), 2))
    for pat in K_PATTERNS['strong']:
        for m in re.finditer(pat, text, re.IGNORECASE):
            mentions.append((m.start(), 3))
    mentions.sort(key=lambda x: x[0])
    return mentions


def count_ingredients(text):
    """
    Count distinct named materials/ingredients.
    Looks for patterns like "Take X", "X -- N lot", ingredient list items.
    """
    ingredients = set()

    # Parenthetical Latin/German names are strong ingredient markers
    paren_matches = re.findall(r'([A-Z][a-z]+(?:\s+[a-z]+)*)\s*\(', text)
    for m in paren_matches:
        # Skip common non-ingredient parens
        if m.lower() not in {'page', 'that', 'which', 'each', 'the', 'this',
                              'recipe', 'book', 'chapter', 'note', 'item'}:
            ingredients.add(m.lower())

    # "Take X" patterns
    take_matches = re.findall(r'[Tt]ake\s+([A-Z][a-z]+(?:\s+[a-z]+){0,3})', text)
    for m in take_matches:
        word = m.split()[0].lower()
        if word not in {'the', 'all', 'one', 'this', 'that', 'it', 'a', 'these',
                        'thereof', 'therein', 'thereto', 'good', 'noble', 'fine',
                        'fresh', 'best', 'very', 'white', 'red', 'proper'}:
            ingredients.add(m.lower().rstrip(',. '))

    # Capitalized ingredient entries (standalone lines or list items)
    line_items = re.findall(r'^([A-Z][a-z]+(?:\s+[a-z]+){0,4})\s*(?:,|--|each|one|two|three|four|half|\d)',
                            text, re.MULTILINE)
    for m in line_items:
        word = m.split()[0].lower()
        if word not in {'take', 'the', 'this', 'that', 'all', 'these', 'and',
                        'but', 'item', 'note', 'first', 'second', 'third',
                        'then', 'recipe', 'also', 'afterward', 'thereafter',
                        'what', 'which', 'if', 'for', 'not', 'when', 'how',
                        'its', 'let', 'do', 'put', 'set'}:
            ingredients.add(m.lower().rstrip(',. '))

    # "Recipe:" entries (Latin pharmacopeia)
    recipe_items = re.findall(r'(?:Recipe:\s*)?([A-Z][a-z]+(?:\s+[a-z]+){0,3})\s*(?:--|\()',
                              text)
    for m in recipe_items:
        word = m.split()[0].lower()
        if word not in {'recipe', 'take', 'the', 'this', 'that', 'page', 'and',
                        'item', 'thereof'}:
            ingredients.add(m.lower().rstrip(',. '))

    return len(ingredients)


def count_steps(text):
    """Count distinct operational steps in the recipe."""
    step_patterns = [
        r'\bdistill(?:ed|ing)?\b',
        r'\bdigest(?:ed|ing|ion)?\b',
        r'\bpour\s+(?:back|over|it)\b',
        r'\bgrind\b|\bpound(?:ed|ing)?\b|\bcrush(?:ed|ing)?\b',
        r'\bmix(?:ed|ing)?\b(?!\s+up)',
        r'\bsteep\b|\bsoak\b',
        r'\bseal(?:ed|ing)?\b',
        r'\bstrain(?:ed|ing)?\b|\bfiltr(?:ation|um)\b',
        r'\bstir(?:red|ring)?\b',
        r'\bclarif(?:y|ied|ying)\b|\bskim(?:med|ming)?\b',
        r'\bcalcin(?:e|ed|ation)\b',
        r'\brectif(?:y|ied|ying)\b',
        r'\bchop(?:ped|ping)?\b',
        r'\bwash(?:ed|ing)?\b',
        r'\b(?:set|place)\s+(?:in|it)\b.*\b(?:sun|horse|dung|earth|balneum)\b',
        r'\bcirculat(?:e|ed|ing|ion)\b',
        r'\bamalga(?:m|mated|mating)\b',
        r'\bdissolv(?:e|ed|ing)\b',
        r'\bburn(?:ed|t|ing)?\b(?:.*\baway\b)?',
    ]
    total = 0
    for pat in step_patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        if matches:
            total += len(matches)
    # Normalize: each cluster of related steps counts once
    # But keep raw count as proxy for procedural complexity
    return max(1, total)


def has_keyword(text, patterns):
    """Return True if any pattern matches."""
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


# ── Manual overrides for structural features ────────────────────────
# Based on careful reading of each recipe's actual text

MANUAL_OVERRIDES = {
    0: {  # Quintessence (pelican)
        "primary_technique": "circulation",
        "fire_degree": 1,
        "has_cohobation": False,
        "has_digestion": False,
        "has_circulation": True,
        "n_ingredients_override": 1,  # Just burnt wine
        "n_steps_override": 5,  # burn wine, distill 7x, put in pelican, circulate, test
    },
    1: {  # Albertus Magnus AV
        "primary_technique": "distillation",
        "fire_degree": 1,
        "has_cohobation": True,   # "pour it back over the spices"
        "has_digestion": True,    # "balneum Mariae to digest"
        "has_circulation": False,
        "n_ingredients_override": 10,  # ginger, cinnamon, cubeb, cloves, nutmeg, mace, cardamom, zedoary, galangal, long pepper
        "n_steps_override": 6,  # grind, steep, digest 43 days, distill BM, cohobate, re-digest+distill
    },
    2: {  # Drink of Youth
        "primary_technique": "distillation",
        "fire_degree": 1,
        "has_cohobation": True,   # "pour it back over the feces"
        "has_digestion": True,    # "horse manure to digest" + "Balneum Mariae"
        "has_circulation": False,
        "n_ingredients_override": 14,  # sage, nutmeg, cloves, ginger, grains of paradise, cinnamon, laurel oil, castoreum, spikenard, rosemary herb+flowers, rue, marjoram, citrus rind
        "n_steps_override": 7,  # grind, combine, digest in horse dung, distill BM, cohobate, distill 2nd, distill in ash bath
    },
    3: {  # Anti-pestilence AV (1511)
        "primary_technique": "distillation",
        "fire_degree": 1,
        "has_cohobation": False,
        "has_digestion": True,    # "digest for eight days"
        "has_circulation": False,
        "n_ingredients_override": 27,  # Pearl confection, ambergris, musk, Galen's joy, rose confection, sandalwood, liberans, bezoar electuary, theriac, mithridate, white dittany, burnet saxifrage, masterwort, angelica, elecampane, birthwort, Armenian bole, sealed earth, rhubarb, spodium, ivory, clove buds, musk, ambergris, saffron, sugar, syrups
        "n_steps_override": 4,  # combine, digest 8 days, distill BM, add finishing ingredients
    },
    4: {  # Fourth AV Composita
        "primary_technique": "distillation",
        "fire_degree": 1,
        "has_cohobation": True,   # "pour it back over the feces"
        "has_digestion": True,    # "putrefy for eight days in horse manure"
        "has_circulation": False,
        "n_ingredients_override": 3,  # cloves, white ginger, rosemary herb
        "n_steps_override": 5,  # grind, seal, putrefy, distill BM, cohobate 2x
    },
    5: {  # Pfalzgraf AV
        "primary_technique": "distillation",
        "fire_degree": 1,
        "has_cohobation": True,   # "pour back over the residue"
        "has_digestion": True,    # "bury in earth for thirty days"
        "has_circulation": False,
        "n_ingredients_override": 24,  # sage, nutmeg, mace, ginger, grains of paradise, cinnamon, galangal, zedoary, camphor, rhubarb, rosemary, lavender, marjoram, rue, chamomile, masterwort, fennel, red roses, betony, southernwood, castoreum, spikenard, long pepper, laurel oil
        "n_steps_override": 7,  # pound/chop/crush, combine, seal, bury 30 days, distill BM, cohobate, distill 3x
    },
    6: {  # Sixth AV / Water of Life
        "primary_technique": "distillation",
        "fire_degree": 1,
        "has_cohobation": False,
        "has_digestion": True,    # "digest for two days"
        "has_circulation": False,
        "n_ingredients_override": 8,  # herbs (unspecified), roots, spices, musk, ambergris, camphor, sugar + base spirit
        "n_steps_override": 9,  # digest herbs 2 days, distill BM, add spices, steep 8 days, distill again, add finishing, stir, settle, decant through cloth
    },
    7: {  # Turpentine/Honey AV
        "primary_technique": "distillation",
        "fire_degree": 2,
        "has_cohobation": False,
        "has_digestion": True,    # "digest in horse manure for eight days"
        "has_circulation": False,
        "n_ingredients_override": 38,  # turpentine, honey, grains of paradise, bugloss, saffron, borage, rhubarb, lemon balm, sage, fir tips, hyssop, chamomile, blessed thistle, vervain, rosemary, wormwood, musk, aloeswood, balm of Gilead, sandalwood, sweet flag, lavender, citron, laserwort, caraway, mace, nutmeg, cinnamon, galangal, cloves, cubeb, ginger, long pepper, saffron again, grains of paradise, cardamom, camel grass, coriander, juniper, orris root + more
        "n_steps_override": 8,  # wash turpentine, clarify honey, mix, steep 8 days, distill ash bath, add musk (no re-distill), add spices, digest again
    },
    8: {  # Bishop of Strasbourg's AV
        "primary_technique": "infusion",
        "fire_degree": 1,
        "has_cohobation": False,
        "has_digestion": False,
        "has_circulation": False,
        "n_ingredients_override": 4,  # sage water, rosemary water, the aqua vitae itself, bath sponge
        "n_steps_override": 3,  # mix waters, soak sponge, rub limbs
    },
    9: {  # Grand AV Composita
        "primary_technique": "distillation",
        "fire_degree": 1,
        "has_cohobation": False,
        "has_digestion": True,    # "stand for three days in Balneum Mariae"
        "has_circulation": False,
        "n_ingredients_override": 58,  # Massive recipe: sage, rosemary, cinnamon, ginger, cloves, nutmeg, grains of paradise, sweet flag, galangal, long pepper, zedoary, mace, cardamom, cubeb, rue, marjoram, lavender, roses, theriac, mithridate, laurel oil, citron, borage, rosemary flowers, masterwort, angelica, rhapontic, juniper, mint varieties, motherwort, castoreum, vervain, betony, aloeswood, balm of Gilead, spikenard, oak mistletoe, peony, rhubarb, St John's wort, pennyroyal, basil, fennel, leopard's bane, saffron, ambergris, musk, camphor, sugar, gold ducats, plus 8 pharmacopeia species
        "n_steps_override": 7,  # grind coarsest, distill BM 14 days (slow), add camphor+musk, digest 3 days lukewarm BM, filter per filtrum, add species+gold+sugar
    },
    10: {  # Theriac
        "primary_technique": "infusion",
        "fire_degree": 1,
        "has_cohobation": False,
        "has_digestion": True,    # 6-month fermentation/blending
        "has_circulation": False,
        "n_ingredients_override": 64,  # Explicitly stated: "64 simplicia and composita"
        "n_steps_override": 12,  # soak opium in wine, grind scordeon, soften acacia+hypocist, pound gums, prepare saffron+agaric, warm honey, add species in stages, add opium, add garlic, add storax+turpentine, add gums warmed, strain, add balsam, store+stir schedule over 6 months
    },
    11: {  # Mithridate
        "primary_technique": "infusion",
        "fire_degree": 1,
        "has_cohobation": False,
        "has_digestion": True,    # compound preparation with honey
        "has_circulation": False,
        "n_ingredients_override": 72,  # Even larger ingredient list than Theriac
        "n_steps_override": 4,  # soften appropriate ingredients, pound and sift dry, combine with honey, store
    },
    12: {  # Artificial Balsam (Gentile's)
        "primary_technique": "distillation",
        "fire_degree": 2,
        "has_cohobation": False,
        "has_digestion": True,    # "set in Balneum Mariae for three days to digest"
        "has_circulation": True,  # "place it in a circulatorium and let it circulate"
        "n_ingredients_override": 19,  # aloeswood, opopanax, pine resin, bdellium, galbanum, mastic, sarcocolla, blessed oil, carpobalsamum, xylobalsamum, opobalsamum, laurel oil, dragon's blood, galangal, castoreum, mace, cinnamon, cardamom, grains of paradise, citron peel, turpentine oil, tree oil, plus labdanum and frankincense
        "n_steps_override": 8,  # crush gums, steep in spirit, digest BM 3 days, add powdered spices+oils, digest again 3 days, distill in ashes, collect 3 fractions (water/yellow/brown), sun exposure or circulate 14 days
    },
    13: {  # Aurum Potabile
        "primary_technique": "calcination",
        "fire_degree": 3,
        "has_cohobation": False,
        "has_digestion": False,
        "has_circulation": False,
        "n_ingredients_override": 7,  # sal ammoniac, saltpeter, sulfur, sublimated mercury, gold, quicksilver, saffron
        "n_steps_override": 10,  # grind salts, distill aqua fortis, beat gold into plates, heat mercury in crucible, amalgamate, pour into cold water, add sulfur, heat to burn sulfur, calcine in crucible till red, dissolve in aqua fortis, distill per alembic
    },
    14: {  # Hair growth water
        "primary_technique": "distillation",
        "fire_degree": 2,
        "has_cohobation": False,
        "has_digestion": False,
        "has_circulation": False,
        "n_ingredients_override": 3,  # virgin honey, Venetian liquorice, marshmallow root
        "n_steps_override": 5,  # powder ingredients, combine in cucurbit, distill in ash bath (collect white then yellow fractions), set in sun 1-2 months, apply with brush
    },
    15: {  # Hair color-change water
        "primary_technique": "distillation",
        "fire_degree": 1,
        "has_cohobation": False,
        "has_digestion": True,    # "putrefy" in balneum Mariae
        "has_circulation": False,
        "n_ingredients_override": 7,  # burned wine tartar, white lily water, lily of valley water, lovage water, egg whites, brimstone, rock salt
        "n_steps_override": 5,  # mix, seal with blind helm, digest/putrefy BM 3 days, distill BM, set in sun 1 month
    },
    16: {  # Noble Memory Water
        "primary_technique": "distillation",
        "fire_degree": 1,
        "has_cohobation": True,   # "pour the water back over it"
        "has_digestion": True,    # "putrefy for three days in horse dung"
        "has_circulation": False,
        "n_ingredients_override": 23,  # marjoram water, rosemary water, iris water, bugloss water, lemon balm water, borage water, yellow violet water, red rose water, cinnamon, cardamom, ginger, cubeb, spikenard, clove leaves, galangal, long pepper, camel grass, senna, burnt ivory, red coral, mastic, storax calamite, burnt silk, musk
        "n_steps_override": 8,  # combine waters, add spices, putrefy 3 days horse dung, distill BM (very slow), grind residue, cohobate, repeat 3x, hang musk in silk, set in sun 1 month
    },
    17: {  # Anti-melancholy Heart Water
        "primary_technique": "distillation",
        "fire_degree": 1,
        "has_cohobation": True,   # "distilled three times"
        "has_digestion": True,    # "digested for 8 days in horse dung"
        "has_circulation": False,
        "n_ingredients_override": 16,  # bugloss water, borage water, basil water, lemon balm water, rosemary water, yellow violet water, germander water, polypody water, hart's tongue water, tamarisk water, dya pliris species, dya anthos species, leticie Galieni species
        "n_steps_override": 5,  # combine, digest 8 days horse dung, distill BM, repeat 3x, rectify 40 days sun
    },
    18: {  # Cold-type Dizziness Water
        "primary_technique": "distillation",
        "fire_degree": 1,
        "has_cohobation": True,   # "pouring it back over the residue three times"
        "has_digestion": True,    # "steep in wine 8-14 days in horse dung"
        "has_circulation": False,
        "n_ingredients_override": 6,  # origanum, mountain germander, cinquefoil, avens, calamint, mountain parsley
        "n_steps_override": 5,  # pound herbs, steep 8-14 days horse dung, distill BM, cohobate 3x, rectify 40 days sun
    },
    19: {  # Anti-drunkenness Water
        "primary_technique": "distillation",
        "fire_degree": 1,
        "has_cohobation": True,   # "water poured back over the residue"
        "has_digestion": True,    # "digest for 8 days in horse dung"
        "has_circulation": False,
        "n_ingredients_override": 3,  # peony water, dog's gourd water, crushed almonds
        "n_steps_override": 5,  # mix, digest 8 days horse dung, distill BM (very slow), cohobate to 3rd time, set in sun 40 days
    },
}


# ── Main featurization ─────────────────────────────────────────────

def featurize_recipe(text, recipe_def):
    """Extract all 4-channel features from recipe text."""
    idx = recipe_def["recipe_idx"]
    override = MANUAL_OVERRIDES.get(idx, {})

    n_words = count_words(text)
    if n_words == 0:
        n_words = 1  # avoid division by zero

    # -- Structural metadata (use overrides based on close reading) --
    n_ingredients = override.get("n_ingredients_override", count_ingredients(text))
    n_steps = override.get("n_steps_override", count_steps(text))
    primary_technique = override.get("primary_technique", "distillation")
    fire_degree = override.get("fire_degree", 1)
    has_cohobation = override.get("has_cohobation", False)
    has_digestion = override.get("has_digestion", False)
    has_circulation = override.get("has_circulation", False)

    # -- k_channel (heat/thermal) --
    k_total = count_pattern_matches(text, K_ALL)
    heat_rate = round(k_total / n_words, 4)

    heat_mentions = extract_heat_mentions(text)
    if heat_mentions:
        mean_heat = round(sum(h for _, h in heat_mentions) / len(heat_mentions), 2)
        # Count transitions in heat level
        transitions = 0
        for i in range(1, len(heat_mentions)):
            if heat_mentions[i][1] != heat_mentions[i-1][1]:
                transitions += 1
        heat_transition_rate = round(transitions / len(heat_mentions), 3) if len(heat_mentions) > 1 else 0.0
    else:
        mean_heat = float(fire_degree)
        heat_transition_rate = 0.0

    k_channel = {
        "heat_rate": heat_rate,
        "mean_heat_intensity": mean_heat,
        "heat_transition_rate": heat_transition_rate,
        "raw_heat_mentions": k_total,
    }

    # -- h_channel (monitoring/observation) --
    h_total = count_pattern_matches(text, H_ALL)
    monitoring_rate = round(h_total / n_words, 4)

    h_color = count_pattern_matches(text, H_COLOR)
    h_consist = count_pattern_matches(text, H_CONSISTENCY)
    h_volat = count_pattern_matches(text, H_VOLATILITY)

    h_denom = max(h_total, 1)
    color_frac = round(h_color / h_denom, 3)
    consistency_frac = round(h_consist / h_denom, 3)
    volatility_frac = round(h_volat / h_denom, 3)

    # Chain rate: sequential monitoring (look for "when...then" or "first...then...then")
    chain_markers = len(re.findall(
        r'(?:first|then|afterward|thereafter|when.*(?:then|afterward))',
        text, re.IGNORECASE
    ))
    chain_rate = round(chain_markers / h_denom, 3)

    h_channel = {
        "monitoring_rate": monitoring_rate,
        "color_frac": color_frac,
        "consistency_frac": consistency_frac,
        "volatility_frac": volatility_frac,
        "chain_rate": chain_rate,
        "raw_monitoring_mentions": h_total,
    }

    # -- t_channel (termination/endpoint) --
    t_total = count_pattern_matches(text, T_ALL)
    termination_rate = round(t_total / n_words, 4)

    t_thresh = count_pattern_matches(text, T_THRESHOLD)
    t_time = count_pattern_matches(text, T_TIME)
    t_denom = max(t_thresh + t_time, 1)
    threshold_frac = round(t_thresh / t_denom, 3)

    t_channel = {
        "termination_rate": termination_rate,
        "threshold_frac": threshold_frac,
        "raw_termination_mentions": t_total,
    }

    # -- e_channel (correction/caution) --
    e_total = count_pattern_matches(text, E_ALL)
    correction_rate = round(e_total / n_words, 4)

    e_recov = count_pattern_matches(text, E_RECOVERABLE)
    e_fatal = count_pattern_matches(text, E_FATAL)
    e_denom = max(e_recov + e_fatal, 1)
    recoverable_frac = round(e_recov / e_denom, 3)

    e_drift = count_pattern_matches(text, E_DRIFT)
    process_drift_frac = round(e_drift / max(e_total, 1), 3)

    e_channel = {
        "correction_rate": correction_rate,
        "recoverable_frac": recoverable_frac,
        "process_drift_frac": process_drift_frac,
        "raw_correction_mentions": e_total,
    }

    return {
        "recipe_idx": idx,
        "name": recipe_def["name"],
        "lines": recipe_def["lines"],
        "n_words": n_words,
        "n_ingredients": n_ingredients,
        "n_steps": n_steps,
        "primary_technique": primary_technique,
        "fire_degree": fire_degree,
        "has_cohobation": has_cohobation,
        "has_digestion": has_digestion,
        "has_circulation": has_circulation,
        "k_channel": k_channel,
        "h_channel": h_channel,
        "t_channel": t_channel,
        "e_channel": e_channel,
    }


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(script_dir, "brunschwig_1512_english.txt")
    output_path = os.path.join(script_dir, "brunschwig_1512_compound_features.json")

    # Load full text as lines (1-indexed)
    with open(source_path, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    results = []
    for recipe_def in RECIPES:
        start = recipe_def["start"] - 1  # Convert to 0-indexed
        end = recipe_def["end"]          # Slice end is exclusive
        text = ''.join(all_lines[start:end])

        features = featurize_recipe(text, recipe_def)
        results.append(features)

    output = {
        "metadata": {
            "source": "brunschwig_1512_english.txt",
            "method": "4-channel featurization (k/h/t/e) + structural metadata",
            "n_recipes": len(results),
            "channels": {
                "k": "heat/thermal (fire intensity, transitions)",
                "h": "monitoring (color, consistency, volatility, sequential observation)",
                "t": "termination (threshold vs time-based endpoints)",
                "e": "correction (caution, recoverable vs fatal errors, process drift)",
            },
        },
        "recipes": results,
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"Featurized {len(results)} recipes -> {output_path}")
    print()
    print(f"{'#':<3} {'Name':<40} {'Words':>5} {'Ingr':>4} {'Steps':>5} "
          f"{'k_rate':>6} {'h_rate':>6} {'t_rate':>6} {'e_rate':>6} {'Technique':<14}")
    print("-" * 110)
    for r in results:
        print(f"{r['recipe_idx']:<3} {r['name']:<40} {r['n_words']:>5} "
              f"{r['n_ingredients']:>4} {r['n_steps']:>5} "
              f"{r['k_channel']['heat_rate']:>6.4f} "
              f"{r['h_channel']['monitoring_rate']:>6.4f} "
              f"{r['t_channel']['termination_rate']:>6.4f} "
              f"{r['e_channel']['correction_rate']:>6.4f} "
              f"{r['primary_technique']:<14}")

    # Print channel statistics
    print()
    print("=== Channel Statistics ===")
    for ch_name in ['k_channel', 'h_channel', 't_channel', 'e_channel']:
        rate_key = {
            'k_channel': 'heat_rate',
            'h_channel': 'monitoring_rate',
            't_channel': 'termination_rate',
            'e_channel': 'correction_rate',
        }[ch_name]
        rates = [r[ch_name][rate_key] for r in results]
        print(f"  {ch_name}: min={min(rates):.4f}  max={max(rates):.4f}  "
              f"mean={sum(rates)/len(rates):.4f}")

    # Print structural feature summary
    print()
    print("=== Structural Features ===")
    print(f"  Recipes with cohobation: {sum(1 for r in results if r['has_cohobation'])}/20")
    print(f"  Recipes with digestion:  {sum(1 for r in results if r['has_digestion'])}/20")
    print(f"  Recipes with circulation:{sum(1 for r in results if r['has_circulation'])}/20")
    tech_counts = {}
    for r in results:
        t = r['primary_technique']
        tech_counts[t] = tech_counts.get(t, 0) + 1
    for t, c in sorted(tech_counts.items(), key=lambda x: -x[1]):
        print(f"  Technique '{t}': {c} recipes")


if __name__ == "__main__":
    main()
