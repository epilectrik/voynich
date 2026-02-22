"""
ATOM_GLOSS_AUDIT: Cross-Check Atom Glosses Against Compound Evidence
=====================================================================
Phase 424 — Uses the 91 manually glossed compound MIDDLEs as ground
truth to validate and correct the 18 atom-level glosses.

Method:
  1. Load GLOSSING.md expert-validated glosses as authority
  2. Load middle_dictionary.json for dictionary glosses
  3. For each compound MIDDLE with a manual gloss, decompose into atoms
  4. Show atom-gloss composition alongside manual gloss
  5. Score consistency: does the atom decomposition explain the compound?
  6. Flag discrepancies between GLOSSING.md and dictionary
  7. Generate autogloss candidates for all unglossed MIDDLEs

Key question: can we lock a high-confidence atom gloss set and use it
to auto-generate compound glosses?

Provenance: C1190 (additive composition), C1193 (compositional duality)
"""
import json
import sys
import re
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/ATOM_GLOSS_AUDIT/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# GLOSS SOURCES
# ============================================================

# Expert-validated atom glosses from GLOSSING.md (the authority)
GLOSSING_MD_ATOMS = {
    "k": "heat",
    "e": "cool",
    "h": "watch",
    "y": "end",
    "l": "frame",
    "r": "input",
    "o": "work",
    "d": "mark",
    "s": "sequence",
    "i": "iterate",
    "t": "transfer",
    "a": "yield",
    "c": "adjust",
    "m": "final",
    "p": "pause",
    "f": "flag",
    "n": "halt",
    "g": "complete",
}

# Expert-validated compound glosses from GLOSSING.md
GLOSSING_MD_COMPOUNDS = {
    "edy": "batch",
    "eey": "extended cool",
    "ol": "continue",
    "dy": "close",
    "ke": "sustained heat",
    "ed": "discharge",
    "eo": "cool-open",
    "od": "collect",
    "ck": "direct heat",
    "ek": "precision",
    "ee": "extended cool",
    "eeo": "extended cool, work",
    "ok": "seal",
    "ep": "precision cool",
    "eol": "sustain output",
    "te": "rapid gather",
    "eeol": "overnight standing",
    "aii": "unseal",
    "kc": "intense heat-seal",
}


def load_dictionary_glosses():
    """Load glosses from middle_dictionary.json."""
    with open("data/middle_dictionary.json") as f:
        d = json.load(f)["middles"]

    atom_glosses = {}
    compound_glosses = {}
    for mid, info in d.items():
        gloss = info.get("gloss")
        if gloss:
            if len(mid) == 1:
                atom_glosses[mid] = gloss
            else:
                compound_glosses[mid] = gloss

    return atom_glosses, compound_glosses


def get_token_counts():
    """Get per-MIDDLE token counts from transcript."""
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


def main():
    print("=" * 72)
    print("ATOM GLOSS AUDIT: Cross-Check Against Compound Evidence")
    print("Phase 424")
    print("=" * 72)
    print()

    # Load data
    dict_atoms, dict_compounds = load_dictionary_glosses()
    token_counts = get_token_counts()

    # ============================================================
    # STEP 1: Dictionary vs GLOSSING.md discrepancies
    # ============================================================
    print("=" * 72)
    print("STEP 1: Atom Gloss Discrepancies (Dictionary vs GLOSSING.md)")
    print("=" * 72)
    print()

    print(f"  {'Atom':>6s}  {'Dictionary':>15s}  {'GLOSSING.md':>15s}  {'Match':>7s}")
    print(f"  {'----':>6s}  {'----------':>15s}  {'-----------':>15s}  {'-----':>7s}")

    discrepancies = {}
    for atom in sorted(GLOSSING_MD_ATOMS.keys()):
        gmd = GLOSSING_MD_ATOMS[atom]
        dct = dict_atoms.get(atom, "---")
        match = "YES" if gmd == dct else "NO" if dct != "---" else "MISSING"
        if match == "NO":
            discrepancies[atom] = {"glossing_md": gmd, "dictionary": dct}
        print(f"  {atom:>6s}  {dct:>15s}  {gmd:>15s}  {match:>7s}")

    print()
    if discrepancies:
        print(f"  DISCREPANCIES FOUND: {len(discrepancies)}")
        for atom, info in discrepancies.items():
            print(f"    {atom}: dictionary='{info['dictionary']}' vs GLOSSING.md='{info['glossing_md']}'")
    else:
        print(f"  NO DISCREPANCIES")
    print()

    # ============================================================
    # STEP 2: Cross-check compounds against atom decomposition
    # ============================================================
    print("=" * 72)
    print("STEP 2: Compound Gloss Cross-Check")
    print("       Does atom decomposition explain the compound gloss?")
    print("=" * 72)
    print()

    # Merge all known compound glosses (GLOSSING.md takes priority)
    all_compound_glosses = dict(dict_compounds)
    all_compound_glosses.update(GLOSSING_MD_COMPOUNDS)

    # Use GLOSSING.md atoms as authority
    atom_glosses = dict(GLOSSING_MD_ATOMS)

    print(f"  {'Middle':>10s}  {'Count':>6s}  {'Compound Gloss':>20s}  {'Atom Decomposition':>30s}  {'Fit'}")
    print(f"  {'------':>10s}  {'-----':>6s}  {'--------------':>20s}  {'------------------':>30s}  {'---'}")

    consistency_scores = defaultdict(list)  # atom -> list of (compound, fit_score)
    crosscheck_results = []

    for mid in sorted(all_compound_glosses.keys(), key=lambda x: -token_counts.get(x, 0)):
        compound_gloss = all_compound_glosses[mid]
        count = token_counts.get(mid, 0)

        # Decompose into atoms
        atoms = list(mid)
        atom_parts = []
        all_known = True
        for a in atoms:
            g = atom_glosses.get(a)
            if g:
                atom_parts.append(f"{a}={g}")
            else:
                atom_parts.append(f"{a}=?")
                all_known = False

        decomp = " + ".join(atom_parts)

        # Simple fit assessment
        # We can't do semantic comparison programmatically, so we flag
        # known good patterns and known problems
        fit = assess_fit(mid, compound_gloss, atoms, atom_glosses)

        print(f"  {mid:>10s}  {count:>6d}  {compound_gloss:>20s}  {decomp:>30s}  {fit}")

        for a in atoms:
            if a in atom_glosses:
                consistency_scores[a].append((mid, compound_gloss, fit))

        crosscheck_results.append({
            "middle": mid,
            "count": count,
            "compound_gloss": compound_gloss,
            "decomposition": decomp,
            "atoms": atoms,
            "fit": fit,
        })

    print()

    # ============================================================
    # STEP 3: Per-atom consistency report
    # ============================================================
    print("=" * 72)
    print("STEP 3: Per-Atom Consistency Report")
    print("       How consistently does each atom's gloss explain compounds?")
    print("=" * 72)
    print()

    atom_report = {}
    for atom in sorted(atom_glosses.keys()):
        gloss = atom_glosses[atom]
        appearances = consistency_scores.get(atom, [])
        n_total = len(appearances)
        n_good = sum(1 for _, _, f in appearances if f in ("GOOD", "STRONG"))
        n_ok = sum(1 for _, _, f in appearances if f == "PLAUSIBLE")
        n_bad = sum(1 for _, _, f in appearances if f in ("WEAK", "CONFLICT"))
        n_unk = sum(1 for _, _, f in appearances if f == "UNKNOWN")

        if n_total == 0:
            rate = 0
        else:
            rate = (n_good + n_ok) / n_total

        standalone_count = token_counts.get(atom, 0)

        status = "LOCKED" if rate >= 0.7 and n_total >= 3 else \
                 "TENTATIVE" if rate >= 0.5 else \
                 "REVIEW" if n_total >= 2 else \
                 "INSUFFICIENT"

        print(f"  {atom} = {gloss:>12s}  "
              f"standalone={standalone_count:>5d}  "
              f"compounds={n_total:>3d}  "
              f"good={n_good}  ok={n_ok}  bad={n_bad}  unk={n_unk}  "
              f"rate={rate:.0%}  "
              f"STATUS: {status}")

        if n_bad > 0:
            bad_compounds = [(m, g) for m, g, f in appearances
                             if f in ("WEAK", "CONFLICT")]
            for m, g in bad_compounds:
                print(f"       CONFLICT: {m} = '{g}'")

        atom_report[atom] = {
            "gloss": gloss,
            "standalone_count": standalone_count,
            "n_compounds": n_total,
            "n_good": n_good,
            "n_ok": n_ok,
            "n_bad": n_bad,
            "n_unknown": n_unk,
            "consistency_rate": round(rate, 3),
            "status": status,
        }

    print()

    n_locked = sum(1 for v in atom_report.values() if v["status"] == "LOCKED")
    n_tentative = sum(1 for v in atom_report.values() if v["status"] == "TENTATIVE")
    n_review = sum(1 for v in atom_report.values() if v["status"] == "REVIEW")
    n_insuf = sum(1 for v in atom_report.values() if v["status"] == "INSUFFICIENT")

    print(f"  SUMMARY: {n_locked} LOCKED, {n_tentative} TENTATIVE, "
          f"{n_review} REVIEW, {n_insuf} INSUFFICIENT")
    print()

    # ============================================================
    # STEP 4: Autogloss candidates for unglossed MIDDLEs
    # ============================================================
    print("=" * 72)
    print("STEP 4: Autogloss Candidates (Top 50 unglossed by frequency)")
    print("=" * 72)
    print()

    # Get all MIDDLEs from transcript
    all_middles = sorted(token_counts.keys(), key=lambda x: -token_counts[x])

    unglossed = [m for m in all_middles
                 if m not in all_compound_glosses and m not in atom_glosses
                 and len(m) >= 2]

    print(f"  Total MIDDLEs: {len(all_middles)}")
    print(f"  Glossed (atoms + compounds): {len(atom_glosses) + len(all_compound_glosses)}")
    print(f"  Unglossed compounds: {len(unglossed)}")
    print()

    locked_atoms = {a for a, v in atom_report.items() if v["status"] == "LOCKED"}
    tentative_atoms = {a for a, v in atom_report.items() if v["status"] == "TENTATIVE"}

    print(f"  {'Middle':>12s}  {'Count':>6s}  {'Autogloss':>30s}  {'Confidence':>12s}")
    print(f"  {'------':>12s}  {'-----':>6s}  {'---------':>30s}  {'----------':>12s}")

    autogloss_results = []
    for mid in unglossed[:50]:
        atoms = list(mid)
        parts = []
        all_locked = True
        all_known = True
        for a in atoms:
            g = atom_glosses.get(a)
            if g:
                parts.append(g)
                if a not in locked_atoms:
                    all_locked = False
            else:
                parts.append("?")
                all_known = False
                all_locked = False

        if all_known:
            autogloss = "-".join(parts)
            if all_locked:
                confidence = "HIGH"
            elif all(a in locked_atoms or a in tentative_atoms for a in atoms):
                confidence = "MEDIUM"
            else:
                confidence = "LOW"
        else:
            autogloss = "-".join(parts)
            confidence = "INCOMPLETE"

        count = token_counts[mid]
        print(f"  {mid:>12s}  {count:>6d}  {autogloss:>30s}  {confidence:>12s}")

        autogloss_results.append({
            "middle": mid,
            "count": count,
            "autogloss": autogloss,
            "confidence": confidence,
            "atoms": atoms,
        })

    print()

    # ============================================================
    # STEP 5: Summary and recommendations
    # ============================================================
    print("=" * 72)
    print("STEP 5: Summary and Recommendations")
    print("=" * 72)
    print()

    n_high = sum(1 for r in autogloss_results if r["confidence"] == "HIGH")
    n_med = sum(1 for r in autogloss_results if r["confidence"] == "MEDIUM")
    n_low = sum(1 for r in autogloss_results if r["confidence"] == "LOW")

    print(f"  Autogloss coverage (top 50 unglossed):")
    print(f"    HIGH confidence:   {n_high}")
    print(f"    MEDIUM confidence: {n_med}")
    print(f"    LOW confidence:    {n_low}")
    print()

    if discrepancies:
        print(f"  RECOMMENDED DICTIONARY CORRECTIONS:")
        for atom, info in discrepancies.items():
            print(f"    {atom}: '{info['dictionary']}' -> '{info['glossing_md']}' "
                  f"(per GLOSSING.md expert validation)")
    print()

    # Save results
    results = {
        "phase": "ATOM_GLOSS_AUDIT",
        "phase_number": 424,
        "discrepancies": discrepancies,
        "atom_report": atom_report,
        "crosscheck": crosscheck_results,
        "autogloss_top50": autogloss_results,
    }

    out_path = RESULTS_DIR / "atom_gloss_audit.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Results saved to: {out_path}")


def assess_fit(middle, compound_gloss, atoms, atom_glosses):
    """Assess whether atom decomposition explains the compound gloss.

    Uses pattern matching against known compositional patterns.
    Returns: STRONG, GOOD, PLAUSIBLE, WEAK, CONFLICT, UNKNOWN
    """
    compound_gloss_lower = compound_gloss.lower()
    atom_parts = [atom_glosses.get(a, "") for a in atoms]

    # Check if any atom gloss appears directly in compound gloss
    direct_matches = sum(1 for p in atom_parts if p and p in compound_gloss_lower)

    # Check known compositional patterns
    # Pattern: double letter = "extended X" (ee = extended cool, etc.)
    if len(atoms) >= 2 and atoms[0] == atoms[1]:
        first_gloss = atom_glosses.get(atoms[0], "")
        if "extended" in compound_gloss_lower and first_gloss in compound_gloss_lower:
            return "STRONG"

    # Pattern: X + y = "X done/complete"
    if atoms[-1] == "y":
        return "GOOD" if direct_matches >= 1 else "PLAUSIBLE"

    # Pattern: e + X = cooling variant (eo, ek, ep, ed, eol)
    if atoms[0] == "e":
        if "cool" in compound_gloss_lower or "precision" in compound_gloss_lower:
            return "STRONG"
        if "discharge" in compound_gloss_lower or "output" in compound_gloss_lower:
            return "GOOD"

    # Pattern: k + X = heating variant (ke, kc)
    if atoms[0] == "k":
        if "heat" in compound_gloss_lower:
            return "STRONG"

    # Pattern: X + k = X-type heating (ck = direct heat, ek = precision)
    if atoms[-1] == "k":
        if "heat" in compound_gloss_lower:
            return "GOOD"

    # Check for direct word matches
    if direct_matches >= 2:
        return "STRONG"
    elif direct_matches >= 1:
        return "GOOD"

    # Known special cases
    # edy = "batch" — e(cool) + d(mark) + y(end) -> doesn't obviously map
    if middle == "edy" and compound_gloss_lower == "batch":
        return "WEAK"

    # te = "rapid gather" — t(transfer) + e(cool) -> transfer-cool?
    if middle == "te" and "gather" in compound_gloss_lower:
        return "PLAUSIBLE"

    # aii = "unseal" — a(yield) + i(iterate) + i(iterate) -> yield-iterate-iterate?
    if middle == "aii" and "unseal" in compound_gloss_lower:
        return "WEAK"

    # od = "collect" — o(work) + d(mark) -> work-mark = collect? plausible
    if middle == "od":
        return "PLAUSIBLE"

    # ol = "continue" — o(work) + l(frame) -> work-frame = continue? plausible
    if middle == "ol":
        return "PLAUSIBLE"

    # For everything else, check partial semantic compatibility
    if len(atom_parts) >= 2 and all(p for p in atom_parts):
        return "UNKNOWN"

    return "UNKNOWN"


if __name__ == "__main__":
    main()
