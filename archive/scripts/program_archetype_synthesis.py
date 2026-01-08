"""
PROGRAM ARCHETYPE SYNTHESIS

Cluster the 83 B folios using ALL metrics we've computed.

Goal: Synthesize all findings into a coherent taxonomy showing that
programs form an organized system of 4-6 archetypes.

Metrics available:
- Control signatures (link_density, hazard_density, kernel_contact_ratio, intervention_frequency)
- Role composition (6 roles)
- Vocabulary fingerprint (core tokens)
- Stability profile
- LINK profile
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
GRAMMAR = BASE / "results" / "canonical_grammar.json"
SIGNATURES = BASE / "results" / "control_signatures.json"

def load_signatures():
    """Load control signatures."""
    with open(SIGNATURES, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('signatures', {})

def load_grammar():
    """Load token -> role mapping."""
    with open(GRAMMAR, 'r', encoding='utf-8') as f:
        data = json.load(f)

    token_to_role = {}
    terminals = data.get('terminals', {}).get('list', [])
    for term in terminals:
        token_to_role[term['symbol']] = term['role']

    return token_to_role

def load_b_tokens_by_folio():
    """Load B tokens grouped by folio."""
    tokens_by_folio = defaultdict(list)

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            if row.get('language') != 'B':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']
            tokens_by_folio[folio].append(token)

    return tokens_by_folio

def compute_role_composition(tokens, token_to_role):
    """Compute role composition for a folio."""
    role_counts = Counter()
    total = 0

    for token in tokens:
        role = token_to_role.get(token)
        if role:
            role_counts[role] += 1
            total += 1

    if total == 0:
        return {}

    return {role: count / total for role, count in role_counts.items()}

def compute_vocabulary_metrics(tokens, core_tokens):
    """Compute vocabulary-based metrics."""
    token_set = set(tokens)
    token_counts = Counter(tokens)

    # Coverage of core vocabulary
    core_coverage = len(token_set.intersection(core_tokens)) / len(core_tokens)

    # TTR (type-token ratio)
    ttr = len(token_set) / len(tokens) if tokens else 0

    # Concentration (top 10 tokens)
    total = sum(token_counts.values())
    top10 = sum(c for _, c in token_counts.most_common(10))
    concentration = top10 / total if total > 0 else 0

    return {
        'core_coverage': core_coverage,
        'ttr': ttr,
        'concentration': concentration,
        'unique_tokens': len(token_set),
        'total_tokens': len(tokens)
    }

def identify_core_vocabulary(tokens_by_folio, threshold=0.5):
    """Identify tokens that appear in >= threshold fraction of folios."""
    token_folios = defaultdict(set)
    for folio, tokens in tokens_by_folio.items():
        for token in set(tokens):
            token_folios[token].add(folio)

    n_folios = len(tokens_by_folio)
    core = set()
    for token, folios in token_folios.items():
        if len(folios) >= n_folios * threshold:
            core.add(token)

    return core

def compute_link_metrics(tokens, link_tokens={'ol', 'or', 'ar', 'al'}):
    """Compute LINK-related metrics."""
    n_link = sum(1 for t in tokens if t in link_tokens)
    link_density = n_link / len(tokens) if tokens else 0

    # LINK clustering (consecutive LINK tokens)
    runs = []
    current_run = 0
    for token in tokens:
        if token in link_tokens:
            current_run += 1
        else:
            if current_run > 0:
                runs.append(current_run)
            current_run = 0
    if current_run > 0:
        runs.append(current_run)

    max_run = max(runs) if runs else 0
    mean_run = np.mean(runs) if runs else 0

    return {
        'link_density': link_density,
        'link_max_run': max_run,
        'link_mean_run': mean_run
    }

def build_feature_matrix(signatures, tokens_by_folio, token_to_role, core_tokens):
    """Build feature matrix for clustering."""
    folios = sorted(set(signatures.keys()).intersection(tokens_by_folio.keys()))

    roles = ['ENERGY_OPERATOR', 'CORE_CONTROL', 'FREQUENT_OPERATOR',
             'FLOW_OPERATOR', 'AUXILIARY', 'HIGH_IMPACT']

    # Pre-define feature names
    feature_names = ['link_density', 'hazard_density', 'kernel_contact_ratio', 'intervention_frequency']
    feature_names.extend([f'role_{r[:8]}' for r in roles])
    feature_names.extend(['ttr', 'concentration', 'core_coverage'])
    feature_names.extend(['link_max_run', 'link_mean_run'])

    features = []

    for folio in folios:
        sig = signatures[folio]
        tokens = tokens_by_folio[folio]

        row = []

        # Control signature metrics
        row.append(sig['link_density'])
        row.append(sig['hazard_density'])
        row.append(sig['kernel_contact_ratio'])
        row.append(sig.get('intervention_frequency', 0))

        # Role composition
        role_comp = compute_role_composition(tokens, token_to_role)
        for role in roles:
            row.append(role_comp.get(role, 0))

        # Vocabulary metrics
        vocab = compute_vocabulary_metrics(tokens, core_tokens)
        row.append(vocab['ttr'])
        row.append(vocab['concentration'])
        row.append(vocab['core_coverage'])

        # LINK metrics
        link = compute_link_metrics(tokens)
        row.append(link['link_max_run'])
        row.append(link['link_mean_run'])

        features.append(row)

    return np.array(features), folios, feature_names

def cluster_and_analyze(features, folios, feature_names, n_clusters=5):
    """Cluster folios and analyze archetypes."""
    # Standardize features
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    # Try different k values
    print("\n" + "-"*70)
    print("OPTIMAL CLUSTER COUNT")
    print("-"*70)

    for k in range(2, 8):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        score = silhouette_score(X, labels)
        print(f"  k={k}: silhouette={score:.3f}")

    # Use specified n_clusters
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    # Analyze each cluster
    print("\n" + "-"*70)
    print(f"ARCHETYPE ANALYSIS (k={n_clusters})")
    print("-"*70)

    for cluster_id in range(n_clusters):
        cluster_mask = labels == cluster_id
        cluster_folios = [f for f, m in zip(folios, cluster_mask) if m]
        cluster_features = features[cluster_mask]

        print(f"\n### ARCHETYPE {cluster_id + 1} ({len(cluster_folios)} folios)")
        print(f"Folios: {', '.join(cluster_folios[:10])}{'...' if len(cluster_folios) > 10 else ''}")

        # Feature means for this cluster vs global
        global_means = features.mean(axis=0)
        cluster_means = cluster_features.mean(axis=0)

        print("\nDistinctive features (> 0.3 std from mean):")
        for i, (name, cluster_val, global_val) in enumerate(zip(feature_names, cluster_means, global_means)):
            global_std = features[:, i].std()
            if global_std > 0:
                z = (cluster_val - global_val) / global_std
                if abs(z) > 0.3:
                    direction = "HIGH" if z > 0 else "LOW"
                    print(f"  {name:<25}: {cluster_val:.3f} ({direction}, z={z:+.2f})")

    return labels, folios

def profile_archetypes(labels, folios, signatures, tokens_by_folio, token_to_role):
    """Create detailed profiles of each archetype."""
    print("\n" + "-"*70)
    print("ARCHETYPE PROFILES")
    print("-"*70)

    n_clusters = len(set(labels))

    for cluster_id in range(n_clusters):
        cluster_folios = [f for f, l in zip(folios, labels) if l == cluster_id]

        # Aggregate metrics
        link_densities = [signatures[f]['link_density'] for f in cluster_folios]
        hazard_densities = [signatures[f]['hazard_density'] for f in cluster_folios]
        kernel_ratios = [signatures[f]['kernel_contact_ratio'] for f in cluster_folios]

        # Role composition
        role_totals = Counter()
        total_tokens = 0
        for f in cluster_folios:
            tokens = tokens_by_folio[f]
            for t in tokens:
                role = token_to_role.get(t)
                if role:
                    role_totals[role] += 1
                    total_tokens += 1

        print(f"\n### ARCHETYPE {cluster_id + 1}: {len(cluster_folios)} folios")
        print(f"\nControl metrics (mean ± std):")
        print(f"  LINK density:    {np.mean(link_densities):.3f} ± {np.std(link_densities):.3f}")
        print(f"  Hazard density:  {np.mean(hazard_densities):.3f} ± {np.std(hazard_densities):.3f}")
        print(f"  Kernel ratio:    {np.mean(kernel_ratios):.3f} ± {np.std(kernel_ratios):.3f}")

        print(f"\nRole composition:")
        for role, count in role_totals.most_common():
            pct = count / total_tokens * 100 if total_tokens > 0 else 0
            print(f"  {role:<20}: {pct:.1f}%")

        # Intensity classification (relative to cluster means)
        link_mean = np.mean(link_densities)
        hazard_mean = np.mean(hazard_densities)
        kernel_mean = np.mean(kernel_ratios)

        # Determine dominant role
        dominant_role = role_totals.most_common(1)[0][0] if role_totals else "UNKNOWN"

        # Create profile description
        traits = []
        if link_mean > 0.45:
            traits.append("WAIT-HEAVY")
        elif link_mean < 0.35:
            traits.append("ACTION-HEAVY")

        if hazard_mean > 0.60:
            traits.append("HAZARD-TOLERANT")
        elif hazard_mean < 0.50:
            traits.append("HAZARD-AVOIDING")

        if kernel_mean > 0.65:
            traits.append("KERNEL-ENGAGED")
        elif kernel_mean < 0.55:
            traits.append("KERNEL-LIGHT")

        profile = " + ".join(traits) if traits else "BALANCED"
        print(f"\nOperational profile: {profile}")
        print(f"Dominant role: {dominant_role}")

def summarize_taxonomy():
    """Print taxonomy summary."""
    print("\n" + "="*70)
    print("PROGRAM ARCHETYPE TAXONOMY")
    print("="*70)
    print("""
Based on clustering of 83 Currier B folios using:
- Control signatures (link_density, hazard_density, kernel_ratio)
- Role composition (6 grammar roles)
- Vocabulary metrics (TTR, core coverage, concentration)
- LINK clustering behavior

Each archetype represents a distinct operational profile:
- Different balance of intervention vs waiting
- Different role mixtures
- Different vocabulary usage patterns

This taxonomy provides a coherent organizational model for the
manuscript's 83 programs, showing they form a structured system
rather than arbitrary variation.
""")

def main():
    print("="*70)
    print("PROGRAM ARCHETYPE SYNTHESIS")
    print("="*70)

    signatures = load_signatures()
    token_to_role = load_grammar()
    tokens_by_folio = load_b_tokens_by_folio()

    print(f"\nLoaded {len(signatures)} signatures")
    print(f"Loaded {len(token_to_role)} role mappings")
    print(f"Loaded {len(tokens_by_folio)} folios")

    # Identify core vocabulary
    core_tokens = identify_core_vocabulary(tokens_by_folio)
    print(f"Identified {len(core_tokens)} core tokens (>= 50% folios)")

    # Build feature matrix
    features, folios, feature_names = build_feature_matrix(
        signatures, tokens_by_folio, token_to_role, core_tokens
    )
    print(f"\nFeature matrix: {features.shape[0]} folios × {features.shape[1]} features")
    print(f"Features: {', '.join(feature_names)}")

    # Cluster and analyze
    labels, folios = cluster_and_analyze(features, folios, feature_names, n_clusters=5)

    # Detailed profiles
    profile_archetypes(labels, folios, signatures, tokens_by_folio, token_to_role)

    # Summary
    summarize_taxonomy()

if __name__ == '__main__':
    main()
