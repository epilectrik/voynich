"""
SID-01.1: Section Regime Clustering Test

Tests whether section identity can be compressed into a smaller number of
stable residue regimes.

Parent Test: SID-01 (Global Residue Convergence)
Objective: Conditional structure reduction
"""

import sys
import os
import math
import random
import numpy as np
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional
from sklearn.cluster import KMeans, AgglomerativeClustering, SpectralClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.insert(0, r'C:\git\voynich')

# =============================================================================
# DATA LOADING
# =============================================================================

# Grammar tokens (from SID-01)
GRAMMAR_TOKENS = {
    'qokaiin', 'chey', 'cheey', 'chedy', 'okaiin', 'dar', 'okal', 'saiin',
    'qokal', 'daiin', 'dol', 'ckhey', 'chol', 'dy', 'cheky', 'tedy', 'ol',
    'aiin', 'checkhy', 'otain', 'shey', 'shol', 'shedy', 'shy', 'shor',
    'qo', 'qok', 'ok', 'al', 'or', 'ar', 'dal', 'qokedy', 'okey', 'okeey',
    'okedy', 'chee', 'cheol', 'ched', 'chor', 'char', 'sho', 'she',
    'qokeey', 'qokain', 'okain', 'sheey', 'sheo', 'otar',
    'oteey', 'otedy', 'okeedy', 'taiin', 'cthaiin', 'cthol', 'cthor', 'cthy',
    'kcheol', 'kchey', 'kcheedy', 'pchedy', 'pchey', 'fchedy', 'fchey'
}

# Forbidden transitions (from SID-01)
FORBIDDEN_PAIRS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'), ('chol', 'r'),
    ('chedy', 'ee'), ('chey', 'chedy'), ('l', 'chol'), ('dy', 'aiin'),
    ('dy', 'chey'), ('or', 'dal'), ('ar', 'chol'), ('qo', 'shey'),
    ('qo', 'shy'), ('ok', 'shol'), ('ol', 'shor'), ('dar', 'qokaiin'),
    ('qokaiin', 'qokedy')
]

HAZARD_TOKENS = set()
for a, b in FORBIDDEN_PAIRS:
    HAZARD_TOKENS.add(a)
    HAZARD_TOKENS.add(b)


def load_transcription():
    """Load and parse the interlinear transcription."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    tokens = []
    sections = []
    folios = []
    line_positions = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                word = parts[0].strip('"')
                folio = parts[2].strip('"')
                section = parts[3].strip('"')

                if word and not word.startswith('*'):
                    tokens.append(word)
                    folios.append(folio)
                    sections.append(section)

                    try:
                        line_pos = int(parts[11].strip('"')) if len(parts) > 11 else 0
                        is_line_initial = (parts[13].strip('"') == '1') if len(parts) > 13 else False
                        line_positions.append((line_pos, is_line_initial))
                    except:
                        line_positions.append((0, False))

    return tokens, sections, folios, line_positions


def is_residue_token(token: str) -> bool:
    """Check if token is residue (not grammar)."""
    t_lower = token.lower()
    is_grammar = (
        t_lower in GRAMMAR_TOKENS or
        t_lower.startswith('qo') or
        t_lower.startswith('ch') or
        t_lower.startswith('sh') or
        t_lower.endswith('aiin') or
        t_lower.endswith('dy') or
        t_lower.endswith('ol') or
        t_lower.endswith('or') or
        t_lower.endswith('ar') or
        t_lower.endswith('ain')
    )
    return not is_grammar


def compute_entropy(counter: Counter) -> float:
    """Compute Shannon entropy of a distribution."""
    total = sum(counter.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in counter.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return entropy


# =============================================================================
# SECTION FEATURE COMPUTATION
# =============================================================================

def compute_section_features(tokens: List[str], sections: List[str],
                            folios: List[str], line_positions: List[Tuple]) -> Dict:
    """Compute structural features for each section."""

    # Group data by section
    section_data = defaultdict(lambda: {
        'tokens': [],
        'residue_tokens': [],
        'folios': set(),
        'line_initial_count': 0,
        'total_count': 0
    })

    for i, (token, section, folio, (line_pos, is_initial)) in enumerate(
            zip(tokens, sections, folios, line_positions)):
        section_data[section]['tokens'].append(token)
        section_data[section]['folios'].add(folio)
        section_data[section]['total_count'] += 1
        if is_initial:
            section_data[section]['line_initial_count'] += 1

        if is_residue_token(token):
            section_data[section]['residue_tokens'].append(token)

    # Compute features per section
    features = {}
    all_residue_types = set()

    for section, data in section_data.items():
        residue_tokens = data['residue_tokens']
        all_residue_types.update(t.lower() for t in residue_tokens)

    for section, data in section_data.items():
        residue_tokens = data['residue_tokens']
        all_tokens = data['tokens']

        if not residue_tokens:
            continue

        # Feature 1: Residue token density
        residue_density = len(residue_tokens) / len(all_tokens) if all_tokens else 0

        # Feature 2: Section-exclusive vocabulary fraction
        residue_types = set(t.lower() for t in residue_tokens)
        other_section_types = set()
        for other_section, other_data in section_data.items():
            if other_section != section:
                other_section_types.update(t.lower() for t in other_data['residue_tokens'])

        exclusive_types = residue_types - other_section_types
        exclusive_fraction = len(exclusive_types) / len(residue_types) if residue_types else 0

        # Feature 3 & 4: Prefix and suffix entropy
        prefixes = Counter(t[:2].lower() for t in residue_tokens if len(t) >= 2)
        suffixes = Counter(t[-2:].lower() for t in residue_tokens if len(t) >= 2)
        prefix_entropy = compute_entropy(prefixes)
        suffix_entropy = compute_entropy(suffixes)

        # Feature 5: Mean hazard distance
        hazard_positions = []
        for i, t in enumerate(all_tokens):
            if t.lower() in HAZARD_TOKENS:
                hazard_positions.append(i)

        distances = []
        for i, t in enumerate(all_tokens):
            if is_residue_token(t) and hazard_positions:
                min_dist = min(abs(i - hp) for hp in hazard_positions)
                distances.append(min_dist)

        mean_hazard_distance = np.mean(distances) if distances else 10.0

        # Feature 6: Residue repetition rate
        residue_counter = Counter(t.lower() for t in residue_tokens)
        repeated_tokens = sum(1 for c in residue_counter.values() if c > 1)
        repetition_rate = repeated_tokens / len(residue_counter) if residue_counter else 0

        # Feature 7: Local bigram entropy
        bigrams = Counter()
        for t in residue_tokens:
            t_lower = t.lower()
            for i in range(len(t_lower) - 1):
                bigrams[t_lower[i:i+2]] += 1
        bigram_entropy = compute_entropy(bigrams)

        # Feature 8: Morphological type diversity (type-token ratio)
        type_token_ratio = len(residue_types) / len(residue_tokens) if residue_tokens else 0

        features[section] = {
            'residue_density': residue_density,
            'exclusive_fraction': exclusive_fraction,
            'prefix_entropy': prefix_entropy,
            'suffix_entropy': suffix_entropy,
            'mean_hazard_distance': mean_hazard_distance,
            'repetition_rate': repetition_rate,
            'bigram_entropy': bigram_entropy,
            'type_token_ratio': type_token_ratio,
            'n_residue_tokens': len(residue_tokens),
            'n_residue_types': len(residue_types),
            'n_folios': len(data['folios'])
        }

    return features


# =============================================================================
# CLUSTERING METHODS
# =============================================================================

def prepare_feature_matrix(features: Dict) -> Tuple[np.ndarray, List[str], List[str]]:
    """Convert feature dict to numpy matrix."""
    sections = sorted(features.keys())
    feature_names = [
        'residue_density', 'exclusive_fraction', 'prefix_entropy',
        'suffix_entropy', 'mean_hazard_distance', 'repetition_rate',
        'bigram_entropy', 'type_token_ratio'
    ]

    X = np.array([
        [features[s][f] for f in feature_names]
        for s in sections
    ])

    return X, sections, feature_names


def run_clustering_analysis(X: np.ndarray, sections: List[str],
                           max_k: int = 10) -> Dict:
    """Run clustering methods A, B, C."""

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    n_sections = len(sections)
    max_k = min(max_k, n_sections - 1)

    results = {
        'kmeans': {},
        'hierarchical': {},
        'spectral': {},
        'stability': {},
        'best_k': None,
        'best_method': None
    }

    # Method A: Run clustering for k = 2 to max_k
    for k in range(2, max_k + 1):
        # K-Means
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        km_labels = kmeans.fit_predict(X_scaled)
        km_silhouette = silhouette_score(X_scaled, km_labels) if k < n_sections else 0
        results['kmeans'][k] = {
            'labels': km_labels.tolist(),
            'silhouette': km_silhouette,
            'inertia': kmeans.inertia_
        }

        # Hierarchical
        hier = AgglomerativeClustering(n_clusters=k)
        hier_labels = hier.fit_predict(X_scaled)
        hier_silhouette = silhouette_score(X_scaled, hier_labels) if k < n_sections else 0
        results['hierarchical'][k] = {
            'labels': hier_labels.tolist(),
            'silhouette': hier_silhouette
        }

        # Spectral (only if k <= n_sections - 1)
        if k < n_sections:
            try:
                spec = SpectralClustering(n_clusters=k, random_state=42,
                                         affinity='nearest_neighbors', n_neighbors=min(3, n_sections-1))
                spec_labels = spec.fit_predict(X_scaled)
                spec_silhouette = silhouette_score(X_scaled, spec_labels)
                results['spectral'][k] = {
                    'labels': spec_labels.tolist(),
                    'silhouette': spec_silhouette
                }
            except:
                results['spectral'][k] = {'labels': [], 'silhouette': 0}

    # Stability analysis under resampling
    n_bootstrap = 50
    for k in range(2, max_k + 1):
        stability_scores = []
        for _ in range(n_bootstrap):
            # Bootstrap sample
            indices = np.random.choice(n_sections, n_sections, replace=True)
            X_boot = X_scaled[indices]

            if len(np.unique(indices)) >= k:
                try:
                    kmeans = KMeans(n_clusters=k, random_state=None, n_init=5)
                    labels = kmeans.fit_predict(X_boot)
                    if len(np.unique(labels)) >= 2:
                        stability_scores.append(silhouette_score(X_boot, labels))
                except:
                    pass

        results['stability'][k] = {
            'mean': np.mean(stability_scores) if stability_scores else 0,
            'std': np.std(stability_scores) if stability_scores else 1
        }

    # Find best k (Method B: minimum k explaining >= 80% variance)
    # Using elbow method approximation
    if results['kmeans']:
        inertias = [results['kmeans'][k]['inertia'] for k in sorted(results['kmeans'].keys())]
        if inertias:
            total_var = inertias[0]
            explained_vars = [(total_var - inertias[i]) / total_var for i in range(len(inertias))]

            best_k = 2
            for i, (k, ev) in enumerate(zip(sorted(results['kmeans'].keys()), explained_vars)):
                if ev >= 0.8:
                    best_k = k
                    break

            # Also consider silhouette
            best_silhouette = 0
            best_silhouette_k = 2
            for k, data in results['kmeans'].items():
                if data['silhouette'] > best_silhouette:
                    best_silhouette = data['silhouette']
                    best_silhouette_k = k

            results['best_k'] = best_k
            results['best_silhouette_k'] = best_silhouette_k

    return results


def run_predictive_comparison(features: Dict, clustering_results: Dict,
                             tokens: List[str], sections: List[str]) -> Dict:
    """Method C: Compare predictive power of regime-ID vs section-ID."""

    X, section_list, feature_names = prepare_feature_matrix(features)

    if len(section_list) < 3:
        return {'error': 'Too few sections for meaningful comparison'}

    # Create target vectors from residue statistics
    # We predict residue features from section/cluster identity

    # Build per-token dataset
    token_features = []
    token_sections = []
    token_residue = []

    section_to_idx = {s: i for i, s in enumerate(section_list)}

    for token, section in zip(tokens, sections):
        if section in section_to_idx and is_residue_token(token):
            token_sections.append(section_to_idx[section])
            token_residue.append(len(token))  # Use token length as simple target
            token_features.append([
                len(token),
                1 if token[0].lower() in 'aeiou' else 0,
                sum(1 for c in token.lower() if c in 'aeiou')
            ])

    if len(token_features) < 100:
        return {'error': 'Insufficient data for predictive test'}

    X_tokens = np.array(token_features)
    y_sections = np.array(token_sections)

    results = {}

    # Get best clustering
    best_k = clustering_results.get('best_silhouette_k', 3)
    if best_k in clustering_results.get('kmeans', {}):
        cluster_labels = clustering_results['kmeans'][best_k]['labels']

        # Map sections to clusters
        section_to_cluster = {section_list[i]: cluster_labels[i] for i in range(len(section_list))}
        y_clusters = np.array([section_to_cluster.get(sections[i], 0)
                              for i, (token, section) in enumerate(zip(tokens, sections))
                              if section in section_to_idx and is_residue_token(token)])

        # Cross-validation comparison
        if len(np.unique(y_sections)) >= 2 and len(np.unique(y_clusters)) >= 2:
            cv = StratifiedKFold(n_splits=min(5, len(np.unique(y_sections))), shuffle=True, random_state=42)

            # Section-ID classifier
            try:
                clf_section = LogisticRegression(max_iter=1000, random_state=42)
                scores_section = cross_val_score(clf_section, X_tokens, y_sections, cv=cv, scoring='accuracy')
                results['section_accuracy'] = np.mean(scores_section)
                results['section_std'] = np.std(scores_section)
            except:
                results['section_accuracy'] = 0
                results['section_std'] = 1

            # Cluster-ID classifier
            try:
                clf_cluster = LogisticRegression(max_iter=1000, random_state=42)
                scores_cluster = cross_val_score(clf_cluster, X_tokens, y_clusters, cv=cv, scoring='accuracy')
                results['cluster_accuracy'] = np.mean(scores_cluster)
                results['cluster_std'] = np.std(scores_cluster)
            except:
                results['cluster_accuracy'] = 0
                results['cluster_std'] = 1

            # Comparison
            results['compression_effective'] = results['cluster_accuracy'] >= results['section_accuracy'] * 0.95
            results['best_k'] = best_k

    return results


# =============================================================================
# VERDICT GENERATION
# =============================================================================

def generate_verdict(features: Dict, clustering: Dict, predictive: Dict) -> Dict:
    """Generate SID-01.1 verdict."""

    verdict = {
        'section_count': len(features),
        'features_used': 8,
        'clustering_summary': {},
        'regime_descriptions': [],
        'reducibility': None,
        'final_verdict': None
    }

    # Summarize clustering results
    if 'kmeans' in clustering:
        best_k = clustering.get('best_silhouette_k', 2)
        best_silhouette = clustering['kmeans'].get(best_k, {}).get('silhouette', 0)

        verdict['clustering_summary'] = {
            'best_k': best_k,
            'best_silhouette': best_silhouette,
            'stability': clustering.get('stability', {}).get(best_k, {})
        }

        # Check hard failure conditions
        n_sections = len(features)

        # Failure 1: k ~= N (every section is its own cluster)
        if best_k >= n_sections - 1:
            verdict['reducibility'] = 'FAILURE_NO_COMPRESSION'
            verdict['final_verdict'] = 'SECTIONS_IRREDUCIBLE'
            verdict['failure_reason'] = 'Optimal k equals section count - no compression'
            return verdict

        # Failure 2: Low silhouette (weak clustering)
        if best_silhouette < 0.25:
            verdict['reducibility'] = 'FAILURE_WEAK_CLUSTERING'
            verdict['final_verdict'] = 'WEAK_STRUCTURE_ONLY'
            verdict['failure_reason'] = f'Silhouette score {best_silhouette:.3f} below threshold 0.25'
            return verdict

        # Failure 3: Unstable under resampling
        stability = clustering.get('stability', {}).get(best_k, {})
        if stability.get('std', 1) > 0.15:
            verdict['reducibility'] = 'FAILURE_UNSTABLE'
            verdict['final_verdict'] = 'WEAK_STRUCTURE_ONLY'
            verdict['failure_reason'] = f'Clustering unstable (std={stability.get("std", 1):.3f})'
            return verdict

        # Check predictive comparison
        if 'compression_effective' in predictive:
            if not predictive['compression_effective']:
                verdict['reducibility'] = 'PARTIAL_REDUCTION'
                verdict['final_verdict'] = 'WEAK_STRUCTURE_ONLY'
                verdict['failure_reason'] = 'Cluster-ID does not match section-ID predictive power'
                return verdict

        # If we get here, clustering has succeeded
        if best_k <= 5 and best_silhouette >= 0.4:
            verdict['reducibility'] = 'FULL_REDUCTION'
            verdict['final_verdict'] = 'REGIMES_EXIST'
        elif best_k <= 5:
            verdict['reducibility'] = 'PARTIAL_REDUCTION'
            verdict['final_verdict'] = 'WEAK_STRUCTURE_ONLY'
        else:
            verdict['reducibility'] = 'MINIMAL_REDUCTION'
            verdict['final_verdict'] = 'WEAK_STRUCTURE_ONLY'

    return verdict


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 70)
    print("SID-01.1: SECTION REGIME CLUSTERING TEST")
    print("=" * 70)
    print()

    # Load data
    print("Loading transcription data...")
    tokens, sections, folios, line_positions = load_transcription()
    print(f"  Loaded {len(tokens)} tokens across {len(set(sections))} sections")

    # Compute section features
    print("\nComputing section features...")
    features = compute_section_features(tokens, sections, folios, line_positions)
    print(f"  Computed features for {len(features)} sections")

    # Print feature summary (Section A)
    print("\n" + "=" * 70)
    print("SECTION A: FEATURE SUMMARY")
    print("=" * 70)

    X, section_list, feature_names = prepare_feature_matrix(features)

    print("\nFeatures computed per section:")
    for i, f in enumerate(feature_names):
        print(f"  {i+1}. {f}")

    print("\nSection feature values:")
    print(f"{'Section':<10} {'Density':<10} {'Exclusive':<10} {'PfxEnt':<10} {'SfxEnt':<10} {'HazDist':<10} {'RepRate':<10} {'BigramEnt':<10} {'TTR':<10}")
    print("-" * 90)
    for section in section_list:
        f = features[section]
        print(f"{section:<10} {f['residue_density']:.3f}      {f['exclusive_fraction']:.3f}      {f['prefix_entropy']:.3f}      {f['suffix_entropy']:.3f}      {f['mean_hazard_distance']:.2f}       {f['repetition_rate']:.3f}      {f['bigram_entropy']:.3f}      {f['type_token_ratio']:.3f}")

    # Run clustering (Section B)
    print("\n" + "=" * 70)
    print("SECTION B: CLUSTERING RESULTS")
    print("=" * 70)

    clustering = run_clustering_analysis(X, section_list)

    print("\nK-Means clustering results:")
    print(f"{'k':<5} {'Silhouette':<12} {'Stability Mean':<15} {'Stability Std':<15}")
    print("-" * 50)
    for k in sorted(clustering['kmeans'].keys()):
        sil = clustering['kmeans'][k]['silhouette']
        stab = clustering['stability'].get(k, {})
        print(f"{k:<5} {sil:<12.3f} {stab.get('mean', 0):<15.3f} {stab.get('std', 0):<15.3f}")

    print(f"\nBest k (by silhouette): {clustering.get('best_silhouette_k', 'N/A')}")
    print(f"Best k (by variance): {clustering.get('best_k', 'N/A')}")

    # Regime descriptions (Section C)
    print("\n" + "=" * 70)
    print("SECTION C: REGIME DESCRIPTIONS")
    print("=" * 70)

    best_k = clustering.get('best_silhouette_k', 3)
    if best_k in clustering['kmeans']:
        labels = clustering['kmeans'][best_k]['labels']

        for regime in range(best_k):
            regime_sections = [section_list[i] for i in range(len(section_list)) if labels[i] == regime]
            print(f"\nREGIME_{regime}:")
            print(f"  Sections: {', '.join(regime_sections)}")
            print(f"  Count: {len(regime_sections)}")

            # Compute regime means
            regime_features = [features[s] for s in regime_sections]
            if regime_features:
                mean_density = np.mean([f['residue_density'] for f in regime_features])
                mean_exclusive = np.mean([f['exclusive_fraction'] for f in regime_features])
                mean_hazard = np.mean([f['mean_hazard_distance'] for f in regime_features])
                print(f"  Mean residue density: {mean_density:.3f}")
                print(f"  Mean exclusive fraction: {mean_exclusive:.3f}")
                print(f"  Mean hazard distance: {mean_hazard:.2f}")

    # Predictive comparison (Section D)
    print("\n" + "=" * 70)
    print("SECTION D: PREDICTIVE COMPARISON")
    print("=" * 70)

    predictive = run_predictive_comparison(features, clustering, tokens, sections)

    if 'error' in predictive:
        print(f"\n  {predictive['error']}")
    else:
        print(f"\n  Section-ID accuracy: {predictive.get('section_accuracy', 0):.3f} (+/- {predictive.get('section_std', 0):.3f})")
        print(f"  Cluster-ID accuracy: {predictive.get('cluster_accuracy', 0):.3f} (+/- {predictive.get('cluster_std', 0):.3f})")
        print(f"  Compression effective: {predictive.get('compression_effective', False)}")

    # Reducibility assessment (Section E)
    print("\n" + "=" * 70)
    print("SECTION E: REDUCIBILITY ASSESSMENT")
    print("=" * 70)

    verdict = generate_verdict(features, clustering, predictive)

    print(f"\n  Section count: {verdict['section_count']}")
    print(f"  Best k: {verdict['clustering_summary'].get('best_k', 'N/A')}")
    print(f"  Reducibility: {verdict['reducibility']}")
    if 'failure_reason' in verdict:
        print(f"  Reason: {verdict['failure_reason']}")

    # Final verdict (Section F)
    print("\n" + "=" * 70)
    print("SECTION F: SID-01.1 VERDICT")
    print("=" * 70)

    verdict_map = {
        'REGIMES_EXIST': 'REGIMES EXIST (k <= 5, stable)',
        'WEAK_STRUCTURE_ONLY': 'WEAK STRUCTURE ONLY',
        'SECTIONS_IRREDUCIBLE': 'SECTIONS ARE IRREDUCIBLE'
    }

    print(f"""
+-----------------------------------------------------------------------+
|                                                                       |
|   {verdict_map.get(verdict['final_verdict'], verdict['final_verdict']):<65} |
|                                                                       |
+-----------------------------------------------------------------------+
""")

    if verdict['final_verdict'] == 'REGIMES_EXIST':
        print("Section identity CAN be compressed into a smaller set of regimes.")
        print(f"Optimal regime count: {verdict['clustering_summary'].get('best_k', 'N/A')}")
    elif verdict['final_verdict'] == 'WEAK_STRUCTURE_ONLY':
        print("Partial structure detected, but not sufficient for reliable compression.")
        print("Section identity remains the primary conditioning variable.")
    else:
        print("No compression achievable. Each section behaves idiosyncratically.")
        print("Section identity is IRREDUCIBLE.")

    # Write verdict to file
    output_path = r'C:\git\voynich\phases\SID01_global_residue_convergence\SID01_1_verdict.md'
    write_verdict_report(verdict, features, clustering, predictive, output_path)
    print(f"\nVerdict written to: {output_path}")

    return verdict


def write_verdict_report(verdict: Dict, features: Dict, clustering: Dict,
                        predictive: Dict, output_path: str):
    """Write formal verdict report to markdown file."""

    X, section_list, feature_names = prepare_feature_matrix(features)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# SID-01.1: Section Regime Clustering Test -- VERDICT\n\n")
        f.write("**Status:** COMPLETE\n")
        f.write("**Date:** 2026-01-05\n")
        f.write("**Test ID:** SID-01.1\n")
        f.write("**Parent Test:** SID-01 (Global Residue Convergence)\n")
        f.write("**Objective Class:** Conditional structure reduction\n\n")
        f.write("---\n\n")

        # Section A
        f.write("## SECTION A: FEATURE SUMMARY\n\n")
        f.write("| # | Feature | Description |\n")
        f.write("|---|---------|-------------|\n")
        for i, fn in enumerate(feature_names):
            desc = {
                'residue_density': 'Fraction of tokens that are residue',
                'exclusive_fraction': 'Fraction of residue types unique to this section',
                'prefix_entropy': 'Shannon entropy of 2-char prefixes',
                'suffix_entropy': 'Shannon entropy of 2-char suffixes',
                'mean_hazard_distance': 'Mean distance to nearest hazard token',
                'repetition_rate': 'Fraction of types appearing >1 time',
                'bigram_entropy': 'Shannon entropy of character bigrams',
                'type_token_ratio': 'Vocabulary diversity (types/tokens)'
            }.get(fn, fn)
            f.write(f"| {i+1} | {fn} | {desc} |\n")
        f.write("\n")

        f.write("### Section Feature Values\n\n")
        f.write("| Section | Density | Exclusive | PfxEnt | SfxEnt | HazDist | RepRate | BigramEnt | TTR |\n")
        f.write("|---------|---------|-----------|--------|--------|---------|---------|-----------|-----|\n")
        for section in section_list:
            feat = features[section]
            f.write(f"| {section} | {feat['residue_density']:.3f} | {feat['exclusive_fraction']:.3f} | ")
            f.write(f"{feat['prefix_entropy']:.3f} | {feat['suffix_entropy']:.3f} | {feat['mean_hazard_distance']:.2f} | ")
            f.write(f"{feat['repetition_rate']:.3f} | {feat['bigram_entropy']:.3f} | {feat['type_token_ratio']:.3f} |\n")
        f.write("\n---\n\n")

        # Section B
        f.write("## SECTION B: CLUSTERING RESULTS\n\n")
        f.write("### K-Means Results\n\n")
        f.write("| k | Silhouette | Stability Mean | Stability Std |\n")
        f.write("|---|------------|----------------|---------------|\n")
        for k in sorted(clustering['kmeans'].keys()):
            sil = clustering['kmeans'][k]['silhouette']
            stab = clustering['stability'].get(k, {})
            f.write(f"| {k} | {sil:.3f} | {stab.get('mean', 0):.3f} | {stab.get('std', 0):.3f} |\n")
        f.write(f"\n**Best k (silhouette):** {clustering.get('best_silhouette_k', 'N/A')}\n")
        f.write(f"**Best k (variance):** {clustering.get('best_k', 'N/A')}\n\n")
        f.write("---\n\n")

        # Section C
        f.write("## SECTION C: REGIME DESCRIPTIONS\n\n")
        best_k = clustering.get('best_silhouette_k', 3)
        if best_k in clustering['kmeans']:
            labels = clustering['kmeans'][best_k]['labels']
            for regime in range(best_k):
                regime_sections = [section_list[i] for i in range(len(section_list)) if labels[i] == regime]
                f.write(f"### REGIME_{regime}\n\n")
                f.write(f"- **Sections:** {', '.join(regime_sections)}\n")
                f.write(f"- **Count:** {len(regime_sections)}\n")

                regime_features = [features[s] for s in regime_sections]
                if regime_features:
                    f.write(f"- **Mean residue density:** {np.mean([feat['residue_density'] for feat in regime_features]):.3f}\n")
                    f.write(f"- **Mean exclusive fraction:** {np.mean([feat['exclusive_fraction'] for feat in regime_features]):.3f}\n")
                    f.write(f"- **Mean hazard distance:** {np.mean([feat['mean_hazard_distance'] for feat in regime_features]):.2f}\n")
                f.write("\n")
        f.write("---\n\n")

        # Section D
        f.write("## SECTION D: PREDICTIVE COMPARISON\n\n")
        if 'error' in predictive:
            f.write(f"**Error:** {predictive['error']}\n\n")
        else:
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Section-ID accuracy | {predictive.get('section_accuracy', 0):.3f} (+/- {predictive.get('section_std', 0):.3f}) |\n")
            f.write(f"| Cluster-ID accuracy | {predictive.get('cluster_accuracy', 0):.3f} (+/- {predictive.get('cluster_std', 0):.3f}) |\n")
            f.write(f"| Compression effective | {predictive.get('compression_effective', False)} |\n")
        f.write("\n---\n\n")

        # Section E
        f.write("## SECTION E: REDUCIBILITY ASSESSMENT\n\n")
        f.write(f"- **Section count:** {verdict['section_count']}\n")
        f.write(f"- **Best k:** {verdict['clustering_summary'].get('best_k', 'N/A')}\n")
        f.write(f"- **Best silhouette:** {verdict['clustering_summary'].get('best_silhouette', 'N/A'):.3f}\n")
        f.write(f"- **Reducibility:** {verdict['reducibility']}\n")
        if 'failure_reason' in verdict:
            f.write(f"- **Reason:** {verdict['failure_reason']}\n")
        f.write("\n---\n\n")

        # Section F
        f.write("## SECTION F: SID-01.1 VERDICT\n\n")
        f.write("```\n")
        verdict_text = {
            'REGIMES_EXIST': 'REGIMES EXIST (k <= 5, stable)',
            'WEAK_STRUCTURE_ONLY': 'WEAK STRUCTURE ONLY',
            'SECTIONS_IRREDUCIBLE': 'SECTIONS ARE IRREDUCIBLE'
        }.get(verdict['final_verdict'], verdict['final_verdict'])
        f.write(f"+-----------------------------------------------------------------------+\n")
        f.write(f"|                                                                       |\n")
        f.write(f"|   {verdict_text:<65} |\n")
        f.write(f"|                                                                       |\n")
        f.write(f"+-----------------------------------------------------------------------+\n")
        f.write("```\n\n")

        if verdict['final_verdict'] == 'REGIMES_EXIST':
            f.write("Section identity CAN be compressed into a smaller set of regimes.\n")
        elif verdict['final_verdict'] == 'WEAK_STRUCTURE_ONLY':
            f.write("Partial structure detected, but not sufficient for reliable compression.\n")
            f.write("Section identity remains the primary conditioning variable.\n")
        else:
            f.write("No compression achievable. Each section behaves idiosyncratically.\n")
            f.write("Section identity is IRREDUCIBLE.\n")

        f.write("\n---\n\n")
        f.write("*SID-01.1 Complete.*\n")


if __name__ == '__main__':
    main()
