"""
FL RESOLUTION TEST 6: Section T Diagnostic

Hypothesis H4: Section T lacks FL gradient because it suppresses
assessment output, not because execution differs.

Rerun Tests 1-3 within Section T only. Compare effect sizes to S/B.
Absence does NOT falsify FL globally - it localizes architectural variation.
"""
import sys, json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy.stats import chi2_contingency, spearmanr
from sklearn.metrics import normalized_mutual_info_score

sys.path.insert(0, str(Path('C:/git/voynich').resolve()))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': 0, 'i': 0, 'in': 1, 'r': 2, 'ar': 2,
    'al': 3, 'l': 3, 'ol': 3, 'o': 4, 'ly': 4, 'am': 4,
    'm': 5, 'dy': 5, 'ry': 5, 'y': 5,
}
FL_MIDDLES = set(FL_STAGE_MAP.keys())

CLASS_MAP_PATH = Path('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json')
with open(CLASS_MAP_PATH, 'r', encoding='utf-8') as f:
    class_data = json.load(f)
TOKEN_TO_ROLE = class_data.get('token_to_role', {})
TOKEN_TO_CLASS = {k: int(v) for k, v in class_data.get('token_to_class', {}).items()}

LINK_CLASS = 29

tx = Transcript()
morph = Morphology()

# Collect Section T tokens (Currier B only)
section_t_tokens = defaultdict(list)
section_sb_tokens = defaultdict(list)

STRONG_FWD = {'f26v','f76v','f112r','f82r','f115v','f85r2','f105r','f108v','f94r','f95v2','f106r'}

for t in tx.currier_b():
    if t.section == 'T':
        section_t_tokens[(t.folio, t.line)].append(t)
    elif t.folio in STRONG_FWD:
        section_sb_tokens[(t.folio, t.line)].append(t)

def annotate(word):
    m = morph.extract(word)
    if not m:
        return {'word': word, 'is_fl': False, 'stage': None, 'prefix': None,
                'middle': None, 'suffix': None,
                'role': TOKEN_TO_ROLE.get(word, 'UNK'),
                'cls': TOKEN_TO_CLASS.get(word, -1)}
    is_fl = m.middle is not None and m.middle in FL_MIDDLES
    prefix = m.prefix if m.prefix else '_'
    stage = FL_STAGE_MAP.get(m.middle) if is_fl else None
    suffix = m.suffix if m.suffix else '_none'
    return {'word': word, 'is_fl': is_fl, 'stage': stage, 'prefix': prefix,
            'middle': m.middle, 'suffix': suffix,
            'role': TOKEN_TO_ROLE.get(word, 'UNK'),
            'cls': TOKEN_TO_CLASS.get(word, -1)}

WINDOW = 2
N_SHUFFLES = 1000
rng = np.random.default_rng(42)
STAGE_NAMES = ['INIT', 'EARL', 'MEDI', 'LATE', 'FINL', 'TERM']

print("=" * 80, flush=True)
print("FL RESOLUTION TEST 6: SECTION T DIAGNOSTIC", flush=True)
print("=" * 80, flush=True)

# =============================================
# Basic profile of Section T
# =============================================
t_annotated = {}
for key, tokens in section_t_tokens.items():
    t_annotated[key] = [annotate(t.word) for t in tokens]

t_fl_count = sum(1 for annots in t_annotated.values() for a in annots if a['is_fl'])
t_total = sum(len(annots) for annots in t_annotated.values())
t_fl_rate = t_fl_count / t_total if t_total > 0 else 0

sb_fl_count = sum(1 for tokens in section_sb_tokens.values()
                  for t in tokens
                  for m_result in [morph.extract(t.word)]
                  if m_result and m_result.middle and m_result.middle in FL_MIDDLES)
sb_total = sum(len(tokens) for tokens in section_sb_tokens.values())
sb_fl_rate = sb_fl_count / sb_total if sb_total > 0 else 0

print(f"\n  Section T: {t_total} tokens, {t_fl_count} FL ({t_fl_rate*100:.1f}%)", flush=True)
print(f"  Section S/B (strong-fwd): {sb_total} tokens, {sb_fl_count} FL ({sb_fl_rate*100:.1f}%)", flush=True)
print(f"  Section T lines: {len(t_annotated)}", flush=True)
print(f"  Section T folios: {len(set(k[0] for k in t_annotated))}", flush=True)

# FL stage distribution in T
t_stage_dist = Counter()
for annots in t_annotated.values():
    for a in annots:
        if a['is_fl']:
            t_stage_dist[a['stage']] += 1
print(f"  Section T FL stages: {dict(sorted(t_stage_dist.items()))}", flush=True)

# FL prefix distribution in T
t_prefix_dist = Counter()
for annots in t_annotated.values():
    for a in annots:
        if a['is_fl']:
            t_prefix_dist[a['prefix']] += 1
print(f"  Section T FL prefixes: {dict(t_prefix_dist.most_common(10))}", flush=True)

if t_fl_count < 20:
    print(f"\n  INSUFFICIENT FL DATA IN SECTION T ({t_fl_count} tokens). Limited analysis.", flush=True)

# =============================================
# 6A: FL Stage vs Neighbor MIDDLE in Section T
# =============================================
print(f"\n{'='*70}", flush=True)
print("6A. SECTION T: FL STAGE vs NEIGHBOR MIDDLE", flush=True)
print(f"{'='*70}", flush=True)

t_pairs = []
for key, annots in t_annotated.items():
    for idx, a in enumerate(annots):
        if not a['is_fl']:
            continue
        for offset in range(-WINDOW, WINDOW + 1):
            if offset == 0:
                continue
            j = idx + offset
            if 0 <= j < len(annots):
                b = annots[j]
                if not b['is_fl'] and b['middle'] and b['role'] != 'UNK':
                    t_pairs.append({
                        'fl_stage': a['stage'],
                        'fl_prefix': a['prefix'],
                        'nb_middle': b['middle'],
                        'nb_role': b['role'],
                        'nb_suffix': b.get('suffix', '_none'),
                    })

print(f"  Section T FL-neighbor pairs: {len(t_pairs)}", flush=True)

if len(t_pairs) >= 20:
    t_fl_s = [p['fl_stage'] for p in t_pairs]
    t_nb_m = [p['nb_middle'] for p in t_pairs]

    if len(set(t_fl_s)) >= 2 and len(set(t_nb_m)) >= 2:
        real_nmi_t = normalized_mutual_info_score(t_fl_s, t_nb_m)

        shuf_nmis_t = []
        for _ in range(N_SHUFFLES):
            shuf_s = list(t_fl_s)
            rng.shuffle(shuf_s)
            shuf_nmis_t.append(normalized_mutual_info_score(shuf_s, t_nb_m))

        p_val_t = sum(1 for s in shuf_nmis_t if s >= real_nmi_t) / N_SHUFFLES
        print(f"  NMI: {real_nmi_t:.6f}  shuffle: {np.mean(shuf_nmis_t):.6f}", flush=True)
        print(f"  p={p_val_t:.4f}", flush=True)
    else:
        print(f"  Insufficient variance for NMI", flush=True)
else:
    print(f"  Insufficient data", flush=True)

# =============================================
# 6B: FL-LINK distance in Section T
# =============================================
print(f"\n{'='*70}", flush=True)
print("6B. SECTION T: FL-LINK DISTANCE", flush=True)
print(f"{'='*70}", flush=True)

t_fl_link_dists = []
t_op_link_dists = []

for key, annots in t_annotated.items():
    link_pos = [i for i, a in enumerate(annots) if a['cls'] == LINK_CLASS and not a['is_fl']]
    if not link_pos:
        continue
    for i, a in enumerate(annots):
        min_dist = min(abs(i - lp) for lp in link_pos)
        if a['is_fl']:
            t_fl_link_dists.append(min_dist)
        elif a['role'] != 'UNK' and a['cls'] != LINK_CLASS:
            t_op_link_dists.append(min_dist)

if t_fl_link_dists:
    print(f"  T FL mean dist to LINK: {np.mean(t_fl_link_dists):.2f} (n={len(t_fl_link_dists)})", flush=True)
    print(f"  T OP mean dist to LINK: {np.mean(t_op_link_dists):.2f} (n={len(t_op_link_dists)})", flush=True)
else:
    print(f"  No FL-LINK co-occurrence in Section T", flush=True)

# =============================================
# 6C: FL Stage vs Suffix in Section T
# =============================================
print(f"\n{'='*70}", flush=True)
print("6C. SECTION T: FL STAGE vs NEIGHBOR SUFFIX", flush=True)
print(f"{'='*70}", flush=True)

t_suf_pairs = [(p['fl_stage'], p['nb_suffix']) for p in t_pairs
                if p['nb_suffix'] and p['nb_role'] != 'CORE_CONTROL']

if len(t_suf_pairs) >= 20:
    t_fl_s2 = [s for s, _ in t_suf_pairs]
    t_nb_suf = [su for _, su in t_suf_pairs]

    if len(set(t_fl_s2)) >= 2 and len(set(t_nb_suf)) >= 2:
        real_nmi_suf_t = normalized_mutual_info_score(t_fl_s2, t_nb_suf)

        shuf_nmis_suf_t = []
        for _ in range(N_SHUFFLES):
            shuf_s = list(t_fl_s2)
            rng.shuffle(shuf_s)
            shuf_nmis_suf_t.append(normalized_mutual_info_score(shuf_s, t_nb_suf))

        p_val_suf_t = sum(1 for s in shuf_nmis_suf_t if s >= real_nmi_suf_t) / N_SHUFFLES
        print(f"  NMI(stage, suffix): {real_nmi_suf_t:.6f}  shuffle: {np.mean(shuf_nmis_suf_t):.6f}", flush=True)
        print(f"  p={p_val_suf_t:.4f}", flush=True)
    else:
        print(f"  Insufficient variance", flush=True)
else:
    print(f"  Insufficient data (n={len(t_suf_pairs)})", flush=True)

# =============================================
# VERDICT
# =============================================
print(f"\n{'='*70}", flush=True)
print("VERDICT", flush=True)
print(f"{'='*70}", flush=True)

print(f"  Section T FL rate: {t_fl_rate*100:.1f}% (vs S/B: {sb_fl_rate*100:.1f}%)", flush=True)
if t_fl_count < 20:
    print(f"  -> Section T has too few FL tokens for meaningful testing", flush=True)
    print(f"  -> Consistent with FL suppression, but cannot distinguish from low sample", flush=True)
else:
    print(f"  -> Section T has enough FL for analysis", flush=True)
    print(f"  -> Compare effect sizes above to S/B results from Tests 1-3", flush=True)

print(flush=True)
