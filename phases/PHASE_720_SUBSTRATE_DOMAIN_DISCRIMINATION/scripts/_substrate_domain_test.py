"""PHASE_720: Substrate-quintet (C2032) domain-discrimination test.

After PHASE_718 confirmed the 8D matcher is generic, test whether the surviving
substrate-quintet signature (C2032 lag2/lag1 stem-class autocorrelation) is
domain-discriminative within medieval procedural Latin.

Methodology reuses `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/_c2031_codicillus_cross_validation.py`:
  1. Load Latin paragraphs (blank-line-separated, 20-50 words)
  2. Compute Latin stem per word (lowercase, strip case ending, first 3 chars)
  3. Compute lag-N same-stem rate vs within-paragraph shuffled null
  4. Compute r21 = lag2_excess / lag1_excess

Test corpora:
  - Codicillus (reference: r21 ≈ -0.22 expected)
  - Mesue (reference: r21 ≈ -0.17 expected)
  - Rupescissa (distillation/quintessence Latin — PWRE-compatible)
  - Theophilus (metalwork/glass/pigments — PWRE-EXCLUDED class)

Pre-registered prediction: if PWRE narrowing is right, Rupescissa should show
Codicillus-like signature (in-domain distillation Latin), Theophilus should show
distinct signature (out-of-domain metalwork).
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
OUT_PATH = ROOT / 'phases' / 'PHASE_720_SUBSTRATE_DOMAIN_DISCRIMINATION' / 'results' / 'substrate_domain_results.json'

rng = random.Random(720)
N_PERM = 200

# Latin stem stripping per existing methodology
LATIN_ENDINGS = re.compile(
    r"(arum|orum|ibus|ius|ium|atis|atos|atus|ate|ata|ato|atu|"
    r"is|es|us|um|am|em|im|os|as|ae|ai|ei|i|o|u|m|s)$"
)


def latin_stem(word):
    w = word.lower()
    if len(w) > 4:
        w = LATIN_ENDINGS.sub("", w)
    return w[:3]


def load_paragraphs_by_blanklines(filepath, min_len=20, max_len=50, skip_lines=0):
    """Load Latin paragraphs separated by blank lines, filter by word count."""
    if not Path(filepath).exists():
        return []
    text = Path(filepath).read_text(encoding='utf-8', errors='replace')
    lines = text.split('\n')
    if skip_lines > 0:
        lines = lines[skip_lines:]
    paragraphs = []
    current = []
    for line in lines:
        if not line.strip():
            if current:
                words = re.findall(r"\b[a-zA-Z]+\b", " ".join(current))
                if min_len <= len(words) <= max_len:
                    paragraphs.append(words)
                current = []
        else:
            current.append(line.strip())
    if current:
        words = re.findall(r"\b[a-zA-Z]+\b", " ".join(current))
        if min_len <= len(words) <= max_len:
            paragraphs.append(words)
    return paragraphs


def lag_same_rate(seq, lag):
    if len(seq) <= lag:
        return 0.0, 0
    n_pairs = len(seq) - lag
    n_same = sum(1 for i in range(n_pairs) if seq[i] == seq[i + lag])
    return n_same / n_pairs, n_pairs


def lag_excess(paragraphs, lag, n_perm=N_PERM):
    """Observed minus shuffled-null same-stem-class rate at lag."""
    total_pairs = 0
    total_obs = 0
    total_null = 0.0
    for p in paragraphs:
        stems = [latin_stem(w) for w in p]
        if len(stems) <= lag:
            continue
        rate, pairs = lag_same_rate(stems, lag)
        total_pairs += pairs
        total_obs += int(round(rate * pairs))
        shuffled = list(stems)
        for _ in range(n_perm):
            rng.shuffle(shuffled)
            r, _ = lag_same_rate(shuffled, lag)
            total_null += r * pairs / n_perm
    if total_pairs == 0:
        return None
    return {
        "lag": lag,
        "n_pairs": total_pairs,
        "obs_rate": total_obs / total_pairs,
        "null_rate": total_null / total_pairs,
        "excess": (total_obs - total_null) / total_pairs,
    }


def compute_corpus_signature(label, paragraphs):
    """Compute lag1/lag2/lag3 stem-class autocorrelation + r21."""
    if not paragraphs or len(paragraphs) < 5:
        return {'label': label, 'error': f'too few paragraphs: {len(paragraphs)}'}

    n_words = sum(len(p) for p in paragraphs)
    lag1 = lag_excess(paragraphs, 1)
    lag2 = lag_excess(paragraphs, 2)
    lag3 = lag_excess(paragraphs, 3)
    if lag1 is None or lag2 is None:
        return {'label': label, 'error': 'insufficient pairs'}

    r21 = lag2['excess'] / lag1['excess'] if abs(lag1['excess']) > 1e-6 else float('nan')
    r31 = lag3['excess'] / lag1['excess'] if abs(lag1['excess']) > 1e-6 and lag3 else float('nan')

    return {
        'label': label,
        'n_paragraphs': len(paragraphs),
        'n_words': n_words,
        'lag1': lag1,
        'lag2': lag2,
        'lag3': lag3,
        'lag1_excess': lag1['excess'],
        'lag2_excess': lag2['excess'],
        'lag3_excess': lag3['excess'] if lag3 else None,
        'r21': r21,
        'r31': r31,
    }


def main():
    print("=" * 80)
    print("PHASE_720 SUBSTRATE-QUINTET DOMAIN-DISCRIMINATION TEST")
    print("=" * 80)

    # Reference baselines (verify reproduction of known values)
    print("\n[REFERENCE: Codicillus — expected r21 ≈ -0.22]")
    cod_paras = load_paragraphs_by_blanklines(
        ROOT / 'sources' / 'codicillus' / 'codicillus_complete_latin.txt'
    )
    print(f"  {len(cod_paras)} paragraphs (20-50 words)")
    cod_result = compute_corpus_signature('Codicillus', cod_paras)

    print("\n[REFERENCE: Mesue Grabadin — expected r21 ≈ -0.17]")
    # Try the liber_primus first
    mesue_path = ROOT / 'sources' / 'mesue_grabadin' / 'mesue_grabadin_liber_primus.txt'
    if not mesue_path.exists():
        mesue_path = ROOT / 'sources' / 'mesue_grabadin' / 'mesue_grabadin_latin_full.txt'
    mesue_paras = load_paragraphs_by_blanklines(mesue_path)
    print(f"  {len(mesue_paras)} paragraphs (20-50 words)")
    mesue_result = compute_corpus_signature('Mesue Grabadin', mesue_paras)

    # NEW corpora
    print("\n[NEW: Rupescissa — distillation/quintessence Latin]")
    rup_path = ROOT / 'sources' / 'rupescissa' / 'rupescissa_latin_1561.txt'
    rup_paras = load_paragraphs_by_blanklines(rup_path, skip_lines=200)  # skip title page
    print(f"  {len(rup_paras)} paragraphs (20-50 words)")
    rup_result = compute_corpus_signature('Rupescissa', rup_paras)

    print("\n[NEW: Theophilus body — metalwork/glass/pigments (PWRE-EXCLUDED class)]")
    # Use only body sections per Theophilus README
    theo_path = ROOT / 'sources' / 'theophilus' / 'theophilus_hendrie_1847.txt'
    theo_lines = theo_path.read_text(encoding='utf-8', errors='replace').split('\n')
    # Latin body ranges per README: 2242-4283, 7213-9147, 10537-20528 (skip notes)
    theo_body = []
    theo_body.extend(theo_lines[2242:4283])
    theo_body.extend(theo_lines[7213:9147])
    theo_body.extend(theo_lines[10537:11337])  # Book III Latin only
    # Write to temp and process
    theo_text = '\n'.join(theo_body)
    theo_paras = []
    current = []
    for line in theo_body:
        if not line.strip():
            if current:
                words = re.findall(r"\b[a-zA-Z]+\b", " ".join(current))
                if 20 <= len(words) <= 50:
                    theo_paras.append(words)
                current = []
        else:
            current.append(line.strip())
    if current:
        words = re.findall(r"\b[a-zA-Z]+\b", " ".join(current))
        if 20 <= len(words) <= 50:
            theo_paras.append(words)
    print(f"  {len(theo_paras)} paragraphs (20-50 words)")
    theo_result = compute_corpus_signature('Theophilus body', theo_paras)

    # ---- Summary table ----
    print("\n" + "=" * 80)
    print("CROSS-CORPUS C2032 STEM-CLASS SIGNATURE SUMMARY")
    print("=" * 80)
    print(f"\n{'Corpus':<28}{'n_paras':>10}{'n_words':>10}{'lag1_exc':>11}{'lag2_exc':>11}{'r21':>10}")
    print("-" * 80)
    for r in [cod_result, mesue_result, rup_result, theo_result]:
        if 'error' in r:
            print(f"{r['label']:<28}  ERROR: {r['error']}")
            continue
        print(f"{r['label']:<28}{r['n_paragraphs']:>10}{r['n_words']:>10}"
              f"{r['lag1_excess']:>+11.5f}{r['lag2_excess']:>+11.5f}{r['r21']:>+10.3f}")

    print(f"\n  REFERENCE: Voynich Section B r21 (known): -0.66")
    print(f"  REFERENCE: Mensural notation r21 (known): +0.18")

    # ---- Pre-registered prediction check ----
    print("\n" + "=" * 80)
    print("PRE-REGISTERED PREDICTION CHECK")
    print("=" * 80)

    if 'error' in rup_result or 'error' in theo_result:
        print("\n  Cannot evaluate — corpus errors")
    else:
        rup_r21 = rup_result['r21']
        theo_r21 = theo_result['r21']
        cod_r21 = cod_result.get('r21', float('nan'))
        diff = abs(theo_r21 - rup_r21)
        print(f"\n  Rupescissa (distillation, PWRE-compatible) r21: {rup_r21:+.3f}")
        print(f"  Theophilus (metalwork, PWRE-EXCLUDED) r21: {theo_r21:+.3f}")
        print(f"  Codicillus (in-domain Latin reference) r21: {cod_r21:+.3f}")
        print(f"  Difference (Theophilus - Rupescissa): {theo_r21 - rup_r21:+.3f}")

        rup_in_distillation_range = -0.30 <= rup_r21 <= -0.10
        theo_substantially_different = diff > 0.05
        theo_unexpected_voynich_like = theo_r21 < -0.50

        if rup_in_distillation_range and theo_substantially_different:
            verdict = "PWRE NARROWING EXTERNALLY VALIDATED — substrate quintet discriminates distillation from metalwork"
        elif theo_unexpected_voynich_like:
            verdict = "UNEXPECTED — Theophilus shows Voynich-like signature, reverses PWRE prediction"
        elif diff < 0.10:
            verdict = "SUBSTRATE QUINTET GENERIC — discriminates Voynich from Latin but not domain-within-Latin"
        else:
            verdict = "MIXED / unclear"

        print(f"\n  VERDICT: {verdict}")

    # Save
    out = {
        'method': 'PHASE_720 substrate-quintet domain-discrimination test',
        'n_permutations': N_PERM,
        'methodology': 'C2032 stem-class autocorrelation, reused from _c2031_codicillus_cross_validation.py',
        'results': {
            'codicillus': cod_result,
            'mesue': mesue_result,
            'rupescissa': rup_result,
            'theophilus_body': theo_result,
        },
        'reference_voynich_section_b_r21': -0.66,
        'reference_mensural_r21': 0.18,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
