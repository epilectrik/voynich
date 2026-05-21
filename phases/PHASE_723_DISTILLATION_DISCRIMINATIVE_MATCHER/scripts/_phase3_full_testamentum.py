"""PHASE_723 Phase 3: Apply distillation-discriminative features to full
Pseudo-Lull Testamentum (~104k words). Test if signature matches Codicillus
baseline established in Phase 1-2.

Pre-registered: full Testamentum should show discrimination_score in the
Codicillus range (+0.005 to +0.025) if features generalize beyond Codicillus
subset. If it's much lower, the Codicillus signature is a subset-specific
property. If it's much higher, the full corpus is even more operational-recipe
dense than Codicillus alone.

Also tested: Mesue Grabadin (pharmacy) as additional class. Pharmacy uses some
distillation/apparatus vocabulary but its compounds are different from alchemy.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from statistics import mean, median, stdev

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
OUT_PATH = ROOT / 'phases' / 'PHASE_723_DISTILLATION_DISCRIMINATIVE_MATCHER' / 'results' / 'phase3_testamentum.json'

# Reuse feature definitions from v1
sys.path.insert(0, str(ROOT / 'phases' / 'PHASE_723_DISTILLATION_DISCRIMINATIVE_MATCHER' / 'scripts'))
from _distillation_matcher_v1 import (
    DISTILLATION_MARKERS, METALWORK_MARKERS, EXCLUDED_AMBIGUOUS,
    has_marker, score_paragraph, load_paragraphs, analyze_corpus,
    mann_whitney_u,
)


def load_mesue_paragraphs():
    """Mesue uses §-tag format per shared_628.py. Parse accordingly."""
    p = ROOT / 'sources' / 'mesue_grabadin' / 'mesue_grabadin_liber_primus.txt'
    if not p.exists():
        return []
    text = p.read_text(encoding='utf-8', errors='replace')
    paragraphs = []
    for line in text.split('\n'):
        if not line.strip() or line.startswith('#'):
            continue
        m = re.match(r"^§\d+\t(.+)$", line)
        if m:
            words = re.findall(r"\b[a-zA-Z]+\b", m.group(1))
            if 15 <= len(words) <= 80:
                paragraphs.append([w.lower() for w in words])
    return paragraphs


def main():
    print("=" * 90)
    print("PHASE_723 PHASE 3: Full Testamentum + Mesue")
    print("=" * 90)

    # Load FULL Pseudo-Lull Testamentum
    print("\n[Loading full Pseudo-Lull Testamentum at 15-80 paragraph filter]")
    pl = load_paragraphs(
        ROOT / 'sources' / 'pseudo_lull_testamentum' / 'testamentum_complete_latin.txt'
    )
    print(f"  Full Testamentum: {len(pl)} paragraphs")

    # Also load Codicillus + Theophilus for reference comparison
    cod = load_paragraphs(ROOT / 'sources' / 'codicillus' / 'codicillus_complete_latin.txt')
    print(f"  Codicillus (reference): {len(cod)} paragraphs")

    theo_text = (ROOT / 'sources' / 'theophilus' / 'theophilus_hendrie_1847.txt').read_text(
        encoding='utf-8', errors='replace'
    )
    theo_lines = theo_text.split('\n')
    theo_body = []
    theo_body.extend(theo_lines[2242:4283])
    theo_body.extend(theo_lines[7213:9147])
    theo_body.extend(theo_lines[10537:11337])
    theo_paras = []
    current = []
    for line in theo_body:
        if not line.strip():
            if current:
                words = re.findall(r"\b[a-zA-Z]+\b", " ".join(current))
                if 15 <= len(words) <= 80:
                    theo_paras.append([w.lower() for w in words])
                current = []
        else:
            current.append(line.strip())
    if current:
        words = re.findall(r"\b[a-zA-Z]+\b", " ".join(current))
        if 15 <= len(words) <= 80:
            theo_paras.append([w.lower() for w in words])
    print(f"  Theophilus body (reference): {len(theo_paras)} paragraphs")

    # Mesue (pharmacy, additional class)
    mesue = load_mesue_paragraphs()
    print(f"  Mesue Grabadin (pharmacy): {len(mesue)} paragraphs")

    # Analyze each corpus
    print("\n[Computing distillation/metalwork scores]")
    pl_r = analyze_corpus('Pseudo-Lull Testamentum (FULL)', pl, 'distillation')
    cod_r = analyze_corpus('Codicillus (subset, reference)', cod, 'distillation')
    theo_r = analyze_corpus('Theophilus body (reference)', theo_paras, 'metalwork')
    mesue_r = analyze_corpus('Mesue Grabadin', mesue, 'pharmacy')

    # Summary
    print("\n" + "=" * 95)
    print("SIGNATURE TABLE")
    print("=" * 95)
    print(f"\n{'Corpus':<35}{'class':<14}{'n_paras':>10}{'dist_score':>14}"
          f"{'metal_score':>14}{'discrim_score':>16}")
    print("-" * 103)
    for r in [pl_r, cod_r, theo_r, mesue_r]:
        if 'error' in r:
            print(f"{r['label']:<35} ERROR")
            continue
        print(f"{r['label']:<35}{r['expected_class']:<14}{r['n_paragraphs']:>10}"
              f"{r['distillation_score_mean']:>+14.5f}"
              f"{r['metalwork_score_mean']:>+14.5f}"
              f"{r['discrimination_score_mean']:>+16.5f}")

    print("\nRaw marker hits:")
    for r in [pl_r, cod_r, theo_r, mesue_r]:
        if 'error' in r:
            continue
        dist_per_1k = 1000 * r['total_distillation_hits'] / max(r['total_words'], 1)
        metal_per_1k = 1000 * r['total_metalwork_hits'] / max(r['total_words'], 1)
        print(f"  {r['label']:<35} dist={r['total_distillation_hits']:>5} "
              f"({dist_per_1k:.2f}/1k)  metal={r['total_metalwork_hits']:>5} "
              f"({metal_per_1k:.2f}/1k)  total_words={r['total_words']}")

    # Pre-registered Phase 3 criteria
    print("\n" + "=" * 95)
    print("PRE-REGISTERED PHASE 3 CRITERIA")
    print("=" * 95)
    pl_disc = pl_r['discrimination_score_mean']
    cod_disc = cod_r['discrimination_score_mean']
    theo_disc = theo_r['discrimination_score_mean']

    # P3-C1: Full Testamentum discrimination_score > +0.005 (in distillation range)
    p3_c1_pass = pl_disc > +0.005
    print(f"\n  P3-C1: Full Testamentum discrimination > +0.005? "
          f"({pl_disc:+.5f}) → {'PASS' if p3_c1_pass else 'FAIL'}")

    # P3-C2: Full Testamentum within reasonable distance of Codicillus subset
    delta_cod = abs(pl_disc - cod_disc)
    p3_c2_pass = delta_cod < 0.020
    print(f"  P3-C2: |Full Testamentum - Codicillus subset| < 0.020? "
          f"({delta_cod:.5f}) → {'PASS' if p3_c2_pass else 'FAIL'}")

    # P3-C3: Full Testamentum vs Theophilus separation significant
    u_pl_theo, p_pl_theo = mann_whitney_u(
        pl_r['discrimination_scores'], theo_r['discrimination_scores']
    )
    p3_c3_pass = p_pl_theo < 0.01
    print(f"  P3-C3: Full Testamentum vs Theophilus Mann-Whitney p < 0.01? "
          f"(U={u_pl_theo:.1f}, p={p_pl_theo:.5f}) → {'PASS' if p3_c3_pass else 'FAIL'}")

    n_pass_p3 = sum([p3_c1_pass, p3_c2_pass, p3_c3_pass])
    print(f"\n  PHASE 3 PASS COUNT: {n_pass_p3}/3")

    if n_pass_p3 == 3:
        verdict_p3 = "PHASE 3 PASSES — features generalize from Codicillus subset to full Testamentum; matcher is corpus-portable"
    elif n_pass_p3 == 2:
        verdict_p3 = "PHASE 3 PARTIAL — features partially generalize"
    else:
        verdict_p3 = "PHASE 3 FAILS — features may be Codicillus-subset-specific"

    print(f"\n  VERDICT: {verdict_p3}")

    # Pharmacy interpretation
    if 'error' not in mesue_r:
        mesue_disc = mesue_r['discrimination_score_mean']
        print(f"\n[Mesue pharmacy as additional class]:")
        print(f"  Mesue discrimination_score: {mesue_disc:+.5f}")
        if mesue_disc > +0.005:
            mesue_class = "DISTILLATION-LIKE (pharmacy uses distillation apparatus)"
        elif mesue_disc < -0.005:
            mesue_class = "METALWORK-LIKE (unexpected for pharmacy)"
        else:
            mesue_class = "NEUTRAL (pharmacy uses neither distillation nor metalwork heavily)"
        print(f"  Pharmacy classifies as: {mesue_class}")

    # Top distillation-dense paragraphs from full Testamentum
    print("\n" + "=" * 95)
    print("QUALITATIVE: Top distillation-dense paragraphs from full Testamentum")
    print("=" * 95)
    pl_scored = list(zip(pl_r['discrimination_scores'], range(len(pl))))
    pl_scored.sort(key=lambda x: -x[0])
    for s, idx in pl_scored[:5]:
        snippet = ' '.join(pl[idx][:18])
        print(f"  score={s:+.4f}: {snippet}...")

    print("\nBottom (most metalwork-like) paragraphs from full Testamentum:")
    for s, idx in pl_scored[-5:]:
        snippet = ' '.join(pl[idx][:18])
        print(f"  score={s:+.4f}: {snippet}...")

    # Save
    out = {
        'method': 'PHASE_723 Phase 3 full Testamentum + Mesue',
        'results': {
            'full_testamentum': {k: v for k, v in pl_r.items() if k != 'discrimination_scores'},
            'codicillus_reference': {k: v for k, v in cod_r.items() if k != 'discrimination_scores'},
            'theophilus_reference': {k: v for k, v in theo_r.items() if k != 'discrimination_scores'},
            'mesue_pharmacy': {k: v for k, v in mesue_r.items() if k != 'discrimination_scores'},
        },
        'phase3_criteria': {
            'p3_c1_full_testamentum_pos': {'observed': pl_disc, 'pass': p3_c1_pass},
            'p3_c2_close_to_codicillus': {'observed': delta_cod, 'pass': p3_c2_pass},
            'p3_c3_separates_from_theophilus': {'u': u_pl_theo, 'p': p_pl_theo, 'pass': p3_c3_pass},
            'n_pass': n_pass_p3,
        },
        'verdict': verdict_p3,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
