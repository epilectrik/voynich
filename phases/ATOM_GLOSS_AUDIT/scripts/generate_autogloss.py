"""
ATOM_GLOSS_AUDIT: Autogloss Generator
=======================================
Phase 424 — Generates auto-composed glosses for all unglossed compound
MIDDLEs using validated atom glosses.

Steps:
  1. Fix 5 dictionary discrepancies (i, l, o, r, s) to match GLOSSING.md
  2. Assign confidence tiers to atom glosses based on compound evidence
  3. Auto-generate compound glosses from atom decomposition
  4. Output updated dictionary + human-readable review file

Atom confidence tiers (from spot-check analysis):
  LOCKED:    Strong compound evidence, internally consistent
  SOLID:     Good evidence, correct but label might be refined
  PLAUSIBLE: Thin evidence, nothing contradicts
  WEAK:      Correct direction but very generic/abstract

Provenance: C1190 (additive composition), C777 (FL state index)
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/ATOM_GLOSS_AUDIT/results")

# ============================================================
# VALIDATED ATOM GLOSSES (from spot-check analysis)
# ============================================================

ATOM_GLOSSES = {
    # LOCKED: strong compound evidence
    "k": {"gloss": "heat", "confidence": "LOCKED",
           "evidence": "ke=sustained heat, ck=direct heat, ek=precision, kc=intense heat-seal; order-sensitive; 2083 standalone"},
    "e": {"gloss": "cool", "confidence": "LOCKED",
           "evidence": "ee=extended cool, eey=extended cool, eo=cool-open, ep=precision cool; stability anchor C105; 867 standalone"},
    "h": {"gloss": "watch", "confidence": "LOCKED",
           "evidence": "monitoring kernel C1154; ch=active test, sh=passive monitor (C929); domain-dependent; 48 standalone"},
    "y": {"gloss": "end", "confidence": "LOCKED",
           "evidence": "dy=close, ey=set, ly=end, ry=finish, hy=confirm; every -y compound is termination; 513 standalone"},
    "i": {"gloss": "iterate", "confidence": "LOCKED",
           "evidence": "ii=repeat, iin=iterate, in=link, ai=open, ain=intake, aiin=settle; i+n family perfectly consistent; FL pos 0.345"},
    "n": {"gloss": "halt", "confidence": "LOCKED",
           "evidence": "in=link(iterate+halt), iin=iterate, ain=intake, aiin=settle, an=bind; terminates iteration; 7 standalone"},
    "a": {"gloss": "yield", "confidence": "LOCKED",
           "evidence": "ai=open, ar=release, al=gather, am=finalize, ain=intake; consistent open/give/release sense; 64 standalone"},
    "m": {"gloss": "final", "confidence": "LOCKED",
           "evidence": "am=finalize, om=work(terminal); FL pos 0.94 = FINAL stage; 76 standalone"},

    # SOLID: correct, label might be refined
    "d": {"gloss": "mark", "confidence": "SOLID",
           "evidence": "ed=discharge, od=collect, ked=release, keed=vent, eod=stand; all output/product operations; could be 'product'"},
    "t": {"gloss": "transfer", "confidence": "SOLID",
           "evidence": "ct=control, te=rapid gather, et=path, ot=route, ect=regulate; abstract but compounds fit 'move/convey'"},

    # PLAUSIBLE: thin evidence, nothing contradicts
    "c": {"gloss": "adjust", "confidence": "PLAUSIBLE",
           "evidence": "ck=direct heat, kc=intense heat-seal, ct=control, ect=regulate; almost always in ch compound; 5 standalone"},
    "p": {"gloss": "pause", "confidence": "PLAUSIBLE",
           "evidence": "pch=pause, op=start, ep=precision cool; 47 standalone"},
    "f": {"gloss": "flag", "confidence": "PLAUSIBLE",
           "evidence": "fch=note; 17 standalone; too few compounds to validate"},
    "s": {"gloss": "sequence", "confidence": "PLAUSIBLE",
           "evidence": "ksh=scan, lsh=verify, sh=verify; mostly sh compounds; FL-excluded primitive"},

    # WEAK: correct direction but generic
    "o": {"gloss": "work", "confidence": "WEAK",
           "evidence": "ol=continue, or=portion, od=collect, opch=operate; very generic; FL pos 0.751; 388 standalone"},
    "l": {"gloss": "frame", "confidence": "WEAK",
           "evidence": "ol=continue, al=gather, lk=frame, ly=end, lo=open; tenuous connections; FL pos 0.618; 855 standalone"},
    "r": {"gloss": "input", "confidence": "WEAK",
           "evidence": "ar=release, or=portion, ry=finish; only 3 glossed compounds; FL pos 0.507; 749 standalone"},

    # SPECIAL
    "g": {"gloss": "complete", "confidence": "PLAUSIBLE",
           "evidence": "87% line-end, ~1/folio; 8 standalone; only 3 compounds (all hapax)"},
    "x": {"gloss": "diagram", "confidence": "PLAUSIBLE",
           "evidence": "C764; AZC-related; 0 standalone in B text MIDDLEs"},
    "q": {"gloss": None, "confidence": "SPECIAL",
           "evidence": "qo-form prefix variant; not a true MIDDLE atom"},
}


def get_token_counts():
    tx = Transcript()
    morph = Morphology()
    counts = Counter()
    for token in tx.currier_b():
        if token.is_label or token.is_uncertain or not token.word.strip():
            continue
        m = morph.extract(token.word)
        if m.middle and not m.is_empty_middle:
            counts[m.middle] += 1
    return counts


def compose_autogloss(middle):
    """Generate auto-composed gloss from atom decomposition.
    Returns (gloss_string, confidence, atoms_used)."""
    atoms = list(middle)
    parts = []
    min_confidence = "LOCKED"
    confidence_order = ["LOCKED", "SOLID", "PLAUSIBLE", "WEAK", "SPECIAL"]

    for a in atoms:
        info = ATOM_GLOSSES.get(a)
        if info is None or info["gloss"] is None:
            return None, "INCOMPLETE", atoms
        parts.append(info["gloss"])
        # Track minimum confidence
        a_conf = info["confidence"]
        if confidence_order.index(a_conf) > confidence_order.index(min_confidence):
            min_confidence = a_conf

    gloss = "-".join(parts)
    return gloss, min_confidence, atoms


def main():
    print("=" * 72)
    print("ATOM GLOSS AUDIT: Autogloss Generator")
    print("Phase 424")
    print("=" * 72)
    print()

    counts = get_token_counts()

    # Load current dictionary
    with open("data/middle_dictionary.json") as f:
        dictionary = json.load(f)

    middles = dictionary["middles"]

    # ============================================================
    # STEP 1: Fix atom glosses in dictionary
    # ============================================================
    print("STEP 1: Fixing atom glosses to match GLOSSING.md")
    print()

    fixes = {
        "i": ("early", "iterate"),
        "l": ("late", "frame"),
        "o": ("near", "work"),
        "r": ("mid", "input"),
        "s": ("break", "sequence"),
    }

    for atom, (old, new) in fixes.items():
        if atom in middles:
            current = middles[atom].get("gloss")
            if current == old:
                middles[atom]["gloss"] = new
                # Preserve FL state info in notes
                if middles[atom].get("notes"):
                    middles[atom]["notes"].append(
                        f"Gloss updated: '{old}' -> '{new}' (GLOSSING.md expert validation, Phase 424). "
                        f"FL state position preserved as structural observation per C777."
                    )
                print(f"  FIXED: {atom} '{old}' -> '{new}'")
            else:
                print(f"  SKIP: {atom} already '{current}' (expected '{old}')")

    # Add confidence tier to all atom entries
    for atom, info in ATOM_GLOSSES.items():
        if atom in middles:
            middles[atom]["gloss_confidence"] = info["confidence"]
            middles[atom]["gloss_evidence"] = info["evidence"]

    print()

    # ============================================================
    # STEP 2: Generate autoglosses for unglossed compounds
    # ============================================================
    print("STEP 2: Generating autoglosses")
    print()

    all_middles = sorted(counts.keys(), key=lambda x: -counts[x])

    autoglossed = 0
    already_glossed = 0
    incomplete = 0
    single_char = 0

    review_lines = []
    review_lines.append("AUTOGLOSS REVIEW FILE")
    review_lines.append("=" * 72)
    review_lines.append("Review these auto-generated glosses. Mark any that seem wrong.")
    review_lines.append("Glosses are composed from atom root concepts joined by '-'.")
    review_lines.append("")
    review_lines.append(f"{'Middle':<14s}  {'Count':>5s}  {'Confidence':<10s}  {'Autogloss':<35s}  {'Existing':<25s}")
    review_lines.append(f"{'------':<14s}  {'-----':>5s}  {'----------':<10s}  {'---------':<35s}  {'--------':<25s}")

    confidence_counts = Counter()

    for mid in all_middles:
        count = counts[mid]

        if len(mid) == 1:
            single_char += 1
            continue

        existing = middles.get(mid, {}).get("gloss")

        autogloss, confidence, atoms = compose_autogloss(mid)

        if autogloss is None:
            incomplete += 1
            continue

        confidence_counts[confidence] += 1

        if existing:
            already_glossed += 1
            # Still show for cross-checking
            review_lines.append(
                f"{mid:<14s}  {count:>5d}  {confidence:<10s}  {autogloss:<35s}  {existing:<25s}")
        else:
            autoglossed += 1
            # Write autogloss to dictionary
            if mid not in middles:
                middles[mid] = {
                    "kernel": None,
                    "regime": None,
                    "gloss": None,
                    "token_count": count,
                    "folio_count": None,
                    "example_tokens": [],
                    "notes": [],
                }
            middles[mid]["autogloss"] = autogloss
            middles[mid]["autogloss_confidence"] = confidence
            middles[mid]["autogloss_atoms"] = "".join(atoms)

            review_lines.append(
                f"{mid:<14s}  {count:>5d}  {confidence:<10s}  {autogloss:<35s}  {'---':<25s}")

    print(f"  Single-char atoms: {single_char}")
    print(f"  Already glossed:   {already_glossed}")
    print(f"  Auto-glossed:      {autoglossed}")
    print(f"  Incomplete (q):    {incomplete}")
    print()
    print(f"  Confidence distribution:")
    for conf in ["LOCKED", "SOLID", "PLAUSIBLE", "WEAK"]:
        print(f"    {conf}: {confidence_counts[conf]}")
    print()

    # ============================================================
    # STEP 3: Update dictionary metadata
    # ============================================================
    dictionary["meta"]["version"] = "3.0"
    dictionary["meta"]["atom_gloss_audit"] = (
        "Phase 424: Fixed 5 atom glosses to GLOSSING.md expert-validated values "
        "(i:early->iterate, l:late->frame, o:near->work, r:mid->input, s:break->sequence). "
        "Added confidence tiers. Added autogloss field for compound MIDDLEs."
    )
    dictionary["meta"]["autogloss_count"] = autoglossed
    dictionary["meta"]["glossed"] = already_glossed + single_char  # manual glosses

    # Save updated dictionary
    dict_path = Path("data/middle_dictionary.json")
    with open(dict_path, "w") as f:
        json.dump(dictionary, f, indent=2)
    print(f"  Updated dictionary saved to: {dict_path}")

    # Save review file
    review_path = RESULTS_DIR / "autogloss_review.txt"
    with open(review_path, "w", encoding="utf-8") as f:
        f.write("\n".join(review_lines))
    print(f"  Review file saved to: {review_path}")

    # Save summary stats
    summary = {
        "phase": "ATOM_GLOSS_AUDIT",
        "phase_number": 424,
        "atom_fixes": {k: {"old": v[0], "new": v[1]} for k, v in fixes.items()},
        "atom_confidence": {a: {"gloss": v["gloss"], "confidence": v["confidence"]}
                           for a, v in ATOM_GLOSSES.items()},
        "autogloss_count": autoglossed,
        "already_glossed": already_glossed,
        "incomplete": incomplete,
        "confidence_distribution": dict(confidence_counts),
    }
    summary_path = RESULTS_DIR / "autogloss_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Summary saved to: {summary_path}")

    print()
    print("=" * 72)
    print("DONE. Review autogloss_review.txt for spot-checking.")
    print("=" * 72)


if __name__ == "__main__":
    main()
