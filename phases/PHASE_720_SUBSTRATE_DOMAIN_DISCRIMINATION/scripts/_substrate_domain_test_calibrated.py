"""PHASE_720 v2 (CALIBRATED): use broader length filter 15-80 words.

Calibration gap from v1 (length 20-50 gave Codicillus r21=-0.007) resolved:
the canonical C2032 Codicillus -0.22 baseline uses length 15-80 filter per
phases/RECIPE_FOLIO_CORRESPONDENCE/results/c2031_codicillus_cross_validation.json.

Re-run all four corpora with calibrated 15-80 filter to enable apples-to-apples
comparison against the documented Codicillus -0.22 reference.
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
OUT_PATH = ROOT / 'phases' / 'PHASE_720_SUBSTRATE_DOMAIN_DISCRIMINATION' / 'results' / 'substrate_domain_calibrated.json'

rng = random.Random(720)
N_PERM = 200

LATIN_ENDINGS = re.compile(
    r"(arum|orum|ibus|ius|ium|atis|atos|atus|ate|ata|ato|atu|"
    r"is|es|us|um|am|em|im|os|as|ae|ai|ei|i|o|u|m|s)$"
)


def latin_stem(word):
    w = word.lower()
    if len(w) > 4:
        w = LATIN_ENDINGS.sub("", w)
    return w[:3]


def load_paragraphs(filepath, min_len=15, max_len=80, skip_lines=0):
    """Load paragraphs separated by blank lines. CALIBRATED filter 15-80."""
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


def compute_signature(label, paragraphs):
    if not paragraphs or len(paragraphs) < 5:
        return {'label': label, 'error': f'too few paragraphs: {len(paragraphs)}'}
    n_words = sum(len(p) for p in paragraphs)
    lag1 = lag_excess(paragraphs, 1)
    lag2 = lag_excess(paragraphs, 2)
    lag3 = lag_excess(paragraphs, 3)
    if lag1 is None or lag2 is None:
        return {'label': label, 'error': 'insufficient pairs'}
    r21 = lag2['excess'] / lag1['excess'] if abs(lag1['excess']) > 1e-6 else float('nan')
    return {
        'label': label,
        'n_paragraphs': len(paragraphs),
        'n_words': n_words,
        'lag1_excess': lag1['excess'],
        'lag2_excess': lag2['excess'],
        'lag3_excess': lag3['excess'] if lag3 else None,
        'r21': r21,
        'lag1_full': lag1, 'lag2_full': lag2, 'lag3_full': lag3,
    }


def main():
    print("=" * 80)
    print("PHASE_720 v2 CALIBRATED: length filter 15-80 (matches canonical C2032)")
    print("=" * 80)

    print("\n[CALIBRATION CHECK: Codicillus, expected r21≈-0.22 with 15-80 filter]")
    cod = load_paragraphs(ROOT / 'sources' / 'codicillus' / 'codicillus_complete_latin.txt')
    print(f"  {len(cod)} paragraphs")
    cod_r = compute_signature('Codicillus', cod)

    print("\n[Mesue Grabadin, expected r21≈-0.17 with broader filter]")
    mesue_path = ROOT / 'sources' / 'mesue_grabadin' / 'mesue_grabadin_liber_primus.txt'
    if not mesue_path.exists():
        mesue_path = ROOT / 'sources' / 'mesue_grabadin' / 'mesue_grabadin_latin_full.txt'
    mes = load_paragraphs(mesue_path)
    print(f"  {len(mes)} paragraphs")
    mes_r = compute_signature('Mesue', mes)

    print("\n[Rupescissa, distillation Latin]")
    rup = load_paragraphs(
        ROOT / 'sources' / 'rupescissa' / 'rupescissa_latin_1561.txt', skip_lines=200
    )
    print(f"  {len(rup)} paragraphs")
    rup_r = compute_signature('Rupescissa', rup)

    print("\n[Theophilus body, metalwork Latin (PWRE-EXCLUDED class)]")
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
                    theo_paras.append(words)
                current = []
        else:
            current.append(line.strip())
    if current:
        words = re.findall(r"\b[a-zA-Z]+\b", " ".join(current))
        if 15 <= len(words) <= 80:
            theo_paras.append(words)
    print(f"  {len(theo_paras)} paragraphs")
    theo_r = compute_signature('Theophilus body', theo_paras)

    # ---- Summary table ----
    print("\n" + "=" * 80)
    print("CALIBRATED CROSS-CORPUS C2032 (15-80 LENGTH FILTER)")
    print("=" * 80)
    print(f"\n{'Corpus':<30}{'n_paras':>10}{'n_words':>10}{'lag1_exc':>11}{'lag2_exc':>11}{'r21':>10}")
    print("-" * 82)
    for r in [cod_r, mes_r, rup_r, theo_r]:
        if 'error' in r:
            print(f"{r['label']:<30}  ERROR: {r['error']}")
            continue
        print(f"{r['label']:<30}{r['n_paragraphs']:>10}{r['n_words']:>10}"
              f"{r['lag1_excess']:>+11.5f}{r['lag2_excess']:>+11.5f}{r['r21']:>+10.3f}")

    print(f"\n  REFERENCE: Voynich Section B r21: -0.66")
    print(f"  REFERENCE: Codicillus expected: -0.22 (calibration check)")
    print(f"  REFERENCE: Mensural notation r21: +0.18")

    # ---- Verdict ----
    print("\n" + "=" * 80)
    print("CALIBRATION CHECK + PRE-REGISTERED PREDICTION")
    print("=" * 80)

    if 'error' not in cod_r:
        cod_r21 = cod_r['r21']
        cod_calibration_ok = -0.30 <= cod_r21 <= -0.10
        print(f"\n  Codicillus r21: {cod_r21:+.3f}  "
              f"(expected -0.22) — calibration: {'OK' if cod_calibration_ok else 'OFF'}")

    if 'error' not in rup_r and 'error' not in theo_r:
        rup_r21 = rup_r['r21']
        theo_r21 = theo_r['r21']
        diff = abs(theo_r21 - rup_r21)
        print(f"\n  Rupescissa (distillation, PWRE-compatible): r21={rup_r21:+.3f}")
        print(f"  Theophilus (metalwork, PWRE-EXCLUDED): r21={theo_r21:+.3f}")
        print(f"  Difference: {theo_r21 - rup_r21:+.3f}")

        rup_in_dist_range = -0.30 <= rup_r21 <= -0.10
        theo_substantially_different = diff > 0.10
        theo_voynich_like = theo_r21 < -0.50

        if rup_in_dist_range and theo_substantially_different:
            verdict = "PWRE NARROWING EXTERNALLY VALIDATED — substrate quintet discriminates distillation from metalwork"
        elif theo_voynich_like:
            verdict = "UNEXPECTED — Theophilus shows Voynich-like signature"
        elif diff < 0.15:
            verdict = "SUBSTRATE QUINTET GENERIC AT DOMAIN LEVEL — both Latin corpora similar"
        else:
            verdict = "PARTIAL DISCRIMINATION — Rupescissa and Theophilus differ but not as predicted"

        print(f"\n  VERDICT: {verdict}")

    # Save
    out = {
        'method': 'PHASE_720 v2 calibrated (15-80 length filter)',
        'n_permutations': N_PERM,
        'calibration_check_codicillus_expected_minus_0_22': cod_r.get('r21'),
        'results': {
            'codicillus': cod_r, 'mesue': mes_r,
            'rupescissa': rup_r, 'theophilus_body': theo_r,
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
