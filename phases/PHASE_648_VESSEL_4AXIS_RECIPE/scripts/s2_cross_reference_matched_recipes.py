"""
Phase 648 Step 2: Cross-reference o-prefix folio profile with matched recipes.

For each matched folio, get its 4 o-prefix fractions and compare against
the recipe's known physical emphasis. Test predictions:

- TRANSFER recipes (cohobation, distillation, drip-counting) → ot-enriched
- STAGING recipes (multi-chamber, sealed, putrefaction) → ol-enriched
- TEMPERATURE recipes (coagulation, fusibility) → ok-enriched
- OBSERVATION recipes (silver-plate test, element separation) → or-enriched
"""
import sys
import json
sys.path.insert(0, '.')

# Load profile
with open('phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/o_prefix_folio_profile.json') as f:
    profile = json.load(f)

# Load matched recipes
with open('phases/SISMEL_RECIPE_CORPUS/results/matched_recipes_status.json') as f:
    matches = json.load(f)

# Predicted physical channel for each matched recipe
# Based on recipe label content — locked before viewing prefix data
RECIPE_PREDICTIONS = {
    'f75r':  {'pred': 'ot', 'reason': '9x/4x reflux distillation = transfer'},
    'f76r':  {'pred': 'or', 'reason': 'silver-plate test = observation/yield'},
    'f84r':  {'pred': 'ol', 'reason': 'balneum + putrefaction = multi-chamber staging'},
    'f79r':  {'pred': 'ot', 'reason': 'sublimation = transfer (vapor to recipient)'},
    'f82r':  {'pred': 'ol', 'reason': 'sealed maceration = chamber-state staging'},
    'f103r': {'pred': 'ol', 'reason': 'multi-chamber ferment multiplication'},
    'f76v':  {'pred': 'ol', 'reason': 'ferment join+bind = staging'},
    'f77v':  {'pred': 'ol', 'reason': 'furnace specification = staging/setup'},
    'f81v':  {'pred': 'ol', 'reason': 'potable gold = multi-step staging'},
    'f82v':  {'pred': 'ol', 'reason': 'vessel specification = staging/setup'},
    'f112r': {'pred': 'ot', 'reason': 'cohobation = explicit repeated transfer'},
    'f112v': {'pred': 'ol', 'reason': 'lunaria→quicksilver = multi-stage'},
    'f116r': {'pred': 'ok', 'reason': 'fusibility test = temperature-driven'},
    'f107r': {'pred': 'ok', 'reason': 'coagulation = temperature transition'},
    'f80r':  {'pred': 'ol', 'reason': 'animal ash multi-chapter = multi-step staging'},
    'f83r':  {'pred': 'ot', 'reason': 'drip-counted = transfer/drip (C1958 anchor)'},
}

# Compute ranks: for each folio, which prefix is most enriched relative to
# corpus mean? Use z-score-style: (folio_frac - mean) / mean
def rank_prefixes(folio):
    if folio not in profile:
        return None
    p = profile[folio]
    # Corpus means from Step 1
    means = {'ok': 0.0691, 'ot': 0.0591, 'ol': 0.0543, 'or': 0.0214}
    rel = {pref: (p[f'{pref}_frac'] - means[pref]) / means[pref] for pref in means}
    sorted_rel = sorted(rel.items(), key=lambda x: -x[1])
    return sorted_rel, p

print("="*100)
print(f"{'Folio':6s}  {'Recipe':50s}  {'Pred':4s}  {'Top':4s}  {'Match?':7s}  Top 2 prefixes (rel-enrichment)")
print("="*100)

correct = 0
total = 0
results = []
for m in matches:
    folio = m['folio']
    if folio not in profile:
        continue
    pred = RECIPE_PREDICTIONS.get(folio, {}).get('pred', '?')
    ranked, p = rank_prefixes(folio)
    top_pref = ranked[0][0]
    top_rel = ranked[0][1]
    second_pref = ranked[1][0]
    second_rel = ranked[1][1]
    match = 'YES' if top_pref == pred else ('2nd' if second_pref == pred else 'no')
    if match == 'YES':
        correct += 1
    total += 1
    print(f"{folio:6s}  {m['recipe_label'][:48]:50s}  {pred:4s}  {top_pref:4s}  "
          f"{match:7s}  {top_pref}={top_rel:+.2f}  {second_pref}={second_rel:+.2f}")
    results.append({
        'folio': folio,
        'recipe': m['recipe_label'],
        'tier': m['tier'],
        'predicted_prefix': pred,
        'top_prefix': top_pref,
        'top_rel_enrichment': round(top_rel, 3),
        'second_prefix': second_pref,
        'second_rel_enrichment': round(second_rel, 3),
        'all_ranks': [(r, round(v,3)) for r,v in ranked],
        'match': match,
        'reason': RECIPE_PREDICTIONS.get(folio, {}).get('reason', ''),
    })

print()
print(f"Top-1 prediction accuracy: {correct}/{total} = {correct/total*100:.1f}%")
print(f"Random baseline: 25% (4 prefixes)")

# Per-channel accuracy
from collections import defaultdict
by_pred = defaultdict(lambda: {'correct': 0, 'total': 0})
for r in results:
    by_pred[r['predicted_prefix']]['total'] += 1
    if r['match'] == 'YES':
        by_pred[r['predicted_prefix']]['correct'] += 1

print()
print("Per-channel accuracy (top-1):")
for pref, s in by_pred.items():
    print(f"  {pref}: {s['correct']}/{s['total']}")

# Save results
with open('phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/cross_reference.json', 'w') as f:
    json.dump(results, f, indent=2)
