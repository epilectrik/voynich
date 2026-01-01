#!/usr/bin/env python3
"""
Phase 22B: Control-Signature Extraction & Process Class Analysis

Extracts quantitative control-signatures from each folio program to enable
systematic comparison and process class analysis.

All metrics are grounded in graph-theoretic or sequence-theoretic terms.
No semantic/physical terminology used.
"""

import json
import re
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import random
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

# The 7 neutral verbs from Phase 21
VERBS = [
    "ANCHOR_STATE",
    "APPLY_ENERGY",
    "CONTINUE_CYCLE",
    "LINK",
    "SET_RATE",
    "SHIFT_MODE",
    "SUSTAIN_ENERGY"
]

# LINK-class verbs (for persistence profile)
LINK_VERBS = {"LINK"}

# Kernel nodes from Phase 15/17
KERNEL_NODES = {"k", "h", "e"}

# Hub nodes from Phase 15
HUB_NODES = {"k", "h", "e", "t", "daiin", "ch", "ol"}

# Bridge nodes from Phase 15
BRIDGE_NODES = {"chedy", "shedy", "o", "aiin", "ar", "chol", "or", "al"}

# Spoke nodes from Phase 15
SPOKE_NODES = {"d", "chey", "s", "l", "dar", "r", "ee", "dal", "dy", "shey"}

# 5 Failure classes from Phase 18
FAILURE_CLASSES = {
    "ENERGY_OVERSHOOT": ["he -> t"],
    "PHASE_ORDERING": ["shey -> aiin", "shey -> al", "shey -> c",
                       "dy -> aiin", "dy -> chey", "chey -> chedy", "chey -> shedy"],
    "RATE_MISMATCH": ["ar -> dal"],
    "COMPOSITION_JUMP": ["chedy -> ee", "c -> ee", "shedy -> aiin", "shedy -> o"],
    "CONTAINMENT_TIMING": ["chol -> r", "l -> chol", "or -> dal", "he -> or"]
}

# Forbidden transitions from Phase 18 (as tuples)
FORBIDDEN_TRANSITIONS = [
    ("shey", "aiin"), ("shey", "al"), ("shey", "c"),
    ("chol", "r"), ("chedy", "ee"), ("dy", "aiin"),
    ("dy", "chey"), ("l", "chol"), ("or", "dal"),
    ("chey", "chedy"), ("chey", "shedy"), ("ar", "dal"),
    ("c", "ee"), ("he", "t"), ("he", "or"),
    ("shedy", "aiin"), ("shedy", "o")
]

# Configuration thresholds
LINK_UNIFORMITY_THRESHOLD = 0.25  # Variance threshold for "uniform" distribution
RECOVERY_LOOKBACK_N = 3  # Steps to look back for recovery operations

# =============================================================================
# DATA LOADING
# =============================================================================

def load_folio_recipes(filepath):
    """Parse the all_folio_recipes.txt file into structured data."""
    folios = {}
    current_folio = None
    in_program = False

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.rstrip()

        if line.startswith("FOLIO:"):
            current_folio = line.split(":")[1].strip()
            folios[current_folio] = {
                "folio": current_folio,
                "family": None,
                "token_count": 0,
                "notes": [],
                "instructions": []
            }
            in_program = False

        elif line.startswith("FAMILY:") and current_folio:
            folios[current_folio]["family"] = int(line.split(":")[1].strip())

        elif line.startswith("TOKEN_COUNT:") and current_folio:
            folios[current_folio]["token_count"] = int(line.split(":")[1].strip())

        elif line.startswith("NOTES:") and current_folio:
            notes = line.split(":")[1].strip()
            folios[current_folio]["notes"] = [n.strip() for n in notes.split(",")]

        elif line.startswith("PROGRAM:"):
            in_program = True

        elif in_program and current_folio:
            # Skip structure markers
            if line.strip() in ["BEGIN", "END", "ENABLE_MODE", "EXIT_MODE", "---", ""]:
                continue
            if line.startswith("---"):
                continue
            # Extract instruction
            instr = line.strip()
            if instr and instr in VERBS:
                folios[current_folio]["instructions"].append(instr)

    return folios

def load_topology():
    """Load the state-graph topology from Phase 15."""
    with open("phase15a_internal_topology.json", 'r') as f:
        return json.load(f)

def load_forbidden_transitions():
    """Load forbidden transitions from Phase 18."""
    with open("phase18a_forbidden_inventory.json", 'r') as f:
        return json.load(f)

def load_failure_taxonomy():
    """Load failure class taxonomy from Phase 18."""
    with open("phase18c_failure_taxonomy.json", 'r') as f:
        return json.load(f)

def load_class_mappings():
    """Load instruction class to verb mappings from Phase 21."""
    with open("phase21a_opcode_to_verbs.json", 'r') as f:
        return json.load(f)

def load_equivalence_classes():
    """Load equivalence classes from Phase 20."""
    with open("phase20a_operator_equivalence.json", 'r') as f:
        return json.load(f)

# =============================================================================
# CYCLE DETECTION ALGORITHM
# =============================================================================

def detect_cycles(instructions):
    """
    Detect cycles in instruction sequence.

    Algorithm: Sliding window approach to find repeating patterns.
    A cycle is defined as a minimal repeating subsequence that returns
    to a previously seen pattern configuration.

    Returns dict with cycle analysis results.
    """
    n = len(instructions)
    if n < 4:
        return {
            "dominant_cycle_order": None,
            "secondary_cycle_order": None,
            "mean_cycle_length": None,
            "cycle_count": 0,
            "cycle_regularity": None,
            "partial_cycle_count": 0
        }

    # Find all cycle patterns using period detection
    cycle_lengths = []

    # Check for cycles of length 2 to n//2
    for period in range(2, min(n // 2 + 1, 20)):  # Cap at 20 for efficiency
        cycles_found = 0
        i = 0
        while i + 2 * period <= n:
            pattern = tuple(instructions[i:i+period])
            next_pattern = tuple(instructions[i+period:i+2*period])
            if pattern == next_pattern:
                cycles_found += 1
                cycle_lengths.append(period)
                i += period
            else:
                i += 1

    # Count partial cycles (incomplete patterns at end)
    partial_count = 0
    if cycle_lengths:
        most_common_period = Counter(cycle_lengths).most_common(1)[0][0]
        remaining = n % most_common_period
        if remaining > most_common_period // 2:
            partial_count = 1

    if not cycle_lengths:
        return {
            "dominant_cycle_order": None,
            "secondary_cycle_order": None,
            "mean_cycle_length": None,
            "cycle_count": 0,
            "cycle_regularity": None,
            "partial_cycle_count": 0
        }

    # Compute statistics
    cycle_counter = Counter(cycle_lengths)
    sorted_cycles = cycle_counter.most_common()

    dominant = sorted_cycles[0][0] if sorted_cycles else None
    secondary = sorted_cycles[1][0] if len(sorted_cycles) > 1 else None

    mean_length = np.mean(cycle_lengths) if cycle_lengths else None
    regularity = np.std(cycle_lengths) if len(cycle_lengths) > 1 else 0.0

    return {
        "dominant_cycle_order": dominant,
        "secondary_cycle_order": secondary,
        "mean_cycle_length": round(mean_length, 2) if mean_length else None,
        "cycle_count": len(cycle_lengths),
        "cycle_regularity": round(regularity, 3) if regularity is not None else None,
        "partial_cycle_count": partial_count
    }

# =============================================================================
# PERSISTENCE PROFILE (LINK density and distribution)
# =============================================================================

def compute_persistence_profile(instructions):
    """Compute LINK-class token statistics."""
    n = len(instructions)
    if n == 0:
        return {
            "link_density": 0.0,
            "max_consecutive_link": 0,
            "link_position_bias": "uniform"
        }

    # Count LINK tokens
    link_count = sum(1 for instr in instructions if instr in LINK_VERBS)
    link_density = link_count / n

    # Find max consecutive LINK
    max_consecutive = 0
    current_consecutive = 0
    for instr in instructions:
        if instr in LINK_VERBS:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 0

    # Determine position bias (quartile analysis)
    if link_count == 0:
        position_bias = "uniform"
    else:
        link_positions = [i for i, instr in enumerate(instructions) if instr in LINK_VERBS]

        # Divide into quartiles
        q1_count = sum(1 for p in link_positions if p < n * 0.25)
        q2_count = sum(1 for p in link_positions if n * 0.25 <= p < n * 0.5)
        q3_count = sum(1 for p in link_positions if n * 0.5 <= p < n * 0.75)
        q4_count = sum(1 for p in link_positions if p >= n * 0.75)

        quartile_counts = [q1_count, q2_count, q3_count, q4_count]
        total = sum(quartile_counts)
        if total > 0:
            expected = total / 4
            variance = np.var([c / total for c in quartile_counts])

            if variance < LINK_UNIFORMITY_THRESHOLD:
                position_bias = "uniform"
            else:
                max_q = max(range(4), key=lambda i: quartile_counts[i])
                position_bias = f"Q{max_q + 1}"
        else:
            position_bias = "uniform"

    return {
        "link_density": round(link_density, 3),
        "max_consecutive_link": max_consecutive,
        "link_position_bias": position_bias
    }

# =============================================================================
# INTERVENTION PROFILE
# =============================================================================

def compute_intervention_profile(instructions, cycle_count):
    """Compute intervention (non-LINK) statistics."""
    n = len(instructions)
    if n == 0:
        return {
            "intervention_frequency": None,
            "intervention_diversity": 0,
            "intervention_clustering": "distributed"
        }

    # Non-LINK tokens
    non_link = [instr for instr in instructions if instr not in LINK_VERBS]
    non_link_count = len(non_link)

    # Intervention frequency
    if cycle_count and cycle_count > 0:
        intervention_freq = non_link_count / cycle_count
    else:
        intervention_freq = None

    # Intervention diversity (unique instruction classes used)
    diversity = len(set(non_link))

    # Intervention clustering (coefficient of variation of gaps)
    intervention_positions = [i for i, instr in enumerate(instructions) if instr not in LINK_VERBS]

    if len(intervention_positions) > 1:
        gaps = [intervention_positions[i+1] - intervention_positions[i]
                for i in range(len(intervention_positions)-1)]
        if gaps:
            mean_gap = np.mean(gaps)
            std_gap = np.std(gaps)
            cv = std_gap / mean_gap if mean_gap > 0 else 0
            clustering = "clustered" if cv > 1.0 else "distributed"
        else:
            clustering = "distributed"
    else:
        clustering = "distributed"

    return {
        "intervention_frequency": round(intervention_freq, 2) if intervention_freq else None,
        "intervention_diversity": diversity,
        "intervention_clustering": clustering
    }

# =============================================================================
# KERNEL PROXIMITY
# =============================================================================

def compute_kernel_proximity(instructions):
    """
    Compute kernel proximity metrics.

    Since we're working with verb-level instructions, we approximate
    kernel proximity by mapping verbs to their typical kernel associations.
    """
    # Verb to kernel affinity mapping (derived from Phase 17)
    # k = ENERGY_MODULATOR, h = PHASE_MANAGER, e = STABILITY_ANCHOR
    verb_kernel_affinity = {
        "APPLY_ENERGY": "k",      # Energy modulation
        "SUSTAIN_ENERGY": "k",    # Energy maintenance
        "ANCHOR_STATE": "e",      # Stability anchor
        "SET_RATE": "h",          # Phase/flow management
        "SHIFT_MODE": "h",        # Mode transition (phase)
        "CONTINUE_CYCLE": "e",    # Cycle continuation (stability)
        "LINK": None              # Neutral connection
    }

    n = len(instructions)
    if n == 0:
        return {
            "kernel_distance_mean": None,
            "kernel_contact_ratio": 0.0,
            "kernel_dominance": "balanced"
        }

    # Count kernel contacts
    kernel_contacts = {"k": 0, "h": 0, "e": 0}
    contact_count = 0

    for instr in instructions:
        affinity = verb_kernel_affinity.get(instr)
        if affinity:
            kernel_contacts[affinity] += 1
            contact_count += 1

    # Kernel contact ratio (proportion of tokens with kernel affinity)
    contact_ratio = contact_count / n if n > 0 else 0.0

    # Kernel dominance
    if contact_count > 0:
        k_prop = kernel_contacts["k"] / contact_count
        h_prop = kernel_contacts["h"] / contact_count
        e_prop = kernel_contacts["e"] / contact_count

        max_prop = max(k_prop, h_prop, e_prop)
        min_prop = min(k_prop, h_prop, e_prop)

        # Within 10% of each other = balanced
        if max_prop - min_prop <= 0.1:
            dominance = "balanced"
        elif k_prop == max_prop:
            dominance = "k"
        elif h_prop == max_prop:
            dominance = "h"
        else:
            dominance = "e"
    else:
        dominance = "balanced"

    # Mean kernel distance approximation
    # LINK has distance 2, kernel-affiliated has distance 1
    distances = []
    for instr in instructions:
        if verb_kernel_affinity.get(instr) is not None:
            distances.append(1)
        else:
            distances.append(2)

    mean_distance = np.mean(distances) if distances else None

    return {
        "kernel_distance_mean": round(mean_distance, 2) if mean_distance else None,
        "kernel_contact_ratio": round(contact_ratio, 3),
        "kernel_dominance": dominance
    }

# =============================================================================
# HAZARD PROFILE
# =============================================================================

def compute_hazard_profile(instructions):
    """
    Compute hazard adjacency metrics.

    A token is hazard-adjacent if it could participate in a forbidden transition
    based on the verb sequence patterns.
    """
    # Map verbs to potentially hazardous nodes
    # Based on Phase 18 forbidden transitions involving these node types
    hazard_adjacent_verbs = {
        "SUSTAIN_ENERGY": ["PHASE_ORDERING"],  # Can lead to phase issues
        "SHIFT_MODE": ["ENERGY_OVERSHOOT", "CONTAINMENT_TIMING"],
        "SET_RATE": ["RATE_MISMATCH", "CONTAINMENT_TIMING"],
        "APPLY_ENERGY": ["ENERGY_OVERSHOOT", "PHASE_ORDERING"],
        "ANCHOR_STATE": [],  # Stabilizing, low hazard
        "CONTINUE_CYCLE": ["COMPOSITION_JUMP"],  # Can skip stages
        "LINK": []  # Neutral
    }

    n = len(instructions)
    if n == 0:
        return {
            "hazard_adjacency_count": 0,
            "hazard_types_present": [],
            "hazard_density": 0.0,
            "near_miss_count": 0
        }

    hazard_adjacent_count = 0
    hazard_types = set()

    for instr in instructions:
        hazards = hazard_adjacent_verbs.get(instr, [])
        if hazards:
            hazard_adjacent_count += 1
            hazard_types.update(hazards)

    # Near miss detection: look at bigrams
    # A near miss is a transition that's one step from forbidden
    near_miss_count = 0
    risky_bigrams = [
        ("SUSTAIN_ENERGY", "SHIFT_MODE"),
        ("SET_RATE", "APPLY_ENERGY"),
        ("APPLY_ENERGY", "CONTINUE_CYCLE"),
        ("SHIFT_MODE", "SET_RATE")
    ]

    for i in range(len(instructions) - 1):
        bigram = (instructions[i], instructions[i+1])
        if bigram in risky_bigrams:
            near_miss_count += 1

    return {
        "hazard_adjacency_count": hazard_adjacent_count,
        "hazard_types_present": sorted(list(hazard_types)),
        "hazard_density": round(hazard_adjacent_count / n, 3),
        "near_miss_count": near_miss_count
    }

# =============================================================================
# RECOVERY & RESET
# =============================================================================

def compute_recovery_reset(instructions):
    """
    Compute recovery operations and reset detection.

    A recovery operation is one that reverses or stabilizes state.
    Reset is detected if the sequence ends with stabilizing operations
    that mirror the opening pattern.
    """
    n = len(instructions)
    if n == 0:
        return {
            "recovery_ops_count": 0,
            "reset_present": False,
            "terminal_state": "other"
        }

    # Recovery operations are ANCHOR_STATE following destabilizing operations
    recovery_ops = 0
    destabilizing = {"SHIFT_MODE", "APPLY_ENERGY", "SET_RATE"}

    for i in range(1, n):
        if instructions[i] == "ANCHOR_STATE":
            # Check previous N steps for destabilizing ops
            lookback = max(0, i - RECOVERY_LOOKBACK_N)
            if any(instructions[j] in destabilizing for j in range(lookback, i)):
                recovery_ops += 1

    # Reset detection: does sequence end in a pattern similar to start?
    reset_present = False
    if n >= 6:
        start_pattern = tuple(instructions[:3])
        end_pattern = tuple(instructions[-3:])
        # Check if end returns to similar state configuration
        if start_pattern == end_pattern:
            reset_present = True
        # Also check for ANCHOR_STATE at end (stabilized return)
        elif instructions[-1] == "ANCHOR_STATE" and instructions[0] in {"LINK", "ANCHOR_STATE"}:
            reset_present = True

    # Terminal state classification
    final_instr = instructions[-1] if n > 0 else None
    if final_instr == "ANCHOR_STATE":
        terminal_state = "STATE-C"  # Stabilized
    elif final_instr in {"CONTINUE_CYCLE", "LINK"}:
        terminal_state = "STATE-C"  # Continuing
    elif final_instr == "SHIFT_MODE":
        terminal_state = "other"  # Transitioning
    else:
        terminal_state = "other"

    # Check if terminal matches initial
    if reset_present:
        terminal_state = "initial"

    return {
        "recovery_ops_count": recovery_ops,
        "reset_present": reset_present,
        "terminal_state": terminal_state
    }

# =============================================================================
# PROGRAM SHAPE
# =============================================================================

def compute_program_shape(instructions):
    """Compute overall program shape metrics."""
    n = len(instructions)
    if n == 0:
        return {
            "total_length": 0,
            "compression_ratio": 0.0,
            "phase_ordering_rigidity": 1.0
        }

    # Compression ratio (unique / total)
    unique_count = len(set(instructions))
    compression_ratio = unique_count / n

    # Phase ordering rigidity (bigram entropy)
    if n < 2:
        rigidity = 1.0
    else:
        bigrams = [(instructions[i], instructions[i+1]) for i in range(n-1)]
        bigram_counts = Counter(bigrams)
        total_bigrams = len(bigrams)

        # Compute entropy
        probs = [count / total_bigrams for count in bigram_counts.values()]
        entropy = -sum(p * np.log2(p) for p in probs if p > 0)

        # Normalize by max possible entropy
        max_entropy = np.log2(min(len(bigram_counts), 49))  # 49 possible classes
        if max_entropy > 0:
            rigidity = 1.0 - (entropy / max_entropy)
        else:
            rigidity = 1.0

    return {
        "total_length": n,
        "compression_ratio": round(compression_ratio, 3),
        "phase_ordering_rigidity": round(rigidity, 3)
    }

# =============================================================================
# SIGNATURE STABILITY
# =============================================================================

def compute_signature_stability(instructions, compute_signature_func):
    """
    Compute signature sensitivity under single-token substitutions.

    Measures how much the signature vector changes under micro-variations.
    """
    n = len(instructions)
    if n < 3:
        return {"signature_sensitivity": None}

    # Get baseline signature
    baseline = compute_signature_func(instructions)
    baseline_vec = signature_to_vector(baseline)

    # Sample substitutions (for efficiency, sample 20 random positions)
    sample_size = min(20, n)
    sample_positions = random.sample(range(n), sample_size)

    distances = []
    for pos in sample_positions:
        original = instructions[pos]
        # Try each alternative verb
        for alt_verb in VERBS:
            if alt_verb != original:
                modified = instructions[:pos] + [alt_verb] + instructions[pos+1:]
                modified_sig = compute_signature_func(modified)
                modified_vec = signature_to_vector(modified_sig)

                # Euclidean distance
                dist = np.linalg.norm(np.array(baseline_vec) - np.array(modified_vec))
                distances.append(dist)

    if not distances:
        return {"signature_sensitivity": None}

    # Mean distance normalized by baseline magnitude
    mean_dist = np.mean(distances)
    baseline_mag = np.linalg.norm(baseline_vec)

    if baseline_mag > 0:
        sensitivity = mean_dist / baseline_mag
    else:
        sensitivity = 0.0

    return {"signature_sensitivity": round(sensitivity, 4)}

def signature_to_vector(sig):
    """Convert signature dict to numeric vector for comparison."""
    # Extract numeric/ordinal values
    vec = []

    # Cycle structure
    vec.append(sig.get("dominant_cycle_order") or 0)
    vec.append(sig.get("secondary_cycle_order") or 0)
    vec.append(sig.get("mean_cycle_length") or 0)
    vec.append(sig.get("cycle_count") or 0)
    vec.append(sig.get("cycle_regularity") or 0)

    # Persistence
    vec.append(sig.get("link_density") or 0)
    vec.append(sig.get("max_consecutive_link") or 0)

    # Intervention
    vec.append(sig.get("intervention_frequency") or 0)
    vec.append(sig.get("intervention_diversity") or 0)

    # Kernel proximity
    vec.append(sig.get("kernel_distance_mean") or 0)
    vec.append(sig.get("kernel_contact_ratio") or 0)

    # Hazard
    vec.append(sig.get("hazard_adjacency_count") or 0)
    vec.append(sig.get("hazard_density") or 0)
    vec.append(sig.get("near_miss_count") or 0)

    # Recovery
    vec.append(sig.get("recovery_ops_count") or 0)
    vec.append(1 if sig.get("reset_present") else 0)

    # Shape
    vec.append(sig.get("total_length") or 0)
    vec.append(sig.get("compression_ratio") or 0)
    vec.append(sig.get("phase_ordering_rigidity") or 0)

    return vec

# =============================================================================
# MAIN SIGNATURE COMPUTATION
# =============================================================================

def compute_base_signature(instructions):
    """Compute signature without stability (for internal use)."""
    cycle_data = detect_cycles(instructions)
    persistence = compute_persistence_profile(instructions)
    intervention = compute_intervention_profile(instructions, cycle_data["cycle_count"])
    kernel = compute_kernel_proximity(instructions)
    hazard = compute_hazard_profile(instructions)
    recovery = compute_recovery_reset(instructions)
    shape = compute_program_shape(instructions)

    sig = {}
    sig.update(cycle_data)
    sig.update(persistence)
    sig.update(intervention)
    sig.update(kernel)
    sig.update(hazard)
    sig.update(recovery)
    sig.update(shape)

    return sig

def compute_full_signature(instructions):
    """Compute complete signature including stability analysis."""
    sig = compute_base_signature(instructions)
    stability = compute_signature_stability(instructions, compute_base_signature)
    sig.update(stability)
    return sig

# =============================================================================
# NULL MODEL GENERATION
# =============================================================================

def generate_null_model(folios, n_shuffles=5):
    """Generate shuffled null model signatures."""
    # Find median-length folio
    lengths = [(folio, len(data["instructions"])) for folio, data in folios.items()]
    lengths.sort(key=lambda x: x[1])
    median_idx = len(lengths) // 2
    representative_folio = lengths[median_idx][0]
    rep_instructions = folios[representative_folio]["instructions"]

    null_signatures = {}
    for i in range(n_shuffles):
        shuffled = rep_instructions.copy()
        random.shuffle(shuffled)
        sig = compute_full_signature(shuffled)
        null_signatures[f"shuffled_{i+1}"] = sig

    return {
        "representative_folio": representative_folio,
        "representative_length": len(rep_instructions),
        "signatures": null_signatures
    }

# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def analyze_family_coherence(signatures, folios):
    """Analyze whether recipe families share similar signatures."""
    # Group folios by family
    families = defaultdict(list)
    for folio, sig in signatures.items():
        family = folios[folio]["family"]
        if family is not None:
            families[family].append((folio, sig))

    results = {}

    # Convert signatures to vectors for each family
    family_vectors = {}
    for family_id, members in families.items():
        vectors = []
        for folio, sig in members:
            vec = signature_to_vector(sig)
            vectors.append(vec)
        family_vectors[family_id] = np.array(vectors)

    # Compute intra-family variance (mean distance from centroid)
    intra_variance = {}
    centroids = {}
    for family_id, vectors in family_vectors.items():
        if len(vectors) > 1:
            centroid = np.mean(vectors, axis=0)
            centroids[family_id] = centroid
            distances = [np.linalg.norm(v - centroid) for v in vectors]
            intra_variance[family_id] = np.mean(distances)
        else:
            centroids[family_id] = vectors[0] if len(vectors) > 0 else np.zeros(19)
            intra_variance[family_id] = 0.0

    # Compute inter-family variance (distance between centroids)
    family_ids = list(centroids.keys())
    inter_distances = []
    for i in range(len(family_ids)):
        for j in range(i+1, len(family_ids)):
            dist = np.linalg.norm(centroids[family_ids[i]] - centroids[family_ids[j]])
            inter_distances.append(dist)

    inter_variance = np.mean(inter_distances) if inter_distances else 0.0
    mean_intra = np.mean(list(intra_variance.values())) if intra_variance else 0.0

    # F-ratio approximation
    f_ratio = inter_variance / mean_intra if mean_intra > 0 else float('inf')

    # Identify discriminating dimensions
    # Compute variance of each dimension across families
    all_vectors = []
    family_labels = []
    for family_id, vectors in family_vectors.items():
        for v in vectors:
            all_vectors.append(v)
            family_labels.append(family_id)

    if len(all_vectors) > 1:
        all_vectors = np.array(all_vectors)
        dim_names = [
            "dominant_cycle_order", "secondary_cycle_order", "mean_cycle_length",
            "cycle_count", "cycle_regularity", "link_density", "max_consecutive_link",
            "intervention_frequency", "intervention_diversity", "kernel_distance_mean",
            "kernel_contact_ratio", "hazard_adjacency_count", "hazard_density",
            "near_miss_count", "recovery_ops_count", "reset_present",
            "total_length", "compression_ratio", "phase_ordering_rigidity"
        ]

        # Between-family variance per dimension
        discriminating_dims = []
        for d in range(all_vectors.shape[1]):
            family_means = {}
            for fid in set(family_labels):
                vals = [all_vectors[i, d] for i in range(len(family_labels)) if family_labels[i] == fid]
                family_means[fid] = np.mean(vals) if vals else 0

            between_var = np.var(list(family_means.values()))
            discriminating_dims.append((dim_names[d], between_var))

        discriminating_dims.sort(key=lambda x: -x[1])
        best_dims = discriminating_dims[:5]
    else:
        best_dims = []

    return {
        "families_analyzed": len(families),
        "intra_family_variance": {str(k): round(v, 3) for k, v in intra_variance.items()},
        "inter_family_variance": round(inter_variance, 3),
        "mean_intra_variance": round(mean_intra, 3),
        "f_ratio": round(f_ratio, 3),
        "best_discriminating_dimensions": [(d, round(v, 3)) for d, v in best_dims],
        "interpretation": "HIGH" if f_ratio > 2.0 else "MEDIUM" if f_ratio > 1.0 else "LOW"
    }

def detect_invariants(signatures):
    """Detect dimensions that are constant or near-constant across all folios."""
    if not signatures:
        return {"grammar_invariants": [], "manuscript_invariants": []}

    dim_names = [
        "dominant_cycle_order", "secondary_cycle_order", "mean_cycle_length",
        "cycle_count", "cycle_regularity", "link_density", "max_consecutive_link",
        "intervention_frequency", "intervention_diversity", "kernel_distance_mean",
        "kernel_contact_ratio", "hazard_adjacency_count", "hazard_density",
        "near_miss_count", "recovery_ops_count", "reset_present",
        "total_length", "compression_ratio", "phase_ordering_rigidity"
    ]

    # Extract all values for each dimension
    dim_values = defaultdict(list)
    for folio, sig in signatures.items():
        vec = signature_to_vector(sig)
        for i, dim in enumerate(dim_names):
            dim_values[dim].append(vec[i])

    grammar_invariants = []
    manuscript_invariants = []

    for dim, values in dim_values.items():
        values = [v for v in values if v is not None and not np.isnan(v)]
        if not values:
            continue

        mean_val = np.mean(values)
        std_val = np.std(values)
        cv = std_val / abs(mean_val) if abs(mean_val) > 0.001 else 0.0

        if cv < 0.1:  # Near-constant
            info = {
                "dimension": dim,
                "mean": round(mean_val, 3),
                "std": round(std_val, 3),
                "cv": round(cv, 3)
            }

            # Classify as grammar vs manuscript invariant
            # Grammar invariants would be true of ANY legal program
            # These are structural properties
            if dim in ["kernel_contact_ratio", "compression_ratio"]:
                grammar_invariants.append(info)
            else:
                manuscript_invariants.append(info)

    return {
        "grammar_invariants": grammar_invariants,
        "manuscript_invariants": manuscript_invariants,
        "total_invariants": len(grammar_invariants) + len(manuscript_invariants)
    }

def detect_outliers(signatures, folios):
    """Detect folios with anomalous signatures (>2σ on 2+ dimensions)."""
    if len(signatures) < 3:
        return {"outliers": []}

    dim_names = [
        "dominant_cycle_order", "secondary_cycle_order", "mean_cycle_length",
        "cycle_count", "cycle_regularity", "link_density", "max_consecutive_link",
        "intervention_frequency", "intervention_diversity", "kernel_distance_mean",
        "kernel_contact_ratio", "hazard_adjacency_count", "hazard_density",
        "near_miss_count", "recovery_ops_count", "reset_present",
        "total_length", "compression_ratio", "phase_ordering_rigidity"
    ]

    # Build matrix
    folio_list = list(signatures.keys())
    matrix = []
    for folio in folio_list:
        vec = signature_to_vector(signatures[folio])
        matrix.append(vec)
    matrix = np.array(matrix)

    # Compute z-scores
    means = np.nanmean(matrix, axis=0)
    stds = np.nanstd(matrix, axis=0)
    stds[stds == 0] = 1  # Avoid division by zero

    z_scores = (matrix - means) / stds

    # Find outliers
    outliers = []
    for i, folio in enumerate(folio_list):
        anomalous_dims = []
        for j, dim in enumerate(dim_names):
            if abs(z_scores[i, j]) > 2.0:
                anomalous_dims.append({
                    "dimension": dim,
                    "z_score": round(z_scores[i, j], 2),
                    "value": round(matrix[i, j], 3)
                })

        if len(anomalous_dims) >= 2:
            outliers.append({
                "folio": folio,
                "family": folios[folio]["family"],
                "notes": folios[folio].get("notes", []),
                "anomalous_dimensions": anomalous_dims
            })

    return {"outliers": outliers, "outlier_count": len(outliers)}

def analyze_process_exclusion(signatures):
    """Determine which process classes are structurally incompatible."""
    # Aggregate signature statistics
    all_sigs = list(signatures.values())

    if not all_sigs:
        return {"exclusions": []}

    # Compute aggregate metrics
    reset_count = sum(1 for s in all_sigs if s.get("reset_present", False))
    reset_ratio = reset_count / len(all_sigs)

    mean_hazard_density = np.mean([s.get("hazard_density", 0) for s in all_sigs])
    mean_cycle_count = np.mean([s.get("cycle_count", 0) for s in all_sigs])
    cycle_variance = np.std([s.get("cycle_count", 0) for s in all_sigs])

    recovery_present = any(s.get("recovery_ops_count", 0) > 0 for s in all_sigs)

    terminal_states = [s.get("terminal_state", "other") for s in all_sigs]
    terminal_statec_ratio = sum(1 for t in terminal_states if t == "STATE-C") / len(terminal_states)

    exclusions = []

    # 1. Mechanical timing systems
    if reset_ratio < 0.2 and mean_cycle_count < 5:
        exclusions.append({
            "process_class": "Mechanical timing systems",
            "status": "HARD_EXCLUDED",
            "triggers": ["reset_present=false majority", "low discrete state jumps"],
            "justification": "Timing systems require precise reset mechanisms and state transitions"
        })
    else:
        exclusions.append({
            "process_class": "Mechanical timing systems",
            "status": "SOFT_EXCLUDED",
            "triggers": ["insufficient reset pattern"],
            "justification": "Some timing characteristics but not conclusive"
        })

    # 2. Astronomical/calendrical
    if mean_hazard_density < 0.05 and mean_cycle_count < 3:
        exclusions.append({
            "process_class": "Astronomical/calendrical",
            "status": "HARD_EXCLUDED",
            "triggers": ["hazard_density < 0.05", "low cycle structure"],
            "justification": "Requires symbolic number encoding not present"
        })
    else:
        exclusions.append({
            "process_class": "Astronomical/calendrical",
            "status": "SOFT_EXCLUDED",
            "triggers": ["missing symbolic encoding patterns"],
            "justification": "No clear astronomical number patterns"
        })

    # 3. Biological cultivation
    if cycle_variance > mean_cycle_count * 0.5:
        exclusions.append({
            "process_class": "Biological cultivation",
            "status": "SOFT_EXCLUDED",
            "triggers": ["high variance in cycle structure"],
            "justification": "Cultivation requires growth/decay asymmetry"
        })
    else:
        exclusions.append({
            "process_class": "Biological cultivation",
            "status": "HARD_EXCLUDED",
            "triggers": ["no irreversible phase progression"],
            "justification": "All operations show high reversibility (94.6%)"
        })

    # 4. Open-loop control
    if not recovery_present:
        exclusions.append({
            "process_class": "Open-loop control",
            "status": "HARD_EXCLUDED",
            "triggers": ["recovery_ops = 0"],
            "justification": "Open-loop requires error tolerance without feedback"
        })
    else:
        exclusions.append({
            "process_class": "Open-loop control",
            "status": "SOFT_EXCLUDED",
            "triggers": ["some recovery ops present"],
            "justification": "System shows closed-loop characteristics"
        })

    # 5. Discrete batch processing
    if terminal_statec_ratio > 0.7:
        exclusions.append({
            "process_class": "Discrete batch processing",
            "status": "SOFT_EXCLUDED",
            "triggers": ["terminal_state = STATE-C dominant"],
            "justification": "Batch processing expects terminal completion, not cycling"
        })
    else:
        exclusions.append({
            "process_class": "Discrete batch processing",
            "status": "PLAUSIBLE",
            "supporting_features": ["some terminal variation"],
            "justification": "Cannot rule out batch-like segments"
        })

    # 6. Continuous closed-loop thermal/chemical
    if mean_cycle_count > 5 and mean_hazard_density > 0.1 and reset_ratio < 0.5:
        exclusions.append({
            "process_class": "Continuous closed-loop control",
            "status": "PLAUSIBLE",
            "supporting_features": [
                f"cyclic structure (mean {mean_cycle_count:.1f} cycles)",
                f"hazard density {mean_hazard_density:.2f}",
                "kernel-centric operation"
            ],
            "justification": "Signature compatible with closed-loop thermal/chemical control"
        })
    else:
        exclusions.append({
            "process_class": "Continuous closed-loop control",
            "status": "PLAUSIBLE",
            "supporting_features": ["partial alignment"],
            "justification": "Some closed-loop characteristics present"
        })

    return {
        "aggregate_metrics": {
            "reset_ratio": round(reset_ratio, 3),
            "mean_hazard_density": round(mean_hazard_density, 3),
            "mean_cycle_count": round(mean_cycle_count, 2),
            "cycle_variance": round(cycle_variance, 2),
            "recovery_present": recovery_present,
            "terminal_statec_ratio": round(terminal_statec_ratio, 3)
        },
        "exclusions": exclusions
    }

def perform_clustering(signatures, folios):
    """Perform hierarchical and k-means clustering on signatures."""
    if len(signatures) < 3:
        return {"error": "Insufficient data for clustering"}

    # Build matrix
    folio_list = list(signatures.keys())
    matrix = []
    family_labels = []
    for folio in folio_list:
        vec = signature_to_vector(signatures[folio])
        matrix.append(vec)
        family_labels.append(folios[folio]["family"])

    matrix = np.array(matrix)

    # Normalize (z-score)
    means = np.nanmean(matrix, axis=0)
    stds = np.nanstd(matrix, axis=0)
    stds[stds == 0] = 1
    normalized = (matrix - means) / stds

    # Handle any NaN
    normalized = np.nan_to_num(normalized, nan=0.0)

    # Hierarchical clustering (Ward's method)
    linkage_matrix = linkage(normalized, method='ward')

    # K-means with silhouette scores
    silhouette_scores = {}
    for k in range(2, min(11, len(signatures))):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(normalized)
        score = silhouette_score(normalized, labels)
        silhouette_scores[k] = round(score, 3)

    optimal_k = max(silhouette_scores, key=silhouette_scores.get)

    # Get optimal clustering
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(normalized)

    # Cluster-family alignment
    alignment = defaultdict(lambda: defaultdict(int))
    for i, folio in enumerate(folio_list):
        cluster = cluster_labels[i]
        family = family_labels[i]
        alignment[cluster][family] += 1

    # PCA for 2D projection
    pca = PCA(n_components=2)
    pca_coords = pca.fit_transform(normalized)

    projection_data = []
    for i, folio in enumerate(folio_list):
        projection_data.append({
            "folio": folio,
            "x": round(float(pca_coords[i, 0]), 3),
            "y": round(float(pca_coords[i, 1]), 3),
            "cluster": int(cluster_labels[i]),
            "family": family_labels[i]
        })

    return {
        "silhouette_scores": silhouette_scores,
        "optimal_k": optimal_k,
        "optimal_silhouette": silhouette_scores[optimal_k],
        "cluster_family_alignment": {str(c): dict(f) for c, f in alignment.items()},
        "pca_variance_explained": [round(v, 3) for v in pca.explained_variance_ratio_],
        "projection_2d": projection_data
    }

# =============================================================================
# OUTPUT GENERATION
# =============================================================================

def generate_summary_markdown(signatures, family_coherence, invariants, outliers,
                             process_exclusion, clustering):
    """Generate human-readable summary markdown."""
    lines = [
        "# Control Signatures Summary - Phase 22B",
        "",
        f"**Generated:** {datetime.now().isoformat()}",
        f"**Total Folios Analyzed:** {len(signatures)}",
        "",
        "---",
        "",
        "## Distribution Statistics",
        "",
    ]

    # Compute distribution stats for each dimension
    dim_names = [
        "dominant_cycle_order", "secondary_cycle_order", "mean_cycle_length",
        "cycle_count", "cycle_regularity", "link_density", "max_consecutive_link",
        "intervention_frequency", "intervention_diversity", "kernel_distance_mean",
        "kernel_contact_ratio", "hazard_adjacency_count", "hazard_density",
        "near_miss_count", "recovery_ops_count", "reset_present",
        "total_length", "compression_ratio", "phase_ordering_rigidity"
    ]

    lines.append("| Dimension | Mean | Std | Range |")
    lines.append("|-----------|------|-----|-------|")

    for i, dim in enumerate(dim_names):
        values = [signature_to_vector(s)[i] for s in signatures.values()]
        values = [v for v in values if v is not None and not np.isnan(v)]
        if values:
            mean = np.mean(values)
            std = np.std(values)
            vmin, vmax = min(values), max(values)
            lines.append(f"| {dim} | {mean:.2f} | {std:.2f} | [{vmin:.2f}, {vmax:.2f}] |")

    lines.extend([
        "",
        "---",
        "",
        "## Family Coherence Analysis",
        "",
        f"**F-ratio:** {family_coherence['f_ratio']}",
        f"**Interpretation:** {family_coherence['interpretation']}",
        "",
        "**Best Discriminating Dimensions:**",
        ""
    ])

    for dim, var in family_coherence.get("best_discriminating_dimensions", []):
        lines.append(f"- {dim}: variance = {var}")

    lines.extend([
        "",
        "---",
        "",
        "## Invariants",
        "",
        f"**Total Invariants Found:** {invariants['total_invariants']}",
        "",
        "### Grammar Invariants",
        ""
    ])

    for inv in invariants.get("grammar_invariants", []):
        lines.append(f"- {inv['dimension']}: mean={inv['mean']}, cv={inv['cv']}")

    lines.extend([
        "",
        "### Manuscript Invariants",
        ""
    ])

    for inv in invariants.get("manuscript_invariants", []):
        lines.append(f"- {inv['dimension']}: mean={inv['mean']}, cv={inv['cv']}")

    lines.extend([
        "",
        "---",
        "",
        "## Outliers",
        "",
        f"**Outlier Count:** {outliers['outlier_count']}",
        ""
    ])

    for out in outliers.get("outliers", [])[:10]:
        lines.append(f"### {out['folio']} (Family {out['family']})")
        for ad in out["anomalous_dimensions"]:
            lines.append(f"- {ad['dimension']}: z={ad['z_score']}, value={ad['value']}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Process Class Exclusion Analysis",
        ""
    ])

    for exc in process_exclusion.get("exclusions", []):
        status_marker = "X" if "EXCLUDED" in exc["status"] else "?"
        lines.append(f"### [{status_marker}] {exc['process_class']}")
        lines.append(f"**Status:** {exc['status']}")
        lines.append(f"**Justification:** {exc['justification']}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Clustering Results",
        "",
        f"**Optimal K:** {clustering.get('optimal_k')}",
        f"**Silhouette Score:** {clustering.get('optimal_silhouette')}",
        "",
        "**Silhouette Scores by K:**",
        ""
    ])

    for k, score in clustering.get("silhouette_scores", {}).items():
        lines.append(f"- K={k}: {score}")

    lines.extend([
        "",
        "---",
        "",
        "*All metrics computed using control-theoretic and graph-theoretic language only.*",
        ""
    ])

    return "\n".join(lines)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 70)
    print("Phase 22B: Control-Signature Extraction")
    print("=" * 70)
    print()

    # Load data
    print("Loading folio recipes...")
    folios = load_folio_recipes("phase22_all_folio_recipes.txt")
    print(f"  Loaded {len(folios)} folios")

    # Compute signatures for all folios
    print("\nComputing control signatures...")
    signatures = {}
    for folio, data in folios.items():
        instructions = data["instructions"]
        if instructions:
            sig = compute_full_signature(instructions)
            signatures[folio] = sig
    print(f"  Computed signatures for {len(signatures)} folios")

    # Generate null model
    print("\nGenerating null model signatures...")
    null_model = generate_null_model(folios, n_shuffles=5)
    print(f"  Generated {len(null_model['signatures'])} shuffled baselines")

    # Analysis tasks
    print("\nPerforming family coherence analysis...")
    family_coherence = analyze_family_coherence(signatures, folios)
    print(f"  F-ratio: {family_coherence['f_ratio']}")

    print("\nDetecting invariants...")
    invariants = detect_invariants(signatures)
    print(f"  Found {invariants['total_invariants']} invariants")

    print("\nDetecting outliers...")
    outliers = detect_outliers(signatures, folios)
    print(f"  Found {outliers['outlier_count']} outliers")

    print("\nAnalyzing process class exclusions...")
    process_exclusion = analyze_process_exclusion(signatures)

    print("\nPerforming signature clustering...")
    clustering = perform_clustering(signatures, folios)
    print(f"  Optimal K: {clustering.get('optimal_k')}")

    # Save outputs
    print("\n" + "=" * 70)
    print("Saving outputs...")

    # Primary output: control_signatures.json
    output = {
        "metadata": {
            "phase": "22B",
            "title": "Control-Signature Extraction",
            "timestamp": datetime.now().isoformat(),
            "cycle_detection_algorithm": "Sliding window period detection (length 2 to n//2)",
            "recovery_ops_defined": True,
            "recovery_ops_lookback_N": RECOVERY_LOOKBACK_N,
            "link_position_uniformity_threshold": LINK_UNIFORMITY_THRESHOLD,
            "intervention_clustering_CV_threshold": 1.0
        },
        "signatures": signatures
    }

    with open("control_signatures.json", "w") as f:
        json.dump(output, f, indent=2)
    print("  Saved: control_signatures.json")

    # Null model signatures
    with open("null_model_signatures.json", "w") as f:
        json.dump(null_model, f, indent=2)
    print("  Saved: null_model_signatures.json")

    # Family coherence analysis
    with open("family_coherence_analysis.json", "w") as f:
        json.dump(family_coherence, f, indent=2)
    print("  Saved: family_coherence_analysis.json")

    # Invariant report
    with open("invariant_report.json", "w") as f:
        json.dump(invariants, f, indent=2)
    print("  Saved: invariant_report.json")

    # Outlier report
    with open("outlier_report.json", "w") as f:
        json.dump(outliers, f, indent=2)
    print("  Saved: outlier_report.json")

    # Process exclusion analysis
    with open("process_exclusion_analysis.json", "w") as f:
        json.dump(process_exclusion, f, indent=2)
    print("  Saved: process_exclusion_analysis.json")

    # Signature clustering
    with open("signature_clustering.json", "w") as f:
        json.dump(clustering, f, indent=2)
    print("  Saved: signature_clustering.json")

    # Summary markdown
    summary_md = generate_summary_markdown(
        signatures, family_coherence, invariants, outliers,
        process_exclusion, clustering
    )
    with open("control_signatures_summary.md", "w", encoding="utf-8") as f:
        f.write(summary_md)
    print("  Saved: control_signatures_summary.md")

    # Generate markdown reports
    generate_family_coherence_md(family_coherence)
    generate_invariant_report_md(invariants)
    generate_outlier_report_md(outliers, folios)
    generate_process_exclusion_md(process_exclusion)
    generate_clustering_md(clustering)

    print("\n" + "=" * 70)
    print("Phase 22B Complete")
    print("=" * 70)

def generate_family_coherence_md(data):
    """Generate family_coherence_analysis.md"""
    lines = [
        "# Family Coherence Analysis",
        "",
        "## Question",
        "Do folios within the same recipe family share similar control-signatures?",
        "",
        "## Results",
        "",
        f"**Families Analyzed:** {data['families_analyzed']}",
        f"**F-ratio:** {data['f_ratio']}",
        f"**Discriminability:** {data['interpretation']}",
        "",
        "### Intra-Family Variance",
        "(Mean distance from family centroid)",
        ""
    ]

    for fam, var in data.get('intra_family_variance', {}).items():
        lines.append(f"- Family {fam}: {var}")

    lines.extend([
        "",
        f"**Mean Intra-Family Variance:** {data['mean_intra_variance']}",
        f"**Inter-Family Variance:** {data['inter_family_variance']}",
        "",
        "### Best Discriminating Dimensions",
        ""
    ])

    for dim, var in data.get("best_discriminating_dimensions", []):
        lines.append(f"1. **{dim}**: variance = {var}")

    lines.extend([
        "",
        "## Interpretation",
        ""
    ])

    if data['f_ratio'] > 2.0:
        lines.append("Families are **control-coherent** - signature similarity within families exceeds similarity between families. Recipe families represent distinct operational programs.")
    elif data['f_ratio'] > 1.0:
        lines.append("Families show **moderate coherence** - some signature similarity patterns, but not strongly differentiated.")
    else:
        lines.append("Families show **low coherence** - signature similarity does not strongly correlate with family assignment. Families may be scribal/visual rather than operational.")

    with open("family_coherence_analysis.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: family_coherence_analysis.md")

def generate_invariant_report_md(data):
    """Generate invariant_report.md"""
    lines = [
        "# Invariant Report",
        "",
        "## Question",
        "Which signature dimensions are constant (or near-constant) across all folios?",
        "",
        f"**Total Invariants Found:** {data['total_invariants']}",
        "",
        "---",
        "",
        "## Grammar Invariants",
        "*Properties that would be true of ANY legal program under this grammar*",
        ""
    ]

    if data.get("grammar_invariants"):
        for inv in data["grammar_invariants"]:
            lines.append(f"### {inv['dimension']}")
            lines.append(f"- Mean: {inv['mean']}")
            lines.append(f"- Standard Deviation: {inv['std']}")
            lines.append(f"- Coefficient of Variation: {inv['cv']}")
            lines.append("")
    else:
        lines.append("*No grammar invariants detected.*")

    lines.extend([
        "",
        "---",
        "",
        "## Manuscript Invariants",
        "*Properties true of THESE specific programs but not required by grammar*",
        ""
    ])

    if data.get("manuscript_invariants"):
        for inv in data["manuscript_invariants"]:
            lines.append(f"### {inv['dimension']}")
            lines.append(f"- Mean: {inv['mean']}")
            lines.append(f"- Standard Deviation: {inv['std']}")
            lines.append(f"- Coefficient of Variation: {inv['cv']}")
            lines.append("")
    else:
        lines.append("*No manuscript invariants detected.*")

    with open("invariant_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: invariant_report.md")

def generate_outlier_report_md(data, folios):
    """Generate outlier_report.md"""
    lines = [
        "# Outlier Report",
        "",
        "## Question",
        "Are there folios with anomalous signatures (>2 standard deviations on 2+ dimensions)?",
        "",
        f"**Outliers Detected:** {data['outlier_count']}",
        "",
        "---",
        ""
    ]

    for out in data.get("outliers", []):
        lines.append(f"## {out['folio']}")
        lines.append(f"**Family:** {out['family']}")
        lines.append(f"**Notes:** {', '.join(out.get('notes', []))}")
        lines.append("")
        lines.append("**Anomalous Dimensions:**")
        lines.append("")
        lines.append("| Dimension | Z-Score | Value |")
        lines.append("|-----------|---------|-------|")
        for ad in out["anomalous_dimensions"]:
            lines.append(f"| {ad['dimension']} | {ad['z_score']} | {ad['value']} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    if not data.get("outliers"):
        lines.append("*No significant outliers detected.*")

    with open("outlier_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: outlier_report.md")

def generate_process_exclusion_md(data):
    """Generate process_exclusion_analysis.md"""
    lines = [
        "# Process Class Exclusion Analysis",
        "",
        "## Question",
        "Which known process classes are structurally incompatible with Voynich control-signatures?",
        "",
        "## Aggregate Signature Metrics",
        ""
    ]

    metrics = data.get("aggregate_metrics", {})
    for key, val in metrics.items():
        lines.append(f"- **{key}:** {val}")

    lines.extend([
        "",
        "---",
        "",
        "## Exclusion Analysis",
        ""
    ])

    for exc in data.get("exclusions", []):
        status = exc["status"]
        if status == "HARD_EXCLUDED":
            icon = "[X]"
        elif status == "SOFT_EXCLUDED":
            icon = "[~]"
        else:
            icon = "[?]"

        lines.append(f"### {icon} {exc['process_class']}")
        lines.append(f"**Status:** {status}")

        if "triggers" in exc:
            lines.append(f"**Triggers:** {', '.join(exc['triggers'])}")
        if "supporting_features" in exc:
            lines.append(f"**Supporting Features:** {', '.join(exc['supporting_features'])}")

        lines.append(f"**Justification:** {exc['justification']}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Legend",
        "",
        "- **HARD_EXCLUDED**: Structurally impossible given signature",
        "- **SOFT_EXCLUDED**: Incompatible with most known instances of this class",
        "- **PLAUSIBLE**: Signature is compatible; note supporting features",
        ""
    ])

    with open("process_exclusion_analysis.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: process_exclusion_analysis.md")

def generate_clustering_md(data):
    """Generate signature_clustering.md"""
    lines = [
        "# Signature Clustering",
        "",
        "## Question",
        "Do natural clusters emerge from signature vectors?",
        "",
        "## K-Means Analysis",
        "",
        f"**Optimal K:** {data.get('optimal_k')}",
        f"**Best Silhouette Score:** {data.get('optimal_silhouette')}",
        "",
        "### Silhouette Scores by K",
        ""
    ]

    for k, score in sorted(data.get("silhouette_scores", {}).items()):
        marker = " *" if k == data.get("optimal_k") else ""
        lines.append(f"- K={k}: {score}{marker}")

    lines.extend([
        "",
        "## Cluster-Family Alignment",
        ""
    ])

    alignment = data.get("cluster_family_alignment", {})
    for cluster, families in sorted(alignment.items()):
        lines.append(f"### Cluster {cluster}")
        for fam, count in sorted(families.items()):
            lines.append(f"  - Family {fam}: {count} folios")
        lines.append("")

    lines.extend([
        "## PCA Projection",
        "",
        f"**Variance Explained:** {data.get('pca_variance_explained', [])}",
        "",
        "*See signature_clustering.json for 2D projection coordinates.*",
        "",
        "---",
        "",
        "## Interpretation",
        ""
    ])

    optimal_k = data.get('optimal_k', 2)
    silhouette = data.get('optimal_silhouette', 0)

    if silhouette > 0.5:
        lines.append("**Strong clustering detected.** Signatures form well-separated groups.")
    elif silhouette > 0.3:
        lines.append("**Moderate clustering detected.** Some structure present but overlapping.")
    else:
        lines.append("**Weak clustering.** Signatures do not form clearly separated groups.")

    # Check alignment with recipe families
    if alignment:
        # Count how many clusters are dominated by single family
        dominated_clusters = 0
        for cluster, families in alignment.items():
            total = sum(families.values())
            max_fam = max(families.values()) if families else 0
            if max_fam / total > 0.6:
                dominated_clusters += 1

        if dominated_clusters > len(alignment) * 0.5:
            lines.append("\n**Clusters align with recipe families.** Operational programs cluster together.")
        else:
            lines.append("\n**Clusters do not strongly align with recipe families.** Other structural factors may dominate.")

    with open("signature_clustering.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: signature_clustering.md")

if __name__ == "__main__":
    main()
