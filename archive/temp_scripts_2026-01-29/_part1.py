#!/usr/bin/env python3
"""
Line Type Comparison: PP-pure vs RI-bearing lines in Currier A

Hypothesis: PP-pure lines (ri_count == 0) and RI-bearing lines (ri_count > 0)
serve different structural roles:
  - PP-pure lines: toolbox / compatibility context lines
  - RI-bearing lines: product entry lines with specific identifiers
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology, RecordAnalyzer

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def shannon_entropy(counter):
    """Compute Shannon entropy from a Counter."""
    total = sum(counter.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counter.values() if c > 0]
    return -sum(p * math.log2(p) for p in probs)


def mw_report(a, b, la, lb, name):
    """Run Mann-Whitney U test and return structured report."""
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    r = {}
    r["metric"] = name
    r["group_a"] = la
    r["group_b"] = lb
    r["n_a"] = len(a)
    r["n_b"] = len(b)
    r["mean_a"] = float(np.mean(a)) if len(a) > 0 else None
    r["mean_b"] = float(np.mean(b)) if len(b) > 0 else None
    r["median_a"] = float(np.median(a)) if len(a) > 0 else None
    r["median_b"] = float(np.median(b)) if len(b) > 0 else None
    r["std_a"] = float(np.std(a, ddof=1)) if len(a) > 1 else None
    r["std_b"] = float(np.std(b, ddof=1)) if len(b) > 1 else None
    if len(a) > 0 and len(b) > 0:
        stat, pval = stats.mannwhitneyu(a, b, alternative="two-sided")
        r["U_statistic"] = float(stat)
        r["p_value"] = float(pval)
        n1n2 = len(a) * len(b)
        r["rank_biserial"] = float(1 - 2 * stat / n1n2) if n1n2 > 0 else None
        ps = math.sqrt(
            ((len(a)-1)*np.var(a, ddof=1) + (len(b)-1)*np.var(b, ddof=1))
            / (len(a) + len(b) - 2)
        ) if (len(a) + len(b)) > 2 else 1.0
        r["cohens_d"] = float((np.mean(a) - np.mean(b)) / ps) if ps > 0 else None
    else:
        r["U_statistic"] = None
        r["p_value"] = None
        r["rank_biserial"] = None
        r["cohens_d"] = None
    return r

def main():
    print("=" * 70)
    print("LINE TYPE COMPARISON: PP-pure vs RI-bearing in Currier A")
    print("=" * 70)

    analyzer = RecordAnalyzer()
    folios = analyzer.get_folios()

    # Collect all records
    all_records = []
    folio_records = defaultdict(list)
    for folio in folios:
        records = analyzer.analyze_folio(folio)
        for rec in records:
            if len(rec.tokens) > 0:
                all_records.append(rec)
                folio_records[folio].append(rec)

    # Partition into PP-pure and RI-bearing
    pp_pure = [rec for rec in all_records if rec.ri_count == 0]
    ri_bearing = [rec for rec in all_records if rec.ri_count > 0]

    print("")
    print("Total lines: %d" % len(all_records))
    print("PP-pure lines (ri_count == 0): %d (%.1f%%)" % (
        len(pp_pure), 100*len(pp_pure)/len(all_records)))
    print("RI-bearing lines (ri_count > 0): %d (%.1f%%)" % (
        len(ri_bearing), 100*len(ri_bearing)/len(all_records)))

    results = {
        "summary": {
            "total_lines": len(all_records),
            "pp_pure_count": len(pp_pure),
            "ri_bearing_count": len(ri_bearing),
            "pp_pure_pct": round(100 * len(pp_pure) / len(all_records), 2),
            "ri_bearing_pct": round(100 * len(ri_bearing) / len(all_records), 2),
            "total_folios": len(folios),
        },
        "tests": {}
    }

    # ==================================================================
    # TEST 1: Token count comparison
    # ==================================================================
    print("")
    print("-" * 70)
    print("TEST 1: Token Count per Line")
    print("-" * 70)

    pp_len = [len(rec.tokens) for rec in pp_pure]
    ri_len = [len(rec.tokens) for rec in ri_bearing]

    t1 = mw_report(pp_len, ri_len, "PP-pure", "RI-bearing", "tokens_per_line")
    print("  PP-pure:    mean=%.2f, median=%.1f, std=%.2f" % (
        t1["mean_a"], t1["median_a"], t1["std_a"]))
    print("  RI-bearing: mean=%.2f, median=%.1f, std=%.2f" % (
        t1["mean_b"], t1["median_b"], t1["std_b"]))
    print("  Mann-Whitney U=%.0f, p=%.2e" % (t1["U_statistic"], t1["p_value"]))
    print("  Cohen d=%.3f, rank-biserial r=%.3f" % (t1["cohens_d"], t1["rank_biserial"]))
    results["tests"]["token_count"] = t1

    # ==================================================================
    # TEST 2: PP token density
    # ==================================================================
    print("")
    print("-" * 70)
    print("TEST 2: PP Token Density")
    print("-" * 70)

    t2a = mw_report(
        [rec.pp_count for rec in pp_pure],
        [rec.pp_count for rec in ri_bearing],
        "PP-pure", "RI-bearing", "pp_tokens_per_line"
    )
    print("  PP tokens per line:")
    print("    PP-pure:    mean=%.2f, median=%.1f" % (t2a["mean_a"], t2a["median_a"]))
    print("    RI-bearing: mean=%.2f, median=%.1f" % (t2a["mean_b"], t2a["median_b"]))
    print("    Mann-Whitney p=%.2e, Cohen d=%.3f" % (t2a["p_value"], t2a["cohens_d"]))

    pp_frac = [rec.pp_count / len(rec.tokens) if len(rec.tokens) > 0 else 0
               for rec in pp_pure]
    ri_frac = [rec.pp_count / len(rec.tokens) if len(rec.tokens) > 0 else 0
               for rec in ri_bearing]

    t2b = mw_report(pp_frac, ri_frac, "PP-pure", "RI-bearing", "pp_fraction")
    print("  PP fraction:")
    print("    PP-pure:    mean=%.3f" % t2b["mean_a"])
    print("    RI-bearing: mean=%.3f" % t2b["mean_b"])
    print("    Mann-Whitney p=%.2e, Cohen d=%.3f" % (t2b["p_value"], t2b["cohens_d"]))
    results["tests"]["pp_density_absolute"] = t2a
    results["tests"]["pp_density_fraction"] = t2b

    # ==================================================================
    # TEST 3: INFRA (DA-family) content
    # ==================================================================
    print("")
    print("-" * 70)
    print("TEST 3: INFRA (DA-family) Content")
    print("-" * 70)

    t3a = mw_report(
        [rec.infra_count for rec in pp_pure],
        [rec.infra_count for rec in ri_bearing],
        "PP-pure", "RI-bearing", "infra_tokens_per_line"
    )
    print("  INFRA tokens per line:")
    print("    PP-pure:    mean=%.2f, median=%.1f" % (t3a["mean_a"], t3a["median_a"]))
    print("    RI-bearing: mean=%.2f, median=%.1f" % (t3a["mean_b"], t3a["median_b"]))
    print("    Mann-Whitney p=%.2e, Cohen d=%.3f" % (t3a["p_value"], t3a["cohens_d"]))

    ifrac_pp = [rec.infra_count / len(rec.tokens) if len(rec.tokens) > 0 else 0
                for rec in pp_pure]
    ifrac_ri = [rec.infra_count / len(rec.tokens) if len(rec.tokens) > 0 else 0
                for rec in ri_bearing]

    t3b = mw_report(ifrac_pp, ifrac_ri, "PP-pure", "RI-bearing", "infra_fraction")
    print("  INFRA fraction:")
    print("    PP-pure:    mean=%.3f" % t3b["mean_a"])
    print("    RI-bearing: mean=%.3f" % t3b["mean_b"])
    print("    Mann-Whitney p=%.2e, Cohen d=%.3f" % (t3b["p_value"], t3b["cohens_d"]))
    results["tests"]["infra_absolute"] = t3a
    results["tests"]["infra_fraction"] = t3b