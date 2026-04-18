"""
Phase 642, Script 3: Match 26 pharmaceutical-cluster folios against 7 Brunschwig
1512 ingredient-reference chapters.

Target corpus: 7 "Von X" ingredient chapters (Piper, Cinnamomum, Rosa, Scordeon,
Opium, Agaricus, Crocus) — the unique 1512 ingredient-description cluster.

Match cluster: 26 folios identified in s2 as pharmaceutical-regime (f33r/v, f34r/v,
f39r/v, f40r/v, f43r, f50r/v, f55r/v, f85r1/2, f86v4-6, f94r/v, f95r1/2/v1/v2,
f105v, f114r).

CRITICAL TEST: does f55r rank OPIUM in top-3?
  - If YES: systematic pipeline reproduces the hand-targeted PT-018 finding
  - If NO: pipeline isn't capturing what made PT-018 work, feature design fails

Also check: do the 16 matched-Testamentum folios (negative control) rank LOW
across all 7 ingredient chapters?
"""
import sys, io, os, json
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, ROOT)

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load 1512 ingredient chapters
with open(os.path.join(os.path.dirname(__file__), '..', 'results', 'brunschwig_1512_ingredient_chapters.json'), 'r', encoding='utf-8') as f:
    ingredients = json.load(f)['chapters']

# Load cluster assignments
with open(os.path.join(os.path.dirname(__file__), '..', 'results', 'unsupervised_cluster.json'), 'r', encoding='utf-8') as f:
    cluster_data = json.load(f)
F55R_CLUSTER = cluster_data['f55r_cluster']
PHARM_CLUSTER_FOLIOS = [f for f, c in cluster_data['cluster_assignments'].items() if c == F55R_CLUSTER]
MATCHED_TESTAMENTUM = {'f75r','f76r','f84r','f79r','f82r','f103r','f76v','f77v','f81v','f82v','f112r','f112v','f116r','f107r','f80r','f83r'}

print(f"Pharmaceutical cluster size: {len(PHARM_CLUSTER_FOLIOS)}")
print(f"Matched Testamentum (negative control): {len(MATCHED_TESTAMENTUM)}")
print(f"Ingredient chapters: {len(ingredients)}")

# ============================================================
# Feature mapping between Voynich-side and Brunschwig-side
# ============================================================
# Voynich operational signatures → Brunschwig feature proxies
#
# The matching is based on STRUCTURAL similarity of operation density, not
# literal word matching. Each side's features are z-normalized within its
# corpus, then cosine similarity is computed across mapped feature pairs.
#
# Mapping:
#   Voynich otal/iin suffix rate  ↔ Brunschwig extraction_count (drip/flow)
#   Voynich -iin/-ain rate         ↔ Brunschwig sealing_count + vessel_count
#   Voynich multi-paragraph count  ↔ Brunschwig multiple_methods_count
#   Voynich e-depth profile        ↔ Brunschwig gentle_heat_count
#   Voynich ch+sh prefix           ↔ Brunschwig monitoring_count
#   Voynich qot-compound rate      ↔ Brunschwig drying_count (apparatus stationary)

def folio_matching_features(folio):
    """Extract features from a Voynich folio that map to Brunschwig ingredient features."""
    tokens = [t for t in tx.currier_b() if t.folio == folio and t.word.strip() and '*' not in t.word]
    n = max(1, len(tokens))

    # Count suffix -iin/-ain (containment/sealing proxy)
    iin_count = sum(1 for t in tokens if t.word.endswith('iin') or t.word.endswith('ain'))
    # Count otal-family tokens (extraction/drip proxy)
    otal_count = sum(1 for t in tokens if t.word in ('otal','otaldiin','otar','otol','otaly'))
    # Count qokaiin-like tokens (apparatus-sustained proxy)
    qokaiin_count = sum(1 for t in tokens if t.word == 'qokaiin' or t.word == 'qokain')
    # Count e-depth ≥2 (gentle heat proxy)
    gentle_heat = 0
    ch_sh_count = 0
    qot_count = 0
    par_count = 0
    dal_count = 0
    for t in tokens:
        m = morph.extract(t.word)
        a = morph.atomize(t.word)
        if m and m.prefix in ('ch', 'sh'):
            ch_sh_count += 1
        if a and a.e_depth is not None and a.e_depth >= 2:
            gentle_heat += 1
        if t.par_initial:
            par_count += 1
        if m and m.prefix == 'qo' and a and a.atoms and a.atoms[0][0] == 't':
            qot_count += 1
        if t.word == 'dal':
            dal_count += 1

    return {
        'f_extraction': otal_count / n,
        'f_sealing': iin_count / n,
        'f_multi_method': par_count / n * 100,  # paragraph density as multi-method proxy
        'f_gentle_heat': gentle_heat / n,
        'f_monitoring': ch_sh_count / n,
        'f_sustained_apparatus': (qot_count + qokaiin_count) / n,
        'f_dosage': dal_count / n,
    }

def ingredient_matching_features(ch):
    """Extract matching features from a Brunschwig ingredient chapter."""
    f = ch['features']
    wc = max(1, ch['word_count'])
    return {
        'f_extraction': f['extraction_count'] / wc * 100,
        'f_sealing': f['sealing_count'] / wc * 100,
        'f_multi_method': f['multiple_methods_count'] / wc * 100,
        'f_gentle_heat': f['gentle_heat_count'] / wc * 100,
        'f_monitoring': f['monitoring_count'] / wc * 100,
        'f_sustained_apparatus': f['drying_count'] / wc * 100,
        'f_dosage': f['dosage_specific_count'] / wc * 100,
    }

# ============================================================
# Build all feature vectors + standardize
# ============================================================
FEATURE_KEYS = ['f_extraction','f_sealing','f_multi_method','f_gentle_heat',
                'f_monitoring','f_sustained_apparatus','f_dosage']

# Compute for all Brunschwig ingredient chapters
ing_features = []
for ch in ingredients:
    feats = ingredient_matching_features(ch)
    ing_features.append((ch['ingredient'], feats))

# Compute for cluster folios + matched Testamentum (as negative control)
all_folios_to_match = PHARM_CLUSTER_FOLIOS + [f for f in MATCHED_TESTAMENTUM if f not in PHARM_CLUSTER_FOLIOS]
folio_features = []
for folio in all_folios_to_match:
    feats = folio_matching_features(folio)
    folio_features.append((folio, feats))

# Z-normalize each side independently
def zn(values):
    import statistics
    if len(values) < 2: return values
    m = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 1.0
    sd = sd if sd > 0 else 1.0
    return [(v - m) / sd for v in values]

# Build z-scored feature vectors
ing_z = {name: {} for name, _ in ing_features}
folio_z = {name: {} for name, _ in folio_features}

for key in FEATURE_KEYS:
    ing_vals = [feats[key] for _, feats in ing_features]
    folio_vals = [feats[key] for _, feats in folio_features]
    ing_z_vals = zn(ing_vals)
    folio_z_vals = zn(folio_vals)
    for (name, _), v in zip(ing_features, ing_z_vals):
        ing_z[name][key] = v
    for (name, _), v in zip(folio_features, folio_z_vals):
        folio_z[name][key] = v

# ============================================================
# Match each folio to each ingredient via cosine similarity
# ============================================================
import math

def cosine_sim(a_dict, b_dict, keys):
    a = [a_dict[k] for k in keys]
    b = [b_dict[k] for k in keys]
    dot = sum(ai*bi for ai, bi in zip(a, b))
    na = math.sqrt(sum(ai*ai for ai in a))
    nb = math.sqrt(sum(bi*bi for bi in b))
    if na * nb == 0: return 0.0
    return dot / (na * nb)

print("\n" + "="*90)
print("PER-FOLIO RANKED MATCHES to 1512 Ingredient Chapters")
print("="*90)

all_folio_results = {}
for folio, _ in folio_features:
    scores = []
    for ing_name, _ in ing_features:
        sim = cosine_sim(folio_z[folio], ing_z[ing_name], FEATURE_KEYS)
        scores.append((ing_name, sim))
    scores.sort(key=lambda x: -x[1])
    all_folio_results[folio] = scores

# ============================================================
# Report: pharmaceutical-cluster folios top-3 candidates
# ============================================================
print("\nPHARMACEUTICAL CLUSTER FOLIOS:")
print(f"{'Folio':<7} Top-3 Brunschwig candidates")
print("-" * 90)
for folio in PHARM_CLUSTER_FOLIOS:
    scores = all_folio_results[folio]
    top3 = scores[:3]
    line = f"{folio:<7s} "
    for i, (ing, sim) in enumerate(top3):
        line += f"{i+1}.{ing}({sim:+.2f}) "
    print(line)

# KEY TEST: does f55r rank opium in top-3?
print("\n" + "="*90)
print("CRITICAL TEST: f55r's ranking for each ingredient")
print("="*90)
f55r_scores = all_folio_results.get('f55r', [])
for i, (ing, sim) in enumerate(f55r_scores, 1):
    marker = ' *** OPIUM (our target) ***' if ing.lower() == 'opium' else ''
    print(f"  #{i}: {ing:<15s} sim={sim:+.3f}{marker}")

# ============================================================
# NEGATIVE CONTROL: matched Testamentum folios should rank LOW
# ============================================================
print("\n" + "="*90)
print("NEGATIVE CONTROL: matched Testamentum folios (should rank LOW)")
print("="*90)
print(f"{'Folio':<7} Top-3 Brunschwig (these should all have LOW similarity)")
print("-" * 90)
for folio in sorted(MATCHED_TESTAMENTUM):
    if folio not in all_folio_results: continue
    scores = all_folio_results[folio]
    top3 = scores[:3]
    line = f"{folio:<7s} "
    for i, (ing, sim) in enumerate(top3):
        line += f"{i+1}.{ing}({sim:+.2f}) "
    print(line)

# ============================================================
# AGGREGATE STATS
# ============================================================
print("\n" + "="*90)
print("AGGREGATE ANALYSIS")
print("="*90)

# Mean top-1 similarity for pharm cluster vs matched Testamentum
pharm_top1_sims = [all_folio_results[f][0][1] for f in PHARM_CLUSTER_FOLIOS]
testa_top1_sims = [all_folio_results[f][0][1] for f in MATCHED_TESTAMENTUM if f in all_folio_results]
print(f"Pharm cluster mean top-1 similarity: {sum(pharm_top1_sims)/len(pharm_top1_sims):+.3f}")
print(f"Matched Testamentum mean top-1 similarity: {sum(testa_top1_sims)/len(testa_top1_sims):+.3f}")

# f55r opium rank
f55r_opium_rank = [i for i, (ing, _) in enumerate(f55r_scores, 1) if ing.lower() == 'opium']
if f55r_opium_rank:
    rank = f55r_opium_rank[0]
    print(f"\nf55r OPIUM rank: #{rank}/7")
    if rank <= 3:
        print(f"  *** PASS: opium in top-3 ***  Systematic pipeline reproduces PT-018")
    else:
        print(f"  *** FAIL: opium rank {rank} ***  Pipeline does not capture PT-018 signal")

# Count how often opium is top-1 vs other folios
opium_top1_count = sum(1 for f in PHARM_CLUSTER_FOLIOS if all_folio_results[f][0][0].lower() == 'opium')
print(f"\nPharm-cluster folios with OPIUM as top-1: {opium_top1_count}/{len(PHARM_CLUSTER_FOLIOS)}")

# Save
out = {
    'metadata': {
        'phase': 642,
        'script': 's3_folio_ingredient_matching',
        'n_pharm_cluster': len(PHARM_CLUSTER_FOLIOS),
        'n_ingredients': len(ingredients),
    },
    'per_folio_ranked': {f: [(ing, sim) for ing, sim in scores] for f, scores in all_folio_results.items()},
    'pharm_top1_mean_sim': sum(pharm_top1_sims)/len(pharm_top1_sims),
    'testa_top1_mean_sim': sum(testa_top1_sims)/len(testa_top1_sims) if testa_top1_sims else None,
    'f55r_opium_rank': f55r_opium_rank[0] if f55r_opium_rank else None,
    'opium_top1_count_pharm': opium_top1_count,
}
out_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'folio_ingredient_matching.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
print(f"\nWrote {out_path}")
