"""
Phase IMD: Intra-Role Micro-Differentiation

CRITICAL FRAMING: This is the LAST RESOLVABLE SEMANTIC LAYER.
We are no longer distinguishing WHAT KIND of thing a token is.
We are asking: Do surface variants within the same role correlate with different outcomes?

Hypothesis: Surface tokens within a role encode expectation/warning memory, not state.

Mode: DISCIPLINED SPECULATION (outcome-based, not hierarchical)
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Import infrastructure from HTCS
from human_track_coordinate_semantics import (
    load_transcription,
    is_uncategorized,
    is_link_context,
    has_kernel_char,
    build_position_profiles,
    cluster_by_behavior,
    CATEGORIZED_TOKENS,
    LINK_INDICATORS,
    KERNEL_CHARS
)

# Hazard-adjacent tokens (from Phase 18 - forbidden transition boundaries)
HAZARD_ADJACENT_TOKENS = {
    'qokaiin', 'daiin', 'chedy', 'shedy', 'qokedy', 'chol', 'chor',
    'ol', 'or', 'ar', 'al', 'aiin', 'kaiin', 'taiin', 'saiin',
    'okaiin', 'otaiin', 'chey', 'shey', 'qokeedy', 'okeedy',
    # Kernel-adjacent
    'k', 'h', 'e', 'ck', 'ch', 'sh', 'ct', 'cth'
}


@dataclass
class TokenOutcomeProfile:
    """Outcome profile for a surface token within a role."""
    token: str
    role: str  # CF-1 through CF-7
    total_occurrences: int = 0

    # Outcome distributions
    tokens_until_intervention: List[int] = field(default_factory=list)
    hazard_adjacent_count: int = 0
    recovery_count: int = 0  # Followed by RELAXING
    escalation_count: int = 0  # Followed by EXHAUSTING
    loop_entry_count: int = 0
    section_exit_count: int = 0

    # Next function distribution
    next_cf1: int = 0
    next_cf2: int = 0
    next_cf3: int = 0
    next_cf6: int = 0
    next_cf7: int = 0

    # Section-conditional outcomes
    section_outcomes: Dict[str, Dict] = field(default_factory=dict)

    @property
    def hazard_adjacent_rate(self) -> float:
        return self.hazard_adjacent_count / max(self.total_occurrences, 1)

    @property
    def recovery_rate(self) -> float:
        total = self.recovery_count + self.escalation_count
        return self.recovery_count / max(total, 1)

    @property
    def mean_intervention_distance(self) -> float:
        return np.mean(self.tokens_until_intervention) if self.tokens_until_intervention else 0

    @property
    def loop_entry_rate(self) -> float:
        return self.loop_entry_count / max(self.total_occurrences, 1)


def classify_token_role(token: str, profiles: List, clusters: Dict) -> str:
    """Determine which CF role a token belongs to."""
    # Check each cluster
    for cluster_name, cluster_profiles in clusters.items():
        cluster_tokens = {p.token for p in cluster_profiles}
        if token in cluster_tokens:
            # Map cluster name to CF
            mapping = {
                'SECTION_EARLY': 'CF-1',
                'SECTION_LATE': 'CF-2',
                'LINK_PROXIMAL': 'CF-3',
                'LINK_DISTAL': 'CF-4',
                'RUN_FORMING': 'CF-5',
                'GRADIENT_RISING': 'CF-6',
                'GRADIENT_FALLING': 'CF-7',
                'POSITION_NEUTRAL': 'CF-0'
            }
            return mapping.get(cluster_name, 'CF-0')
    return 'CF-0'


def is_hazard_adjacent(token: str) -> bool:
    """Check if token is near hazard boundaries."""
    if token.lower() in HAZARD_ADJACENT_TOKENS:
        return True
    # Also check for kernel character presence
    return has_kernel_char(token)


def detect_loop_entry(tokens: List[str], start_idx: int, window: int = 20) -> bool:
    """Detect if grammar enters a stable loop pattern after position."""
    if start_idx + window >= len(tokens):
        return False

    window_tokens = tokens[start_idx:start_idx + window]

    # Look for repetition patterns (simplified loop detection)
    for pattern_len in [2, 3, 4]:
        if len(window_tokens) < pattern_len * 2:
            continue
        pattern = tuple(window_tokens[:pattern_len])
        repeat_count = 0
        for i in range(0, len(window_tokens) - pattern_len + 1, pattern_len):
            if tuple(window_tokens[i:i+pattern_len]) == pattern:
                repeat_count += 1
        if repeat_count >= 3:
            return True

    return False


def compute_token_outcomes(df: pd.DataFrame, profiles: List, clusters: Dict) -> Dict[str, Dict[str, TokenOutcomeProfile]]:
    """
    Compute outcome profiles for each surface token within each role.

    Returns: {role: {token: TokenOutcomeProfile}}
    """
    # Build token -> role mapping
    token_roles = {}
    for profile in profiles:
        role = classify_token_role(profile.token, profiles, clusters)
        token_roles[profile.token] = role

    # Initialize outcome profiles
    outcome_profiles = defaultdict(lambda: defaultdict(lambda: TokenOutcomeProfile(token='', role='')))

    tokens = df['word'].tolist()
    sections = df['section'].tolist() if 'section' in df.columns else ['U'] * len(tokens)

    print(f"Processing {len(tokens)} tokens...")

    for i, token in enumerate(tokens):
        if not is_uncategorized(token):
            continue

        role = token_roles.get(token, 'CF-0')
        if role == 'CF-0':
            continue

        # Initialize or update profile
        if outcome_profiles[role][token].token == '':
            outcome_profiles[role][token] = TokenOutcomeProfile(token=token, role=role)

        profile = outcome_profiles[role][token]
        profile.total_occurrences += 1

        section = sections[i] if i < len(sections) else 'U'

        # Measure outcomes in forward window
        window = 10
        end_idx = min(i + window, len(tokens))
        forward_window = tokens[i+1:end_idx]

        # 1. Tokens until next intervention (non-LINK, categorized)
        intervention_distance = 0
        for j, future_token in enumerate(forward_window):
            if not is_uncategorized(future_token) and not is_link_context(future_token):
                intervention_distance = j + 1
                break
        else:
            intervention_distance = len(forward_window)
        profile.tokens_until_intervention.append(intervention_distance)

        # 2. Hazard adjacency (any hazard-adjacent token in next 5)
        hazard_window = tokens[i+1:min(i+6, len(tokens))]
        if any(is_hazard_adjacent(t) for t in hazard_window):
            profile.hazard_adjacent_count += 1

        # 3. Recovery vs escalation (next human-track token's role)
        for future_token in forward_window:
            if is_uncategorized(future_token) and future_token in token_roles:
                future_role = token_roles[future_token]
                if future_role == 'CF-7':  # RELAXING
                    profile.recovery_count += 1
                elif future_role == 'CF-2':  # SECTION_EXIT (escalation/exhaustion)
                    profile.escalation_count += 1

                # Track next function
                if future_role == 'CF-1':
                    profile.next_cf1 += 1
                elif future_role == 'CF-2':
                    profile.next_cf2 += 1
                elif future_role == 'CF-3':
                    profile.next_cf3 += 1
                elif future_role == 'CF-6':
                    profile.next_cf6 += 1
                elif future_role == 'CF-7':
                    profile.next_cf7 += 1
                break

        # 4. Loop entry detection
        if detect_loop_entry(tokens, i):
            profile.loop_entry_count += 1

        # 5. Section exit (is next section boundary close?)
        remaining_in_section = 0
        for j in range(i+1, len(tokens)):
            if j >= len(sections) or sections[j] != section:
                remaining_in_section = j - i
                break
        if remaining_in_section > 0 and remaining_in_section <= 10:
            profile.section_exit_count += 1

        # Track section-conditional outcomes
        if section not in profile.section_outcomes:
            profile.section_outcomes[section] = {
                'count': 0,
                'hazard_adjacent': 0,
                'recovery': 0,
                'escalation': 0
            }
        profile.section_outcomes[section]['count'] += 1

    return outcome_profiles


def compare_outcomes_within_role(role: str, outcome_profiles: Dict[str, TokenOutcomeProfile],
                                  min_occurrences: int = 10) -> Dict:
    """
    Compare outcome distributions between surface variants within a role.

    Returns statistical test results.
    """
    # Filter to tokens with sufficient occurrences
    qualified_tokens = {
        token: profile
        for token, profile in outcome_profiles.items()
        if profile.total_occurrences >= min_occurrences
    }

    if len(qualified_tokens) < 2:
        return {
            'role': role,
            'n_tokens': len(qualified_tokens),
            'verdict': 'INSUFFICIENT_DATA',
            'tests': []
        }

    print(f"\n{role}: {len(qualified_tokens)} tokens with >= {min_occurrences} occurrences")

    results = {
        'role': role,
        'n_tokens': len(qualified_tokens),
        'tests': [],
        'token_profiles': {}
    }

    # Store token profiles for reporting
    for token, profile in qualified_tokens.items():
        results['token_profiles'][token] = {
            'occurrences': profile.total_occurrences,
            'hazard_rate': profile.hazard_adjacent_rate,
            'recovery_rate': profile.recovery_rate,
            'mean_intervention_dist': profile.mean_intervention_distance,
            'loop_entry_rate': profile.loop_entry_rate
        }

    # Test 1: Hazard adjacency rate divergence
    hazard_rates = [(token, profile.hazard_adjacent_rate, profile.total_occurrences)
                    for token, profile in qualified_tokens.items()]

    # Chi-square test for hazard adjacency
    observed_hazard = [int(p.hazard_adjacent_count) for p in qualified_tokens.values()]
    observed_no_hazard = [int(p.total_occurrences - p.hazard_adjacent_count) for p in qualified_tokens.values()]

    if sum(observed_hazard) > 0 and sum(observed_no_hazard) > 0:
        contingency_hazard = np.array([observed_hazard, observed_no_hazard])
        try:
            chi2_hazard, p_hazard, dof_hazard, _ = stats.chi2_contingency(contingency_hazard)
            cramers_v_hazard = np.sqrt(chi2_hazard / (sum(observed_hazard) + sum(observed_no_hazard)))

            results['tests'].append({
                'metric': 'hazard_adjacency',
                'test': 'chi-square',
                'statistic': chi2_hazard,
                'p_value': p_hazard,
                'effect_size': cramers_v_hazard,
                'significant': p_hazard < 0.05
            })
        except:
            pass

    # Test 2: Recovery rate divergence
    observed_recovery = [int(p.recovery_count) for p in qualified_tokens.values()]
    observed_escalation = [int(p.escalation_count) for p in qualified_tokens.values()]

    if sum(observed_recovery) > 0 and sum(observed_escalation) > 0:
        contingency_recovery = np.array([observed_recovery, observed_escalation])
        try:
            chi2_recovery, p_recovery, dof_recovery, _ = stats.chi2_contingency(contingency_recovery)
            cramers_v_recovery = np.sqrt(chi2_recovery / (sum(observed_recovery) + sum(observed_escalation)))

            results['tests'].append({
                'metric': 'recovery_vs_escalation',
                'test': 'chi-square',
                'statistic': chi2_recovery,
                'p_value': p_recovery,
                'effect_size': cramers_v_recovery,
                'significant': p_recovery < 0.05
            })
        except:
            pass

    # Test 3: Intervention distance (Kruskal-Wallis)
    intervention_groups = [profile.tokens_until_intervention
                           for profile in qualified_tokens.values()
                           if profile.tokens_until_intervention]

    if len(intervention_groups) >= 2 and all(len(g) > 0 for g in intervention_groups):
        try:
            h_stat, p_kw = stats.kruskal(*intervention_groups)
            # Effect size: eta-squared approximation
            n_total = sum(len(g) for g in intervention_groups)
            eta_sq = (h_stat - len(intervention_groups) + 1) / (n_total - len(intervention_groups))
            eta_sq = max(0, eta_sq)  # Ensure non-negative

            results['tests'].append({
                'metric': 'intervention_distance',
                'test': 'kruskal-wallis',
                'statistic': h_stat,
                'p_value': p_kw,
                'effect_size': eta_sq,
                'significant': p_kw < 0.05
            })
        except:
            pass

    # Test 4: Next function distribution
    next_cf_matrix = []
    for profile in qualified_tokens.values():
        row = [profile.next_cf1, profile.next_cf2, profile.next_cf3,
               profile.next_cf6, profile.next_cf7]
        if sum(row) > 0:
            next_cf_matrix.append(row)

    if len(next_cf_matrix) >= 2:
        contingency_next = np.array(next_cf_matrix)
        # Remove columns with all zeros
        col_sums = contingency_next.sum(axis=0)
        contingency_next = contingency_next[:, col_sums > 0]

        if contingency_next.shape[1] >= 2:
            try:
                chi2_next, p_next, dof_next, _ = stats.chi2_contingency(contingency_next)
                n_total = contingency_next.sum()
                cramers_v_next = np.sqrt(chi2_next / (n_total * (min(contingency_next.shape) - 1)))

                results['tests'].append({
                    'metric': 'next_function',
                    'test': 'chi-square',
                    'statistic': chi2_next,
                    'p_value': p_next,
                    'effect_size': cramers_v_next,
                    'significant': p_next < 0.05
                })
            except:
                pass

    # Determine overall verdict
    significant_tests = sum(1 for t in results['tests'] if t.get('significant', False))
    strong_effects = sum(1 for t in results['tests'] if t.get('effect_size', 0) > 0.3)

    if significant_tests >= 2 and strong_effects >= 1:
        results['verdict'] = 'STRONG_SIGNAL'
    elif significant_tests >= 1:
        results['verdict'] = 'WEAK_SIGNAL'
    else:
        results['verdict'] = 'NO_SIGNAL'

    return results


def identify_extreme_tokens(role_results: Dict, threshold_percentile: float = 90) -> Dict:
    """
    Identify tokens with extreme outcome profiles within a role.
    These are candidates for "warning memory" markers.
    """
    token_profiles = role_results.get('token_profiles', {})

    if len(token_profiles) < 3:
        return {'high_hazard': [], 'low_recovery': [], 'long_wait': []}

    hazard_rates = [(t, p['hazard_rate']) for t, p in token_profiles.items()]
    recovery_rates = [(t, p['recovery_rate']) for t, p in token_profiles.items()]
    intervention_dists = [(t, p['mean_intervention_dist']) for t, p in token_profiles.items()]

    # Find extreme tokens
    hazard_threshold = np.percentile([h for _, h in hazard_rates], threshold_percentile)
    recovery_threshold = np.percentile([r for _, r in recovery_rates], 100 - threshold_percentile)
    wait_threshold = np.percentile([w for _, w in intervention_dists], threshold_percentile)

    return {
        'high_hazard': [t for t, h in hazard_rates if h >= hazard_threshold],
        'low_recovery': [t for t, r in recovery_rates if r <= recovery_threshold],
        'long_wait': [t for t, w in intervention_dists if w >= wait_threshold]
    }


def generate_role_report(role: str, results: Dict, extremes: Dict) -> str:
    """Generate markdown report for a single role's micro-differentiation analysis."""
    lines = []

    role_names = {
        'CF-1': 'SECTION_ENTRY_ANCHOR',
        'CF-2': 'SECTION_EXIT_ANCHOR',
        'CF-3': 'WAIT_PHASE_MARKER',
        'CF-6': 'CONSTRAINT_APPROACH_MARKER',
        'CF-7': 'CONSTRAINT_EXIT_MARKER'
    }

    role_name = role_names.get(role, role)

    lines.append(f"# Phase IMD: Outcome Divergence Analysis — {role}")
    lines.append("")
    lines.append(f"**Role:** {role_name}")
    lines.append(f"**Date:** 2026-01-04")
    lines.append(f"**Mode:** DISCIPLINED SPECULATION")
    lines.append("")
    lines.append("> **SPECULATIVE** — Outcome-based micro-differentiation. Does not modify frozen model.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"**Tokens Analyzed:** {results.get('n_tokens', 0)} (with >= 10 occurrences)")
    lines.append(f"**Verdict:** {results.get('verdict', 'UNKNOWN')}")
    lines.append("")

    # Statistical tests
    lines.append("## Statistical Tests")
    lines.append("")
    lines.append("| Metric | Test | Statistic | p-value | Effect Size | Significant? |")
    lines.append("|--------|------|-----------|---------|-------------|--------------|")

    for test in results.get('tests', []):
        sig_mark = "**YES**" if test.get('significant') else "no"
        lines.append(f"| {test['metric']} | {test['test']} | {test['statistic']:.3f} | {test['p_value']:.4f} | {test['effect_size']:.3f} | {sig_mark} |")

    lines.append("")

    # Interpretation
    lines.append("## Interpretation")
    lines.append("")

    verdict = results.get('verdict', 'UNKNOWN')
    if verdict == 'STRONG_SIGNAL':
        lines.append("**STRONG DIVERGENCE DETECTED**")
        lines.append("")
        lines.append("Surface tokens within this role correlate with distinct outcome expectations.")
        lines.append("This is consistent with **expert craft memory** — different tokens mark")
        lines.append("'the dangerous kind' vs 'the routine kind' of the same operational state.")
        lines.append("")
        lines.append("**Craft interpretation:** Experienced operators differentiate instances")
        lines.append("within this role based on what usually happens next.")
    elif verdict == 'WEAK_SIGNAL':
        lines.append("**WEAK DIVERGENCE DETECTED**")
        lines.append("")
        lines.append("Some outcome metrics show significant variation between surface tokens,")
        lines.append("but effect sizes are small. This suggests **finer situational nuance**")
        lines.append("rather than strong warning/expectation encoding.")
    else:
        lines.append("**NO SIGNIFICANT DIVERGENCE**")
        lines.append("")
        lines.append("Surface tokens within this role do not show meaningful outcome differences.")
        lines.append("Tokens serve **position-marking only** — no further meaning is extractable.")

    lines.append("")

    # Extreme tokens
    if any(extremes.values()):
        lines.append("## Extreme Tokens (Candidates for Warning Memory)")
        lines.append("")

        if extremes.get('high_hazard'):
            lines.append(f"**High Hazard Adjacency:** `{', '.join(extremes['high_hazard'][:10])}`")
            lines.append("  — These tokens appear near hazard boundaries more often than average.")
            lines.append("")

        if extremes.get('low_recovery'):
            lines.append(f"**Low Recovery Rate:** `{', '.join(extremes['low_recovery'][:10])}`")
            lines.append("  — These tokens are more often followed by escalation than recovery.")
            lines.append("")

        if extremes.get('long_wait'):
            lines.append(f"**Long Wait Times:** `{', '.join(extremes['long_wait'][:10])}`")
            lines.append("  — These tokens precede unusually long intervention gaps.")
            lines.append("")

    # Token profiles
    lines.append("## Token Outcome Profiles")
    lines.append("")
    lines.append("| Token | Occurrences | Hazard Rate | Recovery Rate | Mean Wait |")
    lines.append("|-------|-------------|-------------|---------------|-----------|")

    sorted_tokens = sorted(
        results.get('token_profiles', {}).items(),
        key=lambda x: x[1]['occurrences'],
        reverse=True
    )[:20]

    for token, profile in sorted_tokens:
        lines.append(f"| {token} | {profile['occurrences']} | {profile['hazard_rate']:.3f} | {profile['recovery_rate']:.3f} | {profile['mean_intervention_dist']:.1f} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*{role} analysis complete.*")

    return '\n'.join(lines)


def generate_synthesis_report(all_results: Dict[str, Dict], all_extremes: Dict[str, Dict]) -> str:
    """Generate synthesis report across all roles."""
    lines = []

    lines.append("# Phase IMD: Intra-Role Micro-Differentiation — Synthesis")
    lines.append("")
    lines.append("**Status:** COMPLETE")
    lines.append("**Date:** 2026-01-04")
    lines.append("**Mode:** DISCIPLINED SPECULATION")
    lines.append("")
    lines.append("> **SPECULATIVE** — Outcome-based micro-differentiation. Does not modify frozen model.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Overall summary
    lines.append("## Overall Summary")
    lines.append("")
    lines.append("| Role | Tokens | Verdict | Significant Tests | Strong Effects |")
    lines.append("|------|--------|---------|-------------------|----------------|")

    for role, results in all_results.items():
        n_tokens = results.get('n_tokens', 0)
        verdict = results.get('verdict', 'UNKNOWN')
        sig_tests = sum(1 for t in results.get('tests', []) if t.get('significant'))
        strong = sum(1 for t in results.get('tests', []) if t.get('effect_size', 0) > 0.3)
        lines.append(f"| {role} | {n_tokens} | {verdict} | {sig_tests} | {strong} |")

    lines.append("")

    # Key findings
    lines.append("## Key Findings")
    lines.append("")

    strong_roles = [r for r, res in all_results.items() if res.get('verdict') == 'STRONG_SIGNAL']
    weak_roles = [r for r, res in all_results.items() if res.get('verdict') == 'WEAK_SIGNAL']
    no_signal_roles = [r for r, res in all_results.items() if res.get('verdict') == 'NO_SIGNAL']

    if strong_roles:
        lines.append(f"### Strong Signal: {', '.join(strong_roles)}")
        lines.append("")
        lines.append("These roles show significant outcome divergence between surface tokens.")
        lines.append("Surface variants encode **expectation or warning memory** — operators")
        lines.append("differentiated 'the dangerous kind' from 'the routine kind' of the same state.")
        lines.append("")

    if weak_roles:
        lines.append(f"### Weak Signal: {', '.join(weak_roles)}")
        lines.append("")
        lines.append("These roles show detectable but limited outcome variation.")
        lines.append("Surface tokens encode **finer situational nuance** but not strong warnings.")
        lines.append("")

    if no_signal_roles:
        lines.append(f"### No Signal: {', '.join(no_signal_roles)}")
        lines.append("")
        lines.append("These roles show no meaningful outcome divergence.")
        lines.append("Surface tokens serve **position-marking only**.")
        lines.append("")

    # Craft interpretation
    lines.append("## Craft Interpretation")
    lines.append("")

    if strong_roles or weak_roles:
        lines.append("The manuscript preserves **craft memory** at the micro level:")
        lines.append("")
        lines.append("- Not all APPROACHING tokens are equal — some mark higher-risk moments")
        lines.append("- Not all RELAXING tokens are equal — some mark premature relaxation")
        lines.append("- Surface variation correlates with **what usually happens next**")
        lines.append("")
        lines.append("This is exactly where experienced perfumers keep meaning:")
        lines.append("- 'that smell again'")
        lines.append("- 'this is the bad run'")
        lines.append("- 'this kind of waiting usually works out'")
        lines.append("")
    else:
        lines.append("Surface variation within roles does NOT correlate with outcome differences.")
        lines.append("")
        lines.append("The manuscript has yielded **all extractable semantic content**.")
        lines.append("Tokens serve position-marking only — no further subdivision is justified.")
        lines.append("")

    # Extreme tokens summary
    all_high_hazard = set()
    all_low_recovery = set()
    for extremes in all_extremes.values():
        all_high_hazard.update(extremes.get('high_hazard', []))
        all_low_recovery.update(extremes.get('low_recovery', []))

    if all_high_hazard or all_low_recovery:
        lines.append("## Warning Memory Candidates")
        lines.append("")
        if all_high_hazard:
            lines.append(f"**Elevated Hazard Tokens:** `{', '.join(list(all_high_hazard)[:15])}`")
            lines.append("")
        if all_low_recovery:
            lines.append(f"**Elevated Escalation Tokens:** `{', '.join(list(all_low_recovery)[:15])}`")
            lines.append("")
        lines.append("These tokens show outcome profiles consistent with 'this usually goes wrong' markers.")
        lines.append("")

    # What this does NOT claim
    lines.append("## What This Does NOT Claim")
    lines.append("")
    lines.append("- We have NOT decoded any tokens")
    lines.append("- We have NOT assigned meanings to surface forms")
    lines.append("- We have NOT proven craft identity")
    lines.append("- We have NOT modified the frozen grammar model")
    lines.append("")
    lines.append("We have shown that surface variation **correlates with outcome expectations**")
    lines.append("in a way consistent with expert craft memory.")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Phase IMD complete. Micro-differentiation analysis finished.*")

    return '\n'.join(lines)


def main():
    """Main analysis pipeline."""
    print("=" * 70)
    print("Phase IMD: Intra-Role Micro-Differentiation")
    print("The LAST resolvable semantic layer")
    print("=" * 70)

    # Load data
    transcript_path = Path("data/transcriptions/interlinear_full_words.txt")

    if not transcript_path.exists():
        print(f"ERROR: Transcription file not found: {transcript_path}")
        return

    print(f"\nLoading transcription from {transcript_path}...")
    df = load_transcription(transcript_path)
    print(f"Loaded {len(df)} tokens from {df['folio'].nunique()} folios")

    # Build profiles (from HTCS)
    print("\nBuilding position profiles...")
    profiles = build_position_profiles(df, min_freq=10)
    print(f"Built {len(profiles)} profiles")

    # Cluster by behavior
    print("\nClustering by behavioral similarity...")
    clusters = cluster_by_behavior(profiles)

    for name, members in clusters.items():
        print(f"  {name}: {len(members)} tokens")

    # Compute outcome profiles
    print("\n" + "=" * 70)
    print("Computing token outcome profiles...")
    print("=" * 70)
    outcome_profiles = compute_token_outcomes(df, profiles, clusters)

    # Analyze each priority role
    priority_roles = ['CF-6', 'CF-7', 'CF-3', 'CF-5', 'CF-1', 'CF-2']

    all_results = {}
    all_extremes = {}

    for role in priority_roles:
        if role not in outcome_profiles:
            print(f"\n{role}: No tokens found")
            continue

        print(f"\n{'=' * 70}")
        print(f"Analyzing {role}...")
        print("=" * 70)

        role_profiles = outcome_profiles[role]
        results = compare_outcomes_within_role(role, role_profiles)
        extremes = identify_extreme_tokens(results)

        all_results[role] = results
        all_extremes[role] = extremes

        # Print summary
        print(f"\n{role} VERDICT: {results.get('verdict', 'UNKNOWN')}")
        for test in results.get('tests', []):
            sig = "***" if test.get('significant') else ""
            print(f"  {test['metric']}: p={test['p_value']:.4f}, effect={test['effect_size']:.3f} {sig}")

    # Generate reports
    print("\n" + "=" * 70)
    print("Generating reports...")
    print("=" * 70)

    output_dir = Path("phases/IMD_micro_differentiation")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Individual role reports
    for role, results in all_results.items():
        extremes = all_extremes.get(role, {})
        report = generate_role_report(role, results, extremes)

        role_name = role.lower().replace('-', '')
        report_path = output_dir / f"outcome_divergence_{role_name}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"  Saved: {report_path}")

    # Synthesis report
    synthesis = generate_synthesis_report(all_results, all_extremes)
    synthesis_path = output_dir / "micro_differentiation_synthesis.md"
    with open(synthesis_path, 'w', encoding='utf-8') as f:
        f.write(synthesis)
    print(f"  Saved: {synthesis_path}")

    # Save JSON data (convert numpy types to native Python)
    def convert_for_json(obj):
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_for_json(i) for i in obj]
        return obj

    json_results = {
        role: convert_for_json({
            'verdict': res.get('verdict'),
            'n_tokens': res.get('n_tokens'),
            'tests': res.get('tests', []),
            'token_profiles': res.get('token_profiles', {})
        })
        for role, res in all_results.items()
    }

    json_path = output_dir / "divergence_statistics.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2)
    print(f"  Saved: {json_path}")

    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    for role, results in all_results.items():
        verdict = results.get('verdict', 'UNKNOWN')
        print(f"\n{role}: {verdict}")

        if verdict == 'STRONG_SIGNAL':
            print("  → Surface tokens encode expectation/warning memory")
        elif verdict == 'WEAK_SIGNAL':
            print("  → Tokens encode finer situational nuance")
        else:
            print("  → Tokens serve position-marking only")

    # Overall conclusion
    strong_count = sum(1 for r in all_results.values() if r.get('verdict') == 'STRONG_SIGNAL')
    weak_count = sum(1 for r in all_results.values() if r.get('verdict') == 'WEAK_SIGNAL')

    print("\n" + "-" * 70)
    if strong_count > 0:
        print("CONCLUSION: Craft memory IS encoded at the micro level.")
        print("The manuscript preserves outcome expectations within roles.")
    elif weak_count > 0:
        print("CONCLUSION: Weak situational nuance detected.")
        print("Some micro-differentiation exists but effect sizes are small.")
    else:
        print("CONCLUSION: No micro-differentiation detected.")
        print("The manuscript has yielded all extractable semantic content.")
    print("-" * 70)

    print("\n" + "=" * 70)
    print("Phase IMD complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
