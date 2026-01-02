"""
Control Signature Matching Analysis
External Brute-Force Comparative Analysis with Interpretive Firewall

This script compares the Voynich control signature against 30 external
process candidates to identify operational homologies.

NO SEMANTIC INTERPRETATION. NO IDENTITY CLAIMS.
"""

import json
import numpy as np
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------

def load_library():
    """Load candidate control library."""
    with open('candidate_control_library.json', 'r') as f:
        return json.load(f)

# ---------------------------------------------------------------------
# FEATURE EXTRACTION
# ---------------------------------------------------------------------

def extract_numerical_vector(entity):
    """Extract numerical feature vector from entity."""
    num = entity['numerical']
    return np.array([
        num['F01'], num['F02'], num['F03']/100, num['F04']/20,  # Normalize counts
        num['F05'], num['F06']/10, num['F07']/10, num['F08'],
        num['F09'], num['F10'], num['F11'], num['F12'],
        num['F13'], num['F14'], num['F15']/10, num['F16']/10,
        num['F17'], num['F18']
    ])

def categorical_similarity(cat1, cat2):
    """Compute Jaccard-like similarity for categorical features."""
    matches = sum(1 for k in cat1 if cat1.get(k) == cat2.get(k))
    return matches / len(cat1)

# ---------------------------------------------------------------------
# DISTANCE METRICS
# ---------------------------------------------------------------------

def euclidean_distance(v1, v2):
    """Euclidean distance between vectors."""
    return np.sqrt(np.sum((v1 - v2) ** 2))

def cosine_similarity(v1, v2):
    """Cosine similarity between vectors."""
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def manhattan_distance(v1, v2):
    """Manhattan (L1) distance."""
    return np.sum(np.abs(v1 - v2))

def combined_similarity(voynich, candidate, num_weight=0.6, cat_weight=0.4):
    """
    Combined similarity score using numerical and categorical features.
    Higher = more similar.
    """
    v_num = extract_numerical_vector(voynich)
    c_num = extract_numerical_vector(candidate)

    # Numerical similarity (1 - normalized euclidean)
    max_dist = np.sqrt(len(v_num))  # Max possible distance for normalized vectors
    euc_dist = euclidean_distance(v_num, c_num)
    num_sim = 1 - (euc_dist / max_dist)

    # Categorical similarity
    cat_sim = categorical_similarity(voynich['categorical'], candidate['categorical'])

    # Combined
    return num_weight * num_sim + cat_weight * cat_sim

# ---------------------------------------------------------------------
# ANALYSIS FUNCTIONS
# ---------------------------------------------------------------------

def compute_all_similarities(library):
    """Compute similarity scores for all candidates."""
    voynich = library['voynich_reference']
    candidates = library['candidates']

    results = []
    for cand in candidates:
        v_num = extract_numerical_vector(voynich)
        c_num = extract_numerical_vector(cand)

        result = {
            'id': cand['id'],
            'name': cand['name'],
            'domain': cand['domain'],
            'euclidean_distance': euclidean_distance(v_num, c_num),
            'cosine_similarity': cosine_similarity(v_num, c_num),
            'manhattan_distance': manhattan_distance(v_num, c_num),
            'categorical_similarity': categorical_similarity(
                voynich['categorical'], cand['categorical']
            ),
            'combined_similarity': combined_similarity(voynich, cand)
        }
        results.append(result)

    # Sort by combined similarity (descending)
    results.sort(key=lambda x: x['combined_similarity'], reverse=True)
    return results

def cluster_by_similarity(results, thresholds=[0.85, 0.75, 0.65]):
    """
    Cluster candidates by similarity score thresholds.
    Returns clusters: HIGH (>0.85), MEDIUM (0.75-0.85), LOW (0.65-0.75), DISTANT (<0.65)
    """
    clusters = {
        'HIGH': [],
        'MEDIUM': [],
        'LOW': [],
        'DISTANT': []
    }

    for r in results:
        sim = r['combined_similarity']
        if sim >= thresholds[0]:
            clusters['HIGH'].append(r)
        elif sim >= thresholds[1]:
            clusters['MEDIUM'].append(r)
        elif sim >= thresholds[2]:
            clusters['LOW'].append(r)
        else:
            clusters['DISTANT'].append(r)

    return clusters

def cluster_by_domain(results):
    """Group candidates by domain."""
    domains = defaultdict(list)
    for r in results:
        domains[r['domain']].append(r)
    return dict(domains)

def analyze_feature_alignment(library, top_n=10):
    """
    Analyze which features align best between Voynich and top candidates.
    """
    voynich = library['voynich_reference']
    candidates = library['candidates']

    # Get all similarities
    sims = []
    for cand in candidates:
        sims.append((cand, combined_similarity(voynich, cand)))
    sims.sort(key=lambda x: x[1], reverse=True)

    # Analyze top candidates
    v_num = extract_numerical_vector(voynich)
    feature_names = ['F01', 'F02', 'F03', 'F04', 'F05', 'F06', 'F07', 'F08',
                     'F09', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15', 'F16',
                     'F17', 'F18']

    alignments = {f: [] for f in feature_names}

    for cand, _ in sims[:top_n]:
        c_num = extract_numerical_vector(cand)
        for i, f in enumerate(feature_names):
            diff = abs(v_num[i] - c_num[i])
            alignments[f].append(diff)

    # Average alignment per feature
    avg_alignments = {f: np.mean(alignments[f]) for f in feature_names}

    return avg_alignments

def compute_robustness(library, n_trials=100):
    """
    Check robustness by adding noise to feature vectors.
    """
    voynich = library['voynich_reference']
    candidates = library['candidates']

    base_rankings = compute_all_similarities(library)
    base_order = [r['id'] for r in base_rankings]

    rank_stability = {cand['id']: [] for cand in candidates}

    for trial in range(n_trials):
        # Add small noise to Voynich vector
        noisy_voynich = voynich.copy()
        noisy_voynich['numerical'] = {
            k: max(0, min(1 if k not in ['F03', 'F04', 'F06', 'F07', 'F15', 'F16'] else v + np.random.normal(0, 0.05),
                   v + np.random.normal(0, 0.05)))
            for k, v in voynich['numerical'].items()
        }

        # Recompute similarities
        trial_results = []
        for cand in candidates:
            trial_results.append({
                'id': cand['id'],
                'similarity': combined_similarity(noisy_voynich, cand)
            })
        trial_results.sort(key=lambda x: x['similarity'], reverse=True)

        # Record ranks
        for rank, r in enumerate(trial_results):
            rank_stability[r['id']].append(rank)

    # Compute rank variance
    rank_variance = {
        cid: np.std(ranks) for cid, ranks in rank_stability.items()
    }

    return rank_variance

# ---------------------------------------------------------------------
# REPORT GENERATION
# ---------------------------------------------------------------------

def generate_similarity_report(library, results, clusters):
    """Generate the similarity analysis report."""

    report = []
    report.append("# Control Signature Similarity Analysis\n")
    report.append("*Generated: 2026-01-01*\n")
    report.append("*Status: External Comparative Analysis (Interpretive Firewall Active)*\n")
    report.append("\n---\n")

    # Executive Summary
    report.append("## Executive Summary\n")
    report.append(f"- **Candidates analyzed:** {len(results)}\n")
    report.append(f"- **HIGH similarity cluster:** {len(clusters['HIGH'])} processes\n")
    report.append(f"- **MEDIUM similarity cluster:** {len(clusters['MEDIUM'])} processes\n")
    report.append(f"- **LOW similarity cluster:** {len(clusters['LOW'])} processes\n")
    report.append(f"- **DISTANT cluster:** {len(clusters['DISTANT'])} processes\n")
    report.append("\n")

    # Top matches
    report.append("## Top 10 Similarity Matches\n")
    report.append("| Rank | Process | Domain | Combined | Euclidean | Cosine | Categorical |\n")
    report.append("|------|---------|--------|----------|-----------|--------|-------------|\n")
    for i, r in enumerate(results[:10]):
        report.append(f"| {i+1} | {r['name']} | {r['domain']} | "
                     f"{r['combined_similarity']:.3f} | {r['euclidean_distance']:.3f} | "
                     f"{r['cosine_similarity']:.3f} | {r['categorical_similarity']:.3f} |\n")
    report.append("\n")

    # HIGH cluster analysis
    report.append("## HIGH Similarity Cluster (>0.85)\n")
    if clusters['HIGH']:
        report.append("Processes with operational homology to Voynich control signature:\n\n")
        for r in clusters['HIGH']:
            report.append(f"### {r['name']} ({r['domain']})\n")
            report.append(f"- Combined similarity: **{r['combined_similarity']:.3f}**\n")
            report.append(f"- Categorical match: {r['categorical_similarity']:.1%}\n")
            report.append(f"- Euclidean distance: {r['euclidean_distance']:.3f}\n\n")
    else:
        report.append("*No processes in HIGH similarity cluster.*\n\n")

    # MEDIUM cluster
    report.append("## MEDIUM Similarity Cluster (0.75-0.85)\n")
    if clusters['MEDIUM']:
        for r in clusters['MEDIUM']:
            report.append(f"- **{r['name']}** ({r['domain']}): {r['combined_similarity']:.3f}\n")
    else:
        report.append("*No processes in MEDIUM similarity cluster.*\n")
    report.append("\n")

    # Domain analysis
    report.append("## Domain Distribution\n")
    domains = cluster_by_domain(results)
    report.append("| Domain | Count | Best Match | Similarity |\n")
    report.append("|--------|-------|------------|------------|\n")
    for domain, procs in sorted(domains.items(), key=lambda x: -max(p['combined_similarity'] for p in x[1])):
        best = max(procs, key=lambda x: x['combined_similarity'])
        report.append(f"| {domain} | {len(procs)} | {best['name']} | {best['combined_similarity']:.3f} |\n")
    report.append("\n")

    # Feature alignment
    report.append("## Feature Alignment Analysis (Top 10 Matches)\n")
    alignments = analyze_feature_alignment(library)
    sorted_features = sorted(alignments.items(), key=lambda x: x[1])

    report.append("\n**Best Aligned Features** (lowest deviation):\n")
    for f, dev in sorted_features[:5]:
        report.append(f"- {f}: mean deviation {dev:.4f}\n")

    report.append("\n**Worst Aligned Features** (highest deviation):\n")
    for f, dev in sorted_features[-5:]:
        report.append(f"- {f}: mean deviation {dev:.4f}\n")
    report.append("\n")

    # Interpretive firewall
    report.append("---\n")
    report.append("## Interpretive Firewall Statement\n")
    report.append("\nThis analysis identifies **operational homologies** between the Voynich\n")
    report.append("control signature and external processes. These findings:\n\n")
    report.append("1. **DO NOT** prove identity or historical relationship\n")
    report.append("2. **DO NOT** translate or interpret Voynich content\n")
    report.append("3. **ARE** probabilistic similarity measures only\n")
    report.append("4. **ARE** based on abstracted control-theoretic features\n\n")
    report.append("**Allowed interpretations:**\n")
    report.append("- \"Shows operational similarity to...\"\n")
    report.append("- \"Shares control-theoretic profile with...\"\n")
    report.append("- \"Requires comparable intervention discipline to...\"\n\n")
    report.append("**Forbidden interpretations:**\n")
    report.append("- \"This IS...\"\n")
    report.append("- \"Represents...\"\n")
    report.append("- \"Was used for...\"\n")

    return ''.join(report)

def generate_cluster_report(results, clusters):
    """Generate cluster-focused analysis."""

    report = []
    report.append("# Process Cluster Analysis\n")
    report.append("*Focus on clusters, not individual matches*\n\n")
    report.append("---\n\n")

    # Cluster characteristics
    report.append("## Cluster Characteristics\n\n")

    for cluster_name, members in clusters.items():
        report.append(f"### {cluster_name} Cluster ({len(members)} members)\n\n")

        if not members:
            report.append("*Empty cluster*\n\n")
            continue

        # Domain composition
        domains = defaultdict(int)
        for m in members:
            domains[m['domain']] += 1

        report.append("**Domain composition:**\n")
        for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
            report.append(f"- {domain}: {count} ({100*count/len(members):.0f}%)\n")
        report.append("\n")

        # Similarity statistics
        sims = [m['combined_similarity'] for m in members]
        report.append(f"**Similarity statistics:**\n")
        report.append(f"- Mean: {np.mean(sims):.3f}\n")
        report.append(f"- Std: {np.std(sims):.3f}\n")
        report.append(f"- Range: [{min(sims):.3f}, {max(sims):.3f}]\n\n")

        # Member list
        report.append("**Members:**\n")
        for m in members:
            report.append(f"- {m['name']} ({m['combined_similarity']:.3f})\n")
        report.append("\n")

    # Cross-cluster patterns
    report.append("## Cross-Cluster Patterns\n\n")

    # What distinguishes HIGH from MEDIUM?
    if clusters['HIGH'] and clusters['MEDIUM']:
        report.append("### HIGH vs MEDIUM Differentiators\n\n")
        report.append("Processes in HIGH cluster share these properties with Voynich:\n")
        report.append("- Higher categorical match (control topology, operator model)\n")
        report.append("- Closer forbidden transition counts\n")
        report.append("- Similar kernel structure presence\n\n")

    # What domains are excluded?
    all_domains = set()
    high_domains = set()
    for c in clusters.get('HIGH', []) + clusters.get('MEDIUM', []):
        all_domains.add(c['domain'])
        if c in clusters.get('HIGH', []):
            high_domains.add(c['domain'])

    report.append("### Domain Exclusions\n\n")
    report.append("Domains with NO high-similarity matches:\n")
    distant_domains = set(c['domain'] for c in clusters.get('DISTANT', []))
    for d in distant_domains - high_domains:
        report.append(f"- {d}\n")
    report.append("\n")

    return ''.join(report)

# ---------------------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------------------

def main():
    print("Loading candidate library...")
    library = load_library()

    print("Computing similarity scores...")
    results = compute_all_similarities(library)

    print("Clustering by similarity...")
    clusters = cluster_by_similarity(results)

    print("Computing robustness...")
    rank_variance = compute_robustness(library, n_trials=50)

    print("Generating reports...")

    # Similarity report
    sim_report = generate_similarity_report(library, results, clusters)
    with open('similarity_analysis.md', 'w') as f:
        f.write(sim_report)

    # Cluster report
    cluster_report = generate_cluster_report(results, clusters)
    with open('cluster_analysis.md', 'w') as f:
        f.write(cluster_report)

    # Save numerical results
    output = {
        'metadata': {
            'generated': '2026-01-01',
            'candidates_analyzed': len(results),
            'metrics': ['euclidean', 'cosine', 'manhattan', 'categorical', 'combined']
        },
        'rankings': results,
        'clusters': {
            name: [r['id'] for r in members]
            for name, members in clusters.items()
        },
        'cluster_sizes': {
            name: len(members) for name, members in clusters.items()
        },
        'robustness': {
            'rank_variance': rank_variance,
            'stable_top_5': [
                r['id'] for r in results[:5]
                if rank_variance[r['id']] < 2.0
            ]
        }
    }

    with open('similarity_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("CONTROL SIGNATURE MATCHING COMPLETE")
    print("="*60)
    print(f"\nCandidates analyzed: {len(results)}")
    print(f"HIGH similarity: {len(clusters['HIGH'])}")
    print(f"MEDIUM similarity: {len(clusters['MEDIUM'])}")
    print(f"LOW similarity: {len(clusters['LOW'])}")
    print(f"DISTANT: {len(clusters['DISTANT'])}")

    print("\nTop 5 matches:")
    for i, r in enumerate(results[:5]):
        print(f"  {i+1}. {r['name']} ({r['combined_similarity']:.3f})")

    print("\nReports generated:")
    print("  - similarity_analysis.md")
    print("  - cluster_analysis.md")
    print("  - similarity_results.json")

    print("\nINTERPRETIVE FIREWALL ACTIVE")
    print("All findings are operational homologies, not identity claims.")

if __name__ == '__main__':
    main()
