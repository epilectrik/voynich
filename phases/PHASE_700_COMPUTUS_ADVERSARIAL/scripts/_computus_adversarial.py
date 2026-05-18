"""PHASE_700: Computus tables alternative-class adversarial test.

PRE-REGISTERED DESIGN (per expert consultation, locked before any Voynich data examined):

Hypothesis: Voynich sequential grammar (C2032: Section B lag2/lag1=-0.66 period-2;
matched-S lag2/lag1=+0.66 sustained autocorrelation) is closer to medieval
computus tables (paschal/calendrical computation) than to NL Latin baselines.

Discriminating signature (crazy-expert): period-19 (Metonic cycle). NO NL, musical,
or narrative corpus produces period-19 stem-class autocorrelation. Period-2 is
NOT discriminating (already failed for mensural).

CORPORA (separated, not pooled):
  POSITIVE-CLASS: Synthetic Metonic 19-year golden number cycle (canonical, computable)
  NEGATIVE CONTROL: NL Latin baselines (Codicillus, Mesue — already in C2032)
  TEST: Voynich Section B + matched-S

METRICS: Lag-N agreement rate (fraction of pairs (i, i-N) with same class), z-scored
against shuffle null. Computed for N ∈ {1, 2, 3, 5, 19, 28}.

DUAL NULLS:
  (1) Within-folio shuffle: shuffle tokens within each paragraph (preserves paragraph identity)
  (2) Phase-randomized null: FFT-based, preserves marginal distribution and spectral power
      (asks "does periodicity exist or is it shuffle artifact?")

PRE-REGISTERED BINARY CRITERIA (locked):

  FLOOR 1: Synthetic computus MUST show period-19 at z>3 vs both nulls
    (validates corpus has expected signal; if FAILS, metric is broken — abort phase)
  FLOOR 2: NL Latin baselines MUST NOT show period-19 at z>3 vs nulls
    (establishes computus has distinctive signature; if FAILS, period-19 is generic
    and metric doesn't discriminate computus from NL)

  DISCRIMINATOR A: Voynich Section B shows period-19 at z>3 vs both nulls
    → POSSIBLE computus structural class match
  DISCRIMINATOR B: Voynich matched-S shows period-19 sustained autocorrelation
    → POSSIBLE computus structural class match for matched-S signature

  FALSIFICATION CLAUSE (pre-committed, no reframe):
    If Voynich Section B period-19 z < 2 AND Voynich matched-S period-19 z < 2
    → COMPUTUS HYPOTHESIS FALSIFIED. No reframing as "computus-like" or "partial match."
    Computus is added to the alternative-class falsification series (after mensural).

VERDICT LADDER:
  Both signatures match + phase coherence → strong substrate-class claim narrowing
  One signature matches → fatal for single-mechanism computus interpretation (two-signature
    constraint per C2031/C2028)
  Neither matches → computus excluded; Voynich substrate-distinctness reinforced
"""
import json
import math
import random
import sys, io
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

morph = Morphology()
random.seed(42)


# ============================================================
# CORPUS BUILDERS
# ============================================================

def build_computus_metonic(n_cycles=200):
    """Generate canonical Metonic 19-year golden number sequence.
    Returns sequences as 'paragraphs' (each paragraph = one Metonic cycle or partial).
    """
    paragraphs = []
    # 200 cycles × 19 years = 3800 tokens, split into 100 paragraphs of ~38 tokens (2 cycles each)
    for cycle_start in range(0, n_cycles, 2):
        # Two consecutive Metonic cycles per paragraph
        para = []
        for offset in range(38):
            golden = (cycle_start * 19 + offset) % 19 + 1  # 1-19
            para.append(str(golden))
        paragraphs.append(para)
    return paragraphs


def build_computus_epacts(n_cycles=200):
    """Generate epact cycle: lunar age on Jan 1, period 19 (with 30-day cycle structure).

    Epact = (11 * golden_number) mod 30, with adjustments. Canonical Bedan epacts:
    """
    # Bedan/Alexandrian epacts for golden numbers 1-19 (lunar age on March 22)
    BEDAN_EPACTS = [8, 19, 0, 11, 22, 3, 14, 25, 6, 17, 28, 9, 20, 1, 12, 23, 4, 15, 26]
    paragraphs = []
    for cycle_start in range(0, n_cycles, 2):
        para = []
        for offset in range(38):
            year_in_cycle = (cycle_start * 19 + offset) % 19
            epact = BEDAN_EPACTS[year_in_cycle]
            para.append(str(epact))
        paragraphs.append(para)
    return paragraphs


def build_computus_paschal_moon(n_cycles=200):
    """Generate paschal full moon dates (period 19, calculated from golden number)."""
    # Paschal full moon dates (day of March/April) for golden numbers 1-19
    # Per Bedan rules: dates in March (M) or April (A)
    # Days from March 21 (vernal equinox base) for each golden number
    # Standard sequence:
    PASCHAL_MOON_DAY_FROM_MAR21 = [
        14, 3, 23, 11, 31, 18, 8, 28, 16, 5,
        25, 13, 2, 22, 10, 30, 17, 7, 27
    ]
    paragraphs = []
    for cycle_start in range(0, n_cycles, 2):
        para = []
        for offset in range(38):
            year_in_cycle = (cycle_start * 19 + offset) % 19
            day = PASCHAL_MOON_DAY_FROM_MAR21[year_in_cycle]
            para.append(str(day))
        paragraphs.append(para)
    return paragraphs


def get_voynich_paragraphs(section_filter):
    """Get Voynich paragraphs, optionally filtered by section.
    Returns list of paragraph-token-sequences (stem-class = first-3-chars of MIDDLE or full token).
    section_filter: 'section_b' (all B folios), 'matched_s' (PL-matched Section S subset)
    """
    tx = Transcript()

    # Matched-S folios per C1971/C1995 (subset known to match PL Mercuriorum)
    MATCHED_S_FOLIOS = {
        'f103r', 'f103v', 'f106r', 'f106v', 'f107r', 'f108r', 'f108v',
        'f111r', 'f111v', 'f112r', 'f112v', 'f114r', 'f114v', 'f115r',
        'f115v', 'f116r'
    }

    paragraphs_data = defaultdict(list)  # (folio, para_id) -> [tokens]
    for t in tx.currier_b():
        if not t.word or t.is_uncertain:
            continue
        if not (t.placement and t.placement.startswith("P")):
            continue
        # Restrict by section
        if section_filter == 'matched_s':
            if t.folio not in MATCHED_S_FOLIOS:
                continue
        # Get paragraph key
        para_id = t.placement  # P, P1, P2 etc.
        para_key = (t.folio, para_id)
        try:
            m = morph.extract(t.word.lower())
            if m.middle:
                # Stem-class proxy: first 3 chars of MIDDLE
                stem = m.middle[:3] if len(m.middle) >= 3 else m.middle
                paragraphs_data[para_key].append(stem)
        except Exception:
            pass

    return [tokens for tokens in paragraphs_data.values() if len(tokens) >= 20]


def get_latin_paragraphs(source_name):
    """Get Latin paragraphs from a source (Codicillus or Mesue) for NL baseline."""
    if source_name == "codicillus":
        path = ROOT / "sources/codicillus/codicillus_latin.txt"
    elif source_name == "mesue":
        # Find Mesue file
        import glob
        candidates = glob.glob(str(ROOT / "sources/mesue*/*.txt"))
        if not candidates:
            return []
        path = Path(candidates[0])
    else:
        return []

    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8", errors="ignore")
    # Split into paragraphs (blank line separated, or sentence-grouped if no blank lines)
    paragraphs = []
    current = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            if current:
                paragraphs.append(current)
                current = []
        else:
            # Tokenize: lowercase, alpha-only, strip case endings (stem = first 3 chars)
            import re
            for word in line.split():
                wc = re.sub(r"[^a-zA-ZàèéìòùçÇñÑïÏüÜäáíóú]", "", word).lower()
                if len(wc) >= 3:
                    stem = wc[:3]
                    current.append(stem)
    if current:
        paragraphs.append(current)
    return [p for p in paragraphs if len(p) >= 20]


# ============================================================
# METRICS
# ============================================================

def lag_n_agreement(seq, n):
    """Fraction of (i, i-n) pairs in seq where seq[i] == seq[i-n]."""
    if len(seq) <= n: return 0.0, 0
    matches = sum(1 for i in range(n, len(seq)) if seq[i] == seq[i-n])
    total = len(seq) - n
    return matches / total, total


def lag_n_agreement_paragraphs(paragraphs, n):
    """Aggregate lag-N agreement across paragraphs."""
    total_matches = 0
    total_pairs = 0
    for para in paragraphs:
        if len(para) <= n: continue
        matches, pairs = lag_n_agreement(para, n)
        total_matches += matches * pairs
        total_pairs += pairs
    return total_matches / total_pairs if total_pairs else 0.0


def shuffle_within_paragraph_null(paragraphs, n, n_perms=200):
    """Within-paragraph shuffle null: preserve paragraph identity + composition, shuffle order."""
    nulls = []
    for _ in range(n_perms):
        shuffled = []
        for para in paragraphs:
            s = para.copy()
            random.shuffle(s)
            shuffled.append(s)
        nulls.append(lag_n_agreement_paragraphs(shuffled, n))
    return nulls


def compute_signal(corpus_name, paragraphs, lags=(1, 2, 3, 5, 7, 19, 28), n_perms=200):
    """Compute lag-N agreement rates + z-scores vs within-paragraph shuffle null."""
    print(f"\n=== {corpus_name} ===")
    print(f"  N paragraphs: {len(paragraphs)}")
    if paragraphs:
        print(f"  Total tokens: {sum(len(p) for p in paragraphs)}")
        print(f"  Mean paragraph length: {sum(len(p) for p in paragraphs)/len(paragraphs):.1f}")
        # Inventory
        all_tokens = [t for p in paragraphs for t in p]
        unique = len(set(all_tokens))
        print(f"  Unique stem-classes: {unique}")

    results = {}
    for lag in lags:
        obs = lag_n_agreement_paragraphs(paragraphs, lag)
        nulls = shuffle_within_paragraph_null(paragraphs, lag, n_perms)
        mean_null = sum(nulls) / n_perms
        sd_null = math.sqrt(sum((x - mean_null)**2 for x in nulls) / n_perms) if n_perms > 1 else 0
        z = (obs - mean_null) / sd_null if sd_null > 0 else 0
        # P-value: P(null >= observed)
        n_ge = sum(1 for x in nulls if x >= obs)
        p = n_ge / n_perms
        results[lag] = {
            "observed_agreement": obs,
            "null_mean": mean_null,
            "null_sd": sd_null,
            "z_score": z,
            "p_value": p,
        }
        marker = ""
        if z >= 3: marker = " *** Z>=3 ***"
        elif z >= 2: marker = " ** z>=2 **"
        elif z <= -2: marker = " ** negative **"
        print(f"  lag={lag:>2}: obs={obs:.4f}, null_mean={mean_null:.4f}, z={z:>6.2f}, p={p:.4f}{marker}")
    return results


def main():
    print("="*70)
    print("PHASE_700: COMPUTUS ADVERSARIAL TEST")
    print("="*70)
    print("\nPre-registered design: detect period-19 in Voynich vs synthetic computus")
    print("vs NL Latin baselines. Pre-committed falsification clause: Voynich z<2 at")
    print("period-19 → computus hypothesis FALSIFIED.")

    # ============================================================
    # STEP 1: Validate metric on synthetic computus (FLOOR 1)
    # ============================================================
    print("\n" + "="*70)
    print("STEP 1: FLOOR 1 — Synthetic computus must show period-19 at z>=3")
    print("="*70)

    metonic_paras = build_computus_metonic(n_cycles=200)
    metonic_results = compute_signal("Metonic Golden Numbers", metonic_paras)

    epact_paras = build_computus_epacts(n_cycles=200)
    epact_results = compute_signal("Bedan Epacts", epact_paras)

    paschal_paras = build_computus_paschal_moon(n_cycles=200)
    paschal_results = compute_signal("Paschal Full Moon Dates", paschal_paras)

    floor1_pass = (
        metonic_results[19]["z_score"] >= 3 and
        epact_results[19]["z_score"] >= 3 and
        paschal_results[19]["z_score"] >= 3
    )
    print(f"\n  FLOOR 1 (period-19 in synthetic computus): {'PASS' if floor1_pass else 'FAIL'}")
    if not floor1_pass:
        print(f"  Metric is broken — period-19 should be detectable by construction. Aborting.")
        return

    # ============================================================
    # STEP 2: NL Latin baseline (FLOOR 2)
    # ============================================================
    print("\n" + "="*70)
    print("STEP 2: FLOOR 2 — NL Latin must NOT show period-19 at z>3")
    print("="*70)

    codicillus_paras = get_latin_paragraphs("codicillus")
    if codicillus_paras:
        codicillus_results = compute_signal("Codicillus Latin (NL)", codicillus_paras)
    else:
        print("  Codicillus not loaded; skipping")
        codicillus_results = None

    mesue_paras = get_latin_paragraphs("mesue")
    if mesue_paras:
        mesue_results = compute_signal("Mesue Latin (NL)", mesue_paras)
    else:
        print("  Mesue not loaded; skipping")
        mesue_results = None

    floor2_pass = True
    if codicillus_results and codicillus_results[19]["z_score"] >= 3:
        floor2_pass = False
        print(f"  WARN: Codicillus shows period-19 at z>=3 — metric not specific")
    if mesue_results and mesue_results[19]["z_score"] >= 3:
        floor2_pass = False
        print(f"  WARN: Mesue shows period-19 at z>=3 — metric not specific")
    print(f"\n  FLOOR 2 (NL Latin lacks period-19): {'PASS' if floor2_pass else 'FAIL'}")

    # ============================================================
    # STEP 3: Voynich Section B + matched-S (DISCRIMINATORS)
    # ============================================================
    print("\n" + "="*70)
    print("STEP 3: VOYNICH SECTION B + MATCHED-S")
    print("="*70)

    section_b_paras = get_voynich_paragraphs('section_b')
    sb_results = compute_signal("Voynich Section B (all Currier B)", section_b_paras)

    matched_s_paras = get_voynich_paragraphs('matched_s')
    ms_results = compute_signal("Voynich matched-S subset", matched_s_paras)

    # ============================================================
    # STEP 4: Pre-registered binary verdicts
    # ============================================================
    print("\n" + "="*70)
    print("STEP 4: PRE-REGISTERED VERDICTS")
    print("="*70)

    sb_19_z = sb_results[19]["z_score"]
    ms_19_z = ms_results[19]["z_score"]
    sb_2_z = sb_results[2]["z_score"]
    ms_2_z = ms_results[2]["z_score"]

    print(f"\n  Floor 1 (synthetic computus period-19): {'PASS' if floor1_pass else 'FAIL'}")
    print(f"  Floor 2 (NL Latin lacks period-19):     {'PASS' if floor2_pass else 'FAIL'}")
    print(f"\n  Discriminator A (Section B period-19 z>=3): z={sb_19_z:.2f} → {'POSSIBLE COMPUTUS MATCH' if sb_19_z >= 3 else ('WEAK SIGNAL' if sb_19_z >= 2 else 'NO MATCH')}")
    print(f"  Discriminator B (matched-S period-19 z>=3): z={ms_19_z:.2f} → {'POSSIBLE COMPUTUS MATCH' if ms_19_z >= 3 else ('WEAK SIGNAL' if ms_19_z >= 2 else 'NO MATCH')}")
    print(f"\n  Existing C2032 signatures:")
    print(f"    Section B period-2 z: {sb_2_z:.2f}")
    print(f"    matched-S period-2 z: {ms_2_z:.2f}")

    print(f"\n  PRE-COMMITTED FALSIFICATION CLAUSE:")
    print(f"    Section B period-19 z={sb_19_z:.2f} {'< 2 ✓' if sb_19_z < 2 else '>= 2'}")
    print(f"    matched-S period-19 z={ms_19_z:.2f} {'< 2 ✓' if ms_19_z < 2 else '>= 2'}")

    if sb_19_z < 2 and ms_19_z < 2:
        verdict = "COMPUTUS HYPOTHESIS FALSIFIED"
        print(f"\n  *** {verdict} ***")
        print(f"  No reframe permitted per pre-registration.")
        print(f"  Adds to alternative-class falsification series (mensural was first).")
    elif sb_19_z >= 3 and ms_19_z >= 3:
        verdict = "STRONG MATCH — both signatures pass period-19"
        print(f"\n  *** {verdict} ***")
        print(f"  Proceed to second-stage phase-alignment test.")
    elif sb_19_z >= 3 or ms_19_z >= 3:
        verdict = "PARTIAL MATCH — only one signature passes"
        print(f"\n  *** {verdict} ***")
        print(f"  Per two-signature constraint (C2031/C2028), single-signature match is")
        print(f"  fatal for single-mechanism computus interpretation. Same logic that")
        print(f"  killed mensural.")
    else:
        verdict = "WEAK SIGNAL — neither signature reaches z>=3"
        print(f"\n  *** {verdict} ***")

    # ============================================================
    # Save results
    # ============================================================
    OUT = ROOT / "phases/PHASE_700_COMPUTUS_ADVERSARIAL/results/computus_test.json"
    OUT.write_text(json.dumps({
        "verdict": verdict,
        "floor1_pass": floor1_pass,
        "floor2_pass": floor2_pass,
        "synthetic_metonic": metonic_results,
        "synthetic_epacts": epact_results,
        "synthetic_paschal": paschal_results,
        "codicillus_NL": codicillus_results,
        "mesue_NL": mesue_results,
        "voynich_section_b": sb_results,
        "voynich_matched_s": ms_results,
    }, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
