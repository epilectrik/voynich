"""
COMPOUND DECOMPOSITION ANALYSIS (Tier 4)
=========================================
Tests whether multi-character MIDDLEs decompose compositionally into
single-character atoms, where each atom has ONE consistent meaning
across all its appearances.

Methodology:
  1. Define atomic alphabet (single-char MIDDLEs with glosses)
  2. For each multi-char MIDDLE with a gloss, decompose into atoms
  3. Present atom glosses alongside compound gloss for human evaluation
  4. Score each atom's consistency across all its compound appearances
  5. Identify "crossword constraints" — atoms whose definition is
     forced by multiple independent compounds

The key leverage: each letter must work independently AND in every
compound it appears in. One meaning per letter, tested across all
contexts simultaneously.
"""
import json
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path("phases/COMPOUND_DECOMPOSITION/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_middles():
    with open("data/middle_dictionary.json") as f:
        d = json.load(f)
    return d["middles"]


def get_atoms(middles):
    """Extract single-character MIDDLEs with glosses as the atomic alphabet."""
    atoms = {}
    for name, info in middles.items():
        if len(name) == 1 and info.get("gloss"):
            atoms[name] = {
                "gloss": info["gloss"],
                "kernel": info.get("kernel"),
                "tokens": info.get("token_count", 0),
            }
    return atoms


def decompose(middle, atoms):
    """Decompose a multi-char MIDDLE into single-char atoms.
    Returns list of (char, gloss) tuples, or None if any char is unknown."""
    result = []
    for ch in middle:
        if ch in atoms:
            result.append((ch, atoms[ch]["gloss"]))
        else:
            result.append((ch, None))
    return result


def main():
    middles = load_middles()
    atoms = get_atoms(middles)

    # Also add proposed atoms that don't have glosses yet but we're testing
    # These are the German abbreviation candidates
    proposed = {
        "o": "vessel",   # Ofen (furnace/vessel)
        "c": "adjust",   # current dict gloss
        "n": "halt",     # current dict gloss
    }

    print("=" * 72)
    print("COMPOUND DECOMPOSITION ANALYSIS")
    print("=" * 72)
    print()

    # --- Section 1: Atomic Alphabet ---
    print("ATOMIC ALPHABET (single-character MIDDLEs)")
    print("-" * 50)
    print(f"  {'char':4s} {'gloss':14s} {'kernel':6s} {'tokens':>6s}  confidence")
    print(f"  {'----':4s} {'-----':14s} {'------':6s} {'------':>6s}  ----------")
    confidence_map = {
        "k": "TIER 2 (kernel)",
        "e": "TIER 2 (kernel)",
        "h": "TIER 2 (kernel)",
        "d": "moderate",
        "t": "moderate",
        "s": "moderate",
        "l": "moderate",
        "r": "moderate",
        "y": "moderate",
        "m": "moderate",
        "a": "weak",
        "o": "weak",
        "c": "weak",
        "i": "weak",
        "p": "weak",
        "f": "very weak",
        "n": "very weak",
        "g": "very weak",
        "x": "diagram-only",
    }
    for ch in sorted(atoms.keys(), key=lambda x: atoms[x]["tokens"], reverse=True):
        info = atoms[ch]
        conf = confidence_map.get(ch, "?")
        print(f"  {ch:4s} {info['gloss']:14s} {str(info['kernel']):>6s} {info['tokens']:6d}  {conf}")
    print()

    # --- Section 2: Compound Decomposition Table ---
    # Get all multi-char MIDDLEs with glosses, sorted by token count
    compounds = []
    for name, info in middles.items():
        if len(name) > 1 and info.get("gloss") and info.get("token_count", 0) >= 5:
            compounds.append((info["token_count"], name, info["gloss"],
                              info.get("kernel")))
    compounds.sort(reverse=True)

    print("COMPOUND DECOMPOSITION TABLE")
    print("(MIDDLEs with gloss, >= 5 tokens)")
    print("-" * 72)
    print(f"  {'MIDDLE':10s} {'tokens':>5s} {'gloss':14s} {'decomposition':30s} {'fit':5s}")
    print(f"  {'------':10s} {'-----':>5s} {'-----':14s} {'-------------':30s} {'---':5s}")

    # Track per-atom compound appearances for crossword analysis
    atom_contexts = defaultdict(list)
    fit_results = []

    for tc, name, gloss, kernel in compounds:
        parts = decompose(name, atoms)

        # Build decomposition string
        decomp_parts = []
        all_known = True
        for ch, atom_gloss in parts:
            if atom_gloss:
                decomp_parts.append(f"{ch}({atom_gloss})")
                atom_contexts[ch].append((name, gloss))
            elif ch in proposed:
                decomp_parts.append(f"{ch}({proposed[ch]}*)")
                atom_contexts[ch].append((name, gloss))
            else:
                decomp_parts.append(f"{ch}(?)")
                all_known = False
                atom_contexts[ch].append((name, gloss))

        decomp_str = " + ".join(decomp_parts)

        # Truncate for display
        if len(decomp_str) > 45:
            decomp_str = decomp_str[:42] + "..."

        print(f"  {name:10s} {tc:5d} {gloss:14s} {decomp_str}")
        fit_results.append({
            "middle": name, "tokens": tc, "gloss": gloss,
            "kernel": kernel, "decomposition": [(c, g) for c, g in parts],
            "all_atoms_known": all_known
        })

    print()

    # --- Section 3: Crossword Constraints ---
    print("CROSSWORD CONSTRAINTS (per-atom compound contexts)")
    print("Each atom must have ONE meaning that works in ALL these compounds.")
    print("-" * 72)

    for ch in sorted(atom_contexts.keys(),
                     key=lambda x: len(atom_contexts[x]), reverse=True):
        contexts = atom_contexts[ch]
        atom_gloss = atoms.get(ch, {}).get("gloss", proposed.get(ch, "???"))
        n = len(contexts)
        if n < 2:
            continue

        print(f"\n  {ch} = \"{atom_gloss}\"  ({n} compound appearances)")

        # Group by first occurrence
        seen = set()
        for mid_name, mid_gloss in contexts:
            if mid_name not in seen:
                seen.add(mid_name)
                # Show the compound and what this atom needs to contribute
                other_atoms = [c for c in mid_name if c != ch]
                other_glosses = [atoms.get(c, {}).get("gloss",
                                 proposed.get(c, "?")) for c in other_atoms]
                others_str = " + ".join(f"{c}({g})" for c, g in
                                        zip(other_atoms, other_glosses))
                print(f"    {mid_name:12s} = \"{mid_gloss:14s}\"  "
                      f"({ch}={atom_gloss} + {others_str})")

    print()

    # --- Section 4: Conflict Detection ---
    print("CONFLICT ANALYSIS")
    print("Compounds where atom composition seems inconsistent with gloss")
    print("-" * 72)

    # For each compound, generate a naive "combined meaning" and flag
    # if it clearly conflicts with the actual gloss
    # This is necessarily subjective, so we just present the data

    # Focus on high-frequency compounds where all atoms are known
    print("\n  HIGH-CONFIDENCE COMPOUNDS (all atoms Tier 2, >= 20 tokens):")
    tier2_atoms = {"k", "e", "h"}
    for tc, name, gloss, kernel in compounds:
        if tc < 20:
            continue
        chars = set(name)
        # Check if compound uses only tier-2 atoms
        if chars.issubset(tier2_atoms):
            parts = decompose(name, atoms)
            decomp = " + ".join(f"{c}({g})" for c, g in parts)
            print(f"    {name:10s} = {decomp:30s} -> \"{gloss}\" ({tc} tokens)")

    print("\n  STRONG COMPOUNDS (all atoms have glosses, >= 30 tokens):")
    for tc, name, gloss, kernel in compounds:
        if tc < 30:
            continue
        parts = decompose(name, atoms)
        if all(g is not None for _, g in parts):
            decomp = " + ".join(f"{c}({g})" for c, g in parts)
            print(f"    {name:10s} = {decomp:40s} -> \"{gloss}\" ({tc} tokens)")

    print()

    # --- Section 5: The "o" Test ---
    print("THE 'O' TEST")
    print("If o = 'vessel' (Ofen), do all o-compounds make sense?")
    print("-" * 72)

    o_compounds = [(tc, name, gloss, kernel) for tc, name, gloss, kernel
                   in compounds if "o" in name]
    o_compounds.sort(reverse=True)

    for tc, name, gloss, kernel in o_compounds:
        parts = []
        for ch in name:
            if ch == "o":
                parts.append("o(vessel)")
            elif ch in atoms:
                parts.append(f"{ch}({atoms[ch]['gloss']})")
            elif ch in proposed:
                parts.append(f"{ch}({proposed[ch]}*)")
            else:
                parts.append(f"{ch}(?)")
        decomp = " + ".join(parts)
        print(f"  {name:10s} {tc:5d} = {decomp:40s} -> \"{gloss}\"")

    print()

    # --- Section 6: Alternative Gloss Candidates ---
    print("ALTERNATIVE GLOSS CANDIDATES FOR WEAK ATOMS")
    print("For atoms with weak confidence, what gloss would make")
    print("all compounds fit better?")
    print("-" * 72)

    weak_atoms = ["o", "a", "c", "i", "p", "n"]
    for ch in weak_atoms:
        contexts = atom_contexts.get(ch, [])
        if not contexts:
            continue
        current = atoms.get(ch, {}).get("gloss", proposed.get(ch, "???"))
        unique_compounds = []
        seen = set()
        for mid_name, mid_gloss in contexts:
            if mid_name not in seen:
                seen.add(mid_name)
                unique_compounds.append((mid_name, mid_gloss))

        print(f"\n  {ch} (current: \"{current}\", {len(unique_compounds)} compounds):")
        print(f"  What single meaning for '{ch}' makes ALL of these work?")
        for mid_name, mid_gloss in unique_compounds[:15]:
            other_parts = []
            for c2 in mid_name:
                if c2 != ch:
                    g = atoms.get(c2, {}).get("gloss", proposed.get(c2, "?"))
                    other_parts.append(f"{c2}={g}")
            others = ", ".join(other_parts)
            print(f"    {mid_name:12s} \"{mid_gloss:14s}\"  (other atoms: {others})")

    # --- Save full results ---
    output = {
        "atoms": {k: v for k, v in atoms.items()},
        "proposed_atoms": proposed,
        "compounds": fit_results,
        "atom_contexts": {k: list(set(v)) for k, v in atom_contexts.items()},
    }
    out_path = RESULTS_DIR / "compound_decomposition.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nFull results saved to: {out_path}")


if __name__ == "__main__":
    main()
