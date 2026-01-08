"""
Forgiving vs Brittle Program Axis Test (SHOT 2)

Question: Is there a skill-level dimension orthogonal to aggressive/conservative?

Success Criteria:
- If orthogonal axis exists -> Tier 4 interpretation: "competency-graded reference"
- If collapses to existing axes -> closure: "no separate skill dimension"

Phase SITD - Shot in the Dark Exploratory Tests
"""

import json
import math
from collections import defaultdict, Counter
import statistics

def load_currier_b_data():
    """Load Currier B tokens by folio."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    folios = defaultdict(list)

    with open(filepath, 'r', encoding='latin-1') as f:
        header = None
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split('\t')
            parts = [p.strip('"') for p in parts]

            if header is None:
                header = parts
                continue

            if len(parts) < 14:
                continue

            token = parts[0]
            folio = parts[2]
            currier = parts[6]
            transcriber = parts[12]

            if currier == 'B' and transcriber == 'H' and token and '*' not in token:
                folios[folio].append(token)

    return folios

# Known hazard source tokens (from Phase 18 forbidden transitions)
HAZARD_SOURCES = {'shey', 'chol', 'chedy', 'dy', 'l', 'or', 'chey'}
HAZARD_TARGETS = {'aiin', 'al', 'c', 'r', 'ee', 'dal', 'chol', 'chedy'}

# QO-prefix tokens (known escape routes from HAV phase)
QO_ESCAPE_PREFIXES = ['qo']

# Known regime classifications (from OPS phases)
AGGRESSIVE_FOLIOS = ['f75r', 'f76r', 'f77r', 'f78r', 'f79r', 'f80r']
CONSERVATIVE_FOLIOS = ['f102r', 'f103r', 'f104r', 'f105r', 'f106r', 'f107r']

def is_hazard_token(token):
    """Check if token is hazard-related (source or target of forbidden)."""
    return token in HAZARD_SOURCES or token in HAZARD_TARGETS

def is_escape_token(token):
    """Check if token is a qo-escape (safe transition)."""
    for prefix in QO_ESCAPE_PREFIXES:
        if token.startswith(prefix):
            return True
    return False

def compute_program_metrics(tokens):
    """Compute forgiveness metrics for a program (folio)."""
    if len(tokens) < 10:
        return None

    # 1. Hazard density
    hazard_count = sum(1 for t in tokens if is_hazard_token(t))
    hazard_density = hazard_count / len(tokens)

    # 2. Escape availability (qo-prefix density)
    escape_count = sum(1 for t in tokens if is_escape_token(t))
    escape_density = escape_count / len(tokens)

    # 3. Mean distance to escape
    # For each non-escape token, how far to nearest escape?
    distances = []
    for i, t in enumerate(tokens):
        if not is_escape_token(t):
            # Find nearest escape
            min_dist = float('inf')
            for j, t2 in enumerate(tokens):
                if is_escape_token(t2):
                    dist = abs(i - j)
                    if dist < min_dist:
                        min_dist = dist
            if min_dist < float('inf'):
                distances.append(min_dist)

    mean_escape_distance = statistics.mean(distances) if distances else float('inf')

    # 4. Recovery margin: how many distinct escape tokens available
    unique_escapes = len(set(t for t in tokens if is_escape_token(t)))
    recovery_diversity = unique_escapes / len(tokens)

    # 5. Hazard clustering: do hazards bunch together or spread out?
    hazard_positions = [i for i, t in enumerate(tokens) if is_hazard_token(t)]
    if len(hazard_positions) >= 2:
        hazard_gaps = [hazard_positions[i+1] - hazard_positions[i] for i in range(len(hazard_positions)-1)]
        hazard_spread = statistics.stdev(hazard_gaps) if len(hazard_gaps) > 1 else 0
    else:
        hazard_spread = 0

    # 6. Safe corridor length: longest run without hazards
    max_safe_run = 0
    current_run = 0
    for t in tokens:
        if is_hazard_token(t):
            max_safe_run = max(max_safe_run, current_run)
            current_run = 0
        else:
            current_run += 1
    max_safe_run = max(max_safe_run, current_run)

    return {
        'token_count': len(tokens),
        'hazard_density': hazard_density,
        'escape_density': escape_density,
        'mean_escape_distance': mean_escape_distance,
        'recovery_diversity': recovery_diversity,
        'hazard_spread': hazard_spread,
        'max_safe_run': max_safe_run
    }

def compute_forgiveness_score(metrics):
    """Combine metrics into single forgiveness score (higher = more forgiving)."""
    if metrics is None:
        return None

    # Low hazard density = forgiving
    # High escape density = forgiving
    # Low escape distance = forgiving
    # High recovery diversity = forgiving
    # High safe runs = forgiving

    # Normalize and combine
    score = 0
    score -= metrics['hazard_density'] * 10  # Penalize hazards
    score += metrics['escape_density'] * 10  # Reward escapes
    score -= min(metrics['mean_escape_distance'], 10) / 10  # Penalize far escapes
    score += metrics['recovery_diversity'] * 5  # Reward diverse escapes
    score += min(metrics['max_safe_run'], 50) / 50  # Reward safe corridors

    return score

def main():
    print("=" * 70)
    print("FORGIVING VS BRITTLE PROGRAM AXIS TEST (SHOT 2)")
    print("=" * 70)
    print("\nQuestion: Is there a skill-level axis orthogonal to aggressive/conservative?")
    print("Success: If orthogonal axis exists -> competency-graded reference\n")

    # Load data
    print("Loading data...")
    folios = load_currier_b_data()
    print(f"  B folios: {len(folios)}")

    # Compute metrics for each program
    print("\nComputing program metrics...")
    program_data = {}
    for folio, tokens in folios.items():
        metrics = compute_program_metrics(tokens)
        if metrics:
            metrics['forgiveness'] = compute_forgiveness_score(metrics)
            program_data[folio] = metrics

    print(f"  Programs with sufficient data: {len(program_data)}")

    # === TEST 1: Distribution of forgiveness scores ===
    print("\n" + "-" * 70)
    print("TEST 1: Distribution of Forgiveness Scores")
    print("-" * 70)

    scores = [m['forgiveness'] for m in program_data.values()]
    scores.sort()

    print(f"\n  Min: {min(scores):.3f}")
    print(f"  Max: {max(scores):.3f}")
    print(f"  Mean: {statistics.mean(scores):.3f}")
    print(f"  Stdev: {statistics.stdev(scores):.3f}")
    print(f"  Range: {max(scores) - min(scores):.3f}")

    # Quartiles
    q1 = scores[len(scores)//4]
    q2 = scores[len(scores)//2]
    q3 = scores[3*len(scores)//4]
    print(f"\n  Q1 (25%): {q1:.3f}")
    print(f"  Q2 (50%): {q2:.3f}")
    print(f"  Q3 (75%): {q3:.3f}")

    # === TEST 2: Most forgiving vs most brittle programs ===
    print("\n" + "-" * 70)
    print("TEST 2: Extreme Programs")
    print("-" * 70)

    ranked = sorted(program_data.items(), key=lambda x: x[1]['forgiveness'])

    print("\n--- Most BRITTLE (unforgiving) programs ---")
    print(f"{'Folio':<10} {'Score':>8} {'Hazard%':>8} {'Escape%':>8} {'EscDist':>8}")
    for folio, m in ranked[:10]:
        print(f"{folio:<10} {m['forgiveness']:>8.3f} {m['hazard_density']*100:>7.1f}% {m['escape_density']*100:>7.1f}% {m['mean_escape_distance']:>8.1f}")

    print("\n--- Most FORGIVING programs ---")
    for folio, m in ranked[-10:]:
        print(f"{folio:<10} {m['forgiveness']:>8.3f} {m['hazard_density']*100:>7.1f}% {m['escape_density']*100:>7.1f}% {m['mean_escape_distance']:>8.1f}")

    # === TEST 3: Correlation with known regime classifications ===
    print("\n" + "-" * 70)
    print("TEST 3: Correlation with Aggressive/Conservative")
    print("-" * 70)

    aggressive_scores = [program_data[f]['forgiveness'] for f in AGGRESSIVE_FOLIOS if f in program_data]
    conservative_scores = [program_data[f]['forgiveness'] for f in CONSERVATIVE_FOLIOS if f in program_data]

    if aggressive_scores and conservative_scores:
        print(f"\n  Aggressive folios ({len(aggressive_scores)}): mean forgiveness = {statistics.mean(aggressive_scores):.3f}")
        print(f"  Conservative folios ({len(conservative_scores)}): mean forgiveness = {statistics.mean(conservative_scores):.3f}")

        # Are they different?
        diff = statistics.mean(aggressive_scores) - statistics.mean(conservative_scores)
        overall_std = statistics.stdev(scores)
        effect_size = diff / overall_std if overall_std > 0 else 0

        print(f"\n  Difference: {diff:.3f}")
        print(f"  Effect size (Cohen's d): {effect_size:.3f}")

        if abs(effect_size) < 0.3:
            print("  => WEAK correlation with aggressive/conservative")
        elif abs(effect_size) < 0.8:
            print("  => MODERATE correlation with aggressive/conservative")
        else:
            print("  => STRONG correlation with aggressive/conservative")
    else:
        print("  (Insufficient data for regime comparison)")

    # === TEST 4: Component independence ===
    print("\n" + "-" * 70)
    print("TEST 4: Component Independence")
    print("-" * 70)

    # Check if hazard density and escape density are independent
    hazards = [m['hazard_density'] for m in program_data.values()]
    escapes = [m['escape_density'] for m in program_data.values()]

    # Simple correlation (Pearson-ish)
    mean_h = statistics.mean(hazards)
    mean_e = statistics.mean(escapes)
    cov = sum((h - mean_h) * (e - mean_e) for h, e in zip(hazards, escapes)) / len(hazards)
    std_h = statistics.stdev(hazards)
    std_e = statistics.stdev(escapes)
    corr_he = cov / (std_h * std_e) if std_h > 0 and std_e > 0 else 0

    print(f"\n  Hazard density vs Escape density correlation: {corr_he:.3f}")

    if abs(corr_he) < 0.3:
        print("  => Components are relatively INDEPENDENT")
        print("  => Forgiveness is a distinct dimension, not just inverse of hazard")
    else:
        print("  => Components are CORRELATED")
        print("  => Forgiveness may collapse to simpler metric")

    # === TEST 5: Quartile analysis ===
    print("\n" + "-" * 70)
    print("TEST 5: Quartile Profiles")
    print("-" * 70)

    # Group programs by forgiveness quartile
    quartile_bins = [
        ('Q1 (Brittle)', [f for f, m in program_data.items() if m['forgiveness'] <= q1]),
        ('Q2', [f for f, m in program_data.items() if q1 < m['forgiveness'] <= q2]),
        ('Q3', [f for f, m in program_data.items() if q2 < m['forgiveness'] <= q3]),
        ('Q4 (Forgiving)', [f for f, m in program_data.items() if m['forgiveness'] > q3])
    ]

    print(f"\n{'Quartile':<16} {'Count':>6} {'Hazard%':>8} {'Escape%':>8} {'SafeRun':>8}")
    print("-" * 50)

    for label, members in quartile_bins:
        if members:
            avg_hazard = statistics.mean([program_data[f]['hazard_density'] for f in members])
            avg_escape = statistics.mean([program_data[f]['escape_density'] for f in members])
            avg_safe = statistics.mean([program_data[f]['max_safe_run'] for f in members])
            print(f"{label:<16} {len(members):>6} {avg_hazard*100:>7.1f}% {avg_escape*100:>7.1f}% {avg_safe:>8.1f}")

    # === SUMMARY ===
    print("\n" + "=" * 70)
    print("SUMMARY: Forgiving vs Brittle Axis Test")
    print("=" * 70)

    spread = max(scores) - min(scores)
    spread_in_std = spread / statistics.stdev(scores) if statistics.stdev(scores) > 0 else 0

    print(f"""
    Forgiveness score range: {spread:.3f} ({spread_in_std:.1f} std devs)
    Hazard-Escape correlation: {corr_he:.3f}
    Aggressive/Conservative effect size: {effect_size:.3f}

    """)

    # Decision logic
    if spread_in_std > 3 and abs(corr_he) < 0.5:
        print("""    FINDING: DISTINCT FORGIVENESS AXIS DETECTED

    Programs vary along a forgiving<->brittle continuum that is
    NOT fully explained by hazard density alone.

    Interpretation (Tier 4):
    - The manuscript may serve operators at different skill levels
    - Forgiving programs: more escape routes, spread-out hazards
    - Brittle programs: concentrated hazards, fewer recovery options
    - This is consistent with "competency-graded reference"

    STATUS: POTENTIAL TIER 4 INTERPRETATION
    """)
    elif abs(effect_size) > 0.5:
        print("""    FINDING: FORGIVENESS CORRELATES WITH AGGRESSIVE/CONSERVATIVE

    The forgiving<->brittle axis is NOT orthogonal to known regimes.
    It largely captures the same variance.

    STATUS: CLOSURE (no distinct skill dimension)
    """)
    else:
        print("""    FINDING: WEAK/INCONCLUSIVE SIGNAL

    There is some variation in forgiveness, but:
    - Range is modest
    - May collapse to existing classifications

    STATUS: CLOSURE (insufficient evidence for new axis)
    """)

if __name__ == '__main__':
    main()
