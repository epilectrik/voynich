#!/usr/bin/env python3
"""
VOYNICH PROCESS-FAMILY SYNTAX SIGNIFICANCE TEST
Extreme Brute-Force Structural Validation

PRE-REGISTERED HYPOTHESES:
H0: Process families and their prefix/suffix syntax have NO causal role in execution
H1: Process families correspond to emergent statistical clusters with limited influence
H2: Process families are functionally necessary; disrupting syntax degrades execution

ALL 5 TESTS MUST BE RUN.
"""

import json
import random
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from sklearn.metrics import adjusted_rand_score
from sklearn.cluster import AgglomerativeClustering
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# DATA LOADING
# ============================================================================

def load_corpus():
    """Load transcription corpus."""
    corpus_path = Path("data/transcriptions/interlinear_full_words.txt")
    records = []
    with open(corpus_path, "r", encoding="utf-8") as f:
        header = True
        for line in f:
            if header:
                header = False
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                # Column 0: word, Column 2: folio
                token = parts[0].strip('"')
                folio = parts[2].strip('"')
                if token and folio:
                    records.append({
                        "folio": folio,
                        "token": token
                    })
    return records

def load_families():
    """Load process family definitions."""
    with open("phase20c_recipe_clusters.json", "r") as f:
        data = json.load(f)
    families = {}
    for fam in data["families"]:
        family_id = fam["family_id"]
        for folio in fam["member_folios"]:
            families[folio] = family_id
    return families, data["families"]

def load_equivalence_classes():
    """Load 49 instruction classes."""
    with open("phase20a_operator_equivalence.json", "r") as f:
        data = json.load(f)
    token_to_class = {}
    class_to_tokens = defaultdict(list)
    for cls in data["classes"]:
        class_id = cls["class_id"]
        for member in cls["members"]:
            if member:
                token_to_class[member] = class_id
                class_to_tokens[class_id].append(member)
    return token_to_class, class_to_tokens, data["classes"]

def load_grammar():
    """Load canonical grammar with forbidden transitions."""
    with open("phase20d_canonical_grammar.json", "r") as f:
        data = json.load(f)

    forbidden = set()
    for constraint in data["constraints"]["sample"]:
        if constraint["type"] == "FORBIDDEN":
            pattern = constraint["pattern"]
            parts = pattern.split(" -> ")
            if len(parts) == 2:
                forbidden.add((parts[0].strip(), parts[1].strip()))
    return forbidden, data

def load_affixes():
    """Load affix operator definitions."""
    with open("phase7b_affix_operations.json", "r") as f:
        data = json.load(f)
    return data["affix_operation_table"]

# ============================================================================
# AFFIX EXTRACTION
# ============================================================================

KNOWN_PREFIXES = [
    "qok", "qot", "qo", "cho", "cha", "che", "ch", "sho", "sha", "she", "sh",
    "oke", "ote", "oko", "ota", "ok", "ot", "ol", "op", "of", "oc",
    "dai", "da", "ai", "al", "ar", "or",
    "cp", "cf", "fc", "pc", "po", "ps", "ts",
    "yk", "yt", "yc", "yp",
    "lk", "lc", "ls",
    "kc", "ke", "ko",
    "tc", "te", "to",
    "dc", "ds", "do",
    "sa", "so", "ra", "ro"
]
KNOWN_PREFIXES = sorted(KNOWN_PREFIXES, key=len, reverse=True)

KNOWN_SUFFIXES = [
    "aiin", "eedy", "eey", "edy", "ey", "hy", "dy",
    "ain", "iin", "in", "an",
    "ol", "al", "ar", "or", "ir", "am",
    "y", "d", "s", "o", "r", "l", "m"
]
KNOWN_SUFFIXES = sorted(KNOWN_SUFFIXES, key=len, reverse=True)

def extract_prefix(token):
    """Extract prefix from token."""
    for prefix in KNOWN_PREFIXES:
        if token.startswith(prefix) and len(token) > len(prefix):
            return prefix
    return ""

def extract_suffix(token):
    """Extract suffix from token."""
    for suffix in KNOWN_SUFFIXES:
        if token.endswith(suffix) and len(token) > len(suffix):
            return suffix
    return ""

def extract_middle(token, prefix, suffix):
    """Extract middle after removing prefix and suffix."""
    start = len(prefix) if prefix else 0
    end = len(token) - len(suffix) if suffix else len(token)
    return token[start:end] if end > start else token

# ============================================================================
# EXECUTION METRICS
# ============================================================================

def compute_execution_metrics(tokens, token_to_class, forbidden):
    """
    Compute execution metrics for a sequence of tokens.
    Returns: legality, convergence, hazard_count, kernel_adjacency
    """
    if not tokens:
        return {"legality": 1.0, "convergence": 0.0, "hazard_count": 0, "kernel_adjacency": 0.0}

    # Count forbidden transitions
    violations = 0
    total_transitions = 0
    for i in range(len(tokens) - 1):
        t1, t2 = tokens[i], tokens[i+1]
        total_transitions += 1
        if (t1, t2) in forbidden:
            violations += 1

    legality = 1.0 - (violations / max(total_transitions, 1))

    # Convergence: measure concentration in classes 32 (daiin), 33 (ol), 34 (aiin/o)
    kernel_classes = {32, 33, 34, 30, 31}  # Core control classes
    kernel_count = sum(1 for t in tokens if token_to_class.get(t, 0) in kernel_classes)
    convergence = kernel_count / len(tokens) if tokens else 0

    # Hazard proximity: how many tokens are adjacent to forbidden pairs
    hazard_nodes = set()
    for (a, b) in forbidden:
        hazard_nodes.add(a)
        hazard_nodes.add(b)
    hazard_adjacent = sum(1 for t in tokens if t in hazard_nodes)
    kernel_adjacency = hazard_adjacent / len(tokens) if tokens else 0

    return {
        "legality": legality,
        "convergence": convergence,
        "hazard_count": violations,
        "kernel_adjacency": kernel_adjacency
    }

# ============================================================================
# TEST 1: FAMILY SYNTAX RANDOMIZATION (PRIMARY KILL TEST)
# ============================================================================

def test1_family_syntax_randomization(folio_data, families, token_to_class,
                                       class_to_tokens, forbidden, n_iterations=10000):
    """
    Test whether family-specific prefix/suffix syntax is required for execution.

    Procedure:
    - Preserve instruction class order
    - Preserve token counts
    - Randomly shuffle prefix/suffix morphology ACROSS families

    Kill criterion: If randomized manuscripts match original within noise -> H0 survives
    """
    print("=" * 70)
    print("TEST 1: FAMILY SYNTAX RANDOMIZATION (PRIMARY KILL TEST)")
    print("=" * 70)
    import sys

    # Extract per-family prefix/suffix distributions
    print("Extracting family data...", flush=True)
    family_prefixes = defaultdict(list)
    family_suffixes = defaultdict(list)
    family_tokens = defaultdict(list)

    for folio, tokens in folio_data.items():
        if folio not in families:
            continue
        fam_id = families[folio]
        # Limit tokens per family to prevent memory issues
        tokens_sample = tokens[:1000] if len(tokens) > 1000 else tokens
        for token in tokens_sample:
            prefix = extract_prefix(token)
            suffix = extract_suffix(token)
            if prefix:
                family_prefixes[fam_id].append(prefix)
            if suffix:
                family_suffixes[fam_id].append(suffix)
            family_tokens[fam_id].append(token)

    print(f"Found {len(family_tokens)} families with data", flush=True)
    for fam_id, tokens in family_tokens.items():
        print(f"  Family {fam_id}: {len(tokens)} tokens", flush=True)

    # Compute original metrics per family
    original_metrics = {}
    for fam_id, tokens in family_tokens.items():
        original_metrics[fam_id] = compute_execution_metrics(tokens, token_to_class, forbidden)

    # Global prefix/suffix pools (for cross-family shuffling)
    all_prefixes = []
    all_suffixes = []
    for prefixes in family_prefixes.values():
        all_prefixes.extend(prefixes)
    for suffixes in family_suffixes.values():
        all_suffixes.extend(suffixes)

    # Run randomization iterations
    randomized_results = defaultdict(list)

    print(f"Running {n_iterations} randomization iterations...", flush=True)
    for iteration in range(n_iterations):
        if iteration % 100 == 0:
            print(f"  Iteration {iteration}/{n_iterations}", flush=True)

        for fam_id, tokens in family_tokens.items():
            # Create randomized version: same class sequence, random prefix/suffix
            randomized_tokens = []
            for token in tokens:
                cls_id = token_to_class.get(token, 0)

                # Get a random token from the same class
                if cls_id in class_to_tokens and class_to_tokens[cls_id]:
                    # Choose random member from same class
                    new_token = random.choice(class_to_tokens[cls_id])
                else:
                    new_token = token

                # Now swap prefix/suffix from global pool
                if random.random() < 0.5 and all_prefixes:
                    old_prefix = extract_prefix(new_token)
                    old_suffix = extract_suffix(new_token)
                    middle = extract_middle(new_token, old_prefix, old_suffix)

                    new_prefix = random.choice(all_prefixes) if random.random() < 0.5 else old_prefix
                    new_suffix = random.choice(all_suffixes) if random.random() < 0.5 else old_suffix

                    # Reconstruct token (this may create non-existent tokens - that's the test)
                    new_token = new_prefix + middle + new_suffix

                randomized_tokens.append(new_token)

            metrics = compute_execution_metrics(randomized_tokens, token_to_class, forbidden)
            for key, value in metrics.items():
                randomized_results[(fam_id, key)].append(value)

    # Compute statistics
    print("\n--- RESULTS ---")
    results = {
        "test_name": "FAMILY_SYNTAX_RANDOMIZATION",
        "iterations": n_iterations,
        "per_family": {},
        "aggregate": {}
    }

    all_original_legality = []
    all_random_legality = []
    all_original_convergence = []
    all_random_convergence = []

    # Effect size: Cohen's d
    def cohens_d(orig_val, rand_vals):
        if not rand_vals or np.std(rand_vals) == 0:
            return 0.0
        return (orig_val - np.mean(rand_vals)) / np.std(rand_vals)

    for fam_id in sorted(original_metrics.keys()):
        orig = original_metrics[fam_id]

        rand_legality = randomized_results[(fam_id, "legality")]
        rand_convergence = randomized_results[(fam_id, "convergence")]
        rand_hazard = randomized_results[(fam_id, "hazard_count")]
        rand_kernel = randomized_results[(fam_id, "kernel_adjacency")]

        d_legality = cohens_d(orig["legality"], rand_legality)
        d_convergence = cohens_d(orig["convergence"], rand_convergence)

        results["per_family"][fam_id] = {
            "original_legality": orig["legality"],
            "random_legality_mean": np.mean(rand_legality),
            "random_legality_std": np.std(rand_legality),
            "effect_size_legality": d_legality,
            "original_convergence": orig["convergence"],
            "random_convergence_mean": np.mean(rand_convergence),
            "effect_size_convergence": d_convergence
        }

        all_original_legality.append(orig["legality"])
        all_random_legality.extend(rand_legality)
        all_original_convergence.append(orig["convergence"])
        all_random_convergence.extend(rand_convergence)

        print(f"Family {fam_id}:")
        print(f"  Original legality: {orig['legality']:.4f}, Random mean: {np.mean(rand_legality):.4f} (d={d_legality:.3f})")
        print(f"  Original convergence: {orig['convergence']:.4f}, Random mean: {np.mean(rand_convergence):.4f} (d={d_convergence:.3f})")

    # Aggregate effect
    aggregate_d_legality = cohens_d(np.mean(all_original_legality), all_random_legality)
    aggregate_d_convergence = cohens_d(np.mean(all_original_convergence), all_random_convergence)

    results["aggregate"] = {
        "original_legality_mean": np.mean(all_original_legality),
        "random_legality_mean": np.mean(all_random_legality),
        "aggregate_effect_legality": aggregate_d_legality,
        "original_convergence_mean": np.mean(all_original_convergence),
        "random_convergence_mean": np.mean(all_random_convergence),
        "aggregate_effect_convergence": aggregate_d_convergence
    }

    # Kill criterion: effect size < 0.2 = trivial, H0 survives
    if abs(aggregate_d_legality) < 0.2 and abs(aggregate_d_convergence) < 0.2:
        verdict = "H0_SURVIVES"
        interpretation = "Randomized manuscripts match original within noise. Family syntax has NO causal role."
    elif abs(aggregate_d_legality) < 0.5 and abs(aggregate_d_convergence) < 0.5:
        verdict = "H1_WEAK_STRUCTURE"
        interpretation = "Small effect detected. Family syntax has LIMITED, non-essential influence."
    else:
        verdict = "H2_STRONG_STRUCTURE"
        interpretation = "Large effect detected. Family syntax is FUNCTIONALLY NECESSARY."

    results["verdict"] = verdict
    results["interpretation"] = interpretation

    print(f"\n*** VERDICT: {verdict} ***")
    print(f"Aggregate effect (legality): {aggregate_d_legality:.3f}")
    print(f"Aggregate effect (convergence): {aggregate_d_convergence:.3f}")
    print(interpretation)

    return results

# ============================================================================
# TEST 2: FAMILY LABEL ERASURE
# ============================================================================

def test2_family_label_erasure(folio_data, families, token_to_class, forbidden):
    """
    Test whether family identity carries explanatory power.

    Procedure:
    - Collapse all family labels
    - Re-cluster solely on execution metrics
    - Compare recovered clusters to original families

    Metric: Adjusted Rand Index (ARI)
    - ARI ~ 0 -> families not structural
    - ARI >> 0 -> families reflect intrinsic structure
    """
    print("\n" + "=" * 70)
    print("TEST 2: FAMILY LABEL ERASURE")
    print("=" * 70)

    # Compute execution features per folio
    folio_features = []
    folio_labels = []
    folio_names = []

    for folio, tokens in folio_data.items():
        if folio not in families:
            continue

        metrics = compute_execution_metrics(tokens, token_to_class, forbidden)

        # Feature vector: [legality, convergence, kernel_adjacency, length_normalized]
        features = [
            metrics["legality"],
            metrics["convergence"],
            metrics["kernel_adjacency"],
            len(tokens) / 1000.0  # Normalized length
        ]

        # Add prefix/suffix distribution features
        prefix_counts = Counter(extract_prefix(t) for t in tokens if extract_prefix(t))
        suffix_counts = Counter(extract_suffix(t) for t in tokens if extract_suffix(t))

        # Top 5 prefixes as features
        top_prefixes = ["qo", "ch", "sh", "ok", "ot"]
        for p in top_prefixes:
            features.append(prefix_counts.get(p, 0) / max(len(tokens), 1))

        # Top 5 suffixes as features
        top_suffixes = ["aiin", "edy", "ol", "ar", "y"]
        for s in top_suffixes:
            features.append(suffix_counts.get(s, 0) / max(len(tokens), 1))

        folio_features.append(features)
        folio_labels.append(families[folio])
        folio_names.append(folio)

    if len(folio_features) < 10:
        print("Not enough folios for clustering analysis.")
        return {"verdict": "INSUFFICIENT_DATA"}

    X = np.array(folio_features)
    true_labels = np.array(folio_labels)
    n_clusters = len(set(true_labels))

    print(f"Clustering {len(X)} folios into {n_clusters} clusters...")

    # Cluster without family labels
    clusterer = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
    recovered_labels = clusterer.fit_predict(X)

    # Compute ARI
    ari = adjusted_rand_score(true_labels, recovered_labels)

    print(f"Adjusted Rand Index: {ari:.4f}")

    # Interpretation
    if ari < 0.1:
        verdict = "FAMILIES_NOT_STRUCTURAL"
        interpretation = "Families cannot be recovered from execution metrics. They are DESCRIPTIVE artifacts."
    elif ari < 0.4:
        verdict = "FAMILIES_WEAKLY_STRUCTURAL"
        interpretation = "Partial recovery. Families have SOME structural basis but are not strongly defined."
    else:
        verdict = "FAMILIES_STRONGLY_STRUCTURAL"
        interpretation = "High recovery. Families reflect INTRINSIC execution structure."

    results = {
        "test_name": "FAMILY_LABEL_ERASURE",
        "n_folios": len(X),
        "n_clusters": n_clusters,
        "adjusted_rand_index": ari,
        "verdict": verdict,
        "interpretation": interpretation
    }

    print(f"\n*** VERDICT: {verdict} ***")
    print(interpretation)

    return results

# ============================================================================
# TEST 3: CROSS-FAMILY SYNTAX TRANSPLANT
# ============================================================================

def test3_cross_family_transplant(folio_data, families, family_defs,
                                   token_to_class, forbidden):
    """
    Test whether syntax from one family functions in another.

    Procedure:
    - Take token sequences from family A
    - Replace prefix/suffix patterns with those from family B
    - Preserve instruction-class skeleton

    High transferability -> weak structure
    Low transferability -> strong family specificity
    """
    print("\n" + "=" * 70)
    print("TEST 3: CROSS-FAMILY SYNTAX TRANSPLANT")
    print("=" * 70)

    # Build per-family prefix/suffix pools
    family_prefix_pool = defaultdict(list)
    family_suffix_pool = defaultdict(list)
    family_tokens = defaultdict(list)

    for folio, tokens in folio_data.items():
        if folio not in families:
            continue
        fam_id = families[folio]
        family_tokens[fam_id].extend(tokens)
        for token in tokens:
            p = extract_prefix(token)
            s = extract_suffix(token)
            if p:
                family_prefix_pool[fam_id].append(p)
            if s:
                family_suffix_pool[fam_id].append(s)

    # Get unique family IDs with sufficient data
    valid_families = [fam_id for fam_id in family_tokens if len(family_tokens[fam_id]) >= 100]

    if len(valid_families) < 2:
        print("Not enough families with sufficient data for transplant test.")
        return {"verdict": "INSUFFICIENT_DATA"}

    # Compute baseline metrics per family
    baseline_metrics = {}
    for fam_id in valid_families:
        baseline_metrics[fam_id] = compute_execution_metrics(
            family_tokens[fam_id], token_to_class, forbidden
        )

    # Perform bidirectional transplants
    transplant_results = []

    print(f"Testing transplants between {len(valid_families)} families...")

    for i, fam_a in enumerate(valid_families):
        for fam_b in valid_families[i+1:]:
            # A -> B transplant: take A's structure, use B's syntax
            transplanted_a_to_b = []
            for token in family_tokens[fam_a][:500]:  # Limit for speed
                old_p = extract_prefix(token)
                old_s = extract_suffix(token)
                middle = extract_middle(token, old_p, old_s)

                # Replace with family B syntax
                new_p = random.choice(family_prefix_pool[fam_b]) if family_prefix_pool[fam_b] and old_p else old_p
                new_s = random.choice(family_suffix_pool[fam_b]) if family_suffix_pool[fam_b] and old_s else old_s

                transplanted_a_to_b.append(new_p + middle + new_s)

            metrics_a_to_b = compute_execution_metrics(
                transplanted_a_to_b, token_to_class, forbidden
            )

            # B -> A transplant
            transplanted_b_to_a = []
            for token in family_tokens[fam_b][:500]:
                old_p = extract_prefix(token)
                old_s = extract_suffix(token)
                middle = extract_middle(token, old_p, old_s)

                new_p = random.choice(family_prefix_pool[fam_a]) if family_prefix_pool[fam_a] and old_p else old_p
                new_s = random.choice(family_suffix_pool[fam_a]) if family_suffix_pool[fam_a] and old_s else old_s

                transplanted_b_to_a.append(new_p + middle + new_s)

            metrics_b_to_a = compute_execution_metrics(
                transplanted_b_to_a, token_to_class, forbidden
            )

            # Compute degradation
            degradation_a = baseline_metrics[fam_a]["legality"] - metrics_a_to_b["legality"]
            degradation_b = baseline_metrics[fam_b]["legality"] - metrics_b_to_a["legality"]

            transplant_results.append({
                "pair": f"{fam_a}->{fam_b}",
                "baseline_a": baseline_metrics[fam_a]["legality"],
                "transplanted": metrics_a_to_b["legality"],
                "degradation": degradation_a
            })
            transplant_results.append({
                "pair": f"{fam_b}->{fam_a}",
                "baseline_b": baseline_metrics[fam_b]["legality"],
                "transplanted": metrics_b_to_a["legality"],
                "degradation": degradation_b
            })

    # Aggregate statistics
    all_degradations = [r["degradation"] for r in transplant_results]
    mean_degradation = np.mean(all_degradations)
    std_degradation = np.std(all_degradations)
    max_degradation = max(all_degradations)

    print(f"\nTransplant degradation statistics:")
    print(f"  Mean: {mean_degradation:.4f}")
    print(f"  Std: {std_degradation:.4f}")
    print(f"  Max: {max_degradation:.4f}")

    # High transferability = low degradation
    if mean_degradation < 0.01 and max_degradation < 0.05:
        verdict = "HIGH_TRANSFERABILITY"
        interpretation = "Syntax transplants cause minimal degradation. Family syntax is INTERCHANGEABLE."
    elif mean_degradation < 0.05:
        verdict = "MODERATE_TRANSFERABILITY"
        interpretation = "Some degradation but limited. Family syntax has WEAK specificity."
    else:
        verdict = "LOW_TRANSFERABILITY"
        interpretation = "Significant degradation. Family syntax has STRONG specificity."

    results = {
        "test_name": "CROSS_FAMILY_TRANSPLANT",
        "n_pairs_tested": len(transplant_results),
        "mean_degradation": mean_degradation,
        "std_degradation": std_degradation,
        "max_degradation": max_degradation,
        "details": transplant_results[:20],  # Top 20 for report
        "verdict": verdict,
        "interpretation": interpretation
    }

    print(f"\n*** VERDICT: {verdict} ***")
    print(interpretation)

    return results

# ============================================================================
# TEST 4: PARTIAL SYNTAX DEGRADATION CURVE
# ============================================================================

def test4_degradation_curve(folio_data, families, token_to_class,
                            class_to_tokens, forbidden, n_samples=100):
    """
    Measure how much family syntax can be damaged before failure.

    Procedure:
    - Gradually perturb prefix/suffix structures (0-100%)
    - Measure degradation curves

    Metrics: Stability half-life, Hazard onset threshold
    """
    print("\n" + "=" * 70)
    print("TEST 4: PARTIAL SYNTAX DEGRADATION CURVE")
    print("=" * 70)

    # Collect all tokens with family labels
    all_tokens = []
    for folio, tokens in folio_data.items():
        if folio in families:
            all_tokens.extend(tokens)

    if len(all_tokens) < 1000:
        print("Insufficient data for degradation curve analysis.")
        return {"verdict": "INSUFFICIENT_DATA"}

    # Build global prefix/suffix pools
    all_prefixes = [extract_prefix(t) for t in all_tokens if extract_prefix(t)]
    all_suffixes = [extract_suffix(t) for t in all_tokens if extract_suffix(t)]

    # Baseline metrics
    baseline = compute_execution_metrics(all_tokens[:5000], token_to_class, forbidden)
    print(f"Baseline legality: {baseline['legality']:.4f}")
    print(f"Baseline convergence: {baseline['convergence']:.4f}")

    # Test degradation at different perturbation levels
    perturbation_levels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    degradation_curve = []

    print("\nTesting perturbation levels...")
    for pct in perturbation_levels:
        legalities = []
        convergences = []

        for _ in range(n_samples):
            perturbed_tokens = []
            for token in all_tokens[:2000]:  # Sample for speed
                if random.random() * 100 < pct:
                    # Perturb this token's syntax
                    old_p = extract_prefix(token)
                    old_s = extract_suffix(token)
                    middle = extract_middle(token, old_p, old_s)

                    new_p = random.choice(all_prefixes) if all_prefixes and old_p else old_p
                    new_s = random.choice(all_suffixes) if all_suffixes and old_s else old_s

                    perturbed_tokens.append(new_p + middle + new_s)
                else:
                    perturbed_tokens.append(token)

            metrics = compute_execution_metrics(perturbed_tokens, token_to_class, forbidden)
            legalities.append(metrics["legality"])
            convergences.append(metrics["convergence"])

        mean_legality = np.mean(legalities)
        mean_convergence = np.mean(convergences)

        degradation_curve.append({
            "perturbation_pct": pct,
            "mean_legality": mean_legality,
            "mean_convergence": mean_convergence,
            "legality_std": np.std(legalities),
            "convergence_std": np.std(convergences)
        })

        print(f"  {pct}%: legality={mean_legality:.4f}, convergence={mean_convergence:.4f}")

    # Find stability half-life (perturbation level where metrics drop to 50% of baseline)
    half_life_legality = None
    half_life_convergence = None

    half_target_legality = baseline["legality"] * 0.5
    half_target_convergence = baseline["convergence"] * 0.5

    for point in degradation_curve:
        if half_life_legality is None and point["mean_legality"] < half_target_legality:
            half_life_legality = point["perturbation_pct"]
        if half_life_convergence is None and point["mean_convergence"] < half_target_convergence:
            half_life_convergence = point["perturbation_pct"]

    # If metrics never drop to 50%, system is highly robust
    if half_life_legality is None:
        half_life_legality = ">100%"
    if half_life_convergence is None:
        half_life_convergence = ">100%"

    # Compute total degradation from 0% to 100%
    total_degradation_legality = degradation_curve[0]["mean_legality"] - degradation_curve[-1]["mean_legality"]
    total_degradation_convergence = degradation_curve[0]["mean_convergence"] - degradation_curve[-1]["mean_convergence"]

    print(f"\nHalf-life (legality): {half_life_legality}")
    print(f"Half-life (convergence): {half_life_convergence}")
    print(f"Total degradation (legality): {total_degradation_legality:.4f}")
    print(f"Total degradation (convergence): {total_degradation_convergence:.4f}")

    # Interpretation
    if total_degradation_legality < 0.02 and total_degradation_convergence < 0.02:
        verdict = "SYNTAX_IRRELEVANT"
        interpretation = "100% perturbation causes <2% degradation. Syntax is DECORATIVE."
    elif total_degradation_legality < 0.1:
        verdict = "SYNTAX_MARGINAL"
        interpretation = "Full perturbation causes <10% degradation. Syntax has MARGINAL impact."
    else:
        verdict = "SYNTAX_CRITICAL"
        interpretation = "Significant degradation under perturbation. Syntax is FUNCTIONALLY CRITICAL."

    results = {
        "test_name": "DEGRADATION_CURVE",
        "baseline_legality": baseline["legality"],
        "baseline_convergence": baseline["convergence"],
        "degradation_curve": degradation_curve,
        "half_life_legality": half_life_legality,
        "half_life_convergence": half_life_convergence,
        "total_degradation_legality": total_degradation_legality,
        "total_degradation_convergence": total_degradation_convergence,
        "verdict": verdict,
        "interpretation": interpretation
    }

    print(f"\n*** VERDICT: {verdict} ***")
    print(interpretation)

    return results

# ============================================================================
# TEST 5: SYNTHETIC FAMILY GENERATION CONTROL
# ============================================================================

def test5_synthetic_control(folio_data, families, token_to_class, forbidden):
    """
    Ensure families are not detection artifacts.

    Procedure:
    - Generate synthetic grammar with same token inventory but random adjacency
    - Force identical clustering procedure

    If synthetic families show similar "syntax" effects -> artifact
    If not -> real structure
    """
    print("\n" + "=" * 70)
    print("TEST 5: SYNTHETIC FAMILY GENERATION CONTROL")
    print("=" * 70)

    # Collect all tokens and their classes
    all_tokens = []
    for folio, tokens in folio_data.items():
        if folio in families:
            all_tokens.extend(tokens)

    unique_tokens = list(set(all_tokens))
    print(f"Vocabulary size: {len(unique_tokens)} unique tokens")

    # Generate synthetic folios by random sampling (preserving token inventory)
    n_synthetic_folios = 50
    synthetic_folio_size = 500

    synthetic_folios = {}
    for i in range(n_synthetic_folios):
        synthetic_folios[f"synthetic_{i}"] = random.choices(unique_tokens, k=synthetic_folio_size)

    # Compute execution features for synthetic folios
    synthetic_features = []
    for folio, tokens in synthetic_folios.items():
        metrics = compute_execution_metrics(tokens, token_to_class, forbidden)

        features = [
            metrics["legality"],
            metrics["convergence"],
            metrics["kernel_adjacency"],
            len(tokens) / 1000.0
        ]

        prefix_counts = Counter(extract_prefix(t) for t in tokens if extract_prefix(t))
        suffix_counts = Counter(extract_suffix(t) for t in tokens if extract_suffix(t))

        top_prefixes = ["qo", "ch", "sh", "ok", "ot"]
        for p in top_prefixes:
            features.append(prefix_counts.get(p, 0) / max(len(tokens), 1))

        top_suffixes = ["aiin", "edy", "ol", "ar", "y"]
        for s in top_suffixes:
            features.append(suffix_counts.get(s, 0) / max(len(tokens), 1))

        synthetic_features.append(features)

    X_synthetic = np.array(synthetic_features)

    # Cluster synthetic folios
    n_clusters = len(set(families.values()))
    clusterer = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
    synthetic_labels = clusterer.fit_predict(X_synthetic)

    # Measure within-cluster variance for synthetic families
    synthetic_within_var = []
    for cluster_id in range(n_clusters):
        cluster_mask = synthetic_labels == cluster_id
        if cluster_mask.sum() > 1:
            cluster_features = X_synthetic[cluster_mask]
            within_var = np.var(cluster_features, axis=0).mean()
            synthetic_within_var.append(within_var)

    mean_synthetic_var = np.mean(synthetic_within_var) if synthetic_within_var else 0

    # Now compare to real families
    real_features = []
    real_labels = []
    for folio, tokens in folio_data.items():
        if folio not in families:
            continue

        metrics = compute_execution_metrics(tokens, token_to_class, forbidden)
        features = [
            metrics["legality"],
            metrics["convergence"],
            metrics["kernel_adjacency"],
            len(tokens) / 1000.0
        ]

        prefix_counts = Counter(extract_prefix(t) for t in tokens if extract_prefix(t))
        suffix_counts = Counter(extract_suffix(t) for t in tokens if extract_suffix(t))

        for p in ["qo", "ch", "sh", "ok", "ot"]:
            features.append(prefix_counts.get(p, 0) / max(len(tokens), 1))
        for s in ["aiin", "edy", "ol", "ar", "y"]:
            features.append(suffix_counts.get(s, 0) / max(len(tokens), 1))

        real_features.append(features)
        real_labels.append(families[folio])

    X_real = np.array(real_features)
    real_labels = np.array(real_labels)

    # Compute within-cluster variance for real families
    real_within_var = []
    for fam_id in set(real_labels):
        cluster_mask = real_labels == fam_id
        if cluster_mask.sum() > 1:
            cluster_features = X_real[cluster_mask]
            within_var = np.var(cluster_features, axis=0).mean()
            real_within_var.append(within_var)

    mean_real_var = np.mean(real_within_var) if real_within_var else 0

    print(f"\nReal family within-cluster variance: {mean_real_var:.6f}")
    print(f"Synthetic family within-cluster variance: {mean_synthetic_var:.6f}")

    # If synthetic variance is similar or lower -> families are artifacts
    variance_ratio = mean_real_var / max(mean_synthetic_var, 1e-10)

    print(f"Variance ratio (real/synthetic): {variance_ratio:.4f}")

    if variance_ratio > 0.5 and variance_ratio < 2.0:
        verdict = "FAMILIES_ARTIFACTUAL"
        interpretation = "Synthetic clustering produces similar structure. Families may be DETECTION ARTIFACTS."
    elif variance_ratio < 0.5:
        verdict = "FAMILIES_STRUCTURED"
        interpretation = "Real families have LOWER variance than synthetic. Families reflect REAL structure."
    else:
        verdict = "FAMILIES_WEAKLY_STRUCTURED"
        interpretation = "Real families have higher variance but within tolerance. Structure is WEAK."

    results = {
        "test_name": "SYNTHETIC_CONTROL",
        "n_synthetic_folios": n_synthetic_folios,
        "n_real_folios": len(X_real),
        "n_clusters": n_clusters,
        "real_within_cluster_variance": mean_real_var,
        "synthetic_within_cluster_variance": mean_synthetic_var,
        "variance_ratio": variance_ratio,
        "verdict": verdict,
        "interpretation": interpretation
    }

    print(f"\n*** VERDICT: {verdict} ***")
    print(interpretation)

    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("VOYNICH PROCESS-FAMILY SYNTAX SIGNIFICANCE TEST")
    print("=" * 70)
    print("\nLoading data...")

    # Load all required data
    records = load_corpus()
    families, family_defs = load_families()
    token_to_class, class_to_tokens, classes = load_equivalence_classes()
    forbidden, grammar = load_grammar()
    affixes = load_affixes()

    print(f"Loaded {len(records)} records")
    print(f"Loaded {len(families)} folio->family mappings")
    print(f"Loaded {len(token_to_class)} token->class mappings")
    print(f"Loaded {len(forbidden)} forbidden transitions")

    # Organize tokens by folio
    folio_data = defaultdict(list)
    for rec in records:
        if rec["token"]:
            folio_data[rec["folio"]].append(rec["token"])

    print(f"Organized tokens for {len(folio_data)} folios")

    # Run all tests
    all_results = {}

    # Test 1: Family Syntax Randomization (PRIMARY KILL TEST)
    all_results["test1"] = test1_family_syntax_randomization(
        folio_data, families, token_to_class, class_to_tokens, forbidden,
        n_iterations=1000  # Full statistical test
    )

    # Test 2: Family Label Erasure
    all_results["test2"] = test2_family_label_erasure(
        folio_data, families, token_to_class, forbidden
    )

    # Test 3: Cross-Family Syntax Transplant
    all_results["test3"] = test3_cross_family_transplant(
        folio_data, families, family_defs, token_to_class, forbidden
    )

    # Test 4: Partial Syntax Degradation Curve
    all_results["test4"] = test4_degradation_curve(
        folio_data, families, token_to_class, class_to_tokens, forbidden,
        n_samples=200  # Full statistical test
    )

    # Test 5: Synthetic Family Generation Control
    all_results["test5"] = test5_synthetic_control(
        folio_data, families, token_to_class, forbidden
    )

    # ========================================================================
    # FINAL VERDICT
    # ========================================================================
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)

    # Count signals for each hypothesis
    h0_signals = 0  # Syntax has NO causal role
    h1_signals = 0  # Weak structure
    h2_signals = 0  # Strong structure

    verdicts = []
    for test_name, result in all_results.items():
        verdict = result.get("verdict", "UNKNOWN")
        verdicts.append((test_name, verdict))

        if "H0" in verdict or "IRRELEVANT" in verdict or "ARTIFACTUAL" in verdict or "HIGH_TRANSFERABILITY" in verdict:
            h0_signals += 1
        elif "WEAK" in verdict or "MARGINAL" in verdict or "MODERATE" in verdict:
            h1_signals += 1
        elif "STRONG" in verdict or "CRITICAL" in verdict or "LOW_TRANSFERABILITY" in verdict or "STRUCTURED" in verdict:
            h2_signals += 1

    print("\nTest Results:")
    for test_name, verdict in verdicts:
        print(f"  {test_name}: {verdict}")

    print(f"\nSignal counts:")
    print(f"  H0 (no causal role): {h0_signals}")
    print(f"  H1 (weak structure): {h1_signals}")
    print(f"  H2 (strong structure): {h2_signals}")

    # Decision rule
    if h0_signals >= 3:
        final_verdict = "H0_SUPPORTED"
        final_interpretation = ("Family syntax has NO causal role in execution. "
                                "Families are DESCRIPTIVE CLUSTERS, not functional units.")
    elif h2_signals >= 3:
        final_verdict = "H2_SUPPORTED"
        final_interpretation = ("Family syntax is FUNCTIONALLY NECESSARY. "
                                "Families represent distinct operational programs.")
    else:
        final_verdict = "H1_SUPPORTED"
        final_interpretation = ("Family syntax has LIMITED, non-essential influence. "
                                "Families are emergent patterns with weak structural basis.")

    # Check for kill condition (Test 1)
    test1_verdict = all_results["test1"].get("verdict", "")
    if "H0_SURVIVES" in test1_verdict:
        final_verdict = "H0_SUPPORTED (KILL_CONDITION_MET)"
        final_interpretation = ("PRIMARY KILL TEST PASSED. Family syntax randomization "
                                "produces equivalent execution. H0 is STRONGLY SUPPORTED.")

    all_results["final_verdict"] = {
        "verdict": final_verdict,
        "interpretation": final_interpretation,
        "h0_signals": h0_signals,
        "h1_signals": h1_signals,
        "h2_signals": h2_signals
    }

    print(f"\n*** FINAL VERDICT: {final_verdict} ***")
    print(final_interpretation)

    # Save results
    with open("family_syntax_metrics.json", "w") as f:
        # Convert numpy types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(v) for v in obj]
            return obj

        json.dump(convert_numpy(all_results), f, indent=2)

    print("\nResults saved to family_syntax_metrics.json")

    # Generate markdown report
    generate_report(all_results)

    return all_results

def generate_report(results):
    """Generate markdown report."""
    report = """# Family Syntax Significance Test Report

*Generated: 2026-01-01*

---

## Executive Summary

"""

    final = results.get("final_verdict", {})
    verdict = final.get("verdict", "UNKNOWN")
    interpretation = final.get("interpretation", "")

    report += f"**FINAL VERDICT: {verdict}**\n\n"
    report += f"> {interpretation}\n\n"

    report += "---\n\n## Test Results\n\n"
    report += "| Test | Verdict | Key Finding |\n"
    report += "|------|---------|-------------|\n"

    for i in range(1, 6):
        test_key = f"test{i}"
        if test_key in results:
            r = results[test_key]
            test_name = r.get("test_name", f"Test {i}")
            test_verdict = r.get("verdict", "UNKNOWN")
            test_interp = r.get("interpretation", "")[:80] + "..." if len(r.get("interpretation", "")) > 80 else r.get("interpretation", "")
            report += f"| {test_name} | {test_verdict} | {test_interp} |\n"

    report += "\n---\n\n"

    # Test 1 details
    if "test1" in results:
        r = results["test1"]
        report += "## Test 1: Family Syntax Randomization\n\n"
        report += f"**Iterations:** {r.get('iterations', 'N/A')}\n\n"

        agg = r.get("aggregate", {})
        report += f"**Aggregate Effect Sizes:**\n"
        report += f"- Legality: d = {agg.get('aggregate_effect_legality', 0):.3f}\n"
        report += f"- Convergence: d = {agg.get('aggregate_effect_convergence', 0):.3f}\n\n"
        report += f"**Kill Criterion:** Effect size < 0.2 = trivial\n\n"
        report += f"**Verdict:** {r.get('verdict', 'UNKNOWN')}\n\n"

    # Test 2 details
    if "test2" in results:
        r = results["test2"]
        report += "## Test 2: Family Label Erasure\n\n"
        report += f"**Adjusted Rand Index:** {r.get('adjusted_rand_index', 0):.4f}\n\n"
        report += f"**Interpretation:**\n"
        report += f"- ARI ~ 0: Families cannot be recovered (descriptive)\n"
        report += f"- ARI >> 0: Families reflect intrinsic structure\n\n"
        report += f"**Verdict:** {r.get('verdict', 'UNKNOWN')}\n\n"

    # Test 3 details
    if "test3" in results:
        r = results["test3"]
        report += "## Test 3: Cross-Family Syntax Transplant\n\n"
        report += f"**Mean Degradation:** {r.get('mean_degradation', 0):.4f}\n"
        report += f"**Max Degradation:** {r.get('max_degradation', 0):.4f}\n\n"
        report += f"**Verdict:** {r.get('verdict', 'UNKNOWN')}\n\n"

    # Test 4 details
    if "test4" in results:
        r = results["test4"]
        report += "## Test 4: Partial Syntax Degradation Curve\n\n"
        report += f"**Baseline Legality:** {r.get('baseline_legality', 0):.4f}\n"
        report += f"**Total Degradation (0% to 100%):** {r.get('total_degradation_legality', 0):.4f}\n"
        report += f"**Half-life (Legality):** {r.get('half_life_legality', 'N/A')}\n\n"
        report += f"**Verdict:** {r.get('verdict', 'UNKNOWN')}\n\n"

    # Test 5 details
    if "test5" in results:
        r = results["test5"]
        report += "## Test 5: Synthetic Family Generation Control\n\n"
        report += f"**Variance Ratio (Real/Synthetic):** {r.get('variance_ratio', 0):.4f}\n\n"
        report += f"**Interpretation:**\n"
        report += f"- Ratio ~ 1: Synthetic produces similar structure (artifact)\n"
        report += f"- Ratio < 0.5: Real families have lower variance (real structure)\n\n"
        report += f"**Verdict:** {r.get('verdict', 'UNKNOWN')}\n\n"

    report += """---

## Hypothesis Summary

| Hypothesis | Description | Signals |
|------------|-------------|---------|
"""

    report += f"| H0 | Syntax has NO causal role | {final.get('h0_signals', 0)} |\n"
    report += f"| H1 | Weak emergent structure | {final.get('h1_signals', 0)} |\n"
    report += f"| H2 | Functionally necessary | {final.get('h2_signals', 0)} |\n\n"

    report += """---

## Interpretive Firewall

> All findings describe structural properties measured on textual data.
> No semantic interpretation of family content has been applied.
> Domain-specific language has been strictly avoided.

---

*Report generated by Family Syntax Significance Test Suite*
"""

    with open("family_syntax_significance_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("Report saved to family_syntax_significance_report.md")

if __name__ == "__main__":
    main()
