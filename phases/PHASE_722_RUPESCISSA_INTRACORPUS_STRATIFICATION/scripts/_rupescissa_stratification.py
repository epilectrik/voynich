"""PHASE_722: Rupescissa intra-corpus register stratification.

Split Rupescissa paragraphs into recipe-dense vs theory-dense, compute C2032 r21
per stratum, test whether register-tracking interpretation of C2053 cross-corpus
pattern holds at intra-corpus resolution.

Pre-registered binary criteria per INDEX.md.
"""
from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
OUT_PATH = ROOT / 'phases' / 'PHASE_722_RUPESCISSA_INTRACORPUS_STRATIFICATION' / 'results' / 'rupescissa_stratification.json'

rng = random.Random(722)
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


# Register markers (Latin)
RECIPE_MARKERS = {
    # Imperative verbs (procedural commands)
    'recipe', 'accipe', 'sume', 'da', 'mitte', 'pone', 'misce', 'tere', 'agita',
    'coque', 'decoque', 'distilla', 'sublima', 'calcina', 'serva',
    'solvitur', 'coquitur', 'distillatur', 'fit', 'fiat', 'efficitur',
    # Measurement units
    'uncia', 'unciae', 'libra', 'librae', 'drachma', 'drachmae', 'pondus',
    'pondera', 'pars', 'partes',
    # Procedural sequence markers
    'tunc', 'deinde', 'postea', 'donec', 'usquequo', 'post',
}

THEORY_MARKERS = {
    # Abstract concepts
    'natura', 'naturae', 'essentia', 'essentiae', 'virtus', 'virtutis',
    'qualitas', 'qualitatis', 'substantia', 'substantiae',
    'materia', 'materiae', 'forma', 'formae',
    'principium', 'principia', 'fundamentum',
    'philosoph', 'philosophi', 'philosophus', 'philosophia',
    'secretum', 'mysterium',
    # Logical connectives
    'ergo', 'igitur', 'scilicet', 'sicut', 'quia', 'quoniam',
    'propterea', 'nam', 'enim',
}


def load_rupescissa_paragraphs(min_len=15, max_len=80, skip_lines=200):
    path = ROOT / 'sources' / 'rupescissa' / 'rupescissa_latin_1561.txt'
    text = path.read_text(encoding='utf-8', errors='replace')
    lines = text.split('\n')[skip_lines:]
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


def score_paragraph(paragraph):
    """Compute register score for a paragraph.
    Positive = recipe-dense, negative = theory-dense.
    Score is per-word density difference.
    """
    word_set = [w.lower() for w in paragraph]
    n_recipe = sum(1 for w in word_set if any(w.startswith(m) for m in RECIPE_MARKERS))
    n_theory = sum(1 for w in word_set if any(w.startswith(m) for m in THEORY_MARKERS))
    n_words = len(word_set)
    return (n_recipe - n_theory) / max(n_words, 1), n_recipe, n_theory


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
        "lag": lag, "n_pairs": total_pairs,
        "obs_rate": total_obs / total_pairs,
        "null_rate": total_null / total_pairs,
        "excess": (total_obs - total_null) / total_pairs,
    }


def compute_r21(paragraphs, label):
    if not paragraphs or len(paragraphs) < 5:
        return {'label': label, 'error': f'too few paragraphs: {len(paragraphs)}'}
    n_words = sum(len(p) for p in paragraphs)
    lag1 = lag_excess(paragraphs, 1)
    lag2 = lag_excess(paragraphs, 2)
    if lag1 is None or lag2 is None:
        return {'label': label, 'error': 'insufficient pairs'}
    r21 = lag2['excess'] / lag1['excess'] if abs(lag1['excess']) > 1e-6 else float('nan')
    return {
        'label': label,
        'n_paragraphs': len(paragraphs),
        'n_words': n_words,
        'lag1_excess': lag1['excess'],
        'lag2_excess': lag2['excess'],
        'r21': r21,
    }


def main():
    print("=" * 80)
    print("PHASE_722 RUPESCISSA INTRA-CORPUS REGISTER STRATIFICATION")
    print("=" * 80)

    print("\nLoading Rupescissa paragraphs...")
    paragraphs = load_rupescissa_paragraphs()
    print(f"  N paragraphs: {len(paragraphs)}")

    # Score each paragraph
    print("\nScoring register density...")
    scores = []
    for i, p in enumerate(paragraphs):
        score, n_recipe, n_theory = score_paragraph(p)
        scores.append((score, n_recipe, n_theory, len(p), i, p))

    # Stats
    score_vals = [s[0] for s in scores]
    recipe_counts = [s[1] for s in scores]
    theory_counts = [s[2] for s in scores]
    print(f"  Register-score distribution:")
    print(f"    min={min(score_vals):.4f}, max={max(score_vals):.4f}")
    print(f"    median={sorted(score_vals)[len(score_vals)//2]:.4f}")
    print(f"  Recipe-marker counts: mean={sum(recipe_counts)/len(recipe_counts):.2f}, "
          f"total={sum(recipe_counts)}")
    print(f"  Theory-marker counts: mean={sum(theory_counts)/len(theory_counts):.2f}, "
          f"total={sum(theory_counts)}")

    # Sort by score (high = recipe-dense, low = theory-dense)
    scores.sort(key=lambda x: -x[0])
    n = len(scores)
    quartile_size = n // 4
    print(f"\n  Quartile size: {quartile_size} paragraphs each (N total = {n})")

    recipe_dense_paras = [s[5] for s in scores[:quartile_size]]
    middle_paras = [s[5] for s in scores[quartile_size:3*quartile_size]]
    theory_dense_paras = [s[5] for s in scores[3*quartile_size:]]

    # Compute r21 per stratum
    print("\n" + "=" * 80)
    print("REGISTER-STRATIFIED r21")
    print("=" * 80)

    recipe_r = compute_r21(recipe_dense_paras, 'Recipe-dense (top quartile by score)')
    middle_r = compute_r21(middle_paras, 'Middle 50% (mixed register)')
    theory_r = compute_r21(theory_dense_paras, 'Theory-dense (bottom quartile)')

    print(f"\n{'Stratum':<45}{'n_paras':>10}{'lag1':>10}{'lag2':>10}{'r21':>10}")
    print("-" * 85)
    for r in [recipe_r, middle_r, theory_r]:
        if 'error' in r:
            print(f"{r['label']:<45}  ERROR: {r['error']}")
            continue
        print(f"{r['label']:<45}{r['n_paragraphs']:>10}"
              f"{r['lag1_excess']:>+10.5f}{r['lag2_excess']:>+10.5f}{r['r21']:>+10.3f}")

    # ---- Control 1: Random quartile split ----
    print("\n" + "=" * 80)
    print("CONTROL 1: Random quartile split (any-split-shows-difference check)")
    print("=" * 80)
    random_quartile_results = []
    for trial in range(3):
        rng_ctrl = random.Random(722 + trial)
        shuffled = list(range(n))
        rng_ctrl.shuffle(shuffled)
        top_q = [paragraphs[i] for i in shuffled[:quartile_size]]
        bot_q = [paragraphs[i] for i in shuffled[3*quartile_size:]]
        top_r = compute_r21(top_q, f'Random top quartile (seed {trial})')
        bot_r = compute_r21(bot_q, f'Random bottom quartile (seed {trial})')
        random_quartile_results.append({
            'seed': trial,
            'top_r21': top_r.get('r21', float('nan')),
            'bot_r21': bot_r.get('r21', float('nan')),
            'difference': abs((top_r.get('r21', 0) or 0) - (bot_r.get('r21', 0) or 0)),
        })
        print(f"  Seed {trial}: top r21={top_r.get('r21', 'N/A'):.3f}, "
              f"bot r21={bot_r.get('r21', 'N/A'):.3f}, "
              f"diff={random_quartile_results[-1]['difference']:.3f}")

    # ---- Control 2: Length quartile split ----
    print("\n" + "=" * 80)
    print("CONTROL 2: Length quartile split (length confound check)")
    print("=" * 80)
    length_sorted = sorted(range(n), key=lambda i: -len(paragraphs[i]))
    longest_q = [paragraphs[i] for i in length_sorted[:quartile_size]]
    shortest_q = [paragraphs[i] for i in length_sorted[3*quartile_size:]]
    long_r = compute_r21(longest_q, 'Longest quartile')
    short_r = compute_r21(shortest_q, 'Shortest quartile')
    print(f"  Longest quartile r21:  {long_r.get('r21', 'N/A'):+.3f}")
    print(f"  Shortest quartile r21: {short_r.get('r21', 'N/A'):+.3f}")
    length_diff = abs((long_r.get('r21', 0) or 0) - (short_r.get('r21', 0) or 0))
    print(f"  Difference: {length_diff:.3f}")

    # ---- Pre-registered verdict ----
    print("\n" + "=" * 80)
    print("PRE-REGISTERED VERDICT")
    print("=" * 80)

    if 'error' in recipe_r or 'error' in theory_r:
        verdict = "ERROR — insufficient data in one or both strata"
    else:
        recipe_r21 = recipe_r['r21']
        theory_r21 = theory_r['r21']
        diff = theory_r21 - recipe_r21

        # Check controls
        random_max_diff = max((r['difference'] for r in random_quartile_results
                              if not (r['difference'] != r['difference'])), default=0)
        register_diff = abs(diff)

        print(f"\n  Recipe-dense r21: {recipe_r21:+.3f}")
        print(f"  Theory-dense r21: {theory_r21:+.3f}")
        print(f"  Register-stratified difference: {register_diff:.3f}")
        print(f"  Random-quartile max difference (3 trials): {random_max_diff:.3f}")
        print(f"  Length-quartile difference: {length_diff:.3f}")

        clean_sign_reversal = recipe_r21 < -0.10 and theory_r21 > +0.10
        same_sign = (recipe_r21 < 0 and theory_r21 < 0) or (recipe_r21 > 0 and theory_r21 > 0)
        register_above_random = register_diff > random_max_diff * 1.5
        register_above_length = register_diff > length_diff * 1.5

        if clean_sign_reversal and register_above_random and register_above_length:
            verdict = "REGISTER-TRACKING CONFIRMED at intra-corpus resolution"
        elif clean_sign_reversal and not (register_above_random and register_above_length):
            verdict = "PARTIAL — sign reversal observed but confound controls suspicious"
        elif same_sign:
            verdict = "REGISTER HYPOTHESIS FAILS — within-corpus split same-sign"
        else:
            verdict = "MIXED — outcome doesn't match pre-registered patterns cleanly"

        print(f"\n  VERDICT: {verdict}")

    # Save
    out = {
        'method': 'PHASE_722 Rupescissa intra-corpus register stratification',
        'n_paragraphs_total': n,
        'quartile_size': quartile_size,
        'n_permutations': N_PERM,
        'recipe_dense': recipe_r,
        'middle': middle_r,
        'theory_dense': theory_r,
        'random_quartile_controls': random_quartile_results,
        'length_quartile_control': {
            'longest_r21': long_r.get('r21'),
            'shortest_r21': short_r.get('r21'),
            'difference': length_diff,
        },
        'verdict': verdict if 'error' not in recipe_r and 'error' not in theory_r else 'ERROR',
        'reference': {
            'rupescissa_overall_r21_phase_720': +0.226,
            'codicillus_r21_canonical': -0.229,
            'voynich_section_b_r21': -0.66,
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
