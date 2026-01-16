"""
Full AZC Landscape Investigation.

Tests:
1. Map all 30 AZC folios by section
2. Analyze structural token coverage across full dataset
3. Re-test record boundaries with complete data

Refinements:
- CSP (Compatibility Survival Power) metric to distinguish universal vs polarizing tokens
- Trajectory logging for post-hoc validation of boundary detection
"""
from pathlib import Path
import sys
import json
import random
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps.azc_folio_animator.core.folio_loader import FolioLoader


def load_all_azc_folios():
    """Load ALL AZC folios (Z, A, C, H, S sections)."""
    results_dir = Path(__file__).parent.parent.parent / "results"
    features_path = results_dir / "azc_folio_features.json"

    with open(features_path) as f:
        data = json.load(f)

    folios_by_section = defaultdict(list)
    for folio_id, fdata in data.get('folios', {}).items():
        section = fdata.get('section', 'UNKNOWN')
        folios_by_section[section].append(folio_id)

    return folios_by_section, data


def build_token_to_folio_map(loader, all_folio_ids):
    """Build complete token -> folio mapping."""
    token_to_folios = defaultdict(set)
    folio_to_tokens = {}

    for folio_id in all_folio_ids:
        folio = loader.get_folio(folio_id.lstrip('f'))
        if not folio:
            continue

        tokens = set(t.text for t in folio.tokens)
        folio_to_tokens[folio_id] = tokens

        for token in tokens:
            token_to_folios[token].add(folio_id)

    return dict(token_to_folios), folio_to_tokens


def phase1_section_analysis(folios_by_section, token_to_folios, folio_to_tokens):
    """Phase 1: Analyze what each section contributes."""
    print("=" * 60)
    print("PHASE 1: Section Vocabulary Analysis")
    print("=" * 60)

    section_vocab = {}
    for section, folio_ids in folios_by_section.items():
        vocab = set()
        for fid in folio_ids:
            if fid in folio_to_tokens:
                vocab.update(folio_to_tokens[fid])
        section_vocab[section] = vocab
        print(f"\n{section}: {len(folio_ids)} folios, {len(vocab)} unique tokens")

    # Section overlap analysis
    print("\n--- Section Overlap (Jaccard) ---")
    sections = list(section_vocab.keys())
    for i, s1 in enumerate(sections):
        for s2 in sections[i+1:]:
            v1, v2 = section_vocab[s1], section_vocab[s2]
            inter = len(v1 & v2)
            union = len(v1 | v2)
            jaccard = inter / union if union > 0 else 0
            print(f"{s1} vs {s2}: {jaccard:.3f} ({inter} shared)")

    return section_vocab


def compute_csp(token, token_to_folios, all_tokens, n_samples=100):
    """
    Compute Compatibility Survival Power for a token.
    CSP = mean compatibility size when token is added to random bundles.
    """
    if token not in token_to_folios:
        return 0.0

    token_folios = token_to_folios[token]
    other_tokens = [t for t in all_tokens if t != token and t in token_to_folios]

    if len(other_tokens) < 3:
        return len(token_folios)  # Not enough tokens for meaningful CSP

    survival_sizes = []
    for _ in range(n_samples):
        # Random bundle of 2-5 other tokens
        bundle_size = random.randint(2, min(5, len(other_tokens)))
        bundle = random.sample(other_tokens, bundle_size)

        # Compute intersection WITH the target token
        folio_sets = [token_to_folios[t] for t in bundle if t in token_to_folios]
        folio_sets.append(token_folios)

        if folio_sets:
            intersection = set.intersection(*folio_sets)
            survival_sizes.append(len(intersection))

    return sum(survival_sizes) / len(survival_sizes) if survival_sizes else 0.0


def phase2_structural_tokens(token_to_folios, total_folios):
    """Phase 2: Analyze structural token coverage + CSP."""
    print("\n" + "=" * 60)
    print("PHASE 2: Structural Token Analysis")
    print("=" * 60)

    # Sort by coverage
    coverage = [(t, len(f)) for t, f in token_to_folios.items()]
    coverage.sort(key=lambda x: -x[1])
    all_tokens = [t for t, _ in coverage]

    print(f"\nTotal AZC folios: {total_folios}")
    print(f"\n--- Top 20 tokens by folio coverage ---")
    for token, count in coverage[:20]:
        pct = count / total_folios * 100
        folios = sorted(token_to_folios[token])
        print(f"{token:12} -> {count:2}/{total_folios} ({pct:5.1f}%): {folios[:6]}...")

    # Find truly universal tokens (80%+ coverage)
    universal = [(t, c) for t, c in coverage if c >= total_folios * 0.8]
    print(f"\n--- Universal tokens (80%+ = {int(total_folios*0.8)}+ folios) ---")
    print(f"Count: {len(universal)}")
    for t, c in universal[:10]:
        print(f"  {t}: {c} folios")

    # Cumulative intersection test
    print("\n--- Cumulative Intersection Decay ---")
    structural = ['ar', 'daiin', 'ol', 'al', 'or', 'aiin', 'dar', 'chol', 'shol']
    cumulative = None
    for token in structural:
        if token not in token_to_folios:
            continue
        folios = token_to_folios[token]
        if cumulative is None:
            cumulative = folios.copy()
        else:
            cumulative = cumulative & folios
        print(f"After {token:8}: {len(cumulative):2} folios remaining")

    # CSP Analysis (Refinement 1)
    print("\n--- Compatibility Survival Power (CSP) ---")
    print("CSP = mean compatibility when token added to random bundles")
    print("High coverage + LOW CSP = polarizing token")

    csp_results = []
    for token in structural:
        if token in token_to_folios:
            csp = compute_csp(token, token_to_folios, all_tokens)
            folio_count = len(token_to_folios[token])
            csp_results.append((token, folio_count, csp))
            classification = "universal" if csp > 5 else "polarizing" if folio_count > 15 else "restrictive"
            print(f"  {token:12}: coverage={folio_count:2}, CSP={csp:.1f} -> {classification}")

    return coverage, csp_results


def phase3_record_boundary_comparison(loader, token_to_folios_20, token_to_folios_30):
    """Phase 3: Compare record boundaries with 20 vs 30 folios.

    Refinement 2: Strict compatibility-existence boundary detection.
    Logs compatibility trajectory per line for post-hoc validation.
    """
    print("\n" + "=" * 60)
    print("PHASE 3: Record Boundary Comparison")
    print("=" * 60)
    print("Boundary condition: compatibility_count == 0 (strict)")

    def count_compatible(tokens, token_to_folios):
        if not tokens:
            return 30  # Max
        folio_sets = [token_to_folios.get(t, set()) for t in tokens]
        folio_sets = [f for f in folio_sets if f]  # Remove empty
        if not folio_sets:
            return 30
        return len(set.intersection(*folio_sets))

    test_folios = ['1r', '2r', '3r']
    all_trajectories = {}

    for label, t2f, max_folios in [("20 folios (Z+A)", token_to_folios_20, 20),
                                    ("30 folios (all)", token_to_folios_30, 30)]:
        print(f"\n--- {label} ---")
        total_boundaries = 0
        total_lines = 0
        all_trajectories[label] = {}

        for folio_id in test_folios:
            folio = loader.get_folio(folio_id)
            if not folio:
                continue

            boundaries = 0
            accumulated = []
            trajectory = []  # Log compatibility at each line

            for line_num, line_tokens in enumerate(folio.lines):
                line_texts = [t.text for t in line_tokens]
                new_accum = accumulated + line_texts

                compat = count_compatible(new_accum, t2f)
                trajectory.append(compat)

                # STRICT boundary: compatibility == 0
                if compat == 0 and accumulated:
                    boundaries += 1
                    accumulated = line_texts
                    # Recompute for new record start
                    compat = count_compatible(accumulated, t2f)
                else:
                    accumulated = new_accum

            total_boundaries += boundaries
            total_lines += len(folio.lines)
            all_trajectories[label][folio_id] = trajectory
            print(f"  f{folio_id}: {len(folio.lines)} lines, {boundaries} boundaries")
            print(f"    Trajectory: {trajectory[:10]}{'...' if len(trajectory) > 10 else ''}")

        mean_record = total_lines / (total_boundaries + 1) if total_boundaries >= 0 else total_lines
        print(f"  Mean record length: {mean_record:.2f} lines")

    return all_trajectories


def main():
    # Load all data
    folios_by_section, features_data = load_all_azc_folios()

    print("=" * 60)
    print("FULL AZC LANDSCAPE INVESTIGATION")
    print("Testing with complete ZACHS folio set")
    print("=" * 60)

    print("\nAZC Sections found:")
    for section, ids in sorted(folios_by_section.items()):
        print(f"  {section}: {len(ids)} folios")

    all_folio_ids = []
    for ids in folios_by_section.values():
        all_folio_ids.extend(ids)
    print(f"\nTotal AZC folios: {len(all_folio_ids)}")

    loader = FolioLoader()
    loader.load()

    # Build full token map
    token_to_folios, folio_to_tokens = build_token_to_folio_map(loader, all_folio_ids)

    print(f"Total unique tokens across all AZC: {len(token_to_folios)}")

    # Phase 1
    section_vocab = phase1_section_analysis(folios_by_section, token_to_folios, folio_to_tokens)

    # Phase 2 (returns coverage + CSP results)
    coverage, csp_results = phase2_structural_tokens(token_to_folios, len(all_folio_ids))

    # Phase 3 - build 20-folio map for comparison
    za_ids = folios_by_section.get('Z', []) + folios_by_section.get('A', [])
    token_to_folios_20, _ = build_token_to_folio_map(loader, za_ids)

    trajectories = phase3_record_boundary_comparison(loader, token_to_folios_20, token_to_folios)

    # Save results
    results = {
        'sections': {s: len(ids) for s, ids in folios_by_section.items()},
        'total_folios': len(all_folio_ids),
        'total_tokens': len(token_to_folios),
        'section_vocab_sizes': {s: len(v) for s, v in section_vocab.items()},
        'csp_results': [{'token': t, 'coverage': c, 'csp': round(csp, 2)}
                        for t, c, csp in csp_results],
        'trajectories': trajectories
    }

    results_path = Path(__file__).parent.parent.parent / "results" / "full_azc_landscape.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")


if __name__ == '__main__':
    main()
