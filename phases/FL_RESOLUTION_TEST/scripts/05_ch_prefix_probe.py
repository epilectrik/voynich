"""
FL RESOLUTION TEST 5: ch-Prefix Probe

Rerun Tests 1-3 for ch-prefixed FL tokens only.
Reason: ch has known precision semantics (C412, C929), weak dampening signals.

If ch-FL shows stronger token-level effects -> precision assessment mode
If not -> no prefix-specific semantics
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

STRONG_FWD = {'f26v','f76v','f112r','f82r','f115v','f85r2','f105r','f108v','f94r','f95v2','f106r'}
LINK_CLASS = 29

tx = Transcript()
morph = Morphology()

line_tokens = defaultdict(list)
for t in tx.currier_b():
    if t.folio in STRONG_FWD:
        line_tokens[(t.folio, t.line)].append(t)

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

annotated_lines = {}
for key, tokens in line_tokens.items():
    annotated_lines[key] = [annotate(t.word) for t in tokens]

WINDOW = 2
N_SHUFFLES = 1000
rng = np.random.default_rng(42)
STAGE_NAMES = ['INIT', 'EARL', 'MEDI', 'LATE', 'FINL', 'TERM']

print("=" * 80, flush=True)
print("FL RESOLUTION TEST 5: ch-PREFIX PROBE", flush=True)
print("=" * 80, flush=True)

# =============================================
# Collect pairs for ch-FL only
# =============================================
ch_pairs = []
for key, annots in annotated_lines.items():
    for idx, a in enumerate(annots):
        if not a['is_fl'] or a['prefix'] != 'ch':
            continue
        fl_stage = a['stage']

        for offset in range(-WINDOW, WINDOW + 1):
            if offset == 0:
                continue
            j = idx + offset
            if 0 <= j < len(annots):
                b = annots[j]
                if not b['is_fl'] and b['role'] != 'UNK':
                    ch_pairs.append({
                        'fl_stage': fl_stage,
                        'nb_middle': b['middle'],
                        'nb_role': b['role'],
                        'nb_prefix': b['prefix'],
                        'nb_suffix': b.get('suffix', '_none'),
                        'line_key': key,
                    })

print(f"  ch-FL neighbor pairs: {len(ch_pairs)}", flush=True)

ch_fl_count = sum(1 for key, annots in annotated_lines.items()
                  for a in annots if a['is_fl'] and a['prefix'] == 'ch')
print(f"  ch-FL tokens total: {ch_fl_count}", flush=True)

# Stage distribution for ch-FL
ch_stage_dist = Counter()
for key, annots in annotated_lines.items():
    for a in annots:
        if a['is_fl'] and a['prefix'] == 'ch':
            ch_stage_dist[a['stage']] += 1
print(f"  ch-FL stage distribution: {dict(sorted(ch_stage_dist.items()))}", flush=True)

if len(ch_pairs) < 20:
    print(f"\n  INSUFFICIENT DATA for ch-prefix probe. SKIPPING.", flush=True)
else:
    # =============================================
    # TEST 5A: ch-FL Stage vs Neighbor MIDDLE (variant selection)
    # =============================================
    print(f"\n{'='*70}", flush=True)
    print("5A. ch-FL STAGE vs NEIGHBOR MIDDLE (variant selection)", flush=True)
    print(f"{'='*70}", flush=True)

    ch_fl_s = [p['fl_stage'] for p in ch_pairs if p['nb_middle']]
    ch_nb_m = [p['nb_middle'] for p in ch_pairs if p['nb_middle']]

    if len(set(ch_fl_s)) >= 2 and len(set(ch_nb_m)) >= 2:
        real_nmi = normalized_mutual_info_score(ch_fl_s, ch_nb_m)

        shuf_nmis = []
        for _ in range(N_SHUFFLES):
            shuf_s = list(ch_fl_s)
            rng.shuffle(shuf_s)
            shuf_nmis.append(normalized_mutual_info_score(shuf_s, ch_nb_m))

        p_val = sum(1 for s in shuf_nmis if s >= real_nmi) / N_SHUFFLES
        pctile = sum(1 for s in shuf_nmis if s < real_nmi) / N_SHUFFLES * 100
        print(f"  NMI: {real_nmi:.6f}  shuffle: {np.mean(shuf_nmis):.6f}+/-{np.std(shuf_nmis):.6f}", flush=True)
        print(f"  Percentile: {pctile:.1f}th  p={p_val:.4f}", flush=True)
        sig = "PASS" if p_val < 0.001 else "weak" if p_val < 0.05 else "FAIL"
        print(f"  Verdict: {sig}", flush=True)
    else:
        print(f"  Insufficient variance for NMI", flush=True)

    # =============================================
    # TEST 5B: ch-FL distance to LINK
    # =============================================
    print(f"\n{'='*70}", flush=True)
    print("5B. ch-FL DISTANCE TO LINK", flush=True)
    print(f"{'='*70}", flush=True)

    ch_link_dists = []
    other_fl_link_dists = []

    for key, annots in annotated_lines.items():
        link_pos = [i for i, a in enumerate(annots) if a['cls'] == LINK_CLASS and not a['is_fl']]
        if not link_pos:
            continue
        for i, a in enumerate(annots):
            if a['is_fl']:
                min_dist = min(abs(i - lp) for lp in link_pos)
                if a['prefix'] == 'ch':
                    ch_link_dists.append(min_dist)
                else:
                    other_fl_link_dists.append(min_dist)

    if ch_link_dists and other_fl_link_dists:
        print(f"  ch-FL mean dist to LINK: {np.mean(ch_link_dists):.2f} (n={len(ch_link_dists)})", flush=True)
        print(f"  other-FL mean dist to LINK: {np.mean(other_fl_link_dists):.2f} (n={len(other_fl_link_dists)})", flush=True)
    else:
        print(f"  Insufficient LINK co-occurrence data", flush=True)

    # =============================================
    # TEST 5C: ch-FL Stage vs Neighbor SUFFIX
    # =============================================
    print(f"\n{'='*70}", flush=True)
    print("5C. ch-FL STAGE vs NEIGHBOR SUFFIX", flush=True)
    print(f"{'='*70}", flush=True)

    ch_suf_pairs = [(p['fl_stage'], p['nb_suffix']) for p in ch_pairs
                     if p['nb_suffix'] and p['nb_role'] != 'CORE_CONTROL']

    if len(ch_suf_pairs) >= 20:
        ch_fl_s2 = [s for s, _ in ch_suf_pairs]
        ch_nb_suf = [su for _, su in ch_suf_pairs]

        if len(set(ch_fl_s2)) >= 2 and len(set(ch_nb_suf)) >= 2:
            real_nmi_suf = normalized_mutual_info_score(ch_fl_s2, ch_nb_suf)

            shuf_nmis_suf = []
            for _ in range(N_SHUFFLES):
                shuf_s = list(ch_fl_s2)
                rng.shuffle(shuf_s)
                shuf_nmis_suf.append(normalized_mutual_info_score(shuf_s, ch_nb_suf))

            p_val_suf = sum(1 for s in shuf_nmis_suf if s >= real_nmi_suf) / N_SHUFFLES
            print(f"  NMI(ch-stage, suffix): {real_nmi_suf:.6f}  shuffle: {np.mean(shuf_nmis_suf):.6f}", flush=True)
            print(f"  p={p_val_suf:.4f}", flush=True)
        else:
            print(f"  Insufficient variance", flush=True)
    else:
        print(f"  Insufficient data (n={len(ch_suf_pairs)})", flush=True)

    # Compare ch vs all-FL effect sizes
    print(f"\n{'='*70}", flush=True)
    print("COMPARISON: ch-FL vs ALL-FL EFFECT SIZES", flush=True)
    print(f"{'='*70}", flush=True)

    # All-FL variant NMI for comparison
    all_pairs = []
    for key, annots in annotated_lines.items():
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
                        all_pairs.append((a['stage'], b['middle']))

    if all_pairs:
        all_s = [s for s, _ in all_pairs]
        all_m = [m for _, m in all_pairs]
        all_nmi = normalized_mutual_info_score(all_s, all_m)
        print(f"  ALL-FL NMI(stage, neighbor_middle): {all_nmi:.6f} (n={len(all_pairs)})", flush=True)
        if len(ch_fl_s) >= 2 and len(ch_nb_m) >= 2:
            print(f"  ch-FL NMI(stage, neighbor_middle):  {real_nmi:.6f} (n={len(ch_fl_s)})", flush=True)
            if real_nmi > all_nmi * 1.5:
                print(f"  -> ch-FL shows STRONGER variant selection than average", flush=True)
            elif real_nmi < all_nmi * 0.5:
                print(f"  -> ch-FL shows WEAKER variant selection than average", flush=True)
            else:
                print(f"  -> ch-FL shows similar effect size to all-FL", flush=True)

print(flush=True)
