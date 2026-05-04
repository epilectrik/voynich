"""
Phase 680 Script 3: Peek at paths between rosettes.

The 8 paths connecting the outer rosettes (NW->N->NE->E->SE->S->SW->W->NW)
have very few words (25 total). Too sparse for per-path fingerprints, but
we can:
  1. List every path token + its morphology
  2. Pool path tokens and compare fingerprint to pooled rosette nodes
  3. Check whether paths use bridge MIDDLEs (operational backbone) or
     non-bridge MIDDLEs (identification vocabulary, dark pipeline)
"""
import json
import sys
from collections import Counter
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Morphology


def main():
    d = json.load(open(Path(__file__).resolve().parents[3] / "data" / "rosettes_annotated.json", encoding="utf-8"))
    ents = d["entities"]
    morph = Morphology()

    print("=== EVERY PATH TOKEN ===\n")
    print(f"  {'Path':<18} {'Word':<14} {'Prefix':<6} {'Middle':<14} {'Suffix':<6} {'Bridge?':<8} {'Atoms':<30}")
    path_words_all = []
    for path_key in sorted([k for k in ents.keys() if k.startswith("PATH")]):
        for sub_name, sub in ents[path_key].get("sub_regions", {}).items():
            for locus in sub.get("loci", []):
                for w in locus.get("words", []):
                    word = w.get("word", "")
                    pre = w.get("prefix") or "-"
                    mid = w.get("middle") or "-"
                    suf = w.get("suffix") or w.get("terminal") or "-"
                    is_b = "YES" if w.get("is_bridge") else "no"
                    # Atomize for atom signature
                    clean = word.replace(".", "").replace(",", "").replace("'", "").strip()
                    atoms_str = "-"
                    if clean and "*" not in clean:
                        a = morph.atomize(clean)
                        atoms_str = "+".join(f"{c}({r[:1]})" for c, r, _ in a.atoms)
                        path_words_all.append({"word": clean, "atoms": a, "path": path_key, "sub": sub_name})
                    print(f"  {path_key:<18} {word:<14} {pre:<6} {mid:<14} {suf:<6} {is_b:<8} {atoms_str}")

    # Bridge vs non-bridge analysis
    n_bridge = 0
    n_total = 0
    for path_key in [k for k in ents.keys() if k.startswith("PATH")]:
        n_bridge += len(ents[path_key].get("bridge_middles", []))
        n_total += len(ents[path_key].get("unique_middles", []))
    print(f"\n=== PATH BRIDGE-vs-NON-BRIDGE ===")
    print(f"  Path MIDDLEs total: {n_total}")
    print(f"  Path MIDDLEs that are bridge: {n_bridge}")
    print(f"  Bridge fraction: {n_bridge/max(1, n_total)*100:.1f}%")
    # Compare to rosette node bridge fraction
    n_node_bridge = 0
    n_node_total = 0
    for ros_key in ["CENTER", "NORTH", "NE", "EAST", "SE", "SOUTH", "SW", "WEST", "NW"]:
        n_node_bridge += len(ents[ros_key].get("bridge_middles", []))
        n_node_total += len(ents[ros_key].get("unique_middles", []))
    print(f"  Rosette-node MIDDLEs total: {n_node_total}")
    print(f"  Rosette-node MIDDLEs that are bridge: {n_node_bridge}")
    print(f"  Bridge fraction (rosette nodes): {n_node_bridge/max(1, n_node_total)*100:.1f}%")

    # Pooled fingerprint comparison (paths vs nodes)
    print("\n=== POOLED FINGERPRINT: PATHS vs NODES ===")
    def pool_fingerprint(words_list):
        prefix_count = Counter()
        head_count = Counter()
        term_count = Counter()
        kernel_count = Counter()
        edepth_values = []
        bare_count = 0
        n_atomized = 0
        n = 0
        for w in words_list:
            word_str = w.get("word") if isinstance(w, dict) else w
            if not word_str:
                continue
            clean = word_str.replace(".", "").replace(",", "").replace("'", "").strip()
            if not clean or "*" in clean:
                continue
            n += 1
            a = morph.atomize(clean)
            prefix_count[a.prefix or "BARE"] += 1
            if not a.prefix:
                bare_count += 1
            if a.atoms:
                n_atomized += 1
                head_char, head_role, _ = a.atoms[0]
                if head_role == "HEAD":
                    head_count[head_char] += 1
                term_char, term_role, _ = a.atoms[-1]
                if term_role == "TERM":
                    term_count[term_char] += 1
                for ch, role, _ in a.atoms:
                    if ch in "kehpc":
                        kernel_count[ch] += 1
                edepth_values.append(a.e_depth)
        if n_atomized == 0:
            return None
        return {
            "n": n, "n_atomized": n_atomized,
            "prefix_rates": {p: c / n for p, c in prefix_count.items()},
            "head_rates": {h: c / n_atomized for h, c in head_count.items()},
            "term_rates": {t: c / n_atomized for t, c in term_count.items()},
            "kernel_rates": {k: c / n_atomized for k, c in kernel_count.items()},
            "edepth_mean": mean(edepth_values) if edepth_values else 0,
            "bare_rate": bare_count / n,
        }

    # Collect path words
    path_words = []
    for path_key in [k for k in ents.keys() if k.startswith("PATH")]:
        for sub_name, sub in ents[path_key].get("sub_regions", {}).items():
            for locus in sub.get("loci", []):
                for w in locus.get("words", []):
                    path_words.append(w)
    # Collect rosette node words
    node_words = []
    for ros_key in ["CENTER", "NORTH", "NE", "EAST", "SE", "SOUTH", "SW", "WEST", "NW"]:
        for sub_name, sub in ents[ros_key].get("sub_regions", {}).items():
            for locus in sub.get("loci", []):
                for w in locus.get("words", []):
                    node_words.append(w)

    paths_fp = pool_fingerprint(path_words)
    nodes_fp = pool_fingerprint(node_words)

    if paths_fp and nodes_fp:
        print(f"\n  {'Metric':<14} {'Paths (n='+str(paths_fp['n'])+')':<14} {'Nodes (n='+str(nodes_fp['n'])+')':<14} Diff")
        print(f"  BARE rate     {paths_fp['bare_rate']*100:>6.1f}%        {nodes_fp['bare_rate']*100:>6.1f}%        "
              f"{(paths_fp['bare_rate']-nodes_fp['bare_rate'])*100:>+5.1f}%")
        print(f"  e-depth mean  {paths_fp['edepth_mean']:>6.2f}         {nodes_fp['edepth_mean']:>6.2f}         "
              f"{paths_fp['edepth_mean']-nodes_fp['edepth_mean']:>+5.2f}")
        print()
        print(f"  PREFIX rates:")
        all_prefixes = set(paths_fp["prefix_rates"]) | set(nodes_fp["prefix_rates"])
        for p in sorted(all_prefixes):
            pp = paths_fp["prefix_rates"].get(p, 0)
            np_ = nodes_fp["prefix_rates"].get(p, 0)
            if pp > 0.04 or np_ > 0.04:
                print(f"    {p:<12} paths {pp*100:>5.1f}%  nodes {np_*100:>5.1f}%  diff {(pp-np_)*100:>+5.1f}%")
        print()
        print(f"  HEAD atoms:")
        for h in "aeokt":
            ph = paths_fp["head_rates"].get(h, 0)
            nh = nodes_fp["head_rates"].get(h, 0)
            print(f"    {h:<3} paths {ph*100:>5.1f}%  nodes {nh*100:>5.1f}%  diff {(ph-nh)*100:>+5.1f}%")
        print()
        print(f"  TERM atoms:")
        for t in "ynlrm":
            pt = paths_fp["term_rates"].get(t, 0)
            nt = nodes_fp["term_rates"].get(t, 0)
            if pt > 0.05 or nt > 0.05:
                print(f"    {t:<3} paths {pt*100:>5.1f}%  nodes {nt*100:>5.1f}%  diff {(pt-nt)*100:>+5.1f}%")


if __name__ == "__main__":
    main()
