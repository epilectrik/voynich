"""
intra_folio_paragraph_probe.py - How do paragraphs on the same folio relate?

Questions:
1. Vocabulary overlap within folio vs across folios
2. Role composition by paragraph ordinal
3. First paragraph vs others
4. Do paragraphs "converge" or "diverge" across sequence?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import statistics
import random

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Role classes
CC_CLASSES = {10, 11, 12, 17}
EN_CLASSES = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}
FL_CLASSES = {7, 30, 38, 40}
FQ_CLASSES = {9, 13, 14, 23}

def get_role(cls):
    if cls in CC_CLASSES: return 'CC'
    if cls in EN_CLASSES: return 'EN'
    if cls in FL_CLASSES: return 'FL'
    if cls in FQ_CLASSES: return 'FQ'
    return 'AX'

def jaccard(set1, set2):
    if not set1 and not set2:
        return 0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load class map
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    # Load B paragraphs
    with open(results_dir / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    with open(results_dir / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Build paragraph vocabulary sets
    par_vocab = {}
    par_roles = {}

    for par in inventory['paragraphs']:
        par_id = par['par_id']
        tokens = tokens_by_par[par_id]

        vocab = set()
        role_counts = Counter()

        for t in tokens:
            word = t['word']
            if word and '*' not in word:
                vocab.add(word)
                if word in class_map:
                    role = get_role(class_map[word])
                    role_counts[role] += 1

        par_vocab[par_id] = vocab
        total = sum(role_counts.values())
        par_roles[par_id] = {r: role_counts[r]/total if total > 0 else 0 for r in ['EN', 'FL', 'FQ', 'CC', 'AX']}

    # Group by folio
    folio_pars = defaultdict(list)
    for par in inventory['paragraphs']:
        folio_pars[par['folio']].append(par)

    # === 1. INTRA-FOLIO vs INTER-FOLIO SIMILARITY ===
    print("=== INTRA-FOLIO vs INTER-FOLIO VOCABULARY SIMILARITY ===\n")

    intra_folio_sims = []
    inter_folio_sims = []

    all_par_ids = list(par_vocab.keys())

    for folio, pars in folio_pars.items():
        if len(pars) < 2:
            continue

        # Intra-folio: compare all pairs within folio
        for i in range(len(pars)):
            for j in range(i+1, len(pars)):
                sim = jaccard(par_vocab[pars[i]['par_id']], par_vocab[pars[j]['par_id']])
                intra_folio_sims.append(sim)

    # Inter-folio: random pairs from different folios
    random.seed(42)
    for _ in range(len(intra_folio_sims)):
        p1, p2 = random.sample(all_par_ids, 2)
        # Ensure different folios
        f1 = next(p['folio'] for p in inventory['paragraphs'] if p['par_id'] == p1)
        f2 = next(p['folio'] for p in inventory['paragraphs'] if p['par_id'] == p2)
        if f1 != f2:
            sim = jaccard(par_vocab[p1], par_vocab[p2])
            inter_folio_sims.append(sim)

    print(f"Intra-folio pairs: {len(intra_folio_sims)}")
    print(f"  Mean Jaccard: {statistics.mean(intra_folio_sims):.3f}")
    print(f"  Median: {statistics.median(intra_folio_sims):.3f}")

    print(f"\nInter-folio pairs: {len(inter_folio_sims)}")
    print(f"  Mean Jaccard: {statistics.mean(inter_folio_sims):.3f}")
    print(f"  Median: {statistics.median(inter_folio_sims):.3f}")

    ratio = statistics.mean(intra_folio_sims) / statistics.mean(inter_folio_sims) if inter_folio_sims else 0
    print(f"\nIntra/Inter ratio: {ratio:.2f}x")

    # === 2. VOCABULARY OVERLAP BY PARAGRAPH ORDINAL ===
    print("\n=== VOCABULARY OVERLAP: PAR 1 vs LATER PARAGRAPHS ===\n")

    # For each folio, compare par 1 vocabulary with par 2, 3, 4...
    par1_vs_later = defaultdict(list)

    for folio, pars in folio_pars.items():
        if len(pars) < 2:
            continue

        par1_vocab = par_vocab[pars[0]['par_id']]

        for i, par in enumerate(pars[1:], start=2):
            later_vocab = par_vocab[par['par_id']]
            sim = jaccard(par1_vocab, later_vocab)
            par1_vs_later[i].append(sim)

    print("Par 1 vs Par N similarity:")
    for ordinal in sorted(par1_vs_later.keys())[:8]:
        sims = par1_vs_later[ordinal]
        if sims:
            print(f"  Par 1 vs Par {ordinal}: mean={statistics.mean(sims):.3f}, n={len(sims)}")

    # === 3. ROLE COMPOSITION BY ORDINAL ===
    print("\n=== ROLE COMPOSITION BY PARAGRAPH ORDINAL ===\n")

    role_by_ordinal = defaultdict(lambda: defaultdict(list))

    for folio, pars in folio_pars.items():
        for i, par in enumerate(pars, start=1):
            roles = par_roles[par['par_id']]
            for role, rate in roles.items():
                role_by_ordinal[min(i, 6)][role].append(rate)  # Cap at 6+

    print("Mean role rates by ordinal position:")
    print(f"{'Ordinal':<8} {'EN':>8} {'FL':>8} {'FQ':>8} {'CC':>8} {'n':>6}")
    for ordinal in sorted(role_by_ordinal.keys()):
        roles = role_by_ordinal[ordinal]
        n = len(roles['EN'])
        en = statistics.mean(roles['EN']) if roles['EN'] else 0
        fl = statistics.mean(roles['FL']) if roles['FL'] else 0
        fq = statistics.mean(roles['FQ']) if roles['FQ'] else 0
        cc = statistics.mean(roles['CC']) if roles['CC'] else 0
        label = f"{ordinal}+" if ordinal == 6 else str(ordinal)
        print(f"{label:<8} {en:>8.3f} {fl:>8.3f} {fq:>8.3f} {cc:>8.3f} {n:>6}")

    # === 4. FIRST PARAGRAPH DISTINCTIVENESS ===
    print("\n=== FIRST PARAGRAPH DISTINCTIVENESS ===\n")

    par1_en = []
    par1_fl = []
    later_en = []
    later_fl = []

    for folio, pars in folio_pars.items():
        if len(pars) < 2:
            continue

        par1_roles = par_roles[pars[0]['par_id']]
        par1_en.append(par1_roles['EN'])
        par1_fl.append(par1_roles['FL'])

        for par in pars[1:]:
            roles = par_roles[par['par_id']]
            later_en.append(roles['EN'])
            later_fl.append(roles['FL'])

    print(f"EN rate: Par 1 = {statistics.mean(par1_en):.3f}, Later = {statistics.mean(later_en):.3f}")
    print(f"FL rate: Par 1 = {statistics.mean(par1_fl):.3f}, Later = {statistics.mean(later_fl):.3f}")

    # === 5. ADJACENT PARAGRAPH SIMILARITY ===
    print("\n=== ADJACENT vs NON-ADJACENT PARAGRAPH SIMILARITY ===\n")

    adjacent_sims = []
    nonadjacent_sims = []

    for folio, pars in folio_pars.items():
        if len(pars) < 3:
            continue

        for i in range(len(pars) - 1):
            # Adjacent
            sim = jaccard(par_vocab[pars[i]['par_id']], par_vocab[pars[i+1]['par_id']])
            adjacent_sims.append(sim)

        # Non-adjacent (skip 1)
        for i in range(len(pars) - 2):
            sim = jaccard(par_vocab[pars[i]['par_id']], par_vocab[pars[i+2]['par_id']])
            nonadjacent_sims.append(sim)

    print(f"Adjacent pairs: mean={statistics.mean(adjacent_sims):.3f}, n={len(adjacent_sims)}")
    print(f"Skip-1 pairs: mean={statistics.mean(nonadjacent_sims):.3f}, n={len(nonadjacent_sims)}")

    adj_ratio = statistics.mean(adjacent_sims) / statistics.mean(nonadjacent_sims) if nonadjacent_sims else 0
    print(f"Adjacent/Skip-1 ratio: {adj_ratio:.2f}x")

    # === 6. UNIQUE VOCABULARY BY ORDINAL ===
    print("\n=== VOCABULARY INTRODUCED BY EACH PARAGRAPH ===\n")

    new_vocab_by_ordinal = defaultdict(list)

    for folio, pars in folio_pars.items():
        seen_vocab = set()
        for i, par in enumerate(pars, start=1):
            vocab = par_vocab[par['par_id']]
            new_words = vocab - seen_vocab
            new_rate = len(new_words) / len(vocab) if vocab else 0
            new_vocab_by_ordinal[min(i, 6)].append(new_rate)
            seen_vocab |= vocab

    print("Fraction of 'new' vocabulary by ordinal:")
    for ordinal in sorted(new_vocab_by_ordinal.keys()):
        rates = new_vocab_by_ordinal[ordinal]
        label = f"{ordinal}+" if ordinal == 6 else str(ordinal)
        print(f"  Par {label}: {statistics.mean(rates):.3f} new")

if __name__ == '__main__':
    main()
