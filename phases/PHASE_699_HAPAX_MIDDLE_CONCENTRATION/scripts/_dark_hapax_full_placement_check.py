"""Check whether dark-pipeline hapax identifications are TRULY hapax across
all placement types, or if they appear elsewhere (labels, rings, etc.) that
my P-placement filter missed.

User's question: if alod names a vessel, we should see it on multiple folios.
If it's truly hapax across ALL placements (P, L, R, S, C), then it CANNOT be
a generic vessel/material name — because aludels (and other named classes)
are used on multiple folios per the project's recipe matches.
"""
import json
import sys, io
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

morph = Morphology()


def collect_all_placements():
    """Collect MIDDLE occurrences across ALL placements (no filter except H-track + non-uncertain)."""
    tx = Transcript()
    middle_folio_placement = defaultdict(list)  # middle -> [(folio, placement)]
    for t in tx.all(h_only=True):
        if not t.word or t.is_uncertain:
            continue
        if not t.placement:
            continue
        try:
            m = morph.extract(t.word.lower())
            if m.middle:
                middle_folio_placement[m.middle].append((t.folio, t.placement))
        except Exception:
            pass
    return dict(middle_folio_placement)


def main():
    # Load dark pipeline list
    dark_data = json.loads((ROOT / "data/dark_pipeline_middles.json").read_text(encoding="utf-8"))
    dark_middles = set(dark_data["middles"])

    middle_occurrences = collect_all_placements()

    # Focus on the dictionary-named hapax identifiers
    dictionary_hapax_candidates = ["alod", "fsh", "olyd", "cs", "loch", "rol", "ea"]

    print("="*70)
    print("DARK PIPELINE 'HAPAX' IDENTIFICATIONS — full-placement check")
    print("="*70)

    for m in dictionary_hapax_candidates:
        if m not in middle_occurrences:
            print(f"\n{m}: NOT FOUND in any placement across Currier corpus")
            continue
        occurrences = middle_occurrences[m]
        n_total = len(occurrences)
        folios = set(folio for folio, _ in occurrences)
        placements = Counter(p for _, p in occurrences)
        sections = set()
        # Get Currier section per folio
        # (would need section lookup — just report folio list)
        print(f"\n{m}: {n_total} total occurrences across {len(folios)} folios")
        print(f"  Placements: {dict(placements)}")
        # Show per-folio
        by_folio = defaultdict(list)
        for folio, placement in occurrences:
            by_folio[folio].append(placement)
        for folio in sorted(by_folio.keys()):
            ps = by_folio[folio]
            print(f"  {folio}: {len(ps)}× ({Counter(ps)})")

    # Now check all 78 hapax × dark pipeline overlap — how many are truly singular under broader placement?
    print(f"\n" + "="*70)
    print(f"TRUE-HAPAX AUDIT — all 78 originally-hapax dark pipeline MIDDLEs")
    print(f"="*70)

    # Re-derive my original 78 hapaxes (P-only)
    # Use the data I generated
    from collections import Counter as C
    p_only_middles = C()
    tx = Transcript()
    for t in tx.currier_b():
        if not t.word or t.is_uncertain: continue
        if not (t.placement and t.placement.startswith("P")): continue
        try:
            mm = morph.extract(t.word.lower())
            if mm.middle: p_only_middles[mm.middle] += 1
        except Exception: pass
    p_hapaxes = set(m for m, f in p_only_middles.items() if f == 1)
    hapax_dark = p_hapaxes & dark_middles

    truly_hapax_corpus_wide = 0
    multi_folio_under_broader_filter = 0
    multi_occurrence_same_folio = 0

    for m in sorted(hapax_dark):
        if m not in middle_occurrences:
            continue
        occ = middle_occurrences[m]
        folios = set(folio for folio, _ in occ)
        if len(occ) == 1:
            truly_hapax_corpus_wide += 1
        elif len(folios) > 1:
            multi_folio_under_broader_filter += 1
        else:
            multi_occurrence_same_folio += 1

    print(f"\n  Of 78 P-only hapax × dark pipeline MIDDLEs:")
    print(f"    Truly hapax corpus-wide (1 occurrence, any placement): {truly_hapax_corpus_wide}")
    print(f"    Multi-occurrence on SAME folio (1 folio, multiple placements): {multi_occurrence_same_folio}")
    print(f"    Multi-FOLIO under broader placement filter: {multi_folio_under_broader_filter}")

    # Show samples of each
    print(f"\n  --- Multi-folio (broader filter) examples ---")
    multifolio_examples = []
    for m in sorted(hapax_dark):
        if m not in middle_occurrences: continue
        occ = middle_occurrences[m]
        folios = set(folio for folio, _ in occ)
        if len(folios) > 1:
            multifolio_examples.append((m, len(occ), len(folios), Counter(p for _, p in occ)))
    multifolio_examples.sort(key=lambda x: -x[1])
    for m, n_total, n_folios, placements in multifolio_examples[:15]:
        print(f"    {m}: {n_total}× on {n_folios} folios, placements={dict(placements)}")

    print(f"\n  --- Multi-occurrence same-folio examples ---")
    sf_examples = []
    for m in sorted(hapax_dark):
        if m not in middle_occurrences: continue
        occ = middle_occurrences[m]
        folios = set(folio for folio, _ in occ)
        if len(folios) == 1 and len(occ) > 1:
            sf_examples.append((m, len(occ), Counter(p for _, p in occ)))
    sf_examples.sort(key=lambda x: -x[1])
    for m, n_total, placements in sf_examples[:10]:
        print(f"    {m}: {n_total}× on 1 folio, placements={dict(placements)}")

    OUT = ROOT / "phases/PHASE_699_HAPAX_MIDDLE_CONCENTRATION/results/dark_hapax_full_placement_audit.json"
    OUT.write_text(json.dumps({
        "n_p_only_hapax_in_dark": len(hapax_dark),
        "truly_hapax_corpus_wide": truly_hapax_corpus_wide,
        "multi_occurrence_same_folio": multi_occurrence_same_folio,
        "multi_folio_under_broader_filter": multi_folio_under_broader_filter,
        "dictionary_identifiers_full_placement": {
            m: {"n_total": len(middle_occurrences.get(m, [])),
                "folios": list(set(f for f, _ in middle_occurrences.get(m, []))),
                "placements": dict(Counter(p for _, p in middle_occurrences.get(m, [])))}
            for m in dictionary_hapax_candidates
        },
    }, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
