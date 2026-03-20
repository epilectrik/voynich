"""Gallows Sequential Properties Analysis

For each gallows type (k/t/p/f), test whether paragraphs of that type
show sequential dependencies within folios -- body similarity chains,
run clustering, drift patterns, reset/continuation behavior.

Core question: Is one gallows type the "main program body" with sequential
flow, while others are interventions that interrupt the sequence?

Tests:
  S1: Same-type run clustering (are same-type paras adjacent more than chance?)
  S2: Within-folio same-type body cohesion (same-type more similar than cross-type?)
  S3: Consecutive body similarity (does para N predict para N+1? by gallows type)
  S4: Sequential body drift (does occurrence 1,2,3... of type X show systematic change?)
  S5: Reset detection (after type X, is the next para more/less predictable from the previous?)
  S6: Cross-paragraph gallows prediction (does para N's body predict para N+1's gallows?)
  S7: Category/kernel profile continuity per gallows type
"""
import sys, json, warnings
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import mannwhitneyu, spearmanr, chi2_contingency, pearsonr, kruskal

warnings.filterwarnings('ignore')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, BFolioDecoder, Morphology, CategoryClassifier

tx = Transcript()
decoder = BFolioDecoder()
morph = Morphology()
cc = CategoryClassifier()

ALL_ATOMS = sorted('kehtpfdscigolamynr')
GALLOWS_SET = set('ktpf')
GALLOWS_TYPES = ['k', 't', 'p', 'f']
CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']

def cosine_sim(a, b):
    """Cosine similarity between two vectors."""
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))

def atom_vec(atom_counts, total):
    """Convert atom counter to fraction vector over ALL_ATOMS."""
    if total == 0:
        return np.zeros(len(ALL_ATOMS))
    return np.array([atom_counts.get(a, 0) / total for a in ALL_ATOMS])

def cat_vec(cat_counts):
    """Convert category counter to fraction vector."""
    total = sum(cat_counts.values())
    if total == 0:
        return np.zeros(len(CATEGORIES))
    return np.array([cat_counts.get(c, 0) / total for c in CATEGORIES])

def kernel_vec(kd):
    """Convert kernel dist to [k_frac, h_frac, e_frac]."""
    total = sum(kd.values())
    if total == 0:
        return np.zeros(3)
    return np.array([kd.get('k', 0) / total, kd.get('h', 0) / total, kd.get('e', 0) / total])

# ============================================================
# DATA COLLECTION
# ============================================================
print("Collecting paragraph data...")

folio_sections = {}
for tok in tx.currier_b():
    if tok.folio not in folio_sections:
        folio_sections[tok.folio] = tok.section
folios = sorted(folio_sections.keys())

SECTION_MAP = {'S': 'Stars', 'B': 'Bio', 'H': 'Herbal', 'T': 'Cosmo', 'C': 'Cosmo'}

# Build ordered paragraph records per folio
folio_paras = {}  # fid -> [list of para records in order]

for fid in folios:
    sec = SECTION_MAP.get(folio_sections[fid], folio_sections[fid])
    paragraphs = decoder.analyze_folio_paragraphs(fid)
    records = []

    for i, para in enumerate(paragraphs):
        bt = para.boundary_token or ''
        gtype = bt[0] if bt and bt[0] in GALLOWS_SET else 'none'

        # Body atoms (skip gallows-initial token)
        body_atoms = Counter()
        body_total = 0
        cat_counts = Counter()
        first_skipped = False
        for line in para.lines:
            for tok in line.tokens:
                if not first_skipped:
                    first_skipped = True
                    continue
                if tok.morph and tok.morph.middle:
                    mid = tok.morph.middle
                    for ch in mid:
                        if ch in set('kehtpfdscigolamynr'):
                            body_atoms[ch] += 1
                            body_total += 1
                    cat = cc.classify(mid)
                    if cat:
                        cat_counts[cat] += 1

        if para.token_count < 3 or body_total == 0:
            continue

        records.append({
            'gallows': gtype,
            'section': sec,
            'folio': fid,
            'ordinal': i,
            'body_atoms': dict(body_atoms),
            'body_total': body_total,
            'atom_vec': atom_vec(body_atoms, body_total),
            'cat_counts': dict(cat_counts),
            'cat_vec': cat_vec(cat_counts),
            'kernel_dist': dict(para.kernel_dist),
            'kernel_vec': kernel_vec(para.kernel_dist),
            'token_count': para.token_count,
            'line_count': para.line_count,
            'escape_lines': para.escape_lines,
            'terminal_lines': para.terminal_lines,
        })

    if records:
        folio_paras[fid] = records

# Summary
total_paras = sum(len(v) for v in folio_paras.values())
gtype_counts = Counter()
for recs in folio_paras.values():
    for r in recs:
        gtype_counts[r['gallows']] += 1
print(f"  {total_paras} paragraphs across {len(folio_paras)} folios")
print(f"  By type: {dict(gtype_counts)}")

# Only gallows-initial paragraphs for most tests
folio_gallows_paras = {}
for fid, recs in folio_paras.items():
    gp = [r for r in recs if r['gallows'] != 'none']
    if gp:
        folio_gallows_paras[fid] = gp

n_gallows = sum(len(v) for v in folio_gallows_paras.values())
print(f"  {n_gallows} gallows-initial paragraphs in {len(folio_gallows_paras)} folios")

results = {'meta': {
    'total_paras': total_paras,
    'gallows_paras': n_gallows,
    'by_type': dict(gtype_counts),
    'n_folios': len(folio_paras),
}}

# ============================================================
# S1: SAME-TYPE RUN CLUSTERING
# ============================================================
print("\n=== S1: Same-Type Run Clustering ===")
# Are same-type gallows paragraphs more likely to be adjacent than chance?
# Compare observed same-type transitions to shuffled null.

observed_same = defaultdict(int)  # gtype -> count of same-type consecutive pairs
observed_total = defaultdict(int)  # gtype -> count of all pairs involving this type
all_transitions = []

for fid, recs in folio_gallows_paras.items():
    if len(recs) < 2:
        continue
    for j in range(len(recs) - 1):
        g1, g2 = recs[j]['gallows'], recs[j+1]['gallows']
        all_transitions.append((g1, g2))
        observed_total[g1] += 1
        if g1 == g2:
            observed_same[g1] += 1

# Shuffled null: permute gallows labels within each folio, 500 times
n_perms = 500
null_same = {g: [] for g in GALLOWS_TYPES}
rng = np.random.RandomState(42)

for _ in range(n_perms):
    perm_same = defaultdict(int)
    perm_total = defaultdict(int)
    for fid, recs in folio_gallows_paras.items():
        if len(recs) < 2:
            continue
        labels = [r['gallows'] for r in recs]
        rng.shuffle(labels)
        for j in range(len(labels) - 1):
            g1, g2 = labels[j], labels[j+1]
            perm_total[g1] += 1
            if g1 == g2:
                perm_same[g1] += 1
    for g in GALLOWS_TYPES:
        rate = perm_same[g] / max(perm_total[g], 1)
        null_same[g].append(rate)

s1_results = {}
for g in GALLOWS_TYPES:
    obs_rate = observed_same[g] / max(observed_total[g], 1)
    null_arr = np.array(null_same[g])
    null_mean = float(np.mean(null_arr))
    null_std = float(np.std(null_arr))
    z = (obs_rate - null_mean) / null_std if null_std > 0 else 0
    p_above = float(np.mean(null_arr >= obs_rate))
    s1_results[g] = {
        'obs_same_pairs': int(observed_same[g]),
        'obs_total_pairs': int(observed_total[g]),
        'obs_rate': round(obs_rate, 4),
        'null_mean': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'z': round(z, 2),
        'p_above': round(p_above, 4),
    }
    sig = '***' if p_above < 0.001 else '**' if p_above < 0.01 else '*' if p_above < 0.05 else ''
    print(f"  {g}: obs_rate={obs_rate:.3f} null_mean={null_mean:.3f} z={z:+.2f} p={p_above:.4f} {sig}")

# Also test: transition matrix (what follows each gallows type?)
print("\n  Transition matrix (row=from, col=to):")
trans_matrix = defaultdict(lambda: defaultdict(int))
for g1, g2 in all_transitions:
    trans_matrix[g1][g2] += 1
print(f"  {'':>4s}", end='')
for g2 in GALLOWS_TYPES:
    print(f"  {g2:>6s}", end='')
print()
for g1 in GALLOWS_TYPES:
    total = sum(trans_matrix[g1].values())
    print(f"  {g1:>4s}", end='')
    for g2 in GALLOWS_TYPES:
        ct = trans_matrix[g1][g2]
        pct = ct / total * 100 if total > 0 else 0
        print(f"  {pct:5.1f}%", end='')
    print(f"  (n={total})")

results['S1_run_clustering'] = s1_results

# ============================================================
# S2: WITHIN-FOLIO SAME-TYPE BODY COHESION
# ============================================================
print("\n=== S2: Within-Folio Same-Type Body Cohesion ===")
# For each gallows type, compare body similarity of same-type paragraphs
# within a folio to cross-type paragraphs within the same folio.

same_type_sims = {g: [] for g in GALLOWS_TYPES}
cross_type_sims = {g: [] for g in GALLOWS_TYPES}

for fid, recs in folio_gallows_paras.items():
    if len(recs) < 3:
        continue
    # Group by gallows type
    by_type = defaultdict(list)
    for r in recs:
        by_type[r['gallows']].append(r)

    for g in GALLOWS_TYPES:
        if len(by_type[g]) < 2:
            continue
        # Same-type pairs
        gp = by_type[g]
        for i in range(len(gp)):
            for j in range(i+1, len(gp)):
                sim = cosine_sim(gp[i]['atom_vec'], gp[j]['atom_vec'])
                same_type_sims[g].append(sim)

        # Cross-type: each g para vs each non-g para
        others = [r for r in recs if r['gallows'] != g]
        if not others:
            continue
        for gp_r in by_type[g]:
            for o in others:
                sim = cosine_sim(gp_r['atom_vec'], o['atom_vec'])
                cross_type_sims[g].append(sim)

s2_results = {}
for g in GALLOWS_TYPES:
    same = same_type_sims[g]
    cross = cross_type_sims[g]
    if len(same) < 5 or len(cross) < 5:
        s2_results[g] = {'status': 'insufficient_data', 'n_same': len(same), 'n_cross': len(cross)}
        print(f"  {g}: insufficient data (same={len(same)}, cross={len(cross)})")
        continue
    mean_same = float(np.mean(same))
    mean_cross = float(np.mean(cross))
    stat, p = mannwhitneyu(same, cross, alternative='greater')
    s2_results[g] = {
        'mean_same': round(mean_same, 4),
        'mean_cross': round(mean_cross, 4),
        'delta': round(mean_same - mean_cross, 4),
        'n_same': len(same),
        'n_cross': len(cross),
        'MW_p': round(float(p), 6),
    }
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    print(f"  {g}: same={mean_same:.4f} cross={mean_cross:.4f} delta={mean_same-mean_cross:+.4f} p={p:.6f} {sig}")

results['S2_same_type_cohesion'] = s2_results

# ============================================================
# S3: CONSECUTIVE BODY SIMILARITY BY GALLOWS TYPE
# ============================================================
print("\n=== S3: Consecutive Body Similarity ===")
# For consecutive paragraph pairs, compute body cosine similarity.
# Split by: same-type vs cross-type, and by specific gallows of para N.

consec_same = {g: [] for g in GALLOWS_TYPES}
consec_cross = {g: [] for g in GALLOWS_TYPES}  # keyed by para N's type
consec_all = []

for fid, recs in folio_gallows_paras.items():
    if len(recs) < 2:
        continue
    for j in range(len(recs) - 1):
        r1, r2 = recs[j], recs[j+1]
        sim = cosine_sim(r1['atom_vec'], r2['atom_vec'])
        consec_all.append(sim)
        if r1['gallows'] == r2['gallows']:
            consec_same[r1['gallows']].append(sim)
        else:
            consec_cross[r1['gallows']].append(sim)

# Also: does para N's body predict N+1's body? Correlation per atom dimension
# (this tests sequential flow independent of gallows type match)
consec_by_gtype = {g: {'body_n': [], 'body_n1': []} for g in GALLOWS_TYPES}
consec_by_gtype['all'] = {'body_n': [], 'body_n1': []}
for fid, recs in folio_gallows_paras.items():
    if len(recs) < 2:
        continue
    for j in range(len(recs) - 1):
        r1, r2 = recs[j], recs[j+1]
        consec_by_gtype[r1['gallows']]['body_n'].append(r1['atom_vec'])
        consec_by_gtype[r1['gallows']]['body_n1'].append(r2['atom_vec'])
        consec_by_gtype['all']['body_n'].append(r1['atom_vec'])
        consec_by_gtype['all']['body_n1'].append(r2['atom_vec'])

s3_results = {}
print("  Consecutive same-type vs cross-type cosine similarity:")
for g in GALLOWS_TYPES:
    same = consec_same[g]
    cross = consec_cross[g]
    n_same = len(same)
    n_cross = len(cross)
    entry = {'n_same': n_same, 'n_cross': n_cross}
    if n_same >= 3:
        entry['mean_same'] = round(float(np.mean(same)), 4)
    if n_cross >= 3:
        entry['mean_cross'] = round(float(np.mean(cross)), 4)
    if n_same >= 5 and n_cross >= 5:
        stat, p = mannwhitneyu(same, cross, alternative='greater')
        entry['MW_p'] = round(float(p), 6)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"  {g}: same={entry.get('mean_same','?'):.4f}(n={n_same}) "
              f"cross={entry.get('mean_cross','?'):.4f}(n={n_cross}) p={p:.4f} {sig}")
    else:
        print(f"  {g}: same(n={n_same}) cross(n={n_cross}) -- too few for test")
    s3_results[g] = entry

# Per-atom sequential correlation: does atom X fraction in para N predict atom X in para N+1?
print("\n  Per-atom N->N+1 correlation (all gallows types):")
for key in ['all'] + GALLOWS_TYPES:
    data = consec_by_gtype[key]
    if len(data['body_n']) < 10:
        print(f"  {key}: insufficient data (n={len(data['body_n'])})")
        continue
    X = np.array(data['body_n'])
    Y = np.array(data['body_n1'])
    # Mean cross-atom correlation
    atom_corrs = {}
    for ai, aname in enumerate(ALL_ATOMS):
        if np.std(X[:, ai]) > 0 and np.std(Y[:, ai]) > 0:
            r, p = pearsonr(X[:, ai], Y[:, ai])
            atom_corrs[aname] = round(float(r), 3)
    mean_r = float(np.mean(list(atom_corrs.values()))) if atom_corrs else 0
    # Also overall cosine between concatenated vectors
    overall_cos = float(np.mean([cosine_sim(X[i], Y[i]) for i in range(len(X))]))
    s3_results[f'{key}_sequential'] = {
        'n_pairs': len(data['body_n']),
        'mean_cosine_N_N1': round(overall_cos, 4),
        'mean_atom_corr': round(mean_r, 4),
        'atom_correlations': atom_corrs,
    }
    # Print top/bottom atoms
    sorted_atoms = sorted(atom_corrs.items(), key=lambda x: x[1], reverse=True)
    top3 = sorted_atoms[:3]
    bot3 = sorted_atoms[-3:]
    print(f"  {key:>5s}(n={len(data['body_n']):3d}): mean_cos={overall_cos:.3f} mean_r={mean_r:.3f}  "
          f"top: {' '.join(f'{a}={r:.3f}' for a,r in top3)}  "
          f"bot: {' '.join(f'{a}={r:.3f}' for a,r in bot3)}")

results['S3_consecutive_similarity'] = s3_results

# ============================================================
# S4: SEQUENTIAL BODY DRIFT PER GALLOWS TYPE
# ============================================================
print("\n=== S4: Sequential Body Drift ===")
# For each gallows type, track the 1st, 2nd, 3rd... occurrence in a folio.
# Does body composition drift systematically with occurrence number?

occurrence_data = {g: defaultdict(list) for g in GALLOWS_TYPES}  # g -> {occ_num -> [atom_vecs]}
occurrence_features = {g: defaultdict(list) for g in GALLOWS_TYPES}  # g -> {occ_num -> [token_count, line_count...]}

for fid, recs in folio_gallows_paras.items():
    type_counter = Counter()
    for r in recs:
        g = r['gallows']
        type_counter[g] += 1
        occ = type_counter[g]  # 1-indexed occurrence number
        occurrence_data[g][occ].append(r['atom_vec'])
        occurrence_features[g][occ].append({
            'tokens': r['token_count'],
            'lines': r['line_count'],
            'escape': r['escape_lines'],
            'terminal': r['terminal_lines'],
        })

s4_results = {}
for g in GALLOWS_TYPES:
    od = occurrence_data[g]
    max_occ = max(od.keys()) if od else 0
    n_folios_with_2plus = sum(1 for recs in folio_gallows_paras.values()
                              if sum(1 for r in recs if r['gallows'] == g) >= 2)
    entry = {
        'max_occurrences': max_occ,
        'folios_with_2plus': n_folios_with_2plus,
        'occurrence_counts': {str(k): len(v) for k, v in sorted(od.items()) if k <= 6},
    }

    # Test: does body composition change from occurrence 1 to occurrence 2+?
    if len(od.get(1, [])) >= 10 and len(od.get(2, [])) >= 5:
        vecs1 = np.array(od[1])
        vecs2_plus = np.array([v for k in range(2, max_occ+1) for v in od.get(k, [])])
        mean1 = np.mean(vecs1, axis=0)
        mean2 = np.mean(vecs2_plus, axis=0)
        drift_cos = cosine_sim(mean1, mean2)
        entry['occ1_vs_2plus'] = {
            'cosine': round(drift_cos, 4),
            'n_occ1': len(od[1]),
            'n_occ2plus': len(vecs2_plus),
        }
        # Per-atom drift: correlate occurrence number with atom fraction
        all_occs = []
        all_vecs = []
        for k, vecs in sorted(od.items()):
            for v in vecs:
                all_occs.append(k)
                all_vecs.append(v)
        all_occs = np.array(all_occs)
        all_vecs = np.array(all_vecs)
        drift_corrs = {}
        for ai, aname in enumerate(ALL_ATOMS):
            if np.std(all_vecs[:, ai]) > 0:
                r, p = spearmanr(all_occs, all_vecs[:, ai])
                drift_corrs[aname] = {'rho': round(float(r), 3), 'p': round(float(p), 4)}
        entry['drift_correlations'] = drift_corrs

        # Structural drift: token count, line count
        occ1_feats = occurrence_features[g][1]
        occ2_feats = [f for k in range(2, max_occ+1) for f in occurrence_features[g].get(k, [])]
        if occ1_feats and occ2_feats:
            tok1 = [f['tokens'] for f in occ1_feats]
            tok2 = [f['tokens'] for f in occ2_feats]
            entry['token_count_occ1'] = round(float(np.mean(tok1)), 1)
            entry['token_count_occ2plus'] = round(float(np.mean(tok2)), 1)
            line1 = [f['lines'] for f in occ1_feats]
            line2 = [f['lines'] for f in occ2_feats]
            entry['line_count_occ1'] = round(float(np.mean(line1)), 1)
            entry['line_count_occ2plus'] = round(float(np.mean(line2)), 1)

    s4_results[g] = entry
    d = entry.get('occ1_vs_2plus', {})
    drifts = entry.get('drift_correlations', {})
    sig_drifts = {a: v for a, v in drifts.items() if v['p'] < 0.05}
    print(f"  {g}: max_occ={max_occ} folios_w_2+={n_folios_with_2plus} "
          f"cos(1 vs 2+)={d.get('cosine', '?')} "
          f"sig_drifts={len(sig_drifts)}/{len(drifts)}")
    if sig_drifts:
        for a, v in sorted(sig_drifts.items(), key=lambda x: abs(x[1]['rho']), reverse=True)[:5]:
            print(f"    {a}: rho={v['rho']:+.3f} p={v['p']:.4f}")

results['S4_sequential_drift'] = s4_results

# ============================================================
# S5: RESET DETECTION
# ============================================================
print("\n=== S5: Reset Detection ===")
# After a paragraph of type X, is the next paragraph's body more different
# from the previous paragraph than usual?
# Measure: |body(N+1) - body(N-1)| when para N is type X
#   vs baseline: |body(N+1) - body(N-1)| for all consecutive triples

reset_scores = {g: [] for g in GALLOWS_TYPES}
baseline_scores = []

for fid, recs in folio_gallows_paras.items():
    if len(recs) < 3:
        continue
    for j in range(1, len(recs) - 1):
        # Triple: recs[j-1], recs[j], recs[j+1]
        cos_skip = cosine_sim(recs[j-1]['atom_vec'], recs[j+1]['atom_vec'])
        cos_adj = cosine_sim(recs[j-1]['atom_vec'], recs[j]['atom_vec'])
        baseline_scores.append(cos_skip)
        reset_scores[recs[j]['gallows']].append(cos_skip)

# Also: continuation score -- when para N is type X, cos(N, N+1)
cont_scores = {g: [] for g in GALLOWS_TYPES}
for fid, recs in folio_gallows_paras.items():
    if len(recs) < 2:
        continue
    for j in range(len(recs) - 1):
        cos_fwd = cosine_sim(recs[j]['atom_vec'], recs[j+1]['atom_vec'])
        cont_scores[recs[j]['gallows']].append(cos_fwd)

s5_results = {}
baseline_mean = float(np.mean(baseline_scores))
print(f"  Baseline skip-1 cosine (all triples): {baseline_mean:.4f} (n={len(baseline_scores)})")

for g in GALLOWS_TYPES:
    rs = reset_scores[g]
    cs = cont_scores[g]
    entry = {'n_triples': len(rs), 'n_pairs': len(cs)}
    if len(rs) >= 5:
        mean_skip = float(np.mean(rs))
        stat, p = mannwhitneyu(rs, baseline_scores, alternative='two-sided')
        entry['mean_skip_cosine'] = round(mean_skip, 4)
        entry['baseline_mean'] = round(baseline_mean, 4)
        entry['skip_vs_baseline_p'] = round(float(p), 6)
        # Interpretation: if mean_skip < baseline, type X causes a reset
        # if mean_skip > baseline, type X preserves continuity
        if mean_skip < baseline_mean:
            entry['direction'] = 'RESET (breaks continuity)'
        else:
            entry['direction'] = 'CONTINUITY (preserves flow)'
    if len(cs) >= 5:
        entry['mean_forward_cosine'] = round(float(np.mean(cs)), 4)

    s5_results[g] = entry
    skip = entry.get('mean_skip_cosine', '?')
    fwd = entry.get('mean_forward_cosine', '?')
    direction = entry.get('direction', '?')
    p_val = entry.get('skip_vs_baseline_p', '?')
    print(f"  {g}: skip_cos={skip} fwd_cos={fwd} direction={direction} p={p_val}")

results['S5_reset_detection'] = s5_results

# ============================================================
# S6: CROSS-PARAGRAPH GALLOWS PREDICTION
# ============================================================
print("\n=== S6: Cross-Paragraph Gallows Prediction ===")
# Can para N's body predict what gallows type para N+1 will use?
# And: does para N's gallows type predict para N+1's gallows type?

# Already have transition matrix from S1. Now test body prediction.
# For each atom, compute mean body fraction in para N, grouped by N+1's gallows type.
# Then chi2 contingency test.

next_gtype_bodies = {g: [] for g in GALLOWS_TYPES}
for fid, recs in folio_gallows_paras.items():
    if len(recs) < 2:
        continue
    for j in range(len(recs) - 1):
        next_g = recs[j+1]['gallows']
        next_gtype_bodies[next_g].append(recs[j]['atom_vec'])

s6_results = {}
print("  Mean body fractions of para N, grouped by N+1's gallows type:")
print(f"  {'':>6s}", end='')
for a in ['k', 'e', 'h', 't', 'p', 'f']:
    print(f"  {a:>6s}", end='')
print(f"  {'n':>5s}")
for g in GALLOWS_TYPES:
    vecs = next_gtype_bodies[g]
    if len(vecs) < 3:
        continue
    means = np.mean(vecs, axis=0)
    print(f"  ->{g:>3s}", end='')
    for a in ['k', 'e', 'h', 't', 'p', 'f']:
        ai = ALL_ATOMS.index(a)
        print(f"  {means[ai]:.4f}", end='')
    print(f"  {len(vecs):5d}")

# Test: does N+1's gallows type depend on N's gallows type (beyond baseline)?
# Already shown in transition matrix. Compute chi2.
trans_table = np.zeros((4, 4), dtype=int)
for i, g1 in enumerate(GALLOWS_TYPES):
    for j, g2 in enumerate(GALLOWS_TYPES):
        trans_table[i, j] = trans_matrix[g1][g2]
if trans_table.sum() > 0:
    chi2, p, dof, expected = chi2_contingency(trans_table)
    from scipy.stats import contingency
    V = float(np.sqrt(chi2 / (trans_table.sum() * min(3, 3))))
    s6_results['transition_chi2'] = {
        'chi2': round(float(chi2), 2),
        'p': round(float(p), 6),
        'V': round(V, 4),
        'dof': int(dof),
        'n': int(trans_table.sum()),
    }
    print(f"\n  Transition chi2: {chi2:.2f} p={p:.6f} V={V:.4f} n={trans_table.sum()}")

# Test: does N's body predict N+1's gallows? Kruskal-Wallis per atom
print("\n  N's body predicting N+1's gallows (KW per atom):")
sig_atoms = []
for ai, aname in enumerate(ALL_ATOMS):
    groups = []
    for g in GALLOWS_TYPES:
        vecs = next_gtype_bodies[g]
        if len(vecs) >= 3:
            groups.append([v[ai] for v in vecs])
    if len(groups) >= 2:
        stat, p = kruskal(*groups)
        if p < 0.05:
            sig_atoms.append((aname, float(stat), float(p)))
s6_results['body_predicts_next_gallows'] = {
    'sig_atoms': [(a, round(s, 2), round(p, 4)) for a, s, p in sig_atoms],
    'n_sig': len(sig_atoms),
    'n_tested': len(ALL_ATOMS),
}
if sig_atoms:
    for a, s, p in sorted(sig_atoms, key=lambda x: x[2]):
        print(f"    {a}: KW={s:.2f} p={p:.4f}")
else:
    print("    None significant")

results['S6_cross_prediction'] = s6_results

# ============================================================
# S7: CATEGORY/KERNEL CONTINUITY PER GALLOWS TYPE
# ============================================================
print("\n=== S7: Category/Kernel Continuity ===")
# For consecutive same-type pairs, is category/kernel profile more similar
# than consecutive cross-type pairs?

cat_same = {g: [] for g in GALLOWS_TYPES}
cat_cross = {g: [] for g in GALLOWS_TYPES}
ker_same = {g: [] for g in GALLOWS_TYPES}
ker_cross = {g: [] for g in GALLOWS_TYPES}

for fid, recs in folio_gallows_paras.items():
    if len(recs) < 2:
        continue
    for j in range(len(recs) - 1):
        r1, r2 = recs[j], recs[j+1]
        cat_sim = cosine_sim(r1['cat_vec'], r2['cat_vec'])
        ker_sim = cosine_sim(r1['kernel_vec'], r2['kernel_vec'])
        g1 = r1['gallows']
        if g1 == r2['gallows']:
            cat_same[g1].append(cat_sim)
            ker_same[g1].append(ker_sim)
        else:
            cat_cross[g1].append(cat_sim)
            ker_cross[g1].append(ker_sim)

s7_results = {}
for g in GALLOWS_TYPES:
    entry = {}
    # Category
    cs, cc_ = cat_same[g], cat_cross[g]
    if len(cs) >= 3 and len(cc_) >= 3:
        entry['cat_same_mean'] = round(float(np.mean(cs)), 4)
        entry['cat_cross_mean'] = round(float(np.mean(cc_)), 4)
        entry['cat_n_same'] = len(cs)
        entry['cat_n_cross'] = len(cc_)
        if len(cs) >= 5 and len(cc_) >= 5:
            stat, p = mannwhitneyu(cs, cc_, alternative='greater')
            entry['cat_MW_p'] = round(float(p), 6)
    # Kernel
    ks, kc = ker_same[g], ker_cross[g]
    if len(ks) >= 3 and len(kc) >= 3:
        entry['ker_same_mean'] = round(float(np.mean(ks)), 4)
        entry['ker_cross_mean'] = round(float(np.mean(kc)), 4)
        entry['ker_n_same'] = len(ks)
        entry['ker_n_cross'] = len(kc)
        if len(ks) >= 5 and len(kc) >= 5:
            stat, p = mannwhitneyu(ks, kc, alternative='greater')
            entry['ker_MW_p'] = round(float(p), 6)
    s7_results[g] = entry
    cat_d = entry.get('cat_same_mean', '?')
    cat_c = entry.get('cat_cross_mean', '?')
    ker_d = entry.get('ker_same_mean', '?')
    ker_c = entry.get('ker_cross_mean', '?')
    print(f"  {g}: cat(same={cat_d} cross={cat_c}) ker(same={ker_d} cross={ker_c})")

results['S7_category_kernel_continuity'] = s7_results

# ============================================================
# SYNTHESIS
# ============================================================
print("\n=== Synthesis ===")

# Which gallows type shows the strongest sequential properties?
print("  Sequential profile by gallows type:")
for g in GALLOWS_TYPES:
    props = []
    # S1: clustering
    s1 = s1_results.get(g, {})
    if s1.get('p_above', 1) < 0.05:
        props.append(f"CLUSTERS(z={s1['z']:+.1f})")
    # S3: forward prediction
    s3 = s3_results.get(f'{g}_sequential', {})
    if s3:
        props.append(f"seq_cos={s3.get('mean_cosine_N_N1', '?')}")
    # S4: drift
    s4 = s4_results.get(g, {})
    n_drift = len([v for v in s4.get('drift_correlations', {}).values() if v['p'] < 0.05])
    if n_drift > 0:
        props.append(f"DRIFTS({n_drift} atoms)")
    # S5: reset/continue
    s5 = s5_results.get(g, {})
    if s5.get('skip_vs_baseline_p', 1) < 0.05:
        props.append(s5.get('direction', '?'))

    print(f"  {g}: {'; '.join(props) if props else 'no significant sequential properties'}")

# Output
out_path = ROOT / 'phases' / 'GALLOWS_DEPLOYMENT_DISENTANGLEMENT' / 'results' / 'gallows_sequential_results.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults written to {out_path}")
print("Done.")
