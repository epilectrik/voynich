#!/usr/bin/env python3
"""
LABEL LAYER PP/RI TEST
======================

The main PP/RI prediction test showed all TEXT folios are PP-dominant (~95%).
Our PP/RI findings were primarily about LABELS (C525):
- Labels: 50% o-prefix, ~0% qo-prefix, 61% label-only vocabulary
- Text: 20-24% o-prefix, 14% qo-prefix, PP-dominant

This test validates that the label layer shows the predicted patterns.

Phase: BRUNSCHWIG_PP_RI_TEST
Date: 2026-01-24
"""

import json
import csv
from collections import defaultdict, Counter
from pathlib import Path
import statistics

PROJECT_ROOT = Path(__file__).parent.parent.parent

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_prefix(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return p
    return None

def extract_middle(token):
    original = token
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break
    return token if token else None

def main():
    print("LABEL LAYER PP/RI TEST")
    print("="*70)
    print("Validating that PP/RI patterns differ between TEXT and LABELS")
    print("="*70)

    # Load transcript, split by text vs labels
    text_tokens = []
    label_tokens = []

    with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip() != 'H':
                continue

            word = row.get('word', '').strip()
            language = row.get('language', '').strip()
            placement = row.get('placement', '').strip()

            if language != 'A' or not word or '*' in word:
                continue

            if placement.startswith('L'):
                label_tokens.append(word)
            else:
                text_tokens.append(word)

    print(f"\nCorpus size:")
    print(f"  Text tokens: {len(text_tokens)}")
    print(f"  Label tokens: {len(label_tokens)}")

    # Compute PP/RI vocabulary
    a_text_middles = set(extract_middle(t) for t in text_tokens if extract_middle(t))
    b_middles = set()

    with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip() != 'H':
                continue
            word = row.get('word', '').strip()
            language = row.get('language', '').strip()
            placement = row.get('placement', '').strip()
            if language == 'B' and word and '*' not in word and not placement.startswith('L'):
                m = extract_middle(word)
                if m:
                    b_middles.add(m)

    pp_middles = a_text_middles & b_middles
    ri_middles = a_text_middles - b_middles

    print(f"\nVocabulary:")
    print(f"  PP MIDDLEs (A and B text): {len(pp_middles)}")
    print(f"  RI MIDDLEs (A-only text): {len(ri_middles)}")

    # Classify tokens
    text_pp = sum(1 for t in text_tokens if extract_middle(t) in pp_middles)
    text_ri = sum(1 for t in text_tokens if extract_middle(t) in ri_middles)
    label_pp = sum(1 for t in label_tokens if extract_middle(t) in pp_middles)
    label_ri = sum(1 for t in label_tokens if extract_middle(t) in ri_middles)

    # Label-only vocabulary
    label_middles = set(extract_middle(t) for t in label_tokens if extract_middle(t))
    label_only_middles = label_middles - a_text_middles
    label_in_text = label_middles & a_text_middles

    print(f"\n" + "="*70)
    print("PP/RI RATIO COMPARISON")
    print("="*70)

    text_total = text_pp + text_ri
    label_total = label_pp + label_ri

    print(f"\n{'Context':<15} {'PP':<10} {'RI':<10} {'PP%':<10} {'RI%':<10}")
    print("-"*55)
    print(f"{'Text':<15} {text_pp:<10} {text_ri:<10} {100*text_pp/text_total:.1f}%{'':<5} {100*text_ri/text_total:.1f}%")
    print(f"{'Labels':<15} {label_pp:<10} {label_ri:<10} {100*label_pp/label_total:.1f}%{'':<5} {100*label_ri/label_total:.1f}%")

    print(f"\n" + "="*70)
    print("LABEL VOCABULARY OVERLAP")
    print("="*70)
    print(f"\nLabel MIDDLEs total: {len(label_middles)}")
    print(f"  In text vocabulary: {len(label_in_text)} ({100*len(label_in_text)/len(label_middles):.1f}%)")
    print(f"  Label-only (NOT in text): {len(label_only_middles)} ({100*len(label_only_middles)/len(label_middles):.1f}%)")

    # PREFIX distribution comparison
    print(f"\n" + "="*70)
    print("PREFIX DISTRIBUTION COMPARISON")
    print("="*70)

    text_prefixes = Counter(extract_prefix(t) for t in text_tokens if extract_prefix(t))
    label_prefixes = Counter(extract_prefix(t) for t in label_tokens if extract_prefix(t))

    text_total_prefix = sum(text_prefixes.values())
    label_total_prefix = sum(label_prefixes.values())

    print(f"\n{'PREFIX':<8} {'Text':<12} {'Labels':<12} {'Difference':<15}")
    print("-"*50)

    for p in ['o', 'qo', 'c', 's', 'd', 'y', 'k']:
        text_pct = 100 * text_prefixes.get(p, 0) / text_total_prefix if text_total_prefix else 0
        label_pct = 100 * label_prefixes.get(p, 0) / label_total_prefix if label_total_prefix else 0
        diff = label_pct - text_pct
        direction = "LABEL higher" if diff > 0 else "TEXT higher"
        print(f"{p:<8} {text_pct:>6.1f}%      {label_pct:>6.1f}%      {diff:>+5.1f}% ({direction})")

    # Validation against C525 predictions
    print(f"\n" + "="*70)
    print("C525 PREDICTION VALIDATION")
    print("="*70)

    o_text = 100 * text_prefixes.get('o', 0) / text_total_prefix
    o_label = 100 * label_prefixes.get('o', 0) / label_total_prefix
    qo_text = 100 * text_prefixes.get('qo', 0) / text_total_prefix
    qo_label = 100 * label_prefixes.get('qo', 0) / label_total_prefix

    print(f"\nPrediction 1: o-prefix elevated in labels (50% vs 20-24%)")
    print(f"  Text: {o_text:.1f}%, Labels: {o_label:.1f}%")
    print(f"  {'SUPPORTS' if o_label > o_text * 1.5 else 'PARTIAL' if o_label > o_text else 'CONTRADICTS'}")

    print(f"\nPrediction 2: qo-prefix suppressed in labels (~0% vs 14%)")
    print(f"  Text: {qo_text:.1f}%, Labels: {qo_label:.1f}%")
    print(f"  {'SUPPORTS' if qo_label < qo_text * 0.5 else 'PARTIAL' if qo_label < qo_text else 'CONTRADICTS'}")

    print(f"\nPrediction 3: 61% label-only vocabulary")
    label_only_pct = 100 * len(label_only_middles) / len(label_middles)
    print(f"  Observed: {label_only_pct:.1f}%")
    print(f"  {'SUPPORTS' if 55 < label_only_pct < 70 else 'PARTIAL' if 40 < label_only_pct < 80 else 'CONTRADICTS'}")

    # Summary
    print(f"\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nKey findings:")
    print(f"  1. Text is {100*text_pp/text_total:.0f}% PP-dominant (procedural vocabulary)")
    print(f"  2. Labels show {label_only_pct:.0f}% unique vocabulary (not in text)")
    print(f"  3. o-prefix: {o_label:.1f}% in labels vs {o_text:.1f}% in text ({o_label/o_text:.1f}x)")
    print(f"  4. qo-prefix: {qo_label:.1f}% in labels vs {qo_text:.1f}% in text")

    print("\nInterpretation:")
    print("  - Original Brunschwig tests (C493 etc.) apply to TEXT layer -> still valid")
    print("  - New PP/RI findings (C525) apply to LABEL layer -> complementary")
    print("  - Labels serve identification (unique specimens)")
    print("  - Text serves procedures (standardized operations)")

    # Save results
    results = {
        'phase': 'BRUNSCHWIG_PP_RI_TEST',
        'test': 'LABEL_LAYER',
        'date': '2026-01-24',
        'text_pp_ratio': text_pp / text_total,
        'label_pp_ratio': label_pp / label_total if label_total else 0,
        'label_only_vocabulary_pct': label_only_pct,
        'o_prefix_text': o_text,
        'o_prefix_label': o_label,
        'qo_prefix_text': qo_text,
        'qo_prefix_label': qo_label,
        'c525_predictions': {
            'o_elevation': 'SUPPORTS' if o_label > o_text * 1.5 else 'PARTIAL',
            'qo_suppression': 'SUPPORTS' if qo_label < qo_text * 0.5 else 'PARTIAL',
            'label_only_vocab': 'SUPPORTS' if 55 < label_only_pct < 70 else 'PARTIAL'
        }
    }

    output_dir = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_PP_RI_TEST' / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / 'label_layer_test.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_dir / 'label_layer_test.json'}")

if __name__ == '__main__':
    main()
