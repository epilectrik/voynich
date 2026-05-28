"""Discriminating test: does o-HEAD 'arrange' rate track plant morphological complexity?

PRE-REGISTERED (locked before running):
HYPOTHESIS: If o-HEAD 'arrange' encodes botanical spatial structure, then folios
with MORE morphological complexity (more distinct structural tags: root/leaf/flower/
composite) should have HIGHER o-HEAD rate.

TEST: Spearman correlation between (n morphology tags per folio) and (o-HEAD rate).
PASS: positive rho, p < 0.05.

SECONDARY: COMPOSITE folios (multiple plants = maximal spatial arrangement)
should have higher o-HEAD than single-plant folios.

NULL CONSIDERATION: control for folio token count (confound check).

CAVEAT: N=24 folios only (the blind morphology classification sample). Underpowered.
"""
import re
import sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr, mannwhitneyu

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# ===== Parse morphology classification table =====
morph_file = Path('C:/git/voynich/phases/PPC_program_plant_correlation/plant_morphology_classification.md').read_text(encoding='utf-8')
ALL_TAGS = ['ROOT_HEAVY', 'FLOWER_DOMINANT', 'LEAFY_HERB', 'WOODY_SHRUB', 'COMPOSITE', 'AMBIGUOUS']

folio_tags = {}
for line in morph_file.split('\n'):
    m = re.match(r'\|\s*\*\*(f\d+[rv]\d?)\*\*\s*\|\s*([A-Z_]+)\s*\|\s*([^|]*)\|', line)
    if m:
        folio = m.group(1)
        primary = m.group(2).strip()
        secondary_raw = m.group(3).strip()
        secondary = [t.strip() for t in secondary_raw.split(',') if t.strip() in ALL_TAGS]
        tags = set([primary] + secondary)
        tags = {t for t in tags if t in ALL_TAGS}
        folio_tags[folio] = tags

print(f'Parsed morphology for {len(folio_tags)} folios')

# ===== Get o-HEAD rate per folio =====
tx = Transcript(); morph = Morphology()
folio_head = defaultdict(Counter)
folio_total = Counter()
for t in tx.currier_a(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    try:
        a = morph.atomize(w)
    except Exception:
        continue
    folio_total[t.folio] += 1
    head = None
    if hasattr(a, 'atoms'):
        for c, r, _ in a.atoms:
            if r == 'HEAD':
                head = c
                break
    if head:
        folio_head[t.folio][head] += 1

# ===== Build paired data =====
data = []
for folio, tags in folio_tags.items():
    if folio_total.get(folio, 0) < 15:
        continue
    o_rate = folio_head[folio].get('o', 0) / folio_total[folio]
    n_tags = len(tags)
    is_composite = 'COMPOSITE' in tags
    # "structural richness" = has all 3 of root/leaf/flower
    full_structure = len({'ROOT_HEAVY', 'FLOWER_DOMINANT', 'LEAFY_HERB'} & tags)
    data.append({
        'folio': folio, 'o_rate': o_rate, 'n_tags': n_tags,
        'composite': is_composite, 'full_structure': full_structure,
        'n_tokens': folio_total[folio], 'tags': tags,
    })

print(f'Folios with both morphology + >=15 A tokens: {len(data)}')

# ===== TEST 1: tag-count vs o-rate correlation =====
print('\n=== TEST 1: n morphology tags vs o-HEAD rate ===')
tag_counts = np.array([d['n_tags'] for d in data])
o_rates = np.array([d['o_rate'] for d in data])
rho, p = spearmanr(tag_counts, o_rates)
print(f'  Spearman rho = {rho:+.3f}, p = {p:.4f} (n={len(data)})')
test1_pass = rho > 0 and p < 0.05
print(f'  TEST 1 VERDICT: {"PASS" if test1_pass else "FAIL"}')

# ===== TEST 2: full-structure count vs o-rate =====
print('\n=== TEST 2: root+leaf+flower count vs o-HEAD rate ===')
full_struct = np.array([d['full_structure'] for d in data])
rho2, p2 = spearmanr(full_struct, o_rates)
print(f'  Spearman rho = {rho2:+.3f}, p = {p2:.4f}')
test2_pass = rho2 > 0 and p2 < 0.05
print(f'  TEST 2 VERDICT: {"PASS" if test2_pass else "FAIL"}')

# ===== TEST 3: COMPOSITE vs non-composite o-rate =====
print('\n=== TEST 3: COMPOSITE (multi-plant) vs single-plant o-HEAD ===')
composite_o = [d['o_rate'] for d in data if d['composite']]
single_o = [d['o_rate'] for d in data if not d['composite']]
print(f'  COMPOSITE folios: n={len(composite_o)}, mean o-rate={np.mean(composite_o) if composite_o else 0:.3f}')
print(f'  Single-plant folios: n={len(single_o)}, mean o-rate={np.mean(single_o):.3f}')
if composite_o and single_o:
    u, p3 = mannwhitneyu(composite_o, single_o, alternative='greater')
    print(f'  Mann-Whitney (composite > single): p = {p3:.4f}')
    test3_pass = p3 < 0.05
else:
    test3_pass = False
    p3 = None
print(f'  TEST 3 VERDICT: {"PASS" if test3_pass else "FAIL/insufficient"}')

# ===== Confound check: token count vs o-rate =====
print('\n=== CONFOUND CHECK: folio token count vs o-HEAD rate ===')
toks = np.array([d['n_tokens'] for d in data])
rho_c, p_c = spearmanr(toks, o_rates)
print(f'  Spearman rho(tokens, o-rate) = {rho_c:+.3f}, p = {p_c:.4f}')
print(f'  (If significant, token count confounds the morphology correlation)')

# Show the data
print('\n=== Per-folio data (sorted by o-rate) ===')
data.sort(key=lambda d: -d['o_rate'])
print(f'{"Folio":<8} {"o-rate":>7} {"n_tags":>7} {"full":>5} {"comp":>5} {"toks":>5}  tags')
for d in data:
    comp = 'Y' if d['composite'] else ''
    print(f'{d["folio"]:<8} {d["o_rate"]:>7.3f} {d["n_tags"]:>7} {d["full_structure"]:>5} {comp:>5} {d["n_tokens"]:>5}  {sorted(d["tags"])}')

# ===== Verdict =====
print('\n' + '=' * 60)
print('=== VERDICT ===')
print('=' * 60)
print(f'Test 1 (tag-count corr):    {"PASS" if test1_pass else "FAIL"} (rho={rho:+.3f}, p={p:.3f})')
print(f'Test 2 (full-structure):    {"PASS" if test2_pass else "FAIL"} (rho={rho2:+.3f}, p={p2:.3f})')
print(f'Test 3 (composite):         {"PASS" if test3_pass else "FAIL"}')
n_pass = sum([test1_pass, test2_pass, test3_pass])
print(f'\nTotal: {n_pass}/3')
if n_pass >= 2:
    print('SUPPORTED: o-HEAD "arrange" rate tracks botanical morphological complexity.')
    print('The arrangement-vocabulary-encodes-plant-structure hypothesis gains support.')
elif n_pass == 1:
    print('WEAK: one test positive; suggestive but underpowered (N=24).')
else:
    print('NOT SUPPORTED: o-HEAD rate does not track plant morphological complexity.')
    print('"Arrangement" is more likely staging/organization than botanical spatial structure.')
