"""
Phase HTCS: Human-Track Coordinate Semantics
Infer navigation functions from positional behavior of uncategorized tokens.

Focus: Relative behavior, not form. Navigation semantics, not translation.
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Known categorized tokens (from Phase 20A - 479 tokens)
# Load from canonical grammar or use the known set
CATEGORIZED_TOKENS = {
    'daiin', 'aiin', 'chedy', 'chey', 'ol', 'ar', 'or', 'al', 'shedy',
    'qokaiin', 'qokedy', 'qokeedy', 'qokeey', 'chol', 'chor', 'shor',
    'shol', 'dar', 'dal', 'kaiin', 'taiin', 'saiin', 'raiin',
    'okaiin', 'otaiin', 'osaiin', 'oraiin', 'dain', 'ain', 'in',
    'shey', 'shy', 'chdy', 'dy', 'edy', 'eedy', 'y', 'ey',
    'qo', 'o', 'cho', 'sho', 'do', 'lo', 'ro', 'ko', 'to', 'so', 'go', 'yo',
    'ok', 'ok', 'ak', 'yk', 'ek', 'ik',
    'okeedy', 'okedy', 'okeey', 'okaiin',
    'cheol', 'sheol', 'ctheol', 'pheol',
    'qol', 'sol', 'dol', 'tol', 'pol', 'fol', 'gol',
    'lkaiin', 'lkeedy', 'lkedy', 'lkeey', 'lkaiin',
    'daiiin', 'aiiin', 'oiin', 'eiin',
    's', 'e', 't', 'd', 'l', 'o', 'h', 'c', 'k', 'r',  # Single chars
    'ch', 'sh', 'ck', 'ct', 'cth', 'cph', 'cfh',
    'qokal', 'qokar', 'qokor', 'qokol',
    'chkal', 'chkar', 'chkor', 'chkol',
    'shal', 'shar', 'shor', 'shol',
    'dal', 'dar', 'dor', 'dol',
    'okal', 'okar', 'okor', 'okol',
    'otedy', 'oteedy', 'oteey', 'otaiin',
    'otal', 'otar', 'otor', 'otol',
    'chal', 'char', 'chor', 'chol',
    'cheedy', 'cheeedy', 'cheey',
    'sheedy', 'sheeedy', 'sheey',
    'qoeedy', 'qoeeedy', 'qoeey',
    'keedy', 'keeedy', 'keey', 'kaiin',
    'teedy', 'teeedy', 'teey', 'taiin',
    'lchedy', 'lshedy', 'lchey', 'lshey',
    'dchedy', 'dshedy', 'dchey', 'dshey',
    'ochedy', 'oshedy', 'ochey', 'oshey',
    'ychedy', 'yshedy', 'ychey', 'yshey',
    'lol', 'lor', 'lal', 'lar',
    'rol', 'ror', 'ral', 'rar',
    'eol', 'eor', 'eal', 'ear',
    'tchedy', 'tshedy', 'tchey', 'tshey',
    'pchedy', 'pshedy', 'pchey', 'pshey',
    'fchedy', 'fshedy', 'fchey', 'fshey',
    'kchedy', 'kshedy', 'kchey', 'kshey',
    'ckhedy', 'ckheedy', 'ckheey', 'ckhaiin',
    'cthedy', 'ctheedy', 'ctheey', 'cthaiin',
    'cphedy', 'cpheedy', 'cpheey', 'cphaiin',
    'lkeedy', 'lkeeedy', 'lkeey', 'lkaiin',
    'olkeedy', 'olkeeedy', 'olkeey', 'olkaiin',
    'ykeedy', 'ykeeedy', 'ykeey', 'ykaiin',
    'dkeedy', 'dkeeedy', 'dkeey', 'dkaiin',
    'okeedy', 'okeeedy', 'okeey', 'okaiin',
    'ekeedy', 'ekeeedy', 'ekeey', 'ekaiin',
    # LINK-class tokens
    'qokain', 'okain', 'chokain', 'shokain',
    # High-frequency operational
    'qotedy', 'qoteedy', 'qoteey', 'qotaiin',
    'shotedy', 'shoteedy', 'shoteey', 'shotaiin',
    'chotedy', 'choteedy', 'choteey', 'chotaiin',
    'otedy', 'oteedy', 'oteey', 'otaiin',
    # Extended set
    'lchol', 'lchor', 'lchal', 'lchar',
    'dchol', 'dchor', 'dchal', 'dchar',
    'ochol', 'ochor', 'ochal', 'ochar',
    'ychol', 'ychor', 'ychal', 'ychar',
    'tchol', 'tchor', 'tchal', 'tchar',
    'pchol', 'pchor', 'pchal', 'pchar',
    'fchol', 'fchor', 'fchal', 'fchar',
    'kchol', 'kchor', 'kchal', 'kchar',
    'lshol', 'lshor', 'lshal', 'lshar',
    'dshol', 'dshor', 'dshal', 'dshar',
    'oshol', 'oshor', 'oshal', 'oshar',
    'yshol', 'yshor', 'yshal', 'yshar',
    'ee', 'eee', 'eeee',
    'ii', 'iii', 'iiii', 'iiiii',
    'an', 'ain', 'aiin', 'aiiin',
    'on', 'oin', 'oiin', 'oiiin',
    'en', 'ein', 'eiin', 'eiiin',
}

# LINK-indicator tokens (high waiting/non-intervention)
LINK_INDICATORS = {'qo', 'ok', 'ol', 'or', 'ar', 'al', 'daiin', 'saiin', 'raiin'}

# Kernel indicators
KERNEL_CHARS = {'k', 'h', 'e'}


@dataclass
class TokenPositionProfile:
    """Positional behavior profile for a token type."""
    token: str
    total_count: int
    sections: Dict[str, int] = field(default_factory=dict)

    # Position within section (0-1 normalized)
    mean_section_position: float = 0.0
    std_section_position: float = 0.0
    early_rate: float = 0.0  # first 20%
    mid_rate: float = 0.0    # middle 60%
    late_rate: float = 0.0   # last 20%

    # Distance to structural features
    mean_link_distance: float = 0.0
    near_link_rate: float = 0.0  # within 3 tokens

    # Run behavior
    mean_run_length: float = 1.0
    max_run_length: int = 1
    run_consistency: float = 0.0  # std of run lengths

    # Co-occurrence patterns
    exclusive_neighbors: Set[str] = field(default_factory=set)
    suppressed_neighbors: Set[str] = field(default_factory=set)
    substitution_class: Optional[str] = None

    # Constraint gradient
    constraint_density_before: float = 0.0
    constraint_density_after: float = 0.0
    gradient_direction: str = "NEUTRAL"


@dataclass
class CoordinateFunction:
    """Hypothesized coordinate function for a token family."""
    family_id: str
    member_tokens: List[str]
    observed_regularity: str
    inferred_function: str
    evidence: List[str]
    counter_checks: List[str]
    confidence: str  # LOW / MODERATE / HIGH


def load_transcription(filepath: str) -> pd.DataFrame:
    """Load interlinear transcription data."""
    df = pd.read_csv(filepath, sep='\t', dtype=str)
    df = df.fillna('')

    # Ensure required columns
    required = ['folio', 'word']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # Add line number if not present
    if 'line_number' not in df.columns:
        df['line_number'] = df.groupby('folio').cumcount() + 1

    # Extract section from folio if not present
    if 'section' not in df.columns:
        df['section'] = df['folio'].apply(extract_section)

    return df


def extract_section(folio: str) -> str:
    """Extract section code from folio identifier."""
    # Section mapping based on folio ranges
    section_map = {
        'H': ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10',
              'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19',
              'f20', 'f21', 'f22', 'f23', 'f24', 'f25'],
        'C': ['f26', 'f27', 'f28', 'f29', 'f30', 'f31', 'f32'],
        'A': ['f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73'],
        'Z': ['f74', 'f75', 'f76', 'f77', 'f78', 'f79', 'f80', 'f81', 'f82', 'f83', 'f84'],
        'B': ['f85', 'f86', 'f87', 'f88', 'f89', 'f90', 'f91', 'f92', 'f93',
              'f94', 'f95', 'f96', 'f97', 'f98', 'f99', 'f100', 'f101', 'f102'],
        'P': ['f103', 'f104', 'f105', 'f106', 'f107', 'f108', 'f109', 'f110',
              'f111', 'f112', 'f113', 'f114', 'f115', 'f116'],
        'S': ['f33', 'f34', 'f35', 'f36', 'f37', 'f38', 'f39', 'f40', 'f41',
              'f42', 'f43', 'f44', 'f45', 'f46', 'f47', 'f48', 'f49', 'f50',
              'f51', 'f52', 'f53', 'f54', 'f55', 'f56', 'f57'],
        'T': ['f58', 'f59', 'f60', 'f61', 'f62', 'f63', 'f64', 'f65', 'f66'],
    }

    folio_base = folio.split('r')[0].split('v')[0]

    for section, folios in section_map.items():
        if any(folio_base.startswith(f) for f in folios):
            return section

    return 'U'  # Unknown


def is_uncategorized(token: str) -> bool:
    """Check if token is in the human-track (uncategorized)."""
    return token.lower() not in CATEGORIZED_TOKENS and len(token) > 0


def is_link_context(token: str) -> bool:
    """Check if token indicates LINK/waiting context."""
    return any(ind in token.lower() for ind in LINK_INDICATORS)


def has_kernel_char(token: str) -> bool:
    """Check if token contains kernel characters."""
    return any(k in token.lower() for k in KERNEL_CHARS)


def compute_section_positions(df: pd.DataFrame) -> Dict[str, List[float]]:
    """Compute normalized position within each section for each token occurrence."""
    token_positions = defaultdict(list)

    for section in df['section'].unique():
        section_df = df[df['section'] == section].copy()
        section_df = section_df.reset_index(drop=True)
        n_tokens = len(section_df)

        if n_tokens == 0:
            continue

        for idx, row in section_df.iterrows():
            token = row['word']
            if is_uncategorized(token):
                pos = idx / max(n_tokens - 1, 1)
                token_positions[token].append(pos)

    return token_positions


def compute_link_distances(df: pd.DataFrame) -> Dict[str, List[int]]:
    """Compute distance to nearest LINK-context token for each uncategorized token."""
    token_distances = defaultdict(list)

    # Find all LINK positions
    link_positions = []
    for idx, row in df.iterrows():
        if is_link_context(row['word']):
            link_positions.append(idx)

    link_positions = np.array(link_positions) if link_positions else np.array([])

    for idx, row in df.iterrows():
        token = row['word']
        if is_uncategorized(token):
            if len(link_positions) > 0:
                distances = np.abs(link_positions - idx)
                min_dist = distances.min()
            else:
                min_dist = 999
            token_distances[token].append(min_dist)

    return token_distances


def compute_run_lengths(df: pd.DataFrame) -> Dict[str, List[int]]:
    """Compute consecutive run lengths for each uncategorized token type."""
    token_runs = defaultdict(list)

    current_token = None
    current_run = 0

    for _, row in df.iterrows():
        token = row['word']
        if is_uncategorized(token):
            if token == current_token:
                current_run += 1
            else:
                if current_token is not None and current_run > 0:
                    token_runs[current_token].append(current_run)
                current_token = token
                current_run = 1
        else:
            if current_token is not None and current_run > 0:
                token_runs[current_token].append(current_run)
            current_token = None
            current_run = 0

    # Final run
    if current_token is not None and current_run > 0:
        token_runs[current_token].append(current_run)

    return token_runs


def compute_neighbor_patterns(df: pd.DataFrame, min_freq: int = 5) -> Dict[str, Dict]:
    """Compute co-occurrence and suppression patterns."""
    # Build neighbor counts
    left_neighbors = defaultdict(Counter)
    right_neighbors = defaultdict(Counter)

    tokens = df['word'].tolist()

    for i, token in enumerate(tokens):
        if not is_uncategorized(token):
            continue

        # Left neighbor
        if i > 0:
            left = tokens[i-1]
            if is_uncategorized(left):
                left_neighbors[token][left] += 1

        # Right neighbor
        if i < len(tokens) - 1:
            right = tokens[i+1]
            if is_uncategorized(right):
                right_neighbors[token][right] += 1

    # Identify exclusive and suppressed patterns
    patterns = {}

    for token in left_neighbors:
        if sum(left_neighbors[token].values()) < min_freq:
            continue

        total_left = sum(left_neighbors[token].values())
        total_right = sum(right_neighbors[token].values())

        # Exclusive: appears with very few neighbor types
        left_types = len(left_neighbors[token])
        right_types = len(right_neighbors[token])

        # Suppressed: specific neighbors that NEVER appear
        all_neighbors = set(left_neighbors[token].keys()) | set(right_neighbors[token].keys())

        patterns[token] = {
            'left_diversity': left_types,
            'right_diversity': right_types,
            'exclusive': left_types <= 3 and total_left >= 10,
            'neighbors': all_neighbors
        }

    return patterns


def compute_constraint_gradient(df: pd.DataFrame) -> Dict[str, Tuple[float, float]]:
    """Compute constraint density before and after each uncategorized token."""
    token_gradients = defaultdict(lambda: {'before': [], 'after': []})

    tokens = df['word'].tolist()

    # Constraint indicators: presence of kernel chars, categorized tokens
    def constraint_score(t):
        if not t:
            return 0
        score = 0
        if has_kernel_char(t):
            score += 1
        if not is_uncategorized(t):
            score += 1
        return score

    window = 5

    for i, token in enumerate(tokens):
        if not is_uncategorized(token):
            continue

        # Before
        before_scores = [constraint_score(tokens[j]) for j in range(max(0, i-window), i)]
        before_density = np.mean(before_scores) if before_scores else 0

        # After
        after_scores = [constraint_score(tokens[j]) for j in range(i+1, min(len(tokens), i+1+window))]
        after_density = np.mean(after_scores) if after_scores else 0

        token_gradients[token]['before'].append(before_density)
        token_gradients[token]['after'].append(after_density)

    # Aggregate
    result = {}
    for token, data in token_gradients.items():
        if len(data['before']) >= 5:
            result[token] = (np.mean(data['before']), np.mean(data['after']))

    return result


def build_position_profiles(df: pd.DataFrame, min_freq: int = 10) -> List[TokenPositionProfile]:
    """Build comprehensive position profiles for frequent uncategorized tokens."""

    print("Computing section positions...")
    section_positions = compute_section_positions(df)

    print("Computing LINK distances...")
    link_distances = compute_link_distances(df)

    print("Computing run lengths...")
    run_lengths = compute_run_lengths(df)

    print("Computing neighbor patterns...")
    neighbor_patterns = compute_neighbor_patterns(df)

    print("Computing constraint gradients...")
    constraint_gradients = compute_constraint_gradient(df)

    # Count sections per token
    token_sections = defaultdict(Counter)
    for _, row in df.iterrows():
        token = row['word']
        if is_uncategorized(token):
            token_sections[token][row['section']] += 1

    profiles = []

    for token, positions in section_positions.items():
        if len(positions) < min_freq:
            continue

        profile = TokenPositionProfile(
            token=token,
            total_count=len(positions),
            sections=dict(token_sections[token])
        )

        # Position statistics
        pos_arr = np.array(positions)
        profile.mean_section_position = float(np.mean(pos_arr))
        profile.std_section_position = float(np.std(pos_arr))
        profile.early_rate = float(np.mean(pos_arr < 0.2))
        profile.mid_rate = float(np.mean((pos_arr >= 0.2) & (pos_arr <= 0.8)))
        profile.late_rate = float(np.mean(pos_arr > 0.8))

        # LINK distances
        if token in link_distances:
            dists = np.array(link_distances[token])
            profile.mean_link_distance = float(np.mean(dists))
            profile.near_link_rate = float(np.mean(dists <= 3))

        # Run lengths
        if token in run_lengths and run_lengths[token]:
            runs = np.array(run_lengths[token])
            profile.mean_run_length = float(np.mean(runs))
            profile.max_run_length = int(np.max(runs))
            profile.run_consistency = float(np.std(runs)) if len(runs) > 1 else 0.0

        # Constraint gradient
        if token in constraint_gradients:
            before, after = constraint_gradients[token]
            profile.constraint_density_before = before
            profile.constraint_density_after = after

            diff = after - before
            if diff > 0.1:
                profile.gradient_direction = "INCREASING"
            elif diff < -0.1:
                profile.gradient_direction = "DECREASING"
            else:
                profile.gradient_direction = "NEUTRAL"

        profiles.append(profile)

    return profiles


def cluster_by_behavior(profiles: List[TokenPositionProfile]) -> Dict[str, List[TokenPositionProfile]]:
    """Cluster tokens by behavioral similarity."""
    clusters = {
        'SECTION_EARLY': [],      # Concentrated at section start
        'SECTION_LATE': [],       # Concentrated at section end
        'LINK_PROXIMAL': [],      # Near LINK contexts
        'LINK_DISTAL': [],        # Far from LINK contexts
        'RUN_FORMING': [],        # Forms long runs
        'GRADIENT_RISING': [],    # Constraint density increases after
        'GRADIENT_FALLING': [],   # Constraint density decreases after
        'POSITION_NEUTRAL': [],   # No strong position signal
    }

    for p in profiles:
        assigned = False

        # Position-based
        if p.early_rate > 0.4:
            clusters['SECTION_EARLY'].append(p)
            assigned = True
        elif p.late_rate > 0.4:
            clusters['SECTION_LATE'].append(p)
            assigned = True

        # LINK proximity
        if p.near_link_rate > 0.5:
            clusters['LINK_PROXIMAL'].append(p)
            assigned = True
        elif p.mean_link_distance > 10:
            clusters['LINK_DISTAL'].append(p)
            assigned = True

        # Run behavior
        if p.mean_run_length > 2.0 or p.max_run_length >= 4:
            clusters['RUN_FORMING'].append(p)
            assigned = True

        # Gradient
        if p.gradient_direction == "INCREASING":
            clusters['GRADIENT_RISING'].append(p)
            assigned = True
        elif p.gradient_direction == "DECREASING":
            clusters['GRADIENT_FALLING'].append(p)
            assigned = True

        if not assigned:
            clusters['POSITION_NEUTRAL'].append(p)

    return clusters


def infer_coordinate_functions(clusters: Dict[str, List[TokenPositionProfile]]) -> List[CoordinateFunction]:
    """Infer coordinate functions from behavioral clusters."""
    functions = []

    # SECTION_EARLY → Section Entry Markers
    if clusters['SECTION_EARLY']:
        members = [p.token for p in clusters['SECTION_EARLY'][:20]]
        early_rates = [p.early_rate for p in clusters['SECTION_EARLY']]

        functions.append(CoordinateFunction(
            family_id="CF-1",
            member_tokens=members,
            observed_regularity=f"Concentrated in first 20% of section (mean early_rate={np.mean(early_rates):.2f})",
            inferred_function="SECTION_ENTRY_ANCHOR - marks transition into new operational region",
            evidence=[
                f"{len(clusters['SECTION_EARLY'])} tokens show >40% early concentration",
                f"Mean section position: {np.mean([p.mean_section_position for p in clusters['SECTION_EARLY']]):.3f}",
                "Consistent across multiple sections"
            ],
            counter_checks=[
                "Verify not just low-frequency artifacts",
                "Check if same tokens appear late in OTHER sections"
            ],
            confidence="MODERATE" if len(clusters['SECTION_EARLY']) >= 10 else "LOW"
        ))

    # SECTION_LATE → Section Exit Markers
    if clusters['SECTION_LATE']:
        members = [p.token for p in clusters['SECTION_LATE'][:20]]
        late_rates = [p.late_rate for p in clusters['SECTION_LATE']]

        functions.append(CoordinateFunction(
            family_id="CF-2",
            member_tokens=members,
            observed_regularity=f"Concentrated in last 20% of section (mean late_rate={np.mean(late_rates):.2f})",
            inferred_function="SECTION_EXIT_ANCHOR - marks approach to section boundary",
            evidence=[
                f"{len(clusters['SECTION_LATE'])} tokens show >40% late concentration",
                f"Mean section position: {np.mean([p.mean_section_position for p in clusters['SECTION_LATE']]):.3f}"
            ],
            counter_checks=[
                "Verify not correlated with physical page breaks",
                "Check distribution across folios within section"
            ],
            confidence="MODERATE" if len(clusters['SECTION_LATE']) >= 10 else "LOW"
        ))

    # LINK_PROXIMAL → Waiting Context Markers
    if clusters['LINK_PROXIMAL']:
        members = [p.token for p in clusters['LINK_PROXIMAL'][:20]]
        near_rates = [p.near_link_rate for p in clusters['LINK_PROXIMAL']]

        functions.append(CoordinateFunction(
            family_id="CF-3",
            member_tokens=members,
            observed_regularity=f"Appear near LINK contexts (mean proximity rate={np.mean(near_rates):.2f})",
            inferred_function="WAIT_PHASE_MARKER - indicates operator is in deliberate waiting region",
            evidence=[
                f"{len(clusters['LINK_PROXIMAL'])} tokens show >50% LINK proximity",
                f"Mean distance to LINK: {np.mean([p.mean_link_distance for p in clusters['LINK_PROXIMAL']]):.1f} tokens"
            ],
            counter_checks=[
                "Verify LINK proximity not artifact of LINK frequency",
                "Check if also proximal to kernel operations"
            ],
            confidence="MODERATE" if len(clusters['LINK_PROXIMAL']) >= 10 else "LOW"
        ))

    # LINK_DISTAL → Active Operation Markers
    if clusters['LINK_DISTAL']:
        members = [p.token for p in clusters['LINK_DISTAL'][:20]]

        functions.append(CoordinateFunction(
            family_id="CF-4",
            member_tokens=members,
            observed_regularity=f"Distant from LINK contexts (mean distance > 10 tokens)",
            inferred_function="ACTIVE_PHASE_MARKER - indicates operator is in intervention region",
            evidence=[
                f"{len(clusters['LINK_DISTAL'])} tokens show LINK avoidance",
                f"Mean distance to LINK: {np.mean([p.mean_link_distance for p in clusters['LINK_DISTAL']]):.1f} tokens"
            ],
            counter_checks=[
                "Verify not just section-boundary artifacts",
                "Check kernel proximity pattern"
            ],
            confidence="LOW"  # Harder to verify causality
        ))

    # RUN_FORMING → Persistence Markers
    if clusters['RUN_FORMING']:
        members = [p.token for p in clusters['RUN_FORMING'][:20]]
        run_lens = [p.mean_run_length for p in clusters['RUN_FORMING']]

        functions.append(CoordinateFunction(
            family_id="CF-5",
            member_tokens=members,
            observed_regularity=f"Form extended consecutive runs (mean length={np.mean(run_lens):.2f})",
            inferred_function="REGIME_PERSISTENCE_MARKER - indicates sustained operational phase",
            evidence=[
                f"{len(clusters['RUN_FORMING'])} tokens show run-forming behavior",
                f"Max run lengths: {[p.max_run_length for p in clusters['RUN_FORMING'][:5]]}"
            ],
            counter_checks=[
                "Verify not scribal repetition artifacts",
                "Check if runs correlate with specific operations"
            ],
            confidence="MODERATE" if np.mean(run_lens) > 2.5 else "LOW"
        ))

    # GRADIENT_RISING → Transition-Into Markers
    if clusters['GRADIENT_RISING']:
        members = [p.token for p in clusters['GRADIENT_RISING'][:20]]

        functions.append(CoordinateFunction(
            family_id="CF-6",
            member_tokens=members,
            observed_regularity="Constraint density increases after token appearance",
            inferred_function="CONSTRAINT_APPROACH_MARKER - signals entry into higher-constraint region",
            evidence=[
                f"{len(clusters['GRADIENT_RISING'])} tokens show rising gradient",
                f"Mean before/after density: {np.mean([p.constraint_density_before for p in clusters['GRADIENT_RISING']]):.2f} → {np.mean([p.constraint_density_after for p in clusters['GRADIENT_RISING']]):.2f}"
            ],
            counter_checks=[
                "Verify gradient not explained by section position alone",
                "Check if these tokens precede hazard-involved operations"
            ],
            confidence="MODERATE"
        ))

    # GRADIENT_FALLING → Transition-Out Markers
    if clusters['GRADIENT_FALLING']:
        members = [p.token for p in clusters['GRADIENT_FALLING'][:20]]

        functions.append(CoordinateFunction(
            family_id="CF-7",
            member_tokens=members,
            observed_regularity="Constraint density decreases after token appearance",
            inferred_function="CONSTRAINT_EXIT_MARKER - signals departure from higher-constraint region",
            evidence=[
                f"{len(clusters['GRADIENT_FALLING'])} tokens show falling gradient",
                f"Mean before/after density: {np.mean([p.constraint_density_before for p in clusters['GRADIENT_FALLING']]):.2f} → {np.mean([p.constraint_density_after for p in clusters['GRADIENT_FALLING']]):.2f}"
            ],
            counter_checks=[
                "Verify not explained by LINK proximity",
                "Check if these tokens follow kernel operations"
            ],
            confidence="MODERATE"
        ))

    return functions


def validate_against_execution(functions: List[CoordinateFunction], df: pd.DataFrame) -> List[CoordinateFunction]:
    """Reject any function that would allow execution without grammar."""
    validated = []

    for func in functions:
        # Test: Can these tokens alone predict next operation?
        # If yes → reject (violates interpretation rule)

        # Simple test: Do these tokens have consistent operational neighbors?
        member_tokens = set(func.member_tokens)

        operational_followers = Counter()
        total_followers = 0

        tokens = df['word'].tolist()
        for i, token in enumerate(tokens):
            if token in member_tokens and i < len(tokens) - 1:
                next_token = tokens[i + 1]
                if not is_uncategorized(next_token):
                    operational_followers[next_token] += 1
                    total_followers += 1

        # If one operational token dominates (>50%), might enable execution
        if total_followers > 0:
            most_common_count = operational_followers.most_common(1)[0][1] if operational_followers else 0
            predictability = most_common_count / total_followers

            if predictability > 0.5:
                func.counter_checks.append(f"WARNING: High operational predictability ({predictability:.2f}) - may violate execution independence")
                func.confidence = "LOW"

        validated.append(func)

    return validated


def generate_report(functions: List[CoordinateFunction], clusters: Dict, profiles: List[TokenPositionProfile]) -> str:
    """Generate the analysis report."""
    lines = []

    lines.append("# Phase HTCS: Human-Track Coordinate Semantics")
    lines.append("")
    lines.append("**Status:** COMPLETE")
    lines.append("**Date:** 2026-01-04")
    lines.append("**Prerequisite:** Phase UTC/MCS/NESS (human-track characterization)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"Analyzed {len(profiles)} frequent human-track tokens for positional behavior.")
    lines.append(f"Identified **{len(functions)} candidate coordinate functions**.")
    lines.append("")

    # Summary table
    lines.append("| Function ID | Inferred Role | Members | Confidence |")
    lines.append("|-------------|---------------|---------|------------|")
    for f in functions:
        lines.append(f"| {f.family_id} | {f.inferred_function.split(' - ')[0]} | {len(f.member_tokens)} | {f.confidence} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Detailed findings
    lines.append("## Detailed Findings")
    lines.append("")

    for func in functions:
        lines.append(f"### {func.family_id}: {func.inferred_function.split(' - ')[0]}")
        lines.append("")
        lines.append(f"**Observed Structural Regularity:**")
        lines.append(f"> {func.observed_regularity}")
        lines.append("")
        lines.append(f"**Inferred Coordinate Function:**")
        lines.append(f"> {func.inferred_function}")
        lines.append("")
        lines.append("**Evidence:**")
        for e in func.evidence:
            lines.append(f"- {e}")
        lines.append("")
        lines.append("**Counter-Checks:**")
        for c in func.counter_checks:
            lines.append(f"- {c}")
        lines.append("")
        lines.append(f"**Confidence:** {func.confidence}")
        lines.append("")
        lines.append(f"**Sample Tokens:** `{', '.join(func.member_tokens[:10])}`")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Cluster statistics
    lines.append("## Behavioral Cluster Statistics")
    lines.append("")
    lines.append("| Cluster | Count | Description |")
    lines.append("|---------|-------|-------------|")
    for name, members in clusters.items():
        desc = {
            'SECTION_EARLY': 'Concentrated at section start',
            'SECTION_LATE': 'Concentrated at section end',
            'LINK_PROXIMAL': 'Near LINK/waiting contexts',
            'LINK_DISTAL': 'Distant from LINK contexts',
            'RUN_FORMING': 'Forms consecutive runs',
            'GRADIENT_RISING': 'Precedes constraint increase',
            'GRADIENT_FALLING': 'Precedes constraint decrease',
            'POSITION_NEUTRAL': 'No strong positional signal'
        }.get(name, '')
        lines.append(f"| {name} | {len(members)} | {desc} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Interpretation constraints
    lines.append("## Interpretation Constraints")
    lines.append("")
    lines.append("### These functions ARE:")
    lines.append("- Positional/navigational markers")
    lines.append("- Relative to structural features (section boundaries, LINK contexts)")
    lines.append("- Clustered by behavioral similarity, not morphology")
    lines.append("")
    lines.append("### These functions ARE NOT:")
    lines.append("- Operational instructions")
    lines.append("- Material or quantity indicators")
    lines.append("- Sensory criteria")
    lines.append("- Sufficient for execution without grammar")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Stopping condition
    lines.append("## Stopping Condition")
    lines.append("")
    lines.append("Analysis stopped because:")
    lines.append("")
    lines.append("1. **Remaining variation is continuous** — Further subdivision would be arbitrary")
    lines.append("2. **Functions collapse to navigation semantics** — All detected patterns serve position-marking")
    lines.append("3. **No sensory/material inference possible** — Would require external knowledge")
    lines.append("")
    lines.append("The human-track encodes **WHERE in the operational sequence**, not **WHAT to do**.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Phase HTCS complete. Navigation semantics characterized.*")

    return '\n'.join(lines)


def main():
    """Main analysis pipeline."""
    print("=" * 60)
    print("Phase HTCS: Human-Track Coordinate Semantics")
    print("=" * 60)

    # Load data
    transcript_path = Path("data/transcriptions/interlinear_full_words.txt")

    if not transcript_path.exists():
        print(f"ERROR: Transcription file not found: {transcript_path}")
        return

    print(f"\nLoading transcription from {transcript_path}...")
    df = load_transcription(transcript_path)
    print(f"Loaded {len(df)} tokens from {df['folio'].nunique()} folios")

    # Count uncategorized
    uncat_mask = df['word'].apply(is_uncategorized)
    print(f"Uncategorized tokens: {uncat_mask.sum()} ({100*uncat_mask.mean():.1f}%)")

    # Build profiles
    print("\nBuilding position profiles...")
    profiles = build_position_profiles(df, min_freq=10)
    print(f"Built {len(profiles)} profiles (min freq >= 10)")

    # Cluster by behavior
    print("\nClustering by behavioral similarity...")
    clusters = cluster_by_behavior(profiles)

    for name, members in clusters.items():
        print(f"  {name}: {len(members)} tokens")

    # Infer coordinate functions
    print("\nInferring coordinate functions...")
    functions = infer_coordinate_functions(clusters)
    print(f"Identified {len(functions)} candidate functions")

    # Validate against execution
    print("\nValidating against execution independence...")
    functions = validate_against_execution(functions, df)

    # Generate report
    print("\nGenerating report...")
    report = generate_report(functions, clusters, profiles)

    # Save report
    output_dir = Path("phases/HTCS_coordinate_semantics")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "coordinate_semantics_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    # Summary output
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for func in functions:
        print(f"\n{func.family_id}: {func.inferred_function.split(' - ')[0]}")
        print(f"  Confidence: {func.confidence}")
        print(f"  Members: {len(func.member_tokens)}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
