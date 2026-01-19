"""
T9: Puff Danger Profile -> HT Density Correlation
Expert-proposed "killer test"

Hypothesis: Puff materials flagged as dangerous correlate with higher HT density
in corresponding Voynich folios (via positional mapping).

C459 establishes HT as anticipatory compensation (r=0.343, p=0.0015).
If dangerous materials require extra caution, HT should be elevated.
"""

import json
import numpy as np
from scipy import stats
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

# Puff dangerous chapters (from puff_83_chapters.json)
PUFF_DANGEROUS = {
    17: ("Nachtschatten", "Solanum nigrum"),    # Nightshade
    38: ("Spindelbom", "Euonymus europaea"),    # Euonymus
    57: ("Mauchen", "Papaver somniferum"),       # Poppy
    60: ("Poleyen", "Mentha pulegium"),          # Pennyroyal
    79: ("Bilsen", "Hyoscyamus niger"),          # Henbane
}

def load_proposed_order():
    """Load proposed folio order with positions."""
    folio_order = []
    with open(RESULTS_DIR / "proposed_folio_order.txt", 'r', encoding='utf-8') as f:
        for line in f:
            if '|' in line and 'REGIME' in line:
                parts = line.split('|')
                if len(parts) >= 5:
                    try:
                        pos = int(parts[0].strip())
                        folio = parts[1].strip()
                        regime = parts[2].strip()
                        folio_order.append({
                            'position': pos,
                            'folio': folio,
                            'regime': regime,
                        })
                    except (ValueError, IndexError):
                        continue
    folio_order.sort(key=lambda x: x['position'])
    return folio_order

def load_ht_density():
    """Load HT density per folio."""
    with open(RESULTS_DIR / "ht_folio_features.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {f: d.get('ht_density', 0) for f, d in data['folios'].items()}

def run_test():
    """Run T9: Danger -> HT correlation test."""
    print("=" * 60)
    print("T9: PUFF DANGER PROFILE -> HT DENSITY CORRELATION")
    print("=" * 60)
    print()

    # Load data
    folio_order = load_proposed_order()
    ht_density = load_ht_density()

    print(f"Loaded {len(folio_order)} folios in proposed order")
    print(f"HT density available for {len(ht_density)} folios")
    print()

    # Categorize folios as dangerous or safe based on Puff position
    dangerous_positions = set(PUFF_DANGEROUS.keys())
    dangerous_ht = []
    safe_ht = []
    position_ht_map = {}

    for entry in folio_order[:83]:  # Only first 83 (matching Puff chapters)
        pos = entry['position']
        folio = entry['folio']

        ht = ht_density.get(folio, None)
        if ht is None:
            continue

        position_ht_map[pos] = ht

        if pos in dangerous_positions:
            dangerous_ht.append(ht)
            mat_name, lat_name = PUFF_DANGEROUS[pos]
            print(f"  DANGEROUS Pos {pos}: {folio} -> HT={ht:.4f} ({mat_name})")
        else:
            safe_ht.append(ht)

    print()
    print("-" * 60)
    print("RESULTS")
    print("-" * 60)
    print()

    # Basic statistics
    danger_mean = np.mean(dangerous_ht) if dangerous_ht else 0
    danger_std = np.std(dangerous_ht) if dangerous_ht else 0
    safe_mean = np.mean(safe_ht) if safe_ht else 0
    safe_std = np.std(safe_ht) if safe_ht else 0

    print(f"Dangerous materials (n={len(dangerous_ht)}):")
    print(f"  Mean HT density: {danger_mean:.4f}")
    print(f"  Std HT density:  {danger_std:.4f}")
    print()
    print(f"Safe materials (n={len(safe_ht)}):")
    print(f"  Mean HT density: {safe_mean:.4f}")
    print(f"  Std HT density:  {safe_std:.4f}")
    print()

    # Effect size
    if danger_mean > safe_mean:
        enrichment = danger_mean / safe_mean if safe_mean > 0 else float('inf')
        print(f"HT Enrichment in dangerous: {enrichment:.2f}x")
    else:
        enrichment = safe_mean / danger_mean if danger_mean > 0 else float('inf')
        print(f"HT Enrichment in SAFE (unexpected): {enrichment:.2f}x")
    print()

    # Statistical test (Mann-Whitney U)
    if len(dangerous_ht) >= 2 and len(safe_ht) >= 2:
        u_stat, p_value = stats.mannwhitneyu(dangerous_ht, safe_ht, alternative='greater')
        print(f"Mann-Whitney U test (dangerous > safe):")
        print(f"  U statistic: {u_stat:.1f}")
        print(f"  p-value: {p_value:.4f}")
    else:
        u_stat, p_value = None, None
        print("Insufficient data for Mann-Whitney U test")
    print()

    # Permutation test for robustness
    all_ht = dangerous_ht + safe_ht
    n_danger = len(dangerous_ht)
    observed_diff = danger_mean - safe_mean

    n_perms = 10000
    perm_diffs = []
    for _ in range(n_perms):
        np.random.shuffle(all_ht)
        perm_danger = all_ht[:n_danger]
        perm_safe = all_ht[n_danger:]
        perm_diffs.append(np.mean(perm_danger) - np.mean(perm_safe))

    perm_p = np.mean([d >= observed_diff for d in perm_diffs])
    print(f"Permutation test ({n_perms:,} permutations):")
    print(f"  Observed difference: {observed_diff:.4f}")
    print(f"  Permutation p-value: {perm_p:.4f}")
    print()

    # Verdict
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)

    passed = False
    verdict_detail = ""

    if danger_mean > safe_mean and perm_p < 0.05:
        passed = True
        verdict_detail = f"HT elevated {enrichment:.1f}x at dangerous positions (p={perm_p:.4f})"
    elif danger_mean > safe_mean:
        verdict_detail = f"HT elevated {enrichment:.2f}x but not significant (p={perm_p:.4f})"
    else:
        verdict_detail = f"No HT elevation at dangerous positions (effect reversed)"

    print(f"\nTest PASS criterion: Dangerous HT > Safe HT, permutation p < 0.05")
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    print(f"Detail: {verdict_detail}")
    print()

    # Save results
    results = {
        "test": "T9_danger_ht_correlation",
        "hypothesis": "Puff dangerous materials correlate with higher HT density",
        "reference_constraint": "C459 (HT as anticipatory compensation)",
        "data": {
            "dangerous_positions": list(dangerous_positions),
            "dangerous_n": len(dangerous_ht),
            "safe_n": len(safe_ht),
            "dangerous_ht_values": dangerous_ht,
            "dangerous_mean": round(danger_mean, 4),
            "dangerous_std": round(danger_std, 4),
            "safe_mean": round(safe_mean, 4),
            "safe_std": round(safe_std, 4),
        },
        "statistics": {
            "enrichment": round(enrichment, 4) if danger_mean > safe_mean else round(-1/enrichment, 4),
            "mann_whitney_u": u_stat,
            "mann_whitney_p": p_value,
            "permutation_p": round(perm_p, 4),
            "observed_difference": round(observed_diff, 4),
        },
        "verdict": {
            "passed": passed,
            "detail": verdict_detail,
            "interpretation": "HT anticipatory compensation is/is not elevated for dangerous materials"
        }
    }

    with open(RESULTS_DIR / "puff_danger_ht_test.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: results/puff_danger_ht_test.json")

    return results

if __name__ == "__main__":
    run_test()
