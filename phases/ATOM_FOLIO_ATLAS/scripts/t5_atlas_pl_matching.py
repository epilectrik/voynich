"""
T5: Atlas-based PL chapter matching using atomize()-corrected features.

Replaces Phase 628's 8D residual matching with atlas-derived features.
Uses PL chapter operational profiles (from source text) matched against
folio atlas profiles (from atomize()).

PL-side features (from chapter text):
  - heat_density: heat term count / chapter lines
  - monitoring_density: monitoring term count / chapter lines
  - termination_density: termination term count / chapter lines
  - correction_density: correction term count / chapter lines
  - cipher_density: cipher letter count / chapter lines
  - chapter_length: number of lines (complexity proxy)

V-side features (from atlas):
  - qo_pct: thermal prefix rate
  - ch_pct + sh_pct: monitoring rate
  - gentle_ratio: e-depth ratio (balneum signature)
  - dar + dal: material/specification operations
  - dark_unique: identification vocabulary size
  - k_pct, e_pct: HEAD distribution

Matching: for each PL chapter, find the folio whose operational profile
best matches the chapter's expected profile. Validate with permutation test.
"""

import sys, io, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

# Load atlas
with open(ROOT / 'phases' / 'ATOM_FOLIO_ATLAS' / 'results' / 'folio_atlas.json', encoding='utf-8') as f:
    atlas = json.load(f)

# Load PL structural profile
with open(ROOT / 'phases' / 'PSEUDO_LULL_CHARACTERIZATION' / 'results' / 'pseudo_lull_structural_profile.json', encoding='utf-8') as f:
    pl_profile = json.load(f)

# Load PL text
with open(ROOT / 'sources' / 'pseudo_lull_testamentum' / 'testamentum_complete_english.txt', encoding='utf-8') as f:
    en_lines = f.read().split('\n')

pl_chapters = pl_profile['E1_chapters']
print(f"Atlas: {len(atlas)} folios")
print(f"PL chapters: {len(pl_chapters)}")
print(f"PL text: {len(en_lines)} lines")

# ═══ PL CHAPTER FEATURES ═══
# Derive operational features from chapter metadata + text content

def chapter_features(ch):
    """Extract operational features from a PL chapter."""
    n_lines = ch['en_line_end'] - ch['en_line_start']
    if n_lines <= 0:
        n_lines = 1

    # From pre-extracted profile
    heat = ch.get('heat_count', 0) / n_lines
    monitoring = ch.get('monitoring_count', 0) / n_lines
    termination = ch.get('termination_count', 0) / n_lines
    correction = ch.get('correction_count', 0) / n_lines
    cipher = ch.get('cipher_count', 0) / n_lines
    judgment = ch.get('judgment_count', 0) / n_lines

    # From chapter text — count specific operational keywords
    text = '\n'.join(en_lines[ch['en_line_start']:ch['en_line_end']]).lower()

    # Balneum/bath references
    balneum = len(re.findall(r'balneum|bath|bain|balneo', text))
    # Distillation references
    distill = len(re.findall(r'distill|alembic|cucurbit', text))
    # Sublimation references
    sublim = len(re.findall(r'sublim|ascend|volatile', text))
    # Fixation references
    fix = len(re.findall(r'fix|fixat|immobil', text))
    # Dissolution references
    dissolv = len(re.findall(r'dissolv|solut|resolut', text))
    # Fermentation references
    ferment = len(re.findall(r'ferment', text))
    # Color monitoring (nigredo/albedo/rubedo)
    color = len(re.findall(r'black|white|red|color|colour|nigr|alb|rub', text))
    # Iteration references
    iterate = len(re.findall(r'repeat|reiter|again|times|iterate', text))
    # Fire degree references
    fire = len(re.findall(r'fire|flame|ash|gentle|strong|moderate|fierce', text))

    return {
        'heat_d': heat,
        'monitor_d': monitoring,
        'term_d': termination,
        'correct_d': correction,
        'cipher_d': cipher,
        'judgment_d': judgment,
        'balneum': balneum / n_lines,
        'distill': distill / n_lines,
        'sublim': sublim / n_lines,
        'fix': fix / n_lines,
        'dissolv': dissolv / n_lines,
        'ferment': ferment / n_lines,
        'color': color / n_lines,
        'iterate': iterate / n_lines,
        'fire': fire / n_lines,
        'n_lines': n_lines,
        'family': ch.get('primary_family', '?'),
        'part': ch.get('part', '?'),
        'tp': ch.get('theory_practice', '?'),
    }

# ═══ MAPPING: PL features -> V features ═══
# Each PL feature dimension maps to a V atlas feature

# PL heat_density -> V qo_pct (thermal operations)
# PL monitoring_density -> V (ch_pct + sh_pct) (monitoring)
# PL balneum -> V gentle_ratio (balneum = gentle heat)
# PL correction_density -> V (ok_pct + ot_pct) (correction/verification)
# PL iterate -> V dar (repeated operations involve material additions?)
# PL cipher_density -> V dark_unique (cipher letters ~ identification vocabulary)
# PL n_lines -> V n_tokens (chapter size ~ folio size)

def pl_to_v_distance(pl_feat, v_entry):
    """Compute distance between PL chapter features and V folio atlas entry."""
    # Normalize PL features to roughly same scale as V percentages
    # PL densities are typically 0-1 per line; V features are 0-40% range

    d = 0
    # Heat: PL heat_density -> V qo_pct
    pl_heat = pl_feat['heat_d'] * 40 + pl_feat['fire'] * 20  # scale to ~V range
    d += (pl_heat - v_entry['qo_pct']) ** 2

    # Monitoring: PL monitor -> V (ch + sh)
    pl_mon = pl_feat['monitor_d'] * 40 + pl_feat['color'] * 15
    v_mon = v_entry['ch_pct'] + v_entry['sh_pct']
    d += (pl_mon - v_mon) ** 2

    # Balneum: PL balneum -> V gentle_ratio
    pl_bal = pl_feat['balneum'] * 100
    v_gentle = v_entry['gentle_ratio'] * 100
    d += (pl_bal - v_gentle) ** 2 * 0.5  # downweight — sparse feature

    # Correction: PL correction -> V (ok + ot)
    pl_corr = pl_feat['correct_d'] * 30
    v_corr = v_entry['ok_pct'] + v_entry['ot_pct']
    d += (pl_corr - v_corr) ** 2

    # Complexity: PL lines -> V tokens (normalized)
    pl_size = pl_feat['n_lines'] / 50 * 400  # normalize to V token range
    d += ((pl_size - v_entry['n_tokens']) / 100) ** 2  # scale down

    # Iteration/termination: PL terminate + iterate -> V dar count
    pl_iter = (pl_feat['term_d'] + pl_feat['iterate']) * 10
    d += (pl_iter - v_entry['dar']) ** 2 * 0.3

    return math.sqrt(d)


# ═══ MATCH ALL PRACTICAL MERCURIORUM CHAPTERS ═══
print("\n" + "=" * 110)
print("MATCHING: Practical Mercuriorum chapters -> V folios")
print("=" * 110)

# Get practical/mixed Mercuriorum chapters
merc_practical = [ch for ch in pl_chapters
                  if ch['part'] == 'Mercuriorum'
                  and ch.get('theory_practice') in ('practical', 'mixed')
                  and ch.get('primary_family') != 'theoretical']

print(f"\nPractical Mercuriorum chapters: {len(merc_practical)}")

# Also include Practica practical chapters
pract_practical = [ch for ch in pl_chapters
                   if ch['part'] == 'Practica'
                   and ch.get('theory_practice') in ('practical', 'mixed')
                   and ch.get('primary_family') != 'theoretical']
print(f"Practical Practica chapters: {len(pract_practical)}")

all_practical = merc_practical + pract_practical
print(f"Total practical chapters to match: {len(all_practical)}")

# All V folios as candidates (don't exclude matched — let it find them)
v_folios = sorted(atlas.keys())

# Match each chapter
results = []
for ch in sorted(all_practical, key=lambda c: c['en_line_start']):
    feat = chapter_features(ch)
    num = ch['number']
    fam = feat['family']
    part = feat['part']

    # Find top 3 matches
    dists = []
    for f in v_folios:
        d = pl_to_v_distance(feat, atlas[f])
        dists.append((f, d))
    dists.sort(key=lambda x: x[1])

    top1_f, top1_d = dists[0]
    top2_f, top2_d = dists[1]
    top3_f, top3_d = dists[2]
    ratio = top2_d / top1_d if top1_d > 0 else 0

    results.append({
        'chapter': num, 'part': part, 'family': fam,
        'n_lines': feat['n_lines'],
        'top1': top1_f, 'dist1': top1_d,
        'top2': top2_f, 'dist2': top2_d,
        'ratio': ratio,
        'confident': ratio > 1.15,
        'heat_d': feat['heat_d'], 'monitor_d': feat['monitor_d'],
        'balneum': feat['balneum'],
    })

# Print results
print(f"\n{'Ch':>4} {'Part':>12} {'Family':>15} {'Lines':>5} {'Top1':>8} {'Dist':>7} "
      f"{'Top2':>8} {'Dist2':>7} {'Ratio':>6} {'Conf':>5}")
print("-" * 100)

for r in results:
    conf = 'Y' if r['confident'] else ''
    print(f"{r['chapter']:>4} {r['part']:>12} {r['family']:>15} {r['n_lines']:5d} "
          f"{r['top1']:>8} {r['dist1']:7.2f} {r['top2']:>8} {r['dist2']:7.2f} "
          f"{r['ratio']:6.3f} {conf:>5}")

# ═══ CHECK PHASE 628 CONCORDANCE ═══
print("\n\n" + "=" * 110)
print("PHASE 628 CONCORDANCE: Do old matches still hold?")
print("=" * 110)

phase628_matches = {
    19: 'f75r', 18: 'f76r', 27: 'f77v', 14: 'f84r', 16: 'f108r',
    24: 'f84v', 9: 'f83r', 11: 'f112r',
}

concordant = 0
total_628 = 0
for r in results:
    ch = r['chapter']
    if ch in phase628_matches:
        expected = phase628_matches[ch]
        match = r['top1'] == expected
        if match: concordant += 1
        total_628 += 1
        print(f"  Ch{ch}: Phase 628={expected}, Atlas={r['top1']} "
              f"{'MATCH' if match else 'DIFFERENT'} (dist={r['dist1']:.2f})")

print(f"\n  Concordance: {concordant}/{total_628} ({100*concordant/total_628:.0f}%)" if total_628 > 0 else "")

# ═══ PERMUTATION TEST ═══
print("\n\n" + "=" * 110)
print("PERMUTATION TEST: Are matches better than random?")
print("=" * 110)

random.seed(42)
real_mean_ratio = sum(r['ratio'] for r in results) / len(results)
real_confident = sum(1 for r in results if r['confident'])

N_PERM = 1000
perm_ratios = []
perm_confidents = []

for _ in range(N_PERM):
    # Shuffle chapter features among chapters (keep folio atlas fixed)
    shuffled_feats = [chapter_features(ch) for ch in all_practical]
    random.shuffle(shuffled_feats)

    perm_results = []
    for feat in shuffled_feats:
        dists = [(f, pl_to_v_distance(feat, atlas[f])) for f in v_folios]
        dists.sort(key=lambda x: x[1])
        ratio = dists[1][1] / dists[0][1] if dists[0][1] > 0 else 0
        perm_results.append(ratio)

    perm_ratios.append(sum(perm_results) / len(perm_results))
    perm_confidents.append(sum(1 for r in perm_results if r > 1.15))

perm_mean_ratio = sum(perm_ratios) / len(perm_ratios)
p_ratio = sum(1 for pr in perm_ratios if pr >= real_mean_ratio) / N_PERM
p_conf = sum(1 for pc in perm_confidents if pc >= real_confident) / N_PERM

print(f"\n  Real mean ratio: {real_mean_ratio:.3f}")
print(f"  Null mean ratio: {perm_mean_ratio:.3f}")
print(f"  p (ratio): {p_ratio:.3f}")
print(f"\n  Real confident matches: {real_confident}/{len(results)}")
print(f"  Null confident matches: {sum(perm_confidents)/len(perm_confidents):.1f}")
print(f"  p (confident): {p_conf:.3f}")

if p_ratio < 0.05 and p_conf < 0.05:
    print(f"\n  PASS: Matching is significantly better than random")
elif p_ratio < 0.05 or p_conf < 0.05:
    print(f"\n  PARTIAL: One metric significant, one not")
else:
    print(f"\n  FAIL: Matching not distinguishable from random")

# ═══ NEW MATCHES (not in Phase 628) ═══
print("\n\n" + "=" * 110)
print("NEW CONFIDENT MATCHES (not in Phase 628)")
print("=" * 110)

for r in results:
    if r['confident'] and r['chapter'] not in phase628_matches:
        e = atlas[r['top1']]
        print(f"\n  Ch{r['chapter']} ({r['family']}, {r['part']}) -> {r['top1']}")
        print(f"    Ratio: {r['ratio']:.3f}, Distance: {r['dist1']:.2f}")
        print(f"    Folio: sec={e['section']} type={e['doc_type']} qo={e['qo_pct']}% "
              f"ch={e['ch_pct']}% gentle={100*e['gentle_ratio']:.0f}% dar={e['dar']} dal={e['dal']}")
        print(f"    Chapter: {r['n_lines']}L, heat={r['heat_d']:.2f}/L, "
              f"monitor={r['monitor_d']:.2f}/L, balneum={r['balneum']:.2f}/L")

# Save results
out = {
    'matches': results,
    'concordance': {'matched': concordant, 'total': total_628},
    'permutation': {
        'real_mean_ratio': real_mean_ratio,
        'null_mean_ratio': perm_mean_ratio,
        'p_ratio': p_ratio,
        'real_confident': real_confident,
        'p_confident': p_conf,
    }
}
out_path = ROOT / 'phases' / 'ATOM_FOLIO_ATLAS' / 'results' / 't5_matching.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
print(f"\nSaved: {out_path}")

print(f"\n{'=' * 110}")
print("DONE")
print(f"{'=' * 110}")
