"""
C1962 out-of-sample validation.

Phase 648 registered C1962 within-sample (16/16 top-1 fit on matched
recipes). The pending test: do the C1962 axes (ol=vessel-content state,
ot=transfer/iteration, ok=thermal regime, or=outcome) predict matches
on UNMATCHED folios?

Method (reverse-blind per C1935 template):
1. Compute o-prefix profile for each Currier B folio
2. Filter to UNMATCHED folios with strong dominance (top o-prefix
   rel-enrichment > +0.5)
3. For each candidate, predict expected recipe content from C1962 axes
4. Auto-classify unmatched PL Testamentum chapters by content (vessel/
   transfer/thermal/outcome keywords)
5. Score directional concordance: do unmatched-folio predicted-channel
   patterns concentrate on matching-channel unmatched recipes?

This converts C1962 from within-sample fit to out-of-sample test.
"""
import sys
import json
import re
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from scripts.voynich import Transcript
from collections import defaultdict, Counter

tx = Transcript()

# Load existing data
with open('phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/o_prefix_folio_profile.json') as f:
    profile = json.load(f)
with open('phases/SISMEL_RECIPE_CORPUS/results/matched_recipes_status.json') as f:
    matches = json.load(f)
with open('phases/SISMEL_RECIPE_CORPUS/results/sismel_corpus.json', encoding='utf-8') as f:
    corpus = json.load(f)

matched_folios = {m['folio'] for m in matches}
matched_chapters = {(m['part'], m['chapter_num']) for m in matches}

# Step 1: Identify unmatched folios with strong o-prefix dominance
means = {'ok': 0.0691, 'ot': 0.0591, 'ol': 0.0543, 'or': 0.0214}

candidates = []
for f, p in profile.items():
    if f in matched_folios: continue  # only unmatched
    rel = {pref: (p[f'{pref}_frac'] - means[pref]) / means[pref] for pref in means}
    sorted_rel = sorted(rel.items(), key=lambda x: -x[1])
    top_pref, top_rel = sorted_rel[0]
    if top_rel >= 0.5:  # at least 50% above corpus mean
        candidates.append({
            'folio': f, 'top_prefix': top_pref, 'top_rel': top_rel,
            'rates': {pref: p[f'{pref}_frac'] for pref in means},
            'all_ranks': sorted_rel,
        })

candidates.sort(key=lambda x: -x['top_rel'])

print("="*78)
print("UNMATCHED FOLIOS WITH STRONG O-PREFIX DOMINANCE (top rel >= +0.5)")
print("="*78)
print()
print(f"{'Folio':>7s}  {'Top':>4s}  {'Rel':>6s}  {'ok%':>5s}  {'ot%':>5s}  {'ol%':>5s}  {'or%':>5s}")
print("-"*60)
for c in candidates:
    r = c['rates']
    print(f"  {c['folio']:>5s}  {c['top_prefix']:>4s}  {c['top_rel']:>+6.2f}  "
          f"{r['ok']*100:>4.1f}%  {r['ot']*100:>4.1f}%  "
          f"{r['ol']*100:>4.1f}%  {r['or']*100:>4.1f}%")

# Step 2: Group candidates by predicted channel-class
candidates_by_pref = defaultdict(list)
for c in candidates:
    candidates_by_pref[c['top_prefix']].append(c['folio'])

print()
print(f"Total unmatched candidates: {len(candidates)}")
for pref in ('ok', 'ot', 'ol', 'or'):
    n = len(candidates_by_pref[pref])
    print(f"  {pref}-dominant unmatched: {n} folios")

# Step 3: Auto-classify unmatched PL Testamentum chapters
TIER_KEYWORDS = {
    'ol': ['vexell', 'vexel', 'cap', 'alembic', 'alambic', 'cubertor', 'cucurbit',
           'cendres', 'bany', 'balne', 'apparel', 'condensori', 'distillatori',
           'ampolla', 'recipient', 'continensa'],
    'ot': ['vegades', 'distill', 'distil', 'reitera', 'sublim', 'cohob',
           'separar', 'separa', 'transfere', 'goter', 'gota'],
    'ok': ['foch', 'calor', 'calid', 'igne', 'fire', 'ignis', 'fervor',
           'calcin', 'foco', 'temperat', 'lent', 'lauger'],
    'or': ['tinctura', 'tintura', 'colors', 'rubi', 'roig', 'blanc', 'verd',
           'final', 'compli', 'fini', 'perfeccio', 'projec'],
}

def classify_chapter_content(text):
    """Return dominant predicted o-prefix channel based on keyword density."""
    text_l = text.lower()
    scores = {}
    for pref, keywords in TIER_KEYWORDS.items():
        score = sum(text_l.count(kw) for kw in keywords)
        scores[pref] = score
    if not scores or max(scores.values()) == 0:
        return None, scores
    top = max(scores, key=lambda k: scores[k])
    return top, scores

# Process unmatched chapters
unmatched_chapters = []
for part_name, part_data in corpus['parts'].items():
    for ch in part_data['chapters']:
        if (part_name, ch['chapter_num']) in matched_chapters: continue
        text = ' '.join((p.get('catalan') or '') + ' ' + (p.get('latin') or '')
                        for p in ch.get('paragraphs', []))
        if not text.strip(): continue
        dominant, scores = classify_chapter_content(text)
        if dominant:
            unmatched_chapters.append({
                'part': part_name, 'num': ch['chapter_num'],
                'title': (ch.get('title_catalan') or '')[:80],
                'dominant': dominant, 'scores': scores,
            })

print()
print("="*78)
print(f"UNMATCHED PL CHAPTERS: {len(unmatched_chapters)}")
print("="*78)
chap_by_dominant = defaultdict(list)
for ch in unmatched_chapters:
    chap_by_dominant[ch['dominant']].append(ch)
for pref in ('ok', 'ot', 'ol', 'or'):
    n = len(chap_by_dominant[pref])
    print(f"  {pref}-dominant unmatched chapters: {n}")

# Step 4: Predictive concordance
# For each unmatched folio with channel-class X, find chapters with
# matching channel-class. Compare to base rate.
print()
print("="*78)
print("PREDICTIVE CONCORDANCE")
print("="*78)
print()
print("Predicted: unmatched X-dominant folios should preferentially match")
print("X-dominant unmatched chapters.")
print()

# Per-channel match rates
total_chapters = len(unmatched_chapters)
print(f"Chapter base rates (P(chapter is X-dominant)):")
for pref in ('ok', 'ot', 'ol', 'or'):
    rate = len(chap_by_dominant[pref]) / total_chapters
    print(f"  {pref}: {rate*100:.1f}%")

print()
print("Folio dominance distribution:")
for pref in ('ok', 'ot', 'ol', 'or'):
    n = len(candidates_by_pref[pref])
    print(f"  {pref}: {n} folios")

# Sample candidate matches
print()
print("="*78)
print("TOP CANDIDATES WITH PREDICTED MATCHES")
print("="*78)
print()
for c in candidates[:8]:
    f = c['folio']
    pref = c['top_prefix']
    matching = chap_by_dominant.get(pref, [])
    print(f"\n--- {f} ({pref}-dominant, rel={c['top_rel']:+.2f})")
    print(f"  Folio rates: " + ", ".join(f"{k}={v*100:.1f}%" for k, v in c['rates'].items()))
    print(f"  C1962 prediction: this folio should match a recipe emphasizing "
          f"{'vessel-content state' if pref == 'ol' else 'transfer/iteration' if pref == 'ot' else 'thermal regime' if pref == 'ok' else 'outcome/completion'}")
    print(f"  {pref}-dominant unmatched chapters available: {len(matching)}")
    if matching:
        # Show top 3 by score
        top_matches = sorted(matching, key=lambda x: -x['scores'][pref])[:3]
        for m in top_matches:
            print(f"    -> {m['part']}.{m['num']}: {m['title']} (score={m['scores'][pref]})")

# Save
import os
os.makedirs('scratch', exist_ok=True)
with open('scratch/c1962_out_of_sample.json', 'w') as f:
    json.dump({
        'candidates': candidates,
        'unmatched_chapters': unmatched_chapters,
        'chapters_by_dominant': {k: len(v) for k, v in chap_by_dominant.items()},
    }, f, indent=2, default=str)
print()
print("Saved: scratch/c1962_out_of_sample.json")
