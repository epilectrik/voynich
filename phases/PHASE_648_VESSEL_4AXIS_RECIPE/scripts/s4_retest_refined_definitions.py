"""
Phase 648 Step 4: Re-run cross-reference test with refined channel definitions
derived from reading actual Catalan recipe text.

REFINED DEFINITIONS:
- ol = vessel-content state monitoring (what's in which vessel, batch identity, vessel role)
- ot = material transfer / addition / iteration cycles (broader than drip rate)
- ok = thermal regime / fire-degree state
- or = unconfirmed

CAVEAT: Definitions were derived from reading these same recipes' texts,
so this is within-sample confirmation, not out-of-sample test. Read accordingly.

Predictions classified by reading the Catalan recipe text and identifying:
- PRIMARY operation (what dominates the recipe's procedural content)
- SECONDARY operation (next-most-emphasized)
"""
import sys
import json
sys.path.insert(0, '.')

with open('phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/o_prefix_folio_profile.json') as f:
    profile = json.load(f)

# Text-grounded predictions: PRIMARY and SECONDARY for each match
# Locked-in based on careful reading of Catalan text in s3 output
PREDICTIONS = {
    'f75r':  {'primary': 'ol', 'secondary': 'ot',
              'evidence': 'first/second/third water kept separate ("metràs a part"); 4x/9x reflux iteration'},
    'f76r':  {'primary': 'ok', 'secondary': 'ol',
              'evidence': 'theoretical M/O/L symbolic chapter; calcination-driven preparation; "preparació de O e de L se fa..."'},
    'f84r':  {'primary': 'ol', 'secondary': 'ot',
              'evidence': 'apparatus arrangement (alembic on cucurbit, vessel in balneum); transfer between configurations'},
    'f79r':  {'primary': 'ol', 'secondary': 'ot',
              'evidence': 'state transition (sublimative -> fixed); iterative return of distillate'},
    'f82r':  {'primary': 'ok', 'secondary': 'ol',
              'evidence': 'theoretical fire-regime: "multiplicació del foch", "calor temprada/naturall/excellent", "lent foch"'},
    'f103r': {'primary': 'ot', 'secondary': 'ol',
              'evidence': 'chamber B+C combination ("mesclar s\'[h]a tot en un"); multi-chamber arrangement'},
    'f76v':  {'primary': 'ot', 'secondary': 'ol',
              'evidence': 'adding H by weight; adding fifth letter; explicit additions until state'},
    'f77v':  {'primary': 'ol', 'secondary': 'ok',
              'evidence': 'specification of subjects (leon vert, fum gelat); classifying contents'},
    'f81v':  {'primary': 'ol', 'secondary': 'ot',
              'evidence': 'multi-vessel work (carabaça, balneum); distillation transfer steps'},
    'f82v':  {'primary': 'ol', 'secondary': 'ok',
              'evidence': 'stone-in-elements specification (where the stone resides in each element)'},
    'f112r': {'primary': 'ot', 'secondary': 'ok',
              'evidence': '3x distill in balneum, pour back onto earth, repeated cohobation cycle'},
    'f112v': {'primary': 'ot', 'secondary': 'ol',
              'evidence': 'distillation separating elements one by one; "continua en bany ta distillació en tro..."'},
    'f116r': {'primary': 'ot', 'secondary': 'ol',
              'evidence': 'reiterate sublimation of unfixed onto fixed until similarly fixed'},
    'f107r': {'primary': 'ot', 'secondary': 'ok',
              'evidence': 'color transitions through repeated heating cycles'},
    'f80r':  {'primary': 'ol', 'secondary': 'ot',
              'evidence': 'vessel-naming chapter: distillatori/dissolutori/putrefactori/calcinatori — vessel role identity'},
    'f83r':  {'primary': 'ol', 'secondary': 'ot',
              'evidence': 'sealed in ampoule with cera comuna for 2 days; vessel-content state maintained'},
}

# Load matched recipes
with open('phases/SISMEL_RECIPE_CORPUS/results/matched_recipes_status.json') as f:
    matches = json.load(f)

means = {'ok': 0.0691, 'ot': 0.0591, 'ol': 0.0543, 'or': 0.0214}

def rank_prefixes(folio):
    p = profile[folio]
    rel = {pref: (p[f'{pref}_frac'] - means[pref]) / means[pref] for pref in means}
    return sorted(rel.items(), key=lambda x: -x[1])

print("="*100)
print("ROUND 2: TEXT-GROUNDED PREDICTIONS UNDER REFINED CHANNEL DEFINITIONS")
print("="*100)
print(f"{'Folio':6s} {'Pri':4s} {'Top':4s} {'Match':6s}  {'Sec':4s} {'2nd':4s} {'Top2':6s}  Evidence")
print("-"*120)

top1_correct = 0
top2_correct = 0  # Both primary and secondary in top-2
either_in_top2 = 0  # Primary appears in top 2
total = 0
results = []

for m in matches:
    f = m['folio']
    if f not in profile or f not in PREDICTIONS:
        continue
    pred = PREDICTIONS[f]
    pri = pred['primary']
    sec = pred['secondary']
    ranked = rank_prefixes(f)
    top1 = ranked[0][0]
    top2 = ranked[1][0]
    actual_top2 = {top1, top2}
    predicted_top2 = {pri, sec}

    pri_match = (pri == top1)
    pri_in_top2 = (pri in actual_top2)
    sec_in_top2 = (sec in actual_top2)
    both_in_top2 = (predicted_top2 == actual_top2)

    if pri_match: top1_correct += 1
    if both_in_top2: top2_correct += 1
    if pri_in_top2: either_in_top2 += 1
    total += 1

    pri_flag = 'YES' if pri_match else 'no'
    top2_flag = 'YES' if both_in_top2 else ('1of2' if pri_in_top2 else 'no')

    print(f"{f:6s} {pri:4s} {top1:4s} {pri_flag:6s}  {sec:4s} {top2:4s} {top2_flag:6s}  {pred['evidence'][:65]}")

    results.append({
        'folio': f, 'predicted_primary': pri, 'predicted_secondary': sec,
        'actual_top': top1, 'actual_second': top2,
        'top1_correct': pri_match, 'top2_correct': both_in_top2,
        'evidence': pred['evidence'],
        'rates': {pref: profile[f][f'{pref}_frac'] for pref in means},
    })

print()
print(f"Top-1 accuracy: {top1_correct}/{total} = {top1_correct/total*100:.1f}%")
print(f"Top-2 accuracy (both predicted prefixes match actual top-2): {top2_correct}/{total} = {top2_correct/total*100:.1f}%")
print(f"Primary-in-top-2 accuracy: {either_in_top2}/{total} = {either_in_top2/total*100:.1f}%")
print()
print("Random baselines:")
print(f"  Top-1: 25% (1/4)")
print(f"  Top-2 (both match unordered): 16.7% (1 / C(4,2)=6)")
print(f"  Primary-in-top-2: 50% (2/4)")
print()
print("Round 1 (label-based): top-1 = 37.5%")
print(f"Round 2 (text-grounded): top-1 = {top1_correct/total*100:.1f}%")

# Save results
with open('phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/refined_test.json', 'w') as f:
    json.dump({'results': results,
               'top1_acc': top1_correct/total,
               'top2_acc': top2_correct/total,
               'primary_in_top2_acc': either_in_top2/total,
               'n': total,
               'caveat': 'Within-sample test — predictions were derived from reading these same recipes'}, f, indent=2)
