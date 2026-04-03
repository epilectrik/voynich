"""
Extract operational profiles from all distinct Aqua Vitae Composita recipes
in Brunschwig's 1512 Large Book of Distillation (English translation).

Source: sources/brunschwig_1512/brunschwig_1512_english.txt
Focus: Chapter XXVI compound AV recipes + scattered recipes elsewhere.

Purpose: Compare operational signatures against 4 Voynich folios that
appear to encode alcohol-compound herbal preparations.
"""


def print_table(recipes):
    """Print recipes as a formatted comparison table."""

    # Header
    cols = [
        ("ID", 4),
        ("Name / Description", 42),
        ("Lines", 14),
        ("Ingr", 4),
        ("Steep", 22),
        ("Dist", 4),
        ("Fire Type", 14),
        ("Cohob", 5),
        ("Post-Dist Adds", 28),
        ("Ops", 3),
        ("Distinctive Feature", 44),
    ]

    sep = "+".join("-" * w for _, w in cols)
    sep = "+" + sep + "+"
    hdr = "|".join(h.center(w) for h, w in cols)
    hdr = "|" + hdr + "|"

    print("=" * 200)
    print("BRUNSCHWIG 1512 -- AQUA VITAE COMPOSITA: OPERATIONAL PROFILES")
    print("=" * 200)
    print()
    print(sep)
    print(hdr)
    print(sep)

    for r in recipes:
        row = "|".join(
            str(r[h]).ljust(w) if h != "ID" and h != "Ingr" and h != "Dist" and h != "Ops"
            else str(r[h]).center(w)
            for h, w in cols
        )
        print("|" + row + "|")
    print(sep)


def main():
    recipes = [
        # =====================================================================
        # RECIPE 1: Albertus Magnus AV Composita (the canonical recipe)
        # Chapter XXVI, pages 185-189
        # =====================================================================
        {
            "ID": "R1",
            "Name / Description":
                "Albertus Magnus AV Composita (canonical)",
            "Lines": "11875-11921",
            "Ingr": 10,
            "Steep":
                "8 or 43d balneum mariae",
            "Dist": 3,
            "Fire Type": "balneum mariae",
            "Cohob": "YES",
            "Post-Dist Adds": "none",
            "Ops": 8,
            "Distinctive Feature":
                "3 grades: Aqua benedicta / AV composita / Aqua balsami",
        },

        # =====================================================================
        # RECIPE 1b: Extended Simplicia addition to R1
        # Pages 187-188 -- optional herbal layer added to R1
        # =====================================================================
        {
            "ID": "R1b",
            "Name / Description":
                "R1 + herbal extension (rue/sage/castor)",
            "Lines": "11925-11936",
            "Ingr": 17,
            "Steep":
                "8 or 43d balneum mariae",
            "Dist": 3,
            "Fire Type": "balneum mariae",
            "Cohob": "YES",
            "Post-Dist Adds": "none",
            "Ops": 9,
            "Distinctive Feature":
                "Adds 7 botanicals (rue, sage, castoreum, citrus, etc.)",
        },

        # =====================================================================
        # RECIPE 2: "Drink of Youth" / Second Balsam
        # Pages 196-199 (lines 12293-12438)
        # =====================================================================
        {
            "ID": "R2",
            "Name / Description":
                "Drink of Youth / Second Balsam",
            "Lines": "12293-12438",
            "Ingr": 14,
            "Steep":
                "3wk horse dung / BM",
            "Dist": 4,
            "Fire Type": "BM x3, ash x1",
            "Cohob": "YES",
            "Post-Dist Adds": "none",
            "Ops": 10,
            "Distinctive Feature":
                "37 enumerated virtues; wine base not AV; final pass = ash",
        },

        # =====================================================================
        # RECIPE 3: Pestilence AV (composed 1511)
        # Pages 200-201 (lines 12447-12564)
        # =====================================================================
        {
            "ID": "R3",
            "Name / Description":
                "Anti-Pestilence AV (Brunschwig 1511)",
            "Lines": "12447-12564",
            "Ingr": 25,
            "Steep":
                "8d digestion",
            "Dist": 1,
            "Fire Type": "balneum mariae",
            "Cohob": "NO",
            "Post-Dist Adds": "musk, ambergris, saffron(silk), sugar, syrups, unicorn",
            "Ops": 12,
            "Distinctive Feature":
                "Pharmacopeia compounds (6 species); Boli Armeni 3x wash cycle",
        },

        # =====================================================================
        # RECIPE 4: Common Inexpensive AV
        # Pages 201-202 (lines 12569-12594)
        # =====================================================================
        {
            "ID": "R4",
            "Name / Description":
                "Common Inexpensive AV (3 spices)",
            "Lines": "12569-12594",
            "Ingr": 3,
            "Steep":
                "14d in tin pitcher",
            "Dist": 3,
            "Fire Type": "balneum mariae",
            "Cohob": "NO",
            "Post-Dist Adds": "2-3 gold ducats",
            "Ops": 5,
            "Distinctive Feature":
                "Minimal recipe: cinnamon+ginger+mace + gold coins",
        },

        # =====================================================================
        # RECIPE 5: Fourth AV -- Common Man's AV
        # Pages 202-203 (lines 12596-12621)
        # =====================================================================
        {
            "ID": "R5",
            "Name / Description":
                "Fourth AV (Common Man's recipe)",
            "Lines": "12596-12621",
            "Ingr": 3,
            "Steep":
                "8d horse dung",
            "Dist": 3,
            "Fire Type": "balneum mariae",
            "Cohob": "YES",
            "Post-Dist Adds": "none",
            "Ops": 7,
            "Distinctive Feature":
                "Simplest cohobation recipe; cloves+ginger+rosemary only",
        },

        # =====================================================================
        # RECIPE 6: Count Palatine's AV
        # Pages 203-204 (lines 12628-12682)
        # =====================================================================
        {
            "ID": "R6",
            "Name / Description":
                "Count Palatine of Rhine's AV",
            "Lines": "12628-12682",
            "Ingr": 27,
            "Steep":
                "30d buried in earth",
            "Dist": 4,
            "Fire Type": "balneum mariae",
            "Cohob": "YES",
            "Post-Dist Adds": "fresh sage at final pass",
            "Ops": 11,
            "Distinctive Feature":
                "Earth burial digestion (30d); fresh sage added at 4th pass",
        },

        # =====================================================================
        # RECIPE 7: Sixth AV / Water of Life (Brunschwig's masterwork)
        # Pages 204-214 (lines 12684-13092)
        # =====================================================================
        {
            "ID": "R7",
            "Name / Description":
                "Sixth AV / Water of Life (masterwork)",
            "Lines": "12684-13092",
            "Ingr": 68,
            "Steep":
                "2d herbs, 8d spices",
            "Dist": 2,
            "Fire Type": "BM + ash (3-frac)",
            "Cohob": "NO",
            "Post-Dist Adds": "ambergris, musk, 15 gold leaves, camphor, sugar",
            "Ops": 18,
            "Distinctive Feature":
                "2-stage load; 3-fraction distill (clear/yellow/black oil); gold leaf",
        },

        # =====================================================================
        # RECIPE 8: Delightful AV with Turpentine & Honey
        # Pages 215-219 (lines 13098-13236)
        # =====================================================================
        {
            "ID": "R8",
            "Name / Description":
                "Delightful AV (turpentine + honey)",
            "Lines": "13098-13236",
            "Ingr": 55,
            "Steep":
                "8d sealed, then 8d/3d",
            "Dist": 2,
            "Fire Type": "ash bath",
            "Cohob": "NO",
            "Post-Dist Adds": "musk (steeped not distilled), ambergris, 15 gold leaves",
            "Ops": 16,
            "Distinctive Feature":
                "Turpentine+honey base (unique); 3-stage ingredient loading",
        },

        # =====================================================================
        # RECIPE 9: Youth-restoring AV with honey & aloeswood
        # Pages 223-225 (lines 13379-13432)
        # =====================================================================
        {
            "ID": "R9",
            "Name / Description":
                "Youth AV (honey + aloeswood + gum arabic)",
            "Lines": "13379-13432",
            "Ingr": 12,
            "Steep":
                "8d horse dung",
            "Dist": 1,
            "Fire Type": "balneum mariae",
            "Cohob": "NO",
            "Post-Dist Adds": "musk, ambergris",
            "Ops": 6,
            "Distinctive Feature":
                "AV distilled 4x as base; honey + gum arabic = emulsifier; tooth whitening",
        },

        # =====================================================================
        # RECIPE 10: Another good AV (lavender/basil emphasis)
        # Pages 225-226 (lines 13434-13460)
        # =====================================================================
        {
            "ID": "R10",
            "Name / Description":
                "AV with lavender/basil/balm emphasis",
            "Lines": "13434-13460",
            "Ingr": 17,
            "Steep":
                "14d digestion",
            "Dist": 1,
            "Fire Type": "balneum mariae",
            "Cohob": "NO",
            "Post-Dist Adds": "musk (pre-loaded)",
            "Ops": 5,
            "Distinctive Feature":
                "Herbs dried NOT in sun; balm herb 2 lot = dominant aromatic",
        },

        # =====================================================================
        # RECIPE 11: AV for Palsy and Dizziness
        # Pages 226-227 (lines 13464-13488)
        # =====================================================================
        {
            "ID": "R11",
            "Name / Description":
                "AV for Palsy and Dizziness",
            "Lines": "13464-13488",
            "Ingr": 16,
            "Steep":
                "14d in white wine",
            "Dist": 1,
            "Fire Type": "per alembicum",
            "Cohob": "NO",
            "Post-Dist Adds": "none",
            "Ops": 4,
            "Distinctive Feature":
                "White wine base (not AV); sage 3/4 lb = dominant; peony emphasis",
        },

        # =====================================================================
        # RECIPE 12: Bishop of Strasbourg's AV
        # Pages 227-232 (lines 13492-13679)
        # =====================================================================
        {
            "ID": "R12",
            "Name / Description":
                "Bishop of Strasbourg's AV",
            "Lines": "13492-13679",
            "Ingr": 16,
            "Steep":
                "3-4d, then musk hung",
            "Dist": 2,
            "Fire Type": "BM (very slow)",
            "Cohob": "NO",
            "Post-Dist Adds": "musk in silk hung permanently; pharmacopeia species",
            "Ops": 10,
            "Distinctive Feature":
                "Musk hung in red silk cloth for life of water; organ-specific dosing",
        },

        # =====================================================================
        # RECIPE 13: Grand AV Composita (Ch. LXXXVII-LXXXVIII)
        # Pages 277-283 (lines 15426-15670)
        # =====================================================================
        {
            "ID": "R13",
            "Name / Description":
                "Grand AV Composita (Ch.LXXXVII-LXXXVIII)",
            "Lines": "15426-15670",
            "Ingr": 52,
            "Steep":
                "14d dist + 3d BM",
            "Dist": 2,
            "Fire Type": "ash + BM + filtrum",
            "Cohob": "NO",
            "Post-Dist Adds": "camphor, musk, 8 pharmacop. species, 10-20 gold ducats, sugar",
            "Ops": 15,
            "Distinctive Feature":
                "Filtration distillation (per Filtrum); gold = aurum potabile; month cellar rest",
        },

        # =====================================================================
        # RECIPE 14: Another AV to distill (later in text)
        # Pages 457-458 (lines 22080-22104)
        # =====================================================================
        {
            "ID": "R14",
            "Name / Description":
                "Simple AV (ginger-cinnamon-spice)",
            "Lines": "22080-22104",
            "Ingr": 11,
            "Steep":
                "8d standing",
            "Dist": 1,
            "Fire Type": "per alembicum",
            "Cohob": "NO",
            "Post-Dist Adds": "none",
            "Ops": 4,
            "Distinctive Feature":
                "Wine base (not AV); no cohobation; calamus+tormentil = digestive focus",
        },

        # =====================================================================
        # RECIPE 15: Common AV / Drink of Youth (sage-dominant)
        # Pages 458 (lines 22106-22122)
        # =====================================================================
        {
            "ID": "R15",
            "Name / Description":
                "Common AV / Drink of Youth (sage)",
            "Lines": "22106-22122",
            "Ingr": 10,
            "Steep":
                "14d steeping",
            "Dist": 1,
            "Fire Type": "balneum mariae",
            "Cohob": "NO",
            "Post-Dist Adds": "none",
            "Ops": 4,
            "Distinctive Feature":
                "Sage 3/4 lb dominant; optional rue/spikenard/citrus/castor upgrade",
        },
    ]

    print_table(recipes)

    # =========================================================================
    # SUMMARY STATISTICS
    # =========================================================================
    print()
    print("=" * 120)
    print("SUMMARY STATISTICS")
    print("=" * 120)
    print()

    total = len(recipes)
    print(f"Total distinct AV composita recipes extracted: {total}")
    print()

    # Cohobation count
    cohob_yes = sum(1 for r in recipes if r["Cohob"] == "YES")
    print(f"Recipes using cohobation (pour-back):  {cohob_yes}/{total}")
    print(f"Recipes without cohobation:            {total - cohob_yes}/{total}")
    print()

    # Fire types
    print("Fire type distribution:")
    fire_types = {}
    for r in recipes:
        ft = r["Fire Type"]
        fire_types[ft] = fire_types.get(ft, 0) + 1
    for ft, count in sorted(fire_types.items(), key=lambda x: -x[1]):
        print(f"  {ft:30s}  {count}")
    print()

    # Distillation passes
    print("Distillation pass distribution:")
    dist_counts = {}
    for r in recipes:
        d = r["Dist"]
        dist_counts[d] = dist_counts.get(d, 0) + 1
    for d in sorted(dist_counts.keys()):
        print(f"  {d} pass(es):  {dist_counts[d]} recipes")
    print()

    # Ingredient count range
    ingr_counts = [r["Ingr"] for r in recipes]
    print(f"Ingredient count range: {min(ingr_counts)} - {max(ingr_counts)}")
    print(f"  Mean: {sum(ingr_counts)/len(ingr_counts):.1f}")
    print(f"  Median: {sorted(ingr_counts)[len(ingr_counts)//2]}")
    print()

    # Post-distillation additions
    print("Post-distillation precious additions:")
    musk_count = sum(1 for r in recipes if "musk" in r["Post-Dist Adds"].lower())
    amber_count = sum(1 for r in recipes if "amber" in r["Post-Dist Adds"].lower())
    gold_count = sum(1 for r in recipes if "gold" in r["Post-Dist Adds"].lower())
    camphor_count = sum(1 for r in recipes if "camphor" in r["Post-Dist Adds"].lower())
    sugar_count = sum(1 for r in recipes if "sugar" in r["Post-Dist Adds"].lower())
    print(f"  Musk:      {musk_count}/{total}")
    print(f"  Ambergris: {amber_count}/{total}")
    print(f"  Gold:      {gold_count}/{total}")
    print(f"  Camphor:   {camphor_count}/{total}")
    print(f"  Sugar:     {sugar_count}/{total}")
    print()

    # Steeping method distribution
    print("Steeping/digestion method:")
    bm_steep = sum(1 for r in recipes if "balneum" in r["Steep"].lower() or "BM" in r["Steep"])
    horse = sum(1 for r in recipes if "horse" in r["Steep"].lower())
    earth = sum(1 for r in recipes if "earth" in r["Steep"].lower() or "buried" in r["Steep"].lower())
    plain = sum(1 for r in recipes if "standing" in r["Steep"].lower() or "steeping" in r["Steep"].lower()
                or "digestion" in r["Steep"].lower() or "sealed" in r["Steep"].lower()
                or "tin" in r["Steep"].lower())
    wine = sum(1 for r in recipes if "wine" in r["Steep"].lower())
    print(f"  Balneum mariae:  {bm_steep}")
    print(f"  Horse dung:      {horse}")
    print(f"  Buried in earth: {earth}")
    print(f"  White wine:      {wine}")
    print(f"  Plain standing:  {plain}")
    print()

    # =========================================================================
    # OPERATIONAL SIGNATURE COMPARISON GRID
    # =========================================================================
    print("=" * 120)
    print("OPERATIONAL SIGNATURE GRID (for Voynich folio comparison)")
    print("=" * 120)
    print()
    print("Feature dimensions that vary across recipes and could map to")
    print("Voynich token-level variation:")
    print()
    print("  1. COMPLEXITY TIER (ingredient count)")
    print("     Minimal (3-11):    R4, R5, R14, R15              -- 4 recipes")
    print("     Medium (12-17):    R1, R1b, R2, R9, R10, R11, R12 -- 7 recipes")
    print("     Complex (25-68):   R3, R6, R7, R8, R13           -- 5 recipes")
    print()
    print("  2. HEAT REGIME")
    print("     Pure BM (gentle):  R1, R1b, R3, R4, R5, R9, R10, R12, R15  -- 9 recipes")
    print("     BM + ash (graded): R2, R7, R13                             -- 3 recipes")
    print("     Pure ash:          R8                                       -- 1 recipe")
    print("     Unspecified:       R6, R11, R14                             -- 3 recipes")
    print()
    print("  3. COHOBATION (cyclical redistillation)")
    print("     Yes (3-4 passes):  R1, R1b, R2, R5, R6                     -- 5 recipes")
    print("     No (1-2 passes):   R3, R4, R7, R8, R9, R10, R11, R12-R15  -- 10 recipes")
    print()
    print("  4. DIGESTION METHOD")
    print("     Balneum mariae:    R1, R1b                    -- warm water bath")
    print("     Horse dung:        R2, R5, R9                 -- slow ferment heat")
    print("     Earth burial:      R6                          -- cool anaerobic")
    print("     Standing:          R4, R7, R8, R10, R14       -- ambient")
    print("     Wine soak:         R11, R15                    -- solvent extraction")
    print("     Mixed/staged:      R3, R12, R13               -- multiple phases")
    print()
    print("  5. POST-DISTILLATION ENRICHMENT (non-distilled additions)")
    print("     None:              R1, R1b, R2, R5, R6, R10, R11, R14, R15  -- 9 recipes")
    print("     Precious only:     R7, R8, R9, R12                          -- 4 recipes")
    print("     Pharmacopeia:      R3, R13                                  -- 2 recipes")
    print("     Gold + precious:   R4, R7, R8, R13                          -- 4 recipes")
    print()

    # =========================================================================
    # THIRD BOOK -- AV-based compound waters
    # =========================================================================
    print("=" * 120)
    print("THIRD BOOK (Das dritte Buch): AV-BASED COMPOUND WATERS")
    print("=" * 120)
    print()
    print("The Third Book (starting line 33395) contains disease-specific compound")
    print("waters but these are MIXED waters (combining pre-made distilled waters),")
    print("NOT AV composita recipes. They use AV as a dosing vehicle, not a base.")
    print()
    print("Pattern: 'Take [organ-specific water], 2 lot, + 1 spoonful AV, drink.'")
    print("This is the APPLICATION layer, not the PRODUCTION layer.")
    print()
    print("Exception found at line 33663: A compound water using distilled wine as")
    print("solvent with violet herb, digested 4d in horse dung, distilled 3x in BM,")
    print("then sun-aged 1 month. This is a compound water production recipe using")
    print("distilled wine, but it is NOT labeled as AV composita.")
    print()
    print("CONCLUSION: No new AV composita recipes in the Third Book.")
    print("All 16 recipes (15 distinct + 1 extension) are in Ch. XXVI + Ch. LXXXVII-LXXXVIII.")
    print()

    # =========================================================================
    # KEY OBSERVATIONS FOR VOYNICH COMPARISON
    # =========================================================================
    print("=" * 120)
    print("KEY OBSERVATIONS FOR VOYNICH FOLIO COMPARISON")
    print("=" * 120)
    print()
    print("1. GRADED DISTILLATION NAMES (R1): 1st = Aqua benedicta, 2nd = AV composita,")
    print("   3rd = Aqua balsami. This is a 3-tier quality ladder from a SINGLE recipe.")
    print("   A folio encoding this could show 3 paragraphs with increasing complexity.")
    print()
    print("2. OPERATIONAL VERBS (action vocabulary for Voynich token mapping):")
    print("   grind/pound, pour, seal, digest/steep, distill, pour-back (cohobate),")
    print("   strain, add, hang (musk in silk), bury, stir, settle, decant, store.")
    print("   Total distinct operations across all recipes: ~14 verb classes.")
    print()
    print("3. INGREDIENT CATEGORIES (5 tiers, loaded at different stages):")
    print("   a. SPICES (always present): ginger, cinnamon, cloves, nutmeg, mace,")
    print("      galangal, long pepper, cubeb, cardamom, grains of paradise, zedoary")
    print("   b. HERBS (often 2nd loading): sage, rosemary, rue, lavender, marjoram,")
    print("      pennyroyal, betony, hyssop, mint, wormwood")
    print("   c. RESINS/WOODS: aloeswood, balm of Gilead, spikenard, turpentine")
    print("   d. PRECIOUS (post-distill): musk, ambergris, camphor, gold, saffron")
    print("   e. PHARMACY (composita): theriac, mithridate, dya-series confections")
    print()
    print("4. UNIVERSAL CORE (appears in 12+ recipes): ginger, cinnamon, cloves,")
    print("   nutmeg, galangal. These 5 spices form the invariant kernel.")
    print("   -> Compare to Voynich B kernel tokens (high-frequency, positionally stable).")
    print()
    print("5. RECIPE COMPLEXITY CORRELATES WITH PATRON STATUS:")
    print("   Minimal (R4,R5):  'common man'  -- 3 ingredients, basic cohobation")
    print("   Medium (R2,R10):  'general use'  -- 14-17 ingredients, single feature")
    print("   Complex (R7,R13): 'bishop/duke'  -- 52-68 ingredients, multi-stage")
    print("   -> If Voynich folios encode recipes, paragraph density may signal tier.")
    print()
    print("6. COHOBATION = CYCLIC REDISTILLATION:")
    print("   5/15 recipes use pour-back. These all have 3-4 distillation passes.")
    print("   Cohobation recipes are structurally repetitive (same operation looped).")
    print("   -> Look for Voynich paragraphs with repeated token sequences.")
    print()
    print("7. TIME CONSTANTS:")
    print("   Digestion:  3d / 7d / 8d / 14d / 21d / 30d / 43d")
    print("   Distillation: slow drop-counting (1-2-3-4 = 1 drop)")
    print("   Post-aging: 1 month cellar rest (R13), 20-30 years optimal storage")
    print("   -> These temporal parameters could map to numerical tokens in Voynich.")


if __name__ == "__main__":
    main()
