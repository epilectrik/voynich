"""
Phase 8: Domain Overlay Stress-Testing

Tests 7 candidate real-world domains against the validated semantic model
to determine which could plausibly produce a system shaped like this.

Ground Rules:
1. Model is frozen - no changes to roles, operators, grammar, slots
2. No word guessing - only structural role mapping
3. Score fit, not truth - testing plausibility, not claiming certainty
4. Kill weak hypotheses fast - most domains should fail quickly
5. Survivors must explain the shape - why this structure, why A/B, why operators
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Model constants from Phase 7 (FROZEN)
MODEL = {
    "clusters": {
        "FLEXIBLE_CORE": {
            "size": 35,
            "mean_a_ratio": 0.40,
            "description": "High affix compatibility, grammatically versatile",
            "examples": ["ka", "ho", "o", "ko", "ai"]
        },
        "DEFINITION_CORE": {
            "size": 25,
            "mean_a_ratio": 0.755,
            "description": "Primarily A-text, marks core definitions",
            "examples": ["hor", "hold", "sy", "tcho", "hocth"]
        },
        "EXPOSITION_CORE": {
            "size": 33,
            "mean_a_ratio": 0.122,
            "description": "Primarily B-text, marks applications/expositions",
            "examples": ["hek", "ckh", "ky", "hcth", "ty"]
        },
        "RESTRICTED_CORE": {
            "size": 187,  # clusters 2 and 4 combined
            "mean_a_ratio": 0.26,
            "description": "Low variability, constrained semantic usage",
            "examples": ["ar", "taii", "y", "or", "ha"]
        }
    },
    "operators": {
        "POSITION": {
            "count": 6,
            "members": ["cf", "fc", "of", "op", "cp", "ts"],
            "function": "Entry-initial markers, control slot placement"
        },
        "SCOPE": {
            "count": 16,
            "members": ["cho", "cha", "sho", "sha", "ot", "dai", "al", "oko", "ara"],
            "function": "Hub/category association modifiers (>40% concentration)"
        },
        "SEMANTIC": {
            "count": 8,
            "members": ["sh", "or", "ol", "ok", "po", "che", "she", "ota"],
            "function": "General content/semantic modifiers"
        }
    },
    "grammar": {
        "slots": 10,
        "rules": 11,
        "coverage": 0.951,
        "slot_roles": {
            "0": "TOPIC - Entry topic/subject introduction",
            "1-2": "PRIMARY - Primary content/predicate position",
            "3-5": "SECONDARY - Secondary content/argument position",
            "6-7": "MODIFIER - Modifier/elaboration position",
            "8-9": "TERMINAL - Terminal/closing position"
        },
        "constraint_ratio": 0.95  # 95% of transitions are forbidden
    },
    "populations": {
        "A": {
            "entries": 114,
            "mean_words": 124,
            "dominant_core": "DEFINITION_CORE",
            "core_concentration": 0.755
        },
        "B": {
            "entries": 83,
            "mean_words": 352,
            "dominant_core": "EXPOSITION_CORE",
            "core_concentration": 0.878,
            "length_ratio": 2.84  # B is 2.84x longer than A
        }
    },
    "hubs": {
        "count": 8,
        "primary": ["tol", "pol", "sho", "tor"],
        "secondary": ["pchor", "par", "paiin", "kor"],
        "mean_heading_length": 4.0,
        "reference_counts": {"tol": 34, "pol": 25, "sho": 19, "tor": 14}
    }
}

# Define the 7 candidate domains
DOMAINS = {
    "D1": {
        "name": "Pharmacology / Materia Medica",
        "rationale": "Property-based plant classification, therapeutic applications"
    },
    "D2": {
        "name": "Alchemical Transformation Grammar",
        "rationale": "Process stages, substance states, transformation rules"
    },
    "D3": {
        "name": "Medical Diagnostics",
        "rationale": "Symptom-treatment mapping, condition-remedy pairing"
    },
    "D4": {
        "name": "Natural Property Classification",
        "rationale": "Non-taxonomic properties (hot/cold, wet/dry, degrees)"
    },
    "D5": {
        "name": "Logical/Inferential Rule System",
        "rationale": "Formal reasoning, conditional rules, argument structure"
    },
    "D6": {
        "name": "Astrological Influence Grammar",
        "rationale": "Planetary influences, aspects, applications (not zodiac labels)"
    },
    "D7": {
        "name": "Agricultural Process Encoding",
        "rationale": "Cultivation stages, seasonal procedures, crop properties"
    }
}


def construct_overlay(domain_id: str) -> Dict:
    """Construct a semantic overlay mapping for a given domain."""

    domain = DOMAINS[domain_id]
    name = domain["name"]

    overlays = {
        "D1": {  # Pharmacology / Materia Medica
            "slot_interpretation": {
                "SLOT_0": "Primary substance/plant identifier",
                "SLOT_1_2": "Primary therapeutic property or action",
                "SLOT_3_5": "Secondary indications or preparations",
                "SLOT_6_7": "Dosage/application modifiers",
                "SLOT_8_9": "Contraindications or terminal notes"
            },
            "role_mapping": {
                "DEFINITION_CORE": "Core substances/simples (75% in A = definitional catalog)",
                "EXPOSITION_CORE": "Compound preparations/applications (88% in B = applied formulas)",
                "FLEXIBLE_CORE": "Common modifiers (hot, cold, degrees, parts)",
                "RESTRICTED_CORE": "Specific properties with constrained usage"
            },
            "operator_interpretation": {
                "POSITION": "Entry structure markers (this preparation starts here)",
                "SCOPE": "Category shifters (from herb X to preparation type Y)",
                "SEMANTIC": "Property modifiers (degree, quality, part)"
            },
            "ab_function": {
                "A_text": "Materia medica definitions - what each simple IS",
                "B_text": "Pharmaceutical applications - how to USE combinations",
                "length_explanation": "Applications require more detail (dosing, timing, preparation steps)"
            },
            "hub_interpretation": "8 major drug categories (purgatives, tonics, etc.) or humoral classes"
        },

        "D2": {  # Alchemical Transformation Grammar
            "slot_interpretation": {
                "SLOT_0": "Starting material or stage identifier",
                "SLOT_1_2": "Primary transformation operation",
                "SLOT_3_5": "Secondary processes or reagents",
                "SLOT_6_7": "Condition modifiers (heat, time, vessel)",
                "SLOT_8_9": "Result state or next stage"
            },
            "role_mapping": {
                "DEFINITION_CORE": "Prima materia / base substances (definitional)",
                "EXPOSITION_CORE": "Process descriptions / transformation sequences",
                "FLEXIBLE_CORE": "Universal operations (solve, coagula, distill)",
                "RESTRICTED_CORE": "Specific reagents or states with limited contexts"
            },
            "operator_interpretation": {
                "POSITION": "Stage markers (begin sequence, end sequence)",
                "SCOPE": "Process category shifters (wet path vs dry path)",
                "SEMANTIC": "Quality modifiers (degree of calcination, purity)"
            },
            "ab_function": {
                "A_text": "Definitions of materials and their properties",
                "B_text": "Detailed process sequences and transformations",
                "length_explanation": "Processes require step-by-step elaboration"
            },
            "hub_interpretation": "8 major stages (nigredo, albedo, etc.) or 7 metals + 1 stone"
        },

        "D3": {  # Medical Diagnostics
            "slot_interpretation": {
                "SLOT_0": "Primary symptom or condition",
                "SLOT_1_2": "Diagnostic indicators",
                "SLOT_3_5": "Treatment approaches",
                "SLOT_6_7": "Prognostic modifiers",
                "SLOT_8_9": "Outcome expectations or warnings"
            },
            "role_mapping": {
                "DEFINITION_CORE": "Disease definitions / condition categories",
                "EXPOSITION_CORE": "Treatment protocols / case discussions",
                "FLEXIBLE_CORE": "Common symptoms that appear across conditions",
                "RESTRICTED_CORE": "Specific diagnostic signs with limited contexts"
            },
            "operator_interpretation": {
                "POSITION": "Entry structure (this case begins here)",
                "SCOPE": "Body system shifters (from symptom to affected organ)",
                "SEMANTIC": "Severity/quality modifiers"
            },
            "ab_function": {
                "A_text": "Disease definitions and diagnostic criteria",
                "B_text": "Extended treatment discussions and case analyses",
                "length_explanation": "Treatments require more elaborate instructions than definitions"
            },
            "hub_interpretation": "8 major body systems or humoral disease categories"
        },

        "D4": {  # Natural Property Classification
            "slot_interpretation": {
                "SLOT_0": "Entity being classified",
                "SLOT_1_2": "Primary quality assignments (hot/cold, wet/dry)",
                "SLOT_3_5": "Degree specifications and secondary qualities",
                "SLOT_6_7": "Contextual modifiers",
                "SLOT_8_9": "Application contexts or notes"
            },
            "role_mapping": {
                "DEFINITION_CORE": "Core entities with defined properties",
                "EXPOSITION_CORE": "Property applications and combinations",
                "FLEXIBLE_CORE": "Quality terms that apply across categories",
                "RESTRICTED_CORE": "Specific degree markers with constrained usage"
            },
            "operator_interpretation": {
                "POSITION": "Classification entry structure",
                "SCOPE": "Quality domain shifters (from hot/cold to wet/dry)",
                "SEMANTIC": "Degree modifiers (1st, 2nd, 3rd, 4th degree)"
            },
            "ab_function": {
                "A_text": "Property definitions - what quality X means",
                "B_text": "Extended applications - how qualities interact/combine",
                "length_explanation": "Combinations and applications need elaboration"
            },
            "hub_interpretation": "8 fundamental qualities or 4 elements x 2 states"
        },

        "D5": {  # Logical/Inferential Rule System
            "slot_interpretation": {
                "SLOT_0": "Rule identifier or antecedent marker",
                "SLOT_1_2": "Primary conditions",
                "SLOT_3_5": "Consequent terms or secondary conditions",
                "SLOT_6_7": "Qualifying clauses",
                "SLOT_8_9": "Conclusion markers or rule terminators"
            },
            "role_mapping": {
                "DEFINITION_CORE": "Primitive terms / axioms",
                "EXPOSITION_CORE": "Derived rules / complex inferences",
                "FLEXIBLE_CORE": "Logical connectives and quantifiers",
                "RESTRICTED_CORE": "Specific terms with constrained logical roles"
            },
            "operator_interpretation": {
                "POSITION": "Rule structure markers (if, then, therefore)",
                "SCOPE": "Domain shifters (from premise to conclusion)",
                "SEMANTIC": "Modality modifiers (necessity, possibility)"
            },
            "ab_function": {
                "A_text": "Basic rules and definitions",
                "B_text": "Extended derivations and complex arguments",
                "length_explanation": "Derivations chain multiple steps"
            },
            "hub_interpretation": "8 major rule categories or inference types"
        },

        "D6": {  # Astrological Influence Grammar
            "slot_interpretation": {
                "SLOT_0": "Planetary/celestial identifier",
                "SLOT_1_2": "Primary influence or aspect",
                "SLOT_3_5": "Secondary influences or house positions",
                "SLOT_6_7": "Temporal/conditional modifiers",
                "SLOT_8_9": "Application or outcome notes"
            },
            "role_mapping": {
                "DEFINITION_CORE": "Planetary nature definitions",
                "EXPOSITION_CORE": "Influence applications and combinations",
                "FLEXIBLE_CORE": "Aspect terms that apply across planets",
                "RESTRICTED_CORE": "Specific dignities/debilities with constrained usage"
            },
            "operator_interpretation": {
                "POSITION": "Chart/reading structure markers",
                "SCOPE": "Domain shifters (from planet to house to aspect)",
                "SEMANTIC": "Strength/quality modifiers (benefic, malefic)"
            },
            "ab_function": {
                "A_text": "Planet/sign definitions and essential natures",
                "B_text": "Extended horoscope applications and delineations",
                "length_explanation": "Delineations elaborate on combinations of influences"
            },
            "hub_interpretation": "7 planets + 1 node, or 8 major dignity types"
        },

        "D7": {  # Agricultural Process Encoding
            "slot_interpretation": {
                "SLOT_0": "Crop or process identifier",
                "SLOT_1_2": "Primary cultivation action",
                "SLOT_3_5": "Secondary procedures or conditions",
                "SLOT_6_7": "Timing/seasonal modifiers",
                "SLOT_8_9": "Expected outcomes or notes"
            },
            "role_mapping": {
                "DEFINITION_CORE": "Crop definitions and characteristics",
                "EXPOSITION_CORE": "Cultivation sequences and procedures",
                "FLEXIBLE_CORE": "Common actions (sow, harvest, water)",
                "RESTRICTED_CORE": "Specific treatments with constrained contexts"
            },
            "operator_interpretation": {
                "POSITION": "Sequence markers (start planting, end harvest)",
                "SCOPE": "Domain shifters (from field prep to planting to harvest)",
                "SEMANTIC": "Condition modifiers (soil type, weather)"
            },
            "ab_function": {
                "A_text": "Crop definitions - what each plant needs",
                "B_text": "Cultivation procedures - how to grow and process",
                "length_explanation": "Procedures have multiple seasonal steps"
            },
            "hub_interpretation": "8 major crop categories or seasonal divisions"
        }
    }

    return {
        "domain_id": domain_id,
        "domain_name": name,
        "rationale": domain["rationale"],
        "overlay": overlays[domain_id]
    }


def test_slot_count_plausibility(domain_id: str, overlay: Dict) -> Dict:
    """Test A: Does typical entry length (5-10 GAMMA tokens) make sense?"""

    # Model facts: 10 slots, A entries ~124 words, B entries ~352 words
    # Typical content tokens per entry: 5-15 for A, 15-50 for B

    assessments = {
        "D1": {
            "score": "PASS",
            "reasoning": "Materia medica entries typically list: substance, properties (2-3), preparations (2-3), applications (2-3). 5-10 core content elements is standard for herbal entries."
        },
        "D2": {
            "score": "PASS",
            "reasoning": "Alchemical operations often have 5-12 stages. Each stage is a transformation step. Entry length matches process description."
        },
        "D3": {
            "score": "PASS",
            "reasoning": "Medical entries: symptom, diagnosis, treatment approach, modifiers, prognosis. 5-10 slots matches typical diagnostic schema."
        },
        "D4": {
            "score": "PASS",
            "reasoning": "Property classification: entity, primary qualities (2), secondary qualities (2), degrees (2), applications (2). Matches slot structure."
        },
        "D5": {
            "score": "WEAK",
            "reasoning": "Logical rules vary widely in complexity. Simple rules need 3-4 slots, complex derivations need many more. 10-slot fixed structure is somewhat rigid for logic."
        },
        "D6": {
            "score": "PASS",
            "reasoning": "Astrological delineations: planet, sign, house, aspects (2-3), applications (2-3). 5-10 elements is typical for horoscope entries."
        },
        "D7": {
            "score": "PASS",
            "reasoning": "Agricultural entries: crop, soil prep, planting, care (2-3), harvest, processing. 5-10 slots matches seasonal procedure description."
        }
    }

    result = assessments[domain_id]
    return {
        "test": "A - Slot Count Plausibility",
        "question": "Does typical entry length (5-10 GAMMA tokens) make sense?",
        "score": result["score"],
        "reasoning": result["reasoning"]
    }


def test_ab_usage_alignment(domain_id: str, overlay: Dict) -> Dict:
    """Test B: Does A=short definitions, B=long expositions match domain workflow?"""

    # Model facts: A=124 words (definitions), B=352 words (expositions), 2.84x ratio
    # DEFINITION_CORE 75% in A, EXPOSITION_CORE 88% in B

    assessments = {
        "D1": {
            "score": "PASS",
            "reasoning": "Materia medica DEFINES simples briefly in catalog form (A), then APPLIES them in compound preparations requiring detailed instructions (B). 2.84x length difference aligns with definition vs recipe elaboration."
        },
        "D2": {
            "score": "PASS",
            "reasoning": "Alchemy DEFINES substances/stages briefly (A), then elaborates PROCESSES with step-by-step sequences (B). Length ratio matches definition vs procedural description."
        },
        "D3": {
            "score": "PASS",
            "reasoning": "Medicine DEFINES diseases/conditions briefly (A), then elaborates treatment protocols (B). Diagnostic criteria are short; treatment discussions are long."
        },
        "D4": {
            "score": "WEAK",
            "reasoning": "Property classification is more uniform. Both definitions and applications are typically brief. The 2.84x length difference is harder to explain - property combinations shouldn't need 3x more text."
        },
        "D5": {
            "score": "WEAK",
            "reasoning": "Logical systems don't naturally split into short definitions vs long derivations with this ratio. Axioms are short, but so are most derived rules. Extended proofs exist but don't dominate."
        },
        "D6": {
            "score": "PASS",
            "reasoning": "Astrology DEFINES planetary natures briefly (A), then elaborates delineations with multiple aspect interpretations (B). A natal chart reading is indeed much longer than a planet definition."
        },
        "D7": {
            "score": "PASS",
            "reasoning": "Agriculture DEFINES crops briefly (A), then elaborates seasonal procedures with multiple steps (B). Cultivation instructions are inherently longer than crop identification."
        }
    }

    result = assessments[domain_id]
    return {
        "test": "B - A/B Usage Alignment",
        "question": "Does A=short definitions, B=long expositions match domain workflow?",
        "model_facts": "A=124 words, B=352 words (2.84x), DEFINITION_CORE 75% in A, EXPOSITION_CORE 88% in B",
        "score": result["score"],
        "reasoning": result["reasoning"]
    }


def test_operator_scope_alignment(domain_id: str, overlay: Dict) -> Dict:
    """Test C: Do hub-shifting operators and positional markers make sense?"""

    # Model facts:
    # - 6 POSITION operators (entry-initial markers)
    # - 16 SCOPE operators (shift hub/category association, >40% concentration)
    # - 8 SEMANTIC operators (general modifiers)

    assessments = {
        "D1": {
            "score": "PASS",
            "reasoning": "Pharmacology needs: category markers (purgative, tonic), scope shifters (from herb to preparation type), and semantic modifiers (degree, part). Hub-shifting operators map to drug class changes within compounds."
        },
        "D2": {
            "score": "PASS",
            "reasoning": "Alchemy needs: stage markers (begin/end), process shifters (calcination -> dissolution), quality modifiers. Scope operators as process-category shifters fits well."
        },
        "D3": {
            "score": "PASS",
            "reasoning": "Medical diagnostics needs: case structure markers, system shifters (from symptom to organ to treatment), severity modifiers. Hub-shifting for body system navigation."
        },
        "D4": {
            "score": "WEAK",
            "reasoning": "Property classification has fewer natural scope-shifts. Hot/cold and wet/dry are the main domains. 16 scope operators seems excessive for a 4-quality system."
        },
        "D5": {
            "score": "FAIL",
            "reasoning": "Logical systems use connectives (and, or, if-then) not scope-shifting operators. The hub-association mechanism doesn't map well to logical structure. Position markers work, but scope operators are misaligned."
        },
        "D6": {
            "score": "PASS",
            "reasoning": "Astrology needs: chart position markers, domain shifters (planet -> house -> aspect), and influence modifiers. Scope operators as domain navigators fits perfectly."
        },
        "D7": {
            "score": "WEAK",
            "reasoning": "Agriculture has seasonal scope-shifts but 16 distinct scope operators seems excessive. Planting -> growing -> harvesting is only 3 major scope changes."
        }
    }

    result = assessments[domain_id]
    return {
        "test": "C - Operator Scope Alignment",
        "question": "Do hub-shifting operators and positional markers make sense?",
        "model_facts": "6 POSITION, 16 SCOPE (>40% hub concentration), 8 SEMANTIC operators",
        "score": result["score"],
        "reasoning": result["reasoning"]
    }


def test_role_distribution_fit(domain_id: str, overlay: Dict) -> Dict:
    """Test D: Do the 4 role types map plausibly to domain primitives?"""

    # Model facts:
    # - DEFINITION_CORE (25, 75.5% A): definitional primitives
    # - EXPOSITION_CORE (33, 12.2% A = 88% B): application vocabulary
    # - FLEXIBLE_CORE (35, 40% A): versatile elements
    # - RESTRICTED_CORE (187, 26% A): constrained terms

    assessments = {
        "D1": {
            "score": "PASS",
            "reasoning": "DEFINITION_CORE=25 base herbs. EXPOSITION_CORE=33 preparation types. FLEXIBLE_CORE=35 common modifiers (hot, cold, degrees). RESTRICTED_CORE=187 specific properties/effects. Distribution matches materia medica vocabulary structure."
        },
        "D2": {
            "score": "PASS",
            "reasoning": "DEFINITION_CORE=materials/substances. EXPOSITION_CORE=process verbs. FLEXIBLE_CORE=universal operations (solve, coagula). RESTRICTED_CORE=specific reagents and states. Matches alchemical vocabulary."
        },
        "D3": {
            "score": "PASS",
            "reasoning": "DEFINITION_CORE=disease categories. EXPOSITION_CORE=treatment actions. FLEXIBLE_CORE=common symptoms. RESTRICTED_CORE=specific diagnostic signs. Matches diagnostic vocabulary."
        },
        "D4": {
            "score": "WEAK",
            "reasoning": "DEFINITION_CORE would be quality terms (hot, cold, wet, dry) but that's only ~4, not 25. RESTRICTED_CORE at 187 seems too large for a property classification system with limited qualities."
        },
        "D5": {
            "score": "FAIL",
            "reasoning": "DEFINITION_CORE as axioms makes sense (25 primitives). But RESTRICTED_CORE at 187 specific terms with constrained usage doesn't match logical vocabulary, which is typically small and precisely defined."
        },
        "D6": {
            "score": "PASS",
            "reasoning": "DEFINITION_CORE=7 planets + essentials. EXPOSITION_CORE=aspects and delineations. FLEXIBLE_CORE=universal significators. RESTRICTED_CORE=specific dignities, terms, faces. Matches astrological vocabulary."
        },
        "D7": {
            "score": "WEAK",
            "reasoning": "DEFINITION_CORE=crops (25 plausible). EXPOSITION_CORE=procedures. But RESTRICTED_CORE at 187 seems large for agricultural terminology, which is relatively simple."
        }
    }

    result = assessments[domain_id]
    return {
        "test": "D - Role Distribution Fit",
        "question": "Do role cluster sizes match expected domain vocabulary structure?",
        "model_facts": "DEFINITION=25 (75% A), EXPOSITION=33 (88% B), FLEXIBLE=35 (40% A), RESTRICTED=187 (26% A)",
        "score": result["score"],
        "reasoning": result["reasoning"]
    }


def test_abstraction_justification(domain_id: str, overlay: Dict) -> Dict:
    """Test E: Why would domain X abstract away referents?"""

    # Model facts: No plant names, no zodiac labels, no obvious referents
    # High abstraction - referential content is encoded, not named

    assessments = {
        "D1": {
            "score": "PASS",
            "reasoning": "Pharmacological shorthand is historically common. Practitioners used category codes, not full plant names. Secrecy, space constraints, and professional jargon all justify abstraction. Apothecaries' marks were intentionally opaque."
        },
        "D2": {
            "score": "PASS",
            "reasoning": "Alchemy is FAMOUS for deliberate obscurity. Decknamen (cover names), symbolic encoding, and intentional veiling of processes is the historical norm. Abstraction is expected, even required."
        },
        "D3": {
            "score": "WEAK",
            "reasoning": "Medical texts typically name conditions and treatments explicitly for practical use. Abstraction would reduce clinical utility. Some guild secrecy existed, but medical texts are usually direct."
        },
        "D4": {
            "score": "PASS",
            "reasoning": "Property classification systems are inherently abstract. Galenic qualities (hot, cold, wet, dry) and degrees ARE the abstraction - no need for specific referents. System encodes relationships, not instances."
        },
        "D5": {
            "score": "PASS",
            "reasoning": "Logical systems are definitionally abstract. Variables, predicates, and rules don't name specific referents. Abstraction is the point, not a choice."
        },
        "D6": {
            "score": "WEAK",
            "reasoning": "Astrological texts typically name planets, signs, and houses explicitly. Some shorthand exists (glyphs), but the underlying referents (Mars, Leo, 7th house) are usually stated. Full abstraction is unusual."
        },
        "D7": {
            "score": "FAIL",
            "reasoning": "Agricultural texts are practical. Farmers need to know which crop, which season, which procedure. Abstracting away the referents would make the text useless for actual farming."
        }
    }

    result = assessments[domain_id]
    return {
        "test": "E - Abstraction Justification",
        "question": "Why would domain X abstract away referents (no named plants, etc.)?",
        "score": result["score"],
        "reasoning": result["reasoning"]
    }


def test_hub_category_fit(domain_id: str, overlay: Dict) -> Dict:
    """Test F: Could 8 major categories naturally organize domain X?"""

    # Model facts:
    # - 8 hubs: tol, pol, sho, tor, pchor, par, paiin, kor
    # - Hub headings are short (4.0 chars mean)
    # - Hubs have functional roles (opener, closer, support)

    assessments = {
        "D1": {
            "score": "PASS",
            "reasoning": "8 drug categories is plausible: purgatives, emetics, tonics, sedatives, febrifuges, digestives, topicals, compound preparations. Medieval pharmacology often used ~8 major groupings."
        },
        "D2": {
            "score": "PASS",
            "reasoning": "8 stages/categories: 7 classical metals (lead->gold) + the philosophers' stone. Or 8 operations: calcination, solution, separation, conjunction, putrefaction, congelation, cibation, sublimation."
        },
        "D3": {
            "score": "PASS",
            "reasoning": "8 body systems or disease categories is plausible. Galenic medicine recognized ~8 major organ systems. Humoral theory provides another categorical framework."
        },
        "D4": {
            "score": "WEAK",
            "reasoning": "4 elements x 2 = 8 is forced. The natural property framework has 4 qualities, not 8. Two extra categories need justification."
        },
        "D5": {
            "score": "FAIL",
            "reasoning": "Logical systems don't naturally partition into 8 categories. Aristotelian syllogisms have 3-4 figures. Modal logic doesn't use 8-fold categories. The hub structure is misaligned."
        },
        "D6": {
            "score": "PASS",
            "reasoning": "7 planets + 1 node = 8. Or 7 planets + lot of fortune. Astrological systems naturally use 7-8 primary significators as organizing categories."
        },
        "D7": {
            "score": "WEAK",
            "reasoning": "8 crop categories is possible but arbitrary. Agricultural organization is usually by season (4) or crop type (grains, vegetables, fruits = 3-5). 8 specific categories needs more justification."
        }
    }

    result = assessments[domain_id]
    return {
        "test": "F - Hub Category Fit",
        "question": "Could 8 major categories naturally organize domain X?",
        "model_facts": "8 hubs, mean heading length 4.0 chars, functional roles (opener/closer/support)",
        "score": result["score"],
        "reasoning": result["reasoning"]
    }


def score_domain(tests: List[Dict]) -> Tuple[float, str, str]:
    """Calculate domain score and verdict."""

    pass_count = sum(1 for t in tests if t["score"] == "PASS")
    weak_count = sum(1 for t in tests if t["score"] == "WEAK")
    fail_count = sum(1 for t in tests if t["score"] == "FAIL")

    score = pass_count + 0.5 * weak_count

    # Elimination rule: 2+ FAILs = eliminated
    if fail_count >= 2:
        verdict = "ELIMINATED"
        elimination_reason = f"{fail_count} FAIL scores (threshold: <2)"
    elif fail_count == 1:
        verdict = "SURVIVES_WEAK" if score >= 3.5 else "ELIMINATED"
        elimination_reason = "1 FAIL but insufficient compensating passes" if verdict == "ELIMINATED" else None
    else:
        verdict = "SURVIVES"
        elimination_reason = None

    return score, verdict, elimination_reason


def analyze_survivor(domain_id: str, overlay_result: Dict, tests: List[Dict]) -> Dict:
    """Generate detailed analysis for surviving domains."""

    name = overlay_result["domain_name"]
    overlay = overlay_result["overlay"]

    # Why it fits - based on PASSing tests
    why_fits = []
    for t in tests:
        if t["score"] == "PASS":
            why_fits.append(f"{t['test'].split('-')[1].strip()}: {t['reasoning'][:100]}...")

    # What it explains
    explanations = {
        "D1": {
            "ab_split": "A defines simples (materia medica catalog), B applies them in compound preparations",
            "operators": "Scope operators shift between drug categories (purgative, tonic, etc.)",
            "abstraction": "Apothecary marks and professional jargon justify encoding over naming",
            "hub_categories": "8 major drug classes organize the pharmacopeia"
        },
        "D2": {
            "ab_split": "A defines materials and their natures, B describes transformation sequences",
            "operators": "Scope operators mark process transitions (calcination -> dissolution)",
            "abstraction": "Alchemy intentionally veils knowledge; Decknamen are historically documented",
            "hub_categories": "7 metals + stone, or 8 major alchemical operations"
        },
        "D3": {
            "ab_split": "A defines diseases/conditions, B elaborates treatment protocols",
            "operators": "Scope operators navigate body systems (from symptom to organ to treatment)",
            "abstraction": "Guild secrecy existed but is less common than in alchemy",
            "hub_categories": "8 major organ systems or humoral disease categories"
        },
        "D6": {
            "ab_split": "A defines planetary natures, B elaborates chart delineations",
            "operators": "Scope operators navigate astrological domains (planet -> house -> aspect)",
            "abstraction": "Less justified - astrology typically names its referents explicitly",
            "hub_categories": "7 planets + 1 node naturally provides 8-fold organization"
        }
    }

    if domain_id not in explanations:
        explanations[domain_id] = {
            "ab_split": "Definitions vs applications pattern",
            "operators": "Domain-specific scope navigation",
            "abstraction": "Domain-specific justification",
            "hub_categories": "8 natural categories"
        }

    # Predictions if this domain is correct
    predictions = {
        "D1": [
            "Hub headings should group semantically by therapeutic effect",
            "Scope operators should correlate with preparation type changes",
            "Entry structure should match: substance -> properties -> preparations -> applications"
        ],
        "D2": [
            "Sequence of slots should mirror alchemical process order",
            "Scope operators should correlate with stage transitions",
            "Entry structure should match: material -> operation -> conditions -> result"
        ],
        "D3": [
            "Entry structure should match: symptom -> diagnosis -> treatment -> prognosis",
            "Scope operators should correlate with anatomical system changes",
            "EXPOSITION_CORE tokens should relate to treatment actions"
        ],
        "D6": [
            "Hub structure should reflect planetary hierarchy",
            "Scope operators should correlate with chart domain transitions",
            "DEFINITION_CORE tokens should include planetary significators"
        ]
    }

    if domain_id not in predictions:
        predictions[domain_id] = ["Generic prediction 1", "Generic prediction 2"]

    return {
        "domain_id": domain_id,
        "domain_name": name,
        "why_it_fits": why_fits,
        "what_it_explains": explanations[domain_id],
        "what_it_predicts": predictions[domain_id],
        "remaining_questions": [
            "Would need external evidence (plant IDs, recipe matches) to confirm",
            "Abstraction level still unexplained for practical use",
            "Hub heading meanings unverified"
        ]
    }


def run_phase8():
    """Execute Phase 8 domain overlay stress-testing."""

    print("=" * 70)
    print("PHASE 8: DOMAIN OVERLAY STRESS-TESTING")
    print("=" * 70)
    print()

    # Step 1: Model Summary
    print("STEP 1: MODEL SUMMARY (FROZEN)")
    print("-" * 40)
    print(f"Clusters: {sum(c['size'] for c in MODEL['clusters'].values())} middles in 4 role types")
    for name, cluster in MODEL["clusters"].items():
        print(f"  {name}: {cluster['size']} middles, {cluster['mean_a_ratio']*100:.1f}% A-text")
    print(f"Operators: {sum(o['count'] for o in MODEL['operators'].values())} total")
    for name, op in MODEL["operators"].items():
        print(f"  {name}: {op['count']} ({op['function'][:50]}...)")
    print(f"Grammar: {MODEL['grammar']['slots']} slots, {MODEL['grammar']['rules']} rules, {MODEL['grammar']['coverage']*100:.1f}% coverage")
    print(f"A entries: {MODEL['populations']['A']['entries']}, mean {MODEL['populations']['A']['mean_words']} words")
    print(f"B entries: {MODEL['populations']['B']['entries']}, mean {MODEL['populations']['B']['mean_words']} words (2.84x)")
    print(f"Hubs: {MODEL['hubs']['count']} categories")
    print()

    # Step 2-4: Test each domain
    all_overlays = {}
    all_eliminations = []
    all_survivors = []

    for domain_id in DOMAINS:
        print(f"TESTING {domain_id}: {DOMAINS[domain_id]['name']}")
        print("-" * 40)

        # Construct overlay
        overlay_result = construct_overlay(domain_id)

        # Run all 6 tests
        tests = [
            test_slot_count_plausibility(domain_id, overlay_result),
            test_ab_usage_alignment(domain_id, overlay_result),
            test_operator_scope_alignment(domain_id, overlay_result),
            test_role_distribution_fit(domain_id, overlay_result),
            test_abstraction_justification(domain_id, overlay_result),
            test_hub_category_fit(domain_id, overlay_result)
        ]

        # Print test results
        for t in tests:
            print(f"  {t['test']}: {t['score']}")

        # Score
        score, verdict, elimination_reason = score_domain(tests)
        print(f"  SCORE: {score}/6.0")
        print(f"  VERDICT: {verdict}")
        if elimination_reason:
            print(f"  REASON: {elimination_reason}")
        print()

        # Store results
        overlay_entry = {
            "domain_id": domain_id,
            "domain_name": DOMAINS[domain_id]["name"],
            "rationale": DOMAINS[domain_id]["rationale"],
            "overlay": overlay_result["overlay"],
            "tests": tests,
            "score": score,
            "verdict": verdict
        }
        all_overlays[domain_id] = overlay_entry

        if verdict == "ELIMINATED":
            all_eliminations.append({
                "domain_id": domain_id,
                "domain_name": DOMAINS[domain_id]["name"],
                "score": score,
                "elimination_reason": elimination_reason,
                "failed_tests": [t["test"] for t in tests if t["score"] == "FAIL"]
            })
        else:
            survivor_analysis = analyze_survivor(domain_id, overlay_result, tests)
            survivor_analysis["score"] = score
            survivor_analysis["verdict"] = verdict
            all_survivors.append(survivor_analysis)

    # Sort survivors by score
    all_survivors.sort(key=lambda x: x["score"], reverse=True)

    # Step 5: Print summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"ELIMINATED: {len(all_eliminations)}")
    for e in all_eliminations:
        print(f"  {e['domain_id']}: {e['domain_name']} (score={e['score']}, {e['elimination_reason']})")
    print()
    print(f"SURVIVORS: {len(all_survivors)}")
    for s in all_survivors:
        print(f"  {s['domain_id']}: {s['domain_name']} (score={s['score']}, {s['verdict']})")
    print()

    # Step 6: Synthesis
    synthesis = {
        "metadata": {
            "phase": "8",
            "title": "Domain Overlay Stress-Testing Synthesis",
            "timestamp": datetime.now().isoformat()
        },
        "summary": {
            "domains_tested": len(DOMAINS),
            "eliminated": len(all_eliminations),
            "survivors": len(all_survivors)
        },
        "rankings": [
            {"rank": i+1, "domain_id": s["domain_id"], "domain_name": s["domain_name"], "score": s["score"]}
            for i, s in enumerate(all_survivors)
        ],
        "interpretation": "",
        "what_survivors_share": [],
        "implications": [],
        "external_evidence_needed": []
    }

    # Generate interpretation
    if len(all_survivors) == 1:
        synthesis["interpretation"] = f"STRONG HYPOTHESIS: Only {all_survivors[0]['domain_name']} survives all tests."
    elif len(all_survivors) <= 3:
        names = [s["domain_name"] for s in all_survivors]
        synthesis["interpretation"] = f"DOMAIN FAMILY: {', '.join(names)} all survive. They likely share a common organizing principle."

        # What do survivors share?
        shared = []
        if any("Pharmaco" in s["domain_name"] or "Medical" in s["domain_name"] for s in all_survivors):
            shared.append("Medical/pharmaceutical knowledge organization")
        if any("Alchem" in s["domain_name"] for s in all_survivors):
            shared.append("Transformation/process encoding")
        if any("Astro" in s["domain_name"] for s in all_survivors):
            shared.append("Celestial influence systems")
        synthesis["what_survivors_share"] = shared
    else:
        synthesis["interpretation"] = "DOMAIN-GENERAL: Multiple domains survive, suggesting the system may be a general encoding framework."

    synthesis["implications"] = [
        f"Best fit: {all_survivors[0]['domain_name']} (score {all_survivors[0]['score']}/6.0)",
        "A/B split represents definition vs application workflow",
        "8 hubs represent major categorical divisions",
        "Abstraction is intentional and domain-appropriate"
    ]

    synthesis["external_evidence_needed"] = [
        "Identification of ANY single word/symbol meaning",
        "Match between entry structure and known medieval texts",
        "Correlation between hub categories and documented classification systems"
    ]

    # Save outputs
    print("Saving outputs...")

    with open("phase8_domain_overlays.json", "w") as f:
        json.dump(all_overlays, f, indent=2)
    print("  -> phase8_domain_overlays.json")

    with open("phase8_elimination_log.json", "w") as f:
        json.dump(all_eliminations, f, indent=2)
    print("  -> phase8_elimination_log.json")

    with open("phase8_survivors.json", "w") as f:
        json.dump(all_survivors, f, indent=2)
    print("  -> phase8_survivors.json")

    with open("phase8_synthesis.json", "w") as f:
        json.dump(synthesis, f, indent=2)
    print("  -> phase8_synthesis.json")

    print()
    print("=" * 70)
    print("PHASE 8 COMPLETE")
    print("=" * 70)

    return synthesis


if __name__ == "__main__":
    run_phase8()
