"""
PCI-V2 scoring script.

Reads predictions.json and features.json, mechanically computes class scores
per the pre-registered protocol.

Scoring rule (from PROTOCOL.md):
  class_score = (MATCHES - 2*MISMATCHES - 5*INCOMPATIBLE) / scoring_features

where:
  MATCH        = prediction direction matches observed direction
  MISMATCH     = prediction direction contradicts observed direction
  INCOMPATIBLE = observed value directly falsifies class (auto-disqualifies)
  NEUTRAL      = excluded from numerator and denominator

Classes with any INCOMPATIBLE flag are disqualified from "best-fit" status
regardless of score.

Execution: python score.py
Output: writes results.json to the same directory.
"""
import sys, os, json
from pathlib import Path


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def score_class(class_name, predictions, features):
    """Compute score for a single class.

    Returns dict with:
      matches, mismatches, incompatibles, neutrals, scoring_features,
      raw_score, normalized_score, disqualified (bool)
    """
    matches = 0
    mismatches = 0
    incompatibles = 0
    neutrals = 0
    details = []

    for feat_id in sorted(features['features'].keys()):
        observed = features['features'][feat_id]['observed']
        predicted = predictions['predictions'][feat_id][class_name]

        if predicted == "NEUTRAL":
            neutrals += 1
            details.append({'feature': feat_id, 'observed': observed, 'predicted': predicted, 'result': 'NEUTRAL'})
            continue

        if predicted == "INCOMPATIBLE":
            # The class predicts this feature should NOT be present (categorically).
            # If the feature IS present in observations, that falsifies the class.
            if observed == "HIGH":
                incompatibles += 1
                details.append({'feature': feat_id, 'observed': observed, 'predicted': predicted, 'result': 'FALSIFIED'})
            else:
                # Feature absent, so "INCOMPATIBLE" prediction is satisfied
                matches += 1
                details.append({'feature': feat_id, 'observed': observed, 'predicted': predicted, 'result': 'MATCH (absent as predicted)'})
            continue

        # HIGH or LOW predictions vs observed HIGH or LOW
        if predicted == "HIGH" and observed == "HIGH":
            matches += 1
            details.append({'feature': feat_id, 'observed': observed, 'predicted': predicted, 'result': 'MATCH'})
        elif predicted == "LOW" and observed == "LOW":
            matches += 1
            details.append({'feature': feat_id, 'observed': observed, 'predicted': predicted, 'result': 'MATCH'})
        elif predicted == "HIGH" and observed == "LOW":
            mismatches += 1
            details.append({'feature': feat_id, 'observed': observed, 'predicted': predicted, 'result': 'MISMATCH'})
        elif predicted == "LOW" and observed == "HIGH":
            mismatches += 1
            details.append({'feature': feat_id, 'observed': observed, 'predicted': predicted, 'result': 'MISMATCH'})
        else:
            # Shouldn't happen with current prediction vocab
            details.append({'feature': feat_id, 'observed': observed, 'predicted': predicted, 'result': 'UNKNOWN'})

    scoring_features = matches + mismatches + incompatibles
    raw_score = matches - 2 * mismatches - 5 * incompatibles
    normalized = raw_score / scoring_features if scoring_features > 0 else 0.0
    disqualified = incompatibles > 0

    return {
        'class': class_name,
        'matches': matches,
        'mismatches': mismatches,
        'incompatibles': incompatibles,
        'neutrals': neutrals,
        'scoring_features': scoring_features,
        'raw_score': raw_score,
        'normalized_score': normalized,
        'disqualified': disqualified,
        'details': details,
    }


def main():
    here = Path(__file__).parent
    predictions = load_json(here / 'predictions.json')
    features = load_json(here / 'features.json')

    # Assert predictions haven't been modified (simple structural check)
    assert predictions['metadata']['locked'], "Predictions not marked as locked!"

    results = []
    for class_name in sorted(predictions['classes'].keys()):
        results.append(score_class(class_name, predictions, features))

    # Sort by score descending (disqualified classes appear at bottom regardless)
    results.sort(key=lambda r: (0 if r['disqualified'] else 1, r['normalized_score']), reverse=True)

    # Identify winner per decision rule
    eligible = [r for r in results if not r['disqualified']]
    if not eligible:
        verdict = "ALL_DISQUALIFIED"
        winner = None
        margin = None
    else:
        winner = eligible[0]['class']
        if len(eligible) > 1:
            margin = eligible[0]['normalized_score'] - eligible[1]['normalized_score']
        else:
            margin = float('inf')

        if margin > 0.15:
            verdict = "CLEAR_WINNER"
        elif eligible[0]['normalized_score'] <= 0:
            verdict = "NO_CLASS_FITS"
        else:
            verdict = "CLOSE_COMPETITION"

    output = {
        'metadata': {
            'phase': 'PCI-V2',
            'executed': 'yes',
            'protocol_commit': '1e973cb',
        },
        'verdict': verdict,
        'winner': winner,
        'margin': margin,
        'results': results,
    }

    out_path = here / 'results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Print summary
    print()
    print("=" * 80)
    print("PCI-V2 SCORING RESULTS")
    print("=" * 80)
    print()
    print(f"{'Class':<8} {'Match':>6} {'Mis':>5} {'Incomp':>7} {'Neut':>5} {'Raw':>6} {'Norm':>8} {'Status':<15}")
    print("-" * 80)
    for r in results:
        status = "DISQUALIFIED" if r['disqualified'] else ""
        print(f"{r['class']:<8} {r['matches']:>6} {r['mismatches']:>5} {r['incompatibles']:>7} "
              f"{r['neutrals']:>5} {r['raw_score']:>6} {r['normalized_score']:>8.3f} {status:<15}")

    print()
    print(f"VERDICT: {verdict}")
    print(f"WINNER: {winner}")
    if margin is not None and margin != float('inf'):
        print(f"MARGIN: {margin:.3f}")

    print()
    print(f"Results written to: {out_path}")


if __name__ == '__main__':
    main()
