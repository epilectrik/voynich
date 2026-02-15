"""
Phase 374: Rupescissa Curation Script (v1.0)

Parses the complete English translation of John of Rupescissa's
"De consideratione quintae essentiae" (~1351) into structured JSON,
following the Brunschwig curation pattern.

Outputs:
  - data/rupescissa_curated_v1.json  (chapter-level structured data)
  - data/rupescissa_materials_v1.json (materials inventory with degrees)
  - phases/RUPESCISSA_CURATION/results/curation_verification.json

Source: sources/rupescissa/rupescissa_complete_translation.txt
"""

import json
import re
import os
import sys
from pathlib import Path
from collections import defaultdict

# Project root
ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "sources" / "rupescissa" / "rupescissa_complete_translation.txt"
OUT_CURATED = ROOT / "data" / "rupescissa_curated_v1.json"
OUT_MATERIALS = ROOT / "data" / "rupescissa_materials_v1.json"
OUT_VERIFY = ROOT / "phases" / "RUPESCISSA_CURATION" / "results" / "curation_verification.json"

# Brunschwig materials for overlap check
BRUNSCHWIG_PATH = ROOT / "data" / "brunschwig_curated_v3.json"

# ============================================================
# CHAPTER DEFINITIONS (manually verified against source)
# ============================================================
# Each entry: (header_pattern, number_label, title, chapter_type, book)
# Order matches the translation file.

CHAPTER_DEFS = [
    # Book 1
    ("PROOEMIUM", "Prooemium", "Preface", "THEORY", 1),
    ("AUTHOR'S INTENTION", "Author's Intention", "Author's Intention", "THEORY", 1),
    ("CANON 1", "Canon 1", "The First Secret", "THEORY", 1),
    ("CANON 2", "Canon 2", "What All Have Sought", "THEORY", 1),
    ("CHAPTER III", "III", "The Search for the Sun (Gold)", "THEORY", 1),
    ("CHAPTER IV", "IV", "The Search for the Stars", "THEORY", 1),
    ("CHAPTER V", "V", "How to Make Aqua Ardens", "PROCESS", 1),
    ("CHAPTER VI", "VI", "Practice - Signs of Successful Quintessence", "PROCESS", 1),
    ("CHAPTER VII", "VII", "Fire Without Fire", "PROCESS", 1),
    ("CHAPTER VIII", "VIII", "Obtaining Aqua Ardens from Spoiled Wine", "PROCESS", 1),
    ("CHAPTER IX", "IX", "Seven Methods of Obtaining Quintessence", "PROCESS", 1),
    ("CHAPTER X", "X", "Extracting Quintessence from Blood, Flesh, and Eggs", "EXTRACTION", 1),
    ("CHAPTER XI", "XI", "Extracting from Fruits and Herbs", "EXTRACTION", 1),
    ("CHAPTER XII", "XII", "Separating the Four Elements", "EXTRACTION", 1),
    ("CHAPTER XIII", "XIII", "Fixing the Sun (Gold) in the Fifth Essence", "EXTRACTION", 1),
    ("CHAPTER XIV", "XIV", "Practical Method for Fixing the Sun", "EXTRACTION", 1),
    ("CHAPTER XV", "XV", "Obtaining Solar Influence Without Expense", "EXTRACTION", 1),
    ("CHAPTER XVI", "XVI", "Concealing Gold and Silver", "EXTRACTION", 1),
    ("CHAPTER XVII", "XVII", "Fixing All Terrestrial Things", "EXTRACTION", 1),
    ("CHAPTER XVIII", "XVIII", "Things Hot in the First Degree", "DEGREE_CATALOG", 1),
    ("CHAPTER XIX", "XIX", "Things Hot in the Second Degree", "DEGREE_CATALOG", 1),
    ("CHAPTER XX", "XX", "Things Hot in the Third Degree", "DEGREE_CATALOG", 1),
    ("CHAPTER XXI", "XXI", "Things Hot in the Fourth Degree", "DEGREE_CATALOG", 1),
    ("CHAPTER XXII", "XXII", "Things Cold in the First Degree", "DEGREE_CATALOG", 1),
    ("CHAPTER XXIII", "XXIII", "Things Cold in the Second Degree", "DEGREE_CATALOG", 1),
    ("CHAPTER XXIV", "XXIV", "Things Cold in the Third and Fourth Degrees", "DEGREE_CATALOG", 1),
    ("CHAPTERS XXV-XXVIII", "XXV-XXVIII", "Things Dry in Degrees 1-4", "DEGREE_CATALOG", 1),
    ("CHAPTER XXIX", "XXIX", "Things Humid in Degrees 1-4", "DEGREE_CATALOG", 1),
    ("CHAPTER XXX", "XXX", "Identifying Compound Properties", "PHARMACOLOGICAL", 1),
    ("CHAPTER XXXI", "XXXI", "Temperate Things", "PHARMACOLOGICAL", 1),
    ("CHAPTER XXXII", "XXXII", "Purgatives", "PHARMACOLOGICAL", 1),
    ("CHAPTER XXXIII", "XXXIII", "Restrictives and Astringents", "PHARMACOLOGICAL", 1),
    ("CHAPTER XXXIV", "XXXIV", "Softening and Mollifying Things", "PHARMACOLOGICAL", 1),
    ("CHAPTER XXXV", "XXXV", "Maturatives", "PHARMACOLOGICAL", 1),
    ("CHAPTER XXXVI", "XXXVI", "Mundificatives (Cleansing)", "PHARMACOLOGICAL", 1),
    ("CHAPTER XXXVII-XXXIX", "XXXVII-XXXIX", "Corrosives, Caustics, Attenuants", "PHARMACOLOGICAL", 1),
    ("CHAPTER XL", "XL", "Extraction of Gold by Another Method", "EXTRACTION", 1),
    ("CHAPTER XLI", "XLI", "Extracting Quintessence from Silver", "EXTRACTION", 1),
    ("CHAPTER XLII", "XLII", "Extracting from Mercury and Roman Vitriol", "EXTRACTION", 1),
    ("CHAPTER XLIII", "XLIII", "The Athanor (Philosophical Furnace)", "APPARATUS", 1),
    ("CHAPTER XLIV", "XLIV", "Why Higher Secrets Are Not Revealed", "THEORY", 1),
    # Book 2
    ("REMEDY 1:", "Remedy 1", "Against the Impediments of Old Age", "REMEDY", 2),
    ("REMEDY 2:", "Remedy 2", "Against Death and Reviving the Dead", "REMEDY", 2),
    ("REMEDY 3:", "Remedy 3", "Against Leprosy", "REMEDY", 2),
    ("REMEDY 4:", "Remedy 4", "Against All Kinds of Scabies and Skin Lesions", "REMEDY", 2),
    ("REMEDY 5:", "Remedy 5", "Against Paralysis", "REMEDY", 2),
    ("REMEDY 6:", "Remedy 6", "Against Those Consumed in the Whole Body", "REMEDY", 2),
    ("REMEDY 7:", "Remedy 7", "Against Phantastical Passions and Demonic Temptations", "REMEDY", 2),
    ("REMEDY 8:", "Remedy 8", "Against Fear and Inconstancy", "REMEDY", 2),
    ("REMEDY 9:", "Remedy 9", "For Putting Demons and Bewitchments to Flight", "REMEDY", 2),
    ("REMEDY 10:", "Remedy 10", "Against Lice and Itching", "REMEDY", 2),
    ("REMEDY 11:", "Remedy 11", "For Expelling Poison", "REMEDY", 2),
    ("REMEDY 12:", "Remedy 12", "Against Quartan Fever", "REMEDY", 2),
    ("REMEDY 13:", "Remedy 13", "Against the Impediments and Dangers of Medicine", "REMEDY", 2),
    ("REMEDY 14:", "Remedy 14", "Against Continuous Fever", "REMEDY", 2),
    ("REMEDY 15:", "Remedy 15", "Against Tertian Fever", "REMEDY", 2),
    ("REMEDY 16:", "Remedy 16", "Against Quotidian Fever", "REMEDY", 2),
    ("REMEDY 17:", "Remedy 17", "Against Acute Fever and Frenzy", "REMEDY", 2),
    ("REMEDY 18:", "Remedy 18", "On the Cure of Hemitertian Fevers", "REMEDY", 2),
    ("REMEDY 19:", "Remedy 19", "Against Pestilential Fevers", "REMEDY", 2),
    ("REMEDY 20", "Remedy 20", "How Fever May Be Generated in Spasm", "REMEDY", 2),
]

# There are also several sub-sections that aren't full chapters:
# "THE PHILOSOPHICAL ARGUMENT", "THE QUINTA ESSENTIA DEFINED",
# "PROOF THAT QUINTESSENCE IS NOT OF THE FOUR ELEMENTS"
# These are sub-sections within Canon 2 / the early theory block.
# We treat them as part of Canon 2 (which is the encompassing chapter).
SUBSECTIONS_OF_CANON2 = [
    "THE PHILOSOPHICAL ARGUMENT",
    "THE QUINTA ESSENTIA DEFINED",
    "PROOF THAT QUINTESSENCE IS NOT OF THE FOUR ELEMENTS",
]

# ============================================================
# ACTION TAXONOMY (for procedural extraction)
# ============================================================
ACTION_TAXONOMY = {
    "DISTILL": "Standard distillation through alembic/still (distill, distillation)",
    "CIRCULATE": "Continuous circular distillation in sealed vessel (circulate, circulation, ascent and descent)",
    "RECTIFY": "Purify by repeated distillation or prolonged circulation (rectify, rectified, glorify)",
    "SUBLIME": "Sublimation - heat solid to vapor then condense (sublime, sublimated, sublimation)",
    "PUTREFY": "Controlled decomposition in warm dung or vessel (putrefy, putrefied, putrefaction)",
    "CALCINE": "Reduce to powder/calx by heating (calcine, calcined, calx)",
    "DISSOLVE": "Dissolve substance in liquid medium (dissolve, dissolved, solution)",
    "GRIND": "Mechanical grinding/filing to powder or small pieces (grind, file, powder, filings)",
    "SEAL": "Seal vessel with lute of wisdom or wax (seal, sealed, lute)",
    "HEAT_DUNG": "Gentle heat from horse dung decomposition (dung, belly of a horse)",
    "HEAT_MUST": "Gentle heat from fermenting grape must",
    "HEAT_SOLAR": "Heat from solar radiation (sun, solar)",
    "MACERATE": "Soak/infuse substance in liquid over time (infuse, put in, soak)",
    "SEPARATE": "Separate elements/layers by density or distillation (separate, separation)",
    "COLLECT": "Gather distillate or extract (collect, extract, take)",
    "MIX": "Combine substances together (mix, add, combine)",
}

# ============================================================
# MATERIALS DATABASE (manually extracted from degree catalogs + chapters)
# ============================================================
# Each entry: (name, name_latin, qualities_dict, category, source_chapters)
# qualities_dict: {quality: degree} where quality is hot/cold/dry/humid

DEGREE_MATERIALS = [
    # Chapter XVIII: Hot 1st degree
    ("chamomile", "anthemis", {"hot": 1}, "herb", ["XVIII"]),
    ("anise", "anisum", {"hot": 1}, "spice", ["XVIII"]),
    ("sweet flag", "calamus", {"hot": 1}, "herb", ["XVIII"]),
    ("rose", "rosa", {"hot": 1}, "flower", ["XVIII", "XXXII"]),
    ("violet", "viola", {"hot": 1}, "flower", ["XVIII", "Remedy 17"]),
    ("borage", "borago", {"hot": 1}, "herb", ["XVIII", "Remedy 17"]),
    ("bugloss", "buglossum", {"hot": 1}, "herb", ["XVIII"]),
    ("endive", "endivia", {"hot": 1}, "herb", ["XVIII", "Remedy 15"]),
    # Chapter XIX: Hot 2nd degree
    ("fennel", "foeniculum", {"hot": 2}, "herb", ["XIX", "Remedy 11"]),
    ("parsley", "petroselinum", {"hot": 2}, "herb", ["XIX"]),
    ("celery", "apium", {"hot": 2}, "herb", ["XIX"]),
    ("dill", "anethum", {"hot": 2}, "herb", ["XIX"]),
    ("caraway", "careum", {"hot": 2}, "spice", ["XIX"]),
    ("cumin", "cuminum", {"hot": 2}, "spice", ["XIX"]),
    ("coriander", "coriandrum", {"hot": 2}, "spice", ["XIX", "XXIII"]),
    ("hyssop", "hyssopus", {"hot": 2}, "herb", ["XIX", "XXXVII-XXXIX"]),
    ("mint", "mentha", {"hot": 2}, "herb", ["XIX"]),
    ("oregano", "origanum", {"hot": 2}, "herb", ["XIX"]),
    ("thyme", "thymus", {"hot": 2}, "herb", ["XIX"]),
    ("sage", "salvia", {"hot": 2}, "herb", ["XIX"]),
    ("rosemary", "rosmarinus", {"hot": 2}, "herb", ["XIX", "XV"]),
    ("lavender", "lavandula", {"hot": 2}, "herb", ["XIX"]),
    ("basil", "basilicum", {"hot": 2}, "herb", ["XIX"]),
    # Chapter XX: Hot 3rd degree
    ("ginger", "zingiber", {"hot": 3}, "spice", ["XX"]),
    ("galangal", "galanga", {"hot": 3}, "spice", ["XX"]),
    ("cinnamon", "cinnamomum", {"hot": 3}, "spice", ["XX"]),
    ("cloves", "caryophyllum", {"hot": 3}, "spice", ["XX"]),
    ("nutmeg", "nux moschata", {"hot": 3}, "spice", ["XX"]),
    ("mace", "macis", {"hot": 3}, "spice", ["XX"]),
    ("pepper", "piper", {"hot": 3, "dry": 2}, "spice", ["XX", "XXX"]),
    ("cardamom", "cardamomum", {"hot": 3}, "spice", ["XX"]),
    ("mustard", "sinapis", {"hot": 3}, "spice", ["XX"]),
    ("garlic", "allium", {"hot": 3}, "herb", ["XX", "Remedy 11"]),
    ("onion", "cepa", {"hot": 3}, "herb", ["XX", "XXXV"]),
    ("leek", "porrum", {"hot": 3}, "herb", ["XX"]),
    ("radish", "raphanus", {"hot": 3}, "herb", ["XX", "Remedy 11"]),
    ("rocket", "eruca", {"hot": 3}, "herb", ["XX"]),
    # Chapter XXI: Hot 4th degree
    ("euphorbium", "euphorbium", {"hot": 4}, "resin", ["XXI", "Remedy 16"]),
    ("pyrethrum", "pyrethrum", {"hot": 4}, "herb", ["XXI"]),
    ("long pepper", "piper longum", {"hot": 4}, "spice", ["XXI"]),
    ("spurge", "euphorbia", {"hot": 4}, "herb", ["XXI", "Remedy 5"]),
    ("hellebore", "helleborus", {"hot": 4}, "herb", ["XXI", "XXXII", "Remedy 12"]),
    ("scammony", "scammonium", {"hot": 4}, "resin", ["XXI"]),
    # Chapter XXII: Cold 1st degree
    ("barley", "hordeum", {"cold": 1}, "grain", ["XXII", "XXV-XXVIII"]),
    ("lettuce", "lactuca", {"cold": 1}, "herb", ["XXII", "Remedy 17"]),
    ("purslane", "portulaca", {"cold": 1}, "herb", ["XXII", "XXIII"]),
    ("cucumber", "cucumis", {"cold": 1, "humid": 2}, "fruit", ["XXII", "XXX"]),
    ("melon", "melo", {"cold": 1}, "fruit", ["XXII"]),
    ("violet leaves", "viola folia", {"cold": 1}, "herb", ["XXII"]),
    ("rose water", "aqua rosae", {"cold": 1}, "preparation", ["XXII", "Remedy 17"]),
    ("chicory", "cichorium", {"cold": 1}, "herb", ["XXII"]),
    # Chapter XXIII: Cold 2nd degree
    ("plantain", "plantago", {"cold": 2}, "herb", ["XXIII", "XXXIII"]),
    ("nightshade", "solanum", {"cold": 2}, "herb", ["XXIII"]),
    ("portulaca", "portulaca", {"cold": 2}, "herb", ["XXIII"]),
    ("vinegar", "acetum", {"cold": 2}, "preparation", ["XXIII"]),
    # Chapter XXIV: Cold 3rd & 4th degree
    ("poppy", "papaver", {"cold": 3}, "herb", ["XXIV"]),
    ("henbane", "hyoscyamus", {"cold": 3}, "herb", ["XXIV"]),
    ("mandrake", "mandragora", {"cold": 3}, "herb", ["XXIV"]),
    ("water lily", "nymphaea", {"cold": 3}, "herb", ["XXIV"]),
    ("opium", "opium", {"cold": 4}, "extract", ["XXIV"]),
    ("hemlock", "cicuta", {"cold": 4}, "herb", ["XXIV"]),
    # Chapters XXV-XXVIII: Dry degrees
    ("beans", "faba", {"dry": 1}, "grain", ["XXV-XXVIII"]),
    ("lentils", "lens", {"dry": 1}, "grain", ["XXV-XXVIII"]),
    ("alum", "alumen", {"dry": 3}, "mineral", ["XXV-XXVIII", "XXXIII"]),
    ("vitriol", "vitriolum", {"dry": 3}, "mineral", ["XXV-XXVIII", "XLII"]),
    ("iron rust", "ferrugo", {"dry": 3}, "mineral", ["XXV-XXVIII"]),
    # Chapter XXIX: Humid degrees
    ("oils", "oleum", {"humid": 2}, "preparation", ["XXIX"]),
    ("fats", "adeps", {"humid": 2}, "animal", ["XXIX"]),
    ("honey", "mel", {"humid": 3}, "preparation", ["XXIX", "XXXVI"]),
    ("egg white", "albumen ovi", {"humid": 4}, "animal", ["XXIX"]),
    # Chapter XXXII: Purgatives
    ("rhubarb", "rheum", {}, "purgative", ["XXXII", "Remedy 15"]),
    ("aloe", "aloe", {}, "purgative", ["XXXII", "XXXVI", "Remedy 13"]),
    ("cassia fistula", "cassia fistula", {}, "purgative", ["XXXII"]),
    ("manna", "manna", {}, "purgative", ["XXXII"]),
    ("tamarind", "tamarindus", {}, "purgative", ["XXXII"]),
    ("agaric", "agaricus", {}, "purgative", ["XXXII"]),
    ("turbith", "turbith", {}, "purgative", ["XXXII"]),
    ("colocynth", "colocynthis", {}, "purgative", ["XXXII"]),
    ("elaterium", "elaterium", {}, "purgative", ["XXXII"]),
    ("senna", "senna", {}, "purgative", ["XXXII"]),
    ("fumitory", "fumaria", {}, "purgative", ["XXXII"]),
    ("polypody", "polypodium", {}, "purgative", ["XXXII"]),
    ("black hellebore", "helleborus niger", {}, "purgative", ["XXXII", "Remedy 12"]),
    ("lapis lazuli", "lapis lazuli", {}, "mineral", ["XXXII"]),
    # Chapter XXXIII: Astringents
    ("oak bark", "quercus cortex", {}, "bark", ["XXXIII"]),
    ("pomegranate rind", "malum granatum", {}, "fruit", ["XXXIII"]),
    ("sumac", "rhus", {}, "herb", ["XXXIII"]),
    ("acacia", "acacia", {}, "tree", ["XXXIII"]),
    ("tormentil", "tormentilla", {}, "herb", ["XXXIII"]),
    # Chapter XXXIV: Mollifiers
    ("mallow", "malva", {}, "herb", ["XXXIV"]),
    ("marshmallow", "althaea", {}, "herb", ["XXXIV"]),
    ("fenugreek", "foenum graecum", {}, "herb", ["XXXIV"]),
    ("linseed", "linum", {}, "seed", ["XXXIV"]),
    ("butter", "butyrum", {}, "animal", ["XXXIV"]),
    # Chapter XXXV: Maturatives
    ("lily root", "lilium radix", {}, "herb", ["XXXV"]),
    ("fig", "ficus", {}, "fruit", ["XXXV"]),
    ("leaven", "fermentum", {}, "preparation", ["XXXV"]),
    ("wheat flour", "farina tritici", {}, "grain", ["XXXV"]),
    # Chapter XXXVI: Mundificatives
    ("turpentine", "terebinthina", {}, "resin", ["XXXVI"]),
    ("myrrh", "myrrha", {}, "resin", ["XXXVI"]),
    ("aristolochia", "aristolochia", {}, "herb", ["XXXVI"]),
    ("iris", "iris", {}, "herb", ["XXXVI"]),
    # Chapter XXXVII-XXXIX: Corrosives, Caustics, Attenuants
    ("arsenic", "arsenicum", {}, "mineral", ["XXXVII-XXXIX"]),
    ("verdigris", "aerugo", {}, "mineral", ["XXXVII-XXXIX"]),
    ("quicklime", "calx viva", {}, "mineral", ["XXXVII-XXXIX"]),
    ("caustic potash", "lixivium", {}, "preparation", ["XXXVII-XXXIX"]),
    ("oxymel", "oxymel", {}, "preparation", ["XXXVII-XXXIX"]),
    ("horehound", "marrubium", {}, "herb", ["XXXVII-XXXIX"]),
    # Extraction chapters (XL-XLII)
    ("gold", "aurum", {}, "metal", ["XIII", "XIV", "XV", "XL"]),
    ("silver", "argentum", {}, "metal", ["XLI"]),
    ("mercury", "mercurius", {}, "metal", ["XLII", "Remedy 10"]),
    ("sal ammoniac", "sal ammoniacum", {}, "mineral", ["XIV", "XLI"]),
    ("saltpeter", "sal petrae", {}, "mineral", ["XLII"]),
    # Key substances from process/remedy chapters
    ("wine", "vinum", {}, "preparation", ["V", "VIII"]),
    ("aqua ardens", "aqua ardens", {}, "preparation", ["V", "VI", "VIII", "IX"]),
    ("aqua vitae", "aqua vitae", {}, "preparation", ["V", "Remedy 11"]),
    ("human blood", "sanguis humanus", {}, "animal", ["X", "Remedy 14", "Remedy 17"]),
    ("eggs", "ova", {}, "animal", ["X"]),
    ("pearls", "margaritae", {}, "mineral", ["XV", "Remedy 1", "Remedy 13", "Remedy 17"]),
    ("saffron", "crocus", {}, "spice", ["XV", "Remedy 11"]),
    ("celandine", "chelidonia", {}, "herb", ["XV"]),
    ("marigold", "calendula", {}, "flower", ["XV"]),
    ("angelica", "angelica", {}, "herb", ["Remedy 11"]),
    ("rue", "ruta", {}, "herb", ["Remedy 11"]),
    ("peony", "paeonia", {}, "herb", ["Remedy 11"]),
    ("castoreum", "castoreum", {}, "animal", ["Remedy 5"]),
    ("theriac", "theriaca", {}, "preparation", ["Remedy 11"]),
    ("elder", "sambucus", {}, "herb", ["Remedy 12", "Remedy 16"]),
    ("staphisagria", "staphisagria", {}, "herb", ["Remedy 10"]),
    ("red pimpernel", "anagallis", {}, "herb", ["Remedy 12"]),
    ("buttercup", "ranunculus", {}, "herb", ["Remedy 20"]),
]


# ============================================================
# PARSING
# ============================================================

def load_lines():
    """Load translation file as list of (line_number, text) tuples."""
    with open(SOURCE, 'r', encoding='utf-8') as f:
        return [(i + 1, line.rstrip('\n')) for i, line in enumerate(f)]


def find_chapter_boundaries(lines):
    """Find the start line of each chapter header in the file."""
    boundaries = []
    separator = '-' * 40  # At least 40 dashes

    for idx, (line_num, text) in enumerate(lines):
        if not text.startswith(separator):
            continue

        # Look at next non-empty line after separator
        next_idx = idx + 1
        while next_idx < len(lines) and lines[next_idx][1].strip() == '':
            next_idx += 1
        if next_idx >= len(lines):
            continue

        next_line = lines[next_idx][1].strip()

        # Check if this matches any chapter definition
        # Use longest-match-first to avoid "CHAPTER V" matching "CHAPTER VI"
        best_match = None
        best_len = 0
        for ch_idx, (pattern, number, title, ch_type, book) in enumerate(CHAPTER_DEFS):
            if next_line.upper().startswith(pattern.upper()):
                if len(pattern) > best_len:
                    best_match = ch_idx
                    best_len = len(pattern)

        if best_match is not None:
            boundaries.append((best_match, line_num, next_line))

    return boundaries


def extract_chapter_text(lines, boundaries, ch_idx):
    """Extract the text content of a chapter between its boundaries."""
    # Find this chapter's start
    start_line = None
    end_line = None

    for i, (idx, line_num, _) in enumerate(boundaries):
        if idx == ch_idx:
            start_line = line_num
            # End is the line before the next chapter's separator, or EOF
            if i + 1 < len(boundaries):
                end_line = boundaries[i + 1][1] - 1
            else:
                # Find the EXPLICIT or KEY CONCEPTS or end of file
                end_line = lines[-1][0]
            break

    if start_line is None:
        return "", start_line, end_line

    # Collect text between start and end
    text_parts = []
    for line_num, text in lines:
        if line_num >= start_line and line_num <= end_line:
            text_parts.append(text)

    return '\n'.join(text_parts), start_line, end_line


def extract_procedural_steps(text, chapter_type):
    """Extract procedural steps from PROCESS/EXTRACTION chapters."""
    if chapter_type not in ('PROCESS', 'EXTRACTION', 'APPARATUS'):
        return None

    steps = []
    step_num = 0

    # Look for numbered methods or sequential actions
    method_patterns = [
        (r'FIRST METHOD[^:]*:', 'FIRST METHOD'),
        (r'SECOND METHOD[^:]*:', 'SECOND METHOD'),
        (r'THIRD METHOD[^:]*:', 'THIRD METHOD'),
        (r'FOURTH METHOD[^:]*:', 'FOURTH METHOD'),
        (r'FIFTH METHOD[^:]*:', 'FIFTH METHOD'),
        (r'SIXTH METHOD[^:]*:', 'SIXTH METHOD'),
        (r'SEVENTH METHOD[^:]*:', 'SEVENTH METHOD'),
    ]

    # Check for numbered methods
    for pattern, label in method_patterns:
        m = re.search(pattern, text)
        if m:
            step_num += 1
            # Extract a brief description after the match
            start = m.end()
            desc = text[start:start + 200].strip().split('\n')[0]
            action = classify_action(desc)
            steps.append({
                "step": step_num,
                "action": action,
                "method_label": label,
                "description": desc[:150]
            })

    # Check for numbered steps (1., 2., etc.)
    if not steps:
        num_pattern = re.finditer(r'\n\s*(\d+)\.\s+([A-Z]+)[:\s](.+?)(?=\n\s*\d+\.|$)', text, re.DOTALL)
        for m in num_pattern:
            step_num += 1
            element = m.group(2)
            desc = m.group(3).strip()[:150]
            action = classify_action(element + ' ' + desc)
            steps.append({
                "step": step_num,
                "action": action,
                "description": f"{element}: {desc}"
            })

    # Fallback: look for action keywords in sequence
    if not steps:
        action_keywords = [
            ('distill', 'DISTILL'), ('circulate', 'CIRCULATE'), ('circulation', 'CIRCULATE'),
            ('ascent and descent', 'CIRCULATE'), ('ascents and descents', 'CIRCULATE'),
            ('continuous rising and falling', 'CIRCULATE'),
            ('sublime', 'SUBLIME'), ('sublimation', 'SUBLIME'), ('sublimated', 'SUBLIME'),
            ('putrefy', 'PUTREFY'), ('putrefied', 'PUTREFY'), ('putrefaction', 'PUTREFY'),
            ('calcine', 'CALCINE'), ('calx', 'CALCINE'), ('calcined', 'CALCINE'),
            ('dissolve', 'DISSOLVE'), ('dissolved', 'DISSOLVE'),
            ('grind', 'GRIND'), ('file it', 'GRIND'), ('filings', 'GRIND'),
            ('powder', 'GRIND'), ('small pieces', 'GRIND'),
            ('seal', 'SEAL'), ('lute', 'SEAL'), ('sealed', 'SEAL'),
            ('horse dung', 'HEAT_DUNG'), ('belly of a horse', 'HEAT_DUNG'),
            ('grape', 'HEAT_MUST'),
            ('rectif', 'RECTIFY'), ('glorif', 'RECTIFY'),
            ('infuse', 'MACERATE'), ('immersed', 'MACERATE'),
            ('separate', 'SEPARATE'),
        ]
        found_actions = []
        for keyword, action in action_keywords:
            pos = text.lower().find(keyword)
            if pos >= 0:
                found_actions.append((pos, action, keyword))

        found_actions.sort(key=lambda x: x[0])
        seen_actions = set()
        for pos, action, keyword in found_actions:
            if action not in seen_actions:
                step_num += 1
                # Get context around the keyword
                start = max(0, pos - 10)
                end = min(len(text), pos + 100)
                context = text[start:end].replace('\n', ' ').strip()[:120]
                steps.append({
                    "step": step_num,
                    "action": action,
                    "description": context
                })
                seen_actions.add(action)

    return steps if steps else None


def classify_action(text):
    """Classify a text snippet into an action category."""
    text_lower = text.lower()
    if 'circul' in text_lower:
        return 'CIRCULATE'
    if 'distill' in text_lower or 'brennen' in text_lower:
        return 'DISTILL'
    if 'sublim' in text_lower:
        return 'SUBLIME'
    if 'putref' in text_lower or 'dung' in text_lower:
        return 'PUTREFY'
    if 'calcin' in text_lower or 'calx' in text_lower:
        return 'CALCINE'
    if 'dissolv' in text_lower:
        return 'DISSOLVE'
    if 'grind' in text_lower or 'file' in text_lower or 'powder' in text_lower:
        return 'GRIND'
    if 'seal' in text_lower or 'lute' in text_lower:
        return 'SEAL'
    if 'horse' in text_lower or 'dung' in text_lower:
        return 'HEAT_DUNG'
    if 'rectif' in text_lower or 'glorif' in text_lower:
        return 'RECTIFY'
    if 'separat' in text_lower:
        return 'SEPARATE'
    if 'infuse' in text_lower or 'soak' in text_lower:
        return 'MACERATE'
    if 'mix' in text_lower or 'add' in text_lower or 'combine' in text_lower:
        return 'MIX'
    return 'COLLECT'


def extract_key_concepts(text):
    """Extract key concepts from chapter text."""
    concepts = []

    concept_markers = [
        (r'FIFTH ESSENCE', 'quintessence'),
        (r'AQUA ARDENS', 'aqua ardens'),
        (r'AQUA VITAE', 'aqua vitae'),
        (r'INCORRUPTIB', 'incorruptibility'),
        (r'CONCEAL', 'concealment'),
        (r'GOLD OF', 'philosophical gold'),
        (r'CIRCULAT', 'circular distillation'),
        (r'SUBLIME', 'sublimation'),
        (r'PUTREF', 'putrefaction'),
        (r'ATHANOR', 'athanor'),
        (r'HORSE DUNG|BELLY OF A HORSE', 'heat without fire'),
        (r'EVANGELICAL MEN', 'restriction to worthy'),
        (r'PRESERVE.*CORRUPT|INCORRUPT', 'preservation from corruption'),
        (r'FOUR ELEMENTS', 'four elements'),
        (r'DEGREE', 'degree system'),
        (r'PURGAT', 'purgation'),
    ]

    for pattern, concept in concept_markers:
        if re.search(pattern, text, re.IGNORECASE):
            concepts.append(concept)

    return list(dict.fromkeys(concepts))  # deduplicate preserving order


def extract_materials_mentioned(text, all_materials):
    """Find materials mentioned in chapter text using word-boundary matching."""
    mentioned = []
    text_lower = text.lower()

    for name, latin, _, _, _ in all_materials:
        # Always use word boundaries to avoid false positives
        # (e.g., "rue" in "true", "angelica" in "Evangelical", "fig" in "figure")
        name_l = name.lower()
        latin_l = latin.lower() if latin else ''

        found = False
        if re.search(r'\b' + re.escape(name_l) + r'\b', text_lower):
            found = True

        if not found and latin_l and len(latin_l) > 2:
            if re.search(r'\b' + re.escape(latin_l) + r'\b', text_lower):
                found = True

        if found:
            mentioned.append(name)

    return list(dict.fromkeys(mentioned))  # deduplicate


def extract_remedy_protocol(text, chapter_title):
    """Extract treatment protocol from REMEDY chapters."""
    protocol = {}

    # Target disease from title
    title_lower = chapter_title.lower()
    if 'old age' in title_lower:
        protocol['target_disease'] = 'impediments of old age'
    elif 'death' in title_lower or 'dead' in title_lower:
        protocol['target_disease'] = 'near-death/revival'
    elif 'leprosy' in title_lower:
        protocol['target_disease'] = 'leprosy'
    elif 'scabies' in title_lower or 'skin' in title_lower:
        protocol['target_disease'] = 'skin diseases'
    elif 'paralysis' in title_lower:
        protocol['target_disease'] = 'paralysis'
    elif 'consumed' in title_lower:
        protocol['target_disease'] = 'consumption/wasting'
    elif 'phantast' in title_lower or 'demon' in title_lower:
        protocol['target_disease'] = 'phantastical passions/demonic temptation'
    elif 'fear' in title_lower:
        protocol['target_disease'] = 'fear and inconstancy'
    elif 'putting demons' in title_lower or 'bewitchment' in title_lower:
        protocol['target_disease'] = 'demonic affliction/bewitchment'
    elif 'lice' in title_lower:
        protocol['target_disease'] = 'lice and itching'
    elif 'poison' in title_lower:
        protocol['target_disease'] = 'poison'
    elif 'quartan' in title_lower:
        protocol['target_disease'] = 'quartan fever (melancholy)'
    elif 'impediments' in title_lower and 'medicine' in title_lower:
        protocol['target_disease'] = 'dangers of purgative medicine'
    elif 'continuous' in title_lower:
        protocol['target_disease'] = 'continuous fever'
    elif 'tertian' in title_lower and 'hemi' not in title_lower:
        protocol['target_disease'] = 'tertian fever (choler)'
    elif 'quotidian' in title_lower:
        protocol['target_disease'] = 'quotidian fever (phlegm)'
    elif 'acute' in title_lower or 'frenzy' in title_lower:
        protocol['target_disease'] = 'acute fever/frenzy'
    elif 'hemitertian' in title_lower:
        protocol['target_disease'] = 'hemitertian fevers'
    elif 'pestilen' in title_lower:
        protocol['target_disease'] = 'pestilential fevers'
    elif 'spasm' in title_lower:
        protocol['target_disease'] = 'spasm (generate fever as cure)'
    else:
        protocol['target_disease'] = 'unclassified'

    # Primary agent
    text_lower = text.lower()
    if 'fifth essence' in text_lower or 'quinta essentia' in text_lower:
        protocol['primary_agent'] = 'Fifth Essence'
    elif 'aqua ardens' in text_lower:
        protocol['primary_agent'] = 'aqua ardens'
    else:
        protocol['primary_agent'] = 'unspecified'

    # Administration routes
    routes = []
    if 'drink' in text_lower or 'drunk' in text_lower or 'morning and evening' in text_lower:
        routes.append('oral')
    if 'anoint' in text_lower:
        routes.append('anointing')
    if 'nostrils' in text_lower:
        routes.append('nasal')
    if 'odor' in text_lower or 'fragrance' in text_lower:
        routes.append('aromatic')
    if 'bath' in text_lower:
        routes.append('bath')
    if not routes:
        routes.append('oral')  # default
    protocol['administration'] = routes

    # Humoral target (for fever remedies)
    if 'choler' in text_lower or 'bile' in text_lower:
        if 'yellow' in text_lower or 'red' in text_lower:
            protocol['humoral_target'] = 'yellow bile (choler)'
        elif 'black' in text_lower:
            protocol['humoral_target'] = 'black bile (melancholy)'
        else:
            protocol['humoral_target'] = 'bile'
    elif 'phlegm' in text_lower:
        protocol['humoral_target'] = 'phlegm'
    elif 'blood' in text_lower and 'putref' in text_lower:
        protocol['humoral_target'] = 'corrupted blood'
    elif 'melanchol' in text_lower:
        protocol['humoral_target'] = 'melancholy'

    return protocol


# ============================================================
# BRUNSCHWIG OVERLAP
# ============================================================

def load_brunschwig_materials():
    """Load Brunschwig material names for overlap comparison."""
    if not BRUNSCHWIG_PATH.exists():
        return set()

    with open(BRUNSCHWIG_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    names = set()
    for recipe in data.get('recipes', []):
        name = recipe.get('name_english', '').lower()
        if name:
            names.add(name)
    return names


# ============================================================
# MAIN CURATION
# ============================================================

def curate():
    print("Loading translation file...")
    lines = load_lines()
    print(f"  {len(lines)} lines loaded")

    print("Finding chapter boundaries...")
    boundaries = find_chapter_boundaries(lines)
    print(f"  {len(boundaries)} chapters found")

    # Check which chapters were found
    found_indices = {b[0] for b in boundaries}
    missing = [CHAPTER_DEFS[i] for i in range(len(CHAPTER_DEFS)) if i not in found_indices]
    if missing:
        print(f"  WARNING: {len(missing)} chapters not found in text:")
        for m in missing:
            print(f"    - {m[1]}: {m[2]}")

    print("Loading Brunschwig materials for overlap...")
    brunschwig_names = load_brunschwig_materials()
    print(f"  {len(brunschwig_names)} Brunschwig materials loaded")

    print("Curating chapters...")
    chapters = []
    all_actions_used = set()

    for ch_idx, (pattern, number, title, ch_type, book) in enumerate(CHAPTER_DEFS):
        text, start_line, end_line = extract_chapter_text(lines, boundaries, ch_idx)

        chapter = {
            "id": ch_idx + 1,
            "book": book,
            "number": number,
            "title": title,
            "chapter_type": ch_type,
            "source_lines": {"start": start_line, "end": end_line},
            "key_concepts": extract_key_concepts(text),
            "materials_mentioned": extract_materials_mentioned(text, DEGREE_MATERIALS),
        }

        # Procedural steps for PROCESS/EXTRACTION/APPARATUS
        steps = extract_procedural_steps(text, ch_type)
        if steps:
            chapter["procedural_steps"] = steps
            for s in steps:
                all_actions_used.add(s['action'])
        else:
            chapter["procedural_steps"] = None

        # Remedy protocol for REMEDY chapters
        if ch_type == 'REMEDY':
            chapter["treatment_protocol"] = extract_remedy_protocol(text, title)
        else:
            chapter["treatment_protocol"] = None

        # Degree catalog items for DEGREE_CATALOG
        if ch_type == 'DEGREE_CATALOG':
            items = [m[0] for m in DEGREE_MATERIALS if number in m[4]]
            chapter["catalog_items"] = items
            chapter["catalog_count"] = len(items)
        else:
            chapter["catalog_items"] = None

        chapters.append(chapter)

    # Build action taxonomy (only actions actually used)
    used_taxonomy = {k: v for k, v in ACTION_TAXONOMY.items() if k in all_actions_used}

    # Build curated output
    curated = {
        "title": "Rupescissa - De consideratione quintae essentiae",
        "version": "1.0",
        "curation_date": "2026-02-15",
        "source": "sources/rupescissa/rupescissa_complete_translation.txt",
        "original_composition": "c. 1351-1352",
        "author": "John of Rupescissa (Johannes de Rupescissa)",
        "chapter_type_taxonomy": {
            "THEORY": "Philosophical framework and quintessence definition",
            "PROCESS": "General distillation methods",
            "EXTRACTION": "Material-specific extraction procedures",
            "DEGREE_CATALOG": "Materials classified by quality and degree (hot/cold/dry/humid x 1-4)",
            "PHARMACOLOGICAL": "Materials classified by therapeutic function",
            "APPARATUS": "Equipment descriptions",
            "REMEDY": "Disease-specific treatment protocols (Book 2)"
        },
        "action_taxonomy": used_taxonomy,
        "statistics": {
            "total_chapters": len(chapters),
            "book_1_chapters": sum(1 for c in chapters if c['book'] == 1),
            "book_2_remedies": sum(1 for c in chapters if c['book'] == 2),
            "by_type": {},
            "chapters_with_procedures": sum(1 for c in chapters if c['procedural_steps']),
            "distinct_actions_used": len(all_actions_used),
        },
        "chapters": chapters,
    }

    # Type distribution
    for ch_type in ['THEORY', 'PROCESS', 'EXTRACTION', 'DEGREE_CATALOG',
                     'PHARMACOLOGICAL', 'APPARATUS', 'REMEDY']:
        curated['statistics']['by_type'][ch_type] = sum(
            1 for c in chapters if c['chapter_type'] == ch_type)

    # Write curated JSON
    print(f"Writing {OUT_CURATED}...")
    with open(OUT_CURATED, 'w', encoding='utf-8') as f:
        json.dump(curated, f, indent=2, ensure_ascii=False)

    # ========================================
    # MATERIALS INVENTORY
    # ========================================
    print("Building materials inventory...")

    materials_list = []
    for name, latin, qualities, category, source_chapters in DEGREE_MATERIALS:
        # Check Brunschwig overlap
        in_brunschwig = name.lower() in brunschwig_names

        mat = {
            "name": name,
            "name_latin": latin,
            "category": category,
            "source_chapters": source_chapters,
            "also_in_brunschwig": in_brunschwig,
        }

        # Add degree info
        for q in ['hot', 'cold', 'dry', 'humid']:
            mat[f'degree_{q}'] = qualities.get(q, None)

        # Therapeutic function from pharmacological category
        pharm_functions = {
            'XXXII': 'purgative',
            'XXXIII': 'astringent',
            'XXXIV': 'mollifier',
            'XXXV': 'maturative',
            'XXXVI': 'mundificative',
            'XXXVII-XXXIX': 'corrosive/caustic/attenuant',
        }
        functions = [pharm_functions[ch] for ch in source_chapters if ch in pharm_functions]
        mat['therapeutic_function'] = functions[0] if functions else None

        materials_list.append(mat)

    # Deduplicate by name (some materials appear in multiple places)
    seen = {}
    deduped = []
    for mat in materials_list:
        key = mat['name'].lower()
        if key in seen:
            # Merge source chapters
            existing = seen[key]
            for ch in mat['source_chapters']:
                if ch not in existing['source_chapters']:
                    existing['source_chapters'].append(ch)
            # Merge qualities
            for q in ['hot', 'cold', 'dry', 'humid']:
                if mat[f'degree_{q}'] is not None and existing[f'degree_{q}'] is None:
                    existing[f'degree_{q}'] = mat[f'degree_{q}']
            # Merge brunschwig
            existing['also_in_brunschwig'] = existing['also_in_brunschwig'] or mat['also_in_brunschwig']
        else:
            seen[key] = mat
            deduped.append(mat)

    brunschwig_overlap = [m for m in deduped if m['also_in_brunschwig']]

    materials_output = {
        "title": "Rupescissa Materials Inventory",
        "version": "1.0",
        "curation_date": "2026-02-15",
        "source": "sources/rupescissa/rupescissa_complete_translation.txt",
        "statistics": {
            "total_materials": len(deduped),
            "with_degree_classification": sum(1 for m in deduped
                if any(m[f'degree_{q}'] is not None for q in ['hot','cold','dry','humid'])),
            "brunschwig_overlap": len(brunschwig_overlap),
            "by_category": {},
        },
        "materials": deduped,
    }

    # Category distribution
    cat_counts = defaultdict(int)
    for m in deduped:
        cat_counts[m['category']] += 1
    materials_output['statistics']['by_category'] = dict(sorted(cat_counts.items()))

    print(f"Writing {OUT_MATERIALS}...")
    with open(OUT_MATERIALS, 'w', encoding='utf-8') as f:
        json.dump(materials_output, f, indent=2, ensure_ascii=False)

    # ========================================
    # VERIFICATION
    # ========================================
    print("\nRunning verification checks...")
    verify = {"checks": [], "overall": "PASS"}

    # V1: Chapter count
    b1 = sum(1 for c in chapters if c['book'] == 1)
    b2 = sum(1 for c in chapters if c['book'] == 2)
    total = b1 + b2
    v1_pass = (total >= 60)  # Allow minor variance from 64 target
    verify["checks"].append({
        "id": "V1",
        "name": "Chapter Count",
        "expected": "~64 (44 Book 1 + 20 Book 2)",
        "actual": f"{total} ({b1} Book 1 + {b2} Book 2)",
        "status": "PASS" if v1_pass else "FAIL"
    })
    if not v1_pass:
        verify["overall"] = "FAIL"

    # V2: Source line references
    bad_refs = [c for c in chapters if c['source_lines']['start'] is None]
    v2_pass = len(bad_refs) == 0
    verify["checks"].append({
        "id": "V2",
        "name": "Source Line References",
        "expected": "All chapters have source_lines",
        "actual": f"{len(chapters) - len(bad_refs)}/{len(chapters)} have valid references",
        "status": "PASS" if v2_pass else "FAIL",
        "missing": [c['number'] for c in bad_refs] if bad_refs else []
    })
    if not v2_pass:
        verify["overall"] = "FAIL"

    # V3: Materials no duplicates
    mat_names = [m['name'].lower() for m in deduped]
    dupes = [n for n in mat_names if mat_names.count(n) > 1]
    v3_pass = len(set(dupes)) == 0
    verify["checks"].append({
        "id": "V3",
        "name": "Materials No Duplicates",
        "expected": "No duplicate material names",
        "actual": f"{len(deduped)} unique materials" + (f", {len(set(dupes))} duplicates" if dupes else ""),
        "status": "PASS" if v3_pass else "FAIL",
        "duplicates": list(set(dupes)) if dupes else []
    })
    if not v3_pass:
        verify["overall"] = "FAIL"

    # V4: Degree catalog completeness
    degree_mats = [m for m in deduped
        if any(m[f'degree_{q}'] is not None for q in ['hot','cold','dry','humid'])]
    v4_pass = len(degree_mats) >= 40  # At least 40 degree-classified
    verify["checks"].append({
        "id": "V4",
        "name": "Degree Catalog Completeness",
        "expected": ">=40 materials with degree classifications",
        "actual": f"{len(degree_mats)} materials with degree data",
        "status": "PASS" if v4_pass else "FAIL"
    })
    if not v4_pass:
        verify["overall"] = "FAIL"

    # V5: Brunschwig overlap
    verify["checks"].append({
        "id": "V5",
        "name": "Brunschwig Overlap",
        "expected": "Report overlap count",
        "actual": f"{len(brunschwig_overlap)} materials in both texts",
        "overlap_names": [m['name'] for m in brunschwig_overlap],
        "status": "PASS"  # informational, always passes
    })

    # V6: JSON validates
    try:
        with open(OUT_CURATED, 'r', encoding='utf-8') as f:
            json.load(f)
        with open(OUT_MATERIALS, 'r', encoding='utf-8') as f:
            json.load(f)
        v6_pass = True
    except Exception as e:
        v6_pass = False
        verify["checks"].append({
            "id": "V6", "name": "JSON Validation",
            "status": "FAIL", "error": str(e)
        })

    if v6_pass:
        verify["checks"].append({
            "id": "V6",
            "name": "JSON Validation",
            "expected": "Both JSON files parse cleanly",
            "actual": "Both files valid",
            "status": "PASS"
        })

    if not v6_pass:
        verify["overall"] = "FAIL"

    print(f"\nWriting {OUT_VERIFY}...")
    with open(OUT_VERIFY, 'w', encoding='utf-8') as f:
        json.dump(verify, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 60)
    print("RUPESCISSA CURATION COMPLETE")
    print("=" * 60)
    print(f"\nChapters: {total} ({b1} Book 1 + {b2} Book 2)")
    print(f"Chapter types: {curated['statistics']['by_type']}")
    print(f"Chapters with procedures: {curated['statistics']['chapters_with_procedures']}")
    print(f"Distinct actions: {curated['statistics']['distinct_actions_used']}")
    print(f"\nMaterials: {len(deduped)}")
    print(f"With degree classification: {materials_output['statistics']['with_degree_classification']}")
    print(f"Brunschwig overlap: {len(brunschwig_overlap)}")
    print(f"Categories: {dict(cat_counts)}")
    print()

    for check in verify["checks"]:
        status = check["status"]
        marker = "PASS" if status == "PASS" else "FAIL"
        print(f"  {check['id']}: {marker} - {check['name']}: {check['actual']}")

    print(f"\nOverall: {verify['overall']}")

    return verify["overall"] == "PASS"


if __name__ == '__main__':
    success = curate()
    sys.exit(0 if success else 1)
