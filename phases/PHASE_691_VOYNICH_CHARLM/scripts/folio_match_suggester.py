#!/usr/bin/env python3
"""
Phase 691.x: Recipe-folio match suggester.

Given the 9 confirmed Voynich-PL distillation matches, find candidate
matches for unmatched Currier-B folios via LM-embedding similarity.

Approach:
  1. Compute per-folio embedding (frequency-weighted mean of token embeddings
     from Phase 691.2 trained model)
  2. For each confirmed match (folio -> chapter), find nearest unmatched
     folios in embedding space
  3. Suggest those as candidates for matching recipe family

This DOESN'T claim direct recipe matches. It identifies UNMATCHED folios
that are structurally near CONFIRMED-MATCH folios — candidates worth
running through the Phase 668 matching pipeline.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript


def main():
    # Load token embeddings from Phase 691.2
    emb_path = PHASE_DIR / 'results' / 'embeddings' / 'token_embeddings_without_tag_seed691.npz'
    npz = np.load(emb_path, allow_pickle=True)
    tokens = list(npz['tokens'])
    embeddings = npz['embeddings']  # (V, 256)
    counts = npz['occurrences']
    print(f"Loaded {len(tokens)} token embeddings (dim {embeddings.shape[1]})")
    token_to_idx = {t: i for i, t in enumerate(tokens)}

    # Compute per-folio embedding (frequency-weighted mean of token embeddings)
    tx = Transcript()
    folio_token_counts = defaultdict(lambda: defaultdict(int))
    for tok in tx.all(h_only=True):
        if tok.word and not tok.is_uncertain:
            folio_token_counts[tok.folio][tok.word] += 1

    folios = sorted(folio_token_counts.keys())
    folio_embs = {}
    folio_total_tokens = {}
    for f in folios:
        tcounts = folio_token_counts[f]
        weighted_sum = np.zeros(embeddings.shape[1])
        total = 0
        for w, c in tcounts.items():
            if w in token_to_idx:
                weighted_sum += embeddings[token_to_idx[w]] * c
                total += c
        if total > 0:
            folio_embs[f] = weighted_sum / total
            folio_total_tokens[f] = total
    print(f"Computed embeddings for {len(folio_embs)} folios")

    # Load confirmed matches
    match_path = PROJECT_ROOT / 'phases/RECIPE_FOLIO_CORRESPONDENCE/results/recipe_matching.json'
    match_data = json.loads(match_path.read_text())
    table = match_data['T1_distillation_matching']['match_table']
    confirmed = [m for m in table if m.get('confident')]
    confirmed_folios = set(m['folio'] for m in confirmed)
    all_scored_folios = set(m['folio'] for m in table)
    print(f"\nConfirmed matches: {len(confirmed)}")
    print(f"All scored folios: {len(all_scored_folios)}")
    print(f"Folios in corpus but never scored: {len(folio_embs) - len(all_scored_folios)}")

    # Compute pairwise cosine similarities
    folio_list = sorted(folio_embs.keys())
    emb_matrix = np.array([folio_embs[f] for f in folio_list])
    norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True) + 1e-9
    emb_norm = emb_matrix / norms
    sim_matrix = emb_norm @ emb_norm.T  # (F, F)
    folio_idx = {f: i for i, f in enumerate(folio_list)}

    # For each confirmed match, find nearest UNMATCHED folios in embedding space
    print(f"\n=== Candidate matches via LM-embedding proximity to confirmed matches ===")
    print(f"  For each confirmed match, the top-5 nearest unmatched folios are")
    print(f"  candidates for matching recipes near (or related to) the same chapter.\n")

    candidates = defaultdict(list)  # folio -> list of (confirmed_neighbor, chapter, similarity)
    for m in confirmed:
        cf = m['folio']
        chapter = m['chapter_number']
        if cf not in folio_idx:
            continue
        i = folio_idx[cf]
        sims = sim_matrix[i]
        # Sort all folios by similarity descending
        order = np.argsort(-sims)
        nearest_unmatched = []
        for j in order[:30]:
            f2 = folio_list[j]
            if f2 == cf:
                continue
            if f2 in all_scored_folios:
                continue
            nearest_unmatched.append((f2, float(sims[j])))
            if len(nearest_unmatched) >= 8:
                break
        print(f"  {cf} (matches Ch{chapter}, family={m.get('family','?')}):")
        for f2, sim in nearest_unmatched[:5]:
            n_tok = folio_total_tokens.get(f2, 0)
            print(f"    {f2:>7s}  sim={sim:.3f}  ({n_tok} tokens)  → candidate match for chapter near {chapter}")
            candidates[f2].append({'similar_to': cf, 'chapter_hint': chapter, 'similarity': sim})

    # For each unmatched folio, list which confirmed matches it's most similar to
    print(f"\n=== Top candidate matches per unmatched folio ===")
    print(f"  (Folios with high cosine similarity to confirmed-match folios)\n")
    unmatched_with_hints = []
    for f in folio_list:
        if f in all_scored_folios:
            continue
        if f not in folio_idx:
            continue
        # Get similarity to each confirmed-match folio
        i = folio_idx[f]
        sim_to_confirmed = []
        for m in confirmed:
            cf = m['folio']
            if cf in folio_idx:
                j = folio_idx[cf]
                sim_to_confirmed.append((cf, m['chapter_number'], float(sim_matrix[i, j])))
        sim_to_confirmed.sort(key=lambda x: -x[2])
        if sim_to_confirmed:
            top = sim_to_confirmed[0]
            unmatched_with_hints.append((f, top[2], top[0], top[1], folio_total_tokens.get(f, 0)))

    # Sort unmatched folios by their best confirmed-match similarity
    unmatched_with_hints.sort(key=lambda x: -x[1])
    print(f"  {'folio':>7s}  {'best_sim':>9s}  {'closest_confirmed':>17s}  {'hint_chapter':>12s}  {'n_tokens':>9s}")
    print(f"  {'─'*70}")
    for f, sim, cf, ch, n in unmatched_with_hints[:25]:
        print(f"  {f:>7s}  {sim:>9.3f}  {cf:>17s}  Ch{ch:>11d}  {n:>9d}")

    # Save full table
    out = {
        'method': 'folio_embedding_similarity_to_confirmed_matches',
        'n_folios_with_embeddings': len(folio_embs),
        'n_confirmed_matches': len(confirmed),
        'candidates_per_confirmed': {
            cf: [{'folio': f, 'similarity': s} for f, s in [
                (folio_list[j], float(sim_matrix[folio_idx[cf], j]))
                for j in np.argsort(-sim_matrix[folio_idx[cf]])[:10]
                if folio_list[j] != cf and folio_list[j] not in all_scored_folios
            ][:8]] for cf in [m['folio'] for m in confirmed] if cf in folio_idx
        },
        'top_candidates_per_unmatched': [
            {'folio': f, 'similarity': sim, 'closest_confirmed': cf,
             'hint_chapter': ch, 'n_tokens': n}
            for f, sim, cf, ch, n in unmatched_with_hints[:50]
        ],
    }
    out_path = PHASE_DIR / 'results' / 'predictions' / 'folio_match_suggestions.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
