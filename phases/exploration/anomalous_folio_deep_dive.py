#!/usr/bin/env python3
"""
E3: Anomalous Folio Deep Dive

Investigates what makes f41r, f65r, f67r2, f86v5 special beyond HT.

These 4 folios cluster by human burden across system boundaries:
- f41r, f86v5: B folios, HT hotspots
- f65r, f67r2: AZC folios, HT hotspots

Key insight from E2: ALL B folios have zero escape, so that's not what
distinguishes f41r and f86v5. Something else makes them HT hotspots.

Questions:
1. What manuscript positions are these folios at?
2. Where in their quires do they fall?
3. What are their neighbors like?
4. What other metrics distinguish them from similar folios?
5. Are there other HT hotspots that DON'T share these properties?
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

# Target anomalous folios
ANOMALOUS_FOLIOS = ["f41r", "f65r", "f67r2", "f86v5"]


def get_folio_order(unified):
    """Get manuscript order of folios."""
    folios = list(unified['profiles'].keys())

    def folio_sort_key(f):
        match = re.match(r'f(\d+)([rv]?)(\d*)', f)
        if match:
            num = int(match.group(1))
            side = 0 if match.group(2) == 'r' else 1 if match.group(2) == 'v' else 0
            sub = int(match.group(3)) if match.group(3) else 0
            return (num, side, sub)
        return (9999, 0, 0)

    return sorted(folios, key=folio_sort_key)


def load_data():
    """Load all relevant data files."""
    # Unified profiles
    with open(RESULTS_DIR / "unified_folio_profiles.json") as f:
        unified = json.load(f)

    # Get folio order from profiles
    folio_order = get_folio_order(unified)

    # Quire data (from E1)
    with open(RESULTS_DIR / "quire_rhythm_analysis.json") as f:
        quire_data = json.load(f)

    return unified, folio_order, quire_data


def get_folio_position(folio, folio_order):
    """Get folio's position in manuscript order."""
    try:
        return folio_order.index(folio)
    except ValueError:
        return None


def get_quire_info(folio, quire_profiles):
    """Get quire information for a folio."""
    for quire, profile in quire_profiles.items():
        if folio >= profile.get("first_folio", "") and folio <= profile.get("last_folio", ""):
            # This is approximate - quire assignment
            return {
                "quire": quire,
                "quire_size": profile["n_folios"],
                "quire_ht_mean": profile["ht_mean"],
                "quire_ht_std": profile["ht_std"]
            }
    return None


def analyze_anomalous_folios(unified, folio_order, quire_data):
    """Deep analysis of the 4 anomalous folios."""
    profiles = unified.get("profiles", {})
    quire_profiles = quire_data.get("quire_profiles", {})

    results = []

    for folio in ANOMALOUS_FOLIOS:
        if folio not in profiles:
            print(f"  WARNING: {folio} not found in profiles")
            continue

        profile = profiles[folio]
        position = get_folio_position(folio, folio_order)
        total_folios = len(folio_order)

        # Basic info
        info = {
            "folio": folio,
            "system": profile.get("system"),
            "ht_density": profile.get("ht_density"),
            "ht_percentile_in_system": None,  # Will calculate
            "position": position,
            "position_percentile": round(position / total_folios * 100, 1) if position else None,
        }

        # Regime info
        if profile.get("system") == "B":
            b_metrics = profile.get("b_metrics", {}) or {}
            info["regime"] = b_metrics.get("regime")
            info["hazard_density"] = b_metrics.get("hazard_density")
            info["escape_density"] = b_metrics.get("escape_density")
            info["cei"] = b_metrics.get("cei_total")
        elif profile.get("system") == "AZC":
            azc_metrics = profile.get("azc_metrics", {}) or {}
            info["azc_ratio"] = azc_metrics.get("azc_ratio")
            info["qo_density"] = azc_metrics.get("qo_density")

        # Quire info
        for quire, qp in quire_profiles.items():
            first = qp.get("first_folio", "")
            last = qp.get("last_folio", "")
            # Check if folio is in this quire
            if folio in [p["folio"] for p in unified.get("profiles", {}).values()
                         if p.get("quire") == quire]:
                info["quire"] = quire
                info["quire_ht_mean"] = qp.get("ht_mean")
                info["quire_n_folios"] = qp.get("n_folios")
                break
        else:
            # Fallback: get from profile if available
            if "quire" in profile:
                info["quire"] = profile.get("quire")

        # Calculate HT percentile within system
        system = profile.get("system")
        system_hts = [p.get("ht_density", 0) for p in profiles.values()
                      if p.get("system") == system and p.get("ht_density") is not None]
        if system_hts:
            ht = profile.get("ht_density", 0)
            percentile = sum(1 for h in system_hts if h <= ht) / len(system_hts) * 100
            info["ht_percentile_in_system"] = round(percentile, 1)

        # Get neighbors
        if position:
            before_folio = folio_order[position - 1] if position > 0 else None
            after_folio = folio_order[position + 1] if position < len(folio_order) - 1 else None

            if before_folio and before_folio in profiles:
                before_profile = profiles[before_folio]
                info["neighbor_before"] = {
                    "folio": before_folio,
                    "system": before_profile.get("system"),
                    "ht_density": before_profile.get("ht_density")
                }

            if after_folio and after_folio in profiles:
                after_profile = profiles[after_folio]
                info["neighbor_after"] = {
                    "folio": after_folio,
                    "system": after_profile.get("system"),
                    "ht_density": after_profile.get("ht_density")
                }

        results.append(info)

    return results


def find_comparable_folios(unified, anomalous_results):
    """Find folios similar to anomalous ones that are NOT HT hotspots."""
    profiles = unified.get("profiles", {})

    comparisons = {}

    for anomalous in anomalous_results:
        folio = anomalous["folio"]
        system = anomalous["system"]
        ht = anomalous["ht_density"]

        # Find same-system folios with normal HT
        same_system = []
        for f, p in profiles.items():
            if p.get("system") == system and f != folio:
                same_system.append({
                    "folio": f,
                    "ht_density": p.get("ht_density"),
                    "regime": p.get("regime") if system == "B" else None,
                    "hazard_density": p.get("hazard_density") if system == "B" else None,
                })

        # Sort by HT to find median examples
        same_system.sort(key=lambda x: x.get("ht_density", 0))

        if same_system:
            median_idx = len(same_system) // 2
            comparisons[folio] = {
                "anomalous_ht": ht,
                "system_median_ht": same_system[median_idx]["ht_density"],
                "system_median_example": same_system[median_idx]["folio"],
                "lowest_ht_in_system": same_system[0],
                "highest_ht_in_system": same_system[-1],
                "n_in_system": len(same_system) + 1  # +1 for the anomalous one
            }

    return comparisons


def analyze_all_ht_hotspots(unified):
    """Find ALL HT hotspots across all systems."""
    profiles = unified.get("profiles", {})

    # Calculate 95th percentile HT threshold per system
    by_system = defaultdict(list)
    for f, p in profiles.items():
        if p.get("ht_density") is not None:
            by_system[p.get("system")].append((f, p.get("ht_density")))

    hotspots = []
    for system, folios in by_system.items():
        folios.sort(key=lambda x: x[1])
        threshold_idx = int(len(folios) * 0.95)
        threshold = folios[threshold_idx][1] if threshold_idx < len(folios) else folios[-1][1]

        for f, ht in folios:
            if ht >= threshold:
                p = profiles[f]
                hotspots.append({
                    "folio": f,
                    "system": system,
                    "ht_density": ht,
                    "regime": p.get("regime"),
                    "is_anomalous": f in ANOMALOUS_FOLIOS
                })

    return hotspots


def analyze_position_patterns(anomalous_results, unified, folio_order):
    """Check if anomalous folios share positional patterns."""
    profiles = unified.get("profiles", {})

    patterns = {
        "positions": [],
        "quire_positions": [],
        "at_quire_boundary": [],
        "at_system_boundary": [],
    }

    for result in anomalous_results:
        folio = result["folio"]
        position = result.get("position")

        if position:
            patterns["positions"].append(position)

            # Check system boundary
            before = folio_order[position - 1] if position > 0 else None
            after = folio_order[position + 1] if position < len(folio_order) - 1 else None

            system = result.get("system")
            before_system = profiles.get(before, {}).get("system") if before else None
            after_system = profiles.get(after, {}).get("system") if after else None

            at_boundary = (before_system != system if before_system else False) or \
                          (after_system != system if after_system else False)
            patterns["at_system_boundary"].append({
                "folio": folio,
                "at_boundary": at_boundary,
                "before_system": before_system,
                "after_system": after_system
            })

    return patterns


def analyze_distinguishing_features(anomalous_results, unified):
    """Find what metrics distinguish anomalous folios from their peers."""
    profiles = unified.get("profiles", {})

    features = {}

    for result in anomalous_results:
        folio = result["folio"]
        system = result["system"]

        # Get all same-system folios
        same_system = [(f, p) for f, p in profiles.items() if p.get("system") == system]

        if system == "B":
            # For B folios, check regime distribution of hotspots
            regime = result.get("regime")
            same_regime = [f for f, p in same_system
                           if (p.get("b_metrics") or {}).get("regime") == regime]
            regime_hts = [profiles[f].get("ht_density", 0) for f in same_regime]

            if regime_hts:
                mean_regime_ht = sum(regime_hts) / len(regime_hts)
                features[folio] = {
                    "regime": regime,
                    "n_in_regime": len(same_regime),
                    "regime_mean_ht": round(mean_regime_ht, 4),
                    "folio_ht": result["ht_density"],
                    "ht_vs_regime_mean": round(result["ht_density"] - mean_regime_ht, 4),
                    "hazard_density": result.get("hazard_density"),
                }

                # Get regime hazard stats
                regime_hazards = [(profiles[f].get("b_metrics") or {}).get("hazard_density")
                                  for f in same_regime]
                regime_hazards = [h for h in regime_hazards if h is not None]
                if regime_hazards and result.get("hazard_density") is not None:
                    mean_hazard = sum(regime_hazards) / len(regime_hazards)
                    features[folio]["regime_mean_hazard"] = round(mean_hazard, 4)
                    features[folio]["hazard_vs_regime_mean"] = round(
                        result.get("hazard_density") - mean_hazard, 4)

        elif system == "AZC":
            # For AZC folios, check azc_ratio and qo_density
            azc_metrics = profiles[folio].get("azc_metrics") or {}
            azc_ratio = azc_metrics.get("azc_ratio")
            qo_density = azc_metrics.get("qo_density")

            all_azc_ratios = [(p.get("azc_metrics") or {}).get("azc_ratio")
                              for _, p in same_system]
            all_azc_ratios = [r for r in all_azc_ratios if r is not None]

            all_qo = [(p.get("azc_metrics") or {}).get("qo_density")
                      for _, p in same_system]
            all_qo = [q for q in all_qo if q is not None]

            features[folio] = {
                "azc_ratio": azc_ratio,
                "qo_density": qo_density,
                "ht_density": result["ht_density"],
            }

            if all_azc_ratios:
                mean_ratio = sum(all_azc_ratios) / len(all_azc_ratios)
                features[folio]["system_mean_azc_ratio"] = round(mean_ratio, 4)
            if all_qo:
                mean_qo = sum(all_qo) / len(all_qo)
                features[folio]["system_mean_qo"] = round(mean_qo, 4)

    return features


def main():
    print("=" * 70)
    print("E3: Anomalous Folio Deep Dive")
    print("=" * 70)

    print("\n[1] Loading data...")
    unified, folio_order, quire_data = load_data()
    profiles = unified.get("profiles", {})
    print(f"    Profiles: {len(profiles)}")
    print(f"    Anomalous folios: {ANOMALOUS_FOLIOS}")

    print("\n[2] Analyzing anomalous folios...")
    anomalous_results = analyze_anomalous_folios(unified, folio_order, quire_data)

    for result in anomalous_results:
        print(f"\n    {result['folio']} ({result['system']}):")
        print(f"      HT: {result['ht_density']:.4f} ({result.get('ht_percentile_in_system', 'N/A')}th percentile)")
        print(f"      Position: {result.get('position')} ({result.get('position_percentile')}% through manuscript)")
        if result.get('regime'):
            print(f"      Regime: {result['regime']}")
            print(f"      Hazard: {result.get('hazard_density', 'N/A')}")

    print("\n[3] Finding comparable folios...")
    comparisons = find_comparable_folios(unified, anomalous_results)

    for folio, comp in comparisons.items():
        print(f"\n    {folio}:")
        print(f"      This folio HT: {comp['anomalous_ht']:.4f}")
        print(f"      System median HT: {comp['system_median_ht']:.4f}")
        print(f"      Ratio to median: {comp['anomalous_ht'] / comp['system_median_ht']:.2f}x")

    print("\n[4] Finding ALL HT hotspots...")
    all_hotspots = analyze_all_ht_hotspots(unified)
    print(f"    Total hotspots (>95th percentile): {len(all_hotspots)}")

    anomalous_in_hotspots = [h for h in all_hotspots if h["is_anomalous"]]
    other_hotspots = [h for h in all_hotspots if not h["is_anomalous"]]

    print(f"    Anomalous in hotspots: {len(anomalous_in_hotspots)}")
    print(f"    Other hotspots: {len(other_hotspots)}")

    for h in other_hotspots:
        print(f"      {h['folio']} ({h['system']}): HT={h['ht_density']:.4f}")

    print("\n[5] Analyzing position patterns...")
    position_patterns = analyze_position_patterns(anomalous_results, unified, folio_order)

    for boundary in position_patterns["at_system_boundary"]:
        print(f"    {boundary['folio']}: at_boundary={boundary['at_boundary']}")
        if boundary.get("before_system"):
            print(f"      Before: {boundary['before_system']}")
        if boundary.get("after_system"):
            print(f"      After: {boundary['after_system']}")

    print("\n[6] Analyzing distinguishing features...")
    distinguishing = analyze_distinguishing_features(anomalous_results, unified)

    for folio, features in distinguishing.items():
        print(f"\n    {folio}:")
        for key, val in features.items():
            print(f"      {key}: {val}")

    print("\n[7] Synthesizing key findings...")

    # Determine what makes these special
    key_findings = []

    # Check if they're at system boundaries
    boundary_count = sum(1 for b in position_patterns["at_system_boundary"] if b["at_boundary"])
    if boundary_count > 0:
        key_findings.append({
            "finding": f"{boundary_count} of 4 anomalous folios are at system boundaries",
            "interpretation": "HT hotspots may mark transitions"
        })

    # Check position clustering
    positions = position_patterns["positions"]
    if positions:
        mean_pos = sum(positions) / len(positions)
        total = len(folio_order)
        if mean_pos < total * 0.33:
            key_findings.append({
                "finding": "Anomalous folios cluster in early third of manuscript",
                "interpretation": "Front-loaded vigilance markers"
            })
        elif mean_pos > total * 0.67:
            key_findings.append({
                "finding": "Anomalous folios cluster in late third of manuscript",
                "interpretation": "Back-loaded vigilance markers"
            })
        else:
            key_findings.append({
                "finding": "Anomalous folios are distributed throughout manuscript",
                "mean_position_percentile": round(mean_pos / total * 100, 1),
                "interpretation": "No positional clustering"
            })

    # Check regime patterns for B folios
    b_regimes = [r.get("regime") for r in anomalous_results if r.get("system") == "B"]
    if b_regimes:
        unique_regimes = set(b_regimes)
        if len(unique_regimes) == 1:
            key_findings.append({
                "finding": f"Both B hotspots are {list(unique_regimes)[0]}",
                "interpretation": "Regime-specific HT elevation"
            })
        else:
            key_findings.append({
                "finding": f"B hotspots span regimes: {list(unique_regimes)}",
                "interpretation": "HT elevation not regime-specific"
            })

    # Check if other hotspots exist that we didn't identify
    if other_hotspots:
        key_findings.append({
            "finding": f"{len(other_hotspots)} additional HT hotspots exist beyond the 4 anomalous",
            "other_hotspots": [h["folio"] for h in other_hotspots],
            "interpretation": "Anomalous 4 are not the ONLY hotspots"
        })

    for finding in key_findings:
        print(f"\n    - {finding['finding']}")
        print(f"      {finding['interpretation']}")

    # Compile output
    output = {
        "metadata": {
            "analysis": "E3 - Anomalous Folio Deep Dive",
            "description": "Investigating what makes f41r, f65r, f67r2, f86v5 special",
            "target_folios": ANOMALOUS_FOLIOS,
        },
        "anomalous_profiles": anomalous_results,
        "comparisons_to_peers": comparisons,
        "all_ht_hotspots": all_hotspots,
        "position_patterns": position_patterns,
        "distinguishing_features": distinguishing,
        "key_findings": key_findings,
    }

    # Save output
    print("\n[8] Saving output...")
    output_path = RESULTS_DIR / "anomalous_folio_deep_dive.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"    Saved to: {output_path}")

    print("\n" + "=" * 70)
    print("E3 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
