"""
T8: Puff Processing Complexity -> Vocabulary Breadth
Simplified version testing whether complex Puff materials require broader vocabulary.

Hypothesis: Later Puff chapters (more complex materials) require B programs
with larger vocabulary footprints.

Uses:
- Puff chapter position as complexity proxy (later = more complex)
- B folio vocabulary size (type count)
- Correlation between position and vocabulary breadth
"""

import json
import numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict
import csv

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"
DATA_DIR = Path(__file__).parent.parent.parent / "data"

def load_proposed_order():
    """Load proposed folio order with positions."""
    folio_order = []
    with open(RESULTS_DIR / "proposed_folio_order.txt", 'r', encoding='utf-8') as f:
        for line in f:
            if '|' in line and 'REGIME' in line:
                parts = line.split('|')
                if len(parts) >= 6:
                    try:
                        pos = int(parts[0].strip())
                        folio = parts[1].strip()
                        regime = parts[2].strip()
                        cei = float(parts[5].strip()) if len(parts) > 5 else 0.0
                        folio_order.append({
                            'position': pos,
                            'folio': folio,
                            'regime': regime,
                            'cei': cei,
                        })
                    except (ValueError, IndexError):
                        continue
    folio_order.sort(key=lambda x: x['position'])
    return folio_order

def load_folio_vocabulary():
    """Load vocabulary size per B folio from transcript."""
    transcript_path = DATA_DIR / "transcriptions" / "interlinear_full_words.txt"

    folio_vocab = defaultdict(set)

    with open(transcript_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            # H-only filtering
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue

            # B folios only
            language = row.get('language', '').strip().strip('"')
            if language != 'B':
                continue

            folio = row.get('folio', '').strip().strip('"')
            word = row.get('word', '').strip().strip('"')

            if folio and word and '*' not in word:
                folio_vocab[folio].add(word)

    return {f: len(v) for f, v in folio_vocab.items()}

def run_test():
    """Run T8: Complexity -> Vocabulary Breadth correlation test."""
    print("=" * 60)
    print("T8: PUFF COMPLEXITY -> VOCABULARY BREADTH")
    print("=" * 60)
    print()

    # Load data
    folio_order = load_proposed_order()
    folio_vocab = load_folio_vocabulary()

    print(f"Loaded {len(folio_order)} folios in proposed order")
    print(f"Vocabulary sizes for {len(folio_vocab)} B folios")
    print()

    # Match positions to vocabulary sizes
    positions = []
    vocab_sizes = []
    cei_values = []

    for entry in folio_order[:83]:
        pos = entry['position']
        folio = entry['folio']
        cei = entry['cei']

        vocab = folio_vocab.get(folio, None)
        if vocab is None:
            continue

        positions.append(pos)
        vocab_sizes.append(vocab)
        cei_values.append(cei)

    print(f"Matched {len(positions)}/83 positions to vocabulary data")
    print()

    # Test 1: Position -> Vocabulary Size correlation
    print("-" * 60)
    print("TEST 1: Position -> Vocabulary Size")
    print("-" * 60)

    rho1, p1 = stats.spearmanr(positions, vocab_sizes)
    print(f"Spearman rho: {rho1:.4f}")
    print(f"p-value: {p1:.4e}")

    test1_pass = rho1 > 0.2 and p1 < 0.05
    print(f"Pass criterion: rho > 0.2, p < 0.05")
    print(f"Result: {'PASS' if test1_pass else 'FAIL'}")
    print()

    # Test 2: Position -> CEI correlation (sanity check)
    print("-" * 60)
    print("TEST 2: Position -> CEI (sanity check)")
    print("-" * 60)

    rho2, p2 = stats.spearmanr(positions, cei_values)
    print(f"Spearman rho: {rho2:.4f}")
    print(f"p-value: {p2:.4e}")

    test2_pass = rho2 > 0.5 and p2 < 0.05
    print(f"Expected: Strong positive (by design of proposed order)")
    print(f"Result: {'PASS' if test2_pass else 'FAIL'}")
    print()

    # Test 3: Vocabulary Size -> CEI correlation
    print("-" * 60)
    print("TEST 3: Vocabulary Size -> CEI")
    print("-" * 60)

    rho3, p3 = stats.spearmanr(vocab_sizes, cei_values)
    print(f"Spearman rho: {rho3:.4f}")
    print(f"p-value: {p3:.4e}")

    test3_pass = abs(rho3) > 0.2 and p3 < 0.05
    print(f"Pass criterion: |rho| > 0.2, p < 0.05")
    print(f"Result: {'PASS' if test3_pass else 'FAIL'}")
    print()

    # Summary statistics
    print("-" * 60)
    print("SUMMARY STATISTICS")
    print("-" * 60)

    print(f"\nVocabulary sizes:")
    print(f"  Mean: {np.mean(vocab_sizes):.1f}")
    print(f"  Std:  {np.std(vocab_sizes):.1f}")
    print(f"  Min:  {min(vocab_sizes)}")
    print(f"  Max:  {max(vocab_sizes)}")

    # By thirds
    third = len(positions) // 3
    early_vocab = vocab_sizes[:third]
    middle_vocab = vocab_sizes[third:2*third]
    late_vocab = vocab_sizes[2*third:]

    print(f"\nBy position thirds:")
    print(f"  Early (1-{third}):  mean={np.mean(early_vocab):.1f}")
    print(f"  Middle ({third+1}-{2*third}): mean={np.mean(middle_vocab):.1f}")
    print(f"  Late ({2*third+1}-83):   mean={np.mean(late_vocab):.1f}")
    print()

    # Verdict
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)

    passed = test1_pass
    if test1_pass:
        verdict_detail = f"Position-Vocabulary correlation significant (rho={rho1:.3f}, p={p1:.4f})"
    else:
        if rho1 > 0:
            verdict_detail = f"Weak positive correlation (rho={rho1:.3f}) but not significant (p={p1:.4f})"
        else:
            verdict_detail = f"No positive correlation found (rho={rho1:.3f})"

    print(f"\nTest PASS criterion: Position-Vocabulary rho > 0.2, p < 0.05")
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    print(f"Detail: {verdict_detail}")
    print()

    # Save results
    results = {
        "test": "T8_complexity_breadth",
        "hypothesis": "Later Puff chapters (complex) require larger vocabulary footprints",
        "data": {
            "n_matched": len(positions),
            "vocab_mean": round(np.mean(vocab_sizes), 1),
            "vocab_std": round(np.std(vocab_sizes), 1),
            "vocab_min": min(vocab_sizes),
            "vocab_max": max(vocab_sizes),
            "early_third_mean": round(np.mean(early_vocab), 1),
            "middle_third_mean": round(np.mean(middle_vocab), 1),
            "late_third_mean": round(np.mean(late_vocab), 1),
        },
        "tests": {
            "position_vocab": {
                "rho": round(rho1, 4),
                "p": round(p1, 6),
                "passed": bool(test1_pass)
            },
            "position_cei": {
                "rho": round(rho2, 4),
                "p": round(p2, 6),
                "passed": bool(test2_pass)
            },
            "vocab_cei": {
                "rho": round(rho3, 4),
                "p": round(p3, 6),
                "passed": bool(test3_pass)
            }
        },
        "verdict": {
            "passed": bool(passed),
            "detail": verdict_detail
        }
    }

    with open(RESULTS_DIR / "puff_complexity_breadth_test.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: results/puff_complexity_breadth_test.json")

    return results

if __name__ == "__main__":
    run_test()
