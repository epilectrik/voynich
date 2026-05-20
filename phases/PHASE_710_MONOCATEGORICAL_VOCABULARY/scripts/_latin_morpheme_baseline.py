"""Add Latin morpheme inventory baseline.

The original PHASE_710 main test compared Voynich atoms to Latin top-50 WORD-FORMS.
That's an asymmetric comparison — Voynich atoms are sub-token morpheme-like primitives.
The right NL comparator is Latin MORPHEMES (productive derivational + inflectional suffixes).

Latin morpheme inventory curated from standard sources (Allen's Sketch of Comparative
Latin Grammar / Gildersleeve & Lodge). Productive morphemes only, not lexical roots
(roots are vast and trivially heterogeneous; morphemes are the architectural inventory
that compares to Voynich's atom layer).
"""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
PHASE_DIR = ROOT / 'phases' / 'PHASE_710_MONOCATEGORICAL_VOCABULARY'
OUT_PATH = PHASE_DIR / 'reference_data' / 'latin_morpheme_inventory.json'

LATIN_MORPHEMES = {
    # ENTITY-forming derivational suffixes (nominalizers)
    "-atio":  {"category": "ENTITY",   "subcat": "action_noun_suffix",      "_note": "creates abstract action-noun: amare → amatio"},
    "-tio":   {"category": "ENTITY",   "subcat": "action_noun_suffix",      "_note": "variant of -atio"},
    "-tor":   {"category": "ENTITY",   "subcat": "agent_noun_suffix",       "_note": "creates agent noun: amare → amator"},
    "-trix":  {"category": "ENTITY",   "subcat": "agent_noun_suffix_fem"},
    "-ium":   {"category": "ENTITY",   "subcat": "place_result_noun",       "_note": "praedium, ingenium"},
    "-arium": {"category": "ENTITY",   "subcat": "container_noun",          "_note": "armarium, granarium"},
    "-tas":   {"category": "ENTITY",   "subcat": "abstract_noun_suffix",    "_note": "veritas, libertas"},
    "-tudo":  {"category": "ENTITY",   "subcat": "state_noun_suffix",       "_note": "magnitudo"},
    "-mentum":{"category": "ENTITY",   "subcat": "instrumental_noun",       "_note": "ornamentum"},
    "-ulus":  {"category": "ENTITY",   "subcat": "diminutive_noun"},
    "-cul":   {"category": "ENTITY",   "subcat": "diminutive_noun"},

    # PROPERTY-forming derivational suffixes (adjectivizers)
    "-ilis":  {"category": "PROPERTY", "subcat": "adjective_capability"},
    "-alis":  {"category": "PROPERTY", "subcat": "adjective_relational"},
    "-aris":  {"category": "PROPERTY", "subcat": "adjective_relational"},
    "-arius": {"category": "PROPERTY", "subcat": "adjective_relational"},
    "-osus":  {"category": "PROPERTY", "subcat": "adjective_abundance"},
    "-bilis": {"category": "PROPERTY", "subcat": "adjective_possibility"},
    "-anus":  {"category": "PROPERTY", "subcat": "adjective_relational"},
    "-inus":  {"category": "PROPERTY", "subcat": "adjective_relational"},

    # OPERATION-forming derivational suffixes (verbalizers / verbal infinitives)
    "-are":   {"category": "OPERATION","subcat": "infinitive_1st_conj"},
    "-ere":   {"category": "OPERATION","subcat": "infinitive_2nd_3rd_conj"},
    "-ire":   {"category": "OPERATION","subcat": "infinitive_4th_conj"},
    "-izare": {"category": "OPERATION","subcat": "verb_greek_loan",        "_note": "baptizare, alchimizare"},
    "-ficare":{"category": "OPERATION","subcat": "verb_causative",         "_note": "calefacere"},
    "-escere":{"category": "OPERATION","subcat": "verb_inchoative",        "_note": "calescere"},
    "-itare": {"category": "OPERATION","subcat": "verb_frequentative",     "_note": "agitare"},

    # FUNCTION (inflectional case endings — case markers carry NO lexical content)
    "-us":    {"category": "FUNCTION", "subcat": "case_nom_sg_masc"},
    "-i":     {"category": "FUNCTION", "subcat": "case_gen_sg / nom_pl"},
    "-o":     {"category": "FUNCTION", "subcat": "case_dat_abl_sg"},
    "-um":    {"category": "FUNCTION", "subcat": "case_acc_sg_neut"},
    "-orum": {"category": "FUNCTION", "subcat": "case_gen_pl"},
    "-is":    {"category": "FUNCTION", "subcat": "case_dat_abl_pl / gen_sg"},
    "-a":     {"category": "FUNCTION", "subcat": "case_nom_sg_fem"},
    "-ae":    {"category": "FUNCTION", "subcat": "case_gen_dat_sg_fem"},
    "-am":    {"category": "FUNCTION", "subcat": "case_acc_sg_fem"},
    "-as":    {"category": "FUNCTION", "subcat": "case_acc_pl_fem"},
    "-em":    {"category": "FUNCTION", "subcat": "case_acc_sg_3rd"},
    "-e":     {"category": "FUNCTION", "subcat": "case_voc_sg / abl_sg"},

    # FUNCTION (inflectional verb endings — tense/aspect/person markers)
    "-t":     {"category": "FUNCTION", "subcat": "verb_3sg_present"},
    "-nt":    {"category": "FUNCTION", "subcat": "verb_3pl_present"},
    "-bat":   {"category": "FUNCTION", "subcat": "verb_3sg_imperfect"},
    "-bit":   {"category": "FUNCTION", "subcat": "verb_3sg_future"},
    "-erunt": {"category": "FUNCTION", "subcat": "verb_3pl_perfect"},
    "-tur":   {"category": "FUNCTION", "subcat": "verb_passive_3sg"},
    "-mus":   {"category": "FUNCTION", "subcat": "verb_1pl"},
    "-tis":   {"category": "FUNCTION", "subcat": "verb_2pl"},
}


def main():
    print("=" * 90)
    print("LATIN MORPHEME INVENTORY BASELINE")
    print("=" * 90)

    cat_counter = Counter(m["category"] for m in LATIN_MORPHEMES.values())
    n = len(LATIN_MORPHEMES)

    print(f"\n  N morphemes: {n}")
    print(f"  Source: Allen comparative grammar / Gildersleeve & Lodge — productive morpheme inventory")
    print(f"\n  Category distribution:")
    for cat, c in cat_counter.most_common():
        print(f"    {cat:<12} {c:>3}   ({c/n:.2%})")

    dom_cat, dom_count = cat_counter.most_common(1)[0]
    print(f"\n  Dominant: {dom_cat} (H={dom_count/n:.2%})")
    print(f"  H_OPERATION: {cat_counter.get('OPERATION', 0) / n:.2%}")

    # Save with same structure as other inventories
    out = {
        "_source": "Allen comparative Latin grammar / Gildersleeve & Lodge — productive derivational and inflectional morphemes",
        "_note": "Roots excluded (vast and trivially heterogeneous). This is the architectural morpheme inventory analogous to Voynich's atom layer.",
        "items": LATIN_MORPHEMES,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f"\n  Written: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
