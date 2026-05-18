"""PHASE_699 follow-up: Hapax × Dark-Pipeline overlap test.

Question: are any hapax MIDDLEs in the established 300 dark-pipeline (C1137,
C1140 four-way partition)?

If many hapaxes overlap with dark pipeline:
  → Hapax cohort contains a small but specific lexical-content subset.
  → Crazy-expert's "lexical content tail" hypothesis is partially right
    (some lexical content lives at hapax frequency, not just at n_4_10).

If few hapaxes overlap:
  → Original framework holds: hapaxes are operational productive tail; dark
    pipeline (lexical content) is at frequency 3-60, NOT at hapax.

Also: verify the dictionary's folio-exclusive material identifiers (loch, rol,
ea, fsh, alod, olyd) — what are their actual corpus frequencies?
"""
import json
import sys
import io
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

morph = Morphology()


def collect_middle_data():
    tx = Transcript()
    middle_folio = defaultdict(lambda: Counter())
    for t in tx.currier_b():
        if not t.word or t.is_uncertain:
            continue
        if not (t.placement and t.placement.startswith("P")):
            continue
        try:
            m = morph.extract(t.word.lower())
            if m.middle:
                middle_folio[m.middle][t.folio] += 1
        except Exception:
            pass
    return dict(middle_folio)


def main():
    # Load dark pipeline MIDDLEs
    dark_data = json.loads((ROOT / "data/dark_pipeline_middles.json").read_text(encoding="utf-8"))
    dark_middles = set(dark_data["middles"])
    print(f"Dark pipeline MIDDLEs (per C1137/C1140): {len(dark_middles)}")

    # Load MIDDLE-folio data
    middle_folio = collect_middle_data()
    print(f"Currier B MIDDLE inventory: {len(middle_folio)}")

    # Compute frequencies for each MIDDLE
    middle_freq = {m: sum(fc.values()) for m, fc in middle_folio.items()}
    middle_n_folios = {m: len(fc) for m, fc in middle_folio.items()}

    # =================================================================
    # 1. Dark pipeline coverage in PP-track
    # =================================================================
    dark_present_in_b = [m for m in dark_middles if m in middle_freq]
    dark_absent_in_b = [m for m in dark_middles if m not in middle_freq]
    print(f"\nDark pipeline MIDDLEs present in current Currier B H-track + P-placement: {len(dark_present_in_b)}/{len(dark_middles)}")
    print(f"Dark pipeline MIDDLEs absent: {len(dark_absent_in_b)}")
    if dark_absent_in_b[:10]:
        print(f"  First 10 absent: {dark_absent_in_b[:10]}")
        print(f"  (These may have been catalogued under different placement filters / pre-cleanup data)")

    # =================================================================
    # 2. Hapax × Dark Pipeline Overlap
    # =================================================================
    hapax_middles = set(m for m, f in middle_freq.items() if f == 1)
    print(f"\nHapax MIDDLEs (n=1) in current data: {len(hapax_middles)}")
    hapax_dark_overlap = hapax_middles & dark_middles
    hapax_not_dark = hapax_middles - dark_middles
    dark_not_hapax = dark_middles - hapax_middles - set(dark_absent_in_b)
    print(f"\n=== KEY OVERLAP ===")
    print(f"  Hapax ∩ Dark Pipeline: {len(hapax_dark_overlap)}")
    print(f"  Hapax NOT in Dark Pipeline: {len(hapax_not_dark)} ({100*len(hapax_not_dark)/len(hapax_middles):.1f}%)")
    print(f"  Dark Pipeline NOT hapax (present in B): {len(dark_not_hapax)}")

    if hapax_dark_overlap:
        print(f"\n=== HAPAX MIDDLES THAT ARE IN DARK PIPELINE ===")
        for m in sorted(hapax_dark_overlap):
            folio = list(middle_folio[m].keys())[0]
            print(f"  {m}: appears 1× on {folio}")

    # =================================================================
    # 3. Where in the frequency distribution does the dark pipeline live?
    # =================================================================
    dark_freqs = [middle_freq[m] for m in dark_present_in_b]
    print(f"\n=== DARK PIPELINE FREQUENCY DISTRIBUTION ===")
    print(f"  Total dark pipeline MIDDLEs (present in B): {len(dark_present_in_b)}")
    print(f"  Frequency band counts:")
    bands = [(1, "n=1 (hapax)"), (2, "n=2"), (3, "n=3"), (4, "n=4-5"), (6, "n=6-10"), (11, "n=11-30"), (31, "n=31+")]
    for i, (low, label) in enumerate(bands):
        if i+1 < len(bands):
            high = bands[i+1][0]
            count = sum(1 for f in dark_freqs if low <= f < high)
        else:
            count = sum(1 for f in dark_freqs if f >= low)
        print(f"    {label}: {count}")
    print(f"  Mean dark pipeline frequency: {sum(dark_freqs)/len(dark_freqs):.2f}")
    print(f"  Median dark pipeline frequency: {sorted(dark_freqs)[len(dark_freqs)//2]}")

    # =================================================================
    # 4. Folio-exclusive dark pipeline MIDDLEs
    # =================================================================
    print(f"\n=== FOLIO-EXCLUSIVE DARK PIPELINE MIDDLES (n_folios=1) ===")
    dark_folio_exclusive = [m for m in dark_present_in_b if middle_n_folios[m] == 1]
    print(f"  Total folio-exclusive: {len(dark_folio_exclusive)}/{len(dark_present_in_b)}")
    # For each, show frequency and folio
    print(f"\n  Folio-exclusive dark MIDDLEs (sample):")
    for m in sorted(dark_folio_exclusive, key=lambda x: -middle_freq[x])[:25]:
        f = middle_freq[m]
        folio = list(middle_folio[m].keys())[0]
        hapax_flag = " [HAPAX]" if f == 1 else ""
        print(f"    {m}: {f}× on {folio}{hapax_flag}")

    # =================================================================
    # 5. Specific dictionary identifiers
    # =================================================================
    dict_identifiers = {
        "loch": "f82r (lunaria moisture)",
        "rol": "f76v (tincture ferment)",
        "ea": "f112r (ruby liquor)",
        "fsh": "f83r (lute compound)",
        "alod": "f108r (aludel ash-phase vessel)",
        "olyd": "f81v (gold solution)",
        "fch": "mercury (corpus-wide marker)",
        "cs": "gold (corpus-wide marker)",
        "eckh": "volatile liquid",
        "lch": "distillation apparatus",
        "lk": "fire state",
    }
    print(f"\n=== DICTIONARY IDENTIFIERS — actual corpus frequency ===")
    for m, desc in dict_identifiers.items():
        if m in middle_freq:
            f = middle_freq[m]
            nf = middle_n_folios[m]
            is_hapax = " [HAPAX]" if f == 1 else ""
            is_dark = " [DARK]" if m in dark_middles else " [NOT-DARK?]"
            print(f"  {m} ({desc}): {f}× on {nf} folios{is_hapax}{is_dark}")
        else:
            print(f"  {m} ({desc}): NOT PRESENT in current Currier B P-placement data")

    # =================================================================
    # 6. Reframing summary
    # =================================================================
    print(f"\n" + "="*70)
    print(f"REFRAMING SUMMARY")
    print(f"="*70)
    print(f"""
Hapax cohort: {len(hapax_middles)} unique MIDDLEs
  └─ In dark pipeline: {len(hapax_dark_overlap)} ({100*len(hapax_dark_overlap)/len(hapax_middles):.1f}%)
  └─ NOT in dark pipeline: {len(hapax_not_dark)} ({100*len(hapax_not_dark)/len(hapax_middles):.1f}%)

Dark pipeline cohort: {len(dark_present_in_b)} MIDDLEs (in B P-placement)
  └─ Hapax (n=1): {len(hapax_dark_overlap)} ({100*len(hapax_dark_overlap)/len(dark_present_in_b):.1f}%)
  └─ Non-hapax (n>=2): {len(dark_not_hapax)} ({100*len(dark_not_hapax)/len(dark_present_in_b):.1f}%)

If hapax∩dark is small: dark pipeline mostly lives at n>=2 frequency, hapax
cohort is largely operational tail (not lexical).

If hapax∩dark is large: hapax cohort contains a substantial dark-pipeline
subset — the lexical layer extends into the hapax frequency range.
""")

    OUT = ROOT / "phases/PHASE_699_HAPAX_MIDDLE_CONCENTRATION/results/hapax_dark_pipeline_overlap.json"
    OUT.write_text(json.dumps({
        "method": "Hapax × Dark Pipeline overlap test (PHASE_699 follow-up)",
        "n_dark_pipeline_total": len(dark_middles),
        "n_dark_pipeline_in_current_B": len(dark_present_in_b),
        "n_hapax_middles": len(hapax_middles),
        "n_hapax_dark_overlap": len(hapax_dark_overlap),
        "n_hapax_not_dark": len(hapax_not_dark),
        "n_dark_not_hapax": len(dark_not_hapax),
        "hapax_dark_overlap_list": sorted(hapax_dark_overlap),
        "dark_pipeline_freq_mean": sum(dark_freqs)/len(dark_freqs) if dark_freqs else 0,
        "dark_pipeline_freq_median": sorted(dark_freqs)[len(dark_freqs)//2] if dark_freqs else 0,
        "dictionary_identifier_frequencies": {
            m: {"freq": middle_freq.get(m, 0), "n_folios": middle_n_folios.get(m, 0),
                "is_hapax": middle_freq.get(m, 0) == 1, "is_dark": m in dark_middles,
                "folios": list(middle_folio.get(m, {}).keys())[:5]}
            for m, _ in dict_identifiers.items()
        },
        "n_dark_folio_exclusive": len(dark_folio_exclusive),
        "dark_folio_exclusive_sample": [{"middle": m, "freq": middle_freq[m],
                                          "folio": list(middle_folio[m].keys())[0],
                                          "is_hapax": middle_freq[m] == 1}
                                         for m in sorted(dark_folio_exclusive, key=lambda x: -middle_freq[x])[:30]],
    }, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
