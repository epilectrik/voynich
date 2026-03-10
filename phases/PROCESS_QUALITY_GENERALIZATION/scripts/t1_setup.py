"""
Phase 571 T1: Setup and upstream data verification.

Loads 570a F-parameter data, verifies upstream data coverage for all 18 folios
(20-folio pilot minus f40v and f81v which have zero CLOSE lines), and outputs
a unified config JSON for T2/T3.
"""

import json
import os
import sys
from datetime import datetime, timezone
from collections import defaultdict

# Paths
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PILOT_PATH = os.path.join(ROOT, "phases", "FOLIO_SPECIFIC_APPARATUS_PILOT", "results", "t1_pilot_selection.json")
OUTPUT_DIR = os.path.join(ROOT, "phases", "PROCESS_QUALITY_GENERALIZATION", "results")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "t1_setup.json")

# The 18 folios (20-folio pilot minus f40v, f81v which have zero CLOSE lines)
EXCLUDED = ["f40v", "f81v"]
TARGET_FOLIOS = sorted([
    "f78r", "f84r", "f79r", "f55r", "f43v", "f34r", "f31r", "f39v",
    "f95r1", "f104r", "f111r", "f116r", "f105r", "f108v", "f66r",
    "f85r1", "f86v5", "f86v6"
])

# Original 4 pilot folios from 570a
ORIGINAL_4_PILOT = ["f108v", "f86v6", "f111r", "f84r"]

# 7 upstream data files to verify
UPSTREAM_FILES = {
    "line_packets": os.path.join(ROOT, "phases", "SECTION_TEMPLATE_TRACE_EXECUTOR", "results", "t3_line_packets.json"),
    "closure_cts": os.path.join(ROOT, "phases", "SECTION_TEMPLATE_TRACE_EXECUTOR", "results", "t7_closure_cts.json"),
    "supervisory_tokens": os.path.join(ROOT, "phases", "VIRTUAL_APPARATUS_COUPLING", "results", "t2b_supervisory_interface_unrouted.json"),
    "folio_budgets": os.path.join(ROOT, "phases", "SECTION_TEMPLATE_TRACE_EXECUTOR", "results", "t2_folio_budgets.json"),
    "event_taxonomy": os.path.join(ROOT, "phases", "EVENTIVE_CLOSURE_PACKETS", "results", "t1_event_taxonomy.json"),
    "regime_mapping": os.path.join(ROOT, "data", "regime_folio_mapping.json"),
    "dwell_architecture": os.path.join(ROOT, "phases", "REGIME_DWELL_ARCHITECTURE", "results", "dwell_architecture.json"),
}


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_line_packets(data, folios):
    """line_packets: keys are 'folio|line', extract folio part."""
    packets = data.get("line_packets", {})
    found_folios = set()
    for key in packets:
        folio = key.split("|")[0]
        found_folios.add(folio)
    missing = [f for f in folios if f not in found_folios]
    counts = defaultdict(int)
    for key in packets:
        folio = key.split("|")[0]
        if folio in folios:
            counts[folio] += 1
    return missing, dict(counts)


def check_closure_cts(data, folios):
    """line_cts: keys are 'folio|line', extract folio part."""
    cts = data.get("line_cts", {})
    found_folios = set()
    for key in cts:
        folio = key.split("|")[0]
        found_folios.add(folio)
    missing = [f for f in folios if f not in found_folios]
    counts = defaultdict(int)
    for key in cts:
        folio = key.split("|")[0]
        if folio in folios:
            counts[folio] += 1
    return missing, dict(counts)


def check_supervisory_tokens(data, folios):
    """token_signals: array of objects with 'folio' field."""
    tokens = data.get("token_signals", [])
    found_folios = set()
    counts = defaultdict(int)
    for t in tokens:
        folio = t.get("folio", "")
        found_folios.add(folio)
        if folio in folios:
            counts[folio] += 1
    missing = [f for f in folios if f not in found_folios]
    return missing, dict(counts)


def check_folio_budgets(data, folios):
    """folio_budgets: top-level keys are folio names."""
    budgets = data.get("folio_budgets", {})
    missing = [f for f in folios if f not in budgets]
    counts = {f: 1 for f in folios if f in budgets}
    return missing, counts


def check_event_taxonomy(data, folios):
    """event_map: keys are 'folio|line', count entries per folio."""
    emap = data.get("event_map", {})
    found_folios = set()
    counts = defaultdict(int)
    for key in emap:
        folio = key.split("|")[0]
        found_folios.add(folio)
        if folio in folios:
            counts[folio] += 1
    missing = [f for f in folios if f not in found_folios]
    return missing, dict(counts)


def check_regime_mapping(data, folios):
    """regime_assignments: top-level keys are folio names."""
    assignments = data.get("regime_assignments", {})
    missing = [f for f in folios if f not in assignments]
    counts = {f: 1 for f in folios if f in assignments}
    return missing, counts


def check_dwell_architecture(data, folios):
    """folio_details: array of objects with 'folio' field."""
    details = data.get("folio_details", [])
    found_folios = set()
    for d in details:
        found_folios.add(d.get("folio", ""))
    missing = [f for f in folios if f not in found_folios]
    counts = {f: 1 for f in folios if f in found_folios}
    return missing, counts


def main():
    # --- Load pilot selection data ---
    print("=" * 70)
    print("Phase 571 T1: Setup and Upstream Data Verification")
    print("=" * 70)
    print()

    pilot = load_json(PILOT_PATH)
    folio_params = pilot["folio_parameters"]
    pilot_proxies = pilot["all_pilot_proxies"]

    # Verify all 18 folios present in pilot data
    missing_in_pilot = [f for f in TARGET_FOLIOS if f not in folio_params]
    if missing_in_pilot:
        print(f"FATAL: Missing folios in pilot folio_parameters: {missing_in_pilot}")
        sys.exit(1)

    missing_in_proxies = [f for f in TARGET_FOLIOS if f not in pilot_proxies]
    if missing_in_proxies:
        print(f"FATAL: Missing folios in pilot all_pilot_proxies: {missing_in_proxies}")
        sys.exit(1)

    # Build folio_configs
    folio_configs = {}
    for f in TARGET_FOLIOS:
        fp = folio_params[f]
        pp = pilot_proxies[f]
        folio_configs[f] = {
            "F1": fp["F1"],
            "F2": fp["F2"],
            "F3": fp["F3"],
            "F4_raw": fp["F4_raw"],
            "F5": fp["F5"],
            "profile": fp["profile"],
            "section": fp["section"],
            "n_close_lines": pp["n_close_lines"],
            "n_work_pred": pp["n_work_pred"],
        }

    # Build section and profile groupings
    sections = defaultdict(list)
    profiles = defaultdict(list)
    for f in TARGET_FOLIOS:
        sections[folio_configs[f]["section"]].append(f)
        profiles[folio_configs[f]["profile"]].append(f)
    sections = {k: sorted(v) for k, v in sorted(sections.items())}
    profiles = {k: sorted(v) for k, v in sorted(profiles.items())}

    # --- Verify 7 upstream data files ---
    print("Upstream Data Coverage Check")
    print("-" * 70)

    checkers = {
        "line_packets": check_line_packets,
        "closure_cts": check_closure_cts,
        "supervisory_tokens": check_supervisory_tokens,
        "folio_budgets": check_folio_budgets,
        "event_taxonomy": check_event_taxonomy,
        "regime_mapping": check_regime_mapping,
        "dwell_architecture": check_dwell_architecture,
    }

    data_coverage = {}
    all_ok = True

    for name, path in UPSTREAM_FILES.items():
        if not os.path.exists(path):
            print(f"  MISSING FILE: {name} -> {path}")
            data_coverage[name] = False
            all_ok = False
            continue

        data = load_json(path)
        missing, counts = checkers[name](data, TARGET_FOLIOS)

        if missing:
            print(f"  {name}: INCOMPLETE — missing {missing}")
            data_coverage[name] = False
            all_ok = False
        else:
            data_coverage[name] = True

        # Print coverage summary
        covered = len(TARGET_FOLIOS) - len(missing)
        total_entries = sum(counts.values()) if counts else 0
        print(f"  {name}: {covered}/18 folios, {total_entries} entries  {'OK' if not missing else 'FAIL'}")

    print()

    # --- Print folio summary ---
    print("Folio Configuration Summary")
    print("-" * 70)
    print(f"  {'Folio':<8} {'Sect':>4} {'Profile':<28} {'F1':>6} {'F2':>6} {'F3':>6} {'F4r':>6} {'F5':>6} {'CL':>4} {'WP':>4}")
    print(f"  {'-----':<8} {'----':>4} {'-------':<28} {'--':>6} {'--':>6} {'--':>6} {'---':>6} {'--':>6} {'--':>4} {'--':>4}")
    for f in TARGET_FOLIOS:
        c = folio_configs[f]
        print(f"  {f:<8} {c['section']:>4} {c['profile']:<28} {c['F1']:>6.4f} {c['F2']:>6.4f} {c['F3']:>6.4f} {c['F4_raw']:>6.4f} {c['F5']:>6.4f} {c['n_close_lines']:>4} {c['n_work_pred']:>4}")
    print()

    # Section/profile summary
    print("Section Distribution:")
    for s, fs in sections.items():
        print(f"  {s}: {fs}")

    print()
    print("Profile Distribution:")
    for p, fs in profiles.items():
        print(f"  {p}: {fs}")

    print()
    print(f"Original 4-pilot folios: {ORIGINAL_4_PILOT}")
    print(f"Excluded (zero CLOSE lines): {EXCLUDED}")
    print()

    if all_ok:
        print("ALL 7 upstream data files verified — full coverage for 18 folios.")
    else:
        print("WARNING: Some upstream data files have incomplete coverage.")

    # --- Write output ---
    output = {
        "metadata": {
            "phase": "571",
            "script": "t1_setup.py",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "n_folios": len(TARGET_FOLIOS),
            "excluded": EXCLUDED,
            "exclusion_reason": "zero CLOSE lines in event taxonomy",
        },
        "folios": TARGET_FOLIOS,
        "folio_configs": folio_configs,
        "data_coverage": data_coverage,
        "summary": {
            "sections": sections,
            "profiles": profiles,
            "original_4_pilot": ORIGINAL_4_PILOT,
        },
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput written: {OUTPUT_PATH}")
    print(f"  n_folios: {len(TARGET_FOLIOS)}")
    print(f"  data_coverage: {sum(v for v in data_coverage.values())}/7 complete")


if __name__ == "__main__":
    main()
