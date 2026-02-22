"""
ATOM_GLOSS_AUDIT: Spot-Check Report
====================================
Generates a human-readable report organized by atom family for
eyeball validation of atom glosses against compound evidence.

For each atom, shows:
  1. All compounds where that atom appears, sorted by frequency
  2. The manual gloss (if any) alongside the atom decomposition
  3. Whether the decomposition is consistent with the manual gloss

Output: phases/ATOM_GLOSS_AUDIT/results/spotcheck_report.txt
"""
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/ATOM_GLOSS_AUDIT/results")

# Expert-validated atom glosses from GLOSSING.md
ATOM_GLOSSES = {
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

# All known manual glosses (GLOSSING.md + dictionary, GLOSSING.md priority)
MANUAL_GLOSSES = {}


def load_all_glosses():
    """Merge glosses from dictionary and GLOSSING.md."""
    with open("data/middle_dictionary.json") as f:
        d = json.load(f)["middles"]

    for mid, info in d.items():
        g = info.get("gloss")
        if g:
            MANUAL_GLOSSES[mid] = g

    # GLOSSING.md overrides (expert-validated)
    glossing_md = {
        "k": "heat", "e": "cool", "h": "watch", "y": "end",
        "l": "frame", "r": "input", "o": "work", "d": "mark",
        "s": "sequence", "i": "iterate", "t": "transfer", "a": "yield",
        "c": "adjust", "m": "final", "p": "pause", "f": "flag",
        "n": "halt", "g": "complete",
        "edy": "batch", "eey": "extended cool", "ol": "continue",
        "dy": "close", "ke": "sustained heat", "ed": "discharge",
        "eo": "cool-open", "od": "collect", "ck": "direct heat",
        "ek": "precision", "ee": "extended cool", "eeo": "extended cool, work",
        "ok": "seal", "ep": "precision cool", "eol": "sustain output",
        "te": "rapid gather", "eeol": "overnight standing",
        "aii": "unseal", "kc": "intense heat-seal",
    }
    MANUAL_GLOSSES.update(glossing_md)


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


def decompose(middle):
    """Decompose a MIDDLE into atom glosses."""
    parts = []
    for ch in middle:
        g = ATOM_GLOSSES.get(ch, "?")
        parts.append(f"{ch}({g})")
    return " + ".join(parts)


def decompose_short(middle):
    """Short form: just the glosses joined."""
    parts = [ATOM_GLOSSES.get(ch, "?") for ch in middle]
    return "-".join(parts)


def main():
    load_all_glosses()
    counts = get_token_counts()

    lines = []
    def out(s=""):
        lines.append(s)
        print(s)

    out("=" * 78)
    out("ATOM GLOSS AUDIT: Spot-Check Report")
    out("=" * 78)
    out()
    out("Instructions: For each atom, review its compound appearances.")
    out("Mark each compound:  [OK] decomposition explains the gloss")
    out("                     [??] unclear, needs discussion")
    out("                     [NO] decomposition contradicts the gloss")
    out("If most compounds are [OK], the atom gloss is validated.")
    out("If several are [NO], the atom gloss may need revision.")
    out()

    # Build atom -> compounds index
    atom_compounds = defaultdict(list)
    all_middles = sorted(counts.keys(), key=lambda x: -counts[x])

    for mid in all_middles:
        if len(mid) < 2:
            continue
        for ch in set(mid):  # unique atoms in this middle
            if ch in ATOM_GLOSSES:
                atom_compounds[ch].append(mid)

    # Order atoms by standalone frequency (most important first)
    atom_order = sorted(ATOM_GLOSSES.keys(),
                        key=lambda a: -counts.get(a, 0))

    for atom in atom_order:
        gloss = ATOM_GLOSSES[atom]
        standalone = counts.get(atom, 0)
        compounds = atom_compounds.get(atom, [])

        # Sort compounds by frequency
        compounds = sorted(compounds, key=lambda m: -counts.get(m, 0))

        # Only show top compounds (cap at 25 for readability)
        show = compounds[:25]

        out("=" * 78)
        out(f"  ATOM: {atom} = \"{gloss}\"    (standalone: {standalone} tokens)")
        out(f"  Appears in {len(compounds)} compounds "
            f"({len([c for c in compounds if c in MANUAL_GLOSSES])} glossed)")
        out("-" * 78)
        out()
        out(f"  {'Middle':<12s}  {'Count':>5s}  {'Manual Gloss':<22s}  {'Atom Decomposition':<30s}")
        out(f"  {'------':<12s}  {'-----':>5s}  {'------------':<22s}  {'------------------':<30s}")

        for mid in show:
            c = counts.get(mid, 0)
            manual = MANUAL_GLOSSES.get(mid, "")
            decomp = decompose_short(mid)

            # Highlight this atom's position in the compound
            pos_str = ""
            positions = [i for i, ch in enumerate(mid) if ch == atom]
            if len(mid) <= 6:
                marked = ""
                for i, ch in enumerate(mid):
                    if ch == atom:
                        marked += ch.upper()
                    else:
                        marked += ch
                pos_str = f"  [{marked}]"

            manual_display = manual if manual else "---"
            out(f"  {mid:<12s}  {c:>5d}  {manual_display:<22s}  {decomp:<30s}{pos_str}")

        if len(compounds) > 25:
            out(f"  ... and {len(compounds) - 25} more compounds")

        out()

        # Quick summary for this atom
        glossed = [m for m in compounds if m in MANUAL_GLOSSES]
        if glossed:
            out(f"  VALIDATION SUMMARY for {atom}=\"{gloss}\":")
            out(f"    Glossed compounds: {len(glossed)}/{len(compounds)}")

            # Show glossed compounds grouped by whether the atom gloss
            # appears in the compound gloss (crude but useful signal)
            contains_atom = [m for m in glossed
                             if gloss.lower() in MANUAL_GLOSSES[m].lower()]
            doesnt_contain = [m for m in glossed
                              if gloss.lower() not in MANUAL_GLOSSES[m].lower()]

            if contains_atom:
                out(f"    Contains \"{gloss}\": "
                    + ", ".join(f"{m}={MANUAL_GLOSSES[m]}" for m in contains_atom[:8]))
            if doesnt_contain:
                out(f"    Does NOT contain \"{gloss}\": "
                    + ", ".join(f"{m}={MANUAL_GLOSSES[m]}" for m in doesnt_contain[:8]))

            if len(contains_atom) >= len(glossed) * 0.5:
                out(f"    --> LIKELY CORRECT (>={len(contains_atom)}/{len(glossed)} "
                    f"compounds contain the atom gloss)")
            else:
                out(f"    --> NEEDS REVIEW (only {len(contains_atom)}/{len(glossed)} "
                    f"compounds contain the atom gloss)")
        else:
            out(f"  No glossed compounds to validate against.")

        out()

    # ================================================================
    # FINAL SUMMARY
    # ================================================================
    out("=" * 78)
    out("OVERALL ATOM CONFIDENCE")
    out("=" * 78)
    out()
    out(f"  {'Atom':<6s}  {'Gloss':<12s}  {'Standalone':>10s}  {'Compounds':>10s}  "
        f"{'Glossed':>8s}  {'Contains':>8s}  {'Signal'}")
    out(f"  {'----':<6s}  {'-----':<12s}  {'----------':>10s}  {'---------':>10s}  "
        f"{'-------':>8s}  {'--------':>8s}  {'------'}")

    for atom in atom_order:
        gloss = ATOM_GLOSSES[atom]
        standalone = counts.get(atom, 0)
        compounds = atom_compounds.get(atom, [])
        glossed = [m for m in compounds if m in MANUAL_GLOSSES]
        contains = [m for m in glossed
                    if gloss.lower() in MANUAL_GLOSSES[m].lower()]

        if len(glossed) >= 3:
            rate = len(contains) / len(glossed)
            if rate >= 0.5:
                signal = "STRONG"
            elif rate >= 0.25:
                signal = "MODERATE"
            else:
                signal = "WEAK"
        elif len(glossed) >= 1:
            signal = "LIMITED"
        else:
            signal = "NONE"

        out(f"  {atom:<6s}  {gloss:<12s}  {standalone:>10d}  {len(compounds):>10d}  "
            f"{len(glossed):>8d}  {len(contains):>8d}  {signal}")

    out()
    out("Signal key:")
    out("  STRONG:   >=50% of glossed compounds contain the atom gloss word")
    out("  MODERATE: 25-50% contain it")
    out("  WEAK:     <25% contain it (atom gloss may be wrong or too abstract)")
    out("  LIMITED:  <3 glossed compounds (insufficient evidence)")
    out("  NONE:     no glossed compounds")
    out()
    out("NOTE: 'Contains' is a crude keyword match. An atom gloss can be")
    out("correct even if the compound gloss doesn't literally contain the word.")
    out("E.g., e='cool' is correct even though ek='precision' doesn't contain")
    out("'cool' -- precision IS a type of careful cooling. Use human judgment.")

    # Save report
    report_path = RESULTS_DIR / "spotcheck_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
