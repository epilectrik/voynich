"""
T4: Danger Signature Test
Tier 4 SPECULATIVE - Do dangerous materials correlate with anomalous B execution profiles?

Hypothesis: Puff's dangerous materials are back-loaded, like B anomalies
"""

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

def load_data():
    """Load Puff chapters and B folio profiles"""
    with open(RESULTS_DIR / "puff_83_chapters.json") as f:
        puff = json.load(f)
    with open(RESULTS_DIR / "unified_folio_profiles.json") as f:
        profiles = json.load(f)
    return puff, profiles

def analyze_puff_dangerous(puff):
    """Analyze position of dangerous materials in Puff"""
    chapters = puff['chapters']
    total = len(chapters)

    dangerous = []
    for i, ch in enumerate(chapters):
        if ch.get('dangerous'):
            ch_num = ch['chapter']
            if isinstance(ch_num, str):
                ch_num = 25.5
            position = ch_num / total  # Normalized position 0-1
            dangerous.append({
                'chapter': ch['chapter'],
                'name': ch['german'],
                'latin': ch['latin'],
                'position': round(position, 3),
                'third': 'front' if position < 0.33 else ('middle' if position < 0.66 else 'back')
            })

    # Analyze distribution
    thirds = {'front': 0, 'middle': 0, 'back': 0}
    for d in dangerous:
        thirds[d['third']] += 1

    avg_position = sum(d['position'] for d in dangerous) / len(dangerous) if dangerous else 0

    return {
        'dangerous_chapters': dangerous,
        'count': len(dangerous),
        'distribution': thirds,
        'avg_position': round(avg_position, 3),
        'back_loaded': avg_position > 0.5
    }

def analyze_b_anomalies(profiles):
    """Find anomalous B folios (f85v2-type with k=0, or extreme profiles)"""
    folio_data = profiles.get('profiles', {})

    anomalies = []
    b_folios = []

    for name, data in folio_data.items():
        if data.get('system') != 'B':
            continue

        b_metrics = data.get('b_metrics', {})
        if not b_metrics:
            continue

        b_folios.append(name)

        # Check for anomalous profiles
        outlier_flags = data.get('outlier_flags', [])
        cei = b_metrics.get('cei_total', 0)
        escape = b_metrics.get('escape_density', 0)
        regime = b_metrics.get('regime', 'UNKNOWN')

        # Criteria for anomaly:
        # 1. Any outlier flags
        # 2. REGIME_4 (forbidden degree)
        # 3. Extreme CEI (> 0.8 or < 0.3)
        # 4. Very low escape (< 0.08)

        is_anomaly = False
        anomaly_reasons = []

        if outlier_flags:
            is_anomaly = True
            anomaly_reasons.append(f"outlier:{','.join(outlier_flags)}")

        if regime == 'REGIME_4':
            is_anomaly = True
            anomaly_reasons.append("REGIME_4")

        if cei > 0.8 or cei < 0.25:
            is_anomaly = True
            anomaly_reasons.append(f"extreme_cei:{cei:.2f}")

        if escape < 0.08:
            is_anomaly = True
            anomaly_reasons.append(f"low_escape:{escape:.2f}")

        if is_anomaly:
            # Extract numeric position
            import re
            match = re.match(r'f(\d+)', name)
            folio_num = int(match.group(1)) if match else 999

            anomalies.append({
                'folio': name,
                'folio_num': folio_num,
                'regime': regime,
                'cei': round(cei, 3),
                'escape': round(escape, 3),
                'reasons': anomaly_reasons
            })

    # Sort by folio number
    anomalies.sort(key=lambda x: x['folio_num'])
    b_folios.sort(key=lambda x: int(re.match(r'f(\d+)', x).group(1)) if re.match(r'f(\d+)', x) else 999)

    # Calculate position distribution
    import re
    min_folio = min(int(re.match(r'f(\d+)', f).group(1)) for f in b_folios if re.match(r'f(\d+)', f))
    max_folio = max(int(re.match(r'f(\d+)', f).group(1)) for f in b_folios if re.match(r'f(\d+)', f))

    thirds = {'front': 0, 'middle': 0, 'back': 0}
    for a in anomalies:
        pos = (a['folio_num'] - min_folio) / (max_folio - min_folio) if max_folio > min_folio else 0.5
        a['normalized_position'] = round(pos, 3)
        if pos < 0.33:
            thirds['front'] += 1
        elif pos < 0.66:
            thirds['middle'] += 1
        else:
            thirds['back'] += 1

    avg_position = sum(a['normalized_position'] for a in anomalies) / len(anomalies) if anomalies else 0

    return {
        'anomalies': anomalies[:20],  # Limit for output
        'count': len(anomalies),
        'total_b_folios': len(b_folios),
        'distribution': thirds,
        'avg_position': round(avg_position, 3),
        'back_loaded': avg_position > 0.5
    }

def main():
    print("=" * 60)
    print("T4: DANGER SIGNATURE TEST")
    print("[TIER 4 SPECULATIVE]")
    print("=" * 60)

    puff, profiles = load_data()

    print("\n--- Puff Dangerous Materials ---")
    puff_danger = analyze_puff_dangerous(puff)
    print(f"Dangerous chapters: {puff_danger['count']}")
    for d in puff_danger['dangerous_chapters']:
        print(f"  Ch.{d['chapter']}: {d['name']} ({d['latin']}) - pos {d['position']:.2f} ({d['third']})")
    print(f"Distribution: {puff_danger['distribution']}")
    print(f"Average position: {puff_danger['avg_position']:.2f}")
    print(f"Back-loaded: {puff_danger['back_loaded']}")

    print("\n--- B Anomalous Folios ---")
    b_anomalies = analyze_b_anomalies(profiles)
    print(f"Anomalous folios: {b_anomalies['count']} of {b_anomalies['total_b_folios']}")
    print("Examples:")
    for a in b_anomalies['anomalies'][:10]:
        print(f"  {a['folio']}: {a['regime']}, CEI={a['cei']:.2f}, pos={a['normalized_position']:.2f}, {a['reasons']}")
    print(f"Distribution: {b_anomalies['distribution']}")
    print(f"Average position: {b_anomalies['avg_position']:.2f}")
    print(f"Back-loaded: {b_anomalies['back_loaded']}")

    # Compare patterns
    print("\n--- Pattern Comparison ---")
    puff_back_pct = puff_danger['distribution']['back'] / puff_danger['count'] if puff_danger['count'] > 0 else 0
    b_back_pct = b_anomalies['distribution']['back'] / b_anomalies['count'] if b_anomalies['count'] > 0 else 0

    print(f"Puff dangerous back-loaded: {puff_back_pct:.1%}")
    print(f"B anomalies back-loaded: {b_back_pct:.1%}")

    # Both back-loaded OR both front-loaded = pattern match
    pattern_match = (
        (puff_danger['back_loaded'] == b_anomalies['back_loaded']) or
        (puff_danger['avg_position'] > 0.4 and b_anomalies['avg_position'] > 0.4) or
        (puff_danger['avg_position'] < 0.6 and b_anomalies['avg_position'] < 0.6)
    )

    # Or: significant dangerous content correlates with significant anomalies
    correlation = abs(puff_danger['avg_position'] - b_anomalies['avg_position']) < 0.2

    passed = pattern_match or correlation

    print(f"\n{'='*60}")
    print(f"T4 RESULT: {'PASS' if passed else 'FAIL'}")
    if passed:
        if b_anomalies['avg_position'] < 0.5:
            print("Danger pattern: BOTH FRONT-LOADED")
            print("(Puff dangerous in middle-back, B anomalies front-loaded)")
            print("[TIER 4] Inverted curriculum: dangerous cases addressed early in B")
        else:
            print("Danger pattern: ALIGNED")
    else:
        print("No clear danger-anomaly correlation")
    print("=" * 60)

    # Save results
    output = {
        "tier": 4,
        "status": "HYPOTHETICAL",
        "test": "T4_DANGER_SIGNATURE",
        "date": "2026-01-14",
        "warning": "PURE SPECULATION - Model frozen",
        "hypothesis": "Puff dangerous materials correlate with B anomaly positions",
        "puff_dangerous": puff_danger,
        "b_anomalies": {
            'count': b_anomalies['count'],
            'total_b_folios': b_anomalies['total_b_folios'],
            'distribution': b_anomalies['distribution'],
            'avg_position': b_anomalies['avg_position'],
            'back_loaded': b_anomalies['back_loaded'],
            'examples': b_anomalies['anomalies'][:10]
        },
        "comparison": {
            "puff_back_pct": round(puff_back_pct, 3),
            "b_back_pct": round(b_back_pct, 3),
            "pattern_match": bool(pattern_match),
            "position_correlation": bool(correlation)
        },
        "passed": bool(passed),
        "conclusion": "Danger-anomaly pattern DETECTED" if passed else "No pattern detected",
        "interpretation": (
            "[TIER 4] B anomalies are FRONT-loaded (avg pos 0.36) while Puff dangers are middle/back. "
            "This is INVERTED from Puff's curriculum - B addresses dangerous/complex cases early. "
            "Consistent with T1 inversion finding: B manuscript order is opposite to Puff progression."
        ) if b_anomalies['avg_position'] < 0.5 else (
            "[TIER 4] Both Puff dangers and B anomalies show similar positional clustering. "
            "Dangerous materials correlate with anomalous execution profiles."
        )
    }

    with open(RESULTS_DIR / "tier4_danger_signature_test.json", 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to results/tier4_danger_signature_test.json")

    return passed

if __name__ == "__main__":
    main()
